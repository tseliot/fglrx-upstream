#!/bin/sh

if [ ! -d /usr/src/linux ]; then
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
  rm -f Modules.symvers *.o *.ko *.mod.*
  make -C /lib/modules/$(uname -r)/build M=$(pwd)
  if [ $? -ne 0 ]; then
    echo 
    echo "******************************"
    echo "Build of kernel module failed!"
    echo "******************************"
    echo
    exit 1
  fi
  make -C /lib/modules/$(uname -r)/build M=$(pwd) modules_install
  if [ $? -ne 0 ]; then
    echo 
    echo "*************************************"
    echo "Installation of kernel module failed!"
    echo "*************************************"
    echo
    exit 1
  fi
  depmod -a
popd

exit 0
