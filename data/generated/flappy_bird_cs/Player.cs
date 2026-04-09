using System.Collections.Generic;
using UnityEngine;
[RequireComponent(typeof(SpriteRenderer))]
public class Player : MonoBehaviour
{
    public float strength = 5.0f;
    public float gravity = -9.81f;
    public float tilt = 5.0f;
    public Vector3 Direction = new Vector3(0, 0, 0);
    public int SpriteIndex = 0;
    [SerializeField] private List<object> sprites;
    [SerializeField] private SpriteRenderer SpriteRenderer;
     void Awake()
    {
        SpriteRenderer = GetComponent<SpriteRenderer>();
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
        Direction = Vector3.zero;
    }
     void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space) || Input.GetMouseButtonDown(0))
        {
            Direction = Vector3.up * strength;
        }
        Direction = new Vector3( Direction.x, Direction.y + gravity * Time.deltaTime, Direction.z);
        transform.position = transform.position + Direction * Time.deltaTime;
        var rotation = transform.eulerAngles;
        rotation = new Vector3(rotation.x, rotation.y, Direction.y * tilt);
        transform.eulerAngles = rotation;
    }
    public void AnimateSprite()
    {
        SpriteIndex += 1;
        if (SpriteIndex >= sprites.Count)
        {
            SpriteIndex = 0;
        }
        if (SpriteIndex < sprites.Count && SpriteIndex >= 0)
        {
            if (SpriteRenderer != null)
            {
                SpriteRenderer.sprite = sprites[SpriteIndex];
            }
        }
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        if (other.gameObject.CompareTag("Obstacle"))
        {
            GameManager.instance.GameOver();
        }
        else if (other.gameObject.CompareTag("Scoring"))
        {
            GameManager.instance.IncreaseScore();
        }
    }
}
