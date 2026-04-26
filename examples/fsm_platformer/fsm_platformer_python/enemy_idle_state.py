"""Enemy Idle State — no movement, waits for TimeTransition."""

from __future__ import annotations

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2

from fsm_platformer_python.fsm import FSMState


class EnemyIdleState(FSMState):
    """Enemy stands still."""

    def act(self, owner: MonoBehaviour) -> None:
        from fsm_platformer_python.enemy_behaviour import EnemyBehaviour
        enemy: EnemyBehaviour = owner  # type: ignore

        rb = enemy.rb
        rb.velocity = Vector2(0, rb.velocity.y)
