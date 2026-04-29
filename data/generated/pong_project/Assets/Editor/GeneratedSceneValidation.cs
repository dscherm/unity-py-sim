using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Pong;

public class GeneratedSceneValidation
{
    public static string Execute()
    {
        var failures = new List<string>();
        int expectedCount = 11;

        // === GAMEOBJECT COUNT ===
        // FU-4 FindObjectsByType migration — FindObjectsOfType is deprecated
        // in Unity 6 (CS0618); FindObjectsByType requires an explicit sort mode.
        var allGOs = Object.FindObjectsByType<GameObject>(FindObjectsSortMode.None);
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

        // --- LeftPaddle ---
        {
            var go = GameObject.Find("LeftPaddle");
            if (go == null) failures.Add("Missing GameObject: LeftPaddle");
            else
            {
                if (go.tag != "Paddle") failures.Add("LeftPaddle tag " + go.tag + " != Paddle");
            }
        }

        // --- RightPaddle ---
        {
            var go = GameObject.Find("RightPaddle");
            if (go == null) failures.Add("Missing GameObject: RightPaddle");
            else
            {
                if (go.tag != "Paddle") failures.Add("RightPaddle tag " + go.tag + " != Paddle");
            }
        }

        // --- Ball ---
        {
            var go = GameObject.Find("Ball");
            if (go == null) failures.Add("Missing GameObject: Ball");
            else
            {
            }
        }

        // --- TopWall ---
        {
            var go = GameObject.Find("TopWall");
            if (go == null) failures.Add("Missing GameObject: TopWall");
            else
            {
                if (go.tag != "Wall") failures.Add("TopWall tag " + go.tag + " != Wall");
            }
        }

        // --- BottomWall ---
        {
            var go = GameObject.Find("BottomWall");
            if (go == null) failures.Add("Missing GameObject: BottomWall");
            else
            {
                if (go.tag != "Wall") failures.Add("BottomWall tag " + go.tag + " != Wall");
            }
        }

        // --- CenterLine ---
        {
            var go = GameObject.Find("CenterLine");
            if (go == null) failures.Add("Missing GameObject: CenterLine");
            else
            {
            }
        }

        // --- Goal_left ---
        {
            var go = GameObject.Find("Goal_left");
            if (go == null) failures.Add("Missing GameObject: Goal_left");
            else
            {
            }
        }

        // --- Goal_right ---
        {
            var go = GameObject.Find("Goal_right");
            if (go == null) failures.Add("Missing GameObject: Goal_right");
            else
            {
            }
        }

        // --- ScoreManager ---
        {
            var go = GameObject.Find("ScoreManager");
            if (go == null) failures.Add("Missing GameObject: ScoreManager");
            else
            {
            }
        }

        // --- ScoreDisplay ---
        {
            var go = GameObject.Find("ScoreDisplay");
            if (go == null) failures.Add("Missing GameObject: ScoreDisplay");
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
