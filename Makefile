BUILDDIR =  build
VERSION = 1.0.7-1
VERSION_FILE = VERSION-FILE

version-file:
	@$(SHELL_PATH) ./VERSION-GEN
-include $(VERSION_FILE)

TARFILE = cyg-apt-$(VERSION).tar.bz2
SRCTARFILE = cyg-apt-$(VERSION)-src.tar.bz2
TOOLS = tools
CP = /usr/bin/cp -f
RM = /usr/bin/rm -f
MV = /usr/bin/mv
GZIP = /usr/bin/gzip
TMP = tmp

all:
	$(CP) cyg-apt $(BUILDDIR)/root/usr/bin
	$(GZIP) -c cyg-apt.1 > cyg-apt.1.gz
	$(MV) cyg-apt.1.gz $(BUILDDIR)/root/usr/share/man/man1/
	$(CP) postinstall-cyg-apt.sh $(BUILDDIR)/root/etc/postinstall/cyg-apt.sh
	$(CP) cygwin.sig $(BUILDDIR)/root/usr/share/cyg-apt
	cd $(BUILDDIR)/root ; pwd ; tar --exclude=".svn" -jcf $(TARFILE) *;\
mv $(TARFILE) ../release-2/cyg-apt;
	$(CP) setup.hint $(BUILDDIR)/release-2/cyg-apt
	$(TOOLS)/md5.sum.py -f $(BUILDDIR)/release-2/cyg-apt/ $(BUILDDIR)/release-2/cyg-apt/md5.sum
ifdef CYGAPT_TESTMIRROR
	scp $(BUILDDIR)/release-2/cyg-apt/* $(CYGAPT_TESTMIRROR)/release-2/cyg-apt
endif
	$(TOOLS)/setup_ini_diff_make.py mini_mirror/setup-2.ini cyg-apt install md5 --field-input=$(BUILDDIR)/release-2/cyg-apt/$(TARFILE)
	patch mini_mirror/setup-2.ini setup-2.ini.diff
ifdef CYGAPT_TESTMIRROR
	scp mini_mirror/setup-2.ini $(CYGAPT_TESTMIRROR)/setup-2.ini
endif
	$(RM) *.diff
	$(RM) mini_mirror/setup-2.ini.sig 
	gpg -u "cyg-apt"  --output mini_mirror/setup-2.ini.sig --detach-sig mini_mirror/setup-2.ini
ifdef CYGAPT_TESTMIRROR
	bzip2 -k -c mini_mirror/setup-2.ini > mini_mirror/setup-2.bz2
	scp mini_mirror/setup-2.ini mini_mirror/setup-2.ini.sig mini_mirror/setup-2.bz2 $(CYGAPT_TESTMIRROR)
endif
	$(TOOLS)/hasfiles.py $(BUILDDIR)/root svn

install:
	$(CP) $(BUILDDIR)/release-2/cyg-apt/$(TARFILE) /
	cd /; tar -xf /$(TARFILE)
	/etc/postinstall/cyg-apt.sh
	$(MV) /etc/postinstall/cyg-apt.sh /etc/postinstall/cyg-apt.sh.done

testpackages:
	cd mini_mirror/testpkg/src/; make
	cd mini_mirror/testpkg-lib/src/; make

distclean: clean
	cd mini_mirror/testpkg/src/; make clean
	cd mini_mirror/testpkg-lib/src/; make clean

source: version-file
	mkdir -p build/cyg-apt-$(VERSION)
	tools/copy.py * -e build -d build/cyg-apt-$(VERSION)
	cd $(BUILDDIR); tar -jcf release-2/cyg-apt/$(SRCTARFILE) cyg-apt-$(VERSION) --exclude=".svn" --exclude="local_cache" --exclude="$(SRCTARFILE)"

version-file-clean:
	$(RM) $(VERSION_FILE)

clean: version-file-clean
	$(RM) $(BUILDDIR)/root/*.bz2
	$(RM) $(BUILDDIR)/release-2/cyg-apt/*
	$(RM) $(BUILDDIR)/setup-2.ini
	$(RM) $(BUILDDIR)/root/usr/bin/*
	$(RM) $(BUILDDIR)/root/etc/postinstall/*
	$(RM) $(BUILDDIR)/root/usr/share/cyg-apt/*
	$(RM) $(BUILDDIR)/root/usr/share/man/man1/cyg-apt/*
	$(TOOLS)/hasfiles.py $(BUILDDIR) svn
	$(RM) *.diff

.PHONY: version-file-clean
