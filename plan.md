# plan.md — unity-py-sim

Task queue for Ralph Loop. JSON blocks in triple-backtick fences.
Only ONE task per iteration. Mark `"passes": true` when complete.

---

## Phase 1: Simulator Foundation

### Task 1: Math classes — Vector2, Vector3, Quaternion, Mathf

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Implement Vector2, Vector3, Quaternion math classes backed by numpy/pyrr and Mathf static methods",
  "steps": [
    "Implement src/engine/math/vector.py — Vector2 and Vector3 classes wrapping numpy arrays",
    "Support arithmetic operators (+,-,*,/), dot(), cross(), magnitude, normalized, distance()",
    "Add static constructors: Vector3.zero, Vector3.one, Vector3.up, Vector3.forward, etc.",
    "Implement src/engine/math/quaternion.py — Quaternion wrapping pyrr",
    "Support euler_angles property, angle_axis(), identity, slerp()",
    "Implement src/engine/math/mathf.py — Mathf.lerp, clamp, approximately, deg2rad, rad2deg",
    "Write tests/engine/test_math.py — at least 20 tests covering all operations",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 2: Core classes — Component, MonoBehaviour, GameObject

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Implement core Component, MonoBehaviour, and GameObject classes with global registry",
  "steps": [
    "Implement src/engine/core.py — Component base class with game_object back-reference",
    "Implement MonoBehaviour(Component) with lifecycle method stubs (awake, start, update, fixed_update, late_update, on_destroy)",
    "Implement GameObject with name, tag, layer, transform, components list",
    "Implement add_component(cls), get_component(cls), get_components_in_children(cls)",
    "Implement static methods: GameObject.find(name), GameObject.find_with_tag(tag), GameObject.destroy(obj)",
    "Use a module-level registry dict for find/find_with_tag",
    "Write tests/engine/test_core.py — at least 15 tests covering creation, components, find, destroy",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 3: Transform component with parent-child hierarchy

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Implement Transform component with position, rotation, scale, and parent-child hierarchy",
  "steps": [
    "Implement src/engine/transform.py — Transform(Component)",
    "Properties: position, rotation, local_scale, parent, children, forward, right, up",
    "Methods: translate(), rotate(), look_at(), set_parent()",
    "Local-to-world and world-to-local coordinate conversion",
    "Auto-create Transform when GameObject is instantiated",
    "Write tests/engine/test_transform.py — hierarchy tests, coordinate conversion, rotation",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 4: Time and Input managers

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Implement Time and Input static manager classes",
  "steps": [
    "Implement src/engine/time_manager.py — Time static class with delta_time, fixed_delta_time, time, frame_count, time_scale",
    "Implement src/engine/input_manager.py — Input static class",
    "Input methods: get_key, get_key_down, get_key_up, get_axis, get_mouse_position, get_mouse_button",
    "Axis mapping for Horizontal (A/D, Left/Right) and Vertical (W/S, Up/Down)",
    "Key state tracking with current/previous frame for transition detection",
    "Write tests/engine/test_time.py and tests/engine/test_input.py",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 5: LifecycleManager — frame loop orchestrator

```json
{
  "category": "feature",
  "priority": 1,
  "description": "Implement LifecycleManager singleton managing the full Unity lifecycle",
  "steps": [
    "Implement src/engine/lifecycle.py — LifecycleManager singleton",
    "Awake queue, start queue, update list, fixed_update list, late_update list, destroy queue",
    "register_component() and unregister_component() methods",
    "process_awake_queue(), process_start_queue(), run_fixed_update(), run_update(), run_late_update(), process_destroy_queue()",
    "Respect Component.enabled flag — skip disabled components",
    "Write tests/engine/test_lifecycle.py — test ordering, enable/disable, destroy during update",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 6: Physics layer — Rigidbody2D, colliders, PhysicsManager

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Implement pymunk-backed 2D physics with collision dispatch to MonoBehaviour callbacks",
  "steps": [
    "Implement src/engine/physics/physics_manager.py — wraps pymunk.Space, manages bodies/shapes",
    "Implement src/engine/physics/rigidbody.py — Rigidbody2D(Component) wrapping pymunk.Body",
    "Properties: velocity, angular_velocity, mass, drag, gravity_scale, body_type enum",
    "Methods: add_force(), add_torque(), move_position() for kinematic",
    "Implement src/engine/physics/collider.py — BoxCollider2D, CircleCollider2D wrapping pymunk.Shape",
    "Wire pymunk collision handlers to dispatch on_collision_enter_2d, on_trigger_enter_2d, etc.",
    "Create Collision2D data class with game_object, contacts, relative_velocity",
    "Sync pymunk body positions back to Transform each physics step",
    "Write tests/engine/test_physics.py — gravity, collision detection, trigger callbacks",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 7: Rendering layer — pygame display, Camera, SpriteRenderer

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Implement pygame rendering with Camera world-to-screen conversion and sorted SpriteRenderer",
  "steps": [
    "Implement src/engine/rendering/display.py — DisplayManager (pygame init, surface, event pump)",
    "Implement src/engine/rendering/camera.py — Camera(Component) with orthographic_size, background_color",
    "World-to-screen and screen-to-world coordinate conversion",
    "Implement src/engine/rendering/renderer.py — SpriteRenderer(Component) with color, sprite, sorting_order",
    "RenderManager — collects all SpriteRenderers, sorts by sorting_order, renders through Camera",
    "Support basic shapes (rect, circle) as fallback when no sprite assigned",
    "Write tests/engine/test_rendering.py — coordinate conversion, sorting order",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 8: Scene manager and main app loop

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Implement SceneManager and the main game loop entry point (app.py)",
  "steps": [
    "Implement src/engine/scene.py — SceneManager singleton with global GameObject registry",
    "Implement src/engine/app.py — run() function with the full frame loop",
    "Frame loop: Input poll -> awake -> start -> fixed update accumulator -> physics step -> update -> late update -> render -> destroy",
    "Integrate Time, Input, LifecycleManager, PhysicsManager, DisplayManager",
    "Write a minimal smoke test that creates GameObjects and runs 10 frames headlessly",
    "Verify all tests pass"
  ],
  "passes": false
}
```

---

## Phase 2: Reference Mapping + Pong

### Task 9: Reference mapping data and query layer

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Create the reference mapping JSON files and Python query layer for all implemented engine classes",
  "steps": [
    "Create src/reference/mappings/classes.json — mappings for MonoBehaviour, GameObject, Transform, Rigidbody2D, colliders, Camera, SpriteRenderer",
    "Create src/reference/mappings/methods.json — all implemented methods with signatures",
    "Create src/reference/mappings/properties.json — all implemented properties",
    "Create src/reference/mappings/lifecycle.json — full lifecycle method mapping table",
    "Create src/reference/mappings/enums.json — Space, ForceMode2D, RigidbodyType2D, KeyCode",
    "Create src/reference/mappings/patterns.json — at least 5 common patterns (GetComponent, Instantiate, Destroy, Input axis, coroutine)",
    "Create src/reference/mappings/notes.json — at least 5 behavioral difference notes",
    "Implement src/reference/mapping.py — load and query the mappings",
    "Write tests/reference/test_mapping.py and test_mapping_completeness.py",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 10: Pong in Unity C# (controlled reference)

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Write a simple Pong game in Unity C# as the controlled reference for roundtrip testing",
  "steps": [
    "Create examples/pong/pong_unity/PaddleController.cs — MonoBehaviour, Input.GetAxis, Rigidbody2D.velocity",
    "Create examples/pong/pong_unity/BallController.cs — MonoBehaviour, Start() launches ball, OnCollisionEnter2D reflects",
    "Create examples/pong/pong_unity/ScoreManager.cs — static score tracking",
    "Create examples/pong/pong_unity/GameManager.cs — game state, reset, serve",
    "Keep each file under 80 lines — intentionally simple",
    "Document which Unity APIs each file uses in comments"
  ],
  "passes": false
}
```

### Task 11: Pong in Python using the simulator

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Write the Python equivalent of Pong using the simulator and verify it runs",
  "steps": [
    "Create examples/pong/pong_python/paddle_controller.py — MonoBehaviour subclass using simulator API",
    "Create examples/pong/pong_python/ball_controller.py — same logic as C# version",
    "Create examples/pong/pong_python/score_manager.py — same logic",
    "Create examples/pong/pong_python/game_manager.py — same logic",
    "Create examples/pong/run_pong.py — sets up scene and runs game loop",
    "Verify the Python version runs: python examples/pong/run_pong.py",
    "Add the C#/Python file pairs to data/corpus/pairs/"
  ],
  "passes": false
}
```

---

## Phase 3: C# -> Python Translator

### Task 12: C# parser using tree-sitter

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Implement C# parser using tree-sitter that produces IR dataclasses",
  "steps": [
    "Define IR dataclasses in src/translator/csharp_parser.py: CSharpClass, CSharpField, CSharpProperty, CSharpMethod, CSharpParameter",
    "Parse class declarations, inheritance, attributes",
    "Parse method bodies into structured blocks",
    "Parse field declarations with types, modifiers, initializers",
    "Write tests/translator/test_csharp_parser.py — parse each Pong C# file, verify IR structure",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 13: Type mapper and translation rules

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Implement bidirectional type mapper and JSON-driven translation rules",
  "steps": [
    "Create src/translator/rules/type_mappings.json with full C# to Python type table",
    "Create src/translator/rules/translation_rules.json with naming conventions and lifecycle mappings",
    "Implement src/translator/type_mapper.py — load rules, map types bidirectionally",
    "Handle generic types: List<T> to list[T], Dictionary<K,V> to dict[K,V]",
    "Handle nullable types: int? to int | None",
    "Write tests for type_mapper covering all type categories",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 14: C# to Python translator core

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Implement the core C# to Python translator targeting the simulator API",
  "steps": [
    "Implement src/translator/csharp_to_python.py — main translate_file() function",
    "Convert CSharpClass IR to Python source code",
    "Handle class inheritance, field declarations, method signatures",
    "Handle method body translation (expressions, assignments, if/else, for/foreach, while)",
    "Use reference mapping to translate Unity API calls",
    "Apply naming convention rules (PascalCase to snake_case)",
    "Emit proper imports at top of generated file",
    "Write tests/translator/test_csharp_to_python.py — translate each Pong C# file, verify output",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 15: Pattern handlers

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Implement pattern handlers for coroutines, serialized fields, events, generics, LINQ, properties",
  "steps": [
    "Implement src/translator/pattern_handlers/coroutine.py — IEnumerator/yield to async/await",
    "Implement src/translator/pattern_handlers/serialized_field.py — SerializeField to class vars",
    "Implement src/translator/pattern_handlers/event_delegate.py — events/delegates to callbacks",
    "Implement src/translator/pattern_handlers/generics.py — C# generics to Python type hints",
    "Implement src/translator/pattern_handlers/properties.py — C# get/set to @property",
    "Implement src/translator/pattern_handlers/linq.py — LINQ to list comprehensions",
    "Write tests/translator/test_pattern_handlers.py — at least 3 tests per handler",
    "Verify all tests pass"
  ],
  "passes": false
}
```

---

## Phase 4: Python -> C# Reverse Translator

### Task 16: Python parser for simulator-aware IR

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Implement Python parser that extracts simulator-aware IR using stdlib ast",
  "steps": [
    "Implement src/translator/python_parser.py using stdlib ast module",
    "Extract class hierarchy, detect MonoBehaviour subclasses",
    "Extract fields with type annotations",
    "Extract methods, identify lifecycle methods by name",
    "Identify simulator API calls: get_component, find, instantiate, destroy",
    "Write tests/translator/test_python_parser.py — parse each Pong Python file",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 17: Python to C# translator with Jinja2 templates

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Implement Python to C# reverse translator producing idiomatic Unity code",
  "steps": [
    "Create src/translator/templates/monobehaviour.cs.j2 — C# MonoBehaviour template",
    "Implement src/translator/python_to_csharp.py — main translate_file() function",
    "Reverse all naming conventions (snake_case to PascalCase/camelCase)",
    "Map simulator API back to Unity API using reference mappings",
    "Handle using directives — infer from types used",
    "Handle float literal suffixes (5.0 to 5f)",
    "Implement reverse pattern handlers (async to coroutine, etc.)",
    "Write tests/translator/test_python_to_csharp.py — translate each Pong Python file, verify output",
    "Verify all tests pass"
  ],
  "passes": false
}
```

---

## Phase 5: Roundtrip Validation + More Games

### Task 18: Roundtrip test framework

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Implement roundtrip test framework — C# to Python to C# equivalence scoring",
  "steps": [
    "Implement tests/translator/test_roundtrip.py",
    "For each Pong C# file: parse, translate to Python, translate back to C#, compare ASTs",
    "Define equivalence scoring: structural match, type match, naming match, body match",
    "Implement src/gates/roundtrip_gate.py — runs roundtrip on all corpus pairs",
    "Implement src/gates/accuracy_tracker.py — records scores to data/metrics/",
    "Verify all tests pass, document accuracy scores in activity.md"
  ],
  "passes": false
}
```

### Task 19: Convention and structural gates

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Implement convention gate and structural gate for generated C# validation",
  "steps": [
    "Implement src/gates/structural_gate.py — tree-sitter parse validation of generated C#",
    "Implement src/gates/convention_gate.py — Unity convention checks",
    "Checks: MonoBehaviour inheritance, lifecycle method signatures, SerializeField usage, using directives",
    "Check: no new MonoBehaviour() — must use AddComponent",
    "Write tests for both gates",
    "Verify all tests pass"
  ],
  "passes": false
}
```

### Task 20: Breakout as second test game

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Write Breakout as second test game and expand the translation corpus",
  "steps": [
    "Create examples/breakout/breakout_unity/ — C# version (BrickController, PaddleController, BallController, LevelManager)",
    "Create examples/breakout/breakout_python/ — Python version using simulator",
    "Run roundtrip translation on Breakout files",
    "Add pairs to data/corpus/",
    "Document new patterns in data/lessons/patterns.md",
    "Document gotchas in data/lessons/gotchas.md",
    "Update translation accuracy metrics"
  ],
  "passes": false
}
```

### Task 21: First open-source Unity project from GitHub

```json
{
  "category": "feature",
  "priority": 3,
  "description": "Test translator with a real open-source Unity 2D game from GitHub",
  "steps": [
    "Choose a simple open-source Unity 2D game from GitHub (< 10 scripts)",
    "Run C# to Python translator on all MonoBehaviour scripts",
    "Document which files translated cleanly vs. needed manual fixes",
    "Run translated Python in simulator, note failures",
    "Add successful pairs to corpus",
    "Record lessons learned in data/lessons/",
    "Promote universal lessons to ~/ralph-universal/lessons/ via proposal"
  ],
  "passes": false
}
```

---

## Phase 6: Ralph Loop Wiring

### Task 22: Wire custom gates into Ralph loop

```json
{
  "category": "feature",
  "priority": 2,
  "description": "Wire custom translation gates into Ralph loop for autonomous improvement",
  "steps": [
    "Extend ralph.config.json with custom gate commands if needed",
    "Add to PROMPT.md: instructions for running roundtrip gate after translator changes",
    "Configure data/corpus/corpus_index.json as a tracked accuracy ledger",
    "Create a Ralph task template for translate-new-Unity-project workflow",
    "Test full Ralph loop: 5 iterations on a translator improvement task",
    "Verify gates fire correctly, metrics are recorded"
  ],
  "passes": false
}
```
