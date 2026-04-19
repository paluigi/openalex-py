# Querying

## Immutable Builder

Every method on a query object returns a **new instance**. The original is never mutated:

```python
base = Works()
q1 = base.filter(publication_year=2024)
q2 = q1.filter(is_oa=True)

# base is unchanged — no shared mutable state bugs
assert "filter" not in base.params
```

## Get by ID

```python
# By OpenAlex ID
work = await Works().get_by_id("W2741809807")

# By DOI
work = await Works().get_by_id("https://doi.org/10.7717/peerj.4375")

# By ORCID
author = await Authors().get_by_id("https://orcid.org/0000-0002-4297-0502")

# By ROR
institution = await Institutions().get_by_id("https://ror.org/04pp8hn57")
```

## Random Entity

```python
work = await Works().random()
author = await Authors().random()
institution = await Institutions().random()
```

## Filtering

### Basic filters

```python
results = await Works().filter(
    publication_year=2024,
    is_oa=True,
    type="article"
).get()
```

### Nested filters

Use dicts for dot-notation filters:

```python
# authorships.institutions.ror = "04pp8hn57"
results = await Works().filter(
    authorships={"institutions": {"ror": "04pp8hn57"}}
).get()
```

### AND operator (list values)

```python
# institutions.country_code = "fr" AND "gb"
results = await Works().filter(
    institutions={"country_code": ["fr", "gb"]}
).get()
```

### OR operator

```python
# doi = "10.1234/a" OR "10.1234/b"
results = await Works().filter_or(
    doi=["10.1016/s0924-9338(99)80239-9", "10.1002/andp.19213690304"]
).get()
```

### NOT operator

```python
# country_code != "us"
results = await Institutions().filter_not(country_code="us").get()
```

### Comparison operators

```python
# cited_by_count > 100
results = await Works().filter_gt(cited_by_count=100).get()

# publication_year < 2020
results = await Works().filter_lt(publication_year=2020).get()
```

### Range syntax

```python
# publication_year 2020-2024
results = await Works().filter(publication_year="2020-2024").get()
```

### Chaining filters

```python
results = await (
    Works()
    .filter(publication_year=2024)
    .filter(is_oa=True)
    .filter(type="article")
    .get()
)
```

## Search

```python
# Full-text search
results = await Works().search("fierce creatures").get()

# Search with filters
results = await Works().search("dna").filter(publication_year=2024).get()
```

## Search Filters (deprecated by OpenAlex)

Prefer the `search` parameter. The `.search` filter suffix is deprecated but still available:

```python
results = await Authors().search_filter(display_name="einstein").get()
```

## Sort

```python
results = await Works().sort(cited_by_count="desc").get()
```

## Group By

```python
groups = await Works().filter(
    publication_year=2024
).group_by("topics.id").get()

for g in groups:
    print(f"{g.key_display_name}: {g.count}")
```

## Select Fields

Reduce response size by selecting only needed fields:

```python
results = await Works().select(["id", "doi", "title"]).get()
```

## Sample

Get random samples:

```python
results = await Works().sample(100, seed=42).get()
```

## Count

```python
count = await Works().filter(publication_year=2024).count()
print(f"{count} works published in 2024")
```

## Autocomplete

```python
# Global autocomplete
results = await openalexpy.autocomplete("stockholm resilience")

# Entity-specific autocomplete
results = await Works().filter(publication_year=2024).autocomplete("planetary")
```
