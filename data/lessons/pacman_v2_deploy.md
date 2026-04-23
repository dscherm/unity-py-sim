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

## Update: PV-1 SHIPPED — 5 more gaps surfaced

**PV-1 status: ✅ shipped.**  Commit implemented scope-aware
`_declared_vars` in `src/translator/python_to_csharp.py` (dict of
`name -> first-declaration indent level`, pruned before each
statement).  Verified: `GhostHome.cs` now emits `var target`,
`var elapsed`, `var t`, `var x`, `var y` in BOTH sibling
if-blocks — the 15 original CS0103 errors are gone.  Tests:
`tests/translator/test_python_to_csharp.py::TestSiblingBlockScoping`
(+3).

With PV-1 unblocked, `check_compile_errors` on regenerated
Pacman V2 surfaces 5 NEW gaps that PV-1 had been masking:

### PV-3 — Python `return` inside a coroutine must yield break
`GhostHome.cs:38` — `error CS1622: Cannot return a value from an
iterator. Use the yield return statement to return a value, or
yield break to end the iteration.`

Python coroutine uses `return` early-exit; C# IEnumerator methods
must use `yield break`.  Translator needs to detect early-exit
`return` in a coroutine context and rewrite.

### PV-4 — Parameter shadowing with enclosing-scope locals
`GhostBehavior.cs:19` — `error CS0136: A local or parameter named
'duration' cannot be declared in this scope because that name is
used in an enclosing local scope to define a local or parameter`.

Python's flat scope lets a method parameter name match a local
name used elsewhere in the function.  C# forbids a parameter name
from being reused as a local within the same method.  Translator
needs to detect parameter-shadowing in method bodies and rename
either the parameter or the conflicting local.

### PV-5 — String→float conversion unhandled in expression translation
`GhostChase.cs:38` — `error CS0030: Cannot convert type 'string'
to 'float'`.  Python's duck-typing allows `"0.5" + 1.0`-ish
patterns; C# is strict.  Translator needs to either infer type
mismatches earlier or emit explicit `float.Parse(...)` calls.

### PV-6 — Typed reference fields emitted as `object`
`Ghost.cs:73` — `error CS1061: 'object' does not contain a
definition for 'Enable'`.  A field that should be typed (e.g., a
MonoBehaviour reference) is being emitted as `public object foo`.
Similar symptom class to gap 1's List<object> inference; needs
the same kind of class-aware inference for plain reference fields.

### PV-7 — `snapped` local variable name stripped by symbol rewriting
`Movement.cs:84-89` — `error CS0103: The name 'snapped' does not
exist in the current context` at multiple sites.  Likely a
name-mangling conflict in the symbol table (snake-to-camel
collision, or reserved-name filtering).  Needs targeted
investigation into how `snapped` gets dropped from
`_current_symbols` or `_declared_vars`.

### PV-2 (unchanged) — Hand-added helper namespace miss
`RuntimeSpriteSetup.cs:80` still needs `using PacmanV2;` — this
is user-side maintenance, not a translator concern.

## Recommended next steps

Pacman V2 still doesn't compile after PV-1's fix, but the work
has narrowed from ~20 errors to 6 — each in a distinct translator
pattern.  PV-3 (yield break for coroutine returns) is the
highest-leverage next fix (affects anywhere a Python coroutine
early-exits).  PV-4/5/6/7 are smaller targeted fixes.  Order of
attack based on error-cascade impact:

1. PV-3 (yield break)
2. PV-4 (parameter shadowing)
3. PV-7 (snapped symbol)
4. PV-6 (object typing)
5. PV-5 (string/float)
6. PV-2 (user-side, trivial)
