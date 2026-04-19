from __future__ import annotations

import copy
from typing import Any
from typing import TypeVar

from openalexpy.client import AsyncOpenAlexClient
from openalexpy.client import SyncOpenAlexClient
from openalexpy.content import PDF
from openalexpy.content import TEI
from openalexpy.entities import Author
from openalexpy.entities import AutocompleteResult
from openalexpy.entities import Award
from openalexpy.entities import Domain
from openalexpy.entities import Field
from openalexpy.entities import Funder
from openalexpy.entities import GroupByResult
from openalexpy.entities import Institution
from openalexpy.entities import Keyword
from openalexpy.entities import Publisher
from openalexpy.entities import Source
from openalexpy.entities import Subfield
from openalexpy.entities import Topic
from openalexpy.entities import Work
from openalexpy.filters import build_filter_params
from openalexpy.filters import build_search_filter_params
from openalexpy.filters import build_sort_params
from openalexpy.filters import merge_filter_strings
from openalexpy.pagination import AsyncPaginator
from openalexpy.pagination import SyncPaginator
from openalexpy.response import OpenAlexResponse
from openalexpy.response import parse_response_meta

T = TypeVar("T")

_ENDPOINT_MAP: dict[str, str] = {
    "Works": "works",
    "Authors": "authors",
    "Sources": "sources",
    "Institutions": "institutions",
    "Topics": "topics",
    "Publishers": "publishers",
    "Funders": "funders",
    "Awards": "awards",
    "Keywords": "keywords",
    "Domains": "domains",
    "Fields": "fields",
    "Subfields": "subfields",
}

_MODEL_MAP: dict[str, type] = {
    "Works": Work,
    "Authors": Author,
    "Sources": Source,
    "Institutions": Institution,
    "Topics": Topic,
    "Publishers": Publisher,
    "Funders": Funder,
    "Awards": Award,
    "Keywords": Keyword,
    "Domains": Domain,
    "Fields": Field,
    "Subfields": Subfield,
}


def _validate_per_page(per_page: int | None) -> int:
    if per_page is None:
        return 25
    if isinstance(per_page, str):
        raise ValueError("per_page must be an integer, not a string")
    if not isinstance(per_page, int):
        raise ValueError("per_page must be an integer")
    if per_page < 1 or per_page > 100:
        raise ValueError("per_page must be between 1 and 100")
    return per_page


class Query:
    def __init__(
        self,
        endpoint: str,
        model_class: type,
        params: dict | None = None,
    ) -> None:
        self._endpoint = endpoint
        self._model_class = model_class
        self._params = copy.deepcopy(params) if params else {}

    def _clone(self, **overrides: Any) -> Query:
        new = Query(self._endpoint, self._model_class, self._params)
        new._params.update(overrides)
        return new

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def model_class(self) -> type:
        return self._model_class

    @property
    def params(self) -> dict:
        return copy.deepcopy(self._params)

    def filter(self, **kwargs: Any) -> Query:
        new = self._clone()
        filter_str = build_filter_params(kwargs)
        existing = new._params.get("filter")
        new._params["filter"] = merge_filter_strings(existing, filter_str)
        return new

    def filter_and(self, **kwargs: Any) -> Query:
        return self.filter(**kwargs)

    def filter_or(self, **kwargs: Any) -> Query:
        from openalexpy.filters import or_

        new = self._clone()
        filter_str = build_filter_params(or_(kwargs))
        existing = new._params.get("filter")
        new._params["filter"] = merge_filter_strings(existing, filter_str)
        return new

    def filter_not(self, **kwargs: Any) -> Query:
        from openalexpy.filters import not_

        wrapped = {k: not_(v) for k, v in kwargs.items()}
        return self.filter(**wrapped)

    def filter_gt(self, **kwargs: Any) -> Query:
        from openalexpy.filters import gt_

        wrapped = {k: gt_(v) for k, v in kwargs.items()}
        return self.filter(**wrapped)

    def filter_lt(self, **kwargs: Any) -> Query:
        from openalexpy.filters import lt_

        wrapped = {k: lt_(v) for k, v in kwargs.items()}
        return self.filter(**wrapped)

    def search(self, query: str) -> Query:
        new = self._clone()
        new._params["search"] = query
        return new

    def search_filter(self, **kwargs: Any) -> Query:
        new = self._clone()
        filter_str = build_search_filter_params(kwargs)
        existing = new._params.get("filter")
        new._params["filter"] = merge_filter_strings(existing, filter_str)
        return new

    def sort(self, **kwargs: Any) -> Query:
        new = self._clone()
        new._params["sort"] = build_sort_params(kwargs)
        return new

    def group_by(self, key: str) -> Query:
        new = self._clone()
        new._params["group-by"] = key
        return new

    def sample(self, n: int, seed: int | None = None) -> Query:
        new = self._clone()
        new._params["sample"] = str(n)
        if seed is not None:
            new._params["seed"] = str(seed)
        return new

    def select(self, fields: list[str] | str) -> Query:
        new = self._clone()
        if isinstance(fields, list):
            new._params["select"] = ",".join(fields)
        else:
            new._params["select"] = fields
        return new


class AsyncQuery(Query):
    async def get(
        self,
        per_page: int | None = None,
        return_meta: bool = False,
        cursor: str | None = None,
        page: int | None = None,
    ) -> list | OpenAlexResponse:
        pp = _validate_per_page(per_page)
        client = AsyncOpenAlexClient()

        params = copy.deepcopy(self._params)
        params["per_page"] = str(pp)

        if cursor is not None:
            params["cursor"] = cursor
        elif page is not None:
            params["page"] = str(page)

        if "group-by" in params:
            data = await client.get_json(self._endpoint, params)
            groups = data.get("group_by", [])
            group_results = [GroupByResult(**g) for g in groups]
            if return_meta:
                return OpenAlexResponse(
                    results=[],
                    meta=parse_response_meta(data.get("meta", {})),
                    rate_limit=None,
                    group_by=group_results,
                )
            return group_results

        data = await client.get_json(self._endpoint, params)

        results_raw = data.get("results", [])
        results = [self._model_class(**r) for r in results_raw]

        if return_meta:
            meta = parse_response_meta(data.get("meta", {}))
            return OpenAlexResponse(
                results=results,
                meta=meta,
                rate_limit=None,
            )

        return results

    async def count(self) -> int:
        client = AsyncOpenAlexClient()
        params = copy.deepcopy(self._params)
        params["per_page"] = "1"
        data = await client.get_json(self._endpoint, params)
        return data.get("meta", {}).get("count", 0)

    async def random(self) -> Any:
        client = AsyncOpenAlexClient()
        endpoint = f"{self._endpoint}/random"
        data = await client.get_json(endpoint)
        return self._model_class(**data)

    async def get_by_id(self, entity_id: str) -> Any:
        client = AsyncOpenAlexClient()
        endpoint = f"{self._endpoint}/{entity_id}"
        data = await client.get_json(endpoint)

        if self._model_class == Work:
            work = Work(**data)
            work_id = work.id or entity_id
            work_id = work_id.replace("https://openalex.org/", "")
            work._pdf = PDF(work_id)
            work._tei = TEI(work_id)
            return work

        return self._model_class(**data)

    async def get_batch(self, ids: list[str]) -> list:
        if len(ids) > 100:
            raise ValueError("Maximum 100 IDs per batch request")
        pipe_ids = "|".join(ids)
        new = self._clone()
        existing = new._params.get("filter")
        new._params["filter"] = merge_filter_strings(existing, f"openalex:{pipe_ids}")
        return await new.get(per_page=len(ids))

    def paginate(
        self,
        method: str = "cursor",
        per_page: int = 25,
        n_max: int | None = 10000,
    ) -> AsyncPaginator:
        _validate_per_page(per_page)

        if "sample" in self._params and method == "cursor":
            raise ValueError(
                "Sample is not compatible with cursor pagination. "
                "Use method='page' instead."
            )

        client = AsyncOpenAlexClient()
        base_params = copy.deepcopy(self._params)

        async def fetch_func(p: dict) -> dict:
            merged = {**base_params, **p}
            return await client.get_json(self._endpoint, merged)

        return AsyncPaginator(
            fetch_func,
            self._model_class,
            method=method,
            per_page=per_page,
            n_max=n_max,
        )

    async def autocomplete(self, query: str) -> list[AutocompleteResult]:
        client = AsyncOpenAlexClient()
        params = copy.deepcopy(self._params)
        params["q"] = query
        data = await client.get_json(f"autocomplete/{self._endpoint}", params)
        results = data.get("results", [])
        return [AutocompleteResult(**r) for r in results]


class SyncQuery(Query):
    def get(
        self,
        per_page: int | None = None,
        return_meta: bool = False,
        cursor: str | None = None,
        page: int | None = None,
    ) -> list | OpenAlexResponse:
        pp = _validate_per_page(per_page)
        client = SyncOpenAlexClient()

        params = copy.deepcopy(self._params)
        params["per_page"] = str(pp)

        if cursor is not None:
            params["cursor"] = cursor
        elif page is not None:
            params["page"] = str(page)

        if "group-by" in params:
            data = client.get_json(self._endpoint, params)
            groups = data.get("group_by", [])
            group_results = [GroupByResult(**g) for g in groups]
            if return_meta:
                return OpenAlexResponse(
                    results=[],
                    meta=parse_response_meta(data.get("meta", {})),
                    rate_limit=None,
                    group_by=group_results,
                )
            return group_results

        data = client.get_json(self._endpoint, params)

        results_raw = data.get("results", [])
        results = [self._model_class(**r) for r in results_raw]

        if return_meta:
            meta = parse_response_meta(data.get("meta", {}))
            return OpenAlexResponse(
                results=results,
                meta=meta,
                rate_limit=None,
            )

        return results

    def count(self) -> int:
        client = SyncOpenAlexClient()
        params = copy.deepcopy(self._params)
        params["per_page"] = "1"
        data = client.get_json(self._endpoint, params)
        return data.get("meta", {}).get("count", 0)

    def random(self) -> Any:
        client = SyncOpenAlexClient()
        endpoint = f"{self._endpoint}/random"
        data = client.get_json(endpoint)
        return self._model_class(**data)

    def get_by_id(self, entity_id: str) -> Any:
        client = SyncOpenAlexClient()
        endpoint = f"{self._endpoint}/{entity_id}"
        data = client.get_json(endpoint)

        if self._model_class == Work:
            work = Work(**data)
            work_id = work.id or entity_id
            work_id = work_id.replace("https://openalex.org/", "")
            work._pdf = PDF(work_id)
            work._tei = TEI(work_id)
            return work

        return self._model_class(**data)

    def get_batch(self, ids: list[str]) -> list:
        if len(ids) > 100:
            raise ValueError("Maximum 100 IDs per batch request")
        new = self._clone()
        pipe_ids = "|".join(ids)
        existing = new._params.get("filter")
        new._params["filter"] = merge_filter_strings(existing, f"openalex:{pipe_ids}")
        return new.get(per_page=len(ids))

    def paginate(
        self,
        method: str = "cursor",
        per_page: int = 25,
        n_max: int | None = 10000,
    ) -> SyncPaginator:
        _validate_per_page(per_page)

        if "sample" in self._params and method == "cursor":
            raise ValueError(
                "Sample is not compatible with cursor pagination. "
                "Use method='page' instead."
            )

        client = SyncOpenAlexClient()
        base_params = copy.deepcopy(self._params)

        def fetch_func(p: dict) -> dict:
            merged = {**base_params, **p}
            return client.get_json(self._endpoint, merged)

        return SyncPaginator(
            fetch_func,
            self._model_class,
            method=method,
            per_page=per_page,
            n_max=n_max,
        )

    def autocomplete(self, query: str) -> list[AutocompleteResult]:
        client = SyncOpenAlexClient()
        params = copy.deepcopy(self._params)
        params["q"] = query
        data = client.get_json(f"autocomplete/{self._endpoint}", params)
        results = data.get("results", [])
        return [AutocompleteResult(**r) for r in results]


class Works(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("works", Work)

    def similar(self, text: str) -> Works:
        new = Works.__new__(Works)
        new._endpoint = self._endpoint
        new._model_class = self._model_class
        new._params = copy.deepcopy(self._params)
        new._params["search.semantic"] = text
        return new


class Authors(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("authors", Author)


class Sources(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("sources", Source)


class Institutions(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("institutions", Institution)


class Topics(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("topics", Topic)


class Publishers(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("publishers", Publisher)


class Funders(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("funders", Funder)


class Awards(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("awards", Award)


class Keywords(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("keywords", Keyword)


class Domains(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("domains", Domain)


class Fields(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("fields", Field)


class Subfields(AsyncQuery):
    def __init__(self) -> None:
        super().__init__("subfields", Subfield)


class WorksSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("works", Work)

    def similar(self, text: str) -> WorksSync:
        new = WorksSync.__new__(WorksSync)
        new._endpoint = self._endpoint
        new._model_class = self._model_class
        new._params = copy.deepcopy(self._params)
        new._params["search.semantic"] = text
        return new


class AuthorsSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("authors", Author)


class SourcesSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("sources", Source)


class InstitutionsSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("institutions", Institution)


class TopicsSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("topics", Topic)


class PublishersSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("publishers", Publisher)


class FundersSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("funders", Funder)


class AwardsSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("awards", Award)


class KeywordsSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("keywords", Keyword)


class DomainsSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("domains", Domain)


class FieldsSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("fields", Field)


class SubfieldsSync(SyncQuery):
    def __init__(self) -> None:
        super().__init__("subfields", Subfield)


async def autocomplete(query: str) -> list[AutocompleteResult]:
    client = AsyncOpenAlexClient()
    params: dict[str, str] = {"q": query}
    data = await client.get_json("autocomplete", params)
    results = data.get("results", [])
    return [AutocompleteResult(**r) for r in results]


def autocomplete_sync(query: str) -> list[AutocompleteResult]:
    client = SyncOpenAlexClient()
    params: dict[str, str] = {"q": query}
    data = client.get_json("autocomplete", params)
    results = data.get("results", [])
    return [AutocompleteResult(**r) for r in results]
