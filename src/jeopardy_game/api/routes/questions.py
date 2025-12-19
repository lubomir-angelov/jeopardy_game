# src/jeopardy_game/app/api/routes/questions.py
"""API routes for retrieving questions and verifying answers."""

from __future__ import annotations

import re
from typing import Final

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from jeopardy_game.api.deps import get_db
from jeopardy_game.models.question import Question
from jeopardy_game.schemas.question import QuestionOut
from jeopardy_game.schemas.verify import VerifyAnswerIn, VerifyAnswerOut
from jeopardy_game.services.answer_checker import is_answer_correct

router = APIRouter(tags=["questions"])

# Keep these aligned with dataset values you ingest.
ALLOWED_ROUNDS: Final[set[str]] = {"Jeopardy!", "Double Jeopardy!", "Final Jeopardy!"}


_VALUE_RE = re.compile(r"^\s*\$?\s*(\d+)\s*$")


def _parse_value_to_int(value_raw: str) -> int:
    """Parse a value query parameter like '$200' or '200' into an int.

    Raises:
        HTTPException: If the value cannot be parsed or is out of allowed bounds.
    """
    match = _VALUE_RE.match(value_raw or "")
    if not match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid value format. Use '$200' or '200'.",
        )

    value_int = int(match.group(1))

    # Task requirement: subset up to $1200. Enforce to match stored subset.
    if value_int <= 0 or value_int > 1200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Value must be between 1 and 1200 (inclusive).",
        )

    return value_int


def _to_question_out(q: Question) -> QuestionOut:
    """Map ORM Question -> API response schema (without leaking answer)."""
    return QuestionOut(
        question_id=q.id,
        round=q.round,
        category=q.category,
        value=f"${q.value}",
        question=q.question,
    )


@router.get(
    "/question/",
    response_model=QuestionOut,
    summary="Get a random question filtered by round and value",
)
def get_random_question(
    round_: str = Query(..., alias="round", description='One of: "Jeopardy!", "Double Jeopardy!", "Final Jeopardy!"'),
    value: str = Query(..., description='Question value like "$200"'),
    db: Session = Depends(get_db),
) -> QuestionOut:
    """Return a random question matching the given round and value."""
    if round_ not in ALLOWED_ROUNDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid round. Allowed values: {sorted(ALLOWED_ROUNDS)}",
        )

    value_int = _parse_value_to_int(value)

    stmt = (
        select(Question)
        .where(Question.round == round_)
        .where(Question.value == value_int)
        .order_by(func.random())
        .limit(1)
    )
    q = db.execute(stmt).scalars().first()
    if q is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No question found for the given round and value.",
        )

    return _to_question_out(q)


@router.post(
    "/verify-answer/",
    response_model=VerifyAnswerOut,
    summary="Verify a user's answer against the stored correct answer",
)
def verify_answer(payload: VerifyAnswerIn, db: Session = Depends(get_db)) -> VerifyAnswerOut:
    """Verify a user's answer.

    This uses a heuristic similarity-based matcher (LLM optional later).
    """
    q = db.get(Question, payload.question_id)
    if q is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found.",
        )

    is_correct, explanation = is_answer_correct(
        user_answer=payload.user_answer,
        correct_answer=q.answer,
    )

    return VerifyAnswerOut(
        is_correct=is_correct,
        ai_response=explanation,
    )
