# Testing Lessons

Hard-won lessons about testing the unity-py-sim engine.

---

## Worktree / Agent Isolation Staleness

**Problem**: When spawning agents in isolated worktrees (e.g. for independent test validation), the worktree may be created from a stale branch or commit that doesn't include recent work. The agent then writes tests against old code and reports features as "missing" when they actually exist.

**How it happened**: An independent test validation agent was launched in a worktree. The worktree branched from a commit 15+ commits behind HEAD. The agent reported that coroutines, PhysicsMaterial2D, Stay callbacks, Debug, Audio, UI, and Scene loading "do not exist" — but they had all been implemented on the main branch.

**Prevention**:
- Before launching an agent in a worktree, ensure the worktree is based on the latest commit (`git log --oneline -1` in the worktree should match the main branch)
- If an agent reports features as missing that you know exist, check the worktree's commit hash first
- For validation agents that need to test NEW code, prefer running them in the main working directory rather than an isolated worktree, or explicitly verify the worktree is up-to-date

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
