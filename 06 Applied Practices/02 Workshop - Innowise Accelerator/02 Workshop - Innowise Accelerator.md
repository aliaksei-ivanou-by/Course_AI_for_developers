# Workshop: Innowise Accelerator for Structured AI-Assisted Development

**Sources:**

- Internal Innowise workshop recording (approximately 58 minutes)
- Upstream repository: [innowise-ai/cpp-embedded-accelerator](https://github.com/innowise-ai/cpp-embedded-accelerator)
- Included source snapshot: [C++ / Embedded Accelerator v2.6.0](cpp-embedded-accelerator-main/README.md)
- Companion source: [Architecture](cpp-embedded-accelerator-main/docs/ARCHITECTURE.md) and [changelog](cpp-embedded-accelerator-main/docs/CHANGELOG.md)
- [Claude Code: Subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code: Agent Skills](https://code.claude.com/docs/en/skills)
- [Claude Code: Hooks guide](https://code.claude.com/docs/en/hooks-guide)
- [Claude Code: Settings](https://code.claude.com/docs/en/settings)
- [OpenCode: Skills](https://opencode.ai/docs/skills)
- [OpenCode: Rules](https://opencode.ai/docs/rules/)
- [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines)
- [Vercel React Best Practices](https://github.com/vercel-labs/open-agents/tree/main/.agents/skills/vercel-react-best-practices)
- [Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/)
- [European Accessibility Act](https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/european-accessibility-act-eaa_en)
- [European Commission: Application of the GDPR](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/application-gdpr_en)

Innowise Accelerator is an internal, stack-aware framework for Claude Code. It packages engineering practices into commands, isolated agents, reusable skills, hooks, settings, and persistent project artifacts. The version demonstrated in the workshop focused on Node.js applications—primarily NestJS backends and React or Next.js frontends—and was described as being adapted by other departments for additional stacks.

The framework's main contribution is not a new model or a fully autonomous software factory. It is a controlled workflow that makes AI-assisted work smaller, more explicit, easier to review, and less dependent on one long chat session.

This lesson also includes the source snapshot of a later **C++ / Embedded Accelerator** port. It preserves the workshop's controlled-workflow ideas but is not the same Node/NestJS implementation shown in the recording. Treat the workshop and the companion source as two related versions, not as one interchangeable product.

> **Source distinction:** The workshop described its Node/NestJS Accelerator as internal know-how. The included C++ / Embedded port has an [upstream GitHub repository](https://github.com/innowise-ai/cpp-embedded-accelerator), but its bundled package metadata says `Proprietary` and the snapshot contains no separate `LICENSE` file. Link to the upstream source and follow the usage terms stated by its owner; do not assume that the workshop implementation and this port have the same access or licensing model.

## Learning Objectives

By the end of this lesson, you should be able to:

- explain the problems the Accelerator is designed to solve;
- distinguish commands, agents, skills, hooks, settings, and project artifacts;
- describe the framework's four workflow phases and its manual control gates;
- use specifications and task files to hand context across short agent sessions;
- evaluate when parallel agents and Git worktrees are appropriate;
- identify security boundaries that prompts alone cannot enforce;
- distinguish demonstrated behavior from roadmap proposals and anecdotal results; and
- plan a safe pilot for a greenfield or brownfield project.

## Version and Evidence Notice

The exact skill list, commands, model identifiers, installation process, and supported stacks are version-dependent. The workshop reported 19 skills in the demonstrated version, but that number should not be treated as a permanent interface.

The implementation example was a workshop demonstration, not a controlled benchmark. Its elapsed time, generated test volume, and perceived quality show what was possible in that particular case; they do not establish a general productivity multiplier. Measure outcomes on your own project against a comparable baseline.

Claude Code and OpenCode also evolve quickly. Check their current official documentation before relying on a specific settings key, permission behavior, concurrency limit, directory convention, or compatibility feature.

## Included Companion Implementation: `embacc` v2.6.0

The bundled [`cpp-embedded-accelerator-main`](cpp-embedded-accelerator-main/README.md) directory was taken from the [Innowise AI upstream repository](https://github.com/innowise-ai/cpp-embedded-accelerator). It is an AI engineering accelerator for C++ and embedded teams, with reusable workflows for architecture, implementation, code review, testing, debugging, performance profiling, and target verification. Its host integrations cover Codex, Claude Code, and OpenCode; the included version also contains a Pi adapter.

The package metadata identifies this snapshot as version **2.6.0** and sets `license = "Proprietary"`; the snapshot does not include a standalone `LICENSE` file. This explains the earlier caution: a public GitHub location is valid to link and cite, but public visibility alone does not label a project as open source. The course therefore records both the upstream source and the license metadata without inventing additional restrictions.

### How It Differs from the Workshop Version

| Workshop demonstration | Included C++ / Embedded port |
| --- | --- |
| Focused on Node.js, NestJS, React, and Next.js | Focused on C++, embedded systems, robotics, Rust, and Python |
| Primarily described through Claude Code project configuration | Supports Claude Code, Codex, OpenCode, and Pi through native adapters |
| Used repository-local tasks, specifications, commands, agents, skills, and hooks | Keeps normal runtime state under `~/.embacc` or `ACCELERATOR_HOME` |
| Reported 19 skills at workshop time | Ships 17 canonical workflow and engineering-discipline skills |
| Used task and specification registries in the project | Uses hidden external task workspaces with `STATE.md` as the resume point |
| Presented stack-specific knowledge as part of the workflow | Intentionally excludes large topical knowledge packs from the maintained core |

These differences show that the Accelerator is an evolving design family. Do not use the bundled C++ port as proof that the original Node implementation has the same commands, storage model, security properties, or supported hosts.

### External State Model

In normal use, `embacc` stores accelerator-owned state outside the client repository:

```text
~/.embacc/                         # or ACCELERATOR_HOME
├── core/<version>/.agents/skills/
└── projects/<project-id>/
    ├── PROJECT.md
    ├── discovery.json
    ├── agent.json
    ├── tasks/<task>/
    │   └── STATE.md
    ├── mcp/
    ├── agent-config/skills/
    ├── ast-grep/
    └── state/
```

This design reduces accidental pollution of a customer's repository, but the external directory still contains sensitive project-derived context and session state. Apply appropriate filesystem permissions, retention rules, backup policy, and deletion procedures.

### Command Surface

After an authorized installation, the intended starting flow is:

```bash
embacc setup /path/to/project
embacc
```

The public command surface in version 2.6.0 is:

| Command | Purpose |
| --- | --- |
| `embacc setup .` | Discover repository evidence and create or refresh external `PROJECT.md` context |
| `embacc run <host> .` | Launch Claude Code, Codex, OpenCode, or Pi for the project |
| `embacc doctor .` | Diagnose the external project state and optional tooling |
| `embacc refresh .` | Repeat discovery and update generated project context |
| `embacc config .` | Print or open the external project configuration directory |
| `embacc reflect .` | Analyze prior project sessions and propose reusable learning |
| `embacc install ...` | Explicitly materialize selected shared agent configuration in a repository |
| `embacc self-update` | Update the globally installed package through Pixi |
| `embacc version` | Print the installed Accelerator version |

`setup`, `run`, `doctor`, `refresh`, `config`, and `reflect` are designed to keep Accelerator infrastructure outside the target repository. `install` is a separate opt-in mode for teams that deliberately want shared repository-local configuration.

### The 17 Canonical Skills

The shipped skills form a workflow layer rather than a general knowledge library:

| Group | Skills |
| --- | --- |
| Onboarding and routing | `project-onboard`, `feature`, `bug` |
| Task continuity | `task-workspace`, `handoff` |
| Requirements and planning | `requirements-analyst`, `requirements-clarifier`, `writing-plans` |
| Implementation and tests | `coder`, `testing`, `systematic-debugger` |
| Review and verification | `self-review`, `code-reviewer`, `verify` |
| Pull-request work | `review-pr`, `pr-review-response` |
| Immediate learning | `stabilize` |

Feature and bug routes contain explicit human gates before implementation. `STATE.md` preserves the approved stage, evidence, and next action across a cleared context or a new agent session.

`embacc reflect` is not another canonical skill. It is a batch CLI workflow that analyzes discoverable past sessions and may propose a project-private learned skill. Existing learned skills are not overwritten automatically, while rule changes still require human approval. The separate `stabilize` skill captures a correction or recurring workflow problem during the active session.

### Host Delivery Model

The package adapts the same workflow to different harnesses:

- **Claude Code** receives an external merged plugin and project context.
- **Codex** receives Accelerator-owned user-scope skill directories plus a generated project profile; project-private learned skill text remains scoped to that project.
- **OpenCode** receives external skill roots and translated supported configuration.
- **Pi** receives canonical and learned skills through its native skill arguments and settings.

The adapters deliberately report unsupported integration features instead of silently emulating them. Even so, every host has different permission and configuration semantics. Test a representative workflow on the exact installed versions before relying on equivalent behavior.

### Explicit Repository Installation

When a team intentionally wants shared repository-local configuration, it can preview an installation:

```bash
embacc install /path/to/repo --tools claude,opencode --dry-run
```

The installer copies `AGENTS.md`, canonical skills, and selected thin adapter files—not the Python runtime, tests, or complete template sources. It records hashes for files it owns. On refresh, an unchanged managed file can be updated or removed, while a locally modified file becomes a conflict and is preserved.

Use `--allow-dirty` only after reviewing an already-dirty working tree. A successful installer test does not remove the need to inspect the planned files and repository policy.

### Structural Search

`ast-grep` is an optional runtime dependency in the Pixi package. During `setup` or `refresh`, `embacc` can generate an external `sgconfig.yml` and run a real structural scan for each discovered supported language. The result is recorded in project context so agents can prefer structural search for syntax-aware queries and refactors.

If `ast-grep` is unavailable, the Accelerator degrades to ordinary grep or ripgrep guidance rather than failing the workflow. A configured grammar scan is useful evidence that parsing works; it is not a semantic index or proof that a refactor is correct.

### Local Verification of the Included Snapshot

The following verification was performed on the included source on September 29, 2026:

| Check | Result | Notes |
| --- | --- | --- |
| `python tests/run_all.py` | **PASS** | All 13 deterministic/local test modules passed |
| External Claude/OpenCode live safety tests | **NOT RUN** | Optional checks may invoke installed agents or models |
| Live `ast-grep` project scan | **NOT RUN** | `ast-grep` was not installed in the verification environment; fallback behavior passed |
| Pi dynamic extension test | **NOT RUN** | Node/npm were unavailable; static Pi safety checks passed |
| Real Pixi self-update smoke check | **NOT RUN** | Pixi was not on `PATH`; dispatch, error handling, and no-op tests passed |

The local suite validates packaging, workflow metadata and gates, repository discovery, adapters, external-state isolation, reflection, Git safety rules, explicit installation conflicts, CLI dispatch, and static Pi safety. It does not prove that every external agent version, model, target board, compiler, or customer repository will behave correctly.

### Installation Was Not Performed During Course Processing

The source was inspected and tested in place. It was **not** installed globally, did not run `embacc setup` against another repository, did not launch an external coding agent, and did not perform a self-update. This keeps course preparation separate from adopting the tool on a workstation.

## The Problem the Accelerator Addresses

An unconstrained coding-agent conversation often mixes requirements, architecture, implementation, debugging, and review in one growing context. Over time, the agent may lose important details, repeat work, infer missing decisions, or continue into the next phase before a human has reviewed the current result.

The Accelerator replaces that pattern with a staged process:

| Unstructured agent session | Accelerator approach |
| --- | --- |
| One chat accumulates every detail | Each activity runs in a focused context |
| The model decides when to continue | The workflow stops at explicit human gates |
| Important decisions remain in chat history | Decisions are written to versioned project artifacts |
| Generic advice is applied to every stack | Stack-specific skills encode local conventions |
| Ownership of generated files is unclear | Artifact names record which skill produced them |
| Review happens only at the end | Review, tests, and debugging are separate stages |

The result is a framework for **guided autonomy**: the agent can perform substantial work inside a bounded step, while the developer retains control over transitions, trade-offs, and acceptance.

## Six Design Principles

### 1. Isolate Context by Task

Each command delegates to a specialized agent with its own context. The subagent reads only the instructions and artifacts needed for its assignment, then returns a concise result to the main conversation.

This reduces context pollution and makes failures easier to localize. Isolation does not make the subagent correct; it makes its inputs and outputs easier to inspect.

### 2. Stop After Completing One Step

A command completes its current responsibility, reports the result, recommends a next action, and stops. It does not silently move from requirements to architecture to implementation.

The pause is a review gate. A developer may accept the recommendation, select an alternative, revise an artifact, or end the workflow.

### 3. Hand Off Context Explicitly

Every step should leave a compact handoff containing:

- what was completed;
- which files were created or changed;
- assumptions and unresolved questions;
- verification performed;
- the recommended next step; and
- reasonable alternatives.

A handoff is more reliable than expecting a later agent to reconstruct intent from an entire transcript.

### 4. Treat Specifications as Living Artifacts

Temporary work is stored in task-oriented documents, while durable system knowledge is promoted into specifications. A manifest indexes the available specifications so that later agents can load only the relevant ones.

The artifact is useful only if code changes keep it current. A stale specification is worse than no specification because it appears authoritative.

### 5. Prefer Minimal Sufficiency

Each skill has one clear job. Plans should be decomposed into small, testable changes, and generated code should follow principles such as DRY and YAGNI without introducing abstractions merely because an agent can create them.

### 6. Preserve Provenance

Generated file names are prefixed or otherwise labeled with the skill that created them. This makes it easier to understand why an artifact exists, which workflow stage owns it, and where to make improvements when its structure is weak.

## Architecture: Command → Agent → Skill

The framework uses three main layers:

```text
Developer
    │ invokes
    ▼
Command ── selects the workflow entry point
    │ delegates
    ▼
Agent ── receives an isolated role, context, and tool scope
    │ loads
    ▼
Skill ── contains the task-specific method and output contract
    │ produces
    ▼
Artifact + concise handoff
    │
    └── developer reviews and chooses the next step
```

| Layer | Responsibility | Example |
| --- | --- | --- |
| **Command** | Provides a memorable entry point and collects invocation arguments | Start requirements analysis or code review |
| **Agent** | Runs the work in a separate context with an appropriate role and tools | Requirements analyst, architect, debugger |
| **Skill** | Defines the repeatable procedure, constraints, and expected output | Ask clarifying questions, produce an API contract, review a diff |
| **Hook** | Runs deterministic automation on a lifecycle or tool event | Notify when an agent finishes or block a prohibited command |
| **Setting** | Defines shared or personal Claude Code behavior | Permissions, hooks, environment-specific preferences |
| **Artifact** | Persists decisions and work state across sessions | Requirement, architecture, task, or specification document |

The distinction matters. A skill is prompt-based guidance; a hook is executable automation; an agent controls context and tools; and settings determine how the local harness behaves. None of these should be treated as interchangeable.

## Representative Project Layout

The demonstrated layout can be understood as follows:

```text
project/
├── .claude/
│   ├── settings.json
│   ├── settings.local.json
│   ├── commands/
│   ├── agents/
│   ├── skills/
│   └── hooks/
├── Tasks/
├── Specs/
│   └── manifest.md
└── skill-flow.md
```

- `.claude/settings.json` contains project-shared configuration and can be committed after review.
- `.claude/settings.local.json` contains personal configuration and should normally remain untracked.
- `commands/`, `agents/`, and `skills/` define the workflow building blocks.
- `hooks/` contains scripts or hook configuration triggered by Claude Code events.
- `Tasks/` stores temporary or feature-specific working artifacts.
- `Specs/` stores durable system knowledge.
- `Specs/manifest.md` provides an index for selective context loading.
- `skill-flow.md` describes intended transitions between skills.

Exact paths and names are framework conventions, not universal Claude Code requirements.

## The Four Workflow Phases

### Phase 1: Understanding

The requirements analyst converts an initial request into a structured requirement. A brainstorming skill can then ask focused questions about scope, users, edge cases, and constraints.

The goal is not to generate implementation details early. It is to expose ambiguity before architecture and code amplify it.

Expected outputs include:

- problem statement and business goal;
- actors and primary scenarios;
- in-scope and out-of-scope behavior;
- acceptance criteria;
- non-functional constraints;
- open questions and explicit assumptions.

### Phase 2: Planning

Planning turns an approved requirement into implementation contracts and a reviewable sequence of work.

| Capability | Typical output |
| --- | --- |
| Architecture | Components, responsibilities, data flow, trade-offs |
| API design | Endpoints, payloads, validation, errors, authorization |
| Frontend design | Page and component structure, states, interactions |
| Plan writing | Ordered tasks with dependencies and verification steps |

The API contract is especially important when backend and frontend work will run in parallel. Both sides need a common, approved boundary before separate agents start coding.

### Phase 3: Development

Development includes repository isolation, implementation, review, tests, debugging, and branch completion. The workshop demonstrated stack-specific coding skills for a layered NestJS backend and a React or Next.js frontend.

Representative skills include:

- creating a Git worktree;
- backend and frontend implementation;
- code review;
- test generation;
- systematic debugging; and
- finishing a development branch.

Generated code remains subject to the project's existing architecture, linting, tests, security controls, and human review. A skill's conventions should not silently override repository rules.

### Phase 4: Finalization

Finalization prepares completed work for delivery. It can include documentation generation, release preparation, final verification, and branch integration or pull-request preparation.

This phase should confirm that implementation artifacts and durable specifications agree. It should not be used to retroactively invent documentation for decisions that were never reviewed.

## Two Typical Workflows

### Full Feature

```text
Initial request
  → requirements analysis
  → brainstorming and clarification
  → architecture
  → API and/or frontend design
  → implementation plan
  → backend/frontend development
  → review
  → tests
  → debugging if needed
  → documentation and branch completion
```

Every arrow is a potential human gate. Some steps can be skipped when they add no value, but the reason should be explicit. A small frontend-only change, for example, may not require a new API design.

### Bug Fix

```text
Reproduction and evidence
  → systematic diagnosis
  → minimal fix
  → targeted tests
  → review
  → branch completion
        │
        └── failing verification → return to diagnosis
```

The debugger should identify a supported cause before the coder changes production code. This prevents a plausible-looking patch from masking the real failure.

## Persistent Artifacts and Context Management

The Accelerator treats files—not chat history—as the primary handoff medium. A useful artifact should be:

- scoped to one decision or stage;
- readable without the original conversation;
- explicit about assumptions and status;
- linked to related artifacts;
- updated when implementation changes; and
- small enough for selective loading.

The manifest should describe each specification briefly so an agent can decide what to read. Loading the entire `Specs/` directory for every task recreates the context problem that the framework is meant to solve.

Do not store secrets, raw credentials, unnecessary personal data, or client-confidential material in agent artifacts. Apply the same classification, retention, and access rules used for the rest of the repository.

## Stack Specialization

The demonstrated version's main differentiator from a generic specification framework is its opinionated knowledge of Node.js, NestJS, React, and Next.js. It can encode preferred project structure, controller-service-repository boundaries, component design, test patterns, and external best-practice guidance.

That specialization is valuable when it matches the project. It becomes a liability when treated as universal. Porting the framework to Python, .NET, Java, or another stack requires more than changing a technology name. At minimum, review and adapt:

- architecture and coding skills;
- framework-specific validation and security rules;
- project layout assumptions;
- test tools and quality gates;
- package and build commands; and
- examples embedded in prompts.

Vercel's Web Interface Guidelines and React Best Practices can strengthen a frontend skill, but they remain guidance. They do not replace repository conventions, performance measurement, design review, or accessibility validation.

## Parallel Agents and Git Worktrees

Claude Code subagents can run with isolated context, and worktree isolation can give separate tasks independent working directories. The workshop demonstrated parallel frontend and backend work based on a shared contract.

Use parallelism only when tasks have:

- a stable interface between them;
- little or no file overlap;
- independent verification paths; and
- an identified person or step responsible for integration.

In this framework, subagents do not need direct peer-to-peer conversation. They coordinate through approved artifacts and return summaries to the main session. This improves traceability, but the developer must reconcile incompatible assumptions and merge results.

Do not assume a fixed safe number of simultaneous agents. Practical concurrency depends on the current product, account limits, machine resources, test infrastructure, repository size, and the amount of integration work created.

## Hooks, Permissions, and the Security Boundary

This is the most important correction to a common misunderstanding: **instructions inside a skill are not a security boundary**. Prompt text can guide a model, but deterministic controls should enforce high-impact restrictions.

Claude Code supports project settings, permission rules, hooks, sandboxing, and managed settings. Use them in layers:

| Risk | Recommended control |
| --- | --- |
| Reading secrets such as `.env` | Deny rules, least-privilege tool access, secret isolation |
| Destructive shell commands | Narrow command permissions, sandboxing, `PreToolUse` hooks |
| Modification of agent configuration | Repository review, protected branches, ownership rules, managed settings where available |
| Malicious project hooks | Review configuration before trust; treat hooks as executable code |
| Unexpected network or package activity | Restricted environment, approved registries, command review |
| Unsafe generated changes | Worktree or branch isolation, diff review, tests, recoverable backups |

The shared `.claude/settings.json` should be reviewed like source code. Personal rules belong in `.claude/settings.local.json`, which is normally untracked. Do not grant broad shell access merely to avoid confirmation prompts.

Hooks can block tool calls or add checks, but a hook itself can execute commands with the user's privileges. Inspect hook source, pin or control dependencies, and avoid running untrusted project configuration on a sensitive workstation.

## Greenfield and Brownfield Adoption

The workshop positioned the demonstrated version as stronger for greenfield work. A large existing repository requires additional discovery before generic skills can safely modify it.

Claude Code's project initialization can create a useful instruction file, but one generated file is not a complete brownfield model. Before adopting the Accelerator in an existing system:

1. Map modules, ownership boundaries, entry points, and build commands.
2. Record architecture decisions and local conventions.
3. Identify generated code, legacy zones, and files that must not be changed.
4. Establish a reliable test baseline.
5. Pilot one bounded feature or bug fix.
6. Compare generated artifacts with the code and correct false assumptions.
7. Expand only after the workflow produces repeatable, reviewable results.

Very large brownfield support was described as work in progress rather than a proven capability. Treat project-specific customization as engineering work with its own tests and maintenance burden.

## Portability to OpenCode and Other Harnesses

OpenCode currently discovers skills from several compatible locations, including `.claude/skills`, and can use `CLAUDE.md`-style instructions. This can reduce migration effort for some artifacts.

However, renaming `.claude` to `.opencode` is not a complete migration strategy. Validate each category separately:

- skill discovery and frontmatter;
- agents and their tool permissions;
- custom commands;
- hooks and lifecycle events;
- settings and precedence;
- model and provider identifiers;
- environment variables; and
- worktree and background-task behavior.

Build a small compatibility test that invokes one representative workflow, checks its artifact, verifies permission enforcement, and confirms that failure behavior is understood. Portability should be demonstrated, not inferred from similar directory names.

## What the Demonstration Showed

The workshop used a real-project-style epic with a NestJS backend and Next.js frontend, authentication, four user roles, separate dashboards, and design input stored in CSV files. The presenter reported:

- approximately two to three hours for the demonstrated implementation flow;
- parallel frontend and backend development;
- generated tests totaling 2,236 lines of code;
- consistent stack-specific patterns; and
- traceable requirements, plans, and specifications.

These are **observations**, not benchmark results. Lines of test code are not a quality metric by themselves, and elapsed time excludes differences in requirements quality, review depth, model cost, retries, and later maintenance.

A credible evaluation should compare:

| Dimension | Example measure |
| --- | --- |
| Delivery | Lead time from approved requirement to reviewed change |
| Quality | Escaped defects, test effectiveness, review findings |
| Rework | Changes caused by misunderstood requirements or architecture |
| Cost | Model spend, developer time, CI usage |
| Maintainability | Complexity, duplication, convention compliance |
| Traceability | Ability to connect code and tests to approved requirements |
| Developer experience | Cognitive load, predictability, ease of recovery |

## Accessibility Is a Requirement, Not a Generated Guarantee

The demonstrated version did not establish built-in accessibility assurance. Frontend best-practice skills may catch some issues, but they do not certify WCAG conformance or compliance with applicable law.

For a real project:

1. Identify the products, services, jurisdictions, and contractual rules in scope.
2. Define the applicable accessibility target, such as selected WCAG 2.2 conformance criteria.
3. Add accessibility acceptance criteria to requirements and design artifacts.
4. Combine automated checks with keyboard, screen-reader, zoom, contrast, focus, error-state, and human usability testing.
5. Record exceptions, evidence, and ownership.

The European Accessibility Act applies to specified categories of products and services; it is not a blanket statement that every commercial website must meet one identical rule. Seek qualified legal and accessibility advice for the actual product and jurisdiction.

## Data Protection and Self-Hosted Models

The workshop discussed self-hosted models as a possible option for sensitive environments. Self-hosting can reduce some external data transfers, but it does not by itself establish GDPR compliance.

An organization still needs to assess, as applicable:

- the purpose and lawful basis for processing;
- data minimization and retention;
- controller and processor responsibilities;
- contracts and subprocessors;
- international transfers;
- access controls, logging, encryption, and incident response;
- data-subject rights; and
- whether a data protection impact assessment is required.

Conversely, using a cloud provider is not automatically non-compliant. The controller must select processors that provide sufficient guarantees and define appropriate contractual, technical, and organizational measures. Follow organizational security, legal, and privacy review rather than choosing a deployment model from a workshop claim.

## Current Capabilities Versus Roadmap

The workshop mixed demonstrated features with ideas for future development. Keep them separate when planning adoption.

| Demonstrated or described as current | Discussed as roadmap or proposal |
| --- | --- |
| Command-agent-skill architecture | Broader adoption across departments |
| Requirements, planning, coding, review, test, and debug skills | Expanded NestJS guidance and a CQRS/DDD variant |
| Task and specification artifacts | Reflection and prompt-enhancement skills |
| Notifications through hooks | CI/CD pipeline generation |
| NestJS and React/Next.js specialization | Dedicated security auditing |
| Worktree-based parallel tasks | Performance testing, monitoring, tracing, alerts, and dashboards |
| Utility skills for creating and updating skills | Stronger accessibility coverage |

A roadmap item should not appear in a client proposal, estimate, or project plan as an available capability until its implementation and verification are confirmed.

## How Skills Are Selected

Clear skill descriptions help the model choose a relevant capability, while each completed step recommends a small set of next actions. This narrows the decision space and makes the intended flow discoverable.

Automatic selection can still fail when descriptions overlap or the request is vague. For important work:

- invoke the desired command explicitly;
- inspect which skill and agent were selected;
- require the output contract you expect; and
- stop if the chosen workflow does not match the task.

Predictable manual invocation is often preferable to clever but opaque routing.

## A Safe Adoption Checklist

Before using the Accelerator on production work:

- [ ] Record the upstream source and follow the repository owner's stated license and usage terms.
- [ ] Review every project setting, hook, command, agent, and skill before trusting it.
- [ ] Verify that local configuration and secrets are excluded from source control.
- [ ] Select a bounded pilot with clear acceptance criteria and a test baseline.
- [ ] Adapt stack-specific rules to the repository instead of forcing defaults.
- [ ] Define which artifact is authoritative at each workflow stage.
- [ ] Add security, privacy, accessibility, and operational requirements early.
- [ ] Use a branch or worktree and keep all changes recoverable.
- [ ] Require human review before phase transitions and integration.
- [ ] Measure time, cost, defects, rework, and developer effort against a baseline.
- [ ] Record gaps as framework improvements rather than hiding them in prompts.

## Practical Exercise: Run a Bounded Pilot

Choose a small feature that can be completed and reviewed independently. Avoid sensitive data and high-risk production access.

1. Write a one-page requirement with scope, acceptance criteria, constraints, and exclusions.
2. Use the understanding phase to identify ambiguity; approve the revised artifact.
3. Produce only the architecture and interface decisions needed for this feature.
4. Create a short implementation plan with explicit verification for every step.
5. Implement the change in an isolated branch or worktree.
6. Run review, tests, and a security check as separate activities.
7. Compare the final code with the requirement and update durable specifications.
8. Record elapsed developer time, model usage, review findings, rework, and defects.
9. Identify one framework change that would improve the next pilot.

Success is not “the agent produced a lot of code.” Success is a correct, maintainable, traceable change whose cost and risk are understood.

## Common Mistakes

- **Treating the workflow as full autonomy.** The design intentionally relies on human gates.
- **Assuming a skill is a policy control.** Prompt instructions can be ignored or misapplied; enforce critical restrictions outside the prompt.
- **Running every step for every task.** Use only the stages that reduce uncertainty or risk.
- **Parallelizing coupled work.** Shared files and unstable interfaces create more integration work than time saved.
- **Counting generated tests instead of evaluating them.** Check behavior, failure sensitivity, coverage relevance, and maintainability.
- **Letting specifications drift.** Update or retire stale artifacts.
- **Forcing greenfield conventions onto a brownfield system.** Discover the existing architecture first.
- **Assuming OpenCode migration is a folder rename.** Test every integration surface.
- **Equating self-hosting with compliance.** Deployment location is only one part of privacy and security governance.
- **Presenting roadmap items as current features.** Verify the installed framework version.
- **Sharing internal assets without authorization.** Confirm ownership and distribution rules first.

## Key Takeaway

Innowise Accelerator demonstrates a practical pattern for AI-assisted engineering: isolate each task, persist decisions in reviewable artifacts, encode stack-specific practices in reusable skills, and require humans to control transitions. Its value comes from disciplined orchestration and traceability—not from removing developers from the process. Adopt it incrementally, enforce security outside prompt text, validate portability and compliance claims, and judge it by verified project outcomes rather than demo speed or generated code volume.
