"""Tests for audio system — AudioClip, AudioSource, AudioListener."""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.audio import AudioClip, AudioSource, AudioListener


@pytest.fixture(autouse=True)
def reset():
    yield
    AudioListener.reset()
    _clear_registry()


class TestAudioClip:
    def test_create_empty(self):
        clip = AudioClip()
        assert clip.path is None
        assert clip.length == 0.0

    def test_create_with_path(self):
        clip = AudioClip("sounds/hit.wav")
        assert clip.path == "sounds/hit.wav"


class TestAudioSource:
    def test_default_properties(self):
        go = GameObject("Sound")
        src = go.add_component(AudioSource)
        assert src.clip is None
        assert src.volume == 1.0
        assert src.pitch == 1.0
        assert src.loop is False
        assert src.is_playing is False

    def test_set_clip(self):
        go = GameObject("Sound")
        src = go.add_component(AudioSource)
        clip = AudioClip("test.wav")
        src.clip = clip
        assert src.clip is clip

    def test_volume_clamped(self):
        go = GameObject("Sound")
        src = go.add_component(AudioSource)
        src.volume = 1.5
        assert src.volume == 1.0
        src.volume = -0.5
        assert src.volume == 0.0

    def test_set_loop(self):
        go = GameObject("Sound")
        src = go.add_component(AudioSource)
        src.loop = True
        assert src.loop is True

    def test_play_without_clip_no_error(self):
        go = GameObject("Sound")
        src = go.add_component(AudioSource)
        src.play()  # Should not raise

    def test_stop(self):
        go = GameObject("Sound")
        src = go.add_component(AudioSource)
        src.stop()
        assert src.is_playing is False

    def test_play_sets_playing_flag(self):
        go = GameObject("Sound")
        src = go.add_component(AudioSource)
        clip = AudioClip("nonexistent.wav")
        src.clip = clip
        src.play()
        # Without pygame mixer, _channel will be None but _playing flag is set
        assert src._playing is True

    def test_on_destroy_stops(self):
        go = GameObject("Sound")
        src = go.add_component(AudioSource)
        src._playing = True
        src.on_destroy()
        assert src._playing is False


class TestAudioListener:
    def test_singleton(self):
        go = GameObject("Camera")
        listener = go.add_component(AudioListener)
        assert AudioListener._main is listener

    def test_only_first_becomes_main(self):
        go1 = GameObject("Cam1")
        l1 = go1.add_component(AudioListener)
        go2 = GameObject("Cam2")
        l2 = go2.add_component(AudioListener)
        assert AudioListener._main is l1

    def test_destroy_clears_main(self):
        go = GameObject("Camera")
        listener = go.add_component(AudioListener)
        assert AudioListener._main is listener
        listener.on_destroy()
        assert AudioListener._main is None
