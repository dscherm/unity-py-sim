#!/usr/bin/env python3
"""Playtest wrapper — runs an example and auto-records errors and feedback.

Usage:
    python tools/playtest.py breakout          # run breakout
    python tools/playtest.py pong              # run pong
    python tools/playtest.py fsm_platformer    # run fsm platformer
    python tools/playtest.py breakout --frames 500  # headless with frame limit

Captures:
    - All runtime errors/exceptions → data/lessons/playtest_errors.jsonl
    - Auto-appends new gotchas to data/lessons/gotchas.md
    - Logs session summary to .ralph/playtest_log.jsonl
"""

import sys
import os
import io
import json
import subprocess
import traceback
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOTCHAS_FILE = ROOT / "data" / "lessons" / "gotchas.md"
ERROR_LOG = ROOT / "data" / "lessons" / "playtest_errors.jsonl"
SESSION_LOG = ROOT / ".ralph" / "playtest_log.jsonl"
OBS_FILE = ROOT / ".ralph" / "observations.jsonl"
RALPH_UNIVERSAL = Path("D:/Projects/ralph-universal")

EXAMPLES = {
    "breakout": "examples/breakout/run_breakout.py",
    "pong": "examples/pong/run_pong.py",
    "fsm_platformer": "examples/fsm_platformer/run_fsm_platformer.py",
    "fsm": "examples/fsm_platformer/run_fsm_platformer.py",
}


def run_playtest(example: str, extra_args: list[str]) -> dict:
    """Run an example and capture all output."""
    script = EXAMPLES.get(example)
    if not script:
        print(f"Unknown example: {example}")
        print(f"Available: {', '.join(EXAMPLES.keys())}")
        sys.exit(1)

    script_path = ROOT / script
    if not script_path.exists():
        print(f"Script not found: {script_path}")
        sys.exit(1)

    ts = datetime.now(timezone.utc).isoformat()
    print(f"[playtest] Starting {example} at {ts}")
    print(f"[playtest] Errors will be auto-recorded to data/lessons/")
    print()

    # Run the example, capturing stderr for errors
    cmd = [sys.executable, str(script_path)] + extra_args
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        stderr=subprocess.PIPE,
        text=True,
    )

    stderr = proc.stderr or ""
    errors = parse_errors(stderr)
    duration = "unknown"  # subprocess doesn't track this easily

    session = {
        "timestamp": ts,
        "example": example,
        "exit_code": proc.returncode,
        "errors_found": len(errors),
        "error_types": list(set(e["type"] for e in errors)),
        "args": extra_args,
    }

    # Record session
    SESSION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(session) + "\n")

    # Record errors
    if errors:
        print(f"\n[playtest] Captured {len(errors)} error(s):")
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)

        for err in errors:
            err["timestamp"] = ts
            err["example"] = example
            with open(ERROR_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(err) + "\n")
            print(f"  - {err['type']}: {err['message'][:80]}")

        # Auto-append to gotchas.md
        append_gotchas(errors, example, ts)
        print(f"\n[playtest] Errors recorded to:")
        print(f"  {ERROR_LOG}")
        print(f"  {GOTCHAS_FILE}")
    else:
        print(f"\n[playtest] Clean run — no errors detected.")

    # Emit observation record for ralph-universal sync
    emit_observation(session, errors)

    print(f"[playtest] Session logged to {SESSION_LOG}")
    return session


def parse_errors(stderr: str) -> list[dict]:
    """Extract structured errors from stderr output."""
    errors = []
    lines = stderr.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        # Python traceback
        if "Traceback (most recent call last):" in line:
            tb_lines = [line]
            i += 1
            while i < len(lines) and not (
                lines[i] and not lines[i].startswith(" ") and ":" in lines[i]
                and "File " not in lines[i]
            ):
                tb_lines.append(lines[i])
                i += 1
            if i < len(lines):
                tb_lines.append(lines[i])
                error_line = lines[i]
                # Parse error type and message
                if ":" in error_line:
                    parts = error_line.split(":", 1)
                    err_type = parts[0].strip()
                    err_msg = parts[1].strip() if len(parts) > 1 else ""
                else:
                    err_type = error_line.strip()
                    err_msg = ""

                # Extract file and line from traceback
                file_info = ""
                for tl in tb_lines:
                    if 'File "' in tl and "breakout" in tl.lower() or "pong" in tl.lower() or "fsm" in tl.lower():
                        file_info = tl.strip()

                errors.append({
                    "type": err_type,
                    "message": err_msg,
                    "file": file_info,
                    "traceback": "\n".join(tb_lines[-6:]),  # last 6 lines
                })
            i += 1
        # Simple error line
        elif "Error" in line or "Exception" in line:
            if "cffi callback" not in line and "pygame" not in line.lower():
                errors.append({
                    "type": "RuntimeError",
                    "message": line.strip(),
                    "file": "",
                    "traceback": line,
                })
            i += 1
        else:
            i += 1

    # Deduplicate by type+message
    seen = set()
    unique = []
    for e in errors:
        key = (e["type"], e["message"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique


def append_gotchas(errors: list[dict], example: str, ts: str):
    """Append new errors to gotchas.md if not already documented."""
    if not GOTCHAS_FILE.exists():
        return

    existing = GOTCHAS_FILE.read_text(encoding="utf-8")

    new_entries = []
    for err in errors:
        # Check if this error type is already documented
        if err["message"] and err["message"][:40] in existing:
            continue
        if err["type"] in existing and err.get("file", "") and err["file"][:30] in existing:
            continue

        entry = (
            f"- **{err['type']}**: `{err['message'][:100]}` "
            f"— found in {example} playtest ({ts[:10]})"
        )
        if err.get("file"):
            entry += f"\n  Source: `{err['file'][:100]}`"
        new_entries.append(entry)

    if new_entries:
        section = f"\n## Playtest Errors (auto-recorded)\n" + "\n".join(new_entries) + "\n"
        # Check if section already exists
        if "## Playtest Errors" in existing:
            # Append to existing section
            existing = existing.rstrip() + "\n" + "\n".join(new_entries) + "\n"
        else:
            existing = existing.rstrip() + "\n" + section

        GOTCHAS_FILE.write_text(existing, encoding="utf-8")


def emit_observation(session: dict, errors: list[dict]):
    """Emit an observation record to .ralph/observations.jsonl and ralph-universal."""
    ts = session["timestamp"]
    example = session["example"]
    project = ROOT.name

    # Build error signatures from parsed errors
    error_signatures = []
    for err in errors:
        sig = f"{err['type']}: {err['message'][:80]}"
        error_signatures.append(sig)

    # Deterministic id from timestamp + example
    raw_id = f"playtest-{example}-{ts}"
    short_hash = hashlib.sha1(raw_id.encode()).hexdigest()[:7]

    obs = {
        "version": "1",
        "id": f"obs-playtest-{short_hash}",
        "timestamp": ts,
        "project": project,
        "run_id": "playtest",
        "iteration": 0,
        "files": {"count": 0, "test_files_touched": False},
        "gate": {
            "result": "pass" if not errors else "fail",
        },
        "error_signatures": error_signatures,
        "source": "playtest",
        "example": example,
    }

    obs_json = json.dumps(obs)

    # Write to local .ralph/observations.jsonl
    OBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OBS_FILE, "a", encoding="utf-8") as f:
        f.write(obs_json + "\n")

    # Sync to ralph-universal global observations if available
    global_dir = RALPH_UNIVERSAL / "observations"
    if global_dir.is_dir():
        global_file = global_dir / f"{project}.jsonl"
        with open(global_file, "a", encoding="utf-8") as f:
            f.write(obs_json + "\n")
        print(f"[playtest] Observation synced to {global_file}")

    print(f"[playtest] Observation recorded: gate={obs['gate']['result']}, "
          f"errors={len(error_signatures)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/playtest.py <example> [--frames N] [--headless]")
        print(f"Examples: {', '.join(EXAMPLES.keys())}")
        sys.exit(1)

    example_name = sys.argv[1]
    extra = sys.argv[2:]
    run_playtest(example_name, extra)
