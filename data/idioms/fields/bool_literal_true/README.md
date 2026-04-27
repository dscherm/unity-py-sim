# fields/bool_literal_true

Python `True` lowers to C# `true` (lowercase). Critical: `True` in C# is a parse error.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.

## Why this is safe

`True/False/None` → `true/false/null` translation is tracked by the syntax compilation gate.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
