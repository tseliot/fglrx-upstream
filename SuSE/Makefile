# Makefile

specfiles101=x690.SLES10-IA32.spec x690.SLED10-IA32.spec x690_64a.SLES10-AMD64.spec x690_64a.SLED10-AMD64.spec
specfiles102=x710.SUSE102-IA32.spec x710_64a.SUSE102-AMD64.spec
specfiles103=x710.SUSE103-IA32.spec x710_64a.SUSE103-AMD64.spec
specfiles110=x710.SUSE110-IA32.spec x710_64a.SUSE110-AMD64.spec
specfiles111=x740.SUSE111-IA32.spec x740_64a.SUSE111-AMD64.spec
specfiles=$(specfiles101) $(specfiles102) $(specfiles103) $(specfiles110) $(specfiles111)

tarball=suse.tar.bz2

all:
	for i in $(specfiles); do \
          arch=""; \
          echo $$i | grep -q AMD64 && arch="64"; \
          xver=6_9_0; \
          echo $$i | grep -q x710 && xver=7_1_0; \
          echo $$i | grep -q x740 && xver=7_4_0; \
	  suse=`echo $$i | cut -d "." -f 2 | cut -d "-" -f 1`; \
	  sed s/Name:\ fglrx/Name:\ fglrx$${arch}_$${xver}_$${suse}/g fglrx.spec > $$i; \
	done

diff:	all
	for i in $(specfiles); do diff -u fglrx.spec $$i; done

dist:	all
	tar cjf $(tarball) *

clean:
	rm -f $(tarball) *~
