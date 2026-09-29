#!/usr/bin/env python3
"""Regression tests for the minimal repository installer."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-accelerator.py"
EXPECTED_SKILLS = {
    "bug",
    "code-reviewer",
    "coder",
    "feature",
    "handoff",
    "project-onboard",
    "pr-review-response",
    "requirements-analyst",
    "requirements-clarifier",
    "review-pr",
    "self-review",
    "stabilize",
    "systematic-debugger",
    "task-workspace",
    "testing",
    "verify",
    "writing-plans",
}


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INSTALLER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], text=True, capture_output=True, check=False, timeout=20
    )


def make_repo(parent: Path, name: str, *, agents: str | None = None) -> Path:
    repo = parent / name
    repo.mkdir()
    if git(repo, "init", "-q").returncode:
        raise RuntimeError("git init failed")
    (repo / "client.cpp").write_text("int client() { return 7; }\n", encoding="utf-8")
    if agents is not None:
        (repo / "AGENTS.md").write_text(agents, encoding="utf-8")
    git(repo, "add", "-A")
    result = git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "baseline")
    if result.returncode:
        raise RuntimeError(result.stderr)
    return repo


def files(repo: Path) -> set[Path]:
    return {
        path.relative_to(repo)
        for path in repo.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(repo).parts
    }


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="embacc-install-test-") as td:
        base = Path(td)
        repo = make_repo(base, "client")
        baseline = files(repo)

        dry = run(str(repo), "--tools", "codex", "--dry-run")
        expect(dry.returncode == 0, f"dry-run failed: {dry.stderr}", failures)
        expect(files(repo) == baseline, "dry-run changed repository files", failures)

        first = run(str(repo), "--tools", "codex")
        expect(first.returncode == 0, f"Codex install failed: {first.stderr}", failures)
        expect((repo / "AGENTS.md").is_file(), "AGENTS.md missing", failures)
        found_skills = {p.parent.name for p in (repo / ".agents/skills").glob("*/SKILL.md")}
        expect(found_skills == EXPECTED_SKILLS, f"wrong skills installed: {found_skills}", failures)
        expect(not (repo / ".codex").exists(), "Codex should need no generated .codex adapter", failures)
        expect(not (repo / "scripts").exists(), "runtime scripts leaked into client repository", failures)
        state_path = repo / ".accelerator-install.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        expect(state["tools"] == ["codex"], "wrong tool selection in state", failures)
        expect(all(isinstance(v, str) and len(v) == 64 for v in state["files"].values()), "state hashes are not minimal strings", failures)

        # Package upgrades must refresh an existing managed install instead of
        # rejecting the previous package version when the state schema is unchanged.
        state["version"] = "2.7.1"
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        again = run(str(repo), "--allow-dirty")
        expect(again.returncode == 0, f"cross-version repeat install/refresh failed: {again.stderr}", failures)
        refreshed_state = json.loads(state_path.read_text(encoding="utf-8"))
        expect(refreshed_state["version"] == "2.6.0", "refresh did not rewrite install state to current package version", failures)

        switch = run(str(repo), "--tools", "claude", "--allow-dirty")
        expect(switch.returncode == 0, f"tool switch to Claude failed: {switch.stderr}", failures)
        expect((repo / "CLAUDE.md").is_file(), "Claude template missing", failures)
        expect((repo / ".claude/settings.json").is_file(), "Claude settings missing", failures)
        claude_skills = list((repo / ".claude/skills").glob("acc-*/SKILL.md"))
        expect(len(claude_skills) == len(EXPECTED_SKILLS), "Claude thin adapters missing", failures)
        expect(not (repo / ".claude/agents").exists(), "redundant Claude subagents should not be generated", failures)

        switch2 = run(str(repo), "--tools", "opencode", "--allow-dirty")
        expect(switch2.returncode == 0, f"tool switch to OpenCode failed: {switch2.stderr}", failures)
        expect(not (repo / "CLAUDE.md").exists(), "stale Claude template was not removed", failures)
        expect(not (repo / ".claude").exists(), "stale Claude adapter directory was not pruned", failures)
        expect((repo / "opencode.json").is_file(), "OpenCode config missing", failures)
        expect(len(list((repo / ".opencode/commands").glob("acc-*.md"))) == len(EXPECTED_SKILLS), "OpenCode commands missing", failures)
        expect(not (repo / ".opencode/agents").exists(), "redundant OpenCode subagents should not be generated", failures)

        # Modified managed content must fail closed and preserve the local edit.
        agents = repo / "AGENTS.md"
        custom = agents.read_text(encoding="utf-8") + "\n# local edit\n"
        agents.write_text(custom, encoding="utf-8")
        conflict = run(str(repo), "--tools", "pi", "--allow-dirty")
        expect(conflict.returncode == 2, "modified managed file did not produce a conflict", failures)
        expect(agents.read_text(encoding="utf-8") == custom, "conflicting local edit was overwritten", failures)

        dirty = make_repo(base, "dirty")
        (dirty / "client.cpp").write_text("dirty\n", encoding="utf-8")
        refused = run(str(dirty), "--tools", "pi")
        expect(refused.returncode == 1 and "dirty" in refused.stderr.lower(), "dirty working tree was not refused", failures)

        occupied = make_repo(base, "occupied", agents="# customer policy\n")
        occupied_result = run(str(occupied), "--tools", "codex")
        expect(occupied_result.returncode == 2, "pre-existing AGENTS.md was not treated as a conflict", failures)
        expect((occupied / "AGENTS.md").read_text(encoding="utf-8") == "# customer policy\n", "customer AGENTS.md changed", failures)

        invalid = run(str(repo), "--tools", "bogus", "--dry-run")
        expect(invalid.returncode == 1 and "unknown tools" in invalid.stderr, "unknown tool was accepted", failures)

    if failures:
        print("EMBACC INSTALL TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("EMBACC INSTALL TEST: PASS (dry-run/install/cross-version-refresh/tool-switch/conflict/dirty-tree)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
