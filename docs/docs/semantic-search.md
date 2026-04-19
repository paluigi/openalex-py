# Semantic Search

Semantic search uses AI embeddings to find works by **meaning**, not just keywords. A query about "machine learning in healthcare" will find papers using "AI-driven diagnosis" or "computational medicine."

## Basic Usage

```python
import openalexpy

results = await openalexpy.Works().similar(
    "machine learning for drug discovery"
).get()

for work in results:
    print(f"{work.title} (score: {work.relevance_score})")
```

## Combined with Filters

Semantic search supports all standard filters server-side:

```python
results = await (
    openalexpy.Works()
    .similar("climate change impacts on biodiversity")
    .filter(publication_year=">2022", is_oa=True)
    .sort(cited_by_count="desc")
    .get(per_page=50)
)
```

## Count

```python
count = await openalexpy.Works().similar("quantum computing").count()
print(f"{count} semantically similar works")
```

## Important Limitations

| Limit | Value |
|-------|-------|
| Results per request | **50** (max) |
| Rate limit | **1 request per second** |
| Searchable works | Only those with abstracts (~217M) |
| Cost | $1 per 1,000 calls |

The library automatically enforces the 1 req/s rate limit for semantic search requests.

## Semantic vs Keyword Search

| Use keyword search when... | Use semantic search when... |
|---|---|
| You know the exact terms | You want conceptually related works |
| You need filters/sorting | You're exploring a new research area |
| You want specific fields | Your query is a sentence or paragraph |
| You need >50 results | Quality matters more than quantity |

## Best Practices

### 1. Use natural language queries

```python
# Good — descriptive query
results = await Works().similar(
    "methods for detecting gravitational waves using interferometry"
).get()

# Less effective — just keywords
results = await Works().similar("gravitational waves").get()
```

### 2. Combine with filters to narrow scope

```python
results = await (
    Works()
    .similar("CRISPR gene editing")
    .filter(type="article", publication_year=">2023")
    .select(["id", "title", "doi", "cited_by_count"])
    .get(per_page=50)
)
```

### 3. Use `return_meta=True` for cost tracking

```python
response = await Works().similar("quantum error correction").get(
    per_page=50, return_meta=True
)
print(f"Cost: ${response.meta.cost_usd}")
```

### 4. Respect the 50-result cap

Semantic search returns at most 50 results. If you need more, refine your query or use keyword search with pagination instead.
