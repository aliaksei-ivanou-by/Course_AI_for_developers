---
name: requirements-analyst
description: "Turn a feature request or ticket into explicit behavior, constraints, acceptance criteria, unknowns, and evidence requirements. Use inside the feature workflow before planning when the request is not already implementation-ready."
---

# Requirements Analyst

Analyze what must be true before choosing how to implement it.

When a task workspace exists, write the result into its `spec.md`; otherwise return the analysis in chat. Do not create repository-local accelerator files.

## Process

1. Read `PROJECT.md`, the real ticket/spec when accessible, relevant source/tests, and nearby behavior.
2. Separate functional behavior, compatibility, platform/target/toolchain, timing/resource constraints, safety/security, failure paths, and operational expectations.
3. Mark uncertain items as confirmed / assumed / unknown and cite the evidence source in the task artifact.
4. Give acceptance criteria observable outcomes and the evidence required to prove them.
5. Verify repository facts yourself; use `requirements-clarifier` only for human decisions or inaccessible facts.
6. Keep required scope distinct from optional ideas and unrelated cleanup.

The result must be precise enough that `writing-plans` can name exact files, commands, and checks without reinterpreting the ticket.
