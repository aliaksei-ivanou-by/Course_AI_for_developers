#!/usr/bin/env python3
"""Focused regression tests for the Claude git guard."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
import embacc_gitguard as guard  # noqa: E402


def probe(command: str) -> int:
    return guard.run({"tool_name": "Bash", "tool_input": {"command": command}})


def main() -> int:
    blocked = (
        "git push origin main",
        "git reset --hard HEAD~1",
        "git clean -fd",
        "git branch -D old",
        "git checkout .",
        "git restore .",
        "git worktree remove --force ../wt",
        "git commit -m test --no-verify",
        "git commit -n -m test",
        "git commit --no-gpg-sign -m test",
    )
    allowed = (
        "git status",
        "git diff",
        "git add -A",
        "git commit -m test",
        "git branch -d merged",
        "git clean -n",
        "git restore src/file.cpp",
        "cat > notes.md <<'EOF'\ngit push origin main\nEOF",
    )

    failures = [f"dangerous command was not blocked: {cmd}" for cmd in blocked if probe(cmd) != 2]
    failures += [f"safe command was blocked: {cmd}" for cmd in allowed if probe(cmd) != 0]
    if guard.run({"tool_name": "Read", "tool_input": {}}) != 0:
        failures.append("non-Bash tools should be ignored")

    if failures:
        print("GIT GUARD TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("GIT GUARD TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
