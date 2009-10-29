BUILDDIR= ../build
TARFILE = testpkg-0.0.1-0.tar.bz2
TOOLS = ../../../tools/
CP = /usr/bin/cp -f
CC = gcc
RM = /usr/bin/rm -rf

all:
	$(CC) testpkg.c -o $(BUILDDIR)/root/usr/bin/testpkg
	$(CP) postinstall-testpkg.sh $(BUILDDIR)/root/etc/postinstall/testpkg.sh
	$(CP) preremove-testpkg.sh $(BUILDDIR)/root/etc/preremove/testpkg.sh
	$(CP) postremove-testpkg.sh $(BUILDDIR)/root/etc/postremove/testpkg.sh
	cd $(BUILDDIR)/root/usr/bin ; ln -sf testpkg.exe link_to_testpkg.exe; ln -f testpkg.exe hardlink_to_testpkg.exe
	cd $(BUILDDIR)/root ; pwd ; tar --exclude=".svn" -jcf $(TARFILE) *;\
$(CP) $(TARFILE) ../release-2/testpkg;\
$(CP) $(TARFILE) ../release-2/testpkg/testpkg-0.0.1-0-src.tar.bz2;\
cd ../../src;\
$(CP) ver2_marker $(BUILDDIR)/root/etc/;\
cd $(BUILDDIR)/root ; pwd ; tar --exclude=".svn" -jcf $(TARFILE) *;\
$(CP) $(TARFILE) ../release-2/testpkg/testpkg-0.0.2-0.tar.bz2;\
rm etc/ver2_marker;\
/usr/bin/rm -rf $(TARFILE)
	$(CP) ../../setup-2.ini $(BUILDDIR)/
	$(CP) setup.hint $(BUILDDIR)/release-2/testpkg
	$(TOOLS)md5.sum.py -f $(BUILDDIR)/release-2/testpkg/ $(BUILDDIR)/release-2/testpkg/md5.sum
ifdef CYGAPT_TESTMIRROR
	scp $(BUILDDIR)/release-2/testpkg/* $(CYGAPT_TESTMIRROR)/release-2/testpkg
	scp $(BUILDDIR)/setup-2.ini $(CYGAPT_TESTMIRROR)
endif # CYGAPT_TESTMIRROR
	$(TOOLS)setup_ini_diff_make.py ../../setup-2.ini testpkg install md5 --field-input=$(BUILDDIR)/release-2/testpkg/testpkg-0.0.1-0.tar.bz2
	patch ../../setup-2.ini setup-2.ini.diff

	$(TOOLS)setup_ini_diff_make.py ../../setup-2.ini testpkg source md5 --field-input=$(BUILDDIR)/release-2/testpkg/testpkg-0.0.1-0-src.tar.bz2
	patch ../../setup-2.ini setup-2.ini.diff

	$(TOOLS)setup_ini_diff_make.py ../../setup-2.ini testpkg install md5 --section=test --field-input=$(BUILDDIR)/release-2/testpkg/testpkg-0.0.2-0.tar.bz2
	patch ../../setup-2.ini setup-2.ini.diff

	/usr/bin/rm -f ../../setup-2.ini.sig 
	gpg -u "cyg-apt"  --output ../../setup-2.ini.sig --detach-sig ../../setup-2.ini
ifdef CYGAPT_TESTMIRROR
	scp ../../setup-2.ini ../../setup-2.ini.sig $(CYGAPT_TESTMIRROR)
endif # CYGAPT_TESTMIRROR
	$(RM) testpkg-0.0.1-0-src.tar.bz2.diff
	$(RM) setup-2.ini.diff
	$(RM) testpkg-0.0.1-0.tar.bz2.diff	
	$(TOOLS)hasfiles.py $(BUILDDIR)/root svn


clean:
	$(RM) $(BUILDDIR)/release-2/testpkg/*
	$(RM) $(BUILDDIR)/setup-2.ini
	$(RM) $(BUILDDIR)/root/usr/bin/*
	$(RM) $(BUILDDIR)/root/etc/ver2_marker
	$(RM) $(BUILDDIR)/root/etc/postinstall/*
	$(RM) $(BUILDDIR)/root/etc/preremove/*
	$(RM) $(BUILDDIR)/root/etc/postremove/*
	$(TOOLS)hasfiles.py $(BUILDDIR) svn
	$(RM) setup-2.ini.diff
