from __future__ import annotations

from jeopardy_game.services.agents.llm_agent import LlmAgent, LlmAgentConfig
from jeopardy_game.services.openai_client import OpenAIClient


def build_agent(*, name: str, skill: str) -> LlmAgent:
    client = OpenAIClient.from_env()
    return LlmAgent(name=name, client=client, config=LlmAgentConfig(skill=skill))
