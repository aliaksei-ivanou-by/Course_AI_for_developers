#!/usr/bin/env python3
"""Focused tests for the ast-grep structural-search integration: hidden
config/state, graceful degradation when the binary is absent, and (when a
real `ast-grep` is installed on this machine) a genuine structural scan
against real source files. Mirrors tests/test_pi_safety.py's convention of
running the real thing when possible and skipping only the live-fire part
when the external tool truly is not installed -- never fabricating a result."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import embacc_astgrep as astgrep  # noqa: E402
import embacc_projectdoc as projectdoc  # noqa: E402


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    skipped_live = False

    with tempfile.TemporaryDirectory(prefix="embacc-astgrep-") as td:
        base = Path(td)
        state_dir = base / "state"
        repo_root = base / "repo"
        repo_root.mkdir()
        state_dir.mkdir()

        # --- pure logic, no subprocess -------------------------------------------------
        discovery = {"languages": {"cpp": {}, "python": {}, "rust": {}, "go": {}, "_cxx_standard_hint": {}}}
        expect(
            astgrep.languages_for(discovery) == ["cpp", "python", "rust"],
            f"languages_for mapped unexpected set: {astgrep.languages_for(discovery)}", failures,
        )
        expect(astgrep.languages_for({}) == [], "languages_for on empty discovery should be empty", failures)

        cfg = astgrep.ensure_config(state_dir)
        expect(cfg == astgrep.config_path(state_dir), "ensure_config did not return the documented config_path", failures)
        expect(cfg.is_file(), "ensure_config did not write sgconfig.yml", failures)
        expect((astgrep.state_root(state_dir) / astgrep.RULES_DIRNAME).is_dir(), "ensure_config did not create the rules directory", failures)
        first_content = cfg.read_text(encoding="utf-8")
        custom = first_content + "\n# hand-edited\n"
        cfg.write_text(custom, encoding="utf-8")
        astgrep.ensure_config(state_dir)
        expect(cfg.read_text(encoding="utf-8") == custom, "ensure_config overwrote a hand-edited sgconfig.yml", failures)

        fresh_state = base / "fresh-state"
        fresh_state.mkdir()
        status = astgrep.quick_status(fresh_state)
        expect(status["cached_index"] is None, "quick_status should report no cached index before any build_index call", failures)
        expect(status["config_exists"] is False, "quick_status should report no config before ensure_config/build_index", failures)

        # --- pixi-sibling fallback: embacc's own run-dependency, found without
        # a separate `pixi global expose ast-grep` -- deterministic via a fake
        # sys.executable, no real pixi env required to test it -------------------------
        real_executable = sys.executable
        real_which = shutil.which
        try:
            fake_env = base / "fake-pixi-env"
            windows_style = fake_env / "Library" / "bin" / "ast-grep.exe"
            posix_style = fake_env / "bin" / "ast-grep"
            windows_style.parent.mkdir(parents=True)
            windows_style.write_text("", encoding="utf-8")
            posix_style.parent.mkdir(parents=True)
            posix_style.write_text("", encoding="utf-8")
            sys.executable = str(fake_env / "python.exe")  # never created; only .parent matters

            shutil.which = lambda name: None  # simulate nothing named ast-grep on PATH
            sibling = astgrep._pixi_env_binary()
            expect(sibling is not None and sibling.is_file(), "pixi-sibling fallback did not find either conda layout", failures)
            expect(astgrep.binary() == str(sibling), "binary() did not fall back to the pixi-sibling copy when PATH lookup failed", failures)

            shutil.which = lambda name: "/usr/bin/ast-grep" if name == astgrep.BINARY_NAME else None
            expect(astgrep.binary() == "/usr/bin/ast-grep", "binary() must prefer a standalone PATH install over the pixi-sibling fallback", failures)
        finally:
            sys.executable = real_executable
            shutil.which = real_which

        # --- forced-unavailable path: deterministic on every machine, including
        # this dev box which does have a real ast-grep on PATH ------------------------
        real_binary = astgrep.binary
        try:
            astgrep.binary = lambda: None  # type: ignore[assignment]
            unavailable_state = base / "unavailable-state"
            unavailable_state.mkdir()
            result = astgrep.build_index(repo_root, unavailable_state, discovery)
            expect(result["available"] is False, "forced-unavailable build_index reported available=True", failures)
            expect(result["languages"] == {}, "forced-unavailable build_index should not run any language scan", failures)
            expect(astgrep.index_path(unavailable_state).is_file(), "index.json should still be written when unavailable", failures)
            expect(not astgrep.config_path(unavailable_state).is_file(), "sgconfig.yml should not be written when ast-grep is unavailable", failures)
            quick = astgrep.quick_status(unavailable_state)
            expect(quick["available"] is False, "quick_status should reflect the forced-unavailable binary()", failures)
        finally:
            astgrep.binary = real_binary  # type: ignore[assignment]

        # --- real scan, only when a genuine ast-grep is on PATH here -----------------
        exe = astgrep.binary()
        if not exe:
            skipped_live = True
        else:
            (repo_root / "main.c").write_text("int add(int a, int b) { return a + b; }\n", encoding="utf-8")
            (repo_root / "util.py").write_text("def greet(name):\n    return name\n", encoding="utf-8")
            real_discovery = {"languages": {"c": {}, "python": {}}}
            live_state = base / "live-state"
            live_state.mkdir()
            result = astgrep.build_index(repo_root, live_state, real_discovery, exe=exe)
            expect(result["available"] is True, "real ast-grep binary reported available=False", failures)
            expect(bool(result.get("version")), "real ast-grep scan did not record a version string", failures)
            expect(not (result.get("version") or "").lower().startswith("ast-grep ast-grep"), "version string still has the redundant ast-grep prefix", failures)
            for lang in ("c", "python"):
                info = result["languages"].get(lang)
                expect(info is not None and info.get("status") == "verified", f"real ast-grep scan did not verify {lang}: {info}", failures)
                expect(isinstance((info or {}).get("matches"), int) and info["matches"] > 0, f"real ast-grep scan found zero matches for {lang} against real source", failures)
            expect(astgrep.config_path(live_state).is_file(), "real scan did not write hidden sgconfig.yml", failures)
            expect(astgrep.index_path(live_state).is_file(), "real scan did not write hidden index.json", failures)
            cached = astgrep.load_index(live_state)
            expect(cached == result, "load_index did not round-trip what build_index wrote", failures)
            quick = astgrep.quick_status(live_state)
            expect(quick["available"] is True and quick["config_exists"] is True, "quick_status did not reflect the real, just-built index", failures)

        # --- PROJECT.md section rendering, pure function, no subprocess --------------
        available_section = projectdoc._section_structural_search({
            "ast_grep": {"available": True, "version": "0.45.2", "languages": {"c": {"status": "verified"}, "python": {"status": "error"}}},
            "external_state_dir": str(state_dir),
        })
        expect("ast-grep 0.45.2 available" in available_section, "structural search section did not report the version", failures)
        expect("Structurally verified against this project's real files: c." in available_section, "structural search section did not list the verified language", failures)
        expect("Not verified (run `embacc doctor` for detail): python." in available_section, "structural search section did not surface the failed language", failures)
        expect(str(astgrep.config_path(state_dir)) in available_section, "structural search section did not include the hidden config path", failures)

        unavailable_section = projectdoc._section_structural_search({"ast_grep": {"available": False}})
        expect("not found on PATH" in unavailable_section, "structural search section did not degrade gracefully when unavailable", failures)
        expect("grep/ripgrep" in unavailable_section, "structural search section did not suggest a fallback when unavailable", failures)

        missing_key_section = projectdoc._section_structural_search({})
        expect("not found on PATH" in missing_key_section, "structural search section crashed/misbehaved with no ast_grep key at all", failures)

    if failures:
        print("AST-GREP TEST: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    suffix = " (live scan skipped -- ast-grep not installed on this machine)" if skipped_live else " (including a real scan against real source)"
    print(f"AST-GREP TEST: PASS{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
