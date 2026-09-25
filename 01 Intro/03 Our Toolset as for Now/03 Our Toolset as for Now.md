# Current Toolset for AI-Assisted Development

This lesson introduces the tools currently used in the course to accelerate AI-assisted software development. The focus is on practical developer tools that can work from the terminal, integrate with editors, write code, run tests, assist with pull requests, and support agentic workflows.

The core toolset consists of Claude Code, OpenAI Codex, and Google Antigravity. Each tool has its own interface, model selection, strengths, and usage limits. All three can act on a developer's behalf, so they must be used with the same care as any other tool that can run terminal commands and modify a codebase.

## Toolset at a Glance

| Tool | Main interfaces | Model options covered in this lesson | Notable characteristics |
| --- | --- | --- | --- |
| Claude Code | CLI and editor extension | Opus, Sonnet, and Haiku | An industry-leading reference point for features such as subagents, MCP, skills, and hooks |
| OpenAI Codex | CLI and VS Code extension | GPT-5.5, GPT-5.4, and GPT-5.4 mini | Strong terminal capabilities and generous usage limits for the price |
| Google Antigravity | CLI and its own VS Code-based IDE | Gemini 3.5 Flash, Gemini 3.1 Pro, Claude Sonnet, and Claude Opus | Google-backed agent environment with a free tier for Innowise users |

## Claude Code

Claude Code is one of the main tools used for AI-assisted development. It is available as a terminal or CLI tool and as an editor extension. Its interactive interface includes slash commands and a wide range of configuration options.

Claude Code supports Anthropic models such as Opus, Sonnet, and Haiku. The lesson also mentions Fable, a previously available model that was considered strong but is currently unavailable because of United States government security restrictions. Even without Fable, Claude Code remains one of the industry's leading AI-assisted development tools.

Claude Code is also important because Anthropic introduced or popularized several capabilities that now appear across the market, including:

- Subagents
- Model Context Protocol (MCP) support
- Agent skills
- Hooks
- Other configurable workflow features

Tools such as OpenAI Codex and Google Antigravity now follow many of the same patterns. Claude Code therefore serves both as a capable coding assistant and as a reference point for the design of modern AI development agents.

## OpenAI Codex

OpenAI Codex can be understood as ChatGPT in the terminal. It can write code, run tests, create or assist with pull requests, and perform many other command-line tasks.

This level of access makes Codex powerful, but it also requires caution. A command-line agent that can perform the same actions as a developer can also make mistakes at the same level of access. The same principle applies to Claude Code and Google Antigravity.

At the time covered by this lesson, Codex offers several model options:

- GPT-5.5 as the frontier model
- GPT-5.4 as an older and less expensive model
- GPT-5.4 mini as a faster and less expensive option

Codex can be customized through settings and configuration. Developers can configure elements such as the status line and use statistics commands to monitor their usage limits. This is useful because the remaining allowance determines how much work can realistically be completed during the day.

The same principle applies to the other tools: developers should understand their limits and select an appropriate tool and model for each task.

## Google Antigravity

Google Antigravity is another tool in the current AI-assisted development toolset. Google previously offered Gemini CLI, which has now been deprecated in favor of the newer Antigravity CLI.

Antigravity supports Google models such as Gemini 3.5 Flash and Gemini 3.1 Pro. It also provides access to Claude Sonnet and Claude Opus, although not to their latest versions. This is possible because Claude models run in Google Cloud and can therefore be offered through Google Antigravity.

Antigravity includes many of the same feature categories as Claude Code and Codex, including skills, subagents, and MCP support. These tools are becoming increasingly similar in terms of their available capabilities.

The quality of Antigravity is a matter of personal preference. The most useful way to evaluate it is to try it in real workflows and compare its behavior, output quality, and limits with the other tools.

Google Antigravity is also available on a free tier. Anyone with an Innowise account can access it and determine whether it fits their workflow.

## Comparing Usage Limits and Value

Usage limits are one of the main practical differences between these tools.

For a monthly cost of approximately $20, OpenAI Codex currently provides the most generous limits and more working capacity than Claude Code or Google Antigravity at the same price point.

Output quality is more subjective. Some developers prefer Claude Code, while others prefer Codex or Antigravity. The best choice depends on the task, model behavior, and individual workflow.

Limits matter in daily work. A tool may produce excellent results, but it may be less suitable for long or repeated development sessions if it reaches its allowance too quickly. Developers should monitor their remaining usage and understand how much work they can complete before a limit is reached.

## Working in VS Code

All three tools can be incorporated into a VS Code-based workflow.

- **Built-in terminal:** Developers can launch Codex, Claude Code, or Antigravity from the terminal in VS Code and let the agent work in the open project.
- **Editor extensions:** Claude Code and Codex are available as VS Code extensions, providing integrated side chats and extension-based workflows.
- **Multiple assistants:** GitHub Copilot, Codex, and Claude Code can all be available in the same editor, although the setup may need to be managed to avoid unnecessary duplication.
- **Antigravity IDE:** Antigravity has its own application and IDE. It resembles VS Code because it is a fork of VS Code, and it includes a built-in chat window for working with the Antigravity agent.

## Why Cursor and GitHub Copilot Are Not the Main Focus

Cursor and GitHub Copilot remain popular AI development tools, but they are not the primary focus of this lesson.

The main reason is the balance between price and usable output. Cursor is no longer as affordable as it was when it received more substantial subsidies, and its $20 plan does not provide as much working capacity as the tools covered here.

GitHub Copilot is also not central to this comparison because the lesson focuses on tools that currently provide more useful output for the same cost. Claude Code, OpenAI Codex, and Google Antigravity are treated as the main remaining options for the workflows discussed in the course.

This does not make Cursor or GitHub Copilot useless. Both remain widely used, but Claude Code, Codex, and Antigravity are the key tools for the current cost-to-performance comparison.

## Practical Guidance

When working with any terminal-based coding agent:

1. Remember that the agent may be able to perform many of the same actions as a developer using the CLI.
2. Review meaningful changes and commands carefully.
3. Monitor usage limits and remaining daily capacity.
4. Choose a model and tool that fit the task, budget, and preferred workflow.
5. Compare tools through real development work rather than relying only on feature lists.

## Key Takeaway

Claude Code, OpenAI Codex, and Google Antigravity form the core toolset presented in this lesson. Claude Code helped establish many modern agent features, Codex combines strong command-line capabilities with generous limits, and Antigravity offers a Google-backed agent environment with both Google and Claude models.

All three tools can accelerate software development, but they must be used carefully. Developers remain responsible for supervising their actions, reviewing results, monitoring limits, and selecting the right tool for each task. Future lessons will explore specific use cases and show how these tools can be applied in real development workflows.
