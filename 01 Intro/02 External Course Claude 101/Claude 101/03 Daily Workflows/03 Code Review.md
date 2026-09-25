# Code Review

Claude Code includes several features that can make Git workflows faster.

## Review with a Subagent

Before pushing a pull request, ask Claude to use a subagent to review the changes. The subagent works in its own context window and reviews the code with fresh eyes, without carrying the bias of the main agent that implemented the changes.

Restrict a code-review subagent to read-only tools. A reviewer should identify and report issues, not edit files. Store the subagent configuration in the repository so the entire team uses the same reviewer.

## The `/commit-push-pr` Skill

The `/commit-push-pr` skill handles the commit, push, and pull-request creation in one step.

If a Slack MCP server is configured and its channels are listed in `CLAUDE.md`, the skill automatically posts the pull-request link to the team's channel.

## Session Linking with `--from-pr`

When Claude creates a pull request through `gh pr create`, the session is linked to that pull request automatically. To return later—for example, to address review comments or fix a failing build—run:

```shell
claude --from-pr <PR_NUMBER>
```

Claude resumes the session associated with that pull request.

## Recap

Use a subagent for an unbiased code review before pushing. Use `/commit-push-pr` to automate the commit-to-pull-request workflow, and use `--from-pr` to resume work on an existing pull request.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=RKsADl0ZC3Y)
