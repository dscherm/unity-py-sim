"""
Contract tests for the GitHub Actions CI workflow at .github/workflows/test.yml.

Assertions are derived from the M-6 task spec — not from reading the YAML implementation.
These tests specify what the workflow MUST contain, not what it happens to contain.
"""

import os
import pytest
import yaml

WORKFLOW_PATH = os.path.join(
    os.path.dirname(__file__),  # tests/integration/
    "..", "..",                 # project root
    ".github", "workflows", "test.yml"
)
WORKFLOW_PATH = os.path.normpath(WORKFLOW_PATH)


@pytest.fixture(scope="module")
def workflow():
    """Load and parse the workflow YAML once for all tests."""
    assert os.path.isfile(WORKFLOW_PATH), (
        f"Workflow file not found at {WORKFLOW_PATH}"
    )
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data is not None, "Workflow YAML parsed to None (empty file?)"
    return data


# ---------------------------------------------------------------------------
# 1. File exists and is valid YAML
# ---------------------------------------------------------------------------

def test_workflow_file_exists_and_parses(workflow):
    """Workflow file exists at .github/workflows/test.yml and parses as valid YAML."""
    assert isinstance(workflow, dict), "Top-level YAML must be a mapping"


# ---------------------------------------------------------------------------
# 2. Triggers
# ---------------------------------------------------------------------------

def test_workflow_triggers_on_push_and_pr(workflow):
    """Workflow triggers on push to master/main and on pull_request to master/main."""
    on = workflow.get("on", workflow.get(True))  # 'on' can parse as True in PyYAML
    assert on is not None, "Workflow must have an 'on:' trigger block"

    push = on.get("push", {}) or {}
    pr = on.get("pull_request", {}) or {}

    push_branches = push.get("branches", []) or []
    pr_branches = pr.get("branches", []) or []

    valid_main_branches = {"master", "main"}

    assert any(b in valid_main_branches for b in push_branches), (
        f"push.branches must include 'master' or 'main', got: {push_branches}"
    )
    assert any(b in valid_main_branches for b in pr_branches), (
        f"pull_request.branches must include 'master' or 'main', got: {pr_branches}"
    )


# ---------------------------------------------------------------------------
# 3. pytest job
# ---------------------------------------------------------------------------

def test_pytest_job_exists(workflow):
    """Workflow has a 'pytest' job."""
    jobs = workflow.get("jobs", {})
    assert "pytest" in jobs, f"Expected 'pytest' job, found jobs: {list(jobs.keys())}"


def test_pytest_job_runs_on_ubuntu_latest(workflow):
    """pytest job runs on ubuntu-latest."""
    job = workflow["jobs"]["pytest"]
    assert job.get("runs-on") == "ubuntu-latest", (
        f"pytest job must run on ubuntu-latest, got: {job.get('runs-on')}"
    )


def test_pytest_job_uses_checkout_and_setup_python(workflow):
    """pytest job uses actions/checkout@v4 and actions/setup-python@v5."""
    steps = workflow["jobs"]["pytest"].get("steps", [])
    uses_values = [s.get("uses", "") for s in steps if s]

    assert any(u.startswith("actions/checkout@v4") for u in uses_values), (
        f"pytest job must use actions/checkout@v4, found: {uses_values}"
    )
    assert any(u.startswith("actions/setup-python@v5") for u in uses_values), (
        f"pytest job must use actions/setup-python@v5, found: {uses_values}"
    )


def test_pytest_job_installs_requirements(workflow):
    """pytest job installs dependencies from requirements.txt."""
    steps = workflow["jobs"]["pytest"].get("steps", [])
    run_commands = " ".join(s.get("run", "") for s in steps if s)
    assert "requirements.txt" in run_commands, (
        "pytest job must install from requirements.txt"
    )


def test_pytest_job_runs_pytest(workflow):
    """pytest job runs python -m pytest tests/."""
    steps = workflow["jobs"]["pytest"].get("steps", [])
    run_commands = " ".join(s.get("run", "") for s in steps if s)
    assert "pytest" in run_commands and "tests/" in run_commands, (
        "pytest job must run pytest against tests/"
    )


def test_pytest_job_sets_sdl_videodriver_dummy(workflow):
    """pytest job sets SDL_VIDEODRIVER: dummy for headless pygame."""
    steps = workflow["jobs"]["pytest"].get("steps", [])
    # SDL_VIDEODRIVER can be in step-level env or job-level env
    job = workflow["jobs"]["pytest"]
    job_env = job.get("env", {}) or {}

    # Collect all env blocks from every step
    all_envs = [job_env]
    for step in steps:
        if step and step.get("env"):
            all_envs.append(step["env"])

    found = any(
        env.get("SDL_VIDEODRIVER") == "dummy"
        for env in all_envs
    )
    assert found, (
        "pytest job must set SDL_VIDEODRIVER=dummy (headless pygame). "
        f"Searched job env and all step envs."
    )


# ---------------------------------------------------------------------------
# 4. ruff job
# ---------------------------------------------------------------------------

def test_ruff_job_runs_ruff_check(workflow):
    """Workflow has a 'ruff' job that runs ruff check on src/, tests/, tools/."""
    jobs = workflow.get("jobs", {})
    assert "ruff" in jobs, f"Expected 'ruff' job, found jobs: {list(jobs.keys())}"

    steps = jobs["ruff"].get("steps", [])
    run_commands = " ".join(s.get("run", "") for s in steps if s)

    assert "ruff check" in run_commands, (
        f"ruff job must run 'ruff check', got run commands: {run_commands!r}"
    )

    for target in ("src/", "tests/", "tools/"):
        assert target in run_commands, (
            f"ruff job must check '{target}', missing from run commands: {run_commands!r}"
        )


# ---------------------------------------------------------------------------
# 5. gates job
# ---------------------------------------------------------------------------

def test_gates_job_runs_gate_pipeline(workflow):
    """Workflow has a 'gates' job that runs python -m tools.gate_pipeline --quick."""
    jobs = workflow.get("jobs", {})
    assert "gates" in jobs, f"Expected 'gates' job, found jobs: {list(jobs.keys())}"

    steps = jobs["gates"].get("steps", [])
    run_commands = " ".join(s.get("run", "") for s in steps if s)

    assert "tools.gate_pipeline" in run_commands, (
        f"gates job must run tools.gate_pipeline, got: {run_commands!r}"
    )
    assert "--quick" in run_commands, (
        f"gates job must pass --quick flag, got: {run_commands!r}"
    )


# ---------------------------------------------------------------------------
# 6. Concurrency with cancel-in-progress
# ---------------------------------------------------------------------------

def test_concurrency_cancel_in_progress(workflow):
    """Workflow sets concurrency with cancel-in-progress: true."""
    concurrency = workflow.get("concurrency")
    assert concurrency is not None, (
        "Workflow must define a 'concurrency:' block to cancel superseded pushes"
    )
    assert concurrency.get("cancel-in-progress") is True, (
        f"concurrency.cancel-in-progress must be true, got: {concurrency}"
    )


# ---------------------------------------------------------------------------
# 7. pip cache via setup-python
# ---------------------------------------------------------------------------

def test_pytest_job_caches_pip(workflow):
    """pytest job caches pip via cache: pip on the setup-python action."""
    steps = workflow["jobs"]["pytest"].get("steps", [])

    setup_python_steps = [
        s for s in steps
        if s and s.get("uses", "").startswith("actions/setup-python")
    ]
    assert setup_python_steps, "No setup-python step found in pytest job"

    found_cache = any(
        (s.get("with") or {}).get("cache") == "pip"
        for s in setup_python_steps
    )
    assert found_cache, (
        "actions/setup-python step must include 'with: cache: pip' for pip caching. "
        f"setup-python steps found: {setup_python_steps}"
    )
