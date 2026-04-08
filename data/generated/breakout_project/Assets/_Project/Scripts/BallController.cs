using System;
using UnityEngine;
[RequireComponent(typeof(Rigidbody2D))]
public class BallController : MonoBehaviour
{
    public float speed = 6.0f;
    public float maxSpeed = 12.0f;
    public bool attached = true;
    public Vector2 paddleOffset = new Vector2(0, 0.6f);
    public bool showTrajectory = true;
    [SerializeField] private Rigidbody2D rb;
    [SerializeField] private GameObject paddle;
     void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        paddle = GameObject.Find("Paddle");
    }
     void Update()
    {
        if (attached)
        {
            // Follow paddle
            if (paddle != null)
            {
                Vector2 paddlePos = paddle.transform.position;
                transform.position = new Vector2( paddlePos.x + paddleOffset.x, paddlePos.y + paddleOffset.y);
                rb.MovePosition(transform.position);
            }
            // Launch on space
            if (Input.GetKeyDown(KeyCode.Space))
            {
                Launch();
            }
            return;
        }
        Vector2 pos = transform.position;
        Vector2 vel = rb.velocity;
        if (pos.x < -7.5f && vel.x < 0)
        {
            rb.velocity = new Vector2(-vel.x, vel.y);
            transform.position = new Vector2(-7.5f, pos.y);
        }
        else if (pos.x > 7.5f && vel.x > 0)
        {
            rb.velocity = new Vector2(-vel.x, vel.y);
            transform.position = new Vector2(7.5f, pos.y);
        }
        if (pos.y > 5.5f && vel.y > 0)
        {
            rb.velocity = new Vector2(vel.x, -vel.y);
            transform.position = new Vector2(pos.x, 5.5f);
        }
        if (pos.y < -6.0f)
        {
            GameManager.OnBallLost();
            ResetState();
            return;
        }
        if (showTrajectory && !attached)
        {
            vel = rb.velocity;
            if (vel.sqrMagnitude > 0.01f)
            {
                Vector2 Start = transform.position;
                Vector2 end = new Vector2(Start.x + vel.x * 0.3f, Start.y + vel.y * 0.3f);
                Debug.DrawLine(Start, end, new Color32(255, 255, 0, 255), 0f);
            }
        }
    }
     void OnCollisionEnter2D(Collision2D collision)
    {
        AudioSource audio = GetComponent<AudioSource>();
        if (collision.gameObject.tag == "Paddle")
        {
            // Angle based on hit position
            Vector2 paddlePos = collision.gameObject.transform.position;
            float hitX = transform.position.x - paddlePos.x;
            // Normalize to -1..1 based on paddle width (~2 units)
            float normalized = Mathf.Max(-1.0f, Mathf.Min(1.0f, hitX / 1.0f));
            // Angle between 30 and 150 degrees (always upward)
            float angle = Mathf.PI * (0.25f + 0.5f * (1.0f - (normalized + 1.0f) / 2.0f));
            Vector2 direction = new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)).normalized;
            rb.velocity = direction * speed;
        }
        else if (collision.gameObject.tag == "Brick")
        {
            // Reflect off brick
            Vector2 vel = rb.velocity;
            // Simple: reflect Y
            rb.velocity = new Vector2(vel.x, -vel.y);
        }
    }
    public void Launch()
    {
        attached = false;
        float angle = Mathf.PI / 2 + Random.Range(-0.3f, 0.3f);
        Vector2 direction = new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)).normalized;
        rb.velocity = direction * speed;
    }
    public void ResetState()
    {
        attached = true;
        rb.velocity = Vector2.zero;
        if (paddle != null)
        {
            Vector2 paddlePos = paddle.transform.position;
            transform.position = new Vector2( paddlePos.x + paddleOffset.x, paddlePos.y + paddleOffset.y);
            rb.MovePosition(transform.position);
        }
    }
}
