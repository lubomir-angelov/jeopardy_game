"""Application configuration."""

from __future__ import annotations

import os


def get_database_url() -> str:
    """Return DATABASE_URL from environment or a sensible local default."""
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/jeopardy",
    )
