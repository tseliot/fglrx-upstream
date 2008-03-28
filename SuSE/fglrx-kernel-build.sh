#!/bin/sh

linuxsrc=/lib/modules/$(uname -r)/build

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

pushd /usr/src/kernel-modules/fglrx
  make -C $linuxsrc M=$PWD
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
