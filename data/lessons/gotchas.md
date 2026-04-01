# Translation Gotchas

Behavioral differences discovered during C# <-> Python translation.

---

## Physics API
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

## Behavioral Differences
- **FSMState.Act()** in Python takes `MonoBehaviour` base type; original Unity C# used `EnemyBehaviour` — generalization required
- **MonoBehaviour cast**: Python duck-types (`player = owner`), C# requires explicit cast (`var player = (PlayerInputHandler)owner`)
- **Command.DoBeforeLeaving()** called explicitly in Python, sometimes implicit in C# via CommandProcessor
