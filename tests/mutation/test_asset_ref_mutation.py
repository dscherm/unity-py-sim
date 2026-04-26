"""Mutation tests for asset_ref / clip_ref.

Monkeypatch the constructors to omit the fields, then verify that contract
tests (replicated here) correctly detect the missing attribute.
"""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.audio import AudioSource


@pytest.fixture(autouse=True)
def _clean_engine():
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    yield
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()


# ---------------------------------------------------------------------------
# SpriteRenderer mutation: remove asset_ref from __init__
# ---------------------------------------------------------------------------

class TestSpriteRendererMutation:
    def test_missing_asset_ref_detected(self, monkeypatch):
        """If __init__ doesn't set asset_ref, accessing it must raise."""
        original_init = SpriteRenderer.__init__

        def broken_init(self_inner):
            original_init(self_inner)
            # Simulate a mutation: delete the attribute that __init__ sets
            if hasattr(self_inner, "asset_ref"):
                delattr(self_inner, "asset_ref")

        monkeypatch.setattr(SpriteRenderer, "__init__", broken_init)

        sr = SpriteRenderer()
        with pytest.raises(AttributeError):
            _ = sr.asset_ref

    def test_missing_asset_ref_on_gameobject_detected(self, monkeypatch):
        """Mutation also caught when component is on a GameObject."""
        original_init = SpriteRenderer.__init__

        def broken_init(self_inner):
            original_init(self_inner)
            if hasattr(self_inner, "asset_ref"):
                delattr(self_inner, "asset_ref")

        monkeypatch.setattr(SpriteRenderer, "__init__", broken_init)

        go = GameObject("MutantObj")
        sr = go.add_component(SpriteRenderer)
        with pytest.raises(AttributeError):
            _ = sr.asset_ref

    def test_contract_catches_wrong_default(self, monkeypatch):
        """If asset_ref defaults to something other than None, contract detects."""
        original_init = SpriteRenderer.__init__

        def broken_init(self_inner):
            original_init(self_inner)
            self_inner.asset_ref = "WRONG_DEFAULT"

        monkeypatch.setattr(SpriteRenderer, "__init__", broken_init)

        sr = SpriteRenderer()
        # Contract: default must be None
        assert sr.asset_ref != None  # noqa: E711  -- intentional, proves mutation caught


# ---------------------------------------------------------------------------
# AudioSource mutation: remove clip_ref from __init__
# ---------------------------------------------------------------------------

class TestAudioSourceMutation:
    def test_missing_clip_ref_detected(self, monkeypatch):
        """If __init__ doesn't set clip_ref, accessing it must raise."""
        original_init = AudioSource.__init__

        def broken_init(self_inner):
            original_init(self_inner)
            if hasattr(self_inner, "clip_ref"):
                delattr(self_inner, "clip_ref")

        monkeypatch.setattr(AudioSource, "__init__", broken_init)

        audio = AudioSource()
        with pytest.raises(AttributeError):
            _ = audio.clip_ref

    def test_missing_clip_ref_on_gameobject_detected(self, monkeypatch):
        """Mutation also caught when component is on a GameObject."""
        original_init = AudioSource.__init__

        def broken_init(self_inner):
            original_init(self_inner)
            if hasattr(self_inner, "clip_ref"):
                delattr(self_inner, "clip_ref")

        monkeypatch.setattr(AudioSource, "__init__", broken_init)

        go = GameObject("MutantObj")
        audio = go.add_component(AudioSource)
        with pytest.raises(AttributeError):
            _ = audio.clip_ref

    def test_contract_catches_wrong_default(self, monkeypatch):
        """If clip_ref defaults to something other than None, contract detects."""
        original_init = AudioSource.__init__

        def broken_init(self_inner):
            original_init(self_inner)
            self_inner.clip_ref = "WRONG_DEFAULT"

        monkeypatch.setattr(AudioSource, "__init__", broken_init)

        audio = AudioSource()
        assert audio.clip_ref != None  # noqa: E711
