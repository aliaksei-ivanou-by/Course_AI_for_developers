# Skills vs. Other Claude Code Features

Claude Code supports several customization mechanisms: Skills, `CLAUDE.md`, subagents, hooks, and MCP servers. They solve different problems and are most effective when combined deliberately rather than used interchangeably.

## `CLAUDE.md` vs. Skills

`CLAUDE.md` contains always-on instructions. Its contents enter every conversation, so it is appropriate for rules and context that should influence all work in the project.

Use `CLAUDE.md` for:

- project-wide standards;
- constraints such as “never modify the database schema”;
- framework preferences; and
- coding and formatting conventions.

Skills load on demand when Claude matches a request to a Skill description. They are appropriate for detailed knowledge that is relevant only to particular tasks.

Use Skills for:

- task-specific expertise;
- specialized knowledge needed only occasionally; and
- detailed procedures that would otherwise occupy every conversation's context.

![Comparison of CLAUDE.md and Skills](CLAUDE.md%20and%20Skills%20Comparison.png)

For example, a requirement to use TypeScript strict mode belongs in `CLAUDE.md`. A pull-request review checklist belongs in a Skill because it is needed only when reviewing changes.

## Skills vs. Subagents

A Skill adds instructions and knowledge to the current conversation. Claude continues working in the existing context with the newly loaded guidance.

A subagent receives a delegated task and works in a separate context. It can have different instructions and tool access, then return its result to the parent conversation.

Use a subagent when:

- the task should run in an isolated context;
- delegated work needs different tools or instructions; or
- intermediate details should not occupy the main conversation.

Use a Skill when the current conversation needs specialized knowledge or a repeatable procedure.

## Skills vs. Hooks

Hooks are event-driven. They run when configured Claude Code events occur—for example, before or after particular tool calls. A hook can validate an operation, run a formatter after a file edit, block an unsafe command, or send a notification.

Skills are request-driven. They activate when the user's request matches the Skill description and provide guidance that affects how Claude approaches the task.

Use hooks for deterministic operations that must run when a specific event occurs. Use Skills for knowledge, checklists, and reasoning procedures that should apply to matching requests.

## Skills vs. MCP Servers

MCP servers connect Claude Code to external tools, services, and data sources. They provide capabilities such as querying a company system, accessing current documentation, or interacting with an external API.

Skills tell Claude how to perform a type of work; MCP servers give Claude additional tools with which to perform it. A Skill can instruct Claude when and how to use tools exposed by an MCP server.

## Choose the Right Mechanism

| Mechanism | Activation | Primary purpose |
| --- | --- | --- |
| `CLAUDE.md` | Loaded in every conversation | Always-on project context and standards |
| Skills | Loaded when a request matches | Reusable task-specific expertise and procedures |
| Subagents | Started for delegated work | Isolated execution with a separate context |
| Hooks | Triggered by configured events | Deterministic validation, automation, and side effects |
| MCP servers | Tools called when needed | Access to external systems, services, and data |

## Combine the Features

A project can use all five mechanisms together:

- `CLAUDE.md` defines standards that always apply.
- Skills provide specialized procedures on demand.
- Hooks enforce deterministic checks around agent actions.
- Subagents handle isolated or delegated work.
- MCP servers connect the agent to external capabilities and information.

Choose each mechanism for its specialty. Avoid putting every instruction into a Skill when an always-on rule, isolated subagent, deterministic hook, or external tool would express the requirement more clearly.

## Recap

- Use `CLAUDE.md` for instructions that should always be present.
- Use Skills for knowledge that should load automatically only for relevant tasks.
- Use subagents for delegated work in separate contexts.
- Use hooks for event-driven automation and enforcement.
- Use MCP servers to provide external tools and integrations.
- Combine these features to create a complete customization strategy.

## Lesson Reflection

- Which instructions in your current `CLAUDE.md` would be better as on-demand Skills?
- Which combination of Skills, hooks, subagents, and MCP servers would address your team's most common workflow problems?

## What's Next?

In the next lesson, you will learn how to share Skills through repositories, plugins, custom subagents, and enterprise managed settings.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=IgNN4v0BJdU)
