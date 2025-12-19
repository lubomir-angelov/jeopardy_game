# jeopardy_game
Test repo for a small backend for playing jeopardy like game

# Repo structure
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

# Local setup - Jeopardy Game API

Small FastAPI + PostgreSQL + SQLAlchemy API that:
- Returns a random Jeopardy question filtered by `round` and `value`
- Verifies a user’s answer against the stored correct answer (tolerant to minor typos)

## Requirements
- Python 3.13+
- PostgreSQL 14+ (local or Docker)
- `pip`
- make (optional)
- Docker & docker-compose
- The JEOPARDY_CSV.csv files is added to the assets/ folder

## Environment variables
The API expects a database URL via `DATABASE_URL`.

Example:
```bash
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/jeopardy"
```

## Initial Setup (without Makefile and make)

```bash
# 1) Create venv folder if needed
mkdir -p ~/venvs

# 2) Create venv
python3 -m venv ~/venvs/jeopardy_game

# 3) Activate venv
source ~/venvs/jeopardy_game/bin/activate

# 4) Upgrade pip tooling
python -m pip install --upgrade pip setuptools wheel

# 5) Install dependencies
pip install -r requirements.txt
```

## Run PostgreSQL (example)

Create a local database named jeopardy and ensure your DATABASE_URL points to it.

Example using psql:

```bash
createdb jeopardy
```

Or with a dockerized PostgreSQL (example):

```bash
docker run --rm -d \
  --name jeopardy-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=jeopardy \
  -p 5432:5432 \
  postgres:16
```

Then:
```
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/jeopardy"
```


# Makefile Usage from repo root

Local venv install:

```bash
make install
```

Run API locally (Postgres must be reachable and DATABASE_URL set):
```bash
export DATABASE_URL="postgresql+psycopg://jeopardy:jeopardy@localhost:5432/jeopardy"
make run
```

Run full Docker stack:
```bash
make up
```

Wipe DB volume and start fresh:
```bash
make reset
make up
```