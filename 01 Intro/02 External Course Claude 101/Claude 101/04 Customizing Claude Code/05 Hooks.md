# Hooks

Hooks run commands at specific points in the Claude Code lifecycle. Unlike prompts and other guidance, hooks are deterministic: they run whenever their configured conditions are met.

## Why Use Hooks?

A `CLAUDE.md` instruction can ask Claude to run Prettier after every file edit, but Claude may occasionally omit that step. A hook enforces it every time.

Common uses include:

- Automatically formatting edited files.
- Logging executed commands for compliance.
- Blocking dangerous operations, such as modifying production files.
- Sending notifications when Claude finishes a task.

## How Hooks Work

Hooks are configured in `settings.json`. Each hook defines an event, an optional matcher that selects applicable tools, and a command to run.

Available events include:

- `PreToolUse` — runs before a tool call.
- `PostToolUse` — runs after a tool call completes.
- `UserPromptSubmit` — runs after a prompt is submitted but before Claude processes it.
- `Stop` — runs when Claude finishes responding.
- `Notification` — runs when Claude sends a notification.

Configure hooks through `/hooks` in Claude Code or edit `settings.json` directly.

![Claude Code hooks settings file](Hooks%20Settings%20File.png)

## Example: Automatic Formatting

A common hook automatically formats files after edits. Configure a `PostToolUse` hook with an `Edit|MultiEdit|Write` matcher so it runs whenever Claude modifies a file. The command can inspect the file extension and select the appropriate formatter, such as Prettier for TypeScript or `gofmt` for Go.

## Blocking Actions with `PreToolUse`

A `PreToolUse` hook can block a tool call before it runs. The hook receives the tool name and input as JSON through standard input. Its exit code determines what happens next:

- **Exit code 0:** continue normally.
- **Exit code 2:** block the action and return the standard-error message to Claude as feedback.
- **Any other exit code:** display a non-blocking error without stopping the action.

This mechanism can enforce rules such as blocking writes to production configuration, dangerous shell commands, or commits to the main branch.

![PreToolUse hook configuration](PreToolUse%20Hook%20Configuration.png)

## Sharing Hooks with a Team

Hooks stored in `.claude/settings.json` are project-level and can be committed to the repository. Use the `CLAUDE_PROJECT_DIR` environment variable when referencing project scripts so commands work regardless of Claude's current working directory.

## Recap

Hooks provide deterministic control over Claude Code. Use `PostToolUse` for actions such as formatting and logging, and use `PreToolUse` to block unsafe operations. Configure hooks through `/hooks` or `settings.json`, then commit project-level hooks so the team shares the same behavior.

If something must happen every time, place it in a hook rather than relying only on a prompt.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=IkaPHiMDazM)
