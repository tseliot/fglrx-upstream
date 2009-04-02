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

    # Se l'architettura è a 64 bit, allora sposto, se necessario,
    # anche la directory "${ROOT_DIR}/arch/x86/usr/lib" con le librerie
    # a 32 bit.
    # Ci sono due filosofie sulla posizione delle librerie a 32 bit in
    # una distribuzione Slackware-based:
    # 1) Le librerie a 64 bit vanno sotto /usr/lib64, mentre quelle a 32 bit
    #    vanno sotto /usr/lib (Slamd64)
    # 2) Le librerie a 64 bit vanno sotto /usr/lib ed esiste un link
    #    /usr/lib64 che punta a /usr/lib, mentre le librerie a 32 bit vanno sotto
    #    /usr/lib32 (Bluewhite64)
    if [ ${ARCH} = "x86_64" ]; then
	if [ ! -h /usr/lib64 ]; then # Se /usr/lib64 non è un link, allora Slamd64
	    if [ -d /usr/lib ]; then # Se sono presenti già librerie a 32 bit
		mv ${ROOT_DIR}/arch/x86/usr/lib usr; # Sposto le librerie sotto usr/lib
		LIB_DIR=usr/lib; # Usata nel passaggio 1.1
	    fi
	else # /usr/lib64 è un link simbolico, quindi Bluewhite64
	    if [ -d /usr/lib32 ]; then # Se sono presenti già librerie a 32 bit
		mkdir usr/lib32;
		mv ${ROOT_DIR}/arch/x86/usr/lib/* usr/lib32; # Sposto le librerie sotto usr/lib
		LIB_DIR=usr/lib32; # Usata nel passaggio 1.1
	    fi
	fi
    fi

    # Aggiungo directory nell'elenco delle directory con le librerie $LIB_DIR
    case ${ARCH} in
	x86_64)
   	    for lib_dir in usr/lib64 usr/X11R6/lib64 usr/X11R6/lib; do
		if [ -d ${lib_dir}/ ]; then
		    LIB_DIR="${LIB_DIR} ${lib_dir}";
		fi;
	    done
	    LIB_DIR=${LIB_DIR# }; # Tolgo l'eventuale spazio iniziale
	    ;;
	x86)
	    LIB_DIR=usr/lib usr/X11R6/lib;
	    ;;
    esac
    
    # 1.1)
    # Make some symbolik link
    for dir in ${LIB_DIR};
    do
	( cd $dir;
	    for file in *.so.1.?;
	    do
		[ $file = '*.so.1.?' ] && break; # Se vero, allora non esistono file '*.so.1.?'
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
	for file in amdpcsdb; do
	    [ -f $file ] && mv $file ${file}.new;
	done
    )

    # 6)
    # If use xorg >= 7, remove obsolete directory X11R6
    # I moduli per il server X vanno ora sotto /usr/lib(64)/xorg/modules e non più
    # sotto /usr/X11R6/lib(64)/modules
    if (( $XORG_7 )); then
	for dir in ${LIB_DIR}; # Move X usr/$LIB_DIR/modules in usr/$LIB_DIR/xorg/modules
	do
	    if [ -d ${dir}/modules ]; then # Controllo che la directory sia una di quelle che contiene i moduli
		mkdir ${dir}/xorg;
		mv ${dir}/modules ${dir}/xorg;
	    fi
	done
	cp -a usr/X11R6/* usr/;
	rm -rf usr/X11R6;
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
    # Sposto, se esistono, tutti i file .desktop della directory
    # usr/share/gnome in usr/share/applications e poi cancello
    # la directory
    if [ -d usr/share/gnome ]; then
	mkdir -p usr/share/applications
	find usr/share/gnome -name '*desktop' -exec mv '{}' usr/share/applications \;
	rm -rf usr/share/gnome;
    fi

    # 9)
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
    [ "x${TMP_FILE}" != "x" ] && echo ${X_PACK_NAME} >> ${TMP_FILE};

    cd ${ROOT_DIR};
    
    return 0;
}
