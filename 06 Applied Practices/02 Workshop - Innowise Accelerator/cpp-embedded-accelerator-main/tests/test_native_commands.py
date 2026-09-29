#!/usr/bin/env python3
"""Smoke tests for setup/run/doctor/refresh/config in external-state mode."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "scripts" / "embacc_native.py"


def git(repo: Path, *args: str) -> None:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)


def make_repo(parent: Path, name: str, *, customer_agents: bool = False) -> Path:
    repo = parent / name
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)\nproject(x CXX)\n", encoding="utf-8")
    if customer_agents:
        (repo / "AGENTS.md").write_text("# Customer instructions\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "baseline")
    return repo


def snapshot(repo: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(repo): path.read_bytes()
        for path in repo.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(repo).parts
    }


def run(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(NATIVE), *args],
        cwd=ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=30,
    )


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="embacc-native-") as td:
        base = Path(td)
        env = {
            **os.environ,
            "ACCELERATOR_HOME": str(base / "home"),
            "CODEX_HOME": str(base / "codex"),
            "EMBACC_CODEX_SKILLS_ROOT": str(base / "codex-user-skills"),
        }
        repo = make_repo(base, "repo", customer_agents=True)
        before = snapshot(repo)

        setup = run(env, "setup", str(repo), "--no-agent")
        expect(setup.returncode == 0, f"setup failed: {setup.stderr}", failures)
        expect(snapshot(repo) == before, "setup modified the client repository", failures)

        projects = list((base / "home" / "projects").iterdir())
        expect(len(projects) == 1, "setup did not create exactly one external project state", failures)
        state = projects[0]
        expect((state / "PROJECT.md").is_file(), "setup did not create external PROJECT.md", failures)
        expect((state / "discovery.json").is_file(), "setup did not save discovery", failures)
        mcp_example = state / "mcp" / "servers.json.example"
        expect(mcp_example.is_file(), "setup did not create MCP example", failures)
        try:
            json.loads(mcp_example.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"MCP example is not valid JSON: {exc}")
        agent_state = json.loads((state / "agent.json").read_text(encoding="utf-8"))
        expect(agent_state.get("guard_git") is True, "git guard default was not persisted", failures)
        expect(agent_state.get("canonical_skills") is True, "skills default was not persisted", failures)

        # ast-grep: hidden state only, graceful either way (CI has no ast-grep
        # installed -- this exercises the "unavailable" branch there and the
        # real scan branch wherever the binary is present, never a hard skip).
        discovery = json.loads((state / "discovery.json").read_text(encoding="utf-8"))
        ast_grep = discovery.get("ast_grep")
        expect(isinstance(ast_grep, dict) and "available" in ast_grep, "setup did not record ast-grep status in discovery.json", failures)
        project_md_text = (state / "PROJECT.md").read_text(encoding="utf-8")
        expect("## Structural code search" in project_md_text, "PROJECT.md is missing the ast-grep section", failures)
        expect((state / "ast-grep" / "index.json").is_file(), "ast-grep index.json was not written to hidden state", failures)
        if ast_grep and ast_grep.get("available"):
            expect((state / "ast-grep" / "sgconfig.yml").is_file(), "ast-grep available but hidden sgconfig.yml was not written", failures)
        else:
            expect(not (state / "ast-grep" / "sgconfig.yml").exists(), "ast-grep unavailable but a hidden sgconfig.yml was still written", failures)
        expect(snapshot(repo) == before, "ast-grep indexing modified the client repository", failures)

        doctor = run(env, "--source-root", str(ROOT), "doctor", str(repo))
        expect(doctor.returncode == 0 and "EMBACC PROJECT DIAGNOSTIC" in doctor.stdout, f"doctor failed: {doctor.stderr}", failures)
        expect("canonical workflow package: PASS (17 host-safe skills)" in doctor.stdout, "doctor did not validate canonical workflow frontmatter", failures)
        expect("ast-grep:" in doctor.stdout, "doctor did not report ast-grep status", failures)
        expect(snapshot(repo) == before, "doctor modified the client repository", failures)

        codex_setup = run(env, "setup", str(repo), "--agent", "codex")
        expect(codex_setup.returncode == 0, f"Codex setup failed: {codex_setup.stderr}", failures)
        codex_dry = run(
            env, "--source-root", str(ROOT), "run", "codex", str(repo),
            "--agent-binary", "fake-codex", "--dry-run",
        )
        expect(codex_dry.returncode == 0, f"Codex dry-run preparation failed: {codex_dry.stderr}", failures)
        codex_doctor = run(env, "--source-root", str(ROOT), "doctor", str(repo))
        expect("Codex effective workflow skills: 17/17" in codex_doctor.stdout, "doctor cannot confirm Codex workflow skill visibility", failures)
        expect("Codex project context profile: PASS" in codex_doctor.stdout, "doctor cannot confirm Codex project context profile", failures)
        expect(snapshot(repo) == before, "Codex setup/run/doctor modified the client repository", failures)

        config = run(env, "config", str(repo))
        expect(config.returncode == 0 and config.stdout.strip() == str(state), "config printed wrong external directory", failures)

        refresh = run(env, "refresh", str(repo))
        expect(refresh.returncode == 0 and "refreshed:" in refresh.stdout, f"refresh failed: {refresh.stderr}", failures)
        expect(snapshot(repo) == before, "refresh modified the client repository", failures)

        no_skills = run(env, "setup", str(repo), "--no-agent", "--no-skills")
        expect(no_skills.returncode == 0, f"setup --no-skills failed: {no_skills.stderr}", failures)
        agent_state = json.loads((state / "agent.json").read_text(encoding="utf-8"))
        expect(agent_state.get("canonical_skills") is False, "--no-skills did not persist", failures)

        dry_run = run(
            env,
            "--source-root", str(ROOT),
            "run", "claude", str(repo),
            "--agent-binary", "fake-claude",
            "--dry-run",
        )
        expect(dry_run.returncode == 0 and "DRY RUN" in dry_run.stdout, f"run --dry-run failed: {dry_run.stderr}", failures)
        expect(snapshot(repo) == before, "run --dry-run modified the client repository", failures)

        fresh = make_repo(base, "fresh")
        fresh_before = snapshot(fresh)
        fallback = run(env, "refresh", str(fresh))
        expect(fallback.returncode == 0 and "running full setup" in fallback.stdout, f"refresh fallback failed: {fallback.stderr}", failures)
        expect(snapshot(fresh) == fresh_before, "refresh fallback modified the repository", failures)

        help_result = run(env, "setup", "--help")
        expect("skills-codex" not in help_result.stdout, "removed --skills-codex still appears in setup help", failures)

    if failures:
        print("NATIVE COMMAND TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("NATIVE COMMAND TEST: PASS (external-state workflow remains repo-write-free)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
