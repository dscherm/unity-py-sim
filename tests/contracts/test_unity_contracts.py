"""Contract tests verifying this engine matches Unity's documented behavior.

These are NOT "does my code work" tests -- they verify "does this match
how Unity actually behaves" according to the Unity documentation.
"""

from __future__ import annotations

import pytest

from src.engine.core import (
    Component,
    GameObject,
    MonoBehaviour,
    _clear_registry,
)
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.input_manager import Input
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.transform import Transform
from src.engine.scene import SceneManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_all():
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    Time._reset()
    Input._reset()


@pytest.fixture(autouse=True)
def clean_state():
    _reset_all()
    yield
    _reset_all()


# ===========================================================================
# Contract 1: Lifecycle ordering
# ===========================================================================

class TestLifecycleOrdering:
    """Unity contract: Awake -> Start -> FixedUpdate -> Update -> LateUpdate."""

    def test_awake_fires_before_start(self):
        """Awake must fire before Start on the same component."""
        log = []

        class Recorder(MonoBehaviour):
            def awake(self):
                log.append("awake")
            def start(self):
                log.append("start")

        go = GameObject("Test")
        rec = go.add_component(Recorder)
        lm = LifecycleManager.instance()
        lm.register_component(rec)
        lm.process_awake_queue()
        lm.process_start_queue()

        assert log == ["awake", "start"], f"Expected [awake, start], got {log}"

    def test_start_fires_before_first_update(self):
        """Start must complete before the first Update call."""
        log = []

        class Recorder(MonoBehaviour):
            def start(self):
                log.append("start")
            def update(self):
                log.append("update")

        go = GameObject("Test")
        rec = go.add_component(Recorder)
        lm = LifecycleManager.instance()
        lm.register_component(rec)
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.run_update()

        assert log.index("start") < log.index("update")

    def test_fixed_update_before_update_in_lifecycle(self):
        """FixedUpdate runs before Update in the Unity execution order."""
        log = []

        class Recorder(MonoBehaviour):
            def fixed_update(self):
                log.append("fixed_update")
            def update(self):
                log.append("update")

        go = GameObject("Test")
        rec = go.add_component(Recorder)
        lm = LifecycleManager.instance()
        lm.register_component(rec)
        lm.process_awake_queue()
        lm.process_start_queue()

        # Simulate one frame: fixed then update
        lm.run_fixed_update()
        lm.run_update()

        assert log == ["fixed_update", "update"], f"Got {log}"

    def test_late_update_after_update(self):
        """LateUpdate must fire after Update."""
        log = []

        class Recorder(MonoBehaviour):
            def update(self):
                log.append("update")
            def late_update(self):
                log.append("late_update")

        go = GameObject("Test")
        rec = go.add_component(Recorder)
        lm = LifecycleManager.instance()
        lm.register_component(rec)
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.run_update()
        lm.run_late_update()

        assert log == ["update", "late_update"], f"Got {log}"

    def test_on_destroy_fires_on_all_components(self):
        """OnDestroy should be called on every component when a GO is destroyed."""
        destroyed = []

        class Comp1(Component):
            def on_destroy(self):
                destroyed.append("comp1")

        class Comp2(Component):
            def on_destroy(self):
                destroyed.append("comp2")

        go = GameObject("Test")
        go.add_component(Comp1)
        go.add_component(Comp2)

        GameObject.destroy(go)

        assert "comp1" in destroyed
        assert "comp2" in destroyed


# ===========================================================================
# Contract 2: Collider defaults match Unity
# ===========================================================================

class TestColliderDefaults:
    """Unity contract: default friction=0.4, elasticity mapped to physics material."""

    def test_default_collider_friction_is_0_4(self):
        """Unity default PhysicsMaterial2D friction is 0.4."""
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.build()

        # The _register_shape method sets friction=0.4
        assert col._shape is not None
        assert abs(col._shape.friction - 0.4) < 0.001, (
            f"Expected friction=0.4, got {col._shape.friction}"
        )

    def test_default_collider_elasticity_is_0(self):
        """Unity's default PhysicsMaterial2D has bounciness=0 (not 1)."""
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.build()

        assert col._shape is not None
        assert abs(col._shape.elasticity - 0.0) < 0.001, (
            f"Expected elasticity=0.0 (Unity default), got {col._shape.elasticity}"
        )


# ===========================================================================
# Contract 3: Collision callback ordering (Enter then Exit)
# ===========================================================================

class TestCollisionCallbackOrdering:
    """Unity contract: Enter fires on first contact, Exit when contact ends."""

    def test_enter_fires_on_first_contact(self):
        """OnCollisionEnter2D fires when two bodies first touch."""
        events = []

        class Tracker(MonoBehaviour):
            def on_collision_enter_2d(self, collision):
                events.append("enter")
            def on_collision_exit_2d(self, collision):
                events.append("exit")

        pm = PhysicsManager.instance()

        # Ball
        ball = GameObject("Ball")
        ball.transform.position = Vector2(0, 3)
        rb_ball = ball.add_component(Rigidbody2D)
        rb_ball._body.position = (0, 3)
        col_ball = ball.add_component(CircleCollider2D)
        col_ball.radius = 0.5
        col_ball.build()
        tracker = ball.add_component(Tracker)
        LifecycleManager.instance().register_component(tracker)

        # Floor
        floor = GameObject("Floor")
        rb_floor = floor.add_component(Rigidbody2D)
        rb_floor.body_type = RigidbodyType2D.STATIC
        rb_floor._body.position = (0, 0)
        col_floor = floor.add_component(BoxCollider2D)
        col_floor.size = Vector2(20, 1)
        col_floor.build()

        # Step physics until collision
        for _ in range(200):
            pm.step(0.02)

        assert "enter" in events, "OnCollisionEnter2D never fired"

    def test_trigger_enter_fires_for_sensor_shapes(self):
        """OnTriggerEnter2D fires when overlapping a trigger collider."""
        events = []

        class Tracker(MonoBehaviour):
            def on_trigger_enter_2d(self, other):
                events.append("trigger_enter")

        pm = PhysicsManager.instance()

        # Projectile
        proj = GameObject("Proj")
        rb_proj = proj.add_component(Rigidbody2D)
        rb_proj._body.position = (0, 3)
        col_proj = proj.add_component(CircleCollider2D)
        col_proj.radius = 0.5
        col_proj.build()
        tracker = proj.add_component(Tracker)
        LifecycleManager.instance().register_component(tracker)

        # Trigger zone
        zone = GameObject("Zone")
        rb_zone = zone.add_component(Rigidbody2D)
        rb_zone.body_type = RigidbodyType2D.STATIC
        rb_zone._body.position = (0, 0)
        col_zone = zone.add_component(BoxCollider2D)
        col_zone.size = Vector2(10, 2)
        col_zone.is_trigger = True
        col_zone.build()

        for _ in range(200):
            pm.step(0.02)

        assert "trigger_enter" in events, "OnTriggerEnter2D never fired"


# ===========================================================================
# Contract 4: GameObject.Destroy semantics
# ===========================================================================

class TestDestroySemantics:
    """Unity contract: Destroy removes from Find, sets active=False, fires OnDestroy."""

    def test_destroyed_object_not_findable(self):
        """After Destroy, Find() should return None."""
        go = GameObject("Target")
        assert GameObject.find("Target") is not None

        GameObject.destroy(go)
        assert GameObject.find("Target") is None

    def test_destroyed_object_has_active_false(self):
        """After Destroy, active should be False."""
        go = GameObject("Target")
        assert go.active is True

        GameObject.destroy(go)
        assert go.active is False

    def test_on_destroy_callback_fires(self):
        """OnDestroy should fire on all components."""
        destroyed = []

        class Trackable(Component):
            def on_destroy(self):
                destroyed.append(self)

        go = GameObject("Target")
        comp = go.add_component(Trackable)
        GameObject.destroy(go)

        assert len(destroyed) == 1
        assert destroyed[0] is comp

    def test_destroyed_object_not_in_tag_search(self):
        """Destroyed objects should not appear in find_with_tag."""
        go = GameObject("Target", tag="Enemy")
        assert GameObject.find_with_tag("Enemy") is not None

        GameObject.destroy(go)
        assert GameObject.find_with_tag("Enemy") is None

    def test_find_game_objects_with_tag_excludes_destroyed(self):
        """find_game_objects_with_tag should not return destroyed objects."""
        go1 = GameObject("A", tag="Enemy")
        go2 = GameObject("B", tag="Enemy")
        assert len(GameObject.find_game_objects_with_tag("Enemy")) == 2

        GameObject.destroy(go1)
        result = GameObject.find_game_objects_with_tag("Enemy")
        assert len(result) == 1
        assert result[0] is go2


# ===========================================================================
# Contract 5: SceneManager.clear
# ===========================================================================

class TestSceneManagerContracts:
    """Unity contract: scene clear destroys all non-DontDestroyOnLoad objects."""

    def test_clear_removes_all_objects(self):
        """SceneManager.clear() should make all GameObjects unfindable."""
        go1 = GameObject("A")
        go2 = GameObject("B")
        go3 = GameObject("C")

        assert len(SceneManager.get_all_game_objects()) == 3

        SceneManager.clear()
        assert len(SceneManager.get_all_game_objects()) == 0
        assert GameObject.find("A") is None
        assert GameObject.find("B") is None


# ===========================================================================
# Contract 6: Input.GetKeyDown semantics
# ===========================================================================

class TestInputContracts:
    """Unity contract: GetKeyDown returns true only on the FIRST frame."""

    def test_get_key_down_true_on_first_frame(self):
        """GetKeyDown returns True the frame a key is first pressed."""
        Input._reset()
        Input._begin_frame()  # frame 0: no keys
        Input._set_key_state("space", True)

        assert Input.get_key_down("space") is True

    def test_get_key_down_false_on_subsequent_frames(self):
        """GetKeyDown returns False on the second frame while key held."""
        Input._reset()
        Input._begin_frame()  # frame 0
        Input._set_key_state("space", True)
        assert Input.get_key_down("space") is True

        # Next frame: key still held
        Input._begin_frame()  # snapshots current -> previous
        assert Input.get_key_down("space") is False, (
            "GetKeyDown should be False on second frame while key is held"
        )

    def test_get_key_up_true_on_release_frame(self):
        """GetKeyUp returns True the frame a key is released."""
        Input._reset()
        Input._begin_frame()
        Input._set_key_state("space", True)

        Input._begin_frame()  # space now in previous
        Input._set_key_state("space", False)

        assert Input.get_key_up("space") is True

    def test_get_key_returns_true_while_held(self):
        """GetKey returns True every frame while key is held."""
        Input._reset()
        Input._set_key_state("space", True)

        assert Input.get_key("space") is True
        Input._begin_frame()
        assert Input.get_key("space") is True  # still held

    def test_get_axis_returns_correct_values(self):
        """GetAxis for Horizontal should return 1.0 for 'd' and -1.0 for 'a'."""
        Input._reset()
        Input._set_key_state("d", True)
        assert Input.get_axis("Horizontal") == 1.0

        Input._set_key_state("d", False)
        Input._set_key_state("a", True)
        assert Input.get_axis("Horizontal") == -1.0


# ===========================================================================
# Contract 7: Transform hierarchy
# ===========================================================================

class TestTransformHierarchy:
    """Unity contract: parent-child relationships are consistent."""

    def test_set_parent_updates_children_list(self):
        """Setting parent should add child to parent's children."""
        parent = GameObject("Parent")
        child = GameObject("Child")

        child.transform.set_parent(parent.transform)
        assert child.transform in parent.transform.children

    def test_child_count_is_accurate(self):
        """child_count should reflect actual number of children."""
        parent = GameObject("Parent")
        assert parent.transform.child_count == 0

        c1 = GameObject("C1")
        c1.transform.set_parent(parent.transform)
        assert parent.transform.child_count == 1

        c2 = GameObject("C2")
        c2.transform.set_parent(parent.transform)
        assert parent.transform.child_count == 2

    def test_removing_parent_cleans_children_list(self):
        """Setting parent to None should remove from old parent's children."""
        parent = GameObject("Parent")
        child = GameObject("Child")

        child.transform.set_parent(parent.transform)
        assert parent.transform.child_count == 1

        child.transform.set_parent(None)
        assert parent.transform.child_count == 0
        assert child.transform not in parent.transform.children

    def test_reparenting_moves_between_parents(self):
        """Reparenting should remove from old parent and add to new."""
        p1 = GameObject("P1")
        p2 = GameObject("P2")
        child = GameObject("Child")

        child.transform.set_parent(p1.transform)
        assert p1.transform.child_count == 1
        assert p2.transform.child_count == 0

        child.transform.set_parent(p2.transform)
        assert p1.transform.child_count == 0
        assert p2.transform.child_count == 1


# ===========================================================================
# Contract 8: Physics gravity direction
# ===========================================================================

class TestPhysicsGravityContract:
    """Unity contract: default gravity is (0, -9.81)."""

    def test_default_gravity_is_downward(self):
        """Physics gravity should default to (0, -9.81)."""
        pm = PhysicsManager.instance()
        g = pm.gravity
        assert abs(g.x) < 0.001, f"Gravity x should be 0, got {g.x}"
        assert abs(g.y - (-9.81)) < 0.01, f"Gravity y should be -9.81, got {g.y}"


# ===========================================================================
# Contract 9: Time defaults
# ===========================================================================

class TestTimeContracts:
    """Unity contract: Time defaults match documented values."""

    def test_fixed_delta_time_default(self):
        """Unity's default fixed timestep is 0.02 (1/50)."""
        Time._reset()
        assert abs(Time._fixed_delta_time - 0.02) < 0.001, (
            f"Expected fixedDeltaTime=0.02, got {Time._fixed_delta_time}"
        )

    def test_time_scale_default_is_1(self):
        """Unity's default timeScale is 1.0."""
        Time._reset()
        assert abs(Time._time_scale - 1.0) < 0.001

    def test_frame_count_starts_at_zero(self):
        """Frame count should start at 0."""
        Time._reset()
        assert Time._frame_count == 0


# ===========================================================================
# Contract 10: Rigidbody2D body types
# ===========================================================================

class TestRigidbodyContracts:
    """Unity contract: body type enum maps correctly."""

    def test_default_body_type_is_dynamic(self):
        """New Rigidbody2D should default to Dynamic."""
        import pymunk
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        assert rb.body_type == RigidbodyType2D.DYNAMIC
        assert rb._body.body_type == pymunk.Body.DYNAMIC

    def test_static_body_type_maps_correctly(self):
        """Setting STATIC should map to pymunk STATIC."""
        import pymunk
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        assert rb._body.body_type == pymunk.Body.STATIC

    def test_kinematic_body_type_maps_correctly(self):
        """Setting KINEMATIC should map to pymunk KINEMATIC."""
        import pymunk
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.KINEMATIC
        assert rb._body.body_type == pymunk.Body.KINEMATIC

    def test_default_mass_is_1(self):
        """Unity default Rigidbody2D mass is 1."""
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        assert abs(rb.mass - 1.0) < 0.001


# ===========================================================================
# Contract 11: Component attachment
# ===========================================================================

class TestComponentContracts:
    """Unity contract: components are properly attached to GameObjects."""

    def test_component_knows_its_game_object(self):
        """After add_component, component.game_object returns the GO."""
        go = GameObject("Test")
        comp = go.add_component(Component)
        assert comp.game_object is go

    def test_get_component_returns_correct_type(self):
        """get_component should find attached components by type."""
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        found = go.get_component(Rigidbody2D)
        assert found is rb

    def test_get_component_returns_none_if_missing(self):
        """get_component returns None if type not attached."""
        go = GameObject("Test")
        assert go.get_component(Rigidbody2D) is None

    def test_transform_auto_created(self):
        """Accessing transform creates one if not present (Unity behavior)."""
        go = GameObject("Test")
        t = go.transform
        assert t is not None
        assert isinstance(t, Transform)
