# RTK and Caveman: Reducing Agent Token Usage

AI coding sessions spend tokens in both directions: the agent reads prompts, files, tool schemas, and command output, then produces explanations, code, and tool calls. RTK and Caveman are third-party tools that reduce different parts of that traffic. They can improve efficiency, but compression is a lossy transformation unless the original data remains available. Adoption therefore requires workload-specific evaluation, privacy review, and an escape path to the full output.

> **Time-sensitive content:** The commands and capabilities below reflect the upstream projects in October 2026. Check their current documentation, release notes, license, and security policy before installation.

## Two Different Optimization Targets

| Tool | Primary target | Basic mechanism |
| --- | --- | --- |
| RTK (Rust Token Killer) | Input tokens from shell-command output | Intercepts or wraps supported commands and emits a condensed representation |
| Caveman response skill | Output tokens from agent prose | Instructs the agent to remove filler while preserving technical content |
| Caveman proxy/runtime | Input and context traffic as well as output | Compresses supported streams before they reach the provider and retains recovery mechanisms where configured |

The distinction matters. Shortening the agent's final explanation does not reduce a large test log already sent into the context. Conversely, filtering command output does not make the agent's prose concise.

## RTK

[RTK](https://github.com/rtk-ai/rtk) is a Rust CLI proxy for common development commands. It filters their output before an AI coding tool reads it. Examples include compacting `git status`, grouping search results by file, collapsing successful tests to counts, and retaining the relevant part of failures.

RTK can be invoked explicitly:

```text
rtk git status
rtk rg "pattern" src/
rtk cargo test
```

For supported agents, an initialization command installs integration that rewrites eligible shell calls automatically. The exact flag is agent-specific; for example, the upstream documentation lists:

```text
rtk init -g
rtk init -g --codex
rtk init --show
```

Inspect what the initializer will modify and use the current upstream instructions for the target agent. Hooks and configuration formats evolve.

### What RTK can preserve or lose

A good filter keeps failure locations, exit status, filenames, changed-file state, test counts, and a way to recover omitted details. It may intentionally remove repeated passing lines, progress bars, boilerplate, long unchanged diff context, or duplicated diagnostics.

That trade-off can hide a clue. A warning that looks repetitive may explain the failure; a trimmed stack trace may remove the first application frame; a grouped diff may conceal ordering. The current project can preserve full output for failed or truncated commands and return a recall handle. Verify this behavior in the installed version and use raw output whenever the condensed form is insufficient.

### Measuring RTK

The project reports large reductions for supported command output, but those percentages are not automatically equal to lower provider billing or a proportional decrease in total session tokens. Measure:

- original and condensed bytes or tokens for representative commands;
- whether every necessary diagnostic survives;
- how often the agent asks for the full output or reruns commands;
- end-to-end task success, latency, and provider-reported usage;
- failures on unsupported commands and unusual output formats.

## Caveman

[Caveman](https://github.com/JuliusBrussee/caveman) began as a terse response style and now includes a broader skill, CLI, proxy, and related compression components. The simplest form is a response skill that asks an agent to remove filler, hedging, pleasantries, and excess grammar while retaining code, commands, errors, and technical meaning.

The response skill primarily changes what the agent writes. This can make interactive explanations and handoffs shorter. Its benefit is smaller in coding sessions dominated by file content, tool calls, and logs. The project's own documentation distinguishes skill-only results from proxy results and recommends measuring the actual workload rather than treating a headline percentage as universal.

The broader Caveman tooling can also compress what an agent reads. That introduces stronger dependencies and a larger review surface than a Markdown response skill. Check exactly which component is being installed, which local files or hooks it changes, what traffic it proxies, how original content can be recovered, and whether telemetry is enabled.

### When terse output helps

- repetitive progress updates;
- routine command explanations;
- concise review findings;
- established teams that already understand the terminology;
- high-volume workflows where output verbosity is a measured cost.

### When terse output hurts

- security warnings and irreversible-action confirmations;
- onboarding and teaching;
- requirements with subtle exceptions;
- incident reports and handoffs that need causal detail;
- complex multi-step procedures where missing grammar creates ambiguity;
- regulated records that require complete reasoning and evidence.

A useful concise mode must relax when clarity is more important than token reduction.

## Security and Operational Review

Before installing either tool:

1. Read the repository, release, license, and security documentation.
2. Inspect installation scripts and the files, hooks, environment variables, or proxy settings they change.
3. Confirm where command output and prompts are processed and stored.
4. Review telemetry defaults and disable collection if organizational policy requires it.
5. Pin or control versions in managed environments.
6. Test uninstall and recovery before broad rollout.

A hook or proxy sits on a sensitive boundary. It can see commands, paths, logs, and possibly prompts or model traffic. Treat it as development infrastructure, not as a cosmetic prompt tweak.

## Evaluation Plan

Use paired tasks rather than a single impressive transcript:

1. Select representative repository tasks: search, test failure, review, refactor, and documentation.
2. Run a baseline without compression.
3. Run the same tasks with one component enabled at a time.
4. Compare provider-reported input and output tokens, cost, latency, task success, and human review time.
5. Inspect cases where details were omitted or the agent reran a command.
6. Keep the tool only where the savings exceed the added failure and maintenance cost.

Do not combine RTK, a terse skill, prompt caching, model routing, and context changes in the first experiment. Change one factor at a time so the result can be attributed.

## Choosing Between Them

- Use a terse response instruction or skill when generated prose is the measured source of waste.
- Use RTK when supported shell output dominates the context and raw details remain recoverable.
- Consider a broader proxy only after reviewing its trust boundary and demonstrating an end-to-end benefit.
- Use built-in bounded reads, targeted search, quiet test modes, and concise commands first when they already solve the problem.

The objective is not the highest compression ratio. It is the lowest total cost that preserves correct, reviewable work.

## Related Course Material

- [Context Windows, Caching, Cost, and Performance](../../04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md)
- [Reducing MCP Server and Tool Context Overhead](../../04%20Context%20Engineering/01%20General%20practices/06%20Reducing%20the%20number%20of%20MCP%20servers/06%20Reducing%20the%20number%20of%20MCP%20servers.md)
- [RTK repository](https://github.com/rtk-ai/rtk)
- [Caveman repository](https://github.com/JuliusBrussee/caveman)

