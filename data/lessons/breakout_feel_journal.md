---
game: breakout
deploy_commit: 38e00d3
deploy_at: "2026-04-27T01:27:17Z"
shipped_at: "2026-04-27T01:27:17Z"
tweaks: []
notes: |
  ASP-7 deploy_commit for Breakout is 38e00d3 — the first commit where the
  home_machine.yml workflow went all-green for both Breakout and Flappy Bird
  (run 24972279901, 2026-04-27 01:27 UTC). Per SUCCESS.md ASP-5, that run
  validated PlayMode tests passing under Unity 6000.4.0f1.

  72h window: [2026-04-27T01:27:17Z, 2026-04-30T01:27:17Z]. As of the
  initial seed journal (2026-04-28), no commits have touched
  `data/generated/breakout_project/` or `examples/breakout/` since the
  deploy_commit — `git log --since=2026-04-27T01:27Z -- data/generated/
  breakout_project/ examples/breakout/` returns empty.

  This is honest: Breakout shipped at MAN-1 = 1 manual intervention
  (Gap B2 GameManager.cs camelCase patch, fixed at source post-deploy in
  fc9496e on 2026-04-26 — counts as MAN-1, not ASP-7), and there has been
  no post-CI-deploy feel-tuning. The game's mechanics, physics, and
  behaviors translated cleanly from the Python sim.

  See `data/lessons/breakout_deploy.md` for the MAN-1 intervention ledger
  and the gap catalog (B1-B6) that informed the source-side fixes.
---

# ASP-7 feel journal — breakout

## Why zero tweaks

Breakout exemplifies the playground-fidelity story ASP-7 is meant to
track. The Python sim (`examples/breakout/run_breakout.py`) tunes physics
constants (ball velocity, paddle response, brick HP) under pygame; those
constants translate to Unity unchanged via `tools/pipeline.py breakout`,
and the home_machine PlayMode tests confirm they behave as expected on
Unity 6.

The work that *did* happen during the Breakout deploy session
(documented in `data/lessons/breakout_deploy.md`) was setup-side:
sprite paths, package manifest, scaffolder GUID drift, int-vs-float
SerializedProperty. None of those are runtime-behavior tweaks under
ASP-7's definition — they're pipeline gaps that landed as MAN-1
manual interventions or source-side fixes.

## Promotion criterion

ASP-7 promotes from advisory to required when 3 distinct games clear
the J=5 bar within the same calendar week. Breakout is game #1.
Flappy Bird is #2 (see `flappy_bird_feel_journal.md`). A third game
(any of pong, space_invaders, angry_birds, fsm_platformer, pacman_v2,
pacman) needs to deploy and pass to flip the gate.
