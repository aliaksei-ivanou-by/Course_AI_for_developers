# Summary: Task Master AI

Task Master AI is an open-source CLI and MCP task-management layer for AI-assisted development. It converts a reviewed PRD or specification into tasks, records dependencies and status, analyzes complexity, expands selected work into subtasks, and recommends the next unblocked task. This persistent execution state reduces dependence on a long chat history, but it does not replace product decisions, architecture, testing, or code review.

Task Master and Hamster are related but distinct. Task Master is the local project tool; Hamster is a broader hosted platform for team goals, research, briefs, plans, shared context, collaboration, and delivery. Task Master can be used without Hamster.

The core workflow is:

```text
init → configure models → parse PRD → review tasks
     → analyze complexity → review report → expand selected tasks
     → next → show → implement → verify → set status → repeat
```

Use `task-master models --setup` for the main, research, and fallback roles. Depending on the chosen provider, Task Master can use API keys or authenticated Claude Code/Codex CLI installations. Keep secrets outside version control, copy current model IDs from the provider, and do not treat the fixed costs or model names shown in a recording as permanent.

Task Master can complement GitHub Spec Kit: Spec Kit clarifies and plans the feature, while Task Master manages persistent execution state. Use a consolidated input containing scope, acceptance criteria, stack, constraints, and test expectations; otherwise the model may invent missing technical decisions. Define one authoritative task list to avoid drift between Spec Kit, Task Master, and an external issue tracker.

Task Master is most useful for large, dependency-heavy work that spans sessions or agents. It is usually overhead for a small feature that fits in one focused session. Review every generated task graph, expand only genuinely complex tasks, load only the MCP tools you need, and mark work done only after verification succeeds.
