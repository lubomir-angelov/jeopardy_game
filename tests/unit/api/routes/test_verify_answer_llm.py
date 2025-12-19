# tests/test_verify_answer_llm.py
from __future__ import annotations


def test_verify_answer_llm_fallback_used(client, monkeypatch):
    # Force LLM to be enabled
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    # Patch the OpenAIClient.create_response method to return a Responses-like payload
    from jeopardy_game.services import openai_client as openai_client_module

    def fake_create_response(self, payload):
        # Minimal structure expected by _extract_output_text()
        return {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": '{"is_correct": true, "explanation": "Acceptable spelling variant."}'}
                    ],
                }
            ]
        }

    monkeypatch.setattr(openai_client_module.OpenAIClient, "create_response", fake_create_response)

    # Provide an answer that is likely to be rejected by heuristic (depends on your threshold).
    resp = client.post("/verify-answer/", json={"question_id": 1, "user_answer": "Coperniadawdacs"})
    assert resp.status_code == 200
    data = resp.json()

    # The fake LLM always returns correct=True
    assert data["is_correct"] is True
    assert data["ai_response"] == "Acceptable spelling variant."
