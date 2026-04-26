using UnityEngine;
[RequireComponent(typeof(SpriteRenderer))]
public class Invader : MonoBehaviour
{
    [SerializeField] private tuple[] animationSprites = [];
    [SerializeField] private float animationTime = 1f;
    [SerializeField] private int score = 10;
    [SerializeField] private int animationFrame = 0;
    [SerializeField] private float Timer = 0f;
    private SpriteRenderer? spriteRenderer;
     void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        if (spriteRenderer && animationSprites)
        {
            spriteRenderer.color = animationSprites[0];
        }
    }
     void Start()
    {

    }
     void Update()
    {
        _timer += Time.deltaTime;
        if (_timer >= animationTime)
        {
            _timer -= animationTime;
            AnimateSprite();
        }
    }
    public void AnimateSprite()
    {
        animationFrame += 1;
        if (animationFrame >= animationSprites.Count)
        {
            animationFrame = 0;
        }
        if (spriteRenderer && animationSprites)
        {
            spriteRenderer.color = animationSprites[animationFrame];
        }
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        if (other.layer == LAYER_LASER)
        {
            // GameManager.Instance.OnInvaderKilled(this)
            if (GameManager.instance != null)
            {
                GameManager.instance.onInvaderKilled(this);
            }
        }
        // else if (other.gameObject.layer == LayerMask.NameToLayer("Boundary"))
        else if (other.layer == LAYER_BOUNDARY)
        {
            if (GameManager.instance != null)
            {
                GameManager.instance.onBoundaryReached();
            }
        }
    }
}
