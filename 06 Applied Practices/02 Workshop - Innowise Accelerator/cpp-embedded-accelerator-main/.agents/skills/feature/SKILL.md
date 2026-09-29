---
name: feature
description: "End-to-end feature workflow for outstaff development: task workspace, real ticket/context, spec, human spec gate, implementation plan, human plan gate, implementation, self-review, verification and handoff/draft deliverables. Use for non-trivial feature work or feature tickets."
---

# Feature

Use `task-workspace` for any feature that deserves multiple phases/sessions. Tiny one-prompt, <=2-file changes may skip the ceremony unless the developer asks for it.

## Resume rule

If a task directory already exists, read `STATE.md` first. Never infer a gate from old chat when `STATE.md` says `PENDING`.

## Flow

### 0. Pre-flight
- Resolve project context and target repo.
- Inspect `git status`; never clean/stash/discard user work automatically.
- If a ticket/key is supplied and the configured source of truth is reachable, fetch the real ticket.
- Create `<external_state_dir>/tasks/<slug>/STATE.md` via `task-workspace`.

### 1. Spec
Use `requirements-analyst` and `requirements-clarifier` as needed. Write `spec.md`. From this point the approved spec is the task source; do not repeatedly reinterpret the original chat/ticket.

### 2. HUMAN GATE — spec
Present the artifact path, scope, explicit non-scope, key decisions and acceptance criteria. Ask for approval and stop. No implementation plan or code before approval. Record the result in `STATE.md`.

### 3. Plan
Use `writing-plans`; write `plan.md` with exact files/commands/evidence.

### 4. HUMAN GATE — plan
Present the path, blast radius, important tradeoffs and verification plan. Ask for approval and stop. No implementation before approval. Record it.

### 5. Implement
Use `coder` and `testing` for changed behavior. If a materially new requirement or file area appears, reopen the relevant gate instead of scope-creeping.

### 6. Review and verify
Run `self-review`, fix accepted findings, then `verify`. Write `verification.md` and update `STATE.md`.

### 7. Handoff / drafts
Prepare `commit-message.txt`, `mr.md`, and `tracker-comment.md` when useful. The developer publishes them unless they explicitly request an external action.

### 8. Learn
If the task exposed a durable project gotcha or repeated workflow friction, use `stabilize`. Do not turn one-off noise into permanent policy.
