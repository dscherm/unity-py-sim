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

## System.Random vs UnityEngine.Random Ambiguity
- Translator emits `using System;` for `Math.Max`/`Math.Min` calls. When the same file also uses `Random.Range` or `Random.value`, C# can't resolve which `Random` to use.
- **Fix**: Translator should emit `Mathf.Max`/`Mathf.Min` (UnityEngine) instead of `Math.Max`/`Math.Min` (System). This eliminates the need for `using System;` entirely in most cases.
- Discovered in: Breakout deployment (BallController.cs, PaddleController.cs, PowerupType.cs)

## Cross-File Module Function Calls
- Python module-level functions like `maybe_spawn_powerup()` get placed as static methods on the last MonoBehaviour class in the file. But callers in OTHER files emit the bare function name without class qualification.
- `MaybeSpawnPowerup(pos)` → should be `Powerup.MaybeSpawnPowerup(pos)`
- The `_post_process` in `project_translator.py` handles cross-file constants but not cross-file function calls.
- Discovered in: Breakout (Brick.cs calling Powerup.MaybeSpawnPowerup)

## Constants Injected Into Enums
- `_post_process` injects `POWERUP_CONFIGS` constant into the first `{` in the file. If the first class is an `enum`, this creates invalid C# (fields inside enums).
- Fix: `_post_process` constant injection should skip enum blocks and find the first real class brace.
- Discovered in: Breakout (PowerupType.cs — enum + dataclass + MonoBehaviour in one file)

## Namespace Collisions in Multi-Game Projects
- Multiple games with same-named classes (e.g. `GameManager`) cause compile errors when deployed to the same Unity project.
- Fix: Always use `namespace` parameter in `translate_project()` when deploying multiple games.
- This is a deployment concern, not a translator bug.

## Bool Truthiness → `!= null` Bug
- Python `if self.game_over:` (truthy check on bool) translates to `if (GameManager.gameOver != null)` instead of `if (GameManager.gameOver)`. A bool is never null in C#, so `!= null` is always true.
- This caused Breakout to show "Game Over!" immediately on start.
- The translator's truthiness handling must distinguish between nullable types (where `!= null` is correct) and value types like bool (where bare value is correct).

## `Reset()` Name Collision with Unity Lifecycle
- Unity calls `Reset()` automatically on any MonoBehaviour when added via `AddComponent` in the editor. If translated code has a `Reset()` method (from Python's `reset()`), it fires during scene setup before the component is initialized, causing NullReferenceExceptions.
- Fix: translator should rename `reset()` to something else (e.g. `ResetState()`, `ResetGame()`) or detect the collision.

## Runtime-Created UI Not Visible
- UI created at runtime via `new GameObject` + `AddComponent<Text>` renders in editor UI capture but may not be visible in Game view. Pre-built scene UI (created via editor scripts) works reliably.
- Root cause unclear — possibly related to Unity 6 UI rendering pipeline or Canvas initialization timing.
- Workaround: pre-build UI in scene setup scripts, wire references via SerializedObject.

## First Successful Unity Deployment (2026-04-05)
- Space Invaders: 7 Python files → 7 C# files → **compiles and runs playably in Unity 6**
- Breakout: 5 Python files → 5 C# files → **compiles and runs** (gameplay works, UI visibility issue unresolved)
- Pipeline: translate_project() → copy to Unity → install com.unity.ugui → scene setup via CoPlay → play
- 5 deployment issues found (see gotchas.md "Unity Deployment" section), all fixable without modifying translated C#
- Key insight: the translated CODE is correct. The gaps are in **project configuration** (packages, layers, collision matrix) and **scene setup** (asset assignment, positions, prefab wiring) — not in the C# output itself.
