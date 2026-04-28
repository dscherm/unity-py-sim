"""Generate the data/idioms/ catalog from inline idiom specs (M-11).

Each idiom is one of:
  (1) safe-only — Python snippet + frozen C# expected output. The catalog locks
      in the translator's CURRENT behavior so future translator changes either
      stay equivalent or fail loudly and force an intentional fixture refresh.
  (2) unsafe-paired — adds an `unsafe.py` showing the failure mode plus a
      `unsafe.notes.md` describing why the unsafe form is bad and what to do
      instead. The `safe.py` is the recommended rewrite.

Run with no args to (re)generate the entire catalog under `data/idioms/`. Run
with `--check` to verify without writing — useful as a diff-detector.

The script does NOT replace `tests/idioms/test_idiom_catalog.py` — that test
runs `tools/translate_snippet.py --diff` against every safe.cs.expected and
fails if reality drifts. Re-run this script intentionally when fixtures need
updating; commit the diff.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IDIOMS_ROOT = REPO_ROOT / "data" / "idioms"
SNIPPET_TOOL = REPO_ROOT / "tools" / "translate_snippet.py"


@dataclass
class Idiom:
    area: str
    name: str
    summary: str
    safe_py: str
    extra_args: list[str] = field(default_factory=list)
    unsafe_py: str | None = None
    unsafe_notes: str | None = None
    why_safe: str = ""
    why_unsafe: str = ""


# 20 idioms across 8 feature areas — sourced from data/lessons/{patterns,gotchas}.md
# plus the 3 fresh observations from the M-10 validation agent.
IDIOMS: list[Idiom] = [
    # ── lifecycle ────────────────────────────────────────────────────────────
    Idiom(
        area="lifecycle",
        name="start_method",
        summary="`def start(self)` translates to `void Start()` — the canonical Unity entry point.",
        safe_py='class Bootstrap:\n    def start(self):\n        pass\n',
        why_safe="Method-name lifecycle mapping is the safest possible idiom — direct Unity contract.",
    ),
    Idiom(
        area="lifecycle",
        name="update_self_transform",
        summary="`def update(self): self.transform.position += ...` lowers self → implicit instance reference.",
        safe_py=(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.math.vector import Vector3\n"
            "class Mover(MonoBehaviour):\n"
            "    def update(self):\n"
            "        self.transform.position += Vector3(1.0, 0.0, 0.0)\n"
        ),
        why_safe="Per-frame state mutation through transform is bread-and-butter Unity, fully covered.",
    ),
    Idiom(
        area="lifecycle",
        name="coroutine_with_waitforseconds",
        summary="Generator yields to `WaitForSeconds(...)` translate to `IEnumerator` + `yield return new WaitForSeconds(...)`.",
        safe_py=(
            "from src.engine.core import MonoBehaviour, WaitForSeconds\n"
            "from typing import Iterator\n"
            "class Spawner(MonoBehaviour):\n"
            "    def spawn_loop(self) -> Iterator:\n"
            "        yield WaitForSeconds(2.0)\n"
        ),
        why_safe="Coroutines were 'now handled' per data/lessons/patterns.md as of 2026-04-03.",
    ),
    # ── fields ───────────────────────────────────────────────────────────────
    Idiom(
        area="fields",
        name="typed_int_field",
        summary="`x: int = 5` becomes `public int x = 5;` — straight type+default mapping.",
        safe_py="class Counter:\n    count: int = 0\n",
        why_safe="Primitive-typed instance fields are the most-tested translator path.",
    ),
    Idiom(
        area="fields",
        name="typed_float_field",
        summary="`speed: float = 5.0` becomes `public float speed = 5.0f;` — note the `f` literal suffix.",
        safe_py="class Mover:\n    speed: float = 5.0\n",
        why_safe="Float literal suffix is auto-emitted; without it the C# compiler picks `double`.",
    ),
    Idiom(
        area="fields",
        name="bool_literal_true",
        summary="Python `True` lowers to C# `true` (lowercase). Critical: `True` in C# is a parse error.",
        safe_py="class Toggle:\n    active: bool = True\n",
        why_safe="`True/False/None` → `true/false/null` translation is tracked by the syntax compilation gate.",
    ),
    Idiom(
        area="fields",
        name="list_of_components",
        summary="`bricks: list[GameObject]` lowers to ARRAY form `GameObject[]`, NOT `List<GameObject>`.",
        safe_py=(
            "from src.engine.core import GameObject\n"
            "class Pool:\n"
            "    bricks: list[GameObject] = []\n"
        ),
        why_safe=(
            "PINNED to current behavior. Note: the M-10 validation agent flagged that the "
            "translator emits the array form (`GameObject[]`), not the generic list form "
            "(`List<GameObject>`), even while it still emits `using System.Collections.Generic;`. "
            "This contradicts gap-1 acceptance criteria in .claude/.ralph-spec.md. The idiom is "
            "captured here so any future translator change to `List<GameObject>` shows up as a "
            "fixture diff and forces an explicit decision."
        ),
    ),
    # ── naming ───────────────────────────────────────────────────────────────
    Idiom(
        area="naming",
        name="snake_case_method",
        summary="`def take_damage(self, dmg)` becomes `void TakeDamage(int dmg)`. Pascal-case applied.",
        safe_py=(
            "class Health:\n"
            "    hp: int = 100\n"
            "    def take_damage(self, dmg: int) -> None:\n"
            "        self.hp -= dmg\n"
        ),
        why_safe="Method-name conversion is robust per data/lessons/patterns.md.",
    ),
    Idiom(
        area="naming",
        name="upper_snake_constant",
        summary="`MAX_HEALTH: int = 100` is preserved as `MAX_HEALTH` (no Pascal-casing of UPPER_SNAKE).",
        safe_py="class Limits:\n    MAX_HEALTH: int = 100\n",
        why_safe="Constants stay UPPER_SNAKE in idiomatic C# for readability — translator respects this.",
    ),
    # ── inheritance ──────────────────────────────────────────────────────────
    Idiom(
        area="inheritance",
        name="monobehaviour_subclass",
        summary="`class Foo(MonoBehaviour)` becomes `public class Foo : MonoBehaviour`.",
        safe_py=(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    pass\n"
        ),
        why_safe="The single most fundamental Unity translation — inheritance from MonoBehaviour.",
    ),
    Idiom(
        area="inheritance",
        name="enum_subclass",
        summary="`class State(Enum)` with `IDLE = 0` members becomes `public enum State { Idle, ... }`.",
        safe_py=(
            "from enum import Enum\n"
            "class State(Enum):\n"
            "    IDLE = 0\n"
            "    RUNNING = 1\n"
        ),
        why_safe="Enum translation handled per data/lessons/patterns.md (since 2026-04-03).",
    ),
    # ── math ─────────────────────────────────────────────────────────────────
    Idiom(
        area="math",
        name="vector3_constructor_literal",
        summary="`Vector3(1.0, 2.0, 3.0)` becomes `new Vector3(1.0f, 2.0f, 3.0f)` — `f` suffixes auto-added.",
        safe_py=(
            "from src.engine.math.vector import Vector3\n"
            "class V:\n"
            "    def origin(self):\n"
            "        v = Vector3(1.0, 2.0, 3.0)\n"
        ),
        why_safe="Float-suffix promotion on Vector3 ctor args is a translator-correctness milestone.",
    ),
    Idiom(
        area="math",
        name="vector3_zero_constant",
        summary="`Vector3.zero` translates to `Vector3.zero` verbatim — static constants line up cleanly.",
        safe_py=(
            "from src.engine.math.vector import Vector3\n"
            "class V:\n"
            "    def at_origin(self):\n"
            "        return Vector3.zero\n"
        ),
        why_safe="Static-member access on math types is name-preserving across both languages.",
    ),
    # ── input ────────────────────────────────────────────────────────────────
    Idiom(
        area="input",
        name="keyboard_current_null_safe",
        summary=(
            "New Input System reads must use `Keyboard.current?.X.Y == true` — "
            "`Keyboard.current` is null in batchmode tests."
        ),
        safe_py=(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_system import Input\n"
            "class Player(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if Input.get_key_down('space'):\n"
            "            pass\n"
        ),
        extra_args=["--input-system", "new"],
        why_safe=(
            "Locks in the null-safe `?.X.Y == true` pattern that translator-input-system-null-guard "
            "(closed 2026-04-27) emits. Prevents regression to unconditional `Keyboard.current.X` "
            "accesses that throw NullReferenceException under Unity Test Framework PlayMode."
        ),
    ),
    # ── collections ──────────────────────────────────────────────────────────
    Idiom(
        area="collections",
        name="list_append",
        summary="`xs.append(x)` translates to `xs.Add(x);` (Unity uses C# List<T>.Add).",
        safe_py=(
            "class Pool:\n"
            "    items: list[int] = []\n"
            "    def add_one(self):\n"
            "        self.items.append(1)\n"
        ),
        why_safe="`.append` → `.Add` is one of the 'now handled' wins per data/lessons/patterns.md.",
    ),
    Idiom(
        area="collections",
        name="len_call",
        summary="`len(xs)` translates to `xs.Count` (assuming xs is a list field; arrays use .Length).",
        safe_py=(
            "class Pool:\n"
            "    items: list[int] = []\n"
            "    def size(self) -> int:\n"
            "        return len(self.items)\n"
        ),
        why_safe="`len()` mapping handled by translator's collection-aware lowering.",
    ),
    # ── unsafe (4) — paired before/after ─────────────────────────────────────
    Idiom(
        area="unsafe",
        name="property_decorator",
        summary="`@property` getters DO NOT lower to C# property syntax. Translator emits a regular method.",
        safe_py=(
            "class Health:\n"
            "    hp: int = 100\n"
            "    def get_max_hp(self) -> int:\n"
            "        return 100\n"
        ),
        unsafe_py=(
            "class Health:\n"
            "    hp: int = 100\n"
            "    @property\n"
            "    def max_hp(self) -> int:\n"
            "        return 100\n"
        ),
        unsafe_notes=(
            "Per data/lessons/patterns.md (Medium-difficulty section), `@property` is not "
            "converted to C# property syntax. Output is a method body but call-sites elsewhere "
            "in your code will still try to access it as a field, breaking compilation. "
            "Rewrite as an explicit `get_*` method named with `get_` prefix."
        ),
        why_safe="Explicit getter method translates predictably; reader knows it's a method call.",
        why_unsafe="@property compiles fine here in isolation but call-sites assume field-style access.",
    ),
    Idiom(
        area="unsafe",
        name="fstring_interpolation",
        summary="Python f-strings DO NOT lower to C# `$\"...\"` interpolation. Use `+` concatenation or `.ToString()`.",
        safe_py=(
            "class Score:\n"
            "    points: int = 0\n"
            "    def label(self) -> str:\n"
            "        return 'Score: ' + str(self.points)\n"
        ),
        unsafe_py=(
            "class Score:\n"
            "    points: int = 0\n"
            "    def label(self) -> str:\n"
            "        return f'Score: {self.points}'\n"
        ),
        unsafe_notes=(
            "Per data/lessons/patterns.md, f-strings are NOT converted. The output is invalid C# "
            "(literal `f'...'` syntax). Use string concatenation or call `.ToString()` explicitly."
        ),
        why_safe="String concatenation lowers cleanly to C# `+` operator.",
        why_unsafe="f'...' literal leaks verbatim into C# output, breaking compilation.",
    ),
    Idiom(
        area="unsafe",
        name="hasattr_check",
        summary="`hasattr(x, 'attr')` becomes a literal `true` ternary — drops the runtime check.",
        safe_py=(
            "from src.engine.core import GameObject\n"
            "class Probe:\n"
            "    target: GameObject\n"
            "    def safe_get(self):\n"
            "        if self.target is not None:\n"
            "            return self.target\n"
            "        return None\n"
        ),
        unsafe_py=(
            "from src.engine.core import GameObject\n"
            "class Probe:\n"
            "    target: GameObject\n"
            "    def safe_get(self):\n"
            "        return self.target if hasattr(self, 'target') else None\n"
        ),
        unsafe_notes=(
            "Per data/lessons/gotchas.md (Pacman section), `hasattr()` translates to a `true ? ... : null` "
            "ternary, dropping the actual reflection check. C# doesn't have hasattr; use null checks "
            "(`x is not None`) or interface checks instead."
        ),
        why_safe="Explicit null check translates to `if (target != null)` — the C# idiom.",
        why_unsafe="hasattr always-true short-circuits the safety check at runtime.",
    ),
    Idiom(
        area="unsafe",
        name="inline_method_import",
        summary="`from X import Y` inside a method body leaks verbatim as Python statement, invalid C#.",
        safe_py=(
            "from src.engine.core import GameObject\n"
            "class Loader:\n"
            "    def find_player(self):\n"
            "        return GameObject.find('Player')\n"
        ),
        unsafe_py=(
            "class Loader:\n"
            "    def find_player(self):\n"
            "        from src.engine.core import GameObject\n"
            "        return GameObject.find('Player')\n"
        ),
        unsafe_notes=(
            "Per data/lessons/patterns.md, method-body imports emit verbatim, producing invalid C# "
            "(`from ... import ...` is not a statement). Rewrite by hoisting the import to the "
            "module top so the translator can lift it into a C# `using` directive instead."
        ),
        why_safe="Module-top imports translate to C# `using` directives, hoisted properly.",
        why_unsafe="In-method import is a Python-only pattern; translator can't lift it.",
    ),
]


def _run_translator(idiom: Idiom) -> str:
    args = [sys.executable, str(SNIPPET_TOOL), "--code", idiom.safe_py, *idiom.extra_args]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=15)
    if proc.returncode != 0:
        raise RuntimeError(
            f"translator failed for {idiom.area}/{idiom.name}: "
            f"exit={proc.returncode} stderr={proc.stderr.strip()}"
        )
    return proc.stdout


def _readme(idiom: Idiom) -> str:
    body = [
        f"# {idiom.area}/{idiom.name}",
        "",
        idiom.summary,
        "",
        "## Files",
        "",
        "- `safe.py` — Python that translates cleanly (recommended form).",
        "- `safe.cs.expected` — frozen C# output. The idiom-catalog test runs",
        "  `tools/translate_snippet.py --file safe.py --diff safe.cs.expected`",
        "  and fails if the translator drifts.",
    ]
    if idiom.unsafe_py is not None:
        body += [
            "- `unsafe.py` — Python that translates BADLY. Captured for contrast.",
            "- `unsafe.notes.md` — failure-mode description and why `safe.py` is the rewrite.",
        ]
    body += [""]
    if idiom.why_safe:
        body += ["## Why this is safe", "", idiom.why_safe, ""]
    if idiom.why_unsafe:
        body += ["## Why the unsafe form fails", "", idiom.why_unsafe, ""]
    body += [
        "## Regenerating the fixture",
        "",
        "Re-run `python tools/build_idiom_catalog.py` to refresh `safe.cs.expected`",
        "if the translator's behavior on this idiom changes intentionally.",
        "",
    ]
    return "\n".join(body)


def _generate_idiom(idiom: Idiom, *, check_only: bool) -> tuple[bool, str]:
    target = IDIOMS_ROOT / idiom.area / idiom.name
    safe_cs = _run_translator(idiom)

    files: dict[Path, str] = {
        target / "safe.py": idiom.safe_py,
        target / "safe.cs.expected": safe_cs,
        target / "README.md": _readme(idiom),
    }
    if idiom.extra_args:
        files[target / "extra_args.txt"] = " ".join(idiom.extra_args) + "\n"
    if idiom.unsafe_py is not None:
        files[target / "unsafe.py"] = idiom.unsafe_py
    if idiom.unsafe_notes is not None:
        files[target / "unsafe.notes.md"] = idiom.unsafe_notes + "\n"

    drifted = False
    msg_lines: list[str] = []
    for path, content in files.items():
        existing = path.read_text(encoding="utf-8") if path.exists() else None
        if existing == content:
            continue
        drifted = True
        msg_lines.append(f"  drift: {path.relative_to(REPO_ROOT)}")
        if not check_only:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    return drifted, "\n".join(msg_lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the data/idioms/ catalog.")
    parser.add_argument(
        "--check", action="store_true",
        help="Compare disk to spec; exit 1 on drift; do not write.",
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Delete data/idioms/ before regenerating (orphan cleanup).",
    )
    args = parser.parse_args(argv)

    if args.clean and not args.check and IDIOMS_ROOT.exists():
        shutil.rmtree(IDIOMS_ROOT)

    drift_total = 0
    for idiom in IDIOMS:
        drifted, msg = _generate_idiom(idiom, check_only=args.check)
        if drifted:
            drift_total += 1
            print(f"[{idiom.area}/{idiom.name}]")
            if msg:
                print(msg)

    if args.check and drift_total:
        print(f"FAIL: {drift_total} idiom(s) drifted from spec.")
        return 1
    print(f"OK: {len(IDIOMS)} idiom(s) "
          + ("checked" if args.check else "(re)generated") + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
