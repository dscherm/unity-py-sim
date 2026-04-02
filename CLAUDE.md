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

## Lessons (READ BEFORE BUILDING)

Before creating or modifying examples, read these:

**Engine gotchas** (`data/lessons/gotchas.md`):
- `GameObject._registry` doesn't exist — use `GameObject.find()` and `GameObject.find_game_objects_with_tag()`
- Unity 6 uses `linearVelocity` not `velocity`
- Python engine Input API is legacy-style; Unity projects may use new Input System
- Animator controllers, scene objects, prefabs are Unity assets — not translatable by code

**Translation patterns** (`data/lessons/patterns.md`):
- Easy: class inheritance, field declarations, lifecycle methods
- Medium: for loops, list operations, property accessors (translator produces rough output)
- Hard: Input System, Physics2D.OverlapCircle, animator wiring, SerializeField

**Cross-project lessons** (`D:/Projects/ralph-universal/lessons/`):
- `unity-asset-runtime-mismatch` — modify .controller assets via MCP, not Editor scripts
- `scene-object-pixel-values` — verify world-space transforms after automated setup
- `credit-exhaustion-phantom-passes` — API credit errors create phantom "pass" iterations
- `bootstrap-overwrites-config` — bootstrap.py overwrites existing ralph.config.json
- `small-iterations-succeed` — keep changes to 1-5 files per task

## Cross-Machine Workflow

1. This machine: Python development, simulator, translator, local gates
2. Push to GitHub: `dscherm/unity-py-sim`
3. Home machine: `dotnet build` on generated C#, Unity-MCP runtime testing (CoplayDev + IvanMurzak)
