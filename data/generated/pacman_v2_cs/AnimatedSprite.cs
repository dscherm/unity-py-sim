using System.Collections.Generic;
using UnityEngine;
[RequireComponent(typeof(SpriteRenderer))]
public class AnimatedSprite : MonoBehaviour
{
    public float animationTime = 0.25f;
    public bool loop = true;
    public int AnimationFrame = 0;
    public float Timer = 0.0f;
    public pygame.Surface[] sprites;
    public SpriteRenderer SpriteRenderer;
    public pygame.Surface[] sprites;
    public static object SPRITES_DIR = os.path.join(os.path.dirname(__file__), '..', 'sprites');
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
    public static pygame.Surface LoadSpriteFile(string name, int? sizePx)
    {
        if (!pygame.GetInit())
        {
            pygame.Init();
        }
        if (pygame.display.GetSurface() == null)
        {
            pygame.display.SetMode((1, 1), pygame.NOFRAME);
        }
        var path = os.path.Join(SPRITES_DIR, name);
        var surf = pygame.image.Load(path).ConvertAlpha();
        if (sizePx != null)
        {
            surf = pygame.transform.Scale(surf, (sizePx, sizePx));
        }
        return surf;
    }
}
