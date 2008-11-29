#!/bin/sh
#
# Purpose
#   Mandriva ATI packaging script
#
# Usage
#   See README.distro document

# List of supported distributions.
SuppDistro="2006.0 2007.0 2007.1 2008.0 2008.1 2009.0 2009.1"

#Function: getSupportedPackages()
#Purpose: lists distribution supported packages
getSupportedPackages()
{
    #Determine absolute path of <installer root>/<distro>
    #RelDistroDir=`dirname $0`
    #AbsDistroDir=`cd ${RelDistroDir} 2>/dev/null && pwd`
    #RootDir="${AbsDistroDir}/../../"

    for d in ${SuppDistro}; do
	    echo $d
    done
}

buildPrep()
{
    distro=$2
    dryrun=$3
    if [ ! -f /etc/mandriva-release ]; then
        echo "You can build Mandriva packages only on a Mandriva Linux system."
        exit ${ATI_INSTALLER_ERR_PREP}
    fi
    [ -x /usr/bin/rpmbuild ] && exit 0

    if [ -n "$dryrun" ]; then
        echo "You need the rpm-build package to build packages."
        exit ${ATI_INSTALLER_ERR_PREP}
    fi

    if [ -n "$DISPLAY" ]; then
        gurpmi --auto rpm-build
    else
        su -c "urpmi --auto rpm-build"
    fi

    [ -x /usr/bin/rpmbuild ] && exit 0

    echo "Package rpm-build is needed but installation failed."
    exit ${ATI_INSTALLER_ERR_PREP}
}

#Function: buildPackage()
#Purpose: build the requested package if it is supported
buildPackage()
{
    DistroName=$1						# Well known X or distro name
    RelDistroDir=`dirname $0`					# Relative path to the distro directory
    AbsDistroDir=`cd ${RelDistroDir} 2>/dev/null && pwd`	# Absolute path to the distro directory
    InstallerRootDir=`pwd`    					# Absolute path of the <installer root> directory
    RpmDirs="BUILD SPECS SOURCES RPMS SRPMS tmp"
    Arch=`uname -m`						# Architecture

    # before trying to build something, check that we have at least rpm-build
    if [ ! -x /usr/bin/rpmbuild ]; then
	    echo "Please install the rpm-build package !"
	    exit 1
    fi

    RpmRoot=`mktemp -d ${TMPDIR:=/tmp}/ati.XXXXXX`		# Rpm TopDir
    TmpPkgBuildDir="${RpmRoot}/BUILD"
    TmpPkgBuildOut="${RpmRoot}/pkg_build.out"			# Temporary file to output diagnostics of the 
    TmpPkgSpec="${RpmRoot}/SPECS/fglrx.spec"			# Spec file
    EXIT_CODE=0							# Script exit code

    # create directories
    for d in ${RpmDirs}; do
	    mkdir -p ${RpmRoot}/$d
    done

    # copy spec file and binaries
    cp ${AbsDistroDir}/fglrx.spec ${TmpPkgSpec}

    #Build the package
    LC_ALL=C rpm -bb --with ati \
	--define "_topdir ${RpmRoot}" \
	--define "_tmppath ${RpmRoot}/tmp" \
	--define "_builddir ${RpmRoot}/BUILD" \
	--define "_rpmdir ${RpmRoot}/RPMS" \
	--define "_sourcedir ${AbsDistroDir}" \
	--define "version $(./ati-packager-helper.sh --version)" \
	--define "rel $(./ati-packager-helper.sh --release)" \
	--define "ati_dir ${InstallerRootDir}" \
	--define "distsuffix amd.mdv" \
	--define "vendor $(./ati-packager-helper.sh --vendor)" \
	--define "packager $(./ati-packager-helper.sh --vendor)" \
	--define "mdkversion $(echo ${DistroName} | tr . 0)" \
	--define "mandriva_release ${DistroName}" \
	${TmpPkgSpec} > ${TmpPkgBuildOut} 2>&1

    #Retrieve the absolute path to the built package
    if [ $? -eq 0 ]; then
        PACKAGE_STR=`grep "Wrote: .*\.rpm" ${TmpPkgBuildOut} | sed -r 's!Wrote:(.*)!\1!'` 	#String containing info where the package was created
    else
	EXIT_CODE=1
    fi
    
    #After-build diagnostics and processing
    if [ ${EXIT_CODE} -eq 0 ]; then
    	AbsInstallerParentDir=`cd ${InstallerRootDir}/.. 2>/dev/null && pwd` 	# Absolute path to the installer parent directory
	for p in ${PACKAGE_STR}; do
        	cp $p ${AbsInstallerParentDir}	# Copy the created package to the directory where the self-extracting driver archive is located
        	echo "Package ${AbsInstallerParentDir}/`basename ${p}` has been successfully generated"
	done
    else
        echo "Package build failed!"
        echo "Package build utility output:"
        cat ${TmpPkgBuildOut} 
		EXIT_CODE=1
    fi
	
    # Clean-up
    rm -rf ${RpmRoot} > /dev/null
    
    exit ${EXIT_CODE}
}

installPackage()
{
    package=$1
    distrover=$(cat /etc/version | cut -d. -f1)
    if [ "${package}" != "${distrover}" ]; then
        echo "Mandriva Linux ${distrover} can't use ${package} packages."
        exit 1
    fi
    packagenames="$(rpm -q --specfile --with ati \
        --qf '%{name}-%{version}-%{release}.%{arch}.rpm\n' \
	--define "version $(./ati-packager-helper.sh --version)" \
	--define "rel $(./ati-packager-helper.sh --release)" \
	--define "distsuffix amd.mdv" \
	--define "mdkversion $(echo ${package} | tr . 0)" \
	--define "mandriva_release ${package}" \
	$(dirname $0)/fglrx.spec | tail -n+2 | grep -v -e ^fglrx-debug -e ^fglrx-__restore__)"
    if [ -z "${packagenames}" ]; then
        echo "Unable to determine package names."
        exit 1
    fi
    pushd ..
    if [ -n "$DISPLAY" ]; then
        gurpmi --auto $packagenames
    else
        su -c "urpmi --auto $packagenames"
    fi
    ret=$?
    popd
    if [ $ret -ne 0 ]; then
        echo "Unable to install packages."
        exit 1
    fi
    echo "Installation successful."
    exit 0
}

isValidDistro()
{
    for supported_list in `getSupportedPackages`
    do
        if [ "${supported_list}" = "$1" ]
        then
            return 0 
        fi
    done
    return 1
}

checkDistro()
{
    if ! isValidDistro $1; then
        echo "Unsupported distribution:" $1
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
--buildpkg)
    #First determine if we are explicitly calling a release build
    package=$2
    support_flag=false
    isValidDistro ${package} && support_flag=true

    #automatically detect
    if [ "${support_flag}" != "true" ]
    then
        package=$(cat /etc/version | cut -d. -f1)
        if isValidDistro ${package}; then
            support_flag=true
            echo "Automatically detected" ${package}
        fi
    fi
    if [ "${support_flag}" = "true" ]
    then
        buildPackage ${package}
    else
        echo "Unable to build package for" ${package}
        exit 1
    fi
    exit 0
    ;;
--buildprep)
    package=$2
    if [ -n "$3" -a "$3" != "--dryrun" ]; then
        echo $3: unsupported option passed by ati-installer.sh
        exit 1
    fi
    checkDistro $package
    buildPrep $2 $3
    ;;
--installpkg)
    package=$2
    checkDistro $package
    installPackage $package
    ;;
--installprep)
    package=$2
    checkDistro $package
    # All this is handled in --installpkg already.
    exit 0
    ;;
--identify)
    package=$2
    if [ -f /etc/mandriva-release -a "${package}" = "$(cat /etc/version | cut -d. -f1,2)" ]; then
        exit 0
    fi
    exit ${ATI_INSTALLER_ERR_VERS}
    ;;
--getAPIVersion)
    exit 2
    ;;
*|--*)
    echo ${action}: unsupported option passed by ati-installer.sh
    exit 0
    ;;
esac

