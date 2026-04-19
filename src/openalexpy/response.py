from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict

from openalexpy.entities import GroupByResult

T = TypeVar("T")


class RateLimitInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    daily_budget_usd: float | None = None
    daily_remaining_usd: float | None = None
    daily_used_usd: float | None = None
    resets_in_seconds: int | None = None
    reset_at: str | None = None
    credits_used: float | None = None
    credits_limit: float | None = None
    credits_remaining: float | None = None


class ResponseMeta(BaseModel):
    model_config = ConfigDict(extra="allow")

    count: int = 0
    db_response_time_ms: int = 0
    page: int | None = None
    per_page: int = 25
    next_cursor: str | None = None
    groups_count: int | None = None
    cost_usd: float | None = None


class OpenAlexResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    results: list[T] = []
    meta: ResponseMeta
    rate_limit: RateLimitInfo | None = None
    group_by: list[GroupByResult] | None = None


def parse_rate_limit_headers(headers: Any) -> RateLimitInfo:
    data: dict[str, Any] = {}
    mapping = {
        "x-ratelimit-limit": "credits_limit",
        "x-ratelimit-remaining": "credits_remaining",
        "x-ratelimit-credits-used": "credits_used",
        "x-ratelimit-reset": "resets_in_seconds",
    }
    for header_key, field_name in mapping.items():
        val = headers.get(header_key)
        if val is not None:
            try:
                data[field_name] = float(val)
            except (ValueError, TypeError):
                pass

    budget = headers.get("x-ratelimit-daily-budget-usd")
    if budget is not None:
        try:
            data["daily_budget_usd"] = float(budget)
        except (ValueError, TypeError):
            pass

    remaining = headers.get("x-ratelimit-daily-remaining-usd")
    if remaining is not None:
        try:
            data["daily_remaining_usd"] = float(remaining)
        except (ValueError, TypeError):
            pass

    used = headers.get("x-ratelimit-daily-used-usd")
    if used is not None:
        try:
            data["daily_used_usd"] = float(used)
        except (ValueError, TypeError):
            pass

    reset = headers.get("x-ratelimit-reset-at")
    if reset is not None:
        data["reset_at"] = reset

    return RateLimitInfo(**data)


def parse_response_meta(data: dict) -> ResponseMeta:
    return ResponseMeta(**data)
