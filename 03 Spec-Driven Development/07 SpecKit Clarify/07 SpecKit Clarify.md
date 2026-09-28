# Clarifying a Feature Specification with Spec Kit

The `clarify` stage finds important ambiguities in the active feature specification, asks focused questions, and writes the confirmed answers back into `spec.md`. It runs after `specify` and before technical planning so the team does not design an implementation on top of unclear product behavior.

This lesson continues the first MVP for a desktop 3D-space modeling application. The initial specification is already detailed, so `clarify` concentrates on a small number of decisions involving interaction behavior, view mode, project scope, and workspace boundaries.

> **Version note:** Current Spec Kit documentation describes `clarify` as an optional quality gate that can ask up to five targeted questions per run. Exact command spelling depends on the installed coding-agent integration.

## Why Clarification Comes Before Planning

A technical plan turns requirements into architecture and implementation choices. If the requirements still have several reasonable interpretations, the plan must guess which product the team intended.

```text
unclear requirement
        ↓
implementation assumption
        ↓
incorrect plan and tasks
        ↓
expensive rework
```

Clarification moves that decision earlier:

```text
unclear requirement
        ↓
targeted product question
        ↓
answer recorded in spec.md
        ↓
plan based on confirmed behavior
```

The goal is not to ask every imaginable question. It is to resolve uncertainty whose answer would materially change user behavior, validation, architecture, data modeling, task decomposition, operational readiness, or compliance.

## Resetting the Agent Context Between Stages

The video starts by clearing a conversation that has grown to roughly 50,000 tokens. Beginning a fresh session can improve focus and reduce the amount of old discussion carried in the active context.

Important decisions survive only because they were written to durable project artifacts such as:

```text
.specify/memory/constitution.md
.specify/feature.json
specs/<active-feature>/spec.md
specs/<active-feature>/checklists/requirements.md
```

This is not hidden cross-session memory. A new agent session must read the relevant files again. That causes some repository discovery and token use, but it is usually more focused than carrying a long transcript containing abandoned ideas, corrections, and unrelated tool output.

Before clearing context, verify that:

1. All accepted product decisions are present in `spec.md`.
2. Project-wide principles are present in the constitution.
3. The correct active feature is recorded in `.specify/feature.json`.
4. There are no important answers that exist only in chat.
5. Generated changes have been reviewed or can be recovered from version control.

## Confirm the Active Feature

Current Spec Kit resolves the feature from `.specify/feature.json` rather than relying only on the checked-out Git branch. Before clarifying, inspect the file and the target specification:

```text
.specify/feature.json
specs/<active-feature>/spec.md
```

This matters when a repository contains several feature directories. Changing Git branches alone does not necessarily select a different Spec Kit feature.

## Invoke the Clarify Skill

Command syntax depends on the integration:

| Integration or reference style | Example |
| --- | --- |
| Claude Code or another hyphenated skills layout | `/speckit-clarify` |
| Canonical dotted notation in Spec Kit references | `/speckit.clarify` |
| Codex skills integration | `$speckit-clarify` |

Run it in the agent chat with no additional text for a broad ambiguity scan:

```text
/speckit-clarify
```

Or direct it toward a suspected problem area:

```text
/speckit-clarify Focus on drawing controls, camera behavior, workspace
boundaries, project limits, and accidental data loss.
```

The optional focus narrows prioritization. It should not instruct the agent to select answers without the product owner's confirmation.

## What the Clarification Scan Examines

The current workflow evaluates specification coverage across categories such as:

- Functional scope and explicit non-goals
- User roles and personas
- Domain entities, identity, relationships, and lifecycle
- Critical interaction and UX flows
- Error, empty, loading, and recovery states
- Performance, scale, reliability, and observability expectations
- Security, privacy, and compliance
- External integrations and data formats
- Edge cases and conflict handling
- Constraints and rejected trade-offs
- Terminology consistency
- Testable completion signals
- TODOs and vague adjectives

Each area can be clear, partial, or missing. The agent prioritizes only questions whose answers have meaningful downstream impact.

## How Current Clarification Questions Work

The current core workflow:

- Asks at most five questions in one run
- Presents one question at a time
- Uses two to five mutually exclusive choices when appropriate
- Provides a recommendation with a short rationale
- Allows a short custom answer when the listed choices do not fit
- Stops early when all critical ambiguity is resolved
- Respects requests such as `done`, `stop`, or `proceed`

A response can be as short as:

```text
B
```

or:

```text
recommended
```

Accepting the recommendation is convenient, but the recommendation is not automatically authoritative. Check it against the product goal, constitution, accessibility needs, and feature scope.

## Example Clarification Areas from the MVP

The transcript is partially garbled, but it clearly demonstrates several categories of product decision. The examples below preserve those categories without pretending that every original sentence was transcribed exactly.

### 1. Height-Adjustment Interaction

The first decision concerns how the user controls the vertical dimension after drawing a footprint.

Possible choices might include:

| Option | Behavior |
| --- | --- |
| A | After completing the footprint, vertical pointer movement adjusts height while the camera remains fixed |
| B | The user enters an exact numeric height |
| C | The application applies a fixed default height with no adjustment in the MVP |

This is a product interaction question because it changes what the user does and how the result is accepted. The implementation algorithm belongs in the later plan.

### 2. Projection or View Mode

The next decision concerns the MVP view presented while modeling, such as perspective, orthographic, or isometric projection.

The specification should define the user-visible behavior and scope:

- Which view is available in the first release?
- Can the user switch views?
- Does the selected view affect drawing precision?
- Which advanced camera modes are explicitly deferred?

The rendering API, projection matrix, and scene-graph implementation do not belong in `clarify` unless a technical constraint blocks correct product behavior.

### 3. Number of Objects and Scale Expectations

Another clarification distinguishes a single-object prototype from a project that can contain multiple modeled spaces or boxes.

Questions include:

- Can one project contain one object or many?
- Is object selection required in the MVP?
- Must objects overlap, touch, or remain separate?
- Is there a product-level capacity target?

If no meaningful scale target is required for acceptance, the technical plan can still choose reasonable internal structures. Do not invent a user-facing limit merely to fill the document.

### 4. Workspace and Grid Boundaries

The transcript discusses what happens when the cursor leaves the modeling area and whether the grid has visible bounds.

Potential product choices include:

| Option | Consequence |
| --- | --- |
| Finite visible workspace | Clear modeling boundary and deterministic out-of-bounds behavior |
| Expandable workspace | User can grow the working area intentionally |
| Effectively infinite grid | Flexible navigation but more complex limits and orientation behavior |

A finite visible grid can make the MVP easier to understand and test. The chosen answer should specify what the user sees and what happens at the boundary.

## Product Questions Versus Planning Decisions

Not every unresolved point belongs in the specification.

| Clarify now in `spec.md` | Defer to `plan` |
| --- | --- |
| What the user sees after completing the footprint | Which rendering library draws it |
| Whether height is adjustable or fixed | How height values are stored internally |
| Whether one project supports multiple objects | Which collection or entity structure is used |
| What happens outside the visible grid | How the coordinate system is represented |
| Which view modes the MVP exposes | How projection matrices are implemented |
| What error feedback the user receives | Which validation class or module produces it |

The video ends with no outstanding high-impact product ambiguities and one deferred planning decision. That is a healthy outcome: implementation choices do not need to be forced into the product specification.

## How Answers Are Persisted

For each accepted answer, the current workflow updates the active specification rather than leaving the decision only in conversation.

It can add a dated clarification section:

```markdown
## Clarifications

### Session 2026-09-28

- Q: How is the workspace bounded? → A: Finite visible grid.
```

It then updates the appropriate normative section as well:

- Functional behavior goes into Functional Requirements.
- Interaction decisions update User Stories or scenarios.
- Entity or lifecycle decisions update the data model.
- Non-functional answers update measurable success criteria.
- Failure behavior goes into Edge Cases or error handling.
- Terminology decisions are normalized throughout the spec.

The dated question record provides history; the updated requirement remains the authoritative rule. Contradictory older wording should be replaced, not preserved alongside the new decision.

Current Spec Kit saves the specification after each accepted answer, reducing the risk that a context loss discards the whole clarification session.

## Requirements Checklist Revalidation

If the feature contains the built-in checklist at:

```text
specs/<active-feature>/checklists/requirements.md
```

the clarification workflow re-evaluates it against the updated specification. An item can become checked when ambiguity is resolved or unchecked if a new answer exposes a gap.

This checklist state represents specification quality. It does not indicate that application code has been implemented.

## When No Questions Are Needed

The initial `specify` run may already have resolved every high-impact ambiguity. In that case, `clarify` should report that no critical questions are worth asking and recommend proceeding.

That result is not a failure or a reason to manufacture questions. Review the coverage summary and confirm that:

- The agent inspected the correct feature.
- Important assumptions are visible.
- Remaining gaps are low-impact or plan-level.
- The product owner agrees that the spec is ready.

The transcript initially reports an unusually complete specification, then performs a scan and resolves several remaining decisions. This illustrates that “looks complete” and “has no meaningful ambiguity” are separate judgments.

## Run Clarify More Than Once When Necessary

One run is limited to five accepted questions. A complex specification can be clarified in focused passes:

```text
/speckit-clarify Focus on permissions and data ownership.
```

```text
/speckit-clarify Focus on failure recovery and offline behavior.
```

```text
/speckit-clarify Focus on accessibility and keyboard workflows.
```

Do not split clarification into endless interviews. Stop when the remaining uncertainty would not materially change planning or acceptance tests.

## Review the Result Before Planning

After the command finishes, inspect the changed artifacts:

```bash
git diff -- specs/
git status --short
```

Confirm that:

1. Every accepted answer appears in `spec.md`.
2. Updated requirements are testable and unambiguous.
3. No contradictory alternative remains elsewhere in the document.
4. The dated clarification record matches the normative requirements.
5. Terminology is consistent.
6. Product decisions were not replaced with technical design.
7. Deferred items are clearly identified as planning decisions or lower-priority unknowns.
8. The requirements checklist reflects the updated spec accurately.

## Readiness to Proceed to `plan`

The feature is ready for planning when:

- No outstanding ambiguity would materially change feature scope or acceptance.
- Primary, cancellation, boundary, and failure behavior are specified.
- Assumptions and explicit non-goals are visible.
- Success criteria are measurable.
- Constitution constraints are satisfied.
- Remaining technical choices are intentionally deferred to planning.

The next command is the planning stage:

```text
/speckit-plan Describe the approved technical stack, architecture constraints,
and implementation guidance.
```

Do not start planning until the updated specification has been reviewed.

## Common Mistakes

- Clearing the session while important answers still exist only in chat
- Assuming a fresh session has private memory of earlier conversations
- Clarifying the wrong feature because `.specify/feature.json` was not checked
- Treating every missing detail as a reason to ask a question
- Accepting the recommended option without evaluating its trade-offs
- Asking several compound questions that cannot be answered independently
- Mixing rendering libraries, data structures, or code architecture into product clarification
- Leaving answers in the clarification log without updating normative requirements
- Retaining contradictory alternatives after a decision is accepted
- Treating checklist completion as implementation completion
- Manufacturing questions after the workflow reports no critical ambiguity
- Proceeding to planning with unresolved scope, security, or core UX decisions

## Key Takeaway

The `clarify` stage protects technical planning from ambiguous product intent. It scans the active specification, asks only high-impact questions, records each answer in `spec.md`, and revalidates the built-in requirements checklist.

Resetting the chat between stages can reduce context noise because Spec Kit stores accepted decisions in Markdown files. The files—not the previous conversation—are the source of truth. Once high-impact ambiguities are resolved and only implementation choices remain, the feature is ready for `plan`.

## Further Reading

- [Spec-Driven Development quickstart](https://github.github.com/spec-kit/quickstart.html)
- [Spec Kit agentic SDD reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)
- [Current `clarify` command template](https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md)
