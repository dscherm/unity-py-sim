using UnityEngine;
using UnityEditor;
using System.Linq;
using Pong;

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
            cam.orthographicSize = 6.0f;
            cam.backgroundColor = new Color(0.078f, 0.078f, 0.118f, 1f);
            cam.clearFlags = CameraClearFlags.SolidColor;
            go_MainCamera.transform.position = new Vector3(0f, 0f, -10f);
            if (go_MainCamera.GetComponent<AspectLock>() == null)
                go_MainCamera.AddComponent<AspectLock>();
            EditorUtility.SetDirty(go_MainCamera);
        }

        // --- LeftPaddle ---
        var go_LeftPaddle = new GameObject("LeftPaddle");
        go_LeftPaddle.tag = "Paddle";
        go_LeftPaddle.transform.position = new Vector3(-7.0f, 0.0f, 0.0f);
        var go_LeftPaddle_rb = go_LeftPaddle.AddComponent<Rigidbody2D>();
        go_LeftPaddle_rb.bodyType = RigidbodyType2D.Kinematic;
        var go_LeftPaddle_bc = go_LeftPaddle.AddComponent<BoxCollider2D>();
        go_LeftPaddle_bc.size = new Vector2(0.5f, 2.0f);
        var go_LeftPaddle_sr = go_LeftPaddle.AddComponent<SpriteRenderer>();
        if (unlitMat != null) go_LeftPaddle_sr.sharedMaterial = unlitMat;
        go_LeftPaddle_sr.color = new Color(0.392f, 0.706f, 1.000f, 1f);
        go_LeftPaddle.AddComponent<Pong.PaddleController>();
        {
            var so = new SerializedObject(go_LeftPaddle.GetComponent<Pong.PaddleController>());
            var prop_speed = so.FindProperty("speed");
            if (prop_speed != null) prop_speed.floatValue = 10.0f;
            var prop_boundY = so.FindProperty("boundY");
            if (prop_boundY != null) prop_boundY.floatValue = 4.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_LeftPaddle);

        // --- RightPaddle ---
        var go_RightPaddle = new GameObject("RightPaddle");
        go_RightPaddle.tag = "Paddle";
        go_RightPaddle.transform.position = new Vector3(7.0f, 0.0f, 0.0f);
        var go_RightPaddle_rb = go_RightPaddle.AddComponent<Rigidbody2D>();
        go_RightPaddle_rb.bodyType = RigidbodyType2D.Kinematic;
        var go_RightPaddle_bc = go_RightPaddle.AddComponent<BoxCollider2D>();
        go_RightPaddle_bc.size = new Vector2(0.5f, 2.0f);
        var go_RightPaddle_sr = go_RightPaddle.AddComponent<SpriteRenderer>();
        if (unlitMat != null) go_RightPaddle_sr.sharedMaterial = unlitMat;
        go_RightPaddle_sr.color = new Color(1.000f, 0.510f, 0.392f, 1f);
        go_RightPaddle.AddComponent<Pong.PaddleController>();
        {
            var so = new SerializedObject(go_RightPaddle.GetComponent<Pong.PaddleController>());
            var prop_speed = so.FindProperty("speed");
            if (prop_speed != null) prop_speed.floatValue = 10.0f;
            var prop_boundY = so.FindProperty("boundY");
            if (prop_boundY != null) prop_boundY.floatValue = 4.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_RightPaddle);

        // --- Ball ---
        var go_Ball = new GameObject("Ball");
        go_Ball.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        var go_Ball_rb = go_Ball.AddComponent<Rigidbody2D>();
        go_Ball_rb.mass = 0.1f;
        go_Ball_rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
        {
            var _mat = AssetDatabase.LoadAssetAtPath<PhysicsMaterial2D>("Assets/Art/BouncyBall.physicsMaterial2D");
            if (_mat != null) go_Ball_rb.sharedMaterial = _mat;
        }
        var go_Ball_cc = go_Ball.AddComponent<CircleCollider2D>();
        go_Ball_cc.radius = 0.25f;
        {
            var _mat = AssetDatabase.LoadAssetAtPath<PhysicsMaterial2D>("Assets/Art/BouncyBall.physicsMaterial2D");
            if (_mat != null) go_Ball_cc.sharedMaterial = _mat;
        }
        var go_Ball_sr = go_Ball.AddComponent<SpriteRenderer>();
        if (unlitMat != null) go_Ball_sr.sharedMaterial = unlitMat;
        go_Ball_sr.color = new Color(1.000f, 1.000f, 0.000f, 1f);
        go_Ball.AddComponent<Pong.BallController>();
        {
            var so = new SerializedObject(go_Ball.GetComponent<Pong.BallController>());
            var prop_initialSpeed = so.FindProperty("initialSpeed");
            if (prop_initialSpeed != null) prop_initialSpeed.floatValue = 6.0f;
            var prop_speedIncrease = so.FindProperty("speedIncrease");
            if (prop_speedIncrease != null) prop_speedIncrease.floatValue = 0.3f;
            var prop_currentSpeed = so.FindProperty("currentSpeed");
            if (prop_currentSpeed != null) prop_currentSpeed.floatValue = 6.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Ball);

        // --- TopWall ---
        var go_TopWall = new GameObject("TopWall");
        go_TopWall.tag = "Wall";
        go_TopWall.transform.position = new Vector3(0.0f, 5.5f, 0.0f);
        var go_TopWall_rb = go_TopWall.AddComponent<Rigidbody2D>();
        go_TopWall_rb.bodyType = RigidbodyType2D.Static;
        var go_TopWall_bc = go_TopWall.AddComponent<BoxCollider2D>();
        go_TopWall_bc.size = new Vector2(20.0f, 1.0f);
        EditorUtility.SetDirty(go_TopWall);

        // --- BottomWall ---
        var go_BottomWall = new GameObject("BottomWall");
        go_BottomWall.tag = "Wall";
        go_BottomWall.transform.position = new Vector3(0.0f, -5.5f, 0.0f);
        var go_BottomWall_rb = go_BottomWall.AddComponent<Rigidbody2D>();
        go_BottomWall_rb.bodyType = RigidbodyType2D.Static;
        var go_BottomWall_bc = go_BottomWall.AddComponent<BoxCollider2D>();
        go_BottomWall_bc.size = new Vector2(20.0f, 1.0f);
        EditorUtility.SetDirty(go_BottomWall);

        // --- CenterLine ---
        var go_CenterLine = new GameObject("CenterLine");
        var go_CenterLine_sr = go_CenterLine.AddComponent<SpriteRenderer>();
        if (unlitMat != null) go_CenterLine_sr.sharedMaterial = unlitMat;
        go_CenterLine_sr.sortingOrder = -1;
        go_CenterLine_sr.color = new Color(0.235f, 0.235f, 0.314f, 1f);
        EditorUtility.SetDirty(go_CenterLine);

        // --- Goal_left ---
        var go_Goal_left = new GameObject("Goal_left");
        EditorUtility.SetDirty(go_Goal_left);

        // --- Goal_right ---
        var go_Goal_right = new GameObject("Goal_right");
        EditorUtility.SetDirty(go_Goal_right);

        // --- ScoreManager ---
        var go_ScoreManager = new GameObject("ScoreManager");
        go_ScoreManager.AddComponent<Pong.ScoreManager>();
        EditorUtility.SetDirty(go_ScoreManager);

        // --- ScoreDisplay ---
        var go_ScoreDisplay = new GameObject("ScoreDisplay");
        EditorUtility.SetDirty(go_ScoreDisplay);

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
}
