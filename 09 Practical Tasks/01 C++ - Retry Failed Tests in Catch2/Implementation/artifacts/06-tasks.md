# Phase 5 Task List

Status: Approved by the human reviewer, including the working model
Plan: [05-plan.md](05-plan.md) · Decisions: [07-decisions.md](07-decisions.md) · Specification: [03-spec.md](03-spec.md)

This is the single authoritative task list for Phase 6. Tasks are ordered by dependency; each ends in behaviour that a test proves. Tests are written in the same task as the code they verify.

## Working Model

- **Where code is written.** Each task is developed and first tested in a scratch clone of the same commit (`317ac1ed…`, branch `task/retry-failed`) in the agent's workspace, built with CMake and GCC on Linux for fast feedback. Only the changed files are then copied into `workspace/Catch2` on the reviewer's machine; nothing else in the checkout is touched.
- **Authoritative validation.** The Windows toolchain recorded in [01-baseline.md](01-baseline.md) is authoritative. After the files are copied, the reviewer runs `scripts/phase6-validate.ps1` (task T00) for the task; its summary goes to `evidence/raw/phase6/<task>-run-NN-<preset>/` and the agent records the result under the task below.
- **Commits.** After a task passes on Windows, the reviewer creates one local commit in `workspace/Catch2` with the message the agent provides; the agent cannot run Git on the reviewer's machine. No push.
- **Warnings are errors.** The presets enable `CATCH_DEVELOPMENT_BUILD`, which turns on `-Werror` (GCC) and `/WX` (MSVC) (`CMakeLists.txt:15-25`, `CMake/CatchMiscFunctions.cmake:31-33`), so every task must compile warning-free with both compilers; code is never added before the task that uses it.
- **Evidence format.** Each task's evidence line records: the Linux focused and regression results, the Windows summary path under `evidence/raw/phase6/<task>-run-NN-<preset>/` with its result, and the commit hash in `workspace/Catch2`.
- **Done means:** focused tests pass on Linux and Windows, the nearest regression set passes on Windows, the diff contains only the task's files, and the evidence line is filled in.

## Dependency Graph

```text
T00 ──┐
T01 ──┼─► T03 ─► T04 ─► T05 ─┬─► T06 ─► T07
T02 ──┘                      ├─► T08
                             ├─► T09
                             ├─► T10 (needs T07 for its crash scenario)
                             └─► T11
T05 … T11 ─► T12 ─► T13 ─► T14
```

T00 is a prerequisite for the Windows evidence of every other task.

There is no cycle. T00, T01, and T02 touch disjoint files and can be done in any order. T08–T11 change separate reporter files but all add scenarios to `tests/TestScripts/testRetryFailed.py`, so they are done one after another.

## Tasks

### [x] T00 — Phase 6 validation script

- **Outcome:** one command builds a chosen preset — `basic-tests` into `C:\build\Course_AI\catch2\basic-test-build` or `all-tests` into `C:\build\Course_AI\catch2\debug-build` (needed for the extra tests, which only the larger presets build) — runs CTest with an optional `-R` filter followed by the full suite of that preset, checks `git status`, and writes a summary per task. It does not regenerate the amalgamated files, so they stay unchanged until T13.
- **Files:** `Implementation/scripts/phase6-validate.ps1` (course repository, not Catch2).
- **Depends on:** none.
- **Focused test:** run it on the unmodified branch for both presets: 82/82 and 145/145 tests, clean tree, summaries written to `evidence/raw/phase6/T00-run-NN-<preset>/`.
- **Evidence:** Linux smoke test of the script logic (`basic`, with and without a filter, scratch build root): configure and build exit 0, 0 warnings, focused 1/1 and full 81/81 passed (the Linux suite has 81 tests; the Windows suite has 82), clean tree. A first Windows run wrote its evidence one folder deeper than the review tooling can read (8 levels below the connected folder, limit 7), so the evidence layout was flattened to `evidence/raw/phase6/<task>-run-NN-<preset>/` and the Windows runs were repeated. Windows `T00-run-01-basic`: HEAD `317ac1ed…` on `task/retry-failed`, clean tree; configure and build exit 0 (no recompilation); **82/82 passed** (19.4 s); no `*.unapproved.txt`; clean after the run. Windows `T00-run-02-all`: same repository state; **145/145 passed** (12.2 s; 16 `uses-python`, 1 `uses-signals`); clean after the run. Both match baseline runs 5 and 6. Observations: an incremental build reports warnings only for recompiled files (run 6 had 4 `D9025` on a full build), and the CMake configuration tests reuse their own earlier builds (about 1.8 s each instead of about 100 s), so T13 must use fresh build directories. No Catch2 commit: T00 changes only the course repository.
- **Independent:** yes.

### [ ] T01 — `--retry-failed` option and configuration

- **Outcome:** `--retry-failed N` is parsed, validated, shown in help, stored in `ConfigData`, and readable through `IConfig`; invalid input fails through Catch2's normal error path before tests start.
- **Files / symbols:** `src/catch2/catch_config.hpp`/`.cpp` (`ConfigData::retryFailed`, `Config::retryFailed`), `src/catch2/interfaces/catch_interfaces_config.hpp`/`.cpp` (non-pure `IConfig::retryFailed`), `src/catch2/internal/catch_commandline.cpp` (`setRetryFailed`, `Opt`), `tests/SelfTest/IntrospectiveTests/CmdLine.tests.cpp`, `tests/CMakeLists.txt` (`RetryFailed::Help`, `RetryFailed::CliError::*`).
- **Depends on:** none.
- **Focused tests:** `SelfTest "[command-line]"` with new sections: default 0; `0`, `1`, `3`, `4294967295` accepted and visible through `Config` and `IConfig`; missing, `-1`, `abc`, `1.5`, `1e3`, `4294967296`, repeated option rejected. CTests: `RetryFailed::Help` (option and its meaning in `-h` output), `RetryFailed::CliError::*` (stderr `Error(s) in input`, no test output).
- **Covers:** CLI-1 – CLI-7; AC-01 – AC-04, AC-05 (configuration part).
- **Regression:** full `basic-tests`; approval tests unchanged.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** yes.

### [ ] T02 — Attempt reporting API (inert)

- **Outcome:** `TestCaseAttemptInfo`, `TestCaseAttemptStats`, the `TestCaseStats` fields, and the non-pure `testCaseAttemptStarting`/`testCaseAttemptEnded` events exist; `MultiReporter` forwards them in listener-then-reporter order; nothing emits them yet.
- **Files / symbols:** `src/catch2/interfaces/catch_interfaces_reporter.hpp`/`.cpp`, `src/catch2/reporters/catch_reporter_multi.hpp`/`.cpp`, `tests/SelfTest/IntrospectiveTests/Reporters.tests.cpp`.
- **Depends on:** none.
- **Focused tests:** extend "Multireporter calls reporters and listeners in correct order" with the two attempt events; a test that a reporter deriving directly from `IEventListener` without the new overrides compiles and receives the default no-op.
- **Covers:** E-9, CO-2, CO-3 (types); AC-33 (unit part).
- **Regression:** full `basic-tests`; approval tests unchanged.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** yes.

### [ ] T03 — Retry test harness at zero retries

- **Outcome:** an extra test executable and scenario script exist and prove the zero-retry baseline before any runner change.
- **Files:** `tests/ExtraTests/X96-RetryFailed.cpp` (hidden counting-fixture tests; `retry-recorder` reporter printing test-case, attempt, and partial events with numbers, totals, flags, output, and enforcing nesting; a reporter and a listener written against the existing API only), `tests/TestScripts/testRetryFailed.py`, `tests/ExtraTests/CMakeLists.txt` (target, CTest `RetryFailed::Scenarios`, label `uses-python`).
- **Depends on:** T00, T01, T02.
- **Focused tests:** (built with the `all-tests` preset) scenarios with the option omitted and `--retry-failed 0` produce identical recorder, XML, and JSON output (fixed seed and order); no attempt events appear; the legacy reporter and listener run.
- **Covers:** CO-1, AC-30 (harness part), AC-32 (at `N = 0`).
- **Regression:** full `all-tests` suite (the new target and CTest are part of it); `basic-tests` and approval tests unchanged.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** no.

### [ ] T04 — Isolate one attempt in `RunContext` without behaviour change

- **Outcome:** the body of `RunContext::runTest` from `prepareTestCase` to `tearDownTestCase` is a private helper that runs exactly one complete attempt and returns its totals and output; behaviour, event order, and data are unchanged.
- **Files / symbols:** `src/catch2/internal/catch_run_context.hpp`/`.cpp` (`runTest` and one new private helper; the counter snapshot/restore helpers come with T05, where they are first used).
- **Depends on:** T03.
- **Focused tests:** T03 zero-retry scenarios; existing `PartialTestCaseEvents`.
- **Covers:** CO-1 (refactoring safety).
- **Regression:** full `basic-tests` and `all-tests`; approval tests unchanged.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** no.

### [ ] T05 — Retry loop with fresh state and attempt events

- **Outcome:** with `N ≥ 1`, failed attempts are retried up to `N` times with fresh trackers, generators, persistent fixtures, RNG seed, and output boundaries; attempt events are emitted and balanced; part numbers continue; superseded counters are restored; `testCaseEnded` carries attempts, `M`, flaky, and all attempts' output.
- **Files / symbols:** `src/catch2/internal/catch_run_context.hpp`/`.cpp` (`runTest` attempt loop per plan §4, counter snapshot/restore helpers); `tests/ExtraTests/X96-RetryFailed.cpp`, `tests/TestScripts/testRetryFailed.py`.
- **Depends on:** T04.
- **Focused tests:** scenarios AC-06 – AC-17 (executions, early stop, per-test budgets, sections, nested sections, generators, generators with sections, persistent and per-run fixtures), AC-20 – AC-22 (attempt numbering, one outer pair, partial events inside attempts, earlier diagnostics and output kept), AC-34 (same random values per attempt, reproducible runs), AC-32 at `N = 2` (legacy reporter and listener with a fail-then-pass test), AC-33 scenario (two reporters and a listener receive the same attempt events in order).
- **Covers:** R-1, R-2, R-4, R-5, R-7; S-1 – S-7, S-9; E-1 – E-6, E-8; CO-6 (code review: no change to debug-break or fatal handling), CO-7.
- **Regression:** full `basic-tests` and `all-tests`; approval tests unchanged; T03 zero-retry scenarios.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** no.

### [ ] T06 — Final totals, exit status, special tags, abort, selection

- **Outcome:** totals and exit codes reflect final attempts only; special tags, skip, abort precedence and budget, filters, sharding, listing, and the largest `N` behave as specified.
- **Files / symbols:** `src/catch2/internal/catch_run_context.cpp` (only if a scenario exposes a defect); `tests/ExtraTests/X96-RetryFailed.cpp`, `tests/TestScripts/testRetryFailed.py`.
- **Depends on:** T05.
- **Focused tests:** AC-05 (`N = 4294967295`, `M = 4294967296` in events), AC-12, AC-18, AC-19, AC-26 (totals per outcome kind), AC-27 (filters `-c`, test spec, `--shard-count`/`--shard-index`), AC-28, AC-29, AC-36 (abort), AC-31 (listing), exit codes for AC-07 – AC-10, Automake `:test-result:` lines for a flaky pass (`PASS`) and an exhausted test (`FAIL`).
- **Covers:** R-3, R-8; T-1 – T-6; AB-1 – AB-3; CO-4, CO-5; CLI-8.
- **Regression:** full `basic-tests` and `all-tests`; approval tests unchanged.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** no.

### [ ] T07 — Fatal error during an attempt

- **Outcome:** with `N ≥ 1`, a fatal signal or structured exception ends the current attempt (attempt end before Catch2's existing test-case end), is not retried, and the process ends as today.
- **Files / symbols:** `src/catch2/internal/catch_run_context.hpp`/`.cpp` (`handleFatalErrorCondition`, current-attempt members); `tests/ExtraTests/X96-RetryFailed.cpp` (platform-guarded crash test like `X36`), `tests/ExtraTests/CMakeLists.txt` (label `uses-signals`).
- **Depends on:** T05; sequenced after T06 so that edits to `catch_run_context.cpp` stay serial.
- **Focused tests:** AC-35 with the recorder: one attempt, balanced attempt events, fatal report.
- **Covers:** R-6, E-7.
- **Regression:** existing `Reporters::CrashInJunitReporter`; full `all-tests`.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** no.

### [ ] T08 — Console and compact reporters

- **Outcome:** console and compact output identify a retry, the attempt of later failures, a flaky pass, and an exhausted test; nothing changes without a retry.
- **Files / symbols:** `src/catch2/reporters/catch_reporter_console.hpp`/`.cpp`, `catch_reporter_compact.hpp`/`.cpp` (attempt overrides per D14); scenarios in `testRetryFailed.py`.
- **Depends on:** T05.
- **Focused tests:** AC-23 for console and compact (fail-then-pass, always-fail); `N = 1` without retries is identical to the option omitted.
- **Covers:** spec §5.2 console, compact.
- **Regression:** approval tests unchanged (console and compact baselines); full `all-tests`.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** code yes; shares `X96-RetryFailed.cpp` and the scenario script, so done in sequence.

### [ ] T09 — XML and JSON reporters

- **Outcome:** XML nests each attempt in `<Attempt>` with `<AttemptResult>` and extends `OverallResult`; JSON adds `attempt` to partial runs and an `attempts` object; output parses and states final status and flakiness; zero-retry output is byte-identical.
- **Files / symbols:** `src/catch2/reporters/catch_reporter_xml.hpp`/`.cpp`, `catch_reporter_json.hpp`/`.cpp` (D11); scenarios in `testRetryFailed.py`.
- **Depends on:** T05.
- **Focused tests:** AC-24; AC-25 for XML and JSON with `xml.etree` and `json`; zero-retry byte identity.
- **Covers:** spec §5.2 XML, JSON.
- **Regression:** approval tests unchanged (XML baselines; JSON has none in approvals); full `all-tests`.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** code yes; shares `X96-RetryFailed.cpp` and the scenario script, so done in sequence.

### [ ] T10 — Cumulative base, JUnit, SonarQube

- **Outcome:** cumulative reporters keep one tree per attempt; JUnit reports only final failures as `<failure>`/`<error>`, prepends superseded failures to `<system-out>`, and keeps `errors`/`failures` correct; SonarQube writes superseded failures as sanitized comments.
- **Files / symbols:** `src/catch2/reporters/catch_reporter_cumulative_base.hpp`/`.cpp` (`TestCaseNode`, `TestCaseAttemptNode`, attempt handling), `catch_reporter_junit.hpp`/`.cpp` (`unexpectedExceptions` per attempt), `catch_reporter_sonarqube.hpp`/`.cpp` (D6, D8, D9); scenarios in `testRetryFailed.py`.
- **Depends on:** T05, T07.
- **Focused tests:** AC-25 for JUnit and SonarQube with `xml.etree` (flaky pass without failure elements, exhausted with final failures, `errors="0" failures="0"` for a flaky pass whose first attempt threw, `--` in a superseded expression); crash scenario with `--reporter JUnit` and `N = 2`.
- **Covers:** spec §5.2 JUnit, SonarQube; S-8.
- **Regression:** approval tests unchanged (JUnit and SonarQube baselines); `Reporters::CrashInJunitReporter`; `BenchmarksInCumulativeReporter`; full `all-tests`.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** code yes; shares `X96-RetryFailed.cpp` and the scenario script, so done in sequence.

### [ ] T11 — TeamCity and TAP reporters

- **Outcome:** with `N ≥ 1`, TeamCity and TAP hold back the current attempt; final attempts are written exactly as today; superseded failures become TeamCity `testStdErr` and TAP `#` diagnostics that do not fail the run.
- **Files / symbols:** `src/catch2/reporters/catch_reporter_teamcity.hpp`/`.cpp`, `catch_reporter_tap.hpp`/`.cpp` (D10); scenarios in `testRetryFailed.py`.
- **Depends on:** T05.
- **Focused tests:** flaky pass yields no `testFailed` and no `not ok`; exhausted test yields them for the final attempt; TAP plan count matches final points; `N = 1` without retries is byte-identical, including `--colour-mode ansi` for TAP.
- **Covers:** spec §5.2 TeamCity, TAP.
- **Regression:** approval tests unchanged (TeamCity and TAP baselines); full `all-tests`.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** code yes; shares `X96-RetryFailed.cpp` and the scenario script, so done in sequence.

### [ ] T12 — Documentation

- **Outcome:** user and extension documentation describe the option and the reporter API as required by spec §10.
- **Files:** `docs/command-line.md` (section and table-of-contents entry), `docs/reporter-events.md` (attempt events, `TestCaseStats` fields), `docs/reporters.md` (retry output of built-in reporters), `docs/test-fixtures.md` (persistent fixtures per attempt); version marker `Catch2 X.Y.Z`.
- **Depends on:** T05 – T11.
- **Focused tests:** checklist of the nine documentation items in spec §10 against the text; examples run as written against the T05 build.
- **Covers:** spec §10.
- **Regression:** none (documentation only).
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** no.

### [ ] T13 — Amalgamated files and full regression

- **Outcome:** tracked amalgamated files are regenerated, and the complete suites pass on Windows.
- **Files:** `extras/catch_amalgamated.hpp`, `extras/catch_amalgamated.cpp`.
- **Depends on:** T12.
- **Focused tests:** `python tools/scripts/generateAmalgamatedFiles.py`; diff limited to source changes and the `Generated:` line; `all-tests` preset build and CTest in **fresh** build directories (incremental builds hide warnings of unchanged files and let the CMake configuration tests reuse earlier builds, see T00) (amalgamated build test included); `basic-tests`; approval tests with no unintended baseline change.
- **Covers:** CO-1 (final confirmation), generated-file deliverable.
- **Regression:** everything; results compared with baseline runs 5 (82/82) and 6 (145/145).
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** no.

### [ ] T14 — Implementation notes

- **Outcome:** `IMPLEMENTATION_NOTES.md` at the Catch2 root covers the nine items the assignment requires, with commands actually run and their results.
- **Files:** `IMPLEMENTATION_NOTES.md`.
- **Depends on:** T13.
- **Focused tests:** each of the nine items present and consistent with the code, tests, and recorded evidence.
- **Covers:** assignment deliverable; contract definition of done.
- **Evidence:** _pending_ (format: see Working Model)
- **Independent:** no.

## Coverage

### Specification requirements

| Requirement | Tasks |
| --- | --- |
| CLI-1 – CLI-7 | T01 |
| CLI-8 | T01 (parsing), T06 (events) |
| R-1, R-2, R-4, R-5, R-7 | T05 |
| R-3, R-8 | T06 |
| R-6 | T07 |
| S-1 – S-7, S-9 | T05 |
| S-8 | T10 |
| E-1 – E-6, E-8 | T05 |
| E-7 | T06 (abort), T07 (fatal) |
| E-9 | T02, T03, T05 |
| §5.2 console, compact | T08 |
| §5.2 XML, JSON | T09 |
| §5.2 JUnit, SonarQube | T10 |
| §5.2 TeamCity, TAP | T11 |
| §5.2 Automake | T06 (final-status scenario; no code change planned) |
| T-1 – T-6 | T06 |
| AB-1 – AB-3 | T06 |
| CO-1 | T03, T04, T13 |
| CO-2, CO-3 | T02, T03, T05 |
| CO-4, CO-5 | T06 |
| CO-6 | T05 (review) |
| CO-7 | T05 |
| Documentation (spec §10) | T12 |
| `IMPLEMENTATION_NOTES.md` | T14 |

### Acceptance scenarios

| Scenarios | Task |
| --- | --- |
| AC-01 – AC-04 | T01 |
| AC-05 | T01 (configuration), T06 (events) |
| AC-06 – AC-17, AC-20 – AC-22, AC-34 | T05 |
| AC-12, AC-18, AC-19, AC-26 – AC-29, AC-31, AC-36 | T06 |
| AC-23 | T08 |
| AC-24 | T09 |
| AC-25 | T09 (XML, JSON), T10 (JUnit, SonarQube) |
| AC-30 | T03, T04, T13 |
| AC-32 | T03 (`N = 0`), T05 (`N = 2`) |
| AC-33 | T02 (unit), T05 (scenario) |
| AC-35 | T07, T10 (with JUnit) |

AC-12 appears under T05 for execution counts and T06 for totals.

## Gate Status

| Gate | Status |
| --- | --- |
| The graph has no hidden circular dependency | ✅ Dependency graph above |
| Tests are part of the relevant task, not deferred | ✅ Every code task lists its focused tests |
| Every specification requirement has at least one task and validation path | ✅ Coverage tables |
| There is one authoritative task list | ✅ This file |
