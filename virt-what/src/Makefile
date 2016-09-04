#
#   DMI Decode
#   BIOS Decode
#   VPD Decode
#
#   Copyright (C) 2000-2002 Alan Cox <alan@redhat.com>
#   Copyright (C) 2002-2015 Jean Delvare <jdelvare@suse.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#

CC      = gcc
CFLAGS  = -W -Wall -Wshadow -Wstrict-prototypes -Wpointer-arith -Wcast-qual \
          -Wcast-align -Wwrite-strings -Wmissing-prototypes -Winline -Wundef

# Let lseek and mmap support 64-bit wide offsets
CFLAGS += -D_FILE_OFFSET_BITS=64

#CFLAGS += -DBIGENDIAN
#CFLAGS += -DALIGNMENT_WORKAROUND

# When debugging, disable -O2 and enable -g.
CFLAGS += -O2
#CFLAGS += -g

# Project path
dmiP=dmidecode/
virtP=virt-what/
binP=../bin/

# Pass linker flags here
LDFLAGS =

RM              := rm -f

# BSD make provides $MACHINE, but GNU make doesn't
MACHINE ?= $(shell uname -m 2>/dev/null)

PROGRAMS := dmidecode64 virt-what-cpuid-helper $(PROGRAMS-$(MACHINE))

all : $(PROGRAMS)

#
# Programs
#

dmidecode64 : $(dmiP)dmidecode.o $(dmiP)dmiopt.o $(dmiP)dmioem.o $(dmiP)util.o
	$(CC) $(LDFLAGS) $(dmiP)dmidecode.o $(dmiP)dmiopt.o $(dmiP)dmioem.o $(dmiP)util.o --static -o $(binP)$@

virt-what-cpuid-helper : $(virtP)virt-what-cpuid-helper.c
	$(CC) --static $< -o $(binP)$@

#
# Objects
#

dmidecode.o : $(dmiP)dmidecode.c $(dmiP)version.h $(dmiP)types.h $(dmiP)util.h \
							$(dmiP)config.h $(dmiP)dmidecode.h $(dmiP)dmiopt.h $(dmiP)dmioem.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $(dmiP)$@

dmiopt.o : $(dmiP)dmiopt.c $(dmiP)config.h $(dmiP)types.h $(dmiP)util.h \
					 $(dmiP)dmidecode.h $(dmiP)dmiopt.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $(dmiP)$@

dmioem.o : $(dmiP)dmioem.c $(dmiP)types.h $(dmiP)dmidecode.h $(dmiP)dmioem.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $(dmiP)$@

util.o : util.c types.h util.h config.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $(dmiP)$@

#
# Commands
#

clean :
	$(RM) $(dmiP)*.o
