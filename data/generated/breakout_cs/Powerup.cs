using System.Collections;
using UnityEngine;
namespace Breakout
{
    public enum PowerupType
    {
        WidePaddle,
        ExtraLife,
        SpeedBall
    }
    public class PowerupConfig
    {
        public static PowerupType powerupType = PowerupType.WidePaddle;
        public static Color32 color = new Color32(255, 255, 255, 255);
        public static float weight = 0f;
    }
    public class Powerup : MonoBehaviour
    {
        public float fallSpeed = 3f;
        public PowerupType powerupType = PowerupType.WidePaddle;
         void Update()
        {
            Vector2 pos = transform.position;
            float newY = pos.y - fallSpeed * Time.deltaTime;
            transform.position = new Vector2(pos.x, newY);
            GameObject paddle = GameObject.Find("Paddle");
            if (paddle != null && paddle.activeSelf)
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
            if (powerupType == PowerupType.ExtraLife)
            {
                GameManager.lives += 1;
                GameManager.UpdateDisplay();
            }
            else if (powerupType == PowerupType.WidePaddle)
            {
                SpriteRenderer sr = paddle.GetComponent<SpriteRenderer>();
                if (sr != null)
                {
                    Vector2 originalSize = new Vector2(sr.size.x, sr.size.y);
                    Color32 originalColor = sr.color;
                    sr.size = new Vector2(3.0f, 0.4f);
                    sr.color = GetColor(PowerupType.WidePaddle);
                    // Revert after 10 seconds via coroutine
                    GameManager gm = GameManager.GetInstance();
                    if (gm != null)
                    {
                        gm.StartCoroutine(RevertPaddle(sr, originalSize, originalColor));
                    }
                }
            }
            else if (powerupType == PowerupType.SpeedBall)
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
        public IEnumerator RevertPaddle(SpriteRenderer sr, Vector2 originalSize, Color32 originalColor)
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
