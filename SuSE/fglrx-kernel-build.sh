#!/bin/sh

linuxsrc=/lib/modules/$(uname -r)/build
linuxinclude=/lib/modules/$(uname -r)/source/include

if [ ! -d "$linuxsrc" ]; then
  echo
  echo "*************************************************************"
  echo "Package \"kernel-source\" needs to be installed by YaST2 first!"
  echo "*************************************************************"
  echo
  exit 1
fi

if [ ! -x /usr/bin/make ]; then
  echo
  echo "****************************************************"
  echo "Package \"make\" needs to be installed by YaST2 first!"
  echo "****************************************************"
  echo
  exit 1
fi

if [ ! -x /usr/bin/gcc ]; then
  echo
  echo "**************************************************"
  echo "Package \"gcc\" needs to be installed by YaST2 first!"
  echo "**************************************************"
  echo
  exit 1
fi

# resolve if we are building for a kernel with a fix for CVE-2010-3081
# On kernels with the fix, use arch_compat_alloc_user_space instead
# of compat_alloc_user_space since the latter is GPL-only
COMPAT_ALLOC_USER_SPACE=compat_alloc_user_space

src_file=$linuxinclude/../arch/x86/include/asm/compat.h
if [ ! -e $src_file ];
then
  src_file=$linuxinclude/asm-x86_64/compat.h
fi
if [ ! -e $src_file ];
then
  echo "Warning:"
  echo "kernel includes at $linuxincludes not found or incomplete"
  echo "file: $src_file"
  echo ""
else
  if [ `cat $src_file | grep -c arch_compat_alloc_user_space` -gt 0 ]
  then
    COMPAT_ALLOC_USER_SPACE=arch_compat_alloc_user_space
  fi
  echo "file $src_file says: COMPAT_ALLOC_USER_SPACE=$COMPAT_ALLOC_USER_SPACE"
fi

pushd /usr/src/kernel-modules/fglrx
  make -C $linuxsrc M=$PWD MODFLAGS="-DMODULE -DATI -DFGL -DCOMPAT_ALLOC_USER_SPACE=$COMPAT_ALLOC_USER_SPACE"
  if [ $? -ne 0 ]; then
    echo 
    echo "******************************"
    echo "Build of kernel module failed!"
    echo "******************************"
    echo
    exit 1
  fi
  make -C $linuxsrc M=$PWD modules_install
  if [ $? -ne 0 ]; then
    echo 
    echo "*************************************"
    echo "Installation of kernel module failed!"
    echo "*************************************"
    echo
    exit 1
  fi
  make -C $linuxsrc M=$PWD clean
  depmod -a
popd

exit 0
