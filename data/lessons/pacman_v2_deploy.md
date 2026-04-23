# Pacman V2 Unity Deployment — First Home-Machine Regen

Session date: 2026-04-22 / 2026-04-23 (cont). Regenerated Pacman V2 into
an existing Unity 6 project at `D:\UnityProjects\Pac-Man-V2` via
`python tools/pipeline.py pacman_v2 --output <path>`. First home-machine
validation of the 7-gap-fix pipeline against a larger game (16 .cs files
vs Flappy Bird's 5; 4 ghost states; coroutine-based transitions).

## Outcome

Pipeline produced 16 translated C# files + scaffolder fixtures cleanly
(pipeline gate passed in 4.7s). Unity compiled most files successfully
but surfaced **2 new gaps** previously invisible in Flappy Bird:

| # | Gap | Severity | File(s) |
|---|---|---|---|
| PV-1 | Coroutine local-variable hoisting lost across Python if-blocks | P0 (prevents compile) | `GhostHome.cs` |
| PV-2 | Hand-added helper scripts in the global namespace can't reference translated classes in `namespace PacmanV2` | P1 | `RuntimeSpriteSetup.cs` |

## Gap PV-1 — Coroutine translator loses variable scope across if-blocks

**Symptom (compile errors at `GhostHome.cs:75–92`, ~15 errors):**
```
error CS0103: The name 'target' does not exist in the current context
error CS0103: The name 'elapsed' does not exist in the current context
error CS0103: The name 'x' does not exist in the current context
error CS0103: The name 'y' does not exist in the current context
error CS0103: The name 't' does not exist in the current context
```

**Root cause.** Python function scope is flat — a variable declared in
one `if` branch is visible in the next `if` branch of the same function.
C# uses lexical block scope — a `var x = ...` inside `if (A) {}` is
NOT visible inside `if (B) {}` at the same level.

The translator emits Python's `target = inside.transform.position` as
`var target = ...` for the FIRST occurrence and plain `target = ...` for
subsequent assignments. That works fine for one if-block but breaks when
Python reassigns the same-named variable in a SIBLING block:

```csharp
public IEnumerator ExitTransition()
{
    ...
    if (inside != null)
    {
        var target = inside.transform.position;   // declared here
        var elapsed = 0.0f;                       // declared here
        while (elapsed < 0.5f)
        {
            var t = elapsed / 0.5f;               // declared here
            var x = startPos.x + (target.x - startPos.x) * t;
            var y = ...;
            ...
        }
    }
    if (outside != null)
    {
        Vector2 insidePos = ...;
        target = outside.transform.position;      // ← CS0103 (out of scope)
        elapsed = 0.0f;                           // ← CS0103
        while (elapsed < 0.5f)
        {
            t = elapsed / 0.5f;                   // ← CS0103
            x = insidePos.x + (target.x - insidePos.x) * t;  // ← CS0103
            y = ...;                              // ← CS0103
        }
    }
    ...
}
```

**Upstream fix options (pick one):**

- **(A) Hoist all local variables to the method top.** Walk the Python
  function, collect every assignment target name, emit typed
  declarations (or `var x = default;` / `Vector3 x;` etc.) at the top
  of the C# method body. Subsequent assignments become plain reassignment.
  This is the standard C# idiom for simulating Python-style function
  scope. Best long-term fix; moderate scope.
- **(B) Track declared-variable set per method scope.** Only emit `var`
  on the FIRST assignment anywhere in the method (not the first in a
  block). Less uniform but smaller translator change.
- **(C) Detect sibling-block reassignment** specifically and bubble the
  declaration up to the least common ancestor. More surgical but
  complex AST analysis.

Option (A) is the cleanest and matches how the existing
`test_semantic_layer.py::test_awake_fallback_merged_into_existing_awake`
test already handles method-body augmentation.

**Files that will need updating:**
- `src/translator/python_to_csharp.py` — method body emission.
- Add tests mirroring the Python if-else assignment pattern and
  asserting no CS0103 references.

**Scope (estimated):** Single-file translator change + ~10 new tests.
Fits in a focused session on top of this one.

## Gap PV-2 — Hand-added global-namespace helpers can't see translated classes

**Symptom (compile error at `RuntimeSpriteSetup.cs:80`):**
```
error CS0246: The type or namespace name 'AnimatedSprite' could not be found
```

**Root cause.** `RuntimeSpriteSetup.cs` is a hand-added helper in the
global namespace. The translator emits all translated classes in
`namespace PacmanV2 { ... }` (via the `--namespace` default and the
scaffolder's namespace wrapping). RuntimeSpriteSetup needs either
`using PacmanV2;` at the top OR to live inside `namespace PacmanV2`.

**Fix (user-side):** add `using PacmanV2;` to the helper script OR move
it into the translated package. This is a one-line local fix.

**Upstream consideration:** the scaffolder does not discover hand-added
Scripts/*.cs files, so it can't auto-fix them. Consider documenting the
convention in the scaffolder output — "scripts you add by hand that
reference translated classes must `using <Namespace>;` first, or live
inside that namespace."

## What shipped already (applies to Pacman V2)

All 7 Flappy Bird deploy gap fixes land in Pacman V2 automatically:
- AutoStart.cs + AspectLock.cs scaffolder fixtures present in
  `Assets/_Project/Scripts/`.
- `.cs.meta` files written with deterministic GUIDs.
- Prefab generator emits deterministic `m_Script` GUIDs.
- `_heal_prefab_script_guids` healed any existing prefabs during scaffold.
- CoPlay generator would emit AspectLock attachment on orthographic
  cameras, prefab-asset refs on prefab-class SerializeFields, etc.
  (not yet observed in Pacman V2 because the scene-setup script for
  Pacman V2 wasn't regenerated this session — only the translator +
  scaffolder ran).

## Recommended next step

Fix gap PV-1 at source (translator variable hoisting). That unblocks
Pacman V2 compilation. Then re-run the pipeline, open the project,
and proceed to the scene-setup + gameplay validation that would have
surfaced Pacman-specific scene/wiring gaps on top.
