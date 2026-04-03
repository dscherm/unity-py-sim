"""Build corpus index and pair files for all Python/C# translation pairs."""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
PAIRS_DIR = ROOT / "data" / "corpus" / "pairs"
PAIRS_DIR.mkdir(parents=True, exist_ok=True)

# All pairs: (id, name, game, python_path, csharp_path)
ALL_PAIRS = [
    ("001", "paddle_controller", "pong",
     "examples/pong/pong_python/paddle_controller.py",
     "examples/pong/pong_unity/PaddleController.cs"),
    ("002", "ball_controller", "pong",
     "examples/pong/pong_python/ball_controller.py",
     "examples/pong/pong_unity/BallController.cs"),
    ("003", "score_manager", "pong",
     "examples/pong/pong_python/score_manager.py",
     "examples/pong/pong_unity/ScoreManager.cs"),
    ("004", "game_manager", "pong",
     "examples/pong/pong_python/game_manager.py",
     "examples/pong/pong_unity/GameManager.cs"),
    ("005", "paddle_controller", "breakout",
     "examples/breakout/breakout_python/paddle_controller.py",
     "examples/breakout/breakout_unity/PaddleController.cs"),
    ("006", "ball_controller", "breakout",
     "examples/breakout/breakout_python/ball_controller.py",
     "examples/breakout/breakout_unity/BallController.cs"),
    ("007", "brick", "breakout",
     "examples/breakout/breakout_python/brick.py",
     "examples/breakout/breakout_unity/Brick.cs"),
    ("008", "game_manager", "breakout",
     "examples/breakout/breakout_python/game_manager.py",
     "examples/breakout/breakout_unity/GameManager.cs"),
    ("009", "powerup", "breakout",
     "examples/breakout/breakout_python/powerup.py",
     "examples/breakout/breakout_unity/Powerup.cs"),
    ("010", "constants", "angry_birds",
     "examples/angry_birds/angry_birds_python/constants.py",
     "examples/angry_birds/angry_birds_unity/Constants.cs"),
    ("011", "enums", "angry_birds",
     "examples/angry_birds/angry_birds_python/enums.py",
     "examples/angry_birds/angry_birds_unity/Enums.cs"),
    ("012", "bird", "angry_birds",
     "examples/angry_birds/angry_birds_python/bird.py",
     "examples/angry_birds/angry_birds_unity/Bird.cs"),
    ("013", "slingshot", "angry_birds",
     "examples/angry_birds/angry_birds_python/slingshot.py",
     "examples/angry_birds/angry_birds_unity/SlingShot.cs"),
    ("014", "brick", "angry_birds",
     "examples/angry_birds/angry_birds_python/brick.py",
     "examples/angry_birds/angry_birds_unity/Brick.cs"),
    ("015", "pig", "angry_birds",
     "examples/angry_birds/angry_birds_python/pig.py",
     "examples/angry_birds/angry_birds_unity/Pig.cs"),
    ("016", "destroyer", "angry_birds",
     "examples/angry_birds/angry_birds_python/destroyer.py",
     "examples/angry_birds/angry_birds_unity/Destroyer.cs"),
    ("017", "game_manager", "angry_birds",
     "examples/angry_birds/angry_birds_python/game_manager.py",
     "examples/angry_birds/angry_birds_unity/GameManager.cs"),
    ("018", "fsm", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/fsm.py",
     "examples/fsm_platformer/fsm_platformer_unity/FSM.cs"),
    ("019", "command", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/command.py",
     "examples/fsm_platformer/fsm_platformer_unity/Command.cs"),
    ("020", "player_idle_state", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/player_idle_state.py",
     "examples/fsm_platformer/fsm_platformer_unity/PlayerIdleState.cs"),
    ("021", "player_running_state", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/player_running_state.py",
     "examples/fsm_platformer/fsm_platformer_unity/PlayerRunningState.cs"),
    ("022", "player_jumping_state", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/player_jumping_state.py",
     "examples/fsm_platformer/fsm_platformer_unity/PlayerJumpingState.cs"),
    ("023", "player_falling_state", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/player_falling_state.py",
     "examples/fsm_platformer/fsm_platformer_unity/PlayerFallingState.cs"),
    ("024", "player_landing_state", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/player_landing_state.py",
     "examples/fsm_platformer/fsm_platformer_unity/PlayerLandingState.cs"),
    ("025", "input_transition", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/input_transition.py",
     "examples/fsm_platformer/fsm_platformer_unity/InputTransition.cs"),
    ("026", "no_input_transition", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/no_input_transition.py",
     "examples/fsm_platformer/fsm_platformer_unity/NoInputTransition.cs"),
    ("027", "jump_transition", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/jump_transition.py",
     "examples/fsm_platformer/fsm_platformer_unity/JumpTransition.cs"),
    ("028", "fall_transition", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/fall_transition.py",
     "examples/fsm_platformer/fsm_platformer_unity/FallTransition.cs"),
    ("029", "grounded_transition", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/grounded_transition.py",
     "examples/fsm_platformer/fsm_platformer_unity/GroundedTransition.cs"),
    ("030", "landing_timer_transition", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/landing_timer_transition.py",
     "examples/fsm_platformer/fsm_platformer_unity/LandingTimerTransition.cs"),
    ("031", "jump_command", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/jump_command.py",
     "examples/fsm_platformer/fsm_platformer_unity/JumpCommand.cs"),
    ("032", "walk_command", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/walk_command.py",
     "examples/fsm_platformer/fsm_platformer_unity/WalkCommand.cs"),
    ("033", "player_input_handler", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/player_input_handler.py",
     "examples/fsm_platformer/fsm_platformer_unity/PlayerInputHandler.cs"),
    ("034", "enemy_idle_state", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/enemy_idle_state.py",
     "examples/fsm_platformer/fsm_platformer_unity/IdleState.cs"),
    ("035", "enemy_walk_state", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/enemy_walk_state.py",
     "examples/fsm_platformer/fsm_platformer_unity/WalkState.cs"),
    ("036", "time_transition", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/time_transition.py",
     "examples/fsm_platformer/fsm_platformer_unity/TimeTransition.cs"),
    ("037", "enemy_behaviour", "fsm_platformer",
     "examples/fsm_platformer/fsm_platformer_python/enemy_behaviour.py",
     "examples/fsm_platformer/fsm_platformer_unity/EnemyBehaviour.cs"),
]


def build():
    # Write pair files
    for pid, name, game, py_path, cs_path in ALL_PAIRS:
        pair_id = f"{pid}_{name}"
        pair_file = PAIRS_DIR / f"{pair_id}.json"
        pair_data = {
            "id": pair_id,
            "unity_file": cs_path,
            "python_file": py_path,
            "game": game,
        }
        pair_file.write_text(json.dumps(pair_data, indent=2) + "\n")

    # Build corpus index
    index = []
    for pid, name, game, py_path, cs_path in ALL_PAIRS:
        pair_id = f"{pid}_{name}"
        index.append({
            "id": pair_id,
            "game": game,
            "file": f"pairs/{pair_id}.json",
        })

    (ROOT / "data" / "corpus" / "corpus_index.json").write_text(
        json.dumps(index, indent=2) + "\n"
    )
    print(f"Wrote {len(index)} entries to corpus_index.json")
    print(f"Wrote {len(ALL_PAIRS)} pair files")


if __name__ == "__main__":
    build()
