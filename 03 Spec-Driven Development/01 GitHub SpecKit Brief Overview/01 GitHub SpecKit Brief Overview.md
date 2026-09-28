# GitHub Spec Kit Process Flow

GitHub Spec Kit provides a structured process for spec-driven development with AI coding agents. Instead of moving directly from a short idea to generated code, the workflow records project principles, feature requirements, technical decisions, and implementation tasks as durable artifacts.

This lesson is a theory-level overview. Later lessons demonstrate the individual steps in practice. The goal here is to understand what each stage is responsible for, how the stages connect, and when the additional ceremony is worthwhile.

> **Version note:** Spec Kit evolves quickly. The lesson introduces the foundational `constitution → specify → clarify → plan → tasks → implement` flow. Current releases also provide optional quality gates such as `checklist` and `analyze`, followed by `converge` after implementation. Always use the command form installed for the selected agent integration.

## Why Use Spec-Driven Development?

AI agents can start coding from a short request, but a complex feature usually contains decisions that should be resolved before implementation:

- What problem is being solved?
- Which user behavior should change?
- What is explicitly out of scope?
- Which project principles and quality standards apply?
- How should the feature fit the existing architecture?
- How can the work be divided into reviewable tasks?
- How will the result be verified?

Spec Kit separates these concerns into stages. Each stage creates or updates Markdown artifacts that become input for the next stage.

```text
Project foundation
    constitution
         ↓
Feature definition
    specify → clarify (optional)
         ↓
Technical design
    plan → checklist (optional)
         ↓
Execution preparation
    tasks → analyze (optional)
         ↓
Delivery
    implement → converge
```

The foundational lesson flow remains useful even when the optional quality gates are omitted.

## Use Spec Kit for the Right Size of Work

Spec Kit is most valuable for work that benefits from deliberate planning and decomposition, such as:

- A feature that affects several components or services
- A new application, MVP, or proof of concept
- A change with meaningful product ambiguity
- Work with architectural, testing, security, or compliance constraints
- A feature that should be divided into multiple implementation tasks
- Development that may continue across several agent sessions

It may be unnecessary for a trivial refactoring, a one-line bug fix, or a single self-contained function whose expected behavior and implementation are already obvious. The workflow should reduce risk, not add ceremony without benefit.

## Core Workflow at a Glance

| Stage | Typical frequency | Primary focus | Main outcome |
| --- | --- | --- | --- |
| Constitution | Once per project, then amended deliberately | Project-wide principles and governance | Persistent project constitution |
| Specify | Once per feature or major iteration | What and why | Feature specification and user stories |
| Clarify | Optional, before planning | Missing or ambiguous requirements | Answers incorporated into the specification |
| Plan | Once per feature | How | Technical implementation plan |
| Checklist | Optional quality gate | Requirements quality and completeness | Domain-specific checklist |
| Tasks | Once per feature | Work decomposition | Actionable task list |
| Analyze | Optional quality gate | Consistency across artifacts | Report of gaps, conflicts, and missing coverage |
| Implement | One or more passes | Execute the tasks | Code, tests, and other implementation changes |
| Converge | After implementation passes | Compare implementation with artifacts | Remaining work or a converged result |

## Step 1: Establish the Project Constitution

The constitution records the principles that should govern later specifications, plans, tasks, and implementations. It may include:

- Architectural boundaries
- Code-quality expectations
- Testing requirements
- Security and privacy rules
- Documentation standards
- Naming and organization conventions
- Review and validation requirements
- Rules for dependencies and external services

This is often the hardest step because teams may follow important principles without having written them down. A vague statement such as “write high-quality code” is difficult for an agent to apply consistently. A useful principle should be concrete enough to guide decisions and, where possible, to verify.

For example:

```text
All externally observable behavior MUST be covered by automated tests.
Exceptions require a documented rationale in the implementation plan.
```

The initial constitution is normally created once per project. It can later be amended when the team intentionally changes its governing principles, but it should not be regenerated casually for every feature.

### Use Questions to Discover Principles

If the project principles are unclear, ask the agent to interview the team or developer before writing them:

```text
Create the project constitution.
Before writing it, ask questions about architecture, testing, security,
documentation, compatibility, and code-review expectations.
Do not invent principles when a decision has not been made.
```

The lesson suggests asking for a very large number of questions when necessary—even “ask me 100 questions”—to expose hidden expectations. In practice, question count is less important than coverage: prioritize questions whose answers would materially change project decisions.

## Step 2: Specify What the Feature Should Do

The specification stage defines the feature from the product and user perspective. Its focus is **what** should happen and **why**, not the technical implementation.

A useful specification describes:

- The problem or goal
- Target users and user stories
- User actions and observable outcomes
- Functional requirements
- Important scenarios and edge cases
- Acceptance criteria
- Scope and non-goals
- Assumptions or unresolved questions

For an initial application, the specification may define an MVP—minimum viable product—or a proof of concept. After the first version is delivered, the same stage is repeated for each substantial new feature.

Example of specification-level language:

```text
When a signed-in user submits the search form, the application displays
matching results ordered by relevance. If no results exist, the application
shows an empty-state message and preserves the submitted query.
```

This describes observable behavior without deciding which database, framework, component hierarchy, or search algorithm should implement it.

## Step 3: Clarify Ambiguity Before Planning

The clarification stage is optional but valuable when the specification contains unclear or incomplete decisions. Run it before creating the technical plan so that planning does not silently build on assumptions.

Clarification can uncover questions such as:

- What should happen for unauthenticated users?
- Which data is required and which is optional?
- What are the limits, failure states, and fallback behaviors?
- Which compatibility requirements apply?
- How should conflicting user actions be handled?

The agent should incorporate confirmed answers into the specification. If a decision cannot yet be made, it should remain visible as an unresolved question rather than being presented as fact.

Clarification is also useful during constitution creation. Tool support for interactive questions varies, so one agent may provide a smoother interview experience than another. The workflow itself is not tied to a particular model or interface.

## Step 4: Create the Technical Plan

The plan stage translates the reviewed specification into a technical implementation approach. This is where the workflow moves from **what and why** to **how**.

The plan may identify:

- Architecture and component boundaries
- Technologies, libraries, and data models
- Relevant existing files and services
- Interfaces and integration points
- Migration or compatibility work
- Testing and validation strategy
- Technical risks and constraints

If the developer already knows the required approach, that guidance can be included with the planning request:

```text
Create the implementation plan using the existing PostgreSQL database and
the repository's current service-layer pattern. Do not introduce another ORM.
```

If the technical direction is unknown, the plan can be generated from the constitution, specification, and repository context. The result must still be reviewed; a detailed plan is a proposal, not proof that every decision is correct.

## Optional Quality Gate: Generate a Checklist

Current Spec Kit versions can generate requirements-quality checklists. A checklist evaluates whether the written requirements are complete, clear, consistent, and measurable for a selected domain.

This is different from testing the code. It is closer to writing “unit tests for the requirements”: before implementation begins, the team checks whether the specification contains enough information to support a reliable plan and acceptance decision.

## Step 5: Break the Plan into Tasks

The tasks stage decomposes the implementation plan into actionable work items. A useful task list should:

- Map back to requirements and the technical plan
- Identify likely files or components
- Include appropriate testing and validation work
- Respect dependencies and execution order
- Keep tasks small enough to implement and review
- Make parallelizable work visible when appropriate

This decomposition is one of the main reasons to use Spec Kit for larger features. Instead of asking an agent to implement an entire feature in one uncontrolled pass, the project gains an explicit execution roadmap.

## Optional Quality Gate: Analyze Artifact Consistency

After task generation and before implementation, current Spec Kit versions can perform a read-only consistency analysis across the specification, plan, and tasks.

The analysis looks for problems such as:

- A requirement with no corresponding task
- A task that is not justified by the specification
- A technical decision that contradicts a project principle
- Ambiguous or duplicated requirements
- Missing validation work

Important findings should be resolved in the source artifacts before implementation begins.

## Step 6: Implement the Tasks

The implementation stage executes the prepared task list using the constitution, specification, and technical plan as constraints.

The later stages are often less conversational than constitution and specification work because the major decisions have already been recorded. However, “less interactive” does not mean unsupervised. The developer should still:

1. Review proposed changes.
2. Run the relevant tests and checks.
3. Confirm that completed work satisfies the specification.
4. Stop and revise the artifacts if implementation exposes a missing decision.
5. Avoid accepting unrelated changes merely because they were generated with the feature.

The quality of implementation depends heavily on the artifacts created earlier. Clear requirements and a realistic plan reduce guesswork, but they do not eliminate the need for engineering review.

## Step 7: Converge on the Specification

Current Spec Kit releases include a convergence step after implementation. It compares the codebase with the specification, plan, and tasks, then identifies remaining work.

The implementation and convergence stages may repeat:

```text
implement → converge → remaining tasks → implement → converge
```

The loop ends when the convergence report indicates that the implementation satisfies the agreed artifacts. This gives the workflow an explicit completion check rather than treating “the agent stopped coding” as evidence that the feature is finished.

## Command Invocation Depends on the Agent

Spec Kit installation and project initialization are terminal operations. The process stages themselves are invoked inside the coding agent's chat after the project has been initialized.

The logical stages are the same, but syntax varies by integration and installed mode:

| Integration style | Example |
| --- | --- |
| Dotted slash-command notation used in references | `/speckit.specify` |
| Current GitHub Copilot skills mode | `/speckit-specify` |
| Codex skills | `$speckit-specify` |

For Codex, the foundational sequence therefore appears as:

```text
$speckit-constitution
$speckit-specify
$speckit-clarify
$speckit-plan
$speckit-checklist
$speckit-tasks
$speckit-analyze
$speckit-implement
$speckit-converge
```

Use the form exposed by the installed integration rather than converting the command spelling from another agent manually.

## Add Instructions to a Stage When Needed

A process command can be accompanied by natural-language guidance. For example:

```text
/speckit.plan Use the existing authentication service and ask me questions
before choosing a session-storage strategy.
```

Or, in Codex skills mode:

```text
$speckit-plan Use the existing authentication service and ask me questions
before choosing a session-storage strategy.
```

The command starts the appropriate workflow; the accompanying message supplies feature-specific constraints or requests clarification.

## Reset Context Between Major Stages

A useful practice is to start a fresh agent session after completing a major stage, especially when the conversation has become large.

Spec Kit persists important decisions in project artifacts such as the constitution, `spec.md`, `plan.md`, and `tasks.md`. Once those files are complete and reviewed, the next session can read them instead of carrying the full conversational history.

This can provide two benefits:

- **Token efficiency:** Irrelevant conversation history no longer consumes the active context window.
- **Focus and quality:** The agent begins from reviewed artifacts rather than a mixture of abandoned ideas, corrections, and intermediate discussion.

A context reset is safe only when the durable artifacts contain the decisions the next stage needs. Before clearing the session, verify that answers, assumptions, and accepted changes were written to the appropriate files. At the beginning of the new session, instruct the agent to read the constitution and current feature artifacts.

## Common Mistakes

- Using the full workflow for a trivial change that does not need planning
- Writing implementation details inside `specify` before user behavior is clear
- Treating the constitution as generic aspirations instead of testable principles
- Skipping clarification while important product decisions remain unresolved
- Accepting a detailed plan without checking it against the actual repository
- Generating tasks that cannot be traced to requirements
- Starting implementation despite unresolved analysis findings
- Assuming implementation is complete without tests or convergence review
- Keeping a very large chat context even though the accepted decisions already exist in files

## Practical Decision Guide

Before using Spec Kit for a feature, ask:

1. Is the change complex enough to benefit from a specification and plan?
2. Does the project already have a reviewed constitution?
3. Can the desired behavior be described without prematurely choosing implementation details?
4. Are there ambiguities that should be clarified before planning?
5. Does the plan respect the constitution and repository architecture?
6. Do the generated tasks cover every important requirement and validation step?
7. Will the implementation be reviewed against the saved artifacts?

If these questions are answered deliberately, Spec Kit becomes a framework for decision quality rather than merely a collection of agent commands.

## Key Takeaway

GitHub Spec Kit turns AI-assisted development into a sequence of durable, reviewable decisions. The constitution establishes project-wide principles. Each substantial feature then moves from specification and clarification to technical planning, task decomposition, implementation, and convergence.

The most important distinction is simple:

- `specify` defines **what** should be built and **why**.
- `plan` defines **how** it should be built.
- `tasks` divides the plan into executable work.
- `implement` performs that work.
- `converge` checks whether the result actually matches the artifacts.

Because these decisions are stored in Markdown files, developers can reset conversational context, change agent sessions, and continue the project without depending on one endlessly growing chat.

## Further Reading

- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [Supported agent integrations and command invocation](https://github.com/github/spec-kit/blob/main/docs/reference/integrations.md)
- [Agentic spec-driven development reference](https://github.com/github/spec-kit/blob/main/docs/reference/agentic-sdd.md)
