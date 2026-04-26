"""B2 — `inst._foo_bar` must emit `inst.fooBar`, not `inst.FooBar`.

Surfaced by the first live M-7 home-machine deploy run (workflow
24945292331): breakout's GameManager.cs declared its UI fields as
camelCase (`scoreText`) but emitted attribute access as PascalCase
(`inst.ScoreText`), producing CS1061. The two casings come from the
same Python identifier `_score_text`:

  * field declaration path: lstrip("_") then camelCase → `scoreText` ✅
  * symbol-table path: bare `snake_to_camel("_score_text")`

The bare call splits on `_` and gets `['', 'score', 'text']`, then
`parts[0] + Capitalize(rest)` yields `'' + 'Score' + 'Text' = 'ScoreText'`.
That's PascalCase, not camelCase, and it leaks through the symbol
table into every cross-instance attribute access.

The fix lives in `snake_to_camel` itself: strip leading underscores
before splitting, so all callers (field declarations AND symbol-table
lookups) produce identical names.
"""

from __future__ import annotations

from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate
from src.translator.type_mapper import snake_to_camel


class TestSnakeToCamelLeadingUnderscore:
    """Unit-level: leading underscores must not flip the result to PascalCase."""

    def test_single_leading_underscore(self):
        assert snake_to_camel("_score_text") == "scoreText"

    def test_single_leading_underscore_one_word(self):
        assert snake_to_camel("_canvas") == "canvas"

    def test_no_underscore_unchanged(self):
        # Regression guard: existing behavior must hold.
        assert snake_to_camel("speed") == "speed"
        assert snake_to_camel("delta_time") == "deltaTime"

    def test_no_leading_underscore_unchanged(self):
        assert snake_to_camel("input_axis") == "inputAxis"

    def test_multiple_leading_underscores_collapsed(self):
        # `__dunder_field` is rare in MonoBehaviours but if it appears
        # we want a sensible non-empty result, not "" or "DunderField".
        assert snake_to_camel("__dunder_field") == "dunderField"


class TestUnderscoreFieldAttributeAccess:
    """End-to-end: cross-instance access on a `_field` must match the field declaration."""

    def test_inst_dot_underscore_field_emits_camel_case(self):
        code = '''
from engine import MonoBehaviour

class GameManager(MonoBehaviour):
    _score_text: str = ""

    def update(self):
        inst: GameManager | None = GameManager._instance
        if inst is not None:
            inst._score_text = "Score: 0"
'''
        cs = translate(parse_python(code))
        # Field declaration must use camelCase
        assert "scoreText" in cs, f"Field declaration missing camelCase scoreText:\n{cs}"
        # Cross-instance access must ALSO use camelCase, not PascalCase
        assert "inst.scoreText" in cs, f"Expected inst.scoreText (camelCase):\n{cs}"
        assert "inst.ScoreText" not in cs, (
            f"PascalCase leak: inst.ScoreText must not appear "
            f"(field is declared as scoreText):\n{cs}"
        )

    def test_breakout_update_display_pattern(self):
        """Reproduces the exact GameManager._update_display() shape from breakout."""
        code = '''
from engine import MonoBehaviour

class GameManager(MonoBehaviour):
    _score_text: str = ""
    _lives_text: str = ""
    _status_text: str = ""

    @staticmethod
    def _update_display():
        inst: GameManager | None = GameManager._instance
        if inst is not None:
            inst._score_text = "Score: 0"
            inst._lives_text = "Lives: 3"
            inst._status_text = "Game Over!"
'''
        cs = translate(parse_python(code))
        # All three must be camelCase on both declaration AND access
        for camel, pascal in [
            ("scoreText", "ScoreText"),
            ("livesText", "LivesText"),
            ("statusText", "StatusText"),
        ]:
            assert f"inst.{camel}" in cs, f"Missing inst.{camel}:\n{cs}"
            assert f"inst.{pascal}" not in cs, (
                f"PascalCase regression: inst.{pascal} must not appear:\n{cs}"
            )

    def test_underscore_field_via_self_unaffected(self):
        """Self-access via `self._foo` is already correct — guard against regression."""
        code = '''
import engine

class Player(engine.MonoBehaviour):
    _health: int = 100

    def update(self):
        self._health = 50
'''
        cs = translate(parse_python(code))
        # `self._health` becomes either `health` or `this.health` — never PascalCase.
        assert "Health = 50" not in cs, f"PascalCase on self path:\n{cs}"
        assert "health" in cs, f"camelCase health missing:\n{cs}"
