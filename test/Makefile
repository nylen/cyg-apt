all:: sourcetest

TEST_SCRIPT = -m cygapt.test.__main__
ARGUMENTS =
ARGUMENTS += -v

# Print a warning each time it occurs, used for deprecation tests
# see https://docs.python.org/2/using/cmdline.html#cmdoption-W
PYTHON += -Wall

sourcetest: FORCE
	cd $(SD_SRC); $(PYTHON) $(TEST_SCRIPT) $(ARGUMENTS)

installtest: FORCE
	@$(PYTHON) $(TEST_SCRIPT) $(ARGUMENTS)

clean: FORCE


.PHONY: FORCE
.EXPORT_ALL_VARIABLES:
