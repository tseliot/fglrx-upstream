#!/bin/sh
#
# POSTINSTALLATION
#

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
