
%define name		fglrx

# %atibuild is used to enable the ATI installer --buildpkg mode.
# The macros version, rel, ati_dir, distsuffix need to be manually defined.
# The macro mdkversion can also be overridden.
%define atibuild	0
%{?_without_ati: %global atibuild 0}
%{?_with_ati: %global atibuild 1}

%if !%{atibuild}
# NOTE: These version definitions are overridden by ati-packager.sh when
# building with the --buildpkg method of the installer.
# version in installer filename:
%define oversion	8-3
# advertized version:
%define mversion	8.3
# version from release notes and ati-packager-helper.sh:
%define version		8.471
%define rel		2
%else
%define oversion	%{version}
%define mversion	%{version}
%endif

%define priority	1000
%define release %mkrel %{rel}

%define driverpkgname	x11-driver-video-fglrx
%define drivername	fglrx
%define xorg_version	710
%define xorg_libdir	%{_libdir}/xorg
%define xorg_dridir	%{_libdir}/dri
%define xorg_dridir32	%{_prefix}/lib/dri
%define xorg_includedir	%{_includedir}
%define ld_so_conf_dir	%{_sysconfdir}/ld.so.conf.d/GL
%define ld_so_conf_file	ati.conf

# The hardcoded ATI dri directories where we create compat symlinks.
# The LIBGL_DRIVERS_(PATH|DIR) env vars could be used some day.
# Debian does a binary replace in libGL.so, but we prefer not to
# touch it.
%define ati_dridir	/usr/X11R6/%{_lib}/modules/dri
%define ati_dridir32	/usr/X11R6/lib/modules/dri

%if %{mdkversion} <= 200710
%define driverpkgname	ati
%define drivername	ati
%endif

%if %{mdkversion} <= 200600
%define xorg_version	690
%define xorg_libdir	%{_prefix}/X11R6/%{_lib}
%define xorg_dridir	%{xorg_libdir}/modules/dri
%define xorg_dridir32	%{_prefix}/X11R6/lib/modules/dri
%define xorg_includedir	%{_prefix}/X11R6/include
%define ld_so_conf_dir	%{_sysconfdir}/ld.so.conf.d
%endif

%ifarch %ix86
%define xverdir		x%{xorg_version}
%define archdir		arch/x86
%endif
%ifarch x86_64
%define xverdir		x%{xorg_version}_64a
%define archdir		arch/x86_64
%endif

# Other packages should not require any ATI specific proprietary libraries
# (if that is really necessary, we may want to split that specific lib out),
# and this package should not be pulled in when libGL.so.1 is required.
%define _provides_exceptions \\.so
%define common_requires_exceptions libfglrx.\\+\\.so

%ifarch x86_64
# (anssi) Allow installing of 64-bit package if the runtime dependencies
# of 32-bit libraries are not satisfied. If a 32-bit package that requires
# libGL.so.1 is installed, the 32-bit mesa libs are pulled in and that will
# pull the dependencies of 32-bit fglrx libraries in as well.
%define _requires_exceptions %common_requires_exceptions\\|lib.*so\\.[^(]\\+\\(([^)]\\+)\\)\\?$
%else
%define _requires_exceptions %common_requires_exceptions
%endif

Summary:	ATI proprietary X.org driver and libraries
Name:		%{name}
Version:	%{version}
Release:	%{release}
%if !%{atibuild}
Source0:	https://a248.e.akamai.net/f/674/9206/0/www2.ati.com/drivers/linux/ati-driver-installer-%{oversion}-x86.x86_64.run
%endif
Source1:	ati-packager.sh
Source2:	atieventsd.init
Patch0:		ati-8.32.5-uname_r.patch
%if !%{atibuild}
Patch1:		ati-8.19.10-fglrx_gamma-extutil-include.patch
Patch2:		ati-8.19.10-fgl_glxgears-includes.patch
%endif
License:	Proprietary
URL:		http://ati.amd.com/support/driver.html
Group:		System/Kernel and hardware
ExclusiveArch:	%{ix86} x86_64
BuildRoot:	%{_tmppath}/%{name}-root
%if !%{atibuild}
%if %{mdkversion} <= 200600
BuildRequires:	MesaGLU-devel
%else
# TODO: Check which ones are not needed as control panel is not built anymore:
BuildRequires:	mesaglu-devel
BuildRequires:	mesagl-devel
BuildRequires:	libxmu-devel
BuildRequires:	libxinerama-devel
BuildRequires:	libxrender-devel
BuildRequires:	libxft-devel
BuildRequires:	libxaw-devel
BuildRequires:	imake
BuildRequires:	x11-util-cf-files
%endif
BuildRequires:	ImageMagick
%endif

%description
Source package of the ATI proprietary driver. Binary packages are
named x11-driver-video-fglrx on Mandriva Linux 2008, and ati on 2007
and earlier.

%package -n %{driverpkgname}
Summary:	ATI proprietary X.org driver and libraries
Group:		System/Kernel and hardware
%if %{mdkversion} >= 200700
Requires(post):	update-alternatives >= 1.9.0
Requires(postun): update-alternatives
%endif
Obsoletes:	ati_igp
%if %{mdkversion} >= 200800
Suggests:	%{drivername}-control-center = %{version}
Obsoletes:	ati < %{version}-%{release}
Provides:	ati = %{version}-%{release}
Conflicts:	x11-server-common < 1.3.0.0-17
Conflicts:	drakx-kbd-mouse-x11 < 0.26
Obsoletes:	x11-driver-video-fglrx-hd2000 < 8.42.3-5
Requires:	kmod(fglrx)
%endif
Provides:	atieventsd = %{version}-%{release}
Obsoletes:	atieventsd < %{version}-%{release}

%description -n %{driverpkgname}
ATI proprietary X.org graphics driver, related libraries and
configuration tools.

NOTE: You should use XFdrake to configure your ATI card. The
correct packages will be automatically installed and configured.

If you do not want to use XFdrake, see README.manual-setup.

The graphical configuration utility, AMD Catalyst Control Center
Linux Edition, is contained in the package
%{drivername}-control-center.

%package -n %{drivername}-control-center
Summary:	AMD Catalyst Control Center Linux Edition
Group:		System/Kernel and hardware
Requires:	%{driverpkgname} = %{version}
Obsoletes:	ati-utils < %{version}-%{release}
Provides:	ati-utils = %{version}-%{release}
Provides:	amdcccle = %{version}-%{release}
Obsoletes:	ati-ccc < %{version}-%{release}
%if %{mdkversion} >= 200800
Obsoletes:	ati-control-center < %{version}-%{release}
Provides:	ati-control-center = %{version}-%{release}
Obsoletes:	fglrx-hd2000-control-center < 8.42.3-5
%endif

%description -n %{drivername}-control-center
AMD Catalyst Control Center Linux Edition, a graphical configuration
utility for the ATI proprietary X.org driver

%package -n dkms-%{drivername}
Summary:	ATI proprietary kernel module
Group:		System/Kernel and hardware
Requires:	dkms
Requires(post):	dkms
Requires(preun): dkms
%if %{mdkversion} >= 200800
Obsoletes:	dkms-fglrx-hd2000 < 8.42.3-5
Obsoletes:	dkms-ati < %{version}-%{release}
Provides:	dkms-ati = %{version}-%{release}
%endif
Requires:	%{driverpkgname} = %{version}

%description -n dkms-%{drivername}
ATI proprietary kernel module. This is to be used with the
%{driverpkgname} package.

%package -n %{drivername}-devel
Summary:	ATI proprietary development libraries and headers
Group:		Development/C
Requires:	%{driverpkgname} = %{version}-%{release}
%if %{mdkversion} >= 200800
Obsoletes:	fglrx-hd2000-devel < 8.42.3-5
Obsoletes:	ati-devel < %{version}-%{release}
Provides:	ati-devel = %{version}-%{release}
%endif

%description -n %{drivername}-devel
ATI proprietary development libraries and headers. This package is
not required for normal use.

The main driver package name is %{driverpkgname}.

%prep
%setup -T -c
%if %{atibuild}
ln -s %{ati_dir}/%{xverdir} %{ati_dir}/arch .
# patch0 affects common, so we cannot symlink it:
cp -a %{ati_dir}/common .
%else
sh %{SOURCE0} --extract .

mkdir fglrx_tools
tar -xzf common/usr/src/ati/fglrx_sample_source.tgz -C fglrx_tools
cd fglrx_tools # ensure patch does not touch outside
%patch1 -p1
%patch2 -p1
cd -
cmp common/usr/X11R6/include/X11/extensions/fglrx_gamma.h fglrx_tools/lib/fglrx_gamma/fglrx_gamma.h
%endif

cd common # ensure patch does not touch outside
%patch0 -p2
cd -

cat > README.install.urpmi <<EOF
This driver is for ATI Radeon 9500 and newer cards.
Reconfiguring is not necessary when upgrading from a previous Mandriva ATI
driver package.

Use XFdrake to configure X to use the correct ATI driver. Any needed
packages will be automatically installed if not already present.
1. Run XFdrake as root.
2. Go to the Graphics Card list.
3. Select your card (it is usually already autoselected).
4. Answer any questions asked and then quit.

If you do not want to use XFdrake or it does not work correctly for
you, see README.manual-setup for manual installation instructions.
EOF

cat > README.manual-setup <<EOF
This file describes the procedure for the manual installation of this ATI
driver package. You can find the instructions for the recommended automatic
installation in the file 'README.install.urpmi' in this directory.

- Open %{_sysconfdir}/X11/xorg.conf and make the following changes:
  o Change the Driver to "fglrx" in the Device section
  o Make the line below the only 'glx' related line in the Module section:
      Load "glx"
%if %{mdkversion} >= 200710
  o Remove any 'ModulePath' lines from the Files section
%endif
%if %{mdkversion} >= 200700
- Run "update-alternatives --set gl_conf %{ld_so_conf_dir}/%{ld_so_conf_file}" as root.
- Run "ldconfig" as root.
%endif
EOF

%build
%if !%{atibuild}
# %atibuild is done with minimal buildrequires
cd fglrx_tools/lib/fglrx_gamma
xmkmf
# parallel make broken (2007-09-18)
make CC="%__cc %optflags"
cd -
cd fglrx_tools/fgl_glxgears
xmkmf
%make RMAN=/bin/true CC="%__cc %optflags"
cd -
cd fglrx_tools/programs/fglrx_gamma
xmkmf
%make INSTALLED_LIBS=-L../../lib/fglrx_gamma INCLUDES=-I../../../common/usr/X11R6/include CC="%__cc %optflags" RMAN=/bin/true
cd -
%endif

%install
rm -rf %{buildroot}

# dkms
install -d -m755 %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}
cp -a common/lib/modules/fglrx/build_mod/* %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}
cp -a %{archdir}/lib/modules/fglrx/build_mod/* %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}

#install -d -m755 %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}/patches
#install -m644 %{SOURCE3} %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}/patches

cat > %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}/dkms.conf <<EOF
PACKAGE_NAME="%{drivername}"
PACKAGE_VERSION="%{version}-%{release}"
BUILT_MODULE_NAME[0]="fglrx"
DEST_MODULE_LOCATION[0]="/kernel/drivers/char/drm"
MAKE[0]="KERNEL_PATH=\${kernel_source_dir} uname_r=\${kernelver} sh make.sh"
AUTOINSTALL="yes"
EOF

# headers
install -d -m755		%{buildroot}%{_includedir}
cp -a common/usr/include/*	%{buildroot}%{_includedir}

install -d -m755 %{buildroot}%{xorg_includedir}/X11/extensions
install -m644 common/usr/X11R6/include/X11/extensions/*.h  %{buildroot}%{xorg_includedir}/X11/extensions

# install binaries
install -d -m755					%{buildroot}%{_sbindir}
install -m755 %{archdir}/usr/sbin/atieventsd		%{buildroot}%{_sbindir}
install -m755 %{archdir}/usr/sbin/amdnotifyui		%{buildroot}%{_sbindir}
install -m755 common/usr/sbin/*				%{buildroot}%{_sbindir}
install -d -m755					%{buildroot}%{_bindir}
install -m755 %{archdir}/usr/X11R6/bin/aticonfig	%{buildroot}%{_bindir}
install -m755 %{archdir}/usr/X11R6/bin/fglrxinfo	%{buildroot}%{_bindir}
install -m755 %{archdir}/usr/X11R6/bin/amdcccle		%{buildroot}%{_bindir}
%if !%{atibuild}
# install self-built binaries
install -m755 fglrx_tools/fgl_glxgears/fgl_glxgears	%{buildroot}%{_bindir}
install -m755 fglrx_tools/programs/fglrx_gamma/fglrx_xgamma %{buildroot}%{_bindir}
%else
install -m755 %{archdir}/usr/X11R6/bin/fgl_glxgears	%{buildroot}%{_bindir}
install -m755 %{archdir}/usr/X11R6/bin/fglrx_xgamma %{buildroot}%{_bindir}
%endif

# atieventsd initscript
install -d -m755 %{buildroot}%{_initrddir}
install -m755 %{SOURCE2} %{buildroot}%{_initrddir}/atieventsd

# amdcccle data files
install -d -m755 %{buildroot}%{_datadir}/ati/amdcccle
install -m644 common/usr/share/ati/amdcccle/*.qm %{buildroot}%{_datadir}/ati/amdcccle

# man pages
install -d -m755 %{buildroot}%{_mandir}/man1 %{buildroot}%{_mandir}/man8
%if !%{atibuild}
install -m644 fglrx_tools/programs/fglrx_gamma/fglrx_xgamma.man %{buildroot}%{_mandir}/man1/fglrx_xgamma.1
%endif
install -m644 common/usr/share/man/man8/* %{buildroot}%{_mandir}/man8

# menu entry
%if %{mdkversion} <= 200600
install -d -m755 %{buildroot}%{_menudir}
cat <<EOF >%{buildroot}%{_menudir}/%{drivername}-control-center
?package(%{drivername}-control-center):command="%{_bindir}/amdcccle" \
                  icon=%{drivername}-amdcccle.png \
                  needs="x11" \
                  section="System/Configuration/Hardware" \
                  title="ATI Catalyst Control Center" \
                  longtitle="ATI graphics adapter settings" \
                  xdg="true"
EOF
%endif

install -d -m755 %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-fglrx-amdcccle.desktop << EOF
[Desktop Entry]
Name=ATI Catalyst Control Center
Comment=ATI graphics adapter settings
Exec=%{_bindir}/amdcccle
Icon=%{drivername}-amdcccle
Terminal=false
Type=Application
Categories=Settings;HardwareSettings;X-MandrivaLinux-System-Configuration;
EOF

# icons
install -d -m755 %{buildroot}%{_miconsdir} %{buildroot}%{_iconsdir} %{buildroot}%{_liconsdir}
%if !%{atibuild}
convert common/usr/share/icons/ccc_large.xpm -resize 16x16 %{buildroot}%{_miconsdir}/%{drivername}-amdcccle.png
convert common/usr/share/icons/ccc_large.xpm -resize 32x32 %{buildroot}%{_iconsdir}/%{drivername}-amdcccle.png
convert common/usr/share/icons/ccc_large.xpm -resize 48x48 %{buildroot}%{_liconsdir}/%{drivername}-amdcccle.png
%else
install -m644 common/usr/share/icons/ccc_large.xpm %{buildroot}%{_liconsdir}/%{drivername}-amdcccle.xpm
install -m644 common/usr/share/icons/ccc_small.xpm %{buildroot}%{_iconsdir}/%{drivername}-amdcccle.xpm
%endif

# install libraries
install -d -m755					%{buildroot}%{_libdir}/%{drivername}
install -m755 %{archdir}/usr/X11R6/%{_lib}/libGL.so.1.2	%{buildroot}%{_libdir}/%{drivername}
/sbin/ldconfig -n					%{buildroot}%{_libdir}/%{drivername}
ln -s libGL.so.1					%{buildroot}%{_libdir}/%{drivername}/libGL.so
%ifarch x86_64
install -d -m755					%{buildroot}%{_prefix}/lib/%{drivername}
install -m755 arch/x86/usr/X11R6/lib/libGL.so.1.2	%{buildroot}%{_prefix}/lib/%{drivername}
/sbin/ldconfig -n					%{buildroot}%{_prefix}/lib/%{drivername}
ln -s libGL.so.1					%{buildroot}%{_prefix}/lib/%{drivername}/libGL.so
%endif
%if !%{atibuild}
install -m755 fglrx_tools/lib/fglrx_gamma/libfglrx_gamma.so.1.0 %{buildroot}%{_libdir}/%{drivername}
%else
install -m755 %{archdir}/usr/X11R6/%{_lib}/libfglrx_gamma.so.1.0 %{buildroot}%{_libdir}/%{drivername}
%endif
install -m755 %{archdir}/usr/X11R6/%{_lib}/libfglrx_pp.so.1.0 %{buildroot}%{_libdir}/%{drivername}
install -m755 %{archdir}/usr/X11R6/%{_lib}/libfglrx_dm.so.1.0 %{buildroot}%{_libdir}/%{drivername}
install -m755 %{archdir}/usr/X11R6/%{_lib}/libfglrx_tvout.so.1.0 %{buildroot}%{_libdir}/%{drivername}
install -m755 %{archdir}/usr/X11R6/%{_lib}/libatiadlxx.so %{buildroot}%{_libdir}/%{drivername}
/sbin/ldconfig -n					%{buildroot}%{_libdir}/%{drivername}
ln -s libfglrx_gamma.so.1.0				%{buildroot}%{_libdir}/%{drivername}/libfglrx_gamma.so
ln -s libfglrx_pp.so.1.0				%{buildroot}%{_libdir}/%{drivername}/libfglrx_pp.so
ln -s libfglrx_dm.so.1.0				%{buildroot}%{_libdir}/%{drivername}/libfglrx_dm.so
ln -s libfglrx_tvout.so.1.0				%{buildroot}%{_libdir}/%{drivername}/libfglrx_tvout.so
%if !%{atibuild}
install -m644 fglrx_tools/lib/fglrx_gamma/libfglrx_gamma.a %{buildroot}%{_libdir}/%{drivername}
%else
install -m755 %{archdir}/usr/X11R6/%{_lib}/libfglrx_gamma.a %{buildroot}%{_libdir}/%{drivername}
%endif
install -m644 %{archdir}/usr/X11R6/%{_lib}/libfglrx_pp.a %{buildroot}%{_libdir}/%{drivername}
install -m644 %{archdir}/usr/X11R6/%{_lib}/libfglrx_dm.a %{buildroot}%{_libdir}/%{drivername}
install -m644 %{archdir}/usr/X11R6/%{_lib}/libfglrx_tvout.a %{buildroot}%{_libdir}/%{drivername}

# install X.org files
install -d -m755					%{buildroot}%{xorg_libdir}/modules/drivers
install -m755 %{xverdir}/usr/X11R6/%{_lib}/modules/drivers/*.so* %{buildroot}%{xorg_libdir}/modules/drivers
install -d -m755					%{buildroot}%{xorg_libdir}/modules/linux
install -m755 %{xverdir}/usr/X11R6/%{_lib}/modules/linux/*.so* %{buildroot}%{xorg_libdir}/modules/linux
install -m644 %{xverdir}/usr/X11R6/%{_lib}/modules/*.a	%{buildroot}%{xorg_libdir}/modules
install -m644 %{xverdir}/usr/X11R6/%{_lib}/modules/*.*o	%{buildroot}%{xorg_libdir}/modules

# etc files
install -d -m755		%{buildroot}%{_sysconfdir}/ati
install -m644 common/etc/ati/*	%{buildroot}%{_sysconfdir}/ati
chmod 0755			%{buildroot}%{_sysconfdir}/ati/*.sh

# dri libraries
install -d -m755						%{buildroot}%{xorg_dridir}
install -m755 %{archdir}/usr/X11R6/%{_lib}/modules/dri/*	%{buildroot}%{xorg_dridir}
%ifarch x86_64
install -d -m755						%{buildroot}%{xorg_dridir32}
install -m755 arch/x86/usr/X11R6/lib/modules/dri/*		%{buildroot}%{xorg_dridir32}
%endif
%if %{mdkversion} >= 200700
install -d -m755			%{buildroot}%{ati_dridir}
ln -s %{xorg_dridir}/fglrx_dri.so	%{buildroot}%{ati_dridir}
%ifarch x86_64
install -d -m755			%{buildroot}%{ati_dridir32}
ln -s %{xorg_dridir32}/fglrx_dri.so	%{buildroot}%{ati_dridir32}
%endif
%endif

# ld.so.conf
install -d -m755			%{buildroot}%{ld_so_conf_dir}
echo "%{_libdir}/%{drivername}" >	%{buildroot}%{ld_so_conf_dir}/%{ld_so_conf_file}
%ifarch x86_64
echo "%{_prefix}/lib/%{drivername}" >>	%{buildroot}%{ld_so_conf_dir}/%{ld_so_conf_file}
%endif
%if %{mdkversion} >= 200700
touch					%{buildroot}%{_sysconfdir}/ld.so.conf.d/GL.conf
%endif

%if %{mdkversion} >= 200800
%pre -n %{driverpkgname}
# Handle alternatives-era /etc/ati directory
# It may confuse rpm due to it containing %config files
if [ -L %{_sysconfdir}/ati ]; then
	rm %{_sysconfdir}/ati
fi
%endif

%post -n %{driverpkgname}
%if %{mdkversion} >= 200800
# Migrate from pre-alternatives files
if [ ! -L %{_datadir}/applications/mandriva-amdcccle.desktop -a -e %{_datadir}/applications/mandriva-amdcccle.desktop ]; then
	rm -f %{_datadir}/applications/mandriva-amdcccle.desktop
fi
%endif

%if %{mdkversion} >= 200700
%{_sbindir}/update-alternatives \
	--install %{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{ld_so_conf_dir}/%{ld_so_conf_file} %{priority} \
%if %{mdkversion} >= 200800
	--slave %{_libdir}/xorg/modules/extensions/libglx.so libglx %{_libdir}/xorg/modules/extensions/standard/libglx.so
if [ "$(readlink -e %{_sysconfdir}/ld.so.conf.d/GL.conf)" = "%{_sysconfdir}/ld.so.conf.d/GL/ati-hd2000.conf" ]; then
	# Switch from the obsolete hd2000 branch:
	%{_sbindir}/update-alternatives --set gl_conf %{ld_so_conf_dir}/%{ld_so_conf_file}
fi
# When upgrading from alternatives setup, rpm may consider /etc/ati/atiogl.xml
# to exist due to the symlink, even when we remove it in %pre:
if [ -e %{_sysconfdir}/ati/atiogl.xml.rpmnew -a ! -e %{_sysconfdir}/ati/atiogl.xml ]; then
	mv %{_sysconfdir}/ati/atiogl.xml.rpmnew %{_sysconfdir}/ati/atiogl.xml
	echo "Moved %{_sysconfdir}/ati/atiogl.xml.rpmnew back to %{_sysconfdir}/ati/atiogl.xml."
fi
%endif
# empty line so that /sbin/ldconfig is not passed to update-alternatives
%endif
/sbin/ldconfig
%_post_service atieventsd

%if %{mdkversion} >= 200800
%posttrans -n %{driverpkgname}
# RPM seems to leave out the active /etc/fglrx* directory, likely due to
# it being confused with the /etc/ati symlink. We have to clean up ourself:
for dir in %{_sysconfdir}/fglrx %{_sysconfdir}/fglrx-hd2000; do
	if [ -d $dir ]; then
		for file in $dir/*; do
			case "$(basename $file)" in
			control | signature | logo_mask.xbm.example | logo.xbm.example)
				# non-config files, rpm would normally remove
				rm $file;;
			authatieventsd.sh | fglrxprofiles.csv | fglrxrc | atiogl.xml)
				# config files, check for modifications
				case "$(stat -c%s $file)" in
				545 | 838 | 2769 | 10224 | 11018)
					rm $file;;
				*)
					echo "Saving $file as %{_sysconfdir}/ati/$(basename $file).rpmsave."
					mv $file %{_sysconfdir}/ati/$(basename $file).rpmsave;;
				esac
				;;
			esac
		done
		[ $(ls -c $dir | wc -l) -eq 0 ] && rm -r $dir
	fi
done
true
%endif

%preun -n %{driverpkgname}
%_preun_service atieventsd

%postun -n %{driverpkgname}
%if %{mdkversion} >= 200700
if [ ! -f %{ld_so_conf_dir}/%{ld_so_conf_file} ]; then
  %{_sbindir}/update-alternatives --remove gl_conf %{ld_so_conf_dir}/%{ld_so_conf_file}
fi
%endif
/sbin/ldconfig

%if %{mdkversion} >= 200800
%pre -n %{drivername}-control-center
# Handle alternatives-era directory,
# it may confuse rpm.
if [ -L %{_datadir}/ati ]; then
	rm %{_datadir}/ati
fi
%endif

%post -n %{drivername}-control-center
%{update_menus}
%if %{mdkversion} >= 200800
[ -d %{_datadir}/fglrx ] && rm -r %{_datadir}/fglrx
[ -d %{_datadir}/fglrx-hd2000 ] && rm -r %{_datadir}/fglrx-hd2000
true
%endif

%postun -n %{drivername}-control-center
%{clean_menus}

%post -n dkms-%{drivername}
/usr/sbin/dkms --rpm_safe_upgrade add -m %{drivername} -v %{version}-%{release} &&
/usr/sbin/dkms --rpm_safe_upgrade build -m %{drivername} -v %{version}-%{release} &&
/usr/sbin/dkms --rpm_safe_upgrade install -m %{drivername} -v %{version}-%{release} --force

# rmmod any old driver if present and not in use (e.g. by X)
rmmod fglrx > /dev/null 2>&1 || true

%preun -n dkms-%{drivername}
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{drivername} -v %{version}-%{release} --all

# rmmod any old driver if present and not in use (e.g. by X)
rmmod fglrx > /dev/null 2>&1 || true

%clean
rm -rf %{buildroot}

%files -n %{driverpkgname}
%defattr(-,root,root)
%doc README.install.urpmi README.manual-setup
%doc common/usr/share/doc/fglrx/*

%if %{mdkversion} >= 200700
%ghost %{_sysconfdir}/ld.so.conf.d/GL.conf
%dir %{_sysconfdir}/ld.so.conf.d/GL
%{_sysconfdir}/ld.so.conf.d/GL/ati.conf
%else
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/ati.conf
%endif

%dir %{_sysconfdir}/ati
%{_sysconfdir}/ati/control
%{_sysconfdir}/ati/signature
%config(noreplace) %{_sysconfdir}/ati/atiogl.xml
%{_sysconfdir}/ati/logo.xbm.example
%{_sysconfdir}/ati/logo_mask.xbm.example
%config %{_sysconfdir}/ati/authatieventsd.sh
%{_sysconfdir}/ati/amdpcsdb.default

%{_initrddir}/atieventsd

%{_sbindir}/atieventsd
%{_sbindir}/amdnotifyui
%{_sbindir}/atigetsysteminfo.sh

%{_bindir}/aticonfig
%{_bindir}/fgl_glxgears
%{_bindir}/fglrxinfo
%{_bindir}/fglrx_xgamma

%{xorg_libdir}/modules/drivers/fglrx_drv.so
%{xorg_libdir}/modules/linux/libfglrxdrm.so
%{xorg_libdir}/modules/glesx.*o

%{xorg_dridir}/fglrx_dri.so
%ifarch x86_64
%{xorg_dridir32}/fglrx_dri.so
%endif

%dir %{_libdir}/%{drivername}
%{_libdir}/%{drivername}/libGL.so.1
%{_libdir}/%{drivername}/libGL.so.1.*
%ifarch x86_64
%dir %{_prefix}/lib/%{drivername}
%{_prefix}/lib/%{drivername}/libGL.so.1
%{_prefix}/lib/%{drivername}/libGL.so.1.*
%endif

%{_libdir}/%{drivername}/libfglrx_gamma.so.1*
%{_libdir}/%{drivername}/libfglrx_pp.so.1*
%{_libdir}/%{drivername}/libfglrx_dm.so.1*
%{_libdir}/%{drivername}/libfglrx_tvout.so.1*
%{_libdir}/%{drivername}/libatiadlxx.so

%if !%{atibuild}
%{_mandir}/man1/fglrx_xgamma.1*
%endif
%{_mandir}/man8/atieventsd.8*

%dir /usr/X11R6/%{_lib}
%dir /usr/X11R6/%{_lib}/modules
%dir /usr/X11R6/%{_lib}/modules/dri
/usr/X11R6/%{_lib}/modules/dri/fglrx_dri.so
%ifarch x86_64
%dir /usr/X11R6/lib
%dir /usr/X11R6/lib/modules
%dir /usr/X11R6/lib/modules/dri
/usr/X11R6/lib/modules/dri/fglrx_dri.so
%endif

%files -n %{drivername}-control-center
%defattr(-,root,root)
%{_bindir}/amdcccle
%{_datadir}/ati
%if %{atibuild}
%{_iconsdir}/%{drivername}-amdcccle.xpm
%{_liconsdir}/%{drivername}-amdcccle.xpm
%else
%{_miconsdir}/%{drivername}-amdcccle.png
%{_iconsdir}/%{drivername}-amdcccle.png
%{_liconsdir}/%{drivername}-amdcccle.png
%endif
%{_datadir}/applications/mandriva-fglrx-amdcccle.desktop
%if %{mdkversion} <= 200600
%{_menudir}/%{drivername}-control-center
%endif

%files -n %{drivername}-devel
%defattr(-,root,root)
%{_libdir}/%{drivername}/libfglrx_gamma.a
%{_libdir}/%{drivername}/libfglrx_pp.a
%{_libdir}/%{drivername}/libfglrx_dm.a
%{_libdir}/%{drivername}/libfglrx_tvout.a
%{_libdir}/%{drivername}/libfglrx_gamma.so
%{_libdir}/%{drivername}/libfglrx_pp.so
%{_libdir}/%{drivername}/libfglrx_dm.so
%{_libdir}/%{drivername}/libfglrx_tvout.so
%{xorg_libdir}/modules/esut.a
%{xorg_includedir}/X11/extensions/fglrx_gamma.h
%dir %{_includedir}/GL
%{_includedir}/GL/*ATI.h
%{_libdir}/%{drivername}/libGL.so
%ifarch x86_64
%{_prefix}/lib/%{drivername}/libGL.so
%endif

%files -n dkms-%{drivername}
%defattr(-,root,root)
%{_usrsrc}/%{drivername}-%{version}-%{release}

%changelog
* %(LC_ALL=C date "+%a %b %d %Y") %{packager} %{version}-%{release}
- automatic package build by the ATI installer

* Wed Mar 26 2008 Anssi Hannula <anssi@mandriva.org> 8.471-2mdv2008.1
+ Revision: 190341
- do not use alternatives for amdcccle desktop file (fixes #39200)
- amdpcsdb.default is not a config file
- control-center subpackage requires the main package

* Sat Mar 08 2008 Anssi Hannula <anssi@mandriva.org> 8.471-1mdv2008.1
+ Revision: 182051
- new version 8.3 aka 8.471 aka 8.47.3
- now using the ati-packager-helper.sh versioning
- update comments

* Thu Feb 14 2008 Anssi Hannula <anssi@mandriva.org> 8.45.5-1mdv2008.1
+ Revision: 168540
- new version
- drop empty fields from initscript
- exclude unused patches from ati-packager.sh build
- use ati reported version in ati-packager.sh builds
- change distsuffix of ati-packager.sh builds to amd.mdv

* Sun Jan 20 2008 Anssi Hannula <anssi@mandriva.org> 8.45.2-1mdv2008.1
+ Revision: 155387
- new version
- fix ati-packager.sh build
- use automatic detection when no distroversion is selected in
  ati-packager.sh
- restore menu on 2006.0 builds

  + Thierry Vignaud <tvignaud@mandriva.com>
    - drop old menu

* Sun Dec 30 2007 Anssi Hannula <anssi@mandriva.org> 8.44.3-4mdv2008.1
+ Revision: 139573
- obsolete ati-control-center on 2008.0 and newer

* Tue Dec 25 2007 Anssi Hannula <anssi@mandriva.org> 8.44.3-3mdv2008.1
+ Revision: 137792
- fix exit status of %%posttrans in cases where unhandled files exist
  in /etc/fglrx or /etc/fglrx-hd2000

* Tue Dec 25 2007 Anssi Hannula <anssi@mandriva.org> 8.44.3-2mdv2008.1
+ Revision: 137767
- handle more upgrade scenarios
- require kmod(fglrx) in driver package

* Tue Dec 25 2007 Anssi Hannula <anssi@mandriva.org> 8.44.3-1mdv2008.1
+ Revision: 137625
- new version (internally 8.44.3/8.443.1, announced as 7.12)
- drop 2.6.23 support patch, applied upstream

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tvignaud@mandriva.com>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Oct 28 2007 Anssi Hannula <anssi@mandriva.org> 8.40.4-8mdv2008.1
+ Revision: 102854
- use alternatives for fglrx_dri.so to allow 8.42.3 cohabitation

* Fri Sep 21 2007 Anssi Hannula <anssi@mandriva.org> 8.40.4-7mdv2008.0
+ Revision: 91892
- apply a workaround patch for kernel 2.6.23

* Thu Sep 20 2007 Anssi Hannula <anssi@mandriva.org> 8.40.4-6mdv2008.0
+ Revision: 91578
- change %%post to %%posttrans to prevent more problems with rpm removing files

* Thu Sep 20 2007 Anssi Hannula <anssi@mandriva.org> 8.40.4-5mdv2008.0
+ Revision: 91420
- provide ghosts for directories as well (fixes #33809)
- disable parallel make of fglrx_gamma lib

* Sun Sep 16 2007 Anssi Hannula <anssi@mandriva.org> 8.40.4-4mdv2008.0
+ Revision: 87594
- add conflict with old drakx-kbd-mouse-x11
- fix suggests
- check for driver before printing anything in atieventsd initscript
- use alternatives for more files to allow co-existence with fglrx-hd2000

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 8.40.4-3mdv2008.0
+ Revision: 85915
- start atieventsd on runlevel 5 only
- fix versioned provides/obsoletes in control center subpkg
- no need to own /usr/X11R6, it is owned by x11-server-common
- drop useless fgl_glxgears man page, it was an old upstream one
  without all the correct options
- fix menu entry

* Fri Aug 31 2007 Anssi Hannula <anssi@mandriva.org> 8.40.4-2mdv2008.0
+ Revision: 76979
- drop executable perm of fglrx.spec (Charles A Edwards)
- add a note into README.install.urpmi about reconfiguring being
  unnecessary when upgrading

  + Thierry Vignaud <tvignaud@mandriva.com>
    - kill desktop-file-validate's 'warning: key "Encoding" in group "Desktop Entry" is deprecated'

* Sun Aug 26 2007 Anssi Hannula <anssi@mandriva.org> 8.40.4-1mdv2008.0
+ Revision: 71697
- use alternatives for libglx.so
- update documentation
- 8.40.4
- rewrite spec
- preapply uname_r patch
- can now be built as standard rpm as well, i.e. outside ati installer
- build some tools from sources when built outside ati installer
- add patches that fix includes in some tools
- use %%{version}-%%{release} for dkms PACKAGE_VERSION
- now has a source package, named fglrx
- rename to x11-driver-video-fglrx and dkms-fglrx on cooker
- move tools to main driver package, except for amdcccle
- introduce control-center subpackage for amdcccle
- require fixed update-alternatives instead of workarounding bugs
- use generic license tag
- remove hardcoded vendor, packager, prefix tags
- adapt and simplify ati-packager.sh for new spec layout
- clean libGL.so.1 from provides (bug #28216)
- first Mandriva build with the tools enabled (bug #28094)
- better URL
- exclusivearch ix86 x86_64
- add post and preun script requires on dkms
- re-enable devel package
- do not call the next dkms step if previous fails
- own the old X11R6 directories where we are creating the compatibility
  symlink for now
- move atieventsd to the main package; the separation was not useful as it
  was required by main package
- provide png icon
- change distsuffix of the ati installer build
- do not leave temp directory behind in installer mode when rpm-build is not
  installed

