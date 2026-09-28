# Deriving a Spec Kit Constitution from an Existing Project

Spec Kit can be adopted in an existing—or brownfield—codebase without recreating the entire system from specifications. The coding agent studies the repository, identifies documented and consistently enforced project rules, and helps express them as a constitution for future work.

This lesson demonstrates the approach with the open-source [Orbiter Space Flight Simulator](https://github.com/orbitersim/orbiter). Unlike a greenfield project, an existing repository already contains architecture, compatibility constraints, build conventions, tests, public interfaces, and licensing decisions. The task is to discover and validate those rules rather than invent a new project identity.

> **Version note:** Current Spec Kit guidance recommends adopting the toolkit from a clean, reviewable baseline, initializing it in the repository root, and capturing principles that are already evidenced by the project or explicitly approved by its maintainers.

## What Brownfield Adoption Means

A brownfield project contains existing code and history. Its constitution should answer questions such as:

- Which current behaviors and interfaces must remain compatible?
- Which architectural boundaries are intentional?
- Which build and test procedures are authoritative?
- Which domain invariants must never be weakened?
- Which dependencies, platforms, and toolchains are supported?
- Which licensing constraints apply to different components?
- Which apparent patterns are real policy, and which are merely historical accidents?

The constitution governs future development. It does not need to retroactively specify every existing feature before useful work can begin.

## Evidence Before Principles

In a new project, the team can choose principles freely. In an existing project, every inferred principle should be traceable to evidence.

Useful evidence sources include:

| Evidence source | What it can reveal |
| --- | --- |
| `README.md` and user documentation | Product purpose, supported use cases, platform expectations |
| Build instructions and manifests | Toolchain, supported configurations, dependencies |
| Architecture documentation and ADRs | Intended boundaries and design decisions |
| Public headers and SDK documentation | Compatibility surfaces and extension contracts |
| Tests and reference scenarios | Verified behavior and quality gates |
| CI workflows | Checks that are actually enforced |
| Contribution guide | Review, formatting, and change-management policy |
| License files and dependency notices | Distribution and attribution obligations |
| Git history and release notes | Stability promises and evolution patterns |

Code is evidence too, but repeated code patterns do not automatically represent approved policy. Legacy constraints, temporary workarounds, and inconsistent conventions can all appear frequently.

## Workflow Overview

```text
Clone the complete repository
            ↓
Record a clean, reviewable baseline
            ↓
Inspect authoritative project evidence
            ↓
Initialize Spec Kit in place
            ↓
Review initialization changes
            ↓
Ask the agent for an evidence-backed draft
            ↓
Verify every principle and uncertainty
            ↓
Adopt a bounded first feature
```

## Step 1: Clone the Repository Correctly

Orbiter's official README provides both SSH and HTTPS clone commands and includes submodules.

SSH form:

```bash
git clone --recursive git@github.com:orbitersim/orbiter.git
```

HTTPS form:

```bash
git clone --recursive https://github.com/orbitersim/orbiter.git
```

The transcript first encounters an access error. A public repository does not require write access to clone through HTTPS. If the SSH form reports that it cannot read from the repository, common causes include a missing SSH key, an incorrect remote URL, or an account configuration problem. Switching to the official HTTPS URL is often the simplest solution for read-only access.

Do not delete directories or retry commands blindly. First inspect the exact target path and error, especially when a partially created directory may contain work.

### Wait for the Clone to Finish

Do not initialize Spec Kit or ask an agent to analyze the project while `git clone` is still writing files. A partial checkout can produce an incomplete and misleading constitution.

After cloning, enter the repository and verify it:

```bash
cd orbiter
git status --short
git submodule status
git rev-parse HEAD
```

Record the commit SHA used for the analysis. A constitution derived from a moving default branch is harder to reproduce.

### Large Repository Options

For a temporary study checkout, a shallow clone may reduce history transfer:

```bash
git clone --depth 1 --recurse-submodules https://github.com/orbitersim/orbiter.git
```

This saves time but removes most history, which can be valuable when investigating why an interface or convention exists. Use a full clone when history is part of the evidence.

## Step 2: Create a Reviewable Baseline

Before Spec Kit changes the checkout:

1. Confirm that `git status --short` is empty.
2. Record the current commit.
3. Create a branch dedicated to adopting Spec Kit.

Example:

```bash
git switch -c chore/adopt-spec-kit
```

If the repository already contains local changes, commit them, stash them, or create a separate worktree. The goal is to make every Spec Kit-generated file visible in a normal diff.

## Step 3: Inspect the Repository Before Asking the Agent

Do a short human-led orientation pass first. For Orbiter, useful starting points include:

- `README.md`
- `COMPILE.md`
- `LICENSE`
- `CMakeLists.txt` and `CMakePresets.json`
- `.github/`
- `Src/`
- `Tests/`
- `Orbitersdk/`
- `OVP/`
- `Extern/`

The official repository describes Orbiter as a spaceflight simulator based on Newtonian mechanics. Its core is published under the MIT License, while the D3D9Client graphics engine uses LGPL licensing. The documented build uses CMake and Microsoft Visual Studio, and the application has explicit platform and architecture constraints.

These are facts that can seed the analysis. They do not by themselves prove every principle shown in the generated constitution.

## Step 4: Initialize Spec Kit in the Existing Repository

From the repository root, initialize the selected coding-agent integration. For Claude Code with shell scripts:

```bash
specify init --here --force --integration claude --script sh
```

For PowerShell scripts on Windows:

```powershell
specify init --here --force --integration claude --script ps
```

`--here` targets the current directory. `--force` acknowledges that the directory is non-empty and allows Spec Kit to merge its managed files. It should be used only after establishing the clean baseline.

Initialization adds `.specify/` assets and agent-specific command or skill files. It does not automatically understand the application, document existing behavior, or validate inferred principles.

## Step 5: Review Initialization Before Continuing

Inspect the repository immediately after initialization:

```bash
git status --short
git diff --stat
git diff
```

Remember that ordinary `git diff` does not show the content of new untracked files. Open those files explicitly or stage them only when you are ready to review the staged diff.

Confirm that:

- Application source files were not changed unexpectedly.
- Spec Kit files were created at the intended repository root.
- The selected agent integration was installed.
- Existing project instructions were not overwritten unintentionally.
- No secrets, machine-local paths, or generated assets were introduced.

Stop and investigate before creating a constitution if initialization touched unrelated files.

## Step 6: Ask for an Evidence-Backed Constitution

Launch Claude Code from the repository root:

```bash
claude
```

Then invoke the constitution skill in the form exposed by the installed integration. A strong brownfield request is:

```text
/speckit-constitution

Draft a project constitution from the existing repository.

Before writing it, inspect README.md, COMPILE.md, license files, build
configuration, CI workflows, tests, public SDK headers and documentation,
extension boundaries, and relevant source structure.

For every proposed principle:
1. cite the repository evidence that supports it;
2. distinguish an established rule from a recommendation;
3. mark conflicts or missing evidence as TODOs;
4. do not convert accidental legacy patterns into permanent policy;
5. do not modify application source code.

Preserve compatibility and licensing obligations that are explicitly
documented. Ask focused questions only when a missing decision would
materially change project governance.
```

The constitution workflow writes its result to:

```text
.specify/memory/constitution.md
```

## Explore Large Repositories Deliberately

Large projects can exceed an agent's useful context if scanned indiscriminately. The agent should investigate in layers:

1. Read the top-level documentation and manifests.
2. Map major directories and public interfaces.
3. Inspect CI and test entry points.
4. Search for evidence related to each candidate principle.
5. Open representative files instead of every source file.
6. Exclude binaries, generated output, external dependencies, and large assets unless directly relevant.

For example, physical simulation rules may require inspecting numerical code and reference scenarios, while licensing rules require license and third-party notice files. Those questions do not need the same repository context.

The time required for analysis depends on repository size and evidence quality. A fast result should not be assumed complete, and a long analysis is not automatically accurate.

## Orbiter Case Study: Candidate Principles

The video shows an AI-generated constitution with principles resembling the following.

### 1. Physical Realism

Orbiter's README explicitly describes a simulator based on Newtonian mechanics. It is therefore reasonable to propose physical fidelity as a core project principle.

However, the constitution still needs to identify:

- Which physical models are authoritative
- Which approximations are accepted
- How regressions are detected
- Which reference scenarios or tolerances apply

“Realistic physics” alone is too vague to govern implementation.

### 2. Numerical Accuracy

Stable orbital simulation depends on numerical behavior and conserved quantities. The generated constitution may propose integration accuracy, stable reference frames, and regression scenarios as non-negotiable constraints.

These details must be confirmed against source code, test data, project documentation, and maintainer expectations. An agent's knowledge of simulation software is not repository evidence.

### 3. Stable Public SDK and Capability Model

The repository contains an `Orbitersdk/` area and public extension surfaces. That supports investigating compatibility as a possible governing principle.

The existence of an SDK does not automatically prove a strict backward-compatibility guarantee. Before writing `MUST preserve API compatibility`, look for versioning policy, release notes, public header conventions, and maintainer statements.

### 4. Pluggable Architecture

Orbiter includes distinct components and extension-related areas such as SDK and graphics or vessel modules. The generated constitution identifies a pluggable architecture as a project value.

This may be accurate, but the constitution should name the actual extension boundaries and the dependency direction they enforce. “Pluggable” should not become permission to add arbitrary abstraction layers.

### 5. Test and Reference-Scenario Coverage

The repository contains a `Tests/` directory, which is evidence that automated verification exists. It does not prove that every critical path is covered or that a particular coverage threshold is enforced.

A validated principle might require:

- Existing tests to continue passing
- Physics changes to include numerical regression cases
- Public SDK changes to include compatibility checks
- Reference scenarios to define tolerances explicitly

Only adopt these rules if the project already follows them or maintainers agree to introduce them.

### 6. Portable and Reproducible Builds

The repository documents CMake and Visual Studio build procedures. A generated constitution may promote build reproducibility or portability.

Do not overstate current support. “Uses CMake” does not necessarily mean “builds reproducibly on every platform.” Record the actual supported toolchain and treat broader portability as a proposed goal unless CI or documentation proves it.

### 7. Licensing Boundaries

The official README states that the Orbiter core is MIT-licensed and the D3D9Client graphics engine is LGPL-licensed. A constitution can require future changes to preserve component-specific licensing and attribution obligations.

Do not summarize a mixed repository simply as “MIT licensed.” Inspect third-party code and dependency licenses before making distribution decisions.

## Generated Principles Are Candidates, Not Official Policy

The constitution produced in the video is a useful draft derived by an AI agent. It should not be described as the official Orbiter constitution unless the upstream maintainers review and adopt it.

Classify each statement:

| Classification | Meaning | Action |
| --- | --- | --- |
| Evidenced | Explicitly documented or consistently enforced | Cite the evidence and retain it |
| Proposed | Sensible future rule without current proof | Seek maintainer approval before making it binding |
| Conflicting | Repository evidence disagrees | Resolve the conflict; do not hide it |
| Unknown | Evidence is insufficient | Add a named TODO or ask a maintainer |

This prevents a plausible-sounding AI summary from rewriting project history.

## Review the Constitution Against the Repository

For every principle in `.specify/memory/constitution.md`, ask:

1. Which repository file or maintained practice supports it?
2. Is it descriptive of current behavior or prescriptive for future work?
3. Does any existing component violate it?
4. Would enforcing it break compatibility or block necessary maintenance?
5. Is the rule measurable during planning, testing, or review?
6. Does it reflect an upstream maintainer decision?
7. Are platform, SDK, build, and licensing claims precise?
8. Are exceptions and amendment procedures documented?

If the repository contradicts a desirable rule, record it as a migration goal with scope and ownership rather than pretending that compliance already exists.

## Commit Adoption Separately

Keep the Spec Kit adoption changes separate from product changes when practical. A focused commit or pull request lets maintainers review:

- Spec Kit infrastructure
- Agent integration files
- The proposed constitution
- Evidence and open questions
- No unrelated application behavior

A suitable commit message might be:

```text
docs: adopt Spec Kit and add evidence-backed project constitution
```

Do not commit a generated constitution to an upstream open-source project without following its contribution process and obtaining appropriate review.

## Choose a Bounded First Change

After the constitution is accepted, use Spec Kit for the next independently reviewable change. Do not begin by asking the agent to retroactively specify the entire simulator unless that inventory is itself the intended deliverable.

The normal sequence is:

```text
constitution
     ↓
specify a bounded change
     ↓
clarify compatibility questions
     ↓
plan against the existing architecture
     ↓
tasks → analyze → implement → converge
```

The existing codebase remains implementation context. The new feature specification describes the intended change and the behavior that must remain intact.

## Common Mistakes

- Running analysis before the clone and submodules finish
- Using an SSH clone URL without configured SSH credentials and assuming the repository is private
- Initializing Spec Kit with an uncommitted, unreviewable working tree
- Running `--force` without first verifying the target directory
- Asking the agent to scan a huge repository without an evidence strategy
- Treating repeated legacy patterns as intentional architecture
- Promoting reasonable suggestions into “existing principles” without proof
- Assuming the presence of tests proves adequate coverage
- Claiming SDK compatibility without a documented compatibility policy
- Claiming cross-platform or reproducible builds from CMake usage alone
- Ignoring component-specific and third-party licenses
- Trying to specify the entire existing application before making one bounded change

## Key Takeaway

Spec Kit can add spec-driven development to an existing project without starting over. The safe process is to clone a complete repository, establish a clean baseline, initialize Spec Kit in place, review the generated infrastructure, and derive a constitution from authoritative evidence.

The agent can accelerate discovery, but it cannot declare official project policy. Every inferred principle must be confirmed against documentation, code, tests, CI, history, licenses, and maintainer intent. The result should govern future changes without rewriting the project's past.

## Further Reading

- [Adopting Spec Kit in an existing project](https://github.github.com/spec-kit/guides/existing-projects.html)
- [Spec Kit agentic SDD reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)
- [Evolving specifications in existing projects](https://github.github.com/spec-kit/guides/evolving-specs.html)
- [Orbiter Space Flight Simulator repository](https://github.com/orbitersim/orbiter)
