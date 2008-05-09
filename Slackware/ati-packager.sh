#!/bin/bash
# by Emanuele Tomasi <tomasi@cli.di.unipi.it>
#    Ezio Ghibaudo   <ekxius@gmail.com>
#    Federico Rota   <federico.rota01@gmail.com>

function _buildpkg
{
    [ ! -e ${SCRIPT_DIR}/make_module.sh ] && echo -e "\E[00;31m${MESSAGE[11]}\E[00m\n" && exit 1;
    [ ! -e ${SCRIPT_DIR}/make_x.sh ] && echo -e "\E[00;31m${MESSAGE[12]}\E[00m\n" && exit 1;
    
    local OPTIONS=`echo $1 | tr [:upper:] [:lower:]`;
    case $OPTIONS in
	only_module | slack_module)
	    source ${SCRIPT_DIR}/make_module.sh;
	    _make_module;
	    ;;
	only_x | slack_x)
	    source ${SCRIPT_DIR}/make_x.sh;
	    _make_x;
	    ;;
	all | slackware)
	    source ${SCRIPT_DIR}/make_module.sh;
	    _make_module;
	    source ${SCRIPT_DIR}/make_x.sh;
	    _make_x;
	    ;;
	test)
	    local CHECK_SCRIPT=./check.sh;
	    PATH=$PATH:/usr/X11/bin:/usr/X11R6/bin
	    source ${CHECK_SCRIPT} --noprint;
	    set;
	    ;;
	*) echo "$1 ${MESSAGE[10]}";
	    exit 2;
	    ;;
    esac
}

function _detect_kernel_ver_from_PATH_KERNEL
{
    local INCLUDES=${KERNEL_PATH}/include/linux;
    KNL_VER=$(grep UTS_RELEASE ${INCLUDES}/version.h | cut -d'"' -f2);
    if [ -z ${KNL_VER} ]; then
	KNL_VER=$(grep UTS_RELEASE ${INCLUDES}/utsrelease.h | cut -d'"' -f2);
	if [ -z ${KNL_VER} ]; then
	    KNL_VER=$(grep UTS_RELEASE ${INCLUDES}/version-*.h 2>/dev/null | cut -d'"' -f2);
	fi
    fi
    
    if [ -z ${KNL_VER} ]; then
	echo ${MESSAGE[8]};
	exit 1;
    fi
}

function _init_env
{
    [ $(id -u) -gt 0 ] && echo ${MESSAGE[6]} && exit 1;
    
    BUILD_VER=1.2.4;
    
    ROOT_DIR=$PWD; # Usata dal file patch_function (se esiste)
    echo "$ROOT_DIR" | grep -q " " && echo ${MESSAGE[7]} && exit 1;
    
    
    ARCH=$(arch); # Usata dal file patch_function (se esiste)
    [[ $ARCH != x86_64 ]] && ARCH="x86";
    
    # Setto il nome del modulo
    if [ ! -z ${KERNEL_PATH} ]; then
	_detect_kernel_ver_from_PATH_KERNEL; # Setta KNL_VER, variabile usata dalfile patch_function (se esiste)
    else
	KNL_VER=$(uname -r) # Usata dal file patch_function (se esiste)
    fi
    
    if [[ $KNL_VER == "2.6."* ]]; then
	MODULE_NAME=fglrx.ko.gz;
    else
	MODULE_NAME=fglrx.o.gz;
    fi
    
    SCRIPT_DIR=packages/Slackware; # Usata anche dal file patch_function (se esiste)
    ATI_DRIVER_VER=$(./ati-packager-helper.sh --version); # Usata dal file patch_function (se esiste)
    ATI_DRIVER_REL=$(./ati-packager-helper.sh --release);
    
    MODULE_PKG_DIR=${SCRIPT_DIR}/module_pkg;
    MODULE_PACK_NAME=fglrx-module-${ATI_DRIVER_VER}-${ARCH}-${ATI_DRIVER_REL}
    
    X_PKG_DIR=${SCRIPT_DIR}/x_pkg;
    X_PACK_PARTIAL_NAME=fglrx-${ATI_DRIVER_VER}-${ARCH}-${ATI_DRIVER_REL};
    
    DEST_DIR=${PWD%/*};
}

function _check_builder_dependencies 
{
    local DEPS=(ln coreutils\
                cp coreutils\ 
	        mv coreutils\
                rm coreutils\ 
	        mkdir coreutils\
                chmod coreutils\
                find findutils\
                strip binutils\ 
                grep grep\
                sed sed\
                makepkg pkgtools\
                file file\
                xargs findutils\
                gzip gzip\
                depmod module-init-tools\
                mount linux-utils);
    
    local i=0;
    local DEPS_OK=0;
    while [ $i -lt ${#DEPS[@]} ];
    do
	which ${DEPS[$i]} &> /dev/null;
	if [ $? != 0 ];
	then
	    echo -e "\E[00;31m${MESSAGE[4]} ${DEPS[$i]} ${MESSAGE[5]} ${DEPS[${i}+1]}. \E[00m";
	    DEPS_OK=1;
	fi
	let i+=2;
    done
    
    if [ $DEPS_OK != 0 ];
    then
	exit 2;
    fi
}

function _set_builder_language
{
    local EXT=$(echo $LANG | cut -d '_' -f1);
    local FILE="/packages/Slackware/languages/ati-packager.en";
    
    if [ -e "${PWD}"/packages/Slackware/languages/ati-packager.${EXT} ]; then
	local FILE="/packages/Slackware/languages/ati-packager.${EXT}";
    fi
    
    local IFS=$(echo -e '\n\t');
    MESSAGE=($(cat "${PWD}"$FILE));
    
    return;
}

case $1 in
    --get-supported)
	echo -e "All\tOnly_Module\tOnly_X";
	;;
    --buildpkg)
	_set_builder_language;
	_check_builder_dependencies;
	_init_env;
	echo -e "\n${MESSAGE[0]} $BUILD_VER"\
		"\n--------------------------------------------"\
		"\n${MESSAGE[1]}"\
		"\n${MESSAGE[2]}"\
		"\n${MESSAGE[3]}\n";
	_buildpkg $2;
	;;
    *)
	echo "${1}: unsupported option passed by ati-installer.sh";
	;;
esac