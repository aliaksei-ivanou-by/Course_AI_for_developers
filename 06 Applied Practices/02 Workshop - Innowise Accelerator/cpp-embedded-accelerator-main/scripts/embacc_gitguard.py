#!/usr/bin/env python3
"""Claude Code PreToolUse hook: blocks the agent's own Bash tool from
running git actions that should stay a human's call -- publishing (push)
and irreversible destruction (`reset --hard`, `clean -f`, `branch -D`,
`checkout .`/`restore .`). `git commit`/`git add` are deliberately never
blocked here: whether an agent may commit locally is a team's own call,
not a universal default this accelerator should impose.

Opt-in only: referenced from a project's generated Claude `settings.json`
only when `embacc setup --guard-git` was used (see embacc_adapters.py).
Not installed anywhere by default, and never inside the customer repo --
this file lives in the accelerator's own external/bundled scripts and is
pointed to by absolute path.

Fail-closed: any internal error blocks (exit 2) rather than staying
silent; protected credential paths are handled by the agent-specific safety layer.
A human running the identical command directly in their own terminal is
never affected -- this only gates the Bash tool Claude Code itself
invokes.

Known, honest limitation: Claude Code treats only exit code 2 as a
block; a hook whose interpreter never runs at all (a missing `python`,
a moved install) fails *open*, silently. `embacc doctor` live-fires
this script directly rather than trusting that a `settings.json`
reference alone means it works -- see embacc_native.py::cmd_doctor.
"""

from __future__ import annotations

import json
import re
import sys

HUMAN_ONLY: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (re.compile(r"\bgit\b[^\n]*?\bpush\b"), "git push",
     "publishing is a human action -- finish the work and ask the human to push"),
    (re.compile(r"\bgit\b[^\n]*?\breset\b[^\n]*?(?:^|\s)--hard\b"), "git reset --hard",
     "this discards uncommitted work irreversibly -- use `git stash`, a non---hard reset, or ask the human"),
    (re.compile(r"\bgit\b[^\n]*?\bclean\b[^\n]*?(?:^|\s)(?:-\w*f|--force)"), "git clean -f",
     "this deletes untracked files irreversibly -- list them with `git clean -n` and let the human decide"),
    (re.compile(r"\bgit\b[^\n]*?\bbranch\b[^\n]*?(?:^|\s)(?:-D\b|--delete\s+--force\b|-d\s+--force\b|--force\s+--delete\b)"), "git branch -D",
     "force-deleting a branch can drop unmerged commits -- use `git branch -d` or ask the human"),
    (re.compile(r"\bgit\b[^\n]*?\bcheckout\b[^\n]*?(?:^|\s)(?:--\s+)?\.(?:\s|$)"), "git checkout .",
     "this discards every uncommitted change in the tree -- revert the specific files you touched by path"),
    (re.compile(r"\bgit\b[^\n]*?\brestore\b[^\n]*?(?:^|\s)(?:--\s+)?\.(?:\s|$)"), "git restore .",
     "this discards every uncommitted change in the tree -- restore the specific files you touched by path"),
    (re.compile(r"\bgit\b[^\n]*?\bworktree\b[^\n]*?\bremove\b[^\n]*?(?:^|\s)(?:-f\b|--force\b)"), "git worktree remove --force",
     "--force can discard a worktree with unmerged/uncommitted work -- run `git worktree remove <path>` without --force and let a real refusal surface unfinished work"),
    (re.compile(r"\bgit\b[^\n]*?\bcommit\b[^\n]*?(?:^|\s)(?:--no-verify|--no-gpg-sign|-\w*n\b)"), "git commit --no-verify/--no-gpg-sign",
     "skipping hooks or bypassing commit signing is a human call -- fix the underlying issue the hook caught, or ask the human"),
)

SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\||\n")

# A heredoc body written straight into a file (`cat > notes.md <<'EOF' ...
# git push ... EOF`) is prose, not a command -- the word "push" inside a
# draft PR description must not trip the guard. Blank only a writer
# heredoc's body (cat/tee); an interpreter or piped heredoc still executes
# what it carries and stays in scope.
HEREDOC = re.compile(
    r"(?P<head>[^\n]*?)<<-?[ \t]*(?P<q>['\"]?)(?P<tag>[A-Za-z_]\w*)(?P=q)"
    r"(?P<rest>[^\n]*)\n(?P<body>.*?)\n[ \t]*(?P=tag)[ \t]*(?=\n|$)",
    re.S,
)
WRITER_HEAD = re.compile(r"(?:^|[;&|]|\$\()[ \t]*(?:cat|tee)\b[^|\n]*$")


def _strip_writer_heredocs(cmd: str) -> str:
    def repl(match: re.Match[str]) -> str:
        if "|" in match.group("rest") or not WRITER_HEAD.search(match.group("head")):
            return match.group(0)
        start, end = match.span("body")
        base = match.start()
        return match.group(0)[: start - base] + match.group(0)[end - base :]

    try:
        return HEREDOC.sub(repl, cmd)
    except Exception:
        return cmd  # fail-closed: scan the raw command rather than skip the check


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("embacc-gitguard: could not read hook input -- blocking just in case", file=sys.stderr)
        return 2
    try:
        return run(data)
    except Exception as exc:
        print(f"embacc-gitguard: internal error ({exc}) -- blocking just in case", file=sys.stderr)
        return 2


def run(data: dict) -> int:
    """Hook body, separated from stdin handling so tests can call it directly."""
    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command", "")
    scanned = _strip_writer_heredocs(cmd)
    for segment in SEGMENT_SPLIT.split(scanned):
        if not re.search(r"\bgit\b", segment):
            continue
        for pattern, label, alternative in HUMAN_ONLY:
            if pattern.search(segment):
                print(
                    f"embacc-gitguard: BLOCKED -- {label} is reserved for a human. {alternative}. "
                    "Running the identical command directly in your own terminal is unaffected.",
                    file=sys.stderr,
                )
                return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
