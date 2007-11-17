#!/bin/sh
#
# Purpose
#   Sample packaging script
#
# Usage
#   See README.distro document

# prevent problems due to locales when grepping for 'wrote:'
export LC_ALL=C

# List of supported distributions.
SuppDistro="2006 2007 2008"

#Function: getXVersion()
#Purpose : returns the Xorg/Xfree version for a given distribution
getXVersion()
{
	case "$1" in
		2005*) echo "6.8.0"
			;;
		2006*) echo "6.9.0"
			;;
		2007* | 2008*) echo "7.1.0"
			;;
		*)	echo "Err"
			;;
	esac
}

#Function: getXDir()
#Purpose : returns the Xorg/Xfree directory for a given arch and X version
# first arg : X version, second arg : arch
getXDir()
{
	case "$1" in
		6.8.0)	MyDir="x680"
			;;
		6.9.0)  MyDir="x690"
			;;
		7.1.0)  MyDir="x710"
			;;
	esac
	
	if [ "$2" == "x86_64" ]; then
	    MyDir="${MyDir}_64a"
	fi

	echo "${MyDir}"
}
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
    RpmDirs="BUILD SPECS SOURCES RPMS SRPMS"
    Arch=`uname -m`						# Architecture

    if [ $Arch == "x86_64" ]; then
	    PackName="fglrx64"
    else
	    PackName="fglrx"
    fi
    XorgVersion=`getXVersion ${DistroName}`
    AtiXorgVersion=`getXDir ${XorgVersion} ${Arch}`
    Version=`./ati-packager-helper.sh --version`
    RpmRoot=`mktemp -d ${TMPDIR:=/tmp}/ati.XXXXXX`		# Rpm TopDir
    TmpPkgBuildDir="${RpmRoot}/BUILD"
    TmpPkgBuildOut="${RpmRoot}/pkg_build.out"			# Temporary file to output diagnostics of the 
    TmpPkgSpec="${RpmRoot}/SPECS/ati.spec"			# Spec file
    EXIT_CODE=0							# Script exit code

    # before trying to build something, check that we have at least rpm-build
    if [ ! -x /usr/bin/rpmbuild ]; then
	    echo "Please install the rpm-build package !"
	    exit 1
    fi

    # create directories
    for d in ${RpmDirs}; do
	    mkdir -p ${RpmRoot}/$d
    done
    mkdir -p ${TmpPkgBuildDir}/${PackName}-${XorgVersion}-${Version}

    # copy spec file and binaries
    cp ${AbsDistroDir}/ati.spec ${TmpPkgSpec}
    if [ $Arch == "x86_64" ]; then
	    cp -a ${InstallerRootDir}/arch/x86_64/* ${TmpPkgBuildDir}/${PackName}-${XorgVersion}-${Version}
    else
	    cp -a ${InstallerRootDir}/arch/x86/* ${TmpPkgBuildDir}/${PackName}-${XorgVersion}-${Version}
    fi

    # copy atieventsd initscript
    mkdir -p ${TmpPkgBuildDir}/${PackName}-${XorgVersion}-${Version}/etc/init.d
    cp ${AbsDistroDir}/atieventsd.init ${TmpPkgBuildDir}/${PackName}-${XorgVersion}-${Version}/etc/init.d/atieventsd
    
    #Substitute variables in the specfile
    sed -i -f - ${TmpPkgSpec}  <<END_SED_SCRIPT
s!@xorg_version@!${XorgVersion}!
s!@ati_xorg_version@!${AtiXorgVersion}!
s!@version@!`./ati-packager-helper.sh --version`!
s!@release@!`./ati-packager-helper.sh --release`!
s!@packname@!${PackName}!
s!@vendor@!`./ati-packager-helper.sh --vendor`!
s!@mail@!`./ati-packager-helper.sh --url`!
s!@date@!`date +"%a %b %d %Y"`!
END_SED_SCRIPT
 

    # Merge files from different source directories
    cp -a ${InstallerRootDir}/${AtiXorgVersion}/* ${TmpPkgBuildDir}/${PackName}-${XorgVersion}-${Version}
    cp -a ${InstallerRootDir}/common/* ${TmpPkgBuildDir}/${PackName}-${XorgVersion}-${Version}

    #Build the package
    rpm -bb --define "_topdir ${RpmRoot}" --define "_tmppath ${RpmRoot}/BUILD/" ${TmpPkgSpec} > ${TmpPkgBuildOut} 2>&1



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

