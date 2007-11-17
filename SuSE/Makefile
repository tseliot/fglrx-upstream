# Makefile

specfiles91=x430.SUSE91-IA32.spec x430.SLES9-IA32.spec x430.NLD9-IA32.spec x430_64a.SUSE91-AMD64.spec x430_64a.SLES9-AMD64.spec x430_64a.NLD9-AMD64.spec
specfiles92=x680.SUSE92-IA32.spec x680_64a.SUSE92-AMD64.spec
specfiles93=x680.SUSE93-IA32.spec x680_64a.SUSE93-AMD64.spec
specfiles100=x680.SUSE100-IA32.spec x680_64a.SUSE100-AMD64.spec
specfiles101=x690.SUSE101-IA32.spec x690.SLES10-IA32.spec x690.SLED10-IA32.spec x690_64a.SUSE101-AMD64.spec x690_64a.SLES10-AMD64.spec x690_64a.SLED10-AMD64.spec
specfiles102=x710.SUSE102-IA32.spec x710_64a.SUSE102-AMD64.spec
specfiles103=x710.SUSE103-IA32.spec x710_64a.SUSE103-AMD64.spec
specfiles=$(specfiles91) $(specfiles92) $(specfiles93) $(specfiles100) $(specfiles101) $(specfiles102) $(specfiles103)

all:
	for i in $(specfiles); do \
          arch=""; \
          echo $$i | grep -q AMD64 && arch="64"; \
          xver=4_3_0; \
          echo $$i | grep -q x680 && xver=6_8_0; \
          echo $$i | grep -q x690 && xver=6_9_0; \
          echo $$i | grep -q x710 && xver=7_1_0; \
	  suse=`echo $$i | cut -d "." -f 2 | cut -d "-" -f 1`; \
	  sed s/Name:\ fglrx/Name:\ fglrx$${arch}_$${xver}_$${suse}/g fglrx.spec > $$i; \
	done

diff:	all
	for i in $(specfiles); do diff -u fglrx.spec $$i; done

clean:
	rm -f $(specfiles) *~
