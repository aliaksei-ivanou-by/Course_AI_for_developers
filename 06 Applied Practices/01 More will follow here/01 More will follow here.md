# Applied Practices: What Comes Next

## From Foundations to Engineering Outcomes

Thank you for completing the foundational part of the course. You now have the core techniques needed to structure AI-assisted work: clear instructions, explicit specifications, focused context, appropriate tool selection, controlled agent workflows, and systematic verification.

The Applied Practices module is optional. It moves from individual techniques to end-to-end engineering scenarios where success depends on the complete result rather than on a convincing model response.

## Purpose of This Module

Applied lessons connect the practices introduced earlier in the course. A realistic task may require you to:

- understand an existing system and its constraints;
- define a concrete outcome and completion criteria;
- select an appropriate model, agent, and tool set;
- divide work into reviewable steps;
- control permissions, credentials, and external actions;
- validate code and infrastructure with deterministic checks; and
- document decisions, limitations, and evidence.

The goal is not to demonstrate that an agent can generate code. The goal is to show how AI-assisted work can produce a result that is correct, secure, maintainable, and ready for human review.

## An Evolving Collection of Case Studies

This module will be updated with new practical materials and showcases. Future cases may cover workflows introduced in the course overview, such as:

- diagnosing and repairing a failing CI/CD pipeline;
- moving an instant prototype to a controlled cloud environment;
- delivering a bounded full-stack feature or project;
- using agents to automate repeatable engineering work; and
- comparing manual and AI-assisted approaches to the same task.

The exact tools may change, but the engineering method should remain transferable.

## A Common Structure for Applied Lessons

Each case study should make the following elements visible:

| Element | Question |
| --- | --- |
| Starting state | What repository, system, failure, or prototype exists before the work begins? |
| Objective | What observable outcome must be achieved? |
| Constraints | Which technologies, policies, budgets, permissions, and boundaries apply? |
| Plan | How will the work be divided into understandable and reviewable steps? |
| Execution | Which actions are performed by the developer, agent, or external tool? |
| Verification | Which tests, scans, deployments, or manual checks prove the result? |
| Evidence | What logs, diffs, measurements, and decisions should be retained? |
| Retrospective | What worked, what failed, and what should change next time? |

This structure helps separate a reproducible engineering workflow from a polished demonstration that hides assumptions or failed attempts.

## How to Use the Applied Material

1. Read the case objective and constraints before looking at the implementation.
2. Reproduce the workflow in a disposable repository, branch, account, or sandbox.
3. Replace sample requirements with constraints from your own environment.
4. Grant the agent only the permissions required for the current step.
5. Inspect plans, commands, diffs, and external actions before accepting them.
6. Run the same deterministic checks that would be required without AI.
7. Compare the final result, time, cost, failures, and review effort with an appropriate baseline.
8. Record lessons that can become project instructions, checklists, skills, tests, or automation.

Do not copy commands blindly. Cloud services, APIs, agent features, prices, and security requirements change, so verify current official documentation before repeating a recorded workflow.

## Definition of Done for an Applied Exercise

An exercise is not complete merely because the agent says it succeeded. A proportionate definition of done can include:

- the requested behavior or operational outcome is observable;
- acceptance criteria are satisfied;
- relevant automated checks pass;
- the diff contains no unexplained or unrelated changes;
- secrets and sensitive data have not been exposed;
- external resources and costs are understood;
- rollback or recovery is possible where appropriate;
- limitations and remaining risks are documented; and
- a human reviewer can follow the evidence.

Use stronger controls for production systems, customer data, infrastructure changes, and other consequential work.

## Updates

The module is intentionally open-ended and will grow as useful case studies become available. Return to the repository periodically or follow the course newsletter for new materials.

## Key Takeaway

Applied practice turns isolated AI techniques into an accountable engineering process. Focus on observable outcomes, explicit constraints, safe execution, and verification evidence. The value of an AI-assisted workflow is demonstrated by the quality of the completed work, not by the amount of automation it contains.
