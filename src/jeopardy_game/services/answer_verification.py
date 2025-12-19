from __future__ import annotations

from jeopardy_game.schemas.verify import VerifyAnswerOut
from jeopardy_game.services.answer_checker import is_answer_correct
from jeopardy_game.services.llm_verifier import LLMAnswerVerifier
from jeopardy_game.core.config import get_openai_api_key
from jeopardy_game.models.question import Question


def verify_answer_for_question(*, question: Question, user_answer: str) -> VerifyAnswerOut:
    """Verify a user answer against a Question row.

    - Heuristic first (fast)
    - Optional LLM fallback if OPENAI_API_KEY is configured
    - Fail-closed to heuristic if LLM errors
    """
    heuristic_ok, heuristic_msg = is_answer_correct(user_answer, question.answer)

    if heuristic_ok:
        return VerifyAnswerOut(is_correct=True, ai_response=heuristic_msg)

    api_key = get_openai_api_key()
    if not api_key:
        return VerifyAnswerOut(is_correct=False, ai_response=heuristic_msg)

    try:
        verifier = LLMAnswerVerifier(api_key=api_key)
        verdict = verifier.verify(
            question=question.question,
            correct_answer=question.answer,
            user_answer=user_answer,
        )
        return VerifyAnswerOut(is_correct=verdict.is_correct, ai_response=verdict.explanation)
    except Exception:
        return VerifyAnswerOut(is_correct=False, ai_response=heuristic_msg)
