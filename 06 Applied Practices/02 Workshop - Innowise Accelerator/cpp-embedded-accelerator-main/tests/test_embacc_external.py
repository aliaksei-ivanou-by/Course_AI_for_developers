#!/usr/bin/env python3
"""Regression tests for external project identity, core cache, and state isolation."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import embacc_external as ext  # noqa: E402


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {(result.stderr or result.stdout).strip()}")
    return result


def make_repo(parent: Path, name: str, *, remote: str | None = None) -> Path:
    repo = parent / name
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    source = repo / "src" / "main.cpp"
    source.parent.mkdir(parents=True)
    source.write_text("int main() { return 0; }\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "baseline")
    if remote:
        git(repo, "remote", "add", "origin", remote)
    return repo


def snapshot(repo: Path) -> set[Path]:
    return {p.relative_to(repo) for p in repo.rglob("*") if ".git" not in p.relative_to(repo).parts}


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="embacc-external-test-") as td:
        base = Path(td)
        os.environ["ACCELERATOR_HOME"] = str(base / "embacc-home")

        a = make_repo(base, "app")
        other = base / "other"
        other.mkdir()
        b = make_repo(other, "app")
        ida = ext.project_identity(a)
        idb = ext.project_identity(b)
        expect(ida.id != idb.id, "same-named unrelated repositories must not share a project id", failures)
        expect(ext.project_identity(a).id == ida.id, "project identity must be stable", failures)

        remote_repo = make_repo(base, "remote", remote="https://github.com/Example/Repo.git")
        remote_id = ext.project_identity(remote_repo)
        expect(remote_id.key_source == "remote", "origin remote should be the preferred identity key", failures)
        expect(
            ext.normalize_remote("https://github.com/Example/Repo.git") == ext.normalize_remote("git@github.com:Example/Repo.git"),
            "SSH and HTTPS forms of the same remote must normalize identically",
            failures,
        )

        before = snapshot(a)
        core = ext.ensure_core(ROOT)
        expect((core / ".agents" / "skills").is_dir(), "external core must contain canonical skills", failures)
        expect(not (core / "scripts").exists(), "external core must contain skills only, not runtime scripts", failures)
        expect(snapshot(a) == before, "building/reusing the external core must not touch a repository", failures)
        marker_mtime = (core / ".complete").stat().st_mtime
        ext.ensure_core(ROOT)
        expect((core / ".complete").stat().st_mtime == marker_mtime, "completed core cache should be reused", failures)

        state_a = ext.ensure_project_state(ida)
        state_b = ext.ensure_project_state(idb)
        (state_a / "state" / "marker.txt").write_text("A", encoding="utf-8")
        expect(not (state_b / "state" / "marker.txt").exists(), "project state must remain isolated", failures)

        exotic_parent = base / "unicode"
        exotic_parent.mkdir()
        for name in ("Project With Spaces", "Проект-Ω-测试"):
            repo = make_repo(exotic_parent, name)
            identity = ext.project_identity(repo)
            expect(bool(identity.id), f"identity resolution failed for {name!r}", failures)
            expect(ext.ensure_project_state(identity).is_dir(), f"state directory creation failed for {name!r}", failures)

    if failures:
        print("EMBACC EXTERNAL STATE TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("EMBACC EXTERNAL STATE TEST: PASS (identity/skills-only core/isolation/exotic paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
