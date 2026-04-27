# naming/upper_snake_constant

`MAX_HEALTH: int = 100` is preserved as `MAX_HEALTH` (no Pascal-casing of UPPER_SNAKE).

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.

## Why this is safe

Constants stay UPPER_SNAKE in idiomatic C# for readability — translator respects this.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
