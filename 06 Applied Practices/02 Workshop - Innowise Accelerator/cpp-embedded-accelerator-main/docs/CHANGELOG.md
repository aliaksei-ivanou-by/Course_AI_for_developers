# Changelog


## 2.6.0 - workflow-driven core, structural search, self-serve skills

Replaces the previous knowledge-pack-heavy architecture with a simplified,
workflow-driven core, then adds structural code search and closes several
real gaps found by testing on real projects and real agent CLIs.

Core simplification:
- Removed deprecated overlay/route workflow code, 142 knowledge packs and the knowledge-router/search subsystem, project-profile overlays, write-only metrics, task/spec ceremony, archive reports, and the non-enforced policy engine.
- Reduced 33 canonical skills to a focused set of 17 workflow/discipline procedures; removed global Codex skill synchronization, generated Codex hooks/subagents, and redundant Claude/OpenCode subagent adapters.
- Restored the outstaff process layer: guided `project-onboard`, `feature`, `bug`, `review-pr`/`pr-review-response`, external `task-workspace`/`handoff`, requirements/planning/coding/testing/review/verify skills, and immediate-learning `stabilize`.
- `project-onboard` now proactively recommends Jira/Confluence, Context7, code-host, and observability integrations and verifies current MCP setup before configuring one.
- Simplified explicit install to hash-based managed files with fail-closed conflicts; reduced repository Markdown to `README.md`, `AGENTS.md`, architecture, and changelog.
- Split deterministic tests by responsibility under `tests/`.

Session retrospective and learned skills:
- Reworked `reflect` to find Pi sessions from embacc's custom session directory and Pi session-header `cwd`; one structured model call now emits complete reusable `SKILL.md` files in the same pass.
- Validated learned skills are stored in hidden per-project state and injected into future Claude/Codex/OpenCode/Pi sessions, with reserved-name/collision protection and self-reflection-session filtering.

Agent integration isolation:
- Claude and Codex no longer show duplicate canonical skills when a repository already exposes the same names; Codex canonical workflows use dedicated, ownership-marked USER-scope directories instead of a shared, leak-prone sync.
- Fixed a real cross-project skill-duplication bug hit by testing an in-place upgrade: legacy bare-named Codex mirrors (`bug/`, not `embacc-bug/`) from the pre-namespacing sync are now reaped, instead of sitting alongside the new ones forever.

Structural code search:
- Added `ast-grep` structural code intelligence: hidden per-project config/state, a real per-language scan against the repository's own source during `setup`/`refresh`, a fast PATH-only check on `run`, `doctor` diagnostics, and a new PROJECT.md "Structural code search" section reaching every agent -- live-verified changing real agent tool choice, not just present as text.
- Ships as a pixi run-dependency of embacc itself; found automatically (no `--expose` needed) alongside a standalone install if one exists.

Self-serve project-private skills:
- Claude and Codex can now write a learned `SKILL.md` into hidden state themselves when a developer explicitly asks, matching what the AI restrictions section already instructed them to do.
- Fixed a real regression hit while shipping the above and reproduced from an actual user session: bare `embacc` crashed launching Claude with a UNC-network-path parse error; even once fixed, the grant silently did nothing because `--add-dir` requires its target directory to already exist -- now created eagerly on the very first launch.

Other fixes:
- Fixed a cross-project session leak in `embacc reflect`: `find_opencode_sessions` trusted `opencode session list`'s global, unscoped output, so an unrelated project's OpenCode session could be analyzed in a completely different repository's retrospective.
