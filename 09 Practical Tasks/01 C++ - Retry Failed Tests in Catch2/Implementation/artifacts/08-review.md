# Phase 7 Fresh-Context Review

Date: 2026-10-04

Reviewed Catch2 revision: `9037e6faa6638b160d2f24e240f6b671d979c99d`

Baseline: `v3.16.0` (`fd79eadb5bc1760e7cbae12fd45b0d0040d1bb73`)

## Gate Status

**Not passed.** One high-severity and one medium-severity reporter finding remain open. No Catch2 production or test file was changed during this review.

## Findings

### H-1 — Exhausted unexpected `[!shouldfail]` passes are reported as successful by four machine-readable reporters

**Severity:** High

**Status:** Open

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

### M-1 — Accepted failures remain consumer-visible failures in JUnit and TAP

**Severity:** Medium

**Status:** Open; likely resolved by the same semantic-outcome handling as H-1

With `--retry-failed 2`, both `[!mayfail]` failure and expected `[!shouldfail]` failure correctly stop after one attempt and exit successfully. However, an exploratory run of `[.retry-mayfail]` showed:

- JUnit suite counters say `failures="0"`, but the same `<testcase>` contains both `<skipped>` and `<failure>`. Consumers normally derive the case result from the child element, so the document is internally contradictory.
- TAP emits `not ok 1 - false` with exit code 0 and no TODO/SKIP directive, which represents a failing test point.

The accepted-failure scenario is checked only through `retry-recorder` in `tests/TestScripts/testRetryFailed.py:544-584`; the JUnit and TAP parser/output checks at lines 1224-1474 cover ordinary flaky and exhausted failures only.

This behaviour exists in the reporter's assertion-oriented path, but retry-enabled output is required to preserve Catch2's accepted-failure outcome and to report final logical status correctly. The fix should suppress counting failure elements/test points for `totals.testCases.failedButOk`, while retaining the assertion as non-failing diagnostics.

## Verification Gaps

- Machine-readable special-tag coverage is missing. The recorder proves the runner's `[!mayfail]` and `[!shouldfail]` totals, but no built-in reporter test consumes those final semantic outcomes. This gap allowed H-1 and M-1 through the full suite.
- Fatal-path structure is parser-tested only for JUnit. During review, XML output from the fatal fixture remained well-formed; JSON and Automake wrote no stdout before Windows terminated the process. This was not classified as a defect because fatal reporting is explicitly best-effort and the review did not establish a regression from `v3.16.0`, but it remains an unverified compatibility area.
- Debugger-break preservation (`CO-6`) is supported only by code-path inspection; there is no automated debugger integration test.

## Test-Quality Assessment

The main scenario driver generally uses exact event sequences, exact totals, real JSON/XML parsers, negative assertions, exit-code checks, and fresh child processes. It would fail for common production regressions such as missing retries, leaked retry budgets, wrong final-only totals, broken attempt numbering, malformed JSON/XML, or superseded failures counted by the ordinary flaky scenarios. T03 also recorded an actual red harness run before its assertion was corrected.

The weakness is outcome diversity in reporter tests: their flaky/exhausted cases use ordinary failed assertions, where assertion status and semantic test-case status agree. Special tags are exercised only through the recorder, where the authoritative totals are already visible.

## Review Evidence

- Inspected the complete 42-file `v3.16.0..9037e6fa` change set and the relevant unchanged runner, tracker, totals, invoker, and reporter-base code.
- Traced CLI, attempt loop, tracker/generator reset, fixture prepare/tear-down, assertion counter restoration, abort precedence, fatal event balancing, cumulative/streaming reporter state, and zero-retry compatibility against the approved specification and clarifications.
- `git diff --check v3.16.0 HEAD` passed.
- Both the Catch2 checkout and course repository were clean before this artifact was created; ignored Python bytecode caches were the only ignored workspace entries.
- Reproduced H-1 and M-1 with the already validated final Windows binary from the T13 build. No build or full regression was repeated because the review made no Catch2 changes.
- The previously recorded final regression remains: basic preset 92/92, all preset 157/157, focused final checks 2/2 and 3/3, with no unapproved baselines and only the four baseline MSVC `D9025` warnings.

## Resolution Log

| Finding | Resolution | Verification |
| --- | --- | --- |
| H-1 | Open | Reproduced on final binary; fix and focused reporter tests required |
| M-1 | Open | Reproduced on final binary; expected to share H-1's semantic-outcome fix |
