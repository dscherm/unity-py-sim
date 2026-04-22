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


# --------------- Parent/child wiring (gap 6 regression) ---------------

class TestParentChildWiring:
    """Transform.parent round-tripped from scene serializer must emit SetParent calls.

    Regression for data/lessons/coplay_generator_gaps.md gap 6 (fixed in 2a72917,
    no test previously).  If this test disappears, the Pipes prefab's Top/Bottom/
    Scoring children will silently stop scrolling with the Pipes parent.
    """

    def test_child_emits_setparent_when_transform_has_parent(self):
        parent_go = _go("pipes")
        child_go = _go("Top", components=[
            {"type": "Transform", "position": [0, 2, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1],
             "parent": "pipes"},
        ])
        scene = _make_scene(parent_go, child_go)
        result = generate_scene_script(scene)
        assert "go_Top.transform.SetParent(go_pipes.transform, false);" in result

    def test_multiple_children_each_setparent(self):
        parent_go = _go("pipes")
        children = [
            _go(name, components=[
                {"type": "Transform", "position": [0, 0, 0],
                 "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1],
                 "parent": "pipes"},
            ])
            for name in ("Top", "Bottom", "Scoring")
        ]
        scene = _make_scene(parent_go, *children)
        result = generate_scene_script(scene)
        assert "go_Top.transform.SetParent(go_pipes.transform, false);" in result
        assert "go_Bottom.transform.SetParent(go_pipes.transform, false);" in result
        assert "go_Scoring.transform.SetParent(go_pipes.transform, false);" in result

    def test_no_parent_no_setparent(self):
        lone = _go("Orphan", components=[
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
        ])
        scene = _make_scene(lone)
        result = generate_scene_script(scene)
        assert "SetParent" not in result


# --------------- Camera orthographic flag + z=-10 (gap 7 regression) ---------------

class TestCameraOrthographic:
    """Camera with orthographic_size must emit orthographic=true + z<=-10.

    Regression for data/lessons/coplay_generator_gaps.md gap 7 (fixed in 2a72917).
    Without orthographic=true, Unity uses a perspective camera and 2D sprites at
    z=0 render as background color only.  Without z=-10, sprites at z=0 aren't in
    front of the camera.
    """

    def test_orthographic_flag_emitted_when_orthographic_size_set(self):
        camera_go = _go("Main Camera", components=[
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Camera", "orthographic_size": 5,
             "background_color": [0, 0, 0]},
        ])
        scene = _make_scene(camera_go)
        result = generate_scene_script(scene)
        assert "cam.orthographic = true;" in result
        assert "cam.orthographicSize = 5f;" in result

    def test_camera_z_bumped_to_minus_10_when_source_z_zero(self):
        camera_go = _go("Main Camera", components=[
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Camera", "orthographic_size": 5,
             "background_color": [0, 0, 0]},
        ])
        scene = _make_scene(camera_go)
        result = generate_scene_script(scene)
        assert "new Vector3(0f, 0f, -10f);" in result

    def test_camera_z_preserved_when_source_z_nonzero(self):
        camera_go = _go("Main Camera", components=[
            {"type": "Transform", "position": [0, 0, -5],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Camera", "orthographic_size": 5,
             "background_color": [0, 0, 0]},
        ])
        scene = _make_scene(camera_go)
        result = generate_scene_script(scene)
        assert "new Vector3(0f, 0f, -5f);" in result
        # No auto-bump override
        assert "new Vector3(0f, 0f, -10f);" not in result

    def test_no_orthographic_flag_when_orthographic_size_absent(self):
        """Regression: don't emit orthographic=true for plain (non-ortho) cameras."""
        camera_go = _go("Main Camera", components=[
            {"type": "Transform", "position": [0, 0, -10],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Camera", "background_color": [0, 0, 0]},
        ])
        scene = _make_scene(camera_go)
        result = generate_scene_script(scene)
        assert "cam.orthographic = true;" not in result
