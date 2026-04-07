using UnityEngine;
using UnityEditor;
using System.Linq;

public class GeneratedSceneSetup
{
    public static string Execute()
    {
        string result = "";

        // === CREATE TAGS AND LAYERS ===
        var tagManager = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
        var tagsProp = tagManager.FindProperty("tags");
        _EnsureTag(tagsProp, "Ghost");
        _EnsureTag(tagsProp, "Pacman");
        _EnsureTag(tagsProp, "Pellet");
        _EnsureTag(tagsProp, "PowerPellet");
        var layersProp = tagManager.FindProperty("layers");
        _EnsureLayer(layersProp, "Layer6");
        _EnsureLayer(layersProp, "Layer7");
        _EnsureLayer(layersProp, "Layer8");
        tagManager.ApplyModifiedProperties();

        // === LOAD MATERIALS ===
        var unlitMat = AssetDatabase.LoadAssetAtPath<Material>(
            "Packages/com.unity.render-pipelines.universal/Runtime/Materials/Sprite-Unlit-Default.mat");

        // === LOAD SPRITE ASSETS ===
        var sprite_wall = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Wall_00.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Wall_00");
        var sprite_pellet_small = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pellet_Small.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pellet_Small");
        var sprite_pellet_large = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pellet_Large.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pellet_Large");
        var sprite_pacman_01 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_01.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_01");
        var sprite_pacman_02 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_02.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_02");
        var sprite_pacman_03 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_03.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_03");
        var sprite_pacman_death_01 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_01.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_01");
        var sprite_pacman_death_02 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_02.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_02");
        var sprite_pacman_death_03 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_03.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_03");
        var sprite_pacman_death_04 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_04.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_04");
        var sprite_pacman_death_05 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_05.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_05");
        var sprite_pacman_death_06 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_06.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_06");
        var sprite_pacman_death_07 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_07.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_07");
        var sprite_pacman_death_08 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_08.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_08");
        var sprite_pacman_death_09 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_09.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_09");
        var sprite_pacman_death_10 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_10.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_10");
        var sprite_pacman_death_11 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Pacman_Death_11.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Pacman_Death_11");
        var sprite_ghost_blinky = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Body_01.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Body_01");
        var sprite_ghost_pinky = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Body_01.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Body_01");
        var sprite_ghost_inky = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Body_01.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Body_01");
        var sprite_ghost_clyde = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Body_01.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Body_01");
        var sprite_ghost_eyes_up = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Eyes_Up.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Eyes_Up");
        var sprite_ghost_eyes_down = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Eyes_Down.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Eyes_Down");
        var sprite_ghost_eyes_left = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Eyes_Left.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Eyes_Left");
        var sprite_ghost_eyes_right = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Eyes_Right.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Eyes_Right");
        var sprite_ghost_vulnerable_blue_01 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Vulnerable_Blue_01.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Vulnerable_Blue_01");
        var sprite_ghost_vulnerable_blue_02 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Vulnerable_Blue_02.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Vulnerable_Blue_02");
        var sprite_ghost_vulnerable_white_01 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Vulnerable_White_01.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Vulnerable_White_01");
        var sprite_ghost_vulnerable_white_02 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Vulnerable_White_02.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Vulnerable_White_02");
        var sprite_ghost_body_01 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Body_01.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Body_01");
        var sprite_ghost_body_02 = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Ghost_Body_02.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Ghost_Body_02");
        var sprite_node = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Node.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "Node");

        // === CREATE GAMEOBJECTS ===
        // --- MainCamera (use existing Main Camera) ---
        var go_MainCamera = Camera.main?.gameObject;
        if (go_MainCamera != null)
        {
            var cam = go_MainCamera.GetComponent<Camera>();
            cam.orthographicSize = 16.0f;
            cam.backgroundColor = new Color(0.000f, 0.000f, 0.000f, 1f);
            cam.clearFlags = CameraClearFlags.SolidColor;
            EditorUtility.SetDirty(go_MainCamera);
        }

        // --- Wall_0_0 ---
        var go_Wall_0_0 = new GameObject("Wall_0_0");
        go_Wall_0_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_0.transform.position = new Vector3(-13.5f, 15.0f, 0.0f);
        var go_Wall_0_0_rb = go_Wall_0_0.AddComponent<Rigidbody2D>();
        go_Wall_0_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_0_bc = go_Wall_0_0.AddComponent<BoxCollider2D>();
        go_Wall_0_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_0_sr = go_Wall_0_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_0);

        // --- Wall_0_1 ---
        var go_Wall_0_1 = new GameObject("Wall_0_1");
        go_Wall_0_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_1.transform.position = new Vector3(-12.5f, 15.0f, 0.0f);
        var go_Wall_0_1_rb = go_Wall_0_1.AddComponent<Rigidbody2D>();
        go_Wall_0_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_1_bc = go_Wall_0_1.AddComponent<BoxCollider2D>();
        go_Wall_0_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_1_sr = go_Wall_0_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_1);

        // --- Wall_0_2 ---
        var go_Wall_0_2 = new GameObject("Wall_0_2");
        go_Wall_0_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_2.transform.position = new Vector3(-11.5f, 15.0f, 0.0f);
        var go_Wall_0_2_rb = go_Wall_0_2.AddComponent<Rigidbody2D>();
        go_Wall_0_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_2_bc = go_Wall_0_2.AddComponent<BoxCollider2D>();
        go_Wall_0_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_2_sr = go_Wall_0_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_2);

        // --- Wall_0_3 ---
        var go_Wall_0_3 = new GameObject("Wall_0_3");
        go_Wall_0_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_3.transform.position = new Vector3(-10.5f, 15.0f, 0.0f);
        var go_Wall_0_3_rb = go_Wall_0_3.AddComponent<Rigidbody2D>();
        go_Wall_0_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_3_bc = go_Wall_0_3.AddComponent<BoxCollider2D>();
        go_Wall_0_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_3_sr = go_Wall_0_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_3);

        // --- Wall_0_4 ---
        var go_Wall_0_4 = new GameObject("Wall_0_4");
        go_Wall_0_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_4.transform.position = new Vector3(-9.5f, 15.0f, 0.0f);
        var go_Wall_0_4_rb = go_Wall_0_4.AddComponent<Rigidbody2D>();
        go_Wall_0_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_4_bc = go_Wall_0_4.AddComponent<BoxCollider2D>();
        go_Wall_0_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_4_sr = go_Wall_0_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_4);

        // --- Wall_0_5 ---
        var go_Wall_0_5 = new GameObject("Wall_0_5");
        go_Wall_0_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_5.transform.position = new Vector3(-8.5f, 15.0f, 0.0f);
        var go_Wall_0_5_rb = go_Wall_0_5.AddComponent<Rigidbody2D>();
        go_Wall_0_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_5_bc = go_Wall_0_5.AddComponent<BoxCollider2D>();
        go_Wall_0_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_5_sr = go_Wall_0_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_5);

        // --- Wall_0_6 ---
        var go_Wall_0_6 = new GameObject("Wall_0_6");
        go_Wall_0_6.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_6.transform.position = new Vector3(-7.5f, 15.0f, 0.0f);
        var go_Wall_0_6_rb = go_Wall_0_6.AddComponent<Rigidbody2D>();
        go_Wall_0_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_6_bc = go_Wall_0_6.AddComponent<BoxCollider2D>();
        go_Wall_0_6_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_6_sr = go_Wall_0_6.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_6_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_6_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_6);

        // --- Wall_0_7 ---
        var go_Wall_0_7 = new GameObject("Wall_0_7");
        go_Wall_0_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_7.transform.position = new Vector3(-6.5f, 15.0f, 0.0f);
        var go_Wall_0_7_rb = go_Wall_0_7.AddComponent<Rigidbody2D>();
        go_Wall_0_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_7_bc = go_Wall_0_7.AddComponent<BoxCollider2D>();
        go_Wall_0_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_7_sr = go_Wall_0_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_7);

        // --- Wall_0_8 ---
        var go_Wall_0_8 = new GameObject("Wall_0_8");
        go_Wall_0_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_8.transform.position = new Vector3(-5.5f, 15.0f, 0.0f);
        var go_Wall_0_8_rb = go_Wall_0_8.AddComponent<Rigidbody2D>();
        go_Wall_0_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_8_bc = go_Wall_0_8.AddComponent<BoxCollider2D>();
        go_Wall_0_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_8_sr = go_Wall_0_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_8);

        // --- Wall_0_9 ---
        var go_Wall_0_9 = new GameObject("Wall_0_9");
        go_Wall_0_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_9.transform.position = new Vector3(-4.5f, 15.0f, 0.0f);
        var go_Wall_0_9_rb = go_Wall_0_9.AddComponent<Rigidbody2D>();
        go_Wall_0_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_9_bc = go_Wall_0_9.AddComponent<BoxCollider2D>();
        go_Wall_0_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_9_sr = go_Wall_0_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_9);

        // --- Wall_0_10 ---
        var go_Wall_0_10 = new GameObject("Wall_0_10");
        go_Wall_0_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_10.transform.position = new Vector3(-3.5f, 15.0f, 0.0f);
        var go_Wall_0_10_rb = go_Wall_0_10.AddComponent<Rigidbody2D>();
        go_Wall_0_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_10_bc = go_Wall_0_10.AddComponent<BoxCollider2D>();
        go_Wall_0_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_10_sr = go_Wall_0_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_10);

        // --- Wall_0_11 ---
        var go_Wall_0_11 = new GameObject("Wall_0_11");
        go_Wall_0_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_11.transform.position = new Vector3(-2.5f, 15.0f, 0.0f);
        var go_Wall_0_11_rb = go_Wall_0_11.AddComponent<Rigidbody2D>();
        go_Wall_0_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_11_bc = go_Wall_0_11.AddComponent<BoxCollider2D>();
        go_Wall_0_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_11_sr = go_Wall_0_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_11);

        // --- Wall_0_12 ---
        var go_Wall_0_12 = new GameObject("Wall_0_12");
        go_Wall_0_12.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_12.transform.position = new Vector3(-1.5f, 15.0f, 0.0f);
        var go_Wall_0_12_rb = go_Wall_0_12.AddComponent<Rigidbody2D>();
        go_Wall_0_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_12_bc = go_Wall_0_12.AddComponent<BoxCollider2D>();
        go_Wall_0_12_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_12_sr = go_Wall_0_12.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_12_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_12_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_12);

        // --- Wall_0_13 ---
        var go_Wall_0_13 = new GameObject("Wall_0_13");
        go_Wall_0_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_13.transform.position = new Vector3(-0.5f, 15.0f, 0.0f);
        var go_Wall_0_13_rb = go_Wall_0_13.AddComponent<Rigidbody2D>();
        go_Wall_0_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_13_bc = go_Wall_0_13.AddComponent<BoxCollider2D>();
        go_Wall_0_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_13_sr = go_Wall_0_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_13);

        // --- Wall_0_14 ---
        var go_Wall_0_14 = new GameObject("Wall_0_14");
        go_Wall_0_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_14.transform.position = new Vector3(0.5f, 15.0f, 0.0f);
        var go_Wall_0_14_rb = go_Wall_0_14.AddComponent<Rigidbody2D>();
        go_Wall_0_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_14_bc = go_Wall_0_14.AddComponent<BoxCollider2D>();
        go_Wall_0_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_14_sr = go_Wall_0_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_14);

        // --- Wall_0_15 ---
        var go_Wall_0_15 = new GameObject("Wall_0_15");
        go_Wall_0_15.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_15.transform.position = new Vector3(1.5f, 15.0f, 0.0f);
        var go_Wall_0_15_rb = go_Wall_0_15.AddComponent<Rigidbody2D>();
        go_Wall_0_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_15_bc = go_Wall_0_15.AddComponent<BoxCollider2D>();
        go_Wall_0_15_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_15_sr = go_Wall_0_15.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_15_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_15_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_15);

        // --- Wall_0_16 ---
        var go_Wall_0_16 = new GameObject("Wall_0_16");
        go_Wall_0_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_16.transform.position = new Vector3(2.5f, 15.0f, 0.0f);
        var go_Wall_0_16_rb = go_Wall_0_16.AddComponent<Rigidbody2D>();
        go_Wall_0_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_16_bc = go_Wall_0_16.AddComponent<BoxCollider2D>();
        go_Wall_0_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_16_sr = go_Wall_0_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_16);

        // --- Wall_0_17 ---
        var go_Wall_0_17 = new GameObject("Wall_0_17");
        go_Wall_0_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_17.transform.position = new Vector3(3.5f, 15.0f, 0.0f);
        var go_Wall_0_17_rb = go_Wall_0_17.AddComponent<Rigidbody2D>();
        go_Wall_0_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_17_bc = go_Wall_0_17.AddComponent<BoxCollider2D>();
        go_Wall_0_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_17_sr = go_Wall_0_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_17);

        // --- Wall_0_18 ---
        var go_Wall_0_18 = new GameObject("Wall_0_18");
        go_Wall_0_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_18.transform.position = new Vector3(4.5f, 15.0f, 0.0f);
        var go_Wall_0_18_rb = go_Wall_0_18.AddComponent<Rigidbody2D>();
        go_Wall_0_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_18_bc = go_Wall_0_18.AddComponent<BoxCollider2D>();
        go_Wall_0_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_18_sr = go_Wall_0_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_18);

        // --- Wall_0_19 ---
        var go_Wall_0_19 = new GameObject("Wall_0_19");
        go_Wall_0_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_19.transform.position = new Vector3(5.5f, 15.0f, 0.0f);
        var go_Wall_0_19_rb = go_Wall_0_19.AddComponent<Rigidbody2D>();
        go_Wall_0_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_19_bc = go_Wall_0_19.AddComponent<BoxCollider2D>();
        go_Wall_0_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_19_sr = go_Wall_0_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_19);

        // --- Wall_0_20 ---
        var go_Wall_0_20 = new GameObject("Wall_0_20");
        go_Wall_0_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_20.transform.position = new Vector3(6.5f, 15.0f, 0.0f);
        var go_Wall_0_20_rb = go_Wall_0_20.AddComponent<Rigidbody2D>();
        go_Wall_0_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_20_bc = go_Wall_0_20.AddComponent<BoxCollider2D>();
        go_Wall_0_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_20_sr = go_Wall_0_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_20);

        // --- Wall_0_21 ---
        var go_Wall_0_21 = new GameObject("Wall_0_21");
        go_Wall_0_21.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_21.transform.position = new Vector3(7.5f, 15.0f, 0.0f);
        var go_Wall_0_21_rb = go_Wall_0_21.AddComponent<Rigidbody2D>();
        go_Wall_0_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_21_bc = go_Wall_0_21.AddComponent<BoxCollider2D>();
        go_Wall_0_21_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_21_sr = go_Wall_0_21.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_21_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_21_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_21);

        // --- Wall_0_22 ---
        var go_Wall_0_22 = new GameObject("Wall_0_22");
        go_Wall_0_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_22.transform.position = new Vector3(8.5f, 15.0f, 0.0f);
        var go_Wall_0_22_rb = go_Wall_0_22.AddComponent<Rigidbody2D>();
        go_Wall_0_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_22_bc = go_Wall_0_22.AddComponent<BoxCollider2D>();
        go_Wall_0_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_22_sr = go_Wall_0_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_22);

        // --- Wall_0_23 ---
        var go_Wall_0_23 = new GameObject("Wall_0_23");
        go_Wall_0_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_23.transform.position = new Vector3(9.5f, 15.0f, 0.0f);
        var go_Wall_0_23_rb = go_Wall_0_23.AddComponent<Rigidbody2D>();
        go_Wall_0_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_23_bc = go_Wall_0_23.AddComponent<BoxCollider2D>();
        go_Wall_0_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_23_sr = go_Wall_0_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_23);

        // --- Wall_0_24 ---
        var go_Wall_0_24 = new GameObject("Wall_0_24");
        go_Wall_0_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_24.transform.position = new Vector3(10.5f, 15.0f, 0.0f);
        var go_Wall_0_24_rb = go_Wall_0_24.AddComponent<Rigidbody2D>();
        go_Wall_0_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_24_bc = go_Wall_0_24.AddComponent<BoxCollider2D>();
        go_Wall_0_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_24_sr = go_Wall_0_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_24);

        // --- Wall_0_25 ---
        var go_Wall_0_25 = new GameObject("Wall_0_25");
        go_Wall_0_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_25.transform.position = new Vector3(11.5f, 15.0f, 0.0f);
        var go_Wall_0_25_rb = go_Wall_0_25.AddComponent<Rigidbody2D>();
        go_Wall_0_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_25_bc = go_Wall_0_25.AddComponent<BoxCollider2D>();
        go_Wall_0_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_25_sr = go_Wall_0_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_25);

        // --- Wall_0_26 ---
        var go_Wall_0_26 = new GameObject("Wall_0_26");
        go_Wall_0_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_26.transform.position = new Vector3(12.5f, 15.0f, 0.0f);
        var go_Wall_0_26_rb = go_Wall_0_26.AddComponent<Rigidbody2D>();
        go_Wall_0_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_26_bc = go_Wall_0_26.AddComponent<BoxCollider2D>();
        go_Wall_0_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_26_sr = go_Wall_0_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_26);

        // --- Wall_0_27 ---
        var go_Wall_0_27 = new GameObject("Wall_0_27");
        go_Wall_0_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_0_27.transform.position = new Vector3(13.5f, 15.0f, 0.0f);
        var go_Wall_0_27_rb = go_Wall_0_27.AddComponent<Rigidbody2D>();
        go_Wall_0_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_0_27_bc = go_Wall_0_27.AddComponent<BoxCollider2D>();
        go_Wall_0_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_0_27_sr = go_Wall_0_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_0_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_0_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_0_27);

        // --- Wall_1_0 ---
        var go_Wall_1_0 = new GameObject("Wall_1_0");
        go_Wall_1_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_1_0.transform.position = new Vector3(-13.5f, 14.0f, 0.0f);
        var go_Wall_1_0_rb = go_Wall_1_0.AddComponent<Rigidbody2D>();
        go_Wall_1_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_1_0_bc = go_Wall_1_0.AddComponent<BoxCollider2D>();
        go_Wall_1_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_1_0_sr = go_Wall_1_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_1_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_1_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_1_0);

        // --- Pellet_1_1 ---
        var go_Pellet_1_1 = new GameObject("Pellet_1_1");
        go_Pellet_1_1.tag = "Pellet";
        go_Pellet_1_1.transform.position = new Vector3(-12.5f, 14.0f, 0.0f);
        var go_Pellet_1_1_rb = go_Pellet_1_1.AddComponent<Rigidbody2D>();
        go_Pellet_1_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_1_bc = go_Pellet_1_1.AddComponent<BoxCollider2D>();
        go_Pellet_1_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_1_bc.isTrigger = true;
        var go_Pellet_1_1_sr = go_Pellet_1_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_1_sr.sharedMaterial = unlitMat;
        go_Pellet_1_1_sr.sortingOrder = 2;
        go_Pellet_1_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_1);

        // --- Node_1_1 ---
        var go_Node_1_1 = new GameObject("Node_1_1");
        go_Node_1_1.transform.position = new Vector3(-12.5f, 14.0f, 0.0f);
        var go_Node_1_1_rb = go_Node_1_1.AddComponent<Rigidbody2D>();
        go_Node_1_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_1_1_bc = go_Node_1_1.AddComponent<BoxCollider2D>();
        go_Node_1_1_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_1_1_bc.isTrigger = true;
        go_Node_1_1.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_1_1);

        // --- Pellet_1_2 ---
        var go_Pellet_1_2 = new GameObject("Pellet_1_2");
        go_Pellet_1_2.tag = "Pellet";
        go_Pellet_1_2.transform.position = new Vector3(-11.5f, 14.0f, 0.0f);
        var go_Pellet_1_2_rb = go_Pellet_1_2.AddComponent<Rigidbody2D>();
        go_Pellet_1_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_2_bc = go_Pellet_1_2.AddComponent<BoxCollider2D>();
        go_Pellet_1_2_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_2_bc.isTrigger = true;
        var go_Pellet_1_2_sr = go_Pellet_1_2.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_2_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_2_sr.sharedMaterial = unlitMat;
        go_Pellet_1_2_sr.sortingOrder = 2;
        go_Pellet_1_2.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_2);

        // --- Pellet_1_3 ---
        var go_Pellet_1_3 = new GameObject("Pellet_1_3");
        go_Pellet_1_3.tag = "Pellet";
        go_Pellet_1_3.transform.position = new Vector3(-10.5f, 14.0f, 0.0f);
        var go_Pellet_1_3_rb = go_Pellet_1_3.AddComponent<Rigidbody2D>();
        go_Pellet_1_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_3_bc = go_Pellet_1_3.AddComponent<BoxCollider2D>();
        go_Pellet_1_3_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_3_bc.isTrigger = true;
        var go_Pellet_1_3_sr = go_Pellet_1_3.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_3_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_3_sr.sharedMaterial = unlitMat;
        go_Pellet_1_3_sr.sortingOrder = 2;
        go_Pellet_1_3.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_3);

        // --- Pellet_1_4 ---
        var go_Pellet_1_4 = new GameObject("Pellet_1_4");
        go_Pellet_1_4.tag = "Pellet";
        go_Pellet_1_4.transform.position = new Vector3(-9.5f, 14.0f, 0.0f);
        var go_Pellet_1_4_rb = go_Pellet_1_4.AddComponent<Rigidbody2D>();
        go_Pellet_1_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_4_bc = go_Pellet_1_4.AddComponent<BoxCollider2D>();
        go_Pellet_1_4_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_4_bc.isTrigger = true;
        var go_Pellet_1_4_sr = go_Pellet_1_4.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_4_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_4_sr.sharedMaterial = unlitMat;
        go_Pellet_1_4_sr.sortingOrder = 2;
        go_Pellet_1_4.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_4);

        // --- Pellet_1_5 ---
        var go_Pellet_1_5 = new GameObject("Pellet_1_5");
        go_Pellet_1_5.tag = "Pellet";
        go_Pellet_1_5.transform.position = new Vector3(-8.5f, 14.0f, 0.0f);
        var go_Pellet_1_5_rb = go_Pellet_1_5.AddComponent<Rigidbody2D>();
        go_Pellet_1_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_5_bc = go_Pellet_1_5.AddComponent<BoxCollider2D>();
        go_Pellet_1_5_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_5_bc.isTrigger = true;
        var go_Pellet_1_5_sr = go_Pellet_1_5.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_5_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_5_sr.sharedMaterial = unlitMat;
        go_Pellet_1_5_sr.sortingOrder = 2;
        go_Pellet_1_5.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_5);

        // --- Pellet_1_6 ---
        var go_Pellet_1_6 = new GameObject("Pellet_1_6");
        go_Pellet_1_6.tag = "Pellet";
        go_Pellet_1_6.transform.position = new Vector3(-7.5f, 14.0f, 0.0f);
        var go_Pellet_1_6_rb = go_Pellet_1_6.AddComponent<Rigidbody2D>();
        go_Pellet_1_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_6_bc = go_Pellet_1_6.AddComponent<BoxCollider2D>();
        go_Pellet_1_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_6_bc.isTrigger = true;
        var go_Pellet_1_6_sr = go_Pellet_1_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_6_sr.sharedMaterial = unlitMat;
        go_Pellet_1_6_sr.sortingOrder = 2;
        go_Pellet_1_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_6);

        // --- Node_1_6 ---
        var go_Node_1_6 = new GameObject("Node_1_6");
        go_Node_1_6.transform.position = new Vector3(-7.5f, 14.0f, 0.0f);
        var go_Node_1_6_rb = go_Node_1_6.AddComponent<Rigidbody2D>();
        go_Node_1_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_1_6_bc = go_Node_1_6.AddComponent<BoxCollider2D>();
        go_Node_1_6_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_1_6_bc.isTrigger = true;
        go_Node_1_6.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_1_6);

        // --- Pellet_1_7 ---
        var go_Pellet_1_7 = new GameObject("Pellet_1_7");
        go_Pellet_1_7.tag = "Pellet";
        go_Pellet_1_7.transform.position = new Vector3(-6.5f, 14.0f, 0.0f);
        var go_Pellet_1_7_rb = go_Pellet_1_7.AddComponent<Rigidbody2D>();
        go_Pellet_1_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_7_bc = go_Pellet_1_7.AddComponent<BoxCollider2D>();
        go_Pellet_1_7_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_7_bc.isTrigger = true;
        var go_Pellet_1_7_sr = go_Pellet_1_7.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_7_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_7_sr.sharedMaterial = unlitMat;
        go_Pellet_1_7_sr.sortingOrder = 2;
        go_Pellet_1_7.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_7);

        // --- Pellet_1_8 ---
        var go_Pellet_1_8 = new GameObject("Pellet_1_8");
        go_Pellet_1_8.tag = "Pellet";
        go_Pellet_1_8.transform.position = new Vector3(-5.5f, 14.0f, 0.0f);
        var go_Pellet_1_8_rb = go_Pellet_1_8.AddComponent<Rigidbody2D>();
        go_Pellet_1_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_8_bc = go_Pellet_1_8.AddComponent<BoxCollider2D>();
        go_Pellet_1_8_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_8_bc.isTrigger = true;
        var go_Pellet_1_8_sr = go_Pellet_1_8.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_8_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_8_sr.sharedMaterial = unlitMat;
        go_Pellet_1_8_sr.sortingOrder = 2;
        go_Pellet_1_8.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_8);

        // --- Pellet_1_9 ---
        var go_Pellet_1_9 = new GameObject("Pellet_1_9");
        go_Pellet_1_9.tag = "Pellet";
        go_Pellet_1_9.transform.position = new Vector3(-4.5f, 14.0f, 0.0f);
        var go_Pellet_1_9_rb = go_Pellet_1_9.AddComponent<Rigidbody2D>();
        go_Pellet_1_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_9_bc = go_Pellet_1_9.AddComponent<BoxCollider2D>();
        go_Pellet_1_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_9_bc.isTrigger = true;
        var go_Pellet_1_9_sr = go_Pellet_1_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_9_sr.sharedMaterial = unlitMat;
        go_Pellet_1_9_sr.sortingOrder = 2;
        go_Pellet_1_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_9);

        // --- Pellet_1_10 ---
        var go_Pellet_1_10 = new GameObject("Pellet_1_10");
        go_Pellet_1_10.tag = "Pellet";
        go_Pellet_1_10.transform.position = new Vector3(-3.5f, 14.0f, 0.0f);
        var go_Pellet_1_10_rb = go_Pellet_1_10.AddComponent<Rigidbody2D>();
        go_Pellet_1_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_10_bc = go_Pellet_1_10.AddComponent<BoxCollider2D>();
        go_Pellet_1_10_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_10_bc.isTrigger = true;
        var go_Pellet_1_10_sr = go_Pellet_1_10.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_10_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_10_sr.sharedMaterial = unlitMat;
        go_Pellet_1_10_sr.sortingOrder = 2;
        go_Pellet_1_10.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_10);

        // --- Pellet_1_11 ---
        var go_Pellet_1_11 = new GameObject("Pellet_1_11");
        go_Pellet_1_11.tag = "Pellet";
        go_Pellet_1_11.transform.position = new Vector3(-2.5f, 14.0f, 0.0f);
        var go_Pellet_1_11_rb = go_Pellet_1_11.AddComponent<Rigidbody2D>();
        go_Pellet_1_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_11_bc = go_Pellet_1_11.AddComponent<BoxCollider2D>();
        go_Pellet_1_11_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_11_bc.isTrigger = true;
        var go_Pellet_1_11_sr = go_Pellet_1_11.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_11_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_11_sr.sharedMaterial = unlitMat;
        go_Pellet_1_11_sr.sortingOrder = 2;
        go_Pellet_1_11.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_11);

        // --- Pellet_1_12 ---
        var go_Pellet_1_12 = new GameObject("Pellet_1_12");
        go_Pellet_1_12.tag = "Pellet";
        go_Pellet_1_12.transform.position = new Vector3(-1.5f, 14.0f, 0.0f);
        var go_Pellet_1_12_rb = go_Pellet_1_12.AddComponent<Rigidbody2D>();
        go_Pellet_1_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_12_bc = go_Pellet_1_12.AddComponent<BoxCollider2D>();
        go_Pellet_1_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_12_bc.isTrigger = true;
        var go_Pellet_1_12_sr = go_Pellet_1_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_12_sr.sharedMaterial = unlitMat;
        go_Pellet_1_12_sr.sortingOrder = 2;
        go_Pellet_1_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_12);

        // --- Node_1_12 ---
        var go_Node_1_12 = new GameObject("Node_1_12");
        go_Node_1_12.transform.position = new Vector3(-1.5f, 14.0f, 0.0f);
        var go_Node_1_12_rb = go_Node_1_12.AddComponent<Rigidbody2D>();
        go_Node_1_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_1_12_bc = go_Node_1_12.AddComponent<BoxCollider2D>();
        go_Node_1_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_1_12_bc.isTrigger = true;
        go_Node_1_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_1_12);

        // --- Wall_1_13 ---
        var go_Wall_1_13 = new GameObject("Wall_1_13");
        go_Wall_1_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_1_13.transform.position = new Vector3(-0.5f, 14.0f, 0.0f);
        var go_Wall_1_13_rb = go_Wall_1_13.AddComponent<Rigidbody2D>();
        go_Wall_1_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_1_13_bc = go_Wall_1_13.AddComponent<BoxCollider2D>();
        go_Wall_1_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_1_13_sr = go_Wall_1_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_1_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_1_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_1_13);

        // --- Wall_1_14 ---
        var go_Wall_1_14 = new GameObject("Wall_1_14");
        go_Wall_1_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_1_14.transform.position = new Vector3(0.5f, 14.0f, 0.0f);
        var go_Wall_1_14_rb = go_Wall_1_14.AddComponent<Rigidbody2D>();
        go_Wall_1_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_1_14_bc = go_Wall_1_14.AddComponent<BoxCollider2D>();
        go_Wall_1_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_1_14_sr = go_Wall_1_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_1_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_1_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_1_14);

        // --- Pellet_1_15 ---
        var go_Pellet_1_15 = new GameObject("Pellet_1_15");
        go_Pellet_1_15.tag = "Pellet";
        go_Pellet_1_15.transform.position = new Vector3(1.5f, 14.0f, 0.0f);
        var go_Pellet_1_15_rb = go_Pellet_1_15.AddComponent<Rigidbody2D>();
        go_Pellet_1_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_15_bc = go_Pellet_1_15.AddComponent<BoxCollider2D>();
        go_Pellet_1_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_15_bc.isTrigger = true;
        var go_Pellet_1_15_sr = go_Pellet_1_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_15_sr.sharedMaterial = unlitMat;
        go_Pellet_1_15_sr.sortingOrder = 2;
        go_Pellet_1_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_15);

        // --- Node_1_15 ---
        var go_Node_1_15 = new GameObject("Node_1_15");
        go_Node_1_15.transform.position = new Vector3(1.5f, 14.0f, 0.0f);
        var go_Node_1_15_rb = go_Node_1_15.AddComponent<Rigidbody2D>();
        go_Node_1_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_1_15_bc = go_Node_1_15.AddComponent<BoxCollider2D>();
        go_Node_1_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_1_15_bc.isTrigger = true;
        go_Node_1_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_1_15);

        // --- Pellet_1_16 ---
        var go_Pellet_1_16 = new GameObject("Pellet_1_16");
        go_Pellet_1_16.tag = "Pellet";
        go_Pellet_1_16.transform.position = new Vector3(2.5f, 14.0f, 0.0f);
        var go_Pellet_1_16_rb = go_Pellet_1_16.AddComponent<Rigidbody2D>();
        go_Pellet_1_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_16_bc = go_Pellet_1_16.AddComponent<BoxCollider2D>();
        go_Pellet_1_16_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_16_bc.isTrigger = true;
        var go_Pellet_1_16_sr = go_Pellet_1_16.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_16_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_16_sr.sharedMaterial = unlitMat;
        go_Pellet_1_16_sr.sortingOrder = 2;
        go_Pellet_1_16.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_16);

        // --- Pellet_1_17 ---
        var go_Pellet_1_17 = new GameObject("Pellet_1_17");
        go_Pellet_1_17.tag = "Pellet";
        go_Pellet_1_17.transform.position = new Vector3(3.5f, 14.0f, 0.0f);
        var go_Pellet_1_17_rb = go_Pellet_1_17.AddComponent<Rigidbody2D>();
        go_Pellet_1_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_17_bc = go_Pellet_1_17.AddComponent<BoxCollider2D>();
        go_Pellet_1_17_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_17_bc.isTrigger = true;
        var go_Pellet_1_17_sr = go_Pellet_1_17.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_17_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_17_sr.sharedMaterial = unlitMat;
        go_Pellet_1_17_sr.sortingOrder = 2;
        go_Pellet_1_17.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_17);

        // --- Pellet_1_18 ---
        var go_Pellet_1_18 = new GameObject("Pellet_1_18");
        go_Pellet_1_18.tag = "Pellet";
        go_Pellet_1_18.transform.position = new Vector3(4.5f, 14.0f, 0.0f);
        var go_Pellet_1_18_rb = go_Pellet_1_18.AddComponent<Rigidbody2D>();
        go_Pellet_1_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_18_bc = go_Pellet_1_18.AddComponent<BoxCollider2D>();
        go_Pellet_1_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_18_bc.isTrigger = true;
        var go_Pellet_1_18_sr = go_Pellet_1_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_18_sr.sharedMaterial = unlitMat;
        go_Pellet_1_18_sr.sortingOrder = 2;
        go_Pellet_1_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_18);

        // --- Pellet_1_19 ---
        var go_Pellet_1_19 = new GameObject("Pellet_1_19");
        go_Pellet_1_19.tag = "Pellet";
        go_Pellet_1_19.transform.position = new Vector3(5.5f, 14.0f, 0.0f);
        var go_Pellet_1_19_rb = go_Pellet_1_19.AddComponent<Rigidbody2D>();
        go_Pellet_1_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_19_bc = go_Pellet_1_19.AddComponent<BoxCollider2D>();
        go_Pellet_1_19_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_19_bc.isTrigger = true;
        var go_Pellet_1_19_sr = go_Pellet_1_19.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_19_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_19_sr.sharedMaterial = unlitMat;
        go_Pellet_1_19_sr.sortingOrder = 2;
        go_Pellet_1_19.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_19);

        // --- Pellet_1_20 ---
        var go_Pellet_1_20 = new GameObject("Pellet_1_20");
        go_Pellet_1_20.tag = "Pellet";
        go_Pellet_1_20.transform.position = new Vector3(6.5f, 14.0f, 0.0f);
        var go_Pellet_1_20_rb = go_Pellet_1_20.AddComponent<Rigidbody2D>();
        go_Pellet_1_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_20_bc = go_Pellet_1_20.AddComponent<BoxCollider2D>();
        go_Pellet_1_20_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_20_bc.isTrigger = true;
        var go_Pellet_1_20_sr = go_Pellet_1_20.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_20_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_20_sr.sharedMaterial = unlitMat;
        go_Pellet_1_20_sr.sortingOrder = 2;
        go_Pellet_1_20.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_20);

        // --- Pellet_1_21 ---
        var go_Pellet_1_21 = new GameObject("Pellet_1_21");
        go_Pellet_1_21.tag = "Pellet";
        go_Pellet_1_21.transform.position = new Vector3(7.5f, 14.0f, 0.0f);
        var go_Pellet_1_21_rb = go_Pellet_1_21.AddComponent<Rigidbody2D>();
        go_Pellet_1_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_21_bc = go_Pellet_1_21.AddComponent<BoxCollider2D>();
        go_Pellet_1_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_21_bc.isTrigger = true;
        var go_Pellet_1_21_sr = go_Pellet_1_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_21_sr.sharedMaterial = unlitMat;
        go_Pellet_1_21_sr.sortingOrder = 2;
        go_Pellet_1_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_21);

        // --- Node_1_21 ---
        var go_Node_1_21 = new GameObject("Node_1_21");
        go_Node_1_21.transform.position = new Vector3(7.5f, 14.0f, 0.0f);
        var go_Node_1_21_rb = go_Node_1_21.AddComponent<Rigidbody2D>();
        go_Node_1_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_1_21_bc = go_Node_1_21.AddComponent<BoxCollider2D>();
        go_Node_1_21_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_1_21_bc.isTrigger = true;
        go_Node_1_21.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_1_21);

        // --- Pellet_1_22 ---
        var go_Pellet_1_22 = new GameObject("Pellet_1_22");
        go_Pellet_1_22.tag = "Pellet";
        go_Pellet_1_22.transform.position = new Vector3(8.5f, 14.0f, 0.0f);
        var go_Pellet_1_22_rb = go_Pellet_1_22.AddComponent<Rigidbody2D>();
        go_Pellet_1_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_22_bc = go_Pellet_1_22.AddComponent<BoxCollider2D>();
        go_Pellet_1_22_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_22_bc.isTrigger = true;
        var go_Pellet_1_22_sr = go_Pellet_1_22.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_22_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_22_sr.sharedMaterial = unlitMat;
        go_Pellet_1_22_sr.sortingOrder = 2;
        go_Pellet_1_22.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_22);

        // --- Pellet_1_23 ---
        var go_Pellet_1_23 = new GameObject("Pellet_1_23");
        go_Pellet_1_23.tag = "Pellet";
        go_Pellet_1_23.transform.position = new Vector3(9.5f, 14.0f, 0.0f);
        var go_Pellet_1_23_rb = go_Pellet_1_23.AddComponent<Rigidbody2D>();
        go_Pellet_1_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_23_bc = go_Pellet_1_23.AddComponent<BoxCollider2D>();
        go_Pellet_1_23_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_23_bc.isTrigger = true;
        var go_Pellet_1_23_sr = go_Pellet_1_23.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_23_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_23_sr.sharedMaterial = unlitMat;
        go_Pellet_1_23_sr.sortingOrder = 2;
        go_Pellet_1_23.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_23);

        // --- Pellet_1_24 ---
        var go_Pellet_1_24 = new GameObject("Pellet_1_24");
        go_Pellet_1_24.tag = "Pellet";
        go_Pellet_1_24.transform.position = new Vector3(10.5f, 14.0f, 0.0f);
        var go_Pellet_1_24_rb = go_Pellet_1_24.AddComponent<Rigidbody2D>();
        go_Pellet_1_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_24_bc = go_Pellet_1_24.AddComponent<BoxCollider2D>();
        go_Pellet_1_24_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_24_bc.isTrigger = true;
        var go_Pellet_1_24_sr = go_Pellet_1_24.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_24_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_24_sr.sharedMaterial = unlitMat;
        go_Pellet_1_24_sr.sortingOrder = 2;
        go_Pellet_1_24.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_24);

        // --- Pellet_1_25 ---
        var go_Pellet_1_25 = new GameObject("Pellet_1_25");
        go_Pellet_1_25.tag = "Pellet";
        go_Pellet_1_25.transform.position = new Vector3(11.5f, 14.0f, 0.0f);
        var go_Pellet_1_25_rb = go_Pellet_1_25.AddComponent<Rigidbody2D>();
        go_Pellet_1_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_25_bc = go_Pellet_1_25.AddComponent<BoxCollider2D>();
        go_Pellet_1_25_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_25_bc.isTrigger = true;
        var go_Pellet_1_25_sr = go_Pellet_1_25.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_25_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_25_sr.sharedMaterial = unlitMat;
        go_Pellet_1_25_sr.sortingOrder = 2;
        go_Pellet_1_25.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_25);

        // --- Pellet_1_26 ---
        var go_Pellet_1_26 = new GameObject("Pellet_1_26");
        go_Pellet_1_26.tag = "Pellet";
        go_Pellet_1_26.transform.position = new Vector3(12.5f, 14.0f, 0.0f);
        var go_Pellet_1_26_rb = go_Pellet_1_26.AddComponent<Rigidbody2D>();
        go_Pellet_1_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_1_26_bc = go_Pellet_1_26.AddComponent<BoxCollider2D>();
        go_Pellet_1_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_1_26_bc.isTrigger = true;
        var go_Pellet_1_26_sr = go_Pellet_1_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_1_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_1_26_sr.sharedMaterial = unlitMat;
        go_Pellet_1_26_sr.sortingOrder = 2;
        go_Pellet_1_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_1_26);

        // --- Node_1_26 ---
        var go_Node_1_26 = new GameObject("Node_1_26");
        go_Node_1_26.transform.position = new Vector3(12.5f, 14.0f, 0.0f);
        var go_Node_1_26_rb = go_Node_1_26.AddComponent<Rigidbody2D>();
        go_Node_1_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_1_26_bc = go_Node_1_26.AddComponent<BoxCollider2D>();
        go_Node_1_26_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_1_26_bc.isTrigger = true;
        go_Node_1_26.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_1_26);

        // --- Wall_1_27 ---
        var go_Wall_1_27 = new GameObject("Wall_1_27");
        go_Wall_1_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_1_27.transform.position = new Vector3(13.5f, 14.0f, 0.0f);
        var go_Wall_1_27_rb = go_Wall_1_27.AddComponent<Rigidbody2D>();
        go_Wall_1_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_1_27_bc = go_Wall_1_27.AddComponent<BoxCollider2D>();
        go_Wall_1_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_1_27_sr = go_Wall_1_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_1_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_1_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_1_27);

        // --- Wall_2_0 ---
        var go_Wall_2_0 = new GameObject("Wall_2_0");
        go_Wall_2_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_0.transform.position = new Vector3(-13.5f, 13.0f, 0.0f);
        var go_Wall_2_0_rb = go_Wall_2_0.AddComponent<Rigidbody2D>();
        go_Wall_2_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_0_bc = go_Wall_2_0.AddComponent<BoxCollider2D>();
        go_Wall_2_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_0_sr = go_Wall_2_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_0);

        // --- Pellet_2_1 ---
        var go_Pellet_2_1 = new GameObject("Pellet_2_1");
        go_Pellet_2_1.tag = "Pellet";
        go_Pellet_2_1.transform.position = new Vector3(-12.5f, 13.0f, 0.0f);
        var go_Pellet_2_1_rb = go_Pellet_2_1.AddComponent<Rigidbody2D>();
        go_Pellet_2_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_2_1_bc = go_Pellet_2_1.AddComponent<BoxCollider2D>();
        go_Pellet_2_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_2_1_bc.isTrigger = true;
        var go_Pellet_2_1_sr = go_Pellet_2_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_2_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_2_1_sr.sharedMaterial = unlitMat;
        go_Pellet_2_1_sr.sortingOrder = 2;
        go_Pellet_2_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_2_1);

        // --- Wall_2_2 ---
        var go_Wall_2_2 = new GameObject("Wall_2_2");
        go_Wall_2_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_2.transform.position = new Vector3(-11.5f, 13.0f, 0.0f);
        var go_Wall_2_2_rb = go_Wall_2_2.AddComponent<Rigidbody2D>();
        go_Wall_2_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_2_bc = go_Wall_2_2.AddComponent<BoxCollider2D>();
        go_Wall_2_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_2_sr = go_Wall_2_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_2);

        // --- Wall_2_3 ---
        var go_Wall_2_3 = new GameObject("Wall_2_3");
        go_Wall_2_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_3.transform.position = new Vector3(-10.5f, 13.0f, 0.0f);
        var go_Wall_2_3_rb = go_Wall_2_3.AddComponent<Rigidbody2D>();
        go_Wall_2_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_3_bc = go_Wall_2_3.AddComponent<BoxCollider2D>();
        go_Wall_2_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_3_sr = go_Wall_2_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_3);

        // --- Wall_2_4 ---
        var go_Wall_2_4 = new GameObject("Wall_2_4");
        go_Wall_2_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_4.transform.position = new Vector3(-9.5f, 13.0f, 0.0f);
        var go_Wall_2_4_rb = go_Wall_2_4.AddComponent<Rigidbody2D>();
        go_Wall_2_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_4_bc = go_Wall_2_4.AddComponent<BoxCollider2D>();
        go_Wall_2_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_4_sr = go_Wall_2_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_4);

        // --- Wall_2_5 ---
        var go_Wall_2_5 = new GameObject("Wall_2_5");
        go_Wall_2_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_5.transform.position = new Vector3(-8.5f, 13.0f, 0.0f);
        var go_Wall_2_5_rb = go_Wall_2_5.AddComponent<Rigidbody2D>();
        go_Wall_2_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_5_bc = go_Wall_2_5.AddComponent<BoxCollider2D>();
        go_Wall_2_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_5_sr = go_Wall_2_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_5);

        // --- Pellet_2_6 ---
        var go_Pellet_2_6 = new GameObject("Pellet_2_6");
        go_Pellet_2_6.tag = "Pellet";
        go_Pellet_2_6.transform.position = new Vector3(-7.5f, 13.0f, 0.0f);
        var go_Pellet_2_6_rb = go_Pellet_2_6.AddComponent<Rigidbody2D>();
        go_Pellet_2_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_2_6_bc = go_Pellet_2_6.AddComponent<BoxCollider2D>();
        go_Pellet_2_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_2_6_bc.isTrigger = true;
        var go_Pellet_2_6_sr = go_Pellet_2_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_2_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_2_6_sr.sharedMaterial = unlitMat;
        go_Pellet_2_6_sr.sortingOrder = 2;
        go_Pellet_2_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_2_6);

        // --- Wall_2_7 ---
        var go_Wall_2_7 = new GameObject("Wall_2_7");
        go_Wall_2_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_7.transform.position = new Vector3(-6.5f, 13.0f, 0.0f);
        var go_Wall_2_7_rb = go_Wall_2_7.AddComponent<Rigidbody2D>();
        go_Wall_2_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_7_bc = go_Wall_2_7.AddComponent<BoxCollider2D>();
        go_Wall_2_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_7_sr = go_Wall_2_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_7);

        // --- Wall_2_8 ---
        var go_Wall_2_8 = new GameObject("Wall_2_8");
        go_Wall_2_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_8.transform.position = new Vector3(-5.5f, 13.0f, 0.0f);
        var go_Wall_2_8_rb = go_Wall_2_8.AddComponent<Rigidbody2D>();
        go_Wall_2_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_8_bc = go_Wall_2_8.AddComponent<BoxCollider2D>();
        go_Wall_2_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_8_sr = go_Wall_2_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_8);

        // --- Wall_2_9 ---
        var go_Wall_2_9 = new GameObject("Wall_2_9");
        go_Wall_2_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_9.transform.position = new Vector3(-4.5f, 13.0f, 0.0f);
        var go_Wall_2_9_rb = go_Wall_2_9.AddComponent<Rigidbody2D>();
        go_Wall_2_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_9_bc = go_Wall_2_9.AddComponent<BoxCollider2D>();
        go_Wall_2_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_9_sr = go_Wall_2_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_9);

        // --- Wall_2_10 ---
        var go_Wall_2_10 = new GameObject("Wall_2_10");
        go_Wall_2_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_10.transform.position = new Vector3(-3.5f, 13.0f, 0.0f);
        var go_Wall_2_10_rb = go_Wall_2_10.AddComponent<Rigidbody2D>();
        go_Wall_2_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_10_bc = go_Wall_2_10.AddComponent<BoxCollider2D>();
        go_Wall_2_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_10_sr = go_Wall_2_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_10);

        // --- Wall_2_11 ---
        var go_Wall_2_11 = new GameObject("Wall_2_11");
        go_Wall_2_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_11.transform.position = new Vector3(-2.5f, 13.0f, 0.0f);
        var go_Wall_2_11_rb = go_Wall_2_11.AddComponent<Rigidbody2D>();
        go_Wall_2_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_11_bc = go_Wall_2_11.AddComponent<BoxCollider2D>();
        go_Wall_2_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_11_sr = go_Wall_2_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_11);

        // --- Pellet_2_12 ---
        var go_Pellet_2_12 = new GameObject("Pellet_2_12");
        go_Pellet_2_12.tag = "Pellet";
        go_Pellet_2_12.transform.position = new Vector3(-1.5f, 13.0f, 0.0f);
        var go_Pellet_2_12_rb = go_Pellet_2_12.AddComponent<Rigidbody2D>();
        go_Pellet_2_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_2_12_bc = go_Pellet_2_12.AddComponent<BoxCollider2D>();
        go_Pellet_2_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_2_12_bc.isTrigger = true;
        var go_Pellet_2_12_sr = go_Pellet_2_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_2_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_2_12_sr.sharedMaterial = unlitMat;
        go_Pellet_2_12_sr.sortingOrder = 2;
        go_Pellet_2_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_2_12);

        // --- Wall_2_13 ---
        var go_Wall_2_13 = new GameObject("Wall_2_13");
        go_Wall_2_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_13.transform.position = new Vector3(-0.5f, 13.0f, 0.0f);
        var go_Wall_2_13_rb = go_Wall_2_13.AddComponent<Rigidbody2D>();
        go_Wall_2_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_13_bc = go_Wall_2_13.AddComponent<BoxCollider2D>();
        go_Wall_2_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_13_sr = go_Wall_2_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_13);

        // --- Wall_2_14 ---
        var go_Wall_2_14 = new GameObject("Wall_2_14");
        go_Wall_2_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_14.transform.position = new Vector3(0.5f, 13.0f, 0.0f);
        var go_Wall_2_14_rb = go_Wall_2_14.AddComponent<Rigidbody2D>();
        go_Wall_2_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_14_bc = go_Wall_2_14.AddComponent<BoxCollider2D>();
        go_Wall_2_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_14_sr = go_Wall_2_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_14);

        // --- Pellet_2_15 ---
        var go_Pellet_2_15 = new GameObject("Pellet_2_15");
        go_Pellet_2_15.tag = "Pellet";
        go_Pellet_2_15.transform.position = new Vector3(1.5f, 13.0f, 0.0f);
        var go_Pellet_2_15_rb = go_Pellet_2_15.AddComponent<Rigidbody2D>();
        go_Pellet_2_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_2_15_bc = go_Pellet_2_15.AddComponent<BoxCollider2D>();
        go_Pellet_2_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_2_15_bc.isTrigger = true;
        var go_Pellet_2_15_sr = go_Pellet_2_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_2_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_2_15_sr.sharedMaterial = unlitMat;
        go_Pellet_2_15_sr.sortingOrder = 2;
        go_Pellet_2_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_2_15);

        // --- Wall_2_16 ---
        var go_Wall_2_16 = new GameObject("Wall_2_16");
        go_Wall_2_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_16.transform.position = new Vector3(2.5f, 13.0f, 0.0f);
        var go_Wall_2_16_rb = go_Wall_2_16.AddComponent<Rigidbody2D>();
        go_Wall_2_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_16_bc = go_Wall_2_16.AddComponent<BoxCollider2D>();
        go_Wall_2_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_16_sr = go_Wall_2_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_16);

        // --- Wall_2_17 ---
        var go_Wall_2_17 = new GameObject("Wall_2_17");
        go_Wall_2_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_17.transform.position = new Vector3(3.5f, 13.0f, 0.0f);
        var go_Wall_2_17_rb = go_Wall_2_17.AddComponent<Rigidbody2D>();
        go_Wall_2_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_17_bc = go_Wall_2_17.AddComponent<BoxCollider2D>();
        go_Wall_2_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_17_sr = go_Wall_2_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_17);

        // --- Wall_2_18 ---
        var go_Wall_2_18 = new GameObject("Wall_2_18");
        go_Wall_2_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_18.transform.position = new Vector3(4.5f, 13.0f, 0.0f);
        var go_Wall_2_18_rb = go_Wall_2_18.AddComponent<Rigidbody2D>();
        go_Wall_2_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_18_bc = go_Wall_2_18.AddComponent<BoxCollider2D>();
        go_Wall_2_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_18_sr = go_Wall_2_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_18);

        // --- Wall_2_19 ---
        var go_Wall_2_19 = new GameObject("Wall_2_19");
        go_Wall_2_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_19.transform.position = new Vector3(5.5f, 13.0f, 0.0f);
        var go_Wall_2_19_rb = go_Wall_2_19.AddComponent<Rigidbody2D>();
        go_Wall_2_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_19_bc = go_Wall_2_19.AddComponent<BoxCollider2D>();
        go_Wall_2_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_19_sr = go_Wall_2_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_19);

        // --- Wall_2_20 ---
        var go_Wall_2_20 = new GameObject("Wall_2_20");
        go_Wall_2_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_20.transform.position = new Vector3(6.5f, 13.0f, 0.0f);
        var go_Wall_2_20_rb = go_Wall_2_20.AddComponent<Rigidbody2D>();
        go_Wall_2_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_20_bc = go_Wall_2_20.AddComponent<BoxCollider2D>();
        go_Wall_2_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_20_sr = go_Wall_2_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_20);

        // --- Pellet_2_21 ---
        var go_Pellet_2_21 = new GameObject("Pellet_2_21");
        go_Pellet_2_21.tag = "Pellet";
        go_Pellet_2_21.transform.position = new Vector3(7.5f, 13.0f, 0.0f);
        var go_Pellet_2_21_rb = go_Pellet_2_21.AddComponent<Rigidbody2D>();
        go_Pellet_2_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_2_21_bc = go_Pellet_2_21.AddComponent<BoxCollider2D>();
        go_Pellet_2_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_2_21_bc.isTrigger = true;
        var go_Pellet_2_21_sr = go_Pellet_2_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_2_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_2_21_sr.sharedMaterial = unlitMat;
        go_Pellet_2_21_sr.sortingOrder = 2;
        go_Pellet_2_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_2_21);

        // --- Wall_2_22 ---
        var go_Wall_2_22 = new GameObject("Wall_2_22");
        go_Wall_2_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_22.transform.position = new Vector3(8.5f, 13.0f, 0.0f);
        var go_Wall_2_22_rb = go_Wall_2_22.AddComponent<Rigidbody2D>();
        go_Wall_2_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_22_bc = go_Wall_2_22.AddComponent<BoxCollider2D>();
        go_Wall_2_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_22_sr = go_Wall_2_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_22);

        // --- Wall_2_23 ---
        var go_Wall_2_23 = new GameObject("Wall_2_23");
        go_Wall_2_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_23.transform.position = new Vector3(9.5f, 13.0f, 0.0f);
        var go_Wall_2_23_rb = go_Wall_2_23.AddComponent<Rigidbody2D>();
        go_Wall_2_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_23_bc = go_Wall_2_23.AddComponent<BoxCollider2D>();
        go_Wall_2_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_23_sr = go_Wall_2_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_23);

        // --- Wall_2_24 ---
        var go_Wall_2_24 = new GameObject("Wall_2_24");
        go_Wall_2_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_24.transform.position = new Vector3(10.5f, 13.0f, 0.0f);
        var go_Wall_2_24_rb = go_Wall_2_24.AddComponent<Rigidbody2D>();
        go_Wall_2_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_24_bc = go_Wall_2_24.AddComponent<BoxCollider2D>();
        go_Wall_2_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_24_sr = go_Wall_2_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_24);

        // --- Wall_2_25 ---
        var go_Wall_2_25 = new GameObject("Wall_2_25");
        go_Wall_2_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_25.transform.position = new Vector3(11.5f, 13.0f, 0.0f);
        var go_Wall_2_25_rb = go_Wall_2_25.AddComponent<Rigidbody2D>();
        go_Wall_2_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_25_bc = go_Wall_2_25.AddComponent<BoxCollider2D>();
        go_Wall_2_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_25_sr = go_Wall_2_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_25);

        // --- Pellet_2_26 ---
        var go_Pellet_2_26 = new GameObject("Pellet_2_26");
        go_Pellet_2_26.tag = "Pellet";
        go_Pellet_2_26.transform.position = new Vector3(12.5f, 13.0f, 0.0f);
        var go_Pellet_2_26_rb = go_Pellet_2_26.AddComponent<Rigidbody2D>();
        go_Pellet_2_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_2_26_bc = go_Pellet_2_26.AddComponent<BoxCollider2D>();
        go_Pellet_2_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_2_26_bc.isTrigger = true;
        var go_Pellet_2_26_sr = go_Pellet_2_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_2_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_2_26_sr.sharedMaterial = unlitMat;
        go_Pellet_2_26_sr.sortingOrder = 2;
        go_Pellet_2_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_2_26);

        // --- Wall_2_27 ---
        var go_Wall_2_27 = new GameObject("Wall_2_27");
        go_Wall_2_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_2_27.transform.position = new Vector3(13.5f, 13.0f, 0.0f);
        var go_Wall_2_27_rb = go_Wall_2_27.AddComponent<Rigidbody2D>();
        go_Wall_2_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_2_27_bc = go_Wall_2_27.AddComponent<BoxCollider2D>();
        go_Wall_2_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_2_27_sr = go_Wall_2_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_2_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_2_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_2_27);

        // --- Wall_3_0 ---
        var go_Wall_3_0 = new GameObject("Wall_3_0");
        go_Wall_3_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_0.transform.position = new Vector3(-13.5f, 12.0f, 0.0f);
        var go_Wall_3_0_rb = go_Wall_3_0.AddComponent<Rigidbody2D>();
        go_Wall_3_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_0_bc = go_Wall_3_0.AddComponent<BoxCollider2D>();
        go_Wall_3_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_0_sr = go_Wall_3_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_0);

        // --- Pellet_3_1 ---
        var go_Pellet_3_1 = new GameObject("Pellet_3_1");
        go_Pellet_3_1.tag = "PowerPellet";
        go_Pellet_3_1.transform.position = new Vector3(-12.5f, 12.0f, 0.0f);
        var go_Pellet_3_1_rb = go_Pellet_3_1.AddComponent<Rigidbody2D>();
        go_Pellet_3_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_3_1_bc = go_Pellet_3_1.AddComponent<BoxCollider2D>();
        go_Pellet_3_1_bc.size = new Vector2(0.5f, 0.5f);
        go_Pellet_3_1_bc.isTrigger = true;
        var go_Pellet_3_1_sr = go_Pellet_3_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_large != null) go_Pellet_3_1_sr.sprite = sprite_pellet_large;
        if (unlitMat != null) go_Pellet_3_1_sr.sharedMaterial = unlitMat;
        go_Pellet_3_1_sr.sortingOrder = 2;
        go_Pellet_3_1.AddComponent<PowerPellet>();
        // PowerPellet.duration = 8.0
        // PowerPellet.points = 50
        EditorUtility.SetDirty(go_Pellet_3_1);

        // --- Wall_3_2 ---
        var go_Wall_3_2 = new GameObject("Wall_3_2");
        go_Wall_3_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_2.transform.position = new Vector3(-11.5f, 12.0f, 0.0f);
        var go_Wall_3_2_rb = go_Wall_3_2.AddComponent<Rigidbody2D>();
        go_Wall_3_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_2_bc = go_Wall_3_2.AddComponent<BoxCollider2D>();
        go_Wall_3_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_2_sr = go_Wall_3_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_2);

        // --- Wall_3_3 ---
        var go_Wall_3_3 = new GameObject("Wall_3_3");
        go_Wall_3_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_3.transform.position = new Vector3(-10.5f, 12.0f, 0.0f);
        var go_Wall_3_3_rb = go_Wall_3_3.AddComponent<Rigidbody2D>();
        go_Wall_3_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_3_bc = go_Wall_3_3.AddComponent<BoxCollider2D>();
        go_Wall_3_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_3_sr = go_Wall_3_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_3);

        // --- Wall_3_4 ---
        var go_Wall_3_4 = new GameObject("Wall_3_4");
        go_Wall_3_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_4.transform.position = new Vector3(-9.5f, 12.0f, 0.0f);
        var go_Wall_3_4_rb = go_Wall_3_4.AddComponent<Rigidbody2D>();
        go_Wall_3_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_4_bc = go_Wall_3_4.AddComponent<BoxCollider2D>();
        go_Wall_3_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_4_sr = go_Wall_3_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_4);

        // --- Wall_3_5 ---
        var go_Wall_3_5 = new GameObject("Wall_3_5");
        go_Wall_3_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_5.transform.position = new Vector3(-8.5f, 12.0f, 0.0f);
        var go_Wall_3_5_rb = go_Wall_3_5.AddComponent<Rigidbody2D>();
        go_Wall_3_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_5_bc = go_Wall_3_5.AddComponent<BoxCollider2D>();
        go_Wall_3_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_5_sr = go_Wall_3_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_5);

        // --- Pellet_3_6 ---
        var go_Pellet_3_6 = new GameObject("Pellet_3_6");
        go_Pellet_3_6.tag = "Pellet";
        go_Pellet_3_6.transform.position = new Vector3(-7.5f, 12.0f, 0.0f);
        var go_Pellet_3_6_rb = go_Pellet_3_6.AddComponent<Rigidbody2D>();
        go_Pellet_3_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_3_6_bc = go_Pellet_3_6.AddComponent<BoxCollider2D>();
        go_Pellet_3_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_3_6_bc.isTrigger = true;
        var go_Pellet_3_6_sr = go_Pellet_3_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_3_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_3_6_sr.sharedMaterial = unlitMat;
        go_Pellet_3_6_sr.sortingOrder = 2;
        go_Pellet_3_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_3_6);

        // --- Wall_3_7 ---
        var go_Wall_3_7 = new GameObject("Wall_3_7");
        go_Wall_3_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_7.transform.position = new Vector3(-6.5f, 12.0f, 0.0f);
        var go_Wall_3_7_rb = go_Wall_3_7.AddComponent<Rigidbody2D>();
        go_Wall_3_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_7_bc = go_Wall_3_7.AddComponent<BoxCollider2D>();
        go_Wall_3_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_7_sr = go_Wall_3_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_7);

        // --- Wall_3_8 ---
        var go_Wall_3_8 = new GameObject("Wall_3_8");
        go_Wall_3_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_8.transform.position = new Vector3(-5.5f, 12.0f, 0.0f);
        var go_Wall_3_8_rb = go_Wall_3_8.AddComponent<Rigidbody2D>();
        go_Wall_3_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_8_bc = go_Wall_3_8.AddComponent<BoxCollider2D>();
        go_Wall_3_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_8_sr = go_Wall_3_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_8);

        // --- Wall_3_9 ---
        var go_Wall_3_9 = new GameObject("Wall_3_9");
        go_Wall_3_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_9.transform.position = new Vector3(-4.5f, 12.0f, 0.0f);
        var go_Wall_3_9_rb = go_Wall_3_9.AddComponent<Rigidbody2D>();
        go_Wall_3_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_9_bc = go_Wall_3_9.AddComponent<BoxCollider2D>();
        go_Wall_3_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_9_sr = go_Wall_3_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_9);

        // --- Wall_3_10 ---
        var go_Wall_3_10 = new GameObject("Wall_3_10");
        go_Wall_3_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_10.transform.position = new Vector3(-3.5f, 12.0f, 0.0f);
        var go_Wall_3_10_rb = go_Wall_3_10.AddComponent<Rigidbody2D>();
        go_Wall_3_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_10_bc = go_Wall_3_10.AddComponent<BoxCollider2D>();
        go_Wall_3_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_10_sr = go_Wall_3_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_10);

        // --- Wall_3_11 ---
        var go_Wall_3_11 = new GameObject("Wall_3_11");
        go_Wall_3_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_11.transform.position = new Vector3(-2.5f, 12.0f, 0.0f);
        var go_Wall_3_11_rb = go_Wall_3_11.AddComponent<Rigidbody2D>();
        go_Wall_3_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_11_bc = go_Wall_3_11.AddComponent<BoxCollider2D>();
        go_Wall_3_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_11_sr = go_Wall_3_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_11);

        // --- Pellet_3_12 ---
        var go_Pellet_3_12 = new GameObject("Pellet_3_12");
        go_Pellet_3_12.tag = "Pellet";
        go_Pellet_3_12.transform.position = new Vector3(-1.5f, 12.0f, 0.0f);
        var go_Pellet_3_12_rb = go_Pellet_3_12.AddComponent<Rigidbody2D>();
        go_Pellet_3_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_3_12_bc = go_Pellet_3_12.AddComponent<BoxCollider2D>();
        go_Pellet_3_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_3_12_bc.isTrigger = true;
        var go_Pellet_3_12_sr = go_Pellet_3_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_3_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_3_12_sr.sharedMaterial = unlitMat;
        go_Pellet_3_12_sr.sortingOrder = 2;
        go_Pellet_3_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_3_12);

        // --- Wall_3_13 ---
        var go_Wall_3_13 = new GameObject("Wall_3_13");
        go_Wall_3_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_13.transform.position = new Vector3(-0.5f, 12.0f, 0.0f);
        var go_Wall_3_13_rb = go_Wall_3_13.AddComponent<Rigidbody2D>();
        go_Wall_3_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_13_bc = go_Wall_3_13.AddComponent<BoxCollider2D>();
        go_Wall_3_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_13_sr = go_Wall_3_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_13);

        // --- Wall_3_14 ---
        var go_Wall_3_14 = new GameObject("Wall_3_14");
        go_Wall_3_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_14.transform.position = new Vector3(0.5f, 12.0f, 0.0f);
        var go_Wall_3_14_rb = go_Wall_3_14.AddComponent<Rigidbody2D>();
        go_Wall_3_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_14_bc = go_Wall_3_14.AddComponent<BoxCollider2D>();
        go_Wall_3_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_14_sr = go_Wall_3_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_14);

        // --- Pellet_3_15 ---
        var go_Pellet_3_15 = new GameObject("Pellet_3_15");
        go_Pellet_3_15.tag = "Pellet";
        go_Pellet_3_15.transform.position = new Vector3(1.5f, 12.0f, 0.0f);
        var go_Pellet_3_15_rb = go_Pellet_3_15.AddComponent<Rigidbody2D>();
        go_Pellet_3_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_3_15_bc = go_Pellet_3_15.AddComponent<BoxCollider2D>();
        go_Pellet_3_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_3_15_bc.isTrigger = true;
        var go_Pellet_3_15_sr = go_Pellet_3_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_3_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_3_15_sr.sharedMaterial = unlitMat;
        go_Pellet_3_15_sr.sortingOrder = 2;
        go_Pellet_3_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_3_15);

        // --- Wall_3_16 ---
        var go_Wall_3_16 = new GameObject("Wall_3_16");
        go_Wall_3_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_16.transform.position = new Vector3(2.5f, 12.0f, 0.0f);
        var go_Wall_3_16_rb = go_Wall_3_16.AddComponent<Rigidbody2D>();
        go_Wall_3_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_16_bc = go_Wall_3_16.AddComponent<BoxCollider2D>();
        go_Wall_3_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_16_sr = go_Wall_3_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_16);

        // --- Wall_3_17 ---
        var go_Wall_3_17 = new GameObject("Wall_3_17");
        go_Wall_3_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_17.transform.position = new Vector3(3.5f, 12.0f, 0.0f);
        var go_Wall_3_17_rb = go_Wall_3_17.AddComponent<Rigidbody2D>();
        go_Wall_3_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_17_bc = go_Wall_3_17.AddComponent<BoxCollider2D>();
        go_Wall_3_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_17_sr = go_Wall_3_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_17);

        // --- Wall_3_18 ---
        var go_Wall_3_18 = new GameObject("Wall_3_18");
        go_Wall_3_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_18.transform.position = new Vector3(4.5f, 12.0f, 0.0f);
        var go_Wall_3_18_rb = go_Wall_3_18.AddComponent<Rigidbody2D>();
        go_Wall_3_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_18_bc = go_Wall_3_18.AddComponent<BoxCollider2D>();
        go_Wall_3_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_18_sr = go_Wall_3_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_18);

        // --- Wall_3_19 ---
        var go_Wall_3_19 = new GameObject("Wall_3_19");
        go_Wall_3_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_19.transform.position = new Vector3(5.5f, 12.0f, 0.0f);
        var go_Wall_3_19_rb = go_Wall_3_19.AddComponent<Rigidbody2D>();
        go_Wall_3_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_19_bc = go_Wall_3_19.AddComponent<BoxCollider2D>();
        go_Wall_3_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_19_sr = go_Wall_3_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_19);

        // --- Wall_3_20 ---
        var go_Wall_3_20 = new GameObject("Wall_3_20");
        go_Wall_3_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_20.transform.position = new Vector3(6.5f, 12.0f, 0.0f);
        var go_Wall_3_20_rb = go_Wall_3_20.AddComponent<Rigidbody2D>();
        go_Wall_3_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_20_bc = go_Wall_3_20.AddComponent<BoxCollider2D>();
        go_Wall_3_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_20_sr = go_Wall_3_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_20);

        // --- Pellet_3_21 ---
        var go_Pellet_3_21 = new GameObject("Pellet_3_21");
        go_Pellet_3_21.tag = "Pellet";
        go_Pellet_3_21.transform.position = new Vector3(7.5f, 12.0f, 0.0f);
        var go_Pellet_3_21_rb = go_Pellet_3_21.AddComponent<Rigidbody2D>();
        go_Pellet_3_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_3_21_bc = go_Pellet_3_21.AddComponent<BoxCollider2D>();
        go_Pellet_3_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_3_21_bc.isTrigger = true;
        var go_Pellet_3_21_sr = go_Pellet_3_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_3_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_3_21_sr.sharedMaterial = unlitMat;
        go_Pellet_3_21_sr.sortingOrder = 2;
        go_Pellet_3_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_3_21);

        // --- Wall_3_22 ---
        var go_Wall_3_22 = new GameObject("Wall_3_22");
        go_Wall_3_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_22.transform.position = new Vector3(8.5f, 12.0f, 0.0f);
        var go_Wall_3_22_rb = go_Wall_3_22.AddComponent<Rigidbody2D>();
        go_Wall_3_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_22_bc = go_Wall_3_22.AddComponent<BoxCollider2D>();
        go_Wall_3_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_22_sr = go_Wall_3_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_22);

        // --- Wall_3_23 ---
        var go_Wall_3_23 = new GameObject("Wall_3_23");
        go_Wall_3_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_23.transform.position = new Vector3(9.5f, 12.0f, 0.0f);
        var go_Wall_3_23_rb = go_Wall_3_23.AddComponent<Rigidbody2D>();
        go_Wall_3_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_23_bc = go_Wall_3_23.AddComponent<BoxCollider2D>();
        go_Wall_3_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_23_sr = go_Wall_3_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_23);

        // --- Wall_3_24 ---
        var go_Wall_3_24 = new GameObject("Wall_3_24");
        go_Wall_3_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_24.transform.position = new Vector3(10.5f, 12.0f, 0.0f);
        var go_Wall_3_24_rb = go_Wall_3_24.AddComponent<Rigidbody2D>();
        go_Wall_3_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_24_bc = go_Wall_3_24.AddComponent<BoxCollider2D>();
        go_Wall_3_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_24_sr = go_Wall_3_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_24);

        // --- Wall_3_25 ---
        var go_Wall_3_25 = new GameObject("Wall_3_25");
        go_Wall_3_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_25.transform.position = new Vector3(11.5f, 12.0f, 0.0f);
        var go_Wall_3_25_rb = go_Wall_3_25.AddComponent<Rigidbody2D>();
        go_Wall_3_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_25_bc = go_Wall_3_25.AddComponent<BoxCollider2D>();
        go_Wall_3_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_25_sr = go_Wall_3_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_25);

        // --- Pellet_3_26 ---
        var go_Pellet_3_26 = new GameObject("Pellet_3_26");
        go_Pellet_3_26.tag = "PowerPellet";
        go_Pellet_3_26.transform.position = new Vector3(12.5f, 12.0f, 0.0f);
        var go_Pellet_3_26_rb = go_Pellet_3_26.AddComponent<Rigidbody2D>();
        go_Pellet_3_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_3_26_bc = go_Pellet_3_26.AddComponent<BoxCollider2D>();
        go_Pellet_3_26_bc.size = new Vector2(0.5f, 0.5f);
        go_Pellet_3_26_bc.isTrigger = true;
        var go_Pellet_3_26_sr = go_Pellet_3_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_large != null) go_Pellet_3_26_sr.sprite = sprite_pellet_large;
        if (unlitMat != null) go_Pellet_3_26_sr.sharedMaterial = unlitMat;
        go_Pellet_3_26_sr.sortingOrder = 2;
        go_Pellet_3_26.AddComponent<PowerPellet>();
        // PowerPellet.duration = 8.0
        // PowerPellet.points = 50
        EditorUtility.SetDirty(go_Pellet_3_26);

        // --- Wall_3_27 ---
        var go_Wall_3_27 = new GameObject("Wall_3_27");
        go_Wall_3_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_3_27.transform.position = new Vector3(13.5f, 12.0f, 0.0f);
        var go_Wall_3_27_rb = go_Wall_3_27.AddComponent<Rigidbody2D>();
        go_Wall_3_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_3_27_bc = go_Wall_3_27.AddComponent<BoxCollider2D>();
        go_Wall_3_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_3_27_sr = go_Wall_3_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_3_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_3_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_3_27);

        // --- Wall_4_0 ---
        var go_Wall_4_0 = new GameObject("Wall_4_0");
        go_Wall_4_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_0.transform.position = new Vector3(-13.5f, 11.0f, 0.0f);
        var go_Wall_4_0_rb = go_Wall_4_0.AddComponent<Rigidbody2D>();
        go_Wall_4_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_0_bc = go_Wall_4_0.AddComponent<BoxCollider2D>();
        go_Wall_4_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_0_sr = go_Wall_4_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_0);

        // --- Pellet_4_1 ---
        var go_Pellet_4_1 = new GameObject("Pellet_4_1");
        go_Pellet_4_1.tag = "Pellet";
        go_Pellet_4_1.transform.position = new Vector3(-12.5f, 11.0f, 0.0f);
        var go_Pellet_4_1_rb = go_Pellet_4_1.AddComponent<Rigidbody2D>();
        go_Pellet_4_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_4_1_bc = go_Pellet_4_1.AddComponent<BoxCollider2D>();
        go_Pellet_4_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_4_1_bc.isTrigger = true;
        var go_Pellet_4_1_sr = go_Pellet_4_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_4_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_4_1_sr.sharedMaterial = unlitMat;
        go_Pellet_4_1_sr.sortingOrder = 2;
        go_Pellet_4_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_4_1);

        // --- Wall_4_2 ---
        var go_Wall_4_2 = new GameObject("Wall_4_2");
        go_Wall_4_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_2.transform.position = new Vector3(-11.5f, 11.0f, 0.0f);
        var go_Wall_4_2_rb = go_Wall_4_2.AddComponent<Rigidbody2D>();
        go_Wall_4_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_2_bc = go_Wall_4_2.AddComponent<BoxCollider2D>();
        go_Wall_4_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_2_sr = go_Wall_4_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_2);

        // --- Wall_4_3 ---
        var go_Wall_4_3 = new GameObject("Wall_4_3");
        go_Wall_4_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_3.transform.position = new Vector3(-10.5f, 11.0f, 0.0f);
        var go_Wall_4_3_rb = go_Wall_4_3.AddComponent<Rigidbody2D>();
        go_Wall_4_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_3_bc = go_Wall_4_3.AddComponent<BoxCollider2D>();
        go_Wall_4_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_3_sr = go_Wall_4_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_3);

        // --- Wall_4_4 ---
        var go_Wall_4_4 = new GameObject("Wall_4_4");
        go_Wall_4_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_4.transform.position = new Vector3(-9.5f, 11.0f, 0.0f);
        var go_Wall_4_4_rb = go_Wall_4_4.AddComponent<Rigidbody2D>();
        go_Wall_4_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_4_bc = go_Wall_4_4.AddComponent<BoxCollider2D>();
        go_Wall_4_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_4_sr = go_Wall_4_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_4);

        // --- Wall_4_5 ---
        var go_Wall_4_5 = new GameObject("Wall_4_5");
        go_Wall_4_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_5.transform.position = new Vector3(-8.5f, 11.0f, 0.0f);
        var go_Wall_4_5_rb = go_Wall_4_5.AddComponent<Rigidbody2D>();
        go_Wall_4_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_5_bc = go_Wall_4_5.AddComponent<BoxCollider2D>();
        go_Wall_4_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_5_sr = go_Wall_4_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_5);

        // --- Pellet_4_6 ---
        var go_Pellet_4_6 = new GameObject("Pellet_4_6");
        go_Pellet_4_6.tag = "Pellet";
        go_Pellet_4_6.transform.position = new Vector3(-7.5f, 11.0f, 0.0f);
        var go_Pellet_4_6_rb = go_Pellet_4_6.AddComponent<Rigidbody2D>();
        go_Pellet_4_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_4_6_bc = go_Pellet_4_6.AddComponent<BoxCollider2D>();
        go_Pellet_4_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_4_6_bc.isTrigger = true;
        var go_Pellet_4_6_sr = go_Pellet_4_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_4_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_4_6_sr.sharedMaterial = unlitMat;
        go_Pellet_4_6_sr.sortingOrder = 2;
        go_Pellet_4_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_4_6);

        // --- Wall_4_7 ---
        var go_Wall_4_7 = new GameObject("Wall_4_7");
        go_Wall_4_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_7.transform.position = new Vector3(-6.5f, 11.0f, 0.0f);
        var go_Wall_4_7_rb = go_Wall_4_7.AddComponent<Rigidbody2D>();
        go_Wall_4_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_7_bc = go_Wall_4_7.AddComponent<BoxCollider2D>();
        go_Wall_4_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_7_sr = go_Wall_4_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_7);

        // --- Wall_4_8 ---
        var go_Wall_4_8 = new GameObject("Wall_4_8");
        go_Wall_4_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_8.transform.position = new Vector3(-5.5f, 11.0f, 0.0f);
        var go_Wall_4_8_rb = go_Wall_4_8.AddComponent<Rigidbody2D>();
        go_Wall_4_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_8_bc = go_Wall_4_8.AddComponent<BoxCollider2D>();
        go_Wall_4_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_8_sr = go_Wall_4_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_8);

        // --- Wall_4_9 ---
        var go_Wall_4_9 = new GameObject("Wall_4_9");
        go_Wall_4_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_9.transform.position = new Vector3(-4.5f, 11.0f, 0.0f);
        var go_Wall_4_9_rb = go_Wall_4_9.AddComponent<Rigidbody2D>();
        go_Wall_4_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_9_bc = go_Wall_4_9.AddComponent<BoxCollider2D>();
        go_Wall_4_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_9_sr = go_Wall_4_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_9);

        // --- Wall_4_10 ---
        var go_Wall_4_10 = new GameObject("Wall_4_10");
        go_Wall_4_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_10.transform.position = new Vector3(-3.5f, 11.0f, 0.0f);
        var go_Wall_4_10_rb = go_Wall_4_10.AddComponent<Rigidbody2D>();
        go_Wall_4_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_10_bc = go_Wall_4_10.AddComponent<BoxCollider2D>();
        go_Wall_4_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_10_sr = go_Wall_4_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_10);

        // --- Wall_4_11 ---
        var go_Wall_4_11 = new GameObject("Wall_4_11");
        go_Wall_4_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_11.transform.position = new Vector3(-2.5f, 11.0f, 0.0f);
        var go_Wall_4_11_rb = go_Wall_4_11.AddComponent<Rigidbody2D>();
        go_Wall_4_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_11_bc = go_Wall_4_11.AddComponent<BoxCollider2D>();
        go_Wall_4_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_11_sr = go_Wall_4_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_11);

        // --- Pellet_4_12 ---
        var go_Pellet_4_12 = new GameObject("Pellet_4_12");
        go_Pellet_4_12.tag = "Pellet";
        go_Pellet_4_12.transform.position = new Vector3(-1.5f, 11.0f, 0.0f);
        var go_Pellet_4_12_rb = go_Pellet_4_12.AddComponent<Rigidbody2D>();
        go_Pellet_4_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_4_12_bc = go_Pellet_4_12.AddComponent<BoxCollider2D>();
        go_Pellet_4_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_4_12_bc.isTrigger = true;
        var go_Pellet_4_12_sr = go_Pellet_4_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_4_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_4_12_sr.sharedMaterial = unlitMat;
        go_Pellet_4_12_sr.sortingOrder = 2;
        go_Pellet_4_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_4_12);

        // --- Wall_4_13 ---
        var go_Wall_4_13 = new GameObject("Wall_4_13");
        go_Wall_4_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_13.transform.position = new Vector3(-0.5f, 11.0f, 0.0f);
        var go_Wall_4_13_rb = go_Wall_4_13.AddComponent<Rigidbody2D>();
        go_Wall_4_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_13_bc = go_Wall_4_13.AddComponent<BoxCollider2D>();
        go_Wall_4_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_13_sr = go_Wall_4_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_13);

        // --- Wall_4_14 ---
        var go_Wall_4_14 = new GameObject("Wall_4_14");
        go_Wall_4_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_14.transform.position = new Vector3(0.5f, 11.0f, 0.0f);
        var go_Wall_4_14_rb = go_Wall_4_14.AddComponent<Rigidbody2D>();
        go_Wall_4_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_14_bc = go_Wall_4_14.AddComponent<BoxCollider2D>();
        go_Wall_4_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_14_sr = go_Wall_4_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_14);

        // --- Pellet_4_15 ---
        var go_Pellet_4_15 = new GameObject("Pellet_4_15");
        go_Pellet_4_15.tag = "Pellet";
        go_Pellet_4_15.transform.position = new Vector3(1.5f, 11.0f, 0.0f);
        var go_Pellet_4_15_rb = go_Pellet_4_15.AddComponent<Rigidbody2D>();
        go_Pellet_4_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_4_15_bc = go_Pellet_4_15.AddComponent<BoxCollider2D>();
        go_Pellet_4_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_4_15_bc.isTrigger = true;
        var go_Pellet_4_15_sr = go_Pellet_4_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_4_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_4_15_sr.sharedMaterial = unlitMat;
        go_Pellet_4_15_sr.sortingOrder = 2;
        go_Pellet_4_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_4_15);

        // --- Wall_4_16 ---
        var go_Wall_4_16 = new GameObject("Wall_4_16");
        go_Wall_4_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_16.transform.position = new Vector3(2.5f, 11.0f, 0.0f);
        var go_Wall_4_16_rb = go_Wall_4_16.AddComponent<Rigidbody2D>();
        go_Wall_4_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_16_bc = go_Wall_4_16.AddComponent<BoxCollider2D>();
        go_Wall_4_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_16_sr = go_Wall_4_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_16);

        // --- Wall_4_17 ---
        var go_Wall_4_17 = new GameObject("Wall_4_17");
        go_Wall_4_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_17.transform.position = new Vector3(3.5f, 11.0f, 0.0f);
        var go_Wall_4_17_rb = go_Wall_4_17.AddComponent<Rigidbody2D>();
        go_Wall_4_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_17_bc = go_Wall_4_17.AddComponent<BoxCollider2D>();
        go_Wall_4_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_17_sr = go_Wall_4_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_17);

        // --- Wall_4_18 ---
        var go_Wall_4_18 = new GameObject("Wall_4_18");
        go_Wall_4_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_18.transform.position = new Vector3(4.5f, 11.0f, 0.0f);
        var go_Wall_4_18_rb = go_Wall_4_18.AddComponent<Rigidbody2D>();
        go_Wall_4_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_18_bc = go_Wall_4_18.AddComponent<BoxCollider2D>();
        go_Wall_4_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_18_sr = go_Wall_4_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_18);

        // --- Wall_4_19 ---
        var go_Wall_4_19 = new GameObject("Wall_4_19");
        go_Wall_4_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_19.transform.position = new Vector3(5.5f, 11.0f, 0.0f);
        var go_Wall_4_19_rb = go_Wall_4_19.AddComponent<Rigidbody2D>();
        go_Wall_4_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_19_bc = go_Wall_4_19.AddComponent<BoxCollider2D>();
        go_Wall_4_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_19_sr = go_Wall_4_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_19);

        // --- Wall_4_20 ---
        var go_Wall_4_20 = new GameObject("Wall_4_20");
        go_Wall_4_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_20.transform.position = new Vector3(6.5f, 11.0f, 0.0f);
        var go_Wall_4_20_rb = go_Wall_4_20.AddComponent<Rigidbody2D>();
        go_Wall_4_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_20_bc = go_Wall_4_20.AddComponent<BoxCollider2D>();
        go_Wall_4_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_20_sr = go_Wall_4_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_20);

        // --- Pellet_4_21 ---
        var go_Pellet_4_21 = new GameObject("Pellet_4_21");
        go_Pellet_4_21.tag = "Pellet";
        go_Pellet_4_21.transform.position = new Vector3(7.5f, 11.0f, 0.0f);
        var go_Pellet_4_21_rb = go_Pellet_4_21.AddComponent<Rigidbody2D>();
        go_Pellet_4_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_4_21_bc = go_Pellet_4_21.AddComponent<BoxCollider2D>();
        go_Pellet_4_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_4_21_bc.isTrigger = true;
        var go_Pellet_4_21_sr = go_Pellet_4_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_4_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_4_21_sr.sharedMaterial = unlitMat;
        go_Pellet_4_21_sr.sortingOrder = 2;
        go_Pellet_4_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_4_21);

        // --- Wall_4_22 ---
        var go_Wall_4_22 = new GameObject("Wall_4_22");
        go_Wall_4_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_22.transform.position = new Vector3(8.5f, 11.0f, 0.0f);
        var go_Wall_4_22_rb = go_Wall_4_22.AddComponent<Rigidbody2D>();
        go_Wall_4_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_22_bc = go_Wall_4_22.AddComponent<BoxCollider2D>();
        go_Wall_4_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_22_sr = go_Wall_4_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_22);

        // --- Wall_4_23 ---
        var go_Wall_4_23 = new GameObject("Wall_4_23");
        go_Wall_4_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_23.transform.position = new Vector3(9.5f, 11.0f, 0.0f);
        var go_Wall_4_23_rb = go_Wall_4_23.AddComponent<Rigidbody2D>();
        go_Wall_4_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_23_bc = go_Wall_4_23.AddComponent<BoxCollider2D>();
        go_Wall_4_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_23_sr = go_Wall_4_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_23);

        // --- Wall_4_24 ---
        var go_Wall_4_24 = new GameObject("Wall_4_24");
        go_Wall_4_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_24.transform.position = new Vector3(10.5f, 11.0f, 0.0f);
        var go_Wall_4_24_rb = go_Wall_4_24.AddComponent<Rigidbody2D>();
        go_Wall_4_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_24_bc = go_Wall_4_24.AddComponent<BoxCollider2D>();
        go_Wall_4_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_24_sr = go_Wall_4_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_24);

        // --- Wall_4_25 ---
        var go_Wall_4_25 = new GameObject("Wall_4_25");
        go_Wall_4_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_25.transform.position = new Vector3(11.5f, 11.0f, 0.0f);
        var go_Wall_4_25_rb = go_Wall_4_25.AddComponent<Rigidbody2D>();
        go_Wall_4_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_25_bc = go_Wall_4_25.AddComponent<BoxCollider2D>();
        go_Wall_4_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_25_sr = go_Wall_4_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_25);

        // --- Pellet_4_26 ---
        var go_Pellet_4_26 = new GameObject("Pellet_4_26");
        go_Pellet_4_26.tag = "Pellet";
        go_Pellet_4_26.transform.position = new Vector3(12.5f, 11.0f, 0.0f);
        var go_Pellet_4_26_rb = go_Pellet_4_26.AddComponent<Rigidbody2D>();
        go_Pellet_4_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_4_26_bc = go_Pellet_4_26.AddComponent<BoxCollider2D>();
        go_Pellet_4_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_4_26_bc.isTrigger = true;
        var go_Pellet_4_26_sr = go_Pellet_4_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_4_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_4_26_sr.sharedMaterial = unlitMat;
        go_Pellet_4_26_sr.sortingOrder = 2;
        go_Pellet_4_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_4_26);

        // --- Wall_4_27 ---
        var go_Wall_4_27 = new GameObject("Wall_4_27");
        go_Wall_4_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_4_27.transform.position = new Vector3(13.5f, 11.0f, 0.0f);
        var go_Wall_4_27_rb = go_Wall_4_27.AddComponent<Rigidbody2D>();
        go_Wall_4_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_4_27_bc = go_Wall_4_27.AddComponent<BoxCollider2D>();
        go_Wall_4_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_4_27_sr = go_Wall_4_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_4_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_4_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_4_27);

        // --- Wall_5_0 ---
        var go_Wall_5_0 = new GameObject("Wall_5_0");
        go_Wall_5_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_5_0.transform.position = new Vector3(-13.5f, 10.0f, 0.0f);
        var go_Wall_5_0_rb = go_Wall_5_0.AddComponent<Rigidbody2D>();
        go_Wall_5_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_5_0_bc = go_Wall_5_0.AddComponent<BoxCollider2D>();
        go_Wall_5_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_5_0_sr = go_Wall_5_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_5_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_5_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_5_0);

        // --- Pellet_5_1 ---
        var go_Pellet_5_1 = new GameObject("Pellet_5_1");
        go_Pellet_5_1.tag = "Pellet";
        go_Pellet_5_1.transform.position = new Vector3(-12.5f, 10.0f, 0.0f);
        var go_Pellet_5_1_rb = go_Pellet_5_1.AddComponent<Rigidbody2D>();
        go_Pellet_5_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_1_bc = go_Pellet_5_1.AddComponent<BoxCollider2D>();
        go_Pellet_5_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_1_bc.isTrigger = true;
        var go_Pellet_5_1_sr = go_Pellet_5_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_1_sr.sharedMaterial = unlitMat;
        go_Pellet_5_1_sr.sortingOrder = 2;
        go_Pellet_5_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_1);

        // --- Node_5_1 ---
        var go_Node_5_1 = new GameObject("Node_5_1");
        go_Node_5_1.transform.position = new Vector3(-12.5f, 10.0f, 0.0f);
        var go_Node_5_1_rb = go_Node_5_1.AddComponent<Rigidbody2D>();
        go_Node_5_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_5_1_bc = go_Node_5_1.AddComponent<BoxCollider2D>();
        go_Node_5_1_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_5_1_bc.isTrigger = true;
        go_Node_5_1.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_5_1);

        // --- Pellet_5_2 ---
        var go_Pellet_5_2 = new GameObject("Pellet_5_2");
        go_Pellet_5_2.tag = "Pellet";
        go_Pellet_5_2.transform.position = new Vector3(-11.5f, 10.0f, 0.0f);
        var go_Pellet_5_2_rb = go_Pellet_5_2.AddComponent<Rigidbody2D>();
        go_Pellet_5_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_2_bc = go_Pellet_5_2.AddComponent<BoxCollider2D>();
        go_Pellet_5_2_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_2_bc.isTrigger = true;
        var go_Pellet_5_2_sr = go_Pellet_5_2.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_2_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_2_sr.sharedMaterial = unlitMat;
        go_Pellet_5_2_sr.sortingOrder = 2;
        go_Pellet_5_2.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_2);

        // --- Pellet_5_3 ---
        var go_Pellet_5_3 = new GameObject("Pellet_5_3");
        go_Pellet_5_3.tag = "Pellet";
        go_Pellet_5_3.transform.position = new Vector3(-10.5f, 10.0f, 0.0f);
        var go_Pellet_5_3_rb = go_Pellet_5_3.AddComponent<Rigidbody2D>();
        go_Pellet_5_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_3_bc = go_Pellet_5_3.AddComponent<BoxCollider2D>();
        go_Pellet_5_3_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_3_bc.isTrigger = true;
        var go_Pellet_5_3_sr = go_Pellet_5_3.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_3_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_3_sr.sharedMaterial = unlitMat;
        go_Pellet_5_3_sr.sortingOrder = 2;
        go_Pellet_5_3.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_3);

        // --- Pellet_5_4 ---
        var go_Pellet_5_4 = new GameObject("Pellet_5_4");
        go_Pellet_5_4.tag = "Pellet";
        go_Pellet_5_4.transform.position = new Vector3(-9.5f, 10.0f, 0.0f);
        var go_Pellet_5_4_rb = go_Pellet_5_4.AddComponent<Rigidbody2D>();
        go_Pellet_5_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_4_bc = go_Pellet_5_4.AddComponent<BoxCollider2D>();
        go_Pellet_5_4_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_4_bc.isTrigger = true;
        var go_Pellet_5_4_sr = go_Pellet_5_4.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_4_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_4_sr.sharedMaterial = unlitMat;
        go_Pellet_5_4_sr.sortingOrder = 2;
        go_Pellet_5_4.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_4);

        // --- Pellet_5_5 ---
        var go_Pellet_5_5 = new GameObject("Pellet_5_5");
        go_Pellet_5_5.tag = "Pellet";
        go_Pellet_5_5.transform.position = new Vector3(-8.5f, 10.0f, 0.0f);
        var go_Pellet_5_5_rb = go_Pellet_5_5.AddComponent<Rigidbody2D>();
        go_Pellet_5_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_5_bc = go_Pellet_5_5.AddComponent<BoxCollider2D>();
        go_Pellet_5_5_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_5_bc.isTrigger = true;
        var go_Pellet_5_5_sr = go_Pellet_5_5.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_5_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_5_sr.sharedMaterial = unlitMat;
        go_Pellet_5_5_sr.sortingOrder = 2;
        go_Pellet_5_5.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_5);

        // --- Pellet_5_6 ---
        var go_Pellet_5_6 = new GameObject("Pellet_5_6");
        go_Pellet_5_6.tag = "Pellet";
        go_Pellet_5_6.transform.position = new Vector3(-7.5f, 10.0f, 0.0f);
        var go_Pellet_5_6_rb = go_Pellet_5_6.AddComponent<Rigidbody2D>();
        go_Pellet_5_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_6_bc = go_Pellet_5_6.AddComponent<BoxCollider2D>();
        go_Pellet_5_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_6_bc.isTrigger = true;
        var go_Pellet_5_6_sr = go_Pellet_5_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_6_sr.sharedMaterial = unlitMat;
        go_Pellet_5_6_sr.sortingOrder = 2;
        go_Pellet_5_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_6);

        // --- Node_5_6 ---
        var go_Node_5_6 = new GameObject("Node_5_6");
        go_Node_5_6.transform.position = new Vector3(-7.5f, 10.0f, 0.0f);
        var go_Node_5_6_rb = go_Node_5_6.AddComponent<Rigidbody2D>();
        go_Node_5_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_5_6_bc = go_Node_5_6.AddComponent<BoxCollider2D>();
        go_Node_5_6_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_5_6_bc.isTrigger = true;
        go_Node_5_6.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_5_6);

        // --- Pellet_5_7 ---
        var go_Pellet_5_7 = new GameObject("Pellet_5_7");
        go_Pellet_5_7.tag = "Pellet";
        go_Pellet_5_7.transform.position = new Vector3(-6.5f, 10.0f, 0.0f);
        var go_Pellet_5_7_rb = go_Pellet_5_7.AddComponent<Rigidbody2D>();
        go_Pellet_5_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_7_bc = go_Pellet_5_7.AddComponent<BoxCollider2D>();
        go_Pellet_5_7_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_7_bc.isTrigger = true;
        var go_Pellet_5_7_sr = go_Pellet_5_7.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_7_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_7_sr.sharedMaterial = unlitMat;
        go_Pellet_5_7_sr.sortingOrder = 2;
        go_Pellet_5_7.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_7);

        // --- Pellet_5_8 ---
        var go_Pellet_5_8 = new GameObject("Pellet_5_8");
        go_Pellet_5_8.tag = "Pellet";
        go_Pellet_5_8.transform.position = new Vector3(-5.5f, 10.0f, 0.0f);
        var go_Pellet_5_8_rb = go_Pellet_5_8.AddComponent<Rigidbody2D>();
        go_Pellet_5_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_8_bc = go_Pellet_5_8.AddComponent<BoxCollider2D>();
        go_Pellet_5_8_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_8_bc.isTrigger = true;
        var go_Pellet_5_8_sr = go_Pellet_5_8.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_8_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_8_sr.sharedMaterial = unlitMat;
        go_Pellet_5_8_sr.sortingOrder = 2;
        go_Pellet_5_8.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_8);

        // --- Pellet_5_9 ---
        var go_Pellet_5_9 = new GameObject("Pellet_5_9");
        go_Pellet_5_9.tag = "Pellet";
        go_Pellet_5_9.transform.position = new Vector3(-4.5f, 10.0f, 0.0f);
        var go_Pellet_5_9_rb = go_Pellet_5_9.AddComponent<Rigidbody2D>();
        go_Pellet_5_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_9_bc = go_Pellet_5_9.AddComponent<BoxCollider2D>();
        go_Pellet_5_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_9_bc.isTrigger = true;
        var go_Pellet_5_9_sr = go_Pellet_5_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_9_sr.sharedMaterial = unlitMat;
        go_Pellet_5_9_sr.sortingOrder = 2;
        go_Pellet_5_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_9);

        // --- Node_5_9 ---
        var go_Node_5_9 = new GameObject("Node_5_9");
        go_Node_5_9.transform.position = new Vector3(-4.5f, 10.0f, 0.0f);
        var go_Node_5_9_rb = go_Node_5_9.AddComponent<Rigidbody2D>();
        go_Node_5_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_5_9_bc = go_Node_5_9.AddComponent<BoxCollider2D>();
        go_Node_5_9_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_5_9_bc.isTrigger = true;
        go_Node_5_9.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_5_9);

        // --- Pellet_5_10 ---
        var go_Pellet_5_10 = new GameObject("Pellet_5_10");
        go_Pellet_5_10.tag = "Pellet";
        go_Pellet_5_10.transform.position = new Vector3(-3.5f, 10.0f, 0.0f);
        var go_Pellet_5_10_rb = go_Pellet_5_10.AddComponent<Rigidbody2D>();
        go_Pellet_5_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_10_bc = go_Pellet_5_10.AddComponent<BoxCollider2D>();
        go_Pellet_5_10_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_10_bc.isTrigger = true;
        var go_Pellet_5_10_sr = go_Pellet_5_10.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_10_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_10_sr.sharedMaterial = unlitMat;
        go_Pellet_5_10_sr.sortingOrder = 2;
        go_Pellet_5_10.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_10);

        // --- Pellet_5_11 ---
        var go_Pellet_5_11 = new GameObject("Pellet_5_11");
        go_Pellet_5_11.tag = "Pellet";
        go_Pellet_5_11.transform.position = new Vector3(-2.5f, 10.0f, 0.0f);
        var go_Pellet_5_11_rb = go_Pellet_5_11.AddComponent<Rigidbody2D>();
        go_Pellet_5_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_11_bc = go_Pellet_5_11.AddComponent<BoxCollider2D>();
        go_Pellet_5_11_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_11_bc.isTrigger = true;
        var go_Pellet_5_11_sr = go_Pellet_5_11.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_11_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_11_sr.sharedMaterial = unlitMat;
        go_Pellet_5_11_sr.sortingOrder = 2;
        go_Pellet_5_11.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_11);

        // --- Pellet_5_12 ---
        var go_Pellet_5_12 = new GameObject("Pellet_5_12");
        go_Pellet_5_12.tag = "Pellet";
        go_Pellet_5_12.transform.position = new Vector3(-1.5f, 10.0f, 0.0f);
        var go_Pellet_5_12_rb = go_Pellet_5_12.AddComponent<Rigidbody2D>();
        go_Pellet_5_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_12_bc = go_Pellet_5_12.AddComponent<BoxCollider2D>();
        go_Pellet_5_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_12_bc.isTrigger = true;
        var go_Pellet_5_12_sr = go_Pellet_5_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_12_sr.sharedMaterial = unlitMat;
        go_Pellet_5_12_sr.sortingOrder = 2;
        go_Pellet_5_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_12);

        // --- Node_5_12 ---
        var go_Node_5_12 = new GameObject("Node_5_12");
        go_Node_5_12.transform.position = new Vector3(-1.5f, 10.0f, 0.0f);
        var go_Node_5_12_rb = go_Node_5_12.AddComponent<Rigidbody2D>();
        go_Node_5_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_5_12_bc = go_Node_5_12.AddComponent<BoxCollider2D>();
        go_Node_5_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_5_12_bc.isTrigger = true;
        go_Node_5_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_5_12);

        // --- Pellet_5_13 ---
        var go_Pellet_5_13 = new GameObject("Pellet_5_13");
        go_Pellet_5_13.tag = "Pellet";
        go_Pellet_5_13.transform.position = new Vector3(-0.5f, 10.0f, 0.0f);
        var go_Pellet_5_13_rb = go_Pellet_5_13.AddComponent<Rigidbody2D>();
        go_Pellet_5_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_13_bc = go_Pellet_5_13.AddComponent<BoxCollider2D>();
        go_Pellet_5_13_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_13_bc.isTrigger = true;
        var go_Pellet_5_13_sr = go_Pellet_5_13.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_13_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_13_sr.sharedMaterial = unlitMat;
        go_Pellet_5_13_sr.sortingOrder = 2;
        go_Pellet_5_13.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_13);

        // --- Pellet_5_14 ---
        var go_Pellet_5_14 = new GameObject("Pellet_5_14");
        go_Pellet_5_14.tag = "Pellet";
        go_Pellet_5_14.transform.position = new Vector3(0.5f, 10.0f, 0.0f);
        var go_Pellet_5_14_rb = go_Pellet_5_14.AddComponent<Rigidbody2D>();
        go_Pellet_5_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_14_bc = go_Pellet_5_14.AddComponent<BoxCollider2D>();
        go_Pellet_5_14_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_14_bc.isTrigger = true;
        var go_Pellet_5_14_sr = go_Pellet_5_14.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_14_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_14_sr.sharedMaterial = unlitMat;
        go_Pellet_5_14_sr.sortingOrder = 2;
        go_Pellet_5_14.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_14);

        // --- Pellet_5_15 ---
        var go_Pellet_5_15 = new GameObject("Pellet_5_15");
        go_Pellet_5_15.tag = "Pellet";
        go_Pellet_5_15.transform.position = new Vector3(1.5f, 10.0f, 0.0f);
        var go_Pellet_5_15_rb = go_Pellet_5_15.AddComponent<Rigidbody2D>();
        go_Pellet_5_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_15_bc = go_Pellet_5_15.AddComponent<BoxCollider2D>();
        go_Pellet_5_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_15_bc.isTrigger = true;
        var go_Pellet_5_15_sr = go_Pellet_5_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_15_sr.sharedMaterial = unlitMat;
        go_Pellet_5_15_sr.sortingOrder = 2;
        go_Pellet_5_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_15);

        // --- Node_5_15 ---
        var go_Node_5_15 = new GameObject("Node_5_15");
        go_Node_5_15.transform.position = new Vector3(1.5f, 10.0f, 0.0f);
        var go_Node_5_15_rb = go_Node_5_15.AddComponent<Rigidbody2D>();
        go_Node_5_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_5_15_bc = go_Node_5_15.AddComponent<BoxCollider2D>();
        go_Node_5_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_5_15_bc.isTrigger = true;
        go_Node_5_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_5_15);

        // --- Pellet_5_16 ---
        var go_Pellet_5_16 = new GameObject("Pellet_5_16");
        go_Pellet_5_16.tag = "Pellet";
        go_Pellet_5_16.transform.position = new Vector3(2.5f, 10.0f, 0.0f);
        var go_Pellet_5_16_rb = go_Pellet_5_16.AddComponent<Rigidbody2D>();
        go_Pellet_5_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_16_bc = go_Pellet_5_16.AddComponent<BoxCollider2D>();
        go_Pellet_5_16_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_16_bc.isTrigger = true;
        var go_Pellet_5_16_sr = go_Pellet_5_16.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_16_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_16_sr.sharedMaterial = unlitMat;
        go_Pellet_5_16_sr.sortingOrder = 2;
        go_Pellet_5_16.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_16);

        // --- Pellet_5_17 ---
        var go_Pellet_5_17 = new GameObject("Pellet_5_17");
        go_Pellet_5_17.tag = "Pellet";
        go_Pellet_5_17.transform.position = new Vector3(3.5f, 10.0f, 0.0f);
        var go_Pellet_5_17_rb = go_Pellet_5_17.AddComponent<Rigidbody2D>();
        go_Pellet_5_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_17_bc = go_Pellet_5_17.AddComponent<BoxCollider2D>();
        go_Pellet_5_17_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_17_bc.isTrigger = true;
        var go_Pellet_5_17_sr = go_Pellet_5_17.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_17_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_17_sr.sharedMaterial = unlitMat;
        go_Pellet_5_17_sr.sortingOrder = 2;
        go_Pellet_5_17.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_17);

        // --- Pellet_5_18 ---
        var go_Pellet_5_18 = new GameObject("Pellet_5_18");
        go_Pellet_5_18.tag = "Pellet";
        go_Pellet_5_18.transform.position = new Vector3(4.5f, 10.0f, 0.0f);
        var go_Pellet_5_18_rb = go_Pellet_5_18.AddComponent<Rigidbody2D>();
        go_Pellet_5_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_18_bc = go_Pellet_5_18.AddComponent<BoxCollider2D>();
        go_Pellet_5_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_18_bc.isTrigger = true;
        var go_Pellet_5_18_sr = go_Pellet_5_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_18_sr.sharedMaterial = unlitMat;
        go_Pellet_5_18_sr.sortingOrder = 2;
        go_Pellet_5_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_18);

        // --- Node_5_18 ---
        var go_Node_5_18 = new GameObject("Node_5_18");
        go_Node_5_18.transform.position = new Vector3(4.5f, 10.0f, 0.0f);
        var go_Node_5_18_rb = go_Node_5_18.AddComponent<Rigidbody2D>();
        go_Node_5_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_5_18_bc = go_Node_5_18.AddComponent<BoxCollider2D>();
        go_Node_5_18_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_5_18_bc.isTrigger = true;
        go_Node_5_18.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_5_18);

        // --- Pellet_5_19 ---
        var go_Pellet_5_19 = new GameObject("Pellet_5_19");
        go_Pellet_5_19.tag = "Pellet";
        go_Pellet_5_19.transform.position = new Vector3(5.5f, 10.0f, 0.0f);
        var go_Pellet_5_19_rb = go_Pellet_5_19.AddComponent<Rigidbody2D>();
        go_Pellet_5_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_19_bc = go_Pellet_5_19.AddComponent<BoxCollider2D>();
        go_Pellet_5_19_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_19_bc.isTrigger = true;
        var go_Pellet_5_19_sr = go_Pellet_5_19.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_19_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_19_sr.sharedMaterial = unlitMat;
        go_Pellet_5_19_sr.sortingOrder = 2;
        go_Pellet_5_19.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_19);

        // --- Pellet_5_20 ---
        var go_Pellet_5_20 = new GameObject("Pellet_5_20");
        go_Pellet_5_20.tag = "Pellet";
        go_Pellet_5_20.transform.position = new Vector3(6.5f, 10.0f, 0.0f);
        var go_Pellet_5_20_rb = go_Pellet_5_20.AddComponent<Rigidbody2D>();
        go_Pellet_5_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_20_bc = go_Pellet_5_20.AddComponent<BoxCollider2D>();
        go_Pellet_5_20_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_20_bc.isTrigger = true;
        var go_Pellet_5_20_sr = go_Pellet_5_20.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_20_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_20_sr.sharedMaterial = unlitMat;
        go_Pellet_5_20_sr.sortingOrder = 2;
        go_Pellet_5_20.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_20);

        // --- Pellet_5_21 ---
        var go_Pellet_5_21 = new GameObject("Pellet_5_21");
        go_Pellet_5_21.tag = "Pellet";
        go_Pellet_5_21.transform.position = new Vector3(7.5f, 10.0f, 0.0f);
        var go_Pellet_5_21_rb = go_Pellet_5_21.AddComponent<Rigidbody2D>();
        go_Pellet_5_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_21_bc = go_Pellet_5_21.AddComponent<BoxCollider2D>();
        go_Pellet_5_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_21_bc.isTrigger = true;
        var go_Pellet_5_21_sr = go_Pellet_5_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_21_sr.sharedMaterial = unlitMat;
        go_Pellet_5_21_sr.sortingOrder = 2;
        go_Pellet_5_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_21);

        // --- Node_5_21 ---
        var go_Node_5_21 = new GameObject("Node_5_21");
        go_Node_5_21.transform.position = new Vector3(7.5f, 10.0f, 0.0f);
        var go_Node_5_21_rb = go_Node_5_21.AddComponent<Rigidbody2D>();
        go_Node_5_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_5_21_bc = go_Node_5_21.AddComponent<BoxCollider2D>();
        go_Node_5_21_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_5_21_bc.isTrigger = true;
        go_Node_5_21.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_5_21);

        // --- Pellet_5_22 ---
        var go_Pellet_5_22 = new GameObject("Pellet_5_22");
        go_Pellet_5_22.tag = "Pellet";
        go_Pellet_5_22.transform.position = new Vector3(8.5f, 10.0f, 0.0f);
        var go_Pellet_5_22_rb = go_Pellet_5_22.AddComponent<Rigidbody2D>();
        go_Pellet_5_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_22_bc = go_Pellet_5_22.AddComponent<BoxCollider2D>();
        go_Pellet_5_22_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_22_bc.isTrigger = true;
        var go_Pellet_5_22_sr = go_Pellet_5_22.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_22_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_22_sr.sharedMaterial = unlitMat;
        go_Pellet_5_22_sr.sortingOrder = 2;
        go_Pellet_5_22.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_22);

        // --- Pellet_5_23 ---
        var go_Pellet_5_23 = new GameObject("Pellet_5_23");
        go_Pellet_5_23.tag = "Pellet";
        go_Pellet_5_23.transform.position = new Vector3(9.5f, 10.0f, 0.0f);
        var go_Pellet_5_23_rb = go_Pellet_5_23.AddComponent<Rigidbody2D>();
        go_Pellet_5_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_23_bc = go_Pellet_5_23.AddComponent<BoxCollider2D>();
        go_Pellet_5_23_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_23_bc.isTrigger = true;
        var go_Pellet_5_23_sr = go_Pellet_5_23.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_23_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_23_sr.sharedMaterial = unlitMat;
        go_Pellet_5_23_sr.sortingOrder = 2;
        go_Pellet_5_23.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_23);

        // --- Pellet_5_24 ---
        var go_Pellet_5_24 = new GameObject("Pellet_5_24");
        go_Pellet_5_24.tag = "Pellet";
        go_Pellet_5_24.transform.position = new Vector3(10.5f, 10.0f, 0.0f);
        var go_Pellet_5_24_rb = go_Pellet_5_24.AddComponent<Rigidbody2D>();
        go_Pellet_5_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_24_bc = go_Pellet_5_24.AddComponent<BoxCollider2D>();
        go_Pellet_5_24_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_24_bc.isTrigger = true;
        var go_Pellet_5_24_sr = go_Pellet_5_24.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_24_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_24_sr.sharedMaterial = unlitMat;
        go_Pellet_5_24_sr.sortingOrder = 2;
        go_Pellet_5_24.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_24);

        // --- Pellet_5_25 ---
        var go_Pellet_5_25 = new GameObject("Pellet_5_25");
        go_Pellet_5_25.tag = "Pellet";
        go_Pellet_5_25.transform.position = new Vector3(11.5f, 10.0f, 0.0f);
        var go_Pellet_5_25_rb = go_Pellet_5_25.AddComponent<Rigidbody2D>();
        go_Pellet_5_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_25_bc = go_Pellet_5_25.AddComponent<BoxCollider2D>();
        go_Pellet_5_25_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_25_bc.isTrigger = true;
        var go_Pellet_5_25_sr = go_Pellet_5_25.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_25_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_25_sr.sharedMaterial = unlitMat;
        go_Pellet_5_25_sr.sortingOrder = 2;
        go_Pellet_5_25.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_25);

        // --- Pellet_5_26 ---
        var go_Pellet_5_26 = new GameObject("Pellet_5_26");
        go_Pellet_5_26.tag = "Pellet";
        go_Pellet_5_26.transform.position = new Vector3(12.5f, 10.0f, 0.0f);
        var go_Pellet_5_26_rb = go_Pellet_5_26.AddComponent<Rigidbody2D>();
        go_Pellet_5_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_5_26_bc = go_Pellet_5_26.AddComponent<BoxCollider2D>();
        go_Pellet_5_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_5_26_bc.isTrigger = true;
        var go_Pellet_5_26_sr = go_Pellet_5_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_5_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_5_26_sr.sharedMaterial = unlitMat;
        go_Pellet_5_26_sr.sortingOrder = 2;
        go_Pellet_5_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_5_26);

        // --- Node_5_26 ---
        var go_Node_5_26 = new GameObject("Node_5_26");
        go_Node_5_26.transform.position = new Vector3(12.5f, 10.0f, 0.0f);
        var go_Node_5_26_rb = go_Node_5_26.AddComponent<Rigidbody2D>();
        go_Node_5_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_5_26_bc = go_Node_5_26.AddComponent<BoxCollider2D>();
        go_Node_5_26_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_5_26_bc.isTrigger = true;
        go_Node_5_26.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_5_26);

        // --- Wall_5_27 ---
        var go_Wall_5_27 = new GameObject("Wall_5_27");
        go_Wall_5_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_5_27.transform.position = new Vector3(13.5f, 10.0f, 0.0f);
        var go_Wall_5_27_rb = go_Wall_5_27.AddComponent<Rigidbody2D>();
        go_Wall_5_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_5_27_bc = go_Wall_5_27.AddComponent<BoxCollider2D>();
        go_Wall_5_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_5_27_sr = go_Wall_5_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_5_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_5_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_5_27);

        // --- Wall_6_0 ---
        var go_Wall_6_0 = new GameObject("Wall_6_0");
        go_Wall_6_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_0.transform.position = new Vector3(-13.5f, 9.0f, 0.0f);
        var go_Wall_6_0_rb = go_Wall_6_0.AddComponent<Rigidbody2D>();
        go_Wall_6_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_0_bc = go_Wall_6_0.AddComponent<BoxCollider2D>();
        go_Wall_6_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_0_sr = go_Wall_6_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_0);

        // --- Pellet_6_1 ---
        var go_Pellet_6_1 = new GameObject("Pellet_6_1");
        go_Pellet_6_1.tag = "Pellet";
        go_Pellet_6_1.transform.position = new Vector3(-12.5f, 9.0f, 0.0f);
        var go_Pellet_6_1_rb = go_Pellet_6_1.AddComponent<Rigidbody2D>();
        go_Pellet_6_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_6_1_bc = go_Pellet_6_1.AddComponent<BoxCollider2D>();
        go_Pellet_6_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_6_1_bc.isTrigger = true;
        var go_Pellet_6_1_sr = go_Pellet_6_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_6_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_6_1_sr.sharedMaterial = unlitMat;
        go_Pellet_6_1_sr.sortingOrder = 2;
        go_Pellet_6_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_6_1);

        // --- Wall_6_2 ---
        var go_Wall_6_2 = new GameObject("Wall_6_2");
        go_Wall_6_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_2.transform.position = new Vector3(-11.5f, 9.0f, 0.0f);
        var go_Wall_6_2_rb = go_Wall_6_2.AddComponent<Rigidbody2D>();
        go_Wall_6_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_2_bc = go_Wall_6_2.AddComponent<BoxCollider2D>();
        go_Wall_6_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_2_sr = go_Wall_6_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_2);

        // --- Wall_6_3 ---
        var go_Wall_6_3 = new GameObject("Wall_6_3");
        go_Wall_6_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_3.transform.position = new Vector3(-10.5f, 9.0f, 0.0f);
        var go_Wall_6_3_rb = go_Wall_6_3.AddComponent<Rigidbody2D>();
        go_Wall_6_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_3_bc = go_Wall_6_3.AddComponent<BoxCollider2D>();
        go_Wall_6_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_3_sr = go_Wall_6_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_3);

        // --- Wall_6_4 ---
        var go_Wall_6_4 = new GameObject("Wall_6_4");
        go_Wall_6_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_4.transform.position = new Vector3(-9.5f, 9.0f, 0.0f);
        var go_Wall_6_4_rb = go_Wall_6_4.AddComponent<Rigidbody2D>();
        go_Wall_6_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_4_bc = go_Wall_6_4.AddComponent<BoxCollider2D>();
        go_Wall_6_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_4_sr = go_Wall_6_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_4);

        // --- Wall_6_5 ---
        var go_Wall_6_5 = new GameObject("Wall_6_5");
        go_Wall_6_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_5.transform.position = new Vector3(-8.5f, 9.0f, 0.0f);
        var go_Wall_6_5_rb = go_Wall_6_5.AddComponent<Rigidbody2D>();
        go_Wall_6_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_5_bc = go_Wall_6_5.AddComponent<BoxCollider2D>();
        go_Wall_6_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_5_sr = go_Wall_6_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_5);

        // --- Pellet_6_6 ---
        var go_Pellet_6_6 = new GameObject("Pellet_6_6");
        go_Pellet_6_6.tag = "Pellet";
        go_Pellet_6_6.transform.position = new Vector3(-7.5f, 9.0f, 0.0f);
        var go_Pellet_6_6_rb = go_Pellet_6_6.AddComponent<Rigidbody2D>();
        go_Pellet_6_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_6_6_bc = go_Pellet_6_6.AddComponent<BoxCollider2D>();
        go_Pellet_6_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_6_6_bc.isTrigger = true;
        var go_Pellet_6_6_sr = go_Pellet_6_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_6_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_6_6_sr.sharedMaterial = unlitMat;
        go_Pellet_6_6_sr.sortingOrder = 2;
        go_Pellet_6_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_6_6);

        // --- Wall_6_7 ---
        var go_Wall_6_7 = new GameObject("Wall_6_7");
        go_Wall_6_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_7.transform.position = new Vector3(-6.5f, 9.0f, 0.0f);
        var go_Wall_6_7_rb = go_Wall_6_7.AddComponent<Rigidbody2D>();
        go_Wall_6_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_7_bc = go_Wall_6_7.AddComponent<BoxCollider2D>();
        go_Wall_6_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_7_sr = go_Wall_6_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_7);

        // --- Wall_6_8 ---
        var go_Wall_6_8 = new GameObject("Wall_6_8");
        go_Wall_6_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_8.transform.position = new Vector3(-5.5f, 9.0f, 0.0f);
        var go_Wall_6_8_rb = go_Wall_6_8.AddComponent<Rigidbody2D>();
        go_Wall_6_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_8_bc = go_Wall_6_8.AddComponent<BoxCollider2D>();
        go_Wall_6_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_8_sr = go_Wall_6_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_8);

        // --- Pellet_6_9 ---
        var go_Pellet_6_9 = new GameObject("Pellet_6_9");
        go_Pellet_6_9.tag = "Pellet";
        go_Pellet_6_9.transform.position = new Vector3(-4.5f, 9.0f, 0.0f);
        var go_Pellet_6_9_rb = go_Pellet_6_9.AddComponent<Rigidbody2D>();
        go_Pellet_6_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_6_9_bc = go_Pellet_6_9.AddComponent<BoxCollider2D>();
        go_Pellet_6_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_6_9_bc.isTrigger = true;
        var go_Pellet_6_9_sr = go_Pellet_6_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_6_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_6_9_sr.sharedMaterial = unlitMat;
        go_Pellet_6_9_sr.sortingOrder = 2;
        go_Pellet_6_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_6_9);

        // --- Wall_6_10 ---
        var go_Wall_6_10 = new GameObject("Wall_6_10");
        go_Wall_6_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_10.transform.position = new Vector3(-3.5f, 9.0f, 0.0f);
        var go_Wall_6_10_rb = go_Wall_6_10.AddComponent<Rigidbody2D>();
        go_Wall_6_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_10_bc = go_Wall_6_10.AddComponent<BoxCollider2D>();
        go_Wall_6_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_10_sr = go_Wall_6_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_10);

        // --- Wall_6_11 ---
        var go_Wall_6_11 = new GameObject("Wall_6_11");
        go_Wall_6_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_11.transform.position = new Vector3(-2.5f, 9.0f, 0.0f);
        var go_Wall_6_11_rb = go_Wall_6_11.AddComponent<Rigidbody2D>();
        go_Wall_6_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_11_bc = go_Wall_6_11.AddComponent<BoxCollider2D>();
        go_Wall_6_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_11_sr = go_Wall_6_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_11);

        // --- Wall_6_12 ---
        var go_Wall_6_12 = new GameObject("Wall_6_12");
        go_Wall_6_12.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_12.transform.position = new Vector3(-1.5f, 9.0f, 0.0f);
        var go_Wall_6_12_rb = go_Wall_6_12.AddComponent<Rigidbody2D>();
        go_Wall_6_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_12_bc = go_Wall_6_12.AddComponent<BoxCollider2D>();
        go_Wall_6_12_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_12_sr = go_Wall_6_12.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_12_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_12_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_12);

        // --- Wall_6_13 ---
        var go_Wall_6_13 = new GameObject("Wall_6_13");
        go_Wall_6_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_13.transform.position = new Vector3(-0.5f, 9.0f, 0.0f);
        var go_Wall_6_13_rb = go_Wall_6_13.AddComponent<Rigidbody2D>();
        go_Wall_6_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_13_bc = go_Wall_6_13.AddComponent<BoxCollider2D>();
        go_Wall_6_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_13_sr = go_Wall_6_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_13);

        // --- Wall_6_14 ---
        var go_Wall_6_14 = new GameObject("Wall_6_14");
        go_Wall_6_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_14.transform.position = new Vector3(0.5f, 9.0f, 0.0f);
        var go_Wall_6_14_rb = go_Wall_6_14.AddComponent<Rigidbody2D>();
        go_Wall_6_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_14_bc = go_Wall_6_14.AddComponent<BoxCollider2D>();
        go_Wall_6_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_14_sr = go_Wall_6_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_14);

        // --- Wall_6_15 ---
        var go_Wall_6_15 = new GameObject("Wall_6_15");
        go_Wall_6_15.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_15.transform.position = new Vector3(1.5f, 9.0f, 0.0f);
        var go_Wall_6_15_rb = go_Wall_6_15.AddComponent<Rigidbody2D>();
        go_Wall_6_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_15_bc = go_Wall_6_15.AddComponent<BoxCollider2D>();
        go_Wall_6_15_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_15_sr = go_Wall_6_15.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_15_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_15_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_15);

        // --- Wall_6_16 ---
        var go_Wall_6_16 = new GameObject("Wall_6_16");
        go_Wall_6_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_16.transform.position = new Vector3(2.5f, 9.0f, 0.0f);
        var go_Wall_6_16_rb = go_Wall_6_16.AddComponent<Rigidbody2D>();
        go_Wall_6_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_16_bc = go_Wall_6_16.AddComponent<BoxCollider2D>();
        go_Wall_6_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_16_sr = go_Wall_6_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_16);

        // --- Wall_6_17 ---
        var go_Wall_6_17 = new GameObject("Wall_6_17");
        go_Wall_6_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_17.transform.position = new Vector3(3.5f, 9.0f, 0.0f);
        var go_Wall_6_17_rb = go_Wall_6_17.AddComponent<Rigidbody2D>();
        go_Wall_6_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_17_bc = go_Wall_6_17.AddComponent<BoxCollider2D>();
        go_Wall_6_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_17_sr = go_Wall_6_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_17);

        // --- Pellet_6_18 ---
        var go_Pellet_6_18 = new GameObject("Pellet_6_18");
        go_Pellet_6_18.tag = "Pellet";
        go_Pellet_6_18.transform.position = new Vector3(4.5f, 9.0f, 0.0f);
        var go_Pellet_6_18_rb = go_Pellet_6_18.AddComponent<Rigidbody2D>();
        go_Pellet_6_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_6_18_bc = go_Pellet_6_18.AddComponent<BoxCollider2D>();
        go_Pellet_6_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_6_18_bc.isTrigger = true;
        var go_Pellet_6_18_sr = go_Pellet_6_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_6_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_6_18_sr.sharedMaterial = unlitMat;
        go_Pellet_6_18_sr.sortingOrder = 2;
        go_Pellet_6_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_6_18);

        // --- Wall_6_19 ---
        var go_Wall_6_19 = new GameObject("Wall_6_19");
        go_Wall_6_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_19.transform.position = new Vector3(5.5f, 9.0f, 0.0f);
        var go_Wall_6_19_rb = go_Wall_6_19.AddComponent<Rigidbody2D>();
        go_Wall_6_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_19_bc = go_Wall_6_19.AddComponent<BoxCollider2D>();
        go_Wall_6_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_19_sr = go_Wall_6_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_19);

        // --- Wall_6_20 ---
        var go_Wall_6_20 = new GameObject("Wall_6_20");
        go_Wall_6_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_20.transform.position = new Vector3(6.5f, 9.0f, 0.0f);
        var go_Wall_6_20_rb = go_Wall_6_20.AddComponent<Rigidbody2D>();
        go_Wall_6_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_20_bc = go_Wall_6_20.AddComponent<BoxCollider2D>();
        go_Wall_6_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_20_sr = go_Wall_6_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_20);

        // --- Pellet_6_21 ---
        var go_Pellet_6_21 = new GameObject("Pellet_6_21");
        go_Pellet_6_21.tag = "Pellet";
        go_Pellet_6_21.transform.position = new Vector3(7.5f, 9.0f, 0.0f);
        var go_Pellet_6_21_rb = go_Pellet_6_21.AddComponent<Rigidbody2D>();
        go_Pellet_6_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_6_21_bc = go_Pellet_6_21.AddComponent<BoxCollider2D>();
        go_Pellet_6_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_6_21_bc.isTrigger = true;
        var go_Pellet_6_21_sr = go_Pellet_6_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_6_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_6_21_sr.sharedMaterial = unlitMat;
        go_Pellet_6_21_sr.sortingOrder = 2;
        go_Pellet_6_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_6_21);

        // --- Wall_6_22 ---
        var go_Wall_6_22 = new GameObject("Wall_6_22");
        go_Wall_6_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_22.transform.position = new Vector3(8.5f, 9.0f, 0.0f);
        var go_Wall_6_22_rb = go_Wall_6_22.AddComponent<Rigidbody2D>();
        go_Wall_6_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_22_bc = go_Wall_6_22.AddComponent<BoxCollider2D>();
        go_Wall_6_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_22_sr = go_Wall_6_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_22);

        // --- Wall_6_23 ---
        var go_Wall_6_23 = new GameObject("Wall_6_23");
        go_Wall_6_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_23.transform.position = new Vector3(9.5f, 9.0f, 0.0f);
        var go_Wall_6_23_rb = go_Wall_6_23.AddComponent<Rigidbody2D>();
        go_Wall_6_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_23_bc = go_Wall_6_23.AddComponent<BoxCollider2D>();
        go_Wall_6_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_23_sr = go_Wall_6_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_23);

        // --- Wall_6_24 ---
        var go_Wall_6_24 = new GameObject("Wall_6_24");
        go_Wall_6_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_24.transform.position = new Vector3(10.5f, 9.0f, 0.0f);
        var go_Wall_6_24_rb = go_Wall_6_24.AddComponent<Rigidbody2D>();
        go_Wall_6_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_24_bc = go_Wall_6_24.AddComponent<BoxCollider2D>();
        go_Wall_6_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_24_sr = go_Wall_6_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_24);

        // --- Wall_6_25 ---
        var go_Wall_6_25 = new GameObject("Wall_6_25");
        go_Wall_6_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_25.transform.position = new Vector3(11.5f, 9.0f, 0.0f);
        var go_Wall_6_25_rb = go_Wall_6_25.AddComponent<Rigidbody2D>();
        go_Wall_6_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_25_bc = go_Wall_6_25.AddComponent<BoxCollider2D>();
        go_Wall_6_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_25_sr = go_Wall_6_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_25);

        // --- Pellet_6_26 ---
        var go_Pellet_6_26 = new GameObject("Pellet_6_26");
        go_Pellet_6_26.tag = "Pellet";
        go_Pellet_6_26.transform.position = new Vector3(12.5f, 9.0f, 0.0f);
        var go_Pellet_6_26_rb = go_Pellet_6_26.AddComponent<Rigidbody2D>();
        go_Pellet_6_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_6_26_bc = go_Pellet_6_26.AddComponent<BoxCollider2D>();
        go_Pellet_6_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_6_26_bc.isTrigger = true;
        var go_Pellet_6_26_sr = go_Pellet_6_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_6_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_6_26_sr.sharedMaterial = unlitMat;
        go_Pellet_6_26_sr.sortingOrder = 2;
        go_Pellet_6_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_6_26);

        // --- Wall_6_27 ---
        var go_Wall_6_27 = new GameObject("Wall_6_27");
        go_Wall_6_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_6_27.transform.position = new Vector3(13.5f, 9.0f, 0.0f);
        var go_Wall_6_27_rb = go_Wall_6_27.AddComponent<Rigidbody2D>();
        go_Wall_6_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_6_27_bc = go_Wall_6_27.AddComponent<BoxCollider2D>();
        go_Wall_6_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_6_27_sr = go_Wall_6_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_6_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_6_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_6_27);

        // --- Wall_7_0 ---
        var go_Wall_7_0 = new GameObject("Wall_7_0");
        go_Wall_7_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_0.transform.position = new Vector3(-13.5f, 8.0f, 0.0f);
        var go_Wall_7_0_rb = go_Wall_7_0.AddComponent<Rigidbody2D>();
        go_Wall_7_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_0_bc = go_Wall_7_0.AddComponent<BoxCollider2D>();
        go_Wall_7_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_0_sr = go_Wall_7_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_0);

        // --- Pellet_7_1 ---
        var go_Pellet_7_1 = new GameObject("Pellet_7_1");
        go_Pellet_7_1.tag = "Pellet";
        go_Pellet_7_1.transform.position = new Vector3(-12.5f, 8.0f, 0.0f);
        var go_Pellet_7_1_rb = go_Pellet_7_1.AddComponent<Rigidbody2D>();
        go_Pellet_7_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_7_1_bc = go_Pellet_7_1.AddComponent<BoxCollider2D>();
        go_Pellet_7_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_7_1_bc.isTrigger = true;
        var go_Pellet_7_1_sr = go_Pellet_7_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_7_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_7_1_sr.sharedMaterial = unlitMat;
        go_Pellet_7_1_sr.sortingOrder = 2;
        go_Pellet_7_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_7_1);

        // --- Wall_7_2 ---
        var go_Wall_7_2 = new GameObject("Wall_7_2");
        go_Wall_7_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_2.transform.position = new Vector3(-11.5f, 8.0f, 0.0f);
        var go_Wall_7_2_rb = go_Wall_7_2.AddComponent<Rigidbody2D>();
        go_Wall_7_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_2_bc = go_Wall_7_2.AddComponent<BoxCollider2D>();
        go_Wall_7_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_2_sr = go_Wall_7_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_2);

        // --- Wall_7_3 ---
        var go_Wall_7_3 = new GameObject("Wall_7_3");
        go_Wall_7_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_3.transform.position = new Vector3(-10.5f, 8.0f, 0.0f);
        var go_Wall_7_3_rb = go_Wall_7_3.AddComponent<Rigidbody2D>();
        go_Wall_7_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_3_bc = go_Wall_7_3.AddComponent<BoxCollider2D>();
        go_Wall_7_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_3_sr = go_Wall_7_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_3);

        // --- Wall_7_4 ---
        var go_Wall_7_4 = new GameObject("Wall_7_4");
        go_Wall_7_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_4.transform.position = new Vector3(-9.5f, 8.0f, 0.0f);
        var go_Wall_7_4_rb = go_Wall_7_4.AddComponent<Rigidbody2D>();
        go_Wall_7_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_4_bc = go_Wall_7_4.AddComponent<BoxCollider2D>();
        go_Wall_7_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_4_sr = go_Wall_7_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_4);

        // --- Wall_7_5 ---
        var go_Wall_7_5 = new GameObject("Wall_7_5");
        go_Wall_7_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_5.transform.position = new Vector3(-8.5f, 8.0f, 0.0f);
        var go_Wall_7_5_rb = go_Wall_7_5.AddComponent<Rigidbody2D>();
        go_Wall_7_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_5_bc = go_Wall_7_5.AddComponent<BoxCollider2D>();
        go_Wall_7_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_5_sr = go_Wall_7_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_5);

        // --- Pellet_7_6 ---
        var go_Pellet_7_6 = new GameObject("Pellet_7_6");
        go_Pellet_7_6.tag = "Pellet";
        go_Pellet_7_6.transform.position = new Vector3(-7.5f, 8.0f, 0.0f);
        var go_Pellet_7_6_rb = go_Pellet_7_6.AddComponent<Rigidbody2D>();
        go_Pellet_7_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_7_6_bc = go_Pellet_7_6.AddComponent<BoxCollider2D>();
        go_Pellet_7_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_7_6_bc.isTrigger = true;
        var go_Pellet_7_6_sr = go_Pellet_7_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_7_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_7_6_sr.sharedMaterial = unlitMat;
        go_Pellet_7_6_sr.sortingOrder = 2;
        go_Pellet_7_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_7_6);

        // --- Wall_7_7 ---
        var go_Wall_7_7 = new GameObject("Wall_7_7");
        go_Wall_7_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_7.transform.position = new Vector3(-6.5f, 8.0f, 0.0f);
        var go_Wall_7_7_rb = go_Wall_7_7.AddComponent<Rigidbody2D>();
        go_Wall_7_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_7_bc = go_Wall_7_7.AddComponent<BoxCollider2D>();
        go_Wall_7_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_7_sr = go_Wall_7_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_7);

        // --- Wall_7_8 ---
        var go_Wall_7_8 = new GameObject("Wall_7_8");
        go_Wall_7_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_8.transform.position = new Vector3(-5.5f, 8.0f, 0.0f);
        var go_Wall_7_8_rb = go_Wall_7_8.AddComponent<Rigidbody2D>();
        go_Wall_7_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_8_bc = go_Wall_7_8.AddComponent<BoxCollider2D>();
        go_Wall_7_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_8_sr = go_Wall_7_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_8);

        // --- Pellet_7_9 ---
        var go_Pellet_7_9 = new GameObject("Pellet_7_9");
        go_Pellet_7_9.tag = "Pellet";
        go_Pellet_7_9.transform.position = new Vector3(-4.5f, 8.0f, 0.0f);
        var go_Pellet_7_9_rb = go_Pellet_7_9.AddComponent<Rigidbody2D>();
        go_Pellet_7_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_7_9_bc = go_Pellet_7_9.AddComponent<BoxCollider2D>();
        go_Pellet_7_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_7_9_bc.isTrigger = true;
        var go_Pellet_7_9_sr = go_Pellet_7_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_7_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_7_9_sr.sharedMaterial = unlitMat;
        go_Pellet_7_9_sr.sortingOrder = 2;
        go_Pellet_7_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_7_9);

        // --- Wall_7_10 ---
        var go_Wall_7_10 = new GameObject("Wall_7_10");
        go_Wall_7_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_10.transform.position = new Vector3(-3.5f, 8.0f, 0.0f);
        var go_Wall_7_10_rb = go_Wall_7_10.AddComponent<Rigidbody2D>();
        go_Wall_7_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_10_bc = go_Wall_7_10.AddComponent<BoxCollider2D>();
        go_Wall_7_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_10_sr = go_Wall_7_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_10);

        // --- Wall_7_11 ---
        var go_Wall_7_11 = new GameObject("Wall_7_11");
        go_Wall_7_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_11.transform.position = new Vector3(-2.5f, 8.0f, 0.0f);
        var go_Wall_7_11_rb = go_Wall_7_11.AddComponent<Rigidbody2D>();
        go_Wall_7_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_11_bc = go_Wall_7_11.AddComponent<BoxCollider2D>();
        go_Wall_7_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_11_sr = go_Wall_7_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_11);

        // --- Wall_7_12 ---
        var go_Wall_7_12 = new GameObject("Wall_7_12");
        go_Wall_7_12.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_12.transform.position = new Vector3(-1.5f, 8.0f, 0.0f);
        var go_Wall_7_12_rb = go_Wall_7_12.AddComponent<Rigidbody2D>();
        go_Wall_7_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_12_bc = go_Wall_7_12.AddComponent<BoxCollider2D>();
        go_Wall_7_12_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_12_sr = go_Wall_7_12.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_12_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_12_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_12);

        // --- Wall_7_13 ---
        var go_Wall_7_13 = new GameObject("Wall_7_13");
        go_Wall_7_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_13.transform.position = new Vector3(-0.5f, 8.0f, 0.0f);
        var go_Wall_7_13_rb = go_Wall_7_13.AddComponent<Rigidbody2D>();
        go_Wall_7_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_13_bc = go_Wall_7_13.AddComponent<BoxCollider2D>();
        go_Wall_7_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_13_sr = go_Wall_7_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_13);

        // --- Wall_7_14 ---
        var go_Wall_7_14 = new GameObject("Wall_7_14");
        go_Wall_7_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_14.transform.position = new Vector3(0.5f, 8.0f, 0.0f);
        var go_Wall_7_14_rb = go_Wall_7_14.AddComponent<Rigidbody2D>();
        go_Wall_7_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_14_bc = go_Wall_7_14.AddComponent<BoxCollider2D>();
        go_Wall_7_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_14_sr = go_Wall_7_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_14);

        // --- Wall_7_15 ---
        var go_Wall_7_15 = new GameObject("Wall_7_15");
        go_Wall_7_15.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_15.transform.position = new Vector3(1.5f, 8.0f, 0.0f);
        var go_Wall_7_15_rb = go_Wall_7_15.AddComponent<Rigidbody2D>();
        go_Wall_7_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_15_bc = go_Wall_7_15.AddComponent<BoxCollider2D>();
        go_Wall_7_15_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_15_sr = go_Wall_7_15.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_15_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_15_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_15);

        // --- Wall_7_16 ---
        var go_Wall_7_16 = new GameObject("Wall_7_16");
        go_Wall_7_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_16.transform.position = new Vector3(2.5f, 8.0f, 0.0f);
        var go_Wall_7_16_rb = go_Wall_7_16.AddComponent<Rigidbody2D>();
        go_Wall_7_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_16_bc = go_Wall_7_16.AddComponent<BoxCollider2D>();
        go_Wall_7_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_16_sr = go_Wall_7_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_16);

        // --- Wall_7_17 ---
        var go_Wall_7_17 = new GameObject("Wall_7_17");
        go_Wall_7_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_17.transform.position = new Vector3(3.5f, 8.0f, 0.0f);
        var go_Wall_7_17_rb = go_Wall_7_17.AddComponent<Rigidbody2D>();
        go_Wall_7_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_17_bc = go_Wall_7_17.AddComponent<BoxCollider2D>();
        go_Wall_7_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_17_sr = go_Wall_7_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_17);

        // --- Pellet_7_18 ---
        var go_Pellet_7_18 = new GameObject("Pellet_7_18");
        go_Pellet_7_18.tag = "Pellet";
        go_Pellet_7_18.transform.position = new Vector3(4.5f, 8.0f, 0.0f);
        var go_Pellet_7_18_rb = go_Pellet_7_18.AddComponent<Rigidbody2D>();
        go_Pellet_7_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_7_18_bc = go_Pellet_7_18.AddComponent<BoxCollider2D>();
        go_Pellet_7_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_7_18_bc.isTrigger = true;
        var go_Pellet_7_18_sr = go_Pellet_7_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_7_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_7_18_sr.sharedMaterial = unlitMat;
        go_Pellet_7_18_sr.sortingOrder = 2;
        go_Pellet_7_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_7_18);

        // --- Wall_7_19 ---
        var go_Wall_7_19 = new GameObject("Wall_7_19");
        go_Wall_7_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_19.transform.position = new Vector3(5.5f, 8.0f, 0.0f);
        var go_Wall_7_19_rb = go_Wall_7_19.AddComponent<Rigidbody2D>();
        go_Wall_7_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_19_bc = go_Wall_7_19.AddComponent<BoxCollider2D>();
        go_Wall_7_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_19_sr = go_Wall_7_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_19);

        // --- Wall_7_20 ---
        var go_Wall_7_20 = new GameObject("Wall_7_20");
        go_Wall_7_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_20.transform.position = new Vector3(6.5f, 8.0f, 0.0f);
        var go_Wall_7_20_rb = go_Wall_7_20.AddComponent<Rigidbody2D>();
        go_Wall_7_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_20_bc = go_Wall_7_20.AddComponent<BoxCollider2D>();
        go_Wall_7_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_20_sr = go_Wall_7_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_20);

        // --- Pellet_7_21 ---
        var go_Pellet_7_21 = new GameObject("Pellet_7_21");
        go_Pellet_7_21.tag = "Pellet";
        go_Pellet_7_21.transform.position = new Vector3(7.5f, 8.0f, 0.0f);
        var go_Pellet_7_21_rb = go_Pellet_7_21.AddComponent<Rigidbody2D>();
        go_Pellet_7_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_7_21_bc = go_Pellet_7_21.AddComponent<BoxCollider2D>();
        go_Pellet_7_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_7_21_bc.isTrigger = true;
        var go_Pellet_7_21_sr = go_Pellet_7_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_7_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_7_21_sr.sharedMaterial = unlitMat;
        go_Pellet_7_21_sr.sortingOrder = 2;
        go_Pellet_7_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_7_21);

        // --- Wall_7_22 ---
        var go_Wall_7_22 = new GameObject("Wall_7_22");
        go_Wall_7_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_22.transform.position = new Vector3(8.5f, 8.0f, 0.0f);
        var go_Wall_7_22_rb = go_Wall_7_22.AddComponent<Rigidbody2D>();
        go_Wall_7_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_22_bc = go_Wall_7_22.AddComponent<BoxCollider2D>();
        go_Wall_7_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_22_sr = go_Wall_7_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_22);

        // --- Wall_7_23 ---
        var go_Wall_7_23 = new GameObject("Wall_7_23");
        go_Wall_7_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_23.transform.position = new Vector3(9.5f, 8.0f, 0.0f);
        var go_Wall_7_23_rb = go_Wall_7_23.AddComponent<Rigidbody2D>();
        go_Wall_7_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_23_bc = go_Wall_7_23.AddComponent<BoxCollider2D>();
        go_Wall_7_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_23_sr = go_Wall_7_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_23);

        // --- Wall_7_24 ---
        var go_Wall_7_24 = new GameObject("Wall_7_24");
        go_Wall_7_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_24.transform.position = new Vector3(10.5f, 8.0f, 0.0f);
        var go_Wall_7_24_rb = go_Wall_7_24.AddComponent<Rigidbody2D>();
        go_Wall_7_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_24_bc = go_Wall_7_24.AddComponent<BoxCollider2D>();
        go_Wall_7_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_24_sr = go_Wall_7_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_24);

        // --- Wall_7_25 ---
        var go_Wall_7_25 = new GameObject("Wall_7_25");
        go_Wall_7_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_25.transform.position = new Vector3(11.5f, 8.0f, 0.0f);
        var go_Wall_7_25_rb = go_Wall_7_25.AddComponent<Rigidbody2D>();
        go_Wall_7_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_25_bc = go_Wall_7_25.AddComponent<BoxCollider2D>();
        go_Wall_7_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_25_sr = go_Wall_7_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_25);

        // --- Pellet_7_26 ---
        var go_Pellet_7_26 = new GameObject("Pellet_7_26");
        go_Pellet_7_26.tag = "Pellet";
        go_Pellet_7_26.transform.position = new Vector3(12.5f, 8.0f, 0.0f);
        var go_Pellet_7_26_rb = go_Pellet_7_26.AddComponent<Rigidbody2D>();
        go_Pellet_7_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_7_26_bc = go_Pellet_7_26.AddComponent<BoxCollider2D>();
        go_Pellet_7_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_7_26_bc.isTrigger = true;
        var go_Pellet_7_26_sr = go_Pellet_7_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_7_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_7_26_sr.sharedMaterial = unlitMat;
        go_Pellet_7_26_sr.sortingOrder = 2;
        go_Pellet_7_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_7_26);

        // --- Wall_7_27 ---
        var go_Wall_7_27 = new GameObject("Wall_7_27");
        go_Wall_7_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_7_27.transform.position = new Vector3(13.5f, 8.0f, 0.0f);
        var go_Wall_7_27_rb = go_Wall_7_27.AddComponent<Rigidbody2D>();
        go_Wall_7_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_7_27_bc = go_Wall_7_27.AddComponent<BoxCollider2D>();
        go_Wall_7_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_7_27_sr = go_Wall_7_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_7_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_7_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_7_27);

        // --- Wall_8_0 ---
        var go_Wall_8_0 = new GameObject("Wall_8_0");
        go_Wall_8_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_8_0.transform.position = new Vector3(-13.5f, 7.0f, 0.0f);
        var go_Wall_8_0_rb = go_Wall_8_0.AddComponent<Rigidbody2D>();
        go_Wall_8_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_8_0_bc = go_Wall_8_0.AddComponent<BoxCollider2D>();
        go_Wall_8_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_8_0_sr = go_Wall_8_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_8_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_8_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_8_0);

        // --- Pellet_8_1 ---
        var go_Pellet_8_1 = new GameObject("Pellet_8_1");
        go_Pellet_8_1.tag = "Pellet";
        go_Pellet_8_1.transform.position = new Vector3(-12.5f, 7.0f, 0.0f);
        var go_Pellet_8_1_rb = go_Pellet_8_1.AddComponent<Rigidbody2D>();
        go_Pellet_8_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_1_bc = go_Pellet_8_1.AddComponent<BoxCollider2D>();
        go_Pellet_8_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_1_bc.isTrigger = true;
        var go_Pellet_8_1_sr = go_Pellet_8_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_1_sr.sharedMaterial = unlitMat;
        go_Pellet_8_1_sr.sortingOrder = 2;
        go_Pellet_8_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_1);

        // --- Node_8_1 ---
        var go_Node_8_1 = new GameObject("Node_8_1");
        go_Node_8_1.transform.position = new Vector3(-12.5f, 7.0f, 0.0f);
        var go_Node_8_1_rb = go_Node_8_1.AddComponent<Rigidbody2D>();
        go_Node_8_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_8_1_bc = go_Node_8_1.AddComponent<BoxCollider2D>();
        go_Node_8_1_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_8_1_bc.isTrigger = true;
        go_Node_8_1.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_8_1);

        // --- Pellet_8_2 ---
        var go_Pellet_8_2 = new GameObject("Pellet_8_2");
        go_Pellet_8_2.tag = "Pellet";
        go_Pellet_8_2.transform.position = new Vector3(-11.5f, 7.0f, 0.0f);
        var go_Pellet_8_2_rb = go_Pellet_8_2.AddComponent<Rigidbody2D>();
        go_Pellet_8_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_2_bc = go_Pellet_8_2.AddComponent<BoxCollider2D>();
        go_Pellet_8_2_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_2_bc.isTrigger = true;
        var go_Pellet_8_2_sr = go_Pellet_8_2.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_2_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_2_sr.sharedMaterial = unlitMat;
        go_Pellet_8_2_sr.sortingOrder = 2;
        go_Pellet_8_2.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_2);

        // --- Pellet_8_3 ---
        var go_Pellet_8_3 = new GameObject("Pellet_8_3");
        go_Pellet_8_3.tag = "Pellet";
        go_Pellet_8_3.transform.position = new Vector3(-10.5f, 7.0f, 0.0f);
        var go_Pellet_8_3_rb = go_Pellet_8_3.AddComponent<Rigidbody2D>();
        go_Pellet_8_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_3_bc = go_Pellet_8_3.AddComponent<BoxCollider2D>();
        go_Pellet_8_3_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_3_bc.isTrigger = true;
        var go_Pellet_8_3_sr = go_Pellet_8_3.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_3_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_3_sr.sharedMaterial = unlitMat;
        go_Pellet_8_3_sr.sortingOrder = 2;
        go_Pellet_8_3.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_3);

        // --- Pellet_8_4 ---
        var go_Pellet_8_4 = new GameObject("Pellet_8_4");
        go_Pellet_8_4.tag = "Pellet";
        go_Pellet_8_4.transform.position = new Vector3(-9.5f, 7.0f, 0.0f);
        var go_Pellet_8_4_rb = go_Pellet_8_4.AddComponent<Rigidbody2D>();
        go_Pellet_8_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_4_bc = go_Pellet_8_4.AddComponent<BoxCollider2D>();
        go_Pellet_8_4_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_4_bc.isTrigger = true;
        var go_Pellet_8_4_sr = go_Pellet_8_4.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_4_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_4_sr.sharedMaterial = unlitMat;
        go_Pellet_8_4_sr.sortingOrder = 2;
        go_Pellet_8_4.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_4);

        // --- Pellet_8_5 ---
        var go_Pellet_8_5 = new GameObject("Pellet_8_5");
        go_Pellet_8_5.tag = "Pellet";
        go_Pellet_8_5.transform.position = new Vector3(-8.5f, 7.0f, 0.0f);
        var go_Pellet_8_5_rb = go_Pellet_8_5.AddComponent<Rigidbody2D>();
        go_Pellet_8_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_5_bc = go_Pellet_8_5.AddComponent<BoxCollider2D>();
        go_Pellet_8_5_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_5_bc.isTrigger = true;
        var go_Pellet_8_5_sr = go_Pellet_8_5.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_5_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_5_sr.sharedMaterial = unlitMat;
        go_Pellet_8_5_sr.sortingOrder = 2;
        go_Pellet_8_5.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_5);

        // --- Pellet_8_6 ---
        var go_Pellet_8_6 = new GameObject("Pellet_8_6");
        go_Pellet_8_6.tag = "Pellet";
        go_Pellet_8_6.transform.position = new Vector3(-7.5f, 7.0f, 0.0f);
        var go_Pellet_8_6_rb = go_Pellet_8_6.AddComponent<Rigidbody2D>();
        go_Pellet_8_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_6_bc = go_Pellet_8_6.AddComponent<BoxCollider2D>();
        go_Pellet_8_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_6_bc.isTrigger = true;
        var go_Pellet_8_6_sr = go_Pellet_8_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_6_sr.sharedMaterial = unlitMat;
        go_Pellet_8_6_sr.sortingOrder = 2;
        go_Pellet_8_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_6);

        // --- Node_8_6 ---
        var go_Node_8_6 = new GameObject("Node_8_6");
        go_Node_8_6.transform.position = new Vector3(-7.5f, 7.0f, 0.0f);
        var go_Node_8_6_rb = go_Node_8_6.AddComponent<Rigidbody2D>();
        go_Node_8_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_8_6_bc = go_Node_8_6.AddComponent<BoxCollider2D>();
        go_Node_8_6_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_8_6_bc.isTrigger = true;
        go_Node_8_6.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_8_6);

        // --- Wall_8_7 ---
        var go_Wall_8_7 = new GameObject("Wall_8_7");
        go_Wall_8_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_8_7.transform.position = new Vector3(-6.5f, 7.0f, 0.0f);
        var go_Wall_8_7_rb = go_Wall_8_7.AddComponent<Rigidbody2D>();
        go_Wall_8_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_8_7_bc = go_Wall_8_7.AddComponent<BoxCollider2D>();
        go_Wall_8_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_8_7_sr = go_Wall_8_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_8_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_8_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_8_7);

        // --- Wall_8_8 ---
        var go_Wall_8_8 = new GameObject("Wall_8_8");
        go_Wall_8_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_8_8.transform.position = new Vector3(-5.5f, 7.0f, 0.0f);
        var go_Wall_8_8_rb = go_Wall_8_8.AddComponent<Rigidbody2D>();
        go_Wall_8_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_8_8_bc = go_Wall_8_8.AddComponent<BoxCollider2D>();
        go_Wall_8_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_8_8_sr = go_Wall_8_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_8_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_8_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_8_8);

        // --- Pellet_8_9 ---
        var go_Pellet_8_9 = new GameObject("Pellet_8_9");
        go_Pellet_8_9.tag = "Pellet";
        go_Pellet_8_9.transform.position = new Vector3(-4.5f, 7.0f, 0.0f);
        var go_Pellet_8_9_rb = go_Pellet_8_9.AddComponent<Rigidbody2D>();
        go_Pellet_8_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_9_bc = go_Pellet_8_9.AddComponent<BoxCollider2D>();
        go_Pellet_8_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_9_bc.isTrigger = true;
        var go_Pellet_8_9_sr = go_Pellet_8_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_9_sr.sharedMaterial = unlitMat;
        go_Pellet_8_9_sr.sortingOrder = 2;
        go_Pellet_8_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_9);

        // --- Node_8_9 ---
        var go_Node_8_9 = new GameObject("Node_8_9");
        go_Node_8_9.transform.position = new Vector3(-4.5f, 7.0f, 0.0f);
        var go_Node_8_9_rb = go_Node_8_9.AddComponent<Rigidbody2D>();
        go_Node_8_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_8_9_bc = go_Node_8_9.AddComponent<BoxCollider2D>();
        go_Node_8_9_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_8_9_bc.isTrigger = true;
        go_Node_8_9.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_8_9);

        // --- Pellet_8_10 ---
        var go_Pellet_8_10 = new GameObject("Pellet_8_10");
        go_Pellet_8_10.tag = "Pellet";
        go_Pellet_8_10.transform.position = new Vector3(-3.5f, 7.0f, 0.0f);
        var go_Pellet_8_10_rb = go_Pellet_8_10.AddComponent<Rigidbody2D>();
        go_Pellet_8_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_10_bc = go_Pellet_8_10.AddComponent<BoxCollider2D>();
        go_Pellet_8_10_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_10_bc.isTrigger = true;
        var go_Pellet_8_10_sr = go_Pellet_8_10.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_10_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_10_sr.sharedMaterial = unlitMat;
        go_Pellet_8_10_sr.sortingOrder = 2;
        go_Pellet_8_10.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_10);

        // --- Pellet_8_11 ---
        var go_Pellet_8_11 = new GameObject("Pellet_8_11");
        go_Pellet_8_11.tag = "Pellet";
        go_Pellet_8_11.transform.position = new Vector3(-2.5f, 7.0f, 0.0f);
        var go_Pellet_8_11_rb = go_Pellet_8_11.AddComponent<Rigidbody2D>();
        go_Pellet_8_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_11_bc = go_Pellet_8_11.AddComponent<BoxCollider2D>();
        go_Pellet_8_11_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_11_bc.isTrigger = true;
        var go_Pellet_8_11_sr = go_Pellet_8_11.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_11_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_11_sr.sharedMaterial = unlitMat;
        go_Pellet_8_11_sr.sortingOrder = 2;
        go_Pellet_8_11.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_11);

        // --- Pellet_8_12 ---
        var go_Pellet_8_12 = new GameObject("Pellet_8_12");
        go_Pellet_8_12.tag = "Pellet";
        go_Pellet_8_12.transform.position = new Vector3(-1.5f, 7.0f, 0.0f);
        var go_Pellet_8_12_rb = go_Pellet_8_12.AddComponent<Rigidbody2D>();
        go_Pellet_8_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_12_bc = go_Pellet_8_12.AddComponent<BoxCollider2D>();
        go_Pellet_8_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_12_bc.isTrigger = true;
        var go_Pellet_8_12_sr = go_Pellet_8_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_12_sr.sharedMaterial = unlitMat;
        go_Pellet_8_12_sr.sortingOrder = 2;
        go_Pellet_8_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_12);

        // --- Node_8_12 ---
        var go_Node_8_12 = new GameObject("Node_8_12");
        go_Node_8_12.transform.position = new Vector3(-1.5f, 7.0f, 0.0f);
        var go_Node_8_12_rb = go_Node_8_12.AddComponent<Rigidbody2D>();
        go_Node_8_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_8_12_bc = go_Node_8_12.AddComponent<BoxCollider2D>();
        go_Node_8_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_8_12_bc.isTrigger = true;
        go_Node_8_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_8_12);

        // --- Wall_8_13 ---
        var go_Wall_8_13 = new GameObject("Wall_8_13");
        go_Wall_8_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_8_13.transform.position = new Vector3(-0.5f, 7.0f, 0.0f);
        var go_Wall_8_13_rb = go_Wall_8_13.AddComponent<Rigidbody2D>();
        go_Wall_8_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_8_13_bc = go_Wall_8_13.AddComponent<BoxCollider2D>();
        go_Wall_8_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_8_13_sr = go_Wall_8_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_8_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_8_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_8_13);

        // --- Wall_8_14 ---
        var go_Wall_8_14 = new GameObject("Wall_8_14");
        go_Wall_8_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_8_14.transform.position = new Vector3(0.5f, 7.0f, 0.0f);
        var go_Wall_8_14_rb = go_Wall_8_14.AddComponent<Rigidbody2D>();
        go_Wall_8_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_8_14_bc = go_Wall_8_14.AddComponent<BoxCollider2D>();
        go_Wall_8_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_8_14_sr = go_Wall_8_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_8_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_8_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_8_14);

        // --- Pellet_8_15 ---
        var go_Pellet_8_15 = new GameObject("Pellet_8_15");
        go_Pellet_8_15.tag = "Pellet";
        go_Pellet_8_15.transform.position = new Vector3(1.5f, 7.0f, 0.0f);
        var go_Pellet_8_15_rb = go_Pellet_8_15.AddComponent<Rigidbody2D>();
        go_Pellet_8_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_15_bc = go_Pellet_8_15.AddComponent<BoxCollider2D>();
        go_Pellet_8_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_15_bc.isTrigger = true;
        var go_Pellet_8_15_sr = go_Pellet_8_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_15_sr.sharedMaterial = unlitMat;
        go_Pellet_8_15_sr.sortingOrder = 2;
        go_Pellet_8_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_15);

        // --- Node_8_15 ---
        var go_Node_8_15 = new GameObject("Node_8_15");
        go_Node_8_15.transform.position = new Vector3(1.5f, 7.0f, 0.0f);
        var go_Node_8_15_rb = go_Node_8_15.AddComponent<Rigidbody2D>();
        go_Node_8_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_8_15_bc = go_Node_8_15.AddComponent<BoxCollider2D>();
        go_Node_8_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_8_15_bc.isTrigger = true;
        go_Node_8_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_8_15);

        // --- Pellet_8_16 ---
        var go_Pellet_8_16 = new GameObject("Pellet_8_16");
        go_Pellet_8_16.tag = "Pellet";
        go_Pellet_8_16.transform.position = new Vector3(2.5f, 7.0f, 0.0f);
        var go_Pellet_8_16_rb = go_Pellet_8_16.AddComponent<Rigidbody2D>();
        go_Pellet_8_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_16_bc = go_Pellet_8_16.AddComponent<BoxCollider2D>();
        go_Pellet_8_16_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_16_bc.isTrigger = true;
        var go_Pellet_8_16_sr = go_Pellet_8_16.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_16_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_16_sr.sharedMaterial = unlitMat;
        go_Pellet_8_16_sr.sortingOrder = 2;
        go_Pellet_8_16.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_16);

        // --- Pellet_8_17 ---
        var go_Pellet_8_17 = new GameObject("Pellet_8_17");
        go_Pellet_8_17.tag = "Pellet";
        go_Pellet_8_17.transform.position = new Vector3(3.5f, 7.0f, 0.0f);
        var go_Pellet_8_17_rb = go_Pellet_8_17.AddComponent<Rigidbody2D>();
        go_Pellet_8_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_17_bc = go_Pellet_8_17.AddComponent<BoxCollider2D>();
        go_Pellet_8_17_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_17_bc.isTrigger = true;
        var go_Pellet_8_17_sr = go_Pellet_8_17.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_17_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_17_sr.sharedMaterial = unlitMat;
        go_Pellet_8_17_sr.sortingOrder = 2;
        go_Pellet_8_17.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_17);

        // --- Pellet_8_18 ---
        var go_Pellet_8_18 = new GameObject("Pellet_8_18");
        go_Pellet_8_18.tag = "Pellet";
        go_Pellet_8_18.transform.position = new Vector3(4.5f, 7.0f, 0.0f);
        var go_Pellet_8_18_rb = go_Pellet_8_18.AddComponent<Rigidbody2D>();
        go_Pellet_8_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_18_bc = go_Pellet_8_18.AddComponent<BoxCollider2D>();
        go_Pellet_8_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_18_bc.isTrigger = true;
        var go_Pellet_8_18_sr = go_Pellet_8_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_18_sr.sharedMaterial = unlitMat;
        go_Pellet_8_18_sr.sortingOrder = 2;
        go_Pellet_8_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_18);

        // --- Node_8_18 ---
        var go_Node_8_18 = new GameObject("Node_8_18");
        go_Node_8_18.transform.position = new Vector3(4.5f, 7.0f, 0.0f);
        var go_Node_8_18_rb = go_Node_8_18.AddComponent<Rigidbody2D>();
        go_Node_8_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_8_18_bc = go_Node_8_18.AddComponent<BoxCollider2D>();
        go_Node_8_18_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_8_18_bc.isTrigger = true;
        go_Node_8_18.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_8_18);

        // --- Wall_8_19 ---
        var go_Wall_8_19 = new GameObject("Wall_8_19");
        go_Wall_8_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_8_19.transform.position = new Vector3(5.5f, 7.0f, 0.0f);
        var go_Wall_8_19_rb = go_Wall_8_19.AddComponent<Rigidbody2D>();
        go_Wall_8_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_8_19_bc = go_Wall_8_19.AddComponent<BoxCollider2D>();
        go_Wall_8_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_8_19_sr = go_Wall_8_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_8_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_8_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_8_19);

        // --- Wall_8_20 ---
        var go_Wall_8_20 = new GameObject("Wall_8_20");
        go_Wall_8_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_8_20.transform.position = new Vector3(6.5f, 7.0f, 0.0f);
        var go_Wall_8_20_rb = go_Wall_8_20.AddComponent<Rigidbody2D>();
        go_Wall_8_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_8_20_bc = go_Wall_8_20.AddComponent<BoxCollider2D>();
        go_Wall_8_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_8_20_sr = go_Wall_8_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_8_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_8_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_8_20);

        // --- Pellet_8_21 ---
        var go_Pellet_8_21 = new GameObject("Pellet_8_21");
        go_Pellet_8_21.tag = "Pellet";
        go_Pellet_8_21.transform.position = new Vector3(7.5f, 7.0f, 0.0f);
        var go_Pellet_8_21_rb = go_Pellet_8_21.AddComponent<Rigidbody2D>();
        go_Pellet_8_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_21_bc = go_Pellet_8_21.AddComponent<BoxCollider2D>();
        go_Pellet_8_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_21_bc.isTrigger = true;
        var go_Pellet_8_21_sr = go_Pellet_8_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_21_sr.sharedMaterial = unlitMat;
        go_Pellet_8_21_sr.sortingOrder = 2;
        go_Pellet_8_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_21);

        // --- Node_8_21 ---
        var go_Node_8_21 = new GameObject("Node_8_21");
        go_Node_8_21.transform.position = new Vector3(7.5f, 7.0f, 0.0f);
        var go_Node_8_21_rb = go_Node_8_21.AddComponent<Rigidbody2D>();
        go_Node_8_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_8_21_bc = go_Node_8_21.AddComponent<BoxCollider2D>();
        go_Node_8_21_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_8_21_bc.isTrigger = true;
        go_Node_8_21.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_8_21);

        // --- Pellet_8_22 ---
        var go_Pellet_8_22 = new GameObject("Pellet_8_22");
        go_Pellet_8_22.tag = "Pellet";
        go_Pellet_8_22.transform.position = new Vector3(8.5f, 7.0f, 0.0f);
        var go_Pellet_8_22_rb = go_Pellet_8_22.AddComponent<Rigidbody2D>();
        go_Pellet_8_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_22_bc = go_Pellet_8_22.AddComponent<BoxCollider2D>();
        go_Pellet_8_22_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_22_bc.isTrigger = true;
        var go_Pellet_8_22_sr = go_Pellet_8_22.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_22_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_22_sr.sharedMaterial = unlitMat;
        go_Pellet_8_22_sr.sortingOrder = 2;
        go_Pellet_8_22.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_22);

        // --- Pellet_8_23 ---
        var go_Pellet_8_23 = new GameObject("Pellet_8_23");
        go_Pellet_8_23.tag = "Pellet";
        go_Pellet_8_23.transform.position = new Vector3(9.5f, 7.0f, 0.0f);
        var go_Pellet_8_23_rb = go_Pellet_8_23.AddComponent<Rigidbody2D>();
        go_Pellet_8_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_23_bc = go_Pellet_8_23.AddComponent<BoxCollider2D>();
        go_Pellet_8_23_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_23_bc.isTrigger = true;
        var go_Pellet_8_23_sr = go_Pellet_8_23.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_23_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_23_sr.sharedMaterial = unlitMat;
        go_Pellet_8_23_sr.sortingOrder = 2;
        go_Pellet_8_23.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_23);

        // --- Pellet_8_24 ---
        var go_Pellet_8_24 = new GameObject("Pellet_8_24");
        go_Pellet_8_24.tag = "Pellet";
        go_Pellet_8_24.transform.position = new Vector3(10.5f, 7.0f, 0.0f);
        var go_Pellet_8_24_rb = go_Pellet_8_24.AddComponent<Rigidbody2D>();
        go_Pellet_8_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_24_bc = go_Pellet_8_24.AddComponent<BoxCollider2D>();
        go_Pellet_8_24_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_24_bc.isTrigger = true;
        var go_Pellet_8_24_sr = go_Pellet_8_24.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_24_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_24_sr.sharedMaterial = unlitMat;
        go_Pellet_8_24_sr.sortingOrder = 2;
        go_Pellet_8_24.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_24);

        // --- Pellet_8_25 ---
        var go_Pellet_8_25 = new GameObject("Pellet_8_25");
        go_Pellet_8_25.tag = "Pellet";
        go_Pellet_8_25.transform.position = new Vector3(11.5f, 7.0f, 0.0f);
        var go_Pellet_8_25_rb = go_Pellet_8_25.AddComponent<Rigidbody2D>();
        go_Pellet_8_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_25_bc = go_Pellet_8_25.AddComponent<BoxCollider2D>();
        go_Pellet_8_25_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_25_bc.isTrigger = true;
        var go_Pellet_8_25_sr = go_Pellet_8_25.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_25_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_25_sr.sharedMaterial = unlitMat;
        go_Pellet_8_25_sr.sortingOrder = 2;
        go_Pellet_8_25.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_25);

        // --- Pellet_8_26 ---
        var go_Pellet_8_26 = new GameObject("Pellet_8_26");
        go_Pellet_8_26.tag = "Pellet";
        go_Pellet_8_26.transform.position = new Vector3(12.5f, 7.0f, 0.0f);
        var go_Pellet_8_26_rb = go_Pellet_8_26.AddComponent<Rigidbody2D>();
        go_Pellet_8_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_8_26_bc = go_Pellet_8_26.AddComponent<BoxCollider2D>();
        go_Pellet_8_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_8_26_bc.isTrigger = true;
        var go_Pellet_8_26_sr = go_Pellet_8_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_8_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_8_26_sr.sharedMaterial = unlitMat;
        go_Pellet_8_26_sr.sortingOrder = 2;
        go_Pellet_8_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_8_26);

        // --- Node_8_26 ---
        var go_Node_8_26 = new GameObject("Node_8_26");
        go_Node_8_26.transform.position = new Vector3(12.5f, 7.0f, 0.0f);
        var go_Node_8_26_rb = go_Node_8_26.AddComponent<Rigidbody2D>();
        go_Node_8_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_8_26_bc = go_Node_8_26.AddComponent<BoxCollider2D>();
        go_Node_8_26_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_8_26_bc.isTrigger = true;
        go_Node_8_26.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_8_26);

        // --- Wall_8_27 ---
        var go_Wall_8_27 = new GameObject("Wall_8_27");
        go_Wall_8_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_8_27.transform.position = new Vector3(13.5f, 7.0f, 0.0f);
        var go_Wall_8_27_rb = go_Wall_8_27.AddComponent<Rigidbody2D>();
        go_Wall_8_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_8_27_bc = go_Wall_8_27.AddComponent<BoxCollider2D>();
        go_Wall_8_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_8_27_sr = go_Wall_8_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_8_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_8_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_8_27);

        // --- Wall_9_0 ---
        var go_Wall_9_0 = new GameObject("Wall_9_0");
        go_Wall_9_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_0.transform.position = new Vector3(-13.5f, 6.0f, 0.0f);
        var go_Wall_9_0_rb = go_Wall_9_0.AddComponent<Rigidbody2D>();
        go_Wall_9_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_0_bc = go_Wall_9_0.AddComponent<BoxCollider2D>();
        go_Wall_9_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_0_sr = go_Wall_9_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_0);

        // --- Wall_9_1 ---
        var go_Wall_9_1 = new GameObject("Wall_9_1");
        go_Wall_9_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_1.transform.position = new Vector3(-12.5f, 6.0f, 0.0f);
        var go_Wall_9_1_rb = go_Wall_9_1.AddComponent<Rigidbody2D>();
        go_Wall_9_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_1_bc = go_Wall_9_1.AddComponent<BoxCollider2D>();
        go_Wall_9_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_1_sr = go_Wall_9_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_1);

        // --- Wall_9_2 ---
        var go_Wall_9_2 = new GameObject("Wall_9_2");
        go_Wall_9_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_2.transform.position = new Vector3(-11.5f, 6.0f, 0.0f);
        var go_Wall_9_2_rb = go_Wall_9_2.AddComponent<Rigidbody2D>();
        go_Wall_9_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_2_bc = go_Wall_9_2.AddComponent<BoxCollider2D>();
        go_Wall_9_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_2_sr = go_Wall_9_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_2);

        // --- Wall_9_3 ---
        var go_Wall_9_3 = new GameObject("Wall_9_3");
        go_Wall_9_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_3.transform.position = new Vector3(-10.5f, 6.0f, 0.0f);
        var go_Wall_9_3_rb = go_Wall_9_3.AddComponent<Rigidbody2D>();
        go_Wall_9_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_3_bc = go_Wall_9_3.AddComponent<BoxCollider2D>();
        go_Wall_9_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_3_sr = go_Wall_9_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_3);

        // --- Wall_9_4 ---
        var go_Wall_9_4 = new GameObject("Wall_9_4");
        go_Wall_9_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_4.transform.position = new Vector3(-9.5f, 6.0f, 0.0f);
        var go_Wall_9_4_rb = go_Wall_9_4.AddComponent<Rigidbody2D>();
        go_Wall_9_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_4_bc = go_Wall_9_4.AddComponent<BoxCollider2D>();
        go_Wall_9_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_4_sr = go_Wall_9_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_4);

        // --- Wall_9_5 ---
        var go_Wall_9_5 = new GameObject("Wall_9_5");
        go_Wall_9_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_5.transform.position = new Vector3(-8.5f, 6.0f, 0.0f);
        var go_Wall_9_5_rb = go_Wall_9_5.AddComponent<Rigidbody2D>();
        go_Wall_9_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_5_bc = go_Wall_9_5.AddComponent<BoxCollider2D>();
        go_Wall_9_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_5_sr = go_Wall_9_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_5);

        // --- Pellet_9_6 ---
        var go_Pellet_9_6 = new GameObject("Pellet_9_6");
        go_Pellet_9_6.tag = "Pellet";
        go_Pellet_9_6.transform.position = new Vector3(-7.5f, 6.0f, 0.0f);
        var go_Pellet_9_6_rb = go_Pellet_9_6.AddComponent<Rigidbody2D>();
        go_Pellet_9_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_9_6_bc = go_Pellet_9_6.AddComponent<BoxCollider2D>();
        go_Pellet_9_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_9_6_bc.isTrigger = true;
        var go_Pellet_9_6_sr = go_Pellet_9_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_9_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_9_6_sr.sharedMaterial = unlitMat;
        go_Pellet_9_6_sr.sortingOrder = 2;
        go_Pellet_9_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_9_6);

        // --- Wall_9_7 ---
        var go_Wall_9_7 = new GameObject("Wall_9_7");
        go_Wall_9_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_7.transform.position = new Vector3(-6.5f, 6.0f, 0.0f);
        var go_Wall_9_7_rb = go_Wall_9_7.AddComponent<Rigidbody2D>();
        go_Wall_9_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_7_bc = go_Wall_9_7.AddComponent<BoxCollider2D>();
        go_Wall_9_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_7_sr = go_Wall_9_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_7);

        // --- Wall_9_8 ---
        var go_Wall_9_8 = new GameObject("Wall_9_8");
        go_Wall_9_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_8.transform.position = new Vector3(-5.5f, 6.0f, 0.0f);
        var go_Wall_9_8_rb = go_Wall_9_8.AddComponent<Rigidbody2D>();
        go_Wall_9_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_8_bc = go_Wall_9_8.AddComponent<BoxCollider2D>();
        go_Wall_9_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_8_sr = go_Wall_9_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_8);

        // --- Wall_9_9 ---
        var go_Wall_9_9 = new GameObject("Wall_9_9");
        go_Wall_9_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_9.transform.position = new Vector3(-4.5f, 6.0f, 0.0f);
        var go_Wall_9_9_rb = go_Wall_9_9.AddComponent<Rigidbody2D>();
        go_Wall_9_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_9_bc = go_Wall_9_9.AddComponent<BoxCollider2D>();
        go_Wall_9_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_9_sr = go_Wall_9_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_9);

        // --- Wall_9_10 ---
        var go_Wall_9_10 = new GameObject("Wall_9_10");
        go_Wall_9_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_10.transform.position = new Vector3(-3.5f, 6.0f, 0.0f);
        var go_Wall_9_10_rb = go_Wall_9_10.AddComponent<Rigidbody2D>();
        go_Wall_9_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_10_bc = go_Wall_9_10.AddComponent<BoxCollider2D>();
        go_Wall_9_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_10_sr = go_Wall_9_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_10);

        // --- Wall_9_11 ---
        var go_Wall_9_11 = new GameObject("Wall_9_11");
        go_Wall_9_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_11.transform.position = new Vector3(-2.5f, 6.0f, 0.0f);
        var go_Wall_9_11_rb = go_Wall_9_11.AddComponent<Rigidbody2D>();
        go_Wall_9_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_11_bc = go_Wall_9_11.AddComponent<BoxCollider2D>();
        go_Wall_9_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_11_sr = go_Wall_9_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_11);

        // --- Wall_9_13 ---
        var go_Wall_9_13 = new GameObject("Wall_9_13");
        go_Wall_9_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_13.transform.position = new Vector3(-0.5f, 6.0f, 0.0f);
        var go_Wall_9_13_rb = go_Wall_9_13.AddComponent<Rigidbody2D>();
        go_Wall_9_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_13_bc = go_Wall_9_13.AddComponent<BoxCollider2D>();
        go_Wall_9_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_13_sr = go_Wall_9_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_13);

        // --- Wall_9_14 ---
        var go_Wall_9_14 = new GameObject("Wall_9_14");
        go_Wall_9_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_14.transform.position = new Vector3(0.5f, 6.0f, 0.0f);
        var go_Wall_9_14_rb = go_Wall_9_14.AddComponent<Rigidbody2D>();
        go_Wall_9_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_14_bc = go_Wall_9_14.AddComponent<BoxCollider2D>();
        go_Wall_9_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_14_sr = go_Wall_9_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_14);

        // --- Wall_9_16 ---
        var go_Wall_9_16 = new GameObject("Wall_9_16");
        go_Wall_9_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_16.transform.position = new Vector3(2.5f, 6.0f, 0.0f);
        var go_Wall_9_16_rb = go_Wall_9_16.AddComponent<Rigidbody2D>();
        go_Wall_9_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_16_bc = go_Wall_9_16.AddComponent<BoxCollider2D>();
        go_Wall_9_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_16_sr = go_Wall_9_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_16);

        // --- Wall_9_17 ---
        var go_Wall_9_17 = new GameObject("Wall_9_17");
        go_Wall_9_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_17.transform.position = new Vector3(3.5f, 6.0f, 0.0f);
        var go_Wall_9_17_rb = go_Wall_9_17.AddComponent<Rigidbody2D>();
        go_Wall_9_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_17_bc = go_Wall_9_17.AddComponent<BoxCollider2D>();
        go_Wall_9_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_17_sr = go_Wall_9_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_17);

        // --- Wall_9_18 ---
        var go_Wall_9_18 = new GameObject("Wall_9_18");
        go_Wall_9_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_18.transform.position = new Vector3(4.5f, 6.0f, 0.0f);
        var go_Wall_9_18_rb = go_Wall_9_18.AddComponent<Rigidbody2D>();
        go_Wall_9_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_18_bc = go_Wall_9_18.AddComponent<BoxCollider2D>();
        go_Wall_9_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_18_sr = go_Wall_9_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_18);

        // --- Wall_9_19 ---
        var go_Wall_9_19 = new GameObject("Wall_9_19");
        go_Wall_9_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_19.transform.position = new Vector3(5.5f, 6.0f, 0.0f);
        var go_Wall_9_19_rb = go_Wall_9_19.AddComponent<Rigidbody2D>();
        go_Wall_9_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_19_bc = go_Wall_9_19.AddComponent<BoxCollider2D>();
        go_Wall_9_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_19_sr = go_Wall_9_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_19);

        // --- Wall_9_20 ---
        var go_Wall_9_20 = new GameObject("Wall_9_20");
        go_Wall_9_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_20.transform.position = new Vector3(6.5f, 6.0f, 0.0f);
        var go_Wall_9_20_rb = go_Wall_9_20.AddComponent<Rigidbody2D>();
        go_Wall_9_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_20_bc = go_Wall_9_20.AddComponent<BoxCollider2D>();
        go_Wall_9_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_20_sr = go_Wall_9_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_20);

        // --- Pellet_9_21 ---
        var go_Pellet_9_21 = new GameObject("Pellet_9_21");
        go_Pellet_9_21.tag = "Pellet";
        go_Pellet_9_21.transform.position = new Vector3(7.5f, 6.0f, 0.0f);
        var go_Pellet_9_21_rb = go_Pellet_9_21.AddComponent<Rigidbody2D>();
        go_Pellet_9_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_9_21_bc = go_Pellet_9_21.AddComponent<BoxCollider2D>();
        go_Pellet_9_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_9_21_bc.isTrigger = true;
        var go_Pellet_9_21_sr = go_Pellet_9_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_9_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_9_21_sr.sharedMaterial = unlitMat;
        go_Pellet_9_21_sr.sortingOrder = 2;
        go_Pellet_9_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_9_21);

        // --- Wall_9_22 ---
        var go_Wall_9_22 = new GameObject("Wall_9_22");
        go_Wall_9_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_22.transform.position = new Vector3(8.5f, 6.0f, 0.0f);
        var go_Wall_9_22_rb = go_Wall_9_22.AddComponent<Rigidbody2D>();
        go_Wall_9_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_22_bc = go_Wall_9_22.AddComponent<BoxCollider2D>();
        go_Wall_9_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_22_sr = go_Wall_9_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_22);

        // --- Wall_9_23 ---
        var go_Wall_9_23 = new GameObject("Wall_9_23");
        go_Wall_9_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_23.transform.position = new Vector3(9.5f, 6.0f, 0.0f);
        var go_Wall_9_23_rb = go_Wall_9_23.AddComponent<Rigidbody2D>();
        go_Wall_9_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_23_bc = go_Wall_9_23.AddComponent<BoxCollider2D>();
        go_Wall_9_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_23_sr = go_Wall_9_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_23);

        // --- Wall_9_24 ---
        var go_Wall_9_24 = new GameObject("Wall_9_24");
        go_Wall_9_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_24.transform.position = new Vector3(10.5f, 6.0f, 0.0f);
        var go_Wall_9_24_rb = go_Wall_9_24.AddComponent<Rigidbody2D>();
        go_Wall_9_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_24_bc = go_Wall_9_24.AddComponent<BoxCollider2D>();
        go_Wall_9_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_24_sr = go_Wall_9_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_24);

        // --- Wall_9_25 ---
        var go_Wall_9_25 = new GameObject("Wall_9_25");
        go_Wall_9_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_25.transform.position = new Vector3(11.5f, 6.0f, 0.0f);
        var go_Wall_9_25_rb = go_Wall_9_25.AddComponent<Rigidbody2D>();
        go_Wall_9_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_25_bc = go_Wall_9_25.AddComponent<BoxCollider2D>();
        go_Wall_9_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_25_sr = go_Wall_9_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_25);

        // --- Wall_9_26 ---
        var go_Wall_9_26 = new GameObject("Wall_9_26");
        go_Wall_9_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_26.transform.position = new Vector3(12.5f, 6.0f, 0.0f);
        var go_Wall_9_26_rb = go_Wall_9_26.AddComponent<Rigidbody2D>();
        go_Wall_9_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_26_bc = go_Wall_9_26.AddComponent<BoxCollider2D>();
        go_Wall_9_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_26_sr = go_Wall_9_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_26);

        // --- Wall_9_27 ---
        var go_Wall_9_27 = new GameObject("Wall_9_27");
        go_Wall_9_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_9_27.transform.position = new Vector3(13.5f, 6.0f, 0.0f);
        var go_Wall_9_27_rb = go_Wall_9_27.AddComponent<Rigidbody2D>();
        go_Wall_9_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_9_27_bc = go_Wall_9_27.AddComponent<BoxCollider2D>();
        go_Wall_9_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_9_27_sr = go_Wall_9_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_9_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_9_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_9_27);

        // --- Wall_10_0 ---
        var go_Wall_10_0 = new GameObject("Wall_10_0");
        go_Wall_10_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_0.transform.position = new Vector3(-13.5f, 5.0f, 0.0f);
        var go_Wall_10_0_rb = go_Wall_10_0.AddComponent<Rigidbody2D>();
        go_Wall_10_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_0_bc = go_Wall_10_0.AddComponent<BoxCollider2D>();
        go_Wall_10_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_0_sr = go_Wall_10_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_0);

        // --- Wall_10_1 ---
        var go_Wall_10_1 = new GameObject("Wall_10_1");
        go_Wall_10_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_1.transform.position = new Vector3(-12.5f, 5.0f, 0.0f);
        var go_Wall_10_1_rb = go_Wall_10_1.AddComponent<Rigidbody2D>();
        go_Wall_10_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_1_bc = go_Wall_10_1.AddComponent<BoxCollider2D>();
        go_Wall_10_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_1_sr = go_Wall_10_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_1);

        // --- Wall_10_2 ---
        var go_Wall_10_2 = new GameObject("Wall_10_2");
        go_Wall_10_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_2.transform.position = new Vector3(-11.5f, 5.0f, 0.0f);
        var go_Wall_10_2_rb = go_Wall_10_2.AddComponent<Rigidbody2D>();
        go_Wall_10_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_2_bc = go_Wall_10_2.AddComponent<BoxCollider2D>();
        go_Wall_10_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_2_sr = go_Wall_10_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_2);

        // --- Wall_10_3 ---
        var go_Wall_10_3 = new GameObject("Wall_10_3");
        go_Wall_10_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_3.transform.position = new Vector3(-10.5f, 5.0f, 0.0f);
        var go_Wall_10_3_rb = go_Wall_10_3.AddComponent<Rigidbody2D>();
        go_Wall_10_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_3_bc = go_Wall_10_3.AddComponent<BoxCollider2D>();
        go_Wall_10_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_3_sr = go_Wall_10_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_3);

        // --- Wall_10_4 ---
        var go_Wall_10_4 = new GameObject("Wall_10_4");
        go_Wall_10_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_4.transform.position = new Vector3(-9.5f, 5.0f, 0.0f);
        var go_Wall_10_4_rb = go_Wall_10_4.AddComponent<Rigidbody2D>();
        go_Wall_10_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_4_bc = go_Wall_10_4.AddComponent<BoxCollider2D>();
        go_Wall_10_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_4_sr = go_Wall_10_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_4);

        // --- Wall_10_5 ---
        var go_Wall_10_5 = new GameObject("Wall_10_5");
        go_Wall_10_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_5.transform.position = new Vector3(-8.5f, 5.0f, 0.0f);
        var go_Wall_10_5_rb = go_Wall_10_5.AddComponent<Rigidbody2D>();
        go_Wall_10_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_5_bc = go_Wall_10_5.AddComponent<BoxCollider2D>();
        go_Wall_10_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_5_sr = go_Wall_10_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_5);

        // --- Pellet_10_6 ---
        var go_Pellet_10_6 = new GameObject("Pellet_10_6");
        go_Pellet_10_6.tag = "Pellet";
        go_Pellet_10_6.transform.position = new Vector3(-7.5f, 5.0f, 0.0f);
        var go_Pellet_10_6_rb = go_Pellet_10_6.AddComponent<Rigidbody2D>();
        go_Pellet_10_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_10_6_bc = go_Pellet_10_6.AddComponent<BoxCollider2D>();
        go_Pellet_10_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_10_6_bc.isTrigger = true;
        var go_Pellet_10_6_sr = go_Pellet_10_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_10_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_10_6_sr.sharedMaterial = unlitMat;
        go_Pellet_10_6_sr.sortingOrder = 2;
        go_Pellet_10_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_10_6);

        // --- Wall_10_7 ---
        var go_Wall_10_7 = new GameObject("Wall_10_7");
        go_Wall_10_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_7.transform.position = new Vector3(-6.5f, 5.0f, 0.0f);
        var go_Wall_10_7_rb = go_Wall_10_7.AddComponent<Rigidbody2D>();
        go_Wall_10_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_7_bc = go_Wall_10_7.AddComponent<BoxCollider2D>();
        go_Wall_10_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_7_sr = go_Wall_10_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_7);

        // --- Wall_10_8 ---
        var go_Wall_10_8 = new GameObject("Wall_10_8");
        go_Wall_10_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_8.transform.position = new Vector3(-5.5f, 5.0f, 0.0f);
        var go_Wall_10_8_rb = go_Wall_10_8.AddComponent<Rigidbody2D>();
        go_Wall_10_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_8_bc = go_Wall_10_8.AddComponent<BoxCollider2D>();
        go_Wall_10_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_8_sr = go_Wall_10_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_8);

        // --- Wall_10_9 ---
        var go_Wall_10_9 = new GameObject("Wall_10_9");
        go_Wall_10_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_9.transform.position = new Vector3(-4.5f, 5.0f, 0.0f);
        var go_Wall_10_9_rb = go_Wall_10_9.AddComponent<Rigidbody2D>();
        go_Wall_10_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_9_bc = go_Wall_10_9.AddComponent<BoxCollider2D>();
        go_Wall_10_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_9_sr = go_Wall_10_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_9);

        // --- Wall_10_10 ---
        var go_Wall_10_10 = new GameObject("Wall_10_10");
        go_Wall_10_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_10.transform.position = new Vector3(-3.5f, 5.0f, 0.0f);
        var go_Wall_10_10_rb = go_Wall_10_10.AddComponent<Rigidbody2D>();
        go_Wall_10_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_10_bc = go_Wall_10_10.AddComponent<BoxCollider2D>();
        go_Wall_10_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_10_sr = go_Wall_10_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_10);

        // --- Wall_10_11 ---
        var go_Wall_10_11 = new GameObject("Wall_10_11");
        go_Wall_10_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_11.transform.position = new Vector3(-2.5f, 5.0f, 0.0f);
        var go_Wall_10_11_rb = go_Wall_10_11.AddComponent<Rigidbody2D>();
        go_Wall_10_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_11_bc = go_Wall_10_11.AddComponent<BoxCollider2D>();
        go_Wall_10_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_11_sr = go_Wall_10_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_11);

        // --- Wall_10_13 ---
        var go_Wall_10_13 = new GameObject("Wall_10_13");
        go_Wall_10_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_13.transform.position = new Vector3(-0.5f, 5.0f, 0.0f);
        var go_Wall_10_13_rb = go_Wall_10_13.AddComponent<Rigidbody2D>();
        go_Wall_10_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_13_bc = go_Wall_10_13.AddComponent<BoxCollider2D>();
        go_Wall_10_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_13_sr = go_Wall_10_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_13);

        // --- Wall_10_14 ---
        var go_Wall_10_14 = new GameObject("Wall_10_14");
        go_Wall_10_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_14.transform.position = new Vector3(0.5f, 5.0f, 0.0f);
        var go_Wall_10_14_rb = go_Wall_10_14.AddComponent<Rigidbody2D>();
        go_Wall_10_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_14_bc = go_Wall_10_14.AddComponent<BoxCollider2D>();
        go_Wall_10_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_14_sr = go_Wall_10_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_14);

        // --- Wall_10_16 ---
        var go_Wall_10_16 = new GameObject("Wall_10_16");
        go_Wall_10_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_16.transform.position = new Vector3(2.5f, 5.0f, 0.0f);
        var go_Wall_10_16_rb = go_Wall_10_16.AddComponent<Rigidbody2D>();
        go_Wall_10_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_16_bc = go_Wall_10_16.AddComponent<BoxCollider2D>();
        go_Wall_10_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_16_sr = go_Wall_10_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_16);

        // --- Wall_10_17 ---
        var go_Wall_10_17 = new GameObject("Wall_10_17");
        go_Wall_10_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_17.transform.position = new Vector3(3.5f, 5.0f, 0.0f);
        var go_Wall_10_17_rb = go_Wall_10_17.AddComponent<Rigidbody2D>();
        go_Wall_10_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_17_bc = go_Wall_10_17.AddComponent<BoxCollider2D>();
        go_Wall_10_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_17_sr = go_Wall_10_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_17);

        // --- Wall_10_18 ---
        var go_Wall_10_18 = new GameObject("Wall_10_18");
        go_Wall_10_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_18.transform.position = new Vector3(4.5f, 5.0f, 0.0f);
        var go_Wall_10_18_rb = go_Wall_10_18.AddComponent<Rigidbody2D>();
        go_Wall_10_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_18_bc = go_Wall_10_18.AddComponent<BoxCollider2D>();
        go_Wall_10_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_18_sr = go_Wall_10_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_18);

        // --- Wall_10_19 ---
        var go_Wall_10_19 = new GameObject("Wall_10_19");
        go_Wall_10_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_19.transform.position = new Vector3(5.5f, 5.0f, 0.0f);
        var go_Wall_10_19_rb = go_Wall_10_19.AddComponent<Rigidbody2D>();
        go_Wall_10_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_19_bc = go_Wall_10_19.AddComponent<BoxCollider2D>();
        go_Wall_10_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_19_sr = go_Wall_10_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_19);

        // --- Wall_10_20 ---
        var go_Wall_10_20 = new GameObject("Wall_10_20");
        go_Wall_10_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_20.transform.position = new Vector3(6.5f, 5.0f, 0.0f);
        var go_Wall_10_20_rb = go_Wall_10_20.AddComponent<Rigidbody2D>();
        go_Wall_10_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_20_bc = go_Wall_10_20.AddComponent<BoxCollider2D>();
        go_Wall_10_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_20_sr = go_Wall_10_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_20);

        // --- Pellet_10_21 ---
        var go_Pellet_10_21 = new GameObject("Pellet_10_21");
        go_Pellet_10_21.tag = "Pellet";
        go_Pellet_10_21.transform.position = new Vector3(7.5f, 5.0f, 0.0f);
        var go_Pellet_10_21_rb = go_Pellet_10_21.AddComponent<Rigidbody2D>();
        go_Pellet_10_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_10_21_bc = go_Pellet_10_21.AddComponent<BoxCollider2D>();
        go_Pellet_10_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_10_21_bc.isTrigger = true;
        var go_Pellet_10_21_sr = go_Pellet_10_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_10_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_10_21_sr.sharedMaterial = unlitMat;
        go_Pellet_10_21_sr.sortingOrder = 2;
        go_Pellet_10_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_10_21);

        // --- Wall_10_22 ---
        var go_Wall_10_22 = new GameObject("Wall_10_22");
        go_Wall_10_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_22.transform.position = new Vector3(8.5f, 5.0f, 0.0f);
        var go_Wall_10_22_rb = go_Wall_10_22.AddComponent<Rigidbody2D>();
        go_Wall_10_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_22_bc = go_Wall_10_22.AddComponent<BoxCollider2D>();
        go_Wall_10_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_22_sr = go_Wall_10_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_22);

        // --- Wall_10_23 ---
        var go_Wall_10_23 = new GameObject("Wall_10_23");
        go_Wall_10_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_23.transform.position = new Vector3(9.5f, 5.0f, 0.0f);
        var go_Wall_10_23_rb = go_Wall_10_23.AddComponent<Rigidbody2D>();
        go_Wall_10_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_23_bc = go_Wall_10_23.AddComponent<BoxCollider2D>();
        go_Wall_10_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_23_sr = go_Wall_10_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_23);

        // --- Wall_10_24 ---
        var go_Wall_10_24 = new GameObject("Wall_10_24");
        go_Wall_10_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_24.transform.position = new Vector3(10.5f, 5.0f, 0.0f);
        var go_Wall_10_24_rb = go_Wall_10_24.AddComponent<Rigidbody2D>();
        go_Wall_10_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_24_bc = go_Wall_10_24.AddComponent<BoxCollider2D>();
        go_Wall_10_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_24_sr = go_Wall_10_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_24);

        // --- Wall_10_25 ---
        var go_Wall_10_25 = new GameObject("Wall_10_25");
        go_Wall_10_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_25.transform.position = new Vector3(11.5f, 5.0f, 0.0f);
        var go_Wall_10_25_rb = go_Wall_10_25.AddComponent<Rigidbody2D>();
        go_Wall_10_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_25_bc = go_Wall_10_25.AddComponent<BoxCollider2D>();
        go_Wall_10_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_25_sr = go_Wall_10_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_25);

        // --- Wall_10_26 ---
        var go_Wall_10_26 = new GameObject("Wall_10_26");
        go_Wall_10_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_26.transform.position = new Vector3(12.5f, 5.0f, 0.0f);
        var go_Wall_10_26_rb = go_Wall_10_26.AddComponent<Rigidbody2D>();
        go_Wall_10_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_26_bc = go_Wall_10_26.AddComponent<BoxCollider2D>();
        go_Wall_10_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_26_sr = go_Wall_10_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_26);

        // --- Wall_10_27 ---
        var go_Wall_10_27 = new GameObject("Wall_10_27");
        go_Wall_10_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_10_27.transform.position = new Vector3(13.5f, 5.0f, 0.0f);
        var go_Wall_10_27_rb = go_Wall_10_27.AddComponent<Rigidbody2D>();
        go_Wall_10_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_10_27_bc = go_Wall_10_27.AddComponent<BoxCollider2D>();
        go_Wall_10_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_10_27_sr = go_Wall_10_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_10_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_10_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_10_27);

        // --- Wall_11_0 ---
        var go_Wall_11_0 = new GameObject("Wall_11_0");
        go_Wall_11_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_0.transform.position = new Vector3(-13.5f, 4.0f, 0.0f);
        var go_Wall_11_0_rb = go_Wall_11_0.AddComponent<Rigidbody2D>();
        go_Wall_11_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_0_bc = go_Wall_11_0.AddComponent<BoxCollider2D>();
        go_Wall_11_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_0_sr = go_Wall_11_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_0);

        // --- Wall_11_1 ---
        var go_Wall_11_1 = new GameObject("Wall_11_1");
        go_Wall_11_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_1.transform.position = new Vector3(-12.5f, 4.0f, 0.0f);
        var go_Wall_11_1_rb = go_Wall_11_1.AddComponent<Rigidbody2D>();
        go_Wall_11_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_1_bc = go_Wall_11_1.AddComponent<BoxCollider2D>();
        go_Wall_11_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_1_sr = go_Wall_11_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_1);

        // --- Wall_11_2 ---
        var go_Wall_11_2 = new GameObject("Wall_11_2");
        go_Wall_11_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_2.transform.position = new Vector3(-11.5f, 4.0f, 0.0f);
        var go_Wall_11_2_rb = go_Wall_11_2.AddComponent<Rigidbody2D>();
        go_Wall_11_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_2_bc = go_Wall_11_2.AddComponent<BoxCollider2D>();
        go_Wall_11_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_2_sr = go_Wall_11_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_2);

        // --- Wall_11_3 ---
        var go_Wall_11_3 = new GameObject("Wall_11_3");
        go_Wall_11_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_3.transform.position = new Vector3(-10.5f, 4.0f, 0.0f);
        var go_Wall_11_3_rb = go_Wall_11_3.AddComponent<Rigidbody2D>();
        go_Wall_11_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_3_bc = go_Wall_11_3.AddComponent<BoxCollider2D>();
        go_Wall_11_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_3_sr = go_Wall_11_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_3);

        // --- Wall_11_4 ---
        var go_Wall_11_4 = new GameObject("Wall_11_4");
        go_Wall_11_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_4.transform.position = new Vector3(-9.5f, 4.0f, 0.0f);
        var go_Wall_11_4_rb = go_Wall_11_4.AddComponent<Rigidbody2D>();
        go_Wall_11_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_4_bc = go_Wall_11_4.AddComponent<BoxCollider2D>();
        go_Wall_11_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_4_sr = go_Wall_11_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_4);

        // --- Wall_11_5 ---
        var go_Wall_11_5 = new GameObject("Wall_11_5");
        go_Wall_11_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_5.transform.position = new Vector3(-8.5f, 4.0f, 0.0f);
        var go_Wall_11_5_rb = go_Wall_11_5.AddComponent<Rigidbody2D>();
        go_Wall_11_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_5_bc = go_Wall_11_5.AddComponent<BoxCollider2D>();
        go_Wall_11_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_5_sr = go_Wall_11_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_5);

        // --- Pellet_11_6 ---
        var go_Pellet_11_6 = new GameObject("Pellet_11_6");
        go_Pellet_11_6.tag = "Pellet";
        go_Pellet_11_6.transform.position = new Vector3(-7.5f, 4.0f, 0.0f);
        var go_Pellet_11_6_rb = go_Pellet_11_6.AddComponent<Rigidbody2D>();
        go_Pellet_11_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_11_6_bc = go_Pellet_11_6.AddComponent<BoxCollider2D>();
        go_Pellet_11_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_11_6_bc.isTrigger = true;
        var go_Pellet_11_6_sr = go_Pellet_11_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_11_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_11_6_sr.sharedMaterial = unlitMat;
        go_Pellet_11_6_sr.sortingOrder = 2;
        go_Pellet_11_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_11_6);

        // --- Wall_11_7 ---
        var go_Wall_11_7 = new GameObject("Wall_11_7");
        go_Wall_11_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_7.transform.position = new Vector3(-6.5f, 4.0f, 0.0f);
        var go_Wall_11_7_rb = go_Wall_11_7.AddComponent<Rigidbody2D>();
        go_Wall_11_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_7_bc = go_Wall_11_7.AddComponent<BoxCollider2D>();
        go_Wall_11_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_7_sr = go_Wall_11_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_7);

        // --- Wall_11_8 ---
        var go_Wall_11_8 = new GameObject("Wall_11_8");
        go_Wall_11_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_8.transform.position = new Vector3(-5.5f, 4.0f, 0.0f);
        var go_Wall_11_8_rb = go_Wall_11_8.AddComponent<Rigidbody2D>();
        go_Wall_11_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_8_bc = go_Wall_11_8.AddComponent<BoxCollider2D>();
        go_Wall_11_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_8_sr = go_Wall_11_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_8);

        // --- Node_11_9 ---
        var go_Node_11_9 = new GameObject("Node_11_9");
        go_Node_11_9.transform.position = new Vector3(-4.5f, 4.0f, 0.0f);
        var go_Node_11_9_rb = go_Node_11_9.AddComponent<Rigidbody2D>();
        go_Node_11_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_11_9_bc = go_Node_11_9.AddComponent<BoxCollider2D>();
        go_Node_11_9_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_11_9_bc.isTrigger = true;
        go_Node_11_9.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_11_9);

        // --- Node_11_12 ---
        var go_Node_11_12 = new GameObject("Node_11_12");
        go_Node_11_12.transform.position = new Vector3(-1.5f, 4.0f, 0.0f);
        var go_Node_11_12_rb = go_Node_11_12.AddComponent<Rigidbody2D>();
        go_Node_11_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_11_12_bc = go_Node_11_12.AddComponent<BoxCollider2D>();
        go_Node_11_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_11_12_bc.isTrigger = true;
        go_Node_11_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_11_12);

        // --- Node_11_13 ---
        var go_Node_11_13 = new GameObject("Node_11_13");
        go_Node_11_13.transform.position = new Vector3(-0.5f, 4.0f, 0.0f);
        var go_Node_11_13_rb = go_Node_11_13.AddComponent<Rigidbody2D>();
        go_Node_11_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_11_13_bc = go_Node_11_13.AddComponent<BoxCollider2D>();
        go_Node_11_13_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_11_13_bc.isTrigger = true;
        go_Node_11_13.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_11_13);

        // --- Node_11_14 ---
        var go_Node_11_14 = new GameObject("Node_11_14");
        go_Node_11_14.transform.position = new Vector3(0.5f, 4.0f, 0.0f);
        var go_Node_11_14_rb = go_Node_11_14.AddComponent<Rigidbody2D>();
        go_Node_11_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_11_14_bc = go_Node_11_14.AddComponent<BoxCollider2D>();
        go_Node_11_14_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_11_14_bc.isTrigger = true;
        go_Node_11_14.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_11_14);

        // --- Node_11_15 ---
        var go_Node_11_15 = new GameObject("Node_11_15");
        go_Node_11_15.transform.position = new Vector3(1.5f, 4.0f, 0.0f);
        var go_Node_11_15_rb = go_Node_11_15.AddComponent<Rigidbody2D>();
        go_Node_11_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_11_15_bc = go_Node_11_15.AddComponent<BoxCollider2D>();
        go_Node_11_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_11_15_bc.isTrigger = true;
        go_Node_11_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_11_15);

        // --- Node_11_18 ---
        var go_Node_11_18 = new GameObject("Node_11_18");
        go_Node_11_18.transform.position = new Vector3(4.5f, 4.0f, 0.0f);
        var go_Node_11_18_rb = go_Node_11_18.AddComponent<Rigidbody2D>();
        go_Node_11_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_11_18_bc = go_Node_11_18.AddComponent<BoxCollider2D>();
        go_Node_11_18_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_11_18_bc.isTrigger = true;
        go_Node_11_18.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_11_18);

        // --- Wall_11_19 ---
        var go_Wall_11_19 = new GameObject("Wall_11_19");
        go_Wall_11_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_19.transform.position = new Vector3(5.5f, 4.0f, 0.0f);
        var go_Wall_11_19_rb = go_Wall_11_19.AddComponent<Rigidbody2D>();
        go_Wall_11_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_19_bc = go_Wall_11_19.AddComponent<BoxCollider2D>();
        go_Wall_11_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_19_sr = go_Wall_11_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_19);

        // --- Wall_11_20 ---
        var go_Wall_11_20 = new GameObject("Wall_11_20");
        go_Wall_11_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_20.transform.position = new Vector3(6.5f, 4.0f, 0.0f);
        var go_Wall_11_20_rb = go_Wall_11_20.AddComponent<Rigidbody2D>();
        go_Wall_11_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_20_bc = go_Wall_11_20.AddComponent<BoxCollider2D>();
        go_Wall_11_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_20_sr = go_Wall_11_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_20);

        // --- Pellet_11_21 ---
        var go_Pellet_11_21 = new GameObject("Pellet_11_21");
        go_Pellet_11_21.tag = "Pellet";
        go_Pellet_11_21.transform.position = new Vector3(7.5f, 4.0f, 0.0f);
        var go_Pellet_11_21_rb = go_Pellet_11_21.AddComponent<Rigidbody2D>();
        go_Pellet_11_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_11_21_bc = go_Pellet_11_21.AddComponent<BoxCollider2D>();
        go_Pellet_11_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_11_21_bc.isTrigger = true;
        var go_Pellet_11_21_sr = go_Pellet_11_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_11_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_11_21_sr.sharedMaterial = unlitMat;
        go_Pellet_11_21_sr.sortingOrder = 2;
        go_Pellet_11_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_11_21);

        // --- Wall_11_22 ---
        var go_Wall_11_22 = new GameObject("Wall_11_22");
        go_Wall_11_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_22.transform.position = new Vector3(8.5f, 4.0f, 0.0f);
        var go_Wall_11_22_rb = go_Wall_11_22.AddComponent<Rigidbody2D>();
        go_Wall_11_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_22_bc = go_Wall_11_22.AddComponent<BoxCollider2D>();
        go_Wall_11_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_22_sr = go_Wall_11_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_22);

        // --- Wall_11_23 ---
        var go_Wall_11_23 = new GameObject("Wall_11_23");
        go_Wall_11_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_23.transform.position = new Vector3(9.5f, 4.0f, 0.0f);
        var go_Wall_11_23_rb = go_Wall_11_23.AddComponent<Rigidbody2D>();
        go_Wall_11_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_23_bc = go_Wall_11_23.AddComponent<BoxCollider2D>();
        go_Wall_11_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_23_sr = go_Wall_11_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_23);

        // --- Wall_11_24 ---
        var go_Wall_11_24 = new GameObject("Wall_11_24");
        go_Wall_11_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_24.transform.position = new Vector3(10.5f, 4.0f, 0.0f);
        var go_Wall_11_24_rb = go_Wall_11_24.AddComponent<Rigidbody2D>();
        go_Wall_11_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_24_bc = go_Wall_11_24.AddComponent<BoxCollider2D>();
        go_Wall_11_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_24_sr = go_Wall_11_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_24);

        // --- Wall_11_25 ---
        var go_Wall_11_25 = new GameObject("Wall_11_25");
        go_Wall_11_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_25.transform.position = new Vector3(11.5f, 4.0f, 0.0f);
        var go_Wall_11_25_rb = go_Wall_11_25.AddComponent<Rigidbody2D>();
        go_Wall_11_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_25_bc = go_Wall_11_25.AddComponent<BoxCollider2D>();
        go_Wall_11_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_25_sr = go_Wall_11_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_25);

        // --- Wall_11_26 ---
        var go_Wall_11_26 = new GameObject("Wall_11_26");
        go_Wall_11_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_26.transform.position = new Vector3(12.5f, 4.0f, 0.0f);
        var go_Wall_11_26_rb = go_Wall_11_26.AddComponent<Rigidbody2D>();
        go_Wall_11_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_26_bc = go_Wall_11_26.AddComponent<BoxCollider2D>();
        go_Wall_11_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_26_sr = go_Wall_11_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_26);

        // --- Wall_11_27 ---
        var go_Wall_11_27 = new GameObject("Wall_11_27");
        go_Wall_11_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_11_27.transform.position = new Vector3(13.5f, 4.0f, 0.0f);
        var go_Wall_11_27_rb = go_Wall_11_27.AddComponent<Rigidbody2D>();
        go_Wall_11_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_11_27_bc = go_Wall_11_27.AddComponent<BoxCollider2D>();
        go_Wall_11_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_11_27_sr = go_Wall_11_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_11_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_11_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_11_27);

        // --- Wall_12_0 ---
        var go_Wall_12_0 = new GameObject("Wall_12_0");
        go_Wall_12_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_0.transform.position = new Vector3(-13.5f, 3.0f, 0.0f);
        var go_Wall_12_0_rb = go_Wall_12_0.AddComponent<Rigidbody2D>();
        go_Wall_12_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_0_bc = go_Wall_12_0.AddComponent<BoxCollider2D>();
        go_Wall_12_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_0_sr = go_Wall_12_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_0);

        // --- Wall_12_1 ---
        var go_Wall_12_1 = new GameObject("Wall_12_1");
        go_Wall_12_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_1.transform.position = new Vector3(-12.5f, 3.0f, 0.0f);
        var go_Wall_12_1_rb = go_Wall_12_1.AddComponent<Rigidbody2D>();
        go_Wall_12_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_1_bc = go_Wall_12_1.AddComponent<BoxCollider2D>();
        go_Wall_12_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_1_sr = go_Wall_12_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_1);

        // --- Wall_12_2 ---
        var go_Wall_12_2 = new GameObject("Wall_12_2");
        go_Wall_12_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_2.transform.position = new Vector3(-11.5f, 3.0f, 0.0f);
        var go_Wall_12_2_rb = go_Wall_12_2.AddComponent<Rigidbody2D>();
        go_Wall_12_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_2_bc = go_Wall_12_2.AddComponent<BoxCollider2D>();
        go_Wall_12_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_2_sr = go_Wall_12_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_2);

        // --- Wall_12_3 ---
        var go_Wall_12_3 = new GameObject("Wall_12_3");
        go_Wall_12_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_3.transform.position = new Vector3(-10.5f, 3.0f, 0.0f);
        var go_Wall_12_3_rb = go_Wall_12_3.AddComponent<Rigidbody2D>();
        go_Wall_12_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_3_bc = go_Wall_12_3.AddComponent<BoxCollider2D>();
        go_Wall_12_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_3_sr = go_Wall_12_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_3);

        // --- Wall_12_4 ---
        var go_Wall_12_4 = new GameObject("Wall_12_4");
        go_Wall_12_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_4.transform.position = new Vector3(-9.5f, 3.0f, 0.0f);
        var go_Wall_12_4_rb = go_Wall_12_4.AddComponent<Rigidbody2D>();
        go_Wall_12_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_4_bc = go_Wall_12_4.AddComponent<BoxCollider2D>();
        go_Wall_12_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_4_sr = go_Wall_12_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_4);

        // --- Wall_12_5 ---
        var go_Wall_12_5 = new GameObject("Wall_12_5");
        go_Wall_12_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_5.transform.position = new Vector3(-8.5f, 3.0f, 0.0f);
        var go_Wall_12_5_rb = go_Wall_12_5.AddComponent<Rigidbody2D>();
        go_Wall_12_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_5_bc = go_Wall_12_5.AddComponent<BoxCollider2D>();
        go_Wall_12_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_5_sr = go_Wall_12_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_5);

        // --- Pellet_12_6 ---
        var go_Pellet_12_6 = new GameObject("Pellet_12_6");
        go_Pellet_12_6.tag = "Pellet";
        go_Pellet_12_6.transform.position = new Vector3(-7.5f, 3.0f, 0.0f);
        var go_Pellet_12_6_rb = go_Pellet_12_6.AddComponent<Rigidbody2D>();
        go_Pellet_12_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_12_6_bc = go_Pellet_12_6.AddComponent<BoxCollider2D>();
        go_Pellet_12_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_12_6_bc.isTrigger = true;
        var go_Pellet_12_6_sr = go_Pellet_12_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_12_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_12_6_sr.sharedMaterial = unlitMat;
        go_Pellet_12_6_sr.sortingOrder = 2;
        go_Pellet_12_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_12_6);

        // --- Wall_12_7 ---
        var go_Wall_12_7 = new GameObject("Wall_12_7");
        go_Wall_12_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_7.transform.position = new Vector3(-6.5f, 3.0f, 0.0f);
        var go_Wall_12_7_rb = go_Wall_12_7.AddComponent<Rigidbody2D>();
        go_Wall_12_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_7_bc = go_Wall_12_7.AddComponent<BoxCollider2D>();
        go_Wall_12_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_7_sr = go_Wall_12_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_7);

        // --- Wall_12_8 ---
        var go_Wall_12_8 = new GameObject("Wall_12_8");
        go_Wall_12_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_8.transform.position = new Vector3(-5.5f, 3.0f, 0.0f);
        var go_Wall_12_8_rb = go_Wall_12_8.AddComponent<Rigidbody2D>();
        go_Wall_12_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_8_bc = go_Wall_12_8.AddComponent<BoxCollider2D>();
        go_Wall_12_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_8_sr = go_Wall_12_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_8);

        // --- Wall_12_10 ---
        var go_Wall_12_10 = new GameObject("Wall_12_10");
        go_Wall_12_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_10.transform.position = new Vector3(-3.5f, 3.0f, 0.0f);
        var go_Wall_12_10_rb = go_Wall_12_10.AddComponent<Rigidbody2D>();
        go_Wall_12_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_10_bc = go_Wall_12_10.AddComponent<BoxCollider2D>();
        go_Wall_12_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_10_sr = go_Wall_12_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_10);

        // --- Wall_12_11 ---
        var go_Wall_12_11 = new GameObject("Wall_12_11");
        go_Wall_12_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_11.transform.position = new Vector3(-2.5f, 3.0f, 0.0f);
        var go_Wall_12_11_rb = go_Wall_12_11.AddComponent<Rigidbody2D>();
        go_Wall_12_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_11_bc = go_Wall_12_11.AddComponent<BoxCollider2D>();
        go_Wall_12_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_11_sr = go_Wall_12_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_11);

        // --- Wall_12_12 ---
        var go_Wall_12_12 = new GameObject("Wall_12_12");
        go_Wall_12_12.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_12.transform.position = new Vector3(-1.5f, 3.0f, 0.0f);
        var go_Wall_12_12_rb = go_Wall_12_12.AddComponent<Rigidbody2D>();
        go_Wall_12_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_12_bc = go_Wall_12_12.AddComponent<BoxCollider2D>();
        go_Wall_12_12_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_12_sr = go_Wall_12_12.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_12_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_12_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_12);

        // --- Node_12_13 ---
        var go_Node_12_13 = new GameObject("Node_12_13");
        go_Node_12_13.transform.position = new Vector3(-0.5f, 3.0f, 0.0f);
        var go_Node_12_13_rb = go_Node_12_13.AddComponent<Rigidbody2D>();
        go_Node_12_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_12_13_bc = go_Node_12_13.AddComponent<BoxCollider2D>();
        go_Node_12_13_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_12_13_bc.isTrigger = true;
        go_Node_12_13.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_12_13);

        // --- Node_12_14 ---
        var go_Node_12_14 = new GameObject("Node_12_14");
        go_Node_12_14.transform.position = new Vector3(0.5f, 3.0f, 0.0f);
        var go_Node_12_14_rb = go_Node_12_14.AddComponent<Rigidbody2D>();
        go_Node_12_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_12_14_bc = go_Node_12_14.AddComponent<BoxCollider2D>();
        go_Node_12_14_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_12_14_bc.isTrigger = true;
        go_Node_12_14.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_12_14);

        // --- Wall_12_15 ---
        var go_Wall_12_15 = new GameObject("Wall_12_15");
        go_Wall_12_15.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_15.transform.position = new Vector3(1.5f, 3.0f, 0.0f);
        var go_Wall_12_15_rb = go_Wall_12_15.AddComponent<Rigidbody2D>();
        go_Wall_12_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_15_bc = go_Wall_12_15.AddComponent<BoxCollider2D>();
        go_Wall_12_15_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_15_sr = go_Wall_12_15.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_15_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_15_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_15);

        // --- Wall_12_16 ---
        var go_Wall_12_16 = new GameObject("Wall_12_16");
        go_Wall_12_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_16.transform.position = new Vector3(2.5f, 3.0f, 0.0f);
        var go_Wall_12_16_rb = go_Wall_12_16.AddComponent<Rigidbody2D>();
        go_Wall_12_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_16_bc = go_Wall_12_16.AddComponent<BoxCollider2D>();
        go_Wall_12_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_16_sr = go_Wall_12_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_16);

        // --- Wall_12_17 ---
        var go_Wall_12_17 = new GameObject("Wall_12_17");
        go_Wall_12_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_17.transform.position = new Vector3(3.5f, 3.0f, 0.0f);
        var go_Wall_12_17_rb = go_Wall_12_17.AddComponent<Rigidbody2D>();
        go_Wall_12_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_17_bc = go_Wall_12_17.AddComponent<BoxCollider2D>();
        go_Wall_12_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_17_sr = go_Wall_12_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_17);

        // --- Wall_12_19 ---
        var go_Wall_12_19 = new GameObject("Wall_12_19");
        go_Wall_12_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_19.transform.position = new Vector3(5.5f, 3.0f, 0.0f);
        var go_Wall_12_19_rb = go_Wall_12_19.AddComponent<Rigidbody2D>();
        go_Wall_12_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_19_bc = go_Wall_12_19.AddComponent<BoxCollider2D>();
        go_Wall_12_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_19_sr = go_Wall_12_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_19);

        // --- Wall_12_20 ---
        var go_Wall_12_20 = new GameObject("Wall_12_20");
        go_Wall_12_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_20.transform.position = new Vector3(6.5f, 3.0f, 0.0f);
        var go_Wall_12_20_rb = go_Wall_12_20.AddComponent<Rigidbody2D>();
        go_Wall_12_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_20_bc = go_Wall_12_20.AddComponent<BoxCollider2D>();
        go_Wall_12_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_20_sr = go_Wall_12_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_20);

        // --- Pellet_12_21 ---
        var go_Pellet_12_21 = new GameObject("Pellet_12_21");
        go_Pellet_12_21.tag = "Pellet";
        go_Pellet_12_21.transform.position = new Vector3(7.5f, 3.0f, 0.0f);
        var go_Pellet_12_21_rb = go_Pellet_12_21.AddComponent<Rigidbody2D>();
        go_Pellet_12_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_12_21_bc = go_Pellet_12_21.AddComponent<BoxCollider2D>();
        go_Pellet_12_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_12_21_bc.isTrigger = true;
        var go_Pellet_12_21_sr = go_Pellet_12_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_12_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_12_21_sr.sharedMaterial = unlitMat;
        go_Pellet_12_21_sr.sortingOrder = 2;
        go_Pellet_12_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_12_21);

        // --- Wall_12_22 ---
        var go_Wall_12_22 = new GameObject("Wall_12_22");
        go_Wall_12_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_22.transform.position = new Vector3(8.5f, 3.0f, 0.0f);
        var go_Wall_12_22_rb = go_Wall_12_22.AddComponent<Rigidbody2D>();
        go_Wall_12_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_22_bc = go_Wall_12_22.AddComponent<BoxCollider2D>();
        go_Wall_12_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_22_sr = go_Wall_12_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_22);

        // --- Wall_12_23 ---
        var go_Wall_12_23 = new GameObject("Wall_12_23");
        go_Wall_12_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_23.transform.position = new Vector3(9.5f, 3.0f, 0.0f);
        var go_Wall_12_23_rb = go_Wall_12_23.AddComponent<Rigidbody2D>();
        go_Wall_12_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_23_bc = go_Wall_12_23.AddComponent<BoxCollider2D>();
        go_Wall_12_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_23_sr = go_Wall_12_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_23);

        // --- Wall_12_24 ---
        var go_Wall_12_24 = new GameObject("Wall_12_24");
        go_Wall_12_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_24.transform.position = new Vector3(10.5f, 3.0f, 0.0f);
        var go_Wall_12_24_rb = go_Wall_12_24.AddComponent<Rigidbody2D>();
        go_Wall_12_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_24_bc = go_Wall_12_24.AddComponent<BoxCollider2D>();
        go_Wall_12_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_24_sr = go_Wall_12_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_24);

        // --- Wall_12_25 ---
        var go_Wall_12_25 = new GameObject("Wall_12_25");
        go_Wall_12_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_25.transform.position = new Vector3(11.5f, 3.0f, 0.0f);
        var go_Wall_12_25_rb = go_Wall_12_25.AddComponent<Rigidbody2D>();
        go_Wall_12_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_25_bc = go_Wall_12_25.AddComponent<BoxCollider2D>();
        go_Wall_12_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_25_sr = go_Wall_12_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_25);

        // --- Wall_12_26 ---
        var go_Wall_12_26 = new GameObject("Wall_12_26");
        go_Wall_12_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_26.transform.position = new Vector3(12.5f, 3.0f, 0.0f);
        var go_Wall_12_26_rb = go_Wall_12_26.AddComponent<Rigidbody2D>();
        go_Wall_12_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_26_bc = go_Wall_12_26.AddComponent<BoxCollider2D>();
        go_Wall_12_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_26_sr = go_Wall_12_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_26);

        // --- Wall_12_27 ---
        var go_Wall_12_27 = new GameObject("Wall_12_27");
        go_Wall_12_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_12_27.transform.position = new Vector3(13.5f, 3.0f, 0.0f);
        var go_Wall_12_27_rb = go_Wall_12_27.AddComponent<Rigidbody2D>();
        go_Wall_12_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_12_27_bc = go_Wall_12_27.AddComponent<BoxCollider2D>();
        go_Wall_12_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_12_27_sr = go_Wall_12_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_12_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_12_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_12_27);

        // --- Wall_13_0 ---
        var go_Wall_13_0 = new GameObject("Wall_13_0");
        go_Wall_13_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_0.transform.position = new Vector3(-13.5f, 2.0f, 0.0f);
        var go_Wall_13_0_rb = go_Wall_13_0.AddComponent<Rigidbody2D>();
        go_Wall_13_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_0_bc = go_Wall_13_0.AddComponent<BoxCollider2D>();
        go_Wall_13_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_0_sr = go_Wall_13_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_0);

        // --- Wall_13_1 ---
        var go_Wall_13_1 = new GameObject("Wall_13_1");
        go_Wall_13_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_1.transform.position = new Vector3(-12.5f, 2.0f, 0.0f);
        var go_Wall_13_1_rb = go_Wall_13_1.AddComponent<Rigidbody2D>();
        go_Wall_13_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_1_bc = go_Wall_13_1.AddComponent<BoxCollider2D>();
        go_Wall_13_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_1_sr = go_Wall_13_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_1);

        // --- Wall_13_2 ---
        var go_Wall_13_2 = new GameObject("Wall_13_2");
        go_Wall_13_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_2.transform.position = new Vector3(-11.5f, 2.0f, 0.0f);
        var go_Wall_13_2_rb = go_Wall_13_2.AddComponent<Rigidbody2D>();
        go_Wall_13_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_2_bc = go_Wall_13_2.AddComponent<BoxCollider2D>();
        go_Wall_13_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_2_sr = go_Wall_13_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_2);

        // --- Wall_13_3 ---
        var go_Wall_13_3 = new GameObject("Wall_13_3");
        go_Wall_13_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_3.transform.position = new Vector3(-10.5f, 2.0f, 0.0f);
        var go_Wall_13_3_rb = go_Wall_13_3.AddComponent<Rigidbody2D>();
        go_Wall_13_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_3_bc = go_Wall_13_3.AddComponent<BoxCollider2D>();
        go_Wall_13_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_3_sr = go_Wall_13_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_3);

        // --- Wall_13_4 ---
        var go_Wall_13_4 = new GameObject("Wall_13_4");
        go_Wall_13_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_4.transform.position = new Vector3(-9.5f, 2.0f, 0.0f);
        var go_Wall_13_4_rb = go_Wall_13_4.AddComponent<Rigidbody2D>();
        go_Wall_13_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_4_bc = go_Wall_13_4.AddComponent<BoxCollider2D>();
        go_Wall_13_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_4_sr = go_Wall_13_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_4);

        // --- Wall_13_5 ---
        var go_Wall_13_5 = new GameObject("Wall_13_5");
        go_Wall_13_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_5.transform.position = new Vector3(-8.5f, 2.0f, 0.0f);
        var go_Wall_13_5_rb = go_Wall_13_5.AddComponent<Rigidbody2D>();
        go_Wall_13_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_5_bc = go_Wall_13_5.AddComponent<BoxCollider2D>();
        go_Wall_13_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_5_sr = go_Wall_13_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_5);

        // --- Pellet_13_6 ---
        var go_Pellet_13_6 = new GameObject("Pellet_13_6");
        go_Pellet_13_6.tag = "Pellet";
        go_Pellet_13_6.transform.position = new Vector3(-7.5f, 2.0f, 0.0f);
        var go_Pellet_13_6_rb = go_Pellet_13_6.AddComponent<Rigidbody2D>();
        go_Pellet_13_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_13_6_bc = go_Pellet_13_6.AddComponent<BoxCollider2D>();
        go_Pellet_13_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_13_6_bc.isTrigger = true;
        var go_Pellet_13_6_sr = go_Pellet_13_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_13_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_13_6_sr.sharedMaterial = unlitMat;
        go_Pellet_13_6_sr.sortingOrder = 2;
        go_Pellet_13_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_13_6);

        // --- Wall_13_7 ---
        var go_Wall_13_7 = new GameObject("Wall_13_7");
        go_Wall_13_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_7.transform.position = new Vector3(-6.5f, 2.0f, 0.0f);
        var go_Wall_13_7_rb = go_Wall_13_7.AddComponent<Rigidbody2D>();
        go_Wall_13_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_7_bc = go_Wall_13_7.AddComponent<BoxCollider2D>();
        go_Wall_13_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_7_sr = go_Wall_13_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_7);

        // --- Wall_13_8 ---
        var go_Wall_13_8 = new GameObject("Wall_13_8");
        go_Wall_13_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_8.transform.position = new Vector3(-5.5f, 2.0f, 0.0f);
        var go_Wall_13_8_rb = go_Wall_13_8.AddComponent<Rigidbody2D>();
        go_Wall_13_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_8_bc = go_Wall_13_8.AddComponent<BoxCollider2D>();
        go_Wall_13_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_8_sr = go_Wall_13_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_8);

        // --- Wall_13_10 ---
        var go_Wall_13_10 = new GameObject("Wall_13_10");
        go_Wall_13_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_10.transform.position = new Vector3(-3.5f, 2.0f, 0.0f);
        var go_Wall_13_10_rb = go_Wall_13_10.AddComponent<Rigidbody2D>();
        go_Wall_13_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_10_bc = go_Wall_13_10.AddComponent<BoxCollider2D>();
        go_Wall_13_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_10_sr = go_Wall_13_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_10);

        // --- Node_13_11 ---
        var go_Node_13_11 = new GameObject("Node_13_11");
        go_Node_13_11.transform.position = new Vector3(-2.5f, 2.0f, 0.0f);
        var go_Node_13_11_rb = go_Node_13_11.AddComponent<Rigidbody2D>();
        go_Node_13_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_13_11_bc = go_Node_13_11.AddComponent<BoxCollider2D>();
        go_Node_13_11_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_13_11_bc.isTrigger = true;
        go_Node_13_11.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_13_11);

        // --- Node_13_12 ---
        var go_Node_13_12 = new GameObject("Node_13_12");
        go_Node_13_12.transform.position = new Vector3(-1.5f, 2.0f, 0.0f);
        var go_Node_13_12_rb = go_Node_13_12.AddComponent<Rigidbody2D>();
        go_Node_13_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_13_12_bc = go_Node_13_12.AddComponent<BoxCollider2D>();
        go_Node_13_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_13_12_bc.isTrigger = true;
        go_Node_13_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_13_12);

        // --- Node_13_13 ---
        var go_Node_13_13 = new GameObject("Node_13_13");
        go_Node_13_13.transform.position = new Vector3(-0.5f, 2.0f, 0.0f);
        var go_Node_13_13_rb = go_Node_13_13.AddComponent<Rigidbody2D>();
        go_Node_13_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_13_13_bc = go_Node_13_13.AddComponent<BoxCollider2D>();
        go_Node_13_13_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_13_13_bc.isTrigger = true;
        go_Node_13_13.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_13_13);

        // --- Node_13_14 ---
        var go_Node_13_14 = new GameObject("Node_13_14");
        go_Node_13_14.transform.position = new Vector3(0.5f, 2.0f, 0.0f);
        var go_Node_13_14_rb = go_Node_13_14.AddComponent<Rigidbody2D>();
        go_Node_13_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_13_14_bc = go_Node_13_14.AddComponent<BoxCollider2D>();
        go_Node_13_14_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_13_14_bc.isTrigger = true;
        go_Node_13_14.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_13_14);

        // --- Node_13_15 ---
        var go_Node_13_15 = new GameObject("Node_13_15");
        go_Node_13_15.transform.position = new Vector3(1.5f, 2.0f, 0.0f);
        var go_Node_13_15_rb = go_Node_13_15.AddComponent<Rigidbody2D>();
        go_Node_13_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_13_15_bc = go_Node_13_15.AddComponent<BoxCollider2D>();
        go_Node_13_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_13_15_bc.isTrigger = true;
        go_Node_13_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_13_15);

        // --- Node_13_16 ---
        var go_Node_13_16 = new GameObject("Node_13_16");
        go_Node_13_16.transform.position = new Vector3(2.5f, 2.0f, 0.0f);
        var go_Node_13_16_rb = go_Node_13_16.AddComponent<Rigidbody2D>();
        go_Node_13_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_13_16_bc = go_Node_13_16.AddComponent<BoxCollider2D>();
        go_Node_13_16_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_13_16_bc.isTrigger = true;
        go_Node_13_16.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_13_16);

        // --- Wall_13_17 ---
        var go_Wall_13_17 = new GameObject("Wall_13_17");
        go_Wall_13_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_17.transform.position = new Vector3(3.5f, 2.0f, 0.0f);
        var go_Wall_13_17_rb = go_Wall_13_17.AddComponent<Rigidbody2D>();
        go_Wall_13_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_17_bc = go_Wall_13_17.AddComponent<BoxCollider2D>();
        go_Wall_13_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_17_sr = go_Wall_13_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_17);

        // --- Wall_13_19 ---
        var go_Wall_13_19 = new GameObject("Wall_13_19");
        go_Wall_13_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_19.transform.position = new Vector3(5.5f, 2.0f, 0.0f);
        var go_Wall_13_19_rb = go_Wall_13_19.AddComponent<Rigidbody2D>();
        go_Wall_13_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_19_bc = go_Wall_13_19.AddComponent<BoxCollider2D>();
        go_Wall_13_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_19_sr = go_Wall_13_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_19);

        // --- Wall_13_20 ---
        var go_Wall_13_20 = new GameObject("Wall_13_20");
        go_Wall_13_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_20.transform.position = new Vector3(6.5f, 2.0f, 0.0f);
        var go_Wall_13_20_rb = go_Wall_13_20.AddComponent<Rigidbody2D>();
        go_Wall_13_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_20_bc = go_Wall_13_20.AddComponent<BoxCollider2D>();
        go_Wall_13_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_20_sr = go_Wall_13_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_20);

        // --- Pellet_13_21 ---
        var go_Pellet_13_21 = new GameObject("Pellet_13_21");
        go_Pellet_13_21.tag = "Pellet";
        go_Pellet_13_21.transform.position = new Vector3(7.5f, 2.0f, 0.0f);
        var go_Pellet_13_21_rb = go_Pellet_13_21.AddComponent<Rigidbody2D>();
        go_Pellet_13_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_13_21_bc = go_Pellet_13_21.AddComponent<BoxCollider2D>();
        go_Pellet_13_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_13_21_bc.isTrigger = true;
        var go_Pellet_13_21_sr = go_Pellet_13_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_13_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_13_21_sr.sharedMaterial = unlitMat;
        go_Pellet_13_21_sr.sortingOrder = 2;
        go_Pellet_13_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_13_21);

        // --- Wall_13_22 ---
        var go_Wall_13_22 = new GameObject("Wall_13_22");
        go_Wall_13_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_22.transform.position = new Vector3(8.5f, 2.0f, 0.0f);
        var go_Wall_13_22_rb = go_Wall_13_22.AddComponent<Rigidbody2D>();
        go_Wall_13_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_22_bc = go_Wall_13_22.AddComponent<BoxCollider2D>();
        go_Wall_13_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_22_sr = go_Wall_13_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_22);

        // --- Wall_13_23 ---
        var go_Wall_13_23 = new GameObject("Wall_13_23");
        go_Wall_13_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_23.transform.position = new Vector3(9.5f, 2.0f, 0.0f);
        var go_Wall_13_23_rb = go_Wall_13_23.AddComponent<Rigidbody2D>();
        go_Wall_13_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_23_bc = go_Wall_13_23.AddComponent<BoxCollider2D>();
        go_Wall_13_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_23_sr = go_Wall_13_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_23);

        // --- Wall_13_24 ---
        var go_Wall_13_24 = new GameObject("Wall_13_24");
        go_Wall_13_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_24.transform.position = new Vector3(10.5f, 2.0f, 0.0f);
        var go_Wall_13_24_rb = go_Wall_13_24.AddComponent<Rigidbody2D>();
        go_Wall_13_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_24_bc = go_Wall_13_24.AddComponent<BoxCollider2D>();
        go_Wall_13_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_24_sr = go_Wall_13_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_24);

        // --- Wall_13_25 ---
        var go_Wall_13_25 = new GameObject("Wall_13_25");
        go_Wall_13_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_25.transform.position = new Vector3(11.5f, 2.0f, 0.0f);
        var go_Wall_13_25_rb = go_Wall_13_25.AddComponent<Rigidbody2D>();
        go_Wall_13_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_25_bc = go_Wall_13_25.AddComponent<BoxCollider2D>();
        go_Wall_13_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_25_sr = go_Wall_13_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_25);

        // --- Wall_13_26 ---
        var go_Wall_13_26 = new GameObject("Wall_13_26");
        go_Wall_13_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_26.transform.position = new Vector3(12.5f, 2.0f, 0.0f);
        var go_Wall_13_26_rb = go_Wall_13_26.AddComponent<Rigidbody2D>();
        go_Wall_13_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_26_bc = go_Wall_13_26.AddComponent<BoxCollider2D>();
        go_Wall_13_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_26_sr = go_Wall_13_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_26);

        // --- Wall_13_27 ---
        var go_Wall_13_27 = new GameObject("Wall_13_27");
        go_Wall_13_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_13_27.transform.position = new Vector3(13.5f, 2.0f, 0.0f);
        var go_Wall_13_27_rb = go_Wall_13_27.AddComponent<Rigidbody2D>();
        go_Wall_13_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_13_27_bc = go_Wall_13_27.AddComponent<BoxCollider2D>();
        go_Wall_13_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_13_27_sr = go_Wall_13_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_13_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_13_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_13_27);

        // --- Passage_14_0 ---
        var go_Passage_14_0 = new GameObject("Passage_14_0");
        go_Passage_14_0.transform.position = new Vector3(-13.5f, 1.0f, 0.0f);
        var go_Passage_14_0_rb = go_Passage_14_0.AddComponent<Rigidbody2D>();
        go_Passage_14_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Passage_14_0_bc = go_Passage_14_0.AddComponent<BoxCollider2D>();
        go_Passage_14_0_bc.size = new Vector2(1.0f, 1.0f);
        go_Passage_14_0_bc.isTrigger = true;
        go_Passage_14_0.AddComponent<Passage>();
        EditorUtility.SetDirty(go_Passage_14_0);

        // --- Node_14_6 ---
        var go_Node_14_6 = new GameObject("Node_14_6");
        go_Node_14_6.transform.position = new Vector3(-7.5f, 1.0f, 0.0f);
        var go_Node_14_6_rb = go_Node_14_6.AddComponent<Rigidbody2D>();
        go_Node_14_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_14_6_bc = go_Node_14_6.AddComponent<BoxCollider2D>();
        go_Node_14_6_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_14_6_bc.isTrigger = true;
        go_Node_14_6.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_14_6);

        // --- Pellet_14_7 ---
        var go_Pellet_14_7 = new GameObject("Pellet_14_7");
        go_Pellet_14_7.tag = "Pellet";
        go_Pellet_14_7.transform.position = new Vector3(-6.5f, 1.0f, 0.0f);
        var go_Pellet_14_7_rb = go_Pellet_14_7.AddComponent<Rigidbody2D>();
        go_Pellet_14_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_14_7_bc = go_Pellet_14_7.AddComponent<BoxCollider2D>();
        go_Pellet_14_7_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_14_7_bc.isTrigger = true;
        var go_Pellet_14_7_sr = go_Pellet_14_7.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_14_7_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_14_7_sr.sharedMaterial = unlitMat;
        go_Pellet_14_7_sr.sortingOrder = 2;
        go_Pellet_14_7.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_14_7);

        // --- Node_14_9 ---
        var go_Node_14_9 = new GameObject("Node_14_9");
        go_Node_14_9.transform.position = new Vector3(-4.5f, 1.0f, 0.0f);
        var go_Node_14_9_rb = go_Node_14_9.AddComponent<Rigidbody2D>();
        go_Node_14_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_14_9_bc = go_Node_14_9.AddComponent<BoxCollider2D>();
        go_Node_14_9_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_14_9_bc.isTrigger = true;
        go_Node_14_9.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_14_9);

        // --- Wall_14_10 ---
        var go_Wall_14_10 = new GameObject("Wall_14_10");
        go_Wall_14_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_14_10.transform.position = new Vector3(-3.5f, 1.0f, 0.0f);
        var go_Wall_14_10_rb = go_Wall_14_10.AddComponent<Rigidbody2D>();
        go_Wall_14_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_14_10_bc = go_Wall_14_10.AddComponent<BoxCollider2D>();
        go_Wall_14_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_14_10_sr = go_Wall_14_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_14_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_14_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_14_10);

        // --- Node_14_11 ---
        var go_Node_14_11 = new GameObject("Node_14_11");
        go_Node_14_11.transform.position = new Vector3(-2.5f, 1.0f, 0.0f);
        var go_Node_14_11_rb = go_Node_14_11.AddComponent<Rigidbody2D>();
        go_Node_14_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_14_11_bc = go_Node_14_11.AddComponent<BoxCollider2D>();
        go_Node_14_11_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_14_11_bc.isTrigger = true;
        go_Node_14_11.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_14_11);

        // --- Node_14_12 ---
        var go_Node_14_12 = new GameObject("Node_14_12");
        go_Node_14_12.transform.position = new Vector3(-1.5f, 1.0f, 0.0f);
        var go_Node_14_12_rb = go_Node_14_12.AddComponent<Rigidbody2D>();
        go_Node_14_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_14_12_bc = go_Node_14_12.AddComponent<BoxCollider2D>();
        go_Node_14_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_14_12_bc.isTrigger = true;
        go_Node_14_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_14_12);

        // --- Node_14_13 ---
        var go_Node_14_13 = new GameObject("Node_14_13");
        go_Node_14_13.transform.position = new Vector3(-0.5f, 1.0f, 0.0f);
        var go_Node_14_13_rb = go_Node_14_13.AddComponent<Rigidbody2D>();
        go_Node_14_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_14_13_bc = go_Node_14_13.AddComponent<BoxCollider2D>();
        go_Node_14_13_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_14_13_bc.isTrigger = true;
        go_Node_14_13.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_14_13);

        // --- Node_14_14 ---
        var go_Node_14_14 = new GameObject("Node_14_14");
        go_Node_14_14.transform.position = new Vector3(0.5f, 1.0f, 0.0f);
        var go_Node_14_14_rb = go_Node_14_14.AddComponent<Rigidbody2D>();
        go_Node_14_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_14_14_bc = go_Node_14_14.AddComponent<BoxCollider2D>();
        go_Node_14_14_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_14_14_bc.isTrigger = true;
        go_Node_14_14.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_14_14);

        // --- Node_14_15 ---
        var go_Node_14_15 = new GameObject("Node_14_15");
        go_Node_14_15.transform.position = new Vector3(1.5f, 1.0f, 0.0f);
        var go_Node_14_15_rb = go_Node_14_15.AddComponent<Rigidbody2D>();
        go_Node_14_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_14_15_bc = go_Node_14_15.AddComponent<BoxCollider2D>();
        go_Node_14_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_14_15_bc.isTrigger = true;
        go_Node_14_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_14_15);

        // --- Node_14_16 ---
        var go_Node_14_16 = new GameObject("Node_14_16");
        go_Node_14_16.transform.position = new Vector3(2.5f, 1.0f, 0.0f);
        var go_Node_14_16_rb = go_Node_14_16.AddComponent<Rigidbody2D>();
        go_Node_14_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_14_16_bc = go_Node_14_16.AddComponent<BoxCollider2D>();
        go_Node_14_16_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_14_16_bc.isTrigger = true;
        go_Node_14_16.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_14_16);

        // --- Wall_14_17 ---
        var go_Wall_14_17 = new GameObject("Wall_14_17");
        go_Wall_14_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_14_17.transform.position = new Vector3(3.5f, 1.0f, 0.0f);
        var go_Wall_14_17_rb = go_Wall_14_17.AddComponent<Rigidbody2D>();
        go_Wall_14_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_14_17_bc = go_Wall_14_17.AddComponent<BoxCollider2D>();
        go_Wall_14_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_14_17_sr = go_Wall_14_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_14_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_14_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_14_17);

        // --- Node_14_18 ---
        var go_Node_14_18 = new GameObject("Node_14_18");
        go_Node_14_18.transform.position = new Vector3(4.5f, 1.0f, 0.0f);
        var go_Node_14_18_rb = go_Node_14_18.AddComponent<Rigidbody2D>();
        go_Node_14_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_14_18_bc = go_Node_14_18.AddComponent<BoxCollider2D>();
        go_Node_14_18_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_14_18_bc.isTrigger = true;
        go_Node_14_18.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_14_18);

        // --- Pellet_14_20 ---
        var go_Pellet_14_20 = new GameObject("Pellet_14_20");
        go_Pellet_14_20.tag = "Pellet";
        go_Pellet_14_20.transform.position = new Vector3(6.5f, 1.0f, 0.0f);
        var go_Pellet_14_20_rb = go_Pellet_14_20.AddComponent<Rigidbody2D>();
        go_Pellet_14_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_14_20_bc = go_Pellet_14_20.AddComponent<BoxCollider2D>();
        go_Pellet_14_20_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_14_20_bc.isTrigger = true;
        var go_Pellet_14_20_sr = go_Pellet_14_20.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_14_20_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_14_20_sr.sharedMaterial = unlitMat;
        go_Pellet_14_20_sr.sortingOrder = 2;
        go_Pellet_14_20.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_14_20);

        // --- Node_14_21 ---
        var go_Node_14_21 = new GameObject("Node_14_21");
        go_Node_14_21.transform.position = new Vector3(7.5f, 1.0f, 0.0f);
        var go_Node_14_21_rb = go_Node_14_21.AddComponent<Rigidbody2D>();
        go_Node_14_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_14_21_bc = go_Node_14_21.AddComponent<BoxCollider2D>();
        go_Node_14_21_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_14_21_bc.isTrigger = true;
        go_Node_14_21.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_14_21);

        // --- Passage_14_27 ---
        var go_Passage_14_27 = new GameObject("Passage_14_27");
        go_Passage_14_27.transform.position = new Vector3(13.5f, 1.0f, 0.0f);
        var go_Passage_14_27_rb = go_Passage_14_27.AddComponent<Rigidbody2D>();
        go_Passage_14_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Passage_14_27_bc = go_Passage_14_27.AddComponent<BoxCollider2D>();
        go_Passage_14_27_bc.size = new Vector2(1.0f, 1.0f);
        go_Passage_14_27_bc.isTrigger = true;
        go_Passage_14_27.AddComponent<Passage>();
        EditorUtility.SetDirty(go_Passage_14_27);

        // --- Wall_15_0 ---
        var go_Wall_15_0 = new GameObject("Wall_15_0");
        go_Wall_15_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_0.transform.position = new Vector3(-13.5f, 0.0f, 0.0f);
        var go_Wall_15_0_rb = go_Wall_15_0.AddComponent<Rigidbody2D>();
        go_Wall_15_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_0_bc = go_Wall_15_0.AddComponent<BoxCollider2D>();
        go_Wall_15_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_0_sr = go_Wall_15_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_0);

        // --- Wall_15_1 ---
        var go_Wall_15_1 = new GameObject("Wall_15_1");
        go_Wall_15_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_1.transform.position = new Vector3(-12.5f, 0.0f, 0.0f);
        var go_Wall_15_1_rb = go_Wall_15_1.AddComponent<Rigidbody2D>();
        go_Wall_15_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_1_bc = go_Wall_15_1.AddComponent<BoxCollider2D>();
        go_Wall_15_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_1_sr = go_Wall_15_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_1);

        // --- Wall_15_2 ---
        var go_Wall_15_2 = new GameObject("Wall_15_2");
        go_Wall_15_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_2.transform.position = new Vector3(-11.5f, 0.0f, 0.0f);
        var go_Wall_15_2_rb = go_Wall_15_2.AddComponent<Rigidbody2D>();
        go_Wall_15_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_2_bc = go_Wall_15_2.AddComponent<BoxCollider2D>();
        go_Wall_15_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_2_sr = go_Wall_15_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_2);

        // --- Wall_15_3 ---
        var go_Wall_15_3 = new GameObject("Wall_15_3");
        go_Wall_15_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_3.transform.position = new Vector3(-10.5f, 0.0f, 0.0f);
        var go_Wall_15_3_rb = go_Wall_15_3.AddComponent<Rigidbody2D>();
        go_Wall_15_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_3_bc = go_Wall_15_3.AddComponent<BoxCollider2D>();
        go_Wall_15_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_3_sr = go_Wall_15_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_3);

        // --- Wall_15_4 ---
        var go_Wall_15_4 = new GameObject("Wall_15_4");
        go_Wall_15_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_4.transform.position = new Vector3(-9.5f, 0.0f, 0.0f);
        var go_Wall_15_4_rb = go_Wall_15_4.AddComponent<Rigidbody2D>();
        go_Wall_15_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_4_bc = go_Wall_15_4.AddComponent<BoxCollider2D>();
        go_Wall_15_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_4_sr = go_Wall_15_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_4);

        // --- Wall_15_5 ---
        var go_Wall_15_5 = new GameObject("Wall_15_5");
        go_Wall_15_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_5.transform.position = new Vector3(-8.5f, 0.0f, 0.0f);
        var go_Wall_15_5_rb = go_Wall_15_5.AddComponent<Rigidbody2D>();
        go_Wall_15_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_5_bc = go_Wall_15_5.AddComponent<BoxCollider2D>();
        go_Wall_15_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_5_sr = go_Wall_15_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_5);

        // --- Pellet_15_6 ---
        var go_Pellet_15_6 = new GameObject("Pellet_15_6");
        go_Pellet_15_6.tag = "Pellet";
        go_Pellet_15_6.transform.position = new Vector3(-7.5f, 0.0f, 0.0f);
        var go_Pellet_15_6_rb = go_Pellet_15_6.AddComponent<Rigidbody2D>();
        go_Pellet_15_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_15_6_bc = go_Pellet_15_6.AddComponent<BoxCollider2D>();
        go_Pellet_15_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_15_6_bc.isTrigger = true;
        var go_Pellet_15_6_sr = go_Pellet_15_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_15_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_15_6_sr.sharedMaterial = unlitMat;
        go_Pellet_15_6_sr.sortingOrder = 2;
        go_Pellet_15_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_15_6);

        // --- Wall_15_7 ---
        var go_Wall_15_7 = new GameObject("Wall_15_7");
        go_Wall_15_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_7.transform.position = new Vector3(-6.5f, 0.0f, 0.0f);
        var go_Wall_15_7_rb = go_Wall_15_7.AddComponent<Rigidbody2D>();
        go_Wall_15_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_7_bc = go_Wall_15_7.AddComponent<BoxCollider2D>();
        go_Wall_15_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_7_sr = go_Wall_15_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_7);

        // --- Wall_15_8 ---
        var go_Wall_15_8 = new GameObject("Wall_15_8");
        go_Wall_15_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_8.transform.position = new Vector3(-5.5f, 0.0f, 0.0f);
        var go_Wall_15_8_rb = go_Wall_15_8.AddComponent<Rigidbody2D>();
        go_Wall_15_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_8_bc = go_Wall_15_8.AddComponent<BoxCollider2D>();
        go_Wall_15_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_8_sr = go_Wall_15_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_8);

        // --- Wall_15_10 ---
        var go_Wall_15_10 = new GameObject("Wall_15_10");
        go_Wall_15_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_10.transform.position = new Vector3(-3.5f, 0.0f, 0.0f);
        var go_Wall_15_10_rb = go_Wall_15_10.AddComponent<Rigidbody2D>();
        go_Wall_15_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_10_bc = go_Wall_15_10.AddComponent<BoxCollider2D>();
        go_Wall_15_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_10_sr = go_Wall_15_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_10);

        // --- Node_15_11 ---
        var go_Node_15_11 = new GameObject("Node_15_11");
        go_Node_15_11.transform.position = new Vector3(-2.5f, 0.0f, 0.0f);
        var go_Node_15_11_rb = go_Node_15_11.AddComponent<Rigidbody2D>();
        go_Node_15_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_15_11_bc = go_Node_15_11.AddComponent<BoxCollider2D>();
        go_Node_15_11_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_15_11_bc.isTrigger = true;
        go_Node_15_11.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_15_11);

        // --- Node_15_12 ---
        var go_Node_15_12 = new GameObject("Node_15_12");
        go_Node_15_12.transform.position = new Vector3(-1.5f, 0.0f, 0.0f);
        var go_Node_15_12_rb = go_Node_15_12.AddComponent<Rigidbody2D>();
        go_Node_15_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_15_12_bc = go_Node_15_12.AddComponent<BoxCollider2D>();
        go_Node_15_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_15_12_bc.isTrigger = true;
        go_Node_15_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_15_12);

        // --- Node_15_13 ---
        var go_Node_15_13 = new GameObject("Node_15_13");
        go_Node_15_13.transform.position = new Vector3(-0.5f, 0.0f, 0.0f);
        var go_Node_15_13_rb = go_Node_15_13.AddComponent<Rigidbody2D>();
        go_Node_15_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_15_13_bc = go_Node_15_13.AddComponent<BoxCollider2D>();
        go_Node_15_13_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_15_13_bc.isTrigger = true;
        go_Node_15_13.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_15_13);

        // --- Node_15_14 ---
        var go_Node_15_14 = new GameObject("Node_15_14");
        go_Node_15_14.transform.position = new Vector3(0.5f, 0.0f, 0.0f);
        var go_Node_15_14_rb = go_Node_15_14.AddComponent<Rigidbody2D>();
        go_Node_15_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_15_14_bc = go_Node_15_14.AddComponent<BoxCollider2D>();
        go_Node_15_14_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_15_14_bc.isTrigger = true;
        go_Node_15_14.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_15_14);

        // --- Node_15_15 ---
        var go_Node_15_15 = new GameObject("Node_15_15");
        go_Node_15_15.transform.position = new Vector3(1.5f, 0.0f, 0.0f);
        var go_Node_15_15_rb = go_Node_15_15.AddComponent<Rigidbody2D>();
        go_Node_15_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_15_15_bc = go_Node_15_15.AddComponent<BoxCollider2D>();
        go_Node_15_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_15_15_bc.isTrigger = true;
        go_Node_15_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_15_15);

        // --- Node_15_16 ---
        var go_Node_15_16 = new GameObject("Node_15_16");
        go_Node_15_16.transform.position = new Vector3(2.5f, 0.0f, 0.0f);
        var go_Node_15_16_rb = go_Node_15_16.AddComponent<Rigidbody2D>();
        go_Node_15_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_15_16_bc = go_Node_15_16.AddComponent<BoxCollider2D>();
        go_Node_15_16_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_15_16_bc.isTrigger = true;
        go_Node_15_16.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_15_16);

        // --- Wall_15_17 ---
        var go_Wall_15_17 = new GameObject("Wall_15_17");
        go_Wall_15_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_17.transform.position = new Vector3(3.5f, 0.0f, 0.0f);
        var go_Wall_15_17_rb = go_Wall_15_17.AddComponent<Rigidbody2D>();
        go_Wall_15_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_17_bc = go_Wall_15_17.AddComponent<BoxCollider2D>();
        go_Wall_15_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_17_sr = go_Wall_15_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_17);

        // --- Wall_15_19 ---
        var go_Wall_15_19 = new GameObject("Wall_15_19");
        go_Wall_15_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_19.transform.position = new Vector3(5.5f, 0.0f, 0.0f);
        var go_Wall_15_19_rb = go_Wall_15_19.AddComponent<Rigidbody2D>();
        go_Wall_15_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_19_bc = go_Wall_15_19.AddComponent<BoxCollider2D>();
        go_Wall_15_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_19_sr = go_Wall_15_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_19);

        // --- Wall_15_20 ---
        var go_Wall_15_20 = new GameObject("Wall_15_20");
        go_Wall_15_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_20.transform.position = new Vector3(6.5f, 0.0f, 0.0f);
        var go_Wall_15_20_rb = go_Wall_15_20.AddComponent<Rigidbody2D>();
        go_Wall_15_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_20_bc = go_Wall_15_20.AddComponent<BoxCollider2D>();
        go_Wall_15_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_20_sr = go_Wall_15_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_20);

        // --- Pellet_15_21 ---
        var go_Pellet_15_21 = new GameObject("Pellet_15_21");
        go_Pellet_15_21.tag = "Pellet";
        go_Pellet_15_21.transform.position = new Vector3(7.5f, 0.0f, 0.0f);
        var go_Pellet_15_21_rb = go_Pellet_15_21.AddComponent<Rigidbody2D>();
        go_Pellet_15_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_15_21_bc = go_Pellet_15_21.AddComponent<BoxCollider2D>();
        go_Pellet_15_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_15_21_bc.isTrigger = true;
        var go_Pellet_15_21_sr = go_Pellet_15_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_15_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_15_21_sr.sharedMaterial = unlitMat;
        go_Pellet_15_21_sr.sortingOrder = 2;
        go_Pellet_15_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_15_21);

        // --- Wall_15_22 ---
        var go_Wall_15_22 = new GameObject("Wall_15_22");
        go_Wall_15_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_22.transform.position = new Vector3(8.5f, 0.0f, 0.0f);
        var go_Wall_15_22_rb = go_Wall_15_22.AddComponent<Rigidbody2D>();
        go_Wall_15_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_22_bc = go_Wall_15_22.AddComponent<BoxCollider2D>();
        go_Wall_15_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_22_sr = go_Wall_15_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_22);

        // --- Wall_15_23 ---
        var go_Wall_15_23 = new GameObject("Wall_15_23");
        go_Wall_15_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_23.transform.position = new Vector3(9.5f, 0.0f, 0.0f);
        var go_Wall_15_23_rb = go_Wall_15_23.AddComponent<Rigidbody2D>();
        go_Wall_15_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_23_bc = go_Wall_15_23.AddComponent<BoxCollider2D>();
        go_Wall_15_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_23_sr = go_Wall_15_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_23);

        // --- Wall_15_24 ---
        var go_Wall_15_24 = new GameObject("Wall_15_24");
        go_Wall_15_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_24.transform.position = new Vector3(10.5f, 0.0f, 0.0f);
        var go_Wall_15_24_rb = go_Wall_15_24.AddComponent<Rigidbody2D>();
        go_Wall_15_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_24_bc = go_Wall_15_24.AddComponent<BoxCollider2D>();
        go_Wall_15_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_24_sr = go_Wall_15_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_24);

        // --- Wall_15_25 ---
        var go_Wall_15_25 = new GameObject("Wall_15_25");
        go_Wall_15_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_25.transform.position = new Vector3(11.5f, 0.0f, 0.0f);
        var go_Wall_15_25_rb = go_Wall_15_25.AddComponent<Rigidbody2D>();
        go_Wall_15_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_25_bc = go_Wall_15_25.AddComponent<BoxCollider2D>();
        go_Wall_15_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_25_sr = go_Wall_15_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_25);

        // --- Wall_15_26 ---
        var go_Wall_15_26 = new GameObject("Wall_15_26");
        go_Wall_15_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_26.transform.position = new Vector3(12.5f, 0.0f, 0.0f);
        var go_Wall_15_26_rb = go_Wall_15_26.AddComponent<Rigidbody2D>();
        go_Wall_15_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_26_bc = go_Wall_15_26.AddComponent<BoxCollider2D>();
        go_Wall_15_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_26_sr = go_Wall_15_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_26);

        // --- Wall_15_27 ---
        var go_Wall_15_27 = new GameObject("Wall_15_27");
        go_Wall_15_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_15_27.transform.position = new Vector3(13.5f, 0.0f, 0.0f);
        var go_Wall_15_27_rb = go_Wall_15_27.AddComponent<Rigidbody2D>();
        go_Wall_15_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_15_27_bc = go_Wall_15_27.AddComponent<BoxCollider2D>();
        go_Wall_15_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_15_27_sr = go_Wall_15_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_15_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_15_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_15_27);

        // --- Wall_16_0 ---
        var go_Wall_16_0 = new GameObject("Wall_16_0");
        go_Wall_16_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_0.transform.position = new Vector3(-13.5f, -1.0f, 0.0f);
        var go_Wall_16_0_rb = go_Wall_16_0.AddComponent<Rigidbody2D>();
        go_Wall_16_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_0_bc = go_Wall_16_0.AddComponent<BoxCollider2D>();
        go_Wall_16_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_0_sr = go_Wall_16_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_0);

        // --- Wall_16_1 ---
        var go_Wall_16_1 = new GameObject("Wall_16_1");
        go_Wall_16_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_1.transform.position = new Vector3(-12.5f, -1.0f, 0.0f);
        var go_Wall_16_1_rb = go_Wall_16_1.AddComponent<Rigidbody2D>();
        go_Wall_16_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_1_bc = go_Wall_16_1.AddComponent<BoxCollider2D>();
        go_Wall_16_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_1_sr = go_Wall_16_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_1);

        // --- Wall_16_2 ---
        var go_Wall_16_2 = new GameObject("Wall_16_2");
        go_Wall_16_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_2.transform.position = new Vector3(-11.5f, -1.0f, 0.0f);
        var go_Wall_16_2_rb = go_Wall_16_2.AddComponent<Rigidbody2D>();
        go_Wall_16_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_2_bc = go_Wall_16_2.AddComponent<BoxCollider2D>();
        go_Wall_16_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_2_sr = go_Wall_16_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_2);

        // --- Wall_16_3 ---
        var go_Wall_16_3 = new GameObject("Wall_16_3");
        go_Wall_16_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_3.transform.position = new Vector3(-10.5f, -1.0f, 0.0f);
        var go_Wall_16_3_rb = go_Wall_16_3.AddComponent<Rigidbody2D>();
        go_Wall_16_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_3_bc = go_Wall_16_3.AddComponent<BoxCollider2D>();
        go_Wall_16_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_3_sr = go_Wall_16_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_3);

        // --- Wall_16_4 ---
        var go_Wall_16_4 = new GameObject("Wall_16_4");
        go_Wall_16_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_4.transform.position = new Vector3(-9.5f, -1.0f, 0.0f);
        var go_Wall_16_4_rb = go_Wall_16_4.AddComponent<Rigidbody2D>();
        go_Wall_16_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_4_bc = go_Wall_16_4.AddComponent<BoxCollider2D>();
        go_Wall_16_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_4_sr = go_Wall_16_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_4);

        // --- Wall_16_5 ---
        var go_Wall_16_5 = new GameObject("Wall_16_5");
        go_Wall_16_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_5.transform.position = new Vector3(-8.5f, -1.0f, 0.0f);
        var go_Wall_16_5_rb = go_Wall_16_5.AddComponent<Rigidbody2D>();
        go_Wall_16_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_5_bc = go_Wall_16_5.AddComponent<BoxCollider2D>();
        go_Wall_16_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_5_sr = go_Wall_16_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_5);

        // --- Pellet_16_6 ---
        var go_Pellet_16_6 = new GameObject("Pellet_16_6");
        go_Pellet_16_6.tag = "Pellet";
        go_Pellet_16_6.transform.position = new Vector3(-7.5f, -1.0f, 0.0f);
        var go_Pellet_16_6_rb = go_Pellet_16_6.AddComponent<Rigidbody2D>();
        go_Pellet_16_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_16_6_bc = go_Pellet_16_6.AddComponent<BoxCollider2D>();
        go_Pellet_16_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_16_6_bc.isTrigger = true;
        var go_Pellet_16_6_sr = go_Pellet_16_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_16_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_16_6_sr.sharedMaterial = unlitMat;
        go_Pellet_16_6_sr.sortingOrder = 2;
        go_Pellet_16_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_16_6);

        // --- Wall_16_7 ---
        var go_Wall_16_7 = new GameObject("Wall_16_7");
        go_Wall_16_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_7.transform.position = new Vector3(-6.5f, -1.0f, 0.0f);
        var go_Wall_16_7_rb = go_Wall_16_7.AddComponent<Rigidbody2D>();
        go_Wall_16_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_7_bc = go_Wall_16_7.AddComponent<BoxCollider2D>();
        go_Wall_16_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_7_sr = go_Wall_16_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_7);

        // --- Wall_16_8 ---
        var go_Wall_16_8 = new GameObject("Wall_16_8");
        go_Wall_16_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_8.transform.position = new Vector3(-5.5f, -1.0f, 0.0f);
        var go_Wall_16_8_rb = go_Wall_16_8.AddComponent<Rigidbody2D>();
        go_Wall_16_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_8_bc = go_Wall_16_8.AddComponent<BoxCollider2D>();
        go_Wall_16_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_8_sr = go_Wall_16_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_8);

        // --- Wall_16_10 ---
        var go_Wall_16_10 = new GameObject("Wall_16_10");
        go_Wall_16_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_10.transform.position = new Vector3(-3.5f, -1.0f, 0.0f);
        var go_Wall_16_10_rb = go_Wall_16_10.AddComponent<Rigidbody2D>();
        go_Wall_16_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_10_bc = go_Wall_16_10.AddComponent<BoxCollider2D>();
        go_Wall_16_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_10_sr = go_Wall_16_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_10);

        // --- Wall_16_11 ---
        var go_Wall_16_11 = new GameObject("Wall_16_11");
        go_Wall_16_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_11.transform.position = new Vector3(-2.5f, -1.0f, 0.0f);
        var go_Wall_16_11_rb = go_Wall_16_11.AddComponent<Rigidbody2D>();
        go_Wall_16_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_11_bc = go_Wall_16_11.AddComponent<BoxCollider2D>();
        go_Wall_16_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_11_sr = go_Wall_16_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_11);

        // --- Wall_16_12 ---
        var go_Wall_16_12 = new GameObject("Wall_16_12");
        go_Wall_16_12.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_12.transform.position = new Vector3(-1.5f, -1.0f, 0.0f);
        var go_Wall_16_12_rb = go_Wall_16_12.AddComponent<Rigidbody2D>();
        go_Wall_16_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_12_bc = go_Wall_16_12.AddComponent<BoxCollider2D>();
        go_Wall_16_12_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_12_sr = go_Wall_16_12.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_12_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_12_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_12);

        // --- Wall_16_13 ---
        var go_Wall_16_13 = new GameObject("Wall_16_13");
        go_Wall_16_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_13.transform.position = new Vector3(-0.5f, -1.0f, 0.0f);
        var go_Wall_16_13_rb = go_Wall_16_13.AddComponent<Rigidbody2D>();
        go_Wall_16_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_13_bc = go_Wall_16_13.AddComponent<BoxCollider2D>();
        go_Wall_16_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_13_sr = go_Wall_16_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_13);

        // --- Wall_16_14 ---
        var go_Wall_16_14 = new GameObject("Wall_16_14");
        go_Wall_16_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_14.transform.position = new Vector3(0.5f, -1.0f, 0.0f);
        var go_Wall_16_14_rb = go_Wall_16_14.AddComponent<Rigidbody2D>();
        go_Wall_16_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_14_bc = go_Wall_16_14.AddComponent<BoxCollider2D>();
        go_Wall_16_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_14_sr = go_Wall_16_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_14);

        // --- Wall_16_15 ---
        var go_Wall_16_15 = new GameObject("Wall_16_15");
        go_Wall_16_15.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_15.transform.position = new Vector3(1.5f, -1.0f, 0.0f);
        var go_Wall_16_15_rb = go_Wall_16_15.AddComponent<Rigidbody2D>();
        go_Wall_16_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_15_bc = go_Wall_16_15.AddComponent<BoxCollider2D>();
        go_Wall_16_15_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_15_sr = go_Wall_16_15.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_15_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_15_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_15);

        // --- Wall_16_16 ---
        var go_Wall_16_16 = new GameObject("Wall_16_16");
        go_Wall_16_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_16.transform.position = new Vector3(2.5f, -1.0f, 0.0f);
        var go_Wall_16_16_rb = go_Wall_16_16.AddComponent<Rigidbody2D>();
        go_Wall_16_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_16_bc = go_Wall_16_16.AddComponent<BoxCollider2D>();
        go_Wall_16_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_16_sr = go_Wall_16_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_16);

        // --- Wall_16_17 ---
        var go_Wall_16_17 = new GameObject("Wall_16_17");
        go_Wall_16_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_17.transform.position = new Vector3(3.5f, -1.0f, 0.0f);
        var go_Wall_16_17_rb = go_Wall_16_17.AddComponent<Rigidbody2D>();
        go_Wall_16_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_17_bc = go_Wall_16_17.AddComponent<BoxCollider2D>();
        go_Wall_16_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_17_sr = go_Wall_16_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_17);

        // --- Wall_16_19 ---
        var go_Wall_16_19 = new GameObject("Wall_16_19");
        go_Wall_16_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_19.transform.position = new Vector3(5.5f, -1.0f, 0.0f);
        var go_Wall_16_19_rb = go_Wall_16_19.AddComponent<Rigidbody2D>();
        go_Wall_16_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_19_bc = go_Wall_16_19.AddComponent<BoxCollider2D>();
        go_Wall_16_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_19_sr = go_Wall_16_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_19);

        // --- Wall_16_20 ---
        var go_Wall_16_20 = new GameObject("Wall_16_20");
        go_Wall_16_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_20.transform.position = new Vector3(6.5f, -1.0f, 0.0f);
        var go_Wall_16_20_rb = go_Wall_16_20.AddComponent<Rigidbody2D>();
        go_Wall_16_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_20_bc = go_Wall_16_20.AddComponent<BoxCollider2D>();
        go_Wall_16_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_20_sr = go_Wall_16_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_20);

        // --- Pellet_16_21 ---
        var go_Pellet_16_21 = new GameObject("Pellet_16_21");
        go_Pellet_16_21.tag = "Pellet";
        go_Pellet_16_21.transform.position = new Vector3(7.5f, -1.0f, 0.0f);
        var go_Pellet_16_21_rb = go_Pellet_16_21.AddComponent<Rigidbody2D>();
        go_Pellet_16_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_16_21_bc = go_Pellet_16_21.AddComponent<BoxCollider2D>();
        go_Pellet_16_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_16_21_bc.isTrigger = true;
        var go_Pellet_16_21_sr = go_Pellet_16_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_16_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_16_21_sr.sharedMaterial = unlitMat;
        go_Pellet_16_21_sr.sortingOrder = 2;
        go_Pellet_16_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_16_21);

        // --- Wall_16_22 ---
        var go_Wall_16_22 = new GameObject("Wall_16_22");
        go_Wall_16_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_22.transform.position = new Vector3(8.5f, -1.0f, 0.0f);
        var go_Wall_16_22_rb = go_Wall_16_22.AddComponent<Rigidbody2D>();
        go_Wall_16_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_22_bc = go_Wall_16_22.AddComponent<BoxCollider2D>();
        go_Wall_16_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_22_sr = go_Wall_16_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_22);

        // --- Wall_16_23 ---
        var go_Wall_16_23 = new GameObject("Wall_16_23");
        go_Wall_16_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_23.transform.position = new Vector3(9.5f, -1.0f, 0.0f);
        var go_Wall_16_23_rb = go_Wall_16_23.AddComponent<Rigidbody2D>();
        go_Wall_16_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_23_bc = go_Wall_16_23.AddComponent<BoxCollider2D>();
        go_Wall_16_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_23_sr = go_Wall_16_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_23);

        // --- Wall_16_24 ---
        var go_Wall_16_24 = new GameObject("Wall_16_24");
        go_Wall_16_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_24.transform.position = new Vector3(10.5f, -1.0f, 0.0f);
        var go_Wall_16_24_rb = go_Wall_16_24.AddComponent<Rigidbody2D>();
        go_Wall_16_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_24_bc = go_Wall_16_24.AddComponent<BoxCollider2D>();
        go_Wall_16_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_24_sr = go_Wall_16_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_24);

        // --- Wall_16_25 ---
        var go_Wall_16_25 = new GameObject("Wall_16_25");
        go_Wall_16_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_25.transform.position = new Vector3(11.5f, -1.0f, 0.0f);
        var go_Wall_16_25_rb = go_Wall_16_25.AddComponent<Rigidbody2D>();
        go_Wall_16_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_25_bc = go_Wall_16_25.AddComponent<BoxCollider2D>();
        go_Wall_16_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_25_sr = go_Wall_16_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_25);

        // --- Wall_16_26 ---
        var go_Wall_16_26 = new GameObject("Wall_16_26");
        go_Wall_16_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_26.transform.position = new Vector3(12.5f, -1.0f, 0.0f);
        var go_Wall_16_26_rb = go_Wall_16_26.AddComponent<Rigidbody2D>();
        go_Wall_16_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_26_bc = go_Wall_16_26.AddComponent<BoxCollider2D>();
        go_Wall_16_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_26_sr = go_Wall_16_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_26);

        // --- Wall_16_27 ---
        var go_Wall_16_27 = new GameObject("Wall_16_27");
        go_Wall_16_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_16_27.transform.position = new Vector3(13.5f, -1.0f, 0.0f);
        var go_Wall_16_27_rb = go_Wall_16_27.AddComponent<Rigidbody2D>();
        go_Wall_16_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_16_27_bc = go_Wall_16_27.AddComponent<BoxCollider2D>();
        go_Wall_16_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_16_27_sr = go_Wall_16_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_16_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_16_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_16_27);

        // --- Wall_17_0 ---
        var go_Wall_17_0 = new GameObject("Wall_17_0");
        go_Wall_17_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_0.transform.position = new Vector3(-13.5f, -2.0f, 0.0f);
        var go_Wall_17_0_rb = go_Wall_17_0.AddComponent<Rigidbody2D>();
        go_Wall_17_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_0_bc = go_Wall_17_0.AddComponent<BoxCollider2D>();
        go_Wall_17_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_0_sr = go_Wall_17_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_0);

        // --- Wall_17_1 ---
        var go_Wall_17_1 = new GameObject("Wall_17_1");
        go_Wall_17_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_1.transform.position = new Vector3(-12.5f, -2.0f, 0.0f);
        var go_Wall_17_1_rb = go_Wall_17_1.AddComponent<Rigidbody2D>();
        go_Wall_17_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_1_bc = go_Wall_17_1.AddComponent<BoxCollider2D>();
        go_Wall_17_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_1_sr = go_Wall_17_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_1);

        // --- Wall_17_2 ---
        var go_Wall_17_2 = new GameObject("Wall_17_2");
        go_Wall_17_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_2.transform.position = new Vector3(-11.5f, -2.0f, 0.0f);
        var go_Wall_17_2_rb = go_Wall_17_2.AddComponent<Rigidbody2D>();
        go_Wall_17_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_2_bc = go_Wall_17_2.AddComponent<BoxCollider2D>();
        go_Wall_17_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_2_sr = go_Wall_17_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_2);

        // --- Wall_17_3 ---
        var go_Wall_17_3 = new GameObject("Wall_17_3");
        go_Wall_17_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_3.transform.position = new Vector3(-10.5f, -2.0f, 0.0f);
        var go_Wall_17_3_rb = go_Wall_17_3.AddComponent<Rigidbody2D>();
        go_Wall_17_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_3_bc = go_Wall_17_3.AddComponent<BoxCollider2D>();
        go_Wall_17_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_3_sr = go_Wall_17_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_3);

        // --- Wall_17_4 ---
        var go_Wall_17_4 = new GameObject("Wall_17_4");
        go_Wall_17_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_4.transform.position = new Vector3(-9.5f, -2.0f, 0.0f);
        var go_Wall_17_4_rb = go_Wall_17_4.AddComponent<Rigidbody2D>();
        go_Wall_17_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_4_bc = go_Wall_17_4.AddComponent<BoxCollider2D>();
        go_Wall_17_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_4_sr = go_Wall_17_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_4);

        // --- Wall_17_5 ---
        var go_Wall_17_5 = new GameObject("Wall_17_5");
        go_Wall_17_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_5.transform.position = new Vector3(-8.5f, -2.0f, 0.0f);
        var go_Wall_17_5_rb = go_Wall_17_5.AddComponent<Rigidbody2D>();
        go_Wall_17_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_5_bc = go_Wall_17_5.AddComponent<BoxCollider2D>();
        go_Wall_17_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_5_sr = go_Wall_17_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_5);

        // --- Pellet_17_6 ---
        var go_Pellet_17_6 = new GameObject("Pellet_17_6");
        go_Pellet_17_6.tag = "Pellet";
        go_Pellet_17_6.transform.position = new Vector3(-7.5f, -2.0f, 0.0f);
        var go_Pellet_17_6_rb = go_Pellet_17_6.AddComponent<Rigidbody2D>();
        go_Pellet_17_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_17_6_bc = go_Pellet_17_6.AddComponent<BoxCollider2D>();
        go_Pellet_17_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_17_6_bc.isTrigger = true;
        var go_Pellet_17_6_sr = go_Pellet_17_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_17_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_17_6_sr.sharedMaterial = unlitMat;
        go_Pellet_17_6_sr.sortingOrder = 2;
        go_Pellet_17_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_17_6);

        // --- Wall_17_7 ---
        var go_Wall_17_7 = new GameObject("Wall_17_7");
        go_Wall_17_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_7.transform.position = new Vector3(-6.5f, -2.0f, 0.0f);
        var go_Wall_17_7_rb = go_Wall_17_7.AddComponent<Rigidbody2D>();
        go_Wall_17_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_7_bc = go_Wall_17_7.AddComponent<BoxCollider2D>();
        go_Wall_17_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_7_sr = go_Wall_17_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_7);

        // --- Wall_17_8 ---
        var go_Wall_17_8 = new GameObject("Wall_17_8");
        go_Wall_17_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_8.transform.position = new Vector3(-5.5f, -2.0f, 0.0f);
        var go_Wall_17_8_rb = go_Wall_17_8.AddComponent<Rigidbody2D>();
        go_Wall_17_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_8_bc = go_Wall_17_8.AddComponent<BoxCollider2D>();
        go_Wall_17_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_8_sr = go_Wall_17_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_8);

        // --- Node_17_9 ---
        var go_Node_17_9 = new GameObject("Node_17_9");
        go_Node_17_9.transform.position = new Vector3(-4.5f, -2.0f, 0.0f);
        var go_Node_17_9_rb = go_Node_17_9.AddComponent<Rigidbody2D>();
        go_Node_17_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_17_9_bc = go_Node_17_9.AddComponent<BoxCollider2D>();
        go_Node_17_9_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_17_9_bc.isTrigger = true;
        go_Node_17_9.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_17_9);

        // --- Node_17_18 ---
        var go_Node_17_18 = new GameObject("Node_17_18");
        go_Node_17_18.transform.position = new Vector3(4.5f, -2.0f, 0.0f);
        var go_Node_17_18_rb = go_Node_17_18.AddComponent<Rigidbody2D>();
        go_Node_17_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_17_18_bc = go_Node_17_18.AddComponent<BoxCollider2D>();
        go_Node_17_18_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_17_18_bc.isTrigger = true;
        go_Node_17_18.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_17_18);

        // --- Wall_17_19 ---
        var go_Wall_17_19 = new GameObject("Wall_17_19");
        go_Wall_17_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_19.transform.position = new Vector3(5.5f, -2.0f, 0.0f);
        var go_Wall_17_19_rb = go_Wall_17_19.AddComponent<Rigidbody2D>();
        go_Wall_17_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_19_bc = go_Wall_17_19.AddComponent<BoxCollider2D>();
        go_Wall_17_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_19_sr = go_Wall_17_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_19);

        // --- Wall_17_20 ---
        var go_Wall_17_20 = new GameObject("Wall_17_20");
        go_Wall_17_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_20.transform.position = new Vector3(6.5f, -2.0f, 0.0f);
        var go_Wall_17_20_rb = go_Wall_17_20.AddComponent<Rigidbody2D>();
        go_Wall_17_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_20_bc = go_Wall_17_20.AddComponent<BoxCollider2D>();
        go_Wall_17_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_20_sr = go_Wall_17_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_20);

        // --- Pellet_17_21 ---
        var go_Pellet_17_21 = new GameObject("Pellet_17_21");
        go_Pellet_17_21.tag = "Pellet";
        go_Pellet_17_21.transform.position = new Vector3(7.5f, -2.0f, 0.0f);
        var go_Pellet_17_21_rb = go_Pellet_17_21.AddComponent<Rigidbody2D>();
        go_Pellet_17_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_17_21_bc = go_Pellet_17_21.AddComponent<BoxCollider2D>();
        go_Pellet_17_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_17_21_bc.isTrigger = true;
        var go_Pellet_17_21_sr = go_Pellet_17_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_17_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_17_21_sr.sharedMaterial = unlitMat;
        go_Pellet_17_21_sr.sortingOrder = 2;
        go_Pellet_17_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_17_21);

        // --- Wall_17_22 ---
        var go_Wall_17_22 = new GameObject("Wall_17_22");
        go_Wall_17_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_22.transform.position = new Vector3(8.5f, -2.0f, 0.0f);
        var go_Wall_17_22_rb = go_Wall_17_22.AddComponent<Rigidbody2D>();
        go_Wall_17_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_22_bc = go_Wall_17_22.AddComponent<BoxCollider2D>();
        go_Wall_17_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_22_sr = go_Wall_17_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_22);

        // --- Wall_17_23 ---
        var go_Wall_17_23 = new GameObject("Wall_17_23");
        go_Wall_17_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_23.transform.position = new Vector3(9.5f, -2.0f, 0.0f);
        var go_Wall_17_23_rb = go_Wall_17_23.AddComponent<Rigidbody2D>();
        go_Wall_17_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_23_bc = go_Wall_17_23.AddComponent<BoxCollider2D>();
        go_Wall_17_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_23_sr = go_Wall_17_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_23);

        // --- Wall_17_24 ---
        var go_Wall_17_24 = new GameObject("Wall_17_24");
        go_Wall_17_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_24.transform.position = new Vector3(10.5f, -2.0f, 0.0f);
        var go_Wall_17_24_rb = go_Wall_17_24.AddComponent<Rigidbody2D>();
        go_Wall_17_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_24_bc = go_Wall_17_24.AddComponent<BoxCollider2D>();
        go_Wall_17_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_24_sr = go_Wall_17_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_24);

        // --- Wall_17_25 ---
        var go_Wall_17_25 = new GameObject("Wall_17_25");
        go_Wall_17_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_25.transform.position = new Vector3(11.5f, -2.0f, 0.0f);
        var go_Wall_17_25_rb = go_Wall_17_25.AddComponent<Rigidbody2D>();
        go_Wall_17_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_25_bc = go_Wall_17_25.AddComponent<BoxCollider2D>();
        go_Wall_17_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_25_sr = go_Wall_17_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_25);

        // --- Wall_17_26 ---
        var go_Wall_17_26 = new GameObject("Wall_17_26");
        go_Wall_17_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_26.transform.position = new Vector3(12.5f, -2.0f, 0.0f);
        var go_Wall_17_26_rb = go_Wall_17_26.AddComponent<Rigidbody2D>();
        go_Wall_17_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_26_bc = go_Wall_17_26.AddComponent<BoxCollider2D>();
        go_Wall_17_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_26_sr = go_Wall_17_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_26);

        // --- Wall_17_27 ---
        var go_Wall_17_27 = new GameObject("Wall_17_27");
        go_Wall_17_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_17_27.transform.position = new Vector3(13.5f, -2.0f, 0.0f);
        var go_Wall_17_27_rb = go_Wall_17_27.AddComponent<Rigidbody2D>();
        go_Wall_17_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_17_27_bc = go_Wall_17_27.AddComponent<BoxCollider2D>();
        go_Wall_17_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_17_27_sr = go_Wall_17_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_17_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_17_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_17_27);

        // --- Wall_18_0 ---
        var go_Wall_18_0 = new GameObject("Wall_18_0");
        go_Wall_18_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_0.transform.position = new Vector3(-13.5f, -3.0f, 0.0f);
        var go_Wall_18_0_rb = go_Wall_18_0.AddComponent<Rigidbody2D>();
        go_Wall_18_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_0_bc = go_Wall_18_0.AddComponent<BoxCollider2D>();
        go_Wall_18_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_0_sr = go_Wall_18_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_0);

        // --- Wall_18_1 ---
        var go_Wall_18_1 = new GameObject("Wall_18_1");
        go_Wall_18_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_1.transform.position = new Vector3(-12.5f, -3.0f, 0.0f);
        var go_Wall_18_1_rb = go_Wall_18_1.AddComponent<Rigidbody2D>();
        go_Wall_18_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_1_bc = go_Wall_18_1.AddComponent<BoxCollider2D>();
        go_Wall_18_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_1_sr = go_Wall_18_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_1);

        // --- Wall_18_2 ---
        var go_Wall_18_2 = new GameObject("Wall_18_2");
        go_Wall_18_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_2.transform.position = new Vector3(-11.5f, -3.0f, 0.0f);
        var go_Wall_18_2_rb = go_Wall_18_2.AddComponent<Rigidbody2D>();
        go_Wall_18_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_2_bc = go_Wall_18_2.AddComponent<BoxCollider2D>();
        go_Wall_18_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_2_sr = go_Wall_18_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_2);

        // --- Wall_18_3 ---
        var go_Wall_18_3 = new GameObject("Wall_18_3");
        go_Wall_18_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_3.transform.position = new Vector3(-10.5f, -3.0f, 0.0f);
        var go_Wall_18_3_rb = go_Wall_18_3.AddComponent<Rigidbody2D>();
        go_Wall_18_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_3_bc = go_Wall_18_3.AddComponent<BoxCollider2D>();
        go_Wall_18_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_3_sr = go_Wall_18_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_3);

        // --- Wall_18_4 ---
        var go_Wall_18_4 = new GameObject("Wall_18_4");
        go_Wall_18_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_4.transform.position = new Vector3(-9.5f, -3.0f, 0.0f);
        var go_Wall_18_4_rb = go_Wall_18_4.AddComponent<Rigidbody2D>();
        go_Wall_18_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_4_bc = go_Wall_18_4.AddComponent<BoxCollider2D>();
        go_Wall_18_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_4_sr = go_Wall_18_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_4);

        // --- Wall_18_5 ---
        var go_Wall_18_5 = new GameObject("Wall_18_5");
        go_Wall_18_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_5.transform.position = new Vector3(-8.5f, -3.0f, 0.0f);
        var go_Wall_18_5_rb = go_Wall_18_5.AddComponent<Rigidbody2D>();
        go_Wall_18_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_5_bc = go_Wall_18_5.AddComponent<BoxCollider2D>();
        go_Wall_18_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_5_sr = go_Wall_18_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_5);

        // --- Pellet_18_6 ---
        var go_Pellet_18_6 = new GameObject("Pellet_18_6");
        go_Pellet_18_6.tag = "Pellet";
        go_Pellet_18_6.transform.position = new Vector3(-7.5f, -3.0f, 0.0f);
        var go_Pellet_18_6_rb = go_Pellet_18_6.AddComponent<Rigidbody2D>();
        go_Pellet_18_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_18_6_bc = go_Pellet_18_6.AddComponent<BoxCollider2D>();
        go_Pellet_18_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_18_6_bc.isTrigger = true;
        var go_Pellet_18_6_sr = go_Pellet_18_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_18_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_18_6_sr.sharedMaterial = unlitMat;
        go_Pellet_18_6_sr.sortingOrder = 2;
        go_Pellet_18_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_18_6);

        // --- Wall_18_7 ---
        var go_Wall_18_7 = new GameObject("Wall_18_7");
        go_Wall_18_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_7.transform.position = new Vector3(-6.5f, -3.0f, 0.0f);
        var go_Wall_18_7_rb = go_Wall_18_7.AddComponent<Rigidbody2D>();
        go_Wall_18_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_7_bc = go_Wall_18_7.AddComponent<BoxCollider2D>();
        go_Wall_18_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_7_sr = go_Wall_18_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_7);

        // --- Wall_18_8 ---
        var go_Wall_18_8 = new GameObject("Wall_18_8");
        go_Wall_18_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_8.transform.position = new Vector3(-5.5f, -3.0f, 0.0f);
        var go_Wall_18_8_rb = go_Wall_18_8.AddComponent<Rigidbody2D>();
        go_Wall_18_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_8_bc = go_Wall_18_8.AddComponent<BoxCollider2D>();
        go_Wall_18_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_8_sr = go_Wall_18_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_8);

        // --- Wall_18_10 ---
        var go_Wall_18_10 = new GameObject("Wall_18_10");
        go_Wall_18_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_10.transform.position = new Vector3(-3.5f, -3.0f, 0.0f);
        var go_Wall_18_10_rb = go_Wall_18_10.AddComponent<Rigidbody2D>();
        go_Wall_18_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_10_bc = go_Wall_18_10.AddComponent<BoxCollider2D>();
        go_Wall_18_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_10_sr = go_Wall_18_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_10);

        // --- Wall_18_11 ---
        var go_Wall_18_11 = new GameObject("Wall_18_11");
        go_Wall_18_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_11.transform.position = new Vector3(-2.5f, -3.0f, 0.0f);
        var go_Wall_18_11_rb = go_Wall_18_11.AddComponent<Rigidbody2D>();
        go_Wall_18_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_11_bc = go_Wall_18_11.AddComponent<BoxCollider2D>();
        go_Wall_18_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_11_sr = go_Wall_18_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_11);

        // --- Wall_18_12 ---
        var go_Wall_18_12 = new GameObject("Wall_18_12");
        go_Wall_18_12.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_12.transform.position = new Vector3(-1.5f, -3.0f, 0.0f);
        var go_Wall_18_12_rb = go_Wall_18_12.AddComponent<Rigidbody2D>();
        go_Wall_18_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_12_bc = go_Wall_18_12.AddComponent<BoxCollider2D>();
        go_Wall_18_12_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_12_sr = go_Wall_18_12.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_12_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_12_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_12);

        // --- Wall_18_13 ---
        var go_Wall_18_13 = new GameObject("Wall_18_13");
        go_Wall_18_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_13.transform.position = new Vector3(-0.5f, -3.0f, 0.0f);
        var go_Wall_18_13_rb = go_Wall_18_13.AddComponent<Rigidbody2D>();
        go_Wall_18_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_13_bc = go_Wall_18_13.AddComponent<BoxCollider2D>();
        go_Wall_18_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_13_sr = go_Wall_18_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_13);

        // --- Wall_18_14 ---
        var go_Wall_18_14 = new GameObject("Wall_18_14");
        go_Wall_18_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_14.transform.position = new Vector3(0.5f, -3.0f, 0.0f);
        var go_Wall_18_14_rb = go_Wall_18_14.AddComponent<Rigidbody2D>();
        go_Wall_18_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_14_bc = go_Wall_18_14.AddComponent<BoxCollider2D>();
        go_Wall_18_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_14_sr = go_Wall_18_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_14);

        // --- Wall_18_15 ---
        var go_Wall_18_15 = new GameObject("Wall_18_15");
        go_Wall_18_15.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_15.transform.position = new Vector3(1.5f, -3.0f, 0.0f);
        var go_Wall_18_15_rb = go_Wall_18_15.AddComponent<Rigidbody2D>();
        go_Wall_18_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_15_bc = go_Wall_18_15.AddComponent<BoxCollider2D>();
        go_Wall_18_15_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_15_sr = go_Wall_18_15.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_15_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_15_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_15);

        // --- Wall_18_16 ---
        var go_Wall_18_16 = new GameObject("Wall_18_16");
        go_Wall_18_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_16.transform.position = new Vector3(2.5f, -3.0f, 0.0f);
        var go_Wall_18_16_rb = go_Wall_18_16.AddComponent<Rigidbody2D>();
        go_Wall_18_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_16_bc = go_Wall_18_16.AddComponent<BoxCollider2D>();
        go_Wall_18_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_16_sr = go_Wall_18_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_16);

        // --- Wall_18_17 ---
        var go_Wall_18_17 = new GameObject("Wall_18_17");
        go_Wall_18_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_17.transform.position = new Vector3(3.5f, -3.0f, 0.0f);
        var go_Wall_18_17_rb = go_Wall_18_17.AddComponent<Rigidbody2D>();
        go_Wall_18_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_17_bc = go_Wall_18_17.AddComponent<BoxCollider2D>();
        go_Wall_18_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_17_sr = go_Wall_18_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_17);

        // --- Wall_18_19 ---
        var go_Wall_18_19 = new GameObject("Wall_18_19");
        go_Wall_18_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_19.transform.position = new Vector3(5.5f, -3.0f, 0.0f);
        var go_Wall_18_19_rb = go_Wall_18_19.AddComponent<Rigidbody2D>();
        go_Wall_18_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_19_bc = go_Wall_18_19.AddComponent<BoxCollider2D>();
        go_Wall_18_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_19_sr = go_Wall_18_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_19);

        // --- Wall_18_20 ---
        var go_Wall_18_20 = new GameObject("Wall_18_20");
        go_Wall_18_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_20.transform.position = new Vector3(6.5f, -3.0f, 0.0f);
        var go_Wall_18_20_rb = go_Wall_18_20.AddComponent<Rigidbody2D>();
        go_Wall_18_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_20_bc = go_Wall_18_20.AddComponent<BoxCollider2D>();
        go_Wall_18_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_20_sr = go_Wall_18_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_20);

        // --- Pellet_18_21 ---
        var go_Pellet_18_21 = new GameObject("Pellet_18_21");
        go_Pellet_18_21.tag = "Pellet";
        go_Pellet_18_21.transform.position = new Vector3(7.5f, -3.0f, 0.0f);
        var go_Pellet_18_21_rb = go_Pellet_18_21.AddComponent<Rigidbody2D>();
        go_Pellet_18_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_18_21_bc = go_Pellet_18_21.AddComponent<BoxCollider2D>();
        go_Pellet_18_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_18_21_bc.isTrigger = true;
        var go_Pellet_18_21_sr = go_Pellet_18_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_18_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_18_21_sr.sharedMaterial = unlitMat;
        go_Pellet_18_21_sr.sortingOrder = 2;
        go_Pellet_18_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_18_21);

        // --- Wall_18_22 ---
        var go_Wall_18_22 = new GameObject("Wall_18_22");
        go_Wall_18_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_22.transform.position = new Vector3(8.5f, -3.0f, 0.0f);
        var go_Wall_18_22_rb = go_Wall_18_22.AddComponent<Rigidbody2D>();
        go_Wall_18_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_22_bc = go_Wall_18_22.AddComponent<BoxCollider2D>();
        go_Wall_18_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_22_sr = go_Wall_18_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_22);

        // --- Wall_18_23 ---
        var go_Wall_18_23 = new GameObject("Wall_18_23");
        go_Wall_18_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_23.transform.position = new Vector3(9.5f, -3.0f, 0.0f);
        var go_Wall_18_23_rb = go_Wall_18_23.AddComponent<Rigidbody2D>();
        go_Wall_18_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_23_bc = go_Wall_18_23.AddComponent<BoxCollider2D>();
        go_Wall_18_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_23_sr = go_Wall_18_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_23);

        // --- Wall_18_24 ---
        var go_Wall_18_24 = new GameObject("Wall_18_24");
        go_Wall_18_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_24.transform.position = new Vector3(10.5f, -3.0f, 0.0f);
        var go_Wall_18_24_rb = go_Wall_18_24.AddComponent<Rigidbody2D>();
        go_Wall_18_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_24_bc = go_Wall_18_24.AddComponent<BoxCollider2D>();
        go_Wall_18_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_24_sr = go_Wall_18_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_24);

        // --- Wall_18_25 ---
        var go_Wall_18_25 = new GameObject("Wall_18_25");
        go_Wall_18_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_25.transform.position = new Vector3(11.5f, -3.0f, 0.0f);
        var go_Wall_18_25_rb = go_Wall_18_25.AddComponent<Rigidbody2D>();
        go_Wall_18_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_25_bc = go_Wall_18_25.AddComponent<BoxCollider2D>();
        go_Wall_18_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_25_sr = go_Wall_18_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_25);

        // --- Wall_18_26 ---
        var go_Wall_18_26 = new GameObject("Wall_18_26");
        go_Wall_18_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_26.transform.position = new Vector3(12.5f, -3.0f, 0.0f);
        var go_Wall_18_26_rb = go_Wall_18_26.AddComponent<Rigidbody2D>();
        go_Wall_18_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_26_bc = go_Wall_18_26.AddComponent<BoxCollider2D>();
        go_Wall_18_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_26_sr = go_Wall_18_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_26);

        // --- Wall_18_27 ---
        var go_Wall_18_27 = new GameObject("Wall_18_27");
        go_Wall_18_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_18_27.transform.position = new Vector3(13.5f, -3.0f, 0.0f);
        var go_Wall_18_27_rb = go_Wall_18_27.AddComponent<Rigidbody2D>();
        go_Wall_18_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_18_27_bc = go_Wall_18_27.AddComponent<BoxCollider2D>();
        go_Wall_18_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_18_27_sr = go_Wall_18_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_18_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_18_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_18_27);

        // --- Wall_19_0 ---
        var go_Wall_19_0 = new GameObject("Wall_19_0");
        go_Wall_19_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_0.transform.position = new Vector3(-13.5f, -4.0f, 0.0f);
        var go_Wall_19_0_rb = go_Wall_19_0.AddComponent<Rigidbody2D>();
        go_Wall_19_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_0_bc = go_Wall_19_0.AddComponent<BoxCollider2D>();
        go_Wall_19_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_0_sr = go_Wall_19_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_0);

        // --- Wall_19_1 ---
        var go_Wall_19_1 = new GameObject("Wall_19_1");
        go_Wall_19_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_1.transform.position = new Vector3(-12.5f, -4.0f, 0.0f);
        var go_Wall_19_1_rb = go_Wall_19_1.AddComponent<Rigidbody2D>();
        go_Wall_19_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_1_bc = go_Wall_19_1.AddComponent<BoxCollider2D>();
        go_Wall_19_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_1_sr = go_Wall_19_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_1);

        // --- Wall_19_2 ---
        var go_Wall_19_2 = new GameObject("Wall_19_2");
        go_Wall_19_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_2.transform.position = new Vector3(-11.5f, -4.0f, 0.0f);
        var go_Wall_19_2_rb = go_Wall_19_2.AddComponent<Rigidbody2D>();
        go_Wall_19_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_2_bc = go_Wall_19_2.AddComponent<BoxCollider2D>();
        go_Wall_19_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_2_sr = go_Wall_19_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_2);

        // --- Wall_19_3 ---
        var go_Wall_19_3 = new GameObject("Wall_19_3");
        go_Wall_19_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_3.transform.position = new Vector3(-10.5f, -4.0f, 0.0f);
        var go_Wall_19_3_rb = go_Wall_19_3.AddComponent<Rigidbody2D>();
        go_Wall_19_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_3_bc = go_Wall_19_3.AddComponent<BoxCollider2D>();
        go_Wall_19_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_3_sr = go_Wall_19_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_3);

        // --- Wall_19_4 ---
        var go_Wall_19_4 = new GameObject("Wall_19_4");
        go_Wall_19_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_4.transform.position = new Vector3(-9.5f, -4.0f, 0.0f);
        var go_Wall_19_4_rb = go_Wall_19_4.AddComponent<Rigidbody2D>();
        go_Wall_19_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_4_bc = go_Wall_19_4.AddComponent<BoxCollider2D>();
        go_Wall_19_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_4_sr = go_Wall_19_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_4);

        // --- Wall_19_5 ---
        var go_Wall_19_5 = new GameObject("Wall_19_5");
        go_Wall_19_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_5.transform.position = new Vector3(-8.5f, -4.0f, 0.0f);
        var go_Wall_19_5_rb = go_Wall_19_5.AddComponent<Rigidbody2D>();
        go_Wall_19_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_5_bc = go_Wall_19_5.AddComponent<BoxCollider2D>();
        go_Wall_19_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_5_sr = go_Wall_19_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_5);

        // --- Pellet_19_6 ---
        var go_Pellet_19_6 = new GameObject("Pellet_19_6");
        go_Pellet_19_6.tag = "Pellet";
        go_Pellet_19_6.transform.position = new Vector3(-7.5f, -4.0f, 0.0f);
        var go_Pellet_19_6_rb = go_Pellet_19_6.AddComponent<Rigidbody2D>();
        go_Pellet_19_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_19_6_bc = go_Pellet_19_6.AddComponent<BoxCollider2D>();
        go_Pellet_19_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_19_6_bc.isTrigger = true;
        var go_Pellet_19_6_sr = go_Pellet_19_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_19_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_19_6_sr.sharedMaterial = unlitMat;
        go_Pellet_19_6_sr.sortingOrder = 2;
        go_Pellet_19_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_19_6);

        // --- Wall_19_7 ---
        var go_Wall_19_7 = new GameObject("Wall_19_7");
        go_Wall_19_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_7.transform.position = new Vector3(-6.5f, -4.0f, 0.0f);
        var go_Wall_19_7_rb = go_Wall_19_7.AddComponent<Rigidbody2D>();
        go_Wall_19_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_7_bc = go_Wall_19_7.AddComponent<BoxCollider2D>();
        go_Wall_19_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_7_sr = go_Wall_19_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_7);

        // --- Wall_19_8 ---
        var go_Wall_19_8 = new GameObject("Wall_19_8");
        go_Wall_19_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_8.transform.position = new Vector3(-5.5f, -4.0f, 0.0f);
        var go_Wall_19_8_rb = go_Wall_19_8.AddComponent<Rigidbody2D>();
        go_Wall_19_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_8_bc = go_Wall_19_8.AddComponent<BoxCollider2D>();
        go_Wall_19_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_8_sr = go_Wall_19_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_8);

        // --- Wall_19_10 ---
        var go_Wall_19_10 = new GameObject("Wall_19_10");
        go_Wall_19_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_10.transform.position = new Vector3(-3.5f, -4.0f, 0.0f);
        var go_Wall_19_10_rb = go_Wall_19_10.AddComponent<Rigidbody2D>();
        go_Wall_19_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_10_bc = go_Wall_19_10.AddComponent<BoxCollider2D>();
        go_Wall_19_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_10_sr = go_Wall_19_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_10);

        // --- Wall_19_11 ---
        var go_Wall_19_11 = new GameObject("Wall_19_11");
        go_Wall_19_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_11.transform.position = new Vector3(-2.5f, -4.0f, 0.0f);
        var go_Wall_19_11_rb = go_Wall_19_11.AddComponent<Rigidbody2D>();
        go_Wall_19_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_11_bc = go_Wall_19_11.AddComponent<BoxCollider2D>();
        go_Wall_19_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_11_sr = go_Wall_19_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_11);

        // --- Wall_19_12 ---
        var go_Wall_19_12 = new GameObject("Wall_19_12");
        go_Wall_19_12.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_12.transform.position = new Vector3(-1.5f, -4.0f, 0.0f);
        var go_Wall_19_12_rb = go_Wall_19_12.AddComponent<Rigidbody2D>();
        go_Wall_19_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_12_bc = go_Wall_19_12.AddComponent<BoxCollider2D>();
        go_Wall_19_12_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_12_sr = go_Wall_19_12.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_12_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_12_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_12);

        // --- Wall_19_13 ---
        var go_Wall_19_13 = new GameObject("Wall_19_13");
        go_Wall_19_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_13.transform.position = new Vector3(-0.5f, -4.0f, 0.0f);
        var go_Wall_19_13_rb = go_Wall_19_13.AddComponent<Rigidbody2D>();
        go_Wall_19_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_13_bc = go_Wall_19_13.AddComponent<BoxCollider2D>();
        go_Wall_19_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_13_sr = go_Wall_19_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_13);

        // --- Wall_19_14 ---
        var go_Wall_19_14 = new GameObject("Wall_19_14");
        go_Wall_19_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_14.transform.position = new Vector3(0.5f, -4.0f, 0.0f);
        var go_Wall_19_14_rb = go_Wall_19_14.AddComponent<Rigidbody2D>();
        go_Wall_19_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_14_bc = go_Wall_19_14.AddComponent<BoxCollider2D>();
        go_Wall_19_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_14_sr = go_Wall_19_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_14);

        // --- Wall_19_15 ---
        var go_Wall_19_15 = new GameObject("Wall_19_15");
        go_Wall_19_15.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_15.transform.position = new Vector3(1.5f, -4.0f, 0.0f);
        var go_Wall_19_15_rb = go_Wall_19_15.AddComponent<Rigidbody2D>();
        go_Wall_19_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_15_bc = go_Wall_19_15.AddComponent<BoxCollider2D>();
        go_Wall_19_15_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_15_sr = go_Wall_19_15.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_15_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_15_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_15);

        // --- Wall_19_16 ---
        var go_Wall_19_16 = new GameObject("Wall_19_16");
        go_Wall_19_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_16.transform.position = new Vector3(2.5f, -4.0f, 0.0f);
        var go_Wall_19_16_rb = go_Wall_19_16.AddComponent<Rigidbody2D>();
        go_Wall_19_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_16_bc = go_Wall_19_16.AddComponent<BoxCollider2D>();
        go_Wall_19_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_16_sr = go_Wall_19_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_16);

        // --- Wall_19_17 ---
        var go_Wall_19_17 = new GameObject("Wall_19_17");
        go_Wall_19_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_17.transform.position = new Vector3(3.5f, -4.0f, 0.0f);
        var go_Wall_19_17_rb = go_Wall_19_17.AddComponent<Rigidbody2D>();
        go_Wall_19_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_17_bc = go_Wall_19_17.AddComponent<BoxCollider2D>();
        go_Wall_19_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_17_sr = go_Wall_19_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_17);

        // --- Wall_19_19 ---
        var go_Wall_19_19 = new GameObject("Wall_19_19");
        go_Wall_19_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_19.transform.position = new Vector3(5.5f, -4.0f, 0.0f);
        var go_Wall_19_19_rb = go_Wall_19_19.AddComponent<Rigidbody2D>();
        go_Wall_19_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_19_bc = go_Wall_19_19.AddComponent<BoxCollider2D>();
        go_Wall_19_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_19_sr = go_Wall_19_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_19);

        // --- Wall_19_20 ---
        var go_Wall_19_20 = new GameObject("Wall_19_20");
        go_Wall_19_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_20.transform.position = new Vector3(6.5f, -4.0f, 0.0f);
        var go_Wall_19_20_rb = go_Wall_19_20.AddComponent<Rigidbody2D>();
        go_Wall_19_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_20_bc = go_Wall_19_20.AddComponent<BoxCollider2D>();
        go_Wall_19_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_20_sr = go_Wall_19_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_20);

        // --- Pellet_19_21 ---
        var go_Pellet_19_21 = new GameObject("Pellet_19_21");
        go_Pellet_19_21.tag = "Pellet";
        go_Pellet_19_21.transform.position = new Vector3(7.5f, -4.0f, 0.0f);
        var go_Pellet_19_21_rb = go_Pellet_19_21.AddComponent<Rigidbody2D>();
        go_Pellet_19_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_19_21_bc = go_Pellet_19_21.AddComponent<BoxCollider2D>();
        go_Pellet_19_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_19_21_bc.isTrigger = true;
        var go_Pellet_19_21_sr = go_Pellet_19_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_19_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_19_21_sr.sharedMaterial = unlitMat;
        go_Pellet_19_21_sr.sortingOrder = 2;
        go_Pellet_19_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_19_21);

        // --- Wall_19_22 ---
        var go_Wall_19_22 = new GameObject("Wall_19_22");
        go_Wall_19_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_22.transform.position = new Vector3(8.5f, -4.0f, 0.0f);
        var go_Wall_19_22_rb = go_Wall_19_22.AddComponent<Rigidbody2D>();
        go_Wall_19_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_22_bc = go_Wall_19_22.AddComponent<BoxCollider2D>();
        go_Wall_19_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_22_sr = go_Wall_19_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_22);

        // --- Wall_19_23 ---
        var go_Wall_19_23 = new GameObject("Wall_19_23");
        go_Wall_19_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_23.transform.position = new Vector3(9.5f, -4.0f, 0.0f);
        var go_Wall_19_23_rb = go_Wall_19_23.AddComponent<Rigidbody2D>();
        go_Wall_19_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_23_bc = go_Wall_19_23.AddComponent<BoxCollider2D>();
        go_Wall_19_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_23_sr = go_Wall_19_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_23);

        // --- Wall_19_24 ---
        var go_Wall_19_24 = new GameObject("Wall_19_24");
        go_Wall_19_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_24.transform.position = new Vector3(10.5f, -4.0f, 0.0f);
        var go_Wall_19_24_rb = go_Wall_19_24.AddComponent<Rigidbody2D>();
        go_Wall_19_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_24_bc = go_Wall_19_24.AddComponent<BoxCollider2D>();
        go_Wall_19_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_24_sr = go_Wall_19_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_24);

        // --- Wall_19_25 ---
        var go_Wall_19_25 = new GameObject("Wall_19_25");
        go_Wall_19_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_25.transform.position = new Vector3(11.5f, -4.0f, 0.0f);
        var go_Wall_19_25_rb = go_Wall_19_25.AddComponent<Rigidbody2D>();
        go_Wall_19_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_25_bc = go_Wall_19_25.AddComponent<BoxCollider2D>();
        go_Wall_19_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_25_sr = go_Wall_19_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_25);

        // --- Wall_19_26 ---
        var go_Wall_19_26 = new GameObject("Wall_19_26");
        go_Wall_19_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_26.transform.position = new Vector3(12.5f, -4.0f, 0.0f);
        var go_Wall_19_26_rb = go_Wall_19_26.AddComponent<Rigidbody2D>();
        go_Wall_19_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_26_bc = go_Wall_19_26.AddComponent<BoxCollider2D>();
        go_Wall_19_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_26_sr = go_Wall_19_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_26);

        // --- Wall_19_27 ---
        var go_Wall_19_27 = new GameObject("Wall_19_27");
        go_Wall_19_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_19_27.transform.position = new Vector3(13.5f, -4.0f, 0.0f);
        var go_Wall_19_27_rb = go_Wall_19_27.AddComponent<Rigidbody2D>();
        go_Wall_19_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_19_27_bc = go_Wall_19_27.AddComponent<BoxCollider2D>();
        go_Wall_19_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_19_27_sr = go_Wall_19_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_19_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_19_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_19_27);

        // --- Wall_20_0 ---
        var go_Wall_20_0 = new GameObject("Wall_20_0");
        go_Wall_20_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_20_0.transform.position = new Vector3(-13.5f, -5.0f, 0.0f);
        var go_Wall_20_0_rb = go_Wall_20_0.AddComponent<Rigidbody2D>();
        go_Wall_20_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_20_0_bc = go_Wall_20_0.AddComponent<BoxCollider2D>();
        go_Wall_20_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_20_0_sr = go_Wall_20_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_20_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_20_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_20_0);

        // --- Pellet_20_1 ---
        var go_Pellet_20_1 = new GameObject("Pellet_20_1");
        go_Pellet_20_1.tag = "Pellet";
        go_Pellet_20_1.transform.position = new Vector3(-12.5f, -5.0f, 0.0f);
        var go_Pellet_20_1_rb = go_Pellet_20_1.AddComponent<Rigidbody2D>();
        go_Pellet_20_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_1_bc = go_Pellet_20_1.AddComponent<BoxCollider2D>();
        go_Pellet_20_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_1_bc.isTrigger = true;
        var go_Pellet_20_1_sr = go_Pellet_20_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_1_sr.sharedMaterial = unlitMat;
        go_Pellet_20_1_sr.sortingOrder = 2;
        go_Pellet_20_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_1);

        // --- Node_20_1 ---
        var go_Node_20_1 = new GameObject("Node_20_1");
        go_Node_20_1.transform.position = new Vector3(-12.5f, -5.0f, 0.0f);
        var go_Node_20_1_rb = go_Node_20_1.AddComponent<Rigidbody2D>();
        go_Node_20_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_20_1_bc = go_Node_20_1.AddComponent<BoxCollider2D>();
        go_Node_20_1_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_20_1_bc.isTrigger = true;
        go_Node_20_1.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_20_1);

        // --- Pellet_20_2 ---
        var go_Pellet_20_2 = new GameObject("Pellet_20_2");
        go_Pellet_20_2.tag = "Pellet";
        go_Pellet_20_2.transform.position = new Vector3(-11.5f, -5.0f, 0.0f);
        var go_Pellet_20_2_rb = go_Pellet_20_2.AddComponent<Rigidbody2D>();
        go_Pellet_20_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_2_bc = go_Pellet_20_2.AddComponent<BoxCollider2D>();
        go_Pellet_20_2_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_2_bc.isTrigger = true;
        var go_Pellet_20_2_sr = go_Pellet_20_2.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_2_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_2_sr.sharedMaterial = unlitMat;
        go_Pellet_20_2_sr.sortingOrder = 2;
        go_Pellet_20_2.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_2);

        // --- Pellet_20_3 ---
        var go_Pellet_20_3 = new GameObject("Pellet_20_3");
        go_Pellet_20_3.tag = "Pellet";
        go_Pellet_20_3.transform.position = new Vector3(-10.5f, -5.0f, 0.0f);
        var go_Pellet_20_3_rb = go_Pellet_20_3.AddComponent<Rigidbody2D>();
        go_Pellet_20_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_3_bc = go_Pellet_20_3.AddComponent<BoxCollider2D>();
        go_Pellet_20_3_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_3_bc.isTrigger = true;
        var go_Pellet_20_3_sr = go_Pellet_20_3.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_3_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_3_sr.sharedMaterial = unlitMat;
        go_Pellet_20_3_sr.sortingOrder = 2;
        go_Pellet_20_3.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_3);

        // --- Pellet_20_4 ---
        var go_Pellet_20_4 = new GameObject("Pellet_20_4");
        go_Pellet_20_4.tag = "Pellet";
        go_Pellet_20_4.transform.position = new Vector3(-9.5f, -5.0f, 0.0f);
        var go_Pellet_20_4_rb = go_Pellet_20_4.AddComponent<Rigidbody2D>();
        go_Pellet_20_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_4_bc = go_Pellet_20_4.AddComponent<BoxCollider2D>();
        go_Pellet_20_4_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_4_bc.isTrigger = true;
        var go_Pellet_20_4_sr = go_Pellet_20_4.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_4_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_4_sr.sharedMaterial = unlitMat;
        go_Pellet_20_4_sr.sortingOrder = 2;
        go_Pellet_20_4.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_4);

        // --- Pellet_20_5 ---
        var go_Pellet_20_5 = new GameObject("Pellet_20_5");
        go_Pellet_20_5.tag = "Pellet";
        go_Pellet_20_5.transform.position = new Vector3(-8.5f, -5.0f, 0.0f);
        var go_Pellet_20_5_rb = go_Pellet_20_5.AddComponent<Rigidbody2D>();
        go_Pellet_20_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_5_bc = go_Pellet_20_5.AddComponent<BoxCollider2D>();
        go_Pellet_20_5_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_5_bc.isTrigger = true;
        var go_Pellet_20_5_sr = go_Pellet_20_5.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_5_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_5_sr.sharedMaterial = unlitMat;
        go_Pellet_20_5_sr.sortingOrder = 2;
        go_Pellet_20_5.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_5);

        // --- Pellet_20_6 ---
        var go_Pellet_20_6 = new GameObject("Pellet_20_6");
        go_Pellet_20_6.tag = "Pellet";
        go_Pellet_20_6.transform.position = new Vector3(-7.5f, -5.0f, 0.0f);
        var go_Pellet_20_6_rb = go_Pellet_20_6.AddComponent<Rigidbody2D>();
        go_Pellet_20_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_6_bc = go_Pellet_20_6.AddComponent<BoxCollider2D>();
        go_Pellet_20_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_6_bc.isTrigger = true;
        var go_Pellet_20_6_sr = go_Pellet_20_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_6_sr.sharedMaterial = unlitMat;
        go_Pellet_20_6_sr.sortingOrder = 2;
        go_Pellet_20_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_6);

        // --- Node_20_6 ---
        var go_Node_20_6 = new GameObject("Node_20_6");
        go_Node_20_6.transform.position = new Vector3(-7.5f, -5.0f, 0.0f);
        var go_Node_20_6_rb = go_Node_20_6.AddComponent<Rigidbody2D>();
        go_Node_20_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_20_6_bc = go_Node_20_6.AddComponent<BoxCollider2D>();
        go_Node_20_6_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_20_6_bc.isTrigger = true;
        go_Node_20_6.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_20_6);

        // --- Pellet_20_7 ---
        var go_Pellet_20_7 = new GameObject("Pellet_20_7");
        go_Pellet_20_7.tag = "Pellet";
        go_Pellet_20_7.transform.position = new Vector3(-6.5f, -5.0f, 0.0f);
        var go_Pellet_20_7_rb = go_Pellet_20_7.AddComponent<Rigidbody2D>();
        go_Pellet_20_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_7_bc = go_Pellet_20_7.AddComponent<BoxCollider2D>();
        go_Pellet_20_7_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_7_bc.isTrigger = true;
        var go_Pellet_20_7_sr = go_Pellet_20_7.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_7_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_7_sr.sharedMaterial = unlitMat;
        go_Pellet_20_7_sr.sortingOrder = 2;
        go_Pellet_20_7.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_7);

        // --- Pellet_20_8 ---
        var go_Pellet_20_8 = new GameObject("Pellet_20_8");
        go_Pellet_20_8.tag = "Pellet";
        go_Pellet_20_8.transform.position = new Vector3(-5.5f, -5.0f, 0.0f);
        var go_Pellet_20_8_rb = go_Pellet_20_8.AddComponent<Rigidbody2D>();
        go_Pellet_20_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_8_bc = go_Pellet_20_8.AddComponent<BoxCollider2D>();
        go_Pellet_20_8_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_8_bc.isTrigger = true;
        var go_Pellet_20_8_sr = go_Pellet_20_8.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_8_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_8_sr.sharedMaterial = unlitMat;
        go_Pellet_20_8_sr.sortingOrder = 2;
        go_Pellet_20_8.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_8);

        // --- Pellet_20_9 ---
        var go_Pellet_20_9 = new GameObject("Pellet_20_9");
        go_Pellet_20_9.tag = "Pellet";
        go_Pellet_20_9.transform.position = new Vector3(-4.5f, -5.0f, 0.0f);
        var go_Pellet_20_9_rb = go_Pellet_20_9.AddComponent<Rigidbody2D>();
        go_Pellet_20_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_9_bc = go_Pellet_20_9.AddComponent<BoxCollider2D>();
        go_Pellet_20_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_9_bc.isTrigger = true;
        var go_Pellet_20_9_sr = go_Pellet_20_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_9_sr.sharedMaterial = unlitMat;
        go_Pellet_20_9_sr.sortingOrder = 2;
        go_Pellet_20_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_9);

        // --- Node_20_9 ---
        var go_Node_20_9 = new GameObject("Node_20_9");
        go_Node_20_9.transform.position = new Vector3(-4.5f, -5.0f, 0.0f);
        var go_Node_20_9_rb = go_Node_20_9.AddComponent<Rigidbody2D>();
        go_Node_20_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_20_9_bc = go_Node_20_9.AddComponent<BoxCollider2D>();
        go_Node_20_9_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_20_9_bc.isTrigger = true;
        go_Node_20_9.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_20_9);

        // --- Pellet_20_10 ---
        var go_Pellet_20_10 = new GameObject("Pellet_20_10");
        go_Pellet_20_10.tag = "Pellet";
        go_Pellet_20_10.transform.position = new Vector3(-3.5f, -5.0f, 0.0f);
        var go_Pellet_20_10_rb = go_Pellet_20_10.AddComponent<Rigidbody2D>();
        go_Pellet_20_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_10_bc = go_Pellet_20_10.AddComponent<BoxCollider2D>();
        go_Pellet_20_10_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_10_bc.isTrigger = true;
        var go_Pellet_20_10_sr = go_Pellet_20_10.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_10_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_10_sr.sharedMaterial = unlitMat;
        go_Pellet_20_10_sr.sortingOrder = 2;
        go_Pellet_20_10.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_10);

        // --- Pellet_20_11 ---
        var go_Pellet_20_11 = new GameObject("Pellet_20_11");
        go_Pellet_20_11.tag = "Pellet";
        go_Pellet_20_11.transform.position = new Vector3(-2.5f, -5.0f, 0.0f);
        var go_Pellet_20_11_rb = go_Pellet_20_11.AddComponent<Rigidbody2D>();
        go_Pellet_20_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_11_bc = go_Pellet_20_11.AddComponent<BoxCollider2D>();
        go_Pellet_20_11_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_11_bc.isTrigger = true;
        var go_Pellet_20_11_sr = go_Pellet_20_11.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_11_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_11_sr.sharedMaterial = unlitMat;
        go_Pellet_20_11_sr.sortingOrder = 2;
        go_Pellet_20_11.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_11);

        // --- Pellet_20_12 ---
        var go_Pellet_20_12 = new GameObject("Pellet_20_12");
        go_Pellet_20_12.tag = "Pellet";
        go_Pellet_20_12.transform.position = new Vector3(-1.5f, -5.0f, 0.0f);
        var go_Pellet_20_12_rb = go_Pellet_20_12.AddComponent<Rigidbody2D>();
        go_Pellet_20_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_12_bc = go_Pellet_20_12.AddComponent<BoxCollider2D>();
        go_Pellet_20_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_12_bc.isTrigger = true;
        var go_Pellet_20_12_sr = go_Pellet_20_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_12_sr.sharedMaterial = unlitMat;
        go_Pellet_20_12_sr.sortingOrder = 2;
        go_Pellet_20_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_12);

        // --- Node_20_12 ---
        var go_Node_20_12 = new GameObject("Node_20_12");
        go_Node_20_12.transform.position = new Vector3(-1.5f, -5.0f, 0.0f);
        var go_Node_20_12_rb = go_Node_20_12.AddComponent<Rigidbody2D>();
        go_Node_20_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_20_12_bc = go_Node_20_12.AddComponent<BoxCollider2D>();
        go_Node_20_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_20_12_bc.isTrigger = true;
        go_Node_20_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_20_12);

        // --- Wall_20_13 ---
        var go_Wall_20_13 = new GameObject("Wall_20_13");
        go_Wall_20_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_20_13.transform.position = new Vector3(-0.5f, -5.0f, 0.0f);
        var go_Wall_20_13_rb = go_Wall_20_13.AddComponent<Rigidbody2D>();
        go_Wall_20_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_20_13_bc = go_Wall_20_13.AddComponent<BoxCollider2D>();
        go_Wall_20_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_20_13_sr = go_Wall_20_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_20_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_20_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_20_13);

        // --- Wall_20_14 ---
        var go_Wall_20_14 = new GameObject("Wall_20_14");
        go_Wall_20_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_20_14.transform.position = new Vector3(0.5f, -5.0f, 0.0f);
        var go_Wall_20_14_rb = go_Wall_20_14.AddComponent<Rigidbody2D>();
        go_Wall_20_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_20_14_bc = go_Wall_20_14.AddComponent<BoxCollider2D>();
        go_Wall_20_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_20_14_sr = go_Wall_20_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_20_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_20_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_20_14);

        // --- Pellet_20_15 ---
        var go_Pellet_20_15 = new GameObject("Pellet_20_15");
        go_Pellet_20_15.tag = "Pellet";
        go_Pellet_20_15.transform.position = new Vector3(1.5f, -5.0f, 0.0f);
        var go_Pellet_20_15_rb = go_Pellet_20_15.AddComponent<Rigidbody2D>();
        go_Pellet_20_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_15_bc = go_Pellet_20_15.AddComponent<BoxCollider2D>();
        go_Pellet_20_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_15_bc.isTrigger = true;
        var go_Pellet_20_15_sr = go_Pellet_20_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_15_sr.sharedMaterial = unlitMat;
        go_Pellet_20_15_sr.sortingOrder = 2;
        go_Pellet_20_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_15);

        // --- Node_20_15 ---
        var go_Node_20_15 = new GameObject("Node_20_15");
        go_Node_20_15.transform.position = new Vector3(1.5f, -5.0f, 0.0f);
        var go_Node_20_15_rb = go_Node_20_15.AddComponent<Rigidbody2D>();
        go_Node_20_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_20_15_bc = go_Node_20_15.AddComponent<BoxCollider2D>();
        go_Node_20_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_20_15_bc.isTrigger = true;
        go_Node_20_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_20_15);

        // --- Pellet_20_16 ---
        var go_Pellet_20_16 = new GameObject("Pellet_20_16");
        go_Pellet_20_16.tag = "Pellet";
        go_Pellet_20_16.transform.position = new Vector3(2.5f, -5.0f, 0.0f);
        var go_Pellet_20_16_rb = go_Pellet_20_16.AddComponent<Rigidbody2D>();
        go_Pellet_20_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_16_bc = go_Pellet_20_16.AddComponent<BoxCollider2D>();
        go_Pellet_20_16_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_16_bc.isTrigger = true;
        var go_Pellet_20_16_sr = go_Pellet_20_16.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_16_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_16_sr.sharedMaterial = unlitMat;
        go_Pellet_20_16_sr.sortingOrder = 2;
        go_Pellet_20_16.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_16);

        // --- Pellet_20_17 ---
        var go_Pellet_20_17 = new GameObject("Pellet_20_17");
        go_Pellet_20_17.tag = "Pellet";
        go_Pellet_20_17.transform.position = new Vector3(3.5f, -5.0f, 0.0f);
        var go_Pellet_20_17_rb = go_Pellet_20_17.AddComponent<Rigidbody2D>();
        go_Pellet_20_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_17_bc = go_Pellet_20_17.AddComponent<BoxCollider2D>();
        go_Pellet_20_17_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_17_bc.isTrigger = true;
        var go_Pellet_20_17_sr = go_Pellet_20_17.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_17_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_17_sr.sharedMaterial = unlitMat;
        go_Pellet_20_17_sr.sortingOrder = 2;
        go_Pellet_20_17.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_17);

        // --- Pellet_20_18 ---
        var go_Pellet_20_18 = new GameObject("Pellet_20_18");
        go_Pellet_20_18.tag = "Pellet";
        go_Pellet_20_18.transform.position = new Vector3(4.5f, -5.0f, 0.0f);
        var go_Pellet_20_18_rb = go_Pellet_20_18.AddComponent<Rigidbody2D>();
        go_Pellet_20_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_18_bc = go_Pellet_20_18.AddComponent<BoxCollider2D>();
        go_Pellet_20_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_18_bc.isTrigger = true;
        var go_Pellet_20_18_sr = go_Pellet_20_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_18_sr.sharedMaterial = unlitMat;
        go_Pellet_20_18_sr.sortingOrder = 2;
        go_Pellet_20_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_18);

        // --- Node_20_18 ---
        var go_Node_20_18 = new GameObject("Node_20_18");
        go_Node_20_18.transform.position = new Vector3(4.5f, -5.0f, 0.0f);
        var go_Node_20_18_rb = go_Node_20_18.AddComponent<Rigidbody2D>();
        go_Node_20_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_20_18_bc = go_Node_20_18.AddComponent<BoxCollider2D>();
        go_Node_20_18_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_20_18_bc.isTrigger = true;
        go_Node_20_18.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_20_18);

        // --- Pellet_20_19 ---
        var go_Pellet_20_19 = new GameObject("Pellet_20_19");
        go_Pellet_20_19.tag = "Pellet";
        go_Pellet_20_19.transform.position = new Vector3(5.5f, -5.0f, 0.0f);
        var go_Pellet_20_19_rb = go_Pellet_20_19.AddComponent<Rigidbody2D>();
        go_Pellet_20_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_19_bc = go_Pellet_20_19.AddComponent<BoxCollider2D>();
        go_Pellet_20_19_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_19_bc.isTrigger = true;
        var go_Pellet_20_19_sr = go_Pellet_20_19.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_19_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_19_sr.sharedMaterial = unlitMat;
        go_Pellet_20_19_sr.sortingOrder = 2;
        go_Pellet_20_19.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_19);

        // --- Pellet_20_20 ---
        var go_Pellet_20_20 = new GameObject("Pellet_20_20");
        go_Pellet_20_20.tag = "Pellet";
        go_Pellet_20_20.transform.position = new Vector3(6.5f, -5.0f, 0.0f);
        var go_Pellet_20_20_rb = go_Pellet_20_20.AddComponent<Rigidbody2D>();
        go_Pellet_20_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_20_bc = go_Pellet_20_20.AddComponent<BoxCollider2D>();
        go_Pellet_20_20_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_20_bc.isTrigger = true;
        var go_Pellet_20_20_sr = go_Pellet_20_20.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_20_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_20_sr.sharedMaterial = unlitMat;
        go_Pellet_20_20_sr.sortingOrder = 2;
        go_Pellet_20_20.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_20);

        // --- Pellet_20_21 ---
        var go_Pellet_20_21 = new GameObject("Pellet_20_21");
        go_Pellet_20_21.tag = "Pellet";
        go_Pellet_20_21.transform.position = new Vector3(7.5f, -5.0f, 0.0f);
        var go_Pellet_20_21_rb = go_Pellet_20_21.AddComponent<Rigidbody2D>();
        go_Pellet_20_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_21_bc = go_Pellet_20_21.AddComponent<BoxCollider2D>();
        go_Pellet_20_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_21_bc.isTrigger = true;
        var go_Pellet_20_21_sr = go_Pellet_20_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_21_sr.sharedMaterial = unlitMat;
        go_Pellet_20_21_sr.sortingOrder = 2;
        go_Pellet_20_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_21);

        // --- Node_20_21 ---
        var go_Node_20_21 = new GameObject("Node_20_21");
        go_Node_20_21.transform.position = new Vector3(7.5f, -5.0f, 0.0f);
        var go_Node_20_21_rb = go_Node_20_21.AddComponent<Rigidbody2D>();
        go_Node_20_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_20_21_bc = go_Node_20_21.AddComponent<BoxCollider2D>();
        go_Node_20_21_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_20_21_bc.isTrigger = true;
        go_Node_20_21.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_20_21);

        // --- Pellet_20_22 ---
        var go_Pellet_20_22 = new GameObject("Pellet_20_22");
        go_Pellet_20_22.tag = "Pellet";
        go_Pellet_20_22.transform.position = new Vector3(8.5f, -5.0f, 0.0f);
        var go_Pellet_20_22_rb = go_Pellet_20_22.AddComponent<Rigidbody2D>();
        go_Pellet_20_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_22_bc = go_Pellet_20_22.AddComponent<BoxCollider2D>();
        go_Pellet_20_22_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_22_bc.isTrigger = true;
        var go_Pellet_20_22_sr = go_Pellet_20_22.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_22_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_22_sr.sharedMaterial = unlitMat;
        go_Pellet_20_22_sr.sortingOrder = 2;
        go_Pellet_20_22.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_22);

        // --- Pellet_20_23 ---
        var go_Pellet_20_23 = new GameObject("Pellet_20_23");
        go_Pellet_20_23.tag = "Pellet";
        go_Pellet_20_23.transform.position = new Vector3(9.5f, -5.0f, 0.0f);
        var go_Pellet_20_23_rb = go_Pellet_20_23.AddComponent<Rigidbody2D>();
        go_Pellet_20_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_23_bc = go_Pellet_20_23.AddComponent<BoxCollider2D>();
        go_Pellet_20_23_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_23_bc.isTrigger = true;
        var go_Pellet_20_23_sr = go_Pellet_20_23.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_23_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_23_sr.sharedMaterial = unlitMat;
        go_Pellet_20_23_sr.sortingOrder = 2;
        go_Pellet_20_23.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_23);

        // --- Pellet_20_24 ---
        var go_Pellet_20_24 = new GameObject("Pellet_20_24");
        go_Pellet_20_24.tag = "Pellet";
        go_Pellet_20_24.transform.position = new Vector3(10.5f, -5.0f, 0.0f);
        var go_Pellet_20_24_rb = go_Pellet_20_24.AddComponent<Rigidbody2D>();
        go_Pellet_20_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_24_bc = go_Pellet_20_24.AddComponent<BoxCollider2D>();
        go_Pellet_20_24_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_24_bc.isTrigger = true;
        var go_Pellet_20_24_sr = go_Pellet_20_24.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_24_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_24_sr.sharedMaterial = unlitMat;
        go_Pellet_20_24_sr.sortingOrder = 2;
        go_Pellet_20_24.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_24);

        // --- Pellet_20_25 ---
        var go_Pellet_20_25 = new GameObject("Pellet_20_25");
        go_Pellet_20_25.tag = "Pellet";
        go_Pellet_20_25.transform.position = new Vector3(11.5f, -5.0f, 0.0f);
        var go_Pellet_20_25_rb = go_Pellet_20_25.AddComponent<Rigidbody2D>();
        go_Pellet_20_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_25_bc = go_Pellet_20_25.AddComponent<BoxCollider2D>();
        go_Pellet_20_25_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_25_bc.isTrigger = true;
        var go_Pellet_20_25_sr = go_Pellet_20_25.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_25_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_25_sr.sharedMaterial = unlitMat;
        go_Pellet_20_25_sr.sortingOrder = 2;
        go_Pellet_20_25.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_25);

        // --- Pellet_20_26 ---
        var go_Pellet_20_26 = new GameObject("Pellet_20_26");
        go_Pellet_20_26.tag = "Pellet";
        go_Pellet_20_26.transform.position = new Vector3(12.5f, -5.0f, 0.0f);
        var go_Pellet_20_26_rb = go_Pellet_20_26.AddComponent<Rigidbody2D>();
        go_Pellet_20_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_20_26_bc = go_Pellet_20_26.AddComponent<BoxCollider2D>();
        go_Pellet_20_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_20_26_bc.isTrigger = true;
        var go_Pellet_20_26_sr = go_Pellet_20_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_20_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_20_26_sr.sharedMaterial = unlitMat;
        go_Pellet_20_26_sr.sortingOrder = 2;
        go_Pellet_20_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_20_26);

        // --- Node_20_26 ---
        var go_Node_20_26 = new GameObject("Node_20_26");
        go_Node_20_26.transform.position = new Vector3(12.5f, -5.0f, 0.0f);
        var go_Node_20_26_rb = go_Node_20_26.AddComponent<Rigidbody2D>();
        go_Node_20_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_20_26_bc = go_Node_20_26.AddComponent<BoxCollider2D>();
        go_Node_20_26_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_20_26_bc.isTrigger = true;
        go_Node_20_26.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_20_26);

        // --- Wall_20_27 ---
        var go_Wall_20_27 = new GameObject("Wall_20_27");
        go_Wall_20_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_20_27.transform.position = new Vector3(13.5f, -5.0f, 0.0f);
        var go_Wall_20_27_rb = go_Wall_20_27.AddComponent<Rigidbody2D>();
        go_Wall_20_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_20_27_bc = go_Wall_20_27.AddComponent<BoxCollider2D>();
        go_Wall_20_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_20_27_sr = go_Wall_20_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_20_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_20_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_20_27);

        // --- Wall_21_0 ---
        var go_Wall_21_0 = new GameObject("Wall_21_0");
        go_Wall_21_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_0.transform.position = new Vector3(-13.5f, -6.0f, 0.0f);
        var go_Wall_21_0_rb = go_Wall_21_0.AddComponent<Rigidbody2D>();
        go_Wall_21_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_0_bc = go_Wall_21_0.AddComponent<BoxCollider2D>();
        go_Wall_21_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_0_sr = go_Wall_21_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_0);

        // --- Pellet_21_1 ---
        var go_Pellet_21_1 = new GameObject("Pellet_21_1");
        go_Pellet_21_1.tag = "Pellet";
        go_Pellet_21_1.transform.position = new Vector3(-12.5f, -6.0f, 0.0f);
        var go_Pellet_21_1_rb = go_Pellet_21_1.AddComponent<Rigidbody2D>();
        go_Pellet_21_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_21_1_bc = go_Pellet_21_1.AddComponent<BoxCollider2D>();
        go_Pellet_21_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_21_1_bc.isTrigger = true;
        var go_Pellet_21_1_sr = go_Pellet_21_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_21_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_21_1_sr.sharedMaterial = unlitMat;
        go_Pellet_21_1_sr.sortingOrder = 2;
        go_Pellet_21_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_21_1);

        // --- Wall_21_2 ---
        var go_Wall_21_2 = new GameObject("Wall_21_2");
        go_Wall_21_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_2.transform.position = new Vector3(-11.5f, -6.0f, 0.0f);
        var go_Wall_21_2_rb = go_Wall_21_2.AddComponent<Rigidbody2D>();
        go_Wall_21_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_2_bc = go_Wall_21_2.AddComponent<BoxCollider2D>();
        go_Wall_21_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_2_sr = go_Wall_21_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_2);

        // --- Wall_21_3 ---
        var go_Wall_21_3 = new GameObject("Wall_21_3");
        go_Wall_21_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_3.transform.position = new Vector3(-10.5f, -6.0f, 0.0f);
        var go_Wall_21_3_rb = go_Wall_21_3.AddComponent<Rigidbody2D>();
        go_Wall_21_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_3_bc = go_Wall_21_3.AddComponent<BoxCollider2D>();
        go_Wall_21_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_3_sr = go_Wall_21_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_3);

        // --- Wall_21_4 ---
        var go_Wall_21_4 = new GameObject("Wall_21_4");
        go_Wall_21_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_4.transform.position = new Vector3(-9.5f, -6.0f, 0.0f);
        var go_Wall_21_4_rb = go_Wall_21_4.AddComponent<Rigidbody2D>();
        go_Wall_21_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_4_bc = go_Wall_21_4.AddComponent<BoxCollider2D>();
        go_Wall_21_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_4_sr = go_Wall_21_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_4);

        // --- Wall_21_5 ---
        var go_Wall_21_5 = new GameObject("Wall_21_5");
        go_Wall_21_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_5.transform.position = new Vector3(-8.5f, -6.0f, 0.0f);
        var go_Wall_21_5_rb = go_Wall_21_5.AddComponent<Rigidbody2D>();
        go_Wall_21_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_5_bc = go_Wall_21_5.AddComponent<BoxCollider2D>();
        go_Wall_21_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_5_sr = go_Wall_21_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_5);

        // --- Pellet_21_6 ---
        var go_Pellet_21_6 = new GameObject("Pellet_21_6");
        go_Pellet_21_6.tag = "Pellet";
        go_Pellet_21_6.transform.position = new Vector3(-7.5f, -6.0f, 0.0f);
        var go_Pellet_21_6_rb = go_Pellet_21_6.AddComponent<Rigidbody2D>();
        go_Pellet_21_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_21_6_bc = go_Pellet_21_6.AddComponent<BoxCollider2D>();
        go_Pellet_21_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_21_6_bc.isTrigger = true;
        var go_Pellet_21_6_sr = go_Pellet_21_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_21_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_21_6_sr.sharedMaterial = unlitMat;
        go_Pellet_21_6_sr.sortingOrder = 2;
        go_Pellet_21_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_21_6);

        // --- Wall_21_7 ---
        var go_Wall_21_7 = new GameObject("Wall_21_7");
        go_Wall_21_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_7.transform.position = new Vector3(-6.5f, -6.0f, 0.0f);
        var go_Wall_21_7_rb = go_Wall_21_7.AddComponent<Rigidbody2D>();
        go_Wall_21_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_7_bc = go_Wall_21_7.AddComponent<BoxCollider2D>();
        go_Wall_21_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_7_sr = go_Wall_21_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_7);

        // --- Wall_21_8 ---
        var go_Wall_21_8 = new GameObject("Wall_21_8");
        go_Wall_21_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_8.transform.position = new Vector3(-5.5f, -6.0f, 0.0f);
        var go_Wall_21_8_rb = go_Wall_21_8.AddComponent<Rigidbody2D>();
        go_Wall_21_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_8_bc = go_Wall_21_8.AddComponent<BoxCollider2D>();
        go_Wall_21_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_8_sr = go_Wall_21_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_8);

        // --- Wall_21_9 ---
        var go_Wall_21_9 = new GameObject("Wall_21_9");
        go_Wall_21_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_9.transform.position = new Vector3(-4.5f, -6.0f, 0.0f);
        var go_Wall_21_9_rb = go_Wall_21_9.AddComponent<Rigidbody2D>();
        go_Wall_21_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_9_bc = go_Wall_21_9.AddComponent<BoxCollider2D>();
        go_Wall_21_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_9_sr = go_Wall_21_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_9);

        // --- Wall_21_10 ---
        var go_Wall_21_10 = new GameObject("Wall_21_10");
        go_Wall_21_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_10.transform.position = new Vector3(-3.5f, -6.0f, 0.0f);
        var go_Wall_21_10_rb = go_Wall_21_10.AddComponent<Rigidbody2D>();
        go_Wall_21_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_10_bc = go_Wall_21_10.AddComponent<BoxCollider2D>();
        go_Wall_21_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_10_sr = go_Wall_21_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_10);

        // --- Wall_21_11 ---
        var go_Wall_21_11 = new GameObject("Wall_21_11");
        go_Wall_21_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_11.transform.position = new Vector3(-2.5f, -6.0f, 0.0f);
        var go_Wall_21_11_rb = go_Wall_21_11.AddComponent<Rigidbody2D>();
        go_Wall_21_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_11_bc = go_Wall_21_11.AddComponent<BoxCollider2D>();
        go_Wall_21_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_11_sr = go_Wall_21_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_11);

        // --- Pellet_21_12 ---
        var go_Pellet_21_12 = new GameObject("Pellet_21_12");
        go_Pellet_21_12.tag = "Pellet";
        go_Pellet_21_12.transform.position = new Vector3(-1.5f, -6.0f, 0.0f);
        var go_Pellet_21_12_rb = go_Pellet_21_12.AddComponent<Rigidbody2D>();
        go_Pellet_21_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_21_12_bc = go_Pellet_21_12.AddComponent<BoxCollider2D>();
        go_Pellet_21_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_21_12_bc.isTrigger = true;
        var go_Pellet_21_12_sr = go_Pellet_21_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_21_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_21_12_sr.sharedMaterial = unlitMat;
        go_Pellet_21_12_sr.sortingOrder = 2;
        go_Pellet_21_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_21_12);

        // --- Wall_21_13 ---
        var go_Wall_21_13 = new GameObject("Wall_21_13");
        go_Wall_21_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_13.transform.position = new Vector3(-0.5f, -6.0f, 0.0f);
        var go_Wall_21_13_rb = go_Wall_21_13.AddComponent<Rigidbody2D>();
        go_Wall_21_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_13_bc = go_Wall_21_13.AddComponent<BoxCollider2D>();
        go_Wall_21_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_13_sr = go_Wall_21_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_13);

        // --- Wall_21_14 ---
        var go_Wall_21_14 = new GameObject("Wall_21_14");
        go_Wall_21_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_14.transform.position = new Vector3(0.5f, -6.0f, 0.0f);
        var go_Wall_21_14_rb = go_Wall_21_14.AddComponent<Rigidbody2D>();
        go_Wall_21_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_14_bc = go_Wall_21_14.AddComponent<BoxCollider2D>();
        go_Wall_21_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_14_sr = go_Wall_21_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_14);

        // --- Pellet_21_15 ---
        var go_Pellet_21_15 = new GameObject("Pellet_21_15");
        go_Pellet_21_15.tag = "Pellet";
        go_Pellet_21_15.transform.position = new Vector3(1.5f, -6.0f, 0.0f);
        var go_Pellet_21_15_rb = go_Pellet_21_15.AddComponent<Rigidbody2D>();
        go_Pellet_21_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_21_15_bc = go_Pellet_21_15.AddComponent<BoxCollider2D>();
        go_Pellet_21_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_21_15_bc.isTrigger = true;
        var go_Pellet_21_15_sr = go_Pellet_21_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_21_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_21_15_sr.sharedMaterial = unlitMat;
        go_Pellet_21_15_sr.sortingOrder = 2;
        go_Pellet_21_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_21_15);

        // --- Wall_21_16 ---
        var go_Wall_21_16 = new GameObject("Wall_21_16");
        go_Wall_21_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_16.transform.position = new Vector3(2.5f, -6.0f, 0.0f);
        var go_Wall_21_16_rb = go_Wall_21_16.AddComponent<Rigidbody2D>();
        go_Wall_21_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_16_bc = go_Wall_21_16.AddComponent<BoxCollider2D>();
        go_Wall_21_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_16_sr = go_Wall_21_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_16);

        // --- Wall_21_17 ---
        var go_Wall_21_17 = new GameObject("Wall_21_17");
        go_Wall_21_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_17.transform.position = new Vector3(3.5f, -6.0f, 0.0f);
        var go_Wall_21_17_rb = go_Wall_21_17.AddComponent<Rigidbody2D>();
        go_Wall_21_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_17_bc = go_Wall_21_17.AddComponent<BoxCollider2D>();
        go_Wall_21_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_17_sr = go_Wall_21_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_17);

        // --- Wall_21_18 ---
        var go_Wall_21_18 = new GameObject("Wall_21_18");
        go_Wall_21_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_18.transform.position = new Vector3(4.5f, -6.0f, 0.0f);
        var go_Wall_21_18_rb = go_Wall_21_18.AddComponent<Rigidbody2D>();
        go_Wall_21_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_18_bc = go_Wall_21_18.AddComponent<BoxCollider2D>();
        go_Wall_21_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_18_sr = go_Wall_21_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_18);

        // --- Wall_21_19 ---
        var go_Wall_21_19 = new GameObject("Wall_21_19");
        go_Wall_21_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_19.transform.position = new Vector3(5.5f, -6.0f, 0.0f);
        var go_Wall_21_19_rb = go_Wall_21_19.AddComponent<Rigidbody2D>();
        go_Wall_21_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_19_bc = go_Wall_21_19.AddComponent<BoxCollider2D>();
        go_Wall_21_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_19_sr = go_Wall_21_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_19);

        // --- Wall_21_20 ---
        var go_Wall_21_20 = new GameObject("Wall_21_20");
        go_Wall_21_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_20.transform.position = new Vector3(6.5f, -6.0f, 0.0f);
        var go_Wall_21_20_rb = go_Wall_21_20.AddComponent<Rigidbody2D>();
        go_Wall_21_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_20_bc = go_Wall_21_20.AddComponent<BoxCollider2D>();
        go_Wall_21_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_20_sr = go_Wall_21_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_20);

        // --- Pellet_21_21 ---
        var go_Pellet_21_21 = new GameObject("Pellet_21_21");
        go_Pellet_21_21.tag = "Pellet";
        go_Pellet_21_21.transform.position = new Vector3(7.5f, -6.0f, 0.0f);
        var go_Pellet_21_21_rb = go_Pellet_21_21.AddComponent<Rigidbody2D>();
        go_Pellet_21_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_21_21_bc = go_Pellet_21_21.AddComponent<BoxCollider2D>();
        go_Pellet_21_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_21_21_bc.isTrigger = true;
        var go_Pellet_21_21_sr = go_Pellet_21_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_21_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_21_21_sr.sharedMaterial = unlitMat;
        go_Pellet_21_21_sr.sortingOrder = 2;
        go_Pellet_21_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_21_21);

        // --- Wall_21_22 ---
        var go_Wall_21_22 = new GameObject("Wall_21_22");
        go_Wall_21_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_22.transform.position = new Vector3(8.5f, -6.0f, 0.0f);
        var go_Wall_21_22_rb = go_Wall_21_22.AddComponent<Rigidbody2D>();
        go_Wall_21_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_22_bc = go_Wall_21_22.AddComponent<BoxCollider2D>();
        go_Wall_21_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_22_sr = go_Wall_21_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_22);

        // --- Wall_21_23 ---
        var go_Wall_21_23 = new GameObject("Wall_21_23");
        go_Wall_21_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_23.transform.position = new Vector3(9.5f, -6.0f, 0.0f);
        var go_Wall_21_23_rb = go_Wall_21_23.AddComponent<Rigidbody2D>();
        go_Wall_21_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_23_bc = go_Wall_21_23.AddComponent<BoxCollider2D>();
        go_Wall_21_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_23_sr = go_Wall_21_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_23);

        // --- Wall_21_24 ---
        var go_Wall_21_24 = new GameObject("Wall_21_24");
        go_Wall_21_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_24.transform.position = new Vector3(10.5f, -6.0f, 0.0f);
        var go_Wall_21_24_rb = go_Wall_21_24.AddComponent<Rigidbody2D>();
        go_Wall_21_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_24_bc = go_Wall_21_24.AddComponent<BoxCollider2D>();
        go_Wall_21_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_24_sr = go_Wall_21_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_24);

        // --- Wall_21_25 ---
        var go_Wall_21_25 = new GameObject("Wall_21_25");
        go_Wall_21_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_25.transform.position = new Vector3(11.5f, -6.0f, 0.0f);
        var go_Wall_21_25_rb = go_Wall_21_25.AddComponent<Rigidbody2D>();
        go_Wall_21_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_25_bc = go_Wall_21_25.AddComponent<BoxCollider2D>();
        go_Wall_21_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_25_sr = go_Wall_21_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_25);

        // --- Pellet_21_26 ---
        var go_Pellet_21_26 = new GameObject("Pellet_21_26");
        go_Pellet_21_26.tag = "Pellet";
        go_Pellet_21_26.transform.position = new Vector3(12.5f, -6.0f, 0.0f);
        var go_Pellet_21_26_rb = go_Pellet_21_26.AddComponent<Rigidbody2D>();
        go_Pellet_21_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_21_26_bc = go_Pellet_21_26.AddComponent<BoxCollider2D>();
        go_Pellet_21_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_21_26_bc.isTrigger = true;
        var go_Pellet_21_26_sr = go_Pellet_21_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_21_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_21_26_sr.sharedMaterial = unlitMat;
        go_Pellet_21_26_sr.sortingOrder = 2;
        go_Pellet_21_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_21_26);

        // --- Wall_21_27 ---
        var go_Wall_21_27 = new GameObject("Wall_21_27");
        go_Wall_21_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_21_27.transform.position = new Vector3(13.5f, -6.0f, 0.0f);
        var go_Wall_21_27_rb = go_Wall_21_27.AddComponent<Rigidbody2D>();
        go_Wall_21_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_21_27_bc = go_Wall_21_27.AddComponent<BoxCollider2D>();
        go_Wall_21_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_21_27_sr = go_Wall_21_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_21_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_21_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_21_27);

        // --- Wall_22_0 ---
        var go_Wall_22_0 = new GameObject("Wall_22_0");
        go_Wall_22_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_0.transform.position = new Vector3(-13.5f, -7.0f, 0.0f);
        var go_Wall_22_0_rb = go_Wall_22_0.AddComponent<Rigidbody2D>();
        go_Wall_22_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_0_bc = go_Wall_22_0.AddComponent<BoxCollider2D>();
        go_Wall_22_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_0_sr = go_Wall_22_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_0);

        // --- Pellet_22_1 ---
        var go_Pellet_22_1 = new GameObject("Pellet_22_1");
        go_Pellet_22_1.tag = "Pellet";
        go_Pellet_22_1.transform.position = new Vector3(-12.5f, -7.0f, 0.0f);
        var go_Pellet_22_1_rb = go_Pellet_22_1.AddComponent<Rigidbody2D>();
        go_Pellet_22_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_22_1_bc = go_Pellet_22_1.AddComponent<BoxCollider2D>();
        go_Pellet_22_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_22_1_bc.isTrigger = true;
        var go_Pellet_22_1_sr = go_Pellet_22_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_22_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_22_1_sr.sharedMaterial = unlitMat;
        go_Pellet_22_1_sr.sortingOrder = 2;
        go_Pellet_22_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_22_1);

        // --- Wall_22_2 ---
        var go_Wall_22_2 = new GameObject("Wall_22_2");
        go_Wall_22_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_2.transform.position = new Vector3(-11.5f, -7.0f, 0.0f);
        var go_Wall_22_2_rb = go_Wall_22_2.AddComponent<Rigidbody2D>();
        go_Wall_22_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_2_bc = go_Wall_22_2.AddComponent<BoxCollider2D>();
        go_Wall_22_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_2_sr = go_Wall_22_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_2);

        // --- Wall_22_3 ---
        var go_Wall_22_3 = new GameObject("Wall_22_3");
        go_Wall_22_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_3.transform.position = new Vector3(-10.5f, -7.0f, 0.0f);
        var go_Wall_22_3_rb = go_Wall_22_3.AddComponent<Rigidbody2D>();
        go_Wall_22_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_3_bc = go_Wall_22_3.AddComponent<BoxCollider2D>();
        go_Wall_22_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_3_sr = go_Wall_22_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_3);

        // --- Wall_22_4 ---
        var go_Wall_22_4 = new GameObject("Wall_22_4");
        go_Wall_22_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_4.transform.position = new Vector3(-9.5f, -7.0f, 0.0f);
        var go_Wall_22_4_rb = go_Wall_22_4.AddComponent<Rigidbody2D>();
        go_Wall_22_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_4_bc = go_Wall_22_4.AddComponent<BoxCollider2D>();
        go_Wall_22_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_4_sr = go_Wall_22_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_4);

        // --- Wall_22_5 ---
        var go_Wall_22_5 = new GameObject("Wall_22_5");
        go_Wall_22_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_5.transform.position = new Vector3(-8.5f, -7.0f, 0.0f);
        var go_Wall_22_5_rb = go_Wall_22_5.AddComponent<Rigidbody2D>();
        go_Wall_22_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_5_bc = go_Wall_22_5.AddComponent<BoxCollider2D>();
        go_Wall_22_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_5_sr = go_Wall_22_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_5);

        // --- Pellet_22_6 ---
        var go_Pellet_22_6 = new GameObject("Pellet_22_6");
        go_Pellet_22_6.tag = "Pellet";
        go_Pellet_22_6.transform.position = new Vector3(-7.5f, -7.0f, 0.0f);
        var go_Pellet_22_6_rb = go_Pellet_22_6.AddComponent<Rigidbody2D>();
        go_Pellet_22_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_22_6_bc = go_Pellet_22_6.AddComponent<BoxCollider2D>();
        go_Pellet_22_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_22_6_bc.isTrigger = true;
        var go_Pellet_22_6_sr = go_Pellet_22_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_22_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_22_6_sr.sharedMaterial = unlitMat;
        go_Pellet_22_6_sr.sortingOrder = 2;
        go_Pellet_22_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_22_6);

        // --- Wall_22_7 ---
        var go_Wall_22_7 = new GameObject("Wall_22_7");
        go_Wall_22_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_7.transform.position = new Vector3(-6.5f, -7.0f, 0.0f);
        var go_Wall_22_7_rb = go_Wall_22_7.AddComponent<Rigidbody2D>();
        go_Wall_22_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_7_bc = go_Wall_22_7.AddComponent<BoxCollider2D>();
        go_Wall_22_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_7_sr = go_Wall_22_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_7);

        // --- Wall_22_8 ---
        var go_Wall_22_8 = new GameObject("Wall_22_8");
        go_Wall_22_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_8.transform.position = new Vector3(-5.5f, -7.0f, 0.0f);
        var go_Wall_22_8_rb = go_Wall_22_8.AddComponent<Rigidbody2D>();
        go_Wall_22_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_8_bc = go_Wall_22_8.AddComponent<BoxCollider2D>();
        go_Wall_22_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_8_sr = go_Wall_22_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_8);

        // --- Wall_22_9 ---
        var go_Wall_22_9 = new GameObject("Wall_22_9");
        go_Wall_22_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_9.transform.position = new Vector3(-4.5f, -7.0f, 0.0f);
        var go_Wall_22_9_rb = go_Wall_22_9.AddComponent<Rigidbody2D>();
        go_Wall_22_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_9_bc = go_Wall_22_9.AddComponent<BoxCollider2D>();
        go_Wall_22_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_9_sr = go_Wall_22_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_9);

        // --- Wall_22_10 ---
        var go_Wall_22_10 = new GameObject("Wall_22_10");
        go_Wall_22_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_10.transform.position = new Vector3(-3.5f, -7.0f, 0.0f);
        var go_Wall_22_10_rb = go_Wall_22_10.AddComponent<Rigidbody2D>();
        go_Wall_22_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_10_bc = go_Wall_22_10.AddComponent<BoxCollider2D>();
        go_Wall_22_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_10_sr = go_Wall_22_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_10);

        // --- Wall_22_11 ---
        var go_Wall_22_11 = new GameObject("Wall_22_11");
        go_Wall_22_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_11.transform.position = new Vector3(-2.5f, -7.0f, 0.0f);
        var go_Wall_22_11_rb = go_Wall_22_11.AddComponent<Rigidbody2D>();
        go_Wall_22_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_11_bc = go_Wall_22_11.AddComponent<BoxCollider2D>();
        go_Wall_22_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_11_sr = go_Wall_22_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_11);

        // --- Pellet_22_12 ---
        var go_Pellet_22_12 = new GameObject("Pellet_22_12");
        go_Pellet_22_12.tag = "Pellet";
        go_Pellet_22_12.transform.position = new Vector3(-1.5f, -7.0f, 0.0f);
        var go_Pellet_22_12_rb = go_Pellet_22_12.AddComponent<Rigidbody2D>();
        go_Pellet_22_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_22_12_bc = go_Pellet_22_12.AddComponent<BoxCollider2D>();
        go_Pellet_22_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_22_12_bc.isTrigger = true;
        var go_Pellet_22_12_sr = go_Pellet_22_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_22_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_22_12_sr.sharedMaterial = unlitMat;
        go_Pellet_22_12_sr.sortingOrder = 2;
        go_Pellet_22_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_22_12);

        // --- Wall_22_13 ---
        var go_Wall_22_13 = new GameObject("Wall_22_13");
        go_Wall_22_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_13.transform.position = new Vector3(-0.5f, -7.0f, 0.0f);
        var go_Wall_22_13_rb = go_Wall_22_13.AddComponent<Rigidbody2D>();
        go_Wall_22_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_13_bc = go_Wall_22_13.AddComponent<BoxCollider2D>();
        go_Wall_22_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_13_sr = go_Wall_22_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_13);

        // --- Wall_22_14 ---
        var go_Wall_22_14 = new GameObject("Wall_22_14");
        go_Wall_22_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_14.transform.position = new Vector3(0.5f, -7.0f, 0.0f);
        var go_Wall_22_14_rb = go_Wall_22_14.AddComponent<Rigidbody2D>();
        go_Wall_22_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_14_bc = go_Wall_22_14.AddComponent<BoxCollider2D>();
        go_Wall_22_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_14_sr = go_Wall_22_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_14);

        // --- Pellet_22_15 ---
        var go_Pellet_22_15 = new GameObject("Pellet_22_15");
        go_Pellet_22_15.tag = "Pellet";
        go_Pellet_22_15.transform.position = new Vector3(1.5f, -7.0f, 0.0f);
        var go_Pellet_22_15_rb = go_Pellet_22_15.AddComponent<Rigidbody2D>();
        go_Pellet_22_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_22_15_bc = go_Pellet_22_15.AddComponent<BoxCollider2D>();
        go_Pellet_22_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_22_15_bc.isTrigger = true;
        var go_Pellet_22_15_sr = go_Pellet_22_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_22_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_22_15_sr.sharedMaterial = unlitMat;
        go_Pellet_22_15_sr.sortingOrder = 2;
        go_Pellet_22_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_22_15);

        // --- Wall_22_16 ---
        var go_Wall_22_16 = new GameObject("Wall_22_16");
        go_Wall_22_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_16.transform.position = new Vector3(2.5f, -7.0f, 0.0f);
        var go_Wall_22_16_rb = go_Wall_22_16.AddComponent<Rigidbody2D>();
        go_Wall_22_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_16_bc = go_Wall_22_16.AddComponent<BoxCollider2D>();
        go_Wall_22_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_16_sr = go_Wall_22_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_16);

        // --- Wall_22_17 ---
        var go_Wall_22_17 = new GameObject("Wall_22_17");
        go_Wall_22_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_17.transform.position = new Vector3(3.5f, -7.0f, 0.0f);
        var go_Wall_22_17_rb = go_Wall_22_17.AddComponent<Rigidbody2D>();
        go_Wall_22_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_17_bc = go_Wall_22_17.AddComponent<BoxCollider2D>();
        go_Wall_22_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_17_sr = go_Wall_22_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_17);

        // --- Wall_22_18 ---
        var go_Wall_22_18 = new GameObject("Wall_22_18");
        go_Wall_22_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_18.transform.position = new Vector3(4.5f, -7.0f, 0.0f);
        var go_Wall_22_18_rb = go_Wall_22_18.AddComponent<Rigidbody2D>();
        go_Wall_22_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_18_bc = go_Wall_22_18.AddComponent<BoxCollider2D>();
        go_Wall_22_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_18_sr = go_Wall_22_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_18);

        // --- Wall_22_19 ---
        var go_Wall_22_19 = new GameObject("Wall_22_19");
        go_Wall_22_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_19.transform.position = new Vector3(5.5f, -7.0f, 0.0f);
        var go_Wall_22_19_rb = go_Wall_22_19.AddComponent<Rigidbody2D>();
        go_Wall_22_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_19_bc = go_Wall_22_19.AddComponent<BoxCollider2D>();
        go_Wall_22_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_19_sr = go_Wall_22_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_19);

        // --- Wall_22_20 ---
        var go_Wall_22_20 = new GameObject("Wall_22_20");
        go_Wall_22_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_20.transform.position = new Vector3(6.5f, -7.0f, 0.0f);
        var go_Wall_22_20_rb = go_Wall_22_20.AddComponent<Rigidbody2D>();
        go_Wall_22_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_20_bc = go_Wall_22_20.AddComponent<BoxCollider2D>();
        go_Wall_22_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_20_sr = go_Wall_22_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_20);

        // --- Pellet_22_21 ---
        var go_Pellet_22_21 = new GameObject("Pellet_22_21");
        go_Pellet_22_21.tag = "Pellet";
        go_Pellet_22_21.transform.position = new Vector3(7.5f, -7.0f, 0.0f);
        var go_Pellet_22_21_rb = go_Pellet_22_21.AddComponent<Rigidbody2D>();
        go_Pellet_22_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_22_21_bc = go_Pellet_22_21.AddComponent<BoxCollider2D>();
        go_Pellet_22_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_22_21_bc.isTrigger = true;
        var go_Pellet_22_21_sr = go_Pellet_22_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_22_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_22_21_sr.sharedMaterial = unlitMat;
        go_Pellet_22_21_sr.sortingOrder = 2;
        go_Pellet_22_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_22_21);

        // --- Wall_22_22 ---
        var go_Wall_22_22 = new GameObject("Wall_22_22");
        go_Wall_22_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_22.transform.position = new Vector3(8.5f, -7.0f, 0.0f);
        var go_Wall_22_22_rb = go_Wall_22_22.AddComponent<Rigidbody2D>();
        go_Wall_22_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_22_bc = go_Wall_22_22.AddComponent<BoxCollider2D>();
        go_Wall_22_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_22_sr = go_Wall_22_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_22);

        // --- Wall_22_23 ---
        var go_Wall_22_23 = new GameObject("Wall_22_23");
        go_Wall_22_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_23.transform.position = new Vector3(9.5f, -7.0f, 0.0f);
        var go_Wall_22_23_rb = go_Wall_22_23.AddComponent<Rigidbody2D>();
        go_Wall_22_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_23_bc = go_Wall_22_23.AddComponent<BoxCollider2D>();
        go_Wall_22_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_23_sr = go_Wall_22_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_23);

        // --- Wall_22_24 ---
        var go_Wall_22_24 = new GameObject("Wall_22_24");
        go_Wall_22_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_24.transform.position = new Vector3(10.5f, -7.0f, 0.0f);
        var go_Wall_22_24_rb = go_Wall_22_24.AddComponent<Rigidbody2D>();
        go_Wall_22_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_24_bc = go_Wall_22_24.AddComponent<BoxCollider2D>();
        go_Wall_22_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_24_sr = go_Wall_22_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_24);

        // --- Wall_22_25 ---
        var go_Wall_22_25 = new GameObject("Wall_22_25");
        go_Wall_22_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_25.transform.position = new Vector3(11.5f, -7.0f, 0.0f);
        var go_Wall_22_25_rb = go_Wall_22_25.AddComponent<Rigidbody2D>();
        go_Wall_22_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_25_bc = go_Wall_22_25.AddComponent<BoxCollider2D>();
        go_Wall_22_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_25_sr = go_Wall_22_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_25);

        // --- Pellet_22_26 ---
        var go_Pellet_22_26 = new GameObject("Pellet_22_26");
        go_Pellet_22_26.tag = "Pellet";
        go_Pellet_22_26.transform.position = new Vector3(12.5f, -7.0f, 0.0f);
        var go_Pellet_22_26_rb = go_Pellet_22_26.AddComponent<Rigidbody2D>();
        go_Pellet_22_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_22_26_bc = go_Pellet_22_26.AddComponent<BoxCollider2D>();
        go_Pellet_22_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_22_26_bc.isTrigger = true;
        var go_Pellet_22_26_sr = go_Pellet_22_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_22_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_22_26_sr.sharedMaterial = unlitMat;
        go_Pellet_22_26_sr.sortingOrder = 2;
        go_Pellet_22_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_22_26);

        // --- Wall_22_27 ---
        var go_Wall_22_27 = new GameObject("Wall_22_27");
        go_Wall_22_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_22_27.transform.position = new Vector3(13.5f, -7.0f, 0.0f);
        var go_Wall_22_27_rb = go_Wall_22_27.AddComponent<Rigidbody2D>();
        go_Wall_22_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_22_27_bc = go_Wall_22_27.AddComponent<BoxCollider2D>();
        go_Wall_22_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_22_27_sr = go_Wall_22_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_22_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_22_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_22_27);

        // --- Wall_23_0 ---
        var go_Wall_23_0 = new GameObject("Wall_23_0");
        go_Wall_23_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_23_0.transform.position = new Vector3(-13.5f, -8.0f, 0.0f);
        var go_Wall_23_0_rb = go_Wall_23_0.AddComponent<Rigidbody2D>();
        go_Wall_23_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_23_0_bc = go_Wall_23_0.AddComponent<BoxCollider2D>();
        go_Wall_23_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_23_0_sr = go_Wall_23_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_23_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_23_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_23_0);

        // --- Pellet_23_1 ---
        var go_Pellet_23_1 = new GameObject("Pellet_23_1");
        go_Pellet_23_1.tag = "PowerPellet";
        go_Pellet_23_1.transform.position = new Vector3(-12.5f, -8.0f, 0.0f);
        var go_Pellet_23_1_rb = go_Pellet_23_1.AddComponent<Rigidbody2D>();
        go_Pellet_23_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_1_bc = go_Pellet_23_1.AddComponent<BoxCollider2D>();
        go_Pellet_23_1_bc.size = new Vector2(0.5f, 0.5f);
        go_Pellet_23_1_bc.isTrigger = true;
        var go_Pellet_23_1_sr = go_Pellet_23_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_large != null) go_Pellet_23_1_sr.sprite = sprite_pellet_large;
        if (unlitMat != null) go_Pellet_23_1_sr.sharedMaterial = unlitMat;
        go_Pellet_23_1_sr.sortingOrder = 2;
        go_Pellet_23_1.AddComponent<PowerPellet>();
        // PowerPellet.duration = 8.0
        // PowerPellet.points = 50
        EditorUtility.SetDirty(go_Pellet_23_1);

        // --- Node_23_1 ---
        var go_Node_23_1 = new GameObject("Node_23_1");
        go_Node_23_1.transform.position = new Vector3(-12.5f, -8.0f, 0.0f);
        var go_Node_23_1_rb = go_Node_23_1.AddComponent<Rigidbody2D>();
        go_Node_23_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_23_1_bc = go_Node_23_1.AddComponent<BoxCollider2D>();
        go_Node_23_1_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_23_1_bc.isTrigger = true;
        go_Node_23_1.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_23_1);

        // --- Pellet_23_2 ---
        var go_Pellet_23_2 = new GameObject("Pellet_23_2");
        go_Pellet_23_2.tag = "Pellet";
        go_Pellet_23_2.transform.position = new Vector3(-11.5f, -8.0f, 0.0f);
        var go_Pellet_23_2_rb = go_Pellet_23_2.AddComponent<Rigidbody2D>();
        go_Pellet_23_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_2_bc = go_Pellet_23_2.AddComponent<BoxCollider2D>();
        go_Pellet_23_2_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_2_bc.isTrigger = true;
        var go_Pellet_23_2_sr = go_Pellet_23_2.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_2_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_2_sr.sharedMaterial = unlitMat;
        go_Pellet_23_2_sr.sortingOrder = 2;
        go_Pellet_23_2.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_2);

        // --- Pellet_23_3 ---
        var go_Pellet_23_3 = new GameObject("Pellet_23_3");
        go_Pellet_23_3.tag = "Pellet";
        go_Pellet_23_3.transform.position = new Vector3(-10.5f, -8.0f, 0.0f);
        var go_Pellet_23_3_rb = go_Pellet_23_3.AddComponent<Rigidbody2D>();
        go_Pellet_23_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_3_bc = go_Pellet_23_3.AddComponent<BoxCollider2D>();
        go_Pellet_23_3_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_3_bc.isTrigger = true;
        var go_Pellet_23_3_sr = go_Pellet_23_3.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_3_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_3_sr.sharedMaterial = unlitMat;
        go_Pellet_23_3_sr.sortingOrder = 2;
        go_Pellet_23_3.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_3);

        // --- Node_23_3 ---
        var go_Node_23_3 = new GameObject("Node_23_3");
        go_Node_23_3.transform.position = new Vector3(-10.5f, -8.0f, 0.0f);
        var go_Node_23_3_rb = go_Node_23_3.AddComponent<Rigidbody2D>();
        go_Node_23_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_23_3_bc = go_Node_23_3.AddComponent<BoxCollider2D>();
        go_Node_23_3_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_23_3_bc.isTrigger = true;
        go_Node_23_3.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_23_3);

        // --- Wall_23_4 ---
        var go_Wall_23_4 = new GameObject("Wall_23_4");
        go_Wall_23_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_23_4.transform.position = new Vector3(-9.5f, -8.0f, 0.0f);
        var go_Wall_23_4_rb = go_Wall_23_4.AddComponent<Rigidbody2D>();
        go_Wall_23_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_23_4_bc = go_Wall_23_4.AddComponent<BoxCollider2D>();
        go_Wall_23_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_23_4_sr = go_Wall_23_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_23_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_23_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_23_4);

        // --- Wall_23_5 ---
        var go_Wall_23_5 = new GameObject("Wall_23_5");
        go_Wall_23_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_23_5.transform.position = new Vector3(-8.5f, -8.0f, 0.0f);
        var go_Wall_23_5_rb = go_Wall_23_5.AddComponent<Rigidbody2D>();
        go_Wall_23_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_23_5_bc = go_Wall_23_5.AddComponent<BoxCollider2D>();
        go_Wall_23_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_23_5_sr = go_Wall_23_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_23_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_23_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_23_5);

        // --- Pellet_23_6 ---
        var go_Pellet_23_6 = new GameObject("Pellet_23_6");
        go_Pellet_23_6.tag = "Pellet";
        go_Pellet_23_6.transform.position = new Vector3(-7.5f, -8.0f, 0.0f);
        var go_Pellet_23_6_rb = go_Pellet_23_6.AddComponent<Rigidbody2D>();
        go_Pellet_23_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_6_bc = go_Pellet_23_6.AddComponent<BoxCollider2D>();
        go_Pellet_23_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_6_bc.isTrigger = true;
        var go_Pellet_23_6_sr = go_Pellet_23_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_6_sr.sharedMaterial = unlitMat;
        go_Pellet_23_6_sr.sortingOrder = 2;
        go_Pellet_23_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_6);

        // --- Node_23_6 ---
        var go_Node_23_6 = new GameObject("Node_23_6");
        go_Node_23_6.transform.position = new Vector3(-7.5f, -8.0f, 0.0f);
        var go_Node_23_6_rb = go_Node_23_6.AddComponent<Rigidbody2D>();
        go_Node_23_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_23_6_bc = go_Node_23_6.AddComponent<BoxCollider2D>();
        go_Node_23_6_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_23_6_bc.isTrigger = true;
        go_Node_23_6.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_23_6);

        // --- Pellet_23_7 ---
        var go_Pellet_23_7 = new GameObject("Pellet_23_7");
        go_Pellet_23_7.tag = "Pellet";
        go_Pellet_23_7.transform.position = new Vector3(-6.5f, -8.0f, 0.0f);
        var go_Pellet_23_7_rb = go_Pellet_23_7.AddComponent<Rigidbody2D>();
        go_Pellet_23_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_7_bc = go_Pellet_23_7.AddComponent<BoxCollider2D>();
        go_Pellet_23_7_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_7_bc.isTrigger = true;
        var go_Pellet_23_7_sr = go_Pellet_23_7.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_7_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_7_sr.sharedMaterial = unlitMat;
        go_Pellet_23_7_sr.sortingOrder = 2;
        go_Pellet_23_7.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_7);

        // --- Pellet_23_8 ---
        var go_Pellet_23_8 = new GameObject("Pellet_23_8");
        go_Pellet_23_8.tag = "Pellet";
        go_Pellet_23_8.transform.position = new Vector3(-5.5f, -8.0f, 0.0f);
        var go_Pellet_23_8_rb = go_Pellet_23_8.AddComponent<Rigidbody2D>();
        go_Pellet_23_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_8_bc = go_Pellet_23_8.AddComponent<BoxCollider2D>();
        go_Pellet_23_8_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_8_bc.isTrigger = true;
        var go_Pellet_23_8_sr = go_Pellet_23_8.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_8_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_8_sr.sharedMaterial = unlitMat;
        go_Pellet_23_8_sr.sortingOrder = 2;
        go_Pellet_23_8.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_8);

        // --- Pellet_23_9 ---
        var go_Pellet_23_9 = new GameObject("Pellet_23_9");
        go_Pellet_23_9.tag = "Pellet";
        go_Pellet_23_9.transform.position = new Vector3(-4.5f, -8.0f, 0.0f);
        var go_Pellet_23_9_rb = go_Pellet_23_9.AddComponent<Rigidbody2D>();
        go_Pellet_23_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_9_bc = go_Pellet_23_9.AddComponent<BoxCollider2D>();
        go_Pellet_23_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_9_bc.isTrigger = true;
        var go_Pellet_23_9_sr = go_Pellet_23_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_9_sr.sharedMaterial = unlitMat;
        go_Pellet_23_9_sr.sortingOrder = 2;
        go_Pellet_23_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_9);

        // --- Node_23_9 ---
        var go_Node_23_9 = new GameObject("Node_23_9");
        go_Node_23_9.transform.position = new Vector3(-4.5f, -8.0f, 0.0f);
        var go_Node_23_9_rb = go_Node_23_9.AddComponent<Rigidbody2D>();
        go_Node_23_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_23_9_bc = go_Node_23_9.AddComponent<BoxCollider2D>();
        go_Node_23_9_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_23_9_bc.isTrigger = true;
        go_Node_23_9.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_23_9);

        // --- Pellet_23_10 ---
        var go_Pellet_23_10 = new GameObject("Pellet_23_10");
        go_Pellet_23_10.tag = "Pellet";
        go_Pellet_23_10.transform.position = new Vector3(-3.5f, -8.0f, 0.0f);
        var go_Pellet_23_10_rb = go_Pellet_23_10.AddComponent<Rigidbody2D>();
        go_Pellet_23_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_10_bc = go_Pellet_23_10.AddComponent<BoxCollider2D>();
        go_Pellet_23_10_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_10_bc.isTrigger = true;
        var go_Pellet_23_10_sr = go_Pellet_23_10.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_10_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_10_sr.sharedMaterial = unlitMat;
        go_Pellet_23_10_sr.sortingOrder = 2;
        go_Pellet_23_10.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_10);

        // --- Pellet_23_11 ---
        var go_Pellet_23_11 = new GameObject("Pellet_23_11");
        go_Pellet_23_11.tag = "Pellet";
        go_Pellet_23_11.transform.position = new Vector3(-2.5f, -8.0f, 0.0f);
        var go_Pellet_23_11_rb = go_Pellet_23_11.AddComponent<Rigidbody2D>();
        go_Pellet_23_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_11_bc = go_Pellet_23_11.AddComponent<BoxCollider2D>();
        go_Pellet_23_11_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_11_bc.isTrigger = true;
        var go_Pellet_23_11_sr = go_Pellet_23_11.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_11_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_11_sr.sharedMaterial = unlitMat;
        go_Pellet_23_11_sr.sortingOrder = 2;
        go_Pellet_23_11.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_11);

        // --- Pellet_23_12 ---
        var go_Pellet_23_12 = new GameObject("Pellet_23_12");
        go_Pellet_23_12.tag = "Pellet";
        go_Pellet_23_12.transform.position = new Vector3(-1.5f, -8.0f, 0.0f);
        var go_Pellet_23_12_rb = go_Pellet_23_12.AddComponent<Rigidbody2D>();
        go_Pellet_23_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_12_bc = go_Pellet_23_12.AddComponent<BoxCollider2D>();
        go_Pellet_23_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_12_bc.isTrigger = true;
        var go_Pellet_23_12_sr = go_Pellet_23_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_12_sr.sharedMaterial = unlitMat;
        go_Pellet_23_12_sr.sortingOrder = 2;
        go_Pellet_23_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_12);

        // --- Node_23_12 ---
        var go_Node_23_12 = new GameObject("Node_23_12");
        go_Node_23_12.transform.position = new Vector3(-1.5f, -8.0f, 0.0f);
        var go_Node_23_12_rb = go_Node_23_12.AddComponent<Rigidbody2D>();
        go_Node_23_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_23_12_bc = go_Node_23_12.AddComponent<BoxCollider2D>();
        go_Node_23_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_23_12_bc.isTrigger = true;
        go_Node_23_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_23_12);

        // --- Pellet_23_14 ---
        var go_Pellet_23_14 = new GameObject("Pellet_23_14");
        go_Pellet_23_14.tag = "Pellet";
        go_Pellet_23_14.transform.position = new Vector3(0.5f, -8.0f, 0.0f);
        var go_Pellet_23_14_rb = go_Pellet_23_14.AddComponent<Rigidbody2D>();
        go_Pellet_23_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_14_bc = go_Pellet_23_14.AddComponent<BoxCollider2D>();
        go_Pellet_23_14_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_14_bc.isTrigger = true;
        var go_Pellet_23_14_sr = go_Pellet_23_14.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_14_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_14_sr.sharedMaterial = unlitMat;
        go_Pellet_23_14_sr.sortingOrder = 2;
        go_Pellet_23_14.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_14);

        // --- Pellet_23_15 ---
        var go_Pellet_23_15 = new GameObject("Pellet_23_15");
        go_Pellet_23_15.tag = "Pellet";
        go_Pellet_23_15.transform.position = new Vector3(1.5f, -8.0f, 0.0f);
        var go_Pellet_23_15_rb = go_Pellet_23_15.AddComponent<Rigidbody2D>();
        go_Pellet_23_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_15_bc = go_Pellet_23_15.AddComponent<BoxCollider2D>();
        go_Pellet_23_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_15_bc.isTrigger = true;
        var go_Pellet_23_15_sr = go_Pellet_23_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_15_sr.sharedMaterial = unlitMat;
        go_Pellet_23_15_sr.sortingOrder = 2;
        go_Pellet_23_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_15);

        // --- Node_23_15 ---
        var go_Node_23_15 = new GameObject("Node_23_15");
        go_Node_23_15.transform.position = new Vector3(1.5f, -8.0f, 0.0f);
        var go_Node_23_15_rb = go_Node_23_15.AddComponent<Rigidbody2D>();
        go_Node_23_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_23_15_bc = go_Node_23_15.AddComponent<BoxCollider2D>();
        go_Node_23_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_23_15_bc.isTrigger = true;
        go_Node_23_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_23_15);

        // --- Pellet_23_16 ---
        var go_Pellet_23_16 = new GameObject("Pellet_23_16");
        go_Pellet_23_16.tag = "Pellet";
        go_Pellet_23_16.transform.position = new Vector3(2.5f, -8.0f, 0.0f);
        var go_Pellet_23_16_rb = go_Pellet_23_16.AddComponent<Rigidbody2D>();
        go_Pellet_23_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_16_bc = go_Pellet_23_16.AddComponent<BoxCollider2D>();
        go_Pellet_23_16_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_16_bc.isTrigger = true;
        var go_Pellet_23_16_sr = go_Pellet_23_16.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_16_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_16_sr.sharedMaterial = unlitMat;
        go_Pellet_23_16_sr.sortingOrder = 2;
        go_Pellet_23_16.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_16);

        // --- Pellet_23_17 ---
        var go_Pellet_23_17 = new GameObject("Pellet_23_17");
        go_Pellet_23_17.tag = "Pellet";
        go_Pellet_23_17.transform.position = new Vector3(3.5f, -8.0f, 0.0f);
        var go_Pellet_23_17_rb = go_Pellet_23_17.AddComponent<Rigidbody2D>();
        go_Pellet_23_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_17_bc = go_Pellet_23_17.AddComponent<BoxCollider2D>();
        go_Pellet_23_17_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_17_bc.isTrigger = true;
        var go_Pellet_23_17_sr = go_Pellet_23_17.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_17_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_17_sr.sharedMaterial = unlitMat;
        go_Pellet_23_17_sr.sortingOrder = 2;
        go_Pellet_23_17.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_17);

        // --- Pellet_23_18 ---
        var go_Pellet_23_18 = new GameObject("Pellet_23_18");
        go_Pellet_23_18.tag = "Pellet";
        go_Pellet_23_18.transform.position = new Vector3(4.5f, -8.0f, 0.0f);
        var go_Pellet_23_18_rb = go_Pellet_23_18.AddComponent<Rigidbody2D>();
        go_Pellet_23_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_18_bc = go_Pellet_23_18.AddComponent<BoxCollider2D>();
        go_Pellet_23_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_18_bc.isTrigger = true;
        var go_Pellet_23_18_sr = go_Pellet_23_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_18_sr.sharedMaterial = unlitMat;
        go_Pellet_23_18_sr.sortingOrder = 2;
        go_Pellet_23_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_18);

        // --- Node_23_18 ---
        var go_Node_23_18 = new GameObject("Node_23_18");
        go_Node_23_18.transform.position = new Vector3(4.5f, -8.0f, 0.0f);
        var go_Node_23_18_rb = go_Node_23_18.AddComponent<Rigidbody2D>();
        go_Node_23_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_23_18_bc = go_Node_23_18.AddComponent<BoxCollider2D>();
        go_Node_23_18_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_23_18_bc.isTrigger = true;
        go_Node_23_18.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_23_18);

        // --- Pellet_23_19 ---
        var go_Pellet_23_19 = new GameObject("Pellet_23_19");
        go_Pellet_23_19.tag = "Pellet";
        go_Pellet_23_19.transform.position = new Vector3(5.5f, -8.0f, 0.0f);
        var go_Pellet_23_19_rb = go_Pellet_23_19.AddComponent<Rigidbody2D>();
        go_Pellet_23_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_19_bc = go_Pellet_23_19.AddComponent<BoxCollider2D>();
        go_Pellet_23_19_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_19_bc.isTrigger = true;
        var go_Pellet_23_19_sr = go_Pellet_23_19.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_19_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_19_sr.sharedMaterial = unlitMat;
        go_Pellet_23_19_sr.sortingOrder = 2;
        go_Pellet_23_19.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_19);

        // --- Pellet_23_20 ---
        var go_Pellet_23_20 = new GameObject("Pellet_23_20");
        go_Pellet_23_20.tag = "Pellet";
        go_Pellet_23_20.transform.position = new Vector3(6.5f, -8.0f, 0.0f);
        var go_Pellet_23_20_rb = go_Pellet_23_20.AddComponent<Rigidbody2D>();
        go_Pellet_23_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_20_bc = go_Pellet_23_20.AddComponent<BoxCollider2D>();
        go_Pellet_23_20_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_20_bc.isTrigger = true;
        var go_Pellet_23_20_sr = go_Pellet_23_20.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_20_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_20_sr.sharedMaterial = unlitMat;
        go_Pellet_23_20_sr.sortingOrder = 2;
        go_Pellet_23_20.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_20);

        // --- Pellet_23_21 ---
        var go_Pellet_23_21 = new GameObject("Pellet_23_21");
        go_Pellet_23_21.tag = "Pellet";
        go_Pellet_23_21.transform.position = new Vector3(7.5f, -8.0f, 0.0f);
        var go_Pellet_23_21_rb = go_Pellet_23_21.AddComponent<Rigidbody2D>();
        go_Pellet_23_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_21_bc = go_Pellet_23_21.AddComponent<BoxCollider2D>();
        go_Pellet_23_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_21_bc.isTrigger = true;
        var go_Pellet_23_21_sr = go_Pellet_23_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_21_sr.sharedMaterial = unlitMat;
        go_Pellet_23_21_sr.sortingOrder = 2;
        go_Pellet_23_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_21);

        // --- Node_23_21 ---
        var go_Node_23_21 = new GameObject("Node_23_21");
        go_Node_23_21.transform.position = new Vector3(7.5f, -8.0f, 0.0f);
        var go_Node_23_21_rb = go_Node_23_21.AddComponent<Rigidbody2D>();
        go_Node_23_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_23_21_bc = go_Node_23_21.AddComponent<BoxCollider2D>();
        go_Node_23_21_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_23_21_bc.isTrigger = true;
        go_Node_23_21.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_23_21);

        // --- Wall_23_22 ---
        var go_Wall_23_22 = new GameObject("Wall_23_22");
        go_Wall_23_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_23_22.transform.position = new Vector3(8.5f, -8.0f, 0.0f);
        var go_Wall_23_22_rb = go_Wall_23_22.AddComponent<Rigidbody2D>();
        go_Wall_23_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_23_22_bc = go_Wall_23_22.AddComponent<BoxCollider2D>();
        go_Wall_23_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_23_22_sr = go_Wall_23_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_23_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_23_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_23_22);

        // --- Wall_23_23 ---
        var go_Wall_23_23 = new GameObject("Wall_23_23");
        go_Wall_23_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_23_23.transform.position = new Vector3(9.5f, -8.0f, 0.0f);
        var go_Wall_23_23_rb = go_Wall_23_23.AddComponent<Rigidbody2D>();
        go_Wall_23_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_23_23_bc = go_Wall_23_23.AddComponent<BoxCollider2D>();
        go_Wall_23_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_23_23_sr = go_Wall_23_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_23_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_23_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_23_23);

        // --- Pellet_23_24 ---
        var go_Pellet_23_24 = new GameObject("Pellet_23_24");
        go_Pellet_23_24.tag = "Pellet";
        go_Pellet_23_24.transform.position = new Vector3(10.5f, -8.0f, 0.0f);
        var go_Pellet_23_24_rb = go_Pellet_23_24.AddComponent<Rigidbody2D>();
        go_Pellet_23_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_24_bc = go_Pellet_23_24.AddComponent<BoxCollider2D>();
        go_Pellet_23_24_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_24_bc.isTrigger = true;
        var go_Pellet_23_24_sr = go_Pellet_23_24.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_24_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_24_sr.sharedMaterial = unlitMat;
        go_Pellet_23_24_sr.sortingOrder = 2;
        go_Pellet_23_24.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_24);

        // --- Node_23_24 ---
        var go_Node_23_24 = new GameObject("Node_23_24");
        go_Node_23_24.transform.position = new Vector3(10.5f, -8.0f, 0.0f);
        var go_Node_23_24_rb = go_Node_23_24.AddComponent<Rigidbody2D>();
        go_Node_23_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_23_24_bc = go_Node_23_24.AddComponent<BoxCollider2D>();
        go_Node_23_24_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_23_24_bc.isTrigger = true;
        go_Node_23_24.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_23_24);

        // --- Pellet_23_25 ---
        var go_Pellet_23_25 = new GameObject("Pellet_23_25");
        go_Pellet_23_25.tag = "Pellet";
        go_Pellet_23_25.transform.position = new Vector3(11.5f, -8.0f, 0.0f);
        var go_Pellet_23_25_rb = go_Pellet_23_25.AddComponent<Rigidbody2D>();
        go_Pellet_23_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_25_bc = go_Pellet_23_25.AddComponent<BoxCollider2D>();
        go_Pellet_23_25_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_23_25_bc.isTrigger = true;
        var go_Pellet_23_25_sr = go_Pellet_23_25.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_23_25_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_23_25_sr.sharedMaterial = unlitMat;
        go_Pellet_23_25_sr.sortingOrder = 2;
        go_Pellet_23_25.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_23_25);

        // --- Pellet_23_26 ---
        var go_Pellet_23_26 = new GameObject("Pellet_23_26");
        go_Pellet_23_26.tag = "PowerPellet";
        go_Pellet_23_26.transform.position = new Vector3(12.5f, -8.0f, 0.0f);
        var go_Pellet_23_26_rb = go_Pellet_23_26.AddComponent<Rigidbody2D>();
        go_Pellet_23_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_23_26_bc = go_Pellet_23_26.AddComponent<BoxCollider2D>();
        go_Pellet_23_26_bc.size = new Vector2(0.5f, 0.5f);
        go_Pellet_23_26_bc.isTrigger = true;
        var go_Pellet_23_26_sr = go_Pellet_23_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_large != null) go_Pellet_23_26_sr.sprite = sprite_pellet_large;
        if (unlitMat != null) go_Pellet_23_26_sr.sharedMaterial = unlitMat;
        go_Pellet_23_26_sr.sortingOrder = 2;
        go_Pellet_23_26.AddComponent<PowerPellet>();
        // PowerPellet.duration = 8.0
        // PowerPellet.points = 50
        EditorUtility.SetDirty(go_Pellet_23_26);

        // --- Node_23_26 ---
        var go_Node_23_26 = new GameObject("Node_23_26");
        go_Node_23_26.transform.position = new Vector3(12.5f, -8.0f, 0.0f);
        var go_Node_23_26_rb = go_Node_23_26.AddComponent<Rigidbody2D>();
        go_Node_23_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_23_26_bc = go_Node_23_26.AddComponent<BoxCollider2D>();
        go_Node_23_26_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_23_26_bc.isTrigger = true;
        go_Node_23_26.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_23_26);

        // --- Wall_23_27 ---
        var go_Wall_23_27 = new GameObject("Wall_23_27");
        go_Wall_23_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_23_27.transform.position = new Vector3(13.5f, -8.0f, 0.0f);
        var go_Wall_23_27_rb = go_Wall_23_27.AddComponent<Rigidbody2D>();
        go_Wall_23_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_23_27_bc = go_Wall_23_27.AddComponent<BoxCollider2D>();
        go_Wall_23_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_23_27_sr = go_Wall_23_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_23_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_23_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_23_27);

        // --- Wall_24_0 ---
        var go_Wall_24_0 = new GameObject("Wall_24_0");
        go_Wall_24_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_0.transform.position = new Vector3(-13.5f, -9.0f, 0.0f);
        var go_Wall_24_0_rb = go_Wall_24_0.AddComponent<Rigidbody2D>();
        go_Wall_24_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_0_bc = go_Wall_24_0.AddComponent<BoxCollider2D>();
        go_Wall_24_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_0_sr = go_Wall_24_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_0);

        // --- Wall_24_1 ---
        var go_Wall_24_1 = new GameObject("Wall_24_1");
        go_Wall_24_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_1.transform.position = new Vector3(-12.5f, -9.0f, 0.0f);
        var go_Wall_24_1_rb = go_Wall_24_1.AddComponent<Rigidbody2D>();
        go_Wall_24_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_1_bc = go_Wall_24_1.AddComponent<BoxCollider2D>();
        go_Wall_24_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_1_sr = go_Wall_24_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_1);

        // --- Wall_24_2 ---
        var go_Wall_24_2 = new GameObject("Wall_24_2");
        go_Wall_24_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_2.transform.position = new Vector3(-11.5f, -9.0f, 0.0f);
        var go_Wall_24_2_rb = go_Wall_24_2.AddComponent<Rigidbody2D>();
        go_Wall_24_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_2_bc = go_Wall_24_2.AddComponent<BoxCollider2D>();
        go_Wall_24_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_2_sr = go_Wall_24_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_2);

        // --- Pellet_24_3 ---
        var go_Pellet_24_3 = new GameObject("Pellet_24_3");
        go_Pellet_24_3.tag = "Pellet";
        go_Pellet_24_3.transform.position = new Vector3(-10.5f, -9.0f, 0.0f);
        var go_Pellet_24_3_rb = go_Pellet_24_3.AddComponent<Rigidbody2D>();
        go_Pellet_24_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_24_3_bc = go_Pellet_24_3.AddComponent<BoxCollider2D>();
        go_Pellet_24_3_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_24_3_bc.isTrigger = true;
        var go_Pellet_24_3_sr = go_Pellet_24_3.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_24_3_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_24_3_sr.sharedMaterial = unlitMat;
        go_Pellet_24_3_sr.sortingOrder = 2;
        go_Pellet_24_3.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_24_3);

        // --- Wall_24_4 ---
        var go_Wall_24_4 = new GameObject("Wall_24_4");
        go_Wall_24_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_4.transform.position = new Vector3(-9.5f, -9.0f, 0.0f);
        var go_Wall_24_4_rb = go_Wall_24_4.AddComponent<Rigidbody2D>();
        go_Wall_24_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_4_bc = go_Wall_24_4.AddComponent<BoxCollider2D>();
        go_Wall_24_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_4_sr = go_Wall_24_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_4);

        // --- Wall_24_5 ---
        var go_Wall_24_5 = new GameObject("Wall_24_5");
        go_Wall_24_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_5.transform.position = new Vector3(-8.5f, -9.0f, 0.0f);
        var go_Wall_24_5_rb = go_Wall_24_5.AddComponent<Rigidbody2D>();
        go_Wall_24_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_5_bc = go_Wall_24_5.AddComponent<BoxCollider2D>();
        go_Wall_24_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_5_sr = go_Wall_24_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_5);

        // --- Pellet_24_6 ---
        var go_Pellet_24_6 = new GameObject("Pellet_24_6");
        go_Pellet_24_6.tag = "Pellet";
        go_Pellet_24_6.transform.position = new Vector3(-7.5f, -9.0f, 0.0f);
        var go_Pellet_24_6_rb = go_Pellet_24_6.AddComponent<Rigidbody2D>();
        go_Pellet_24_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_24_6_bc = go_Pellet_24_6.AddComponent<BoxCollider2D>();
        go_Pellet_24_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_24_6_bc.isTrigger = true;
        var go_Pellet_24_6_sr = go_Pellet_24_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_24_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_24_6_sr.sharedMaterial = unlitMat;
        go_Pellet_24_6_sr.sortingOrder = 2;
        go_Pellet_24_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_24_6);

        // --- Wall_24_7 ---
        var go_Wall_24_7 = new GameObject("Wall_24_7");
        go_Wall_24_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_7.transform.position = new Vector3(-6.5f, -9.0f, 0.0f);
        var go_Wall_24_7_rb = go_Wall_24_7.AddComponent<Rigidbody2D>();
        go_Wall_24_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_7_bc = go_Wall_24_7.AddComponent<BoxCollider2D>();
        go_Wall_24_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_7_sr = go_Wall_24_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_7);

        // --- Wall_24_8 ---
        var go_Wall_24_8 = new GameObject("Wall_24_8");
        go_Wall_24_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_8.transform.position = new Vector3(-5.5f, -9.0f, 0.0f);
        var go_Wall_24_8_rb = go_Wall_24_8.AddComponent<Rigidbody2D>();
        go_Wall_24_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_8_bc = go_Wall_24_8.AddComponent<BoxCollider2D>();
        go_Wall_24_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_8_sr = go_Wall_24_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_8);

        // --- Pellet_24_9 ---
        var go_Pellet_24_9 = new GameObject("Pellet_24_9");
        go_Pellet_24_9.tag = "Pellet";
        go_Pellet_24_9.transform.position = new Vector3(-4.5f, -9.0f, 0.0f);
        var go_Pellet_24_9_rb = go_Pellet_24_9.AddComponent<Rigidbody2D>();
        go_Pellet_24_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_24_9_bc = go_Pellet_24_9.AddComponent<BoxCollider2D>();
        go_Pellet_24_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_24_9_bc.isTrigger = true;
        var go_Pellet_24_9_sr = go_Pellet_24_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_24_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_24_9_sr.sharedMaterial = unlitMat;
        go_Pellet_24_9_sr.sortingOrder = 2;
        go_Pellet_24_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_24_9);

        // --- Wall_24_10 ---
        var go_Wall_24_10 = new GameObject("Wall_24_10");
        go_Wall_24_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_10.transform.position = new Vector3(-3.5f, -9.0f, 0.0f);
        var go_Wall_24_10_rb = go_Wall_24_10.AddComponent<Rigidbody2D>();
        go_Wall_24_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_10_bc = go_Wall_24_10.AddComponent<BoxCollider2D>();
        go_Wall_24_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_10_sr = go_Wall_24_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_10);

        // --- Wall_24_11 ---
        var go_Wall_24_11 = new GameObject("Wall_24_11");
        go_Wall_24_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_11.transform.position = new Vector3(-2.5f, -9.0f, 0.0f);
        var go_Wall_24_11_rb = go_Wall_24_11.AddComponent<Rigidbody2D>();
        go_Wall_24_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_11_bc = go_Wall_24_11.AddComponent<BoxCollider2D>();
        go_Wall_24_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_11_sr = go_Wall_24_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_11);

        // --- Wall_24_12 ---
        var go_Wall_24_12 = new GameObject("Wall_24_12");
        go_Wall_24_12.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_12.transform.position = new Vector3(-1.5f, -9.0f, 0.0f);
        var go_Wall_24_12_rb = go_Wall_24_12.AddComponent<Rigidbody2D>();
        go_Wall_24_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_12_bc = go_Wall_24_12.AddComponent<BoxCollider2D>();
        go_Wall_24_12_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_12_sr = go_Wall_24_12.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_12_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_12_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_12);

        // --- Wall_24_13 ---
        var go_Wall_24_13 = new GameObject("Wall_24_13");
        go_Wall_24_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_13.transform.position = new Vector3(-0.5f, -9.0f, 0.0f);
        var go_Wall_24_13_rb = go_Wall_24_13.AddComponent<Rigidbody2D>();
        go_Wall_24_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_13_bc = go_Wall_24_13.AddComponent<BoxCollider2D>();
        go_Wall_24_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_13_sr = go_Wall_24_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_13);

        // --- Wall_24_14 ---
        var go_Wall_24_14 = new GameObject("Wall_24_14");
        go_Wall_24_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_14.transform.position = new Vector3(0.5f, -9.0f, 0.0f);
        var go_Wall_24_14_rb = go_Wall_24_14.AddComponent<Rigidbody2D>();
        go_Wall_24_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_14_bc = go_Wall_24_14.AddComponent<BoxCollider2D>();
        go_Wall_24_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_14_sr = go_Wall_24_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_14);

        // --- Wall_24_15 ---
        var go_Wall_24_15 = new GameObject("Wall_24_15");
        go_Wall_24_15.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_15.transform.position = new Vector3(1.5f, -9.0f, 0.0f);
        var go_Wall_24_15_rb = go_Wall_24_15.AddComponent<Rigidbody2D>();
        go_Wall_24_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_15_bc = go_Wall_24_15.AddComponent<BoxCollider2D>();
        go_Wall_24_15_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_15_sr = go_Wall_24_15.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_15_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_15_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_15);

        // --- Wall_24_16 ---
        var go_Wall_24_16 = new GameObject("Wall_24_16");
        go_Wall_24_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_16.transform.position = new Vector3(2.5f, -9.0f, 0.0f);
        var go_Wall_24_16_rb = go_Wall_24_16.AddComponent<Rigidbody2D>();
        go_Wall_24_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_16_bc = go_Wall_24_16.AddComponent<BoxCollider2D>();
        go_Wall_24_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_16_sr = go_Wall_24_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_16);

        // --- Wall_24_17 ---
        var go_Wall_24_17 = new GameObject("Wall_24_17");
        go_Wall_24_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_17.transform.position = new Vector3(3.5f, -9.0f, 0.0f);
        var go_Wall_24_17_rb = go_Wall_24_17.AddComponent<Rigidbody2D>();
        go_Wall_24_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_17_bc = go_Wall_24_17.AddComponent<BoxCollider2D>();
        go_Wall_24_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_17_sr = go_Wall_24_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_17);

        // --- Pellet_24_18 ---
        var go_Pellet_24_18 = new GameObject("Pellet_24_18");
        go_Pellet_24_18.tag = "Pellet";
        go_Pellet_24_18.transform.position = new Vector3(4.5f, -9.0f, 0.0f);
        var go_Pellet_24_18_rb = go_Pellet_24_18.AddComponent<Rigidbody2D>();
        go_Pellet_24_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_24_18_bc = go_Pellet_24_18.AddComponent<BoxCollider2D>();
        go_Pellet_24_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_24_18_bc.isTrigger = true;
        var go_Pellet_24_18_sr = go_Pellet_24_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_24_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_24_18_sr.sharedMaterial = unlitMat;
        go_Pellet_24_18_sr.sortingOrder = 2;
        go_Pellet_24_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_24_18);

        // --- Wall_24_19 ---
        var go_Wall_24_19 = new GameObject("Wall_24_19");
        go_Wall_24_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_19.transform.position = new Vector3(5.5f, -9.0f, 0.0f);
        var go_Wall_24_19_rb = go_Wall_24_19.AddComponent<Rigidbody2D>();
        go_Wall_24_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_19_bc = go_Wall_24_19.AddComponent<BoxCollider2D>();
        go_Wall_24_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_19_sr = go_Wall_24_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_19);

        // --- Wall_24_20 ---
        var go_Wall_24_20 = new GameObject("Wall_24_20");
        go_Wall_24_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_20.transform.position = new Vector3(6.5f, -9.0f, 0.0f);
        var go_Wall_24_20_rb = go_Wall_24_20.AddComponent<Rigidbody2D>();
        go_Wall_24_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_20_bc = go_Wall_24_20.AddComponent<BoxCollider2D>();
        go_Wall_24_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_20_sr = go_Wall_24_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_20);

        // --- Pellet_24_21 ---
        var go_Pellet_24_21 = new GameObject("Pellet_24_21");
        go_Pellet_24_21.tag = "Pellet";
        go_Pellet_24_21.transform.position = new Vector3(7.5f, -9.0f, 0.0f);
        var go_Pellet_24_21_rb = go_Pellet_24_21.AddComponent<Rigidbody2D>();
        go_Pellet_24_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_24_21_bc = go_Pellet_24_21.AddComponent<BoxCollider2D>();
        go_Pellet_24_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_24_21_bc.isTrigger = true;
        var go_Pellet_24_21_sr = go_Pellet_24_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_24_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_24_21_sr.sharedMaterial = unlitMat;
        go_Pellet_24_21_sr.sortingOrder = 2;
        go_Pellet_24_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_24_21);

        // --- Wall_24_22 ---
        var go_Wall_24_22 = new GameObject("Wall_24_22");
        go_Wall_24_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_22.transform.position = new Vector3(8.5f, -9.0f, 0.0f);
        var go_Wall_24_22_rb = go_Wall_24_22.AddComponent<Rigidbody2D>();
        go_Wall_24_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_22_bc = go_Wall_24_22.AddComponent<BoxCollider2D>();
        go_Wall_24_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_22_sr = go_Wall_24_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_22);

        // --- Wall_24_23 ---
        var go_Wall_24_23 = new GameObject("Wall_24_23");
        go_Wall_24_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_23.transform.position = new Vector3(9.5f, -9.0f, 0.0f);
        var go_Wall_24_23_rb = go_Wall_24_23.AddComponent<Rigidbody2D>();
        go_Wall_24_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_23_bc = go_Wall_24_23.AddComponent<BoxCollider2D>();
        go_Wall_24_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_23_sr = go_Wall_24_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_23);

        // --- Pellet_24_24 ---
        var go_Pellet_24_24 = new GameObject("Pellet_24_24");
        go_Pellet_24_24.tag = "Pellet";
        go_Pellet_24_24.transform.position = new Vector3(10.5f, -9.0f, 0.0f);
        var go_Pellet_24_24_rb = go_Pellet_24_24.AddComponent<Rigidbody2D>();
        go_Pellet_24_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_24_24_bc = go_Pellet_24_24.AddComponent<BoxCollider2D>();
        go_Pellet_24_24_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_24_24_bc.isTrigger = true;
        var go_Pellet_24_24_sr = go_Pellet_24_24.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_24_24_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_24_24_sr.sharedMaterial = unlitMat;
        go_Pellet_24_24_sr.sortingOrder = 2;
        go_Pellet_24_24.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_24_24);

        // --- Wall_24_25 ---
        var go_Wall_24_25 = new GameObject("Wall_24_25");
        go_Wall_24_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_25.transform.position = new Vector3(11.5f, -9.0f, 0.0f);
        var go_Wall_24_25_rb = go_Wall_24_25.AddComponent<Rigidbody2D>();
        go_Wall_24_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_25_bc = go_Wall_24_25.AddComponent<BoxCollider2D>();
        go_Wall_24_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_25_sr = go_Wall_24_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_25);

        // --- Wall_24_26 ---
        var go_Wall_24_26 = new GameObject("Wall_24_26");
        go_Wall_24_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_26.transform.position = new Vector3(12.5f, -9.0f, 0.0f);
        var go_Wall_24_26_rb = go_Wall_24_26.AddComponent<Rigidbody2D>();
        go_Wall_24_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_26_bc = go_Wall_24_26.AddComponent<BoxCollider2D>();
        go_Wall_24_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_26_sr = go_Wall_24_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_26);

        // --- Wall_24_27 ---
        var go_Wall_24_27 = new GameObject("Wall_24_27");
        go_Wall_24_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_24_27.transform.position = new Vector3(13.5f, -9.0f, 0.0f);
        var go_Wall_24_27_rb = go_Wall_24_27.AddComponent<Rigidbody2D>();
        go_Wall_24_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_24_27_bc = go_Wall_24_27.AddComponent<BoxCollider2D>();
        go_Wall_24_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_24_27_sr = go_Wall_24_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_24_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_24_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_24_27);

        // --- Wall_25_0 ---
        var go_Wall_25_0 = new GameObject("Wall_25_0");
        go_Wall_25_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_0.transform.position = new Vector3(-13.5f, -10.0f, 0.0f);
        var go_Wall_25_0_rb = go_Wall_25_0.AddComponent<Rigidbody2D>();
        go_Wall_25_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_0_bc = go_Wall_25_0.AddComponent<BoxCollider2D>();
        go_Wall_25_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_0_sr = go_Wall_25_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_0);

        // --- Wall_25_1 ---
        var go_Wall_25_1 = new GameObject("Wall_25_1");
        go_Wall_25_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_1.transform.position = new Vector3(-12.5f, -10.0f, 0.0f);
        var go_Wall_25_1_rb = go_Wall_25_1.AddComponent<Rigidbody2D>();
        go_Wall_25_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_1_bc = go_Wall_25_1.AddComponent<BoxCollider2D>();
        go_Wall_25_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_1_sr = go_Wall_25_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_1);

        // --- Wall_25_2 ---
        var go_Wall_25_2 = new GameObject("Wall_25_2");
        go_Wall_25_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_2.transform.position = new Vector3(-11.5f, -10.0f, 0.0f);
        var go_Wall_25_2_rb = go_Wall_25_2.AddComponent<Rigidbody2D>();
        go_Wall_25_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_2_bc = go_Wall_25_2.AddComponent<BoxCollider2D>();
        go_Wall_25_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_2_sr = go_Wall_25_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_2);

        // --- Pellet_25_3 ---
        var go_Pellet_25_3 = new GameObject("Pellet_25_3");
        go_Pellet_25_3.tag = "Pellet";
        go_Pellet_25_3.transform.position = new Vector3(-10.5f, -10.0f, 0.0f);
        var go_Pellet_25_3_rb = go_Pellet_25_3.AddComponent<Rigidbody2D>();
        go_Pellet_25_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_25_3_bc = go_Pellet_25_3.AddComponent<BoxCollider2D>();
        go_Pellet_25_3_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_25_3_bc.isTrigger = true;
        var go_Pellet_25_3_sr = go_Pellet_25_3.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_25_3_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_25_3_sr.sharedMaterial = unlitMat;
        go_Pellet_25_3_sr.sortingOrder = 2;
        go_Pellet_25_3.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_25_3);

        // --- Wall_25_4 ---
        var go_Wall_25_4 = new GameObject("Wall_25_4");
        go_Wall_25_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_4.transform.position = new Vector3(-9.5f, -10.0f, 0.0f);
        var go_Wall_25_4_rb = go_Wall_25_4.AddComponent<Rigidbody2D>();
        go_Wall_25_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_4_bc = go_Wall_25_4.AddComponent<BoxCollider2D>();
        go_Wall_25_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_4_sr = go_Wall_25_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_4);

        // --- Wall_25_5 ---
        var go_Wall_25_5 = new GameObject("Wall_25_5");
        go_Wall_25_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_5.transform.position = new Vector3(-8.5f, -10.0f, 0.0f);
        var go_Wall_25_5_rb = go_Wall_25_5.AddComponent<Rigidbody2D>();
        go_Wall_25_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_5_bc = go_Wall_25_5.AddComponent<BoxCollider2D>();
        go_Wall_25_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_5_sr = go_Wall_25_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_5);

        // --- Pellet_25_6 ---
        var go_Pellet_25_6 = new GameObject("Pellet_25_6");
        go_Pellet_25_6.tag = "Pellet";
        go_Pellet_25_6.transform.position = new Vector3(-7.5f, -10.0f, 0.0f);
        var go_Pellet_25_6_rb = go_Pellet_25_6.AddComponent<Rigidbody2D>();
        go_Pellet_25_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_25_6_bc = go_Pellet_25_6.AddComponent<BoxCollider2D>();
        go_Pellet_25_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_25_6_bc.isTrigger = true;
        var go_Pellet_25_6_sr = go_Pellet_25_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_25_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_25_6_sr.sharedMaterial = unlitMat;
        go_Pellet_25_6_sr.sortingOrder = 2;
        go_Pellet_25_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_25_6);

        // --- Wall_25_7 ---
        var go_Wall_25_7 = new GameObject("Wall_25_7");
        go_Wall_25_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_7.transform.position = new Vector3(-6.5f, -10.0f, 0.0f);
        var go_Wall_25_7_rb = go_Wall_25_7.AddComponent<Rigidbody2D>();
        go_Wall_25_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_7_bc = go_Wall_25_7.AddComponent<BoxCollider2D>();
        go_Wall_25_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_7_sr = go_Wall_25_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_7);

        // --- Wall_25_8 ---
        var go_Wall_25_8 = new GameObject("Wall_25_8");
        go_Wall_25_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_8.transform.position = new Vector3(-5.5f, -10.0f, 0.0f);
        var go_Wall_25_8_rb = go_Wall_25_8.AddComponent<Rigidbody2D>();
        go_Wall_25_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_8_bc = go_Wall_25_8.AddComponent<BoxCollider2D>();
        go_Wall_25_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_8_sr = go_Wall_25_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_8);

        // --- Pellet_25_9 ---
        var go_Pellet_25_9 = new GameObject("Pellet_25_9");
        go_Pellet_25_9.tag = "Pellet";
        go_Pellet_25_9.transform.position = new Vector3(-4.5f, -10.0f, 0.0f);
        var go_Pellet_25_9_rb = go_Pellet_25_9.AddComponent<Rigidbody2D>();
        go_Pellet_25_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_25_9_bc = go_Pellet_25_9.AddComponent<BoxCollider2D>();
        go_Pellet_25_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_25_9_bc.isTrigger = true;
        var go_Pellet_25_9_sr = go_Pellet_25_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_25_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_25_9_sr.sharedMaterial = unlitMat;
        go_Pellet_25_9_sr.sortingOrder = 2;
        go_Pellet_25_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_25_9);

        // --- Wall_25_10 ---
        var go_Wall_25_10 = new GameObject("Wall_25_10");
        go_Wall_25_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_10.transform.position = new Vector3(-3.5f, -10.0f, 0.0f);
        var go_Wall_25_10_rb = go_Wall_25_10.AddComponent<Rigidbody2D>();
        go_Wall_25_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_10_bc = go_Wall_25_10.AddComponent<BoxCollider2D>();
        go_Wall_25_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_10_sr = go_Wall_25_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_10);

        // --- Wall_25_11 ---
        var go_Wall_25_11 = new GameObject("Wall_25_11");
        go_Wall_25_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_11.transform.position = new Vector3(-2.5f, -10.0f, 0.0f);
        var go_Wall_25_11_rb = go_Wall_25_11.AddComponent<Rigidbody2D>();
        go_Wall_25_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_11_bc = go_Wall_25_11.AddComponent<BoxCollider2D>();
        go_Wall_25_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_11_sr = go_Wall_25_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_11);

        // --- Wall_25_12 ---
        var go_Wall_25_12 = new GameObject("Wall_25_12");
        go_Wall_25_12.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_12.transform.position = new Vector3(-1.5f, -10.0f, 0.0f);
        var go_Wall_25_12_rb = go_Wall_25_12.AddComponent<Rigidbody2D>();
        go_Wall_25_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_12_bc = go_Wall_25_12.AddComponent<BoxCollider2D>();
        go_Wall_25_12_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_12_sr = go_Wall_25_12.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_12_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_12_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_12);

        // --- Wall_25_13 ---
        var go_Wall_25_13 = new GameObject("Wall_25_13");
        go_Wall_25_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_13.transform.position = new Vector3(-0.5f, -10.0f, 0.0f);
        var go_Wall_25_13_rb = go_Wall_25_13.AddComponent<Rigidbody2D>();
        go_Wall_25_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_13_bc = go_Wall_25_13.AddComponent<BoxCollider2D>();
        go_Wall_25_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_13_sr = go_Wall_25_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_13);

        // --- Wall_25_14 ---
        var go_Wall_25_14 = new GameObject("Wall_25_14");
        go_Wall_25_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_14.transform.position = new Vector3(0.5f, -10.0f, 0.0f);
        var go_Wall_25_14_rb = go_Wall_25_14.AddComponent<Rigidbody2D>();
        go_Wall_25_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_14_bc = go_Wall_25_14.AddComponent<BoxCollider2D>();
        go_Wall_25_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_14_sr = go_Wall_25_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_14);

        // --- Wall_25_15 ---
        var go_Wall_25_15 = new GameObject("Wall_25_15");
        go_Wall_25_15.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_15.transform.position = new Vector3(1.5f, -10.0f, 0.0f);
        var go_Wall_25_15_rb = go_Wall_25_15.AddComponent<Rigidbody2D>();
        go_Wall_25_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_15_bc = go_Wall_25_15.AddComponent<BoxCollider2D>();
        go_Wall_25_15_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_15_sr = go_Wall_25_15.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_15_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_15_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_15);

        // --- Wall_25_16 ---
        var go_Wall_25_16 = new GameObject("Wall_25_16");
        go_Wall_25_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_16.transform.position = new Vector3(2.5f, -10.0f, 0.0f);
        var go_Wall_25_16_rb = go_Wall_25_16.AddComponent<Rigidbody2D>();
        go_Wall_25_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_16_bc = go_Wall_25_16.AddComponent<BoxCollider2D>();
        go_Wall_25_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_16_sr = go_Wall_25_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_16);

        // --- Wall_25_17 ---
        var go_Wall_25_17 = new GameObject("Wall_25_17");
        go_Wall_25_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_17.transform.position = new Vector3(3.5f, -10.0f, 0.0f);
        var go_Wall_25_17_rb = go_Wall_25_17.AddComponent<Rigidbody2D>();
        go_Wall_25_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_17_bc = go_Wall_25_17.AddComponent<BoxCollider2D>();
        go_Wall_25_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_17_sr = go_Wall_25_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_17);

        // --- Pellet_25_18 ---
        var go_Pellet_25_18 = new GameObject("Pellet_25_18");
        go_Pellet_25_18.tag = "Pellet";
        go_Pellet_25_18.transform.position = new Vector3(4.5f, -10.0f, 0.0f);
        var go_Pellet_25_18_rb = go_Pellet_25_18.AddComponent<Rigidbody2D>();
        go_Pellet_25_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_25_18_bc = go_Pellet_25_18.AddComponent<BoxCollider2D>();
        go_Pellet_25_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_25_18_bc.isTrigger = true;
        var go_Pellet_25_18_sr = go_Pellet_25_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_25_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_25_18_sr.sharedMaterial = unlitMat;
        go_Pellet_25_18_sr.sortingOrder = 2;
        go_Pellet_25_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_25_18);

        // --- Wall_25_19 ---
        var go_Wall_25_19 = new GameObject("Wall_25_19");
        go_Wall_25_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_19.transform.position = new Vector3(5.5f, -10.0f, 0.0f);
        var go_Wall_25_19_rb = go_Wall_25_19.AddComponent<Rigidbody2D>();
        go_Wall_25_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_19_bc = go_Wall_25_19.AddComponent<BoxCollider2D>();
        go_Wall_25_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_19_sr = go_Wall_25_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_19);

        // --- Wall_25_20 ---
        var go_Wall_25_20 = new GameObject("Wall_25_20");
        go_Wall_25_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_20.transform.position = new Vector3(6.5f, -10.0f, 0.0f);
        var go_Wall_25_20_rb = go_Wall_25_20.AddComponent<Rigidbody2D>();
        go_Wall_25_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_20_bc = go_Wall_25_20.AddComponent<BoxCollider2D>();
        go_Wall_25_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_20_sr = go_Wall_25_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_20);

        // --- Pellet_25_21 ---
        var go_Pellet_25_21 = new GameObject("Pellet_25_21");
        go_Pellet_25_21.tag = "Pellet";
        go_Pellet_25_21.transform.position = new Vector3(7.5f, -10.0f, 0.0f);
        var go_Pellet_25_21_rb = go_Pellet_25_21.AddComponent<Rigidbody2D>();
        go_Pellet_25_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_25_21_bc = go_Pellet_25_21.AddComponent<BoxCollider2D>();
        go_Pellet_25_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_25_21_bc.isTrigger = true;
        var go_Pellet_25_21_sr = go_Pellet_25_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_25_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_25_21_sr.sharedMaterial = unlitMat;
        go_Pellet_25_21_sr.sortingOrder = 2;
        go_Pellet_25_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_25_21);

        // --- Wall_25_22 ---
        var go_Wall_25_22 = new GameObject("Wall_25_22");
        go_Wall_25_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_22.transform.position = new Vector3(8.5f, -10.0f, 0.0f);
        var go_Wall_25_22_rb = go_Wall_25_22.AddComponent<Rigidbody2D>();
        go_Wall_25_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_22_bc = go_Wall_25_22.AddComponent<BoxCollider2D>();
        go_Wall_25_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_22_sr = go_Wall_25_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_22);

        // --- Wall_25_23 ---
        var go_Wall_25_23 = new GameObject("Wall_25_23");
        go_Wall_25_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_23.transform.position = new Vector3(9.5f, -10.0f, 0.0f);
        var go_Wall_25_23_rb = go_Wall_25_23.AddComponent<Rigidbody2D>();
        go_Wall_25_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_23_bc = go_Wall_25_23.AddComponent<BoxCollider2D>();
        go_Wall_25_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_23_sr = go_Wall_25_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_23);

        // --- Pellet_25_24 ---
        var go_Pellet_25_24 = new GameObject("Pellet_25_24");
        go_Pellet_25_24.tag = "Pellet";
        go_Pellet_25_24.transform.position = new Vector3(10.5f, -10.0f, 0.0f);
        var go_Pellet_25_24_rb = go_Pellet_25_24.AddComponent<Rigidbody2D>();
        go_Pellet_25_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_25_24_bc = go_Pellet_25_24.AddComponent<BoxCollider2D>();
        go_Pellet_25_24_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_25_24_bc.isTrigger = true;
        var go_Pellet_25_24_sr = go_Pellet_25_24.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_25_24_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_25_24_sr.sharedMaterial = unlitMat;
        go_Pellet_25_24_sr.sortingOrder = 2;
        go_Pellet_25_24.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_25_24);

        // --- Wall_25_25 ---
        var go_Wall_25_25 = new GameObject("Wall_25_25");
        go_Wall_25_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_25.transform.position = new Vector3(11.5f, -10.0f, 0.0f);
        var go_Wall_25_25_rb = go_Wall_25_25.AddComponent<Rigidbody2D>();
        go_Wall_25_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_25_bc = go_Wall_25_25.AddComponent<BoxCollider2D>();
        go_Wall_25_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_25_sr = go_Wall_25_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_25);

        // --- Wall_25_26 ---
        var go_Wall_25_26 = new GameObject("Wall_25_26");
        go_Wall_25_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_26.transform.position = new Vector3(12.5f, -10.0f, 0.0f);
        var go_Wall_25_26_rb = go_Wall_25_26.AddComponent<Rigidbody2D>();
        go_Wall_25_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_26_bc = go_Wall_25_26.AddComponent<BoxCollider2D>();
        go_Wall_25_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_26_sr = go_Wall_25_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_26);

        // --- Wall_25_27 ---
        var go_Wall_25_27 = new GameObject("Wall_25_27");
        go_Wall_25_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_25_27.transform.position = new Vector3(13.5f, -10.0f, 0.0f);
        var go_Wall_25_27_rb = go_Wall_25_27.AddComponent<Rigidbody2D>();
        go_Wall_25_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_25_27_bc = go_Wall_25_27.AddComponent<BoxCollider2D>();
        go_Wall_25_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_25_27_sr = go_Wall_25_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_25_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_25_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_25_27);

        // --- Wall_26_0 ---
        var go_Wall_26_0 = new GameObject("Wall_26_0");
        go_Wall_26_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_26_0.transform.position = new Vector3(-13.5f, -11.0f, 0.0f);
        var go_Wall_26_0_rb = go_Wall_26_0.AddComponent<Rigidbody2D>();
        go_Wall_26_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_26_0_bc = go_Wall_26_0.AddComponent<BoxCollider2D>();
        go_Wall_26_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_26_0_sr = go_Wall_26_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_26_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_26_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_26_0);

        // --- Pellet_26_1 ---
        var go_Pellet_26_1 = new GameObject("Pellet_26_1");
        go_Pellet_26_1.tag = "Pellet";
        go_Pellet_26_1.transform.position = new Vector3(-12.5f, -11.0f, 0.0f);
        var go_Pellet_26_1_rb = go_Pellet_26_1.AddComponent<Rigidbody2D>();
        go_Pellet_26_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_1_bc = go_Pellet_26_1.AddComponent<BoxCollider2D>();
        go_Pellet_26_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_1_bc.isTrigger = true;
        var go_Pellet_26_1_sr = go_Pellet_26_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_1_sr.sharedMaterial = unlitMat;
        go_Pellet_26_1_sr.sortingOrder = 2;
        go_Pellet_26_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_1);

        // --- Node_26_1 ---
        var go_Node_26_1 = new GameObject("Node_26_1");
        go_Node_26_1.transform.position = new Vector3(-12.5f, -11.0f, 0.0f);
        var go_Node_26_1_rb = go_Node_26_1.AddComponent<Rigidbody2D>();
        go_Node_26_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_26_1_bc = go_Node_26_1.AddComponent<BoxCollider2D>();
        go_Node_26_1_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_26_1_bc.isTrigger = true;
        go_Node_26_1.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_26_1);

        // --- Pellet_26_2 ---
        var go_Pellet_26_2 = new GameObject("Pellet_26_2");
        go_Pellet_26_2.tag = "Pellet";
        go_Pellet_26_2.transform.position = new Vector3(-11.5f, -11.0f, 0.0f);
        var go_Pellet_26_2_rb = go_Pellet_26_2.AddComponent<Rigidbody2D>();
        go_Pellet_26_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_2_bc = go_Pellet_26_2.AddComponent<BoxCollider2D>();
        go_Pellet_26_2_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_2_bc.isTrigger = true;
        var go_Pellet_26_2_sr = go_Pellet_26_2.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_2_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_2_sr.sharedMaterial = unlitMat;
        go_Pellet_26_2_sr.sortingOrder = 2;
        go_Pellet_26_2.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_2);

        // --- Pellet_26_3 ---
        var go_Pellet_26_3 = new GameObject("Pellet_26_3");
        go_Pellet_26_3.tag = "Pellet";
        go_Pellet_26_3.transform.position = new Vector3(-10.5f, -11.0f, 0.0f);
        var go_Pellet_26_3_rb = go_Pellet_26_3.AddComponent<Rigidbody2D>();
        go_Pellet_26_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_3_bc = go_Pellet_26_3.AddComponent<BoxCollider2D>();
        go_Pellet_26_3_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_3_bc.isTrigger = true;
        var go_Pellet_26_3_sr = go_Pellet_26_3.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_3_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_3_sr.sharedMaterial = unlitMat;
        go_Pellet_26_3_sr.sortingOrder = 2;
        go_Pellet_26_3.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_3);

        // --- Node_26_3 ---
        var go_Node_26_3 = new GameObject("Node_26_3");
        go_Node_26_3.transform.position = new Vector3(-10.5f, -11.0f, 0.0f);
        var go_Node_26_3_rb = go_Node_26_3.AddComponent<Rigidbody2D>();
        go_Node_26_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_26_3_bc = go_Node_26_3.AddComponent<BoxCollider2D>();
        go_Node_26_3_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_26_3_bc.isTrigger = true;
        go_Node_26_3.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_26_3);

        // --- Pellet_26_4 ---
        var go_Pellet_26_4 = new GameObject("Pellet_26_4");
        go_Pellet_26_4.tag = "Pellet";
        go_Pellet_26_4.transform.position = new Vector3(-9.5f, -11.0f, 0.0f);
        var go_Pellet_26_4_rb = go_Pellet_26_4.AddComponent<Rigidbody2D>();
        go_Pellet_26_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_4_bc = go_Pellet_26_4.AddComponent<BoxCollider2D>();
        go_Pellet_26_4_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_4_bc.isTrigger = true;
        var go_Pellet_26_4_sr = go_Pellet_26_4.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_4_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_4_sr.sharedMaterial = unlitMat;
        go_Pellet_26_4_sr.sortingOrder = 2;
        go_Pellet_26_4.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_4);

        // --- Pellet_26_5 ---
        var go_Pellet_26_5 = new GameObject("Pellet_26_5");
        go_Pellet_26_5.tag = "Pellet";
        go_Pellet_26_5.transform.position = new Vector3(-8.5f, -11.0f, 0.0f);
        var go_Pellet_26_5_rb = go_Pellet_26_5.AddComponent<Rigidbody2D>();
        go_Pellet_26_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_5_bc = go_Pellet_26_5.AddComponent<BoxCollider2D>();
        go_Pellet_26_5_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_5_bc.isTrigger = true;
        var go_Pellet_26_5_sr = go_Pellet_26_5.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_5_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_5_sr.sharedMaterial = unlitMat;
        go_Pellet_26_5_sr.sortingOrder = 2;
        go_Pellet_26_5.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_5);

        // --- Pellet_26_6 ---
        var go_Pellet_26_6 = new GameObject("Pellet_26_6");
        go_Pellet_26_6.tag = "Pellet";
        go_Pellet_26_6.transform.position = new Vector3(-7.5f, -11.0f, 0.0f);
        var go_Pellet_26_6_rb = go_Pellet_26_6.AddComponent<Rigidbody2D>();
        go_Pellet_26_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_6_bc = go_Pellet_26_6.AddComponent<BoxCollider2D>();
        go_Pellet_26_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_6_bc.isTrigger = true;
        var go_Pellet_26_6_sr = go_Pellet_26_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_6_sr.sharedMaterial = unlitMat;
        go_Pellet_26_6_sr.sortingOrder = 2;
        go_Pellet_26_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_6);

        // --- Node_26_6 ---
        var go_Node_26_6 = new GameObject("Node_26_6");
        go_Node_26_6.transform.position = new Vector3(-7.5f, -11.0f, 0.0f);
        var go_Node_26_6_rb = go_Node_26_6.AddComponent<Rigidbody2D>();
        go_Node_26_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_26_6_bc = go_Node_26_6.AddComponent<BoxCollider2D>();
        go_Node_26_6_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_26_6_bc.isTrigger = true;
        go_Node_26_6.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_26_6);

        // --- Wall_26_7 ---
        var go_Wall_26_7 = new GameObject("Wall_26_7");
        go_Wall_26_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_26_7.transform.position = new Vector3(-6.5f, -11.0f, 0.0f);
        var go_Wall_26_7_rb = go_Wall_26_7.AddComponent<Rigidbody2D>();
        go_Wall_26_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_26_7_bc = go_Wall_26_7.AddComponent<BoxCollider2D>();
        go_Wall_26_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_26_7_sr = go_Wall_26_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_26_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_26_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_26_7);

        // --- Wall_26_8 ---
        var go_Wall_26_8 = new GameObject("Wall_26_8");
        go_Wall_26_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_26_8.transform.position = new Vector3(-5.5f, -11.0f, 0.0f);
        var go_Wall_26_8_rb = go_Wall_26_8.AddComponent<Rigidbody2D>();
        go_Wall_26_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_26_8_bc = go_Wall_26_8.AddComponent<BoxCollider2D>();
        go_Wall_26_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_26_8_sr = go_Wall_26_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_26_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_26_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_26_8);

        // --- Pellet_26_9 ---
        var go_Pellet_26_9 = new GameObject("Pellet_26_9");
        go_Pellet_26_9.tag = "Pellet";
        go_Pellet_26_9.transform.position = new Vector3(-4.5f, -11.0f, 0.0f);
        var go_Pellet_26_9_rb = go_Pellet_26_9.AddComponent<Rigidbody2D>();
        go_Pellet_26_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_9_bc = go_Pellet_26_9.AddComponent<BoxCollider2D>();
        go_Pellet_26_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_9_bc.isTrigger = true;
        var go_Pellet_26_9_sr = go_Pellet_26_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_9_sr.sharedMaterial = unlitMat;
        go_Pellet_26_9_sr.sortingOrder = 2;
        go_Pellet_26_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_9);

        // --- Node_26_9 ---
        var go_Node_26_9 = new GameObject("Node_26_9");
        go_Node_26_9.transform.position = new Vector3(-4.5f, -11.0f, 0.0f);
        var go_Node_26_9_rb = go_Node_26_9.AddComponent<Rigidbody2D>();
        go_Node_26_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_26_9_bc = go_Node_26_9.AddComponent<BoxCollider2D>();
        go_Node_26_9_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_26_9_bc.isTrigger = true;
        go_Node_26_9.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_26_9);

        // --- Pellet_26_10 ---
        var go_Pellet_26_10 = new GameObject("Pellet_26_10");
        go_Pellet_26_10.tag = "Pellet";
        go_Pellet_26_10.transform.position = new Vector3(-3.5f, -11.0f, 0.0f);
        var go_Pellet_26_10_rb = go_Pellet_26_10.AddComponent<Rigidbody2D>();
        go_Pellet_26_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_10_bc = go_Pellet_26_10.AddComponent<BoxCollider2D>();
        go_Pellet_26_10_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_10_bc.isTrigger = true;
        var go_Pellet_26_10_sr = go_Pellet_26_10.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_10_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_10_sr.sharedMaterial = unlitMat;
        go_Pellet_26_10_sr.sortingOrder = 2;
        go_Pellet_26_10.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_10);

        // --- Pellet_26_11 ---
        var go_Pellet_26_11 = new GameObject("Pellet_26_11");
        go_Pellet_26_11.tag = "Pellet";
        go_Pellet_26_11.transform.position = new Vector3(-2.5f, -11.0f, 0.0f);
        var go_Pellet_26_11_rb = go_Pellet_26_11.AddComponent<Rigidbody2D>();
        go_Pellet_26_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_11_bc = go_Pellet_26_11.AddComponent<BoxCollider2D>();
        go_Pellet_26_11_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_11_bc.isTrigger = true;
        var go_Pellet_26_11_sr = go_Pellet_26_11.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_11_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_11_sr.sharedMaterial = unlitMat;
        go_Pellet_26_11_sr.sortingOrder = 2;
        go_Pellet_26_11.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_11);

        // --- Pellet_26_12 ---
        var go_Pellet_26_12 = new GameObject("Pellet_26_12");
        go_Pellet_26_12.tag = "Pellet";
        go_Pellet_26_12.transform.position = new Vector3(-1.5f, -11.0f, 0.0f);
        var go_Pellet_26_12_rb = go_Pellet_26_12.AddComponent<Rigidbody2D>();
        go_Pellet_26_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_12_bc = go_Pellet_26_12.AddComponent<BoxCollider2D>();
        go_Pellet_26_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_12_bc.isTrigger = true;
        var go_Pellet_26_12_sr = go_Pellet_26_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_12_sr.sharedMaterial = unlitMat;
        go_Pellet_26_12_sr.sortingOrder = 2;
        go_Pellet_26_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_12);

        // --- Node_26_12 ---
        var go_Node_26_12 = new GameObject("Node_26_12");
        go_Node_26_12.transform.position = new Vector3(-1.5f, -11.0f, 0.0f);
        var go_Node_26_12_rb = go_Node_26_12.AddComponent<Rigidbody2D>();
        go_Node_26_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_26_12_bc = go_Node_26_12.AddComponent<BoxCollider2D>();
        go_Node_26_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_26_12_bc.isTrigger = true;
        go_Node_26_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_26_12);

        // --- Wall_26_13 ---
        var go_Wall_26_13 = new GameObject("Wall_26_13");
        go_Wall_26_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_26_13.transform.position = new Vector3(-0.5f, -11.0f, 0.0f);
        var go_Wall_26_13_rb = go_Wall_26_13.AddComponent<Rigidbody2D>();
        go_Wall_26_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_26_13_bc = go_Wall_26_13.AddComponent<BoxCollider2D>();
        go_Wall_26_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_26_13_sr = go_Wall_26_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_26_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_26_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_26_13);

        // --- Wall_26_14 ---
        var go_Wall_26_14 = new GameObject("Wall_26_14");
        go_Wall_26_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_26_14.transform.position = new Vector3(0.5f, -11.0f, 0.0f);
        var go_Wall_26_14_rb = go_Wall_26_14.AddComponent<Rigidbody2D>();
        go_Wall_26_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_26_14_bc = go_Wall_26_14.AddComponent<BoxCollider2D>();
        go_Wall_26_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_26_14_sr = go_Wall_26_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_26_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_26_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_26_14);

        // --- Pellet_26_15 ---
        var go_Pellet_26_15 = new GameObject("Pellet_26_15");
        go_Pellet_26_15.tag = "Pellet";
        go_Pellet_26_15.transform.position = new Vector3(1.5f, -11.0f, 0.0f);
        var go_Pellet_26_15_rb = go_Pellet_26_15.AddComponent<Rigidbody2D>();
        go_Pellet_26_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_15_bc = go_Pellet_26_15.AddComponent<BoxCollider2D>();
        go_Pellet_26_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_15_bc.isTrigger = true;
        var go_Pellet_26_15_sr = go_Pellet_26_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_15_sr.sharedMaterial = unlitMat;
        go_Pellet_26_15_sr.sortingOrder = 2;
        go_Pellet_26_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_15);

        // --- Node_26_15 ---
        var go_Node_26_15 = new GameObject("Node_26_15");
        go_Node_26_15.transform.position = new Vector3(1.5f, -11.0f, 0.0f);
        var go_Node_26_15_rb = go_Node_26_15.AddComponent<Rigidbody2D>();
        go_Node_26_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_26_15_bc = go_Node_26_15.AddComponent<BoxCollider2D>();
        go_Node_26_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_26_15_bc.isTrigger = true;
        go_Node_26_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_26_15);

        // --- Pellet_26_16 ---
        var go_Pellet_26_16 = new GameObject("Pellet_26_16");
        go_Pellet_26_16.tag = "Pellet";
        go_Pellet_26_16.transform.position = new Vector3(2.5f, -11.0f, 0.0f);
        var go_Pellet_26_16_rb = go_Pellet_26_16.AddComponent<Rigidbody2D>();
        go_Pellet_26_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_16_bc = go_Pellet_26_16.AddComponent<BoxCollider2D>();
        go_Pellet_26_16_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_16_bc.isTrigger = true;
        var go_Pellet_26_16_sr = go_Pellet_26_16.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_16_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_16_sr.sharedMaterial = unlitMat;
        go_Pellet_26_16_sr.sortingOrder = 2;
        go_Pellet_26_16.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_16);

        // --- Pellet_26_17 ---
        var go_Pellet_26_17 = new GameObject("Pellet_26_17");
        go_Pellet_26_17.tag = "Pellet";
        go_Pellet_26_17.transform.position = new Vector3(3.5f, -11.0f, 0.0f);
        var go_Pellet_26_17_rb = go_Pellet_26_17.AddComponent<Rigidbody2D>();
        go_Pellet_26_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_17_bc = go_Pellet_26_17.AddComponent<BoxCollider2D>();
        go_Pellet_26_17_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_17_bc.isTrigger = true;
        var go_Pellet_26_17_sr = go_Pellet_26_17.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_17_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_17_sr.sharedMaterial = unlitMat;
        go_Pellet_26_17_sr.sortingOrder = 2;
        go_Pellet_26_17.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_17);

        // --- Pellet_26_18 ---
        var go_Pellet_26_18 = new GameObject("Pellet_26_18");
        go_Pellet_26_18.tag = "Pellet";
        go_Pellet_26_18.transform.position = new Vector3(4.5f, -11.0f, 0.0f);
        var go_Pellet_26_18_rb = go_Pellet_26_18.AddComponent<Rigidbody2D>();
        go_Pellet_26_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_18_bc = go_Pellet_26_18.AddComponent<BoxCollider2D>();
        go_Pellet_26_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_18_bc.isTrigger = true;
        var go_Pellet_26_18_sr = go_Pellet_26_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_18_sr.sharedMaterial = unlitMat;
        go_Pellet_26_18_sr.sortingOrder = 2;
        go_Pellet_26_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_18);

        // --- Node_26_18 ---
        var go_Node_26_18 = new GameObject("Node_26_18");
        go_Node_26_18.transform.position = new Vector3(4.5f, -11.0f, 0.0f);
        var go_Node_26_18_rb = go_Node_26_18.AddComponent<Rigidbody2D>();
        go_Node_26_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_26_18_bc = go_Node_26_18.AddComponent<BoxCollider2D>();
        go_Node_26_18_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_26_18_bc.isTrigger = true;
        go_Node_26_18.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_26_18);

        // --- Wall_26_19 ---
        var go_Wall_26_19 = new GameObject("Wall_26_19");
        go_Wall_26_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_26_19.transform.position = new Vector3(5.5f, -11.0f, 0.0f);
        var go_Wall_26_19_rb = go_Wall_26_19.AddComponent<Rigidbody2D>();
        go_Wall_26_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_26_19_bc = go_Wall_26_19.AddComponent<BoxCollider2D>();
        go_Wall_26_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_26_19_sr = go_Wall_26_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_26_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_26_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_26_19);

        // --- Wall_26_20 ---
        var go_Wall_26_20 = new GameObject("Wall_26_20");
        go_Wall_26_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_26_20.transform.position = new Vector3(6.5f, -11.0f, 0.0f);
        var go_Wall_26_20_rb = go_Wall_26_20.AddComponent<Rigidbody2D>();
        go_Wall_26_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_26_20_bc = go_Wall_26_20.AddComponent<BoxCollider2D>();
        go_Wall_26_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_26_20_sr = go_Wall_26_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_26_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_26_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_26_20);

        // --- Pellet_26_21 ---
        var go_Pellet_26_21 = new GameObject("Pellet_26_21");
        go_Pellet_26_21.tag = "Pellet";
        go_Pellet_26_21.transform.position = new Vector3(7.5f, -11.0f, 0.0f);
        var go_Pellet_26_21_rb = go_Pellet_26_21.AddComponent<Rigidbody2D>();
        go_Pellet_26_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_21_bc = go_Pellet_26_21.AddComponent<BoxCollider2D>();
        go_Pellet_26_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_21_bc.isTrigger = true;
        var go_Pellet_26_21_sr = go_Pellet_26_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_21_sr.sharedMaterial = unlitMat;
        go_Pellet_26_21_sr.sortingOrder = 2;
        go_Pellet_26_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_21);

        // --- Node_26_21 ---
        var go_Node_26_21 = new GameObject("Node_26_21");
        go_Node_26_21.transform.position = new Vector3(7.5f, -11.0f, 0.0f);
        var go_Node_26_21_rb = go_Node_26_21.AddComponent<Rigidbody2D>();
        go_Node_26_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_26_21_bc = go_Node_26_21.AddComponent<BoxCollider2D>();
        go_Node_26_21_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_26_21_bc.isTrigger = true;
        go_Node_26_21.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_26_21);

        // --- Pellet_26_22 ---
        var go_Pellet_26_22 = new GameObject("Pellet_26_22");
        go_Pellet_26_22.tag = "Pellet";
        go_Pellet_26_22.transform.position = new Vector3(8.5f, -11.0f, 0.0f);
        var go_Pellet_26_22_rb = go_Pellet_26_22.AddComponent<Rigidbody2D>();
        go_Pellet_26_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_22_bc = go_Pellet_26_22.AddComponent<BoxCollider2D>();
        go_Pellet_26_22_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_22_bc.isTrigger = true;
        var go_Pellet_26_22_sr = go_Pellet_26_22.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_22_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_22_sr.sharedMaterial = unlitMat;
        go_Pellet_26_22_sr.sortingOrder = 2;
        go_Pellet_26_22.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_22);

        // --- Pellet_26_23 ---
        var go_Pellet_26_23 = new GameObject("Pellet_26_23");
        go_Pellet_26_23.tag = "Pellet";
        go_Pellet_26_23.transform.position = new Vector3(9.5f, -11.0f, 0.0f);
        var go_Pellet_26_23_rb = go_Pellet_26_23.AddComponent<Rigidbody2D>();
        go_Pellet_26_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_23_bc = go_Pellet_26_23.AddComponent<BoxCollider2D>();
        go_Pellet_26_23_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_23_bc.isTrigger = true;
        var go_Pellet_26_23_sr = go_Pellet_26_23.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_23_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_23_sr.sharedMaterial = unlitMat;
        go_Pellet_26_23_sr.sortingOrder = 2;
        go_Pellet_26_23.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_23);

        // --- Pellet_26_24 ---
        var go_Pellet_26_24 = new GameObject("Pellet_26_24");
        go_Pellet_26_24.tag = "Pellet";
        go_Pellet_26_24.transform.position = new Vector3(10.5f, -11.0f, 0.0f);
        var go_Pellet_26_24_rb = go_Pellet_26_24.AddComponent<Rigidbody2D>();
        go_Pellet_26_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_24_bc = go_Pellet_26_24.AddComponent<BoxCollider2D>();
        go_Pellet_26_24_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_24_bc.isTrigger = true;
        var go_Pellet_26_24_sr = go_Pellet_26_24.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_24_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_24_sr.sharedMaterial = unlitMat;
        go_Pellet_26_24_sr.sortingOrder = 2;
        go_Pellet_26_24.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_24);

        // --- Node_26_24 ---
        var go_Node_26_24 = new GameObject("Node_26_24");
        go_Node_26_24.transform.position = new Vector3(10.5f, -11.0f, 0.0f);
        var go_Node_26_24_rb = go_Node_26_24.AddComponent<Rigidbody2D>();
        go_Node_26_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_26_24_bc = go_Node_26_24.AddComponent<BoxCollider2D>();
        go_Node_26_24_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_26_24_bc.isTrigger = true;
        go_Node_26_24.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_26_24);

        // --- Pellet_26_25 ---
        var go_Pellet_26_25 = new GameObject("Pellet_26_25");
        go_Pellet_26_25.tag = "Pellet";
        go_Pellet_26_25.transform.position = new Vector3(11.5f, -11.0f, 0.0f);
        var go_Pellet_26_25_rb = go_Pellet_26_25.AddComponent<Rigidbody2D>();
        go_Pellet_26_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_25_bc = go_Pellet_26_25.AddComponent<BoxCollider2D>();
        go_Pellet_26_25_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_25_bc.isTrigger = true;
        var go_Pellet_26_25_sr = go_Pellet_26_25.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_25_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_25_sr.sharedMaterial = unlitMat;
        go_Pellet_26_25_sr.sortingOrder = 2;
        go_Pellet_26_25.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_25);

        // --- Pellet_26_26 ---
        var go_Pellet_26_26 = new GameObject("Pellet_26_26");
        go_Pellet_26_26.tag = "Pellet";
        go_Pellet_26_26.transform.position = new Vector3(12.5f, -11.0f, 0.0f);
        var go_Pellet_26_26_rb = go_Pellet_26_26.AddComponent<Rigidbody2D>();
        go_Pellet_26_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_26_26_bc = go_Pellet_26_26.AddComponent<BoxCollider2D>();
        go_Pellet_26_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_26_26_bc.isTrigger = true;
        var go_Pellet_26_26_sr = go_Pellet_26_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_26_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_26_26_sr.sharedMaterial = unlitMat;
        go_Pellet_26_26_sr.sortingOrder = 2;
        go_Pellet_26_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_26_26);

        // --- Node_26_26 ---
        var go_Node_26_26 = new GameObject("Node_26_26");
        go_Node_26_26.transform.position = new Vector3(12.5f, -11.0f, 0.0f);
        var go_Node_26_26_rb = go_Node_26_26.AddComponent<Rigidbody2D>();
        go_Node_26_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_26_26_bc = go_Node_26_26.AddComponent<BoxCollider2D>();
        go_Node_26_26_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_26_26_bc.isTrigger = true;
        go_Node_26_26.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_26_26);

        // --- Wall_26_27 ---
        var go_Wall_26_27 = new GameObject("Wall_26_27");
        go_Wall_26_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_26_27.transform.position = new Vector3(13.5f, -11.0f, 0.0f);
        var go_Wall_26_27_rb = go_Wall_26_27.AddComponent<Rigidbody2D>();
        go_Wall_26_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_26_27_bc = go_Wall_26_27.AddComponent<BoxCollider2D>();
        go_Wall_26_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_26_27_sr = go_Wall_26_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_26_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_26_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_26_27);

        // --- Wall_27_0 ---
        var go_Wall_27_0 = new GameObject("Wall_27_0");
        go_Wall_27_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_0.transform.position = new Vector3(-13.5f, -12.0f, 0.0f);
        var go_Wall_27_0_rb = go_Wall_27_0.AddComponent<Rigidbody2D>();
        go_Wall_27_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_0_bc = go_Wall_27_0.AddComponent<BoxCollider2D>();
        go_Wall_27_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_0_sr = go_Wall_27_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_0);

        // --- Pellet_27_1 ---
        var go_Pellet_27_1 = new GameObject("Pellet_27_1");
        go_Pellet_27_1.tag = "Pellet";
        go_Pellet_27_1.transform.position = new Vector3(-12.5f, -12.0f, 0.0f);
        var go_Pellet_27_1_rb = go_Pellet_27_1.AddComponent<Rigidbody2D>();
        go_Pellet_27_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_27_1_bc = go_Pellet_27_1.AddComponent<BoxCollider2D>();
        go_Pellet_27_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_27_1_bc.isTrigger = true;
        var go_Pellet_27_1_sr = go_Pellet_27_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_27_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_27_1_sr.sharedMaterial = unlitMat;
        go_Pellet_27_1_sr.sortingOrder = 2;
        go_Pellet_27_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_27_1);

        // --- Wall_27_2 ---
        var go_Wall_27_2 = new GameObject("Wall_27_2");
        go_Wall_27_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_2.transform.position = new Vector3(-11.5f, -12.0f, 0.0f);
        var go_Wall_27_2_rb = go_Wall_27_2.AddComponent<Rigidbody2D>();
        go_Wall_27_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_2_bc = go_Wall_27_2.AddComponent<BoxCollider2D>();
        go_Wall_27_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_2_sr = go_Wall_27_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_2);

        // --- Wall_27_3 ---
        var go_Wall_27_3 = new GameObject("Wall_27_3");
        go_Wall_27_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_3.transform.position = new Vector3(-10.5f, -12.0f, 0.0f);
        var go_Wall_27_3_rb = go_Wall_27_3.AddComponent<Rigidbody2D>();
        go_Wall_27_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_3_bc = go_Wall_27_3.AddComponent<BoxCollider2D>();
        go_Wall_27_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_3_sr = go_Wall_27_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_3);

        // --- Wall_27_4 ---
        var go_Wall_27_4 = new GameObject("Wall_27_4");
        go_Wall_27_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_4.transform.position = new Vector3(-9.5f, -12.0f, 0.0f);
        var go_Wall_27_4_rb = go_Wall_27_4.AddComponent<Rigidbody2D>();
        go_Wall_27_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_4_bc = go_Wall_27_4.AddComponent<BoxCollider2D>();
        go_Wall_27_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_4_sr = go_Wall_27_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_4);

        // --- Wall_27_5 ---
        var go_Wall_27_5 = new GameObject("Wall_27_5");
        go_Wall_27_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_5.transform.position = new Vector3(-8.5f, -12.0f, 0.0f);
        var go_Wall_27_5_rb = go_Wall_27_5.AddComponent<Rigidbody2D>();
        go_Wall_27_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_5_bc = go_Wall_27_5.AddComponent<BoxCollider2D>();
        go_Wall_27_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_5_sr = go_Wall_27_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_5);

        // --- Wall_27_6 ---
        var go_Wall_27_6 = new GameObject("Wall_27_6");
        go_Wall_27_6.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_6.transform.position = new Vector3(-7.5f, -12.0f, 0.0f);
        var go_Wall_27_6_rb = go_Wall_27_6.AddComponent<Rigidbody2D>();
        go_Wall_27_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_6_bc = go_Wall_27_6.AddComponent<BoxCollider2D>();
        go_Wall_27_6_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_6_sr = go_Wall_27_6.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_6_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_6_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_6);

        // --- Wall_27_7 ---
        var go_Wall_27_7 = new GameObject("Wall_27_7");
        go_Wall_27_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_7.transform.position = new Vector3(-6.5f, -12.0f, 0.0f);
        var go_Wall_27_7_rb = go_Wall_27_7.AddComponent<Rigidbody2D>();
        go_Wall_27_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_7_bc = go_Wall_27_7.AddComponent<BoxCollider2D>();
        go_Wall_27_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_7_sr = go_Wall_27_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_7);

        // --- Wall_27_8 ---
        var go_Wall_27_8 = new GameObject("Wall_27_8");
        go_Wall_27_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_8.transform.position = new Vector3(-5.5f, -12.0f, 0.0f);
        var go_Wall_27_8_rb = go_Wall_27_8.AddComponent<Rigidbody2D>();
        go_Wall_27_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_8_bc = go_Wall_27_8.AddComponent<BoxCollider2D>();
        go_Wall_27_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_8_sr = go_Wall_27_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_8);

        // --- Wall_27_9 ---
        var go_Wall_27_9 = new GameObject("Wall_27_9");
        go_Wall_27_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_9.transform.position = new Vector3(-4.5f, -12.0f, 0.0f);
        var go_Wall_27_9_rb = go_Wall_27_9.AddComponent<Rigidbody2D>();
        go_Wall_27_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_9_bc = go_Wall_27_9.AddComponent<BoxCollider2D>();
        go_Wall_27_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_9_sr = go_Wall_27_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_9);

        // --- Wall_27_10 ---
        var go_Wall_27_10 = new GameObject("Wall_27_10");
        go_Wall_27_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_10.transform.position = new Vector3(-3.5f, -12.0f, 0.0f);
        var go_Wall_27_10_rb = go_Wall_27_10.AddComponent<Rigidbody2D>();
        go_Wall_27_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_10_bc = go_Wall_27_10.AddComponent<BoxCollider2D>();
        go_Wall_27_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_10_sr = go_Wall_27_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_10);

        // --- Wall_27_11 ---
        var go_Wall_27_11 = new GameObject("Wall_27_11");
        go_Wall_27_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_11.transform.position = new Vector3(-2.5f, -12.0f, 0.0f);
        var go_Wall_27_11_rb = go_Wall_27_11.AddComponent<Rigidbody2D>();
        go_Wall_27_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_11_bc = go_Wall_27_11.AddComponent<BoxCollider2D>();
        go_Wall_27_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_11_sr = go_Wall_27_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_11);

        // --- Pellet_27_12 ---
        var go_Pellet_27_12 = new GameObject("Pellet_27_12");
        go_Pellet_27_12.tag = "Pellet";
        go_Pellet_27_12.transform.position = new Vector3(-1.5f, -12.0f, 0.0f);
        var go_Pellet_27_12_rb = go_Pellet_27_12.AddComponent<Rigidbody2D>();
        go_Pellet_27_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_27_12_bc = go_Pellet_27_12.AddComponent<BoxCollider2D>();
        go_Pellet_27_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_27_12_bc.isTrigger = true;
        var go_Pellet_27_12_sr = go_Pellet_27_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_27_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_27_12_sr.sharedMaterial = unlitMat;
        go_Pellet_27_12_sr.sortingOrder = 2;
        go_Pellet_27_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_27_12);

        // --- Wall_27_13 ---
        var go_Wall_27_13 = new GameObject("Wall_27_13");
        go_Wall_27_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_13.transform.position = new Vector3(-0.5f, -12.0f, 0.0f);
        var go_Wall_27_13_rb = go_Wall_27_13.AddComponent<Rigidbody2D>();
        go_Wall_27_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_13_bc = go_Wall_27_13.AddComponent<BoxCollider2D>();
        go_Wall_27_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_13_sr = go_Wall_27_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_13);

        // --- Wall_27_14 ---
        var go_Wall_27_14 = new GameObject("Wall_27_14");
        go_Wall_27_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_14.transform.position = new Vector3(0.5f, -12.0f, 0.0f);
        var go_Wall_27_14_rb = go_Wall_27_14.AddComponent<Rigidbody2D>();
        go_Wall_27_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_14_bc = go_Wall_27_14.AddComponent<BoxCollider2D>();
        go_Wall_27_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_14_sr = go_Wall_27_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_14);

        // --- Pellet_27_15 ---
        var go_Pellet_27_15 = new GameObject("Pellet_27_15");
        go_Pellet_27_15.tag = "Pellet";
        go_Pellet_27_15.transform.position = new Vector3(1.5f, -12.0f, 0.0f);
        var go_Pellet_27_15_rb = go_Pellet_27_15.AddComponent<Rigidbody2D>();
        go_Pellet_27_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_27_15_bc = go_Pellet_27_15.AddComponent<BoxCollider2D>();
        go_Pellet_27_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_27_15_bc.isTrigger = true;
        var go_Pellet_27_15_sr = go_Pellet_27_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_27_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_27_15_sr.sharedMaterial = unlitMat;
        go_Pellet_27_15_sr.sortingOrder = 2;
        go_Pellet_27_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_27_15);

        // --- Wall_27_16 ---
        var go_Wall_27_16 = new GameObject("Wall_27_16");
        go_Wall_27_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_16.transform.position = new Vector3(2.5f, -12.0f, 0.0f);
        var go_Wall_27_16_rb = go_Wall_27_16.AddComponent<Rigidbody2D>();
        go_Wall_27_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_16_bc = go_Wall_27_16.AddComponent<BoxCollider2D>();
        go_Wall_27_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_16_sr = go_Wall_27_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_16);

        // --- Wall_27_17 ---
        var go_Wall_27_17 = new GameObject("Wall_27_17");
        go_Wall_27_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_17.transform.position = new Vector3(3.5f, -12.0f, 0.0f);
        var go_Wall_27_17_rb = go_Wall_27_17.AddComponent<Rigidbody2D>();
        go_Wall_27_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_17_bc = go_Wall_27_17.AddComponent<BoxCollider2D>();
        go_Wall_27_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_17_sr = go_Wall_27_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_17);

        // --- Wall_27_18 ---
        var go_Wall_27_18 = new GameObject("Wall_27_18");
        go_Wall_27_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_18.transform.position = new Vector3(4.5f, -12.0f, 0.0f);
        var go_Wall_27_18_rb = go_Wall_27_18.AddComponent<Rigidbody2D>();
        go_Wall_27_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_18_bc = go_Wall_27_18.AddComponent<BoxCollider2D>();
        go_Wall_27_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_18_sr = go_Wall_27_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_18);

        // --- Wall_27_19 ---
        var go_Wall_27_19 = new GameObject("Wall_27_19");
        go_Wall_27_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_19.transform.position = new Vector3(5.5f, -12.0f, 0.0f);
        var go_Wall_27_19_rb = go_Wall_27_19.AddComponent<Rigidbody2D>();
        go_Wall_27_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_19_bc = go_Wall_27_19.AddComponent<BoxCollider2D>();
        go_Wall_27_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_19_sr = go_Wall_27_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_19);

        // --- Wall_27_20 ---
        var go_Wall_27_20 = new GameObject("Wall_27_20");
        go_Wall_27_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_20.transform.position = new Vector3(6.5f, -12.0f, 0.0f);
        var go_Wall_27_20_rb = go_Wall_27_20.AddComponent<Rigidbody2D>();
        go_Wall_27_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_20_bc = go_Wall_27_20.AddComponent<BoxCollider2D>();
        go_Wall_27_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_20_sr = go_Wall_27_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_20);

        // --- Wall_27_21 ---
        var go_Wall_27_21 = new GameObject("Wall_27_21");
        go_Wall_27_21.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_21.transform.position = new Vector3(7.5f, -12.0f, 0.0f);
        var go_Wall_27_21_rb = go_Wall_27_21.AddComponent<Rigidbody2D>();
        go_Wall_27_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_21_bc = go_Wall_27_21.AddComponent<BoxCollider2D>();
        go_Wall_27_21_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_21_sr = go_Wall_27_21.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_21_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_21_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_21);

        // --- Wall_27_22 ---
        var go_Wall_27_22 = new GameObject("Wall_27_22");
        go_Wall_27_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_22.transform.position = new Vector3(8.5f, -12.0f, 0.0f);
        var go_Wall_27_22_rb = go_Wall_27_22.AddComponent<Rigidbody2D>();
        go_Wall_27_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_22_bc = go_Wall_27_22.AddComponent<BoxCollider2D>();
        go_Wall_27_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_22_sr = go_Wall_27_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_22);

        // --- Wall_27_23 ---
        var go_Wall_27_23 = new GameObject("Wall_27_23");
        go_Wall_27_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_23.transform.position = new Vector3(9.5f, -12.0f, 0.0f);
        var go_Wall_27_23_rb = go_Wall_27_23.AddComponent<Rigidbody2D>();
        go_Wall_27_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_23_bc = go_Wall_27_23.AddComponent<BoxCollider2D>();
        go_Wall_27_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_23_sr = go_Wall_27_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_23);

        // --- Wall_27_24 ---
        var go_Wall_27_24 = new GameObject("Wall_27_24");
        go_Wall_27_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_24.transform.position = new Vector3(10.5f, -12.0f, 0.0f);
        var go_Wall_27_24_rb = go_Wall_27_24.AddComponent<Rigidbody2D>();
        go_Wall_27_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_24_bc = go_Wall_27_24.AddComponent<BoxCollider2D>();
        go_Wall_27_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_24_sr = go_Wall_27_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_24);

        // --- Wall_27_25 ---
        var go_Wall_27_25 = new GameObject("Wall_27_25");
        go_Wall_27_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_25.transform.position = new Vector3(11.5f, -12.0f, 0.0f);
        var go_Wall_27_25_rb = go_Wall_27_25.AddComponent<Rigidbody2D>();
        go_Wall_27_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_25_bc = go_Wall_27_25.AddComponent<BoxCollider2D>();
        go_Wall_27_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_25_sr = go_Wall_27_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_25);

        // --- Pellet_27_26 ---
        var go_Pellet_27_26 = new GameObject("Pellet_27_26");
        go_Pellet_27_26.tag = "Pellet";
        go_Pellet_27_26.transform.position = new Vector3(12.5f, -12.0f, 0.0f);
        var go_Pellet_27_26_rb = go_Pellet_27_26.AddComponent<Rigidbody2D>();
        go_Pellet_27_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_27_26_bc = go_Pellet_27_26.AddComponent<BoxCollider2D>();
        go_Pellet_27_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_27_26_bc.isTrigger = true;
        var go_Pellet_27_26_sr = go_Pellet_27_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_27_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_27_26_sr.sharedMaterial = unlitMat;
        go_Pellet_27_26_sr.sortingOrder = 2;
        go_Pellet_27_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_27_26);

        // --- Wall_27_27 ---
        var go_Wall_27_27 = new GameObject("Wall_27_27");
        go_Wall_27_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_27_27.transform.position = new Vector3(13.5f, -12.0f, 0.0f);
        var go_Wall_27_27_rb = go_Wall_27_27.AddComponent<Rigidbody2D>();
        go_Wall_27_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_27_27_bc = go_Wall_27_27.AddComponent<BoxCollider2D>();
        go_Wall_27_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_27_27_sr = go_Wall_27_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_27_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_27_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_27_27);

        // --- Wall_28_0 ---
        var go_Wall_28_0 = new GameObject("Wall_28_0");
        go_Wall_28_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_0.transform.position = new Vector3(-13.5f, -13.0f, 0.0f);
        var go_Wall_28_0_rb = go_Wall_28_0.AddComponent<Rigidbody2D>();
        go_Wall_28_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_0_bc = go_Wall_28_0.AddComponent<BoxCollider2D>();
        go_Wall_28_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_0_sr = go_Wall_28_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_0);

        // --- Pellet_28_1 ---
        var go_Pellet_28_1 = new GameObject("Pellet_28_1");
        go_Pellet_28_1.tag = "Pellet";
        go_Pellet_28_1.transform.position = new Vector3(-12.5f, -13.0f, 0.0f);
        var go_Pellet_28_1_rb = go_Pellet_28_1.AddComponent<Rigidbody2D>();
        go_Pellet_28_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_28_1_bc = go_Pellet_28_1.AddComponent<BoxCollider2D>();
        go_Pellet_28_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_28_1_bc.isTrigger = true;
        var go_Pellet_28_1_sr = go_Pellet_28_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_28_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_28_1_sr.sharedMaterial = unlitMat;
        go_Pellet_28_1_sr.sortingOrder = 2;
        go_Pellet_28_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_28_1);

        // --- Wall_28_2 ---
        var go_Wall_28_2 = new GameObject("Wall_28_2");
        go_Wall_28_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_2.transform.position = new Vector3(-11.5f, -13.0f, 0.0f);
        var go_Wall_28_2_rb = go_Wall_28_2.AddComponent<Rigidbody2D>();
        go_Wall_28_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_2_bc = go_Wall_28_2.AddComponent<BoxCollider2D>();
        go_Wall_28_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_2_sr = go_Wall_28_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_2);

        // --- Wall_28_3 ---
        var go_Wall_28_3 = new GameObject("Wall_28_3");
        go_Wall_28_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_3.transform.position = new Vector3(-10.5f, -13.0f, 0.0f);
        var go_Wall_28_3_rb = go_Wall_28_3.AddComponent<Rigidbody2D>();
        go_Wall_28_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_3_bc = go_Wall_28_3.AddComponent<BoxCollider2D>();
        go_Wall_28_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_3_sr = go_Wall_28_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_3);

        // --- Wall_28_4 ---
        var go_Wall_28_4 = new GameObject("Wall_28_4");
        go_Wall_28_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_4.transform.position = new Vector3(-9.5f, -13.0f, 0.0f);
        var go_Wall_28_4_rb = go_Wall_28_4.AddComponent<Rigidbody2D>();
        go_Wall_28_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_4_bc = go_Wall_28_4.AddComponent<BoxCollider2D>();
        go_Wall_28_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_4_sr = go_Wall_28_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_4);

        // --- Wall_28_5 ---
        var go_Wall_28_5 = new GameObject("Wall_28_5");
        go_Wall_28_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_5.transform.position = new Vector3(-8.5f, -13.0f, 0.0f);
        var go_Wall_28_5_rb = go_Wall_28_5.AddComponent<Rigidbody2D>();
        go_Wall_28_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_5_bc = go_Wall_28_5.AddComponent<BoxCollider2D>();
        go_Wall_28_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_5_sr = go_Wall_28_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_5);

        // --- Wall_28_6 ---
        var go_Wall_28_6 = new GameObject("Wall_28_6");
        go_Wall_28_6.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_6.transform.position = new Vector3(-7.5f, -13.0f, 0.0f);
        var go_Wall_28_6_rb = go_Wall_28_6.AddComponent<Rigidbody2D>();
        go_Wall_28_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_6_bc = go_Wall_28_6.AddComponent<BoxCollider2D>();
        go_Wall_28_6_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_6_sr = go_Wall_28_6.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_6_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_6_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_6);

        // --- Wall_28_7 ---
        var go_Wall_28_7 = new GameObject("Wall_28_7");
        go_Wall_28_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_7.transform.position = new Vector3(-6.5f, -13.0f, 0.0f);
        var go_Wall_28_7_rb = go_Wall_28_7.AddComponent<Rigidbody2D>();
        go_Wall_28_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_7_bc = go_Wall_28_7.AddComponent<BoxCollider2D>();
        go_Wall_28_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_7_sr = go_Wall_28_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_7);

        // --- Wall_28_8 ---
        var go_Wall_28_8 = new GameObject("Wall_28_8");
        go_Wall_28_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_8.transform.position = new Vector3(-5.5f, -13.0f, 0.0f);
        var go_Wall_28_8_rb = go_Wall_28_8.AddComponent<Rigidbody2D>();
        go_Wall_28_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_8_bc = go_Wall_28_8.AddComponent<BoxCollider2D>();
        go_Wall_28_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_8_sr = go_Wall_28_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_8);

        // --- Wall_28_9 ---
        var go_Wall_28_9 = new GameObject("Wall_28_9");
        go_Wall_28_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_9.transform.position = new Vector3(-4.5f, -13.0f, 0.0f);
        var go_Wall_28_9_rb = go_Wall_28_9.AddComponent<Rigidbody2D>();
        go_Wall_28_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_9_bc = go_Wall_28_9.AddComponent<BoxCollider2D>();
        go_Wall_28_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_9_sr = go_Wall_28_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_9);

        // --- Wall_28_10 ---
        var go_Wall_28_10 = new GameObject("Wall_28_10");
        go_Wall_28_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_10.transform.position = new Vector3(-3.5f, -13.0f, 0.0f);
        var go_Wall_28_10_rb = go_Wall_28_10.AddComponent<Rigidbody2D>();
        go_Wall_28_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_10_bc = go_Wall_28_10.AddComponent<BoxCollider2D>();
        go_Wall_28_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_10_sr = go_Wall_28_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_10);

        // --- Wall_28_11 ---
        var go_Wall_28_11 = new GameObject("Wall_28_11");
        go_Wall_28_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_11.transform.position = new Vector3(-2.5f, -13.0f, 0.0f);
        var go_Wall_28_11_rb = go_Wall_28_11.AddComponent<Rigidbody2D>();
        go_Wall_28_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_11_bc = go_Wall_28_11.AddComponent<BoxCollider2D>();
        go_Wall_28_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_11_sr = go_Wall_28_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_11);

        // --- Pellet_28_12 ---
        var go_Pellet_28_12 = new GameObject("Pellet_28_12");
        go_Pellet_28_12.tag = "Pellet";
        go_Pellet_28_12.transform.position = new Vector3(-1.5f, -13.0f, 0.0f);
        var go_Pellet_28_12_rb = go_Pellet_28_12.AddComponent<Rigidbody2D>();
        go_Pellet_28_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_28_12_bc = go_Pellet_28_12.AddComponent<BoxCollider2D>();
        go_Pellet_28_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_28_12_bc.isTrigger = true;
        var go_Pellet_28_12_sr = go_Pellet_28_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_28_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_28_12_sr.sharedMaterial = unlitMat;
        go_Pellet_28_12_sr.sortingOrder = 2;
        go_Pellet_28_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_28_12);

        // --- Wall_28_13 ---
        var go_Wall_28_13 = new GameObject("Wall_28_13");
        go_Wall_28_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_13.transform.position = new Vector3(-0.5f, -13.0f, 0.0f);
        var go_Wall_28_13_rb = go_Wall_28_13.AddComponent<Rigidbody2D>();
        go_Wall_28_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_13_bc = go_Wall_28_13.AddComponent<BoxCollider2D>();
        go_Wall_28_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_13_sr = go_Wall_28_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_13);

        // --- Wall_28_14 ---
        var go_Wall_28_14 = new GameObject("Wall_28_14");
        go_Wall_28_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_14.transform.position = new Vector3(0.5f, -13.0f, 0.0f);
        var go_Wall_28_14_rb = go_Wall_28_14.AddComponent<Rigidbody2D>();
        go_Wall_28_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_14_bc = go_Wall_28_14.AddComponent<BoxCollider2D>();
        go_Wall_28_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_14_sr = go_Wall_28_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_14);

        // --- Pellet_28_15 ---
        var go_Pellet_28_15 = new GameObject("Pellet_28_15");
        go_Pellet_28_15.tag = "Pellet";
        go_Pellet_28_15.transform.position = new Vector3(1.5f, -13.0f, 0.0f);
        var go_Pellet_28_15_rb = go_Pellet_28_15.AddComponent<Rigidbody2D>();
        go_Pellet_28_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_28_15_bc = go_Pellet_28_15.AddComponent<BoxCollider2D>();
        go_Pellet_28_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_28_15_bc.isTrigger = true;
        var go_Pellet_28_15_sr = go_Pellet_28_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_28_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_28_15_sr.sharedMaterial = unlitMat;
        go_Pellet_28_15_sr.sortingOrder = 2;
        go_Pellet_28_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_28_15);

        // --- Wall_28_16 ---
        var go_Wall_28_16 = new GameObject("Wall_28_16");
        go_Wall_28_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_16.transform.position = new Vector3(2.5f, -13.0f, 0.0f);
        var go_Wall_28_16_rb = go_Wall_28_16.AddComponent<Rigidbody2D>();
        go_Wall_28_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_16_bc = go_Wall_28_16.AddComponent<BoxCollider2D>();
        go_Wall_28_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_16_sr = go_Wall_28_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_16);

        // --- Wall_28_17 ---
        var go_Wall_28_17 = new GameObject("Wall_28_17");
        go_Wall_28_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_17.transform.position = new Vector3(3.5f, -13.0f, 0.0f);
        var go_Wall_28_17_rb = go_Wall_28_17.AddComponent<Rigidbody2D>();
        go_Wall_28_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_17_bc = go_Wall_28_17.AddComponent<BoxCollider2D>();
        go_Wall_28_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_17_sr = go_Wall_28_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_17);

        // --- Wall_28_18 ---
        var go_Wall_28_18 = new GameObject("Wall_28_18");
        go_Wall_28_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_18.transform.position = new Vector3(4.5f, -13.0f, 0.0f);
        var go_Wall_28_18_rb = go_Wall_28_18.AddComponent<Rigidbody2D>();
        go_Wall_28_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_18_bc = go_Wall_28_18.AddComponent<BoxCollider2D>();
        go_Wall_28_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_18_sr = go_Wall_28_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_18);

        // --- Wall_28_19 ---
        var go_Wall_28_19 = new GameObject("Wall_28_19");
        go_Wall_28_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_19.transform.position = new Vector3(5.5f, -13.0f, 0.0f);
        var go_Wall_28_19_rb = go_Wall_28_19.AddComponent<Rigidbody2D>();
        go_Wall_28_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_19_bc = go_Wall_28_19.AddComponent<BoxCollider2D>();
        go_Wall_28_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_19_sr = go_Wall_28_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_19);

        // --- Wall_28_20 ---
        var go_Wall_28_20 = new GameObject("Wall_28_20");
        go_Wall_28_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_20.transform.position = new Vector3(6.5f, -13.0f, 0.0f);
        var go_Wall_28_20_rb = go_Wall_28_20.AddComponent<Rigidbody2D>();
        go_Wall_28_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_20_bc = go_Wall_28_20.AddComponent<BoxCollider2D>();
        go_Wall_28_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_20_sr = go_Wall_28_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_20);

        // --- Wall_28_21 ---
        var go_Wall_28_21 = new GameObject("Wall_28_21");
        go_Wall_28_21.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_21.transform.position = new Vector3(7.5f, -13.0f, 0.0f);
        var go_Wall_28_21_rb = go_Wall_28_21.AddComponent<Rigidbody2D>();
        go_Wall_28_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_21_bc = go_Wall_28_21.AddComponent<BoxCollider2D>();
        go_Wall_28_21_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_21_sr = go_Wall_28_21.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_21_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_21_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_21);

        // --- Wall_28_22 ---
        var go_Wall_28_22 = new GameObject("Wall_28_22");
        go_Wall_28_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_22.transform.position = new Vector3(8.5f, -13.0f, 0.0f);
        var go_Wall_28_22_rb = go_Wall_28_22.AddComponent<Rigidbody2D>();
        go_Wall_28_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_22_bc = go_Wall_28_22.AddComponent<BoxCollider2D>();
        go_Wall_28_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_22_sr = go_Wall_28_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_22);

        // --- Wall_28_23 ---
        var go_Wall_28_23 = new GameObject("Wall_28_23");
        go_Wall_28_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_23.transform.position = new Vector3(9.5f, -13.0f, 0.0f);
        var go_Wall_28_23_rb = go_Wall_28_23.AddComponent<Rigidbody2D>();
        go_Wall_28_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_23_bc = go_Wall_28_23.AddComponent<BoxCollider2D>();
        go_Wall_28_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_23_sr = go_Wall_28_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_23);

        // --- Wall_28_24 ---
        var go_Wall_28_24 = new GameObject("Wall_28_24");
        go_Wall_28_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_24.transform.position = new Vector3(10.5f, -13.0f, 0.0f);
        var go_Wall_28_24_rb = go_Wall_28_24.AddComponent<Rigidbody2D>();
        go_Wall_28_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_24_bc = go_Wall_28_24.AddComponent<BoxCollider2D>();
        go_Wall_28_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_24_sr = go_Wall_28_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_24);

        // --- Wall_28_25 ---
        var go_Wall_28_25 = new GameObject("Wall_28_25");
        go_Wall_28_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_25.transform.position = new Vector3(11.5f, -13.0f, 0.0f);
        var go_Wall_28_25_rb = go_Wall_28_25.AddComponent<Rigidbody2D>();
        go_Wall_28_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_25_bc = go_Wall_28_25.AddComponent<BoxCollider2D>();
        go_Wall_28_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_25_sr = go_Wall_28_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_25);

        // --- Pellet_28_26 ---
        var go_Pellet_28_26 = new GameObject("Pellet_28_26");
        go_Pellet_28_26.tag = "Pellet";
        go_Pellet_28_26.transform.position = new Vector3(12.5f, -13.0f, 0.0f);
        var go_Pellet_28_26_rb = go_Pellet_28_26.AddComponent<Rigidbody2D>();
        go_Pellet_28_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_28_26_bc = go_Pellet_28_26.AddComponent<BoxCollider2D>();
        go_Pellet_28_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_28_26_bc.isTrigger = true;
        var go_Pellet_28_26_sr = go_Pellet_28_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_28_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_28_26_sr.sharedMaterial = unlitMat;
        go_Pellet_28_26_sr.sortingOrder = 2;
        go_Pellet_28_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_28_26);

        // --- Wall_28_27 ---
        var go_Wall_28_27 = new GameObject("Wall_28_27");
        go_Wall_28_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_28_27.transform.position = new Vector3(13.5f, -13.0f, 0.0f);
        var go_Wall_28_27_rb = go_Wall_28_27.AddComponent<Rigidbody2D>();
        go_Wall_28_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_28_27_bc = go_Wall_28_27.AddComponent<BoxCollider2D>();
        go_Wall_28_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_28_27_sr = go_Wall_28_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_28_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_28_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_28_27);

        // --- Wall_29_0 ---
        var go_Wall_29_0 = new GameObject("Wall_29_0");
        go_Wall_29_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_29_0.transform.position = new Vector3(-13.5f, -14.0f, 0.0f);
        var go_Wall_29_0_rb = go_Wall_29_0.AddComponent<Rigidbody2D>();
        go_Wall_29_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_29_0_bc = go_Wall_29_0.AddComponent<BoxCollider2D>();
        go_Wall_29_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_29_0_sr = go_Wall_29_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_29_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_29_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_29_0);

        // --- Pellet_29_1 ---
        var go_Pellet_29_1 = new GameObject("Pellet_29_1");
        go_Pellet_29_1.tag = "Pellet";
        go_Pellet_29_1.transform.position = new Vector3(-12.5f, -14.0f, 0.0f);
        var go_Pellet_29_1_rb = go_Pellet_29_1.AddComponent<Rigidbody2D>();
        go_Pellet_29_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_1_bc = go_Pellet_29_1.AddComponent<BoxCollider2D>();
        go_Pellet_29_1_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_1_bc.isTrigger = true;
        var go_Pellet_29_1_sr = go_Pellet_29_1.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_1_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_1_sr.sharedMaterial = unlitMat;
        go_Pellet_29_1_sr.sortingOrder = 2;
        go_Pellet_29_1.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_1);

        // --- Node_29_1 ---
        var go_Node_29_1 = new GameObject("Node_29_1");
        go_Node_29_1.transform.position = new Vector3(-12.5f, -14.0f, 0.0f);
        var go_Node_29_1_rb = go_Node_29_1.AddComponent<Rigidbody2D>();
        go_Node_29_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_29_1_bc = go_Node_29_1.AddComponent<BoxCollider2D>();
        go_Node_29_1_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_29_1_bc.isTrigger = true;
        go_Node_29_1.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_29_1);

        // --- Pellet_29_2 ---
        var go_Pellet_29_2 = new GameObject("Pellet_29_2");
        go_Pellet_29_2.tag = "Pellet";
        go_Pellet_29_2.transform.position = new Vector3(-11.5f, -14.0f, 0.0f);
        var go_Pellet_29_2_rb = go_Pellet_29_2.AddComponent<Rigidbody2D>();
        go_Pellet_29_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_2_bc = go_Pellet_29_2.AddComponent<BoxCollider2D>();
        go_Pellet_29_2_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_2_bc.isTrigger = true;
        var go_Pellet_29_2_sr = go_Pellet_29_2.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_2_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_2_sr.sharedMaterial = unlitMat;
        go_Pellet_29_2_sr.sortingOrder = 2;
        go_Pellet_29_2.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_2);

        // --- Pellet_29_3 ---
        var go_Pellet_29_3 = new GameObject("Pellet_29_3");
        go_Pellet_29_3.tag = "Pellet";
        go_Pellet_29_3.transform.position = new Vector3(-10.5f, -14.0f, 0.0f);
        var go_Pellet_29_3_rb = go_Pellet_29_3.AddComponent<Rigidbody2D>();
        go_Pellet_29_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_3_bc = go_Pellet_29_3.AddComponent<BoxCollider2D>();
        go_Pellet_29_3_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_3_bc.isTrigger = true;
        var go_Pellet_29_3_sr = go_Pellet_29_3.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_3_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_3_sr.sharedMaterial = unlitMat;
        go_Pellet_29_3_sr.sortingOrder = 2;
        go_Pellet_29_3.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_3);

        // --- Pellet_29_4 ---
        var go_Pellet_29_4 = new GameObject("Pellet_29_4");
        go_Pellet_29_4.tag = "Pellet";
        go_Pellet_29_4.transform.position = new Vector3(-9.5f, -14.0f, 0.0f);
        var go_Pellet_29_4_rb = go_Pellet_29_4.AddComponent<Rigidbody2D>();
        go_Pellet_29_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_4_bc = go_Pellet_29_4.AddComponent<BoxCollider2D>();
        go_Pellet_29_4_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_4_bc.isTrigger = true;
        var go_Pellet_29_4_sr = go_Pellet_29_4.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_4_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_4_sr.sharedMaterial = unlitMat;
        go_Pellet_29_4_sr.sortingOrder = 2;
        go_Pellet_29_4.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_4);

        // --- Pellet_29_5 ---
        var go_Pellet_29_5 = new GameObject("Pellet_29_5");
        go_Pellet_29_5.tag = "Pellet";
        go_Pellet_29_5.transform.position = new Vector3(-8.5f, -14.0f, 0.0f);
        var go_Pellet_29_5_rb = go_Pellet_29_5.AddComponent<Rigidbody2D>();
        go_Pellet_29_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_5_bc = go_Pellet_29_5.AddComponent<BoxCollider2D>();
        go_Pellet_29_5_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_5_bc.isTrigger = true;
        var go_Pellet_29_5_sr = go_Pellet_29_5.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_5_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_5_sr.sharedMaterial = unlitMat;
        go_Pellet_29_5_sr.sortingOrder = 2;
        go_Pellet_29_5.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_5);

        // --- Pellet_29_6 ---
        var go_Pellet_29_6 = new GameObject("Pellet_29_6");
        go_Pellet_29_6.tag = "Pellet";
        go_Pellet_29_6.transform.position = new Vector3(-7.5f, -14.0f, 0.0f);
        var go_Pellet_29_6_rb = go_Pellet_29_6.AddComponent<Rigidbody2D>();
        go_Pellet_29_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_6_bc = go_Pellet_29_6.AddComponent<BoxCollider2D>();
        go_Pellet_29_6_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_6_bc.isTrigger = true;
        var go_Pellet_29_6_sr = go_Pellet_29_6.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_6_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_6_sr.sharedMaterial = unlitMat;
        go_Pellet_29_6_sr.sortingOrder = 2;
        go_Pellet_29_6.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_6);

        // --- Pellet_29_7 ---
        var go_Pellet_29_7 = new GameObject("Pellet_29_7");
        go_Pellet_29_7.tag = "Pellet";
        go_Pellet_29_7.transform.position = new Vector3(-6.5f, -14.0f, 0.0f);
        var go_Pellet_29_7_rb = go_Pellet_29_7.AddComponent<Rigidbody2D>();
        go_Pellet_29_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_7_bc = go_Pellet_29_7.AddComponent<BoxCollider2D>();
        go_Pellet_29_7_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_7_bc.isTrigger = true;
        var go_Pellet_29_7_sr = go_Pellet_29_7.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_7_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_7_sr.sharedMaterial = unlitMat;
        go_Pellet_29_7_sr.sortingOrder = 2;
        go_Pellet_29_7.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_7);

        // --- Pellet_29_8 ---
        var go_Pellet_29_8 = new GameObject("Pellet_29_8");
        go_Pellet_29_8.tag = "Pellet";
        go_Pellet_29_8.transform.position = new Vector3(-5.5f, -14.0f, 0.0f);
        var go_Pellet_29_8_rb = go_Pellet_29_8.AddComponent<Rigidbody2D>();
        go_Pellet_29_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_8_bc = go_Pellet_29_8.AddComponent<BoxCollider2D>();
        go_Pellet_29_8_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_8_bc.isTrigger = true;
        var go_Pellet_29_8_sr = go_Pellet_29_8.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_8_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_8_sr.sharedMaterial = unlitMat;
        go_Pellet_29_8_sr.sortingOrder = 2;
        go_Pellet_29_8.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_8);

        // --- Pellet_29_9 ---
        var go_Pellet_29_9 = new GameObject("Pellet_29_9");
        go_Pellet_29_9.tag = "Pellet";
        go_Pellet_29_9.transform.position = new Vector3(-4.5f, -14.0f, 0.0f);
        var go_Pellet_29_9_rb = go_Pellet_29_9.AddComponent<Rigidbody2D>();
        go_Pellet_29_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_9_bc = go_Pellet_29_9.AddComponent<BoxCollider2D>();
        go_Pellet_29_9_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_9_bc.isTrigger = true;
        var go_Pellet_29_9_sr = go_Pellet_29_9.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_9_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_9_sr.sharedMaterial = unlitMat;
        go_Pellet_29_9_sr.sortingOrder = 2;
        go_Pellet_29_9.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_9);

        // --- Pellet_29_10 ---
        var go_Pellet_29_10 = new GameObject("Pellet_29_10");
        go_Pellet_29_10.tag = "Pellet";
        go_Pellet_29_10.transform.position = new Vector3(-3.5f, -14.0f, 0.0f);
        var go_Pellet_29_10_rb = go_Pellet_29_10.AddComponent<Rigidbody2D>();
        go_Pellet_29_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_10_bc = go_Pellet_29_10.AddComponent<BoxCollider2D>();
        go_Pellet_29_10_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_10_bc.isTrigger = true;
        var go_Pellet_29_10_sr = go_Pellet_29_10.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_10_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_10_sr.sharedMaterial = unlitMat;
        go_Pellet_29_10_sr.sortingOrder = 2;
        go_Pellet_29_10.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_10);

        // --- Pellet_29_11 ---
        var go_Pellet_29_11 = new GameObject("Pellet_29_11");
        go_Pellet_29_11.tag = "Pellet";
        go_Pellet_29_11.transform.position = new Vector3(-2.5f, -14.0f, 0.0f);
        var go_Pellet_29_11_rb = go_Pellet_29_11.AddComponent<Rigidbody2D>();
        go_Pellet_29_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_11_bc = go_Pellet_29_11.AddComponent<BoxCollider2D>();
        go_Pellet_29_11_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_11_bc.isTrigger = true;
        var go_Pellet_29_11_sr = go_Pellet_29_11.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_11_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_11_sr.sharedMaterial = unlitMat;
        go_Pellet_29_11_sr.sortingOrder = 2;
        go_Pellet_29_11.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_11);

        // --- Pellet_29_12 ---
        var go_Pellet_29_12 = new GameObject("Pellet_29_12");
        go_Pellet_29_12.tag = "Pellet";
        go_Pellet_29_12.transform.position = new Vector3(-1.5f, -14.0f, 0.0f);
        var go_Pellet_29_12_rb = go_Pellet_29_12.AddComponent<Rigidbody2D>();
        go_Pellet_29_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_12_bc = go_Pellet_29_12.AddComponent<BoxCollider2D>();
        go_Pellet_29_12_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_12_bc.isTrigger = true;
        var go_Pellet_29_12_sr = go_Pellet_29_12.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_12_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_12_sr.sharedMaterial = unlitMat;
        go_Pellet_29_12_sr.sortingOrder = 2;
        go_Pellet_29_12.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_12);

        // --- Node_29_12 ---
        var go_Node_29_12 = new GameObject("Node_29_12");
        go_Node_29_12.transform.position = new Vector3(-1.5f, -14.0f, 0.0f);
        var go_Node_29_12_rb = go_Node_29_12.AddComponent<Rigidbody2D>();
        go_Node_29_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_29_12_bc = go_Node_29_12.AddComponent<BoxCollider2D>();
        go_Node_29_12_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_29_12_bc.isTrigger = true;
        go_Node_29_12.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_29_12);

        // --- Pellet_29_13 ---
        var go_Pellet_29_13 = new GameObject("Pellet_29_13");
        go_Pellet_29_13.tag = "Pellet";
        go_Pellet_29_13.transform.position = new Vector3(-0.5f, -14.0f, 0.0f);
        var go_Pellet_29_13_rb = go_Pellet_29_13.AddComponent<Rigidbody2D>();
        go_Pellet_29_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_13_bc = go_Pellet_29_13.AddComponent<BoxCollider2D>();
        go_Pellet_29_13_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_13_bc.isTrigger = true;
        var go_Pellet_29_13_sr = go_Pellet_29_13.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_13_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_13_sr.sharedMaterial = unlitMat;
        go_Pellet_29_13_sr.sortingOrder = 2;
        go_Pellet_29_13.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_13);

        // --- Pellet_29_14 ---
        var go_Pellet_29_14 = new GameObject("Pellet_29_14");
        go_Pellet_29_14.tag = "Pellet";
        go_Pellet_29_14.transform.position = new Vector3(0.5f, -14.0f, 0.0f);
        var go_Pellet_29_14_rb = go_Pellet_29_14.AddComponent<Rigidbody2D>();
        go_Pellet_29_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_14_bc = go_Pellet_29_14.AddComponent<BoxCollider2D>();
        go_Pellet_29_14_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_14_bc.isTrigger = true;
        var go_Pellet_29_14_sr = go_Pellet_29_14.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_14_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_14_sr.sharedMaterial = unlitMat;
        go_Pellet_29_14_sr.sortingOrder = 2;
        go_Pellet_29_14.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_14);

        // --- Pellet_29_15 ---
        var go_Pellet_29_15 = new GameObject("Pellet_29_15");
        go_Pellet_29_15.tag = "Pellet";
        go_Pellet_29_15.transform.position = new Vector3(1.5f, -14.0f, 0.0f);
        var go_Pellet_29_15_rb = go_Pellet_29_15.AddComponent<Rigidbody2D>();
        go_Pellet_29_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_15_bc = go_Pellet_29_15.AddComponent<BoxCollider2D>();
        go_Pellet_29_15_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_15_bc.isTrigger = true;
        var go_Pellet_29_15_sr = go_Pellet_29_15.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_15_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_15_sr.sharedMaterial = unlitMat;
        go_Pellet_29_15_sr.sortingOrder = 2;
        go_Pellet_29_15.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_15);

        // --- Node_29_15 ---
        var go_Node_29_15 = new GameObject("Node_29_15");
        go_Node_29_15.transform.position = new Vector3(1.5f, -14.0f, 0.0f);
        var go_Node_29_15_rb = go_Node_29_15.AddComponent<Rigidbody2D>();
        go_Node_29_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_29_15_bc = go_Node_29_15.AddComponent<BoxCollider2D>();
        go_Node_29_15_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_29_15_bc.isTrigger = true;
        go_Node_29_15.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_29_15);

        // --- Pellet_29_16 ---
        var go_Pellet_29_16 = new GameObject("Pellet_29_16");
        go_Pellet_29_16.tag = "Pellet";
        go_Pellet_29_16.transform.position = new Vector3(2.5f, -14.0f, 0.0f);
        var go_Pellet_29_16_rb = go_Pellet_29_16.AddComponent<Rigidbody2D>();
        go_Pellet_29_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_16_bc = go_Pellet_29_16.AddComponent<BoxCollider2D>();
        go_Pellet_29_16_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_16_bc.isTrigger = true;
        var go_Pellet_29_16_sr = go_Pellet_29_16.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_16_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_16_sr.sharedMaterial = unlitMat;
        go_Pellet_29_16_sr.sortingOrder = 2;
        go_Pellet_29_16.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_16);

        // --- Pellet_29_17 ---
        var go_Pellet_29_17 = new GameObject("Pellet_29_17");
        go_Pellet_29_17.tag = "Pellet";
        go_Pellet_29_17.transform.position = new Vector3(3.5f, -14.0f, 0.0f);
        var go_Pellet_29_17_rb = go_Pellet_29_17.AddComponent<Rigidbody2D>();
        go_Pellet_29_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_17_bc = go_Pellet_29_17.AddComponent<BoxCollider2D>();
        go_Pellet_29_17_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_17_bc.isTrigger = true;
        var go_Pellet_29_17_sr = go_Pellet_29_17.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_17_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_17_sr.sharedMaterial = unlitMat;
        go_Pellet_29_17_sr.sortingOrder = 2;
        go_Pellet_29_17.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_17);

        // --- Pellet_29_18 ---
        var go_Pellet_29_18 = new GameObject("Pellet_29_18");
        go_Pellet_29_18.tag = "Pellet";
        go_Pellet_29_18.transform.position = new Vector3(4.5f, -14.0f, 0.0f);
        var go_Pellet_29_18_rb = go_Pellet_29_18.AddComponent<Rigidbody2D>();
        go_Pellet_29_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_18_bc = go_Pellet_29_18.AddComponent<BoxCollider2D>();
        go_Pellet_29_18_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_18_bc.isTrigger = true;
        var go_Pellet_29_18_sr = go_Pellet_29_18.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_18_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_18_sr.sharedMaterial = unlitMat;
        go_Pellet_29_18_sr.sortingOrder = 2;
        go_Pellet_29_18.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_18);

        // --- Pellet_29_19 ---
        var go_Pellet_29_19 = new GameObject("Pellet_29_19");
        go_Pellet_29_19.tag = "Pellet";
        go_Pellet_29_19.transform.position = new Vector3(5.5f, -14.0f, 0.0f);
        var go_Pellet_29_19_rb = go_Pellet_29_19.AddComponent<Rigidbody2D>();
        go_Pellet_29_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_19_bc = go_Pellet_29_19.AddComponent<BoxCollider2D>();
        go_Pellet_29_19_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_19_bc.isTrigger = true;
        var go_Pellet_29_19_sr = go_Pellet_29_19.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_19_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_19_sr.sharedMaterial = unlitMat;
        go_Pellet_29_19_sr.sortingOrder = 2;
        go_Pellet_29_19.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_19);

        // --- Pellet_29_20 ---
        var go_Pellet_29_20 = new GameObject("Pellet_29_20");
        go_Pellet_29_20.tag = "Pellet";
        go_Pellet_29_20.transform.position = new Vector3(6.5f, -14.0f, 0.0f);
        var go_Pellet_29_20_rb = go_Pellet_29_20.AddComponent<Rigidbody2D>();
        go_Pellet_29_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_20_bc = go_Pellet_29_20.AddComponent<BoxCollider2D>();
        go_Pellet_29_20_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_20_bc.isTrigger = true;
        var go_Pellet_29_20_sr = go_Pellet_29_20.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_20_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_20_sr.sharedMaterial = unlitMat;
        go_Pellet_29_20_sr.sortingOrder = 2;
        go_Pellet_29_20.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_20);

        // --- Pellet_29_21 ---
        var go_Pellet_29_21 = new GameObject("Pellet_29_21");
        go_Pellet_29_21.tag = "Pellet";
        go_Pellet_29_21.transform.position = new Vector3(7.5f, -14.0f, 0.0f);
        var go_Pellet_29_21_rb = go_Pellet_29_21.AddComponent<Rigidbody2D>();
        go_Pellet_29_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_21_bc = go_Pellet_29_21.AddComponent<BoxCollider2D>();
        go_Pellet_29_21_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_21_bc.isTrigger = true;
        var go_Pellet_29_21_sr = go_Pellet_29_21.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_21_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_21_sr.sharedMaterial = unlitMat;
        go_Pellet_29_21_sr.sortingOrder = 2;
        go_Pellet_29_21.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_21);

        // --- Pellet_29_22 ---
        var go_Pellet_29_22 = new GameObject("Pellet_29_22");
        go_Pellet_29_22.tag = "Pellet";
        go_Pellet_29_22.transform.position = new Vector3(8.5f, -14.0f, 0.0f);
        var go_Pellet_29_22_rb = go_Pellet_29_22.AddComponent<Rigidbody2D>();
        go_Pellet_29_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_22_bc = go_Pellet_29_22.AddComponent<BoxCollider2D>();
        go_Pellet_29_22_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_22_bc.isTrigger = true;
        var go_Pellet_29_22_sr = go_Pellet_29_22.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_22_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_22_sr.sharedMaterial = unlitMat;
        go_Pellet_29_22_sr.sortingOrder = 2;
        go_Pellet_29_22.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_22);

        // --- Pellet_29_23 ---
        var go_Pellet_29_23 = new GameObject("Pellet_29_23");
        go_Pellet_29_23.tag = "Pellet";
        go_Pellet_29_23.transform.position = new Vector3(9.5f, -14.0f, 0.0f);
        var go_Pellet_29_23_rb = go_Pellet_29_23.AddComponent<Rigidbody2D>();
        go_Pellet_29_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_23_bc = go_Pellet_29_23.AddComponent<BoxCollider2D>();
        go_Pellet_29_23_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_23_bc.isTrigger = true;
        var go_Pellet_29_23_sr = go_Pellet_29_23.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_23_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_23_sr.sharedMaterial = unlitMat;
        go_Pellet_29_23_sr.sortingOrder = 2;
        go_Pellet_29_23.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_23);

        // --- Pellet_29_24 ---
        var go_Pellet_29_24 = new GameObject("Pellet_29_24");
        go_Pellet_29_24.tag = "Pellet";
        go_Pellet_29_24.transform.position = new Vector3(10.5f, -14.0f, 0.0f);
        var go_Pellet_29_24_rb = go_Pellet_29_24.AddComponent<Rigidbody2D>();
        go_Pellet_29_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_24_bc = go_Pellet_29_24.AddComponent<BoxCollider2D>();
        go_Pellet_29_24_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_24_bc.isTrigger = true;
        var go_Pellet_29_24_sr = go_Pellet_29_24.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_24_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_24_sr.sharedMaterial = unlitMat;
        go_Pellet_29_24_sr.sortingOrder = 2;
        go_Pellet_29_24.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_24);

        // --- Pellet_29_25 ---
        var go_Pellet_29_25 = new GameObject("Pellet_29_25");
        go_Pellet_29_25.tag = "Pellet";
        go_Pellet_29_25.transform.position = new Vector3(11.5f, -14.0f, 0.0f);
        var go_Pellet_29_25_rb = go_Pellet_29_25.AddComponent<Rigidbody2D>();
        go_Pellet_29_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_25_bc = go_Pellet_29_25.AddComponent<BoxCollider2D>();
        go_Pellet_29_25_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_25_bc.isTrigger = true;
        var go_Pellet_29_25_sr = go_Pellet_29_25.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_25_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_25_sr.sharedMaterial = unlitMat;
        go_Pellet_29_25_sr.sortingOrder = 2;
        go_Pellet_29_25.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_25);

        // --- Pellet_29_26 ---
        var go_Pellet_29_26 = new GameObject("Pellet_29_26");
        go_Pellet_29_26.tag = "Pellet";
        go_Pellet_29_26.transform.position = new Vector3(12.5f, -14.0f, 0.0f);
        var go_Pellet_29_26_rb = go_Pellet_29_26.AddComponent<Rigidbody2D>();
        go_Pellet_29_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Pellet_29_26_bc = go_Pellet_29_26.AddComponent<BoxCollider2D>();
        go_Pellet_29_26_bc.size = new Vector2(0.25f, 0.25f);
        go_Pellet_29_26_bc.isTrigger = true;
        var go_Pellet_29_26_sr = go_Pellet_29_26.AddComponent<SpriteRenderer>();
        if (sprite_pellet_small != null) go_Pellet_29_26_sr.sprite = sprite_pellet_small;
        if (unlitMat != null) go_Pellet_29_26_sr.sharedMaterial = unlitMat;
        go_Pellet_29_26_sr.sortingOrder = 2;
        go_Pellet_29_26.AddComponent<Pellet>();
        // Pellet.points = 10
        EditorUtility.SetDirty(go_Pellet_29_26);

        // --- Node_29_26 ---
        var go_Node_29_26 = new GameObject("Node_29_26");
        go_Node_29_26.transform.position = new Vector3(12.5f, -14.0f, 0.0f);
        var go_Node_29_26_rb = go_Node_29_26.AddComponent<Rigidbody2D>();
        go_Node_29_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Node_29_26_bc = go_Node_29_26.AddComponent<BoxCollider2D>();
        go_Node_29_26_bc.size = new Vector2(0.5f, 0.5f);
        go_Node_29_26_bc.isTrigger = true;
        go_Node_29_26.AddComponent<Node>();
        // Node.obstacleLayer = 6
        EditorUtility.SetDirty(go_Node_29_26);

        // --- Wall_29_27 ---
        var go_Wall_29_27 = new GameObject("Wall_29_27");
        go_Wall_29_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_29_27.transform.position = new Vector3(13.5f, -14.0f, 0.0f);
        var go_Wall_29_27_rb = go_Wall_29_27.AddComponent<Rigidbody2D>();
        go_Wall_29_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_29_27_bc = go_Wall_29_27.AddComponent<BoxCollider2D>();
        go_Wall_29_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_29_27_sr = go_Wall_29_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_29_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_29_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_29_27);

        // --- Wall_30_0 ---
        var go_Wall_30_0 = new GameObject("Wall_30_0");
        go_Wall_30_0.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_0.transform.position = new Vector3(-13.5f, -15.0f, 0.0f);
        var go_Wall_30_0_rb = go_Wall_30_0.AddComponent<Rigidbody2D>();
        go_Wall_30_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_0_bc = go_Wall_30_0.AddComponent<BoxCollider2D>();
        go_Wall_30_0_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_0_sr = go_Wall_30_0.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_0_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_0_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_0);

        // --- Wall_30_1 ---
        var go_Wall_30_1 = new GameObject("Wall_30_1");
        go_Wall_30_1.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_1.transform.position = new Vector3(-12.5f, -15.0f, 0.0f);
        var go_Wall_30_1_rb = go_Wall_30_1.AddComponent<Rigidbody2D>();
        go_Wall_30_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_1_bc = go_Wall_30_1.AddComponent<BoxCollider2D>();
        go_Wall_30_1_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_1_sr = go_Wall_30_1.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_1_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_1_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_1);

        // --- Wall_30_2 ---
        var go_Wall_30_2 = new GameObject("Wall_30_2");
        go_Wall_30_2.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_2.transform.position = new Vector3(-11.5f, -15.0f, 0.0f);
        var go_Wall_30_2_rb = go_Wall_30_2.AddComponent<Rigidbody2D>();
        go_Wall_30_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_2_bc = go_Wall_30_2.AddComponent<BoxCollider2D>();
        go_Wall_30_2_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_2_sr = go_Wall_30_2.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_2_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_2_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_2);

        // --- Wall_30_3 ---
        var go_Wall_30_3 = new GameObject("Wall_30_3");
        go_Wall_30_3.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_3.transform.position = new Vector3(-10.5f, -15.0f, 0.0f);
        var go_Wall_30_3_rb = go_Wall_30_3.AddComponent<Rigidbody2D>();
        go_Wall_30_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_3_bc = go_Wall_30_3.AddComponent<BoxCollider2D>();
        go_Wall_30_3_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_3_sr = go_Wall_30_3.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_3_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_3_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_3);

        // --- Wall_30_4 ---
        var go_Wall_30_4 = new GameObject("Wall_30_4");
        go_Wall_30_4.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_4.transform.position = new Vector3(-9.5f, -15.0f, 0.0f);
        var go_Wall_30_4_rb = go_Wall_30_4.AddComponent<Rigidbody2D>();
        go_Wall_30_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_4_bc = go_Wall_30_4.AddComponent<BoxCollider2D>();
        go_Wall_30_4_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_4_sr = go_Wall_30_4.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_4_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_4_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_4);

        // --- Wall_30_5 ---
        var go_Wall_30_5 = new GameObject("Wall_30_5");
        go_Wall_30_5.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_5.transform.position = new Vector3(-8.5f, -15.0f, 0.0f);
        var go_Wall_30_5_rb = go_Wall_30_5.AddComponent<Rigidbody2D>();
        go_Wall_30_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_5_bc = go_Wall_30_5.AddComponent<BoxCollider2D>();
        go_Wall_30_5_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_5_sr = go_Wall_30_5.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_5_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_5_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_5);

        // --- Wall_30_6 ---
        var go_Wall_30_6 = new GameObject("Wall_30_6");
        go_Wall_30_6.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_6.transform.position = new Vector3(-7.5f, -15.0f, 0.0f);
        var go_Wall_30_6_rb = go_Wall_30_6.AddComponent<Rigidbody2D>();
        go_Wall_30_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_6_bc = go_Wall_30_6.AddComponent<BoxCollider2D>();
        go_Wall_30_6_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_6_sr = go_Wall_30_6.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_6_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_6_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_6);

        // --- Wall_30_7 ---
        var go_Wall_30_7 = new GameObject("Wall_30_7");
        go_Wall_30_7.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_7.transform.position = new Vector3(-6.5f, -15.0f, 0.0f);
        var go_Wall_30_7_rb = go_Wall_30_7.AddComponent<Rigidbody2D>();
        go_Wall_30_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_7_bc = go_Wall_30_7.AddComponent<BoxCollider2D>();
        go_Wall_30_7_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_7_sr = go_Wall_30_7.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_7_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_7_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_7);

        // --- Wall_30_8 ---
        var go_Wall_30_8 = new GameObject("Wall_30_8");
        go_Wall_30_8.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_8.transform.position = new Vector3(-5.5f, -15.0f, 0.0f);
        var go_Wall_30_8_rb = go_Wall_30_8.AddComponent<Rigidbody2D>();
        go_Wall_30_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_8_bc = go_Wall_30_8.AddComponent<BoxCollider2D>();
        go_Wall_30_8_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_8_sr = go_Wall_30_8.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_8_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_8_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_8);

        // --- Wall_30_9 ---
        var go_Wall_30_9 = new GameObject("Wall_30_9");
        go_Wall_30_9.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_9.transform.position = new Vector3(-4.5f, -15.0f, 0.0f);
        var go_Wall_30_9_rb = go_Wall_30_9.AddComponent<Rigidbody2D>();
        go_Wall_30_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_9_bc = go_Wall_30_9.AddComponent<BoxCollider2D>();
        go_Wall_30_9_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_9_sr = go_Wall_30_9.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_9_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_9_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_9);

        // --- Wall_30_10 ---
        var go_Wall_30_10 = new GameObject("Wall_30_10");
        go_Wall_30_10.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_10.transform.position = new Vector3(-3.5f, -15.0f, 0.0f);
        var go_Wall_30_10_rb = go_Wall_30_10.AddComponent<Rigidbody2D>();
        go_Wall_30_10_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_10_bc = go_Wall_30_10.AddComponent<BoxCollider2D>();
        go_Wall_30_10_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_10_sr = go_Wall_30_10.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_10_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_10_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_10);

        // --- Wall_30_11 ---
        var go_Wall_30_11 = new GameObject("Wall_30_11");
        go_Wall_30_11.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_11.transform.position = new Vector3(-2.5f, -15.0f, 0.0f);
        var go_Wall_30_11_rb = go_Wall_30_11.AddComponent<Rigidbody2D>();
        go_Wall_30_11_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_11_bc = go_Wall_30_11.AddComponent<BoxCollider2D>();
        go_Wall_30_11_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_11_sr = go_Wall_30_11.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_11_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_11_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_11);

        // --- Wall_30_12 ---
        var go_Wall_30_12 = new GameObject("Wall_30_12");
        go_Wall_30_12.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_12.transform.position = new Vector3(-1.5f, -15.0f, 0.0f);
        var go_Wall_30_12_rb = go_Wall_30_12.AddComponent<Rigidbody2D>();
        go_Wall_30_12_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_12_bc = go_Wall_30_12.AddComponent<BoxCollider2D>();
        go_Wall_30_12_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_12_sr = go_Wall_30_12.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_12_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_12_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_12);

        // --- Wall_30_13 ---
        var go_Wall_30_13 = new GameObject("Wall_30_13");
        go_Wall_30_13.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_13.transform.position = new Vector3(-0.5f, -15.0f, 0.0f);
        var go_Wall_30_13_rb = go_Wall_30_13.AddComponent<Rigidbody2D>();
        go_Wall_30_13_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_13_bc = go_Wall_30_13.AddComponent<BoxCollider2D>();
        go_Wall_30_13_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_13_sr = go_Wall_30_13.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_13_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_13_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_13);

        // --- Wall_30_14 ---
        var go_Wall_30_14 = new GameObject("Wall_30_14");
        go_Wall_30_14.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_14.transform.position = new Vector3(0.5f, -15.0f, 0.0f);
        var go_Wall_30_14_rb = go_Wall_30_14.AddComponent<Rigidbody2D>();
        go_Wall_30_14_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_14_bc = go_Wall_30_14.AddComponent<BoxCollider2D>();
        go_Wall_30_14_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_14_sr = go_Wall_30_14.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_14_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_14_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_14);

        // --- Wall_30_15 ---
        var go_Wall_30_15 = new GameObject("Wall_30_15");
        go_Wall_30_15.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_15.transform.position = new Vector3(1.5f, -15.0f, 0.0f);
        var go_Wall_30_15_rb = go_Wall_30_15.AddComponent<Rigidbody2D>();
        go_Wall_30_15_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_15_bc = go_Wall_30_15.AddComponent<BoxCollider2D>();
        go_Wall_30_15_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_15_sr = go_Wall_30_15.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_15_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_15_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_15);

        // --- Wall_30_16 ---
        var go_Wall_30_16 = new GameObject("Wall_30_16");
        go_Wall_30_16.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_16.transform.position = new Vector3(2.5f, -15.0f, 0.0f);
        var go_Wall_30_16_rb = go_Wall_30_16.AddComponent<Rigidbody2D>();
        go_Wall_30_16_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_16_bc = go_Wall_30_16.AddComponent<BoxCollider2D>();
        go_Wall_30_16_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_16_sr = go_Wall_30_16.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_16_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_16_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_16);

        // --- Wall_30_17 ---
        var go_Wall_30_17 = new GameObject("Wall_30_17");
        go_Wall_30_17.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_17.transform.position = new Vector3(3.5f, -15.0f, 0.0f);
        var go_Wall_30_17_rb = go_Wall_30_17.AddComponent<Rigidbody2D>();
        go_Wall_30_17_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_17_bc = go_Wall_30_17.AddComponent<BoxCollider2D>();
        go_Wall_30_17_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_17_sr = go_Wall_30_17.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_17_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_17_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_17);

        // --- Wall_30_18 ---
        var go_Wall_30_18 = new GameObject("Wall_30_18");
        go_Wall_30_18.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_18.transform.position = new Vector3(4.5f, -15.0f, 0.0f);
        var go_Wall_30_18_rb = go_Wall_30_18.AddComponent<Rigidbody2D>();
        go_Wall_30_18_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_18_bc = go_Wall_30_18.AddComponent<BoxCollider2D>();
        go_Wall_30_18_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_18_sr = go_Wall_30_18.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_18_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_18_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_18);

        // --- Wall_30_19 ---
        var go_Wall_30_19 = new GameObject("Wall_30_19");
        go_Wall_30_19.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_19.transform.position = new Vector3(5.5f, -15.0f, 0.0f);
        var go_Wall_30_19_rb = go_Wall_30_19.AddComponent<Rigidbody2D>();
        go_Wall_30_19_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_19_bc = go_Wall_30_19.AddComponent<BoxCollider2D>();
        go_Wall_30_19_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_19_sr = go_Wall_30_19.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_19_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_19_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_19);

        // --- Wall_30_20 ---
        var go_Wall_30_20 = new GameObject("Wall_30_20");
        go_Wall_30_20.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_20.transform.position = new Vector3(6.5f, -15.0f, 0.0f);
        var go_Wall_30_20_rb = go_Wall_30_20.AddComponent<Rigidbody2D>();
        go_Wall_30_20_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_20_bc = go_Wall_30_20.AddComponent<BoxCollider2D>();
        go_Wall_30_20_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_20_sr = go_Wall_30_20.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_20_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_20_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_20);

        // --- Wall_30_21 ---
        var go_Wall_30_21 = new GameObject("Wall_30_21");
        go_Wall_30_21.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_21.transform.position = new Vector3(7.5f, -15.0f, 0.0f);
        var go_Wall_30_21_rb = go_Wall_30_21.AddComponent<Rigidbody2D>();
        go_Wall_30_21_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_21_bc = go_Wall_30_21.AddComponent<BoxCollider2D>();
        go_Wall_30_21_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_21_sr = go_Wall_30_21.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_21_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_21_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_21);

        // --- Wall_30_22 ---
        var go_Wall_30_22 = new GameObject("Wall_30_22");
        go_Wall_30_22.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_22.transform.position = new Vector3(8.5f, -15.0f, 0.0f);
        var go_Wall_30_22_rb = go_Wall_30_22.AddComponent<Rigidbody2D>();
        go_Wall_30_22_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_22_bc = go_Wall_30_22.AddComponent<BoxCollider2D>();
        go_Wall_30_22_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_22_sr = go_Wall_30_22.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_22_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_22_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_22);

        // --- Wall_30_23 ---
        var go_Wall_30_23 = new GameObject("Wall_30_23");
        go_Wall_30_23.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_23.transform.position = new Vector3(9.5f, -15.0f, 0.0f);
        var go_Wall_30_23_rb = go_Wall_30_23.AddComponent<Rigidbody2D>();
        go_Wall_30_23_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_23_bc = go_Wall_30_23.AddComponent<BoxCollider2D>();
        go_Wall_30_23_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_23_sr = go_Wall_30_23.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_23_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_23_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_23);

        // --- Wall_30_24 ---
        var go_Wall_30_24 = new GameObject("Wall_30_24");
        go_Wall_30_24.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_24.transform.position = new Vector3(10.5f, -15.0f, 0.0f);
        var go_Wall_30_24_rb = go_Wall_30_24.AddComponent<Rigidbody2D>();
        go_Wall_30_24_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_24_bc = go_Wall_30_24.AddComponent<BoxCollider2D>();
        go_Wall_30_24_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_24_sr = go_Wall_30_24.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_24_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_24_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_24);

        // --- Wall_30_25 ---
        var go_Wall_30_25 = new GameObject("Wall_30_25");
        go_Wall_30_25.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_25.transform.position = new Vector3(11.5f, -15.0f, 0.0f);
        var go_Wall_30_25_rb = go_Wall_30_25.AddComponent<Rigidbody2D>();
        go_Wall_30_25_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_25_bc = go_Wall_30_25.AddComponent<BoxCollider2D>();
        go_Wall_30_25_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_25_sr = go_Wall_30_25.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_25_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_25_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_25);

        // --- Wall_30_26 ---
        var go_Wall_30_26 = new GameObject("Wall_30_26");
        go_Wall_30_26.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_26.transform.position = new Vector3(12.5f, -15.0f, 0.0f);
        var go_Wall_30_26_rb = go_Wall_30_26.AddComponent<Rigidbody2D>();
        go_Wall_30_26_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_26_bc = go_Wall_30_26.AddComponent<BoxCollider2D>();
        go_Wall_30_26_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_26_sr = go_Wall_30_26.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_26_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_26_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_26);

        // --- Wall_30_27 ---
        var go_Wall_30_27 = new GameObject("Wall_30_27");
        go_Wall_30_27.layer = LayerMask.NameToLayer("Layer6");
        go_Wall_30_27.transform.position = new Vector3(13.5f, -15.0f, 0.0f);
        var go_Wall_30_27_rb = go_Wall_30_27.AddComponent<Rigidbody2D>();
        go_Wall_30_27_rb.bodyType = RigidbodyType2D.Static;
        var go_Wall_30_27_bc = go_Wall_30_27.AddComponent<BoxCollider2D>();
        go_Wall_30_27_bc.size = new Vector2(1.0f, 1.0f);
        var go_Wall_30_27_sr = go_Wall_30_27.AddComponent<SpriteRenderer>();
        if (sprite_wall != null) go_Wall_30_27_sr.sprite = sprite_wall;
        if (unlitMat != null) go_Wall_30_27_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Wall_30_27);

        // --- GhostGate_13 ---
        var go_GhostGate_13 = new GameObject("GhostGate_13");
        go_GhostGate_13.layer = LayerMask.NameToLayer("Layer6");
        go_GhostGate_13.transform.position = new Vector3(-0.5f, 3.0f, 0.0f);
        var go_GhostGate_13_rb = go_GhostGate_13.AddComponent<Rigidbody2D>();
        go_GhostGate_13_rb.bodyType = RigidbodyType2D.Static;
        var go_GhostGate_13_bc = go_GhostGate_13.AddComponent<BoxCollider2D>();
        go_GhostGate_13_bc.size = new Vector2(1.0f, 0.5f);
        EditorUtility.SetDirty(go_GhostGate_13);

        // --- GhostGate_14 ---
        var go_GhostGate_14 = new GameObject("GhostGate_14");
        go_GhostGate_14.layer = LayerMask.NameToLayer("Layer6");
        go_GhostGate_14.transform.position = new Vector3(0.5f, 3.0f, 0.0f);
        var go_GhostGate_14_rb = go_GhostGate_14.AddComponent<Rigidbody2D>();
        go_GhostGate_14_rb.bodyType = RigidbodyType2D.Static;
        var go_GhostGate_14_bc = go_GhostGate_14.AddComponent<BoxCollider2D>();
        go_GhostGate_14_bc.size = new Vector2(1.0f, 0.5f);
        EditorUtility.SetDirty(go_GhostGate_14);

        // --- Pacman ---
        var go_Pacman = new GameObject("Pacman");
        go_Pacman.tag = "Pacman";
        go_Pacman.layer = LayerMask.NameToLayer("Layer7");
        go_Pacman.transform.position = new Vector3(0.5f, -8.0f, 0.0f);
        var go_Pacman_rb = go_Pacman.AddComponent<Rigidbody2D>();
        go_Pacman_rb.bodyType = RigidbodyType2D.Kinematic;
        var go_Pacman_cc = go_Pacman.AddComponent<CircleCollider2D>();
        go_Pacman_cc.radius = 0.5f;
        var go_Pacman_sr = go_Pacman.AddComponent<SpriteRenderer>();
        if (sprite_pacman_01 != null) go_Pacman_sr.sprite = sprite_pacman_01;
        if (unlitMat != null) go_Pacman_sr.sharedMaterial = unlitMat;
        go_Pacman_sr.sortingOrder = 5;
        go_Pacman.AddComponent<AnimatedSprite>();
        // AnimatedSprite.animationTime = 0.15
        go_Pacman.AddComponent<Movement>();
        // Movement.obstacleLayer = 6
        // Movement.speed = 8.0
        // Movement.speedMultiplier = 1.0
        go_Pacman.AddComponent<Pacman>();
        EditorUtility.SetDirty(go_Pacman);

        // --- PacmanDeath ---
        var go_PacmanDeath = new GameObject("PacmanDeath");
        go_PacmanDeath.transform.position = new Vector3(0.5f, -8.0f, 0.0f);
        var go_PacmanDeath_sr = go_PacmanDeath.AddComponent<SpriteRenderer>();
        if (sprite_pacman_death_01 != null) go_PacmanDeath_sr.sprite = sprite_pacman_death_01;
        if (unlitMat != null) go_PacmanDeath_sr.sharedMaterial = unlitMat;
        go_PacmanDeath_sr.sortingOrder = 5;
        go_PacmanDeath.AddComponent<AnimatedSprite>();
        // AnimatedSprite.animationTime = 0.1
        EditorUtility.SetDirty(go_PacmanDeath);

        // --- GhostHome_Inside ---
        var go_GhostHome_Inside = new GameObject("GhostHome_Inside");
        go_GhostHome_Inside.transform.position = new Vector3(0.5f, 1.0f, 0.0f);
        EditorUtility.SetDirty(go_GhostHome_Inside);

        // --- GhostHome_Outside ---
        var go_GhostHome_Outside = new GameObject("GhostHome_Outside");
        go_GhostHome_Outside.transform.position = new Vector3(0.5f, 4.0f, 0.0f);
        EditorUtility.SetDirty(go_GhostHome_Outside);

        // --- Blinky ---
        var go_Blinky = new GameObject("Blinky");
        go_Blinky.tag = "Ghost";
        go_Blinky.layer = LayerMask.NameToLayer("Layer8");
        go_Blinky.transform.position = new Vector3(0.5f, 4.0f, 0.0f);
        var go_Blinky_rb = go_Blinky.AddComponent<Rigidbody2D>();
        go_Blinky_rb.bodyType = RigidbodyType2D.Kinematic;
        var go_Blinky_cc = go_Blinky.AddComponent<CircleCollider2D>();
        go_Blinky_cc.radius = 0.5f;
        var go_Blinky_sr = go_Blinky.AddComponent<SpriteRenderer>();
        if (sprite_ghost_blinky != null) go_Blinky_sr.sprite = sprite_ghost_blinky;
        if (unlitMat != null) go_Blinky_sr.sharedMaterial = unlitMat;
        go_Blinky_sr.sortingOrder = 4;
        go_Blinky.AddComponent<Movement>();
        // Movement.obstacleLayer = 6
        // Movement.speed = 7.0
        // Movement.speedMultiplier = 1.0
        go_Blinky.AddComponent<Ghost>();
        // Ghost.points = 200
        go_Blinky.AddComponent<GhostHome>();
        go_Blinky.AddComponent<GhostScatter>();
        // GhostScatter.duration = 7.0
        go_Blinky.AddComponent<GhostChase>();
        // GhostChase.duration = 20.0
        go_Blinky.AddComponent<GhostFrightened>();
        // GhostFrightened.duration = 8.0
        EditorUtility.SetDirty(go_Blinky);

        // --- Pinky ---
        var go_Pinky = new GameObject("Pinky");
        go_Pinky.tag = "Ghost";
        go_Pinky.layer = LayerMask.NameToLayer("Layer8");
        go_Pinky.transform.position = new Vector3(0.5f, 1.0f, 0.0f);
        var go_Pinky_rb = go_Pinky.AddComponent<Rigidbody2D>();
        go_Pinky_rb.bodyType = RigidbodyType2D.Kinematic;
        var go_Pinky_cc = go_Pinky.AddComponent<CircleCollider2D>();
        go_Pinky_cc.radius = 0.5f;
        var go_Pinky_sr = go_Pinky.AddComponent<SpriteRenderer>();
        if (sprite_ghost_pinky != null) go_Pinky_sr.sprite = sprite_ghost_pinky;
        if (unlitMat != null) go_Pinky_sr.sharedMaterial = unlitMat;
        go_Pinky_sr.sortingOrder = 4;
        go_Pinky.AddComponent<Movement>();
        // Movement.obstacleLayer = 6
        // Movement.speed = 7.0
        // Movement.speedMultiplier = 1.0
        go_Pinky.AddComponent<Ghost>();
        // Ghost.points = 200
        go_Pinky.AddComponent<GhostHome>();
        go_Pinky.AddComponent<GhostScatter>();
        // GhostScatter.duration = 7.0
        go_Pinky.AddComponent<GhostChase>();
        // GhostChase.duration = 20.0
        go_Pinky.AddComponent<GhostFrightened>();
        // GhostFrightened.duration = 8.0
        EditorUtility.SetDirty(go_Pinky);

        // --- Inky ---
        var go_Inky = new GameObject("Inky");
        go_Inky.tag = "Ghost";
        go_Inky.layer = LayerMask.NameToLayer("Layer8");
        go_Inky.transform.position = new Vector3(-1.5f, 1.0f, 0.0f);
        var go_Inky_rb = go_Inky.AddComponent<Rigidbody2D>();
        go_Inky_rb.bodyType = RigidbodyType2D.Kinematic;
        var go_Inky_cc = go_Inky.AddComponent<CircleCollider2D>();
        go_Inky_cc.radius = 0.5f;
        var go_Inky_sr = go_Inky.AddComponent<SpriteRenderer>();
        if (sprite_ghost_inky != null) go_Inky_sr.sprite = sprite_ghost_inky;
        if (unlitMat != null) go_Inky_sr.sharedMaterial = unlitMat;
        go_Inky_sr.sortingOrder = 4;
        go_Inky.AddComponent<Movement>();
        // Movement.obstacleLayer = 6
        // Movement.speed = 7.0
        // Movement.speedMultiplier = 1.0
        go_Inky.AddComponent<Ghost>();
        // Ghost.points = 200
        go_Inky.AddComponent<GhostHome>();
        go_Inky.AddComponent<GhostScatter>();
        // GhostScatter.duration = 5.0
        go_Inky.AddComponent<GhostChase>();
        // GhostChase.duration = 20.0
        go_Inky.AddComponent<GhostFrightened>();
        // GhostFrightened.duration = 8.0
        EditorUtility.SetDirty(go_Inky);

        // --- Clyde ---
        var go_Clyde = new GameObject("Clyde");
        go_Clyde.tag = "Ghost";
        go_Clyde.layer = LayerMask.NameToLayer("Layer8");
        go_Clyde.transform.position = new Vector3(2.5f, 1.0f, 0.0f);
        var go_Clyde_rb = go_Clyde.AddComponent<Rigidbody2D>();
        go_Clyde_rb.bodyType = RigidbodyType2D.Kinematic;
        var go_Clyde_cc = go_Clyde.AddComponent<CircleCollider2D>();
        go_Clyde_cc.radius = 0.5f;
        var go_Clyde_sr = go_Clyde.AddComponent<SpriteRenderer>();
        if (sprite_ghost_clyde != null) go_Clyde_sr.sprite = sprite_ghost_clyde;
        if (unlitMat != null) go_Clyde_sr.sharedMaterial = unlitMat;
        go_Clyde_sr.sortingOrder = 4;
        go_Clyde.AddComponent<Movement>();
        // Movement.obstacleLayer = 6
        // Movement.speed = 7.0
        // Movement.speedMultiplier = 1.0
        go_Clyde.AddComponent<Ghost>();
        // Ghost.points = 200
        go_Clyde.AddComponent<GhostHome>();
        go_Clyde.AddComponent<GhostScatter>();
        // GhostScatter.duration = 5.0
        go_Clyde.AddComponent<GhostChase>();
        // GhostChase.duration = 20.0
        go_Clyde.AddComponent<GhostFrightened>();
        // GhostFrightened.duration = 8.0
        EditorUtility.SetDirty(go_Clyde);

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
            var so = new SerializedObject(go_Pellet_1_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_1_1.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_1_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_2.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_3.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_4.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_5.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_1_6.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_1_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_7.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_8.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_10.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_10; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_11.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_11; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_1_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_1_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_1_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_1_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_16.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_16; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_17.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_17; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_19.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_19; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_20.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_20; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_1_21.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_1_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_22.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_22; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_23.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_23; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_24.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_25.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_25; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_1_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_1_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_1_26.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_1_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_2_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_2_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_2_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_2_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_2_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_2_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_2_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_2_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_2_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_2_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_2_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_2_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_3_1.GetComponent<PowerPellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_3_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_3_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_3_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_3_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_3_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_3_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_3_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_3_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_3_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_3_26.GetComponent<PowerPellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_3_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_4_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_4_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_4_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_4_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_4_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_4_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_4_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_4_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_4_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_4_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_4_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_4_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_5_1.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_5_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_2.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_3.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_4.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_5.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_5_6.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_5_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_7.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_8.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_5_9.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_5_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_10.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_10; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_11.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_11; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_5_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_5_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_13.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_13; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_14.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_14; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_5_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_5_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_16.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_16; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_17.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_17; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_5_18.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_5_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_19.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_19; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_20.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_20; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_5_21.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_5_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_22.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_22; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_23.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_23; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_24.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_25.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_25; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_5_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_5_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_5_26.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_5_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_6_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_6_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_6_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_6_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_6_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_6_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_6_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_6_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_6_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_6_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_6_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_6_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_7_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_7_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_7_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_7_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_7_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_7_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_7_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_7_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_7_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_7_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_7_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_7_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_8_1.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_8_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_2.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_3.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_4.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_5.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_8_6.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_8_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_8_9.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_8_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_10.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_10; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_11.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_11; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_8_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_8_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_8_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_8_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_16.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_16; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_17.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_17; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_8_18.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_8_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_8_21.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_8_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_22.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_22; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_23.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_23; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_24.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_25.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_25; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_8_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_8_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_8_26.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_8_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_9_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_9_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_9_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_9_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_10_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_10_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_10_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_10_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_11_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_11_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_11_9.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_11_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_11_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_11_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_11_13.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_11_13; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_11_14.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_11_14; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_11_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_11_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_11_18.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_11_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_11_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_11_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_12_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_12_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_12_13.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_12_13; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_12_14.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_12_14; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_12_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_12_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_13_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_13_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_13_11.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_13_11; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_13_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_13_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_13_13.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_13_13; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_13_14.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_13_14; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_13_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_13_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_13_16.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_13_16; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_13_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_13_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Passage_14_0.GetComponent<Passage>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Passage_14_0; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_14_6.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_14_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_14_7.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_14_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_14_9.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_14_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_14_11.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_14_11; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_14_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_14_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_14_13.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_14_13; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_14_14.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_14_14; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_14_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_14_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_14_16.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_14_16; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_14_18.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_14_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_14_20.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_14_20; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_14_21.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_14_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Passage_14_27.GetComponent<Passage>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Passage_14_27; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_15_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_15_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_15_11.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_15_11; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_15_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_15_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_15_13.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_15_13; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_15_14.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_15_14; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_15_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_15_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_15_16.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_15_16; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_15_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_15_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_16_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_16_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_16_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_16_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_17_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_17_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_17_9.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_17_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_17_18.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_17_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_17_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_17_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_18_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_18_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_18_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_18_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_19_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_19_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_19_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_19_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_20_1.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_20_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_2.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_3.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_4.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_5.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_20_6.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_20_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_7.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_8.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_20_9.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_20_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_10.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_10; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_11.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_11; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_20_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_20_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_20_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_20_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_16.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_16; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_17.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_17; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_20_18.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_20_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_19.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_19; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_20.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_20; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_20_21.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_20_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_22.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_22; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_23.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_23; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_24.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_25.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_25; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_20_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_20_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_20_26.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_20_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_21_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_21_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_21_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_21_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_21_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_21_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_21_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_21_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_21_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_21_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_21_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_21_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_22_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_22_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_22_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_22_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_22_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_22_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_22_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_22_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_22_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_22_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_22_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_22_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_1.GetComponent<PowerPellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_23_1.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_23_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_2.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_3.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_23_3.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_23_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_23_6.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_23_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_7.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_8.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_23_9.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_23_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_10.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_10; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_11.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_11; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_23_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_23_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_14.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_14; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_23_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_23_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_16.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_16; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_17.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_17; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_23_18.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_23_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_19.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_19; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_20.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_20; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_23_21.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_23_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_24.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_23_24.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_23_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_25.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_25; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_23_26.GetComponent<PowerPellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_23_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_23_26.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_23_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_24_3.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_24_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_24_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_24_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_24_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_24_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_24_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_24_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_24_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_24_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_24_24.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_24_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_25_3.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_25_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_25_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_25_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_25_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_25_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_25_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_25_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_25_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_25_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_25_24.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_25_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_26_1.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_26_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_2.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_3.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_26_3.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_26_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_4.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_5.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_26_6.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_26_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_26_9.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_26_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_10.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_10; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_11.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_11; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_26_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_26_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_26_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_26_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_16.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_16; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_17.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_17; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_26_18.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_26_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_26_21.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_26_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_22.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_22; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_23.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_23; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_24.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_26_24.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_26_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_25.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_25; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_26_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_26_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_26_26.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_26_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_27_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_27_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_27_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_27_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_27_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_27_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_27_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_27_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_28_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_28_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_28_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_28_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_28_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_28_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_28_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_28_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_1.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_29_1.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_29_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_2.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_3.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_4.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_5.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_6.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_7.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_8.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_9.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_10.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_10; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_11.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_11; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_12.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_29_12.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_29_12; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_13.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_13; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_14.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_14; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_15.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_29_15.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_29_15; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_16.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_16; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_17.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_17; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_18.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_18; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_19.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_19; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_20.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_20; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_21.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_21; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_22.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_22; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_23.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_23; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_24.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_24; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_25.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_25; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pellet_29_26.GetComponent<Pellet>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pellet_29_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Node_29_26.GetComponent<Node>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Node_29_26; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pacman.GetComponent<AnimatedSprite>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pacman; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pacman.GetComponent<Movement>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pacman; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pacman.GetComponent<Pacman>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pacman; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_PacmanDeath.GetComponent<AnimatedSprite>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_PacmanDeath; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Blinky.GetComponent<Movement>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Blinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Blinky.GetComponent<Ghost>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Blinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Blinky.GetComponent<GhostHome>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Blinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Blinky.GetComponent<GhostScatter>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Blinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Blinky.GetComponent<GhostChase>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Blinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Blinky.GetComponent<GhostFrightened>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Blinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pinky.GetComponent<Movement>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pinky.GetComponent<Ghost>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pinky.GetComponent<GhostHome>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pinky.GetComponent<GhostScatter>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pinky.GetComponent<GhostChase>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pinky.GetComponent<GhostFrightened>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pinky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Inky.GetComponent<Movement>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Inky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Inky.GetComponent<Ghost>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Inky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Inky.GetComponent<GhostHome>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Inky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Inky.GetComponent<GhostScatter>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Inky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Inky.GetComponent<GhostChase>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Inky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Inky.GetComponent<GhostFrightened>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Inky; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Clyde.GetComponent<Movement>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Clyde; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Clyde.GetComponent<Ghost>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Clyde; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Clyde.GetComponent<GhostHome>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Clyde; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Clyde.GetComponent<GhostScatter>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Clyde; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Clyde.GetComponent<GhostChase>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Clyde; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Clyde.GetComponent<GhostFrightened>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Clyde; so.ApplyModifiedProperties(); }
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

        result = "Scene setup complete: 894 GameObjects";
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
