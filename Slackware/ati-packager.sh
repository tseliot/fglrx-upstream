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

# Inizializzazione: esegue alcuni controlli di base e imposta delle variabili
# d'ambiente utitli per le altre funzioni.
function _init_env
{
    # Mi assicuro che tutti i comandi interni alla bash necessari, siano abilitati
    enable cd echo exit export local return set source test

    # Controllo i comandi esterni essenziali!
    if ! grep --version >& /dev/null || ! id --version >& /dev/null\
	|| ! gettext --version >& /dev/null; then
	_print '1;31' '' 'You need to install at least one these commands:'\
                         '\n\t- grep\n\t- id\n\t- gettext'
	exit 1
    fi

    # ROOT_DIR = directory attuale
    ROOT_DIR=$PWD

    # Directory, relativa a ROOT_DIR, in cui si trova questo script.
    # Si ricordi che quando l'ati-installer.sh esegue questo script la root directory
    # è ROOT_DIR
    SCRIPT_DIR=packages/Slackware

    # Settaggi per gettext. Inclusione della funzione eval_gettext().
    export TEXTDOMAIN=ATI_SlackBuild
    export TEXTDOMAINDIR=${ROOT_DIR}/${SCRIPT_DIR}/locale
    if ! source gettext.sh; then
	_print '1;31' '' 'gettext.sh: file not found or not executable'
	exit 1
    fi

    [ $(id -u) -gt 0 ] && _print '' '' "`gettext 'Only root can do it!'`" && exit 1

    echo "$ROOT_DIR" | grep -q ' ' && _print '' '' "`gettext "The name of the current directory mustn't contain any spaces"`" && exit 1

    # Comandi esterni da cui il builder dipende nella fase di creazione dei pacchetti
    BUILD_DEPS=(chmod cp cut file find gzip ln makepkg mkdir mv rm sed sh strip tar xargs)

    # Comandi esterni da cui il builder dipende nella fase di installazione dei pacchetti
    INSTALL_DEPS=(basename dirname depmod installpkg lsmod md5sum modprobe ps upgradepkg)

    # Architettura, può essere 'x86' o 'x86_64'
    ARCH=$(arch)
    [[ $ARCH != x86_64 ]] && ARCH='x86'

    # Release del kernel in uso
    KNL_RELEASE=$(uname -r)

    ATI_DRIVER_NAME=fglrx
    ATI_DRIVER_VER=$(./ati-packager-helper.sh --version)
    ATI_DRIVER_REL=$(./ati-packager-helper.sh --release)

    # Directory in cui verranno spostati i pacchetti creati e altri file
    DEST_DIR=${PWD%/*}

    # File temporaneo che contiene l'elenco dei pacchetti creati.
    # Questo file è creato/modificato dalle funzioni che creano i pacchetti
    # se, e solo se, l'installer ($PPID) viene invocato con l'opzione --buildandinstallpkg,
    # e viene cancellato quando questo script viene invocato con il paramentro
    # --installpkg
    TMP_FILE=''
    if grep -q -- '--buildandinstallpkg' /proc/${PPID}/cmdline; then
	TMP_FILE=${DEST_DIR}/tmpSlackwarePkg.txt
    fi

    # Controllo l'esistenza di alcuni comandi utili ma non necessari
    which -V &> /dev/null && USE_WHICH=1 || USE_WHICH=0
    tput -V &> /dev/null && USE_TPUT=1 || USE_TPUT=0
}

# Controlla l'esistenza dei comandi necessari, ma esterni al build
# $1 può essere:
#   'build': per i comandi necessari alla costruzione dei pacchetti
#   'install': per i comandi necessari all'installazione dei pacchetti
#   nessuno dei precedenti: allora $* è un elenco di comandi separati da uno spazio
# $2 può essere (nel caso $1 sia o 'build' o 'install'):
#   '': stampa a video solo il nome dei comandi non trovati
#   '--dryrun': stampa a video il nome del comando che sta controllando
function _check_external_command
{
    local i=0
    local DEPS_OK=0
    local DRYRUN=0

    [ "x$2" = 'x--dryrun' ] && DRYRUN=1

    case $1 in
	build)
	    local DEPS=(${BUILD_DEPS[@]})
	    ;;
	install)
	    local DEPS=(${INSTALL_DEPS[@]})
	    ;;
	*)
	    local DEPS=($*)
	    ;;
    esac

    while [ $i -lt ${#DEPS[@]} ]
    do
	local _command=${DEPS[$i]}
	if (( $DRYRUN )); then
	    _print '' 'n' "`eval_gettext \"Check for command: \\\${_command}\"`"
	    (( $USE_TPUT )) && tput hpa 45
	    echo -n '   [ '
	fi

	if (( $USE_WHICH )); then
	    which ${_command} &> /dev/null
	else
	    grep "bin/${_command}\$" ${DIR_PACKAGE}/* &> /dev/null
	fi

	if [ $? != 0 ]; then
	    if (( $DRYRUN )); then
		_print '1;31' 'n' "`gettext 'NOT FOUND'`"
	    else
		_print '1;31' '' "`eval_gettext \"You must install \\\${_command}\"`"
	    fi
	    DEPS_OK=1
	elif (( $DRYRUN )); then
	    _print '1;32' 'n' "`gettext 'OK'`"
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
# $1 può essere una stringa nulla ('') oppure un colore nella forma ?;??.
#    Per il colore si veda uno dei seguenti valori:
#
#    Nero           0;30     Grigio Scuro  1;30
#    Blu            0;34     Blu Chiaro    1;34
#    Verde          0;32     Verde Chiaro  1;32
#    Ciano          0;36     Ciano Chiaro  1;36
#    Rosso          0;31     Rosso Chiaro  1;31
#    Viola          0;35     Viola Chiaro  1;35
#    Marrone        0;33     Giallo        1;33
#    Grigio Chiaro  0;37     Bianco        1;37
#
# $2 può essere una stringa nulla ('') oppure il carattere 'n'. Se vale 'n',
#    allora dopo la stampa non va a capo.
function _print
{
    local color=$1
    local new_line=$2
    shift 2

    if [ -z $color ]
    then
	echo -e${new_line} "${*}"
    else
	echo -e${new_line} "\E[${color}m${*}\E[00m"
    fi

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
    [ ! -e ${SCRIPT_DIR}/make_module.sh ] && _print '1;31' '' "`gettext 'make_module.sh script missing!'`\n" && return 1
    [ ! -e ${SCRIPT_DIR}/make_x.sh ] && _print '1;31' '' "`gettext 'make_x.sh script missing!'`\n" && return 1

    local DRYRUN=0
    [ "x$2" != 'x' ] && DRYRUN=1

    local version=$1
    case $version in
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
	*) _print '' '' "`eval_gettext \"\\\$version unsupported.\"`"
            return 1
	    ;;
    esac

    return 0
}

# Implemente l'opzione --installpkg dello script
function _installpkg
{
    _print '1;32' '' "`gettext 'Install/Upgrade package/s'`"

    # Controllo l'esistenza del file temporaneo in cui sono scritti i nomi dei pacchetti da installare
    [ ! -f ${TMP_FILE} ] && _print '1;31' '' "`eval_gettext \"ERROR: \\\${TMP_FILE}, file not found\"`" && return 1

    # Installo i pacchetti
    for pkg in $(<${TMP_FILE})
    do
	if [ -f ${DIR_PACKAGE}/${pkg%.tgz} ]; then
            upgradepkg --reinstall "${DEST_DIR}/$pkg"; # Il pacchetto era già installato
	elif [ -f ${DIR_PACKAGE}/$(echo $pkg | cut -d'-' -f-2)* ]; then
	    upgradepkg "${DEST_DIR}/$pkg"; # Il pacchetto era installato ad una versione diversa
	else
	    installpkg "${DEST_DIR}/$pkg"; # Il pacchetto non era installato
	fi
    done

    # Se il modulo è già in memoria, scarico il vecchio e
    # ricarico il nuovo
    if lsmod | grep -q ${ATI_DRIVER_NAME}; then
	local module=${ATI_DRIVER_NAME}
	_print '1;33' '' "`eval_gettext \"Reloading module \\\$module\"`"
	modprobe -r $module
	modprobe $module
    fi

    # Controllo se il server X è attivo
    if ps -C X >/dev/null; then
	_print '1;33' '' "`gettext 'Warning: you must rerun the X server'`"
    fi

    return 0
}

# Directory che contiene l'elenco dei pacchetti installati nelle distribuzioni
# basate su Slackware
DIR_PACKAGE=/var/log/packages

# L'elenco dei maintaners dell'ATI SlackBuild (è una lista separata da ';')
MAINTAINERS='Emanuele Tomasi <tomasi@cli.di.unipi.it>'

# Versione dell'ATI SlackBuild
BUILD_VER=1.4.4

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

	[ ! -d ${DIR_PACKAGE} ] && exit ${ATI_INSTALLER_ERR_VERS}

	exit 0
	;;

    # Questo script onora le API versione 2 dell'ati-installer.sh
    --getAPIVersion)
	exit 2
	;;

    # Lista dei maintainer (separata da ';')
    --get-maintainer)
	echo ${MAINTAINERS}
	exit 0
	;;
esac

_init_env
case $1 in
    # Controllo che tutto il necessario alla costruzione dei pacchetti
    # sia correttamente installato
    --buildprep)
	echo -en "\nATI SlackBuild Version $BUILD_VER"\
                "\n--------------------------------------------"\
                "\nby: "
	echo -e ${MAINTAINERS//;/\\n} "\n"

	EXIT_STATUS=0

	# Controllo che $3 sia un blank oppure --dryrun
	opt=$3
	if [ "x${opt}" != 'x' ] && [ "x${opt}" != 'x--dryrun' ]; then
	    _print '1;31' '' "`eval_gettext \"ERROR: \\\${opt} is not a valid parameter\"`"
	    EXIT_STATUS=${ATI_INSTALLER_ERR_PREP}
	fi
	unset opt

	# Controllo l'esistenza dei comandi esterni necessari alla costruzione del pacchetto
        ! _check_external_command 'build' $3 && EXIT_STATUS=${ATI_INSTALLER_ERR_PREP}

	# Controllo che il parametro $2 sia un nome di pacchetto da costruire, valido
	! _buildpkg $2 '--dryrun' && EXIT_STATUS=${ATI_INSTALLER_ERR_PREP}

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
	command=$1
	_print '' '' "`eval_gettext \"\\\${command}: unsupported option passed by ati-installer.sh\"`"
	exit 1
	;;
esac