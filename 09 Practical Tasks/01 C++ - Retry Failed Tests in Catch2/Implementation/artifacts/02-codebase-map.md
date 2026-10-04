# Phase 2 Codebase Map

Status: Complete — accepted by the human reviewer
Contract: [00-task-contract.md](00-task-contract.md) · Baseline: [01-baseline.md](01-baseline.md)

This map traces how Catch2 `v3.16.0` executes and reports one selected test case. It records confirmed facts with source references, separates open questions, and names the smallest seams the future plan can use. It does not choose a design.

References use `path:line` relative to the Catch2 root at commit `317ac1ed4c0bb6e6b91eafc817e05c488feffcb3`; the same lines are at `https://github.com/catchorg/Catch2/blob/v3.16.0/<path>#L<line>`. The exploration read an unmodified copy of the tag; no file in `workspace/Catch2` was changed.

## 1. Configuration: CLI to `IConfig`

| Step | Fact | Reference |
| --- | --- | --- |
| Parser | `makeCommandLineParser( ConfigData& )` builds one Clara parser; every option writes into `ConfigData` | `src/catch2/internal/catch_commandline.cpp:24`, options `:262-375` |
| Unsigned-value pattern | Options that need validation use a lambda with `parseUInt` and return `ParserResult::runtimeError(...)` on failure (`--shard-count`, `--shard-index`, `--benchmark-samples`) | `catch_commandline.cpp:185-219` |
| `parseUInt` | Trims input; rejects empty input, a leading `-`, trailing characters (so `1.5` and `abc` fail), and values above `unsigned int` max | `src/catch2/internal/catch_parse_numbers.cpp:18-50` |
| Abort options | `-a/--abort` sets `abortAfter = 1`; `-x/--abortx` takes a plain `int`; Clara rejects non-integers, but there is no range check | `catch_commandline.cpp:283-288` |
| Storage | `ConfigData` is a plain struct of defaults (`abortAfter = -1`, `shardCount = 1`, ...) | `src/catch2/catch_config.hpp:48-97` |
| Exposure | `Config` implements `IConfig` and returns `m_data` fields (e.g. `Config::abortAfter`) | `catch_config.hpp:99-151`, `src/catch2/catch_config.cpp:213-223` |
| Abstraction | Every `IConfig` member is pure virtual; `Config` is the only implementation in `src/`, `tests/`, and `examples/` | `src/catch2/interfaces/catch_interfaces_config.hpp:67-102` |
| Error path | `Session::applyCommandLine` prints `Error(s) in input:` plus the Clara message to stderr and returns `UnspecifiedErrorExitCode`; `Session::run(argc, argv)` runs tests only when that call returns 0, so no reporter is created and no test runs | `src/catch2/catch_session.cpp:244-270`, `src/catch2/catch_session.hpp:44-51` |
| Help | `showHelp()` prints the Clara-generated option list, so the help text is the string passed to `Opt(...)( "..." )` | `Session::showHelp`, `catch_session.cpp:230`, called at `:264-265`; existing `VersionCheck` CTest runs `SelfTest -h` (`tests/CMakeLists.txt:417`) |

Consequence for later phases: an `IConfig` member added as pure virtual would break any out-of-tree `IConfig` implementation. A non-pure virtual with a default value keeps such code compiling (it changes the vtable, which Catch2 does not treat as stable ABI).

## 2. Lifecycle of One Selected Test Case

### 2.1 Session and selection

| Step | Fact | Reference |
| --- | --- | --- |
| Selection | `TestGroup` collects matching tests (hidden tests only through a positive spec), then applies `createShard` before anything runs | `catch_session.cpp:81-106` |
| Loop | `TestGroup::execute` calls `RunContext::runTest` per test and sums the returned `Totals`; once `RunContext::aborting()` is true, remaining tests get `skipTest` instead | `catch_session.cpp:109-126` |
| Exit status | Computed from the summed `Totals`: no tests → `NoTestsRunExitCode`, all skipped → `AllTestsSkippedExitCode`, `totals.assertions.failed > 0` → `TestFailureExitCode`, else `0` | `catch_session.cpp:393-416` |
| Listing | `list(...)` returns before `TestGroup` is created, so listing never executes tests | `catch_session.cpp:387-390` |

### 2.2 `RunContext::runTest` — the logical test-case boundary

`src/catch2/internal/catch_run_context.cpp:361-453`, in order:

1. Snapshot `prevTotals` from the running totals (`:362-363`).
2. `m_reporter->testCaseStarting(testInfo)` (`:366`).
3. `testCase.prepareTestCase()` (`:367`) — invoker hook, see §4.
4. `m_trackerContext.startRun()` creates a **new root tracker**; `setFilters(...)` applies `-c`/path filters to it (`:371-374`).
5. `seedRng(*m_config)` once per test case, deliberately before the first entry (`:376-407`).
6. Partial-run loop `do { ... } while (!m_testCaseTracker->isSuccessfullyCompleted() && !aborting())` (`:412-433`). Each iteration:
   - `startCycle()` and `SectionTracker::acquire` for the test-case tracker (`:413-414`);
   - `testCasePartialStarting(testInfo, testRuns)` (`:416`);
   - `runCurrentTest()` (`:420`, body below);
   - per-run stdout/stderr taken from the output redirect, buffers cleared, and appended to the test-case aggregate (`:421-425`);
   - `testCasePartialEnded(TestCaseStats(one-run delta, one-run output), testRuns)` (`:428-430`);
   - `++testRuns` (`:432`). `testRuns` is a per-test-case counter starting at 0.
7. `deltaTotals = m_totals.delta(prevTotals)` classifies the whole test case (`:435`; `Totals::delta` in `src/catch2/catch_totals.cpp:52-63`).
8. `[!shouldfail]` unexpected pass: if `expectedToFail()` and the case counted as passed, move it to failed and add one failed assertion **to `deltaTotals` only** (`:436-440`).
9. `m_totals.testCases += deltaTotals.testCases` (`:441`). Running assertion totals are not adjusted by step 8.
10. `testCase.tearDownTestCase()` (`:442`).
11. `m_reporter->testCaseEnded(TestCaseStats(deltaTotals, aggregated output, aborting()))` (`:443-447`).
12. Return `deltaTotals` to the session (`:452`).

### 2.3 `RunContext::runCurrentTest` — one partial run

`catch_run_context.cpp:751-796`:

- Emits `sectionStarting` for an implicit section named after the test case (`:752-754`).
- Activates output redirect, starts the timer, and calls `invokeActiveTestCase()` under a `FatalConditionHandlerGuard` (`:762-768`, `:798-809`).
- Catches `TestFailureException` (a `REQUIRE`-style stop or an abort), `TestSkipException` (`SKIP`), and any other exception, which becomes a `ThrewException` assertion via `handleUnexpectedInflightException` (`:769-782`).
- Closes the test-case tracker, ends unfinished sections, clears unscoped messages, and emits `sectionEnded` for the implicit section (`:787-795`).

### 2.4 Attempt boundary versus partial-run boundary

```text
testRunStarting                                   RunContext ctor   (:346)
  testCaseStarting                                runTest           (:366)   <- logical test case
    prepareTestCase                               invoker           (:367)
    startRun + setFilters, seedRng                trackers / RNG    (:371-407)
    repeat until root tracker complete or aborting:
      testCasePartialStarting(n)                  (:416)            <- partial run n
        sectionStarting(<test case>)              (:754)
          sectionStarting/Ended, assertionStarting/Ended ...
        sectionEnded(<test case>)                 (:795)
      testCasePartialEnded(n)                     (:430)
    tearDownTestCase                              invoker           (:442)
  testCaseEnded                                   (:443)
  skipTest                                        only after abort  (catch_session.cpp:115)
testRunEnded                                      RunContext dtor   (:358)
```

Today one logical test case equals one complete traversal. A partial run is one entry into the body. The future attempt boundary has to sit between the two: it must enclose a complete partial-run loop (steps 4–6 plus the per-attempt classification) and stay inside `testCaseStarting`/`testCaseEnded`. Nothing in the current code represents an attempt.

## 3. Sections and Generators

| Fact | Reference |
| --- | --- |
| `TrackerContext::startRun()` replaces the root tracker with a new `SectionTracker` and resets the current tracker; the old tree, including every child section and generator tracker, is destroyed with it | `src/catch2/internal/catch_test_case_tracker.cpp:86-95` |
| `startCycle()` only rewinds the current tracker to the root for the next partial run; it keeps the tree | `src/catch2/internal/catch_test_case_tracker.hpp:216-219` |
| Section trackers are found or created on each `SECTION` entry by name and location; a section runs only if its tracker opens | `RunContext::sectionStarted`, `catch_run_context.cpp:504-528`; `SectionTracker::acquire` and `tryOpen`, `catch_test_case_tracker.cpp:226-255` |
| Tracker states: `NotStarted`, `Executing`, `ExecutingChildren`, `NeedsAnotherRun`, `CompletedSuccessfully`, `Failed`; `close()` completes a tracker, `fail()` marks it failed and asks the parent for another run | `catch_test_case_tracker.hpp:88-95`, `catch_test_case_tracker.cpp:125-160` |
| A section left by an exception goes through `sectionEndedEarly` and is closed later by `handleUnfinishedSections` | `catch_run_context.cpp:609-618`, `:811-821` |
| Generator trackers own their generator (`GeneratorBasePtr`). They are created as children of the current tracker the first time `GENERATE` is reached, then looked up on later partial runs | `GeneratorTracker`, `catch_run_context.cpp:38-201`; `acquireGeneratorTracker` / `createGeneratorTracker`, `:529-575` |
| A generator advances (`countedNext()`) in `GeneratorTracker::close()` when its subtree completed, and resets its children when it moves on | `catch_run_context.cpp:129-193` |
| Path and generator filters are read from the root tracker's filter pointer and applied when trackers are created | `catch_run_context.cpp:55-84`; `setFilters` at `:373-374` |
| `random(...)` generators take their seed from the shared RNG when created (`Detail::getSeed()` returns `sharedRng()()`); `runTest` reseeds that RNG once per test case before the first entry, and its comment explains why reseeding on every entry would give equal sequences | `src/catch2/generators/catch_generators_random.hpp:90-102`, `src/catch2/generators/catch_generators_random.cpp:17`; `catch_run_context.cpp:376-407` |

Consequence: a fresh traversal with fresh generator instances is obtained by calling `startRun()` and `setFilters(...)` again. Reseeding the RNG at the same point would make every attempt see the same random sequence as attempt 1 (an open question for Phase 3, §10).

## 4. Fixtures and the Test Invoker

| Invoker | Fixture lifetime today | Reference |
| --- | --- | --- |
| Free function (`TEST_CASE`) | No fixture | `TestInvokerAsFunction`, `src/catch2/internal/catch_test_registry.cpp:52-61` |
| `TestInvokerAsMethod<C>` (`TEST_CASE_METHOD`, `METHOD_AS_TEST_CASE`) | A new `C` on the stack for **every** `invoke()`, i.e. every partial run | `src/catch2/internal/catch_test_registry.hpp:31-41`; both macros call `makeTestInvoker` at `:165` and `:203` |
| `TestInvokerFixture<C>` (`TEST_CASE_PERSISTENT_FIXTURE`, since 3.7.0) | Created in `prepareTestCase()`, shared by all partial runs, destroyed in `tearDownTestCase()` | `catch_test_registry.hpp:51-72`; docs `docs/test-fixtures.md:89-95` |
| `ITestInvoker` defaults | `prepareTestCase` and `tearDownTestCase` are empty virtuals | `catch_test_registry.cpp:19-20`, `src/catch2/interfaces/catch_interfaces_test_invoker.hpp:15-17` |

`runTest` calls prepare once before the partial-run loop and tear-down once after it (`catch_run_context.cpp:367`, `:442`). For persistent fixtures, a fresh fixture per attempt therefore requires a prepare/tear-down pair per attempt; `TEST_CASE_METHOD` fixtures are already fresh per partial run.

## 5. Results, Special Tags, and Totals

| Topic | Fact | Reference |
| --- | --- | --- |
| Assertion counting | `assertionEnded` counts `Ok` as passed, `ExplicitSkip` as skipped, a failure as `failedButOk` when `okToFail()` (`[!mayfail]` or `[!shouldfail]`), otherwise failed | `catch_run_context.cpp:456-494` |
| Fast path | Passing assertions not reported to reporters only increment the counter | `assertionPassedFastPath`, `:730-736`; `handleExpr`, `:823-844` |
| Counter storage | Counts live in `Detail::AtomicCounts` (real atomics with `CATCH_CONFIG_THREAD_SAFE_ASSERTIONS`, plain `Counts` otherwise); `updateTotalsFromAtomics` copies them into `m_totals.assertions` | `src/catch2/internal/catch_thread_support.hpp:22-44`; `catch_run_context.cpp:738-745` |
| Test-case classification | `Totals::delta`: any failed assertion → failed; else any `failedButOk` → `failedButOk`; else any skipped → skipped; else passed | `src/catch2/catch_totals.cpp:52-63` |
| Tag parsing | `[!shouldfail]` → `ShouldFail`, `[!mayfail]` → `MayFail`; `okToFail()` is either; `expectedToFail()` is `ShouldFail` only | `src/catch2/catch_test_case_info.cpp:56-62`, `:208-212` |
| Unexpected pass | Applied once per test case after the loop, to `deltaTotals` only | `catch_run_context.cpp:436-440` |
| Skip | `SKIP` records an `ExplicitSkip` result and throws `TestSkipException`, caught in `runCurrentTest` | `catch_run_context.cpp:878-882`, `:771-772` |
| Missing assertions | With `-w NoAssertions`, an empty leaf section or test adds a failed assertion | `testForMissingAssertions`, `catch_run_context.cpp:577-587` |
| Run totals | `testRunEnded` receives `RunContext::m_totals` from the destructor, not the session's summed totals; for an unexpected `[!shouldfail]` pass the two differ in assertion counts, because only the session's totals include the failed assertion added in step 8 | `catch_run_context.cpp:356-359` vs `catch_session.cpp:112-113` |

Running totals are cumulative for the whole run. `AssertionStats` carries a copy of them (`catch_run_context.cpp:484`); among built-in reporters, the console reporter only checks whether that total is non-zero (`src/catch2/reporters/catch_reporter_console.cpp:139`).

## 6. Abort Handling

| Fact | Reference |
| --- | --- |
| `aborting()` is `m_atomicAssertionCount.failed >= m_abortAfterXFailedAssertions`, using run-wide failed assertions; `failedButOk` does not count | `catch_run_context.cpp:747-749` |
| The threshold is cached from `IConfig::abortAfter()`; the default `-1` becomes the maximum `size_t`, so the run never aborts | `catch_run_context.cpp:340`, `catch_config.hpp:64` |
| Once aborting, every failing assertion throws (`shouldThrow = aborting() || normal disposition`), ending the partial run | `populateReaction`, `catch_run_context.cpp:907-911` |
| The partial-run loop stops when aborting; `TestCaseStats::aborting` is set; the session skips the remaining tests with `skipTest` | `catch_run_context.cpp:433`, `:447`; `catch_session.cpp:112-115` |

Consequence: failed assertions from an attempt that is later superseded would stay in the atomic counter and consume the abort budget of later test cases unless the counter is restored. With `--abort` (threshold 1), the first counted failure in any attempt reaches the threshold, so no retry can start after it (contract §In Scope).

## 7. Output Capture

| Fact | Reference |
| --- | --- |
| Redirection is enabled when any reporter sets `ReporterPreferences::shouldRedirectStdOut` | `catch_run_context.cpp:339`; `src/catch2/interfaces/catch_interfaces_reporter.hpp:115-130` |
| Output is captured only while the test body runs and is deactivated around reporter calls | `scopedActivate` at `catch_run_context.cpp:764`; `scopedDeactivate` at `:482`, `:520`, `:600` |
| Each partial run's output goes to `testCasePartialEnded`; the concatenation of all partial runs goes to `testCaseEnded` | `catch_run_context.cpp:421-430`, `:443-447` |
| `MultiReporter` writes captured output to the real stdout/stderr at `testCasePartialEnded` when some reporters capture and others do not | `src/catch2/reporters/catch_reporter_multi.cpp:138-152` |

## 8. Reporter Architecture

### 8.1 Interface and bases

| Component | Fact | Reference |
| --- | --- | --- |
| `IEventListener` | Every event is pure virtual, including `testCase*`, `testCasePartial*`, `skipTest`, and `fatalErrorEncountered`; `partNumber` is `uint64_t` | `src/catch2/interfaces/catch_interfaces_reporter.hpp:141-226` |
| `TestCaseStats` | Holds `testInfo`, `totals`, `stdOut`, `stdErr`, `aborting`; built with a 5-argument constructor | `catch_interfaces_reporter.hpp:88-100` |
| `ReporterBase` | Common base for built-in reporters; adds stream, colour, and listing support | `src/catch2/reporters/catch_reporter_common_base.hpp:29` |
| `StreamingReporterBase` | Empty defaults for partial events; tracks `currentTestCaseInfo` and a section stack | `src/catch2/reporters/catch_reporter_streaming_base.hpp:18-70` |
| `CumulativeReporterBase` | Builds one section tree per test case; `sectionStarting` **reuses** an existing child node with the same `SectionInfo` line, so repeated entries merge into one node and append their assertions; `testCaseEnded` moves the tree into the run node; output is attached to the deepest section | `src/catch2/reporters/catch_reporter_cumulative_base.hpp:62-151`, `catch_reporter_cumulative_base.cpp:68-145` |
| `EventListenerBase` | Empty defaults for all 22 `IEventListener` events; base for user listeners | `src/catch2/reporters/catch_reporter_event_listener.hpp:47-53`, `.cpp:33-37` |
| `MultiReporter` | Explicitly overrides and forwards each event to listeners first, then reporters; filters passing `assertionEnded` by preferences | `src/catch2/reporters/catch_reporter_multi.hpp:15-77`, `catch_reporter_multi.cpp:95-175` |

Compatibility note: a new pure virtual on `IEventListener` would break every reporter or listener that derives from it directly, including `MultiReporter` and test-only reporters. A new non-pure virtual with an empty body compiles everywhere, but `MultiReporter` must forward it explicitly or reporters behind it never see it.

### 8.2 Built-in reporters and where they decide pass or fail

| Reporter | Base | Behaviour relevant to retries | Reference |
| --- | --- | --- | --- |
| console | Streaming | Prints failing assertions as they arrive, with lazily printed test/section headers; totals from `TestRunStats` | `catch_reporter_console.cpp:422-462`, `:516-560`, `:631` |
| compact | Streaming | Prints failing assertions inline | `catch_reporter_compact.cpp:222-236` |
| XML | Streaming | Writes assertions inline inside `<TestCase>`; `<OverallResult success=...>` comes from `testCaseEnded` totals | `catch_reporter_xml.cpp:67-77`, `:190-203` |
| JSON | Streaming | One object per test case with a `runs` array of partial runs (`run-idx` = `partNumber`), each with path, captured output, and totals | `catch_reporter_json.cpp:174-255` |
| JUnit | Cumulative | Writes `<testcase>` per section node with `<failure>` children from stored assertions; suite counts from `TestRunStats` | `catch_reporter_junit.cpp:109-123`, `:131-215` |
| SonarQube | Cumulative | Writes failures from stored assertions | `catch_reporter_sonarqube.cpp:63-110` |
| TeamCity | Streaming | At a failing or skipped `assertionEnded`: `##teamcity[testIgnored ...]` for a skip or an `okToFail` test, otherwise `##teamcity[testFailed ...]` | `catch_reporter_teamcity.cpp:60-130`, `:140` |
| TAP | Streaming | Requests every assertion (`shouldReportAllAssertions = true`) and emits a numbered `ok`/`not ok` line for each | `catch_reporter_tap.hpp:20-21`, `catch_reporter_tap.cpp:207-215` |
| Automake | Streaming | Emits one `:test-result:` line per test case at `testCaseEnded`: `SKIP`, `PASS`, `XFAIL`, or `FAIL` from the final totals | `catch_reporter_automake.cpp:17-30` |

Consequence: reporters that judge a test case from its final `TestCaseStats` (XML `OverallResult`, Automake, JSON totals) follow the final outcome automatically. Reporters that emit failures as they happen (TeamCity, TAP, console, compact) or that derive failures from the merged section tree (JUnit, SonarQube) would show a flaky pass as failed unless attempt information reaches them.

## 9. Test Infrastructure

| Layer | What it gives | Reference |
| --- | --- | --- |
| CLI unit tests | `makeCommandLineParser(ConfigData&)` driven from `SelfTest`, checking `ConfigData` fields and parse failures | `tests/SelfTest/IntrospectiveTests/CmdLine.tests.cpp:30-43`, `:189-257`, `:353-358` |
| Event-order listener | `ValidatingTestListener`, registered in every `SelfTest` run, enforces nesting and requires `partNumber` to start at 0 and increase by 1 within a test case | `tests/SelfTest/TestRegistrations.cpp:33-181` (part numbers at `:66-82`, `:117-126`) |
| Multi-reporter order | `"Multireporter calls reporters and listeners in correct order"` | `tests/SelfTest/IntrospectiveTests/Reporters.tests.cpp:198` |
| Event-sequence executables | `ExtraTests` build small executables with a custom reporter; a Python script compares the printed event sequence (pattern: `X21-PartialTestCaseEvents.cpp` + `testPartialTestCaseEvent.py`) | `tests/ExtraTests/X21-PartialTestCaseEvents.cpp`, `tests/ExtraTests/CMakeLists.txt:252-261`, `tests/TestScripts/testPartialTestCaseEvent.py` |
| Exit codes and output regexes | CTest entries run `SelfTest` or an extra executable with arguments and check `PASS_REGULAR_EXPRESSION`, `FAIL_REGULAR_EXPRESSION`, or `WILL_FAIL` | `tests/CMakeLists.txt:173-737`, e.g. `:414`, `:476-528`; `tests/ExtraTests/CMakeLists.txt` |
| Approval tests | `tools/scripts/approvalTests.py` runs `SelfTest` 11 times with `"~[!nonportable]~[!benchmark]~[approvals] *"`, `--order lex`, and `--rng-seed 1`, producing 19 outputs that it compares with `tests/SelfTest/Baselines/*.approved.txt` | `tests/CMakeLists.txt:395-412`; `tools/scripts/approvalTests.py:205-240` |
| Hidden tests in approvals | A positive pattern such as `*` also selects hidden (`[.]`) tests, so new `SelfTest` cases appear in every baseline unless they carry an excluded tag | `src/catch2/catch_test_spec.cpp:62-75`; `docs/command-line.md:90-93` |
| Reporter filter/seed checks | Per-reporter CTest loops for console, compact, JUnit, SonarQube, TAP, XML, JSON | `tests/CMakeLists.txt:676-712` |

## 10. Build and Generated Files

- `extras/catch_amalgamated.hpp` is generated from `src/catch2/catch_all.hpp` and its includes; `extras/catch_amalgamated.cpp` concatenates every `src/catch2/**/*.cpp` (`tools/scripts/generateAmalgamatedFiles.py:15-18`, `:105-123`). Any change to a `src/catch2` header or source therefore changes the amalgamation; run 6 confirmed that regeneration on the unmodified tree changes only the `Generated:` line.
- An amalgamated build is tested by `ExtraTests` (`tests/ExtraTests/CMakeLists.txt:578-579`).
- New source files must be listed in `src/CMakeLists.txt` and `src/catch2/meson.build` (Bazel uses globs, `BUILD.bazel:98-102`); new public headers must also be reachable from the convenience headers checked by the `CheckConvenienceHeaders` CTest (`tests/CMakeLists.txt:467`).

## 11. Answers to the Phase 2 Questions

| # | Question | Answer (sections above) |
| --- | --- | --- |
| 1 | Where is CLI state parsed, stored, exposed? | `catch_commandline.cpp` → `ConfigData` → `Config` / `IConfig` (§1) |
| 2 | Where does one logical test case begin and end? | `RunContext::runTest`, between `testCaseStarting` and `testCaseEnded` (§2.2) |
| 3 | How do events nest? | Run ⊃ test case ⊃ partial run ⊃ implicit test-case section ⊃ sections ⊃ assertions (§2.4) |
| 4 | When are trackers created, advanced, completed, reset? | Created on first entry, advanced in `close()`, completed per traversal, reset only by `startRun()` (§3) |
| 5 | When are fixtures prepared and destroyed? | Persistent fixture per test case via prepare/tear-down; method fixtures per partial run (§4) |
| 6 | Where are special tags and skip applied? | Assertion counting, `Totals::delta`, and the unexpected-pass adjustment in `runTest` (§5) |
| 7 | How do assertion totals become test-case totals and the exit code? | Atomic counts → `m_totals` → `delta` → summed in `TestGroup::execute` → `runInternal` (§2.1, §5) |
| 8 | How do `--abort`/`--abortx` observe failures? | Run-wide failed counter compared in `aborting()`; checked in assertions, the partial loop, and the session loop (§6) |
| 9 | Which reporter paths need compatibility care? | `IEventListener` pure virtuals, `MultiReporter` forwarding, `CumulativeReporterBase` tree merging, streaming reporters that emit failures inline (§8) |
| 10 | How are reporter outputs tested? | Approval baselines, per-reporter CTest regexes, `ExtraTests` with Python scripts, `ValidatingTestListener` (§9) |
| 11 | Which headers require regenerated amalgamated output? | Any file under `src/catch2` (§10) |
| 12 | Which focused tests can prove behaviour without approval snapshots? | `CmdLine.tests.cpp` for parsing; `ExtraTests` executables with counting fixtures, a recording reporter, and exit-code or output checks; a CLI-error CTest on stderr (§9) |

## 12. Smallest Safe Seams

These are locations the plan can use, not decisions.

| Concern | Seam | Why it is small |
| --- | --- | --- |
| Option | One `Opt` in `makeCommandLineParser` with a `parseUInt`-style lambda; one `ConfigData` field; one `Config` getter; one non-pure `IConfig` virtual | Mirrors `--shard-index` and `--benchmark-samples` |
| Attempt loop | Inside `RunContext::runTest`, around steps 3–8, between `testCaseStarting` and `testCaseEnded` | Keeps one outer test-case pair and leaves the partial loop intact |
| Fresh state | `startRun()` + `setFilters()`, invoker prepare/tear-down, optional `seedRng`, output buffers, all per attempt | Existing calls, only moved into the loop |
| Per-attempt classification | Same `delta` + unexpected-pass logic, applied to the attempt's own totals | Reuses Catch2's classifier |
| Totals and abort budget | Snapshot the atomic counters before an attempt and restore them when the attempt is superseded | `aborting()` and run totals then ignore superseded attempts without new bookkeeping in the session |
| Reporter event | Non-pure virtual(s) on `IEventListener` with empty defaults, explicit forwarding in `MultiReporter` | Source-compatible for every existing reporter |
| Cumulative reporters | `CumulativeReporterBase` tree handling at attempt boundaries | One base serves JUnit and SonarQube |

## 13. Open Questions for Phase 3

1. Should `partNumber` continue across attempts or restart at 0? Restarting breaks the `partNumber` check in `ValidatingTestListener` (§9) unless an attempt event resets it; continuing keeps the listener valid but blurs per-attempt numbering.
2. Should the RNG be reseeded at the start of every attempt (identical random sequence per attempt) or only once per test case (different sequence on retry)?
3. What do reporters receive as the attempt's stats: a new struct, or `TestCaseStats` plus attempt fields? Adding fields to `TestCaseStats` changes its constructor.
4. What does `testCaseEnded` carry for stdout/stderr: the final attempt only or all attempts? JUnit and SonarQube attach it to the deepest section of the merged tree.
5. How should reporters that emit failures inline (TeamCity `testFailed`, TAP `not ok`, compact, console) present a failure that a later attempt supersedes?
6. Should `TestRunStats` totals and the session's summed totals both exclude superseded attempts? Today they already differ for unexpected `[!shouldfail]` passes (§5).
7. How does an attempt event pair stay balanced on the fatal-error path, where `handleFatalErrorCondition` emits `sectionEnded`, `testCaseEnded`, and `testRunEnded` itself (`catch_run_context.cpp:663-728`) before the process ends (POSIX: the handler restores the previous handlers and re-raises the signal, `src/catch2/internal/catch_fatal_condition_handler.cpp:191-204`)?
8. With `CATCH_CONFIG_THREAD_SAFE_ASSERTIONS`, is restoring the atomic counters at an attempt boundary safe? It is only safe if user threads from the test body have finished by then.
9. Where do deterministic retry tests live: `SelfTest` (affects approval baselines unless excluded by tag) or `ExtraTests` (separate executables, no baseline impact)?

## 14. Risks

| Risk | Impact | Reference |
| --- | --- | --- |
| Superseded failures left in atomic counters | Wrong final assertion totals, wrong exit code for flaky passes, abort budget consumed | §5, §6 |
| Cumulative tree merges sections from several attempts | JUnit/SonarQube show `<failure>` for a flaky pass | `catch_reporter_cumulative_base.cpp:68-95` |
| Persistent fixture reused across attempts | Fixture state leaks into retries | §4 |
| Not re-applying filters after `startRun()` | `-c`/path filters ignored on retries | `catch_run_context.cpp:371-374` |
| New pure virtuals on `IConfig` or `IEventListener` | Out-of-tree configs, reporters, and listeners stop compiling | §1, §8.1 |
| Event added but not forwarded by `MultiReporter` | Reporters behind the multi-reporter never see attempts | `catch_reporter_multi.cpp:95-175` |
| Retry tests added to `SelfTest` without tag exclusion | Unintended changes in all 19 approval baselines | §9 |
| Zero-retry path changed | Baseline event sequence or totals differ from `v3.16.0` | contract compatibility constraints |

## Gate Status

| Gate | Status |
| --- | --- |
| Every architectural statement used by the future plan has a source reference | ✅ Each fact above cites `path:line` in the pinned tag |
| Attempt boundaries and partial-run boundaries are clearly distinguished | ✅ §2.4 |
| The baseline event and totals flow is understandable end to end | ✅ §2, §5, §6 |
| No production code has been changed | ✅ Read-only analysis of an unmodified copy of the tag; `workspace/Catch2` untouched |
