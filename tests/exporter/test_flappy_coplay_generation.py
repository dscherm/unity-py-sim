"""Integration test for Flappy Bird CoPlay script generation (plan Task 7).

Exercises tools/gen_flappy_coplay.py end-to-end:
  setup_scene -> scene_serializer.serialize_scene -> coplay_generator
  -> GeneratedSceneSetup.cs + GeneratedSceneValidation.cs.

Asserts the output script references the right assets, tags, prefab, and
UI elements called out by plan.md Flappy Task 7.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_generator(tmp_path: Path, namespace: str | None = None) -> tuple[str, str, dict]:
    out_cs = tmp_path / "GeneratedSceneSetup.cs"
    out_val = tmp_path / "GeneratedSceneValidation.cs"
    out_scene = tmp_path / "flappy_scene.json"
    cmd = [sys.executable, str(REPO_ROOT / "tools" / "gen_flappy_coplay.py"),
           "--output", str(out_cs),
           "--validation-output", str(out_val),
           "--scene-json", str(out_scene)]
    if namespace is not None:
        cmd += ["--namespace", namespace]
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, f"generator failed: {proc.stderr}"
    return (
        out_cs.read_text(encoding="utf-8"),
        out_val.read_text(encoding="utf-8"),
        json.loads(out_scene.read_text(encoding="utf-8")),
    )


def test_generator_exits_cleanly_and_produces_scripts(tmp_path):
    setup_cs, val_cs, scene = _run_generator(tmp_path)
    assert "class GeneratedSceneSetup" in setup_cs
    assert "class GeneratedSceneValidation" in val_cs
    assert len(scene.get("game_objects", [])) > 0


def test_generated_script_loads_original_sprites_not_colored_rects(tmp_path):
    setup_cs, _, _ = _run_generator(tmp_path)
    # Bird animation frames from flappy_bird_mapping.json must be loaded
    assert "Bird_01.png" in setup_cs
    assert "Bird_02.png" in setup_cs
    assert "Bird_03.png" in setup_cs
    # Background + Ground + Pipe sprites
    assert "Background.png" in setup_cs
    assert "Ground.png" in setup_cs
    assert "Pipe.png" in setup_cs


def test_generated_script_creates_main_camera(tmp_path):
    setup_cs, _, _ = _run_generator(tmp_path)
    # S4-3/S7-2 fallback: find-or-create Main Camera
    assert "Camera.main" in setup_cs or "MainCamera" in setup_cs


def test_generated_script_assigns_obstacle_and_scoring_tags(tmp_path):
    setup_cs, _, _ = _run_generator(tmp_path)
    assert '"Obstacle"' in setup_cs
    assert '"Scoring"' in setup_cs
    # Registered into TagManager.asset
    assert "_EnsureTag" in setup_cs


def test_generated_script_wires_sprite_renderers(tmp_path):
    setup_cs, _, _ = _run_generator(tmp_path)
    # SpriteRenderer components must actually receive a sprite assignment
    assert "AddComponent<SpriteRenderer>" in setup_cs
    assert ".sprite = sprite_" in setup_cs


def test_validation_script_checks_gameobjects(tmp_path):
    _, val_cs, scene = _run_generator(tmp_path)
    # Validation must know the expected count
    assert str(len(scene["game_objects"])) in val_cs
    # FU-4 FindObjectsByType migration: Unity 6 deprecated FindObjectsOfType
    # (CS0618) in favour of FindObjectsByType which requires an explicit sort
    # mode. The validation script must use the non-deprecated form.
    assert "FindObjectsByType<GameObject>(FindObjectsSortMode.None)" in val_cs
    assert "FindObjectsOfType<GameObject>" not in val_cs
    # PASS/FAIL marker from S5-3
    assert "PASS" in val_cs and "FAIL" in val_cs


def test_generator_emits_using_directive_for_default_namespace(tmp_path):
    # Translator now wraps every Flappy Bird MonoBehaviour in
    # `namespace FlappyBird { ... }` (per src/translator/project_translator.py
    # GAME_NAMESPACES), so the generator must emit `using FlappyBird;`
    # at the top of both editor scripts to satisfy bare type references
    # in the generated GetComponent<T>() / AddComponent<T>() calls.
    # See tests/exporter/test_coplay_namespace_emission.py for the
    # hardened contract — this is the smoke check against the
    # default-flag invocation only.
    setup_cs, val_cs, _ = _run_generator(tmp_path)
    assert "using FlappyBird;" in setup_cs
    assert "using FlappyBird;" in val_cs


def test_generator_honors_explicit_namespace(tmp_path):
    # When callers do wrap translated scripts in a namespace, the generator
    # must emit the prefix for MonoBehaviour GetComponent/AddComponent calls.
    setup_cs, val_cs, _ = _run_generator(tmp_path, namespace="MyGame")
    assert "MyGame.Player" in setup_cs or "MyGame.Player" in val_cs
    # And the matching `using` directive must be declared so the bare
    # class refs in `_p.objectReferenceValue.name` checks resolve.
    assert "using MyGame;" in setup_cs
    assert "using MyGame;" in val_cs
