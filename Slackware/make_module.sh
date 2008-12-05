# Usata da make_module. Crea il pacchetto per la Slackware
function _make_module_pkg
{
    cd ${ROOT_DIR}/${MODULE_PKG_DIR};
    
    # Estraggo la versione del kernel dal modulo creato
    local MODULE_KERNEL_VERSION=$(modinfo ./${MODULE_NAME} | grep vermagic| tr -s ' ' ' '| cut -d' ' -f2);
    local MODULE_DEST_DIR=lib/modules/${MODULE_KERNEL_VERSION}/external;

    mkdir -p ${MODULE_DEST_DIR};
    mv ${MODULE_NAME} ${MODULE_DEST_DIR};

    # Modifico il nome del pacchetto aggiungendo alla fine, la versione del kernel
    MODULE_PACK_NAME=${MODULE_PACK_NAME}_kernel_${MODULE_KERNEL_VERSION//-/_}.tgz;
    makepkg -l y -c n ${MODULE_PACK_NAME};
    
    mv ${MODULE_PACK_NAME} ${DEST_DIR};

    [ "x${TMP_FILE}" != "x" ] && echo ${MODULE_PACK_NAME} >> ${TMP_FILE};

    cd ${ROOT_DIR};
   
    return 0;
}

# Crea il modulo per il kernel
function _make_module
{
    local MODULE_DIR=lib/modules/fglrx/build_mod;

    # Copy arch-depend files
    mv arch/${ARCH}/${MODULE_DIR}/* common/${MODULE_DIR};

    cd common/${MODULE_DIR};

    # Se ci sono, applico le patch
    source ${ROOT_DIR}/${SCRIPT_DIR}/patch_functions.sh;
    _module_patch;
    
    # Make modules with ati's script
    if ! sh make.sh; then
	echo ${MESSAGE[9]};
	exit 1;
    fi

    # Make module package
    cat ../fglrx*.ko | gzip -c >> ${ROOT_DIR}/${MODULE_PKG_DIR}/$MODULE_NAME;
    _make_module_pkg;
    
    return 0;
}