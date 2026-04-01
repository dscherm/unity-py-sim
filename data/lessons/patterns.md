# Translation Patterns

Lessons learned about which Unity patterns are easy/hard to translate to Python.

---

## Easy (translator handles well)
- **Class inheritance** — `class Foo(MonoBehaviour)` ↔ `class Foo : MonoBehaviour` maps cleanly
- **Field declarations** — `self.speed: float = 10.0` ↔ `[SerializeField] private float speed = 10f`
- **Lifecycle methods** — `start()`, `update()`, `fixed_update()` ↔ `Start()`, `Update()`, `FixedUpdate()`
- **Type mappings** — `int`, `float`, `str` ↔ `int`, `float`, `string` handled by type_mapper

## Medium (translator produces rough output, needs adaptation)
- **For loops** — `for t in self.transitions:` generates TODO comment instead of `foreach`
- **List operations** — `.append()` not translated to `.Add()`, Python list syntax not converted to `List<T>`
- **Property accessors** — Python `@property` not converted to C# property syntax
- **Docstrings** — Triple-quoted docstrings appear as string literal statements in C#
- **Self references** — `self.` not always stripped to `this.` or bare reference

## Hard (translator cannot handle, requires manual C#)
- **Input System** — Python uses `Input.get_axis()` (legacy-style), Unity may need `InputActionAsset` (new Input System)
- **Physics2D.OverlapCircle** — No Python equivalent in engine, ground checks use Y-position comparison
- **Animator controller wiring** — Animator params, states, transitions are Unity assets, not code
- **SerializeField attributes** — Python has no equivalent; translator must infer from field patterns
- **GetComponent<T>() generics** — Python `get_component(T)` → C# `GetComponent<T>()` generic syntax

## Observed (from fsm-command-patterns v2, 2026-04-01)
- FSM pattern (5 states, 6 transitions) translated structurally but ALL files needed manual adaptation
- Reference C# files used as deployment source instead of raw translator output
- Translator is useful for comparison/gap analysis, not production code generation (yet)
