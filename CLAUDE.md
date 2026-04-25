# unity-py-sim

> **NEVER use `isolation: "worktree"` when spawning agents in this project.** Worktrees consistently land on stale commits (failed 3 out of 3 times). Always run agents in the main working directory. See `data/lessons/testing.md` for details.

Python simulation of Unity's core game engine for bidirectional C# <-> Python translation.

## Purpose

Enable Python-first game development that translates to Unity C# via Ralph loop automation.
Develop games in Python on the work machine, validate C# output on the home machine via Unity MCP.

## Architecture

- **Engine** (`src/engine/`): Python classes mirroring Unity's component system (GameObject, MonoBehaviour, Transform, etc.) with pymunk physics and pygame rendering.
- **Reference** (`src/reference/`): JSON mapping files (classes, methods, patterns) that are both human-readable learning resources and machine-readable translation tables.
- **Translator** (`src/translator/`): AST-based bidirectional C# <-> Python translator using tree-sitter (C#) and stdlib ast (Python). Deterministic — no LLM in the translation pipeline.
- **Gates** (`src/gates/`): Custom validation gates — structural (C# parses), convention (Unity patterns), roundtrip (C# -> Py -> C# equivalence scoring).
- **Assets** (`src/assets/`): Asset manifest system — maps Python asset_ref names to Unity asset paths. Bridges the gap between colored rectangles in Python and real sprites in Unity.
- **Exporter** (`src/exporter/`): Scene serializer and CoPlay MCP script generator — captures running Python scenes to JSON and generates Unity editor scripts for scene reconstruction via CoPlay MCP.
- **Data** (`data/`): Translation corpus, accuracy metrics, asset manifests, asset mappings, lessons learned.

## Key Conventions

- All math backed by numpy (vectors) and pyrr (quaternions)
- Unity lifecycle order: Awake -> Start -> FixedUpdate -> physics -> collision -> Update -> LateUpdate -> render -> destroy
- Naming: Python uses snake_case for methods/fields, Unity uses PascalCase/camelCase — translator handles conversion
- Tests mirror source structure: `src/engine/core.py` -> `tests/engine/test_core.py`

## Testing

```bash
python -m pytest tests/ -v              # full suite
python -m pytest tests/engine/ -v       # engine only
python -m pytest tests/translator/ -v   # translator only
```

### Post-Task Independent Validation (MANDATORY — DO NOT SKIP)

> **BLOCKING REQUIREMENT:** After completing ANY feature or engine task, you MUST spawn a separate validation agent BEFORE marking the task as complete or moving to the next task. This is NOT optional. If you find yourself about to start the next task without having spawned a validation agent, STOP and spawn one first. The implementing agent must NEVER write its own validation tests.

This rule exists because the agent that wrote the code has blind spots about its own assumptions (see `data/lessons/testing.md`). This has been reinforced by the user — never skip this step.

**Process:**
1. Implement the feature, commit it
2. **IMMEDIATELY** spawn a new agent (do not proceed to any other work) with these rules:
   - **NEVER use `isolation: "worktree"`** — worktrees in this project consistently land on stale commits (see `data/lessons/testing.md`). Run in the main working directory instead.
   - **NEVER read existing test files** in `tests/` — they were written by the implementing agent and will bias assumptions. Only read `src/` and `examples/` source code.
   - Derive contract tests from **Unity documentation**, not from what the code does
   - Write **integration tests** (run through `app.run()` game loop)
   - Write **contract tests** (verify Unity behavioral specs, not implementation details)
   - Write **mutation tests** (monkeypatch breakage, prove tests catch it)
   - Place tests in `tests/integration/`, `tests/contracts/`, `tests/mutation/`
   - Run the full test suite to verify no regressions
3. The validation agent must NOT modify any `src/` files — tests only
4. Review the agent's findings before proceeding to the next task
5. **If the validation agent finds bugs, fix them before moving on**

## Ralph Loop

```bash
~/ralph-universal/ralph.sh --dry-run    # validate setup
~/ralph-universal/ralph.sh 20           # run 20 iterations
~/ralph-universal/ralph-plan.sh         # read-only analysis
```

## Playtest

Always use the playtest wrapper — it auto-records errors to `data/lessons/`:
```bash
python tools/playtest.py breakout        # visual
python tools/playtest.py pong            # visual
python tools/playtest.py fsm_platformer  # visual
python tools/playtest.py breakout --headless --frames 300  # headless
```

## Lessons

Before creating or modifying examples, read the relevant lesson files:
- `data/lessons/gotchas.md` — engine API pitfalls and behavioral differences
- `data/lessons/patterns.md` — what translates well vs poorly
- `data/lessons/testing.md` — testing strategy lessons (worktree staleness, unit vs integration, contract design)
- `D:/Projects/ralph-universal/lessons/` — cross-project lessons (filtered by `applies-to: gamedev`)

## Cross-Machine Workflow

1. This machine: Python development, simulator, translator, local gates
2. Push to GitHub: `dscherm/unity-py-sim`
3. Home machine: `dotnet build` on generated C#, Unity-MCP runtime testing (CoplayDev + IvanMurzak)

## Auto-Commit Policy

When work is complete and the test suite passes, stage the relevant files (`git add <paths>`) before ending your turn. The Stop hook in `.claude/settings.json` will auto-commit anything staged with a generated message — you do **not** need to ask the user before committing.

- Only stage files that belong to the just-completed unit of work; never `git add -A`.
- Never auto-commit `.claude/settings.local.json`, `.ralph/` runtime files, or generated `data/generated/**` artifacts (those need explicit user approval).
- If tests fail, do **not** stage. Fix or surface the failure first.
- Pushing to remote still requires explicit user approval.
