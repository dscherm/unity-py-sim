using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Breakout;

public class GeneratedSceneValidation
{
    public static string Execute()
    {
        var failures = new List<string>();
        int expectedCount = 87;

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

        // --- Paddle ---
        {
            var go = GameObject.Find("Paddle");
            if (go == null) failures.Add("Missing GameObject: Paddle");
            else
            {
                if (go.tag != "Paddle") failures.Add("Paddle tag " + go.tag + " != Paddle");
            }
        }

        // --- Ball ---
        {
            var go = GameObject.Find("Ball");
            if (go == null) failures.Add("Missing GameObject: Ball");
            else
            {
                if (go.tag != "Ball") failures.Add("Ball tag " + go.tag + " != Ball");
            }
        }

        // --- LeftWall ---
        {
            var go = GameObject.Find("LeftWall");
            if (go == null) failures.Add("Missing GameObject: LeftWall");
            else
            {
                if (go.tag != "Wall") failures.Add("LeftWall tag " + go.tag + " != Wall");
            }
        }

        // --- RightWall ---
        {
            var go = GameObject.Find("RightWall");
            if (go == null) failures.Add("Missing GameObject: RightWall");
            else
            {
                if (go.tag != "Wall") failures.Add("RightWall tag " + go.tag + " != Wall");
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

        // --- Brick_0_0 ---
        {
            var go = GameObject.Find("Brick_0_0");
            if (go == null) failures.Add("Missing GameObject: Brick_0_0");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_0_0 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_0_1 ---
        {
            var go = GameObject.Find("Brick_0_1");
            if (go == null) failures.Add("Missing GameObject: Brick_0_1");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_0_1 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_0_2 ---
        {
            var go = GameObject.Find("Brick_0_2");
            if (go == null) failures.Add("Missing GameObject: Brick_0_2");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_0_2 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_0_3 ---
        {
            var go = GameObject.Find("Brick_0_3");
            if (go == null) failures.Add("Missing GameObject: Brick_0_3");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_0_3 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_0_4 ---
        {
            var go = GameObject.Find("Brick_0_4");
            if (go == null) failures.Add("Missing GameObject: Brick_0_4");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_0_4 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_0_5 ---
        {
            var go = GameObject.Find("Brick_0_5");
            if (go == null) failures.Add("Missing GameObject: Brick_0_5");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_0_5 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_0_6 ---
        {
            var go = GameObject.Find("Brick_0_6");
            if (go == null) failures.Add("Missing GameObject: Brick_0_6");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_0_6 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_0_7 ---
        {
            var go = GameObject.Find("Brick_0_7");
            if (go == null) failures.Add("Missing GameObject: Brick_0_7");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_0_7 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_0_8 ---
        {
            var go = GameObject.Find("Brick_0_8");
            if (go == null) failures.Add("Missing GameObject: Brick_0_8");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_0_8 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_0_9 ---
        {
            var go = GameObject.Find("Brick_0_9");
            if (go == null) failures.Add("Missing GameObject: Brick_0_9");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_0_9 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_1_0 ---
        {
            var go = GameObject.Find("Brick_1_0");
            if (go == null) failures.Add("Missing GameObject: Brick_1_0");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_1_0 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_1_1 ---
        {
            var go = GameObject.Find("Brick_1_1");
            if (go == null) failures.Add("Missing GameObject: Brick_1_1");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_1_1 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_1_2 ---
        {
            var go = GameObject.Find("Brick_1_2");
            if (go == null) failures.Add("Missing GameObject: Brick_1_2");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_1_2 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_1_3 ---
        {
            var go = GameObject.Find("Brick_1_3");
            if (go == null) failures.Add("Missing GameObject: Brick_1_3");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_1_3 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_1_4 ---
        {
            var go = GameObject.Find("Brick_1_4");
            if (go == null) failures.Add("Missing GameObject: Brick_1_4");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_1_4 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_1_5 ---
        {
            var go = GameObject.Find("Brick_1_5");
            if (go == null) failures.Add("Missing GameObject: Brick_1_5");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_1_5 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_1_6 ---
        {
            var go = GameObject.Find("Brick_1_6");
            if (go == null) failures.Add("Missing GameObject: Brick_1_6");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_1_6 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_1_7 ---
        {
            var go = GameObject.Find("Brick_1_7");
            if (go == null) failures.Add("Missing GameObject: Brick_1_7");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_1_7 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_1_8 ---
        {
            var go = GameObject.Find("Brick_1_8");
            if (go == null) failures.Add("Missing GameObject: Brick_1_8");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_1_8 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_1_9 ---
        {
            var go = GameObject.Find("Brick_1_9");
            if (go == null) failures.Add("Missing GameObject: Brick_1_9");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_1_9 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_2_0 ---
        {
            var go = GameObject.Find("Brick_2_0");
            if (go == null) failures.Add("Missing GameObject: Brick_2_0");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_2_0 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_2_1 ---
        {
            var go = GameObject.Find("Brick_2_1");
            if (go == null) failures.Add("Missing GameObject: Brick_2_1");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_2_1 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_2_2 ---
        {
            var go = GameObject.Find("Brick_2_2");
            if (go == null) failures.Add("Missing GameObject: Brick_2_2");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_2_2 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_2_3 ---
        {
            var go = GameObject.Find("Brick_2_3");
            if (go == null) failures.Add("Missing GameObject: Brick_2_3");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_2_3 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_2_4 ---
        {
            var go = GameObject.Find("Brick_2_4");
            if (go == null) failures.Add("Missing GameObject: Brick_2_4");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_2_4 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_2_5 ---
        {
            var go = GameObject.Find("Brick_2_5");
            if (go == null) failures.Add("Missing GameObject: Brick_2_5");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_2_5 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_2_6 ---
        {
            var go = GameObject.Find("Brick_2_6");
            if (go == null) failures.Add("Missing GameObject: Brick_2_6");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_2_6 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_2_7 ---
        {
            var go = GameObject.Find("Brick_2_7");
            if (go == null) failures.Add("Missing GameObject: Brick_2_7");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_2_7 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_2_8 ---
        {
            var go = GameObject.Find("Brick_2_8");
            if (go == null) failures.Add("Missing GameObject: Brick_2_8");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_2_8 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_2_9 ---
        {
            var go = GameObject.Find("Brick_2_9");
            if (go == null) failures.Add("Missing GameObject: Brick_2_9");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_2_9 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_3_0 ---
        {
            var go = GameObject.Find("Brick_3_0");
            if (go == null) failures.Add("Missing GameObject: Brick_3_0");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_3_0 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_3_1 ---
        {
            var go = GameObject.Find("Brick_3_1");
            if (go == null) failures.Add("Missing GameObject: Brick_3_1");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_3_1 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_3_2 ---
        {
            var go = GameObject.Find("Brick_3_2");
            if (go == null) failures.Add("Missing GameObject: Brick_3_2");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_3_2 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_3_3 ---
        {
            var go = GameObject.Find("Brick_3_3");
            if (go == null) failures.Add("Missing GameObject: Brick_3_3");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_3_3 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_3_4 ---
        {
            var go = GameObject.Find("Brick_3_4");
            if (go == null) failures.Add("Missing GameObject: Brick_3_4");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_3_4 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_3_5 ---
        {
            var go = GameObject.Find("Brick_3_5");
            if (go == null) failures.Add("Missing GameObject: Brick_3_5");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_3_5 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_3_6 ---
        {
            var go = GameObject.Find("Brick_3_6");
            if (go == null) failures.Add("Missing GameObject: Brick_3_6");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_3_6 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_3_7 ---
        {
            var go = GameObject.Find("Brick_3_7");
            if (go == null) failures.Add("Missing GameObject: Brick_3_7");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_3_7 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_3_8 ---
        {
            var go = GameObject.Find("Brick_3_8");
            if (go == null) failures.Add("Missing GameObject: Brick_3_8");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_3_8 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_3_9 ---
        {
            var go = GameObject.Find("Brick_3_9");
            if (go == null) failures.Add("Missing GameObject: Brick_3_9");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_3_9 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_4_0 ---
        {
            var go = GameObject.Find("Brick_4_0");
            if (go == null) failures.Add("Missing GameObject: Brick_4_0");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_4_0 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_4_1 ---
        {
            var go = GameObject.Find("Brick_4_1");
            if (go == null) failures.Add("Missing GameObject: Brick_4_1");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_4_1 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_4_2 ---
        {
            var go = GameObject.Find("Brick_4_2");
            if (go == null) failures.Add("Missing GameObject: Brick_4_2");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_4_2 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_4_3 ---
        {
            var go = GameObject.Find("Brick_4_3");
            if (go == null) failures.Add("Missing GameObject: Brick_4_3");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_4_3 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_4_4 ---
        {
            var go = GameObject.Find("Brick_4_4");
            if (go == null) failures.Add("Missing GameObject: Brick_4_4");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_4_4 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_4_5 ---
        {
            var go = GameObject.Find("Brick_4_5");
            if (go == null) failures.Add("Missing GameObject: Brick_4_5");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_4_5 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_4_6 ---
        {
            var go = GameObject.Find("Brick_4_6");
            if (go == null) failures.Add("Missing GameObject: Brick_4_6");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_4_6 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_4_7 ---
        {
            var go = GameObject.Find("Brick_4_7");
            if (go == null) failures.Add("Missing GameObject: Brick_4_7");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_4_7 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_4_8 ---
        {
            var go = GameObject.Find("Brick_4_8");
            if (go == null) failures.Add("Missing GameObject: Brick_4_8");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_4_8 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_4_9 ---
        {
            var go = GameObject.Find("Brick_4_9");
            if (go == null) failures.Add("Missing GameObject: Brick_4_9");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_4_9 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_5_0 ---
        {
            var go = GameObject.Find("Brick_5_0");
            if (go == null) failures.Add("Missing GameObject: Brick_5_0");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_5_0 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_5_1 ---
        {
            var go = GameObject.Find("Brick_5_1");
            if (go == null) failures.Add("Missing GameObject: Brick_5_1");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_5_1 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_5_2 ---
        {
            var go = GameObject.Find("Brick_5_2");
            if (go == null) failures.Add("Missing GameObject: Brick_5_2");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_5_2 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_5_3 ---
        {
            var go = GameObject.Find("Brick_5_3");
            if (go == null) failures.Add("Missing GameObject: Brick_5_3");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_5_3 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_5_4 ---
        {
            var go = GameObject.Find("Brick_5_4");
            if (go == null) failures.Add("Missing GameObject: Brick_5_4");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_5_4 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_5_5 ---
        {
            var go = GameObject.Find("Brick_5_5");
            if (go == null) failures.Add("Missing GameObject: Brick_5_5");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_5_5 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_5_6 ---
        {
            var go = GameObject.Find("Brick_5_6");
            if (go == null) failures.Add("Missing GameObject: Brick_5_6");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_5_6 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_5_7 ---
        {
            var go = GameObject.Find("Brick_5_7");
            if (go == null) failures.Add("Missing GameObject: Brick_5_7");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_5_7 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_5_8 ---
        {
            var go = GameObject.Find("Brick_5_8");
            if (go == null) failures.Add("Missing GameObject: Brick_5_8");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_5_8 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_5_9 ---
        {
            var go = GameObject.Find("Brick_5_9");
            if (go == null) failures.Add("Missing GameObject: Brick_5_9");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_5_9 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_6_0 ---
        {
            var go = GameObject.Find("Brick_6_0");
            if (go == null) failures.Add("Missing GameObject: Brick_6_0");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_6_0 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_6_1 ---
        {
            var go = GameObject.Find("Brick_6_1");
            if (go == null) failures.Add("Missing GameObject: Brick_6_1");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_6_1 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_6_2 ---
        {
            var go = GameObject.Find("Brick_6_2");
            if (go == null) failures.Add("Missing GameObject: Brick_6_2");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_6_2 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_6_3 ---
        {
            var go = GameObject.Find("Brick_6_3");
            if (go == null) failures.Add("Missing GameObject: Brick_6_3");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_6_3 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_6_4 ---
        {
            var go = GameObject.Find("Brick_6_4");
            if (go == null) failures.Add("Missing GameObject: Brick_6_4");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_6_4 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_6_5 ---
        {
            var go = GameObject.Find("Brick_6_5");
            if (go == null) failures.Add("Missing GameObject: Brick_6_5");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_6_5 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_6_6 ---
        {
            var go = GameObject.Find("Brick_6_6");
            if (go == null) failures.Add("Missing GameObject: Brick_6_6");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_6_6 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_6_7 ---
        {
            var go = GameObject.Find("Brick_6_7");
            if (go == null) failures.Add("Missing GameObject: Brick_6_7");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_6_7 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_6_8 ---
        {
            var go = GameObject.Find("Brick_6_8");
            if (go == null) failures.Add("Missing GameObject: Brick_6_8");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_6_8 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_6_9 ---
        {
            var go = GameObject.Find("Brick_6_9");
            if (go == null) failures.Add("Missing GameObject: Brick_6_9");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_6_9 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_7_0 ---
        {
            var go = GameObject.Find("Brick_7_0");
            if (go == null) failures.Add("Missing GameObject: Brick_7_0");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_7_0 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_7_1 ---
        {
            var go = GameObject.Find("Brick_7_1");
            if (go == null) failures.Add("Missing GameObject: Brick_7_1");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_7_1 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_7_2 ---
        {
            var go = GameObject.Find("Brick_7_2");
            if (go == null) failures.Add("Missing GameObject: Brick_7_2");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_7_2 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_7_3 ---
        {
            var go = GameObject.Find("Brick_7_3");
            if (go == null) failures.Add("Missing GameObject: Brick_7_3");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_7_3 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_7_4 ---
        {
            var go = GameObject.Find("Brick_7_4");
            if (go == null) failures.Add("Missing GameObject: Brick_7_4");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_7_4 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_7_5 ---
        {
            var go = GameObject.Find("Brick_7_5");
            if (go == null) failures.Add("Missing GameObject: Brick_7_5");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_7_5 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_7_6 ---
        {
            var go = GameObject.Find("Brick_7_6");
            if (go == null) failures.Add("Missing GameObject: Brick_7_6");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_7_6 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_7_7 ---
        {
            var go = GameObject.Find("Brick_7_7");
            if (go == null) failures.Add("Missing GameObject: Brick_7_7");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_7_7 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_7_8 ---
        {
            var go = GameObject.Find("Brick_7_8");
            if (go == null) failures.Add("Missing GameObject: Brick_7_8");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_7_8 tag " + go.tag + " != Brick");
            }
        }

        // --- Brick_7_9 ---
        {
            var go = GameObject.Find("Brick_7_9");
            if (go == null) failures.Add("Missing GameObject: Brick_7_9");
            else
            {
                if (go.tag != "Brick") failures.Add("Brick_7_9 tag " + go.tag + " != Brick");
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
