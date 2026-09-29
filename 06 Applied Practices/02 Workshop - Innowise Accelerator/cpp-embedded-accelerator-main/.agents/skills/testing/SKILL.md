---
name: testing
description: "Keep tests coupled to changed behavior, not implementation details. Use during feature/bug implementation, when choosing a test seam, or when deciding whether a behavior needs regression protection. Bug fixes prefer a failing reproduction before the fix when a practical seam exists."
---

# Testing

Tests ship with behavior changes in the same deliverable. Test through a stable public seam rather than private implementation details.

## Rules

- Read neighboring tests first and match the repository's real framework, naming, fixtures and test command.
- Prefer the narrowest seam that observes the contract: public API/method, protocol/parser boundary, message handler, data-access contract, CLI, or target interface.
- Do not mock internal collaborators merely because mocking is convenient; mock at external/expensive boundaries when necessary.
- A behavior-changing feature should normally have a credible regression signal. If no automated seam is practical, record why and use the best explicit verification method instead.
- For bug fixes, when practical, make the failure observable before the fix and prove the regression test would fail without the fix.
- Avoid watch-mode/interactive test runners in agent sessions; use a terminating command.
- Do not claim host tests prove hardware/target behavior.

Record exact commands and PASS/FAIL/NOT RUN in the active task `verification.md`/`STATE.md`.
