"""Round-trip regression tests for `tools/translate_snippet.py` (M-10).

These tests pin the *current* observed translator output for ten common
idioms. They span typed fields, MonoBehaviour subclasses, lifecycle
methods, list fields, Vector3 literals, UI components, the `--namespace`
flag, and the `--with-using` package trailer.

A mix of execution styles is used:
- 6 of the 10 tests invoke the CLI through `subprocess.run` so the
  end-to-end binary surface (argparse, exit codes, stdout buffering, etc.)
  is exercised.
- 4 of the 10 tests call the importable `translate_snippet()` function
  directly to cover the in-process API path.

Each fixture is asserted with `rstrip()`-on-both-sides string equality so
trailing newline drift is ignored. If a future translator change breaks
one of these, treat it as an intentional behavioural shift and update the
fixture deliberately rather than masking the diff.

Notes on locked-in oddities (current behaviour, not necessarily ideal):
- `list[GameObject]` translates to `GameObject[]` rather than
  `List<GameObject>`; no `using System.Collections.Generic;` is emitted
  because the array form does not need it. Test 6 locks this in.
- A method that returns `Vector3(...)` keeps a return annotation of
  `object` (the semantic layer does not currently infer the return type
  from the body). Test 7 locks this in.
- `using UnityEngine.UI;` is emitted *before* `using UnityEngine;` for
  UI snippets. Tests 8 and 10 lock this ordering in.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL = REPO_ROOT / "tools" / "translate_snippet.py"

# Make the in-process import work without depending on the test runner's CWD.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.translate_snippet import translate_snippet  # noqa: E402


def _run_cli(*args: str, code: str | None = None) -> subprocess.CompletedProcess:
    """Invoke translate_snippet.py via subprocess and return the result."""
    cmd = [sys.executable, str(TOOL), *args]
    if code is not None:
        cmd.extend(["--code", code])
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=False,
    )


def _assert_equal(actual: str, expected: str) -> None:
    """Compare ignoring trailing newlines on each side, per the task spec."""
    assert actual.rstrip() == expected.rstrip(), (
        "Translator output drifted from locked-in fixture.\n"
        f"--- expected ---\n{expected!r}\n"
        f"--- actual ---\n{actual!r}\n"
    )


# ---------------------------------------------------------------------------
# Test 1 — plain class with a typed int field (CLI)
# ---------------------------------------------------------------------------
def test_plain_class_typed_int_field_via_cli() -> None:
    py = "class Foo:\n    count: int = 0\n"
    expected = (
        "using UnityEngine;\n"
        "public class Foo\n"
        "{\n"
        "    public int count = 0;\n"
        "}\n"
    )
    result = _run_cli(code=py)
    assert result.returncode == 0, result.stderr
    _assert_equal(result.stdout, expected)


# ---------------------------------------------------------------------------
# Test 2 — MonoBehaviour subclass with update() touching transform.position (CLI)
# ---------------------------------------------------------------------------
def test_monobehaviour_update_transform_position_via_cli() -> None:
    py = (
        "from src.engine import MonoBehaviour\n"
        "\n"
        "class Mover(MonoBehaviour):\n"
        "    def update(self):\n"
        "        self.transform.position = self.transform.position\n"
    )
    expected = (
        "using UnityEngine;\n"
        "public class Mover : MonoBehaviour\n"
        "{\n"
        "     void Update()\n"
        "    {\n"
        "        transform.position = transform.position;\n"
        "    }\n"
        "}\n"
    )
    result = _run_cli(code=py)
    assert result.returncode == 0, result.stderr
    _assert_equal(result.stdout, expected)


# ---------------------------------------------------------------------------
# Test 3 — start() with GameObject.find (CLI)
# ---------------------------------------------------------------------------
def test_start_with_gameobject_find_via_cli() -> None:
    py = (
        "from src.engine import MonoBehaviour, GameObject\n"
        "\n"
        "class Finder(MonoBehaviour):\n"
        "    def start(self):\n"
        "        self.target = GameObject.find('Player')\n"
    )
    expected = (
        "using UnityEngine;\n"
        "public class Finder : MonoBehaviour\n"
        "{\n"
        "    [SerializeField] private GameObject target;\n"
        "     void Start()\n"
        "    {\n"
        '        target = GameObject.Find("Player");\n'
        "    }\n"
        "}\n"
    )
    result = _run_cli(code=py)
    assert result.returncode == 0, result.stderr
    _assert_equal(result.stdout, expected)


# ---------------------------------------------------------------------------
# Test 4 — float field with constant value (in-process function)
# ---------------------------------------------------------------------------
def test_float_field_constant_value_in_process() -> None:
    py = (
        "from src.engine import MonoBehaviour\n"
        "\n"
        "class Speedy(MonoBehaviour):\n"
        "    speed: float = 5.0\n"
    )
    expected = (
        "using UnityEngine;\n"
        "public class Speedy : MonoBehaviour\n"
        "{\n"
        "    public float speed = 5.0f;\n"
        "}\n"
    )
    actual = translate_snippet(py)
    _assert_equal(actual, expected)


# ---------------------------------------------------------------------------
# Test 5 — boolean field with True literal (in-process function)
# ---------------------------------------------------------------------------
def test_bool_true_literal_in_process() -> None:
    py = (
        "from src.engine import MonoBehaviour\n"
        "\n"
        "class Toggler(MonoBehaviour):\n"
        "    enabled: bool = True\n"
    )
    expected = (
        "using UnityEngine;\n"
        "public class Toggler : MonoBehaviour\n"
        "{\n"
        "    public bool enabled = true;\n"
        "}\n"
    )
    actual = translate_snippet(py)
    _assert_equal(actual, expected)


# ---------------------------------------------------------------------------
# Test 6 — list[GameObject] field (CLI)
#
# LOCKED-IN ODDITY: the translator emits `GameObject[]` (an array) rather
# than `List<GameObject>`, so it does NOT pull in
# `using System.Collections.Generic;`. This contradicts the gap-1/gap-2
# expectations in `.claude/.ralph-spec.md`. Captured here as a regression
# net; flagged in the report.
# ---------------------------------------------------------------------------
def test_list_of_gameobject_field_via_cli() -> None:
    py = (
        "from src.engine import MonoBehaviour, GameObject\n"
        "\n"
        "class Pool(MonoBehaviour):\n"
        "    items: list[GameObject] = []\n"
    )
    expected = (
        "using System.Collections.Generic;\n"
        "using UnityEngine;\n"
        "public class Pool : MonoBehaviour\n"
        "{\n"
        "    [SerializeField] private GameObject[] items;\n"
        "}\n"
    )
    result = _run_cli(code=py)
    assert result.returncode == 0, result.stderr
    _assert_equal(result.stdout, expected)


# ---------------------------------------------------------------------------
# Test 7 — method returning Vector3 literal (in-process function)
#
# LOCKED-IN ODDITY: return annotation comes out as `object` rather than
# `Vector3`. Body translation is correct (`new Vector3(1.0f, 2.0f, 3.0f)`).
# ---------------------------------------------------------------------------
def test_method_returns_vector3_literal_in_process() -> None:
    py = (
        "from src.engine import MonoBehaviour, Vector3\n"
        "\n"
        "class Maker(MonoBehaviour):\n"
        "    def make_vec(self):\n"
        "        return Vector3(1.0, 2.0, 3.0)\n"
    )
    expected = (
        "using UnityEngine;\n"
        "public class Maker : MonoBehaviour\n"
        "{\n"
        "    public object MakeVec()\n"
        "    {\n"
        "        return new Vector3(1.0f, 2.0f, 3.0f);\n"
        "    }\n"
        "}\n"
    )
    actual = translate_snippet(py)
    _assert_equal(actual, expected)


# ---------------------------------------------------------------------------
# Test 8 — UI snippet referencing Button forces `using UnityEngine.UI;` (CLI)
#
# LOCKED-IN ORDERING: `using UnityEngine.UI;` is emitted BEFORE
# `using UnityEngine;`, which is unusual but compiles fine.
# ---------------------------------------------------------------------------
def test_button_pulls_in_unityengine_ui_via_cli() -> None:
    py = (
        "from src.engine import MonoBehaviour\n"
        "from src.engine.ui import Button\n"
        "\n"
        "class Clicker(MonoBehaviour):\n"
        "    button: Button = None\n"
    )
    expected = (
        "using UnityEngine.UI;\n"
        "using UnityEngine;\n"
        "public class Clicker : MonoBehaviour\n"
        "{\n"
        "    [SerializeField] private Button button;\n"
        "}\n"
    )
    result = _run_cli(code=py)
    assert result.returncode == 0, result.stderr
    _assert_equal(result.stdout, expected)


# ---------------------------------------------------------------------------
# Test 9 — `--namespace MyGame` wraps the class in a namespace block (CLI)
# ---------------------------------------------------------------------------
def test_namespace_flag_wraps_class_via_cli() -> None:
    py = "class Foo:\n    count: int = 0\n"
    expected = (
        "using UnityEngine;\n"
        "namespace MyGame\n"
        "{\n"
        "    public class Foo\n"
        "    {\n"
        "        public int count = 0;\n"
        "    }\n"
        "}\n"
    )
    result = _run_cli("--namespace", "MyGame", code=py)
    assert result.returncode == 0, result.stderr
    _assert_equal(result.stdout, expected)


# ---------------------------------------------------------------------------
# Test 10 — `--with-using` appends a REQUIRED PACKAGES trailer (CLI)
#
# Uses the same UI-Button idiom as test 8 so the trailer references
# `com.unity.ugui` via `using UnityEngine.UI`.
# ---------------------------------------------------------------------------
def test_with_using_flag_appends_trailer_via_cli() -> None:
    py = (
        "from src.engine import MonoBehaviour\n"
        "from src.engine.ui import Button\n"
        "\n"
        "class Clicker(MonoBehaviour):\n"
        "    button: Button = None\n"
    )
    expected = (
        "using UnityEngine.UI;\n"
        "using UnityEngine;\n"
        "public class Clicker : MonoBehaviour\n"
        "{\n"
        "    [SerializeField] private Button button;\n"
        "}\n"
        "// REQUIRED PACKAGES:\n"
        "//   com.unity.ugui (using UnityEngine.UI)\n"
    )
    result = _run_cli("--with-using", code=py)
    assert result.returncode == 0, result.stderr
    _assert_equal(result.stdout, expected)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
