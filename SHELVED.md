# SHELVED.md — phases deliberately not pursued

Phases listed here are *not* abandoned — they're explicitly out of scope for the current cycle (Coverage and Maturation, 2026-04-24+). To revive a shelved phase, propose it as a new task in `plan.md` with rationale tied to a specific `SUCCESS.md` criterion.

This file is paired with `SUCCESS.md`. Together they define the boundary between in-scope and out-of-scope work.

---

## Shelved phases (from `plan.md`)

### Engine Expansion P3 — Particles, Tilemap, CharacterController2D

**Why shelved**: No game in `examples/` currently requires particles, tilemap-based level construction, or a CharacterController2D. Adding these expands the engine surface area without advancing any `SUCCESS.md` criterion. Revive when a target game can't be built without one of them.

**Original tasks**: plan.md tasks 10-12 in "Engine Expansion P3 — Particles, Tilemap, CharacterController."

### Engine Expansion P3+ — Visual Polish (Sprite Atlas + TextMeshPro-lite)

**Why shelved**: Premature polish. The current SpriteRenderer + UI.Text path covers all 8 example games. Atlas and rich text are wishlist items.

**Original tasks**: plan.md tasks 13-14 in "Engine Expansion P3+ — Visual Polish."

### Simulator Redesign — Unity-Native Patterns

**Why shelved**: Risk-heavy refactor (auto-registration lifecycle, auto-build colliders, prefab registry, serializable data classes, class-level constants). Each task is a working-tree-wide rewrite that could destabilize the test suite for a marginal "more Unity-like" payoff. None of the 5 mandatory criteria depend on it. Revive only if a translator pattern *cannot* be implemented because of the current simulator design.

**Original tasks**: plan.md "Phase: Simulator Redesign — Unity-Native Patterns" Tasks 1-5+.

### Space Invaders Clone (further iteration)

**Why shelved**: 7 of 7 Space Invaders tasks are `passes: true` per plan.md and the project memory notes "Space Invaders deployed: code is correct" (commit fc6c05b lineage). Further iteration on Space Invaders is duplicative with M-1 (Breakout E2E) for proving N≥2. Revive only if Space Invaders is chosen as a third E2E demo (counts toward MAN-1 if so).

### Pacman V1 — Hierarchical Architecture Task 8 (E2E pipeline validation)

**Why shelved**: User redirect 2026-04-24 chose Breakout instead of Pacman V1 for the second E2E demonstration (now M-1). Pacman V1's pipeline components are all green in isolation; the only outstanding work is the home-machine deploy-and-playtest ritual. That ritual is in scope under M-7 (cross-machine automation). Once M-7 ships, re-running the Pacman V1 deploy is essentially free — but it doesn't need to happen *first*.

### Pacman V2 — Zigurous Tutorial Port (further iteration)

**Why shelved**: All 7 plan.md tasks for Pacman V2 are `passes: true`. The port served its purpose (tested whether accumulated lessons produce a faster cleaner implementation than v1). Further iteration is research, not shipping. Revive if Pacman V2 is chosen as a third E2E deploy under MAN-1.

### Angry Birds Clone (further iteration)

**Why shelved**: All 11 plan.md Angry Birds tasks are `passes: true`. The Angry Birds work drove engine features (PhysicsMaterial2D, mouse drag, trajectory preview) that are now generally available. Further iteration adds engine features no SUCCESS.md criterion needs.

---

## Anti-tasks (proposed but rejected)

These are ideas that have come up in conversation but are explicitly not on any roadmap.

- **Replace pygame with Bevy/Pyxel/etc.** — pygame is the rendering substrate for the simulator and works. Switching engines is a year-long project with no SUCCESS.md payoff.
- **Translate Python → JavaScript/TypeScript for web games** — the project is Unity-targeted by definition.
- **Add an LLM-assisted translation fallback** — translator is deterministic by design (CLAUDE.md). LLM fallbacks introduce variance that defeats reproducibility.
- **Multiplayer / networking** — out of scope for 2D single-player gamedev simulation.

---

## Reviving a shelved item

To move something off this list:
1. Cite the specific `SUCCESS.md` criterion the work advances (mandatory or aspirational).
2. Open a new task in `plan.md` with `id`, `description`, `steps`, `passes: false`.
3. Run `python /d/Projects/ralph-universal/tools/bridge_state.py refresh` to load it.
4. Delete the relevant section here.
