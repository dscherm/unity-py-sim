using UnityEngine;
[RequireComponent(typeof(Movement))]
[RequireComponent(typeof(SpriteRenderer))]
public class GhostEyes : MonoBehaviour
{
    public pygame.Surface spriteUp;
    public pygame.Surface spriteDown;
    public pygame.Surface spriteLeft;
    public pygame.Surface spriteRight;
    public SpriteRenderer SpriteRenderer;
    public Movement? Movement;
    public GameObject? ParentGo;
     void Awake()
    {
        SpriteRenderer = GetComponent<SpriteRenderer>();
        var parent = transform.parent;
        if (parent != null)
        {
            ParentGo = parent.gameObject;
            Movement = parent.gameObject.GetComponent<Movement>();
        }
    }
     void Update()
    {
        if (ParentGo != null && !ParentGo.activeSelf)
        {
            if (SpriteRenderer != null)
            {
                SpriteRenderer.enabled = false;
            }
            return;
        }
        else if (ParentGo != null && ParentGo.activeSelf)
        {
            if (SpriteRenderer != null && !SpriteRenderer.enabled)
            {
                SpriteRenderer.enabled = true;
            }
        }
        if (ParentGo != null)
        {
            transform.position.x = ParentGo.transform.position.x;
            transform.position.y = ParentGo.transform.position.y;
        }
        if (SpriteRenderer == null || Movement == null)
        {
            return;
        }
        var d = Movement.direction;
        if (d.y > 0)
        {
            SpriteRenderer.sprite = spriteUp;
        }
        else if (d.y < 0)
        {
            SpriteRenderer.sprite = spriteDown;
        }
        else if (d.x < 0)
        {
            SpriteRenderer.sprite = spriteLeft;
        }
        else if (d.x > 0)
        {
            SpriteRenderer.sprite = spriteRight;
        }
    }
}
