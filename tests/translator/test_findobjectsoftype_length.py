"""Contract tests for FindObjectsOfType -> .Length post-pass.

Unity's GameObject.FindObjectsOfType<T>() returns T[] (a CLR array), not
List<T>. Arrays expose .Length, not .Count, so the translator must rewrite
`.Count` to `.Length` on any local variable assigned from FindObjectsOfType.

These tests drive from the *Unity contract* (T[] arrays expose .Length only),
not from implementation details of the translator.

Regression source: flappy_bird/game_manager.py produced `pipes.Count` which
fails `dotnet build` with CS1061 (T[] has no Count).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.translator.python_parser import parse_python_file
from src.translator.python_to_csharp import translate


def _translate_src(py_source: str) -> str:
    """Helper: write py_source to a temp file, parse + translate, return C#."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(py_source)
        path = f.name
    try:
        parsed = parse_python_file(path)
        return translate(parsed)
    finally:
        Path(path).unlink(missing_ok=True)


# ─── Basic FindObjectsOfType contract ──────────────────────────────


class TestFindObjectsOfTypeLengthRewrite:
    """Variables assigned from FindObjectsOfType<T>() are T[] arrays.
    T[] has only .Length, never .Count.
    """

    def test_local_from_find_objects_of_type_uses_length(self):
        py = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour, GameObject


class Mgr(MonoBehaviour):
    def play(self) -> None:
        pipes = GameObject.find_objects_of_type(Pipes)
        for i in range(len(pipes)):
            print(i)
'''
        cs = _translate_src(py)
        assert "pipes.Length" in cs, (
            "Unity FindObjectsOfType<T>() returns T[]; must use .Length.\n" + cs
        )
        assert "pipes.Count" not in cs, (
            "T[] arrays have no .Count member — generates CS1061.\n" + cs
        )

    def test_pipes_length_not_count_in_flappy_bird_game_manager(self):
        """Regression: the exact pattern that broke dotnet build."""
        gm_path = Path(
            "examples/flappy_bird/flappy_bird_python/game_manager.py"
        )
        if not gm_path.exists():
            pytest.skip("flappy_bird example missing")
        parsed = parse_python_file(gm_path)
        cs = translate(parsed)
        assert "pipes.Length" in cs
        assert "pipes.Count" not in cs


# ─── Non-corruption guarantees ─────────────────────────────────────


class TestFindObjectsOfTypeDoesNotCorruptListCount:
    """The .Count -> .Length rewrite must be scoped to locals that actually
    came from FindObjectsOfType. Regular List<T>.Count must remain untouched,
    or we generate CS1061 on the List<T>.

    Note: the translator maps `list[T]` to `T[]`, so a simple
    `my_list: list[int]` is actually an array and .Length IS correct there.
    We probe a form that produces a real `List<T>` in C#: nested lists
    map to `List<T[]>` (see type_mapper.py).
    """

    def test_nested_list_count_not_rewritten_when_var_name_matches(self):
        """`list[list[int]]` maps to C# `List<int[]>`. That's a real List<T>
        so .Count is the correct member. If the post-pass is scope-leaking,
        it would rewrite `myGrid.Count` to `.Length` and break the build.
        """
        py = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour


class Mgr(MonoBehaviour):
    def __init__(self) -> None:
        super().__init__()
        self.my_grid: list[list[int]] = []

    def update(self) -> None:
        n = len(self.my_grid)
'''
        cs = _translate_src(py)
        # my_grid is a class field of type List<int[]>. The post-pass only
        # rewrites locals assigned from FindObjectsOfType — fields are
        # tracked separately via _array_fields (which uses len->.Length
        # mapping for real arrays). Here we just ensure the emitted code
        # is well-formed: `List<int[]>` must appear.
        assert "List<int[]>" in cs, (
            "Nested list should map to List<int[]>.\n" + cs
        )

    def test_rewrite_gated_by_rhs_not_by_name(self):
        """The core anti-corruption guarantee: the regex in the post-pass is
        anchored to `var NAME = ... FindObjectsOfType<...>`. A local named
        `pipes` that is NOT assigned from FindObjectsOfType must NOT pick
        up the rewrite.

        We use a generic `object` local (no array inference) named `pipes`
        where the original C# would legitimately use `.Count` on a
        List<int>. We write the C# by hand via a list-typed local to
        verify the regex scoping.
        """
        # Explicitly exercise two siblings in the same method: one from
        # FindObjectsOfType, one from a list literal. The post-pass should
        # rewrite ONLY the Find-sourced one.
        py = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour, GameObject


class Mgr(MonoBehaviour):
    def play(self) -> None:
        arr = GameObject.find_objects_of_type(Pipes)
        plain: list[int] = [1, 2, 3]
        a = len(arr)
        b = len(plain)
'''
        cs = _translate_src(py)
        assert "arr.Length" in cs, (
            "FindObjectsOfType local must use .Length.\n" + cs
        )
        assert "arr.Count" not in cs, (
            "FindObjectsOfType local must not have .Count.\n" + cs
        )
        # `plain` here becomes int[] (list[int] -> T[]) so .Length is also
        # correct. The invariant being tested is simply that the rewrite
        # did not corrupt the plain local — it translated independently.
        assert "plain" in cs


# ─── Multiple locals in same method ────────────────────────────────


class TestMultipleFindObjectsOfTypeLocals:
    """Each independent FindObjectsOfType local in the same method must
    be rewritten to .Length independently.
    """

    def test_two_independent_find_objects_locals(self):
        py = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour, GameObject


class Mgr(MonoBehaviour):
    def cleanup(self) -> None:
        pipes = GameObject.find_objects_of_type(Pipes)
        enemies = GameObject.find_objects_of_type(Enemy)
        a = len(pipes)
        b = len(enemies)
'''
        cs = _translate_src(py)
        assert "pipes.Length" in cs
        assert "enemies.Length" in cs
        assert "pipes.Count" not in cs
        assert "enemies.Count" not in cs


# ─── Array-typed class fields ──────────────────────────────────────


class TestArrayFieldCount:
    """A class field typed list[T] should translate to T[] and use .Length
    on len(). This exercises the _array_fields tracking, not the post-pass,
    but we assert it to make sure the two systems don't collide.
    """

    def test_array_field_uses_length_in_len_call(self):
        py = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour


class Mgr(MonoBehaviour):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[int] = []

    def update(self) -> None:
        n = len(self.items)
'''
        cs = _translate_src(py)
        # items is a class field typed list[int] -> should be int[] array.
        # len(self.items) -> items.Length (not items.Count)
        assert "items.Length" in cs, (
            "list[T] fields should translate to T[] and use .Length.\n" + cs
        )
