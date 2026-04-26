"""Contract tests for transform.children post-pass rewrite.

Unity's Transform implements only the non-generic IEnumerator; it does not
implement IEnumerable<Transform>. Using `var child` in a foreach over a
Transform would therefore infer `object`, and the resulting code won't
compile when code downstream treats child as Transform.

The translator must:
  1. Rewrite `foreach (var x in <expr>.transform.children)`
     to `foreach (Transform x in <expr>.transform)` — explicit Transform.
  2. Strip `.children` from any remaining references on a transform
     (e.g. `x = obj.transform.children[0]` -> `x = obj.transform[0]`).
  3. Leave any unrelated identifier called `children` alone
     (e.g. `my_dict.children` must not be stripped).

Regression source: flappy_bird/spawner.py produced
`foreach (var child in pipesGo.transform.children)` which fails dotnet build
with CS1579 (no public GetEnumerator on IEnumerator).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.translator.python_parser import parse_python_file
from src.translator.python_to_csharp import translate


def _translate_src(py_source: str) -> str:
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


# ─── foreach rewrite ───────────────────────────────────────────────


class TestForeachTransformChildrenRewrite:
    def test_foreach_over_other_objects_transform_children(self):
        """`for c in pipes_go.transform.children: ...` must use Transform,
        not var, in the foreach — and iterate pipesGo.transform directly.
        """
        py = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour, GameObject


class Sp(MonoBehaviour):
    def spawn(self) -> None:
        pipes_go: GameObject | None = None
        if pipes_go is not None:
            for c in pipes_go.transform.children:
                print(c.game_object.name)
'''
        cs = _translate_src(py)
        assert "foreach (Transform c in pipesGo.transform)" in cs, (
            "foreach over transform.children must yield Transform c (not var) "
            "and iterate transform directly.\n" + cs
        )
        assert "transform.children" not in cs, (
            "Transform has no .children property; must be stripped.\n" + cs
        )
        assert "foreach (var c" not in cs, (
            "var would infer 'object' from non-generic IEnumerator.\n" + cs
        )

    def test_foreach_over_self_transform_children(self):
        py = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour


class Holder(MonoBehaviour):
    def update(self) -> None:
        for c in self.transform.children:
            print(c.game_object.name)
'''
        cs = _translate_src(py)
        assert "foreach (Transform c in transform)" in cs, (
            "self.transform.children -> transform (no .children).\n" + cs
        )
        assert "transform.children" not in cs

    def test_flappy_bird_spawner_no_transform_children(self):
        """Regression: the exact pattern that broke dotnet build."""
        sp = Path("examples/flappy_bird/flappy_bird_python/spawner.py")
        if not sp.exists():
            pytest.skip("flappy_bird example missing")
        parsed = parse_python_file(sp)
        cs = translate(parsed)
        assert "transform.children" not in cs, (
            "Spawner must not reference Transform.children.\n" + cs
        )
        assert "foreach (Transform child in pipesGo.transform)" in cs


# ─── Non-foreach uses ──────────────────────────────────────────────


class TestNonForeachTransformChildren:
    """Any other .children reference on a transform should get the .children
    suffix stripped so that Transform's native indexer / enumerator is used.
    """

    def test_bare_transform_children_stripped(self):
        py = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour


class H(MonoBehaviour):
    def update(self) -> None:
        _ = self.transform.children
'''
        cs = _translate_src(py)
        assert "transform.children" not in cs, (
            "Bare transform.children must be rewritten to transform.\n" + cs
        )


# ─── Non-corruption: unrelated 'children' identifier ───────────────


class TestChildrenIdentifierNotOnTransformUntouched:
    """The post-pass regex matches the literal substring `transform.children`.
    Any identifier named `children` that is NOT preceded by `transform.`
    must be untouched (e.g. a dict field named children).
    """

    def test_dict_children_attribute_untouched(self):
        py = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour


class H(MonoBehaviour):
    def __init__(self) -> None:
        super().__init__()
        self.children: list[int] = []

    def update(self) -> None:
        n = len(self.children)
'''
        cs = _translate_src(py)
        # The translator emits `children.Length` from len(self.children).
        # The post-pass must NOT mangle `children` into something else.
        assert "children" in cs, (
            "Identifier 'children' (not on a transform) must survive.\n" + cs
        )
        # Sanity: we did not strip 'children' from a non-transform context
        # into an empty identifier or similar.
        assert ".Length" in cs or ".length" in cs
