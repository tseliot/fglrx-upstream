#!/bin/bash 
#
# Script to adjust power mode of ati graphic chips
#

getXuser() {
        user=`finger| grep -m1 ":$displaynum " | awk '{print $1}'`
        if [ x"$user" = x"" ]; then
                user=`finger| grep -m1 ":$displaynum" | awk '{print $1}'`
        fi
        if [ x"$user" != x"" ]; then
                userhome=`getent passwd $user | cut -d: -f6`
                export XAUTHORITY=$userhome/.Xauthority
        else
                export XAUTHORITY=""
        fi
}

case "$1" in
    true)
	echo "**ATI Low power"
	for x in /tmp/.X11-unix/*; do
	    displaynum=`echo $x | sed s#/tmp/.X11-unix/X##`
	    getXuser;
	    if [ x"$XAUTHORITY" != x"" ]; then
		export DISPLAY=":$displaynum"	    
		su $user -c "/usr/bin/aticonfig --set-powerstate=1 --effective=now"
	    fi
	done
	;;
    false)
	echo "**ATI high power"
	for x in /tmp/.X11-unix/*; do
	    displaynum=`echo $x | sed s#/tmp/.X11-unix/X##`
	    getXuser;
	    if [ x"$XAUTHORITY" != x"" ]; then
		export DISPLAY=":$displaynum"
		su $user -c "/usr/bin/aticonfig --set-powerstate=3 --effective=now"
	    fi
	done
	;;
esac
