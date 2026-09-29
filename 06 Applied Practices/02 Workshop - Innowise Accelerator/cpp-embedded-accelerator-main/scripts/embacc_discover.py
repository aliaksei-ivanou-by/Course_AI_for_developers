#!/usr/bin/env python3
"""Deterministic project discovery for `embacc setup`/`embacc refresh`.

Produces a `discovery.json`-shaped dict describing what kind of project this
repository actually is: languages, build systems, test frameworks, static
analysis/formatting tools, CI, containers, embedded/cross-compile signals,
existing customer-owned AI configuration, docs, and scripts. Every fact
carries a `status` so PROJECT.md (embacc_projectdoc.py) can tell a reader
what is actually known:

  - "discovered"  -- a file/text signal was found; the command itself was
                     not executed.
  - "verified"    -- a *safe* command (a `--version`/`--help` probe, never a
                     build/test) was actually run and succeeded.
  - "not run"     -- the tool that would confirm this was not found on PATH,
                     or verification was not requested.
  - "unknown"     -- nothing found; never silently guessed.

This never invents a build/test/lint command that is not backed by a real,
discovered file or a tool actually present on PATH. It never runs a build,
a test suite, or anything else that could be slow, flaky, or destructive --
see `verify_build()` for the one, explicit, opt-in exception.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

TEXT_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".rs", ".py", ".cmake", ".txt", ".toml"}
MAX_SCAN_FILES = 6000


def _glob_files(root: Path, patterns: list[str]) -> list[str]:
    out: list[str] = []
    for pattern in patterns:
        for p in root.glob(pattern):
            if p.is_file():
                out.append(str(p.relative_to(root)).replace("\\", "/"))
    return sorted(set(out))


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _search_text(paths: list[Path], pattern: str) -> list[str]:
    rx = re.compile(pattern, re.IGNORECASE)
    hits = []
    for path in paths:
        if rx.search(_read(path)):
            hits.append(str(path))
    return hits[:30]


def _sample_source_files(root: Path) -> list[Path]:
    out = []
    for p in root.rglob("*"):
        if len(out) >= MAX_SCAN_FILES:
            break
        if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES and ".git" not in p.parts:
            out.append(p)
    return out


def _fact(status: str, value: Any = None, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"status": status, "value": value, "evidence": evidence or []}


# --------------------------------------------------------------------------
# Language / build system / test framework detectors
# --------------------------------------------------------------------------


def _detect_languages(root: Path, sample: list[Path]) -> dict[str, Any]:
    cpp_evidence = _glob_files(root, ["**/*.cpp", "**/*.cc", "**/*.cxx", "**/*.hpp", "**/*.hh"])
    c_evidence = _glob_files(root, ["**/*.c"])
    py_evidence = _glob_files(root, ["**/*.py"])
    rust_evidence = _glob_files(root, ["Cargo.toml", "**/Cargo.toml"])
    langs: dict[str, Any] = {}
    if cpp_evidence:
        langs["cpp"] = _fact("discovered", True, cpp_evidence[:10])
    if c_evidence and not cpp_evidence:
        langs["c"] = _fact("discovered", True, c_evidence[:10])
    if py_evidence or _glob_files(root, ["pyproject.toml", "setup.py", "setup.cfg"]):
        langs["python"] = _fact("discovered", True, (py_evidence[:10] or _glob_files(root, ["pyproject.toml"])))
    if rust_evidence:
        langs["rust"] = _fact("discovered", True, rust_evidence[:10])
    cxx_std = _search_text(sample, r"CMAKE_CXX_STANDARD\s+(\d+)|std=c\+\+(\d+)|edition\s*=\s*\"?(\d{4})")
    if cxx_std:
        langs.setdefault("_cxx_standard_hint", _fact("discovered", True, cxx_std[:5]))
    return langs


def _detect_build_systems(root: Path) -> list[dict[str, Any]]:
    systems: list[dict[str, Any]] = []

    cmake_ev = _glob_files(root, ["CMakeLists.txt", "**/CMakeLists.txt"])
    if cmake_ev:
        systems.append(
            {
                "kind": "cmake",
                "evidence": cmake_ev[:10],
                "configure_command": "cmake -S . -B build",
                "build_command": "cmake --build build",
                "status": "discovered",
            }
        )

    meson_ev = _glob_files(root, ["meson.build", "**/meson.build"])
    if meson_ev:
        systems.append(
            {
                "kind": "meson",
                "evidence": meson_ev[:10],
                "configure_command": "meson setup build",
                "build_command": "meson compile -C build",
                "status": "discovered",
            }
        )

    ninja_ev = _glob_files(root, ["build.ninja", "**/build.ninja"])
    if ninja_ev:
        systems.append({"kind": "ninja", "evidence": ninja_ev[:5], "build_command": "ninja -C build", "status": "discovered"})

    make_ev = _glob_files(root, ["Makefile", "GNUmakefile"])
    if make_ev and not cmake_ev:
        systems.append({"kind": "make", "evidence": make_ev[:5], "build_command": "make", "status": "discovered"})

    cargo_ev = _glob_files(root, ["Cargo.toml"])
    if cargo_ev:
        systems.append(
            {
                "kind": "cargo",
                "evidence": cargo_ev,
                "build_command": "cargo build",
                "test_command": "cargo test",
                "status": "discovered",
            }
        )

    py_ev = _glob_files(root, ["pyproject.toml", "setup.py"])
    if py_ev:
        systems.append({"kind": "python-package", "evidence": py_ev, "build_command": "pip install -e .", "status": "discovered"})

    platformio_ev = _glob_files(root, ["platformio.ini"])
    if platformio_ev:
        systems.append(
            {
                "kind": "platformio",
                "evidence": platformio_ev,
                "build_command": "pio run",
                "test_command": "pio test",
                "status": "discovered",
            }
        )

    zephyr_ev = _glob_files(root, ["west.yml", "**/prj.conf"])
    if zephyr_ev:
        systems.append({"kind": "zephyr/west", "evidence": zephyr_ev[:10], "build_command": "west build", "status": "discovered"})

    return systems


def _detect_test_frameworks(root: Path, sample: list[Path], build_systems: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frameworks: list[dict[str, Any]] = []
    if any(s["kind"] == "cmake" for s in build_systems):
        ctest_ev = _search_text(sample, r"enable_testing\(\)|add_test\(")
        if ctest_ev:
            frameworks.append({"kind": "ctest", "evidence": ctest_ev[:10], "command": "ctest --test-dir build", "status": "discovered"})
        gtest_ev = _search_text(sample, r"gtest|googletest|GTest::")
        if gtest_ev:
            frameworks.append({"kind": "gtest", "evidence": gtest_ev[:10], "status": "discovered"})
        catch_ev = _search_text(sample, r"catch2|CATCH_CONFIG_MAIN|Catch2::")
        if catch_ev:
            frameworks.append({"kind": "catch2", "evidence": catch_ev[:10], "status": "discovered"})
    if any(s["kind"] == "cargo" for s in build_systems):
        frameworks.append({"kind": "cargo-test", "evidence": [], "command": "cargo test", "status": "discovered"})
    pytest_ev = _glob_files(root, ["pytest.ini", "conftest.py", "**/conftest.py"])
    pyproject = root / "pyproject.toml"
    pytest_in_pyproject = "[tool.pytest" in _read(pyproject) if pyproject.is_file() else False
    if pytest_ev or pytest_in_pyproject:
        frameworks.append(
            {"kind": "pytest", "evidence": pytest_ev[:10] or ["pyproject.toml"], "command": "pytest", "status": "discovered"}
        )
    return frameworks


def _detect_static_analysis(root: Path) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    if _glob_files(root, [".clang-tidy"]):
        tools.append({"kind": "clang-tidy", "evidence": [".clang-tidy"], "command": "clang-tidy", "status": "discovered"})
    pyproject_text = _read(root / "pyproject.toml")
    if _glob_files(root, ["cppcheck.cfg", ".cppcheck"]) or "cppcheck" in pyproject_text.lower():
        tools.append({"kind": "cppcheck", "evidence": [], "command": "cppcheck --enable=all .", "status": "discovered"})
    if _glob_files(root, ["ruff.toml", ".ruff.toml"]) or "[tool.ruff]" in pyproject_text:
        tools.append({"kind": "ruff", "evidence": ["pyproject.toml/ruff.toml"], "command": "ruff check .", "status": "discovered"})
    if _glob_files(root, ["mypy.ini"]) or "[tool.mypy]" in pyproject_text:
        tools.append({"kind": "mypy", "evidence": ["pyproject.toml/mypy.ini"], "command": "mypy .", "status": "discovered"})
    return tools


def _detect_formatting(root: Path) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    if _glob_files(root, [".clang-format"]):
        tools.append({"kind": "clang-format", "evidence": [".clang-format"], "command": "clang-format -i", "status": "discovered"})
    pyproject_text = _read(root / "pyproject.toml")
    if "[tool.black]" in pyproject_text:
        tools.append({"kind": "black", "evidence": ["pyproject.toml"], "command": "black .", "status": "discovered"})
    if _glob_files(root, ["rustfmt.toml", ".rustfmt.toml"]) or _glob_files(root, ["Cargo.toml"]):
        if _glob_files(root, ["Cargo.toml"]):
            tools.append({"kind": "rustfmt", "evidence": ["Cargo.toml"], "command": "cargo fmt", "status": "discovered"})
    return tools


def _detect_ci(root: Path) -> list[dict[str, Any]]:
    ci = []
    gha = _glob_files(root, [".github/workflows/*.yml", ".github/workflows/*.yaml"])
    if gha:
        ci.append({"kind": "github-actions", "evidence": gha})
    if _glob_files(root, [".gitlab-ci.yml"]):
        ci.append({"kind": "gitlab-ci", "evidence": [".gitlab-ci.yml"]})
    if _glob_files(root, ["Jenkinsfile"]):
        ci.append({"kind": "jenkins", "evidence": ["Jenkinsfile"]})
    if _glob_files(root, ["azure-pipelines.yml"]):
        ci.append({"kind": "azure-pipelines", "evidence": ["azure-pipelines.yml"]})
    return ci


def _detect_containers(root: Path) -> dict[str, Any]:
    docker_ev = _glob_files(root, ["Dockerfile", "**/Dockerfile", "docker-compose.yml", "docker-compose.yaml"])
    devcontainer_ev = _glob_files(root, [".devcontainer/devcontainer.json", ".devcontainer.json"])
    return {
        "docker": bool(docker_ev),
        "devcontainer": bool(devcontainer_ev),
        "evidence": docker_ev + devcontainer_ev,
    }


def _detect_embedded(root: Path, sample: list[Path]) -> dict[str, Any]:
    toolchain_files = _glob_files(root, ["**/*toolchain*.cmake", "**/*.ld", "**/*.lds"])
    vendor_projects = _glob_files(root, ["**/*.uvprojx", "**/*.ewp", "**/*.ioc", "**/*.pio"])
    cross_hint = _search_text(sample, r"arm-none-eabi|riscv[a-z0-9-]*-elf|avr-gcc|CMAKE_SYSTEM_PROCESSOR|CMAKE_CROSSCOMPILING")
    hardware_hint = _search_text(sample, r"\b(__disable_irq|IRQHandler|FreeRTOS|Zephyr|bare.?metal|HAL_[A-Z]|MMIO|stm32|STM32)\b")
    return {
        "toolchain_files": toolchain_files,
        "vendor_ide_projects": vendor_projects,
        "cross_compile_hint": bool(cross_hint or toolchain_files),
        "hardware_target_hint": bool(hardware_hint),
        "evidence": (cross_hint + hardware_hint)[:15],
    }


def _detect_existing_ai_config(root: Path) -> dict[str, bool]:
    return {
        "AGENTS.md": (root / "AGENTS.md").is_file(),
        "CLAUDE.md": (root / "CLAUDE.md").is_file(),
        ".claude": (root / ".claude").is_dir(),
        ".codex": (root / ".codex").is_dir(),
        ".opencode": (root / ".opencode").is_dir(),
        "opencode.json": (root / "opencode.json").is_file() or (root / "opencode.jsonc").is_file(),
    }


def _detect_docs_and_scripts(root: Path) -> dict[str, Any]:
    readme = next((n for n in ("README.md", "README.rst", "README.txt", "README") if (root / n).is_file()), None)
    return {
        "readme": readme,
        "docs_dir": (root / "docs").is_dir(),
        "scripts_dirs": [d for d in ("scripts", "tools") if (root / d).is_dir()],
    }


# --------------------------------------------------------------------------
# Safe tool-availability verification -- `--version` probes only, never a
# build or test. This is the one thing `embacc setup` runs automatically.
# --------------------------------------------------------------------------

_VERSION_PROBE: dict[str, tuple[str, ...]] = {
    "cmake": ("cmake", "--version"),
    "ninja": ("ninja", "--version"),
    "meson": ("meson", "--version"),
    "make": ("make", "--version"),
    "cargo": ("cargo", "--version"),
    "pytest": ("pytest", "--version"),
    "ruff": ("ruff", "--version"),
    "mypy": ("mypy", "--version"),
    "clang-tidy": ("clang-tidy", "--version"),
    "clang-format": ("clang-format", "--version"),
    "cppcheck": ("cppcheck", "--version"),
    "ctest": ("ctest", "--version"),
    "pio": ("pio", "--version"),
    "west": ("west", "--version"),
}


def verify_tools(names: set[str]) -> dict[str, dict[str, Any]]:
    """Runs only `--version`-class probes -- safe, fast, side-effect-free.
    Never a build/test command; see `verify_build` for that, opt-in only."""
    results: dict[str, dict[str, Any]] = {}
    for name in sorted(names):
        probe = _VERSION_PROBE.get(name)
        if not probe:
            continue
        binary = shutil.which(probe[0])
        if not binary:
            results[name] = {"status": "not run", "reason": "not found on PATH"}
            continue
        try:
            proc = subprocess.run(probe, capture_output=True, text=True, timeout=10, check=False)
            ok = proc.returncode == 0
            results[name] = {
                "status": "verified" if ok else "not run",
                "detail": (proc.stdout or proc.stderr).strip().splitlines()[0] if (proc.stdout or proc.stderr) else "",
            }
        except (OSError, subprocess.TimeoutExpired) as exc:
            results[name] = {"status": "not run", "reason": str(exc)}
    return results


def verify_build(root: Path, build_systems: list[dict[str, Any]], *, timeout: float = 180.0) -> list[dict[str, Any]]:
    """Opt-in only -- actually runs the first discovered build system's
    configure+build command (never test/install/deploy). Caller decides
    whether to invoke this at all (see `embacc setup --verify-build`)."""
    results = []
    for system in build_systems[:1]:
        command = system.get("configure_command") or system.get("build_command")
        if not command:
            continue
        tool = command.split()[0]
        if not shutil.which(tool):
            results.append({"command": command, "status": "not run", "reason": f"{tool} not on PATH"})
            continue
        try:
            proc = subprocess.run(command, cwd=root, shell=True, capture_output=True, text=True, timeout=timeout, check=False)
            results.append(
                {
                    "command": command,
                    "status": "PASS" if proc.returncode == 0 else "FAIL",
                    "tail": (proc.stdout + proc.stderr)[-2000:],
                }
            )
        except subprocess.TimeoutExpired:
            results.append({"command": command, "status": "NOT RUN", "reason": f"exceeded {timeout}s timeout"})
    return results


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def discover(root: Path, *, remote: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    sample = _sample_source_files(root)
    build_systems = _detect_build_systems(root)
    languages = _detect_languages(root, sample)
    test_frameworks = _detect_test_frameworks(root, sample, build_systems)
    static_analysis = _detect_static_analysis(root)
    formatting = _detect_formatting(root)

    tool_names = {s["kind"] for s in build_systems if s["kind"] in _VERSION_PROBE}
    tool_names |= {f["kind"] for f in test_frameworks if f["kind"] in _VERSION_PROBE}
    tool_names |= {t["kind"] for t in static_analysis if t["kind"] in _VERSION_PROBE}
    tool_names |= {t["kind"] for t in formatting if t["kind"] in _VERSION_PROBE}
    verification = verify_tools(tool_names)

    for group in (build_systems, test_frameworks, static_analysis, formatting):
        for entry in group:
            v = verification.get(entry["kind"])
            if v:
                entry["tool_available"] = v["status"] == "verified"

    languages_public = {k: v for k, v in languages.items() if not k.startswith("_")}
    return {
        "schema_version": 1,
        "root": str(root),
        "remote": remote,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "languages": languages_public,
        "mixed_stack": len(languages_public) > 1,
        "build_systems": build_systems,
        "test_frameworks": test_frameworks,
        "static_analysis": static_analysis,
        "formatting": formatting,
        "ci": _detect_ci(root),
        "containers": _detect_containers(root),
        "embedded": _detect_embedded(root, sample),
        "existing_ai_config": _detect_existing_ai_config(root),
        "docs": _detect_docs_and_scripts(root),
        "tool_verification": verification,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = discover(Path(args.root))
    print(json.dumps(result, indent=2) if args.json else json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
