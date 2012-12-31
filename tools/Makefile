SRC = completion.bash
D_COMPLETION = bash_completion.d
D_BUILD = $(SD_BUILD)/$(ID_SYSCONF)/$(D_COMPLETION)
EXEC = $(EXENAME)

all:: $(D_BUILD)/$(EXEC)

$(D_BUILD):
	$(MKDIR) $(D_BUILD)

$(D_BUILD)/$(EXEC): $(SRC) $(D_BUILD)
	$(CP) "$<" "$@"

install: $(D_BUILD)/$(EXEC)
	$(INSTALL) -d -m 755 $(ID_ROOT)/$(ID_SYSCONF)/$(D_COMPLETION)
	$(INSTALL) -m 755 "$<" $(ID_ROOT)/$(ID_SYSCONF)/$(D_COMPLETION)

clean: FORCE


.PHONY: FORCE
.EXPORT_ALL_VARIABLES: