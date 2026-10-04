# Phase 4 Technical Plan

Status: Approved by the human reviewer
Inputs: [03-spec.md](03-spec.md) (requirement IDs), [04-clarifications.md](04-clarifications.md) (C1–C15), [02-codebase-map.md](02-codebase-map.md) (M §), decisions in [07-decisions.md](07-decisions.md) (D1–D16)

This plan chooses the design. Production code is not changed until the reviewer approves it.

## 1. Current Architecture (summary)

One logical test case runs inside `RunContext::runTest` (M §2.2): `testCaseStarting`, invoker `prepareTestCase`, a new tracker root, one RNG seed, then a loop of partial runs until the root tracker completes or the run aborts, classification by `Totals::delta` plus the unexpected-pass adjustment, invoker `tearDownTestCase`, and `testCaseEnded`. Assertion counts live in run-wide (optionally atomic) counters that also drive `--abort`/`--abortx` (M §5, §6). Reporters receive events through `IEventListener`, whose members are all pure virtual; `MultiReporter` forwards each event explicitly (M §8). There is no attempt concept.

## 2. Design Options Considered

| Option | Summary | Verdict |
| --- | --- | --- |
| A. Attempt loop inside `RunContext::runTest` | Wrap the existing partial-run loop in an attempt loop between `testCaseStarting` and `testCaseEnded`; restore counters for superseded attempts | **Chosen** (D1, D2): smallest change, keeps one outer event pair, reuses Catch2's classifier |
| B. Rerun from the session loop | `TestGroup::execute` calls `runTest` again for failed tests | Rejected: emits several `testCaseStarting`/`testCaseEnded` pairs (E-1), sums superseded totals, splits abort handling |
| C. Separate retry runner class | New class orchestrating attempts around `RunContext` | Rejected: more code and indirection for the same seam; `RunContext` owns all needed state privately |
| D. Separate per-attempt accumulators instead of restoring counters | Count assertions into an attempt-local structure and merge only final results | Rejected: touches every assertion path, the fast path, and thread-safe counters; restoring a snapshot touches one place (D2) |

## 3. Retry-Decision Boundary

The decision is taken in `runTest` after the partial-run loop of an attempt has finished, the attempt has been classified, and the invoker tear-down has run (R-1):

```text
retry = attemptTotals.testCases.failed > 0      // Catch2's classification incl. unexpected [!shouldfail] pass (R-2, R-3)
        && retriesUsed < N                       // never computes N + 1 in 32 bits (CLI-8, C13)
        && !aborting()                           // abort precedence (AB-1)
```

`attemptTotals` is computed exactly as today's `deltaTotals` (`m_totals.delta(...)` plus the unexpected-pass adjustment), but relative to the start of the attempt.

## 4. Per-Attempt Lifecycle

Pseudo-code of the new `runTest`; lines marked `[N≥1]` run only when `m_config->retryFailed() > 0`.

```text
testCaseStarting(testInfo)
maxAttempts = uint64(N) + 1; retriesUsed = 0; partNumber = 0       // part numbers continue across attempts (E-5, C2)
allOut = allErr = ""
loop:
    updateTotalsFromAtomics(); totalsAtAttemptStart = m_totals
    attemptStart = snapshot(m_atomicAssertionCount)
    [N≥1] testCaseAttemptStarting({&testInfo, attempt = retriesUsed + 1, maxAttempts})
    testCase.prepareTestCase()                                     // persistent fixture per attempt (S-7, C9)
    m_activeTestCase = &testCase
    root = m_trackerContext.startRun(); root.setFilters(...)       // fresh trackers and generators, filters re-applied (S-1..S-3)
    seedRng(*m_config)                                             // same values each attempt (S-4, C3)
    attemptOut = attemptErr = ""
    do { ...existing partial-run body, unchanged, using partNumber++... } while (!complete && !aborting())
    attemptTotals = m_totals.delta(totalsAtAttemptStart) + unexpected-pass adjustment
    testCase.tearDownTestCase()
    allOut += attemptOut; allErr += attemptErr                     // C4
    retry = <decision of §3>
    [N≥1] testCaseAttemptEnded({..., totals = attemptTotals, attemptOut, attemptErr, aborting(), isFinal = !retry})
    if (!retry) break
    restore(m_atomicAssertionCount, attemptStart); updateTotalsFromAtomics()   // superseded attempt leaves totals and abort budget (T-2, AB-2)
    ++retriesUsed
deltaTotals = attemptTotals of the last attempt
m_totals.testCases += deltaTotals.testCases
stats = TestCaseStats(testInfo, deltaTotals, allOut, allErr, aborting())
stats.attemptCount = retriesUsed + 1; stats.maxAttempts = maxAttempts; stats.isFlaky = retriesUsed > 0 && deltaTotals.testCases.passed == 1
testCaseEnded(stats)
return deltaTotals
```

Zero-retry equivalence (CO-1): with `N = 0` the loop body runs once; no attempt event is emitted; `prepareTestCase`, `startRun`, `setFilters`, `seedRng`, the partial loop, the adjustment, `tearDownTestCase`, and `testCaseEnded` run in the same order and with the same data as today. The order of these calls is the same as today. The spike (§13) confirmed identical XML output for the omitted option and `0` apart from the random seed.

## 5. Separating Diagnostics from Final Totals

- Superseded attempts are reported live (E-8): assertions, sections, messages, benchmarks, partial events, and `testCaseAttemptEnded` with that attempt's totals and output.
- Then the run-wide assertion counters are restored to the snapshot taken at the attempt start (D2). Consequences: `m_totals.assertions`, `TestRunStats`, the session's summed totals, the exit code, and `aborting()` no longer contain the superseded attempt (T-2, AB-2). `m_totals.testCases` is only incremented once per logical test case, as today (T-1).
- Restoring happens on the runner thread after the test body has returned (C15). With `CATCH_CONFIG_THREAD_SAFE_ASSERTIONS`, each atomic counter is stored individually; without it, the `Counts` value is assigned.
- `testCaseEnded` totals are the final attempt's totals (T-2), its output is all attempts (C4), and new fields describe attempts and flakiness (E-6).

## 6. Reporter API and Compatibility

### 6.1 New public types and events (D3, D4)

In `catch2/interfaces/catch_interfaces_reporter.hpp`:

```cpp
struct TestCaseAttemptInfo {
    TestCaseInfo const* testInfo;
    std::uint64_t attemptNumber;   // one-based
    std::uint64_t maxAttempts;     // N + 1
};

struct TestCaseAttemptStats {
    TestCaseInfo const* testInfo;
    std::uint64_t attemptNumber;
    std::uint64_t maxAttempts;
    Totals totals;                 // this attempt only, Catch2's classification
    std::string stdOut;            // this attempt only
    std::string stdErr;
    bool aborting;
    bool isFinal;                  // false: a retry follows
};

struct TestCaseStats {
    // existing members and constructor unchanged
    std::uint64_t attemptCount = 1;
    std::uint64_t maxAttempts = 1;
    bool isFlaky = false;
};

class IEventListener {
    // existing pure virtuals unchanged
    //! Called before every attempt when --retry-failed > 0
    virtual void testCaseAttemptStarting( TestCaseAttemptInfo const& attemptInfo );
    //! Called after every attempt when --retry-failed > 0
    virtual void testCaseAttemptEnded( TestCaseAttemptStats const& attemptStats );
};
```

- Both events are non-pure virtuals with empty bodies in `catch_interfaces_reporter.cpp`, so every existing reporter and listener compiles unchanged (CO-2, E-9). `EventListenerBase`, `StreamingReporterBase`, and `ReporterBase` inherit the no-op.
- `MultiReporter` overrides both and forwards to listeners first, then reporters, like every other event (E-9).
- New `TestCaseStats` members use default member initializers; the 5-argument constructor is unchanged, so code that builds `TestCaseStats` keeps today's meaning (CO-3).
- Nesting and numbering follow §5.1 of the specification: inside `testCaseStarting`/`testCaseEnded`, enclosing partial events, never emitted with `N = 0` (C1).

### 6.2 Configuration (D5)

- `ConfigData::retryFailed` (`unsigned int`, default 0); `Config::retryFailed()` returns it.
- `IConfig::retryFailed()` is a non-pure virtual returning 0, defined in `catch_interfaces_config.cpp` (CLI-6, CO-2).
- `makeCommandLineParser`: `Opt( setRetryFailed, "retries" )["--retry-failed"]( "number of times to retry a failed test case after its first attempt (default: 0)" )`. `setRetryFailed` uses `parseUInt` and reports `"Could not parse '<value>' as retry count"` like `--shard-count` (CLI-1..CLI-5, C12).

### 6.3 Cumulative reporters (D6)

`CumulativeReporterBase` keeps one section tree per attempt:

- `testCaseAttemptEnded` with `isFinal == false` moves the current root section into a superseded-attempt list together with the attempt stats, and resets the root and deepest-section pointers, so the next attempt builds a fresh tree (S-8).
- `TestCaseNode` becomes a struct derived from `Node<TestCaseStats, SectionNode>` with one extra member, `std::vector<Detail::unique_ptr<TestCaseAttemptNode>> supersededAttempts`; `TestCaseAttemptNode` holds `TestCaseAttemptStats` and the attempt's root `SectionNode`. `children` still holds exactly the final attempt's root, so existing cumulative reporters that read `children.front()` see the final attempt.
- With `N = 0`, no attempt event arrives and the tree is built exactly as today.

## 7. Built-in Reporter Changes

All changes apply only when attempt events arrive (`N ≥ 1`); behaviour with `N = 0` is unchanged (CO-1). Output only changes when a retry happens, except for the structural fields of XML and JSON (C1, spec §5.2).

| Reporter | Change | Spec |
| --- | --- | --- |
| console | Track the current attempt. When an attempt ends with `isFinal == false`, print `Attempt k of M failed; retrying test case '<name>'`. Failures printed during attempt `k ≥ 2` get `(attempt k of M)` in the lazily printed test-case header. At `testCaseEnded` with `attemptCount > 1`: `Test case '<name>' passed on attempt k of M (flaky)` or `Test case '<name>' failed after k of M attempts`. | §5.2 console, AC-23, D14 |
| compact | Same three messages in compact one-line form. | §5.2 compact, D14 |
| XML | `testCaseAttemptStarting` opens `<Attempt number="k" maxAttempts="M">`; `testCaseAttemptEnded` writes `<AttemptResult success=".." skips=".." final=".."/>` and closes it, so the attempt's sections and assertions nest inside. `OverallResult` gains `attempts`, `maxAttempts`, and `flaky` attributes when `maxAttempts > 1`. `xml-format-version` unchanged. | §5.2 XML, AC-24, AC-25 |
| JSON | Each partial-run object gains `"attempt": k` when `maxAttempts > 1`. After the test-case `totals`, a new `"attempts"` object: `{"used", "max", "flaky", "results": [{"attempt", "final", "totals": {"assertions": {...}}}]}`, built from stored attempt stats. Format `version` unchanged. | §5.2 JSON, AC-24, AC-25 |
| JUnit | Final attempt written as today (`children.front()`). For each superseded attempt, its failures are rendered with the existing failure text format into a block `Attempt k of M failed:` that is prepended to the `<system-out>` of the first `<testcase>` element of that test case; if the final attempt emits no `<testcase>` element, the root one is emitted to hold the block (D8). Suite `failures`/`tests`/`skipped` come from the restored run totals; the reporter's own `unexpectedExceptions` counter (`catch_reporter_junit.cpp:113-117`, used for `errors` and subtracted for `failures` at `:136-137`) is counted per attempt and the counts of superseded attempts are dropped, otherwise `failures` could underflow for a flaky pass whose earlier attempt threw. | §5.2 JUnit, C8, AC-25 |
| SonarQube | Final attempt written as today. Superseded failures are written as XML comments `<!-- Attempt k of M failed: ... -->` before the test case's elements, with `--` sanitized because `XmlWriter::writeComment` does not escape it (D9). | §5.2 SonarQube, C8 |
| TeamCity | When `maxAttempts > 1`, each failure/ignore message is rendered to a string at `assertionEnded` (it depends on the section stack at that moment) and held until `testCaseAttemptEnded`: final attempt → written unchanged; superseded → written as `##teamcity[testStdErr ...]` with an `Attempt k of M failed:` prefix, a message the reporter already writes inside a test (D10). | §5.2 TeamCity, C8 |
| TAP | When `maxAttempts > 1`, copies of the attempt's `AssertionStats` are kept after forcing expression expansion. At attempt end: final → printed through the normal printer and colour as numbered test points, byte-identical to today; superseded → printed colour-free as `# ` diagnostic lines without consuming test-point numbers. The closing `1..N` plan uses run totals, which exclude superseded attempts (D10). | §5.2 TAP, C8 |
| Automake | No change: it already writes one line from the final `testCaseEnded` totals. | §5.2 Automake |

## 8. Abort Interaction

- The partial-run loop still stops when `aborting()` becomes true (existing behaviour). The attempt is then classified, `aborting()` blocks the retry, `testCaseAttemptEnded` reports `aborting = true, isFinal = true`, and `testCaseEnded` follows. `TestGroup::execute` then skips the remaining tests with `skipTest`, unchanged (AB-1, E-7).
- Restoring counters after a superseded attempt keeps its failures out of the abort count (AB-2). The unexpected-pass adjustment never touches the counters, so such an attempt is retried under `--abort`, as Catch2 today does not abort on it (AB-3, C14, AC-36).
- Fatal errors: when an attempt is active and `N ≥ 1`, `handleFatalErrorCondition` emits `testCaseAttemptEnded` (current attempt, `isFinal = true`, the same one-failure totals it already reports) after its existing section clean-up and implicit-section `sectionEnded`, and before its existing `testCaseEnded` and `testRunEnded` (`catch_run_context.cpp:697-727`). This order keeps the XML writer's element stack consistent (E-7, C10, D15). The existing fatal path does not end the open partial run; that pre-existing behaviour is left unchanged.

## 9. Affected Files and Symbols

| File | Change |
| --- | --- |
| `src/catch2/catch_config.hpp`, `.cpp` | `ConfigData::retryFailed`; `Config::retryFailed()` |
| `src/catch2/interfaces/catch_interfaces_config.hpp`, `.cpp` | `IConfig::retryFailed()` non-pure, returns 0 |
| `src/catch2/internal/catch_commandline.cpp` | `setRetryFailed` lambda and `--retry-failed` option |
| `src/catch2/interfaces/catch_interfaces_reporter.hpp`, `.cpp` | `TestCaseAttemptInfo`, `TestCaseAttemptStats`, `TestCaseStats` fields, two non-pure events |
| `src/catch2/internal/catch_run_context.hpp`, `.cpp` | Attempt loop in `runTest`; counter snapshot/restore helpers; current-attempt members for the fatal path |
| `src/catch2/reporters/catch_reporter_multi.hpp`, `.cpp` | Forward both events |
| `src/catch2/reporters/catch_reporter_cumulative_base.hpp`, `.cpp` | Attempt trees, `TestCaseNode` struct, `TestCaseAttemptNode` |
| `src/catch2/reporters/catch_reporter_{console,compact,xml,json,junit,sonarqube,teamcity,tap}.hpp`, `.cpp` | §7 |
| `tests/SelfTest/IntrospectiveTests/CmdLine.tests.cpp` | Parsing and configuration tests |
| `tests/SelfTest/IntrospectiveTests/Reporters.tests.cpp` | Multi-reporter forwarding order including attempt events |
| `tests/ExtraTests/X96-RetryFailed.cpp`, `tests/ExtraTests/CMakeLists.txt` | Retry scenarios executable, recording reporter, legacy reporter/listener |
| `tests/TestScripts/testRetryFailed.py` | Scenario runner and output parsers |
| `tests/CMakeLists.txt` | Help-text and CLI-error CTests |
| `docs/command-line.md`, `docs/reporter-events.md`, `docs/reporters.md`, `docs/test-fixtures.md` | Documentation (§11) |
| `extras/catch_amalgamated.hpp`, `.cpp` | Regenerated |
| `IMPLEMENTATION_NOTES.md` | New, repository root |

No new source or header files are added under `src/`, so `src/CMakeLists.txt`, `meson.build`, and the convenience headers need no change (M §10).

## 10. Test Strategy

### 10.1 Test assets

| Asset | Layer | Purpose |
| --- | --- | --- |
| `CmdLine.tests.cpp` additions | SelfTest unit | Default, accepted values incl. `4294967295`, rejected values, `Config`/`IConfig` exposure |
| CTest `RetryFailed::Help` | Process | `SelfTest -h` output contains the option and its meaning |
| CTests `RetryFailed::CliError::*` | Process | `--retry-failed` with no value, `-1`, `abc`, `1.5`, `4294967296`, twice: `Error(s) in input` on stderr, no test output |
| `X96-RetryFailed.cpp` | Extra executable | Hidden counting-fixture tests (counters in statics, one process per scenario), a `retry-recorder` reporter that prints every test-case, attempt, and partial event with numbers, totals, flags, and outputs, enforcing nesting with `CATCH_ENFORCE`; a reporter and a listener written against the existing API only |
| `testRetryFailed.py` | Python (label `uses-python`) | Runs scenarios, compares recorder output, exit codes, and attempt counts; parses JSON with `json`, XML/JUnit/SonarQube with `xml.etree`; checks console, compact, TAP, TeamCity markers |
| Approval baselines | Existing | Unchanged: no SelfTest test uses retries, proving zero-retry output for all built-in reporters (CO-1) |
| `Reporters.tests.cpp` addition | SelfTest unit | Multi-reporter forwards attempt events to listeners then reporters |
| Crash scenario | Extra executable, label `uses-signals` | Fatal error with `N = 2` and with JUnit: one attempt, balanced attempt end, reporter does not crash |

Retry scenarios live in `ExtraTests`, not in `SelfTest`, so approval baselines do not change (D12, CO-1).

### 10.2 Scenario coverage

| Spec scenarios | Test |
| --- | --- |
| AC-01, AC-02, AC-05 (config part) | `CmdLine.tests.cpp` |
| AC-03 | `RetryFailed::CliError::*` |
| AC-04 | `RetryFailed::Help` |
| AC-05 (events), AC-06 – AC-22, AC-26 – AC-29, AC-31, AC-34, AC-36 | `testRetryFailed.py` scenarios on `X96-RetryFailed` |
| AC-23, AC-24, AC-25 | `testRetryFailed.py` reporter scenarios (console, compact, XML, JSON, JUnit, SonarQube, TAP, TeamCity) with real parsers |
| AC-30 | Existing approval tests unchanged; `testRetryFailed.py` compares recorder, XML, and JSON output for option omitted vs `0` with fixed seed and order; existing `PartialTestCaseEvents` test unchanged |
| AC-32 | Legacy reporter and listener in `X96-RetryFailed` compile and run with `N = 2` |
| AC-33 | `Reporters.tests.cpp` addition and a multi-reporter scenario |
| AC-35 | Crash scenario (platform-guarded like `X36`) |

### 10.3 Validation runs

Phase 6 per task: build `basic-tests` and run the focused tests; Phase 8: full `basic-tests` and `all-tests` suites, approval tests, amalgamated build test, all in `C:\build\Course_AI\catch2\` (allowed by the contract's permission boundary), compared with runs 5 and 6 of the baseline.

## 11. Documentation and Generated Files

- `docs/command-line.md`: new `--retry-failed` section and table-of-contents entry: syntax, default, `N` as retries after attempt 1, examples for 0, 1, several, final-result and flaky semantics, attempts versus partial runs, fresh state, the test-owned-state limitation, special tags, abort options.
- `docs/reporter-events.md`: `testCaseAttempt` events with lifecycle, nesting, numbering, `N = 0` behaviour, compatibility; new `TestCaseStats` fields. Version marker `Introduced in Catch2 X.Y.Z`, the placeholder Catch2's release script replaces (`tools/scripts/releaseCommon.py:114-121`).
- `docs/reporters.md`: how built-in reporters show retries (XML/JSON fields, JUnit `system-out`, SonarQube comments, TeamCity, TAP).
- `docs/test-fixtures.md`: persistent fixtures are recreated per attempt.
- `extras/catch_amalgamated.*` regenerated with `tools/scripts/generateAmalgamatedFiles.py`; expected diff limited to the changed sources plus the `Generated:` line.
- `IMPLEMENTATION_NOTES.md` with the nine items required by the assignment.

## 12. Risks and Rollback

| Risk | Mitigation | Detection |
| --- | --- | --- |
| Zero-retry behaviour changes | All new behaviour behind `N ≥ 1` and attempt events; no SelfTest test uses retries | Approval tests, existing CTests, omitted-vs-`0` comparison |
| Counter restore incomplete (thread-safe build) | One helper used in one place; covers all four counters | Totals and exit-code scenarios; Phase 8 review of the thread-safe branch |
| Cumulative tree handling breaks JUnit/SonarQube (including the crash path) | Final attempt stays in `children.front()`; superseded attempts separate | JUnit/SonarQube parser scenarios; crash scenario with JUnit |
| Lazy expression expansion and colour in held-back TAP/TeamCity output | TeamCity: render strings at `assertionEnded`; TAP: copy `AssertionStats` after forced expansion and print at attempt end through the normal colour path | TAP/TeamCity scenarios, including `--colour-mode ansi` for TAP. Residual risk shared with `CumulativeReporterBase`: an expansion that yields an empty string is not cached and would be recomputed; Catch2's expansions of failed expressions are never empty in practice |
| With `N ≥ 1`, TAP lines are written at the end of each attempt | Documented limitation: TAP does not capture test output, so lines can interleave differently with text the test prints directly; the TAP stream itself is unchanged when no retry happens | TAP scenario comparing omitted vs `N = 1` without retries |
| JUnit `unexpectedExceptions` counts superseded attempts (`failures = failed - errors` could underflow) | Count per attempt and drop superseded counts (§7) | JUnit scenario: exception in attempt 1, pass in attempt 2 → `errors="0" failures="0"` |
| XML comment text containing `--` | Sanitize before `writeComment` | SonarQube scenario with a `--` expression |
| Custom reporters relying on today's behaviour under retries | Events optional; legacy reporter scenario | AC-32 |
| Amalgamated files drift | Regenerate in the final task | `all-tests` amalgamated build test |

Rollback: every task lands as a separate local commit on `task/retry-failed`; any task can be reverted with `git revert`. Because the feature is inert at `N = 0`, a partial implementation never changes default behaviour.

## 13. Spike

A disposable spike patched `RunContext::runTest` in a scratch copy of the `v3.16.0` amalgamated sources (environment variable instead of a CLI option, no reporter events, non-thread-safe counters only) and was built with GCC 13 on Linux in the agent's scratch workspace, not with the MSVC toolchain of the baseline; it is not production code and was not copied anywhere. Results:

| Check | Result |
| --- | --- |
| Section restart (nested sections, fail in B on attempt 1) | Attempt 2 re-traversed `A1`, `A2`, `B`; final totals counted only attempt 2 |
| Generator restart (`GENERATE(1, 2, 3)`, fail on 3) | Attempt 2 yielded 1, 2, 3 again |
| Persistent fixture per attempt | Attempt 2 got a new instance (`ctor = 2`, one live instance, member reset) |
| RNG reseed per attempt | `random(0, 100000)` produced the same two values in both attempts |
| Always failing, `N = 2` | 3 attempts; `test cases: 1 failed; assertions: 1 failed`; exit 42 |
| `--abort`, failing test | 1 attempt; later test skipped |
| `--abort`, unexpected `[!shouldfail]` pass | 3 attempts; run continued (AC-36) |
| `--abortx 2 --retry-failed 1`, flaky then always-failing then passing | No abort; 3 test cases, 2 passed, 1 failed (AC-29) |
| Omitted option vs `0` | XML identical except the random seed attribute |

## 14. Requirement Coverage

| Spec | Design | Test |
| --- | --- | --- |
| CLI-1 – CLI-8 | §6.2, §3, D5, D13 | CmdLine tests, Help, CliError, AC-05 |
| R-1 – R-8 | §3, §4 | AC-06 – AC-12, AC-18, AC-19, AC-36 |
| S-1 – S-9 | §4, §6.3, D6, D7 | AC-13 – AC-17, AC-34 |
| E-1 – E-9 | §4, §6.1, §8, D3, D4 | AC-20 – AC-22, AC-32, AC-33, AC-35 |
| §5.2 reporters | §7, D8 – D11, D14 | AC-23 – AC-25 |
| T-1 – T-6 | §5 | AC-07 – AC-12, AC-26 |
| AB-1 – AB-3 | §8 | AC-28, AC-29, AC-36 |
| CO-1 – CO-7 | §4, §6, §10 | AC-30 – AC-34, approval tests |
| Documentation (spec §10) | §11, D16 | Phase 7 review |

## 15. Required Design Checks

| Check | Answer |
| --- | --- |
| Zero-retry path preserves events and statistics | §4 equivalence; no events at `N = 0`; spike and approval tests |
| Fresh tracker root and fixture lifecycle per retry | `startRun` + `setFilters`, prepare/tear-down per attempt (§4); spike |
| Earlier diagnostics observable without entering totals | Live events + `testCaseAttemptEnded`, then counter restore (§5) |
| No new pure virtual for custom reporters | Non-pure events with empty bodies (§6.1) |
| Partial-run events not reused as attempt events | Separate `testCaseAttempt*` events; part numbers continue (§6.1, C2) |
| Retry-limit arithmetic cannot overflow | `retriesUsed < N`; `maxAttempts` is `uint64_t(N) + 1` (§3, D13) |
| Abort reached mid-attempt | §8 |

## 16. Sources

All design facts come from the pinned Catch2 tag; per the reviewer's style decision, access dates are not recorded, and the commit pin identifies the version.

| Source (tag `v3.16.0`, commit `317ac1ed4c0bb6e6b91eafc817e05c488feffcb3`) | Why it matters |
| --- | --- |
| `https://github.com/catchorg/Catch2/blob/v3.16.0/src/catch2/internal/catch_run_context.cpp` | Attempt loop location, counters, abort, fatal path (§3–§5, §8) |
| `https://github.com/catchorg/Catch2/blob/v3.16.0/src/catch2/interfaces/catch_interfaces_reporter.hpp` | Event API and data structures (§6.1) |
| `https://github.com/catchorg/Catch2/blob/v3.16.0/src/catch2/reporters/` | Reporter bases and built-in reporters (§6.3, §7) |
| `https://github.com/catchorg/Catch2/blob/v3.16.0/src/catch2/internal/catch_commandline.cpp`, `catch_parse_numbers.cpp` | Option parsing pattern (§6.2) |
| `https://github.com/catchorg/Catch2/blob/v3.16.0/src/catch2/internal/catch_xmlwriter.cpp` | `writeComment` does not escape (§7 SonarQube) |
| `https://github.com/catchorg/Catch2/blob/v3.16.0/tools/scripts/releaseCommon.py` | `X.Y.Z` documentation placeholder (§11) |
| `https://github.com/catchorg/Catch2/blob/v3.16.0/tests/ExtraTests/` | Extra-test and crash-test patterns (§10) |

## Gate Status

| Gate | Status |
| --- | --- |
| All critical requirements map to a design element and a planned test | ✅ §14 |
| Public API changes are justified and have a compatibility story | ✅ §6, D3 – D6 |
| Risks are explicit, especially reporter baselines and totals accounting | ✅ §12 |
| The human reviewer approves the plan before production edits begin | ✅ Approved |
