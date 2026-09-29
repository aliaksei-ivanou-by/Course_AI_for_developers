---
name: systematic-debugger
description: "Diagnose C++/embedded build, runtime, concurrency, memory, timing, protocol, and target failures by reproducing and isolating root cause before changing code."
---

# Systematic Debugger

## Method

1. Record the exact symptom, expected behavior, environment, revision, build type, toolchain, target, and reproduction command/input.
2. Classify the evidence level: compile, link, host runtime, sanitizer, simulator, target, HIL, performance.
3. Preserve logs, symbols, core/minidump, trace, packet capture, register/error state, map file, or benchmark data as applicable.
4. Reproduce consistently. For a behavioral bug with a practical test seam, encode the reproduction as a failing regression test and observe it fail before the fix. If that is impossible, record exactly why and preserve the next-best reproduction evidence. If intermittent, measure frequency and control timing/load rather than guessing.
5. Narrow the failing boundary using the smallest discriminating experiment.
6. Form one falsifiable hypothesis at a time.
7. Change one variable, collect evidence, and update the hypothesis.
8. Identify root cause, trigger, affected scope, ruled-out alternatives, and why existing tests/diagnostics missed it. Separate root cause from symptom.
9. Record the diagnosis before proposing a fix. Add a regression test or durable diagnostic before/following the fix where feasible. After three failed fix hypotheses on the same cause, stop and reassess the model instead of trying a fourth patch.

## Common Evidence Paths

- compile/link: command lines, generated files, symbols, ABI/toolchain mismatch;
- memory/lifetime: ASan/UBSan/Valgrind/page heap/core dump;
- concurrency: TSan, lock/task traces, scheduler events, shutdown ordering;
- embedded: reset reason, fault registers, stack watermark, watchdog, JTAG trace, logic analyzer;
- protocol: raw bytes, framing/version/endian, partial I/O, retries;
- performance: release build, target utilization, flame graph/trace, percentile distribution.

## Rules

- Do not “fix” by adding sleeps, retries, larger buffers, disabled checks, or broad locks without proving causality.
- Do not confuse a changed symptom with a solved root cause.
- Do not run destructive target operations without explicit authorization and recovery.

If the request that invoked this skill only asked for diagnosis, return root cause or the narrowest remaining hypothesis, evidence, and recommended `coder` or focused verification action, then STOP — do not apply the fix unasked.

If the request already asked for a fix and verification (not diagnosis alone), a human already made the routing decision by asking for it in this turn: apply the narrowest fix implied by the confirmed root cause yourself, then verify it the same way the bug was reproduced. Do not stop at diagnosis and hand off a fix the user already asked you to make — an unimplemented "Next Steps: apply the fix" is not a completed task.
