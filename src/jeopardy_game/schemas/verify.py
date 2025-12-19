"""Pydantic schemas for verifying an answer."""

from pydantic import BaseModel, Field


class VerifyAnswerIn(BaseModel):
    """Request body for verifying a user's answer."""

    question_id: int = Field(..., ge=1)
    user_answer: str = Field(..., min_length=1)


class VerifyAnswerOut(BaseModel):
    """Response body for answer verification."""

    is_correct: bool
    ai_response: str
