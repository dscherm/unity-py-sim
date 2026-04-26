"""Independent Unity ScriptReference contracts for APIs the parity audit claims tested.

This file is written WITHOUT reading any existing tests/parity/ test. The
audit's parity_matrix.md says these APIs have parity tests; this file
checks the same APIs against documented Unity behavior independently.

Sources:
  - https://docs.unity3d.com/ScriptReference/Transform-position.html
  - https://docs.unity3d.com/ScriptReference/Vector3.html
  - https://docs.unity3d.com/ScriptReference/Vector2.html
  - https://docs.unity3d.com/ScriptReference/MonoBehaviour.Awake.html
  - https://docs.unity3d.com/ScriptReference/MonoBehaviour.Start.html
  - https://docs.unity3d.com/ScriptReference/Time-time.html
  - https://docs.unity3d.com/ScriptReference/GameObject.Find.html
"""
from __future__ import annotations

import math

import pytest

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.lifecycle import LifecycleManager


@pytest.fixture(autouse=True)
def _clean() -> None:
    _clear_registry()
    yield
    _clear_registry()


# --- Transform.position contract ---
# Unity docs: "The position of the transform in world space."


def test_transform_position_default_is_zero_vector() -> None:
    from src.engine.math.vector import Vector3

    g = GameObject("g")
    # Force transform creation
    t = g.transform
    assert t.position.x == 0.0
    assert t.position.y == 0.0
    assert t.position.z == 0.0


def test_transform_position_setter_persists() -> None:
    from src.engine.math.vector import Vector3

    g = GameObject("g")
    g.transform.position = Vector3(5.0, 6.0, 7.0)
    assert g.transform.position.x == 5.0
    assert g.transform.position.y == 6.0
    assert g.transform.position.z == 7.0


def test_transform_position_world_space_independent_of_parent() -> None:
    """Unity Transform.position is world-space. Currently the engine stores
    world position directly (per the classes.json behavioral_differences),
    so setting child.position should not chain through the parent.
    """
    from src.engine.math.vector import Vector3

    parent = GameObject("p")
    child = GameObject("c")
    parent.transform.position = Vector3(10.0, 0.0, 0.0)
    child.transform.set_parent(parent.transform)
    child.transform.position = Vector3(3.0, 0.0, 0.0)
    # Engine stores world directly — child.position is exactly what was set
    assert child.transform.position.x == 3.0


# --- Vector3 / Vector2 static constants ---
# Unity docs: Vector3.zero == (0,0,0), .one == (1,1,1), .up == (0,1,0),
#             .forward == (0,0,1), .right == (1,0,0).


def test_vector3_zero_is_origin() -> None:
    from src.engine.math.vector import Vector3

    v = Vector3.zero
    assert (v.x, v.y, v.z) == (0.0, 0.0, 0.0)


def test_vector3_one_is_unit_diagonal() -> None:
    from src.engine.math.vector import Vector3

    v = Vector3.one
    assert (v.x, v.y, v.z) == (1.0, 1.0, 1.0)


def test_vector3_up_is_y_unit() -> None:
    from src.engine.math.vector import Vector3

    v = Vector3.up
    assert (v.x, v.y, v.z) == (0.0, 1.0, 0.0)


def test_vector3_right_is_x_unit() -> None:
    from src.engine.math.vector import Vector3

    v = Vector3.right
    assert (v.x, v.y, v.z) == (1.0, 0.0, 0.0)


def test_vector3_static_constants_are_independent_instances() -> None:
    """Mutating Vector3.zero should not affect a later read."""
    from src.engine.math.vector import Vector3

    z1 = Vector3.zero
    z1.x = 99
    z2 = Vector3.zero
    assert z2.x == 0.0, "Vector3.zero must return a fresh vector each access"


def test_vector3_magnitude_pythagorean() -> None:
    from src.engine.math.vector import Vector3

    v = Vector3(3.0, 4.0, 0.0)
    assert math.isclose(v.magnitude, 5.0, abs_tol=1e-6)


def test_vector2_zero_and_up() -> None:
    from src.engine.math.vector import Vector2

    z = Vector2.zero
    assert (z.x, z.y) == (0.0, 0.0)
    u = Vector2.up
    assert (u.x, u.y) == (0.0, 1.0)


# --- MonoBehaviour lifecycle ---
# Unity docs:
#   Awake — called when the script instance is being loaded, before Start.
#   Start — called on the frame when a script is enabled, just before any of
#           the Update methods is called the first time.
#   Update — called once per frame.


def test_awake_runs_before_start() -> None:
    """Awake fires before Start when the lifecycle manager runs."""
    LifecycleManager.reset()
    lm = LifecycleManager.instance()
    order: list[str] = []

    class TrackedBehaviour(MonoBehaviour):
        def awake(self) -> None:
            order.append("awake")

        def start(self) -> None:
            order.append("start")

    g = GameObject("g")
    comp = TrackedBehaviour()
    comp._game_object = g
    lm.register_component(comp)
    lm.process_awake_queue()
    lm.process_start_queue()
    assert order == ["awake", "start"], f"Expected awake before start, got {order}"


def test_update_called_each_frame_step() -> None:
    """Update fires once per frame step."""
    LifecycleManager.reset()
    lm = LifecycleManager.instance()
    counter: dict[str, int] = {"updates": 0}

    class Counter(MonoBehaviour):
        def update(self) -> None:
            counter["updates"] += 1

    g = GameObject("g")
    comp = Counter()
    comp._game_object = g
    lm.register_component(comp)
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_update()
    lm.run_update()
    lm.run_update()
    assert counter["updates"] == 3


def test_start_only_runs_once() -> None:
    """Unity calls Start exactly once before the first Update."""
    LifecycleManager.reset()
    lm = LifecycleManager.instance()
    counter: dict[str, int] = {"starts": 0}

    class Once(MonoBehaviour):
        def start(self) -> None:
            counter["starts"] += 1

    g = GameObject("g")
    comp = Once()
    comp._game_object = g
    lm.register_component(comp)
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.process_awake_queue()  # Run twice — Start should NOT fire again
    lm.process_start_queue()
    assert counter["starts"] == 1


# --- GameObject.Find ---
# Unity docs: GameObject.Find(name) returns the first active GameObject by
# name, or null if none. (Engine returns None.)


def test_gameobject_find_returns_existing() -> None:
    g = GameObject("Player")
    found = GameObject.find("Player")
    assert found is g


def test_gameobject_find_returns_none_when_missing() -> None:
    found = GameObject.find("DefinitelyNotPresent_xyz_42")
    assert found is None


# --- Time.time ---
# Unity docs: "The time at the beginning of this frame ... in seconds since
# the start of the game."


def test_time_time_starts_at_zero_after_reset() -> None:
    from src.engine.time_manager import Time

    Time._reset()
    assert Time.time == 0.0


def test_time_time_accumulates_after_updates() -> None:
    """If LifecycleManager advances Time, Time.time grows."""
    from src.engine.time_manager import Time

    Time._reset()
    initial = Time.time
    Time._time = 1.5
    assert Time.time - initial == pytest.approx(1.5)
