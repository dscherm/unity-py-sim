"""Enemy Walk State — moves horizontally, flips at bounds."""

from __future__ import annotations

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2, Vector3

from fsm_platformer_python.fsm import FSMState


class EnemyWalkState(FSMState):
    """Enemy walks in the direction it faces."""

    def __init__(self, walk_speed: float = 1.5) -> None:
        super().__init__()
        self.walk_speed: float = walk_speed

    def act(self, owner: MonoBehaviour) -> None:
        from fsm_platformer_python.enemy_behaviour import EnemyBehaviour
        enemy: EnemyBehaviour = owner  # type: ignore

        # Direction based on facing (local_scale.x sign)
        scale = enemy.transform.local_scale
        direction = -1.0 if scale.x > 0 else 1.0

        rb = enemy.rb
        rb.velocity = Vector2(direction * self.walk_speed, rb.velocity.y)

        # Flip at patrol bounds
        x = enemy.transform.position.x
        if x < enemy.patrol_min_x:
            enemy.transform.local_scale = Vector3(-abs(scale.x), scale.y, scale.z)
        elif x > enemy.patrol_max_x:
            enemy.transform.local_scale = Vector3(abs(scale.x), scale.y, scale.z)
