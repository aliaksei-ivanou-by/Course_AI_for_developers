---
name: verify
description: "Run the applicable C++/embedded Definition of Done tier and produce a PASS/FAIL/NOT RUN readiness report before completion, PR, merge, or release."
---

# Verify

When a task workspace exists, write the report to `<external_state_dir>/tasks/<slug>/verification.md`; otherwise report it in chat.

## Process

1. Read the project context already provided (`PROJECT.md`'s "Verification matrix" section), task requirements/spec or diagnosis, CI, repository commands, and any active STATE.md.
2. Select Tier 0, 1, 2, or 3 and explain why.
3. Discover commands from repository docs/CI/presets/build files; do not default blindly to CMake.
4. Construct a requirement/acceptance-criterion list from the approved task artifact and plan.
5. Run each applicable check.
6. Record:
   - exact command;
   - host/target/toolchain/build type;
   - PASS, FAIL, or NOT RUN;
   - evidence and relevant output;
   - impact of missing evidence.
7. Build a requirement-to-evidence matrix: each required ID/criterion maps to implementation evidence, executed verification evidence, status, and gap.
8. Verify claims about API/ABI/wire/persistence, hardware, and performance against actual evidence.
9. Summarize blockers, unrequested/scope concerns carried from self-review/convergence, and remaining risk.

## Result Rules

- Any required FAIL means overall FAIL.
- Any required target/resource/security/safety check that is NOT RUN prevents a fully complete Tier 2/3 result.
- Missing tooling is NOT RUN, not PASS.
- A clean build does not substitute for tests.
- Host tests do not substitute for required target/HIL evidence.

## Report Format

```markdown
## Verification Report

**Tier:** 2 — Target/System
**Revision:** ...
**Host:** ...
**Target:** ...

| Check | Command/Method | Status | Evidence / Risk |
|---|---|---|---|

### Requirement Evidence

| Requirement / criterion | Implementation evidence | Verification evidence | Status / gap |
|---|---|---|---|

**Overall:** PASS | FAIL | CONDITIONAL
**Blocking issues:** ...
**Unverified paths:** ...
```

If PASS, update task `STATE.md` as ready for handoff/delivery; if FAIL, route to the narrowest relevant skill. Then STOP.
