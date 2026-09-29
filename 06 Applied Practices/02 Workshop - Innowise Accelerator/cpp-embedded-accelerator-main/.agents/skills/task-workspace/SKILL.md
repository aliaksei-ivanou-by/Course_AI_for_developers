---
name: task-workspace
description: "Give a real feature, bug, or review task a resumable external workspace with STATE.md, task artifacts, decisions, gates, and draft deliverables. Use for work that spans phases or sessions; skip it for trivial one-prompt changes."
---

# Task Workspace

Keep workflow state outside the customer repository while making long-running work resumable.

## Location

Resolve the project state directory with `embacc config .`, then use:

`<external_state_dir>/tasks/<slug>/`

Use the ticket key when one exists (`PROJ-123`); otherwise use a short stable slug (`fix-flash-timeout`). Never create `tasks/`, specs, plans, reflection files, or accelerator metadata inside the customer repository unless the developer explicitly asks for repository-local artifacts.

## STATE.md

Create `STATE.md` first and keep it concise. It is the source of truth after `/clear`, context compaction, agent switching, or a later session.

Keep these sections:
- **Goal** — observable outcome.
- **Phase / next action** — exactly where the flow is and what happens next.
- **Gates** — each human gate is `PENDING`, `APPROVED`, or `REJECTED`; for approval record a short quote of the developer's approving words.
- **Decisions** — stable `D-1`, `D-2`, ... entries with reason.
- **Evidence** — exact commands/checks and PASS/FAIL/NOT RUN.
- **Blockers / open questions**.
- **Links** — ticket, branch, MR/PR when known.

Update `STATE.md` at every phase boundary. On resume, read it before the ticket or chat history. A gate not recorded as `APPROVED` is unresolved.

## Standard artifacts

Create only artifacts the active flow needs:
- feature: `spec.md`, `plan.md`, `verification.md`;
- bug: `diagnosis.md`, `plan.md`, `verification.md`;
- review: `review.md` and optionally `verification.md`;
- common: `notes.md`, `commit-message.txt`, `mr.md`, `tracker-comment.md`.

Draft deliverables are for the developer to publish unless they explicitly ask the agent to perform the external action.

## Scope discipline

Put real but unrelated findings in `notes.md`; do not silently widen the active task. For a tiny change that fits in one prompt and touches at most two files, skip this workspace entirely unless the developer asks for tracked workflow state.

## Finish

Before deleting a completed task workspace, move genuinely durable knowledge into `PROJECT.md` or a hidden project skill via `stabilize`. One-off task history does not need to become permanent policy.
