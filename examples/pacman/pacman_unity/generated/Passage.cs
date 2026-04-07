using UnityEngine;
public class Passage : MonoBehaviour
{
    // TODO: populate _recent_teleports with game data
    private static readonly object[] _recent_teleports = new object[0];
    public Transform connection;
    public static Dictionary<int, float> _recent_teleports = null;
    public static float _TELEPORT_COOLDOWN = 0.5f;
     void OnTriggerEnter2D(Collider2D other)
    {
        var objId = id(other.gameObject);
        var now = Time.time;
        if (objId in recentTeleports)
        {
            if (now - recentTeleports[objId] < _TELEPORT_COOLDOWN)
            {
                return;
            }
        }
        recentTeleports[objId] = now;
        Vector2 position = new Vector2( connection.position.x, connection.position.y);
        other.transform.position = position;
        var rb = other.GetComponent<Rigidbody2D>();
        if (rb != null)
        {
            rb.MovePosition(position);
        }
    }
}
