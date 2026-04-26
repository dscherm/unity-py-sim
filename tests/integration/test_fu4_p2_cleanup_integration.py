"""FU-4 P2 cleanup trio integration tests.

Covers the three P2 follow-ups from
`.ralph/bridge-state.json::completion.follow_ups`
(originally flagged in `data/lessons/coplay_generator_gaps.md`):

1. ``FindObjectsOfType<T>()`` → ``FindObjectsByType<T>(FindObjectsSortMode.None)``
   for Unity 6 targets — the deprecated form fires CS0618.
2. Scene-save-path correction — the generator must save the scene at the
   canonical ``Assets/_Project/Scenes/Scene.unity`` path rather than letting
   Unity save wherever the active scene happens to live.
3. ``EditorSceneManager.NewScene`` editor-only guard — running the
   scene-setup script while Unity is in Play mode throws
   ``InvalidOperationException``; the setup must refuse to run instead.

These tests exercise behaviour through the generator + translator entry
points (not implementation internals) so they stay honest if the
realization of each fix moves.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from src.exporter.coplay_generator import (
    generate_scene_script,
    generate_validation_script,
)
from src.translator.python_parser import parse_python_file
from src.translator.python_to_csharp import translate


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _minimal_scene() -> dict:
    """Smallest scene payload the generator accepts — a single GameObject
    with a camera and a single child GameObject so the validation path runs."""
    return {
        "game_objects": [
            {
                "name": "MainCamera",
                "tag": "MainCamera",
                "layer": 0,
                "components": [
                    {
                        "type": "Camera",
                        "orthographic": True,
                        "orthographic_size": 5.0,
                    },
                ],
            },
            {
                "name": "Player",
                "tag": "Untagged",
                "layer": 0,
                "components": [
                    {"type": "SpriteRenderer"},
                ],
            },
        ],
        "physics": {"layers": {}, "ignore_collision_pairs": []},
    }


def _translate_src(py_source: str, *, unity_version: int = 6) -> str:
    """Translate an in-memory Python source snippet; return C#."""
    tmp = Path("_fu4_probe.py")
    tmp.write_text(textwrap.dedent(py_source), encoding="utf-8")
    try:
        parsed = parse_python_file(tmp)
        return translate(parsed, unity_version=unity_version)
    finally:
        tmp.unlink(missing_ok=True)


# --------------------------------------------------------------------------
# Item 1: FindObjectsByType migration for Unity 6
# --------------------------------------------------------------------------


def test_unity6_translates_find_objects_of_type_to_by_type() -> None:
    """`GameObject.find_objects_of_type(T)` → `FindObjectsByType<T>(FindObjectsSortMode.None)`
    when targeting Unity 6. The deprecated form fires CS0618."""
    py = """
        from src.engine.core import MonoBehaviour, GameObject

        class Mgr(MonoBehaviour):
            def play(self) -> None:
                pipes = GameObject.find_objects_of_type(Pipes)
                for i in range(len(pipes)):
                    pass
    """
    cs = _translate_src(py, unity_version=6)

    assert "FindObjectsByType<Pipes>(FindObjectsSortMode.None)" in cs, (
        f"Unity 6 must emit the non-deprecated form; got:\n{cs}"
    )
    assert "FindObjectsOfType<Pipes>" not in cs, (
        f"Deprecated FindObjectsOfType must not appear in Unity 6 output:\n{cs}"
    )


def test_unity5_keeps_find_objects_of_type() -> None:
    """Unity 5 predates FindObjectsByType / FindObjectsSortMode — the legacy
    form must still be emitted there so the translator stays compatible with
    both project generations."""
    py = """
        from src.engine.core import MonoBehaviour, GameObject

        class Mgr(MonoBehaviour):
            def play(self) -> None:
                pipes = GameObject.find_objects_of_type(Pipes)
    """
    cs = _translate_src(py, unity_version=5)

    assert "FindObjectsOfType<Pipes>()" in cs, (
        f"Unity 5 target must keep FindObjectsOfType<T>():\n{cs}"
    )
    assert "FindObjectsByType" not in cs, (
        f"FindObjectsByType is Unity 6+; must not appear in Unity 5 output:\n{cs}"
    )


def test_unity6_length_rewrite_still_fires_on_by_type() -> None:
    """The existing `.Count` → `.Length` post-pass was regex-anchored to
    `FindObjectsOfType<`. After the FU-4 migration it must also match the new
    `FindObjectsByType<` form — otherwise the Unity-6 code regresses to
    `pipes.Count` (CS1061, `T[]` has no Count member)."""
    py = """
        from src.engine.core import MonoBehaviour, GameObject

        class Mgr(MonoBehaviour):
            def play(self) -> None:
                pipes = GameObject.find_objects_of_type(Pipes)
                n = len(pipes)
    """
    cs = _translate_src(py, unity_version=6)

    assert "pipes.Length" in cs, (
        f"len(pipes) on a FindObjectsByType result must become pipes.Length:\n{cs}"
    )
    assert "pipes.Count" not in cs, (
        f"T[] arrays expose .Length only — .Count is CS1061:\n{cs}"
    )


def test_validation_script_uses_find_objects_by_type() -> None:
    """CoPlay's GeneratedSceneValidation.cs must also emit the Unity 6 form —
    it's committed under ``Assets/Editor/`` and runs on the home machine
    which builds against Unity 6 DLLs (commit cc9359c)."""
    val_cs = generate_validation_script(_minimal_scene())

    assert (
        "FindObjectsByType<GameObject>(FindObjectsSortMode.None)" in val_cs
    ), f"Validation script must use Unity 6 FindObjectsByType:\n{val_cs}"
    assert "FindObjectsOfType<GameObject>" not in val_cs, (
        f"Deprecated call must not survive in the validation script:\n{val_cs}"
    )


# --------------------------------------------------------------------------
# Item 2: Scene-save-path correction
# --------------------------------------------------------------------------


def test_setup_script_saves_scene_to_project_scenes_path() -> None:
    """The setup script must emit the canonical scene path so CoPlay's
    ``save_scene`` / EditorSceneManager calls don't silently drop the
    scene file at ``Assets/`` root."""
    setup_cs = generate_scene_script(_minimal_scene(), mapping_data=None)

    assert '"Assets/_Project/Scenes/Scene.unity"' in setup_cs, (
        f"Setup script must name the canonical scene path explicitly:\n{setup_cs}"
    )
    assert "SaveScene" in setup_cs, (
        f"Setup script must call SaveScene(scene, path) — SaveOpenScenes "
        f"alone can save to the wrong directory when the active scene has no "
        f"path:\n{setup_cs}"
    )


def test_setup_script_preserves_active_scene_path_when_present() -> None:
    """When Unity already has the scene saved at a real path, the explicit
    SaveScene must be skipped so existing project structures aren't moved
    out from under the user."""
    setup_cs = generate_scene_script(_minimal_scene(), mapping_data=None)

    # Branching: empty active-scene path → SaveScene(scene, explicit path)
    # Non-empty → SaveOpenScenes() (preserves the existing location).
    assert "string.IsNullOrEmpty(_activeScene.path)" in setup_cs, (
        f"Setup script must branch on whether the active scene already has a "
        f"path — unconditionally calling SaveScene clobbers user-saved "
        f"scenes.\n{setup_cs}"
    )
    assert "SaveOpenScenes" in setup_cs, (
        f"The non-empty-path branch must fall back to SaveOpenScenes:\n{setup_cs}"
    )


def test_setup_script_creates_scenes_directory_before_save() -> None:
    """SaveScene(path) requires the parent directory to exist — otherwise
    Unity throws UnityException: Could not save. The setup must mkdir -p
    the Scenes dir before calling SaveScene."""
    setup_cs = generate_scene_script(_minimal_scene(), mapping_data=None)

    # Directory.CreateDirectory is idempotent when the dir exists, so it's
    # safe to always call.
    assert "Directory.CreateDirectory" in setup_cs, (
        f"Setup script must ensure Assets/_Project/Scenes exists before "
        f"SaveScene:\n{setup_cs}"
    )
    assert "Assets/_Project/Scenes" in setup_cs


# --------------------------------------------------------------------------
# Item 3: EditorSceneManager.NewScene play-mode guard
# --------------------------------------------------------------------------


def test_setup_script_refuses_to_run_in_play_mode() -> None:
    """Running the setup script while the editor is in Play mode throws
    InvalidOperationException on EditorSceneManager.NewScene. The setup
    must bail with a readable message before touching scene state."""
    setup_cs = generate_scene_script(_minimal_scene(), mapping_data=None)

    assert "EditorApplication.isPlaying" in setup_cs, (
        f"Setup script must check EditorApplication.isPlaying to refuse "
        f"running mid-play:\n{setup_cs}"
    )
    # Either property — isPlayingOrWillChangePlaymode is the strict form
    # (also catches the moment right before Play mode starts).
    assert (
        "isPlayingOrWillChangePlaymode" in setup_cs
        or "isPlaying" in setup_cs
    )


def test_play_mode_guard_fires_before_scene_mutation() -> None:
    """The guard must be the FIRST control-flow gate in Execute — if scene
    mutation happens before the check, the setup has already corrupted
    state when it realizes Play mode is active."""
    setup_cs = generate_scene_script(_minimal_scene(), mapping_data=None)

    # Locate the Execute() method and the first scene-mutation call.
    execute_start = setup_cs.index("public static string Execute()")
    guard_pos = setup_cs.index("EditorApplication.isPlaying", execute_start)

    # A scene-mutation marker: the first concrete mutation call site.
    # Deliberately excludes string tokens the implementation may mention in
    # comments (e.g. `EditorSceneManager.NewScene` which describes the
    # motivation for the guard) — only code that actually mutates scene
    # state counts.
    mutation_markers = [
        "new GameObject(",
        "MarkSceneDirty",
        "Directory.CreateDirectory",
    ]
    first_mutation = min(
        (setup_cs.index(m, execute_start) for m in mutation_markers if m in setup_cs[execute_start:]),
        default=-1,
    )

    assert first_mutation > guard_pos, (
        f"Play-mode guard at offset {guard_pos} must precede the first "
        f"scene mutation at offset {first_mutation}:\n{setup_cs[execute_start:execute_start + 2000]}"
    )


def test_play_mode_guard_returns_skipped_marker() -> None:
    """The return value when the guard fires must be an identifiable skip
    marker so CoPlay callers can distinguish 'bailed safely' from 'scene
    setup failed'. Callers grep the return string — a generic empty string
    or exception would look like a crash."""
    setup_cs = generate_scene_script(_minimal_scene(), mapping_data=None)

    assert "skipped" in setup_cs.lower(), (
        f"Play-mode guard must return a readable 'skipped' marker:\n{setup_cs}"
    )


# --------------------------------------------------------------------------
# Cross-cutting: all three fixes survive namespace wrapping
# --------------------------------------------------------------------------


def test_all_three_fixes_survive_namespace_kwarg() -> None:
    """Passing ``namespace="FlappyBird"`` must not regress any of the three
    fixes — they all live in the Execute() body, not in the namespace
    wrapper."""
    setup_cs = generate_scene_script(
        _minimal_scene(), mapping_data=None, namespace="FlappyBird",
    )

    assert "EditorApplication.isPlaying" in setup_cs
    assert '"Assets/_Project/Scenes/Scene.unity"' in setup_cs
    assert "SaveScene" in setup_cs
