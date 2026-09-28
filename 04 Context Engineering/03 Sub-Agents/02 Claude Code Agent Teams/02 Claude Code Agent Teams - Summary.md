# Summary: Claude Code Agent Teams

Claude Code Agent Teams coordinate several independent Claude Code sessions. A team lead assigns or creates work, teammates operate in separate context windows, a shared task list tracks progress, and agents can communicate directly. This is heavier than ordinary subagent delegation and is most useful for genuinely parallel research, review, competing debugging hypotheses, or feature work with clearly separated ownership.

Agent Teams is experimental and disabled by default. Enable it with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. The default in-process display works in any terminal; `tmux` or iTerm2 is only required for supported split-pane workflows. Teammates load project context such as `CLAUDE.md`, skills, and MCP configuration, but they do not inherit the lead's conversation history, so spawn prompts must contain the task-specific context.

Keep teams small, give each teammate an independent scope and clear deliverable, avoid same-file edits, monitor progress, and shut workers down cleanly. Each teammate consumes tokens independently, so measure usage and choose models according to task difficulty. Preserve normal permission controls: bypassing permission checks is especially risky when multiple sessions can modify files or execute commands.

After a team workflow has succeeded repeatedly, it can be documented as a reusable skill with parameterized roles, inputs, output requirements, verification, and shutdown steps. Always verify current setup and limitations against the official Claude Code Agent Teams documentation.
