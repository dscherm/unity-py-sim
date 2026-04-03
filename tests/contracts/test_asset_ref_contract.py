"""Contract tests for asset_ref (SpriteRenderer) and clip_ref (AudioSource).

These fields are symbolic metadata for Unity export and must not alter
runtime rendering or audio behaviour.
"""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.audio import AudioSource, AudioClip
from src.engine.math.vector import Vector2


@pytest.fixture(autouse=True)
def _clean_engine():
    """Reset all global engine state between tests."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    yield
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()


# ---------------------------------------------------------------------------
# SpriteRenderer.asset_ref defaults
# ---------------------------------------------------------------------------

class TestSpriteRendererAssetRefDefault:
    def test_default_is_none(self):
        sr = SpriteRenderer()
        assert sr.asset_ref is None

    def test_default_type(self):
        sr = SpriteRenderer()
        assert sr.asset_ref is None or isinstance(sr.asset_ref, str)


# ---------------------------------------------------------------------------
# AudioSource.clip_ref defaults
# ---------------------------------------------------------------------------

class TestAudioSourceClipRefDefault:
    def test_default_is_none(self):
        audio = AudioSource()
        assert audio.clip_ref is None

    def test_default_type(self):
        audio = AudioSource()
        assert audio.clip_ref is None or isinstance(audio.clip_ref, str)


# ---------------------------------------------------------------------------
# Read-write round-trip
# ---------------------------------------------------------------------------

class TestAssetRefReadWrite:
    def test_sprite_renderer_set_and_read(self):
        sr = SpriteRenderer()
        sr.asset_ref = "bird_red"
        assert sr.asset_ref == "bird_red"

    def test_sprite_renderer_overwrite(self):
        sr = SpriteRenderer()
        sr.asset_ref = "bird_red"
        sr.asset_ref = "bird_blue"
        assert sr.asset_ref == "bird_blue"

    def test_sprite_renderer_set_back_to_none(self):
        sr = SpriteRenderer()
        sr.asset_ref = "bird_red"
        sr.asset_ref = None
        assert sr.asset_ref is None

    def test_audio_source_set_and_read(self):
        audio = AudioSource()
        audio.clip_ref = "bird_launch_sfx"
        assert audio.clip_ref == "bird_launch_sfx"

    def test_audio_source_overwrite(self):
        audio = AudioSource()
        audio.clip_ref = "sfx_a"
        audio.clip_ref = "sfx_b"
        assert audio.clip_ref == "sfx_b"

    def test_audio_source_set_back_to_none(self):
        audio = AudioSource()
        audio.clip_ref = "sfx_a"
        audio.clip_ref = None
        assert audio.clip_ref is None


# ---------------------------------------------------------------------------
# asset_ref must NOT affect rendering properties
# ---------------------------------------------------------------------------

class TestAssetRefDoesNotAffectRendering:
    def test_color_unchanged(self):
        sr = SpriteRenderer()
        original_color = sr.color
        sr.asset_ref = "some_sprite"
        assert sr.color == original_color

    def test_size_unchanged(self):
        sr = SpriteRenderer()
        original_size = (sr.size.x, sr.size.y)
        sr.asset_ref = "some_sprite"
        assert (sr.size.x, sr.size.y) == original_size

    def test_sorting_order_unchanged(self):
        sr = SpriteRenderer()
        original_order = sr.sorting_order
        sr.asset_ref = "some_sprite"
        assert sr.sorting_order == original_order

    def test_sprite_unchanged(self):
        sr = SpriteRenderer()
        original_sprite = sr.sprite
        sr.asset_ref = "some_sprite"
        assert sr.sprite is original_sprite


# ---------------------------------------------------------------------------
# clip_ref must NOT affect audio properties or playback
# ---------------------------------------------------------------------------

class TestClipRefDoesNotAffectAudio:
    def test_clip_unchanged(self):
        audio = AudioSource()
        original_clip = audio.clip
        audio.clip_ref = "bird_launch_sfx"
        assert audio.clip is original_clip

    def test_volume_unchanged(self):
        audio = AudioSource()
        original_vol = audio.volume
        audio.clip_ref = "bird_launch_sfx"
        assert audio.volume == original_vol

    def test_pitch_unchanged(self):
        audio = AudioSource()
        original_pitch = audio.pitch
        audio.clip_ref = "bird_launch_sfx"
        assert audio.pitch == original_pitch

    def test_loop_unchanged(self):
        audio = AudioSource()
        original_loop = audio.loop
        audio.clip_ref = "bird_launch_sfx"
        assert audio.loop == original_loop

    def test_is_playing_unchanged(self):
        audio = AudioSource()
        audio.clip_ref = "bird_launch_sfx"
        assert audio.is_playing is False


# ---------------------------------------------------------------------------
# asset_ref / clip_ref survive component lifecycle on GameObjects
# ---------------------------------------------------------------------------

class TestAssetRefSurvivesLifecycle:
    def test_sprite_renderer_on_gameobject(self):
        go = GameObject("TestObj")
        sr = go.add_component(SpriteRenderer)
        sr.asset_ref = "bird_red"
        retrieved = go.get_component(SpriteRenderer)
        assert retrieved is not None
        assert retrieved.asset_ref == "bird_red"

    def test_audio_source_on_gameobject(self):
        go = GameObject("TestObj")
        audio = go.add_component(AudioSource)
        audio.clip_ref = "bird_launch_sfx"
        retrieved = go.get_component(AudioSource)
        assert retrieved is not None
        assert retrieved.clip_ref == "bird_launch_sfx"

    def test_multiple_components_independent(self):
        """Two SpriteRenderers on different objects have independent asset_ref."""
        go1 = GameObject("Obj1")
        sr1 = go1.add_component(SpriteRenderer)
        sr1.asset_ref = "bird_red"

        go2 = GameObject("Obj2")
        sr2 = go2.add_component(SpriteRenderer)
        sr2.asset_ref = "pig_normal"

        assert sr1.asset_ref == "bird_red"
        assert sr2.asset_ref == "pig_normal"

    def test_find_gameobject_preserves_asset_ref(self):
        go = GameObject("MyBird", tag="Bird")
        sr = go.add_component(SpriteRenderer)
        sr.asset_ref = "bird_red"

        found = GameObject.find("MyBird")
        assert found is not None
        assert found.get_component(SpriteRenderer).asset_ref == "bird_red"
