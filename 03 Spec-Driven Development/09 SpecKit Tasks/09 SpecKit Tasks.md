# Generating an Implementation Task List with Spec Kit

The `tasks` stage converts an approved technical plan into an ordered, executable work breakdown. Its main output is `tasks.md`: a checklist organized by setup work, shared prerequisites, user stories, and final cross-cutting work.

This stage does not implement the feature. It defines what must be implemented, in what order, and which items may safely run in parallel.

This lesson continues the desktop 3D-space modeling MVP after its feature specification has been clarified and its implementation plan has been created.

> **Version note:** Current Spec Kit task generation requires `spec.md` and `plan.md`. It can also use `data-model.md`, `contracts/`, `research.md`, `quickstart.md`, and the project constitution when they exist.

## Position in the Workflow

The task list sits between technical design and implementation:

```text
constitution   project-wide rules
spec.md        user needs and acceptance scenarios
plan.md        technical approach and project structure
design files   models, contracts, research, quickstart
      ↓
tasks          dependency-ordered implementation checklist
      ↓
analyze        consistency check before coding
      ↓
implement      execute and verify the tasks
```

The transcript demonstrates the shorter path from `tasks` directly to `implement`. The current complete workflow should normally run the read-only `analyze` check first, especially for substantial features.

## Resetting Context Before Task Generation

The video starts a fresh agent session before invoking `tasks`. This is reasonable after the specification and plan have been reviewed because accepted decisions are stored in Markdown files rather than only in the conversation.

Before resetting, verify that:

- `spec.md` contains all accepted clarifications.
- `plan.md` reflects the approved architecture and source structure.
- Supporting design artifacts are complete and consistent.
- The intended feature is still active.
- Important decisions do not exist only in chat history.
- The working tree is saved or committed according to the team's recovery policy.

A new session still needs to read the project files. Resetting reduces irrelevant conversational context; it does not eliminate repository discovery or guarantee lower total cost.

## Invoke the Tasks Skill

Command syntax depends on the coding-agent integration:

| Integration or reference style | Example |
| --- | --- |
| Claude Code or another hyphenated skills layout | `/speckit-tasks` |
| Canonical dotted notation in Spec Kit references | `/speckit.tasks` |
| Codex skills integration | `$speckit-tasks` |

The basic invocation is sufficient when the upstream artifacts are complete:

```text
/speckit-tasks
```

Additional guidance can make the expected quality explicit without redesigning the feature:

```text
/speckit-tasks

Ensure that every constitution-mandated test and every quickstart scenario maps
to an implementation or validation task. Mark a task [P] only when it changes
different files and has no dependency on an unfinished task. Include exact file
paths and keep each user story independently testable.
```

Do not use this prompt to introduce new requirements or silently change technical decisions. Correct the owning specification or plan first and then regenerate the affected tasks.

## Inputs and Output

The generator uses the active feature directory and reads the available planning documents.

### Required Inputs

- `spec.md` supplies user stories, priorities, functional requirements, and acceptance scenarios.
- `plan.md` supplies the selected stack, architecture, and source-code layout.

### Optional Inputs

- `data-model.md` supplies entities, relationships, and validation rules.
- `contracts/` supplies interfaces and boundary definitions.
- `research.md` supplies selected approaches and technical rationale.
- `quickstart.md` supplies end-to-end validation scenarios.
- The constitution supplies project-wide quality and governance obligations.

The output is normally:

```text
specs/<active-feature>/tasks.md
```

Generation can take time because the agent must reconcile several artifacts, map requirements to work, determine dependencies, and identify real parallel opportunities. Duration alone is not evidence that the result is complete.

## The Strict Task Format

Each task in the current core template must follow this checklist form:

```text
- [ ] T001 [P?] [US?] Description with an exact file path
```

Each element has a specific meaning:

| Element | Meaning |
| --- | --- |
| `- [ ]` | Required Markdown checkbox for an incomplete task |
| `T001` | Sequential task identifier in execution order |
| `[P]` | Optional marker: safe to run in parallel under stated conditions |
| `[US1]` | User-story label; required inside user-story phases |
| Description | Concrete action including the affected file path |

Examples:

```text
- [ ] T001 Create the Rust application skeleton in Cargo.toml and src/main.rs
- [ ] T005 [P] [US1] Add immutable grid-coordinate types in src/model/grid.rs
- [ ] T006 [P] [US1] Add footprint validation tests in tests/footprint_validation.rs
- [ ] T007 [US1] Implement footprint validation in src/model/footprint.rs
```

`[P]` does not mean “prefer parallel execution.” It means the task has no dependency on incomplete work and changes files that another simultaneous task does not change. The implementer still needs to consider shared interfaces, generated files, build configuration, and other semantic conflicts.

Tasks outside user-story phases, such as Setup and Foundational work, do not receive a `[US#]` label. Task IDs express ordering, not priority; story priority comes from the specification.

## How `tasks.md` Is Organized

The current template uses dependency-aware phases.

### Phase 1: Setup

Setup creates the initial repository structure and common tooling. Examples include creating directories, initializing project configuration, or configuring formatting and linting.

Setup has no feature-phase dependency, although its own tasks may still have an internal order.

### Phase 2: Foundational

Foundational tasks provide shared prerequisites required by all or most user stories. Examples include core types, application bootstrapping, persistence foundations, or common error handling.

This phase depends on Setup and blocks user-story implementation. Calling a foundational task `[P]` only permits parallelism with other compatible tasks inside that ready phase; it does not permit starting dependent stories early.

### Phase 3 and Later: User Stories

Each user story receives its own phase, normally in priority order: P1, P2, P3, and so on. A good story phase contains everything needed to produce an independently testable increment.

Within a story, a typical order is:

```text
tests, when required → models → services → interfaces → integration → validation
```

Tests are not added automatically by the core template unless the specification requests them, the user asks for test-driven development, or the constitution requires them. When tests are required, they should be written before the implementation they verify and initially fail for the expected reason.

### Final Phase: Polish and Cross-Cutting Concerns

The final phase contains work that spans multiple stories, such as documentation, performance verification, security hardening, cleanup, or full quickstart validation. It depends on all stories included in the intended release scope.

## Example for the 3D-Space MVP

A simplified task structure could look like this:

```text
Phase 1 — Setup
- [ ] T001 Initialize the native desktop project in Cargo.toml and src/main.rs
- [ ] T002 [P] Configure formatting rules in rustfmt.toml
- [ ] T003 [P] Configure test support in Cargo.toml

Phase 2 — Foundational
- [ ] T004 Create project and workspace state in src/model/project.rs
- [ ] T005 [P] Add grid-coordinate conversion in src/model/grid.rs
- [ ] T006 Add shared drawing state in src/interaction/drawing_state.rs

Phase 3 — User Story 1: Draw a valid closed footprint
- [ ] T007 [P] [US1] Add footprint validation cases in tests/footprint_validation.rs
- [ ] T008 [US1] Implement footprint geometry in src/model/footprint.rs
- [ ] T009 [US1] Connect pointer input to drawing state in src/interaction/drawing.rs
- [ ] T010 [US1] Validate the story against its acceptance scenarios in specs/001-grid-space-mvp/quickstart.md
```

These paths are illustrative. Generated tasks must use the actual structure approved in this project's `plan.md`.

Notice that T007 and T008 should not automatically run in parallel if test-first development is required: the test must be written and observed failing before implementation begins. A mechanically applied `[P]` marker can therefore violate the intended workflow even when the files differ.

## Review `tasks.md` Before Implementation

Open the generated file and inspect more than the number of tasks. Confirm that:

1. Every required user story has its own phase.
2. Every functional requirement maps to one or more tasks.
3. Each story ends in independently verifiable behavior.
4. Setup and Foundational work are separated correctly.
5. Task descriptions contain exact repository paths.
6. Task IDs are sequential and labels use the required format.
7. Dependencies and execution order are feasible.
8. `[P]` appears only on genuinely independent work.
9. Required tests, security checks, and constitution gates are represented.
10. Contracts, data-model rules, and quickstart scenarios are covered.
11. No task adds scope that was never approved.
12. Tasks are small enough to complete and verify individually.

For traceability, reviewers should be able to move in both directions:

```text
requirement → story → design decision → task → verification
task → design decision → requirement or project obligation
```

A task with no upstream reason may be scope creep. A requirement with no downstream task is an implementation gap.

## Sequential and Parallel Execution

The generated task list should document phase dependencies and parallel examples. Choose the execution style from the actual dependency graph, not from a blanket preference.

| Strategy | Appropriate when | Main caution |
| --- | --- | --- |
| Sequential | Small feature, one developer, shared files, uncertain interfaces | Slower but easiest to coordinate |
| Parallel tasks | `[P]` tasks have disjoint files and settled interfaces | Integration and semantic conflicts can still occur |
| Parallel stories | Foundational phase is complete and stories are independent | Shared models or contracts may couple the stories |
| Scoped batches | The full list is large or risky | Stop and validate at phase boundaries |

For most features, the simplest safe approach is incremental delivery:

1. Complete Setup.
2. Complete and validate Foundational work.
3. Implement the highest-priority story.
4. Verify that story independently as the MVP.
5. Continue with later stories only after the increment is stable.

## Subagents and an Orchestrator

The transcript suggests using several subagents under one orchestrator. This can improve throughput, but it is an optional execution technique rather than a universal Spec Kit requirement.

A useful orchestrator should:

- Select only currently unblocked tasks.
- Give each subagent a precise task, allowed files, inputs, and validation command.
- Prevent simultaneous edits to the same files or generated state.
- Track task dependencies and completion evidence.
- Review and integrate every result.
- Run repository-level checks after parallel work is combined.
- Keep `tasks.md` completion markers accurate.

Use subagents when tasks are genuinely independent and coordination overhead is lower than the time saved. Prefer sequential execution when the work is small, the design is still moving, tasks touch common files, or failures are hard to isolate.

For example, a supported agent can receive guidance such as:

```text
/speckit-implement

Execute only the currently unblocked [P] tasks from the active phase. Delegate
each task to a separate subagent only when its files are disjoint. Keep one
orchestrator responsible for dependency checks, review, integration, and the
final test run. Stop after this phase and report evidence for every completed task.
```

For a very large feature with parallel story teams, isolated Git worktrees may be needed. This avoids multiple agents overwriting the active-feature state or changing the same checkout concurrently. Merge order and validation still need explicit ownership.

## Does Subagent Use Belong in the Constitution?

The video discovers that the constitution does not mention subagents. That is not necessarily an omission.

The constitution should contain durable, project-wide engineering principles: required quality gates, compatibility rules, testing obligations, dependency policy, security constraints, and governance. Tool-specific orchestration usually belongs in agent instructions, a team runbook, or the invocation used for the current implementation.

Add a constitution principle only when the team has deliberately decided that it is binding across features and tools. Even then, define the outcome rather than a fragile product-specific mechanism. For example:

```text
Independent work may be delegated only after dependencies and file ownership are
explicit. A designated integrator remains accountable for review, integration,
and repository-level verification.
```

Do not amend the constitution merely because one task list offers parallel work. Also do not edit it while task generation is running: finish or stop the current operation, amend and ratify the constitution explicitly, then regenerate downstream artifacts whose assumptions changed.

## Run the Consistency Check

After reviewing `tasks.md`, run the current read-only analysis command before implementation:

```text
/speckit-analyze
```

or, depending on the integration:

```text
/speckit.analyze
$speckit-analyze
```

The analysis checks for inconsistencies, duplication, ambiguity, missing coverage, and constitution conflicts across `spec.md`, `plan.md`, and `tasks.md`. It should not modify those artifacts.

Resolve findings in the file that owns the decision:

| Finding | Corrective action |
| --- | --- |
| Missing or ambiguous behavior | Revise or clarify `spec.md` |
| Incorrect technical approach | Revise `plan.md` or its design artifacts |
| Missing, oversized, or misordered work | Revise or regenerate `tasks.md` |
| Genuine project-rule mismatch | Review the design or explicitly amend the constitution |

Regenerate downstream artifacts as needed and repeat analysis until critical findings are resolved.

## Prepare for Implementation

Once the task list is reviewed and the consistency check passes, saving the artifact allows another clean context reset. The next session can reconstruct its work from the active feature and `tasks.md`.

Instead of executing the entire list in one unattended run, the implement command can be scoped:

```text
/speckit-implement Execute Setup and Foundational only, validate them, and stop.
```

or:

```text
/speckit-implement Execute User Story 1 only and stop after its independent validation passes.
```

During implementation, the agent should respect the documented order, run compatible `[P]` tasks together only when safe, stop on a failed blocking task, and change completed checkboxes from `[ ]` to `[X]` only after the corresponding work has been verified.

## Inspect the Generated Changes

Review the active feature directory before moving forward:

```bash
git status --short
git diff -- specs/
```

Because untracked files do not appear in ordinary `git diff`, open a newly generated `tasks.md` directly or stage it only when it is ready for review.

Useful questions include:

- Does the list target the intended active feature?
- Did generation change any upstream artifact unexpectedly?
- Are all file paths valid for the planned repository structure?
- Are task and story dependencies documented clearly?
- Can the first story produce a meaningful, independently testable MVP?

## Common Mistakes

- Running `tasks` before the specification and plan are approved
- Assuming a long generated checklist must be complete
- Writing vague tasks without exact file paths
- Organizing tasks only by technical layer instead of by user story
- Treating `[P]` as an instruction to parallelize everything
- Starting story work before Foundational tasks are complete
- Letting parallel agents edit the same files or checkout state
- Marking tasks complete before tests and validation pass
- Adding tests inconsistently with the specification or constitution
- Putting transient, tool-specific agent behavior into the constitution
- Treating an orchestrator as a substitute for review and integration
- Skipping `analyze` before implementation
- Resetting context while decisions still exist only in the conversation
- Running the entire implementation in one batch when phased validation is safer

## Key Takeaway

The `tasks` stage turns a reviewed feature design into a traceable and dependency-aware implementation checklist. A useful `tasks.md` is organized around independently testable user stories, identifies blocking foundations, uses exact file paths, and marks parallel work conservatively.

Subagents can accelerate independent tasks, while one orchestrator coordinates dependencies and integration. They are not mandatory, and their use usually belongs in execution guidance rather than the project constitution. Review the task list, run the consistency analysis, and then implement in small validated phases.

## Further Reading

- [Spec Kit agentic SDD reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)
- [Current `tasks` command template](https://github.com/github/spec-kit/blob/main/templates/commands/tasks.md)
- [Current task-list template](https://github.com/github/spec-kit/blob/main/templates/tasks-template.md)
- [Current `implement` command template](https://github.com/github/spec-kit/blob/main/templates/commands/implement.md)
- [Spec Kit guidance for complex features and parallel execution](https://github.github.com/spec-kit/concepts/complex-features.html)
- [Spec-of-specs and isolated parallel work](https://github.github.com/spec-kit/concepts/spec-of-specs.html)
