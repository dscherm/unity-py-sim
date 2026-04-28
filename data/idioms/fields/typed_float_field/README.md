# fields/typed_float_field

`speed: float = 5.0` becomes `public float speed = 5.0f;` — note the `f` literal suffix.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.

## Why this is safe

Float literal suffix is auto-emitted; without it the C# compiler picks `double`.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
