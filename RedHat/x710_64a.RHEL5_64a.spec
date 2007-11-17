#############################################################################
# spec file header                                                          #
#############################################################################
Name: fglrx64_7_1_0
Summary: %ATI_DRIVER_SUMMARY
Version: %ATI_DRIVER_VERSION
Release: %ATI_DRIVER_RELEASE
License: Other License(s), see package
Vendor: %ATI_DRIVER_VENDOR
URL: %ATI_DRIVER_URL
Conflicts: fglrx-glc22
Conflicts: fglrx
Conflicts: fglrx_4_3_0
Conflicts: fglrx64_4_3_0
Conflicts: fglrx_6_8_0
Conflicts: fglrx64_6_8_0
Conflicts: fglrx_6_9_0
Conflicts: fglrx64_6_9_0
Conflicts: fglrx_7_1_0
Group: Servers
ExclusiveArch: x86_64

# local rpm options
%define __check_files   %{nil}

#############################################################################
# spec file description                                                     #
#############################################################################
%description
%ATI_DRIVER_DESCRIPTION

#############################################################################
# pre install actions                                                       #
#############################################################################
%pre

DRV_RELEASE=%ATI_DRIVER_VERSION

# policy layer initialization
_XVER_USER_SPEC="none"
NO_PRINT="1"
###Begin: check_sh - DO NOT REMOVE; used in b30specfile.sh ###

DetectX()
{
x_binaries="X Xorg XFree86"
x_dirs="/usr/X11R6/bin/ /usr/local/bin/ /usr/X11/bin/ /usr/bin/ /bin/"


for the_x_binary in ${x_binaries}; do
    x_full_dirs=""
    for x_tmp in ${x_dirs}; do
        x_full_dirs=${x_full_dirs}" "${x_tmp}${the_x_binary}
    done
    x_full_dirs=${x_full_dirs}" "`which ${the_x_binary}`
    for x_bin in ${x_full_dirs}; do 
        if [ -x ${x_bin} ];
        then
            # First, try to detect XFree86
            x_ver_num=`${x_bin} -version 2>&1 | grep 'XFree86 Version [0-9]\.' | sed -e 's/^.*XFree86 Version //' | cut -d' ' -f1`
	
        if [ "$x_ver_num" ]
        then
            X_VERSION="XFree86"
	    
            # Correct XFree86 version
            if [ `echo "$x_ver_num" | grep -c '^4\.0\.99'` -gt 0 ]
            then
                x_ver_num="4.1.0"
            fi
	
            if [ `echo "$x_ver_num" | grep -c '^4\.2\.99'` -gt 0 ]
            then
                x_ver_num="4.3.0"
            fi
        fi
	
        if [ -z "${X_VERSION}" ]
        then
            # XFree86 has not been detected, try to detect XOrg up to 7.2
            x_ver_num=`${x_bin} -version 2>&1 | grep 'X Window System Version [0-9]\.' | sed -e 's/^.*X Window System Version //' | cut -d' ' -f1`

            if [ "$x_ver_num" ]
            then
                X_VERSION="Xorg"

                if [ `echo "$x_ver_num" | grep -c '^6\.8\.99'` -gt 0 ]
                then
                    x_ver_num="6.9.0"
                fi

                if [ `echo "$x_ver_num" | grep -c '^7\.1\.1'` -gt 0 ]
                then
                    x_ver_num="7.1.1"
                fi
            fi
        fi
        
        if [ -z "${X_VERSION}" ]
        then
            # XOrg 7.2 or lower has not been detected, try to detect XOrg 7.3
            # We don't want to detect and run on anything higher than XOrg 7.3
            # because starting this version we use autodetection of video driver ABI
            # and we want to know that we need to test the driver if there is a major change
            # in the X server version
            xorg_server_ver_num=`${x_bin} -version 2>&1 | grep 'X\.Org X Server [0-9]\.[0-9]' | sed -e 's/^.*X\.Org X Server //' | cut -d' ' -f1`

            if [ "$xorg_server_ver_num" ]
            then
                if [ `echo "$xorg_server_ver_num" | grep -c '^1\.4'` -gt 0 ]
                then
                    X_VERSION="Xorg"
                    x_ver_num="7.3"
                fi
            fi
        fi
    fi
    if [ "${X_VERSION}" ]
    then
       break
    fi

    done
    if [ "${X_VERSION}" ]
    then
       break
    fi
done
# Produce the final X version string
if [ "${X_VERSION}" ]
then
    X_VERSION="${X_VERSION} ${x_ver_num}"
fi
}

########################################################################
# Begin of the main script


if [ "${NO_PRINT}" != "1" ]; then
    echo "Detected configuration:"
fi

# Detect system architecture
if [ "${NO_DETECT}" != "1" ]; then
    _ARCH=`uname -m`
fi

if [ "${NO_PRINT}" != "1" ]; then
    case ${_ARCH} in
        i?86)	arch_bits="32-bit";;
        x86_64)	arch_bits="64-bit";;
    esac

    echo "Architecture: ${_ARCH} (${arch_bits})"
fi

# Try to detect version of X, if X_VERSION is not set explicitly by the user
if [ -z "${X_VERSION}" ]; then
    # Detect X version
    if [ "${NO_DETECT}" != "1" ]; then
        DetectX
    fi

    if [ -z "${X_VERSION}" ]; then
        if [ "${NO_PRINT}" != "1" ]; then
            echo "X Server: unable to detect"
        fi
    else
        if [ "${NO_PRINT}" != "1" ]; then
            echo "X Server: ${X_VERSION}"
        fi

        if [ "${NO_DETECT}" != "1" ]; then
            # Generate internal name for the version of X
            x_name=`echo ${X_VERSION} | cut -d ' ' -f1`
            x_ver=`echo ${X_VERSION} | cut -d ' ' -f2`
            x_maj=`echo ${x_ver} | cut -d '.' -f1`
            x_min=`echo ${x_ver} | cut -d '.' -f2`
            x_ver_internal="x${x_maj}${x_min}0"
            # Map Xorg 7.3 to x710
            if [ "${x_name}" == "Xorg" -a ${x_maj} -eq 7 -a ${x_min} -eq 3 ]; then
                x_ver_internal=x710
            else
                # Workaround to set internal version number (for platform binary
                # directory) to handle modular X
                if [ ${x_maj} -lt 4 -o ${x_maj} -ge 7 ]; then
                    # X.org 7.0 is non-modular and is handled elsewhere
                    if [ "${x_ver_internal}" != "x700" ]; then
                        x_ver_internal=x710
                    fi
                fi
            fi
            
            X_VERSION=${x_ver_internal}

            if [ "${_ARCH}" = "x86_64" ]; then
                X_VERSION=${X_VERSION}_64a
            fi
        fi
    fi
else
    # If X_VERSION was set by the user, don't try to detect X, just use user's value
    if [ "${NO_PRINT}" != "1" ]; then

        # see --nodetect and --override in check.sh header for explanation
        if [ "${NO_DETECT}" = "1" ]; then
            if [ "${OVERRIDE}" = "1" ]; then
                OVERRIDE_STRING=" (OVERRIDEN BY USER)" 
            else
                OVERRIDE_STRING=""
            fi
        else
            OVERRIDE_STRING=" (OVERRIDEN BY USER)" 
        fi

        if [ -x map_xname.sh ]; then
            echo "X Server${OVERRIDE_STRING}: `./map_xname.sh ${X_VERSION}`"
        else
            echo "X Server${OVERRIDE_STRING}: ${X_VERSION} (lookup failed)"
        fi
    fi
fi

# unset values in case this script is sourced again
unset NO_PRINT
unset NO_DETECT
unset OVERRIDE

###End: check_sh - DO NOT REMOVE; used in b30specfile.sh ###
###Begin: interfaceversion - DO NOT REMOVE; used in b30specfile.sh ###

# Version of the policy interface that this script supports; see WARNING in
#  default_policy.sh header for more details
DEFAULT_POLICY_INTERFACE_VERSION=2

###End: interfaceversion - DO NOT REMOVE; used in b30specfile.sh ###
###Begin: printversion - DO NOT REMOVE; used in b30specfile.sh ###
    _XVER_DETECTED=$X_VERSION

    if [ "${_ARCH}" = "x86_64" -a -d "/usr/lib32" ]
    then
        _LIBDIR32=lib32
    else
        _LIBDIR32=lib
    fi

    _UNAME_R=`uname -r`

    # NOTE: increment DEFAULT_POLICY_INTEFACE_VERSION when interface changes;
    #  see WARNING in header of default_policy.sh for details
    POLICY_VERSION="default:v${DEFAULT_POLICY_INTERFACE_VERSION}:${_ARCH}:${_LIBDIR32}:${_XVER_DETECTED}:${_XVER_USER_SPEC}:${_UNAME_R}"
###End: printversion - DO NOT REMOVE; used in b30specfile.sh ###
version=${POLICY_VERSION}
###Begin: printpolicy - DO NOT REMOVE; used in b30specfile.sh ###

    # NOTE: increment DEFAULT_POLICY_INTEFACE_VERSION when interface changes;
    #  see WARNING in header of default_policy.sh for details

    INPUT_POLICY_NAME=`echo ${version} | cut -d: -f1`
    INPUT_INTERFACE_VERSION=`echo ${version} | cut -d: -f2`
    ARCH=`echo ${version} | cut -d: -f3`
    LIBDIR32=`echo ${version} | cut -d: -f4`
    XVER_DETECTED=`echo ${version} | cut -d: -f5`
    XVER_USER_SPEC=`echo ${version} | cut -d: -f6`
    UNAME_R=`echo ${version} | cut -d: -f7`
    REMAINDER=`echo ${version} | cut -d: -f8`


    ### Step 2: ensure variables from version string are sane and compatible ###

    ERROR_MESSAGE="error: ${version} is not supported"

    # verify policy name matches the one this script was designed for
    if [ "${INPUT_POLICY_NAME}" != "default" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # verify interface version matches the one this script was designed for
    if [ "${INPUT_INTERFACE_VERSION}" != "v${DEFAULT_POLICY_INTERFACE_VERSION}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check ARCH for sanity
    case "${ARCH}" in
    i?86 | x86_64)
        ;;
    *)
        echo ${ERROR_MESSAGE}
        exit 1
        ;;
    esac

    # check LIBDIR32 for sanity
    if [ "${LIBDIR32}" != "lib" -a "${LIBDIR32}" != "lib32" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check XVER_DETECTED for sanity
    echo ${XVER_DETECTED} | grep -q '^x[1-9][0-9]0_64a$'
    RETVAL64=$?
    echo ${XVER_DETECTED} | grep -q '^x[1-9][0-9]0$'
    RETVAL32=$?
    if [ ${RETVAL64} -ne 0 -a ${RETVAL32} -ne 0 ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check XVER_USER_SPEC for sanity
    echo ${XVER_USER_SPEC} | grep -q '^x[1-9][0-9]0_64a$'
    RETVAL64=$?
    echo ${XVER_USER_SPEC} | grep -q '^x[1-9][0-9]0$'
    RETVAL32=$?
    if [ ${RETVAL64} -ne 0 -a ${RETVAL32} -ne 0 -a "${XVER_USER_SPEC}" != "none" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check UNAME_R for sanity
    if [ -z "${UNAME_R}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # verify there are no extra fields
    if [ -n "${REMAINDER}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi


    ### Step 3: determine variable values based on version string ###

    # determine which XVER will be used as the final X_VERSION
    if [ "${XVER_USER_SPEC}" != "none" ]
    then
        XVER=${XVER_USER_SPEC}
    else
        XVER=${XVER_DETECTED}
    fi

    # set paths specific to the X version
    XVER_MAJOR=`echo ${XVER} | cut -c2`
    if [ $XVER_MAJOR -ge 7 ]
    then
        LIB_PREFIX_32=/usr/${LIBDIR32}/xorg
        LIB_PREFIX_64=/usr/lib64/xorg
        DRV_PREFIX_32=/usr/${LIBDIR32}
        DRV_PREFIX_64=/usr/lib64

        ATI_X_BIN=/usr/bin
        ATI_X11_INCLUDE=/usr/include/X11/extensions
    else
        LIB_PREFIX_32=/usr/X11R6/${LIBDIR32}
        LIB_PREFIX_64=/usr/X11R6/lib64
        DRV_PREFIX_32=/usr/X11R6/lib/modules
        DRV_PREFIX_64=/usr/X11R6/lib64/modules

        ATI_X_BIN=/usr/X11R6/bin
        ATI_X11_INCLUDE=/usr/X11R6/include/X11/extensions
    fi

    # set paths specific to the architecture
    if [ "${ARCH}" = "x86_64" ]
    then
        ATI_XLIB=${LIB_PREFIX_64}

        ATI_XLIB_32=${LIB_PREFIX_32}
        ATI_XLIB_64=${LIB_PREFIX_64}
        ATI_3D_DRV_32=${DRV_PREFIX_32}/dri
        ATI_3D_DRV_64=${DRV_PREFIX_64}/dri
    else
        ATI_XLIB=${LIB_PREFIX_32}

        ATI_XLIB_32=${LIB_PREFIX_32}
        ATI_XLIB_64=
        ATI_3D_DRV_32=${DRV_PREFIX_32}/dri
        ATI_3D_DRV_64=
    fi

    # set the variables; we need to do it this way (setting the variables
    #  then printing the variable/value pairs) because the b30specfile.sh needs
    #  the variables set

        ATI_SBIN=/usr/sbin
    ATI_KERN_MOD=/lib/modules/fglrx
      ATI_2D_DRV=${ATI_XLIB}/modules/drivers
    ATI_X_MODULE=${ATI_XLIB}/modules
     ATI_DRM_LIB=${ATI_XLIB}/modules/linux
 ATI_CP_KDE3_LNK=/opt/kde3/share/applnk
  ATI_GL_INCLUDE=/usr/include/GL
  ATI_CP_KDE_LNK=/usr/share/applnk
         ATI_DOC=/usr/share/doc/ati
ATI_CP_GNOME_LNK=/usr/share/gnome/apps
        ATI_ICON=/usr/share/icons
         ATI_MAN=/usr/share/man
         ATI_SRC=/usr/src/ati
      ATI_CP_BIN=${ATI_X_BIN}
     ATI_CP_I18N=/usr/share/ati/amdcccle
   ATI_KERN_INST=/lib/modules/${UNAME_R}/kernel/drivers/char/drm
         ATI_LOG=/usr/share/ati
      ATI_CONFIG=/etc/ati
      ATI_UNINST=/usr/share/ati

###End: printpolicy - DO NOT REMOVE; used in b30specfile.sh ###


##############################################################
# COMMON HEADER: Initialize variables and declare subroutines

BackupInstPath()
{
    if [ ! -d /etc/ati ]
    then
        # /etc/ati is not a directory or doesn't exist so no backup is required
        return 0
    fi

    if [ -n "$1" ]
    then
        FILE_PREFIX=$1
    else
        # client did not pass in FILE_PREFIX parameter and /etc/ati exists
        return 64
    fi

    if [ ! -f /etc/ati/$FILE_PREFIX ]
    then
        return 0
    fi

    COUNTER=0

    ls /etc/ati/$FILE_PREFIX.backup-${COUNTER} > /dev/null 2>&1
    RETURN_CODE=$?
    while [ 0 -eq $RETURN_CODE ]
    do
        COUNTER=$((${COUNTER}+1))
        ls /etc/ati/$FILE_PREFIX.backup-${COUNTER} > /dev/null 2>&1
        RETURN_CODE=$?
    done

    cp -p /etc/ati/$FILE_PREFIX /etc/ati/$FILE_PREFIX.backup-${COUNTER}

    RETURN_CODE=$?

    if [ 0 -ne $RETURN_CODE ]
    then
        # copy failed
        return 65
    fi

    return 0
}

# i.e., lib for 32-bit and lib64 for 64-bit.
if [ `uname -m` = "x86_64" ];
then
  LIB=lib64
else
  LIB=lib
fi

# LIB32 always points to the 32-bit libraries (native in 32-bit,
# 32-on-64 in 64-bit) regardless of the system native bitwidth.
# Use lib32 and lib64; if lib32 doesn't exist assume lib is for lib32
if [ -d "/usr/lib32" ]; then
  LIB32=lib32
else
  LIB32=lib
fi

#process INSTALLPATH, if it's "/" then need to purge it
#SETUP_INSTALLPATH is a Loki Setup environment variable
INSTALLPATH=${SETUP_INSTALLPATH}
if [ "${INSTALLPATH}" = "/" ]
then
    INSTALLPATH=""
fi

# project name and derived defines
MODULE=fglrx
IP_LIB_PREFIX=lib${MODULE}_ip

# general purpose paths
XF_BIN=${INSTALLPATH}${ATI_X_BIN}
XF_LIB=${INSTALLPATH}${ATI_XLIB}
OS_MOD=${INSTALLPATH}`dirname ${ATI_KERN_MOD}`
USR_LIB=${INSTALLPATH}/usr/${LIB}
MODULE=`basename ${ATI_KERN_MOD}`

#FGLRX install log
LOG_PATH=${INSTALLPATH}${ATI_LOG}
LOG_FILE=${LOG_PATH}/fglrx-install.log
if [ ! -e ${LOG_PATH} ]
then
  mkdir -p ${LOG_PATH} 2>/dev/null 
fi
if [ ! -e ${LOG_FILE} ]
then
  touch ${LOG_FILE}
fi

#DKMS version
DKMS_VER=`dkms -V 2> /dev/null | cut -d " " -f2`

#DKMS expects kernel module sources to be placed under this directory
DKMS_KM_SOURCE=/usr/src/${MODULE}-${DRV_RELEASE}

# END OF COMMON HEADER
#######################
##################
# PREINSTALLATION

###Begin: pre_drv ###
# manage lib dir contents

  # determine which lib dirs are of relevance in current system
  /sbin/ldconfig -v -N -X 2>/dev/null | sed -e 's/ (.*)$//g' | sed -n -e '/^\/.*:$/s/:$//p' >libdirs.txt

  # remove all invalid paths to simplify the following code  
  # have a look for the XF86 lib dir at the same time
  found_xf86_libdir=0;
  echo -n >libdirs2.txt
  for libdir in `cat libdirs.txt`;
  do
    if [ -d $libdir ]
    then
      echo $libdir >>libdirs2.txt
    fi
  done
 
  # browse all dirs and cleanup existing libGL.so* symlinks
  for libdir in `cat libdirs2.txt`;
  do 
    for libfile in `ls -1 $libdir/libGL.so* 2>/dev/null`;
    do

      # If the file is libGL.so, save to /usr/share/ati/libGLdir.txt
      if [ libname="libGL.so" ]; then
        echo $libdir>/usr/share/ati/libGLdir.txt
      fi

      libname=`find $libfile -printf %f`
      # act on file, depending on its type
      if [ -h $libdir/$libname ]
      then
        # delete symlinks
        rm -f $libdir/$libname 2>/dev/null
      else
        if [ -f $libdir/$libname ]
        then
          # remove/rename regular files
          # depending on backup file
          if [ -e $libdir/FGL.renamed.$libname ]
          then
            # if already a backup exists, simply delete them
            rm -f $libdir/$libname 2>/dev/null
          else
            # if there is no backup then perform a backup
            mv $libdir/$libname $libdir/FGL.renamed.$libname 2>/dev/null
          fi
        else
          echo "[Warning] Driver : lib file ${libdir}/${libname} is of unknown type and therefore not handled." >> ${LOG_FILE}
        fi
      fi
    done
  done

  # cleanup helper files
  rm -f libdirs.txt libdirs2.txt 2>/dev/null

  # we dont intend to make backups of our own previously installed files
  # therefore check if there is NO backup of libGL.so.1.2 and then create a dummy
  if [ ! -f $XF_LIB/FGL.renamed.libGL.so.1.2 ];
  then
    touch $XF_LIB/FGL.renamed.libGL.so.1.2 2>/dev/null
  fi

# backup inst_path_* files in case user wants to go back to a previous profile

  BackupInstPath inst_path_default
  BackupInstPath inst_path_override
###End: pre_drv ###

if [ -z ${DKMS_VER} ]; then
	# No DKMS detected
###Begin: pre_km ###
	# === kernel modules ===
	# stop kernel module
	/sbin/rmmod ${MODULE} 2> /dev/null

	# remove kernel module directory

	# make sure we're not doing "rm -rf /"; that would be bad
	if [ -z "${OS_MOD}" -a -z "${MODULE}" ]
	then
		echo "Error: OS_MOD and MODULE are both empty in pre.sh; aborting" 1>&2
		echo "rm operation to prevent unwanted data loss" 1>&2

		exit 1
	fi
  
	rm -R -f ${OS_MOD}/${MODULE} 2> /dev/null

	# remove kernel module from all existing kernel configurations
	rm -f ${OS_MOD}/*/kernel/drivers/char/drm/${MODULE}*.*o 2> /dev/null
###End: pre_km ###
# No DKMS preinstallation actions required
fi

###Begin: pre_cp ###
# === control panel application === 
# remove any existing version of the control panel binary
# Prior to 8.35 the control panel was called fireglcontrol*.  This app
# is now obsolete and will no longer be built, but we should clean up any
# old references if they are found.
rm -f ${INSTALLPATH}/usr/X11R6/bin/fireglcontrol* > /dev/null
rm -f ${INSTALLPATH}/usr/X11R6/bin/amdcccle > /dev/null
###End: pre_cp ###

exit 0;

#############################################################################
# post install actions                                                      #
#############################################################################
%post

DRV_RELEASE=%ATI_DRIVER_VERSION

# policy layer initialization
_XVER_USER_SPEC="none"
NO_PRINT="1"
###Begin: check_sh - DO NOT REMOVE; used in b30specfile.sh ###

DetectX()
{
x_binaries="X Xorg XFree86"
x_dirs="/usr/X11R6/bin/ /usr/local/bin/ /usr/X11/bin/ /usr/bin/ /bin/"


for the_x_binary in ${x_binaries}; do
    x_full_dirs=""
    for x_tmp in ${x_dirs}; do
        x_full_dirs=${x_full_dirs}" "${x_tmp}${the_x_binary}
    done
    x_full_dirs=${x_full_dirs}" "`which ${the_x_binary}`
    for x_bin in ${x_full_dirs}; do 
        if [ -x ${x_bin} ];
        then
            # First, try to detect XFree86
            x_ver_num=`${x_bin} -version 2>&1 | grep 'XFree86 Version [0-9]\.' | sed -e 's/^.*XFree86 Version //' | cut -d' ' -f1`
	
        if [ "$x_ver_num" ]
        then
            X_VERSION="XFree86"
	    
            # Correct XFree86 version
            if [ `echo "$x_ver_num" | grep -c '^4\.0\.99'` -gt 0 ]
            then
                x_ver_num="4.1.0"
            fi
	
            if [ `echo "$x_ver_num" | grep -c '^4\.2\.99'` -gt 0 ]
            then
                x_ver_num="4.3.0"
            fi
        fi
	
        if [ -z "${X_VERSION}" ]
        then
            # XFree86 has not been detected, try to detect XOrg up to 7.2
            x_ver_num=`${x_bin} -version 2>&1 | grep 'X Window System Version [0-9]\.' | sed -e 's/^.*X Window System Version //' | cut -d' ' -f1`

            if [ "$x_ver_num" ]
            then
                X_VERSION="Xorg"

                if [ `echo "$x_ver_num" | grep -c '^6\.8\.99'` -gt 0 ]
                then
                    x_ver_num="6.9.0"
                fi

                if [ `echo "$x_ver_num" | grep -c '^7\.1\.1'` -gt 0 ]
                then
                    x_ver_num="7.1.1"
                fi
            fi
        fi
        
        if [ -z "${X_VERSION}" ]
        then
            # XOrg 7.2 or lower has not been detected, try to detect XOrg 7.3
            # We don't want to detect and run on anything higher than XOrg 7.3
            # because starting this version we use autodetection of video driver ABI
            # and we want to know that we need to test the driver if there is a major change
            # in the X server version
            xorg_server_ver_num=`${x_bin} -version 2>&1 | grep 'X\.Org X Server [0-9]\.[0-9]' | sed -e 's/^.*X\.Org X Server //' | cut -d' ' -f1`

            if [ "$xorg_server_ver_num" ]
            then
                if [ `echo "$xorg_server_ver_num" | grep -c '^1\.4'` -gt 0 ]
                then
                    X_VERSION="Xorg"
                    x_ver_num="7.3"
                fi
            fi
        fi
    fi
    if [ "${X_VERSION}" ]
    then
       break
    fi

    done
    if [ "${X_VERSION}" ]
    then
       break
    fi
done
# Produce the final X version string
if [ "${X_VERSION}" ]
then
    X_VERSION="${X_VERSION} ${x_ver_num}"
fi
}

########################################################################
# Begin of the main script


if [ "${NO_PRINT}" != "1" ]; then
    echo "Detected configuration:"
fi

# Detect system architecture
if [ "${NO_DETECT}" != "1" ]; then
    _ARCH=`uname -m`
fi

if [ "${NO_PRINT}" != "1" ]; then
    case ${_ARCH} in
        i?86)	arch_bits="32-bit";;
        x86_64)	arch_bits="64-bit";;
    esac

    echo "Architecture: ${_ARCH} (${arch_bits})"
fi

# Try to detect version of X, if X_VERSION is not set explicitly by the user
if [ -z "${X_VERSION}" ]; then
    # Detect X version
    if [ "${NO_DETECT}" != "1" ]; then
        DetectX
    fi

    if [ -z "${X_VERSION}" ]; then
        if [ "${NO_PRINT}" != "1" ]; then
            echo "X Server: unable to detect"
        fi
    else
        if [ "${NO_PRINT}" != "1" ]; then
            echo "X Server: ${X_VERSION}"
        fi

        if [ "${NO_DETECT}" != "1" ]; then
            # Generate internal name for the version of X
            x_name=`echo ${X_VERSION} | cut -d ' ' -f1`
            x_ver=`echo ${X_VERSION} | cut -d ' ' -f2`
            x_maj=`echo ${x_ver} | cut -d '.' -f1`
            x_min=`echo ${x_ver} | cut -d '.' -f2`
            x_ver_internal="x${x_maj}${x_min}0"
            # Map Xorg 7.3 to x710
            if [ "${x_name}" == "Xorg" -a ${x_maj} -eq 7 -a ${x_min} -eq 3 ]; then
                x_ver_internal=x710
            else
                # Workaround to set internal version number (for platform binary
                # directory) to handle modular X
                if [ ${x_maj} -lt 4 -o ${x_maj} -ge 7 ]; then
                    # X.org 7.0 is non-modular and is handled elsewhere
                    if [ "${x_ver_internal}" != "x700" ]; then
                        x_ver_internal=x710
                    fi
                fi
            fi
            
            X_VERSION=${x_ver_internal}

            if [ "${_ARCH}" = "x86_64" ]; then
                X_VERSION=${X_VERSION}_64a
            fi
        fi
    fi
else
    # If X_VERSION was set by the user, don't try to detect X, just use user's value
    if [ "${NO_PRINT}" != "1" ]; then

        # see --nodetect and --override in check.sh header for explanation
        if [ "${NO_DETECT}" = "1" ]; then
            if [ "${OVERRIDE}" = "1" ]; then
                OVERRIDE_STRING=" (OVERRIDEN BY USER)" 
            else
                OVERRIDE_STRING=""
            fi
        else
            OVERRIDE_STRING=" (OVERRIDEN BY USER)" 
        fi

        if [ -x map_xname.sh ]; then
            echo "X Server${OVERRIDE_STRING}: `./map_xname.sh ${X_VERSION}`"
        else
            echo "X Server${OVERRIDE_STRING}: ${X_VERSION} (lookup failed)"
        fi
    fi
fi

# unset values in case this script is sourced again
unset NO_PRINT
unset NO_DETECT
unset OVERRIDE

###End: check_sh - DO NOT REMOVE; used in b30specfile.sh ###
###Begin: interfaceversion - DO NOT REMOVE; used in b30specfile.sh ###

# Version of the policy interface that this script supports; see WARNING in
#  default_policy.sh header for more details
DEFAULT_POLICY_INTERFACE_VERSION=2

###End: interfaceversion - DO NOT REMOVE; used in b30specfile.sh ###
###Begin: printversion - DO NOT REMOVE; used in b30specfile.sh ###
    _XVER_DETECTED=$X_VERSION

    if [ "${_ARCH}" = "x86_64" -a -d "/usr/lib32" ]
    then
        _LIBDIR32=lib32
    else
        _LIBDIR32=lib
    fi

    _UNAME_R=`uname -r`

    # NOTE: increment DEFAULT_POLICY_INTEFACE_VERSION when interface changes;
    #  see WARNING in header of default_policy.sh for details
    POLICY_VERSION="default:v${DEFAULT_POLICY_INTERFACE_VERSION}:${_ARCH}:${_LIBDIR32}:${_XVER_DETECTED}:${_XVER_USER_SPEC}:${_UNAME_R}"
###End: printversion - DO NOT REMOVE; used in b30specfile.sh ###
version=${POLICY_VERSION}
###Begin: printpolicy - DO NOT REMOVE; used in b30specfile.sh ###

    # NOTE: increment DEFAULT_POLICY_INTEFACE_VERSION when interface changes;
    #  see WARNING in header of default_policy.sh for details

    INPUT_POLICY_NAME=`echo ${version} | cut -d: -f1`
    INPUT_INTERFACE_VERSION=`echo ${version} | cut -d: -f2`
    ARCH=`echo ${version} | cut -d: -f3`
    LIBDIR32=`echo ${version} | cut -d: -f4`
    XVER_DETECTED=`echo ${version} | cut -d: -f5`
    XVER_USER_SPEC=`echo ${version} | cut -d: -f6`
    UNAME_R=`echo ${version} | cut -d: -f7`
    REMAINDER=`echo ${version} | cut -d: -f8`


    ### Step 2: ensure variables from version string are sane and compatible ###

    ERROR_MESSAGE="error: ${version} is not supported"

    # verify policy name matches the one this script was designed for
    if [ "${INPUT_POLICY_NAME}" != "default" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # verify interface version matches the one this script was designed for
    if [ "${INPUT_INTERFACE_VERSION}" != "v${DEFAULT_POLICY_INTERFACE_VERSION}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check ARCH for sanity
    case "${ARCH}" in
    i?86 | x86_64)
        ;;
    *)
        echo ${ERROR_MESSAGE}
        exit 1
        ;;
    esac

    # check LIBDIR32 for sanity
    if [ "${LIBDIR32}" != "lib" -a "${LIBDIR32}" != "lib32" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check XVER_DETECTED for sanity
    echo ${XVER_DETECTED} | grep -q '^x[1-9][0-9]0_64a$'
    RETVAL64=$?
    echo ${XVER_DETECTED} | grep -q '^x[1-9][0-9]0$'
    RETVAL32=$?
    if [ ${RETVAL64} -ne 0 -a ${RETVAL32} -ne 0 ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check XVER_USER_SPEC for sanity
    echo ${XVER_USER_SPEC} | grep -q '^x[1-9][0-9]0_64a$'
    RETVAL64=$?
    echo ${XVER_USER_SPEC} | grep -q '^x[1-9][0-9]0$'
    RETVAL32=$?
    if [ ${RETVAL64} -ne 0 -a ${RETVAL32} -ne 0 -a "${XVER_USER_SPEC}" != "none" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check UNAME_R for sanity
    if [ -z "${UNAME_R}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # verify there are no extra fields
    if [ -n "${REMAINDER}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi


    ### Step 3: determine variable values based on version string ###

    # determine which XVER will be used as the final X_VERSION
    if [ "${XVER_USER_SPEC}" != "none" ]
    then
        XVER=${XVER_USER_SPEC}
    else
        XVER=${XVER_DETECTED}
    fi

    # set paths specific to the X version
    XVER_MAJOR=`echo ${XVER} | cut -c2`
    if [ $XVER_MAJOR -ge 7 ]
    then
        LIB_PREFIX_32=/usr/${LIBDIR32}/xorg
        LIB_PREFIX_64=/usr/lib64/xorg
        DRV_PREFIX_32=/usr/${LIBDIR32}
        DRV_PREFIX_64=/usr/lib64

        ATI_X_BIN=/usr/bin
        ATI_X11_INCLUDE=/usr/include/X11/extensions
    else
        LIB_PREFIX_32=/usr/X11R6/${LIBDIR32}
        LIB_PREFIX_64=/usr/X11R6/lib64
        DRV_PREFIX_32=/usr/X11R6/lib/modules
        DRV_PREFIX_64=/usr/X11R6/lib64/modules

        ATI_X_BIN=/usr/X11R6/bin
        ATI_X11_INCLUDE=/usr/X11R6/include/X11/extensions
    fi

    # set paths specific to the architecture
    if [ "${ARCH}" = "x86_64" ]
    then
        ATI_XLIB=${LIB_PREFIX_64}

        ATI_XLIB_32=${LIB_PREFIX_32}
        ATI_XLIB_64=${LIB_PREFIX_64}
        ATI_3D_DRV_32=${DRV_PREFIX_32}/dri
        ATI_3D_DRV_64=${DRV_PREFIX_64}/dri
    else
        ATI_XLIB=${LIB_PREFIX_32}

        ATI_XLIB_32=${LIB_PREFIX_32}
        ATI_XLIB_64=
        ATI_3D_DRV_32=${DRV_PREFIX_32}/dri
        ATI_3D_DRV_64=
    fi

    # set the variables; we need to do it this way (setting the variables
    #  then printing the variable/value pairs) because the b30specfile.sh needs
    #  the variables set

        ATI_SBIN=/usr/sbin
    ATI_KERN_MOD=/lib/modules/fglrx
      ATI_2D_DRV=${ATI_XLIB}/modules/drivers
    ATI_X_MODULE=${ATI_XLIB}/modules
     ATI_DRM_LIB=${ATI_XLIB}/modules/linux
 ATI_CP_KDE3_LNK=/opt/kde3/share/applnk
  ATI_GL_INCLUDE=/usr/include/GL
  ATI_CP_KDE_LNK=/usr/share/applnk
         ATI_DOC=/usr/share/doc/ati
ATI_CP_GNOME_LNK=/usr/share/gnome/apps
        ATI_ICON=/usr/share/icons
         ATI_MAN=/usr/share/man
         ATI_SRC=/usr/src/ati
      ATI_CP_BIN=${ATI_X_BIN}
     ATI_CP_I18N=/usr/share/ati/amdcccle
   ATI_KERN_INST=/lib/modules/${UNAME_R}/kernel/drivers/char/drm
         ATI_LOG=/usr/share/ati
      ATI_CONFIG=/etc/ati
      ATI_UNINST=/usr/share/ati

###End: printpolicy - DO NOT REMOVE; used in b30specfile.sh ###


##############################################################
# COMMON HEADER: Initialize variables and declare subroutines

BackupInstPath()
{
    if [ ! -d /etc/ati ]
    then
        # /etc/ati is not a directory or doesn't exist so no backup is required
        return 0
    fi

    if [ -n "$1" ]
    then
        FILE_PREFIX=$1
    else
        # client did not pass in FILE_PREFIX parameter and /etc/ati exists
        return 64
    fi

    if [ ! -f /etc/ati/$FILE_PREFIX ]
    then
        return 0
    fi

    COUNTER=0

    ls /etc/ati/$FILE_PREFIX.backup-${COUNTER} > /dev/null 2>&1
    RETURN_CODE=$?
    while [ 0 -eq $RETURN_CODE ]
    do
        COUNTER=$((${COUNTER}+1))
        ls /etc/ati/$FILE_PREFIX.backup-${COUNTER} > /dev/null 2>&1
        RETURN_CODE=$?
    done

    cp -p /etc/ati/$FILE_PREFIX /etc/ati/$FILE_PREFIX.backup-${COUNTER}

    RETURN_CODE=$?

    if [ 0 -ne $RETURN_CODE ]
    then
        # copy failed
        return 65
    fi

    return 0
}

# i.e., lib for 32-bit and lib64 for 64-bit.
if [ `uname -m` = "x86_64" ];
then
  LIB=lib64
else
  LIB=lib
fi

# LIB32 always points to the 32-bit libraries (native in 32-bit,
# 32-on-64 in 64-bit) regardless of the system native bitwidth.
# Use lib32 and lib64; if lib32 doesn't exist assume lib is for lib32
if [ -d "/usr/lib32" ]; then
  LIB32=lib32
else
  LIB32=lib
fi

#process INSTALLPATH, if it's "/" then need to purge it
#SETUP_INSTALLPATH is a Loki Setup environment variable
INSTALLPATH=${SETUP_INSTALLPATH}
if [ "${INSTALLPATH}" = "/" ]
then
    INSTALLPATH=""
fi

# project name and derived defines
MODULE=fglrx
IP_LIB_PREFIX=lib${MODULE}_ip

# general purpose paths
XF_BIN=${INSTALLPATH}${ATI_X_BIN}
XF_LIB=${INSTALLPATH}${ATI_XLIB}
OS_MOD=${INSTALLPATH}`dirname ${ATI_KERN_MOD}`
USR_LIB=${INSTALLPATH}/usr/${LIB}
MODULE=`basename ${ATI_KERN_MOD}`

#FGLRX install log
LOG_PATH=${INSTALLPATH}${ATI_LOG}
LOG_FILE=${LOG_PATH}/fglrx-install.log
if [ ! -e ${LOG_PATH} ]
then
  mkdir -p ${LOG_PATH} 2>/dev/null 
fi
if [ ! -e ${LOG_FILE} ]
then
  touch ${LOG_FILE}
fi

#DKMS version
DKMS_VER=`dkms -V 2> /dev/null | cut -d " " -f2`

#DKMS expects kernel module sources to be placed under this directory
DKMS_KM_SOURCE=/usr/src/${MODULE}-${DRV_RELEASE}

# END OF COMMON HEADER
#######################
###################
# POSTINSTALLATION

###Begin: post_drv1 ###

# cover SuSE special case...
if [ `ls -1 ${INSTALLPATH}/usr/X11R6/bin/switch2* 2>/dev/null | grep "" -c 2>/dev/null` -gt 0 ]
then
  if [ -e ${INSTALLPATH}/usr/X11R6/bin/switch2xf86-4 ]
  then
    ${INSTALLPATH}/usr/X11R6/bin/switch2xf86-4
  fi

  if [ -e ${INSTALLPATH}/usr/X11R6/bin/switch2xf86_glx ]
  then
    echo "[Warning] Driver : swiching OpenGL library support to XFree86 4.x.x DRI method" >> ${LOG_FILE}
   else
    echo "[Warning] Driver : can't switch OpenGL library support to XFree86 4.x.x DRI method" >> ${LOG_FILE}
    echo "[Warning]        : because package xf86_glx-4.*.i386.rpm is not installed." >> ${LOG_FILE}
    echo "[Warning]        : please install and run switch2xf86_glx afterwards." >> ${LOG_FILE}
  fi
fi

  GLDRISEARCHPATH=${INSTALLPATH}${ATI_3D_DRV_32}
  LDLIBSEARCHPATHX=${INSTALLPATH}${ATI_XLIB_32}

if [ -n "${ATI_XLIB_64}" -a -n "${ATI_3D_DRV_64}" ]
then
  GLDRISEARCHPATH=${GLDRISEARCHPATH}:${INSTALLPATH}${ATI_3D_DRV_64}
  LDLIBSEARCHPATHX=${LDLIBSEARCHPATHX}:${INSTALLPATH}${ATI_XLIB_64}
fi

# set environment variable LD_LIBRARY_PATH
# add ATI_PROFILE script located in
#  - /etc/profile.d if dir exists, else
#  - /etc/ati and add a line in /etc/profile for sourcing

ATI_PROFILE_START="### START ATI FGLRX ###"
ATI_PROFILE_END="### END ATI FGLRX ###"
ATI_PROFILE_FNAME="ati-fglrx"

ATI_PROFILE="### START ATI FGLRX ###
### Automatically modified by ATI Proprietary driver scripts
### Please do not modify between START ATI FGLRX and END ATI FGLRX

if [ \$LD_LIBRARY_PATH ]
then
  if ! set | grep LD_LIBRARY_PATH | grep ${LDLIBSEARCHPATHX} > /dev/null
  then
    LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:${LDLIBSEARCHPATHX}
    export LD_LIBRARY_PATH
  fi
else
  LD_LIBRARY_PATH=${LDLIBSEARCHPATHX}
  export LD_LIBRARY_PATH
fi

if [ \$LIBGL_DRIVERS_PATH ]
then
  if ! set | grep LIBGL_DRIVERS_PATH | grep ${GLDRISEARCHPATH} > /dev/null
  then
    LIBGL_DRIVERS_PATH=\$LIBGL_DRIVERS_PATH:${GLDRISEARCHPATH}
    export LIBGL_DRIVERS_PATH
  fi
else
  LIBGL_DRIVERS_PATH=${GLDRISEARCHPATH}
  export LIBGL_DRIVERS_PATH
fi

### END ATI FGLRX ###
"

# replaces any previous script if existing
ATI_PROFILE_FILE1="/etc/profile.d/${ATI_PROFILE_FNAME}.sh"
ATI_PROFILE_FILE2="/etc/ati/${ATI_PROFILE_FNAME}.sh"

if [ -d `dirname ${ATI_PROFILE_FILE1}` ];
then
  printf "${ATI_PROFILE}" > ${ATI_PROFILE_FILE1}
  chmod +x ${ATI_PROFILE_FILE1}

elif [ -d `dirname ${ATI_PROFILE_FILE2}` ];
then
  printf "${ATI_PROFILE}" > ${ATI_PROFILE_FILE2}
  chmod +x ${ATI_PROFILE_FILE2}

  PROFILE_COMMENT=" # Do not modify - set by ATI FGLRX"
  PROFILE_LINE="\. /etc/ati/${ATI_PROFILE_FNAME}\.sh ${PROFILE_COMMENT}"
  if ! grep -e "${PROFILE_LINE}" /etc/profile > /dev/null
  then
     PROFILE_LINE=". ${ATI_PROFILE_FILE2} ${PROFILE_COMMENT}"
     printf "${PROFILE_LINE}\n" >> /etc/profile
  fi
fi

###End: post_drv1 ###

if [ -z ${DKMS_VER} ]; then
	# No DKMS detected
###Begin: post_km ###
	# === kernel module ===
	echo "[Message] Kernel Module : Trying to install a precompiled kernel module." >> ${LOG_FILE}
	cd ${OS_MOD}/${MODULE}
	#make_install.sh information should be contained in readme, not in fglrx-install.log
	sh make_install.sh 1>&2 >/dev/null 
	if [ $? -ne 0 ]; then 
	  echo "[Message] Kernel Module : Precompiled kernel module version mismatched." >> ${LOG_FILE}
	  if test -d ${OS_MOD}/`uname -r`/build; then 
	    # build kernel module
	    echo "[Message] Kernel Module : Found kernel module build environment, generating kernel module now." >> ${LOG_FILE}
	    cd ${OS_MOD}/${MODULE}/build_mod
	    sh make.sh --nohints >> ${LOG_FILE}
	    if [ $? -eq 0 ]; then
	        cd ${OS_MOD}/${MODULE}
	        sh make_install.sh >> ${LOG_FILE}
	        if [ $? -ne 0 ]; then
	            echo "[Error] Kernel Module : Failed to install compiled kernel module - please consult readme." >> ${LOG_FILE}
	        fi
	    else
	       	echo "[Error] Kernel Module : Failed to compile kernel module - please consult readme." >> ${LOG_FILE}
	    fi
	  else
	    echo "[Error] Kernel Module : No kernel module build environment - please consult readme." >> ${LOG_FILE}
	  fi
	fi
	/sbin/depmod
###End: post_km ###
else
	# DKMS detected
	# DKMS compatible kernel module postinstallation actions
	DKMS_STATUS=0

	# Copy kernel module sources from the legacy location to where DKMS expects them

	# make sure we're not doing "rm -rf /"; that would be bad
	if [ "/" = "${DKMS_KM_SOURCE}" ]
	then
		echo "Error: DKMS_KM_SOURCE is / in post.sh; aborting rm operation" 1>&2
		echo "to prevent unwanted data loss" 1>&2

		exit 1
	fi

	rm -R -f ${DKMS_KM_SOURCE} 2> /dev/null	# Clean up old contents first
	cp -R ${OS_MOD}/${MODULE}/build_mod ${DKMS_KM_SOURCE}

	# DKMS installation takes kernel module sources from /usr/src/<module>-<ver>
	# Therefore, we can remove our legacy directory already at this stage

	# make sure we're not doing "rm -rf /"; that would be bad
	if [ -z "${OS_MOD}" -a -z "${MODULE}" ]
	then
		echo "Error: OS_MOD and MODULE are both empty in post.sh; aborting" 1>&2
		echo "rm operation to prevent unwanted data loss" 1>&2

		exit 1
	fi

	rm -R -f ${OS_MOD}/${MODULE} 2> /dev/null

	# Create dkms.conf
	cat - > ${DKMS_KM_SOURCE}/dkms.conf<<__DKMS_CONF_EOF
PACKAGE_NAME="${MODULE}"
PACKAGE_VERSION="${DRV_RELEASE}"

CLEAN="rm -f *.*o"

BUILT_MODULE_NAME[0]="${MODULE}"
MAKE[0]="pushd \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build; sh make.sh --nohints; popd"
DEST_MODULE_LOCATION[0]="/kernel/drivers/char/drm"
__DKMS_CONF_EOF

	# Create Makefile to support build for 2.6
	cat - > ${DKMS_KM_SOURCE}/Makefile<<__MAKEFILE_EOF
# "Fake" makefile required by DKMS to build modules for 2.6 kernels

all:
	@sh make.sh
__MAKEFILE_EOF

	# Add the module to DKMS
	dkms add -m ${MODULE} -v ${DRV_RELEASE} --rpm_safe_upgrade >> ${LOG_FILE}
	
	if [ $? -ne 0 ]; then
    	echo "[Error] Kernel Module : Failed to add ${MODULE}-${DRV_RELEASE} to DKMS" >> ${LOG_FILE}
		DKMS_STATUS=1
	else
		# Build the module
		dkms build -m ${MODULE} -v ${DRV_RELEASE} >> ${LOG_FILE}

		if [ $? -ne 0 ]; then
    		echo "[Error] Kernel Module : Failed to build ${MODULE}-${DRV_RELEASE} with DKMS" >> ${LOG_FILE}
			DKMS_STATUS=2
		else
			# Install the module
			dkms install -m ${MODULE} -v ${DRV_RELEASE} >> ${LOG_FILE}

			if [ $? -ne 0 ]; then
    			echo "[Error] Kernel Module : Failed to install ${MODULE}-${DRV_RELEASE} using DKMS" >> ${LOG_FILE}
				DKMS_STATUS=3
			fi
		fi

		if [ ${DKMS_STATUS} -gt 0 ]; then
   			echo "[Error] Kernel Module : Removing ${MODULE}-${DRV_RELEASE} from DKMS" >> ${LOG_FILE}
			dkms remove -m ${MODULE} -v ${DRV_RELEASE} --rpm_safe_upgrade >> ${LOG_FILE}
		fi
	fi

	if [ ${DKMS_STATUS} -gt 0 ]; then
   		echo "DKMS part of installation failed.  Please refer to ${LOG_FILE} for details"
	fi
fi

###Begin: post_drv2 ###

# manage lib dir contents
XF_BIN=${INSTALLPATH}${ATI_X_BIN}
XF_LIB=${INSTALLPATH}${ATI_XLIB}
XF_LIB32=${INSTALLPATH}${ATI_XLIB_32}

USR_LIB=${INSTALLPATH}/usr/${LIB}
USR_LIB32=${INSTALLPATH}/usr/${LIB32}

# cleanup standard symlinks
rm -f $XF_LIB/libGL.so
rm -f $XF_LIB/libGL.so.1
rm -f $USR_LIB/libGL.so
rm -f $USR_LIB/libGL.so.1
# create standard symlinks

#      *** NOTICE ***      #
# If our libGL.so.1.2 changes version, or the GL libraries 
# change, this code becomes obsolete.
if [ -e $XF_LIB/libGL.fgl.so.1.2 ]; then
  ln -s $XF_LIB/libGL.fgl.so.1.2 $XF_LIB/libGL.so
  ln -s $XF_LIB/libGL.fgl.so.1.2 $XF_LIB/libGL.so.1
  ln -s $XF_LIB/libGL.fgl.so.1.2 $XF_LIB/libGL.so.1.2

  ln -s $XF_LIB/libGL.fgl.so.1.2 $USR_LIB/libGL.so
  ln -s $XF_LIB/libGL.fgl.so.1.2 $USR_LIB/libGL.so.1
  ln -s $XF_LIB/libGL.fgl.so.1.2 $USR_LIB/libGL.so.1.2
else
  ln -s $XF_LIB/libGL.so.1.2 $XF_LIB/libGL.so
  ln -s $XF_LIB/libGL.so.1.2 $XF_LIB/libGL.so.1
  ln -s $XF_LIB/libGL.so.1.2 $USR_LIB/libGL.so
  ln -s $XF_LIB/libGL.so.1.2 $USR_LIB/libGL.so.1
fi

# cleanup/create symlinks for 32-on-64 only if needed
if [ "$LIB" != "$LIB32" ];
then
  rm -f $XF_LIB32/libGL.so
  rm -f $XF_LIB32/libGL.so.1
  rm -f $USR_LIB32/libGL.so
  rm -f $USR_LIB32/libGL.so.1

  #      *** NOTICE ***      #
  # If our libGL.so.1.2 changes version, or the GL libraries
  # change, this code becomes obsolete.
  if [ -e $XF_LIB32/libGL.fgl.so.1.2 ]; then
    ln -s $XF_LIB32/libGL.fgl.so.1.2 $XF_LIB32/libGL.so
    ln -s $XF_LIB32/libGL.fgl.so.1.2 $XF_LIB32/libGL.so.1
    ln -s $XF_LIB32/libGL.fgl.so.1.2 $XF_LIB32/libGL.so.1.2

    ln -s $XF_LIB32/libGL.fgl.so.1.2 $USR_LIB32/libGL.so
    ln -s $XF_LIB32/libGL.fgl.so.1.2 $USR_LIB32/libGL.so.1
    ln -s $XF_LIB32/libGL.fgl.so.1.2 $USR_LIB32/libGL.so.1.2
  else
    ln -s $XF_LIB32/libGL.so.1.2 $XF_LIB32/libGL.so
    ln -s $XF_LIB32/libGL.so.1.2 $XF_LIB32/libGL.so.1
    ln -s $XF_LIB32/libGL.so.1.2 $USR_LIB32/libGL.so
    ln -s $XF_LIB32/libGL.so.1.2 $USR_LIB32/libGL.so.1
  fi
fi

#for those systems that don't look
/sbin/ldconfig -n ${XF_LIB}

#not really needed? (only libGL, which was manually linked above)
if [ "${LIB}" != "${LIB32}" ]; then
  /sbin/ldconfig -n ${XF_LIB32}
fi

# rebuild any remaining library symlinks
/sbin/ldconfig

###End: post_drv2 ###

# SELinux workaround for RHEL5 only
###Begin: selinux - DO NOT REMOVE; used in b30specfile.sh ###

# Change security context when SELinux secutiry policy is enforcing.
# Source Context:AAsystem_u:system_r:unconfined_t:SystemLow-SystemHigh
# Target Context:AAsystem_u:object_r:lib_t
# Target Objects:AA$USR_LIB/xorg/modules/drivers/fglrx_drv.so, $USR_LIB/xorg/libGL.so.1.2, $USR_LIB/dri/fglrx_dri.so
# Affected RPM Packages:AAglibc, gnome-screensaver, xorg-x11-server [application]
# Policy RPM:AAselinux-policy-2.4.6-30.el5
# Selinux Enabled:AATrue
# Policy Type:AAtargeted
# MLS Enabled:AATrue
# Enforcing Mode:AAEnforcing
# Plugin Name:AAplugins.allow_execmod
#
# Allowing access if you trust share library to run correctly, we need to change the file context to textrel_shlib_t.

if [ "${_ARCH}" = "x86_64" ]; then
       SE_USRLIB=/usr/lib64
else
       SE_USRLIB=/usr/lib
fi

# RHEL5 detection
if [ -f /etc/redhat-release ]; then
    read -r redhat_release < /etc/redhat-release
    if [[ `echo $redhat_release | grep "Red Hat"` ]]; then
        RH_VERSION=`echo $redhat_release | sed -e "s/.*release //" -e "s/[^0-9]//g"`
    fi
fi

if [ ${RH_VERSION} = "5" ]; then
    #Change security context if SELINUX is not disabled.
    SE_STAT=`getenforce`
    SELINUX_CMD=`which chcon`
    if [ $? = 0 ] && [ "${SE_STAT}" != "Disabled" ]; then
        ${SELINUX_CMD} -t textrel_shlib_t ${SE_USRLIB}/xorg/modules/drivers/fglrx_drv.so
        ${SELINUX_CMD} -t textrel_shlib_t /usr/lib*/xorg/libGL.so.1.2
        ${SELINUX_CMD} -t textrel_shlib_t /usr/lib*/dri/fglrx_dri.so
        ${SELINUX_CMD} -t textrel_shlib_t ${SE_USRLIB}/xorg/modules/glesx.so
    fi

    #Redhat assumes libGL.so.1.2 of fglrx is at "/usr/lib(64)?/fglrx/libGL\.so(\.[^/]*)*)".
    #Workaround the problem by change file_contexts.local file for Now. May need to contact Redhat.
    CONTEXT_LOCAL="/etc/selinux/targeted/contexts/files/file_contexts.local"
    grep "/usr/lib(64)?/xorg/libGL.so.1.2" ${CONTEXT_LOCAL} >/dev/null 2>&1
    if [ $? -ne 0 ] ; then
        echo "/usr/lib(64)?/xorg/libGL.so.1.2 system_u:object_r:textrel_shlib_t:s0" >> ${CONTEXT_LOCAL}
    fi
    grep "/usr/lib(64)?/xorg/modules/glesx.so" ${CONTEXT_LOCAL} >/dev/null 2>&1
    if [ $? -ne 0 ] ; then
        echo "/usr/lib(64)?/xorg/modules/glesx.so system_u:object_r:textrel_shlib_t:s0" >> ${CONTEXT_LOCAL}
    fi
fi

echo "[Message] Driver : End of installation " >> ${LOG_FILE}
exit 0;

###End: selinux - DO NOT REMOVE; used in b30specfile.sh ###

#############################################################################
# pre uninstall actions                                                     #
#############################################################################
%preun

DRV_RELEASE=%ATI_DRIVER_VERSION

# policy layer initialization
_XVER_USER_SPEC="none"
NO_PRINT="1"
###Begin: check_sh - DO NOT REMOVE; used in b30specfile.sh ###

DetectX()
{
x_binaries="X Xorg XFree86"
x_dirs="/usr/X11R6/bin/ /usr/local/bin/ /usr/X11/bin/ /usr/bin/ /bin/"


for the_x_binary in ${x_binaries}; do
    x_full_dirs=""
    for x_tmp in ${x_dirs}; do
        x_full_dirs=${x_full_dirs}" "${x_tmp}${the_x_binary}
    done
    x_full_dirs=${x_full_dirs}" "`which ${the_x_binary}`
    for x_bin in ${x_full_dirs}; do 
        if [ -x ${x_bin} ];
        then
            # First, try to detect XFree86
            x_ver_num=`${x_bin} -version 2>&1 | grep 'XFree86 Version [0-9]\.' | sed -e 's/^.*XFree86 Version //' | cut -d' ' -f1`
	
        if [ "$x_ver_num" ]
        then
            X_VERSION="XFree86"
	    
            # Correct XFree86 version
            if [ `echo "$x_ver_num" | grep -c '^4\.0\.99'` -gt 0 ]
            then
                x_ver_num="4.1.0"
            fi
	
            if [ `echo "$x_ver_num" | grep -c '^4\.2\.99'` -gt 0 ]
            then
                x_ver_num="4.3.0"
            fi
        fi
	
        if [ -z "${X_VERSION}" ]
        then
            # XFree86 has not been detected, try to detect XOrg up to 7.2
            x_ver_num=`${x_bin} -version 2>&1 | grep 'X Window System Version [0-9]\.' | sed -e 's/^.*X Window System Version //' | cut -d' ' -f1`

            if [ "$x_ver_num" ]
            then
                X_VERSION="Xorg"

                if [ `echo "$x_ver_num" | grep -c '^6\.8\.99'` -gt 0 ]
                then
                    x_ver_num="6.9.0"
                fi

                if [ `echo "$x_ver_num" | grep -c '^7\.1\.1'` -gt 0 ]
                then
                    x_ver_num="7.1.1"
                fi
            fi
        fi
        
        if [ -z "${X_VERSION}" ]
        then
            # XOrg 7.2 or lower has not been detected, try to detect XOrg 7.3
            # We don't want to detect and run on anything higher than XOrg 7.3
            # because starting this version we use autodetection of video driver ABI
            # and we want to know that we need to test the driver if there is a major change
            # in the X server version
            xorg_server_ver_num=`${x_bin} -version 2>&1 | grep 'X\.Org X Server [0-9]\.[0-9]' | sed -e 's/^.*X\.Org X Server //' | cut -d' ' -f1`

            if [ "$xorg_server_ver_num" ]
            then
                if [ `echo "$xorg_server_ver_num" | grep -c '^1\.4'` -gt 0 ]
                then
                    X_VERSION="Xorg"
                    x_ver_num="7.3"
                fi
            fi
        fi
    fi
    if [ "${X_VERSION}" ]
    then
       break
    fi

    done
    if [ "${X_VERSION}" ]
    then
       break
    fi
done
# Produce the final X version string
if [ "${X_VERSION}" ]
then
    X_VERSION="${X_VERSION} ${x_ver_num}"
fi
}

########################################################################
# Begin of the main script


if [ "${NO_PRINT}" != "1" ]; then
    echo "Detected configuration:"
fi

# Detect system architecture
if [ "${NO_DETECT}" != "1" ]; then
    _ARCH=`uname -m`
fi

if [ "${NO_PRINT}" != "1" ]; then
    case ${_ARCH} in
        i?86)	arch_bits="32-bit";;
        x86_64)	arch_bits="64-bit";;
    esac

    echo "Architecture: ${_ARCH} (${arch_bits})"
fi

# Try to detect version of X, if X_VERSION is not set explicitly by the user
if [ -z "${X_VERSION}" ]; then
    # Detect X version
    if [ "${NO_DETECT}" != "1" ]; then
        DetectX
    fi

    if [ -z "${X_VERSION}" ]; then
        if [ "${NO_PRINT}" != "1" ]; then
            echo "X Server: unable to detect"
        fi
    else
        if [ "${NO_PRINT}" != "1" ]; then
            echo "X Server: ${X_VERSION}"
        fi

        if [ "${NO_DETECT}" != "1" ]; then
            # Generate internal name for the version of X
            x_name=`echo ${X_VERSION} | cut -d ' ' -f1`
            x_ver=`echo ${X_VERSION} | cut -d ' ' -f2`
            x_maj=`echo ${x_ver} | cut -d '.' -f1`
            x_min=`echo ${x_ver} | cut -d '.' -f2`
            x_ver_internal="x${x_maj}${x_min}0"
            # Map Xorg 7.3 to x710
            if [ "${x_name}" == "Xorg" -a ${x_maj} -eq 7 -a ${x_min} -eq 3 ]; then
                x_ver_internal=x710
            else
                # Workaround to set internal version number (for platform binary
                # directory) to handle modular X
                if [ ${x_maj} -lt 4 -o ${x_maj} -ge 7 ]; then
                    # X.org 7.0 is non-modular and is handled elsewhere
                    if [ "${x_ver_internal}" != "x700" ]; then
                        x_ver_internal=x710
                    fi
                fi
            fi
            
            X_VERSION=${x_ver_internal}

            if [ "${_ARCH}" = "x86_64" ]; then
                X_VERSION=${X_VERSION}_64a
            fi
        fi
    fi
else
    # If X_VERSION was set by the user, don't try to detect X, just use user's value
    if [ "${NO_PRINT}" != "1" ]; then

        # see --nodetect and --override in check.sh header for explanation
        if [ "${NO_DETECT}" = "1" ]; then
            if [ "${OVERRIDE}" = "1" ]; then
                OVERRIDE_STRING=" (OVERRIDEN BY USER)" 
            else
                OVERRIDE_STRING=""
            fi
        else
            OVERRIDE_STRING=" (OVERRIDEN BY USER)" 
        fi

        if [ -x map_xname.sh ]; then
            echo "X Server${OVERRIDE_STRING}: `./map_xname.sh ${X_VERSION}`"
        else
            echo "X Server${OVERRIDE_STRING}: ${X_VERSION} (lookup failed)"
        fi
    fi
fi

# unset values in case this script is sourced again
unset NO_PRINT
unset NO_DETECT
unset OVERRIDE

###End: check_sh - DO NOT REMOVE; used in b30specfile.sh ###
###Begin: interfaceversion - DO NOT REMOVE; used in b30specfile.sh ###

# Version of the policy interface that this script supports; see WARNING in
#  default_policy.sh header for more details
DEFAULT_POLICY_INTERFACE_VERSION=2

###End: interfaceversion - DO NOT REMOVE; used in b30specfile.sh ###
###Begin: printversion - DO NOT REMOVE; used in b30specfile.sh ###
    _XVER_DETECTED=$X_VERSION

    if [ "${_ARCH}" = "x86_64" -a -d "/usr/lib32" ]
    then
        _LIBDIR32=lib32
    else
        _LIBDIR32=lib
    fi

    _UNAME_R=`uname -r`

    # NOTE: increment DEFAULT_POLICY_INTEFACE_VERSION when interface changes;
    #  see WARNING in header of default_policy.sh for details
    POLICY_VERSION="default:v${DEFAULT_POLICY_INTERFACE_VERSION}:${_ARCH}:${_LIBDIR32}:${_XVER_DETECTED}:${_XVER_USER_SPEC}:${_UNAME_R}"
###End: printversion - DO NOT REMOVE; used in b30specfile.sh ###
version=${POLICY_VERSION}
###Begin: printpolicy - DO NOT REMOVE; used in b30specfile.sh ###

    # NOTE: increment DEFAULT_POLICY_INTEFACE_VERSION when interface changes;
    #  see WARNING in header of default_policy.sh for details

    INPUT_POLICY_NAME=`echo ${version} | cut -d: -f1`
    INPUT_INTERFACE_VERSION=`echo ${version} | cut -d: -f2`
    ARCH=`echo ${version} | cut -d: -f3`
    LIBDIR32=`echo ${version} | cut -d: -f4`
    XVER_DETECTED=`echo ${version} | cut -d: -f5`
    XVER_USER_SPEC=`echo ${version} | cut -d: -f6`
    UNAME_R=`echo ${version} | cut -d: -f7`
    REMAINDER=`echo ${version} | cut -d: -f8`


    ### Step 2: ensure variables from version string are sane and compatible ###

    ERROR_MESSAGE="error: ${version} is not supported"

    # verify policy name matches the one this script was designed for
    if [ "${INPUT_POLICY_NAME}" != "default" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # verify interface version matches the one this script was designed for
    if [ "${INPUT_INTERFACE_VERSION}" != "v${DEFAULT_POLICY_INTERFACE_VERSION}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check ARCH for sanity
    case "${ARCH}" in
    i?86 | x86_64)
        ;;
    *)
        echo ${ERROR_MESSAGE}
        exit 1
        ;;
    esac

    # check LIBDIR32 for sanity
    if [ "${LIBDIR32}" != "lib" -a "${LIBDIR32}" != "lib32" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check XVER_DETECTED for sanity
    echo ${XVER_DETECTED} | grep -q '^x[1-9][0-9]0_64a$'
    RETVAL64=$?
    echo ${XVER_DETECTED} | grep -q '^x[1-9][0-9]0$'
    RETVAL32=$?
    if [ ${RETVAL64} -ne 0 -a ${RETVAL32} -ne 0 ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check XVER_USER_SPEC for sanity
    echo ${XVER_USER_SPEC} | grep -q '^x[1-9][0-9]0_64a$'
    RETVAL64=$?
    echo ${XVER_USER_SPEC} | grep -q '^x[1-9][0-9]0$'
    RETVAL32=$?
    if [ ${RETVAL64} -ne 0 -a ${RETVAL32} -ne 0 -a "${XVER_USER_SPEC}" != "none" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check UNAME_R for sanity
    if [ -z "${UNAME_R}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # verify there are no extra fields
    if [ -n "${REMAINDER}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi


    ### Step 3: determine variable values based on version string ###

    # determine which XVER will be used as the final X_VERSION
    if [ "${XVER_USER_SPEC}" != "none" ]
    then
        XVER=${XVER_USER_SPEC}
    else
        XVER=${XVER_DETECTED}
    fi

    # set paths specific to the X version
    XVER_MAJOR=`echo ${XVER} | cut -c2`
    if [ $XVER_MAJOR -ge 7 ]
    then
        LIB_PREFIX_32=/usr/${LIBDIR32}/xorg
        LIB_PREFIX_64=/usr/lib64/xorg
        DRV_PREFIX_32=/usr/${LIBDIR32}
        DRV_PREFIX_64=/usr/lib64

        ATI_X_BIN=/usr/bin
        ATI_X11_INCLUDE=/usr/include/X11/extensions
    else
        LIB_PREFIX_32=/usr/X11R6/${LIBDIR32}
        LIB_PREFIX_64=/usr/X11R6/lib64
        DRV_PREFIX_32=/usr/X11R6/lib/modules
        DRV_PREFIX_64=/usr/X11R6/lib64/modules

        ATI_X_BIN=/usr/X11R6/bin
        ATI_X11_INCLUDE=/usr/X11R6/include/X11/extensions
    fi

    # set paths specific to the architecture
    if [ "${ARCH}" = "x86_64" ]
    then
        ATI_XLIB=${LIB_PREFIX_64}

        ATI_XLIB_32=${LIB_PREFIX_32}
        ATI_XLIB_64=${LIB_PREFIX_64}
        ATI_3D_DRV_32=${DRV_PREFIX_32}/dri
        ATI_3D_DRV_64=${DRV_PREFIX_64}/dri
    else
        ATI_XLIB=${LIB_PREFIX_32}

        ATI_XLIB_32=${LIB_PREFIX_32}
        ATI_XLIB_64=
        ATI_3D_DRV_32=${DRV_PREFIX_32}/dri
        ATI_3D_DRV_64=
    fi

    # set the variables; we need to do it this way (setting the variables
    #  then printing the variable/value pairs) because the b30specfile.sh needs
    #  the variables set

        ATI_SBIN=/usr/sbin
    ATI_KERN_MOD=/lib/modules/fglrx
      ATI_2D_DRV=${ATI_XLIB}/modules/drivers
    ATI_X_MODULE=${ATI_XLIB}/modules
     ATI_DRM_LIB=${ATI_XLIB}/modules/linux
 ATI_CP_KDE3_LNK=/opt/kde3/share/applnk
  ATI_GL_INCLUDE=/usr/include/GL
  ATI_CP_KDE_LNK=/usr/share/applnk
         ATI_DOC=/usr/share/doc/ati
ATI_CP_GNOME_LNK=/usr/share/gnome/apps
        ATI_ICON=/usr/share/icons
         ATI_MAN=/usr/share/man
         ATI_SRC=/usr/src/ati
      ATI_CP_BIN=${ATI_X_BIN}
     ATI_CP_I18N=/usr/share/ati/amdcccle
   ATI_KERN_INST=/lib/modules/${UNAME_R}/kernel/drivers/char/drm
         ATI_LOG=/usr/share/ati
      ATI_CONFIG=/etc/ati
      ATI_UNINST=/usr/share/ati

###End: printpolicy - DO NOT REMOVE; used in b30specfile.sh ###


##############################################################
# COMMON HEADER: Initialize variables and declare subroutines

BackupInstPath()
{
    if [ ! -d /etc/ati ]
    then
        # /etc/ati is not a directory or doesn't exist so no backup is required
        return 0
    fi

    if [ -n "$1" ]
    then
        FILE_PREFIX=$1
    else
        # client did not pass in FILE_PREFIX parameter and /etc/ati exists
        return 64
    fi

    if [ ! -f /etc/ati/$FILE_PREFIX ]
    then
        return 0
    fi

    COUNTER=0

    ls /etc/ati/$FILE_PREFIX.backup-${COUNTER} > /dev/null 2>&1
    RETURN_CODE=$?
    while [ 0 -eq $RETURN_CODE ]
    do
        COUNTER=$((${COUNTER}+1))
        ls /etc/ati/$FILE_PREFIX.backup-${COUNTER} > /dev/null 2>&1
        RETURN_CODE=$?
    done

    cp -p /etc/ati/$FILE_PREFIX /etc/ati/$FILE_PREFIX.backup-${COUNTER}

    RETURN_CODE=$?

    if [ 0 -ne $RETURN_CODE ]
    then
        # copy failed
        return 65
    fi

    return 0
}

# i.e., lib for 32-bit and lib64 for 64-bit.
if [ `uname -m` = "x86_64" ];
then
  LIB=lib64
else
  LIB=lib
fi

# LIB32 always points to the 32-bit libraries (native in 32-bit,
# 32-on-64 in 64-bit) regardless of the system native bitwidth.
# Use lib32 and lib64; if lib32 doesn't exist assume lib is for lib32
if [ -d "/usr/lib32" ]; then
  LIB32=lib32
else
  LIB32=lib
fi

#process INSTALLPATH, if it's "/" then need to purge it
#SETUP_INSTALLPATH is a Loki Setup environment variable
INSTALLPATH=${SETUP_INSTALLPATH}
if [ "${INSTALLPATH}" = "/" ]
then
    INSTALLPATH=""
fi

# project name and derived defines
MODULE=fglrx
IP_LIB_PREFIX=lib${MODULE}_ip

# general purpose paths
XF_BIN=${INSTALLPATH}${ATI_X_BIN}
XF_LIB=${INSTALLPATH}${ATI_XLIB}
OS_MOD=${INSTALLPATH}`dirname ${ATI_KERN_MOD}`
USR_LIB=${INSTALLPATH}/usr/${LIB}
MODULE=`basename ${ATI_KERN_MOD}`

#FGLRX install log
LOG_PATH=${INSTALLPATH}${ATI_LOG}
LOG_FILE=${LOG_PATH}/fglrx-install.log
if [ ! -e ${LOG_PATH} ]
then
  mkdir -p ${LOG_PATH} 2>/dev/null 
fi
if [ ! -e ${LOG_FILE} ]
then
  touch ${LOG_FILE}
fi

#DKMS version
DKMS_VER=`dkms -V 2> /dev/null | cut -d " " -f2`

#DKMS expects kernel module sources to be placed under this directory
DKMS_KM_SOURCE=/usr/src/${MODULE}-${DRV_RELEASE}

# END OF COMMON HEADER
#######################
####################
# PREUNINSTALLATION

###Begin: preun_drv ###
# backup inst_path_* files in case user wants to go back to a previous profile

  BackupInstPath inst_path_default
  BackupInstPath inst_path_override
###End: preun_drv ###

if [ -z ${DKMS_VER} ]; then
###Begin: preun_km ###
	#stop kernel mode driver
	/sbin/rmmod ${MODULE} 2> /dev/null
###End: preun_km ###
#No preuninstallation steps for the DKMS case
fi

exit 0;

#############################################################################
# post uninstall actions                                                    #
#############################################################################
%postun

DRV_RELEASE=%ATI_DRIVER_VERSION

# policy layer initialization
_XVER_USER_SPEC="none"
NO_PRINT="1"
###Begin: check_sh - DO NOT REMOVE; used in b30specfile.sh ###

DetectX()
{
x_binaries="X Xorg XFree86"
x_dirs="/usr/X11R6/bin/ /usr/local/bin/ /usr/X11/bin/ /usr/bin/ /bin/"


for the_x_binary in ${x_binaries}; do
    x_full_dirs=""
    for x_tmp in ${x_dirs}; do
        x_full_dirs=${x_full_dirs}" "${x_tmp}${the_x_binary}
    done
    x_full_dirs=${x_full_dirs}" "`which ${the_x_binary}`
    for x_bin in ${x_full_dirs}; do 
        if [ -x ${x_bin} ];
        then
            # First, try to detect XFree86
            x_ver_num=`${x_bin} -version 2>&1 | grep 'XFree86 Version [0-9]\.' | sed -e 's/^.*XFree86 Version //' | cut -d' ' -f1`
	
        if [ "$x_ver_num" ]
        then
            X_VERSION="XFree86"
	    
            # Correct XFree86 version
            if [ `echo "$x_ver_num" | grep -c '^4\.0\.99'` -gt 0 ]
            then
                x_ver_num="4.1.0"
            fi
	
            if [ `echo "$x_ver_num" | grep -c '^4\.2\.99'` -gt 0 ]
            then
                x_ver_num="4.3.0"
            fi
        fi
	
        if [ -z "${X_VERSION}" ]
        then
            # XFree86 has not been detected, try to detect XOrg up to 7.2
            x_ver_num=`${x_bin} -version 2>&1 | grep 'X Window System Version [0-9]\.' | sed -e 's/^.*X Window System Version //' | cut -d' ' -f1`

            if [ "$x_ver_num" ]
            then
                X_VERSION="Xorg"

                if [ `echo "$x_ver_num" | grep -c '^6\.8\.99'` -gt 0 ]
                then
                    x_ver_num="6.9.0"
                fi

                if [ `echo "$x_ver_num" | grep -c '^7\.1\.1'` -gt 0 ]
                then
                    x_ver_num="7.1.1"
                fi
            fi
        fi
        
        if [ -z "${X_VERSION}" ]
        then
            # XOrg 7.2 or lower has not been detected, try to detect XOrg 7.3
            # We don't want to detect and run on anything higher than XOrg 7.3
            # because starting this version we use autodetection of video driver ABI
            # and we want to know that we need to test the driver if there is a major change
            # in the X server version
            xorg_server_ver_num=`${x_bin} -version 2>&1 | grep 'X\.Org X Server [0-9]\.[0-9]' | sed -e 's/^.*X\.Org X Server //' | cut -d' ' -f1`

            if [ "$xorg_server_ver_num" ]
            then
                if [ `echo "$xorg_server_ver_num" | grep -c '^1\.4'` -gt 0 ]
                then
                    X_VERSION="Xorg"
                    x_ver_num="7.3"
                fi
            fi
        fi
    fi
    if [ "${X_VERSION}" ]
    then
       break
    fi

    done
    if [ "${X_VERSION}" ]
    then
       break
    fi
done
# Produce the final X version string
if [ "${X_VERSION}" ]
then
    X_VERSION="${X_VERSION} ${x_ver_num}"
fi
}

########################################################################
# Begin of the main script


if [ "${NO_PRINT}" != "1" ]; then
    echo "Detected configuration:"
fi

# Detect system architecture
if [ "${NO_DETECT}" != "1" ]; then
    _ARCH=`uname -m`
fi

if [ "${NO_PRINT}" != "1" ]; then
    case ${_ARCH} in
        i?86)	arch_bits="32-bit";;
        x86_64)	arch_bits="64-bit";;
    esac

    echo "Architecture: ${_ARCH} (${arch_bits})"
fi

# Try to detect version of X, if X_VERSION is not set explicitly by the user
if [ -z "${X_VERSION}" ]; then
    # Detect X version
    if [ "${NO_DETECT}" != "1" ]; then
        DetectX
    fi

    if [ -z "${X_VERSION}" ]; then
        if [ "${NO_PRINT}" != "1" ]; then
            echo "X Server: unable to detect"
        fi
    else
        if [ "${NO_PRINT}" != "1" ]; then
            echo "X Server: ${X_VERSION}"
        fi

        if [ "${NO_DETECT}" != "1" ]; then
            # Generate internal name for the version of X
            x_name=`echo ${X_VERSION} | cut -d ' ' -f1`
            x_ver=`echo ${X_VERSION} | cut -d ' ' -f2`
            x_maj=`echo ${x_ver} | cut -d '.' -f1`
            x_min=`echo ${x_ver} | cut -d '.' -f2`
            x_ver_internal="x${x_maj}${x_min}0"
            # Map Xorg 7.3 to x710
            if [ "${x_name}" == "Xorg" -a ${x_maj} -eq 7 -a ${x_min} -eq 3 ]; then
                x_ver_internal=x710
            else
                # Workaround to set internal version number (for platform binary
                # directory) to handle modular X
                if [ ${x_maj} -lt 4 -o ${x_maj} -ge 7 ]; then
                    # X.org 7.0 is non-modular and is handled elsewhere
                    if [ "${x_ver_internal}" != "x700" ]; then
                        x_ver_internal=x710
                    fi
                fi
            fi
            
            X_VERSION=${x_ver_internal}

            if [ "${_ARCH}" = "x86_64" ]; then
                X_VERSION=${X_VERSION}_64a
            fi
        fi
    fi
else
    # If X_VERSION was set by the user, don't try to detect X, just use user's value
    if [ "${NO_PRINT}" != "1" ]; then

        # see --nodetect and --override in check.sh header for explanation
        if [ "${NO_DETECT}" = "1" ]; then
            if [ "${OVERRIDE}" = "1" ]; then
                OVERRIDE_STRING=" (OVERRIDEN BY USER)" 
            else
                OVERRIDE_STRING=""
            fi
        else
            OVERRIDE_STRING=" (OVERRIDEN BY USER)" 
        fi

        if [ -x map_xname.sh ]; then
            echo "X Server${OVERRIDE_STRING}: `./map_xname.sh ${X_VERSION}`"
        else
            echo "X Server${OVERRIDE_STRING}: ${X_VERSION} (lookup failed)"
        fi
    fi
fi

# unset values in case this script is sourced again
unset NO_PRINT
unset NO_DETECT
unset OVERRIDE

###End: check_sh - DO NOT REMOVE; used in b30specfile.sh ###
###Begin: interfaceversion - DO NOT REMOVE; used in b30specfile.sh ###

# Version of the policy interface that this script supports; see WARNING in
#  default_policy.sh header for more details
DEFAULT_POLICY_INTERFACE_VERSION=2

###End: interfaceversion - DO NOT REMOVE; used in b30specfile.sh ###
###Begin: printversion - DO NOT REMOVE; used in b30specfile.sh ###
    _XVER_DETECTED=$X_VERSION

    if [ "${_ARCH}" = "x86_64" -a -d "/usr/lib32" ]
    then
        _LIBDIR32=lib32
    else
        _LIBDIR32=lib
    fi

    _UNAME_R=`uname -r`

    # NOTE: increment DEFAULT_POLICY_INTEFACE_VERSION when interface changes;
    #  see WARNING in header of default_policy.sh for details
    POLICY_VERSION="default:v${DEFAULT_POLICY_INTERFACE_VERSION}:${_ARCH}:${_LIBDIR32}:${_XVER_DETECTED}:${_XVER_USER_SPEC}:${_UNAME_R}"
###End: printversion - DO NOT REMOVE; used in b30specfile.sh ###
version=${POLICY_VERSION}
###Begin: printpolicy - DO NOT REMOVE; used in b30specfile.sh ###

    # NOTE: increment DEFAULT_POLICY_INTEFACE_VERSION when interface changes;
    #  see WARNING in header of default_policy.sh for details

    INPUT_POLICY_NAME=`echo ${version} | cut -d: -f1`
    INPUT_INTERFACE_VERSION=`echo ${version} | cut -d: -f2`
    ARCH=`echo ${version} | cut -d: -f3`
    LIBDIR32=`echo ${version} | cut -d: -f4`
    XVER_DETECTED=`echo ${version} | cut -d: -f5`
    XVER_USER_SPEC=`echo ${version} | cut -d: -f6`
    UNAME_R=`echo ${version} | cut -d: -f7`
    REMAINDER=`echo ${version} | cut -d: -f8`


    ### Step 2: ensure variables from version string are sane and compatible ###

    ERROR_MESSAGE="error: ${version} is not supported"

    # verify policy name matches the one this script was designed for
    if [ "${INPUT_POLICY_NAME}" != "default" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # verify interface version matches the one this script was designed for
    if [ "${INPUT_INTERFACE_VERSION}" != "v${DEFAULT_POLICY_INTERFACE_VERSION}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check ARCH for sanity
    case "${ARCH}" in
    i?86 | x86_64)
        ;;
    *)
        echo ${ERROR_MESSAGE}
        exit 1
        ;;
    esac

    # check LIBDIR32 for sanity
    if [ "${LIBDIR32}" != "lib" -a "${LIBDIR32}" != "lib32" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check XVER_DETECTED for sanity
    echo ${XVER_DETECTED} | grep -q '^x[1-9][0-9]0_64a$'
    RETVAL64=$?
    echo ${XVER_DETECTED} | grep -q '^x[1-9][0-9]0$'
    RETVAL32=$?
    if [ ${RETVAL64} -ne 0 -a ${RETVAL32} -ne 0 ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check XVER_USER_SPEC for sanity
    echo ${XVER_USER_SPEC} | grep -q '^x[1-9][0-9]0_64a$'
    RETVAL64=$?
    echo ${XVER_USER_SPEC} | grep -q '^x[1-9][0-9]0$'
    RETVAL32=$?
    if [ ${RETVAL64} -ne 0 -a ${RETVAL32} -ne 0 -a "${XVER_USER_SPEC}" != "none" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # check UNAME_R for sanity
    if [ -z "${UNAME_R}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi

    # verify there are no extra fields
    if [ -n "${REMAINDER}" ]
    then
        echo ${ERROR_MESSAGE}
        exit 1
    fi


    ### Step 3: determine variable values based on version string ###

    # determine which XVER will be used as the final X_VERSION
    if [ "${XVER_USER_SPEC}" != "none" ]
    then
        XVER=${XVER_USER_SPEC}
    else
        XVER=${XVER_DETECTED}
    fi

    # set paths specific to the X version
    XVER_MAJOR=`echo ${XVER} | cut -c2`
    if [ $XVER_MAJOR -ge 7 ]
    then
        LIB_PREFIX_32=/usr/${LIBDIR32}/xorg
        LIB_PREFIX_64=/usr/lib64/xorg
        DRV_PREFIX_32=/usr/${LIBDIR32}
        DRV_PREFIX_64=/usr/lib64

        ATI_X_BIN=/usr/bin
        ATI_X11_INCLUDE=/usr/include/X11/extensions
    else
        LIB_PREFIX_32=/usr/X11R6/${LIBDIR32}
        LIB_PREFIX_64=/usr/X11R6/lib64
        DRV_PREFIX_32=/usr/X11R6/lib/modules
        DRV_PREFIX_64=/usr/X11R6/lib64/modules

        ATI_X_BIN=/usr/X11R6/bin
        ATI_X11_INCLUDE=/usr/X11R6/include/X11/extensions
    fi

    # set paths specific to the architecture
    if [ "${ARCH}" = "x86_64" ]
    then
        ATI_XLIB=${LIB_PREFIX_64}

        ATI_XLIB_32=${LIB_PREFIX_32}
        ATI_XLIB_64=${LIB_PREFIX_64}
        ATI_3D_DRV_32=${DRV_PREFIX_32}/dri
        ATI_3D_DRV_64=${DRV_PREFIX_64}/dri
    else
        ATI_XLIB=${LIB_PREFIX_32}

        ATI_XLIB_32=${LIB_PREFIX_32}
        ATI_XLIB_64=
        ATI_3D_DRV_32=${DRV_PREFIX_32}/dri
        ATI_3D_DRV_64=
    fi

    # set the variables; we need to do it this way (setting the variables
    #  then printing the variable/value pairs) because the b30specfile.sh needs
    #  the variables set

        ATI_SBIN=/usr/sbin
    ATI_KERN_MOD=/lib/modules/fglrx
      ATI_2D_DRV=${ATI_XLIB}/modules/drivers
    ATI_X_MODULE=${ATI_XLIB}/modules
     ATI_DRM_LIB=${ATI_XLIB}/modules/linux
 ATI_CP_KDE3_LNK=/opt/kde3/share/applnk
  ATI_GL_INCLUDE=/usr/include/GL
  ATI_CP_KDE_LNK=/usr/share/applnk
         ATI_DOC=/usr/share/doc/ati
ATI_CP_GNOME_LNK=/usr/share/gnome/apps
        ATI_ICON=/usr/share/icons
         ATI_MAN=/usr/share/man
         ATI_SRC=/usr/src/ati
      ATI_CP_BIN=${ATI_X_BIN}
     ATI_CP_I18N=/usr/share/ati/amdcccle
   ATI_KERN_INST=/lib/modules/${UNAME_R}/kernel/drivers/char/drm
         ATI_LOG=/usr/share/ati
      ATI_CONFIG=/etc/ati
      ATI_UNINST=/usr/share/ati

###End: printpolicy - DO NOT REMOVE; used in b30specfile.sh ###


##############################################################
# COMMON HEADER: Initialize variables and declare subroutines

BackupInstPath()
{
    if [ ! -d /etc/ati ]
    then
        # /etc/ati is not a directory or doesn't exist so no backup is required
        return 0
    fi

    if [ -n "$1" ]
    then
        FILE_PREFIX=$1
    else
        # client did not pass in FILE_PREFIX parameter and /etc/ati exists
        return 64
    fi

    if [ ! -f /etc/ati/$FILE_PREFIX ]
    then
        return 0
    fi

    COUNTER=0

    ls /etc/ati/$FILE_PREFIX.backup-${COUNTER} > /dev/null 2>&1
    RETURN_CODE=$?
    while [ 0 -eq $RETURN_CODE ]
    do
        COUNTER=$((${COUNTER}+1))
        ls /etc/ati/$FILE_PREFIX.backup-${COUNTER} > /dev/null 2>&1
        RETURN_CODE=$?
    done

    cp -p /etc/ati/$FILE_PREFIX /etc/ati/$FILE_PREFIX.backup-${COUNTER}

    RETURN_CODE=$?

    if [ 0 -ne $RETURN_CODE ]
    then
        # copy failed
        return 65
    fi

    return 0
}

# i.e., lib for 32-bit and lib64 for 64-bit.
if [ `uname -m` = "x86_64" ];
then
  LIB=lib64
else
  LIB=lib
fi

# LIB32 always points to the 32-bit libraries (native in 32-bit,
# 32-on-64 in 64-bit) regardless of the system native bitwidth.
# Use lib32 and lib64; if lib32 doesn't exist assume lib is for lib32
if [ -d "/usr/lib32" ]; then
  LIB32=lib32
else
  LIB32=lib
fi

#process INSTALLPATH, if it's "/" then need to purge it
#SETUP_INSTALLPATH is a Loki Setup environment variable
INSTALLPATH=${SETUP_INSTALLPATH}
if [ "${INSTALLPATH}" = "/" ]
then
    INSTALLPATH=""
fi

# project name and derived defines
MODULE=fglrx
IP_LIB_PREFIX=lib${MODULE}_ip

# general purpose paths
XF_BIN=${INSTALLPATH}${ATI_X_BIN}
XF_LIB=${INSTALLPATH}${ATI_XLIB}
OS_MOD=${INSTALLPATH}`dirname ${ATI_KERN_MOD}`
USR_LIB=${INSTALLPATH}/usr/${LIB}
MODULE=`basename ${ATI_KERN_MOD}`

#FGLRX install log
LOG_PATH=${INSTALLPATH}${ATI_LOG}
LOG_FILE=${LOG_PATH}/fglrx-install.log
if [ ! -e ${LOG_PATH} ]
then
  mkdir -p ${LOG_PATH} 2>/dev/null 
fi
if [ ! -e ${LOG_FILE} ]
then
  touch ${LOG_FILE}
fi

#DKMS version
DKMS_VER=`dkms -V 2> /dev/null | cut -d " " -f2`

#DKMS expects kernel module sources to be placed under this directory
DKMS_KM_SOURCE=/usr/src/${MODULE}-${DRV_RELEASE}

# END OF COMMON HEADER
#######################
#####################
# POSTUNINSTALLATION

# when this is the last package instance then undo any thing that the installscript did
if [ $1 -eq 0 ];
then
  echo "Detected uninstall of last package instance"
  echo "Restoring system environment..."

###Begin: postun_rn ###

  # === release notes ===
  rm -rf ${INSTALLPATH}${ATI_DOC}/release-notes > /dev/null

###End: postun_rn ###


###Begin: postun_cp ###

  # remove links and icon
  rm -f ${INSTALLPATH}${ATI_CP_KDE_LNK}/amdcccle.kdelnk > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_GNOME_LNK}/amdcccle.desktop > /dev/null
  rm -f ${INSTALLPATH}${ATI_ICON}/ccc_large.xpm > /dev/null
  rm -f ${INSTALLPATH}${ATI_ICON}/ccc_small.xpm > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_KDE3_LNK}/amdcccle_kde3.desktop > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_I18N}/*.qm > /dev/null
  rmdir --ignore-fail-on-non-empty ${INSTALLPATH}${ATI_CP_I18N} 2>/dev/null

  # remove legacy links and icon
  # Prior to 8.35 the control panel was called fireglcontrol*.  This app
  # is now obsolete and will no longer be built, but we should clean up any
  # old references if they are found.
  rm -f ${INSTALLPATH}${ATI_CP_KDE_LNK}/fireglcontrol.kdelnk > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_GNOME_LNK}/fireglcontrol.desktop > /dev/null
  rm -f ${INSTALLPATH}${ATI_ICON}/ati.xpm > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_KDE3_LNK}/fireglcontrol_kde3.desktop > /dev/null
  # remove legacy sources
  # Prior to 8.35 the control panel source code had to be included as it
  # used the open version of Qt.  amdcccle doesn't have this requirement so
  # source files are no longer shipped, but we should clean up any old
  # references if they are found.
  rm -f ${INSTALLPATH}${ATI_SRC}/fglrx_panel_sources.tgz > /dev/null

###End: postun_cp ###

if [ -z ${DKMS_VER} ]; then
###Begin: postun_km ###
  # === kernel module ===
  # remove kernel module directory
  if [ -d ${OS_MOD}/${MODULE} ]; then

		# make sure we're not doing "rm -rf /"; that would be bad
		if [ -z "${OS_MOD}" -a -z "${MODULE}" ]
		then
			echo "Error: OS_MOD and MODULE are both empty in post_un.sh;" 1>&2
			echo "aborting rm operation to prevent unwanted data loss" 1>&2

			exit 1
		fi

    rm -R -f ${OS_MOD}/${MODULE}
  fi
  
  # remove kernel module from all existing kernel configurations
  #rm -f /lib/modules/*/kernel/drivers/char/drm/fglrx*.*o 2> /dev/null
  # remove last kernel module installed
  rm -f ${ATI_KERN_INST}/${MODULE}*.*o
  #refresh modules.dep to remove fglrx*.ko link from modules.dep
  /sbin/depmod
###End: postun_km ###
else
	# DKMS compatible kernel module postuninstallation actions
	dkms uninstall -m ${MODULE} -v ${DRV_RELEASE} > /dev/null
	
	if [ $? -gt 0 ]; then
		echo "Errors during DKMS module uninstallation"
	else	
		dkms remove -m ${MODULE} -v ${DRV_RELEASE} -k `uname -r` --rpm_safe_upgrade > /dev/null
		
		if [ $? -gt 0 ]; then
			echo "Errors during DKMS module removal"
		fi
	fi

	# We shouldn't delete module sources from the source tree, because they may be
	# refered by DKMS for other kernels
	##!! However!  We can check status of the module, and if there are no refs, we can delete the source!
fi

###Begin: postun_drv ###

  # determine which lib dirs are of relevance in current system
  /sbin/ldconfig -v -N -X 2>/dev/null | sed -e 's/ (.*)$//g' | sed -n -e '/^\/.*:$/s/:$//p' >libdirs.txt

  # remove all invalid paths to simplify the following code  
  # have a look for the XF86 lib dir at the same time
  found_xf86_libdir=0;
  echo -n >libdirs2.txt
  for libdir in `cat libdirs.txt`;
  do
    if [ -d $libdir ]
    then
      echo $libdir >>libdirs2.txt
    fi
  done

  # browse all dirs and cleanup existing libGL.so* symlinks
  for libdir in `cat libdirs2.txt`;
  do 
    for libfile in `ls -1 $libdir/libGL.so* 2>/dev/null`;
    do
      libname=`find $libfile -printf %f`
      # act on file, depending on its type
      if [ -h $libdir/$libname ]
      then
        # delete symlinks
        rm -f $libdir/$libname
      else
        if [ -f $libdir/$libname ]
        then
          # remove regular files
          rm -f $libdir/$libname
        else
          echo "WARNING: lib file $libdir/$libname"
          echo "is of unknown type and therefore not handled."
        fi
      fi
    done
  done

  # Step 2: restore any "libGL.so*" from XFree86
  # - zero sized files will finally get deleted
  for libdir in `cat libdirs2.txt`;
  do
    for libfile in `ls -1 $libdir/FGL.renamed.libGL.so* 2>/dev/null`;
    do
      libname=`find $libfile -printf %f`
      origlibfile=`echo $libdir/$libname | sed -n -e 's/FGL\.renamed\.//p'`
      origlibname=`echo $libname | sed -n -e 's/FGL\.renamed\.//p'`
      mv $libdir/$libname $libdir/$origlibname
      if [ ! -s $libdir/$origlibname ]
      then
        rm -f $libdir/$origlibname
      fi
    done
  done

  # Step 3: rebuild any library symlinks
  /sbin/ldconfig

  # Ensures correct install of libGL.so symlink
  libdir=`cat /usr/share/ati/libGLdir.txt`
  ln -s $libdir/libGL.so.1 $libdir/libGL.so
  rm /usr/share/ati/libGLdir.txt

  # cleanup helper files
  rm -f libdirs.txt libdirs2.txt

  # Step X: backup current xconf & restore last .original backup
  OLD_DIR=`pwd`
  cd ${INSTALLPATH}/etc/X11/
  xconf_list="XF86Config
XF86Config-4
xorg.conf"

  for xconf in ${xconf_list}; do
  if [ -f ${xconf} ]; then
    count=0
    #backup last xconf
    #assume the current xconf has fglrx, backup to <xconf>.fglrx-<#>
    while [ -f "${xconf}.fglrx-${count}" ]; do
        count=$(( ${count} + 1 ))
    done
    cp "${xconf}" "${xconf}.fglrx-${count}"

    #now restore the last saved non-fglrx
    count=0
    while [ -f "${xconf}.original-${count}" ]; do
       count=$(( ${count} + 1 ))
    done
    if [ ${count} -ne 0 ]; then
        cp -f "${xconf}.original-$(( ${count} - 1 ))" "${xconf}"
    fi
  fi
  done

  cd ${OLD_DIR}

  # Remove ATI_PROFILE script (from post.sh)
  ATI_PROFILE_FNAME="ati-fglrx"
  PROFILE_COMMENT=" # Do not modify - set by ATI FGLRX"
  PROFILE_LINE="\. /etc/ati/${ATI_PROFILE_FNAME}\.sh ${PROFILE_COMMENT}"
  ATI_PROFILE_FILE1="/etc/profile.d/${ATI_PROFILE_FNAME}.sh"
  ATI_PROFILE_FILE2="/etc/ati/${ATI_PROFILE_FNAME}.sh"

  if [ -w "${ATI_PROFILE_FILE1}" ]; then
    rm -f "${ATI_PROFILE_FILE1}"

  elif [ -w "${ATI_PROFILE_FILE2}" ]; then
    rm -f "${ATI_PROFILE_FILE2}"

    PROFILE_TEMP=`mktemp -t profile_temp.XXXXXX`
    if [ $? -eq 0 ]; then
      # Match tempfile permissions with current profile
      chmod --reference=/etc/profile ${PROFILE_TEMP} 2>/dev/null
      grep -ve "${PROFILE_LINE}" /etc/profile 2>/dev/null > ${PROFILE_TEMP}
      if [ $? -eq 0 ]; then
        mv -f ${PROFILE_TEMP} /etc/profile 2>/dev/null
      fi
    fi

  fi

  # remove docs
  # make sure we're not doing "rm -rf /"; that would be bad
  if [ "${ATI_DOC}" = "/" ]
  then
    echo "Error: ATI_DOC is / in post_un.sh;" 1>&2
    echo "aborting rm operation to prevent unwanted data loss" 1>&2

    exit 1
  fi
  rm -rf ${ATI_DOC} 2>/dev/null

  echo "restore of system environment completed"

###End: postun_drv ###
fi


### RPM-only usage below here ###

# ATI_LOG and license clean up
LIC_PATH=${ATI_LOG}
LIC_FILE=ATI_LICENSE.TXT
LOG_FILE=fglrx-install.log

# remove files, ignore nonexisting file, never prompt
rm -f ${ATI_LOG}/${LOG_FILE} 2>/dev/null
rm -f ${LIC_PATH}/${LIC_FILE} 2>/dev/null

#remove ${LOG_PATH}, ignore non-empty directory to avoid removing any non-driver files the user stores in there
rmdir --ignore-fail-on-non-empty ${ATI_LOG} 2>/dev/null

exit 0;

#############################################################################
# file list                                                                 #
# NOTE: Remove the grep -v "fireglcontrol" pipe step below when we no       #
#       longer build the old fireglcontrol panel.  This filter is a         #
#       temporary measure to prevent it from being inadvertently installed. #
#############################################################################
%files

