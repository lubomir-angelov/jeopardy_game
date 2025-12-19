"""LLM-based answer verification."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from jeopardy_game.core.config import get_openai_base_url, get_openai_model
from jeopardy_game.services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class LLMVerdict(BaseModel):
    """Structured verdict returned by the LLM."""

    is_correct: bool = Field(..., description="Whether the user's answer should be accepted as correct.")
    explanation: str = Field(..., min_length=1, description="Short explanation for the verdict.")


class LLMAnswerVerifier:
    """Verifies answers using OpenAI Responses API."""

    def __init__(self, *, api_key: str) -> None:
        self._client = OpenAIClient(api_key=api_key, base_url=get_openai_base_url())

    def verify(self, *, question: str, correct_answer: str, user_answer: str) -> LLMVerdict:
        model = get_openai_model()

        schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "is_correct": {"type": "boolean"},
                "explanation": {"type": "string"},
            },
            "required": ["is_correct", "explanation"],
            "additionalProperties": False,
        }

        prompt_system = (
            "You are a strict-but-fair Jeopardy judge. "
            "Decide if the user's answer should be accepted as correct given the question and the official answer. "
            "Be tolerant of minor spelling errors, punctuation differences, and common synonyms. "
            "If the user's answer is clearly wrong, mark it incorrect."
        )

        prompt_user = (
            f"QUESTION: {question}\n"
            f"OFFICIAL ANSWER: {correct_answer}\n"
            f"USER ANSWER: {user_answer}\n"
            "Return your decision in the required JSON format."
        )

        payload: dict[str, Any] = {
            "model": model,
            "input": [
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user},
            ],
            # Structured Outputs via JSON schema.
            # The docs describe enabling json_schema via text.format. :contentReference[oaicite:4]{index=4}
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "jeopardy_answer_verdict",
                    "schema": schema,
                    "strict": True,
                }
            },
        }

        raw = self._client.create_response(payload=payload)
        parsed_text = _extract_output_text(raw)
        try:
            data = json.loads(parsed_text)
        except json.JSONDecodeError as exc:
            logger.warning("LLM returned non-JSON output: %r", parsed_text)
            raise RuntimeError(f"LLM output was not valid JSON: {exc}") from exc

        try:
            return LLMVerdict.model_validate(data)
        except ValidationError as exc:
            raise RuntimeError(f"LLM output did not match schema: {exc}") from exc


def _extract_output_text(response_json: dict[str, Any]) -> str:
    """Extract the assistant text from a Responses API response."""
    # Responses API returns an `output` array with message content items.
    # We'll pull the first output_text we find.
    output = response_json.get("output", [])
    for item in output:
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                return content["text"]

    # Fallback: attempt a couple of known alternative shapes, then fail loudly.
    raise RuntimeError("Unable to extract output text from OpenAI response.")
