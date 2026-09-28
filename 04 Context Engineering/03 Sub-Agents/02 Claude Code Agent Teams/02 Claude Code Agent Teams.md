# Claude Code Agent Teams

**Source:** [Learn 90% of Claude Code Agent Teams in 22 Minutes](https://www.youtube.com/watch?v=cSkoaCCmq0w)  
**Format:** Public YouTube video  
**Duration:** Approximately 22 minutes

Claude Code Agent Teams coordinate several independent Claude Code sessions around a shared objective. One session acts as the team lead, teammates work in their own context windows, and the team uses shared tasks and direct messages to coordinate parallel work.

Agent teams can examine a problem from several perspectives at once, but they also consume substantially more tokens and introduce coordination overhead. They are useful only when the work can be divided into meaningful, mostly independent streams.

## Version Notice

Agent Teams is an experimental Claude Code feature, so configuration, interface behavior, model availability, pricing, and limitations can change.

The video demonstrates an earlier setup based on Claude Code with Opus 4.6. The current official workflow still uses the `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` flag, but the documented display setting is `teammateMode`. The default in-process interface does not require `tmux`.

Use the [current Agent Teams documentation](https://code.claude.com/docs/en/agent-teams) as the source of truth when performing the exercise.

## Three Ways to Organize Work

Claude Code supports several related patterns. Choose the lightest one that can complete the task reliably.

| Pattern | Context and coordination | Best fit | Main trade-off |
| --- | --- | --- | --- |
| Main session | One conversation performs and observes all work | Sequential tasks and work requiring continuous user interaction | Large investigations can fill the main context |
| Subagent | A focused worker uses a separate context and returns a result to its caller | Research, verification, review, or another bounded task | Intermediate detail is compressed during handoff |
| Agent team | Independent Claude Code sessions coordinate through messages and a shared task list | Complex parallel work requiring collaboration between workers | Higher token use and coordination overhead |

The following diagram summarizes the three modes shown in the video:

![Comparison of Claude Code default mode, subagents, and agent teams](Claude%20Code%20Work%20Modes.png)

The architectural difference matters more than the number of agents. An agent team is not merely a larger group of subagents: each teammate is an independent session that can communicate with the lead and other teammates.

## When to Use Agent Teams

Agent teams are strongest when parallel exploration provides real value:

- several reviewers can inspect security, performance, and test coverage independently;
- investigators can test competing debugging hypotheses and challenge one another;
- a feature can be split across frontend, backend, and tests with clear ownership;
- researchers can analyze different evidence sources or opposing viewpoints; or
- new modules can be implemented in separate files with limited dependencies.

Prefer a single session or a subagent when:

- tasks must be performed in a strict sequence;
- several workers would need to edit the same files;
- the task is too small to justify team startup and coordination;
- one worker cannot proceed until another exposes detailed intermediate findings; or
- the main conversation needs to observe and react to every step.

> **Decision rule:** Use an agent team when teammates need independent contexts *and* need to exchange findings or coordinate work with one another.

## Team Architecture

An agent team contains four main elements:

| Component | Responsibility |
| --- | --- |
| Team lead | Interprets the objective, creates or assigns work, monitors progress, and synthesizes results |
| Teammates | Work independently in separate Claude Code sessions |
| Shared task list | Tracks pending, in-progress, completed, and dependent tasks |
| Messaging system | Delivers messages between the lead and teammates, or directly between teammates |

![Lifecycle of a Claude Code agent team](Agent%20Team%20Lifecycle.png)

Task claiming uses locking so that two teammates do not intentionally claim the same shared task at the same time. This does not prevent accidental overlap caused by vague assignments, so the lead should still define clear responsibilities and file ownership.

## Enable Agent Teams

First update Claude Code through the installation method used on your machine and verify that the installed version supports Agent Teams.

Agent teams are disabled by default. Enable them through a Claude Code `settings.json` file or an environment variable. A user-level configuration can look like this:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

User-level settings normally live at `~/.claude/settings.json`. On Windows, `~/.claude` resolves to `%USERPROFILE%\.claude`.

Because this is an experimental feature, enabling it can also affect ordinary delegation: a named subagent may launch as a teammate while agent teams are enabled. Set the variable to `0` when you want named workers to behave as ordinary subagents again.

## Choose a Display Mode

Agent teams support two primary presentation styles:

| Mode | Behavior | Requirements |
| --- | --- | --- |
| In-process | Teammates appear inside the lead's terminal and can be selected from the agent panel | Works in any terminal; no additional setup |
| Split panes | Each teammate receives a visible terminal pane | Requires `tmux` or iTerm2 support |

The default is in-process mode. To use automatic split panes when the environment supports them, add `teammateMode`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "teammateMode": "auto"
}
```

You can also choose the mode for one launch:

```bash
claude --teammate-mode auto
```

`tmux` is optional and is only needed for its split-pane workflow. Current Claude Code documentation notes that split panes are not supported in the VS Code integrated terminal or Windows Terminal; use in-process mode there. On supported macOS or Linux terminal setups, `tmux` can provide a separate pane for each teammate.

## Start a Team

Ask explicitly for an agent team and describe the roles, boundaries, deliverables, and model requirements. For example:

```text
Create an agent team to review PR #142.

Use three teammates:
1. Security reviewer: inspect authentication, authorization, and input handling.
2. Performance reviewer: inspect database access, allocations, and hot paths.
3. Test reviewer: assess coverage, missing edge cases, and regression risk.

Each teammate must cite files and lines, report obstacles, and avoid modifying code.
Wait for all three reports, reconcile duplicate findings, and return one prioritized summary.
Use Sonnet for the teammates.
```

A strong team prompt defines:

- the shared objective;
- the number and names of teammates;
- a distinct perspective or file scope for each teammate;
- allowed actions and tools;
- the expected result from each worker;
- how conflicts or duplicate findings should be handled; and
- the condition for declaring the team finished.

Claude may decide that a simpler mechanism is sufficient. If the task genuinely requires a team and Claude creates ordinary subagents instead, restate that you explicitly want an agent team.

## Give Teammates Enough Context

Teammates load normal project context such as `CLAUDE.md`, configured MCP servers, and available skills. They do **not** inherit the lead's conversation history.

The lead must include task-specific context in each spawn prompt:

- exact files, modules, or URLs to inspect;
- relevant architectural decisions;
- current symptoms or observed failures;
- constraints and non-goals;
- the definition of done; and
- the required output format.

Do not assume that a teammate knows what the lead discussed ten minutes earlier. Put durable project facts in appropriate repository documentation and pass temporary task facts explicitly.

## Assign and Coordinate Work

The lead can assign tasks to named teammates, while teammates with access to the shared task tools can claim available unblocked work themselves. Dependencies prevent a task from being claimed until its prerequisites are complete.

Good tasks are:

- large enough that parallel execution saves meaningful time;
- small enough to finish with a clear deliverable;
- independent from other active tasks; and
- scoped to distinct files or analysis domains.

Avoid assigning two editing teammates to the same file. File-level ownership reduces overwrites and conflicting implementations.

Current guidance suggests beginning with three to five teammates for most workflows. More teammates increase token cost, communication, and conflict risk; they do not guarantee proportionally faster results.

## Monitor and Steer the Team

In in-process mode, select a teammate in the agent panel to inspect its transcript or send it an additional instruction. In split-pane mode, interact with the relevant pane.

Monitor for:

- duplicated or overlapping work;
- a teammate blocked by missing context or permissions;
- tasks reported as unfinished even though the work is complete;
- a teammate pursuing an unproductive approach;
- the lead beginning implementation before required research is finished; and
- conclusions that conflict across teammates.

If necessary, tell the lead to wait for all assigned work, redirect a teammate, update a stale task, or replace a failed worker.

## Models, Effort, and Cost

Each teammate has its own context window and sends its own model requests. Token use therefore grows with the number of active teammates.

You can request a model in the spawn prompt:

```text
Spawn four teammates to analyze these independent modules. Use Sonnet for each teammate.
```

Choose the least expensive model that can complete each role reliably. A simple file inventory may not need the same model as an architectural review or ambiguous debugging investigation.

Do not treat the video's observed session price as a reusable estimate. Actual cost depends on the selected models, prompts, cache behavior, task duration, tool results, and number of teammates. Review usage after representative runs and adjust team size, task boundaries, and model selection.

## Permissions and Safety

Teammates generally start with the lead's permission mode, and their permission requests surface in the lead session.

The video launches Claude Code with permission checks bypassed for demonstration. Do not use that mode as a general setup recommendation. With several independent sessions, bypassing permission checks expands the number of processes that can modify files or execute commands without confirmation.

Prefer:

- normal permission prompts;
- explicit allowlists for routine safe operations;
- read-only teammates for research and review;
- isolated branches or worktrees for independent implementation;
- clear file ownership; and
- review of the final diff before merging or deployment.

Never place secrets in shared prompts, logs, task descriptions, or memory files.

## Shut Down Teammates Cleanly

Ask the lead to shut down an unneeded teammate by name:

```text
Ask the performance-reviewer teammate to shut down.
```

The teammate can finish its current operation, approve the request, and exit gracefully. Before ending a coding team:

1. Confirm that all required tasks are complete.
2. Run the relevant tests and validation.
3. Review the combined changes for conflicts.
4. Record any unresolved decisions or limitations.
5. Shut down teammates and end the lead session.

The team configuration is cleaned up when the session ends, while task data may remain available according to Claude Code's retention behavior.

## Preserve Useful Knowledge

The video suggests a shared Markdown file for bugs, attempted fixes, and decisions. This can be useful when information must survive a session, but treat it as a deliberate project artifact rather than an unrestricted scratchpad.

A useful handoff file can record:

```markdown
# Team Handoff

## Decisions
- Decision, rationale, and affected files

## Completed Work
- Task, owner, and verification result

## Known Issues
- Symptom, attempted approaches, and current hypothesis

## Next Steps
- Owner, dependency, and definition of done
```

Assign one owner or use append-only sections to avoid concurrent edits to the same document.

## Turn a Successful Workflow into a Skill

After a team workflow succeeds repeatedly, package the repeatable instructions as a skill. The video demonstrates this with a research-team process.

![Turning an agent-team workflow into a reusable skill](Agent%20Team%20Workflow%20to%20Skill.png)

A reusable team skill can define:

- required inputs such as the research topic;
- default and optional teammate roles;
- model-selection rules;
- source and citation requirements;
- communication and challenge rules;
- expected final report structure; and
- shutdown and verification steps.

Develop the workflow manually first. Once the sequence and failure modes are understood, ask Claude to convert the proven process into a skill and review the generated `SKILL.md`. Update the skill whenever the real workflow changes.

## Current Experimental Limitations

Check the official documentation before relying on Agent Teams. Current limitations include:

- in-process teammates are not restored by session resume or rewind;
- task status may occasionally lag behind completed work;
- shutdown can wait for an active request or tool call;
- each session has one team and one fixed lead;
- teammates cannot create nested teams;
- split panes require supported `tmux` or iTerm2 environments; and
- same-file edits remain vulnerable to conflicts and overwrites.

These limitations reinforce the main operating principle: keep teams small, tasks independent, ownership explicit, and progress observable.

## Practical Exercise

Use a read-only workflow for the first experiment:

1. Enable Agent Teams in `settings.json`.
2. Start Claude Code in in-process mode.
3. Select a repository or pull request with enough complexity for parallel review.
4. Spawn three teammates for security, performance, and test coverage.
5. Require file-and-line evidence and an `Obstacles Encountered` section.
6. Inspect each teammate's progress and redirect unclear work.
7. Ask the lead to synthesize and deduplicate the findings.
8. Review token usage and decide whether the team produced enough value to justify its cost.
9. Shut down the team cleanly.

## Recap

- Agent teams coordinate independent Claude Code sessions through messages and shared tasks.
- Use them when workers need to collaborate across genuinely parallel workstreams.
- Use a single session or subagents for smaller, sequential, or tightly coupled tasks.
- Agent Teams remains experimental and must currently be enabled explicitly.
- In-process mode works without `tmux`; split panes require a supported external terminal setup.
- Teammates receive project context and a spawn prompt, but not the lead's conversation history.
- Clear roles, task boundaries, file ownership, and output formats reduce wasted work.
- Token use grows with the number of teammates, so measure cost instead of relying on one recorded example.
- Preserve permission checks and review the combined result before accepting changes.
- Convert a stable, proven team workflow into a reusable skill when repetition justifies it.

## References

- [YouTube lesson: Learn 90% of Claude Code Agent Teams in 22 Minutes](https://www.youtube.com/watch?v=cSkoaCCmq0w)
- [Official Claude Code Agent Teams documentation](https://code.claude.com/docs/en/agent-teams)
