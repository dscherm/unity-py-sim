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
