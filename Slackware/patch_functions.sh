# Copyright (c) 2009 Emanuele Tomasi, Ezio Ghibaudo, Federico Rota

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

# Applica le patch ai file prima di creare il modulo del kernel
# Si dà la possibilità all'utente di patchare i file, se esiste
# un file chiamato /etc/ati/patch/patch-${ATI_DRIVER_VER}-${KNL_VER}
# allora la funzione esegue:
#     patch < /etc/ati/patch/patch-${ATI_DRIVER_VER}-${KNL_VER}
function _module_patch
{
    local KNL_VER=$(uname -r)
    local DIR_PATCH=/etc/ati/patch

    # Vecchia patch per il file make.sh fornito dalla ATI
    sed -i '/if.*\[.*$MODVERSIONS = 0 \]/{s/\($MODVERSIONS\)/"\1"/}' make.sh

    # Controllo se l'utente ha delle patch da applicare
    if [ -d $DIR_PATCH ]; then
	for file in ${DIR_PATCH}/*; do
	    if [ -f $file ] && [ $file = "${DIR_PATCH}/patch-${ATI_DRIVER_VER}-${KNL_VER}" ]; then
		_print_with_color '1;33' "${MESSAGE[22]}";
		echo -e "\t$file";
		if ! grep 'bin/patch$' ${DIR_PACKAGE}/* &> /dev/null; then
		    _print_with_color '1;31' "${MESSAGE[23]}\n";
		else
		    _print_with_color '1;32' "${MESSAGE[24]}\n";
		    patch < $file;
		fi
		break;
	    fi
	done

	# Applico la ati_to_gpl.patch, se la trovo e se l'md5sum corrisponde
	if [ -f ${DIR_PATCH}/ati_to_gpl.patch ]; then
	    _print_with_color '1;33' "${MESSAGE[25]}"
	    if md5sum -c ${ROOT_DIR}/${SCRIPT_DIR}/atg.md5sum; then #&> /dev/null; then
		_print_with_color '1;32' "${MESSAGE[24]}\n";
		sh ${DIR_PATCH}/ati_to_gpl.patch;
	    else
		_print_with_color '1;31' "${MESSAGE[26]}\n";
	    fi
	fi
    fi
}
