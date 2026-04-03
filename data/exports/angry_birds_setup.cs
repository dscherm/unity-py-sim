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
        _EnsureTag(tagsProp, "Bird");
        _EnsureTag(tagsProp, "Brick");
        _EnsureTag(tagsProp, "Ground");
        _EnsureTag(tagsProp, "Pig");
        tagManager.ApplyModifiedProperties();

        // === LOAD MATERIALS ===
        var unlitMat = AssetDatabase.LoadAssetAtPath<Material>(
            "Packages/com.unity.render-pipelines.universal/Runtime/Materials/Sprite-Unlit-Default.mat");

        // === LOAD SPRITE ASSETS ===
        var sprite_bird_red = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/angry_birds_ocs_sprites__update__by_jared33-d5mg197.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "angry_birds_ocs_sprites__update__by_jared33-d5mg197_0");
        var sprite_pig_normal = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/small_helmet_pig_sprites_by_chinzapep-d57z4bs.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "small_helmet_pig_sprites_by_chinzapep-d57z4bs_0");
        var sprite_brick_wood = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/Blocks/INGAME_BLOCKS_WOOD_1.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "INGAME_BLOCKS_WOOD_1_0");
        var sprite_slingshot = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/slingshot.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "slingshot_0");
        var sprite_ground_grass = AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/forest/forest-2.png")
            .OfType<Sprite>().FirstOrDefault(s => s.name == "forest-2_6");

        // === CREATE GAMEOBJECTS ===
        // --- MainCamera (use existing Main Camera) ---
        var go_MainCamera = Camera.main?.gameObject;
        if (go_MainCamera != null)
        {
            var cam = go_MainCamera.GetComponent<Camera>();
            cam.orthographicSize = 6.0f;
            cam.backgroundColor = new Color(0.529f, 0.784f, 0.922f, 1f);
            cam.clearFlags = CameraClearFlags.SolidColor;
            EditorUtility.SetDirty(go_MainCamera);
        }

        // --- Ground ---
        var go_Ground = new GameObject("Ground");
        go_Ground.tag = "Ground";
        go_Ground.transform.position = new Vector3(0.0f, -5.0f, 0.0f);
        var go_Ground_rb = go_Ground.AddComponent<Rigidbody2D>();
        go_Ground_rb.bodyType = RigidbodyType2D.Static;
        var go_Ground_bc = go_Ground.AddComponent<BoxCollider2D>();
        go_Ground_bc.size = new Vector2(30.0f, 1.0f);
        var go_Ground_sr = go_Ground.AddComponent<SpriteRenderer>();
        if (sprite_ground_grass != null) go_Ground_sr.sprite = sprite_ground_grass;
        if (unlitMat != null) go_Ground_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Ground);

        // --- Slingshot ---
        var go_Slingshot = new GameObject("Slingshot");
        go_Slingshot.transform.position = new Vector3(-5.0f, -3.5f, 0.0f);
        go_Slingshot.AddComponent<AngryBirds.Slingshot>();
        // Slingshot.throwSpeed = 5.0
        var go_Slingshot_sr = go_Slingshot.AddComponent<SpriteRenderer>();
        if (sprite_slingshot != null) go_Slingshot_sr.sprite = sprite_slingshot;
        if (unlitMat != null) go_Slingshot_sr.sharedMaterial = unlitMat;
        EditorUtility.SetDirty(go_Slingshot);

        // --- Destroyer_Bottom ---
        var go_Destroyer_Bottom = new GameObject("Destroyer_Bottom");
        go_Destroyer_Bottom.transform.position = new Vector3(0.0f, -10.0f, 0.0f);
        var go_Destroyer_Bottom_rb = go_Destroyer_Bottom.AddComponent<Rigidbody2D>();
        go_Destroyer_Bottom_rb.bodyType = RigidbodyType2D.Static;
        var go_Destroyer_Bottom_bc = go_Destroyer_Bottom.AddComponent<BoxCollider2D>();
        go_Destroyer_Bottom_bc.size = new Vector2(40.0f, 2.0f);
        go_Destroyer_Bottom_bc.isTrigger = true;
        go_Destroyer_Bottom.AddComponent<AngryBirds.Destroyer>();
        EditorUtility.SetDirty(go_Destroyer_Bottom);

        // --- Destroyer_Left ---
        var go_Destroyer_Left = new GameObject("Destroyer_Left");
        go_Destroyer_Left.transform.position = new Vector3(-18.0f, 0.0f, 0.0f);
        var go_Destroyer_Left_rb = go_Destroyer_Left.AddComponent<Rigidbody2D>();
        go_Destroyer_Left_rb.bodyType = RigidbodyType2D.Static;
        var go_Destroyer_Left_bc = go_Destroyer_Left.AddComponent<BoxCollider2D>();
        go_Destroyer_Left_bc.size = new Vector2(2.0f, 30.0f);
        go_Destroyer_Left_bc.isTrigger = true;
        go_Destroyer_Left.AddComponent<AngryBirds.Destroyer>();
        EditorUtility.SetDirty(go_Destroyer_Left);

        // --- Destroyer_Right ---
        var go_Destroyer_Right = new GameObject("Destroyer_Right");
        go_Destroyer_Right.transform.position = new Vector3(18.0f, 0.0f, 0.0f);
        var go_Destroyer_Right_rb = go_Destroyer_Right.AddComponent<Rigidbody2D>();
        go_Destroyer_Right_rb.bodyType = RigidbodyType2D.Static;
        var go_Destroyer_Right_bc = go_Destroyer_Right.AddComponent<BoxCollider2D>();
        go_Destroyer_Right_bc.size = new Vector2(2.0f, 30.0f);
        go_Destroyer_Right_bc.isTrigger = true;
        go_Destroyer_Right.AddComponent<AngryBirds.Destroyer>();
        EditorUtility.SetDirty(go_Destroyer_Right);

        // --- Bird_1 ---
        var go_Bird_1 = new GameObject("Bird_1");
        go_Bird_1.tag = "Bird";
        go_Bird_1.transform.position = new Vector3(-5.0f, -3.5f, 0.0f);
        var go_Bird_1_rb = go_Bird_1.AddComponent<Rigidbody2D>();
        var go_Bird_1_cc = go_Bird_1.AddComponent<CircleCollider2D>();
        go_Bird_1_cc.radius = 0.3f;
        var go_Bird_1_sr = go_Bird_1.AddComponent<SpriteRenderer>();
        if (sprite_bird_red != null) go_Bird_1_sr.sprite = sprite_bird_red;
        if (unlitMat != null) go_Bird_1_sr.sharedMaterial = unlitMat;
        go_Bird_1.AddComponent<AudioSource>();
        go_Bird_1.AddComponent<AngryBirds.Bird>();
        EditorUtility.SetDirty(go_Bird_1);

        // --- Bird_2 ---
        var go_Bird_2 = new GameObject("Bird_2");
        go_Bird_2.tag = "Bird";
        go_Bird_2.transform.position = new Vector3(-7.0f, -4.2f, 0.0f);
        var go_Bird_2_rb = go_Bird_2.AddComponent<Rigidbody2D>();
        var go_Bird_2_cc = go_Bird_2.AddComponent<CircleCollider2D>();
        go_Bird_2_cc.radius = 0.3f;
        var go_Bird_2_sr = go_Bird_2.AddComponent<SpriteRenderer>();
        if (sprite_bird_red != null) go_Bird_2_sr.sprite = sprite_bird_red;
        if (unlitMat != null) go_Bird_2_sr.sharedMaterial = unlitMat;
        go_Bird_2.AddComponent<AudioSource>();
        go_Bird_2.AddComponent<AngryBirds.Bird>();
        EditorUtility.SetDirty(go_Bird_2);

        // --- Bird_3 ---
        var go_Bird_3 = new GameObject("Bird_3");
        go_Bird_3.tag = "Bird";
        go_Bird_3.transform.position = new Vector3(-8.0f, -4.2f, 0.0f);
        var go_Bird_3_rb = go_Bird_3.AddComponent<Rigidbody2D>();
        var go_Bird_3_cc = go_Bird_3.AddComponent<CircleCollider2D>();
        go_Bird_3_cc.radius = 0.3f;
        var go_Bird_3_sr = go_Bird_3.AddComponent<SpriteRenderer>();
        if (sprite_bird_red != null) go_Bird_3_sr.sprite = sprite_bird_red;
        if (unlitMat != null) go_Bird_3_sr.sharedMaterial = unlitMat;
        go_Bird_3.AddComponent<AudioSource>();
        go_Bird_3.AddComponent<AngryBirds.Bird>();
        EditorUtility.SetDirty(go_Bird_3);

        // --- B_pL ---
        var go_B_pL = new GameObject("B_pL");
        go_B_pL.tag = "Brick";
        go_B_pL.transform.position = new Vector3(4.0f, -4.0f, 0.0f);
        var go_B_pL_rb = go_B_pL.AddComponent<Rigidbody2D>();
        go_B_pL_rb.mass = 0.5f;
        var go_B_pL_bc = go_B_pL.AddComponent<BoxCollider2D>();
        go_B_pL_bc.size = new Vector2(0.4f, 1.0f);
        var go_B_pL_sr = go_B_pL.AddComponent<SpriteRenderer>();
        if (sprite_brick_wood != null) go_B_pL_sr.sprite = sprite_brick_wood;
        if (unlitMat != null) go_B_pL_sr.sharedMaterial = unlitMat;
        go_B_pL.AddComponent<AudioSource>();
        go_B_pL.AddComponent<AngryBirds.Brick>();
        // Brick.health = 70
        // Brick.maxHealth = 70
        EditorUtility.SetDirty(go_B_pL);

        // --- B_pR ---
        var go_B_pR = new GameObject("B_pR");
        go_B_pR.tag = "Brick";
        go_B_pR.transform.position = new Vector3(6.0f, -4.0f, 0.0f);
        var go_B_pR_rb = go_B_pR.AddComponent<Rigidbody2D>();
        go_B_pR_rb.mass = 0.5f;
        var go_B_pR_bc = go_B_pR.AddComponent<BoxCollider2D>();
        go_B_pR_bc.size = new Vector2(0.4f, 1.0f);
        var go_B_pR_sr = go_B_pR.AddComponent<SpriteRenderer>();
        if (sprite_brick_wood != null) go_B_pR_sr.sprite = sprite_brick_wood;
        if (unlitMat != null) go_B_pR_sr.sharedMaterial = unlitMat;
        go_B_pR.AddComponent<AudioSource>();
        go_B_pR.AddComponent<AngryBirds.Brick>();
        // Brick.health = 70
        // Brick.maxHealth = 70
        EditorUtility.SetDirty(go_B_pR);

        // --- B_b1 ---
        var go_B_b1 = new GameObject("B_b1");
        go_B_b1.tag = "Brick";
        go_B_b1.transform.position = new Vector3(5.0f, -3.2f, 0.0f);
        var go_B_b1_rb = go_B_b1.AddComponent<Rigidbody2D>();
        go_B_b1_rb.mass = 0.5f;
        var go_B_b1_bc = go_B_b1.AddComponent<BoxCollider2D>();
        go_B_b1_bc.size = new Vector2(2.5f, 0.3f);
        var go_B_b1_sr = go_B_b1.AddComponent<SpriteRenderer>();
        if (sprite_brick_wood != null) go_B_b1_sr.sprite = sprite_brick_wood;
        if (unlitMat != null) go_B_b1_sr.sharedMaterial = unlitMat;
        go_B_b1.AddComponent<AudioSource>();
        go_B_b1.AddComponent<AngryBirds.Brick>();
        // Brick.health = 50
        // Brick.maxHealth = 50
        EditorUtility.SetDirty(go_B_b1);

        // --- B_uL ---
        var go_B_uL = new GameObject("B_uL");
        go_B_uL.tag = "Brick";
        go_B_uL.transform.position = new Vector3(4.5f, -2.7f, 0.0f);
        var go_B_uL_rb = go_B_uL.AddComponent<Rigidbody2D>();
        go_B_uL_rb.mass = 0.5f;
        var go_B_uL_bc = go_B_uL.AddComponent<BoxCollider2D>();
        go_B_uL_bc.size = new Vector2(0.4f, 0.7f);
        var go_B_uL_sr = go_B_uL.AddComponent<SpriteRenderer>();
        if (sprite_brick_wood != null) go_B_uL_sr.sprite = sprite_brick_wood;
        if (unlitMat != null) go_B_uL_sr.sharedMaterial = unlitMat;
        go_B_uL.AddComponent<AudioSource>();
        go_B_uL.AddComponent<AngryBirds.Brick>();
        // Brick.health = 40
        // Brick.maxHealth = 40
        EditorUtility.SetDirty(go_B_uL);

        // --- B_uR ---
        var go_B_uR = new GameObject("B_uR");
        go_B_uR.tag = "Brick";
        go_B_uR.transform.position = new Vector3(5.5f, -2.7f, 0.0f);
        var go_B_uR_rb = go_B_uR.AddComponent<Rigidbody2D>();
        go_B_uR_rb.mass = 0.5f;
        var go_B_uR_bc = go_B_uR.AddComponent<BoxCollider2D>();
        go_B_uR_bc.size = new Vector2(0.4f, 0.7f);
        var go_B_uR_sr = go_B_uR.AddComponent<SpriteRenderer>();
        if (sprite_brick_wood != null) go_B_uR_sr.sprite = sprite_brick_wood;
        if (unlitMat != null) go_B_uR_sr.sharedMaterial = unlitMat;
        go_B_uR.AddComponent<AudioSource>();
        go_B_uR.AddComponent<AngryBirds.Brick>();
        // Brick.health = 40
        // Brick.maxHealth = 40
        EditorUtility.SetDirty(go_B_uR);

        // --- B_cap ---
        var go_B_cap = new GameObject("B_cap");
        go_B_cap.tag = "Brick";
        go_B_cap.transform.position = new Vector3(5.0f, -2.1f, 0.0f);
        var go_B_cap_rb = go_B_cap.AddComponent<Rigidbody2D>();
        go_B_cap_rb.mass = 0.5f;
        var go_B_cap_bc = go_B_cap.AddComponent<BoxCollider2D>();
        go_B_cap_bc.size = new Vector2(1.5f, 0.3f);
        var go_B_cap_sr = go_B_cap.AddComponent<SpriteRenderer>();
        if (sprite_brick_wood != null) go_B_cap_sr.sprite = sprite_brick_wood;
        if (unlitMat != null) go_B_cap_sr.sharedMaterial = unlitMat;
        go_B_cap.AddComponent<AudioSource>();
        go_B_cap.AddComponent<AngryBirds.Brick>();
        // Brick.health = 90
        // Brick.maxHealth = 90
        EditorUtility.SetDirty(go_B_cap);

        // --- Pig_1 ---
        var go_Pig_1 = new GameObject("Pig_1");
        go_Pig_1.tag = "Pig";
        go_Pig_1.transform.position = new Vector3(5.0f, -3.7f, 0.0f);
        var go_Pig_1_rb = go_Pig_1.AddComponent<Rigidbody2D>();
        go_Pig_1_rb.mass = 0.8f;
        var go_Pig_1_cc = go_Pig_1.AddComponent<CircleCollider2D>();
        go_Pig_1_cc.radius = 0.3f;
        var go_Pig_1_sr = go_Pig_1.AddComponent<SpriteRenderer>();
        if (sprite_pig_normal != null) go_Pig_1_sr.sprite = sprite_pig_normal;
        if (unlitMat != null) go_Pig_1_sr.sharedMaterial = unlitMat;
        go_Pig_1.AddComponent<AudioSource>();
        go_Pig_1.AddComponent<AngryBirds.Pig>();
        // Pig.health = 150.0
        EditorUtility.SetDirty(go_Pig_1);

        // --- Pig_2 ---
        var go_Pig_2 = new GameObject("Pig_2");
        go_Pig_2.tag = "Pig";
        go_Pig_2.transform.position = new Vector3(6.5f, -4.2f, 0.0f);
        var go_Pig_2_rb = go_Pig_2.AddComponent<Rigidbody2D>();
        go_Pig_2_rb.mass = 0.8f;
        var go_Pig_2_cc = go_Pig_2.AddComponent<CircleCollider2D>();
        go_Pig_2_cc.radius = 0.3f;
        var go_Pig_2_sr = go_Pig_2.AddComponent<SpriteRenderer>();
        if (sprite_pig_normal != null) go_Pig_2_sr.sprite = sprite_pig_normal;
        if (unlitMat != null) go_Pig_2_sr.sharedMaterial = unlitMat;
        go_Pig_2.AddComponent<AudioSource>();
        go_Pig_2.AddComponent<AngryBirds.Pig>();
        // Pig.health = 150.0
        EditorUtility.SetDirty(go_Pig_2);

        // --- GameManager ---
        var go_GameManager = new GameObject("GameManager");
        go_GameManager.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        go_GameManager.AddComponent<AngryBirds.GameManager>();
        EditorUtility.SetDirty(go_GameManager);

        // --- QuitHandler ---
        var go_QuitHandler = new GameObject("QuitHandler");
        go_QuitHandler.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
        go_QuitHandler.AddComponent<AngryBirds.QuitHandler>();
        EditorUtility.SetDirty(go_QuitHandler);

        // === WIRE CROSS-REFERENCES ===
        {
            var so = new SerializedObject(go_Slingshot.GetComponent<AngryBirds.Slingshot>());
            var prop = so.FindProperty("birdToThrow");
            if (prop != null) { prop.objectReferenceValue = go_Bird_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Slingshot.GetComponent<AngryBirds.Slingshot>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Slingshot; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Destroyer_Bottom.GetComponent<AngryBirds.Destroyer>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Destroyer_Bottom; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Destroyer_Left.GetComponent<AngryBirds.Destroyer>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Destroyer_Left; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Destroyer_Right.GetComponent<AngryBirds.Destroyer>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Destroyer_Right; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Bird_1.GetComponent<AngryBirds.Bird>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Bird_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Bird_2.GetComponent<AngryBirds.Bird>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Bird_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Bird_3.GetComponent<AngryBirds.Bird>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Bird_3; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_B_pL.GetComponent<AngryBirds.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_B_pL; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_B_pR.GetComponent<AngryBirds.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_B_pR; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_B_b1.GetComponent<AngryBirds.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_B_b1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_B_uL.GetComponent<AngryBirds.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_B_uL; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_B_uR.GetComponent<AngryBirds.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_B_uR; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_B_cap.GetComponent<AngryBirds.Brick>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_B_cap; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pig_1.GetComponent<AngryBirds.Pig>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pig_1; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_Pig_2.GetComponent<AngryBirds.Pig>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_Pig_2; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_GameManager.GetComponent<AngryBirds.GameManager>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_GameManager; so.ApplyModifiedProperties(); }
        }
        {
            var so = new SerializedObject(go_QuitHandler.GetComponent<AngryBirds.QuitHandler>());
            var prop = so.FindProperty("gameObject");
            if (prop != null) { prop.objectReferenceValue = go_QuitHandler; so.ApplyModifiedProperties(); }
        }

        // === SAVE ===
        UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(
            UnityEditor.SceneManagement.EditorSceneManager.GetActiveScene());
        UnityEditor.SceneManagement.EditorSceneManager.SaveOpenScenes();

        result = "Scene setup complete: 19 GameObjects";
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
