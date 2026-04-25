# Breakout — Home-Machine Deploy Notes (M-1)

Tracking gaps surfaced during the home-machine deploy of `data/generated/breakout_project/` for M-1 (Coverage and Maturation phase, 2026-04-24+).

This file is the M-1 equivalent of `data/lessons/flappy_bird_deploy.md`.

## Pipeline regen (this machine)

Commands run:
```
.venv/Scripts/python -m tools.pipeline breakout --validate
.venv/Scripts/python -m tools.gen_coplay \
  --runner examples/breakout/run_breakout.py \
  --mapping data/mappings/breakout_mapping.json \
  --namespace Breakout \
  --output data/generated/breakout_project/Assets/Editor/GeneratedSceneSetup.cs \
  --validation-output data/generated/breakout_project/Assets/Editor/GeneratedSceneValidation.cs \
  --source examples/breakout/breakout_python
```

Results:
- 5 translated C# files (BallController, Brick, GameManager, PaddleController, PowerupType)
- 30 files in scaffold (incl. ProjectSettings, Packages/manifest.json, sprites)
- Structural gate 5/5 pass
- 87 GameObjects serialized to GeneratedSceneSetup.cs
- 3 sprite mappings, 5 translated classes in registry

## Gaps surfaced (2026-04-24)

### Gap B1 — `com.coplaydev.coplay` missing from manifest.json

**Symptom**: `list_unity_project_roots` discovered the breakout_project but `get_unity_editor_state` and `check_compile_errors` both failed with "Unity Editor is not running at the specified project root." The CoPlay MCP plugin requires the `com.coplaydev.coplay` package to be installed in the project; without it the editor doesn't expose MCP endpoints.

**Root cause**: `src/exporter/project_scaffolder.py:_DEFAULT_PACKAGES` did not include `com.coplaydev.coplay`. This was the same FU-2 manual intervention from Flappy Bird ("added com.coplaydev.coplay to manifest.json") that was never fixed at the source.

**Fix shipped**: added `"com.coplaydev.coplay": "https://github.com/CoplayDev/unity-plugin.git#beta"` to `_DEFAULT_PACKAGES`. Future regens of any game now include the package by default.

**Counts**: 1 manual intervention saved for every future deploy.

## Manual interventions remaining (target ≤5 per SUCCESS.md MAN-1)

After Unity opens the project and installs CoPlay:

1. *(verify)* CoPlay plugin auto-installs from the patched manifest (no human click needed in theory; Unity may prompt for Git Trust on first open)
2. **Focus Unity Editor on `data/generated/breakout_project/`** so it picks up the manifest change and installs CoPlay (one-time per checkout)
3. **Run Tools → Setup Generated Scene** menu item from CoPlay to execute `GeneratedSceneSetup.cs`
4. *(maybe)* Re-wire any Inspector references that didn't auto-populate
5. **Press Play** and verify gameplay

## Acceptance for M-1

Per `SUCCESS.md` MAN-1: the bar is "≤5 manual interventions" to playable game. Tracking against that target. Will update once home-machine playtest completes.

## Update log

- 2026-04-24: regen + gap B1 fix shipped at source. Unity-side deploy + playtest pending.
