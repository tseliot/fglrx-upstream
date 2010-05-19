# Makefile

specfiles101=x690.SLE10-IA32.spec x690_64a.SLE10-AMD64.spec
specfiles103=x690.SUSE103-IA32.spec x690_64a.SUSE103-AMD64.spec
specfiles110=x690.SUSE110-IA32.spec x690_64a.SUSE110-AMD64.spec
specfiles111=x740.SUSE111-IA32.spec x740_64a.SUSE111-AMD64.spec x740.SLE11-IA32.spec x740_64a.SLE11-AMD64.spec
specfiles112=x740.SUSE112-IA32.spec x740_64a.SUSE112-AMD64.spec
specfiles113=x750.SUSE113-IA32.spec x750_64a.SUSE113-AMD64.spec
specfiles=$(specfiles101) $(specfiles103) $(specfiles110) $(specfiles111) $(specfiles112) $(specfiles113)

tarball=suse.tar.bz2

all:
	for i in $(specfiles); do \
          arch=""; \
          echo $$i | grep -q AMD64 && arch="64"; \
          xver=6_9_0; \
          echo $$i | grep -q x740 && xver=7_4_0; \
          echo $$i | grep -q x750 && xver=7_5_0; \
	  suse=`echo $$i | cut -d "." -f 2 | cut -d "-" -f 1`; \
	  sed s/Name:\ fglrx/Name:\ fglrx$${arch}_$${xver}_$${suse}/g fglrx.spec > $$i; \
	done

diff:	all
	for i in $(specfiles); do diff -u fglrx.spec $$i; done

dist:	all
	tar cjf $(tarball) *

clean:
	rm -f $(tarball) *~
