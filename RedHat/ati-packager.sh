#!/bin/sh
#
# Purpose
#   Sample packaging script
#
# Usage
#   See README.distro document

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
    RelDistroDir=`dirname $0`					# Relative path to the distro directory
    AbsDistroDir=`cd ${RelDistroDir} 2>/dev/null && pwd` 	# Absolute path to the distro directory
    InstallerRootDir=`pwd`    					# Absolute path of the <installer root> directory
    TmpPkgBuildOut="/tmp/pkg_build.out"				# Temporary file to output diagnostics of the package build utility
    TmpDrvFilesDir=/tmp/fglrx					# Temporary directory to merge files from the common, arch and x* directories
    TmpDrvFilesDirRHEL5=/tmp/fglrx_rhel5        		# Temporary directory to mergx files to RHEL5 specific tree
    TmpPkgSpec=/tmp/fglrx.spec					# Final RHEL3/4 spec file as a result of the original spec file after variables substituted
    TmpPkgSpecRHEL5=/tmp/fglrx_rhel5.spec                       # Final RHEL5 spec file as a result of the original spec file after variables substituted
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
        ARCH_LIB=lib
    else
        ARCH=x86_64
    	ARCHDIR=x86_64
        ARCH_LIB=lib64
        X_DIR64=${X_DIR}_64a
    fi
    
    PKG_SPEC="${AbsDistroDir}/${X_DIR}.${X_NAME}.spec"	# Package specification file for the requested package
    
    #[Re]create the merging directory, or clean it up
	rm -rf ${TmpDrvFilesDir} > /dev/null
	mkdir ${TmpDrvFilesDir}

        rm -rf ${TmpDrvFilesDirRHEL5} > /dev/null
        mkdir ${TmpDrvFilesDirRHEL5}

    # RHEL5 RPM packages
    echo ${X_DIR} | grep x710 > /dev/null;
    if [ $? -eq 0 ]; then
        cp -R ${InstallerRootDir}/common/* ${TmpDrvFilesDirRHEL5}
        cp -R ${InstallerRootDir}/arch/${ARCHDIR}/* ${TmpDrvFilesDirRHEL5}
    	cp -R ${InstallerRootDir}/${X_DIR}/* ${TmpDrvFilesDirRHEL5}

	if [ "${ARCH}" = "x86_64" ]; then
	    cp -R ${InstallerRootDir}/arch/x86/usr/X11R6/lib ${TmpDrvFilesDirRHEL5}/usr/X11R6
	fi

        # Move files from the common, arch and x* directories as required for X11R7-based distribution releases (RHEL5)
        mkdir -p ${TmpDrvFilesDirRHEL5}/usr/include
        mv ${TmpDrvFilesDirRHEL5}/usr/X11R6/include/X11 \
           ${TmpDrvFilesDirRHEL5}/usr/include

        if [ -d ${TmpDrvFilesDirRHEL5}/usr/X11R6/lib/modules/dri ]; then
            mkdir -p ${TmpDrvFilesDirRHEL5}/usr/lib/dri
            mv -f ${TmpDrvFilesDirRHEL5}/usr/X11R6/lib/modules/dri/* ${TmpDrvFilesDirRHEL5}/usr/lib/dri
        fi
        if [ -d ${TmpDrvFilesDirRHEL5}/usr/X11R6/lib64/modules/dri ]; then
            mkdir -p ${TmpDrvFilesDirRHEL5}/usr/lib64/dri
            mv -f ${TmpDrvFilesDirRHEL5}/usr/X11R6/lib64/modules/dri/* ${TmpDrvFilesDirRHEL5}/usr/lib64/dri
        fi

        mkdir -p ${TmpDrvFilesDirRHEL5}/usr/${ARCH_LIB}/xorg/modules
        mv ${TmpDrvFilesDirRHEL5}/usr/X11R6/${ARCH_LIB}/modules/{drivers,linux} \
           ${TmpDrvFilesDirRHEL5}/usr/${ARCH_LIB}/xorg/modules
        mv ${TmpDrvFilesDirRHEL5}/usr/X11R6/${ARCH_LIB}/modules/glesx* \
           ${TmpDrvFilesDirRHEL5}/usr/${ARCH_LIB}/xorg/modules

        #Move the directory for the OpenGL libraries
        #mkdir -p ${TmpDrvFilesDirRHEL5}/usr/${ARCH_LIB}/xorg
        if [ -f ${TmpDrvFilesDirRHEL5}/usr/X11R6/lib/libGL.so.1.2 ]; then
            if [ "$ARCH" = "x86_64" ]; then
                mkdir -p ${TmpDrvFilesDirRHEL5}/usr/lib/xorg                     
            fi
            mv -f ${TmpDrvFilesDirRHEL5}/usr/X11R6/lib/libGL.so.1.2 ${TmpDrvFilesDirRHEL5}/usr/lib/xorg
        fi
        if [ -f ${TmpDrvFilesDirRHEL5}/usr/X11R6/lib64/libGL.so.1.2 ]; then
            mv -f ${TmpDrvFilesDirRHEL5}/usr/X11R6/lib64/libGL.so.1.2 ${TmpDrvFilesDirRHEL5}/usr/lib64/xorg
        fi

        mv ${TmpDrvFilesDirRHEL5}/usr/X11R6/${ARCH_LIB}/lib*.a \
           ${TmpDrvFilesDirRHEL5}/usr/${ARCH_LIB}/xorg

	if [ "${ARCH}" = "x86_64" ]; then
	    mv ${TmpDrvFilesDirRHEL5}/usr/X11R6/lib/lib*.a \
               ${TmpDrvFilesDirRHEL5}/usr/lib/xorg
	fi

	# Move the binaries to /usr/bin
	mkdir -p ${TmpDrvFilesDirRHEL5}/usr/bin
	mv ${TmpDrvFilesDirRHEL5}/usr/X11R6/bin/* \
	   ${TmpDrvFilesDirRHEL5}/usr/bin

    #Substitute variables in the specfile
    echo "requires: compat-libstdc++-33" > ${TmpPkgSpecRHEL5}
    sed -f - ${PKG_SPEC} >> ${TmpPkgSpecRHEL5} <<END_SED_SCRIPT
s!%ATI_DRIVER_VERSION!`./ati-packager-helper.sh --version`!
s!%ATI_DRIVER_RELEASE!`./ati-packager-helper.sh --release`!
s!%ATI_DRIVER_DESCRIPTION!`./ati-packager-helper.sh --description`!
s!%ATI_DRIVER_URL!`./ati-packager-helper.sh --url`!
s!%ATI_DRIVER_VENDOR!`./ati-packager-helper.sh --vendor`!
s!%ATI_DRIVER_SUMMARY!`./ati-packager-helper.sh --summary`!
s!%ATI_DRIVER_BUILD_ROOT!${TmpDrvFilesDirRHEL5}!
END_SED_SCRIPT

    find ${TmpDrvFilesDirRHEL5} -type f -name "*" | grep -v "fireglcontrol" | sed -e "s!${TmpDrvFilesDirRHEL5}!!" >> ${TmpPkgSpecRHEL5}

    #Build the package
    #RHEL5 RPM packages
    rpmbuild -bb --root ${TmpDrvFilesDirRHEL5} --target ${ARCH} ${TmpPkgSpecRHEL5} > ${TmpPkgBuildOut} 2>&1

    else

	    #Merge files from different source directories
        cp -R ${InstallerRootDir}/common/* ${TmpDrvFilesDir}
        cp -R ${InstallerRootDir}/arch/${ARCHDIR}/* ${TmpDrvFilesDir}
        cp -R ${InstallerRootDir}/${X_DIR}/* ${TmpDrvFilesDir}

	if [ "${ARCH}" = "x86_64" ]; then
            cp -R ${InstallerRootDir}/arch/x86/usr/X11R6/lib ${TmpDrvFilesDir}/usr/X11R6
        fi

    #      *** NOTICE ***      #
    # If our libGL.so.1.2 changes version, or the GL libraries
    # change, this code becomes obsolete.
    if [ -f ${TmpDrvFilesDir}/usr/X11R6/lib/libGL.so.1.2 ]; then
        mv -f ${TmpDrvFilesDir}/usr/X11R6/lib/libGL.so.1.2 ${TmpDrvFilesDir}/usr/X11R6/lib/libGL.fgl.so.1.2
    fi

    if [ -f ${TmpDrvFilesDir}/usr/X11R6/lib64/libGL.so.1.2 ]; then
        mv -f ${TmpDrvFilesDir}/usr/X11R6/lib64/libGL.so.1.2 ${TmpDrvFilesDir}/usr/X11R6/lib64/libGL.fgl.so.1.2
    fi

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

    find ${TmpDrvFilesDir} -type f -name "*" | grep -v "fireglcontrol" | sed -e "s!${TmpDrvFilesDir}!!" >> ${TmpPkgSpec}

    #Build the package
    #RHEL3/4 RPM packages
    rpmbuild -bb --root ${TmpDrvFilesDir} --target ${ARCH} ${TmpPkgSpec} > ${TmpPkgBuildOut} 2>&1

    fi
    
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
        echo "Package build utility output:"
        cat ${TmpPkgBuildOut} 
		EXIT_CODE=1
    fi
	
	#Clean-up
    rm -f ${TmpPkgSpec} > /dev/null
    rm -f ${TmpPkgSpecRHEL5} > /dev/null
    rm -f ${TmpPkgBuildOut} > /dev/null
    rm -rf ${TmpDrvFilesDir} > /dev/null
    rm -rf ${TmpDrvFilesDirRHEL5} > /dev/null
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

