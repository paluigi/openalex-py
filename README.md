# openalexpy

A modern, async-first Python library for the [OpenAlex API](https://developers.openalex.org/).

## Acknowledgements

This library was inspired by **[PyAlex](https://github.com/J535D165/pyalex)** by Jonathan de Bruin.
PyAlex pioneered the Python interface to OpenAlex and proved the value of a fluent,
pipe-able query builder for scholarly data. `openalexpy` builds on those foundations
with native async support, full type safety via Pydantic, and cost-aware API usage.

## Features

- **Async-first** with sync wrappers — `httpx`-based, `asyncio`-native
- **Fully typed** — Pydantic v2 models for all entities with IDE autocomplete
- **Cost-aware** — Parses `X-RateLimit-*` headers, distinguishes credit exhaustion from temporary rate limits, exposes `cost_usd` on every response
- **Correct API key handling** — Uses `api_key` query parameter as documented by OpenAlex (not undocumented headers)
- **Immutable query builder** — Each method returns a new instance, no shared mutable state bugs
- **Two-step content download** — Properly handles PDF/TEI redirects preserving rate-limit headers
- **Semantic search** — First-class support for `search.semantic` with automatic 1 req/s rate limiting

## Installation

```bash
uv add openalexpy
```

or

```bash
pip install openalexpy
```

Requires Python 3.10+.

## Quick Start

### Configure your API key

```python
import openalexpy

openalexpy.config.api_key = "YOUR_API_KEY"
```

Or set the `OPENALEX_API_KEY` environment variable.

### Async usage (recommended)

```python
import asyncio
import openalexpy

async def main():
    # Get a single work
    work = await openalexpy.Works().get_by_id("W2741809807")
    print(work.title)
    print(work.abstract)

    # Filter works
    results = await openalexpy.Works().filter(
        publication_year=2024, is_oa=True
    ).sort(cited_by_count="desc").get(per_page=10)

    for w in results:
        print(f"{w.title} ({w.cited_by_count} citations)")

    # Semantic search
    similar = await openalexpy.Works().similar(
        "machine learning for drug discovery"
    ).filter(publication_year=">2022").get(per_page=50)

    # Paginate through all results
    pager = openalexpy.Works().filter(
        author={"id": "A5023888391"}
    ).paginate(per_page=100)

    async for page in pager:
        for work in page:
            print(work.id)

asyncio.run(main())
```

### Sync usage

```python
import openalexpy

openalexpy.config.api_key = "YOUR_API_KEY"

# Get a single work
work = openalexpy.WorksSync().get_by_id("W2741809807")

# Filter and get
results = openalexpy.WorksSync().filter(
    publication_year=2024
).sort(cited_by_count="desc").get(per_page=10)

# Paginate
pager = openalexpy.WorksSync().filter(
    author={"id": "A5023888391"}
).paginate(per_page=100)

for page in pager:
    for work in page:
        print(work.id)
```

## Supported Entities

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

## Query Building

All query methods return a **new instance** — the original query is never mutated.

```python
base = openalexpy.Works()

# Chain filters
q = base.filter(publication_year=2024).filter(is_oa=True)

# base is unchanged
assert "filter" not in base.params
```

### Filter operators

```python
# AND (default)
Works().filter(institutions={"country_code": ["fr", "gb"]})

# OR
Works().filter_or(doi=["10.1234/a", "10.1234/b"])

# NOT
Institutions().filter_not(country_code="us")

# Greater than / Less than
Works().filter_gt(cited_by_count=100)
Works().filter_lt(publication_year=2020)
```

### Semantic search

```python
# Basic semantic search (capped at 50 results per request)
results = await Works().similar("climate change impacts").get()

# Combined with filters
results = await (
    Works()
    .similar("quantum computing applications")
    .filter(publication_year=">2022", is_oa=True)
    .get(per_page=50)
)
```

### Pagination

```python
# Cursor pagination (default, for deep pagination)
pager = Works().filter(publication_year=2024).paginate(per_page=100, n_max=5000)

async for page in pager:
    print(len(page))

# Page-based pagination (limited to 10,000 results)
pager = Works().search("dna").paginate(method="page", per_page=100)
```

### Content download (PDF/TEI)

```python
work = await Works().get_by_id("W4412002745")

# Get PDF bytes
pdf_bytes = await work._pdf.get()

# Download to file
await work._pdf.download("paper.pdf")

# TEI XML
tei_bytes = await work._tei.get()
```

## Cost Monitoring

Every API response includes cost information:

```python
response = await Works().filter(publication_year=2024).get(
    per_page=100, return_meta=True
)
print(f"Cost: ${response.meta.cost_usd}")
print(f"Total results: {response.meta.count}")

# Check rate limit status
client = openalexpy.client.AsyncOpenAlexClient()
status = await client.get_rate_limit_status()
print(status)
```

## Error Handling

```python
from openalexpy import QueryError, RateLimitError, CreditsExhaustedError

try:
    results = await Works().filter(bad_filter=True).get()
except QueryError as e:
    print(f"Bad query: {e}")
except CreditsExhaustedError as e:
    print(f"Daily credits exhausted. Resets at: {e.reset_at}")
except RateLimitError as e:
    print(f"Temporarily rate limited. Retry after: {e.retry_after}s")
```

## License

[MIT](LICENSE)
