# GitHub Spec Kit Quiz

**Minimum grade to pass:** 70%  
**Attempts allowed:** Unlimited  
**Number of questions:** 10  
**Question type:** Single choice

## Questions, Answers, and Feedback

### 1. How often does the project constitution usually need to be created?

- A. Every time the developer resets the conversation context
  - **Feedback:** Incorrect. Resetting context does not require recreating the constitution because the important work is stored in project Markdown files and can be read by a new agent session.
- B. Before every task in the task list is executed
  - **Feedback:** Incorrect. Tasks are created later in the workflow. The constitution is not recreated before every individual task; those tasks reuse the same project principles.
- C. Only after the implementation command has finished
  - **Feedback:** Incorrect. The constitution belongs near the beginning of the process so it can guide specification, planning, tasks, and implementation—not only after implementation has finished.
- D. Usually once, before it is reused in later iterations
  - **Feedback:** Correct. Defining the constitution can be difficult, but it normally needs to be created only once and can guide later work. It may still be amended deliberately when the project's principles genuinely change.

**Correct answer:** D. Usually once, before it is reused in later iterations.

### 2. What is the role of the optional clarification step?

- A. To automatically deploy the finished application
  - **Feedback:** Incorrect. The clarification step asks questions and improves requirements; it does not build or deploy the application.
- B. To replace the need for project principles entirely
  - **Feedback:** Incorrect. Question-driven clarification can help establish or refine missing details, but it does not remove the value of a constitution that records project-wide principles.
- C. To skip the specification and move directly into coding
  - **Feedback:** Incorrect. Clarification supports and improves the specification process; it does not replace the specification with immediate coding.
- D. To ask questions and reduce uncertainty before planning or implementation
  - **Feedback:** Correct. The clarification step identifies missing details and turns ambiguous decisions into explicit requirements before the AI creates a plan or starts building.

**Correct answer:** D. To ask questions and reduce uncertainty before planning or implementation.

### 3. Why can resetting the conversation context after each step be helpful?

- A. It guarantees that implementation will require no developer review
  - **Feedback:** Incorrect. Resetting context can improve efficiency and focus, but it does not remove the need for developer review of artifacts, code, tests, and behavior.
- B. It prevents Markdown files from being created in the project
  - **Feedback:** Incorrect. The workflow relies on Markdown files created by Spec Kit to preserve the constitution, specification, plan, tasks, and other decisions.
- C. It reduces conversation context as the work is saved in project files
  - **Feedback:** Correct. Since the constitution, specifications, plans, and tasks are stored in Markdown files, the conversation does not need to carry all previous context forever. Reset only after the current work has actually been saved and reviewed.
- D. It forces GitHub Spec Kit to forget the project principles
  - **Feedback:** Incorrect. The goal is not to lose important information. The project principles and other artifacts remain in repository files and can be loaded by the next session.

**Correct answer:** C. It reduces conversation context as the work is saved in project files.

### 4. When can the `speckit.specify` step be used after the initial MVP or proof of concept?

- A. Only after the constitution is deleted and recreated
  - **Feedback:** Incorrect. The constitution is meant to be reused across feature iterations, not deleted and recreated before each new feature.
- B. Only when the implementation command fails
  - **Feedback:** Incorrect. The Specify step is part of normal feature development, not only an error-recovery action after implementation fails.
- C. Only for replacing all existing project principles
  - **Feedback:** Incorrect. Project principles are handled by the constitution. The Specify step describes a feature and its expected behavior.
- D. For future iterations when adding new features
  - **Feedback:** Correct. After the initial MVP or proof of concept, a new feature can begin another Spec Kit cycle from the Specify step against the existing codebase.

**Correct answer:** D. For future iterations when adding new features.

### 5. What happens during the Plan step?

- A. A technical implementation plan is created
  - **Feedback:** Correct. The Plan step begins translating the reviewed specification into a technical implementation approach and may produce supporting design artifacts.
- B. The MVP is pushed to production automatically
  - **Feedback:** Incorrect. Planning does not automatically deploy, publish, merge, or push the product to production.
- C. The developer writes the complete source code manually
  - **Feedback:** Incorrect. Plan is not full manual implementation. It creates the technical approach that guides later task generation and execution.
- D. The AI deletes old Markdown files to reduce context usage
  - **Feedback:** Incorrect. The workflow depends on Markdown files as durable artifacts. They are not deleted during ordinary planning.

**Correct answer:** A. A technical implementation plan is created.

### 6. Why is it useful to break the plan into tasks?

- A. It prevents the AI from reading the project constitution
  - **Feedback:** Incorrect. The constitution remains useful context for later stages; creating tasks does not prevent the agent from applying project principles.
- B. It turns every feature into a single command with no review needed
  - **Feedback:** Incorrect. Even when some commands are non-interactive, the workflow still requires developer judgment, validation, and review.
- C. It divides larger implementation work into smaller manageable pieces
  - **Feedback:** Correct. The Tasks step organizes complex implementation work into smaller pieces that are easier to execute, review, validate, resume, and sometimes parallelize.
- D. It removes the need to review the final implementation
  - **Feedback:** Incorrect. Developers still need to review and test the agent's output. Task decomposition improves structure, not accountability.

**Correct answer:** C. It divides larger implementation work into smaller manageable pieces.

### 7. What should the `speckit.specify` step focus on?

- A. How to optimize the model's token usage during implementation
  - **Feedback:** Incorrect. Context efficiency is a useful operational concern, but it is not the main purpose of the Specify step.
- B. Which task should be implemented first by the AI
  - **Feedback:** Incorrect. Task ordering comes later, after the implementation plan and task breakdown have been created.
- C. What needs to be done and what behavior is expected
  - **Feedback:** Correct. The specification describes the feature from the requirements side: what the user does, what result the system should show, and why the behavior is needed.
- D. The exact source-code structure that must be generated
  - **Feedback:** Incorrect. Specify is not primarily about implementation details. Exact source structure and architectural decisions belong in Plan.

**Correct answer:** C. What needs to be done and what behavior is expected.

### 8. Why is the Constitution step often considered the hardest part of the process?

- A. It requires defining project principles, which may be unclear at first
  - **Feedback:** Correct. This step can be difficult because developers may not immediately know what their project principles should be or how to ask the AI to establish them.
- B. It requires the developer to manually implement every feature before using AI
  - **Feedback:** Incorrect. The Constitution step defines principles; it does not require developers to implement features manually before using AI-assisted development.
- C. It depends on external documentation that GitHub Spec Kit does not create
  - **Feedback:** Incorrect. External evidence may inform some principles, but the difficulty described in the course is knowing which principles to define and what to ask—not obtaining a required external document.
- D. It can only be completed after the MVP has already been deployed
  - **Feedback:** Incorrect. The constitution is normally established near the beginning, before feature specifications and implementation, so it can guide the MVP and later work.

**Correct answer:** A. It requires defining project principles, which may be unclear at first.

### 9. What is usually the first major step in the GitHub Spec Kit workflow?

- A. Running implementation immediately so the AI can discover the project structure
  - **Feedback:** Incorrect. The workflow begins with principles and written structure, not immediate implementation. Jumping straight to code removes the foundation that guides later stages.
- B. Creating a final deployment package for the finished application
  - **Feedback:** Incorrect. Deployment is not the first step; it occurs much later, after requirements, planning, implementation, and validation.
- C. Writing unit tests before any requirements are described
  - **Feedback:** Incorrect. Testing may be required by the project, but this workflow starts by establishing principles rather than writing tests before any requirements exist.
- D. Establishing the project constitution or principles
  - **Feedback:** Correct. The constitution defines project principles that guide future specifications, plans, tasks, and implementation. After initialization, constitution-first is the workflow taught in this module.

**Correct answer:** D. Establishing the project constitution or principles.

### 10. What kind of work is GitHub Spec Kit best suited for?

- A. Single helper functions that can be completed in one direct prompt
  - **Feedback:** Incorrect. A single simple helper function usually does not justify a full specification, plan, task breakdown, and implementation cycle.
- B. Tiny syntax fixes that do not need any written context
  - **Feedback:** Incorrect. The workflow is usually too structured for a tiny syntax change that does not require meaningful planning.
- C. Formatting-only changes that do not affect application behavior
  - **Feedback:** Incorrect. Formatting-only work is normally too simple for a full spec-driven cycle unless it belongs to a larger planned change.
- D. More complex features that benefit from planning and task breakdown
  - **Feedback:** Correct. Spec Kit is most useful when a feature is complex enough to benefit from planning, smaller tasks, controlled execution, and structured review.

**Correct answer:** D. More complex features that benefit from planning and task breakdown.

## Answer Key

| Question | Answer |
| --- | --- |
| 1 | D |
| 2 | D |
| 3 | C |
| 4 | D |
| 5 | A |
| 6 | C |
| 7 | C |
| 8 | A |
| 9 | D |
| 10 | D |
