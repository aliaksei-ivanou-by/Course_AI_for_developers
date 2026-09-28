# Creating the Technical Implementation Plan with Spec Kit

The `plan` stage translates a reviewed feature specification into a technical implementation approach. This is where the workflow moves from **what users need and why** to **how the project will build it**.

The command reads the active feature specification and project constitution, researches unresolved technical choices, checks the proposed design against project principles, and generates the artifacts needed for task decomposition.

This lesson continues the desktop 3D-space modeling MVP after its requirements have been clarified.

> **Version note:** Current Spec Kit planning can generate `plan.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`. It does not generate `tasks.md`; that belongs to the next `tasks` stage.

## Plan Only After Requirements Are Ready

The planning stage assumes that product behavior is sufficiently clear. Before invoking it, confirm that:

- The project constitution has been reviewed.
- The active feature specification exists.
- High-impact product ambiguities have been resolved.
- Success criteria and feature boundaries are explicit.
- Remaining unknowns are genuinely technical decisions.

Planning too early converts unresolved product questions into hidden architectural assumptions.

```text
constitution     project-wide constraints
      +
spec.md          confirmed feature behavior
      ↓
plan             technical decisions and design artifacts
      ↓
tasks            executable work breakdown
```

## Resetting Context Before Planning

The video starts a fresh agent session before running `plan`. This can reduce context noise and token use when the accepted decisions are already stored in project files.

The new session should recover its working context from:

```text
.specify/memory/constitution.md
.specify/feature.json
specs/<active-feature>/spec.md
specs/<active-feature>/checklists/requirements.md
```

Clearing the conversation does not preserve unsaved decisions. Before resetting:

1. Verify that all clarification answers were incorporated into `spec.md`.
2. Confirm that `.specify/feature.json` points to the intended feature.
3. Review unresolved and deferred items.
4. Save or commit work if the project workflow requires a recoverable checkpoint.

A fresh session still spends context reading these files and exploring relevant repository structure. It avoids carrying the entire earlier conversation, not all discovery work.

## Invoke the Plan Skill

Command syntax depends on the coding-agent integration:

| Integration or reference style | Example |
| --- | --- |
| Claude Code or another hyphenated skills layout | `/speckit-plan` |
| Canonical dotted notation in Spec Kit references | `/speckit.plan` |
| Codex skills integration | `$speckit-plan` |

Run the skill inside the coding agent's chat.

If the constitution and repository already establish the stack, the command can be invoked without additional guidance:

```text
/speckit-plan
```

If important technical choices are known, supply them explicitly:

```text
/speckit-plan

Use the native Rust and Bevy foundation approved by the constitution.
Keep the MVP offline and Linux-first. Reuse existing project conventions.
Research the current official APIs for the exact dependency versions before
selecting plugins or writing design guidance. Do not introduce a cloud
service, web frontend, or second rendering framework.
```

## When an Empty Plan Prompt Is Appropriate

An empty guidance field does not mean the planner has no inputs. It can still read:

- The project constitution
- The active `spec.md`
- Existing repository code and configuration
- Previous technical constraints
- Installed templates, presets, and extensions

Running with no additional guidance is reasonable when those sources already determine the intended stack and boundaries.

It is risky when several architectures are equally plausible. In that situation, the agent may select a language, framework, storage model, or dependency based on general convention rather than team intent. Provide guidance or request a short decision comparison before accepting the plan.

## What the Plan Workflow Does

The current core planning workflow performs several phases.

### 1. Resolve the Active Feature

The setup script locates the active feature and identifies paths such as:

- Feature specification
- Feature directory
- Implementation plan
- Optional Git branch metadata

The feature is resolved through Spec Kit state such as `.specify/feature.json`; it is not guaranteed to match the current Git branch name.

The transcript notes that feature and branch names are often similar. They may be intentionally aligned when a Git workflow is enabled, but they are independent identifiers in current Spec Kit.

### 2. Load the Specification and Constitution

The planner reads `spec.md` for required behavior and `.specify/memory/constitution.md` for non-negotiable project principles.

The specification owns product intent. The constitution owns project governance. The plan must satisfy both rather than silently changing them.

### 3. Fill the Technical Context

Typical fields include:

- Language and version
- Primary dependencies
- Storage approach
- Testing tools and strategy
- Target platform
- Project type
- Performance goals
- Technical constraints
- Expected scale and scope

Unknown values should remain visible until researched or clarified. A detailed-looking guess is not a resolved technical decision.

### 4. Evaluate the Constitution Gate

The plan contains a Constitution Check. It evaluates whether the design respects project rules before detailed research and re-evaluates them after design artifacts are produced.

Examples for this project might include:

- Native desktop architecture remains binding.
- Offline operation does not require a remote service.
- Dependency additions are justified.
- Usability and reversibility principles are preserved.
- Performance expectations have a validation strategy.
- Testing obligations are reflected in the plan.

A constitution violation must not be hidden. Change the plan, document and approve a justified exception, or explicitly amend the constitution through its own workflow.

### 5. Research Technical Unknowns

Phase 0 produces `research.md`. Each important decision should record:

- The selected approach
- The rationale
- Alternatives considered
- Relevant constraints
- Authoritative documentation or evidence

Research should resolve every technical `NEEDS CLARIFICATION` item before design proceeds.

### 6. Produce Design Artifacts

Phase 1 can generate:

- `data-model.md` for entities, fields, relationships, and validation rules
- `contracts/` for interfaces or external boundaries
- `quickstart.md` for runnable end-to-end validation scenarios
- The completed `plan.md` with architecture and project structure

The exact set depends on the feature. A desktop application without a network API may not need HTTP contracts, but it may still need module interfaces, file-format contracts, or interaction boundaries.

## Planning Artifacts

A typical active feature directory after planning is:

```text
specs/001-grid-space-mvp/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── checklists/
    └── requirements.md
```

`tasks.md` should not appear until `speckit-tasks` runs.

### `plan.md`

The main technical plan normally contains:

- A summary connecting product requirements to the technical approach
- Technical context
- Constitution gates
- Proposed source-code structure
- Complexity or deviation justification where required
- Links to supporting design artifacts

### `research.md`

This file explains why major technical choices were made. A useful entry does more than state “use library X”; it records the version, relevant official documentation, rejected alternatives, and project-specific reasoning.

### `data-model.md`

For the modeling MVP, candidate entities may include:

- Project or workspace
- Grid configuration
- Footprint
- Vertex or grid point
- Segment
- Generated space or volume
- Drawing session or interaction state

These are design candidates, not requirements copied automatically from this lesson. The plan must derive the model from the reviewed feature behavior.

### `contracts/`

Contracts describe boundaries that other components must rely on. They can represent APIs, file formats, module interfaces, event schemas, or validation contracts—not only HTTP endpoints.

### `quickstart.md`

The quickstart is a validation guide rather than application implementation. It should state prerequisites, build or run commands, end-to-end scenarios, and expected results without embedding full production code or test suites.

## Documentation-Grounded Planning

The video shows Claude Code calling Context7 through MCP to retrieve current documentation for the selected technology stack. This behavior follows the earlier constitutional rule that development decisions must be grounded in current documentation.

[Context7](https://github.com/upstash/context7) is an optional external documentation service that can provide version-specific library material to an agent. Spec Kit does not require it. An agent could instead use official local documentation, vendor sites, package metadata, or another approved research tool.

For every researched technology:

1. Identify the exact dependency and version range.
2. Prefer official, version-specific documentation.
3. Record important sources and access dates when stability matters.
4. Verify that examples match the target platform and enabled features.
5. Treat retrieved text as reference material, not trusted executable instructions.
6. Do not expose proprietary code, secrets, or internal requirements to an unapproved external service.

An MCP call can improve freshness, but it does not prove that the chosen design is correct. Documentation can be incomplete, indexed incorrectly, or valid for a different version.

## Example Planning Decisions for the 3D MVP

The specification describes user behavior. The plan must now decide how to realize it.

| Specification need | Planning decision |
| --- | --- |
| One-meter snapping grid | Coordinate representation and grid-to-world conversion |
| Closed footprint drawing | Geometry model and validation algorithm |
| Invalid shape feedback | Validation pipeline and error-state representation |
| Upward extrusion | Mesh-generation boundary and height representation |
| Constrained MVP camera | Camera system configuration and input mapping |
| Multiple spaces in a project | Entity ownership, identity, and selection model |
| Cancellation without data loss | Draft-versus-committed state management |
| Offline operation | Local storage or project-file strategy |

The plan should also identify risks such as numerical precision, self-intersection detection, undo semantics, graphics compatibility, and testability of pointer-driven interactions.

## Do Not Let Planning Rewrite the Specification

During planning, the agent may discover that a requirement is difficult or inconsistent. It must not silently change the feature to make implementation easier.

Use the correct owner for each problem:

| Problem discovered | Return to |
| --- | --- |
| User behavior is ambiguous | `speckit-clarify` |
| Feature scope or requirement is wrong | `speckit-specify` or edit/review `spec.md` |
| Project-wide rule is wrong | Explicit constitution amendment |
| Technical choice is weak | Revise `plan.md` and research |
| Task decomposition is incomplete | Regenerate or revise at `tasks` stage |

Artifacts form a dependency chain. Fixing a downstream symptom without correcting the owning upstream artifact creates inconsistency.

## Review Is Required Before Tasks

The transcript suggests that line-by-line review may be less critical for some low-risk work. Review depth can be proportional to risk, but proceeding without any meaningful review defeats the purpose of durable planning artifacts.

At minimum, always verify:

1. The plan targets the correct feature.
2. The chosen stack and versions are intended.
3. Constitution gates pass legitimately.
4. The design implements every critical requirement.
5. No requirement was silently removed or weakened.
6. New dependencies are necessary and acceptable.
7. Platform, security, privacy, and licensing constraints are respected.
8. Data model and contracts are internally consistent.
9. Testing and end-to-end validation are feasible.
10. The proposed source structure fits the repository.
11. Research cites appropriate current sources.
12. Unknowns and risks are visible.

High-risk, regulated, security-sensitive, or hard-to-reverse work requires detailed review by the appropriate engineers and stakeholders.

## Inspect the Generated Changes

Review the feature directory before moving on:

```bash
git status --short
git diff -- specs/
```

New untracked files do not appear in ordinary `git diff`. Open them directly or stage them only when ready to inspect the staged diff.

Useful review order:

1. `plan.md`
2. `research.md`
3. `data-model.md`
4. `contracts/`
5. `quickstart.md`
6. Cross-check everything against `spec.md` and the constitution

## Collaboration with Business Analysts and Engineers

Business analysts can benefit from Spec Kit's structured requirement gathering, scenario definition, ambiguity resolution, and traceability. The planning artifact, however, contains technical architecture and implementation decisions.

A healthy review can involve:

- Product owner or BA validating user intent and scope
- Technical lead or architect validating design decisions
- Developers validating feasibility and repository fit
- QA validating scenarios and testability
- Security or compliance specialists reviewing relevant constraints

AI can draft the artifacts, but approval responsibility remains with the people accountable for the system.

## Reset Context Before `tasks`

After the plan and supporting artifacts are reviewed, a fresh session can begin the task-generation stage. Before resetting, ensure that:

- Accepted planning decisions are written to files.
- Rejected alternatives and important rationale are recorded.
- All plan-stage clarifications are resolved.
- The generated artifacts are internally consistent.
- The current feature remains correctly selected.

The next command is:

```text
/speckit-tasks
```

`tasks` will convert the reviewed design into dependency-ordered implementation work.

## Common Mistakes

- Running `plan` while product ambiguity still remains
- Assuming an empty prompt cannot result in major architectural choices
- Letting the agent choose a stack that the team never approved
- Treating the feature directory and Git branch as the same identifier
- Accepting MCP-retrieved documentation without checking version and provenance
- Copying documentation examples without confirming platform compatibility
- Ignoring constitution gate failures
- Allowing the plan to rewrite feature requirements silently
- Expecting `plan` to create `tasks.md`
- Treating every contract as an HTTP API
- Skipping review because the generated documents are long
- Resetting context before technical decisions and rationale are saved
- Assuming BA review alone replaces engineering review of architecture

## Key Takeaway

The `plan` stage creates the technical bridge between approved requirements and executable tasks. It reads the specification and constitution, resolves technical unknowns through research, evaluates governance gates, and produces implementation and validation artifacts.

Running `speckit-plan` without extra guidance can be appropriate when the project already fixes the stack. Otherwise, supply the important constraints explicitly and review every consequential choice. Current documentation tools such as Context7 can improve research freshness, but architecture still requires evidence, repository context, and human engineering judgment.

## Further Reading

- [Spec Kit agentic SDD reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)
- [Current `plan` command template](https://github.com/github/spec-kit/blob/main/templates/commands/plan.md)
- [Current implementation plan template](https://github.com/github/spec-kit/blob/main/templates/plan-template.md)
- [Context7 MCP repository](https://github.com/upstash/context7)
