"""Contract tests for Flappy Bird engine APIs — derived from Unity documentation.

Tests verify engine behavior matches Unity's documented contracts, NOT the
implementation details of any particular game script.
"""

import pytest

from src.engine.core import MonoBehaviour, GameObject, Component, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.time_manager import Time
from src.engine.transform import Transform
from src.engine.math.vector import Vector3
from src.engine.math.quaternion import Quaternion
from src.engine.coroutine import WaitForSeconds
from src.engine.rendering.camera import Camera
from src.engine.random import Random


@pytest.fixture(autouse=True)
def clean_state():
    """Reset all global state between tests."""
    _clear_registry()
    LifecycleManager.reset()
    Time._reset()
    Camera._reset_main()
    # Reset GameManager singleton if loaded
    try:
        from examples.flappy_bird.flappy_bird_python.game_manager import GameManager
        GameManager.instance = None
    except ImportError:
        pass
    yield
    _clear_registry()
    LifecycleManager.reset()
    Time._reset()
    Camera._reset_main()


# ---------------------------------------------------------------------------
# InvokeRepeating — Unity docs: "Invokes the method methodName in time seconds,
# then repeatedly every repeatRate seconds."
# ---------------------------------------------------------------------------

class _Counter(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.count = 0

    def tick(self):
        self.count += 1


class TestInvokeRepeating:
    """Unity docs: InvokeRepeating calls method after delay, then every repeatRate seconds."""

    def _tick_lifecycle(self, lm, dt, n=1):
        """Simulate n frames with given delta time."""
        for _ in range(n):
            Time._delta_time = dt
            Time._time = Time._time + dt
            lm.run_update()  # This also ticks coroutines

    def test_initial_delay_before_first_call(self):
        """Method should NOT be called before the initial delay elapses."""
        go = GameObject("Test")
        comp = go.add_component(_Counter)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        comp.invoke_repeating("tick", 1.0, 0.5)

        # Tick for 0.5s — should not have fired yet (delay is 1.0)
        self._tick_lifecycle(lm, 0.5, 1)
        assert comp.count == 0, "Method called before initial delay expired"

    def test_fires_after_delay(self):
        """Method should fire once the initial delay elapses."""
        go = GameObject("Test")
        comp = go.add_component(_Counter)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        comp.invoke_repeating("tick", 0.5, 10.0)

        # Tick past the delay
        self._tick_lifecycle(lm, 0.6, 1)
        assert comp.count == 1, "Method should fire once after initial delay"

    def test_repeats_at_repeat_rate(self):
        """Method should fire repeatedly at the repeat rate after initial delay."""
        go = GameObject("Test")
        comp = go.add_component(_Counter)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        comp.invoke_repeating("tick", 0.0, 0.25)

        # Zero delay means first call happens immediately on first tick
        # Then repeats every 0.25s
        # Tick 4 times at 0.25s each = 1.0s total
        for _ in range(4):
            self._tick_lifecycle(lm, 0.25, 1)

        assert comp.count >= 3, f"Expected at least 3 repeats in 1.0s at 0.25 rate, got {comp.count}"

    def test_cancel_invoke_stops_repeating(self):
        """CancelInvoke should stop InvokeRepeating."""
        go = GameObject("Test")
        comp = go.add_component(_Counter)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        comp.invoke_repeating("tick", 0.0, 0.1)
        self._tick_lifecycle(lm, 0.15, 1)
        count_before = comp.count

        comp.cancel_invoke("tick")
        self._tick_lifecycle(lm, 1.0, 5)
        assert comp.count == count_before, "CancelInvoke did not stop repeating calls"


# ---------------------------------------------------------------------------
# CompareTag — Unity docs: "Returns true if the GameObject's tag matches."
# ---------------------------------------------------------------------------

class TestCompareTag:
    """Unity docs: CompareTag returns true only for exact tag match."""

    def test_exact_match_returns_true(self):
        go = GameObject("Test", tag="Player")
        assert go.compare_tag("Player") is True

    def test_different_tag_returns_false(self):
        go = GameObject("Test", tag="Player")
        assert go.compare_tag("Enemy") is False

    def test_case_sensitive(self):
        """Unity's CompareTag is case-sensitive."""
        go = GameObject("Test", tag="Player")
        assert go.compare_tag("player") is False

    def test_default_tag_is_untagged(self):
        go = GameObject("Test")
        assert go.compare_tag("Untagged") is True

    def test_empty_string_no_match(self):
        go = GameObject("Test", tag="Player")
        assert go.compare_tag("") is False


# ---------------------------------------------------------------------------
# FindObjectsOfType — Unity docs: "Returns a list of all active loaded objects
# of Type type." Does NOT return inactive objects.
# ---------------------------------------------------------------------------

class _Marker(MonoBehaviour):
    pass


class TestFindObjectsOfType:
    """Unity docs: FindObjectsOfType returns only active components."""

    def test_finds_active_components(self):
        go1 = GameObject("A")
        m1 = go1.add_component(_Marker)
        go2 = GameObject("B")
        m2 = go2.add_component(_Marker)

        found = GameObject.find_objects_of_type(_Marker)
        assert len(found) == 2
        assert m1 in found
        assert m2 in found

    def test_excludes_inactive_game_objects(self):
        go1 = GameObject("Active")
        go1.add_component(_Marker)
        go2 = GameObject("Inactive")
        go2.add_component(_Marker)
        go2.set_active(False)

        found = GameObject.find_objects_of_type(_Marker)
        assert len(found) == 1

    def test_returns_empty_when_none_exist(self):
        found = GameObject.find_objects_of_type(_Marker)
        assert found == []


# ---------------------------------------------------------------------------
# Instantiate — Unity docs: "Clones the object original and returns the clone.
# This function makes a copy of an object in a similar way to the Duplicate
# command in the editor." Children are also cloned.
# ---------------------------------------------------------------------------

class TestInstantiate:
    """Unity docs: Instantiate creates a deep copy including children."""

    def test_clone_has_same_name(self):
        original = GameObject("Prefab")
        clone = GameObject.instantiate(original)
        assert clone.name == "Prefab"

    def test_clone_is_different_object(self):
        original = GameObject("Prefab")
        clone = GameObject.instantiate(original)
        assert clone is not original
        assert clone.instance_id != original.instance_id

    def test_clone_includes_children(self):
        parent = GameObject("Parent")
        child_a = GameObject("ChildA")
        child_a.transform.set_parent(parent.transform)
        child_b = GameObject("ChildB")
        child_b.transform.set_parent(parent.transform)

        clone = GameObject.instantiate(parent)
        assert clone.transform.child_count == 2
        child_names = [c.game_object.name for c in clone.transform.children]
        assert "ChildA" in child_names
        assert "ChildB" in child_names

    def test_cloned_children_are_new_objects(self):
        parent = GameObject("Parent")
        child = GameObject("Child")
        child.transform.set_parent(parent.transform)

        clone = GameObject.instantiate(parent)
        original_child = parent.transform.children[0].game_object
        cloned_child = clone.transform.children[0].game_object
        assert cloned_child is not original_child
        assert cloned_child.instance_id != original_child.instance_id

    def test_position_override(self):
        original = GameObject("Prefab")
        original.transform.position = Vector3(0, 0, 0)
        target_pos = Vector3(10, 20, 0)

        clone = GameObject.instantiate(original, position=target_pos)
        assert abs(clone.transform.position.x - 10) < 0.01
        assert abs(clone.transform.position.y - 20) < 0.01

    def test_cloned_components_are_copies(self):
        """Components on the original should be duplicated, not shared."""
        original = GameObject("Prefab")
        original.add_component(_Marker)

        clone = GameObject.instantiate(original)
        orig_marker = original.get_component(_Marker)
        clone_marker = clone.get_component(_Marker)
        assert clone_marker is not None
        assert clone_marker is not orig_marker

    def test_clone_is_active(self):
        """Unity: Instantiate always returns an active clone, even if template was inactive."""
        original = GameObject("Prefab")
        original.active = False

        clone = GameObject.instantiate(original)
        assert clone.active is True


# ---------------------------------------------------------------------------
# OnEnable — Unity docs: "Called when the object becomes enabled and active.
# OnEnable is called just after the object is enabled. This happens when a
# MonoBehaviour instance is created, such as when a level is loaded or a
# GameObject with a MonoBehaviour component is instantiated."
# ---------------------------------------------------------------------------

class _EnableTracker(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.enable_count = 0
        self.disable_count = 0

    def on_enable(self):
        self.enable_count += 1

    def on_disable(self):
        self.disable_count += 1


class TestOnEnable:
    """Unity docs: OnEnable fires on first activation (after Awake) and each re-enable."""

    def test_on_enable_fires_after_awake_for_initially_enabled(self):
        go = GameObject("Test")
        comp = go.add_component(_EnableTracker)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()

        assert comp.enable_count == 1, "OnEnable should fire after Awake for initially-enabled components"

    def test_on_enable_fires_on_re_enable(self):
        go = GameObject("Test")
        comp = go.add_component(_EnableTracker)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()

        # Disable then re-enable
        comp.enabled = False
        comp.enabled = True
        assert comp.enable_count == 2, "OnEnable should fire again on re-enable"

    def test_on_disable_fires(self):
        go = GameObject("Test")
        comp = go.add_component(_EnableTracker)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()

        comp.enabled = False
        assert comp.disable_count == 1


# ---------------------------------------------------------------------------
# Time.timeScale — Unity docs: "The scale at which time passes. This can be
# used for slow motion effects or to speed up your application. When timeScale
# is 1.0, time passes as fast as real time. When timeScale is 0.5 time passes
# 2x slower than realtime. When timeScale is set to zero the game is basically
# paused." Update still runs, but Time.deltaTime becomes 0.
# ---------------------------------------------------------------------------

class TestTimeScale:
    """Unity docs: Time.timeScale = 0 pauses gameplay but Update still runs."""

    def test_time_scale_zero_makes_delta_time_zero(self):
        Time._delta_time = 0.016
        Time.set_time_scale(0.0)
        assert Time.delta_time == 0.0, "delta_time should be 0 when timeScale is 0"

    def test_time_scale_one_normal_delta(self):
        Time._delta_time = 0.016
        Time.set_time_scale(1.0)
        assert abs(Time.delta_time - 0.016) < 1e-6

    def test_time_scale_half_halves_delta(self):
        Time._delta_time = 0.016
        Time.set_time_scale(0.5)
        assert abs(Time.delta_time - 0.008) < 1e-6

    def test_update_still_runs_when_paused(self):
        """Unity docs: Update is still called when timeScale is 0."""

        class _UpdateCounter(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.updates = 0
            def update(self):
                self.updates += 1

        go = GameObject("Test")
        comp = go.add_component(_UpdateCounter)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        Time.set_time_scale(0.0)
        Time._delta_time = 0.016
        lm.run_update()

        assert comp.updates == 1, "Update should still be called when timeScale is 0"


# ---------------------------------------------------------------------------
# SetActive — Unity docs: "Activates/Deactivates the GameObject, depending on
# the given true or false value."
# ---------------------------------------------------------------------------

class TestSetActive:
    """Unity docs: SetActive(false) deactivates a GameObject."""

    def test_set_active_false_deactivates(self):
        go = GameObject("Test")
        go.set_active(False)
        assert go.active is False

    def test_set_active_true_activates(self):
        go = GameObject("Test")
        go.set_active(False)
        go.set_active(True)
        assert go.active is True

    def test_inactive_not_found_by_find(self):
        """Unity docs: Find only returns active GameObjects."""
        go = GameObject("Hidden")
        go.set_active(False)
        assert GameObject.find("Hidden") is None

    def test_inactive_not_found_by_tag(self):
        go = GameObject("Hidden", tag="Special")
        go.set_active(False)
        assert GameObject.find_with_tag("Special") is None


# ---------------------------------------------------------------------------
# DestroyImmediate — Unity docs: "Destroys the object obj immediately. You are
# strongly recommended to use Destroy instead."
# ---------------------------------------------------------------------------

class TestDestroyImmediate:
    """Unity docs: DestroyImmediate removes the object immediately."""

    def test_removes_from_registry(self):
        go = GameObject("Target")
        assert GameObject.find("Target") is not None
        GameObject.destroy_immediate(go)
        assert GameObject.find("Target") is None

    def test_calls_on_destroy(self):
        class _DestroyTracker(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.destroyed = False
            def on_destroy(self):
                self.destroyed = True

        go = GameObject("Target")
        comp = go.add_component(_DestroyTracker)
        GameObject.destroy_immediate(go)
        assert comp.destroyed is True

    def test_deactivates_object(self):
        go = GameObject("Target")
        GameObject.destroy_immediate(go)
        assert go.active is False


# ---------------------------------------------------------------------------
# Transform.eulerAngles — Unity docs: "The rotation as Euler angles in degrees.
# The x, y, and z angles represent a rotation z degrees around the z axis,
# x degrees around the x axis, and y degrees around the y axis (in that order)."
# ---------------------------------------------------------------------------

class TestEulerAngles:
    """Unity docs: Transform.eulerAngles get/set rotation in degrees."""

    def test_default_euler_angles_are_zero(self):
        go = GameObject("Test")
        ea = go.transform.euler_angles
        assert abs(ea.x) < 0.1
        assert abs(ea.y) < 0.1
        assert abs(ea.z) < 0.1

    def test_set_euler_angles(self):
        go = GameObject("Test")
        go.transform.euler_angles = Vector3(0, 0, 45)
        ea = go.transform.euler_angles
        assert abs(ea.z - 45) < 0.5, f"Expected z~45, got {ea.z}"

    def test_euler_angles_roundtrip(self):
        """Set euler angles, read back, should be approximately the same."""
        go = GameObject("Test")
        go.transform.euler_angles = Vector3(10, 20, 30)
        ea = go.transform.euler_angles
        assert abs(ea.x - 10) < 1.0, f"X: expected ~10, got {ea.x}"
        assert abs(ea.y - 20) < 1.0, f"Y: expected ~20, got {ea.y}"
        assert abs(ea.z - 30) < 1.0, f"Z: expected ~30, got {ea.z}"


# ---------------------------------------------------------------------------
# Camera.ScreenToWorldPoint — Unity docs: "Transforms a point from screen space
# into world space, where world space is defined as the coordinate system at the
# very top of your game's hierarchy."
# ---------------------------------------------------------------------------

class TestScreenToWorldPoint:
    """Unity docs: Camera.ScreenToWorldPoint converts screen pixels to world coordinates."""

    def test_screen_origin_maps_to_bottom_left_world(self):
        cam_go = GameObject("Cam")
        cam = cam_go.add_component(Camera)
        cam.orthographic_size = 5.0
        # Screen (0,0) should map to bottom-left of camera view
        # For a camera at origin with ortho_size 5.0 and 800x600 screen:
        # world_x = 0 + (0 - 400) / ppu, world_y = 0 - (0 - 300) / ppu
        result = cam.screen_to_world_point(Vector3(0, 0, 0), 800, 600)
        # With ortho_size=5 and height=600: ppu = 60
        # world_x = -400/60 = -6.67, world_y = +300/60 = 5.0
        assert result.x < 0, f"Expected negative x, got {result.x}"
        assert result.y > 0, f"Expected positive y, got {result.y}"

    def test_screen_center_maps_to_camera_position(self):
        cam_go = GameObject("Cam")
        cam = cam_go.add_component(Camera)
        cam_go.transform.position = Vector3(5, 10, 0)

        result = cam.screen_to_world_point(Vector3(400, 300, 0), 800, 600)
        assert abs(result.x - 5.0) < 0.1
        assert abs(result.y - 10.0) < 0.1


# ---------------------------------------------------------------------------
# Random.Range — Unity docs: "Returns a random float within [minInclusive..maxInclusive]"
# ---------------------------------------------------------------------------

class TestRandomRange:

    def test_range_within_bounds(self):
        for _ in range(100):
            val = Random.range(1.0, 5.0)
            assert 1.0 <= val <= 5.0, f"Value {val} out of range [1.0, 5.0]"

    def test_range_int_max_exclusive(self):
        """Unity docs: integer overload max is exclusive."""
        results = set()
        for _ in range(200):
            val = Random.range_int(0, 3)
            results.add(val)
            assert 0 <= val <= 2, f"Value {val} should be in [0, 2]"
        # With 200 tries, we should see all values 0, 1, 2
        assert results == {0, 1, 2}, f"Expected all values 0-2, got {results}"
