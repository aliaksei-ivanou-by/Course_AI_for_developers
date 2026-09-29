#!/usr/bin/env python3
"""Focused tests for the public ``embacc`` command surface and dispatch."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from embacc import __version__, cli  # noqa: E402

SUPPORTED = ("setup", "run", "doctor", "refresh", "config", "reflect", "install", "self-update", "version")
REMOVED = ("understand", "do", "debug", "review", "verify", "route", "materialize", "update", "uninstall", "check", "stash", "unstash")


def main() -> int:
    failures: list[str] = []

    for command in SUPPORTED:
        if not re.search(rf"^\s{{4}}{re.escape(command)}(?:\s|$)", cli.HELP, re.MULTILINE):
            failures.append(f"supported command missing from help: {command}")
    for command in REMOVED:
        if re.search(rf"^\s{{4}}{re.escape(command)}(?:\s|$)", cli.HELP, re.MULTILINE):
            failures.append(f"removed command still appears in help: {command}")

    calls: list[tuple[str, list[str]]] = []
    original = cli._run
    cli._run = lambda script, args: calls.append((script, list(args))) or 0
    try:
        if cli.main([]) != 0 or calls.pop() != ("embacc_native.py", ["auto", "."]):
            failures.append("bare embacc does not dispatch to native auto mode")
        if cli.main(["reflect", ".", "--yes"]) != 0 or calls.pop() != ("embacc_native.py", ["reflect", ".", "--yes"]):
            failures.append("reflect dispatch is wrong")
        if cli.main(["install", ".", "--tools", "codex"]) != 0 or calls.pop() != ("install-accelerator.py", [".", "--tools", "codex"]):
            failures.append("install dispatch is wrong")
        if cli.main(["self-update", "--dry-run"]) != 0 or calls.pop() != ("embacc_selfupdate.py", ["--dry-run"]):
            failures.append("self-update dispatch is wrong")
    finally:
        cli._run = original

    if cli.main(["version"]) != 0:
        failures.append("version command failed")
    if cli.main(["definitely-removed"]) != 2:
        failures.append("unknown commands must return 2")

    if failures:
        print("EMBACC CLI TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"EMBACC CLI TEST: PASS (public surface + dispatch, version {__version__})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
