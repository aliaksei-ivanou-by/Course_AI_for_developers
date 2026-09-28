# One Task, One Chat: Dividing Work across Sessions

The simplest way to prevent context from becoming noisy is to give each agent session one coherent objective. This is the **one task, one chat** principle.

The principle is a scoping heuristic, not a literal requirement to open a new conversation for every command or tiny edit. A task can contain investigation, planning, implementation, testing, documentation, and review when all of them serve the same outcome.

> **Scope test:** If all requested work can share one definition of done, it can usually remain in one session. If the work needs different goals, evidence, constraints, or success criteria, split it.

## Project, Task, and Session Are Different Units

These terms are easy to conflate:

| Unit | Meaning | Example |
| --- | --- | --- |
| Project | A long-lived product or repository | Payment service |
| Task | A bounded outcome with a definition of done | Prevent duplicate payment submission |
| Session or chat | The conversation and working context used to complete a task | Investigation and implementation thread for the duplicate-payment defect |
| Turn | One user request and the agent's resulting work | “Run the focused regression test” |

A project normally contains many tasks and therefore many sessions. A single task usually spans multiple turns. “One task, one chat” does not mean “one project, one chat” or “one message, one chat.”

## Why Mixed Tasks Cause Problems

Every session develops a local working context containing goals, instructions, files, tool results, decisions, and examples. Mixing unrelated objectives can create two kinds of interference.

### Context Clash

Context clash occurs when material from an earlier task conflicts with the current task:

- An old requirement contradicts a new one.
- A previous coding convention belongs to another repository.
- The earlier task allowed a dependency that the new task prohibits.
- A former output format continues to influence the response.
- The conversation refers to a branch or file state that is no longer current.

Later instructions may formally take precedence, but the irrelevant alternatives still consume context and make the intended boundary less clear.

### Context Distraction

Context distraction occurs when old material is not contradictory but no longer useful. The agent must process marketing notes, unrelated code, legal text, research results, or verbose logs while solving a different problem.

Possible consequences include:

- Higher input-token usage
- Slower responses
- Important evidence becoming harder to locate
- Repeated use of stale assumptions
- More clarification and repair turns
- Earlier context compaction

The problem is not that an agent literally becomes confused by every topic change. The practical risk is that irrelevant context competes with the evidence that should drive the current decision.

## Define “One Task” by Outcome

Separate sessions by goal, not merely by activity type.

For example, these activities may belong in the **same** task:

```text
reproduce checkout race
        ↓
inspect payment flow
        ↓
design idempotency fix
        ↓
implement code and tests
        ↓
update relevant documentation
        ↓
validate the accepted behavior
```

They share one definition of done: the duplicate-submission defect is fixed and verified.

By contrast, the following requests do not share one outcome and should normally use different sessions:

```text
fix checkout race
write product launch copy
review a vendor contract
outline a training video
```

Dividing them prevents one task's tone, assumptions, documents, and constraints from leaking into another.

## When to Continue the Same Session

Stay in the current chat when the next request:

- Clarifies the same objective
- Corrects an implementation made in the session
- Asks for another validation of the same deliverable
- Responds to a question or blocker raised by the agent
- Adds a requirement that remains compatible with the task's definition of done
- Requests documentation directly required by the implemented change
- Continues an investigation whose findings are needed for the current fix

Examples:

```text
“The regression test still fails on Windows; continue the same fix.”
“Keep the API unchanged and revise the implementation.”
“Now run the integration test required by the acceptance criteria.”
```

Starting over in these cases can be wasteful because a new session may have to rediscover the same files, failures, and decisions.

## When to Start a New Session

Start a new chat when:

- The objective changes.
- The work moves to an unrelated feature or repository.
- A different definition of done is required.
- The earlier task has finished and its implementation history is no longer useful.
- Old assumptions conflict with the new direction.
- The current session contains so much unrelated exploration that compaction would still leave a poor working set.
- An independent review should not inherit the implementation discussion and its anchoring bias.
- Two tasks should run in parallel without sharing mutable state.

A useful diagnostic question is:

> Would a competent engineer need the previous conversation to perform this request correctly?

If the answer is no, begin a focused session. If the answer is yes, keep the relevant thread or create a concise handoff before moving.

## New Session, Compaction, or Fork?

Choose the transition according to the relationship between the old and new work.

| Situation | Preferred action | Reason |
| --- | --- | --- |
| Same objective, context becoming large | Compact | Preserve the task while summarizing exploration |
| Same base evidence, two alternative approaches | Fork when supported | Compare paths without mixing their later histories |
| New unrelated objective | New session | Avoid carrying irrelevant state |
| Independent review of completed work | New review session | Reduce anchoring to the implementation reasoning |
| Long task with durable milestones | Continue the task with project-state files | Preserve verified progress without depending only on chat history |

Compaction and a new session are not interchangeable. Compaction says, “continue the same objective with a shorter history.” A new session says, “begin a different objective with a deliberately selected context.”

## Codex Cloud Encourages Task Isolation

Codex Cloud can run coding tasks in isolated cloud environments and execute multiple tasks in parallel. This interface naturally encourages users to create a separate task for each reviewable outcome.

A typical flow is:

1. Select the repository and configured environment.
2. Describe one bounded result.
3. Let the task continue while doing other work.
4. Inspect its logs, summary, and diff.
5. Request a follow-up for the same outcome or open a pull request.
6. Start another cloud task for a different objective.

### Background Does Not Mean Unsteerable

The transcript describes a background agent that cannot be interacted with and never asks questions. That is too absolute for current Codex workflows.

Codex Cloud lets a task run in the background, but the user can review its output and request follow-up work. Current managed Codex sessions can also support progress events, continuation, and steering depending on the surface and integration.

The practical lesson is not “the agent can never communicate.” It is:

- Give autonomous work enough context to proceed safely.
- Define which decisions the agent may make alone.
- Identify conditions that require clarification or approval.
- Provide measurable completion criteria.
- Review the resulting diff and evidence before accepting it.

An agent should not invent a consequential product decision merely because it is running unattended.

## Parallel Tasks Need Filesystem Isolation Too

Separate chats isolate conversational context, but they do not automatically prevent file conflicts. When several coding tasks run concurrently, use separate cloud environments, branches, or Git worktrees.

```text
task A chat ── branch/worktree A ── focused diff A
task B chat ── branch/worktree B ── focused diff B
task C chat ── branch/worktree C ── focused diff C
```

Before starting parallel tasks, check:

- Whether they modify the same files
- Whether one depends on another's unmerged change
- Whether migrations or generated artifacts conflict
- Which validation each task owns
- How the results will be integrated

Independent sessions improve context isolation; independent workspaces improve change isolation.

## Write a Task That Can Stand Alone

A new session starts with less conversational history, so its initial request must contain the information needed to work responsibly.

Use a compact task contract:

```markdown
## Objective
Prevent duplicate checkout submissions caused by concurrent requests.

## Scope
- Payment submission and its focused tests
- Preserve the public endpoint contract

## Evidence
- Failure reproduction: `tests/payments/idempotency.test.ts`
- Current flow: `src/payments/submit.ts`

## Constraints
- Do not add a production dependency.
- Do not apply migrations outside the test database.

## Done when
- The new regression test passes.
- Existing payment tests pass.
- The implementation explains the idempotency boundary.

## Decision boundaries
Stop and ask before changing the public API or persistence schema.
```

This is more reliable than “continue from the other chat” or pasting an entire transcript.

## Preserve Durable State between Sessions

Starting a clean chat should not erase important project knowledge. Move stable information into the repository:

- `AGENTS.md` or a tool-native equivalent for working conventions
- Specifications for accepted requirements
- Plans and task lists for approved implementation work
- Architecture decision records for durable decisions
- Tests for executable behavior
- A progress or handoff file for long-running work
- Git history for completed changes and rationale

A concise handoff should record:

```text
objective and definition of done
current status
confirmed facts and sources
decisions and rejected alternatives
files changed
checks run and their results
remaining blockers and next action
```

Do not preserve every conversational detail. Preserve the information another competent session needs to continue correctly.

## Avoid Oversplitting

Opening too many tiny sessions can create its own cost:

- Repeated repository discovery
- Repeated loading of project instructions and tool definitions
- Loss of local reasoning about a defect
- More handoff documents to maintain
- Fragmented ownership of validation

Do not create a new chat merely because the task changes phase from research to coding or from coding to testing. Split when the **objective** changes or when independent execution provides a real benefit.

## Session Decision Examples

| Next request | Same session? | Why |
| --- | ---: | --- |
| Fix the test failure caused by the current implementation | Yes | Same deliverable and evidence |
| Add documentation required for the current feature | Usually | Same definition of done |
| Research an API needed for the current design | Usually, or delegate | Findings directly support the task |
| Review the completed change independently | Prefer a new session | Fresh perspective reduces anchoring |
| Begin a separate feature in the same repository | No | New objective and acceptance criteria |
| Write unrelated marketing copy | No | Different goal, evidence, and constraints |
| Compare two competing implementation approaches | Fork if available | Shared starting point, divergent histories |
| Rename a second nearby variable while making a tiny cleanup | Use judgment | A new session may cost more than the isolation helps |

## Recommended Workflow

```text
define one outcome and “done when”
              ↓
start a focused session in the correct repository and branch
              ↓
provide relevant evidence, constraints, and decision boundaries
              ↓
investigate → implement → validate within the same task
              ↓
review the summary, diff, and verification evidence
              ↓
save durable decisions and finish the task
              ↓
start a new session for the next independent outcome
```

## Common Mistakes

- Keeping one chat for an entire project indefinitely
- Starting a new session for every tiny command
- Separating research, coding, testing, and documentation even when they serve one outcome
- Mixing unrelated repositories or business domains in one context
- Starting a clean session without supplying necessary requirements and evidence
- Copying the entire old transcript instead of preparing a concise handoff
- Assuming an unattended agent should make every decision without escalation
- Running parallel chats against the same working tree without coordination
- Treating a separate chat as a substitute for a separate branch or worktree
- Continuing a finished task's thread for convenience when the objective has changed
- Accepting a background result without reviewing its diff and validation evidence

## Key Takeaway

“One task, one chat” means one coherent objective per working context. Keep the same session while investigation, implementation, testing, and documentation contribute to one definition of done. Start a new session when the objective, evidence, constraints, or success criteria change. For background and parallel work, isolate both the conversation and the filesystem, provide clear decision boundaries, and preserve durable state in project artifacts rather than relying on an ever-growing chat history.

## Further Reading

- [Official OpenAI documentation: Codex Cloud](https://learn.chatgpt.com/docs/cloud)
- [OpenAI: Running long-horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)
- [OpenAI: Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)
