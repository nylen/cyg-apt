SRC = main.py
D_BUILD = $(SD_BUILD)/$(ID_EXEC)
EXEC = $(EXENAME)
PYPKG = cygapt
PY_VERSION_FILE = $(PYPKG)/version.py
SRCLIB = $(wildcard $(PYPKG)/*.py)

GPG_CYGWIN_PUBKEY = cygwin.sig

all:: $(D_BUILD)/$(EXEC)

$(D_BUILD):
	$(MKDIR) $(D_BUILD)
	$(MKDIR) $(SD_BUILD)/$(ID_SYSCONF)/postinstall
	$(MKDIR) $(SD_BUILD)/$(ID_DATA)/$(EXENAME)

$(D_BUILD)/$(EXEC): $(SRC) $(SRCLIB) $(D_BUILD)
	$(SHELL_PATH) ./postinstall-gen.sh > $(SD_BUILD)/$(ID_SYSCONF)/postinstall/$(EXENAME).sh
	$(CP) $(SD_ROOT)/LICENSE $(PYPKG)
	@echo "__version__ = '$(VERSION)'" > $(PY_VERSION_FILE)
	$(PYTHON) setup.py bdist --format=tar --plat-name=""
	$(RM) $(PYPKG)/LICENSE
	$(TAR) -C $(SD_BUILD) -xf dist/$(PYPKG)-$(VERSION)..tar
	$(CP) $(GPG_CYGWIN_PUBKEY) $(SD_BUILD)/$(ID_DATA)/$(EXENAME)
	$(CP) "$<" "$@"

install: $(D_BUILD)/$(EXEC)
	$(INSTALL) -d -m 755 $(ID_ROOT)/$(ID_DATA)/$(EXENAME)
	$(INSTALL) $(GPG_CYGWIN_PUBKEY) $(ID_ROOT)/$(ID_DATA)/$(EXENAME)
	$(INSTALL) -m 755 "$<" $(ID_ROOT)/$(ID_EXEC)
	$(PYTHON) setup.py install
	$(INSTALL) $(SD_BUILD)/$(ID_SYSCONF)/postinstall/$(EXENAME).sh $(ID_ROOT)/$(ID_SYSCONF)/postinstall
	$(SHELL_PATH) $(ID_ROOT)/$(ID_SYSCONF)/postinstall/$(EXENAME).sh
	$(MV) $(ID_ROOT)/$(ID_SYSCONF)/postinstall/$(EXENAME).sh $(ID_ROOT)/$(ID_SYSCONF)/postinstall/$(EXENAME).sh.done

clean: FORCE
	$(PYTHON) setup.py clean
	$(RM) -r build dist $(PY_VERSION_FILE)

.PHONY: FORCE
.EXPORT_ALL_VARIABLES:
