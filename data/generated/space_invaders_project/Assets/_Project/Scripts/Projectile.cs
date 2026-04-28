using UnityEngine;
namespace SpaceInvaders
{
    [RequireComponent(typeof(BoxCollider2D))]
    public class Projectile : MonoBehaviour
    {
        public Vector3 direction = new Vector3(0, 1, 0);
        public float speed = 20.0f;
        [SerializeField] private BoxCollider2D boxCollider;
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
         void OnTriggerEnter2D(Collider2D other)
        {
            CheckCollision(other.gameObject);
        }
         void OnTriggerStay2D(Collider2D other)
        {
            CheckCollision(other.gameObject);
        }
        public void CheckCollision(GameObject other)
        {
            Bunker bunker = other.GetComponent<Bunker>();
            if (bunker == null || bunker.CheckCollision(boxCollider, transform.position))
            {
                // Destroy(gameObject)
                gameObject.SetActive(false);
            }
        }
    }
}
