"""Shared fixtures for unity-py-sim tests."""

import pytest


@pytest.fixture(autouse=True)
def reset_engine_state():
    """Reset all global engine state between tests."""
    yield
    from src.engine.core import _clear_registry
    from src.engine.lifecycle import LifecycleManager
    from src.engine.physics.physics_manager import PhysicsManager
    from src.engine.rendering.display import DisplayManager
    from src.engine.time_manager import Time
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    DisplayManager.reset()
    Time._reset()
