from __future__ import annotations

import random
from dataclasses import dataclass

from jeopardy_game.services.agents.base import Agent, AgentAnswer
from jeopardy_game.services.openai_client import OpenAIClient


@dataclass(frozen=True)
class LlmAgentConfig:
    skill: str  # "easy" | "medium" | "hard"
    temperature: float = 0.2


class LlmAgent(Agent):
    """LLM-based agent with a configurable mistake rate by skill."""

    def __init__(self, *, name: str, client: OpenAIClient, config: LlmAgentConfig) -> None:
        self.name = name
        self._client = client
        self._cfg = config

    def _mistake_rate(self) -> float:
        # Higher skill => lower mistake probability
        return {"easy": 0.40, "medium": 0.20, "hard": 0.08}.get(self._cfg.skill, 0.20)

    def answer_question(self, *, question: str, category: str, round_name: str, value: str) -> AgentAnswer:
        prompt = (
            "You are playing Jeopardy.\n"
            f"Round: {round_name}\n"
            f"Category: {category}\n"
            f"Value: {value}\n"
            f"Clue: {question}\n\n"
            "Answer with ONLY the short answer (no explanation, no punctuation)."
        )

        payload = {
            "model": self._client.model,
            "input": prompt,
            "temperature": self._cfg.temperature,
        }

        raw = self._client.create_response(payload)
        text = self._client.extract_output_text(raw).strip()

        # Controlled “skill” mistakes: sometimes corrupt the answer slightly or replace with "I don't know"
        if random.random() < self._mistake_rate():
            if random.random() < 0.5:
                text = "I don't know"
            else:
                text = text + "s"  # tiny perturbation

        return AgentAnswer(answer=text, rationale=None)
