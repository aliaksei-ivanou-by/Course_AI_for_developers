# Installing Claude Code

Claude Code is simple to install whether you want to use it in the terminal, on the web, or in an IDE.

## Terminal

The available installation methods depend on the operating system:

- **macOS, Linux, or WSL:** use the `curl` installation command. Homebrew is also supported, but the Homebrew installation does not support automatic updates.
- **Windows PowerShell:** use the `Invoke-RestMethod` installation command.
- **Windows Command Prompt:** use the `curl` installation command.
- **Windows Package Manager:** `winget` is also supported, but this installation method does not support automatic updates.

![Claude Code terminal installation](Claude%20Code%20Terminal%20Installation.png)

After installation, navigate to the project directory and run:

```shell
claude
```

If the command is not available immediately, restart the terminal. During initial setup, choose a color theme and sign in using one of the available methods: a Claude account on a Pro, Max, or Enterprise plan, an API key, or an organization-provided Claude Enterprise account.

![Claude Code login methods](Claude%20Code%20Login%20Methods.png)

Claude Code can access the directory in which you start it and all of that directory's subfolders.

## Visual Studio Code

Open the Extensions panel and search for **Claude Code**. Select the extension published by Anthropic with the blue verification check, then install it.

After installation, you may need to restart VS Code. Open the command palette with `Ctrl/Cmd + Shift + P` and search for **Claude Code: Open in New Tab**. You can also use the Claude logo in the sidebar when it is visible.

![Claude Code extension for VS Code](Claude%20Code%20VS%20Code%20Extension.png)

The VS Code extension provides an experience similar to the terminal. You can also disable its UI and use Claude Code directly through the integrated terminal.

## JetBrains IDEs

Install the Claude Code plugin from the JetBrains Marketplace and restart the IDE. After restarting, click the Claude logo to open a pane containing the terminal experience alongside the editor.

![Claude Code plugin for JetBrains IDEs](Claude%20Code%20JetBrains%20Plugin.png)

## Claude Desktop

After installing and signing in to Claude Desktop, select **Code** at the top of the application. Code mode lets you work in a specific folder, change permissions, and use a cloud environment.

![Code mode in Claude Desktop](Claude%20Desktop%20Code%20Mode.png)

## Web

Open [claude.ai/code](https://claude.ai/code) or select **Code** in the sidebar of the Claude chat application. The web version works similarly to the desktop application but is limited to GitHub repositories.

![Claude Code web interface](Claude%20Code%20Web%20Interface.png)

## Which Interface Should I Use?

- Use the **terminal** to receive new features first.
- Use an **IDE integration** for a similar experience embedded in your editor.
- Use **Claude Desktop** to let Claude work in the background while you handle other tasks.
- Use **Claude Code on the web** to work remotely with projects stored in GitHub repositories.

Choose the interface that best fits your workflow.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=0kILa02vKuI)
