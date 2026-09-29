#!/usr/bin/env python3
"""Update embacc itself via its pixi global install.

embacc is distributed only via `pixi global install --git <url> --branch
main` (see README.md "Quick start") -- there is no PyPI package. This shells
out to `pixi global update <env>` for the dedicated pixi environment whose
exposed commands include `embacc` and whose sole explicit dependency is this
package, rather than reimplementing git/version resolution here. This updates the
embacc package itself; repository installation is handled separately by `embacc install`.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


PACKAGE_NAME = "cpp-embedded-accelerator"


class SelfUpdateError(RuntimeError):
    pass


def find_pixi() -> str:
    pixi = shutil.which("pixi")
    if not pixi:
        raise SelfUpdateError(
            "pixi was not found on PATH; embacc self-update requires the same pixi global install "
            "described in README.md 'Quick start' (`pixi global install --git <url> --branch main`)"
        )
    return pixi


def find_embacc_environment(pixi: str) -> tuple[str, str | None]:
    try:
        result = subprocess.run(
            [pixi, "global", "list", "--json"],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise SelfUpdateError(f"could not run `pixi global list --json`: {exc}") from exc
    if result.returncode != 0:
        raise SelfUpdateError(f"`pixi global list --json` failed: {(result.stderr or result.stdout).strip()}")
    try:
        environments = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SelfUpdateError(f"could not parse `pixi global list --json` output: {exc}") from exc
    if not isinstance(environments, list):
        raise SelfUpdateError("unexpected `pixi global list --json` output: expected a list of environments")

    exposed_matches: list[str] = []
    package_matches: list[tuple[str, str | None, list[str]]] = []
    for env in environments:
        if not isinstance(env, dict):
            continue
        exposed = env.get("exposed", [])
        if not isinstance(exposed, list):
            continue
        if any(isinstance(item, dict) and item.get("exposed_name") == "embacc" for item in exposed):
            name = env.get("name")
            if not isinstance(name, str) or not name:
                continue
            exposed_matches.append(name)

            dependencies = env.get("dependencies")
            if not isinstance(dependencies, list):
                continue
            package_dependency = next(
                (
                    item
                    for item in dependencies
                    if isinstance(item, dict) and item.get("name") == PACKAGE_NAME
                ),
                None,
            )
            if package_dependency is None:
                continue

            extra_dependencies: list[str] = []
            for item in dependencies:
                dependency_name = item.get("name") if isinstance(item, dict) else None
                if dependency_name == PACKAGE_NAME:
                    continue
                extra_dependencies.append(dependency_name if isinstance(dependency_name, str) else "<unknown>")
            version = package_dependency.get("version")
            package_matches.append((name, version if isinstance(version, str) else None, extra_dependencies))

    if not package_matches:
        if exposed_matches:
            raise SelfUpdateError(
                "a pixi global environment exposes `embacc`, but none declares the expected "
                f"`{PACKAGE_NAME}` dependency ({', '.join(sorted(exposed_matches))}); refusing to update "
                "an unrelated environment"
            )
        raise SelfUpdateError(
            "embacc is not managed by a pixi global install on this machine (no environment exposes "
            "`embacc`); self-update only supports that install path -- see README.md 'Quick start'"
        )
    if len(package_matches) > 1:
        raise SelfUpdateError(
            "more than one pixi global environment exposes `embacc` from the expected package ("
            + ", ".join(sorted(match[0] for match in package_matches))
            + "); "
            "run `pixi global update <env>` yourself for the one you mean"
        )

    name, version, extra_dependencies = package_matches[0]
    if extra_dependencies:
        raise SelfUpdateError(
            f"pixi environment `{name}` also contains other explicit dependencies "
            f"({', '.join(sorted(extra_dependencies))}); `pixi global update {name}` would update the "
            "whole environment, so self-update refuses to change unrelated tools. Install embacc in its "
            "own environment as shown in README.md, or update this shared environment manually"
        )
    return name, version


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="show the plan without updating anything")
    args = parser.parse_args()

    try:
        pixi = find_pixi()
        environment, before = find_embacc_environment(pixi)
    except SelfUpdateError as exc:
        print(f"EMBACC SELF-UPDATE: FAIL - {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("EMBACC SELF-UPDATE PLAN")
        print(f"Environment: {environment}")
        print(f"Current version: {before or 'unknown'}")
        print(f"Command: {pixi} global update {environment}")
        print("DRY RUN: no changes made")
        return 0

    try:
        result = subprocess.run([pixi, "global", "update", environment])
    except OSError as exc:
        print(f"EMBACC SELF-UPDATE: FAIL - could not run pixi: {exc}", file=sys.stderr)
        return 1
    if result.returncode != 0:
        print(
            f"EMBACC SELF-UPDATE: FAIL - `pixi global update {environment}` exited {result.returncode}",
            file=sys.stderr,
        )
        return result.returncode

    try:
        updated_environment, after = find_embacc_environment(pixi)
        if updated_environment != environment:
            after = None
    except SelfUpdateError:
        after = None

    if before and after and before != after:
        print(f"EMBACC SELF-UPDATE: PASS ({before or 'unknown'} -> {after})")
    elif after:
        print(f"EMBACC SELF-UPDATE: PASS (update completed; installed version remains {after})")
    else:
        print("EMBACC SELF-UPDATE: PASS (update ran, but the new version could not be confirmed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
