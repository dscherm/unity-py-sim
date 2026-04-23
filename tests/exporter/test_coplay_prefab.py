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

    def test_aspect_lock_attached_to_orthographic_camera(self):
        """Gap 5: orthographic cameras get AspectLock auto-attached so the
        viewport letterboxes to the game's intended aspect."""
        camera_go = _go("Main Camera", components=[
            {"type": "Transform", "position": [0, 0, -10],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Camera", "orthographic_size": 5,
             "background_color": [0, 0, 0]},
        ])
        scene = _make_scene(camera_go)
        result = generate_scene_script(scene)
        assert "AddComponent<AspectLock>()" in result
        # Idempotency guard so re-running Setup doesn't stack duplicates.
        assert "GetComponent<AspectLock>() == null" in result

    def test_aspect_lock_not_attached_to_perspective_camera(self):
        """Only 2D / orthographic scenes need AspectLock; perspective
        cameras handle aspect natively via FOV."""
        camera_go = _go("Main Camera", components=[
            {"type": "Transform", "position": [0, 0, -10],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Camera", "background_color": [0, 0, 0]},  # no orthographic_size
        ])
        scene = _make_scene(camera_go)
        result = generate_scene_script(scene)
        assert "AspectLock" not in result


# --------------- Prefab-asset SerializeField refs (Flappy Bird deploy lesson) ---------------

class TestPrefabAssetSerializeFieldRef:
    """When a MonoBehaviour field's GameObjectRef target matches a prefab class,
    the generator must wire the field to the prefab *asset* on disk, not to the
    scene GameObject of the same name.

    Motivation: GameManager.Play() destroys all Pipes instances at round-start
    for cleanup.  If Spawner.prefab points to the scene-object "Pipes", that
    destroy loop nukes the template and Instantiate(null) stops spawning.
    A prefab-asset reference survives because the asset is an on-disk resource.
    """

    def test_ref_to_prefab_class_loads_prefab_asset(self):
        spawner = _go("Spawner", components=[
            {"type": "Transform", "position": [8, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Spawner", "is_monobehaviour": True,
             "fields": {"prefab": {"_type": "GameObjectRef", "name": "Pipes"}}},
        ])
        pipes = _go("Pipes")  # Scene object with the same name
        scene = _make_scene(spawner, pipes)
        manifest = _prefab_manifest("Pipes")
        result = generate_scene_script(scene, prefab_manifest=manifest)
        # Must load the asset, not reference the scene object
        assert 'AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Project/Prefabs/Pipes.prefab")' in result
        # Must NOT wire the scene-object reference for this field
        assert "prop.objectReferenceValue = go_Pipes;" not in result

    def test_ref_to_prefab_dynamic_instance_name_still_resolves(self):
        """`Pipes(Clone)` / `Pipes_0` style names are prefab instances;
        prefix match should still wire the prefab asset."""
        spawner = _go("Spawner", components=[
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Spawner", "is_monobehaviour": True,
             "fields": {"prefab": {"_type": "GameObjectRef", "name": "Pipes_0"}}},
        ])
        scene = _make_scene(spawner)
        manifest = _prefab_manifest("Pipes")
        result = generate_scene_script(scene, prefab_manifest=manifest)
        assert 'AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Project/Prefabs/Pipes.prefab")' in result

    def test_ref_to_non_prefab_still_uses_scene_object(self):
        """Cross-GameObject SerializeField for non-prefab classes (e.g. the
        GameManager singleton) must still wire the scene reference."""
        player = _go("Player", components=[
            {"type": "Transform", "position": [-2, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Player", "is_monobehaviour": True,
             "fields": {"gameManager": {"_type": "GameObjectRef", "name": "GameManager"}}},
        ])
        gm = _go("GameManager")
        scene = _make_scene(player, gm)
        manifest = _prefab_manifest("Pipes")  # GameManager NOT in prefab list
        result = generate_scene_script(scene, prefab_manifest=manifest)
        assert "prop.objectReferenceValue = go_GameManager;" in result
        # Must NOT load a GameManager prefab asset
        assert "GameManager.prefab" not in result

    def test_no_manifest_falls_back_to_scene_reference(self):
        """Without a prefab manifest, all refs wire the scene object (back-compat)."""
        spawner = _go("Spawner", components=[
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Spawner", "is_monobehaviour": True,
             "fields": {"prefab": {"_type": "GameObjectRef", "name": "Pipes"}}},
        ])
        pipes = _go("Pipes")
        scene = _make_scene(spawner, pipes)
        result = generate_scene_script(scene)  # no manifest
        assert "prop.objectReferenceValue = go_Pipes;" in result
        assert "LoadAssetAtPath<GameObject>" not in result


# --------------- AutoStart fixture (Flappy Bird deploy lesson gap 1) ---------------

class TestAutoStartFixture:
    """The generator always emits an AutoStart GameObject so scaffolder-
    supplied AutoStart.cs runs at Play time and un-pauses any paused
    GameManager.  Without this, games where run_*.py wires the UI Play
    button (and thus has no .cs click-handler after the gap 4 filter)
    start paused and never recover.  See data/lessons/flappy_bird_deploy.md.
    """

    def test_autostart_gameobject_created(self):
        scene = _make_scene(_go("Player"))
        result = generate_scene_script(scene)
        assert 'new GameObject("AutoStart")' in result
        assert "AddComponent<AutoStart>()" in result

    def test_autostart_idempotent_when_scene_already_has_one(self):
        """If the Python scene already exports an AutoStart GameObject,
        the generator must not emit a second one."""
        scene = _make_scene(_go("Player"), _go("AutoStart"))
        result = generate_scene_script(scene)
        # The runtime find-or-create guard may appear, but no second
        # explicit `new GameObject("AutoStart")` outside that guard.
        # Count occurrences of the literal creation line.
        occurrences = result.count('new GameObject("AutoStart")')
        assert occurrences <= 1, (
            f"AutoStart emitted {occurrences} times — must be 0 or 1."
        )

    def test_autostart_uses_find_guard_for_reruns(self):
        """The emitted code must check `GameObject.Find(\"AutoStart\")` so
        re-running Setup doesn't duplicate the fixture."""
        scene = _make_scene(_go("Player"))
        result = generate_scene_script(scene)
        assert 'GameObject.Find("AutoStart")' in result


# --------------- Tiled sprite drawMode (Flappy Bird deploy lesson gap 4) ---------------

class TestParallaxSpriteTiling:
    """SpriteRenderers on GameObjects that also have a Parallax MonoBehaviour
    must emit `drawMode = SpriteDrawMode.Tiled` + a wide `size` so the
    scrolling background covers any reasonable orthographic viewport.

    Without this, a 6u-wide sprite scrolling through an ~18u-wide viewport
    leaves blue camera-background strips on the sides and disappears
    mid-cycle (the symptom in flappy_bird_deploy.md gap 4).
    """

    def test_parallax_sprite_emits_tiled_drawmode(self):
        background = _go("Background", components=[
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "SpriteRenderer", "color": [255, 255, 255],
             "size": [6.0, 10.67], "asset_ref": "background"},
            {"type": "Parallax", "is_monobehaviour": True,
             "fields": {"animationSpeed": 0.5, "wrapWidth": 20.0}},
        ])
        scene = _make_scene(background)
        result = generate_scene_script(scene)
        assert "drawMode = SpriteDrawMode.Tiled" in result
        # Width must be wide (we use 40 as a generous default)
        assert "new Vector2(40f, 10.67f)" in result

    def test_non_parallax_sprite_stays_simple(self):
        """A SpriteRenderer without a Parallax sibling component must NOT
        be tiled — player sprites, pipe sprites, etc. should render at
        their natural size."""
        player = _go("Player", components=[
            {"type": "Transform", "position": [-2, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "SpriteRenderer", "color": [255, 255, 255],
             "size": [0.7, 0.5], "asset_ref": "bird_01"},
        ])
        scene = _make_scene(player)
        result = generate_scene_script(scene)
        assert "SpriteDrawMode.Tiled" not in result

    def test_sprite_array_field_wired_from_sprite_mappings(self):
        """Gap 6 (data/lessons/flappy_bird_deploy.md): a SpriteArrayRef
        field is wired via SerializedObject with one entry per asset
        name, pointing to the `sprite_<name>` variables the header of
        the generated script loads from sprite_mappings."""
        player = _go("Player", components=[
            {"type": "Transform", "position": [-2, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Player", "is_monobehaviour": True,
             "fields": {
                 "sprites": {
                     "_type": "SpriteArrayRef",
                     "refs": ["bird_01", "bird_02", "bird_03"],
                 }
             }},
        ])
        scene = _make_scene(player)
        mapping = {
            "sprites": {
                "bird_01": {"unity_path": "Assets/Art/Sprites/Bird_01.png"},
                "bird_02": {"unity_path": "Assets/Art/Sprites/Bird_02.png"},
                "bird_03": {"unity_path": "Assets/Art/Sprites/Bird_03.png"},
            }
        }
        result = generate_scene_script(scene, mapping)
        assert "FindProperty(\"sprites\")" in result
        assert "prop.arraySize = 3" in result
        assert "objectReferenceValue = sprite_bird_01" in result
        assert "objectReferenceValue = sprite_bird_02" in result
        assert "objectReferenceValue = sprite_bird_03" in result

    def test_sprite_array_skips_entries_not_in_mapping(self):
        """If some asset names aren't in sprite_mappings, only the known
        ones are wired — no reference to an undeclared `sprite_foo` var
        that would produce a compile error."""
        player = _go("Player", components=[
            {"type": "Transform", "position": [0, 0, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "Player", "is_monobehaviour": True,
             "fields": {
                 "sprites": {
                     "_type": "SpriteArrayRef",
                     "refs": ["bird_01", "unknown_asset", "bird_02"],
                 }
             }},
        ])
        scene = _make_scene(player)
        mapping = {
            "sprites": {
                "bird_01": {"unity_path": "Assets/Art/Sprites/Bird_01.png"},
                "bird_02": {"unity_path": "Assets/Art/Sprites/Bird_02.png"},
            }
        }
        result = generate_scene_script(scene, mapping)
        # 2 known entries — arraySize matches only resolvable ones.
        assert "prop.arraySize = 2" in result
        assert "sprite_bird_01" in result
        assert "sprite_bird_02" in result
        assert "sprite_unknown_asset" not in result

    def test_parallax_preserves_sprite_vertical_extent(self):
        """The tiled size keeps the sprite's native height so the vertical
        visual doesn't get stretched — only the width expands to tile."""
        ground = _go("Ground", components=[
            {"type": "Transform", "position": [0, -5.5, 0],
             "rotation": [0, 0, 0, 1], "local_scale": [1, 1, 1]},
            {"type": "SpriteRenderer", "color": [255, 255, 255],
             "size": [7.0, 2.33], "asset_ref": "ground"},
            {"type": "Parallax", "is_monobehaviour": True,
             "fields": {"animationSpeed": 2.0}},
        ])
        scene = _make_scene(ground)
        result = generate_scene_script(scene)
        # Height 2.33 preserved
        assert "2.33f)" in result
        # Stretched width
        assert "new Vector2(40f, 2.33f)" in result
