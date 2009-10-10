BUILDDIR =  ../build
TARFILE = testpkg-0.0.1-0.tar.bz2
TOOLS = ../../../tools/

all:
	gcc testpkg.c -o $(BUILDDIR)/root/usr/bin/testpkg
	/usr/bin/cp postinstall-testpkg.sh $(BUILDDIR)/root/etc/postinstall/testpkg.sh
	/usr/bin/cp preremove-testpkg.sh $(BUILDDIR)/root/etc/preremove/testpkg.sh
	/usr/bin/cp postremove-testpkg.sh $(BUILDDIR)/root/etc/postremove/testpkg.sh
	cd $(BUILDDIR)/root ; pwd ; tar --exclude=".svn" -jcf $(TARFILE) *;\
cp $(TARFILE) ../release-2/testpkg;\
cp $(TARFILE) ../release-2/testpkg/testpkg-0.0.1-0-src.tar.bz2;\
cd ../../src;\
/usr/bin/cp ver2_marker $(BUILDDIR)/root/etc/;\
cd $(BUILDDIR)/root ; pwd ; tar --exclude=".svn" -jcf $(TARFILE) *;\
cp $(TARFILE) ../release-2/testpkg/testpkg-0.0.2-0.tar.bz2;\
rm etc/ver2_marker;\
/usr/bin/rm -rf $(TARFILE)
	cp ../../setup-2.ini ../build
	/usr/bin/cp setup.hint $(BUILDDIR)/release-2/testpkg
	$(TOOLS)md5.sum.py -f ../build/release-2/testpkg/ ../build/release-2/testpkg/md5.sum
	scp ../build/release-2/testpkg/* chrisc@wanda:~/public_html/release-2/testpkg
	scp ../build/setup-2.ini chrisc@wanda:~/public_html/

	$(TOOLS)setup_ini_diff_make.py ../../setup-2.ini testpkg install md5 --field-input=../build/release-2/testpkg/testpkg-0.0.1-0.tar.bz2
	patch ../../setup-2.ini setup-2.ini.diff

	$(TOOLS)setup_ini_diff_make.py ../../setup-2.ini testpkg source md5 --field-input=../build/release-2/testpkg/testpkg-0.0.1-0-src.tar.bz2
	patch ../../setup-2.ini setup-2.ini.diff

	$(TOOLS)setup_ini_diff_make.py ../../setup-2.ini testpkg install md5 --section=test --field-input=../build/release-2/testpkg/testpkg-0.0.2-0.tar.bz2
	patch ../../setup-2.ini setup-2.ini.diff


	scp ../../setup-2.ini chrisc@wanda:~/public_html/setup-2.ini
	/usr/bin/rm -rf testpkg-0.0.1-0-src.tar.bz2.diff
	/usr/bin/rm -rf setup-2.ini.diff
	/usr/bin/rm -rf testpkg-0.0.1-0.tar.bz2.diff	
	$(TOOLS)hasfiles.py ../build/root svn


clean:
	/usr/bin/rm -f ../build/release-2/testpkg/*
	/usr/bin/rm -f ../build/setup-2.ini
	/usr/bin/rm -f ../build/root/usr/bin/*
	/usr/bin/rm -f ../build/root/etc/ver2_marker
	/usr/bin/rm -f ../build/root/etc/postinstall/*
	/usr/bin/rm -f ../build/root/etc/preremove/*
	/usr/bin/rm -f ../build/root/etc/postremove/*
	$(TOOLS)hasfiles.py ../build svn
	/usr/bin/rm -f setup-2.ini.diff
