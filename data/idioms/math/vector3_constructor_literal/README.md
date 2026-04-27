# math/vector3_constructor_literal

`Vector3(1.0, 2.0, 3.0)` becomes `new Vector3(1.0f, 2.0f, 3.0f)` — `f` suffixes auto-added.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.

## Why this is safe

Float-suffix promotion on Vector3 ctor args is a translator-correctness milestone.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
