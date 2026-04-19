from __future__ import annotations

import pytest

from openalexpy.query import Authors
from openalexpy.query import AuthorsSync
from openalexpy.query import Awards
from openalexpy.query import Domains
from openalexpy.query import Fields
from openalexpy.query import Funders
from openalexpy.query import Institutions
from openalexpy.query import Keywords
from openalexpy.query import Publishers
from openalexpy.query import Sources
from openalexpy.query import Subfields
from openalexpy.query import Topics
from openalexpy.query import Works
from openalexpy.query import WorksSync


class TestQueryImmutability:
    def test_filter_returns_new_instance(self):
        w1 = Works()
        w2 = w1.filter(publication_year=2020)
        assert w1 is not w2
        assert w1.params == {}
        assert "filter" in w2.params

    def test_chain_does_not_mutate_original(self):
        w1 = Works()
        w2 = w1.filter(publication_year=2020)
        w3 = w2.filter(is_oa=True)
        assert w1.params == {}
        assert "is_oa" not in w2.params.get("filter", "")
        assert "is_oa" in w3.params.get("filter", "")

    def test_search_returns_new_instance(self):
        w1 = Works()
        w2 = w1.search("dna")
        assert "search" not in w1.params
        assert w2.params["search"] == "dna"

    def test_sort_returns_new_instance(self):
        w1 = Works()
        w2 = w1.sort(cited_by_count="desc")
        assert "sort" not in w1.params
        assert w2.params["sort"] == "cited_by_count:desc"


class TestWorksQuery:
    def test_basic_filter(self):
        w = Works().filter(publication_year=2020, is_oa=True)
        f = w.params["filter"]
        parts = set(f.split(","))
        assert "publication_year:2020" in parts
        assert "is_oa:true" in parts

    def test_nested_filter(self):
        w = Works().filter(authorships={"institutions": {"ror": "04pp8hn57"}})
        assert w.params["filter"] == "authorships.institutions.ror:04pp8hn57"

    def test_filter_or(self):
        w = Works().filter_or(
            doi=["10.1016/s0924-9338(99)80239-9", "10.1002/andp.19213690304"]
        )
        assert "doi:" in w.params["filter"]
        assert "|" in w.params["filter"]

    def test_filter_not(self):
        w = Works().filter_not(country_code="us")
        assert "!us" in w.params["filter"]

    def test_filter_gt(self):
        w = Works().filter_gt(cited_by_count=100)
        assert ">100" in w.params["filter"]

    def test_filter_lt(self):
        w = Works().filter_lt(publication_year=2020)
        assert "<2020" in w.params["filter"]

    def test_search(self):
        w = Works().search("fierce creatures")
        assert w.params["search"] == "fierce creatures"

    def test_search_filter(self):
        w = Authors().search_filter(display_name="einstein")
        assert "display_name.search:einstein" in w.params["filter"]

    def test_similar(self):
        w = Works().similar("machine learning for drug discovery")
        assert w.params["search.semantic"] == "machine learning for drug discovery"

    def test_similar_with_filter(self):
        w = (
            Works()
            .similar("climate change")
            .filter(publication_year=">2020")
            .filter(is_oa=True)
        )
        assert w.params["search.semantic"] == "climate change"
        assert "publication_year:%3E2020" in w.params["filter"]
        assert "is_oa:true" in w.params["filter"]

    def test_sort(self):
        w = Works().sort(cited_by_count="desc")
        assert w.params["sort"] == "cited_by_count:desc"

    def test_group_by(self):
        w = Works().group_by("institutions.country_code")
        assert w.params["group-by"] == "institutions.country_code"

    def test_sample(self):
        w = Works().sample(100, seed=535)
        assert w.params["sample"] == "100"
        assert w.params["seed"] == "535"

    def test_sample_no_seed(self):
        w = Works().sample(50)
        assert w.params["sample"] == "50"
        assert "seed" not in w.params

    def test_select_list(self):
        w = Works().select(["id", "doi", "display_name"])
        assert w.params["select"] == "id,doi,display_name"

    def test_select_string(self):
        w = Works().select("id,doi")
        assert w.params["select"] == "id,doi"


class TestAllEntities:
    @pytest.mark.parametrize(
        "cls",
        [
            Works,
            Authors,
            Sources,
            Institutions,
            Topics,
            Publishers,
            Funders,
            Awards,
            Keywords,
            Domains,
            Fields,
            Subfields,
        ],
    )
    def test_endpoints(self, cls):
        q = cls()
        assert q.endpoint is not None
        assert isinstance(q.endpoint, str)

    @pytest.mark.parametrize(
        "cls",
        [
            Works,
            Authors,
            Sources,
            Institutions,
            Topics,
            Publishers,
            Funders,
            Awards,
            Keywords,
            Domains,
            Fields,
            Subfields,
        ],
    )
    def test_filter_chainable(self, cls):
        q = cls().filter(works_count=">0")
        assert "filter" in q.params


class TestSyncQueries:
    def test_sync_works_filter(self):
        w = WorksSync().filter(publication_year=2020)
        assert "publication_year:2020" in w.params["filter"]

    def test_sync_works_similar(self):
        w = WorksSync().similar("test query")
        assert w.params["search.semantic"] == "test query"

    def test_sync_authors(self):
        a = AuthorsSync()
        assert a.endpoint == "authors"


class TestPerValidation:
    def test_per_page_none(self):
        from openalexpy.query import _validate_per_page

        assert _validate_per_page(None) == 25

    def test_per_page_valid(self):
        from openalexpy.query import _validate_per_page

        assert _validate_per_page(50) == 50

    def test_per_page_too_large(self):
        from openalexpy.query import _validate_per_page

        with pytest.raises(ValueError, match="between 1 and 100"):
            _validate_per_page(1000)

    def test_per_page_string(self):
        from openalexpy.query import _validate_per_page

        with pytest.raises(ValueError, match="not a string"):
            _validate_per_page("100")

    def test_per_page_zero(self):
        from openalexpy.query import _validate_per_page

        with pytest.raises(ValueError, match="between 1 and 100"):
            _validate_per_page(0)
