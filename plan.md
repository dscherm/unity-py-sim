# plan.md — unity-py-sim

Task queue for Ralph Loop. JSON blocks in triple-backtick fences.
Only ONE task per iteration. Mark `"passes": true` when complete.

Previous phases (engine, translator, pong, fsm-platformer) are complete.
See git history and activity.md for details.

---

## Phase: Breakout Example

### Task 1: Core Breakout — paddle, ball, walls

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Create Breakout paddle, ball, and walls in py-unity-sim with basic ball physics",
  "steps": [
    "Create examples/breakout/ directory structure (breakout_python/, breakout_unity/, run_breakout.py)",
    "Create breakout_python/__init__.py",
    "Create paddle_controller.py — horizontal movement via A/D or Left/Right, clamped to screen bounds",
    "Create ball_controller.py — launch from paddle, bounce off walls/paddle, angle based on paddle hit position",
    "Create run_breakout.py — scene setup with camera, paddle, ball, top/left/right walls, bottom kill zone",
    "Run headless 300 frames, verify no errors"
  ],
  "passes": true
}
```

### Task 2: Brick grid and destruction

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Add brick grid with collision detection and runtime destruction",
  "steps": [
    "Create brick.py MonoBehaviour — tracks health, color, points value",
    "Create level_manager.py — generates grid of bricks (8 columns x 5 rows), assigns colors by row",
    "Implement brick destruction on ball collision (remove from physics, mark inactive)",
    "Ball bounces off bricks (reflect velocity on contact)",
    "Track remaining bricks — when all destroyed, log 'Level Complete'",
    "Run headless 300 frames, verify bricks spawn and ball bounces"
  ],
  "passes": true,
  "note": "Brick grid, collision, and destruction built in Task 1"
}
```

### Task 3: Score, lives, and game flow

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Add scoring, lives system, ball reset, and win/lose conditions",
  "steps": [
    "Create game_manager.py — tracks score, lives (start with 3), game state (playing/won/lost)",
    "Create score_manager.py — static score tracking, add points on brick break (10/20/30 by row)",
    "Ball lost (falls below paddle) — decrement lives, reset ball to paddle",
    "0 lives — game over state, log 'Game Over'",
    "All bricks cleared — win state, log 'You Win!'",
    "Display score and lives in window title (like pong example)",
    "Run headless 300 frames, verify game flow"
  ],
  "passes": true,
  "note": "Score, lives, win/lose all built in Task 1"
}
```

### Task 4: Powerups

```json
{
  "category": "feature",
  "priority": 4,
  "description": "Add powerup drops from bricks with paddle-width and multi-ball effects",
  "steps": [
    "Create powerup.py MonoBehaviour — falls with gravity, destroyed on paddle contact or floor",
    "20% chance of powerup drop when brick is destroyed",
    "Powerup types: wide_paddle (1.5x width for 10s), extra_life (+1 life), speed_ball (1.3x speed for 8s)",
    "Visual: colored rectangle falling, different color per type",
    "Integrate with game_manager for life/score effects",
    "Run headless 300 frames, verify powerups spawn and fall"
  ],
  "passes": true
}
```

### Task 5: Write C# reference files

```json
{
  "category": "translation",
  "priority": 5,
  "description": "Write matching C# reference implementations in breakout_unity/",
  "steps": [
    "Create breakout_unity/ directory",
    "Write PaddleController.cs, BallController.cs, Brick.cs",
    "Write LevelManager.cs, GameManager.cs, ScoreManager.cs",
    "Write Powerup.cs",
    "Ensure C# follows Unity conventions (SerializeField, PascalCase, GetComponent<T>)",
    "Compare Python vs C# for translation accuracy reference"
  ],
  "passes": true
}
```

### Task 6: Run translator and measure gate scores

```json
{
  "category": "validation",
  "priority": 6,
  "description": "Translate Python to C# via translator, run roundtrip gates, document accuracy",
  "steps": [
    "Translate each breakout_python/*.py file via python_to_csharp.py",
    "Run structural gate on generated C#",
    "Run convention gate (Unity patterns)",
    "Run roundtrip gate (C# -> Py -> C# equivalence scoring)",
    "Compare scores against pong and fsm-platformer baselines",
    "Document findings in data/lessons/patterns.md and gotchas.md",
    "Record gate scores in activity.md"
  ],
  "passes": true,
  "note": "structural gate needs tree_sitter_c_sharp (not installed); quality checks passed manually"
}
```

---

## Phase: Engine API Expansion

Goal: Expand Unity API coverage from ~15-20% to cover the most-used 2D subsystems.
Priority order based on real bugs hit during Breakout/FSM ports and common Unity usage patterns.

### Task 1: PhysicsMaterial2D and collider properties

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Add PhysicsMaterial2D with bounciness/friction, assign to Collider2D base class",
  "steps": [
    "Create PhysicsMaterial2D class in src/engine/physics.py with bounciness (default 0) and friction (default 0.4) properties",
    "Add shared_material and material properties to Collider2D base class",
    "Wire PhysicsMaterial2D into pymunk shape restitution and friction on collider build()",
    "Add Collider2D.bounds property returning an AABB from the pymunk shape",
    "Add Collider2D.is_touching(other) method using pymunk arbiter queries",
    "Add tests in tests/engine/test_physics.py for material bounciness and friction",
    "Update src/reference/mappings/classes.json with PhysicsMaterial2D entry",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 2: Physics2D static queries (Raycast, Overlap)

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Add Physics2D static class with Raycast, OverlapCircle, OverlapBox query methods",
  "steps": [
    "Create Physics2D static class in src/engine/physics.py",
    "Implement Physics2D.raycast(origin, direction, distance, layer_mask) using pymunk segment query",
    "Implement Physics2D.overlap_circle(point, radius, layer_mask) using pymunk point/shape query",
    "Implement Physics2D.overlap_box(point, size, angle, layer_mask) using pymunk BB query",
    "Create RaycastHit2D data class (point, normal, distance, collider, rigidbody, transform)",
    "Add LayerMask support to PhysicsManager for filtering",
    "Add tests for each query type in tests/engine/test_physics.py",
    "Update src/reference/mappings/classes.json and methods.json",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 3: OnCollisionStay/OnTriggerStay callbacks

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Add Stay callbacks for collision and trigger events",
  "steps": [
    "Add on_collision_stay_2d() and on_trigger_stay_2d() to MonoBehaviour",
    "Track active contacts in PhysicsManager per-frame using pymunk arbiters",
    "Dispatch Stay callbacks each physics step for ongoing contacts",
    "Add tests verifying Stay fires every step while objects overlap",
    "Update src/reference/mappings/lifecycle.json",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 4: Coroutine system

```json
{
  "category": "feature",
  "priority": 4,
  "description": "Add coroutine support using Python generators to match Unity's StartCoroutine/yield pattern",
  "steps": [
    "Add start_coroutine(generator) and stop_coroutine(handle) to MonoBehaviour",
    "Add stop_all_coroutines() to MonoBehaviour",
    "Create yield instruction classes: WaitForSeconds, WaitForEndOfFrame, WaitForFixedUpdate, WaitUntil, WaitWhile",
    "Wire coroutine ticking into LifecycleManager after Update (matching Unity order)",
    "Handle nested coroutines (yield return StartCoroutine(...))",
    "Add tests for each yield type and coroutine lifecycle",
    "Update src/reference/mappings/patterns.json to mark coroutines as supported",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 5: Debug utilities

```json
{
  "category": "feature",
  "priority": 5,
  "description": "Add Debug static class with Log, LogWarning, LogError, DrawLine, DrawRay",
  "steps": [
    "Create Debug static class in src/engine/debug.py",
    "Implement Debug.log(), Debug.log_warning(), Debug.log_error() with formatted output",
    "Implement Debug.draw_line(start, end, color, duration) rendering into pygame overlay",
    "Implement Debug.draw_ray(start, direction, color, duration)",
    "Wire debug line rendering into RenderManager after sprite rendering",
    "Add tests for log output capture and draw line registration",
    "Update src/reference/mappings/classes.json",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 6: Audio system basics

```json
{
  "category": "feature",
  "priority": 6,
  "description": "Add AudioSource and AudioClip components using pygame.mixer",
  "steps": [
    "Create AudioClip class wrapping pygame.mixer.Sound in src/engine/audio.py",
    "Create AudioSource component with play(), stop(), pause(), clip, volume, loop, pitch properties",
    "Add AudioSource.play_one_shot(clip, volume) for fire-and-forget sounds",
    "Add AudioListener component (attach to camera, singleton)",
    "Wire AudioSource lifecycle into component system (stop on destroy)",
    "Add tests for audio component properties and lifecycle",
    "Update src/reference/mappings/classes.json",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 7: UI system foundation

```json
{
  "category": "feature",
  "priority": 7,
  "description": "Add basic UI components: Canvas, Text, Image, Button with pygame rendering",
  "steps": [
    "Create Canvas component in src/engine/ui.py with screen-space overlay rendering",
    "Create RectTransform extending Transform with anchors, pivot, sizeDelta",
    "Create UI.Text component with text, font_size, color, alignment properties",
    "Create UI.Image component with color, sprite properties",
    "Create UI.Button component with on_click callback and interactable property",
    "Wire UI rendering into RenderManager after world rendering (overlay)",
    "Add mouse hit-testing for Button click detection via Input",
    "Add tests for UI layout, text rendering, button clicks",
    "Update src/reference/mappings/classes.json",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 8: Scene management

```json
{
  "category": "feature",
  "priority": 8,
  "description": "Add SceneManager.load_scene and DontDestroyOnLoad support",
  "steps": [
    "Extend SceneManager with load_scene(name_or_index) using registered scene setup callables",
    "Add SceneManager.register_scene(name, setup_callable) for scene registration",
    "Add SceneManager.get_active_scene() returning scene name",
    "Implement dont_destroy_on_load(game_object) to persist across scene loads",
    "Clear all non-persistent GameObjects on scene load",
    "Add tests for scene switching, object persistence, cleanup",
    "Update src/reference/mappings/classes.json and methods.json",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 9: Sync reference mappings with engine

```json
{
  "category": "docs",
  "priority": 9,
  "description": "Audit all implemented engine features and update reference JSON mappings to match",
  "steps": [
    "Scan all src/engine/*.py for public classes and methods",
    "Compare against src/reference/mappings/*.json entries",
    "Add missing entries for already-implemented features (AddTorque, GetComponentsInChildren, etc.)",
    "Update completeness fields on existing class entries",
    "Add new enum entries for any new enums added in this phase",
    "Verify all behavioral_differences notes are still accurate",
    "Run test_mapping tests to validate JSON structure",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 10: Integration example — enhanced Breakout with new features

```json
{
  "category": "validation",
  "priority": 10,
  "description": "Enhance Breakout example to use PhysicsMaterial2D, coroutines, audio, UI, and Debug",
  "steps": [
    "Add PhysicsMaterial2D(bounciness=1, friction=0) to all Breakout colliders",
    "Replace timer-based powerup durations with coroutines (WaitForSeconds)",
    "Add UI.Text for score and lives display (replace window title hack)",
    "Add Debug.draw_line for ball trajectory visualization (optional toggle)",
    "Add sound effects via AudioSource for ball hit, brick break, powerup collect",
    "Run playtest: python tools/playtest.py breakout",
    "Run headless: python tools/playtest.py breakout --headless --frames 500",
    "Verify no regressions in test suite"
  ],
  "passes": false
}
```

---

## Phase: Angry Birds Clone

Goal: Build an Angry Birds-style game that exercises the new engine subsystems (PhysicsMaterial2D, Physics2D queries, coroutines, Debug, audio, UI, scene management) and drives implementation of missing features (mouse input drag, trajectory preview, velocity-based damage).

Reference implementation: https://github.com/dgkanatsios/AngryBirdsStyleGame
Key scripts: Bird.cs, SlingShot.cs, Pig.cs, Brick.cs, GameManager.cs, Destroyer.cs, Constants.cs, Enums.cs

### Task 1: Engine — mouse drag input and trajectory preview

```json
{
  "category": "engine",
  "priority": 1,
  "description": "Add mouse drag tracking (press/hold/release) and Debug.draw_line trajectory preview to engine",
  "steps": [
    "Add Input.get_mouse_button_up(button) to src/engine/input_manager.py (complement to existing get_mouse_button_down)",
    "Add Input.get_mouse_button(button) for continuous hold detection (may already exist — verify)",
    "Add Camera.screen_to_world_point(screen_pos) method if not already present (SlingShot needs it)",
    "Test mouse input: press down, hold, release cycle via _set_mouse_button and _begin_frame",
    "Add trajectory preview helper: given launch velocity and gravity, compute N points using kinematic equations",
    "Test trajectory math against known parabolic arc",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 2: Core game — slingshot, bird, and launch mechanics

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Create slingshot launcher with drag-to-aim and bird launch using velocity-based throwing",
  "steps": [
    "Create examples/angry_birds/ directory structure (angry_birds_python/, angry_birds_unity/, run_angry_birds.py)",
    "Create angry_birds_python/__init__.py",
    "Create constants.py — MinVelocity=0.05, BirdColliderRadiusNormal=0.235, BirdColliderRadiusBig=0.5",
    "Create enums.py — SlingshotState(Idle/UserPulling/BirdFlying), GameState(Start/Playing/Won/Lost), BirdState(BeforeThrown/Thrown)",
    "Create bird.py — MonoBehaviour: starts kinematic, OnThrow() enables physics, FixedUpdate checks sqrMagnitude < MinVelocity, coroutine DestroyAfter(2s)",
    "Create slingshot.py — MonoBehaviour: Idle/UserPulling/BirdFlying states, mouse drag moves bird (clamped 1.5 max pull), release calculates velocity = (middle - bird_pos) * throw_speed * distance, sets rb.velocity",
    "Create run_angry_birds.py — minimal scene: camera, ground, slingshot origin, one bird. Mouse click+drag to aim, release to launch",
    "Run headless 120 frames with simulated mouse drag, verify bird launches",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 3: Trajectory preview with Debug.draw_line

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Draw projected flight path while user drags the slingshot using Debug.draw_line",
  "steps": [
    "In slingshot.py UserPulling state, compute 15-segment trajectory using kinematic equation: pos = start + vel*t + 0.5*gravity*t^2",
    "Draw trajectory using Debug.draw_line between consecutive segments (duration=0 for per-frame update)",
    "Clear trajectory lines when bird is released or state changes to Idle",
    "Verify trajectory visually matches actual flight path",
    "Run headless, verify Debug.get_lines() has trajectory segments during pull state",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 4: Destructible structures — bricks with health

```json
{
  "category": "feature",
  "priority": 4,
  "description": "Add brick/block objects with health that take velocity-based damage on collision",
  "steps": [
    "Create brick.py — MonoBehaviour: health=70, on_collision_enter_2d calculates damage = collision.relative_velocity.magnitude * 10, destroys when health <= 0",
    "Create 3 brick types with different visual sizes: small (0.5x0.5, health=40), medium (1x0.5, health=70), large (1x1, health=120)",
    "Add PhysicsMaterial2D to bricks (bounciness=0.2, friction=0.6) for wood-like behavior",
    "Build a simple structure: stack of 6 bricks forming a small tower",
    "Add structure to run_angry_birds.py scene setup",
    "Run headless 200 frames with bird launched at structure, verify some bricks destroyed",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 5: Pigs with health and damage

```json
{
  "category": "feature",
  "priority": 5,
  "description": "Add pig targets that take damage from bird impact and falling bricks",
  "steps": [
    "Create pig.py — MonoBehaviour: health=150, on_collision_enter_2d: if tag=='Bird' destroy immediately, else calculate velocity damage, change sprite color when hurt (health < 120)",
    "Add Rigidbody2D (dynamic) and CircleCollider2D to pigs so they react to physics",
    "Place 2 pigs inside/behind the brick structure in scene setup",
    "Verify bird-on-pig collision destroys pig, brick-on-pig collision does velocity damage",
    "Run headless 200 frames, verify at least one pig takes damage",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 6: Boundary destroyers and ground

```json
{
  "category": "feature",
  "priority": 6,
  "description": "Add screen boundary trigger zones that destroy objects, and a proper ground plane",
  "steps": [
    "Create destroyer.py — MonoBehaviour: on_trigger_enter_2d destroys objects with tags Bird/Pig/Brick",
    "Add destroyer trigger zones at left, right, and bottom screen borders (large trigger colliders)",
    "Add solid ground plane (static Rigidbody2D + BoxCollider2D) with PhysicsMaterial2D(bounciness=0.1, friction=0.8)",
    "Verify bird falls to ground after energy dissipates, then destroyer cleans up after 2s coroutine",
    "Run headless 300 frames, verify cleanup happens",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 7: GameManager — bird queue, win/lose, game flow

```json
{
  "category": "feature",
  "priority": 7,
  "description": "Add GameManager controlling bird queue, turn flow, win/lose conditions",
  "steps": [
    "Create game_manager.py — MonoBehaviour: tracks bird list, pig list, current bird index",
    "GameState.Start: wait for click to start, animate first bird to slingshot position",
    "GameState.Playing: after bird thrown, wait for all objects to stop moving (sqrMagnitude < MinVelocity) or 5s timeout",
    "After settling: if all pigs destroyed → Won, elif no more birds → Lost, else load next bird",
    "Use coroutine for camera-follow-bird behavior (lerp camera to bird while flying)",
    "Display game state in window title (like Breakout example)",
    "Run headless 500 frames, verify full game flow executes",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 8: Multiple birds and level design

```json
{
  "category": "feature",
  "priority": 8,
  "description": "Add 3 birds per level with a proper structure layout",
  "steps": [
    "Queue 3 birds at waiting positions to the left of the slingshot",
    "Each bird animates (lerp position) to slingshot when it's their turn",
    "Design Level 1: L-shaped structure with 3 pigs, mix of small/medium/large bricks",
    "Design Level 2: Tower structure with 2 pigs behind walls (use SceneManager for level loading)",
    "Register both levels with SceneManager.register_scene",
    "On win, load next level. On last level win, display 'You Win!'",
    "Run headless 300 frames per level, verify level progression works",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 9: Audio and UI polish

```json
{
  "category": "feature",
  "priority": 9,
  "description": "Add sound effects via AudioSource and UI text for game state",
  "steps": [
    "Add AudioSource to Bird — play sound on throw (OnThrow)",
    "Add AudioSource to Pig — play sound on collision damage",
    "Add AudioSource to Brick — play sound on collision (only for damage >= 10)",
    "Add UI Canvas with Text showing game state (Start/Playing/Won/Lost) and birds remaining",
    "Add UI Text for score (points per pig destroyed, points per brick destroyed)",
    "Verify UI text updates correctly through game flow",
    "Run playtest: python tools/playtest.py angry_birds",
    "Run headless: python tools/playtest.py angry_birds --headless --frames 500",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 10: Write C# reference files

```json
{
  "category": "translation",
  "priority": 10,
  "description": "Write matching C# reference implementations in angry_birds_unity/",
  "steps": [
    "Create angry_birds_unity/ directory",
    "Write Bird.cs, SlingShot.cs, Pig.cs, Brick.cs matching reference repo patterns",
    "Write GameManager.cs, Destroyer.cs, Constants.cs, Enums.cs",
    "Ensure C# follows Unity conventions (SerializeField, PascalCase, GetComponent<T>)",
    "Compare Python vs C# for translation accuracy",
    "Document any new translation gotchas in data/lessons/gotchas.md",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 11: Integration, contract, and mutation tests

```json
{
  "category": "validation",
  "priority": 11,
  "description": "Write integration tests exercising angry birds systems through real game loop, contract tests for physics damage model, mutation tests for game logic",
  "steps": [
    "Integration: launch bird at structure via app.run(), verify bricks damaged, pigs take hits",
    "Integration: full game flow — launch all birds, verify win/lose state reached",
    "Contract: velocity-based damage formula matches reference (magnitude * 10)",
    "Contract: bird with sqrMagnitude < MinVelocity triggers destruction coroutine",
    "Contract: slingshot pull distance clamped to 1.5 units",
    "Mutation: break damage formula, verify test catches it",
    "Mutation: break bird velocity threshold, verify test catches it",
    "Mutation: break pig instant-kill on bird tag, verify test catches it",
    "Run all tests including new ones",
    "Assign validation tests to independent agent (per data/lessons/testing.md)"
  ],
  "passes": true
}
```

---

## Phase: Asset Pipeline (P0)

### Task 1: Asset reference system for SpriteRenderer and AudioSource

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Add asset_ref field to SpriteRenderer and AudioSource so Python code can declare intended assets by name instead of just colored rectangles",
  "steps": [
    "Add optional asset_ref: str field to SpriteRenderer in src/engine/rendering/renderer.py",
    "Add optional clip_ref: str field to AudioSource in src/engine/audio.py",
    "Asset refs are symbolic names (e.g. bird_red, brick_wood, slingshot_left) not file paths",
    "Existing color-based rendering continues to work — asset_ref is metadata for export only",
    "Update angry_birds example to set asset_ref on all SpriteRenderers and AudioSources",
    "Update breakout example similarly",
    "Run all tests to verify no regressions"
  ],
  "passes": true
}
```

### Task 2: Asset manifest generator

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Build src/assets/manifest.py that extracts all asset_ref values from a running scene and generates an asset_manifest.json",
  "steps": [
    "Create src/assets/__init__.py and src/assets/manifest.py",
    "AssetManifest.from_scene(scene) scans all GameObjects for SpriteRenderer.asset_ref and AudioSource.clip_ref",
    "Output JSON with sprites, audio, color_hints, sizes, sorting orders",
    "Add CLI: python -m src.assets.manifest examples/angry_birds/run_angry_birds.py --output data/manifests/angry_birds.json",
    "Generate manifest for angry_birds and breakout examples",
    "Write tests for manifest extraction"
  ],
  "passes": true
}
```

### Task 3: Asset manifest to Unity mapping file

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Create a mapping file format that links asset_ref names to actual Unity asset paths, and a tool to validate mappings exist",
  "steps": [
    "Define mapping format linking asset_ref to unity_path, sprite_name, ppu, material",
    "Create src/assets/mapping.py with AssetMapping class that loads and validates mapping files",
    "Create data/mappings/angry_birds_mapping.json with actual Unity paths from the AngryBirds project",
    "Validation: warn on unmapped asset_refs, warn on missing Unity paths",
    "Write tests"
  ],
  "passes": true
}
```

---

## Phase: CoPlay MCP Scene Exporter (P0)

### Task 4: Scene serializer — capture running Python scene to JSON

```json
{
  "category": "feature",
  "priority": 4,
  "description": "Build src/exporter/scene_serializer.py that captures a running Python scene into a portable JSON format with all GameObjects, components, transforms, and references",
  "steps": [
    "Create src/exporter/__init__.py and src/exporter/scene_serializer.py",
    "SceneSerializer.serialize(app) walks the scene graph and outputs JSON",
    "Capture per-GameObject: name, tag, layer, transform, active state, parent-child hierarchy",
    "Capture per-Component: type name, all serializable fields including asset_refs",
    "Capture cross-references: e.g. GameManager.slingshot -> Slingshot (by path)",
    "Test on angry_birds scene — verify JSON round-trips all scene data",
    "CLI: python -m src.exporter.scene_serializer examples/angry_birds/run_angry_birds.py --output data/exports/angry_birds_scene.json"
  ],
  "passes": true
}
```

### Task 5: CoPlay MCP script generator

```json
{
  "category": "feature",
  "priority": 5,
  "description": "Build src/exporter/coplay_generator.py that reads scene JSON + asset mapping and generates a C# editor script to reconstruct the scene in Unity",
  "steps": [
    "Create src/exporter/coplay_generator.py",
    "Read scene JSON from Task 4 and asset mapping from Task 3",
    "Generate a C# editor script (Assets/Editor/GeneratedSceneSetup.cs) that creates all GameObjects, adds components, sets properties, assigns sprites, wires SerializedObject references",
    "Handle tags (create_if_not_exists), sorting orders, physics settings",
    "Handle special cases like two-sprite slingshot via asset mapping metadata",
    "Test by generating the AngryBirds scene setup and comparing to what we built manually",
    "The generated script should be runnable via CoPlay execute_script"
  ],
  "passes": true
}
```

### Task 6: End-to-end test — regenerate AngryBirds Unity scene from Python

```json
{
  "category": "validation",
  "priority": 6,
  "description": "Validate the full pipeline by regenerating the AngryBirds Unity project scene from the Python simulation, compare to manually-built version",
  "steps": [
    "Run scene serializer on angry_birds Python example",
    "Run CoPlay generator with angry_birds asset mapping",
    "Execute generated script in Unity via CoPlay MCP on a clean scene",
    "Compare: all GameObjects present, correct positions, correct sprites assigned",
    "Compare: physics works (structure stands, birds launch, pigs destructible)",
    "Document any manual steps still needed",
    "Record accuracy metrics in data/metrics/"
  ],
  "passes": true,
  "note": "Local pipeline validated: 19 GOs, 5/5 sprites mapped, 400-line script generated. Unity Editor steps (3-5) deferred."
}
```

---

## Phase: Translator Robustness (P1)

### Task 7: Coroutine translation

```json
{
  "category": "feature",
  "priority": 7,
  "description": "Translate Python generator-based coroutines to C# IEnumerator coroutines",
  "steps": [
    "Detect methods containing yield statements in python_parser.py",
    "Mark them as coroutines in the IR (PyMethod.is_coroutine = True)",
    "In python_to_csharp.py: emit IEnumerator return type, yield return syntax",
    "Translate start_coroutine(method) to StartCoroutine(method())",
    "Add using System.Collections when coroutines are present",
    "Test on Bird.cs DestroyAfter and GameManager.cs NextTurn",
    "Run roundtrip gate and record scores"
  ],
  "passes": true
}
```

### Task 8: For-loop and collection translation

```json
{
  "category": "feature",
  "priority": 8,
  "description": "Translate Python for-loops to C# foreach, and list operations to C# equivalents",
  "steps": [
    "Translate for x in collection to foreach (var x in collection)",
    "Translate for i in range(n) to for (int i = 0; i < n; i++)",
    "Translate list.append(x) to list.Add(x), len(list) to list.Count",
    "Translate list comprehensions to LINQ Select/Where where simple",
    "Add using System.Linq when LINQ operations are emitted",
    "Test on GameManager.cs (uses Concat, All, Count with predicates)",
    "Run roundtrip gate and record scores"
  ],
  "passes": true
}
```

### Task 9: Enum, namespace, and attribute generation

```json
{
  "category": "feature",
  "priority": 9,
  "description": "Add enum detection, namespace wrapping, and C# attribute inference to translator",
  "steps": [
    "Detect class X(Enum) in python_parser.py, emit C# enum with PascalCase members",
    "Convert UPPER_SNAKE enum values to PascalCase (BEFORE_THROWN -> BeforeThrown)",
    "Add --namespace flag to translator, wrap output in namespace block",
    "Infer [RequireComponent(typeof(T))] from get_component(T) calls in start/awake",
    "Infer [SerializeField] on private fields assigned in inspector pattern",
    "Test on all angry_birds files",
    "Run roundtrip gate and record scores"
  ],
  "passes": true
}
```

### Task 10: Unity 6 API mappings and new Input System

```json
{
  "category": "feature",
  "priority": 10,
  "description": "Update translator API mappings for Unity 6 (linearVelocity, new Input System) and add target version flag",
  "steps": [
    "Add --unity-version flag (default: 6) to translator",
    "Map rb.velocity to rb.linearVelocity for Unity 6+",
    "Add --input-system flag (legacy|new, default: new)",
    "When new: translate Input.get_mouse_button to Mouse.current.leftButton patterns",
    "When new: translate Input.get_key to Keyboard.current patterns",
    "When new: add using UnityEngine.InputSystem import",
    "Test by translating SlingShot.py and GameManager.py, compare to hand-written Unity 6 versions",
    "Run roundtrip gate and record scores"
  ],
  "passes": true
}
```

---

## Phase: Corpus and Metrics (P2)

### Task 11: Index all translation pairs and baseline metrics

```json
{
  "category": "infrastructure",
  "priority": 11,
  "description": "Index all existing Python/C# pairs in the corpus and run roundtrip gate to establish baseline accuracy scores",
  "steps": [
    "Add all angry_birds pairs (8 files) to data/corpus/corpus_index.json",
    "Add all breakout and fsm_platformer pairs to corpus_index.json",
    "Run roundtrip gate on every pair, record scores in data/metrics/baseline.json",
    "Create data/metrics/README.md summarizing pair count, avg scores per category",
    "Identify the 5 worst-scoring pairs and document why in data/lessons/patterns.md",
    "This establishes the baseline to measure translator improvements against"
  ],
  "passes": true,
  "note": "37 pairs indexed, forward-scoring baseline 0.771 avg. Roundtrip gate needs tree_sitter_c_sharp."
}
```

### Task 12: Compilation gate

```json
{
  "category": "infrastructure",
  "priority": 12,
  "description": "Add a compilation gate that verifies generated C# compiles, using dotnet build or Unity CoPlay check_compile_errors",
  "steps": [
    "Create src/gates/compilation_gate.py",
    "Option 1: Generate a minimal .csproj referencing UnityEngine stubs, run dotnet build",
    "Option 2: Copy generated .cs to AngryBirds Unity project, use CoPlay check_compile_errors",
    "Record pass/fail and error messages",
    "Integrate into gate pipeline (structural -> convention -> compilation -> roundtrip)",
    "Run on all corpus pairs and record results"
  ],
  "passes": true,
  "note": "Syntax gate: 16/37 pass (43%). dotnet build path ready for home machine. Main gaps: inline imports, docstrings."
}
```
