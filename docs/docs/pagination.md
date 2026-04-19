# Pagination

OpenAlex supports two pagination methods. Both are supported by `openalexpy`.

## Cursor Pagination (default)

Use cursor pagination for deep pagination beyond 10,000 results. This is the recommended method.

```python
pager = openalexpy.Works().filter(
    publication_year=2024
).paginate(per_page=100, n_max=5000)

async for page in pager:
    for work in page:
        print(work.id)
```

### Iterate all results

```python
from itertools import chain

query = openalexpy.Works().filter(publication_year=2024)
pager = query.paginate(per_page=100, n_max=None)

async for page in pager:
    for work in page:
        print(work.id)
```

## Page-based Pagination

Limited to 10,000 results, but sometimes useful:

```python
pager = openalexpy.Works().search("dna").paginate(
    method="page", per_page=100
)

async for page in pager:
    print(len(page))
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `method` | `"cursor"` | `"cursor"` or `"page"` |
| `per_page` | `25` | Results per page (max 100) |
| `n_max` | `10000` | Maximum results to fetch. `None` for unlimited. |

## Sync Pagination

```python
pager = openalexpy.WorksSync().filter(publication_year=2024).paginate(per_page=100)

for page in pager:
    for work in page:
        print(work.id)
```

## Sample + Pagination

Sample is not compatible with cursor pagination:

```python
# This raises ValueError
Works().sample(100).paginate(method="cursor")

# Use page pagination instead
pager = Works().sample(100).paginate(method="page", per_page=50)
```
