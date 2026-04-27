# Idiom Catalog (M-11)

A machine-checkable map of which Python idioms translate cleanly to C# in
unity-py-sim, and which don't.

Every idiom is a directory under `data/idioms/<feature_area>/<idiom_name>/`
with a frozen `safe.cs.expected` C# fixture. The test suite at
`tests/idioms/test_idiom_catalog.py` walks every entry, runs
`tools/translate_snippet.py --diff`, and fails if reality drifts. Drift is
sometimes a translator regression, sometimes a translator improvement — the
test forces the choice to be intentional.

## When to consult the catalog

- **Authoring a new game on unity-py-sim** — scan the `safe/` half before
  picking an idiom; if your pattern isn't here, run `tools/translate_snippet.py
  --code "..."` to preview what the translator will emit.
- **Reviewing translator changes** — if `tests/idioms/` goes red on a PR, the
  diff in `safe.cs.expected` shows you exactly what changed and you decide
  whether it's a fix or a regression.
- **Filing a translator gotcha** — instead of a free-form note in
  `data/lessons/gotchas.md`, ship a paired `safe.py` + `unsafe.py` directory
  that the test suite can enforce going forward.

## Directory layout

```
data/idioms/
  README.md                 ← this file
  <feature_area>/           ← lifecycle, fields, naming, inheritance, math,
    <idiom_name>/                 input, collections, unsafe (8 areas as of M-11)
      README.md             ← description, why-it's-safe, how-to-regenerate
      safe.py               ← Python that translates cleanly (recommended form)
      safe.cs.expected      ← frozen C# output — the regression net
      extra_args.txt        ← optional: extra CLI flags (e.g., --input-system new)
      unsafe.py             ← only on `unsafe/*` idioms: the failing form
      unsafe.notes.md       ← only on `unsafe/*` idioms: failure mode + rewrite
```

The eight current feature areas:

- `lifecycle/` — Awake/Start/Update/coroutines, Unity entry-point conventions.
- `fields/` — typed instance fields, default values, list/dict/array forms.
- `naming/` — snake_case → PascalCase rules; UPPER_SNAKE constants.
- `inheritance/` — MonoBehaviour subclassing, Enum subclassing.
- `math/` — Vector2/Vector3 constructors and static constants.
- `input/` — new Input System (`Input.get_key_down` → `Keyboard.current?.X.Y == true`).
- `collections/` — list operations (`.append`, `len()`).
- `unsafe/` — patterns that translate badly: `@property`, f-strings,
  `hasattr`, in-method imports.

## Adding a new idiom

```bash
# 1. Edit tools/build_idiom_catalog.py — append an Idiom(...) dataclass entry.
# 2. Run the script to generate the directory + capture current translator output.
python tools/build_idiom_catalog.py

# 3. Run the catalog tests to confirm the new idiom round-trips.
python -m pytest tests/idioms/ -v

# 4. Commit data/idioms/<area>/<name>/ + tools/build_idiom_catalog.py.
```

If the translator's emission for your new idiom looks WRONG to you, still
commit the catalog entry first — pinning current behavior. Then file a
follow-up that fixes the translator and updates the fixture in the same PR.
The catalog's job is to prevent silent drift, not to prescribe what the
translator should do.

## Refreshing fixtures after an intentional translator change

```bash
# After a translator PR that intentionally changes emission for known idioms:
python tools/build_idiom_catalog.py        # rewrite all fixtures
python -m pytest tests/idioms/ -v          # confirm green
git diff data/idioms/                      # review the diff carefully — this is
                                           # the moment a translator regression
                                           # would slip through; reject if the
                                           # change isn't explicitly desired
```

## Drift detection in CI

`pytest tests/` (the standard CI invocation in `.github/workflows/test.yml`)
already picks up `tests/idioms/`. No additional CI step is needed.

## Anti-pattern: "fix" the catalog without fixing the translator

If `safe.cs.expected` for an idiom looks wrong but the translator hasn't
changed, **do not** rewrite the fixture. The catalog is descriptive, not
prescriptive. File the translator bug separately. Only refresh the fixture
when the translator's emission has actually changed and the change is wanted.
