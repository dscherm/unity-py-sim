namespace SpaceInvaders
{
    using UnityEngine;
    [RequireComponent(typeof(BoxCollider2D))]
    public class Projectile : MonoBehaviour
    {
        public Vector3 direction = new Vector3(0, 1, 0);
        public float speed = 20f;
        public BoxCollider2D boxCollider;
         void Awake()
        {
            boxCollider = GetComponent<BoxCollider2D>();
        }
         void Update()
        {
            Vector2 pos = transform.position;
            float dx = speed * Time.deltaTime * direction.x;
            float dy = speed * Time.deltaTime * direction.y;
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
            Bunker bunker = true ? other.GetComponent<Bunker>() : null;
            if (bunker == null || bunker.CheckCollision(boxCollider, transform.position))
            {
                // Destroy(gameObject)
                gameObject.SetActive(false);
            }
        }
    }
}
