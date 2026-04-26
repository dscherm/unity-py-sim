using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ResetAndRunSetup
{
    public static string Execute()
    {
        // Test sprite load first to diagnose path/meta issues
        var testSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Sprites/Bird_01.png");
        string diag = testSprite != null
            ? $"Bird_01 loads OK ({testSprite.rect.width}x{testSprite.rect.height})"
            : "Bird_01 LOAD FAILED — path or import type wrong";

        // Fresh scene to avoid stale GameObjects with null sprites
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        EditorSceneManager.SaveScene(scene, "Assets/_Project/Scenes/Scene.unity");

        var result = GeneratedSceneSetup.Execute();

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene, "Assets/_Project/Scenes/Scene.unity");

        return diag + " | " + result;
    }
}
