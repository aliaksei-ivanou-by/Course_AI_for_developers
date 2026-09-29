---
name: self-review
description: "Review the current C++/embedded change before completion on two independent axes: repository/engineering standards and task/spec intent, then triage verification gaps and scope creep. Use after implementation and before final verification or PR preparation."
---

# Self Review

Read the diff; do not substitute a green build for review. When a task workspace exists, write persistent findings to `<external_state_dir>/tasks/<slug>/self-review.md`; otherwise report them in chat.

## 0. Pin the Change

- Verify the actual base branch.
- Record merge-base/base revision, `git diff <base>...HEAD`, commit list, and working-tree changes.
- If the task started from an already-dirty tree, distinguish pre-existing changes from this task using `STATE.md` or recorded baseline evidence.

## 1. Axis A — Standards and Engineering Correctness

Review independently against:

- repository policy, compiler/linter/build settings, neighboring code conventions;
- C++ lifetime, UB, alignment, integer/range safety, exception/RTTI/allocation policy;
- handles/resources and partial-failure cleanup;
- concurrency, lock ordering, atomics, callbacks-after-destruction, task/ISR rules;
- portability, target assumptions, ABI/wire/persistence compatibility;
- performance/resource budgets and bounded work;
- security/safety boundaries and diagnostic leakage.

When independent read-only subagents are available, use one for this axis. Otherwise run it as a separate pass and record that independence was reduced.

## 2. Axis B — Requirements / Spec Intent

Review separately against task requirements, acceptance criteria, architecture/contracts, and approved plan:

- missing or partial requirements;
- behavior implemented incorrectly;
- behavior nobody requested;
- plan deviations not justified by new evidence;
- compatibility or target evidence that the task requires but the change does not provide.

When independent subagents are available, use a different read-only pass/subagent from Axis A.

## 3. Verification Gap

For every behavior introduced or changed ask:

> If this breaks tomorrow, which check fails?

A behavior with no credible test/static/target/measurement signal is a finding. Host-only evidence must not protect a target-only claim on paper.

## 4. Triage by Origin

| Label | Meaning | Action |
|---|---|---|
| `intent_gap` | task was misunderstood | repair understanding/spec before code |
| `bad_spec` | requirement/spec is wrong or contradictory | correct/clarify the spec; do not hide it in code |
| `patch` | real defect in the current change | fix now and re-check |
| `defer` | real issue outside approved scope | add to the task workspace `notes.md` |
| `reject` | false positive | record evidence for rejection |

Each finding includes severity, `file:line`/symbol, failure scenario, evidence, triage label, and concrete next action.

## 5. Exit

Re-review only the changed parts after patches. If repeated review uncovers the same architecture-level problem three times, stop and surface it rather than continuing an edit loop.

Return a compact summary and suggest `code-reviewer` or `verify` as appropriate, then STOP.
