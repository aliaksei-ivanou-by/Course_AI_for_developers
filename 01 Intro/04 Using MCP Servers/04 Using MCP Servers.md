# Using Model Context Protocol Servers with AI Agents

Model Context Protocol (MCP) extends AI agents with additional tools through a standardized interface. Instead of building a separate custom integration for every tool and teaching the agent how to use it, an MCP server exposes capabilities with clear descriptions and usage patterns.

![Model Context Protocol explained in three levels](Model%20Context%20Protocol%20Explained.png)

*Source and further reading: [Model Context Protocol Explained in 3 Levels of Difficulty](https://machinelearningmastery.com/model-context-protocol-explained-in-3-levels-of-difficulty/)*

## What MCP Servers Add to AI Agents

MCP is useful when an AI agent needs to work with external systems, developer tools, documentation, design platforms, testing tools, or project infrastructure. Once an MCP server is connected to a session, the agent can call its tools directly and perform tasks beyond the model's built-in knowledge and capabilities.

For example, an agent might use an MCP server to:

- Interact with GitHub
- Look up current documentation
- Work with a database backend
- Connect to a design platform
- Run browser tests

The MCP server acts as a trusted extension point between the agent and these external capabilities.

## Official and Custom MCP Servers

There are two main ways to obtain an MCP server.

### Official MCP Servers

Trusted companies provide official MCP servers for their products. Examples include Microsoft, GitHub, Atlassian, Figma, and Supabase. Official servers are usually the safest and most reliable choice when connecting an agent to important systems.

### Custom MCP Servers

When no official server exists, developers can create their own. AI can help generate the required code, making it possible to build an integration for a private workflow or internal tool instead of depending on an unknown third-party repository.

A custom server provides both flexibility and a potential security advantage: the organization controls the code, behavior, and exact tools exposed to the agent.

## Why Official MCP Servers Are Recommended

An AI agent generally treats a connected MCP server as trusted because the user chose to connect it. If that server exposes dangerous, unexpected, or malicious commands, the agent may call them while completing a task.

> **Security rule:** Prefer official MCP servers whenever they are available. Use only approved or internally reviewed alternatives for important work.

Examples include:

- Use GitHub's official MCP server for GitHub operations.
- Use Microsoft's Playwright MCP server for browser testing.
- Use Figma's official MCP server for design and frontend workflows.

An MCP server from an unknown developer may appear useful but can contain behavior that is difficult to inspect, unsafe, or intentionally malicious. Unknown third-party servers should therefore be avoided for sensitive work.

## Useful MCP Servers for AI-Assisted Development

| MCP server | Typical use |
| --- | --- |
| GitHub | Working with repositories, project data, issues, and other GitHub functionality |
| Playwright | Browser testing and web automation through a structured tool interface |
| Context7 | Retrieving current code documentation instead of relying only on model training data |
| Figma | Providing design context for frontend implementation and design-related work |
| Supabase | Configuring, debugging, building, and migrating projects that depend on Supabase |

### GitHub MCP

A GitHub MCP server lets an agent interact with GitHub functionality through a tool interface. It is useful when the agent needs to work with repositories, project data, issues, or related features. The recommended choice is the official GitHub-provided server.

### Playwright MCP

Playwright supports browser testing and web automation. Connecting it through Microsoft's official MCP server gives an agent a structured way to use these capabilities without requiring a completely custom integration.

### Context7 MCP

Context7 gives AI agents access to current code documentation. This matters because model training data may be months or years old, which can lead to deprecated APIs, outdated patterns, or examples that no longer work.

With Context7, an agent can consult current guidance before generating code or recommendations. This is especially valuable for fast-moving libraries, frameworks, cloud tools, and infrastructure technologies such as Terraform.

### Figma MCP

Figma's MCP server can support designers and frontend developers. It supplies design context that helps an agent understand layouts, design systems, and implementation requirements while building or adjusting a frontend application.

### Supabase MCP

Supabase MCP is useful when an agent needs to configure Supabase, diagnose Supabase-related problems, or build a new project that depends on it.

It can also assist with migrations. For example, a project created with Lovable may depend on Supabase. Moving that project to an independent cloud provider can introduce configuration and debugging challenges. Giving the agent access to Supabase operations through MCP can accelerate this work.

## Configuring an AI Agent to Use an MCP Server

Each MCP server normally provides its own setup instructions. The exact configuration depends on both the server and the AI agent.

A typical setup process is:

1. Open the MCP server's official website or documentation.
2. Find the installation or setup section.
3. Select the instructions for the AI agent being used.
4. Add the server with the provided command or edit the agent's configuration file.
5. Confirm that the server is available in the agent session.

For example, Context7 provides a unified setup command:

```bash
npx ctx7 setup
```

Some servers also provide manual configuration for multiple agents. With Claude Code, setup may involve the `claude mcp add` command, selecting a scope, and supplying the options required by the server. Another option is to edit the agent's JSON configuration directly.

The general pattern is consistent: follow the MCP server's instructions and configure the AI agent to connect to that server.

## Security Rules for MCP Usage

Security is part of MCP setup, not an afterthought. Because an agent trusts the connected servers, each integration must be evaluated before use.

Follow these practical rules:

1. Prefer official MCP servers.
2. Use only approved or internally reviewed servers for company work.
3. Avoid repositories from unknown developers when sensitive systems or data are involved.
4. Build a custom MCP server when no trusted option exists and the integration is necessary.
5. Review the tools and commands exposed by a server before granting access.
6. Treat MCP servers as approved software and maintain an organizational allowlist.

For example, suppose an agent needs to access Google Drive, but no official server is available and the only option is an unknown hobbyist repository. The safer choice is not to use that repository. A custom MCP server is preferable because its code can be inspected and the exposed tools can be controlled.

Organizations should manage MCP servers in the same way they manage other approved software. An allowlist helps prevent employees from connecting agents to unknown tools that could expose company data or enable unsafe actions.

## Confirming That an MCP Server Is Being Used

An agent may call tools from a connected MCP server whenever they are relevant to a task. To observe this behavior clearly, explicitly ask the agent to use a particular server.

For example, ask an agent connected to Context7 to check the Terraform documentation through Context7. The workflow may look like this:

1. The agent calls a Context7 tool to resolve the Terraform library ID.
2. Context7 identifies the appropriate documentation source.
3. The agent queries that source for relevant documentation or examples.
4. The retrieved information is used to produce a more current answer or code sample.

This demonstrates the practical value of MCP: the agent can retrieve relevant information during the development workflow instead of relying solely on its training data.

## Why Current Documentation Matters

AI models may not know the latest versions of libraries, frameworks, or tools. In software development, this can produce deprecated APIs, invalid configuration syntax, outdated implementation patterns, or examples that no longer work.

Documentation tools such as Context7 address this limitation by letting the agent retrieve current documentation when it needs it. This is especially useful in development environments where frameworks, cloud tooling, and library APIs change frequently.

## Moving Beyond Introductory MCP Usage

The basic MCP workflow is straightforward: choose a trusted server, connect it to the agent, and allow the agent to use its tools when needed.

More advanced topics include building custom MCP servers and designing tool interfaces for specific workplace requirements. Anthropic documentation and Anthropic Skilljar courses provide introductory and advanced learning paths for developers who want to create their own MCP servers.

## Key Takeaway

MCP can significantly expand an AI agent's capabilities by connecting it to tools, documentation, and external systems through a standard interface. Its value depends on trust: connected servers must be official, approved, or carefully reviewed. Used responsibly, MCP can accelerate AI-assisted development while keeping integrations understandable and controlled.
