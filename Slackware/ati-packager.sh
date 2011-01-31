#!/bin/bash

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

# Imposta la lingua dei messaggi del builder.
# Crea l'array MESSAGE usato per le stampe dei messaggi in output
function _set_builder_language
{
    local EXT=$(echo $LANG | cut -d '_' -f1)
    local FILE='/packages/Slackware/languages/ati-packager.en'

    if [ -e "${PWD}"/packages/Slackware/languages/ati-packager.${EXT} ]; then
	local FILE="/packages/Slackware/languages/ati-packager.${EXT}"
    fi

    local IFS=$(echo -e '\n\t')
    MESSAGE=($(cat "${PWD}"$FILE))

    return 0
}

# Inizializzazione: esegue alcuni controlli di base e imposta delle variabili
# d'ambiente utitli per le altre funzioni.
function _init_env
{
    [ $(id -u) -gt 0 ] && echo ${MESSAGE[6]} && exit 1

    BUILD_VER=1.4.2

    # ROOT_DIR = directory attuale
    ROOT_DIR=$PWD
    echo "$ROOT_DIR" | grep -q ' ' && echo ${MESSAGE[7]} && exit 1

    # Comandi interni alla bash da cui il builder dipende
    BUILTIN_DEPS=(\[ cd echo exit local return set source)

    # Comandi esterni da cui il builder dipende nella fase di creazione dei pacchetti
    BUILD_DEPS=(chmod cp cut file find grep gzip id ln makepkg mkdir modinfo mv rm sed sh
	strip tar tr xargs)

    # Comandi esterni da cui il builder dipende nella fase di installazione dei pacchetti
    INSTALL_DEPS=(basename dirname depmod installpkg lsmod md5sum modprobe ps upgradepkg)

    # Mi assicuro che tutti i comandi interni alla bash necessari, siano abilitati
    enable ${BUILTIN_DEPS[@]}

    # Architettura, può essere 'x86' o 'x86_64'
    ARCH=$(arch)
    [[ $ARCH != x86_64 ]] && ARCH='x86'

    # Informazioni sul kernel in uso
    KNL_RELEASE=$(uname -r)
    KNL_VERSION=$(echo $KNL_RELEASE | cut -d '.' -f1)
    KNL_MAJOR=$(echo $KNL_RELEASE | cut -d '.' -f2)
    KNL_MINOR=$(echo $KNL_RELEASE | cut -d '.' -f3)
    KNL_BUILD=$(echo $KNL_RELEASE | cut -d '.' -f4)

    # Directory, relativa alla root directory attuale, in cui si trova questo script.
    # Si ricordi che quando l'ati-installer.sh esegue questo script, la root directory
    # non è quella in cui si trova questo script.
    SCRIPT_DIR=packages/Slackware

    ATI_DRIVER_VER=$(./ati-packager-helper.sh --version)
    ATI_DRIVER_REL=$(./ati-packager-helper.sh --release)

    # Nome del modulo del kernel
    MODULE_NAME=fglrx.ko.gz

    # Directory in cui verranno messi i file per la creazione del pacchetto del modulo
    # del kernel
    MODULE_PKG_DIR=${SCRIPT_DIR}/module_pkg

    # Nome del pacchetto del modulo del kernel
    MODULE_PACK_NAME=fglrx-module-${ATI_DRIVER_VER}-${ARCH}-${ATI_DRIVER_REL}

    # Directory in cui verranno messi i file per la creazione del pacchetto per il server X
    X_PKG_DIR=${SCRIPT_DIR}/x_pkg

    # Nome parziale (verrà poi integrato) del pacchetto per il server X
    X_PACK_PARTIAL_NAME=fglrx-${ATI_DRIVER_VER}-${ARCH}-${ATI_DRIVER_REL}

    # Directory in cui verranno spostati i pacchetti creati e altri file
    DEST_DIR=${PWD%/*}

    # File temporaneo che contiene l'elenco dei pacchetti creati.
    # Questo file è creato/modificato dalle funzioni che creano i pacchetti
    # se, e solo se, l'installer ($PPID) viene invocato con l'opzione --buildandinstallpkg,
    # e viene cancellato quando questo script viene invocato con il paramentro
    # --installpkg
    if grep -q -- '--buildandinstallpkg' /proc/${PPID}/cmdline; then
      TMP_FILE=${DEST_DIR}/tmpSlackwarePkg.txt
    else
      TMP_FILE=''
    fi

    # Controllo l'esistenza di alcuni comandi utili ma non necessari
    which -V &> /dev/null && USE_WHICH=1 || USE_WHICH=0
    tput -V &> /dev/null && USE_TPUT=1 || USE_TPUT=0
}

# Controlla l'esistenza dei comandi necessari, ma esterni al build
# $1 può essere:
# 'build': controlla l'esistenza dei comandi necessari alla costruzione dei pacchetti
# 'install': controlla l'esistenza dei comandi necessari all'installazione dei pacchetti
# $2 può essere:
# '': stampa a video solo il nome dei comandi non trovati
# '--dryrun': stampa a video il nome del comando che sta controllando
function _check_external_command
{
    local i=0
    local DEPS_OK=0
    local DRYRUN=0
    [ "x$2" = 'x--dryrun' ] && DRYRUN=1

    # Se non ho il comando which e neanche il comando grep, errore
    if (( ! $USE_WHICH )) && ! grep -V &> /dev/null; then
	_print_with_color '1;31' "${MESSAGE[4]} grep"
	return 1
    fi

    case $1 in
	build)
	    local DEPS=(${BUILD_DEPS[@]})
	    ;;
	install)
	    local DEPS=(${INSTALL_DEPS[@]})
	    ;;
    esac

    while [ $i -lt ${#DEPS[@]} ]
    do
	if (( $DRYRUN )); then
	    echo -n "${MESSAGE[5]} ${DEPS[$i]}"
	    (( $USE_TPUT )) && tput hpa 35
	    echo -n '[ '
	fi

	if (( $USE_WHICH )); then
	    which ${DEPS[$i]} &> /dev/null
	else
	    grep "bin/${DEPS[$i]}\$" ${DIR_PACKAGE}/* &> /dev/null
	fi

	if [ $? != 0 ]; then
	    (( $DRYRUN )) && local OPT='_n'
	    _print_with_color "1;31${OPT}" "${MESSAGE[4]} ${DEPS[$i]}"
	    DEPS_OK=1
	elif (( $DRYRUN )); then
	    _print_with_color '1;32_n' 'OK'
	fi

	(( $DRYRUN )) && echo ' ]'
	let i++
    done

    if [ $DEPS_OK != 0 ]
    then
	return 1
    fi

    return 0
}

# Stampa a video i parametri $[2-*]
# $1 è nella forma COLORE[_n], dove
# COLORE può essere uno dei seguenti valori (quelli nella forma ?;??):
#
# Nero           0;30     Grigio Scuro  1;30
# Blu            0;34     Blu Chiaro    1;34
# Verde          0;32     Verde Chiaro  1;32
# Ciano          0;36     Ciano Chiaro  1;36
# Rosso          0;31     Rosso Chiaro  1;31
# Viola          0;35     Viola Chiaro  1;35
# Marrone        0;33     Giallo        1;33
# Grigio Chiaro  0;37     Bianco        1;37
function _print_with_color
{
    local COLOR=${1%_*}
    local NEW_LINE=${1#*_}
    [ $1 = $NEW_LINE ] && NEW_LINE=''
    shift
    echo -e${NEW_LINE} "\E[${COLOR}m${*}\E[00m"
    return 0
}

# Implementa l'opzione --buildpkg dello script
# $1: nome del pacchetto da costruire
# $2 può essere:
# '' : costruisce il pacchetto
# '--dryrun': controlla solo che il parametro $1 sia corretto
#             ritorna 0 se lo è, 1 altrimenti
function _buildpkg
{
    [ ! -e ${SCRIPT_DIR}/make_module.sh ] && _print_with_color '1;31' "${MESSAGE[11]}\n" && return 1
    [ ! -e ${SCRIPT_DIR}/make_x.sh ] && _print_with_color '1;31' "${MESSAGE[12]}\n" && return 1

    local DRYRUN=0
    [ "x$2" != 'x' ] && DRYRUN=1

    case "$1" in
	Only_Module)
	    (( $DRYRUN )) && return 0
	    source ${SCRIPT_DIR}/make_module.sh
	    _make_module
	    ;;
	Only_X)
	    (( $DRYRUN )) && return 0
	    source ${SCRIPT_DIR}/make_x.sh
	    _make_x
	    ;;
	All)
	    (( $DRYRUN )) && return 0
	    source ${SCRIPT_DIR}/make_module.sh
	    _make_module
	    source ${SCRIPT_DIR}/make_x.sh
	    _make_x
	    ;;
	*) echo "$1 ${MESSAGE[10]}"
           return 1
	   ;;
    esac

    return 0
}

# Implemente l'opzione --installpkg dello script
function _installpkg
{
  _print_with_color '1;32' "${MESSAGE[19]}"

  # Controllo l'esistenza del file temporaneo in cui sono scritti i nomi dei pacchetti
  # da installare
  [ ! -f ${TMP_FILE} ] && _print_with_color '1;31' "${MESSAGE[16]} ${TMP_FILE}, ${MESSAGE[17]}" && return 1

  # Controllo che il server X non sia attivo
  ps -C X >/dev/null && _print_with_color '1;31' "${MESSAGE[16]} ${MESSAGE[20]}" && return 1

  # Se MODULE_IN_MEMORY == 1 il modulo è già presente in memoria
  local MODULE_IN_MEMORY=0
  lsmod | grep -q ${MODULE_NAME%.ko.gz} && MODULE_IN_MEMORY=1

  # Installo i pacchetti
  for pkg in $(<${TMP_FILE})
    do
      if [ -f ${DIR_PACKAGE}${pkg%.tgz} ]; then
        upgradepkg --reinstall "${DEST_DIR}/$pkg"; # Il pacchetto era già installato
      elif [ -f ${DIR_PACKAGE}$(echo $pkg | cut -d'-' -f-2)* ]; then
	upgradepkg "${DEST_DIR}/$pkg"; # Il pacchetto era installato ad una versione diversa
      else
	installpkg "${DEST_DIR}/$pkg"; # Il pacchetto non era installato
      fi
    done

  # Se il modulo è già in memoria, scarico il vecchio e
  # ricarico il nuovo
  if [ $MODULE_IN_MEMORY -eq 1 ]; then
    echo "${MESSAGE[21]} ${MODULE_NAME%.ko.gz};"
    modprobe -r ${MODULE_NAME%.ko.gz}
    modprobe ${MODULE_NAME%.ko.gz}
  fi

  return 0
}

# Directory che contiene l'elenco dei pacchetti installati nelle distribuzioni
# basate su Slackware
DIR_PACKAGE=/var/log/packages/

# Per queste opzioni, non c'è bisogno dell'inizializzazione
case $1 in
    # Stampa l'elenco dei nomi di pacchetto che è possibile costruire
    --get-supported)
	echo -e 'All\tOnly_Module\tOnly_X'
	exit 0
	;;

    # Ritorna:
    # ${ATI_INSTALLER_ERR_VERS}: se la distribuzione su cui si sta tentando di eseguire lo script
    #                            non è basata su Slackware
    # 0: Se la distribuzione su cui si sta tentando di eseguire lo script è basata su Slackware
    #    e se il pacchetto che si vuole creare è 'All'.
    --identify)
	[ $2 != 'All' ] && exit ${ATI_INSTALLER_ERR_VERS}

	[ -d ${DIR_PACKAGE} ] && exit 0

	exit ${ATI_INSTALLER_ERR_VERS}
	;;

    # Questo script onora le API versione 2 dell'ati-installer.sh
    --getAPIVersion)
	exit 2
	;;

    # Lista dei maintainer (separata da ';')
    --get-maintainer)
	echo "Emanuele Tomasi <tomasi@cli.di.unipi.it>"
	exit 0
	;;
esac

_set_builder_language
_init_env
case $1 in
    # Controllo che tutto il necessario alla costruzione dei pacchetti
    # sia correttamente installato
    --buildprep)
	echo -e "\n${MESSAGE[0]} $BUILD_VER"\
		"\n--------------------------------------------"\
		"\n${MESSAGE[1]}\n"

	EXIT_STATUS=0

	# Controllo che $3 sia un blank oppure --dryrun
	if [ "x$3" != 'x' ] && [ "x$3" != 'x--dryrun' ]; then
	    _print_with_color '1;31' "${MESSAGE[16]} $3 ${MESSAGE[18]}"
	    EXIT_STATUS=${ATI_INSTALLER_ERR_PREP}
	fi

	# Controllo che il parametro $2 sia un nome di pacchetto da costruire, valido
	! _buildpkg $2 '--dryrun' && EXIT_STATUS=${ATI_INSTALLER_ERR_PREP}

	# Controllo l'esistenza dei comandi esterni necessari alla costruzione del pacchetto
        ! _check_external_command 'build' $3 && EXIT_STATUS=${ATI_INSTALLER_ERR_PREP}

	# Elimino, se esiste, il file temporaneo creato/modificato da --buildpkg
	rm -f ${TMP_FILE}

	exit $EXIT_STATUS
	;;
    # Creo il/i pacchetto/i
    --buildpkg)
	_buildpkg $2
	exit $?
	;;

    # Controllo che tutto il necessario alla corretta installazione del/i pacchetto/i
    # sia correttamente installato
    --installprep)
	DRYRUN=0
	[ "x$3" = 'x--dryrun' ] && DRYRUN=1

	EXIT_STATUS=0

	# Controllo l'esistenza dei comandi esterni necessari
	! _check_external_command 'install' $3 && EXIT_STATUS=${ATI_INSTALLER_ERR_PREP}

	# Controllo che la versione del server Xorg sia maggiore o uguale a 6.7
	source ./check.sh --noprint
	if [ -z ${X_VERSION} ]; then
	    (( $DRYRUN )) && _print_with_color '1;31' "${MESSAGE[13]} >= 6.7"
	    EXIT_STATUS=${ATI_INSTALLER_ERR_PREP}
	fi

	# Controllo che la versione del kernel sia maggiore o uguale a 2.6
	if [ $KNL_VERSION -lt 2 ] || [ $KNL_MAJOR -lt 6 ]; then
	    (( $DRYRUN )) && _print_with_color '1;31' "${MESSAGE[14]} >= 2.6"
	    EXIT_STATUS=${ATI_INSTALLER_ERR_PREP}
	fi

	# Controllo la versione delle librerie glibc
	GLIBC_VER=$(ldconfig --version| head -n1 | grep -o [[:digit:]]\.[[:digit:]])
	if [ $(echo $GLIBC_VER | cut -d'.' -f1) -lt 2 ] || [ $(echo $GLIBC_VER | cut -d'.' -f2) -lt 2 ]; then
	    (( $DRYRUN )) && _print_with_color '1;31' "${MESSAGE[15]} >= 2.2"
	    EXIT_STATUS=${ATI_INSTALLER_ERR_PREP}
	fi

	exit $EXIT_STATUS
	;;

    # Installo i pacchetti creati dall'opzione --buildpkg, il nome dei pacchetti creati
    # si trova nel file ${TMP_FILE}. Alla fine elimino suddetto file.
    --installpkg)
        _installpkg
        VALUE=$?

	rm -f ${TMP_FILE}
	exit $VALUE
	;;

    *)
	echo "${1}: unsupported option passed by ati-installer.sh"
	exit 1
	;;
esac