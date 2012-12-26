SRC = $(wildcard *.1)
D_BUILD = $(SD_BUILD)/$(ID_MAN)
D_MAN1 = man1
MAN1 = $(D_MAN1)/$(EXENAME).1.gz

all:: $(D_BUILD)/$(MAN1)

$(D_BUILD):
	$(MKDIR) $(D_BUILD)/$(D_MAN1)

$(D_BUILD)/$(MAN1): $(SRC) $(D_BUILD)
	$(GZ) -c $< > $@
	$(GZ) -t $@

install: $(D_BUILD)/$(MAN1)
	$(INSTALL) $< $(ID_ROOT)/$(ID_MAN)/$(D_MAN1)

clean: FORCE


.PHONY: FORCE
.EXPORT_ALL_VARIABLES: