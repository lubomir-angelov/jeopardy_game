from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentAnswer:
    answer: str
    rationale: str | None = None


class Agent:
    """Base agent interface."""

    name: str

    def answer_question(self, *, question: str, category: str, round_name: str, value: str) -> AgentAnswer:
        raise NotImplementedError
