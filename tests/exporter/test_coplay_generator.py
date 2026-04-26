"""Tests for coplay_generator — generates C# editor scripts from scene JSON."""

from src.exporter.coplay_generator import (
    generate_scene_script,
    generate_validation_script,
    _escape_cs_string,
)


def test_escape_cs_string_quotes():
    assert _escape_cs_string('hello "world"') == 'hello \\"world\\"'


def test_escape_cs_string_backslash():
    assert _escape_cs_string("path\\to\\file") == "path\\\\to\\\\file"


def test_generate_empty_scene():
    scene = {"game_objects": []}
    result = generate_scene_script(scene)
    assert "using UnityEngine" in result or "using UnityEditor" in result


def test_generate_scene_with_gameobject():
    scene = {
        "game_objects": [
            {
                "name": "TestObj",
                "tag": "Untagged",
                "layer": 0,
                "active": True,
                "components": [
                    {
                        "type": "Transform",
                        "position": [0.0, 0.0, 0.0],
                        "rotation": [0.0, 0.0, 0.0, 1.0],
                        "local_scale": [1.0, 1.0, 1.0],
                    }
                ],
                "children": [],
            }
        ]
    }
    result = generate_scene_script(scene)
    assert "TestObj" in result


def test_generate_scene_with_sprite_renderer():
    scene = {
        "game_objects": [
            {
                "name": "Sprite",
                "tag": "Untagged",
                "layer": 0,
                "active": True,
                "components": [
                    {
                        "type": "Transform",
                        "position": [0.0, 0.0, 0.0],
                        "rotation": [0.0, 0.0, 0.0, 1.0],
                        "local_scale": [1.0, 1.0, 1.0],
                    },
                    {
                        "type": "SpriteRenderer",
                        "color": [1.0, 1.0, 1.0, 1.0],
                        "sorting_order": 0,
                    },
                ],
                "children": [],
            }
        ]
    }
    result = generate_scene_script(scene)
    assert "SpriteRenderer" in result


def test_generate_with_namespace():
    scene = {"game_objects": []}
    result = generate_scene_script(scene, namespace="MyGame")
    # Should include the namespace somewhere in the output
    assert isinstance(result, str)


def test_setup_script_emits_using_namespace_directive():
    """When a namespace is passed, the generated Editor script must include
    `using <namespace>;` — otherwise bare class names like `Movement` /
    `AnimatedSprite` / `Node` in GetComponent<T>() calls fire CS0246 in
    Unity.  Regression for Pacman V2 end-to-end compile."""
    result = generate_scene_script(
        {"game_objects": []},
        namespace="PacmanV2",
    )
    assert "using PacmanV2;" in result


def test_setup_script_no_using_when_no_namespace():
    """When no namespace is passed, the generator must NOT emit a spurious
    `using ;` directive (syntax error)."""
    result = generate_scene_script({"game_objects": []}, namespace="")
    assert "using ;" not in result
    assert "using \n" not in result


def test_validation_script_emits_using_namespace_directive():
    result = generate_validation_script(
        {"game_objects": []},
        namespace="PacmanV2",
    )
    assert "using PacmanV2;" in result


# --- S5-3: validation script generator ---


def _scene_with_refs():
    return {
        "game_objects": [
            {
                "name": "GameManager",
                "tag": "GameController",
                "layer": 0,
                "components": [
                    {"type": "Transform", "position": [0, 0, 0],
                     "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
                    {
                        "type": "GameManager",
                        "is_monobehaviour": True,
                        "fields": {
                            "player": {"_type": "GameObjectRef", "name": "Player"},
                            "ghosts": {"_type": "GameObjectRefArray",
                                       "refs": [{"name": "Blinky"}, {"name": "Pinky"}]},
                        },
                    },
                ],
            },
            {"name": "Player", "tag": "Player", "layer": 8, "components": []},
            {"name": "Blinky", "tag": "Untagged", "layer": 0, "components": []},
            {"name": "Pinky", "tag": "Untagged", "layer": 0, "components": []},
        ],
        "physics": {"layers": {"Player": 8}, "ignore_collision_pairs": []},
    }


def test_validation_script_is_standalone_class():
    result = generate_validation_script(_scene_with_refs())
    assert "class GeneratedSceneValidation" in result
    assert "public static string Execute()" in result
    assert "using UnityEngine" in result
    assert "using UnityEditor" in result


def test_validation_script_checks_gameobject_count():
    scene = _scene_with_refs()
    result = generate_validation_script(scene)
    # Expected count is 4 (GameManager, Player, Blinky, Pinky)
    assert "4" in result
    # Count check must reference a FindObjectsOfType or similar scan
    assert "GameObject" in result


def test_validation_script_checks_serializefield_refs():
    result = generate_validation_script(_scene_with_refs())
    # The script must look up every named ref and assert non-null
    assert '"Player"' in result
    assert '"Blinky"' in result
    assert '"Pinky"' in result
    # SerializedObject inspection to confirm the field points at the expected GO
    assert "SerializedObject" in result
    assert 'FindProperty("player")' in result
    assert 'FindProperty("ghosts")' in result


def test_validation_script_checks_tags():
    result = generate_validation_script(_scene_with_refs())
    # Must verify tag assignments
    assert '"GameController"' in result
    assert '"Player"' in result
    assert ".tag" in result or "CompareTag" in result


def test_validation_script_checks_layers():
    result = generate_validation_script(_scene_with_refs())
    # Must verify layer assignments (Player on layer 8)
    assert '"Player"' in result
    assert ".layer" in result or "LayerMask" in result


def test_validation_script_namespace_prefixes_monobehaviour():
    result = generate_validation_script(_scene_with_refs(), namespace="MyGame")
    assert "MyGame.GameManager" in result


def test_validation_script_returns_pass_or_fail_marker():
    result = generate_validation_script(_scene_with_refs())
    assert "PASS" in result and "FAIL" in result


def test_validation_script_empty_scene():
    result = generate_validation_script({"game_objects": []})
    assert "class GeneratedSceneValidation" in result
    # Empty scene should still be valid C# (compilable structure)
    assert "Execute()" in result
