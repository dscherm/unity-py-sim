using UnityEngine;
[RequireComponent(typeof(BoxCollider2D))]
public class Projectile : MonoBehaviour
{
    [SerializeField] private Vector3 direction = Vector3(0, 1, 0);
    [SerializeField] private float speed = 20f;
     void Awake()
    {
        box_collider = GetComponent<BoxCollider2D>();
    }
     void Update()
    {
        var pos = transform.position;
        var dx = speed * Time.deltaTime * direction.x;
        var dy = speed * Time.deltaTime * direction.y;
        transform.position = new Vector2(pos.x + dx, pos.y + dy);
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        _check_collision(other);
    }
     void OnTriggerStay2D(Collider2D other)
    {
        _check_collision(other);
    }
    public void CheckCollision(Collider2D other)
    {
        from space_invaders_python.bunker import Bunker;
        var bunker = other.get_component(Bunker) if hasattr(other, "get_component") else null;
        if (bunker == null || bunker.check_collision(box_collider, transform.position))
        {
            // Destroy(gameObject)
            game_object.active = false;
        }
    }
}
