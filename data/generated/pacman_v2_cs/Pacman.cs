using UnityEngine.InputSystem;
using UnityEngine;
[RequireComponent(typeof(CircleCollider2D))]
[RequireComponent(typeof(Movement))]
[RequireComponent(typeof(SpriteRenderer))]
public class Pacman : MonoBehaviour
{
    public AnimatedSprite deathSequence;
    public SpriteRenderer SpriteRenderer;
    public CircleCollider2D Collider;
    public Movement movement;
    public bool enabled;
     void Awake()
    {
        SpriteRenderer = GetComponent<SpriteRenderer>();
        Collider = GetComponent<CircleCollider2D>();
        movement = GetComponent<Movement>();
    }
     void Update()
    {
        if (Keyboard.current.wKey.wasPressedThisFrame || Keyboard.current.upArrowKey.wasPressedThisFrame)
        {
            movement.SetDirection(new Vector2(0, 1));
        }
        else if (Keyboard.current.sKey.wasPressedThisFrame || Keyboard.current.downArrowKey.wasPressedThisFrame)
        {
            movement.SetDirection(new Vector2(0, -1));
        }
        else if (Keyboard.current.aKey.wasPressedThisFrame || Keyboard.current.leftArrowKey.wasPressedThisFrame)
        {
            movement.SetDirection(new Vector2(-1, 0));
        }
        else if (Keyboard.current.dKey.wasPressedThisFrame || Keyboard.current.rightArrowKey.wasPressedThisFrame)
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
