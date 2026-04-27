"""Sub-1s Python → C# preview tool (M-10).

Pipe a Python fragment in, get the translator's C# output back. No project
context, no scaffolder, no scene serializer — just `parse_python` →
`translate` and write the result to stdout. Designed for LLM agents and
humans to ask "what would this Python translate to?" without paying the full
pipeline cost.

Usage:
  python tools/translate_snippet.py --code "class Foo: pass"
  python tools/translate_snippet.py --file path/to/snippet.py
  echo 'class Foo: pass' | python tools/translate_snippet.py
  python tools/translate_snippet.py --file snippet.py --diff expected.cs

Exit codes:
  0 — translated successfully (and matched --diff fixture if provided)
  1 — translation produced output that diverges from --diff fixture
  2 — invalid arguments or input
  3 — translator raised an exception while parsing or translating
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.translator.python_parser import parse_python  # noqa: E402
from src.translator.python_to_csharp import (  # noqa: E402
    detect_required_packages,
    translate,
)


def translate_snippet(
    source: str,
    *,
    namespace: str | None = None,
    unity_version: int = 6,
    input_system: str = "new",
) -> str:
    """Translate a Python source string to C# without going through the project pipeline."""
    parsed = parse_python(source)
    return translate(
        parsed,
        namespace=namespace,
        unity_version=unity_version,
        input_system=input_system,
    )


def _read_input(args: argparse.Namespace) -> str:
    if args.code is not None:
        return args.code
    if args.file is not None:
        return Path(args.file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit(
        "tools/translate_snippet.py: provide --code, --file, or pipe Python on stdin"
    )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="translate_snippet",
        description="Sub-1s Python → C# preview using the unity-py-sim translator.",
    )
    src = p.add_mutually_exclusive_group()
    src.add_argument("--code", help="Inline Python source to translate.")
    src.add_argument("--file", help="Path to a .py file to translate.")
    p.add_argument(
        "--namespace",
        help="Optional C# namespace to wrap the output in (matches translator's project mode).",
    )
    p.add_argument("--unity-version", type=int, default=6, help="Target Unity version (default 6).")
    p.add_argument(
        "--input-system",
        default="new",
        choices=("new", "legacy"),
        help="Input system flavor (default 'new').",
    )
    p.add_argument(
        "--with-using",
        action="store_true",
        help=(
            "Append a `// REQUIRED PACKAGES:` trailer listing Unity packages the output "
            "would pull in via its `using` directives. Useful when checking whether a "
            "snippet would force a manifest.json edit."
        ),
    )
    p.add_argument(
        "--diff",
        help=(
            "Compare the translated output to a fixture file. Exits non-zero on mismatch "
            "and prints a unified diff. No diff = silent zero exit."
        ),
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        py_source = _read_input(args)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2
    if not py_source.strip():
        print("translate_snippet: empty input", file=sys.stderr)
        return 2

    try:
        cs = translate_snippet(
            py_source,
            namespace=args.namespace,
            unity_version=args.unity_version,
            input_system=args.input_system,
        )
    except Exception as e:  # noqa: BLE001 — surface any translator error to stderr
        print(f"translate_snippet: translator failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 3

    if args.with_using:
        pkgs = detect_required_packages(cs)
        if pkgs:
            trailer = "\n// REQUIRED PACKAGES:\n" + "\n".join(
                f"//   {p['package']} ({p['reason']})" for p in pkgs
            )
            cs = cs.rstrip("\n") + trailer + "\n"

    if args.diff:
        expected = Path(args.diff).read_text(encoding="utf-8")
        if cs == expected:
            return 0
        diff = "".join(
            difflib.unified_diff(
                expected.splitlines(keepends=True),
                cs.splitlines(keepends=True),
                fromfile=str(args.diff),
                tofile="<translated>",
            )
        )
        sys.stdout.write(diff)
        return 1

    sys.stdout.write(cs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
