namespace Breakout
{
    using UnityEngine;
    using UnityEngine.InputSystem;
    [RequireComponent(typeof(Rigidbody2D))]
    public class BallController : MonoBehaviour
    {
        public float speed = 6f;
        public float maxSpeed = 12f;
        public bool attached = true;
        public Vector2 paddleOffset = new Vector2(0, 0.6);
        public bool showTrajectory = true;
         void Start()
        {
            rb: Rigidbody2D = GetComponent<Rigidbody2D>();
            rb.SyncFromTransform();
            paddle: GameObject | null = GameObject.Find("Paddle");
        }
         void Update()
        {
            if (attached != null)
            {
                // Follow paddle
                if (paddle != null)
                {
                    paddle_pos: Vector2 = paddle.transform.position;
                    transform.position = new Vector2( paddle_pos.x + paddleOffset.x, paddle_pos.y + paddleOffset.y);
                    rb.MovePosition(transform.position);
                }
                // Launch on space
                if (Keyboard.current.spaceKey.wasPressedThisFrame)
                {
                    Launch();
                }
                return;
            }
            pos: Vector2 = transform.position;
            vel: Vector2 = rb.linearVelocity;
            if (pos.x < -7.5f && vel.x < 0)
            {
                rb.linearVelocity = new Vector2(-vel.x, vel.y);
                transform.position = new Vector2(-7.5f, pos.y);
            }
            else if (pos.x > 7.5f && vel.x > 0)
            {
                rb.linearVelocity = new Vector2(-vel.x, vel.y);
                transform.position = new Vector2(7.5f, pos.y);
            }
            if (pos.y > 5.5f && vel.y > 0)
            {
                rb.linearVelocity = new Vector2(vel.x, -vel.y);
                transform.position = new Vector2(pos.x, 5.5f);
            }
            if (pos.y < -6.0f)
            {
                GameManager.OnBallLost();
                Reset();
                return;
            }
            if (showTrajectory != null && !attached)
            {
                var vel = rb.linearVelocity;
                if (vel.sqrMagnitude > 0.01f)
                {
                    Start: Vector2 = transform.position;
                    end: Vector2 = new Vector2(Start.x + vel.x * 0.3f, Start.y + vel.y * 0.3f);
                    Debug.DrawLine(Start, end, color=(255, 255, 0), duration=0);
                }
            }
        }
         void OnCollisionEnter2D(Collision2D collision)
        {
            audio: AudioSource | null = GetComponent<AudioSource>();
            if (collision.gameObject.tag == "Paddle")
            {
                if (audio != null)
                {
                    audio.clipRef = "paddle_hit";
                }
                // Angle based on hit position
                paddle_pos: Vector2 = collision.gameObject.transform.position;
                hit_x: float = transform.position.x - paddle_pos.x;
                // Normalize to -1..1 based on paddle width (~2 units)
                normalized: float = Mathf.Max(-1.0f, Mathf.Min(1.0f, hit_x / 1.0f));
                // Angle between 30 and 150 degrees (always upward)
                angle: float = math.pi * (0.25f + 0.5f * (1.0f - (normalized + 1.0f) / 2.0f));
                direction: Vector2 = new Vector2(math.Cos(angle), math.Sin(angle)).normalized;
                rb.linearVelocity = direction * speed;
            }
            else if (collision.gameObject.tag == "Brick")
            {
                if (audio != null)
                {
                    audio.clipRef = "brick_hit";
                }
                // Reflect off brick
                vel: Vector2 = rb.linearVelocity;
                // Simple: reflect Y
                rb.linearVelocity = new Vector2(vel.x, -vel.y);
            }
        }
        public void Launch()
        {
            attached = false;
            angle: float = math.pi / 2 + Random.Range(-0.3f, 0.3f);
            direction: Vector2 = new Vector2(math.Cos(angle), math.Sin(angle)).normalized;
            rb.linearVelocity = direction * speed;
        }
        public void Reset()
        {
            attached = true;
            rb.linearVelocity = Vector2.zero;
            if (paddle != null)
            {
                paddle_pos: Vector2 = paddle.transform.position;
                transform.position = new Vector2( paddle_pos.x + paddleOffset.x, paddle_pos.y + paddleOffset.y);
                rb.MovePosition(transform.position);
            }
        }
    }
}
