# Translator Compilability Lessons

Collected across 9 rounds of Python→C# translator fixes (2026-04-04).
Started at 0/7 files compiling, ended at ~11/13 with 7 total errors remaining.

## Stubs Design
- **Don't redefine .NET built-ins** — List<T>, Dictionary, IDisposable already exist in .NET 8. Only stub Unity types.
- **Struct properties, not fields** — `Vector2.normalized` must be a property (`=> default`), not a field. Self-referential fields cause struct layout cycles.
- **Implicit operators** — Unity has implicit Vector2↔Vector3 and Color32↔Color conversion. Add these to stubs or the compiler rejects assignments.
- **AllowMultiple on attributes** — `[RequireComponent]` needs `[AttributeUsage(AllowMultiple = true)]`.

## Naming Conventions
- **UPPER_CASE constants** — preserve as-is everywhere. Don't camelCase (`GRIDRows`) or PascalCase. The enum UPPER→Pascal regex must use an allowlist of known enum types, not a blocklist.
- **snake_case → camelCase for fields, PascalCase for methods** — this is the basic rule, but UPPER_CASE is the exception.
- **Bare snake_case function calls** — module-level functions like `maybe_spawn_powerup()` need explicit PascalCase conversion even without a dot prefix or underscore prefix.

## Scoping
- **Python typed assignments create new scope** — `gm: GameManager = ...` should ALWAYS emit a new declaration in C#, even if `gm` was declared in a sibling if-block. `_declared_vars` is flat but C# has block scoping.
- **Empty blocks must be stripped** — when all statements inside an `if` or `try` are stripped (simulator-only), remove the block header too, or C# gets empty if-bodies.

## Type Mapping
- **Color tuples** — `(R,G,B)` → `Color32` only when target type is color-related. Guard with `csharp_type` check. Negative lookbehind for Vector2/Vector3 constructors.
- **Nullable value types** — `tuple[int,int] | None` → `(int,int)?` (add `?` suffix). Detect `| None` before stripping it.
- **`.Count` vs `.Length`** — arrays use `.Length`, Lists use `.Count`. Track from field declarations AND local variable declarations. Check dotted form too.
- **`.ToList()` vs `.ToArray()`** — check assignment target type. If `T[]`, use `.ToArray()`.

## Module-Level Code
- **Module functions** → `public static` methods on the last MonoBehaviour class in the file.
- **Module constants** → `public static` fields on the class.
- **Cross-file imports** — the translator can't resolve these. Module function calls from other files need manual class qualification (`Powerup.MaybeSpawnPowerup`).

## Dataclasses
- Detect `@dataclass` decorator → mark fields as instance (not class-level/static).
- Constructor kwargs `ClassName(field=value)` → C# object initializer `new ClassName { CamelField = value }`.
- Dataclass fields in plain classes should be `public`, not `private`.

## Simulator Stripping
- Strip: `clipRef`, `assetRef`, `_sync_from_transform`, `DisplayManager`, `PhysicsManager`, `LifecycleManager`, `hasattr()`, pymunk internals.
- Cascade: if a variable assignment is stripped (`dm = DisplayManager.instance()`), subsequent uses of that variable (`dm._title`) must also be stripped.
- Strip target AND value: check both `cs_target == "__STRIP__"` and `cs_value == "__STRIP__"`.

## List Comprehension Gotcha
- When loop variable is `_`, do NOT call `.replace("_", cs_var)` — it strips all underscores from the entire expression, turning `GRID_COLS` into `GRIDCOLS`. Use word-boundary regex or skip entirely for `_`.
