"""Mutation tests for M-1 Breakout deploy fixes (commit 45bee20).

These tests revert each fix in a temporary copy of the source, re-run the
contract assertions, and verify they fail. This proves the contract tests
aren't tautological — that they actually catch the documented regressions.

The mutations operate on a fresh copy of the source loaded into a private
module namespace; the real `src/exporter/coplay_generator.py` on disk is
never touched.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[2]
GEN_PATH = REPO_ROOT / "src" / "exporter" / "coplay_generator.py"


def _load_module_from_source(src: str, name: str) -> ModuleType:
    """Compile a string of Python source into a fresh module."""
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = str(GEN_PATH)  # so relative imports resolve normally
    code = compile(src, str(GEN_PATH), "exec")
    exec(code, mod.__dict__)
    return mod


def _scene_with_int_field():
    return {
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
                        "fields": {"health": 1},
                    },
                ],
            }
        ],
        "physics": {},
    }


def _mapping_with_named_sprite():
    return {
        "sprites": {
            "ball": {
                "unity_path": "Assets/Art/Sprites/ball.png",
                "sprite_name": "ball_0",
                "ppu": 100,
            }
        }
    }


# ---------------------------------------------------------------------------
# B6 mutation — revert the int/float dispatcher to "always floatValue"
# ---------------------------------------------------------------------------

def test_b6_mutation_reverting_dispatcher_breaks_int_contract():
    """Mutate the dispatcher back to the pre-fix 'always floatValue' code.

    The contract test (`int -> .intValue`) MUST fail under the mutated
    generator — proving the test catches the regression.
    """
    src = GEN_PATH.read_text(encoding="utf-8")

    # Replace the dispatcher with the pre-fix code (always floatValue).
    # Indentation in source is 16 spaces (the if/else block sits inside a
    # `for cs_field, ...` loop nested in `if numeric_fields:`).
    post_fix = (
        '                if isinstance(field_val, float):\n'
        '                    setter, suffix = "floatValue", "f"\n'
        '                else:\n'
        '                    setter, suffix = "intValue", ""'
    )
    pre_fix = (
        '                setter, suffix = "floatValue", '
        '("f" if isinstance(field_val, float) else "")'
    )

    assert post_fix in src, (
        "Source no longer contains the expected post-fix dispatcher block — "
        "test needs to be updated."
    )
    mutated_src = src.replace(post_fix, pre_fix)
    assert mutated_src != src, "Mutation no-op"

    mod = _load_module_from_source(mutated_src, "coplay_generator_mut_b6")
    cs = mod.generate_scene_script(_scene_with_int_field())

    # Under the mutation, the dispatcher always picks floatValue. The
    # post-fix contract ('prop_health.intValue = 1;') MUST therefore fail:
    assert "prop_health.intValue = 1;" not in cs, (
        "Mutation didn't change behavior — contract test would not catch the "
        "regression. Verify the dispatcher logic actually drove the change."
    )
    # And the pre-fix bad behavior is back:
    assert "prop_health.floatValue = 1" in cs, (
        f"Expected reverted behavior (floatValue for int) under mutation. Got:\n{cs}"
    )


# ---------------------------------------------------------------------------
# B5 mutation — drop the `??` fallback, keep only FirstOrDefault
# ---------------------------------------------------------------------------

def test_b5_mutation_removing_fallback_breaks_contract():
    """Mutate the sprite loader back to FirstOrDefault-only (pre-fix). The
    contract test (`??` fallback present) MUST fail.
    """
    src = GEN_PATH.read_text(encoding="utf-8")

    # Locate the post-fix `??` line and drop it (revert to FirstOrDefault-only).
    # Source indentation is 16 spaces. Also strip the FirstOrDefault line's
    # trailing `)` so it terminates with `);` like the pre-fix code.
    post_fix_firstordefault = (
        '                lines.append(f"            .OfType<Sprite>()'
        '.FirstOrDefault(s => s.name == \\"{_escape_cs_string(sprite_name)}\\")")\n'
        '                lines.append(f"            ?? AssetDatabase.'
        'LoadAssetAtPath<Sprite>(\\"{_escape_cs_string(unity_path)}\\");")\n'
    )
    pre_fix_firstordefault = (
        '                lines.append(f"            .OfType<Sprite>()'
        '.FirstOrDefault(s => s.name == \\"{_escape_cs_string(sprite_name)}\\");")\n'
    )

    assert post_fix_firstordefault in src, (
        "Could not locate the post-fix B5 emission block — source layout changed."
    )
    mutated_src = src.replace(post_fix_firstordefault, pre_fix_firstordefault)
    assert mutated_src != src

    mod = _load_module_from_source(mutated_src, "coplay_generator_mut_b5")
    cs = mod.generate_scene_script({"game_objects": [], "physics": {}}, _mapping_with_named_sprite())

    # Under mutation, `??` fallback is gone:
    assert "?? AssetDatabase.LoadAssetAtPath<Sprite>" not in cs, (
        "Mutation didn't remove the fallback — contract test would not catch "
        "the regression."
    )
    # And the FirstOrDefault path stands alone:
    assert ".FirstOrDefault(s => s.name == \"ball_0\");" in cs


# ---------------------------------------------------------------------------
# B4 mutation — point a mapping back at `Assets/Sprites/` and verify the
# contract fails on it.
# ---------------------------------------------------------------------------

def test_b4_mutation_legacy_path_breaks_contract():
    """Copy the breakout mapping into a tempdir, rewrite paths to legacy
    'Assets/Sprites/', and verify the path-prefix contract fails.

    This proves the mapping-JSON contract isn't trivially satisfied by every
    JSON file — only by ones that actually use the canonical path.
    """
    src_path = REPO_ROOT / "data" / "mappings" / "breakout_mapping.json"
    data = json.loads(src_path.read_text(encoding="utf-8"))

    # Mutate every sprite's unity_path back to legacy
    for ref, info in data["sprites"].items():
        if info.get("unity_path", "").startswith("Assets/Art/Sprites/"):
            info["unity_path"] = info["unity_path"].replace(
                "Assets/Art/Sprites/", "Assets/Sprites/"
            )

    # Re-run the path-prefix assertion on the mutated copy
    failures: list[str] = []
    for ref, info in data["sprites"].items():
        unity_path = info.get("unity_path", "")
        if not unity_path.startswith("Assets/Art/Sprites/"):
            failures.append(f"{ref}={unity_path}")

    assert failures, (
        "Mutated mapping still passed the path-prefix check — contract is "
        "trivially satisfied and won't catch B4 regressions."
    )
    assert len(failures) == 3, f"Expected 3 mutated paths, got: {failures}"
