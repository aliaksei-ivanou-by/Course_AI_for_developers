# Reducing MCP Server and Tool Context Overhead

Model Context Protocol (MCP) gives an AI agent a standardized way to discover and call external tools. A server can expose code search, documentation retrieval, browser automation, issue tracking, repository operations, databases, and many other capabilities.

That flexibility is valuable, but each integration has a cost. Depending on the agent runtime and configuration, the model may receive server descriptions, tool descriptions, input schemas, and instructions before it uses any tool. Tool results then add more context during execution. Connecting every available server “just in case” can therefore increase token use, latency, and tool-selection difficulty.

The objective is not to eliminate MCP. It is to expose the smallest useful tool surface for the current task and choose MCP, a CLI, a native tool, or a hybrid architecture according to the job.

> **Core principle:** Make capabilities available when they are needed, not merely because they exist.

## What an MCP Integration Can Add to Context

An MCP connection may contribute several kinds of information:

- The server name and a high-level description
- Tool names and descriptions
- Input schemas, parameter descriptions, and examples
- Server or tool instructions
- Resource and prompt metadata
- Tool-call arguments and returned results
- Errors, logs, and retry output

The exact behavior depends on the client, model, provider, server, and configuration. Two distinctions are especially important.

### Connected Does Not Always Mean Fully Loaded

Some clients load every tool definition eagerly. Others support deferred loading or tool search: the model initially sees only enough information to discover a relevant tool, and the complete schema is added later if that tool is selected.

OpenAI's tool-search documentation describes this as dynamic loading of deferred tools. The model can begin with a server or namespace description instead of every individual definition. Anthropic also documents deferred loading and tool search for supported tool configurations.

Therefore, the statement “every connected MCP server always puts all its tools into every prompt” is too broad. It can be true for an eager-loading setup, but it is not a universal property of MCP.

### Tool Metadata and Tool Results Are Different Costs

Tool metadata is the information the model needs to understand how a tool works. Tool results are the files, records, logs, or other data returned after a call. Optimizing only the initial tool list is not enough if a selected tool later returns thousands of irrelevant lines.

```text
total tool-related context
    ≈ discovery metadata
    + loaded tool definitions
    + call arguments
    + returned results
    + retained tool history
```

This is a conceptual model, not a billing formula. Prompt caching, context compaction, provider pricing, and agent-runtime behavior affect the actual cost.

## Do Not Treat Character Counts as Token Counts

A description containing 2,000 characters does not necessarily consume 2,000 tokens. Tokenization depends on the model and the text. Likewise, observations such as “this server added 1,000 tokens,” “the initial context was 50,000 tokens,” or “built-in tools use 15,000 tokens” describe one environment at one point in time, not constants that apply to every agent.

When evaluating an integration, measure the selected runtime directly:

1. Record the baseline context, latency, and cost without the integration.
2. Enable the server or toolset.
3. Repeat representative tasks with the same model and inputs.
4. Compare task success, tool-selection accuracy, context use, latency, and cost.
5. Recheck after product or configuration changes.

Optimize for reliable task completion, not for the smallest token counter in isolation.

## Eager Loading, Deferred Loading, and Allowlists

There is no single best loading strategy.

| Strategy | Good fit | Main trade-off |
| --- | --- | --- |
| Eager definitions | A small set of tools used frequently | Immediate availability, but definitions occupy the initial context |
| Deferred tools or tool search | A large catalog where each task needs only a few tools | Lower baseline context, but discovery adds a step and can select poorly if descriptions are vague |
| Tool allowlist | A broad server whose current task needs a known subset | Predictable surface, but the list must be maintained |
| Project-specific server profile | Different repositories need different integrations | Strong isolation, but configuration becomes project-specific |
| Disable until needed | Rare, expensive, or privileged integrations | Minimal default surface, but activation interrupts the workflow |

For deferred discovery to work well, the high-level server and tool descriptions still need to be clear. A description such as “miscellaneous utilities” gives the model little basis for finding the right capability.

## MCP, CLI, or Native Tool?

The public Google for Developers video linked with this lesson compares two common approaches.

### CLI

A command-line interface is a direct invocation:

```text
agent → command + arguments → stdout/stderr + exit code
```

A CLI is attractive when:

- A mature command already exists.
- The operation is stable and called in a predictable way.
- The command can return concise, machine-readable output such as JSON.
- Local scripting and shell composition are useful.
- Dynamic discovery is unnecessary.

A CLI can reduce upfront schema exposure, but it does not make context free. The agent still needs instructions for choosing and invoking the command, and the command's output enters the working context. Verbose help text, fragile parsing, shell quoting, unrestricted commands, and credential leakage can create new reliability and security problems.

### MCP

MCP adds a protocol layer through which an agent can discover structured tools and understand their inputs. It is attractive when:

- Tools must be discovered dynamically.
- Typed schemas reduce ambiguity.
- One integration should work across compatible clients.
- A remote service needs structured authentication or lifecycle handling.
- Many tools must be organized under one server.
- Other agents or users need to discover the same capabilities.

The schema and discovery layer creates overhead, but it can also prevent invalid calls and reduce custom glue code. With deferred loading, a large MCP catalog does not necessarily have to occupy the initial context.

### Native Function or Product Integration

When the application owner controls both the agent and the service, a small native tool can be simpler than either a generic CLI wrapper or a complete MCP server. This can be a good fit for a narrow, stable operation, but it sacrifices MCP's portability.

### Hybrid Is Normal

The Google video offers a useful starting heuristic:

- If the agent is acting much like a developer at a terminal, a CLI may be sufficient.
- If it must discover capabilities and act through a reusable integration on behalf of users or other agents, MCP may be preferable.

This is not a law. A practical agent can use local CLIs for build and repository operations, MCP for remote business systems, and native tools for product-specific actions.

> **Decision question from the video:** Does the capability need discovery, or is direct invocation enough?

## CLI Does Not Automatically Replace MCP

Converting an MCP server into a command-line interface can move the server's detailed schemas out of the model's always-loaded context. It does not remove the underlying server, permissions, authentication, network calls, or operational risks. It also replaces typed protocol interaction with command construction and output parsing.

Compare end-to-end behavior:

| Concern | CLI | MCP |
| --- | --- | --- |
| Upfront definitions | Often small if instructions are concise | Can be large when eagerly loaded; smaller with deferred loading |
| Discovery | Help text, documentation, or agent skill | Standardized tool discovery and schemas |
| Output | Text or JSON chosen by the CLI | Structured tool result, depending on implementation |
| Portability | Broad terminal availability | Broad availability across compatible MCP clients |
| Composition | Strong shell and scripting ecosystem | Structured calls orchestrated by the agent runtime |
| Safety risks | Shell injection, broad executable access, leaked environment data | Malicious servers, prompt injection, broad permissions, unsafe side effects |
| Best case | Stable direct operation with reliable machine-readable output | Discoverable integration with typed operations and controlled permissions |

Choose the interface that improves correctness and maintainability for representative tasks. “CLI is always lighter” and “MCP is always better structured” are both incomplete rules.

## Skills as a Progressive-Disclosure Layer

Agent skills can teach a model when and how to use a CLI or another capability without loading the full instructions at all times. In OpenAI's skills model, discovery begins with a skill's name and description; the full `SKILL.md` and supporting resources are loaded only when the skill is selected.

```text
short skill metadata
        ↓ selected when relevant
full operating instructions
        ↓ invoked when needed
CLI, script, API, or other tool
```

This progressive-disclosure pattern is useful, but skill quality matters. A vague summary may never be selected, while an overly broad skill may activate too often. Skills can also contain privileged instructions or executable code, so third-party packages must be reviewed before use.

## Examples: Context7 CLI and MCPorter

The lesson transcript refers to two tools that illustrate the CLI approach.

### Context7

Context7 supports both MCP and a CLI-plus-skills workflow. Its current CLI is named `ctx7`. The project documentation shows commands such as:

```bash
ctx7 library react "server components"
ctx7 docs /facebook/react "server components"
```

The appropriate mode depends on the client and task. An existing `ctx7` command can be economical for direct documentation queries, while the MCP integration may be more convenient when the agent benefits from structured discovery.

### MCPorter

The tool mentioned in the transcript as “MCorter” is **MCPorter**. It is a third-party TypeScript runtime and CLI that can discover and call configured MCP servers from a terminal. It can also generate a standalone CLI for a server.

That can let an agent reach an MCP-backed capability through concise command instructions instead of keeping all server tool schemas loaded. It should be treated as an architectural adapter, not as a universal performance or security fix. Review the project, generated interface, credentials, permissions, output format, and maintenance implications before adoption.

## Build a Task-Specific Tool Profile

A minimal setup should reflect the actual objective rather than one person's permanent list of favorite servers.

| Task | Likely useful capabilities | Often unnecessary |
| --- | --- | --- |
| Local backend defect | Repository search, filesystem access, test runner, relevant documentation | Browser automation, design tools, unrelated SaaS integrations |
| Frontend interaction defect | Repository search, browser automation, screenshots, framework docs | Database administration or issue trackers if not part of the task |
| Pull-request maintenance | Git and repository host tools | Full browser automation and unrelated documentation servers |
| Jira or Confluence workflow | Relevant Atlassian integration with narrow permissions | Code indexing when no repository work is required |
| Library migration | Code search, tests, current official documentation | Broad remote-service integrations |

Codebase indexing can be useful on large or semantically complex repositories, but it is not mandatory for every task. Built-in filesystem search and tools such as `rg` may be sufficient. Similarly, current documentation can come from an official website, a documentation CLI, an MCP server, or a cached local source. Select the least complex option that remains accurate and convenient.

## Practical Optimization Workflow

### 1. Inventory the Current Surface

List each connected server, the tools it exposes, why the current task needs them, and their access level. Remove “maybe useful someday” from the default profile.

### 2. Start with the Task, Not the Tool

Write the objective and expected actions first. Enable only the integrations required to inspect evidence, change state, and validate the result.

### 3. Prefer Deferred Loading for Large Catalogs

If the client supports tool search or deferred loading, use it for large servers from which a typical task selects only a few operations. Keep a small, frequently used toolset eager when immediate availability is more valuable than the metadata cost.

### 4. Restrict Broad Servers

Use per-tool enablement, allowlists, project profiles, or narrowly scoped server configurations. A repository task rarely needs every operation from a large Git hosting or project-management integration.

### 5. Bound Tool Results

Use filters, pagination, line limits, date ranges, field selection, and summaries. Returning one precise record is often more useful than returning an entire issue history or thousands of log lines.

### 6. Choose CLI When Direct Invocation Is Better

Prefer an established CLI when the operation is stable and its output is reliable. Request machine-readable output when available and expose only approved commands rather than unrestricted shell access.

### 7. Keep Descriptions Concise but Complete

Remove redundant prose, not semantics. Tool descriptions must still explain when the tool should be used, required inputs, important side effects, and safety boundaries.

### 8. Measure End-to-End Results

Compare completed-task quality, invalid calls, repair turns, latency, token use, and cost. A smaller prompt that causes repeated failures is not an optimization.

## Security and Trust Boundaries

Reducing context does not reduce the need for security review. MCP servers, CLIs, and skills can all perform privileged work.

Use the following controls:

- Install tools only from trusted or internally reviewed sources.
- Grant the minimum repository, filesystem, network, and account permissions.
- Separate read-only discovery from state-changing operations.
- Require confirmation for destructive, financial, publishing, or externally visible actions.
- Avoid placing secrets in prompts, command arguments, logs, or tool results.
- Treat remote content and tool output as untrusted data that may contain prompt injection.
- Pin or review versions where supply-chain risk matters.
- Audit generated wrappers and skill instructions before execution.

A smaller tool list improves inspectability, but least privilege and explicit action boundaries remain essential.

## Common Mistakes

- Enabling every available MCP server for every project
- Assuming every connected server eagerly loads all tool schemas
- Assuming deferred loading is supported in every client and configuration
- Treating characters, tokens, cached tokens, and billed tokens as equivalent
- Repeating one observed context count as a universal constant
- Optimizing definitions while allowing unbounded tool results
- Replacing a structured MCP tool with a CLI that produces ambiguous text
- Letting the agent execute an unrestricted shell merely to avoid MCP metadata
- Using short descriptions that omit side effects or required parameters
- Treating MCPorter as a way to remove the underlying trust boundary
- Installing third-party skills or CLIs without reviewing their instructions and permissions
- Disabling a necessary tool and forcing the model to guess instead

## Recommended Decision Process

```text
define the task and required capabilities
                  ↓
does a reliable direct CLI or native tool already exist?
        ┌─────────┴─────────┐
       yes                  no
        ↓                    ↓
does the task need       use or build a structured
dynamic discovery?      integration when justified
   ┌────┴────┐
  no        yes
   ↓          ↓
use CLI   consider MCP
or native with deferred loading
   └────┬─────┘
        ↓
restrict permissions and result size
        ↓
measure correctness, latency, context, and cost
```

The result may be a hybrid rather than one permanent answer.

## Key Takeaway

MCP server count is only a proxy for the real concern: how much tool metadata and output enters the working context, when it is loaded, and whether it helps the task. Keep the active capability surface focused, use deferred discovery for large catalogs when the runtime supports it, limit tool results, and consider a CLI or native tool for stable direct operations. MCP remains valuable when structured discovery, portability, and reusable integrations justify the protocol layer. Choose with measurements and security boundaries, not with a blanket rule that one interface must replace the other.

## Public Video and Further Reading

- [Google for Developers: CLI or MCP? How should AI agents interact with external tools?](https://www.youtube.com/watch?v=7UOxdg6hUT8)
- [OpenAI: Tool search](https://developers.openai.com/api/docs/guides/tools-tool-search)
- [OpenAI: Skills](https://developers.openai.com/api/docs/guides/tools-skills)
- [Anthropic: Manage tool context](https://platform.claude.com/docs/en/agents-and-tools/tool-use/manage-tool-context)
- [Anthropic: Tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)
- [Context7 documentation: CLI](https://context7.com/docs/clients/cli)
- [Context7 source repository](https://github.com/upstash/context7)
- [MCPorter source repository](https://github.com/openclaw/mcporter)
