// Editor-only Play-mode harness for headless validation runs.
//
// Invoked by the home-machine GitHub Actions workflow via:
//     Unity.exe -batchmode -projectPath <p> -executeMethod HomeMachinePlaytest.Run
//
// Behavior: enters Play mode, advances Unity for HOMEPT_FRAMES frames
// (default 300 = 5 sec at 60 fps), captures a screenshot every
// HOMEPT_SCREENSHOT_EVERY frames, tallies log errors/exceptions, writes
// a summary JSON, exits Unity with non-zero status if any errors fired.
//
// All paths and counts are env-var driven so the workflow can override
// without recompiling. Output dir defaults to data/lessons/<game>_playtest_<ts>/
// when the project sits under data/generated/<game>_project, otherwise
// to <projectPath>/playtest_<ts>/.
//
// This file is COPIED into Assets/Editor/ by the workflow before each
// run so it doesn't pollute committed project trees.

#if UNITY_EDITOR
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

public static class HomeMachinePlaytest
{
    private const string Tag = "[home-playtest]";

    private static int s_frames;
    private static int s_screenshotEvery;
    private static string s_outputDir;
    private static int s_errorCount;
    private static int s_exceptionCount;
    private static int s_warningCount;
    private static List<string> s_errorLines;
    private static int s_framesElapsed;
    private static int s_screenshotIndex;
    private static GameObject s_runner;

    public static void Run()
    {
        s_frames = ReadIntEnv("HOMEPT_FRAMES", 300);
        s_screenshotEvery = ReadIntEnv("HOMEPT_SCREENSHOT_EVERY", 60);
        s_outputDir = ResolveOutputDir();
        s_errorCount = 0;
        s_exceptionCount = 0;
        s_warningCount = 0;
        s_errorLines = new List<string>();
        s_framesElapsed = 0;
        s_screenshotIndex = 0;

        Directory.CreateDirectory(s_outputDir);
        Application.logMessageReceived += OnLog;
        EditorApplication.playModeStateChanged += OnPlayModeStateChanged;

        Log($"frames={s_frames} screenshot_every={s_screenshotEvery} output={s_outputDir}");
        EditorApplication.isPlaying = true;
    }

    private static void OnPlayModeStateChanged(PlayModeStateChange change)
    {
        if (change != PlayModeStateChange.EnteredPlayMode) return;
        s_runner = new GameObject("HomeMachinePlaytestRunner");
        UnityEngine.Object.DontDestroyOnLoad(s_runner);
        var driver = s_runner.AddComponent<PlaytestDriver>();
        driver.StartCoroutine(driver.Drive());
    }

    private static IEnumerator DriveImpl()
    {
        while (s_framesElapsed < s_frames)
        {
            if (s_screenshotEvery > 0 && s_framesElapsed % s_screenshotEvery == 0)
            {
                CaptureScreenshot();
            }
            s_framesElapsed++;
            yield return null;
        }
        CaptureScreenshot();
        Finish();
    }

    private static void CaptureScreenshot()
    {
        var name = $"frame_{s_screenshotIndex:D4}.png";
        var path = Path.Combine(s_outputDir, name);
        ScreenCapture.CaptureScreenshot(path);
        s_screenshotIndex++;
    }

    private static void OnLog(string condition, string stack, LogType type)
    {
        switch (type)
        {
            case LogType.Error:
            case LogType.Assert:
                s_errorCount++;
                s_errorLines.Add($"[error] {condition}");
                break;
            case LogType.Exception:
                s_exceptionCount++;
                s_errorLines.Add($"[exception] {condition}\n{stack}");
                break;
            case LogType.Warning:
                s_warningCount++;
                break;
        }
    }

    private static void Finish()
    {
        var summary = new Dictionary<string, object>
        {
            { "frames", s_framesElapsed },
            { "screenshots", s_screenshotIndex },
            { "errors", s_errorCount },
            { "exceptions", s_exceptionCount },
            { "warnings", s_warningCount },
            { "output_dir", s_outputDir },
            { "timestamp_utc", DateTime.UtcNow.ToString("o") },
        };
        var json = ToJson(summary, s_errorLines);
        File.WriteAllText(Path.Combine(s_outputDir, "summary.json"), json);
        Log($"errors={s_errorCount} exceptions={s_exceptionCount} warnings={s_warningCount}");

        Application.logMessageReceived -= OnLog;
        EditorApplication.playModeStateChanged -= OnPlayModeStateChanged;
        EditorApplication.isPlaying = false;

        var code = (s_errorCount + s_exceptionCount) > 0 ? 1 : 0;
        EditorApplication.Exit(code);
    }

    private static string ToJson(Dictionary<string, object> summary, List<string> errors)
    {
        var sb = new System.Text.StringBuilder();
        sb.Append("{");
        var first = true;
        foreach (var kv in summary)
        {
            if (!first) sb.Append(",");
            first = false;
            sb.Append("\"").Append(kv.Key).Append("\":");
            if (kv.Value is string str) sb.Append("\"").Append(JsonEscape(str)).Append("\"");
            else sb.Append(kv.Value);
        }
        sb.Append(",\"error_lines\":[");
        for (var i = 0; i < errors.Count; i++)
        {
            if (i > 0) sb.Append(",");
            sb.Append("\"").Append(JsonEscape(errors[i])).Append("\"");
        }
        sb.Append("]}");
        return sb.ToString();
    }

    private static string JsonEscape(string s)
    {
        return s.Replace("\\", "\\\\")
                .Replace("\"", "\\\"")
                .Replace("\n", "\\n")
                .Replace("\r", "\\r")
                .Replace("\t", "\\t");
    }

    private static int ReadIntEnv(string key, int fallback)
    {
        var raw = Environment.GetEnvironmentVariable(key);
        return int.TryParse(raw, out var v) && v > 0 ? v : fallback;
    }

    private static string ResolveOutputDir()
    {
        var explicitDir = Environment.GetEnvironmentVariable("HOMEPT_OUTPUT_DIR");
        if (!string.IsNullOrEmpty(explicitDir)) return explicitDir;

        var projectPath = Path.GetFullPath(Application.dataPath + "/..");
        var projectName = Path.GetFileName(projectPath);
        var game = projectName.EndsWith("_project") ? projectName.Substring(0, projectName.Length - "_project".Length) : projectName;
        var ts = DateTime.UtcNow.ToString("yyyyMMddTHHmmssZ");

        var repoRoot = Path.GetFullPath(Path.Combine(projectPath, "..", "..", ".."));
        var lessonsDir = Path.Combine(repoRoot, "data", "lessons");
        if (Directory.Exists(lessonsDir))
        {
            return Path.Combine(lessonsDir, $"{game}_playtest_{ts}");
        }
        return Path.Combine(projectPath, $"playtest_{ts}");
    }

    private static void Log(string msg) => Debug.Log($"{Tag} {msg}");

    // Coroutines need a MonoBehaviour host. Driver lives only during Play mode.
    private class PlaytestDriver : MonoBehaviour
    {
        public IEnumerator Drive() => DriveImpl();
    }
}
#endif
