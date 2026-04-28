# input/keyboard_current_null_safe

New Input System reads must use `Keyboard.current?.X.Y == true` — `Keyboard.current` is null in batchmode tests.

## Files

- `safe.py` — Python that translates cleanly (recommended form).
- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs
  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`
  and fails if the translator drifts.

## Why this is safe

Locks in the null-safe `?.X.Y == true` pattern that translator-input-system-null-guard (closed 2026-04-27) emits. Prevents regression to unconditional `Keyboard.current.X` accesses that throw NullReferenceException under Unity Test Framework PlayMode.

## Regenerating the fixture

Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`
if the translator's behavior on this idiom changes intentionally.
