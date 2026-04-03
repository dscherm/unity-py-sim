using UnityEngine;
public class Invaders : MonoBehaviour
{
    [SerializeField] private float speedCurveMax = 5f;
    [SerializeField] private Vector3 direction = Vector3(1, 0, 0);
    [SerializeField] private Vector3 initialPosition = Vector3(0, 0, 0);
    [SerializeField] private int rows = 5;
    [SerializeField] private int columns = 11;
    [SerializeField] private float missileSpawnRate = 1f;
    [SerializeField] private float MissileTimer = 0f;
    [SerializeField] private GameObject[] InvaderChildren = [];
     void Awake()
    {
        initialPosition = new Vector3(;
        {
            transform.position.x,;
            transform.position.y,;
            0,;
        }
        );
        CreateInvaderGrid();
    }
    public void CreateInvaderGrid()
    {
        var lm = LifecycleManager.instance();
        for (int i = 0; i < rows; i++)
        {
            var width = 2f * (columns - 1);
            var height = 2f * (rows - 1);
            // Vector2 centerOffset = new Vector2(-width * 0.5f, -height * 0.5f)
            Vector2 center_offset = new Vector2(-width * 0.5, -height * 0.5);
            // Vector3 rowPosition = new Vector3(centerOffset.x, (2f * i) + centerOffset.y, 0f)
            Vector3 row_position = new Vector3(center_offset.x, (2f * i) + center_offset.y, 0);
            var config = ROW_CONFIG[i % ROW_CONFIG.Count];
            for (int j = 0; j < columns; j++)
            {
                // Invader invader = Instantiate(prefabs[i], transform)
                var invader_go = new GameObject(f"Invader_{i}_{j}", tag="Invader");
                invader_go.layer = 10  # LAYER_INVADER;
                var rb = invader_go.addComponent(Rigidbody2D);
                rb.bodyType = RigidbodyType2D.KINEMATIC;
                var col = invader_go.addComponent(BoxCollider2D);
                col.size = new Vector2(1.5, 1.5);
                col.is_trigger = true;
                col.build();
                var sr = invader_go.addComponent(SpriteRenderer);
                sr.color = config["animationSprites"][0];
                sr.size = new Vector2(1.5, 1f);
                sr.sortingOrder = 2;
                var inv = invader_go.addComponent(Invader);
                inv.score = config["score"];
                inv.animationSprites = config["animationSprites"];
                lm.registerComponent(inv);
                // Vector3 position = rowPosition; position.x += 2f * j
                Vector3 position = new Vector3(row_position.x + 2f * j, row_position.y, 0);
                // invader.transform.localPosition = position
                invader_go.transform.position = new Vector2(transform.position.x + position.x, transform.position.y + position.y);
                _invaderChildren.Add(invader_go);
            }
        }
    }
     void Start()
    {

    }
    public void MissileAttack()
    {
        var amountAlive = getAliveCount();
        if (amountAlive == 0)
        {
            return;
        }
        foreach (var invaderGo in _invaderChildren)
        {
            // if (!invader.gameObject.activeInHierarchy) continue
            if (!invader_go.active)
            {
                continue;
            }
            // if (Random.value < (1f / amountAlive))
            if (Random.value < (1f / amountAlive))
            {
                // Instantiate(missilePrefab, invader.position, Quaternion.identity)
                InstantiateMissile(invader_go.transform.position);
                break;
            }
        }
    }
    public void InstantiateMissile(object position)
    {
        var missile = new GameObject("Missile", tag="Missile");
        missile.layer = LAYER_MISSILE;
        missile.transform.position = new Vector2(position.x, position.y - 0.5);
        var rb = missile.addComponent(Rigidbody2D);
        rb.bodyType = RigidbodyType2D.KINEMATIC;
        var col = missile.addComponent(BoxCollider2D);
        col.size = new Vector2(0.2, 0.6);
        col.is_trigger = true;
        col.build();
        var sr = missile.addComponent(SpriteRenderer);
        sr.color = (255, 80, 80);
        sr.size = new Vector2(0.2, 0.6);
        sr.sortingOrder = 5;
        var proj = missile.addComponent(Projectile);
        proj.direction = new Vector3(0, -1, 0)  # Vector3.down;
        proj.speed = 10f;
        LifecycleManager.instance().registerComponent(proj);
    }
     void Update()
    {
        var totalCount = rows * columns;
        var amountAlive = getAliveCount();
        var amountKilled = totalCount - amountAlive;
        var percentKilled = amountKilled / float(totalCount) if totalCount > 0 else 0;
        var speed = 1f + percentKilled * (speedCurveMax - 1f);
        var pos = transform.position;
        var dx = speed * Time.deltaTime * direction.x;
        transform.position = new Vector2(pos.x + dx, pos.y);
        foreach (var invaderGo in _invaderChildren)
        {
            if (invader_go.active)
            {
                var inv_pos = invader_go.transform.position;
                invader_go.transform.position = new Vector2(inv_pos.x + dx, inv_pos.y);
            }
        }
        var leftEdge = -6.5;
        var rightEdge = 6.5;
        foreach (var invaderGo in _invaderChildren)
        {
            if (!invader_go.active)
            {
                continue;
            }
            // if (direction == Vector3.right && invader.position.x >= (rightEdge.x - 1f))
            if (direction.x > 0 && invader_go.transform.position.x >= (rightEdge - 1f))
            {
                AdvanceRow();
                break;
            }
            else if (direction.x < 0 && invader_go.transform.position.x <= (leftEdge + 1f))
            {
                AdvanceRow();
                break;
            }
        }
        _missileTimer += Time.deltaTime;
        if (_missileTimer >= missileSpawnRate)
        {
            _missileTimer -= missileSpawnRate;
            MissileAttack();
        }
    }
    public void AdvanceRow()
    {
        direction = new Vector3(-direction.x, 0, 0);
        var pos = transform.position;
        transform.position = new Vector2(pos.x, pos.y - 1f);
        foreach (var invaderGo in _invaderChildren)
        {
            if (invader_go.active)
            {
                var inv_pos = invader_go.transform.position;
                invader_go.transform.position = new Vector2(inv_pos.x, inv_pos.y - 1f);
            }
        }
    }
    public void ResetInvaders()
    {
        direction = new Vector3(1, 0, 0)  # Vector3.right;
        transform.position = new Vector2(initialPosition.x, initialPosition.y);
        // TODO: translate for loop: for idx, invader_go in enumerate(this._invaderChildren):
        {
            var row = idx // columns;
            var col = idx % columns;
            var width = 2f * (columns - 1);
            var height = 2f * (rows - 1);
            var x = -width * 0.5 + 2f * col;
            var y = -height * 0.5 + 2f * row;
            invader_go.transform.position = new Vector2(initialPosition.x + x, initialPosition.y + y);
            // invader.gameObject.SetActive(true)
            invader_go.active = true;
        }
    }
    public void GetAliveCount()
    {
        var count = 0;
        foreach (var invaderGo in _invaderChildren)
        {
            if (invader_go.active)
            {
                count += 1;
            }
        }
        return count;
    }
}
