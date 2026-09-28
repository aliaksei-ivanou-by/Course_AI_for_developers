# Sharing Skills

Skills become more valuable when they are shared. A common Skill can standardize code reviews, documentation, security checks, and other recurring work across a project, team, or organization.

Claude Code supports three main distribution approaches: project repositories, plugins, and enterprise managed settings. Custom subagents can also be configured to load selected Skills for delegated work.

## Commit Project Skills to a Repository

The simplest way to share a project-specific Skill is to store it under `.claude/skills/` and commit it to the repository:

```text
.claude/
├── agents/
├── hooks/
├── skills/
│   └── pr-review/
│       └── SKILL.md
└── settings.json
```

Anyone who clones the repository receives the Skill without a separate installation step. Updates arrive through the team's normal Git pull workflow.

Repository-based Skills work well for:

- project-specific coding standards;
- workflows tied to the repository;
- guidance that references the codebase structure; and
- conventions that should evolve with the project.

## Distribute Skills Through Plugins

Plugins package Claude Code extensions for reuse across multiple repositories. A plugin can contain a `skills/` directory in which each Skill has its own folder and `SKILL.md` file.

After publishing the plugin through a marketplace, other users can discover and install it in Claude Code.

![Discovering plugins in the Claude Code marketplace](Claude%20Code%20Plugin%20Marketplace.png)

Plugins are appropriate when Skills are useful beyond one repository or immediate team. They provide a reusable distribution and update mechanism for a broader audience.

Before installing a third-party plugin, review its Skills, scripts, permissions, and external dependencies just as you would review other executable software.

## Deploy Skills Through Enterprise Managed Settings

Administrators can distribute Skills and plugins through managed organizational configuration. Enterprise Skills have the highest priority and override personal, project, or plugin Skills with the same name.

Managed settings can also restrict plugin installation to approved marketplaces. For example:

```json
{
  "strictKnownMarketplaces": [
    {
      "source": "github",
      "repo": "acme-corp/approved-plugins"
    },
    {
      "source": "npm",
      "package": "@acme-corp/compliance-plugins"
    }
  ]
}
```

![Approved plugin sources in enterprise managed settings](Enterprise%20Managed%20Plugin%20Settings.png)

Enterprise distribution is the appropriate choice for mandatory security rules, compliance workflows, and development standards that must remain consistent across the organization.

## Give Skills to Custom Subagents

Subagents start with separate contexts and do not automatically inherit the Skills available to the main conversation.

There are two important distinctions:

- Built-in agents cannot access Skills.
- Custom subagents can use Skills only when their frontmatter explicitly lists them.

Create a custom subagent under `.claude/agents/`. The `/agents` command can guide you through the process interactively.

![Creating a custom subagent with the agents command](Claude%20Code%20Custom%20Agent%20Creation.png)

The custom agent's frontmatter can specify the Skills that should be loaded:

```yaml
---
name: frontend-security-accessibility-reviewer
description: Use this agent to review frontend code for security and accessibility issues.
tools: Bash, Glob, Grep, Read, WebFetch, WebSearch, Skill
model: sonnet
color: blue
skills: accessibility-audit, performance-check
---
```

The named Skills must already exist in an available Skills directory. They are loaded when the custom subagent starts and apply throughout its work rather than being discovered on demand inside that subagent.

This pattern is useful when:

- delegated work needs isolated, specialized expertise;
- different subagents require different standards; or
- standards must apply consistently without being repeated in every delegation prompt.

## Choose a Distribution Method

| Method | Scope | Best suited for |
| --- | --- | --- |
| Project repository | One repository and its contributors | Project-specific workflows and standards |
| Plugin or marketplace | Multiple projects, teams, or community users | Reusable Skills with independent distribution |
| Enterprise managed settings | Entire organization | Mandatory security, compliance, and engineering standards |
| Custom subagent configuration | A delegated agent role | Loading selected expertise into isolated work |

These methods can be combined. For example, an organization can approve a plugin marketplace centrally, a team can install a shared plugin, and a custom review subagent can load selected Skills from it.

## Recap

- Commit project Skills under `.claude/skills/` to share them through Git.
- Use plugins to distribute reusable Skills across repositories.
- Use enterprise managed settings for mandatory organization-wide standards.
- Custom subagents require an explicit `skills` field.
- Skills listed for a custom subagent load when that subagent starts.

## Lesson Reflection

- Which distribution method best fits the Skills your team needs?
- Which delegated workflows would benefit from custom subagents with explicitly assigned Skills?

## What's Next?

In the final lesson, you will troubleshoot Skills that do not trigger or load correctly, naming conflicts, and script runtime errors.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=OCBi3eScNLk)
