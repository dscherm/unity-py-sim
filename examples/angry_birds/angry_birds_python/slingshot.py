"""Slingshot launcher — drag to aim, release to throw."""

from src.engine.core import GameObject, MonoBehaviour
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.input_manager import Input
from src.engine.rendering.camera import Camera
from src.engine.math.vector import Vector2, Vector3
from src.engine.debug import Debug
from src.engine.trajectory import predict_trajectory
from src.engine.physics.physics_manager import PhysicsManager

from .constants import Constants
from .enums import SlingshotState


class Slingshot(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.slingshot_state = SlingshotState.IDLE
        self.bird_to_throw: GameObject | None = None
        self.slingshot_center = Vector2(0, 0)
        self.throw_speed = Constants.THROW_SPEED
        self.time_since_thrown = 0.0

    def start(self):
        self.slingshot_center = Vector2(
            self.transform.position.x,
            self.transform.position.y,
        )

    def update(self):
        if self.slingshot_state == SlingshotState.IDLE:
            self._handle_idle()
        elif self.slingshot_state == SlingshotState.USER_PULLING:
            self._handle_pulling()

    def _handle_idle(self):
        if self.bird_to_throw is None:
            return
        if Input.get_mouse_button_down(0):
            mouse = Input.get_mouse_position()
            cam = Camera.main
            if cam is None:
                return
            from src.engine.rendering.display import DisplayManager
            dm = DisplayManager.instance()
            world_pos = cam.screen_to_world(
                (int(mouse[0]), int(mouse[1])), dm.width, dm.height
            )
            bird_pos = self.bird_to_throw.transform.position
            dist = Vector2.distance(world_pos, Vector2(bird_pos.x, bird_pos.y))
            if dist < Constants.BIRD_COLLIDER_RADIUS_BIG * 3:
                self.slingshot_state = SlingshotState.USER_PULLING

    def _handle_pulling(self):
        if self.bird_to_throw is None:
            return

        if Input.get_mouse_button(0):
            mouse = Input.get_mouse_position()
            cam = Camera.main
            if cam is None:
                return
            from src.engine.rendering.display import DisplayManager
            dm = DisplayManager.instance()
            world_pos = cam.screen_to_world(
                (int(mouse[0]), int(mouse[1])), dm.width, dm.height
            )
            # Clamp pull distance
            dist = Vector2.distance(world_pos, self.slingshot_center)
            if dist > Constants.SLINGSHOT_MAX_PULL:
                direction = (world_pos - self.slingshot_center).normalized
                world_pos = self.slingshot_center + direction * Constants.SLINGSHOT_MAX_PULL

            self.bird_to_throw.transform.position = world_pos

            # Draw trajectory preview
            velocity = self._calc_throw_velocity(world_pos)
            gravity = PhysicsManager.instance().gravity
            points = predict_trajectory(
                start=world_pos, velocity=velocity, gravity=gravity,
                segments=Constants.TRAJECTORY_SEGMENTS, time_step=0.08,
            )
            for i in range(len(points) - 1):
                Debug.draw_line(points[i], points[i + 1], color=(255, 255, 100), duration=0.0)

        else:
            # Released — throw or snap back
            bird_pos = Vector2(
                self.bird_to_throw.transform.position.x,
                self.bird_to_throw.transform.position.y,
            )
            dist = Vector2.distance(self.slingshot_center, bird_pos)
            if dist > 0.3:
                self._throw_bird(bird_pos, dist)
            else:
                self.bird_to_throw.transform.position = self.slingshot_center
                self.slingshot_state = SlingshotState.IDLE

    def _calc_throw_velocity(self, bird_pos: Vector2) -> Vector2:
        v = self.slingshot_center - bird_pos
        dist = Vector2.distance(self.slingshot_center, bird_pos)
        return Vector2(v.x * self.throw_speed * dist, v.y * self.throw_speed * dist)

    def _throw_bird(self, bird_pos: Vector2, distance: float):
        from .bird import Bird
        from src.engine.time_manager import Time

        velocity = self._calc_throw_velocity(bird_pos)
        bird_comp = self.bird_to_throw.get_component(Bird)
        if bird_comp:
            bird_comp.on_throw()

        rb = self.bird_to_throw.get_component(Rigidbody2D)
        if rb:
            rb.velocity = velocity

        self.time_since_thrown = Time.time
        self.slingshot_state = SlingshotState.BIRD_FLYING
