from __future__ import annotations

from typing import Literal


class OpenAlexConfig:
    def __init__(self) -> None:
        self.api_key: str | None = None
        self.base_url: str = "https://api.openalex.org"
        self.content_base_url: str = "https://content.openalex.org"
        self.user_agent: str = "openalexpy/0.1.0"
        self.max_retries: int = 3
        self.retry_backoff_factor: float = 0.5
        self.timeout: float = 30.0
        self.on_credits_exhausted: Literal["raise", "wait"] = "raise"


config = OpenAlexConfig()
