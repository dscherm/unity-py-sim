# Memories
<!-- Auto-populated by synthesize_memories.py. Max 15 entries, 2KB. -->
<!-- Stale entries (>10 iterations without reinforcement) are auto-evicted. -->
<!-- Compacted by compact_memories.py every 5 iterations. -->

## Translator docstring leak
<!-- type: pattern | last_seen: 6 | tags: translator, quality -->
Python triple-quoted docstrings emit as bare string literal statements in C#. The translator does not strip or convert them. Every translated file shows inflated line counts from docstrings. Tracked since Breakout (Task 6).

## Physics material double-bounce
<!-- type: pattern | last_seen: 5 | tags: physics, gotcha, unity -->
Assigning PhysicsMaterial2D(bounciness=1) AND manually reflecting velocity in OnCollisionEnter2D causes double-bounce. Let the material handle wall/brick bounces; only override for paddle angle control. Discovered in Breakout Unity port.

## Input System API gap
<!-- type: pattern | last_seen: 5 | tags: translator, input, unity -->
Python engine uses legacy Input.get_axis() / get_key_down(). Unity projects may use new Input System (InputActionAsset, ReadValue, WasPressedThisFrame). The Input System type is invisible to translation. First FSM port caused 999+ compile errors from this mismatch.

## Worktree isolation breaks validators
<!-- type: pattern | last_seen: 6 | tags: testing, worktree, ralph -->
Worktree isolation for validation agents consistently lands on stale commits (3/3 failures). Always run validators in main working directory. This is a top-level ban in CLAUDE.md.

## KINEMATIC to DYNAMIC loses mass in pymunk
<!-- type: pattern | last_seen: 5 | tags: physics, engine, bug -->
Switching Rigidbody2D.body_type from KINEMATIC to DYNAMIC zeroes pymunk mass/moment. Engine must save/restore mass across transition. Without fix, Space.step() crashes. Unity handles this automatically. Fixed in body_type setter.

## Translator compilation milestone
<!-- type: milestone | last_seen: 5 | tags: translator, compilation -->
Space Invaders (7 files) reached zero compile errors on 2026-04-05 after 11 rounds of fixes. Breakout followed same day. Key fixes: symbol table for scope, type inference from annotations, enum allowlist, UPPER_CASE constants, nullable tuples, truthiness handling.

## Ghost state machine pattern (Pacman)
<!-- type: pattern | last_seen: 6 | tags: pacman, design, fsm -->
Ghosts use 5 behavior MonoBehaviours (scatter, chase, frightened, home, eyes) aggregated by a ghost.py controller. Each behavior is enable(duration)/disable() with coroutine timers. State transitions: scatter<->chase on timer, frightened on power pellet, home on eaten, eyes returning to home. Node-based pathfinding at maze intersections.

## Auto-register components pattern
<!-- type: pattern | last_seen: 4 | tags: engine, redesign, simulator -->
Simulator redesign removed all manual LifecycleManager.register() and collider.build() calls from game code. Components auto-register on add_component() and colliders auto-build. This matches Unity behavior and produces cleaner translator output.

## Gate pipeline recursive timeout
<!-- type: pattern | last_seen: 6 | tags: gates, testing, infrastructure -->
Gate pipeline (tests + translate + structural + convention + playtest) can trigger recursive post-commit hooks causing timeouts. Fixed by guarding against re-entrant observation recording.

## Pellet reactivation bug
<!-- type: pattern | last_seen: 6 | tags: pacman, bug, gameobject -->
GameManager.new_round() must reactivate pellet GameObjects (set_active(True)), not just reset state. Inactive GameObjects skip lifecycle and trigger callbacks. Caught by independent validation agent (52 tests).
