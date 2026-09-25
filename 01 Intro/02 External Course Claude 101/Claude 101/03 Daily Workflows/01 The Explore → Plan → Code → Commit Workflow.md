# The Explore → Plan → Code → Commit Workflow

If you take one thing away from this course, let it be this workflow: **Explore, Plan, Code, and Commit**. Without it, developers often jump straight to asking Claude to write code, which requires more course correction later.

## Explore and Plan

The fastest way to handle the Explore and Plan stages is with Plan Mode. In this mode, Claude cannot edit files. It uses read-only tools to gather information and determine how to approach the implementation.

Press `Shift + Tab` until **Plan Mode** appears below the text input, then enter a prompt such as:

![Plan Mode enabled in Claude Code](Plan%20Mode%20Active.png)

> I need to add WebP conversion to our image upload pipeline. Figure out where in the pipeline it should happen, whether we need new dependencies, and how to approach it.

Claude reads the relevant files, performs any necessary web searches, and returns a plan of action. Review the plan and decide whether it meets your criteria. If it does not, ask Claude to revise specific areas.

![Claude Code plan for WebP conversion](WebP%20Conversion%20Plan.png)

This is the best stage for course correction because no code has been written yet. You can also run the Explore subagent outside Plan Mode when you want a general summary of the codebase without making changes afterward.

## Code

When the plan looks correct, approve it and let Claude work through the plan items. You can choose whether Claude automatically accepts file edits or asks for approval each time.

Claude attempts to troubleshoot problems before considering the plan complete, but you may still need to intervene. Because the work began in Plan Mode, you retain the context behind the implementation and can use it to guide Claude's next decisions.

Use these practices to make the coding stage smoother:

- **Define success criteria.** Make the expected result explicit so Claude can determine what “correct” looks like.
- **Add useful tools.** Tools that help Claude complete its goals reduce back-and-forth communication. For web UI work, for example, the Claude in Chrome extension lets Claude Code control a browser tab and test the interface directly.

![Claude in Chrome extension](Claude%20in%20Chrome%20Extension.png)

- **Include a test suite.** Give Claude reliable tests that it can run continuously. Claude can also write tests, but verify that they are a dependable source of truth and do not produce false positives.

> **Quick tip:** If Claude repeatedly encounters the same issue, ask it to save the solution in the project's `CLAUDE.md` file.

## Commit

After testing the changes yourself and confirming the result, prepare to push the code. Before committing, run a code-review subagent. The subagent reviews the code with a fresh context and does not carry the main agent's bias from the implementation session.

![Code-review subagent in Claude Code](Code%20Reviewer%20Subagent.png)

Then ask Claude to generate a commit message in your preferred style. Repeat the workflow for the next task.

## Recap

- **Explore** gives Claude the relevant project context.
- **Plan** creates an implementation plan that defines the path to success.
- **Code** is the iterative work between you and Claude before reaching the final result.
- **Commit** adds a final review before pushing the code and starting the next feature.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=xJQuF02NAK8)
