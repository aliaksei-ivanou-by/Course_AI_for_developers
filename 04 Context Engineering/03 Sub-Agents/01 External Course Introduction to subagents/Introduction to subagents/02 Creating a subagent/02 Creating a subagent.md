# Creating a Subagent

Claude Code includes built-in subagents, but you can also create specialized assistants for recurring tasks such as code review, test generation, documentation, or security analysis.

A custom subagent is a Markdown file with YAML frontmatter. The frontmatter defines when Claude should use the subagent and which capabilities it has; the Markdown body provides the subagent's system prompt.

## Version Note

The lesson video demonstrates the interactive creation wizard opened with `/agents` in Claude Code v2.0.59. In Claude Code v2.1.198 and later, `/agents` no longer opens that wizard. Ask Claude to create the subagent or edit its Markdown definition directly instead.

The file format and the `.claude/agents/` and `~/.claude/agents/` locations remain unchanged, so the configuration concepts from the lesson still apply.

## Choose the Scope

The location of the definition determines where the subagent is available:

| Scope | Location | Use when |
| --- | --- | --- |
| Project | `.claude/agents/` | The subagent is specific to one repository and should be shared with the team |
| User | `~/.claude/agents/` | The subagent should be available across all projects on your machine |

On Windows, `~/.claude/agents/` refers to the `.claude\agents` directory inside your user profile.

## Create the Definition

In current versions of Claude Code, describe the subagent you want and ask Claude to save it at the appropriate scope. For example:

```text
Create a project-level code-quality-reviewer subagent in .claude/agents/.
It should review recent code changes for correctness, security, maintainability,
and performance. Make it read-only and use Sonnet.
```

You can also create the Markdown file manually. The older wizard shown in the video offered two equivalent options: generate the definition with Claude or configure it yourself.

![Claude Code subagent creation options](Claude%20Code%20Subagent%20Creation.png)

## Restrict Tool Access

Give a subagent only the tools it needs. This keeps its responsibilities clear and reduces the chance of unintended actions.

The lesson groups tools into these categories:

- read-only tools;
- edit tools;
- execution tools;
- MCP tools; and
- other tools.

For example, a code-review subagent normally needs to read and search code but not edit it. Execution tools may still be useful when the reviewer needs to inspect a diff or run tests.

![Selecting tools for a Claude Code subagent](Claude%20Code%20Subagent%20Tool%20Selection.png)

## Choose a Model and Color

Choose a model according to the complexity and cost of the work:

| Model | Suitable use |
| --- | --- |
| Haiku | Fast, lightweight tasks |
| Sonnet | A balance of speed and depth |
| Opus | Complex analysis and difficult reasoning |
| Inherit | Use the model selected for the main conversation |

The optional color makes the active subagent easier to recognize in the interface.

![Choosing a color for a Claude Code subagent](Claude%20Code%20Subagent%20Color%20Selection.png)

## Understand the Configuration File

A project-level definition is typically stored at `.claude/agents/<agent-name>.md`. A code-review subagent might look like this:

```markdown
---
name: code-quality-reviewer
description: Reviews recently modified code for quality, security, and project-standard compliance. Use proactively after substantial code changes.
tools: Read, Glob, Grep, Bash
model: sonnet
color: purple
---

You are an expert code reviewer.

Examine recently written or modified code and identify issues that could affect
correctness, security, maintainability, or performance. Report findings in
priority order, cite the relevant files and lines, and explain any limitations.
```

The main fields are:

| Field | Purpose |
| --- | --- |
| `name` | Unique identifier used to reference the subagent |
| `description` | Explains when Claude should delegate work to the subagent |
| `tools` | Lists the tools the subagent may use |
| `model` | Selects `haiku`, `sonnet`, `opus`, or `inherit` |
| `color` | Sets the identifying color shown in the interface |

Everything below the frontmatter is the system prompt. It should state the subagent's role, what it must inspect, how it should work, and how it should report results.

## Enable Automatic Delegation

Claude uses the `description` field to decide when a task should be delegated. Make the description specific and concise. State the trigger, the intended task, and the situations in which the subagent should be used.

The word `proactively` can signal that Claude should consider the subagent automatically after a matching event:

```yaml
description: Reviews recent code changes. Use proactively after substantial implementation work.
```

Concrete trigger scenarios are more reliable than a vague role description. Keep detailed procedures in the system prompt so the always-visible description remains short.

## Invoke and Test the Subagent

You can request the subagent explicitly:

```text
Use the code-quality-reviewer subagent to review my recent changes.
```

You can also reference it by name with `@agent code-quality-reviewer`.

![Testing a Claude Code code-review subagent](Claude%20Code%20Subagent%20Test.png)

After creating the definition, make a small code change and ask for a review. Confirm that the intended subagent runs, has the expected tools, and returns a useful result.

If Claude does not delegate as expected:

1. Check that the file is in the correct `agents` directory.
2. Confirm that the YAML frontmatter is valid.
3. Make the `description` more specific about trigger scenarios.
4. Restart Claude Code if the `agents` directory was created after the current session started.

## Recap

- A custom subagent is a Markdown file with YAML frontmatter and a system prompt.
- Store project subagents in `.claude/agents/` and personal subagents in `~/.claude/agents/`.
- Restrict tools to the minimum required for the role.
- Use the `description` to define when delegation should happen.
- Put detailed behavior and output requirements in the system prompt.
- Test the subagent with a representative task and refine its triggers if necessary.

## Lesson Reflection

- Which recurring task in your workflow would benefit most from a dedicated subagent?
- What is the minimum set of tools that subagent would need?
- What concrete wording would make its delegation trigger unambiguous?

## What's Next?

In the next lesson, you will learn how to design reliable subagents with narrow responsibilities, structured output, obstacle reporting, and limited tool access.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=arD6qEWa2Xc)
