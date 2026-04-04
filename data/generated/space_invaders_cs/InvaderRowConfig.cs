namespace SpaceInvaders
{
    using UnityEngine;

    public class InvaderRowConfig
    {
        public static (int, int, int)[] animationSprites = field(default_factory=list);
        public static int score = 10;
    }
    using UnityEngine;
    using System.Collections.Generic;
    public class Invaders : MonoBehaviour
    {
        public float speedCurveMax = 5f;
        public Vector3 direction = new Vector3(1, 0, 0);
        public Vector3 initialPosition = new Vector3(0, 0, 0);
        public int rows = 5;
        public int columns = 11;
        public float missileSpawnRate = 1f;
        public float MissileTimer = 0f;
        public List<GameObject> InvaderChildren;
        public static InvaderRowConfig[] ROWConfig = [InvaderRowConfig(animation_sprites=[(50, 255, 50), (30, 200, 30)], score=10), InvaderRowConfig(animation_sprites=[(50, 255, 50), (30, 200, 30)], score=10), InvaderRowConfig(animation_sprites=[(50, 200, 255), (30, 150, 200)], score=20), InvaderRowConfig(animation_sprites=[(50, 200, 255), (30, 150, 200)], score=20), InvaderRowConfig(animation_sprites=[(255, 100, 100), (200, 60, 60)], score=30)];
         void Awake()
        {
            initialPosition = new Vector3( transform.position.x, transform.position.y, 0);
            CreateInvaderGrid();
        }
        public void CreateInvaderGrid()
        {
            for (int i = 0; i < rows; i++)
            {
                width: float = 2.0f * (columns - 1);
                height: float = 2.0f * (rows - 1);
                // Vector2 centerOffset = new Vector2(-width * 0.5f, -height * 0.5f)
                center_offset: Vector2 = new Vector2(-width * 0.5f, -height * 0.5f);
                // Vector3 rowPosition = new Vector3(centerOffset.x, (2f * i) + centerOffset.y, 0f)
                row_position: Vector3 = new Vector3(center_offset.x, (2.0f * i) + center_offset.y, 0);
                // TODO: config: InvaderRowConfig = Invaders.ROW_CONFIG[i % Invaders.ROW_CONFIG.Count];
                for (int j = 0; j < columns; j++)
                {
                    // Invader invader = Instantiate(prefabs[i], transform)
                    invader_go: GameObject = new GameObject($"Invader_{i}_{j}");
                    invader_go.layer = Layers.INVADER;
                    rb: Rigidbody2D = invader_go.AddComponent<Rigidbody2D>();
                    rb.bodyType = RigidbodyType2D.Kinematic;
                    col: BoxCollider2D = invader_go.AddComponent<BoxCollider2D>();
                    col.size = new Vector2(1.5f, 1.5f);
                    col.isTrigger = true;
                    sr: SpriteRenderer = invader_go.AddComponent<SpriteRenderer>();
                    sr.color = config.animationSprites[0];
                    sr.size = new Vector2(1.5f, 1.0f);
                    sr.sortingOrder = 2;
                    inv: Invader = invader_go.AddComponent<Invader>();
                    inv.score = config.score;
                    inv.animationSprites = config.animationSprites;
                    // Vector3 position = rowPosition; position.x += 2f * j
                    position: Vector3 = new Vector3(row_position.x + 2.0f * j, row_position.y, 0);
                    // invader.transform.localPosition = position
                    invader_go.transform.position = new Vector2( transform.position.x + position.x, transform.position.y + position.y);
                    InvaderChildren.Add(invader_go);
                }
            }
        }
         void Start()
        {

        }
        public void MissileAttack()
        {
            amount_alive: int = GetAliveCount();
            if (amount_alive == 0)
            {
                return;
            }
            foreach (var invaderGo in InvaderChildren)
            {
                // if (!invader.gameObject.activeInHierarchy) continue
                if (!invaderGo.active)
                {
                    continue;
                }
                // if (Random.value < (1f / amountAlive))
                if (Random.value < (1.0f / amount_alive))
                {
                    // Instantiate(missilePrefab, invader.position, Quaternion.identity)
                    InstantiateMissile(invaderGo.transform.position);
                    break;
                }
            }
        }
        public void InstantiateMissile(Vector2 position)
        {
            pos: Vector2 = new Vector2(position.x, position.y - 0.5f);
            missile: GameObject = Instantiate("Missile", position=pos);
            missile.layer = Layers.MISSILE;
        }
         void Update()
        {
            total_count: int = rows * columns;
            amount_alive: int = GetAliveCount();
            amount_killed: int = total_count - amount_alive;
            total_count > 0 ? percent_killed: float = amount_killed / (float)(total_count) : 0;
            speed: float = 1.0f + percent_killed * (speedCurveMax - 1.0f);
            pos: Vector2 = transform.position;
            dx: float = speed * Time.deltaTime * direction.x;
            transform.position = new Vector2(pos.x + dx, pos.y);
            foreach (var invaderGo in InvaderChildren)
            {
                if (invaderGo.active)
                {
                    inv_pos: Vector2 = invaderGo.transform.position;
                    invaderGo.transform.position = new Vector2(inv_pos.x + dx, inv_pos.y);
                }
            }
            left_edge: float = -6.5f;
            right_edge: float = 6.5f;
            foreach (var invaderGo in InvaderChildren)
            {
                if (!invaderGo.active)
                {
                    continue;
                }
                // if (direction == Vector3.right && invader.position.x >= (rightEdge.x - 1f))
                if (direction.x > 0 && invaderGo.transform.position.x >= (right_edge - 1.0f))
                {
                    AdvanceRow();
                    break;
                }
                else if (direction.x < 0 && invaderGo.transform.position.x <= (left_edge + 1.0f))
                {
                    AdvanceRow();
                    break;
                }
            }
            MissileTimer += Time.deltaTime;
            if (MissileTimer >= missileSpawnRate)
            {
                MissileTimer -= missileSpawnRate;
                MissileAttack();
            }
        }
        public void AdvanceRow()
        {
            direction = new Vector3(-direction.x, 0, 0);
            pos: Vector2 = transform.position;
            transform.position = new Vector2(pos.x, pos.y - 1.0f);
            foreach (var invaderGo in InvaderChildren)
            {
                if (invaderGo.active)
                {
                    inv_pos: Vector2 = invaderGo.transform.position;
                    invaderGo.transform.position = new Vector2(inv_pos.x, inv_pos.y - 1.0f);
                }
            }
        }
        public void ResetInvaders()
        {
            direction = new Vector3(1, 0, 0);
            transform.position = new Vector2(initialPosition.x, initialPosition.y);
            for (int idx = 0; idx < InvaderChildren.Count; idx++)
            {
                var invaderGo = InvaderChildren[idx];
                row: int = idx / columns;
                col: int = idx % columns;
                width: float = 2.0f * (columns - 1);
                height: float = 2.0f * (rows - 1);
                x: float = -width * 0.5f + 2.0f * col;
                y: float = -height * 0.5f + 2.0f * row;
                invaderGo.transform.position = new Vector2( initialPosition.x + x, initialPosition.y + y);
                // invader.gameObject.SetActive(true)
                invaderGo.SetActive(true);
            }
        }
        public int GetAliveCount()
        {
            count: int = 0;
            foreach (var invaderGo in InvaderChildren)
            {
                if (invaderGo.active)
                {
                    count += 1;
                }
            }
            return count;
        }
    }
}
