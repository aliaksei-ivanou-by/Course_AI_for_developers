#!/usr/bin/env python3
"""Focused tests for session discovery, reflection parsing, and learned skills."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import embacc_reflect as reflect  # noqa: E402


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="embacc-reflect-") as td:
        base = Path(td)
        repo = base / "repo"
        repo.mkdir()

        claude = base / "claude.jsonl"
        claude.write_text(
            "\n".join([
                json.dumps({"type": "user", "message": {"role": "user", "content": "Please fix it"}}),
                json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Fixed"}]}}),
            ]) + "\n",
            encoding="utf-8",
        )
        turns = reflect.extract_claude_transcript(claude)
        expect([t["text"] for t in turns] == ["Please fix it", "Fixed"], "Claude transcript extraction failed", failures)

        # Pi: verify header-based discovery in the default tree and the exact
        # custom session-dir used by embacc. This is the regression that used
        # to make `reflect` miss Pi sessions created through `embacc run`.
        pi_home = base / "home"
        default_pi = pi_home / ".pi" / "agent" / "sessions" / "whatever" / "default.jsonl"
        default_pi.parent.mkdir(parents=True)
        default_pi.write_text(
            json.dumps({"type": "session", "version": 3, "cwd": str(repo)}) + "\n" +
            json.dumps({"type": "message", "message": {"role": "user", "content": [{"type": "text", "text": "Pi default"}]}}) + "\n",
            encoding="utf-8",
        )
        private_pi_dir = base / "state" / "state" / "pi-sessions"
        private_pi_dir.mkdir(parents=True)
        private_pi = private_pi_dir / "private.jsonl"
        private_pi.write_text(
            json.dumps({"type": "session", "version": 3, "cwd": str(repo)}) + "\n" +
            json.dumps({"type": "message", "message": {"role": "assistant", "content": [{"type": "text", "text": "Pi private"}]}}) + "\n",
            encoding="utf-8",
        )
        other_pi = private_pi_dir / "other.jsonl"
        other_pi.write_text(json.dumps({"type": "session", "version": 3, "cwd": str(base / "other")}) + "\n", encoding="utf-8")
        found_pi = reflect.find_pi_sessions(repo, home=pi_home, extra_dirs=[private_pi_dir])
        expect(set(found_pi) == {default_pi, private_pi}, f"Pi session lookup failed: {found_pi}", failures)
        expect(reflect.extract_pi_transcript(private_pi)[0]["text"] == "Pi private", "Pi transcript extraction failed", failures)

        codex_home = base / "codex"
        session = codex_home / "sessions" / "2026" / "09" / "s.jsonl"
        session.parent.mkdir(parents=True)
        session.write_text(
            json.dumps({"type": "session_meta", "payload": {"cwd": str(repo)}}) + "\n" +
            json.dumps({"type": "response_item", "payload": {"role": "user", "content": [{"type": "input_text", "text": "Codex user"}]}}) + "\n" +
            json.dumps({"type": "response_item", "payload": {"role": "assistant", "content": [{"type": "output_text", "text": "Codex answer"}]}}) + "\n",
            encoding="utf-8",
        )
        old_codex_home = os.environ.get("CODEX_HOME")
        os.environ["CODEX_HOME"] = str(codex_home)
        try:
            found = reflect.find_codex_sessions(repo)
        finally:
            if old_codex_home is None:
                os.environ.pop("CODEX_HOME", None)
            else:
                os.environ["CODEX_HOME"] = old_codex_home
        expect(found == [session], f"Codex session lookup failed: {found}", failures)
        codex_turns = reflect.extract_codex_transcript(session)
        expect(
            [turn["text"] for turn in codex_turns] == ["Codex user", "Codex answer"],
            f"Codex input_text/output_text extraction failed: {codex_turns}", failures,
        )

        export = "Exporting session: ses_123\n" + json.dumps({
            "info": {"time": {"updated": 1_700_000_000_000}},
            "messages": [{"info": {"role": "user"}, "parts": [{"type": "text", "text": "OpenCode user"}]}],
        })
        opencode_turns, updated = reflect.parse_opencode_export(export)
        expect(opencode_turns and opencode_turns[0]["text"] == "OpenCode user", "OpenCode export parsing failed", failures)
        expect(updated == 1_700_000_000, "OpenCode updated timestamp conversion failed", failures)

        digest, truncated = reflect.build_digest([("long", "x" * 100)], max_chars=20)
        expect(truncated and digest, "oversized first session produced an empty digest", failures)

        skill_description = "Reproduce first: capture evidence before changing code"
        # Mimic the exact malformed-YAML class that broke Pi in 2.7.0.
        # Embacc must rebuild safe frontmatter from structured metadata.
        skill_content = f"""---\nname: reproduce-first\ndescription: {skill_description}\n---\n\n# Reproduce first\n\n1. Capture the failing behavior.\n2. Minimize the reproduction.\n3. Change code only after the failure is observable.\n"""
        model_output = "model banner\n" + json.dumps({
            "summary": "The developer repeatedly asks for evidence before edits.",
            "rules": ["Reproduce defects before changing code."],
            "skills": [{
                "name": "reproduce-first",
                "description": skill_description,
                "content": skill_content,
            }],
            "friction_points": ["Changes were proposed before reproduction."],
        })
        parsed = reflect.parse_reflect_response(model_output)
        expect(parsed["valid"], "valid reflection JSON was rejected", failures)
        expect(parsed["summary"].startswith("The developer"), "reflect summary parsing failed", failures)
        expect(parsed["rules"] == ["Reproduce defects before changing code."], "reflect rule parsing failed", failures)
        expect(parsed["skills"][0]["name"] == "reproduce-first", "reflect skill parsing failed", failures)

        state = base / "project-state"
        saved = reflect.save_generated_skills(state, parsed["skills"])
        skill_path = state / "agent-config" / "skills" / "reproduce-first" / "SKILL.md"
        expect(saved[0]["status"] == "saved" and skill_path.is_file(), f"generated skill was not saved: {saved}", failures)
        saved_text = skill_path.read_text(encoding="utf-8")
        expect(f'description: {json.dumps(skill_description)}' in saved_text, "learned skill description was not safely quoted", failures)
        expect("# Reproduce first" in saved_text, "learned skill body changed during frontmatter normalization", failures)

        unchanged = reflect.save_generated_skills(state, parsed["skills"])
        expect(unchanged[0]["status"] == "unchanged", "identical learned skill should be idempotent", failures)
        conflicting = [dict(parsed["skills"][0], content=skill_content.replace("# Reproduce first", "# Changed"))]
        conflict = reflect.save_generated_skills(state, conflicting)
        expect(conflict[0]["status"] == "conflict", "existing learned skill was not protected", failures)
        expect("# Reproduce first" in skill_path.read_text(encoding="utf-8"), "conflict overwrote existing learned skill", failures)

        reserved_skill = {
            "name": "feature",
            "description": "Bad collision",
            "content": "---\nname: feature\ndescription: Bad collision\n---\n\n# Collision\n",
        }
        reserved = reflect.save_generated_skills(state, [reserved_skill], reserved_names={"feature", "bug"})
        expect(reserved[0]["status"] == "rejected", "learned skill must not shadow a built-in workflow", failures)

        report = reflect.write_reflection_report(
            state, agent="pi", sessions=[("Pi session abc", 1.0, "digest")], reflection=parsed, skill_results=saved,
        )
        expect(report.is_file() and "reproduce-first" in report.read_text(encoding="utf-8"), "reflection report was not written", failures)
        terminal = reflect.format_terminal_report(
            agent="pi", sessions=[("Pi session abc", 1.0, "digest")], reflection=parsed, skill_results=saved, report_path=report,
        )
        expect("EMBACC SESSION RETROSPECTIVE" in terminal and "LEARNED SKILLS" in terminal and "reproduce-first" in terminal and "SAVED REPORT" in terminal and report.name in terminal, "structured reflect output is incomplete", failures)

        # Malformed model output must fail closed: no invented rules/skills.
        malformed = reflect.parse_reflect_response("not json at all")
        expect(not malformed["valid"] and not malformed["rules"] and not malformed["skills"], "malformed reflection did not fail closed", failures)

        self_reflect_turns = [{"role": "user", "text": reflect.REFLECT_MARKER + " internal analysis"}]
        expect(reflect.is_reflection_session(self_reflect_turns), "reflection feedback-loop marker was not detected", failures)

        # No history must remain a free no-op and must not invoke an agent.
        empty_repo = base / "empty-repo"
        empty_repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=empty_repo, check=True)
        env = {
            **os.environ,
            "HOME": str(base / "empty-home"),
            "ACCELERATOR_HOME": str(base / "embacc-home"),
            "CODEX_HOME": str(base / "empty-codex"),
            "PI_CODING_AGENT_SESSION_DIR": str(base / "empty-pi"),
        }
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/embacc_native.py"), "reflect", str(empty_repo), "--yes"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )
        expect(result.returncode == 0, f"reflect no-history path failed: {result.stderr}", failures)
        expect("No project session history found" in result.stdout, "reflect no-history path did not stop cleanly", failures)

    if failures:
        print("REFLECT TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("REFLECT TEST: PASS (Pi custom history + one-call skill parsing + hidden persistence + conflict safety)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
