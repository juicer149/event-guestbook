PYTHON := .venv/bin/python
PIP := .venv/bin/pip
MANAGE := $(PYTHON) manage.py

.PHONY: help venv install setup run check migrate makemigrations \
	superuser shell test test-v clean

help:
	@echo "Event Guestbook commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install         Install project dependencies"
	@echo "  make setup           Create venv, install dependencies, migrate"
	@echo ""
	@echo "Django:"
	@echo "  make run             Run development server"
	@echo "  make check           Run Django system checks"
	@echo "  make migrate         Apply migrations"
	@echo "  make makemigrations  Create migrations"
	@echo "  make superuser       Create Django superuser"
	@echo "  make shell           Run Django shell"
	@echo ""
	@echo "Tests:"
	@echo "  make test            Run tests"
	@echo "  make test-v          Run verbose tests"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           Remove generated caches and build metadata"

venv:
	@test -x $(PYTHON) || python3 -m venv .venv

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -e .

setup: install migrate

run:
	$(MANAGE) runserver

check:
	$(MANAGE) check

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

superuser:
	$(MANAGE) createsuperuser

shell:
	$(MANAGE) shell

test:
	$(MANAGE) test

test-v:
	$(MANAGE) test --verbosity=2

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
