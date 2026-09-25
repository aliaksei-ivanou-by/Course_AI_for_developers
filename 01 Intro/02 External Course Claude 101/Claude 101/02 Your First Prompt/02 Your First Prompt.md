# Your First Prompt

You interact with Claude Code as you would with any AI assistant. When entering a prompt, consider the available permission and planning modes: they can protect your project and make the workflow easier to control.

## Auto-Accept vs. Approval

Press `Shift + Tab` to cycle between permission modes:

- **Approval mode:** Claude asks for permission whenever it wants to edit a file or run a command.
- **Auto-accept mode:** File edits are approved automatically, but commands still require permission.

There is no single correct choice. Use the mode that matches the amount of control you want to retain.

![Claude Code auto-accept mode](Claude%20Code%20Auto-Accept%20Mode.png)

## Plan Mode

Plan Mode is also available through the `Shift + Tab` menu. It uses read-only tools to analyze the codebase and research the proposed implementation. Claude may ask clarifying questions before returning a detailed plan that it can execute.

Plan Mode is useful for complex changes and safe code reviews. It is especially helpful when asking Claude to perform a multi-step implementation.

![Claude Code Plan Mode](Claude%20Code%20Plan%20Mode.png)

## Example: Add a Dark Mode Toggle

Suppose an application needs a dark mode toggle. Open the project's root directory, run `claude`, and press `Shift + Tab` until Plan Mode is enabled. Then enter a descriptive prompt such as:

> My app needs a dark mode implemented across the entire app. Can you create a toggle switch on the header that allows a user to toggle between light mode and dark mode? I need you to find a good contrast color that works based on my existing light theme.

![Dark mode implementation prompt in Plan Mode](Dark%20Mode%20Prompt%20in%20Plan%20Mode.png)

Let Claude prepare the plan. Review it, and if it looks correct, accept it and allow Claude to request approval at each step. At the end, you can inspect what Claude changed and how it reached its conclusions.

## Recap

Be as descriptive as possible when prompting Claude Code. You can remain involved at every step through approval mode. Use Plan Mode to let Claude investigate the details and prepare an implementation before changing any code.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=gbetp6D7J_Q)
