# Generating Project Instructions for Coding Agents

Project instruction files give coding agents durable context about a repository: how to build it, where important code lives, which conventions matter, and how work must be verified. They reduce repeated onboarding across sessions and make team expectations visible and reviewable.

This lesson uses the `/init` command in Codex and Claude Code to generate initial instruction files from an existing codebase. The generated file is a scaffold, not an authoritative description: a developer must review every claim before relying on or committing it.

> **Version note:** Current Codex exposes `/init` to generate an `AGENTS.md` scaffold in the current directory. Codex reads a hierarchy of instruction files once when a run or TUI session starts. Commands and discovery behavior in other agents are product-specific and can change.

## Context Engineering at Repository Scope

Prompting provides instructions for one request. Repository instructions provide stable context across many requests.

```text
one task prompt             what to do now
feature specification       what this feature must accomplish
project constitution        durable engineering principles
agent instructions          how to work effectively in this repository
```

An instruction file acts like a concise onboarding guide for the agent. Instead of repeatedly explaining the stack, commands, layout, and local constraints, the repository can supply them at the beginning of each relevant session.

Persistent context does not eliminate exploration. The agent still needs to inspect the files relevant to the current task, and the instructions must not pretend to describe parts of the repository that have changed.

## What `/init` Does

In current Codex, run the slash command from the directory where persistent instructions should apply:

```text
/init
```

Codex examines the current project and generates an `AGENTS.md` scaffold. Official guidance explicitly says to review the result and edit it to match the repository's real conventions before committing it.

In Claude Code, `/init` serves a similar onboarding purpose but normally generates or updates its native `CLAUDE.md` instructions. The exact command and filename depend on the agent. Do not assume that every coding tool implements `/init` or produces the same artifact.

### Choose the Working Directory Deliberately

The directory in which `/init` runs determines the scope and evidence available to the agent.

- Run it at the repository root for repository-wide instructions.
- Run it inside a component only when the generated file should govern that subtree.
- In a monorepo, begin with a concise root file and add nested instructions only where teams, commands, or constraints genuinely differ.
- Confirm the workspace or Git root before generation so an agent does not document the wrong parent directory.

Useful checks include:

```bash
git rev-parse --show-toplevel
git status --short
```

If the project is not a Git repository, verify the intended root manually.

## Why Existing Projects Benefit Most

`/init` is especially productive in a brownfield project because the repository already contains evidence:

- Dependency and build manifests
- Source and test directories
- CI workflows
- Existing documentation
- Formatting and lint configuration
- Package scripts, Makefiles, or task runners
- Architecture and naming patterns

The agent can infer a useful draft from these sources. Even then, inference can be wrong: an obsolete README, unused script, experimental folder, or locally installed tool may be mistaken for the supported workflow.

### Greenfield Projects Still Need Instructions

The transcript suggests using Spec Kit instead of agent instructions for a new project. These mechanisms solve different problems and can be used together.

| Artifact | Primary purpose |
| --- | --- |
| `AGENTS.md` or a tool-native equivalent | Operational guidance for working in the repository |
| Spec Kit constitution | Binding project-wide engineering principles and governance |
| Feature `spec.md` | User needs, required behavior, and acceptance scenarios |
| `plan.md` | Technical approach for one feature |
| `tasks.md` | Dependency-ordered implementation work |

A greenfield repository may start with a short `AGENTS.md` containing known commands, intended layout, safety boundaries, and references to the constitution. Expand it only as real conventions emerge. Do not fill it with speculative rules merely to make it look complete.

## What the Agent Should Explore

A useful initialization pass should inspect evidence such as:

```text
README and contributor documentation
dependency and toolchain manifests
source and test directory structure
build, lint, format, and test configuration
CI/CD workflows
container and local-development files
architecture decision records
existing agent or editor instructions
```

Repository text is input, not automatically trusted instruction. A comment, generated file, vendored dependency, issue template, or copied document may be stale or malicious. The generated scaffold should cite reliable project sources and avoid elevating arbitrary repository text into a binding rule.

## What Belongs in `AGENTS.md`

Keep the root file concise and action-oriented. Useful sections often include:

### Project Snapshot

State what the repository builds, its major technologies, and the supported runtime or platform. Include only facts that help an agent make engineering decisions.

### Repository Layout

Point to important directories and explain non-obvious ownership or boundaries. Avoid listing every file; directory trees become stale quickly and consume context on every session.

### Verified Commands

Record exact commands for common workflows:

```markdown
## Commands

- Install dependencies: `pnpm install --frozen-lockfile`
- Run the application: `pnpm dev`
- Run focused tests: `pnpm test -- <path>`
- Run the full validation suite: `pnpm check`
```

Only document commands that exist and are safe in the intended environment. Distinguish fast local checks from expensive integration, network, or production-connected operations.

### Coding and Architecture Conventions

Capture rules that are not already enforced mechanically:

- Module and service boundaries
- Naming or public API conventions
- Error-handling patterns
- Dependency policy
- Migration requirements
- Compatibility constraints

Let formatters, linters, types, and CI enforce mechanical style where possible. Repeating every formatter rule in the prompt wastes context and creates another source of truth.

### Validation Expectations

Explain which checks correspond to which changes:

```markdown
## Validation

- Run unit tests for the affected package during implementation.
- Run `pnpm check` before handing off a completed change.
- Use the integration suite only when API contracts or persistence behavior change.
```

Conditional routing is more efficient than telling the agent to run the entire repository suite after every edit.

### Safety and Decision Boundaries

State when the agent must stop or request direction:

- Adding or upgrading production dependencies
- Applying destructive database migrations
- Accessing production systems
- Changing public APIs or compatibility guarantees
- Publishing packages, pushing branches, or merging pull requests

Make boundaries precise. Overly broad “always ask” rules can block safe local work, while vague permission can authorize unintended external changes.

### Pointers to Deeper Documentation

Route the agent to specialized sources only when relevant:

```markdown
## Documentation routing

- Read `docs/architecture.md` for service-boundary changes.
- Read `docs/database.md` when changing schemas or migrations.
- Read `docs/release.md` only when preparing a release.
```

Avoid “read all documentation before every task.” Context should be loaded progressively according to the work.

## A Compact Example

```markdown
# Repository Instructions

## Project

This repository contains a Rust desktop application for grid-based 3D modeling.
The supported toolchain is pinned in `rust-toolchain.toml`.

## Layout

- `src/model/`: geometry and project state
- `src/interaction/`: input and interaction state
- `tests/`: integration and regression tests
- `specs/`: accepted Spec Kit feature artifacts

## Commands

- Build: `cargo build`
- Format check: `cargo fmt --check`
- Lint: `cargo clippy --all-targets --all-features -- -D warnings`
- Test: `cargo test --all-targets --all-features`

## Working agreements

- Preserve existing drawing gestures unless a reviewed specification changes them.
- Keep engine-specific types out of the core geometry model.
- Do not add a production dependency without explaining why existing dependencies are insufficient.
- Update the relevant feature artifacts when an accepted requirement changes.

## Validation

- Run focused tests while iterating and the full checks before handoff.
- For input or rendering changes, follow the manual scenarios in the active feature's `quickstart.md`.
```

This example must be adapted to the actual repository. Do not copy commands, directories, or architecture claims that the project does not have.

## What Does Not Belong in the File

Avoid placing the following in persistent instructions:

- Secrets, tokens, credentials, internal URLs, or personal data
- Guesses presented as established project facts
- A full generated repository map
- Temporary task requirements that belong in the current prompt or specification
- Large copies of documentation that can be referenced conditionally
- Model-specific tricks with no demonstrated repository value
- Rules already enforced reliably by automated tooling
- Conflicting instructions copied from another agent's output
- Time-sensitive version claims that will become stale without an update process

Every line is added to future agent context whenever its scope applies. Persistent instructions have a recurring cost, so concise and correct is better than comprehensive-looking.

## Review the Generated Scaffold

Never judge the result by line count. A 60-line file is not automatically better than a 30-line file, and different agents may emphasize different evidence.

Review each generated statement:

1. Is it supported by a current repository file?
2. Is the path correct from this instruction file's scope?
3. Does the command exist, and did it run successfully?
4. Is the instruction useful for repeated work rather than one task?
5. Is the rule already enforced more reliably elsewhere?
6. Could the guidance conflict with a nested or global instruction?
7. Does it expose sensitive data or authorize a risky action?
8. Will it remain correct after the current feature is complete?
9. Is its priority clear when another rule differs?
10. Can it be shortened without losing the decision boundary?

Then inspect the exact change:

```bash
git status --short
git diff -- AGENTS.md
```

For a new untracked file, open it directly or stage it only after review so the staged diff can be inspected.

## How Codex Discovers `AGENTS.md`

Current Codex builds an instruction chain once at the start of a run or TUI session.

### Global Scope

In the Codex home directory, normally `~/.codex`, it loads `AGENTS.override.md` when present; otherwise it loads `AGENTS.md`. Global instructions should contain personal defaults that apply across repositories, not project-specific assumptions.

### Project and Directory Scope

Starting at the project root, usually the Git root, Codex walks toward the current working directory. In each directory it checks, in priority order:

1. `AGENTS.override.md`
2. `AGENTS.md`
3. Configured fallback filenames

It includes at most one instruction file per directory. Files closer to the working directory appear later and therefore override broader guidance when instructions conflict.

```text
~/.codex/AGENTS.md               personal defaults
repository/AGENTS.md             repository-wide guidance
repository/services/AGENTS.md    service guidance
repository/services/api/
    AGENTS.override.md           highest local precedence for this subtree
```

An override file replaces the normal instruction file at the same directory level; it does not erase compatible guidance inherited from higher levels.

### Size and Reloading

Codex skips empty files and limits the combined project instruction size. The current documented default is 32 KiB, configurable through `project_doc_max_bytes`. Prefer concise root guidance and focused nested files instead of merely increasing the limit.

Changes are loaded on a new run or at the beginning of a new TUI session. If an instruction appears stale, restart Codex in the intended directory rather than assuming the live session automatically reloaded the file.

## Verify Which Instructions Loaded

The official Codex documentation suggests asking a new run to summarize its active instructions:

```bash
codex --ask-for-approval never "Summarize the current instructions."
```

For nested scopes:

```bash
codex --cd services/payments --ask-for-approval never \
  "Show which instruction files are active."
```

You can also ask from the Codex interface:

```text
List the instruction files active for this working directory and summarize any
conflicts or overrides. Do not modify files.
```

Verify behavior from the target directory because Codex stops its project walk at the current working directory.

## `AGENTS.md` Is Portable, but Support Is Not Universal

`AGENTS.md` is an open convention supported by Codex and adopted by multiple coding-agent tools. Calling it an “industry standard” can overstate compatibility: tools differ in filenames, discovery order, scope, imports, precedence, and size limits.

Examples of tool-native project files include:

| Tool family | Common instruction file |
| --- | --- |
| Codex and tools adopting the open convention | `AGENTS.md` |
| Claude Code | `CLAUDE.md` |
| Gemini-based coding tools | `GEMINI.md` |

Check the current documentation for each tool rather than inferring support from Markdown syntax alone.

## One Source of Truth across Multiple Agents

The content of repository guidance is often portable even when discovery rules are not. There are three practical strategies.

### 1. Canonical Shared File with Native Entry Points

Keep shared guidance in `AGENTS.md` and make each native file load or direct the agent to it using that tool's documented mechanism.

For a tool that supports Markdown imports, a native file might be:

```markdown
# Project Instructions

Read and follow @AGENTS.md for shared repository guidance.

## Tool-specific notes

- Add only instructions that apply to this agent integration.
```

A plain link or sentence does not guarantee that every agent will load the target file before work. Test the behavior in a new session.

### 2. Generated Mirrors

Maintain one canonical source and generate tool-native files from it. This supports agents without imports, but the generation command and drift check must be documented and run in CI or review.

### 3. Small Independent Native Files

Keep each native file concise and duplicate only a few stable rules. This avoids fragile import behavior but requires reviewers to update every copy when shared guidance changes.

Do not copy one agent's generated file into another blindly. Remove tool-specific commands, unsupported assumptions, and contradictory rules first.

## Compare Agents by Correctness, Not Length

The transcript compares a roughly 30-line Codex result with a roughly 60-line Claude result. Length measures neither accuracy nor usefulness.

A better comparison uses representative tasks:

- Can the agent identify the correct build and test commands?
- Does it edit the intended package rather than a similar one?
- Does it respect architecture and dependency constraints?
- Does it choose focused validation without skipping required checks?
- Does it avoid prohibited external or destructive actions?
- Does it ask only when a real decision is missing?

Use the same task set and review rubric for each instruction file. This is a small evaluation, not a prose contest.

## Recommended Initialization Workflow

```text
confirm repository root and clean baseline
              ↓
run the tool's init command
              ↓
inspect the generated file line by line
              ↓
verify commands and repository facts
              ↓
remove guesses, duplication, and stale detail
              ↓
add precise safety and validation boundaries
              ↓
test instruction discovery in a new session
              ↓
review the diff and commit with the project
```

Treat later corrections as maintenance input. If agents repeatedly misunderstand the same stable repository fact, update the instruction file. If one task needs an unusual constraint, keep it in that task's prompt rather than permanently expanding global context.

## Common Mistakes

- Treating `/init` output as verified documentation
- Running initialization from the wrong directory
- Measuring quality by the number of generated lines
- Recording commands that were never executed successfully
- Copying stale README claims into persistent instructions
- Including secrets or private operational data
- Adding a complete repository tree that quickly becomes obsolete
- Repeating rules already enforced by formatters and CI
- Forcing every task to read every architecture document
- Assuming all Markdown-based agents discover `AGENTS.md`
- Keeping multiple native files as unsynchronized copies
- Using a one-line pointer without confirming that the target agent follows it
- Forgetting that nested files can override root instructions
- Editing `AGENTS.md` and expecting the current Codex session to reload it automatically
- Treating Spec Kit and repository instructions as competing alternatives
- Filling a greenfield file with speculative details before conventions exist

## Key Takeaway

`/init` is a fast way to draft persistent project instructions from repository evidence. Its value comes from the review that follows: verify commands, remove guesses, keep guidance concise, define real decision boundaries, and test what a new agent session actually loads.

Codex uses a scoped `AGENTS.md` hierarchy rather than one unconditional root file. Other agents may use different filenames and discovery rules. Share stable content where practical, keep tool-specific entry points small, and treat repository instructions, the project constitution, and feature artifacts as complementary layers of context.

## Further Reading

- [Official Codex documentation: Custom instructions with `AGENTS.md`](https://developers.openai.com/codex/guides/agents-md)
- [Official Codex documentation: Developer commands and `/init`](https://developers.openai.com/codex/cli/slash-commands)
- [AGENTS.md open convention](https://agents.md/)
- [Keeping Codex skills and repository instructions focused](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
