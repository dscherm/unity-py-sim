using UnityEngine;
[RequireComponent(typeof(SpriteRenderer))]
public class Player : MonoBehaviour
{
    [SerializeField] private GameManager gameManager;
    public float strength = 5.0f;
    public float gravity = -9.81f;
    public float tilt = 5.0f;
    public Vector3 direction = new Vector3(0, 0, 0);
    public int spriteIndex = 0;
    public List<object> sprites;
    [SerializeField] private SpriteRenderer spriteRenderer;
     void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
    }
     void Start()
    {
        InvokeRepeating("AnimateSprite", 0.15f, 0.15f);
    }
     void OnEnable()
    {
        var position = transform.position;
        position = new Vector3(position.x, 0.0f, position.z);
        transform.position = position;
        direction = Vector3.zero;
    }
     void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space) || Input.GetMouseButtonDown(0))
        {
            direction = Vector3.up * strength;
        }
        direction = new Vector3( direction.x, direction.y + gravity * Time.deltaTime, direction.z);
        transform.position = transform.position + direction * Time.deltaTime;
        var rotation = transform.eulerAngles;
        rotation = new Vector3(rotation.x, rotation.y, direction.y * tilt);
        transform.eulerAngles = rotation;
    }
    public void AnimateSprite()
    {
        spriteIndex += 1;
        if (spriteIndex >= sprites.Count)
        {
            spriteIndex = 0;
        }
        if (spriteIndex < sprites.Count && spriteIndex >= 0)
        {
            if (spriteRenderer != null)
            {
                spriteRenderer.sprite = sprites[spriteIndex];
            }
        }
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        if (other.gameObject.CompareTag("Obstacle"))
        {
            gameManager.GameOver();
        }
        else if (other.gameObject.CompareTag("Scoring"))
        {
            gameManager.IncreaseScore();
        }
    }
}
