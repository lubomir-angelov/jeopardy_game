"""OpenAI API client using requests (no SDK required)."""

from __future__ import annotations

import json
import logging
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
        timeout_s: float = 20.0,
        max_retries: int = 2,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        self._session = requests.Session()

    def create_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /v1/responses and return the parsed JSON response."""
        url = f"{self._base_url}/responses"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        # Simple retry on transient failures (429/5xx/timeouts).
        for attempt in range(self._max_retries + 1):
            try:
                resp = self._session.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=self._timeout_s,
                )
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(f"Transient OpenAI error {resp.status_code}: {resp.text}", response=resp)
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
