# CoPlay Generator & Translator Gaps — Flappy Bird → Unity

Discovered 2026-04-21 while getting the generated flappy_bird_project to build + render in Unity. Each item below was a distinct compile or runtime blocker. Fixes applied to the generated project manually via CoPlay MCP; **all 8 need to be applied at the source** (`src/translator/python_to_csharp.py`, `src/exporter/coplay_generator.py`, `src/exporter/project_scaffolder.py`) so regeneration stops clobbering them.

## Compile blockers (script translator)

### 1. `List<T>` types emit `List<object>` instead of inferring element type
**Where:** `src/translator/python_to_csharp.py` — field type inference from Python `list[Sprite]` or assignment context.
**Symptom:** `Player.cs:52 error CS0266: Cannot implicitly convert type 'object' to 'UnityEngine.Sprite'`
**Fix in generated file:** `public List<object> sprites` → `public List<Sprite> sprites`
**Root fix:** infer List element type from Python annotation, usage (`sprites[i]` assigned to Sprite-typed field), or default to a project-configured reference type set.

### 2. `List<>` emitted without `using System.Collections.Generic;`
**Where:** `python_to_csharp.py` — `extra_using` collection.
**Symptom:** `CS0246: The type or namespace name 'List<>' could not be found`
**Fix in generated file:** prepend `using System.Collections.Generic;`
**Root fix:** scan translated body for `List<`, `Dictionary<`, `HashSet<` tokens and add the corresponding using to `extra_using`.

## Compile blockers (CoPlay scene generator)

### 3. Namespace prefix without `namespace` wrapper
**Where:** `src/exporter/coplay_generator.py` — `--namespace FlappyBird` default emits `FlappyBird.Player`, `FlappyBird.GameManager`, etc. in both `GeneratedSceneSetup.cs` and `GeneratedSceneValidation.cs`. But translated scripts live in the global namespace.
**Symptom:** 5+ `CS0246: The type or namespace name 'FlappyBird' could not be found` errors.
**Fix in generated file:** `sed -i 's/FlappyBird\.//g' Assets/Editor/GeneratedScene*.cs`
**Root fix:** either emit `namespace <X> { … }` wrappers in the translated scripts, or stop prefixing the generated editor scripts. Drop the default.

### 4. Inline-defined MonoBehaviours in `run_*.py` never translated
**Where:** `src/translator/project_translator.py` translates `examples/<game>/<game>_python/*.py` but skips `run_<game>.py`. `PlayButtonHandler` and `QuitHandler` live inline in `run_flappy_bird.py`, get serialized into the scene graph, but no `.cs` file exists for them.
**Symptom:** `CS0246: The type or namespace name 'PlayButtonHandler' could not be found`
**Fix in generated file:** hand-authored `Assets/_Project/Scripts/PlayButtonHandler.cs` stub.
**Root fix:** either (a) translate inline classes from the run file too, (b) split them out into the `<game>_python/` package before translation, or (c) have the scene serializer filter out components whose class wasn't translated.

## Runtime blockers (scaffolder + scene generator)

### 5. Sprite mapping `unity_path` doesn't match scaffolder output directory
**Where:** `data/mappings/flappy_bird_mapping.json` uses `Assets/Sprites/Bird_01.png`; `src/exporter/project_scaffolder.py:_copy_project_sprites` writes to `Assets/Art/Sprites/`. `coplay_generator.py` emits `AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/…")` which silently returns null.
**Symptom:** `SpriteRenderer.sprite == null`, scene renders as camera background color only.
**Fix in generated file:** `sed -i 's|"Assets/Sprites/|"Assets/Art/Sprites/|g' Assets/Editor/GeneratedSceneSetup.cs`
**Root fix:** align mapping JSON convention with scaffolder output path (prefer `Assets/Art/Sprites/` as the canonical location and rewrite the 5 mapping files), OR parameterize scaffolder to put PNGs wherever mapping says.

### 6. Parent/child relationships not preserved in scene setup
**Where:** `src/exporter/coplay_generator.py` — emits `new GameObject("Top")` etc. without calling `.transform.SetParent(parentGo.transform)`. Python side had `top_go.transform.set_parent(prefab.transform)` but this info is dropped.
**Symptom:** Pipes prefab has no Top/Bottom/Scoring children → Pipes.Update moves an empty container, sprites stay at world origin. Visible as "pipes floating / not scrolling."
**Fix in generated file:** call `mcp__coplay-mcp__parent_game_object` per child.
**Root fix:** scene serializer + generator must round-trip `transform.parent` references by name.

### 7. `Camera.orthographic` flag not translated
**Where:** `src/exporter/coplay_generator.py` — sets `orthographicSize` but leaves `orthographic` = false (Unity default).
**Symptom:** 2D sprites at z=0 are invisible behind a perspective camera at origin. Looks like baby-blue background color only.
**Fix in generated file:** `set_property MainCamera/Camera/orthographic=true`; also reposition camera z=-10 so it's in front of sprites.
**Root fix:** detect `orthographic_size != None` (or any `Camera.orthographic` explicit set) in Python → emit `cam.orthographic = true;` + `transform.position = new Vector3(0, 0, -10);` in the generator.

## Scaffolder issues

### 8. `TagManager.asset` YAML is malformed
**Where:** `src/exporter/project_scaffolder.py:_write_tag_manager`.
**Symptoms:**
- `Unable to parse file ProjectSettings/TagManager.asset: Parser Failure at line N: Expect ':' between key and value within mapping`
- Empty layer slots emitted as bare `-\n` (null scalar) instead of `- ""` (empty-string scalar).
- `sortingLayers:` used instead of Unity 6's expected `m_SortingLayers:`.
- Missing `serializedVersion: 2` under `TagManager:`.
**Fix in generated file:** rewrote with `- ""` empty strings, `m_SortingLayers`, `serializedVersion: 2`.
**Root fix:** update the template in `_write_tag_manager` to match Unity 6 canonical format.

## Secondary observations (not blockers)

- `FindObjectsOfType<T>()` is deprecated in Unity 6 — `FindObjectsByType<T>(FindObjectSortMode.None)` is the replacement. Current translator emits the deprecated form → warning CS0618. Not blocking but worth updating.
- `EditorSceneManager.NewScene` fails during Play mode with `InvalidOperationException`. The `SceneSetupMenu.cs` wrapper should refuse to run mid-play.
- `save_scene` MCP tool saved `Scene.unity` to `Assets/` root rather than the active scene's `Assets/_Project/Scenes/` path — future scene saves should pass a full path.
- `Player.OnTriggerEnter2D` throws `NullReferenceException` on `gameManager.GameOver()` — the `[SerializeField] private GameManager gameManager` on Player is null because the generator doesn't wire inter-MonoBehaviour field references. Related to (6): field references by GameObject name need to round-trip through scene serialization.

## Fix priority

P0 (block compile): 1, 2, 3, 4
P0 (block render): 5, 6, 7, 8
P1: NullReferenceException wiring (Player.gameManager, likely others — related to gap 6's parent/ref class)
P2: FindObjectsByType migration, scene-save-path, editor-guard on NewScene
