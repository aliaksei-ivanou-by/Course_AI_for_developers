# Architecture

## Goal

Keep accelerator-owned context and workflow state outside customer repositories in normal mode, while giving coding agents a consistent outstaff process that survives session boundaries.

## External state

`~/.embacc` (or `ACCELERATOR_HOME`) owns two scopes:

```text
~/.embacc/
├── core/<version>/.agents/skills/    # canonical workflow + discipline skills
└── projects/<project-id>/
    ├── PROJECT.md                    # generated + human-enriched project context
    ├── discovery.json
    ├── agent.json
    ├── tasks/<slug>/                 # resumable feature/bug/review artifacts
    ├── mcp/                          # project context integrations
    ├── agent-config/skills/          # private learned project skills
    ├── ast-grep/                     # hidden sgconfig.yml + rules/ + index.json
    └── state/                        # hashes, sessions, reflections
```

Normal `setup/run/doctor/refresh/config/reflect` never create accelerator infrastructure in the customer repository.

## Process layer

The canonical library intentionally includes workflow orchestration rather than topical knowledge packs:

- onboarding: `project-onboard`;
- routes: `feature`, `bug`, `review-pr`, `pr-review-response`;
- task continuity: `task-workspace`, `handoff`;
- requirements/plan/implementation: `requirements-analyst`, `requirements-clarifier`, `writing-plans`, `coder`, `testing`;
- engineering checks: `systematic-debugger`, `self-review`, `code-reviewer`, `verify`;
- immediate learning: `stabilize`.

Feature and bug routes create artifacts under the external `tasks/<slug>/` directory and record blocking human gates in `STATE.md`. This preserves the useful control flow from the original outstaff accelerator without reintroducing repository-local task/spec registries.

## Onboarding and external context

`embacc setup` is deterministic and non-interactive. `project-onboard` is the agent-driven human layer: it fills the project facts discovery cannot infer and recommends external sources based on actual team workflow. Typical candidates are Jira/Confluence, Context7, GitHub/GitLab and observability systems.

Approved MCP definitions live in the external project `mcp/servers.json`. The onboarding skill must verify current server/package/auth instructions from authoritative documentation before writing a recipe and must keep credentials out of chat.

## Session reflection

`embacc reflect` is a CLI workflow, not a canonical skill name. It gathers project-related Claude/Pi/Codex/OpenCode sessions, excludes reflection sessions themselves, makes one analysis call, prints a structured report, proposes project rules, and may return complete reusable `SKILL.md` content. Valid learned skills are stored at:

`projects/<project-id>/agent-config/skills/<name>/SKILL.md`

Existing differing skills are preserved as conflicts. The separate `stabilize` skill handles immediate incident-driven learning during an active session.

Claude and Codex are also launched with self-serve write access to their own project's `agent-config/skills/` directory, so an agent can write a learned skill there itself when a developer explicitly asks (matching the AI restrictions instruction that already names this path). For Claude that is `--permission-mode acceptEdits` (live-fire confirmed: a directory-scoped `permissions.allow` Edit() rule alone did not suppress the approval prompt for a launch outside the repo, so this is session-wide, not scoped, edit auto-acceptance) plus `permissions.additionalDirectories` for the directory grant. For Codex it is `sandbox_mode = "workspace-write"` plus a `sandbox_workspace_write.writable_roots` entry naming only that directory (scoped, unlike Claude's grant). OpenCode already grants this through its own `permission.external_directory` config; Pi is unaffected.

## Structural code search

`ast-grep` is a declared `[tool.pixi.package.run-dependencies]` (conda-forge), so it installs into the same isolated pixi global environment as `embacc` itself -- no `--expose` needed (see README.md "Install"). Detection (`embacc_astgrep.binary()`) checks PATH first, so a developer's own standalone install still wins, and falls back to the copy inside embacc's own pixi environment (found relative to `sys.executable`, the conda `Library/bin`/`bin` layout) automatically. `embacc setup`/`refresh` detect an `ast-grep` binary this way and, only when found, write a hidden `sgconfig.yml` + empty `rules/` under `projects/<project-id>/ast-grep/` and run one real structural scan per discovered language (cpp/c/python/rust) against the repository's own source to confirm ast-grep's grammar actually parses it, caching the result to `ast-grep/index.json`. `embacc run` only re-checks PATH availability (no subprocess scan) so launch stays fast; a changed availability since the last index prints a note suggesting `embacc refresh`. The result is surfaced to every agent through a `PROJECT.md` "Structural code search" section (config path, verified languages, and a preference for `ast-grep` over regex grep for structural search/refactor) and to `embacc doctor`. Entirely optional: when the binary is absent, setup/run/doctor degrade to a plain "not found, fall back to grep/ripgrep" note and never fail.

## Agent adapters

Claude, OpenCode and Pi receive canonical and private project skills through their native external mechanisms. Codex receives `PROJECT.md` through a generated profile using `developer_instructions`; canonical workflows are mirrored into Embacc-owned USER-scope directories under `$HOME/.agents/skills`, while project-private learned skill text is injected only into that project's profile.

MCP config is translated only for agents with supported native mechanisms. An unsupported integration is reported honestly rather than emulated by a hidden transport layer.

## Explicit install

`embacc install` is the opt-in repository-local path. It materializes `AGENTS.md`, canonical skills and selected thin tool adapters. It never ships the Python runtime, tests, docs, knowledge packs, or template source tree into the customer repository.

Managed files use hash-based ownership: a file is refreshed/removed only while its current content still matches the last installed content. Human-modified files become conflicts and are preserved.

## Removed architecture

The project does not carry deprecated overlay/route executors, topical knowledge packs, project-profile overlays, write-only metrics, a non-enforced policy engine, a separate skill-creator/eval framework, installer self-replication, or generated Codex hook/subagent infrastructure.
