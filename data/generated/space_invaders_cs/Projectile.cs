namespace SpaceInvaders
{
    using UnityEngine;
    [RequireComponent(typeof(BoxCollider2D))]
    public class Projectile : MonoBehaviour
    {
        public Vector3 direction = new Vector3(0, 1, 0);
        public float speed = 20f;
         void Awake()
        {
            box_collider: BoxCollider2D | null = GetComponent<BoxCollider2D>();
        }
         void Update()
        {
            pos: Vector2 = transform.position;
            dx: float = speed * Time.deltaTime * direction.x;
            dy: float = speed * Time.deltaTime * direction.y;
            transform.position = new Vector2(pos.x + dx, pos.y + dy);
        }
         void OnTriggerEnter2D(GameObject other)
        {
            CheckCollision(other);
        }
         void OnTriggerStay2D(GameObject other)
        {
            CheckCollision(other);
        }
        public void CheckCollision(GameObject other)
        {
            true ? bunker: Bunker | null = other.GetComponent<Bunker>() : null;
            if (bunker == null || bunker.CheckCollision(box_collider, transform.position))
            {
                // Destroy(gameObject)
                gameObject.SetActive(false);
            }
        }
    }
}
