// Auto-generated PlayMode test (Unity Test Framework).
// Game: pong
//
// Loads the game's main scene, ticks frames for ~3 seconds, asserts no
// Error / Exception / Assert log events fire. Catches runtime regressions
// (Awake/Start/Update NullRefs etc.) that the deploy-only batchmode harness
// in M-7 v1 misses.
//
// Source: tools/home_machine_playmode_test.cs.j2 — regenerate via project_scaffolder.

using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
#if UNITY_EDITOR
using UnityEditor.SceneManagement;
#endif

public class PlayModeTests
{
    const string ScenePath = "Assets/_Project/Scenes/Scene.unity";
    const int FramesToTick = 180; // ~3 seconds at 60 fps

    [UnityTest]
    public IEnumerator PlayForNSeconds_NoLoggedExceptions()
    {
        var errors = new List<string>();
        Application.LogCallback handler = (string condition, string stackTrace, LogType type) =>
        {
            if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert)
            {
                errors.Add($"[{type}] {condition}");
            }
        };
        Application.logMessageReceived += handler;
        try
        {
#if UNITY_EDITOR
            var loadParams = new LoadSceneParameters(LoadSceneMode.Single);
            yield return EditorSceneManager.LoadSceneAsyncInPlayMode(ScenePath, loadParams);
#else
            yield return SceneManager.LoadSceneAsync("Scene", LoadSceneMode.Single);
#endif
            yield return null; // one frame to settle after scene load

            for (int i = 0; i < FramesToTick; i++)
            {
                yield return null;
            }
        }
        finally
        {
            Application.logMessageReceived -= handler;
        }

        if (errors.Count > 0)
        {
            Assert.Fail(
                $"Logged {errors.Count} error(s)/exception(s) during PlayMode:\n  - "
                + string.Join("\n  - ", errors)
            );
        }
    }
}
