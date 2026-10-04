# Design Decisions

Status: Approved by the human reviewer
Plan: [05-plan.md](05-plan.md) · Specification: [03-spec.md](03-spec.md) · Clarifications: [04-clarifications.md](04-clarifications.md)

Each decision records the context, the alternatives, the choice, and its consequences. "Reviewer" marks choices the human reviewer made; the others were approved together with the plan.

## D1. Attempt loop inside `RunContext::runTest`

- Context: one logical test case runs entirely in `runTest`; it owns the tracker context, counters, output redirect, and reporter (M §2.2).
- Alternatives: rerun from `TestGroup::execute`; a separate retry runner class; the attempt loop inside `runTest`.
- Choice: the loop inside `runTest`, around prepare, tracker reset, seeding, the partial-run loop, classification, and tear-down.
- Consequences: one outer `testCaseStarting`/`testCaseEnded` pair (E-1); no changes to the session; the zero-retry path is the same code with one iteration.

## D2. Restore assertion counters for superseded attempts

- Context: assertion counters are run-wide and drive totals, the exit code, and `--abort` (M §5, §6).
- Alternatives: attempt-local accumulators merged at the end; subtracting the attempt's counts afterwards; restoring a snapshot taken at the attempt start.
- Choice: snapshot at attempt start, restore when a retry follows. Restoring an exact snapshot cannot underflow and touches one place, while accumulators would change every assertion path including the fast path.
- Consequences: totals, `TestRunStats`, exit status, and the abort budget exclude superseded attempts (T-2, AB-2); diagnostics remain delivered live (E-8). Running totals inside individual assertion events can briefly include a superseded attempt (C6). In thread-safe builds the guarantee covers assertions made before the body returns (C15).

## D3. New reporter events as non-pure virtuals

- Context: every `IEventListener` member is pure virtual; a new pure virtual breaks every direct implementation (M §8.1).
- Alternatives: new pure virtuals; reusing `testCasePartial*` (forbidden by E-5); smuggling attempt data into `testCaseStarting`/`Ended`; non-pure virtuals with empty bodies.
- Choice: `testCaseAttemptStarting(TestCaseAttemptInfo const&)` and `testCaseAttemptEnded(TestCaseAttemptStats const&)` with empty default bodies; `MultiReporter` forwards both.
- Consequences: existing reporters and listeners compile and run unchanged (CO-2, AC-32); reporters opt in by overriding. The vtable layout changes, which Catch2 does not treat as stable ABI.

## D4. Attempt data structures and `TestCaseStats` fields

- Context: reporters need the one-based attempt number, `M`, the attempt's own totals and output, and whether a retry follows (E-3, E-4); `testCaseEnded` needs attempts used, `M`, and flaky (E-6).
- Alternatives: extend `TestCaseStats` constructor arguments; new structs plus defaulted fields; a side channel through the config.
- Choice: new `TestCaseAttemptInfo` and `TestCaseAttemptStats` structs; `TestCaseStats` gains `attemptCount = 1`, `maxAttempts = 1`, `isFlaky = false` with default member initializers and an unchanged constructor. `isFinal` alone expresses "a retry follows" (`!isFinal`).
- Consequences: code that constructs or reads `TestCaseStats` keeps today's meaning (CO-3).

## D5. Configuration and command line

- Context: the option must go through Catch2's normal CLI and configuration abstraction (CLI-1 – CLI-6).
- Choice: `ConfigData::retryFailed` (`unsigned int`, default 0), `Config::retryFailed()`, non-pure `IConfig::retryFailed()` returning 0, and an `Opt` using `parseUInt` like `--shard-count`. Help text: "number of times to retry a failed test case after its first attempt (default: 0)".
- Consequences: one number syntax across options (C12); custom `IConfig` implementations keep compiling and behave as `N = 0`.

## D6. Cumulative reporters keep one tree per attempt

- Context: `CumulativeReporterBase` merges repeated section entries into one tree, which would mix failures of all attempts (M §8.1, §14).
- Alternatives: leave merging as is (flaky pass shows failures in JUnit/SonarQube); store all attempts as extra `children` (breaks reporters that expect one child); a separate superseded-attempt list.
- Choice: at a non-final `testCaseAttemptEnded`, move the root section into `supersededAttempts` with the attempt stats and start a fresh tree. `TestCaseNode` becomes a struct derived from `Node<TestCaseStats, SectionNode>` that adds `supersededAttempts`; `children` still holds only the final attempt's root.
- Consequences: existing cumulative reporters see the final attempt as today; JUnit and SonarQube can render superseded attempts separately.

## D7. Fresh state per attempt

- Context: S-1 – S-7 and the spike (plan §13).
- Choice: per attempt, call `prepareTestCase`, `startRun` + `setFilters`, `seedRng`, run the partial loop, then `tearDownTestCase`; keep the part-number counter across attempts (C2); collect output per attempt and append to the test-case total (C4).
- Consequences: persistent fixtures are recreated per attempt (C9); generators and trackers are new objects; random values repeat (C3).

## D8. JUnit: superseded failures in `<system-out>` (reviewer)

- Alternatives: Maven Surefire `<flakyFailure>`/`<rerunFailure>` elements (needs an external schema the contract does not allow consulting, and strict JUnit validators may reject them); XML comments (invisible in CI tools); text in the standard `<system-out>` element.
- Choice: render each superseded attempt's failures with the existing failure text format into an `Attempt k of M failed:` block prepended to the `<system-out>` of the test case's first `<testcase>` element; emit the root `<testcase>` if needed to hold it.
- Consequences: CI tools show the diagnostics and do not count them as failures; the format stays standard JUnit. The reporter's run-level `unexpectedExceptions` counter must also ignore superseded attempts, because `failures` is computed as `failed - unexpectedExceptions` (`src/catch2/reporters/catch_reporter_junit.cpp:113-117`, `:136-137`).

## D9. SonarQube: superseded failures as XML comments

- Context: Catch2's SonarQube reporter writes only `testExecutions`, `file`, `testCase`, and inside it `failure`, `error`, or `skipped` (`src/catch2/reporters/catch_reporter_sonarqube.cpp:38-135`). The SonarQube schema cannot be consulted under the contract's network rules, so unknown elements are treated as an import risk.
- Choice: write `<!-- Attempt k of M failed: ... -->` comments before the test case's elements; replace `--` in the text because `XmlWriter::writeComment` does not escape (`src/catch2/internal/catch_xmlwriter.cpp:308-315`).
- Consequences: output stays parseable and Sonar counts only final failures; diagnostics are visible in the file.

## D10. TeamCity and TAP hold back the current attempt

- Context: both write failures at the moment of the assertion (M §8.2), before it is known whether the attempt will be superseded. TeamCity builds each message from the section stack at that moment (`printSectionHeader`, `src/catch2/reporters/catch_reporter_teamcity.cpp:60-130`, `:157`) and captures test stdout (`shouldRedirectStdOut = true`). TAP writes coloured text through the reporter's colour implementation (`catch_reporter_tap.cpp:131-177`) and does not capture test stdout.
- Choice, only when `maxAttempts > 1`:
  - TeamCity renders each message to a string at `assertionEnded` (no colour is involved) and keeps the strings until `testCaseAttemptEnded`. Final attempt: the strings are written unchanged. Superseded: the same text is written as `##teamcity[testStdErr ...]`, a message the reporter already writes inside a test, prefixed `Attempt k of M failed:`.
  - TAP stores a copy of each `AssertionStats` after forcing expression expansion, the technique `CumulativeReporterBase` uses (`catch_reporter_cumulative_base.cpp:99-118`; the expanded text is cached in `AssertionResultData::reconstructedExpression`, `src/catch2/catch_assertion_result.cpp:18-28`), together with the test name. Final attempt: the copies are printed at `testCaseAttemptEnded` through the normal printer, stream, and colour, so the bytes are the same as today. Superseded: each copy is printed through a colour-free printer into a string and written as `# ` diagnostic lines that consume no test-point numbers.
- Consequences: with `N = 0` nothing changes. With `N ≥ 1` the reporters' own output is byte-identical to today when no retry happens, but its lines appear at the end of each attempt instead of at each assertion. For TAP, which does not capture test output, this can change how TAP lines interleave with text the test writes directly to stdout; this is recorded as a limitation (plan §12). TeamCity captures test output, so its stream is unaffected.

## D11. XML and JSON structural shapes

- Choice (XML): `<Attempt number="k" maxAttempts="M">` around the attempt's sections and assertions, closed by `<AttemptResult success skips final/>`; `OverallResult` gains `attempts`, `maxAttempts`, `flaky` when `maxAttempts > 1`.
- Choice (JSON): `"attempt": k` in each partial-run object when `maxAttempts > 1`; an `"attempts"` object after the test case's `totals`: `used`, `max`, `flaky`, and `results` (attempt number, `final`, assertion totals).
- Consequences: format version numbers stay unchanged (C7); zero-retry output is byte-identical.

## D12. Retry tests live in `ExtraTests`

- Context: any new `SelfTest` case appears in all 19 approval outputs (M §9).
- Alternatives: `SelfTest` cases with excluded tags; a dedicated extra executable plus a Python scenario script.
- Choice: `tests/ExtraTests/X96-RetryFailed.cpp` with a recording reporter and legacy reporter/listener, driven by `tests/TestScripts/testRetryFailed.py`. CLI parsing and multi-reporter unit tests stay in `SelfTest` because they do not run tests; they carry the `[approvals]` tag, which `tools/scripts/approvalTests.py:213-228` excludes, as the existing "Parse rng seed in different formats" does.
- Consequences: approval baselines stay unchanged (CO-1); each scenario runs in a fresh process, so static counters make deterministic flaky fixtures.

## D13. Types and overflow safety

- Choice: `N` is `unsigned int`; `retriesUsed` and attempt numbers are `std::uint64_t`; the loop compares `retriesUsed < N`; `maxAttempts = static_cast<std::uint64_t>(N) + 1`.
- Consequences: `N = 4294967295` gives `maxAttempts = 4294967296` without overflow (CLI-8, AC-05).

## D14. Console and compact messages

- Choice: print only when a retry happens: `Attempt k of M failed; retrying test case '<name>'` after a superseded attempt; `(attempt k of M)` in the test-case header for failures in attempts `k ≥ 2`; `Test case '<name>' passed on attempt k of M (flaky)` or `Test case '<name>' failed after k of M attempts` at the end. Compact uses the same wording on one line.
- Consequences: no console change for `N ≥ 1` runs without retries; exact wording is fixed by Phase 6 tests.

## D15. Fatal-error path

- Choice: when `N ≥ 1` and an attempt is active, `handleFatalErrorCondition` emits `testCaseAttemptEnded` (`isFinal = true`) after its existing section clean-up and implicit-section `sectionEnded`, and before its existing `testCaseEnded` and `testRunEnded`, so reporters that nest elements (XML) close them in order. The existing unbalanced partial run on this path is left unchanged.
- Consequences: attempt events stay balanced as far as the existing fatal reporting goes (E-7, C10).

## D16. Documentation set and version marker

- Choice: update `docs/command-line.md`, `docs/reporter-events.md`, `docs/reporters.md`, `docs/test-fixtures.md`; mark new features `Introduced in Catch2 X.Y.Z`, the placeholder replaced by Catch2's release script (`tools/scripts/releaseCommon.py:114-121`).
- Consequences: documentation follows project conventions; the release version is filled in by the maintainers.
