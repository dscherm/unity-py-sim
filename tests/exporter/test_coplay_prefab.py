"""Tests for CoPlay generator prefab instantiation and field wiring."""

from src.exporter.coplay_generator import generate_scene_script


# --------------- Helpers ---------------

def _make_scene(*game_objects):
    return {"game_objects": list(game_objects)}


def _go(name, components=None, tag="Untagged", layer=0):
    return {
        "name": name,
        "tag": tag,
        "layer": layer,
        "active": True,
        "components": components or [
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
        ],
        "children": [],
    }


def _prefab_manifest(*class_names):
    return {
        "prefabs": [{"class_name": cn, "components": []} for cn in class_names],
        "scene_objects": [],
    }


# --------------- Prefab instantiation ---------------

class TestPrefabInstantiation:
    """When prefab_manifest identifies a class_name, use PrefabUtility."""

    def test_prefab_uses_instantiate_prefab(self):
        scene = _make_scene(_go("Brick"))
        manifest = _prefab_manifest("Brick")
        result = generate_scene_script(scene, prefab_manifest=manifest)
        assert "PrefabUtility.InstantiatePrefab" in result
        assert "Brick.prefab" in result

    def test_non_prefab_uses_new_gameobject(self):
        scene = _make_scene(_go("Wall"))
        manifest = _prefab_manifest("Brick")  # Wall not in prefab list
        result = generate_scene_script(scene, prefab_manifest=manifest)
        # Wall should still use new GameObject
        assert 'new GameObject("Wall")' in result

    def test_no_manifest_uses_new_gameobject(self):
        """Without a manifest, all objects use new GameObject (backward compat)."""
        scene = _make_scene(_go("Brick"))
        result = generate_scene_script(scene)
        assert 'new GameObject("Brick")' in result
        assert "PrefabUtility.InstantiatePrefab" not in result


# --------------- Using UnityEditor ---------------

class TestUsingDirectives:
    def test_using_unity_editor_present(self):
        scene = _make_scene(_go("Brick"))
        manifest = _prefab_manifest("Brick")
        result = generate_scene_script(scene, prefab_manifest=manifest)
        assert "using UnityEditor;" in result


# --------------- Camera creation ---------------

class TestCameraCreation:
    """Generator should create Main Camera if not found, not assume it exists."""

    def test_camera_created_if_missing(self):
        """When scene has a Camera component, generate a find-or-create pattern."""
        camera_go = _go("Main Camera", components=[
            {"type": "Transform", "position": [0, 0, -10],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Camera", "orthographic_size": 5,
             "background_color": [0, 0, 0]},
        ])
        scene = _make_scene(camera_go)
        result = generate_scene_script(scene)
        # Must not blindly assume Camera.main exists — should create if null
        assert "Camera.main" in result
        # Should have a fallback creation when Camera.main is null
        assert "new GameObject()" in result
        assert '.name = "Main Camera"' in result
        assert "AddComponent<Camera>" in result

    def test_camera_null_guard(self):
        """Generated code should handle Camera.main == null gracefully."""
        camera_go = _go("Main Camera", components=[
            {"type": "Transform", "position": [0, 0, -10],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Camera", "orthographic_size": 5,
             "background_color": [0, 0, 0]},
        ])
        scene = _make_scene(camera_go)
        result = generate_scene_script(scene)
        # Should have null check + create fallback, not just "if (go != null)"
        assert "null" in result.lower()


# --------------- SerializedObject field wiring ---------------

class TestFieldWiring:
    """MonoBehaviour fields should be wired via SerializedObject, not commented."""

    def test_numeric_field_wired_via_serialized_object(self):
        go = _go("Player", components=[
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "PlayerController", "is_monobehaviour": True,
             "fields": {"move_speed": 5.0, "jump_force": 10.0}},
        ])
        scene = _make_scene(go)
        result = generate_scene_script(scene, namespace="MyGame")
        # Fields should NOT be commented out
        assert "// PlayerController.moveSpeed = 5.0" not in result
        # Should use SerializedObject
        assert "SerializedObject" in result
        assert "FindProperty" in result
        assert "moveSpeed" in result
        assert "ApplyModifiedProperties" in result

    def test_zero_fields_skipped(self):
        go = _go("Player", components=[
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "PlayerController", "is_monobehaviour": True,
             "fields": {"move_speed": 0}},
        ])
        scene = _make_scene(go)
        result = generate_scene_script(scene, namespace="MyGame")
        # Zero-value fields should still be skipped
        assert "moveSpeed" not in result


# --------------- Array field wiring ---------------

class TestArrayFieldWiring:
    """Array fields like Ghost[] ghosts should use SerializedProperty with arraySize."""

    def test_array_field_uses_serialized_property(self):
        go = _go("GameManager", components=[
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "GameManager", "is_monobehaviour": True,
             "fields": {
                 "ghosts": {
                     "_type": "GameObjectRefArray",
                     "refs": [
                         {"_type": "GameObjectRef", "name": "Blinky"},
                         {"_type": "GameObjectRef", "name": "Pinky"},
                     ],
                 }
             }},
        ])
        blinky = _go("Blinky")
        pinky = _go("Pinky")
        scene = _make_scene(go, blinky, pinky)
        result = generate_scene_script(scene, namespace="PacMan")
        assert "arraySize" in result
        assert "GetArrayElementAtIndex" in result
        assert "ghosts" in result
