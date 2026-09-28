# Creating a Spec Kit Constitution Interactively

A project constitution defines the durable principles that guide every later specification, plan, task list, and implementation decision. It is the first governance artifact to establish after initializing Spec Kit in a project.

This lesson demonstrates an interactive approach with Claude Code. The developer begins with only a project idea and asks the agent to discover the necessary principles through focused questions. This is especially useful when the developer understands the desired product but does not yet know which technical and engineering constraints should become permanent project rules.

> **Version note:** Spec Kit command names and integration layouts evolve. Current documentation uses `speckit` in workflow command names. The transcript's `/specify.constitution` form should not be copied. Use the command or skill form exposed by the integration installed in the project.

## What a Project Constitution Is

A constitution is the project's highest-level engineering policy. It captures decisions that should remain valid across many features, such as:

- Architectural boundaries
- Supported platforms
- Dependency policy
- Testing and quality requirements
- Performance expectations
- Security and privacy principles
- Accessibility and user-experience standards
- Documentation and compatibility rules
- Governance and amendment procedures

It is usually established once near the beginning of a project and then amended deliberately when project governance changes. “Once per project” does not mean immutable; it means that a new constitution should not be regenerated independently for every feature.

## What a Constitution Is Not

A constitution is not:

- A feature specification
- A backlog or task list
- A complete architecture document
- A collection of generic aspirations
- A place to request implementation work

For example, “users can export a model as OBJ” is normally a feature requirement. “The project MUST use open, documented file formats and MUST avoid proprietary lock-in” can be a project principle.

A technology choice belongs in the constitution only when it is intended to be a binding project-wide constraint. Otherwise, it should be selected later during technical planning.

## Workflow Overview

```text
Install the Specify CLI
        ↓
Initialize Spec Kit in the project
        ↓
Launch the selected coding agent
        ↓
Run the constitution skill
        ↓
Answer high-impact questions
        ↓
Review .specify/memory/constitution.md
        ↓
Begin the first feature specification
```

## Step 1: Prepare the Workspace

The video starts from an empty directory. Confirm that the terminal is in the intended project directory before initialization:

```bash
pwd
```

On PowerShell, the equivalent check is:

```powershell
Get-Location
```

Also confirm that the Spec Kit CLI is available:

```bash
specify version
```

Initialization writes project scaffolding and agent-integration files. Do not run it in a random directory merely because that directory happens to be open in the terminal.

## Step 2: Initialize Spec Kit for Claude Code

The transcript uses `specify init .`, where `.` means the current directory. Current documentation also provides the more explicit `--here` option.

For Claude Code with shell scripts on Linux or macOS:

```bash
specify init --here --integration claude --script sh
```

For Claude Code with PowerShell scripts on Windows:

```powershell
specify init --here --integration claude --script ps
```

The shorter interactive form is also valid:

```bash
specify init .
```

When the integration is not specified, an interactive terminal can ask which supported coding agent to configure. Supplying `--integration claude` makes the intended integration explicit and reproducible.

Initialization creates shared Spec Kit assets under `.specify/` and installs the integration-specific skills for Claude Code under `.claude/skills/` in current releases.

### Existing Projects Require Additional Care

The demonstration uses an empty directory. For an existing repository:

1. Commit or stash current work.
2. Create a separate branch if the project uses version control.
3. Read the existing-project guide.
4. Initialize from the repository root.
5. Review every generated or changed file.

Current Spec Kit supports initialization in a non-empty directory with `--force`, but that flag acknowledges possible managed-file changes. It should not be used before creating a reviewable baseline.

## Step 3: Launch Claude Code in the Project

After initialization, start Claude Code from the same project directory:

```bash
claude
```

The transcript's references to “cloud code” are transcription errors. The demonstrated tool is **Claude Code**.

The Spec Kit workflow stages are invoked inside the coding agent's chat. They are not ordinary shell commands.

## Step 4: Invoke the Constitution Skill

The logical command is named `speckit.constitution`, while the visible syntax depends on the selected agent and integration mode.

| Context | Typical form |
| --- | --- |
| Canonical dotted notation in Spec Kit references | `/speckit.constitution` |
| Skills exposed with hyphenated slash commands | `/speckit-constitution` |
| Codex skills integration | `$speckit-constitution` |

For the Claude Code skills layout demonstrated in this lesson, use the constitution skill shown by Claude Code, commonly:

```text
/speckit-constitution
```

If that spelling is not recognized, inspect the skills generated in `.claude/skills/` and use the form shown by the installed integration. Do not substitute `/specify.constitution`; `specify` is the terminal CLI name, while the agent workflow uses `speckit` command names.

## Step 5: Request an Interactive Interview

Running the constitution skill with no useful context may cause the agent to infer decisions from a sparse repository or produce generic principles. Provide the project idea and explicitly ask for questions before the constitution is written.

Example:

```text
/speckit-constitution

Help me establish the constitution for a lightweight native desktop
application for creating 3D models and scenes.

I am not an experienced desktop application developer. Interview me before
writing the constitution. Ask focused questions about users, platforms,
architecture, data ownership, dependencies, testing, performance, UX,
accessibility, licensing, and governance. Explain the important trade-offs.
Do not invent a binding principle when I have not made the decision.
```

This prompt supplies product direction without pretending that every engineering decision is already known.

The developer in the video enters the command but pauses before submitting it. This is a useful habit: review the request before starting a workflow that will write a governance artifact.

## What the Interview Should Clarify

The agent's questions should focus on decisions that materially change the project.

| Area | Example question | Why it matters |
| --- | --- | --- |
| Product | Who is the primary user? | Determines acceptable complexity and UX expectations |
| Platform | Which operating systems must be supported initially? | Affects frameworks, packaging, testing, and CI |
| Architecture | Native application, web application, or hybrid? | Shapes the entire technical foundation |
| Technology | Is a language or framework a binding constraint? | Determines whether it belongs in the constitution or plan |
| Data | Local-first, cloud-first, or synchronized? | Affects privacy, storage, failure modes, and offline behavior |
| Dependencies | Prefer proven libraries or minimal dependencies? | Changes maintenance, security, and implementation cost |
| Testing | Strict TDD, required automated tests, or risk-based testing? | Defines a non-negotiable quality gate |
| Performance | What measurable responsiveness is required? | Converts “fast” into an enforceable expectation |
| UX | What must a first-time user accomplish without help? | Makes ease of use testable |
| Accessibility | Which input and visual-accessibility baselines apply? | Prevents accessibility from becoming an afterthought |
| Formats | Which import and export formats are required? | Affects interoperability and scope |
| Governance | Who approves amendments and exceptions? | Defines how the constitution can evolve |

The goal is not to maximize the number of questions. The goal is to expose the few choices whose answers would change architecture, delivery, or acceptance criteria.

## Case Study: Native 3D Modeling Application

The lesson uses a hypothetical desktop tool for non-experts who want to create 3D models and scenes. The interactive discussion leads toward the following decisions.

### Product and Platform

- The initial audience is everyday non-expert users.
- The first supported platform is Linux.
- The application is native rather than browser-based.
- The first release is intentionally narrower than a mature professional modeling suite.

Linux-first scope is not presented as universally superior. It is selected because the developer can build and test on Linux immediately and does not currently have a suitable Windows validation environment.

### Technical Foundation

- A native Rust foundation with the Bevy engine is considered a good fit for a custom lightweight 3D tool.
- Native C++ is discussed as an alternative.
- The choice should optimize for responsiveness and a smaller footprint instead of web deployment convenience.

If Rust and Bevy are intended to remain binding for the whole project, they can become constitutional constraints. If the team is still evaluating them, record the evaluation in technical planning rather than prematurely freezing the choice.

### Data and File Handling

- User projects remain offline and local by default.
- The application starts with its own open, documented project format.
- Additional export formats can be added later as explicit features.

This keeps the initial scope manageable while making data ownership and future interoperability visible.

### Quality and Testing

- Testing discipline must be explicit rather than described vaguely as “good test coverage.”
- The developer must choose between strict test-first development, required automated tests, or a risk-based approach.
- Critical project behavior and file integrity require repeatable verification.

### Performance

- Startup should be fast.
- Interactive modeling should remain responsive.
- The application should run acceptably on integrated graphics available to the developer's Linux test environment.

These statements still need measurable targets before they can act as reliable gates. For example, define a reference machine, representative scene, startup threshold, interaction frame budget, and memory limit.

### User Experience

- A first-time user should complete a basic model without reading a manual.
- Common actions should require very few interactions; the demonstration proposes a two-click budget.
- Actions that change the model should be reversible.
- The interface should expose only the controls needed for the current task.

“No manual required” and “two clicks” are testable only when tied to named user journeys. A constitution should state how the principle will be evaluated rather than relying on slogans.

### Accessibility

- Keyboard navigation should cover essential workflows.
- Visual design should remain usable for people with common forms of color-vision deficiency.
- Accessibility expectations should be part of the baseline, not postponed without an explicit scope decision.

### Governance

- The project initially has a solo maintainer.
- Licensing should be resolved before public distribution.
- The maintainer decides constitutional amendments and documents the reason for each material change.

## A Second Example: Minimal Agent Harness

The video also shows a constitution from a different hobby project: a minimal coding-agent harness. Its principles include:

- Simplicity before feature breadth
- Minimal external dependencies
- Avoidance of excessive abstraction and over-engineering
- Go-only implementation
- Preference for small, understandable components

These principles make sense for a minimal harness but would be inappropriate as universal software-engineering rules. For example, implementing common capabilities from scratch can increase security and maintenance risk. The constitution must reflect the specific project's goals and include the rationale behind unusual constraints.

## Turn Answers into Enforceable Principles

A good constitution translates preferences into rules that can guide reviews.

Weak wording:

```text
The application should be fast, easy to use, and mostly offline.
```

Stronger wording:

```text
## Offline-First Data Ownership

Project files MUST remain usable without a network connection. Core modeling
workflows MUST NOT require a cloud account or remote service. Any future
network synchronization MUST be optional, disclose transmitted data, and
preserve a complete local project copy.

Rationale: users retain control of their work, and core functionality remains
available when connectivity or a remote service fails.
```

The stronger version states what is mandatory, identifies the boundary of the rule, and explains why the constraint exists.

## Review the Generated Constitution

Current Spec Kit writes the project constitution to:

```text
.specify/memory/constitution.md
```

Review the file before accepting it. Confirm that:

1. Every principle reflects an actual decision.
2. Mandatory language such as `MUST` is reserved for genuine non-negotiable rules.
3. Vague goals have measurable validation criteria or a follow-up action.
4. Feature-specific requirements have not been promoted into permanent governance accidentally.
5. No technology was selected only because the agent preferred it.
6. Trade-offs and rationales are visible.
7. Governance explains how amendments, exceptions, and compliance reviews work.
8. Dates and semantic constitution version are correct.
9. No unresolved template placeholders remain without an explained TODO.

The current constitution workflow also creates a temporary Sync Impact Report for human review. The constitution is the source of truth; later commands resolve it at runtime. Current releases do not rewrite every dependent template automatically unless an optional synchronization preset is installed.

## Treat the Constitution as Versioned Governance

An amendment should be intentional and reviewable. Current Spec Kit uses semantic versioning logic for constitution changes:

- **Major:** a principle is removed or redefined incompatibly.
- **Minor:** a new principle or materially expanded governance rule is added.
- **Patch:** wording is clarified without changing the rule's meaning.

In a team project, commit constitution changes separately when practical so reviewers can evaluate governance changes without mixing them into unrelated feature code.

## Common Mistakes

- Copying `/specify.constitution` from an older or inaccurate transcript
- Running `specify init` in the wrong directory
- Using `--force` in an existing project without a clean, reviewable baseline
- Treating the constitution command as a terminal command
- Asking for generic “best practices” and accepting generic output
- Converting temporary feature scope into permanent project law
- Locking in a framework before the trade-offs are understood
- Writing principles that cannot be checked during planning or review
- Allowing the agent to invent governance decisions silently
- Assuming “created once” means the constitution can never be amended
- Moving to feature specification without reviewing the generated file

## Next Step

Once the constitution is reviewed and accepted, define the first feature or product increment with the `specify` stage. In the common hyphenated skills form:

```text
/speckit-specify Describe the first feature in terms of user behavior,
outcomes, constraints, and acceptance scenarios.
```

The next stage should describe **what** users need and **why**. Detailed technology choices and implementation design belong primarily in the later planning stage unless they are already binding constitutional constraints.

## Key Takeaway

Interactive constitution creation is a structured decision-making exercise, not a request for the agent to invent project policy. Initialize Spec Kit for the chosen integration, explain the project, ask the agent to expose important trade-offs, and turn confirmed answers into clear, testable principles.

The constitution is established once as the project's governance foundation, reviewed like code, and amended deliberately. Every later Spec Kit stage should be able to use it to reject plans or implementations that violate the project's agreed rules.

## Further Reading

- [Spec Kit core command reference](https://github.github.com/spec-kit/reference/core.html)
- [Spec Kit agentic SDD reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)
- [Supported integrations and command invocation](https://github.github.com/spec-kit/reference/integrations.html)
- [Adopting Spec Kit in an existing project](https://github.github.com/spec-kit/guides/existing-projects.html)
- [Current constitution command template](https://github.com/github/spec-kit/blob/main/templates/commands/constitution.md)
