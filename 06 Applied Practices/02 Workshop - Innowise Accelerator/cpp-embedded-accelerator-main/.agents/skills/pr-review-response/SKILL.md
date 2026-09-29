---
name: pr-review-response
description: "Process reviewer comments as evidence, not commands: classify each item, verify it against code/spec/context, fix accepted issues one at a time, re-run verification, and prepare concise reply drafts. Use when addressing PR/MR review feedback."
---

# PR Review Response

Reviewer comments are input to evaluate, not authority to execute blindly.

## 1. Gather and pin the round

Read the current diff, active task `STATE.md`, approved spec/diagnosis/plan, and the review comments. When code-host access is configured, fetch the real current review thread; otherwise work from the comments the developer supplied. Record the review round in the task workspace.

## 2. Classify every item

For each comment choose one:
- **accept** — technically correct and in scope;
- **push back** — evidence shows the requested change is wrong/risky/outside the contract;
- **clarify** — intent is ambiguous enough that changing code would be guesswork;
- **defer** — real issue, but outside this task's approved scope.

Support pushback with concrete `file:line`/symbol/contract evidence. Do not argue from preference.

## 3. Human gate for disputed items

Present pushback/clarify/defer items and the evidence before acting. Let the developer decide the position that will be sent externally. Accepted straightforward defects do not need a ceremony gate unless they materially change the approved task scope.

## 4. Implement accepted changes

Handle one item at a time. Use `testing` for behavior changes, then run the applicable focused checks. Do not let a review nit silently become a broad refactor.

After the round, run `self-review` when changes are substantial and `verify` before claiming the comments are addressed.

## 5. Draft replies

Write `<external_state_dir>/tasks/<slug>/pr-review-response.md` when a task workspace exists. Each reply should be short, factual and map to the actual change/evidence. Do not claim a test passed unless it was run. Avoid flattery padding and AI mentions.

Update `STATE.md` with what is resolved, disputed, waiting on the developer, and the next action. Publishing replies/commits/pushes remains a human action unless explicitly requested.
