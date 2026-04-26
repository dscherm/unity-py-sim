# Fix Plan — Stages 2-6: Compilable → Playable Unity Pipeline

Generated from end-to-end research (2026-04-08).
Goal: `python -m src.exporter.scaffold --game breakout` → Unity project that opens, compiles, and plays.

---

## Critical — Stage 2: Translator Runtime Gaps

These prevent generated C# from functioning at runtime even though it compiles.

- [ ] **[S2-1] SerializeField emission for Inspector-wirable fields** — Template `monobehaviour.cs.j2` emits `public object field;` for all fields. Fields referencing MonoBehaviours, GameObjects, or prefabs must emit `[SerializeField] private T field;` with concrete types. Update `python_parser.py` to capture type annotations into `PyField`, update `python_to_csharp.py` field emission to detect MonoBehaviour subclass types and List→array conversions. Test: GameManager.cs should have `[SerializeField] private Ghost[] ghosts;` not `public object ghosts;`. ~8 test failures currently.
- [ ] **[S2-2] Parameter shadowing — emit `this.` for field assignments** — `GameManager.SetScore(int score)` emits `score = score;` instead of `this.score = score;`. Translator must detect when method parameter name matches a field name and prefix with `this.`. File: `python_to_csharp.py` method body translation. Test: Space Invaders GameManager score/lives methods.
- [ ] **[S2-3] Singleton pattern → serialized field references** — `GameManager.instance` pattern compiles but requires scene load ordering. For dependent classes, emit `[SerializeField] private GameManager gameManager;` instead of `GameManager.instance` access. Detect singleton pattern (`instance = self` in awake), rewrite cross-class references. File: semantic_layer.py (new).
- [ ] **[S2-4] Ternary operator condition dropped to `true`** — `Projectile.cs:31` has `true ? other.GetComponent<Bunker>() : null` — condition was stripped. Debug the ternary translation in `_translate_py_expression()`. Test: conditional expressions with object checks.
- [ ] **[S2-5] Cross-file function calls unqualified** — Module-level functions in other files emit unqualified: `MaybeSpawnPowerup()` instead of `Powerup.MaybeSpawnPowerup()`. Fix `project_translator.py` post-process to qualify cross-file function calls using the global class registry. Test: Space Invaders uses cross-file calls.
- [ ] **[S2-6] Constants injected into enum blocks** — `project_translator.py:173` replaces first `{\n` in file. If first declaration is an enum, constants go inside it. Add enum detection before injection. Test: any file with enum + module constants.
- [ ] **[S2-7] Reset() method name collision with Unity lifecycle** — Python `def reset(self):` becomes `public void Reset()` which Unity auto-calls during editor AddComponent. Rename to `ResetState()` or `ResetGame()` in translator. Test: Pacman GameManager reset flow.
- [ ] **[S2-8] Underscore loop variable breaks UPPER_CASE constants** — `for _ in range(N)` translation does `.replace("_", _i)` which strips underscores from `GRID_COLS` → `GRIDCOLS`. Use word-boundary regex. Test: Space Invaders invader grid setup.

## High — Stage 3: Project Scaffolder

- [ ] **[S3-1] Create project_scaffolder.py** — New file `src/exporter/project_scaffolder.py`. Generates Unity project folder structure from `project_structure` in asset mapping (already defined in `data/mappings/pacman_mapping.json`). Create: `Assets/_Project/Scripts/`, `Assets/_Project/Prefabs/`, `Assets/_Project/Scenes/`, `Assets/Art/Sprites/`, `Assets/Editor/`, `Packages/`, `ProjectSettings/`. Add CLI: `python -m src.exporter.scaffold --game <name> --output <dir>`.
- [ ] **[S3-2] Generate Packages/manifest.json** — Read `_required_packages.json` from translator output (already emitted by `project_translator.py`). Map package names to Unity registry format with version pins. Always include: `com.unity.render-pipelines.universal`, `com.unity.2d.sprite`. Conditionally: `com.unity.inputsystem` (if new input detected), `com.unity.ugui` (if UI used), `com.unity.textmeshpro` (if TMPro used).
- [ ] **[S3-3] Generate ProjectSettings/TagManager.asset** — YAML file with tags and sorting layers extracted from scene JSON export or asset manifest. Format: Unity YAML with `%YAML 1.1`, `%TAG !u! tag:unity3d.com,2011:`. Populate `tags` array and `layers` array (user layers start at index 6). Extract from CoPlay generator's tag/layer logic (already implemented in `coplay_generator.py`).
- [ ] **[S3-4] Generate ProjectSettings/Physics2DSettings.asset** — Extract gravity, layer collision matrix from scene export physics section. Already captured by `scene_serializer.py` in `physics.ignore_collision_pairs`. Convert to Unity's 32x32 collision matrix format.
- [ ] **[S3-5] Copy translated C# files to Assets/_Project/Scripts/** — Read translator output dict, write each file to scripts directory. Skip `__init__.cs` and `maze_data.cs` (non-class files). Validate each with structural gate before copying.
- [ ] **[S3-6] Generate ProjectSettings/ProjectVersion.txt** — Single line: `m_EditorVersion: 2022.3.0f1` (or configurable Unity version). This is required for Unity to open the project.

## High — Stage 4: Scene Construction & Prefabs

- [ ] **[S4-1] Prefab candidate detection** — Analyze Python source: anything created via `Instantiate()` or dynamically in loops is a prefab candidate. Scene-setup objects (created in `setup_scene()`) are scene objects. Create `src/exporter/prefab_detector.py` that classifies GameObjects. Test: Pacman pellets/ghosts are prefabs, maze walls are scene objects.
- [ ] **[S4-2] Generate .prefab YAML stubs** — For each prefab candidate, generate a minimal .prefab YAML file with Transform + MonoBehaviour components. Use deterministic GUIDs from class name hash (sha256 → first 32 hex chars). Place in `Assets/_Project/Prefabs/`. These are stubs — real prefabs will be populated via CoPlay MCP.
- [ ] **[S4-3] Update CoPlay generator for prefab instantiation** — Current generator creates bare GameObjects. Update to: load prefabs from `Assets/_Project/Prefabs/`, use `PrefabUtility.InstantiatePrefab()` for scene objects that match a prefab, only create bare GameObjects for unique scene objects. Fix the Main Camera assumption (create if missing).
- [ ] **[S4-4] Wire SerializeField references in CoPlay generator** — Current generator comments out MonoBehaviour field assignments (line 382). Implement proper wiring: after all GameObjects are created, iterate MonoBehaviour fields, find target GameObjects by name, use `SerializedObject` to set references. Handle arrays (`Ghost[] ghosts`).
- [ ] **[S4-5] Generate minimal Scene.unity YAML** — Create a scene file with camera + directional light + empty root objects for the game hierarchy. This lets Unity open the scene immediately. Full population happens via CoPlay generator's Execute().

## Medium — Stage 5: Validation Pipeline

- [ ] **[S5-1] Add dotnet build gate** — Create `src/gates/dotnet_gate.py`. Generate a minimal `.csproj` referencing Unity stub DLLs (or use `dotnet-script`). Run `dotnet build` on generated project. Parse errors. This enables compilation validation without Unity installed. Test: Breakout project should compile with 0 errors.
- [ ] **[S5-2] End-to-end scaffold + gate pipeline** — Wire scaffolder into `project_translator.py`: after translation, call `scaffold_project()`, then run structural gate + convention gate + dotnet gate on output. Report pass/fail per file. CLI: `python -m src.translator.project_translator --game breakout --scaffold --validate`.
- [ ] **[S5-3] CoPlay MCP validation script** — Generate a second editor script that validates the scene after setup: checks all SerializeField references are non-null, verifies tag/layer assignments, counts expected GameObjects. Run via CoPlay MCP on home machine.

## Low — Stage 6: Integration & Polish

- [ ] **[S6-1] Semantic translation layer** — Create `src/translator/semantic_layer.py`. Post-process translated C# to rewrite patterns that compile but don't run: `GameObject("name")` → hierarchy lookup or prefab instantiation, simulator-only code (pygame/pymunk) → strip, Python type unions (`T | None`) → nullable reference. Run after AST translation, before file write.
- [ ] **[S6-2] Full pipeline CLI** — Single command: `python -m src.pipeline --game pacman_v2 --output data/generated/pacman_v2_project/ --validate`. Runs: translate → semantic layer → scaffold → prefab detect → CoPlay generate → structural gate → convention gate → dotnet gate. Outputs unified report.
- [ ] **[S6-3] Pipeline validation on Breakout (simplest game)** — Run full pipeline on Breakout (5 files, simple physics). Deploy to home machine. Verify: opens in Unity, compiles, paddle moves, ball bounces, bricks break. Record manual interventions. Target: <3 manual steps.
