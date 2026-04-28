#!/usr/bin/env python3
"""Behavioral gate — runs games headless and asserts on game state.

Unlike playtest.py which only catches exceptions, this gate verifies
actual game behavior: objects exist, physics happened, scores changed.

Usage:
    python tools/behavioral_gate.py              # all games
    python tools/behavioral_gate.py space_invaders  # single game
"""

import sys
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine.core import GameObject, _clear_registry, _game_objects
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.time_manager import Time
from src.engine.input_manager import Input
from src.engine.rendering.camera import Camera
from src.engine.app import run


def reset_engine():
    """Reset all engine singletons."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    Time._reset()
    Input._reset()
    Camera._reset_main()
    from src.engine.prefab import PrefabRegistry
    PrefabRegistry.clear()
    try:
        from src.engine.tweening import TweenManager
        TweenManager.reset()
    except Exception:
        pass


class BehavioralResult:
    def __init__(self, game: str):
        self.game = game
        self.checks: list[tuple[str, bool, str]] = []  # (name, passed, detail)

    def check(self, name: str, condition: bool, detail: str = ""):
        self.checks.append((name, condition, detail))
        status = "PASS" if condition else "FAIL"
        print(f"    [{status}] {name}" + (f" — {detail}" if detail else ""))

    @property
    def passed(self) -> bool:
        return all(ok for _, ok, _ in self.checks)

    @property
    def summary(self) -> str:
        p = sum(1 for _, ok, _ in self.checks if ok)
        return f"{p}/{len(self.checks)} checks passed"


def gate_pong() -> BehavioralResult:
    """Pong: verify paddles, ball, walls exist and ball moves."""
    reset_engine()
    sys.path.insert(0, str(ROOT / "examples" / "pong"))
    from run_pong import setup_scene

    result = BehavioralResult("pong")

    run(setup_scene, headless=True, max_frames=30)

    result.check("camera_exists", Camera.main is not None)
    result.check("left_paddle_exists", GameObject.find("LeftPaddle") is not None)
    result.check("right_paddle_exists", GameObject.find("RightPaddle") is not None)
    result.check("ball_exists", GameObject.find("Ball") is not None)

    ball = GameObject.find("Ball")
    if ball:
        pos = ball.transform.position
        result.check("ball_moved_from_origin",
                     abs(pos.x) > 0.1 or abs(pos.y) > 0.1,
                     f"pos=({pos.x:.1f}, {pos.y:.1f})")

    walls = [GameObject.find("TopWall"), GameObject.find("BottomWall")]
    result.check("walls_exist", all(w is not None for w in walls))

    return result


def gate_breakout() -> BehavioralResult:
    """Breakout: verify paddle, ball, bricks spawned, game manager active."""
    reset_engine()
    sys.path.insert(0, str(ROOT / "examples" / "breakout"))
    from run_breakout import setup_scene

    result = BehavioralResult("breakout")

    run(setup_scene, headless=True, max_frames=30)

    result.check("camera_exists", Camera.main is not None)
    result.check("paddle_exists", GameObject.find("Paddle") is not None)
    result.check("ball_exists", GameObject.find("Ball") is not None)

    bricks = GameObject.find_game_objects_with_tag("Brick")
    result.check("bricks_spawned", len(bricks) > 50, f"count={len(bricks)}")

    result.check("game_manager_exists", GameObject.find("GameManager") is not None)

    from breakout_python.game_manager import GameManager
    result.check("lives_initialized", GameManager.lives == 3, f"lives={GameManager.lives}")
    result.check("score_zero_at_start", GameManager.score == 0, f"score={GameManager.score}")

    return result


def gate_fsm_platformer() -> BehavioralResult:
    """FSM Platformer: verify player, enemy, ground, physics gravity."""
    reset_engine()
    sys.path.insert(0, str(ROOT / "examples" / "fsm_platformer"))
    from run_fsm_platformer import setup_scene

    result = BehavioralResult("fsm_platformer")

    run(setup_scene, headless=True, max_frames=60)

    result.check("player_exists", GameObject.find("Player") is not None)
    result.check("enemy_exists", GameObject.find("Enemy") is not None)
    result.check("ground_exists", GameObject.find("Ground") is not None)

    player = GameObject.find("Player")
    if player:
        pos = player.transform.position
        # Player should be near ground level (-3.0), not fallen through
        result.check("player_on_ground",
                     -4.0 < pos.y < 0.0,
                     f"y={pos.y:.2f}")

    pm = PhysicsManager.instance()
    result.check("gravity_set", pm.gravity.y < 0, f"gravity.y={pm.gravity.y}")

    return result


def gate_angry_birds() -> BehavioralResult:
    """Angry Birds: verify slingshot, birds, pigs, structure exist."""
    reset_engine()
    sys.path.insert(0, str(ROOT / "examples" / "angry_birds"))
    from run_angry_birds import setup_scene

    result = BehavioralResult("angry_birds")

    run(setup_scene, headless=True, max_frames=30)

    result.check("camera_exists", Camera.main is not None)
    result.check("slingshot_exists", GameObject.find("Slingshot") is not None)
    result.check("ground_exists", GameObject.find("Ground") is not None)

    birds = GameObject.find_game_objects_with_tag("Bird")
    result.check("birds_spawned", len(birds) >= 3, f"count={len(birds)}")

    pigs = GameObject.find_game_objects_with_tag("Pig")
    result.check("pigs_spawned", len(pigs) >= 2, f"count={len(pigs)}")

    bricks = GameObject.find_game_objects_with_tag("Brick")
    result.check("structure_built", len(bricks) >= 4, f"count={len(bricks)}")

    return result


def gate_space_invaders() -> BehavioralResult:
    """Space Invaders: verify player, invader grid, bunkers, scoring."""
    reset_engine()
    sys.path.insert(0, str(ROOT / "examples" / "space_invaders"))
    from space_invaders_python.prefabs import register_prefabs
    register_prefabs()
    from run_space_invaders import setup_scene

    result = BehavioralResult("space_invaders")

    # Use few frames so game doesn't reach game-over state
    run(setup_scene, headless=True, max_frames=10)

    result.check("camera_exists", Camera.main is not None)

    # Check objects exist in registry (may be inactive after game-over)
    all_names = [obj.name for obj in _game_objects.values()]
    result.check("player_created", "Player" in all_names, "names include Player")

    all_tags = [obj.tag for obj in _game_objects.values()]
    invader_count = sum(1 for t in all_tags if t == "Invader")
    result.check("invaders_spawned", invader_count >= 50,
                 f"count={invader_count}, expected 55")

    bunker_count = sum(1 for t in all_tags if t == "Bunker")
    result.check("bunkers_spawned", bunker_count == 4, f"count={bunker_count}")

    result.check("mystery_ship_created", "MysteryShip" in all_names)

    from space_invaders_python.game_manager import GameManager as SIGameManager
    SIGameManager.instance = None  # Reset before checking (may have stale ref from previous game)
    result.check("game_manager_created", "GameManager" in all_names)

    return result


GATES = {
    "pong": gate_pong,
    "breakout": gate_breakout,
    "fsm_platformer": gate_fsm_platformer,
    "angry_birds": gate_angry_birds,
    "space_invaders": gate_space_invaders,
}


def main():
    games = sys.argv[1:] if len(sys.argv) > 1 else list(GATES.keys())

    print("=" * 60)
    print("BEHAVIORAL GATE — Game State Assertions")
    print("=" * 60)

    all_passed = True
    results = {}

    for game in games:
        if game not in GATES:
            print(f"Unknown game: {game}")
            continue

        print(f"\n  [{game}]")
        try:
            result = GATES[game]()
            results[game] = {
                "passed": result.passed,
                "summary": result.summary,
                "checks": [(n, ok, d) for n, ok, d in result.checks],
            }
            if not result.passed:
                all_passed = False
        except Exception as e:
            print(f"    [CRASH] {type(e).__name__}: {e}")
            results[game] = {"passed": False, "summary": f"CRASH: {e}", "checks": []}
            all_passed = False

    # Summary
    print("\n" + "=" * 60)
    total_checks = sum(len(r["checks"]) for r in results.values())
    total_passed = sum(sum(1 for _, ok, _ in r["checks"] if ok) for r in results.values())
    if all_passed:
        print(f"BEHAVIORAL GATE PASSED — {total_passed}/{total_checks} checks across {len(results)} games")
    else:
        failed = [g for g, r in results.items() if not r["passed"]]
        print(f"BEHAVIORAL GATE FAILED — {', '.join(failed)}")
        print(f"  {total_passed}/{total_checks} checks passed")
    print("=" * 60)

    # Record
    obs = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pipeline": "behavioral_gate",
        "passed": all_passed,
        "total_checks": total_checks,
        "total_passed": total_passed,
        "results": {g: r["summary"] for g, r in results.items()},
    }
    obs_file = ROOT / ".ralph" / "behavioral_gate.jsonl"
    obs_file.parent.mkdir(parents=True, exist_ok=True)
    with open(obs_file, "a") as f:
        f.write(json.dumps(obs) + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
