#!/bin/sh
#
# Purpose
#   Sample packaging script
#
# Usage
#   See README.distro document

DRV_RELEASE="`./ati-packager-helper.sh --version`"
DEBEMAIL="`./ati-packager-helper.sh --vendor` <`./ati-packager-helper.sh --url`>"
REVISION="`./ati-packager-helper.sh --release`"

DAPPER="dapper 6.06"
EDGY="edgy 6.10"
FEISTY="feisty 7.04"
GUTSY="gutsy 7.10"
HARDY="hardy 8.04"

# set locale to sane value
export LANG=C
export LC_ALL=C

# set umask to sane value
umask 002

#Root command
if [ `whoami` != "root" ]; then
    if [ -x /usr/bin/gksudo ] && [ ! -z "$DISPLAY" ]; then
        ROOT="/usr/bin/gksudo --description 'AMD_Installer' "
    elif [ -x /usr/bin/kdesu ] && [ ! -z "$DISPLAY" ]; then
        ROOT="/usr/bin/kdesu"
    elif [ -x /usr/bin/sudo ]; then
        ROOT="/usr/bin/sudo"
    fi
else
    ROOT=""
fi

#Synaptic availablity
if [ -x /usr/sbin/synaptic ]; then
    SYNAPTIC="TRUE"
else
    SYNAPTIC=""
fi

#Top level directories used by multiple methods
InstallerRootDir=`pwd`              # Absolute path of the <installer root> directory
AbsInstallerParentDir=`cd ${InstallerRootDir}/.. 2>/dev/null && pwd`    # Absolute path to the installer parent directory

#Function: buildDepends()
#Purpose: checks that all build dependencies are resolved
buildDepends()
{
    if [ ! -x /usr/bin/dpkg-checkbuilddeps ] || [ ! -x /usr/bin/gcc ]; then
        if [ ! -z "$SYNAPTIC" ] && [ ! -z "$DISPLAY" ]; then
            TEMPFILE=`/bin/tempfile`
            cat > $TEMPFILE << EOF
dpkg-dev install
build-essential install
EOF
            $ROOT "sh -c '/usr/sbin/synaptic --set-selections --non-interactive --hide-main-window < $TEMPFILE'"
            rm $TEMPFILE -f
        else
            $ROOT apt-get -y install dpkg-dev build-essential
        fi
        #do a check again in case we have failed here
        if [ ! -x /usr/bin/dpkg-checkbuilddeps ]; then
            echo "Unable to install dpkg-dev and build-essential.  Please manually install and try again."
            exit 4
        fi
    fi
    release=$1
    missing_dependencies=$(dpkg-checkbuilddeps packages/Ubuntu/dists/$release/control 2>&1 | awk -F: '{ print $3 }' | sed 's/([^)]*)//g' | sed 's/|\s[^\s]*//g')
    #'
    if [ ! -z "$missing_dependencies" ]; then
        echo "Resolving build dependencies..."
        if [ ! -z "$SYNAPTIC" ] && [ ! -z "$DISPLAY" ]; then
            TEMPFILE=`/bin/tempfile`
            echo $missing_dependencies | sed 's/$/\ /' | sed 's/\ /\ install\r\n/g' > $TEMPFILE
            $ROOT "sh -c '/usr/sbin/synaptic --set-selections --non-interactive --hide-main-window < $TEMPFILE'"
            rm $TEMPFILE -f
        else
            $ROOT apt-get -y install $missing_dependencies
        fi
        #do a check again, abort if we still have some not installed
        missing_dependencies=$(dpkg-checkbuilddeps packages/Ubuntu/dists/$release/control 2>&1 | awk -F: '{ print $3 }' | sed 's/([^)]*)//g' | sed 's/|\s[^\s]*//g')
        #'
        if [ ! -z "$missing_dependencies" ]; then
            echo "Unable to resolve $missing_dependencies.  Please manually install and try again."
            exit 5
        fi
        echo "Continuing package build"
    fi
}

#Function: getSupportedPackages()
#Purpose: lists distribution supported packages
getSupportedPackages()
{
    echo $DAPPER $EDGY $FEISTY $GUTSY $HARDY
}

makeChangelog()
{
    printf "%b\n" "fglrx-installer (${DRV_RELEASE}-0ubuntu${REVISION}) ${1}; urgency=low\n" \
    > ${TmpDrvFilesDir}/debian/changelog
    printf "%b\n" "  * new release\n" \
    >> ${TmpDrvFilesDir}/debian/changelog
    printf "%b\n" " -- ${DEBEMAIL}  `date --rfc-822`\n" \
    >> ${TmpDrvFilesDir}/debian/changelog
}

installPackages()
{
    #check for dkms
    if [ ! -x /usr/sbin/dkms ] || [ ! -f /usr/lib/libGL.so.1.2 ]; then
        if [ ! -z "$SYNAPTIC" ] && [ ! -z "$DISPLAY" ]; then
            TEMPFILE=`/bin/tempfile`
            cat > $TEMPFILE << EOF
dkms install
libgl1-mesa-glx install
EOF
            $ROOT "sh -c '/usr/sbin/synaptic --set-selections --non-interactive --hide-main-window < $TEMPFILE'"
            rm $TEMPFILE -f
        else
            $ROOT apt-get -y install dkms libgl1-mesa-glx
        fi
    fi

    #Detect target architecture if not set
    if [ -z "$ARCH" ]; then
        ARCH=`dpkg-architecture -qDEB_HOST_ARCH`
    fi
    file="fglrx-installer_${DRV_RELEASE}-0ubuntu${REVISION}_${ARCH}.changes"
    if [ ! -f "${AbsInstallerParentDir}/$file" ]; then
    	echo "Unable to find ${AbsInstallerParentDir}/$file.  Please manually install"
    	exit 10
    else
    	cd ${AbsInstallerParentDir}
    	packages=$(cat $file | grep extra | awk '{print $5}' | grep -v dev | tr "\n" " ")
    	echo $packages
    	$ROOT "sh -c 'dpkg -i ${packages}'"
    fi
}


#Function: buildPackage()
#Purpose: build the requested package if it is supported
buildPackage()
{
    export X_NAME=$1                    # Well known X or distro name (exported for dpkg rules)
    RelDistroDir=`dirname $0`           # Relative path to the distro directory
    AbsDistroDir=`cd ${RelDistroDir} 2>/dev/null && pwd` # Absolute path to the distro directory 
    TmpPkgBuildOut="/tmp/pkg_build.out"         # Temporary file to output diagnostics of the package build utility
    TmpDrvFilesDir=`mktemp -d -t fglrx.XXXXXX`  # Temporary directory to merge files from the common and x* directories


    #Detect x* dir name corresponding to X_NAME
    case ${X_NAME} in
        dapper|6.06) X_DIR=x690; X_NAME=dapper;;
        edgy|6.10)   X_DIR=x710; X_NAME=edgy;;
        feisty|7.04) X_DIR=x710; X_NAME=feisty;;
        gutsy|7.10)  X_DIR=x710; X_NAME=gutsy;;
        hardy|8.04)  X_DIR=x710; X_NAME=hardy;;
        *)
        #Automatically detect
        echo "Error: invalid package name passed to --buildpkg" ; exit 1 ;;
    esac

    #resolve build dependencies
    buildDepends $X_NAME

    #Detect target architecture if not set
    if [ -z "$ARCH" ]; then
        ARCH=`dpkg-architecture -qDEB_HOST_ARCH`
    fi
    if [ "$ARCH" = "x86_x64" ]; then
        ARCH="amd64"
    fi

    case ${ARCH} in
    amd64) ARCH_DIR=x86_64; X_DIR=${X_DIR}_64a;;
    i386)  ARCH_DIR=x86;;
        *) echo "Error: unsupported architecture: ${ARCH}" ; exit 1 ;;
    esac

    PKG_BUILD_UTIL="dpkg-buildpackage" # Package build utility
    PKG_BUILD_OPTIONS="-a${ARCH} -b -nc -tc -uc -d"
    EXIT_CODE=0 # Script exit code

    if [ "$USER" != "root" ]; then
        if [ -x "`which fakeroot`" ]; then
            PKG_BUILD_OPTIONS="$PKG_BUILD_OPTIONS -rfakeroot"
        else
            echo "Error: need root permissions or the \`fakeroot' package installed"
            exit 1
        fi
    fi

    #Merge files from different source directories
    cp -f -R ${InstallerRootDir}/${X_DIR}/* ${TmpDrvFilesDir}
    cp -f -R ${InstallerRootDir}/arch/${ARCH_DIR}/* ${TmpDrvFilesDir}
    cp -f -R ${InstallerRootDir}/common/* ${TmpDrvFilesDir}

    if [ "$ARCH" = "amd64" ]; then
        cp -f -R ${InstallerRootDir}/arch/x86/usr/X11R6/lib \
        ${TmpDrvFilesDir}/usr/X11R6/
    fi

    # Merge package files from the appropriate directories
    chmod -R u+w ${AbsDistroDir}
    cp -f -R ${AbsDistroDir}/dists/${X_NAME} ${TmpDrvFilesDir}/debian
    cp -f -R ${AbsDistroDir}/module ${TmpDrvFilesDir}

    # generate a temporary changelog with version information
    makeChangelog ${X_NAME}

    #Build the package
    cd ${TmpDrvFilesDir}
    ${PKG_BUILD_UTIL} ${PKG_BUILD_OPTIONS} > ${TmpPkgBuildOut} 2>&1

    if [ $? -eq 0 ]; then
        #String containing info where the package was created
        PACKAGE_FILES=`grep 'building package .* in .*\.deb' ${TmpPkgBuildOut} | sed -e 's/.*in \`\(.*\.deb\).*/\1/'`

        for i in ${PACKAGE_FILES}; do
            mv $i ${AbsInstallerParentDir}  # move the created package to the directory where the self-extracting driver archive is located
            echo "Package ${AbsInstallerParentDir}/`basename ${i}` has been successfully generated"
        done

        mv ../fglrx-installer*.changes ${AbsInstallerParentDir}
    else
        echo "Package build failed!"
        echo "Package build utility output:"
        cat ${TmpPkgBuildOut}
        exit 1
    fi

    #Clean-up
    rm -rf ${TmpDrvFilesDir} > /dev/null
    rm -f ${TmpPkgBuildOut} > /dev/null
}

query_lsb()
{
    package=$1
    #First determine if we are explicitly calling a release build
    support_flag=false
    for supported_list in `getSupportedPackages`
    do
        if [ "${supported_list}" = "${package}" ]
        then
            support_flag=true
            break
        fi
    done
    #If we haven't explicitly called, or failed to type something coherent
    #automatically detect
    if [ "${support_flag}" != "true" ]
    then
        package=`lsb_release -s -c`
        for supported_list in `getSupportedPackages`
        do
            if [ "${supported_list}" = "${package}" ]
            then
                support_flag=true
                echo "Automatically detected" ${package}
                break
            fi
        done
        #If we are explicitly trying to build something that isn't supported
        if [ "${support_flag}" != "true" ] && [ "${package}" != "Ubuntu" ]
        then
            echo ${package} "is invalid.  Attempting automatic detection."
        fi
    fi
    if [ "${support_flag}" = "true" ]
    then
        buildPackage ${package}
    else
        echo "Unable to build package for" ${package}
        exit 1
    fi
}

#Starting point of this script, process the {action} argument

#Requested action
action=$1

case "${action}" in
--get-supported)
    getSupportedPackages
    ;;
--autopkg)
    query_lsb $2
    installPackages
    #aticonfig doesn't work on Hardy atm.
    #$ROOT "aticonfig --initial"
    ;;
--installpkg)
    installPackages
    ;;
--buildpkg)
    query_lsb $2
    ;;
*|--*)
    echo ${action}: unsupported option passed by ati-installer.sh
    exit 0
    ;;
esac

