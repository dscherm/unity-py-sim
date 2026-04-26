# Flappy Bird — Unity API Catalog

Source: https://github.com/zigurous/unity-flappy-bird-tutorial (5 scripts, ~150 LOC)

## APIs Used Per Script

### Player.cs
- MonoBehaviour lifecycle: Awake, Start, OnEnable, Update
- GetComponent<SpriteRenderer>()
- InvokeRepeating(nameof(method), delay, interval)
- Input.GetKeyDown(KeyCode.Space)
- Input.GetMouseButtonDown(0)
- Time.deltaTime
- Vector3 arithmetic (+, *, .up, .zero, .left)
- transform.position (get/set)
- transform.eulerAngles (get/set)
- SpriteRenderer.sprite (set from Sprite[] array)
- OnTriggerEnter2D(Collider2D)
- CompareTag("Obstacle"), CompareTag("Scoring")
- Static singleton access: GameManager.Instance

### GameManager.cs
- MonoBehaviour lifecycle: Awake, Start, OnDestroy
- Static property: Instance (singleton pattern)
- [DefaultExecutionOrder(-1)] attribute
- [SerializeField] private fields (Player, Spawner, Text, GameObject x2)
- Time.timeScale (get/set)
- player.enabled (set)
- FindObjectsOfType<Pipes>()
- Destroy(gameObject)
- SetActive(bool)
- UnityEngine.UI.Text.text (set)
- int.ToString()
- DestroyImmediate(gameObject)

### Pipes.cs
- MonoBehaviour lifecycle: Start, Update
- Transform references: top, bottom (child transforms)
- Camera.main.ScreenToWorldPoint(Vector3.zero)
- Vector3 arithmetic (+, *, .up, .down, .left, .zero)
- Time.deltaTime
- Destroy(gameObject)

### Spawner.cs
- MonoBehaviour lifecycle: OnEnable, OnDisable
- InvokeRepeating(nameof(method), rate, rate)
- CancelInvoke(nameof(method))
- Instantiate(prefab, position, rotation) — returns typed Pipes
- Random.Range(float, float)
- Quaternion.identity
- Vector3.up

### Parallax.cs
- MonoBehaviour lifecycle: Awake, Update
- GetComponent<MeshRenderer>()
- MeshRenderer.material.mainTextureOffset (set via += Vector2)
- Time.deltaTime

## Tags Used
- "Obstacle" (pipe colliders)
- "Scoring" (gap trigger between pipes)

## Sorting Layers
- Default only

## Physics
- No Rigidbody2D (manual gravity in Player.Update)
- Trigger colliders only (OnTriggerEnter2D)
- Standard gravity: (0, -9.81)

## Prefabs
- Pipes.prefab: Parent GO + Top pipe (child) + Bottom pipe (child) + Scoring trigger (child)

## Assets
- Sprites: Bird_01.png, Bird_02.png, Bird_03.png (animation frames)
- Sprites: Background.png, Ground.png, Pipe.png
- Sprites: GameOver.png, GetReady.png, PlayButton.png (UI)
- Materials: Background.mat, Ground.mat (parallax scrolling)

## Engine Gaps to Fill
1. InvokeRepeating / CancelInvoke — not in engine, use coroutine or timer
2. MeshRenderer.material.mainTextureOffset — parallax via texture offset (can substitute with transform scroll)
3. Camera.main.ScreenToWorldPoint — exists but verify API
4. FindObjectsOfType<T>() — exists as find_objects_of_type
5. DestroyImmediate — may need alias
6. DefaultExecutionOrder attribute — execution order support
7. CompareTag — exists as compare_tag
8. Sprite[] array on component — sprite animation frames as public field
