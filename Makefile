VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
MANAGE := $(PYTHON) manage.py

DEV_ACCESS_KEY ?= local-secret-key
RUNSERVER_ADDRESS ?= 127.0.0.1:8000

VALID_DEV_PHASES := pre live post closed
REQUESTED_DEV_PHASE := $(filter $(VALID_DEV_PHASES),$(MAKECMDGOALS))
DEV_PHASE ?= $(if $(REQUESTED_DEV_PHASE),$(firstword $(REQUESTED_DEV_PHASE)),live)


.PHONY: help venv install setup \
	run devrun \
	pre live post closed \
	check test \
	migrate makemigrations showmigrations \
	superuser shell devshell \
	clean


help:
	@echo "Available commands:"
	@echo ""
	@echo "  make setup                 Install project and run migrations"
	@echo "  make install               Install project in editable mode"
	@echo "  make run                   Start server without development access"
	@echo "  make devrun                Start server in the live phase"
	@echo "  make devrun pre            Start server in the pre phase"
	@echo "  make devrun live           Start server in the live phase"
	@echo "  make devrun post           Start server in the post phase"
	@echo "  make devrun closed         Start server in the closed phase"
	@echo "  make check                 Run Django system checks"
	@echo "  make test                  Run automated tests"
	@echo "  make migrate               Apply database migrations"
	@echo "  make makemigrations        Create database migrations"
	@echo "  make showmigrations        Show migration status"
	@echo "  make superuser             Create an admin user"
	@echo "  make shell                 Open the Django shell"
	@echo "  make devshell              Open a development Django shell"
	@echo "  make clean                 Remove generated Python files"
	@echo ""
	@echo "Default development access URL:"
	@echo "  http://$(RUNSERVER_ADDRESS)/join/$(DEV_ACCESS_KEY)/"


venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip


install:
	$(PIP) install -e .


setup: install migrate


run:
	$(MANAGE) runserver $(RUNSERVER_ADDRESS)


devrun:
	@if ! echo "$(VALID_DEV_PHASES)" | grep -qw "$(DEV_PHASE)"; then \
		echo "Invalid development phase: $(DEV_PHASE)"; \
		echo "Choose one of: $(VALID_DEV_PHASES)"; \
		exit 1; \
	fi
	@echo "Starting guestbook development server"
	@echo "Phase:      $(DEV_PHASE)"
	@echo "Read URL:   http://$(RUNSERVER_ADDRESS)/"
	@echo "Access URL: http://$(RUNSERVER_ADDRESS)/join/$(DEV_ACCESS_KEY)/"
	@echo ""
	GUESTBOOK_ACCESS_KEY="$(DEV_ACCESS_KEY)" \
	GUESTBOOK_DEV_PHASE="$(DEV_PHASE)" \
		$(MANAGE) runserver $(RUNSERVER_ADDRESS)


pre live post closed:
	@:


check:
	$(MANAGE) check


test:
	$(MANAGE) test


migrate:
	$(MANAGE) migrate


makemigrations:
	$(MANAGE) makemigrations


showmigrations:
	$(MANAGE) showmigrations


superuser:
	$(MANAGE) createsuperuser


shell:
	$(MANAGE) shell


devshell:
	GUESTBOOK_ACCESS_KEY="$(DEV_ACCESS_KEY)" \
	GUESTBOOK_DEV_PHASE="$(DEV_PHASE)" \
		$(MANAGE) shell


clean:
	find . -type d -name "__pycache__" \
		-prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" \
		-prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" \
		-prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" \
		-prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" \
		-prune -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
