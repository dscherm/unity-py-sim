"""Shared fixtures for unity-py-sim tests."""

import pytest


@pytest.fixture(autouse=True)
def reset_engine_state():
    """Reset all global engine state between tests."""
    yield
    from src.engine.core import _clear_registry
    _clear_registry()
