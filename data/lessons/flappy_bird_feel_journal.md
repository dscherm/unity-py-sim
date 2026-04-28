---
game: flappy_bird
deploy_commit: 38e00d3
deploy_at: "2026-04-27T01:27:17Z"
shipped_at: "2026-04-27T01:27:17Z"
tweaks: []
notes: |
  ASP-7 deploy_commit for Flappy Bird is 38e00d3 — the first commit where
  the home_machine.yml workflow went all-green for both Breakout and Flappy
  Bird (run 24972279901, 2026-04-27 01:27 UTC).

  72h window: [2026-04-27T01:27:17Z, 2026-04-30T01:27:17Z]. As of the
  initial seed journal (2026-04-28), no commits have touched
  `data/generated/flappy_bird_project/` or `examples/flappy_bird/` since
  the deploy_commit — `git log --since=2026-04-27T01:27Z -- data/generated/
  flappy_bird_project/ examples/flappy_bird/` returns empty.

  Earlier feel work happened during the 2026-04-22 → 2026-04-24 manual
  playtest sessions (documented in `data/lessons/flappy_bird_deploy.md`):
  AutoStart un-pause timing fix, Spawner prefab wiring, Tiled drawMode
  for parallax, sprite-array wiring, deterministic .cs.meta GUIDs. Those
  were MAN-1 interventions or source-side fixes that closed before the
  ASP-7 deploy_commit; they don't count in this window.

  Honesty caveat: an alternative reading of "deploy_commit" is the
  2026-04-24 Task-8 home-machine playtest at fc6c05b. Under that earlier
  framing, the post-deploy in-window tweaks would be the
  PlayButtonHandler.cs simplification and the AutoStart Start->Update
  move (both documented in flappy_bird_deploy.md, 2026-04-24 section) —
  2 tweaks in the 72h window, still well below J=5. We pick the
  home_machine-CI-green commit because that's the first deploy with a
  reproducible CI bar, which is the truer ASP-7 anchor.
---

# ASP-7 feel journal — flappy_bird

## Why zero tweaks (since 38e00d3)

The hard work on Flappy Bird's feel happened *before* the ASP-7
deploy_commit — during the 2026-04-22 to 2026-04-24 manual home-machine
sessions logged in `flappy_bird_deploy.md`. Those sessions surfaced
seven structural gaps (UI button wiring, prefab-asset SerializeFields,
Tiled drawMode for wide sprites, sprite-array references, deterministic
script GUIDs, etc.) and each gap shipped as a source-side fix to the
translator/scaffolder. By the time the home_machine workflow first
went all-green at 38e00d3, the project regenerated cleanly and the
mechanics (gravity arc, flap impulse, pipe scroll, parallax) were
behaviorally equivalent between pygame and Unity.

## What this journal is *not* tracking

- Sprite swaps, font changes, color tweaks → excluded by ASP-7 definition.
- Setup interventions (manifest edits, CoPlay menu clicks) → those are
  MAN-1 interventions, logged in `flappy_bird_deploy.md`, not here.
- Translator/scaffolder fixes → those are upstream changes that
  regenerate the project; they show up as `chore(generated): regen ...`
  commits but aren't game-specific feel tuning.

## Promotion criterion

This is game #2 toward ASP-7's N=3 requirement. Breakout is #1
(see `breakout_feel_journal.md`). A third game's deploy + journal is
needed to flip the gate from advisory to required.
