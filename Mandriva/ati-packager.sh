#!/bin/sh
#
# Purpose
#   Mandriva ATI packaging script
#
# Usage
#   See README.distro document
#
# License
#   This file is available with the same license as Mandriva fglrx.spec,
#   see that file for detailed license information.

# List of supported distributions.
supported_distros="2007.0 2007.1 2008.0 2008.1 2009.0 2009.1 2010.0 2010.1 2010.2 2011.0"

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

buildPackage()
{
    distro=$1
    buildCheck 1 || exit 1
    installer_root="$PWD"
    temp_root="$(mktemp -d --tmpdir ati.XXXXXX)"

    mkdir -p $temp_root/{RPMS,BUILD,tmp}

    version=$(./ati-packager-helper.sh --version)
    # insert 0 to the end of version if helper_version is two-decimal
    [ $(echo $version | cut -f2 -d.) -lt 100 ] && version=${version}0

    LC_ALL=C rpmbuild -bb --with ati \
	--define "_topdir ${temp_root}" \
	--define "_builddir ${temp_root}/BUILD" \
	--define "_rpmdir ${temp_root}/RPMS" \
	--define "_tmppath ${temp_root}/tmp" \
	--define "_sourcedir ${installer_root}/packages/Mandriva" \
	--define "iversion $(./ati-packager-helper.sh --version)" \
	--define "version $version" \
	--define "rel $(./ati-packager-helper.sh --release)" \
	--define "ati_dir ${installer_root}" \
	--define "distsuffix amd.mdv" \
	--define "vendor $(./ati-packager-helper.sh --vendor)" \
	--define "packager $(./ati-packager-helper.sh --vendor)" \
	--define "mdkversion $(echo ${distro}0 | tr -d .)" \
	--define "mandriva_release ${distro}" \
	${installer_root}/packages/Mandriva/fglrx.spec &> $temp_root/output.log

    if [ $? -ne 0 ]; then
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
    distrover=$(cat /etc/version | cut -d. -f1)
    if [ "${package}" != "${distrover}" ]; then
        echo "Mandriva Linux ${distrover} can't use ${package} packages."
        exit 1
    fi
    packagenames="$(rpm -q --specfile --with ati \
        --qf '%{name}-%{version}-%{release}.%{arch}.rpm\n' \
	--define "version $(./ati-packager-helper.sh --version)" \
	--define "rel $(./ati-packager-helper.sh --release)" \
	--define "distsuffix amd.mdv" \
	--define "mdkversion $(echo ${package}0 | tr -d .)" \
	--define "mandriva_release ${package}" \
	$(dirname $0)/fglrx.spec | tail -n+2 | grep -v -e ^fglrx-debug -e ^fglrx-__restore__)"
    if [ -z "${packagenames}" ]; then
        echo "Unable to determine package names."
        exit 1
    fi
    pushd ..
    if [ -n "$DISPLAY" ]; then
        gurpmi --auto $packagenames
    else
        su -c "urpmi --auto $packagenames"
    fi
    ret=$?
    popd
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
    if [ -f /etc/mandriva-release ] && [ "${package}" = "$(cat /etc/version | cut -d. -f1,2)" ]; then
        exit 0
    fi
    exit ${ATI_INSTALLER_ERR_VERS}
    ;;
--getAPIVersion)
    exit 2
    ;;
*|--*)
    echo ${action}: unsupported option passed by ati-installer.sh
    exit 0
    ;;
esac

