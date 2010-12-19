
##############################################################################
# This .spec file is dual licensed. It can be distributed either with the    #
# terms of GPL version 2 or newer, or with the MIT license included below.   #
# Removing either GPL or MIT license when distributing this file is allowed. #
##############################################################################
# - start of MIT license -
# Copyright (c) 2007-2009 Anssi Hannula, Luiz Fernando Capitulino, Colin Guthrie, Thomas Backlund
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
# - end of MIT license -

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

# When updating, please add new ids to ldetect-lst (merge2pcitable.pl).

# version in installer filename:
%define oversion	10-12
# Advertised version, for description:
%define mversion	10.12
# driver version from ati-packager-helper.sh:
%define iversion	8.801
# release:
%define rel		2
# rpm version (adds 0 in order to not go backwards if iversion is two-decimal)
%define version		%{iversion}%([ $(echo %iversion | wc -c) -le 5 ] && echo 0)
%else
# Best-effort if ATI has made late changes (in atibuild mode)
%define _default_patch_fuzz 2
%endif

%define priority	1000
%define release %mkrel %{rel}

# set to 1 for a prerelease driver with an ubuntu tarball as source
%define ubuntu_prerelease 0

%define driverpkgname	x11-driver-video-fglrx
%define drivername	fglrx
%define xorg_version	pic
# highest supported videodrv abi
%define videodrv_abi	8
%define xorg_libdir	%{_libdir}/xorg
%define xorg_dridir	%{_libdir}/dri
%define xorg_dridir32	%{_prefix}/lib/dri
%define ld_so_conf_file	ati.conf
%define ati_extdir	%{_libdir}/%{drivername}/xorg
%define xorg_extra_modules	%{_libdir}/xorg/extra-modules
%define bundle_qt	0
# The entry in Cards+ this driver should be associated with, if there is
# no entry in ldetect-lst default pcitable:
# cooker ldetect-lst should be up-to-date
%define ldetect_cards_name      %nil

%if %{atibuild}
# ATI cards not listed in main ldetect-lst pcitable are not likely
# to be supported by radeon which is from the same time period.
# radeonhd has greater chance of working due to it not using ID lists.
# (main pcitable entries override our entries)
%define ldetect_cards_name	ATI Radeon HD 2000 and later (vesa/fglrx)
%endif

%if %{mdkversion} <= 201020
%define ldetect_cards_name	ATI Radeon HD 2000 and later (vesa/fglrx)
%endif

%if %{mdkversion} <= 201000
%define ldetect_cards_name	ATI Radeon HD 2000 and later (radeonhd/fglrx)
%endif

%if %{mdkversion} <= 200900
%define ati_extdir	%{xorg_libdir}/modules/extensions/%{drivername}
# radeonhd/fglrx
%define ldetect_cards_name      ATI Radeon X1300 and later
%endif

%if %{mdkversion} <= 200810
%define bundle_qt	1
# vesa/fglrx
%define ldetect_cards_name      ATI Radeon HD 3200
%endif

%if %{mdkversion} <= 200800
# vesa/fglrx
%define ldetect_cards_name      ATI Radeon X1300 - X1950
%endif

%if %{mdkversion} <= 200710
%define driverpkgname	ati
%define drivername	ati
# fbdev/fglrx
%define ldetect_cards_name      ATI Radeon X1300 and later
%endif

%if %{mdkversion} <= 200700
# vesa/fglrx
%define ldetect_cards_name      ATI Radeon (vesa)
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

%define qt_requires_exceptions %nil
%if %{bundle_qt}
# do not require Qt if it is bundled
%define qt_requires_exceptions \\|libQtCore\\.so\\|libQtGui\\.so
%endif

# do not require fglrx stuff, they are all included
%define common_requires_exceptions libfglrx.\\+\\.so\\|libati.\\+\\.so%{qt_requires_exceptions}

%ifarch x86_64
# (anssi) Allow installing of 64-bit package if the runtime dependencies
# of 32-bit libraries are not satisfied. If a 32-bit package that requires
# libGL.so.1 is installed, the 32-bit mesa libs are pulled in and that will
# pull the dependencies of 32-bit fglrx libraries in as well.
%define _requires_exceptions %common_requires_exceptions\\|lib.*so\\.[^(]\\+\\(([^)]\\+)\\)\\?$
%else
%define _requires_exceptions %common_requires_exceptions
%endif

# (anssi) Do not require qt for amdnotifyui (used as event notifier, as
# of 04/2010 only for DisplayPort failures). installing
# fglrx-control-center will satisfy the dependency.
# It is not moved to fglrx-control-center as due to its small size it may
# be wanted on e.g. KDE Ones, which can't have the full fglrx-control-center,
# and due to it having nothing to do with fglrx-control-center.
%define _exclude_files_from_autoreq ^%{_sbindir}/amdnotifyui$

Summary:	ATI proprietary X.org driver and libraries
Name:		%{name}
Version:	%{version}
Release:	%{release}
%if !%{atibuild}
%if !%{ubuntu_prerelease}
Source0:	https://a248.e.akamai.net/f/674/9206/0/www2.ati.com/drivers/linux/ati-driver-installer-%{oversion}-x86.x86_64.run
%else
Source0:        fglrx-installer_%{iversion}.orig.tar.gz
%endif
%endif
Source1:	ati-packager.sh
Source2:	atieventsd.init
%if !%{atibuild}
# Generates fglrx.spec from Mandriva SVN for use in AMD installer
# archive. Requires kenobi access for fetching names for changelog.
# (for manual use)
Source10:	generate-fglrx-spec-from-svn.sh
%endif
%if !%{atibuild}
# Patches that only affect tools (not built in atibuild mode)
Patch1:		ati-8.19.10-fglrx_gamma-extutil-include.patch
Patch4:		fglrx_gamma-fix-underlinking.patch
%endif
Patch3:		fglrx-authfile-locations.patch
Patch9:		fglrx-make_sh-custom-kernel-dir.patch
# do not probe /proc for kernel info as we may be building for a
# different kernel
Patch10:	fglrx-make_sh-no-proc-probe.patch

License:	Freeware
URL:		http://ati.amd.com/support/driver.html
Group:		System/Kernel and hardware
ExclusiveArch:	%{ix86} x86_64
BuildRoot:	%{_tmppath}/%{name}-root
%if !%{atibuild}
BuildRequires:	mesagl-devel
BuildRequires:	libxmu-devel
BuildRequires:	libxaw-devel
BuildRequires:	libxp-devel
BuildRequires:	libxtst-devel
BuildRequires:	imake
# Used by atieventsd:
Suggests:	acpid
BuildRequires:	ImageMagick
%endif

%description
Source package of the ATI proprietary driver. Binary packages are
named x11-driver-video-fglrx on Mandriva Linux 2008 and later, and ati on
2007 and earlier.
%if !%{atibuild}
This package corresponds to ATI Catalyst version %mversion.
%endif

%package -n %{driverpkgname}
Summary:	ATI proprietary X.org driver and libraries
Group:		System/Kernel and hardware
Requires(post):	update-alternatives >= 1.9.0
Requires(postun): update-alternatives
Obsoletes:	ati_igp
%if %{mdkversion} >= 200800
Suggests:	%{drivername}-control-center = %{version}
Obsoletes:	ati < %{version}-%{release}
Provides:	ati = %{version}-%{release}
Conflicts:	x11-server-common < 1.3.0.0-17
Conflicts:	drakx-kbd-mouse-x11 < 0.26
Obsoletes:	x11-driver-video-fglrx-hd2000 < 8.42.3-5
%if %{mdkversion} >= 200810
Requires:	kmod(fglrx) = %{version}
%else
# no versioned provides on 2008.0
Requires:	kmod(fglrx)
%endif
%endif
%if %{mdkversion} >= 200900
# libdri.so
Conflicts:	x11-server-common < 1.4.2-5
%endif
%if %{mdkversion} >= 200910
# many intermediate changes in alternatives scheme
Conflicts:	x11-server-common < 1.6.0-11
%endif
%if %{mdkversion} >= 201100
Requires:	x11-server-common >= 1.9
%if !%{atibuild}
# Conflict with the next videodrv ABI break.
# The driver may support multiple ABI versions and therefore
# a strict version-specific requirement would not be enough.
Conflicts:	xserver-abi(videodrv-%(echo $((%{videodrv_abi} + 1))))
%endif
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
%if !%{atibuild}
This package corresponds to ATI Catalyst version %mversion.
%endif

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
%if !%{bundle_qt}
# 2009.0 and 2009.1 have this one in updates only
Requires:	%{_lib}qtcore4 >= 3:4.5.2
%endif

%description -n %{drivername}-control-center
AMD Catalyst Control Center Linux Edition, a graphical configuration
utility for the ATI proprietary X.org driver.
%if !%{atibuild}
This package corresponds to ATI Catalyst version %mversion.
%endif

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
%if !%{atibuild}
This package corresponds to ATI Catalyst version %mversion.
%endif

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
# patches affects common, so we cannot symlink it:
cp -a %{ati_dir}/common .
%else
%if %ubuntu_prerelease
%setup -q -T -D -a 0
ln -s . common
%else
sh %{SOURCE0} --extract .
%endif

mkdir fglrx_tools
tar -xzf common/usr/src/ati/fglrx_sample_source.tgz -C fglrx_tools
cd fglrx_tools # ensure patch does not touch outside
%patch1 -p1
%patch4 -p1
cd -
cmp common/usr/X11R6/include/X11/extensions/fglrx_gamma.h fglrx_tools/lib/fglrx_gamma/fglrx_gamma.h
%if %ubuntu_prerelease
[ -d "%xverdir" ] || (echo This driver version does not support your X.org server. Please wait for a new release from ATI. >&2; false)
%else
[ "%iversion" = "$(./ati-packager-helper.sh --version)" ]
%endif
%endif

cd common # ensure patches do not touch outside
%patch3 -p2
%patch9 -p2
%patch10 -p2
cd ..

cat > README.install.urpmi <<EOF
This driver is for ATI Radeon HD 2000 and newer cards.
Reconfiguring is not necessary when upgrading from a previous Mandriva ATI
driver package.

Use XFdrake to configure X to use the correct ATI driver. Any needed
packages will be automatically installed if not already present.
1. Run XFdrake as root.
2. Go to the Graphics Card list.
3. Select your card (it is usually already autoselected).
4. Answer any questions asked and then quit.
%if %{mdkversion} <= 200810
5. Run "readlink -f /etc/alternatives/gl_conf". If it says
   "%{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file}", add the following lines into the
   Files section of %{_sysconfdir}/X11/xorg.conf:
          ModulePath "%{ati_extdir}"
          ModulePath "%{xorg_libdir}/modules"
%endif

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
%if %{mdkversion} >= 200900
  o Remove any 'ModulePath' lines from the Files section
%else
  o Make the lines below the only 'ModulePath' lines in the Files section:
      ModulePath "%{ati_extdir}"
      ModulePath "%{xorg_libdir}/modules"
%endif
- Run "update-alternatives --set gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file}" as root.
- Run "ldconfig" as root.
EOF

cat > README.8.600.upgrade.urpmi <<EOF
REMOVED GRAPHICS DRIVER SUPPORT NOTIFICATION:
Versions 8.600 and later of ATI Proprietary Graphics driver (fglrx) only
support Radeon HD 2000 (r600) or newer cards.

If you have an older Radeon card or are unsure, please reconfigure your
driver:
1. Run XFdrake as root or select Graphical server configuration in
   Mandriva Control Center.
2. Go to the Graphics Card list.
3. Select your card (it is usually already autoselected).
4. Answer any questions asked and then quit.
EOF

%if %{mdkversion} <= 200810
cat > README.8.532.upgrade.urpmi <<EOF
IMPORTANT NOTE:
Additional manual upgrade steps are needed in order to fully enable all
features of this version of the proprietary ATI driver on this release
of Mandriva Linux:
Run "readlink -f /etc/alternatives/gl_conf". If it says
"%{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file}", add the following two lines in the Files section
of %{_sysconfdir}/X11/xorg.conf:
      ModulePath "%{ati_extdir}"
      ModulePath "%{xorg_libdir}/modules"
EOF
%endif

%build
%if !%{atibuild}
# %atibuild is done with minimal buildrequires
cd fglrx_tools/lib/fglrx_gamma
xmkmf
# parallel make broken (2007-09-18)
make CC="%__cc %optflags" SHLIBGLOBALSFLAGS="%{?ldflags} -L%{_prefix}/X11R6/%{_lib}"
cd -
cd fglrx_tools/fgl_glxgears
xmkmf
%make RMAN=/bin/true CC="%__cc %optflags -I../../common/usr/include" EXTRA_LDOPTIONS="%{?ldflags}"
cd -
cd fglrx_tools/programs/fglrx_gamma
xmkmf
%make INSTALLED_LIBS=-L../../lib/fglrx_gamma INCLUDES=-I../../../common/usr/X11R6/include CC="%__cc %optflags" RMAN=/bin/true EXTRA_LDOPTIONS="%{?ldflags}"
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
# uname_v set to none so that make.sh doesn't try to use "uname -v" to see
# if the target kernel is SMP (we may be compiling for a different kernel)
MAKE[0]="sh make.sh --uname_r=\${kernelver} --uname_v=none --kernel-dir=\${kernel_source_dir} --no-proc-probe --norootcheck"
CLEAN="rm -rf 2.6.x/.tmp_versions; make -C2.6.x clean"
AUTOINSTALL="yes"
EOF

# headers
install -d -m755		%{buildroot}%{_includedir}
cp -a common/usr/include/*	%{buildroot}%{_includedir}
chmod 0644 %{buildroot}%{_includedir}/*/*.h

install -d -m755 %{buildroot}%{_includedir}/X11/extensions
install -m644 common/usr/X11R6/include/X11/extensions/*.h  %{buildroot}%{_includedir}/X11/extensions

# install binaries
install -d -m755					%{buildroot}%{_sbindir}
install -m755 %{archdir}/usr/sbin/*			%{buildroot}%{_sbindir}
install -m755 common/usr/sbin/*				%{buildroot}%{_sbindir}
install -d -m755					%{buildroot}%{_bindir}
install -m755 %{archdir}/usr/X11R6/bin/*		%{buildroot}%{_bindir}
install -m755 common/usr/X11R6/bin/*			%{buildroot}%{_bindir}
%if !%{atibuild}
# install self-built binaries
install -m755 fglrx_tools/fgl_glxgears/fgl_glxgears	%{buildroot}%{_bindir}
install -m755 fglrx_tools/programs/fglrx_gamma/fglrx_xgamma %{buildroot}%{_bindir}
%endif

# atieventsd initscript
install -d -m755 %{buildroot}%{_initrddir}
install -m755 %{SOURCE2} %{buildroot}%{_initrddir}/atieventsd

# amdcccle data files
install -d -m755 %{buildroot}%{_datadir}/ati/amdcccle
install -m644 common/usr/share/ati/amdcccle/*.qm %{buildroot}%{_datadir}/ati/amdcccle
rm -f amdcccle.langs
for file in common/usr/share/ati/amdcccle/*.qm; do
	file=$(basename $file)
	lang=${file#amdcccle_}
	lang=${lang%%.qm}
	echo "%%lang($lang) %{_datadir}/ati/amdcccle/$file" >> amdcccle.langs
done

# amdcccle super-user mode
install -d -m755 %{buildroot}%{_sysconfdir}/security/console.apps
install -d -m755 %{buildroot}%{_sysconfdir}/pam.d
install -m644 common/etc/security/console.apps/* %{buildroot}%{_sysconfdir}/security/console.apps
ln -s su %{buildroot}%{_sysconfdir}/pam.d/amdcccle-su

# man pages
install -d -m755 %{buildroot}%{_mandir}/man1 %{buildroot}%{_mandir}/man8
%if !%{atibuild}
install -m644 fglrx_tools/programs/fglrx_gamma/fglrx_xgamma.man %{buildroot}%{_mandir}/man1/fglrx_xgamma.1
%endif
install -m644 common/usr/share/man/man8/* %{buildroot}%{_mandir}/man8

# menu entry
install -d -m755 %{buildroot}%{_datadir}/applications
install -m644 common/usr/share/applications/* %{buildroot}%{_datadir}/applications
sed -i 's,^Icon=.*$,Icon=%{drivername}-amdcccle,' %{buildroot}%{_datadir}/applications/*.desktop
# control center doesn't really use GNOME/KDE libraries:
sed -i 's,GNOME;KDE;,,' %{buildroot}%{_datadir}/applications/*.desktop

# icons
install -d -m755 %{buildroot}%{_miconsdir} %{buildroot}%{_iconsdir} %{buildroot}%{_liconsdir}
%if !%{atibuild}
convert common/usr/share/icons/ccc_large.xpm -resize 16x16 %{buildroot}%{_miconsdir}/%{drivername}-amdcccle.png
convert common/usr/share/icons/ccc_large.xpm -resize 32x32 %{buildroot}%{_iconsdir}/%{drivername}-amdcccle.png
convert common/usr/share/icons/ccc_large.xpm -resize 48x48 %{buildroot}%{_liconsdir}/%{drivername}-amdcccle.png
%else
install -m644 common/usr/share/icons/ccc_large.xpm %{buildroot}%{_iconsdir}/%{drivername}-amdcccle.xpm
%endif

# install libraries
install -d -m755					%{buildroot}%{_libdir}/%{drivername}
install -m755 %{archdir}/usr/X11R6/%{_lib}/*.*		%{buildroot}%{_libdir}/%{drivername}
install -m755 %{archdir}/usr/%{_lib}/*			%{buildroot}%{_libdir}/%{drivername}
/sbin/ldconfig -n					%{buildroot}%{_libdir}/%{drivername}
# create devel symlinks
for file in %{buildroot}%{_libdir}/%{drivername}/*.so.*.*; do
	ln -s $(basename $file) ${file%%.so*}.so;
done
%ifarch x86_64
install -d -m755					%{buildroot}%{_prefix}/lib/%{drivername}
install -m755 arch/x86/usr/X11R6/lib/libGL*		%{buildroot}%{_prefix}/lib/%{drivername}
install -m755 arch/x86/usr/lib/*			%{buildroot}%{_prefix}/lib/%{drivername}
/sbin/ldconfig -n					%{buildroot}%{_prefix}/lib/%{drivername}
# create devel symlinks
for file in %{buildroot}%{_prefix}/lib/%{drivername}/*.so.*.*; do
	ln -s $(basename $file) ${file%%.so*}.so;
done
%endif

%if %{bundle_qt}
# install the bundled Qt4 libs on distros with qt4 < 4.4.2
install -d -m755				%{buildroot}%{_libdir}/%{drivername}-qt4
install -m755 %{archdir}/usr/share/ati/%{_lib}/*	%{buildroot}%{_libdir}/%{drivername}-qt4
# RPATH of amdcccle points to datadir, we create a symlink there:
install -d -m755				%{buildroot}/usr/share/ati
ln -s %{_libdir}/%{drivername}-qt4		%{buildroot}/usr/share/ati/%{_lib}
%endif

%if !%{atibuild}
install -m755 fglrx_tools/lib/fglrx_gamma/libfglrx_gamma.so.1.0 %{buildroot}%{_libdir}/%{drivername}
install -m644 fglrx_tools/lib/fglrx_gamma/libfglrx_gamma.a %{buildroot}%{_libdir}/%{drivername}
%endif

# install X.org files
install -d -m755						%{buildroot}%{xorg_libdir}/modules/drivers
install -m755 %{xverdir}/usr/X11R6/%{_lib}/modules/drivers/*.so* %{buildroot}%{xorg_libdir}/modules/drivers
install -d -m755						%{buildroot}%{xorg_libdir}/modules/linux
install -m755 %{xverdir}/usr/X11R6/%{_lib}/modules/linux/*.so*	%{buildroot}%{xorg_libdir}/modules/linux
install -m644 %{xverdir}/usr/X11R6/%{_lib}/modules/*.*o		%{buildroot}%{xorg_libdir}/modules
install -d -m755						%{buildroot}%{ati_extdir}
install -m755 %{xverdir}/usr/X11R6/%{_lib}/modules/extensions/*.so* %{buildroot}%{ati_extdir}

%if %{mdkversion} == 200900
touch							%{buildroot}%{xorg_libdir}/modules/extensions/libdri.so
%endif
%if %{mdkversion} >= 200800 && %{mdkversion} <= 200900
touch							%{buildroot}%{xorg_libdir}/modules/extensions/libglx.so
%endif

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

# ld.so.conf
install -d -m755			%{buildroot}%{_sysconfdir}/ld.so.conf.d/GL
echo "%{_libdir}/%{drivername}" >	%{buildroot}%{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file}
%ifarch x86_64
echo "%{_prefix}/lib/%{drivername}" >>	%{buildroot}%{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file}
%endif
touch					%{buildroot}%{_sysconfdir}/ld.so.conf.d/GL.conf

# modprobe.conf
install -d -m755			%{buildroot}%{_sysconfdir}/modprobe.d
touch					%{buildroot}%{_sysconfdir}/modprobe.d/display-driver
install -d -m755			%{buildroot}%{_sysconfdir}/%{drivername}
echo "blacklist radeon"			> %{buildroot}%{_sysconfdir}/%{drivername}/modprobe.conf

# modprobe.preload.d
install -d -m755			%{buildroot}%{_sysconfdir}/modprobe.preload.d
touch					%{buildroot}%{_sysconfdir}/modprobe.preload.d/display-driver
echo "fglrx"				> %{buildroot}%{_sysconfdir}/%{drivername}/modprobe.preload

# XvMCConfig
echo "libAMDXvBA.so.1" > %{buildroot}%{_sysconfdir}/%{drivername}/XvMCConfig

# install ldetect-lst pcitable files for backports
sed -ne 's|^\s*FGL_ASIC_ID(\(0x....\)).*|\1|gp' common/lib/modules/fglrx/build_mod/fglrxko_pci_ids.h | tr '[:upper:]' '[:lower:]' | sort -u | sed 's,^.*$,0x1002\t\0\t"%{ldetect_cards_name}",' > pcitable.fglrx.lst
[ $(stat -c%s pcitable.fglrx.lst) -gt 500 ]
%if "%{ldetect_cards_name}" != ""
install -d -m755 %{buildroot}%{_datadir}/ldetect-lst/pcitable.d
gzip -c pcitable.fglrx.lst > %{buildroot}%{_datadir}/ldetect-lst/pcitable.d/40%{drivername}.lst.gz
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

%{_sbindir}/update-alternatives \
	--install %{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file} %{priority} \
	--slave %{_sysconfdir}/X11/XvMCConfig xvmcconfig %{_sysconfdir}/%{drivername}/XvMCConfig \
	--slave %{_libdir}/libAMDXvBA.cap %{_lib}AMDXvBA_cap %{_libdir}/%{drivername}/libAMDXvBA.cap \
%ifarch x86_64
	--slave %{_prefix}/lib/libAMDXvBA.cap libAMDXvBA_cap %{_libdir}/%{drivername}/libAMDXvBA.cap \
%endif
	--slave %{_sysconfdir}/modprobe.d/display-driver display-driver.modconf %{_sysconfdir}/%{drivername}/modprobe.conf \
	--slave %{_sysconfdir}/modprobe.preload.d/display-driver display-driver.preload %{_sysconfdir}/%{drivername}/modprobe.preload \
%if %{mdkversion} >= 200910
	--slave %{xorg_extra_modules} xorg_extra_modules %{ati_extdir} \
%else
%if %{mdkversion} >= 200900
	--slave %{_libdir}/xorg/modules/extensions/libdri.so libdri.so %{_libdir}/xorg/modules/extensions/standard/libdri.so \
%endif
%if %{mdkversion} >= 200800
	--slave %{_libdir}/xorg/modules/extensions/libglx.so libglx %{ati_extdir}/libglx.so
%endif

%if %{mdkversion} >= 200800
if [ "$(readlink -e %{_sysconfdir}/ld.so.conf.d/GL.conf)" = "%{_sysconfdir}/ld.so.conf.d/GL/ati-hd2000.conf" ]; then
	# Switch from the obsolete hd2000 branch:
	%{_sbindir}/update-alternatives --set gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file}
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
# Call /sbin/ldconfig explicitely due to alternatives
/sbin/ldconfig -X
%_post_service atieventsd
%if "%{ldetect_cards_name}" != ""
[ -x %{_sbindir}/update-ldetect-lst ] && %{_sbindir}/update-ldetect-lst || :
%endif

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
if [ ! -f %{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file} ]; then
  %{_sbindir}/update-alternatives --remove gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file}
fi
# Call /sbin/ldconfig explicitely due to alternatives
/sbin/ldconfig
%if "%{ldetect_cards_name}" != ""
[ -x %{_sbindir}/update-ldetect-lst ] && %{_sbindir}/update-ldetect-lst || :
%endif

%if %{mdkversion} >= 200800
%pre -n %{drivername}-control-center
# Handle alternatives-era directory,
# it may confuse rpm.
if [ -L %{_datadir}/ati ]; then
	rm %{_datadir}/ati
fi
%endif

%post -n %{drivername}-control-center
%if %mdkversion < 200900
%{update_menus}
%endif
%if %{mdkversion} >= 200800
[ -d %{_datadir}/fglrx ] && rm -r %{_datadir}/fglrx
[ -d %{_datadir}/fglrx-hd2000 ] && rm -r %{_datadir}/fglrx-hd2000
true
%endif

%if %mdkversion < 200900
%postun -n %{drivername}-control-center
%{clean_menus}
%endif

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
%doc README.8.600.upgrade.urpmi
# the documentation files are grossly out of date; the configuration options
# described in configure.html seem to be used by the driver, though, so it is
# packaged, while the other html files are not:
%doc common/usr/share/doc/fglrx/configure.html
%doc common/usr/share/doc/fglrx/ATI_LICENSE.TXT
%if %{mdkversion} <= 200810
%doc README.8.532.upgrade.urpmi
%endif

%if "%{ldetect_cards_name}" != ""
%{_datadir}/ldetect-lst/pcitable.d/40%{drivername}.lst.gz
%endif

%ghost %{_sysconfdir}/ld.so.conf.d/GL.conf
%dir %{_sysconfdir}/ld.so.conf.d/GL
%{_sysconfdir}/ld.so.conf.d/GL/ati.conf

%ghost %{_sysconfdir}/modprobe.d/display-driver
%ghost %{_sysconfdir}/modprobe.preload.d/display-driver
%dir %{_sysconfdir}/%{drivername}
%{_sysconfdir}/%{drivername}/XvMCConfig
%{_sysconfdir}/%{drivername}/modprobe.conf
%{_sysconfdir}/%{drivername}/modprobe.preload

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

%{_bindir}/amdupdaterandrconfig
%{_bindir}/amdxdg-su
%{_bindir}/aticonfig
%{_bindir}/atiodcli
%{_bindir}/atiode
%{_bindir}/fgl_glxgears
%{_bindir}/fglrxinfo
%{_bindir}/fglrx_xgamma

%{xorg_libdir}/modules/drivers/fglrx_drv.so
%{xorg_libdir}/modules/linux/libfglrxdrm.so
%{xorg_libdir}/modules/amdxmm.*o
%{xorg_libdir}/modules/glesx.*o

%dir %{ati_extdir}
%{ati_extdir}/libglx.so
%if %{mdkversion} == 200900
%ghost %{xorg_libdir}/modules/extensions/libdri.so
%endif
%if %{mdkversion} >= 200800 && %{mdkversion} <= 200900
%ghost %{xorg_libdir}/modules/extensions/libglx.so
%endif

%{xorg_dridir}/fglrx_dri.so
%ifarch x86_64
%{xorg_dridir32}/fglrx_dri.so
%endif

%dir %{_libdir}/%{drivername}
%{_libdir}/%{drivername}/libGL.so.1
%{_libdir}/%{drivername}/libGL.so.1.*
%{_libdir}/%{drivername}/libaticalcl.so
%{_libdir}/%{drivername}/libaticaldd.so
%{_libdir}/%{drivername}/libaticalrt.so
%{_libdir}/%{drivername}/libatiuki.so.1*
%ifarch x86_64
%dir %{_prefix}/lib/%{drivername}
%{_prefix}/lib/%{drivername}/libGL.so.1
%{_prefix}/lib/%{drivername}/libGL.so.1.*
%{_prefix}/lib/%{drivername}/libaticalcl.so
%{_prefix}/lib/%{drivername}/libaticaldd.so
%{_prefix}/lib/%{drivername}/libaticalrt.so
%{_prefix}/lib/%{drivername}/libatiuki.so.1*
%endif

%{_libdir}/%{drivername}/libfglrx_gamma.so.1*
%{_libdir}/%{drivername}/libfglrx_dm.so.1*
%{_libdir}/%{drivername}/libatiadlxx.so
%{_libdir}/%{drivername}/libAMDXvBA.cap
%{_libdir}/%{drivername}/libAMDXvBA.so.1*
%{_libdir}/%{drivername}/libXvBAW.so.1*

%if !%{atibuild}
%{_mandir}/man1/fglrx_xgamma.1*
%endif
%{_mandir}/man8/atieventsd.8*

%files -n %{drivername}-control-center -f amdcccle.langs
%defattr(-,root,root)
%doc common/usr/share/doc/amdcccle/*
%{_sysconfdir}/security/console.apps/amdcccle-su
%{_sysconfdir}/pam.d/amdcccle-su
%{_bindir}/amdcccle
%dir %{_datadir}/ati
%dir %{_datadir}/ati/amdcccle
%if %{atibuild}
%{_iconsdir}/%{drivername}-amdcccle.xpm
%else
%{_miconsdir}/%{drivername}-amdcccle.png
%{_iconsdir}/%{drivername}-amdcccle.png
%{_liconsdir}/%{drivername}-amdcccle.png
%endif
%{_datadir}/applications/amdcccle.desktop
%{_datadir}/applications/amdccclesu.desktop
%if %{bundle_qt}
%dir %{_libdir}/%{drivername}-qt4
%{_libdir}/%{drivername}-qt4/libQtCore.so.4
%{_libdir}/%{drivername}-qt4/libQtGui.so.4
%{_datadir}/ati/%{_lib}
%endif

%files -n %{drivername}-devel
%defattr(-,root,root)
%{_libdir}/%{drivername}/libfglrx_gamma.a
%{_libdir}/%{drivername}/libfglrx_dm.a
%{_libdir}/%{drivername}/libfglrx_gamma.so
%{_libdir}/%{drivername}/libfglrx_dm.so
%{_libdir}/%{drivername}/libAMDXvBA.so
%{_libdir}/%{drivername}/libXvBAW.so
%{_includedir}/X11/extensions/fglrx_gamma.h
%dir %{_includedir}/GL
%{_includedir}/GL/*ATI.h
%dir %{_includedir}/ATI
%dir %{_includedir}/ATI/GL
%{_includedir}/ATI/GL/*.h
%{_libdir}/%{drivername}/libGL.so
%{_libdir}/%{drivername}/libatiuki.so
%ifarch x86_64
%{_prefix}/lib/%{drivername}/libGL.so
%{_prefix}/lib/%{drivername}/libatiuki.so
%endif

%files -n dkms-%{drivername}
%defattr(-,root,root)
%{_usrsrc}/%{drivername}-%{version}-%{release}

%changelog
* %(LC_ALL=C date "+%a %b %d %Y") %{packager} %{version}-%{release}
- automatic package build by the ATI installer

* Fri Dec 17 2010 Oden Eriksson <oeriksson@mandriva.com> 8.801-1mdv2011.0
+ Revision: 622548
- 10.12, 8.801

* Thu Nov 18 2010 Anssi Hannula <anssi@mandriva.org> 8.791-1mdv2011.0
+ Revision: 598736
- new version 8.791 aka 10.11
- clarify atibuild conditional statement
- hardcode videodrv abi as the driver is precompiled

* Thu Nov 11 2010 Thierry Vignaud <tv@mandriva.org> 8.783-2mdv2011.0
+ Revision: 595848
- require xorg server with proper ABI

* Fri Oct 22 2010 Anssi Hannula <anssi@mandriva.org> 8.783-1mdv2011.0
+ Revision: 587534
- new version 8.783 aka 10.10
- rediff make_sh-custom-kernel-dir.patch

* Tue Oct 12 2010 Anssi Hannula <anssi@mandriva.org> 8.780-1mdv2011.0
+ Revision: 585045
- new 10.10 prerelease with X.org server 1.9 support (from Ubuntu)
- remove CVE-2010-3081 patch, fixed upstream
- rediff affected patches

* Sat Oct 02 2010 Thomas Backlund <tmb@mandriva.org> 8.771-3mdv2011.0
+ Revision: 582570
- Add compatibility with 2.6.36 kernels (P11, from Ubuntu)
- Use CFLAGS_MODULE together with MODFLAGS in make.sh (P12, from Ubuntu)

* Tue Sep 21 2010 Anssi Hannula <anssi@mandriva.org> 8.771-2mdv2011.0
+ Revision: 580368
- apply CVE-2010-3081 64bit security fix from the kernel commit c41d68a5
  locally (also fixes build on kernels with c41d68a5 applied)
- rediff custom-kernel-dir.patch

* Fri Sep 17 2010 Anssi Hannula <anssi@mandriva.org> 8.771-1mdv2011.0
+ Revision: 579247
- new version 10.9 aka 8.771
- switch to the upstream amdxdg-su wrapper for the superuser control
  center mode as it now works well

* Sat Sep 04 2010 Anssi Hannula <anssi@mandriva.org> 8.762-3mdv2011.0
+ Revision: 575801
- new version 8.762 aka 10.8

* Thu Aug 12 2010 Anssi Hannula <anssi@mandriva.org> 8.753-2mdv2011.0
+ Revision: 569320
- fix XvBA on x86_64 (.cap file was being loaded from a wrong place, so
  compatibility symlink was added; reported by Balcaen John)
- provide pcitable.d files on 2010.1 as well, marking cards as vesa/fglrx

* Thu Aug 12 2010 Anssi Hannula <anssi@mandriva.org> 8.753-1mdv2011.0
+ Revision: 569194
- new version 8.753 aka 10.7
- drop 2.6.34.patch, fixed upstream

* Fri Jul 09 2010 Anssi Hannula <anssi@mandriva.org> 8.741-1mdv2011.0
+ Revision: 549894
- new version 8.741 aka 10.6
- remove fglrx-2.6.33.patch, fixed upstream

* Fri Jun 11 2010 Anssi Hannula <anssi@mandriva.org> 8.732-1mdv2010.1
+ Revision: 547892
- new version 8.732 aka 10.5
- allow specifying repository url for generate-fglrx-spec-from-svn.sh
- version 8.723 aka 10.4
  o this is older than the previous version, but contains support for
    older X.org servers and is therefore suitable for backporting
- fix incorrect categories in menu entry files (issue reported by St?\195?\169phane)

* Wed May 05 2010 Anssi Hannula <anssi@mandriva.org> 8.723.1-6mdv2010.1
+ Revision: 542231
- add a modprobe.preload.d entry loading the module before X server
- blacklist radeon module in modprobe.d entry as udev will now otherwise
  load it

* Sat May 01 2010 Thomas Backlund <tmb@mandriva.org> 8.723.1-5mdv2010.1
+ Revision: 541442
- fix build with 2.6.34 series kernels (from Charles A Edwards)

* Wed Apr 28 2010 Anssi Hannula <anssi@mandriva.org> 8.723.1-4mdv2010.1
+ Revision: 540653
- add alternatives slave for libAMDXvBA.cap (fixes load of XvBA)
- update version info in description (this driver is actually newer than
  10.4, i.e. not a prerelease after all)

* Tue Apr 27 2010 Anssi Hannula <anssi@mandriva.org> 8.723.1-3mdv2010.1
+ Revision: 539736
- do not require qt4 libs in the main package (reported by Christophe
  Fergeau)
  o this allows installing the driver without installing qt4 libraries
  o without qt4 libraries DisplayLink failure notifications won't be shown
  o to get the notifications, users can install fglrx-control-center package

* Tue Apr 27 2010 Christophe Fergeau <cfergeau@mandriva.com> 8.723.1-2mdv2010.1
+ Revision: 539576
- rebuild so that shared libraries are properly stripped again

* Wed Apr 21 2010 Anssi Hannula <anssi@mandriva.org> 8.723.1-1mdv2010.1
+ Revision: 537743
- new 10.4 prerelease 8.723.1 from ubuntu
- fix module load on 32-bit 2.6.33+ systems (modified 2.6.33.patch)

* Tue Mar 30 2010 Anssi Hannula <anssi@mandriva.org> 8.721-1mdv2010.1
+ Revision: 528938
- new version 8.721 (10.4 prerelease from Ubuntu)
  o includes X.org server 1.7 support
- call ldconfig with -X parameter
- adapt file lists
- rediff fglrx-2.6.33.patch

* Tue Mar 30 2010 Anssi Hannula <anssi@mandriva.org> 8.712-1mdv2010.1
+ Revision: 528935
- new version 8.712 aka 10.3
- fix dkms build as non-root user
- fix false smp detection when running on smp kernel
- remove /tmp/AtiXUEvent* before starting atieventsd (fixes bug #57291)

* Thu Feb 25 2010 Anssi Hannula <anssi@mandriva.org> 8.702-1mdv2010.1
+ Revision: 511385
- new version 10.2 aka 8.702
- generalize requires_exceptions on libati*.so.* to avoid future surprises

* Fri Jan 29 2010 Anssi Hannula <anssi@mandriva.org> 8.690-3mdv2010.1
+ Revision: 498068
- call __cmpxchg with constant size argument on 2.6.33+ (2.6.33.patch
  modified, reported by Charles A Edwards)

* Thu Jan 28 2010 Anssi Hannula <anssi@mandriva.org> 8.690-2mdv2010.1
+ Revision: 497792
- add requires_exceptions on libatiuki.so.1 (Charles A Edwards)

* Thu Jan 28 2010 Anssi Hannula <anssi@mandriva.org> 8.690-1mdv2010.1
+ Revision: 497689
- new version 8.69 aka 10.1
- drop 2.6.32.patch, applied upstream
- add 2.6.33+ support (2.6.33.patch, fixes #57259)
- custom libdri.so has been dropped upstream
- do not package most of the very obsolete documentation (bug #57139)

* Fri Jan 08 2010 Anssi Hannula <anssi@mandriva.org> 8.681-3mdv2010.1
+ Revision: 487448
- fix dkms build on 2.6.32+ (fixes #56693, 2.6.32.patch from Ubuntu)

* Sat Dec 19 2009 Anssi Hannula <anssi@mandriva.org> 8.681-1mdv2010.1
+ Revision: 480058
- remove Mandriva 2006.0 support (this can be readded if still actually
  needed, please contact us in such a case)
- new version 8.681 aka 9.12
- use now-bundled QT4 libraries on old distributions as needed

* Sat Nov 21 2009 Anssi Hannula <anssi@mandriva.org> 8.671-1mdv2010.1
+ Revision: 468576
- add libxtst-devel as buildrequires (now needed on cooker due to headers
  having been moved away from x11 proto packages)
- use the new upstream desktop files instead of providing our own
- generate pcitable files on cooker as well in order to catch errors
  (they are still not really installed on cooker, just when backporting)
- new version 8.671 aka 9.11
- add a comment in .spec reminding to update ldetect-lst

* Fri Nov 06 2009 Anssi Hannula <anssi@mandriva.org> 8.661-2mdv2010.1
+ Revision: 461590
- rebuild due to a missing changelog entry for the previous release

* Fri Nov 06 2009 Anssi Hannula <anssi@mandriva.org> 8.661-1mdv2010.1
+ Revision: 461252
- provide a pcitable.d file in backported packages, so that XFdrake sees
  the installed fglrx driver as able to drive the graphics card even if
  ldetect-lst package does not know it
- new version 9.10 aka 8.661
- adapt for upstream changes in xorg targets
- drop rt-compat.patch, affected code has been removed
- rediff make_sh-custom-kernel-dir.patch
- add missing atibuild conditionals into package descriptions

* Sat Sep 19 2009 Anssi Hannula <anssi@mandriva.org> 8.650-1mdv2010.0
+ Revision: 444730
- new version 9.9 aka 8.65
- drop fglrx-reenable-acpi-2.6.29.patch, now unneeded
- replace fgl_glxgears-includes.patch with an include flag

* Wed Aug 19 2009 Anssi Hannula <anssi@mandriva.org> 8.640-1mdv2010.0
+ Revision: 418160
- new version 8.64 aka 9.8
- automatically append 0 to two-decimal upstream version numbers
- drop 2.6.29 and 2.6.30 patches, fixed upstream
- re-enable ACPI notifications on 2.6.29+ (reenable-acpi-2.6.29.patch;
  ATI "fixed" the ACPI headers issue by removing the notification support
  on 2.6.29+; however, our kernel-devel packages contain the necessary
  headers, so reimplement our previous 2.6.29-fixes.patch on top of
  current fglrx)
- fix unexpanded macros in descriptions in atibuild mode

* Wed Aug 05 2009 Anssi Hannula <anssi@mandriva.org> 8.632-2mdv2010.0
+ Revision: 410235
- do not use /proc for probing kernel info to avoid running kernel
  affecting the build (make_sh-no-proc-probe.patch and changes to the
  make command)
- define target uname_a to "none" to prevent make.sh using "uname -a" to
  determine whether target kernel is SMP, instead using the target kernel
  configuration to determine it
- support custom kernel build directories again
  (make_sh-custom-kernel-dir.patch) and use that feature with dkms
- fix failing module load on 2.6.30+ 32-bit SMP kernels due to missing
  symbol flush_tlb_page (2.6.30-smp.patch, reported by Shlomi Fish)

* Tue Jul 28 2009 Anssi Hannula <anssi@mandriva.org> 8.632-1mdv2010.0
+ Revision: 402383
- new version 8.632 aka 9.7
- show advertised version (9.7) in descriptions

* Fri Jul 17 2009 Anssi Hannula <anssi@mandriva.org> 8.620-2mdv2010.0
+ Revision: 396704
- allow redistributing .spec file with MIT license as per AMD request
  (Colin Guthrie, Luiz Fernando Capitulino, and Thomas Backlund agreed)
- clean spec
- fix license tag
- fix missing dot from description
- remove executable permission from headers
- tag language files of fglrx-control-center
- use more wildcards in %%install
- move everything except extensions out from /usr/lib/fglrx/xorg
- fix extraneous ghost files on 2009.1+
- fix backportability
- add copyright doc to fglrx-control-center
- drop compatibility symlinks from /usr/X11R6, it seems the code finally
  supports /usr/lib/dri
- clean up old buildrequires

* Wed Jul 01 2009 Thomas Backlund <tmb@mandriva.org> 8.620-1mdv2010.0
+ Revision: 391139
- add patch7 to better support realtime preempt (Gentoo)
- update patch6 based on Gentoo fixes, and fix it to apply cleanly (2.6.30 buildfix)
- fix patch5 to apply cleanly (2.6.29 buildfix)
- update to Catalyst 9.6 (8.620)

* Tue Jun 30 2009 Thomas Backlund <tmb@mandriva.org> 8.600-3mdv2010.0
+ Revision: 390981
- rediff patch5 to apply cleanly
- fix build with 2.6.30 series kernels

* Mon Apr 13 2009 Anssi Hannula <anssi@mandriva.org> 8.600-2mdv2009.1
+ Revision: 366537
- adapt for dropped alternatives on /usr/bin/Xorg

* Wed Apr 01 2009 Anssi Hannula <anssi@mandriva.org> 8.600-1mdv2009.1
+ Revision: 363380
- add notification of dropped support, shown during upgrade of the package
- new version (8.600)
  o this is the special version AMD provided for Ubuntu Jaunty which
  includes X.org server 1.6 support (the license allows repackaging)
  o this version only supports r600 and newer chipsets (HD2000 onwards)

* Sat Mar 21 2009 Anssi Hannula <anssi@mandriva.org> 8.582-6mdv2009.1
+ Revision: 359879
- remove unneeded hack

* Thu Mar 19 2009 Ander Conselvan de Oliveira <ander@mandriva.com> 8.582-5mdv2009.1
+ Revision: 357792
- ensure the alternatives links are created if its current state is manual

* Mon Mar 16 2009 Ander Conselvan de Oliveira <ander@mandriva.com> 8.582-4mdv2009.1
+ Revision: 356061
- Use alternative X server Xorg 1.5

* Mon Feb 23 2009 Thomas Backlund <tmb@mandriva.org> 8.582-3mdv2009.1
+ Revision: 344323
- fix location of acpica headers so it will build with 2.6.29 series kernels

  + Anssi Hannula <anssi@mandriva.org>
    - use patch fuzz 2 in ati installer mode
    - additional comments in .spec
    - fix build on 2008.1 and earlier

* Sun Feb 22 2009 Anssi Hannula <anssi@mandriva.org> 8.582-2mdv2009.1
+ Revision: 343808
- hack around an error in 2.6.29-fixes.patch that caused build failure
  on earlier kernels

* Sat Feb 21 2009 Anssi Hannula <anssi@mandriva.org> 8.582-1mdv2009.1
+ Revision: 343732
- br libxp-devel
- new version 8.582 aka 9.2

  + Luiz Fernando Capitulino <lcapitulino@mandriva.com>
    - Quick-and-dirty fix to make fglrx compile on 2.6.29-rc

* Mon Feb 02 2009 Anssi Hannula <anssi@mandriva.org> 8.573-1mdv2009.1
+ Revision: 336504
- new version 8.573 aka 9.1

* Sat Dec 20 2008 Anssi Hannula <anssi@mandriva.org> 8.561-1mdv2009.1
+ Revision: 316488
- new version 8.561 aka 8.12
- drop uname_r patch, use the new upstream solution

* Sat Nov 29 2008 Colin Guthrie <cguthrie@mandriva.org> 8.552-2mdv2009.1
+ Revision: 308110
- Hopefully fix xserver 1.5 libglx.so inclusion

  + Anssi Hannula <anssi@mandriva.org>
    - use X.org server 1.5 compatible driver variant on cooker

* Sat Nov 15 2008 Anssi Hannula <anssi@mandriva.org> 8.552-1mdv2009.1
+ Revision: 303545
- new version 8.552 aka 8.11
- drop 2.6.27 support patch, applied upstream

* Sun Nov 02 2008 Anssi Hannula <anssi@mandriva.org> 8.542-2mdv2009.1
+ Revision: 299202
- provide XvMCConfig file so that MPEG/2 acceleration (UVD2) is enabled
  automatically on programs using libXvMCW

* Sun Oct 19 2008 Anssi Hannula <anssi@mandriva.org> 8.542-1mdv2009.1
+ Revision: 295257
- new version 8.542 aka 8.10
- rediff uname_r patch

* Sun Oct 12 2008 Anssi Hannula <anssi@mandriva.org> 8.532-1mdv2009.1
+ Revision: 292944
- 8.532 aka 8.9
  o Driver now includes its own libdri.so; therefore added additional
    manual configuration instructions for 2008.1 and older releases due
    to libdri.so only being handled by alternatives since 2009.0.
    Providing this package in general-purpose pre-2009.0 repositories is
    not recommended.
- rediff 2.6.27 support patch

* Sun Aug 31 2008 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 8.522-3mdv2009.0
+ Revision: 277752
- Really fix fglrx build for Linux 2.6.27

* Thu Aug 28 2008 Luiz Fernando Capitulino <lcapitulino@mandriva.com> 8.522-2mdv2009.0
+ Revision: 277040
- Fix fglrx build for 2.6.27-rc

* Mon Aug 25 2008 Anssi Hannula <anssi@mandriva.org> 8.522-1mdv2009.0
+ Revision: 275718
- new version 8.8 aka 8.522
- drop now unneeded 2.6.26 support patch
- update file list
- add super-user mode menu entry for amdcccle, using more robust
  consolehelper instead of amdxdg-su which upstream created for the
  purpose

* Sun Aug 10 2008 Anssi Hannula <anssi@mandriva.org> 8.512-2mdv2009.0
+ Revision: 270241
- adapt for libdri.so handled by alternatives

* Thu Aug 07 2008 Ander Conselvan de Oliveira <ander@mandriva.com> 8.512-1mdv2009.0
+ Revision: 267038
- Update to version 8.512 (aka Catalyst 8.7)
  Included Gentoo patch to compile against 2.6.26 (Gentoo bug #232609)

* Thu Jul 10 2008 Olivier Blin <oblin@mandriva.com> 8.501-3mdv2009.0
+ Revision: 233211
- conditionally fix build on 2.6.26 (patch from Ubuntu #239967, with some space cleaning)

* Fri Jun 20 2008 Anssi Hannula <anssi@mandriva.org> 8.501-2mdv2009.0
+ Revision: 227323
- restore calls to /sbin/ldconfig, they are there due to alternatives and
  filetriggers do not handle them

* Thu Jun 19 2008 Anssi Hannula <anssi@mandriva.org> 8.501-1mdv2009.0
+ Revision: 226978
- add a custom CLEAN command for dkms to stop it from complaining about
  bad exit status
- adapt to reverted /usr/X11R6 changes on cooker
- 8.501 aka 8.6
- update filelist
- fglrx_gamma: fix underlinking (fix-underlinking.patch)
- use %%ldflags on cooker for fglrx_tools
- import generate-fglrx-spec-from-svn.sh for generating fglrx.spec for
  use within AMD installer archive

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Thu May 29 2008 Anssi Hannula <anssi@mandriva.org> 8.493.1-1mdv2009.0
+ Revision: 212852
- 8.493.1 aka 8.5
- adapt to X11 directory changes of cooker

* Wed May 07 2008 Anssi Hannula <anssi@mandriva.org> 8.476-3mdv2009.0
+ Revision: 202692
- readd 32-bit dri compatibility directories and symlink on x86_64

* Tue May 06 2008 Anssi Hannula <anssi@mandriva.org> 8.476-2mdv2009.0
+ Revision: 201797
- drop /usr/X11R6/ dri symlink from cooker, now handled in
  x11-server-common

* Fri Apr 18 2008 Anssi Hannula <anssi@mandriva.org> 8.476-1mdv2009.0
+ Revision: 195718
- new version (8.476 aka 8.4)
- ensure correct version with ati-packager-helper.sh on non-atibuild
  builds
- suggests acpid for atieventsd
- fix authfile locations in authatieventsd.sh for Mandriva XDM and KDM,
  preventing atieventsd from working properly (partially fixes #33095)
- longer timeout for fglrx driver check in atieventsd initscript
  (see #33095)
- better timeout handling in fglrx check of atieventsd initscript

* Tue Apr 01 2008 Anssi Hannula <anssi@mandriva.org> 8.471-3mdv2008.1
+ Revision: 191501
- add versioned requires on kernel module on 2008.1

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

  + Thierry Vignaud <tv@mandriva.org>
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

  + Thierry Vignaud <tv@mandriva.org>
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

  + Thierry Vignaud <tv@mandriva.org>
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

