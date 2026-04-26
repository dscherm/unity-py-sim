"""Integration tests for S2-3: translate_project() singleton SerializeField injection.

These tests invoke translate_project() on an in-memory multi-file Pacman-style
Python project and verify that the final C# output satisfies Unity's singleton
wiring requirements — no raw `GameManager.Instance.` calls in consumer classes.

Unity requirement (from task S2-3):
- Consumer MonoBehaviours must use [SerializeField] private GameManager gameManager;
- Access sites must become gameManager.score (not GameManager.Instance.score)
- GameManager's own file can still contain the singleton initialization
"""

from __future__ import annotations

import tempfile
from pathlib import Path


from src.translator.project_translator import translate_project


# ---------------------------------------------------------------------------
# Helpers — build a temp directory with Python source files
# ---------------------------------------------------------------------------

def _write_project(files: dict[str, str]) -> Path:
    """Write {filename: source} to a temp dir and return the dir path."""
    tmp = Path(tempfile.mkdtemp())
    for name, src in files.items():
        (tmp / name).write_text(src, encoding="utf-8")
    return tmp


# ---------------------------------------------------------------------------
# Minimal Pacman-style project fixtures
# ---------------------------------------------------------------------------

_GAME_MANAGER_PY = '''\
class GameManager:
    instance = None

    def awake(self):
        GameManager.instance = self
        self.score = 0
        self.level = 1
        self.lives = 3

    def add_score(self, points):
        self.score += points
'''

_PLAYER_PY = '''\
class Player:
    def awake(self):
        self.speed = 5.0
        self.health = 100

    def update(self):
        GameManager.instance.add_score(10)
        score = GameManager.instance.score
'''

_HUD_PY = '''\
class HUD:
    def update(self):
        s = GameManager.instance.score
        l = GameManager.instance.level
        lives = GameManager.instance.lives
'''


# ===========================================================================
# 1. Consumer files: SerializeField present, no Instance leak
# ===========================================================================

class TestConsumerClassesGetSerializeField:
    """Consumer classes (Player, HUD) must end up with injected [SerializeField]
    private GameManager references, and must not contain raw .Instance. calls."""

    def setup_method(self):
        self.project_dir = _write_project({
            "game_manager.py": _GAME_MANAGER_PY,
            "player.py": _PLAYER_PY,
            "hud.py": _HUD_PY,
        })
        self.results = translate_project(str(self.project_dir))

    def _cs_for(self, class_name: str) -> str:
        key = f"{class_name}.cs"
        assert key in self.results, f"{key} not in results: {list(self.results)}"
        return self.results[key]

    def test_player_has_serializefield_injection(self):
        cs = self._cs_for("Player")
        assert "[SerializeField] private GameManager gameManager;" in cs, (
            f"Expected SerializeField injection in Player.cs; got:\n{cs}"
        )

    def test_player_has_no_instance_leak(self):
        cs = self._cs_for("Player")
        assert "GameManager.Instance." not in cs, (
            f"Player.cs still contains raw GameManager.Instance.; got:\n{cs}"
        )

    def test_hud_has_serializefield_injection(self):
        cs = self._cs_for("HUD")
        assert "[SerializeField] private GameManager gameManager;" in cs, (
            f"Expected SerializeField injection in HUD.cs; got:\n{cs}"
        )

    def test_hud_has_no_instance_leak(self):
        cs = self._cs_for("HUD")
        assert "GameManager.Instance." not in cs, (
            f"HUD.cs still contains raw GameManager.Instance.; got:\n{cs}"
        )

    def test_player_uses_field_access(self):
        cs = self._cs_for("Player")
        # After rewrite, score and add_score should be accessed via the field
        assert "gameManager." in cs, (
            f"Player.cs should use gameManager. field access; got:\n{cs}"
        )

    def test_hud_uses_field_access(self):
        cs = self._cs_for("HUD")
        assert "gameManager." in cs, (
            f"HUD.cs should use gameManager. field access; got:\n{cs}"
        )


# ===========================================================================
# 2. GameManager's own file is not corrupted
# ===========================================================================

class TestGameManagerOwnFilePreserved:
    """The GameManager.cs file must still contain the singleton initialization.
    The rewriter must not corrupt its own class body."""

    def setup_method(self):
        self.project_dir = _write_project({
            "game_manager.py": _GAME_MANAGER_PY,
            "player.py": _PLAYER_PY,
        })
        self.results = translate_project(str(self.project_dir))

    def test_gamemanager_cs_exists(self):
        assert "GameManager.cs" in self.results

    def test_gamemanager_not_get_spurious_serializefield(self):
        cs = self.results["GameManager.cs"]
        # GameManager should NOT inject [SerializeField] private GameManager gameManager;
        # into itself — that would be a self-reference cycle
        assert "[SerializeField] private GameManager gameManager;" not in cs, (
            f"GameManager.cs should not inject self-SerializeField; got:\n{cs}"
        )


# ===========================================================================
# 3. Self-assignment still present in GameManager
# ===========================================================================

class TestSingletonInitializationSurvives:
    """The GameManager.Instance = this; initialization must survive translation."""

    def setup_method(self):
        self.project_dir = _write_project({
            "game_manager.py": _GAME_MANAGER_PY,
            "player.py": _PLAYER_PY,
        })
        self.results = translate_project(str(self.project_dir))

    def test_gamemanager_contains_instance_assignment(self):
        cs = self.results["GameManager.cs"]
        # The singleton self-assignment must still be present (e.g. GameManager.Instance = this;)
        # The exact form depends on translation but must include Instance and assignment
        assert "Instance" in cs, (
            f"GameManager.cs lost the Instance field entirely; got:\n{cs}"
        )


# ===========================================================================
# 4. Multiple consumers, single singleton — each consumer gets injection
# ===========================================================================

class TestMultipleConsumers:
    """When more than one file consumes the singleton, each must receive its
    own [SerializeField] injection."""

    _ENEMY_PY = '''\
class Enemy:
    def update(self):
        if GameManager.instance.lives <= 0:
            pass
'''

    def setup_method(self):
        self.project_dir = _write_project({
            "game_manager.py": _GAME_MANAGER_PY,
            "player.py": _PLAYER_PY,
            "hud.py": _HUD_PY,
            "enemy.py": self._ENEMY_PY,
        })
        self.results = translate_project(str(self.project_dir))

    def test_all_three_consumers_have_injection(self):
        for cls in ("Player", "HUD", "Enemy"):
            cs = self.results.get(f"{cls}.cs", "")
            assert "[SerializeField] private GameManager gameManager;" in cs, (
                f"{cls}.cs missing SerializeField injection; got:\n{cs}"
            )

    def test_all_three_consumers_have_no_instance_leak(self):
        for cls in ("Player", "HUD", "Enemy"):
            cs = self.results.get(f"{cls}.cs", "")
            assert "GameManager.Instance." not in cs, (
                f"{cls}.cs still leaks GameManager.Instance.; got:\n{cs}"
            )


# ===========================================================================
# 5. File with no singleton reference is untouched
# ===========================================================================

class TestFileWithoutSingletonReference:
    """A file that never references GameManager.Instance must not receive any
    SerializeField injection for GameManager."""

    _UTILS_PY = '''\
class Utils:
    def clamp(self, v, lo, hi):
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v
'''

    def setup_method(self):
        self.project_dir = _write_project({
            "game_manager.py": _GAME_MANAGER_PY,
            "utils.py": self._UTILS_PY,
        })
        self.results = translate_project(str(self.project_dir))

    def test_utils_has_no_serializefield_for_gamemanager(self):
        cs = self.results.get("Utils.cs", "")
        assert "[SerializeField] private GameManager gameManager;" not in cs, (
            f"Utils.cs should not get GameManager injection; got:\n{cs}"
        )


# ===========================================================================
# 6. Multiple singletons in the same project
# ===========================================================================

class TestMultipleSingletonsInProject:
    """When two classes are singletons, both must be detected and both must
    be injected into consumer files that reference them."""

    _AUDIO_MANAGER_PY = '''\
class AudioManager:
    instance = None

    def awake(self):
        AudioManager.instance = self
        self.volume = 1.0

    def play(self, clip):
        pass
'''

    _UI_PY = '''\
class UI:
    def update(self):
        s = GameManager.instance.score
        v = AudioManager.instance.volume
'''

    def setup_method(self):
        self.project_dir = _write_project({
            "game_manager.py": _GAME_MANAGER_PY,
            "audio_manager.py": self._AUDIO_MANAGER_PY,
            "ui.py": self._UI_PY,
        })
        self.results = translate_project(str(self.project_dir))

    def test_ui_gets_both_serializefield_injections(self):
        cs = self.results.get("UI.cs", "")
        assert "[SerializeField] private GameManager gameManager;" in cs, (
            f"UI.cs missing GameManager injection; got:\n{cs}"
        )
        assert "[SerializeField] private AudioManager audioManager;" in cs, (
            f"UI.cs missing AudioManager injection; got:\n{cs}"
        )

    def test_ui_has_no_instance_leaks(self):
        cs = self.results.get("UI.cs", "")
        assert "GameManager.Instance." not in cs
        assert "AudioManager.Instance." not in cs
