# tests/test_question_endpoint.py
from __future__ import annotations


def test_get_random_question_success(client):
    resp = client.get("/question/", params={"round": "Jeopardy!", "value": "$200"})
    assert resp.status_code == 200
    data = resp.json()

    assert "question_id" in data
    assert data["round"] == "Jeopardy!"
    assert data["value"] == "$200"
    assert isinstance(data["question"], str)
    # Do not leak answers
    assert "answer" not in data


def test_get_random_question_invalid_round(client):
    resp = client.get("/question/", params={"round": "NotARealRound", "value": "$200"})
    assert resp.status_code == 400


def test_get_random_question_invalid_value_format(client):
    resp = client.get("/question/", params={"round": "Jeopardy!", "value": "two hundred"})
    assert resp.status_code == 400


def test_get_random_question_not_found(client):
    # Value exists in validator but not in seeded test data
    resp = client.get("/question/", params={"round": "Jeopardy!", "value": "$1200"})
    assert resp.status_code == 404
