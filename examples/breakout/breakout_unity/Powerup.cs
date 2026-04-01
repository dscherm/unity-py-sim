using UnityEngine;

public enum PowerupType
{
    WidePaddle,
    ExtraLife,
    SpeedBall
}

public class Powerup : MonoBehaviour
{
    [SerializeField] private float fallSpeed = 3f;
    [SerializeField] private PowerupType powerupType = PowerupType.WidePaddle;

    private static readonly Color[] PowerupColors = {
        new Color(0.39f, 0.78f, 1f),    // wide paddle — light blue
        new Color(1f, 0.39f, 0.78f),     // extra life — pink
        new Color(1f, 0.78f, 0.20f),     // speed ball — gold
    };

    void Update()
    {
        transform.position += Vector3.down * fallSpeed * Time.deltaTime;

        // Check paddle collision
        GameObject paddle = GameObject.Find("Paddle");
        if (paddle != null)
        {
            Vector2 pos = transform.position;
            Vector2 pp = paddle.transform.position;
            if (Mathf.Abs(pos.x - pp.x) < 1.2f && Mathf.Abs(pos.y - pp.y) < 0.5f)
            {
                Apply(paddle);
                Destroy(gameObject);
                return;
            }
        }

        // Off screen
        if (transform.position.y < -7f)
        {
            Destroy(gameObject);
        }
    }

    private void Apply(GameObject paddle)
    {
        switch (powerupType)
        {
            case PowerupType.ExtraLife:
                GameManager.Lives++;
                break;

            case PowerupType.WidePaddle:
                var sr = paddle.GetComponent<SpriteRenderer>();
                if (sr != null)
                {
                    sr.size = new Vector2(3f, 0.4f);
                    sr.color = PowerupColors[(int)PowerupType.WidePaddle];
                }
                break;

            case PowerupType.SpeedBall:
                var ball = GameObject.Find("Ball");
                if (ball != null)
                {
                    var bc = ball.GetComponent<BallController>();
                    if (bc != null)
                    {
                        bc.speed = Mathf.Min(bc.speed * 1.3f, bc.maxSpeed);
                    }
                }
                break;
        }
    }

    public static void MaybeSpawn(Vector2 position)
    {
        if (Random.value > 0.20f) return;

        // Pick random type
        PowerupType type = (PowerupType)Random.Range(0, 3);

        GameObject go = new GameObject("Powerup");
        go.transform.position = position;

        var sr = go.AddComponent<SpriteRenderer>();
        sr.color = PowerupColors[(int)type];
        sr.size = new Vector2(0.6f, 0.3f);

        var pu = go.AddComponent<Powerup>();
        pu.powerupType = type;
    }
}
