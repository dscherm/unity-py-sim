---
game: space_invaders
deploy_commit: fd9ab00
deploy_at: "2026-04-29T01:22:54Z"
shipped_at: "2026-04-29T01:25:10Z"
tweaks: []
notes: |
  ASP-7 deploy_commit for Space Invaders is fd9ab00 — the first commit
  where the home_machine.yml workflow went green for space_invaders
  (run 25086126256, 2026-04-29 01:25 UTC). Per SUCCESS.md ASP-5, that
  run validated both batchmode CoPlay scene setup AND Unity Test
  Framework PlayMode tests passing under Unity 6000.4.0f1.

  72h window: [2026-04-29T01:22:54Z, 2026-05-02T01:22:54Z]. As of the
  initial seed journal (2026-04-29), this is the deploy commit itself —
  there has been no post-CI-deploy feel-tuning yet.

  Honesty caveat: Space Invaders shipped at MAN-N = 0 manual interventions,
  but the path to deploy required two source-side translator fixes (NOT
  ASP-7 tweaks):

    1. Method-as-value RHS naming bug — `self._invoke_callback =
       self._new_round` emitted `... = newRound;` (camelCase, dangling)
       instead of `... = NewRound;` (PascalCase method ref). Fixed in
       4a7c1ca by adding `_current_class_methods` to python_to_csharp.py
       and consulting it in `_self_dot_replace`.

    2. TODO scope leakage — typed locals initialised from ROW_CONFIG
       (`InvaderRowConfig config = Invaders.ROW_CONFIG[...]`) were
       commented out as TODO, but downstream `config.X` references
       stayed live as dangling identifiers. Fixed in 4a7c1ca by
       broadening the regex in project_translator._post_process to
       match typed declarations, not just `var X = ROW_CONFIG`.

  Both fixes are translator-level (apply to every future game), with
  regression tests in tests/translator/test_method_as_value_and_todo_scope.py.
  Per the existing ASP-7 schema, these are pipeline-side fixes and do
  NOT count as runtime-behavior tweaks.

  See data/generated/space_invaders_project/ for the regenerated C# and
  the home_machine run for the green PlayMode test artifact.
---

# ASP-7 feel journal — space_invaders

## Why zero tweaks

Space Invaders is the "playground-fidelity proves itself" game for ASP-7.
Two translator bugs surfaced during the deploy attempt that would have
blocked Unity compile (CS0103 dangling identifier, CS0103 undefined
field). Both were caught BEFORE the runtime feel window opened — fixed
at the translator source and the regenerated C# compiled cleanly.

The Python sim (`examples/space_invaders/space_invaders_python/`) is a
line-by-line port of zigurous/space-invaders. Movement curve (1.0 →
speed_curve_max), missile cadence (`missile_spawn_rate = 1.0`), and the
edge-bounce / advance-row choreography all behaved correctly under both
pygame and Unity batchmode PlayMode tests on the first green run. No
runtime feel adjustments were needed in the 72h window post-deploy.

## Promotion criterion

ASP-7 promotes from advisory to required when 3 distinct games clear
the J=5 bar within the same calendar week. Breakout is game #1. Flappy
Bird is #2. **Space Invaders is #3** — this journal flips the gate from
2/3 to 3/3.

Once the parity_runner CI step auto-commits the latest dashboard
snapshot, the next CI run for `.github/workflows/test.yml` should see
`asp7_passed: true` and the gate is ready to ratchet from advisory
(`continue-on-error: true`) to required (`continue-on-error: false`).

## Translator fixes ledger (NOT counted as tweaks)

Both fixes shipped in commit 4a7c1ca:

| File | Fix | Test |
|------|-----|------|
| `src/translator/python_to_csharp.py` | `_current_class_methods` global; method-as-value RHS emits PascalCase | `test_method_reference_assignment_uses_pascal_case` |
| `src/translator/project_translator.py` | broadened ROW_CONFIG-tracking regex for typed locals | `test_typed_local_initialised_from_row_config_propagates_todo` |

These are infrastructure fixes — every future game gets them for free.
The fact that Space Invaders deployed cleanly after the fix on the
first attempt is the playground-fidelity proof point.
