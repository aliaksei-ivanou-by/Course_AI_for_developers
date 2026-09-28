# Context Window Size and Model Performance

A model's advertised context window is a capacity limit, not a recommended amount of material to load into every request. Long context is valuable when the task genuinely requires it, but filling the available window with old messages, duplicate documents, or noisy tool output can make relevant evidence harder to use.

The goal of context engineering is therefore not “use as few tokens as possible.” It is:

> Give the model complete, current, well-structured evidence for the present objective, and exclude material that cannot affect the answer.

> **Version note:** Context-window sizes differ by provider, model, access method, and release. Some current Claude models support up to one million tokens, while others use different limits. Check the selected model rather than assuming that every AI agent has the same capacity.

## Percentage Remaining Can Be Misleading

A usage indicator may show that a session has consumed only 13% of its context window. That sounds small, but the absolute amount depends on the model's capacity.

```text
occupied context ≈ context-window size × occupied percentage

1,000,000 × 13% ≈ 130,000 tokens
  200,000 × 13% ≈  26,000 tokens
```

These are only rough interpretations when the interface rounds percentages or reserves space for reasoning and output. The key point is that both measurements matter:

- The percentage shows proximity to the model's limit.
- The absolute token count shows how much material the model may need to process.
- The content itself determines whether those tokens are useful or distracting.

A large window provides headroom for difficult tasks. It does not mean that maximum occupancy produces maximum quality.

## Capacity Is Not Effective Context

The context window is everything the model can reference while producing the next response. Depending on the agent and model, it can include:

- System, developer, and repository instructions
- Conversation history
- Current task requirements
- Source code and documentation
- Tool definitions and tool results
- Logs, images, and other attachments
- Reasoning and output-token capacity

The **effective context** is the portion that the model can use reliably for the current task. A request can fit within the formal limit yet still perform poorly because important facts are surrounded by irrelevant or contradictory material.

This distinction prevents a common mistake:

```text
fits in the context window
             ≠
the model will use every detail equally well
```

## Lost in the Middle

The paper *Lost in the Middle: How Language Models Use Long Contexts* evaluated models on multi-document question answering and key-value retrieval. The researchers changed where the relevant information appeared while keeping the task otherwise comparable.

They often observed a U-shaped pattern:

- Information near the beginning was used relatively well: a **primacy** effect.
- Information near the end was used relatively well: a **recency** effect.
- Information in the middle was sometimes retrieved or applied less reliably.

![Serial-position recall pattern: information near the beginning and end is more likely to be recalled than information in the middle](Serial%20Position%20Recall%20Pattern.png)

### Explanation Accompanying the Diagram

The words you remembered likely cluster at the beginning and end of the list. The middle gets lost. This is the primacy–recency effect — and LLMs show the same bias.

Instructions at the start and end of a context window get followed. The middle gets buried. This is why more context ≠ better results — and why *Lost in the Middle* (Liu et al., 2023) found accuracy drops of 30%+ when key facts land in the center of long contexts.

### Interpret the Diagram Carefully

The U-shaped diagram is a teaching model, not a universal law for every prompt or current model. The original paper reported significant positional degradation in the tasks and models it tested, but it did not establish one fixed accuracy penalty for every workload. Later models, retrieval strategies, prompt structures, and agent harnesses can behave differently.

Likewise, there is no universal point at exactly 100,000 tokens where all models become ineffective. Treat any such number as a workflow-specific warning threshold that must be validated for the selected model and task.

## Why More Context Can Reduce Quality

### Relevant Evidence Becomes Harder to Locate

A long context can contain many plausible facts. The model must determine which ones govern the current decision, and a key constraint can receive less effective attention when buried among unrelated details.

### Old and New Instructions Can Conflict

Long-running sessions often retain abandoned designs, corrected requirements, or earlier user intentions. Even when the latest instruction should take precedence, stale alternatives create unnecessary ambiguity.

### Tool Output Accumulates Quickly

Build logs, search results, file dumps, generated plans, and tool schemas can consume far more context than the user's messages. A few unbounded outputs can dominate the working set without improving the answer.

### Position and Structure Matter

An unstructured wall of text makes relationships difficult to recover. Headings, explicit priorities, source labels, and concise summaries help the model identify which facts belong together and which rules are binding.

### Compaction Can Lose Detail

When an agent summarizes a long conversation, the new context becomes smaller but less exact. Requirements, unresolved questions, or failed approaches may disappear unless they were saved in durable project artifacts.

## Smaller Is Not Automatically Better

Removing required evidence creates a different failure mode. The agent may:

- Rediscover the same repository facts
- Guess about interfaces or constraints
- Repeat previously rejected approaches
- Ask avoidable questions
- Produce an answer that is concise but wrong
- Spend more tokens repairing the result than the shorter prompt saved

Good context is **sufficient, relevant, current, structured, and traceable**. Token count is only one dimension.

| Context state | Likely outcome |
| --- | --- |
| Too little | Guessing, repeated exploration, missed constraints |
| Large but focused | Appropriate for genuinely complex, evidence-heavy tasks |
| Large and noisy | Higher cost and latency, relevance dilution, contradictions |
| Compact and sufficient | Efficient processing with the necessary evidence preserved |

## Place Important Information Deliberately

Do not rely solely on moving every important statement to the end. That can create duplication and new conflicts. Use a stable structure:

1. Put durable behavioral and safety rules in the appropriate system or repository-instruction layer.
2. State the current objective and success criteria clearly in the task prompt.
3. Load only the source files and evidence needed for that objective.
4. Separate requirements, background, constraints, and output format with headings.
5. Restate a small number of critical task-specific constraints near the requested action when necessary.
6. Ask the agent to verify decisive facts against their authoritative source before acting.

For example:

```markdown
## Objective
Fix duplicate payment submission without changing the public API.

## Relevant evidence
- `src/payments/submit.ts`: current request flow
- `tests/payments/idempotency.test.ts`: required behavior
- Incident log excerpt below: confirmed race sequence

## Constraints
- Preserve the existing endpoint contract.
- Do not add a new production dependency.

## Done when
- The focused regression test passes.
- Existing payment tests still pass.
```

This is easier to use than scattering the same facts throughout a long conversation.

## Reduce Noise without Losing State

### Remove Old Tasks from the Conversation

When the objective changes, start a fresh session or fork the current one. Do not delete legitimate repository files; simply stop loading files and history that are unrelated to the new task.

### Share Focused File Sections

Search for relevant symbols first, then inspect bounded sections. Provide the surrounding code needed to understand contracts and control flow, not an arbitrary fragment or the entire repository.

### Summarize Long Investigations

Replace repeated exploratory discussion with a concise handoff containing:

- Current objective
- Confirmed facts and their sources
- Decisions and rationale
- Files changed
- Checks already run
- Remaining uncertainty and next action

Save this state in a project file when it must survive a new session.

### Compact the Same Objective

Use compaction when the task remains the same but its history has become noisy. Review the resulting summary before relying on it for high-risk work.

### Start Fresh for a Different Objective

A new session is often cleaner than compacting unrelated work together. Load the concise handoff and relevant project artifacts instead of replaying the full conversation.

### Control Tool Context

- Disable unrelated MCP servers and tools when their definitions occupy context.
- Limit log ranges and search-result counts.
- Return concise findings from isolated investigations.
- Avoid loading duplicate versions of the same document.
- Keep generated artifacts only when they support the current decision.

## Choosing a Practical Threshold

Do not adopt 100,000 tokens, 13%, or any other number as a universal cutoff. Establish a threshold from evidence in the actual workflow.

Track:

- Task success and factual accuracy
- Retrieval of constraints placed at different positions
- Latency to the first useful response
- Input, output, and cache-token usage
- Number of clarification and repair turns
- Compaction frequency and information loss
- End-to-end cost per completed task

For a repeatable evaluation, keep the model and task constant, vary the amount and position of irrelevant material, and compare results across multiple runs. A single impressive or disappointing session is not a reliable benchmark.

```text
same task + same evidence
        ↓
short focused context ── measure quality, latency, and cost
        ↓
long noisy context ───── measure the same outcomes
        ↓
decide from repeated results, not window size alone
```

## Practical Workflow

Before each meaningful agent task:

1. Confirm the current objective and expected deliverable.
2. Identify authoritative sources and required constraints.
3. Load only the relevant files, sections, and tool definitions.
4. Put the request and success criteria in a clear structure.
5. Monitor both percentage and absolute context use.
6. Persist decisions and verified progress outside the chat.
7. Compact when continuing the same task with excessive history.
8. Start a new session when the objective changes.
9. Validate the result against tests or source evidence.

## Common Mistakes

- Treating the advertised maximum as a target occupancy
- Assuming every current model has a one-million-token window
- Treating 13% as small without checking the absolute token count
- Claiming that performance always collapses after exactly 100,000 tokens
- Assuming every fact receives equal attention because it fits in context
- Putting a critical requirement only in the middle of an unstructured document
- Repeating the same instruction at many positions and creating conflicts
- Removing necessary evidence merely to lower the token counter
- Keeping old tasks in the same session after the objective changes
- Compacting without preserving requirements, decisions, and progress
- Evaluating context strategy from a single run

## Key Takeaway

A large context window is valuable capacity, but capacity is not the same as reliable use. Long, noisy contexts can dilute relevant evidence and expose positional weaknesses such as “Lost in the Middle.” Keep the working set focused and structured, preserve durable state outside the conversation, and choose compaction or a new session according to whether the objective has changed. There is no universal 100,000-token performance cliff: measure the selected model on representative tasks and optimize for correct completion rather than the smallest possible prompt.

## Practice and Further Reading

- [Anthropic Academy exercise on AI capabilities and limitations](https://anthropic.skilljar.com/ai-capabilities-and-limitations/457834)
- [Liu et al., “Lost in the Middle: How Language Models Use Long Contexts”](https://doi.org/10.1162/tacl_a_00638)
- [Claude Platform documentation: Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- [Claude Platform documentation: Manage tool context](https://platform.claude.com/docs/en/agents-and-tools/tool-use/manage-tool-context)
