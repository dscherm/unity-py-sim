"""Contract tests for M-1 Breakout deploy source fixes (commit 45bee20).

Validates three fixes derived from documented Unity behavior:

  Gap B6 — SerializedProperty.intValue vs floatValue dispatch on Python type.
    Unity docs: SerializedProperty.floatValue setter is only valid when
    propertyType == SerializedPropertyType.Float. Calling .floatValue on
    an Integer-typed property throws InvalidOperationException
    ("<X> is not a supported float value") and the assignment is dropped.
    Reference: https://docs.unity3d.com/ScriptReference/SerializedProperty.html

  Gap B5 — Single-mode sprite fallback.
    Unity TextureImporter.spriteImportMode == Single produces a single
    Sprite asset whose name matches the texture file (e.g. "ball"). Mode
    Multiple slices the texture into named sub-sprites (e.g. "ball_0").
    The generator must work for both — try named sub-sprite first then
    fall back to LoadAssetAtPath<Sprite>(path).

  Gap B4 — sprite path convention.
    The project_scaffolder writes textures to Assets/Art/Sprites/. Mapping
    JSONs must point at that path; otherwise AssetDatabase.LoadAllAssetsAtPath
    returns null at runtime.

NOTE: This test file imports from src/ but never reads tests/ files (per
project CLAUDE.md validation-agent rules).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.exporter.coplay_generator import generate_scene_script

REPO_ROOT = Path(__file__).resolve().parents[2]
MAPPINGS_DIR = REPO_ROOT / "data" / "mappings"


# ---------------------------------------------------------------------------
# Gap B6 — int vs float dispatcher
# ---------------------------------------------------------------------------

def _make_monobehaviour_scene(field_name: str, field_value):
    """Minimal scene with one MonoBehaviour carrying a single numeric field."""
    return {
        "game_objects": [
            {
                "name": "TestObj",
                "tag": "Untagged",
                "components": [
                    {
                        "type": "Transform",
                        "position": [0, 0, 0],
                        "local_scale": [1, 1, 1],
                    },
                    {
                        "type": "Brick",
                        "is_monobehaviour": True,
                        "fields": {field_name: field_value},
                    },
                ],
            }
        ],
        "physics": {},
    }


def test_b6_python_int_emits_intValue_no_f_suffix():
    """Python int -> C# .intValue = N (no 'f' suffix).

    Per Unity docs, SerializedProperty.intValue is the correct accessor for
    Integer-typed properties. The 'f' suffix is a C# float literal marker
    and would cause CS0029 (cannot implicitly convert float to int).
    """
    scene = _make_monobehaviour_scene("health", 1)
    cs = generate_scene_script(scene)
    assert "prop_health.intValue = 1;" in cs, (
        f"Expected 'prop_health.intValue = 1;' in generated C#.\n"
        f"--- generated ---\n{cs}\n--- end ---"
    )
    # Negative: must NOT emit floatValue for an int field
    assert "prop_health.floatValue" not in cs, (
        "Regression: int field is being emitted as floatValue (Gap B6)."
    )
    # Negative: must NOT emit 'f' suffix on an int literal
    assert "prop_health.intValue = 1f" not in cs


def test_b6_python_float_emits_floatValue_with_f_suffix():
    """Python float -> C# .floatValue = Nf (with 'f' suffix).

    The 'f' suffix is required to disambiguate the C# literal as float
    rather than double; without it, Unity's overload resolution may bind
    to the wrong setter or fail to compile.
    """
    scene = _make_monobehaviour_scene("speed", 6.0)
    cs = generate_scene_script(scene)
    assert "prop_speed.floatValue = 6.0f;" in cs, (
        f"Expected 'prop_speed.floatValue = 6.0f;' in generated C#.\n"
        f"--- generated ---\n{cs}\n--- end ---"
    )
    assert "prop_speed.intValue" not in cs


def test_b6_python_bool_is_not_treated_as_int():
    """Python bool is a subclass of int but must NOT trigger numeric wiring.

    The generator's filter is `isinstance(fv, (int, float)) and not isinstance(fv, bool)`.
    A True value should be skipped entirely (booleans aren't numeric SerializeFields).
    """
    scene = _make_monobehaviour_scene("enabled", True)
    cs = generate_scene_script(scene)
    assert "prop_enabled" not in cs


def test_b6_zero_value_skipped():
    """Per source filter (`fv != 0`), zero-valued fields aren't wired.

    Justification: the SerializedField default is 0 in Unity, so re-emitting
    it is redundant. This is existing behavior, not part of the fix, but the
    contract relies on it to keep the dispatcher's surface focused.
    """
    scene = _make_monobehaviour_scene("ignored", 0)
    cs = generate_scene_script(scene)
    assert "prop_ignored" not in cs


def test_b6_mixed_int_and_float_fields_dispatched_correctly():
    """A component with both int and float fields gets both dispatchers."""
    scene = {
        "game_objects": [
            {
                "name": "Brick",
                "components": [
                    {
                        "type": "Transform",
                        "position": [0, 0, 0],
                        "local_scale": [1, 1, 1],
                    },
                    {
                        "type": "Brick",
                        "is_monobehaviour": True,
                        "fields": {"points": 100, "decay_rate": 0.95},
                    },
                ],
            }
        ],
        "physics": {},
    }
    cs = generate_scene_script(scene)
    assert "prop_points.intValue = 100;" in cs
    assert "prop_decayRate.floatValue = 0.95f;" in cs


# ---------------------------------------------------------------------------
# Gap B5 — Single-mode sprite fallback
# ---------------------------------------------------------------------------

def test_b5_named_subsprite_has_null_coalescing_fallback():
    """When sprite_name is set, the generator must emit a `??` fallback to
    LoadAssetAtPath<Sprite>(path) for Single-mode imports.

    The C# null-coalescing operator (??) returns the right-hand side when
    the LINQ FirstOrDefault returns null (i.e., no sub-sprite matched the
    expected name) — which is the Single-mode case where the loaded Sprite's
    .name equals the texture name without a "_0" suffix.
    """
    scene = {"game_objects": [], "physics": {}}
    mapping = {
        "sprites": {
            "ball": {
                "unity_path": "Assets/Art/Sprites/ball.png",
                "sprite_name": "ball_0",
                "ppu": 100,
            }
        }
    }
    cs = generate_scene_script(scene, mapping)

    # Expect both the FirstOrDefault attempt AND the LoadAssetAtPath fallback
    assert ".OfType<Sprite>().FirstOrDefault(s => s.name == \"ball_0\")" in cs
    assert "?? AssetDatabase.LoadAssetAtPath<Sprite>(\"Assets/Art/Sprites/ball.png\")" in cs, (
        "Gap B5 regression: missing Single-mode fallback. Expected '??' chained "
        "to LoadAssetAtPath<Sprite>(path).\n"
        f"--- generated ---\n{cs}\n--- end ---"
    )


def test_b5_no_sprite_name_uses_direct_load_no_fallback_needed():
    """When sprite_name is absent, only LoadAssetAtPath<Sprite> is emitted —
    no FirstOrDefault, no `??`. This path was already correct pre-fix."""
    scene = {"game_objects": [], "physics": {}}
    mapping = {
        "sprites": {
            "logo": {"unity_path": "Assets/Art/Sprites/logo.png", "ppu": 100}
        }
    }
    cs = generate_scene_script(scene, mapping)
    assert "var sprite_logo = AssetDatabase.LoadAssetAtPath<Sprite>(\"Assets/Art/Sprites/logo.png\");" in cs
    assert "FirstOrDefault" not in cs.split("LOAD SPRITE ASSETS")[-1].split("CREATE GAMEOBJECTS")[0]


def test_b5_fallback_path_matches_unity_path_exactly():
    """The fallback's path arg must match the original unity_path — same
    string, character-for-character, including escape semantics."""
    scene = {"game_objects": [], "physics": {}}
    weird_path = "Assets/Art/Sprites/With Space/sprite.png"
    mapping = {
        "sprites": {
            "x": {"unity_path": weird_path, "sprite_name": "x_0", "ppu": 100}
        }
    }
    cs = generate_scene_script(scene, mapping)
    expected = f"?? AssetDatabase.LoadAssetAtPath<Sprite>(\"{weird_path}\");"
    assert expected in cs


# ---------------------------------------------------------------------------
# Gap B4 — mapping JSONs use Assets/Art/Sprites/
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "mapping_filename",
    [
        "breakout_mapping.json",
        "space_invaders_mapping.json",
        "angry_birds_mapping.json",
        "flappy_bird_mapping.json",  # was already correct, regression-guard
    ],
)
def test_b4_all_sprite_unity_paths_under_art_sprites(mapping_filename: str):
    """Every sprite's unity_path must start with 'Assets/Art/Sprites/'.

    The project_scaffolder's _DEFAULT_FOLDERS writes textures to
    'Assets/Art/Sprites/'. A mapping pointing at 'Assets/Sprites/' yields
    AssetDatabase.LoadAllAssetsAtPath returning null at runtime, breaking
    every SpriteRenderer assignment.
    """
    mapping_path = MAPPINGS_DIR / mapping_filename
    data = json.loads(mapping_path.read_text(encoding="utf-8"))
    sprites = data.get("sprites", {})
    assert sprites, f"{mapping_filename} has no sprites — sanity check"
    for ref, info in sprites.items():
        unity_path = info.get("unity_path", "")
        assert unity_path.startswith("Assets/Art/Sprites/"), (
            f"{mapping_filename} sprite '{ref}' unity_path='{unity_path}' "
            f"does not start with 'Assets/Art/Sprites/' (Gap B4)."
        )
        # Negative: explicitly forbid the legacy path
        assert not unity_path.startswith("Assets/Sprites/"), (
            f"{mapping_filename} sprite '{ref}' still uses legacy "
            f"'Assets/Sprites/' path (Gap B4)."
        )


def test_b4_breakout_specific_paths():
    """Hard-coded check: breakout's three sprites at the canonical paths."""
    data = json.loads((MAPPINGS_DIR / "breakout_mapping.json").read_text(encoding="utf-8"))
    paths = {ref: info["unity_path"] for ref, info in data["sprites"].items()}
    assert paths == {
        "paddle": "Assets/Art/Sprites/paddle.png",
        "ball": "Assets/Art/Sprites/ball.png",
        "brick": "Assets/Art/Sprites/brick.png",
    }
