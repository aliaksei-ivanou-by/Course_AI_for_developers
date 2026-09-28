# What Are Skills?

Agent Skills let you teach Claude Code a reusable procedure once instead of repeating the same instructions in every conversation. A Skill can describe how to review a pull request, format a commit message, apply brand guidelines, create documentation, or follow a framework-specific debugging checklist.

## What Is an Agent Skill?

A Skill is a folder containing instructions and optional resources that Claude Code can discover and use for a particular type of task. Its main file is named `SKILL.md`.

Each `SKILL.md` file begins with YAML frontmatter containing a name and description:

```yaml
---
name: pr-review
description: Reviews pull requests for code quality. Use when reviewing PRs or checking code changes.
---
```

The rest of the file contains the task-specific instructions, such as a review checklist, output format, coding standard, or decision process.

![A PR review Skill stored in a project directory](Agent%20Skill%20Structure.png)

## How Claude Activates Skills

Claude Code initially receives the names and descriptions of the available Skills. When a request matches a description, Claude loads the relevant `SKILL.md` instructions and applies them to the task.

The description therefore controls discoverability. It should state both what the Skill does and the situations in which Claude should use it.

When Claude matches the `pr-review` Skill to a pull-request review request, the terminal shows that the Skill was loaded:

![Claude Code automatically loading the PR review Skill](Claude%20Code%20Skill%20Activation.png)

This on-demand loading is an example of progressive disclosure: detailed instructions enter the context only when they are needed.

## Where Skills Live

- **Personal Skills** are stored in `~/.claude/skills/`. They are available across projects on the same machine and are appropriate for personal preferences such as commit-message style or documentation format.
- **Project Skills** are stored in `.claude/skills/` at the repository root. They can be committed to version control and shared with everyone who works on the project.

On Windows, the personal directory is usually:

```text
C:/Users/<your-user>/.claude/skills/
```

## Skills vs. Other Customization Options

| Mechanism | How it is activated | Best suited for |
| --- | --- | --- |
| `CLAUDE.md` | Loaded into every conversation | Instructions that should always apply to the project |
| Skills | Loaded automatically when a request matches the Skill description | Specialized knowledge and repeatable task-specific procedures |
| Slash commands | Invoked explicitly by the user | Actions that the user wants to start manually |

For example, a requirement to always use TypeScript strict mode belongs in `CLAUDE.md`. A pull-request review checklist is better suited to a Skill because it is needed only during code review.

## When to Use Skills

Skills work well for repeatable, specialized tasks such as:

- code-review standards;
- commit-message conventions;
- organizational brand guidelines;
- documentation templates; and
- framework-specific debugging checklists.

A useful rule of thumb is: if you repeatedly explain the same task-specific instructions to Claude, those instructions may belong in a Skill.

## Recap

- A Skill is a folder of reusable instructions and resources centered on `SKILL.md`.
- The YAML frontmatter provides the Skill name and description.
- Claude uses the description to match Skills to requests and loads detailed instructions on demand.
- Personal Skills are available across projects; project Skills can be shared through version control.
- Skills are best for specialized procedures that should activate automatically only when relevant.

## Lesson Reflection

- Which instructions have you repeated in recent Claude Code conversations?
- Which team standards or processes would benefit from being encoded as project Skills?

## What's Next?

In the next lesson, you will create a Skill from scratch and examine how Claude Code discovers, matches, and loads it.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=bjdBVZa66oU)
