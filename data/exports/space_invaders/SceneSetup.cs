using UnityEngine;
using UnityEditor;
using System.Linq;

public class GeneratedSceneSetup
{
    public static string Execute()
    {
        string result = "";

        // === CREATE TAGS ===
        var tagManager = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
        var tagsProp = tagManager.FindProperty("tags");
        _EnsureTag(tagsProp, "Boundary");
        _EnsureTag(tagsProp, "Bunker");
        _EnsureTag(tagsProp, "MysteryShip");
        _EnsureTag(tagsProp, "Player");
        tagManager.ApplyModifiedProperties();

        // === LOAD MATERIALS ===
        var unlitMat = AssetDatabase.LoadAssetAtPath<Material>(
            "Packages/com.unity.render-pipelines.universal/Runtime/Materials/Sprite-Unlit-Default.mat");

        // === LOAD SPRITE ASSETS ===
        var sprite_player_ship = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Player.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Player");
        var sprite_laser = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Laser.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Laser");
        var sprite_missile = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Missile.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Missile");
        var sprite_mystery_ship = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/MysteryShip.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "MysteryShip");
        var sprite_bunker = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Bunker.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Bunker");
        var sprite_splat = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Splat.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Splat");
        var sprite_invader_01_1 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Invader_01-1.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_01-1");
        var sprite_invader_01_2 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Invader_01-2.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_01-2");
        var sprite_invader_02_1 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Invader_02-1.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_02-1");
        var sprite_invader_02_2 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Invader_02-2.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_02-2");
        var sprite_invader_03_1 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Invader_03-1.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_03-1");
        var sprite_invader_03_2 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Invader_03-2.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Invader_03-2");

        // === CREATE GAMEOBJECTS ===
        // --- MainCamera (use existing Main Camera) ---
        var go_MainCamera = Camera.main?.gameObject;
        if (go_MainCamera != null)
        {
            var cam = go_MainCamera.GetComponent<Camera>();
            cam.orthographicSize = 7.0f;
            cam.backgroundColor = new Color(0.020f, 0.020f, 0.059f, 1f);
            cam.clearFlags = CameraClearFlags.SolidColor;
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
        go_Player.AddComponent<Player>();
        // Player.speed = 5.0
        EditorUtility.SetDirty(go_Player);

        // --- InvadersGrid ---
        var go_InvadersGrid = new GameObject("InvadersGrid");
        go_InvadersGrid.transform.position = new Vector3(0.0f, 3.0f, 0.0f);
        go_InvadersGrid.AddComponent<Invaders>();
        // Invaders.baseSpeed = 1.0
        // Invaders.columns = 11
        // Invaders.missileSpawnRate = 1.5
        // Invaders.rows = 5
        // Invaders.speedCurveMax = 5.0
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
        go_Bunker_0.AddComponent<Bunker>();
        // Bunker.splatRadius = 2
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
        go_Bunker_1.AddComponent<Bunker>();
        // Bunker.splatRadius = 2
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
        go_Bunker_2.AddComponent<Bunker>();
        // Bunker.splatRadius = 2
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
        go_Bunker_3.AddComponent<Bunker>();
        // Bunker.splatRadius = 2
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
        go_MysteryShip.AddComponent<MysteryShip>();
        // MysteryShip.cycleTime = 30.0
        // MysteryShip.direction = -1
        // MysteryShip.score = 300
        // MysteryShip.speed = 5.0
        EditorUtility.SetDirty(go_MysteryShip);

        // --- BoundaryTop ---
        var go_BoundaryTop = new GameObject("BoundaryTop");
        go_BoundaryTop.tag = "Boundary";
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
        go_BoundaryBottom.transform.position = new Vector3(0.0f, -7.5f, 0.0f);
        var go_BoundaryBottom_rb = go_BoundaryBottom.AddComponent<Rigidbody2D>();
        go_BoundaryBottom_rb.bodyType = RigidbodyType2D.Static;
        var go_BoundaryBottom_bc = go_BoundaryBottom.AddComponent<BoxCollider2D>();
        go_BoundaryBottom_bc.size = new Vector2(20.0f, 1.0f);
        go_BoundaryBottom_bc.isTrigger = true;
        EditorUtility.SetDirty(go_BoundaryBottom);

        // --- GameManager ---
        var go_GameManager = new GameObject("GameManager");
        go_GameManager.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        go_GameManager.AddComponent<GameManager>();
        // GameManager.lives = 3
        EditorUtility.SetDirty(go_GameManager);

        // --- QuitHandler ---
        var go_QuitHandler = new GameObject("QuitHandler");
        go_QuitHandler.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        go_QuitHandler.AddComponent<QuitHandler>();
        EditorUtility.SetDirty(go_QuitHandler);

        // === WIRE CROSS-REFERENCES ===
        {
            var so = new SerializedObject(go_Player.GetComponent<Player>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Player; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_InvadersGrid.GetComponent<Invaders>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_InvadersGrid; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Bunker_0.GetComponent<Bunker>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Bunker_0; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Bunker_1.GetComponent<Bunker>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Bunker_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Bunker_2.GetComponent<Bunker>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Bunker_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Bunker_3.GetComponent<Bunker>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Bunker_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_MysteryShip.GetComponent<MysteryShip>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_MysteryShip; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_GameManager.GetComponent<GameManager>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_GameManager; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_QuitHandler.GetComponent<QuitHandler>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_QuitHandler; so.ApplyModifiedProperties(); }
        }

        // === SAVE ===
        UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(
            UnityEditor.SceneManagement.EditorSceneManager.GetActiveScene());
        UnityEditor.SceneManagement.EditorSceneManager.SaveOpenScenes();

        result = "Scene setup complete: 12 GameObjects";
        return result;
    }

    static void _EnsureTag(SerializedProperty tagsProp, string tag)
    {
        for (int i = 0; i < tagsProp.arraySize; i++)
            if (tagsProp.GetArrayElementAtIndex(i).stringValue == tag) return;
        tagsProp.InsertArrayElementAtIndex(tagsProp.arraySize);
        tagsProp.GetArrayElementAtIndex(tagsProp.arraySize - 1).stringValue = tag;
    }
}
