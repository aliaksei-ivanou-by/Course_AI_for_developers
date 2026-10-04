# Phase 1 Baseline

Status: Complete — accepted by the human reviewer. Baselines: `basic-tests` 82/82 (run 5), `all-tests` 145/145 (run 6)  
Contract: [00-task-contract.md](00-task-contract.md)

## Repository

| Item | Value |
| --- | --- |
| Repository | https://github.com/catchorg/Catch2.git |
| Tag | `v3.16.0` |
| Commit | `317ac1ed4c0bb6e6b91eafc817e05c488feffcb3` |
| Local checkout | `Implementation/workspace/Catch2` (ignored by the course repository). The course repository was moved from `C:\Users\User\git\Personal\` to `C:\git\Personal\` after run 2; Git state is unaffected |
| Build directory | `C:\build\Course_AI\catch2\basic-test-build` from run 5, and `C:\build\Course_AI\catch2\debug-build` for the `all-tests` preset (outside the course repository; allowed by the contract's permission boundary). Run 4 used `C:\b\catch2-retry\basic-test-build`; the root was renamed afterwards at the reviewer's request |
| Feature branch | `task/retry-failed`, created from the tag after both gates passed |
| Local exclude | `basic-test-build/` added to the clone's `.git/info/exclude` for the in-tree runs 1–3; Catch2's `.gitignore` does not cover it. Harmless once the build moved out of tree |

## Environment

| Tool | Version |
| --- | --- |
| OS | Microsoft Windows 11 Pro (NT 10.0.26300.0) |
| PowerShell | 5.1.26100.9549 |
| Git | 2.56.0.windows.1 |
| CMake / CTest | 4.3.4 |
| Python | 3.13.14 |
| Generator | Visual Studio 18 2026, Community edition (x64 host and target) |
| Compiler | MSVC 19.50.35718.0 (toolset 14.50.35717) |
| Windows SDK | 10.0.26100.0 |

## Commands

Source of the commands: Catch2 `v3.16.0` `docs/contributing.md`, read before the commands were chosen. The configure command is the documented basic-tests command; only the `-B` path changed from run 4. The documentation gives build and test commands only for the `all-tests` snippet (`cmake --build debug-build`, `ctest -j 4 --output-on-failure -C Debug --test-dir debug-build`), so the basic-suite commands follow that pattern with two additions: `--config Debug`, required by the multi-configuration Visual Studio generator, and `--parallel`, which only affects build speed. Repository commands run from `Implementation/`; CMake commands run from the Catch2 root.

| Step | Command | Exit | Result |
| --- | --- | ---: | --- |
| Clone | `git clone https://github.com/catchorg/Catch2.git workspace/Catch2` | 0 | Cloned |
| Checkout | `git -C workspace/Catch2 checkout v3.16.0` | 0 | `HEAD is now at 317ac1ed v3.16.0` |
| Gate | `git -C workspace/Catch2 describe --exact-match --tags HEAD` | — | `v3.16.0` (output recorded; exit code not captured) |
| Gate | `git -C workspace/Catch2 status --short` | — | Empty output, clean (exit code not captured) |
| Branch | `git -C workspace/Catch2 switch -c task/retry-failed` | 0 | Branch created |
| Configure (run 1) | `cmake -B basic-test-build -S . -DCMAKE_BUILD_TYPE=Debug --preset basic-tests` | 1 | Failed in CMake's compiler check (path length); see below |
| Configure (runs 2–3, through `subst W:`) | same | 0 | Configured |
| Build (runs 2–3) | `cmake --build basic-test-build --config Debug --parallel` | 0 | Built (run 2: 78 s; run 3: 170 s) |
| Test (runs 2–3) | `ctest --test-dir basic-test-build -C Debug --output-on-failure` | 8 | 81/82 passed; `ApprovalTests` failed (caused by `subst`; see below) |
| Configure (run 4) | `cmake -B C:\b\catch2-retry\basic-test-build -S . -DCMAKE_BUILD_TYPE=Debug --preset basic-tests` | 0 | Configured in 5 s |
| Build (run 4) | `cmake --build C:\b\catch2-retry\basic-test-build --config Debug --parallel` | 0 | Built in 141 s; no compiler warnings or errors |
| Test (run 4) | `ctest --test-dir C:\b\catch2-retry\basic-test-build -C Debug --output-on-failure` | 0 | **82/82 passed** in 29.8 s |
| Configure (run 5) | `cmake -B C:\build\Course_AI\catch2\basic-test-build -S . -DCMAKE_BUILD_TYPE=Debug --preset basic-tests` | 0 | Configured in 5 s |
| Build (run 5) | `cmake --build C:\build\Course_AI\catch2\basic-test-build --config Debug --parallel` | 0 | Built in 132 s; no compiler warnings or errors |
| Test (run 5) | `ctest --test-dir C:\build\Course_AI\catch2\basic-test-build -C Debug --output-on-failure` | 0 | **82/82 passed** in 23.8 s |

Full logs, ignored by Git, under `evidence/raw/phase1/`: `run-01/` to `run-05/` for runs 1–5 (run 3 is an unchanged rerun of run 2 after the repository move; run 5 is the recorded baseline) and `run-03-precheck-stop/`, a first attempt at run 3 that the script stopped before building because the run-2 build directory still existed. Exit codes come from each run's `summary.txt`. The folders were renamed from timestamps to run numbers after the runs, so paths printed inside the older logs still show the original folder names.

## Run 1 Blocker: Windows Path Length

CMake's "Check for working CXX compiler" step failed with:

```text
FileTracker : error FTK1011: could not create the new file tracking log file:
C:\Users\User\git\Personal\Course_AI_for_developers\09 Practical Tasks\01 C++ - Retry Failed Tests in Catch2\Implementation\workspace\Catch2\basic-test-build\CMakeFiles\CMakeScratch\TryCompile-p38sa5\cmTC_ad88d.dir\Debug\cmTC_ad88d.tlog\link-cvtres.read.1.tlog.
The system cannot find the path specified.
```

The compiler itself ran (`cl` compiled `testCXXCompiler.cxx`); only MSBuild's file tracker failed at the link step. The tracking-log path is 260 characters, which reaches the Windows `MAX_PATH` limit; the checkout root alone is 140 characters. This is an environment limitation, not a Catch2 defect, and it occurred before any change to Catch2.

## Runs 2–3: `ApprovalTests` Failure Caused by `subst`

The first workaround mapped `workspace\Catch2` to drive `W:` with `subst`. Configure and build succeeded, and 81 of 82 CTest tests passed. `ApprovalTests` failed with "Results differed": 14 of the 19 approval comparisons made by `approvalTests.py` differed (`console.std`, `console.swa4`, and the `.sw` and `.sw.multi` baselines of the console, compact, JUnit, SonarQube, TeamCity, and XML reporters). The other 5 matched: the TAP and Automake `.sw` and `.sw.multi` baselines and `default.sw.multi`; their approved output contains no source file paths (checked for `tap.sw.approved.txt`: no `.tests.cpp` occurrences).

Cause: `tools/scripts/approvalTests.py` derives the Catch2 root with `os.path.realpath`, which resolves the `subst` drive to the real `C:\...` path, and then strips that root from reporter file paths. `SelfTest.exe` was built from `W:\` and prints `W:/tests/SelfTest/...`, so the prefix was not stripped and every source location kept `W:/` (for example `-Message.tests.cpp:<line number>` versus `+W:/Message.tests.cpp:<line number>`).

Check: for each of the 14 differing baselines, every removed line matches an added line once `W:/` is deleted (multiset comparison of the `-` and `+` lines in the run-3 CTest log; zero unexplained lines in any baseline). Run 3 produced the same CTest log as run 2 apart from timings (a line diff of the two logs leaves no difference outside the timing values). Runs 4 and 5, built from the real source path, pass `ApprovalTests`, which confirms the cause.

This is an artifact of the workaround, not a Catch2 baseline defect. Side effect: failing comparisons leave `tests/SelfTest/Baselines/*.unapproved.txt` files (ignored by Git). They must be removed before the next run, because `approve.py` would otherwise accept them as baselines.

## Decision: Out-of-Tree Build Directory at a Short Path

| Option | Assessment |
| --- | --- |
| Keep the source in `workspace\Catch2` and put build directories under `C:\build\Course_AI\catch2\` (first `C:\b\catch2-retry\`, renamed after run 4 for a clearer name) | **Chosen** (approved by the reviewer and added to the contract's permission boundary). Source paths stay real, so approval normalization works; build paths stay short enough for later suites |
| `subst` drive mapping | **Rejected after runs 2–3**: breaks `ApprovalTests` as described above |
| In-tree build after the repository move (checkout path now 129 characters) | The compiler-check log path would be 249 characters, so the basic suite would probably fit, but the `all-tests` preset builds `ExtraTests` targets with names up to 52 characters, giving tracker paths of about 300 characters (an estimate from target names, not measured; MSBuild may shorten some intermediate names) |
| Enable Windows long paths | Not tried: a machine-wide registry change outside the task scope, and it is not established that MSBuild's file tracker honors it |
| Switch to the Ninja generator | Not tried: changes the toolchain path, still risks long object paths, and is unnecessary with a short build root |

`scripts/phase1-baseline.ps1` now builds out of tree, stops if the build directory already exists or if stale `*.unapproved.txt` files are present, and lists any new `*.unapproved.txt` files after CTest. The old `workspace\Catch2\basic-test-build` directory (configured for `W:`) and the stale `*.unapproved.txt` files were removed before run 4.

## Run 4: First Clean Run

Commands, from `Implementation/`:

```powershell
Remove-Item -Recurse -Force '.\workspace\Catch2\basic-test-build'
Get-ChildItem '.\workspace\Catch2\tests\SelfTest\Baselines' -Filter *.unapproved.txt | Remove-Item
powershell -ExecutionPolicy Bypass -File .\scripts\phase1-baseline.ps1
```

| Item | Result |
| --- | --- |
| Paths | Implementation 112 characters, checkout 129, build directory 34 |
| Repository state before the build | Commit `317ac1ed…`, exact tag `v3.16.0`, branch `task/retry-failed`, clean |
| Configure | Exit 0. MSVC 19.50.35718.0, Windows SDK 10.0.26100.0, Python 3.13.14 found (Catch2's `CMakeLists.txt` requires Python 3 when tests are built, so a missing interpreter would fail configure rather than skip tests). `HAVE_FLAG__Wno_missing_noreturn` failed (expected: a GCC/Clang flag) |
| Build | Exit 0, 141 s, no compiler warnings or errors |
| CTest | Exit 0. **100% tests passed, 0 tests failed out of 82**, 29.77 s. `ApprovalTests` passed in 10.96 s; four `uses-python` tests ran |
| Approval output | No `*.unapproved.txt` files after the run |
| Source tree after the build | `git status --short` clean |
| Course repository | `git check-ignore -v workspace/Catch2` → `Implementation/.gitignore:2:workspace/`; the build tree is outside the repository |

## Run 5: Baseline at the Final Build Root

A CMake build tree records its own path and cannot be moved, so the build was recreated after the rename. From `Implementation/`:

```powershell
Remove-Item -Recurse -Force 'C:\b\catch2-retry'
powershell -ExecutionPolicy Bypass -File .\scripts\phase1-baseline.ps1
```

Result: identical to run 4. Build directory path 42 characters; configure, build, and CTest exit 0; no compiler warnings or errors; **100% tests passed, 0 tests failed out of 82** (23.78 s, `ApprovalTests` passed in 8.23 s); no `*.unapproved.txt` files; `git status --short` clean; `workspace/Catch2` ignored by the course repository. This run is the reference baseline for later phases.

State checked from the device after run 5: `workspace\Catch2\.git\HEAD` points to `refs/heads/task/retry-failed`; `tests\SelfTest\Baselines\` contains only the 20 tracked `*.approved.txt` files (19 used by `approvalTests.py`, plus `automake.std.approved.txt`, which that script does not compare); the old in-tree `basic-test-build` directory no longer exists.

Independent checks:

- `git ls-remote https://github.com/catchorg/Catch2.git refs/tags/v3.16.0*`: the annotated tag object `fd79eadb…` peels to commit `317ac1ed4c0bb6e6b91eafc817e05c488feffcb3`, the commit recorded above.
- `CMakePresets.json`, `docs/contributing.md`, `tools/scripts/scriptCommon.py`, and `tools/scripts/approvalTests.py` at the tag were compared with the statements in this artifact (preset names and cache variables, documented commands, `os.path.realpath` root detection, 19 approval comparisons).
- Build logs of runs 3–5 contain no `warning` or `error` lines (the run-2 build log was not scanned); the run-1 configure log contains the quoted `FTK1011` errors and shows `cl` compiling `testCXXCompiler.cxx` before the failing `Link:` step.
- Reviewer's commands after run 5: `git -C workspace/Catch2 status --short --ignored` lists only `tools/scripts/__pycache__/` (Python bytecode written when CTest runs Catch2's Python test scripts; ignored, consistent with the `*.pyc` rule in Catch2's `.gitignore`; not a source change). In the course repository, `git check-ignore -v` confirms that `evidence/raw/phase1` and `workspace/Catch2` are ignored, and `git status --short` shows only the Phase 0–1 deliverables (`README.md`, `artifacts/00-task-contract.md`, `artifacts/01-baseline.md`, `scripts/`) plus a stray `Claude outputs/` folder outside this task, which has since been removed.

## Notes for Later Phases

- `scripts/phase1-baseline.ps1` was tightened after run 5: it now exits with an error when CTest fails, stops if `origin` is not the official Catch2 URL, records the number of registered tests and warns if it differs from 82, and also checks that `evidence/raw/phase1` is ignored. These changes add checks only; configure, build, and test commands are unchanged from runs 4–5.
- Visual Studio is a multi-configuration generator: CMake warns that `CMAKE_BUILD_TYPE` is unused. The configuration is chosen by `--config Debug` and `-C Debug`; keep the Catch2 command unchanged for fidelity with `docs/contributing.md`.
- Later build directories (`debug-build` for the `all-tests` preset) go to `C:\build\Course_AI\catch2\` as well.
- The documented `all-tests` sequence first runs `tools/scripts/generateAmalgamatedFiles.py`, which rewrites the tracked `extras/catch_amalgamated.hpp` and `extras/catch_amalgamated.cpp`. Each file's header contains a `//  Generated: <current time>` line, so even on the unmodified tree the expected diff is exactly that one line per file; anything more (for example line endings, which `.gitattributes` normalizes with `* text=auto`) must be recorded as a baseline finding. Run 6 confirmed that only that line changes on this machine.

## Run 6: Full `all-tests` Suite

Commands from the `docs/contributing.md` all-tests snippet, run by `scripts/phase1-all-tests.ps1` from the Catch2 root (evidence: `run-06-all-tests/`):

```powershell
python tools/scripts/generateAmalgamatedFiles.py
cmake -B C:\build\Course_AI\catch2\debug-build -S . -DCMAKE_BUILD_TYPE=Debug --preset all-tests
cmake --build C:\build\Course_AI\catch2\debug-build --config Debug --parallel
ctest -j 4 --output-on-failure -C Debug --test-dir C:\build\Course_AI\catch2\debug-build
```

| Step | Exit | Result |
| --- | ---: | --- |
| Repository state before the run | — | Official origin, commit `317ac1ed…`, exact tag `v3.16.0`, branch `task/retry-failed`, clean |
| Amalgamation | 0 | 181 headers and 108 source files concatenated. `git diff --numstat`: one line changed in each of `extras/catch_amalgamated.hpp` and `extras/catch_amalgamated.cpp`; no changed line other than `Generated:`; no other file changed |
| Configure | 0 | 5 s. Build directory path 37 characters. Surrogate TUs, examples, and extra tests included; the same `HAVE_FLAG__Wno_missing_noreturn` and unused `CMAKE_BUILD_TYPE` messages as runs 4–5 |
| Build | 0 | 124 s, no errors, no path-length failures. 4 compiler warnings, all `D9025` (`overriding '/EHs' with '/EHs-'` and `'/EHc'` with `'/EHc-'`) in the `DisabledExceptions-DefaultHandler` and `DisabledExceptions-CustomHandler` extra tests, which deliberately build without exceptions; they are part of the baseline |
| CTest | 0 | **100% tests passed, 0 tests failed out of 145**, 147.65 s with `-j 4`. Includes `ApprovalTests` (passed), the CMake configuration and helper tests, benchmarking, thread-safety, and extra tests. Labels: 16 `uses-python` tests, 1 `uses-signals` test. No tests skipped or not run |
| Approval output | — | No `*.unapproved.txt` files |
| Source tree after the run | — | Only `extras/catch_amalgamated.cpp` and `extras/catch_amalgamated.hpp` modified, as expected |

The 145-test result is the reference for the broader suite in later phases. The path-length estimate for in-tree builds was not tested, because the build ran out of tree as decided above.

After reviewing the amalgamation check, the reviewer restored the two files with `git -C workspace/Catch2 restore extras/catch_amalgamated.hpp extras/catch_amalgamated.cpp`; `git -C workspace/Catch2 status --short` then printed nothing.

The summary prints the first status line as `M extras/...` without its leading space because the script trimmed command output; both files are unstaged working-tree changes (` M`). The scripts now keep leading whitespace.

## Gate Status

| Gate | Status |
| --- | --- |
| `describe --exact-match --tags HEAD` reports `v3.16.0` before the branch is created | ✅ Passed |
| Source tree clean at baseline | ✅ Passed: clean before every build and after every completed build (runs 2–5) |
| Baseline build and test results recorded honestly | ✅ Runs 1–3 (environment failures), runs 4–5 (`basic-tests`, 82/82), and run 6 (`all-tests`, 145/145) recorded |
| Source tree clean after the `all-tests` run | ✅ Passed: the regenerated amalgamated files were restored and `git status --short` is empty |
| Environment limitations documented | ✅ Path-length blocker, `subst` side effect, and the chosen layout recorded |
| Course repository ignores `workspace/` and build output | ✅ `workspace/` ignored; build output lives outside the repository |
