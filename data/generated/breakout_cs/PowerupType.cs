namespace breakout
{
    public enum PowerupType
    {
        WidePaddle,
        ExtraLife,
        SpeedBall
    }
    using UnityEngine;

    public class PowerupConfig
    {
        public static PowerupType powerupType = PowerupType.WIDE_PADDLE;
        public static (int, int, int) color = (255, 255, 255);
        public static float weight = 0f;
    }
    using UnityEngine;
    using System.Collections;
    public class Powerup : MonoBehaviour
    {
        public float fallSpeed = 3f;
        public PowerupType powerupType = PowerupType.WIDE_PADDLE;
         void Update()
        {
            Vector2 pos = transform.position;
            float newY = pos.y - fallSpeed * Time.deltaTime;
            transform.position = new Vector2(pos.x, newY);
            GameObject paddle = GameObject.Find("Paddle");
            if (paddle != null && paddle.active)
            {
                Vector2 pp = paddle.transform.position;
                if ((Mathf.Abs(pos.x - pp.x) < 1.2f && Mathf.Abs(newY - pp.y) < 0.5f))
                {
                    Apply(paddle);
                    gameObject.SetActive(false);
                    return;
                }
            }
            if (newY < -7)
            {
                gameObject.SetActive(false);
            }
        }
        public void Apply(GameObject paddle)
        {
            AudioSource audio = paddle.GetComponent<AudioSource>();
            if (audio != null)
            {
                audio.clipRef = "powerup_collect";
            }
            if (powerupType == PowerupType.EXTRA_LIFE)
            {
                GameManager.lives += 1;
                GameManager.UpdateDisplay();
            }
            else if (powerupType == PowerupType.WIDE_PADDLE)
            {
                SpriteRenderer sr = paddle.GetComponent<SpriteRenderer>();
                if (sr != null)
                {
                    Vector2 originalSize = new Vector2(sr.size.x, sr.size.y);
                    (int, int, int) originalColor = sr.color;
                    sr.size = new Vector2(3.0f, 0.4f);
                    sr.color = GetColor(PowerupType.WIDE_PADDLE);
                    // Revert after 10 seconds via coroutine
                    GameManager gm = GameManager.GetInstance();
                    if (gm != null)
                    {
                        gm.StartCoroutine(RevertPaddle(sr, originalSize, originalColor));
                    }
                }
            }
            else if (powerupType == PowerupType.SPEED_BALL)
            {
                GameObject ball = GameObject.Find("Ball");
                if (ball != null)
                {
                    BallController bc = ball.GetComponent<BallController>();
                    if (bc != null)
                    {
                        float originalSpeed = bc.speed;
                        bc.speed = Mathf.Min(bc.speed * 1.3f, bc.maxSpeed);
                        // Revert after 8 seconds via coroutine
                        gm = GameManager.GetInstance();
                        if (gm != null)
                        {
                            gm.StartCoroutine(RevertSpeed(bc, originalSpeed));
                        }
                    }
                }
            }
        }
        public IEnumerator RevertPaddle(SpriteRenderer sr, Vector2 originalSize, (int, int, int) originalColor)
        {
            yield return new WaitForSeconds(10.0f);
            if (sr != null && sr.gameObject && sr.gameObject.activeSelf)
            {
                sr.size = originalSize;
                sr.color = originalColor;
            }
        }
        public IEnumerator RevertSpeed(BallController bc, float originalSpeed)
        {
            yield return new WaitForSeconds(8.0f);
            if (bc != null && bc.gameObject && bc.gameObject.activeSelf)
            {
                bc.speed = originalSpeed;
            }
        }
    }
}
