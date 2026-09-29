#!/usr/bin/env python3
"""Regression test for scripts/embacc_selfupdate.py.

A real `pixi global update` has machine-global side effects (network access,
mutates the developer's actual `~/.pixi` state) -- this test must never
trigger one for real. Two techniques, matched to what's actually safe:

1. Direct module import with `subprocess.run` monkeypatched, for every
   branch of the actual decision logic (zero/one/many pixi environments
   exposing `embacc`, success/no-op/failure reporting).
2. Two real-subprocess smoke checks that are side-effect-free by
   construction: `--dry-run` (never calls `pixi global update`) and a
   PATH with no `pixi` on it at all (fails before calling anything).

The pure-logic and missing-pixi checks always run. CLI dispatch is checked
from a source checkout, and only the real `--dry-run` smoke check is omitted
when pixi is not on PATH, as may be the case on CI's ubuntu-latest image.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "embacc_selfupdate.py"

sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
import embacc_selfupdate as su  # noqa: E402


class FakeResult:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def envs_json(*names_with_embacc: str, extra: list[dict] | None = None) -> str:
    environments = [
        {
            "name": name,
            "dependencies": [{"name": su.PACKAGE_NAME, "version": "2.5.0"}],
            "exposed": [{"exposed_name": "embacc", "executable": "embacc"}],
        }
        for name in names_with_embacc
    ]
    environments.extend(extra or [])
    return json.dumps(environments)


def check_zero_matches(failures: list[str]) -> None:
    original = su.subprocess.run
    su.subprocess.run = lambda *a, **k: FakeResult(stdout=envs_json())
    try:
        try:
            su.find_embacc_environment("pixi")
            failures.append("find_embacc_environment should raise when no environment exposes embacc")
        except su.SelfUpdateError as exc:
            if "not managed by a pixi global install" not in str(exc):
                failures.append(f"unexpected zero-match message: {exc}")
    finally:
        su.subprocess.run = original


def check_multiple_matches(failures: list[str]) -> None:
    original = su.subprocess.run
    su.subprocess.run = lambda *a, **k: FakeResult(stdout=envs_json("env-a", "env-b"))
    try:
        try:
            su.find_embacc_environment("pixi")
            failures.append("find_embacc_environment should raise when multiple environments expose embacc")
        except su.SelfUpdateError as exc:
            if "env-a" not in str(exc) or "env-b" not in str(exc):
                failures.append(f"ambiguous-match message should name both candidates: {exc}")
    finally:
        su.subprocess.run = original


def check_list_failure(failures: list[str]) -> None:
    original = su.subprocess.run
    su.subprocess.run = lambda *a, **k: FakeResult(returncode=1, stderr="boom")
    try:
        try:
            su.find_embacc_environment("pixi")
            failures.append("find_embacc_environment should raise when `pixi global list` fails")
        except su.SelfUpdateError as exc:
            if "boom" not in str(exc):
                failures.append(f"list-failure message should include pixi's stderr: {exc}")
    finally:
        su.subprocess.run = original

    su.subprocess.run = lambda *a, **k: FakeResult(stdout="not json")
    try:
        try:
            su.find_embacc_environment("pixi")
            failures.append("find_embacc_environment should raise on unparseable JSON")
        except su.SelfUpdateError:
            pass
    finally:
        su.subprocess.run = original


def check_wrong_package_and_shared_environment(failures: list[str]) -> None:
    original = su.subprocess.run
    wrong_package = {
        "name": "unrelated-tools",
        "dependencies": [{"name": "something-else", "version": "1.0"}],
        "exposed": [{"exposed_name": "embacc", "executable": "not-really-embacc"}],
    }
    su.subprocess.run = lambda *a, **k: FakeResult(stdout=envs_json(extra=[wrong_package]))
    try:
        try:
            su.find_embacc_environment("pixi")
            failures.append("an environment exposing `embacc` without the embacc package should be rejected")
        except su.SelfUpdateError as exc:
            if "unrelated environment" not in str(exc):
                failures.append(f"unexpected wrong-package message: {exc}")
    finally:
        su.subprocess.run = original

    shared_environment = {
        "name": "shared-tools",
        "dependencies": [
            {"name": su.PACKAGE_NAME, "version": "2.5.0"},
            {"name": "another-tool", "version": "1.0"},
        ],
        "exposed": [{"exposed_name": "embacc", "executable": "embacc"}],
    }
    su.subprocess.run = lambda *a, **k: FakeResult(stdout=envs_json(extra=[shared_environment]))
    try:
        try:
            su.find_embacc_environment("pixi")
            failures.append("a shared environment should be rejected before an environment-wide update")
        except su.SelfUpdateError as exc:
            if "whole environment" not in str(exc) or "another-tool" not in str(exc):
                failures.append(f"unexpected shared-environment message: {exc}")
    finally:
        su.subprocess.run = original


def check_single_match(failures: list[str]) -> None:
    original = su.subprocess.run
    su.subprocess.run = lambda *a, **k: FakeResult(stdout=envs_json("cpp-embedded-accelerator"))
    try:
        found = su.find_embacc_environment("pixi")
        if found != ("cpp-embedded-accelerator", "2.5.0"):
            failures.append(f"find_embacc_environment picked the wrong environment: {found!r}")
    finally:
        su.subprocess.run = original


def run_main_with_stubs(
    list_results: list[FakeResult],
    update_result: FakeResult | None,
    *,
    argv: list[str] | None = None,
) -> tuple[int, str, str, list[list[str]]]:
    """Run su.main() with pixi discovery/update stubbed."""
    calls: list[list[str]] = []
    list_iter = iter(list_results)

    def fake_run(command, *a, **k):
        calls.append(list(command))
        if command[1:] == ["global", "list", "--json"]:
            return next(list_iter)
        if command[1:3] == ["global", "update"]:
            assert update_result is not None
            return update_result
        raise AssertionError(f"unexpected subprocess.run call: {command}")

    original_run = su.subprocess.run
    original_which = su.shutil.which
    original_argv = sys.argv
    su.subprocess.run = fake_run
    su.shutil.which = lambda name: "pixi" if name == "pixi" else "embacc"
    sys.argv = ["embacc_selfupdate.py", *(argv or [])]

    from io import StringIO
    out, err = StringIO(), StringIO()
    original_stdout, original_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = out, err
    try:
        rc = su.main()
    finally:
        su.subprocess.run = original_run
        su.shutil.which = original_which
        sys.argv = original_argv
        sys.stdout, sys.stderr = original_stdout, original_stderr
    return rc, out.getvalue(), err.getvalue(), calls


def check_success_no_op(failures: list[str]) -> None:
    rc, out, _err, calls = run_main_with_stubs(
        [
            FakeResult(stdout=envs_json("cpp-embedded-accelerator")),
            FakeResult(stdout=envs_json("cpp-embedded-accelerator")),
        ],
        FakeResult(returncode=0),
    )
    if rc != 0 or "installed version remains 2.5.0" not in out or "already up to date" in out:
        failures.append(f"same-version update should report completion without claiming a no-op: rc={rc} out={out!r}")
    if ["pixi", "global", "update", "cpp-embedded-accelerator"] not in calls:
        failures.append(f"same-version update did not invoke the expected pixi command: {calls!r}")


def check_success_version_bump(failures: list[str]) -> None:
    before = envs_json("cpp-embedded-accelerator")
    after = json.dumps(
        [
            {
                "name": "cpp-embedded-accelerator",
                "dependencies": [{"name": su.PACKAGE_NAME, "version": "2.7.3"}],
                "exposed": [{"exposed_name": "embacc", "executable": "embacc"}],
            }
        ]
    )
    rc, out, _err, _calls = run_main_with_stubs(
        [FakeResult(stdout=before), FakeResult(stdout=after)],
        FakeResult(returncode=0),
    )
    if rc != 0 or "2.5.0 -> 2.7.3" not in out:
        failures.append(f"version-bump update should report old -> new: rc={rc} out={out!r}")


def check_update_failure(failures: list[str]) -> None:
    rc, _out, err, _calls = run_main_with_stubs(
        [FakeResult(stdout=envs_json("cpp-embedded-accelerator"))],
        FakeResult(returncode=3),
    )
    if rc != 3 or "FAIL" not in err:
        failures.append(f"a failing `pixi global update` should propagate its exit code and print FAIL: rc={rc} err={err!r}")


def check_dry_run_logic(failures: list[str]) -> None:
    rc, out, err, calls = run_main_with_stubs(
        [FakeResult(stdout=envs_json("cpp-embedded-accelerator"))],
        None,
        argv=["--dry-run"],
    )
    if rc != 0 or err or "DRY RUN: no changes made" not in out:
        failures.append(f"stubbed dry-run failed: rc={rc} out={out!r} err={err!r}")
    if calls != [["pixi", "global", "list", "--json"]]:
        failures.append(f"dry-run should only inspect the pixi manifest, got calls: {calls!r}")


def check_cli_dispatch(failures: list[str]) -> None:
    if not (ROOT / "src" / "embacc" / "cli.py").is_file():
        return
    sys.path.insert(0, str(ROOT / "src"))
    from embacc import cli

    captured: list[tuple[str, list[str]]] = []
    original_run = cli._run
    cli._run = lambda script, args: captured.append((script, args)) or 0
    try:
        rc = cli.main(["self-update", "--dry-run"])
    finally:
        cli._run = original_run
    expected = [("embacc_selfupdate.py", ["--dry-run"])]
    if rc != 0 or captured != expected:
        failures.append(f"CLI did not dispatch self-update --dry-run correctly: rc={rc} calls={captured!r}")


def check_dry_run_smoke(failures: list[str]) -> None:
    """Real subprocess call -- safe because --dry-run never calls `pixi global update`."""
    if not shutil.which("pixi"):
        return
    run_options = {"text": True, "encoding": "utf-8", "errors": "replace", "capture_output": True, "check": False}
    before = subprocess.run(["pixi", "global", "list", "--json"], **run_options)
    result = subprocess.run([sys.executable, str(SCRIPT), "--dry-run"], **run_options)
    after = subprocess.run(["pixi", "global", "list", "--json"], **run_options)
    if before.stdout != after.stdout:
        failures.append("embacc_selfupdate.py --dry-run must not change `pixi global list --json` output")
    if result.returncode not in (0, 1):
        failures.append(f"--dry-run should exit 0 (found) or 1 (not managed by pixi), got {result.returncode}: {result.stdout!r} {result.stderr!r}")
    if result.returncode == 0 and "DRY RUN: no changes made" not in result.stdout:
        failures.append(f"--dry-run success output missing expected marker: {result.stdout!r}")


def check_pixi_missing_smoke(failures: list[str]) -> None:
    """Real subprocess call with PATH cleared of pixi -- fails before touching anything."""
    with tempfile.TemporaryDirectory(prefix="embacc-no-pixi-") as empty_path_dir:
        env = {**os.environ, "PATH": empty_path_dir}
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            env=env,
        )
    if result.returncode != 1 or "pixi" not in result.stderr.lower() or "PATH" not in result.stderr:
        failures.append(f"missing-pixi run should fail clearly: rc={result.returncode} stderr={result.stderr!r}")


def main() -> int:
    failures: list[str] = []
    source_cli_available = (ROOT / "src" / "embacc" / "cli.py").is_file()
    check_zero_matches(failures)
    check_multiple_matches(failures)
    check_list_failure(failures)
    check_wrong_package_and_shared_environment(failures)
    check_single_match(failures)
    check_success_no_op(failures)
    check_success_version_bump(failures)
    check_update_failure(failures)
    check_dry_run_logic(failures)
    check_cli_dispatch(failures)
    check_pixi_missing_smoke(failures)
    if shutil.which("pixi"):
        check_dry_run_smoke(failures)
    else:
        print("EMBACC SELF-UPDATE TEST: NOTE (pixi not on PATH; real dry-run smoke check not run)")

    if failures:
        print("EMBACC SELF-UPDATE TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    cli_coverage = ", CLI dispatch" if source_cli_available else ""
    print(f"EMBACC SELF-UPDATE TEST: PASS (safe environment discovery{cli_coverage}, "
          "success/version/failure reporting, dry-run no-op, and missing-pixi failure all behave correctly)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
