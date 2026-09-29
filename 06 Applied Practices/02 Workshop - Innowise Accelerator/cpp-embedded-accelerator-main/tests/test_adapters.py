#!/usr/bin/env python3
"""Focused tests for native agent launch-plan generation."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import embacc_adapters as adapters  # noqa: E402
import embacc_resources as resources  # noqa: E402


def snapshot(root: Path) -> set[Path]:
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file()}


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="embacc-adapters-") as td:
        base = Path(td)
        repo = base / "repo"
        repo.mkdir()
        (repo / "client.cpp").write_text("int main(){}\n", encoding="utf-8")
        state = base / "state"
        state.mkdir()
        project_md = state / "PROJECT.md"
        project_md.write_text("# Project\nUse CMake.\n", encoding="utf-8")
        core = base / "core"
        resources.materialize_core_skills(ROOT, core)
        learned = state / "agent-config" / "skills" / "learned-loop"
        learned.mkdir(parents=True)
        (learned / "SKILL.md").write_text(
            '---\nname: learned-loop\ndescription: "Reuse a learned project loop"\n---\n\n# Learned loop\n',
            encoding="utf-8",
        )
        before = snapshot(repo)

        old_codex_home = os.environ.get("CODEX_HOME")
        old_codex_skills = os.environ.get(adapters.CODEX_SKILLS_ROOT_ENV)
        os.environ["CODEX_HOME"] = str(base / "codex-home")
        os.environ[adapters.CODEX_SKILLS_ROOT_ENV] = str(base / "user-home" / ".agents" / "skills")
        try:
            claude = adapters.build_launch_plan(
                "claude", "claude", repo_root=repo, state_dir=state, project_id="abc",
                project_md=project_md, core_dir=core, guard_git=True,
            )
            expect("--append-system-prompt-file" in claude.argv, "Claude did not receive PROJECT.md", failures)
            expect(claude.argv.count("--plugin-dir") == 1, "Claude did not receive its merged skill plugin", failures)
            plugin_dir = Path(claude.argv[claude.argv.index("--plugin-dir") + 1])
            expect((plugin_dir / "skills" / "feature" / "SKILL.md").is_file(), "Claude workflow skill missing from merged plugin", failures)
            expect((plugin_dir / "skills" / "learned-loop" / "SKILL.md").is_file(), "Claude learned skill missing from merged plugin", failures)
            claude_manifest = plugin_dir / ".claude-plugin" / "plugin.json"
            expect(claude_manifest.is_file(), "Claude plugin manifest missing", failures)
            if claude_manifest.is_file():
                manifest_data = json.loads(claude_manifest.read_text(encoding="utf-8"))
                expect(manifest_data.get("name") == "embacc", "Claude plugin manifest has wrong name", failures)
                expect(manifest_data.get("version") == resources.PACKAGE_VERSION, "Claude plugin manifest version mismatch", failures)
            expect("--settings" in claude.argv, "Claude git guard settings were not attached", failures)
            if "--settings" in claude.argv:
                claude_settings = Path(claude.argv[claude.argv.index("--settings") + 1])
                try:
                    settings_data = json.loads(claude_settings.read_text(encoding="utf-8"))
                except (OSError, ValueError) as exc:
                    failures.append(f"Claude generated settings are invalid JSON: {exc}")
                    settings_data = {}
                pre_tool = settings_data.get("hooks", {}).get("PreToolUse", [])
                expect(len(pre_tool) == 1, "Claude git guard must install one PreToolUse handler", failures)
                if pre_tool:
                    expect(pre_tool[0].get("matcher") == "Bash", "Claude git guard matcher is not Bash", failures)
                    handlers = pre_tool[0].get("hooks", [])
                    expect(len(handlers) == 1 and handlers[0].get("type") == "command", "Claude git guard command hook shape is invalid", failures)
            # Self-serve skill authorship. Live-fire tested three approaches
            # before landing here (see embacc_adapters.py comment): a scoped
            # `permissions.allow` Edit() rule, and `permissions.additionalDirectories`
            # (both in settings.json), neither actually granted the write in
            # practice. `--add-dir` + `--permission-mode acceptEdits` (CLI
            # flags) is the one confirmed, live, to work -- and only once the
            # target directory already exists on disk (also live-fire
            # confirmed: identical launch failed against a not-yet-created
            # directory), hence the eager mkdir assertion below.
            learned_skills_dir = state / "agent-config" / "skills"
            expect("--add-dir" in claude.argv, f"Claude launch does not grant access to the learned-skills directory: {claude.argv}", failures)
            if "--add-dir" in claude.argv:
                add_dir_value = claude.argv[claude.argv.index("--add-dir") + 1]
                expect(add_dir_value == str(learned_skills_dir), f"Claude --add-dir targets the wrong directory: {add_dir_value}", failures)
                expect(not add_dir_value.startswith("//"), f"--add-dir must not use the //-prefixed form Claude Code parses as a UNC network path: {add_dir_value}", failures)
            expect(learned_skills_dir.is_dir(), "Claude launch plan must eagerly create the learned-skills directory so --add-dir has something to grant on the very first launch", failures)
            expect(
                claude.argv[-2:] == ["--permission-mode", "acceptEdits"],
                f"Claude launch does not auto-accept edits for self-serve skill authorship: {claude.argv}", failures,
            )
            if "--plugin-dir" in claude.argv:
                plugin_skill_files = sorted((plugin_dir / "skills").glob("*/SKILL.md"))
                expect(len(plugin_skill_files) == len(resources.canonical_skill_names(ROOT)) + 1, "Claude external plugin has the wrong skill count", failures)
                for skill_file in plugin_skill_files:
                    try:
                        resources.skill_metadata(skill_file)
                    except resources.ResourceError as exc:
                        failures.append(f"Claude plugin contains invalid skill frontmatter: {exc}")

            claude_mcp = adapters.build_launch_plan(
                "claude", "claude", repo_root=repo, state_dir=state, project_id="mcp",
                project_md=project_md, core_dir=core, guard_git=True,
                mcp_servers={"example": {"command": "example-mcp", "args": ["--stdio"]}},
            )
            expect("--mcp-config" in claude_mcp.argv, "Claude MCP config flag missing", failures)

            # The main `state` dir above already has agent-config/skills from
            # the learned-loop fixture, so it never actually exercises eager
            # creation on a brand-new project. A completely fresh state dir
            # does: the very first `embacc run claude` on a new project must
            # not be the one launch where --add-dir silently grants nothing.
            never_setup_state = base / "never-setup-state"
            never_setup_state.mkdir()
            expect(not (never_setup_state / "agent-config" / "skills").exists(), "test setup invariant broken: agent-config/skills must not pre-exist here", failures)
            claude_first_launch = adapters.build_launch_plan(
                "claude", "claude", repo_root=repo, state_dir=never_setup_state, project_id="first-launch",
                project_md=None, core_dir=core, guard_git=False,
            )
            expect((never_setup_state / "agent-config" / "skills").is_dir(), "Claude's very first launch for a project must eagerly create agent-config/skills, not defer to the first skill write", failures)
            expect("--add-dir" in claude_first_launch.argv, "Claude's very first launch must still grant --add-dir even with no prior skill activity", failures)
            if "--mcp-config" in claude_mcp.argv:
                mcp_path = Path(claude_mcp.argv[claude_mcp.argv.index("--mcp-config") + 1])
                try:
                    mcp_data = json.loads(mcp_path.read_text(encoding="utf-8"))
                except (OSError, ValueError) as exc:
                    failures.append(f"Claude MCP config is invalid JSON: {exc}")
                    mcp_data = {}
                expect(mcp_data.get("mcpServers", {}).get("example", {}).get("command") == "example-mcp", "Claude MCP config content is wrong", failures)

            codex = adapters.build_launch_plan(
                "codex", "codex", repo_root=repo, state_dir=state, project_id="abc",
                project_md=project_md, core_dir=core,
            )
            expect(codex.argv[:3] == ["codex", "--profile", "embacc-abc"], "Codex profile argv is wrong", failures)
            profile = base / "codex-home" / "embacc-abc.config.toml"
            expect(profile.is_file(), "Codex external profile was not written", failures)
            profile_text = profile.read_text(encoding="utf-8") if profile.is_file() else ""
            expect("developer_instructions = " in profile_text, "Codex profile does not use developer_instructions", failures)
            expect("\ninstructions = " not in "\n" + profile_text, "Codex profile still uses reserved instructions key", failures)
            try:
                parsed_profile = tomllib.loads(profile_text)
            except tomllib.TOMLDecodeError as exc:
                failures.append(f"Codex profile is invalid TOML: {exc}")
                parsed_profile = {}
            expect(parsed_profile.get("developer_instructions", "").startswith("# Project"), "Codex developer_instructions did not survive TOML parsing", failures)
            # Self-serve skill authorship, matching Claude's grant: an extra
            # writable root scoped to this project's hidden learned-skills
            # directory, not a repository-wide sandbox change. Live-fire
            # confirmed `writable_roots` alone (without `sandbox_mode`) was
            # not sufficient for an unattended `codex exec` launch.
            expect(parsed_profile.get("sandbox_mode") == "workspace-write", "Codex profile did not set workspace-write for self-serve skill authorship", failures)
            writable_roots = parsed_profile.get("sandbox_workspace_write", {}).get("writable_roots", [])
            expect(writable_roots == [str(state / "agent-config" / "skills")], f"Codex profile writable_roots is wrong: {writable_roots}", failures)
            expect("# Project" in profile_text and "Use CMake." in profile_text, "Codex PROJECT.md context missing from profile", failures)
            expect("Private learned workflow: learned-loop" in profile_text, "Codex project-private learned skill was not injected into project profile", failures)

            codex_user_skills = base / "user-home" / ".agents" / "skills"
            mirrored = {p.parent.name for p in codex_user_skills.glob("embacc-*/SKILL.md")}
            expected_mirrors = {f"embacc-{name}" for name in resources.canonical_skill_names(ROOT)}
            expect(mirrored == expected_mirrors, f"Codex canonical skill mirror mismatch: {sorted(mirrored)}", failures)
            feature_mirror = codex_user_skills / "embacc-feature"
            expect((feature_mirror / "SKILL.md").is_file(), "Codex feature skill mirror missing", failures)
            marker = feature_mirror / adapters.CODEX_MANAGED_MARKER
            expect(marker.is_file(), "Codex managed skill marker missing", failures)
            expect(not (codex_user_skills / "embacc-learned-loop").exists(), "project-private learned skill leaked into Codex global USER skills", failures)
            expect(any("Codex canonical skills:" in note for note in codex.notes), "Codex did not report managed skill visibility", failures)

            # Pre-namespacing sync left bare-named directories (`bug/`, not
            # `embacc-bug/`) tracked by a single `.embacc-manifest.json`
            # instead of a per-directory marker. An in-place upgrade must
            # reap those -- otherwise Codex shows both the legacy and the
            # namespaced mirror for the same skill name with two different
            # descriptions.
            legacy_manifest_path = codex_user_skills / adapters.LEGACY_CODEX_SKILLS_MANIFEST
            legacy_bug = codex_user_skills / "bug"
            legacy_bug.mkdir(parents=True)
            (legacy_bug / "SKILL.md").write_text("---\nname: bug\ndescription: legacy\n---\n", encoding="utf-8")
            legacy_foreign = codex_user_skills / "my-own-skill"
            legacy_foreign.mkdir(parents=True)
            (legacy_foreign / "SKILL.md").write_text("---\nname: my-own-skill\ndescription: mine\n---\n", encoding="utf-8")
            legacy_manifest_path.write_text(
                json.dumps({"managed": {
                    "bug": {"source": "old", "owner": adapters.LEGACY_CODEX_CANONICAL_OWNER},
                    "my-own-skill": {"source": "old", "owner": "some-other-project-id"},
                }}),
                encoding="utf-8",
            )
            codex_reap = adapters.build_launch_plan(
                "codex", "codex", repo_root=repo, state_dir=state, project_id="abc",
                project_md=project_md, core_dir=core,
            )
            expect(not legacy_bug.exists(), "legacy bare-named Codex skill mirror was not reaped", failures)
            expect(legacy_foreign.exists(), "reap removed a non-canonical-owned legacy entry it must not touch", failures)
            expect(
                json.loads(legacy_manifest_path.read_text(encoding="utf-8"))["managed"].get("my-own-skill", {}).get("owner")
                == "some-other-project-id",
                "reap corrupted the legacy manifest's remaining foreign entry", failures,
            )
            expect(any("legacy Codex skill mirror" in note and "bug" in note for note in codex_reap.notes), "legacy skill reap was not reported", failures)

            status = adapters.codex_integration_status(
                "abc", resources.canonical_skill_names(ROOT), repo_root=repo
            )
            expect(len(status["effective"]) == len(resources.canonical_skill_names(ROOT)), "Codex integration status cannot see effective mirrored skills", failures)
            expect(len(status["active_user"]) == len(resources.canonical_skill_names(ROOT)), "Codex clean repo should use USER mirrors", failures)
            expect(not status["repo_visible"] and not status["suppressed"], "Codex clean repo unexpectedly suppressed USER skills", failures)
            expect(status["profile_exists"] and status["developer_instructions"], "Codex integration status cannot verify project context profile", failures)

            # A repository that already exposes canonical `.agents/skills` must not
            # show duplicate same-name USER mirrors in Codex. Keep USER mirrors for
            # other repositories and disable them only in this project's profile.
            repo_local = base / "repo-local"
            repo_local.mkdir()
            resources.materialize_resources(ROOT, repo_local, ("codex",))
            local_state = base / "repo-local-state"
            local_state.mkdir()
            local_project_md = local_state / "PROJECT.md"
            local_project_md.write_text("# Local project\n", encoding="utf-8")
            codex_local = adapters.build_launch_plan(
                "codex", "codex", repo_root=repo_local, state_dir=local_state, project_id="repo-local",
                project_md=local_project_md, core_dir=core,
            )
            local_profile = base / "codex-home" / "embacc-repo-local.config.toml"
            local_profile_data = tomllib.loads(local_profile.read_text(encoding="utf-8"))
            skill_overrides = local_profile_data.get("skills", {}).get("config", [])
            expect(len(skill_overrides) == len(resources.canonical_skill_names(ROOT)), "Codex did not suppress all duplicate USER workflows", failures)
            for entry in skill_overrides:
                path = Path(entry.get("path", ""))
                expect(entry.get("enabled") is False, f"Codex duplicate override is not disabled: {entry!r}", failures)
                expect(path.name == "SKILL.md", f"Codex duplicate override must target SKILL.md: {path}", failures)
                expect(path.parent.name.startswith(adapters.CODEX_MANAGED_PREFIX), f"Codex duplicate override should target a managed skill: {path}", failures)
                expect(path.is_file(), f"Codex skills.config path does not exist: {path}", failures)
            expect(any("17 duplicate USER" in note for note in codex_local.notes), "Codex duplicate suppression was not reported", failures)
            local_status = adapters.codex_integration_status(
                "repo-local", resources.canonical_skill_names(ROOT), repo_root=repo_local
            )
            expect(len(local_status["repo_visible"]) == len(resources.canonical_skill_names(ROOT)), "Codex repo-local workflows were not detected", failures)
            expect(len(local_status["suppressed"]) == len(resources.canonical_skill_names(ROOT)), "Codex USER duplicates were not reported as suppressed", failures)
            expect(not local_status["active_user"], "Codex duplicate USER workflows remain active", failures)
            expect(len(local_status["effective"]) == len(resources.canonical_skill_names(ROOT)), "Codex effective workflow set is wrong after deduplication", failures)

            # Exact regression for a fresh accelerator checkout opened before
            # `embacc setup`: USER mirrors may already exist from an earlier run,
            # while this repository exposes the same canonical `.agents/skills`.
            # Dedup must still be generated even though no core/project context is
            # active for this launch.
            repo_fresh = base / "repo-fresh-no-setup"
            repo_fresh.mkdir()
            resources.materialize_resources(ROOT, repo_fresh, ("codex",))
            fresh_state = base / "repo-fresh-no-setup-state"
            fresh_state.mkdir()
            codex_fresh = adapters.build_launch_plan(
                "codex", "codex", repo_root=repo_fresh, state_dir=fresh_state,
                project_id="repo-fresh-no-setup", project_md=None, core_dir=None,
            )
            fresh_profile = base / "codex-home" / "embacc-repo-fresh-no-setup.config.toml"
            fresh_profile_data = tomllib.loads(fresh_profile.read_text(encoding="utf-8"))
            fresh_overrides = fresh_profile_data.get("skills", {}).get("config", [])
            expect(
                len(fresh_overrides) == len(resources.canonical_skill_names(ROOT)),
                "Codex fresh/no-setup launch did not suppress stale USER duplicates", failures,
            )
            expect(
                all(entry.get("enabled") is False for entry in fresh_overrides),
                "Codex fresh/no-setup duplicate overrides are not disabled", failures,
            )
            expect(
                any("duplicate protection" in note.lower() for note in codex_fresh.notes),
                "Codex fresh/no-setup launch did not report duplicate protection", failures,
            )
            fresh_status = adapters.codex_integration_status(
                "repo-fresh-no-setup", resources.canonical_skill_names(ROOT), repo_root=repo_fresh
            )
            expect(
                len(fresh_status["suppressed"]) == len(resources.canonical_skill_names(ROOT))
                and not fresh_status["active_user"]
                and len(fresh_status["effective"]) == len(resources.canonical_skill_names(ROOT)),
                "Codex fresh/no-setup effective skill set still contains duplicate USER workflows", failures,
            )

            # Never overwrite a user-owned directory even if it uses our namespace.
            shutil.rmtree(feature_mirror)
            feature_mirror.mkdir(parents=True)
            sentinel = feature_mirror / "USER_OWNED.txt"
            sentinel.write_text("keep me\n", encoding="utf-8")
            codex_collision = adapters.build_launch_plan(
                "codex", "codex", repo_root=repo, state_dir=state, project_id="abc",
                project_md=project_md, core_dir=core,
            )
            expect(sentinel.read_text(encoding="utf-8") == "keep me\n", "Codex mirror overwrote an unowned user directory", failures)
            expect(not (feature_mirror / adapters.CODEX_MANAGED_MARKER).exists(), "Codex mirror claimed ownership of an unowned directory", failures)
            expect(any("collision" in note.lower() and "feature" in note for note in codex_collision.notes), "Codex mirror collision was not reported", failures)

            # Claude repo-local adapters and the external plugin must not expose
            # the same canonical workflow twice. Only project-private learned
            # skills belong in the external plugin in this case.
            repo_claude = base / "repo-claude"
            repo_claude.mkdir()
            resources.materialize_resources(ROOT, repo_claude, ("claude",))
            claude_state = base / "claude-state"
            claude_state.mkdir()
            claude_project_md = claude_state / "PROJECT.md"
            claude_project_md.write_text("# Claude project\n", encoding="utf-8")
            claude_learned = claude_state / "agent-config" / "skills" / "learned-loop"
            claude_learned.mkdir(parents=True)
            shutil.copy2(learned / "SKILL.md", claude_learned / "SKILL.md")
            claude_materialized = adapters.build_launch_plan(
                "claude", "claude", repo_root=repo_claude, state_dir=claude_state, project_id="claude-local",
                project_md=claude_project_md, core_dir=core, guard_git=True,
            )
            expect(claude_materialized.argv.count("--plugin-dir") == 1, "Claude learned-skill plugin missing for materialized repo", failures)
            if "--plugin-dir" in claude_materialized.argv:
                local_plugin = Path(claude_materialized.argv[claude_materialized.argv.index("--plugin-dir") + 1])
                local_plugin_skills = {p.parent.name for p in (local_plugin / "skills").glob("*/SKILL.md")}
                expect(local_plugin_skills == {"learned-loop"}, f"Claude external plugin duplicated repository workflows: {sorted(local_plugin_skills)}", failures)
                local_manifest = local_plugin / ".claude-plugin" / "plugin.json"
                expect(local_manifest.is_file(), "Claude materialized-repo plugin manifest missing", failures)
            expect("--append-system-prompt-file" in claude_materialized.argv, "Claude materialized repo lost PROJECT.md context", failures)
            expect("--settings" in claude_materialized.argv, "Claude materialized repo lost git guard settings", failures)

            opencode = adapters.build_launch_plan(
                "opencode", "opencode", repo_root=repo, state_dir=state, project_id="abc",
                project_md=project_md, core_dir=core,
            )
            expect(opencode.env.get("OPENCODE_CONFIG_DIR"), "OpenCode config directory env missing", failures)
            config_dir = Path(opencode.env["OPENCODE_CONFIG_DIR"])
            expect((config_dir / "opencode.json").is_file(), "OpenCode external config missing", failures)
            opencode_config = json.loads((config_dir / "opencode.json").read_text(encoding="utf-8"))
            expect(str(core / ".agents" / "skills") in opencode_config.get("skills", []), "OpenCode canonical skill source missing", failures)
            expect(str(state / "agent-config" / "skills") in opencode_config.get("skills", []), "OpenCode learned skill source missing", failures)
            expect(not (config_dir / "skill").exists(), "OpenCode unnecessarily copied skill files", failures)
            opencode_model = adapters.build_launch_plan(
                "opencode", "opencode", repo_root=repo, state_dir=state, project_id="model",
                project_md=project_md, core_dir=core, model="provider/model",
            )
            expect(opencode_model.argv.count("--model") == 1, "OpenCode interactive plan duplicated --model", failures)

            pi = adapters.build_launch_plan(
                "pi", "pi", repo_root=repo, state_dir=state, project_id="abc",
                project_md=project_md, core_dir=core,
            )
            expect(pi.argv.count("--skill") == 2, "Pi did not receive canonical + learned skill roots", failures)
            pi_skill_paths = [pi.argv[i + 1] for i, arg in enumerate(pi.argv[:-1]) if arg == "--skill"]
            expect(str(state / "agent-config" / "skills") in pi_skill_paths, "Pi learned skill root missing", failures)
            expect("--session-dir" in pi.argv, "Pi external session directory missing", failures)

            for agent in adapters.AGENTS:
                plan = adapters.build_launch_plan(
                    agent, agent, repo_root=repo, state_dir=state, project_id="stdin",
                    project_md=project_md, stdin_task=True,
                )
                expect(all("TRANSCRIPT" not in arg for arg in plan.argv), f"{agent} embedded stdin task into argv", failures)
        finally:
            if old_codex_home is None:
                os.environ.pop("CODEX_HOME", None)
            else:
                os.environ["CODEX_HOME"] = old_codex_home
            if old_codex_skills is None:
                os.environ.pop(adapters.CODEX_SKILLS_ROOT_ENV, None)
            else:
                os.environ[adapters.CODEX_SKILLS_ROOT_ENV] = old_codex_skills

        expect(snapshot(repo) == before, "adapter plan generation wrote into the client repository", failures)

    if failures:
        print("ADAPTER TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("ADAPTER TEST: PASS (Codex dedup + project context; Claude plugin structure/dedup; OpenCode/Pi plans)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
