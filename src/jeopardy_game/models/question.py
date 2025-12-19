"""ORM model for Jeopardy questions."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Date, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from jeopardy_game.db.base import Base


class Question(Base):
    """Represents a Jeopardy clue/question."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    show_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    air_date: Mapped[dt.date] = mapped_column(Date, nullable=False, index=True)

    # "Jeopardy!", "Double Jeopardy!", "Final Jeopardy!"
    round: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    category: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    # Store as integer dollars (200..1200 for your subset)
    value: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("ix_questions_round_value", "round", "value"),
    )
