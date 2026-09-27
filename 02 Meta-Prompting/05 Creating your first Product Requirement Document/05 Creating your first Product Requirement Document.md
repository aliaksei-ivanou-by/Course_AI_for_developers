# Creating Your First Product Requirements Document

This lesson applies meta-prompting to create a Product Requirements Document (PRD) for a feature or project. Instead of inventing a PRD format from scratch, the workflow uses reusable Markdown instructions from the third-party [snarktank/ai-dev-tasks](https://github.com/snarktank/ai-dev-tasks) repository.

The repository requires no dedicated application or complex installation. Its Markdown files act as structured prompts that guide an AI agent through requirements clarification, PRD creation, task decomposition, and iterative implementation.

> **Third-party content:** Review external prompt files before giving them to an agent, especially when that agent can modify files or run commands. Repository contents may change over time and should not be treated as automatically trusted.

## From an Idea to Implementable Tasks

The workflow separates product definition from implementation planning:

```text
Feature idea
    ↓
create-prd.md
    ↓
Clarifying questions and answers
    ↓
Reviewed PRD
    ↓
generate-tasks.md
    ↓
Reviewed implementation tasks
    ↓
Incremental implementation
```

This separation reduces the risk of starting implementation while the intended behavior, scope, or success criteria are still unclear.

## Why This Is Meta-Prompting

Meta-prompting means using one prompt to create or improve another instruction or artifact. In this workflow:

- `create-prd.md` is a reusable meta-prompt that guides the agent in creating a PRD.
- The developer's feature idea provides the initial product intent.
- The agent asks focused questions instead of silently inventing missing requirements.
- The reviewed PRD becomes structured context for implementation planning.
- `generate-tasks.md` turns the PRD into an actionable task list.

The result is a controlled chain of artifacts rather than one large request that asks an agent to understand, plan, and implement an underspecified feature at once.

## What the AI Dev Tasks Repository Provides

The workflow in this lesson uses two files:

| File | Purpose | Expected output |
| --- | --- | --- |
| `create-prd.md` | Clarifies a feature idea and turns it into a Product Requirements Document | `/tasks/prd-[feature-name].md` |
| `generate-tasks.md` | Converts reviewed requirements into parent tasks, subtasks, and a list of relevant files | `/tasks/tasks-[feature-name].md` |

The files are instructions for an AI agent, not executable software. They can be used by different AI-enabled IDEs and command-line agents as long as the selected tool can read the Markdown files and access the intended workspace.

## Step 1: Prepare the Workspace

Choose one of two starting points.

### Option A: Start a New Project

Create an empty directory and open it in the IDE. This is useful when the PRD will define a new product or a greenfield feature without an existing codebase.

### Option B: Use an Existing Project

Open a project that is already under development. A codebase-aware agent can then inspect relevant files and use existing product behavior, naming, architecture, and constraints when preparing the PRD.

Repository context can improve the document, but it cannot supply business decisions that have never been written down. The developer still needs to explain the problem, intended users, boundaries, and desired outcome.

## Step 2: Add the Ruleset

Clone the repository from the workspace terminal:

```bash
git clone https://github.com/snarktank/ai-dev-tasks.git
```

This creates an `ai-dev-tasks` directory containing the prompt files. Before using them:

1. Read the Markdown instructions.
2. Confirm that they do not request unwanted commands or access.
3. Adapt the output paths, terminology, and workflow to the project when necessary.

Cloning the repository inside another Git repository also creates a nested `.git` directory. If these prompt files are temporary and should not be committed with the project, add the directory to `.gitignore`:

```gitignore
ai-dev-tasks/
```

Another option is to clone the repository elsewhere and copy only the reviewed prompt files that the project needs.

## Step 3: Ask the Agent to Create a PRD

Open the AI chat or command-line agent and reference `create-prd.md` together with the feature idea:

```text
Use @ai-dev-tasks/create-prd.md.

Create a PRD for the following feature:
Add a dark-mode toggle to the settings page.
```

The `@file` notation is supported by many AI development tools, but it is not universal. If the selected agent does not understand it, attach the file through the interface or explicitly ask the agent to read the file by path before applying its instructions.

For an existing project, relevant files can also be referenced:

```text
Use @ai-dev-tasks/create-prd.md.

Create a PRD for adding a dark-mode toggle to the settings page.
Use the existing settings and theme implementation as project context.
Reference:
- @src/settings/
- @src/theme/
```

## Step 4: Answer the Clarifying Questions

The PRD instructions require the agent to ask only the most important questions before generating the document. The current template limits this stage to approximately three to five critical gaps and focuses primarily on what should be built and why.

Typical questions cover:

- The problem or product goal
- The target user
- Required user actions
- Scope and explicit exclusions
- Success criteria

The questions may be presented as a short multiple-choice questionnaire so that the developer can respond compactly:

```text
1A, 2C, 3B
```

These answers are part of the requirements. They should represent actual product decisions rather than selections made only to finish the questionnaire quickly.

## Step 5: Review the Generated PRD

The template instructs the agent to create a Markdown file named `prd-[feature-name].md` inside the `/tasks` directory. Its expected sections include:

1. Introduction and overview
2. Goals
3. User stories
4. Numbered functional requirements
5. Non-goals and out-of-scope behavior
6. Design considerations when applicable
7. Technical considerations when known
8. Success metrics
9. Open questions

The intended reader is a junior developer, so requirements should be explicit, actionable, and understandable without relying on undocumented assumptions.

Review the PRD before any implementation begins:

- Does it describe the correct problem and target users?
- Are the goals measurable?
- Are functional requirements precise and testable?
- Is out-of-scope behavior stated explicitly?
- Are design and technical constraints accurate?
- Are edge cases covered, such as unavailable network access or an unauthenticated user?
- Are unknowns listed as open questions instead of invented facts?

Ask the agent to revise incorrect decisions directly:

```text
Update the PRD to use PostgreSQL instead of SQLite.
Remove mobile support from the current scope.
Add the unauthenticated-user behavior to the functional requirements.
```

The reviewed PRD becomes the source of truth for the feature. Coding should not begin until the document represents the intended product closely enough to guide implementation and validation.

## Step 6: Generate the Implementation Tasks

After approving the PRD, use `generate-tasks.md` to create an implementation plan:

```text
Use @ai-dev-tasks/generate-tasks.md to create tasks from
@tasks/prd-dark-mode.md.
```

The current template uses a two-phase interaction:

1. The agent creates the high-level parent tasks and saves the task file.
2. The agent pauses and asks whether it should generate the subtasks.
3. The developer reviews the high-level plan and responds with `Go` when it is acceptable.
4. The agent expands the plan into smaller subtasks and identifies likely relevant files and tests.

By default, the task list begins with creating a feature branch unless the developer explicitly requests otherwise. The final document uses checkboxes so progress can be recorded as individual subtasks are completed.

## Step 7: Implement Incrementally

The generated task list is an implementation roadmap, not permission to execute everything without review. Work through it one small task at a time:

```text
Start with task 1.1 from the generated task list.
Stop after completing it so I can review the result.
```

After each task:

1. Inspect the changed files.
2. Run the relevant checks or tests.
3. Confirm that the change still agrees with the PRD.
4. Mark the completed subtask in the task file.
5. Continue only when the result is acceptable.

This creates frequent review checkpoints and makes mistakes easier to isolate than a single large implementation request.

## PRD and Task List Serve Different Purposes

| Artifact | Primary question | Typical contents |
| --- | --- | --- |
| PRD | What should be built, for whom, and why? | Goals, users, stories, requirements, non-goals, success metrics, open questions |
| Task list | How can the reviewed requirements be implemented incrementally? | Parent tasks, subtasks, relevant files, tests, dependencies, completion tracking |

The task list should remain traceable to the PRD. If implementation planning reveals a missing or contradictory requirement, update the PRD first and then regenerate or revise the affected tasks.

## Limitations and Safety Considerations

- A template cannot compensate for unclear or incorrect product decisions.
- The agent may still infer unsupported requirements or overlook edge cases.
- File references and `@` syntax vary between AI tools.
- The generic template may need adaptation for the project's architecture, compliance requirements, or delivery process.
- Third-party prompt files can change, so review updates before using them.
- A PRD is not a substitute for design review, technical discovery, threat modeling, or stakeholder approval when those activities are required.
- Generated tasks are proposals and must be checked against the actual repository.
- An agent with terminal access should still operate with appropriate permissions and human review.

## Practical Checklist

Before implementation begins, confirm that:

1. The third-party prompt files have been reviewed.
2. The feature goal and target users are clear.
3. Clarifying questions have been answered deliberately.
4. Functional requirements are numbered and testable.
5. Non-goals prevent accidental scope expansion.
6. Unknowns remain visible as open questions.
7. The PRD has been reviewed as the feature's source of truth.
8. High-level tasks have been approved before generating detailed subtasks.
9. Generated tasks refer to plausible files and tests.
10. Implementation will proceed in small, reviewable steps.

## Key Takeaway

Creating a PRD with `ai-dev-tasks` is a practical introduction to spec-driven development and context engineering. The developer begins with an idea, a reusable meta-prompt forces important questions to be answered, and the resulting PRD becomes structured context for implementation planning.

The value does not come from the template alone. It comes from the review loop: clarify the intent, inspect the PRD, approve the high-level plan, implement one task at a time, and continually verify the code against the agreed requirements.

## Further Reading

- [snarktank/ai-dev-tasks](https://github.com/snarktank/ai-dev-tasks)
- [`create-prd.md`](https://github.com/snarktank/ai-dev-tasks/blob/main/create-prd.md)
- [`generate-tasks.md`](https://github.com/snarktank/ai-dev-tasks/blob/main/generate-tasks.md)
