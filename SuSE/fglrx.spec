#############################################################################
# spec file header                                                          #
#############################################################################

Name:           %PACKAGE_NAME
Summary:        %ATI_DRIVER_SUMMARY
Version:        %ATI_DRIVER_VERSION
Release:        %ATI_DRIVER_RELEASE
License:        %ATI_DRIVER_VENDOR
URL:            %ATI_DRIVER_URL
Group:          Servers
PreReq:         %insserv_prereq %fillup_prereq
Requires:       gcc make patch kernel-source kernel-syms
%if %suse_version < 1130
Requires:       linux-kernel-headers
%else
Requires:       kernel-devel kernel-default-devel kernel-desktop-devel
%endif
Provides:       fglrx km_fglrx
Obsoletes:      fglrx km_fglrx ati-fglrxG02 x11-video-fglrxG02
Obsoletes:      fglrx_6_9_0_SLE10 fglrx64_6_9_0_SLE10 fglrx_7_4_0_SLE11 fglrx64_7_4_0_SLE11
Obsoletes:      fglrx_7_4_0_SUSE111 fglrx64_7_4_0_SUSE111 fglrx_7_4_0_SUSE112 fglrx64_7_4_0_SUSE112 fglrx_7_5_0_SUSE113 fglrx64_7_5_0_SUSE113 fglrx_7_6_0_SUSE114 fglrx64_7_6_0_SUSE114
ExclusiveArch:  %ix86 x86_64
BuildRoot:      %ATI_DRIVER_BUILD_ROOT

%if %suse_version > 1010
%define MODULES_DIR       /usr/%{_lib}/xorg/modules
%define DRI_DRIVERS_DIR   /usr/%{_lib}/dri
%define DRI_DRIVERS32_DIR /usr/lib/dri
%define X11_INCLUDE_DIR   /usr/include/X11
%else
%define MODULES_DIR       /usr/X11R6/%{_lib}/modules
%define DRI_DRIVERS_DIR   /usr/X11R6/%{_lib}/modules/dri
%define DRI_DRIVERS32_DIR /usr/X11R6/lib/modules/dri
%define X11_INCLUDE_DIR   /usr/X11R6/include/X11
%endif

# local rpm options
%define __check_files   %{nil}

#############################################################################
# spec file description                                                     #
#############################################################################
%description
%ATI_DRIVER_DESCRIPTION

%install
%if %suse_version > 1110
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
cp -a %ATI_DRIVER_BUILD_ROOT/* $RPM_BUILD_ROOT
%endif
tmpdir=$(mktemp -d /tmp/ati_fglrx.XXXXXX)
mkdir $tmpdir/fglrx
mv $RPM_BUILD_ROOT/* $tmpdir/fglrx
#
mkdir -p $RPM_BUILD_ROOT/etc/ati \
         $RPM_BUILD_ROOT/etc/init.d \
         $RPM_BUILD_ROOT/etc/modprobe.d \
         $RPM_BUILD_ROOT/etc/pam.d \
         $RPM_BUILD_ROOT/etc/security/console.apps \
         $RPM_BUILD_ROOT/usr/X11R6/%{_lib} \
%ifarch x86_64
         $RPM_BUILD_ROOT/usr/X11R6/lib \
%endif
         $RPM_BUILD_ROOT/usr/bin \
         $RPM_BUILD_ROOT/usr/include/ATI/GL \
         $RPM_BUILD_ROOT/usr/include/GL \
         $RPM_BUILD_ROOT%{X11_INCLUDE_DIR}/extensions \
         $RPM_BUILD_ROOT%{DRI_DRIVERS_DIR} \
%ifarch x86_64
         $RPM_BUILD_ROOT%{DRI_DRIVERS32_DIR} \
         $RPM_BUILD_ROOT/usr/lib \
%endif
%if %suse_version > 1020
         $RPM_BUILD_ROOT/usr/%{_lib}/pm-utils/power.d \
%else
         $RPM_BUILD_ROOT/usr/%{_lib}/powersave/scripts \
%endif
         $RPM_BUILD_ROOT%{MODULES_DIR}/{linux,drivers} \
         $RPM_BUILD_ROOT%{MODULES_DIR}/updates/extensions \
         $RPM_BUILD_ROOT/usr/sbin \
         $RPM_BUILD_ROOT/usr/share/applications \
         $RPM_BUILD_ROOT/usr/share/ati/{amdcccle,%{_lib}} \
         $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx/{articles,patches,user-manual} \
         $RPM_BUILD_ROOT/usr/share/man/man8 \
         $RPM_BUILD_ROOT/usr/share/pixmaps \
         $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx/2.6.x
#         $RPM_BUILD_ROOT/usr/%{_lib}/fglrx/lib \
pushd $tmpdir/fglrx
    install -m 644 etc/ati/* \
                   $RPM_BUILD_ROOT/etc/ati
    install -m 755 etc/ati/authatieventsd.sh \
                   $RPM_BUILD_ROOT/etc/ati
    install -m 755 etc/init.d/* \
                   $RPM_BUILD_ROOT/etc/init.d
    ln -s /etc/init.d/atieventsd $RPM_BUILD_ROOT/usr/sbin/rcatieventsd
    install -m 644 etc/modprobe.d/* \
                   $RPM_BUILD_ROOT/etc/modprobe.d
    ln -s su $RPM_BUILD_ROOT/etc/pam.d/amdcccle-su
    install -m 755 etc/security/console.apps/amdcccle-su \
                   $RPM_BUILD_ROOT/etc/security/console.apps
    install -m 755 usr/X11R6/%{_lib}/* \
                   $RPM_BUILD_ROOT/usr/X11R6/%{_lib}
    ln -s libGL.so.1.2 $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libGL.so.1
    ln -s libGL.so.1 $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libGL.so
    ln -s libfglrx_dm.so.1.0 $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libfglrx_dm.so.1
    ln -s libfglrx_dm.so.1 $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libfglrx_dm.so
    ln -s libfglrx_gamma.so.1.0 $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libfglrx_gamma.so.1
    ln -s libfglrx_gamma.so.1 $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libfglrx_gamma.so
%ifarch x86_64
    install -m 755 usr/X11R6/lib/* \
                   $RPM_BUILD_ROOT/usr/X11R6/lib
    ln -s libGL.so.1.2 $RPM_BUILD_ROOT/usr/X11R6/lib/libGL.so.1
    ln -s libGL.so.1 $RPM_BUILD_ROOT/usr/X11R6/lib/libGL.so
    ln -s libfglrx_dm.so.1.0 $RPM_BUILD_ROOT/usr/X11R6/lib/libfglrx_dm.so.1
    ln -s libfglrx_dm.so.1 $RPM_BUILD_ROOT/usr/X11R6/lib/libfglrx_dm.so
    ln -s libfglrx_gamma.so.1.0 $RPM_BUILD_ROOT/usr/X11R6/lib/libfglrx_gamma.so.1
    ln -s libfglrx_gamma.so.1 $RPM_BUILD_ROOT/usr/X11R6/lib/libfglrx_gamma.so
%endif
    install -m 755 usr/bin/* \
                   $RPM_BUILD_ROOT/usr/bin
    install -m 644 usr/include/ATI/GL/* \
                   $RPM_BUILD_ROOT/usr/include/ATI/GL
    install -m 644 usr/include/GL/* \
                   $RPM_BUILD_ROOT/usr/include/GL
    install -m 644 usr/include/X11/extensions/* \
                   $RPM_BUILD_ROOT%{X11_INCLUDE_DIR}/extensions
    install -m 755 usr/%{_lib}/dri/* \
                   $RPM_BUILD_ROOT%{DRI_DRIVERS_DIR}
    rm -rf usr/%{_lib}/dri
%if %suse_version > 1020
    install -m 755 usr/%{_lib}/pm-utils/power.d/* \
                   $RPM_BUILD_ROOT/usr/%{_lib}/pm-utils/power.d
    rm -rf usr/%{_lib}/pm-utils
%else
    install -m 755 usr/%{_lib}/powersave/scripts/* \
                   $RPM_BUILD_ROOT/usr/%{_lib}/powersave/scripts
    rm -rf usr/%{_lib}/powersave
%endif
    install -m 755 usr/%{_lib}/xorg/modules/drivers/* \
                   $RPM_BUILD_ROOT%{MODULES_DIR}/drivers
    install -m 755 usr/%{_lib}/xorg/modules/linux/* \
                   $RPM_BUILD_ROOT%{MODULES_DIR}/linux
    install -m 755 usr/%{_lib}/xorg/modules/updates/extensions/* \
                   $RPM_BUILD_ROOT%{MODULES_DIR}/updates/extensions
    rm -rf usr/%{_lib}/xorg/modules/{drivers,linux,updates}
    install -m 755 usr/%{_lib}/xorg/modules/* \
                   $RPM_BUILD_ROOT%{MODULES_DIR}
    rm -rf usr/%{_lib}/xorg
    install -m 755 usr/%{_lib}/* \
                   $RPM_BUILD_ROOT/usr/%{_lib}
    ln -s libAMDXvBA.so.1.0 $RPM_BUILD_ROOT/usr/%{_lib}/libAMDXvBA.so.1
    ln -s libAMDXvBA.so.1 $RPM_BUILD_ROOT/usr/%{_lib}/libAMDXvBA.so
    ln -s libXvBAW.so.1.0 $RPM_BUILD_ROOT/usr/%{_lib}/libXvBAW.so.1
    ln -s libXvBAW.so.1 $RPM_BUILD_ROOT/usr/%{_lib}/libXvBAW.so
    ln -s libatiuki.so.1.0 $RPM_BUILD_ROOT/usr/%{_lib}/libatiuki.so.1
    ln -s libatiuki.so.1 $RPM_BUILD_ROOT/usr/%{_lib}/libatiuki.so
%ifarch x86_64
    install -m 755 usr/lib/dri/* \
                   $RPM_BUILD_ROOT%{DRI_DRIVERS32_DIR}
    rm -rf usr/lib/dri
    install -m 644 usr/lib/* \
                   $RPM_BUILD_ROOT/usr/lib
    ln -s libAMDXvBA.so.1.0 $RPM_BUILD_ROOT/usr/lib/libAMDXvBA.so.1
    ln -s libAMDXvBA.so.1 $RPM_BUILD_ROOT/usr/lib/libAMDXvBA.so
    ln -s libXvBAW.so.1.0 $RPM_BUILD_ROOT/usr/lib/libXvBAW.so.1
    ln -s libXvBAW.so.1 $RPM_BUILD_ROOT/usr/lib/libXvBAW.so
    ln -s libatiuki.so.1.0 $RPM_BUILD_ROOT/usr/lib/libatiuki.so.1
    ln -s libatiuki.so.1 $RPM_BUILD_ROOT/usr/lib/libatiuki.so
%endif
    install -m 755 usr/sbin/* \
                   $RPM_BUILD_ROOT/usr/sbin
    install -m 644 usr/share/applications/* \
                   $RPM_BUILD_ROOT/usr/share/applications
    echo "GenericName=ATI Catalyst Control Center" >> $RPM_BUILD_ROOT/usr/share/applications/amdcccle.desktop
    echo "X-SuSE-translate=false" >> $RPM_BUILD_ROOT/usr/share/applications/amdcccle.desktop
    echo "GenericName=ATI Catalyst Control Center (Administrative)" >> $RPM_BUILD_ROOT/usr/share/applications/amdccclesu.desktop
    echo "X-SuSE-translate=false" >> $RPM_BUILD_ROOT/usr/share/applications/amdccclesu.desktop
    install -m 755 usr/share/ati/amdcccle/* \
                   $RPM_BUILD_ROOT/usr/share/ati/amdcccle
    install -m 755 usr/share/ati/%{_lib}/* \
                   $RPM_BUILD_ROOT/usr/share/ati/%{_lib}
    install -m 644 usr/share/doc/packages/fglrx/articles/* \
                   $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx/articles
    install -m 644 usr/share/doc/packages/fglrx/patches/* \
                   $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx/patches
    install -m 644 usr/share/doc/packages/fglrx/user-manual/* \
                   $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx/user-manual
    rm -rf usr/share/doc/packages/fglrx/{articles,patches,user-manual}
    install -m 644 usr/share/doc/packages/fglrx/* \
                   $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx
    test -f usr/share/man/man8/atieventsd.8 && \
        gzip usr/share/man/man8/atieventsd.8 && \
        test -f usr/share/man/man8/atieventsd.8.gz && \
        install -m 644 usr/share/man/man8/atieventsd.8.gz \
                       $RPM_BUILD_ROOT/usr/share/man/man8
    install -m 644 usr/share/pixmaps/* \
                   $RPM_BUILD_ROOT/usr/share/pixmaps
    install -m 644 usr/src/kernel-modules/fglrx/2.6.x/* \
                   $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx/2.6.x
    rm -rf usr/src/kernel-modules/fglrx/2.6.x
    install -m 644 usr/src/kernel-modules/fglrx/* \
                   $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx
    ln -s 2.6.x/Makefile $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx/Makefile
popd
rm -rf $tmpdir
export NO_BRP_CHECK_RPATH=true

%post
%run_ldconfig
CURRENT_PATH=`pwd`
pushd /usr/src/kernel-modules/fglrx
# add kernel patches here
echo "Apply some patches ..."
%if %suse_version > 1030
    patch -p0 -s < /usr/share/doc/packages/fglrx/patches/ati-CONFIG_SMP.patch
    if [ $? -eq 0 ]; then
        echo "ati-CONFIG_SMP.patch applied successfully."
    else
        echo "ati-CONFIG_SMP.patch could not applied! Please report this bug to Sebastian Siebert <freespacer@gmx.de>. Thank you."
    fi
%endif
%if %suse_version > 1100
    patch -p0 -s < /usr/share/doc/packages/fglrx/patches/ati-2.6.27-build-fix-1.patch
    if [ $? -eq 0 ]; then
        echo "ati-2.6.27-build-fix-1.patch applied successfully."
    else
        echo "ati-2.6.27-build-fix-1.patch could not applied! Please report this bug to Sebastian Siebert <freespacer@gmx.de>. Thank you."
    fi
%endif
%if %suse_version > 1100
    patch -p0 -s < /usr/share/doc/packages/fglrx/patches/ati-2.6.36-compat_alloc_user_space.patch
    if [ $? -eq 0 ]; then
        echo "ati-2.6.36-compat_alloc_user_space.patch applied successfully."
    else
        echo "ati-2.6.36-compat_alloc_user_space.patch could not applied! Please report this bug to Sebastian Siebert <freespacer@gmx.de>. Thank you."
    fi
%endif
# placeholder_for_additional_patches_for_fglrx_sources
rm -f *.orig
popd
if [ -x etc/init.d/atieventsd ]; then
    # Create symbolic run level links for atieventsd start script:
    %{fillup_and_insserv -y atieventsd}
fi
%if %suse_version < 1110
    if [ -r /etc/powersave/events ]; then
        grep -q "EVENT_DAEMON_SCHEME_CHANGE=.*ati-powermode.sh" /etc/powersave/events || \
            sed -e 's/\(EVENT_DAEMON_SCHEME_CHANGE="\)\(.*\)/\1ati-powermode.sh \2/g' -i /etc/powersave/events
    fi
%endif
if [ -x etc/init.d/boot.fglrxrebuild ]; then
    # Create symbolic run level links for boot.fglrxrebuild start script:
    %{fillup_and_insserv -y boot.fglrxrebuild}
fi
if [ -f etc/X11/xorg.conf ]; then
    test -f etc/X11/xorg.conf.fglrx-post || \
        cp etc/X11/xorg.conf etc/X11/xorg.conf.fglrx-post
fi
test -f %{MODULES_DIR}/drivers/fglrx_drv.so && \
    touch %{MODULES_DIR}/drivers/fglrx_drv.so
%if %suse_version > 1010
# ATI libGL still uses the old X11R6 path :-(
mkdir -p usr/X11R6/%{_lib}/modules
test -d usr/X11R6/%{_lib}/modules/dri && \
    mv usr/X11R6/%{_lib}/modules/dri usr/X11R6/%{_lib}/modules/dri.old
ln -snf %{DRI_DRIVERS_DIR} usr/X11R6/%{_lib}/modules/dri
%ifarch x86_64
mkdir -p usr/X11R6/lib/modules
test -d usr/X11R6/lib/modules/dri && \
    mv usr/X11R6/lib/modules/dri usr/X11R6/lib/modules/dri.old
ln -snf %{DRI_DRIVERS32_DIR} usr/X11R6/lib/modules/dri
%endif
%endif
usr/bin/fglrx-kernel-build.sh
if [ $? -ne 0 ]; then
    echo 
    echo "**************************************************************"
    echo "Building/installation of fglrx kernel module failed! Try again"
    echo "by calling \"/usr/bin/fglrx-kernel-build.sh\" manually."
    echo "**************************************************************"
    echo 
fi
echo
echo "*************************************************************"
echo "Please read \"/usr/share/doc/packages/fglrx/README.SuSE\" for"
echo "configuration details when using SaX2."
echo "*************************************************************"
echo
# recreate initrd without KMS, if the use of KMS is enabled in initrd
if grep -q NO_KMS_IN_INITRD=\"no\" /etc/sysconfig/kernel; then
    sed -i 's/NO_KMS_IN_INITRD.*/NO_KMS_IN_INITRD="yes"/g' /etc/sysconfig/kernel
    mkinitrd
fi
exit 0

%preun
if [ -x etc/init.d/atieventsd ]; then
    %stop_on_removal atieventsd
fi
if [ -x etc/init.d/boot.fglrxrebuild ]; then
    %stop_on_removal boot.fglrxrebuild
fi
exit 0

%postun
if [ -x etc/init.d/atieventsd ]; then
    # Rearrange run level symlinks after removing the atieventsd init script
    %{insserv_cleanup}
fi
if [ "$1" -eq 0 ]; then
    test -f etc/X11/xorg.conf && \
        cp etc/X11/xorg.conf etc/X11/xorg.conf.fglrx-postun
    if [ -r etc/X11/xorg.conf.fglrx-post ]; then
        mv etc/X11/xorg.conf.fglrx-post etc/X11/xorg.conf
    fi
    # cleanup
    rm -rf usr/src/kernel-modules/fglrx/
    # try to unload the kernel module, which fails if it is still in use
    rmmod fglrx &> /dev/null
    # now remove it 
    if modinfo fglrx 2> /dev/null | grep -q ^filename:; then 
        modfile=$(modinfo fglrx | grep ^filename: | cut -d : -f 2 | head -n 1)
        rm $modfile
    fi
fi
exit 0

%files
%defattr(-, root, root)
#%dir /usr/include/GL
#%ifarch x86_64
#%dir %{DRI_DRIVERS_DIR}
#%endif
#%dir /etc/security/console.apps/
/etc/ati/*
/etc/init.d/*
/etc/modprobe.d/*
/etc/pam.d/*
/etc/security/console.apps/*
/usr/X11R6/%{_lib}/*
%ifarch x86_64
/usr/X11R6/lib/*
%endif
/usr/bin/*
/usr/include/ATI/GL/*
/usr/include/GL/*
%{X11_INCLUDE_DIR}/extensions/*
/usr/%{_lib}/*
%{DRI_DRIVERS_DIR}/*
%ifarch x86_64
/usr/lib/*
%{DRI_DRIVERS32_DIR}/*
%endif
%if %suse_version > 1020
/usr/%{_lib}/pm-utils/*
%endif
%{MODULES_DIR}/*
%{MODULES_DIR}/drivers/*
%{MODULES_DIR}/linux/*
%{MODULES_DIR}/updates/extensions/*
/usr/sbin/*
/usr/share/applications/*
/usr/share/ati/amdcccle/*
/usr/share/ati/%{_lib}/*
/usr/share/doc/packages/fglrx/*
/usr/share/doc/packages/fglrx/articles/*
/usr/share/doc/packages/fglrx/user-manual/*
/usr/share/man/man8/*
/usr/share/pixmaps/*
/usr/src/kernel-modules/fglrx/*
/usr/src/kernel-modules/fglrx/2.6.x/*
%verify(not mtime) %{MODULES_DIR}/drivers/fglrx_drv.*
# powersave script
%if %suse_version > 1020
/usr/%{_lib}/pm-utils/power.d/*
%else
/usr/%{_lib}/powersave/scripts/*
%endif
