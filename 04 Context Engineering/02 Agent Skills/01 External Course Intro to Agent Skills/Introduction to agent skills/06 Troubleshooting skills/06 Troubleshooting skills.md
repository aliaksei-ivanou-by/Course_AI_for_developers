# Troubleshooting Skills

Most Skill problems fall into a small number of categories: invalid structure, failed discovery, unreliable triggering, naming conflicts, missing plugin content, or runtime failures. Diagnose them in that order so that basic configuration problems are eliminated before investigating execution details.

## Start with a Skills Validator

Validate the Skill structure before debugging its behavior. A validator can detect malformed YAML, missing required fields, invalid names, and unsupported directory layouts.

The Agent Skills reference implementation provides this command:

```shell
skills-ref validate path/to/skill
```

Installation varies by operating system. Follow the current instructions in the public [Agent Skills reference library](https://github.com/agentskills/agentskills/tree/main/skills-ref) before using the command.

## Skill Does Not Trigger

If the Skill is valid and available but Claude does not select it, inspect its description. Claude uses semantic matching, so the description must overlap with the intent and language of real requests.

To improve triggering:

1. Compare the description with the phrases users actually type.
2. State both what the Skill does and when it should be used.
3. Add realistic trigger phrases without making the description too broad.
4. Test several request variations.

For a performance-profiling Skill, test requests such as:

- “Help me profile this.”
- “Why is this slow?”
- “Make this faster.”

If a reasonable variation does not activate the Skill, adjust the description to include that intent.

## Skill Does Not Load

If the Skill does not appear in the available Skills list, verify its structure:

```text
.claude/
└── skills/
    └── performance-profiling/
        └── SKILL.md
```

- `SKILL.md` must be inside a named Skill directory, not directly under `.claude/skills/`.
- The filename must be exactly `SKILL.md`.
- The YAML frontmatter must be valid and contain the required `name` and `description` fields.
- Restart Claude Code after creating or changing the Skill.

Run Claude Code in debug mode to inspect loading errors:

```shell
claude --debug
```

Search the debug output for the Skill name or its directory path.

## Wrong Skill Gets Used

If Claude chooses the wrong Skill, the available descriptions may be too similar. Make them more specific by identifying distinct tasks, inputs, outputs, and trigger conditions.

For example, replace two generic descriptions such as `Reviews code for issues` with targeted descriptions for `frontend-accessibility-review` and `backend-security-review`.

## Resolve Priority Conflicts

When multiple Skills use the same name, Claude Code applies this priority order:

1. Enterprise
2. Personal
3. Project
4. Plugins

![Skill priority from enterprise settings to plugins](Skill%20Priority%20Hierarchy.png)

An enterprise `code-review` Skill therefore overrides a personal Skill with the same name. Usually, the simplest fix is to rename the lower-priority Skill more precisely. If an enterprise configuration is involved, contact the administrator before changing organization-managed behavior.

## Plugin Skills Do Not Appear

If an installed plugin does not expose its Skills:

1. Clear the relevant plugin cache.
2. Restart Claude Code.
3. Reinstall the plugin.
4. Validate the plugin's Skill directory structure.

If the problem remains, inspect debug output and confirm that every Skill has its own directory containing a correctly named `SKILL.md` file.

## Diagnose Runtime Errors

A Skill may load successfully but fail when its instructions or scripts run. Check these common causes:

- **Missing dependencies:** install required packages and document prerequisites clearly.
- **File permissions:** on Unix-like systems, executable scripts may require `chmod +x path/to/script`.
- **Path separators:** use forward slashes in Skill instructions and relative paths for cross-platform compatibility.
- **Incorrect working directory:** make paths explicit and avoid assuming that a script starts from a particular directory.
- **Unavailable tools:** confirm that required tools exist and are permitted in the current environment.

## Quick Troubleshooting Checklist

| Symptom | First check |
| --- | --- |
| Skill does not trigger | Improve the description and add realistic trigger phrases |
| Skill does not load | Check directory placement, filename, YAML, restart, and `claude --debug` |
| Wrong Skill is selected | Make competing descriptions more distinct |
| Personal or project Skill is ignored | Check for a higher-priority Skill with the same name |
| Plugin Skills are missing | Clear the cache, restart, reinstall, and validate the plugin structure |
| Skill fails at runtime | Check dependencies, permissions, paths, working directory, and tools |

## Lesson Reflection

- Which troubleshooting step would have saved the most time in a recent agent-customization problem?
- How could your team validate Skills automatically before sharing or merging them?

## Course Wrap-Up

You have completed Introduction to Agent Skills. You can now create, configure, organize, share, and troubleshoot Skills in Claude Code. Start with a real recurring problem: identify instructions you repeatedly give Claude, encode them in a focused Skill, validate the structure, and refine the description using realistic requests.

## Lesson Video

[Watch the lesson on YouTube](https://www.youtube.com/watch?v=YBa1cwaG7is)
