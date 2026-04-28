using UnityEngine;
using UnityEditor;
using System.Linq;
using SpaceInvaders;

public class GeneratedSceneSetup
{
    public static string Execute()
    {
        // FU-4 editor-guard: EditorSceneManager.NewScene and
        // SaveOpenScenes throw InvalidOperationException when the
        // editor is in Play mode.  Fail fast with a readable message
        // rather than corrupting state mid-play.
        if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isPlaying)
        {
            return "[skipped] scene setup refused: editor is in Play mode";
        }

        string result = "";

        // === CREATE TAGS AND LAYERS ===
        var tagManager = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
        var tagsProp = tagManager.FindProperty("tags");
        _EnsureTag(tagsProp, "Boundary");
        _EnsureTag(tagsProp, "Bunker");
        _EnsureTag(tagsProp, "MysteryShip");
        _EnsureTag(tagsProp, "Player");
        var layersProp = tagManager.FindProperty("layers");
        _EnsureLayer(layersProp, "Layer11");
        tagManager.ApplyModifiedProperties();

        // === LOAD MATERIALS ===
        Material unlitMat = null;
        if (UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline != null)
        {
            unlitMat = AssetDatabase.LoadAssetAtPath<Material>(
                "Packages/com.unity.render-pipelines.universal/Runtime/Materials/Sprite-Unlit-Default.mat");
        }
        if (unlitMat == null)
        {
            // Built-in pipeline fallback — Sprites/Default works on both
            var shader = Shader.Find("Sprites/Default");
            if (shader != null) unlitMat = new Material(shader);
        }

        // === LOAD SPRITE ASSETS ===
        var sprite_player_ship = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Player.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Player")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Player.png");
        var sprite_laser = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Laser.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Laser")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Laser.png");
        var sprite_missile = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Missile.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Missile")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Missile.png");
        var sprite_mystery_ship = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/MysteryShip.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "MysteryShip")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/MysteryShip.png");
        var sprite_bunker = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Bunker.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Bunker")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Bunker.png");
        var sprite_splat = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Splat.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Splat")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Splat.png");
        var sprite_invader_01_1 = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Invader_01-1.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_01-1")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Invader_01-1.png");
        var sprite_invader_01_2 = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Invader_01-2.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_01-2")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Invader_01-2.png");
        var sprite_invader_02_1 = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Invader_02-1.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_02-1")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Invader_02-1.png");
        var sprite_invader_02_2 = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Invader_02-2.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_02-2")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Invader_02-2.png");
        var sprite_invader_03_1 = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Invader_03-1.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_03-1")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Invader_03-1.png");
        var sprite_invader_03_2 = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Sprites/Invader_03-2.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_03-2")
            ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Invader_03-2.png");

        // === CREATE GAMEOBJECTS ===
        // --- MainCamera (find or create Main Camera) ---
        var go_MainCamera = Camera.main?.gameObject;
        if (go_MainCamera == null)
        {
            go_MainCamera = new GameObject();
            go_MainCamera.name = "MainCamera";
            go_MainCamera.AddComponent<Camera>();
            go_MainCamera.tag = "MainCamera";
        }
        {
            var cam = go_MainCamera.GetComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 7.0f;
            cam.backgroundColor = new Color(0.020f, 0.020f, 0.059f, 1f);
            cam.clearFlags = CameraClearFlags.SolidColor;
            go_MainCamera.transform.position = new Vector3(0f, 0f, -10f);
            if (go_MainCamera.GetComponent<AspectLock>() == null)
                go_MainCamera.AddComponent<AspectLock>();
            EditorUtility.SetDirty(go_MainCamera);
        }

        // --- Player ---
        var go_Player = new GameObject("Player");
        go_Player.tag = "Player";
        go_Player.transform.position = new Vector3(0.0f, -5.0f, 0.0f);
        var go_Player_rb = go_Player.AddComponent<Rigidbody2D>();
        go_Player_rb.bodyType = RigidbodyType2D.Kinematic;
        var go_Player_bc = go_Player.AddComponent<BoxCollider2D>();
        go_Player_bc.size = new Vector2(1.5f, 0.8f);
        go_Player_bc.isTrigger = true;
        var go_Player_sr = go_Player.AddComponent<SpriteRenderer>();
        if (sprite_player_ship != null) go_Player_sr.sprite = sprite_player_ship;
        if (unlitMat != null) go_Player_sr.sharedMaterial = unlitMat;
        go_Player_sr.sortingOrder = 3;
        go_Player.AddComponent<SpaceInvaders.Player>();
        {
            var so = new SerializedObject(go_Player.GetComponent<SpaceInvaders.Player>());
            var prop_speed = so.FindProperty("speed");
            if (prop_speed != null) prop_speed.floatValue = 5.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Player);

        // --- InvadersGrid ---
        var go_InvadersGrid = new GameObject("InvadersGrid");
        go_InvadersGrid.transform.position = new Vector3(0.0f, 3.0f, 0.0f);
        go_InvadersGrid.AddComponent<SpaceInvaders.Invaders>();
        {
            var so = new SerializedObject(go_InvadersGrid.GetComponent<SpaceInvaders.Invaders>());
            var prop_speedCurveMax = so.FindProperty("speedCurveMax");
            if (prop_speedCurveMax != null) prop_speedCurveMax.floatValue = 5.0f;
            var prop_rows = so.FindProperty("rows");
            if (prop_rows != null) prop_rows.intValue = 5;
            var prop_columns = so.FindProperty("columns");
            if (prop_columns != null) prop_columns.intValue = 11;
            var prop_missileSpawnRate = so.FindProperty("missileSpawnRate");
            if (prop_missileSpawnRate != null) prop_missileSpawnRate.floatValue = 1.5f;
            var prop_baseSpeed = so.FindProperty("baseSpeed");
            if (prop_baseSpeed != null) prop_baseSpeed.floatValue = 1.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_InvadersGrid);

        // --- Bunker_0 ---
        var go_Bunker_0 = new GameObject("Bunker_0");
        go_Bunker_0.tag = "Bunker";
        go_Bunker_0.transform.position = new Vector3(-4.5f, -3.0f, 0.0f);
        var go_Bunker_0_rb = go_Bunker_0.AddComponent<Rigidbody2D>();
        go_Bunker_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Bunker_0_bc = go_Bunker_0.AddComponent<BoxCollider2D>();
        go_Bunker_0_bc.size = new Vector2(2.0f, 1.5f);
        go_Bunker_0_bc.isTrigger = true;
        var go_Bunker_0_sr = go_Bunker_0.AddComponent<SpriteRenderer>();
        if (sprite_bunker != null) go_Bunker_0_sr.sprite = sprite_bunker;
        if (unlitMat != null) go_Bunker_0_sr.sharedMaterial = unlitMat;
        go_Bunker_0_sr.sortingOrder = 1;
        go_Bunker_0.AddComponent<SpaceInvaders.Bunker>();
        {
            var so = new SerializedObject(go_Bunker_0.GetComponent<SpaceInvaders.Bunker>());
            var prop_splatRadius = so.FindProperty("splatRadius");
            if (prop_splatRadius != null) prop_splatRadius.intValue = 2;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Bunker_0);

        // --- Bunker_1 ---
        var go_Bunker_1 = new GameObject("Bunker_1");
        go_Bunker_1.tag = "Bunker";
        go_Bunker_1.transform.position = new Vector3(-1.5f, -3.0f, 0.0f);
        var go_Bunker_1_rb = go_Bunker_1.AddComponent<Rigidbody2D>();
        go_Bunker_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Bunker_1_bc = go_Bunker_1.AddComponent<BoxCollider2D>();
        go_Bunker_1_bc.size = new Vector2(2.0f, 1.5f);
        go_Bunker_1_bc.isTrigger = true;
        var go_Bunker_1_sr = go_Bunker_1.AddComponent<SpriteRenderer>();
        if (sprite_bunker != null) go_Bunker_1_sr.sprite = sprite_bunker;
        if (unlitMat != null) go_Bunker_1_sr.sharedMaterial = unlitMat;
        go_Bunker_1_sr.sortingOrder = 1;
        go_Bunker_1.AddComponent<SpaceInvaders.Bunker>();
        {
            var so = new SerializedObject(go_Bunker_1.GetComponent<SpaceInvaders.Bunker>());
            var prop_splatRadius = so.FindProperty("splatRadius");
            if (prop_splatRadius != null) prop_splatRadius.intValue = 2;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Bunker_1);

        // --- Bunker_2 ---
        var go_Bunker_2 = new GameObject("Bunker_2");
        go_Bunker_2.tag = "Bunker";
        go_Bunker_2.transform.position = new Vector3(1.5f, -3.0f, 0.0f);
        var go_Bunker_2_rb = go_Bunker_2.AddComponent<Rigidbody2D>();
        go_Bunker_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Bunker_2_bc = go_Bunker_2.AddComponent<BoxCollider2D>();
        go_Bunker_2_bc.size = new Vector2(2.0f, 1.5f);
        go_Bunker_2_bc.isTrigger = true;
        var go_Bunker_2_sr = go_Bunker_2.AddComponent<SpriteRenderer>();
        if (sprite_bunker != null) go_Bunker_2_sr.sprite = sprite_bunker;
        if (unlitMat != null) go_Bunker_2_sr.sharedMaterial = unlitMat;
        go_Bunker_2_sr.sortingOrder = 1;
        go_Bunker_2.AddComponent<SpaceInvaders.Bunker>();
        {
            var so = new SerializedObject(go_Bunker_2.GetComponent<SpaceInvaders.Bunker>());
            var prop_splatRadius = so.FindProperty("splatRadius");
            if (prop_splatRadius != null) prop_splatRadius.intValue = 2;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Bunker_2);

        // --- Bunker_3 ---
        var go_Bunker_3 = new GameObject("Bunker_3");
        go_Bunker_3.tag = "Bunker";
        go_Bunker_3.transform.position = new Vector3(4.5f, -3.0f, 0.0f);
        var go_Bunker_3_rb = go_Bunker_3.AddComponent<Rigidbody2D>();
        go_Bunker_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Bunker_3_bc = go_Bunker_3.AddComponent<BoxCollider2D>();
        go_Bunker_3_bc.size = new Vector2(2.0f, 1.5f);
        go_Bunker_3_bc.isTrigger = true;
        var go_Bunker_3_sr = go_Bunker_3.AddComponent<SpriteRenderer>();
        if (sprite_bunker != null) go_Bunker_3_sr.sprite = sprite_bunker;
        if (unlitMat != null) go_Bunker_3_sr.sharedMaterial = unlitMat;
        go_Bunker_3_sr.sortingOrder = 1;
        go_Bunker_3.AddComponent<SpaceInvaders.Bunker>();
        {
            var so = new SerializedObject(go_Bunker_3.GetComponent<SpaceInvaders.Bunker>());
            var prop_splatRadius = so.FindProperty("splatRadius");
            if (prop_splatRadius != null) prop_splatRadius.intValue = 2;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Bunker_3);

        // --- MysteryShip ---
        var go_MysteryShip = new GameObject("MysteryShip");
        go_MysteryShip.tag = "MysteryShip";
        go_MysteryShip.transform.position = new Vector3(-8.0f, 5.5f, 0.0f);
        var go_MysteryShip_rb = go_MysteryShip.AddComponent<Rigidbody2D>();
        go_MysteryShip_rb.bodyType = RigidbodyType2D.Kinematic;
        var go_MysteryShip_bc = go_MysteryShip.AddComponent<BoxCollider2D>();
        go_MysteryShip_bc.size = new Vector2(2.0f, 0.8f);
        go_MysteryShip_bc.isTrigger = true;
        var go_MysteryShip_sr = go_MysteryShip.AddComponent<SpriteRenderer>();
        if (sprite_mystery_ship != null) go_MysteryShip_sr.sprite = sprite_mystery_ship;
        if (unlitMat != null) go_MysteryShip_sr.sharedMaterial = unlitMat;
        go_MysteryShip_sr.sortingOrder = 4;
        go_MysteryShip.AddComponent<SpaceInvaders.MysteryShip>();
        {
            var so = new SerializedObject(go_MysteryShip.GetComponent<SpaceInvaders.MysteryShip>());
            var prop_speed = so.FindProperty("speed");
            if (prop_speed != null) prop_speed.floatValue = 5.0f;
            var prop_cycleTime = so.FindProperty("cycleTime");
            if (prop_cycleTime != null) prop_cycleTime.floatValue = 30.0f;
            var prop_score = so.FindProperty("score");
            if (prop_score != null) prop_score.intValue = 300;
            var prop_direction = so.FindProperty("direction");
            if (prop_direction != null) prop_direction.intValue = -1;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_MysteryShip);

        // --- BoundaryTop ---
        var go_BoundaryTop = new GameObject("BoundaryTop");
        go_BoundaryTop.tag = "Boundary";
        go_BoundaryTop.layer = LayerMask.NameToLayer("Layer11");
        go_BoundaryTop.transform.position = new Vector3(0.0f, 7.5f, 0.0f);
        var go_BoundaryTop_rb = go_BoundaryTop.AddComponent<Rigidbody2D>();
        go_BoundaryTop_rb.bodyType = RigidbodyType2D.Static;
        var go_BoundaryTop_bc = go_BoundaryTop.AddComponent<BoxCollider2D>();
        go_BoundaryTop_bc.size = new Vector2(20.0f, 1.0f);
        go_BoundaryTop_bc.isTrigger = true;
        EditorUtility.SetDirty(go_BoundaryTop);

        // --- BoundaryBottom ---
        var go_BoundaryBottom = new GameObject("BoundaryBottom");
        go_BoundaryBottom.tag = "Boundary";
        go_BoundaryBottom.layer = LayerMask.NameToLayer("Layer11");
        go_BoundaryBottom.transform.position = new Vector3(0.0f, -7.5f, 0.0f);
        var go_BoundaryBottom_rb = go_BoundaryBottom.AddComponent<Rigidbody2D>();
        go_BoundaryBottom_rb.bodyType = RigidbodyType2D.Static;
        var go_BoundaryBottom_bc = go_BoundaryBottom.AddComponent<BoxCollider2D>();
        go_BoundaryBottom_bc.size = new Vector2(20.0f, 1.0f);
        go_BoundaryBottom_bc.isTrigger = true;
        EditorUtility.SetDirty(go_BoundaryBottom);

        // --- GameManager ---
        var go_GameManager = new GameObject("GameManager");
        go_GameManager.AddComponent<SpaceInvaders.GameManager>();
        {
            var so = new SerializedObject(go_GameManager.GetComponent<SpaceInvaders.GameManager>());
            var prop_lives = so.FindProperty("lives");
            if (prop_lives != null) prop_lives.intValue = 3;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_GameManager);

        // === WIRE CROSS-REFERENCES ===

        // --- AutoStart (scaffolder fixture, un-pauses on Play) ---
        if (GameObject.Find("AutoStart") == null)
        {
            var go_AutoStart = new GameObject("AutoStart");
            go_AutoStart.AddComponent<AutoStart>();
            EditorUtility.SetDirty(go_AutoStart);
        }

        // === SAVE ===
        // FU-4 scene-save-path: force the canonical scene path so
        // CoPlay's save_scene MCP call doesn't silently drop Scene.unity
        // at Assets/ root (see coplay_generator_gaps.md P2 observation).
        const string _scenePath = "Assets/_Project/Scenes/Scene.unity";
        var _activeScene = UnityEditor.SceneManagement.EditorSceneManager.GetActiveScene();
        UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(_activeScene);
        if (string.IsNullOrEmpty(_activeScene.path))
        {
            System.IO.Directory.CreateDirectory("Assets/_Project/Scenes");
            UnityEditor.SceneManagement.EditorSceneManager.SaveScene(_activeScene, _scenePath);
        }
        else
        {
            UnityEditor.SceneManagement.EditorSceneManager.SaveOpenScenes();
        }

        result = "Scene setup complete: 11 GameObjects";
        return result;
    }

    static void _EnsureTag(SerializedProperty tagsProp, string tag)
    {
        for (int i = 0; i < tagsProp.arraySize; i++)
            if (tagsProp.GetArrayElementAtIndex(i).stringValue == tag) return;
        tagsProp.InsertArrayElementAtIndex(tagsProp.arraySize);
        tagsProp.GetArrayElementAtIndex(tagsProp.arraySize - 1).stringValue = tag;
    }

    static void _EnsureLayer(SerializedProperty layersProp, string name)
    {
        for (int i = 0; i < layersProp.arraySize; i++)
            if (layersProp.GetArrayElementAtIndex(i).stringValue == name) return;
        for (int i = 8; i < layersProp.arraySize; i++)
        {
            if (string.IsNullOrEmpty(layersProp.GetArrayElementAtIndex(i).stringValue))
            {
                layersProp.GetArrayElementAtIndex(i).stringValue = name;
                return;
            }
        }
    }
}
