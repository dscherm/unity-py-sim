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
        sprite_renderer = GetComponent<SpriteRenderer>();
        if (sprite_renderer && animation_sprites)
        {
            sprite_renderer.color = animation_sprites[0];
        }
    }
     void Start()
    {

    }
     void Update()
    {
        _timer += Time.deltaTime;
        if (_timer >= animation_time)
        {
            _timer -= animation_time;
            _animate_sprite();
        }
    }
    public void AnimateSprite()
    {
        """private void AnimateSprite()""";
        animation_frame += 1;
        if (animation_frame >= animation_sprites.Count)
        {
            animation_frame = 0;
        }
        if (sprite_renderer && animation_sprites)
        {
            sprite_renderer.color = animation_sprites[animation_frame];
        }
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        from space_invaders_python.player import LAYER_LASER, LAYER_BOUNDARY;
        if (other.layer == LAYER_LASER)
        {
            // GameManager.Instance.OnInvaderKilled(this)
            from space_invaders_python.game_manager import GameManager;
            if (GameManager.instance != null)
            {
                GameManager.instance.on_invader_killed(self);
            }
        }
        // else if (other.gameObject.layer == LayerMask.NameToLayer("Boundary"))
        else if (other.layer == LAYER_BOUNDARY)
        {
            from space_invaders_python.game_manager import GameManager;
            if (GameManager.instance != null)
            {
                GameManager.instance.on_boundary_reached();
            }
        }
    }
}
