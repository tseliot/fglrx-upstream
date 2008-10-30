GCC_VER_MAJ      = $(shell $(CC) --version | head -n 1 | sed -e 's/[^0-9. ]//g;s/^ *//;s/^\(.\)\..*$$/\1/')

LIBIP_PREFIX	?= ..

obj-m           += fglrx.o
fglrx-libs      += libfglrx_ip.a.GCC$(GCC_VER_MAJ)
fglrx-c-objs    += firegl_public.o      \
                   kcl_agp.o            \
                   kcl_io.o             \
                   kcl_pci.o            
fglrx-objs      += $(fglrx-c-objs) $(fglrx-libs)
fglrx-hdrs      += firegl_public.h      \
                   fglrxko_pci_ids.h    \
                   kcl_agp.h            \
                   kcl_config.h         \
                   kcl_io.h             \
                   kcl_pci.h            \
                   kcl_type.h           
drm-hdrs        += drm.h drmP.h drm_os_linux.h drm_proc.h drm_compat.h

ifeq ($(PAGE_ATTR_FIX),)
PAGE_ATTR_FIX   =1
endif

EXTRA_CFLAGS    += \
                -I$(PWD) \
                -DFGL \
                -DFGL_LINUX \
                -DFGL_GART_RESERVED_SLOT \
                -DFGL_LINUX253P1_VMA_API \
                -DPAGE_ATTR_FIX=$(PAGE_ATTR_FIX) \

ifeq ($(KERNELRELEASE),)
# on first call from remote location we get into this path
# whilst on second call all is managed by the embedding kernel makefile

ifeq ($(KVER),)
KVER            = $(shell uname -r)
endif

ifeq (1,1)
KDIR            = /lib/modules/$(KVER)/build
else
KDIR            = /usr/src/linux-$(KVER)
endif
PWD             = $(shell pwd)

fglrx-cfiles    = ${fglrx-c-objs:.o=.c}

# default:: kmod_build

kmod_build:: $(fglrx-libs) $(fglrx-cfiles) $(fglrx-hdrs) $(drm-hdrs)
	$(MAKE) -C $(KDIR) SUBDIRS=$(PWD) modules

%.c:
	@ln -s ../$@

%.h:
	@ln -s ../$@

%.GCC$(GCC_VER_MAJ):
	@ln -s $(LIBIP_PREFIX)/$@

# distclean:: clean

clean::
	rm -f *.c *.h *.o *.ko *.GCC* .??*

endif

# ### EOF ###
