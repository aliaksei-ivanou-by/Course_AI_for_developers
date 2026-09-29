---
name: stabilize
description: "Turn a concrete agent mistake, developer correction, recurring workflow friction, or repeated failure pattern into a durable project rule or reusable hidden project skill. Use immediately after \"don't do this again\", \"remember this\", repeated friction, or a proven process improvement. This is incident-driven learning; `embacc reflect` is the separate batch analysis of past sessions."
---

# Stabilize

Convert a concrete incident into durable behavior: **Incident -> Root cause -> Rule or Skill -> Verification**.

## 1. Establish the incident
Record what happened, what should have happened, where it occurred, and the evidence. Do not invent a recurrence from one ambiguous event.

## 2. Decide what should persist
Choose the smallest durable mechanism:
- **PROJECT.md rule** for a project-specific invariant or constraint;
- **hidden project skill** for a reusable multi-step procedure that the agent should invoke again;
- **canonical accelerator change** only when developing embacc itself and the lesson applies broadly.

Do not create a skill for a one-line preference that belongs as a rule.

Before writing a PROJECT.md rule, read the whole target section first, not just the new line in isolation:
- if the new insight duplicates or supersedes an existing bullet, replace that bullet instead of appending a new one;
- if it is too narrow or one-off to hold as a general project invariant, do not add it at all -- record it in the incident only.

A section that keeps growing because each addition looked reasonable on its own is still bloat; judge the new entry against the section as it stands, not in isolation.

## 3. Hidden skill location
For project-specific skills, resolve the state root with `embacc config .` and write:

`<external_state_dir>/agent-config/skills/<name>/SKILL.md`

Use standard YAML frontmatter (`name`, `description`) plus concise operational instructions, triggers, gates, outputs and failure behavior. Never place a learned project skill in the customer repository unless the developer explicitly asks.

## 4. Approval
For a new/changed PROJECT.md rule, show the exact proposed text and obtain explicit approval before writing. For a requested reusable skill, show its name/purpose before creating it when the user's intent did not already clearly authorize creation. Never overwrite an existing differing skill silently.

## 5. Verify
Read back the result, check it does not conflict with existing project rules/skills, and describe what future behavior should now change.

`embacc reflect` is different: it mines prior sessions in batch and may generate learned skills from repeated evidence. Do not call this skill `reflect` and do not treat the two mechanisms as the same operation.
