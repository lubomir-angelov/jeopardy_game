from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


SkillLevel = Literal["easy", "medium", "hard"]


class AgentPlayRequest(BaseModel):
    agent_name: str = Field(default="AI-Bot")
    skill: SkillLevel = Field(default="medium")
    round: str | None = Field(default=None, description="Jeopardy! | Double Jeopardy! | Final Jeopardy!")
    value: str | None = Field(default=None, description='Dollar value string like "$200"')


class AgentPlayResponse(BaseModel):
    agent_name: str
    skill: SkillLevel
    question_id: int
    question: str
    category: str
    round: str
    value: str
    ai_answer: str
    is_correct: bool
    verifier_response: str
