# repo_root/scripts/load_dataset.py
from __future__ import annotations

import os
import re
import time
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from jeopardy_game.db.base import Base
from jeopardy_game.models.question import Question


_VALUE_RE = re.compile(r"^\s*\$?\s*(\d+)\s*$")


def parse_value(value_raw: object) -> Optional[int]:
    """Parse '$200' / '200' into int(200). Return None if unparseable."""
    if value_raw is None:
        return None
    s = str(value_raw).strip()
    if not s:
        return None
    m = _VALUE_RE.match(s)
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

    # If already seeded, skip
    with SessionLocal() as db:
        if db.query(Question.id).limit(1).first() is not None:
            print("Questions already exist; skipping load.")
            return

    # Read CSV robustly (handles BOM via utf-8-sig)
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]

    required_cols = [
        "Show Number",
        "Air Date",
        "Round",
        "Category",
        "Value",
        "Question",
        "Answer",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"CSV is missing required columns: {missing}. Found: {list(df.columns)}")

    # Parse and filter values
    df["value_int"] = df["Value"].map(parse_value)
    df = df[df["value_int"].notna()]
    df = df[df["value_int"] <= max_value]

    # Parse dates (YYYY-MM-DD)
    df["air_date"] = pd.to_datetime(
        df["Air Date"].astype(str).str.strip(),
        format="%Y-%m-%d",
        errors="coerce",
    )
    df = df[df["air_date"].notna()]

    # Drop missing essentials
    df = df.dropna(subset=["Show Number", "Round", "Category", "Question", "Answer", "air_date", "value_int"])

    rows = df.to_dict(orient="records")

    batch_size = 2000
    inserted = 0

    with SessionLocal() as db:
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            objs = [
                Question(
                    show_number=int(str(r["Show Number"]).strip()),
                    air_date=r["air_date"].date(),
                    round=str(r["Round"]).strip(),
                    category=str(r["Category"]).strip(),
                    value=int(r["value_int"]),
                    question=str(r["Question"]).strip(),
                    answer=str(r["Answer"]).strip(),
                )
                for r in batch
            ]
            db.bulk_save_objects(objs)
            db.commit()
            inserted += len(objs)
            print(f"Inserted {inserted}...")

    print(f"Load complete. Inserted: {inserted}")


if __name__ == "__main__":
    main()
