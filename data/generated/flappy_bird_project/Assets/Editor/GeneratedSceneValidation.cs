using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.Linq;
using System.Text;

public class GeneratedSceneValidation
{
    public static string Execute()
    {
        var failures = new List<string>();
        int expectedCount = 17;

        // === GAMEOBJECT COUNT ===
        var allGOs = Object.FindObjectsOfType<GameObject>();
        if (allGOs.Length < expectedCount)
            failures.Add($"GameObject count {allGOs.Length} < expected {expectedCount}");

        // --- MainCamera ---
        {
            var go = GameObject.Find("MainCamera");
            if (go == null) failures.Add("Missing GameObject: MainCamera");
            else
            {
            }
        }

        // --- Player ---
        {
            var go = GameObject.Find("Player");
            if (go == null) failures.Add("Missing GameObject: Player");
            else
            {
            }
        }

        // --- Ground ---
        {
            var go = GameObject.Find("Ground");
            if (go == null) failures.Add("Missing GameObject: Ground");
            else
            {
                if (go.tag != "Obstacle") failures.Add("Ground tag " + go.tag + " != Obstacle");
            }
        }

        // --- Ceiling ---
        {
            var go = GameObject.Find("Ceiling");
            if (go == null) failures.Add("Missing GameObject: Ceiling");
            else
            {
                if (go.tag != "Obstacle") failures.Add("Ceiling tag " + go.tag + " != Obstacle");
            }
        }

        // --- Pipes ---
        {
            var go = GameObject.Find("Pipes");
            if (go == null) failures.Add("Missing GameObject: Pipes");
            else
            {
            }
        }

        // --- Top ---
        {
            var go = GameObject.Find("Top");
            if (go == null) failures.Add("Missing GameObject: Top");
            else
            {
                if (go.tag != "Obstacle") failures.Add("Top tag " + go.tag + " != Obstacle");
            }
        }

        // --- Bottom ---
        {
            var go = GameObject.Find("Bottom");
            if (go == null) failures.Add("Missing GameObject: Bottom");
            else
            {
                if (go.tag != "Obstacle") failures.Add("Bottom tag " + go.tag + " != Obstacle");
            }
        }

        // --- Scoring ---
        {
            var go = GameObject.Find("Scoring");
            if (go == null) failures.Add("Missing GameObject: Scoring");
            else
            {
                if (go.tag != "Scoring") failures.Add("Scoring tag " + go.tag + " != Scoring");
            }
        }

        // --- Spawner ---
        {
            var go = GameObject.Find("Spawner");
            if (go == null) failures.Add("Missing GameObject: Spawner");
            else
            {
                {
                    var _comp = go.GetComponent<Spawner>();
                    if (_comp == null) failures.Add("Spawner missing component Spawner");
                    else {
                        var so = new SerializedObject(_comp);
                        { var _p = so.FindProperty("prefab"); if (_p == null || _p.objectReferenceValue == null) failures.Add("Spawner.prefab null (expected Pipes)"); else if (_p.objectReferenceValue.name != "Pipes") failures.Add("Spawner.prefab " + _p.objectReferenceValue.name + " != Pipes"); }
                    }
                }
            }
        }

        // --- Background ---
        {
            var go = GameObject.Find("Background");
            if (go == null) failures.Add("Missing GameObject: Background");
            else
            {
            }
        }

        // --- GroundParallax ---
        {
            var go = GameObject.Find("GroundParallax");
            if (go == null) failures.Add("Missing GameObject: GroundParallax");
            else
            {
            }
        }

        // --- Canvas ---
        {
            var go = GameObject.Find("Canvas");
            if (go == null) failures.Add("Missing GameObject: Canvas");
            else
            {
            }
        }

        // --- ScoreText ---
        {
            var go = GameObject.Find("ScoreText");
            if (go == null) failures.Add("Missing GameObject: ScoreText");
            else
            {
            }
        }

        // --- GameOver ---
        {
            var go = GameObject.Find("GameOver");
            if (go == null) failures.Add("Missing GameObject: GameOver");
            else
            {
            }
        }

        // --- PlayButton ---
        {
            var go = GameObject.Find("PlayButton");
            if (go == null) failures.Add("Missing GameObject: PlayButton");
            else
            {
            }
        }

        // --- GameManager ---
        {
            var go = GameObject.Find("GameManager");
            if (go == null) failures.Add("Missing GameObject: GameManager");
            else
            {
                {
                    var _comp = go.GetComponent<GameManager>();
                    if (_comp == null) failures.Add("GameManager missing component GameManager");
                    else {
                        var so = new SerializedObject(_comp);
                        { var _p = so.FindProperty("gameOverDisplay"); if (_p == null || _p.objectReferenceValue == null) failures.Add("GameManager.gameOverDisplay null (expected GameOver)"); else if (_p.objectReferenceValue.name != "GameOver") failures.Add("GameManager.gameOverDisplay " + _p.objectReferenceValue.name + " != GameOver"); }
                        { var _p = so.FindProperty("playButton"); if (_p == null || _p.objectReferenceValue == null) failures.Add("GameManager.playButton null (expected PlayButton)"); else if (_p.objectReferenceValue.name != "PlayButton") failures.Add("GameManager.playButton " + _p.objectReferenceValue.name + " != PlayButton"); }
                    }
                }
            }
        }

        // --- PlayButtonHandler ---
        {
            var go = GameObject.Find("PlayButtonHandler");
            if (go == null) failures.Add("Missing GameObject: PlayButtonHandler");
            else
            {
            }
        }

        var sb = new StringBuilder();
        if (failures.Count == 0)
            sb.AppendLine("PASS: validated " + expectedCount + " GameObjects");
        else
        {
            sb.AppendLine("FAIL: " + failures.Count + " issues");
            foreach (var f in failures) sb.AppendLine("  - " + f);
        }
        return sb.ToString();
    }
}
