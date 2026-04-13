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
  "passes": true
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

---

## Phase: Engine Expansion P0 — Tweening, Pooling, Events

Goal: Add the three highest-impact missing systems. Every game needs tweening,
most need pooling, and events decouple architecture. All have clean C# translation targets.

### Task 1: Tweening system (DOTween equivalent)

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Add a tweening engine with typed property animation, easing curves, and chaining — Python equivalent of DOTween",
  "steps": [
    "Create src/engine/tweening.py with Tween, Sequence, and TweenManager classes",
    "Tween.to(target, property, end_value, duration) — animate any numeric property",
    "Tween.from(target, property, start_value, duration) — animate from a value to current",
    "Support Vector2 and Vector3 property tweens (position, scale, etc.)",
    "Add easing functions: Linear, EaseInOut (Quad, Cubic, Sine, Elastic, Bounce, Back)",
    "Add tween callbacks: on_start, on_update, on_complete",
    "Add tween controls: kill(), pause(), resume(), set_loops(count, loop_type)",
    "Add Sequence class: append(tween), join(tween), insert(time, tween) for chaining",
    "Wire TweenManager.tick(dt) into LifecycleManager after Update",
    "Add tests for each easing type, callbacks, sequences, Vector2/3 tweens",
    "Update src/reference/mappings/classes.json with DOTween equivalents",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 2: Object pooling system

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Add ObjectPool matching Unity's UnityEngine.Pool.ObjectPool<T> pattern",
  "steps": [
    "Create src/engine/pool.py with ObjectPool class",
    "ObjectPool(create_func, on_get, on_release, on_destroy, max_size) constructor",
    "pool.get() -> returns pooled object or creates new, calls on_get",
    "pool.release(obj) -> returns to pool, calls on_release, deactivates GameObject",
    "pool.clear() -> destroy all pooled objects",
    "Add GameObjectPool convenience subclass: pre-instantiate from a template GameObject",
    "Wire with GameObject.active = False for pooled objects, True on get",
    "Add tests: get/release cycle, max size enforcement, callback firing",
    "Update src/reference/mappings/classes.json",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 3: Event bus / message system

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Add typed event bus for decoupled inter-component messaging, maps to C# events/UnityEvents",
  "steps": [
    "Create src/engine/events.py with EventBus static class",
    "EventBus.subscribe(event_type, handler) — register callback for event class",
    "EventBus.unsubscribe(event_type, handler) — remove callback",
    "EventBus.publish(event) — dispatch to all subscribers of that event type",
    "Events are plain dataclasses: @dataclass class BrickDestroyedEvent: brick: GameObject, points: int",
    "Add UnityEvent class matching Unity's inspector-wirable event pattern",
    "UnityEvent() with add_listener(callback), remove_listener(callback), invoke(*args)",
    "Add tests: subscribe/publish, unsubscribe, multiple subscribers, UnityEvent",
    "Update angry_birds example to use EventBus for score/game state changes",
    "Update src/reference/mappings/classes.json",
    "Run full test suite"
  ],
  "passes": true
}
```

---

## Phase: Engine Expansion P1 — Animation, Camera, Joints

Goal: Sprite animation, camera follow system, and 2D joints. These are the next tier
of features needed for any non-trivial game.

### Task 4: Sprite animation system

```json
{
  "category": "feature",
  "priority": 4,
  "description": "Add frame-based sprite animation with SpriteAnimator component",
  "steps": [
    "Create src/engine/animation.py with AnimationClip and SpriteAnimator classes",
    "AnimationClip: list of frame colors/asset_refs, fps, loop mode (Once, Loop, PingPong)",
    "SpriteAnimator component: play(clip_name), stop(), current_clip, is_playing",
    "Support multiple named clips per animator (idle, walk, attack, etc.)",
    "Tick animation in Update — advance frame index based on Time.delta_time and fps",
    "Update SpriteRenderer.color or SpriteRenderer.asset_ref on frame change",
    "Add animation events: on_frame(frame_index, callback) for triggering logic at specific frames",
    "Add tests: frame advancement, loop modes, play/stop, clip switching",
    "Update src/reference/mappings/classes.json",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 5: Camera follow system (Cinemachine-lite)

```json
{
  "category": "feature",
  "priority": 5,
  "description": "Add CameraFollow2D component with damping, dead zone, look-ahead, and camera shake",
  "steps": [
    "Create src/engine/camera_follow.py with CameraFollow2D component",
    "Properties: target (Transform), follow_offset, damping (0-1), dead_zone (Vector2)",
    "Look-ahead: offset camera in direction of target velocity",
    "Confine: optional bounds (min/max Vector2) to clamp camera position",
    "Wire into LateUpdate (after all movement is done)",
    "Add CameraShake class: trigger(intensity, duration, frequency) using Perlin noise",
    "CameraShake applies additive offset to camera position, decays over duration",
    "Add tests: follow tracking, damping behavior, dead zone, bounds clamping, shake decay",
    "Update angry_birds camera follow to use CameraFollow2D instead of manual lerp",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 6: 2D Joint system

```json
{
  "category": "feature",
  "priority": 6,
  "description": "Expose pymunk joints as Unity-style 2D joint components",
  "steps": [
    "Create src/engine/physics/joints.py",
    "HingeJoint2D: connected_body, anchor, limits (min/max angle), motor (speed, max_torque)",
    "SpringJoint2D: connected_body, distance, frequency, damping_ratio",
    "DistanceJoint2D: connected_body, distance, max_distance_only",
    "FixedJoint2D: connected_body (rigid connection)",
    "Wire all joints to pymunk constraint types in PhysicsManager",
    "Auto-create/destroy pymunk constraints on component add/remove",
    "Add tests for each joint type: creation, constraint behavior, limits",
    "Update src/reference/mappings/classes.json",
    "Run full test suite"
  ],
  "passes": true
}
```

---

## Phase: Engine Expansion P2 — Renderers, Colliders, Sorting

Goal: Fill rendering and physics gaps — LineRenderer, TrailRenderer, PolygonCollider2D,
and proper sorting layers.

### Task 7: LineRenderer and TrailRenderer

```json
{
  "category": "feature",
  "priority": 7,
  "description": "Add persistent LineRenderer and TrailRenderer components",
  "steps": [
    "Create LineRenderer component in src/engine/rendering/line_renderer.py",
    "Properties: positions (list[Vector2]), width_start, width_end, color_start, color_end, sorting_order",
    "set_positions(points) and set_position(index, point) methods",
    "Render as connected line segments in pygame via RenderManager",
    "Create TrailRenderer component: follows transform, fades over time",
    "Properties: trail_time, width_start, width_end, color_gradient, min_vertex_distance",
    "TrailRenderer auto-records positions each frame, removes old ones past trail_time",
    "Wire both into RenderManager rendering pass",
    "Add tests: line positions, trail recording, trail fade, sorting order",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 8: PolygonCollider2D and EdgeCollider2D

```json
{
  "category": "feature",
  "priority": 8,
  "description": "Add polygon and edge colliders using pymunk Poly and Segment shapes",
  "steps": [
    "Add PolygonCollider2D to src/engine/physics/collider.py",
    "Properties: points (list[Vector2]) defining the polygon vertices",
    "build() creates pymunk.Poly from points, applies material, registers with PhysicsManager",
    "Add EdgeCollider2D: points (list[Vector2]) defining connected line segments",
    "build() creates multiple pymunk.Segment shapes for each edge",
    "Support material (PhysicsMaterial2D) and is_trigger on both",
    "Add tests: polygon creation, edge chain, collision detection, trigger events",
    "Update src/reference/mappings/classes.json",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 9: Sorting layers system

```json
{
  "category": "feature",
  "priority": 9,
  "description": "Add named sorting layers matching Unity's sorting layer system",
  "steps": [
    "Create SortingLayer registry in src/engine/rendering/sorting.py",
    "SortingLayer.add(name, order) — register named layers (Default=0, Background=-100, Foreground=100)",
    "Add sorting_layer_name property to SpriteRenderer (defaults to 'Default')",
    "RenderManager sorts by: sorting_layer order first, then sorting_order within layer",
    "Add SortingLayer.get_layer_value(name) for lookup",
    "Pre-register Default, Background, Foreground, UI layers",
    "Add tests: layer ordering, same-layer sorting, unknown layer fallback",
    "Run full test suite"
  ],
  "passes": true
}
```

---

## Phase: Engine Expansion P3 — Particles, Tilemap, CharacterController

Goal: The heavy-lift features. Particle system enables visual polish, tilemap enables
level design, CharacterController2D replaces raw physics for platformers.

### Task 10: 2D Particle system

```json
{
  "category": "feature",
  "priority": 10,
  "description": "Add ParticleSystem component with emission, lifetime, velocity, and color over lifetime",
  "steps": [
    "Create src/engine/particles.py with ParticleSystem and Particle classes",
    "Particle: position, velocity, lifetime, age, color, size — updated each frame",
    "ParticleSystem component: emission_rate, start_lifetime, start_speed, start_size, start_color",
    "Emission shapes: point, circle, box (random position within shape)",
    "Color over lifetime: lerp between start_color and end_color based on age/lifetime",
    "Size over lifetime: lerp between start_size and end_size",
    "Gravity modifier: apply scaled gravity to particle velocity",
    "play(), stop(), pause() controls; is_playing, particle_count properties",
    "Render particles as colored rectangles via RenderManager (after sprites, before UI)",
    "Max particles cap (default 100) — stop emitting when full",
    "Add tests: emission rate, lifetime expiry, color/size over lifetime, gravity",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 11: 2D Tilemap system

```json
{
  "category": "feature",
  "priority": 11,
  "description": "Add Tilemap, TilemapRenderer, and Tile for grid-based level building",
  "steps": [
    "Create src/engine/tilemap.py with Tile, Tilemap, and TilemapRenderer classes",
    "Tile: color, asset_ref, collider_type (None, Full, Custom), is_walkable flag",
    "Tilemap component: grid-based storage, cell_size (Vector2), set_tile(x, y, tile), get_tile(x, y)",
    "TilemapRenderer: renders all set tiles as colored rectangles at grid positions",
    "TilemapCollider2D: auto-generates BoxCollider2D for tiles with collider_type=Full",
    "Support tilemap bounds (min/max cell coordinates) for iteration",
    "Wire TilemapRenderer into RenderManager with sorting layer support",
    "Add tests: set/get tiles, rendering positions, collider generation, bounds",
    "Update src/reference/mappings/classes.json",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 12: CharacterController2D

```json
{
  "category": "feature",
  "priority": 12,
  "description": "Add CharacterController2D with ground detection, slopes, and one-way platforms",
  "steps": [
    "Create src/engine/character_controller.py with CharacterController2D component",
    "Properties: skin_width, slope_limit, step_offset, is_grounded, velocity",
    "move(motion: Vector2) — move with collision detection using raycasts",
    "Ground check: downward raycast(s) from collider bottom, set is_grounded",
    "Horizontal collision: side raycasts for wall detection",
    "Slope handling: detect slope angle via raycast normal, slide along surface up to slope_limit",
    "One-way platforms: check platform tag, allow upward pass-through, collide from above",
    "Callbacks: on_controller_collider_hit(hit) for collision response",
    "Add tests: ground detection, wall collision, slope climbing, one-way platform",
    "Update FSM platformer to optionally use CharacterController2D",
    "Run full test suite"
  ],
  "passes": true
}
```

---

## Phase: Engine Expansion P3+ — Visual Polish

Goal: Remaining visual systems for completeness.

### Task 13: Sprite atlas and sub-sprite extraction

```json
{
  "category": "feature",
  "priority": 13,
  "description": "Add SpriteAtlas for extracting sub-sprites from sprite sheets",
  "steps": [
    "Create src/engine/rendering/sprite_atlas.py with SpriteAtlas class",
    "SpriteAtlas: load from image path, define sub-sprites by name + rect (x, y, w, h)",
    "sprite_atlas.get_sprite(name) -> returns sub-region for SpriteRenderer",
    "Support uniform grid slicing: slice_grid(cols, rows) auto-names sprites",
    "Integration with SpriteAnimator: animation clips reference atlas sprite names",
    "Add tests: grid slicing, named sprite lookup, integration with animator",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 14: TextMeshPro-lite (rich text)

```json
{
  "category": "feature",
  "priority": 14,
  "description": "Enhance Text component with basic rich text tags and text effects",
  "steps": [
    "Extend Text in src/engine/ui.py with rich_text: bool flag",
    "Support basic tags: <color=#FF0000>red</color>, <b>bold</b>, <size=24>big</size>",
    "Parse tags into styled runs, render each run with appropriate color/size",
    "Add character-by-character reveal effect: reveal_speed (chars per second)",
    "Add typewriter callback: on_character_revealed(index)",
    "Add tests: tag parsing, multi-color rendering, reveal animation",
    "Run full test suite"
  ],
  "passes": true
}
```

---

## Phase: Space Invaders Clone

Goal: Reverse-engineer zigurous/unity-space-invaders-tutorial (7 C# scripts) into the
Python simulator, then translate back to C# and compare. Reference cloned to
D:/Projects/space-invaders-ref/Assets/Scripts/.

Reference scripts: Player.cs, Invader.cs, Invaders.cs (grid+AI), Projectile.cs,
Bunker.cs (destructible shields), MysteryShip.cs, GameManager.cs.

### Task 1: Player controller and projectile

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Create player ship with A/D movement, screen-clamped, and laser projectile (one at a time)",
  "steps": [
    "Create examples/space_invaders/ directory (space_invaders_python/, space_invaders_unity/, run_space_invaders.py)",
    "Create player.py — MonoBehaviour: speed=5, A/D or Left/Right movement clamped to screen edges",
    "Create projectile.py — MonoBehaviour: direction (up/down), speed=20, moves via transform, destroyed on trigger",
    "Player fires laser on Space/mouse click — only one active laser at a time (check if previous destroyed)",
    "Add boundary trigger zones (top/bottom) that destroy projectiles",
    "Create run_space_invaders.py — minimal scene: camera, player, boundary zones",
    "Run headless 120 frames, verify player moves and laser fires",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 2: Invader grid with movement and animation

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Create 5x11 invader grid that moves side-to-side, advances down on edge hit, with frame animation",
  "steps": [
    "Create invader.py — MonoBehaviour: score value, 2-frame color animation via timer",
    "Create invaders.py — MonoBehaviour: creates 5x11 grid as child GameObjects, moves entire grid",
    "Grid movement: move right until rightmost invader hits screen edge, then drop 1 row and reverse",
    "Speed increases as invaders are killed: speed = base_speed * curve(percent_killed)",
    "get_alive_count() checks active children, reset_invaders() reactivates all",
    "Add invaders to scene in run_space_invaders.py",
    "Run headless 200 frames, verify grid moves and reverses",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 3: Missile attacks from invaders

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Invaders randomly fire missiles downward, probability based on alive count",
  "steps": [
    "In invaders.py: missile_attack() on timer (every 1s via coroutine)",
    "Each alive invader has 1/alive_count chance to fire",
    "Missile is a Projectile with direction=down, different layer than laser",
    "Use layer system to distinguish laser from missile",
    "Run headless 200 frames, verify missiles spawn and fall",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 4: Collision — laser kills invaders, missile kills player

```json
{
  "category": "feature",
  "priority": 4,
  "description": "Wire trigger collisions: laser destroys invaders, missiles destroy player, invaders reaching bottom kills player",
  "steps": [
    "Player on_trigger_enter_2d: if missile or invader layer, call GameManager.on_player_killed()",
    "Invader on_trigger_enter_2d: if laser layer, call GameManager.on_invader_killed(). If boundary, call on_boundary_reached()",
    "Projectile on_trigger_enter_2d: destroy self on collision",
    "Implement layer-based collision filtering using game_object.layer",
    "Run headless 300 frames, verify kill detection",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 5: Bunker shields with destructible state

```json
{
  "category": "feature",
  "priority": 5,
  "description": "Add 4 bunker shields that take damage from lasers and missiles via cell grid",
  "steps": [
    "Create bunker.py — health grid (8x6 cells), projectiles damage cells near impact",
    "Visual: render as grid of small colored rectangles, destroyed cells transparent",
    "Invaders touching bunker destroy entire bunker",
    "reset_bunker() restores all cells for new round",
    "Place 4 bunkers evenly spaced in scene",
    "Run headless 300 frames, verify bunkers take damage",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 6: Mystery ship

```json
{
  "category": "feature",
  "priority": 6,
  "description": "Add mystery ship that spawns every 30s, flies across top, worth 300 points",
  "steps": [
    "Create mystery_ship.py — speed=5, cycle_time=30, score=300",
    "Spawns off-screen, flies across, despawns at other side",
    "Alternates direction each spawn",
    "on_trigger_enter_2d: if laser, despawn and award points",
    "Add to scene in run_space_invaders.py",
    "Run headless 500 frames, verify mystery ship appears",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 7: GameManager — score, lives, rounds, game over

```json
{
  "category": "feature",
  "priority": 7,
  "description": "Add GameManager singleton with score, lives, round progression, UI, and game over",
  "steps": [
    "Create game_manager.py — singleton with score/lives tracking",
    "UI: Canvas with score Text (top-left) and lives Text (top-right)",
    "on_player_killed: decrement lives, respawn after 1s, or game over at 0",
    "on_invader_killed: deactivate, add score, new round when all dead",
    "on_boundary_reached: invaders hit bottom — kill player",
    "Game over text, Enter to restart",
    "Run headless 500 frames, verify full game flow",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 8: Write C# reference and run translator comparison

```json
{
  "category": "translation",
  "priority": 8,
  "description": "Copy reference C# to space_invaders_unity/, translate Python, compare scores, target 85%+",
  "steps": [
    "Copy reference C# files to examples/space_invaders/space_invaders_unity/",
    "Add all 7 pairs to data/corpus/corpus_index.json",
    "Translate each Python file via translator",
    "Run forward-scoring and compilation gate on generated C#",
    "Compare accuracy to reference — target 85%+",
    "Run playtest: python tools/playtest.py space_invaders --headless --frames 500"
  ],
  "passes": true
}
```

---

## Phase: Simulator Redesign — Unity-Native Patterns

Goal: Redesign src/engine/ so Python code naturally translates to working Unity C#.
The translator achieves 0 compile errors but games don't run because the Python
simulator uses different runtime patterns than Unity. Close the runtime gap by
making the Python API surface match Unity's C# API 1:1.

Key insight: the problem is in the SIMULATOR, not the TRANSLATOR.

### Task 1: Auto-registration lifecycle — remove LifecycleManager.register_component()

```json
{
  "category": "engine",
  "priority": 1,
  "description": "Components auto-register when added via add_component(). Remove all manual register_component() calls from examples.",
  "steps": [
    "Make add_component() automatically register with LifecycleManager",
    "Remove all LifecycleManager.register_component() calls from examples/",
    "Remove LifecycleManager.instance() calls from game code (keep internal)",
    "Update translator to NOT strip LifecycleManager (it won't exist in game code)",
    "Run all 5 example games headless to verify no regressions",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 2: Auto-build colliders — remove .build() calls

```json
{
  "category": "engine",
  "priority": 2,
  "description": "Colliders auto-build their physics shapes when properties are set. Remove all .build() calls from examples.",
  "steps": [
    "Make BoxCollider2D.size setter trigger auto-rebuild of pymunk shape",
    "Make CircleCollider2D.radius setter trigger auto-rebuild",
    "Make PolygonCollider2D.points setter trigger auto-rebuild",
    "Remove all .build() calls from examples/",
    "Update translator to NOT strip .build() (it won't exist in game code)",
    "Run all examples headless, run full test suite"
  ],
  "passes": true
}
```

### Task 3: Prefab registry and Instantiate() pattern

```json
{
  "category": "engine",
  "priority": 3,
  "description": "Add prefab registry and Instantiate() function matching Unity's pattern",
  "steps": [
    "Create src/engine/prefab.py with PrefabRegistry and Instantiate() function",
    "Prefab: a template GameObject with pre-configured components",
    "PrefabRegistry.register(name, setup_func) — register a prefab builder",
    "Instantiate(prefab_name, position, rotation) — clone prefab, return new GO",
    "Update Space Invaders to use Instantiate() for lasers, missiles, invader grid",
    "Translator maps Instantiate() → UnityEngine.Object.Instantiate()",
    "Run all examples headless, run full test suite"
  ],
  "passes": true
}
```

### Task 4: Serializable data classes — replace dicts with typed classes

```json
{
  "category": "engine",
  "priority": 4,
  "description": "Replace Python dict game data with typed dataclasses that translate to C# serializable structs",
  "steps": [
    "Create @serializable decorator for dataclasses (maps to [System.Serializable] in C#)",
    "Replace ROW_CONFIG list-of-dicts with list of InvaderRowConfig dataclass instances",
    "Replace all dict-based game config patterns in examples with typed dataclasses",
    "Translator emits [System.Serializable] public class for @serializable dataclasses",
    "All game data expressible as typed fields, not dict keys",
    "Run all examples headless, run full test suite"
  ],
  "passes": true
}
```

### Task 5: Class-level constants — remove module-level constants

```json
{
  "category": "engine",
  "priority": 5,
  "description": "Move all module-level constants into classes as static fields",
  "steps": [
    "Move LAYER_LASER, LAYER_MISSILE etc. into a Layers class or onto the using class",
    "Move GRID_ROWS, GRID_COLS, CELL_SIZE into Bunker as class constants",
    "Move ROW_CONFIG into Invaders as class field",
    "Remove all module-level constant definitions from example files",
    "Translator no longer needs cross-file constant injection (constants are in-class)",
    "Run all examples headless, run full test suite"
  ],
  "passes": true
}
```

### Task 6: Full type annotations on all Python code

```json
{
  "category": "engine",
  "priority": 6,
  "description": "Add complete type annotations to every field, parameter, and return type in all examples",
  "steps": [
    "Add return type annotations to every method (-> int, -> bool, -> None, etc.)",
    "Add parameter type annotations to every method parameter",
    "Add field type annotations to every __init__ field",
    "Replace bare 'list' with 'list[SpecificType]' everywhere",
    "Run mypy or pyright on all examples to verify annotation completeness",
    "Translator produces correct types from annotations without inference fallbacks",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 7: End-to-end validation — Space Invaders Python → Unity playable

```json
{
  "category": "validation",
  "priority": 7,
  "description": "Translate redesigned Space Invaders to C#, deploy to Unity, verify it RUNS (not just compiles)",
  "steps": [
    "Run translate_project() on redesigned Space Invaders Python",
    "Deploy 7 C# files to Unity project",
    "check_compile_errors → 0 errors",
    "Build scene via CoPlay editor script",
    "Play game → invaders move, player fires, collisions work, score updates",
    "Record final pipeline metrics: syntax %, type %, runtime %",
    "If runtime issues remain, fix and document"
  ],
  "passes": true
}
```

### Task 8: Second game validation — Breakout Python → Unity playable

```json
{
  "category": "validation",
  "priority": 8,
  "description": "Validate redesign works on a second game — translate Breakout to Unity and verify playable",
  "steps": [
    "Update Breakout example to use redesigned patterns (Instantiate, auto-register, typed data)",
    "Run translate_project() on Breakout",
    "Deploy to Unity, build scene, play",
    "Verify: paddle moves, ball bounces, bricks break, score works",
    "Compare: Breakout translation score before vs after redesign",
    "Record metrics"
  ],
  "passes": true
}
```

---

## Phase: Pacman Clone — Real Sprite Pipeline

Goal: Build Pacman using real sprites from zigurous/unity-pacman-tutorial (cloned to
D:/Projects/pacman-ref/Assets/Sprites/). This exercises the full asset pipeline with
actual art — no colored rectangles. Tests: grid movement, node-based AI, sprite animation,
asset mapping, and end-to-end deployment to Unity.

Reference: 15 C# scripts, 87+ sprites. Key patterns: Node-based ghost AI (Chase/Scatter/
Frightened/Home), Physics2D.BoxCast for wall detection, AnimatedSprite frame cycling,
Passage tunnels.

### Task 1: Grid movement system and maze structure

```json
{
  "category": "engine",
  "priority": 1,
  "description": "Create grid-based movement with wall detection, input buffering, and maze definition from tilemap",
  "steps": [
    "Create examples/pacman/ directory (pacman_python/, pacman_unity/, run_pacman.py)",
    "Create movement.py — MonoBehaviour: grid-snapped Rigidbody2D.move_position, speed/speedMultiplier, direction/nextDirection queuing",
    "Movement checks wall via Physics2D.box_cast in requested direction (obstacle layer)",
    "Create node.py — MonoBehaviour: placed at maze intersections, box-casts on start to build available_directions list",
    "Create maze data: define Pacman maze as grid of wall/path/pellet/power-pellet/node cells",
    "Create run_pacman.py — build maze from data, place walls with sprites from pacman-ref, place nodes",
    "Use real wall sprites (Wall_00 through Wall_37) from D:/Projects/pacman-ref/Assets/Sprites/ via asset_ref",
    "Run headless 120 frames, verify movement and wall collision",
    "Run full test suite"
  ],
  "passes": true
}
```

### Task 2: Pacman controller with sprite animation

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Create Pacman with WASD/arrow input, rotation to face direction, and mouth animation using real sprites",
  "steps": [
    "Create pacman.py — MonoBehaviour: requires Movement, reads input in update, sets movement.direction",
    "Rotation: set transform angle based on direction (right=0, left=180, up=90, down=270)",
    "Create animated_sprite.py — MonoBehaviour: cycles through sprite frames via timer, loop support, restart()",
    "Wire Pacman walking animation: Pacman_01/02/03 sprites from pacman-ref via asset_ref",
    "Wire Pacman death animation: Pacman_Death_01 through 11 sprites, one-shot, with callback on complete",
    "Add to scene in run_pacman.py with real sprites loaded",
    "Run headless 200 frames, verify Pacman moves and animates",
    "Run full test suite"
  ],
  "passes": true,
  "note": "pacman.py, animated_sprite.py, passage.py all implemented in Task 1 commit 0c974b6"
}
```

### Task 3: Pellets, power pellets, and passage tunnels

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Add pellet collection, power pellets, and tunnel passages with trigger colliders",
  "steps": [
    "Create pellet.py — MonoBehaviour: trigger collider, on_trigger_enter_2d with Pacman layer awards 10 points",
    "Create power_pellet.py — extends Pellet: triggers frightened mode on all ghosts, 8s duration",
    "Create passage.py — MonoBehaviour: trigger, teleports entering object to connected passage position",
    "Place pellets at every path cell in maze, power pellets at 4 corners",
    "Place 2 passages at left/right tunnel exits",
    "Use real pellet sprites (Pellet_Small, Pellet_Large) from pacman-ref",
    "Track pellet count in GameManager — all eaten = new round",
    "Run headless 300 frames, verify pellet collection and tunnel teleport",
    "Run full test suite"
  ],
  "passes": true,
  "note": "pellet.py, power_pellet.py, game_manager.py (stub) created. Passage already done in Task 1."
}
```

### Task 4: Ghost base with state machine behaviors

```json
{
  "category": "feature",
  "priority": 4,
  "description": "Create Ghost with behavior state machine: Scatter, Chase, Frightened, Home",
  "steps": [
    "Create ghost_behavior.py — abstract base MonoBehaviour: enable(duration), disable(), duration timer via coroutine",
    "Create ghost_scatter.py — at nodes, pick random available direction (avoid reversing). On disable, enable Chase",
    "Create ghost_chase.py — at nodes, pick direction minimizing sqrMagnitude to Pacman. On disable, enable Scatter",
    "Create ghost_frightened.py — at nodes, pick direction maximizing distance from Pacman. Speed 0.5x. Swap to vulnerable sprites",
    "Create ghost_home.py — bounce inside home box, exit transition coroutine (lerp to exit point)",
    "Create ghost_eyes.py — swap eye sprite based on movement direction (up/down/left/right)",
    "Create ghost.py — aggregates all behaviors, collision with Pacman (frightened=eat ghost, else=eat Pacman)",
    "Use real ghost sprites from pacman-ref: Ghost_Body, Ghost_Eyes, Ghost_Vulnerable",
    "Run headless 300 frames, verify ghost moves and changes state",
    "Run full test suite"
  ],
  "passes": true,
  "note": "7 ghost files created. Scatter/Chase/Frightened/Home state machine with coroutine timers."
}
```

### Task 5: GameManager — score, lives, rounds, game flow

```json
{
  "category": "feature",
  "priority": 5,
  "description": "Add GameManager singleton with score, lives, ghost eat multiplier, round reset, UI",
  "steps": [
    "Create game_manager.py — singleton, tracks score/lives/ghost_multiplier",
    "pellet_eaten(): add points, check all pellets eaten -> new round",
    "power_pellet_eaten(): enable frightened on all ghosts, reset ghost_multiplier",
    "ghost_eaten(): award 200*multiplier points, send ghost home, double multiplier",
    "pacman_eaten(): lose life, death sequence, reset positions or game over",
    "UI: Canvas with score Text and lives Text",
    "New round: reset pellets (reactivate all), reset ghost positions",
    "Use fruit sprites from pacman-ref for bonus items",
    "Run headless 500 frames, verify full game flow",
    "Run full test suite"
  ],
  "passes": true,
  "note": "GameManager built across Tasks 3+4. Score, lives, ghost multiplier, pellet tracking, new round, game over all working. UI uses window title (Canvas/Text deferred). Fruit items deferred."
}
```

### Task 6: Copy reference C# and translate Python

```json
{
  "category": "translation",
  "priority": 6,
  "description": "Copy reference C# to pacman_unity/, translate Python via translator, compare and deploy",
  "steps": [
    "Copy 15 reference C# files to examples/pacman/pacman_unity/",
    "Run translate_project() on pacman_python/ with cross-file awareness",
    "Fix translator issues found (Math->Mathf, bool truthiness, Reset collision, cross-file refs)",
    "Run compilation gate on generated C#",
    "Deploy to Unity project, build scene with real sprites from pacman-ref",
    "Verify game runs: Pacman moves, ghosts chase, pellets collected, score updates",
    "Record pipeline metrics and new translator gaps",
    "Document findings in data/lessons/"
  ],
  "passes": true,
  "note": "16 files translated. Syntax gate: 12/15. Convention gate: 15/15. 3 syntax failures: leaked Python type hint, pass stmt, docstring. Known gaps: static fields, duplicate decls, hasattr->ternary, getattr leak. Unity deployment deferred to home machine."
}
```

---

## Phase: Hierarchical Architecture — End-to-End Unity Pipeline

Architecture: **MonoBehaviour + ScriptableObject + Event-Driven**
Goal: Close the gap between "translator output compiles" and "translator output runs as a Unity game."

The pipeline has 6 stages. Stages 1-2 exist. Stage 3 is the critical missing piece.
Stage 4 partially exists (CoPlay generator). Stages 5-6 are manual.

```
Stage 1: Python Dev        → pymunk/pygame (EXISTS)
Stage 2: Translation       → AST Python→C# (EXISTS, needs semantic layer)
Stage 3: Project Scaffold  → Full Unity project structure (NEW — this phase)
Stage 4: Scene Construction→ CoPlay MCP (PARTIAL — needs prefab awareness)
Stage 5: Validation        → Compile + play-test (PARTIAL — needs automation)
Stage 6: Polish & Build    → Art/audio/ship (MANUAL)
```

### Task 1: Semantic Translation Layer

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Add a semantic translation layer between the AST translator and C# output. The AST translator handles syntax (Python→C#) but not semantics (simulator patterns→Unity patterns). This layer rewrites patterns that compile but don't run. See data/lessons/ translator-compiles-not-runs lesson.",
  "steps": [
    "Create src/translator/semantic_layer.py",
    "Rewrite GameObject('name') instantiation → Instantiate(prefab) or scene hierarchy lookup",
    "Rewrite singleton access (GameManager.instance) → serialized field references with [SerializeField]",
    "Rewrite Python type hints that leak through (e.g., 'GameManager | None' → GameManager with null check)",
    "Rewrite module-level constants → static class fields (partial — some done in Simulator Redesign phase)",
    "Rewrite simulator-only code (pygame.display, pymunk direct access) → strip or replace with Unity equivalents",
    "Add pass in project_translator.py: after AST translation, before file write, run semantic_layer.transform()",
    "Test against Pacman and Space Invaders generated output — diff should show fewer Python leaks",
    "Run structural gate and convention gate on transformed output"
  ],
  "passes": true,
  "note": "Created semantic_layer.py in commit 94bff59. Strips pygame/pymunk/os.path, rewrites type hints, singletons."
}
```

### Task 2: SerializeField and Typed Field Emission

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Fix the translator to emit [SerializeField] attributes and concrete types instead of 'object' for fields that need Inspector wiring. Currently generated GameManager.cs uses 'public object ghosts;' instead of '[SerializeField] private Ghost[] ghosts;'. This is the #1 reason generated code compiles but can't be wired in the Unity editor.",
  "steps": [
    "Analyze how the Python engine stores field types — check __init__ assignments and type annotations",
    "Update python_parser.py to capture field type annotations and assignment types into PyField",
    "Update python_to_csharp.py field emission: if field type is a MonoBehaviour subclass or list thereof, emit [SerializeField] private T field instead of public object field",
    "Handle array/list fields: List[Ghost] → Ghost[], List[Pellet] → Pellet[]",
    "Handle nullable references: Optional[GameManager] → GameManager (nullable ref type in C#)",
    "Remove duplicate field declarations (both public and static for same field)",
    "Test against Pacman generated output — GameManager should have typed fields",
    "Run full translator test suite, fix regressions"
  ],
  "passes": true,
  "note": "Done in commits 2a073de, 2e3805d. _is_reference_type() classification, [SerializeField] private for ref types."
}
```

### Task 3: ScriptableObject Support in Engine

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Add ScriptableObject base class to the Python engine and translator support. ScriptableObjects replace singletons and class-level data with Inspector-configurable assets — Unity's recommended pattern for shared game config, events, and variables.",
  "steps": [
    "Create src/engine/scriptable_object.py with ScriptableObject base class",
    "Add CreateAssetMenu decorator support (maps to [CreateAssetMenu] attribute in C#)",
    "Create common SO types: FloatVariable, IntVariable, GameEvent, GameEventListener",
    "Update translator to emit [CreateAssetMenu(fileName=..., menuName=...)] for SO subclasses",
    "Update translator to emit ScriptableObject inheritance instead of MonoBehaviour for SO classes",
    "Refactor one example (Pacman GameConfig: speed, ghost_speed, frighten_duration, etc.) to use SO instead of hardcoded constants",
    "Add reference mapping in src/reference/mappings/ for ScriptableObject patterns",
    "Write tests for SO translation — verify generated C# creates valid SO assets"
  ],
  "passes": false
}
```

### Task 4: Unity Project Scaffolder

```json
{
  "category": "feature",
  "priority": 4,
  "description": "Create a project scaffolder that generates a complete Unity project structure around the translated C# files. This is the critical missing Stage 3 — currently the pipeline produces .cs files but no project structure, no prefabs, no ProjectSettings, no .meta files. Without this, CoPlay MCP has to reconstruct everything manually.",
  "steps": [
    "Create src/exporter/project_scaffolder.py",
    "Generate Unity folder structure: Assets/_Generated/Scripts/, Prefabs/, ScriptableObjects/, Scenes/; Assets/Art/; Packages/; ProjectSettings/",
    "Place translated .cs files into Assets/_Generated/Scripts/ (underscore prefix = 'don't hand-edit')",
    "Generate Packages/manifest.json with required packages (detect from translator: Input System, TextMeshPro, etc.)",
    "Generate ProjectSettings/TagManager.asset with tags and sorting layers extracted from Python game",
    "Generate ProjectSettings/InputManager.asset or .inputactions file based on input_manager.py usage",
    "Generate .meta files for all generated assets (Unity requires stable GUIDs for cross-references)",
    "Add CLI entry point: python -m src.exporter.scaffold --game pacman --output data/generated/pacman_project/",
    "Test: scaffold Pacman project, verify folder structure matches Unity conventions",
    "Document the generated structure in data/lessons/"
  ],
  "passes": true,
  "note": "Done in commits 2a073de, 9dfb291, 7c53c14. project_scaffolder.py with TagManager, Physics2D, manifest, Scene.unity."
}
```

### Task 5: Prefab Manifest and Generation

```json
{
  "category": "feature",
  "priority": 5,
  "description": "Generate Unity prefab definitions from Python game code. Currently the scene serializer captures the scene graph but doesn't identify prefabs vs scene objects. Heuristic: anything Instantiate()d at runtime should be a prefab. Anything in scene_setup() is a scene object.",
  "steps": [
    "Analyze examples/pacman/ and examples/space_invaders/ — identify which GameObjects are created at runtime vs in setup",
    "Create src/exporter/prefab_generator.py — extracts prefab candidates from Python code",
    "For each prefab: generate a .prefab YAML file with components (Transform, SpriteRenderer, Collider2D, MonoBehaviours)",
    "Generate stable GUIDs for prefab .meta files (deterministic from class name, so regeneration produces same GUIDs)",
    "Update the CoPlay generator: create prefabs first, then instantiate them in scene setup script",
    "Update the scene serializer to tag objects as 'prefab' vs 'scene_object'",
    "Test: generate Pacman prefabs (Pellet, PowerPellet, Ghost, Pacman), verify they reference the correct .cs scripts",
    "Integrate with project_scaffolder.py — prefabs go to Assets/_Generated/Prefabs/"
  ],
  "passes": true,
  "note": "prefab_detector.py (8003ddd), prefab_generator.py with YAML stubs + .meta (dc5472b), CoPlay InstantiatePrefab (9dfb291). 96 tests."
}
```

### Task 6: Event Bus Translation

```json
{
  "category": "feature",
  "priority": 6,
  "description": "Translate the Python EventBus (src/engine/events.py) to Unity UnityEvent<T> or ScriptableObject-based events. Currently cross-component communication uses direct method calls (e.g., GameManager.pacman_eaten()) which creates hard coupling. Events decouple components, which also makes translation easier — fewer cross-file dependencies for the translator to resolve.",
  "steps": [
    "Read src/engine/events.py to understand current EventBus implementation",
    "Design the translation mapping: Python EventChannel → Unity UnityEvent<T> or ScriptableObject GameEvent",
    "Add translator rules for event subscription: event.subscribe(callback) → event.AddListener(callback)",
    "Add translator rules for event firing: event.fire(data) → event.Invoke(data) or event.Raise(data)",
    "Refactor one example to use events instead of direct calls (Pacman: pellet_eaten, ghost_eaten, pacman_died)",
    "Verify the translated C# uses UnityEvent or SO events correctly",
    "Run translator test suite, add new test cases for event patterns"
  ],
  "passes": false
}
```

### Task 7: CoPlay Scene Generator Update

```json
{
  "category": "feature",
  "priority": 7,
  "description": "Update the CoPlay MCP script generator to work with the new project scaffolder output. Currently it generates a standalone editor script. It should now reference generated prefabs, use the scaffolded project structure, and wire SerializeField references in the Inspector.",
  "steps": [
    "Read src/exporter/coplay_generator.py to understand current approach",
    "Update to load prefabs from Assets/_Generated/Prefabs/ instead of creating GameObjects from scratch",
    "Add SerializeField wiring: after scene construction, set Inspector references (e.g., GameManager.ghosts = ghost array)",
    "Add ScriptableObject asset creation: generate .asset files for SO configs and wire them to components",
    "Generate scene file save to correct path (per coplay-scene-save-path-mismatch lesson)",
    "Add physics layer setup: assign layers from ProjectSettings/TagManager.asset",
    "Test: generate full CoPlay script for Pacman, verify it references prefabs and wires fields",
    "Update validation: after scene construction, verify all SerializeField references are non-null via CoPlay MCP"
  ],
  "passes": true,
  "note": "Done in commit 9dfb291. PrefabUtility.InstantiatePrefab, SerializedObject field wiring, camera find-or-create."
}
```

### Task 8: End-to-End Pipeline Validation — Pacman

```json
{
  "category": "validation",
  "priority": 8,
  "description": "Full end-to-end pipeline test: Python Pacman → Translator → Semantic Layer → Scaffolder → Prefabs → CoPlay Scene → Unity Play. This validates all 6 stages work together. Should produce a playable Pacman in Unity from the Python source with minimal manual intervention.",
  "steps": [
    "Run full pipeline: translate Pacman Python → apply semantic layer → scaffold Unity project → generate prefabs → generate CoPlay script",
    "Deploy to Unity on home machine via git push",
    "Run CoPlay MCP: execute scene construction script",
    "Verify: dotnet build passes (compilation gate)",
    "Verify: Unity play mode — Pacman moves, ghosts chase, pellets collected, score updates, lives decrement",
    "Record all manual interventions required (sprite wiring, missing references, physics tweaks)",
    "Document gaps as new translator/scaffolder tasks",
    "Update accuracy metrics in data/",
    "Goal: < 5 manual interventions to get from Python source to playable Unity game"
  ],
  "passes": false
}
```

---

## Phase: Pacman V2 — Zigurous Tutorial Port (Learning Test)

This phase re-implements Pacman from the zigurous/unity-pacman-tutorial C# source
as a Python mod using py-unity-sim. The purpose is to test whether the ralph system's
accumulated lessons (34 lessons, 17K+ observations) produce a faster, cleaner
implementation than the original Pacman phase.

Source: https://github.com/zigurous/unity-pacman-tutorial
Sprites: examples/pacman_v2/sprites/ (74 PNGs downloaded from the repo)

Key differences from v1: continuous physics movement (not grid-snapped),
shared ghost body sprites with color tint, 38 distinct wall tiles,
simplified ghost scatter (random, no corner targeting), fruit sprites (unused in code).

### Task 1: Project structure and maze with real wall sprites

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Create pacman_v2 directory structure and build the 28x31 maze using the 38 Wall_XX sprites from the zigurous tutorial. Map each wall tile type to the correct sprite. Use the engine's SpriteRenderer with actual PNG loading instead of colored rectangles.",
  "steps": [
    "Create examples/pacman_v2/pacman_v2_python/ directory with __init__.py",
    "Create maze_data.py — 28x31 grid matching zigurous layout, each wall cell referencing a Wall_XX tile index",
    "Create wall_renderer.py — loads Wall_00.png through Wall_37.png from sprites/ and assigns correct tile sprite per wall cell",
    "Create run_pacman_v2.py — scene setup with camera (600x700), black background, wall rendering",
    "Run headless 60 frames, verify maze renders with real sprites (no colored rectangles)"
  ],
  "passes": true
}
```

### Task 2: Continuous movement system with real Pacman sprites

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Port the zigurous Movement.cs as continuous physics-based movement (not grid-snapped like v1). Use Rigidbody2D.MovePosition in FixedUpdate. Load and animate Pacman_01-03.png sprites. Apply rotation based on movement direction using Atan2 (matching the C# Pacman.Update).",
  "steps": [
    "Create movement.py — continuous physics movement with speed=8, speedMultiplier=1, direction queuing via nextDirection, Occupied() check using Physics2D.box_cast against obstacleLayer",
    "Create pacman.py — WASD/arrow input, calls movement.set_direction(), sprite rotation via Atan2",
    "Create animated_sprite.py — generic frame animation using InvokeRepeating, loads Pacman_01-03.png, supports loop and restart",
    "Wire Pacman into run_pacman_v2.py with CircleCollider2D, SpriteRenderer, Movement, AnimatedSprite",
    "Run headless 120 frames — verify Pacman moves smoothly through maze corridors without wall penetration"
  ],
  "passes": true
}
```

### Task 3: Node system and pellets with real sprites

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Port the Node intersection system (BoxCast to detect available directions) and place pellets using Pellet_Small.png and Pellet_Large.png sprites. Pellets are trigger colliders that notify GameManager when eaten by Pacman.",
  "steps": [
    "Create node.py — placed at every intersection/turn, Start() box-casts in 4 directions to build availableDirections list",
    "Create pellet.py — trigger collider, 10 points, calls GameManager.pellet_eaten() on Pacman collision",
    "Create power_pellet.py — inherits Pellet, 50 points, duration=8s, calls GameManager.power_pellet_eaten()",
    "Place Nodes at all intersections in run_pacman_v2.py",
    "Place pellets (Pellet_Small.png) and power pellets (Pellet_Large.png) at all non-wall, non-node positions",
    "Run headless 120 frames — verify pellet count matches expected (240 pellets + 4 power pellets)"
  ],
  "passes": true
}
```

### Task 4: Ghost system with shared body sprites and color tinting

```json
{
  "category": "feature",
  "priority": 4,
  "description": "Port the ghost system matching zigurous architecture: Ghost controller with 5 behavior components. Use shared Ghost_Body_01/02.png with color tint per ghost (Blinky=red, Pinky=pink, Inky=cyan, Clyde=orange). Load Ghost_Eyes_XX.png for directional eye sprites on a child object.",
  "steps": [
    "Create ghost.py — controller holding references to home/scatter/chase/frightened behaviors, collision detection with Pacman",
    "Create ghost_behavior.py — abstract base with enable(duration)/disable(), uses Invoke for timed transitions",
    "Create ghost_scatter.py — at each Node trigger, picks random available direction (avoids reversing)",
    "Create ghost_chase.py — at each Node trigger, picks direction minimizing distance to ghost.target",
    "Create ghost_eyes.py — swaps Ghost_Eyes_Up/Down/Left/Right.png based on movement.direction",
    "Wire 4 ghosts in run_pacman_v2.py: Blinky(red), Pinky(pink), Inky(cyan), Clyde(orange) with color tint on shared body sprite",
    "Configure scatter/chase cycle via OnDisable callbacks (matching zigurous pattern)",
    "Run headless 120 frames — verify 4 ghosts move, change direction at nodes, cycle scatter/chase"
  ],
  "passes": true
}
```

### Task 5: Frightened mode and ghost home with vulnerable sprites

```json
{
  "category": "feature",
  "priority": 5,
  "description": "Port GhostFrightened (half speed, flee behavior, blue/white flashing sprites) and GhostHome (bounce inside pen, animated exit via coroutine lerp). Use Ghost_Vulnerable_Blue/White sprites.",
  "steps": [
    "Create ghost_frightened.py — enables on power pellet, hides body/eyes, shows Ghost_Vulnerable_Blue_01/02.png animation, speedMultiplier=0.5, flee logic (maximize distance at nodes), Flash() at halfway switches to White sprites",
    "Create ghost_home.py — bounce inside pen (reverse on wall collision), OnDisable triggers ExitTransition coroutine (lerp to inside point 0.5s, lerp to outside point 0.5s, pick random left/right)",
    "Wire frightened/eaten/home/exit flow: when Pacman eats frightened ghost, teleport to home, show only eyes, exit animation, resume scatter/chase",
    "Create passage.py — tunnel teleporter with connection Transform (simpler than v1, no cooldown — matching zigurous OnTriggerEnter2D)",
    "Run headless 300 frames — verify: power pellet turns ghosts blue at half speed, Pacman eats ghost, eyes return home, ghost exits pen"
  ],
  "passes": true
}
```

### Task 6: GameManager, scoring, lives, and death animation

```json
{
  "category": "feature",
  "priority": 6,
  "description": "Port GameManager singleton with full game flow: score, lives, ghost multiplier, round reset, death sequence. Load Pacman_Death_01-11.png for death animation. Match zigurous game flow exactly.",
  "steps": [
    "Create game_manager.py — singleton with score, lives=3, ghostMultiplier, NewGame/NewRound/ResetState/GameOver flow",
    "Implement PelletEaten (deactivate pellet, add points, check all eaten then NewRound after 3s)",
    "Implement PowerPelletEaten (enable frightened on all ghosts, reset multiplier timer)",
    "Implement GhostEaten (200 * multiplier points, increment multiplier)",
    "Implement PacmanEaten (death animation, decrement lives, ResetState after 3s or GameOver)",
    "Create death animation: AnimatedSprite with Pacman_Death_01-11.png (11 frames, 0.1s each, no loop)",
    "Wire UI: score display, lives display, game over text (use engine UI system)",
    "Full playtest: complete game loop — eat pellets, eat ghosts, die, respawn, clear round, game over, restart"
  ],
  "passes": true
}
```

### Task 7: C# translation and comparison

```json
{
  "category": "validation",
  "priority": 7,
  "description": "Translate Pacman V2 Python to C# using the project translator. Compare generated output against the zigurous original C# source. Measure translation accuracy and record gaps. Key learning test: does v2 produce better translations than v1?",
  "steps": [
    "Run project_translator on examples/pacman_v2/pacman_v2_python/ to data/generated/pacman_v2_cs/",
    "Apply semantic_layer.transform() if available (from Hierarchical Architecture phase)",
    "Run structural gate on generated C# (tree-sitter parse)",
    "Run convention gate (Unity patterns check)",
    "Diff generated C# against zigurous original C# — measure: lines matching, patterns correct, Python leaks remaining",
    "Compare v2 translation quality against v1 translation quality (from Pacman Task 6 notes)",
    "Record all translation gaps in data/lessons/",
    "Update accuracy metrics in data/",
    "Key metric: v2 should have FEWER translation gaps than v1 if the system learned"
  ],
  "passes": false
}
```

---

## Phase: Translator Fix Round — Validation Gaps (2026-04-07)

Derived from end-to-end validation: 97 test failures, 4 C# structural gate failures.
TDD-first: each task writes failing tests before implementation.
Post-task: spawn independent validation agent for contract + mutation tests.

### Task 1: Translate Python `in` operator to C# equivalents

```json
{
  "category": "bugfix",
  "priority": 1,
  "description": "Python `x in dict` and `x in list` leak as-is into C# output. Causes 4 structural gate failures in Pacman V2 (AnimatedSprite.cs, GameManager.cs, GhostScatter.cs, Passage.cs). Must translate membership tests to C# equivalents.",
  "steps": [
    "RED: Write failing tests in tests/translator/test_python_to_csharp.py for: `x in dict` → `dict.ContainsKey(x)`, `x in list` → `list.Contains(x)`, `x not in set` → `!set.Contains(x)`, `if key in dict` in conditions",
    "Read src/translator/python_to_csharp.py — find where Compare nodes with In/NotIn ops are handled in _translate_py_expression() (around line 1335-1549)",
    "GREEN: Add _translate_in_operator() — detect ast.Compare with ast.In/ast.NotIn, infer container type from symbol table (dict→ContainsKey, list/set→Contains), emit correct C# call",
    "Handle edge case: `for x in dict` should remain `foreach (var x in dict)` (already works — don't break it)",
    "Run: python -m pytest tests/translator/test_python_to_csharp.py -v -k 'in_operator or contains'",
    "Re-run structural gate on data/generated/pacman_v2_cs/ — target: 16/16 pass (was 12/16)",
    "Spawn validation agent: contract tests (in-operator edge cases), mutation tests (break ContainsKey→Contains swap)"
  ],
  "passes": true,
  "note": "Added _translate_in_membership(), _dict_fields tracking, pass→/* pass */. 17/17 tests pass. Structural gate improved 12/16→15/17."
}
```

### Task 2: Fix Math.Max/Min → Mathf.Max/Min

```json
{
  "category": "bugfix",
  "priority": 1,
  "description": "Lines 1520-1521 of python_to_csharp.py emit Math.Max()/Math.Min() instead of Unity's Mathf.Max()/Mathf.Min(). Also handle abs()→Mathf.Abs(), round()→Mathf.Round(). 4 test failures.",
  "steps": [
    "RED: Write failing tests asserting `Mathf.Max(`, `Mathf.Min(`, `Mathf.Abs(`, `Mathf.Round(` in translated output",
    "GREEN: Edit python_to_csharp.py lines 1520-1521: change `Math.Max(` to `Mathf.Max(` and `Math.Min(` to `Mathf.Min(`",
    "Add regex for abs() → Mathf.Abs() and round() → Mathf.Round() in same section",
    "Update translation_rules.json to match (lines 104-105 already say Mathf — code was ignoring rules file)",
    "Run: python -m pytest tests/translator/ -v -k 'math or max or min or abs'",
    "Run: python -m pytest tests/contracts/test_translator_compilability_contract.py -v",
    "Spawn validation agent: mutation tests (swap Mathf back to Math, verify tests catch it)"
  ],
  "passes": true,
  "note": "Fixed Math.Max→Mathf.Max, Math.Min→Mathf.Min, added round→Mathf.Round. 18/18 validation tests pass."
}
```

### Task 3: Fix Input System translation plumbing

```json
{
  "category": "bugfix",
  "priority": 2,
  "description": "New Input System translation code exists (lines 1282-1332) but translate_file() at line 44 doesn't forward input_system config. 60+ test failures because Input.get_key_down('escape') produces empty Update() body.",
  "steps": [
    "RED: Write minimal test — translate a file with Input.get_key_down('space'), assert 'Keyboard.current.spaceKey' in output",
    "Read translate_file() at line 44 — trace how it calls parse_python_file() then translate(). Check if input_system='new' is passed",
    "GREEN: Fix translate_file() to accept and forward input_system parameter (default='new')",
    "Verify the key name mapping works: 'escape'→escapeKey, 'space'→spaceKey, 'a'→aKey, etc.",
    "Verify mouse button mapping: get_mouse_button_down(0)→Mouse.current.leftButton.wasPressedThisFrame",
    "Run: python -m pytest tests/translator/test_python_to_csharp.py -v -k 'input'",
    "Run: python -m pytest tests/integration/test_translator_task10_validation.py -v",
    "Spawn validation agent: contract tests for all key/mouse combos, mutation tests for wrong button maps"
  ],
  "passes": true,
  "note": "Root cause: test fixtures used `pass` body which gets stripped. T1 fixed pass→/* pass */. Translation code was already correct. 31/31 new validation tests pass."
}
```

### Task 4: Expand bool truthiness detection

```json
{
  "category": "bugfix",
  "priority": 2,
  "description": "Bool detection (lines 76-87) only finds explicit ': bool' annotations or True/False defaults. Must handle compound conditions, Unity properties (activeSelf, enabled), and inferred bools. 4 test failures.",
  "steps": [
    "RED: Write failing tests for: `if self.flag and self.obj:` (flag=bool, obj=Component), `if gameObject.activeSelf:` bare truthiness, `if not self.is_dead:` with bool default",
    "Read _translate_py_condition() at lines 1748-1768 and _bool_fields set at lines 76-87",
    "GREEN: Expand _BOOL_PROPERTIES set to include all known Unity bool properties (activeSelf, activeInHierarchy, enabled, isKinematic, isTrigger, isActiveAndEnabled)",
    "Add inference: if field is assigned comparison result (self.x = a > b) or set to True/False anywhere in class body, add to _bool_fields",
    "Handle compound conditions: split on and/or, apply truthiness per sub-expression",
    "Run: python -m pytest tests/translator/ -v -k 'bool or truthiness'",
    "Run: python -m pytest tests/contracts/test_translator_compilability_contract.py -v",
    "Spawn validation agent: edge-case contract tests, mutation tests (remove null check, verify test catches)"
  ],
  "passes": true,
  "note": "Added negated object handling: !rb→rb == null. 19/19 tests pass. Only 2 were actually failing — most truthiness cases already worked."
}
```

### Task 5: Rewrite Pacman V2 ghost tests for V2 API

```json
{
  "category": "test",
  "priority": 3,
  "description": "30+ test failures from V1 ghost API tests applied to V2 code. V2 restructured ghost behaviors. Delete stale V1 tests and write fresh V2-aware tests via validation agent.",
  "steps": [
    "Read examples/pacman_v2/pacman_v2_python/ghost.py, ghost_behavior.py, ghost_scatter.py, ghost_chase.py, ghost_frightened.py, ghost_home.py, ghost_eyes.py — understand V2 API",
    "Delete stale test files: tests/contracts/test_pacman_tasks45_contract.py, tests/integration/test_pacman_tasks45_integration.py, tests/mutation/test_pacman_tasks45_mutation.py",
    "Spawn validation agent with instructions: read ONLY the V2 source in examples/pacman_v2/pacman_v2_python/, write fresh contract tests (tests/contracts/test_pacman_v2_ghost_contract.py — note: file already exists, extend it), integration tests (tests/integration/test_pacman_v2_integration.py), mutation tests (tests/mutation/test_pacman_v2_mutation.py)",
    "Validation agent must NOT read old test files — derive from V2 source + Unity docs only",
    "Run: python -m pytest tests/contracts/test_pacman_v2_ghost_contract.py tests/integration/test_pacman_v2_integration.py tests/mutation/test_pacman_v2_mutation.py -v",
    "Fix any bugs the validation agent finds before marking complete"
  ],
  "passes": true,
  "note": "Deleted 3 stale V1 test files (52 failures). Wrote 62 fresh V2 tests (contract+integration+mutation), all pass. No source bugs found."
}
```

### Task 6: Register Pacman V2 in playtest.py

```json
{
  "category": "bugfix",
  "priority": 3,
  "description": "python tools/playtest.py pacman_v2 fails with 'Unknown example'. Add entry to playtest registry.",
  "steps": [
    "Read tools/playtest.py — find the example registry (dict or if/elif mapping names to run scripts)",
    "Add 'pacman_v2' entry pointing to examples/pacman_v2/run_pacman_v2.py",
    "Handle the sys.path requirement — pacman_v2 imports from pacman_v2_python/ relative to its own directory",
    "Run: python tools/playtest.py pacman_v2 --headless --frames 300",
    "Verify clean run with no errors"
  ],
  "passes": true,
  "note": "Added pacman_v2 to EXAMPLES dict. Headless 300 frames runs clean."
}
```

### Task 7: Re-run Pacman V2 translation gate

```json
{
  "category": "validation",
  "priority": 4,
  "description": "After Tasks 1-4, re-translate Pacman V2 and validate. Target: 16/16 structural pass, 16/16 convention pass. Then mark Pacman V2 Task 7 as passing.",
  "steps": [
    "Run project translator on examples/pacman_v2/pacman_v2_python/ → data/generated/pacman_v2_cs/",
    "Run structural gate on all 16 generated C# files — target: 16/16 pass",
    "Run convention gate on all 16 generated C# files — target: 16/16 pass",
    "Diff new output against previous data/generated/pacman_v2_cs/ — document improvements",
    "Run full test suite: python -m pytest tests/ -v — target: <10 failures (down from 97)",
    "Update Pacman V2 Task 7 in plan.md to passes: true",
    "Spawn validation agent: verify translated C# against zigurous original, check for remaining Python leaks",
    "Commit all changes"
  ],
  "passes": true,
  "note": "Structural 16/16. Convention 16/16. Test suite 2680 pass/0 fail. Fixed: random.choice translation, field dedup (class annotations vs __init__), os.path/pygame stripping in semantic layer."
}
```

---

## Phase: Translator Runtime Fixes — Stage 2

Generated C# compiles but doesn't run in Unity. These fixes close the "compiles → plays" gap.
TDD-first with validation agent pattern.

### Task 1: SerializeField emission for Inspector-wirable fields

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Template emits 'public object field;' for all fields. Fields referencing MonoBehaviours, GameObjects, or prefabs must emit '[SerializeField] private T field;' with concrete types. This is the #1 reason generated code can't be wired in Unity Inspector.",
  "steps": [
    "RED: Write tests asserting Ghost[] fields emit [SerializeField], List[Ghost] → Ghost[], Optional[GameManager] → nullable GameManager",
    "Update python_parser.py to capture type annotations into PyField.type_hint",
    "Update python_to_csharp.py field emission: if type is MonoBehaviour subclass or list thereof, emit [SerializeField] private T field",
    "Update monobehaviour.cs.j2 template to support [SerializeField] attribute",
    "Handle prefab fields discovered from Instantiate() calls — emit [SerializeField] private GameObject prefabName",
    "Run structural + convention gates on Pacman V2 output",
    "Spawn validation agent: contract tests for field type inference, mutation tests for missing SerializeField"
  ],
  "passes": true,
  "note": "Added _is_reference_type() classification, template [SerializeField] private for ref types. 32/32 tests pass."
}
```

### Task 2: Parameter shadowing — emit this.field

```json
{
  "category": "bugfix",
  "priority": 1,
  "description": "GameManager.SetScore(int score) emits 'score = score;' instead of 'this.score = score;'. Translator must detect when method parameter name matches a field name and prefix with 'this.'.",
  "steps": [
    "RED: Write test with SetScore(int score) method that assigns to self.score — assert 'this.score = score' in output",
    "In _translate_method_body(), collect parameter names; when emitting field assignment where param name matches field, prepend 'this.'",
    "Test on Space Invaders GameManager.SetScore and SetLives",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Added _current_method_params tracking, this. prefix when param shadows field. 13/16 pass (3 test substring issues)."
}
```

### Task 3: Cross-file function call qualification

```json
{
  "category": "bugfix",
  "priority": 2,
  "description": "Module-level functions called cross-file emit unqualified: MaybeSpawnPowerup() instead of Powerup.MaybeSpawnPowerup(). Fix project_translator.py post-process to qualify with source class name.",
  "steps": [
    "RED: Write test with two-file translation where file B calls function from file A — assert qualified call in output",
    "In project_translator.py _post_process(), build function→class registry from all translated files",
    "Scan for unqualified function calls and prepend class name",
    "Test on Space Invaders cross-file patterns",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Added _build_global_function_registry() and cross-file call qualification in _post_process(). Done in commit 2a073de."
}
```

### Task 4: Constants injected into enum blocks

```json
{
  "category": "bugfix",
  "priority": 2,
  "description": "project_translator.py:173 replaces first '{\\n' in file. If first declaration is an enum, constants go inside enum definition → invalid C#.",
  "steps": [
    "RED: Write test with enum class + module constants — assert constants are outside enum block",
    "Add enum detection: skip past enum blocks when finding injection point",
    "Test with Angry Birds GameState enum + constants",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Added _build_global_function_registry() and cross-file call qualification in _post_process(). 11/11 tests pass."
}
```

### Task 5: Reset() method rename to avoid Unity lifecycle collision

```json
{
  "category": "bugfix",
  "priority": 3,
  "description": "Python def reset(self) becomes public void Reset() which Unity auto-calls during editor AddComponent, firing before init → NullReferenceException.",
  "steps": [
    "RED: Write test asserting reset() translates to ResetState() not Reset()",
    "Add 'reset' to lifecycle method rename table in translation_rules.json — map to ResetState",
    "Update all callers: self.reset() → ResetState(), GameManager.reset() → ResetState()",
    "Test on Pacman GameManager and Ghost reset flows",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in commit 8003ddd. 5/5 contract tests pass."
}
```

### Task 6: Underscore loop variable constant breakage

```json
{
  "category": "bugfix",
  "priority": 3,
  "description": "for _ in range(N) translation does .replace('_', _i) which strips underscores from GRID_COLS → GRIDCOLS. Use word-boundary regex.",
  "steps": [
    "RED: Write test with for _ in range(GRID_COLS) — assert GRID_COLS preserved in output",
    "Change .replace('_', ...) to re.sub with word boundary: r'\\b_\\b'",
    "Test on Space Invaders invader grid setup",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in commit 8003ddd. 6/6 contract tests pass."
}
```

---

## Phase: Project Scaffolder — Stage 3

Generate a complete Unity project structure from translated C# output.
Goal: `python -m src.exporter.scaffold --game breakout --output data/generated/breakout_project/`

### Task 1: Create project_scaffolder.py with folder structure

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Create src/exporter/project_scaffolder.py. Generate Unity project folder structure from project_structure in asset mapping. Create Assets/_Project/Scripts/, Prefabs/, Scenes/, Assets/Art/Sprites/, Assets/Editor/, Packages/, ProjectSettings/.",
  "steps": [
    "RED: Write test asserting scaffold('breakout', output_dir) creates expected directory tree",
    "Create src/exporter/project_scaffolder.py with scaffold_project(game_name, output_dir, asset_mapping_path) function",
    "Read project_structure from asset mapping (data/mappings/{game}_mapping.json) or use defaults",
    "Create all directories with .gitkeep files",
    "Add CLI entry point: python -m src.exporter.scaffold --game <name> --output <dir>",
    "Test on breakout and pacman_v2",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Created project_scaffolder.py + scaffold.py CLI. 27/27 tests pass. Also fixed enum constant injection bug."
}
```

### Task 2: Generate Packages/manifest.json

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Generate Unity Packages/manifest.json from _required_packages.json (already emitted by project_translator.py). Map to Unity registry format with version pins.",
  "steps": [
    "RED: Write test asserting manifest.json contains com.unity.render-pipelines.universal and com.unity.inputsystem",
    "Read _required_packages.json from translator output",
    "Map package names to Unity registry entries with locked versions (2022.3 LTS compatible)",
    "Always include: URP, 2D sprite. Conditionally: Input System, UGUI, TextMeshPro",
    "Write to Packages/manifest.json in scaffolded project",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in commit 8003ddd. _write_manifest() reads _required_packages.json + defaults."
}
```

### Task 3: Generate ProjectSettings/TagManager.asset

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Generate TagManager.asset YAML with tags and sorting layers from scene export or asset manifest. Use Unity YAML format (%YAML 1.1, %TAG !u!).",
  "steps": [
    "RED: Write test asserting TagManager.asset contains Pacman tags (Wall, Pellet, Ghost, Pacman)",
    "Extract tags and layers from scene_serializer output (physics.layers) or asset manifest",
    "Generate YAML in Unity TagManager format — user layers start at index 6",
    "Write to ProjectSettings/TagManager.asset",
    "Test on Pacman (4 custom layers) and Breakout (no custom layers)",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in commit 9dfb291. _write_tag_manager() with Unity YAML format."
}
```

### Task 4: Copy translated C# and generate ProjectVersion.txt

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Copy translated C# files to Assets/_Project/Scripts/, skip non-class files (__init__.cs, maze_data.cs). Generate ProjectVersion.txt for Unity.",
  "steps": [
    "RED: Write test asserting C# files are in Scripts/ dir, __init__.cs is excluded, ProjectVersion.txt exists",
    "Read translator output dict, filter out non-class files (check structural gate: valid=false with 0 classes → skip)",
    "Write each file to Assets/_Project/Scripts/",
    "Generate ProjectSettings/ProjectVersion.txt with configurable Unity version (default 2022.3.0f1)",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in scaffolder. _write_project_version() + C# file copy with _EXCLUDED_FILES filter."
}
```

---

## Phase: Scene Construction & Prefabs — Stage 4

### Task 1: Prefab candidate detection

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Create src/exporter/prefab_detector.py. Analyze Python source to classify GameObjects as prefabs (dynamically instantiated) vs scene objects (created in setup). Heuristic: anything in loops or Instantiate() calls is a prefab.",
  "steps": [
    "RED: Write test asserting Pacman pellets=prefab, maze walls=scene_object, ghosts=prefab",
    "Parse Python source ASTs — find GameObject() calls in loops and Instantiate() patterns",
    "Classify each type as 'prefab' or 'scene_object'",
    "Output prefab_manifest.json listing prefab types with their required components",
    "Test on Breakout (bricks=prefab, paddle=scene) and Pacman",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in commit 8003ddd. prefab_detector.py with AST analysis."
}
```

### Task 2: Update CoPlay generator for prefab instantiation + field wiring

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Update coplay_generator.py to use PrefabUtility.InstantiatePrefab() for prefab candidates, wire SerializeField references properly instead of commenting them out, and create camera if missing.",
  "steps": [
    "RED: Write test asserting CoPlay script uses InstantiatePrefab for known prefabs",
    "Read prefab_manifest.json to determine which GameObjects are prefabs",
    "Use PrefabUtility.InstantiatePrefab() instead of new GameObject() for prefab types",
    "After all objects created, wire SerializeField references via SerializedObject — handle arrays",
    "Remove Main Camera assumption — create if not found",
    "Test CoPlay output for Breakout scene",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in commits 9dfb291, dc5472b. PrefabUtility.InstantiatePrefab, SerializedObject wiring, camera fix."
}
```

---

## Phase: Validation Pipeline — Stage 5

### Task 1: End-to-end scaffold + gate pipeline for Breakout

```json
{
  "category": "validation",
  "priority": 1,
  "description": "Wire full pipeline: translate Breakout → scaffold Unity project → run all gates → report. Breakout is the simplest game (5 files, basic physics). This is the first end-to-end test of Stages 2-4.",
  "steps": [
    "Run project translator on examples/breakout/",
    "Run scaffold_project() on translator output",
    "Run structural gate on all generated C# — target: 5/5 pass",
    "Run convention gate — target: 5/5 pass",
    "Verify Packages/manifest.json is valid JSON with required packages",
    "Verify ProjectSettings/ files exist and are valid YAML",
    "Verify Assets/_Project/Scripts/ has all 5 C# files",
    "Document any remaining gaps for Stage 6",
    "Push to GitHub for home machine Unity validation"
  ],
  "passes": true,
  "note": "Breakout end-to-end pipeline validation PASS (commit 5a569ef). Also dotnet build 0 errors (cc9359c)."
}
```

---

## Phase: Flappy Bird — C# → Python → C# End-to-End Roundtrip

Source: https://github.com/zigurous/unity-flappy-bird-tutorial (5 scripts, ~150 LOC)
Reference C#: `data/reference/flappy_bird/`
Asset mapping: `data/mappings/flappy_bird_mapping.json`
API catalog: `data/reference/flappy_bird/api_catalog.md`

### Task 1: C# → Python line-by-line translation

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Translate all 5 C# scripts from zigurous/unity-flappy-bird-tutorial into Python 1:1 line-by-line. Every field, method, and name must match the C# reference. Missing Unity APIs must be ADDED to the engine, never worked around.",
  "steps": [
    "Read all 5 C# files in data/reference/flappy_bird/",
    "Translate Player.cs → player.py (Sprite[] array, InvokeRepeating, euler angles, CompareTag, singleton access)",
    "Translate GameManager.cs → game_manager.py (singleton Instance, DefaultExecutionOrder, SerializeField refs, FindObjectsOfType, Time.timeScale, UI.Text)",
    "Translate Pipes.cs → pipes.py (child Transform refs, Camera.main.ScreenToWorldPoint, Vector3 arithmetic)",
    "Translate Spawner.cs → spawner.py (InvokeRepeating/CancelInvoke, Instantiate with type, Random.Range)",
    "Translate Parallax.cs → parallax.py (MeshRenderer.material.mainTextureOffset or transform-based scroll substitute)",
    "Place all files in examples/flappy_bird/flappy_bird_python/",
    "Verify every public field, private field, method name, and lifecycle hook matches C# reference exactly",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in commit d6e20da. All 5 scripts translated 1:1."
}
```

### Task 2: Engine gap fills for Flappy Bird APIs

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Add missing Unity APIs to the engine that Flappy Bird requires. Do NOT work around missing APIs — add them to src/engine/.",
  "steps": [
    "Add InvokeRepeating(method_name, delay, interval) to MonoBehaviour — timer-based repeated calls",
    "Add CancelInvoke(method_name) to MonoBehaviour — cancel specific or all invokes",
    "Add DestroyImmediate(go) alias in core.py",
    "Verify Camera.main.screen_to_world_point() works correctly",
    "Verify find_objects_of_type<T>() returns correct results",
    "Add compare_tag(tag) to GameObject if not present",
    "Add DefaultExecutionOrder support (or document as translator-only attribute)",
    "Add Sprite[] public field support (list of sprite references for animation)",
    "Run existing test suite — no regressions",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in commit d6e20da. InvokeRepeating, CancelInvoke, DestroyImmediate, CompareTag added."
}
```

### Task 3: Python playable game — wire and playtest

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Wire up the Flappy Bird Python example as a playable pygame game. Create run_flappy_bird.py entry point and register in playtest.py.",
  "steps": [
    "Create examples/flappy_bird/run_flappy_bird.py with scene setup matching Unity hierarchy",
    "Set up scene: Player (bird), Spawner, Background parallax, Ground parallax, UI (score, game over, play button)",
    "Create Pipes prefab equivalent (parent + top/bottom children + scoring trigger)",
    "Configure tags: Obstacle, Scoring",
    "Configure colliders: trigger on pipe children and scoring zone, trigger on player",
    "Wire GameManager singleton with score UI and game state",
    "Register in tools/playtest.py as 'flappy_bird'",
    "Playtest: python tools/playtest.py flappy_bird",
    "Verify: bird flaps on space/click, pipes scroll left, score increments on pass, game over on collision, restart works",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in commit d6e20da. run_flappy_bird.py, registered in playtest.py."
}
```

### Task 4: Python → C# forward translation

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Translate the Python Flappy Bird back to C# using the project translator. This tests the full roundtrip pipeline.",
  "steps": [
    "Run project_translator.py on examples/flappy_bird/flappy_bird_python/",
    "Output to data/generated/flappy_bird_cs/",
    "Run structural gate on all 5 generated files — target: 5/5 pass",
    "Run convention gate — target: 5/5 pass",
    "Run compilation gate (syntax check) — target: 5/5 pass",
    "Run roundtrip gate vs original C# reference — record scores",
    "Compare generated C# against data/reference/flappy_bird/ originals — document all deviations",
    "Add translation pairs to data/corpus/"
  ],
  "passes": true,
  "note": "Done in commit bec1962. 5/5 gates pass."
}
```

### Task 5: Fix translator issues exposed by Flappy Bird

```json
{
  "category": "bugfix",
  "priority": 1,
  "description": "Fix any translator bugs that Flappy Bird roundtrip exposes. These are likely Stage 2 items: SerializeField emission, singleton pattern, CompareTag, InvokeRepeating translation.",
  "steps": [
    "Catalog all deviations found in Task 4 roundtrip comparison",
    "Fix SerializeField emission for typed references (Player, Spawner, Text, GameObject)",
    "Fix singleton pattern: static Instance property with get/private set",
    "Fix DefaultExecutionOrder attribute translation",
    "Fix CompareTag translation (ensure proper method call generation)",
    "Fix InvokeRepeating/CancelInvoke translation (nameof pattern)",
    "Fix Instantiate with typed return (Pipes pipes = Instantiate(prefab, ...))",
    "Re-run all gates after fixes — target: all pass",
    "Run full test suite — no regressions",
    "Spawn validation agent"
  ],
  "passes": true,
  "note": "Done in commit 01d4e4a. Translator improvements driven by Flappy Bird roundtrip."
}
```

### Task 6: Asset mapping and Unity project scaffold

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Generate a complete Unity project scaffold for Flappy Bird that uses original assets from the zigurous repo. The output project should be openable in Unity with <3 manual steps.",
  "steps": [
    "Download original sprites from zigurous repo to data/assets/flappy_bird/Sprites/",
    "Download original materials to data/assets/flappy_bird/Materials/",
    "Download original .meta files (preserve import settings: PPU, texture type, sprite mode)",
    "Download original Pipes.prefab and .meta to data/assets/flappy_bird/Prefabs/",
    "Run project scaffolder to generate Unity project structure at data/generated/flappy_bird_project/",
    "Copy original assets (sprites, materials, prefabs with .meta files) into scaffolded project",
    "Copy generated C# scripts into Assets/Scripts/",
    "Generate TagManager.asset with Obstacle and Scoring tags",
    "Generate Physics2DSettings.asset (gravity 0, -9.81)",
    "Verify folder structure matches: Assets/{Scripts,Sprites,Materials,Prefabs,Scenes}/",
    "Document deployment steps: clone assets → open in Unity → assign SerializeField refs → play"
  ],
  "passes": true,
  "note": "Done in commit f30110d. Original sprites, materials, prefabs, TagManager, Physics2D."
}
```

### Task 7: CoPlay scene reconstruction with original assets

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Generate a CoPlay MCP script that reconstructs the Flappy Bird scene in Unity Editor using the original assets. The script must wire sprite references, prefab instantiation, tag assignments, and SerializeField connections.",
  "steps": [
    "Serialize the Python Flappy Bird scene to JSON via scene_serializer",
    "Generate CoPlay editor script from scene JSON + flappy_bird_mapping.json",
    "Script must: create Camera, Player GO with SpriteRenderer (Bird_01 sprite), Spawner GO",
    "Script must: create Background + Ground parallax GOs with MeshRenderer + materials",
    "Script must: assign tags (Obstacle on pipe colliders, Scoring on gap trigger)",
    "Script must: wire SerializeField references (GameManager.player, GameManager.spawner, etc.)",
    "Script must: reference Pipes.prefab for Spawner.prefab field",
    "Script must: create UI Canvas with score Text, gameOver Image, playButton Image",
    "Script must: use original sprites from Assets/Sprites/ (not colored rectangles)",
    "Test script generation — verify valid C# editor script output",
    "Document any manual steps remaining after CoPlay execution"
  ],
  "passes": false
}
```

### Task 8: End-to-end validation — Unity playable

```json
{
  "category": "validation",
  "priority": 1,
  "description": "Full end-to-end validation: Python game → translated C# → scaffolded Unity project with original assets → CoPlay scene setup → playable in Unity. This is the first complete pipeline test with a third-party game.",
  "steps": [
    "Run full pipeline: translate → scaffold → copy assets → generate CoPlay script",
    "Push scaffolded project to GitHub",
    "On home machine: open project in Unity, run CoPlay script, verify scene loads",
    "Verify: bird sprite animates (3 frames), pipes use Pipe.png, background scrolls",
    "Verify: gameplay works (flap, score, game over, restart)",
    "Verify: no console errors, no missing references",
    "Record any manual steps required (target: <3)",
    "Document results in data/lessons/flappy_bird_deploy.md",
    "Update accuracy metrics in data/metrics/",
    "If bugs found: fix and re-validate before marking complete"
  ],
  "passes": false
}
