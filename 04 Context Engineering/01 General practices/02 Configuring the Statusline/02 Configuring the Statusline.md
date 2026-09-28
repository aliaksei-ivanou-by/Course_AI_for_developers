# Monitoring Context and Token Usage in Coding Agents

A status line makes an agent session observable. It can show which model and project are active, how much context remains, and selected usage counters without requiring a separate diagnostic command after every turn.

The status line does not manage context by itself. It is an instrument panel: the developer still decides when to narrow the task, remove irrelevant material, compact the conversation, or start a fresh session.

> **Version note:** Status-line fields, defaults, commands, and token accounting can change between product releases. The current Codex documentation says that the default TUI footer contains `model-with-reasoning`, `context-remaining`, and `current-dir`. A screen that shows only a context percentage may come from another release or a customized configuration.

## Four Metrics That Must Not Be Confused

The transcript uses “context” and “tokens consumed” almost interchangeably. They answer different questions.

| Metric | What it answers | How to use it |
| --- | --- | --- |
| Context window | How much material the model can consider in one request, including the space needed for its response and reasoning | Understand the model's per-request capacity |
| Context remaining or occupied | How much of that capacity is currently available or in use | Detect when a long session may need cleanup or compaction |
| Cumulative session tokens | How much input and output has been processed across multiple turns | Compare the relative size of workflows and identify unexpectedly expensive exploration |
| Billable usage | What a provider charges under the active plan, authentication method, token categories, and caching rules | Use provider usage and billing data, not a context percentage, for financial accounting |

Cumulative input can become larger than the context window because it adds work across requests, whereas the context window is a limit on one request. Conversely, a large model window does not mean that the session has already consumed that many tokens.

Other footer items solve different operational problems:

- The model and reasoning level explain which capability and latency profile is active.
- The current directory and Git branch help prevent edits in the wrong project or branch.
- A pull request number is useful only when the session is associated with a pull request.
- Rate-limit information describes account capacity over time, not context occupancy.

## Inspect the Current Codex Session

Run:

```text
/status
```

Current Codex documentation describes `/status` as a session diagnostic that includes the active model, approval policy, writable roots, and token usage. Use it when the footer is too compact or when an unexpected session setting needs investigation.

Before interpreting any percentage, confirm what it represents. For example, `79% context remaining` means that approximately 21% of the displayed context budget is occupied; it does not mean that 21% of a subscription, rate limit, or monetary budget has been used.

## Configure the Codex Status Line Interactively

In the Codex TUI, open the status-line picker:

```text
/statusline
```

Select and order the fields that are useful for the current workflow. A practical minimal layout is:

1. Model with reasoning level
2. Context remaining
3. Current directory
4. Git branch

If the installed version offers cumulative session-token fields, add them when comparing usage between workflows. Do not treat them as an exact invoice: cached input, output, reasoning, authentication mode, subscription entitlements, and current pricing can all affect cost.

After confirming the picker, send a small request or continue working and verify that the footer shows the intended fields. The picker may offer to save the choice for future sessions.

### Configure the Footer in `config.toml`

Codex reads user configuration from `~/.codex/config.toml` and can also use a trusted project's `.codex/config.toml`. Under `[tui]`, `status_line` is an ordered list of footer item identifiers.

```toml
[tui]
status_line = [
  "model-with-reasoning",
  "context-remaining",
  "current-dir",
  "git-branch",
]
```

The documented default is:

```toml
[tui]
status_line = ["model-with-reasoning", "context-remaining", "current-dir"]
```

An empty list hides the footer:

```toml
[tui]
status_line = []
```

Prefer the interactive picker when unsure about supported item identifiers. It reflects the installed Codex version and avoids copying an identifier that may not exist in that build.

## What Happens on the Next Prompt

The transcript says that sending `hello` causes the entire visible conversation to be sent and charged again. This is a useful warning about growing conversations, but it is too absolute.

Relevant prior messages, tool results, project instructions, and tool definitions can contribute to the next model request. However, the agent harness may compact or summarize earlier material, omit content that no longer fits, and use prompt caching. Therefore:

```text
current context occupancy
    != cumulative session input
    != fresh uncached input on the next request
    != exact monetary cost
```

The practical conclusion is still important: long, unfocused sessions make every later turn carry more material and can reduce both efficiency and attention to the most relevant evidence. The goal is not the smallest possible context. The goal is enough relevant context, with as little irrelevant material as practical.

## Act on the Signal

A useful status line supports a simple decision loop:

```text
observe context and location
          ↓
is the current objective still the same?
       ↙                    ↘
     yes                     no
compact if needed      start or fork a focused session
       ↘                    ↙
  reload only the evidence required for the task
```

Use the following practices:

### Keep One Clear Objective

Avoid mixing unrelated features, investigations, and review requests in one conversation. A new objective usually deserves a new session or a fork rather than carrying all prior exploration forward.

### Persist Durable State in Files

Record accepted requirements, plans, decisions, and verified commands in repository artifacts. The next session can load the relevant files instead of depending on a long conversational history.

### Keep Tool Output Focused

Request the relevant log range, file section, or search result rather than loading an entire large artifact. Large outputs can occupy context even when only a few lines matter.

### Compact When the Objective Is Unchanged

Use `/compact` when the same task must continue but the conversation has accumulated substantial exploration. After compaction, restate or verify any critical requirement that must not be lost.

### Start Fresh When the Objective Changes

Use a new conversation, or `/fork` where that workflow is available, when pursuing a different direction. Load only the durable files and evidence required by the new objective.

Do not wait for the context indicator to reach zero. At the same time, do not compact solely because a fixed percentage has been crossed: a coherent, relevant context can be more valuable than an aggressively shortened one.

## Claude Code Example from the Video

The demonstrated Claude Code version enables **verbose output** in its settings and then sends another command so usage details become visible. It also uses:

```text
/context
```

to inspect a visual breakdown of the current context.

Treat this as a version-specific interface example. A verbose mode may expose information beyond token counts, and the location or wording of the setting can change. Its output is diagnostic; enabling it does not reduce context consumption. In a current installation, verify the available commands and the meaning of each reported counter before comparing it with Codex.

The same management principles apply in either tool:

- Inspect context rather than guessing from the number of chat messages.
- Distinguish current occupancy from cumulative usage.
- Keep durable knowledge in project files.
- Compact an ongoing objective and clear or restart for an unrelated one.
- Use provider billing or usage reports for financial accounting.

## Recommended Setup Checklist

1. Confirm the model, reasoning level, working directory, and Git branch.
2. Keep context remaining visible in the footer.
3. Add cumulative usage only when it helps answer a real operational question.
4. Run `/status` when a compact footer does not provide enough detail.
5. Use `/context` in Claude Code when supported to identify what occupies the window.
6. Persist stable decisions in repository files before compacting or ending the session.
7. Start a focused session when the objective changes.
8. Check the provider's usage and billing view before drawing cost conclusions.

## Common Mistakes

- Assuming a context percentage is a cost percentage
- Comparing cumulative session tokens with a single-request context limit
- Treating every displayed input token as newly billed uncached input
- Adding every available footer field until the important signals become hard to see
- Using the wrong directory or branch while focusing only on token counters
- Compacting so aggressively that necessary requirements disappear
- Keeping an unrelated task in the same conversation merely because context remains
- Treating a setting demonstrated in one Claude Code release as a permanent cross-version contract
- Expecting a status line to optimize context automatically

## Key Takeaway

A status line provides observability, not control. In Codex, keep the model, context remaining, working directory, and branch visible; use `/status` for deeper inspection. Interpret context occupancy, cumulative token usage, rate limits, and cost as separate measurements. Then act on the signal by keeping sessions focused, persisting durable state, compacting continued work, and starting fresh when the objective changes.

## Further Reading

- [Codex developer settings and TUI customization](https://learn.chatgpt.com/docs/developer-settings)
- [Codex configuration sample, including `tui.status_line`](https://learn.chatgpt.com/docs/config-file/config-sample)
- [OpenAI guide to conversation state and context windows](https://developers.openai.com/api/docs/guides/conversation-state)
- [OpenAI token-counting guide](https://developers.openai.com/api/docs/guides/token-counting)
- [OpenAI guidance on monitoring, compacting, and forking Codex sessions](https://developers.openai.com/blog/mastering-codex-remote-for-engineering)
