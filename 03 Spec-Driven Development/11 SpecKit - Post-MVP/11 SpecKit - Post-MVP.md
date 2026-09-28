# Adding a New Feature after the MVP with Spec Kit

After an MVP has been implemented and accepted, Spec Kit can drive the next feature without rebuilding the project or rediscovering its principles from scratch. The existing code, constitution, and completed feature artifacts form the baseline; the new behavior gets its own specification and repeats the same quality cycle.

This lesson adds camera navigation to the desktop 3D-space modeling application. Users should be able to zoom with the mouse wheel, rotate the view by dragging with the middle mouse button, recover a useful view, and keep the original drawing workflow working.

> **Version note:** The current Spec Kit workflow also recommends `speckit-analyze` before implementation and `speckit-converge` afterward. Git repository and branch automation is optional and can be supplied by the Git extension; the core specification workflow does not require Git.

## The First MVP Becomes an Existing Project

The first feature started in a nearly empty workspace. The second feature is different: the application already has behavior that must be preserved, architecture that should be reused, and tests that can detect regressions.

The new cycle therefore has two simultaneous goals:

```text
add the camera-navigation behavior
                 +
preserve the accepted modeling behavior
                 ↓
       a safe incremental feature
```

Post-MVP development is not merely “run the same commands again.” Each stage must now reason about an existing codebase and explicit compatibility constraints.

## Start from an Accepted Baseline

The video opens a clean coding-agent session and confirms that the repository is on the main branch. A fresh conversation is useful, but begin only after the previous feature has been accepted and integrated.

Before starting the next specification:

1. Confirm that the intended baseline commit is present.
2. Check the current branch and working-tree state.
3. Pull or otherwise synchronize the approved baseline according to team policy.
4. Run the existing build and tests.
5. Verify that the earlier MVP still behaves as documented.
6. Confirm that the Spec Kit integration and constitution are available.
7. Create or switch to an appropriate feature branch before making feature changes when the project uses branches.

Useful Git checks include:

```bash
git branch --show-current
git status --short
git log -1 --oneline
```

Do not discard unrelated local changes to obtain a clean tree. Preserve them, move them to an appropriate branch or worktree, or ask their owner how to proceed.

### Why the Skills Are Still Available

The transcript notes that a new agent session still exposes all Spec Kit skills or slash commands. They are project-level integration files created during `specify init`, not temporary chat messages. Clearing the conversation does not remove them.

The new session still needs to read the repository, active feature state, constitution, and relevant artifacts. “Clean context” means the old conversation is absent; it does not mean the project has no context.

## Repeat the Feature Cycle

A separate user-facing capability starts another full feature loop:

```text
accepted main baseline
        ↓
specify the camera-navigation experience
        ↓
clarify interaction decisions
        ↓
plan changes against the existing architecture
        ↓
generate and analyze tasks
        ↓
implement in controlled phases
        ↓
converge, review, pull request, and merge
```

The constitution normally remains in force across all these features. Do not create a new constitution merely because the product has entered its second iteration.

## Specify the New User Experience

The transcript starts the new iteration with `speckit-specify` and describes the desired experience rather than its implementation.

Command syntax depends on the coding-agent integration:

| Integration or reference style | Example |
| --- | --- |
| Claude Code or another hyphenated skills layout | `/speckit-specify` |
| Canonical dotted notation in Spec Kit references | `/speckit.specify` |
| Codex skills integration | `$speckit-specify` |

A useful starting prompt is:

```text
/speckit-specify

Add camera navigation to the existing desktop modeling workspace. Users can zoom
in and out with the mouse wheel and rotate the camera by holding and dragging the
middle mouse button. Provide a reliable way to restore a useful model view.
Preserve the existing grid alignment, object creation, dimension adjustment, and
right-click cancellation behavior.
```

At this stage, describe observable behavior:

- Which user gesture triggers an action
- What the user sees as the camera moves
- Which existing interactions must remain unchanged
- How the user recovers from an inconvenient view
- What happens at input boundaries and during another active operation

Do not choose engine APIs, event types, plugins, mathematical representations, camera components, or source files in the specification. Those decisions belong to `plan`.

### Small Feature Does Not Mean Vague Feature

Camera navigation sounds compact, but it contains product decisions with visibly different outcomes:

- Does middle-drag orbit, pan, or do both with modifiers?
- What point does the camera orbit around?
- Does wheel input move the camera, change focal length, or alter orthographic scale?
- Are there minimum and maximum zoom levels?
- What happens when the pointer leaves the workspace?
- Can navigation occur during footprint drawing?
- How does the user reset the view?
- Do keyboard pan controls also move the orbit target?

A short implementation can still require a precise interaction contract.

## Inspect the Generated Specification

After generation, review the new feature directory rather than accepting the success message alone. Confirm that the specification:

- Represents a new feature rather than modifying the completed MVP artifact accidentally
- Describes user-visible navigation behavior
- Preserves existing drawing and cancellation behavior as compatibility requirements
- Defines acceptance scenarios that can be demonstrated
- Contains measurable success criteria
- Lists unresolved decisions explicitly
- Avoids implementation details

If important unanswered questions remain, proceed to `clarify` before planning.

## Clarify the Camera Interaction Model

The video runs `speckit-clarify` because the initial camera specification still has ambiguous behavior.

### 1. What Does the Camera Orbit Around?

Possible targets include:

- The fixed world origin
- A fixed model focus point
- The selected object
- The point under the cursor
- The center of visible geometry

The lesson selects a fixed focus target rather than blindly orbiting the world origin. The generated specification should define how that target is established and whether later actions can move it.

Without this decision, two correct-looking implementations could produce very different navigation experiences.

### 2. How Can the User Recover the View?

Navigation can leave the model off-screen, extremely small, or viewed from an awkward angle. The clarification adds a reset or frame-view action so the user cannot become permanently lost.

The acceptance scenario should define:

- The gesture or control that triggers reset
- What content is framed
- The resulting target, orientation, and zoom behavior
- Behavior when the scene is empty
- Whether reset is immediate or animated

“Provide reset view” is a direction; these details make it testable.

### 3. What Happens to the Orbit Target during Keyboard Panning?

The transcript also asks how the focus target behaves when the user pans with the arrow keys. The important requirement is that camera position and orbit target remain coherent: after panning, a later orbit should not unexpectedly snap back around an obsolete point.

The accepted answer must be written unambiguously into `spec.md`, for example by stating that the target translates with the pan. Because the source transcript is noisy at this point, the generated specification—not an inferred subtitle—is the authority for the exact chosen behavior.

### Clarification Produces Requirements, Not Just Answers

After the questions are answered, inspect the modified specification. Each accepted decision should appear in the relevant requirement, edge case, or acceptance scenario. A chat answer that was not persisted will disappear when the context is cleared.

If additional ambiguity remains, run clarification again with a focus area:

```text
/speckit-clarify Focus on input conflicts during active footprint drawing and on zoom boundaries.
```

## Plan against the Existing Architecture

After clarification, the transcript resets context and runs `speckit-plan`. The planner must inspect the existing input, camera, workspace, interaction-state, and test code before proposing changes.

A useful planning instruction could be:

```text
/speckit-plan

Extend the existing camera and input architecture; do not replace the renderer or
introduce a second interaction framework. Preserve current drawing gestures and
project data. Use the dependency versions already approved by the repository and
consult current official documentation for any camera APIs that are not established
in the codebase.
```

The plan should address at least:

- Camera state and the focus-target representation
- Middle-button gesture state and pointer motion
- Wheel direction, sensitivity, and zoom bounds
- Keyboard panning and target movement
- Reset or frame-view behavior
- Conflicts between navigation and drawing modes
- Regression-test strategy for existing modeling interactions
- Manual validation that cannot be covered adequately by unit tests

Planning should extend the accepted architecture. A new feature is not permission to rewrite working foundations unless the plan documents and justifies that change.

## Generate and Analyze the New Task List

After planning, start a fresh session if useful and run:

```text
/speckit-tasks
```

The new `tasks.md` should be specific to camera navigation. Representative tasks might cover:

- Camera-navigation state and defaults
- Orbit-target behavior
- Middle-mouse drag input
- Wheel zoom and limits
- Keyboard pan behavior
- Reset or frame-view action
- Interaction-mode conflict handling
- Automated camera-math or state-transition tests
- Regression tests for drawing and cancellation
- Quickstart and user-facing documentation updates

Do not mark tasks `[P]` merely because they have different names. Input mapping, camera state, and drawing-mode coordination may touch shared files or interfaces and therefore require sequential execution.

The transcript moves from tasks toward implementation quickly. In the current full workflow, run the read-only consistency gate first:

```text
/speckit-analyze
```

Resolve specification, plan, task, and constitution conflicts before modifying code.

## Implement the Feature Incrementally

The actual commands are familiar from the first MVP, but their inputs are a new feature artifact set:

```text
/speckit-plan
/speckit-tasks
/speckit-analyze
/speckit-implement
```

For a non-trivial interaction feature, scope implementation rather than waiting for one opaque run:

```text
/speckit-implement

Implement only the camera state, orbit target, and their tests. Preserve existing
behavior, update verified task markers, and stop before input integration.
```

Then continue with a separate validated batch:

```text
/speckit-implement

Implement the camera input and reset-view tasks. Run the navigation tests and the
existing modeling regression suite, then stop and report the evidence.
```

An incremental sequence makes it easier to isolate whether a failure came from camera mathematics, device input, drawing-state conflicts, or rendering integration.

## Clear Context at Artifact Boundaries

The video clears the agent context between Plan, Tasks, and later phases after observing a large token count. This is safe only because accepted work has been persisted to the feature artifacts.

Before each reset:

1. Confirm that the current command completed successfully.
2. Review the generated or modified artifacts.
3. Ensure that all decisions and blockers are written to files.
4. Save a recoverable Git checkpoint when appropriate.
5. Record the next command and intended scope.

Do not use a displayed token number such as 90,000 as a universal threshold. Agent platforms count context and billing differently. Artifact boundaries and task scope are more reliable signals than one fixed number.

Generation time is also not a quality measure. Whether Plan takes five minutes or Tasks and implementation take much longer, review the actual output and evidence.

## Validate Both the Feature and Its Regressions

The final demonstration checks the new navigation and then repeats existing modeling actions. That second part is crucial: a new input handler can easily steal events or corrupt drawing state.

A focused acceptance matrix could be:

| Scenario | Expected evidence |
| --- | --- |
| Middle-button orbit | Holding and dragging the middle mouse button rotates the view around the specified focus target |
| Wheel zoom | Scrolling changes the view in the specified direction and respects defined limits |
| Keyboard pan | Arrow-key movement follows the clarified behavior and keeps the orbit target coherent |
| Reset or frame view | The user can recover a useful view after extreme navigation |
| Orbit after pan | The camera orbits around the updated target without an unexpected jump |
| Draw after navigation | A new footprint or object can still be created after moving the camera |
| Navigate around geometry | Existing objects remain stable while the view changes |
| Cancel drawing | Right-click still cancels the active creation operation without unwanted geometry |
| Input conflict | Middle-button navigation during drawing follows the specified rule |
| Empty scene and boundaries | Reset, zoom, and orbit behave safely with no objects and at limit values |

The final narration mentions arrow-button camera movement, while the clarification segment describes arrow-key panning. If generated artifacts define one behavior more precisely, `spec.md` is the source of truth. A spoken demo summary must not silently redefine the feature.

Automated tests should verify deterministic camera-state and coordinate transformations where possible. Manual testing should validate device input, visual feedback, perceived direction, sensitivity, and interaction conflicts.

## Run the Convergence Cycle

After implementation and direct validation, run:

```text
/speckit-converge
```

or the syntax used by the selected integration:

```text
/speckit.converge
$speckit-converge
```

`converge` assesses the current code against `spec.md`, `plan.md`, `tasks.md`, and the constitution. It can identify work that is missing, partial, contradictory, or unrequested.

It does not modify application code or rewrite the existing artifact history. If gaps are found, it appends a Convergence phase to `tasks.md`; review those tasks, run `implement` again, and repeat convergence. If no gaps are found, `tasks.md` remains unchanged and the feature can proceed to final review.

Convergence supplements but does not replace code review, product acceptance, security analysis, accessibility review, or CI.

## Deliver through a Feature Branch and Pull Request

The transcript summarizes the delivery loop as commit, push, open a pull request, and merge to main. The safe version is:

```text
accepted main
    ↓
feature branch
    ↓
spec + plan + tasks + code
    ↓
local validation and convergence
    ↓
reviewed commit(s)
    ↓
push and pull request
    ↓
CI and human review
    ↓
merge into main
```

Before committing:

- Inspect every changed and untracked file.
- Verify that build output, logs, local configuration, and secrets are ignored.
- Review dependency and lockfile changes.
- Confirm that `tasks.md` accurately reflects verified work.
- Rerun the documented quality commands.
- Ensure the new feature did not modify completed MVP artifacts unintentionally.

Before pushing or merging:

- Verify the remote repository and intended visibility.
- Follow branch protection, commit-signing, and review policies.
- Wait for required CI and security checks.
- Resolve review findings and rerun acceptance tests.
- Obtain approval from the people accountable for the product and codebase.

Git state changes are separate from Spec Kit stages. The agent should not assume permission to create a public repository, push, open a pull request, or merge merely because implementation was requested.

## Git Integration Is Optional

Current Spec Kit core does not require Git or guarantee that a feature branch will be created. Teams can manage Git themselves or install the bundled Git extension after reviewing it:

```bash
specify extension add git
```

The active Spec Kit feature and current Git branch are separate pieces of state unless the selected workflow deliberately synchronizes them. Always verify both.

## Preserve the Previous Feature History

For a distinct post-MVP capability such as camera navigation, a flow-forward specification model is easy to audit:

```text
specs/001-grid-space-mvp/          completed MVP history
specs/002-camera-navigation/       new feature artifacts
```

Current Spec Kit documentation describes two other valid models:

| Model | Mutation rule | Main tradeoff |
| --- | --- | --- |
| Flow-forward | Create a new directory for new requirements | Strong history, but related context can be fragmented |
| Living spec | Update `spec.md` first and regenerate derived artifacts | One current contract, but rationale may be lost during regeneration |
| Flow-back | Allow discoveries in code or any artifact, then reconcile all affected files | Flexible, but vulnerable to silent drift |

The model is a team convention, not a CLI option. Document it so contributors know whether completed feature directories are historical records or editable contracts.

## Do Not Reinitialize Spec Kit for Every Feature

The project already contains the integration files, templates, and constitution. Start a new feature with `speckit-specify`; do not run `specify init` again merely because the MVP has been merged.

Keep two maintenance loops separate:

| Loop | Purpose |
| --- | --- |
| Feature evolution | Create specifications, plans, tasks, implementation, and convergence work for product changes |
| Spec Kit upgrade | Refresh managed commands, scripts, templates, integrations, extensions, or presets |

A forced reinitialization is an upgrade operation with its own review requirements. Protect project-specific customizations and inspect its diff.

## Continue the Product One Feature at a Time

After camera navigation has been accepted and merged, the application is ready for another iteration. Repeat the cycle for the next coherent, independently testable feature:

```text
specify → clarify → plan → checklist → tasks → analyze → implement → converge
```

Not every tiny bug or one-line maintenance change needs the full ceremony. Use the complete workflow when the change has meaningful product ambiguity, architectural impact, risk, or cross-team coordination needs.

The central habit is durable intent: make the behavior explicit before asking the agent to change code, and preserve the reasoning required to evaluate the result.

## Common Mistakes

- Starting the next feature from unreviewed or unmerged MVP code
- Editing the completed MVP specification for an unrelated new capability
- Describing camera APIs and internal components during `specify`
- Assuming “zoom” or “rotate” has only one reasonable interaction model
- Failing to persist clarification answers into `spec.md`
- Planning a replacement architecture instead of extending the existing project
- Skipping regression tasks for drawing, resizing, and cancellation
- Treating different filenames as proof that tasks can run in parallel
- Clearing context before decisions are saved in artifacts
- Using elapsed time or token count as proof of quality
- Trusting a successful visual demo without testing limits and input conflicts
- Allowing spoken narration to override the approved specification
- Skipping `analyze` before implementation or `converge` afterward
- Pushing or merging generated changes without reviewing the diff and CI results
- Assuming Spec Kit core automatically manages Git branches
- Running `specify init` again for every new feature

## Key Takeaway

Spec-driven development becomes most valuable after the first MVP. The accepted application, constitution, and earlier artifacts provide durable context, while each substantial new capability receives a fresh specification and repeats the same controlled cycle.

For camera navigation, define the user experience first, clarify the orbit target, recovery behavior, and panning semantics, then plan against the existing architecture. Implement in reviewable batches, test both new navigation and old modeling behavior, converge the result, and deliver it through the project's normal pull-request process. The same pattern can continue feature by feature as the product grows.

## Further Reading

- [Evolving specs in existing projects](https://github.github.com/spec-kit/guides/evolving-specs.html)
- [Spec persistence models](https://github.github.com/spec-kit/concepts/spec-persistence.html)
- [Spec Kit agentic SDD reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)
- [Current `converge` command template](https://github.com/github/spec-kit/blob/main/templates/commands/converge.md)
- [Spec Kit extensions reference](https://github.github.com/spec-kit/reference/extensions.html)
- [Handling complex features and context limits](https://github.github.com/spec-kit/concepts/complex-features.html)
