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

### Gap B2 — Dynamic-field name mismatch in `inst.<attr>` access (PascalCase instead of camelCase)

**Symptom**: 5 compile errors in GameManager.cs (lines 111, 112, 115, 119, 123):
```
GameManager.cs(111,22): error CS1061: 'GameManager' does not contain a definition
for 'ScoreText' and no accessible extension method 'ScoreText' accepting a first
argument of type 'GameManager' could be found
```
And 4 more for `LivesText` and `StatusText`.

**Root cause**: Python source `inst._score_text.text = ...` (where `inst: GameManager` is a local variable holding the singleton). The translator declares the dynamic field correctly as `[SerializeField] private Text scoreText;` (camelCase, underscore stripped) at lines 10-12, but emits the *use* as `inst.ScoreText` (PascalCase) at lines 111-123.

The `_setup_ui()` method translates `self._score_text = ...` → `scoreText = ...` correctly because `self.X` resolves through the symbol table. But `inst._score_text` (where `inst` is a typed local variable, not `self`) doesn't go through the same symbol-table lookup — it falls back to default attribute-access behavior which PascalCases the name.

**Class of bug**: same family as memory `[Underscore-prefixed field name mismatch between declaration and call site (Passage.cs)]` (S12-3). That fix targeted declaration ↔ use mismatch on `self.X`. This case extends to `inst.X` where inst is typed.

**Workaround for this deploy**: patched `data/generated/breakout_project/Assets/_Project/Scripts/GameManager.cs` directly to use camelCase. Counts as 1 manual intervention.

**Fix at source (M-1 follow-up)**: when emitting attribute access `obj.attr`, look up the type of `obj` (declared by type-annotation or singleton-pattern); if the type matches a known class with an `attr` field/dynamic-field, use that class's symbol table instead of default PascalCase. Track as a follow-up task before counting Breakout E2E as fully shipped.

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

### Gap B4 — Sprite path mismatch between mapping JSON and scaffolder

**Symptom**: SpriteRenderer on Ball/Paddle/Brick had `sprite: "None"` after `GeneratedSceneSetup.Execute()`. SceneView frame on each object showed solid color but no sprite. Game view from camera was solid background.

**Root cause**: `data/mappings/breakout_mapping.json` declared `unity_path: "Assets/Sprites/<name>.png"` but `src/exporter/project_scaffolder.py:_DEFAULT_FOLDERS` puts assets at `Assets/Art/Sprites/<name>.png`. `AssetDatabase.LoadAllAssetsAtPath("Assets/Sprites/ball.png")` returned an empty array.

**Fix shipped (source)**: changed `breakout_mapping.json`, `space_invaders_mapping.json`, `angry_birds_mapping.json` from `Assets/Sprites/` → `Assets/Art/Sprites/` to match the scaffolder. `flappy_bird_mapping.json` was already correct (which is why FU-2 worked).

**Counts**: 0 manual interventions (caught and fixed at source before MAN-1 close).

### Gap B5 — sprite_name `_0` suffix only valid in Multiple/sprite-sheet import mode

**Symptom**: Even after Gap B4 fix, sprites still loaded as null. Stack: `LoadAllAssetsAtPath("Assets/Art/Sprites/ball.png").OfType<Sprite>().FirstOrDefault(s => s.name == "ball_0")` returned null.

**Root cause**: The mapping declared `sprite_name: "ball_0"` (Multiple-mode sprite-sheet naming), but the scaffolder's generated `.png.meta` uses `spriteMode: 1` (Single-mode), where the loaded Sprite's name equals the texture name (`"ball"`, no `_0`).

**Fix shipped (source)**: `src/exporter/coplay_generator.py:261-269` now emits a fallback — if the named sub-sprite lookup returns null, fall back to `AssetDatabase.LoadAssetAtPath<Sprite>(unity_path)` which returns the main Sprite for Single-mode imports. Both modes now work.

**Counts**: 0 manual interventions.

### Gap B6 — `floatValue` used unconditionally for int-typed SerializedFields

**Symptom**: 30+ `"type is not a supported float value"` errors during `GeneratedSceneSetup.Execute()`. Stack pointed to `UnityEditor.SerializedProperty:set_floatValue (single)`. Errors did not abort scene creation but silently dropped int field values, leaving Brick.points and Brick.health as 0 — bricks would be destroyed instantly with no scoring.

**Root cause**: `src/exporter/coplay_generator.py:705-708` filtered numeric fields and always emitted `prop.floatValue = ...`. Brick declares `public int points; public int health;`, so the SerializedProperty's propertyType is Integer. Unity throws `InvalidOperationException` on `floatValue` setter against an Integer property. The error format prints "type" because of how Unity 6 stringifies the property type in the message.

**Fix shipped (source)**: dispatch on Python value type — `int` → `intValue`, `float` → `floatValue`. Bool already filtered out before this point.

**Verification**: post-fix, `get_game_object_info` on `Brick_0_0` returned `points: 30, health: 1` (matching Python source).

**Counts**: 0 manual interventions (caught and fixed at source).

## Update log

- 2026-04-24: regen + gap B1 fix shipped at source. Unity-side deploy + playtest pending.
- 2026-04-25: home-machine deploy completed. Gaps B4 (sprite path), B5 (sprite name suffix), B6 (int vs float SerializedProperty) found and fixed at source. Scene renders, sprites visible, Play mode runs without errors. M-1 closed at 1 manual intervention (Gap B2 GameManager.cs camelCase patch — pending source fix).

## Pending source fixes (from this deploy)

- Gap B2 — translator must look up `inst.<attr>` against the typed local's class symbol table to use camelCase rather than default PascalCase. Class of bug: same family as S12-3.
- Gap B3 — validator should accept `Main Camera` (Unity's default) or `MainCamera`. Currently false-positive.
- Unity 6 deprecation — migrate `FindObjectOfType<T>()` (used by `_inject_awake_fallback` and validator) to `FindFirstObjectByType<T>()` to match the FU-4 `FindObjectsByType` migration.
