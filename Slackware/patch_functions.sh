# Copyright (c) 2009 Emanuele Tomasi, Ezio Ghibaudo

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# Usata da _module_patch e da _internal_patch
#
# Applica la patch $1, se e solo se, esiste il programma 'patch'
function _apply_the_patch
{
    if ! grep 'bin/patch$' ${DIR_PACKAGE}/* &> /dev/null; then
	_print_with_color '1;31' "${MESSAGE[23]}\n";
    else
	_print_with_color '1;32' "${MESSAGE[24]}\n";
	patch < $1;
    fi
}

# Usata da _module_patch
#
# Un insieme di patch interne allo SlackBuild. Viene invocata solo se non sono già state trovate patch locali in /etc/ati/patch
function _internal_patch
{
    local ATI_DRIVER_MAJOR_VER=${ATI_DRIVER_VER:0:4}     # Primi 4 caratteri (Es: 8.732 -> 8.73)
    local INT_PATCH_DIR=${ROOT_DIR}/${SCRIPT_DIR}/patch  # Directory che contiene le patch interne
    local file=none                                      # Nome della patch da applicare

    # Controllo l'esistenza della patch e, in caso affermativo, la applico
    if [ -f ${INT_PATCH_DIR}/$file ]; then
	_print_with_color '1;33' "${MESSAGE[27]}";
	echo -e "\t$file";
    	_apply_the_patch ${INT_PATCH_DIR}/$file
    fi
}

# Usata dal file make_module.sh
#
# Applica le patch ai file prima di creare il modulo del kernel
#
# Si dà la possibilità all'utente di patchare i file. Se esiste
# un file chiamato:
#     /etc/ati/patch/patch-${ATI_DRIVER_VER}-${KNL_RELEASE}
# allora la funzione esegue:
#     patch < /etc/ati/patch/patch-${ATI_DRIVER_VER}-${KNL_RELEASE}
#
# Se non esiste un file di patch utente, allora si testano le eventuali
# patch interne invocando la funzione:
#    _internal_patch
function _module_patch
{
    local DIR_PATCH=/etc/ati/patch
    local EXT_PATCH_FOUND=0

    # Vecchia patch per il file make.sh fornito dalla ATI
    sed -i '/if.*\[.*$MODVERSIONS = 0 \]/{s/\($MODVERSIONS\)/"\1"/}' make.sh

    # Controllo se l'utente ha delle patch da applicare
    if [ -d $DIR_PATCH ]; then
	for file in ${DIR_PATCH}/*; do
	    if [ -f $file ] && [ $file = "${DIR_PATCH}/patch-${ATI_DRIVER_VER}-${KNL_RELEASE}" ]; then
		_print_with_color '1;33' "${MESSAGE[22]}";
		echo -e "\t$file";
		_apply_the_patch $file;
		EXT_PATCH_FOUND=1;
		break;
	    fi
	done

	# Applico la ati_to_gpl.patch, se la trovo e se l'md5sum corrisponde
	if [ -f ${DIR_PATCH}/ati_to_gpl.patch ]; then
	    _print_with_color '1;33' "${MESSAGE[25]}"
	    if md5sum -c ${ROOT_DIR}/${SCRIPT_DIR}/atg.md5sum; then
		_print_with_color '1;32' "${MESSAGE[24]}\n";
		sh ${DIR_PATCH}/ati_to_gpl.patch;
	    else
		_print_with_color '1;31' "${MESSAGE[26]}\n";
	    fi
	fi
    fi

    # Se non ho trovato patch locali, provo quelle interne allo SlackBuild
    if [ $EXT_PATCH_FOUND -eq 0 ]; then
	_internal_patch
    fi
}