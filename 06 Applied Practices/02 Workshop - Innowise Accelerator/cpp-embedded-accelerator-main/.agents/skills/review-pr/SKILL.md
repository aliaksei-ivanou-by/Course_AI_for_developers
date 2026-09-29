---
name: review-pr
description: "Review a C++/embedded pull request against requirements, PROJECT.md, correctness, compatibility, target constraints, and supplied verification evidence."
---

# Review Pull Request

1. Read the PR description, diff, related task/specs, PROJECT.md, and CI/evidence.
2. Identify behavior and contract changes before line-level review.
3. Apply the `code-reviewer` categories: correctness/lifetime, concurrency, embedded/portability, interfaces/compatibility, performance/security, tests/evidence.
4. Check that PR claims match evidence level and that target-dependent work is not marked complete from host-only checks.
5. Report findings by severity with file/line and failure scenario.
6. List missing tests, target evidence, documentation, migration, and rollback.

Do not approve based only on green CI when required target or compatibility evidence is absent. Return Context Summary and next actions, then STOP.
