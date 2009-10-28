BUILDDIR =  build
TARFILE = cyg-apt-1.0.6-1.tar.bz2
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
	$(CP) postinstall-cyg-apt.sh $(BUILDDIR)/root/etc/postinstall/
	$(CP) cygwin.sig $(BUILDDIR)/root/usr/share/cyg-apt
	cd $(BUILDDIR)/root ; pwd ; tar --exclude=".svn" -jcf $(TARFILE) *;\
mv $(TARFILE) ../release-2/cyg-apt;
	$(CP) setup.hint $(BUILDDIR)/release-2/cyg-apt
	$(TOOLS)/md5.sum.py -f $(BUILDDIR)/release-2/cyg-apt/ $(BUILDDIR)/release-2/cyg-apt/md5.sum
	scp $(BUILDDIR)/release-2/cyg-apt/* chrisc@wanda:~/public_html/release-2/cyg-apt
	$(TOOLS)/setup_ini_diff_make.py mini_mirror/setup-2.ini cyg-apt install md5 --field-input=$(BUILDDIR)/release-2/cyg-apt/$(TARFILE)
	patch mini_mirror/setup-2.ini setup-2.ini.diff
	scp mini_mirror/setup-2.ini chrisc@wanda:~/public_html/setup-2.ini
	$(RM) *.diff
	$(RM) mini_mirror/setup-2.ini.sig 
	gpg -u "cyg-apt"  --output mini_mirror/setup-2.ini.sig --detach-sig mini_mirror/setup-2.ini
	scp mini_mirror/setup-2.ini mini_mirror/setup-2.ini.sig chrisc@wanda:~/public_html/
	$(TOOLS)/hasfiles.py $(BUILDDIR)/root svn

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