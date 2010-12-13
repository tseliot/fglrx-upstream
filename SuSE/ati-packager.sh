#!/bin/sh
#
# Copyright (c) 2010, Sebastian Siebert (freespacer@gmx.de)
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

export LC_ALL=C
export LANG=C

. `dirname $0`/ati-packager-functions.sh
. `dirname $0`/supportedOS.sh

#Function: getSupportedPackages()
#Purpose: lists distribution supported packages
getSupportedPackages()
{
    for POSITION in $(seq 0 32)
    do
        # break if the value is empty
        if [ -z "${SUSE[$POSITION]}" ]; then
            break;
        fi

        # get the SUSE-Version
        SUSE_VERSION=`echo "${SUSE[$POSITION]}" | cut -f1 -d" "`
        ARCH_XORG_LIST=`echo "${SUSE[$POSITION]}" | cut -f2- -d" "`

        # list all available version of openSUSE and SLE
        for ARCH_XORG in ${ARCH_XORG_LIST}
        do
            ARCH=`echo ${ARCH_XORG} | cut -f1 -d"-"`
            echo "${SUSE_VERSION}-${ARCH}"
        done
    done
}

#Function: buildPackage()
#Purpose: build the requested package if it is supported
buildPackage()
{
    PACKAGE_NAME=$1

    debugMsg "Verbose mode:  on" && print_okay
    debugMsg "Verbose level: ${VERBOSE_LEVEL}" && print_okay

    if [ "${VERBOSE_LEVEL}" = "2" ]; then
        VERBOSE_2_LINE_BREAK='\n'
    fi

    debugMsg "Get information about the machine architecture and the version of SUSE and XOrg ...\n"
    for POSITION in $(seq 0 32)
    do
        # break if the value is empty
        if [ -z "${SUSE[$POSITION]}" ]; then
            break;
        fi

        # get the SUSE-Version
        SUSE_VERSION=`echo "${SUSE[$POSITION]}" | cut -f1 -d" "`
        ARCH_XORG_LIST=`echo "${SUSE[$POSITION]}" | cut -f2- -d" "`

        # list all available version of openSUSE and SLE
        for ARCH_XORG in ${ARCH_XORG_LIST}
        do
            ARCH=`echo ${ARCH_XORG} | cut -f1 -d"-"`
            XORG=`echo ${ARCH_XORG} | cut -f2 -d"-"`
            if [ "${PACKAGE_NAME}" = "${SUSE_VERSION}-${ARCH}" ]; then
                debugMsg "   Package name: ${PACKAGE_NAME}\n"
                debugMsg "   Distribution: ${SUSE_VERSION}\n"
                debugMsg "   Architecture: ${ARCH}\n"
                debugMsg "   XOrg version: ${XORG}"
                print_okay
                break 2
            fi
        done
    done

    debugMsg "Assemble the package name for rpm build ...\n"
    if [ "${ARCH}" = "IA32" ]; then
        PACKAGE_NAME="fglrx_${XORG:1:1}_${XORG:2:1}_${XORG:3:1}_${SUSE_VERSION}"
    elif [ "${ARCH}" = "AMD64" ]; then
        PACKAGE_NAME="fglrx64_${XORG:1:1}_${XORG:2:1}_${XORG:3:1}_${SUSE_VERSION}"
    fi
    debugMsg "   Package name: ${PACKAGE_NAME}" && print_okay

    # set needed variables
    DISTRO_PATH=`cd $(dirname $0) 2>/dev/null && pwd` \
        || checkReturnOutput $? "Could not get the path of distro packaging!"
    debugMsg "Path to the distro packaging:\n   ${DISTRO_PATH}" && print_okay
    INSTALLER_PATH=`pwd` \
        || checkReturnOutput $? "Could not get the path of installer!"
    debugMsg "Path to the installer:\n   ${INSTALLER_PATH}" && print_okay
    TMP_BUILD_OUTPUT="$(mktemp /tmp/ati_pkg_build.out.XXXXXX)" \
        || checkReturnOutput $? "Could not create a temp file in /tmp for the build output!"
    debugMsg "Temporary path to the output from the build:\n   ${TMP_BUILD_OUTPUT}" && print_okay
    TMP_BUILD_PATH="$(mktemp -d /tmp/ati_fglrx.XXXXXX)" \
        || checkReturnOutput $? "Could not create a temp directory in /tmp for the build of rpm file!"
    debugMsg "Temporary path to the build:\n   ${TMP_BUILD_PATH}" && print_okay
    TMP_SPEC_FILE="$(mktemp /tmp/ati_fglrx.spec.XXXXXX)" \
        || checkReturnOutput $? "Could not create a temp file in /tmp for the spec file!"
    debugMsg "Temporary path to the spec file:\n   ${TMP_SPEC_FILE}" && print_okay

    debugMsg "Get the architecture for the ATI arch path: "
    if [ "${ARCH}" = "IA32" ]; then
        ATI_ARCH="x86"
    elif [ "${ARCH}" = "AMD64" ]; then
        ATI_ARCH="x86_64"
    fi
    debugMsg "${ATI_ARCH}" && print_okay

    SPEC_FILE="${DISTRO_PATH}/fglrx.spec"
    debugMsg "Path to the spec file: ${SPEC_FILE}" && print_okay

    VERBOSE_OPTION=""
    if [ "${VERBOSE_LEVEL}" = "2" ]; then
        if [ "${VERBOSE}" = "yes" -o "${VERBOSE}" = "true" -o "${VERBOSE}" = "1" ]; then
            VERBOSE_OPTION="-v"
        fi
    fi

    # create needed directory
    debugMsg "Create needed directory ...${VERBOSE_2_LINE_BREAK}"
    mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/etc/{init.d,modprobe.d,pam.d} \
        || checkReturnOutput $?
    mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/{bin,include,sbin} \
        || checkReturnOutput $?
    mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/lib/dri \
        || checkReturnOutput $?
    mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/src/kernel-modules/fglrx \
        || checkReturnOutput $?
    mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/share/{applications,ati,man,pixmaps} \
        || checkReturnOutput $?
    mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/share/doc/packages/fglrx/patches \
        || checkReturnOutput $?
    mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/X11R6/lib \
        || checkReturnOutput $?
    if [ "${ARCH}" = "IA32" ]; then
        mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/lib/xorg/modules/{drivers,linux,updates} \
            || checkReturnOutput $?
#        mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/lib/xorg/modules/updates/extensions \
#            || checkReturnOutput $?
        if [ "${SUSE_VERSION}" != "SLE10" ]; then
            mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/lib/pm-utils/power.d \
                || checkReturnOutput $?
        else
            mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/lib/powersave/scripts \
                || checkReturnOutput $?
        fi
    elif [ "${ARCH}" = "AMD64" ]; then
        mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/lib64/dri \
            || checkReturnOutput $?
        mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/X11R6/lib64 \
            || checkReturnOutput $?
        mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/lib64/xorg/modules/{drivers,linux,updates} \
            || checkReturnOutput $?
#        mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/lib64/xorg/modules/updates/extensions \
#            || checkReturnOutput $?
        if [ "${SUSE_VERSION}" != "SLE10" ]; then
            mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/lib64/pm-utils/power.d \
                || checkReturnOutput $?
        else
            mkdir ${VERBOSE_OPTION} -p ${TMP_BUILD_PATH}/usr/lib64/powersave/scripts \
                || checkReturnOutput $?
        fi
    fi
    print_okay

    # copy all needed files into $TMP_BUILD_PATH
    debugMsg "Copy all needed files into temporary build path ...${VERBOSE_2_LINE_BREAK}"
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/etc ${TMP_BUILD_PATH} \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/lib/modules/fglrx/build_mod/* ${TMP_BUILD_PATH}/usr/src/kernel-modules/fglrx \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/X11R6/bin/* ${TMP_BUILD_PATH}/usr/bin \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/X11R6/include/* ${TMP_BUILD_PATH}/usr/include \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/include/* ${TMP_BUILD_PATH}/usr/include \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/sbin/* ${TMP_BUILD_PATH}/usr/sbin \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/share/applications/* ${TMP_BUILD_PATH}/usr/share/applications \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/share/ati/* ${TMP_BUILD_PATH}/usr/share/ati \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/share/doc/amdcccle/* ${TMP_BUILD_PATH}/usr/share/doc/packages/fglrx \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/share/doc/fglrx/* ${TMP_BUILD_PATH}/usr/share/doc/packages/fglrx \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/share/icons/* ${TMP_BUILD_PATH}/usr/share/pixmaps \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/share/man/* ${TMP_BUILD_PATH}/usr/share/man \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/common/usr/src/ati/* ${TMP_BUILD_PATH}/usr/share/doc/packages/fglrx \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/lib/modules/fglrx/build_mod/* ${TMP_BUILD_PATH}/usr/src/kernel-modules/fglrx \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/X11R6/bin/* ${TMP_BUILD_PATH}/usr/bin \
        || checkReturnOutput $?
    if [ "${ARCH}" = "IA32" ]; then
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/X11R6/lib/{libAMD*,libXvBAW*,libati*} ${TMP_BUILD_PATH}/usr/lib \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/X11R6/lib/modules/dri/* ${TMP_BUILD_PATH}/usr/lib/dri \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/X11R6/lib/{libGL*,libfglrx*} ${TMP_BUILD_PATH}/usr/X11R6/lib \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/lib/* ${TMP_BUILD_PATH}/usr/lib \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/${XORG}/usr/X11R6/lib/modules/* ${TMP_BUILD_PATH}/usr/lib/xorg/modules \
            || checkReturnOutput $?
        mv ${VERBOSE_OPTION} ${TMP_BUILD_PATH}/usr/lib/xorg/modules/extensions ${TMP_BUILD_PATH}/usr/lib/xorg/modules/updates/ \
            || checkReturnOutput $?
        if [ "${SUSE_VERSION}" != "SLE10" ]; then
            cp ${VERBOSE_OPTION} ${DISTRO_PATH}/ati-powermode.sh ${TMP_BUILD_PATH}/usr/lib/pm-utils/power.d/ \
                || checkReturnOutput $?
        else
            cp ${VERBOSE_OPTION} ${DISTRO_PATH}/{ati-powermode.sh,toggle-lvds.sh} ${TMP_BUILD_PATH}/usr/lib/powersave/scripts/ \
                || checkReturnOutput $?
        fi
    elif [ "${ARCH}" = "AMD64" ]; then
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/X11R6/lib64/{libAMD*,libXvBAW*,libati*} ${TMP_BUILD_PATH}/usr/lib64 \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/X11R6/lib64/modules/dri/* ${TMP_BUILD_PATH}/usr/lib64/dri \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/X11R6/lib64/{libGL*,libfglrx*} ${TMP_BUILD_PATH}/usr/X11R6/lib64 \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/lib64/* ${TMP_BUILD_PATH}/usr/lib64 \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/x86/usr/X11R6/lib/{libAMD*,libXvBAW*,libati*} ${TMP_BUILD_PATH}/usr/lib \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/x86/usr/X11R6/lib/modules/dri/* ${TMP_BUILD_PATH}/usr/lib/dri \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/x86/usr/X11R6/lib/{libGL*,libfglrx*} ${TMP_BUILD_PATH}/usr/X11R6/lib \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/x86/usr/lib/* ${TMP_BUILD_PATH}/usr/lib \
            || checkReturnOutput $?
        cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/${XORG}/usr/X11R6/lib64/modules/* ${TMP_BUILD_PATH}/usr/lib64/xorg/modules \
            || checkReturnOutput $?
        mv ${VERBOSE_OPTION} ${TMP_BUILD_PATH}/usr/lib64/xorg/modules/extensions ${TMP_BUILD_PATH}/usr/lib64/xorg/modules/updates/ \
            || checkReturnOutput $?
        if [ "${SUSE_VERSION}" != "SLE10" ]; then
            cp ${VERBOSE_OPTION} ${DISTRO_PATH}/ati-powermode.sh ${TMP_BUILD_PATH}/usr/lib64/pm-utils/power.d/ \
                || checkReturnOutput $?
        else
            cp ${VERBOSE_OPTION} ${DISTRO_PATH}/{ati-powermode.sh,toggle-lvds.sh} ${TMP_BUILD_PATH}/usr/lib64/powersave/scripts/ \
                || checkReturnOutput $?
        fi
    fi
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/sbin/* ${TMP_BUILD_PATH}/usr/sbin \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} -R ${INSTALLER_PATH}/arch/${ATI_ARCH}/usr/share/ati/* ${TMP_BUILD_PATH}/usr/share/ati \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} ${DISTRO_PATH}/atieventsd.sh ${TMP_BUILD_PATH}/etc/init.d/atieventsd \
        || checkReturnOutput $?
    # replace authatieventsd.sh
    rm ${VERBOSE_OPTION} -f ${TMP_BUILD_PATH}/etc/ati/authatieventsd.sh \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} ${DISTRO_PATH}/authatieventsd.sh ${TMP_BUILD_PATH}/etc/ati/authatieventsd.sh \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} ${DISTRO_PATH}/fglrx-kernel-build.sh ${TMP_BUILD_PATH}/usr/bin \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} ${DISTRO_PATH}/boot.fglrxrebuild ${TMP_BUILD_PATH}/etc/init.d \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} ${DISTRO_PATH}/README.SuSE ${TMP_BUILD_PATH}/usr/share/doc/packages/fglrx \
        || checkReturnOutput $?
    cp ${VERBOSE_OPTION} ${DISTRO_PATH}/fglrx.png ${TMP_BUILD_PATH}/usr/share/pixmaps \
        || checkReturnOutput $?
    echo "blacklist radeon" >${TMP_BUILD_PATH}/etc/modprobe.d/fglrx.conf \
        || checkReturnOutput $?
    print_okay

    # copy patch files to the $TMP_BUILD_PATH
    debugMsg "Copy patch files to the temporary build path ...${VERBOSE_2_LINE_BREAK}"
    cp ${VERBOSE_OPTION} -R ${DISTRO_PATH}/*.patch ${TMP_BUILD_PATH}/usr/share/doc/packages/fglrx/patches
    checkReturnOutput $?

    # clean up temp dir
    debugMsg "Remove unneeded files in the temporary build path ...${VERBOSE_2_LINE_BREAK}"
    rm ${VERBOSE_OPTION} ${TMP_BUILD_PATH}/usr/src/kernel-modules/fglrx/make.sh \
        || checkReturnOutput $?
    rm ${VERBOSE_OPTION} -r ${TMP_BUILD_PATH}/usr/share/doc/packages/fglrx/examples \
        || checkReturnOutput $?
    print_okay

    # substitute variables in the specfile
    debugMsg "Substitute variables in the temporary spec file ...${VERBOSE_2_LINE_BREAK}"
    sed -f - ${DISTRO_PATH}/fglrx.spec > ${TMP_SPEC_FILE} <<END_SED_SCRIPT
s!%PACKAGE_NAME!${PACKAGE_NAME}!
s!%ATI_DRIVER_VERSION!`./ati-packager-helper.sh --version`!
s!%ATI_DRIVER_RELEASE!`./ati-packager-helper.sh --release`!
s!%ATI_DRIVER_DESCRIPTION!`./ati-packager-helper.sh --description`!
s!%ATI_DRIVER_URL!`./ati-packager-helper.sh --url`!
s!%ATI_DRIVER_VENDOR!`./ati-packager-helper.sh --vendor`!
s!%ATI_DRIVER_SUMMARY!`./ati-packager-helper.sh --summary`!
s!%ATI_DRIVER_BUILD_ROOT!${TMP_BUILD_PATH}!
END_SED_SCRIPT
    if [ $? -ne 0 ]; then
        print_failure
        exit 1
    fi
    print_okay

    # build the package
    debugMsg "Build the rpm package now ..."
    


    if [ "${ARCH}" = "IA32" ]; then
        if [ "${VERBOSE_LEVEL}" = "2" ]; then
            rpmbuild -bb --target i586 ${TMP_SPEC_FILE} 2>&1 | tee ${TMP_BUILD_OUTPUT}
        else
            rpmbuild -bb --target i586 ${TMP_SPEC_FILE} > ${TMP_BUILD_OUTPUT} 2>&1
        fi
    elif [ "${ARCH}" = "AMD64" ]; then
        if [ "${VERBOSE_LEVEL}" = "2" ]; then
            rpmbuild -bb --target x86_64 ${TMP_SPEC_FILE} 2>&1 | tee ${TMP_BUILD_OUTPUT}
        else
            rpmbuild -bb --target x86_64 ${TMP_SPEC_FILE} > ${TMP_BUILD_OUTPUT} 2>&1
        fi
    fi
    if [ -n "`grep 'RPM build errors' ${TMP_BUILD_OUTPUT}`" ]; then
        echo -n -e "\n"
        tail -n 20 ${TMP_BUILD_OUTPUT}
        echo "Package build failed!"
        print_failure
        rm -f ${TMP_SPEC_FILE} > /dev/null
        rm -f ${TMP_BUILD_OUTPUT} > /dev/null
        rm -rf ${TMP_BUILD_PATH} > /dev/null
        rm -f ${PACKAGE_FILE}
        exit 1
    fi
    print_okay

    # retrieve the absolute path to the built package
    debugMsg "Retrieve the absolute path to the built package ..."
    PACKAGE_STR=`grep "Wrote: .*\.rpm" ${TMP_BUILD_OUTPUT}`             # String containing info where the package was created
    PACKAGE_FILE_WITH_PATH=`expr "${PACKAGE_STR}" : 'Wrote: \(.*\)'`    # Absolute path to the create package file
    PACKAGE_FILE=`basename ${PACKAGE_FILE_WITH_PATH}`
    print_okay

    # after-build diagnostics and processing
    debugMsg "After-build diagnostics and processing ...\n"
    INSTALLER_PARENT_PATH=`cd ${INSTALLER_PATH}/.. 2>/dev/null && pwd`  # Absolute path to the installer parent directory
    cp ${PACKAGE_FILE_WITH_PATH} ${INSTALLER_PARENT_PATH}               # Copy the created package to the directory where the self-extracting driver archive is located
    echo -n -e "\nPackage ${INSTALLER_PARENT_PATH}/${PACKAGE_FILE} has been successfully generated\n"
    echo -n -e "\nInstall or update the RPM package as follows:\n\n   zypper install ${PACKAGE_FILE}\n\n"
    print_okay

    # clean-up
    debugMsg "Remove unneeded paths and files ...${VERBOSE_2_LINE_BREAK}"
    rm ${VERBOSE_OPTION} -f ${TMP_SPEC_FILE} \
        || checkReturnOutput $?
    rm ${VERBOSE_OPTION} -f ${TMP_BUILD_OUTPUT} \
        || checkReturnOutput $?
    rm ${VERBOSE_OPTION} -rf ${TMP_BUILD_PATH} \
        || checkReturnOutput $?
    rm ${VERBOSE_OPTION} -f ${PACKAGE_FILE_WITH_PATH} \
        || checkReturnOutput $?
    print_okay

    debugMsg "Finished!" && print_okay

    exit 0
}

#Starting point of this script, process the {action} argument

#Requested action
ACTION=$1

case "${ACTION}" in
--get-supported)
    getSupportedPackages
    ;;
--buildpkg)
    PACKAGE=$2
    if [ "${PACKAGE}" = "SUSE-autodetection" ]; then
        echo "Auto detection mode:"
        if [ -f "/etc/SuSE-release" ]; then
            SUSE_NAME=`head -n 1 /etc/SuSE-release | cut -f1 -d" "`
            SUSE_VERSION=`grep VERSION /etc/SuSE-release | sed -e 's/VERSION\s=\s//g'`

            if [ "${SUSE_NAME}" = "openSUSE" ]; then
                ATI_SUSE_NAME="SUSE"
            else
                ATI_SUSE_NAME="SLE"
            fi

            ATI_SUSE_VERSION=`echo "${SUSE_VERSION}" | sed -e 's/\.//g'`

            ARCH="$(uname -m)"
            case "${ARCH}" in
                i?86)
                    ATI_ARCH="IA32"
                    ;;
                x86_64)
                    ATI_ARCH="AMD64"
                    ;;
            esac

            PACKAGE="${ATI_SUSE_NAME}${ATI_SUSE_VERSION}-${ATI_ARCH}"

            echo "   Distribution: ${SUSE_NAME}"
            echo "   Version:      ${SUSE_VERSION}"
            echo "   Architecture: ${ARCH}"
            echo "   Package name: ${ATI_SUSE_NAME}${ATI_SUSE_VERSION}-${ATI_ARCH}"
        fi
    fi

    if [ "${PACKAGE}" != "" ]; then
        SUPPORT_FLAG="false"
        for SUPPORTED_LIST in `getSupportedPackages`
        do
            if [ "${SUPPORTED_LIST}" = "${PACKAGE}" ]; then
                SUPPORT_FLAG="true"
                break
            fi
        done
        if [ "${SUPPORT_FLAG}" = "true" ]; then
            buildPackage ${PACKAGE}
        else
            echo "Requested package is not supported."
        fi
    else
        echo "Please provide package name"
    fi
    exit 0
    ;;
*|--*)
    echo "${ACTION}: unsupported option passed by ati-installer.sh"
    exit 0
    ;;
esac
