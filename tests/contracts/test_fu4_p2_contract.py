"""Contract tests for FU-4 P2 fixes (commit c1ebf95).

Derived independently from:
  - Unity 6 API contract: FindObjectsByType<T>(FindObjectsSortMode)
  - EditorSceneManager.SaveScene / SaveOpenScenes path semantics
  - EditorApplication.isPlaying play-mode guard contract

DO NOT read existing test files before writing these — derived from Unity docs
and src/ source only.
"""

from __future__ import annotations

import re
import textwrap


from src.translator.python_parser import parse_python_file, PyFile
from src.translator.python_to_csharp import translate
from src.exporter.coplay_generator import generate_scene_script, generate_validation_script


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(source: str) -> PyFile:
    """Parse a Python source string into a PyFile IR via a temp file."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(source)
        tmp = f.name
    try:
        return parse_python_file(tmp)
    finally:
        os.unlink(tmp)


def _translate_src(source: str, unity_version: int = 6) -> str:
    parsed = _parse(source)
    return translate(parsed, unity_version=unity_version)


def _minimal_scene(n_objects: int = 1) -> dict:
    return {
        "game_objects": [
            {
                "name": f"Obj{i}",
                "components": [
                    {"type": "Transform", "position": [0, 0, 0], "local_scale": [1, 1, 1]},
                ],
            }
            for i in range(n_objects)
        ]
    }


# ---------------------------------------------------------------------------
# Scenario 1 — FindObjectsByType direction switch (unity_version gate)
# ---------------------------------------------------------------------------

class TestFindObjectsDirectionSwitch:
    """Unity 6 must emit FindObjectsByType; Unity 5 must emit FindObjectsOfType."""

    _SRC_TWO_SITES = textwrap.dedent("""\
        from src.engine.core import MonoBehaviour

        class Manager(MonoBehaviour):
            def update(self):
                widgets_a = GameObject.find_objects_of_type(Widget)
                widgets_b = GameObject.find_objects_of_type(Widget)
        """)

    def test_unity6_emits_find_objects_by_type(self):
        cs = _translate_src(self._SRC_TWO_SITES, unity_version=6)
        assert "FindObjectsByType<Widget>(FindObjectsSortMode.None)" in cs, \
            f"Expected FindObjectsByType with FindObjectsSortMode.None in Unity 6 output:\n{cs}"

    def test_unity6_does_not_emit_find_objects_of_type(self):
        cs = _translate_src(self._SRC_TWO_SITES, unity_version=6)
        assert "FindObjectsOfType<Widget>" not in cs, \
            f"FindObjectsOfType must not appear in Unity 6 output:\n{cs}"

    def test_unity5_emits_find_objects_of_type(self):
        cs = _translate_src(self._SRC_TWO_SITES, unity_version=5)
        assert "FindObjectsOfType<Widget>()" in cs, \
            f"Expected legacy FindObjectsOfType in Unity 5 output:\n{cs}"

    def test_unity5_does_not_emit_find_objects_by_type(self):
        cs = _translate_src(self._SRC_TWO_SITES, unity_version=5)
        assert "FindObjectsByType" not in cs, \
            f"FindObjectsByType must not appear in Unity 5 output:\n{cs}"

    def test_unity6_rewrites_multiple_call_sites(self):
        """Both call sites in the same method must be rewritten — not just the first."""
        cs = _translate_src(self._SRC_TWO_SITES, unity_version=6)
        count = cs.count("FindObjectsByType<Widget>(FindObjectsSortMode.None)")
        assert count >= 2, \
            f"Expected at least 2 rewrites (multiple call sites), got {count}:\n{cs}"


# ---------------------------------------------------------------------------
# Scenario 2 — FindObjectsSortMode.None survives the None→null pass
# ---------------------------------------------------------------------------

class TestFindObjectsSortModeNoneSurvival:
    """The targeted reversal must keep FindObjectsSortMode.None capitalised AND
    must not accidentally re-uppercase ordinary null tokens elsewhere."""

    _SRC = textwrap.dedent("""\
        from src.engine.core import MonoBehaviour

        class Example(MonoBehaviour):
            target: object = None

            def update(self):
                objs = GameObject.find_objects_of_type(Widget)
                if self.target is None:
                    self.target = objs
        """)

    def test_find_objects_sort_mode_none_preserved(self):
        cs = _translate_src(self._SRC, unity_version=6)
        assert "FindObjectsSortMode.None" in cs, \
            f"FindObjectsSortMode.None was corrupted (lowered to .null or missing):\n{cs}"

    def test_find_objects_sort_mode_null_absent(self):
        cs = _translate_src(self._SRC, unity_version=6)
        assert "FindObjectsSortMode.null" not in cs, \
            f"FindObjectsSortMode.null must not appear (reversal failed):\n{cs}"

    def test_ordinary_none_still_becomes_null(self):
        """Python None in non-enum context must still translate to C# null."""
        cs = _translate_src(self._SRC, unity_version=6)
        # `if self.target is None` → `if (this.target == null)`
        assert "null" in cs, \
            f"Ordinary None→null conversion must still fire:\n{cs}"

    def test_no_accidental_null_recapitalised_to_None(self):
        """After reversal pass, there must be no bare token 'None' other than
        inside FindObjectsSortMode.None."""
        cs = _translate_src(self._SRC, unity_version=6)
        # Strip FindObjectsSortMode.None occurrences, then check no bare None remains
        stripped = cs.replace("FindObjectsSortMode.None", "")
        bare_None = re.search(r'\bNone\b', stripped)
        assert bare_None is None, \
            f"Bare 'None' token found outside FindObjectsSortMode context:\n{stripped}"


# ---------------------------------------------------------------------------
# Scenario 3 — .Count → .Length on FindObjectsByType locals
# ---------------------------------------------------------------------------

class TestCountToLengthRewrite:
    """Arrays returned by FindObjectsByType expose .Length (C# array), not .Count."""

    _SRC = textwrap.dedent("""\
        from src.engine.core import MonoBehaviour

        class Manager(MonoBehaviour):
            def update(self):
                widgets = GameObject.find_objects_of_type(Widget)
                n = widgets.Count
        """)

    def test_count_rewritten_to_length(self):
        cs = _translate_src(self._SRC, unity_version=6)
        assert "widgets.Length" in cs, \
            f"Expected widgets.Length (C# array contract), got:\n{cs}"

    def test_dot_count_absent_for_find_objects_local(self):
        cs = _translate_src(self._SRC, unity_version=6)
        assert "widgets.Count" not in cs, \
            f"widgets.Count must be rewritten to .Length:\n{cs}"

    def test_count_rewrite_also_fires_on_unity5(self):
        """FindObjectsOfType also returns T[]; .Count must become .Length on Unity 5."""
        cs = _translate_src(self._SRC, unity_version=5)
        assert "widgets.Length" in cs, \
            f"Unity 5: widgets.Length expected (T[] from FindObjectsOfType):\n{cs}"


# ---------------------------------------------------------------------------
# Scenario 4 — Scene save path branching in generated setup script
# ---------------------------------------------------------------------------

class TestSceneSavePath:
    """generate_scene_script must emit both save branches gated on IsNullOrEmpty."""

    def test_emitted_code_contains_is_null_or_empty_gate(self):
        cs = generate_scene_script(_minimal_scene())
        assert "string.IsNullOrEmpty(_activeScene.path)" in cs, \
            f"IsNullOrEmpty branch gate missing from generated script:\n{cs}"

    def test_emitted_code_contains_save_scene_with_explicit_path(self):
        cs = generate_scene_script(_minimal_scene())
        assert "SaveScene(_activeScene" in cs, \
            f"SaveScene(scene, path) branch missing:\n{cs}"

    def test_emitted_code_contains_save_open_scenes_fallback(self):
        cs = generate_scene_script(_minimal_scene())
        assert "SaveOpenScenes()" in cs, \
            f"SaveOpenScenes() fallback branch missing:\n{cs}"

    def test_save_scene_carries_canonical_path(self):
        """The canonical path must be Assets/_Project/Scenes/Scene.unity."""
        cs = generate_scene_script(_minimal_scene())
        assert "Assets/_Project/Scenes/Scene.unity" in cs, \
            f"Canonical scene path not found in generated script:\n{cs}"


# ---------------------------------------------------------------------------
# Scenario 5 — CreateDirectory must precede SaveScene
# ---------------------------------------------------------------------------

class TestCreateDirectoryPrecedesSaveScene:
    """Directory.CreateDirectory must appear textually before SaveScene on the
    new-scene path, otherwise SaveScene throws UnityException: Could not save."""

    def test_create_directory_before_save_scene(self):
        cs = generate_scene_script(_minimal_scene())
        cd_pos = cs.find("Directory.CreateDirectory(")
        ss_pos = cs.find("SaveScene(_activeScene")
        assert cd_pos != -1, "Directory.CreateDirectory call not found"
        assert ss_pos != -1, "SaveScene call not found"
        assert cd_pos < ss_pos, (
            f"Directory.CreateDirectory (pos {cd_pos}) must appear BEFORE "
            f"SaveScene (pos {ss_pos}) — otherwise SaveScene throws"
        )


# ---------------------------------------------------------------------------
# Scenario 6 — Play-mode guard precedes all scene mutations
# ---------------------------------------------------------------------------

class TestPlayModeGuardPosition:
    """Per Unity contract: EditorSceneManager.NewScene and related APIs throw
    InvalidOperationException when called during Play mode.  The guard must be
    the very first meaningful statement inside Execute(), returning early, so
    no mutation code can run while playing."""

    _MUTATION_TOKENS = [
        "new GameObject(",
        "MarkSceneDirty(",
        "EditorSceneManager.NewScene(",
        "Directory.CreateDirectory(",
    ]

    def _find_after_execute(self, cs: str) -> str:
        """Return the substring of cs starting after 'public static string Execute()'."""
        idx = cs.find("public static string Execute()")
        assert idx != -1, "Execute() method not found in generated script"
        return cs[idx:]

    def test_play_mode_guard_appears_before_scene_mutations(self):
        cs = generate_scene_script(_minimal_scene())
        body = self._find_after_execute(cs)
        guard_pos = body.find("EditorApplication.isPlayingOrWillChangePlaymode")
        assert guard_pos != -1, "Play-mode guard not found in Execute() body"
        for token in self._MUTATION_TOKENS:
            mut_pos = body.find(token)
            if mut_pos != -1:
                assert guard_pos < mut_pos, (
                    f"Guard (pos {guard_pos}) must precede '{token}' (pos {mut_pos})"
                )

    def test_play_mode_guard_uses_early_return(self):
        """Guard must return early — not just set a flag — so downstream code
        cannot execute under any code path in Play mode."""
        cs = generate_scene_script(_minimal_scene())
        body = self._find_after_execute(cs)
        # Find the guard block
        guard_idx = body.find("EditorApplication.isPlayingOrWillChangePlaymode")
        assert guard_idx != -1, "Guard not found"
        # The return statement must appear inside the guard block
        # (i.e. between the guard condition and the first mutation token).
        first_mutation = min(
            (body.find(t) for t in self._MUTATION_TOKENS if body.find(t) != -1),
            default=len(body)
        )
        guard_block = body[guard_idx:first_mutation]
        assert "return " in guard_block, (
            f"No 'return' found inside the guard block — guard does not exit early:\n{guard_block}"
        )


# ---------------------------------------------------------------------------
# Scenario 7 — Guard return value is an identifiable skip marker
# ---------------------------------------------------------------------------

class TestPlayModeGuardSkipMarker:
    """The return string on the guard path must be non-empty and contain 'skip'
    (case-insensitive) so callers can .Contains('skip') on it."""

    def test_guard_return_contains_skip_case_insensitive(self):
        cs = generate_scene_script(_minimal_scene())
        # Find the return statement inside the guard block
        # Pattern: return "..." inside the isPlayingOrWillChangePlaymode branch
        match = re.search(
            r'EditorApplication\.isPlayingOrWillChangePlaymode.*?return\s+"([^"]*)"',
            cs, re.DOTALL
        )
        assert match is not None, \
            "Could not find return string literal inside play-mode guard block"
        return_value = match.group(1)
        assert return_value.strip(), "Guard return value must be non-empty"
        assert "skip" in return_value.lower(), \
            f"Guard return value '{return_value}' does not contain 'skip' (case-insensitive)"


# ---------------------------------------------------------------------------
# Scenario 8 — Validation script uses FindObjectsByType (Unity 6 form)
# ---------------------------------------------------------------------------

class TestValidationScriptUsesUnity6FindObjects:
    """generate_validation_script must emit FindObjectsByType<GameObject>(FindObjectsSortMode.None)
    since it runs under Unity 6 on the home machine (per commit cc9359c)."""

    def test_validation_uses_find_objects_by_type(self):
        cs = generate_validation_script(_minimal_scene())
        assert "FindObjectsByType<GameObject>(FindObjectsSortMode.None)" in cs, \
            f"Validation script must use Unity 6 FindObjectsByType form:\n{cs}"

    def test_validation_does_not_use_find_objects_of_type(self):
        cs = generate_validation_script(_minimal_scene())
        assert "FindObjectsOfType<GameObject>" not in cs, \
            f"Validation script must not use deprecated FindObjectsOfType:\n{cs}"

    def test_validation_uses_dot_length_not_dot_count(self):
        """allGOs is a T[] — must use .Length, not .Count."""
        cs = generate_validation_script(_minimal_scene())
        # Find the local variable assigned from FindObjectsByType
        match = re.search(r'var\s+(\w+)\s*=\s*Object\.FindObjectsByType', cs)
        assert match is not None, "Could not locate FindObjectsByType assignment in validation script"
        local_var = match.group(1)
        assert f"{local_var}.Length" in cs, \
            f"Validation script must use {local_var}.Length (C# array), not .Count:\n{cs}"
        assert f"{local_var}.Count" not in cs, \
            f"Validation script must not use {local_var}.Count:\n{cs}"


# ---------------------------------------------------------------------------
# Scenario 9 — Unity 5 back-compat: FindObjectsOfType still emitted
# ---------------------------------------------------------------------------

class TestUnity5BackCompat:
    """Unity 5 output must use FindObjectsOfType, not FindObjectsByType.
    This guards against a regression that could break the older generated projects."""

    _SRC = textwrap.dedent("""\
        from src.engine.core import MonoBehaviour

        class LegacyManager(MonoBehaviour):
            def start(self):
                items = GameObject.find_objects_of_type(Item)
        """)

    def test_unity5_output_has_find_objects_of_type(self):
        cs = _translate_src(self._SRC, unity_version=5)
        assert "FindObjectsOfType<Item>()" in cs, \
            f"Unity 5 must emit FindObjectsOfType:\n{cs}"

    def test_unity5_output_no_find_objects_by_type(self):
        cs = _translate_src(self._SRC, unity_version=5)
        assert "FindObjectsByType" not in cs, \
            f"Unity 5 must not emit FindObjectsByType:\n{cs}"

    def test_unity5_output_no_find_objects_sort_mode(self):
        cs = _translate_src(self._SRC, unity_version=5)
        assert "FindObjectsSortMode" not in cs, \
            f"FindObjectsSortMode is Unity 6 API — must not appear in Unity 5 output:\n{cs}"


# ---------------------------------------------------------------------------
# Scenario 10 — Mutation: version switch is live at translation time
# ---------------------------------------------------------------------------

class TestVersionSwitchLiveAtTranslationTime:
    """Monkeypatching the config unity_version after one translation must change
    the emitted method name on the next call — proves the switch is not cached."""

    _SRC = textwrap.dedent("""\
        from src.engine.core import MonoBehaviour

        class Probe(MonoBehaviour):
            def update(self):
                all_objs = GameObject.find_objects_of_type(Target)
        """)

    def test_version_switch_changes_emitted_method(self):
        import src.translator.python_to_csharp as _mod

        # First call: Unity 6
        cs_v6 = _translate_src(self._SRC, unity_version=6)
        assert "FindObjectsByType" in cs_v6, "Sanity: v6 should produce FindObjectsByType"

        # Monkeypatch to Unity 5 via the module's _config
        original = _mod._config.unity_version
        try:
            _mod._config.unity_version = 5
            # Re-translate using the patched config directly (same _translate_py_expression path)
            cs_v5 = _translate_src(self._SRC, unity_version=5)
        finally:
            _mod._config.unity_version = original

        assert "FindObjectsOfType" in cs_v5, \
            f"After patching unity_version=5, output must switch to FindObjectsOfType:\n{cs_v5}"
        assert "FindObjectsByType" not in cs_v5, \
            f"FindObjectsByType must disappear when unity_version=5:\n{cs_v5}"

    def test_switching_back_to_v6_restores_new_api(self):
        """After a v5 round, switching back to v6 must restore FindObjectsByType."""
        cs_v5 = _translate_src(self._SRC, unity_version=5)
        cs_v6_again = _translate_src(self._SRC, unity_version=6)
        assert "FindObjectsByType" in cs_v6_again, \
            f"Switching back to v6 must restore FindObjectsByType:\n{cs_v6_again}"
