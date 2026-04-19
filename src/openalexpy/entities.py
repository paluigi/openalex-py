from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class OpenAlexBase(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class CountByYear(OpenAlexBase):
    year: int
    works_count: int = 0
    cited_by_count: int = 0


class DehydratedInstitution(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    ror: str | None = None
    country_code: str | None = None
    type: str | None = None


class DehydratedSource(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    issn: list[str] | None = None
    issn_l: str | None = None
    type: str | None = None


class AuthorPosition(OpenAlexBase):
    is_corresponding: bool = False
    position: str | None = None


class AuthorshipAuthor(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    orcid: str | None = None


class Authorship(OpenAlexBase):
    author: AuthorshipAuthor | None = None
    institutions: list[DehydratedInstitution] | None = None
    countries: list[str] | None = None
    is_corresponding: bool = False
    author_position: str | None = None
    raw_author_name: str | None = None
    raw_affiliation_strings: list[str] | None = None


class Location(OpenAlexBase):
    is_oa: bool = False
    landing_page_url: str | None = None
    pdf_url: str | None = None
    source: DehydratedSource | None = None
    license: str | None = None
    version: str | None = None


class OpenAccess(OpenAlexBase):
    is_oa: bool = False
    oa_status: str | None = None
    oa_url: str | None = None
    any_repository_has_fulltext: bool = False


class TopicDehydrated(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    field: DehydratedField | None = None
    subfield: DehydratedSubfield | None = None


class DehydratedField(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None


class DehydratedSubfield(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None


class DehydratedDomain(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None


class KeywordDehydrated(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    score: float | None = None


class ConceptDehydrated(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    wikidata: str | None = None
    level: int | None = None
    score: float | None = None


class SustainableDevGoal(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    score: float | None = None


class MeshTerm(OpenAlexBase):
    descriptor_ui: str | None = None
    descriptor_name: str | None = None
    qualifier_ui: str | None = None
    qualifier_name: str | None = None
    is_major_topic: bool = False


class Affiliation(OpenAlexBase):
    institution: DehydratedInstitution | None = None
    years: list[int] | None = None
    institution_display_name: str | None = None


class Work(OpenAlexBase):
    id: str | None = None
    doi: str | None = None
    title: str | None = None
    display_name: str | None = None
    publication_year: int | None = None
    publication_date: str | None = None
    type: str | None = None
    cited_by_count: int = 0
    is_oa: bool = False
    is_paratext: bool = False
    language: str | None = None
    relevance_score: float | None = None

    authorships: list[Authorship] | None = None
    primary_location: Location | None = None
    locations: list[Location] | None = None
    topics: list[TopicDehydrated] | None = None
    keywords: list[KeywordDehydrated] | None = None
    concepts: list[ConceptDehydrated] | None = None
    sustainable_development_goals: list[SustainableDevGoal] | None = None
    mesh: list[MeshTerm] | None = None

    referenced_works: list[str] = Field(default_factory=list)
    related_works: list[str] = Field(default_factory=list)

    open_access: OpenAccess | None = None
    cited_by_api_url: str | None = None
    counts_by_year: list[CountByYear] | None = None
    updated_date: str | None = None
    created_date: str | None = None

    abstract_inverted_index: dict[str, list[int]] | None = Field(None, exclude=True)
    abstract_inverted_index_v3: dict[str, list[int]] | None = Field(None, exclude=True)

    @property
    def abstract(self) -> str | None:
        from openalexpy.util import invert_abstract

        idx = self.abstract_inverted_index
        if idx is None:
            idx = self.abstract_inverted_index_v3
        if idx is None:
            return None
        return invert_abstract(idx)


class Author(OpenAlexBase):
    id: str | None = None
    orcid: str | None = None
    display_name: str | None = None
    display_name_alternatives: list[str] = Field(default_factory=list)
    works_count: int = 0
    cited_by_count: int = 0
    last_known_institutions: list[DehydratedInstitution] | None = None
    affiliations: list[Affiliation] | None = None
    counts_by_year: list[CountByYear] | None = None
    updated_date: str | None = None
    created_date: str | None = None
    relevance_score: float | None = None


class Source(OpenAlexBase):
    id: str | None = None
    issn: list[str] | None = None
    issn_l: str | None = None
    display_name: str | None = None
    type: str | None = None
    is_oa: bool = False
    hosted_organization: str | None = None
    works_count: int = 0
    cited_by_count: int = 0
    homepage_url: str | None = None
    apc_prices: list[dict[str, Any]] | None = None
    abbreviations: list[str] | None = None
    abbreviated_title: str | None = None
    alternate_titles: list[str] | None = None
    counts_by_year: list[CountByYear] | None = None
    updated_date: str | None = None
    created_date: str | None = None
    relevance_score: float | None = None


class Institution(OpenAlexBase):
    id: str | None = None
    ror: str | None = None
    display_name: str | None = None
    display_name_alternatives: list[str] = Field(default_factory=list)
    display_name_acronyms: list[str] = Field(default_factory=list)
    country_code: str | None = None
    type: str | None = None
    homepage_url: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None
    associated_institutions: list[DehydratedInstitution] | None = None
    works_count: int = 0
    cited_by_count: int = 0
    is_global_south: bool = False
    latitude: float | None = None
    longitude: float | None = None
    counts_by_year: list[CountByYear] | None = None
    updated_date: str | None = None
    created_date: str | None = None
    relevance_score: float | None = None


class Topic(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    description: str | None = None
    field: DehydratedField | None = None
    subfield: DehydratedSubfield | None = None
    domain: DehydratedDomain | None = None
    keywords: list[KeywordDehydrated] | None = None
    works_count: int = 0
    cited_by_count: int = 0
    counts_by_year: list[CountByYear] | None = None
    updated_date: str | None = None
    created_date: str | None = None
    relevance_score: float | None = None


class Domain(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    fields: list[DehydratedField] | None = None
    works_count: int = 0
    cited_by_count: int = 0
    updated_date: str | None = None
    created_date: str | None = None


class Field(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    domain: DehydratedDomain | None = None
    subfields: list[DehydratedSubfield] | None = None
    works_count: int = 0
    cited_by_count: int = 0
    updated_date: str | None = None
    created_date: str | None = None


class Subfield(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    field: DehydratedField | None = None
    domain: DehydratedDomain | None = None
    topics: list[TopicDehydrated] | None = None
    works_count: int = 0
    cited_by_count: int = 0
    updated_date: str | None = None
    created_date: str | None = None


class Publisher(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    alternate_titles: list[str] | None = None
    hierarchy_level: int | None = None
    parent_publisher: str | None = None
    homepage_url: str | None = None
    image_url: str | None = None
    works_count: int = 0
    cited_by_count: int = 0
    sources_count: int = 0
    counts_by_year: list[CountByYear] | None = None
    updated_date: str | None = None
    created_date: str | None = None
    relevance_score: float | None = None


class Funder(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    alternate_titles: list[str] | None = None
    country_code: str | None = None
    description: str | None = None
    homepage_url: str | None = None
    image_url: str | None = None
    ror: str | None = None
    type: str | None = None
    works_count: int = 0
    cited_by_count: int = 0
    grants_count: int = 0
    counts_by_year: list[CountByYear] | None = None
    updated_date: str | None = None
    created_date: str | None = None
    relevance_score: float | None = None


class Award(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    title: str | None = None
    funder: DehydratedInstitution | None = None
    funder_display_name: str | None = None
    award_amount: float | None = None
    currency: str | None = None
    source: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    updated_date: str | None = None
    created_date: str | None = None


class Keyword(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    works_count: int = 0
    cited_by_count: int = 0
    updated_date: str | None = None
    created_date: str | None = None
    relevance_score: float | None = None


class AutocompleteResult(OpenAlexBase):
    id: str | None = None
    display_name: str | None = None
    entity_type: str | None = None
    external_id: str | None = None
    hint: str | None = None


class GroupByResult(OpenAlexBase):
    key: str | None = None
    key_display_name: str | None = None
    count: int = 0
