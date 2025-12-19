# Makefile (repo root)

VENV_DIR := $(HOME)/venvs/jeopardy_game
PYTHON   := python3.13
PIP      := $(VENV_DIR)/bin/pip

REQS     := src/jeopardy_game/requirements.txt

COMPOSE  := docker compose

.PHONY: help venv install run up up-d down reset logs ps smoke smoke-up

help:
	@echo "make venv      	 - create venv at $(VENV_DIR) (if missing)"
	@echo "make install   	 - install Python deps into venv from $(REQS)"
	@echo "make run       	 - run API locally (requires DATABASE_URL set)"
	@echo "make up        	 - docker compose up --build (attached)"
	@echo "make up-d      	 - docker compose up -d --build (detached)"
	@echo "make down      	 - docker compose down"
	@echo "make reset     	 - docker compose down -v (wipes DB volume)"
	@echo "make logs      	 - docker compose logs -f"
	@echo "make ps        	 - docker compose ps"
	@echo "make smoke     	 - run smoke curls against localhost:8000 (requires API up)"
	@echo "make smoke-up  	 - up-d then run smoke"
	@echo "make smoke-clean  - teardown smoke test environment and clean DB"

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

up-d:
	@$(COMPOSE) up -d --build

down:
	@$(COMPOSE) down

reset:
	@$(COMPOSE) down -v

logs:
	@$(COMPOSE) logs -f

ps:
	@$(COMPOSE) ps

smoke:
	@echo "Running smoke tests against http://localhost:8000 ..."
	@set -e; \
	echo "Waiting for API to be ready..."; \
	for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do \
	  if curl -fsS "http://localhost:8000/openapi.json" >/dev/null 2>&1; then \
	    echo "API is up."; \
	    break; \
	  fi; \
	  sleep 1; \
	done; \
	echo ""; \
	echo "1) Copernics"; \
	curl -s -X POST "http://localhost:8000/verify-answer/" \
	  -H "Content-Type: application/json" \
	  -d '{"question_id": 1, "user_answer": "Copernics"}' ; \
	echo ""; \
	echo ""; \
	echo "2) Coperniadawdacs"; \
	curl -s -X POST "http://localhost:8000/verify-answer/" \
	  -H "Content-Type: application/json" \
	  -d '{"question_id": 1, "user_answer": "Coperniadawdacs"}' ; \
	echo ""; \
	echo ""; \
	echo "3) Copernicuses"; \
	curl -s -X POST "http://localhost:8000/verify-answer/" \
	  -H "Content-Type: application/json" \
	  -d '{"question_id": 1, "user_answer": "Copernicuses"}' ; \
	echo ""; \
	echo ""; \
	echo "4) Copper guy from Medieval Europe"; \
	curl -s -X POST "http://localhost:8000/verify-answer/" \
	  -H "Content-Type: application/json" \
	  -d '{"question_id": 1, "user_answer": "Copper guy from Medieval Europe"}' ; \
	echo ""; \
	echo ""; \
	echo "5) Copper guy astronomer"; \
	curl -s -X POST "http://localhost:8000/verify-answer/" \
	  -H "Content-Type: application/json" \
	  -d '{"question_id": 1, "user_answer": "Copper guy astronomer"}' ; \
	echo ""; \
	echo ""; \
	echo "Done."

smoke-up: up-d
	@$(MAKE) smoke


.PHONY: smoke-clean
smoke-clean:
	@$(COMPOSE) down -v


.PHONY: test
test: install
	@$(VENV_DIR)/bin/pytest -q
