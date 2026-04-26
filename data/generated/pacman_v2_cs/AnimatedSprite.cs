using System.Collections.Generic;
using UnityEngine;
[RequireComponent(typeof(SpriteRenderer))]
public class AnimatedSprite : MonoBehaviour
{
    public float animationTime = 0.25f;
    public bool loop = true;
    public int AnimationFrame = 0;
    public float Timer = 0.0f;
    public Sprite[] sprites;
    [SerializeField] private SpriteRenderer SpriteRenderer;
     void Awake()
    {
        SpriteRenderer = GetComponent<SpriteRenderer>();
        AnimationFrame = 0;
        Timer = 0.0f;
    }
     void OnEnable()
    {
        if (SpriteRenderer != null)
        {
            SpriteRenderer.enabled = true;
        }
    }
     void OnDisable()
    {
        if (SpriteRenderer != null)
        {
            SpriteRenderer.enabled = false;
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
        if (SpriteRenderer == null || !SpriteRenderer.enabled)
        {
            return;
        }
        AnimationFrame += 1;
        if (AnimationFrame >= sprites.Length && loop)
        {
            AnimationFrame = 0;
        }
        if (AnimationFrame >= 0 && AnimationFrame < sprites.Length)
        {
            SpriteRenderer.sprite = sprites[AnimationFrame];
        }
    }
    public void Restart()
    {
        AnimationFrame = -1;
        Timer = 0.0f;
        Advance();
    }
    public static Sprite LoadSpriteFile(string name, int? sizePx)
    {
        {
        }
        {
        }
        if (sizePx != null)
        {
        }
        return surf;
    }
}
