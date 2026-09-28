# Creating a Spec Kit Constitution Non-Interactively

A project constitution can be created in one pass when the project's governing principles are already known. Instead of asking the coding agent to conduct an interview, the developer supplies the confirmed principles together with enough detail to turn them into enforceable rules.

This approach is useful when a team already has engineering standards, architectural constraints, or an approved technology policy. It is faster than an interactive interview, but it transfers more responsibility to the initial prompt: missing or vague input can become missing or vague governance.

> **Version note:** The transcript contains speech-recognition errors such as “cloud code.” The demonstrated agent is Claude Code. Current Spec Kit workflow commands use `speckit`, not `/specify.constitution`. Use the exact skill form exposed by the installed integration.

## Interactive and Non-Interactive Meanings

Two different kinds of interactivity are involved, and they should not be confused.

| Context | Interactive behavior | Non-interactive behavior |
| --- | --- | --- |
| `specify init` in the terminal | Prompts for choices such as the agent integration or script type | Uses explicit arguments and the `--non-interactive` flag |
| Constitution creation in the agent chat | The agent interviews the developer before writing principles | The developer provides the principles up front in one request |

This lesson focuses primarily on the second row: **one-pass constitution creation without a discovery interview**. The terminal initializer can still be run interactively if desired.

## When to Use the One-Pass Approach

Use non-interactive constitution creation when:

- The team has already agreed on its engineering principles.
- An organization provides a reviewed standards baseline.
- The architecture and supported platforms are fixed.
- Testing, security, dependency, and documentation policies are known.
- The project is repeating a proven internal pattern.
- An existing project already makes its governing conventions clear.

Prefer the interactive approach when important choices remain unresolved, the developer does not understand the technical trade-offs, or different answers would materially change the architecture.

```text
Are the project-wide principles already known and approved?
             │
        ┌────┴────┐
       yes        no
        │          │
one-pass prompt   interactive interview
        │          │
        └────┬─────┘
             ↓
 review the generated constitution
```

Both approaches end with human review. “Non-interactive” does not mean “unreviewed.”

## Step 1: Start in the Intended Project Directory

The video uses an empty workspace. Confirm the current directory and the installed Spec Kit version before initialization:

```bash
pwd
specify version
```

In PowerShell:

```powershell
Get-Location
specify version
```

The current directory matters because Spec Kit writes project scaffolding and integration files there.

## Step 2: Initialize Spec Kit

The transcript uses `specify init .`, where `.` means the current directory. An explicit Claude Code initialization with shell scripts is:

```bash
specify init --here --integration claude --script sh
```

For PowerShell scripts on Windows:

```powershell
specify init --here --integration claude --script ps
```

If the terminal initializer itself must run without prompts, provide every required choice and add `--non-interactive`:

```bash
specify init --here --non-interactive --integration claude --script sh
```

This CLI flag does not automatically create the project constitution and does not change how much information the later constitution prompt contains.

The demonstration starts from an empty directory. Before initializing an existing repository, commit or stash current work, read the existing-project guide, and review every generated change.

## Step 3: Launch the Coding Agent

Start Claude Code from the initialized project directory:

```bash
claude
```

The constitution workflow is then invoked inside the agent chat, not in the shell.

Current integrations can expose the same logical command in different forms:

| Integration or reference style | Example |
| --- | --- |
| Claude Code or another hyphenated skills layout | `/speckit-constitution` |
| Canonical dotted notation in Spec Kit references | `/speckit.constitution` |
| Codex skills integration | `$speckit-constitution` |

Use the form generated for the selected agent. The transcript's `/specify.constitution` form mixes the terminal CLI name with the agent workflow name and should not be copied.

## Step 4: Supply the Principles Up Front

The video provides three initial values:

- Minimal dependencies and library imports
- Development grounded in current documentation
- A lightweight application

These are useful directions, but they are not yet enforceable. The words “minimal,” “current,” and “lightweight” need operational meaning.

A stronger one-pass prompt is:

```text
/speckit-constitution

Create the initial constitution for a lightweight desktop application from
the confirmed principles below. Do not conduct a discovery interview. If a
critical governance value cannot be derived safely, preserve it as an
explicit TODO instead of inventing a rule.

1. Minimal dependency surface
   - Prefer the standard library and existing approved project dependencies.
   - Every new runtime dependency requires a written justification covering
     functionality, maintenance status, security, license, and alternatives.
   - Remove unused dependencies and imports.

2. Documentation-grounded development
   - Technical decisions involving external tools or APIs must be checked
     against official documentation for the version actually used.
   - Record important version assumptions and links in the relevant plan or
     decision document.
   - Do not rely only on model memory for time-sensitive behavior.

3. Lightweight desktop operation
   - Keep startup time, memory consumption, installation size, and idle
     resource use within documented budgets.
   - If exact budgets are not approved yet, add named TODOs with an owner and
     review point rather than inventing numbers.

4. Governance
   - The constitution is the source of truth for project-wide principles.
   - Amendments require a rationale, semantic version change, and review.
   - Feature-specific behavior belongs in feature specifications, not here.
```

This prompt remains non-interactive because it provides the decisions and tells the agent how to handle genuinely missing information without launching a broad interview.

## Why the Original Principles Need Refinement

### “Minimal Dependencies”

Counting dependencies is not enough. A project with one abandoned or insecure library may be riskier than a project with several mature, focused libraries.

A useful dependency principle should state:

- What qualifies as a dependency
- Who can approve a new one
- Which evaluation criteria apply
- How unused dependencies are detected and removed
- Whether reimplementing a capability is justified

The goal is a small, explainable dependency surface—not rejecting libraries automatically.

### “Use Up-to-Date Documentation”

“Up to date” changes over time and cannot be guaranteed by wording alone. Make the behavior verifiable:

- Prefer official and version-specific sources.
- Record the library or tool version being used.
- Link important sources from plans or decision records.
- Recheck unstable behavior before implementation.
- Treat remembered syntax as a hypothesis until confirmed.

This principle is especially valuable in AI-assisted development because model knowledge and examples can lag behind current releases.

### “Lightweight”

Lightweight can refer to several different qualities:

- Download or installation size
- Cold-start time
- Idle memory consumption
- CPU or GPU usage
- Number of background processes
- Dependency count
- Architectural complexity

The constitution should identify which dimensions matter. Exact budgets can be added later, but unresolved numbers should remain visible as TODOs rather than becoming invented facts.

## Expected Output

Current Spec Kit writes the constitution to:

```text
.specify/memory/constitution.md
```

For a new project, the initial constitution normally begins at version `1.0.0`. The generated document should contain:

- Named principles
- Non-negotiable rules for each principle
- Rationales where the reason is not obvious
- Governance and amendment rules
- Ratification and amendment dates
- A semantic constitution version
- A temporary Sync Impact Report for review

The quick result shown in the video is expected because the principles are supplied directly and the workspace is empty. Speed is not evidence of correctness; the generated file still requires review.

## Example Principle Transformation

Initial phrase:

```text
Use minimal dependencies.
```

Possible constitutional form:

```text
## I. Minimal and Accountable Dependencies

The project MUST prefer the standard library and already approved
dependencies when they satisfy the requirement. Every new runtime dependency
MUST include a documented justification covering its purpose, maintenance
status, security posture, license, version policy, and rejected alternatives.
Unused dependencies and imports MUST be removed.

Rationale: each dependency expands the project's security, licensing,
compatibility, and long-term maintenance surface.
```

This version can influence planning and code review. The original three-word preference cannot.

## Review the Generated Constitution

Open `.specify/memory/constitution.md` and confirm:

1. The document contains only project-wide principles.
2. Each `MUST` reflects a decision the developer or team actually made.
3. Vague terms have metrics, evaluation criteria, or explicit TODOs.
4. Dependency policy considers risk and maintenance, not only package count.
5. Documentation requirements identify authoritative and version-relevant sources.
6. “Lightweight” names the resource dimensions that matter.
7. No product features or implementation tasks were added accidentally.
8. Dates and constitution version are correct.
9. Governance explains how future amendments are approved.
10. Unresolved placeholders are explained rather than silently guessed.

Remove or resolve the temporary review notes before committing the constitution, according to the workflow used by the installed Spec Kit version.

## Amend the Constitution Later

The video notes that the constitution can be enhanced later. Use the same constitution skill with a narrowly scoped amendment request:

```text
/speckit-constitution

Amend the lightweight-operation principle to add the approved limits below:
- cold startup under 2 seconds on the reference machine;
- idle memory below 150 MB;
- packaged application below 100 MB.

Do not change unrelated principles. Apply the appropriate semantic version
bump and explain the amendment in the Sync Impact Report.
```

Treat the numbers above only as an example. Real budgets must come from product needs, measurements, and the target environment.

Under current Spec Kit semantics:

- A breaking redefinition or removal of governance normally requires a major version increment.
- A new principle or material expansion normally requires a minor increment.
- A wording clarification without changed meaning normally requires a patch increment.

Review amendments as carefully as the initial constitution because every later feature can be affected by them.

## Existing Project Considerations

In an empty project, supplied principles can define the initial direction freely. In an existing project, a one-pass constitution must reconcile proposed rules with evidence in the repository.

Before writing it, inspect:

- Existing architecture and dependency manifests
- Test suites and CI requirements
- Security and compliance documentation
- Supported platforms and runtime versions
- Contribution and review rules
- Existing architectural decision records

Do not declare “minimal dependencies” while ignoring a large existing dependency surface. State whether the principle governs future additions, creates a migration objective, or documents an already established practice.

## Common Mistakes

- Confusing one-pass constitution creation with `specify init --non-interactive`
- Copying `/specify.constitution` instead of using the installed `speckit` skill
- Providing slogans without enforcement criteria
- Asking the model to invent “best practices” instead of supplying approved principles
- Treating the smallest dependency count as automatically safest
- Saying “use current documentation” without recording versions or sources
- Calling an application “lightweight” without defining the relevant resources
- Allowing feature requirements to become permanent governance
- Assuming an empty repository provides evidence for decisions that were never stated
- Accepting a quickly generated constitution without reviewing the file

## Next Step

After reviewing and accepting the constitution, continue with the first feature specification:

```text
/speckit-specify Describe the first product increment in terms of users,
observable behavior, constraints, and acceptance scenarios.
```

The constitution supplies the project-wide constraints. The feature specification defines what the next increment should accomplish and why.

## Key Takeaway

Non-interactive constitution creation works well when the principles are already known. Initialize Spec Kit, invoke the constitution skill in the selected coding agent, and provide the rules together with their scope, rationale, and validation expectations.

The quality of the result depends on the specificity of the input. “Minimal dependencies, current documentation, lightweight application” is a useful start, but a reliable constitution must explain how those values affect decisions and how compliance can be reviewed.

## Further Reading

- [Spec Kit core command reference](https://github.github.com/spec-kit/reference/core.html)
- [Spec Kit agentic SDD reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)
- [Supported integrations and command invocation](https://github.github.com/spec-kit/reference/integrations.html)
- [Current constitution command template](https://github.com/github/spec-kit/blob/main/templates/commands/constitution.md)
