# unity-py-sim

Python simulation of Unity's core game engine for bidirectional C# <-> Python translation.

## Purpose

Enable Python-first game development that translates to Unity C# via Ralph loop automation.
Develop games in Python on the work machine, validate C# output on the home machine via Unity MCP.

## Architecture

- **Engine** (`src/engine/`): Python classes mirroring Unity's component system (GameObject, MonoBehaviour, Transform, etc.) with pymunk physics and pygame rendering.
- **Reference** (`src/reference/`): JSON mapping files (classes, methods, patterns) that are both human-readable learning resources and machine-readable translation tables.
- **Translator** (`src/translator/`): AST-based bidirectional C# <-> Python translator using tree-sitter (C#) and stdlib ast (Python). Deterministic — no LLM in the translation pipeline.
- **Gates** (`src/gates/`): Custom validation gates — structural (C# parses), convention (Unity patterns), roundtrip (C# -> Py -> C# equivalence scoring).
- **Data** (`data/`): Translation corpus, accuracy metrics, lessons learned.

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

### Post-Task Independent Validation (MANDATORY)

After completing any feature or engine task, you MUST spawn a **separate agent** to write tests for it. The implementing agent must NOT write its own validation tests. This rule exists because the agent that wrote the code has blind spots about its own assumptions (see `data/lessons/testing.md`).

**Process:**
1. Implement the feature, commit it
2. Spawn a new agent with these rules:
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
