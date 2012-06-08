
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

# %amdbuild is used to enable the AMD installer --buildpkg mode.
# The macros version, rel, amd_dir, distsuffix need to be manually defined.
# The macro mdkversion can also be overridden.
%define amdbuild	0
%{?_without_amd: %global amdbuild 0}
%{?_with_amd: %global amdbuild 1}

%if !%{amdbuild}
# NOTE: These version definitions are overridden by ati-packager.sh when
# building with the --buildpkg method of the installer.

# When updating, please add new ids to ldetect-lst (merge2pcitable.pl).

# version in installer filename:
%define oversion	12-4
# Advertised version, for description:
%define mversion	12.4
# driver version from ati-packager-helper.sh:
%define iversion	8.96
# release:
%define rel		2
# rpm version (adds 0 in order to not go backwards if iversion is two-decimal)
%define version		%{iversion}%([ $(echo %iversion | wc -c) -le 5 ] && echo 0)
%else
# Best-effort if AMD has made late changes (in amdbuild mode)
%define _default_patch_fuzz 2
%endif

%define priority	1000
%define release %mkrel %{rel}

# set to 1 for a prerelease driver with an ubuntu tarball as source
%define ubuntu_prerelease 0
# set to 1 for a prerelease driver with an OpenCL tarball as source
%define opencl_prerelease 1

%define driverpkgname	x11-driver-video-fglrx
%define drivername	fglrx
%define xorg_version	pic
# highest supported videodrv abi
%define videodrv_abi	10
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

%if %{amdbuild}
# AMD/ATI cards not listed in main ldetect-lst pcitable are not likely
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

# Other packages should not require any AMD specific proprietary libraries
# (if that is really necessary, we may want to split that specific lib out),
# and this package should not be pulled in when libGL.so.1 is required.
%if %{mdvver} < 201200
%define _provides_exceptions \\.so
%else
%define __noautoprov '\\.so'
%endif

%define qt_requires_exceptions %nil
%if %{bundle_qt}
# do not require Qt if it is bundled
%if %{mdvver} < 201200
%define qt_requires_exceptions \\|libQtCore\\.so\\|libQtGui\\.so
%else
%define qt_requires_exceptions |libQtCore\\.so|libQtGui\\.so
%endif
%endif

# do not require fglrx stuff, they are all included
%if %{mdvver} < 201200
%define common_requires_exceptions libfglrx.\\+\\.so\\|libati.\\+\\.so\\|libOpenCL\\.so%{qt_requires_exceptions}
%else
%define common_requires_exceptions libfglrx.+\\.so|libati.+\\.so|libOpenCL\\.so%{qt_requires_exceptions}
%endif

%ifarch x86_64
# (anssi) Allow installing of 64-bit package if the runtime dependencies
# of 32-bit libraries are not satisfied. If a 32-bit package that requires
# libGL.so.1 is installed, the 32-bit mesa libs are pulled in and that will
# pull the dependencies of 32-bit fglrx libraries in as well.
%if %{mdvver} < 201200
%define _requires_exceptions %common_requires_exceptions\\|lib.*so\\.[^(]\\+\\(([^)]\\+)\\)\\?$
%else
%define __noautoreq '%common_requires_exceptions|lib.*so\\.[^(]+(\\([^)]+\\))?$'
%endif
%else
%if %{mdvver} < 201200
%define _requires_exceptions %common_requires_exceptions
%else
%define __noautoreq '%common_requires_exceptions'
%endif
%endif

# (anssi) Do not require qt for amdnotifyui (used as event notifier, as
# of 04/2010 only for DisplayPort failures). installing
# fglrx-control-center will satisfy the dependency.
# It is not moved to fglrx-control-center as due to its small size it may
# be wanted on e.g. KDE Ones, which can't have the full fglrx-control-center,
# and due to it having nothing to do with fglrx-control-center.
%if %{mdvver} <= 201100
%define _exclude_files_from_autoreq ^%{_sbindir}/amdnotifyui$
%else
%define __noautoreqfiles ^%{_sbindir}/amdnotifyui$
%endif

Summary:	AMD proprietary X.org driver and libraries
Name:		%{name}
Version:	%{version}
Release:	%{release}
%if !%{amdbuild}
%if !%{ubuntu_prerelease}
%if !%{opencl_prerelease}
Source0:	http://www2.ati.com/drivers/linux/amd-driver-installer-%{oversion}-x86.x86_64.run
%else
Source0:	http://download2-developer.amd.com/amd/APPSDK/OpenCL1.2betadriversLinux.tgz
%endif
%else
Source0:        fglrx-installer_%{iversion}.orig.tar.gz
%endif
%endif
Source1:	ati-packager.sh
Source2:	atieventsd.init
%if !%{amdbuild}
# Generates fglrx.spec from Mandriva SVN for use in AMD installer
# archive. Requires kenobi access for fetching names for changelog.
# (for manual use)
Source10:	generate-fglrx-spec-from-svn.sh
Source11:	fglrx.rpmlintrc
Source12:	README_for_maintainers.txt
%endif
Patch3:		fglrx-authfile-locations.patch
Patch9:		fglrx-make_sh-custom-kernel-dir.patch
# do not probe /proc for kernel info as we may be building for a
# different kernel
Patch10:	fglrx-make_sh-no-proc-probe.patch
Patch11:	fglrx-8.951-kernel-3.3.x_fix.diff
License:	Freeware
URL:		http://ati.amd.com/support/driver.html
Group:		System/Kernel and hardware
ExclusiveArch:	%{ix86} x86_64
%if %{mdvver} <= 201010
BuildRoot:	%{_tmppath}/%{name}-root
%endif
%if !%{amdbuild}
BuildRequires:	mesagl-devel
BuildRequires:	libxmu-devel
BuildRequires:	libxaw-devel
BuildRequires:	libxp-devel
BuildRequires:	libxtst-devel
BuildRequires:	imake
# Used by atieventsd:
Suggests:	acpid
BuildRequires:	imagemagick
%endif

%description
Source package of the AMD proprietary driver. Binary packages are
named x11-driver-video-fglrx on Mandriva Linux 2008 and later, and ati on
2007 and earlier.
%if !%{amdbuild}
This package corresponds to AMD Catalyst version %mversion.
%endif

%package -n %{driverpkgname}
Summary:	AMD proprietary X.org driver and libraries
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
%if !%{amdbuild}
%if %{mdvver} >= 201200
Requires(post):	rpm-helper
Requires(preun): rpm-helper
%endif
# Conflict with the next videodrv ABI break.
# The driver may support multiple ABI versions and therefore
# a strict version-specific requirement would not be enough.
### This is problematic as it can cause removal of xserver instead (Anssi 04/2011)
###Conflicts:  xserver-abi(videodrv-%(echo $((%{videodrv_abi} + 1))))
%endif
%endif
Provides:	atieventsd = %{version}-%{release}
Obsoletes:	atieventsd < %{version}-%{release}

%description -n %{driverpkgname}
AMD proprietary X.org graphics driver, related libraries and
configuration tools.

NOTE: You should use XFdrake to configure your AMD card. The
correct packages will be automatically installed and configured.

If you do not want to use XFdrake, see README.manual-setup.

The graphical configuration utility, AMD Catalyst Control Center
Linux Edition, is contained in the package
%{drivername}-control-center.
%if !%{amdbuild}
This package corresponds to AMD Catalyst version %mversion.
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
utility for the AMD proprietary X.org driver.
%if !%{amdbuild}
This package corresponds to AMD Catalyst version %mversion.
%endif

%package -n dkms-%{drivername}
Summary:	AMD proprietary kernel module
Group:		System/Kernel and hardware
Requires:	dkms
Requires(post):	dkms
Requires(preun): dkms
%if %{mdkversion} >= 200800
Obsoletes:	dkms-fglrx-hd2000 < 8.42.3-5
Obsoletes:	dkms-ati < %{version}-%{release}
Provides:	dkms-ati = %{version}-%{release}
%endif

%description -n dkms-%{drivername}
AMD proprietary kernel module. This is to be used with the
%{driverpkgname} package.
%if !%{amdbuild}
This package corresponds to AMD Catalyst version %mversion.
%endif

%package -n %{drivername}-devel
Summary:	AMD proprietary development libraries and headers
Group:		Development/C
Requires:	%{driverpkgname} = %{version}-%{release}
%if %{mdkversion} >= 200800
Obsoletes:	fglrx-hd2000-devel < 8.42.3-5
Obsoletes:	ati-devel < %{version}-%{release}
Provides:	ati-devel = %{version}-%{release}
%endif

%description -n %{drivername}-devel
AMD proprietary development libraries and headers. This package is
not required for normal use.

The main driver package name is %{driverpkgname}.

%package -n %{drivername}-opencl
Summary:	OpenCL libraries for the AMD proprietary driver
Group: 		System/Kernel and hardware
Requires:	kmod(fglrx) = %{version}

%description -n %{drivername}-opencl
OpenCL libraries for the AMD proprietary driver. This package is not
required for normal use, it provides libraries to use AMD cards for High
Performance Computing (HPC).

%prep
%setup -T -c
%if %{amdbuild}
ln -s %{amd_dir}/%{xverdir} %{amd_dir}/arch .
# patches affects common, so we cannot symlink it:
cp -a %{amd_dir}/common .
%else
%if %opencl_prerelease
%setup -q -n fglrx-%iversion
sh *.run --extract .
%else
%if %ubuntu_prerelease
%setup -q -T -D -a 0
ln -s . common
%else
sh %{SOURCE0} --extract .
%endif
%endif
mkdir fglrx_tools
tar -xzf common/usr/src/ati/fglrx_sample_source.tgz -C fglrx_tools
%if %ubuntu_prerelease
[ -d "%xverdir" ] || (echo This driver version does not support your X.org server. Please wait for a new release from AMD. >&2; false)
%else
[ "%iversion" = "$(./ati-packager-helper.sh --version)" ]
%endif
%endif

cd common # ensure patches do not touch outside
%patch3 -p2
%patch9 -p2
%patch10 -p2
%patch11 -p0
cd ..

cat > README.install.urpmi <<EOF
This driver is for ATI Radeon HD 2000 and newer cards.
Reconfiguring is not necessary when upgrading from a previous Mandriva AMD
driver package.

Use XFdrake to configure X to use the correct AMD driver. Any needed
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
This file describes the procedure for the manual installation of this AMD
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
Versions 8.600 and later of AMD Proprietary Graphics driver (fglrx) only
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
features of this version of the proprietary AMD driver on this release
of Mandriva Linux:
Run "readlink -f /etc/alternatives/gl_conf". If it says
"%{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file}", add the following two lines in the Files section
of %{_sysconfdir}/X11/xorg.conf:
      ModulePath "%{ati_extdir}"
      ModulePath "%{xorg_libdir}/modules"
EOF
%endif

%build
%if !%{amdbuild}
# %amdbuild is done with minimal buildrequires
cd fglrx_tools/fgl_glxgears
xmkmf
%make RMAN=/bin/true CC="%__cc %optflags -I../../common/usr/include" EXTRA_LDOPTIONS="%{?ldflags}"
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

# install binaries
install -d -m755					%{buildroot}%{_sbindir}
install -m755 %{archdir}/usr/sbin/*			%{buildroot}%{_sbindir}
install -m755 common/usr/sbin/*				%{buildroot}%{_sbindir}
install -d -m755					%{buildroot}%{_bindir}
install -m755 %{archdir}/usr/bin/*			%{buildroot}%{_bindir}
install -m755 %{archdir}/usr/X11R6/bin/*		%{buildroot}%{_bindir}
install -m755 common/usr/X11R6/bin/*			%{buildroot}%{_bindir}
%if !%{amdbuild}
# install self-built binaries
install -m755 fglrx_tools/fgl_glxgears/fgl_glxgears	%{buildroot}%{_bindir}
%endif
# compatibility symlink
ln -s aticonfig %{buildroot}%{_bindir}/amdconfig

# atieventsd initscript
install -d -m755 %{buildroot}%{_initrddir}
install -m755 %{SOURCE2} %{buildroot}%{_initrddir}/atieventsd

# amdcccle data files
install -d -m755 %{buildroot}%{_datadir}/ati/amdcccle
rm -f amdcccle.langs
for fullname in common/usr/share/ati/amdcccle/*.qm; do
	file=$(basename $fullname)
	lang=${file#*_}
	lang=${lang%%.qm}
%if !%{bundle_qt}
	# qt localization not necessary with non-bundled qt
	[ "$file" = "${file#qt}" ] || continue
%endif
	install -m644 $fullname %{buildroot}%{_datadir}/ati/amdcccle
	echo "%%lang($lang) %{_datadir}/ati/amdcccle/$file" >> amdcccle.langs
done

# amdcccle super-user mode
install -d -m755 %{buildroot}%{_sysconfdir}/security/console.apps
install -d -m755 %{buildroot}%{_sysconfdir}/pam.d
install -m644 common/etc/security/console.apps/* %{buildroot}%{_sysconfdir}/security/console.apps
ln -s su %{buildroot}%{_sysconfdir}/pam.d/amdcccle-su

# man pages
install -d -m755 %{buildroot}%{_mandir}/man1 %{buildroot}%{_mandir}/man8
install -m644 common/usr/share/man/man8/* %{buildroot}%{_mandir}/man8

# menu entry
install -d -m755 %{buildroot}%{_datadir}/applications
install -m644 common/usr/share/applications/* %{buildroot}%{_datadir}/applications
sed -i 's,^Icon=.*$,Icon=%{drivername}-amdcccle,' %{buildroot}%{_datadir}/applications/*.desktop
# control center doesn't really use GNOME/KDE libraries:
sed -i 's,GNOME;KDE;,,' %{buildroot}%{_datadir}/applications/*.desktop

# icons
install -d -m755 %{buildroot}%{_miconsdir} %{buildroot}%{_iconsdir} %{buildroot}%{_liconsdir}
%if !%{amdbuild}
convert common/usr/share/icons/ccc_large.xpm -resize 16x16 %{buildroot}%{_miconsdir}/%{drivername}-amdcccle.png
convert common/usr/share/icons/ccc_large.xpm -resize 32x32 %{buildroot}%{_iconsdir}/%{drivername}-amdcccle.png
convert common/usr/share/icons/ccc_large.xpm -resize 48x48 %{buildroot}%{_liconsdir}/%{drivername}-amdcccle.png
%else
install -m644 common/usr/share/icons/ccc_large.xpm %{buildroot}%{_iconsdir}/%{drivername}-amdcccle.xpm
%endif

# install libraries
install -d -m755					%{buildroot}%{_libdir}/%{drivername}
install -m755 %{archdir}/usr/X11R6/%{_lib}/*.*		%{buildroot}%{_libdir}/%{drivername}
install -m755 %{archdir}/usr/X11R6/%{_lib}/fglrx/*	%{buildroot}%{_libdir}/%{drivername}
install -m755 %{archdir}/usr/%{_lib}/*.*		%{buildroot}%{_libdir}/%{drivername}
mv %{buildroot}%{_libdir}/%{drivername}/{fglrx-,}libGL.so.1.2
chmod 0644						%{buildroot}%{_libdir}/%{drivername}/*.a
/sbin/ldconfig -n					%{buildroot}%{_libdir}/%{drivername}
# create devel symlinks
for file in %{buildroot}%{_libdir}/%{drivername}/*.so.*.*; do
	ln -s $(basename $file) ${file%%.so*}.so;
done
%ifarch x86_64
install -d -m755					%{buildroot}%{_prefix}/lib/%{drivername}
install -m755 arch/x86/usr/X11R6/lib/fglrx/*		%{buildroot}%{_prefix}/lib/%{drivername}
install -m755 arch/x86/usr/lib/*.*			%{buildroot}%{_prefix}/lib/%{drivername}
mv %{buildroot}%{_prefix}/lib/%{drivername}/{fglrx-,}libGL.so.1.2
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

# install X.org files
install -d -m755						%{buildroot}%{xorg_libdir}/modules/drivers
install -m755 %{xverdir}/usr/X11R6/%{_lib}/modules/drivers/*.so* %{buildroot}%{xorg_libdir}/modules/drivers
install -d -m755						%{buildroot}%{xorg_libdir}/modules/linux
install -m755 %{xverdir}/usr/X11R6/%{_lib}/modules/linux/*.so*	%{buildroot}%{xorg_libdir}/modules/linux
install -m644 %{xverdir}/usr/X11R6/%{_lib}/modules/*.*o		%{buildroot}%{xorg_libdir}/modules
install -d -m755						%{buildroot}%{ati_extdir}
install -m755 %{xverdir}/usr/X11R6/%{_lib}/modules/extensions/fglrx/*.so* %{buildroot}%{ati_extdir}
mv %{buildroot}%{ati_extdir}/{fglrx-,}libglx.so

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

install -d -m755			%{buildroot}%{_sysconfdir}/%{drivername}

%if %{mdkversion} < 201100
# modprobe.conf
install -d -m755			%{buildroot}%{_sysconfdir}/modprobe.d
touch					%{buildroot}%{_sysconfdir}/modprobe.d/display-driver.conf
echo "blacklist radeon"			> %{buildroot}%{_sysconfdir}/%{drivername}/modprobe.conf

# modprobe.preload.d
install -d -m755			%{buildroot}%{_sysconfdir}/modprobe.preload.d
touch					%{buildroot}%{_sysconfdir}/modprobe.preload.d/display-driver
echo "fglrx"				> %{buildroot}%{_sysconfdir}/%{drivername}/modprobe.preload
%endif

# XvMCConfig
echo "libAMDXvBA.so.1" > %{buildroot}%{_sysconfdir}/%{drivername}/XvMCConfig

# CUDA icd
install -d -m755				%{buildroot}%{_sysconfdir}/OpenCL/vendors
install -m644 %{archdir}/etc/OpenCL/vendors/*	%{buildroot}%{_sysconfdir}/OpenCL/vendors
%ifarch x86_64
install -m644 arch/x86/etc/OpenCL/vendors/*	%{buildroot}%{_sysconfdir}/OpenCL/vendors
%endif

# PowerXpress intel - use Mesa libGL but still keep AMD specific libs in search path
echo "%{_libdir}/mesa" > %{buildroot}%{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf
%ifarch x86_64
echo "%{_prefix}/lib/mesa" >> %{buildroot}%{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf
%endif
cat %{buildroot}%{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file} >> %{buildroot}%{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf

# install ldetect-lst pcitable files for backports
sed -ne 's|^\s*FGL_ASIC_ID(\(0x....\)).*|\1|gp' common/lib/modules/fglrx/build_mod/fglrxko_pci_ids.h | tr '[:upper:]' '[:lower:]' | sort -u | sed 's,^.*$,0x1002\t\0\t"%{ldetect_cards_name}",' > pcitable.fglrx.lst
[ $(stat -c%s pcitable.fglrx.lst) -gt 500 ]
%if "%{ldetect_cards_name}" != ""
install -d -m755 %{buildroot}%{_datadir}/ldetect-lst/pcitable.d
gzip -c pcitable.fglrx.lst > %{buildroot}%{_datadir}/ldetect-lst/pcitable.d/40%{drivername}.lst.gz
%endif

install -d -m755 %{buildroot}%{_datadir}/ati
cat > %{buildroot}%{_datadir}/ati/amd-uninstall.sh <<EOF
#!/bin/bash
# parameters as per AMD: [--force | --dry-run]
dryrun=
while [ -n "\$*" ]; do
	case "\$1" in
	--dryrun)	dryrun="--test" ;;
	--force)	;;
	--preserve)	;;
	--quick)	;;
	--getUninstallVersion) exit 2 ;;
	*)		echo "Unknown option for \$0." >&2 ;;
	esac
	shift
done

# AMD documentation suggests doing rpm -V and use --force to override it,
# but it doesn't make sense with the update-alternatives setup, so we just
# check package presence.
pkgs=
rpm -q --quiet %{driverpkgname}             && pkgs="\$pkgs %{driverpkgname}"
rpm -q --quiet dkms-%{drivername}           && pkgs="\$pkgs dkms-%{drivername}"
rpm -q --quiet %{drivername}-control-center && pkgs="\$pkgs %{drivername}-control-center"
rpm -q --quiet %{drivername}-devel          && pkgs="\$pkgs %{drivername}-devel"
[ -n "\$pkgs" ] || { echo "The AMD proprietary driver is not installed." >&2; exit 1; }
urpme --auto \$dryrun \$pkgs || { echo "Failed to uninstall the AMD proprietary driver." >&2; exit 1; }
[ -n "\$dryrun" ] || echo "The AMD proprietary driver has been uninstalled."
EOF
chmod 0755 %{buildroot}%{_datadir}/ati/amd-uninstall.sh

# PowerXpress (switchable graphics)
# - path hardcoded into driver
install -d -m755 %{buildroot}%{_libdir}/fglrx
cat > %{buildroot}%{_libdir}/fglrx/switchlibGL <<EOF
#!/bin/sh

amd_target="%{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file}"
intel_target="%{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf"

case \$1 in
amd)
	update-alternatives --set gl_conf "\$amd_target" >/dev/null
	ldconfig -X
	;;
intel)
	update-alternatives --set gl_conf "\$intel_target" >/dev/null
	ldconfig -X
	;;
query)
	case \$(readlink -f "%{_sysconfdir}/ld.so.conf.d/GL.conf") in
	\$amd_target)
		echo "amd"
		;;
	\$intel_target)
		echo "intel"
		;;
	*)
		echo "unknown"
		;;
	esac
	;;
esac
EOF
chmod 0755 %{buildroot}%{_libdir}/fglrx/switchlibGL

# It is not feasible to configure these separately with the alternatives
# system, so use the same script for both.
# Note: using a symlink here fails as the driver checks go+w without
# dereferencing the symlink.
cp -a %{buildroot}%{_libdir}/fglrx/switchlibGL %{buildroot}%{_libdir}/fglrx/switchlibglx

#%if %{mdvver} >= 201200
## Strip files that spec-helper misses
#%__strip --strip-unneeded %{buildroot}%{_libdir}/xorg/modules/amdxmm.so
#%endif

# Fix file permissions
find %{buildroot} -name '*.h' -exec %__chmod 0644 {} \;
find %{buildroot} -name '*.c' -exec %__chmod 0644 {} \;

touch %{buildroot}%{_sysconfdir}/ati/atiapfuser.blb

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
%if %{mdkversion} < 201100
	--slave %{_sysconfdir}/modprobe.d/display-driver.conf display-driver.conf %{_sysconfdir}/%{drivername}/modprobe.conf \
	--slave %{_sysconfdir}/modprobe.preload.d/display-driver display-driver.preload %{_sysconfdir}/%{drivername}/modprobe.preload \
%endif
%if %{mdkversion} >= 200910
	--slave %{xorg_extra_modules} xorg_extra_modules %{ati_extdir} \
%else
%if %{mdkversion} >= 200900
	--slave %{_libdir}/xorg/modules/extensions/libdri.so libdri.so %{_libdir}/xorg/modules/extensions/standard/libdri.so \
%endif
%if %{mdkversion} >= 200800
	--slave %{_libdir}/xorg/modules/extensions/libglx.so libglx %{ati_extdir}/libglx.so
%endif
%endif
# Alternative for PowerXpress intel (switchable graphics)
# This is a separate alternative so that this situation can be differentiated
# from standard intel configuration by tools (e.g. so that radeon driver won't
# be loaded despite fglrx not being configured anymore).
%{_sbindir}/update-alternatives \
	--install %{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf 50 \
%if %{mdkversion} < 201100
	--slave %{_sysconfdir}/modprobe.d/display-driver.conf display-driver.conf %{_sysconfdir}/%{drivername}/modprobe.conf \
	--slave %{_sysconfdir}/modprobe.preload.d/display-driver display-driver.preload %{_sysconfdir}/%{drivername}/modprobe.preload \
%endif
%if %{mdkversion} >= 200800 && %{mdkversion} <= 200900
	--slave %{_libdir}/xorg/modules/extensions/libglx.so libglx %{_libdir}/xorg/modules/extensions/standard/libglx.so \
%if %{mdkversion} == 200900
	--slave %{_libdir}/xorg/modules/extensions/libdri.so libdri.so %{_libdir}/xorg/modules/extensions/standard/libdri.so \
%endif
%endif
#
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
# Call /sbin/ldconfig explicitely due to alternatives
/sbin/ldconfig -X
%_post_service atieventsd
%if "%{ldetect_cards_name}" != ""
[ -x %{_sbindir}/update-ldetect-lst ] && %{_sbindir}/update-ldetect-lst || :
%endif

# Clear driver version numbers from amdpcsdb as suggested by AMD.
# (fixes version display in amdcccle after upgrade)
amdconfig --del-pcs-key=LDC,ReleaseVersion &>/dev/null || :
amdconfig --del-pcs-key=LDC,Catalyst_Version &>/dev/null || :

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
if [ ! -f %{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf ]; then
  %{_sbindir}/update-alternatives --remove gl_conf %{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf
fi
# Call /sbin/ldconfig explicitely due to alternatives
/sbin/ldconfig -X
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

%post -n %{drivername}-opencl
# explicit /sbin/ldconfig due to a non-standard library directory
/sbin/ldconfig -X

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
%defattr(0644,root,root)
%doc README.install.urpmi README.manual-setup
%doc README.8.600.upgrade.urpmi
# the documentation files are grossly out of date; the configuration options
# described in configure.html seem to be used by the driver, though, so it is
# packaged, while the other html files are not:
%doc common/usr/share/doc/fglrx/configure.html
%doc common/usr/share/doc/fglrx/LICENSE.TXT
%if %{mdkversion} <= 200810
%doc README.8.532.upgrade.urpmi
%endif

%defattr(-,root,root)

%if "%{ldetect_cards_name}" != ""
%{_datadir}/ldetect-lst/pcitable.d/40%{drivername}.lst.gz
%endif

%ghost %{_sysconfdir}/ld.so.conf.d/GL.conf
%dir %{_sysconfdir}/ld.so.conf.d/GL
%{_sysconfdir}/ld.so.conf.d/GL/ati.conf

%if %{mdkversion} < 201100
%ghost %{_sysconfdir}/modprobe.d/display-driver.conf
%ghost %{_sysconfdir}/modprobe.preload.d/display-driver
%endif
%dir %{_sysconfdir}/%{drivername}
%{_sysconfdir}/%{drivername}/XvMCConfig
%{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf
%if %{mdkversion} < 201100
%{_sysconfdir}/%{drivername}/modprobe.conf
%{_sysconfdir}/%{drivername}/modprobe.preload
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

%{_bindir}/amdconfig
%{_bindir}/amdupdaterandrconfig
%{_bindir}/amdxdg-su
%{_bindir}/aticonfig
%{_bindir}/atiodcli
%{_bindir}/atiode
%{_bindir}/fgl_glxgears
%{_bindir}/fglrxinfo

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

%{_libdir}/%{drivername}/libfglrx_dm.so.1*
%{_libdir}/%{drivername}/libatiadlxx.so
%{_libdir}/%{drivername}/libAMDXvBA.cap
%{_libdir}/%{drivername}/libAMDXvBA.so.1*
%{_libdir}/%{drivername}/libXvBAW.so.1*

# PowerXpress
%{_libdir}/fglrx/switchlibGL
%{_libdir}/fglrx/switchlibglx

%dir %{_datadir}/ati
%{_datadir}/ati/amd-uninstall.sh

%config(noreplace) %{_sysconfdir}/ati/atiapfuser.blb
%config(noreplace) %{_sysconfdir}/ati/atiapfxx.blb

%{_mandir}/man8/atieventsd.8*

%files -n %{drivername}-control-center -f amdcccle.langs
%defattr(-,root,root)
%attr(0644,root,root) %doc common/usr/share/doc/amdcccle/*
%{_sysconfdir}/security/console.apps/amdcccle-su
%{_sysconfdir}/pam.d/amdcccle-su
%{_bindir}/amdcccle
%dir %{_datadir}/ati
%dir %{_datadir}/ati/amdcccle
%if %{amdbuild}
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
%{_libdir}/%{drivername}/libfglrx_dm.a
%{_libdir}/%{drivername}/libfglrx_dm.so
%{_libdir}/%{drivername}/libAMDXvBA.so
%{_libdir}/%{drivername}/libXvBAW.so
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

%files -n %{drivername}-opencl
%defattr(-,root,root)
%dir %{_sysconfdir}/OpenCL
%dir %{_sysconfdir}/OpenCL/vendors
%{_sysconfdir}/OpenCL/vendors/amdocl*.icd
%{_bindir}/clinfo
%{_libdir}/%{drivername}/libamdocl*.so
%{_libdir}/%{drivername}/libOpenCL.so.1
%{_libdir}/%{drivername}/libSlotMaximizer*.so
%ifarch x86_64
%{_prefix}/lib/%{drivername}/libamdocl*.so
%{_prefix}/lib/%{drivername}/libOpenCL.so.1
%{_prefix}/lib/%{drivername}/libSlotMaximizer*.so
%endif

%files -n dkms-%{drivername}
%defattr(0644,root,root)
%{_usrsrc}/%{drivername}-%{version}-%{release}/*.c
%{_usrsrc}/%{drivername}-%{version}-%{release}/*.h
%{_usrsrc}/%{drivername}-%{version}-%{release}/2.6.x/
%{_usrsrc}/%{drivername}-%{version}-%{release}/dkms.conf
%attr(0755,root,root) %{_usrsrc}/%{drivername}-%{version}-%{release}/libfglrx_ip.a
%attr(0755,root,root) %{_usrsrc}/%{drivername}-%{version}-%{release}/make.sh
