# Phase 7 Fresh-Context Review

Date: 2026-10-04

Resolution date: 2026-10-05

Second review date: 2026-10-05

Reviewed Catch2 revision: `9037e6faa6638b160d2f24e240f6b671d979c99d`

Resolved Catch2 revision: `b19a1b75c19b6f85d438e0653855a20f6d5ef95d`

Baseline: `v3.16.0` (`fd79eadb5bc1760e7cbae12fd45b0d0040d1bb73`)

## Gate Status

**Not passed after the second review.** The original H-1 and M-1 findings remain resolved, but the broader outcome matrix exposed one new high-severity and two new medium-severity defects. One low-severity documentation/evidence inconsistency is also open. No Catch2 production or test file was changed during the second review.

## Findings

### H-1 — Exhausted unexpected `[!shouldfail]` passes are reported as successful by four machine-readable reporters

**Severity:** High

**Status:** Resolved

The reviewed specification says that an unexpected pass under `[!shouldfail]` is a failed attempt and remains failed when its retry budget is exhausted (`03-spec.md:51`). It also requires every built-in reporter to report the final status correctly (`04-clarifications.md:72-73`), with final outcome deciding JUnit/SonarQube failure and an exhausted test being failed in TeamCity (`03-spec.md:116-119`).

The runner computes the semantic adjustment only after all assertion and section events have already been delivered: `src/catch2/internal/catch_run_context.cpp:508-513` turns the completed attempt from passed into failed, then sends the correct `TestCaseAttemptStats` and `TestCaseStats` at lines 398-406 and 419-428. The affected reporters nevertheless derive their output from the earlier assertion stream or section tree:

- JUnit writes failure elements from the final section tree (`src/catch2/reporters/catch_reporter_junit.cpp:258-359`) and does not use `TestCaseStats::totals.testCases` to synthesize a semantic final failure.
- SonarQube likewise writes only assertion failures from the final section tree (`src/catch2/reporters/catch_reporter_sonarqube.cpp:145-181`).
- TeamCity buffers assertion-derived service messages and replays them for the final attempt (`src/catch2/reporters/catch_reporter_teamcity.cpp:60-136`, `154-171`).
- TAP buffers assertion results and prints the final attempt's assertions as test points (`src/catch2/reporters/catch_reporter_tap.cpp:230-287`).

The final assertion in this scenario is `CHECK(true)`, so none of those reporters receives a failed assertion even though the authoritative attempt and test-case totals say the logical result is failed.

**Reproduction against the final T13/T14 binary:**

```text
RetryFailed.exe "[.retry-shouldfail-pass]" --retry-failed 2 \
  --reporter <JUnit|SonarQube|TeamCity|TAP> --colour-mode none
```

Every invocation exited with Catch2's test-failure code `42`, after three attempts. The emitted results contradicted that outcome:

| Reporter | Observed final report |
| --- | --- |
| JUnit | `<testsuite errors="0" failures="0" ...>` and no `<failure>` or `<error>` in the test case |
| SonarQube | a `<testCase>` with no `<failure>` or `<error>` |
| TeamCity | `testStarted`, `testStdOut`, and `testFinished`, but no `testFailed` |
| TAP | final `ok 1 - true` and plan `1..1` |

Controls from the same executable reported the semantic failure correctly: XML wrote `OverallResult success="false"`, JSON wrote one failed test case in run totals and failed per-attempt totals, and Automake wrote `:test-result: FAIL`.

**Impact:** CI consumers of these four reporters can accept a failed run or display a failed test as passed, despite the non-zero process exit. This directly violates the reporter contract and the special-tag decision table.

**Required resolution:** make these reporters use authoritative attempt/test-case outcome data when the semantic result differs from the assertion stream. Add parser/consumer-oriented tests for an exhausted unexpected `[!shouldfail]` pass to JUnit, SonarQube, TeamCity, and TAP. Preserve the current zero-retry output compatibility requirement.

**Resolution:** JUnit and SonarQube now synthesize a final failure when the authoritative retry-enabled test-case outcome is failed but the assertion tree contains no failed assertion. TeamCity emits the corresponding `testFailed` service message, and TAP emits a synthetic failing test point with a matching plan. The behavior is gated by `retryFailed() > 0`, so the zero-retry reporter paths remain unchanged. Parser/consumer-oriented scenarios cover all four reporters.

### M-1 — Accepted failures remain consumer-visible failures in JUnit and TAP

**Severity:** Medium

**Status:** Resolved

With `--retry-failed 2`, both `[!mayfail]` failure and expected `[!shouldfail]` failure correctly stop after one attempt and exit successfully. However, an exploratory run of `[.retry-mayfail]` showed:

- JUnit suite counters say `failures="0"`, but the same `<testcase>` contains both `<skipped>` and `<failure>`. Consumers normally derive the case result from the child element, so the document is internally contradictory.
- TAP emits `not ok 1 - false` with exit code 0 and no TODO/SKIP directive, which represents a failing test point.

The accepted-failure scenario is checked only through `retry-recorder` in `tests/TestScripts/testRetryFailed.py:544-584`; the JUnit and TAP parser/output checks at lines 1224-1474 cover ordinary flaky and exhausted failures only.

This behaviour exists in the reporter's assertion-oriented path, but retry-enabled output is required to preserve Catch2's accepted-failure outcome and to report final logical status correctly. The fix should suppress counting failure elements/test points for `totals.testCases.failedButOk`, while retaining the assertion as non-failing diagnostics.

**Resolution:** For retry-enabled output, JUnit represents an accepted failure as skipped and preserves its assertion text under `system-out`, without a `failure` or `error` child. TAP marks the assertion point with `# TODO accepted failure`. SonarQube and TeamCity controls verify that their accepted-failure representations remain non-failing. The new tests parse or inspect each reporter's consumer-visible protocol.

### H-2 — Failures without assertion events produce invalid or misleading machine-readable output

**Severity:** High

**Status:** Open

`-w NoAssertions` creates a retryable failure by incrementing the failed assertion count directly in `RunContext::testForMissingAssertions` (`src/catch2/internal/catch_run_context.cpp:643-652`). It does not emit an `assertionEnded` event. The four assertion-buffering reporters therefore cannot distinguish this outcome from the unexpected `[!shouldfail]` pass fixed by H-1:

- JUnit and SonarQube collect superseded diagnostics only from assertion nodes (`catch_reporter_junit.cpp:109-155`, `catch_reporter_sonarqube.cpp:71-130`) and hard-code their final assertion-free failure as an unexpected `[!shouldfail]` pass (`catch_reporter_junit.cpp:328-387`, `catch_reporter_sonarqube.cpp:172-209`).
- TeamCity buffers only assertion-derived messages and uses the same hard-coded final fallback (`catch_reporter_teamcity.cpp:60-180`).
- TAP buffers only assertion events, adds a synthetic `[!shouldfail]` point, and then computes the plan as the authoritative assertion total plus the synthetic count (`catch_reporter_tap.cpp:231-321`). For `NoAssertions`, the authoritative total already contains the synthetic missing-assertion failure, so the plan is counted twice.

**Reproduction against `b19a1b75`:**

```text
SelfTest.exe "An empty test with no assertions" --retry-failed 1 \
  -w NoAssertions --colour-mode none --reporter <reporter>
```

All four invocations used two attempts and exited with code `42`. Their final output was incorrect:

| Reporter | Observed result |
| --- | --- |
| JUnit | Correct failure count, but `<failure type="!shouldfail">` says the empty test passed unexpectedly; the superseded-attempt `system-out` block contains only its heading |
| SonarQube | Correct failing element, but it claims `[!shouldfail]`; the superseded-attempt comment contains no reason |
| TeamCity | Emits `testFailed`, but the message claims `[!shouldfail]`; no diagnostic is emitted for the superseded first attempt |
| TAP | Emits one `not ok` point claiming `[!shouldfail]`, followed by plan `1..2`; the plan names two points although only one was emitted |

A disposable deterministic case that had no assertions on attempt 1 and passed on attempt 2 also proved the superseded-diagnostic loss: JUnit and SonarQube emitted an empty `Attempt 1 ... failed` block, while TeamCity and TAP emitted no failure reason for attempt 1. Console correctly reported `No assertions in test case`, so the information exists before these reporter-specific buffers discard it.

**Impact:** TAP consumers can reject the result as an inconsistent stream, while all four protocols provide a false failure reason. A flaky pass can also erase the only meaningful diagnostic for its superseded missing-assertion failure. This violates R-5, E-8, and the machine-readable reporter contract.

**Required resolution:** carry or derive the semantic failure reason independently of failed assertion events, preserve `missingAssertions` diagnostics for superseded attempts, and make TAP's plan equal the number of emitted test points. Add exhausted and fail-then-pass `NoAssertions` scenarios for JUnit, SonarQube, TeamCity, and TAP.

### M-2 — Console and compact report final skipped or accepted outcomes as failed

**Severity:** Medium

**Status:** Open

The retry loop correctly stops at every non-failed final outcome, not only at a pass. However, the extra final line in both human-readable reporters branches only on `isFlaky`; every other outcome after more than one attempt is printed as `failed after ...` (`catch_reporter_console.cpp:535-546`, `catch_reporter_compact.cpp:270-282`).

Two disposable deterministic cases reproduced the contradiction:

```cpp
// Attempt 1 fails, attempt 2 skips.
if (++attempt == 1) { CHECK(false); } else { SKIP("second attempt skips"); }

// [!shouldfail]: attempt 1 passes unexpectedly, attempt 2 fails as expected.
CHECK(++attempt < 2);
```

The first run ended with Catch2's all-skipped exit code and summary `1 skipped`, but both reporters printed `Test case 'failure then skip' failed after 2 of 3 attempts`. The second exited successfully and its summary said `1 failed as expected`, but both printed `failed after 2 of 3 attempts`.

**Impact:** the prominent retry-specific line contradicts the authoritative totals and exit status for valid outcomes in the decision table.

**Required resolution:** choose the final message from `TestCaseStats::totals.testCases` (passed, failed, skipped, or accepted failure) rather than treating `!isFlaky` as equivalent to failure. Add both transition scenarios to the recorder and console/compact checks.

### M-3 — JUnit suite counters remain assertion counts instead of final logical-result counts

**Severity:** Medium

**Status:** Open

For retry-enabled output, JUnit initializes `failures`, `skipped`, and `tests` from final assertion totals and only raises them to a test-case-derived minimum (`catch_reporter_junit.cpp:242-265`). This prevents superseded attempts from inflating the counters, but it does not implement the reviewed requirement that suite counters use final logical results (`03-spec.md:116`).

A single deterministic test containing three final `CHECK(false)` assertions, run with `--retry-failed 1`, produced one `<testcase>` element but `<testsuite tests="3" failures="3">`. The final status is failing, but the suite metrics describe three tests and three logical failures instead of one.

**Impact:** JUnit dashboards and aggregate metrics overcount tests and failures, and the suite attributes disagree with the document's child test-case count.

**Required resolution:** define counters from the emitted final test-case representation (including error versus failure and accepted/skipped outcomes), while retaining superseded assertions only as non-counting diagnostics. Add multi-assertion pass and failure cases and assert both suite attributes and child-element counts.

### L-1 — Reporter documentation and final validation note predate the semantic-outcome fix

**Severity:** Low

**Status:** Open

`docs/reporters.md:52-54` says that, when retries are enabled but unused, only XML and JSON differ. After M-1, a one-attempt accepted failure also changes JUnit and TAP output, so the statement is no longer true. `IMPLEMENTATION_NOTES.md:180-209` describes the T13/T14 clean-build result as validation of the final files, but the current reporter fix in `b19a1b75` was committed afterwards and its incremental rebuild/full-suite evidence is recorded only in this course artifact.

**Required resolution:** document the accepted-failure exception and append the post-review reporter change and exact final validation results to `IMPLEMENTATION_NOTES.md`.

## Verification Gaps

- Machine-readable special-tag coverage now covers exhausted unexpected `[!shouldfail]` passes and accepted `[!mayfail]` failures, but not a transition from unexpected pass to accepted `[!shouldfail]` failure.
- `NoAssertions` is named as retryable by R-5 but has no retry or reporter scenario. This gap allowed H-2 through both full suites.
- No test ends a retried logical test case as skipped or accepted failure, so the human-reporter branch in M-2 is untested.
- JUnit scenarios use one final assertion, so assertion-derived suite counters happen to equal logical test-case counters and M-3 is hidden.
- Fatal-path structure is parser-tested only for JUnit. During review, XML output from the fatal fixture remained well-formed; JSON and Automake wrote no stdout before Windows terminated the process. This was not classified as a defect because fatal reporting is explicitly best-effort and the review did not establish a regression from `v3.16.0`, but it remains an unverified compatibility area.
- Debugger-break preservation (`CO-6`) is supported only by code-path inspection; there is no automated debugger integration test.

## Test-Quality Assessment

The main scenario driver generally uses exact event sequences, exact totals, real JSON/XML parsers, negative assertions, exit-code checks, and fresh child processes. It would fail for common production regressions such as missing retries, leaked retry budgets, wrong final-only totals, broken attempt numbering, malformed JSON/XML, or superseded failures counted by the ordinary flaky scenarios. T03 also recorded an actual red harness run before its assertion was corrected.

The first review found that reporter cases used ordinary failed assertions while special tags were exercised only through the recorder. H-1/M-1 added direct special-tag reporter coverage, but the second review showed that the matrix is still organized mainly by assertion outcome. It does not cross retry history with every final outcome, failures created without assertion events, or multiple final assertions. Those missing dimensions explain H-2, M-2, and M-3.

## Review Evidence

- Inspected the complete 42-file `v3.16.0..9037e6fa` change set and the relevant unchanged runner, tracker, totals, invoker, and reporter-base code.
- Traced CLI, attempt loop, tracker/generator reset, fixture prepare/tear-down, assertion counter restoration, abort precedence, fatal event balancing, cumulative/streaming reporter state, and zero-retry compatibility against the approved specification and clarifications.
- `git diff --check v3.16.0 HEAD` passed before the review and `git diff --check` passed again after the resolution.
- Both the Catch2 checkout and course repository were clean before this artifact was created; ignored Python bytecode caches were the only ignored workspace entries. The resolution was committed separately and exported as patch `0015`.
- Reproduced H-1 and M-1 with the previously validated Windows binary, then added scenarios that fail on the reviewed implementation and pass on the resolution.
- Regenerated the amalgamated sources, rebuilt both configured trees, and reran the final suites after the reporter fix: basic preset 92/92 and all preset 157/157. The focused reporter/amalgamation group passed 5/5, no unapproved baselines were produced, and the only build warnings were the four known baseline MSVC `D9025` warnings.
- Applied all 15 exported patches to a separate clean `v3.16.0` worktree. The resulting tree ID, `ce9de81f9b53d5b54637c9157f8f468eae74c762`, exactly matched the implementation branch.
- The second review re-read the complete final 43-file `v3.16.0..b19a1b75` diff and reran the focused cumulative/retry/amalgamation group: 5/5 passed.
- Reproduced H-2 directly with the built `SelfTest.exe` and all affected reporters. Used a disposable external test executable linked against the final Catch2 libraries to reproduce fail-to-skip, unexpected-pass-to-accepted-failure, fail-to-pass `NoAssertions`, and multi-assertion JUnit scenarios without modifying the Catch2 checkout.
- `git diff --check v3.16.0..HEAD` passed after the second review, both tracked repositories remained clean, and no unapproved baseline was present.

## Resolution Log

| Finding | Resolution | Verification |
| --- | --- | --- |
| H-1 | Resolved in `b19a1b75` (`0015-Report-semantic-retry-outcomes-in-machine-reporters.patch`) | New JUnit, SonarQube, TeamCity, and TAP semantic-failure scenarios pass; focused group 5/5; all preset 157/157 |
| M-1 | Resolved in `b19a1b75` (`0015-Report-semantic-retry-outcomes-in-machine-reporters.patch`) | New accepted-failure scenarios pass for all four reporters; basic preset 92/92; all preset 157/157 |
| H-2 | Open | `NoAssertions` direct reproduction: false `[!shouldfail]` reason in four reporters, TAP one point with plan `1..2`, superseded reason lost |
| M-2 | Open | Disposable fail-to-skip and unexpected-pass-to-accepted-failure cases contradict console/compact final lines |
| M-3 | Open | One JUnit child case with three final failures reports `tests="3" failures="3"` |
| L-1 | Open | Documentation and implementation-note evidence inspected against post-review behavior and commit history |
