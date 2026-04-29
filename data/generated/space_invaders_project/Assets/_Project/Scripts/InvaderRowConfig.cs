using System.Collections.Generic;
using UnityEngine;
namespace SpaceInvaders
{
    public class InvaderRowConfig
    {
        public Color32[] animationSprites = new Color32[0];
        public int score = 10;
    }
    public class Invaders : MonoBehaviour
    {
        public float speedCurveMax = 5.0f;
        public Vector3 direction = new Vector3(1, 0, 0);
        public Vector3 initialPosition = new Vector3(0, 0, 0);
        public int rows = 5;
        public int columns = 11;
        public float missileSpawnRate = 1.0f;
        public float missileTimer = 0.0f;
        [SerializeField] private List<GameObject> invaderChildren = new List<GameObject>();
        [SerializeField] private GameObject missilePrefab;
        // TODO: public static InvaderRowConfig[] ROW_CONFIG = new InvaderRowConfig[] { new InvaderRowConfig { animationSprites = new Color32[] { new Color32(50, 255, 50, 255), new Color32(30, 200, 30, 255) }, score = 10 }, new InvaderRowConfig { animationSprites = new Color32[] { new Color32(50, 255, 50, 255), new Color32(30, 200, 30, 255) }, score = 10 }, new InvaderRowConfig { animationSprites = new Color32[] { new Color32(50, 200, 255, 255), new Color32(30, 150, 200, 255) }, score = 20 }, new InvaderRowConfig { animationSprites = new Color32[] { new Color32(50, 200, 255, 255), new Color32(30, 150, 200, 255) }, score = 20 }, new InvaderRowConfig { animationSprites = new Color32[] { new Color32(255, 100, 100, 255), new Color32(200, 60, 60, 255) }, score = 30 } };
         void Awake()
        {
            initialPosition = new Vector3( transform.position.x, transform.position.y, 0);
            CreateInvaderGrid();
        }
        public void CreateInvaderGrid()
        {
            for (int i = 0; i < rows; i++)
            {
                float width = 2.0f * (columns - 1);
                float height = 2.0f * (rows - 1);
                // Vector2 centerOffset = new Vector2(-width * 0.5f, -height * 0.5f)
                Vector2 centerOffset = new Vector2(-width * 0.5f, -height * 0.5f);
                // Vector3 rowPosition = new Vector3(centerOffset.x, (2f * i) + centerOffset.y, 0f)
                Vector3 rowPosition = new Vector3(centerOffset.x, (2.0f * i) + centerOffset.y, 0);
                // TODO: InvaderRowConfig config = Invaders.ROW_CONFIG[i % Invaders.ROW_CONFIG.Length];
                for (int j = 0; j < columns; j++)
                {
                    // Invader invader = Instantiate(prefabs[i], transform)
                    GameObject invaderGo = new GameObject($"Invader_{i}_{j}"); // TODO: wire via Inspector or Instantiate
                    invaderGo.layer = Layers.INVADER;
                    Rigidbody2D rb = invaderGo.AddComponent<Rigidbody2D>();
                    rb.bodyType = RigidbodyType2D.Kinematic;
                    BoxCollider2D col = invaderGo.AddComponent<BoxCollider2D>();
                    col.size = new Vector2(1.5f, 1.5f);
                    col.isTrigger = true;
                    SpriteRenderer sr = invaderGo.AddComponent<SpriteRenderer>();
                    // TODO: sr.color = config.animationSprites[0];
                    sr.size = new Vector2(1.5f, 1.0f);
                    sr.sortingOrder = 2;
                    Invader inv = invaderGo.AddComponent<Invader>();
                    // TODO: inv.score = config.score;
                    // TODO: inv.animationSprites = config.animationSprites;
                    // Vector3 position = rowPosition; position.x += 2f * j
                    Vector3 position = new Vector3(rowPosition.x + 2.0f * j, rowPosition.y, 0);
                    // invader.transform.localPosition = position
                    invaderGo.transform.position = new Vector2( transform.position.x + position.x, transform.position.y + position.y);
                    invaderChildren.Add(invaderGo);
                }
            }
        }
         void Start()
        {
            /* pass */
        }
        public void MissileAttack()
        {
            int amountAlive = GetAliveCount();
            if (amountAlive == 0)
            {
                return;
            }
            foreach (var invaderGo in invaderChildren)
            {
                // if (!invader.gameObject.activeInHierarchy) continue
                if (!invaderGo.activeSelf)
                {
                    continue;
                }
                // if (Random.value < (1f / amountAlive))
                if (Random.value < (1.0f / amountAlive))
                {
                    // Instantiate(missilePrefab, invader.position, Quaternion.identity)
                    InstantiateMissile(invaderGo.transform.position);
                    break;
                }
            }
        }
        public void InstantiateMissile(Vector2 position)
        {
            Vector2 pos = new Vector2(position.x, position.y - 0.5f);
            GameObject missile = Instantiate(missilePrefab, pos, Quaternion.identity);
            missile.layer = Layers.MISSILE;
        }
         void Update()
        {
            int totalCount = rows * columns;
            int amountAlive = GetAliveCount();
            int amountKilled = totalCount - amountAlive;
            float percentKilled = totalCount > 0 ? amountKilled / (float)(totalCount) : 0;
            float speed = 1.0f + percentKilled * (speedCurveMax - 1.0f);
            Vector2 pos = transform.position;
            float dx = speed * Time.deltaTime * direction.x;
            transform.position = new Vector2(pos.x + dx, pos.y);
            foreach (var invaderGo in invaderChildren)
            {
                if (invaderGo.activeSelf)
                {
                    Vector2 invPos = invaderGo.transform.position;
                    invaderGo.transform.position = new Vector2(invPos.x + dx, invPos.y);
                }
            }
            float leftEdge = -6.5f;
            float rightEdge = 6.5f;
            foreach (var invaderGo in invaderChildren)
            {
                if (!invaderGo.activeSelf)
                {
                    continue;
                }
                // if (direction == Vector3.right && invader.position.x >= (rightEdge.x - 1f))
                if (direction.x > 0 && invaderGo.transform.position.x >= (rightEdge - 1.0f))
                {
                    AdvanceRow();
                    break;
                }
                else if (direction.x < 0 && invaderGo.transform.position.x <= (leftEdge + 1.0f))
                {
                    AdvanceRow();
                    break;
                }
            }
            missileTimer += Time.deltaTime;
            if (missileTimer >= missileSpawnRate)
            {
                missileTimer -= missileSpawnRate;
                MissileAttack();
            }
        }
        public void AdvanceRow()
        {
            direction = new Vector3(-direction.x, 0, 0);
            Vector2 pos = transform.position;
            transform.position = new Vector2(pos.x, pos.y - 1.0f);
            foreach (var invaderGo in invaderChildren)
            {
                if (invaderGo.activeSelf)
                {
                    Vector2 invPos = invaderGo.transform.position;
                    invaderGo.transform.position = new Vector2(invPos.x, invPos.y - 1.0f);
                }
            }
        }
        public void ResetInvaders()
        {
            direction = new Vector3(1, 0, 0);
            transform.position = new Vector2(initialPosition.x, initialPosition.y);
            for (int idx = 0; idx < invaderChildren.Count; idx++)
            {
                var invaderGo = invaderChildren[idx];
                int row = idx / columns;
                int col = idx % columns;
                float width = 2.0f * (columns - 1);
                float height = 2.0f * (rows - 1);
                float x = -width * 0.5f + 2.0f * col;
                float y = -height * 0.5f + 2.0f * row;
                invaderGo.transform.position = new Vector2( initialPosition.x + x, initialPosition.y + y);
                // invader.gameObject.SetActive(true)
                invaderGo.SetActive(true);
            }
        }
        public int GetAliveCount()
        {
            int count = 0;
            foreach (var invaderGo in invaderChildren)
            {
                if (invaderGo.activeSelf)
                {
                    count += 1;
                }
            }
            return count;
        }
    }
}
