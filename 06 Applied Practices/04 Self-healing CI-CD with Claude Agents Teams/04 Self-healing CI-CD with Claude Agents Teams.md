# Self-Healing CI/CD with Claude Code Agent Teams

**Sources:**

- Internal recorded demonstration (approximately 10 minutes)
- [Claude Code: Agent teams](https://code.claude.com/docs/en/agent-teams)
- [Claude Code: Subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code: Permission modes](https://code.claude.com/docs/en/permission-modes)
- [GitHub CLI: `gh auth login`](https://cli.github.com/manual/gh_auth_login)
- [GitHub CLI: `gh run view`](https://cli.github.com/manual/gh_run_view)
- [GitHub CLI: `gh run watch`](https://cli.github.com/manual/gh_run_watch)
- [GitHub CLI: `gh pr checks`](https://cli.github.com/manual/gh_pr_checks)
- [GitHub Docs: Scopes for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps)
- [GitHub Docs: About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Docs: About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)

A failing pipeline is one of the most repetitive interruptions in engineering work: open the run, find the failed step, copy the error, form a hypothesis, change something, push, and wait. Each loop is short, but the context switching is expensive.

This lesson shows how a coding agent can run that loop itself. Claude Code reads the failed job through the GitHub CLI, an agent team splits the work into log analysis, fixing, and review, the fix is pushed to the existing pull request, and the agent watches the new run until it passes or fails again. In the recorded demonstration, a broken Docker build was diagnosed, fixed, and verified in about five minutes with a single attempt.

The technique is deliberately simple. Its value comes from knowing which features the tool already has—CLI access, plan mode, agent teams, and per-agent model selection—and from limiting what the agent is allowed to do.

## Learning Objectives

By the end of this lesson, you should be able to:

- describe the self-healing loop: read logs, diagnose, fix, push, watch, and repeat;
- explain why a CLI such as `gh` can replace an MCP server for CI/CD work;
- scope the agent's GitHub access and protect branches against accidental damage;
- write a short, precise prompt that starts the loop from a link to a failed job;
- assign models to agent-team roles by task complexity to control cost;
- recognize when a subagent or a single session is enough instead of a team;
- define stop conditions and review rules so that "green" does not mean "weakened"; and
- adapt the workflow to GitLab or on-premises Git hosting.

## Version Notice

Agent teams are an **experimental** Claude Code feature and are disabled by default. They are enabled with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; see the course lesson [Claude Code Agent Teams](../../04%20Context%20Engineering/03%20Sub-Agents/02%20Claude%20Code%20Agent%20Teams/02%20Claude%20Code%20Agent%20Teams.md) for setup and display modes. Behavior, model names, and limitations change quickly—details below were checked against the official documentation in **October 2026**.

The recording assigned Haiku, Sonnet, and Opus to different roles. Model families and versions available to you depend on your plan and your organization's model allowlist. If a requested model is blocked, Claude Code substitutes another one, so verify which models your teammates actually ran on.

## The Case

The lesson follows the structure used throughout the Applied Practices module.

| Element | In the demonstration |
| --- | --- |
| Starting state | A pull request that prepares a Kafka image and GitHub Actions workflows for an on-premises Kubernetes deployment; the Docker build job fails |
| Objective | Make the pipeline pass without manual log copying or investigation |
| Constraints | Sandbox environment; limited GitHub token; no new pull requests; keep model spend low |
| Plan | Claude Code in plan mode proposes an agent team: log reader, fixer, reviewer, lead |
| Execution | Teammates read logs, fix the build, review the change; the lead pushes to the PR branch and triggers the workflow |
| Verification | The new workflow run: build stage passes, followed by the security-scan stage |
| Evidence | The PR diff, the commit, and the successful run in GitHub Actions |
| Retrospective | One iteration, about five minutes; harder failures may need several loops and up to roughly half an hour |

The sandbox matters. Letting an agent push fixes and re-run pipelines on its own is reasonable when a mistake is cheap. On a production repository the same loop needs stronger review gates, described later.

## The Self-Healing Loop

```text
Link to failed job
      │
      ▼
Read failed logs (gh run view --log-failed)
      │
      ▼
Diagnose root cause ──► Propose fix ──► Review fix
                                            │
                                            ▼
                          Commit and push to the PR branch
                                            │
                                            ▼
                           Watch the new run (gh run watch)
                                            │
                    ┌───────────────────────┴───────────────┐
                    ▼                                       ▼
                 Passed                                  Failed
                    │                                       │
              Report and stop              New logs → back to diagnosis
                                           (until the attempt limit)
```

The loop is "self-healing" only in a narrow sense: the agent repeats the same steps a developer would take. It does not make the pipeline more robust by itself, and it needs a defined exit when it cannot find a fix.

## Why a CLI Instead of an MCP Server

The demonstration used the **GitHub CLI** (`gh`) rather than a GitHub MCP server. For CI/CD work this has several advantages:

- **No extra tool definitions in context.** An MCP server adds its tool schemas to every request; a CLI is invoked only when needed. See [Reducing MCP Server and Tool Context Overhead](../../04%20Context%20Engineering/01%20General%20practices/06%20Reducing%20the%20number%20of%20MCP%20servers/06%20Reducing%20the%20number%20of%20MCP%20servers.md).
- **Familiar, inspectable commands.** Every action appears as an ordinary command that the developer can read, approve, or repeat manually.
- **Existing authentication.** The agent acts with the developer's existing `gh` login and its scopes—no separate integration to configure.
- **Targeted output.** Commands can return only what is needed, such as the logs of failed steps.

Useful commands for this workflow:

```bash
gh pr checks <PR> --watch          # status of all checks on the pull request
gh run list --branch <branch>      # recent runs for the branch
gh run view <run-id> --log-failed  # logs of failed steps only
gh run view <run-id> --job <job-id> --log
gh run rerun <run-id> --failed     # re-run only failed jobs
gh run watch <run-id>              # follow a run until it finishes
```

`--log-failed` is the key to keeping cost low: it gives the model the failing steps instead of thousands of lines of successful output.

## Scope the Agent's Access

The agent runs commands with your credentials, so its permissions are your permissions. The recording relied on the default `gh` token and branch protection as safety boundaries.

### What the Default `gh` Token Can and Cannot Do

`gh auth login` requests the scopes `repo`, `read:org`, and `gist` by default.

| Action | Default `gh` token |
| --- | --- |
| Read code, pull requests, and workflow logs | Yes |
| Push commits and re-run workflows | Yes |
| Delete branches | Yes—unless protected |
| Delete repositories | No—requires the `delete_repo` scope |
| Delete packages | No—requires the `delete:packages` scope |
| Modify files under `.github/workflows/` | No—pushing workflow changes requires the `workflow` scope |

The last row is important for CI/CD repair. If the root cause is in a workflow file, the push is rejected until the `workflow` scope is added (`gh auth refresh --scopes workflow`). Treat that as a deliberate decision, not a hurdle to remove automatically: workflow files control what runs with your repository secrets.

### Protect Branches

The recording's advice is simple: if you are worried that the agent might delete a branch, protect it. Branch protection rules or rulesets can:

- prevent deletion of the branch;
- block force pushes;
- require pull requests and approvals before merging to the default branch; and
- require status checks to pass before merging.

One caveat: the classic `repo` scope acts with your full repository role. If you are a repository administrator, the token can also change protection settings. For stronger isolation, use organization-level rulesets without bypass for your role, a fine-grained personal access token limited to one repository and the permissions it needs, or a GitHub App identity for the agent.

### Run in a Sandbox First

The demonstration ran against a sandbox repository and infrastructure. Start there. A self-healing loop that pushes and triggers pipelines can also trigger deployments, consume runner minutes, and publish images—check what the workflow does after the step that is failing.

## Prepare the Session

### Start Clean

Begin with a new session (`/clear`) instead of continuing a long conversation. The recording checked the status line before starting: unrelated earlier context is paid for on every request and distracts the model. See [One Task, One Chat](../../04%20Context%20Engineering/01%20General%20practices/05%20Dividing%20tasks%20by%20sessions/05%20Dividing%20tasks%20by%20sessions.md) and [Configuring the Status Line](../../04%20Context%20Engineering/01%20General%20practices/02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline.md).

### Provide Project Context

The repository already contained an `AGENTS.md` file, with `CLAUDE.md` as a symbolic link to it, explaining what the project is and how it works. This saved time on codebase exploration—and every teammate loads that project context when it starts. See [Generating Project Instructions for Coding Agents](../../04%20Context%20Engineering/01%20General%20practices/01%20Generating%20the%20agent%20instructions/01%20Generating%20the%20agent%20instructions.md).

### Say That the Code Is Local

A small but useful detail: the prompt stated that the codebase is available locally. Without that hint, the agent may read files through the GitHub API, which is slower, costs more tokens, and does not reflect uncommitted local state.

### Use Plan Mode

The session ran in plan mode, so Claude first investigated the failing job and presented a plan—what is wrong and which team it intends to create—before changing anything. Read the plan carefully; it is the cheapest point at which to correct the approach.

Note that in an agent team, a teammate spawned while the lead is in plan mode sends its own plan to the lead, and the lead session approves it automatically. Your review of the lead's plan is therefore the main human gate; the teammates' edits and commands still go through normal permission prompts.

## The Prompt

The recording used a short prompt with a link to the failing job. A cleaned-up version:

```text
<link to the failed GitHub Actions job>

Check and fix this pipeline. Set up an agent team to self-heal this CI/CD pipeline.

Assign models to teammates according to task complexity:
- Haiku for reading the logs
- Sonnet for code changes
- Opus for orchestration
- Opus for reviewing the code changes

Push fixes to the existing pull request branch. Do not create new pull requests.
The codebase is available locally.
```

What makes it effective:

| Element | Purpose |
| --- | --- |
| Link to the failed job | Gives the agent the exact run and job without manual copy-pasting of errors |
| "Set up an agent team" | Explicitly requests a team; otherwise Claude may choose subagents or a single session |
| Model per role | Keeps routine, high-volume reading on a cheap model and reserves expensive models for judgment |
| "Push to the existing PR" | Keeps the fix in the pull request that failed instead of creating extra PRs |
| "Codebase is available locally" | Avoids reading files through the GitHub API |

## Model Assignment by Task Complexity

| Role | Model in the recording | Why |
| --- | --- | --- |
| Log reader | Haiku | Logs are long but the task is extraction: find the failing step and the error |
| Fixer | Sonnet | Needs to understand the code and make a correct, minimal change |
| Lead / orchestrator | Opus | Interprets the goal, coordinates teammates, decides when the work is done |
| Reviewer | Opus | Judges whether the fix addresses the root cause and does not weaken the pipeline |

The principle is more durable than the specific model names: **pay for reasoning where reasoning matters**. You can also let Claude choose models by complexity itself—the recording noted that this works too, and that there is no need to over-engineer the setup for a simple case. What matters is knowing that the tool can assign different models to different workers.

## What Happened in the Demonstration

1. Claude inspected the failing job and proposed a team in its plan.
2. The log reader started on Haiku and extracted the error from the Docker build logs.
3. The lead spawned a fixer teammate to change the build.
4. The change was reviewed, committed, and pushed to the pull request branch; the agent triggered the workflow on the developer's behalf.
5. The lead watched the run. The build stage passed, followed by the image security-scan stage.
6. The pipeline succeeded after **one attempt**, roughly **five minutes** after the prompt.

In the in-process display mode, you can select any teammate in the agent panel to see its transcript or send it instructions. Split panes show all agents at once but require `tmux` or iTerm2.

The recording estimated that a harder failure may take up to about half an hour of repeated loops. That is an observation from practice, not a benchmark.

## Is an Agent Team Necessary?

For one failing Docker build, a single session or one log-reading subagent would probably have been enough. The official documentation notes that agent teams use significantly more tokens than a single session because every teammate is a separate Claude instance.

| Situation | Lightest suitable option |
| --- | --- |
| One job, one obvious error | Single session with `gh run view --log-failed` |
| Very long logs that would flood the main context | A subagent on a cheap model that returns only the relevant error |
| Several failing jobs with independent causes | Agent team, one teammate per failure area |
| Unclear cause with competing hypotheses | Agent team whose members try to disprove each other's theories |
| Fix that must be reviewed independently before push | Team or subagent with a separate reviewer role |

The demonstration is still a useful template: once the roles and the prompt work on a simple failure, the same setup scales to harder ones.

## Guardrails for an Autonomous Loop

A self-healing loop optimizes for one signal: a green pipeline. Without constraints, an agent can reach that signal in harmful ways. Add explicit rules to the prompt or to project instructions:

- **Fix the root cause.** Do not disable, skip, or delete tests, linters, or security scans to make the pipeline pass.
- **Do not weaken security.** Do not lower scanner severity thresholds, add blanket ignore rules, or remove signature and provenance checks.
- **Limit attempts.** Stop after a fixed number of loops (for example, three) and report findings instead of trying indefinitely.
- **Limit scope.** Change only files related to the failure; explain every change in the commit message.
- **Do not touch secrets.** Never print, rotate, or modify repository secrets; logs may contain sensitive values that are not masked.
- **Keep the human merge.** The agent may push to the PR branch, but merging into the default branch remains a human decision with review.

Then review the result as you would any pull request: read the diff, confirm that the fix is plausible, and check that no checks were removed.

## Adapting the Workflow

| Environment | Adaptation |
| --- | --- |
| GitHub.com | Works as shown with `gh` |
| GitLab.com | Use the GitLab CLI (`glab`) for pipelines, jobs, and logs; scope the token similarly |
| On-premises GitHub Enterprise Server or GitLab | Authenticate the CLI against the internal host; the agent may need VPN or network access from where it runs |
| No CLI access to CI logs | Fall back to an approved MCP integration, or provide exported logs manually |
| Customer repositories | Confirm that the customer permits AI agents to read code and logs and to push changes, and follow their safety requirements |

As the recording concludes: if a customer encourages AI use with appropriate responsibility and safety precautions, this workflow can be applied directly.

## Practical Exercise

Use a sandbox repository with a GitHub Actions workflow.

1. Protect the default branch: block deletion and force pushes, and require a pull request to merge.
2. Introduce a deliberate failure on a feature branch—for example, a wrong base-image tag or a missing file in the Docker build context—and open a pull request.
3. Confirm your `gh` login and its scopes with `gh auth status`.
4. Enable agent teams and start a clean Claude Code session in plan mode.
5. Use the prompt above with the link to the failed job, and add an attempt limit and the guardrails from this lesson.
6. Review the plan; approve it only if the proposed fix targets the root cause.
7. Observe the teammates in the agent panel and note which models they used.
8. When the run passes, review the diff and confirm that no checks were weakened.
9. Repeat with a single session and `gh run view --log-failed` only. Compare time, token usage, and result quality.
10. Record which setup you would use for routine failures and which for complex ones.

## Common Mistakes

- Copying and pasting errors into the chat instead of letting the agent read the logs
- Starting the repair in a long, unrelated session full of old context
- Granting broad tokens (`workflow`, `delete_repo`, administrator rights) by default
- Leaving branches unprotected while an agent can push and delete
- Running every role on the most expensive model
- Creating an agent team for a trivial failure and paying for coordination overhead
- Not telling the agent that the code is local, so it reads files through the API
- Letting the loop run without an attempt limit
- Accepting a green pipeline without checking whether tests or scans were disabled
- Running the loop against production systems before it has been proven in a sandbox

## Key Takeaway

Self-healing CI/CD is a small, practical use of agentic tools: give the agent a link to the failed job, CLI access with limited permissions, project context, and a clear plan-mode prompt, and it will read the logs, fix the problem, push, and watch the pipeline until it passes. Agent teams and per-role model selection keep expensive reasoning where it matters and cheap models on log reading. The developer's work shifts to setting boundaries—token scopes, branch protection, attempt limits, and rules against weakening checks—and to reviewing the final diff before it is merged.
