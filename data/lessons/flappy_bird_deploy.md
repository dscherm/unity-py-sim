# Flappy Bird Unity Deployment — First Home-Machine Playtest

Session date: 2026-04-22. First end-to-end `data/generated/flappy_bird_project/`
playtest on the Windows Unity 6 home machine using CoPlay MCP for in-editor
diagnostics. Progresses plan.md "Flappy Bird Task 8" toward `passes: true`.

## Outcome

After 6 in-editor fixes via CoPlay MCP (all persisted to `Scene.unity` in
Edit mode), the scene is playable: full-width tiled background, sky /
cityscape / grass / ground all render, pipes spawn from the right and
scroll, bird responds to gravity and Space key, `Pipes(Clone)` children
(Top / Bottom / Scoring) round-trip through the prefab.

The 6 manual fixes each map to a specific source gap that needs upstreaming
so regeneration via `tools/gen_flappy_coplay.py` produces a working scene
without hand-patching.

## Fix-by-fix gap catalog

### 1. Game starts frozen (`Time.timeScale = 0`)

**Symptom:** Press Play → bird renders at (-2, 0) with rotation.z ≈ 25°, then
never moves. `direction.y` stays at 5.0 exactly; `spriteIndex` stays 0
forever (InvokeRepeating doesn't fire either).

**Root cause:** `GameManager.Start()` calls `Pause()` which sets
`Time.timeScale = 0.0f`. In the original zigurous Flappy Bird, the UI
`PlayButton.onClick` triggers `GameManager.Play()` to un-pause. That click
handler was wired by `PlayButtonHandler`, an inline MonoBehaviour defined in
`run_flappy_bird.py` — correctly filtered out by coplay gap 4's
translated-class registry (it has no `.cs` counterpart). Without it, there's
no path to un-pause.

**Fix applied in-editor:** added `Assets/_Project/Scripts/AutoStart.cs` —
a MonoBehaviour whose `Start()` calls `GameManager.Instance.Play()`.
Attached to a new `AutoStart` GameObject in the scene.

**Upstream fix needed (coplay_generator):** when the scene graph has a UI
`Button` and a `GameManager.Play()` method exists, emit
`button.onClick.AddListener(() => gameManager.Play())` wiring. Alternatively
the scaffolder could generate the `AutoStart` helper as a standard fixture
for `run_*.py`-bootstrapped games.

### 2. Player NullReferenceException on trigger

**Symptom:** `Player.cs:60 gameManager.GameOver()` throws NRE immediately
when bird touches any Obstacle trigger.

**Root cause:** The on-disk `Player.cs` has a manual patch from commit
`00c9ca0` introducing `[SerializeField] private GameManager gameManager`
plus `gameManager.GameOver()` call sites. The **current translator output**
uses the singleton pattern (`GameManager.instance.GameOver()`) — no
SerializeField needed — so the manual patch is now actively harmful.

**Fix applied in-editor:** `set_property Player.gameManager = GameManager`
(wired the scene object). This worked because both objects are in the scene.

**Upstream fix needed:** regenerate `Player.cs` + `GameManager.cs` to
discard the manual patches; the fresh translator output is correct. Run
`python -m src.translator.project_translator examples/flappy_bird/flappy_bird_python/`.
Alternatively, teach the CoPlay generator to emit cross-GameObject
SerializeField wiring for any MonoBehaviour-typed serialized field whose
target class exists in the scene (broader fix; covers future cases where a
SerializeField is genuinely intended).

### 3. Spawner never spawns pipes (after one round)

**Symptom:** `Spawner.prefab` wired to the scene GameObject named "Pipes".
On `GameManager.Play()` startup, the cleanup loop:

```csharp
var pipes = FindObjectsOfType<Pipes>();
for (int i = 0; i < pipes.Length; i++) Destroy(pipes[i].gameObject);
```

destroys **every** Pipes, including the scene-object template.
`Spawner.prefab` is now a dangling/null reference — no more pipes spawn.

**Fix applied in-editor:**
`set_property Spawner.prefab = Assets/_Project/Prefabs/Pipes.prefab`
(wired to the asset on disk, which survives the Destroy loop).

**Upstream fix (SHIPPED in this session):** `src/exporter/coplay_generator.py`
GameObjectRef wiring now checks if the target name matches a prefab class in
the `prefab_manifest` and emits
`AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Project/Prefabs/X.prefab")`
instead of the scene-object variable.  Tests:
`tests/exporter/test_coplay_prefab.py::TestPrefabAssetSerializeFieldRef`.

### 4. Background / Ground / Ceiling too narrow

**Symptom:** Sprites render as narrow strips in the screen center;
"disappears and reappears" every few seconds due to the Parallax script
scrolling a 6-unit-wide sprite past a 17.78-unit-wide viewport (16:9
orthographic size 5).

**Root cause:** Scene serializer writes `SpriteRenderer.drawMode = Simple`
(Unity's default) and the sprite's intrinsic size (6.0 × 10.67 for the
Background PNG; 7.0 × 2.33 for Ground). CoPlay generator copies those values.
When the Parallax script scrolls the sprite past the viewport's left edge,
the sprite goes fully off-screen before the wrap kicks in — blue camera
background color shows through.

**Fix applied in-editor:** For Background / Ground / GroundParallax:
```
SpriteRenderer.drawMode = Tiled
SpriteRenderer.size     = (30, <sprite_height>)
```
Tiled drawMode makes Unity repeat the sprite texture across the 30-unit
width, so the viewport is always fully covered.

**Upstream fix needed (future):** scene serializer should detect when a
sprite's `extent.x < viewport.x * 1.5` (or expose a
`spriteRenderer.draw_mode = "tiled"` + explicit `tile_size` setting in
the Python engine).  CoPlay generator then emits
`sr.drawMode = SpriteDrawMode.Tiled` + appropriate `size`.

### 5. Camera aspect mismatch (portrait sprite in landscape viewport)

**Symptom:** Flappy Bird's sprite art assumes ~288×512 portrait
(9:16 aspect ≈ 0.56). User's Unity Game view defaulted to 16:9 (~1.78)
→ sprites appear tiny horizontally, vast horizontal expanse of sky visible.

**Root cause:** Project scaffolder doesn't configure a Game-view aspect
preset; Unity picks the default (Free Aspect → usually landscape). The
Python simulator uses a portrait window (`pygame.display.set_mode((288, 512))`).

**Fix applied in-editor:** user manually changes Game view aspect to 9:16
portrait via the dropdown (or leaves as-is and accepts the landscape look
with tiled backgrounds — the fix above makes landscape tolerable).

**Upstream fix needed (future):** scaffolder should emit a default Game
view aspect preset matching the Python simulator's window size, either via
an editor script that calls `EditorWindow.GetGameView().SetSize(...)` or
via `ProjectSettings/` settings.

### 6. Player.sprites list empty after scene setup

**Symptom:** Bird never animates. `AnimateSprite()` runs via
`InvokeRepeating` every 0.15s but `sprites.Count == 0` so the sprite never
changes. (Not a NRE in our translator output because `List<>.Count` on an
empty list is 0, not null.)

**Root cause:** CoPlay generator SerializeField wiring handles scalar
types (gravity, strength, tilt) and single GameObjectRef / GameObjectRefArray,
but NOT sprite-asset lists. The scene serializer has no mechanism to
represent "this field is a List<Sprite> loaded from these asset paths."

**Fix applied in-editor:** added
`Assets/Editor/WireBirdSprites.cs` that loads Bird_01/02/03 via
`AssetDatabase.LoadAssetAtPath<Sprite>` and wires them into the
`sprites` SerializeField via SerializedObject.

**Upstream fix needed (future):** scene serializer + CoPlay generator
need a new `_type: "SpriteArrayRef"` with asset paths; generator emits the
`AssetDatabase.LoadAssetAtPath<Sprite>` + array fill pattern that
`WireBirdSprites.cs` demonstrates.

## Gap 7 — Script .cs.meta GUIDs drift from prefab m_Script refs

Discovered during the second playtest session while diagnosing "pipes
not moving toward the bird."

**Symptom:** Spawner.Spawn() successfully called `Instantiate(prefab)` —
the resulting `Pipes(Clone)` appeared in the hierarchy with its
Top/Bottom/Scoring children — but the clone's root had ONLY a Transform.
The Pipes MonoBehaviour component was missing.  Since Pipes.Update() is
what scrolls the pipe left, every spawn just stacked at the Spawner's
x=8 position forever.  The user saw "the game just keeps adding pipes
to the right side of the screen."

**Root cause:** GUID drift between the scaffolder's prefab output and
Unity's .cs.meta files:

- `Pipes.prefab` m_Script referenced guid `cf73fc57bf8b3384fb060c245c743cab`
  (deterministic from SHA-256 of class name via prefab_generator).
- `Pipes.cs.meta` GUID was `440c45d30e28a1c41bcd8a846a521a22` (random,
  assigned by Unity on first import because the scaffolder didn't write
  `.cs.meta` files — Unity auto-generated them with fresh GUIDs).

Unity couldn't resolve the MonoBehaviour reference when loading the
prefab → silently dropped the component → Instantiate produced a
scriptless shell.

**Fix applied in-editor:** `sed`-equivalent patch to `Pipes.prefab` line
262 — swap the prefab's m_Script guid to match the real .cs.meta guid.
Verified via an editor script `RefreshAndInspect.cs`:
```
Pipes.prefab root now has script: Pipes
```

**Upstream fix (SHIPPED this session):**
- `src/exporter/project_scaffolder.py:_write_cs_meta()` now writes a
  `.cs.meta` beside each scaffolded `.cs`, using
  `_deterministic_guid(f"script:{class_name}")` from prefab_generator.
  Unity honors pre-existing `.meta` files, so the deterministic GUID
  wins over the random one Unity would have generated.
- `src/exporter/prefab_generator.py` MonoBehaviour stub emission now
  writes `m_Script: {fileID: 11500000, guid: <same_deterministic_guid>,
  type: 3}` instead of `fileID: 0` (null script).
- Both sides compute identical GUIDs → prefab resolves the script on
  first project import → Instantiate yields a clone with all its
  MonoBehaviours attached → Update() runs → pipes scroll.

Tests: 4 new cases in
`tests/exporter/test_scaffolder.py::TestScriptMetaDeterministicGuid`
plus an updated assertion in
`tests/exporter/test_prefab_generator.py::test_monobehaviour_for_custom_component`
confirming the GUID round-trip.

## Summary of upstream work

| # | Gap | Severity | Status |
|---|---|---|---|
| 1 | No path to un-pause (UI Play button onClick not wired) | P0 | **SHIPPED** — AutoStart fixture |
| 2 | Awake self-wire fallback for injected singleton SerializeFields | P0 | **SHIPPED** — semantic_layer now adds `if (field == null) field = S.Instance;` to Awake |
| 3 | Prefab-asset references for SerializeField GameObject fields | P0 (blocks spawning) | **SHIPPED** — coplay_generator.py + 4 regression tests |
| 4 | SpriteRenderer Tiled drawMode for wide-viewport sprites | P1 (visual) | **SHIPPED** — Parallax-component heuristic |
| 5 | Game-view aspect preset for portrait games | P2 (cosmetic) | open |
| 6 | Sprite-asset list SerializeField wiring | P1 (animation) | **SHIPPED** — scene serializer emits SpriteArrayRef, generator wires via `sprite_<name>` vars |
| 7 | Deterministic .cs.meta GUIDs matching prefab m_Script refs | P0 (prevents script binding) | **SHIPPED** — this session |

## Commands used in this session (for reproducibility)

```bash
# Regenerate CoPlay scripts
python tools/gen_flappy_coplay.py

# CoPlay MCP operations (from Claude Code):
# - mcp__coplay-mcp__list_unity_project_roots
# - mcp__coplay-mcp__set_unity_project_root <path>
# - mcp__coplay-mcp__play_game / stop_game
# - mcp__coplay-mcp__get_unity_logs
# - mcp__coplay-mcp__get_game_object_info <path>
# - mcp__coplay-mcp__capture_scene_object
# - mcp__coplay-mcp__set_property / create_game_object / add_component
# - mcp__coplay-mcp__save_scene
# - mcp__coplay-mcp__execute_script <path>

# In-Unity: Tools → Setup Generated Scene (re-scaffolds the scene)
```

## Helper scripts added to the flappy_bird_project

- `Assets/_Project/Scripts/AutoStart.cs` — MonoBehaviour that calls
  `GameManager.Instance.Play()` on `Start()`. Workaround for gap 1.
- `Assets/Editor/UnpauseGame.cs` — editor script invokable via
  `execute_script` to force-call `GameManager.Play()` (diagnostic only).
- `Assets/Editor/WireBirdSprites.cs` — editor script to wire Bird_01/02/03
  into `Player.sprites` via SerializedObject. Workaround for gap 6.

These are in the generated project tree and will be overwritten on regen
unless preserved. Upstream fix for gap 1 + gap 6 removes the need for them.
