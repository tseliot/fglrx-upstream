#!/bin/sh
#
# Purpose
#   Mandriva ATI packaging script
#
# Usage
#   See README.distro document

# prevent problems due to locales when grepping for 'wrote:'
export LC_ALL=C

# List of supported distributions.
SuppDistro="2006 2007 2008 2009"

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
    rpm -bb --with ati \
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
	--define "mdkversion ${DistroName}00" \
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
        package=$(cat /etc/version | cut -d. -f1)
        for supported_list in `getSupportedPackages`
        do
            if [ "${supported_list}" = "${package}" ]
            then
                support_flag=true
                echo "Automatically detected" ${package}
                break
            fi
        done
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
*|--*)
    echo ${action}: unsupported option passed by ati-installer.sh
    exit 0
    ;;
esac

