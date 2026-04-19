from __future__ import annotations

import asyncio
import time
from typing import Any
from typing import TypeVar

import httpx

from openalexpy.config import config
from openalexpy.exceptions import CreditsExhaustedError
from openalexpy.exceptions import NotFoundError
from openalexpy.exceptions import OpenAlexError
from openalexpy.exceptions import QueryError
from openalexpy.exceptions import RateLimitError
from openalexpy.response import RateLimitInfo
from openalexpy.response import parse_rate_limit_headers

T = TypeVar("T")

_LAST_SEMANTIC_CALL: float = 0.0


def _is_semantic_search(params: dict) -> bool:
    return "search.semantic" in params


async def _enforce_semantic_rate_limit(params: dict) -> None:
    global _LAST_SEMANTIC_CALL
    if _is_semantic_request(params):
        elapsed = time.monotonic() - _LAST_SEMANTIC_CALL
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)
        _LAST_SEMANTIC_CALL = time.monotonic()


def _is_semantic_request(params: dict) -> bool:
    return "search.semantic" in params


class AsyncOpenAlexClient:
    def __init__(self) -> None:
        self._config = config

    def _build_url(self, endpoint: str, params: dict | None = None) -> str:
        base = self._config.base_url.rstrip("/")
        url = f"{base}/{endpoint}"
        query_parts: list[str] = []

        if params:
            for k, v in params.items():
                if v is None:
                    continue
                query_parts.append(f"{k}={v}")

        if self._config.api_key:
            query_parts.append(f"api_key={self._config.api_key}")

        if query_parts:
            url = f"{url}?{'&'.join(query_parts)}"

        return url

    def _get_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._config.user_agent:
            headers["User-Agent"] = self._config.user_agent
        return headers

    def _handle_error_response(self, response: httpx.Response) -> None:
        if response.status_code == 404:
            raise NotFoundError(f"Not found: {response.url}")

        if response.status_code == 400:
            try:
                data = response.json()
                msg = data.get("error", data.get("message", response.text))
            except Exception:
                msg = response.text
            raise QueryError(f"Bad request: {msg}")

        if response.status_code == 401:
            try:
                data = response.json()
                msg = data.get("error", data.get("message", response.text))
            except Exception:
                msg = response.text
            raise QueryError(f"Unauthorized: {msg}")

        if response.status_code == 429:
            rl = parse_rate_limit_headers(response.headers)
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after else None

            if rl.daily_remaining_usd is not None and rl.daily_remaining_usd <= 0:
                raise CreditsExhaustedError(
                    f"Credits exhausted. Resets at: {rl.reset_at}",
                    reset_at=rl.reset_at,
                    remaining_usd=rl.daily_remaining_usd,
                )

            if rl.credits_remaining is not None and rl.credits_remaining <= 0:
                raise CreditsExhaustedError(
                    f"Credits exhausted. Resets at: {rl.reset_at}",
                    reset_at=rl.reset_at,
                    remaining_usd=rl.credits_remaining,
                )

            raise RateLimitError(
                f"Rate limited. Retry after: {retry_seconds}s",
                retry_after=retry_seconds,
            )

        response.raise_for_status()

    async def _request_with_retry(
        self,
        url: str,
        headers: dict[str, str],
        *,
        follow_redirects: bool = True,
    ) -> httpx.Response:
        max_retries = self._config.max_retries
        backoff = self._config.retry_backoff_factor

        async with httpx.AsyncClient(
            timeout=self._config.timeout,
            follow_redirects=follow_redirects,
        ) as client:
            last_exc: Exception | None = None
            for attempt in range(max_retries + 1):
                try:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code in (500, 503) and attempt < max_retries:
                        await asyncio.sleep(backoff * (2**attempt))
                        continue
                    return resp
                except (httpx.TransportError, httpx.TimeoutException) as exc:
                    last_exc = exc
                    if attempt < max_retries:
                        await asyncio.sleep(backoff * (2**attempt))
                    continue

            raise OpenAlexError(f"Max retries exceeded: {last_exc}") from last_exc

    async def get_json(self, endpoint: str, params: dict | None = None) -> dict:
        url = self._build_url(endpoint, params)
        headers = self._get_headers()
        resp = await self._request_with_retry(url, headers)

        if resp.status_code == 429:
            rl = parse_rate_limit_headers(resp.headers)
            retry_after_raw = resp.headers.get("Retry-After")
            retry_seconds = int(retry_after_raw) if retry_after_raw else None

            if _is_credits_exhausted(rl):
                raise CreditsExhaustedError(
                    f"Credits exhausted. Resets at: {rl.reset_at}",
                    reset_at=rl.reset_at,
                    remaining_usd=rl.daily_remaining_usd or 0.0,
                )

            if retry_seconds and retry_seconds > 0 and self._config.max_retries > 0:
                await asyncio.sleep(retry_seconds)
                resp = await self._request_with_retry(url, headers)
            else:
                raise RateLimitError(
                    "Rate limited",
                    retry_after=retry_seconds,
                )

        if resp.status_code not in (200, 206):
            self._handle_error_response(resp)

        return resp.json()

    async def get_raw(
        self,
        url: str,
        *,
        follow_redirects: bool = True,
    ) -> tuple[bytes, httpx.Headers]:
        headers = self._get_headers()
        if self._config.api_key:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}api_key={self._config.api_key}"

        async with httpx.AsyncClient(
            timeout=self._config.timeout,
            follow_redirects=False,
        ) as client:
            resp = await client.get(url, headers=headers)

            if resp.status_code == 302:
                redirect_headers = resp.headers
                location = redirect_headers.get("location", "")
                if location:
                    cdn_resp = await client.get(
                        location,
                        headers=headers,
                        follow_redirects=True,
                    )
                    return cdn_resp.content, redirect_headers
                return resp.content, redirect_headers

            if resp.status_code not in (200, 206):
                self._handle_error_response(resp)

            return resp.content, resp.headers

    async def get_rate_limit_status(self) -> dict[str, Any]:
        data = await self.get_json("rate-limit")
        return data


class SyncOpenAlexClient:
    def __init__(self) -> None:
        self._config = config

    def _build_url(self, endpoint: str, params: dict | None = None) -> str:
        base = self._config.base_url.rstrip("/")
        url = f"{base}/{endpoint}"
        query_parts: list[str] = []

        if params:
            for k, v in params.items():
                if v is None:
                    continue
                query_parts.append(f"{k}={v}")

        if self._config.api_key:
            query_parts.append(f"api_key={self._config.api_key}")

        if query_parts:
            url = f"{url}?{'&'.join(query_parts)}"

        return url

    def _get_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._config.user_agent:
            headers["User-Agent"] = self._config.user_agent
        return headers

    def _handle_error_response(self, response: httpx.Response) -> None:
        if response.status_code == 404:
            raise NotFoundError(f"Not found: {response.url}")
        if response.status_code == 400:
            try:
                data = response.json()
                msg = data.get("error", data.get("message", response.text))
            except Exception:
                msg = response.text
            raise QueryError(f"Bad request: {msg}")
        if response.status_code == 401:
            try:
                data = response.json()
                msg = data.get("error", data.get("message", response.text))
            except Exception:
                msg = response.text
            raise QueryError(f"Unauthorized: {msg}")
        if response.status_code == 429:
            rl = parse_rate_limit_headers(response.headers)
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after else None
            if _is_credits_exhausted(rl):
                raise CreditsExhaustedError(
                    f"Credits exhausted. Resets at: {rl.reset_at}",
                    reset_at=rl.reset_at,
                    remaining_usd=rl.daily_remaining_usd or 0.0,
                )
            raise RateLimitError(
                f"Rate limited. Retry after: {retry_seconds}s",
                retry_after=retry_seconds,
            )
        response.raise_for_status()

    def get_json(self, endpoint: str, params: dict | None = None) -> dict:
        url = self._build_url(endpoint, params)
        headers = self._get_headers()
        max_retries = self._config.max_retries
        backoff = self._config.retry_backoff_factor

        with httpx.Client(timeout=self._config.timeout) as client:
            last_exc: Exception | None = None
            for attempt in range(max_retries + 1):
                try:
                    resp = client.get(url, headers=headers)
                    if resp.status_code == 429:
                        rl = parse_rate_limit_headers(resp.headers)
                        if _is_credits_exhausted(rl):
                            raise CreditsExhaustedError(
                                f"Credits exhausted. Resets at: {rl.reset_at}",
                                reset_at=rl.reset_at,
                                remaining_usd=rl.daily_remaining_usd or 0.0,
                            )
                        retry_after_raw = resp.headers.get("Retry-After")
                        retry_seconds = (
                            int(retry_after_raw) if retry_after_raw else None
                        )
                        if retry_seconds and attempt < max_retries:
                            time.sleep(retry_seconds)
                            continue
                        raise RateLimitError("Rate limited", retry_after=retry_seconds)
                    if resp.status_code in (500, 503) and attempt < max_retries:
                        time.sleep(backoff * (2**attempt))
                        continue
                    if resp.status_code not in (200, 206):
                        self._handle_error_response(resp)
                    return resp.json()
                except (httpx.TransportError, httpx.TimeoutException) as exc:
                    last_exc = exc
                    if attempt < max_retries:
                        time.sleep(backoff * (2**attempt))
                        continue
            raise OpenAlexError(f"Max retries exceeded: {last_exc}") from last_exc

    def get_raw(
        self,
        url: str,
    ) -> tuple[bytes, httpx.Headers]:
        headers = self._get_headers()
        if self._config.api_key:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}api_key={self._config.api_key}"

        with httpx.Client(
            timeout=self._config.timeout, follow_redirects=False
        ) as client:
            resp = client.get(url, headers=headers)

            if resp.status_code == 302:
                redirect_headers = resp.headers
                location = redirect_headers.get("location", "")
                if location:
                    cdn_resp = client.get(
                        location, headers=headers, follow_redirects=True
                    )
                    return cdn_resp.content, redirect_headers
                return resp.content, redirect_headers

            if resp.status_code not in (200, 206):
                self._handle_error_response(resp)

            return resp.content, resp.headers

    def get_rate_limit_status(self) -> dict[str, Any]:
        return self.get_json("rate-limit")


def _is_credits_exhausted(rl: RateLimitInfo) -> bool:
    if rl.daily_remaining_usd is not None and rl.daily_remaining_usd <= 0:
        return True
    if rl.credits_remaining is not None and rl.credits_remaining <= 0:
        return True
    return False
