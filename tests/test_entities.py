from __future__ import annotations

from openalexpy.entities import Author
from openalexpy.entities import Authorship
from openalexpy.entities import AutocompleteResult
from openalexpy.entities import Award
from openalexpy.entities import DehydratedInstitution
from openalexpy.entities import Funder
from openalexpy.entities import GroupByResult
from openalexpy.entities import Institution
from openalexpy.entities import Keyword
from openalexpy.entities import OpenAccess
from openalexpy.entities import Publisher
from openalexpy.entities import Source
from openalexpy.entities import Topic
from openalexpy.entities import Work


class TestWorkModel:
    def test_basic_work(self):
        w = Work(
            id="W2741809807",
            doi="https://doi.org/10.7717/peerj.4375",
            title="Test work",
            publication_year=2020,
            cited_by_count=42,
        )
        assert w.id == "W2741809807"
        assert w.doi == "https://doi.org/10.7717/peerj.4375"
        assert w.title == "Test work"
        assert w.publication_year == 2020
        assert w.cited_by_count == 42

    def test_work_with_authorships(self):
        w = Work(
            authorships=[
                Authorship(
                    author={"id": "A123", "display_name": "Test Author"},
                    institutions=[DehydratedInstitution(id="I456")],
                )
            ]
        )
        assert len(w.authorships) == 1
        assert w.authorships[0].author.id == "A123"

    def test_work_abstract_inversion(self):
        w = Work(
            abstract_inverted_index={
                "Hello": [0],
                "world": [1],
            }
        )
        assert w.abstract == "Hello world"

    def test_work_abstract_none(self):
        w = Work()
        assert w.abstract is None

    def test_work_abstract_empty(self):
        w = Work(abstract_inverted_index={})
        assert w.abstract == ""

    def test_work_default_lists(self):
        w = Work()
        assert w.referenced_works == []
        assert w.related_works == []

    def test_work_extra_fields_allowed(self):
        w = Work(id="W123", unknown_field="test")
        assert w.id == "W123"

    def test_work_open_access(self):
        w = Work(
            open_access=OpenAccess(
                is_oa=True, oa_status="gold", oa_url="https://example.com"
            )
        )
        assert w.open_access.is_oa is True
        assert w.open_access.oa_status == "gold"


class TestAuthorModel:
    def test_basic_author(self):
        a = Author(
            id="A5027479191",
            display_name="Test Author",
            orcid="https://orcid.org/0000-0002-4297-0502",
            works_count=100,
        )
        assert a.id == "A5027479191"
        assert a.orcid == "https://orcid.org/0000-0002-4297-0502"
        assert a.works_count == 100


class TestInstitutionModel:
    def test_basic_institution(self):
        inst = Institution(
            id="I27837315",
            display_name="MIT",
            country_code="US",
            type="education",
        )
        assert inst.id == "I27837315"
        assert inst.country_code == "US"


class TestSourceModel:
    def test_basic_source(self):
        s = Source(
            id="S123",
            display_name="Nature",
            type="journal",
            issn=["0028-0836"],
        )
        assert s.id == "S123"
        assert s.issn == ["0028-0836"]


class TestTopicModel:
    def test_basic_topic(self):
        t = Topic(
            id="T123",
            display_name="Machine Learning",
            description="AI research",
        )
        assert t.id == "T123"
        assert t.description == "AI research"


class TestPublisherModel:
    def test_basic_publisher(self):
        p = Publisher(id="P4310320990", display_name="Elsevier")
        assert p.id == "P4310320990"


class TestFunderModel:
    def test_basic_funder(self):
        f = Funder(id="F4320322164", display_name="NIH")
        assert f.id == "F4320322164"


class TestAwardModel:
    def test_basic_award(self):
        a = Award(id="A123", display_name="Test Grant")
        assert a.id == "A123"


class TestKeywordModel:
    def test_basic_keyword(self):
        k = Keyword(id="K123", display_name="deep learning")
        assert k.id == "K123"


class TestGroupByResult:
    def test_group_by(self):
        g = GroupByResult(key="US", key_display_name="United States", count=42)
        assert g.key == "US"
        assert g.count == 42


class TestAutocompleteResult:
    def test_autocomplete(self):
        a = AutocompleteResult(
            id="I123",
            display_name="MIT",
            entity_type="institution",
        )
        assert a.entity_type == "institution"
