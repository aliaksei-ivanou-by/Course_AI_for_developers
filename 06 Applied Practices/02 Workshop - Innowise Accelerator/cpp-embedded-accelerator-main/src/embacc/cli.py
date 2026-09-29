"""Public ``embacc`` command.

The project workflow lives in ``embacc_native.py``.  This module intentionally
stays a thin dispatcher so command-line options are defined in one place
instead of being duplicated between the installed entry point and runtime.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from . import __version__

NATIVE_COMMANDS = {"setup", "run", "doctor", "refresh", "config", "reflect"}
PUBLIC_COMMANDS = (*sorted(NATIVE_COMMANDS), "install", "self-update", "version")

HELP = """\
usage: embacc [--version] <command> [options]

External project context for Claude Code, Codex, OpenCode, and Pi.
Run `embacc setup .` once, then bare `embacc` to launch the configured agent.

commands:
    setup        discover a project and create external PROJECT.md context
    run          launch a supported agent for a project
    doctor       diagnose external project state
    refresh      refresh discovery and PROJECT.md
    config       print or open the external project config directory
    reflect      review past sessions, learn reusable skills, propose rules
    install      explicitly materialize the accelerator into a repository
    self-update  update the globally installed embacc package
    version      print the accelerator version

Use `embacc <command> --help` for command-specific options.
"""


def _bundle_root() -> Path:
    here = Path(__file__).resolve().parent
    packaged = here / "_bundle"
    if (packaged / "scripts" / "embacc_native.py").is_file():
        return packaged
    dev_root = here.parent.parent
    if (dev_root / "scripts" / "embacc_native.py").is_file():
        return dev_root
    raise SystemExit(
        "embacc: could not locate bundled accelerator content "
        f"(looked under {packaged} and {dev_root})"
    )


def _run(script: str, args: list[str]) -> int:
    root = _bundle_root()
    command = [sys.executable, str(root / "scripts" / script)]
    if script == "embacc_native.py":
        command += ["--source-root", str(root)]
    return subprocess.run([*command, *args], check=False).returncode


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        return _run("embacc_native.py", ["auto", "."])

    command = args[0]
    tail = args[1:]
    if command in {"-h", "--help"}:
        print(HELP, end="")
        return 0
    if command in {"--version", "version"}:
        if tail:
            print(f"embacc: {command} does not accept arguments", file=sys.stderr)
            return 2
        print(__version__)
        return 0
    if command == "install":
        return _run("install-accelerator.py", tail)
    if command == "self-update":
        return _run("embacc_selfupdate.py", tail)
    if command in NATIVE_COMMANDS:
        return _run("embacc_native.py", args)

    print(
        f"embacc: unknown command {command!r}; choose one of: {', '.join(PUBLIC_COMMANDS)}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
