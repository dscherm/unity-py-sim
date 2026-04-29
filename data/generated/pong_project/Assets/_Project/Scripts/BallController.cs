using UnityEngine;
namespace Pong
{
    [RequireComponent(typeof(Rigidbody2D))]
    public class BallController : MonoBehaviour
    {
        public float initialSpeed = 6.0f;
        public float speedIncrease = 0.3f;
        public float currentSpeed = 6.0f;
        [SerializeField] private Rigidbody2D rb;
         void Start()
        {
            rb = GetComponent<Rigidbody2D>();
            currentSpeed = initialSpeed;
            Launch();
        }
        public void Launch()
        {
            var xDir = Random.value > 0.5f ? 1.0f : -1.0f;
            var yDir = Random.Range(-0.5f, 0.5f);
            Vector2 direction = new Vector2(xDir, yDir).normalized;
            rb.linearVelocity = direction * currentSpeed;
        }
        public void ResetState()
        {
            transform.position = Vector2.zero;
            rb.MovePosition(Vector2.zero);
            rb.linearVelocity = Vector2.zero;
            currentSpeed = initialSpeed;
        }
         void OnCollisionEnter2D(Collision2D collision)
        {
            if (collision.gameObject.tag == "Paddle")
            {
                currentSpeed += speedIncrease;
                // Reflect based on which side the paddle is on
                var paddleX = collision.gameObject.transform.position.x;
                var hitY = transform.position.y - collision.gameObject.transform.position.y;
                var normalizedHit = Mathf.Max(-1.0f, Mathf.Min(1.0f, hitY / 1.0f));
                // Ball goes away from the paddle it hit
                var xDir = paddleX < 0 ? 1.0f : -1.0f;
                Vector2 direction = new Vector2(xDir, normalizedHit).normalized;
                rb.linearVelocity = direction * currentSpeed;
            }
        }
    }
}
