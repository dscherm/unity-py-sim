using UnityEngine;

public class BallController : MonoBehaviour
{
    [SerializeField] private float speed = 6f;
    [SerializeField] private float maxSpeed = 12f;

    private Rigidbody2D rb;
    private Transform paddle;
    private bool attached = true;
    private Vector2 paddleOffset = new Vector2(0, 0.6f);

    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        paddle = GameObject.Find("Paddle").transform;
    }

    void Update()
    {
        if (attached)
        {
            if (paddle != null)
            {
                Vector2 paddlePos = paddle.position;
                transform.position = paddlePos + paddleOffset;
            }

            if (Input.GetKeyDown(KeyCode.Space))
            {
                Launch();
            }
            return;
        }

        // Ball lost
        if (transform.position.y < -6f)
        {
            GameManager.OnBallLost();
            Reset();
        }
    }

    void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Paddle"))
        {
            float hitX = transform.position.x - collision.transform.position.x;
            float normalized = Mathf.Clamp(hitX / 1f, -1f, 1f);
            float angle = Mathf.PI * (0.25f + 0.5f * (1f - (normalized + 1f) / 2f));
            Vector2 direction = new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)).normalized;
            rb.linearVelocity = direction * speed;
        }
        else if (collision.gameObject.CompareTag("Brick"))
        {
            Vector2 vel = rb.linearVelocity;
            rb.linearVelocity = new Vector2(vel.x, -vel.y);
        }
    }

    public void Launch()
    {
        attached = false;
        float angle = Mathf.PI / 2f + Random.Range(-0.3f, 0.3f);
        Vector2 direction = new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)).normalized;
        rb.linearVelocity = direction * speed;
    }

    public void Reset()
    {
        attached = true;
        rb.linearVelocity = Vector2.zero;
        if (paddle != null)
        {
            transform.position = (Vector2)paddle.position + paddleOffset;
        }
    }
}
