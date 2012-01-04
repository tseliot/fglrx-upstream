#!/bin/sh
#
# Purpose
#   Mandriva AMD packaging script
#
# Usage
#   See README.distro document
#
# License
#   This file is available with the same license as Mandriva fglrx.spec,
#   see that file for detailed license information.

# List of supported distributions.
supported_distros="2007.0 2007.1 2008.0 2008.1 2009.0 2009.1 2010.0 2010.1 2010.2 2011.0 2012.0"

buildCheck()
{
    print_msg_uninstalled="$1"
    if [ ! -f /etc/mandriva-release ]; then
        echo "You can build Mandriva packages only on a Mandriva Linux system."
        return 1
    fi
    [ -x /usr/bin/rpmbuild ] && return 0
    if [ -n "$print_msg_uninstalled" ]; then
        echo "You need the rpm-build package to build packages."
    fi
    return 2
}   

buildPrep()
{
    distro=$1
    dryrun=$2

    buildCheck "$dryrun" && exit 0
    [ $? -eq 1 ] && exit ${ATI_INSTALLER_ERR_PREP}

    if [ -n "$DISPLAY" ]; then
        gurpmi --auto rpm-build
    else
        su -c "urpmi --auto rpm-build"
    fi

    [ -x /usr/bin/rpmbuild ] && exit 0

    echo "Package rpm-build is needed but installation failed."
    exit ${ATI_INSTALLER_ERR_PREP}
}

commonRPMparams()
{
    distro=$1
    version=$(./ati-packager-helper.sh --version)
    # insert 0 to the end of version if helper_version is two-decimal
    [ $(echo $version | cut -f2 -d.) -lt 100 ] && version=${version}0
    # --specfile can't take --with
    echo -e "--define\n _with_amd 1"
    echo -e "--define\n iversion $(./ati-packager-helper.sh --version)"
    echo -e "--define\n version $version"
    echo -e "--define\n rel $(./ati-packager-helper.sh --release)"
    echo -e "--define\n distsuffix amd.mdv"
    echo -e "--define\n vendor $(./ati-packager-helper.sh --vendor)"
    echo -e "--define\n packager $(./ati-packager-helper.sh --vendor)"
    echo -e "--define\n mdkversion $(echo ${distro}0 | tr -d .)"
    echo -e "--define\n mandriva_release ${distro}"
    echo -e "--define\n _sourcedir $PWD/packages/Mandriva"
}

buildPackage()
{
    distro=$1
    buildCheck 1 || exit 1
    installer_root="$PWD"
    temp_root="$(mktemp -d --tmpdir amd.XXXXXX)"

    mkdir -p $temp_root/{RPMS,BUILD,tmp}

    # hack to avoid word splitting of --defines from commonRPMparams
    oldIFS="$IFS"
    IFS=$'\n'

    LC_ALL=C rpmbuild -bb \
	$(commonRPMparams $distro) \
	--define "_topdir ${temp_root}" \
	--define "_builddir ${temp_root}/BUILD" \
	--define "_rpmdir ${temp_root}/RPMS" \
	--define "_tmppath ${temp_root}/tmp" \
	--define "amd_dir ${installer_root}" \
	${installer_root}/packages/Mandriva/fglrx.spec &> $temp_root/output.log

    rc=$?
    IFS="$oldIFS"

    if [ $rc -ne 0 ]; then
        echo "Building package failed!"
        echo "rpmbuild output follows:"
        cat $temp_root/output.log
        rm -rf "$temp_root"
        exit 1
    fi
    movedir=$(readlink -f ..)
    for package in ${temp_root}/RPMS/*/*.rpm; do
        mv $package $movedir
        echo "Created package: $movedir/$(basename $package)"
    done
    rm -rf "$temp_root"
    exit 0
}

installPackage()
{
    package=$1
    distrover=$(cat /etc/version | cut -d. -f1,2)
    if [ "${package}" != "${distrover}" ]; then
        echo "Mandriva Linux ${distrover} can't use ${package} packages."
        exit 1
    fi

    # hack to avoid word splitting of --defines from commonRPMparams
    oldIFS="$IFS"
    IFS=$'\n'

    packagenames="$(rpm -q --specfile \
	$(commonRPMparams $package) \
	--qf '%{name}-%{version}-%{release}.%{arch}.rpm\n' \
	$(dirname $0)/fglrx.spec | tail -n+2 | grep -v -e ^fglrx-debug -e ^fglrx-__restore__)"

    IFS="$oldIFS"

    if [ -z "${packagenames}" ]; then
        echo "Unable to determine package names."
        exit 1
    fi
    pushd .. >/dev/null
    if [ -n "$DISPLAY" ]; then
        gurpmi --auto $packagenames
    else
        su -c "urpmi --auto $packagenames"
    fi
    ret=$?
    popd >/dev/null
    if [ $ret -ne 0 ]; then
        echo "Unable to install packages."
        exit 1
    fi
    echo "Installation successful."
    exit 0
}

isValidDistro()
{
    for supp_distro in $supported_distros; do
        [ "${supp_distro}" = "$1" ] && return 0 
    done
    return 1
}

checkDistro()
{
    distro=$1

    if ! isValidDistro "$distro"; then
        echo "Unsupported distribution:" $distro
        exit 1
    fi
}

action=$1

case "${action}" in
--get-supported)
    echo $supported_distros | xargs -n1
    ;;
--buildpkg)
    package=$2
    checkDistro $package
    buildPackage $package
    ;;
--buildprep)
    package=$2
    if [ -n "$3" -a "$3" != "--dryrun" ]; then
        echo $3: unsupported option passed by ati-installer.sh
        exit 1
    fi
    checkDistro $package
    buildPrep $package $3
    ;;
--installpkg)
    package=$2
    checkDistro $package
    installPackage $package
    ;;
--installprep)
    package=$2
    checkDistro $package
    # All this is handled in --installpkg already.
    exit 0
    ;;
--identify)
    package=$2
    if [ -f /etc/mandriva-release ] && [ "${package}" = "$(cut -d. -f1,2 /etc/version)" ]; then
        exit 0
    fi
    exit ${ATI_INSTALLER_ERR_VERS}
    ;;
--get-maintainer)
    echo "Dmitry Mikhirev <dmikhirev@mandriva.org>"
    exit 0
    ;;
--getAPIVersion)
    exit 2
    ;;
*|--*)
    echo ${action}: unsupported option passed by ati-installer.sh
    exit 0
    ;;
esac

