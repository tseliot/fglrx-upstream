#! /bin/sh

config() {
  NEW="$1"
  OLD="`dirname $NEW`/`basename $NEW .new`"
  [ ! -f $NEW ] && return

  # If there's no config file by that name, mv it over:
  if [ ! -f $OLD ]; then
    mv $NEW $OLD
  elif [ "`cat $OLD | md5sum`" = "`cat $NEW | md5sum`" ]; then # toss the redundant copy
    rm $NEW
  fi
  # Otherwise, we leave the .new copy for the admin to consider...
}

config etc/ati/atiogl.xml.new;
config etc/ati/authatieventsd.sh.new;
config etc/ati/fglrxprofiles.csv.new;
config etc/ati/fglrxrc.new;

if ! (mount | grep /dev/shm &>/dev/null); then
   echo -e "\n########################################################################################\n"\
"WARNING: /dev/shm is not mounted, see the file /usr/share/doc/fglrx/articles/devshm.html\n"\
"########################################################################################\n"
fi

echo -e "\n####################################################################\n"\
"NOTE:   You have to modify the X server configuration file to use \n"\
"\tthe ATI driver:\n"\
"\n\t\taticonfig --initial\n\n"\
"\tcan it help you. Run aticonfig without options for more details.\n"\
"####################################################################\n";
