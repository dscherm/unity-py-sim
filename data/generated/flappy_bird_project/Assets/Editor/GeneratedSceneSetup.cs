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
        _EnsureTag(tagsProp, "Obstacle");
        _EnsureTag(tagsProp, "Scoring");
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
        var sprite_bird_01 = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Bird_01.png");
        var sprite_bird_02 = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Bird_02.png");
        var sprite_bird_03 = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Bird_03.png");
        var sprite_background = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Background.png");
        var sprite_ground = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Ground.png");
        var sprite_pipe = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Pipe.png");
        var sprite_game_over = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/GameOver.png");
        var sprite_get_ready = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/GetReady.png");
        var sprite_play_button = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/PlayButton.png");

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
            cam.orthographicSize = 5.0f;
            cam.backgroundColor = new Color(0.443f, 0.773f, 0.812f, 1f);
            cam.clearFlags = CameraClearFlags.SolidColor;
            go_MainCamera.transform.position = new Vector3(0f, 0f, -10f);
            EditorUtility.SetDirty(go_MainCamera);
        }

        // --- Player ---
        var go_Player = new GameObject("Player");
        go_Player.transform.position = new Vector3(-2.0f, 0.0f, 0.0f);
        var go_Player_sr = go_Player.AddComponent<SpriteRenderer>();
        if (sprite_bird_01 != null) go_Player_sr.sprite = sprite_bird_01;
        if (unlitMat != null) go_Player_sr.sharedMaterial = unlitMat;
        var go_Player_bc = go_Player.AddComponent<BoxCollider2D>();
        go_Player_bc.size = new Vector2(0.6f, 0.4f);
        go_Player_bc.isTrigger = true;
        var go_Player_rb = go_Player.AddComponent<Rigidbody2D>();
        go_Player_rb.bodyType = RigidbodyType2D.Kinematic;
        go_Player.AddComponent<Player>();
        {
            var so = new SerializedObject(go_Player.GetComponent<Player>());
            var prop_gravity = so.FindProperty("gravity");
            if (prop_gravity != null) prop_gravity.floatValue = -9.81f;
            var prop_strength = so.FindProperty("strength");
            if (prop_strength != null) prop_strength.floatValue = 5.0f;
            var prop_tilt = so.FindProperty("tilt");
            if (prop_tilt != null) prop_tilt.floatValue = 5.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Player);

        // --- Ground ---
        var go_Ground = new GameObject("Ground");
        go_Ground.tag = "Obstacle";
        go_Ground.transform.position = new Vector3(0.0f, -5.5f, 0.0f);
        var go_Ground_sr = go_Ground.AddComponent<SpriteRenderer>();
        if (sprite_ground != null) go_Ground_sr.sprite = sprite_ground;
        if (unlitMat != null) go_Ground_sr.sharedMaterial = unlitMat;
        var go_Ground_bc = go_Ground.AddComponent<BoxCollider2D>();
        go_Ground_bc.size = new Vector2(20.0f, 1.0f);
        go_Ground_bc.isTrigger = true;
        var go_Ground_rb = go_Ground.AddComponent<Rigidbody2D>();
        go_Ground_rb.bodyType = RigidbodyType2D.Static;
        EditorUtility.SetDirty(go_Ground);

        // --- Ceiling ---
        var go_Ceiling = new GameObject("Ceiling");
        go_Ceiling.tag = "Obstacle";
        go_Ceiling.transform.position = new Vector3(0.0f, 5.5f, 0.0f);
        var go_Ceiling_bc = go_Ceiling.AddComponent<BoxCollider2D>();
        go_Ceiling_bc.size = new Vector2(20.0f, 1.0f);
        go_Ceiling_bc.isTrigger = true;
        var go_Ceiling_rb = go_Ceiling.AddComponent<Rigidbody2D>();
        go_Ceiling_rb.bodyType = RigidbodyType2D.Static;
        EditorUtility.SetDirty(go_Ceiling);

        // --- Pipes ---
        var go_Pipes = new GameObject("Pipes");
        go_Pipes.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        go_Pipes.AddComponent<Pipes>();
        {
            var so = new SerializedObject(go_Pipes.GetComponent<Pipes>());
            var prop_gap = so.FindProperty("gap");
            if (prop_gap != null) prop_gap.floatValue = 3.0f;
            var prop_speed = so.FindProperty("speed");
            if (prop_speed != null) prop_speed.floatValue = 5.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Pipes);

        // --- Top ---
        var go_Top = new GameObject("Top");
        go_Top.tag = "Obstacle";
        go_Top.transform.SetParent(go_Pipes.transform, false);
        go_Top.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        var go_Top_sr = go_Top.AddComponent<SpriteRenderer>();
        if (sprite_pipe != null) go_Top_sr.sprite = sprite_pipe;
        if (unlitMat != null) go_Top_sr.sharedMaterial = unlitMat;
        var go_Top_bc = go_Top.AddComponent<BoxCollider2D>();
        go_Top_bc.size = new Vector2(1.0f, 8.0f);
        go_Top_bc.isTrigger = true;
        var go_Top_rb = go_Top.AddComponent<Rigidbody2D>();
        go_Top_rb.bodyType = RigidbodyType2D.Kinematic;
        EditorUtility.SetDirty(go_Top);

        // --- Bottom ---
        var go_Bottom = new GameObject("Bottom");
        go_Bottom.tag = "Obstacle";
        go_Bottom.transform.SetParent(go_Pipes.transform, false);
        go_Bottom.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        var go_Bottom_sr = go_Bottom.AddComponent<SpriteRenderer>();
        if (sprite_pipe != null) go_Bottom_sr.sprite = sprite_pipe;
        if (unlitMat != null) go_Bottom_sr.sharedMaterial = unlitMat;
        var go_Bottom_bc = go_Bottom.AddComponent<BoxCollider2D>();
        go_Bottom_bc.size = new Vector2(1.0f, 8.0f);
        go_Bottom_bc.isTrigger = true;
        var go_Bottom_rb = go_Bottom.AddComponent<Rigidbody2D>();
        go_Bottom_rb.bodyType = RigidbodyType2D.Kinematic;
        EditorUtility.SetDirty(go_Bottom);

        // --- Scoring ---
        var go_Scoring = new GameObject("Scoring");
        go_Scoring.tag = "Scoring";
        go_Scoring.transform.SetParent(go_Pipes.transform, false);
        go_Scoring.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        var go_Scoring_bc = go_Scoring.AddComponent<BoxCollider2D>();
        go_Scoring_bc.size = new Vector2(1.0f, 6.0f);
        go_Scoring_bc.isTrigger = true;
        var go_Scoring_rb = go_Scoring.AddComponent<Rigidbody2D>();
        go_Scoring_rb.bodyType = RigidbodyType2D.Kinematic;
        EditorUtility.SetDirty(go_Scoring);

        // --- Spawner ---
        var go_Spawner = new GameObject("Spawner");
        go_Spawner.transform.position = new Vector3(8.0f, 0.0f, 0.0f);
        go_Spawner.AddComponent<Spawner>();
        {
            var so = new SerializedObject(go_Spawner.GetComponent<Spawner>());
            var prop_maxHeight = so.FindProperty("maxHeight");
            if (prop_maxHeight != null) prop_maxHeight.floatValue = 1.5f;
            var prop_minHeight = so.FindProperty("minHeight");
            if (prop_minHeight != null) prop_minHeight.floatValue = -1.5f;
            var prop_spawnRate = so.FindProperty("spawnRate");
            if (prop_spawnRate != null) prop_spawnRate.floatValue = 1.5f;
            var prop_verticalGap = so.FindProperty("verticalGap");
            if (prop_verticalGap != null) prop_verticalGap.floatValue = 3.5f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Spawner);

        // --- Background ---
        var go_Background = new GameObject("Background");
        go_Background.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        var go_Background_sr = go_Background.AddComponent<SpriteRenderer>();
        if (sprite_background != null) go_Background_sr.sprite = sprite_background;
        if (unlitMat != null) go_Background_sr.sharedMaterial = unlitMat;
        go_Background_sr.sortingOrder = -10;
        go_Background.AddComponent<Parallax>();
        {
            var so = new SerializedObject(go_Background.GetComponent<Parallax>());
            var prop_animationSpeed = so.FindProperty("animationSpeed");
            if (prop_animationSpeed != null) prop_animationSpeed.floatValue = 0.5f;
            var prop_wrapWidth = so.FindProperty("wrapWidth");
            if (prop_wrapWidth != null) prop_wrapWidth.floatValue = 20.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Background);

        // --- GroundParallax ---
        var go_GroundParallax = new GameObject("GroundParallax");
        go_GroundParallax.transform.position = new Vector3(0.0f, -5.0f, 0.0f);
        var go_GroundParallax_sr = go_GroundParallax.AddComponent<SpriteRenderer>();
        if (sprite_ground != null) go_GroundParallax_sr.sprite = sprite_ground;
        if (unlitMat != null) go_GroundParallax_sr.sharedMaterial = unlitMat;
        go_GroundParallax_sr.sortingOrder = 5;
        go_GroundParallax.AddComponent<Parallax>();
        {
            var so = new SerializedObject(go_GroundParallax.GetComponent<Parallax>());
            var prop_animationSpeed = so.FindProperty("animationSpeed");
            if (prop_animationSpeed != null) prop_animationSpeed.floatValue = 2.0f;
            var prop_wrapWidth = so.FindProperty("wrapWidth");
            if (prop_wrapWidth != null) prop_wrapWidth.floatValue = 20.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_GroundParallax);

        // --- Canvas ---
        var go_Canvas = new GameObject("Canvas");
        go_Canvas.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        EditorUtility.SetDirty(go_Canvas);

        // --- ScoreText ---
        var go_ScoreText = new GameObject("ScoreText");
        go_ScoreText.transform.SetParent(go_Canvas.transform, false);
        go_ScoreText.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        EditorUtility.SetDirty(go_ScoreText);

        // --- GameOver ---
        var go_GameOver = new GameObject("GameOver");
        EditorUtility.SetDirty(go_GameOver);

        // --- PlayButton ---
        var go_PlayButton = new GameObject("PlayButton");
        EditorUtility.SetDirty(go_PlayButton);

        // --- GameManager ---
        var go_GameManager = new GameObject("GameManager");
        go_GameManager.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        go_GameManager.AddComponent<GameManager>();
        EditorUtility.SetDirty(go_GameManager);

        // --- PlayButtonHandler ---
        var go_PlayButtonHandler = new GameObject("PlayButtonHandler");
        EditorUtility.SetDirty(go_PlayButtonHandler);

        // === WIRE CROSS-REFERENCES ===
        {
            var so = new SerializedObject(go_Player.GetComponent<Player>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Player; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pipes.GetComponent<Pipes>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pipes; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Spawner.GetComponent<Spawner>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Spawner; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Spawner.GetComponent<Spawner>());
            var prop = so.FindProperty("prefab");
            if (prop != null) { prop.objectReferenceValue = go_Pipes; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Background.GetComponent<Parallax>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Background; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_GroundParallax.GetComponent<Parallax>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_GroundParallax; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_GameManager.GetComponent<GameManager>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_GameManager; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_GameManager.GetComponent<GameManager>());
            var prop = so.FindProperty("gameOverDisplay");
            if (prop != null) { prop.objectReferenceValue = go_GameOver; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_GameManager.GetComponent<GameManager>());
            var prop = so.FindProperty("playButton");
            if (prop != null) { prop.objectReferenceValue = go_PlayButton; so.ApplyModifiedProperties(); }
        }

        // === SAVE ===
        UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(
            UnityEditor.SceneManagement.EditorSceneManager.GetActiveScene());
        UnityEditor.SceneManagement.EditorSceneManager.SaveOpenScenes();

        result = "Scene setup complete: 17 GameObjects";
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
