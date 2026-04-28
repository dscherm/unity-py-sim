# unsafe/property_decorator

`@property` getters DO NOT lower to C# property syntax. Translator emits a regular method.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.
- `unsafe.py` — Python that translates BADLY. Captured for contrast.
- `unsafe.notes.md` — failure-mode description and why `safe.py` is the rewrite.

## Why this is safe

Explicit getter method translates predictably; reader knows it's a method call.

## Why the unsafe form fails

@property compiles fine here in isolation but call-sites assume field-style access.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
