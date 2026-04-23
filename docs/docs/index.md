# openalexpy

A modern, async-first Python library for the [OpenAlex API](https://developers.openalex.org/).

## Acknowledgements

This library was inspired by **[PyAlex](https://github.com/J535D165/pyalex)** by Jonathan de Bruin.
PyAlex pioneered the Python interface to OpenAlex and proved the value of a fluent,
pipe-able query builder for scholarly data. `openalexpy` builds on those foundations with:

- **Native async/await** support via `httpx`
- **Full type safety** with Pydantic v2 models for all entities
- **Cost-aware API usage** — parses rate-limit headers, distinguishes credit exhaustion from temporary rate limits
- **Correct API key handling** — uses the documented `api_key` query parameter
- **Immutable query builder** — each chained method returns a new instance, no shared mutable state bugs
- **Two-step content download** — properly handles PDF/TEI redirects preserving rate-limit headers

## Features

| Feature | pyalex | openalexpy |
|---------|--------|------------|
| Async | No | Yes (httpx) |
| Typing | Dict subclasses | Full Pydantic v2 models |
| API key | Header (undocumented) | Query param (official) |
| Builder pattern | Mutable (bug-prone) | Immutable |
| Rate limit headers | Discarded | Parsed and exposed |
| 429 handling | Blind retry | Credit exhaustion vs temp rate limit |
| Content download | Broken redirects | Two-step redirect flow |
| Cost tracking | None | `cost_usd` on meta, `RateLimitInfo` on response |

## Installation

```bash
pip install openalex-py
```

or with `uv`:

```bash
uv add openalex-py
```

Requires Python 3.10+.
