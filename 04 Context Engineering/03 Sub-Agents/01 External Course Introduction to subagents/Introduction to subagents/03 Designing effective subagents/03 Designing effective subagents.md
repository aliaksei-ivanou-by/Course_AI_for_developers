# Designing Effective Subagents

Creating a subagent is only the first step. A useful subagent also needs a clear trigger, a narrow responsibility, a predictable output format, explicit obstacle reporting, and only the tools required for its task.

Without these constraints, a subagent may explore too broadly, run longer than necessary, or return information that the main conversation cannot use efficiently.

## How Configuration Shapes Delegation

Claude can see the `name` and `description` of each available subagent. It uses this metadata to decide whether a task should be delegated and which subagent is the best match.

The description also helps the main agent construct the task prompt sent to the subagent. It therefore influences both:

1. **When the subagent runs.**
2. **What information the subagent receives.**

![A subagent description guiding delegation](Subagent%20Description%20Guides%20Delegation.png)

Keep the description concise, but include the information needed to create a useful assignment.

## Write Descriptions That Produce Better Inputs

A generic code-review description may cause the main agent to send a vague request such as "review the current changes." The subagent must then rediscover the scope before it can begin useful work.

A stronger description tells the main agent what inputs to provide:

```yaml
description: Reviews recently modified code for correctness, security, and project-standard compliance. When delegating, specify the exact files or diff to review. Use proactively after substantial code changes.
```

This description defines:

- the task: review recently modified code;
- the quality criteria: correctness, security, and project standards;
- the required input: exact files or a diff; and
- the trigger: substantial code changes.

The same pattern applies to other roles. A research subagent might require a precise question, an allowed source range, and citations in its returned result.

![A detailed prompt generated for a code-review subagent](Subagent%20Delegation%20Prompt.png)

## Define a Structured Output

An explicit output format is one of the strongest controls you can add to a subagent's system prompt. It gives the subagent a completion checklist and gives the parent conversation a predictable result to consume.

Without a clear stopping condition, a subagent may continue searching because it cannot determine when it has gathered enough information.

For a code reviewer, the system prompt could require this structure:

```markdown
## Summary

Briefly state what was reviewed and the overall assessment.

## Critical Issues

List security vulnerabilities, data-integrity risks, and logic errors that must
be fixed immediately. Cite files and lines.

## Major Issues

List architecture problems, significant quality defects, and performance risks.

## Minor Issues

List style inconsistencies, documentation gaps, and small optimizations.

## Recommendations

Provide specific, actionable improvements.

## Approval Status

State whether the change is ready to merge or requires changes.

## Obstacles Encountered

Report setup problems, environment quirks, workarounds, special command flags,
and dependencies that affected the review. Write "None" if there were no obstacles.
```

Requiring every section, including an explicit `None` where appropriate, makes omissions easier to detect.

## Report Obstacles and Workarounds

The final result should contain more than the successful conclusion. If the subagent discovered that a command needs a special flag, a dependency is missing, or the environment behaves unexpectedly, that information must return to the parent conversation.

Otherwise, the main agent may repeat the same failed steps and spend additional time rediscovering the workaround.

Ask the subagent to report:

- setup or permission problems;
- environment-specific behavior;
- failed approaches and their causes;
- workarounds that succeeded;
- commands requiring special flags or configuration;
- missing or conflicting dependencies; and
- uncertainty or work that could not be completed.

![A structured subagent result with obstacle reporting](Subagent%20Structured%20Output%20and%20Obstacles.png)

Obstacle reporting is especially important when the main conversation needs to continue implementation after receiving the subagent's result.

## Limit Tool Access

A subagent should receive the minimum tools needed to perform its role. Limited access reduces unintended side effects and makes the role easier to understand.

| Subagent role | Typical tools | Why |
| --- | --- | --- |
| Research or codebase exploration | `Glob`, `Grep`, `Read` | Can inspect information without modifying files |
| Code reviewer | `Glob`, `Grep`, `Read`, `Bash` | Can inspect code and run commands such as `git diff` or tests |
| Documentation editor | `Glob`, `Grep`, `Read`, `Edit`, `Write` | Can find and update documentation files |
| Implementation agent | Role-specific read, edit, and execution tools | Can modify and verify code within its assigned scope |

Avoid granting edit tools to a reviewer whose job is only to report findings. If execution is unnecessary, omit `Bash` as well.

Tool restrictions are not a substitute for precise instructions. Use both: define a narrow responsibility in the system prompt and enforce the relevant boundary through tool access.

## Put the Patterns Together

An effective subagent definition answers five questions:

1. **When should it run?** The description names concrete trigger scenarios.
2. **What input does it require?** The description tells the parent what scope and context to provide.
3. **What should it do?** The system prompt defines a focused responsibility and evaluation criteria.
4. **What should it return?** A structured format creates a clear stopping point.
5. **What may it access?** The tool list grants only the capabilities needed for the role.

Before using a new subagent in important work, test it on a representative task. Check whether it receives enough context, stops at the right point, reports limitations, and returns a result that the main conversation can act on directly.

## Recap

- The `name` and `description` help Claude select a subagent.
- The description also shapes the task prompt created during delegation.
- A structured output format gives the subagent a stopping condition.
- Obstacles and workarounds must be returned to prevent repeated discovery.
- Tool access should match the role and follow the principle of least privilege.
- Clear instructions and technical restrictions work best together.

## Lesson Reflection

- Does one of your current subagent descriptions specify the exact input it needs?
- Can the subagent determine that it is finished from its required output format?
- Which tools could you remove without preventing it from completing its task?

## What's Next?

In the final lesson, you will learn when subagents are worth using, how to coordinate delegated work, and which common anti-patterns to avoid.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=WPxWKT_OaU4)
