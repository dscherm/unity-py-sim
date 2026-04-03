"""Invaders — manages the 5x11 grid, movement, speed scaling, and missile attacks.

Maps to: zigurous/Invaders.cs
"""

import random

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.coroutine import WaitForSeconds
from src.engine.lifecycle import LifecycleManager


# Row colors (bottom to top) and score values
ROW_CONFIG = [
    {"colors": [(50, 255, 50), (30, 200, 30)], "score": 10},    # row 0 - green
    {"colors": [(50, 255, 50), (30, 200, 30)], "score": 10},    # row 1 - green
    {"colors": [(50, 200, 255), (30, 150, 200)], "score": 20},  # row 2 - cyan
    {"colors": [(50, 200, 255), (30, 150, 200)], "score": 20},  # row 3 - cyan
    {"colors": [(255, 100, 100), (200, 60, 60)], "score": 30},  # row 4 - red (top)
]


class Invaders(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.rows: int = 5
        self.columns: int = 11
        self.base_speed: float = 1.0
        self.missile_spawn_rate: float = 1.0
        self.screen_bound_x: float = 6.5
        self._direction: Vector2 = Vector2(1, 0)  # right
        self._initial_position: Vector2 = Vector2(0, 0)
        self._invader_objects: list[GameObject] = []
        self._missile_timer: float = 0.0

    def start(self):
        self._initial_position = Vector2(
            self.transform.position.x,
            self.transform.position.y,
        )
        self._create_grid()

    def _create_grid(self):
        lm = LifecycleManager.instance()

        for row in range(self.rows):
            width = 2.0 * (self.columns - 1)
            height = 2.0 * (self.rows - 1)
            center_offset_x = -width * 0.5
            center_offset_y = -height * 0.5

            config = ROW_CONFIG[row % len(ROW_CONFIG)]

            for col in range(self.columns):
                x = center_offset_x + 2.0 * col
                y = center_offset_y + 2.0 * row

                name = f"Invader_{row}_{col}"
                invader_go = GameObject(name, tag="Invader")
                invader_go.layer = 10  # LAYER_INVADER
                invader_go.transform.position = Vector2(
                    self.transform.position.x + x,
                    self.transform.position.y + y,
                )

                rb = invader_go.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.KINEMATIC

                col_comp = invader_go.add_component(BoxCollider2D)
                col_comp.size = Vector2(1.5, 1.5)
                col_comp.is_trigger = True
                col_comp.build()

                sr = invader_go.add_component(SpriteRenderer)
                sr.color = config["colors"][0]
                sr.size = Vector2(1.5, 1.0)
                sr.sorting_order = 2

                from space_invaders_python.invader import Invader
                inv = invader_go.add_component(Invader)
                inv.score = config["score"]
                inv.animation_colors = config["colors"]
                lm.register_component(inv)

                self._invader_objects.append(invader_go)

    def update(self):
        # Speed scaling: faster as more invaders die
        total = self.rows * self.columns
        alive = self.get_alive_count()
        if total == 0:
            return
        percent_killed = (total - alive) / total
        speed = self.base_speed + percent_killed * 4.0  # 1x to 5x

        # Move grid
        dx = speed * Time.delta_time * self._direction.x
        pos = self.transform.position
        self.transform.position = Vector2(pos.x + dx, pos.y)

        # Update child positions (since we don't have real parent-child transform propagation for physics)
        for inv_go in self._invader_objects:
            if inv_go.active:
                inv_pos = inv_go.transform.position
                inv_go.transform.position = Vector2(inv_pos.x + dx, inv_pos.y)

        # Check edges
        for inv_go in self._invader_objects:
            if not inv_go.active:
                continue
            if self._direction.x > 0 and inv_go.transform.position.x >= self.screen_bound_x:
                self._advance_row()
                break
            elif self._direction.x < 0 and inv_go.transform.position.x <= -self.screen_bound_x:
                self._advance_row()
                break

        # Missile timer
        self._missile_timer += Time.delta_time
        if self._missile_timer >= self.missile_spawn_rate:
            self._missile_timer -= self.missile_spawn_rate
            self._missile_attack()

    def _advance_row(self):
        self._direction = Vector2(-self._direction.x, 0)
        pos = self.transform.position
        self.transform.position = Vector2(pos.x, pos.y - 1.0)
        for inv_go in self._invader_objects:
            if inv_go.active:
                inv_pos = inv_go.transform.position
                inv_go.transform.position = Vector2(inv_pos.x, inv_pos.y - 1.0)

    def _missile_attack(self):
        alive = self.get_alive_count()
        if alive == 0:
            return

        from space_invaders_python.projectile import Projectile
        from space_invaders_python.player import LAYER_MISSILE
        lm = LifecycleManager.instance()

        for inv_go in self._invader_objects:
            if not inv_go.active:
                continue
            if random.random() < (1.0 / alive):
                # Spawn missile
                missile = GameObject("Missile", tag="Missile")
                missile.layer = LAYER_MISSILE
                missile.transform.position = Vector2(
                    inv_go.transform.position.x,
                    inv_go.transform.position.y - 0.5,
                )

                rb = missile.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.KINEMATIC

                col = missile.add_component(BoxCollider2D)
                col.size = Vector2(0.2, 0.6)
                col.is_trigger = True
                col.build()

                sr = missile.add_component(SpriteRenderer)
                sr.color = (255, 80, 80)
                sr.size = Vector2(0.2, 0.6)
                sr.sorting_order = 5

                proj = missile.add_component(Projectile)
                proj.direction = Vector2(0, -1)
                proj.speed = 10.0
                lm.register_component(proj)
                break  # Only one missile per attack cycle

    def get_alive_count(self) -> int:
        return sum(1 for go in self._invader_objects if go.active)

    def reset_invaders(self):
        self._direction = Vector2(1, 0)
        self.transform.position = self._initial_position

        # Recalculate grid positions
        for idx, inv_go in enumerate(self._invader_objects):
            row = idx // self.columns
            col = idx % self.columns

            width = 2.0 * (self.columns - 1)
            height = 2.0 * (self.rows - 1)
            x = -width * 0.5 + 2.0 * col
            y = -height * 0.5 + 2.0 * row

            inv_go.transform.position = Vector2(
                self._initial_position.x + x,
                self._initial_position.y + y,
            )
            inv_go.active = True
