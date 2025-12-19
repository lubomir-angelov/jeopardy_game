"""Pydantic schemas for question endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class QuestionOut(BaseModel):
    """Response model for a question returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    question_id: int = Field(..., description="Internal question identifier")
    round: str
    category: str
    value: str = Field(..., description='Question value formatted like "$200"')
    question: str
