# unsafe/fstring_interpolation

Python f-strings DO NOT lower to C# `$"..."` interpolation. Use `+` concatenation or `.ToString()`.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.
- `unsafe.py` — Python that translates BADLY. Captured for contrast.
- `unsafe.notes.md` — failure-mode description and why `safe.py` is the rewrite.

## Why this is safe

String concatenation lowers cleanly to C# `+` operator.

## Why the unsafe form fails

f'...' literal leaks verbatim into C# output, breaking compilation.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
