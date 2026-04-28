# AGENT_GUIDE.md — Operating Manual for unity-py-sim

> **Read this first when handed unity-py-sim as a build target.** It tells you
> what the simulator guarantees, what tools answer your moment-to-moment
> "will this translate?" questions, and what will fail your PR.

> **Glossary:** `M-N` = milestone N from `plan.md` (e.g. M-12 is the Gap Gate
> milestone). `MAN-N` / `ASP-N` = mandatory / aspirational criterion N from
> `SUCCESS.md` (e.g. MAN-1 = "≥2 distinct games ship end-to-end"). When this
> doc cites `M-12` or `MAN-1`, look there for the source-of-truth.

The 5-second mental model: write Python that uses Unity-shaped APIs, run it
under `pygame` for instant feedback, then push. CI translates to C#, builds
against Unity 6 reference DLLs, and runs the parity tests on the home machine.
Anything outside the parity-tested API surface is undefined behavior — see (a).

---

## (a) What the simulator is and isn't

**Faithful** for **83 of 87 APIs in the registry** — 80 have a passing
dual-path parity test under `tests/parity/`, and 3 are explicitly parked as
deferred-implementation. Source of truth:
`data/metrics/parity_matrix.json` and the rendered table at
`data/metrics/parity_matrix.md`.

The parity-tested surface includes Transform (position/rotation/scale/parenting/
SetParent/Translate), Rigidbody2D (velocity/mass/drag/gravityScale/bodyType),
Time (deltaTime/fixedDeltaTime/timeScale/frameCount), Input (GetKey/GetKeyDown/
GetAxis), GameObject (activeSelf/SetActive/FindGameObjectsWithTag), the
MonoBehaviour callback set (Awake/Start/OnEnable/OnDisable/Update/FixedUpdate/
LateUpdate), Camera.orthographicSize, SpriteRenderer.sortingOrder, and basic
classes (Quaternion, Mathf, Debug, BoxCollider2D, CircleCollider2D,
PhysicsMaterial2D, Physics2D.Raycast).

**Undefined** outside that surface. `Transform.Rotate`/`LookAt`/`forward`/
`right` are still deferred-untested (M-9) — they need Quaternion-faithful
stub math. `Component.GetComponent`, `Camera.backgroundColor`, and
`SpriteRenderer.color` are parked as *deferred-implementation* (in-scope
long-term, blocked on stub work). Audio, Canvas/RectTransform/Text/Image/
Button, SceneManager, and DOTween are parked as *out-of-scope* for the
headless dual-path harness. All parked APIs carry `PARITY_SCAFFOLD_PARKED`
markers under `tests/parity/`.

3D, Unity Editor extensions, particles, tilemaps, and shaders are off the
roadmap — see `SHELVED.md`.

---

## (b) M-10 — `tools/translate_snippet.py`

When you wonder "will this fragment translate?", paste it into the snippet
tool and read the C# back in under a second. **Wrap fragments in a class** —
the translator emits class-scoped C#, so bare top-level expressions produce
empty output:

```bash
python tools/translate_snippet.py --code "class Mover:
    def Update(self):
        self.transform.position += self.velocity * Time.delta_time"
python tools/translate_snippet.py --file path/to/snippet.py --with-using
python tools/translate_snippet.py --diff expected.cs --file actual.py
echo "x: int = 5" | python tools/translate_snippet.py
```

Cold start ≈ 132 ms. Exit codes: `0` ok, `1` `--diff` mismatch, `2` invalid
input, `3` translator threw. Use it during authoring as a tight feedback loop
— faster than running the full pipeline. Source: `tools/translate_snippet.py`.

---

## (c) M-11 — Idiom catalog (`data/idioms/`)

When the snippet tool says your idiom translates badly (or doesn't), look up
the correct shape in `data/idioms/`. The catalog has paired `safe.py` /
`safe.cs.expected` examples (and where relevant a paired `unsafe.py` showing
the antipattern with a `unsafe.notes.md` explaining the rewrite).

Layout (8 areas, 20 idioms today):
- `lifecycle/` — Awake/Start/Update bodies that translate cleanly
- `fields/` — `[SerializeField]` shape, default-value emission
- `naming/` — snake_case ↔ camelCase rules the translator applies
- `inheritance/` — MonoBehaviour subclassing
- `math/` — Vector3/Quaternion/Mathf usage
- `input/` — `Input.get_key` and friends; the null-safe Keyboard pattern
- `collections/` — `len()` → `.Count` / `.Length`
- `unsafe/` — pre-compile failures the translator can't fix for you

The frozen `.cs.expected` fixtures are validated by
`tests/idioms/test_idiom_catalog.py` (62 parametrized tests). If you add an
idiom, run `python tools/build_idiom_catalog.py --check` to detect drift.
Source: `data/idioms/README.md`.

---

## (d) M-12 — Gap Gate (CI enforcer)

The Gap Gate is a required CI job (`.github/workflows/test.yml :: gap_gate`).
Its contract:

> For every Unity API REFERENCED by a Python file TOUCHED in a PR, there must
> be a passing dual-path parity test under `tests/parity/`.

**Two rules** to internalize:
1. **Untouched files are grandfathered.** If your PR doesn't touch a file, its
   uncovered references don't fail the gate.
2. **Touched files are strict.** Even if a reference predates your edit, the
   gate fails if it's not parity-tested. Adding a single line to a file with
   pre-existing untested API references will fail CI.

**On miss**, the gate writes a skeleton via `tools/parity_scaffold.py` with a
`PARITY_SCAFFOLD_SKELETON` marker. Fill in `scenario_python` and
`scenario_csharp_body`, refresh the matrix
(`python -m src.gates.parity_matrix`), and re-run. The gate's exit codes:
`0` clean, `1` uncovered APIs, `2` I/O error.

Run locally: `python -m src.gates.gap_gate --base master --no-scaffold`.
Source: `src/gates/gap_gate.py`.

---

## (e) Playtest + pipeline workflow

Three loops, in order of increasing cost:

1. **Visual debug (seconds)** — `python tools/playtest.py <game> [--headless --frames 300]`.
   Auto-records errors to `data/lessons/playtest_errors.jsonl`. Use this while
   iterating on engine behavior.
2. **Full Python → C# regen (~30 s)** — `python tools/pipeline.py <game>`.
   Translates the Python game into `data/generated/<game>_project/`,
   scaffolds the Unity project, copies sprites, writes the CoPlay scene
   reconstruction script. **NOTE:** Use `tools/pipeline.py`, NOT
   `python -m src.pipeline` — the latter drops the namespace wrapper and
   fails Unity compile (auto-memory: project_pipeline_command).
3. **End-to-end Unity validation (~5 min, home machine)** —
   `gh workflow run home_machine.yml -f games=<game>`. Runs PlayMode tests via
   `[UnityTest]` runner against the actual Unity 6 install, posts results back
   as a check. Use this before claiming a deploy works (SUCCESS.md ASP-5).

`dotnet build` against `stubs/UnityEngine.cs` is the work-machine ceiling —
it confirms generated C# compiles, which is what the parity harness already
exercises. The home machine is the only place that proves Unity actually
*runs* the game.

---

## (f) Failure-mode shortlist

Cross-linked to `data/lessons/`. When you hit one of these, read the linked
lesson before retrying.

- **Translator-unfriendly idioms** — most common: `dataclass` default factories
  for mutable types, inline method imports inside class bodies, wildcard
  imports, conditional class definitions. See `data/lessons/patterns.md` and
  `data/lessons/translator_compilability.md` (9 rounds of fixes documented).
- **Input-system null traps** — `Keyboard.current.X` and `Mouse.current.X` are
  null until first event in headless contexts. The translator emits the
  `?.X.Y == true` null-conditional Boolean coerce; if you see a NullRef in a
  generated game, that pattern probably wasn't applied. See `data/idioms/
  input/` and `data/lessons/breakout_deploy.md`.
- **Namespace mismatches** — every game has a fixed namespace defined in
  `tools/pipeline.py :: GAME_NAMESPACES`. CoPlay scene scripts auto-default
  to that namespace; missing entries break the scene reconstruction. See
  `data/lessons/coplay_generator_gaps.md`.
- **`SerializeField` cross-component wiring** — generated scene setup wires
  prefab fields by construction, but inline cross-component refs
  (`Player.gameManager`) don't auto-wire. P1 follow-up tracked in
  `data/lessons/coplay_generator_gaps.md`.
- **Pacman-style line-by-line port deviations** — every playtest bug has
  traced back to a Python deviation from the reference C#. Add the missing
  Unity API to the engine; never work around it with a Python idiom. See
  `data/lessons/gotchas.md` and the auto-memory
  `feedback_line_by_line_enforcement`.
- **Audio module** — Unity 6 audio surface differs from earlier versions; the
  parity harness explicitly parks all three Audio APIs. See
  `data/lessons/unity6_audio_module.md`.
- **Worktree staleness** — never spawn agents with `isolation: "worktree"`.
  Three of three attempts landed on stale commits. See `data/lessons/
  testing.md` and CLAUDE.md preamble.

---

## (g) ASP-7 — Playtest fidelity / feel journal

unity-py-sim's second pillar (alongside the Python→Unity translator) is
that the pygame sim is a **playground** — you tune mechanics, physics,
and behaviors in Python so the deployed Unity game arrives shippable
with sprite/art polish the only remaining work. ASP-7 in `SUCCESS.md`
formalizes that pillar with a per-game post-deploy tweak budget.

**When to start a journal:** the moment `home_machine.yml` first goes
all-green for a new game. That commit is the journal's `deploy_commit`
and starts the 72-hour ASP-7 window.

**What counts as a tweak:** anything that changes how the game *plays*
post-deploy — source-code retunes (constants, magic numbers, timing),
Inspector value changes, prefab numeric edits, AnimatorController param
tweaks, audio import settings. Categorize each as `physics-constant`,
`animation-timing`, `audio-mix`, `control-feel`, or `other`.

**What does NOT count:** sprite swaps, recolors, font changes — pure
visual asset edits. Setup interventions (CoPlay menu clicks, manifest
edits) — those live in `<game>_deploy.md` under MAN-1.

**Where the journal lives:** `data/lessons/<game>_feel_journal.md` with
a YAML frontmatter block. Schema and an in-line example: copy
`data/lessons/_feel_journal_template.md`.

**Where the gate runs:** `src/gates/asp7_gate.py`. Local advisory check:
`python -m src.gates.asp7_gate --check`. CI runs it from the snapshot
job in `test.yml` with `continue-on-error: true` until 3 games clear
the J=5 bar in the same calendar week.

If you find yourself making >5 in-window tweaks for a game, that's
diagnostic — the engine has a parity gap that should be fixed at
source (engine API, parity test, idiom catalog) instead of patched
per-game in Unity.

---

## Antipattern checklist (grep your draft before claiming done)

Before opening a PR, grep your changes for these. Each one is a known
foot-gun that will either fail the Gap Gate, fail `dotnet build`, or surface
as a Unity runtime null.

1. **Truthy bool checks** (`if self.game_over:`) — the translator emits
   `if (gameOver != null)`, which is always true in C#. Compare to the literal
   you actually want: `if self.game_over == True:` →
   `if (gameOver == true)`. Source: `data/lessons/translator_compilability.md`
   ("Bool Truthiness → `!= null` Bug").
2. **`Component.GetComponent` calls** — deferred API; either avoid or add a
   parity test.
3. **`Transform.Rotate` / `LookAt` / `forward` / `right`** — deferred; use
   `Quaternion.Euler` / explicit math.
4. **`Camera.backgroundColor` / `SpriteRenderer.color` writes** — deferred;
   either implement + add parity test, or set via prefab.
5. **`Keyboard.current.X` without `?.X.Y == true`** — translator should
   handle, but verify the generated C# matches.
6. **Wildcard imports (`from foo import *`)** — translator drops them; you'll
   lose symbols silently.
7. **Conditional class definitions** (`if cond: class Foo: ...`) — emits
   broken C#.
8. **Mutating engine state inside `__init__`** — use `Awake` / `Start`.
9. **Asserting on `transform.position` after `transform.position = ...`
   without a physics tick** — set via `rb.move_position` if rigidbody is
   attached (auto-memory: project_teleport_must_sync_rb).
10. **New game added to `examples/` without `tools/pipeline.py <game>`
    succeeding + 1 dotnet build green** — it won't pass MAN-1.

---

## Source-of-truth pointers

| Question | Authoritative file |
|---|---|
| What APIs are tested? | `data/metrics/parity_matrix.json` (rendered: `parity_matrix.md`) |
| How do I write idiom X? | `data/idioms/<area>/<idiom>/safe.py` + `safe.cs.expected` |
| What's done / shipped? | `SUCCESS.md` (5 mandatory + 6 aspirational criteria) |
| What's deliberately not pursued? | `SHELVED.md` |
| What broke last time I did X? | `data/lessons/*.md` |
| Will my snippet translate? | `python tools/translate_snippet.py` |
| Will my PR pass CI? | `python -m src.gates.gap_gate --base master --no-scaffold` |
