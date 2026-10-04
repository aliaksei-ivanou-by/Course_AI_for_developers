# Phase 3 Behavioral Specification: `--retry-failed`

Status: Accepted by the human reviewer
Inputs: [task specification](../../01%20C%2B%2B%20-%20Retry%20Failed%20Tests%20in%20Catch2.md) (cited as **A** with its section), [00-task-contract.md](00-task-contract.md), [02-codebase-map.md](02-codebase-map.md) (cited as **M** with its section), decisions in [04-clarifications.md](04-clarifications.md) (cited as **C1–C15**); compatibility requirements are **CO-1–CO-7**

This document states what the feature does and why. It names Catch2 concepts only where they are existing public behaviour that must be preserved; how the behaviour is implemented belongs to the Phase 4 plan. "Catch2 today" means the unmodified `v3.16.0` baseline recorded in [01-baseline.md](01-baseline.md).

## 1. Terms

| Term | Definition |
| --- | --- |
| Logical test case | One registered test case selected for the run. It produces exactly one final result. (A, Terminology) |
| Attempt | One complete execution of a logical test case: every partial run needed to traverse its sections and generators, from a fresh state, ending with a classified outcome. (A, Terminology) |
| Partial run | One entry into the test-case body, as reported by Catch2's existing partial test-case events. A partial run is never a retry. (A, Terminology) |
| Retry | Any attempt after attempt 1. |
| `N` | The retry budget: the number of retries allowed after attempt 1 for each logical test case. Maximum attempts `M = N + 1`. |
| Attempt outcome | The result Catch2 already assigns to a completed run of a test case, after its special-tag handling: passed, failed, skipped, or accepted failure. (A, Retry Decision; M §5) |
| Final outcome | The attempt outcome of the last attempt that runs. |
| Superseded attempt | An attempt whose outcome was failed and that was followed by a retry. |
| Flaky pass | A logical test case whose final outcome is passed and that had at least one superseded attempt. (A, Terminology) |

## 2. Command Line

| ID | Requirement | Source |
| --- | --- | --- |
| CLI-1 | The option is spelled `--retry-failed N`. It has no short alias. | A, CLI |
| CLI-2 | Default `N` is 0. Omitting the option and `--retry-failed 0` behave identically to each other and to Catch2 today when running tests (§8, CO-1). | A, CLI |
| CLI-3 | `N` accepts the same unsigned decimal syntax as `--shard-count`: optional surrounding whitespace, an optional leading `+`, and leading zeros are accepted; the range is `0` to `4294967295` (the largest `unsigned int` on the 32-bit-`int` platforms Catch2 supports). | C12 |
| CLI-4 | A missing value, a negative value, a fractional value (`1.5`), a malformed value (`abc`, `1e3`, `0x10`), a value above `4294967295`, and repeating the option are rejected through Catch2's normal command-line error path: an `Error(s) in input:` message on stderr and a non-zero exit code, before any test case starts and before any reporter output. | A, CLI; C12 |
| CLI-5 | The help text states that `N` is the number of retries after the first attempt, not the total number of attempts, and that the default is 0. | A, CLI |
| CLI-6 | The value is available through Catch2's configuration abstraction, so code that only sees the configuration (reporters, listeners, the runner) can read it. Existing configuration implementations that do not provide it keep compiling and behave as `N = 0`. | A, CLI; contract |
| CLI-7 | The budget applies to each logical test case independently; it is not a run-wide pool. | A, CLI |
| CLI-8 | `M = N + 1` is computed and reported without overflow for the largest accepted `N` (`M = 4294967296`). | A, CLI; C13 |

## 3. Retry Decision

| ID | Requirement | Source |
| --- | --- | --- |
| R-1 | The decision is made only after an attempt is complete, i.e. after all of its partial runs. Partial runs never consume the budget. | A, Retry Decision |
| R-2 | The decision uses Catch2's existing attempt outcome; no second pass/fail classifier is introduced. | A, Retry Decision |
| R-3 | Decision table: | A, Retry Decision |

| Attempt outcome | Retry? | Final outcome if no retry follows |
| --- | --- | --- |
| Passed | No | Passed |
| Failed, retries remaining, abort threshold not reached | Yes | — |
| Failed, no retries remaining | No | Failed |
| Failed, abort threshold reached during the attempt | No | Failed (§7) |
| Skipped | No | Skipped |
| Accepted failure (`[!mayfail]` with failures, `[!shouldfail]` with failures) | No | Accepted failure, as Catch2 today |
| Unexpected pass under `[!shouldfail]` (Catch2 classifies it as failed) | Yes, if retries remain | Failed, as Catch2 today |

| ID | Requirement | Source |
| --- | --- | --- |
| R-4 | A test case that passes on attempt 1 runs exactly once. Retrying stops at the first attempt whose outcome is not failed; unused budget is not consumed. | A, Retry Decision |
| R-5 | Failures that Catch2 recovers from are retryable when they make the attempt outcome failed: failed assertions (`CHECK`, `REQUIRE`), `FAIL`, exceptions that Catch2 converts into a failed assertion, and the missing-assertion failure produced by `-w NoAssertions`. | A, Retry Decision; M §5 |
| R-6 | Failures Catch2 cannot return from are not retryable: crash, fatal signal, structured exception, stack overflow, forced termination. Catch2's existing fatal-error reporting applies, and the process ends as it does today. | A, Retry Decision; M §13 Q7 |
| R-7 | A retry reruns the whole logical test case from its beginning. It never resumes at the failed assertion, section, or generator value. | A, Retry Decision |
| R-8 | An attempt that contains both failed assertions and a skip is failed, because Catch2's existing classification ranks failure above skip (R-2). | M §5; C5 |

## 4. Fresh State per Attempt

Every attempt behaves like a new execution of that one test case in the same process (A, Fresh State).

| ID | Guarantee | Source |
| --- | --- | --- |
| S-1 | Section traversal starts from the first eligible path; nested sections are traversed afresh. | A, Fresh State |
| S-2 | Generators are recreated and start from their first eligible value. | A, Fresh State |
| S-3 | Section, generator, and path filters given on the command line (`-c/--section`, `-g/--generator-index`, `-p/--path-filter`) apply to every attempt exactly as to attempt 1. | A, Interaction |
| S-4 | Catch2's random number generator is reseeded at the start of every attempt with the run's seed, so every attempt sees the same random values as attempt 1 and runs with a fixed `--rng-seed` stay reproducible. | A, Fresh State; C3 |
| S-5 | Assertion and outcome accumulation for the attempt starts from zero. | A, Fresh State |
| S-6 | Output capture boundaries start afresh: each attempt's captured stdout/stderr is attributable to that attempt. | A, Fresh State |
| S-7 | Fixtures: a fixture that Catch2 creates once per test case (`TEST_CASE_PERSISTENT_FIXTURE`) is created before and destroyed after **each attempt**, with balanced construction and destruction. Fixtures Catch2 creates per partial run (`TEST_CASE_METHOD`, `METHOD_AS_TEST_CASE`) keep that behaviour. | A, Fresh State; M §4; C9 |
| S-8 | Reporter-side data that Catch2 owns for the attempt (for example, the section tree a cumulative reporter builds) starts afresh for each attempt, while earlier attempts remain available as diagnostics (§5). | A, Fresh State |
| S-9 | State owned by test code is not rolled back: globals, statics, files, environment variables, databases, network services, threads the test started. This is documented as a limitation and is what deterministic retry tests rely on. | A, Fresh State; C15 |

## 5. Reporter-Observable Behaviour

### 5.1 Event lifecycle

With `N = 0` (or the option omitted), reporters and listeners observe exactly the event sequence and data of Catch2 today (CO-1 in §8). The rules below apply when `N ≥ 1`.

```text
testCaseStarting                          once per logical test case
  attempt start (k = 1, M)                every attempt, including attempt 1
    testCasePartialStarting(p) ... testCasePartialEnded(p)    one or more partial runs
  attempt end (k = 1, M, attempt result)
  attempt start (k = 2, M)                only if attempt 1 was superseded
    ...
  attempt end (k = 2, M, attempt result)
testCaseEnded                             once, with the final result
```

| ID | Requirement | Source |
| --- | --- | --- |
| E-1 | Exactly one `testCaseStarting`/`testCaseEnded` pair per logical test case, regardless of the number of attempts. | A, Reporter Contract |
| E-2 | Every attempt is bracketed by an attempt-start and an attempt-end notification, nested inside the test-case pair and enclosing that attempt's partial runs. Attempt notifications are emitted for every attempt when `N ≥ 1`, including a test that passes on attempt 1, so a reporter sees one consistent shape. | A, Reporter Contract; C1 |
| E-3 | Both notifications carry the one-based attempt number `k` and the maximum `M`. | A, Reporter Contract; C13 |
| E-4 | The attempt-end notification carries the attempt's own result: its assertion counts, its outcome (§3), its captured stdout/stderr, whether it is the final attempt, and whether a retry follows. | A, Reporter Contract; C4 |
| E-5 | Partial-run events keep their meaning ("one entry into the test case"). Their part number keeps increasing across attempts within one logical test case: attempt 1 uses 0…p, attempt 2 continues at p+1. They are never used as attempt events. | A, Reporter Contract; C2 |
| E-6 | `testCaseEnded` carries the final result (§6), whether the test case is a flaky pass, the number of attempts used, and `M`. Its captured stdout/stderr is the output of all attempts, in order. | A, Reporter Contract; C4 |
| E-7 | Every start has a matching end, for failed attempts, the final attempt, an attempt ended by `--abort`/`--abortx`, and, as a best effort, an attempt ended by a fatal error, ended before Catch2's existing fatal-path end of the test case. | A, Reporter Contract; C10 |
| E-8 | Assertions, sections, messages, benchmarks, and captured output of superseded attempts are delivered to reporters as they happen and are not withdrawn. Running totals attached to individual assertion events are progress information; the attempt-end and test-case-end results are authoritative. | A, Reporter Contract; C6 |
| E-9 | Reporters that do not handle attempt notifications keep compiling and working; attempt notifications are optional to handle. Multi-reporter forwarding delivers them to every reporter and listener in the same order as other events. | A, Reporter Contract; contract |

### 5.2 Built-in reporters

When `N ≥ 1` and at least one retry occurs (C7, C8):

| Reporter | Required behaviour |
| --- | --- |
| console | Failures of a superseded attempt are printed as today and clearly marked as belonging to attempt `k` of `M`, with a note that a retry follows. A flaky pass is identified on its own line, naming the attempt that passed. An exhausted test is identified as failed after `M` attempts. Run totals count logical test cases (§6). |
| compact | Failures remain visible; retries and a flaky pass are identified; the summary counts logical test cases. |
| XML | Each attempt is represented structurally with its number, `M`, and outcome, and the assertions written inside it belong to that attempt. The test case's overall result states the final outcome and whether it is flaky. Output stays well-formed; `xml-format-version` is unchanged. |
| JSON | The test-case object states attempts used, `M`, and flaky; each partial-run entry states its attempt number; each attempt's result is available. Output stays valid JSON; the format `version` is unchanged. |
| JUnit | A flaky pass produces a test case without failure or error elements; failures of superseded attempts remain in the report in a form JUnit consumers do not count as failures. An exhausted test reports the failures of its final attempt as failures; failures of its earlier attempts are kept in the same non-counting form. Suite counters use final logical results. Output stays well-formed. |
| SonarQube | As JUnit: final outcome decides failure; superseded failures remain as non-failing diagnostics. |
| TeamCity | A flaky pass is not reported as a failed test; superseded failures remain visible as non-failing messages. An exhausted test is reported as failed. |
| TAP | Superseded failures are not emitted as failing test points; they remain as TAP diagnostic lines. The final attempt's assertions are emitted as test points as today. |
| Automake | One result line per logical test case, based on the final outcome. |

With `N ≥ 1` but no retry in the whole run, every reporter's output may differ from Catch2 today only by the structural attempt information of XML and JSON (E-2). A reporter that writes an attempt's lines at the end of the attempt (TAP, which does not capture test output) produces the same text, but its lines can interleave differently with output the test writes directly to the console. With `N = 0`, output is identical to Catch2 today for every reporter (CO-1).

## 6. Final Statistics and Exit Status

| ID | Requirement | Source |
| --- | --- | --- |
| T-1 | Each logical test case that starts contributes exactly one test-case count, from its final outcome. Test cases not started because the run aborted are handled as Catch2 today: reported as skipped by the abort and not counted. | A, Statistics; A, Interaction |
| T-2 | Final assertion totals contain only the final attempt's assertions. Assertions of superseded attempts are reported as attempt diagnostics (E-4, E-8) and are not added to test-case, run, or session totals. | A, Statistics; C6 |
| T-3 | A flaky pass contributes one passed test case and no failed test case or failed assertion. | A, Statistics |
| T-4 | An exhausted test contributes one failed test case and the assertions of its final attempt. | A, Statistics |
| T-5 | Skipped and accepted-failure outcomes are counted as in Catch2 today. The existing difference for an unexpected `[!shouldfail]` pass (the extra failed assertion appears in the session's totals and exit status but not in the run totals given to reporters) is preserved. | A, Statistics; M §5; C11 |
| T-6 | The exit status follows Catch2's existing rules applied to final logical results: success when every selected test case has an outcome Catch2 treats as successful, including flaky passes; test-failure exit code when at least one test case is finally failed; Catch2's other exit codes (no tests run, all tests skipped, unmatched spec) unchanged. | A, Statistics |

## 7. Abort Options

| ID | Requirement | Source |
| --- | --- | --- |
| AB-1 | `--abort` and `--abortx X` take precedence. If the abort threshold is reached during an attempt, that attempt ends, no retry starts, its outcome is final, and the remaining test cases are handled as Catch2 does today (reported as skipped by the abort). | A, Interaction |
| AB-2 | Failed assertions of a superseded attempt do not count toward the abort threshold for the rest of the run. Failed assertions of a final attempt count as today. | A, Interaction; C6 |
| AB-3 | Consequence: with `--abort` (threshold 1), an attempt with any counted failed assertion reaches the threshold, so it is not retried. An unexpected `[!shouldfail]` pass does not count toward the threshold in Catch2 today, so it is still retried and does not abort the run. With `--abortx X`, an attempt is retried only if its counted failures together with those already counted stayed below `X`. | contract; C14 |

## 8. Compatibility

| ID | Requirement | Source |
| --- | --- | --- |
| CO-1 | With the option omitted or `N = 0`: same tests executed the same number of times, same event sequence and event data, same reporter output for every built-in reporter, same totals, same exit status as Catch2 today. The only intended difference is the help text (`-h`), which lists the new option. Existing approval baselines change only where test cases are intentionally added for this feature. | A, CLI; A, Reporter Contract |
| CO-2 | Existing custom configuration implementations, reporters, and listeners compile and run unchanged: no new mandatory (pure virtual) member is added to a public extension interface. | A, CLI; A, Reporter Contract |
| CO-3 | New public data fields default to the single-attempt, non-flaky values, so existing code that constructs or reads those structures sees today's meaning. | CO-2 |
| CO-4 | Filtering, hidden tests, ordering, sharding, registration, and test selection are unchanged; retries happen inside the already selected shard and never change shard membership or order. | A, Interaction |
| CO-5 | Listing modes do not execute tests and therefore never retry. | A, Interaction |
| CO-6 | Retry support does not suppress debugger breaks (`-b`), fatal-condition handling, or other assertion-time behaviour. | A, Interaction |
| CO-7 | No new session-level nondeterminism: with a fixed seed and order, two runs with the same `N` produce the same sequence of attempts. | A, Fresh State |

## 9. Acceptance Scenarios

Each scenario is checkable from observable behaviour alone. "Counting fixture" means a test that fails a fixed number of times using a counter outside Catch2's control and then passes. `M = N + 1`.

| ID | Given | Expected | Traces to |
| --- | --- | --- | --- |
| AC-01 | Option omitted | `N = 0` visible through configuration | A Req. tests 1 |
| AC-02 | `--retry-failed 0`, `1`, `3`, `4294967295` | Accepted; configuration reports 0, 1, 3, 4294967295 | A tests 2, 3; A CLI table |
| AC-03 | `--retry-failed` (no value), `-1`, `abc`, `1.5`, `1e3`, `4294967296`, option given twice | `Error(s) in input:` on stderr, non-zero exit, no test runs, no reporter output | A tests 3, 4; CLI-4 |
| AC-04 | `-h` | Help lists `--retry-failed` without a short alias and states that `N` counts retries after the first attempt and that the default is 0 | A test 5; CLI-5 |
| AC-05 | `N = 4294967295`, test passes on attempt 1 | Runs once; the attempt notifications report `k = 1` and `M = 4294967296` without overflow | A test 3; CLI-8 |
| AC-06 | `N = 2`, passes immediately | 1 execution; passed; not flaky; exit 0 | A tests 6, 11; Acceptance row 1 |
| AC-07 | `N = 2`, fails once then passes | 2 executions; passed; flaky; exit 0 | A tests 7, 29; Acceptance row 2 |
| AC-08 | `N = 2`, fails twice then passes | 3 executions; passed; flaky; exit 0 | A test 8; Acceptance row 3 |
| AC-09 | `N = 2`, always fails | 3 executions (`N + 1`); failed; not flaky; failure exit code | A tests 9, 30; Acceptance row 4 |
| AC-10 | `N = 1`, would pass on attempt 3 | 2 executions; failed; failure exit code | A test 10; Acceptance row 5 |
| AC-11 | `N = 2`; test X fails once, test Y fails twice, then each passes | X runs 2 times, Y runs 3 times, both are flaky passes; budgets do not leak between them | A test 12; CLI-7 |
| AC-12 | `N = 2`; one immediate pass, one fail-then-pass, one always-fail; each attempt makes exactly one `CHECK` | Immediate pass runs once; test-case totals: 2 passed, 1 failed; assertion totals: 2 passed, 1 failed (final attempts only); failure exit code | A test 13; Acceptance three-test example |
| AC-13 | One `SECTION`, failing on attempt 1 | Attempt 2 starts from the first section | A test 14; S-1 |
| AC-14 | Sibling and nested `SECTION`s, failing in a late path on attempt 1 | Attempt 2 visits the full expected path sequence again, no stale tracker state | A test 15; S-1 |
| AC-15 | `GENERATE`, failing on a late value in attempt 1 | Attempt 2 starts from the first value | A test 16; S-2 |
| AC-16 | Generators combined with nested sections | Attempt 2 repeats the complete traversal | A test 17; S-1, S-2 |
| AC-17 | Persistent and per-run fixtures, failing on attempt 1 | Balanced construction/destruction; each attempt gets a fresh persistent fixture | A test 18; S-7 |
| AC-18 | `SKIP` with `N = 2` | 1 execution; skipped; no retry | A test 19; Acceptance row 6 |
| AC-19 | `[!mayfail]` failing; `[!shouldfail]` failing; `[!shouldfail]` passing with `N = 2` | Accepted failure, 1 execution; accepted failure, 1 execution; 3 executions, failed | A test 20; R-3 |
| AC-20 | `N = 2`, fail-then-pass, recording reporter | Attempt notifications numbered 1 and 2 with `M = 3`, balanced, nested in one test-case pair; final flagged flaky | A tests 21, 22; E-1–E-4 |
| AC-21 | Sections or generators with a retry, recording reporter | Partial events inside each attempt, part numbers continuous across attempts, distinct from attempt notifications | A test 23; E-5 |
| AC-22 | Fail-then-pass that writes to stdout and fails with a message in attempt 1 | Attempt 1 assertions, message, and output are delivered to reporters and kept in the test-case output | A test 24; E-4, E-6, E-8 |
| AC-23 | Console reporter, fail-then-pass and always-fail | Retry and flaky pass identified; exhausted failure identified | A test 25; §5.2 |
| AC-24 | XML and JSON, fail-then-pass | Attempts and flaky represented structurally | A test 26; §5.2 |
| AC-25 | JSON, XML, JUnit, SonarQube outputs for scenario AC-12 | Parse with a real parser; final statuses: pass, pass (flaky), fail | A test 27; §5.2 |
| AC-26 | Immediate pass, flaky pass, exhausted failure, skip, accepted failure | Test-case and assertion totals per T-1–T-5 | A test 28 |
| AC-27 | Run with filters (`-c`, test spec) and with `--shard-count`/`--shard-index` | Only selected tests run; retries stay within the shard; filters apply to every attempt | A test 31; S-3, CO-4 |
| AC-28 | `--abort --retry-failed 2` with a failing test followed by others | No retry; remaining tests reported as skipped by the abort | A test 32; AB-1, AB-3 |
| AC-29 | `--abortx 2 --retry-failed 1`; test A fails 1 assertion on attempt 1 and passes on attempt 2; test B then fails 1 assertion on every attempt; test C passes | A's superseded failure does not count, so B's attempt 1 does not reach the threshold: B runs 2 attempts and ends failed, C runs, and the run does not abort | A test 32; AB-2 |
| AC-30 | Option omitted and `N = 0`, recording reporter and approval baselines | Event sequence, statistics, and outputs identical to Catch2 today | A test 33; CO-1 |
| AC-31 | `--list-tests` with `N = 2` | Nothing executes | A Interaction; CO-5 |
| AC-32 | A reporter and a listener written against today's API, without attempt handling, with `N = 2` and a fail-then-pass test | Both compile unchanged and receive a coherent event sequence; the final result is passed | A Reporter Contract; CO-2, E-9 |
| AC-33 | Two reporters and a listener together, `N = 2`, fail-then-pass | All three receive the same attempt notifications in the same order relative to other events | A Reporter Contract (multi-reporter, listeners); E-9 |
| AC-34 | `N = 2` and a test using `GENERATE(take(3, random(0, 1000)))` that fails on attempt 1, run twice with the same `--rng-seed` | Attempt 2 sees the same values as attempt 1; both runs produce the same sequence | A Fresh State; S-4, CO-7 |
| AC-35 | `N = 2` and a test that triggers a fatal signal, where the platform allows it | One attempt; Catch2's existing fatal-error report; the process ends as today; no retry | A Retry Decision; R-6, E-7 |
| AC-36 | `--abort --retry-failed 2` and a `[!shouldfail]` test that passes, followed by a passing test | 3 attempts; final outcome failed; the run does not abort, so the next test runs (as Catch2 today) | A Retry Decision table; AB-3; C14 |

## 10. Documentation Obligations

The user and extension documentation must cover (A, Documentation Requirements): the syntax and default of `--retry-failed`; `N` as additional attempts; examples for zero, one, and several retries; final-result and flaky semantics; the difference between attempts and partial runs; the fresh-state guarantee (§4); the limitation that test-owned state is not rolled back (S-9); interactions with special tags and abort options (§3, §7); and every new reporter notification or data field with its lifecycle, nesting, numbering, and compatibility behaviour (§5).

## 11. Non-Goals

From the contract and A, Interaction:

- Wrapper executables, scripts, CTest/CI retry loops, or recursive process launches.
- Retrying an individual assertion, section, generator value, or partial run in isolation.
- Retrying crashes, fatal signals, forced termination, or stack overflow.
- Parallel retries, retry delays, retry-only filters, persistence across process launches.
- Rolling back state owned by test code.
- Registering retries as separate test cases; changing shard membership or order.

## Gate Status

| Gate | Status |
| --- | --- |
| A reviewer can determine pass or fail for every acceptance example without seeing the implementation | ✅ §9, with outcomes defined in §3 and §6 |
| No open question would materially change public behaviour or the reporter contract | ✅ All decisions recorded in C1–C15 and accepted by the reviewer |
| The specification says what and why; internal file changes remain in the plan | ✅ No file, class, or callback names introduced; existing Catch2 behaviour named only where it is a compatibility boundary |
