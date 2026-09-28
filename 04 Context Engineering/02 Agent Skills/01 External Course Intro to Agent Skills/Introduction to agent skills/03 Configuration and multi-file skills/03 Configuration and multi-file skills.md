# Configuration and Multi-File Skills

A basic Skill needs only a name, a description, and task instructions. More advanced Skills can select a model, pre-approve tools, and use supporting files so that detailed material enters the context only when it is needed.

## Skill Metadata Fields

The Agent Skills standard defines the core `SKILL.md` frontmatter fields, while Claude Code supports additional configuration fields.

| Field | Required | Purpose |
| --- | --- | --- |
| `name` | Yes | Identifies the Skill. Use lowercase letters, numbers, and hyphens; keep it within 64 characters and match the directory name. |
| `description` | Yes | Explains what the Skill does and when Claude should use it. Claude uses this field for matching; the maximum length is 1,024 characters. |
| `allowed-tools` | No | Pre-approves selected tools while the Skill is active. |
| `model` | No | Selects the Claude model used for the Skill. |

An example configuration looks like this:

```yaml
---
name: codebase-onboarding
description: Helps new developers understand how the system works. Use when explaining the project architecture, directory structure, or component responsibilities.
allowed-tools: Read, Grep, Glob, Bash
model: sonnet
---
```

![A Skill configured with allowed-tools and a model](Skill%20Metadata%20and%20Allowed%20Tools.png)

## Write Effective Descriptions

The description is the primary matching signal. A useful description answers two questions:

1. What does the Skill do?
2. When should Claude use it?

A vague description such as `Helps with documentation` does not provide enough information for reliable matching. A stronger description names the expected output and the requests that should activate it:

```yaml
description: Creates README files, API references, and code documentation. Use when writing or updating project documentation.
```

If a Skill does not activate when expected, compare the description with the language used in actual requests and add relevant terms without making the description so broad that it matches unrelated work.

## Pre-Approve Tools with `allowed-tools`

When a Skill repeatedly uses the same tools, `allowed-tools` can pre-approve them for the turn that activates the Skill. This avoids a separate permission prompt for every listed tool call.

`allowed-tools` does not restrict Claude to those tools. If the instructions require a tool that is not listed, Claude can still request it through the normal permission process. If the field is omitted, all tools continue to follow the normal permission settings.

Be cautious when pre-approving `Bash`, because an unrestricted entry authorizes shell commands generally. For a narrowly scoped Skill, prefer a command pattern when possible:

```yaml
allowed-tools: Read, Grep, Glob, Bash(git status *)
```

To prevent a Skill from using particular tools, Claude Code also supports `disallowed-tools`.

## Use Progressive Disclosure

When Claude activates a Skill, the contents of `SKILL.md` enter the context window. Placing every reference, example, and procedure in one large file consumes unnecessary context and makes the Skill difficult to maintain.

Progressive disclosure keeps the essential workflow in `SKILL.md` and moves specialized material into supporting files that Claude reads only when the current task requires it. A larger Skill can use this structure:

```text
codebase-onboarding/
├── SKILL.md
├── references/
│   ├── architecture-guide.md
│   └── deep-dive-guide.md
├── scripts/
└── assets/
```

- `references/` stores detailed documentation and examples.
- `scripts/` stores executable, repeatable operations.
- `assets/` stores images, templates, and other data files.

The main file should link to each supporting resource and explain when it should be loaded:

```markdown
## Architecture Overview

Only load this reference when the user requests more architectural detail. See [architecture-guide.md](references/architecture-guide.md).
```

![A multi-file Skill using progressive disclosure](Progressive%20Disclosure%20Structure.png)

As a practical guideline, keep `SKILL.md` under 500 lines. When it grows beyond that size, move task-specific details into focused reference files.

## Use Scripts Efficiently

A script can execute without loading its source code into the model context; only the command and its output need to be processed. Tell Claude to run the script rather than read it when the implementation itself is not relevant to the task.

Scripts are especially useful for:

- environment validation;
- consistent data transformations; and
- operations that are safer or more reliable as tested code than as newly generated code.

## Recap

- `name` and `description` are required; `allowed-tools` and `model` are optional.
- A reliable description explains both the capability and its activation conditions.
- `allowed-tools` pre-approves tools but does not remove access to other tools.
- Progressive disclosure keeps `SKILL.md` focused and loads supporting resources only when needed.
- Executing a script can preserve context because its source does not need to be loaded.

## Lesson Reflection

- How would you divide a multi-file Skill between `SKILL.md`, references, scripts, and assets?
- Which tools would you pre-approve for a shared team Skill, and which should continue to require confirmation?

## What's Next?

In the next lesson, you will compare Skills with `CLAUDE.md`, subagents, hooks, and MCP servers so that you can choose the appropriate mechanism for each use case.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=98KaK_rn5rQ)
