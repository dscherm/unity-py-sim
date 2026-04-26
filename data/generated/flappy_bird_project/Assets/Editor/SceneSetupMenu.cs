using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class SceneSetupMenu
{
    private const string ScenePath = "Assets/_Project/Scenes/Scene.unity";

    [MenuItem("Tools/Setup Generated Scene")]
    public static void Setup()
    {
        var dir = Path.GetDirectoryName(ScenePath);
        if (!string.IsNullOrEmpty(dir) && !AssetDatabase.IsValidFolder(dir))
        {
            Directory.CreateDirectory(dir);
            AssetDatabase.Refresh();
        }

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        EditorSceneManager.SaveScene(scene, ScenePath);

        var result = GeneratedSceneSetup.Execute();

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene, ScenePath);

        EditorUtility.DisplayDialog("Scene Setup", result, "OK");
    }
}
