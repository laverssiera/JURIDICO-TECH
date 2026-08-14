SHELL := /usr/bin/env bash

PROFILE_SCRIPT := ./scripts/switch_federation_profile.sh

.PHONY: help \
	profile-local \
	profile-auto \
	profile-real \
	profile-local-dry-run \
	profile-auto-dry-run \
	profile-real-dry-run

help:
	@echo "Targets disponiveis:"
	@echo "  make profile-local"
	@echo "  make profile-auto"
	@echo "  make profile-real"
	@echo "  make profile-local-dry-run"
	@echo "  make profile-auto-dry-run"
	@echo "  make profile-real-dry-run"

profile-local:
	@$(PROFILE_SCRIPT) local

profile-auto:
	@$(PROFILE_SCRIPT) auto

profile-real:
	@$(PROFILE_SCRIPT) real

profile-local-dry-run:
	@$(PROFILE_SCRIPT) local --dry-run

profile-auto-dry-run:
	@$(PROFILE_SCRIPT) auto --dry-run

profile-real-dry-run:
	@$(PROFILE_SCRIPT) real --dry-run
