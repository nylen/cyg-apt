EXEC = cyg-apt
VERSION = v1.0.9
VERSION_FILE = VERSION-FILE
SRC = cyg-apt
GPG_CYGWIN_PUBKEY = cygwin.sig

# The default target of this Makefile is...
all: $(EXEC)

ifndef SHELL_PATH
	SHELL_PATH = /bin/sh
endif

$(VERSION_FILE): FORCE
	@$(SHELL_PATH) ./VERSION-GEN
-include $(VERSION_FILE)
    
PREFIX = /usr
BUILDDIR = build

CP = /usr/bin/cp -f
RM = /usr/bin/rm -f --preserve-root
MV = /usr/bin/mv
MKDIR = /usr/bin/mkdir -p
GZIP = /usr/bin/gzip

version-file-clean: 
	$(RM) $(VERSION_FILE)

$(EXEC)-skel: 
	$(MKDIR) $(BUILDDIR)/root$(PREFIX)/bin
	$(MKDIR) $(BUILDDIR)/root/etc/postinstall
	$(MKDIR) $(BUILDDIR)/root$(PREFIX)/share/man/man1
	$(MKDIR) $(BUILDDIR)/root/etc/bash_completion.d
	$(MKDIR) $(BUILDDIR)/root$(PREFIX)/share/$(EXEC)

$(EXEC): $(EXEC)-skel
	$(CP) $(SRC) $(BUILDDIR)/root$(PREFIX)/bin/$(EXEC)
	@$(SHELL_PATH) ./$(SRC)-postinstall-gen.sh > $(BUILDDIR)/root/etc/postinstall/$(EXEC).sh
	$(GZIP) -c $(SRC).1 > $(BUILDDIR)/root$(PREFIX)/share/man/man1/$(EXEC).1.gz
	$(CP) $(SRC).bash_completion $(BUILDDIR)/root/etc/bash_completion.d/$(EXEC)
	$(CP) $(GPG_CYGWIN_PUBKEY) $(BUILDDIR)/root$(PREFIX)/share/$(EXEC)/$(GPG_CYGWIN_PUBKEY)

$(EXEC)-install: $(EXEC)
	install $(BUILDDIR)/root$(PREFIX)/bin/$(EXEC) $(PREFIX)/bin
	install $(BUILDDIR)/root/etc/postinstall/$(EXEC).sh /etc/postinstall
	install $(BUILDDIR)/root$(PREFIX)/share/man/man1/$(EXEC).1.gz $(PREFIX)/share/man/man1
	install $(BUILDDIR)/root/etc/bash_completion.d/$(EXEC) /etc/bash_completion.d
	install $(BUILDDIR)/root$(PREFIX)/share/$(EXEC)/$(GPG_CYGWIN_PUBKEY) $(PREFIX)/share/$(EXEC)
	/etc/postinstall/$(EXEC).sh
	$(MV) /etc/postinstall/$(EXEC).sh /etc/postinstall/$(EXEC).sh.done

install: $(EXEC)-install

$(EXEC)-package: $(VERSION_FILE) $(EXEC)
	$(MKDIR) $(BUILDDIR)/$(EXEC)-$(VERSION)
	cd $(BUILDDIR)/root ; pwd ; tar -jcf ../$(EXEC)-$(VERSION)/$(EXEC)-$(VERSION).tar.bz2 *
	git archive --prefix="$(EXEC)-$(VERSION)/" --format=tar HEAD | bzip2 -c > $(BUILDDIR)/$(EXEC)-$(VERSION)/$(EXEC)-$(VERSION)-src.tar.bz2

package: $(VERSION_FILE) $(EXEC)-package

.PHONY: $(EXEC)-clean clean mrproper version-file-clean FORCE

$(EXEC)-clean: 
	$(RM) $(BUILDDIR)/root$(PREFIX)/bin/*
	$(RM) $(BUILDDIR)/root/etc/postinstall/*
	$(RM) $(BUILDDIR)/root$(PREFIX)/share/man/man1/*
	$(RM) $(BUILDDIR)/root/etc/bash_completion.d/*
	$(RM) $(BUILDDIR)/root$(PREFIX)/share/$(EXEC)/*

clean: $(EXEC)-clean version-file-clean

mrproper: clean
	$(RM) -r $(BUILDDIR)
