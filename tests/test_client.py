from __future__ import annotations

import pytest

from openalexpy.client import AsyncOpenAlexClient
from openalexpy.client import SyncOpenAlexClient
from openalexpy.config import config
from openalexpy.exceptions import CreditsExhaustedError
from openalexpy.exceptions import QueryError
from openalexpy.exceptions import RateLimitError


class TestClientURLBuilding:
    def test_basic_url(self):
        client = AsyncOpenAlexClient()
        url = client._build_url("works")
        assert url == "https://api.openalex.org/works"

    def test_url_with_params(self):
        client = AsyncOpenAlexClient()
        url = client._build_url("works", {"filter": "publication_year:2020"})
        assert "filter=publication_year:2020" in url
        assert url.startswith("https://api.openalex.org/works")

    def test_url_with_api_key(self):
        original = config.api_key
        try:
            config.api_key = "test-key"
            client = AsyncOpenAlexClient()
            url = client._build_url("works")
            assert "api_key=test-key" in url
        finally:
            config.api_key = original

    def test_url_with_params_and_api_key(self):
        original = config.api_key
        try:
            config.api_key = "test-key"
            client = AsyncOpenAlexClient()
            url = client._build_url("works", {"per_page": "25"})
            assert "per_page=25" in url
            assert "api_key=test-key" in url
        finally:
            config.api_key = original

    def test_sync_client_url(self):
        client = SyncOpenAlexClient()
        url = client._build_url("authors")
        assert url == "https://api.openalex.org/authors"


class TestErrorHandling:
    def test_404_raises_not_found(self):
        import httpx

        from openalexpy.exceptions import NotFoundError

        client = AsyncOpenAlexClient()
        resp = httpx.Response(
            404, request=httpx.Request("GET", "https://api.openalex.org/works/bad")
        )
        with pytest.raises(NotFoundError):
            client._handle_error_response(resp)

    def test_400_raises_query_error(self):
        import httpx

        client = AsyncOpenAlexClient()
        resp = httpx.Response(
            400,
            json={"error": "invalid filter"},
            request=httpx.Request("GET", "https://api.openalex.org/works"),
        )
        with pytest.raises(QueryError, match="Bad request"):
            client._handle_error_response(resp)

    def test_401_raises_query_error(self):
        import httpx

        client = AsyncOpenAlexClient()
        resp = httpx.Response(
            401,
            json={"error": "invalid API key"},
            request=httpx.Request("GET", "https://api.openalex.org/works"),
        )
        with pytest.raises(QueryError, match="Unauthorized"):
            client._handle_error_response(resp)

    def test_429_rate_limit_error(self):
        import httpx

        client = AsyncOpenAlexClient()
        resp = httpx.Response(
            429,
            headers={"Retry-After": "5"},
            request=httpx.Request("GET", "https://api.openalex.org/works"),
        )
        with pytest.raises(RateLimitError) as exc_info:
            client._handle_error_response(resp)
        assert exc_info.value.retry_after == 5

    def test_429_credits_exhausted(self):
        import httpx

        client = AsyncOpenAlexClient()
        resp = httpx.Response(
            429,
            headers={
                "x-ratelimit-daily-remaining-usd": "0",
            },
            request=httpx.Request("GET", "https://api.openalex.org/works"),
        )
        with pytest.raises(CreditsExhaustedError):
            client._handle_error_response(resp)
