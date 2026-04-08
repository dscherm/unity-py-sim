using UnityEngine;
[RequireComponent(typeof(CircleCollider2D))]
[RequireComponent(typeof(Movement))]
[RequireComponent(typeof(SpriteRenderer))]
public class Pacman : MonoBehaviour
{
    [SerializeField] private AnimatedSprite deathSequence;
    [SerializeField] private SpriteRenderer SpriteRenderer;
    [SerializeField] private CircleCollider2D Collider;
    [SerializeField] private Movement movement;
    public bool enabled;
     void Awake()
    {
        SpriteRenderer = GetComponent<SpriteRenderer>();
        Collider = GetComponent<CircleCollider2D>();
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
            transform.rotationZ = math.Degrees(angle);
        }
    }
    public void ResetState()
    {
        enabled = true;
        if (SpriteRenderer != null)
        {
            SpriteRenderer.enabled = true;
        }
        if (Collider != null)
        {
            Collider.enabled = true;
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
        if (SpriteRenderer != null)
        {
            SpriteRenderer.enabled = false;
        }
        if (Collider != null)
        {
            Collider.enabled = false;
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
