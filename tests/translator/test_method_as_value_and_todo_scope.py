"""Translator regression tests surfaced by the Space Invaders home_machine deploy.

Two distinct bugs landed against the same generated project (workflow
~24987xxxxx, 2026-04-28):

(1) **Method-as-value RHS naming.** `self._invoke_callback = self._new_round`
    used to emit `this.invokeCallback = newRound;` — but `NewRound` is the
    PascalCase method name on the class. The bare `_self_dot_replace`
    pass treated `_new_round` as a field reference and camelCased it,
    leaving a dangling identifier (no `newRound` field exists).

(2) **TODO scope leakage.** When `project_translator._postprocess` decides
    to comment out a line that defines a local (e.g. `InvaderRowConfig
    config = Invaders.ROW_CONFIG[...]`), it must ALSO comment out every
    downstream use of `config` — otherwise the C# refers to an undefined
    symbol. The previous regex only matched `var X = ROW_CONFIG`, so
    typed declarations (`InvaderRowConfig config = ...`) escaped the
    tracking and their consumers stayed live.

Both manifested as Unity compile errors that the local `dotnet build`
stub gate did not catch.
"""

from __future__ import annotations

from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate


class TestMethodAsValueRhsEmitsPascalCase:
    """`self._method = self._other_method` (method as value) must emit the
    PascalCase method name on both sides — RHS especially, where the bare
    attribute access used to fall through to field-style camelCase."""

    def test_method_reference_assignment_uses_pascal_case(self):
        code = '''
from src.engine.core import MonoBehaviour


class Game(MonoBehaviour):
    def __init__(self) -> None:
        super().__init__()
        self._invoke_callback: object | None = None

    def on_player_killed(self) -> None:
        self._invoke_callback = self._new_round

    def _new_round(self) -> None:
        pass
'''
        cs = translate(parse_python(code))
        # The method definition is PascalCase
        assert "void NewRound(" in cs, f"Method def missing:\n{cs}"
        # The RHS reference must point at NewRound (the method), not
        # newRound (which would be a non-existent field).
        assert "= NewRound" in cs or "= this.NewRound" in cs, (
            f"Expected method-as-value to use PascalCase NewRound:\n{cs}"
        )
        # Critical: the wrong form must not appear. `newRound` would be a
        # dangling identifier — there is no field by that name.
        assert "= newRound" not in cs, (
            f"Method-as-value emitted as field-style camelCase newRound:\n{cs}"
        )

    def test_field_named_like_method_still_camel_when_no_method_match(self):
        """A `self._foo` reference where `_foo` is NOT a class method must
        stay camelCase — the new method-name short-circuit must not
        over-fire on plain field reads. Guards against my fix promoting
        every `self._X` to PascalCase regardless of whether `X` is a method."""
        code = '''
from src.engine.core import MonoBehaviour


class Game(MonoBehaviour):
    def __init__(self) -> None:
        super().__init__()
        self._invoke_callback: object | None = None
        self._score_value: int = 0

    def update(self) -> None:
        # Plain field read on RHS — must NOT be promoted to PascalCase
        if self._score_value > 10:
            pass
'''
        cs = translate(parse_python(code))
        # `_score_value` is a field, not a method — it must read as `scoreValue`,
        # NOT `ScoreValue`.
        assert "scoreValue" in cs, f"Field declaration missing scoreValue:\n{cs}"
        assert "this.ScoreValue" not in cs and "(ScoreValue " not in cs, (
            f"PascalCase leak — `_score_value` is a field, not a method:\n{cs}"
        )

    def test_lifecycle_method_reference_uses_unity_name(self):
        """Method references to lifecycle methods (start/update/awake)
        must emit the Unity PascalCase name (Start/Update/Awake), not
        the snake form."""
        code = '''
from src.engine.core import MonoBehaviour


class Game(MonoBehaviour):
    def __init__(self) -> None:
        super().__init__()
        self._cb: object | None = None

    def awake(self) -> None:
        self._cb = self.start

    def start(self) -> None:
        pass
'''
        cs = translate(parse_python(code))
        # The RHS method reference should be `Start` (the Unity lifecycle name).
        # `start` (lowercase) would be wrong: that's the Python source name.
        assert "= Start" in cs or "= this.Start" in cs, (
            f"Lifecycle method-reference missing:\n{cs}"
        )


class TestTodoScopeLeakageOnTypedLocal:
    """When a typed local declaration is commented out as TODO (because
    its initializer touches an unsupported symbol like ROW_CONFIG), all
    downstream references to that local must ALSO be commented out —
    otherwise the C# fails to compile with CS0103 'name does not exist'.

    The TODO scope-tracking lives in `project_translator._post_process`
    (which file-level `translate()` does not exercise), so the tests
    drive `_post_process` directly with synthesized C# fragments shaped
    like the actual translator output.
    """

    def test_var_local_initialised_from_row_config_already_propagates(self):
        """Pre-existing behavior: `var X = ROW_CONFIG[...]` already tracks
        downstream uses. Regression guard for the broadened regex."""
        from src.translator.project_translator import _post_process

        cs_in = """\
public class Invaders : MonoBehaviour
{
    void CreateGrid() {
        for (int i = 0; i < rows; i++) {
            var config = ROW_CONFIG[i % ROW_CONFIG.Length];
            sr.color = config.color;
            inv.score = config.score;
        }
    }
}
"""
        cs_out = _post_process(cs_in, {}, {})
        # The `var config` line is TODO'd
        for ln in cs_out.splitlines():
            if "config" in ln and "ROW_CONFIG" in ln:
                assert "// TODO:" in ln, f"var-form decl not TODO'd: {ln}"
            # And downstream `config.X` lines too
            if ("config.color" in ln or "config.score" in ln) and "ROW_CONFIG" not in ln:
                assert "// TODO:" in ln, f"var-form downstream use not TODO'd: {ln}"

    def test_typed_local_initialised_from_row_config_propagates_todo(self):
        """Reproduces the Space Invaders Invaders.cs failure shape:
        `InvaderRowConfig config = Invaders.ROW_CONFIG[i % ...]` was
        commented out, but `config.score` and `config.animation_sprites`
        downstream referenced a now-undefined local."""
        from src.translator.project_translator import _post_process

        cs_in = """\
public class Invaders : MonoBehaviour
{
    void CreateGrid() {
        for (int i = 0; i < rows; i++) {
            InvaderRowConfig config = Invaders.ROW_CONFIG[i % Invaders.ROW_CONFIG.Length];
            sr.color = config.animationSprites[0];
            inv.score = config.score;
            inv.animationSprites = config.animationSprites;
        }
    }
}
"""
        cs_out = _post_process(cs_in, {}, {})
        # The defining line must be commented out (it references ROW_CONFIG).
        lines = cs_out.splitlines()
        config_decl_lines = [ln for ln in lines if "config" in ln and "ROW_CONFIG" in ln]
        assert config_decl_lines, f"config decl not present at all:\n{cs_out}"
        for ln in config_decl_lines:
            assert "// TODO:" in ln, (
                f"config decl referencing ROW_CONFIG must be TODO'd:\n{ln}"
            )

        # Every downstream `config.X` reference must also be TODO'd. A
        # bare `config.score` line would be a dangling identifier.
        config_use_lines = [
            ln for ln in lines
            if ("config.score" in ln or "config.animationSprites" in ln)
            and "ROW_CONFIG" not in ln
        ]
        assert config_use_lines, "No config.X uses found — test setup wrong"
        for ln in config_use_lines:
            assert "// TODO:" in ln, (
                f"Downstream config.X reference not TODO'd "
                f"(would be CS0103 in Unity):\n{ln}\n--- full output ---\n{cs_out}"
            )
