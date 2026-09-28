# Context Engineering for AI-Assisted Development

AI-assisted development improves when the agent receives the right information at the right time. This sounds simple, but a real coding session combines repository rules, user requirements, source files, documentation, tool definitions, command output, conversation history, and model-generated conclusions. If all of it is loaded indiscriminately, the session becomes expensive and noisy. If too little is supplied, the agent guesses.

Context engineering is the discipline of designing that information flow.

It is not merely prompt writing and it is not the pursuit of the smallest possible token count. Its purpose is to give the model a working set that is:

- Sufficient for the present objective
- Relevant rather than merely available
- Current and version-matched
- Structured so priorities are visible
- Traceable to authoritative evidence
- Authorized for the user and task
- Small enough to remain efficient

> **Working definition:** Context engineering determines what an agent can see, when it can see it, how it retrieves more, and which evidence must be preserved or discarded as the task progresses.

## A Layered Model of Agent Context

A coding agent's effective context can be understood as several layers:

```text
durable project instructions
            +
current task contract
            +
selected repository evidence
            +
current external knowledge
            +
available tool definitions
            +
conversation and tool-result history
            ↓
model reasoning and action
            ↓
verified code, tests, and durable project state
```

Each layer has a different lifetime. Repository conventions may remain useful for years. A feature specification may last for one implementation cycle. A compiler error may matter for only one turn. Treating all layers as one undifferentiated transcript is the root of many context problems.

## 1. Preserve Durable Context in Project Instructions

An agent should not rediscover the same project facts in every session. A repository-level instruction file can preserve stable working agreements such as:

- What the project does
- Where important components live
- How to build, test, lint, and format it
- Which architectural boundaries must be respected
- Which actions require approval
- What evidence is required before work is considered complete
- Where deeper specifications and runbooks live

In Codex, `AGENTS.md` is the native project-instruction file. Other tools may use names such as `CLAUDE.md` or `GEMINI.md`. An initialization command can generate a useful scaffold by exploring an existing repository, but generated instructions must be reviewed before they become trusted guidance.

Good project instructions are concise and verifiable:

```markdown
# Repository Instructions

## Project
Backend service for order processing.

## Layout
- `src/domain/`: business rules
- `src/http/`: API adapters
- `tests/`: unit and integration tests

## Commands
- Install: `npm ci`
- Focused test: `npm test -- <path>`
- Full validation: `npm run validate`

## Working agreements
- Keep domain code independent of HTTP and database adapters.
- Do not add a production dependency without approval.
- Ask before changing a public API or database schema.

## Validation
- Add a regression test for behavior changes.
- Report commands run and their results.
```

Project instructions should not contain secrets, temporary task details, enormous repository maps, or statements that have not been checked. They route the agent to deeper sources; they do not replace specifications, architecture records, or tests.

## 2. Give Each Session One Coherent Objective

A project can last years, but an agent session should usually serve one bounded outcome. This is the **one task, one chat** principle.

The rule does not mean opening a new chat for every command. Investigation, planning, implementation, tests, documentation, and repair can remain together when they share one definition of done. A new session becomes appropriate when the objective, repository, evidence, constraints, or success criteria change.

Mixing unrelated tasks creates two forms of interference:

- **Context clash:** old instructions or assumptions conflict with the new task.
- **Context distraction:** irrelevant history consumes attention without directly contradicting anything.

A session should begin with a compact task contract:

```markdown
## Objective
Prevent duplicate order submission during concurrent requests.

## Scope
- Order submission path and focused tests
- Preserve the public endpoint contract

## Relevant evidence
- `src/orders/submit.ts`
- `tests/orders/idempotency.test.ts`

## Constraints
- No new production dependency
- No production-data modification

## Done when
- The regression test passes.
- Existing order tests pass.
- The idempotency boundary is documented.

## Decision boundaries
Stop and ask before changing the public API or persistence schema.
```

When the same task continues but the conversation becomes too large, compact it. When two approaches share a starting point but should diverge, fork if the tool supports it. When the objective changes, start a clean session with a concise handoff.

Parallel conversations also require filesystem isolation. Use separate branches, worktrees, or cloud environments when concurrent agents can modify overlapping files.

## 3. Observe Context without Confusing the Metrics

Status lines and usage views make invisible session state easier to inspect. Useful signals include:

- Selected model and reasoning level
- Current directory and Git branch
- Context occupied or remaining
- Cumulative input and output tokens
- Cache creation and cache reads
- Rate limits or subscription allowances
- Tool calls and separately billed services

These metrics answer different questions. Context occupancy describes the working set for a request. Cumulative usage describes activity across a session. Cache tokens describe reuse of a stable prefix. A displayed cost estimate depends on the model, provider, authentication path, tool pricing, and accounting rules.

```text
context remaining
      ≠ cumulative session tokens
      ≠ cache-read tokens
      ≠ subscription allowance
      ≠ final bill
```

A status line is an observability tool, not an automatic optimization system. Its value is the decision it triggers: narrow tool output, compact a continuing task, move stable conclusions into files, or start a new session for a different objective.

## 4. Understand Prompt Caching

Prompt caching reduces repeated computation for a stable request prefix. The provider may create a cache entry for instructions, earlier messages, files, or tool definitions and later reuse it at a different input rate.

Caching does not remove text from the context window. Cached instructions and history remain visible to the model and can still be irrelevant, contradictory, or too large. Caching and context hygiene solve different problems:

| Mechanism | Primary purpose |
| --- | --- |
| Prompt caching | Reuse repeated input computation |
| Compaction | Summarize history while continuing the same objective |
| New session | Start a different objective without old conversational history |
| Retrieval | Load only evidence relevant to the present question |
| Durable project files | Preserve important state outside one conversation |

Keep stable prefixes stable when caching helps, but do not preserve obsolete material merely to retain a cache hit. Optimize the correctness and total cost of the completed task rather than the price of one request.

## 5. Treat Context Capacity as a Limit, Not a Target

A model's advertised context window is the maximum capacity of a particular configuration. It is not a recommendation to fill the window.

Long context is necessary for some tasks, but more material does not guarantee better reasoning. Important constraints can become harder to locate among duplicate documents, old plans, logs, search results, and tool output. Research often described as *Lost in the Middle* has shown that information position can affect retrieval in long contexts, although the magnitude depends on the model and task.

There is no universal token count at which every model becomes unreliable. A good working set is judged by quality rather than size alone:

| Context state | Likely result |
| --- | --- |
| Too little | Guessing, repeated discovery, missed constraints |
| Compact and sufficient | Efficient use of relevant evidence |
| Large but focused | Appropriate for genuinely complex tasks |
| Large and noisy | Higher latency and cost, conflicting assumptions, weaker retrieval |

Structure matters. Separate objective, evidence, constraints, output requirements, and completion criteria. Place durable rules in repository instructions and current requirements in the task. Avoid scattering critical facts across a long conversation.

## 6. Control Tool Context

External tools extend what an agent can do, but every integration can add metadata and output to the working context. An MCP server may contribute server instructions, tool names, descriptions, input schemas, and results.

The exact cost depends on the client:

- **Eager loading** exposes tool definitions immediately.
- **Deferred loading or tool search** loads detailed definitions when required.
- **Allowlists** expose only a selected subset.
- **Project profiles** enable different toolsets for different repositories.

A connected server does not necessarily mean that every tool schema is loaded into every prompt. Likewise, reducing the number of servers does not help if one remaining tool returns an unbounded log or document.

Choose the interface according to the task:

| Interface | Strong fit |
| --- | --- |
| CLI | Stable direct operation with reliable machine-readable output |
| MCP | Structured discovery, typed inputs, portable or shared integrations |
| Native tool | Narrow product-controlled capability |
| Skill | Progressively disclosed instructions for using a CLI, script, or workflow |
| Hybrid | Real systems that need several of the above |

Moving an MCP capability behind a CLI can reduce upfront schema exposure, but command instructions and output still consume context. It also introduces shell quoting, parsing, credential, and injection risks. MCP has its own risks, including malicious servers, broad permissions, and unsafe side effects.

Use trusted tools, least privilege, bounded results, and explicit confirmation for consequential actions.

## 7. Supply Current External Knowledge

Model knowledge is historical. A published knowledge cutoff does not prove that every earlier API, release, or migration note is known correctly. Software versions, cloud support schedules, security guidance, pricing, and product behavior continue to change.

Ground time-sensitive decisions in current evidence:

- Use web search to discover authoritative sources.
- Fetch a known official page when the URL is already identified.
- Use a documentation retriever for focused library material.
- Query a vendor CLI or API for the target environment's actual state.
- Load internal documentation for private APIs and organizational standards.
- Inspect local manifests and lockfiles to identify the versions the repository really uses.

“Use the latest version” is rarely a complete requirement. The agent needs to know whether “latest” means upstream, available in a managed service, in standard support, compatible with pinned dependencies, permitted in a region, or approved by the organization.

A reliable grounding request separates research from implementation:

```markdown
Before changing code:

1. Read versions and constraints from the repository manifests and lockfiles.
2. Retrieve official documentation for those exact versions.
3. Check the target environment's current support and availability.
4. Record source URLs, versions, and the date checked.
5. Stop and ask if sources conflict or required environment data is unavailable.

Then implement the smallest compatible change and run deterministic validation.
```

Retrieval improves the evidence supplied to the model; it does not certify the result. The agent can select the wrong library, use documentation for another version, ignore a decisive passage, or produce invalid code despite having the correct source.

## 8. Retrieve Repository Evidence with Codebase Indexing

Large repositories cannot be loaded wholesale into a prompt. A codebase index maintains an external representation of files, symbols, relationships, history, or semantic meaning and retrieves a bounded evidence set for the current question.

Different search methods solve different problems:

- Exact text search is strong for known symbols and strings.
- Language servers and static analysis are strong for definitions and references.
- Git is authoritative for history.
- Semantic retrieval is useful when the request and code use different vocabulary.
- Hybrid indexes help with cross-directory or cross-repository architecture.

An index is not proof. Its result may describe the wrong branch, stale content, a test implementation, generated code, or a semantically similar path that is not executed. The agent should use retrieval to select files, then open those files in the current workspace, verify references, and run tests.

```text
index returns candidates
          ↓
source inspection confirms symbols and control flow
          ↓
tests or runtime evidence confirm behavior
```

Index scope is also a security decision. Exclude secrets, customer data, generated artifacts, large dependencies, and anything outside the user's authorization. Verify where code, embeddings, and metadata are processed and stored, how they are deleted, and which branches are indexed.

## One Integrated Workflow

The practices above form one lifecycle rather than a collection of isolated tricks.

### Before the Task

1. Open the correct repository and branch.
2. Load reviewed project instructions.
3. Define one objective and its completion criteria.
4. Identify decision boundaries and risky actions.
5. Select only the tools required for this task.

### During Discovery

1. Inspect manifests, lockfiles, and nearby source.
2. Use exact search for known names.
3. Use indexed retrieval for conceptual or cross-repository questions.
4. Retrieve current official documentation for volatile facts.
5. Record evidence, source version, and uncertainty.

### During Implementation

1. Keep changes within the agreed scope.
2. Bound logs, search results, and tool output.
3. Re-read authoritative source files before relying on a retrieval summary.
4. Monitor context and compact only when continuing the same objective.
5. Stop for missing authority or consequential product decisions.

### During Validation

1. Run focused tests first.
2. Run required broader checks.
3. Review the diff and external side effects.
4. Verify current-environment assumptions with deterministic tools.
5. Report commands, outcomes, and remaining uncertainty.

### At Handoff

1. Save accepted requirements and decisions in durable project artifacts.
2. Record the files changed and checks run.
3. Preserve blockers and the next action.
4. Finish the session when its objective is complete.
5. Start a new session for the next independent outcome.

## Running Example: Updating Infrastructure in a Large Repository

Suppose an agent must update a Kubernetes configuration managed through Terraform in a large multi-service repository.

An undisciplined request would be:

```text
Update Kubernetes to the latest version.
```

The agent may select a remembered version, search the wrong module, load excessive files, or confuse upstream Kubernetes support with the managed provider's lifecycle.

A context-engineered workflow is different:

1. Repository instructions define validation and approval requirements.
2. The task contract names the target service, region, support tier, and definition of done.
3. Exact search locates Terraform constraints and lockfiles.
4. Codebase retrieval finds related modules, add-ons, and deployment policies.
5. Official provider documentation establishes current support.
6. The active account or vendor CLI confirms actual availability.
7. Only the required MCP, CLI, and documentation tools are enabled.
8. The agent implements a narrow change and runs formatting, validation, and policy checks.
9. The pull request records sources, date checked, compatibility reasoning, and remaining rollout steps.

The quality improvement does not come from one longer prompt. It comes from controlling the source, timing, structure, and lifetime of context.

## Context Transition Decisions

Use this compact guide during a session:

| Situation | Preferred action |
| --- | --- |
| Same objective, useful context, adequate capacity | Continue |
| Same objective, excessive exploratory history | Compact and review the summary |
| New unrelated objective | Start a new session |
| Same evidence, competing approaches | Fork when supported |
| Important conclusion must survive the chat | Write it to a project artifact |
| Exact symbol is known | Use lexical or structural search |
| Concept is distributed or vocabulary is unknown | Use semantic or hybrid retrieval |
| Fact may have changed | Retrieve an authoritative current source |
| Large tool catalog, few tools needed | Use deferred discovery or an allowlist |
| Tool output is verbose | Filter, paginate, summarize, or bound it |

## Security Is Part of Context Engineering

Context can contain source code, credentials, customer data, internal tickets, operational logs, and instructions from untrusted sources. Selecting context therefore creates a trust boundary.

Apply these controls:

- Grant each tool and agent only the access required for the task.
- Separate read-only investigation from state-changing operations.
- Do not index secrets or unrestricted production data.
- Treat retrieved documents, issues, web pages, and tool results as untrusted input.
- Require confirmation for destructive, financial, publishing, or externally visible actions.
- Review third-party MCP servers, CLIs, skills, and generated wrappers.
- Verify data processing, storage, retention, deletion, and training policies.
- Keep citations and commit identifiers so claims remain auditable.

Less context is not automatically safer. A small but malicious instruction or an overly privileged tool can be more dangerous than a large document. Context quality includes provenance and authority, not only token count.

## Measure Completed Tasks, Not Isolated Prompts

A useful context strategy should improve engineering outcomes. Evaluate it on repeated representative tasks and measure:

- Correctness and completeness
- Retrieval of decisive constraints
- Unsupported claims and hallucinations
- Time to first useful evidence
- Total wall-clock completion time
- Tool calls and repair turns
- Input, output, and cache-token categories
- External-tool and service cost
- Test, build, and static-analysis results
- Human review effort
- Security or permission violations

One fast response is not a benchmark. Keep the task, repository commit, model, reasoning setting, instructions, and tools fixed when comparing context strategies. Separate one-time indexing or cache creation from steady-state use.

## Common Failure Patterns

- Keeping one conversation for the entire lifetime of a project
- Opening a new session for every tiny command and repeatedly rediscovering state
- Treating an initialization file as unquestionable truth
- Filling the context window because capacity is available
- Confusing context occupancy, session usage, cache reads, and cost
- Compacting without preserving requirements and decisions
- Enabling every MCP server for every task
- Replacing MCP with an unrestricted shell and calling it an optimization
- Allowing tools to return unbounded logs or search results
- Relying on model memory for changing APIs and service versions
- Asking for “latest” without compatibility and support criteria
- Trusting a documentation retriever without checking source and version
- Treating codebase-index results as verified behavior
- Indexing unauthorized repositories, secrets, or customer data
- Comparing tools with different prompts, caches, models, and repository revisions
- Optimizing token count while increasing repair work or lowering correctness

## Practical Checklist

Before asking an agent to perform meaningful work, confirm:

- [ ] The repository, branch, and working directory are correct.
- [ ] Project instructions are reviewed and relevant.
- [ ] The session has one coherent objective.
- [ ] Scope, constraints, completion criteria, and decision boundaries are explicit.
- [ ] Only relevant files and tools are loaded.
- [ ] Volatile facts will be checked against current authoritative sources.
- [ ] Repository retrieval results will be verified in source.
- [ ] Tool permissions and indexed data respect least privilege.
- [ ] Output and logs are bounded.
- [ ] Required tests and validation commands are known.
- [ ] Durable decisions will be saved outside the conversation.
- [ ] A new task will start in a new focused session.

## Key Takeaway

Context engineering is the operating system of effective AI-assisted development. Durable instructions establish how to work. A bounded session establishes what to accomplish. Search and indexing select repository evidence. Documentation retrieval supplies current external facts. Tool configuration controls available actions and overhead. Monitoring, compaction, and session boundaries keep the working set usable. Tests, source inspection, and recorded evidence turn model output into engineering confidence.

The goal is not maximum context and not minimum context. The goal is the **smallest complete, current, trustworthy working set that can produce and verify the required outcome**.

## Detailed Lessons

1. [Generating Project Instructions for Coding Agents](../01%20Generating%20the%20agent%20instructions/01%20Generating%20the%20agent%20instructions.md)
2. [Monitoring Context and Token Usage](../02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline.md)
3. [Context Windows, Prompt Caching, Cost, and Performance](../03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md)
4. [Context Window Size and Model Performance](../04%20Context%20Window%20-%20Performance/04%20Context%20Window%20-%20Performance.md)
5. [One Task, One Chat](../05%20Dividing%20tasks%20by%20sessions/05%20Dividing%20tasks%20by%20sessions.md)
6. [Reducing MCP Server and Tool Context Overhead](../06%20Reducing%20the%20number%20of%20MCP%20servers/06%20Reducing%20the%20number%20of%20MCP%20servers.md)
7. [Providing AI Agents with Up-to-Date Documentation](../07%20Providing%20AI%20with%20up-to-date%20knowledge/07%20Providing%20AI%20with%20up-to-date%20knowledge.md)
8. [Introduction to Codebase Indexing for AI Agents](../08%20Intro%20to%20codebase%20indexing/08%20Intro%20to%20codebase%20indexing.md)
