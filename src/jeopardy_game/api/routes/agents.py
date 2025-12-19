from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from jeopardy_game.api.deps import get_db
from jeopardy_game.models.question import Question
from jeopardy_game.schemas.agent_play import AgentPlayRequest, AgentPlayResponse
from jeopardy_game.services.agents.factory import build_agent
from jeopardy_game.services.answer_checker import is_answer_correct  # adjust import to your verifier function


router = APIRouter(tags=["agents"])


@router.post("/agent-play/", response_model=AgentPlayResponse)
def agent_play(payload: AgentPlayRequest, db: Session = Depends(get_db)) -> AgentPlayResponse:
    # Reuse your existing query logic, or do minimal filtering here:
    q = db.query(Question)

    if payload.round:
        q = q.filter(Question.round == payload.round)
    if payload.value:
        # your model stores int value; convert "$200" -> 200 if needed
        try:
            value_int = int(payload.value.replace("$", "").replace(",", "").strip())
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid value format") from e
        q = q.filter(Question.value == value_int)

    question_row = q.order_by(Question.id.desc()).first()
    if question_row is None:
        raise HTTPException(status_code=404, detail="No questions found for given filters")

    # Agent answers
    agent = build_agent(name=payload.agent_name, skill=payload.skill)
    agent_answer = agent.answer_question(
        question=question_row.question,
        category=question_row.category,
        round_name=question_row.round,
        value=f"${question_row.value}",
    )

    is_correct, explanation = is_answer_correct(
        agent_answer.answer,
        question_row.answer,
    )

    return AgentPlayResponse(
        agent_name=payload.agent_name,
        skill=payload.skill,
        question_id=question_row.id,
        question=question_row.question,
        category=question_row.category,
        round=question_row.round,
        value=f"${question_row.value}",
        ai_answer=agent_answer.answer,
        is_correct=is_correct,
        verifier_response=explanation,
    )
