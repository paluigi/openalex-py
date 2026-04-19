from __future__ import annotations

from urllib.parse import quote_plus


class _LogicalExpression:
    token: str = ""

    def __init__(self, value: str | int | float | bool) -> None:
        self.value = value

    def __str__(self) -> str:
        v = _quote_oa_value(self.value)
        return f"{self.token}{v}"


class not_(_LogicalExpression):
    token = "!"


class gt_(_LogicalExpression):
    token = ">"


class lt_(_LogicalExpression):
    token = "<"


class or_(dict):
    pass


def _quote_oa_value(v: object) -> str:
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, _LogicalExpression):
        inner = _quote_oa_value(v.value)
        return f"{v.token}{inner}"
    if isinstance(v, str):
        return quote_plus(v)
    return str(v)


def _flatten_kv(
    d: dict,
    prefix: str | None = None,
    logical: str = "+",
) -> str:
    parts: list[str] = []
    is_or = isinstance(d, or_)

    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k

        if isinstance(v, dict):
            child_logical = "|" if is_or else logical
            parts.append(_flatten_kv(v, key, child_logical))
        elif isinstance(v, list):
            sep = "|" if is_or else logical
            items: list[str] = []
            for item in v:
                if isinstance(item, dict):
                    items.append(_flatten_kv(item, key, logical))
                else:
                    items.append(_quote_oa_value(item))
            if any(isinstance(item, dict) for item in v):
                parts.append(sep.join(items))
            else:
                parts.append(f"{key}:{sep.join(items)}")
        else:
            parts.append(f"{key}:{_quote_oa_value(v)}")

    return ",".join(parts)


def build_filter_params(kwargs: dict, logical: str = "+") -> str:
    return _flatten_kv(kwargs, logical=logical)


def build_search_filter_params(kwargs: dict) -> str:
    parts: list[str] = []
    for k, v in kwargs.items():
        key = f"{k}.search"
        if isinstance(v, list):
            vals = "|".join(_quote_oa_value(item) for item in v)
            parts.append(f"{key}:{vals}")
        else:
            parts.append(f"{key}:{_quote_oa_value(v)}")
    return ",".join(parts)


def merge_filter_strings(existing: str | None, new: str) -> str:
    if existing:
        return f"{existing},{new}"
    return new


def build_sort_params(kwargs: dict) -> str:
    parts: list[str] = []
    for k, v in kwargs.items():
        parts.append(f"{k}:{v}")
    return ",".join(parts)
