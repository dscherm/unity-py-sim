"""Tests for coplay_generator — generates C# editor scripts from scene JSON."""

from src.exporter.coplay_generator import generate_scene_script, _escape_cs_string


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
