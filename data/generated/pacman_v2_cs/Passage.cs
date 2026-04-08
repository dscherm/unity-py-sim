using UnityEngine;
public class Passage : MonoBehaviour
{
    public GameObject connection;
    public static Dictionary<int, float> _recent_teleports = null;
    public static float _TELEPORT_COOLDOWN = 0.5f;
     void OnTriggerEnter2D(Collider2D other)
    {
        if (connection == null)
        {
            return;
        }
        var otherGo = getattr(other.gameObject, "gameObject", other.gameObject);
        var objId = id(otherGo);
        var now = Time.time;
        if (recentTeleports.ContainsKey(objId))
        {
            if (now - recentTeleports[objId] < _TELEPORT_COOLDOWN)
            {
                return;
            }
        }
        recentTeleports[objId] = now;
        var connPos = connection.transform.position;
        Vector2 newPos = new Vector2(connPos.x, connPos.y);
        otherGo.transform.position = newPos;
        var rb = otherGo.GetComponent<Rigidbody2D>();
        if (rb != null)
        {
            rb.MovePosition(newPos);
        }
    }
}
