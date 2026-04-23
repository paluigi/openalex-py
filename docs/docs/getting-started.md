# Getting Started

## Install

```bash
pip install openalex-py
```

## Configure API Key

Starting February 2026, an API key is **required** for the OpenAlex API. Get a free key at [openalex.org/settings/api](https://openalex.org/settings/api).

```python
import openalexpy

openalexpy.config.api_key = "YOUR_API_KEY"
```

Or set the `OPENALEX_API_KEY` environment variable.

## First Query

### Async (recommended)

```python
import asyncio
import openalexpy

async def main():
    # Get a single work by ID
    work = await openalexpy.Works().get_by_id("W2741809807")
    print(work.title)
    print(work.cited_by_count)

    # Search for works
    results = await openalexpy.Works().search("fierce creatures").get()
    for w in results:
        print(f"{w.title} ({w.publication_year})")

asyncio.run(main())
```

### Sync

```python
import openalexpy

openalexpy.config.api_key = "YOUR_API_KEY"

work = openalexpy.WorksSync().get_by_id("W2741809807")
print(work.title)
```

## Supported Entities

All OpenAlex entities are supported with both async and sync variants:

| Entity | Async | Sync |
|--------|-------|------|
| Works | `Works()` | `WorksSync()` |
| Authors | `Authors()` | `AuthorsSync()` |
| Sources | `Sources()` | `SourcesSync()` |
| Institutions | `Institutions()` | `InstitutionsSync()` |
| Topics | `Topics()` | `TopicsSync()` |
| Publishers | `Publishers()` | `PublishersSync()` |
| Funders | `Funders()` | `FundersSync()` |
| Awards | `Awards()` | `AwardsSync()` |
| Keywords | `Keywords()` | `KeywordsSync()` |
| Domains | `Domains()` | `DomainsSync()` |
| Fields | `Fields()` | `FieldsSync()` |
| Subfields | `Subfields()` | `SubfieldsSync()` |

## Typed Models

All results are Pydantic v2 models with full type hints:

```python
from openalexpy import Work

work: Work = await Works().get_by_id("W2741809807")

# IDE autocomplete works for all fields
work.title          # str | None
work.doi            # str | None
work.publication_year  # int | None
work.cited_by_count    # int
work.authorships    # list[Authorship] | None
work.abstract       # str | None (computed from inverted index)
```
