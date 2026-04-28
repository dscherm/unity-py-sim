using System.Collections.Generic;
using UnityEngine;
namespace SpaceInvaders
{
    [RequireComponent(typeof(SpriteRenderer))]
    public class Invader : MonoBehaviour
    {
    [SerializeField] private GameManager gameManager;
        public float animationTime = 1.0f;
        public int score = 10;
        public int animationFrame = 0;
        public float timer = 0.0f;
        public Color32[] animationSprites;
        public SpriteRenderer spriteRenderer;
         void Awake()
        {
        if (gameManager == null) gameManager = FindObjectOfType<GameManager>();
            spriteRenderer = GetComponent<SpriteRenderer>();
            if (spriteRenderer != null && animationSprites != null)
            {
                spriteRenderer.color = animationSprites[0];
            }
        }
         void Start()
        {
            /* pass */
        }
         void Update()
        {
            timer += Time.deltaTime;
            if (timer >= animationTime)
            {
                timer -= animationTime;
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
                // gameManager.OnInvaderKilled(this)
                if (gameManager != null)
                {
                    gameManager.OnInvaderKilled(this);
                }
            }
            // else if (other.gameObject.layer == LayerMask.NameToLayer("Boundary"))
            else if (other.gameObject.layer == Layers.BOUNDARY)
            {
                if (gameManager != null)
                {
                    gameManager.OnBoundaryReached();
                }
            }
        }
    }
}
