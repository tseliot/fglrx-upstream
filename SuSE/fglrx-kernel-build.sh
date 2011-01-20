#!/bin/sh
#
# Copyright (c) 2010 Sebastian Siebert (freespacer@gmx.de)
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


# Get number of CPU cores to speed up compilation on multi-core machines.
NUM_CORES="`cat /proc/cpuinfo | grep '^processor' | wc -l | grep -E '^[0-9]+$'`";

# If CPU cores could not detected, used only 1 core for compilation.
if [ ! "${NUM_CORES}" -gt 0 ]; then
    NUM_CORES=1
fi

echo -e "\nUsed CPUs/Cores for compilation   =>   [\e[1;32m ${NUM_CORES} \e[0m]"

# compile only supported kernels

KERNEL_LIST="`rpm -q kernel kernel-desktop kernel-default kernel-pae | grep -v 'not installed' | sort`"
SUMMARY_REPORT=""
ERROR_CODE=0

for KERNEL in ${KERNEL_LIST}
do
    KERNEL_LIBRARY="`rpm --list -q ${KERNEL} | sort | grep -m 1 '/lib/modules/'`"
    LINUX_SOURCE="${KERNEL_LIBRARY}/build"
    LINUX_INCLUDE="${KERNEL_LIBRARY}/source/include"
    echo -e "\n\n"
    printf '*%.0s' $(seq 1 80) && echo -n -e "\n"
    echo "*   Kernel:  ${KERNEL}`printf ' %.0s' $(seq 1 $[66-${#KERNEL}])`*"
    echo "*   Source:  ${LINUX_SOURCE}`printf ' %.0s' $(seq 1 $[66-${#LINUX_SOURCE}])`*"
    echo "*   Include: ${LINUX_INCLUDE}`printf ' %.0s' $(seq 1 $[66-${#LINUX_INCLUDE}])`*"
    printf '*%.0s' $(seq 1 80) && echo -n -e "\n"
    echo -e "\n\n"

    # resolve if we are building for a kernel with a fix for CVE-2010-3081
    # On kernels with the fix, use arch_compat_alloc_user_space instead
    # of compat_alloc_user_space since the latter is GPL-only
    COMPAT_ALLOC_USER_SPACE=compat_alloc_user_space

    SOURCE_FILE=${LINUX_INCLUDE}/../arch/x86/include/asm/compat.h
    if [ ! -e ${SOURCE_FILE} ]; then
        SOURCE_FILE=${LINUX_INCLUDE}/asm-x86_64/compat.h
    fi
    if [ ! -e ${SOURCE_FILE} ]; then
        echo "Warning:"
        echo "kernel includes at ${LINUX_INCLUDE} not found or incomplete"
        echo "file: ${SOURCE_FILE}"
        echo  -n -e "\n"
    else
        if [ `cat ${SOURCE_FILE} | grep -c arch_compat_alloc_user_space` -gt 0 ]; then
            COMPAT_ALLOC_USER_SPACE=arch_compat_alloc_user_space
        fi
        echo "file ${SOURCE_FILE} says: COMPAT_ALLOC_USER_SPACE=${COMPAT_ALLOC_USER_SPACE}"
    fi
    pushd /usr/src/kernel-modules/fglrx/2.6.x
        make clean
        cp ../{*.h,*.c,*.a} .
        SUMMARY_REPORT="${SUMMARY_REPORT}\n   Kernel   => ${KERNEL}\n"
        make -j${NUM_CORES} -C ${LINUX_SOURCE} M=${PWD} MODFLAGS="-DMODULE -DATI -DFGL -DCOMPAT_ALLOC_USER_SPACE=${COMPAT_ALLOC_USER_SPACE}"
        if [ $? -ne 0 ]; then
            echo -n -e "\n"
            echo "******************************"
            echo "Build of kernel module failed!"
            echo "******************************"
            echo -n -e "\n"
            SUMMARY_REPORT="${SUMMARY_REPORT}   Build    => [\e[1;31m FAILURE \e[0m]\n"
            SUMMARY_REPORT="${SUMMARY_REPORT}   Install  => [\e[1;31m FAILURE \e[0m]\n"
            ERROR_CODE=1
        else
            SUMMARY_REPORT="${SUMMARY_REPORT}   Build    => [\e[1;32m OK \e[0m]\n"
            make -j${NUM_CORES} -C ${LINUX_SOURCE} M=${PWD} modules_install
            if [ $? -ne 0 ]; then
                echo -n -e "\n"
                echo "*************************************"
                echo "Installation of kernel module failed!"
                echo "*************************************"
                echo -n -e "\n"
                SUMMARY_REPORT="${SUMMARY_REPORT}   Install  => [\e[1;31m FAILURE \e[0m]\n"
                ERROR_CODE=1
            else
                SUMMARY_REPORT="${SUMMARY_REPORT}   Install  => [\e[1;32m OK \e[0m]\n"
            fi
        fi
        make clean
        if [ -f modules.order ]; then
            rm -f modules.order
        fi
    popd
done

echo "Calling 'depmod -a' this may take a while..."
depmod -a

echo -e "\n\nSummary report:"
printf '=%.0s' $(seq 1 80) && echo -n -e "\n"
echo -e "${SUMMARY_REPORT}"

exit ${ERROR_CODE}
