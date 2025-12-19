"""OpenAI API client using requests (no SDK required)."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Minimal OpenAI Responses API client."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        timeout_s: float = 20.0,
        max_retries: int = 2,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        self._session = requests.Session()

    @property
    def model(self) -> str:
        return self._model

    @classmethod
    def from_env(cls) -> "OpenAIClient":
        """Create a client from environment variables.

        Required:
          - OPENAI_API_KEY

        Optional:
          - OPENAI_BASE_URL (default https://api.openai.com/v1)
          - OPENAI_MODEL (default gpt-4o-mini)
          - OPENAI_TIMEOUT_S (default 20)
          - OPENAI_MAX_RETRIES (default 2)
        """
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

        timeout_s = float(os.getenv("OPENAI_TIMEOUT_S", "20.0"))
        max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "2"))

        return cls(
            api_key=api_key,
            base_url=base_url,
            model=model,
            timeout_s=timeout_s,
            max_retries=max_retries,
        )

    def create_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /v1/responses and return the parsed JSON response."""
        url = f"{self._base_url}/responses"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(self._max_retries + 1):
            try:
                resp = self._session.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=self._timeout_s,
                )
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(
                        f"Transient OpenAI error {resp.status_code}: {resp.text}",
                        response=resp,
                    )
                resp.raise_for_status()
                return resp.json()

            except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as exc:
                if attempt >= self._max_retries:
                    logger.exception("OpenAI request failed after retries: %s", exc)
                    raise
                backoff = 0.7 * (2**attempt)
                logger.warning("OpenAI request failed (%s). Retrying in %.1fs...", exc, backoff)
                time.sleep(backoff)

        raise RuntimeError("Unreachable")

    @staticmethod
    def extract_output_text(resp_json: dict[str, Any]) -> str:
        """Extract plain text from a Responses API JSON payload.

        This supports the common structure:
          resp["output"][...]["content"][...]["text"] or ["output_text"].
        """
        output = resp_json.get("output") or []
        chunks: list[str] = []

        for item in output:
            content = item.get("content") or []
            for part in content:
                # observed variants in Responses API payloads
                if "text" in part and isinstance(part["text"], str):
                    chunks.append(part["text"])
                elif part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    chunks.append(part["text"])

        return "\n".join([c for c in chunks if c]).strip()
