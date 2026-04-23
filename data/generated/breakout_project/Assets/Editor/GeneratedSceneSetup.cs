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
        _EnsureTag(tagsProp, "Ball");
        _EnsureTag(tagsProp, "Brick");
        _EnsureTag(tagsProp, "Paddle");
        _EnsureTag(tagsProp, "Wall");
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
        var sprite_paddle = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/paddle.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "paddle_0");
        var sprite_ball = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/ball.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "ball_0");
        var sprite_brick = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/brick.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "brick_0");

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
            cam.backgroundColor = new Color(0.059f, 0.059f, 0.098f, 1f);
            cam.clearFlags = CameraClearFlags.SolidColor;
            go_MainCamera.transform.position = new Vector3(0f, 0f, -10f);
            if (go_MainCamera.GetComponent<AspectLock>() == null)
                go_MainCamera.AddComponent<AspectLock>();
            EditorUtility.SetDirty(go_MainCamera);
        }

        // --- Paddle ---
        var go_Paddle = new GameObject("Paddle");
        go_Paddle.tag = "Paddle";
        go_Paddle.transform.position = new Vector3(0.0f, -5.0f, 0.0f);
        var go_Paddle_rb = go_Paddle.AddComponent<Rigidbody2D>();
        go_Paddle_rb.bodyType = RigidbodyType2D.Kinematic;
        var go_Paddle_bc = go_Paddle.AddComponent<BoxCollider2D>();
        go_Paddle_bc.size = new Vector2(2.0f, 0.4f);
        var go_Paddle_sr = go_Paddle.AddComponent<SpriteRenderer>();
        if (sprite_paddle != null) go_Paddle_sr.sprite = sprite_paddle;
        if (unlitMat != null) go_Paddle_sr.sharedMaterial = unlitMat;
        go_Paddle.AddComponent<Breakout.PaddleController>();
        {
            var so = new SerializedObject(go_Paddle.GetComponent<Breakout.PaddleController>());
            var prop_boundX = so.FindProperty("boundX");
            if (prop_boundX != null) prop_boundX.floatValue = 6.5f;
            var prop_speed = so.FindProperty("speed");
            if (prop_speed != null) prop_speed.floatValue = 12.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Paddle);

        // --- Ball ---
        var go_Ball = new GameObject("Ball");
        go_Ball.tag = "Ball";
        go_Ball.transform.position = new Vector3(0.0f, -4.4f, 0.0f);
        var go_Ball_rb = go_Ball.AddComponent<Rigidbody2D>();
        go_Ball_rb.mass = 0.1f;
        go_Ball_rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
        {
            var _mat = AssetDatabase.LoadAssetAtPath<PhysicsMaterial2D>("Assets/Art/BouncyBall.physicsMaterial2D");
            if (_mat != null) go_Ball_rb.sharedMaterial = _mat;
        }
        var go_Ball_cc = go_Ball.AddComponent<CircleCollider2D>();
        go_Ball_cc.radius = 0.2f;
        {
            var _mat = AssetDatabase.LoadAssetAtPath<PhysicsMaterial2D>("Assets/Art/BouncyBall.physicsMaterial2D");
            if (_mat != null) go_Ball_cc.sharedMaterial = _mat;
        }
        var go_Ball_sr = go_Ball.AddComponent<SpriteRenderer>();
        if (sprite_ball != null) go_Ball_sr.sprite = sprite_ball;
        if (unlitMat != null) go_Ball_sr.sharedMaterial = unlitMat;
        go_Ball.AddComponent<AudioSource>();
        go_Ball.AddComponent<Breakout.BallController>();
        {
            var so = new SerializedObject(go_Ball.GetComponent<Breakout.BallController>());
            var prop_maxSpeed = so.FindProperty("maxSpeed");
            if (prop_maxSpeed != null) prop_maxSpeed.floatValue = 12.0f;
            var prop_speed = so.FindProperty("speed");
            if (prop_speed != null) prop_speed.floatValue = 6.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Ball);

        // --- LeftWall ---
        var go_LeftWall = new GameObject("LeftWall");
        go_LeftWall.tag = "Wall";
        go_LeftWall.transform.position = new Vector3(-8.0f, 0.0f, 0.0f);
        var go_LeftWall_rb = go_LeftWall.AddComponent<Rigidbody2D>();
        go_LeftWall_rb.bodyType = RigidbodyType2D.Static;
        var go_LeftWall_bc = go_LeftWall.AddComponent<BoxCollider2D>();
        go_LeftWall_bc.size = new Vector2(1.0f, 14.0f);
        EditorUtility.SetDirty(go_LeftWall);

        // --- RightWall ---
        var go_RightWall = new GameObject("RightWall");
        go_RightWall.tag = "Wall";
        go_RightWall.transform.position = new Vector3(8.0f, 0.0f, 0.0f);
        var go_RightWall_rb = go_RightWall.AddComponent<Rigidbody2D>();
        go_RightWall_rb.bodyType = RigidbodyType2D.Static;
        var go_RightWall_bc = go_RightWall.AddComponent<BoxCollider2D>();
        go_RightWall_bc.size = new Vector2(1.0f, 14.0f);
        EditorUtility.SetDirty(go_RightWall);

        // --- TopWall ---
        var go_TopWall = new GameObject("TopWall");
        go_TopWall.tag = "Wall";
        go_TopWall.transform.position = new Vector3(0.0f, 6.5f, 0.0f);
        var go_TopWall_rb = go_TopWall.AddComponent<Rigidbody2D>();
        go_TopWall_rb.bodyType = RigidbodyType2D.Static;
        var go_TopWall_bc = go_TopWall.AddComponent<BoxCollider2D>();
        go_TopWall_bc.size = new Vector2(18.0f, 1.0f);
        EditorUtility.SetDirty(go_TopWall);

        // --- Brick_0_0 ---
        var go_Brick_0_0 = new GameObject("Brick_0_0");
        go_Brick_0_0.tag = "Brick";
        go_Brick_0_0.transform.position = new Vector3(-6.300000000000001f, 4.5f, 0.0f);
        var go_Brick_0_0_rb = go_Brick_0_0.AddComponent<Rigidbody2D>();
        go_Brick_0_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_0_0_bc = go_Brick_0_0.AddComponent<BoxCollider2D>();
        go_Brick_0_0_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_0_0_sr = go_Brick_0_0.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_0_0_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_0_0_sr.sharedMaterial = unlitMat;
        go_Brick_0_0.AddComponent<AudioSource>();
        go_Brick_0_0.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_0_0.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_0_0);

        // --- Brick_0_1 ---
        var go_Brick_0_1 = new GameObject("Brick_0_1");
        go_Brick_0_1.tag = "Brick";
        go_Brick_0_1.transform.position = new Vector3(-4.9f, 4.5f, 0.0f);
        var go_Brick_0_1_rb = go_Brick_0_1.AddComponent<Rigidbody2D>();
        go_Brick_0_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_0_1_bc = go_Brick_0_1.AddComponent<BoxCollider2D>();
        go_Brick_0_1_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_0_1_sr = go_Brick_0_1.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_0_1_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_0_1_sr.sharedMaterial = unlitMat;
        go_Brick_0_1.AddComponent<AudioSource>();
        go_Brick_0_1.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_0_1.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_0_1);

        // --- Brick_0_2 ---
        var go_Brick_0_2 = new GameObject("Brick_0_2");
        go_Brick_0_2.tag = "Brick";
        go_Brick_0_2.transform.position = new Vector3(-3.5000000000000004f, 4.5f, 0.0f);
        var go_Brick_0_2_rb = go_Brick_0_2.AddComponent<Rigidbody2D>();
        go_Brick_0_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_0_2_bc = go_Brick_0_2.AddComponent<BoxCollider2D>();
        go_Brick_0_2_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_0_2_sr = go_Brick_0_2.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_0_2_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_0_2_sr.sharedMaterial = unlitMat;
        go_Brick_0_2.AddComponent<AudioSource>();
        go_Brick_0_2.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_0_2.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_0_2);

        // --- Brick_0_3 ---
        var go_Brick_0_3 = new GameObject("Brick_0_3");
        go_Brick_0_3.tag = "Brick";
        go_Brick_0_3.transform.position = new Vector3(-2.1000000000000005f, 4.5f, 0.0f);
        var go_Brick_0_3_rb = go_Brick_0_3.AddComponent<Rigidbody2D>();
        go_Brick_0_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_0_3_bc = go_Brick_0_3.AddComponent<BoxCollider2D>();
        go_Brick_0_3_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_0_3_sr = go_Brick_0_3.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_0_3_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_0_3_sr.sharedMaterial = unlitMat;
        go_Brick_0_3.AddComponent<AudioSource>();
        go_Brick_0_3.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_0_3.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_0_3);

        // --- Brick_0_4 ---
        var go_Brick_0_4 = new GameObject("Brick_0_4");
        go_Brick_0_4.tag = "Brick";
        go_Brick_0_4.transform.position = new Vector3(-0.7000000000000002f, 4.5f, 0.0f);
        var go_Brick_0_4_rb = go_Brick_0_4.AddComponent<Rigidbody2D>();
        go_Brick_0_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_0_4_bc = go_Brick_0_4.AddComponent<BoxCollider2D>();
        go_Brick_0_4_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_0_4_sr = go_Brick_0_4.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_0_4_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_0_4_sr.sharedMaterial = unlitMat;
        go_Brick_0_4.AddComponent<AudioSource>();
        go_Brick_0_4.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_0_4.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_0_4);

        // --- Brick_0_5 ---
        var go_Brick_0_5 = new GameObject("Brick_0_5");
        go_Brick_0_5.tag = "Brick";
        go_Brick_0_5.transform.position = new Vector3(0.7000000000000002f, 4.5f, 0.0f);
        var go_Brick_0_5_rb = go_Brick_0_5.AddComponent<Rigidbody2D>();
        go_Brick_0_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_0_5_bc = go_Brick_0_5.AddComponent<BoxCollider2D>();
        go_Brick_0_5_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_0_5_sr = go_Brick_0_5.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_0_5_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_0_5_sr.sharedMaterial = unlitMat;
        go_Brick_0_5.AddComponent<AudioSource>();
        go_Brick_0_5.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_0_5.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_0_5);

        // --- Brick_0_6 ---
        var go_Brick_0_6 = new GameObject("Brick_0_6");
        go_Brick_0_6.tag = "Brick";
        go_Brick_0_6.transform.position = new Vector3(2.0999999999999996f, 4.5f, 0.0f);
        var go_Brick_0_6_rb = go_Brick_0_6.AddComponent<Rigidbody2D>();
        go_Brick_0_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_0_6_bc = go_Brick_0_6.AddComponent<BoxCollider2D>();
        go_Brick_0_6_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_0_6_sr = go_Brick_0_6.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_0_6_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_0_6_sr.sharedMaterial = unlitMat;
        go_Brick_0_6.AddComponent<AudioSource>();
        go_Brick_0_6.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_0_6.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_0_6);

        // --- Brick_0_7 ---
        var go_Brick_0_7 = new GameObject("Brick_0_7");
        go_Brick_0_7.tag = "Brick";
        go_Brick_0_7.transform.position = new Vector3(3.5f, 4.5f, 0.0f);
        var go_Brick_0_7_rb = go_Brick_0_7.AddComponent<Rigidbody2D>();
        go_Brick_0_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_0_7_bc = go_Brick_0_7.AddComponent<BoxCollider2D>();
        go_Brick_0_7_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_0_7_sr = go_Brick_0_7.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_0_7_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_0_7_sr.sharedMaterial = unlitMat;
        go_Brick_0_7.AddComponent<AudioSource>();
        go_Brick_0_7.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_0_7.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_0_7);

        // --- Brick_0_8 ---
        var go_Brick_0_8 = new GameObject("Brick_0_8");
        go_Brick_0_8.tag = "Brick";
        go_Brick_0_8.transform.position = new Vector3(4.9f, 4.5f, 0.0f);
        var go_Brick_0_8_rb = go_Brick_0_8.AddComponent<Rigidbody2D>();
        go_Brick_0_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_0_8_bc = go_Brick_0_8.AddComponent<BoxCollider2D>();
        go_Brick_0_8_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_0_8_sr = go_Brick_0_8.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_0_8_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_0_8_sr.sharedMaterial = unlitMat;
        go_Brick_0_8.AddComponent<AudioSource>();
        go_Brick_0_8.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_0_8.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_0_8);

        // --- Brick_0_9 ---
        var go_Brick_0_9 = new GameObject("Brick_0_9");
        go_Brick_0_9.tag = "Brick";
        go_Brick_0_9.transform.position = new Vector3(6.300000000000001f, 4.5f, 0.0f);
        var go_Brick_0_9_rb = go_Brick_0_9.AddComponent<Rigidbody2D>();
        go_Brick_0_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_0_9_bc = go_Brick_0_9.AddComponent<BoxCollider2D>();
        go_Brick_0_9_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_0_9_sr = go_Brick_0_9.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_0_9_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_0_9_sr.sharedMaterial = unlitMat;
        go_Brick_0_9.AddComponent<AudioSource>();
        go_Brick_0_9.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_0_9.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_0_9);

        // --- Brick_1_0 ---
        var go_Brick_1_0 = new GameObject("Brick_1_0");
        go_Brick_1_0.tag = "Brick";
        go_Brick_1_0.transform.position = new Vector3(-6.300000000000001f, 3.9f, 0.0f);
        var go_Brick_1_0_rb = go_Brick_1_0.AddComponent<Rigidbody2D>();
        go_Brick_1_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_1_0_bc = go_Brick_1_0.AddComponent<BoxCollider2D>();
        go_Brick_1_0_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_1_0_sr = go_Brick_1_0.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_1_0_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_1_0_sr.sharedMaterial = unlitMat;
        go_Brick_1_0.AddComponent<AudioSource>();
        go_Brick_1_0.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_1_0.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_1_0);

        // --- Brick_1_1 ---
        var go_Brick_1_1 = new GameObject("Brick_1_1");
        go_Brick_1_1.tag = "Brick";
        go_Brick_1_1.transform.position = new Vector3(-4.9f, 3.9f, 0.0f);
        var go_Brick_1_1_rb = go_Brick_1_1.AddComponent<Rigidbody2D>();
        go_Brick_1_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_1_1_bc = go_Brick_1_1.AddComponent<BoxCollider2D>();
        go_Brick_1_1_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_1_1_sr = go_Brick_1_1.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_1_1_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_1_1_sr.sharedMaterial = unlitMat;
        go_Brick_1_1.AddComponent<AudioSource>();
        go_Brick_1_1.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_1_1.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_1_1);

        // --- Brick_1_2 ---
        var go_Brick_1_2 = new GameObject("Brick_1_2");
        go_Brick_1_2.tag = "Brick";
        go_Brick_1_2.transform.position = new Vector3(-3.5000000000000004f, 3.9f, 0.0f);
        var go_Brick_1_2_rb = go_Brick_1_2.AddComponent<Rigidbody2D>();
        go_Brick_1_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_1_2_bc = go_Brick_1_2.AddComponent<BoxCollider2D>();
        go_Brick_1_2_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_1_2_sr = go_Brick_1_2.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_1_2_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_1_2_sr.sharedMaterial = unlitMat;
        go_Brick_1_2.AddComponent<AudioSource>();
        go_Brick_1_2.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_1_2.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_1_2);

        // --- Brick_1_3 ---
        var go_Brick_1_3 = new GameObject("Brick_1_3");
        go_Brick_1_3.tag = "Brick";
        go_Brick_1_3.transform.position = new Vector3(-2.1000000000000005f, 3.9f, 0.0f);
        var go_Brick_1_3_rb = go_Brick_1_3.AddComponent<Rigidbody2D>();
        go_Brick_1_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_1_3_bc = go_Brick_1_3.AddComponent<BoxCollider2D>();
        go_Brick_1_3_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_1_3_sr = go_Brick_1_3.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_1_3_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_1_3_sr.sharedMaterial = unlitMat;
        go_Brick_1_3.AddComponent<AudioSource>();
        go_Brick_1_3.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_1_3.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_1_3);

        // --- Brick_1_4 ---
        var go_Brick_1_4 = new GameObject("Brick_1_4");
        go_Brick_1_4.tag = "Brick";
        go_Brick_1_4.transform.position = new Vector3(-0.7000000000000002f, 3.9f, 0.0f);
        var go_Brick_1_4_rb = go_Brick_1_4.AddComponent<Rigidbody2D>();
        go_Brick_1_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_1_4_bc = go_Brick_1_4.AddComponent<BoxCollider2D>();
        go_Brick_1_4_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_1_4_sr = go_Brick_1_4.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_1_4_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_1_4_sr.sharedMaterial = unlitMat;
        go_Brick_1_4.AddComponent<AudioSource>();
        go_Brick_1_4.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_1_4.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_1_4);

        // --- Brick_1_5 ---
        var go_Brick_1_5 = new GameObject("Brick_1_5");
        go_Brick_1_5.tag = "Brick";
        go_Brick_1_5.transform.position = new Vector3(0.7000000000000002f, 3.9f, 0.0f);
        var go_Brick_1_5_rb = go_Brick_1_5.AddComponent<Rigidbody2D>();
        go_Brick_1_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_1_5_bc = go_Brick_1_5.AddComponent<BoxCollider2D>();
        go_Brick_1_5_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_1_5_sr = go_Brick_1_5.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_1_5_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_1_5_sr.sharedMaterial = unlitMat;
        go_Brick_1_5.AddComponent<AudioSource>();
        go_Brick_1_5.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_1_5.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_1_5);

        // --- Brick_1_6 ---
        var go_Brick_1_6 = new GameObject("Brick_1_6");
        go_Brick_1_6.tag = "Brick";
        go_Brick_1_6.transform.position = new Vector3(2.0999999999999996f, 3.9f, 0.0f);
        var go_Brick_1_6_rb = go_Brick_1_6.AddComponent<Rigidbody2D>();
        go_Brick_1_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_1_6_bc = go_Brick_1_6.AddComponent<BoxCollider2D>();
        go_Brick_1_6_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_1_6_sr = go_Brick_1_6.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_1_6_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_1_6_sr.sharedMaterial = unlitMat;
        go_Brick_1_6.AddComponent<AudioSource>();
        go_Brick_1_6.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_1_6.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_1_6);

        // --- Brick_1_7 ---
        var go_Brick_1_7 = new GameObject("Brick_1_7");
        go_Brick_1_7.tag = "Brick";
        go_Brick_1_7.transform.position = new Vector3(3.5f, 3.9f, 0.0f);
        var go_Brick_1_7_rb = go_Brick_1_7.AddComponent<Rigidbody2D>();
        go_Brick_1_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_1_7_bc = go_Brick_1_7.AddComponent<BoxCollider2D>();
        go_Brick_1_7_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_1_7_sr = go_Brick_1_7.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_1_7_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_1_7_sr.sharedMaterial = unlitMat;
        go_Brick_1_7.AddComponent<AudioSource>();
        go_Brick_1_7.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_1_7.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_1_7);

        // --- Brick_1_8 ---
        var go_Brick_1_8 = new GameObject("Brick_1_8");
        go_Brick_1_8.tag = "Brick";
        go_Brick_1_8.transform.position = new Vector3(4.9f, 3.9f, 0.0f);
        var go_Brick_1_8_rb = go_Brick_1_8.AddComponent<Rigidbody2D>();
        go_Brick_1_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_1_8_bc = go_Brick_1_8.AddComponent<BoxCollider2D>();
        go_Brick_1_8_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_1_8_sr = go_Brick_1_8.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_1_8_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_1_8_sr.sharedMaterial = unlitMat;
        go_Brick_1_8.AddComponent<AudioSource>();
        go_Brick_1_8.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_1_8.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_1_8);

        // --- Brick_1_9 ---
        var go_Brick_1_9 = new GameObject("Brick_1_9");
        go_Brick_1_9.tag = "Brick";
        go_Brick_1_9.transform.position = new Vector3(6.300000000000001f, 3.9f, 0.0f);
        var go_Brick_1_9_rb = go_Brick_1_9.AddComponent<Rigidbody2D>();
        go_Brick_1_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_1_9_bc = go_Brick_1_9.AddComponent<BoxCollider2D>();
        go_Brick_1_9_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_1_9_sr = go_Brick_1_9.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_1_9_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_1_9_sr.sharedMaterial = unlitMat;
        go_Brick_1_9.AddComponent<AudioSource>();
        go_Brick_1_9.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_1_9.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 30;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_1_9);

        // --- Brick_2_0 ---
        var go_Brick_2_0 = new GameObject("Brick_2_0");
        go_Brick_2_0.tag = "Brick";
        go_Brick_2_0.transform.position = new Vector3(-6.300000000000001f, 3.3f, 0.0f);
        var go_Brick_2_0_rb = go_Brick_2_0.AddComponent<Rigidbody2D>();
        go_Brick_2_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_2_0_bc = go_Brick_2_0.AddComponent<BoxCollider2D>();
        go_Brick_2_0_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_2_0_sr = go_Brick_2_0.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_2_0_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_2_0_sr.sharedMaterial = unlitMat;
        go_Brick_2_0.AddComponent<AudioSource>();
        go_Brick_2_0.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_2_0.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_2_0);

        // --- Brick_2_1 ---
        var go_Brick_2_1 = new GameObject("Brick_2_1");
        go_Brick_2_1.tag = "Brick";
        go_Brick_2_1.transform.position = new Vector3(-4.9f, 3.3f, 0.0f);
        var go_Brick_2_1_rb = go_Brick_2_1.AddComponent<Rigidbody2D>();
        go_Brick_2_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_2_1_bc = go_Brick_2_1.AddComponent<BoxCollider2D>();
        go_Brick_2_1_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_2_1_sr = go_Brick_2_1.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_2_1_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_2_1_sr.sharedMaterial = unlitMat;
        go_Brick_2_1.AddComponent<AudioSource>();
        go_Brick_2_1.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_2_1.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_2_1);

        // --- Brick_2_2 ---
        var go_Brick_2_2 = new GameObject("Brick_2_2");
        go_Brick_2_2.tag = "Brick";
        go_Brick_2_2.transform.position = new Vector3(-3.5000000000000004f, 3.3f, 0.0f);
        var go_Brick_2_2_rb = go_Brick_2_2.AddComponent<Rigidbody2D>();
        go_Brick_2_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_2_2_bc = go_Brick_2_2.AddComponent<BoxCollider2D>();
        go_Brick_2_2_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_2_2_sr = go_Brick_2_2.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_2_2_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_2_2_sr.sharedMaterial = unlitMat;
        go_Brick_2_2.AddComponent<AudioSource>();
        go_Brick_2_2.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_2_2.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_2_2);

        // --- Brick_2_3 ---
        var go_Brick_2_3 = new GameObject("Brick_2_3");
        go_Brick_2_3.tag = "Brick";
        go_Brick_2_3.transform.position = new Vector3(-2.1000000000000005f, 3.3f, 0.0f);
        var go_Brick_2_3_rb = go_Brick_2_3.AddComponent<Rigidbody2D>();
        go_Brick_2_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_2_3_bc = go_Brick_2_3.AddComponent<BoxCollider2D>();
        go_Brick_2_3_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_2_3_sr = go_Brick_2_3.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_2_3_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_2_3_sr.sharedMaterial = unlitMat;
        go_Brick_2_3.AddComponent<AudioSource>();
        go_Brick_2_3.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_2_3.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_2_3);

        // --- Brick_2_4 ---
        var go_Brick_2_4 = new GameObject("Brick_2_4");
        go_Brick_2_4.tag = "Brick";
        go_Brick_2_4.transform.position = new Vector3(-0.7000000000000002f, 3.3f, 0.0f);
        var go_Brick_2_4_rb = go_Brick_2_4.AddComponent<Rigidbody2D>();
        go_Brick_2_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_2_4_bc = go_Brick_2_4.AddComponent<BoxCollider2D>();
        go_Brick_2_4_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_2_4_sr = go_Brick_2_4.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_2_4_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_2_4_sr.sharedMaterial = unlitMat;
        go_Brick_2_4.AddComponent<AudioSource>();
        go_Brick_2_4.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_2_4.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_2_4);

        // --- Brick_2_5 ---
        var go_Brick_2_5 = new GameObject("Brick_2_5");
        go_Brick_2_5.tag = "Brick";
        go_Brick_2_5.transform.position = new Vector3(0.7000000000000002f, 3.3f, 0.0f);
        var go_Brick_2_5_rb = go_Brick_2_5.AddComponent<Rigidbody2D>();
        go_Brick_2_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_2_5_bc = go_Brick_2_5.AddComponent<BoxCollider2D>();
        go_Brick_2_5_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_2_5_sr = go_Brick_2_5.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_2_5_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_2_5_sr.sharedMaterial = unlitMat;
        go_Brick_2_5.AddComponent<AudioSource>();
        go_Brick_2_5.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_2_5.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_2_5);

        // --- Brick_2_6 ---
        var go_Brick_2_6 = new GameObject("Brick_2_6");
        go_Brick_2_6.tag = "Brick";
        go_Brick_2_6.transform.position = new Vector3(2.0999999999999996f, 3.3f, 0.0f);
        var go_Brick_2_6_rb = go_Brick_2_6.AddComponent<Rigidbody2D>();
        go_Brick_2_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_2_6_bc = go_Brick_2_6.AddComponent<BoxCollider2D>();
        go_Brick_2_6_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_2_6_sr = go_Brick_2_6.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_2_6_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_2_6_sr.sharedMaterial = unlitMat;
        go_Brick_2_6.AddComponent<AudioSource>();
        go_Brick_2_6.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_2_6.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_2_6);

        // --- Brick_2_7 ---
        var go_Brick_2_7 = new GameObject("Brick_2_7");
        go_Brick_2_7.tag = "Brick";
        go_Brick_2_7.transform.position = new Vector3(3.5f, 3.3f, 0.0f);
        var go_Brick_2_7_rb = go_Brick_2_7.AddComponent<Rigidbody2D>();
        go_Brick_2_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_2_7_bc = go_Brick_2_7.AddComponent<BoxCollider2D>();
        go_Brick_2_7_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_2_7_sr = go_Brick_2_7.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_2_7_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_2_7_sr.sharedMaterial = unlitMat;
        go_Brick_2_7.AddComponent<AudioSource>();
        go_Brick_2_7.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_2_7.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_2_7);

        // --- Brick_2_8 ---
        var go_Brick_2_8 = new GameObject("Brick_2_8");
        go_Brick_2_8.tag = "Brick";
        go_Brick_2_8.transform.position = new Vector3(4.9f, 3.3f, 0.0f);
        var go_Brick_2_8_rb = go_Brick_2_8.AddComponent<Rigidbody2D>();
        go_Brick_2_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_2_8_bc = go_Brick_2_8.AddComponent<BoxCollider2D>();
        go_Brick_2_8_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_2_8_sr = go_Brick_2_8.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_2_8_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_2_8_sr.sharedMaterial = unlitMat;
        go_Brick_2_8.AddComponent<AudioSource>();
        go_Brick_2_8.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_2_8.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_2_8);

        // --- Brick_2_9 ---
        var go_Brick_2_9 = new GameObject("Brick_2_9");
        go_Brick_2_9.tag = "Brick";
        go_Brick_2_9.transform.position = new Vector3(6.300000000000001f, 3.3f, 0.0f);
        var go_Brick_2_9_rb = go_Brick_2_9.AddComponent<Rigidbody2D>();
        go_Brick_2_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_2_9_bc = go_Brick_2_9.AddComponent<BoxCollider2D>();
        go_Brick_2_9_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_2_9_sr = go_Brick_2_9.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_2_9_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_2_9_sr.sharedMaterial = unlitMat;
        go_Brick_2_9.AddComponent<AudioSource>();
        go_Brick_2_9.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_2_9.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_2_9);

        // --- Brick_3_0 ---
        var go_Brick_3_0 = new GameObject("Brick_3_0");
        go_Brick_3_0.tag = "Brick";
        go_Brick_3_0.transform.position = new Vector3(-6.300000000000001f, 2.7f, 0.0f);
        var go_Brick_3_0_rb = go_Brick_3_0.AddComponent<Rigidbody2D>();
        go_Brick_3_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_3_0_bc = go_Brick_3_0.AddComponent<BoxCollider2D>();
        go_Brick_3_0_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_3_0_sr = go_Brick_3_0.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_3_0_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_3_0_sr.sharedMaterial = unlitMat;
        go_Brick_3_0.AddComponent<AudioSource>();
        go_Brick_3_0.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_3_0.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_3_0);

        // --- Brick_3_1 ---
        var go_Brick_3_1 = new GameObject("Brick_3_1");
        go_Brick_3_1.tag = "Brick";
        go_Brick_3_1.transform.position = new Vector3(-4.9f, 2.7f, 0.0f);
        var go_Brick_3_1_rb = go_Brick_3_1.AddComponent<Rigidbody2D>();
        go_Brick_3_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_3_1_bc = go_Brick_3_1.AddComponent<BoxCollider2D>();
        go_Brick_3_1_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_3_1_sr = go_Brick_3_1.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_3_1_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_3_1_sr.sharedMaterial = unlitMat;
        go_Brick_3_1.AddComponent<AudioSource>();
        go_Brick_3_1.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_3_1.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_3_1);

        // --- Brick_3_2 ---
        var go_Brick_3_2 = new GameObject("Brick_3_2");
        go_Brick_3_2.tag = "Brick";
        go_Brick_3_2.transform.position = new Vector3(-3.5000000000000004f, 2.7f, 0.0f);
        var go_Brick_3_2_rb = go_Brick_3_2.AddComponent<Rigidbody2D>();
        go_Brick_3_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_3_2_bc = go_Brick_3_2.AddComponent<BoxCollider2D>();
        go_Brick_3_2_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_3_2_sr = go_Brick_3_2.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_3_2_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_3_2_sr.sharedMaterial = unlitMat;
        go_Brick_3_2.AddComponent<AudioSource>();
        go_Brick_3_2.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_3_2.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_3_2);

        // --- Brick_3_3 ---
        var go_Brick_3_3 = new GameObject("Brick_3_3");
        go_Brick_3_3.tag = "Brick";
        go_Brick_3_3.transform.position = new Vector3(-2.1000000000000005f, 2.7f, 0.0f);
        var go_Brick_3_3_rb = go_Brick_3_3.AddComponent<Rigidbody2D>();
        go_Brick_3_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_3_3_bc = go_Brick_3_3.AddComponent<BoxCollider2D>();
        go_Brick_3_3_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_3_3_sr = go_Brick_3_3.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_3_3_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_3_3_sr.sharedMaterial = unlitMat;
        go_Brick_3_3.AddComponent<AudioSource>();
        go_Brick_3_3.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_3_3.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_3_3);

        // --- Brick_3_4 ---
        var go_Brick_3_4 = new GameObject("Brick_3_4");
        go_Brick_3_4.tag = "Brick";
        go_Brick_3_4.transform.position = new Vector3(-0.7000000000000002f, 2.7f, 0.0f);
        var go_Brick_3_4_rb = go_Brick_3_4.AddComponent<Rigidbody2D>();
        go_Brick_3_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_3_4_bc = go_Brick_3_4.AddComponent<BoxCollider2D>();
        go_Brick_3_4_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_3_4_sr = go_Brick_3_4.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_3_4_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_3_4_sr.sharedMaterial = unlitMat;
        go_Brick_3_4.AddComponent<AudioSource>();
        go_Brick_3_4.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_3_4.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_3_4);

        // --- Brick_3_5 ---
        var go_Brick_3_5 = new GameObject("Brick_3_5");
        go_Brick_3_5.tag = "Brick";
        go_Brick_3_5.transform.position = new Vector3(0.7000000000000002f, 2.7f, 0.0f);
        var go_Brick_3_5_rb = go_Brick_3_5.AddComponent<Rigidbody2D>();
        go_Brick_3_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_3_5_bc = go_Brick_3_5.AddComponent<BoxCollider2D>();
        go_Brick_3_5_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_3_5_sr = go_Brick_3_5.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_3_5_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_3_5_sr.sharedMaterial = unlitMat;
        go_Brick_3_5.AddComponent<AudioSource>();
        go_Brick_3_5.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_3_5.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_3_5);

        // --- Brick_3_6 ---
        var go_Brick_3_6 = new GameObject("Brick_3_6");
        go_Brick_3_6.tag = "Brick";
        go_Brick_3_6.transform.position = new Vector3(2.0999999999999996f, 2.7f, 0.0f);
        var go_Brick_3_6_rb = go_Brick_3_6.AddComponent<Rigidbody2D>();
        go_Brick_3_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_3_6_bc = go_Brick_3_6.AddComponent<BoxCollider2D>();
        go_Brick_3_6_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_3_6_sr = go_Brick_3_6.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_3_6_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_3_6_sr.sharedMaterial = unlitMat;
        go_Brick_3_6.AddComponent<AudioSource>();
        go_Brick_3_6.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_3_6.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_3_6);

        // --- Brick_3_7 ---
        var go_Brick_3_7 = new GameObject("Brick_3_7");
        go_Brick_3_7.tag = "Brick";
        go_Brick_3_7.transform.position = new Vector3(3.5f, 2.7f, 0.0f);
        var go_Brick_3_7_rb = go_Brick_3_7.AddComponent<Rigidbody2D>();
        go_Brick_3_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_3_7_bc = go_Brick_3_7.AddComponent<BoxCollider2D>();
        go_Brick_3_7_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_3_7_sr = go_Brick_3_7.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_3_7_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_3_7_sr.sharedMaterial = unlitMat;
        go_Brick_3_7.AddComponent<AudioSource>();
        go_Brick_3_7.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_3_7.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_3_7);

        // --- Brick_3_8 ---
        var go_Brick_3_8 = new GameObject("Brick_3_8");
        go_Brick_3_8.tag = "Brick";
        go_Brick_3_8.transform.position = new Vector3(4.9f, 2.7f, 0.0f);
        var go_Brick_3_8_rb = go_Brick_3_8.AddComponent<Rigidbody2D>();
        go_Brick_3_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_3_8_bc = go_Brick_3_8.AddComponent<BoxCollider2D>();
        go_Brick_3_8_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_3_8_sr = go_Brick_3_8.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_3_8_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_3_8_sr.sharedMaterial = unlitMat;
        go_Brick_3_8.AddComponent<AudioSource>();
        go_Brick_3_8.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_3_8.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_3_8);

        // --- Brick_3_9 ---
        var go_Brick_3_9 = new GameObject("Brick_3_9");
        go_Brick_3_9.tag = "Brick";
        go_Brick_3_9.transform.position = new Vector3(6.300000000000001f, 2.7f, 0.0f);
        var go_Brick_3_9_rb = go_Brick_3_9.AddComponent<Rigidbody2D>();
        go_Brick_3_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_3_9_bc = go_Brick_3_9.AddComponent<BoxCollider2D>();
        go_Brick_3_9_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_3_9_sr = go_Brick_3_9.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_3_9_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_3_9_sr.sharedMaterial = unlitMat;
        go_Brick_3_9.AddComponent<AudioSource>();
        go_Brick_3_9.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_3_9.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 20;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_3_9);

        // --- Brick_4_0 ---
        var go_Brick_4_0 = new GameObject("Brick_4_0");
        go_Brick_4_0.tag = "Brick";
        go_Brick_4_0.transform.position = new Vector3(-6.300000000000001f, 2.1f, 0.0f);
        var go_Brick_4_0_rb = go_Brick_4_0.AddComponent<Rigidbody2D>();
        go_Brick_4_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_4_0_bc = go_Brick_4_0.AddComponent<BoxCollider2D>();
        go_Brick_4_0_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_4_0_sr = go_Brick_4_0.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_4_0_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_4_0_sr.sharedMaterial = unlitMat;
        go_Brick_4_0.AddComponent<AudioSource>();
        go_Brick_4_0.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_4_0.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_4_0);

        // --- Brick_4_1 ---
        var go_Brick_4_1 = new GameObject("Brick_4_1");
        go_Brick_4_1.tag = "Brick";
        go_Brick_4_1.transform.position = new Vector3(-4.9f, 2.1f, 0.0f);
        var go_Brick_4_1_rb = go_Brick_4_1.AddComponent<Rigidbody2D>();
        go_Brick_4_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_4_1_bc = go_Brick_4_1.AddComponent<BoxCollider2D>();
        go_Brick_4_1_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_4_1_sr = go_Brick_4_1.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_4_1_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_4_1_sr.sharedMaterial = unlitMat;
        go_Brick_4_1.AddComponent<AudioSource>();
        go_Brick_4_1.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_4_1.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_4_1);

        // --- Brick_4_2 ---
        var go_Brick_4_2 = new GameObject("Brick_4_2");
        go_Brick_4_2.tag = "Brick";
        go_Brick_4_2.transform.position = new Vector3(-3.5000000000000004f, 2.1f, 0.0f);
        var go_Brick_4_2_rb = go_Brick_4_2.AddComponent<Rigidbody2D>();
        go_Brick_4_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_4_2_bc = go_Brick_4_2.AddComponent<BoxCollider2D>();
        go_Brick_4_2_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_4_2_sr = go_Brick_4_2.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_4_2_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_4_2_sr.sharedMaterial = unlitMat;
        go_Brick_4_2.AddComponent<AudioSource>();
        go_Brick_4_2.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_4_2.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_4_2);

        // --- Brick_4_3 ---
        var go_Brick_4_3 = new GameObject("Brick_4_3");
        go_Brick_4_3.tag = "Brick";
        go_Brick_4_3.transform.position = new Vector3(-2.1000000000000005f, 2.1f, 0.0f);
        var go_Brick_4_3_rb = go_Brick_4_3.AddComponent<Rigidbody2D>();
        go_Brick_4_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_4_3_bc = go_Brick_4_3.AddComponent<BoxCollider2D>();
        go_Brick_4_3_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_4_3_sr = go_Brick_4_3.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_4_3_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_4_3_sr.sharedMaterial = unlitMat;
        go_Brick_4_3.AddComponent<AudioSource>();
        go_Brick_4_3.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_4_3.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_4_3);

        // --- Brick_4_4 ---
        var go_Brick_4_4 = new GameObject("Brick_4_4");
        go_Brick_4_4.tag = "Brick";
        go_Brick_4_4.transform.position = new Vector3(-0.7000000000000002f, 2.1f, 0.0f);
        var go_Brick_4_4_rb = go_Brick_4_4.AddComponent<Rigidbody2D>();
        go_Brick_4_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_4_4_bc = go_Brick_4_4.AddComponent<BoxCollider2D>();
        go_Brick_4_4_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_4_4_sr = go_Brick_4_4.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_4_4_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_4_4_sr.sharedMaterial = unlitMat;
        go_Brick_4_4.AddComponent<AudioSource>();
        go_Brick_4_4.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_4_4.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_4_4);

        // --- Brick_4_5 ---
        var go_Brick_4_5 = new GameObject("Brick_4_5");
        go_Brick_4_5.tag = "Brick";
        go_Brick_4_5.transform.position = new Vector3(0.7000000000000002f, 2.1f, 0.0f);
        var go_Brick_4_5_rb = go_Brick_4_5.AddComponent<Rigidbody2D>();
        go_Brick_4_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_4_5_bc = go_Brick_4_5.AddComponent<BoxCollider2D>();
        go_Brick_4_5_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_4_5_sr = go_Brick_4_5.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_4_5_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_4_5_sr.sharedMaterial = unlitMat;
        go_Brick_4_5.AddComponent<AudioSource>();
        go_Brick_4_5.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_4_5.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_4_5);

        // --- Brick_4_6 ---
        var go_Brick_4_6 = new GameObject("Brick_4_6");
        go_Brick_4_6.tag = "Brick";
        go_Brick_4_6.transform.position = new Vector3(2.0999999999999996f, 2.1f, 0.0f);
        var go_Brick_4_6_rb = go_Brick_4_6.AddComponent<Rigidbody2D>();
        go_Brick_4_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_4_6_bc = go_Brick_4_6.AddComponent<BoxCollider2D>();
        go_Brick_4_6_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_4_6_sr = go_Brick_4_6.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_4_6_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_4_6_sr.sharedMaterial = unlitMat;
        go_Brick_4_6.AddComponent<AudioSource>();
        go_Brick_4_6.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_4_6.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_4_6);

        // --- Brick_4_7 ---
        var go_Brick_4_7 = new GameObject("Brick_4_7");
        go_Brick_4_7.tag = "Brick";
        go_Brick_4_7.transform.position = new Vector3(3.5f, 2.1f, 0.0f);
        var go_Brick_4_7_rb = go_Brick_4_7.AddComponent<Rigidbody2D>();
        go_Brick_4_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_4_7_bc = go_Brick_4_7.AddComponent<BoxCollider2D>();
        go_Brick_4_7_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_4_7_sr = go_Brick_4_7.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_4_7_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_4_7_sr.sharedMaterial = unlitMat;
        go_Brick_4_7.AddComponent<AudioSource>();
        go_Brick_4_7.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_4_7.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_4_7);

        // --- Brick_4_8 ---
        var go_Brick_4_8 = new GameObject("Brick_4_8");
        go_Brick_4_8.tag = "Brick";
        go_Brick_4_8.transform.position = new Vector3(4.9f, 2.1f, 0.0f);
        var go_Brick_4_8_rb = go_Brick_4_8.AddComponent<Rigidbody2D>();
        go_Brick_4_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_4_8_bc = go_Brick_4_8.AddComponent<BoxCollider2D>();
        go_Brick_4_8_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_4_8_sr = go_Brick_4_8.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_4_8_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_4_8_sr.sharedMaterial = unlitMat;
        go_Brick_4_8.AddComponent<AudioSource>();
        go_Brick_4_8.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_4_8.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_4_8);

        // --- Brick_4_9 ---
        var go_Brick_4_9 = new GameObject("Brick_4_9");
        go_Brick_4_9.tag = "Brick";
        go_Brick_4_9.transform.position = new Vector3(6.300000000000001f, 2.1f, 0.0f);
        var go_Brick_4_9_rb = go_Brick_4_9.AddComponent<Rigidbody2D>();
        go_Brick_4_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_4_9_bc = go_Brick_4_9.AddComponent<BoxCollider2D>();
        go_Brick_4_9_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_4_9_sr = go_Brick_4_9.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_4_9_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_4_9_sr.sharedMaterial = unlitMat;
        go_Brick_4_9.AddComponent<AudioSource>();
        go_Brick_4_9.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_4_9.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_4_9);

        // --- Brick_5_0 ---
        var go_Brick_5_0 = new GameObject("Brick_5_0");
        go_Brick_5_0.tag = "Brick";
        go_Brick_5_0.transform.position = new Vector3(-6.300000000000001f, 1.5f, 0.0f);
        var go_Brick_5_0_rb = go_Brick_5_0.AddComponent<Rigidbody2D>();
        go_Brick_5_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_5_0_bc = go_Brick_5_0.AddComponent<BoxCollider2D>();
        go_Brick_5_0_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_5_0_sr = go_Brick_5_0.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_5_0_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_5_0_sr.sharedMaterial = unlitMat;
        go_Brick_5_0.AddComponent<AudioSource>();
        go_Brick_5_0.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_5_0.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_5_0);

        // --- Brick_5_1 ---
        var go_Brick_5_1 = new GameObject("Brick_5_1");
        go_Brick_5_1.tag = "Brick";
        go_Brick_5_1.transform.position = new Vector3(-4.9f, 1.5f, 0.0f);
        var go_Brick_5_1_rb = go_Brick_5_1.AddComponent<Rigidbody2D>();
        go_Brick_5_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_5_1_bc = go_Brick_5_1.AddComponent<BoxCollider2D>();
        go_Brick_5_1_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_5_1_sr = go_Brick_5_1.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_5_1_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_5_1_sr.sharedMaterial = unlitMat;
        go_Brick_5_1.AddComponent<AudioSource>();
        go_Brick_5_1.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_5_1.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_5_1);

        // --- Brick_5_2 ---
        var go_Brick_5_2 = new GameObject("Brick_5_2");
        go_Brick_5_2.tag = "Brick";
        go_Brick_5_2.transform.position = new Vector3(-3.5000000000000004f, 1.5f, 0.0f);
        var go_Brick_5_2_rb = go_Brick_5_2.AddComponent<Rigidbody2D>();
        go_Brick_5_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_5_2_bc = go_Brick_5_2.AddComponent<BoxCollider2D>();
        go_Brick_5_2_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_5_2_sr = go_Brick_5_2.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_5_2_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_5_2_sr.sharedMaterial = unlitMat;
        go_Brick_5_2.AddComponent<AudioSource>();
        go_Brick_5_2.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_5_2.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_5_2);

        // --- Brick_5_3 ---
        var go_Brick_5_3 = new GameObject("Brick_5_3");
        go_Brick_5_3.tag = "Brick";
        go_Brick_5_3.transform.position = new Vector3(-2.1000000000000005f, 1.5f, 0.0f);
        var go_Brick_5_3_rb = go_Brick_5_3.AddComponent<Rigidbody2D>();
        go_Brick_5_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_5_3_bc = go_Brick_5_3.AddComponent<BoxCollider2D>();
        go_Brick_5_3_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_5_3_sr = go_Brick_5_3.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_5_3_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_5_3_sr.sharedMaterial = unlitMat;
        go_Brick_5_3.AddComponent<AudioSource>();
        go_Brick_5_3.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_5_3.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_5_3);

        // --- Brick_5_4 ---
        var go_Brick_5_4 = new GameObject("Brick_5_4");
        go_Brick_5_4.tag = "Brick";
        go_Brick_5_4.transform.position = new Vector3(-0.7000000000000002f, 1.5f, 0.0f);
        var go_Brick_5_4_rb = go_Brick_5_4.AddComponent<Rigidbody2D>();
        go_Brick_5_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_5_4_bc = go_Brick_5_4.AddComponent<BoxCollider2D>();
        go_Brick_5_4_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_5_4_sr = go_Brick_5_4.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_5_4_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_5_4_sr.sharedMaterial = unlitMat;
        go_Brick_5_4.AddComponent<AudioSource>();
        go_Brick_5_4.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_5_4.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_5_4);

        // --- Brick_5_5 ---
        var go_Brick_5_5 = new GameObject("Brick_5_5");
        go_Brick_5_5.tag = "Brick";
        go_Brick_5_5.transform.position = new Vector3(0.7000000000000002f, 1.5f, 0.0f);
        var go_Brick_5_5_rb = go_Brick_5_5.AddComponent<Rigidbody2D>();
        go_Brick_5_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_5_5_bc = go_Brick_5_5.AddComponent<BoxCollider2D>();
        go_Brick_5_5_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_5_5_sr = go_Brick_5_5.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_5_5_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_5_5_sr.sharedMaterial = unlitMat;
        go_Brick_5_5.AddComponent<AudioSource>();
        go_Brick_5_5.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_5_5.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_5_5);

        // --- Brick_5_6 ---
        var go_Brick_5_6 = new GameObject("Brick_5_6");
        go_Brick_5_6.tag = "Brick";
        go_Brick_5_6.transform.position = new Vector3(2.0999999999999996f, 1.5f, 0.0f);
        var go_Brick_5_6_rb = go_Brick_5_6.AddComponent<Rigidbody2D>();
        go_Brick_5_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_5_6_bc = go_Brick_5_6.AddComponent<BoxCollider2D>();
        go_Brick_5_6_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_5_6_sr = go_Brick_5_6.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_5_6_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_5_6_sr.sharedMaterial = unlitMat;
        go_Brick_5_6.AddComponent<AudioSource>();
        go_Brick_5_6.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_5_6.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_5_6);

        // --- Brick_5_7 ---
        var go_Brick_5_7 = new GameObject("Brick_5_7");
        go_Brick_5_7.tag = "Brick";
        go_Brick_5_7.transform.position = new Vector3(3.5f, 1.5f, 0.0f);
        var go_Brick_5_7_rb = go_Brick_5_7.AddComponent<Rigidbody2D>();
        go_Brick_5_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_5_7_bc = go_Brick_5_7.AddComponent<BoxCollider2D>();
        go_Brick_5_7_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_5_7_sr = go_Brick_5_7.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_5_7_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_5_7_sr.sharedMaterial = unlitMat;
        go_Brick_5_7.AddComponent<AudioSource>();
        go_Brick_5_7.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_5_7.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_5_7);

        // --- Brick_5_8 ---
        var go_Brick_5_8 = new GameObject("Brick_5_8");
        go_Brick_5_8.tag = "Brick";
        go_Brick_5_8.transform.position = new Vector3(4.9f, 1.5f, 0.0f);
        var go_Brick_5_8_rb = go_Brick_5_8.AddComponent<Rigidbody2D>();
        go_Brick_5_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_5_8_bc = go_Brick_5_8.AddComponent<BoxCollider2D>();
        go_Brick_5_8_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_5_8_sr = go_Brick_5_8.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_5_8_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_5_8_sr.sharedMaterial = unlitMat;
        go_Brick_5_8.AddComponent<AudioSource>();
        go_Brick_5_8.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_5_8.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_5_8);

        // --- Brick_5_9 ---
        var go_Brick_5_9 = new GameObject("Brick_5_9");
        go_Brick_5_9.tag = "Brick";
        go_Brick_5_9.transform.position = new Vector3(6.300000000000001f, 1.5f, 0.0f);
        var go_Brick_5_9_rb = go_Brick_5_9.AddComponent<Rigidbody2D>();
        go_Brick_5_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_5_9_bc = go_Brick_5_9.AddComponent<BoxCollider2D>();
        go_Brick_5_9_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_5_9_sr = go_Brick_5_9.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_5_9_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_5_9_sr.sharedMaterial = unlitMat;
        go_Brick_5_9.AddComponent<AudioSource>();
        go_Brick_5_9.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_5_9.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_5_9);

        // --- Brick_6_0 ---
        var go_Brick_6_0 = new GameObject("Brick_6_0");
        go_Brick_6_0.tag = "Brick";
        go_Brick_6_0.transform.position = new Vector3(-6.300000000000001f, 0.9000000000000004f, 0.0f);
        var go_Brick_6_0_rb = go_Brick_6_0.AddComponent<Rigidbody2D>();
        go_Brick_6_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_6_0_bc = go_Brick_6_0.AddComponent<BoxCollider2D>();
        go_Brick_6_0_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_6_0_sr = go_Brick_6_0.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_6_0_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_6_0_sr.sharedMaterial = unlitMat;
        go_Brick_6_0.AddComponent<AudioSource>();
        go_Brick_6_0.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_6_0.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_6_0);

        // --- Brick_6_1 ---
        var go_Brick_6_1 = new GameObject("Brick_6_1");
        go_Brick_6_1.tag = "Brick";
        go_Brick_6_1.transform.position = new Vector3(-4.9f, 0.9000000000000004f, 0.0f);
        var go_Brick_6_1_rb = go_Brick_6_1.AddComponent<Rigidbody2D>();
        go_Brick_6_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_6_1_bc = go_Brick_6_1.AddComponent<BoxCollider2D>();
        go_Brick_6_1_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_6_1_sr = go_Brick_6_1.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_6_1_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_6_1_sr.sharedMaterial = unlitMat;
        go_Brick_6_1.AddComponent<AudioSource>();
        go_Brick_6_1.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_6_1.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_6_1);

        // --- Brick_6_2 ---
        var go_Brick_6_2 = new GameObject("Brick_6_2");
        go_Brick_6_2.tag = "Brick";
        go_Brick_6_2.transform.position = new Vector3(-3.5000000000000004f, 0.9000000000000004f, 0.0f);
        var go_Brick_6_2_rb = go_Brick_6_2.AddComponent<Rigidbody2D>();
        go_Brick_6_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_6_2_bc = go_Brick_6_2.AddComponent<BoxCollider2D>();
        go_Brick_6_2_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_6_2_sr = go_Brick_6_2.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_6_2_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_6_2_sr.sharedMaterial = unlitMat;
        go_Brick_6_2.AddComponent<AudioSource>();
        go_Brick_6_2.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_6_2.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_6_2);

        // --- Brick_6_3 ---
        var go_Brick_6_3 = new GameObject("Brick_6_3");
        go_Brick_6_3.tag = "Brick";
        go_Brick_6_3.transform.position = new Vector3(-2.1000000000000005f, 0.9000000000000004f, 0.0f);
        var go_Brick_6_3_rb = go_Brick_6_3.AddComponent<Rigidbody2D>();
        go_Brick_6_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_6_3_bc = go_Brick_6_3.AddComponent<BoxCollider2D>();
        go_Brick_6_3_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_6_3_sr = go_Brick_6_3.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_6_3_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_6_3_sr.sharedMaterial = unlitMat;
        go_Brick_6_3.AddComponent<AudioSource>();
        go_Brick_6_3.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_6_3.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_6_3);

        // --- Brick_6_4 ---
        var go_Brick_6_4 = new GameObject("Brick_6_4");
        go_Brick_6_4.tag = "Brick";
        go_Brick_6_4.transform.position = new Vector3(-0.7000000000000002f, 0.9000000000000004f, 0.0f);
        var go_Brick_6_4_rb = go_Brick_6_4.AddComponent<Rigidbody2D>();
        go_Brick_6_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_6_4_bc = go_Brick_6_4.AddComponent<BoxCollider2D>();
        go_Brick_6_4_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_6_4_sr = go_Brick_6_4.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_6_4_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_6_4_sr.sharedMaterial = unlitMat;
        go_Brick_6_4.AddComponent<AudioSource>();
        go_Brick_6_4.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_6_4.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_6_4);

        // --- Brick_6_5 ---
        var go_Brick_6_5 = new GameObject("Brick_6_5");
        go_Brick_6_5.tag = "Brick";
        go_Brick_6_5.transform.position = new Vector3(0.7000000000000002f, 0.9000000000000004f, 0.0f);
        var go_Brick_6_5_rb = go_Brick_6_5.AddComponent<Rigidbody2D>();
        go_Brick_6_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_6_5_bc = go_Brick_6_5.AddComponent<BoxCollider2D>();
        go_Brick_6_5_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_6_5_sr = go_Brick_6_5.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_6_5_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_6_5_sr.sharedMaterial = unlitMat;
        go_Brick_6_5.AddComponent<AudioSource>();
        go_Brick_6_5.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_6_5.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_6_5);

        // --- Brick_6_6 ---
        var go_Brick_6_6 = new GameObject("Brick_6_6");
        go_Brick_6_6.tag = "Brick";
        go_Brick_6_6.transform.position = new Vector3(2.0999999999999996f, 0.9000000000000004f, 0.0f);
        var go_Brick_6_6_rb = go_Brick_6_6.AddComponent<Rigidbody2D>();
        go_Brick_6_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_6_6_bc = go_Brick_6_6.AddComponent<BoxCollider2D>();
        go_Brick_6_6_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_6_6_sr = go_Brick_6_6.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_6_6_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_6_6_sr.sharedMaterial = unlitMat;
        go_Brick_6_6.AddComponent<AudioSource>();
        go_Brick_6_6.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_6_6.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_6_6);

        // --- Brick_6_7 ---
        var go_Brick_6_7 = new GameObject("Brick_6_7");
        go_Brick_6_7.tag = "Brick";
        go_Brick_6_7.transform.position = new Vector3(3.5f, 0.9000000000000004f, 0.0f);
        var go_Brick_6_7_rb = go_Brick_6_7.AddComponent<Rigidbody2D>();
        go_Brick_6_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_6_7_bc = go_Brick_6_7.AddComponent<BoxCollider2D>();
        go_Brick_6_7_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_6_7_sr = go_Brick_6_7.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_6_7_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_6_7_sr.sharedMaterial = unlitMat;
        go_Brick_6_7.AddComponent<AudioSource>();
        go_Brick_6_7.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_6_7.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_6_7);

        // --- Brick_6_8 ---
        var go_Brick_6_8 = new GameObject("Brick_6_8");
        go_Brick_6_8.tag = "Brick";
        go_Brick_6_8.transform.position = new Vector3(4.9f, 0.9000000000000004f, 0.0f);
        var go_Brick_6_8_rb = go_Brick_6_8.AddComponent<Rigidbody2D>();
        go_Brick_6_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_6_8_bc = go_Brick_6_8.AddComponent<BoxCollider2D>();
        go_Brick_6_8_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_6_8_sr = go_Brick_6_8.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_6_8_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_6_8_sr.sharedMaterial = unlitMat;
        go_Brick_6_8.AddComponent<AudioSource>();
        go_Brick_6_8.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_6_8.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_6_8);

        // --- Brick_6_9 ---
        var go_Brick_6_9 = new GameObject("Brick_6_9");
        go_Brick_6_9.tag = "Brick";
        go_Brick_6_9.transform.position = new Vector3(6.300000000000001f, 0.9000000000000004f, 0.0f);
        var go_Brick_6_9_rb = go_Brick_6_9.AddComponent<Rigidbody2D>();
        go_Brick_6_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_6_9_bc = go_Brick_6_9.AddComponent<BoxCollider2D>();
        go_Brick_6_9_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_6_9_sr = go_Brick_6_9.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_6_9_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_6_9_sr.sharedMaterial = unlitMat;
        go_Brick_6_9.AddComponent<AudioSource>();
        go_Brick_6_9.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_6_9.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_6_9);

        // --- Brick_7_0 ---
        var go_Brick_7_0 = new GameObject("Brick_7_0");
        go_Brick_7_0.tag = "Brick";
        go_Brick_7_0.transform.position = new Vector3(-6.300000000000001f, 0.2999999999999998f, 0.0f);
        var go_Brick_7_0_rb = go_Brick_7_0.AddComponent<Rigidbody2D>();
        go_Brick_7_0_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_7_0_bc = go_Brick_7_0.AddComponent<BoxCollider2D>();
        go_Brick_7_0_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_7_0_sr = go_Brick_7_0.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_7_0_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_7_0_sr.sharedMaterial = unlitMat;
        go_Brick_7_0.AddComponent<AudioSource>();
        go_Brick_7_0.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_7_0.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_7_0);

        // --- Brick_7_1 ---
        var go_Brick_7_1 = new GameObject("Brick_7_1");
        go_Brick_7_1.tag = "Brick";
        go_Brick_7_1.transform.position = new Vector3(-4.9f, 0.2999999999999998f, 0.0f);
        var go_Brick_7_1_rb = go_Brick_7_1.AddComponent<Rigidbody2D>();
        go_Brick_7_1_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_7_1_bc = go_Brick_7_1.AddComponent<BoxCollider2D>();
        go_Brick_7_1_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_7_1_sr = go_Brick_7_1.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_7_1_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_7_1_sr.sharedMaterial = unlitMat;
        go_Brick_7_1.AddComponent<AudioSource>();
        go_Brick_7_1.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_7_1.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_7_1);

        // --- Brick_7_2 ---
        var go_Brick_7_2 = new GameObject("Brick_7_2");
        go_Brick_7_2.tag = "Brick";
        go_Brick_7_2.transform.position = new Vector3(-3.5000000000000004f, 0.2999999999999998f, 0.0f);
        var go_Brick_7_2_rb = go_Brick_7_2.AddComponent<Rigidbody2D>();
        go_Brick_7_2_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_7_2_bc = go_Brick_7_2.AddComponent<BoxCollider2D>();
        go_Brick_7_2_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_7_2_sr = go_Brick_7_2.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_7_2_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_7_2_sr.sharedMaterial = unlitMat;
        go_Brick_7_2.AddComponent<AudioSource>();
        go_Brick_7_2.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_7_2.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_7_2);

        // --- Brick_7_3 ---
        var go_Brick_7_3 = new GameObject("Brick_7_3");
        go_Brick_7_3.tag = "Brick";
        go_Brick_7_3.transform.position = new Vector3(-2.1000000000000005f, 0.2999999999999998f, 0.0f);
        var go_Brick_7_3_rb = go_Brick_7_3.AddComponent<Rigidbody2D>();
        go_Brick_7_3_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_7_3_bc = go_Brick_7_3.AddComponent<BoxCollider2D>();
        go_Brick_7_3_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_7_3_sr = go_Brick_7_3.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_7_3_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_7_3_sr.sharedMaterial = unlitMat;
        go_Brick_7_3.AddComponent<AudioSource>();
        go_Brick_7_3.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_7_3.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_7_3);

        // --- Brick_7_4 ---
        var go_Brick_7_4 = new GameObject("Brick_7_4");
        go_Brick_7_4.tag = "Brick";
        go_Brick_7_4.transform.position = new Vector3(-0.7000000000000002f, 0.2999999999999998f, 0.0f);
        var go_Brick_7_4_rb = go_Brick_7_4.AddComponent<Rigidbody2D>();
        go_Brick_7_4_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_7_4_bc = go_Brick_7_4.AddComponent<BoxCollider2D>();
        go_Brick_7_4_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_7_4_sr = go_Brick_7_4.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_7_4_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_7_4_sr.sharedMaterial = unlitMat;
        go_Brick_7_4.AddComponent<AudioSource>();
        go_Brick_7_4.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_7_4.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_7_4);

        // --- Brick_7_5 ---
        var go_Brick_7_5 = new GameObject("Brick_7_5");
        go_Brick_7_5.tag = "Brick";
        go_Brick_7_5.transform.position = new Vector3(0.7000000000000002f, 0.2999999999999998f, 0.0f);
        var go_Brick_7_5_rb = go_Brick_7_5.AddComponent<Rigidbody2D>();
        go_Brick_7_5_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_7_5_bc = go_Brick_7_5.AddComponent<BoxCollider2D>();
        go_Brick_7_5_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_7_5_sr = go_Brick_7_5.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_7_5_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_7_5_sr.sharedMaterial = unlitMat;
        go_Brick_7_5.AddComponent<AudioSource>();
        go_Brick_7_5.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_7_5.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_7_5);

        // --- Brick_7_6 ---
        var go_Brick_7_6 = new GameObject("Brick_7_6");
        go_Brick_7_6.tag = "Brick";
        go_Brick_7_6.transform.position = new Vector3(2.0999999999999996f, 0.2999999999999998f, 0.0f);
        var go_Brick_7_6_rb = go_Brick_7_6.AddComponent<Rigidbody2D>();
        go_Brick_7_6_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_7_6_bc = go_Brick_7_6.AddComponent<BoxCollider2D>();
        go_Brick_7_6_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_7_6_sr = go_Brick_7_6.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_7_6_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_7_6_sr.sharedMaterial = unlitMat;
        go_Brick_7_6.AddComponent<AudioSource>();
        go_Brick_7_6.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_7_6.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_7_6);

        // --- Brick_7_7 ---
        var go_Brick_7_7 = new GameObject("Brick_7_7");
        go_Brick_7_7.tag = "Brick";
        go_Brick_7_7.transform.position = new Vector3(3.5f, 0.2999999999999998f, 0.0f);
        var go_Brick_7_7_rb = go_Brick_7_7.AddComponent<Rigidbody2D>();
        go_Brick_7_7_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_7_7_bc = go_Brick_7_7.AddComponent<BoxCollider2D>();
        go_Brick_7_7_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_7_7_sr = go_Brick_7_7.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_7_7_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_7_7_sr.sharedMaterial = unlitMat;
        go_Brick_7_7.AddComponent<AudioSource>();
        go_Brick_7_7.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_7_7.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_7_7);

        // --- Brick_7_8 ---
        var go_Brick_7_8 = new GameObject("Brick_7_8");
        go_Brick_7_8.tag = "Brick";
        go_Brick_7_8.transform.position = new Vector3(4.9f, 0.2999999999999998f, 0.0f);
        var go_Brick_7_8_rb = go_Brick_7_8.AddComponent<Rigidbody2D>();
        go_Brick_7_8_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_7_8_bc = go_Brick_7_8.AddComponent<BoxCollider2D>();
        go_Brick_7_8_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_7_8_sr = go_Brick_7_8.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_7_8_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_7_8_sr.sharedMaterial = unlitMat;
        go_Brick_7_8.AddComponent<AudioSource>();
        go_Brick_7_8.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_7_8.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_7_8);

        // --- Brick_7_9 ---
        var go_Brick_7_9 = new GameObject("Brick_7_9");
        go_Brick_7_9.tag = "Brick";
        go_Brick_7_9.transform.position = new Vector3(6.300000000000001f, 0.2999999999999998f, 0.0f);
        var go_Brick_7_9_rb = go_Brick_7_9.AddComponent<Rigidbody2D>();
        go_Brick_7_9_rb.bodyType = RigidbodyType2D.Static;
        var go_Brick_7_9_bc = go_Brick_7_9.AddComponent<BoxCollider2D>();
        go_Brick_7_9_bc.size = new Vector2(1.3f, 0.5f);
        var go_Brick_7_9_sr = go_Brick_7_9.AddComponent<SpriteRenderer>();
        if (sprite_brick != null) go_Brick_7_9_sr.sprite = sprite_brick;
        if (unlitMat != null) go_Brick_7_9_sr.sharedMaterial = unlitMat;
        go_Brick_7_9.AddComponent<AudioSource>();
        go_Brick_7_9.AddComponent<Breakout.Brick>();
        {
            var so = new SerializedObject(go_Brick_7_9.GetComponent<Breakout.Brick>());
            var prop_health = so.FindProperty("health");
            if (prop_health != null) prop_health.floatValue = 1;
            var prop_points = so.FindProperty("points");
            if (prop_points != null) prop_points.floatValue = 10;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Brick_7_9);

        // --- GameManager ---
        var go_GameManager = new GameObject("GameManager");
        go_GameManager.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        go_GameManager.AddComponent<Breakout.GameManager>();
        {
            var so = new SerializedObject(go_GameManager.GetComponent<Breakout.GameManager>());
            var prop_lives = so.FindProperty("lives");
            if (prop_lives != null) prop_lives.floatValue = 3;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_GameManager);

        // === WIRE CROSS-REFERENCES ===
        {
            var so = new SerializedObject(go_Paddle.GetComponent<Breakout.PaddleController>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Paddle; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Ball.GetComponent<Breakout.BallController>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Ball; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_0_0.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_0_0; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_0_1.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_0_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_0_2.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_0_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_0_3.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_0_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_0_4.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_0_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_0_5.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_0_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_0_6.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_0_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_0_7.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_0_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_0_8.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_0_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_0_9.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_0_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_1_0.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_1_0; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_1_1.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_1_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_1_2.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_1_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_1_3.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_1_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_1_4.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_1_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_1_5.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_1_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_1_6.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_1_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_1_7.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_1_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_1_8.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_1_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_1_9.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_1_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_2_0.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_2_0; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_2_1.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_2_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_2_2.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_2_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_2_3.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_2_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_2_4.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_2_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_2_5.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_2_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_2_6.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_2_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_2_7.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_2_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_2_8.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_2_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_2_9.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_2_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_3_0.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_3_0; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_3_1.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_3_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_3_2.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_3_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_3_3.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_3_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_3_4.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_3_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_3_5.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_3_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_3_6.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_3_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_3_7.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_3_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_3_8.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_3_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_3_9.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_3_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_4_0.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_4_0; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_4_1.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_4_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_4_2.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_4_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_4_3.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_4_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_4_4.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_4_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_4_5.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_4_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_4_6.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_4_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_4_7.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_4_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_4_8.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_4_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_4_9.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_4_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_5_0.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_5_0; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_5_1.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_5_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_5_2.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_5_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_5_3.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_5_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_5_4.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_5_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_5_5.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_5_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_5_6.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_5_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_5_7.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_5_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_5_8.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_5_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_5_9.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_5_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_6_0.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_6_0; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_6_1.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_6_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_6_2.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_6_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_6_3.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_6_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_6_4.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_6_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_6_5.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_6_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_6_6.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_6_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_6_7.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_6_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_6_8.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_6_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_6_9.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_6_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_7_0.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_7_0; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_7_1.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_7_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_7_2.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_7_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_7_3.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_7_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_7_4.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_7_4; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_7_5.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_7_5; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_7_6.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_7_6; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_7_7.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_7_7; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_7_8.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_7_8; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Brick_7_9.GetComponent<Breakout.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Brick_7_9; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_GameManager.GetComponent<Breakout.GameManager>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_GameManager; so.ApplyModifiedProperties(); }
        }

        // --- AutoStart (scaffolder fixture, un-pauses on Play) ---
        if (GameObject.Find("AutoStart") == null)
        {
            var go_AutoStart = new GameObject("AutoStart");
            go_AutoStart.AddComponent<AutoStart>();
            EditorUtility.SetDirty(go_AutoStart);
        }

        // === SAVE ===
        UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(
            UnityEditor.SceneManagement.EditorSceneManager.GetActiveScene());
        UnityEditor.SceneManagement.EditorSceneManager.SaveOpenScenes();

        result = "Scene setup complete: 87 GameObjects";
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
