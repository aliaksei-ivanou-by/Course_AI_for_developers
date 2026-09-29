#!/usr/bin/env python3
"""Safely install or refresh the minimal repository-local accelerator payload."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True
from embacc_resources import (  # noqa: E402
    PACKAGE_VERSION,
    ResourceError,
    materialize_resources,
    parse_tools,
    path_issue,
    sha256,
)

SOURCE_ROOT = Path(__file__).resolve().parents[1]
STATE_NAME = ".accelerator-install.json"


class InstallError(RuntimeError):
    pass


@dataclass(frozen=True)
class Action:
    kind: str
    relative: Path
    source: Path | None = None
    reason: str = ""


def _safe_relative(raw: str) -> Path:
    candidate = PurePosixPath(raw)
    if candidate.is_absolute() or not candidate.parts or ".." in candidate.parts:
        raise InstallError(f"unsafe install-state path: {raw}")
    return Path(*candidate.parts)


def load_state(target: Path) -> dict[str, object] | None:
    path = target / STATE_NAME
    issue = path_issue(target, path)
    if issue:
        raise InstallError(f"unsafe install state path: {issue}")
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise InstallError(f"unsafe {STATE_NAME}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise InstallError(f"invalid {STATE_NAME}: {exc}") from exc
    if not isinstance(data, dict):
        raise InstallError(f"unsupported or invalid {STATE_NAME}")
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        raise InstallError(f"invalid {STATE_NAME}: version must be a non-empty string")
    tools = data.get("tools")
    files = data.get("files")
    if not isinstance(tools, list) or not all(isinstance(item, str) for item in tools):
        raise InstallError(f"invalid {STATE_NAME}: tools must be a string list")
    try:
        if list(parse_tools(",".join(tools))) != tools:
            raise InstallError(f"invalid {STATE_NAME}: tools are duplicated or unordered")
    except ResourceError as exc:
        raise InstallError(str(exc)) from exc
    if not isinstance(files, dict):
        raise InstallError(f"invalid {STATE_NAME}: files must be an object")
    for raw, entry in files.items():
        _safe_relative(raw)
        digest = entry.get("sha256") if isinstance(entry, dict) else entry
        if not isinstance(digest, str) or len(digest) != 64:
            raise InstallError(f"invalid hash for {raw}")
    return data


def _previous_hashes(state: dict[str, object] | None) -> dict[Path, str]:
    if not state:
        return {}
    files = state["files"]
    assert isinstance(files, dict)
    result: dict[Path, str] = {}
    for raw, entry in files.items():
        digest = entry.get("sha256") if isinstance(entry, dict) else entry
        assert isinstance(digest, str)
        result[_safe_relative(raw)] = digest
    return result


def _require_git_root(target: Path) -> None:
    result = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise InstallError("target must be the root of a Git repository")
    actual = Path(result.stdout.strip()).resolve()
    if actual != target.resolve():
        raise InstallError(f"target is not the Git root; actual root is {actual}")


def _git_dirty(target: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(target), "status", "--porcelain=v1"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise InstallError("unable to inspect target Git status")
    return bool(result.stdout.strip())


def _stage(selected: tuple[str, ...], parent: Path) -> dict[Path, Path]:
    stage = parent / "stage"
    try:
        materialize_resources(SOURCE_ROOT, stage, selected)
    except ResourceError as exc:
        raise InstallError(str(exc)) from exc
    desired: dict[Path, Path] = {}
    for source in sorted(stage.rglob("*")):
        if source.is_symlink():
            raise InstallError(f"symbolic link produced in install stage: {source}")
        if source.is_file():
            desired[source.relative_to(stage)] = source
    return desired


def plan_install(
    target: Path,
    desired: dict[Path, Path],
    state: dict[str, object] | None,
) -> list[Action]:
    actions: list[Action] = []
    previous = _previous_hashes(state)

    for relative, source in sorted(desired.items(), key=lambda item: item[0].as_posix()):
        path = target / relative
        issue = path_issue(target, path)
        if issue:
            actions.append(Action("CONFLICT", relative, source, issue))
            continue
        if not path.exists():
            actions.append(Action("CREATE", relative, source))
            continue
        if not path.is_file():
            actions.append(Action("CONFLICT", relative, source, "target is not a regular file"))
            continue

        current = sha256(path)
        wanted = sha256(source)
        if current == wanted:
            actions.append(Action("KEEP", relative, source))
        elif previous.get(relative) == current:
            actions.append(Action("UPDATE", relative, source))
        else:
            reason = "locally modified managed file" if relative in previous else "pre-existing client file"
            actions.append(Action("CONFLICT", relative, source, reason))

    for relative, old_hash in sorted(previous.items(), key=lambda item: item[0].as_posix()):
        if relative in desired:
            continue
        path = target / relative
        issue = path_issue(target, path)
        if issue or not path.is_file():
            actions.append(Action("RELEASE", relative, reason=issue or "already absent/non-file"))
        elif sha256(path) == old_hash:
            actions.append(Action("REMOVE", relative, reason="no longer selected or packaged"))
        else:
            actions.append(Action("RELEASE", relative, reason="preserving locally modified stale file"))
    return actions


def print_plan(target: Path, selected: tuple[str, ...], actions: list[Action], mode: str) -> None:
    print(f"ACCELERATOR {mode.upper()} PLAN")
    print(f"Target: {target}")
    print("Tools: " + (", ".join(selected) if selected else "none"))
    for action in actions:
        if action.kind != "KEEP":
            suffix = f" - {action.reason}" if action.reason else ""
            print(f"{action.kind:<8} {action.relative.as_posix()}{suffix}")
    kinds = ("CREATE", "UPDATE", "REMOVE", "RELEASE", "KEEP", "CONFLICT")
    print("Summary: " + ", ".join(f"{kind.lower()}={sum(a.kind == kind for a in actions)}" for kind in kinds))


def _state_content(target: Path, selected: tuple[str, ...], actions: list[Action]) -> dict[str, object]:
    files = {
        action.relative.as_posix(): sha256(target / action.relative)
        for action in actions
        if action.kind in {"CREATE", "UPDATE", "KEEP"}
    }
    return {"version": PACKAGE_VERSION, "tools": list(selected), "files": dict(sorted(files.items()))}


def _prune_empty_parents(target: Path, relatives: list[Path]) -> None:
    parents = {parent for rel in relatives for parent in (target / rel).parents if parent != target}
    for directory in sorted(parents, key=lambda path: len(path.parts), reverse=True):
        if not path_issue(target, directory):
            try:
                directory.rmdir()
            except OSError:
                pass


def apply_install(target: Path, selected: tuple[str, ...], actions: list[Action]) -> None:
    state_path = target / STATE_NAME
    state_temp = target / f"{STATE_NAME}.tmp"
    if path_issue(target, state_temp) or state_temp.exists() or state_temp.is_symlink():
        raise InstallError(f"unsafe/existing temporary state file: {state_temp}")

    with tempfile.TemporaryDirectory(prefix="acc-install-rollback-") as td:
        backup = Path(td)
        created: list[Path] = []
        replaced: list[Path] = []
        for action in actions:
            if action.kind not in {"UPDATE", "REMOVE"}:
                continue
            path = target / action.relative
            if path.is_file():
                destination = backup / action.relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
                replaced.append(action.relative)
        state_backup = backup / STATE_NAME
        if state_path.is_file():
            shutil.copy2(state_path, state_backup)

        try:
            for action in actions:
                path = target / action.relative
                if action.kind == "CREATE":
                    assert action.source is not None
                    path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(action.source, path)
                    created.append(action.relative)
                elif action.kind == "UPDATE":
                    assert action.source is not None
                    shutil.copy2(action.source, path)
                elif action.kind == "REMOVE":
                    path.unlink()

            for action in actions:
                if action.kind in {"CREATE", "UPDATE", "KEEP"}:
                    assert action.source is not None
                    if sha256(target / action.relative) != sha256(action.source):
                        raise InstallError(f"post-install verification failed: {action.relative}")

            state_temp.write_text(
                json.dumps(_state_content(target, selected, actions), indent=2) + "\n",
                encoding="utf-8",
            )
            state_temp.replace(state_path)
        except Exception:
            state_temp.unlink(missing_ok=True)
            for relative in reversed(created):
                (target / relative).unlink(missing_ok=True)
            for relative in replaced:
                source = backup / relative
                destination = target / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            if state_backup.is_file():
                shutil.copy2(state_backup, state_path)
            else:
                state_path.unlink(missing_ok=True)
            raise

    _prune_empty_parents(target, [a.relative for a in actions if a.kind == "REMOVE"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="existing client Git repository root")
    parser.add_argument("--tools", help="comma-separated integrations; defaults to previous selection, or none")
    parser.add_argument("--dry-run", action="store_true", help="show the plan without writes")
    parser.add_argument("--allow-dirty", action="store_true", help="allow writes in an already-dirty target repository")
    args = parser.parse_args()

    try:
        target = Path(args.target).resolve()
        if not target.is_dir():
            raise InstallError(f"target directory does not exist: {target}")
        _require_git_root(target)
        source = SOURCE_ROOT.resolve()
        if source == target or source.is_relative_to(target) or target.is_relative_to(source):
            raise InstallError("run installation from a separate accelerator checkout/package")

        state = load_state(target)
        if _git_dirty(target) and not args.allow_dirty and not args.dry_run:
            raise InstallError("target working tree is dirty; commit/stash it or use --allow-dirty after review")
        if args.tools is not None:
            selected = parse_tools(args.tools)
        elif state:
            selected = tuple(state["tools"])
        else:
            selected = ()

        with tempfile.TemporaryDirectory(prefix="acc-install-stage-") as td:
            desired = _stage(selected, Path(td))
            actions = plan_install(target, desired, state)
            print_plan(target, selected, actions, "refresh" if state else "install")
            if any(action.kind == "CONFLICT" for action in actions):
                print("ACCELERATOR INSTALL: CONFLICT - no files changed", file=sys.stderr)
                return 2
            if args.dry_run:
                print("DRY RUN: no files changed")
                return 0
            apply_install(target, selected, actions)

        print("ACCELERATOR INSTALL: PASS")
        return 0
    except (InstallError, ResourceError, OSError) as exc:
        print(f"ACCELERATOR INSTALL: FAIL - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
