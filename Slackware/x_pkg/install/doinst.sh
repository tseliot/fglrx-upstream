#! /bin/sh

# Copyright (c) 2009 Emanuele Tomasi, Ezio Ghibaudo

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

echo -e "\n########################################################################\n"\
"NOTE:   You have to modify the X server configuration file to use \n"\
"\tthe ATI driver:\n"\
"\n\t\taticonfig --initial\n\n"\
"\tcan it help you. Run aticonfig without options for more details.\n"\
"########################################################################\n";
