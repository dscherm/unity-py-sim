# Translation Patterns

Lessons learned about which Unity patterns are easy/hard to translate to Python.

---

## Easy (translator handles well)
- **Class inheritance** — `class Foo(MonoBehaviour)` ↔ `class Foo : MonoBehaviour` maps cleanly
- **Field declarations** — `self.speed: float = 10.0` ↔ `[SerializeField] private float speed = 10f`
- **Lifecycle methods** — `start()`, `update()`, `fixed_update()` ↔ `Start()`, `Update()`, `FixedUpdate()`
- **Type mappings** — `int`, `float`, `str` ↔ `int`, `float`, `string` handled by type_mapper

## Medium (translator produces rough output, needs adaptation)
- **Property accessors** — Python `@property` not converted to C# property syntax
- **Docstrings** — Triple-quoted docstrings appear as string literal statements in C#
- **f-strings** — `f"Score: {self.score}"` not converted to C# string interpolation `$"Score: {score}"`
- **try/except** — not translated to try/catch
- **Inline imports** — `from module import X` inside methods emits as-is (invalid C#)
- **Constructor classes** — Python `__init__` with params doesn't map to C# constructor (only MonoBehaviour fields via __init__)

## Hard (translator cannot handle, requires manual C#)
- **Multi-class Python files** — Python files that build multiple types inline (e.g. FSM + states) produce 1 class in C#; reference splits into many files
- **Physics2D.OverlapCircle** — No Python equivalent in engine, ground checks use Y-position comparison
- **Animator controller wiring** — Animator params, states, transitions are Unity assets, not code
- **Input Actions** — `Input.get_axis()` has no direct new Input System equivalent (needs InputActionAsset setup)
- **Class name mismatches** — Python Slingshot vs C# SlingShot (capitalization differences in PascalCase)

## Now Handled (fixed in translator as of 2026-04-03)
- **For loops** — `for x in range(n)` → `for (int x = 0; x < n; x++)`, `for x in coll` → `foreach`
- **List operations** — `.append()` → `.Add()`, `len()` → `.Count`, `list()` → `.ToList()`
- **LINQ** — `all(pred for x in coll)` → `.All(x => pred)`, list comprehensions → `.Where().Select().ToList()`
- **Enums** — `class X(Enum)` → `public enum X { PascalCaseMembers }`
- **Input System** — Legacy: `Input.GetKey()`, New: `Keyboard.current.spaceKey.wasPressedThisFrame`
- **Unity 6 velocity** — `rb.velocity` → `rb.linearVelocity` when unity_version >= 6
- **RequireComponent** — Inferred from `get_component(T)` in start/awake
- **GetComponent<T>()** — `self.get_component(T)` → `GetComponent<T>()`
- **Coroutines** — yield generators → `IEnumerator` with `yield return`
- **Namespace wrapping** — `translate(parsed, namespace="MyGame")`

## Baseline Metrics (2026-04-03, 37 pairs)

| Game | Pairs | Avg Score |
|------|-------|-----------|
| pong | 4 | 0.815 |
| breakout | 5 | 0.896 |
| angry_birds | 8 | 0.763 |
| fsm_platformer | 20 | 0.734 |
| **Overall** | **37** | **0.771** |

### 5 Worst Pairs
1. **player_input_handler** (fsm, 0.273) — Monolith Python file creates FSM/states/transitions inline; C# has 18+ separate classes
2. **enemy_behaviour** (fsm, 0.407) — Same inline-FSM pattern
3. **time_transition** (fsm, 0.475) — Constructor-param class pattern
4. **fsm** (fsm, 0.500) — Property getters not translated
5. **slingshot** (angry_birds, 0.512) — Class name case mismatch, PascalCase public fields

## Observed (from fsm-command-patterns v2, 2026-04-01)
- FSM pattern (5 states, 6 transitions) translated structurally but ALL files needed manual adaptation
- Reference C# files used as deployment source instead of raw translator output
- Translator is useful for comparison/gap analysis, not production code generation (yet)
