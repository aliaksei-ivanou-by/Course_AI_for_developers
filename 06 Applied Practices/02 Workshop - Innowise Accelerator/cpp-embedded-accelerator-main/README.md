# C++ / Embedded Accelerator

`embacc` gives Claude Code, Codex, OpenCode, and Pi a controlled outstaff-development workflow without putting accelerator state into a client repository during normal use.

The maintained core is intentionally focused: project discovery, external `PROJECT.md`, guided onboarding, feature/bug/review flows with human gates, hidden task workspaces, native agent launch, session retrospective/learning, safety helpers, explicit repository install, and self-update. There are no bundled topical knowledge packs.

## Install

From a local checkout:

```bash
pixi global install --path . --force-reinstall
```

From Git:

```bash
pixi global install --git <repository-url> --branch main --force-reinstall
```

`ast-grep` is a declared run-dependency of the `cpp-embedded-accelerator` pixi package (conda-forge), so it installs into the same isolated environment as `embacc` itself -- no separate install step. It does not need `--expose`: embacc looks for a standalone `ast-grep` on PATH first (so an existing manual install still wins), and falls back to the copy inside its own pixi environment automatically. Want `ast-grep` as its own terminal command too? Add `--expose embacc --expose ast-grep` to the command above (once you add any `--expose` flag, pixi stops auto-exposing `embacc` by default, so both need naming together).

## Normal workflow

```bash
embacc setup .
embacc
```

Other supported commands:

```bash
embacc run <claude|codex|opencode|pi> .
embacc doctor .
embacc refresh .
embacc config .
embacc reflect .
embacc self-update
embacc version
```

`setup`, `run`, `doctor`, `refresh`, `config`, and `reflect` keep accelerator-owned state under `~/.embacc` (or `ACCELERATOR_HOME`). They do not materialize accelerator infrastructure into the repository.

`setup` discovers languages, build/test systems, CI, and useful tooling from repository evidence, then creates or refreshes external `PROJECT.md`. Build execution is opt-in. Start the agent and use `project-onboard` to fill human/project context and decide which external sources (for example Jira, Confluence, Context7, GitHub/GitLab, or observability) are worth connecting.

## Controlled workflow skills

The canonical workflow set is:

- `project-onboard`
- `feature`, `bug`
- `task-workspace`
- `requirements-analyst`, `requirements-clarifier`, `writing-plans`
- `coder`, `testing`, `systematic-debugger`
- `self-review`, `code-reviewer`, `verify`
- `review-pr`, `pr-review-response`, `handoff`
- `stabilize`

Feature and bug workflows use hidden task artifacts under `~/.embacc/projects/<project-id>/tasks/<task>/` and explicit human gates before important transitions. `STATE.md` is the resume point after a cleared/new agent session.

Canonical `SKILL.md` metadata uses a strict host-safe frontmatter subset; descriptions are always double-quoted so punctuation such as `:` cannot break Pi/Codex YAML parsing.

### Agent delivery

- Claude receives a private merged plugin containing canonical + project-learned skills. If `embacc install --tools claude` already exposed canonical workflows in `.claude/skills`, the external plugin carries only missing/private learned skills, avoiding duplicate workflows.
- Pi receives canonical and project-learned skill roots through `--skill`.
- OpenCode receives those roots in its external configuration.
- Codex receives canonical workflows through Embacc-managed USER-scope skill directories at `$HOME/.agents/skills/embacc-<name>/`. Codex documents `$HOME/.agents/skills` as a native user skill source. When the current repository already exposes the same canonical name from `.agents/skills`, its project profile disables only the duplicate Embacc USER copy by exact `SKILL.md` path. Embacc only updates/removes directories that carry its ownership marker. Project-private learned skills are **not** copied globally; their complete instructions are injected only into that project's generated Codex profile.

The Codex profile uses `developer_instructions` for external `PROJECT.md` context; it does not use the reserved `instructions` key.

Project-learned skills remain outside the repository at `~/.embacc/projects/<project-id>/agent-config/skills/<name>/SKILL.md`. Claude and Codex are launched with self-serve write access to exactly that directory (Claude: `--permission-mode acceptEdits`, session-wide -- a directory-scoped rule alone was live-fire confirmed not to suppress the approval prompt for a launch outside the repo; Codex: a scoped `sandbox_workspace_write.writable_roots` entry), so an agent can write a learned skill there itself when a developer explicitly asks, matching what the AI restrictions section already instructs it to do.

## Session retrospective

```bash
embacc reflect .
```

`embacc reflect` is a batch retrospective, not a canonical skill. It reads discoverable past sessions for this project across Claude, Pi, Codex, and OpenCode. For Pi it checks both normal Pi history and Embacc's private `--session-dir`. One analysis call returns a structured retrospective and, when a repeated procedure is strongly evidenced, full learned-skill content. Embacc reconstructs host-safe `SKILL.md` frontmatter itself before saving it. Existing learned skills are never overwritten automatically. Project-rule changes still require explicit human approval.

The `stabilize` skill is the in-session mechanism for turning a correction or recurring mistake into a durable rule/workflow; it is deliberately separate from `embacc reflect`.

## Structural code search

When `ast-grep` is on PATH, `embacc setup`/`refresh` write a hidden `sgconfig.yml` under `~/.embacc/projects/<project-id>/ast-grep/` and structurally verify it against the project's own source, one real scan per discovered language. The result reaches every agent through PROJECT.md's "Structural code search" section (hidden config path, verified languages, and a nudge to prefer `ast-grep` over regex grep for structural search/refactor) and through `embacc doctor`. `embacc run` only re-checks PATH availability, not a full re-scan, so launch stays fast. Entirely optional -- absent `ast-grep`, this degrades to a plain "not found, fall back to grep/ripgrep" note.

## Explicit repository install

Use this only when repository-local shared agent configuration is wanted:

```bash
embacc install /path/to/repo --tools codex
embacc install /path/to/repo --tools claude,opencode
```

The install payload contains `AGENTS.md`, all canonical workflow skills, and only selected tool-specific adapter files. It does not copy the Python runtime, tests, docs, or template sources into the client repository. Re-running the same command is the refresh path. A managed file is updated or removed only while its current hash still matches the last installed hash; a local edit becomes a conflict and is preserved.

Use `--dry-run` before an important install and `--allow-dirty` only after reviewing an already-dirty working tree.

## Tests

```bash
python tests/run_all.py
```

Optional checks that may call installed external agent CLIs/models:

```bash
python tests/run_all.py --live
```

## Design rules

- Normal mode never writes accelerator infrastructure into a customer repository.
- Explicit install never silently overwrites client-owned or locally modified files.
- Canonical workflow skills are valuable product behavior; topical knowledge/eval machinery is not part of runtime.
- Documentation is guidance, not an invented security sandbox.
- Canonical skill text lives once in `.agents/skills/`; adapters stay thin.
- Host-facing formats are validated structurally, not merely checked for file existence.

See `docs/ARCHITECTURE.md` for the runtime layout.
