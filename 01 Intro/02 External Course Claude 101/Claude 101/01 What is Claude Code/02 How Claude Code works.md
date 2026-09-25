# How Claude Code Works

Claude Code is different from typical chat applications. Understanding how it works under the hood will help you use it more effectively.

## The Agentic Loop

Claude Code is best explained through the agentic loop:

1. You enter a prompt into Claude Code.
2. Claude gathers the context it needs by interacting with the model, which returns text or a tool call that Claude Code can execute.
3. Claude takes action, such as editing a file or running a command.
4. Claude verifies the results and determines whether they achieve the goal defined in your prompt.
5. If the goal has been achieved, Claude finishes and waits for the next prompt. Otherwise, it returns to the loop and tries again until the results are complete and verifiable.

Throughout the loop, you can add context, interrupt the process, or steer the model toward your goal.

![Claude Code agentic loop](Agentic%20Loop.png)

## Context

Claude has a context window that determines how much conversation history, file content, command output, and other information it can store and reference. When the context reaches its limit, Claude Code compacts the conversation by determining what it can remove or summarize to return the context window to a usable size.

## Tools

Tools are the backbone of how agents work. Most AI assistants take text as input and return text as output. Tools allow Claude Code to execute actions that move it closer to completing a task. These tools can read files, search the web, execute code, and provide other capabilities. Claude Code uses semantic understanding to decide when to call a tool and how to use its output.

## Permissions

Claude Code has several permission modes:

- **Default behavior:** Claude asks for explicit permission before editing a file or running a shell command.
- **Auto-accept:** Files are edited without asking, but commands still require approval.
- **Plan Mode:** Claude uses read-only tools to prepare a plan of action before starting any work.

![Claude Code command approval prompt](Claude%20Code%20Command%20Approval.png)

These behaviors can be configured in the settings file. Be cautious when skipping permissions: giving Claude Code unrestricted permission to run commands can make mistakes harder to catch before they happen.

## Recap

Claude Code combines an agentic loop, a managed context window, tools, and configurable permissions inside the terminal. It can read a codebase, take action, and verify its own work. This makes it fundamentally different from a chat window.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=6bs5b4FltCU)
