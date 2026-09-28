# Creating Your First Skill

This lesson walks through creating a personal Skill that teaches Claude Code to write pull-request descriptions in a consistent format. It also explains how Claude discovers Skills, matches them to requests, and resolves naming conflicts.

## Create the Skill Directory

Personal Skills are stored in `~/.claude/skills/` and are available across your projects. Create a directory whose name matches the Skill name:

```shell
mkdir -p ~/.claude/skills/pr-description
```

On Windows PowerShell, the equivalent command is:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills\pr-description"
```

Create a file named `SKILL.md` inside the new directory.

## Write the `SKILL.md` File

A Skill file has two parts:

1. YAML frontmatter containing metadata.
2. Markdown instructions that Claude follows after activating the Skill.

The following Skill asks Claude to inspect the current branch and produce a structured PR description:

```markdown
---
name: pr-description
description: Writes pull request descriptions. Use when creating a PR, writing a PR, or when the user asks to summarize changes for a pull request.
---

When writing a PR description:

1. Run `git diff main...HEAD` to see all changes on this branch.
2. Write a description following this format:

## What

One sentence explaining what this PR does.

## Why

Brief context on why this change is needed.

## Changes

- Bullet points of specific changes made
- Group related changes together
- Mention any files deleted or renamed
```

The `name` identifies the Skill. The `description` tells Claude when to use it and therefore acts as the matching criterion. Everything after the closing frontmatter delimiter contains the instructions Claude follows.

![A PR description Skill open in Visual Studio Code](PR%20Description%20Skill.png)

## Test the Skill

Claude Code discovers Skills when a session starts. Restart the session after creating the directory or editing its metadata, then check the available Skills list. The new `pr-description` Skill should appear with its description.

![The PR description Skill in the Claude Code available Skills list](Claude%20Code%20Available%20Skills.png)

To test it, make changes on a branch and ask:

```text
Write a PR description for my changes.
```

Claude should select the Skill, inspect the diff, and use the format defined in `SKILL.md`.

## How Skill Matching Works

At startup, Claude Code scans the available Skill locations but initially loads only each Skill's name and description. It does not place every complete `SKILL.md` file into the context window.

When you submit a request, Claude compares its meaning with the available descriptions. If the intent matches a Skill, Claude asks for confirmation before loading the complete instructions into context.

![Confirmation before Claude loads a matching Skill](Skill%20Loading%20Confirmation.png)

Clear descriptions improve matching. Describe both the capability and the situations that should activate it rather than using a vague label such as “helps with code.”

## Skill Priority

When multiple Skills have the same name, Claude Code uses the following priority order:

| Priority | Source | Typical location or purpose |
| --- | --- | --- |
| 1 | Enterprise | Centrally managed organizational settings |
| 2 | Personal | `~/.claude/skills/` |
| 3 | Project | `.claude/skills/` in the repository |
| 4 | Plugins | Skills installed through plugins |

For example, an enterprise `code-review` Skill takes precedence over personal, project, or plugin Skills with the same name. Use descriptive names such as `frontend-review` or `backend-review` to reduce accidental conflicts.

## Update or Remove a Skill

- To update a Skill, edit its `SKILL.md` file.
- To remove a Skill, delete its directory.
- Restart Claude Code after making changes so that the available Skill metadata is refreshed.

## Recap

- A Skill is a directory containing a `SKILL.md` file.
- YAML frontmatter defines its name and matching description.
- Claude initially loads only Skill metadata and loads full instructions after finding a match.
- Enterprise Skills have the highest priority, followed by personal, project, and plugin Skills.
- Restart Claude Code after adding, changing, or removing a Skill.

## Lesson Reflection

- Which recurring task in your workflow could become a Skill, and what description would make it discoverable?
- How should your team divide Skills between personal, project, and enterprise scopes?

## What's Next?

In the next lesson, you will explore additional metadata, tool restrictions with `allowed-tools`, and multi-file organization through progressive disclosure.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=Wx6_vjFFyHM)
