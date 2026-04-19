from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Iterator
from typing import Generic
from typing import TypeVar

T = TypeVar("T")


class AsyncPaginator(Generic[T]):
    def __init__(
        self,
        fetch_func,
        model_class: type[T],
        *,
        method: str = "cursor",
        per_page: int = 25,
        n_max: int | None = 10000,
    ) -> None:
        self._fetch_func = fetch_func
        self._model_class = model_class
        self._method = method
        self._per_page = per_page
        self._n_max = n_max
        self._next_value: str | int | None = "*" if method == "cursor" else 1
        self._total_fetched = 0
        self._page_count = 0

    def __aiter__(self) -> AsyncIterator[list[T]]:
        return self

    async def __anext__(self) -> list[T]:
        if self._next_value is None:
            raise StopAsyncIteration

        if self._n_max is not None and self._total_fetched >= self._n_max:
            raise StopAsyncIteration

        params: dict = {"per_page": str(self._per_page)}

        if self._method == "cursor":
            params["cursor"] = str(self._next_value)
        else:
            params["page"] = str(self._next_value)

        data = await self._fetch_func(params)

        results_raw = data.get("results", [])
        meta = data.get("meta", {})
        results: list[T] = []

        for item in results_raw:
            if isinstance(item, dict):
                results.append(self._model_class(**item))
            else:
                results.append(item)

        self._page_count += 1
        self._total_fetched += len(results)

        if self._method == "cursor":
            self._next_value = meta.get("next_cursor")
        else:
            if len(results) < self._per_page:
                self._next_value = None
            else:
                self._next_value = self._page_count + 1

        if not results:
            raise StopAsyncIteration

        return results


class SyncPaginator(Generic[T]):
    def __init__(
        self,
        fetch_func,
        model_class: type[T],
        *,
        method: str = "cursor",
        per_page: int = 25,
        n_max: int | None = 10000,
    ) -> None:
        self._fetch_func = fetch_func
        self._model_class = model_class
        self._method = method
        self._per_page = per_page
        self._n_max = n_max
        self._next_value: str | int | None = "*" if method == "cursor" else 1
        self._total_fetched = 0
        self._page_count = 0

    def __iter__(self) -> Iterator[list[T]]:
        return self

    def __next__(self) -> list[T]:
        if self._next_value is None:
            raise StopIteration

        if self._n_max is not None and self._total_fetched >= self._n_max:
            raise StopIteration

        params: dict = {"per_page": str(self._per_page)}

        if self._method == "cursor":
            params["cursor"] = str(self._next_value)
        else:
            params["page"] = str(self._next_value)

        data = self._fetch_func(params)

        results_raw = data.get("results", [])
        meta = data.get("meta", {})
        results: list[T] = []

        for item in results_raw:
            if isinstance(item, dict):
                results.append(self._model_class(**item))
            else:
                results.append(item)

        self._page_count += 1
        self._total_fetched += len(results)

        if self._method == "cursor":
            self._next_value = meta.get("next_cursor")
        else:
            if len(results) < self._per_page:
                self._next_value = None
            else:
                self._next_value = self._page_count + 1

        if not results:
            raise StopIteration

        return results
