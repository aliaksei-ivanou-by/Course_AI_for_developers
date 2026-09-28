# What Are Subagents?

Subagents are specialized assistants to which Claude Code can delegate focused tasks. Each subagent works in a separate conversation context, performs the assigned work independently, and returns a concise result to the main conversation.

The file reads, searches, tool calls, and other intermediate details remain inside the subagent's context rather than filling the main context window.

## Why Subagents Matter

Every message and tool result added to a Claude Code conversation consumes part of its context window. Large searches, extensive logs, and the contents of many files can make a long-running conversation noisy and push relevant earlier information out of focus.

A subagent isolates that temporary work. It receives:

1. A system prompt that defines its role and behavior.
2. A task description created by the parent agent from the user's request.

The subagent then reads files, searches the codebase, runs permitted tools, and completes the assigned task in its own context. The main conversation receives the final result or summary without all the intermediate material.

This approach provides context efficiency, but it also introduces a tradeoff: the main conversation has less visibility into the detailed path the subagent followed. A useful subagent should therefore report evidence, assumptions, limitations, and unresolved obstacles clearly.

## A Practical Example

Suppose you need to identify which service handles refunds in an unfamiliar codebase.

Without a subagent, the main conversation might read many files, run searches, and trace several function calls. All those results remain in the main context even though the final answer may be only one or two paragraphs.

With a subagent, Claude delegates the investigation to an isolated worker. The subagent explores the codebase and returns a focused answer identifying the relevant service and supporting evidence. The main context retains the question and the useful result rather than the entire search process.

## Built-In Subagents

Claude Code includes built-in subagents for common types of work:

| Subagent | Primary purpose |
| --- | --- |
| General-purpose | Multi-step tasks that require both exploration and action |
| Explore | Fast codebase searching and navigation |
| Plan | Research and analysis performed while preparing a plan |

Claude Code can select these helpers automatically when a task matches their purpose.

## Custom Subagents

You can also create custom subagents with specialized system prompts, model settings, and tool access. Examples include:

- a code reviewer;
- a test writer;
- a documentation generator;
- a security analyst; or
- a project-specific research assistant.

A focused definition makes the subagent more predictable and helps the parent agent decide when delegation is appropriate.

## When Subagents Help

Subagents are especially useful when a task:

- produces large amounts of temporary search output;
- can be separated cleanly from the main objective;
- requires specialized instructions or restricted tools;
- can run independently or in parallel with other work; or
- needs only a concise result returned to the parent conversation.

Delegation is less useful for a tiny task that the main agent can complete directly with little context overhead.

## Recap

- Subagents perform focused work in separate context windows.
- The parent provides a task description, while the subagent's configuration defines its role and capabilities.
- Intermediate exploration remains isolated from the main conversation.
- The parent receives a concise result or summary.
- Built-in subagents cover common workflows, while custom subagents support specialized roles.
- Isolation saves context but makes clear evidence and obstacle reporting important.

## Lesson Reflection

- Which tasks in your current workflow generate large amounts of temporary context?
- Which of those tasks could be delegated without losing information needed by the main conversation?

## What's Next?

In the next lesson, you will create a custom subagent and configure its scope, description, tools, model, and system prompt.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=jKErNxuxPXg)
