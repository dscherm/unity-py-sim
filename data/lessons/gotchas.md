# Translation Gotchas

Behavioral differences discovered during C# <-> Python translation.

---

## Physics API
- **Unity requires explicit PhysicsMaterial2D for bouncing** — Python pymunk preserves energy by default (coefficient of restitution = 1.0), but Unity's default 2D physics material has bounciness=0 and friction=0.4. A ball game without a `PhysicsMaterial2D(friction=0, bounciness=1)` assigned to ALL colliders (ball, walls, paddle, bricks) will lose energy on every collision — the ball slows down and drifts sideways. This is invisible in the Python simulation because pymunk handles it differently.
- **Discovered in**: Breakout Unity port — ball launched correctly but slowed to a crawl after 2-3 bounces. Fix: create `BouncyBall.physicsMaterial2D` and assign to every collider in the scene.
- **Also set `collisionDetectionMode = Continuous`** on fast-moving balls to prevent tunneling through thin colliders.
- **Don't manually reflect velocity AND use a bouncy physics material** — this causes double-bounce. If you assign `PhysicsMaterial2D(bounciness=1)`, the physics engine already reflects the ball. Adding manual `velocity = new Vector2(vel.x, -vel.y)` in `OnCollisionEnter2D` flips it AGAIN, sending the ball through objects or reversing direction randomly. Let the material handle wall/brick bounces; only override for paddle (custom angle control).
- **Discovered in**: Breakout — ball passed through multiple bricks and changed direction mid-flight because both physics material AND code were reflecting velocity.
- **Unity 6 uses `linearVelocity`** not `velocity` on Rigidbody2D (renamed in Unity 6000.x)
- **Python engine gravity** is set via `PhysicsManager.instance().gravity = Vector2(0, -9.81)`, Unity uses project Physics2D settings
- **Ground check**: Python uses Y-position comparison (`transform.position.y <= ground_y + threshold`), Unity uses `Physics2D.OverlapCircle` with LayerMask — fundamentally different approaches

## Input System
- **Python engine** uses `Input.get_axis("Horizontal")` and `Input.get_key_down("space")` — legacy-style API
- **Unity projects may use new Input System** — `InputActionAsset`, `InputAction`, `ReadValue<Vector2>()`, `WasPressedThisFrame()`
- **The Input System type is invisible to translation** — check `Packages/manifest.json` for `com.unity.inputsystem`
- First FSM port used legacy `Input.GetAxisRaw()` on a new Input System project → 999+ compile errors

## Naming Conventions
- **Python**: `snake_case` methods/fields, `PascalCase` classes
- **C#/Unity**: `PascalCase` public methods, `camelCase` private fields, `PascalCase` classes
- **Translator handles basic conversion** but misses: `is_grounded` → `IsGrounded` (property), `do_before_entering` → `DoBeforeEntering`

## Unity Assets (not translatable)
- **Animator controllers** (.controller) are binary/YAML assets — must be modified via Unity Editor or MCP tools
- **Scene objects** (transforms, colliders) must be set via Inspector or MCP — code that sets them up may never execute
- **Prefabs, materials, sprites** have no Python equivalent — scene setup is manual

## Engine Internal API
- **`GameObject._registry` doesn't exist** — the engine uses a module-level `_game_objects` dict in `core.py`, not a class attribute. Use the public API: `GameObject.find()`, `GameObject.find_game_objects_with_tag()` instead of accessing internal registries.
- **Discovered in**: Breakout `game_manager.py` — `on_brick_destroyed()` tried to iterate `GameObject._registry.values()` to count remaining bricks, caused `AttributeError` at runtime during collision callbacks. Fix: use `GameObject.find_game_objects_with_tag("Brick")`.
- **Rule**: Always use public `GameObject` class methods, never assume internal storage attributes.

## Body Type Switching
- **KINEMATIC->DYNAMIC loses mass in pymunk** — When switching `Rigidbody2D.body_type` from KINEMATIC to DYNAMIC, pymunk zeroes out `mass` and `moment`. The engine must save/restore mass across the transition. Without this fix, `Space.step()` crashes with "dynamic bodies must have mass > 0".
- **Discovered in**: Angry Birds — bird starts kinematic (on slingshot), switches to dynamic on throw. Independent validator caught this before runtime testing.
- **Unity equivalent**: `isKinematic = false` preserves mass automatically. Python engine now handles this in the `body_type` setter.

## Unity 6 API Changes
- **Unity 6 uses `linearVelocity`** not `velocity` on Rigidbody2D (renamed in Unity 6000.x). C# reference files use `linearVelocity`.
- **`CompareTag("Bird")` preferred over `tag == "Bird"`** in Unity for performance, but both work.

## Behavioral Differences
- **FSMState.Act()** in Python takes `MonoBehaviour` base type; original Unity C# used `EnemyBehaviour` — generalization required
- **MonoBehaviour cast**: Python duck-types (`player = owner`), C# requires explicit cast (`var player = (PlayerInputHandler)owner`)
- **Command.DoBeforeLeaving()** called explicitly in Python, sometimes implicit in C# via CommandProcessor

## Unity Deployment — Space Invaders (2026-04-05)

- **`UnityEngine.UI` not installed by default** — Unity 6 projects don't include `com.unity.ugui` out of the box. Any translated code using `UnityEngine.UI.Text` will fail to compile until the package is installed. The translator should warn or document this dependency.
- **Sprite import mode defaults to Multiple** — Programmatically created PNG textures imported via `TextureImporter` can default to `spriteMode: 2` (Multiple) instead of Single. This makes `AssetDatabase.LoadAssetAtPath<Sprite>()` return null. Always set `importer.spriteImportMode = SpriteImportMode.Single` explicitly.
- **Texture compression breaks `SetPixels32`** — Default texture compression is incompatible with runtime pixel manipulation (Bunker destructible shields). Textures that will be modified at runtime need `textureCompression = Uncompressed` and format `RGBA32`.
- **Trigger colliders overlap at spawn** — Projectiles spawned at the player's position immediately trigger `OnTriggerEnter2D` with the player's own collider, destroying the projectile. Fix: layer collision matrix must ignore Laser↔Player collisions. The Python sim doesn't have this problem because collision callbacks are dispatched differently.
- **Boundary zone overlap kills player at start** — If invader grid + collider extents overlap with boundary trigger zones, `OnBoundaryReached()` fires immediately, killing the player before the first frame. Scene layout must account for collider sizes, not just transform positions.
- **Layer collision matrix is not part of the translation** — The translator outputs C# scripts but the Physics2D layer collision matrix is a project setting. Scene setup must configure `Physics2D.IgnoreLayerCollision()` for Laser↔Player, Missile↔Invader, Laser↔Missile. This is a deployment step, not a translation step.

## Translation — Pacman (2026-04-06)

16 files translated, 12/15 pass syntax gate. Key translator gaps found:

- **Instance fields emit as `static`** — Python class-level annotations (`speed: float = 8.0`) translate to `public static float speed = 8.0f` instead of `public float speed = 8.0f`. The translator treats class-body assignments as static. This is the #1 blocker — every file has this.
- **Python type hints leak into C#** — `'GameManager | None'` appears literally in the output as a C# type. The translator doesn't strip Python union type hints or translate `| None` to nullable.
- **`pass` statement leaks** — `on_enable(self): pass` translates to `void OnEnable() { pass; }` instead of an empty method body.
- **Docstrings leak as code** — Multi-line docstrings in methods appear as bare C# statements (e.g. `Unity's BoxCast sweeps && finds exact contact.`).
- **`hasattr()` → bad ternary** — `other.get_component(Node) if hasattr(other, 'get_component') else None` becomes `true ? other.GetComponent<Node>() : null`.
- **`getattr()` leaks verbatim** — `getattr(collision, 'game_object', collision)` appears as-is in C#.
- **Duplicate field declarations** — `__init__` assignments AND class-level annotations both emit fields, causing duplicate declarations.
- **Named arguments in Physics2D calls** — `Physics2D.OverlapBox(point=checkPos, ...)` emits with `point=` keyword which is invalid C#.
- **Coroutines translate well** — `yield None` → `yield return null` and `yield WaitForSeconds(n)` → `yield return new WaitForSeconds(n)` work correctly via the IEnumerator path.

## Playtest Errors (auto-recorded)
- **ImportError**: `DLL load failed while importing bufferproxy: The paging file is too small for this operation to comp` — found in pong playtest (2026-04-05)
  Source: `File "D:\Projects\unity-py-sim\examples\pong\..\..\src\engine\app.py", line 37, in run`
- **ImportError**: `DLL load failed while importing base: The paging file is too small for this operation to complete.` — found in space_invaders playtest (2026-04-05)
- **RuntimeError**: `(ImportError: DLL load failed while importing pixelcopy: The paging file is too small for this opera` — found in breakout playtest (2026-04-05)
- **ImportError**: `DLL load failed while importing _multiarray_umath: The paging file is too small for this operation t` — found in pong playtest (2026-04-05)
- **RuntimeError**: `MemoryError` — found in space_invaders playtest (2026-04-05)
- **SystemError**: `could not initialize PyUIntArrType_Type` — found in space_invaders playtest (2026-04-05)
- **ImportError**: `DLL load failed while importing constants: The paging file is too small for this operation to comple` — found in angry_birds playtest (2026-04-05)
- **ImportError**: `DLL load failed while importing rwobject: The paging file is too small for this operation to complet` — found in angry_birds playtest (2026-04-05)
