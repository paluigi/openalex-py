# Authentication & Costs

## Getting an API Key

An API key is **required** for the OpenAlex API. It's free — just:

1. Create an account at [openalex.org](https://openalex.org/)
2. Copy your key from [openalex.org/settings/api](https://openalex.org/settings/api)

## Configuring the Key

```python
import openalexpy

openalexpy.config.api_key = "YOUR_API_KEY"
```

The library passes the key as a `api_key` query parameter, which is the [officially documented method](https://developers.openalex.org/api-reference/authentication).

## Pricing

Your free API key gives you **$1 of free usage every day**. With that, you can do a mix of:

| Action | Calls | Results | Cost |
|--------|-------|---------|------|
| Get a single entity | Unlimited | Unlimited | Free |
| List+filter | 10,000 | 1,000,000 | $0.10 per 1,000 |
| Search | 1,000 | 100,000 | $1 per 1,000 |
| Semantic search | 1,000 | 50,000 | $1 per 1,000 |
| Content download (PDF) | 100 | 100 PDFs | $10 per 1,000 |

## Monitoring Costs

### Per-request cost

Every response with `return_meta=True` includes the cost:

```python
response = await Works().filter(publication_year=2024).get(
    per_page=100, return_meta=True
)
print(f"This call cost: ${response.meta.cost_usd}")
print(f"Total matching results: {response.meta.count}")

# Estimate total cost for pagination
total_calls = response.meta.count // 100 + 1
estimated_cost = total_calls * response.meta.cost_usd
print(f"Full pagination would cost: ~${estimated_cost:.2f}")
```

### Rate limit status

Check your remaining daily budget programmatically:

```python
from openalexpy.client import AsyncOpenAlexClient

client = AsyncOpenAlexClient()
status = await client.get_rate_limit_status()
print(status)
```

### Rate limit headers

Every API response includes rate-limit headers that the library parses automatically:

| Header | Field on `RateLimitInfo` |
|--------|-------------------------|
| `X-RateLimit-Daily-Budget-Usd` | `daily_budget_usd` |
| `X-RateLimit-Daily-Remaining-Usd` | `daily_remaining_usd` |
| `X-RateLimit-Daily-Used-Usd` | `daily_used_usd` |
| `X-RateLimit-Reset` | `resets_in_seconds` |

## Error Handling for Cost Limits

The library distinguishes two types of 429 errors:

### Temporary rate limit

Too many requests per second. The library respects the `Retry-After` header and retries automatically.

```python
from openalexpy import RateLimitError

try:
    results = await Works().get()
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
```

### Credits exhausted

Daily budget spent. Retrying is pointless until midnight UTC. The library **does not retry** in this case.

```python
from openalexpy import CreditsExhaustedError

try:
    results = await Works().get()
except CreditsExhaustedError as e:
    print(f"Credits exhausted. Resets at: {e.reset_at}")
    print(f"Remaining: ${e.remaining_usd}")
```

## Configuration

```python
import openalexpy

openalexpy.config.api_key = "YOUR_KEY"
openalexpy.config.max_retries = 3          # Retry count for transient errors
openalexpy.config.retry_backoff_factor = 0.5  # Exponential backoff factor
openalexpy.config.timeout = 30.0           # HTTP timeout in seconds
```
