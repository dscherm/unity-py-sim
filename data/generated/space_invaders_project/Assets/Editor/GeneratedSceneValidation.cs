using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using SpaceInvaders;

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

        // --- Player ---
        {
            var go = GameObject.Find("Player");
            if (go == null) failures.Add("Missing GameObject: Player");
            else
            {
                if (go.tag != "Player") failures.Add("Player tag " + go.tag + " != Player");
            }
        }

        // --- InvadersGrid ---
        {
            var go = GameObject.Find("InvadersGrid");
            if (go == null) failures.Add("Missing GameObject: InvadersGrid");
            else
            {
            }
        }

        // --- Bunker_0 ---
        {
            var go = GameObject.Find("Bunker_0");
            if (go == null) failures.Add("Missing GameObject: Bunker_0");
            else
            {
                if (go.tag != "Bunker") failures.Add("Bunker_0 tag " + go.tag + " != Bunker");
            }
        }

        // --- Bunker_1 ---
        {
            var go = GameObject.Find("Bunker_1");
            if (go == null) failures.Add("Missing GameObject: Bunker_1");
            else
            {
                if (go.tag != "Bunker") failures.Add("Bunker_1 tag " + go.tag + " != Bunker");
            }
        }

        // --- Bunker_2 ---
        {
            var go = GameObject.Find("Bunker_2");
            if (go == null) failures.Add("Missing GameObject: Bunker_2");
            else
            {
                if (go.tag != "Bunker") failures.Add("Bunker_2 tag " + go.tag + " != Bunker");
            }
        }

        // --- Bunker_3 ---
        {
            var go = GameObject.Find("Bunker_3");
            if (go == null) failures.Add("Missing GameObject: Bunker_3");
            else
            {
                if (go.tag != "Bunker") failures.Add("Bunker_3 tag " + go.tag + " != Bunker");
            }
        }

        // --- MysteryShip ---
        {
            var go = GameObject.Find("MysteryShip");
            if (go == null) failures.Add("Missing GameObject: MysteryShip");
            else
            {
                if (go.tag != "MysteryShip") failures.Add("MysteryShip tag " + go.tag + " != MysteryShip");
            }
        }

        // --- BoundaryTop ---
        {
            var go = GameObject.Find("BoundaryTop");
            if (go == null) failures.Add("Missing GameObject: BoundaryTop");
            else
            {
                if (go.tag != "Boundary") failures.Add("BoundaryTop tag " + go.tag + " != Boundary");
                { int _expLayer = LayerMask.NameToLayer("Layer11"); if (_expLayer >= 0 && go.layer != _expLayer) failures.Add("BoundaryTop layer " + go.layer + " != Layer11(" + _expLayer + ")"); }
            }
        }

        // --- BoundaryBottom ---
        {
            var go = GameObject.Find("BoundaryBottom");
            if (go == null) failures.Add("Missing GameObject: BoundaryBottom");
            else
            {
                if (go.tag != "Boundary") failures.Add("BoundaryBottom tag " + go.tag + " != Boundary");
                { int _expLayer = LayerMask.NameToLayer("Layer11"); if (_expLayer >= 0 && go.layer != _expLayer) failures.Add("BoundaryBottom layer " + go.layer + " != Layer11(" + _expLayer + ")"); }
            }
        }

        // --- GameManager ---
        {
            var go = GameObject.Find("GameManager");
            if (go == null) failures.Add("Missing GameObject: GameManager");
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
