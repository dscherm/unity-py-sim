# inheritance/monobehaviour_subclass

`class Foo(MonoBehaviour)` becomes `public class Foo : MonoBehaviour`.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.

## Why this is safe

The single most fundamental Unity translation — inheritance from MonoBehaviour.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
