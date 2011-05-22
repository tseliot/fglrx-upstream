
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
%define oversion	11-3
# Advertised version, for description:
%define mversion	11.3
# driver version from ati-packager-helper.sh:
%define iversion	8.840
# release:
%define rel		3
# rpm version (adds 0 in order to not go backwards if iversion is two-decimal)
%define version		%{iversion}%([ $(echo %iversion | wc -c) -le 5 ] && echo 0)
%else
# Best-effort if ATI has made late changes (in atibuild mode)
%define _default_patch_fuzz 2
%endif

%define priority	1000
%define release %mkrel %{rel}

# set to 1 for a prerelease driver with an ubuntu tarball as source
%define ubuntu_prerelease 1

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

%if %{atibuild}
# ATI cards not listed in main ldetect-lst pcitable are not likely
# to be supported by radeon which is from the same time period.
# radeonhd has greater chance of working due to it not using ID lists.
# (main pcitable entries override our entries)
%define ldetect_cards_name	ATI Radeon HD 2000 and later (vesa/fglrx)
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
named x11-driver-video-fglrx on %{_vendor}.
%if !%{atibuild}
This package corresponds to ATI Catalyst version %mversion.
%endif

%package -n %{driverpkgname}
Summary:	ATI proprietary X.org driver and libraries
Group:		System/Kernel and hardware
Requires(post):	update-alternatives >= 1.9.0
Requires(postun): update-alternatives
Obsoletes:	ati_igp
Suggests:	%{drivername}-control-center = %{version}
Obsoletes:	ati < %{version}-%{release}
Provides:	ati = %{version}-%{release}
Requires:	kmod(fglrx) = %{version}
Requires:	x11-server-common >= 1.9
%if !%{atibuild}
# Conflict with the next videodrv ABI break.
# The driver may support multiple ABI versions and therefore
# a strict version-specific requirement would not be enough.
# (ahmad) since X Server 1.10 ABI is now 10 (upstream jumped from 8 to 10)
# make it +2 for now
### This is problematic as it can cause removal of xserver instead (Anssi 04/2011)
### Conflicts:	xserver-abi(videodrv-%(echo $((%{videodrv_abi} + 1))))
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
Obsoletes:	ati-control-center < %{version}-%{release}
Provides:	ati-control-center = %{version}-%{release}
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
Obsoletes:	dkms-ati < %{version}-%{release}
Provides:	dkms-ati = %{version}-%{release}
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
Obsoletes:	ati-devel < %{version}-%{release}
Provides:	ati-devel = %{version}-%{release}

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
Reconfiguring is not necessary when upgrading from a previous %{_vendor} ATI
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
  o Remove any 'ModulePath' lines from the Files section
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
   %{_vendor} Control Center.
2. Go to the Graphics Card list.
3. Select your card (it is usually already autoselected).
4. Answer any questions asked and then quit.
EOF

%build
%if !%{atibuild}
# %atibuild is done with minimal buildrequires
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
install -m755 %{archdir}/usr/X11R6/bin/*		%{buildroot}%{_bindir}
install -m755 common/usr/X11R6/bin/*			%{buildroot}%{_bindir}
%if !%{atibuild}
# install self-built binaries
install -m755 fglrx_tools/fgl_glxgears/fgl_glxgears	%{buildroot}%{_bindir}
%endif

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
install -m755 %{archdir}/usr/X11R6/%{_lib}/fglrx/*	%{buildroot}%{_libdir}/%{drivername}
install -m755 %{archdir}/usr/%{_lib}/*.so*		%{buildroot}%{_libdir}/%{drivername}
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
install -m755 arch/x86/usr/lib/*.so*			%{buildroot}%{_prefix}/lib/%{drivername}
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

# XvMCConfig
install -d -m755 %{buildroot}%{_sysconfdir}/%{drivername}
echo "libAMDXvBA.so.1" > %{buildroot}%{_sysconfdir}/%{drivername}/XvMCConfig

# PowerXpress intel
ln -s %{_sysconfdir}/ld.so.conf.d/GL/standard.conf %{buildroot}%{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf

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
ln -s switchlibGL %{buildroot}%{_libdir}/fglrx/switchlibglx

%pre -n %{driverpkgname}
# Handle alternatives-era /etc/ati directory
# It may confuse rpm due to it containing %config files
if [ -L %{_sysconfdir}/ati ]; then
	rm %{_sysconfdir}/ati
fi

%post -n %{driverpkgname}
# Migrate from pre-alternatives files
if [ ! -L %{_datadir}/applications/mandriva-amdcccle.desktop -a -e %{_datadir}/applications/mandriva-amdcccle.desktop ]; then
	rm -f %{_datadir}/applications/mandriva-amdcccle.desktop
fi

%{_sbindir}/update-alternatives \
	--install %{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{ld_so_conf_file} %{priority} \
	--slave %{_sysconfdir}/X11/XvMCConfig xvmcconfig %{_sysconfdir}/%{drivername}/XvMCConfig \
	--slave %{_libdir}/libAMDXvBA.cap %{_lib}AMDXvBA_cap %{_libdir}/%{drivername}/libAMDXvBA.cap \
%ifarch x86_64
	--slave %{_prefix}/lib/libAMDXvBA.cap libAMDXvBA_cap %{_libdir}/%{drivername}/libAMDXvBA.cap \
%endif
	--slave %{xorg_extra_modules} xorg_extra_modules %{ati_extdir}

# Alternative for PowerXpress intel (switchable graphics)
# This is a separate alternative so that this situation can be differentiated
# from standard intel configuration by tools (e.g. so that radeon driver won't
# be loaded despite fglrx not being configured anymore).
%{_sbindir}/update-alternatives \
	--install %{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf 50

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

# empty line so that /sbin/ldconfig is not passed to update-alternatives

# Call /sbin/ldconfig explicitely due to alternatives
/sbin/ldconfig -X
%_post_service atieventsd
%if "%{ldetect_cards_name}" != ""
[ -x %{_sbindir}/update-ldetect-lst ] && %{_sbindir}/update-ldetect-lst || :
%endif

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
/sbin/ldconfig
%if "%{ldetect_cards_name}" != ""
[ -x %{_sbindir}/update-ldetect-lst ] && %{_sbindir}/update-ldetect-lst || :
%endif

%pre -n %{drivername}-control-center
# Handle alternatives-era directory,
# it may confuse rpm.
if [ -L %{_datadir}/ati ]; then
	rm %{_datadir}/ati
fi

%post -n %{drivername}-control-center
[ -d %{_datadir}/fglrx ] && rm -r %{_datadir}/fglrx
[ -d %{_datadir}/fglrx-hd2000 ] && rm -r %{_datadir}/fglrx-hd2000
true

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

%if "%{ldetect_cards_name}" != ""
%{_datadir}/ldetect-lst/pcitable.d/40%{drivername}.lst.gz
%endif

%ghost %{_sysconfdir}/ld.so.conf.d/GL.conf
%dir %{_sysconfdir}/ld.so.conf.d/GL
%{_sysconfdir}/ld.so.conf.d/GL/ati.conf

%dir %{_sysconfdir}/%{drivername}
%{_sysconfdir}/%{drivername}/XvMCConfig
%{_sysconfdir}/%{drivername}/pxpress-free.ld.so.conf

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

%{xorg_libdir}/modules/drivers/fglrx_drv.so
%{xorg_libdir}/modules/linux/libfglrxdrm.so
%{xorg_libdir}/modules/amdxmm.*o
%{xorg_libdir}/modules/glesx.*o

%dir %{ati_extdir}
%{ati_extdir}/libglx.so

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

%files -n dkms-%{drivername}
%defattr(-,root,root)
%{_usrsrc}/%{drivername}-%{version}-%{release}

%changelog
* %(LC_ALL=C date "+%a %b %d %Y") %{packager} %{version}-%{release}
- automatic package build by the ATI installer

* Sun Apr 17 2011 anssi <anssi> 8.840-3.mga1
+ Revision: 87413
- disable conflicts on videodrv ABI, as it may cause X server to be
  uninstalled instead
- remove references to removed xgamma
- remove now unneeded modprobe.preload.d and modprobe.d entries
- add simple uninstaller script used by the ati binaries

* Sun Apr 17 2011 anssi <anssi> 8.840-2.mga1
+ Revision: 87386
- remove extra alternatives slave mistakenly left after mga cleanup

* Sun Apr 03 2011 ahmad <ahmad> 8.840-1.mga1
+ Revision: 79916
- update to 8.840 (using an Ubuntu orig.gz)
- drop kernel-2.6.38 patch, not needed

* Sat Apr 02 2011 ahmad <ahmad> 8.831.2-2.mga1
+ Revision: 79802
- add patch to fix building the module with kernel-2.6.38 series

* Sat Apr 02 2011 ahmad <ahmad> 8.831.2-1.mga1
+ Revision: 79744
- update to 8.831.2 aka 11.3
- fglrx_gamma isn't available, so comment out its bits in the spec
- bump videodrv_abi to 10
- change the xserver-abi conflicts back to '+ 1'

* Tue Mar 08 2011 ahmad <ahmad> 8.821-3.mga1
+ Revision: 66360
- since X Server 1.10 ABI is now 10 (upstream jumped from 8 to 10), adapt the
  x11-server ABI conflicts to that case

* Thu Feb 24 2011 ahmad <ahmad> 8.821-2.mga1
+ Revision: 58195
- drop old/unneded scriptlest, obsoletes and conflicts
- imported package fglrx

