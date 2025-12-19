# Makefile (repo root)

VENV_DIR := $(HOME)/venvs/jeopardy_game
PYTHON   := python3.13
PIP      := $(VENV_DIR)/bin/pip

REQS     := src/jeopardy_game/requirements.txt

COMPOSE  := docker compose

.PHONY: help venv install run up down reset logs ps

help:
	@echo "make venv     - create venv at $(VENV_DIR) (if missing)"
	@echo "make install  - install Python deps into venv from $(REQS)"
	@echo "make run      - run API locally (requires DATABASE_URL set)"
	@echo "make up       - docker compose up --build (postgres + loader + api)"
	@echo "make down     - docker compose down"
	@echo "make reset    - docker compose down -v (wipes DB volume)"
	@echo "make logs     - docker compose logs -f"
	@echo "make ps       - docker compose ps"

venv:
	@mkdir -p $(HOME)/venvs
	@[ -d "$(VENV_DIR)" ] || ($(PYTHON) -m venv "$(VENV_DIR)")
	@echo "Venv ready: $(VENV_DIR)"

install: venv
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install -r $(REQS)
	@echo "Installed requirements from $(REQS)"

run: install
	@echo "Starting API locally (ensure DATABASE_URL is set)..."
	@PYTHONPATH="$(PWD)/src" "$(VENV_DIR)/bin/uvicorn" jeopardy_game.main:app --reload --host 0.0.0.0 --port 8000

up:
	@$(COMPOSE) up --build

down:
	@$(COMPOSE) down

reset:
	@$(COMPOSE) down -v

logs:
	@$(COMPOSE) logs -f

ps:
	@$(COMPOSE) ps
