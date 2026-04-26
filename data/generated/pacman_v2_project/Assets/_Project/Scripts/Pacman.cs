using UnityEngine;
[RequireComponent(typeof(CircleCollider2D))]
[RequireComponent(typeof(Movement))]
[RequireComponent(typeof(SpriteRenderer))]
public class Pacman : MonoBehaviour
{
    [SerializeField] private AnimatedSprite deathSequence;
    public SpriteRenderer spriteRenderer;
    [SerializeField] private CircleCollider2D collider;
    public Movement movement;
     void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        collider = GetComponent<CircleCollider2D>();
        movement = GetComponent<Movement>();
    }
     void Update()
    {
        if (Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow))
        {
            movement.SetDirection(new Vector2(0, 1));
        }
        else if (Input.GetKeyDown(KeyCode.S) || Input.GetKeyDown(KeyCode.DownArrow))
        {
            movement.SetDirection(new Vector2(0, -1));
        }
        else if (Input.GetKeyDown(KeyCode.A) || Input.GetKeyDown(KeyCode.LeftArrow))
        {
            movement.SetDirection(new Vector2(-1, 0));
        }
        else if (Input.GetKeyDown(KeyCode.D) || Input.GetKeyDown(KeyCode.RightArrow))
        {
            movement.SetDirection(new Vector2(1, 0));
        }
        var direction = movement.direction;
        if (direction.x != 0 || direction.y != 0)
        {
            var angle = Mathf.Atan2(direction.y, direction.x);
            transform.rotation = Quaternion.Euler(0f, 0f, Mathf.Rad2Deg * (angle));
        }
    }
    public void ResetState()
    {
        enabled = true;
        if (spriteRenderer != null)
        {
            spriteRenderer.enabled = true;
        }
        if (collider != null)
        {
            collider.enabled = true;
        }
        if (movement != null)
        {
            movement.ResetState();
        }
        if (deathSequence != null)
        {
            deathSequence.enabled = false;
        }
        gameObject.SetActive(true);
    }
    public void DeathSequenceStart()
    {
        enabled = false;
        if (spriteRenderer != null)
        {
            spriteRenderer.enabled = false;
        }
        if (collider != null)
        {
            collider.enabled = false;
        }
        if (movement != null)
        {
            movement.enabled = false;
        }
        if (deathSequence != null)
        {
            deathSequence.enabled = true;
            deathSequence.Restart();
        }
    }
}
