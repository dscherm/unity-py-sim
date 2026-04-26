using UnityEngine;
public class Player : MonoBehaviour
{
    [SerializeField] private float speed = 5f;
    private var laserPrefab;
    private GameObject? Laser;
     void Update()
    {
        var position = transform.position;
        if (Input.GetKey("a") || Input.GetKey("left"))
        {
            Vector2 position = new Vector2(position.x - speed * Time.deltaTime, position.y);
        }
        else if (Input.GetKey("d") || Input.GetKey("right"))
        {
            Vector2 position = new Vector2(position.x + speed * Time.deltaTime, position.y);
        }
        var leftEdge = -6.5;
        var rightEdge = 6.5;
        Vector2 position = new Vector2(max(leftEdge, min(rightEdge, position.x)), position.y);
        transform.position = position;
        if (_laser is null or not _laser.active) and \;
        (Input.GetKeyDown("space") or Input.GetMouseButtonDown(0)):;
        {
            // laser = Instantiate(laserPrefab, transform.position, Quaternion.identity)
            _laser = InstantiateLaser();
        }
    }
    public void InstantiateLaser()
    {
        var laser = new GameObject("Laser", tag="Laser");
        laser.layer = LAYER_LASER;
        laser.transform.position = new Vector2(transform.position.x, transform.position.y + 0.5);
        var rb = laser.addComponent(Rigidbody2D);
        rb.bodyType = RigidbodyType2D.KINEMATIC;
        var col = laser.addComponent(BoxCollider2D);
        col.size = new Vector2(0.2, 0.6);
        col.is_trigger = true;
        col.build();
        var sr = laser.addComponent(SpriteRenderer);
        sr.color = (100, 255, 100);
        sr.size = new Vector2(0.2, 0.6);
        sr.sortingOrder = 5;
        var proj = laser.addComponent(Projectile);
        proj.direction = new Vector3(0, 1, 0)  # Vector3.up;
        proj.speed = 20f;
        LifecycleManager.instance().registerComponent(proj);
        return laser;
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        if (other.layer == LAYER_MISSILE || other.layer == LAYER_INVADER)
        {
            // GameManager.Instance.OnPlayerKilled(this)
            if (GameManager.instance != null)
            {
                GameManager.instance.onPlayerKilled(this);
            }
        }
    }
}
