# GitHub Spec Kit Companion

This directory is a course companion for the official [GitHub Spec Kit repository](https://github.com/github/spec-kit). It intentionally does not contain a copied snapshot of the whole upstream project.

Installing Spec Kit does **not** require cloning its source repository. For normal course exercises, install the published CLI and let `specify init` create the files required by the selected agent integration.

## Quick Start

Run these commands in a terminal:

```bash
python --version
uv --version
uv tool install specify-cli
specify version
```

The current Spec Kit requirements include Python 3.11 or newer. For a reproducible environment, use the pinned-release installation command from the [official installation guide](https://github.com/github/spec-kit/blob/main/docs/installation.md) instead of automatically selecting the latest package.

## Verify Before Initializing a Project

```bash
specify version
specify self check
```

`specify version` checks that the CLI can run and reports its installed version. `specify self check` performs a read-only check for a newer release; it does not upgrade the installation.

## Initialize a Practice Project

Create a new project using an integration key supported by the installed Spec Kit version:

```bash
specify init <PROJECT_NAME> --integration <AGENT_KEY>
```

Do not type the angle-bracket placeholders literally. Replace them with the project name and integration key. Interactive initialization can also offer a selection when the terminal supports it.

For an existing repository, read the official existing-project instructions first. Commit or back up local changes before using options such as `--here` or `--force`, because initialization can create or update project files.

## Terminal Commands and Agent Commands Are Different

Use the terminal for CLI setup and project initialization:

```text
uv tool install specify-cli
specify version
specify self check
specify init ...
```

After initialization, use the generated Spec Kit skills or commands inside the selected coding agent's chat. Their exact spelling depends on the integration and mode. Examples in current official documentation include `/speckit-*` skill commands, while other integrations may expose a different form.

Do not paste a chat skill such as `/speckit-specify` into PowerShell or Bash, and do not paste a terminal command such as `specify init` into the agent chat expecting it to behave like a Spec Kit workflow stage.

## Optional: Inspect the Upstream Source

The source code is useful when studying templates, integrations, release history, or implementation details, but it is not needed for ordinary use. To inspect it without permanently copying it into the course repository, clone it into the ignored `upstream` directory:

```bash
git clone --depth 1 https://github.com/github/spec-kit.git upstream
```

Update that local checkout later with:

```bash
git -C upstream pull --ff-only
```

The accompanying `.gitignore` excludes `upstream/` so that the external repository is not accidentally committed as a nested Git repository. Use a proper Git submodule only when the course intentionally needs to pin and distribute a specific upstream revision.

## Useful Official References

- [GitHub Spec Kit repository](https://github.com/github/spec-kit)
- [Installation guide](https://github.com/github/spec-kit/blob/main/docs/installation.md)
- [Documentation site](https://github.github.com/spec-kit/)
- [`uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/)
