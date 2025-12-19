# jeopardy_game

Small FastAPI + PostgreSQL + SQLAlchemy API for a Jeopardy-like game.

Features:
- `GET /question/?round=Jeopardy!&value=$200` returns a random question
- `POST /verify-answer/` verifies a user answer (heuristic + optional OpenAI LLM)


## Repo structure
```
jeopardy_game/
  src/
    jeopardy_game/
        __init__.py
        main.py
        core/
          __init__.py
          config.py
          logging.py
        db/
          __init__.py
          base.py
          session.py
        models/
          __init__.py
          question.py
        schemas/
          __init__.py
          question.py
          verify.py
        services/
          __init__.py
          answer_checker.py
        api/
          __init__.py
          deps.py
          routes/
            __init__.py
            questions.py

  scripts/
    load_dataset.py              # reads CSV in assets/, inserts rows

  assets/                        # CSV files and other resources and assets live here
  tests/                         # optional
  docker-compose.yml             # postgres + api (later)
  pyproject.toml
  README.md
```

## Prerequisites

- Python 3.13+
- Docker + Docker Compose (recommended)
- `make` (optional)
- Dataset CSV at `assets/JEOPARDY_CSV.csv` (included in the repo for simplicity)

## Environment

Create a local `.env` file from the example and add your OpenAI key if you want LLM verification.

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY if you want LLM verification
````

Notes:

* `.env` must not be committed.
* If `OPENAI_API_KEY` is not set, the API will fall back to heuristic verification.


# 1) Run with Make (recommended)

From repo root:

```bash
cp .env.example .env
make up
```

Swagger UI:

* [http://localhost:8000/docs](http://localhost:8000/docs)

Run smoke requests (starts stack detached, waits for API, runs curl checks):

```bash
make smoke-up
```

Cleanup:

```bash
make smoke-clean
```

# 2) Run with Docker Compose (no Make)

From repo root:

```bash
cp .env.example .env
docker compose up --build
```

Swagger UI:

* [http://localhost:8000/docs](http://localhost:8000/docs)

To stop:

```bash
docker compose down
```

To wipe the DB volume (fresh load next time):

```bash
docker compose down -v
```

How it works:

* `postgres` starts
* `loader` initializes schema and loads `assets/JEOPARDY_CSV.csv` (value <= 1200), then exits
* `api` starts after `loader` completes successfully

# 3) Pure local (no Docker)

This runs the API in a venv on your host and assumes you have a reachable Postgres instance.

## 3.1 Create and install venv

```bash
mkdir -p ~/venvs
python3.13 -m venv ~/venvs/jeopardy_game
source ~/venvs/jeopardy_game/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -r src/jeopardy_game/requirements.txt
```

## 3.2 Start Postgres (choose one)

### Option A: Local Postgres (already installed)

Create DB/user as you prefer and set `DATABASE_URL`.

### Option B: Postgres via Docker (only DB in Docker)

```bash
docker run --rm -d \
  --name jeopardy-postgres \
  -e POSTGRES_USER=jeopardy \
  -e POSTGRES_PASSWORD=jeopardy \
  -e POSTGRES_DB=jeopardy \
  -p 5432:5432 \
  postgres:16
```

## 3.3 Load dataset

Ensure the dataset exists at `assets/JEOPARDY_CSV.csv`, then:

```bash
export DATABASE_URL="postgresql+psycopg://jeopardy:jeopardy@localhost:5432/jeopardy"
export JEP_CSV_PATH="assets/JEOPARDY_CSV.csv"
export JEP_MAX_VALUE="1200"

PYTHONPATH="$PWD/src" python scripts/load_dataset.py
```

## 3.4 Run API locally

```bash
export DATABASE_URL="postgresql+psycopg://jeopardy:jeopardy@localhost:5432/jeopardy"
export OPENAI_API_KEY="..."         # optional
export OPENAI_MODEL="gpt-4o-mini"   # optional

PYTHONPATH="$PWD/src" uvicorn jeopardy_game.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI:

* [http://localhost:8000/docs](http://localhost:8000/docs)


