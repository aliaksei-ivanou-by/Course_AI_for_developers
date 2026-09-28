# Executing the Implementation Plan with Spec Kit

The `implement` stage turns the approved artifacts into working software. It reads `tasks.md`, executes the work phase by phase, respects dependencies and parallel markers, runs validation, and marks verified tasks as complete.

This lesson follows the desktop 3D-space modeling MVP from task generation through implementation, manual validation, and preparation for the next feature.

> **Version note:** The current core workflow continues beyond `implement` with `converge`, which checks the resulting code against the specification, plan, and task list. Implementation is therefore not complete merely because an agent reports that all tasks ran.

## Position in the Workflow

Implementation consumes the durable decisions created by the earlier stages:

```text
constitution   project-wide rules
spec.md        required behavior and success criteria
plan.md        architecture and technical approach
tasks.md       ordered implementation checklist
      ↓
analyze        pre-implementation consistency check
      ↓
implement      code, tests, validation, and task progress
      ↓
converge       post-implementation gap detection
      ↓
review         human review, commit, pull request, and merge
```

`implement` is the first core stage that is expected to make broad changes to application code. A clean upstream workflow reduces ambiguity, but it does not remove the need to review those changes.

## Reset Context Only After the Inputs Are Durable

The transcript begins by resetting the agent context. This is useful when the accepted requirements, design decisions, and task state are already stored in project files.

Before starting a fresh session, confirm that:

- The correct feature is active.
- `spec.md`, `plan.md`, and `tasks.md` are complete and reviewed.
- The latest `speckit-analyze` findings have been resolved.
- Requirements-quality checklists have been reviewed.
- Important decisions do not exist only in the previous conversation.
- The working tree has a recoverable checkpoint.
- Required secrets and credentials are not embedded in prompts or repository files.

A new session should rediscover context from the artifacts. Resetting a conversation is not a substitute for saving decisions or committing a stable checkpoint.

## Invoke the Implement Skill

Command syntax depends on the selected coding-agent integration:

| Integration or reference style | Example |
| --- | --- |
| Claude Code or another hyphenated skills layout | `/speckit-implement` |
| Canonical dotted notation in Spec Kit references | `/speckit.implement` |
| Codex skills integration | `$speckit-implement` |

For a small, low-risk feature, the basic invocation can execute the complete task list:

```text
/speckit-implement
```

The command also accepts free-form implementation guidance or a task filter. For a larger feature, scope each run explicitly:

```text
/speckit-implement

Execute only the Setup and Foundational phases. Stop after their validation
passes, update completed tasks in tasks.md, and report changed files, commands,
test results, and any blockers. Do not begin User Story 1.
```

Other useful scopes include:

```text
/speckit-implement Only execute tasks T001-T010, then stop and report progress.
```

```text
/speckit-implement Implement User Story 1 only, validate it independently, and stop.
```

The filter should narrow an approved plan, not change the feature. New product behavior belongs in `spec.md`; new architectural choices belong in `plan.md`.

## What the Current Implement Workflow Does

The core command performs more than a loop over task descriptions.

### 1. Run Pre-Implementation Hooks

If enabled extensions register `before_implement` hooks, the command identifies them and executes mandatory hooks before continuing. Optional hooks are reported for the user to invoke when appropriate.

Hooks can add security, compliance, review, or organizational gates. Treat extension code as part of the project's trusted toolchain and review it before installation.

### 2. Resolve the Active Feature and Prerequisites

The setup script locates the active feature directory and requires an implementation task list. If `tasks.md` is missing or incomplete, return to the `tasks` stage rather than improvising the entire implementation from chat history.

### 3. Check Requirements-Quality Checklists

When `checklists/` exists, `implement` counts checked and unchecked items. If any checklist remains incomplete, it reports the failure and asks whether implementation should continue.

These checklist markers are read-only during implementation:

- A checked requirement-quality item means a reviewer accepted the quality of that requirement.
- It does not mean the corresponding code is implemented.
- The implementation command must not silently approve or edit reviewer-owned checklist items.

This differs from `tasks.md`, where `[X]` means a specific implementation task has been completed and verified.

### 4. Load the Implementation Context

The command requires:

- `tasks.md` for execution order and progress
- `plan.md` for the stack, architecture, and file structure

It also reads available supporting artifacts:

- `data-model.md`
- `contracts/`
- `research.md`
- `quickstart.md`
- The project constitution

The agent must implement the combined contract represented by these files. It should not choose whichever document is easiest to follow when they conflict; that conflict should have been fixed before implementation.

### 5. Verify Project Hygiene

The current command detects relevant project tooling and creates or verifies ignore rules such as `.gitignore`, `.dockerignore`, `.prettierignore`, or Terraform and Kubernetes exclusions where applicable.

This matters because build products, local environments, logs, caches, IDE state, and secrets should not enter version control accidentally. Review every automatically added pattern: an overly broad ignore rule can hide required source or configuration files.

### 6. Parse and Execute the Task Graph

The agent extracts phases, task IDs, file paths, dependencies, and `[P]` markers, then executes in dependency order.

Core rules include:

- Complete phases in order.
- Run sequential tasks in their documented order.
- Execute required test tasks before their corresponding implementation.
- Never parallelize tasks that modify the same files.
- Validate a phase before starting a dependent phase.
- Stop when a failed non-parallel task blocks later work.
- Allow independent parallel tasks to complete, but report any failed siblings.
- Mark a task `[X]` only after its work is complete and verified.

### 7. Validate Completion and Run Post-Hooks

Before reporting success, the command checks task completion, conformance with the specification and plan, and required test coverage. It then processes enabled `after_implement` hooks and provides a completion report.

The report is evidence to inspect, not proof by itself.

## Preflight the Development Environment

In the video, implementation stops because the Rust toolchain is not installed. This is a valid blocker: the agent cannot compile or test a Rust application without the required compiler and package tools.

Prefer detecting environment requirements before a long implementation run:

```bash
rustc --version
cargo --version
```

The exact checks should come from `plan.md`, the repository's setup documentation, and pinned toolchain files such as `rust-toolchain.toml` when present.

Before installing a missing system tool:

1. Confirm that it is actually required by the approved plan.
2. Determine the required version and target platform.
3. Use the official installer or the organization's approved package source.
4. Understand whether the change is project-local or system-wide.
5. Avoid pasting unreviewed remote scripts into a privileged shell.
6. Restart or refresh the shell if PATH changes.
7. Re-run version checks and the smallest build command.
8. Record setup instructions so the next developer and CI environment can reproduce them.

Tool installation is an environment change, not ordinary source implementation. An agent should not silently install system software or accept license terms unless that authority is clearly within the task.

## Subagents and the Orchestrator Pattern

The transcript asks the main agent to orchestrate subagents for individual tasks. This can work well when the task graph contains genuinely independent work.

A practical division of responsibility is:

| Role | Responsibility |
| --- | --- |
| Orchestrator | Select ready tasks, enforce dependencies, allocate files, review results, integrate changes, and run repository-level validation |
| Subagent | Complete one narrowly scoped task using only the relevant artifacts and files |
| Human reviewer | Approve consequential choices, evaluate product behavior, and accept the integrated result |

For example:

```text
/speckit-implement

Execute only the current phase. Delegate independent [P] tasks to separate
subagents. Give each subagent one task, explicit allowed files, relevant artifact
excerpts, and its validation command. Keep the main agent responsible for
dependency checks, review, integration, and the final phase test. Stop after the
phase and report evidence.
```

Do not create one subagent for every task mechanically. Delegation is inappropriate when tasks:

- Modify the same files
- Depend on unfinished interfaces or models
- Require a strict test-first sequence
- Change shared build configuration
- Depend on the output of an earlier task
- Are too small to justify coordination overhead

If several agents work on separate feature slices concurrently, use isolated worktrees or equivalent isolated checkouts. Multiple agents should not race over the same working tree, active-feature state, or task markers.

## Model Selection Is Not a Spec Kit Feature

The video assigns a highly capable model to orchestration, a general model to standard implementation, and a smaller model to easy tasks. That is an agent-platform strategy, not behavior defined by Spec Kit.

Model names, availability, limits, and relative strengths change over time. Select models based on the current platform and the risk of the task:

- Use stronger reasoning for architecture-sensitive integration, difficult debugging, security review, and conflict resolution.
- Use faster or cheaper models only for well-specified, low-risk, independently verifiable work.
- Require the same tests and review regardless of model tier.
- Do not assume that a more expensive orchestrator automatically manages context efficiently.

The most reliable optimization is to reduce task scope and context, not merely to route work among model names.

## Monitor Long-Running Implementation

The transcript shows how to inspect subagent status and check whether an agent is waiting for approval. Monitoring is useful, especially when implementation runs for a long time.

Look for:

- A subagent waiting for a permission or clarification
- Repeated commands without meaningful progress
- A failing build retried without addressing the cause
- Tasks being executed out of dependency order
- Concurrent edits to shared files
- Context growth without intermediate checkpoints
- Scope expanding beyond the active feature
- Tests being skipped or weakened to obtain a passing result

A running indicator proves only that a process is active. It does not prove forward progress.

Prefer short execution batches with observable checkpoints. After each phase, the orchestrator should report:

```text
Completed task IDs
Changed files
Validation commands and outcomes
Outstanding failures or assumptions
Current tasks.md state
Next unblocked phase
```

This makes recovery possible even if the session fails or the context must be reset.

## Context Management During Implementation

In the demonstration, the orchestrator accumulated roughly 245,000 tokens while individual subagents used smaller contexts. This indicates that delegation alone did not keep the coordinating session small.

Token counters can represent different things across platforms: current context size, cumulative input and output, cached tokens, or estimated billing. Do not interpret a displayed number without understanding the tool's metric.

More importantly, avoid a universal instruction such as “compact at exactly 100,000 tokens.” The useful threshold depends on the model, agent harness, artifact size, and task complexity. Compaction can also omit details if important state was never recorded in files.

Use structural controls instead:

1. Execute only one phase or a small task range per invocation.
2. Give each subagent only the files and artifact sections it needs.
3. Write progress and decisions back to durable artifacts.
4. Mark verified tasks `[X]` as work completes.
5. Stop and validate at phase boundaries.
6. Start a fresh implementation session for the next phase when useful.
7. Decompose an oversized feature into smaller specifications if one phase is still too large.

Context-management policy usually belongs in agent instructions or a team runbook. Put it in the constitution only when the policy expresses a durable, tool-independent project obligation.

## Prefer Staged Implementation to One Huge Run

The full MVP in the video took approximately one hour and forty-four minutes. A single successful run is possible, but it increases the cost of failures, makes progress harder to inspect, and allows context to accumulate.

A safer sequence is:

```text
Run 1: Setup → validate → stop
Run 2: Foundational → validate → stop
Run 3: User Story 1 → validate as MVP → stop
Run 4: Next user story → validate → stop
Run 5: Polish and cross-cutting checks → stop
```

Because completed tasks are stored as `[X]` in `tasks.md`, the next invocation can resume from durable progress. Always inspect the task list before resuming rather than assuming the previous agent updated it correctly.

When even a single phase does not fit comfortably, split the feature into smaller, independently testable specifications. This adds overhead, so first try phase scoping and carefully selected subagent delegation.

## A Passing Report Is Not Acceptance

The agent in the transcript reports that all phases are complete and all tests pass. Those are useful signals, but acceptance requires independent evidence.

At minimum, inspect:

```bash
git status --short
git diff --stat
git diff
```

Then run the project's documented quality commands yourself or through a trusted CI environment. For a Rust application, a project might use commands such as:

```bash
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-targets --all-features
cargo build --release
```

These are examples, not universal requirements. Use the exact targets, features, and policies approved for the repository.

Also verify that:

- Every required task is marked `[X]` for a valid reason.
- No task was silently skipped.
- Tests were not deleted, weakened, or changed to match a defect.
- The code follows the technical plan and constitution.
- Error paths and boundary cases are exercised.
- No secrets, generated binaries, caches, or local configuration are tracked.
- Dependency and lockfile changes are expected.
- Static-analysis warnings and security findings are addressed according to policy.
- The implementation does not include unrequested future features.

## Validate the MVP Against the Specification

For a graphical desktop application, automated tests alone rarely prove the complete user experience. The video launches the result and manually exercises the modeled workflow.

A requirement-based smoke test for this MVP could include:

| Scenario | Evidence to collect |
| --- | --- |
| Workspace opens successfully | Application launches without an error and displays the modeling area |
| Grid interaction works | Cursor or target point aligns with the specified grid behavior |
| Footprint can be created | The required pointer sequence produces a valid closed shape |
| Dimensions and height can be adjusted | The values change within the specified constraints |
| A volume is generated | The resulting object is visible and geometrically consistent |
| Drawing can be cancelled | Right-click or the specified action exits without committing invalid work |
| Invalid input is handled | The user receives the specified feedback and project state remains valid |

Record the exact build, launch, and validation steps in `quickstart.md` or the project documentation so another reviewer can reproduce them.

The absent camera controls in the demonstration are not a failure if the active specification explicitly excludes them. Adding them during the same implementation would be scope creep. They should become a separate feature specification.

## Run `speckit-converge`

The current core workflow adds a post-implementation convergence step:

```text
/speckit-converge
```

or, depending on the integration:

```text
/speckit.converge
$speckit-converge
```

`converge` compares the codebase with `spec.md`, `plan.md`, and `tasks.md` after implementation. It has two outcomes:

- **Converged:** no gaps are found, and `tasks.md` remains unchanged.
- **Tasks appended:** missing work is added under a Convergence section in `tasks.md`.

If new tasks are appended, review them, run `implement` again for that work, validate the result, and repeat `converge` until it reports convergence.

Convergence is an additional automated check. It does not replace code review, product acceptance, security review, or CI.

## Hand Off to the Post-MVP Workflow

Once implementation and convergence are complete, the feature still needs deliberate source-control review, publication decisions, and product acceptance. A future behavior such as camera navigation should begin a new feature cycle rather than being added casually to the completed MVP.

The next lesson, [Adding a New Feature after the MVP](../11%20SpecKit%20-%20Post-MVP/11%20SpecKit%20-%20Post-MVP.md), covers the complete second iteration: specifying camera navigation against an existing codebase, clarifying its interaction model, repeating the planning and implementation stages, validating regressions, and delivering the change through a pull request.

## Common Mistakes

- Starting implementation before analyzing the artifacts
- Running the entire feature in one opaque session regardless of size
- Allowing an agent to install system tools without verifying source and scope
- Treating every task as suitable for a subagent
- Letting parallel agents edit the same files or working tree
- Assuming a particular model-routing strategy is part of Spec Kit
- Using a fixed token threshold as the only context-management policy
- Ignoring an agent that is waiting for approval or repeatedly failing
- Marking tasks `[X]` before their validation succeeds
- Trusting “all tests passed” without checking the commands and output
- Treating automated tests as complete UI acceptance
- Implementing camera control or another future feature outside the current spec
- Skipping `converge`, code review, or CI
- Initializing or publishing a repository without checking visibility and secrets
- Automatically merging generated code into the main branch

## Key Takeaway

`speckit-implement` executes the approved task graph, but reliable delivery depends on controlled scope and verifiable checkpoints. Preflight the environment, execute one phase or small task range at a time, delegate only genuinely independent work, and keep one orchestrator accountable for integration and validation.

An agent's completion report is the beginning of acceptance, not the end. Inspect the diff, rerun quality checks, exercise the actual user scenarios, run `speckit-converge`, and obtain the required human and CI review before committing, publishing, or merging. New behavior then starts a new specification cycle rather than being appended casually to the completed MVP.

## Further Reading

- [Spec Kit agentic SDD reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)
- [Current `implement` command template](https://github.com/github/spec-kit/blob/main/templates/commands/implement.md)
- [Handling complex features and long implementation runs](https://github.github.com/spec-kit/concepts/complex-features.html)
- [Spec-of-specs decomposition](https://github.github.com/spec-kit/concepts/spec-of-specs.html)
- [Spec Kit customization and extension hooks](https://github.github.com/spec-kit/guides/customization.html)
