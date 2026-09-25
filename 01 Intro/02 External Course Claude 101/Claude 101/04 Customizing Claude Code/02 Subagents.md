# Subagents

Claude can delegate work to subagents that break tasks down and execute component tasks in parallel. Each subagent operates in an isolated context window, which helps manage the main conversation's context.

## How Subagents Work

Tool calls used to explore a codebase or perform web research can consume a significant part of the main context window. The details found during exploration are not always relevant to the feature being developed.

A subagent can handle a task such as exploring the codebase in its own context window. When it finishes, it returns a summary to the main agent. This provides the result without adding the entire exploration process to the primary context.

## Creating a Custom Subagent

Subagents are defined in Markdown files with YAML frontmatter. The easiest way to create one is to run:

```text
/agents
```

Select **Create new agent**, then complete the setup steps:

1. Choose the agent's scope.
2. Define its purpose.
3. Select the tools it can access.
4. Choose its display color.

Claude generates the subagent's name, description, and prompt. This configuration also tells Claude when to invoke the subagent based on the user's request.

## Further Customization

- **Persistent memory** allows a subagent to retain information across conversations, which is useful when it is repeatedly used on the same projects.
- **Preloaded skills** can be configured with the `skills` key and a list of skill names. Unlike skills used in the main conversation, each preloaded skill is added to the subagent's context in full.

## Recap

Subagents keep the primary context focused by performing isolated work in separate context windows and returning only their results.

## Further Learning

For deeper coverage, see the dedicated **Introduction to Subagents** course.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=jKErNxuxPXg)
