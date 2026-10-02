# C++ Practical Task: Retry Failed Tests in Catch2

| Field | Value |
| --- | --- |
| Task | 09.01 |
| Track | C++ |
| Difficulty | Advanced |
| Repository | [catchorg/Catch2](https://github.com/catchorg/Catch2) |
| Base version | [`v3.16.0`](https://github.com/catchorg/Catch2/releases/tag/v3.16.0) |
| Expected effort | 6–10 hours |
| AI development tools | Allowed and expected |

## Task Summary

Extend Catch2 with opt-in support for retrying failed test cases. The feature must be implemented inside Catch2's existing configuration, execution, statistics, and reporter architecture. It must not introduce a wrapper executable, a second test runner, or a script that launches the test process repeatedly.

Add the following command-line option:

```text
--retry-failed N
```

`N` is the maximum number of **additional attempts** after the initial attempt. The default value is `0`.

```console
tests --retry-failed 2
```

This permits at most three attempts for each selected test case:

```text
attempt 1: initial attempt
attempt 2: first retry
attempt 3: second retry
```

The goal is not merely to run a test body again. The implementation must preserve Catch2's logical test-case semantics, restart section and generator traversal correctly, expose retry information through reporters, and keep final statistics and exit status accurate.

## Starting Point

1. Check out the exact `v3.16.0` tag before making changes.
2. Build the unmodified repository and run its basic test suite.
3. Read the project contribution guide, command-line documentation, reporter event documentation, and the current test execution path.
4. Record the baseline build and test commands in the implementation note.

Do not silently switch to a newer branch or release. If the tag cannot be built in the chosen environment, document the blocker before changing production code.

## Terminology

| Term | Meaning in this task |
| --- | --- |
| Logical test case | One registered Catch2 test case selected for the run. It contributes at most one final test-case result. |
| Attempt | One complete execution of the logical test case, including every partial run required to traverse its sections and generators. |
| Partial run | One entry into the test case represented by Catch2's existing `testCasePartialStarting` and `testCasePartialEnded` events. A partial run is not a retry. |
| Retry | Any attempt after attempt 1. |
| Retry budget | The configured value `N`, counted independently for every selected logical test case. |
| Flaky pass | A logical test case whose earlier attempt had a retryable failure and whose final attempt passed. |
| Final outcome | The Catch2 outcome of the last required attempt after existing special-tag semantics have been applied. |

Attempt numbers shown to users and reporters must be one-based. Internal indexing may use a different representation if it is kept private and cannot leak into output.

## Command-Line and Configuration Requirements

- `--retry-failed N` must accept a non-negative integer representable by the chosen configuration type.
- The option must have no short alias.
- The help text must state that `N` is the number of retries, not the total number of attempts.
- Omitting the option must preserve Catch2's existing behavior.
- `--retry-failed 0` must be equivalent to omitting it, including event order, execution count, reporting, statistics, and exit status.
- Positive values must be available through Catch2's normal configuration abstraction, not only through a local command-line-parser variable.
- A missing value, negative value, fractional value, malformed value, or out-of-range value must be rejected through Catch2's normal command-line error path.
- A command-line error must occur before any selected test case starts.
- The retry budget applies independently to every selected test case; it is not a session-wide pool.
- Attempt-limit arithmetic must not overflow for the largest accepted value. Prefer comparing retries already used with `N`, or use a wider type when displaying `N + 1`.
- Extending the public configuration abstraction must preserve source compatibility where practical; do not add a mandatory pure virtual member that breaks otherwise valid custom configuration implementations without a documented compatibility design.

At minimum, validate these inputs:

| Input | Expected result |
| --- | --- |
| option omitted | accepted; zero retries |
| `--retry-failed 0` | accepted; zero retries |
| `--retry-failed 1` | accepted; at most two attempts per test case |
| `--retry-failed 3` | accepted; at most four attempts per test case |
| `--retry-failed` | command-line error |
| `--retry-failed -1` | command-line error |
| `--retry-failed abc` | command-line error |
| `--retry-failed 1.5` | command-line error |
| value larger than the supported type | command-line error |

## Retry Decision and Final Outcome

The retry decision must be made only after one complete attempt finishes. A test case with sections or generators can enter its body many times during one attempt; these entries must not consume the retry budget.

Use Catch2's completed test-case outcome after its existing special-tag handling. Do not invent a second pass/fail classifier based on individual assertions.

| Completed attempt outcome | Retry? | Final result if no retry occurs |
| --- | --- | --- |
| Passed | No | Passed |
| Failed, with budget remaining | Yes | Not final yet |
| Failed, with no budget remaining | No | Failed |
| Skipped | No | Skipped |
| Accepted failure from `[!mayfail]` | No | Preserve Catch2's accepted-failure result |
| Expected failure from `[!shouldfail]` | No | Preserve Catch2's accepted-failure result |
| Unexpected pass from `[!shouldfail]` | Yes, if budget remains | Failed if the budget is exhausted |

Additional rules:

- A test case that passes on attempt 1 must execute exactly once.
- Stop immediately after the first semantically passing attempt.
- A test case that passes after one or more retryable failures has final outcome **passed** and is marked as a flaky pass.
- A test case whose attempts all fail has one final **failed** outcome, not one failed test case per attempt.
- Catchable assertion failures, `REQUIRE`-style early exits, and exceptions that Catch2 normally converts into a test failure are retryable when the completed attempt is failed.
- A process crash, forced termination, fatal signal, stack overflow, or any failure from which Catch2 cannot return to the runner is not retryable.
- A retry reruns the entire logical test case. It must never resume at the failed assertion, section, or generator value.

## Fresh State for Every Attempt

Every retry must behave like a new Catch2 execution of that test case while remaining in the same process.

Reset or recreate all Catch2-managed per-attempt state, including:

- the root tracker and complete `SECTION` traversal state;
- nested-section traversal state;
- generator instances, tracking, and advancement state;
- assertion and test-case result accumulation used to classify the attempt;
- captured standard output and standard error boundaries;
- reporter-side attempt data owned by Catch2;
- the test invoker's prepare/tear-down lifecycle, so fixture-based test cases receive a fresh fixture for every attempt; and
- any other state that controls which partial execution path runs next.

One attempt must still complete every partial run required by the test's sections and generators before the retry decision is made. On retry:

- section traversal starts from its first eligible path;
- nested sections are visited as a fresh traversal;
- generators start again from their first eligible value; and
- fixed `--rng-seed` runs remain reproducible and no new session-level nondeterminism is introduced.

The feature does **not** roll back arbitrary state owned by test code. Global variables, static variables, files, databases, environment variables, network services, and other external side effects remain the test author's responsibility. This boundary must be documented because deterministic retry fixtures can intentionally use controlled external or static state to fail a known number of attempts before passing.

## Reporter and Event Contract

Retry information must travel through Catch2's reporter abstraction. Printing retry messages directly from the runner to standard output is not an acceptable implementation.

The exact data types and callback names are design choices, but the following observable contract is required:

- One logical test case emits one outer `testCaseStarting`/`testCaseEnded` pair.
- Attempt boundaries are observable by reporters, including the one-based attempt number and the maximum permitted number of attempts.
- Existing `testCasePartialStarting`/`testCasePartialEnded` events retain their current meaning. They must not be repurposed as retry events.
- Every emitted start event has a matching end event, including failed attempts and the final attempt.
- The reporter can distinguish an intermediate failed attempt from the final outcome.
- A final pass after an earlier failed attempt is explicitly identifiable as flaky.
- Diagnostics, captured output, and assertion information from earlier failed attempts remain available to reporters; they must not silently disappear after a later pass.
- Built-in console output clearly identifies retries and a flaky final pass.
- At least one built-in machine-readable reporter represents retry or flaky information structurally rather than embedding it only in free-form text.
- JSON, XML, JUnit, and other affected machine-readable reporters continue to emit syntactically valid output and report the correct final test-case status.
- Multi-reporter forwarding, event listeners, streaming reporters, and cumulative reporters remain coherent.
- Adding retry support must not require existing custom reporters to implement a new pure virtual callback merely to compile. Use a backward-compatible default, an existing extensibility mechanism, or another source-compatible design.
- With retries disabled, reporters observe the same event sequence and data as unmodified Catch2 `v3.16.0`.

If a public reporter event or data structure is added, document its lifecycle, nesting, numbering, and compatibility behavior.

## Statistics and Exit Status

Attempt diagnostics and final logical statistics are different concerns and must be stored or aggregated separately.

- Each selected logical test case contributes exactly one final test-case count.
- A flaky pass contributes one passed test case and zero failed test cases.
- An exhausted test contributes one failed test case regardless of the number of attempts.
- A skipped or accepted-failure test preserves Catch2's existing counting semantics.
- Final assertion totals contain the assertions from the final attempt only. Assertions from earlier failed attempts remain reportable as attempt diagnostics but do not inflate session totals.
- Intermediate failures must not make a later flaky pass appear failed in `TestCaseStats`, `TestRunStats`, summary output, or process exit status.
- When all attempts fail, diagnostics from every attempt remain available while the final logical counts come from the last attempt.

The process exit status must be based on final logical outcomes:

- return success when every selected test case has an outcome that Catch2 normally treats as successful, including flaky passes;
- return failure when at least one selected test case remains failed after its retry budget is exhausted; and
- preserve all existing exit-status behavior when retries are disabled.

## Interaction with Existing Features

- Filtering, hidden tests, ordering, sharding, registration, and test selection continue to use Catch2's existing mechanisms.
- A passing test case is not rerun merely because another test case needed retries.
- Retries occur inside the already selected shard and do not change shard membership or test order.
- Listing modes do not execute tests and therefore do not perform retries.
- Existing path filters for sections and generators still apply to every attempt.
- Existing special tags, including `[!mayfail]` and `[!shouldfail]`, retain the semantics described above.
- Existing captured-output behavior remains valid, with output attributable to the correct attempt.
- The retry feature must not suppress debugger breaks, fatal-condition handling, or other existing assertion-time behavior.

`--abort` and `--abortx` take precedence once Catch2's current abort condition is reached. If the threshold is reached during an attempt, do not start another retry and preserve Catch2's existing behavior for skipping the remaining test cases. Failed assertions from an attempt that is safely retried and later superseded must not consume the abort budget for later logical test cases. Cover this behavior with focused automated tests.

Parallel retry scheduling, retry delays, retry-only filters, persistence across process launches, restarting a crashed process, and automatic rollback of external state are out of scope.

## Architecture Guidance

Begin repository exploration in these areas of Catch2 `v3.16.0`:

- `src/catch2/catch_config.*` for stored configuration;
- `src/catch2/interfaces/catch_interfaces_config.hpp` for the configuration abstraction;
- `src/catch2/internal/catch_commandline.*` for command-line parsing;
- `src/catch2/internal/catch_run_context.*` for logical test-case execution, totals, and abort handling;
- `src/catch2/internal/catch_test_case_tracker.*` for sections and generators;
- `src/catch2/interfaces/catch_interfaces_reporter.*` for reporter data and lifecycle events;
- `src/catch2/reporters/` for built-in, multi, streaming, and cumulative reporters;
- `tests/SelfTest/IntrospectiveTests/` for focused internal tests;
- `tests/SelfTest/UsageTests/` and approval baselines for end-to-end behavior; and
- `docs/command-line.md`, `docs/reporter-events.md`, and `docs/reporters.md` for user and extension documentation.

These are starting points, not a required file-change list. Keep the implementation localized, follow existing naming and formatting, reuse Catch2's result types, and avoid unrelated refactoring.

Do not implement the feature by:

- recursively invoking the test executable;
- wrapping Catch2 in a shell, Python, CTest, or CI retry loop;
- treating each retry as a separately registered test case;
- directly editing final totals after reporters have already received contradictory events; or
- discarding failed-attempt diagnostics to make the final totals look correct.

## Required Automated Tests

Use Catch2's existing test infrastructure and add deterministic coverage at the most appropriate layer. At minimum, cover the following cases.

### Command-line and configuration

1. The default retry count is zero.
2. Zero and positive values parse correctly and are visible through the normal configuration interface.
3. Missing, negative, fractional, malformed, and out-of-range values use the normal CLI error path, and the largest accepted value does not overflow attempt-limit logic.
4. A CLI error occurs before test execution.
5. Help output documents the new option and its additional-attempt meaning.

### Execution and state isolation

6. An immediate pass executes once even when retries are configured.
7. A test fails once and passes on the first retry.
8. A test fails multiple times and then passes within the limit.
9. An always-failing test executes exactly `N + 1` times.
10. A test would eventually pass, but the configured limit is exhausted first.
11. Retrying stops immediately after a pass and does not consume unused budget.
12. Retry counts do not leak between multiple test cases.
13. Only failing test cases are retried when passing and failing cases run together.
14. A test with one `SECTION` restarts traversal from the beginning.
15. Multiple sibling and nested `SECTION`s revisit the expected paths without stale tracker state.
16. A test using `GENERATE` restarts from the first eligible generator value.
17. A test combining generators and nested sections restarts the complete traversal.
18. A fixture-based test receives balanced prepare/tear-down calls and a fresh fixture for each attempt.
19. A skipped test is not retried.
20. `[!mayfail]` and `[!shouldfail]` outcomes follow the decision table above.

### Reporting, totals, and integration

21. Reporter attempt events contain correct one-based numbering and are balanced.
22. One outer logical test-case start/end pair is emitted regardless of retry count.
23. Partial-run events remain distinct from attempt events for sections and generators.
24. Diagnostics and captured output from earlier failures remain observable after a flaky pass.
25. Console output identifies the retry and the final flaky pass.
26. At least one machine-readable reporter exposes retry/flaky data structurally.
27. Affected JSON and XML-family outputs remain parseable and have the correct final status.
28. Immediate passes, flaky passes, exhausted failures, skips, and accepted failures have correct final test-case and assertion totals.
29. A flaky pass produces a successful process exit code.
30. An exhausted retry budget produces a failing process exit code.
31. Retry behavior remains isolated under filtering and sharding.
32. The documented abort precedence and abort-budget behavior are deterministic.
33. With the option omitted or set to zero, a recording reporter observes the baseline event sequence and statistics.

Fixtures that simulate flakiness must fail by a controlled attempt counter. Do not use timing, randomness, thread races, network access, or unreliable external resources.

## Acceptance Examples

For an ordinary test case, the following outcomes are required:

| Attempt sequence | `N` | Executions | Final outcome | Flaky | Exit contribution |
| --- | ---: | ---: | --- | --- | --- |
| pass | 2 | 1 | passed | no | success |
| fail, pass | 2 | 2 | passed | yes | success |
| fail, fail, pass | 2 | 3 | passed | yes | success |
| fail, fail, fail | 2 | 3 | failed | no | failure |
| fail, fail, pass would be next | 1 | 2 | failed | no | failure |
| skip | 2 | 1 | skipped | no | existing Catch2 behavior |

For a run containing three tests—one immediate pass, one fail-then-pass, and one always-fail with `N = 2`—the final test-case totals must be two passed and one failed. The failed-attempt assertions remain available as diagnostics but are not added to the final assertion totals.

## Documentation Requirements

Update the relevant Catch2 documentation with:

- the syntax and default value of `--retry-failed`;
- the definition of `N` as additional attempts;
- examples for zero, one, and multiple retries;
- final-result and flaky-reporting semantics;
- the distinction between attempts and partial runs;
- the fresh Catch2-managed state guarantee;
- the external-state rollback limitation;
- interactions with special tags and abort options; and
- any new reporter API, event, or data fields.

If public headers change, regenerate and include Catch2's tracked amalgamated distribution using the project script. These tracked generated sources are deliverables; build directories, caches, and temporary output are not.

## Validation Workflow

Use the commands appropriate for the local generator and platform. A typical validation sequence from the Catch2 repository root is:

```sh
python tools/scripts/generateAmalgamatedFiles.py

cmake -B basic-test-build -S . -DCMAKE_BUILD_TYPE=Debug --preset basic-tests
cmake --build basic-test-build --config Debug
ctest --test-dir basic-test-build -C Debug --output-on-failure
```

Before submission, run the broader relevant suite:

```sh
cmake -B debug-build -S . -DCMAKE_BUILD_TYPE=Debug --preset all-tests
cmake --build debug-build --config Debug
ctest --test-dir debug-build -C Debug --output-on-failure -j 4
```

Catch2 uses approval tests for reporter output. Inspect every baseline difference, approve only intentional changes, and include the required updated baselines. If a full test category cannot run in the available environment, state exactly what was skipped and why; do not describe an unexecuted command as passing.

Also inspect the final diff for unrelated formatting, generated build output, dependency caches, credentials, and accidental API changes.

## Deliverables

Submit the modified Catch2 repository containing:

- the implementation;
- deterministic automated tests;
- updated approval baselines where required;
- command-line and reporter documentation;
- regenerated tracked amalgamated files when public headers or implementation require them;
- any necessary build or test configuration changes; and
- `IMPLEMENTATION_NOTES.md` at the repository root.

The implementation note must include:

1. a concise description of the execution design;
2. the retry decision point and final-outcome rules;
3. how tracker, generator, fixture, output, and assertion state are reset;
4. how intermediate diagnostics are separated from final totals;
5. the reporter API or event design and its compatibility strategy;
6. abort-option and special-tag behavior;
7. the main files changed and why;
8. all validation commands actually run and their results; and
9. known limitations or intentionally unsupported cases.

Do not include build directories, dependency caches, editor state, credentials, or unrelated cleanup.

## Evaluation Rubric

| Area | Weight | What is evaluated |
| --- | ---: | --- |
| Retry behavior and state isolation | 30% | Correct attempt limits, early stop, full section/generator restart, fresh fixtures, and per-test isolation |
| Reporting, statistics, and exit status | 25% | Coherent events, retained diagnostics, flaky visibility, correct final totals, and correct exit code |
| Automated tests | 20% | Deterministic coverage of normal, edge, stateful, reporter, and compatibility cases |
| Catch2 integration and compatibility | 15% | Appropriate architecture, no wrapper runner, localized changes, and preserved zero-retry behavior |
| Documentation and engineering explanation | 10% | Accurate user docs, reporter docs, implementation note, and reproducible validation evidence |

A solution that merely reruns the test body but corrupts section traversal, reporter lifecycle, or final totals is incomplete even if the basic fail-then-pass example works.

## AI-Assisted Development Expectations

Use of AI development tools is expected for repository exploration, architecture analysis, planning, implementation, debugging, test generation, review, and validation.

The submitted work must still be understood and verified by the developer. Be prepared to explain:

- where Catch2 stores and exposes the new option;
- why the retry decision is made at the chosen boundary;
- how every retry receives fresh tracker, generator, and fixture state;
- how failed-attempt diagnostics are retained without entering final totals;
- how reporters learn about attempt boundaries and flaky outcomes;
- how special tags and abort settings behave;
- which tests prove each guarantee; and
- which commands were actually used to validate the repository.

## Completion Checklist

- [ ] The implementation is based on Catch2 `v3.16.0`.
- [ ] `--retry-failed N` is parsed, validated, documented, and exposed through configuration.
- [ ] Omitted option and `--retry-failed 0` preserve baseline behavior and events.
- [ ] Retry count means additional attempts, not total attempts.
- [ ] Passing, skipped, and accepted-failure tests are not retried.
- [ ] Failed tests stop after the first pass or after `N` retries.
- [ ] Sections, nested sections, generators, and fixtures restart correctly.
- [ ] Retry state and counters do not leak between test cases.
- [ ] Attempt and partial-run events remain distinct and balanced.
- [ ] Flaky passes are identifiable and retain earlier diagnostics.
- [ ] Final assertion totals use the final attempt only.
- [ ] Final test-case totals and exit status reflect logical outcomes.
- [ ] Special tags and abort settings follow the documented rules.
- [ ] Existing custom reporter source compatibility is preserved.
- [ ] Machine-readable reporter output remains valid.
- [ ] Required automated tests are deterministic and pass.
- [ ] Relevant existing tests and approval tests pass.
- [ ] Tracked amalgamated files and intentional baselines are updated.
- [ ] Documentation and `IMPLEMENTATION_NOTES.md` are complete.
- [ ] The final diff contains no build output, caches, secrets, or unrelated changes.
