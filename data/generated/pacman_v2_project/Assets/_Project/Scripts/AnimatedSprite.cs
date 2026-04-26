using System.Collections.Generic;
using UnityEngine;
[RequireComponent(typeof(SpriteRenderer))]
public class AnimatedSprite : MonoBehaviour
{
    public float animationTime = 0.25f;
    public bool loop = true;
    public int animationFrame = 0;
    public float timer = 0.0f;
    public Sprite[] sprites;
    public SpriteRenderer spriteRenderer;
     void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        animationFrame = 0;
        timer = 0.0f;
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
        timer += Time.deltaTime;
        if (timer >= animationTime)
        {
            timer -= animationTime;
            Advance();
        }
    }
    public void Advance()
    {
        if (spriteRenderer == null || !spriteRenderer.enabled)
        {
            return;
        }
        animationFrame += 1;
        if (animationFrame >= sprites.Length && loop)
        {
            animationFrame = 0;
        }
        if (animationFrame >= 0 && animationFrame < sprites.Length)
        {
            spriteRenderer.sprite = sprites[animationFrame];
        }
    }
    public void Restart()
    {
        animationFrame = -1;
        timer = 0.0f;
        Advance();
    }
    public static Sprite LoadSpriteFile(string name, int? sizePx = null)
    {
        {
        }
        {
        }
        if (sizePx != null)
        {
        }
        return default;
    }
}
