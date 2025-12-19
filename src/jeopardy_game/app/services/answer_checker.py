"""Answer verification logic (heuristic baseline; LLM can be added later)."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


def _normalize(text: str) -> str:
    """Normalize text for approximate matching.

    Steps:
      - lowercase
      - strip diacritics
      - remove punctuation
      - collapse whitespace
      - remove common Jeopardy-style lead-ins (e.g., 'what is', 'the answer is')
    """
    t = text.strip().lower()

    # Common lead-ins
    t = re.sub(r"^\s*(what is|who is|where is|when is|the answer is|answer is)\s+", "", t)

    # Strip diacritics (e.g., “café” -> “cafe”)
    t = "".join(
        ch for ch in unicodedata.normalize("NFKD", t)
        if not unicodedata.combining(ch)
    )

    # Remove punctuation/symbols, keep alphanumerics and spaces
    t = re.sub(r"[^a-z0-9\s]", " ", t)

    # Remove articles that often cause false negatives
    t = re.sub(r"\b(the|a|an)\b", " ", t)

    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def is_answer_correct(user_answer: str, correct_answer: str, *, threshold: float = 0.86) -> tuple[bool, str]:
    """Check if `user_answer` matches `correct_answer` approximately.

    Args:
        user_answer: Free-text user response.
        correct_answer: Canonical answer from DB.
        threshold: Similarity threshold in [0, 1]. Higher is stricter.

    Returns:
        (is_correct, explanation)
    """
    ua = _normalize(user_answer)
    ca = _normalize(correct_answer)

    if not ua or not ca:
        return False, "Unable to evaluate the answer (empty input after normalization)."

    if ua == ca:
        return True, f"Exact match after normalization: '{correct_answer}'."

    # Containment (handles extra words)
    if ua in ca or ca in ua:
        return True, f"Close match: your answer refers to '{correct_answer}'."

    ratio = SequenceMatcher(a=ua, b=ca).ratio()
    if ratio >= threshold:
        return True, f"Likely correct (similarity {ratio:.2f}): expected '{correct_answer}'."

    return False, f"Does not match closely enough (similarity {ratio:.2f}): expected '{correct_answer}'."
