PYTHON ?= python3
PROFILE ?=

.PHONY: install uninstall help check-profile

help:
	@printf '%s\n' 'Targets:' '  make install PROFILE="/path/to/profile"   Install the mod' '  make uninstall PROFILE="/path/to/profile" Remove the mod' '' 'Find your profile directory via about:support in Zen (see README.md).'

check-profile:
	@test -n "$(strip $(PROFILE))" || { printf '%s\n' 'Error: PROFILE is required. Find your profile directory via about:support in Zen.' 'Usage: make install PROFILE="/full/path/to/profile"' >&2; exit 1; }

install: check-profile
	@$(PYTHON) install.py install --profile "$(PROFILE)"

uninstall: check-profile
	@$(PYTHON) install.py uninstall --profile "$(PROFILE)"
