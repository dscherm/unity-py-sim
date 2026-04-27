# unsafe/inline_method_import

`from X import Y` inside a method body leaks verbatim as Python statement, invalid C#.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.
- `unsafe.py` — Python that translates BADLY. Captured for contrast.
- `unsafe.notes.md` — failure-mode description and why `safe.py` is the rewrite.

## Why this is safe

Module-top imports translate to C# `using` directives, hoisted properly.

## Why the unsafe form fails

In-method import is a Python-only pattern; translator can't lift it.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
