#!/usr/bin/env python3
"""External, per-user accelerator state -- the home of the new default
architecture: accelerator-owned content and per-project state live outside
any customer repository (``~/.embacc`` by default), instead of being
installed into it. See the source-tree architecture notes for the full design.

This module owns three things: locating ``~/.embacc`` (or
``ACCELERATOR_HOME``), computing stable project identity, and maintaining
small external per-project state plus a versioned cache of canonical skills.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from embacc_resources import PACKAGE_VERSION, ResourceError, materialize_core_skills  # noqa: E402

HOME_ENV = "ACCELERATOR_HOME"
PROJECT_STATE_DIRS = ("agent-config", "mcp", "state", "tasks")


class ExternalStateError(RuntimeError):
    pass


def home() -> Path:
    """Root of all accelerator-owned external state. Never inside any
    customer repository; overridable for tests and multi-user machines."""
    override = os.environ.get(HOME_ENV)
    return Path(override).expanduser().resolve() if override else Path.home() / ".embacc"


def core_root() -> Path:
    return home() / "core"


def projects_root() -> Path:
    return home() / "projects"


# --------------------------------------------------------------------------
# Project identity
# --------------------------------------------------------------------------
#
# A project's external state must survive a plain re-clone/re-checkout at
# the same remote (the common case) and must never collide with a different
# repository that merely shares a directory basename. Two sources are used,
# in order of preference:
#
#   1. the "origin" remote URL, normalized (scheme/credentials/host case/
#      trailing ".git" stripped) -- stable across clones, moves, and
#      re-checkouts of the *same* remote, which is the case this is chiefly
#      designed to survive;
#   2. the repository's real (symlink-resolved) root path -- used only when
#      there is no remote (a fresh local-only repository, or no Git at all).
#      This is deliberately path-based and therefore DOES change if such a
#      repository is later moved or renamed; there is no remote-independent
#      fingerprint of an un-pushed repository's *content* that would survive
#      a rewrite/rebase, so this is the documented, honest limitation
#      (see the source-tree architecture notes "Project identity").
#
# A repository with a remote that is later moved on disk keeps the same
# identity (same remote => same id); a repository without a remote that is
# moved gets a *new* identity, and the old one is simply orphaned (never
# deleted automatically -- see `embacc gc`, not implemented in this cut).


@dataclasses.dataclass(frozen=True)
class ProjectIdentity:
    id: str
    slug: str
    root: Path
    remote: str | None
    key_source: str  # "remote" or "path"

    @property
    def dir_name(self) -> str:
        return f"{self.slug}-{self.id}"


_REMOTE_TRIM_RE = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*://)?(?:[^@/]+@)?")
_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _run_git(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *args],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def git_root(target: Path) -> Path | None:
    out = _run_git(["rev-parse", "--show-toplevel"], target)
    return Path(out).resolve() if out else None


def git_remote_url(target: Path) -> str | None:
    return _run_git(["remote", "get-url", "origin"], target) or None


def normalize_remote(url: str) -> str:
    """Collapse SSH/HTTPS/credential/case/`.git`-suffix variants of the same
    remote to one canonical string, e.g. `git@github.com:Org/Repo.git` and
    `https://github.com/Org/Repo` both normalize to `github.com/org/repo`."""
    value = url.strip()
    value = _REMOTE_TRIM_RE.sub("", value)
    value = value.replace(":", "/", 1) if "://" not in url else value
    value = value.removesuffix(".git").removesuffix("/")
    return value.lower()


def _slugify(name: str) -> str:
    slug = _SLUG_RE.sub("-", name).strip("-._")
    return slug[:48] or "project"


def project_identity(target: Path) -> ProjectIdentity:
    """Resolve a stable identity for the repository/directory at ``target``.
    Never writes into ``target``."""
    resolved = target.resolve()
    root = git_root(resolved) or resolved
    remote = git_remote_url(root)
    if remote:
        key = f"remote:{normalize_remote(remote)}"
        source = "remote"
    else:
        # os.path.realpath resolves symlinks on every supported platform,
        # including Windows junctions, unlike Path.resolve() on some old
        # interpreters; the real, canonical path is what protects two
        # differently-named symlinks/junctions to the same directory from
        # getting two different identities, and is proof against relative
        # path tricks (`..`, `.`) creating a spurious second identity.
        key = f"path:{os.path.realpath(root)}"
        source = "path"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    slug = _slugify(root.name)
    return ProjectIdentity(id=digest, slug=slug, root=root, remote=remote, key_source=source)


def project_dir(identity: ProjectIdentity) -> Path:
    return projects_root() / identity.dir_name


# --------------------------------------------------------------------------
# Core cache: one read-only, versioned materialization of the tool-neutral
# package plus every tool adapter, shared by every project. Native runtime
# code reads the canonical skills and other shared assets directly from here.
# --------------------------------------------------------------------------


def _core_version_dir(version: str) -> Path:
    return core_root() / version


def ensure_core(source_root: Path, *, force: bool = False) -> Path:
    """Materialize (or reuse) the tiny shared canonical-skill cache."""
    version_dir = _core_version_dir(PACKAGE_VERSION)
    marker = version_dir / ".complete"
    if marker.is_file() and not force:
        return version_dir
    if version_dir.exists():
        import shutil
        shutil.rmtree(version_dir)
    version_dir.mkdir(parents=True, exist_ok=True)
    try:
        materialize_core_skills(source_root, version_dir)
    except ResourceError as exc:
        raise ExternalStateError(f"unable to materialize external core cache: {exc}") from exc
    marker.write_text(
        json.dumps({"version": PACKAGE_VERSION, "created": time.time()}, indent=2) + "\n",
        encoding="utf-8",
    )
    return version_dir


# --------------------------------------------------------------------------
# Per-project external state
# --------------------------------------------------------------------------


def ensure_project_state(identity: ProjectIdentity) -> Path:
    directory = project_dir(identity)
    for name in PROJECT_STATE_DIRS:
        (directory / name).mkdir(parents=True, exist_ok=True)
    identity_path = directory / "identity.json"
    now = time.time()
    if identity_path.is_file():
        try:
            data = json.loads(identity_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
    else:
        data = {"first_seen": now}
    data.update(
        {
            "id": identity.id,
            "slug": identity.slug,
            "root": str(identity.root),
            "remote": identity.remote,
            "key_source": identity.key_source,
            "last_seen": now,
        }
    )
    data.setdefault("first_seen", now)
    identity_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return directory


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    identity = project_identity(Path(args.target))
    payload = {
        "id": identity.id,
        "slug": identity.slug,
        "root": str(identity.root),
        "remote": identity.remote,
        "key_source": identity.key_source,
        "state_dir": str(project_dir(identity)),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
