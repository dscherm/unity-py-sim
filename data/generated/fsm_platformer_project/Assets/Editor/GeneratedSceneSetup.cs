using UnityEngine;
using UnityEditor;
using System.Linq;
using FSMPlatformer;

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
        _EnsureTag(tagsProp, "Enemy");
        _EnsureTag(tagsProp, "Ground");
        _EnsureTag(tagsProp, "Player");
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
            cam.backgroundColor = new Color(0.157f, 0.157f, 0.235f, 1f);
            cam.clearFlags = CameraClearFlags.SolidColor;
            go_MainCamera.transform.position = new Vector3(0f, 0f, -10f);
            if (go_MainCamera.GetComponent<AspectLock>() == null)
                go_MainCamera.AddComponent<AspectLock>();
            EditorUtility.SetDirty(go_MainCamera);
        }

        // --- Ground ---
        var go_Ground = new GameObject("Ground");
        go_Ground.tag = "Ground";
        go_Ground.transform.position = new Vector3(0.0f, -3.5f, 0.0f);
        var go_Ground_rb = go_Ground.AddComponent<Rigidbody2D>();
        go_Ground_rb.bodyType = RigidbodyType2D.Static;
        var go_Ground_bc = go_Ground.AddComponent<BoxCollider2D>();
        go_Ground_bc.size = new Vector2(20.0f, 1.0f);
        var go_Ground_sr = go_Ground.AddComponent<SpriteRenderer>();
        go_Ground_sr.sprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/WhiteSquare.png");
        if (unlitMat != null) go_Ground_sr.sharedMaterial = unlitMat;
        go_Ground_sr.sortingOrder = -1;
        go_Ground_sr.color = new Color(0.314f, 0.627f, 0.314f, 1f);
        EditorUtility.SetDirty(go_Ground);

        // --- Player ---
        var go_Player = new GameObject("Player");
        go_Player.tag = "Player";
        go_Player.transform.position = new Vector3(-2.0f, -2.5f, 0.0f);
        var go_Player_rb = go_Player.AddComponent<Rigidbody2D>();
        var go_Player_bc = go_Player.AddComponent<BoxCollider2D>();
        go_Player_bc.size = new Vector2(0.8f, 1.0f);
        var go_Player_sr = go_Player.AddComponent<SpriteRenderer>();
        go_Player_sr.sprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/WhiteSquare.png");
        if (unlitMat != null) go_Player_sr.sharedMaterial = unlitMat;
        go_Player_sr.color = new Color(0.392f, 0.706f, 1.000f, 1f);
        go_Player.AddComponent<FSMPlatformer.PlayerInputHandler>();
        {
            var so = new SerializedObject(go_Player.GetComponent<FSMPlatformer.PlayerInputHandler>());
            var prop_moveSpeed = so.FindProperty("moveSpeed");
            if (prop_moveSpeed != null) prop_moveSpeed.floatValue = 3.0f;
            var prop_jumpForce = so.FindProperty("jumpForce");
            if (prop_jumpForce != null) prop_jumpForce.floatValue = 5.0f;
            var prop_groundY = so.FindProperty("groundY");
            if (prop_groundY != null) prop_groundY.floatValue = -3.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Player);

        // --- Enemy ---
        var go_Enemy = new GameObject("Enemy");
        go_Enemy.tag = "Enemy";
        go_Enemy.transform.position = new Vector3(3.0f, -2.5f, 0.0f);
        var go_Enemy_rb = go_Enemy.AddComponent<Rigidbody2D>();
        var go_Enemy_bc = go_Enemy.AddComponent<BoxCollider2D>();
        go_Enemy_bc.size = new Vector2(0.8f, 1.0f);
        var go_Enemy_sr = go_Enemy.AddComponent<SpriteRenderer>();
        go_Enemy_sr.sprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/WhiteSquare.png");
        if (unlitMat != null) go_Enemy_sr.sharedMaterial = unlitMat;
        go_Enemy_sr.color = new Color(1.000f, 0.392f, 0.392f, 1f);
        go_Enemy.AddComponent<FSMPlatformer.EnemyBehaviour>();
        {
            var so = new SerializedObject(go_Enemy.GetComponent<FSMPlatformer.EnemyBehaviour>());
            var prop_idleTime = so.FindProperty("idleTime");
            if (prop_idleTime != null) prop_idleTime.floatValue = 2.0f;
            var prop_walkTime = so.FindProperty("walkTime");
            if (prop_walkTime != null) prop_walkTime.floatValue = 3.0f;
            var prop_walkSpeed = so.FindProperty("walkSpeed");
            if (prop_walkSpeed != null) prop_walkSpeed.floatValue = 1.5f;
            var prop_patrolMinX = so.FindProperty("patrolMinX");
            if (prop_patrolMinX != null) prop_patrolMinX.floatValue = 1.0f;
            var prop_patrolMaxX = so.FindProperty("patrolMaxX");
            if (prop_patrolMaxX != null) prop_patrolMaxX.floatValue = 6.0f;
            so.ApplyModifiedProperties();
        }
        EditorUtility.SetDirty(go_Enemy);

        // --- LeftWall ---
        var go_LeftWall = new GameObject("LeftWall");
        go_LeftWall.transform.position = new Vector3(-9.5f, 0.0f, 0.0f);
        var go_LeftWall_rb = go_LeftWall.AddComponent<Rigidbody2D>();
        go_LeftWall_rb.bodyType = RigidbodyType2D.Static;
        var go_LeftWall_bc = go_LeftWall.AddComponent<BoxCollider2D>();
        go_LeftWall_bc.size = new Vector2(1.0f, 14.0f);
        EditorUtility.SetDirty(go_LeftWall);

        // --- RightWall ---
        var go_RightWall = new GameObject("RightWall");
        go_RightWall.transform.position = new Vector3(9.5f, 0.0f, 0.0f);
        var go_RightWall_rb = go_RightWall.AddComponent<Rigidbody2D>();
        go_RightWall_rb.bodyType = RigidbodyType2D.Static;
        var go_RightWall_bc = go_RightWall.AddComponent<BoxCollider2D>();
        go_RightWall_bc.size = new Vector2(1.0f, 14.0f);
        EditorUtility.SetDirty(go_RightWall);

        // --- StateDisplay ---
        var go_StateDisplay = new GameObject("StateDisplay");
        EditorUtility.SetDirty(go_StateDisplay);

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

        result = "Scene setup complete: 7 GameObjects";
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
