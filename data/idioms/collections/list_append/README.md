# collections/list_append

`xs.append(x)` translates to `xs.Add(x);` (Unity uses C# List<T>.Add).

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.

## Why this is safe

`.append` → `.Add` is one of the 'now handled' wins per data/lessons/patterns.md.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
