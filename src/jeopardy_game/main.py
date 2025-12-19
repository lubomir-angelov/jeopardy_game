# src/jeopardy_game/app/main.py
"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from jeopardy_game.api.routes.questions import router as questions_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Jeopardy Game API",
        version="0.1.0",
    )

    app.include_router(questions_router)

    return app


app = create_app()
