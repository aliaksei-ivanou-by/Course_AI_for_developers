# Context Management

Context is Claude's working memory. Every file it reads, command it runs, and message you send consumes space in the context window.

## What Is the Context Window?

The context window is the amount of information Claude can hold in memory. Prompts, file content, tool calls, and tool results all add to it. Because the available space is finite, it is important to manage it efficiently.

![Claude Code context window diagram](Context%20Window%20Diagram.png)

## What Happens When Context Fills Up?

When the context approaches its limit, Claude Code automatically compacts it. Compaction summarizes important details and removes unnecessary tool results to free space. This process can potentially lose details.

![Automatic context compaction](Automatic%20Context%20Compaction.png)

After compaction, Claude continues the session using a summary of the earlier conversation.

![Compact summary in Claude Code](Compact%20Summary.png)

## Context Commands

### `/compact`

Run `/compact` to compact the conversation manually. The command summarizes everything up to that point and frees context space while preserving a memory of the previous work.

![Manual compact command](Compact%20Command.png)

### `/clear`

Run `/clear` to remove the current conversation and start with no memory of the previous session.

![Clear context command](Clear%20Command.png)

### `/context`

Run `/context` to inspect the current context state. The command shows the context size, the categories consuming the most space, and a visual breakdown of usage.

![Context usage breakdown](Context%20Usage%20Breakdown.png)

## When to Use Each Command

- Use `/compact` when working on a specific feature and approaching the context limit but needing to continue. Keep the remaining context relevant to the current feature.
- Use `/clear` before starting a new feature so that the previous conversation does not introduce irrelevant bias.
- Store information that Claude should remember across sessions in `CLAUDE.md` so it does not need to rediscover it.

![Persistent project instructions in CLAUDE.md](CLAUDE.md%20Persistent%20Instructions.png)

## Tips for Saving Context Space

1. **Be specific.** A vague prompt may look shorter, but it often consumes more context because Claude must explore the codebase and infer the intended result. Clear instructions reduce unnecessary work.
2. **Manage MCP servers.** MCP servers load their available tools into context even when they are not being used. Disable servers unrelated to the current project. Skills can provide similar capabilities without loading everything into context in advance.
3. **Use subagents.** Subagents have separate context windows. For tasks where you only need the result—such as locating authentication endpoints—a subagent can perform the investigation and return a concise summary to the main agent.

## Recap

Effective context management is essential when using Claude Code. Use `/compact` to summarize long sessions, `/clear` to start fresh, and `/context` to inspect usage. Write specific prompts and delegate isolated research tasks to subagents to keep the primary context focused.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=eW3oTyfeWZ0)
