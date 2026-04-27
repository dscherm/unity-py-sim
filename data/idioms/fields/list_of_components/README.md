# fields/list_of_components

`bricks: list[GameObject]` lowers to ARRAY form `GameObject[]`, NOT `List<GameObject>`.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.

## Why this is safe

PINNED to current behavior. Note: the M-10 validation agent flagged that the translator emits the array form (`GameObject[]`), not the generic list form (`List<GameObject>`), even while it still emits `using System.Collections.Generic;`. This contradicts gap-1 acceptance criteria in .claude/.ralph-spec.md. The idiom is captured here so any future translator change to `List<GameObject>` shows up as a fixture diff and forces an explicit decision.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
