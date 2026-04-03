# Testing Lessons

Hard-won lessons about testing the unity-py-sim engine.

---

## HIGH PRIORITY: Do NOT Use Worktree Isolation for Validation Agents

**Problem**: Worktree isolation (`isolation: "worktree"`) consistently creates worktrees from stale commits in this project. This has happened THREE times:

1. **First validator**: Worktree branched 15+ commits behind HEAD. Agent reported 9 new subsystems as "missing."
2. **Second validator**: Same stale branch issue. Agent had to manually `cp` files from the main repo into its worktree, burning time and defeating the purpose of isolation.
3. **Third validator**: Again stale. Agent spent its entire setup phase copying files instead of writing tests.

**Root cause**: The worktree feature branches from whatever commit it picks, which in this repo is consistently far behind HEAD. The "isolation" benefit is outweighed by the staleness cost.

**RULE: Never use `isolation: "worktree"` for validation agents in this project.** Instead, use these two safeguards together:
1. **Run the agent in the main working directory** (no isolation parameter) so it sees current code
2. **Instruct the agent to NOT read existing test files** (`tests/`) — only read source code in `src/` and `examples/`, and derive expectations from Unity documentation

This gives you both benefits: current code (no staleness) AND independent judgment (no test contamination).

## Unit Tests Are Not Validation

**Problem**: All 90 new tests for the engine expansion were unit tests — creating objects in isolation, checking property values, verifying return types. None ran the actual game loop, none compared behavior to Unity, none tested cross-system interactions.

**Prevention**:
- Every new subsystem needs at minimum:
  1. **Unit tests** — does the API work in isolation
  2. **Integration tests** — does it work through `app.run()` with other systems
  3. **Contract tests** — does it match Unity's documented behavior
  4. **Mutation tests** — do tests actually catch breakage (monkeypatch + assert failure)
- Run `python tools/playtest.py <example> --headless --frames 300` after ANY physics or rendering change
- The agent that writes code should NOT be the same agent that validates it

## Contract Test Design

**Problem**: A contract test asserted `elasticity=1.0` as the "correct" default. This was the OLD engine behavior, not Unity's actual default (bounciness=0). The test was testing "does the code do what it used to do" not "does the code match Unity."

**Prevention**:
- Contract tests must be derived from Unity documentation, not from reading the current source code
- Name contract tests with the Unity spec: `test_default_collider_elasticity_is_0` not `test_default_elasticity`
- When a contract test fails, check Unity docs before assuming the code is wrong — the test might be wrong
