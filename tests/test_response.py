from __future__ import annotations

from openalexpy.entities import Work
from openalexpy.response import OpenAlexResponse
from openalexpy.response import RateLimitInfo
from openalexpy.response import ResponseMeta
from openalexpy.response import parse_rate_limit_headers
from openalexpy.response import parse_response_meta


class TestRateLimitInfo:
    def test_default(self):
        rl = RateLimitInfo()
        assert rl.daily_budget_usd is None
        assert rl.daily_remaining_usd is None

    def test_with_values(self):
        rl = RateLimitInfo(
            daily_budget_usd=1.0,
            daily_remaining_usd=0.95,
            daily_used_usd=0.05,
            resets_in_seconds=43200,
        )
        assert rl.daily_budget_usd == 1.0
        assert rl.daily_remaining_usd == 0.95


class TestResponseMeta:
    def test_from_dict(self):
        meta = parse_response_meta(
            {
                "count": 870627,
                "db_response_time_ms": 19,
                "page": 1,
                "per_page": 100,
                "next_cursor": "abc123",
                "cost_usd": 0.0001,
            }
        )
        assert meta.count == 870627
        assert meta.per_page == 100
        assert meta.next_cursor == "abc123"
        assert meta.cost_usd == 0.0001


class TestOpenAlexResponse:
    def test_with_results(self):
        resp = OpenAlexResponse(
            results=[Work(id="W123"), Work(id="W456")],
            meta=ResponseMeta(count=2, per_page=25),
        )
        assert len(resp.results) == 2
        assert resp.meta.count == 2


class TestParseRateLimitHeaders:
    def test_parse_standard_headers(self):
        headers = {
            "x-ratelimit-limit": "100",
            "x-ratelimit-remaining": "95",
            "x-ratelimit-credits-used": "0.0001",
            "x-ratelimit-reset": "43200",
        }
        rl = parse_rate_limit_headers(headers)
        assert rl.credits_limit == 100.0
        assert rl.credits_remaining == 95.0
        assert rl.credits_used == 0.0001
        assert rl.resets_in_seconds == 43200.0

    def test_parse_budget_headers(self):
        headers = {
            "x-ratelimit-daily-budget-usd": "1.0",
            "x-ratelimit-daily-remaining-usd": "0.95",
            "x-ratelimit-daily-used-usd": "0.05",
        }
        rl = parse_rate_limit_headers(headers)
        assert rl.daily_budget_usd == 1.0
        assert rl.daily_remaining_usd == 0.95
        assert rl.daily_used_usd == 0.05

    def test_empty_headers(self):
        rl = parse_rate_limit_headers({})
        assert rl.daily_budget_usd is None
        assert rl.credits_remaining is None

    def test_invalid_header_value(self):
        headers = {"x-ratelimit-limit": "not-a-number"}
        rl = parse_rate_limit_headers(headers)
        assert rl.credits_limit is None
