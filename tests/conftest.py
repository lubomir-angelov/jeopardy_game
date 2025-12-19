# tests/conftest.py
from __future__ import annotations

import datetime as dt
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from jeopardy_game.api.deps import get_db
from jeopardy_game.db.base import Base
from jeopardy_game.main import app as fastapi_app
from jeopardy_game.models.question import Question


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide a SQLite in-memory DB session shared across threads."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # critical: reuse the same connection
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        db.add_all(
            [
                Question(
                    show_number=4680,
                    air_date=dt.date(2004, 12, 31),
                    round="Jeopardy!",
                    category="HISTORY",
                    value=200,
                    question=(
                        "For the last 8 years of his life, Galileo was under house arrest "
                        "for espousing this man's theory"
                    ),
                    answer="Copernicus",
                ),
                Question(
                    show_number=4680,
                    air_date=dt.date(2004, 12, 31),
                    round="Jeopardy!",
                    category="THE COMPANY LINE",
                    value=200,
                    question='In 1963, live on "The Art Linkletter Show", this company served its billionth burger',
                    answer="McDonald's",
                ),
            ]
        )
        db.commit()

        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with DB dependency override."""
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(fastapi_app) as c:
            yield c
    finally:
        fastapi_app.dependency_overrides.clear()
