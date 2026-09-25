# AI for Developers

Practical course materials for AI-assisted software development. The course focuses on using modern AI coding agents to accelerate real engineering work while keeping developers responsible for planning, implementation decisions, review, security, and final results.

The repository contains full lesson notes, concise summaries, external-course notes, reference materials, and quizzes. All materials are written in English and organized in the recommended learning order.

> **Time-sensitive content:** The course reflects the AI development landscape around mid-2026. Model availability, product features, pricing, and usage limits can change quickly.

## Who This Course Is For

The course is designed primarily for:

- Software developers
- DevOps engineers
- QA engineers
- Project managers and business analysts
- Engineering managers and technical leads

It can support both beginners who want to learn faster and experienced professionals who want to improve their productivity with AI-assisted workflows.

## What You Will Learn

The course introduces:

- AI coding agents and their role in software development
- Claude Code, OpenAI Codex, and Google Antigravity
- Terminal- and editor-based agent workflows
- The explore → plan → code → commit workflow
- Context management and project instructions
- Subagents, skills, hooks, and Model Context Protocol (MCP)
- MCP configuration, practical use cases, and security considerations
- Applied workflows such as AI-assisted CI/CD troubleshooting and cloud migration

Later modules are expected to cover meta-prompting, spec-driven development, context engineering, advanced agent techniques, and applied practices.

## Current Course Content

### Module 01 — Introduction

| Lesson | Full material | Short version |
| --- | --- | --- |
| 1. Welcome and course overview | [Introduction to AI-Assisted Development](01%20Intro/01%20Welcome/01.%20Intro.%20AI%20Assisted%20Development.md) | [Summary](01%20Intro/01%20Welcome/01.%20Intro.%20AI%20Assisted%20Development%20-%20Summary.md) |
| 2. External course: Claude Code 101 | [Course overview](01%20Intro/02%20External%20Course%20Claude%20101/02.%20External%20Course%20Claude%20101.md) | [Summary](01%20Intro/02%20External%20Course%20Claude%20101/02.%20External%20Course%20Claude%20101%20-%20Summary.md) |
| 3. Current AI development toolset | [Claude Code, Codex, and Antigravity](01%20Intro/03%20Our%20Toolset%20as%20for%20Now/03%20Our%20Toolset%20as%20for%20Now.md) | [Summary](01%20Intro/03%20Our%20Toolset%20as%20for%20Now/03%20Our%20Toolset%20as%20for%20Now%20-%20Summary.md) |
| 4. Using MCP servers | [Using MCP Servers](01%20Intro/04%20Using%20MCP%20Servers/04%20Using%20MCP%20Servers.md) | [Summary](01%20Intro/04%20Using%20MCP%20Servers/04%20Using%20MCP%20Servers%20-%20Summary.md) |
| 5. Module assessment | [Introduction Module Quiz](01%20Intro/05%20Intro%20Quiz/05%20Intro%20Quiz.md) | — |

The Claude Code 101 section also contains structured notes for every lesson. See its [curriculum](01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/Curriculum.md) for direct navigation.

## How to Use This Repository

1. Follow the numbered modules and lessons in order.
2. Read the full lesson when studying a topic for the first time.
3. Use the separate summary files for quick review.
4. Follow the linked external materials when a lesson includes them.
5. Complete the quiz after finishing the introduction module.
6. Verify time-sensitive product information against official documentation before applying it to production work.

## Repository Structure

```text
Course_AI_for_developers/
├── README.md
└── 01 Intro/
    ├── 01 Welcome/
    ├── 02 External Course Claude 101/
    │   └── Claude 101/
    ├── 03 Our Toolset as for Now/
    ├── 04 Using MCP Servers/
    └── 05 Intro Quiz/
```

Full lessons and summaries are stored separately. Images and other reference files are kept next to the Markdown documents that use them.

## Responsible Use

AI coding agents can read and modify files, execute commands, run tests, and interact with external tools. Review meaningful actions and generated changes, grant only the access required for the task, and use official or internally approved integrations whenever possible.

## Project Status

This repository is a work in progress. The introduction module is available now, and additional course modules will be added over time.
