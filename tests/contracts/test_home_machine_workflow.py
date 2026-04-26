"""Contract tests for `.github/workflows/home_machine.yml`.

Pins the structural shape we depend on so future edits don't silently
regress the deploy pipeline.

The headline rule (B-task `home-machine-yml-skip-step-exit-code`):
when the user dispatches the workflow with an explicit `games` list
that omits a matrix entry, that entry must be SKIPPED at the job
level — visible in the run UI as a gray/neutral dot — never RED.
The previous implementation used an inline `exit 78` step, but
GitHub Actions only honors that neutral-skip code on `uses:` steps,
not `run:` steps. Every dispatch with a non-target game therefore
showed the omitted row as a job failure, contaminating the green/red
signal we rely on for M-7 phase 2 deploys.

Fix: a job-level `if:` guard that uses space-padded `contains()` so
word-boundary matching prevents false positives on substring overlap
between game names.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "home_machine.yml"


@pytest.fixture(scope="module")
def workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def deploy_job(workflow) -> dict:
    return workflow["jobs"]["deploy"]


class TestJobLevelSkipGuard:
    def test_deploy_job_has_if_guard(self, deploy_job):
        assert "if" in deploy_job, (
            "deploy job must declare a job-level `if:` guard so non-target "
            "matrix entries skip cleanly (gray) instead of running and "
            "failing on the inline `exit 78` step."
        )

    def test_if_guard_handles_non_dispatch_events(self, deploy_job):
        guard = deploy_job["if"]
        assert "github.event_name != 'workflow_dispatch'" in guard, (
            "Push events have no `inputs.games`; the guard must short-"
            "circuit so the deploy still runs on master pushes."
        )

    def test_if_guard_handles_empty_games_input(self, deploy_job):
        guard = deploy_job["if"]
        assert "inputs.games == ''" in guard, (
            "Default dispatch (no `games` input) must run every matrix "
            "entry — the empty-string short-circuit guarantees that."
        )

    def test_if_guard_uses_word_boundary_contains(self, deploy_job):
        """Space-padded `contains()` prevents substring false positives.
        Without this, a future game named `flappy_bird_v2` requested via
        dispatch would also match `flappy_bird` and run an unintended
        matrix row.
        """
        guard = deploy_job["if"]
        # Both sides of `contains` must wrap the value in literal spaces
        # so word-boundary matching holds.  The exact format-call is the
        # canonical idiom for this in GitHub Actions expressions.
        assert "format(' {0} ', inputs.games)" in guard
        assert "format(' {0} ', matrix.game)" in guard


class TestNoInlineSkipStep:
    def test_no_skip_step_with_exit_78(self, deploy_job):
        """The inline `Skip if game not requested via dispatch` step
        used `exit 78` to signal a neutral skip — but GHA `run:` steps
        treat any non-zero exit as failure, painting the row red. The
        fix moves the gating to the job level; this contract makes
        sure nobody re-introduces an inline `exit 78` skip step.
        """
        for step in deploy_job["steps"]:
            run_block = step.get("run", "") or ""
            assert "exit 78" not in run_block, (
                f"Step {step.get('name')!r} contains `exit 78` in its run "
                f"block — that pattern is a known footgun on `run:` steps "
                f"(GHA only honors neutral-skip codes on `uses:`). Move "
                f"the skip condition to a job-level or step-level `if:`."
            )

    def test_no_step_named_skip_if_game_not_requested(self, deploy_job):
        """Catch a naïve regression where someone re-adds the previous
        step verbatim under the same name. The job-level `if:` is the
        only acceptable home for this gate.
        """
        names = [step.get("name", "") for step in deploy_job["steps"]]
        assert "Skip if game not requested via dispatch" not in names


class TestCriticalStepsStillPresent:
    """The cleanup must not have removed the deploy or test invocations."""

    def test_deploy_step_present(self, deploy_job):
        names = [step.get("name", "") for step in deploy_job["steps"]]
        assert "Deploy CoPlay scene (batchmode)" in names

    def test_playmode_test_step_present(self, deploy_job):
        names = [step.get("name", "") for step in deploy_job["steps"]]
        assert "Run PlayMode tests" in names
