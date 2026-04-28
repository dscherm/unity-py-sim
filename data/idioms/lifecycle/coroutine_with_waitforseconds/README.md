# lifecycle/coroutine_with_waitforseconds

Generator yields to `WaitForSeconds(...)` translate to `IEnumerator` + `yield return new WaitForSeconds(...)`.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.

## Why this is safe

Coroutines were 'now handled' per data/lessons/patterns.md as of 2026-04-03.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
