using System.Collections.Generic;
using UnityEngine;
namespace SpaceInvaders
{
    [RequireComponent(typeof(SpriteRenderer))]
    public class Invader : MonoBehaviour
    {
        public float animationTime = 1f;
        public int score = 10;
        public int animationFrame = 0;
        public float Timer = 0f;
        public Color32[] animationSprites;
        public SpriteRenderer spriteRenderer;
         void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            if (spriteRenderer != null && animationSprites != null)
            {
                spriteRenderer.color = animationSprites[0];
            }
        }
         void Start()
        {
        }
         void Update()
        {
            Timer += Time.deltaTime;
            if (Timer >= animationTime)
            {
                Timer -= animationTime;
                AnimateSprite();
            }
        }
        public void AnimateSprite()
        {
            animationFrame += 1;
            if (animationFrame >= animationSprites.Length)
            {
                animationFrame = 0;
            }
            if (spriteRenderer != null && animationSprites != null)
            {
                spriteRenderer.color = animationSprites[animationFrame];
            }
        }
         void OnTriggerEnter2D(Collider2D other)
        {
            if (other.gameObject.layer == Layers.LASER)
            {
                // GameManager.Instance.OnInvaderKilled(this)
                if (GameManager.instance != null)
                {
                    GameManager.instance.OnInvaderKilled(this);
                }
            }
            // else if (other.gameObject.layer == LayerMask.NameToLayer("Boundary"))
            else if (other.gameObject.layer == Layers.BOUNDARY)
            {
                if (GameManager.instance != null)
                {
                    GameManager.instance.OnBoundaryReached();
                }
            }
        }
    }
}
