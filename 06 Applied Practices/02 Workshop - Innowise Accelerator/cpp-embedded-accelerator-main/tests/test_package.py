#!/usr/bin/env python3
"""Fast structural validation for the source checkout and install payload."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from embacc_resources import TOOLS, canonical_skills, materialize_resources  # noqa: E402

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
FORBIDDEN_NAMES = {
    "knowledge-packs",
    "skill-creator",
    "accelerator_package.py",
    "configure-tools.py",
    "sync-tool-adapters.py",
    "embacc_policy.py",
    "detect-project-profile.py",
    "search-knowledge-packs.py",
    "DOD.md",
    "GOLDEN-PRINCIPLES.md",
    "TOOL-SUPPORT.md",
}
REQUIRED_RUNTIME = {
    "embacc_adapters.py",
    "embacc_astgrep.py",
    "embacc_discover.py",
    "embacc_external.py",
    "embacc_gitguard.py",
    "embacc_native.py",
    "embacc_projectdoc.py",
    "embacc_reflect.py",
    "embacc_resources.py",
    "embacc_selfupdate.py",
    "install-accelerator.py",
}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_skills(errors: list[str]) -> None:
    try:
        names = {path.parent.name for path in canonical_skills(ROOT)}
    except Exception as exc:
        fail(errors, f"canonical skills invalid: {exc}")
        return
    if names != EXPECTED_SKILLS:
        fail(errors, f"canonical skill set mismatch: expected={sorted(EXPECTED_SKILLS)} actual={sorted(names)}")


def validate_layout(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if "__pycache__" in path.parts or ".git" in path.parts:
            continue
        if path.name in FORBIDDEN_NAMES:
            fail(errors, f"obsolete artifact remains: {path.relative_to(ROOT)}")
    scripts = {path.name for path in (ROOT / "scripts").glob("*.py")}
    missing = REQUIRED_RUNTIME - scripts
    if missing:
        fail(errors, "missing runtime scripts: " + ", ".join(sorted(missing)))

    required_templates = (
        ROOT / "tooling/templates/claude/CLAUDE.md",
        ROOT / "tooling/templates/claude/.claude/settings.json",
        ROOT / "tooling/templates/opencode/opencode.json",
        ROOT / "tooling/templates/pi/.pi/settings.json",
        ROOT / "tooling/templates/pi/.pi/extensions/accelerator-safety.ts",
    )
    for path in required_templates:
        if not path.is_file():
            fail(errors, f"missing tool template: {path.relative_to(ROOT)}")
    if (ROOT / "tooling/templates/codex").exists():
        fail(errors, "Codex template should not exist; Codex consumes AGENTS.md/.agents/skills natively")



def validate_versions(errors: list[str]) -> None:
    import tomllib

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project_version = pyproject["project"]["version"]
    pixi_version = pyproject["tool"]["pixi"]["package"]["version"]
    from embacc_resources import PACKAGE_VERSION

    package_init: dict[str, object] = {}
    exec((ROOT / "src" / "embacc" / "__init__.py").read_text(encoding="utf-8"), package_init)
    public_version = package_init.get("__version__")
    versions = {project_version, pixi_version, PACKAGE_VERSION, public_version}
    if len(versions) != 1:
        fail(errors, f"version mismatch: project={project_version} pixi={pixi_version} resources={PACKAGE_VERSION} public={public_version}")

def validate_python(errors: list[str]) -> None:
    for base in (ROOT / "scripts", ROOT / "tests", ROOT / "src"):
        for path in base.rglob("*.py"):
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except Exception as exc:
                fail(errors, f"Python compile failed {path.relative_to(ROOT)}: {exc}")


def validate_payloads(errors: list[str]) -> None:
    cases = ((), ("codex",), ("claude",), ("opencode",), ("pi",), TOOLS)
    for selected in cases:
        with tempfile.TemporaryDirectory(prefix="embacc-payload-") as td:
            target = Path(td)
            try:
                materialize_resources(ROOT, target, tuple(selected))
            except Exception as exc:
                fail(errors, f"materialization failed for {selected}: {exc}")
                continue
            files = {path.relative_to(target) for path in target.rglob("*") if path.is_file()}
            if Path("AGENTS.md") not in files:
                fail(errors, f"AGENTS.md missing from payload {selected}")
            skills = {path.parent.name for path in (target / ".agents/skills").glob("*/SKILL.md")}
            if skills != EXPECTED_SKILLS:
                fail(errors, f"skill payload mismatch for {selected}: {sorted(skills)}")
            if any(path.parts[0] in {"scripts", "tooling", "tests", "docs"} for path in files):
                fail(errors, f"developer/runtime files leaked into repository payload for {selected}")
            if selected == ("codex",):
                extras = {p for p in files if p != Path("AGENTS.md") and ".agents" not in p.parts}
                if extras:
                    fail(errors, f"Codex payload should need no adapter files: {sorted(map(str, extras))}")


def validate_json(errors: list[str]) -> None:
    for path in (ROOT / "tooling/templates").rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(errors, f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def validate_links(errors: list[str]) -> None:
    for path in (ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))):
        text = path.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(text):
            target = raw.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).resolve().exists():
                fail(errors, f"broken link {path.relative_to(ROOT)} -> {target}")


def main() -> int:
    errors: list[str] = []
    validate_skills(errors)
    validate_layout(errors)
    validate_versions(errors)
    validate_python(errors)
    validate_json(errors)
    validate_payloads(errors)
    validate_links(errors)
    if errors:
        print("PACKAGE VALIDATION: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"PACKAGE VALIDATION: PASS ({len(EXPECTED_SKILLS)} workflow/discipline skills; no knowledge-pack legacy)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
