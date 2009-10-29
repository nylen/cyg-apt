BUILDDIR =  build
TARFILE = cyg-apt-1.0.6-1.tar.bz2
SRCTARFILE = cyg-apt-1.0.6-1-src.tar.bz2
TOOLS = tools
CP = /usr/bin/cp -f
RM = /usr/bin/rm -f
MV = /usr/bin/mv
GZIP = /usr/bin/gzip
TMP = tmp

all:
	$(CP) cyg-apt $(BUILDDIR)/root/usr/bin
	$(GZIP) -c cyg-apt.1 > cyg-apt.1.gz
	$(MV) cyg-apt.1.gz $(BUILDDIR)/root/usr/share/man/man1/cyg-apt/
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
	scp mini_mirror/setup-2.ini mini_mirror/setup-2.ini.sig $(CYGAPT_TESTMIRROR)
endif
	$(TOOLS)/hasfiles.py $(BUILDDIR)/root svn


testpackages:
	cd mini_mirror/testpkg/src/; make
	cd mini_mirror/testpkg-lib/src/; make

distclean: clean
	cd mini_mirror/testpkg/src/; make clean
	cd mini_mirror/testpkg-lib/src/; make clean

source:
	tar -jcf $(BUILDDIR)/release-2/cyg-apt/$(SRCTARFILE) . --exclude=".svn" --exclude="local_cache" --exclude="$(SRCTARFILE)"

clean:
	$(RM) $(BUILDDIR)/root/*.bz2
	$(RM) $(BUILDDIR)/release-2/cyg-apt/*
	$(RM) $(BUILDDIR)/setup-2.ini
	$(RM) $(BUILDDIR)/root/usr/bin/*
	$(RM) $(BUILDDIR)/root/etc/postinstall/*
	$(RM) $(BUILDDIR)/root/usr/share/cyg-apt/*
	$(RM) $(BUILDDIR)/root/usr/share/man/man1/cyg-apt/*
	$(TOOLS)/hasfiles.py $(BUILDDIR) svn
	$(RM) *.diff