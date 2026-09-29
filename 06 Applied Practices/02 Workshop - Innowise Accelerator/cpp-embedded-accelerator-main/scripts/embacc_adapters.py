#!/usr/bin/env python3
"""Build native launch plans for Claude Code, Codex, OpenCode, and Pi."""

from __future__ import annotations

import dataclasses
import json
import os
import re
import shutil
import sys
import tomllib
from pathlib import Path
from typing import Any

import embacc_resources as resources

AGENTS = ("claude", "codex", "opencode", "pi")
CODEX_MANAGED_MARKER = ".embacc-managed.json"
CODEX_MANAGED_PREFIX = "embacc-"
CODEX_LEARNED_CONTEXT_LIMIT = 40_000
CODEX_SKILLS_ROOT_ENV = "EMBACC_CODEX_SKILLS_ROOT"

# Pre-namespacing Codex sync (before the `embacc-` prefix + per-directory
# CODEX_MANAGED_MARKER existed): a single manifest keyed by bare skill name,
# with this owner tag for every skill embacc itself wrote.
LEGACY_CODEX_SKILLS_MANIFEST = ".embacc-manifest.json"
LEGACY_CODEX_CANONICAL_OWNER = "__canonical__"


@dataclasses.dataclass(frozen=True)
class LaunchPlan:
    argv: list[str]
    env: dict[str, str]
    cwd: Path
    config_files: list[Path]
    notes: list[str]


class AdapterError(RuntimeError):
    pass


def _write_json(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def _toml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def gitguard_script_path() -> Path:
    return Path(__file__).resolve().parent / "embacc_gitguard.py"


def _loose_skill_name(path: Path) -> str | None:
    """Read only the frontmatter name from a host skill.

    Repository-owned skills are not required to use Embacc's stricter quoted
    description subset, so duplicate detection deliberately parses only the name.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = resources.FM_RE.match(text)
    if not match:
        return None
    name_match = resources.NAME_RE.search(match.group(1))
    if not name_match:
        return None
    raw = name_match.group(1).strip()
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
            return value.strip() if isinstance(value, str) else None
        except ValueError:
            return None
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1].strip()
    return raw.strip() or None


def _repo_codex_skill_paths(repo_root: Path, expected: set[str]) -> dict[str, Path]:
    """Return canonical names already exposed by this repository to Codex."""
    result: dict[str, Path] = {}
    root = repo_root / ".agents" / "skills"
    if not root.is_dir():
        return result
    for path in sorted(root.glob("*/SKILL.md")):
        name = _loose_skill_name(path)
        if name in expected:
            result.setdefault(name, path)
    return result


def _repo_claude_embacc_skills(repo_root: Path) -> set[str]:
    """Find canonical workflows already exposed by `embacc install --tools claude`."""
    found: set[str] = set()
    root = repo_root / ".claude" / "skills"
    if not root.is_dir():
        return found
    pattern = re.compile(r"Read `\.agents/skills/([^/]+)/SKILL\.md`")
    for path in sorted(root.glob("acc-*/SKILL.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if resources.GENERATED not in text:
            continue
        match = pattern.search(text)
        if match:
            found.add(match.group(1))
    return found


def _build_claude_skill_plugin(
    *, repo_root: Path, state_dir: Path, core_dir: Path | None
) -> Path | None:
    """Build one explicit, valid Claude plugin containing only missing workflows.

    Repository-materialized Embacc adapters take precedence. Project-private learned
    skills are always added here because they intentionally never live in the repo.
    """
    learned = state_dir / "agent-config" / "skills"
    if not core_dir and not learned.is_dir():
        return None

    plugin_root = state_dir / "agent-config" / "claude" / "plugin"
    if plugin_root.exists():
        shutil.rmtree(plugin_root)
    skill_root = plugin_root / "skills"
    skill_root.mkdir(parents=True, exist_ok=True)

    materialized = _repo_claude_embacc_skills(repo_root)
    copied = 0
    if core_dir:
        source_root = core_dir / ".agents" / "skills"
        for entry in sorted(source_root.iterdir()):
            if not entry.is_dir() or not (entry / "SKILL.md").is_file():
                continue
            if entry.name in materialized:
                continue
            shutil.copytree(entry, skill_root / entry.name, dirs_exist_ok=True)
            copied += 1
    if learned.is_dir():
        for entry in sorted(learned.iterdir()):
            if entry.is_dir() and (entry / "SKILL.md").is_file():
                shutil.copytree(entry, skill_root / entry.name, dirs_exist_ok=True)
                copied += 1

    if copied == 0:
        shutil.rmtree(plugin_root, ignore_errors=True)
        return None

    manifest = plugin_root / ".claude-plugin" / "plugin.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(
            {
                "name": "embacc",
                "description": "Embacc workflow skills",
                "version": resources.PACKAGE_VERSION,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return plugin_root


def _claude_plan(
    binary: str,
    *,
    repo_root: Path,
    state_dir: Path,
    project_md: Path | None,
    task: str | None,
    mcp_servers: dict[str, Any] | None,
    model: str | None,
    guard_git: bool,
    stdin_task: bool,
    core_dir: Path | None,
) -> LaunchPlan:
    argv = [binary]
    config_files: list[Path] = []
    notes: list[str] = []
    if model:
        argv += ["--model", model]
    if project_md and project_md.is_file():
        argv += ["--append-system-prompt-file", str(project_md)]
    else:
        notes.append("no PROJECT.md found; run `embacc setup` first")
    if mcp_servers:
        path = _write_json(state_dir / "mcp" / "claude-mcp.json", {"mcpServers": mcp_servers})
        argv += ["--mcp-config", str(path)]
        config_files.append(path)
    plugin_root = _build_claude_skill_plugin(
        repo_root=repo_root, state_dir=state_dir, core_dir=core_dir
    )
    if plugin_root:
        argv += ["--plugin-dir", str(plugin_root)]
        config_files.append(plugin_root)
    settings: dict[str, Any] = {}
    if guard_git:
        command = f'"{sys.executable}" "{gitguard_script_path()}"'
        settings["hooks"] = {
            "PreToolUse": [
                {"matcher": "Bash", "hooks": [{"type": "command", "command": command}]}
            ]
        }
    if settings:
        path = _write_json(state_dir / "agent-config" / "claude" / "settings.json", settings)
        argv += ["--settings", str(path)]
        config_files.append(path)
    # Grants access to this project's hidden learned-skills directory (the
    # exact location the AI restrictions section instructs the agent to
    # write to) so the agent can self-serve skill authorship. Two settings.json
    # approaches were tried first and live-fire tested, each with a real,
    # reproduced discrepancy from documented behavior:
    #   - a directory-scoped `permissions.allow` Edit() rule did NOT suppress
    #     the approval prompt for a launch outside the repo (`claude -p`);
    #   - `permissions.additionalDirectories` with a POSIX-normalized `//c/...`
    #     path is parsed as a UNC network path and refused outright before any
    #     permission logic runs; switching to the raw native path fixed that
    #     parse error, but the grant still silently did not take effect --
    #     the write was still refused as outside the sandbox.
    # `--add-dir` (this CLI flag, not the settings.json field) is the only
    # form confirmed, live, to actually grant the access; `--permission-mode
    # acceptEdits` is the only form confirmed to suppress the resulting
    # approval prompt. Both are session-wide, not scoped to this directory.
    #
    # `--add-dir` silently does nothing for a path that doesn't exist yet on
    # disk (live-fire confirmed: identical launch succeeded once the target
    # already existed, failed with "outside allowed working directories"
    # otherwise) -- and this directory is otherwise created lazily, only
    # when a first skill is actually written there. Create it eagerly here
    # so the very first launch already has the grant, not just the second.
    learned_skills_dir = state_dir / "agent-config" / "skills"
    learned_skills_dir.mkdir(parents=True, exist_ok=True)
    argv += ["--add-dir", str(learned_skills_dir), "--permission-mode", "acceptEdits"]
    if task:
        argv += ["-p", task]
    elif stdin_task:
        argv += ["-p"]
    return LaunchPlan(argv, {}, repo_root, config_files, notes)


def _codex_home() -> Path:
    override = os.environ.get("CODEX_HOME")
    return Path(override).expanduser().resolve() if override else Path.home() / ".codex"


def _codex_user_skills_root() -> Path:
    """Documented Codex USER-scope skill root.

    The environment override exists for isolated tests/managed deployments;
    normal users get the documented ``$HOME/.agents/skills`` location.
    """
    override = os.environ.get(CODEX_SKILLS_ROOT_ENV)
    return Path(override).expanduser().resolve() if override else Path.home() / ".agents" / "skills"


def _reap_legacy_codex_skills(target_root: Path) -> list[str]:
    """Remove bare-named Codex skill mirrors left by the pre-namespacing sync.

    An in-place upgrade from that sync leaves its bare-named directories
    (``bug/``, ``coder/``, ...) on disk forever, since this code only ever
    recognizes its own ``embacc-*`` + CODEX_MANAGED_MARKER convention --
    Codex then shows both the legacy and namespaced mirror for the same
    skill name with two different descriptions. Only entries the legacy
    manifest itself marked LEGACY_CODEX_CANONICAL_OWNER-owned are removed;
    a project-specific or genuinely foreign entry sharing this machine-wide
    directory is left untouched, exactly as the legacy code's own ownership
    model required.
    """
    manifest_path = target_root / LEGACY_CODEX_SKILLS_MANIFEST
    if not manifest_path.is_file():
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    managed = manifest.get("managed")
    if not isinstance(managed, dict):
        return []
    removed: list[str] = []
    for name, entry in list(managed.items()):
        if not isinstance(entry, dict) or entry.get("owner") != LEGACY_CODEX_CANONICAL_OWNER:
            continue
        target = target_root / name
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        removed.append(name)
        del managed[name]
    if removed:
        if managed:
            manifest["managed"] = managed
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        else:
            manifest_path.unlink(missing_ok=True)
    return removed


def _sync_codex_canonical_skills(core_dir: Path) -> tuple[list[Path], list[str]]:
    """Mirror canonical skills into Codex's documented USER skill root.

    Embacc owns only ``embacc-*`` directories containing our marker. Existing
    unowned directories are never overwritten or removed. Directory names are
    namespaced while SKILL.md keeps the canonical skill name shown by Codex.
    """
    source_root = core_dir / ".agents" / "skills"
    target_root = _codex_user_skills_root()
    target_root.mkdir(parents=True, exist_ok=True)
    desired: set[str] = set()
    written: list[Path] = []
    notes: list[str] = []

    reaped = _reap_legacy_codex_skills(target_root)
    if reaped:
        notes.append(
            f"Removed {len(reaped)} legacy Codex skill mirror(s) left by the pre-namespacing sync: "
            + ", ".join(sorted(reaped))
        )

    for source in sorted(source_root.glob("*/SKILL.md")):
        skill_name = source.parent.name
        target_name = f"{CODEX_MANAGED_PREFIX}{skill_name}"
        desired.add(target_name)
        target = target_root / target_name
        marker = target / CODEX_MANAGED_MARKER
        if target.is_symlink():
            notes.append(f"Codex skill mirror collision at {target}; symbolic link left untouched")
            continue
        if target.exists() and not marker.is_file():
            notes.append(
                f"Codex skill mirror collision at {target}; left the unowned directory untouched "
                f"and did not expose built-in skill {skill_name!r} through the user mirror"
            )
            continue
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target / "SKILL.md")
        marker.write_text(
            json.dumps(
                {
                    "owner": "cpp-embedded-accelerator",
                    "version": resources.PACKAGE_VERSION,
                    "skill": skill_name,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(target / "SKILL.md")

    # Remove only stale directories that carry our exact ownership marker.
    for target in target_root.glob(f"{CODEX_MANAGED_PREFIX}*"):
        if target.name in desired or not target.is_dir():
            continue
        marker = target / CODEX_MANAGED_MARKER
        try:
            data = json.loads(marker.read_text(encoding="utf-8")) if marker.is_file() else {}
        except (OSError, ValueError):
            data = {}
        if data.get("owner") == "cpp-embedded-accelerator":
            shutil.rmtree(target)

    return written, notes


def _existing_codex_managed_skills() -> list[Path]:
    """Return valid Embacc-owned USER-scope Codex skill files already on disk.

    This deliberately does not depend on project setup or the current core cache.
    A fresh checkout can still coexist with managed USER mirrors created by an
    earlier Embacc run, and Codex would otherwise show duplicate same-name skills.
    """
    root = _codex_user_skills_root()
    result: list[Path] = []
    if not root.is_dir():
        return result
    for directory in sorted(root.glob(f"{CODEX_MANAGED_PREFIX}*")):
        if directory.is_symlink() or not directory.is_dir():
            continue
        marker = directory / CODEX_MANAGED_MARKER
        skill_md = directory / "SKILL.md"
        if not marker.is_file() or not skill_md.is_file():
            continue
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if data.get("owner") != "cpp-embedded-accelerator":
            continue
        if _loose_skill_name(skill_md):
            result.append(skill_md)
    return result


def _codex_learned_skill_context(state_dir: Path) -> tuple[str, list[str]]:
    """Inline project-private learned workflows into this Codex profile only.

    Direct Codex CLI has documented repository/user/admin/system skill roots,
    but no per-launch arbitrary skill-root flag. Keeping learned skills out of
    the global USER root avoids leaking project-specific procedures to every
    repository.
    """
    root = state_dir / "agent-config" / "skills"
    if not root.is_dir():
        return "", []

    chunks: list[str] = []
    omitted: list[str] = []
    used = 0
    for path in sorted(root.glob("*/SKILL.md")):
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        block = (
            f"\n\n## Private learned workflow: {path.parent.name}\n"
            f"Source: {path}\n\n{content.strip()}"
        )
        if used + len(block) > CODEX_LEARNED_CONTEXT_LIMIT:
            omitted.append(path.parent.name)
            continue
        chunks.append(block)
        used += len(block)
    return "".join(chunks), omitted


def codex_integration_status(
    project_id: str, expected_skills: tuple[str, ...], *, repo_root: Path | None = None
) -> dict[str, Any]:
    """Inspect the effective Embacc skill sources for a Codex launch."""
    root = _codex_user_skills_root()
    user_visible: list[str] = []
    for name in expected_skills:
        directory = root / f"{CODEX_MANAGED_PREFIX}{name}"
        if (directory / "SKILL.md").is_file() and (directory / CODEX_MANAGED_MARKER).is_file():
            user_visible.append(name)

    repo_visible: dict[str, Path] = {}
    if repo_root is not None:
        repo_visible = _repo_codex_skill_paths(repo_root, set(expected_skills))

    profile = _codex_home() / f"embacc-{project_id}.config.toml"
    profile_text = ""
    parsed: dict[str, Any] = {}
    try:
        profile_text = profile.read_text(encoding="utf-8") if profile.is_file() else ""
        parsed = tomllib.loads(profile_text) if profile_text else {}
    except (OSError, tomllib.TOMLDecodeError):
        parsed = {}

    suppressed_paths: set[Path] = set()
    skills_cfg = parsed.get("skills", {}).get("config", []) if isinstance(parsed, dict) else []
    if isinstance(skills_cfg, list):
        for entry in skills_cfg:
            if not isinstance(entry, dict) or entry.get("enabled") is not False:
                continue
            raw = entry.get("path")
            if isinstance(raw, str):
                try:
                    resolved = Path(raw).expanduser().resolve()
                    suppressed_paths.add(resolved)
                    if resolved.name == "SKILL.md":
                        suppressed_paths.add(resolved.parent)
                except OSError:
                    pass

    suppressed: list[str] = []
    active_user: list[str] = []
    for name in user_visible:
        skill_dir = (root / f"{CODEX_MANAGED_PREFIX}{name}").resolve()
        skill_md = (skill_dir / "SKILL.md").resolve()
        if skill_dir in suppressed_paths or skill_md in suppressed_paths:
            suppressed.append(name)
        else:
            active_user.append(name)

    effective = tuple(sorted(set(active_user) | set(repo_visible)))
    return {
        "skills_root": root,
        "user_visible": tuple(user_visible),
        "active_user": tuple(active_user),
        "repo_visible": tuple(sorted(repo_visible)),
        "suppressed": tuple(suppressed),
        "effective": effective,
        "expected": expected_skills,
        "profile": profile,
        "profile_exists": profile.is_file(),
        "developer_instructions": "developer_instructions = " in profile_text,
    }


def _append_codex_duplicate_suppression(
    lines: list[str], *, repo_root: Path, mirrored: list[Path]
) -> tuple[str, ...]:
    """Disable USER mirrors when the repository already exposes the same skill name.

    Codex intentionally lists duplicate same-name skills from REPO and USER scopes.
    The per-profile `skills.config` override lets Embacc keep global workflows for
    ordinary projects while suppressing only the duplicate USER copy in this repo.
    """
    by_name: dict[str, Path] = {}
    for skill_md in mirrored:
        name = _loose_skill_name(skill_md)
        if name:
            by_name[name] = skill_md
    repo_skills = _repo_codex_skill_paths(repo_root, set(by_name))
    suppressed: list[str] = []
    for name in sorted(repo_skills):
        skill_md = by_name.get(name)
        if not skill_md:
            continue
        lines.extend(
            [
                "",
                "[[skills.config]]",
                f"path = {_toml_string(str(skill_md))}",
                "enabled = false",
            ]
        )
        suppressed.append(name)
    return tuple(suppressed)


def _append_codex_writable_skills_root(lines: list[str], state_dir: Path) -> None:
    """Grant Codex write access to exactly this project's hidden learned-
    skills directory -- matching Claude's scoped Edit() permission rule and
    OpenCode's existing `external_directory` allow -- so the agent can
    self-serve skill authorship there without an interactive approval loop.
    Live-confirmed: `sandbox_mode` alone or `writable_roots` alone was not
    enough for an unattended `codex exec` launch; both are required together."""
    learned_skills_dir = state_dir / "agent-config" / "skills"
    lines.append('\nsandbox_mode = "workspace-write"')
    lines.append("\n[sandbox_workspace_write]")
    lines.append(f"writable_roots = [{_toml_string(str(learned_skills_dir))}]")


def _append_mcp_toml(lines: list[str], servers: dict[str, Any]) -> None:
    for name, spec in servers.items():
        lines.append(f"\n[mcp_servers.{name}]")
        nested: list[tuple[str, dict[str, Any]]] = []
        for key, value in spec.items():
            if isinstance(value, dict):
                nested.append((key, value))
            elif isinstance(value, list):
                rendered = "[" + ", ".join(_toml_string(str(item)) for item in value) + "]"
                lines.append(f"{key} = {rendered}")
            elif isinstance(value, bool):
                lines.append(f"{key} = {'true' if value else 'false'}")
            else:
                lines.append(f"{key} = {_toml_string(str(value))}")
        for table, values in nested:
            lines.append(f"\n[mcp_servers.{name}.{table}]")
            for key, value in values.items():
                lines.append(f"{key} = {_toml_string(str(value))}")


def _codex_plan(
    binary: str,
    *,
    repo_root: Path,
    state_dir: Path,
    project_md: Path | None,
    task: str | None,
    mcp_servers: dict[str, Any] | None,
    project_id: str,
    model: str | None,
    stdin_task: bool,
    core_dir: Path | None,
) -> LaunchPlan:
    lines: list[str] = []
    notes: list[str] = []
    developer_parts: list[str] = []
    if project_md and project_md.is_file():
        developer_parts.append(project_md.read_text(encoding="utf-8"))
    else:
        notes.append("no PROJECT.md found; run `embacc setup` first")

    learned_context, omitted_learned = _codex_learned_skill_context(state_dir)
    if learned_context:
        developer_parts.append(
            "Project-private learned workflows follow. Treat them like project-scoped skill instructions "
            "and apply them only when their description matches the current task." + learned_context
        )
    if omitted_learned:
        notes.append(
            "some project-private learned skills were omitted from Codex developer instructions because "
            "the hidden-skill context budget was reached: " + ", ".join(omitted_learned)
        )
    if developer_parts:
        lines.append(f"developer_instructions = {_toml_string(chr(10).join(developer_parts))}")

    mirrored: list[Path] = []
    if core_dir:
        mirrored, mirror_notes = _sync_codex_canonical_skills(core_dir)
        notes.extend(mirror_notes)
    else:
        # Dedup must not depend on `embacc setup`. Managed USER mirrors can remain
        # from another project/version while this repository already exposes the
        # same skills from `.agents/skills`. Codex intentionally lists both.
        mirrored = _existing_codex_managed_skills()

    suppressed = _append_codex_duplicate_suppression(
        lines, repo_root=repo_root, mirrored=mirrored
    )

    if core_dir and mirrored:
        message = (
            f"Codex canonical skills: {len(mirrored)} managed USER skill(s) available under "
            f"{_codex_user_skills_root()}"
        )
        if suppressed:
            message += f"; {len(suppressed)} duplicate USER copy/copies suppressed for this repository"
        notes.append(message)
    elif suppressed:
        notes.append(
            f"Codex duplicate protection: {len(suppressed)} existing managed USER skill copy/copies "
            "suppressed because this repository already exposes the same skill name(s)"
        )

    if mcp_servers:
        _append_mcp_toml(lines, mcp_servers)

    _append_codex_writable_skills_root(lines, state_dir)

    profile_name = f"embacc-{project_id}"
    profile_path = _codex_home() / f"{profile_name}.config.toml"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    config_files: list[Path] = [profile_path]
    argv = [binary, "--profile", profile_name, "-C", str(repo_root)]
    if model:
        argv += ["--model", model]
    if task:
        argv += ["exec", task]
    elif stdin_task:
        argv += ["exec"]
    return LaunchPlan(argv, {}, repo_root, config_files, notes)


def _opencode_plan(
    binary: str,
    *,
    repo_root: Path,
    state_dir: Path,
    project_md: Path | None,
    task: str | None,
    mcp_servers: dict[str, Any] | None,
    model: str | None,
    stdin_task: bool,
    core_dir: Path | None,
) -> LaunchPlan:
    config: dict[str, Any] = {"$schema": "https://opencode.ai/config.json"}
    notes: list[str] = []
    if project_md and project_md.is_file():
        config["instructions"] = [str(project_md)]
    else:
        notes.append("no PROJECT.md found; run `embacc setup` first")
    if mcp_servers:
        config["mcp"] = mcp_servers
    state_pattern = str(state_dir).replace("\\", "/").rstrip("/") + "/**"
    config["permission"] = {"external_directory": {state_pattern: "allow"}}

    config_dir = state_dir / "agent-config" / "opencode"
    skill_sources: list[Path] = []
    if core_dir:
        skill_sources.append(core_dir / ".agents" / "skills")
    learned = state_dir / "agent-config" / "skills"
    if learned.is_dir():
        skill_sources.append(learned)
    if skill_sources:
        config["skills"] = [str(path) for path in skill_sources]
    config_path = _write_json(config_dir / "opencode.json", config)
    config_files = [config_path]

    env = {"OPENCODE_CONFIG_DIR": str(config_dir), "PWD": str(repo_root)}
    if task or stdin_task:
        argv = [binary, "run", "--auto", "--dir", str(repo_root)]
        if model:
            argv += ["--model", model]
        if task:
            argv.append(task)
    else:
        argv = [binary, str(repo_root)]
        if model:
            argv += ["--model", model]
    return LaunchPlan(argv, env, repo_root, config_files, notes)


def _pi_plan(
    binary: str,
    *,
    repo_root: Path,
    state_dir: Path,
    project_md: Path | None,
    task: str | None,
    mcp_servers: dict[str, Any] | None,
    model: str | None,
    stdin_task: bool,
    core_dir: Path | None,
) -> LaunchPlan:
    argv = [binary]
    notes: list[str] = []
    if model:
        argv += ["--model", model]
    if project_md and project_md.is_file():
        argv += ["--append-system-prompt", str(project_md)]
    else:
        notes.append("no PROJECT.md found; run `embacc setup` first")
    if core_dir:
        argv += ["--skill", str(core_dir / ".agents" / "skills")]
    learned = state_dir / "agent-config" / "skills"
    if learned.is_dir():
        argv += ["--skill", str(learned)]
    session_dir = state_dir / "state" / "pi-sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    argv += ["--session-dir", str(session_dir)]
    if mcp_servers:
        notes.append("Pi has no native MCP client; configure integrations with Pi extensions")
    if task:
        argv += ["-p", "--", task]
    elif stdin_task:
        argv += ["-p"]
    return LaunchPlan(argv, {}, repo_root, [], notes)


def build_launch_plan(
    agent: str,
    binary: str,
    *,
    repo_root: Path,
    state_dir: Path,
    project_id: str,
    project_md: Path | None,
    task: str | None = None,
    mcp_servers: dict[str, Any] | None = None,
    model: str | None = None,
    guard_git: bool = False,
    stdin_task: bool = False,
    core_dir: Path | None = None,
) -> LaunchPlan:
    common = dict(
        repo_root=repo_root,
        state_dir=state_dir,
        project_md=project_md,
        task=task,
        mcp_servers=mcp_servers,
        model=model,
        stdin_task=stdin_task,
        core_dir=core_dir,
    )
    if agent == "claude":
        return _claude_plan(binary, guard_git=guard_git, **common)
    if agent == "codex":
        plan = _codex_plan(binary, project_id=project_id, **common)
    elif agent == "opencode":
        plan = _opencode_plan(binary, **common)
    elif agent == "pi":
        plan = _pi_plan(binary, **common)
    else:
        raise AdapterError(f"no native adapter for agent: {agent}")
    if guard_git:
        plan.notes.append(f"git guard is only implemented for Claude; ignored for {agent}")
    return plan
