# Installing GitHub Spec Kit

GitHub Spec Kit is a toolkit for spec-driven development with AI coding agents. It helps teams turn project principles and feature requirements into persistent specifications, implementation plans, task lists, and code changes.

The same workflow can be applied to two common situations:

- **Greenfield development:** starting a new application in an empty workspace
- **Existing projects:** documenting current standards and implementing new features in an established codebase

This lesson focuses on installing the Spec Kit command-line interface. Project initialization and constitution creation are introduced only briefly because they are covered in later lessons.

> **Version note:** Installation commands and prerequisites can change. The commands below reflect the official documentation at the time of writing. Check the current installation guide before using them in a production or managed corporate environment.

## Understand the Two Command-Line Tools

The installation uses two separate tools whose names are easy to confuse:

| Tool | Purpose |
| --- | --- |
| `uv` | A fast Python package and tool manager maintained by Astral |
| `specify` | The command installed by the Spec Kit package named `specify-cli` |

The command mentioned informally in the video as `uv tool install spec kit` is not the official package name. The package to install is **`specify-cli`**, and the resulting executable is **`specify`**.

Using `uv tool install` is recommended because it installs a command-line application in an isolated environment instead of adding its dependencies to the current project or the global Python environment.

## Prerequisites

Before installing Spec Kit, confirm that the environment meets the current requirements:

- Windows, macOS, or Linux
- Python 3.11 or newer
- `uv`, which is recommended, or another isolated installer such as `pipx`
- A supported AI coding agent for the later project workflow
- Git when the selected initialization options require it

Check the available versions:

```bash
python --version
uv --version
```

On Windows, Python may also be available through the launcher:

```powershell
py --version
```

If `uv` is not installed yet, complete the next step first.

## Step 1: Install `uv`

Choose **one** installation method appropriate for the operating system and organization.

### Windows: Official PowerShell Installer

Run the official installer in PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

In a managed corporate environment, do not bypass an organization policy without approval. Use an approved package manager or ask the responsible IT team which installation method is permitted.

### Windows: WinGet

If WinGet is available, `uv` can be installed without running a downloaded PowerShell script directly:

```powershell
winget install --id=astral-sh.uv -e
```

### macOS and Linux: Official Shell Installer

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Review externally downloaded installation scripts before running them when required by the project's security policy.

### Python-Based Alternatives

If Python and `pipx` are already available, install `uv` in an isolated environment:

```bash
pipx install uv
```

Installing through `pip` is also supported:

```bash
pip install uv
```

The `pipx` form is preferable for a standalone command-line application because it avoids mixing the tool's dependencies with other Python packages.

### Verify the Installation

Close and reopen the terminal if the installer changed `PATH`, then run:

```bash
uv --version
```

Do not continue until the terminal recognizes the `uv` command.

## Step 2: Install the Spec Kit CLI

There are two main installation channels. Use one channel consistently so that later upgrades remain predictable.

### Option A: Install a Pinned Release from GitHub

The official guide recommends pinning a specific release when installing directly from the source repository:

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

Replace `vX.Y.Z` with an actual release tag from the project's Releases page, including the leading `v`. Pinning makes the installed version explicit and helps a team reproduce the same environment.

Do not paste the placeholder command unchanged. For example, if the chosen release tag were `v1.2.3`, the end of the source URL would be `@v1.2.3`.

### Option B: Install from PyPI

To install the published `specify-cli` package from PyPI:

```bash
uv tool install specify-cli
```

Alternative installers are also supported:

```bash
pipx install specify-cli
```

```bash
pip install specify-cli
```

Prefer `uv tool install` or `pipx install` for CLI tools. A plain `pip install` may be appropriate in a deliberately managed Python environment, but it is easier to create dependency conflicts when unrelated tools share one environment.

## Step 3: Verify Spec Kit

Confirm that the CLI is available:

```bash
specify version
```

The command should print the installed Spec Kit version. You can also inspect the available operations:

```bash
specify --help
```

At this point, the installation is complete. Seeing an installer replace or reinstall an older version is normal when the tool already exists and a different version is requested. Always verify the resulting version instead of relying only on the installer's final message.

## Preview: Initialize a Project

Installation makes the `specify` CLI available globally. It does not yet configure a project. Initialization is a separate operation:

```bash
specify init <PROJECT_NAME> --integration <AGENT_KEY>
```

Replace the placeholders with the target project name and a supported agent integration. For example, the current official documentation uses keys such as `copilot`, `claude`, and `gemini`.

Spec Kit can initialize either a new project directory or an existing repository. Initialization in a non-empty project may create or modify agent instructions, templates, scripts, and feature artifacts. Commit or back up existing work first, review the integration-specific options, and inspect the resulting changes before accepting them.

On Windows, Spec Kit supports PowerShell-based project scripts. Other systems normally use shell scripts, and the initialization command also provides options for selecting a script type when needed.

The next practical stages are:

```text
install the CLI
      ↓
initialize the project integration
      ↓
establish the project constitution
      ↓
specify and implement individual features
```

## Greenfield and Existing-Project Workflows

The installer is the same for both workflows, but initialization and early project analysis differ.

### Greenfield Project

In an empty workspace, Spec Kit can establish the structure and principles before application code exists. This is a good time to make architecture, testing, security, and documentation expectations explicit.

### Existing Project

In an established repository, the agent should first study the current code, documentation, tests, and conventions. A generated constitution should reflect confirmed project standards rather than inventing new rules from an incomplete scan.

Spec-driven development does not guarantee that a complex feature will succeed in one prompt. Its value is that requirements and decisions become explicit, reviewable artifacts, which can reduce avoidable iterations and make later agent sessions more consistent.

## Troubleshooting

### `python` Reports a Version Older Than 3.11

Install or select a supported Python version before installing Spec Kit. On machines with several Python versions, confirm which interpreter the selected package manager uses.

### `uv` Is Not Recognized

1. Close and reopen the terminal.
2. Run `uv --version` again.
3. Check whether the installer's binary directory was added to `PATH`.
4. If necessary, use an approved alternative such as WinGet or `pipx`.

### `specify` Is Not Recognized

1. Restart the terminal after `uv tool install`.
2. Confirm that the installation completed without errors.
3. Check the tool environment with `uv tool list`.
4. Make sure the installed package was `specify-cli`, not a guessed package named `spec-kit`.

### Installation Is Blocked by Corporate Security Controls

Do not disable endpoint protection, proxy rules, certificate validation, or PowerShell policy controls merely to complete the installation. Use the organization's approved Python registry or package manager, or request the required access from the responsible team.

### The Latest Version Behaves Differently From the Lesson

Run `specify version`, compare it with the version used by the team, and consult the current release notes and installation guide. For shared projects, pinning a known release is safer than allowing every developer to install a different latest version.

## Installation Checklist

- [ ] Python 3.11 or newer is available.
- [ ] `uv --version` succeeds.
- [ ] `specify-cli` was installed from the intended source and version.
- [ ] `specify version` succeeds.
- [ ] The selected AI agent integration is supported.
- [ ] Existing project work is committed or backed up before initialization.
- [ ] Installation and initialization commands comply with organizational security policies.

## Key Takeaway

Installing GitHub Spec Kit is a two-tool process: first install the `uv` package manager, then use it to install the package named `specify-cli`. Verify both tools with `uv --version` and `specify version` before initializing a project.

Spec Kit can support both new and existing codebases, but its main benefit is not a promise of perfect one-shot generation. It provides a repeatable process in which project principles, feature requirements, technical decisions, and tasks are written down and reviewed before implementation.

## Further Reading

- [Local Spec Kit companion and source-inspection guide](github-speckit/README.md)
- [GitHub Spec Kit installation guide](https://github.com/github/spec-kit/blob/main/docs/installation.md)
- [GitHub Spec Kit repository](https://github.com/github/spec-kit)
- [`uv` installation documentation](https://docs.astral.sh/uv/getting-started/installation/)
