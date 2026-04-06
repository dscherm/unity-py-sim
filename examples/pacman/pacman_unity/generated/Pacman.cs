using UnityEngine;
[RequireComponent(typeof(CircleCollider2D))]
[RequireComponent(typeof(Movement))]
[RequireComponent(typeof(SpriteRenderer))]
public class Pacman : MonoBehaviour
{
    public bool enabled;
    public static AnimatedSprite deathSequence = null;
    public static SpriteRenderer spriteRenderer = null;
    public static CircleCollider2D circleCollider = null;
    public static Movement movement = null;
     void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        circleCollider = GetComponent<CircleCollider2D>();
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
        if (movement.direction.x != 0 || movement.direction.y != 0)
        {
            var angle = Mathf.Atan2(movement.direction.y, movement.direction.x);
            var angleDeg = math.Degrees(angle);
            transform.rotation = Quaternion.Euler(0, 0, angleDeg);
        }
    }
    public void ResetState()
    {
        enabled = true;
        if (spriteRenderer != null)
        {
            spriteRenderer.enabled = true;
        }
        if (circleCollider != null)
        {
            circleCollider.enabled = true;
        }
        if (deathSequence != null)
        {
            deathSequence.enabled = false;
        }
        if (movement != null)
        {
            movement.ResetState();
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
        if (circleCollider != null)
        {
            circleCollider.enabled = false;
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
