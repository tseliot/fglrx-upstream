# Copyright (c) 2009 Emanuele Tomasi

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

# Usata da make_module. Crea il pacchetto per la Slackware
function _make_module_pkg
{
    cd ${ROOT_DIR}/${MODULE_PKG_DIR}

    # Estraggo la versione del kernel dal modulo creato
    local MODULE_KERNEL_VERSION=$(modinfo ./${MODULE_NAME} | grep vermagic| tr -s ' ' ' '| cut -d' ' -f2)
    local MODULE_DEST_DIR=lib/modules/${MODULE_KERNEL_VERSION}/external

    mkdir -p ${MODULE_DEST_DIR}
    mv ${MODULE_NAME} ${MODULE_DEST_DIR}

    # Modifico il nome del pacchetto aggiungendo alla fine, la versione del kernel
    MODULE_PACK_NAME=${MODULE_PACK_NAME}_kernel_${MODULE_KERNEL_VERSION//-/_}.tgz

    makepkg -l y -c n ${DEST_DIR}/${MODULE_PACK_NAME}

    [ "x${TMP_FILE}" != "x" ] && echo ${MODULE_PACK_NAME} >> ${TMP_FILE}

    cd ${ROOT_DIR}

    return 0
}

# Crea il modulo per il kernel
function _make_module
{
    local MODULE_DIR=lib/modules/fglrx/build_mod

    # Copy arch-depend files
    mv arch/${ARCH}/${MODULE_DIR}/* common/${MODULE_DIR}

    cd common/${MODULE_DIR}

    # Se ci sono, applico le patch
    source ${ROOT_DIR}/${SCRIPT_DIR}/patch_functions.sh
    _module_patch

    # Make modules with ati's script
    if ! sh make.sh; then
	_print '' '' "`gettext "ERROR: I didn't make module"`"
	exit 1
    fi

    # Make module package
    cat ../fglrx*.ko | gzip -c >> ${ROOT_DIR}/${MODULE_PKG_DIR}/$MODULE_NAME
    _make_module_pkg

    return 0
}