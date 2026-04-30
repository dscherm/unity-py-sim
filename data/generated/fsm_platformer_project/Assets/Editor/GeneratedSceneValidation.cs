using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using FSMPlatformer;

public class GeneratedSceneValidation
{
    public static string Execute()
    {
        var failures = new List<string>();
        int expectedCount = 7;

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

        // --- Ground ---
        {
            var go = GameObject.Find("Ground");
            if (go == null) failures.Add("Missing GameObject: Ground");
            else
            {
                if (go.tag != "Ground") failures.Add("Ground tag " + go.tag + " != Ground");
            }
        }

        // --- Player ---
        {
            var go = GameObject.Find("Player");
            if (go == null) failures.Add("Missing GameObject: Player");
            else
            {
                if (go.tag != "Player") failures.Add("Player tag " + go.tag + " != Player");
            }
        }

        // --- Enemy ---
        {
            var go = GameObject.Find("Enemy");
            if (go == null) failures.Add("Missing GameObject: Enemy");
            else
            {
                if (go.tag != "Enemy") failures.Add("Enemy tag " + go.tag + " != Enemy");
            }
        }

        // --- LeftWall ---
        {
            var go = GameObject.Find("LeftWall");
            if (go == null) failures.Add("Missing GameObject: LeftWall");
            else
            {
            }
        }

        // --- RightWall ---
        {
            var go = GameObject.Find("RightWall");
            if (go == null) failures.Add("Missing GameObject: RightWall");
            else
            {
            }
        }

        // --- StateDisplay ---
        {
            var go = GameObject.Find("StateDisplay");
            if (go == null) failures.Add("Missing GameObject: StateDisplay");
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
