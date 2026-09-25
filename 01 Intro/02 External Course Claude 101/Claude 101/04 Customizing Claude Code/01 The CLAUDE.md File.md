# The `CLAUDE.md` File

One of the most useful Claude Code features is the `CLAUDE.md` file. It gives Claude Code persistent information about a project.

## The Problem It Solves

Without a `CLAUDE.md` file, Claude Code starts fresh in every session. It must explore the codebase again, determine which dependencies are required, and understand which features already exist. During that process, it may make assumptions that are difficult to correct later.

`CLAUDE.md` solves this problem. It is a Markdown file stored in the project root and read automatically at the beginning of every session. Its contents are appended to the prompt, making the file an onboarding guide for the codebase.

## Example

A typical `CLAUDE.md` file might contain:

```markdown
# Project

This is a Next.js 15 app using the App Router, Tailwind, and Drizzle ORM.

# Commands

- Dev server: `pnpm dev`
- Run tests: `pnpm test`
- Lint: `pnpm lint`

# Code Style

- Use 2-space indentation
- Prefer named exports
- All API routes go in `app/api/`
- Use server actions instead of API routes where possible
```

With this information available, Claude already knows the project's stack, commands, and conventions when you ask it to create a component or modify the code.

![Project instructions in CLAUDE.md](CLAUDE.md%20Project%20Instructions.png)

## `CLAUDE.md` for Teams and Individuals

Commit the project-level `CLAUDE.md` file to version control so the whole team benefits from it. Claude Code supports a hierarchy of memory files:

- **Project-level `CLAUDE.md`:** stored in the project root and shared with the team.
- **User-level `CLAUDE.md`:** stored in the user's configuration folder, applies across projects, and contains personal preferences.

## Tips

### Save Repeated Corrections

If you repeatedly give Claude the same correction—for example, always using server actions instead of API routes—ask it to save that rule to memory. It will then be available in future sessions.

![Saving a project rule to Claude memory](Saving%20Project%20Rule%20to%20Claude%20Memory.png)

### Reference Project Documentation

Use `@` with a file path to tell Claude about relevant documentation:

```markdown
## README.md

Please read if you need more information: @README.md
```

### Start Without a Memory File

Consider starting a project without `CLAUDE.md` so you can observe where the model repeatedly needs correction. This helps keep the file compact and focused. When you are ready, run `/init` to have Claude generate the file.

## Recap

The quality of a Claude Code session often depends on context. Use `CLAUDE.md` to provide the project stack, commands, preferences, and conventions, then refine the file as recurring needs become clear.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=O0FGCxkHM-U)
