SRC = main.py
D_BUILD = $(SD_BUILD)/$(ID_EXEC)
EXEC = $(EXENAME)
PYPKG = cygapt
SRCLIB = $(wildcard $(PYPKG)/*.py)

GPG_CYGWIN_PUBKEY = cygwin.sig

all:: $(D_BUILD)/$(EXEC)

$(D_BUILD):
	$(MKDIR) $(D_BUILD)
	$(MKDIR) $(SD_BUILD)/$(ID_SYSCONF)/postinstall
	$(MKDIR) $(SD_BUILD)/$(ID_DATA)/$(EXENAME)

$(D_BUILD)/$(EXEC): $(SRC) $(D_BUILD) $(SRCLIB)
	$(SHELL_PATH) ./postinstall-gen.sh > $(SD_BUILD)/$(ID_SYSCONF)/postinstall/$(EXENAME).sh
	$(PYTHON) setup.py bdist --format=tar --plat-name=""
	$(TAR) -C $(SD_BUILD) -xf dist/$(PYPKG)-$(VERSION)..tar
	$(CP) $(GPG_CYGWIN_PUBKEY) $(SD_BUILD)/$(ID_DATA)/$(EXENAME)
	$(CP) $< $@

install: $(D_BUILD)/$(EXEC)
	$(INSTALL) -d -m 755 $(ID_ROOT)/$(ID_DATA)/$(EXENAME)
	$(INSTALL) $(GPG_CYGWIN_PUBKEY) $(ID_ROOT)/$(ID_DATA)/$(EXENAME)
	$(INSTALL) -m 755 $< $(ID_ROOT)/$(ID_EXEC)
	$(PYTHON) setup.py install
	$(INSTALL) $(SD_BUILD)/$(ID_SYSCONF)/postinstall/$(EXENAME).sh $(ID_ROOT)/$(ID_SYSCONF)/postinstall
	$(SHELL_PATH) $(ID_ROOT)/$(ID_SYSCONF)/postinstall/$(EXENAME).sh
	$(MV) $(ID_ROOT)/$(ID_SYSCONF)/postinstall/$(EXENAME).sh $(ID_ROOT)/$(ID_SYSCONF)/postinstall/$(EXENAME).sh.done

clean: FORCE
	$(PYTHON) setup.py clean
	$(RM) -r build dist

.PHONY: FORCE
.EXPORT_ALL_VARIABLES: