"""Translator regression tests surfaced by the FSM Platformer pipeline.

Running `tools/pipeline.py fsm_platformer` produces 20 C# files that the
structural gate accepts (parses cleanly) but Unity rejects with multiple
CS errors. These four classes of bugs surfaced 2026-04-29:

(1) **`isinstance` leaks**: Python `isinstance(x, T)` and tuple form
    `isinstance(x, (A, B))` are emitted verbatim into C#. The C#
    equivalent is `x is T` (single) or `(x is A || x is B)` (tuple).

(2) **`type(x).__name__` leaks**: Python's `type().__name__` introspection
    is emitted verbatim. C# has no `type()` builtin; the equivalent is
    `x.GetType().Name`.

(3) **Bare constructor calls**: Python `Foo()` instantiation is emitted as
    `Foo()` in C# — but C# requires `new Foo()` for user-defined classes.
    Hidden by Unity built-ins (Vector2, GameObject) which the translator
    already injects `new` for; surfaces for project-defined classes
    (PlayerIdleState, FSM, JumpTransition, etc.).

(4) **Implicit MonoBehaviour-to-derived assignment**: When a method
    parameter is `MonoBehaviour owner` (the translator's default for
    untyped owner-style params) and the body has a typed local
    `PlayerInputHandler player = owner`, C# rejects with CS0266 because
    base→derived needs an explicit cast.

These gaps are universal — fixing them improves translator output for any
future game that uses FSM/Command patterns.
"""

from __future__ import annotations

from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate


class TestIsinstanceTranslation:
    def test_single_class_isinstance_to_is_keyword(self):
        code = '''
from src.engine.core import MonoBehaviour


class A: pass
class B(A): pass


class Game(MonoBehaviour):
    def update(self) -> None:
        x: A = B()
        if isinstance(x, A):
            pass
'''
        cs = translate(parse_python(code))
        # Single-class isinstance translates to `is` operator
        assert "x is A" in cs, f"isinstance(x, A) → 'x is A' missing:\n{cs}"
        assert "isinstance(" not in cs, f"isinstance leaked into C#:\n{cs}"

    def test_tuple_isinstance_to_or_chain(self):
        code = '''
from src.engine.core import MonoBehaviour


class A: pass
class B: pass
class C: pass


class Game(MonoBehaviour):
    def update(self) -> None:
        x: A = A()
        if isinstance(x, (A, B)):
            pass
'''
        cs = translate(parse_python(code))
        # Tuple-form isinstance becomes a chain of `is` ORs.
        # Accept both compact `(x is A || x is B)` and parenthesized variants.
        assert "x is A" in cs
        assert "x is B" in cs
        assert "||" in cs
        assert "isinstance(" not in cs


class TestTypeDunderNameTranslation:
    def test_type_x_dot_dunder_name_to_get_type_dot_name(self):
        code = '''
from src.engine.core import MonoBehaviour


class Game(MonoBehaviour):
    def label(self) -> str:
        x = self
        return type(x).__name__
'''
        cs = translate(parse_python(code))
        # C# equivalent of Python `type(x).__name__`
        assert "x.GetType().Name" in cs or "GetType().Name" in cs, (
            f"type(x).__name__ → x.GetType().Name not emitted:\n{cs}"
        )
        # And the leaky raw Python form must NOT appear
        assert "type(x).__name__" not in cs
        assert ".__name__" not in cs


class TestConstructorNewKeyword:
    def test_user_class_call_gets_new_keyword(self):
        """Bare `Foo()` instantiation of a user-defined class must emit
        `new Foo()` in C# — same rule the translator already applies to
        Vector2/GameObject. Surfaced when PlayerInputHandler.Start emitted
        `var idleState = PlayerIdleState();` (CS0411 in Unity)."""
        code = '''
from src.engine.core import MonoBehaviour


class Helper:
    def __init__(self) -> None:
        pass


class Game(MonoBehaviour):
    def start(self) -> None:
        h = Helper()
'''
        cs = translate(parse_python(code))
        # `new Helper()` emitted, NOT bare `Helper()`
        assert "new Helper()" in cs, (
            f"User class instantiation missing 'new' keyword:\n{cs}"
        )
        # Specifically: `= Helper();` (without `new`) must not appear
        assert "= Helper();" not in cs

    def test_unity_class_already_gets_new_regression_guard(self):
        """Regression guard: existing Unity-class `new` injection must
        stay working alongside the new user-class path."""
        code = '''
from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2


class Game(MonoBehaviour):
    def start(self) -> None:
        v = Vector2(1, 2)
'''
        cs = translate(parse_python(code))
        assert "new Vector2(1" in cs


class TestMonoBehaviourDowncastEmitted:
    def test_typed_local_downcast_from_monobehaviour_param(self):
        """When a method parameter is `owner: MonoBehaviour` (or untyped,
        which the translator defaults to MonoBehaviour) and the body
        declares `player: Derived = owner`, an explicit cast is required.
        FSM Platformer's PlayerRunningState.Act + similar state classes
        all hit this — Python's duck-typing lets `owner` be any
        MonoBehaviour subclass, but C# needs the cast.

        The fix can take either form; the test accepts either an explicit
        `(Derived)owner` C-style cast or `owner as Derived` C# pattern."""
        code = '''
from src.engine.core import MonoBehaviour


class PlayerInputHandler(MonoBehaviour):
    move_speed: float = 3.0


class PlayerRunningState:
    def act(self, owner: MonoBehaviour) -> None:
        player: PlayerInputHandler = owner
        speed = player.move_speed
'''
        cs = translate(parse_python(code))
        # The downcast must appear in some valid C# form.
        downcast_present = (
            "(PlayerInputHandler)owner" in cs
            or "owner as PlayerInputHandler" in cs
            or "(PlayerInputHandler) owner" in cs
        )
        assert downcast_present, (
            f"Downcast from MonoBehaviour owner to PlayerInputHandler "
            f"missing — would be CS0266 in Unity:\n{cs}"
        )
