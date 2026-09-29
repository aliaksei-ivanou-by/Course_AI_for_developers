/**
 * C++ / Embedded Accelerator safety gate for Pi.
 *
 * Pi auto-discovers this project-local extension from .pi/extensions/.
 * It provides a fail-closed boundary for secrets, workspace escapes,
 * destructive local operations, hardware-destructive operations, and
 * external side effects that require explicit interactive approval.
 */

import path from "node:path";
import type { ExtensionAPI, ExtensionContext } from "@mariozechner/pi-coding-agent";

type ToolInput = Record<string, unknown>;
type GateResult = { block: true; reason: string } | undefined;

const WORKSPACE_ROOT = path.resolve(process.cwd());

// A dangerous verb only needs to be preceded by whitespace or a real
// statement separator to count -- not just start-of-statement -- so that a
// wrapper like `find . -exec rm -rf {} \;`, `xargs rm -rf`, `timeout 5 git
// push --force`, or `sh -c "rm -rf /"` cannot hide the verb behind another
// command's argument.
const VERB_BOUNDARY = "(^|[;&|\\n]\\s*|\\s)";

function commandIsRmRf(command: string): boolean {
  const match = new RegExp(`${VERB_BOUNDARY}rm\\s+([^\\n;&|]*)`, "i").exec(command);
  if (!match) return false;
  const flagChars = new Set<string>();
  for (const token of match[2].split(/\s+/)) {
    if (!token || token === "--") break;
    if (token === "--recursive") flagChars.add("r");
    else if (token === "--force") flagChars.add("f");
    else if (/^-[A-Za-z]+$/.test(token)) {
      for (const ch of token.slice(1).toLowerCase()) flagChars.add(ch);
    } else {
      break; // first non-flag token (the target) ends option scanning
    }
  }
  return flagChars.has("r") && flagChars.has("f");
}

const HARD_DENY_BASH: Array<[RegExp | ((command: string) => boolean), string]> = [
  [/(^|[;&|\n]\s*|\s)sudo(?:\s|$)/i, "sudo is forbidden by accelerator policy."],
  [commandIsRmRf, "rm -rf style deletion is forbidden."],
  [/(^|[;&|\n]\s*|\s)chmod\s+777(?:\s|$)/i, "chmod 777 is forbidden."],
  [/(^|[;&|\n]\s*|\s)git\s+reset\s+--hard(?:\s|$)/i, "git reset --hard requires a recovery decision outside the agent."],
  [/(^|[;&|\n]\s*|\s)git\s+clean\s+-[^\n;&|]*f/i, "git clean -f can destroy untracked work and is forbidden."],
  [/(^|[;&|\n]\s*|\s)git\s+checkout\s+--\s+\.(?:\s|$)/i, "Discarding the whole worktree is forbidden."],
  [/(^|[;&|\n]\s*|\s)git\s+restore(?:\s+[^;&|]*)?\s+\.(?:\s|$)/i, "Discarding the whole worktree is forbidden."],
  [/(^|[;&|\n]\s*|\s)git\s+push\b[^\n;&|]*\s(?:-[A-Za-z]*f[A-Za-z]*|--force|--force-with-lease(?:=[^\s;&|]+)?)(?=\s|$)/i, "Force push is forbidden without an out-of-band recovery decision."],
  [/(^|[;&|\n]\s*|\s)dd\s+[^\n;&|]*of=\/dev\/(?:sd|nvme|mmcblk)/i, "Raw writes to block devices are forbidden."],
  [/(^|[;&|\n]\s*)[^#\n;]*\bDROP\s+TABLE\b/i, "DROP TABLE is forbidden by default."],
  [/(^|[;&|\n]\s*|\s)(?:openocd|nrfjprog|west|pyocd|JLinkExe|stm32programmer_cli)\b[^\n;&|]*(?:mass[-_ ]?erase|eraseall|--eraseall|--recover)/i, "Mass erase or device recovery is forbidden by default."],
];

const APPROVAL_BASH: Array<[RegExp, string]> = [
  [/(^|[;&|\n]\s*|\s)git\s+push\b/i, "Git push changes an external system."],
  [/(^|[;&|\n]\s*|\s)gh\s+(?:pr\s+(?:create|merge|close)|release\s+create|issue\s+(?:create|close)|gist\s+create)\b/i, "GitHub mutation requires explicit approval."],
  [/(^|[;&|\n]\s*|\s)(?:scp|sftp)\b/i, "Remote file transfer may disclose client data."],
  [/(^|[;&|\n]\s*|\s)rsync\b[^\n;&|]*\s[^\s]+:[^\s]+/i, "Remote rsync may disclose client data."],
  [/(^|[;&|\n]\s*|\s)ssh\b/i, "Remote command execution requires explicit approval."],
  [/(^|[;&|\n]\s*|\s)curl\b[^\n;&|]*(?:--upload-file|-T\s|--data-binary\s+@|--data\s+@|-d\s+@)/i, "Uploading data with curl requires explicit approval."],
  [/(^|[;&|\n]\s*|\s)wget\b[^\n;&|]*(?:--post-file|--body-file)/i, "Uploading data with wget requires explicit approval."],
  [/(^|[;&|\n]\s*|\s)(?:npm\s+publish|cargo\s+publish|twine\s+upload|docker\s+push)\b/i, "Publishing artifacts requires explicit approval."],
  [/(^|[;&|\n]\s*|\s)(?:kubectl\s+(?:apply|delete|patch|replace|scale)|helm\s+(?:install|upgrade|uninstall))\b/i, "Remote deployment mutation requires explicit approval."],
  [/(^|[;&|\n]\s*|\s)(?:west\s+flash|nrfjprog\b|pyocd\s+flash|JLinkExe\b|stm32programmer_cli\b|openocd\b)/i, "Programming or controlling target hardware requires explicit approval."],
  [/(^|[;&|\n]\s*|\s)(?:cmake\s+--build|ninja|make)\b[^\n;&|]*(?:flash|erase|program)\b/i, "A build target may program or erase hardware and requires explicit approval."],
];

const POLICY_PROTECTED_PATHS = [
  "AGENTS.md",
  ".accelerator-install.json",
  ".agents/skills/",
  ".pi/settings.json",
  ".pi/extensions/accelerator-safety.ts",
  ".claude/settings.json",
  "opencode.json",
  ".codex/hooks.json",
  ".codex/hooks/",
];

const SENSITIVE_SEGMENTS = new Set([
  ".ssh",
  ".aws",
  ".azure",
  ".kube",
  "secrets",
  "credentials",
]);

const SENSITIVE_BASENAMES = [
  /^\.env(?:\..+)?$/i,
  /^id_(?:rsa|dsa|ecdsa|ed25519)$/i,
  /(?:^|[-_.])private[-_.]?key(?:\.|$)/i,
  /\.key$/i,
  /\.(?:p12|pfx)$/i,
  /^(?:credentials|secrets)\.(?:json|ya?ml|toml|ini)$/i,
];

function normalizeCandidate(raw: string): string {
  return raw.replace(/^file:\/\//i, "").trim();
}

function isEnvExample(base: string): boolean {
  return /^\.env\.(?:example|sample|template)$/i.test(base);
}

function isSensitivePath(raw: string): boolean {
  if (!raw || raw.includes("\n")) return false;
  const candidate = normalizeCandidate(raw);
  const parts = candidate.split(/[\\/]+/).filter(Boolean);
  const base = parts.at(-1) ?? "";
  if (isEnvExample(base)) return false;
  if (parts.some((part) => SENSITIVE_SEGMENTS.has(part.toLowerCase()))) return true;
  return SENSITIVE_BASENAMES.some((pattern) => pattern.test(base));
}

function pathFromInput(input: ToolInput): string | undefined {
  for (const key of ["path", "file", "filePath", "directory", "cwd"]) {
    const value = input[key];
    if (typeof value === "string" && value.trim()) return value;
  }
  return undefined;
}

function outsideWorkspace(raw: string): boolean {
  const candidate = normalizeCandidate(raw);
  if (!candidate || candidate === ".") return false;
  const resolved = path.resolve(WORKSPACE_ROOT, candidate);
  const relative = path.relative(WORKSPACE_ROOT, resolved);
  return relative.startsWith(".." + path.sep) || relative === ".." || path.isAbsolute(relative);
}


function normalizedRelative(raw: string): string {
  const resolved = path.resolve(WORKSPACE_ROOT, normalizeCandidate(raw));
  return path.relative(WORKSPACE_ROOT, resolved).replace(/\\/g, "/");
}

function isPolicyProtectedPath(raw: string): boolean {
  const rel = normalizedRelative(raw).toLowerCase();
  return POLICY_PROTECTED_PATHS.some((item) => {
    const normalized = item.replace(/\\/g, "/").toLowerCase();
    return normalized.endsWith("/") ? rel.startsWith(normalized) : rel === normalized;
  });
}

// Safe, well-known sinks that are absolute paths but never a real
// workspace-escaping read/write (redirecting to them is routine).
const ABSOLUTE_PATH_ALLOWLIST = new Set([
  "/dev/null", "/dev/zero", "/dev/full", "/dev/random", "/dev/urandom",
  "/dev/stdin", "/dev/stdout", "/dev/stderr",
]);

function commandReferencesParentPath(command: string): boolean {
  if (/(^|[\s"'=])\.\.[\\/]/.test(command)) return true;
  const tokens = command.replace(/["']/g, "").split(/[\s;&|()<>]+/).filter(Boolean);
  return tokens.some((token) => {
    if (ABSOLUTE_PATH_ALLOWLIST.has(token.toLowerCase())) return false;
    if (!/^(?:\/|[A-Za-z]:[\\/]|\\\\)/.test(token)) return false;
    return outsideWorkspace(token);
  });
}

function commandMutatesProtectedPolicy(command: string): boolean {
  const folded = command.toLowerCase();
  const mentionsProtected = POLICY_PROTECTED_PATHS.some((item) => folded.includes(item.replace(/\/$/, "").toLowerCase()));
  if (!mentionsProtected) return false;
  return /(^|[;&|\n]\s*|\s)(?:rm|mv|cp|install|truncate|perl|python|python3|sed|tee|curl|wget|apply_patch|set-content|add-content|out-file|remove-item|move-item|copy-item|rename-item)\b|(?:>>?|2>)\s*[^;&|]*/i.test(command);
}

// A heredoc whose body is written straight into a file (`cat > f <<'EOF'
// ... EOF`, `tee f <<EOF ... EOF`) carries prose, not something the shell
// executes: a task/PR draft that *tells a human* to run a denied command
// must not trip the same gate as a command that actually runs it. Every
// other heredoc body (an interpreter heredoc like `bash <<EOF`, or one
// piped into a shell) keeps its body in scope, because it is real bypass
// surface. The writer allowlist is intentionally narrow and closed by
// default: unrecognized heads keep their body scanned.
const HEREDOC = /(?<head>[^\n]*?)<<-?[ \t]*(?<q>['"]?)(?<tag>[A-Za-z_]\w*)\k<q>(?<rest>[^\n]*)\n(?<body>[\s\S]*?)\n[ \t]*\k<tag>[ \t]*(?=\n|$)/gd;
const WRITER_HEAD = /(?:^|[;&|]|\$\()[ \t]*(?:cat|tee)\b[^|\n]*$/;

function stripWriterHeredocBodies(cmd: string): string {
  try {
    let result = "";
    let cursor = 0;
    for (const match of cmd.matchAll(HEREDOC)) {
      const groups = match.groups as Record<string, string>;
      const indices = (match as unknown as { indices: { groups: Record<string, [number, number]> } }).indices.groups;
      if (groups.rest.includes("|") || !WRITER_HEAD.test(groups.head)) continue;
      const [bodyStart, bodyEnd] = indices.body;
      result += cmd.slice(cursor, bodyStart);
      cursor = bodyEnd;
    }
    result += cmd.slice(cursor);
    return result;
  } catch {
    return cmd; // fail-closed: scan the raw command rather than skip the check
  }
}

function commandTouchesSensitiveMaterial(command: string): boolean {
  const tokens = command
    .replace(/["']/g, "")
    .split(/[\s;&|()<>]+/)
    .filter(Boolean);
  return tokens.some(isSensitivePath);
}

function blocked(reason: string): GateResult {
  return { block: true, reason };
}

async function requireApproval(ctx: ExtensionContext, reason: string, command: string): Promise<GateResult> {
  if (!ctx.hasUI) {
    return blocked(`${reason} Non-interactive Pi sessions fail closed for approval-required operations.`);
  }
  const approved = await ctx.ui.confirm(
    "C++ / Embedded Accelerator safety gate",
    `${reason}\n\nCommand:\n${command}`,
  );
  if (!approved) return blocked(`Blocked by user: ${reason}`);
  return undefined;
}

export default function acceleratorSafety(pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    const input = event.input as ToolInput;

    if (["read", "write", "edit", "grep", "find", "ls"].includes(event.toolName)) {
      const candidate = pathFromInput(input);
      if (candidate && isSensitivePath(candidate)) {
        return blocked(`Access to sensitive path is forbidden: ${candidate}`);
      }
      if (candidate && outsideWorkspace(candidate)) {
        return blocked(`Workspace escape is forbidden for ${event.toolName}: ${candidate}`);
      }
      if (candidate && ["write", "edit"].includes(event.toolName) && isPolicyProtectedPath(candidate)) {
        return requireApproval(ctx, `Changing accelerator security/policy file requires explicit approval: ${candidate}`, `${event.toolName} ${candidate}`);
      }
    }

    if (event.toolName !== "bash") return undefined;

    const command = typeof input.command === "string" ? input.command.trim() : "";
    if (!command) return undefined;

    if (commandTouchesSensitiveMaterial(command)) {
      return blocked("Shell access to secrets, credentials, private keys, or protected user configuration is forbidden.");
    }

    if (commandMutatesProtectedPolicy(command)) {
      return requireApproval(ctx, "Changing accelerator security/policy files through shell requires explicit approval.", command);
    }

    if (commandReferencesParentPath(command)) {
      return requireApproval(ctx, "Shell access outside the current workspace requires explicit approval.", command);
    }

    const scanned = stripWriterHeredocBodies(command);

    for (const [pattern, reason] of HARD_DENY_BASH) {
      const matched = typeof pattern === "function" ? pattern(scanned) : pattern.test(scanned);
      if (matched) return blocked(reason);
    }

    for (const [pattern, reason] of APPROVAL_BASH) {
      if (pattern.test(scanned)) return requireApproval(ctx, reason, command);
    }

    return undefined;
  });
}
