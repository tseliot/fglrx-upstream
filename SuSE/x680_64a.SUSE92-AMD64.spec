#############################################################################
# spec file header                                                          #
#############################################################################

Name: fglrx64_6_8_0_SUSE92
Summary: %ATI_DRIVER_SUMMARY
Version: %ATI_DRIVER_VERSION
Release: %ATI_DRIVER_RELEASE
License: %ATI_DRIVER_VENDOR
URL: %ATI_DRIVER_URL
Group: Servers
PreReq: %insserv_prereq %fillup_prereq
Provides: fglrx km_fglrx
Obsoletes: fglrx km_fglrx
ExclusiveArch: %ix86 x86_64

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
export RPM_BUILD_ROOT=%ATI_DRIVER_BUILD_ROOT
tmpdir=$(mktemp -d /tmp/fglrx.XXXXXX)
mkdir $tmpdir/fglrx
mv $RPM_BUILD_ROOT/* $tmpdir/fglrx
export RPM_SOURCE_DIR=$(mktemp -d /tmp/fglrx.XXXXXX)
mv $tmpdir/fglrx/suse/* $RPM_SOURCE_DIR 
#
mkdir -p $RPM_BUILD_ROOT/usr/bin \
         $RPM_BUILD_ROOT%{X11_INCLUDE_DIR}/extensions \
%ifarch x86_64
         $RPM_BUILD_ROOT%{DRI_DRIVERS32_DIR} \
%endif
         $RPM_BUILD_ROOT%{MODULES_DIR}/{linux,drivers,extensions} \
         $RPM_BUILD_ROOT%{DRI_DRIVERS_DIR} \
         $RPM_BUILD_ROOT/usr/include/GL \
         $RPM_BUILD_ROOT/usr/X11R6/%{_lib} \
%ifarch x86_64
         $RPM_BUILD_ROOT/usr/X11R6/lib \
%endif
         $RPM_BUILD_ROOT/usr/%{_lib}/fglrx/lib \
         $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx \
         $RPM_BUILD_ROOT/usr/share/pixmaps \
         $RPM_BUILD_ROOT/usr/sbin \
         $RPM_BUILD_ROOT/usr/share/man/man8 \
         $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx \
         $RPM_BUILD_ROOT/etc/ati
pushd $tmpdir/fglrx
  rm -f lib/modules/fglrx/build_mod/make.sh
  mv lib/modules/fglrx/build_mod/* $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx
  chmod 644 $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx/*
  test -e $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx/firegl_agpgart && \
    chmod 755 $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx/firegl_agpgart
  chmod 755 $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx/2.6.x
  chmod 644 $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx/2.6.x/Makefile
  ln -s 2.6.x/Makefile $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx/Makefile
  rm -rf lib
  mv usr/share/doc/fglrx/{articles,user-manual,release-notes} \
    $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx
  chmod 755 $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx/{articles,user-manual}
  if [ -d etc/ati ]; then
    install -m 644 etc/ati/* $RPM_BUILD_ROOT/etc/ati
    rm -rf etc/ati
  fi
  ls etc/* && install -m 644 etc/* $RPM_BUILD_ROOT/etc/ati
  rm -rf etc/
%if %suse_version > 1000
  if [ -f amdcccle ]; then
    ldd amdcccle | grep -q libexpat.so.0 || \
      cp -r usr/share/ati $RPM_BUILD_ROOT/usr/share
  fi
%else
  cp -r usr/share/ati $RPM_BUILD_ROOT/usr/share
%endif
  rm -rf usr/share/ati
%ifarch x86_64
  test -f usr/X11R6/lib/modules/dri/fglrx_dri.so && \
  ( mv usr/X11R6/lib/modules/dri/fglrx_dri.so .
    install -m 444 fglrx_dri.so          $RPM_BUILD_ROOT%{DRI_DRIVERS32_DIR}
    rm fglrx_dri.so 
  )
  mv usr/X11R6/lib/libGL.so.1.2 .
  install -m 755 libGL.so.1.2            $RPM_BUILD_ROOT/usr/X11R6/lib
  ln -snf libGL.so.1.2                   $RPM_BUILD_ROOT/usr/X11R6/lib/libGL.so.1 
  ln -snf libGL.so.1                     $RPM_BUILD_ROOT/usr/X11R6/lib/libGL.so
  rm libGL.so.1.2
  mv usr/X11R6/lib/libfglrx*.a .
  install -m 644 libfglrx*.a             $RPM_BUILD_ROOT/usr/lib
  rm libfglrx*.a 
  mv usr/X11R6/lib/libfglrx*.so* .
  install -m 755 libfglrx*.so*           $RPM_BUILD_ROOT/usr/lib
  rm libfglrx*.so*
%endif
  for i in `find . -type f`; do mv --backup $i .; done
  # make sure we don't overwrite something
  ls *~ && exit 1
  install -m 644 ATI_LICENSE.TXT         $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx
  test -f LICENSE.xmlconfig && \
    install -m 644 LICENSE.xmlconfig     $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx
  install -m 644 *.html                  $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx
  install -m 644 $RPM_SOURCE_DIR/README.SuSE $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx
  install -m 644 $RPM_SOURCE_DIR/sax2-profile $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx
  install -m 755 fgl_glxgears            $RPM_BUILD_ROOT/usr/bin
  test -f fglrx_dri.so && \
    install -m 444 fglrx_dri.so          $RPM_BUILD_ROOT%{DRI_DRIVERS_DIR}
  install -m 444 fglrx_drv.*             $RPM_BUILD_ROOT%{MODULES_DIR}/drivers 
  install -m 644 fglrx_gamma.h           $RPM_BUILD_ROOT/%{X11_INCLUDE_DIR}/extensions
  install -m 644 fglrx_sample_source.tgz $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx
  install -m 755 fglrx_xgamma            $RPM_BUILD_ROOT/usr/bin
  install -m 755 fglrxinfo               $RPM_BUILD_ROOT/usr/bin
%if %suse_version > 1000
  if [ -f amdcccle ]; then
    ldd amdcccle | grep -q libexpat.so.0 || \
      install -m 755 amdcccle  $RPM_BUILD_ROOT/usr/bin
  fi
%else
  install -m 755 amdcccle      $RPM_BUILD_ROOT/usr/bin
%endif
  install -m 644 glxATI.h                $RPM_BUILD_ROOT/usr/include/GL
  install -m 755 libGL.so.1.2            $RPM_BUILD_ROOT/usr/X11R6/%{_lib}
  ln -snf libGL.so.1.2                   $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libGL.so.1
  ln -snf libGL.so.1                     $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libGL.so
  install -m 644 libfglrx_gamma.a        $RPM_BUILD_ROOT/usr/X11R6/%{_lib}
  install -m 755 libfglrx_gamma.so*      $RPM_BUILD_ROOT/usr/X11R6/%{_lib}
  ln -snf libfglrx_gamma.so.1.0          $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libfglrx_gamma.so.1
  install -m 444 libfglrxdrm.*           $RPM_BUILD_ROOT%{MODULES_DIR}/linux
  install -m 755 aticonfig               $RPM_BUILD_ROOT/usr/bin
  install -m 644 libfglrx_pp.a           $RPM_BUILD_ROOT/usr/X11R6/%{_lib}
  install -m 755 libfglrx_pp.so*         $RPM_BUILD_ROOT/usr/X11R6/%{_lib}
  ln -snf libfglrx_pp.so.1.0             $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libfglrx_pp.so.1
  install -m 644 glATI.h                 $RPM_BUILD_ROOT/usr/include/GL
  test -f atigetsysteminfo.sh && \
  install -m 755 atigetsysteminfo.sh     $RPM_BUILD_ROOT/usr/sbin
  test -f atieventsd && \
  install -m 755 atieventsd              $RPM_BUILD_ROOT/usr/sbin
  test -f atieventsd.8 && \
    gzip atieventsd.8
  test -f atieventsd.8.gz && \
  install -m 644 atieventsd.8.gz         $RPM_BUILD_ROOT/usr/share/man/man8
  test -f $RPM_BUILD_ROOT/etc/ati/authatieventsd.sh || \
    install -m 755 $RPM_SOURCE_DIR/authatieventsd.sh $RPM_BUILD_ROOT/etc/ati
  chmod 755 $RPM_BUILD_ROOT/etc/ati/authatieventsd.sh
  test -f libfglrx_tvout.a && \
    install -m 644 libfglrx_tvout.a      $RPM_BUILD_ROOT/usr/X11R6/%{_lib}
  test -f libfglrx_tvout.so.1.0 && \
    install -m 644 libfglrx_tvout.so.1.0 $RPM_BUILD_ROOT/usr/X11R6/%{_lib}
  test -f esut.a && \
    install -m 444 esut.a                $RPM_BUILD_ROOT%{MODULES_DIR}
  test -f glesx.so && \
    install -m 444 glesx.so              $RPM_BUILD_ROOT%{MODULES_DIR}
popd
pushd $RPM_BUILD_ROOT/usr/src/kernel-modules/fglrx
  # add kernel patches here
  rm -f *.orig
popd
install -m 755 $RPM_SOURCE_DIR/fglrx-kernel-build.sh \
  $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
install -m 644 $RPM_SOURCE_DIR/fglrx.desktop \
  $RPM_BUILD_ROOT/usr/share/applications
cp $RPM_SOURCE_DIR/fglrx.png $RPM_BUILD_ROOT/usr/share/pixmaps
%if %suse_version > 1020
mkdir -p $RPM_BUILD_ROOT/usr/%{_lib}/pm-utils/power.d/
install -m 755 $RPM_SOURCE_DIR/ati-powermode.sh \
  $RPM_BUILD_ROOT/usr/%{_lib}/pm-utils/power.d
mkdir -p $RPM_BUILD_ROOT/usr/%{_lib}/powersave/scripts/
install -m 755 $RPM_SOURCE_DIR/toggle-lvds.sh \
  $RPM_BUILD_ROOT/usr/%{_lib}/powersave/scripts/
%else
mkdir -p $RPM_BUILD_ROOT/usr/%{_lib}/powersave/scripts/
install -m 755 $RPM_SOURCE_DIR/{ati-powermode.sh,toggle-lvds.sh} \
  $RPM_BUILD_ROOT/usr/%{_lib}/powersave/scripts/
%endif
mkdir -p $RPM_BUILD_ROOT/etc/init.d
if [ -x $RPM_BUILD_ROOT/usr/sbin/atieventsd ]; then
  install -m 755 $RPM_SOURCE_DIR/atieventsd.sh \
    $RPM_BUILD_ROOT/etc/init.d/atieventsd
  ln -snf /etc/init.d/atieventsd $RPM_BUILD_ROOT/usr/sbin/rcatieventsd
fi
rm -rf $tmpdir
rm -rf $RPM_SOURCE_DIR
echo > files.fglrx
if [ -x $RPM_BUILD_ROOT/usr/sbin/atieventsd ]; then
  cat > files.fglrx << EOF
/etc/init.d/atieventsd
/usr/sbin/atieventsd
/usr/sbin/rcatieventsd
EOF
if [ -f $RPM_BUILD_ROOT/usr/share/man/man8/atieventsd.8.gz ]; then
  echo "/usr/share/man/man8/atieventsd.8.gz" >> files.fglrx
fi
fi
%if %suse_version > 1000
if [ -f $RPM_BUILD_ROOT/usr/bin/amdcccle ]; then
  echo "/usr/bin/amdcccle" >> files.fglrx
fi
%else
echo "/usr/bin/amdcccle" >> files.fglrx
%endif
if [ -f $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libfglrx_tvout.a ]; then
  echo "/usr/X11R6/%{_lib}/libfglrx_tvout.a" >> files.fglrx
fi
if [ -f $RPM_BUILD_ROOT/usr/X11R6/%{_lib}/libfglrx_tvout.so.1.0 ]; then
  echo "/usr/X11R6/%{_lib}/libfglrx_tvout.so.1.0" >> files.fglrx
fi
if [ -f $RPM_BUILD_ROOT/usr/sbin/atigetsysteminfo.sh ]; then
  echo "/usr/sbin/atigetsysteminfo.sh" >> files.fglrx
fi
if [ -f $RPM_BUILD_ROOT/%{MODULES_DIR}/esut.a ]; then
  echo "%{MODULES_DIR}/esut.a" >> files.fglrx
fi
if [ -f $RPM_BUILD_ROOT/%{MODULES_DIR}/glesx.so ]; then
  echo "%{MODULES_DIR}/glesx.so" >> files.fglrx
fi
%ifarch x86_64
if [ -f $RPM_BUILD_ROOT%{DRI_DRIVERS32_DIR}/fglrx_dri.so ]; then
  echo "%{DRI_DRIVERS32_DIR}/fglrx_dri.so" >> files.fglrx
fi
%endif
if [ -f $RPM_BUILD_ROOT%{DRI_DRIVERS_DIR}/fglrx_dri.so ]; then
  echo "%{DRI_DRIVERS_DIR}/fglrx_dri.so" >> files.fglrx
fi
find $RPM_BUILD_ROOT/usr/share/doc/packages/fglrx -type f | xargs chmod 644

%post
%run_ldconfig
if [ -x etc/init.d/atieventsd ]; then
  # Create symbolic run level links for atieventsd start script:
  %{fillup_and_insserv -y atieventsd}
  if [ -r /etc/powersave/events ]; then
    grep -q "EVENT_DAEMON_SCHEME_CHANGE=.*ati-powermode.sh" /etc/powersave/events || \
     sed -e 's/\(EVENT_DAEMON_SCHEME_CHANGE="\)\(.*\)/\1ati-powermode.sh \2/g' -i /etc/powersave/events
  fi
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
ln -snf /usr/%{_lib}/dri usr/X11R6/%{_lib}/modules/dri
%ifarch x86_64
mkdir -p usr/X11R6/lib/modules
test -d usr/X11R6/lib/modules/dri && \
  mv usr/X11R6/lib/modules/dri usr/X11R6/lib/modules/dri.old
ln -snf /usr/lib/dri usr/X11R6/lib/modules/dri
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
exit 0

%preun
if [ -x etc/init.d/atieventsd ]; then
  %stop_on_removal atieventsd
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
fi
exit 0

%files -f files.fglrx
%defattr(-, root, root)
%dir /usr/include/GL
%ifarch x86_64
%dir %{DRI_DRIVERS_DIR}
%endif
/etc/ati/
/usr/include/GL/glxATI.h
/usr/include/GL/glATI.h
%ifarch x86_64
/usr/X11R6/lib/libGL.so
/usr/X11R6/lib/libGL.so.1
/usr/X11R6/lib/libGL.so.1.2
%endif
/usr/X11R6/%{_lib}/libGL.so
/usr/X11R6/%{_lib}/libGL.so.1
/usr/X11R6/%{_lib}/libGL.so.1.2
/usr/share/applications/fglrx.desktop
/usr/share/pixmaps/fglrx.png
/usr/share/doc/packages/fglrx
/usr/bin/fgl_glxgears
/usr/bin/fglrx_xgamma
/usr/bin/fglrxinfo
/usr/bin/fglrx-kernel-build.sh
/usr/bin/aticonfig
%{X11_INCLUDE_DIR}/extensions/fglrx_gamma.h
/usr/X11R6/%{_lib}/libfglrx_gamma.a
/usr/X11R6/%{_lib}/libfglrx_gamma.so*
/usr/X11R6/%{_lib}/libfglrx_pp.a
/usr/X11R6/%{_lib}/libfglrx_pp.so*
%verify(not mtime) %{MODULES_DIR}/drivers/fglrx_drv.*
%{MODULES_DIR}/linux/libfglrxdrm.*
# km_fglrx
%dir /usr/src/kernel-modules
/usr/src/kernel-modules/fglrx/
# powersave script
%if %suse_version > 1020
/usr/%{_lib}/pm-utils/power.d/ati-powermode.sh
%else
/usr/%{_lib}/powersave/scripts/ati-powermode.sh
%endif
# Thinkpad Hotkey script
/usr/%{_lib}/powersave/scripts/toggle-lvds.sh
