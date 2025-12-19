# tests/test_verify_answer_endpoint.py
from __future__ import annotations


def test_verify_answer_correct_typo_heuristic(client, monkeypatch):
    # Ensure LLM is not used
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    resp = client.post("/verify-answer/", json={"question_id": 1, "user_answer": "Copernics"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_correct"] is True
    assert isinstance(data["ai_response"], str)
    assert data["ai_response"]  # non-empty


def test_verify_answer_incorrect_heuristic(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    resp = client.post("/verify-answer/", json={"question_id": 1, "user_answer": "Totally wrong"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_correct"] is False
    assert isinstance(data["ai_response"], str)


def test_verify_answer_question_not_found(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    resp = client.post("/verify-answer/", json={"question_id": 9999, "user_answer": "Copernicus"})
    assert resp.status_code == 404
