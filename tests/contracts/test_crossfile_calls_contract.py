"""Contract tests for cross-file function call qualification.

In Unity/C#, calling a static method from another class requires qualification:
    Powerup.SpawnPowerup()   -- not just SpawnPowerup()
    Enemies.CreateEnemy()    -- not just CreateEnemy()

The translator's project_translator must qualify cross-file calls so the
output compiles.  Intra-file calls and Unity built-ins must NOT be qualified.
"""

from __future__ import annotations

import textwrap
import tempfile
from pathlib import Path


from src.translator.project_translator import translate_project


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_project(files: dict[str, str]) -> str:
    """Write Python files to a temp directory and return the path."""
    tmp = tempfile.mkdtemp(prefix="crossfile_")
    for name, content in files.items():
        (Path(tmp) / name).write_text(textwrap.dedent(content))
    return tmp


def _translate(files: dict[str, str], **kwargs) -> dict[str, str]:
    """Translate a multi-file project from dict of {filename: source}."""
    project_dir = _write_project(files)
    return translate_project(project_dir, **kwargs)


# ---------------------------------------------------------------------------
# Contract: cross-file function calls must be qualified
# ---------------------------------------------------------------------------

class TestCrossFileFunctionCallQualification:
    """When file_b calls a function defined in file_a, the C# output
    must qualify the call with the target class/file name."""

    def test_module_level_function_qualified_across_files(self):
        """enemies.py defines create_enemy(), game_manager.py calls it.
        C# output for GameManager must emit Enemies.CreateEnemy() not CreateEnemy()."""
        files = {
            "enemies.py": """\
                from src.engine.core import MonoBehaviour, GameObject

                def create_enemy(name: str) -> None:
                    go = GameObject(name)

                class Enemy(MonoBehaviour):
                    def start(self) -> None:
                        pass
            """,
            "game_manager.py": """\
                from src.engine.core import MonoBehaviour
                from enemies import create_enemy

                class GameManager(MonoBehaviour):
                    def start(self) -> None:
                        create_enemy("Goblin")
            """,
        }
        results = _translate(files)
        gm_cs = results.get("GameManager.cs", "")
        assert gm_cs, "GameManager.cs not found in output"
        # Must be qualified: Enemies.CreateEnemy("Goblin")
        assert "Enemies.CreateEnemy" in gm_cs, (
            f"Cross-file call create_enemy() should be qualified as Enemies.CreateEnemy() "
            f"but got:\n{gm_cs}"
        )
        # Must NOT have bare unqualified call
        lines = [l.strip() for l in gm_cs.splitlines()]
        bare_calls = [l for l in lines if l.startswith("CreateEnemy(") or "= CreateEnemy(" in l]
        # Filter out lines that ARE qualified (contain Enemies.CreateEnemy)
        unqualified = [l for l in bare_calls if "Enemies.CreateEnemy" not in l]
        assert not unqualified, (
            f"Found unqualified cross-file call(s): {unqualified}"
        )

    def test_class_static_method_qualified_across_files(self):
        """powerup.py defines Powerup with static spawn(), player.py calls it.
        Must emit Powerup.Spawn() not just Spawn()."""
        files = {
            "powerup.py": """\
                from src.engine.core import MonoBehaviour, GameObject

                class Powerup(MonoBehaviour):
                    @staticmethod
                    def spawn(position_x: float) -> None:
                        go = GameObject("Powerup")
            """,
            "player.py": """\
                from src.engine.core import MonoBehaviour
                from powerup import Powerup

                class Player(MonoBehaviour):
                    def update(self) -> None:
                        Powerup.spawn(5.0)
            """,
        }
        results = _translate(files)
        player_cs = results.get("Player.cs", "")
        assert player_cs, "Player.cs not found in output"
        assert "Powerup.Spawn" in player_cs, (
            f"Static cross-file call should be qualified as Powerup.Spawn() "
            f"but got:\n{player_cs}"
        )

    def test_helper_function_from_utils_file(self):
        """utils.py defines helper(), combat.py calls helper().
        Must emit Utils.Helper() in C# output."""
        files = {
            "utils.py": """\
                def helper() -> int:
                    return 42
            """,
            "combat.py": """\
                from src.engine.core import MonoBehaviour
                from utils import helper

                class Combat(MonoBehaviour):
                    def start(self) -> None:
                        val = helper()
            """,
        }
        results = _translate(files)
        combat_cs = results.get("Combat.cs", "")
        assert combat_cs, "Combat.cs not found in output"
        # The call must be qualified with the source file's class name
        assert "Utils.Helper()" in combat_cs or "Utils.Helper()" in combat_cs, (
            f"Cross-file function call helper() should be qualified as Utils.Helper() "
            f"but got:\n{combat_cs}"
        )


class TestIntraFileCallsNotQualified:
    """Calls to methods within the SAME file must NOT be qualified."""

    def test_own_method_not_qualified(self):
        """A class calling its own method should NOT add class prefix."""
        files = {
            "player.py": """\
                from src.engine.core import MonoBehaviour

                class Player(MonoBehaviour):
                    def start(self) -> None:
                        self._reset_health()

                    def _reset_health(self) -> None:
                        pass
            """,
        }
        results = _translate(files)
        player_cs = results.get("Player.cs", "")
        assert player_cs, "Player.cs not found in output"
        # self._reset_health() should translate to ResetHealth() not Player.ResetHealth()
        # Check there's no unnecessary Player. qualification on own instance method
        lines = [l.strip() for l in player_cs.splitlines()]
        overqualified = [l for l in lines if "Player.ResetHealth()" in l]
        assert not overqualified, (
            f"Intra-file method call was over-qualified: {overqualified}"
        )

    def test_module_function_same_file_not_qualified(self):
        """A module-level function called from a class in the same file
        should not be qualified with the file name."""
        files = {
            "game.py": """\
                from src.engine.core import MonoBehaviour

                def compute_score(hits: int) -> int:
                    return hits * 10

                class Game(MonoBehaviour):
                    def start(self) -> None:
                        score = compute_score(5)
            """,
        }
        results = _translate(files)
        game_cs = results.get("Game.cs", "")
        assert game_cs, "Game.cs not found in output"
        # Same-file function — should NOT be qualified as Game.ComputeScore
        lines = [l.strip() for l in game_cs.splitlines()]
        overqualified = [l for l in lines if "Game.ComputeScore" in l]
        assert not overqualified, (
            f"Same-file function was over-qualified: {overqualified}"
        )


class TestUnityBuiltinsNotQualified:
    """Unity/System built-in calls must NEVER be qualified with a user class name."""

    def test_destroy_not_qualified(self):
        """Destroy() is a Unity method — must not be prefixed."""
        files = {
            "bullet.py": """\
                from src.engine.core import MonoBehaviour, Object

                class Bullet(MonoBehaviour):
                    def update(self) -> None:
                        Object.destroy(self.game_object)
            """,
        }
        results = _translate(files)
        bullet_cs = results.get("Bullet.cs", "")
        assert bullet_cs, "Bullet.cs not found in output"
        assert "Destroy(" in bullet_cs, (
            f"Destroy should appear in output:\n{bullet_cs}"
        )
        # Should NOT be qualified with a user class
        lines = [l.strip() for l in bullet_cs.splitlines()]
        bad = [l for l in lines if "Bullet.Destroy(" in l]
        assert not bad, f"Unity Destroy was wrongly qualified: {bad}"

    def test_instantiate_not_qualified(self):
        """Instantiate() is a Unity method — must not be prefixed."""
        files = {
            "spawner.py": """\
                from src.engine.core import MonoBehaviour, Object, GameObject

                class Spawner(MonoBehaviour):
                    def start(self) -> None:
                        obj = Object.instantiate(GameObject("Prefab"))
            """,
        }
        results = _translate(files)
        spawner_cs = results.get("Spawner.cs", "")
        assert spawner_cs, "Spawner.cs not found in output"
        # Instantiate should not have user-class prefix
        lines = [l.strip() for l in spawner_cs.splitlines()]
        bad = [l for l in lines if "Spawner.Instantiate(" in l]
        assert not bad, f"Unity Instantiate was wrongly qualified: {bad}"


class TestMultiFileProjectQualification:
    """End-to-end test with a 3-file project mimicking a real game."""

    def test_three_file_game_project(self):
        """Three files: powerup.py, enemies.py, game_manager.py.
        game_manager calls functions from both other files."""
        files = {
            "powerup.py": """\
                from src.engine.core import MonoBehaviour, GameObject

                def spawn_powerup(x: float, y: float) -> None:
                    go = GameObject("Powerup")

                class Powerup(MonoBehaviour):
                    def start(self) -> None:
                        pass
            """,
            "enemies.py": """\
                from src.engine.core import MonoBehaviour, GameObject

                def create_enemy(enemy_type: str) -> None:
                    go = GameObject(enemy_type)

                class Enemy(MonoBehaviour):
                    def start(self) -> None:
                        pass
            """,
            "game_manager.py": """\
                from src.engine.core import MonoBehaviour
                from powerup import spawn_powerup
                from enemies import create_enemy

                class GameManager(MonoBehaviour):
                    def start(self) -> None:
                        spawn_powerup(1.0, 2.0)
                        create_enemy("Goblin")
            """,
        }
        results = _translate(files)
        gm_cs = results.get("GameManager.cs", "")
        assert gm_cs, "GameManager.cs not found in output"

        # Both cross-file calls must be qualified
        assert "Powerup.SpawnPowerup(" in gm_cs or "SpawnPowerup(" in gm_cs, (
            f"SpawnPowerup call not found in output:\n{gm_cs}"
        )
        # The key assertion: they MUST be qualified
        assert "Powerup.SpawnPowerup(" in gm_cs, (
            f"Cross-file spawn_powerup() must be qualified as Powerup.SpawnPowerup() "
            f"but got:\n{gm_cs}"
        )
        assert "Enemies.CreateEnemy(" in gm_cs or "Enemy.CreateEnemy(" in gm_cs, (
            f"Cross-file create_enemy() must be qualified as Enemies.CreateEnemy() "
            f"or Enemy.CreateEnemy() but got:\n{gm_cs}"
        )
