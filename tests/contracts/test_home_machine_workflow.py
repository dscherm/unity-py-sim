"""Contract tests for `.github/workflows/home_machine.yml`.

Pins the structural shape we depend on so future edits don't silently
regress the deploy pipeline.

The headline rule (B-task `home-machine-yml-skip-step-exit-code`):
when the user dispatches the workflow with an explicit `games` list
that omits a matrix entry, that entry must be SKIPPED — never run
(and therefore never paint the row red on a non-zero exit). The
previous implementation used an inline `exit 78` step, but GitHub
Actions only honors that neutral-skip code on `uses:` steps, not
`run:` steps. Every dispatch with a non-target game therefore
showed the omitted row as a job failure, contaminating the
green/red signal we rely on for M-7 phase 2 deploys.

A first attempt used a job-level `if:` referencing `matrix.game`.
That fails workflow validation: GHA evaluates job-level `if:`
BEFORE matrix expansion, so the `matrix` context is unresolved
there. The current shape uses a `setup` prep job that computes
the matrix as a JSON array from `inputs.games`, and the `deploy`
job consumes it via `fromJSON(needs.setup.outputs.games)`. Non-
target games simply don't appear in the matrix — which is the
cleanest possible "skip" (no row at all, vs. a gray placeholder).
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


@pytest.fixture(scope="module")
def setup_job(workflow) -> dict:
    return workflow["jobs"]["setup"]


class TestDynamicMatrix:
    """The matrix is computed in a `setup` prep job and consumed by
    `deploy` via `fromJSON(needs.setup.outputs.games)`. This is the
    only shape that lets a `workflow_dispatch` `games` input drop
    matrix entries entirely (no row, no red, no neutral-skip code).
    """

    def test_setup_job_exists(self, workflow):
        assert "setup" in workflow["jobs"], (
            "Workflow must declare a `setup` prep job that computes the "
            "deploy matrix from inputs.games — required because GHA "
            "rejects `matrix.X` references in job-level `if:` guards."
        )

    def test_setup_job_runs_on_managed_runner(self, setup_job):
        # The prep job is intentionally NOT on self-hosted: it would
        # block on the same runner the deploy needs, and the prep work
        # (~10s of bash + jq) doesn't need Unity / Windows.
        runs_on = setup_job["runs-on"]
        assert runs_on == "ubuntu-latest", (
            f"setup job should run on ubuntu-latest, got {runs_on!r}"
        )

    def test_setup_job_exposes_games_output(self, setup_job):
        outputs = setup_job.get("outputs") or {}
        assert "games" in outputs, (
            "setup job must expose a `games` output (JSON array string) "
            "so the deploy matrix can fromJSON-parse it."
        )

    def test_deploy_needs_setup(self, deploy_job):
        needs = deploy_job.get("needs")
        # `needs:` may be a string or a list — accept either.
        if isinstance(needs, str):
            needs = [needs]
        assert needs and "setup" in needs, (
            "deploy job must declare `needs: setup` so the dynamic "
            "matrix is resolved before the matrix expands."
        )

    def test_deploy_matrix_uses_setup_output(self, deploy_job):
        matrix = deploy_job["strategy"]["matrix"]
        game = matrix["game"]
        assert isinstance(game, str), (
            "deploy.strategy.matrix.game must be a single string "
            "expression (the fromJSON of needs.setup.outputs.games), "
            f"got {type(game).__name__}: {game!r}"
        )
        assert "fromJSON" in game and "needs.setup.outputs.games" in game, (
            f"deploy.strategy.matrix.game must consume the setup output "
            f"via fromJSON; got: {game!r}"
        )

    def test_deploy_has_no_matrix_aware_job_if(self, deploy_job):
        """Job-level `if:` referencing `matrix.X` fails GHA validation
        (`Unrecognized named-value: 'matrix'`). Future edits must keep
        the matrix filtering in the prep-job, not on the deploy job.
        """
        guard = deploy_job.get("if", "") or ""
        assert "matrix." not in guard, (
            f"deploy job-level `if:` must not reference `matrix.X` — "
            f"GHA rejects it before matrix expansion. Move the filter "
            f"to the setup job's matrix computation. Got: {guard!r}"
        )


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
