"""Invaders — manages the grid, movement, speed scaling, and missile attacks.

Line-by-line port of: zigurous/Invaders.cs
"""

import random

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2, Vector3
from src.engine.time_manager import Time
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.lifecycle import LifecycleManager


# Row configs: animation colors and score (maps to Invader[] prefabs in C#)
ROW_CONFIG = [
    {"animation_sprites": [(50, 255, 50), (30, 200, 30)], "score": 10},
    {"animation_sprites": [(50, 255, 50), (30, 200, 30)], "score": 10},
    {"animation_sprites": [(50, 200, 255), (30, 150, 200)], "score": 20},
    {"animation_sprites": [(50, 200, 255), (30, 150, 200)], "score": 20},
    {"animation_sprites": [(255, 100, 100), (200, 60, 60)], "score": 30},
]


class Invaders(MonoBehaviour):

    def __init__(self):
        super().__init__()
        # [Header("Invaders")]
        # public Invader[] prefabs — we use ROW_CONFIG instead
        # public AnimationCurve speed — we use a simple function
        self.speed_curve_max: float = 5.0  # max speed multiplier
        self.direction: Vector3 = Vector3(1, 0, 0)  # Vector3.right
        self.initial_position: Vector3 = Vector3(0, 0, 0)

        # [Header("Grid")]
        self.rows: int = 5
        self.columns: int = 11

        # [Header("Missiles")]
        # public Projectile missilePrefab — we instantiate inline
        self.missile_spawn_rate: float = 1.0
        self._missile_timer: float = 0.0
        self._invader_children: list[GameObject] = []

    def awake(self):
        # initialPosition = transform.position
        self.initial_position = Vector3(
            self.transform.position.x,
            self.transform.position.y,
            0,
        )
        self._create_invader_grid()

    def _create_invader_grid(self):
        """private void CreateInvaderGrid()"""
        lm = LifecycleManager.instance()

        for i in range(self.rows):
            width = 2.0 * (self.columns - 1)
            height = 2.0 * (self.rows - 1)

            # Vector2 centerOffset = new Vector2(-width * 0.5f, -height * 0.5f)
            center_offset = Vector2(-width * 0.5, -height * 0.5)
            # Vector3 rowPosition = new Vector3(centerOffset.x, (2f * i) + centerOffset.y, 0f)
            row_position = Vector3(center_offset.x, (2.0 * i) + center_offset.y, 0)

            config = ROW_CONFIG[i % len(ROW_CONFIG)]

            for j in range(self.columns):
                # Invader invader = Instantiate(prefabs[i], transform)
                from space_invaders_python.invader import Invader

                invader_go = GameObject(f"Invader_{i}_{j}", tag="Invader")
                invader_go.layer = 10  # LAYER_INVADER

                rb = invader_go.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.KINEMATIC

                col = invader_go.add_component(BoxCollider2D)
                col.size = Vector2(1.5, 1.5)
                col.is_trigger = True
                col.build()

                sr = invader_go.add_component(SpriteRenderer)
                sr.color = config["animation_sprites"][0]
                sr.size = Vector2(1.5, 1.0)
                sr.sorting_order = 2

                inv = invader_go.add_component(Invader)
                inv.score = config["score"]
                inv.animation_sprites = config["animation_sprites"]
                lm.register_component(inv)

                # Vector3 position = rowPosition; position.x += 2f * j
                position = Vector3(row_position.x + 2.0 * j, row_position.y, 0)
                # invader.transform.localPosition = position
                invader_go.transform.position = Vector2(
                    self.transform.position.x + position.x,
                    self.transform.position.y + position.y,
                )

                self._invader_children.append(invader_go)

    def start(self):
        # InvokeRepeating(nameof(MissileAttack), missileSpawnRate, missileSpawnRate)
        # Handled via timer in update
        pass

    def _missile_attack(self):
        """private void MissileAttack()"""
        amount_alive = self.get_alive_count()

        # if (amountAlive == 0) return
        if amount_alive == 0:
            return

        # foreach (Transform invader in transform)
        for invader_go in self._invader_children:
            # if (!invader.gameObject.activeInHierarchy) continue
            if not invader_go.active:
                continue

            # if (Random.value < (1f / amountAlive))
            if random.random() < (1.0 / amount_alive):
                # Instantiate(missilePrefab, invader.position, Quaternion.identity)
                self._instantiate_missile(invader_go.transform.position)
                break

    def _instantiate_missile(self, position):
        """Instantiate(missilePrefab, invader.position, Quaternion.identity)"""
        from space_invaders_python.projectile import Projectile
        from space_invaders_python.player import LAYER_MISSILE

        missile = GameObject("Missile", tag="Missile")
        missile.layer = LAYER_MISSILE
        missile.transform.position = Vector2(position.x, position.y - 0.5)

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
        proj.direction = Vector3(0, -1, 0)  # Vector3.down
        proj.speed = 10.0
        LifecycleManager.instance().register_component(proj)

    def update(self):
        # Speed scaling based on percent killed
        total_count = self.rows * self.columns
        amount_alive = self.get_alive_count()
        amount_killed = total_count - amount_alive
        percent_killed = amount_killed / float(total_count) if total_count > 0 else 0

        # float speed = this.speed.Evaluate(percentKilled)
        # AnimationCurve approximation: linear 1.0 → speed_curve_max
        speed = 1.0 + percent_killed * (self.speed_curve_max - 1.0)

        # transform.position += speed * Time.deltaTime * direction
        pos = self.transform.position
        dx = speed * Time.delta_time * self.direction.x
        self.transform.position = Vector2(pos.x + dx, pos.y)

        # Move children (no real parent-child transform in physics)
        for invader_go in self._invader_children:
            if invader_go.active:
                inv_pos = invader_go.transform.position
                invader_go.transform.position = Vector2(inv_pos.x + dx, inv_pos.y)

        # Edge detection
        left_edge = -6.5
        right_edge = 6.5

        # foreach (Transform invader in transform)
        for invader_go in self._invader_children:
            if not invader_go.active:
                continue

            # if (direction == Vector3.right && invader.position.x >= (rightEdge.x - 1f))
            if self.direction.x > 0 and invader_go.transform.position.x >= (right_edge - 1.0):
                self._advance_row()
                break
            elif self.direction.x < 0 and invader_go.transform.position.x <= (left_edge + 1.0):
                self._advance_row()
                break

        # Missile timer (InvokeRepeating equivalent)
        self._missile_timer += Time.delta_time
        if self._missile_timer >= self.missile_spawn_rate:
            self._missile_timer -= self.missile_spawn_rate
            self._missile_attack()

    def _advance_row(self):
        """private void AdvanceRow()"""
        # direction = new Vector3(-direction.x, 0f, 0f)
        self.direction = Vector3(-self.direction.x, 0, 0)

        # Vector3 position = transform.position; position.y -= 1f
        pos = self.transform.position
        self.transform.position = Vector2(pos.x, pos.y - 1.0)

        for invader_go in self._invader_children:
            if invader_go.active:
                inv_pos = invader_go.transform.position
                invader_go.transform.position = Vector2(inv_pos.x, inv_pos.y - 1.0)

    def reset_invaders(self):
        """public void ResetInvaders()"""
        self.direction = Vector3(1, 0, 0)  # Vector3.right
        self.transform.position = Vector2(self.initial_position.x, self.initial_position.y)

        # Recalculate positions
        for idx, invader_go in enumerate(self._invader_children):
            row = idx // self.columns
            col = idx % self.columns

            width = 2.0 * (self.columns - 1)
            height = 2.0 * (self.rows - 1)
            x = -width * 0.5 + 2.0 * col
            y = -height * 0.5 + 2.0 * row

            invader_go.transform.position = Vector2(
                self.initial_position.x + x,
                self.initial_position.y + y,
            )
            # invader.gameObject.SetActive(true)
            invader_go.active = True

    def get_alive_count(self) -> int:
        """public int GetAliveCount()"""
        count = 0
        for invader_go in self._invader_children:
            if invader_go.active:
                count += 1
        return count
