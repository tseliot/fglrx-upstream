%define name ati
%define xorg_version @xorg_version@
%define ati_xorg_version @ati_xorg_version@
%define version @version@
%define mdkrelease @release@
%define release %mkrel %{mdkrelease}

%define priority 1000

%define pack_name @packname@

%if %{mdkversion} >= 1010
%define mdk_distro_version_file	/etc/release
%else
%define mdk_distro_version_file	/etc/mandrake-release
%endif
%define mdk_distro_version	%(perl -ne '/^([.\\w\\s]+) \\(.+\\).+/ and print $1' < %{mdk_distro_version_file})

%if "%{xorg_version}" == "7.1.0"
%define xorg_lib_path %{_libdir}/xorg
%define xorg_modules_path %{xorg_lib_path}/modules
%define xorg_dri_path %{_libdir}/dri
%define xorg_old_dri_path %{_usr}/X11R6/%{_lib}/modules/dri
%define xorg_include_path %{_usr}/include
%define xorg_dri_path32 %{_usr}/lib/dri
%define xorg_old_dri_path32 %{_usr}/X11R6/lib/modules/dri
%define xorg_bin %{_usr}/bin
%else
%define xorg_lib_path %{_usr}/X11R6/%{_lib}
%define xorg_modules_path %{xorg_lib_path}/modules
%define xorg_dri_path %{xorg_modules_path}/dri
%define xorg_include_path %{_usr}/X11R6/include
%define xorg_dri_path32 %{_usr}/X11R6/lib/modules/dri
%define xorg_bin %{_usr}/X11R6/bin
%endif 

%define build_devel 0
%define build_utils 1

%{?_without_devel: %global build_devel 0}
%{?_with_devel: %global build_devel 1}
%{?_without_utils: %global build_utils 0}
%{?_with_utils: %global build_utils 1}

Summary: 	ATI and OpenGL libraries for X.org %{xorg_version} server
Name:		%{name}
Version:	%{version}
Release:	%{release}
Source:		%{name}-driver-installer-%{version}-x86.x86_64.run
License:	ATI Corp. 2007
url:		http://www.ati.com/
Group:		System/Kernel and hardware
BuildRoot:	%{_tmppath}/%{name}-buildroot
Packager:	@vendor@
Vendor:		@vendor@
Prefix:		%{_prefix}
Requires:	drakxtools >= 9.2-8mdk
Requires:	atieventsd = %{version}-%{release}
%if %{mdkversion} >= 200700
Requires(post): /usr/sbin/update-alternatives
Requires(postun): /usr/sbin/update-alternatives
%endif
Obsoletes:	ati_igp
%if %build_devel
BuildRequires:	libqt-devel
%endif
%define _requires_exceptions %{name} >=\\|devel(.*)

%description
ATI X.org %{xorg_version} server module and OpenGL 1.2 libraries for
Radeon based video cards.
You must also install the ATI_kernel module if you want to utilize these
drivers.

%if %build_devel
%package -n %{name}-devel
Summary: 	ATI GLX include and library files
Group: 		System/Kernel and hardware
Requires: 	%{name} = %{version}-%{release}

%description -n %{name}-devel
ATI GLX include and library for your Radeon based video cards.
%endif

%if %build_utils
%package -n %{name}-utils
Summary:	ATI tools
Group:		System/Kernel and hardware
Requires:	%{name} = %{version}-%{release}

%description -n %{name}-utils
Various utils for the ATI proprietary drivers.
%endif

%package -n dkms-%{name}
Summary:	ATI kernel module for ATI Architecture support.
Group:		System/Kernel and hardware
Requires:	dkms
Provides:	ATI_kernel

%description -n dkms-%{name}
ATI Architecture support for Mandriva %{mdk_distro_version}


%package -n atieventsd
Summary:	ATI events daemon
Group:		System/Kernel and hardware

%description -n atieventsd
External ATI events daemon providing hotkey display switching (currently only 
for IBM/Lenovo laptops), DFP hotplug and thermal event power management 
(PowerPlay).

%prep
cd $RPM_BUILD_DIR/%{pack_name}-%{xorg_version}-%{version}

%build

%install
rm -rf $RPM_BUILD_ROOT
cd $RPM_BUILD_DIR/%{pack_name}-%{xorg_version}-%{version}
mkdir -p $RPM_BUILD_ROOT

# atieventsd
install -d $RPM_BUILD_ROOT/etc/ati/
install -d $RPM_BUILD_ROOT/%{_mandir}/man8/
install -d $RPM_BUILD_ROOT/%{_sbindir}
install -d $RPM_BUILD_ROOT/%{_initrddir}
install -m755 etc/ati/authatieventsd.sh $RPM_BUILD_ROOT/etc/ati/authatieventsd.sh
install -m644 usr/share/man/man8/atieventsd.8 $RPM_BUILD_ROOT/%{_mandir}/man8/atieventsd.8
install -m755 usr/sbin/atieventsd $RPM_BUILD_ROOT/%{_sbindir}/atieventsd
install -m755 etc/init.d/atieventsd $RPM_BUILD_ROOT/%{_initrddir}/atieventsd

# install control panel & friends
%if %build_utils
install -d $RPM_BUILD_ROOT%{_sbindir}
install -d $RPM_BUILD_ROOT%{xorg_bin}
install -d $RPM_BUILD_ROOT%{_liconsdir}
install -d $RPM_BUILD_ROOT%{_iconsdir}
install -d $RPM_BUILD_ROOT%{_datadir}/applications

install -m755 etc/ati/signature $RPM_BUILD_ROOT/etc/ati/signature
install -m755 etc/ati/control $RPM_BUILD_ROOT/etc/ati/control
install -m755 usr/sbin/atigetsysteminfo.sh $RPM_BUILD_ROOT%{_sbindir}
install -m755 usr/X11R6/bin/amdcccle $RPM_BUILD_ROOT%{xorg_bin}
install -m755 usr/X11R6/bin/aticonfig $RPM_BUILD_ROOT%{xorg_bin}
install -m755 usr/X11R6/bin/fgl_glxgears $RPM_BUILD_ROOT%{xorg_bin}
install -m755 usr/X11R6/bin/fglrxinfo $RPM_BUILD_ROOT%{xorg_bin}
install -m755 usr/X11R6/bin/fglrx_xgamma $RPM_BUILD_ROOT%{xorg_bin}
install -m644 usr/share/icons/ccc_large.xpm $RPM_BUILD_ROOT%{_liconsdir}/ccc.xpm
install -m644 usr/share/icons/ccc_small.xpm $RPM_BUILD_ROOT%{_iconsdir}/ccc.xpm

cat > $RPM_BUILD_ROOT%{_datadir}/applications/amdcccle.desktop <<EOF
[Desktop Entry]
Name=ATI Catalyst Control Center
Comment=ATI graphics adapter settings
Icon=ccc.xpm
Exec=%{xorg_bin}/amdcccle
Type=Application
Terminal=false
Categories=X-MandrivaLinux-System-Configuration-Hardware;HardwareSettings;Settings;
EOF
%endif

# driver source
mkdir -p $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{version}
cp -r lib/modules/fglrx/build_mod/* $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{version}
mkdir -p $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{version}/patches
cat > $RPM_BUILD_ROOT/usr/src/%{name}-%{version}/dkms.conf <<EOF
PACKAGE_NAME=%{pack_name}
PACKAGE_VERSION=%{version}

DEST_MODULE_LOCATION[0]=/kernel/drivers/char/drm
BUILT_MODULE_NAME[0]=fglrx
%ifarch x86_64
MAKE[0]="CC=${CC:-%__cc} KERNEL_PATH=\${kernel_source_dir} uname_r=\${kernelver} sh ./make.sh"
%else
MAKE[0]="KERNEL_PATH=\${kernel_source_dir} uname_r=\${kernelver} sh ./make.sh"
%endif

PATCH[0]=make.sh.patch
PATCH_MATCH[0]=*

AUTOINSTALL=yes
EOF

cat > $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{version}/patches/make.sh.patch <<EOF
--- ati-8.32.1.orig/make.sh	2006-11-29 12:24:37.000000000 +0100
+++ ati-8.32.1/make.sh	2006-11-29 12:27:25.000000000 +0100
@@ -71,7 +71,7 @@ fi
 
 # ==============================================================
 # system/kernel identification
-uname_r=\`uname -r\`
+[[ -z \$uname_r ]] && uname_r=\`uname -r\`
 uname_v=\`uname -v\`
 uname_s=\`uname -s\`
 uname_m=\`uname -m\`
@@ -940,6 +940,7 @@ if [ \$kernel_is_26x -gt 0 ]; then
     make CC=\${CC} V=\${V} \\
 	LIBIP_PREFIX=\$(echo "\$LIBIP_PREFIX" | sed -e 's|^\([^/]\)|../\1|') \\
 	MODFLAGS="-DMODULE \$def_for_all \$def_smp \$def_modversions" \\
+	KVER=\$uname_r KDIR=\$KERNEL_PATH \\
 	PAGE_ATTR_FIX=\$PAGE_ATTR_FIX > tlog 2>&1 
     res=\$?
     tee -a \$logfile < tlog
EOF

# install fglrx_gamma.h
%if %build_devel
mkdir -p $RPM_BUILD_ROOT/%{xorg_include_path}/X11/extensions/
install -m644 usr/X11R6/include/X11/extensions/fglrx_gamma.h $RPM_BUILD_ROOT/%{xorg_include_path}/X11/extensions/
%endif

# install GLX libs
mkdir -p $RPM_BUILD_ROOT/%{_libdir}/%{name}
mv usr/X11R6/%{_lib}/libGL.so.1.2 $RPM_BUILD_ROOT/%{_libdir}/%{name}/libGL.so.1.2.%{version}
cp -a usr/X11R6/%{_lib}/lib*so* $RPM_BUILD_ROOT/%{_libdir}/%{name}
%ifarch x86_64
mkdir -p $RPM_BUILD_ROOT/%{_prefix}/lib/%{name}
mv usr/X11R6/lib/libGL.so.1.2 $RPM_BUILD_ROOT/%{_prefix}/lib/%{name}/libGL.so.1.2.%{version}
%endif
pushd $RPM_BUILD_ROOT/%{_libdir}/%{name} ; ln -sf libGL.so.1.2.%{version} libGL.so; ln -sf libGL.so.1.2.%{version} libGL.so.1; popd
%if %build_devel
cp -a usr/X11R6/%{_lib}/lib*a $RPM_BUILD_ROOT/%{_libdir}/%{name}
%endif

# install X.org modules
mkdir -p $RPM_BUILD_ROOT/%{xorg_lib_path}
mkdir -p $RPM_BUILD_ROOT/%{xorg_dri_path}
mkdir -p $RPM_BUILD_ROOT/%{xorg_modules_path}/{drivers,linux}
cp -a usr/X11R6/%{_lib}/modules/dri/* $RPM_BUILD_ROOT/%{xorg_dri_path}/
cp -a usr/X11R6/%{_lib}/modules/drivers/* $RPM_BUILD_ROOT/%{xorg_modules_path}/drivers/
cp -a usr/X11R6/%{_lib}/modules/linux/* $RPM_BUILD_ROOT/%{xorg_modules_path}/linux/
install -m644 usr/X11R6/%{_lib}/libfglrx_gamma.*so* $RPM_BUILD_ROOT/%{xorg_lib_path}
install -m644 usr/X11R6/%{_lib}/modules/glesx.so $RPM_BUILD_ROOT/%{xorg_modules_path}
%if %build_devel
install -m644 usr/X11R6/%{_lib}/libfglrx_gamma.*a $RPM_BUILD_ROOT/%{xorg_lib_path}
install -m644 usr/X11R6/%{_lib}/modules/esut.a $RPM_BUILD_ROOT/%{xorg_modules_path}
%endif
%ifarch x86_64
mkdir -p $RPM_BUILD_ROOT/%{xorg_dri_path32}
cp -a usr/X11R6/lib/modules/dri/*.so $RPM_BUILD_ROOT/%{xorg_dri_path32}
%endif

# install docs
mkdir -p $RPM_BUILD_ROOT/%{_docdir}/%{name}-%{version}
cp -a usr/share/doc/fglrx/ATI_LICENSE.TXT $RPM_BUILD_ROOT/%{_docdir}/%{name}-%{version}

# generate ati.conf for ldconfig extra search patch
%if %{mdkversion} < 200700
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d
cat > $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d/%{name}.conf << EOF
%{_libdir}/%{name}
%ifarch x86_64
%{_usr}/lib/%{name}
%endif
EOF
%else
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/GL
cat >$RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf << EOF
%{_libdir}/%{name}
%ifarch x86_64
%{_usr}/lib/%{name}
%endif
EOF
touch $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/GL.conf
%endif

%if "%{xorg_version}" == "7.1.0"
mkdir -p $RPM_BUILD_ROOT%{xorg_old_dri_path}
cd $RPM_BUILD_ROOT%{xorg_old_dri_path}
ln -sf %{xorg_dri_path}/fglrx_dri.so fglrx_dri.so
%ifarch x86_64
mkdir -p $RPM_BUILD_ROOT%{xorg_old_dri_path32}
cd $RPM_BUILD_ROOT%{xorg_old_dri_path32}
ln -sf %{xorg_dri_path32}/fglrx_dri.so fglrx_dri.so
%endif
%endif

%post
%if %{mdkversion} >= 200700
/usr/sbin/update-alternatives --install %{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf %{priority}
if [ ! -L %{_sysconfdir}/ld.so.conf.d/GL.conf ]; then
  /usr/sbin/update-alternatives --auto gl_conf
fi
%endif
/sbin/ldconfig
echo "Relaunch XFdrake to configure your ATI cards"

%postun
%if %{mdkversion} >= 200700
if [ ! -f %{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf ]; then
  /usr/sbin/update-alternatives --remove gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf
fi
%endif
/sbin/ldconfig

%if %build_devel
%post -n %{name}-devel -p /sbin/ldconfig

%postun -n %{name}-devel -p /sbin/ldconfig
%endif

%post -n dkms-%{name}
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %name -v %version
/usr/sbin/dkms --rpm_safe_upgrade build -m %name -v %version
/usr/sbin/dkms --rpm_safe_upgrade install -m %name -v %version

%if %build_utils
%post -n %{name}-utils
%{update_menus}

%postun -n %{name}-utils
%{clean_menus}
%endif

%preun -n dkms-%{name}
# rmmod can failed
rmmod %{pack_name} >/dev/null 2>&1
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %name -v %version --all

%preun -n atieventsd
%_preun_service atieventsd

%post -n atieventsd
%_post_service atieventsd


%clean
rm -rf $RPM_BUILD_DIR/%{name}-X%{xorg_version}-%{version}/
rm -rf $RPM_BUILD_ROOT

%files -n %{name}
%defattr(-,root,root)
%doc %{_docdir}/%{name}-%{version}/*
%{xorg_lib_path}/libfglrx_gamma.*so*
%{xorg_dri_path}/*
%{xorg_modules_path}/glesx.so
%{xorg_modules_path}/drivers/*
%{xorg_modules_path}/linux/*
%{_libdir}/%{name}
%{_libdir}/%{name}/lib*so*
%ifarch x86_64
%{xorg_dri_path32}/*
%{_prefix}/lib/%{name}
%{_prefix}/lib/%{name}/lib*so*
%endif
%if %{mdkversion} < 200700
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}.conf
%else
%ghost %{_sysconfdir}/ld.so.conf.d/GL.conf
%config %{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf
%{xorg_dri_path}
%{xorg_dri_path}/fglrx_dri.so
%ifarch x86_64
%{xorg_dri_path32}
%{xorg_dri_path32}/fglrx_dri.so
%endif
%endif

%if %build_devel
%files -n %{name}-devel
%defattr(-,root,root)
%doc %{_docdir}/%{name}-%{version}/*
%{xorg_lib_path}/libfglrx_gamma.a
%{xorg_modules_path}/esut.a
%{_libdir}/%{name}/lib*a
%{xorg_include_path}/X11/extensions/fglrx_gamma.h
%endif

%files -n dkms-%{name}
%defattr(-,root,root)
%doc %{_docdir}/%{name}-%{version}/*
%{_usr}/src/%{name}-%{version}/*

%files -n atieventsd
%defattr(-,root,root)
%config /etc/ati/authatieventsd.sh
%{_mandir}/man8/atieventsd.8.*
%{_sbindir}/atieventsd
%{_initrddir}/atieventsd

%if %build_utils
%files -n %{name}-utils
%defattr(-,root,root)
/etc/ati
/etc/ati/control
/etc/ati/signature
%{_sbindir}/atigetsysteminfo.sh
%{xorg_bin}/amdcccle
%{xorg_bin}/aticonfig
%{xorg_bin}/fgl_glxgears
%{xorg_bin}/fglrxinfo 
%{xorg_bin}/fglrx_xgamma
%{_liconsdir}/ccc.xpm
%{_iconsdir}/ccc.xpm
%{_datadir}/applications/amdcccle.desktop
%endif


%changelog
* @date@ Ati Packager <@mail@> @version@-@release@
- @version@

# Local Variables:
# rpm-spec-insert-changelog-version-with-shell: t
# End:
