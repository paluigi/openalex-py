from __future__ import annotations

from openalexpy.filters import _flatten_kv
from openalexpy.filters import _quote_oa_value
from openalexpy.filters import build_filter_params
from openalexpy.filters import build_search_filter_params
from openalexpy.filters import build_sort_params
from openalexpy.filters import gt_
from openalexpy.filters import lt_
from openalexpy.filters import merge_filter_strings
from openalexpy.filters import not_
from openalexpy.filters import or_


class TestQuoteOAValue:
    def test_string(self):
        assert _quote_oa_value("hello") == "hello"

    def test_string_with_spaces(self):
        assert _quote_oa_value("hello world") == "hello+world"

    def test_bool_true(self):
        assert _quote_oa_value(True) == "true"

    def test_bool_false(self):
        assert _quote_oa_value(False) == "false"

    def test_int(self):
        assert _quote_oa_value(2020) == "2020"

    def test_not_expression(self):
        expr = not_("us")
        assert _quote_oa_value(expr) == "!us"

    def test_gt_expression(self):
        expr = gt_(100)
        assert _quote_oa_value(expr) == ">100"

    def test_lt_expression(self):
        expr = lt_(2020)
        assert _quote_oa_value(expr) == "<2020"


class TestFlattenKV:
    def test_simple_filter(self):
        result = _flatten_kv({"publication_year": 2020})
        assert result == "publication_year:2020"

    def test_bool_filter(self):
        result = _flatten_kv({"is_oa": True})
        assert result == "is_oa:true"

    def test_nested_filter(self):
        result = _flatten_kv({"institutions": {"country_code": "us"}})
        assert result == "institutions.country_code:us"

    def test_deeply_nested_filter(self):
        result = _flatten_kv({"authorships": {"institutions": {"ror": "04pp8hn57"}}})
        assert result == "authorships.institutions.ror:04pp8hn57"

    def test_list_values_and(self):
        result = _flatten_kv({"institutions": {"country_code": ["fr", "gb"]}})
        assert result == "institutions.country_code:fr+gb"

    def test_or_dict(self):
        result = _flatten_kv(or_({"country_code": ["fr", "gb"]}))
        assert result == "country_code:fr|gb"

    def test_multiple_keys(self):
        result = _flatten_kv({"publication_year": 2020, "is_oa": True})
        parts = set(result.split(","))
        assert "publication_year:2020" in parts
        assert "is_oa:true" in parts

    def test_not_in_filter(self):
        wrapped = {"country_code": not_("us")}
        result = _flatten_kv(wrapped)
        assert result == "country_code:!us"

    def test_gt_in_filter(self):
        wrapped = {"cited_by_count": gt_(100)}
        result = _flatten_kv(wrapped)
        assert result == "cited_by_count:>100"

    def test_lt_in_filter(self):
        wrapped = {"publication_year": lt_(2020)}
        result = _flatten_kv(wrapped)
        assert result == "publication_year:<2020"

    def test_or_nested_filter(self):
        result = _flatten_kv(or_({"institutions": {"country_code": ["fr", "gb"]}}))
        assert result == "institutions.country_code:fr|gb"


class TestBuildFilterParams:
    def test_simple(self):
        result = build_filter_params({"publication_year": 2020})
        assert result == "publication_year:2020"

    def test_nested(self):
        result = build_filter_params(
            {"authorships": {"institutions": {"ror": "04pp8hn57"}}}
        )
        assert result == "authorships.institutions.ror:04pp8hn57"


class TestBuildSearchFilterParams:
    def test_search_filter(self):
        result = build_search_filter_params({"display_name": "einstein"})
        assert result == "display_name.search:einstein"

    def test_search_filter_title(self):
        result = build_search_filter_params({"title": "cubist"})
        assert result == "title.search:cubist"


class TestBuildSortParams:
    def test_single_sort(self):
        result = build_sort_params({"cited_by_count": "desc"})
        assert result == "cited_by_count:desc"

    def test_multiple_sort(self):
        result = build_sort_params(
            {"cited_by_count": "desc", "publication_year": "asc"}
        )
        parts = set(result.split(","))
        assert "cited_by_count:desc" in parts
        assert "publication_year:asc" in parts


class TestMergeFilterStrings:
    def test_merge_empty(self):
        result = merge_filter_strings(None, "publication_year:2020")
        assert result == "publication_year:2020"

    def test_merge_existing(self):
        result = merge_filter_strings("publication_year:2020", "is_oa:true")
        assert result == "publication_year:2020,is_oa:true"
