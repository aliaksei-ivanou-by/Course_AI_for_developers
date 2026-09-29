---
name: bug
description: "End-to-end bug-fix workflow for outstaff development: reproduce first, root-cause analysis, human diagnosis gate, minimal fix plan, human plan gate, regression protection, self-review and verification. Use for non-trivial broken behavior, incidents, regressions or bug tickets."
---

# Bug

Use `task-workspace` for a bug worth investigating across phases. An obvious tiny <=2-file correction may be handled directly unless the developer asks for the full flow.

## Iron law

Do not implement a fix before the failure is reproduced or the best available evidence is preserved and a root cause is understood. A plausible patch is not a diagnosis.

## Flow

### 0. Pre-flight
Resolve repo/context, inspect git state, fetch the real ticket when configured/reachable, and create `<external_state_dir>/tasks/<slug>/STATE.md`.

### 1. Reproduce
Prefer a deterministic failing regression test. If there is no practical test seam, record the exact logs/trace/core/manual reproduction and why a test is unavailable. Measure intermittency instead of guessing.

### 2. Diagnose
Use `systematic-debugger`; write `diagnosis.md` with symptom, reproduction, falsified hypotheses, root cause, why existing checks missed it, and required verification.

### 3. HUMAN GATE — diagnosis
Present the diagnosis artifact and evidence. Ask for approval and stop. No fix before approval. Record the result in `STATE.md`.

### 4. Fix plan
Use `writing-plans` for the minimal root-cause fix plus regression protection; write `plan.md`.

### 5. HUMAN GATE — fix plan
Present files/blast radius/regression test/evidence. Ask for approval and stop. Record it.

### 6. Implement
Use `coder` and `testing`. Fix the root cause, not only the symptom. Keep unrelated findings in `notes.md`.

### 7. Review and verify
Run `self-review`, then `verify`; write `verification.md` and update `STATE.md`.

### 8. Handoff / drafts
Prepare commit/MR/tracker drafts when useful; bug tracker text must include the root cause and verification. The developer publishes unless explicitly requested otherwise.

### 9. Learn
Use `stabilize` for a durable rule/workflow discovered from this incident.
