# inheritance/enum_subclass

`class State(Enum)` with `IDLE = 0` members becomes `public enum State { Idle, ... }`.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.

## Why this is safe

Enum translation handled per data/lessons/patterns.md (since 2026-04-03).

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
