---
# ASP-7 feel journal — canonical schema.
# Copy this file to `<game>_feel_journal.md` after a deploy goes green and
# fill in the fields below as you tune the game.
#
# Fields:
#   game           — short slug matching examples/<game>/ (e.g. "breakout").
#   deploy_commit  — short or full SHA of the master commit where the
#                    home_machine.yml workflow first went green for this
#                    game. This is the start of the 72h ASP-7 window.
#   deploy_at      — ISO 8601 UTC timestamp of that deploy commit. The 72h
#                    counting window is [deploy_at, deploy_at + 72h].
#   shipped_at     — ISO 8601 UTC timestamp when the author declares the
#                    game has reached "shippable feel". Optional until
#                    the author signs off; set to null while still tuning.
#   tweaks         — list of post-deploy runtime-behavior changes. Each
#                    tweak is one entry with three required fields:
#                      when     — ISO 8601 UTC timestamp.
#                      what     — one-sentence description, ideally citing
#                                 file:line or Inspector path.
#                      category — one of:
#                                   - physics-constant   (mass, drag, gravity, speed, etc.)
#                                   - animation-timing   (clip duration, transition speed, etc.)
#                                   - audio-mix          (volume, pitch, AudioSource params)
#                                   - control-feel       (input response, jump force, etc.)
#                                   - other              (anything that changes runtime behavior
#                                                         and doesn't fit above; explain in `what`)
#                    Optional per-entry: notes — free text for context.
#   notes          — top-level free text. Use this to acknowledge data
#                    gaps in honest reconstructions ("deploy_commit is the
#                    manual playtest, not the home_machine CI run, because
#                    the workflow predates this game's first deploy").
#
# What does NOT count as a tweak (per ASP-7 spec):
#   - Sprite swaps, recolors, font changes, pure visual asset edits.
#   - Setup interventions counted under MAN-1 (CoPlay menu clicks,
#     manifest edits, per-component re-wires that get the game to first
#     playable). Those land in `<game>_deploy.md`, not here.
#
# ASP-7 thresholds:
#   J = 5 tweaks per game
#   N = 3 games required
#   window = 72h after deploy_commit
#
# The gate (`src/gates/asp7_gate.py`) parses this frontmatter and asserts
# `count(in-window tweaks) <= J` per game, and that >= N games pass.
game: example_game
deploy_commit: 0000000
deploy_at: "2026-01-01T00:00:00Z"
shipped_at: null
tweaks:
  - when: "2026-01-01T01:00:00Z"
    what: "Player.cs speed 5 -> 7 — felt sluggish in Unity vs pygame"
    category: control-feel
  - when: "2026-01-01T02:00:00Z"
    what: "Animator: jump-clip duration 0.4 -> 0.5"
    category: animation-timing
  - when: "2026-01-01T03:00:00Z"
    what: "Inspector: BallController drag 0.1 -> 0"
    category: physics-constant
  - when: "2026-01-01T04:00:00Z"
    what: "AudioSource: brick-break volume 0.6 -> 0.8"
    category: audio-mix
  - when: "2026-01-01T05:00:00Z"
    what: "Time.fixedDeltaTime 0.02 -> 0.0167 for tighter physics tick"
    category: other
    notes: "Project Settings -> Time."
notes: |
  This template lives at data/lessons/_feel_journal_template.md.
  See SUCCESS.md ASP-7 and AGENT_GUIDE.md section (g) for the full rules.
---

# ASP-7 feel journal — example_game

This body section is free-form. Use it to narrate the post-deploy tuning
arc: what surprised you about Unity behavior vs the Python sim, which
tweaks moved the needle, and what would have prevented the tweak in a
future cycle (engine API gap, parity test missing, idiom catalog miss).

The structured frontmatter above is what the ASP-7 gate parses. The body
is for humans.
