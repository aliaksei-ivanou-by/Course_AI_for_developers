#!/usr/bin/env python3
"""Focused tests for repository discovery and PROJECT.md refresh behavior."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import embacc_discover as discover  # noqa: E402
import embacc_projectdoc as projectdoc  # noqa: E402


def git(repo: Path, *args: str) -> None:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)


def make_repo(parent: Path) -> Path:
    repo = parent / "mixed"
    repo.mkdir()
    git(repo, "init", "-q")
    files = {
        "CMakeLists.txt": (
            "cmake_minimum_required(VERSION 3.20)\nproject(demo CXX)\n"
            "add_library(demo src/demo.cpp)\nenable_testing()\n"
            "add_executable(demo_test tests/demo_test.cpp)\nadd_test(NAME demo_test COMMAND demo_test)\n"
        ),
        "src/demo.cpp": "int add(int a, int b) { return a + b; }\n",
        "tests/demo_test.cpp": "int main() { return 0; }\n",
        "tools/pyproject.toml": "[project]\nname='tool'\nversion='0.1.0'\n[tool.pytest.ini_options]\n",
        "tools/tool.py": "print('ok')\n",
        "toolchain-arm.cmake": "set(CMAKE_SYSTEM_PROCESSOR arm)\nset(CMAKE_C_COMPILER arm-none-eabi-gcc)\n",
        "linker.ld": "MEMORY { FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 64K }\n",
        "README.md": "# Fixture\n",
    }
    for relative, content in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "baseline")
    return repo


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="embacc-discovery-") as td:
        base = Path(td)
        repo = make_repo(base)
        result = discover.discover(repo)

        expect("cpp" in result["languages"], "C++ was not detected", failures)
        expect("python" in result["languages"], "Python was not detected", failures)
        expect(result["mixed_stack"], "mixed C++/Python repository was not marked mixed-stack", failures)
        expect(any(item["kind"] == "cmake" for item in result["build_systems"]), "CMake was not detected", failures)
        expect(any(item["kind"] == "ctest" for item in result["test_frameworks"]), "CTest was not detected", failures)
        expect(result["embedded"]["cross_compile_hint"], "cross-compile hint was not detected", failures)
        expect(result["embedded"]["toolchain_files"], "toolchain file was not detected", failures)

        state = base / "state"
        state.mkdir()
        first = projectdoc.write_or_refresh(state, result)
        expect(first["created"], "first PROJECT.md generation did not report created", failures)
        project_md = state / "PROJECT.md"
        text = project_md.read_text(encoding="utf-8")
        expect("cmake" in text.lower(), "PROJECT.md omitted detected CMake workflow", failures)
        expect("UNKNOWN" in text, "PROJECT.md should mark unknowable intent instead of inventing it", failures)

        second = projectdoc.write_or_refresh(state, result)
        expect(not second["created"] and not second["updated"], "idempotent refresh changed PROJECT.md", failures)

        marker = "UNKNOWN -- describe what this system/product actually does; discovery cannot infer intent."
        edited = project_md.read_text(encoding="utf-8").replace(marker, "Fixture purpose edited by developer.")
        project_md.write_text(edited, encoding="utf-8")
        for _ in range(3):
            report = projectdoc.write_or_refresh(state, result)
            expect("purpose" in report["preserved"], "hand-edited purpose section was not preserved", failures)
            expect("Fixture purpose edited by developer." in project_md.read_text(encoding="utf-8"), "hand edit was overwritten", failures)

    if failures:
        print("DISCOVERY/PROJECTDOC TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("DISCOVERY/PROJECTDOC TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
