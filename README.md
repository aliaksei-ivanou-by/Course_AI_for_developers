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
- Prompt structuring and context-aware prompt enhancement
- Context management and project instructions
- Subagents, skills, hooks, and Model Context Protocol (MCP)
- MCP configuration, practical use cases, and security considerations
- Applied workflows such as AI-assisted CI/CD troubleshooting and cloud migration

Later modules expand on meta-prompting, spec-driven development, context engineering, advanced agent techniques, and applied practices.

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

### Module 02 — Meta-Prompting

| Lesson | Full material | Short version |
| --- | --- | --- |
| 1. Structuring prompts | [Prompt Engineering in a Nutshell](02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29.md) | [Summary](02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29%20-%20Summary.md) |
| 2. Context-aware prompt enhancement | [Using Augment Code](02%20Meta-Prompting/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code.md) | [Summary](02%20Meta-Prompting/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code%20-%20Summary.md) |
| 3. Tool-agnostic meta-prompting | [Meta-Prompting with Codebase Awareness](02%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting.md) | [Summary](02%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting%20-%20Summary.md) |
| 4. Meta-prompting with NotebookLM | [Source-Grounded PRDs and Project Principles](02%20Meta-Prompting/04%20Meta-Prompting%20with%20NotebookLM/04%20Meta-Prompting%20with%20NotebookLM.md) | [Summary](02%20Meta-Prompting/04%20Meta-Prompting%20with%20NotebookLM/04%20Meta-Prompting%20with%20NotebookLM%20-%20Summary.md) |
| 5. Creating your first PRD | [PRD Generation with AI Dev Tasks](02%20Meta-Prompting/05%20Creating%20your%20first%20Product%20Requirement%20Document/05%20Creating%20your%20first%20Product%20Requirement%20Document.md) | [Summary](02%20Meta-Prompting/05%20Creating%20your%20first%20Product%20Requirement%20Document/05%20Creating%20your%20first%20Product%20Requirement%20Document%20-%20Summary.md) |
| 6. Module assessment | [Structured Prompts Quiz](02%20Meta-Prompting/06%20Structured%20Prompts%20Quiz/06%20Structured%20Prompts%20Quiz.md) | — |

### Module 03 — Spec-Driven Development

| Lesson | Full material | Short version |
| --- | --- | --- |
| 1. GitHub Spec Kit overview | [GitHub Spec Kit Process Flow](03%20Spec-Driven%20Development/01%20GitHub%20SpecKit%20Brief%20Overview/01%20GitHub%20SpecKit%20Brief%20Overview.md) | [Summary](03%20Spec-Driven%20Development/01%20GitHub%20SpecKit%20Brief%20Overview/01%20GitHub%20SpecKit%20Brief%20Overview%20-%20Summary.md) |
| 2. Installing GitHub Spec Kit | [Installing GitHub Spec Kit](03%20Spec-Driven%20Development/02%20Installing%20SpecKit/02%20Installing%20SpecKit.md) | [Summary](03%20Spec-Driven%20Development/02%20Installing%20SpecKit/02%20Installing%20SpecKit%20-%20Summary.md) |
| 3. Creating a project constitution interactively | [Creating a Spec Kit Constitution Interactively](03%20Spec-Driven%20Development/03%20SpecKit%20Constitution%20-%20Interactive/03%20SpecKit%20Constitution%20-%20Interactive.md) | [Summary](03%20Spec-Driven%20Development/03%20SpecKit%20Constitution%20-%20Interactive/03%20SpecKit%20Constitution%20-%20Interactive%20-%20Summary.md) |
| 4. Creating a project constitution non-interactively | [Creating a Spec Kit Constitution Non-Interactively](03%20Spec-Driven%20Development/04%20SpecKit%20Constitution%20-%20Non-Interactive/04%20SpecKit%20Constitution%20-%20Non-Interactive.md) | [Summary](03%20Spec-Driven%20Development/04%20SpecKit%20Constitution%20-%20Non-Interactive/04%20SpecKit%20Constitution%20-%20Non-Interactive%20-%20Summary.md) |
| 5. Deriving a constitution from an existing project | [Brownfield Spec Kit Adoption](03%20Spec-Driven%20Development/05%20SpecKit%20Constitution%20-%20Brownfield/05%20SpecKit%20Constitution%20-%20Brownfield.md) | [Summary](03%20Spec-Driven%20Development/05%20SpecKit%20Constitution%20-%20Brownfield/05%20SpecKit%20Constitution%20-%20Brownfield%20-%20Summary.md) |
| 6. Creating the first feature specification | [Spec Kit Specify](03%20Spec-Driven%20Development/06%20SpecKit%20Specify/06%20SpecKit%20Specify.md) | [Summary](03%20Spec-Driven%20Development/06%20SpecKit%20Specify/06%20SpecKit%20Specify%20-%20Summary.md) |
| 7. Clarifying the feature specification | [Spec Kit Clarify](03%20Spec-Driven%20Development/07%20SpecKit%20Clarify/07%20SpecKit%20Clarify.md) | [Summary](03%20Spec-Driven%20Development/07%20SpecKit%20Clarify/07%20SpecKit%20Clarify%20-%20Summary.md) |
| 8. Creating the technical implementation plan | [Spec Kit Plan](03%20Spec-Driven%20Development/08%20SpecKit%20Plan/08%20SpecKit%20Plan.md) | [Summary](03%20Spec-Driven%20Development/08%20SpecKit%20Plan/08%20SpecKit%20Plan%20-%20Summary.md) |
| 9. Generating the implementation task list | [Spec Kit Tasks](03%20Spec-Driven%20Development/09%20SpecKit%20Tasks/09%20SpecKit%20Tasks.md) | [Summary](03%20Spec-Driven%20Development/09%20SpecKit%20Tasks/09%20SpecKit%20Tasks%20-%20Summary.md) |
| 10. Executing and validating the implementation | [Spec Kit Implement](03%20Spec-Driven%20Development/10%20SpecKit%20Implement/10%20SpecKit%20Implement.md) | [Summary](03%20Spec-Driven%20Development/10%20SpecKit%20Implement/10%20SpecKit%20Implement%20-%20Summary.md) |
| 11. Adding a new feature after the MVP | [Spec Kit Post-MVP](03%20Spec-Driven%20Development/11%20SpecKit%20-%20Post-MVP/11%20SpecKit%20-%20Post-MVP.md) | [Summary](03%20Spec-Driven%20Development/11%20SpecKit%20-%20Post-MVP/11%20SpecKit%20-%20Post-MVP%20-%20Summary.md) |
| 12. Module assessment | [GitHub Spec Kit Quiz](03%20Spec-Driven%20Development/12%20SpecKit%20Quiz/12%20SpecKit%20Quiz.md) | — |

### Module 04 — Context Engineering

#### General Practices

| Lesson | Full material | Short version |
| --- | --- | --- |
| 1. Generating project instructions | [Generating Project Instructions for Coding Agents](04%20Context%20Engineering/01%20General%20practices/01%20Generating%20the%20agent%20instructions/01%20Generating%20the%20agent%20instructions.md) | [Summary](04%20Context%20Engineering/01%20General%20practices/01%20Generating%20the%20agent%20instructions/01%20Generating%20the%20agent%20instructions%20-%20Summary.md) |
| 2. Monitoring context and token usage | [Configuring the Status Line](04%20Context%20Engineering/01%20General%20practices/02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline.md) | [Summary](04%20Context%20Engineering/01%20General%20practices/02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline%20-%20Summary.md) |
| 3. Context caching, cost, and performance | [Context Windows, Prompt Caching, Cost, and Performance](04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md) | [Summary](04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price%20-%20Summary.md) |
| 4. Context size and model performance | [Context Window Size and Model Performance](04%20Context%20Engineering/01%20General%20practices/04%20Context%20Window%20-%20Performance/04%20Context%20Window%20-%20Performance.md) | [Summary](04%20Context%20Engineering/01%20General%20practices/04%20Context%20Window%20-%20Performance/04%20Context%20Window%20-%20Performance%20-%20Summary.md) |
| 5. Dividing work across sessions | [One Task, One Chat](04%20Context%20Engineering/01%20General%20practices/05%20Dividing%20tasks%20by%20sessions/05%20Dividing%20tasks%20by%20sessions.md) | [Summary](04%20Context%20Engineering/01%20General%20practices/05%20Dividing%20tasks%20by%20sessions/05%20Dividing%20tasks%20by%20sessions%20-%20Summary.md) |
| 6. Reducing MCP tool context overhead | [Reducing MCP Server and Tool Context Overhead](04%20Context%20Engineering/01%20General%20practices/06%20Reducing%20the%20number%20of%20MCP%20servers/06%20Reducing%20the%20number%20of%20MCP%20servers.md) | [Summary](04%20Context%20Engineering/01%20General%20practices/06%20Reducing%20the%20number%20of%20MCP%20servers/06%20Reducing%20the%20number%20of%20MCP%20servers%20-%20Summary.md) |
| 7. Providing current documentation | [Providing AI Agents with Up-to-Date Documentation](04%20Context%20Engineering/01%20General%20practices/07%20Providing%20AI%20with%20up-to-date%20knowledge/07%20Providing%20AI%20with%20up-to-date%20knowledge.md) | [Summary](04%20Context%20Engineering/01%20General%20practices/07%20Providing%20AI%20with%20up-to-date%20knowledge/07%20Providing%20AI%20with%20up-to-date%20knowledge%20-%20Summary.md) |
| 8. Introduction to codebase indexing | [Codebase Indexing for AI Agents](04%20Context%20Engineering/01%20General%20practices/08%20Intro%20to%20codebase%20indexing/08%20Intro%20to%20codebase%20indexing.md) | [Summary](04%20Context%20Engineering/01%20General%20practices/08%20Intro%20to%20codebase%20indexing/08%20Intro%20to%20codebase%20indexing%20-%20Summary.md) |
| 9. Consolidated context-engineering article | [Context Engineering for AI-Assisted Development](04%20Context%20Engineering/01%20General%20practices/09%20All%20of%20above%20lessons%20as%20a%20text%20article/09%20All%20of%20above%20lessons%20as%20a%20text%20article.md) | [Summary](04%20Context%20Engineering/01%20General%20practices/09%20All%20of%20above%20lessons%20as%20a%20text%20article/09%20All%20of%20above%20lessons%20as%20a%20text%20article%20-%20Summary.md) |

#### Agent Skills

| Lesson | Full material | Short version |
| --- | --- | --- |
| 1. External course: Introduction to Agent Skills | [Course overview](04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills.md) | [Summary](04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills%20-%20Summary.md) |

The Introduction to Agent Skills section also contains a structured [curriculum](04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/Introduction%20to%20agent%20skills/Curriculum.md) and an [About the Course](04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/Introduction%20to%20agent%20skills/About%20course.md) page.

## How to Use This Repository

1. Follow the numbered modules and lessons in order.
2. Read the full lesson when studying a topic for the first time.
3. Use the separate summary files for quick review.
4. Follow the linked public external materials when a lesson includes them.
5. Complete each available module quiz after finishing its lessons.
6. Verify time-sensitive product information against official documentation before applying it to production work.

## Repository Structure

```text
Course_AI_for_developers/
├── README.md
├── 01 Intro/
│   ├── 01 Welcome/
│   ├── 02 External Course Claude 101/
│   │   └── Claude 101/
│   ├── 03 Our Toolset as for Now/
│   ├── 04 Using MCP Servers/
│   └── 05 Intro Quiz/
├── 02 Meta-Prompting/
│   ├── 01 Structuring Prompts (Prompt Engineering in a Nutshell)/
│   ├── 02 Context-Aware Prompt Enhancement with Augment Code/
│   ├── 03 Tool-Agnostic Meta-Prompting/
│   ├── 04 Meta-Prompting with NotebookLM/
│   ├── 05 Creating your first Product Requirement Document/
│   └── 06 Structured Prompts Quiz/
├── 03 Spec-Driven Development/
    ├── 01 GitHub SpecKit Brief Overview/
    ├── 02 Installing SpecKit/
    ├── 03 SpecKit Constitution - Interactive/
    ├── 04 SpecKit Constitution - Non-Interactive/
    ├── 05 SpecKit Constitution - Brownfield/
    ├── 06 SpecKit Specify/
    ├── 07 SpecKit Clarify/
    ├── 08 SpecKit Plan/
    ├── 09 SpecKit Tasks/
    ├── 10 SpecKit Implement/
    ├── 11 SpecKit - Post-MVP/
    └── 12 SpecKit Quiz/
└── 04 Context Engineering/
    ├── 01 General practices/
    │   ├── 01 Generating the agent instructions/
    │   ├── 02 Configuring the Statusline/
    │   ├── 03 Context window - Caching and Price/
    │   ├── 04 Context Window - Performance/
    │   ├── 05 Dividing tasks by sessions/
    │   ├── 06 Reducing the number of MCP servers/
    │   ├── 07 Providing AI with up-to-date knowledge/
    │   ├── 08 Intro to codebase indexing/
    │   └── 09 All of above lessons as a text article/
    └── 02 Agent Skills/
        └── 01 External Course Intro to Agent Skills/
            └── Introduction to agent skills/
```

Full lessons and summaries are stored separately. Images and other reference files are kept next to the Markdown documents that use them.

## Responsible Use

AI coding agents can read and modify files, execute commands, run tests, and interact with external tools. Review meaningful actions and generated changes, grant only the access required for the task, and use official or internally approved integrations whenever possible.

## Project Status

This repository is a work in progress. The introduction, meta-prompting, and spec-driven development modules, including their assessments, are available now, together with the first nine general-practices lessons in context engineering and the complete six-lesson Introduction to Agent Skills external course. Additional course material will be added over time.
