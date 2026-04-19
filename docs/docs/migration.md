# Migration from PyAlex

This guide helps you migrate from [PyAlex](https://github.com/J535D165/pyalex) to `openalexpy`.

## Configuration

### PyAlex

```python
import pyalex
pyalex.config.api_key = "YOUR_KEY"
```

### openalexpy

```python
import openalexpy
openalexpy.config.api_key = "YOUR_KEY"
```

## Entity Classes

### PyAlex

```python
from pyalex import Works, Authors, Sources, Institutions, Topics, Publishers, Funders
```

### openalexpy

```python
# Async
from openalexpy import Works, Authors, Sources, Institutions, Topics, Publishers, Funders

# Sync
from openalexpy import WorksSync, AuthorsSync, SourcesSync, InstitutionsSync
```

## Query Building

The fluent API is nearly identical, but **each method now returns a new instance**:

```python
# Both work the same way
results = await Works().filter(publication_year=2024, is_oa=True).get()
```

### Key differences

| Feature | pyalex | openalexpy |
|---------|--------|------------|
| Async | No | Yes (await all `.get()`, `.count()`, etc.) |
| Builder mutation | Mutates in place | Returns new instance |
| Return type | `dict` subclass | Pydantic model |
| Abstract access | `work["abstract"]` | `work.abstract` |
| per_page max | 200 | 100 (API limit) |

## Entity Access

### PyAlex

```python
w = Works()["W2741809807"]           # dict subclass
title = w["title"]                    # dict access
abstract = w["abstract"]              # computed property via __getitem__
```

### openalexpy

```python
w = await Works().get_by_id("W2741809807")  # Pydantic model
title = w.title                                # attribute access
abstract = w.abstract                          # computed property
```

## Pagination

### PyAlex

```python
pager = Works().paginate(per_page=200)
for page in pager:
    print(len(page))
```

### openalexpy

```python
pager = Works().paginate(per_page=100)  # max 100
async for page in pager:
    print(len(page))
```

## Content Download

### PyAlex

```python
w = Works()["W4412002745"]
w.pdf.download("paper.pdf")
w.tei.download("paper.xml")
```

### openalexpy

```python
w = await Works().get_by_id("W4412002745")
await w._pdf.download("paper.pdf")
await w._tei.download("paper.xml")
```

## Error Handling

### PyAlex

```python
from pyalex.api import QueryError
```

### openalexpy

```python
from openalexpy import QueryError, RateLimitError, CreditsExhaustedError
```

New exception types for cost-aware error handling:
- `RateLimitError` — temporary rate limit with `retry_after` attribute
- `CreditsExhaustedError` — daily credits spent with `reset_at` attribute
- `NotFoundError` — entity not found
- `ContentUnavailableError` — PDF/TEI download failure

## Dropped Features

| Feature | Reason |
|---------|--------|
| `Concepts` entity | Deprecated by OpenAlex, replaced by Topics |
| N-grams endpoint | Removed by OpenAlex |
| `per_page` > 100 | OpenAlex API limit is 100 |
