from __future__ import annotations

import os

import pytest


def requires_api_key(reason: str = "OPENALEX_API_KEY not set"):
    return pytest.mark.skipif(
        not os.environ.get("OPENALEX_API_KEY"),
        reason=reason,
    )
