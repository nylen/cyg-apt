all:: sourcetest

TEST_SCRIPT = -m cygapt.test.__main__
ARGUMENTS =
ARGUMENTS += -v

sourcetest: FORCE
	@export PYTHONPATH="$(subst \,,$(SD_SRC)):$(PYTHONPATH)";\
$(PYTHON) $(TEST_SCRIPT) $(ARGUMENTS)

installtest: FORCE
	@$(PYTHON) $(TEST_SCRIPT) $(ARGUMENTS)

clean: FORCE


.PHONY: FORCE
.EXPORT_ALL_VARIABLES:
