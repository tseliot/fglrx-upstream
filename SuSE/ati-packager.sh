#!/bin/sh
#
# Purpose
#   Sample packaging script
#
# Usage
#   See README.distro document

export LC_ALL=C
export LANG=C

#Function: getSupportedPackages()
#Purpose: lists distribution supported packages
getSupportedPackages()
{
    #Determine absolute path of <installer root>/<distro>
    RelDistroDir=`dirname $0`
    AbsDistroDir=`cd ${RelDistroDir} 2>/dev/null && pwd`

    #List all spec files in the <installer root>/<distro> directory
    for SpecFile in `ls ${AbsDistroDir}/*.spec 2>/dev/null`; do
		SpecFile=`basename ${SpecFile}`
		X_DIR=${SpecFile%.*.spec}	# Name of the x* directory corresponding the requested package
		X_NAME=${SpecFile#x*.}
		X_NAME=${X_NAME%.spec}		# Well known X or distro name
		
        if [ "${X_DIR}" -a "${X_NAME}" -a -d ${AbsDistroDir}/../../${X_DIR} ]; then
    	    echo ${X_NAME}
        fi
    done
}

#Function: buildPackage()
#Purpose: build the requested package if it is supported
buildPackage()
{
    X_NAME=$1							# Well known X or distro name
    RelDistroDir=`dirname $0`			# Relative path to the distro directory
    AbsDistroDir=`cd ${RelDistroDir} 2>/dev/null && pwd` 	# Absolute path to the distro directory
    InstallerRootDir=`pwd`    			# Absolute path of the <installer root> directory
    # Temporary file to output diagnostics of the package build utility
    TmpPkgBuildOut="$(mktemp /tmp/pkg_build.out.XXXXXX)" || exit 1
    # Temporary directory to merge files from the common and x* directories
    TmpDrvFilesDir="$(mktemp -d /tmp/ati.XXXXXX)" || exit 1
    # Final spec file as a result of the original spec file after variables substituted
    TmpPkgSpec="$(mktemp /tmp/fglrx.spec.XXXXXX)" || exit 1
    EXIT_CODE=0							# Script exit code
	
	#Detect x* dir name corresponding to X_NAME
	X_DIR=`ls ${AbsDistroDir}/x*.${X_NAME}.spec`
	X_DIR=`basename ${X_DIR}`
	X_DIR=${X_DIR%.*.spec}

    #Detect target architechture    
    echo ${X_DIR} | grep _64 > /dev/null;
    if [ $? -eq 1 ]; then
    	ARCH=i386
        ARCHDIR=x86
    else
	ARCH=x86_64
	ARCHDIR=x86_64
    fi
    
    PKG_SPEC="${AbsDistroDir}/${X_DIR}.${X_NAME}.spec"	# Package specification file for the requested package
    
    #[Re]create the merging directory, or clean it up
	rm -rf ${TmpDrvFilesDir} > /dev/null
    mkdir ${TmpDrvFilesDir}

    #Merge files from different source directories
    cp -R ${InstallerRootDir}/common/* ${TmpDrvFilesDir}
    cp -R ${InstallerRootDir}/arch/${ARCHDIR}/* ${TmpDrvFilesDir}
    cp -R ${InstallerRootDir}/${X_DIR}/* ${TmpDrvFilesDir}
    if [ "${ARCH}" = "x86_64" ]; then
        cp -R ${InstallerRootDir}/arch/x86/usr/X11R6/lib ${TmpDrvFilesDir}/usr/X11R6
    fi
    mkdir ${TmpDrvFilesDir}/suse
    cp ${AbsDistroDir}/* ${TmpDrvFilesDir}/suse
    echo ${TmpDrvFilesDir}
    
    #Substitute variables in the specfile
    sed -f - ${PKG_SPEC} > ${TmpPkgSpec} <<END_SED_SCRIPT
s!%ATI_DRIVER_VERSION!`./ati-packager-helper.sh --version`!
s!%ATI_DRIVER_RELEASE!`./ati-packager-helper.sh --release`!
s!%ATI_DRIVER_DESCRIPTION!`./ati-packager-helper.sh --description`!
s!%ATI_DRIVER_URL!`./ati-packager-helper.sh --url`!
s!%ATI_DRIVER_VENDOR!`./ati-packager-helper.sh --vendor`!
s!%ATI_DRIVER_SUMMARY!`./ati-packager-helper.sh --summary`!
s!%ATI_DRIVER_BUILD_ROOT!${TmpDrvFilesDir}!
END_SED_SCRIPT
    
    #Build the package
    rpmbuild -bb --root ${TmpDrvFilesDir} --target ${ARCH} ${TmpPkgSpec} > ${TmpPkgBuildOut} 2>&1

    #Retrieve the absolute path to the built package
    if [ $? -eq 0 ]; then
        PACKAGE_STR=`grep "Wrote: .*\.rpm" ${TmpPkgBuildOut}` 	#String containing info where the package was created
        PACKAGE_FILE=`expr "${PACKAGE_STR}" : 'Wrote: \(.*\)'`	#Absolute path to the create package file
    else
		EXIT_CODE=1
    fi
    
    #After-build diagnostics and processing
    if [ ${EXIT_CODE} -eq 0 ]; then
    	AbsInstallerParentDir=`cd ${InstallerRootDir}/.. 2>/dev/null && pwd` 	# Absolute path to the installer parent directory
        cp ${PACKAGE_FILE} ${AbsInstallerParentDir}	# Copy the created package to the directory where the self-extracting driver archive is located
        echo "Package ${AbsInstallerParentDir}/`basename ${PACKAGE_FILE}` has been successfully generated"
    else
        echo "Package build failed!"
		EXIT_CODE=1
    fi
	
	#Clean-up
    rm -f ${TmpPkgSpec} > /dev/null
    rm -f ${TmpPkgBuildOut} > /dev/null
    rm -rf ${TmpDrvFilesDir} > /dev/null
    rm -f /usr/src/packages/BUILD/files.fglrx \
          ${PACKAGE_FILE}

    exit ${EXIT_CODE}
}

#Starting point of this script, process the {action} argument

#Requested action
action=$1

case "${action}" in
--get-supported)
    getSupportedPackages   
    ;;
--buildpkg)
    package=$2
    if [ "${package}" != "" ]
    then
        support_flag=false
        for supported_list in `getSupportedPackages`
        do
            if [ "${supported_list}" = "${package}" ]
            then
                support_flag=true
                break
            fi
        done
        if [ "${support_flag}" = "true" ]
        then
            buildPackage ${package}
        else
            echo "Requested package is not supported."
        fi
    else
		echo "Please provide package name"
    fi    
    exit 0
    ;;
*|--*)
    echo ${action}: unsupported option passed by ati-installer.sh
    exit 0
    ;;
esac

