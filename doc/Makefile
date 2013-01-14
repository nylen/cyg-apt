SRC = $(wildcard *.1)
D_BUILD = $(SD_BUILD)/$(ID_MAN)
D_MAN1 = man1
MAN1 = $(D_MAN1)/$(EXENAME).1.gz
D_DOC = $(SD_BUILD)/$(ID_DATA)/doc/$(EXENAME)
ID_DOC = $(ID_ROOT)/$(ID_DATA)/doc/$(EXENAME)

INSTALL_DOCS =
INSTALL_DOCS += ../COPYING
INSTALL_DOCS += ../LICENSE
INSTALL_DOCS += ../README.md
INSTALL_DOCS += ../ChangeLog

all:: $(D_BUILD)/$(MAN1) doc

$(D_BUILD):
	$(MKDIR) $(D_BUILD)/$(D_MAN1)

$(D_BUILD)/$(MAN1): $(SRC) $(D_BUILD)
	$(GZ) -c "$<" > "$@"
	$(GZ) -t "$@"

doc: $(INSTALL_DOCS)
	@$(MKDIR) $(D_DOC)
	$(CP) $^ $(D_DOC)

doc-install: doc
	$(CP) -r $(D_DOC) $(ID_DOC)

install: $(D_BUILD)/$(MAN1) doc-install
	$(INSTALL) "$<" $(ID_ROOT)/$(ID_MAN)/$(D_MAN1)

clean: FORCE


.PHONY: FORCE
.EXPORT_ALL_VARIABLES: