"""Application configuration (env-driven)."""

from __future__ import annotations

import os


def get_database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://jeopardy:jeopardy@localhost:5432/jeopardy",
    )


def get_openai_api_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY")


def get_openai_model() -> str:
    # Use a sensible default; can be overridden via env.
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def get_openai_base_url() -> str:
    return os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
