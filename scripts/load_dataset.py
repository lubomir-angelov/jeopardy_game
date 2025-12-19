"""Script to load Jeopardy questions from a CSV into the database. Also inits the DB schema if needed."""
# repo_root/scripts/load_dataset.py
from __future__ import annotations

import csv
import os
import re
import time
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from jeopardy_game.db.base import Base
from jeopardy_game.models.question import Question


_VALUE_RE = re.compile(r"^\s*\$?\s*(\d+)\s*$")


def parse_value(value_raw: str) -> Optional[int]:
    """Parse '$200' / '200' into int(200). Return None if unparseable."""
    if not value_raw:
        return None
    m = _VALUE_RE.match(value_raw)
    if not m:
        return None
    return int(m.group(1))


def wait_for_db(engine, timeout_s: int = 90) -> None:
    """Wait for Postgres to accept connections."""
    start = time.time()
    last_err: Exception | None = None

    while time.time() - start < timeout_s:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            last_err = exc
            time.sleep(1)

    raise RuntimeError(f"Database not ready after {timeout_s}s: {last_err}") from last_err


def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    csv_path = os.environ.get("JEP_CSV_PATH", "/assets/JEOPARDY_CSV.csv")
    max_value = int(os.environ.get("JEP_MAX_VALUE", "1200"))

    engine = create_engine(database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    wait_for_db(engine, timeout_s=90)

    # Create schema (idempotent)
    Base.metadata.create_all(bind=engine)

    # If already seeded, skip.
    with SessionLocal() as db:
        if db.query(Question.id).limit(1).first() is not None:
            print("Questions already exist; skipping load.")
            return

    inserted = 0
    commit_every = 2000

    with open(csv_path, "r", encoding="utf-8", newline="") as f, SessionLocal() as db:
        reader = csv.DictReader(f)

        # Your headers (note the spaces):
        # Show Number, Air Date, Round, Category, Value, Question, Answer
        required_cols = {
            "Show Number",
            "Air Date",
            "Round",
            "Category",
            "Value",
            "Question",
            "Answer",
        }
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f"CSV is missing required columns: {sorted(missing)}")

        for row in reader:
            value_int = parse_value((row.get("Value") or "").strip())
            if value_int is None or value_int > max_value:
                continue

            air_date_raw = (row.get("Air Date") or "").strip()
            # Dataset uses YYYY-MM-DD as shown in your sample
            air_date = datetime.strptime(air_date_raw, "%Y-%m-%d").date()

            q = Question(
                show_number=int((row.get("Show Number") or "0").strip()),
                air_date=air_date,
                round=(row.get("Round") or "").strip(),
                category=(row.get("Category") or "").strip(),
                value=value_int,
                question=(row.get("Question") or "").strip(),
                answer=(row.get("Answer") or "").strip(),
            )
            db.add(q)
            inserted += 1

            if inserted % commit_every == 0:
                db.commit()
                print(f"Inserted {inserted}...")

        db.commit()

    print(f"Load complete. Inserted: {inserted}")


if __name__ == "__main__":
    main()
