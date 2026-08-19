"""Pytest bootstrap.

Loads the sample environment so non-auth tests can import dblingo without
real credentials, and skips tests marked with `auth` when no real Duolingo
JWT is available.
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

SAMPLE_ENV = Path(__file__).parent.parent / ".env.sample"
JWT_PLACEHOLDER = "your_jwt_value_here"

if not os.environ.get("DUOLINGO_JWT"):
    load_dotenv(SAMPLE_ENV, verbose=False)


def has_real_jwt():
    jwt = os.environ.get("DUOLINGO_JWT", "")
    return bool(jwt) and jwt != JWT_PLACEHOLDER


def pytest_collection_modifyitems(config, items):
    if has_real_jwt():
        return
    skip_auth = pytest.mark.skip(reason="DUOLINGO_JWT not set; skipping auth tests")
    for item in items:
        if "auth" in item.keywords:
            item.add_marker(skip_auth)
