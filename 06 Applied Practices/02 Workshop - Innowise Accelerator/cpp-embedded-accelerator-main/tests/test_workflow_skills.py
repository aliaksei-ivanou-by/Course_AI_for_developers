#!/usr/bin/env python3
"""Regression tests for the maintained outstaff workflow layer."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import embacc_external as ext  # noqa: E402
import embacc_resources as resources  # noqa: E402

HOST_FRONTMATTER = re.compile(r'^---\nname: ([a-z0-9]+(?:-[a-z0-9]+)*)\ndescription: ("(?:\\.|[^"\\])*")\n---\n', re.S)


def host_safe_skill(path: Path) -> tuple[str, str]:
    content = path.read_text(encoding="utf-8")
    match = HOST_FRONTMATTER.match(content)
    if not match:
        raise ValueError("frontmatter is not Embacc's strict host-safe two-field format")
    description = json.loads(match.group(2))
    if not isinstance(description, str) or not description.strip():
        raise ValueError("description is empty or not a string")
    return match.group(1), description


EXPECTED = {
    "project-onboard", "feature", "bug", "review-pr", "pr-review-response", "task-workspace", "handoff",
    "requirements-analyst", "requirements-clarifier", "writing-plans", "coder", "testing",
    "systematic-debugger", "self-review", "code-reviewer", "verify", "stabilize",
}


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def text(name: str) -> str:
    return (ROOT / ".agents" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    names = {p.parent.name for p in resources.canonical_skills(ROOT)}
    expect(names == EXPECTED, f"workflow skill set mismatch: {sorted(names)}", failures)
    expect("reflect" not in names, "reflect must remain a CLI operation, not a canonical skill name", failures)
    for skill_path in resources.canonical_skills(ROOT):
        try:
            parsed_name, _description = host_safe_skill(skill_path)
            expect(parsed_name == skill_path.parent.name, f"host-visible skill name mismatch: {skill_path}", failures)
        except (ValueError, json.JSONDecodeError) as exc:
            failures.append(f"host cannot safely parse {skill_path.relative_to(ROOT)}: {exc}")

    feature = text("feature")
    bug = text("bug")
    workspace = text("task-workspace")
    onboard = text("project-onboard")
    stabilize = text("stabilize")

    review_response = text("pr-review-response")
    testing = text("testing")
    for required in ("accept", "push back", "clarify", "defer", "verify"):
        expect(required.lower() in review_response.lower(), f"PR review-response flow missing {required}", failures)
    expect("stable public seam" in testing or "public seam" in testing, "testing skill lacks seam-first guidance", failures)

    for required in ("HUMAN GATE — spec", "HUMAN GATE — plan", "STATE.md", "spec.md", "plan.md"):
        expect(required in feature, f"feature flow missing {required}", failures)
    for required in ("Reproduce", "HUMAN GATE — diagnosis", "HUMAN GATE — fix plan", "diagnosis.md"):
        expect(required in bug, f"bug flow missing {required}", failures)
    expect("<external_state_dir>/tasks/<slug>/" in workspace, "task workspace is not external", failures)
    expect("customer repository" in workspace, "task workspace lacks repository-write boundary", failures)

    for candidate in ("Jira", "Confluence", "Context7", "GitHub", "GitLab", "observability"):
        expect(candidate.lower() in onboard.lower(), f"onboarding does not consider {candidate}", failures)
    expect("mcp/servers.json" in onboard, "onboarding does not write project MCP config", failures)
    expect("authoritative documentation" in onboard, "onboarding may use stale MCP recipes", failures)
    expect("Never ask the developer to paste" in onboard, "onboarding lacks secret handling rule", failures)
    expect("embacc reflect" in stabilize and "separate" in stabilize, "stabilize/reflect distinction missing", failures)

    with tempfile.TemporaryDirectory(prefix="embacc-workflow-") as td:
        old = os.environ.get(ext.HOME_ENV)
        os.environ[ext.HOME_ENV] = str(Path(td) / "home")
        try:
            repo = Path(td) / "repo"
            repo.mkdir()
            (repo / "main.cpp").write_text("int main(){}\n", encoding="utf-8")
            identity = ext.project_identity(repo)
            state = ext.ensure_project_state(identity)
            expect((state / "tasks").is_dir(), "external project state did not create tasks/", failures)
            expect((state / "mcp").is_dir(), "external project state did not create mcp/", failures)
        finally:
            if old is None:
                os.environ.pop(ext.HOME_ENV, None)
            else:
                os.environ[ext.HOME_ENV] = old

    if failures:
        print("WORKFLOW SKILLS TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("WORKFLOW SKILLS TEST: PASS (host-safe frontmatter + routes/gates/external tasks/onboarding/stabilize)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
