PYTHON := .venv/bin/python
PIP := .venv/bin/pip
MANAGE := $(PYTHON) manage.py

VENV := .venv
ENV_FILE ?= .env

VALID_DEV_PHASES := closed pre live post archived
PHASE := $(word 2,$(MAKECMDGOALS))


.PHONY: help \
	venv install setup \
	run devrun \
	closed pre live post archived \
	check test verify \
	migrate makemigrations showmigrations \
	superuser shell devshell \
	collectstatic \
	clean


help:
	@echo ""
	@echo "Event Guestbook"
	@echo ""
	@echo "Setup"
	@echo "  make setup                 Create venv, install packages and migrate"
	@echo "  make venv                  Create the virtual environment"
	@echo "  make install               Install dependencies"
	@echo ""
	@echo "Development"
	@echo "  make run                   Start server using configured event dates"
	@echo "  make devrun                Start server using configured event dates"
	@echo "  make devrun closed         Simulate CLOSED phase"
	@echo "  make devrun pre            Simulate PRE phase"
	@echo "  make devrun live           Simulate LIVE phase"
	@echo "  make devrun post           Simulate POST phase"
	@echo "  make devrun archived       Simulate ARCHIVED phase"
	@echo ""
	@echo "Quality"
	@echo "  make check                 Run Django system checks"
	@echo "  make test                  Run the test suite"
	@echo "  make verify                Check migrations and run all tests"
	@echo ""
	@echo "Database"
	@echo "  make makemigrations        Create Django migrations"
	@echo "  make migrate               Apply Django migrations"
	@echo "  make showmigrations        Show migration status"
	@echo ""
	@echo "Utilities"
	@echo "  make superuser             Create a Django administrator"
	@echo "  make shell                 Open the Django shell"
	@echo "  make devshell              Open a normal Python shell"
	@echo "  make collectstatic         Collect static files"
	@echo "  make clean                 Remove Python cache files"
	@echo ""
	@echo "Environment"
	@echo "  Commands load variables from $(ENV_FILE) when it exists."
	@echo "  Override with: make run ENV_FILE=.env.local"
	@echo ""


venv:
	@test -d $(VENV) || python3 -m venv $(VENV)


install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt


setup: install migrate
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) check


run:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) runserver


devrun:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	if [ -z "$(PHASE)" ]; then \
		$(MANAGE) runserver; \
	elif printf '%s\n' $(VALID_DEV_PHASES) | grep -qx "$(PHASE)"; then \
		GUESTBOOK_DEV_PHASE="$(PHASE)" \
		$(MANAGE) runserver; \
	else \
		echo "Invalid phase: $(PHASE)"; \
		echo "Valid phases: $(VALID_DEV_PHASES)"; \
		exit 1; \
	fi


closed pre live post archived:
	@:


check:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) check


test:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) test


verify:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) check; \
	$(MANAGE) makemigrations --check --dry-run; \
	$(MANAGE) test


makemigrations:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) makemigrations


migrate:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) migrate


showmigrations:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) showmigrations


superuser:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) createsuperuser


shell:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) shell


devshell:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(PYTHON)


collectstatic:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then \
		. "$(ENV_FILE)"; \
	fi; \
	set +a; \
	$(MANAGE) collectstatic --noinput


clean:
	find . \
		-type d \
		-name "__pycache__" \
		-prune \
		-exec rm -rf {} +

	find . \
		-type f \
		-name "*.py[co]" \
		-delete

	find . \
		-type d \
		-name ".pytest_cache" \
		-prune \
		-exec rm -rf {} +

	find . \
		-type d \
		-name ".mypy_cache" \
		-prune \
		-exec rm -rf {} +
