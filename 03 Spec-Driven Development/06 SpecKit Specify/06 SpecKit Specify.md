# Creating the First Feature Specification with Spec Kit

After establishing the project constitution, the next Spec Kit stage is `specify`. This stage turns a product idea into a durable feature specification containing user scenarios, functional requirements, edge cases, assumptions, and measurable success criteria.

The central rule is simple:

- `specify` defines **what users need and why**.
- `plan` later defines **how the system will implement it**.

This lesson begins a complete spec-driven development cycle for a lightweight desktop application that creates three-dimensional spaces. The first iteration defines a deliberately small MVP rather than attempting to design the entire application at once.

> **Version note:** Current Spec Kit releases use the `speckit-specify` skill name, with invocation syntax determined by the selected agent integration. The transcript's phrases such as “spec kit specify” and “cloud code” refer to the Spec Kit specify stage and Claude Code.

## Where `specify` Fits in the Workflow

```text
constitution          project-wide rules
     ↓
specify               what the feature does and why
     ↓
clarify               resolve important ambiguity
     ↓
plan                   choose the technical approach
     ↓
checklist              review requirements quality
     ↓
tasks                  create an execution roadmap
     ↓
analyze                check artifact consistency
     ↓
implement → converge   build and verify the result
```

The shorter workflow can omit some optional quality gates for a small, well-understood feature. Complex, high-risk, or production-facing work benefits from the fuller sequence.

## Spec Kit or Ordinary Plan Mode?

A coding agent's ordinary plan mode can be enough for a small change whose requirements and implementation are already clear. Spec Kit adds value when the work:

- Contains multiple user scenarios or edge cases
- Requires product decisions before technical planning
- Spans several components or agent sessions
- Must remain reviewable by other people
- Needs traceability from requirements to tasks and implementation
- Is likely to evolve through several feature iterations

The additional artifacts require time to create and review. Their purpose is to reduce expensive ambiguity and rework, not to add ceremony to every one-line change.

## Start from a Reviewed Constitution

Before specifying the first feature, confirm that the project constitution exists and reflects the decisions accepted in the previous lessons:

```text
.specify/memory/constitution.md
```

A fresh agent session can work with this constitution because the decision is stored in the project, not because the agent retains the previous chat's private memory. The session must still read the repository artifacts.

Starting a clean session can be useful after a major stage because it removes abandoned discussion and intermediate reasoning from the context. It is safe only when all accepted decisions have been written to the project files.

## Invoke the Specify Skill

The same logical command can appear differently across integrations:

| Integration or reference style | Example |
| --- | --- |
| Claude Code or another hyphenated skills layout | `/speckit-specify` |
| Canonical dotted notation in Spec Kit references | `/speckit.specify` |
| Codex skills integration | `$speckit-specify` |

Run the skill inside the coding agent's chat, not in the terminal.

## Describe One Coherent Product Increment

Current Spec Kit creates one feature directory per `specify` invocation. An MVP can contain several closely related capabilities when they form one coherent user outcome, but unrelated features should be specified separately.

Avoid requests such as:

```text
Build drawing, cloud synchronization, collaborative editing, a plugin
marketplace, user accounts, billing, and mobile applications.
```

That request combines several products and risks producing requirements too broad to validate or implement safely.

A better first increment is:

```text
/speckit-specify

Create the first MVP feature for a desktop application that helps a
non-expert user design a simple three-dimensional space.

The user starts from a top-down square grid, draws a closed footprint by
selecting grid cells or edges, and turns that footprint into a simple
upward-extending 3D space. The MVP must make the drawing state visible,
allow the in-progress action to be cancelled, and prevent accidental loss of
completed work.

Focus on user behavior, scope, failure states, and measurable outcomes.
Do not choose frameworks, rendering libraries, storage technologies, or code
architecture. Apply the project constitution and identify only high-impact
questions that have no safe default.
```

This prompt gives the agent enough product intent to create scenarios without deciding the implementation prematurely.

## Natural-Language Input Is Expected

The developer does not need to write a formal specification before invoking `specify`. The command exists to transform natural-language product intent into a structured artifact.

Useful input usually covers:

- Who the user is
- What the user is trying to accomplish
- The primary interaction or workflow
- The boundaries of the first increment
- Important failure and cancellation behavior
- Known constraints from the product perspective
- What a successful outcome looks like

Dictation can help developers explain an idea more naturally and in greater detail. Review the transcription before submitting it, especially for dimensions, negations, technical terms, and names. Do not dictate confidential product details into a service that is not approved for that data.

## What `speckit-specify` Produces

Current Spec Kit creates a numbered feature directory such as:

```text
specs/001-grid-space-mvp/
├── spec.md
└── checklists/
    └── requirements.md
```

It also records the active feature directory in:

```text
.specify/feature.json
```

Downstream commands use this file to find the active feature. The active feature is not determined solely by the current Git branch. Git feature branches are optional and require the corresponding Spec Kit extension or hook.

### `spec.md`

The specification normally contains:

- Prioritized user stories
- Acceptance scenarios
- Functional requirements
- Edge cases
- Key entities when relevant
- Assumptions
- Measurable, technology-agnostic success criteria

### `checklists/requirements.md`

The built-in requirements checklist validates qualities such as:

- No implementation details leaked into the spec
- Requirements are testable and unambiguous
- Success criteria are measurable
- User scenarios and acceptance conditions exist
- Scope and assumptions are explicit
- Critical clarification markers have been resolved

This built-in checklist is maintained by the `specify` and `clarify` workflows. It is separate from the custom requirements-quality checklists produced later by `speckit-checklist`.

## The Constitution Constrains the Feature

During specification, the agent should read `.specify/memory/constitution.md`. Project-wide principles can constrain the feature without forcing implementation details into it.

For example:

| Constitutional principle | Specification-level effect |
| --- | --- |
| Non-expert usability | The first user flow must be learnable without specialist knowledge |
| Offline-first operation | Core MVP behavior cannot require a network account |
| Reversible actions | Cancellation and recovery scenarios must be specified |
| Lightweight experience | User-facing responsiveness outcomes should be measurable |
| Accessibility baseline | Required keyboard and visual interaction scenarios must be included |

If the specification reveals that a constitution principle is wrong or incomplete, amend the constitution deliberately. Do not rewrite project governance merely because one feature contains ordinary ambiguity.

## Clarifying the 3D Space MVP

The first draft exposes product decisions that materially affect behavior. The lesson demonstrates questions similar to the following.

### Grid or Free-Form Coordinates?

Question:

```text
Does the user draw freely, or must every point snap to a grid?
```

MVP decision:

- Drawing snaps to a square grid.
- One grid cell represents one meter.
- Free-form placement is outside the first increment.

This turns an ambiguous drawing tool into a predictable, testable interaction.

### Which Camera View Is Available?

Question:

```text
Does the MVP use a fixed top-down view, a tilted view, or a freely orbiting
camera?
```

MVP decision:

- Use a constrained view appropriate for drawing the footprint.
- Defer free-orbit camera controls to a later feature.

Deferring free orbit reduces interaction complexity without preventing it from being added later.

### How Does the User Cancel an In-Progress Action?

Question:

```text
What happens when the user wants to abandon a partially drawn footprint?
```

Candidate MVP behavior:

- `Escape` cancels the current drawing operation.
- Right-click may provide the same cancellation action if consistent with the platform's interaction conventions.
- Cancellation removes only the uncommitted preview and preserves previously completed work.

The final specification should choose an exact behavior rather than retain several alternatives.

### Mouse Input or Exact Dimensions?

Question:

```text
Can the user work only with pointer input, or can exact dimensions be entered
numerically?
```

This decision affects MVP scope and accessibility. If numeric input is deferred, the specification should state that explicitly rather than silently implying it exists.

### Invalid or Degenerate Shapes

Question:

```text
What happens when the footprint is open, self-intersecting, too small, or
otherwise invalid?
```

The specification needs observable behavior: prevent completion, highlight the invalid segment, preserve the editable draft, and explain what the user must correct.

### Extrusion Direction

Question:

```text
Can the generated space extend upward, downward, or in both directions?
```

MVP decision:

- Extend upward only.
- Downward extrusion is deferred to a future feature.

### Discarding Completed Work

Question:

```text
When must the application ask for confirmation before discarding work?
```

The requirement should distinguish between cancelling an uncommitted preview and deleting or replacing a completed model. Confirmations that appear for every minor action quickly become noise.

## Record Decisions in the Specification

Answers are valuable only when incorporated into `spec.md`. Do not leave binding product decisions solely in chat history.

Example functional requirements:

```text
- FR-001: The system MUST display a top-down square grid in which one cell
  represents one meter.
- FR-002: The user MUST be able to create a closed footprint whose points
  snap to grid intersections.
- FR-003: The system MUST display an in-progress preview before committing
  the footprint.
- FR-004: Pressing Escape during drawing MUST cancel only the in-progress
  footprint and MUST preserve completed spaces.
- FR-005: The user MUST be able to convert a valid closed footprint into a
  space extending upward from the drawing plane.
- FR-006: The system MUST prevent completion of an invalid footprint and
  identify the part that requires correction.
```

These requirements describe observable behavior without choosing a rendering engine, geometry library, event architecture, or persistence technology.

## Write Testable Acceptance Scenarios

A requirement becomes easier to review when expressed through examples.

```text
Given an empty one-meter grid,
When the user selects four points forming a closed rectangle,
Then the application shows a valid footprint preview aligned to the grid.
```

```text
Given a partially drawn footprint,
When the user presses Escape,
Then the unfinished footprint disappears
And all previously completed spaces remain unchanged.
```

```text
Given a footprint whose edges intersect,
When the user attempts to complete it,
Then the application does not create a 3D space
And identifies the invalid geometry for correction.
```

Acceptance scenarios clarify behavior without dictating code structure.

## Define Measurable Success Criteria

Success criteria should describe user or business outcomes and remain technology-agnostic.

Possible MVP criteria:

- A first-time target user can create a simple rectangular space without external documentation.
- A valid four-corner footprint can be completed and converted into a visible 3D space within a defined task-time threshold.
- Every drawing action aligns to the one-meter grid without manual correction.
- Cancelling an in-progress drawing never changes a previously completed space.
- All tested invalid-footprint scenarios prevent generation and provide actionable feedback.

The team must choose realistic numeric thresholds and a validation method. The agent should not invent product metrics and present them as agreed facts.

## Handle Assumptions and Open Questions

The current `specify` workflow makes reasonable defaults where safe and records assumptions. It reserves clarification markers for decisions that:

- Significantly affect scope or user experience
- Have multiple reasonable interpretations with different consequences
- Lack a safe default

Current core behavior limits the initial specification to three critical clarification markers. This prevents the first pass from turning into an unlimited interview, but it does not guarantee that all ambiguity has been resolved.

Review assumptions carefully. A plausible default chosen by an agent is still an assumption, not a confirmed product decision.

## Use `clarify` as a Separate Quality Gate

After the initial specification, Spec Kit may recommend the clarification stage:

```text
/speckit-clarify
```

Or with a focus:

```text
/speckit-clarify Focus on drawing cancellation, invalid geometry, exact
dimensions, and protection against accidental data loss.
```

The current clarification workflow asks up to five targeted questions per run and writes confirmed answers back into `spec.md`. It should run before technical planning when meaningful ambiguity remains.

If no critical ambiguity is found, `clarify` can report that no formal questions are necessary. Skipping it can be reasonable for a small personal experiment, but doing so knowingly accepts a higher risk of downstream rework.

## Review the Specification Before Advancing

Open the generated `spec.md` and requirements checklist. Confirm that:

1. The feature has one coherent user outcome.
2. The scope is small enough for one implementation cycle.
3. User stories are prioritized and independently testable where possible.
4. Every functional requirement describes observable behavior.
5. Acceptance scenarios cover primary, cancellation, and failure paths.
6. Assumptions are visible and reasonable.
7. Deferred functionality is explicitly out of scope.
8. Success criteria are measurable and technology-agnostic.
9. The feature complies with the project constitution.
10. No framework, database, rendering library, or code architecture has leaked into the product specification.
11. The requirements checklist accurately reflects the document instead of being accepted blindly.

Do not continue merely because the agent reports success. The specification becomes an input to every downstream decision.

## Reusing the Specification Outside Spec Kit

The main specification is a Markdown artifact and can be reviewed or used with another tool. It is valuable even outside the Spec Kit workflow because it records product intent in a structured form.

However, `spec.md` may rely on context stored elsewhere:

- The project constitution
- Linked research or domain documents
- Assumptions recorded in adjacent artifacts
- Repository-specific terminology
- Requirements checklist state

When moving the specification to another tool, provide the necessary context and preserve confidentiality. Do not paste proprietary specifications into an unapproved public service merely because the file format is portable.

## Common Mistakes

- Putting implementation technology into the `specify` prompt
- Combining several unrelated features in one invocation
- Treating an oversized product vision as a reviewable MVP
- Assuming a new chat remembers decisions that were never written to files
- Accepting inferred defaults without reviewing the Assumptions section
- Leaving important decisions only in chat messages
- Describing “easy,” “fast,” or “intuitive” behavior without measurable criteria
- Forgetting cancellation, invalid input, and data-loss scenarios
- Confusing the built-in requirements checklist with implementation progress
- Skipping `clarify` even though product ambiguity remains
- Copying `spec.md` elsewhere without its constitutional and repository context
- Rewriting the constitution to solve a feature-specific requirement problem

## Key Takeaway

The `specify` stage converts an informal feature idea into a reviewable product contract. Describe one coherent increment in natural language, keep the focus on user behavior and outcomes, and let the project constitution constrain the result without introducing premature implementation details.

The specification is complete only when its scenarios, requirements, assumptions, boundaries, and success criteria have been reviewed. Once ambiguity has been reduced—through the initial questions or the separate `clarify` stage—the project is ready to decide how the feature should be built.

## Further Reading

- [Spec-Driven Development quickstart](https://github.github.com/spec-kit/quickstart.html)
- [Spec Kit agentic SDD reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)
- [Current `specify` command template](https://github.com/github/spec-kit/blob/main/templates/commands/specify.md)
- [Current `clarify` command template](https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md)
