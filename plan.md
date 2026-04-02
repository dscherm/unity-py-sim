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
