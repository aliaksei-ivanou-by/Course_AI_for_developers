# Retry Failed Tests in Catch2 — Practical Task 09.01

**English** | [Русский](README.ru.md)

This folder contains a completed advanced C++ practical task from the AI-assisted development course: adding opt-in retries of failed test cases to the [Catch2](https://github.com/catchorg/Catch2) test framework, version `v3.16.0`. The work used AI agents throughout, but every phase passed a human gate and every recorded result comes from a command that was actually run.

| Document | Purpose |
| --- | --- |
| [Task specification](01%20C%2B%2B%20-%20Retry%20Failed%20Tests%20in%20Catch2.md) | The assignment: what had to be delivered |
| [Implementation/README.md](Implementation/README.md) | The working process: phases, gates, session protocol, prompt contract |
| [Implementation/artifacts/](Implementation/artifacts/) | Contract, baseline, codebase map, specification, plan, tasks, decisions, review, validation, retrospective |
| [Implementation/patches/](Implementation/patches/) | The Catch2 changes as 23 patches against `v3.16.0` |
| This README | What the task was, how it was done, results, statistics, and reflections on AI-assisted development |

## 1. The task

Catch2 is a widely used C++ unit-testing framework. The assignment was to add a command-line option:

```text
--retry-failed N
```

`N` is the number of **additional** attempts after the first one, so `--retry-failed 2` allows at most three attempts per test case. The default is `0`.

The difficulty is not running a test body again but keeping Catch2's semantics correct:

- one logical test case must still produce one final result, even after several attempts;
- every attempt must start from fresh Catch2 state: section traversal, generators, fixtures, captured output, and assertion counters;
- the retry decision may only be made after a complete attempt, including every partial run needed to traverse sections and generators;
- special tags (`[!mayfail]`, `[!shouldfail]`), skips, `--abort`/`--abortx`, filtering, and sharding must keep their meaning;
- reporters must see attempt boundaries, keep diagnostics of earlier failed attempts, identify flaky passes, and report correct final totals and exit codes;
- with the option omitted or set to `0`, Catch2 must behave exactly like `v3.16.0`;
- existing custom reporters and configurations must keep compiling.

It was explicitly forbidden to implement this with a wrapper executable, a script that relaunches the test process, or by registering retries as separate test cases. The deliverables were the implementation, deterministic automated tests, documentation, regenerated amalgamated sources, and an `IMPLEMENTATION_NOTES.md` with the commands actually run. The expected effort was 6–10 hours.

## 2. Results at a glance

| Area | Result |
| --- | --- |
| Option | `--retry-failed N`, unsigned, default `0`, no short alias; invalid values go through Catch2's normal command-line error path before any test runs |
| Execution | Attempt loop inside `RunContext::runTest`; one outer `testCaseStarting`/`testCaseEnded` pair per logical test case |
| Fresh state | New tracker root per attempt, fixtures prepared and torn down per attempt, RNG reseeded, output captured per attempt, assertion counters snapshotted and restored for superseded attempts |
| Reporter API | New non-pure events `testCaseAttemptStarting`/`testCaseAttemptEnded`, new `TestCaseAttemptInfo`/`TestCaseAttemptStats`, new `TestCaseStats` fields `attemptCount`, `maxAttempts`, `isFlaky`; existing reporters compile unchanged |
| Built-in reporters | Console, compact, XML, JSON, JUnit, SonarQube, TeamCity, TAP, and Automake all report retries; XML and JSON represent attempts structurally |
| Compatibility | With retries disabled, all 19 approval baselines are unchanged |
| Tests (Windows, MSVC) | `basic-tests` 82 → **92/92**; `all-tests` 145 → **158/158**; only the four `D9025` warnings that the unmodified baseline already has |
| Reproducibility | 23 patches apply to a clean `v3.16.0` and reproduce the validated tree `18072a42c0498a3235e782eb2571883f7d4fb9ef` |
| Review | 9 findings (2 high, 3 medium, 4 low), all resolved; all verification gaps closed |

## 3. How the work was done

### 3.1 Workflow

The work used the C++ / Embedded Accelerator and the phase-gated process recorded in [Implementation/README.md](Implementation/README.md). The `feature` route combined Explore → Plan → Code → Commit, specification-driven development with Spec Kit concepts, context-engineering practices, and explicit human gates. Working state was maintained through `task-workspace`, and reviewed artifacts were exported to the course repository for submission.

| Phase | Output | What happened |
| --- | --- | --- |
| 0. Frame the work | [00-task-contract.md](Implementation/artifacts/00-task-contract.md) | Scope, permissions, and safety rules: no push, no credentials, no destructive Git, repository content treated as untrusted data |
| 1. Pinned baseline | [01-baseline.md](Implementation/artifacts/01-baseline.md) | Clean `v3.16.0` built and tested on Windows: 82/82 basic, 145/145 all; six recorded runs, including the diagnosis of a Windows path-length failure |
| 2. Explore | [02-codebase-map.md](Implementation/artifacts/02-codebase-map.md) | Read-only map of the execution path, trackers, reporters, and tests, with `path:line` references |
| 3. Specify and clarify | [03-spec.md](Implementation/artifacts/03-spec.md), [04-clarifications.md](Implementation/artifacts/04-clarifications.md) | 50 requirements, 36 acceptance scenarios, 15 clarification decisions taken by the reviewer |
| 4. Plan | [05-plan.md](Implementation/artifacts/05-plan.md), [07-decisions.md](Implementation/artifacts/07-decisions.md) | Technical plan and 16 design decisions with alternatives; validated by a throw-away spike before approval |
| 5. Tasks | [06-tasks.md](Implementation/artifacts/06-tasks.md) | 15 tasks (T00–T14), each with files, focused tests, regression set, and evidence format |
| 6. Implement | 14 Catch2 commits (T01–T14) | One commit per task, each validated on Windows before committing |
| 7. Review | [08-review.md](Implementation/artifacts/08-review.md), 5 Catch2 commits | Fresh-context review; findings fixed one at a time |
| 8. Validate | [09-validation.md](Implementation/artifacts/09-validation.md) | Full suites, amalgamation, approval baselines, patch reproducibility, whitespace and secret-marker checks |
| 9. Handoff | [10-retrospective.md](Implementation/artifacts/10-retrospective.md), `patches/` | Retrospective and reproducible patch series |
| Follow-up | T15, T16, 4 Catch2 commits | Closed the remaining verification gaps from the review |

### 3.2 Agents and roles

| Who | Work |
| --- | --- |
| Human reviewer (author) | Set boundaries, answered clarification questions, approved phase gates, reviewed validation results, and pushed the course repository |
| Claude (Anthropic), in Cowork | Phases 0–5, the validation script (T00), T01–T02, the post-handoff audit, and follow-up tasks T15–T16 |
| Codex (OpenAI) | T03–T14, the Phase 7 review and its fixes, Phases 8–9 |

### 3.3 Working model

- **Two environments.** Linux/GCC and Windows/MSVC were both used; Windows/MSVC was the authoritative validation environment. Linux checks were run for selected tasks and follow-up reviews, not necessarily before every change.
- **Scripted and explicit validation.** `scripts/phase6-validate.ps1` checks the branch and base commit, refuses stale approval output, builds a preset incrementally, runs a focused CTest filter and then the full suite, and writes a summary per run to `evidence/raw/phase6/<task>-run-NN-<preset>/`. Some later review and final checks were run as explicit commands and recorded in `09-validation.md`.
- **Reviewed local commits; no Catch2 push.** Commits were created locally through the reviewed workflow, including by the agents using Git tools under the checkout's configured identity. Git author metadata therefore does not by itself show who initiated a commit. The course repository was pushed; the Catch2 task branch was not pushed.
- **Patches as the handoff.** The nested Catch2 checkout is not tracked by the course repository. After every commit the patch series was regenerated with `git format-patch -N` into `patches/`, so the course repository always contains the reproducible code.
- **Evidence before status.** A task was marked done only after its Windows run passed and its evidence line, commit, and patch were recorded.

## 4. Design in brief

```text
testCaseStarting
  attempt 1: testCaseAttemptStarting → partial runs → testCaseAttemptEnded (isFinal = false)
  attempt 2: testCaseAttemptStarting → partial runs → testCaseAttemptEnded (isFinal = true)
testCaseEnded (attemptCount = 2, maxAttempts = 3, isFlaky = true)
```

- **Decision point.** After a whole attempt: retry when the attempt failed, retries remain, and the run is not aborting. The comparison is `retriesUsed < N`, and `maxAttempts = uint64(N) + 1`, so the largest accepted value cannot overflow.
- **Final totals.** Assertion counters are snapshotted before an attempt and restored when the attempt is superseded, so totals, exit status, and the `--abort` budget count only final attempts, while reporters still receive every diagnostic live.
- **Special tags.** Catch2's own outcome rules decide: accepted failures and skips are not retried; an unexpected pass under `[!shouldfail]` is a failure and is retried.
- **Compatibility.** New virtual methods have empty default bodies and `IConfig::retryFailed()` returns `0` by default. With `N = 0` no attempt events are emitted at all.
- **Reporters.** Superseded failures appear as non-failing diagnostics: JUnit `system-out`, SonarQube XML comments, TeamCity `testStdErr`, TAP `#` lines; XML adds `<Attempt>` elements and JSON an `attempts` object.

Full details: `IMPLEMENTATION_NOTES.md` at the root of the patched Catch2 tree (written by patches `0014`, `0019`, `0022`, and `0023`), [05-plan.md](Implementation/artifacts/05-plan.md), and [07-decisions.md](Implementation/artifacts/07-decisions.md).

## 5. Testing strategy

| Layer | What it proves |
| --- | --- |
| SelfTest unit tests (3 test cases) | Option parsing and limits, `IConfig` default, multi-reporter forwarding, source compatibility of a reporter written against the old interface |
| CLI CTests (10) | Help text, every rejected input, error before any test runs, non-zero exit |
| `RetryFailed::Scenarios` | 31 scripted scenario invocations driven by a recording reporter and real parsers (`json`, `xml.etree`); the final Linux run recorded 110 child-process runs. Assertions cover limits, early stop, sections, generators, fixtures, skips, special tags, abort, sharding, totals, exit codes, and built-in reporters |
| `RetryFailed::Fatal` | Fatal signal or structured exception during an attempt: balanced events, and every reporter's output compared with and without retries (18 crashing children) |
| `RetryFailed::DebugBreak` | `--break` still breaks on every failed assertion of every attempt |
| Approval tests | Zero-retry output of all reporters is byte-identical to `v3.16.0` |

New SelfTest cases carry the `[approvals]` tag so they do not alter the approval baselines. Flaky fixtures fail by a controlled per-process counter; no timing, randomness, or external resources are involved. Several new checks were confirmed to fail by deliberately breaking the code.

## 6. Statistics

| Metric | Value |
| --- | --- |
| Catch2 commits / patches | 23 (19 in the main implementation and review, 4 in the follow-up) |
| Changed files | 45 (39 modified, 6 added) |
| Lines | +7,359 / −226 in total; `src/` +1,351 / −110 in 29 files; tests +4,157; docs +173 / −4; `IMPLEMENTATION_NOTES.md` 328 lines; regenerated amalgamated files +1,350 / −112 |
| Specification | 50 requirements, 36 acceptance scenarios, 15 clarifications, 16 design decisions |
| Tasks | 17 (T00–T14 planned, T15–T16 follow-up) |
| CTest | 82 → 92 basic, 145 → 158 all |
| Retry scenario script | 2,460 lines, 110 child process runs per execution |
| Approval baselines changed | 0 of 19 |
| Recorded validation runs | 7 baseline runs and 37 task runs on Windows, plus 10 repeated runs of the fatal test |
| Review findings | 9: H-1, H-2, M-1, M-2, M-3, L-1 from the review; L-2, L-3, L-4 found while closing verification gaps |
| Course artifacts | 11 artifacts and the workflow README, about 2,500 lines and 34,000 words |

## 7. Review findings and lessons

| Finding | Severity | Summary |
| --- | --- | --- |
| H-1 | High | Exhausted unexpected `[!shouldfail]` passes looked successful in JUnit, SonarQube, TeamCity, and TAP |
| H-2 | High | Failures without assertion events (`-w NoAssertions`) produced wrong reasons and an invalid TAP plan |
| M-1 | Medium | Accepted failures appeared as failures in JUnit and TAP |
| M-2 | Medium | Console and compact called final skips and accepted failures "failed" |
| M-3 | Medium | JUnit suite counters counted assertions instead of logical test cases |
| L-1 | Low | Documentation predated the semantic-outcome fix |
| L-2 | Low | TAP repeated the attempt heading for every diagnostic |
| L-3 | Low | JUnit and SonarQube labelled a section without assertions as a test case |
| L-4 | Low | Documentation omitted JUnit counter changes when retries are enabled but unused |

Lessons, from [10-retrospective.md](Implementation/artifacts/10-retrospective.md):

1. Parser-level reporter checks belong in the plan as soon as outcome rules are defined; most defects were in reporters, not in the runner.
2. Record each validation command and its result immediately, and isolate signal-dependent tests when a parallel run times out.
3. Treat every verification gap named in a review as a task with its own test before the handoff, and confirm with a deliberate regression that the test can fail.

## 8. Reproducing the result

```sh
git clone https://github.com/catchorg/Catch2.git
cd Catch2
git checkout v3.16.0          # commit 317ac1ed4c0bb6e6b91eafc817e05c488feffcb3
git switch -c task/retry-failed
git am "<path-to>/Implementation/patches/"*.patch
git rev-parse "HEAD^{tree}"   # 18072a42c0498a3235e782eb2571883f7d4fb9ef

cmake -B basic-test-build -S . -DCMAKE_BUILD_TYPE=Debug --preset basic-tests
cmake --build basic-test-build --config Debug
ctest --test-dir basic-test-build -C Debug --output-on-failure

cmake -B debug-build -S . -DCMAKE_BUILD_TYPE=Debug --preset all-tests
cmake --build debug-build --config Debug
ctest --test-dir debug-build -C Debug --output-on-failure -j 4
```

On Windows, keep the build directories on a short path (for example `C:\build\...`): the default location inside a deep checkout exceeds the 260-character path limit during CMake's compiler checks.

## 9. Known limitations

- Catch2 resets only its own state. Globals, statics, files, environment variables, databases, network services, and threads owned by the test are not rolled back.
- Crashes, fatal signals, structured exceptions, and stack overflows cannot be retried; Catch2 only reports them as completely as before.
- With retries disabled, `v3.16.0` does not report a leaf section without assertions as a failure in JUnit, TeamCity, or TAP; this zero-retry behaviour is kept for compatibility.
- As in `v3.16.0`, JSON and Automake write nothing to stdout when the process dies from a fatal error.
- TAP buffers its lines until an attempt ends, so they can interleave differently with output written directly by the test.

## 10. Workflow reflection

### 10.1 Accelerator feedback

**1. What is the accelerator, in my own words?**
For me, the Accelerator is not another model or an autopilot; it is a controlled layer around a coding agent. It divides work into explicit stages, loads the right skill for each stage, preserves decisions and evidence across sessions, and stops at human approval gates. On this task it guided the Catch2 change from initial investigation to a reproducible patch series without mixing requirements, implementation, and verification in one long chat.

**2. Which agent did I use?**
Through the Accelerator workflow I used Claude (Anthropic) in Cowork mode for onboarding, baseline verification, exploration, specification, planning, the first tasks, and the final follow-up. I then handed the persisted context to Codex (OpenAI), which performed most of the implementation, a fresh-context review, full validation, and submission preparation. The agent switch used a written handoff, so decisions did not have to be reconstructed from chat history. See [3.2](#32-agents-and-roles).

**3. Which skills did I use?**

- `project-onboard` collected the project context: Catch2's purpose, the `v3.16.0` baseline, repository rules, CMake presets, test suites, and Windows/MSVC constraints.
- `feature` drove the end-to-end `--retry-failed` route and placed human gates before specification, planning, and implementation.
- `task-workspace` preserved state, decisions, evidence, and the next action across phases, context compaction, and the switch from Claude to Codex; reviewed results were then exported to `Implementation/artifacts/`.
- `requirements-analyst` turned the assignment into a [specification](Implementation/artifacts/03-spec.md) with 50 requirements and 36 observable acceptance scenarios.
- `requirements-clarifier` separated repository facts from human decisions and recorded decisions C1–C15 in the [clarification artifact](Implementation/artifacts/04-clarifications.md).
- `writing-plans` produced the technical [plan](Implementation/artifacts/05-plan.md), [task list](Implementation/artifacts/06-tasks.md), and design [decisions](Implementation/artifacts/07-decisions.md), including files, dependencies, and verification commands.
- `coder` implemented the approved plan in small changes: one task, focused verification, local commit, and reproducible patch at a time.
- `testing` added regression coverage for the CLI, retry attempts, sections, generators, fixtures, abort behavior, and every reporter; real parsers validated machine-readable formats.
- `systematic-debugger` handled the Windows path limit, approval-test conflicts, the fatal-error test timeout, and reporter defects by reproducing and isolating the cause before applying a minimal fix.
- `self-review` checked each task's diff against the specification and for accidental scope growth before broader validation.
- `code-reviewer` performed an independent fresh-context review. It produced nine findings, including five reporter defects, all of which were resolved.
- `verify` mapped requirements to evidence and ran the final CMake/CTest, approval, parser, amalgamation, patch-replay, and secret-marker checks recorded in the [validation report](Implementation/artifacts/09-validation.md).
- `handoff` transferred the goal, current phase, approved decisions, Git state, command results, and next action between sessions and agents.
- `stabilize` captured recurring lessons: Windows builds moved to a short path, and the stable validation procedure became `phase6-validate.ps1` and its companion scripts.

I did not use `bug`, `review-pr`, or `pr-review-response`: the original work was a new feature, and the deliverable was a local patch series rather than a PR. Defects found during review were resolved inside the same approved feature workspace.

**4. In what order?**
`project-onboard` → `feature` + `task-workspace` → `requirements-analyst` → `requirements-clarifier` → human specification gate → `writing-plans` → human plan gate → `coder` + `testing` + `self-review` for each task → `systematic-debugger` when a check failed → fresh-context `code-reviewer` → findings fixed through the same short loop → `verify` → final `handoff`. `handoff` was also used whenever the session or agent changed, while `stabilize` was invoked immediately after a recurring problem deserved a durable procedure. The Accelerator did not cross gates automatically: a human approved the specification, plan, and final readiness.

**5. Did I like it, and was it easy to get into?**
Yes. I mainly liked the predictability. It was not hard to learn: after `project-onboard`, the `feature` route made the current phase, expected artifact, and next approval gate explicit. The most useful parts were resuming after context compaction, transferring the task from Claude to Codex without losing decisions, and reviewing the implementation with fresh context. The trade-off was noticeable overhead: the specification, plan, and evidence log were substantial for a 6–10 hour assignment. The full route would be excessive for a tiny edit, but it paid off for a change spanning Catch2's runner and many reporters.

**6. What problems did I run into?**
- I first had to adapt the general `feature` route to a large C++ repository and choose the authoritative validation environment. `project-onboard` and `writing-plans` established Windows/MSVC as the primary loop and Linux/GCC as supporting evidence.
- The Windows 260-character path limit broke the CMake compiler check; a `subst` drive workaround then broke the approval tests, so builds moved to `C:\build\Course_AI\catch2\`.
- Every new SelfTest test changes all approval baselines; new tests were tagged `[approvals]` instead of rebasing 19 baselines.
- Warnings are errors on both GCC and MSVC, so no code could be added before the task that used it.
- Line endings differ by file type (`*.py` are LF, sources CRLF on Windows), which had to be preserved when copying files.
- `git format-patch` renumbered earlier patches (`[PATCH k/n]`) and truncated long file names, which produced a duplicate patch; fixed with `-N` and by removing the stale file.
- The fatal-error test once timed out on Windows; it now runs serially with a longer per-child timeout and passed 10 of 10 repeated runs.
- The review found five reporter defects after the implementation was considered done; reporters, not the runner, were where most edge cases hid.

### 10.2 Metrics

**7. How many tasks were completed?** 17 tasks (T00–T16), 23 Catch2 commits, 9 review findings resolved. The Git author identity was configured for the checkout and does not reliably distinguish human-initiated from agent-initiated commits.

**How long did the work take, and how many tokens did it use?** The actual elapsed work time and aggregate token usage were not tracked reliably. The 6–10 hours stated in the assignment is an estimate, not a measured duration.

### 10.3 Questions about AI-assisted development, with examples from this task

**What is the difference between an LLM and an AI agent?**
An LLM maps text to text; an agent runs the model in a loop with tools and feedback from the environment. Here the agent edited files, ran CMake and CTest in a Linux sandbox, read the results, and corrected itself; the Windows runs gave a second, authoritative feedback loop.

**Why is tool calling essential for an agent?**
The model only returns structured calls; the environment executes them. In this task every build, test, file copy to the reviewer's computer, and evidence read was a tool call whose result came back into the context.

**What risks do autonomous agents bring, and how much autonomy should they have?**
Irreversible actions, accumulated errors, cost, and prompt injection. The task workflow prohibited pushing the Catch2 branch, destructive Git operations, credentials, and unrelated deletions; local commits were made through agent Git tools under the configured identity and reviewed at phase gates. This is human-in-the-loop by design, because a wrong change to a widely used framework is expensive.

**How does context-window filling affect quality, and what is "lost in the middle"?**
Quality drops as the context fills, and the middle of a long context is used worst. The long Claude session was compacted once; because decisions lived in artifacts (`06-tasks.md`, `07-decisions.md`) rather than only in the chat, work continued without losing state. Key facts such as the base commit and the validation command were repeated in every task entry and built into the validation script.

**What is prompt engineering, and which techniques were used?**
Writing instructions the model can follow reliably. The workflow defines a reusable XML prompt contract: objective, context, scope, constraints, verification, done-when, output. Read-only stages added "Do not modify files".

**Why does decomposition help, and how should a task be split?**
Small tasks need less context and have an unambiguous done criterion. The plan was split into 15 tasks by verifiable behaviour, not by file: CLI first, then the inert reporter API, a zero-retry harness, an extraction with no behaviour change, the retry loop, and then each reporter group. Each task had its own focused tests and Windows evidence.

**What is meta-prompting?**
Using the model to improve the prompt itself. Phase 3 turned the assignment into a specification using repository evidence, and the clarification step listed the questions the model could not answer alone; the reviewer's answers became decisions C1–C15.

**How does context engineering differ from prompt engineering, and which context is really needed?**
Prompt engineering is what you ask; context engineering is everything that reaches the window. Here: a codebase map with `path:line` references instead of whole files, concise summaries in `artifacts/` while full logs stayed in the ignored `evidence/raw/`, and only the files a task touched were read.

**What should and should not go into memory files?**
Stable conventions, build and test commands, and boundaries — not details visible in the code. The workflow README and the task contract played this role; Catch2 itself got no agent-specific files.

**What are signs of session degradation, and when should a new session start?**
Repeating fixed mistakes and forgetting agreements. The workflow follows "one task, one chat" and requires a handoff note at the end of every session; the switch between Claude and Codex worked because the state was in the artifacts.

**When is a reasoning model worth it?**
For architecture, debugging, and review — here the plan, the attempt-counter design, and the fresh-context review. Mechanical steps such as copying files, regenerating patches, and running the validation script did not need deep reasoning.

**What is specification-driven development, and why does it fit AI coding?**
The specification is the source of truth and the contract between human and agent. Here 50 requirements and 36 acceptance scenarios gave the agents an objective check, and the review judged findings against `03-spec.md`, not against opinions.

**What should a good implementation spec contain?**
Goal, scope and out of scope, acceptance criteria, constraints, and edge cases. `03-spec.md` has requirement groups for CLI, retry decision, state, events, totals, abort, and compatibility, an acceptance table, and documentation obligations.

**What is a skill, and when should it be used? How do hooks differ?**
A skill is a `SKILL.md` containing a method and output contract that the agent loads on demand. Accelerator skills placed the agent in different working modes here: `requirements-analyst` produced the specification, `coder` changed code, `code-reviewer` looked for defects, and `verify` gathered readiness evidence. A hook is different: it is a deterministic command automatically triggered by an agent event, independently of the model's reasoning. I did not add project-specific hooks; the repeated validation procedure was made explicit in `phase6-validate.ps1`, so it could be invoked at the right workflow point and retain its full result.

**Which tasks suit subagents, and what are the risks?**
Independent, read-only work: exploration and review. Implementation touched shared files, so it stayed with one agent at a time; the fresh-context review was a separate session, which gave the same isolation without concurrent edits.

**What is MCP, and what are its risks?**
An open protocol that lets a client use tools exposed by servers. The connection from the cloud agent to the reviewer's computer worked through such a bridge: files were staged and committed through tools with path and depth limits. Its tool descriptions occupy context, and an untrusted server would be a channel for code execution and injection.

**Which data must not be sent to an LLM, and how are secrets handled?**
Secrets, keys, personal data, and data under NDA. No credentials were needed or used; validation included a targeted scan for private-key headers and common token formats.

**What are the risks of AI-generated code, and how should it be checked before merge?**
Ordinary vulnerabilities, missed edge cases, and confident but wrong claims. Here: review against the specification, tests with real parsers, approval baselines, deliberate regressions to prove tests can fail, and an independent check that the patches reproduce the validated tree. The review still found five reporter defects in code that had passed all its tests.

**What is prompt injection, and what is indirect injection?**
Input that takes over the model's instructions; indirect injection arrives through data such as a README, a log, or a web page. The contract treats source files, issues, logs, and web pages as untrusted data, and only the reviewer's chat messages count as instructions.

**How do you debug failing AI workflows and control their cost?**
Look at the recorded steps and reproduce the failing one in isolation. Every validation run left a `summary.txt` with environment, Git state, exit codes, and test totals; the fatal-test timeout was investigated with an isolated run and `ctest --repeat until-fail:10`.

**Why standardize AI workflows across a team?**
Shared gates, artifact templates, and scripts make the results comparable and reviewable regardless of which agent or developer did the work. This task changed agents mid-way without changing the process.
