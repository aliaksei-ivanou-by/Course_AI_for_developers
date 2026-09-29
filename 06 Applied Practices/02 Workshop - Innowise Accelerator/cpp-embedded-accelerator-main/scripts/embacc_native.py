#!/usr/bin/env python3
"""Native external workflow for the C++/Embedded Accelerator.

`setup`, bare `embacc`, `run`, `doctor`, `refresh`, `config`, and `reflect`
keep accelerator-owned project state outside the target repository and hand
context to each agent through that agent's native configuration mechanism.
Workflow orchestration lives in canonical agent skills; this module stays the single
runtime implementation for project operations and hidden state.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import embacc_adapters as adapters  # noqa: E402
import embacc_astgrep as astgrep_mod  # noqa: E402
import embacc_discover as discover_mod  # noqa: E402
import embacc_external as ext  # noqa: E402
import embacc_projectdoc as projectdoc  # noqa: E402
import embacc_reflect as reflect_mod  # noqa: E402
import embacc_resources as resources  # noqa: E402

AGENT_JSON_NAME = "agent.json"
MCP_SERVERS_NAME = "servers.json"


class NativeError(RuntimeError):
    pass


def resolve_repo(target: str) -> Path:
    path = Path(target).resolve()
    if not path.is_dir():
        raise NativeError(f"not a directory: {path}")
    return ext.git_root(path) or path


def discover_agent(explicit: str | None, binary_override: str | None) -> tuple[str, str]:
    """Return ``(agent_name, executable)`` for an explicit or detected agent."""
    if explicit:
        if explicit not in adapters.AGENTS:
            raise NativeError(f"unknown agent: {explicit} (choose one of {', '.join(adapters.AGENTS)})")
        binary = binary_override or shutil.which(explicit)
        if not binary:
            raise NativeError(f"agent CLI not found on PATH: {explicit}")
        return explicit, binary
    for name in adapters.AGENTS:
        binary = shutil.which(name)
        if binary:
            return name, binary
    raise NativeError(
        "no supported agent CLI found on PATH (looked for: " + ", ".join(adapters.AGENTS) + "); "
        "install one or pass --agent with an explicit binary via --agent-binary"
    )


def available_agents() -> dict[str, str | None]:
    return {name: shutil.which(name) for name in adapters.AGENTS}


# Which of a repository's own pre-existing AI files a given agent actually
# reads natively -- live-verified with real marker text against real
# installed binaries (kept here only for customer-config visibility warnings): Codex and OpenCode read AGENTS.md; Claude Code does not
# (its own native file is CLAUDE.md); Pi reads both per its own --help
# (`--no-context-files` disables "AGENTS.md and CLAUDE.md discovery"),
# not independently live-confirmed (no credentials in this environment).
# "Preserved on disk" (every agent, always) is a separate guarantee from
# "read by this agent" -- this table is about the second one only.
AGENT_NATIVE_FILES = {
    "claude": {"CLAUDE.md"},
    "codex": {"AGENTS.md"},
    "opencode": {"AGENTS.md"},
    "pi": {"AGENTS.md", "CLAUDE.md"},
}


def _agent_visibility_warning(discovery: dict, agent: str | None) -> str | None:
    if not agent:
        return None
    existing = {k for k, v in (discovery.get("existing_ai_config") or {}).items() if v}
    present_customer_files = existing & {"AGENTS.md", "CLAUDE.md"}
    if not present_customer_files:
        return None
    natively_read = AGENT_NATIVE_FILES.get(agent, set())
    invisible = present_customer_files - natively_read
    if not invisible:
        return None
    return (
        f"note: this repository's {', '.join(sorted(invisible))} exists and is left untouched, but {agent} "
        f"does not read it natively (only {', '.join(sorted(natively_read)) or 'none of these'}) -- that "
        "customer policy will not automatically reach this agent. See README.md "
        "\"Preserved on disk is not the same as read by every agent.\""
    )


def _print(*args: object) -> None:
    """print(), tolerant of a console codepage (cp1252 on this Windows/
    MINGW64 setup, live-confirmed) that cannot represent a character a real
    transcript or a model's own response legitimately contains (an em-dash,
    an arrow, non-Latin text). Never let a diagnostic/report crash the
    command over what it's reporting."""
    try:
        print(*args)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "ascii"
        print(*(str(a).encode(encoding, errors="replace").decode(encoding) for a in args))


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _agent_state(state_dir: Path) -> dict:
    return _load_json(state_dir / AGENT_JSON_NAME)


def _update_agent_state(state_dir: Path, **changes: object) -> None:
    path = state_dir / AGENT_JSON_NAME
    data = _agent_state(state_dir)
    data.update(changes)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _default_agent(state_dir: Path) -> str | None:
    value = _agent_state(state_dir).get("default_agent")
    return value if isinstance(value, str) else None


def _guard_git_enabled(state_dir: Path) -> bool:
    return bool(_agent_state(state_dir).get("guard_git"))


def _canonical_skills_enabled(state_dir: Path) -> bool:
    return bool(_agent_state(state_dir).get("canonical_skills"))


def _mcp_servers(state_dir: Path) -> dict | None:
    data = _load_json(state_dir / "mcp" / MCP_SERVERS_NAME)
    return data or None


MCP_EXAMPLE = {
    "example": {
        "command": "REPLACE_WITH_VERIFIED_MCP_COMMAND",
        "args": [],
        "env": {"EXAMPLE_TOKEN": "REPLACE_ME"},
    }
}



def _write_mcp_example(state_dir: Path) -> None:
    path = state_dir / "mcp" / "servers.json.example"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(MCP_EXAMPLE, indent=2) + "\n", encoding="utf-8")


LEARNED_RULES_NAME = "learned-rules.json"


def _load_learned_rules(state_dir: Path) -> list[str]:
    data = _load_json(state_dir / "state" / LEARNED_RULES_NAME)
    rules = data.get("rules") if isinstance(data, dict) else None
    return [r for r in rules if isinstance(r, str)] if isinstance(rules, list) else []


def _append_learned_rule(state_dir: Path, rule: str) -> None:
    path = state_dir / "state" / LEARNED_RULES_NAME
    rules = _load_learned_rules(state_dir)
    if rule not in rules:
        rules.append(rule)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"rules": rules}, indent=2) + "\n", encoding="utf-8")


def _confirm(prompt: str, *, default_no: bool = True) -> bool:
    if not sys.stdin.isatty():
        return False
    suffix = "[y/N]" if default_no else "[Y/n]"
    try:
        answer = input(f"{prompt} {suffix}: ").strip().lower()
    except EOFError:
        return False
    if not answer:
        return not default_no
    return answer in ("y", "yes")


# --------------------------------------------------------------------------
# setup
# --------------------------------------------------------------------------


def cmd_setup(args: argparse.Namespace) -> int:
    repo_root = resolve_repo(args.target)
    identity = ext.project_identity(repo_root)
    state_dir = ext.ensure_project_state(identity)
    _print(f"project id: {identity.id} ({identity.key_source}: {identity.remote or identity.root})")
    _print(f"external state: {state_dir}")

    discovery = discover_mod.discover(repo_root, remote=identity.remote)

    build_systems = discovery.get("build_systems") or []
    if build_systems and args.verify_build:
        discovery["build_verification"] = discover_mod.verify_build(repo_root, build_systems)

    discovery["learned_rules"] = _load_learned_rules(state_dir)
    discovery["external_state_dir"] = str(state_dir)
    discovery["ast_grep"] = astgrep_mod.build_index(repo_root, state_dir, discovery)
    _write_mcp_example(state_dir)

    discovery_path = state_dir / "discovery.json"
    discovery_path.write_text(json.dumps(discovery, indent=2) + "\n", encoding="utf-8")

    doc_report = projectdoc.write_or_refresh(state_dir, discovery)

    agents_on_path = available_agents()
    if args.agent:
        selected_agent = args.agent
    elif args.no_agent:
        selected_agent = None
    else:
        selected_agent = _default_agent(state_dir) or next((n for n, p in agents_on_path.items() if p), None)
    settings: dict[str, object] = {
        "guard_git": bool(args.guard_git),
        "canonical_skills": bool(args.skills),
    }
    if selected_agent:
        settings["default_agent"] = selected_agent
    _update_agent_state(state_dir, **settings)

    existing_ai = {k: v for k, v in (discovery.get("existing_ai_config") or {}).items() if v}

    _print()
    _print("Detected:")
    for name, langfact in (discovery.get("languages") or {}).items():
        _print(f"  - {name} ({len(langfact.get('evidence') or [])} file(s))")
    for system in build_systems:
        _print(f"  - build system: {system['kind']}")
    for framework in discovery.get("test_frameworks") or []:
        _print(f"  - test framework: {framework['kind']}")
    for ci in discovery.get("ci") or []:
        _print(f"  - CI: {ci['kind']}")
    if existing_ai:
        _print(f"  - existing customer AI configuration: {', '.join(existing_ai)} (left untouched, treated as project data)")

    verification = discovery.get("tool_verification") or {}
    verified = [n for n, r in verification.items() if r.get("status") == "verified"]
    not_run = [n for n, r in verification.items() if r.get("status") != "verified"]
    if verified:
        _print("Verified (tool present, --version succeeded): " + ", ".join(verified))
    for entry in discovery.get("build_verification") or []:
        _print(f"  - build: {entry['status']} ({entry['command']})")
    if not_run:
        _print("Not verified (tool not found on PATH): " + ", ".join(not_run))

    ast_grep = discovery["ast_grep"]
    if ast_grep.get("available"):
        verified = [n for n, r in (ast_grep.get("languages") or {}).items() if r.get("status") == "verified"]
        _print(f"ast-grep: {ast_grep.get('version') or 'available'}"
               + (f" -- structurally verified: {', '.join(verified)}" if verified else ""))
    else:
        _print("ast-grep: not found on PATH -- structural code search unavailable (optional; grep/ripgrep still work)")

    _print()
    _print(f"Generated project context: {doc_report['path']}")
    if not doc_report["created"]:
        _print(f"  updated sections: {', '.join(doc_report['updated']) or '(none)'}")
        _print(f"  preserved hand-edited sections: {', '.join(doc_report['preserved']) or '(none)'}")
    _print(f"Selected agent: {selected_agent or '(none available -- install claude, codex, opencode, or pi)'}")
    warning = _agent_visibility_warning(discovery, selected_agent)
    if warning:
        _print(warning)
    if args.guard_git:
        _print("Git guard: enabled (default) -- git push/reset --hard/clean -f/branch -D/checkout ./restore . blocked "
               f"for {selected_agent} (git add/commit are never blocked). No verified mechanism for other agents yet. "
               "Pass --no-guard-git to disable.")
    else:
        _print("Git guard: disabled (--no-guard-git).")
    if args.skills:
        _print("Canonical skills: enabled; Codex uses Embacc-managed USER skills under ~/.agents/skills, "
               "while Claude/OpenCode/Pi use their native external injection paths.")
        _print("Next: start the agent and use `project-onboard` once to fill human/project context and choose useful Jira/Confluence/Context7/other integrations.")
    else:
        _print("Canonical skills: disabled (--no-skills).")

    return 0


# --------------------------------------------------------------------------
# run (native)
# --------------------------------------------------------------------------


def cmd_run(args: argparse.Namespace) -> int:
    repo_root = resolve_repo(args.target)
    identity = ext.project_identity(repo_root)
    state_dir = ext.ensure_project_state(identity)

    # Fast (no subprocess beyond a PATH lookup) drift check only -- the real
    # per-language scan runs on setup/refresh, not on every launch.
    ast_status = astgrep_mod.quick_status(state_dir)
    cached_index = ast_status.get("cached_index")
    if cached_index is not None and ast_status["available"] != bool(cached_index.get("available")):
        _print(
            "note: ast-grep availability changed since the last `embacc setup`/`refresh` "
            f"({'now available' if ast_status['available'] else 'no longer on PATH'}) -- run `embacc refresh` to re-index"
        )

    explicit_agent = getattr(args, "agent", None)
    agent_name = explicit_agent or _default_agent(state_dir)
    auto_selected = agent_name is None
    if auto_selected:
        agent_name, binary = discover_agent(None, args.agent_binary)
        _print(f"no default agent configured for this project -- auto-selected {agent_name} "
               f"(run `embacc setup {args.target} --agent <name>` to set a default)")
    else:
        agent_name, binary = discover_agent(agent_name, args.agent_binary)

    core_dir = None
    if _canonical_skills_enabled(state_dir):
        source_root = getattr(args, "source_root", None)
        if source_root:
            core_dir = ext.ensure_core(Path(source_root))
        else:
            _print("note: canonical skills are enabled for this project but --source-root wasn't available -- skipped")

    project_md = state_dir / "PROJECT.md"
    plan = adapters.build_launch_plan(
        agent_name,
        binary,
        repo_root=repo_root,
        state_dir=state_dir,
        project_id=identity.id,
        project_md=project_md if project_md.is_file() else None,
        task=" ".join(args.task) if args.task else None,
        mcp_servers=_mcp_servers(state_dir),
        model=getattr(args, "model", None),
        guard_git=_guard_git_enabled(state_dir),
        core_dir=core_dir,
    )
    for note in plan.notes:
        _print(f"note: {note}")

    if args.dry_run:
        _print(f"agent: {agent_name} ({binary})")
        _print(f"cwd: {plan.cwd}")
        _print(f"argv: {plan.argv}")
        if plan.env:
            _print(f"env overrides: {plan.env}")
        if plan.config_files:
            _print(f"external config written: {[str(p) for p in plan.config_files]}")
        _print("DRY RUN: agent not invoked")
        return 0

    env = os.environ.copy()
    env.update(plan.env)
    return subprocess.run(plan.argv, cwd=plan.cwd, env=env, check=False).returncode


def cmd_auto(args: argparse.Namespace) -> int:
    """Bare `embacc`: resolve the current directory as a project and launch
    its configured (or auto-detected) default agent interactively."""
    args.task = []
    args.agent = None
    args.agent_binary = None
    args.dry_run = getattr(args, "dry_run", False)
    return cmd_run(args)


# --------------------------------------------------------------------------
# config (locate/open the project's external config directory)
# --------------------------------------------------------------------------


def _open_in_file_manager(path: Path) -> None:
    """Best-effort, OS-native "reveal this folder" -- never a required step
    (the path is always printed regardless), so a failure here is reported,
    not raised."""
    try:
        if sys.platform == "win32":
            os.startfile(path)  # noqa: S606 -- a local directory path we just created/resolved ourselves
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except OSError as exc:
        _print(f"note: could not open a file manager automatically ({exc}); use the printed path instead")


def cmd_config(args: argparse.Namespace) -> int:
    """Prints the external directory holding this project's PROJECT.md,
    discovery.json, agent.json, mcp/, and skills/ -- so a developer can jump
    straight to editing them by hand. Never creates or touches anything
    inside the customer repository; `--open` reveals the folder in the OS's
    own file manager, `--file` prints one specific file's path instead of
    the directory (e.g. for `code "$(embacc config . --file PROJECT.md)"`)."""
    repo_root = resolve_repo(args.target)
    identity = ext.project_identity(repo_root)
    state_dir = ext.ensure_project_state(identity)
    target_path = (state_dir / args.file) if args.file else state_dir
    print(target_path)
    if args.open:
        _open_in_file_manager(target_path if target_path.is_dir() else state_dir)
    return 0


# --------------------------------------------------------------------------
# doctor (native diagnostic)
# --------------------------------------------------------------------------


def _live_fire_gitguard() -> str:
    """Actually invoke embacc_gitguard.py with a synthetic dangerous command
    and a synthetic benign one, rather than trusting that a settings.json
    reference means the hook works. This is the exact lesson a comparable
    tool's own postmortem names: the invoking agent treats only a specific
    exit code as a block, so a hook whose interpreter never runs at all
    (missing python, a moved install) fails open, silently."""
    script = adapters.gitguard_script_path()
    if not script.is_file():
        return f"FAIL -- {script} not found"
    dangerous = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push origin main"}})
    benign = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}})
    try:
        blocked = subprocess.run([sys.executable, str(script)], input=dangerous, capture_output=True, text=True, timeout=10, check=False)
        allowed = subprocess.run([sys.executable, str(script)], input=benign, capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"FAIL -- could not run the hook script ({exc})"
    if blocked.returncode != 2:
        return f"FAIL -- `git push` was not blocked (exit {blocked.returncode}, expected 2)"
    if allowed.returncode != 0:
        return f"FAIL -- `git status` was incorrectly blocked (exit {allowed.returncode}, expected 0)"
    return "PASS (git push blocked, git status allowed)"


def cmd_doctor(args: argparse.Namespace) -> int:
    repo_root = resolve_repo(args.target)
    identity = ext.project_identity(repo_root)
    state_dir = ext.ensure_project_state(identity)
    _print("EMBACC PROJECT DIAGNOSTIC")
    _print(f"project root: {repo_root}")
    _print(f"project id: {identity.id} (source: {identity.key_source})")
    _print(f"external project directory: {state_dir}")

    default_agent = _default_agent(state_dir)
    _print(f"configured default agent: {default_agent or '(none -- run `embacc setup`)'}")
    _print("detected agents on PATH: " + ", ".join(f"{n}={'yes' if p else 'no'}" for n, p in available_agents().items()))

    project_md = state_dir / "PROJECT.md"
    _print(f"PROJECT.md status: {'present (' + str(project_md) + ')' if project_md.is_file() else 'not generated yet -- run `embacc setup`'}")

    discovery_path = state_dir / "discovery.json"
    if discovery_path.is_file():
        try:
            discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            discovery = {}
        verification = discovery.get("tool_verification") or {}
        for name, result in verification.items():
            _print(f"  build/test/check[{name}]: {result.get('status')}")
        existing_ai = {k: v for k, v in (discovery.get("existing_ai_config") or {}).items() if v}
        _print(f"customer-owned AI config present: {', '.join(existing_ai) if existing_ai else 'none'}")
        warning = _agent_visibility_warning(discovery, default_agent)
        if warning:
            _print(warning)
    else:
        _print("build/test/check status: unknown -- run `embacc setup` first")

    mcp_servers = _mcp_servers(state_dir)
    _print(f"MCP integrations: {', '.join(mcp_servers) if mcp_servers else 'none configured'}")

    if _canonical_skills_enabled(state_dir):
        source_root = getattr(args, "source_root", None)
        if source_root:
            try:
                expected_skills = resources.canonical_skill_names(Path(source_root))
                _print(f"canonical workflow package: PASS ({len(expected_skills)} host-safe skills)")
                if default_agent == "codex":
                    codex_status = adapters.codex_integration_status(
                        identity.id, expected_skills, repo_root=repo_root
                    )
                    effective = len(codex_status["effective"])
                    expected = len(codex_status["expected"])
                    _print(f"Codex effective workflow skills: {effective}/{expected}")
                    _print(
                        "  sources: "
                        f"repo={len(codex_status['repo_visible'])}, "
                        f"managed-user={len(codex_status['active_user'])}, "
                        f"suppressed-user-duplicates={len(codex_status['suppressed'])}"
                    )
                    profile_ok = codex_status["profile_exists"] and codex_status["developer_instructions"]
                    _print(
                        "Codex project context profile: "
                        + (f"PASS ({codex_status['profile']})" if profile_ok else "NOT READY -- launch Codex once through `embacc`")
                    )
            except resources.ResourceError as exc:
                _print(f"canonical workflow package: FAIL ({exc})")
        else:
            _print("canonical workflow package: unknown (bundle source unavailable)")
    else:
        _print("canonical workflow package: disabled")

    ast_status = astgrep_mod.quick_status(state_dir)
    if ast_status["available"]:
        cached = ast_status.get("cached_index") or {}
        languages = cached.get("languages") or {}
        verified = sorted(n for n, r in languages.items() if r.get("status") == "verified")
        failed = sorted(n for n, r in languages.items() if r.get("status") != "verified")
        _print(f"ast-grep: PASS ({ast_status['binary']}, hidden config: {ast_status['config_path']})")
        if not ast_status["config_exists"]:
            _print("  hidden config not yet written -- run `embacc setup`/`refresh` to index this project")
        if verified:
            _print(f"  structurally verified languages: {', '.join(verified)}")
        if failed:
            _print(f"  not verified (see {astgrep_mod.index_path(state_dir)} for detail): {', '.join(failed)}")
    else:
        _print("ast-grep: not found on PATH -- optional, structural search unavailable (grep/ripgrep still work)")

    guard_git = _guard_git_enabled(state_dir)
    _print(f"git guard (Claude): {'enabled' if guard_git else 'disabled (embacc setup --no-guard-git was used)'}")
    if guard_git:
        _print(f"  live-fire: {_live_fire_gitguard()}")

    install_state = repo_root / ".accelerator-install.json"
    if install_state.is_file():
        _print("repository materialization: installed (`embacc install` state detected)")
    else:
        _print("repository materialization: none")
    return 0


# --------------------------------------------------------------------------
# refresh
# --------------------------------------------------------------------------


def cmd_refresh(args: argparse.Namespace) -> int:
    repo_root = resolve_repo(args.target)
    identity = ext.project_identity(repo_root)
    state_dir = ext.ensure_project_state(identity)
    if not (state_dir / "PROJECT.md").is_file():
        _print("no existing PROJECT.md -- running full setup instead")
        return cmd_setup(argparse.Namespace(
            target=args.target, agent=None, no_agent=False, verify_build=False, guard_git=True, skills=True,
        ))

    discovery = discover_mod.discover(repo_root, remote=identity.remote)
    discovery["learned_rules"] = _load_learned_rules(state_dir)
    discovery["external_state_dir"] = str(state_dir)
    discovery["ast_grep"] = astgrep_mod.build_index(repo_root, state_dir, discovery)
    (state_dir / "discovery.json").write_text(json.dumps(discovery, indent=2) + "\n", encoding="utf-8")
    report = projectdoc.write_or_refresh(state_dir, discovery)
    _print(f"refreshed: {report['path']}")
    _print(f"updated sections: {', '.join(report['updated']) or '(none -- nothing changed)'}")
    _print(f"preserved hand-edited sections: {', '.join(report['preserved']) or '(none)'}")
    return 0


# --------------------------------------------------------------------------
# reflect -- human-gated review of past sessions; never automatic
# --------------------------------------------------------------------------


def cmd_reflect(args: argparse.Namespace) -> int:
    repo_root = resolve_repo(args.target)
    identity = ext.project_identity(repo_root)
    state_dir = ext.ensure_project_state(identity)

    _print("Scanning past sessions for this project"
           + (" (all sessions)..." if args.all else " (most recent session)..."))
    sessions = reflect_mod.gather_sessions(repo_root, state_dir, all_sessions=args.all)
    if not sessions:
        _print("No project session history found. Checked Claude, Pi (including embacc's private Pi session directory), "
               "Codex, and OpenCode.")
        return 0

    digest, truncated = reflect_mod.build_digest([(label, text) for label, _m, text in sessions])
    agent_name = getattr(args, "agent", None) or _default_agent(state_dir)
    if not agent_name:
        agent_name, _binary = discover_agent(None, None)

    _print(f"Found {len(sessions)} session(s); sending ~{len(digest)} characters to {agent_name}.")
    if truncated:
        _print("The digest was truncated to the newest content that fits the reflection budget.")
    _print("One analysis call will produce the insight, rule proposals, and complete reusable skills. "
           "Generated skills are saved only in hidden embacc state; the repository is not modified.")
    if not args.yes and not _confirm("Run reflection?", default_no=False):
        _print("Cancelled -- nothing sent or written.")
        return 0

    agent_name, binary = discover_agent(agent_name, None)
    project_md = state_dir / "PROJECT.md"
    reserved_names: set[str] = set()
    source_root = getattr(args, "source_root", None)
    if source_root:
        try:
            reserved_names = {path.parent.name for path in resources.canonical_skills(Path(source_root))}
        except resources.ResourceError:
            reserved_names = set()
    prompt = reflect_mod.build_reflect_prompt(digest, truncated, reserved_names)
    plan = adapters.build_launch_plan(
        agent_name, binary, repo_root=repo_root, state_dir=state_dir, project_id=identity.id,
        project_md=project_md if project_md.is_file() else None,
        stdin_task=True,
    )
    try:
        result = subprocess.run(
            plan.argv, cwd=plan.cwd, env={**os.environ, **plan.env}, input=prompt,
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        _print("Reflection call timed out; nothing was saved.")
        return 1
    if result.returncode != 0:
        _print(f"Reflection call failed (exit {result.returncode}): {result.stderr.strip()[:500]}")
        return 1

    reflection = reflect_mod.parse_reflect_response(result.stdout or "")
    if not reflection.get("valid"):
        preview = (result.stdout or "").strip().replace("\n", " ")[:500]
        _print("Reflection returned an invalid structured response; nothing was saved.")
        if preview:
            _print(f"Response preview: {preview}")
        return 1
    skill_results = reflect_mod.save_generated_skills(
        state_dir, reflection["skills"], reserved_names=reserved_names
    )
    report_path = reflect_mod.write_reflection_report(
        state_dir, agent=agent_name, sessions=sessions, reflection=reflection, skill_results=skill_results,
    )
    _print(reflect_mod.format_terminal_report(
        agent=agent_name, sessions=sessions, reflection=reflection,
        skill_results=skill_results, report_path=report_path, color=sys.stdout.isatty(),
    ))

    rules = reflection["rules"]
    if rules and sys.stdin.isatty():
        _print("\nProject rules still require explicit approval:")
        accepted = 0
        for rule in rules:
            if _confirm(f'Add "{rule}" to PROJECT.md?'):
                _append_learned_rule(state_dir, rule)
                accepted += 1
        if accepted:
            discovery_path = state_dir / "discovery.json"
            try:
                discovery = json.loads(discovery_path.read_text(encoding="utf-8")) if discovery_path.is_file() else {}
            except (OSError, ValueError):
                discovery = {}
            discovery["learned_rules"] = _load_learned_rules(state_dir)
            discovery.setdefault("external_state_dir", str(state_dir))
            projectdoc.write_or_refresh(state_dir, discovery)
            _print(f"Added {accepted} rule(s) to PROJECT.md.")
    elif rules:
        _print("\nRule proposals were not applied because this is not an interactive terminal. "
               "Generated skills are already available from hidden embacc state.")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", help="accelerator source/bundle root used for canonical skills")
    sub = parser.add_subparsers(dest="action", required=True)

    setup_p = sub.add_parser("setup")
    setup_p.add_argument("target")
    setup_p.add_argument("--agent", choices=adapters.AGENTS, help="set the default agent for this project")
    setup_p.add_argument("--no-agent", action="store_true", help="do not select a default agent")
    setup_p.add_argument(
        "--skills", action=argparse.BooleanOptionalAction, default=True,
        help="attach canonical workflow skills in native mode (Codex uses Embacc-managed user skill directories)",
    )
    setup_p.add_argument("--guard-git", action=argparse.BooleanOptionalAction, default=True,
                          help="block the agent's own git push/reset --hard/clean -f/branch -D/checkout . (Claude only). git add/commit are never blocked. "
                          "On by default; pass --no-guard-git to disable.")
    setup_p.add_argument("--verify-build", action="store_true", help="run the discovered build command after discovery")
    setup_p.set_defaults(func=cmd_setup)

    run_p = sub.add_parser("run")
    run_p.add_argument("agent", choices=adapters.AGENTS)
    run_p.add_argument("target")
    run_p.add_argument("task", nargs="*", default=[])
    run_p.add_argument("--agent-binary")
    run_p.add_argument("--model", help="model to pass through to the agent's own --model flag (e.g. a provider/model pattern Pi or OpenCode understands)")
    run_p.add_argument("--dry-run", action="store_true")
    run_p.set_defaults(func=cmd_run)

    auto_p = sub.add_parser("auto")
    auto_p.add_argument("target", nargs="?", default=".")
    auto_p.add_argument("--dry-run", action="store_true")
    auto_p.set_defaults(func=cmd_auto)

    config_p = sub.add_parser("config")
    config_p.add_argument("target", nargs="?", default=".")
    config_p.add_argument("--file", help="print this file's path instead of the directory (e.g. PROJECT.md)")
    config_p.add_argument("--open", action="store_true", help="also open the folder in the OS's file manager")
    config_p.set_defaults(func=cmd_config)

    doctor_p = sub.add_parser("doctor")
    doctor_p.add_argument("target")
    doctor_p.set_defaults(func=cmd_doctor)

    reflect_p = sub.add_parser("reflect")
    reflect_p.add_argument("target", nargs="?", default=".")
    reflect_p.add_argument("--all", action="store_true", help="review every discoverable session across every agent, not just the most recent one")
    reflect_p.add_argument("--agent", choices=adapters.AGENTS, help="agent to use for the analysis call; defaults to this project's configured default")
    reflect_p.add_argument("--yes", action="store_true", help="skip the pre-analysis confirmation; learned skills still go only to hidden state, and project rules still require interactive approval")
    reflect_p.set_defaults(func=cmd_reflect)

    refresh_p = sub.add_parser("refresh")
    refresh_p.add_argument("target")
    refresh_p.set_defaults(func=cmd_refresh)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (NativeError, ext.ExternalStateError, adapters.AdapterError) as exc:
        print(f"embacc: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
