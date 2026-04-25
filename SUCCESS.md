# SUCCESS.md — unity-py-sim done-conditions

This document is the source of truth for what unity-py-sim considers "done." It supersedes scattered phase descriptions in `plan.md`. When a request would expand the project beyond the criteria below, prefer `SHELVED.md` instead.

Generated 2026-04-24 as M-5 of the Coverage and Maturation phase.

---

## Mandatory criteria

The project is shipped when **all 5 criteria pass simultaneously** on the main branch.

### MAN-1 · Pipeline ships ≥2 distinct games end-to-end

**Definition**: At least 2 distinct games regenerated from `python -m src.pipeline --game <name>` deploy to a real Unity 6 project, run via CoPlay scene reconstruction, and reach a playable state with **≤5 manual interventions per game**. A "manual intervention" is any post-deploy human action: clicking the CoPlay Tools menu counts as 1; per-component re-wires count as 1 each; package-manifest edits count as 1.

**Status (2026-04-25)**: 2 of 2 ✅ (Flappy Bird at 2 interventions, Breakout at 1: GameManager.cs camelCase patch for Gap B2; the rest was source-fix + MCP automation). See `data/lessons/breakout_deploy.md` for the manual-intervention ledger.

**Delivered by**: M-1 (Breakout E2E) — done; Flappy Bird shipped previously.

### MAN-2 · CI green on every PR

**Definition**: GitHub Actions runs the full pytest suite + ruff lint + structural/convention/compilation gates on every push and PR. A failing test or gate blocks merge to main.

**Status (2026-04-24)**: not configured.

**Delivered by**: M-6.

### MAN-3 · No undocumented `passes: false` in plan.md

**Definition**: Every task in `plan.md` is either `passes: true`, or has an explicit reason and target date in a `blocked_on` field, or is moved to `SHELVED.md` with rationale.

**Status (2026-04-24)**: 1 such task (Hierarchical Architecture Task 8 — Pacman V1 E2E, `blocked_on: home-machine Unity deploy`). Per user redirect (2026-04-24), Pacman V1 is moved to `SHELVED.md` and Breakout takes its place via M-1.

**Delivered by**: M-5 (this task) closes it; subsequent tasks must maintain it.

### MAN-4 · Engine ↔ Unity API coverage measured (not estimated)

**Definition**: `CLAUDE.md`'s estimate of "~15-20% Unity API coverage" is replaced by a measured, dated number from a parity audit. The audit lists every Unity API claimed in `src/reference/mappings/`, marks which have a Python implementation, and marks which have a parity test.

**Status (2026-04-24)**: not measured.

**Delivered by**: M-4 (audit step only — full parity test buildout is ASPIRATIONAL).

### MAN-5 · CLAUDE.md auto-commit policy enforced

**Definition**: The Stop hook in `.claude/settings.json` runs auto-commit on staged changes; CLAUDE.md describes the staging conventions; the hook is verified to fire on at least one routine task without manual approval prompts.

**Status (2026-04-24)**: shipped in commit `b176529`. Active starting next session (hook loads at session start).

**Delivered by**: already done — this criterion exists to prevent regression.

---

## Aspirational criteria

These define the project's *maturity*, not its *shipping*. Useful for prioritization but never blocking.

### ASP-1 · Roundtrip translation, compile-equivalent ≥80% of corpus

**Definition**: At least 80% of `data/corpus/` pairs survive C# → Python → C# roundtrip such that the output C# compiles via the compilation gate.

**Delivered by**: M-2.

### ASP-2 · Roundtrip translation, AST-equivalent ≥50% of corpus

**Definition**: At least 50% of `data/corpus/` pairs survive roundtrip such that the output C# is structurally equivalent to the input (modulo whitespace and ordering).

**Delivered by**: M-2.

### ASP-3 · Engine API parity tests ≥90% coverage

**Definition**: At least 90% of Unity APIs claimed in `src/reference/mappings/classes.json` + `methods.json` + `lifecycle.json` + `patterns.json` have a corresponding parity test in `tests/parity/`.

**Delivered by**: M-4 (post-audit expansion).

### ASP-4 · Parity tests ≥80% pass dotnet path, ≥70% pass CoPlay path

**Definition**: Of the parity tests built per ASP-3, at least 80% pass the headless `dotnet run` path against UnityEngine reference DLLs, and at least 70% pass the CoPlay snapshot path on the home machine.

**Delivered by**: M-4 (post-audit expansion).

### ASP-5 · Cross-machine deploy fully automated

**Definition**: Every push to `main` triggers the home-machine self-hosted runner to clone, deploy, run CoPlay, run Play mode for N seconds, capture screenshots and Unity console logs, and post results back as a PR/commit check. Zero manual ritual on the home machine.

**Delivered by**: M-7.

### ASP-6 · Translation accuracy dashboard live

**Definition**: `data/metrics/dashboard.md` is auto-generated from `data/metrics/history/` snapshots taken on every CI run. Trend lines show compile %, gate pass %, contract test pass %, mutation test pass %, and (post-M-2) per-construct roundtrip scores over time.

**Delivered by**: M-3.

---

## Stopping rule

When all 5 mandatory criteria pass, the project enters **maintenance mode**:
- New work is gated by whether it advances an aspirational criterion or fixes a regression in a mandatory criterion.
- Engine expansion (Particles, Tilemap, CharacterController, polish features) is shelved unless a concrete game in `examples/` requires it.
- New games may be added to `examples/` to broaden the corpus, but each new game must pass the MAN-1 ≤5-intervention bar to count.

---

## Anti-criteria (deliberately not pursued)

- **100% Unity API parity** — fool's errand; engine is a *simulation*, not a re-implementation. Target 2D core completeness, not Unity-wide.
- **3D rendering** — out of scope. unity-py-sim is 2D-first.
- **Editor extensions** — Unity Editor scripting (custom inspectors, asset processors beyond the existing CoPlay generator) is out of scope.
- **In-place ralph autonomy on this machine** — see CLAUDE.md "No API / no ralph.sh" memory. Ralph runs on dedicated infrastructure or not at all.
