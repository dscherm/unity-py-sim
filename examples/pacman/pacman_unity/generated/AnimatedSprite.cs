using System.Collections.Generic;
using UnityEngine;
[RequireComponent(typeof(SpriteRenderer))]
public class AnimatedSprite : MonoBehaviour
{
    public string[] spriteRefs;
    public static string[] spriteRefs;
    public static float animationTime = 0.25f;
    public static bool loop = true;
    public static SpriteRenderer spriteRenderer = null;
    public static int AnimationFrame = 0;
    public static float Timer = 0.0f;
     void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
    }
     void OnEnable()
    {
        if (spriteRenderer != null)
        {
            spriteRenderer.enabled = true;
        }
    }
     void OnDisable()
    {
        if (spriteRenderer != null)
        {
            spriteRenderer.enabled = false;
        }
    }
     void Update()
    {
        Timer += Time.deltaTime;
        if (Timer >= animationTime)
        {
            Timer -= animationTime;
            Advance();
        }
    }
    public void Advance()
    {
        if (spriteRenderer == null || !spriteRenderer.enabled)
        {
            return;
        }
        AnimationFrame += 1;
        if (AnimationFrame >= spriteRefs.Length && loop)
        {
            AnimationFrame = 0;
        }
    }
    public void Restart()
    {
        AnimationFrame = -1;
        Advance();
    }
}
