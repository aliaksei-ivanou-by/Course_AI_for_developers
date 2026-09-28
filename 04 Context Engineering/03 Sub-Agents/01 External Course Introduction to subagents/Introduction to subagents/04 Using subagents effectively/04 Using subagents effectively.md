# Using Subagents Effectively

Subagents are most valuable when the main conversation needs the result of a task but does not need its full trail of searches, file reads, logs, and intermediate discoveries.

Delegation introduces overhead: the parent must describe the task, the subagent works with limited context, and its findings must be compressed into a result. Use that tradeoff deliberately.

## The Core Decision Rule

Before delegating, ask one question:

> Does the intermediate work matter to the main conversation?

| Answer | Recommended approach |
| --- | --- |
| No — only the final result matters | Delegate to a subagent |
| Yes — later decisions depend on each discovery | Keep the work in the main conversation |

A good subagent task has a clear boundary, can be completed independently, and returns an output the parent can use without reconstructing the entire investigation.

## When Subagents Work Well

Subagents are a strong fit when:

- the result matters more than the detailed path used to obtain it;
- exploration would add large amounts of temporary material to the main context;
- the task benefits from an independent perspective;
- a specialized system prompt or restricted tool set improves consistency; or
- several tasks are independent enough to run separately.

### Research and Exploration

Research is a classic delegation scenario. Suppose you need to understand how authentication works in an unfamiliar codebase. The main conversation may only need to know where JWT validation occurs and how requests reach that code.

A research subagent can search many files, trace function calls, and compare possible paths in its own context. It can return a concise, evidence-based result such as:

```text
JWT validation occurs in middleware/auth.js:42 and is invoked by the API router
in routes/api.js. Requests that fail validation return before reaching the route handler.
```

The parent receives the location and conclusion without retaining every search result.

### Independent Code Review

A reviewer subagent examines a change in a context separate from the implementation conversation. It can run `git diff`, inspect the modified files, and apply a consistent checklist without being influenced by the discussion that produced the code.

This is especially useful when the review definition includes project-specific requirements such as security checks, architectural boundaries, error-handling conventions, and a structured approval decision.

The subagent should return concrete findings with file and line references, not merely state that the code looks good.

### Tasks Requiring a Different System Prompt

Some tasks benefit from instructions that differ substantially from the main coding workflow:

- A copywriting subagent can follow a defined tone, audience, vocabulary, and content structure.
- A styling subagent can be instructed to read the project's design-system files before changing CSS or components.
- A documentation subagent can enforce a particular style guide and document template.

The advantage comes from the specialized instructions and context, not from attaching an impressive-sounding expert label.

### Independent Parallel Work

Parallel delegation is useful when tasks do not depend on one another. For example, separate subagents could independently:

- research authentication behavior;
- inspect database migration risks; and
- review API documentation coverage.

Each task should have its own inputs and deliverable. The parent then compares or combines the returned results.

Do not parallelize work merely because it can be divided into steps. If one step needs the detailed discoveries from another, separating them creates fragile handoffs.

## When Subagents Get in the Way

Delegation is less effective when it hides information the main conversation needs or adds coordination without adding useful isolation.

### Empty Expert Personas

A subagent described only as a "Python expert" or "Kubernetes specialist" does not automatically gain capabilities beyond the main model. A useful custom subagent needs something concrete, such as:

- a specialized system prompt;
- project-specific standards;
- a restricted or expanded tool set;
- dedicated reference material; or
- a repeatable output format.

If none of these differences exists, the main conversation can usually complete the task directly.

### Sequential Pipelines with Dependent Steps

Consider a pipeline with one subagent reproducing a bug, another diagnosing it, and a third implementing the fix. Each handoff compresses the previous agent's observations. Important logs, failed hypotheses, or environmental details may be lost.

Bug investigation is usually iterative: reproduction changes the diagnosis, and implementation may reveal that the original diagnosis was incomplete. Keep tightly coupled work in one context unless each stage can pass a complete, structured artifact to the next.

### Test Runners That Hide Diagnostic Output

Running tests through a subagent can be counterproductive when the main conversation needs the complete failure output to debug the problem. A summary such as "three tests failed" removes the stack traces, command details, and environment information required for the next step.

Keep test execution in the main conversation when failures will guide immediate debugging. A test subagent is reasonable only when it returns the necessary diagnostics in full or when the parent needs a simple, self-contained verification result.

## Delegation Checklist

Before starting a subagent, confirm that:

1. The task has a clear and narrow objective.
2. The required inputs can be stated up front.
3. The task does not depend on continuous interaction with the parent.
4. The intermediate work can safely remain outside the main context.
5. The expected output format is explicit.
6. Obstacles, uncertainty, and incomplete work will be reported.
7. The assigned tools match the task and no more.
8. The parent knows how it will use the returned result.

If several of these conditions are not met, perform the work directly or redefine the task boundary before delegating.

## Practical Decision Table

| Task | Delegate? | Reason |
| --- | --- | --- |
| Find where authentication is implemented | Usually yes | Search output is temporary; the parent needs locations and evidence |
| Review a completed change | Usually yes | An isolated perspective and reusable checklist add value |
| Investigate and fix an unfamiliar intermittent bug | Usually no | Diagnosis and implementation depend on detailed intermediate discoveries |
| Run a test suite while actively debugging failures | Usually no | Full output is needed in the main conversation |
| Produce copy using a defined brand voice | Often yes | A specialized system prompt makes the role meaningfully different |
| Apply a one-line code edit | Usually no | Delegation costs more than direct execution |

## Recap

- Delegate when the result matters but the intermediate work does not.
- Research, independent review, and specialized-system-prompt tasks are strong use cases.
- Parallelize only tasks that can succeed independently.
- Avoid empty expert personas that do not provide distinct instructions or capabilities.
- Keep tightly coupled sequential work in one context to prevent information loss.
- Do not hide test diagnostics needed for immediate debugging.
- Use explicit inputs, outputs, tool limits, and obstacle reporting for every delegated task.

## Lesson Reflection

- Which task in your current workflow produces temporary context that could be isolated safely?
- Which task should remain in the main conversation because its intermediate discoveries drive later decisions?
- Can any independent checks in your workflow run in parallel without creating handoff dependencies?

## Course Complete

You can now explain how subagents isolate work, create a custom definition, design reliable instructions and outputs, and decide when delegation improves a workflow.

Apply the decision rule to a real task: delegate one self-contained investigation, review the returned evidence, and refine the subagent definition based on what the parent conversation still needed.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=n5LoKZ8Oa-A)
