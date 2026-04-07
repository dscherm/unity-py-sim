using UnityEngine;
[RequireComponent(typeof(Movement))]
[RequireComponent(typeof(SpriteRenderer))]
public class GhostEyes : MonoBehaviour
{
    public string upRef = "ghost_eyes_up";
    public string downRef = "ghost_eyes_down";
    public string leftRef = "ghost_eyes_left";
    public string rightRef = "ghost_eyes_right";
    public SpriteRenderer spriteRenderer;
    public Movement movement;
     void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        movement = gameObject.GetComponent<Movement>();
        if (movement == null && transform.parent != null)
        {
            var parentGo = transform.parent.gameObject;
            if (parentGo != null)
            {
                movement = parentGo.GetComponent<Movement>();
            }
        }
    }
     void Update()
    {
        if (spriteRenderer == null || movement == null)
        {
            return;
        }
        var d = movement.direction;
    }
}
