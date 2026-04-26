using UnityEngine;
namespace PacmanV2
{
    [RequireComponent(typeof(Movement))]
    [RequireComponent(typeof(SpriteRenderer))]
    public class GhostEyes : MonoBehaviour
    {
        public Sprite spriteUp;
        public Sprite spriteDown;
        public Sprite spriteLeft;
        public Sprite spriteRight;
        public SpriteRenderer spriteRenderer;
        [SerializeField] private Movement movement;
        [SerializeField] private GameObject parentGo;
         void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            var parent = transform.parent;
            if (parent != null)
            {
                parentGo = parent.gameObject;
                movement = parent.gameObject.GetComponent<Movement>();
            }
        }
         void Update()
        {
            if (parentGo != null && !parentGo.activeSelf)
            {
                if (spriteRenderer != null)
                {
                    spriteRenderer.enabled = false;
                }
                return;
            }
            else if (parentGo != null && parentGo.activeSelf)
            {
                if (spriteRenderer != null && !spriteRenderer.enabled)
                {
                    spriteRenderer.enabled = true;
                }
            }
            if (parentGo != null)
            {
                transform.position = new Vector3(parentGo.transform.position.x, transform.position.y, transform.position.z);
                transform.position = new Vector3(transform.position.x, parentGo.transform.position.y, transform.position.z);
            }
            if (spriteRenderer == null || movement == null)
            {
                return;
            }
            var d = movement.direction;
            if (d.y > 0)
            {
                spriteRenderer.sprite = spriteUp;
            }
            else if (d.y < 0)
            {
                spriteRenderer.sprite = spriteDown;
            }
            else if (d.x < 0)
            {
                spriteRenderer.sprite = spriteLeft;
            }
            else if (d.x > 0)
            {
                spriteRenderer.sprite = spriteRight;
            }
        }
    }
}
