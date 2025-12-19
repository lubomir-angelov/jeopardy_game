# jeopardy_game
Test repo for a small backend for playing jeopardy like game

# Repo structure
```
jeopardy_game/
  src/
    jeopardy_game/
        app/
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

## Environment variables
The API expects a database URL via `DATABASE_URL`.

Example:
```bash
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/jeopardy"
```