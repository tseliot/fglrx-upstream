#!/bin/sh
#
# Copyright (c) 2010 Sebastian Siebert (freespacer@gmx.de)
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# The pattern of this array is
# for openSUSE: SUSE[(number+1)]="SUSE(version) (arch)-(xorg version) ..."
# for SLE:      SUSE[(number+1)]="SLE(version) (arch)-(xorg version) ..."
#
# Important: The array should have a consecutive numbers!

# supported os
SUSE[0]="SLE10 IA32-x690 AMD64-x690_64a"
SUSE[1]="SLE11 IA32-x740 AMD64-x740_64a"
SUSE[2]="SUSE111 IA32-x740 AMD64-x740_64a"
SUSE[3]="SUSE112 IA32-x740 AMD64-x740_64a"
SUSE[4]="SUSE113 IA32-x750 AMD64-x750_64a"
SUSE[5]="SUSE autodetection"

# unsupported os (unofficial package list)
# unlock this list with, for example:
# UNSUPPORTED="yes" ./ati-driver-installer-<version>-<architecture>.run --buildpkg SuSE/SUSE114-AMD64
if [ "${UNSUPPORTED}" = "yes" -o "${UNSUPPORTED}" = "true" -o "${UNSUPPORTED}" = "1"  ]; then
    SUSE[6]="SUSE114 IA32-x760 AMD64-x760_64a"
fi
