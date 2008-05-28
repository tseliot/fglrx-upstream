# Crea il pacchetto per il server X
function _make_x
{
    local CHECK_SCRIPT=./check.sh;
    local XORG_7=0;
    
    # set X_VERSION
    PATH=$PATH:/usr/X11/bin:/usr/X11R6/bin
    source ${CHECK_SCRIPT} --noprint;
    
    case ${X_VERSION} in
	x670*) # Xorg Server 6.7
	    USE_X_VERSION=${X_VERSION/x670/x680}; # Use the xorg 6.8 files
	    ;;
	x7*) # Xorg Server 7.x
	    XORG_7=1;
	    ;;
    esac
    
    [ -z $USE_X_VERSION ] && USE_X_VERSION=${X_VERSION};
    
    cd ${X_PKG_DIR};
    
    # 1)
    # MOVE ARCH DIPENDENT files
    mkdir usr;
    
    mv ${ROOT_DIR}/arch/${ARCH}/usr/* usr;

    case ${ARCH} in
	x86_64)
   	    for lib_dir in usr/X11R6/lib64 usr/X11R6/lib; do
		if [ -d ${lib_dir}/ ]; then
		    LIB_DIR="${LIB_DIR} ${lib_dir}";
		fi;
	    done
	    LIB_DIR=${LIB_DIR# }; # Tolgo l'eventuale spazio iniziale
	    ;;
	x86)
	    LIB_DIR=usr/X11R6/lib;
	    ;;
    esac
    
    # Make some symbolik link
    for dir in ${LIB_DIR};
    do
	( cd $dir;
	    for file in *.so.1.?;
	    do
		ln -s $file ${file%.*};
		ln -s $file ${file%%.*}.so;
	    done
	)
    done
    
    # 2)
    # MOVE ARCH INDIPENDENT files
    cp -rp ${ROOT_DIR}/common/usr/* usr;
    mkdir -p etc/ati
    mv ${ROOT_DIR}/common/etc/ati/{amdpcsdb.default,atiogl.xml,authatieventsd.sh,control,fglrxprofiles.csv,fglrxrc,signature}\
        etc/ati/ 2>/dev/null;
    
    # 3)
    # MOVE USE_X_VERSION DEPENDENT files
    cp -rp ${ROOT_DIR}/${USE_X_VERSION}/usr/* usr;
    

    # 4)
    # Aggiusto i permessi
    # 4.1) Nella directory usr, tolgo i diritti di esecuzione a tutti i file che non siano:
    #      - binari
    #      - librerie (a meno che non siano .a, a questi tolgo il permesso di esecuzion)
    #      - directory
    ( cd usr;
	find . -not \( -wholename "*bin*" -o \( -wholename "*lib*" -a -not -wholename "*.a" \) \) -not -type d\
	   | xargs chmod -x
    )

    # 4.2) I file in usr/sbin devono avere il permesso di esecuzione solo per il root
    ( cd usr/sbin;
   	chmod go-x *;
    )

    # 4.3) Assicuro i giusti permessi ai binari in usr/X11R6/bin
    ( cd usr/X11R6/bin;
	chmod a+x aticonfig fgl_glxgears fglrxinfo fglrx_xgamma 2>/dev/null;
	chmod go-x amdcccle fireglcontrolpanel 2>/dev/null;
    )

    # 4.4) Aggiusto i permessi ai file in etc/ati
    ( cd etc/ati;
	chmod a-x *;
	chmod a+x authatieventsd.sh 2>/dev/null;
    )

    # 5)
    # Alcuni dei file in etc/ati devono essere spostati come .new in modo da preservarli con la rimozione del
    # pacchetto. Inoltre lo script di installazione del pacchetto provvederà a rinominarli o a cancellarli se
    # necessario.
    ( cd etc/ati;
	for file in atiogl.xml authatieventsd.sh fglrxprofiles.csv fglrxrc; do
	    [ -f $file ] && mv $file ${file}.new;
	done
    )

    # 6)
    # If use xorg >= 7, remove obsolete directory X11R6
    if (( $XORG_7 )); then
	for dir in ${LIB_DIR}; # Move X modules in usr/$LIB_DIR/xorg/modules
	do
	    mkdir ${dir}/xorg;
	    mv ${dir}/modules ${dir}/xorg;
	done
	cp -rp usr/X11R6/* usr/;
	rm -rf usr/X11R6;
	
	echo >> install/doinst.sh;
	for dir in ${LIB_DIR}; do
	    echo "[ ! -d /${dir}/modules ] && ln -s /usr/`basename $dir`/xorg/modules /${dir}/" >> install/doinst.sh;
	done
	echo >> install/doinst.sh;
    fi
    
    # 7)
    # - Sposto, se esiste, la directory usr/share/man in usr.
    # - Comprimo le pagine di manuale, se esistono
    if [ -d usr/share/man ]; then
      mv usr/share/man usr;
      for file in usr/man/*/*; do
        gzip $file;
      done
    fi

    # 8)
    # MAKE PACKAGE
    local X_PACK_NAME=${X_PACK_PARTIAL_NAME/fglrx-/fglrx-${X_VERSION}-}.tgz;
    
    # Modify the slack-desc
    ( cd install;
	sed s/fglrx:/fglrx-${X_VERSION}:/ slack-desc > slack-desc.tmp;
	mv -f slack-desc.tmp slack-desc
    )

    # Strip binaries and libraries
    find . | xargs file | sed -n "/ELF.*executable/b PRINT;/ELF.*shared object/b PRINT;d;:PRINT s/\(.*\):.*/\1/;p;"\
	| xargs strip --strip-unneeded 2> /dev/null
    
    makepkg -l y -c n ${X_PACK_NAME};
    mv ${X_PACK_NAME} ${DEST_DIR};
    echo ${X_PACK_NAME} >> ${TMP_FILE};

    cd ${ROOT_DIR};
    
    return 0;
}
