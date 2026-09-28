# Task Master AI

**Sources:**

- Course lesson: Task Master AI overview (private video, approximately 16 minutes)
- [Task Master AI repository](https://github.com/eyaltoledano/claude-task-master)
- [Task Master documentation](https://docs.task-master.dev/)
- [Hamster](https://tryhamster.com/)
- [OpenRouter documentation](https://openrouter.ai/docs/quickstart)

Task Master AI is a task-management layer for AI-assisted development. It converts a product requirements document (PRD) or another sufficiently detailed specification into a dependency-aware task graph, helps identify work that needs further decomposition, and keeps implementation status outside the agent's temporary conversation context.

This lesson demonstrates Task Master on an existing project and shows how it can complement GitHub Spec Kit. The goal is not merely to generate a long to-do list. The goal is to produce reviewable execution units, keep dependencies explicit, and give a coding agent a reliable answer to the question: **what should be implemented next?**

## Learning Objectives

By the end of this lesson, you should be able to:

- explain what Task Master manages and what remains your responsibility;
- distinguish the open-source Task Master CLI/MCP from the Hamster team platform;
- install and initialize Task Master in a project;
- configure main, research, and fallback model roles safely;
- convert a PRD or Spec Kit artifact into tasks;
- analyze complexity and expand selected tasks into subtasks;
- run a disciplined implementation loop using task status and dependencies; and
- recognize the main cost, context, security, and maintenance trade-offs.

## Version Notice

Task Master evolves quickly. Commands, supported providers, generated files, MCP tool sets, and model identifiers may change after this lesson is published. The workflow below was checked against the official repository and documentation in September 2026, but you should still verify current installation and configuration instructions before using the tool.

Avoid copying model names from a recording. Model catalogs change frequently, especially when using an aggregator such as OpenRouter. Select a currently available model and copy its exact provider/model identifier from the provider's current catalog.

## What Task Master Does

Task Master separates **execution state** from a chat session. Instead of expecting the model to remember a large project plan throughout a long conversation, it stores tasks, subtasks, dependencies, priorities, status, implementation notes, and test guidance in project files.

Its core responsibilities are:

1. **Parse requirements** into an initial set of tasks.
2. **Analyze complexity** and recommend which tasks need decomposition.
3. **Expand tasks** into actionable subtasks.
4. **Resolve dependencies** and recommend the next unblocked task.
5. **Track progress** as work moves from pending to in progress, review, and done.
6. **Update future work** when requirements or implementation decisions change.

Task Master does not replace:

- product decisions and scope control;
- architecture and technology choices;
- code review and security review;
- test execution and verification; or
- a team issue tracker when that system is the official source of truth.

The generated task descriptions are starting points for implementation, not proof that the requirements are correct.

## Task Master and Hamster Are Related but Distinct

The recording describes Task Master as having become the Hamster platform. A more precise current description is that the projects are related, but serve different scopes:

| Product | Main role | Typical usage |
| --- | --- | --- |
| **Task Master AI** | Open-source CLI and MCP task-management tool stored with a code project | Solo or agent-assisted development from a PRD, local specification, or existing task graph |
| **Hamster** | Hosted team platform for goals, initiatives, research, briefs, plans, shared context, collaboration, and delivery | Teams that want to discuss and approve work in a web workspace, then send it to coding agents through CLI or MCP |

You can use Task Master locally without adopting Hamster. You can also use Hamster when the wider collaboration and shared-context workflow is useful.

## The End-to-End Workflow

![Task Master workflow from requirements to tracked implementation](Task%20Master%20Workflow.png)

The important part of the diagram is the feedback loop. Generated tasks should be reviewed, and new evidence should update the plan. A task list that no longer reflects the product or architecture is structured noise, not useful context.

## How Task Master Complements GitHub Spec Kit

Spec Kit and Task Master overlap, so combining them should be deliberate.

| GitHub Spec Kit | Task Master |
| --- | --- |
| Guides requirements through specification, clarification, planning, task generation, and implementation | Focuses on task decomposition, dependencies, status, and choosing the next executable unit |
| Produces Markdown artifacts that explain what and how to build | Maintains structured execution state, including a JSON task database |
| Strong when a feature needs a disciplined specification workflow | Strong when a large implementation needs persistent task orchestration across sessions |

A practical combined flow is:

1. Use Spec Kit to clarify the feature and make the technical plan explicit.
2. Prepare one consolidated input document containing the approved behavior, constraints, stack, and important architectural decisions.
3. Parse that document with Task Master.
4. Review the generated tasks and dependencies before expansion.
5. Use Task Master to drive implementation and record progress.

Do not parse an incomplete behavior-only specification and expect the model to infer your intended stack. In the lesson demonstration, the input omitted technology choices, so the model selected a popular web stack on its own. That was a predictable consequence of missing context.

Also avoid maintaining two competing task lists. Decide which artifact is authoritative for execution and define how changes flow back to the specification.

## Installation Options

Task Master requires Node.js and npm. The official project supports direct CLI use and MCP integration.

### CLI Installation

Install it globally:

```bash
npm install -g task-master-ai
task-master init
```

Or keep it local to the project:

```bash
npm install task-master-ai
npx task-master init
```

Using `npx` avoids depending on a global executable, while a global installation provides the shorter `task-master` command. Choose one convention for the team and document it.

### MCP Integration

Task Master can also run as an MCP server through:

```text
npx -y task-master-ai@latest
```

The exact MCP configuration file and syntax depend on the client. Follow the official Task Master instructions for Claude Code, VS Code, Cursor, Codex, or your chosen agent harness.

Task Master's MCP server supports selective tool loading. Start with the smallest set that supports the current workflow—usually `core` or `standard`—instead of exposing every tool. This applies the context-engineering principle from the previous module: every tool schema and description consumes part of the context window.

## Initialize the Project

From the project root, run:

```bash
task-master init
```

The interactive setup can ask whether the project is for solo or team work, whether generated task files belong in Git, which language to use, and which agent rule profiles should be created. Select only the profiles used by the project. You can change them later with:

```bash
task-master rules setup
```

A current Task Master project generally contains:

```text
.taskmaster/
├── config.json
├── state.json
├── docs/
│   └── prd.md
├── tasks/
│   └── tasks.json
├── reports/
│   └── task-complexity-report.json
└── templates/
    └── example_prd.md
```

Task Master manages `tasks.json`, `config.json`, and `state.json`. Prefer its commands to direct manual editing, because generated files have an expected schema and internal relationships.

## Configure Models

Task Master defines three model roles:

| Role | Responsibility |
| --- | --- |
| **Main** | Task generation, updates, and ordinary planning operations |
| **Research** | Optional work that benefits from current external information |
| **Fallback** | Used when another configured role fails |

Run the guided configuration:

```bash
task-master models --setup
```

Inspect the current configuration and provider-key status with:

```bash
task-master models
```

Model choices are stored in `.taskmaster/config.json`. The official documentation recommends using the `models` command instead of manually changing that file.

### Authentication Choices

Depending on the selected provider, Task Master can use:

- a provider API key, such as Anthropic, OpenAI, Google, Perplexity, xAI, or OpenRouter;
- a local Claude Code installation; or
- a local Codex CLI installation authenticated through OAuth.

Therefore, a separate API key is **not always required**. It is required when the configured model role calls a provider API directly.

### Using OpenRouter Safely

OpenRouter is useful when you want one API to access models from multiple providers. If you choose it:

1. Create a dedicated key for this project or experiment.
2. Apply a spending limit and expiration when appropriate.
3. Store it as `OPENROUTER_API_KEY` in a local `.env` file or the MCP client's secret environment configuration.
4. Ensure `.env` is ignored by Git before placing a secret inside it.
5. Copy exact model identifiers from the current OpenRouter model catalog.
6. Revoke and replace any key that appears in a recording, screenshot, terminal log, chat, or commit.

Never commit provider keys. A short expiration does not make it safe to publish an active key.

The video's fixed price estimates should not be treated as guarantees. Cost depends on the selected model, input size, output size, research calls, retries, and the number of tasks being generated. Check the provider's current pricing and usage dashboard.

> **Token note:** 32,000 tokens do not equal 32,000 words. Tokens are smaller language units, and the conversion varies by language and content. Raising an output-token limit can also increase latency, cost, and the chance of producing unnecessarily large task descriptions.

## Prepare the Input Document

For a complex project, place the approved PRD or consolidated specification in `.taskmaster/docs/`. Markdown is convenient because it is readable in editors and code review.

The input should cover at least:

- the problem and target users;
- in-scope and out-of-scope behavior;
- acceptance criteria;
- the chosen technology stack and important constraints;
- non-functional requirements;
- integration points and data boundaries;
- test and verification expectations; and
- known sequencing or migration constraints.

You can create the PRD through a normal conversation with an agent, use the initialized example template, or adapt a previously approved Spec Kit artifact. Review it before generating tasks: Task Master amplifies both good and bad input.

## Parse the PRD into Tasks

Run:

```bash
task-master parse-prd .taskmaster/docs/prd.md
```

You can request a fixed number of initial tasks or allow the tool to decide according to the current command options. After parsing, inspect the result rather than immediately expanding everything:

```bash
task-master list --with-subtasks
task-master show 1
```

Check that:

- the task boundaries match the intended architecture;
- dependencies point in the correct direction;
- acceptance and test expectations are present;
- the stack was not invented or changed;
- tasks are implementation units rather than vague epics; and
- no product requirement disappeared during decomposition.

JSON helps because it is structured and machine-readable, but JSON is not automatically the "best" format for every model or workflow. The schema, content quality, and validation matter more than the file extension.

## Analyze Complexity

Run the complexity analysis:

```bash
task-master analyze-complexity
task-master complexity-report
```

If a research model is configured and fresh external knowledge is truly useful, add the research option:

```bash
task-master analyze-complexity --research
```

The report assigns complexity scores and recommends how many subtasks each task may need. Treat these recommendations as estimates. A high score may indicate missing decisions rather than a need for more generated subtasks.

Before expanding, look for tasks that should instead be:

- clarified with the product owner;
- split along an architectural boundary;
- preceded by a technical spike;
- postponed from the current release; or
- rejected because they duplicate another task.

## Expand Tasks into Subtasks

To expand all eligible tasks:

```bash
task-master expand --all
```

For research-backed expansion:

```bash
task-master expand --all --research
```

For tighter control, expand one task at a time:

```bash
task-master expand --id=5 --num=3
```

Expanding every task can create unnecessary detail and additional model cost. Prefer targeted expansion when only a few tasks are genuinely complex.

After expansion, validate dependencies and review the hierarchy:

```bash
task-master validate-dependencies
task-master list --with-subtasks
```

## The Daily Implementation Loop

The task graph becomes valuable when it drives a consistent execution loop.

### 1. Select the Next Unblocked Task

```bash
task-master next
task-master show <id>
```

`next` considers task state and dependencies. `show` provides the detailed implementation notes and test strategy for the selected task.

### 2. Mark Work in Progress

```bash
task-master set-status --id=<id> --status=in-progress
```

### 3. Implement and Verify

Ask the coding agent to implement only the selected task and follow the project's instructions. Run the relevant tests, static analysis, and manual checks. Task Master tracks the work; it does not prove that the code is correct.

### 4. Record Useful Findings

For a subtask, append concise implementation information that will help a future session:

```bash
task-master update-subtask --id=<task.subtask> --prompt="Implementation notes and verification evidence"
```

Record durable facts such as the chosen interface, an important constraint, a migration detail, or why a test was added. Do not fill the task database with a transcript of every thought.

### 5. Complete and Repeat

```bash
task-master set-status --id=<id> --status=done
task-master next
```

Only mark a task done after its acceptance criteria are satisfied and the required verification has passed.

## Working with Changing Requirements

Large projects change after task generation. Do not silently implement new assumptions while leaving the old task graph unchanged.

Useful commands include:

```bash
task-master update-task --id=<id> --prompt="Describe the approved change"
task-master update --from=<id> --prompt="Apply this decision to future tasks"
task-master add-task --prompt="Describe the newly approved work"
task-master add-dependency --id=<id> --depends-on=<id>
task-master validate-dependencies
```

If a major change invalidates the original requirements, update the authoritative PRD or specification first, then reconcile the affected tasks. This preserves traceability between intent and implementation.

## Integrating with an Issue Tracker

Generated tasks can be copied or synchronized to systems such as Jira, Linear, or GitHub Issues, depending on the available integrations. Before doing so, decide which system owns each field:

| Concern | Example source of truth |
| --- | --- |
| Product scope and acceptance criteria | Approved PRD or feature specification |
| Team assignment, sprint, and delivery reporting | Jira, Linear, or GitHub Issues |
| Agent-ready decomposition and implementation notes | Task Master |
| Code status and review | Git branch and pull request |

Without this decision, task state will drift between systems. Do not automatically create external tickets during an experiment unless the team has agreed to that workflow.

## When Task Master Helps

Task Master is most useful when:

- the initiative is too large for one focused coding session;
- tasks have meaningful dependencies;
- several sessions or agents need shared execution state;
- the team repeatedly loses implementation context;
- a large PRD needs reviewable decomposition; or
- you need a durable record of what is pending, blocked, in progress, and done.

It may be unnecessary when:

- the feature is small enough for a short plan and one session;
- an existing issue tracker already provides sufficient decomposition and status;
- maintaining the generated task graph costs more than it saves; or
- the team has not agreed on a source of truth.

The first few minutes of setup can feel slower than immediately asking an agent to code. The payoff appears only when the saved coordination and context exceed the framework overhead.

## Common Mistakes

- Parsing a vague PRD and trusting the generated task list without review
- Omitting the technology stack and allowing the model to invent one
- Treating task generation as architecture design rather than a decomposition of approved decisions
- Expanding every task even when the initial task is already actionable
- Running research mode for ordinary work that does not need fresh external information
- Hard-coding model identifiers copied from an old lesson
- Manually editing `tasks.json` or `config.json` and breaking the expected schema
- Committing `.env` or placing active API keys in screenshots and recordings
- Loading every MCP tool when a smaller tool set is sufficient
- Maintaining conflicting task lists in Spec Kit, Task Master, and an issue tracker
- Marking tasks complete without running the required tests and checks
- Assuming Task Master automatically implements or validates the whole project without explicit agent workflow and human review

## Troubleshooting Checklist

### MCP Server Does Not Connect

1. Confirm Node.js and npm are installed.
2. Run `npx -y task-master-ai@latest` directly and inspect the error.
3. Validate the MCP configuration syntax and server key expected by the client.
4. Restart the editor or agent harness after changing MCP settings.
5. Start with the `core` or `standard` tool set.

### Model Calls Fail

1. Run `task-master models` and verify the provider, role, and key status.
2. Confirm that the model identifier exists for the selected provider.
3. Check API credit, spending limit, expiration, and provider availability.
4. Use a fallback role only after confirming that it is configured correctly.

### Generated Tasks Use the Wrong Stack

Add the missing technical constraints to the source document, then update or regenerate the affected tasks. Do not repair a large incorrect task graph one field at a time if the input remains wrong.

### Too Many Tasks or Subtasks

Review the complexity report, reduce automatic expansion, and expand only high-risk tasks. A smaller, reviewed task graph is more useful than a large generated backlog.

## Practical Exercise

Choose an existing project with a reviewed feature specification.

1. Initialize Task Master in the repository.
2. Configure one main model and, only if needed, one research model.
3. Place a reviewed PRD or consolidated Spec Kit document in `.taskmaster/docs/`.
4. Parse it into tasks.
5. Review the initial task boundaries, stack, acceptance criteria, and dependencies.
6. Analyze complexity and inspect the report.
7. Expand only the tasks that genuinely require subtasks.
8. Run `next`, implement one task, verify it, record a concise note, and mark it done.
9. Compare the effort and result with your ordinary agent workflow.

Evaluate whether Task Master reduced coordination and context loss enough to justify its setup and maintenance cost.

## Recap

- Task Master converts a reviewed PRD or specification into a persistent, dependency-aware execution plan.
- Task Master AI and Hamster are related but distinct: the former is a local open-source CLI/MCP tool, while the latter is a broader hosted team platform.
- API keys are not always mandatory because current Task Master versions can also use authenticated Claude Code or Codex CLI installations.
- Configure model roles through `task-master models --setup`; keep secrets outside version control.
- The core flow is `init` → `parse-prd` → review → `analyze-complexity` → review → `expand` → `next` → implement → verify → `set-status`.
- Spec Kit can remain the specification workflow while Task Master manages persistent execution state, but the team must define a single source of truth.
- Structured JSON is useful, but good inputs, clear schemas, validation, and human review determine quality.
- Task Master is valuable for large, dependency-heavy, multi-session work and can be overhead for small features.
- Framework-generated tasks do not replace product judgment, architecture decisions, tests, or code review.

## References

- [Task Master AI repository](https://github.com/eyaltoledano/claude-task-master)
- [Task Master documentation](https://docs.task-master.dev/)
- [Task Master configuration guide](https://github.com/eyaltoledano/claude-task-master/blob/main/docs/configuration.md)
- [Task Master command reference](https://github.com/eyaltoledano/claude-task-master/blob/main/docs/command-reference.md)
- [Hamster](https://tryhamster.com/)
- [OpenRouter quickstart](https://openrouter.ai/docs/quickstart)
- [OpenRouter API key documentation](https://openrouter.ai/docs/api/api-reference/api-keys/create-keys)
