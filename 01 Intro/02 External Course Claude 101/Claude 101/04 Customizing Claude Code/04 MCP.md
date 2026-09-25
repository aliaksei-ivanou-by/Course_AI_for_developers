# Model Context Protocol (MCP)

Model Context Protocol (MCP) is an open standard that lets Claude Code connect to external tools and data sources. Claude can determine when to use these tools to handle a request more effectively.

Much of a project's context may live outside the codebase in databases, productivity applications, or public repositories. MCP connects Claude Code to those sources.

## What Can You Do with MCP?

Tools give agents such as Claude Code the ability to perform actions instead of returning only text.

For example, a Linear MCP server can retrieve the details of project-management issues directly from Linear.

![Using a Linear MCP tool](Linear%20MCP%20Tool%20Call.png)

A documentation server such as Context7 can provide current documentation for project dependencies.

![Looking up documentation through Context7 MCP](Context7%20MCP%20Documentation%20Lookup.png)

## Adding an MCP Server

Add MCP servers with the `claude mcp add` command. Two main server types are supported:

- **HTTP servers:** remote services hosted by a provider and accessed over the network.

![Adding an HTTP MCP server](Add%20HTTP%20MCP%20Server.png)

- **Stdio servers:** local processes that run on the user's machine.

![Adding a stdio MCP server](Add%20Stdio%20MCP%20Server.png)

Use `/mcp` within a Claude Code session to view connected servers, check their status, and disable servers that are not needed.

![MCP server list](MCP%20Server%20List.png)

## Server Scope

MCP servers support three scopes:

- **Local:** available only in the current project and only to the current user.
- **User:** available to the user across all projects.
- **Project:** configured through a `.mcp.json` file committed to version control so everyone working on the codebase receives the same server configuration.

## Context Costs

MCP servers add their tool definitions to the context window even when the tools are not actively used. Use `/mcp` to inspect the configuration and disable servers unrelated to the current task.

![MCP server details](MCP%20Server%20Details.png)

When a tool has a command-line equivalent, such as `gh` for GitHub or `aws` for AWS, the CLI may be more context-efficient because it does not add persistent tool definitions.

A skill may also be a better option. Only the skill's name and description are initially placed in context; Claude loads the full contents when the skill is needed.

If MCP tools consume more than 10% of the context window, Claude Code automatically switches to tool-search mode and discovers tools on demand. This mode may be less reliable.

## Recap

MCP connects Claude Code to external tools and data. Add servers with `claude mcp add`, use `.mcp.json` for a shared project configuration, and disable unused servers to control context consumption.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=kkBFmwkDzdo)
