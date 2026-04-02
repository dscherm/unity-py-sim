"""Unity-compatible audio system: AudioClip, AudioSource, AudioListener."""

from __future__ import annotations

from src.engine.core import Component


class AudioClip:
    """Wraps an audio file. In Unity this is a ScriptableObject asset."""

    def __init__(self, path: str | None = None) -> None:
        self._path = path
        self._sound = None  # pygame.mixer.Sound, loaded lazily
        self._length: float = 0.0

    @property
    def path(self) -> str | None:
        return self._path

    @property
    def length(self) -> float:
        if self._sound is not None:
            return self._sound.get_length()
        return self._length

    def _ensure_loaded(self) -> None:
        """Load the sound via pygame.mixer if not already loaded."""
        if self._sound is None and self._path is not None:
            try:
                import pygame.mixer
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                self._sound = pygame.mixer.Sound(self._path)
            except Exception:
                pass  # Audio unavailable (headless, no hardware, etc.)


class AudioSource(Component):
    """Unity-compatible AudioSource component."""

    def __init__(self) -> None:
        super().__init__()
        self._clip: AudioClip | None = None
        self._volume: float = 1.0
        self._pitch: float = 1.0
        self._loop: bool = False
        self._playing: bool = False
        self._channel = None  # pygame.mixer.Channel

    @property
    def clip(self) -> AudioClip | None:
        return self._clip

    @clip.setter
    def clip(self, value: AudioClip | None) -> None:
        self._clip = value

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = max(0.0, min(1.0, value))
        if self._channel is not None:
            self._channel.set_volume(self._volume)

    @property
    def pitch(self) -> float:
        return self._pitch

    @pitch.setter
    def pitch(self, value: float) -> None:
        self._pitch = value

    @property
    def loop(self) -> bool:
        return self._loop

    @loop.setter
    def loop(self, value: bool) -> None:
        self._loop = value

    @property
    def is_playing(self) -> bool:
        if self._channel is not None:
            return self._channel.get_busy()
        return self._playing

    def play(self) -> None:
        """Play the assigned clip."""
        if self._clip is None:
            return
        self._playing = True
        self._clip._ensure_loaded()
        if self._clip._sound is not None:
            loops = -1 if self._loop else 0
            self._channel = self._clip._sound.play(loops=loops)
            if self._channel is not None:
                self._channel.set_volume(self._volume)

    def stop(self) -> None:
        """Stop playback."""
        self._playing = False
        if self._channel is not None:
            self._channel.stop()
            self._channel = None

    def pause(self) -> None:
        """Pause playback."""
        self._playing = False
        if self._channel is not None:
            self._channel.pause()

    def unpause(self) -> None:
        """Resume paused playback."""
        self._playing = True
        if self._channel is not None:
            self._channel.unpause()

    def play_one_shot(self, clip: AudioClip, volume: float = 1.0) -> None:
        """Play a clip once without affecting the main clip assignment."""
        clip._ensure_loaded()
        if clip._sound is not None:
            channel = clip._sound.play()
            if channel is not None:
                channel.set_volume(volume)

    def on_destroy(self) -> None:
        """Stop audio when component is destroyed."""
        self.stop()


class AudioListener(Component):
    """Marks a GameObject as the audio listener (typically on the main camera).
    Unity has exactly one active AudioListener at a time."""

    _main: AudioListener | None = None

    def __init__(self) -> None:
        super().__init__()
        if AudioListener._main is None:
            AudioListener._main = self

    @classmethod
    def reset(cls) -> None:
        cls._main = None

    def on_destroy(self) -> None:
        if AudioListener._main is self:
            AudioListener._main = None
