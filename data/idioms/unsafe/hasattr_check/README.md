# unsafe/hasattr_check

`hasattr(x, 'attr')` becomes a literal `true` ternary — drops the runtime check.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.
- `unsafe.py` — Python that translates BADLY. Captured for contrast.
- `unsafe.notes.md` — failure-mode description and why `safe.py` is the rewrite.

## Why this is safe

Explicit null check translates to `if (target != null)` — the C# idiom.

## Why the unsafe form fails

hasattr always-true short-circuits the safety check at runtime.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
