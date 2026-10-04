# Phase 3 Clarifications

Status: Accepted by the human reviewer
Specification: [03-spec.md](03-spec.md) · Codebase map: [02-codebase-map.md](02-codebase-map.md)

Each entry records a question that would otherwise change public behaviour, the options considered, the decision, and who made it. "Reviewer" means the human reviewer chose among presented options; "Agent" means the decision follows from the assignment, the contract, or existing Catch2 behaviour; the reviewer accepted all agent decisions together with this document. Every decision is reflected in the specification at the listed IDs.

Baseline facts marked "probed" were checked by building the unmodified `v3.16.0` amalgamated sources with a small test file in the agent's scratch workspace; no file in `workspace/Catch2` was touched.

## Summary

| ID | Topic | Decision | By | Spec |
| --- | --- | --- | --- | --- |
| C1 | Attempt events when `N ≥ 1` | Emitted for every attempt, including a pass on attempt 1; never emitted when `N = 0` | Agent | E-2, §5.2, CO-1 |
| C2 | Part numbers across attempts | Continue increasing within the logical test case | Reviewer | E-5 |
| C3 | Random seed per attempt | Reseed at the start of every attempt | Reviewer | S-4, CO-7 |
| C4 | Captured output in the final event | All attempts, in order; each attempt-end carries its own output | Reviewer | E-4, E-6 |
| C5 | Special tags, skip, and flaky | Use Catch2's attempt outcome; flaky only when the final outcome is passed | Agent | R-3, R-8, §1 |
| C6 | Final totals and abort budget | Final attempt only; superseded attempts excluded from totals and abort budget | Agent | T-2, E-8, AB-2 |
| C7 | Machine-readable reporter scope | XML and JSON structural; all built-in reporters report the final status correctly | Reviewer | §5.2 |
| C8 | Reporters that emit failures as they happen | Superseded failures stay visible but never count as failures in the machine-readable result | Agent | §5.2 |
| C9 | Fixture lifecycle | Persistent fixture created and destroyed per attempt | Agent | S-7 |
| C10 | Fatal error during an attempt | Not retried; attempt end emitted best effort before Catch2's fatal notifications | Agent | R-6, E-7 |
| C11 | Unexpected `[!shouldfail]` pass totals | Preserve Catch2's existing run-total/session-total difference | Agent | T-5 |
| C12 | Value syntax, range, repetition | Same unsigned syntax as `--shard-count`; `0`–`4294967295`; repeating is an error | Agent | CLI-3, CLI-4 |
| C13 | Numbering and `M` | One-based `k`; `M = N + 1` held in a 64-bit unsigned value | Agent | CLI-8, E-3 |
| C14 | Abort precedence | Threshold reached during an attempt ends retrying for that test and the run; an unexpected `[!shouldfail]` pass does not reach it | Agent | AB-1, AB-3 |
| C15 | Threads started by a test | Guarantees apply once the test body has returned; threads left running are test-owned state | Agent | S-9 |

## Decisions

### C1. Attempt events when `N ≥ 1`

- Question: should attempt notifications appear when no retry happens?
- Options: (a) only around retried test cases; (b) around every attempt whenever `N ≥ 1`; (c) always, even with `N = 0`.
- Decision: (b). Option (c) breaks the zero-retry compatibility requirement (A, Reporter Contract: "With retries disabled, reporters observe the same event sequence"). Option (a) would require knowing before attempt 1 whether a retry will happen, which is impossible, or emitting an end without a start. With (b), a reporter sees one consistent shape for every test case in a run with retries enabled.
- Consequence: with `N ≥ 1`, XML and JSON contain attempt information for every test case even if nothing is retried (§5.2). Console and other reporters print nothing extra unless a retry happens.

### C2. Part numbers across attempts (reviewer)

- Options: (a) continue increasing across attempts; (b) restart at 0 for each attempt.
- Decision: (a). The documented meaning of a partial event is one entry into the test case (`docs/reporter-events.md`, `testCasePartial` events), and Catch2 numbers those entries from 0 within a test case (M §2.2). Listeners that check this sequence, such as Catch2's own `ValidatingTestListener` (M §9), keep working. Attempt membership is visible from the attempt notifications that enclose the partial events.

### C3. Random seed per attempt (reviewer)

- Options: (a) reseed at the start of every attempt; (b) seed once per logical test case.
- Decision: (a). Every attempt sees the same random values as attempt 1, which matches "every retry must behave like a new Catch2 execution of that test case" (A, Fresh State) and keeps fixed-seed runs reproducible. A retry therefore re-checks the same inputs that failed rather than passing on different data.

### C4. Captured output (reviewer)

- Options: (a) `testCaseEnded` carries the output of all attempts, in order; (b) final attempt only.
- Decision: (a). Earlier diagnostics "must not silently disappear after a later pass" (A, Reporter Contract), including in reporters that ignore attempt notifications. With `N = 0` there is one attempt, so the data is identical to Catch2 today. Each attempt-end notification carries only that attempt's output, and each partial event keeps its own output as today.

### C5. Special tags, skip, and the flaky flag

- The retry decision uses Catch2's existing attempt outcome (M §5: assertion counting, `Totals::delta`, and the unexpected-pass adjustment). Probed baseline: `[!mayfail]` failing exits 0; `[!shouldfail]` failing exits 0; `[!shouldfail]` passing exits 42 (test failure); a run where every test is skipped exits 4.
- Decisions:
  - `[!mayfail]` or `[!shouldfail]` with failures is an accepted failure: no retry.
  - An unexpected pass under `[!shouldfail]` is failed: retried while budget remains. If a later attempt then fails as expected, the final outcome is accepted failure.
  - An attempt with failed assertions and a later `SKIP` is failed, because Catch2 ranks failure above skip.
  - A test whose superseded attempt failed and whose final attempt skipped is skipped, not flaky.
  - Flaky means the final outcome is passed and at least one attempt was superseded. A final accepted failure or skip after a superseded attempt is not flaky; the attempt notifications still show the retry.

### C6. Final totals and abort budget

- Question: which assertions count, and what about running totals already sent to reporters?
- Decision: test-case, run, and session totals and the exit status use the final attempt only (A, Statistics: "Final assertion totals contain the assertions from the final attempt only"). Failed assertions of superseded attempts do not count toward `--abortx` (A, Interaction). Superseded results are delivered to reporters as they happen and stay available through the attempt-end result (A forbids "discarding failed-attempt diagnostics").
- Running totals inside individual assertion events are cumulative progress values at that moment and may include assertions of an attempt that is later superseded; reporters must take results from the attempt-end and test-case-end notifications. Among built-in reporters, only the console reporter reads that value, and only to check whether it is non-zero (M §5).

### C7. Machine-readable reporter scope (reviewer)

- Options: (a) XML and JSON represent attempts structurally, and every built-in reporter reports the final status correctly; (b) JSON only structurally, with SonarQube, TeamCity, and TAP showing a flaky pass as failed as a documented limitation.
- Decision: (a). The XML `xml-format-version` and JSON `version` stay unchanged (agent decision): the additions are additive and appear only with `N ≥ 1`, so existing consumers of zero-retry output see no change. The assignment requires "correct final test-case status" from "JSON, XML, JUnit, and other affected machine-readable reporters" (A, Reporter Contract); (b) would leave that unmet for three reporters.

### C8. Reporters that emit failures as they happen

- Facts (M §8.2): TeamCity emits `testFailed` at a failing assertion; TAP emits a `not ok` test point per assertion; JUnit and SonarQube derive failures from a section tree that merges repeated entries; console and compact print failures inline.
- Decision: superseded failures must remain visible in every reporter but must not make a machine-readable consumer treat a flaky pass as failed (§5.2): non-failing messages in TeamCity, diagnostic lines in TAP, non-counting entries in JUnit and SonarQube. Human-readable reporters (console, compact) print them inline and mark the attempt. The exact output format of each reporter is a Phase 4 design decision and is fixed by approval or parser-based tests in Phase 6.

### C9. Fixture lifecycle

- Fact (M §4): a persistent fixture is created once per logical test case and shared by its partial runs; per-run fixtures are created for every partial run.
- Decision: a persistent fixture is created before and destroyed after each attempt, so each attempt gets a fresh fixture with balanced construction and destruction (A, Fresh State: "fixture-based test cases receive a fresh fixture for every attempt"). Per-run fixtures are unchanged.

### C10. Fatal error during an attempt

- Fact (M §13 Q7): on a fatal signal or structured exception, Catch2 reports the error, ends the test case and the run itself, and the process terminates.
- Decision: not retryable (A, Retry Decision). To keep start/end events balanced, the current attempt is ended before Catch2's existing fatal-path test-case end, as a best effort with the same reliability as the existing fatal reporting.

### C11. Unexpected `[!shouldfail]` pass totals

- Probed baseline: for a `[!shouldfail]` test that passes, XML run totals show 1 successful assertion and 0 failed assertions, while the test case counts as failed and the exit code is 42. The extra failed assertion exists only in the session's totals (M §5).
- Decision: preserve this behaviour unchanged for final attempts. A superseded unexpected pass contributes nothing to any totals.

### C12. Value syntax, range, and repetition

- Probed baseline for `--shard-count`, which uses Catch2's unsigned parser: accepts `+2`, `007`, ` 2`, `2 `, `4294967295`; rejects `abc`, `1.5`, `1e3`, `0x10`, `4294967296` ("Could not parse ..."); `-1` is read by the parser as an option, so it gives "Expected argument following ...", the same message as a missing value; giving the option twice gives "Unrecognised token: ...". All errors print `Error(s) in input:` and exit with code 1 before any test runs.
- Decision: `--retry-failed` follows the same rules, so users get one consistent number syntax. The assignment's rejected inputs (missing, `-1`, `abc`, `1.5`, too large) are all rejected under these rules.

### C13. Numbering and maximum attempts

- Decision: attempt numbers shown to users and reporters are one-based. `M = N + 1` is carried in a 64-bit unsigned value, so the largest accepted `N` (`4294967295`) gives `M = 4294967296` without overflow. Internally, the retry check compares retries used with `N` and never computes `N + 1` in the 32-bit type (A, CLI).

### C14. Abort precedence

- Fact (M §6): the abort check uses the run-wide count of failed assertions; once reached, failing assertions stop the current partial run, no further partial run starts, and the remaining test cases are reported as skipped.
- Probed baseline: with `--abort`, a `[!shouldfail]` test that passes is counted as a failed test case, but the run does not abort and the next test runs. The extra failed assertion of an unexpected pass is not part of the count the abort check uses (M §5, §6).
- Decision: if the threshold is reached during an attempt, no retry starts (A, Interaction). Consequences: with `--abort`, an attempt with any counted failed assertion is not retried; an unexpected `[!shouldfail]` pass does not reach the threshold, so it is retried while budget remains and the run continues, as Catch2 today; with `--abortx X`, an attempt is retried only if the run-wide count of counted failures, including the attempt's own, stayed below `X`.

### C15. Threads started by a test

- Fact (M §13 Q8): with thread-safe assertions enabled, assertions from other threads update shared counters.
- Decision: the per-attempt guarantees (fresh state, totals restored for superseded attempts) hold for assertions made before the test body returns. A thread that outlives its attempt is state owned by the test (S-9) and is not covered.

## Open Questions from the Codebase Map

| Map §13 | Resolution |
| --- | --- |
| Q1 Part numbers | C2 |
| Q2 RNG reseeding | C3 |
| Q3 Shape of attempt data for reporters | Data content fixed by E-3, E-4, E-6, and CO-3; the concrete types and callback names are a Phase 4 design decision |
| Q4 Output in the final event | C4 |
| Q5 Inline-failure reporters | C7, C8 |
| Q6 Run totals versus session totals | C6, C11 |
| Q7 Fatal-error path | C10 |
| Q8 Thread-safe assertions | C15 |
| Q9 Where retry tests live | Phase 4/5 decision, constrained by CO-1: baselines change only for intentionally added tests |

## Gate Status

| Gate | Status |
| --- | --- |
| Final assertion-total policy | ✅ C6 |
| Special-tag outcomes | ✅ C5, C11 |
| Abort precedence and budget accounting | ✅ C6, C14 |
| Outer test-case versus attempt event lifecycle | ✅ C1, C2, C4 |
| Machine-readable reporter expectations | ✅ C7, C8 |
| Fixture lifecycle | ✅ C9 |
| Largest accepted retry value and overflow safety | ✅ C12, C13 |
| Every answer recorded in the specification | ✅ Spec column of the summary table |
