---
name: writing-plans
description: "Produce an implementation plan grounded in the actual repository: exact files/symbols, steps, compatibility constraints, tests, target evidence and rollback. Use after an approved feature spec or bug diagnosis and before implementation."
---

# Writing Plans

When a task workspace exists, write `plan.md` beside `STATE.md`; otherwise return the plan in chat.

Before planning, read `PROJECT.md`, the approved task artifact (`spec.md` or `diagnosis.md`), source/build/tests/CI, current git state, and 1-3 close repository analogues.

Each plan item should state:
- purpose and affected requirement/root cause;
- exact files and symbols;
- implementation change;
- ownership/threading/ABI/wire/persistence/target implications when relevant;
- exact focused and broader verification commands discovered from this repository;
- expected evidence and any target/HIL/manual step;
- blast radius and rollback/migration note where relevant.

Do not use pseudo-paths when real paths are available. If implementation would exceed the approved scope, the plan must say so before code is changed.
