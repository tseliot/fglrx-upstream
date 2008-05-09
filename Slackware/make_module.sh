# Usata da make_module. Crea il pacchetto per la Slackware
function _make_module_pkg
{
    cd ${MODULE_PKG_DIR};
    
    # Estraggo la versione del kernel dal modulo creato
    local MODULE_KERNEL_VERSION=$(modinfo ./${MODULE_NAME} | grep vermagic| \tr -s ' ' ' '| cut -d' ' -f2);
    local MODULE_DEST_DIR=lib/modules/${MODULE_KERNEL_VERSION}/external;

    mkdir -p ${MODULE_DEST_DIR};
    mv ${MODULE_NAME} ${MODULE_DEST_DIR};

    # Modifico il nome del pacchetto aggiungendo alla fine, la versione del kernel
    MODULE_PACK_NAME=${MODULE_PACK_NAME}_kernel_${MODULE_KERNEL_VERSION//-/_}.tgz;
    makepkg -l y -c n ${MODULE_PACK_NAME};
    
    mv ${MODULE_PACK_NAME} ${DEST_DIR};

    cd ${ROOT_DIR};
   
    return;
}

# Crea il modulo per il kernel
function _make_module
{
    local MODULE_DIR=lib/modules/fglrx/build_mod;

    # Copy arch-depend files
    mv arch/${ARCH}/${MODULE_DIR}/* common/${MODULE_DIR};

    cd common/${MODULE_DIR};

    # Se ci sono, applico le patch (backward compatibility)
    if [ -f ${ROOT_DIR}/${SCRIPT_DIR}/patch_functions.sh ]; then
	source ${ROOT_DIR}/${SCRIPT_DIR}/patch_functions.sh;
	_module_patch;
    fi
    
    # Make modules with ati's script
    if ! sh make.sh; then
	echo ${MESSAGE[9]};
	exit 3;
    fi

    # Make module package
    cd ..;
    if [[ $MODULE_NAME == "fglrx.ko.gz" ]]; then
	mv fglrx*.ko fglrx.ko;
	gzip fglrx.ko; # crea il file con nome uguale a $MODULE_NAME
    else
	mv fglrx*.o fglrx.o;
	gzip fglrx.o; # crea il file con nome uguale a $MODULE_NAME
    fi
    mv ${MODULE_NAME} ${ROOT_DIR}/${MODULE_PKG_DIR};
    
    cd ${ROOT_DIR};
    
    _make_module_pkg;
    
    return;
}
