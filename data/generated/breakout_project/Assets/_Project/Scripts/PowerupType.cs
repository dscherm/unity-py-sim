using System.Collections;
using UnityEngine;
public enum PowerupType
{
    WidePaddle,
    ExtraLife,
    SpeedBall
}
public class PowerupConfig
{
    // TODO: populate POWERUP_CONFIGS with game data
    private static readonly object[] POWERUP_CONFIGS = new object[0];
    public PowerupType powerupType = PowerupType.WidePaddle;
    public Color32 color = new Color32(255, 255, 255, 255);
    public float weight = 0.0f;
}
public class Powerup : MonoBehaviour
{
    public float fallSpeed = 3.0f;
    [SerializeField] private PowerupType powerupType;
    public static PowerupConfig[] POWERUP_CONFIGS = new PowerupConfig[] { new PowerupConfig { color = new Color32(100, 200, 255, 255), weight = 0.4f }, new PowerupConfig { color = new Color32(255, 100, 200, 255), weight = 0.2f }, new PowerupConfig { color = new Color32(255, 200, 50, 255), weight = 0.4f } };
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
                    GameManager gm = GameManager.GetInstance();
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
        if (sr != null && sr.gameObject != null && sr.gameObject.activeSelf)
        {
            sr.size = originalSize;
            sr.color = originalColor;
        }
    }
    public IEnumerator RevertSpeed(BallController bc, float originalSpeed)
    {
        yield return new WaitForSeconds(8.0f);
        if (bc != null && bc.gameObject != null && bc.gameObject.activeSelf)
        {
            bc.speed = originalSpeed;
        }
    }
    public static Color32 GetColor(PowerupType ptype)
    {
        foreach (var cfg in POWERUP_CONFIGS)
        {
            if (cfg.powerupType == ptype)
            {
                return cfg.color;
            }
        }
        return new Color32(255, 255, 255, 255);
    }
    public static void MaybeSpawnPowerup(Vector2 position)
    {
        if (Random.value > 0.20f)
        {
            return;
        }
        float roll = Random.value;
        float cumulative = 0.0f;
        PowerupType chosen = PowerupType.WidePaddle;
        foreach (var cfg in POWERUP_CONFIGS)
        {
            cumulative += cfg.weight;
            if (roll <= cumulative)
            {
                chosen = cfg.powerupType;
                break;
            }
        }
        string name = $"Powerup_{Random.Range(1000, 9999)}";
        GameObject go = new GameObject(name); // TODO: wire via Inspector or Instantiate
        go.transform.position = new Vector2(position.x, position.y);
        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.color = GetColor(chosen);
        sr.size = new Vector2(0.6f, 0.3f);
        Powerup pu = go.AddComponent<Powerup>();
        pu.powerupType = chosen;
    }
}
