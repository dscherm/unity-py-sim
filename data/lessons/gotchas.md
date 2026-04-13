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

## Engine Lifecycle — Pacman (2026-04-06)

- **Awake() must run on disabled components** — The engine was skipping `awake()` for `enabled=False` components. Unity calls `Awake()` regardless of enabled state. This caused ghost behaviors (added disabled) to never initialize their `ghost` reference, breaking all ghost AI.
- **enabled must fire on_enable/on_disable callbacks** — Was a plain attribute. Changed to a property. Without callbacks, `GhostHome.on_disable()` (which starts the exit transition coroutine) never fired.
- **Start() defers for disabled components** — Must stay in start queue until enabled, not be dropped. Components enabled later (by game logic) need their `Start()` called on the first frame they're active.
- **Teleporting must sync Rigidbody2D** — Setting `transform.position` without `rb.move_position()` causes `Movement.fixed_update()` to overwrite the teleport with the stale pymunk body position. Always update BOTH.
- **Grid movement needs explicit snap-to-grid** — Unity's `MovePosition` + `BoxCast` naturally aligns to grid via physics resolution. Our overlap-based detection needs explicit grid-snapping when turning at intersections. Maze X offset=0.5, Y offset=0.0.
- **Node placement must include corners** — Original `is_intersection` only detected 3+ open directions (T-junctions). L-shaped corners (2 non-opposite directions) also need nodes or ghosts get stuck at dead ends.
- **Ghost house needs a gate** — Without a wall at the ghost house entrance, scatter/chase ghosts walk back into the house and get stuck. Add obstacle-layer walls at the entrance row.

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

## V2 Reimplementation Failures (2026-04-07)

Lessons that existed from v1 but were NOT correctly applied during v2 implementation:

- **Passage cooldown is mandatory** — documented in v1 passage.py comments, but v2 initially omitted it. Engine fires triggers every physics step. Without `_recent_teleports` dict + 0.5s cooldown, objects teleport back and forth every frame.
- **GhostBehavior.enable() must force disable→enable** — v1 lesson says "enabled property must fire callbacks" but v2 initially just set `self.enabled = True` which is a no-op if already True. Must explicitly set False then True.
- **Ghost house gate: position matters** — v1 places gate at row 12, cols 13-14 (entrance center) with half-height box. v2 initially placed at cols 11,16 (sides) which blocked ghosts from exiting entirely. Gate must be at the entrance, not the pen walls.
- **Ghost.start() not awake() for behavior lookup** — Behaviors are added to the GameObject after Ghost in scene setup. awake() runs when the component is added, so behaviors don't exist yet. Must use start() for get_component lookups. v1 documented this in a comment but v2 initially used awake().
- **GhostBehavior.invoke method name** — v1 uses `self.invoke("disable", duration)`. v2 initially used `self.invoke("_disable_self", duration)`. The invoke system matches method names exactly — a renamed method silently fails.

**Root cause:** The lessons were documented as text descriptions in gotchas.md but the implementation agent (Claude) didn't cross-reference them during coding. The lesson injection system (`prepare_context.py`) injects ralph-universal cross-project lessons but does NOT inject project-specific lessons from `data/lessons/`. This is a gap.

- **Ghost behaviors must NOT use forced=True in set_direction** — `forced=True` bypasses grid-snapping in Movement.set_direction(). Ghosts drift off the grid after one turn, never overlap with Node triggers again, and freeze at the next wall. V1 uses `set_direction(dir)` without forced in scatter/chase/frightened. Only GhostHome exit transition should use forced (to set initial direction after the lerp).

## V2 Additional Discoveries (2026-04-07)

New lessons discovered during v2 that did NOT exist in v1:

### Engine Bugs Found

- **Engine doesn't propagate active=False to children** — Setting `parent.active = False` does NOT deactivate child GameObjects. Children must check parent state explicitly. In Unity, inactive parents hide all children. Workaround: child components should check `self._parent_go.active` in update().
- **Engine didn't stop updates on inactive objects** — `lifecycle.py` was calling `update()`/`fixed_update()` on components of inactive GameObjects. Objects were invisible but still moving, colliding, and eating pellets. Fixed in lifecycle.py and physics_manager.py to check `game_object.active` before dispatching. This is a CRITICAL engine fix.
- **CoroutineManager list mutation during tick** — `stop_all_coroutines()` and `stop_coroutine()` replace `self._coroutines` with a new list. When called from INSIDE `tick()` (e.g., reset_state triggered by invoke), new coroutines added during the call are appended to the new list, but `tick()` overwrites it with `still_running` from the old list. Result: coroutines silently lost. Workaround: use `update()`-based timers instead of `self.invoke()` for operations that create new coroutines (like reset_state).

### Ghost System Lessons

- **Ghost component must be added BEFORE behaviors in scene setup** — `GhostBehavior.awake()` calls `self.get_component(Ghost)`. If Ghost is added after behaviors, awake() returns None and the ghost reference is never set. V1 adds Ghost first (line 251 of run_pacman.py). V2 initially added Ghost last.
- **All behaviors must start disabled (enabled=False) in scene setup** — If behaviors start enabled (Component default), `Ghost.reset_state()` triggers cascading on_disable callbacks that corrupt state. Set `home.enabled = False`, `scatter.enabled = False`, `chase.enabled = False`, `frightened.enabled = False` explicitly after adding each component.
- **Ghost reset must NOT disable scatter before enabling it** — Calling `scatter.disable()` triggers `GhostScatter.on_disable()` which calls `chase.enable()`, leaving both scatter AND chase active. V1 pattern: only disable frightened and chase, then enable scatter.
- **Rigidbody type must not change on reset** — `Movement.reset_state()` had `rb.is_kinematic = False` which switched KINEMATIC ghosts to DYNAMIC, breaking their physics. Ghosts that use MovePosition must stay KINEMATIC.
- **AnimatedSprite overwrites sprite every frame** — When GhostFrightened swaps the body sprite to blue, the AnimatedSprite component overwrites it on the next update(). Fix: disable AnimatedSprite during frightened mode, re-enable on disable.

### Sprite/Rendering Lessons

- **SpriteRenderer.color does NOT tint sprite blits** — The renderer only uses `color` for the colored-rectangle fallback. When a `.sprite` surface is set, it's blitted directly with no tint. To color-tint a sprite, apply `BLEND_RGB_MULT` to a copy of the surface at creation time.
- **Node triggers need BoxCollider2D(size=0.5), not CircleCollider2D(radius=0.25)** — CircleCollider2D with small radius doesn't reliably overlap with ghost colliders at grid-aligned positions. V1 uses BoxCollider2D with 0.5 size, which gives a larger trigger area.
- **Pygame convert_alpha() requires a display surface** — Loading sprites in headless mode fails with "No video mode has been set". Must call `pygame.display.set_mode((1,1))` before loading any sprites.
- **run() max_frames default must be None, not 0** — `max_frames=0` matches `frames >= 0` on the first frame and exits immediately. Use `None` for unlimited.

### System Architecture Lessons

- **prepare_context.py does NOT inject project-specific lessons** — Only injects cross-project lessons from ralph-universal/lessons/. Project lessons in data/lessons/ are invisible to the loop agent. This is the #1 reason v1 lessons weren't applied in v2.
- **GameManager must be created LAST in scene setup** — GameManager.start() calls new_game() → reset_state() which operates on ghosts. If ghosts haven't had their start() called yet, they have null behavior references. Create GameManager after all ghosts.
- **GameManager deferred calls must use update() timers, not invoke()** — `self.invoke("reset_state", 3.0)` runs reset_state from inside CoroutineManager.tick(), which causes coroutine list mutation bugs. Use a timer in update() instead.

## Simulator-only GameObjects in scene export (2026-04-13)

**Problem:** QuitHandler (and similar simulator-only MonoBehaviours) get serialized into scene JSON and generate `GetComponent<QuitHandler>()` in CoPlay scripts. Unity has no QuitHandler class → CS0246 compile error.

**Fix:** Added `_SIMULATOR_ONLY_OBJECTS` skip set in scene_serializer.py. GameObjects whose names match are excluded from export. Currently: `{"QuitHandler"}`.

**Rule:** Any MonoBehaviour that only exists for the Python simulator (pygame event handling, display management, etc.) must be added to this set. If a new game has a similar pattern, add the name before exporting.
