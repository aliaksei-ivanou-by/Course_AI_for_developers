#!/usr/bin/env python3
"""Run deterministic tests; add --live for external agent/model checks."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_TESTS = (
    "tests/test_package.py",
    "tests/test_workflow_skills.py",
    "tests/test_discovery_projectdoc.py",
    "tests/test_adapters.py",
    "tests/test_astgrep.py",
    "tests/test_native_commands.py",
    "tests/test_reflect.py",
    "tests/test_gitguard.py",
    "tests/test_install_accelerator.py",
    "tests/test_embacc_external.py",
    "tests/test_embacc_selfupdate.py",
    "tests/test_embacc_cli.py",
    "tests/test_pi_safety.py",
)
LIVE_TESTS = ("tests/test_opencode_safety.py", "tests/test_claude_safety.py")


def run(path: str) -> bool:
    print(f"\n==> {path}", flush=True)
    process = subprocess.Popen(
        [sys.executable, path], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate(timeout=5)
        print("TIMEOUT", file=sys.stderr)
        if stdout:
            print(stdout, end="")
        if stderr:
            print(stderr, end="", file=sys.stderr)
        return False
    if stdout:
        print(stdout, end="")
    if stderr:
        print(stderr, end="", file=sys.stderr)
    return process.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="also call installed external agents/models")
    args = parser.parse_args()

    selected = LOCAL_TESTS + (LIVE_TESTS if args.live else ())
    failures = [path for path in selected if not run(path)]
    print()
    if failures:
        print("FAILED: " + ", ".join(failures))
        return 1
    print(f"PASS: {len(selected)} test module(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
