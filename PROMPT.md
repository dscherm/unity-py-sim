# PROMPT.md — unity-py-sim

## Context

@.ralph/pending_tasks.md
@.ralph/recent_activity.md
@.ralph/memories.md
@.ralph/gate_failure.md
@.ralph/human_note.md
@CLAUDE.md

Source code: `src/`. Tests: `tests/`.
Engine: `src/engine/` — Python simulation of Unity's core systems.
Reference: `src/reference/` — Unity<->Python API mapping data + query layer.
Translator: `src/translator/` — Bidirectional C#<->Python translation.
Gates: `src/gates/` — Custom validation gates for translation accuracy.
Data: `data/` — Translation corpus, accuracy metrics, lessons learned.

## Your Task — 8-Phase Sequence

Follow these phases in order. ONE task per iteration.

### Phase 1: Orient

- Read pending tasks (above). Your task is the FIRST one listed.
- Read lesson warnings injected below pending tasks. Apply them proactively.
- Read recent activity to understand what was just completed.
- Read memories for cross-iteration context.
- **If gate_failure.md is non-empty, FIX THE GATE FAILURE before starting any new task.**
- If `.ralph/remote_gate_result.md` exists with status: fail, treat it as a gate failure.
- If human_note.md has content, follow those instructions.

### Phase 2: Search

- Before writing any code, search the codebase for existing implementations.
- Do not duplicate code that already exists. Extend or modify it instead.
- Check both `src/engine/` and `src/translator/` — they share the math and type systems.
- Use subagents for parallel codebase searches when helpful.

### Phase 3: Implement

- Follow the task's `steps` array from pending_tasks.md.
- Full implementations only — no placeholders, no stubs, no TODOs.
- If the task cannot be completed, signal BLOCKED (see Phase 8).

### Phase 4: Verify

- Run targeted tests for the modules you changed:
  ```
  python -m pytest tests/ -v --tb=short
  ```

- If you changed **translator** code, also run roundtrip tests:
  ```
  python -m pytest tests/translator/test_roundtrip.py -v
  ```

- If you changed **translation rules or type mappings** (shared_files), run integration tests:
  ```
  python -m pytest tests/integration/ -v
  ```

- If you touched shared code (`core.py`, `vector.py`, `translation_rules.json`, `type_mappings.json`), run the full test suite:
  ```
  python -m pytest tests/ -x --tb=short -q
  ```

- **NOTE**: C# compilation (`dotnet build`) and Unity runtime tests run on the HOME machine only.
  If you produced C# output, validate syntax with tree-sitter parse — do not attempt `dotnet build` here.

### Phase 5: Record

- Add an entry to `activity.md`:
  ```
  ## YYYY-MM-DD - Task N: Brief Title

  **Goal:** What was being accomplished

  **Changes Made:**
  - `file.py`: Description of change (specific values)

  **Verification:**
  - `test command` -- N passed, 0 failures

  **Status:** COMPLETE
  ```
- If you learned something non-obvious, add it to `.ralph/memories.md`.
- If you discovered a translation pattern or gotcha, add it to `data/lessons/patterns.md` or `data/lessons/gotchas.md`.
- If you discovered new issues, add them as new JSON task blocks at the end of `plan.md`.

### Phase 6: Mark — CRITICAL

**YOU MUST DO THIS.** In `plan.md`, find the JSON block for the task you completed.
Change `"passes": false` to `"passes": true`.

**If you skip this step, the next iteration will re-attempt the same task.**
This is the #1 cause of wasted iterations. VERIFY plan.md is updated before committing.

### Phase 7: Commit

- Stage specific files by name. **NEVER use `git add -A` or `git add .`.**
- Commit with: `type: brief description`
- **NEVER push to remote.**

### Phase 8: Signal

- If ALL pending tasks are done: output `<promise>COMPLETE</promise>`
- If you cannot proceed: output `<promise>BLOCKED</promise>`
- If you completed work but aren't confident: output `<promise>NEEDS_REVIEW</promise>`
- Otherwise: output nothing (the harness will start the next iteration).

## Rules

- **ONE task per iteration. Only one.**
- Fix gate failures before new work.
- No placeholders, stubs, or TODOs.
- Expertise focus: backend, testing

## Architecture Notes

- The simulator mirrors Unity's component system: GameObject -> Component -> MonoBehaviour
- Physics uses pymunk (2D), will graduate to pybullet (3D)
- Rendering uses pygame (2D), will graduate to moderngl/pyglet (3D)
- All vectors backed by numpy, quaternions by pyrr
- Translator is AST-based (tree-sitter for C#, stdlib ast for Python) — NOT LLM-assisted — for deterministic roundtrip fidelity
- Reference mappings in src/reference/mappings/ are JSON files that serve as both human-readable docs and machine-readable translation tables
