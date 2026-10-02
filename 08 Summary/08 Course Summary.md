# AI for Developers — Course Summary

This summary condenses the course into its key topics: LLMs and agents, tokens and the context window, prompt and context engineering, memory files, session management, model choice, specification-driven development, skills, hooks, subagents, MCP, security, cost control, team standardization, and the Innowise Accelerator. Each topic is explained briefly, with links to the lessons where it is taught in depth. Use it for review or as a map back into the course.

A Russian version is available in [08 Course Summary (RU)](08%20Course%20Summary%20%28RU%29.md).

> **Time-sensitive content:** The toolset reflects a June 2026 snapshot, and later lessons were checked in autumn 2026. Specific techniques may age within three to six months. Verify models, commands, prices, and limits against current official documentation.

**How to read this page**

- Each section covers one area of the course and is divided into short topics.
- **Lessons:** lines link to the lessons that cover the topic in depth.
- Module 07 links lead to dedicated lessons on few-shot prompting, RAG, model routing, prompt-injection defenses, and RTK/Caveman.
- A compact map of all course lessons is at the end.

## Contents

1. [AI Fundamentals](#1-ai-fundamentals)
2. [Prompt Engineering and Meta-Prompting](#2-prompt-engineering-and-meta-prompting)
3. [Context Engineering](#3-context-engineering)
4. [Memory Files](#4-memory-files-project-rules)
5. [Session Degradation](#5-session-degradation)
6. [Models: Speed, Cost, Quality](#6-models-speed-cost-quality)
7. [Specification-Driven Development](#7-specification-driven-development-sdd)
8. [AI-Assisted Tools: Skills, Commands, Hooks, Scripts, Subagents](#8-ai-assisted-tools-ide-and-terminal)
9. [Model Context Protocol](#9-model-context-protocol-mcp)
10. [Security and Privacy](#10-security-and-privacy)
11. [Monitoring, Debugging, and Cost Control](#11-monitoring-debugging-and-cost-control)
12. [Tool Selection and Standardization](#12-tool-selection-and-standardization)
13. [Innowise Accelerator](#13-innowise-accelerator)
14. [Ten Principles of the Course](#14-ten-principles-of-the-course)
15. [Course Map](#15-course-map)

---

## 1. AI Fundamentals

### LLMs and Agents

#### LLMs

A large language model is a neural network (a transformer) trained on large text and code corpora to predict the next token. Given input tokens, it generates output tokens one at a time. It has no memory between requests beyond what is in the context, its knowledge stops at a training cutoff, and it can produce fluent but wrong answers (hallucinations).

#### LLMs vs AI agents

An LLM is "text in, text out". An agent is an LLM running **in a loop with tools** and feedback from the environment: it reads files, runs terminal commands, calls APIs, sees the results, and decides the next step until the goal is reached. The loop is: gather context → act → verify → finish or repeat. The user can interrupt and steer at any point.

#### Tool calling

The model executes nothing itself. It returns a **structured tool call** (tool name and JSON arguments, chosen from tool definitions in its context). The harness—Claude Code, Codex, OpenCode—executes the call, subject to permissions, and puts the result back into the context. Without tool calling, the model can only describe actions, not perform them or observe their outcome.

#### Agent loop vs single-shot prompting

Single-shot: one request, one answer, no feedback. Agent loop: plan → act → observe → adjust, repeated. The agent sees the results of its own actions (a failing test, a compiler error) and corrects course. This is also the planning/execution cycle: Claude Code's Plan Mode separates planning (read-only) from execution.

#### When a plain LLM call is enough and when an agent is needed

A single call suffices for a one-off transformation: summarize, translate, rewrite, classify, draft a message. An agent is needed for multi-step work that requires reading the environment and checking intermediate results: implementing a feature, fixing a failing pipeline, refactoring across files, investigating a bug.

#### Risks of autonomous agents

- Irreversible actions: deleted files or branches, pushed code, cloud changes. In the course case study, an agent resized a cloud machine and raised costs from about USD 4 to 25 per day.
- Error accumulation over many steps, and confident "done" reports for incomplete work (a feature whose frontend buttons were missing).
- Cost and token runaway in long loops.
- Prompt injection from untrusted content (see [Security](#prompt-injection)).
- Scope creep: unrelated edits, weakened tests or scans to make a pipeline green.

#### Autonomy levels: human-in-the-loop vs autonomous

- **Human-in-the-loop:** the human approves each consequential action (Claude Code's default permission mode).
- **Human-on-the-loop:** the agent acts within pre-approved limits while the human monitors and can stop it (auto-accept edits, allowlisted commands).
- **Autonomous:** the agent runs unattended, which is acceptable only in a sandbox with scoped credentials and limits.
Choose by reversibility, blast radius, ability to verify the result automatically, data sensitivity, and how proven the workflow is. In Claude Code, Shift+Tab cycles default (asks before edits and commands), auto-accept (edits only), and Plan Mode (read-only). Bypassing permissions belongs only in isolated environments.

**Lessons:** [Welcome](../01%20Intro/01%20Welcome/01.%20Intro.%20AI%20Assisted%20Development.md) · [What is Claude Code](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/01%20What%20is%20Claude%20Code/01%20What%20is%20Claude%20Code.md) · [How Claude Code works](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/01%20What%20is%20Claude%20Code/02%20How%20Claude%20Code%20works.md) · [Structuring prompts](../02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29.md) · [AI-first case study](../06%20Applied%20Practices/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation.md)

### Tokens and the Context Window

#### Tokens and cost

A token is the model's unit of text—often part of a word (roughly four characters of English; other languages and code often need more tokens per word). Providers bill per token for **input** (everything sent: instructions, history, files, tool definitions and results) and **output** (the generated answer). In agent work, input volume is usually much larger, while output tokens cost more per token. Every request re-sends the context, so long sessions get more expensive per message.

#### The context window

The maximum number of tokens the model can see in one request: system prompt, project instructions, conversation history, files, tool definitions and results, and the answer itself. It is the model's short-term working memory, not a permanent database. Context occupancy, cumulative session tokens, rate limits, and the bill are different measurements.

#### Context fill level and answer quality

As the window fills, every request becomes more expensive and quality tends to drop: irrelevant or conflicting history distracts the model, and details in the middle are used less reliably. A practical guideline is to keep occupancy around **20–50%** of the window and compact or restart before it grows further. The course adds that no single threshold is universal—what matters is that the context is sufficient, relevant, and current—so watch absolute numbers, not only percentages (13% of 1M tokens is about 130K).

#### Lost in the middle

Research (Liu et al., 2023) showed that models often use information at the beginning and end of a long context more reliably than information in the middle; the effect varies by model and task. Mitigations: put critical requirements at the start or repeat them at the end, keep the context short and focused, load only relevant excerpts, structure inputs with clear sections, and persist decisions in files instead of burying them in long chats.

**Lessons:** [Context windows, caching, and price](../04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md) · [Context size and performance](../04%20Context%20Engineering/01%20General%20practices/04%20Context%20Window%20-%20Performance/04%20Context%20Window%20-%20Performance.md) · [Status line](../04%20Context%20Engineering/01%20General%20practices/02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline.md) · [Claude 101: context management](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/03%20Daily%20Workflows/02%20Context%20Management.md)

---

## 2. Prompt Engineering and Meta-Prompting

### Prompt Engineering

#### What prompt engineering is

Designing the input to a model so that it reliably produces the intended result: a clear task, the necessary input, constraints, and the expected output format. In everyday coding it matters less than it used to, because agents and enhancers structure prompts for you. It remains essential when you build AI products, custom agents, or harnesses—for example, keeping a customer-facing chatbot on topic and resistant to misuse.

#### Prompting techniques

- **Role prompting:** assign a role and perspective ("You are a security reviewer…").
- **Few-shot prompting:** show input/output examples of the desired behavior.
- **Chain-of-thought:** ask for step-by-step reasoning before the answer.
- **Structuring:** separate task, input, constraints, and output with sections or tags; specify the response format or schema.
- **Constraints and definition of done:** what is in and out of scope, what "finished" means, how to verify it.
- **Decomposition** into smaller, verifiable steps.
Formats: Markdown is familiar but blurs nested boundaries; YAML depends on indentation; JSON is precise but awkward to write by hand; XML gives explicit custom-tag boundaries with matching closing tags. The main risk of an unstructured prompt is that content is mistaken for instructions (the course's translation demo). Structure is not a defense against prompt injection.

#### Few-shot prompting

Few-shot prompting places a small set of input/output examples in the prompt so the model can infer a decision boundary, exact format, style, or abstention rule that is difficult to express in prose. It does not train or fine-tune the model. Start zero-shot and add examples only when they fix a measured ambiguity. Use a small, correct, diverse, consistently delimited set—for example an ordinary case, a boundary case, and a valid "no answer" case—and keep evaluation inputs separate to avoid leakage. Examples consume context, can teach accidental patterns or contradictions, and are not a prompt-injection defense. Retest them when the model or system prompt changes.

#### Chain-of-thought

The model reasons step by step before giving the answer. It helps on logic, math, and multi-step planning, and less on simple lookups or style edits. Reasoning models and "extended thinking" modes already do this internally, so explicitly asking for it adds less there; you control depth through effort or reasoning settings instead. The course covers reasoning levels and plan mode.

#### Decomposition

A small task needs less context and has an unambiguous definition of done, so the model makes fewer assumptions and its result is easier to verify. Split by **verifiable steps**, not by files: each step should produce something you can check (a passing test, a reviewed contract, a working endpoint). In the course, this is Explore → Plan → Code → Commit, Spec Kit's specify → plan → tasks, and Task Master's dependency-ordered task graph.

#### One big prompt vs a chain of small prompts

A chain gives control: you review and correct between steps, and each step has its own focused context. It is slower and costs more round trips. One prompt is fine for a small, tightly coupled task. For complex work, prefer a chain of verifiable steps with artifacts saved between them.

**Lessons:** [Structuring prompts](../02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29.md) · [Few-shot prompting](../07%20Additional%20Themes/01%20Few-Shot%20Prompting/01%20Few-Shot%20Prompting.md) · [Explore → Plan → Code → Commit](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/03%20Daily%20Workflows/01%20The%20Explore%20%E2%86%92%20Plan%20%E2%86%92%20Code%20%E2%86%92%20Commit%20Workflow.md) · [Task Master AI](../04%20Context%20Engineering/04%20Frameworks/02%20Task-Master%20AI/02%20Task-Master%20AI.md)

### Meta-Prompting

#### What meta-prompting is

Using one prompt to create or improve another. The meta task ("rewrite this request into a precise prompt; do not implement anything") is kept separate from the implementation task. The output is a prompt, not code.

#### Generating and improving prompts with AI

- Write a meta-prompt with separate parts: `<meta_task>`, `<draft_prompt>`, `<investigation>` (what the agent may read), `<output_requirements>`.
- Run it with an agent that can read the repository, so the prompt is grounded in the real language, files, conventions, and tests. A general chatbot only polishes wording—in the course it assumed TypeScript for a Go project.
- Ask for confirmed facts, assumptions, and open questions separately; review the result before executing it.
- Context engines such as Augment Code do this with retrieval and semantic search; NotebookLM does it from selected source documents; `ai-dev-tasks` does it by asking 3–5 clarifying questions before writing a PRD.
- An enhanced prompt is a proposal: code cannot reveal UX or product decisions that exist only in your head. State them explicitly.

#### The prompt critique / refinement loop

Generate a prompt → run it → ask the model to critique the result and the prompt against the goal → improve the prompt → repeat until the output meets the criteria. Keep the evaluation criteria fixed, and use a fresh session for each run so earlier failed context does not leak in.

#### Self-improving prompt workflows

Prompts get better systematically rather than by intuition; recurring failures are captured as rules; the improved prompt becomes a reusable asset—a skill, project instruction, or template shared with the team. Risks: overfitting to a few examples and drifting away from the real goal, so keep a small representative test set and human review. The Accelerator's `stabilize` and `reflect` steps are examples of turning corrections into reusable learning.

**Lessons:** [Augment Code enhancement](../02%20Meta-Prompting/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code.md) · [Tool-agnostic meta-prompting](../02%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting.md) · [NotebookLM](../02%20Meta-Prompting/04%20Meta-Prompting%20with%20NotebookLM/04%20Meta-Prompting%20with%20NotebookLM.md) · [First PRD with ai-dev-tasks](../02%20Meta-Prompting/05%20Creating%20your%20first%20Product%20Requirement%20Document/05%20Creating%20your%20first%20Product%20Requirement%20Document.md)

---

## 3. Context Engineering

#### Context engineering vs prompt engineering

Prompt engineering is about *what you say*. Context engineering is about *everything that ends up in the window* and when: system prompt, project instructions, conversation history, files and diffs, tool definitions, tool results, retrieved documentation, skills, and subagent summaries. The goal is a working set that is sufficient, relevant, current, structured, and authorized—not the largest or the smallest prompt.

#### Context sources in AI coding workflows

- System prompt and harness instructions.
- Memory files: `CLAUDE.md`, `AGENTS.md`, rules files.
- Code, diffs, and Git history.
- Tool output: tests, builds, linters, CLI commands.
- Tool definitions from MCP servers.
- Documentation: official docs, Context7, vendor CLIs, internal sources.
- Specifications and task artifacts: PRD, constitution, `spec.md`, `plan.md`, `tasks.md`.
- Skills (loaded on demand), subagent results, and codebase-index search results.

#### Deciding what context the agent needs

Start from the task and its definition of done: give the minimum a competent human would need to solve it—the relevant files, constraints, acceptance criteria, and how to verify. Let the agent retrieve more on demand (search, index, docs) instead of preloading "just in case". The course formalizes this as a **task contract**: objective, scope, evidence, constraints, done-when, decision boundaries.

#### Overstuffed context and what to exclude

Quality degrades (context distraction, lost in the middle, conflicting instructions) and cost grows with every request. Exclude generated or bulky material: lock files, build output, `dist/`, `node_modules/`, minified files, full logs (pass only the failing part, e.g. `gh run view --log-failed`), irrelevant modules, stale chat history, unused MCP servers, and secrets.

#### Reducing token usage without losing quality

- Pass excerpts and search results instead of whole files; bound tool output.
- Summarize and compact (`/compact`) when continuing the same objective; start a new session when the objective changes.
- Delegate noisy subtasks (log reading, research) to subagents that return short summaries, often on cheaper models.
- Keep MCP lean: enable only task-relevant servers, use deferred tool loading for large catalogs, or a CLI instead.
- Rely on prompt caching by keeping the stable prefix unchanged (cache writes cost more, cache reads are discounted); remember that cached tokens still occupy the window.
- Keep instruction files short and move procedures into skills.
- Input- and output-side compression tools such as RTK and Caveman (see [Models](#6-models-speed-cost-quality)).

#### Hierarchical context for large projects

Layer it from always-on to on-demand:
1. A short root `CLAUDE.md`/`AGENTS.md`: purpose, build and test commands, key conventions, boundaries.
2. Nested instruction files per package or module (loaded when the agent works there) and path-scoped rules (Claude Code `.claude/rules/` with `paths:` frontmatter).
3. Skills for procedures, loaded only when relevant.
4. Durable documentation and specifications referenced by link, with an index or manifest (the Accelerator's `Specs/manifest.md`) so the agent reads only what applies.
5. Retrieval for the rest: exact search, language servers, Git history, and a codebase index.

#### Context pipelines for coding agents

Treat context assembly as a pipeline: **instructions → task contract → retrieval** (search, index, docs) **→ selection and trimming → execution → capture** (write decisions and results to artifacts) **→ compaction or handoff** to the next session. Make steps deterministic where possible: scripts that collect only failing logs, hooks that inject context at session start, subagents that summarize, and files rather than chat as the handoff medium. Record sources and versions so results are traceable.

#### RAG vs passing context directly

Retrieval-Augmented Generation finds relevant fragments and inserts them into the model's context before generation. A complete pipeline ingests and parses sources, splits them into meaningful chunks, stores provenance and access metadata, retrieves candidates with keyword, vector, or hybrid search, reranks them, and asks the model to answer from the selected evidence with citations. Use RAG when the collection is larger than the window, changes often, contains private domain knowledge, or requires provenance; pass context directly when the relevant set is small and known.

Evaluate retrieval separately from generation: did the system find the necessary, current, relevant, and authorized evidence, and is the answer actually supported by it with accurate citations or an explicit abstention when evidence is missing? Apply authorization before a chunk reaches the model and treat retrieved text as untrusted content that may contain indirect prompt injection. In the course: Augment's context engine, Auggie's `codebase-retrieval` index, Context7 for library docs, and NotebookLM for source-grounded documents. Retrieved results are leads to verify in the current source.

**Lessons:** [Consolidated context-engineering article](../04%20Context%20Engineering/01%20General%20practices/09%20All%20of%20above%20lessons%20as%20a%20text%20article/09%20All%20of%20above%20lessons%20as%20a%20text%20article.md) · [RAG](../07%20Additional%20Themes/02%20Retrieval-Augmented%20Generation/02%20Retrieval-Augmented%20Generation.md) · [One task, one chat](../04%20Context%20Engineering/01%20General%20practices/05%20Dividing%20tasks%20by%20sessions/05%20Dividing%20tasks%20by%20sessions.md) · [MCP overhead](../04%20Context%20Engineering/01%20General%20practices/06%20Reducing%20the%20number%20of%20MCP%20servers/06%20Reducing%20the%20number%20of%20MCP%20servers.md) · [Up-to-date documentation](../04%20Context%20Engineering/01%20General%20practices/07%20Providing%20AI%20with%20up-to-date%20knowledge/07%20Providing%20AI%20with%20up-to-date%20knowledge.md) · [Codebase indexing](../04%20Context%20Engineering/01%20General%20practices/08%20Intro%20to%20codebase%20indexing/08%20Intro%20to%20codebase%20indexing.md)

---

## 4. Memory Files (Project Rules)

#### Purpose of CLAUDE.md, AGENTS.md, and Cursor rules

They hold persistent project rules that the tool loads automatically into every session, so you don't re-explain the project each time: stack, build and test commands, conventions, architecture boundaries, things the agent must not touch. `CLAUDE.md` is Claude Code's file, `AGENTS.md` is the cross-tool convention (Codex and others; Claude Code can read it too), Cursor uses `.cursor/rules/`. Generate a draft with `/init`, then review every command and claim. Memory files are context, not enforcement—use hooks or permissions for rules that must never be broken.

#### What belongs in memory files and what does not

- **Yes:** build, test, and lint commands; coding conventions that differ from defaults; project layout and architecture boundaries; forbidden areas and actions; known pitfalls; links to deeper docs.
- **No:** anything the agent can see from the code (directory trees, dependency lists), one-off task details, secrets, generated repository maps, rules already enforced by linters or CI, long procedures (make them skills).
- Add a rule when the agent makes the same mistake twice or a reviewer catches something it should have known.

#### Why long instruction files hurt

They are paid for in every session and every request, they dilute attention so the model follows individual instructions less reliably, and they accumulate contradictions and stale rules. Claude Code's guidance is to target under about 200 lines per file; Codex limits project instructions to 32 KiB by default.

#### Memory files for a large codebase

- A concise root file plus nested files per service or package; files closer to the working directory are read last (Claude Code concatenates them; Codex lets the closer file win and supports `AGENTS.override.md`).
- Path-scoped rules (`.claude/rules/*.md` with `paths:`) that load only when matching files are touched.
- Skills for procedures; imports (`@docs/...`) for organization (imports still load at start, so they don't save context).
- Personal settings in `CLAUDE.local.md` or user-level files, never committed.
- One canonical source for multiple tools (for example `CLAUDE.md` that imports `@AGENTS.md`), with a test that a new session actually loads what you expect.
- Periodic audits for contradictions; in monorepos, exclude other teams' files (`claudeMdExcludes`).

**Lessons:** [Generating project instructions](../04%20Context%20Engineering/01%20General%20practices/01%20Generating%20the%20agent%20instructions/01%20Generating%20the%20agent%20instructions.md) · [Claude 101: the CLAUDE.md file](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/04%20Customizing%20Claude%20Code/01%20The%20CLAUDE.md%20File.md)

---

## 5. Session Degradation

#### Signs of a degrading session

The agent goes in circles, reintroduces bugs it already fixed, forgets agreed decisions or constraints, contradicts earlier answers, ignores project instructions, re-reads the same files, gives vaguer answers, or the context indicator shows high occupancy. Two causes have names: **context clash** (earlier instructions or goals conflict with the current task) and **context distraction** (irrelevant history dilutes attention).

#### When to start a new session

When the objective changes, when degradation signs appear, or when a stage is complete (spec approved, plan accepted, feature merged). Before switching, write the outcome to a file—spec, plan, task list, or handoff note—so nothing is lost. Start the new session with a short task contract. Rule of thumb from the course: one task, one chat; work that shares one definition of done can stay together.

#### Context compaction and long-running work

Compaction replaces the conversation history with a summary to free space (`/compact` in Claude Code and Codex; Claude Code also auto-compacts near the limit). Details can be lost, so:
- compact only when continuing the **same** objective, and check the summary;
- keep durable state in files (specs, `tasks.md`, handoff notes), not only in chat;
- use `/clear` or a new session when the objective changes, and fork to compare alternative approaches;
- for very long work, use a tracker such as Spec Kit artifacts, Task Master, or the Accelerator's `STATE.md` as the resume point.
Project-root `CLAUDE.md` is re-read after compaction; instructions given only in chat are not.

**Lessons:** [One task, one chat](../04%20Context%20Engineering/01%20General%20practices/05%20Dividing%20tasks%20by%20sessions/05%20Dividing%20tasks%20by%20sessions.md) · [Status line](../04%20Context%20Engineering/01%20General%20practices/02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline.md) · [Spec Kit overview](../03%20Spec-Driven%20Development/01%20GitHub%20SpecKit%20Brief%20Overview/01%20GitHub%20SpecKit%20Brief%20Overview.md)

---

## 6. Models: Speed, Cost, Quality

#### Fast models vs reasoning models

Reasoning models "think" before answering (internal chains of thought, adjustable effort), which makes them better at complex, multi-step, ambiguous problems—architecture, debugging, review—but slower and more expensive. Fast models (for example Haiku-class) answer quickly and cheaply and are good at well-defined, mechanical tasks.

#### Choosing a model per task

- **Cheap/fast:** reading and summarizing logs, searching and inventorying files, boilerplate, formatting, simple edits, data extraction.
- **Mid-tier (Sonnet-class):** everyday implementation against a clear plan.
- **Strong reasoning (Opus/Fable-class, high effort):** architecture and planning, ambiguous debugging, security and code review, orchestration of other agents.
In the self-healing CI/CD lesson: Haiku read logs, Sonnet fixed code, Opus orchestrated and reviewed. Judge by cost per **completed** task, not per token.

#### When an expensive reasoning model is not justified

Mechanical or repetitive work, simple lookups, formatting and renaming, high-volume batch processing, latency-sensitive interactions, and tasks with a deterministic tool that does the job better (a formatter, a codemod, a linter).

#### Routing between models

Model routing chooses a model per request, workflow step, or agent role. First filter the pool by non-negotiable constraints: data handling and region, required modality and tools, context size, availability, and a task-specific quality floor. Then choose through explicit task mapping, deterministic rules, a learned classifier, a cascade that escalates after a verifiable failure, or an approved fallback. Do not use model self-confidence as the only escalation signal.

Log the actual model, routing reason, fallback path, latency, and cost. Compare the router with single-model and simple rule-based baselines on representative work, measuring completed-task success, schema and tool-call validity, retries, and human correction—not token price alone. Multi-turn workflows may also need model affinity for behavioral continuity and prompt-cache reuse. Examples from the tools include Claude Code's `/model` selector and per-subagent `model` configuration, Task Master's main/research/fallback roles, and multi-model gateways.

#### Orchestration vs one powerful model

Decomposition gives each worker a small, focused context; independent parts run in parallel; cheap models handle bulk work while strong models handle judgment; an independent reviewer with a fresh context catches mistakes the implementer is biased toward. The trade-offs: coordination overhead, more tokens in total (each agent team member is a separate session), and integration risk—use it only when the work truly splits.

#### Optimizing team cost

- Clean, focused sessions; compact or restart instead of endless chats.
- Lean context: short memory files, skills instead of long rules, minimal MCP, bounded tool output.
- Stable prompt prefixes for caching.
- Model routing by task; subagents on cheaper models for noisy work.
- Specs and plans up front to reduce rework (in the case study, rework cost as much as new features).
- Dedicated accounts sized to the workload; usage dashboards, limits, and budgets; cost per task as the metric.
- Shared skills and workflows so the team doesn't rediscover the same solutions.

#### RTK and Caveman

- **[RTK](https://github.com/rtk-ai/rtk) (Rust Token Killer)** is a CLI proxy that filters supported shell-command output before it reaches the agent. It targets **input** tokens from tools such as `git`, search, test runners, and linters; current integrations can rewrite eligible calls through agent-specific hooks.
- **[Caveman](https://github.com/JuliusBrussee/caveman)** provides a terse response skill for reducing agent prose and broader proxy/runtime components for compressing material the agent reads. The component in use determines whether it targets output, input, or both.
- Both are third-party tools. Compression can hide diagnostic detail, and project-reported percentages are not guaranteed end-to-end session savings. Keep raw output recoverable; inspect hooks, proxy boundaries, storage, telemetry, and uninstall behavior; and evaluate provider-reported usage, correctness, reruns, and review time on paired representative tasks.

**Lessons:** [Model routing](../07%20Additional%20Themes/03%20Model%20Routing/03%20Model%20Routing.md) · [RTK and Caveman](../07%20Additional%20Themes/05%20RTK%20and%20Caveman/05%20RTK%20and%20Caveman.md) · [Caching and price](../04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md) · [Agent Teams](../04%20Context%20Engineering/03%20Sub-Agents/02%20Claude%20Code%20Agent%20Teams/02%20Claude%20Code%20Agent%20Teams.md) · [Self-healing CI/CD](../06%20Applied%20Practices/04%20Self-healing%20CI-CD%20with%20Claude%20Agents%20Teams/04%20Self-healing%20CI-CD%20with%20Claude%20Agents%20Teams.md) · [Open-weight models](../05%20Advanced%20Techniques/03%20Using%20local%20LLM%20without%20powerful%20hardware/03%20Using%20local%20LLM%20without%20powerful%20hardware.md) · [Toolset](../01%20Intro/03%20Our%20Toolset%20as%20for%20Now/03%20Our%20Toolset%20as%20for%20Now.md)

---

## 7. Specification-Driven Development (SDD)

#### What specification-driven development is

An approach in which a specification is written and approved first and becomes the source of truth; implementation follows it and is verified against it. The spec is a contract between the human and the AI: it states what to build and why, how success is measured, and what is out of scope. In the course, GitHub Spec Kit implements it.

#### SDD vs implementation-first

Implementation-first starts coding from an idea and discovers requirements along the way; decisions live in people's heads and chat history. SDD front-loads clarification: the constitution (project rules), specification (what and why), plan (how), and tasks are durable files. Changes go through the artifacts first and then the code, and finished work is checked against the spec rather than against memory.

#### Why AI-assisted coding fits SDD

The spec is ready-made, durable context: a new session can re-read it instead of relying on chat history. It reduces hallucinated requirements and assumptions, gives an objective acceptance criterion for the AI's output, and allows context resets between stages. The AI-first case study shows the reverse: without fixed, AI-oriented specs, changes created "instant legacy" and repeated rework.

#### Sections of a good implementation spec

Goal and users; scope and **out of scope**; user stories or flows with acceptance criteria; functional requirements; non-functional constraints (performance, security, accessibility); edge cases and failure behavior; measurable success criteria; dependencies and integrations described precisely; assumptions and open questions. Spec Kit's `spec.md` is technology-agnostic; `plan.md` adds the technical design (stack, data model, contracts, research).

#### Problems of large-scale spec generation

- Hallucinated requirements: in the case study, a four-page brief became an 82-page AI spec with about 30% invented content.
- Context loss across a long document, so the end contradicts the beginning.
- Over-complication, and "hidden stories" nobody approved.
- Forward references between epics ("do this when epic 6 is ready") that the AI simply skips.
- Stale specs after changes, and the cost of regenerating everything.
Mitigations: trace every requirement to a client source or mark it as an assumption; split specs into small files (foundation, epics, discussions, project plan); review in small units; record changes as atomic descriptions or new epics; keep one authoritative artifact per decision.

**Spec Kit essentials**
- **Order:** constitution (once per project) → specify → clarify\* → plan → checklist\* → tasks → analyze\* → implement → converge (\* optional).
- **Setup:** `uv tool install specify-cli`, then `specify init --here --integration <agent>`. `specify` is the terminal CLI; stages run inside the agent chat as `/speckit.plan` (canonical), `/speckit-plan` (Claude Code skills), or `$speckit-plan` (Codex).
- **Artifacts:** `.specify/memory/constitution.md`; `specs/NNN-feature/` containing `spec.md`, `checklists/requirements.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, and `tasks.md`.
- **Rules:** fix a problem in the artifact that owns the decision and regenerate downstream artifacts. Analyze is read-only; converge appends missing tasks. Mark `[X]` only after verification. Each new capability is a new `specs/00N-…` cycle.

**Lessons:** [Spec-Driven Development module](../03%20Spec-Driven%20Development/01%20GitHub%20SpecKit%20Brief%20Overview/01%20GitHub%20SpecKit%20Brief%20Overview.md) · [Specify](../03%20Spec-Driven%20Development/06%20SpecKit%20Specify/06%20SpecKit%20Specify.md) · [Post-MVP](../03%20Spec-Driven%20Development/11%20SpecKit%20-%20Post-MVP/11%20SpecKit%20-%20Post-MVP.md) · [AI-first case study](../06%20Applied%20Practices/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation.md) · [First PRD](../02%20Meta-Prompting/05%20Creating%20your%20first%20Product%20Requirement%20Document/05%20Creating%20your%20first%20Product%20Requirement%20Document.md)

---

## 8. AI-Assisted Tools (IDE and Terminal)

### Claude Code Agent Skills

#### What a skill is

A folder containing `SKILL.md`: YAML frontmatter with `name` (lowercase, hyphens) and `description`, plus Markdown instructions. Next to it can live `references/` (documents loaded when needed), `scripts/` (executed without their source entering context), and `assets/`. Optional frontmatter includes `allowed-tools` (pre-approves tools while the skill is active; it does not restrict other tools) and `model`. Locations: `~/.claude/skills/` (personal) and `.claude/skills/` (project); for same-name skills the priority is enterprise > personal > project > plugin.

#### How a skill enters the context

**Progressive disclosure:** only each skill's name and description sit in context permanently. The body of `SKILL.md` is loaded when the model decides the description matches the task, or when the user invokes it explicitly with `/skill-name`. Reference files load only when the instructions point to them. That is why the description must say what the skill does **and when to use it**. Frontmatter can restrict invocation: `disable-model-invocation: true` (only the user can call it) or `user-invocable: false` (only the model).

#### Skills vs slash commands vs prompts

A slash command is an explicit shortcut that a human calls by name. A skill is a capability the agent can load on its own based on the description, with supporting files, and it can also be called by name. An ordinary prompt is one-off and reuses nothing. In current Claude Code, custom commands have been merged into skills: `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`.

#### Tasks that suit skills

Repeatable procedures with stable steps: a release checklist, creating a module from a template, a code-review checklist, generating a report in a fixed format, a deployment runbook. Not suitable: one-off tasks (use a prompt), always-on rules (memory files), guaranteed execution (hooks), isolated context (subagents), external data and tools (MCP).

#### Reusable engineering workflows with skills

One skill per job, with a precise trigger description and clear inputs and outputs. Keep `SKILL.md` short (under about 500 lines) and move detail into references and deterministic scripts. Chain skills into a workflow with explicit human gates and artifacts as handoff—this is how the Accelerator works (command → agent → skill → artifact). Version skills in Git, test them on representative tasks, and update them when the real process changes. Turn a workflow into a skill only after it has worked manually several times.

#### Standardizing team development with skills

The whole team runs the same procedure and output format; onboarding is faster; corrections are fixed once in the shared skill. Distribute through the repository, a plugin or marketplace, or enterprise-managed settings, and review third-party skills like code.

**Lessons:** [Introduction to Agent Skills](../04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills.md) · [Innowise Accelerator](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md)

### Custom Slash Commands (deprecated—merged into skills)

#### What custom slash commands are

Markdown prompt files in `.claude/commands/` (project) or `~/.claude/commands/` (personal), invoked explicitly as `/name`; arguments arrive through `$ARGUMENTS` (or `$1`, `$2`). Existing command files still work, but new work should use skills, which add supporting files, invocation control, and automatic loading.

#### Slash commands in a team workflow

Commit them to the repository so everyone has the same `/review`, `/release`, or `/commit-push-pr`; give them clear names and documented arguments; combine them with hooks for mandatory checks; and migrate them to skills when they need supporting files or automatic invocation.

### Claude Code Hooks

#### Hooks and their types

Deterministic handlers that run on lifecycle events—most often shell commands, though HTTP, prompt, and agent hook types also exist. Main events: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `PreCompact`, `Notification`, plus newer ones such as `PermissionRequest`, `SessionEnd`, and team events. A matcher selects the tools (for example `Edit|Write`). Hooks are configured in `settings.json` or via `/hooks`; project hooks go in `.claude/settings.json` and are committed.

#### Hooks vs agent instructions

A hook runs **every time** the event occurs; an instruction in `CLAUDE.md` or a skill is context that the model may ignore. A hook can block an action: in `PreToolUse`, exit code 2 blocks the call and sends stderr back to Claude, while exit 0 with JSON can return `permissionDecision: allow | deny | ask` or modified input. Rule: if something must happen every time, make it a hook, not a prompt.

#### Pre-tool hooks

Blocking dangerous commands (`rm -rf`, force pushes, `terraform apply`), protecting files and paths (`.env`, secrets, migrations), validating or rewriting commands (RTK rewrites `git status` into `rtk git status`), enforcing branch rules, and requiring approval for specific tools.

#### Post-tool hooks

Auto-formatting and linting after edits, running affected tests or type checks, logging and auditing tool calls, scanning written files for secrets, and feeding results back to the agent so it fixes problems immediately.

#### Enforcing security policies with hooks

They form a deterministic layer outside the model: deny secret reads and destructive commands, restrict network or cloud commands, scan for secrets and vulnerable dependencies, block edits outside allowed paths, and log everything. Combine them with permission rules, sandboxing, and managed settings. Hooks themselves run with the user's privileges, so review project hooks before trusting a repository and treat them as executable code.

#### Automating code-review checks with hooks

Run linters, formatters, tests, type checks, and SAST after every edit or at `Stop`, and return failures to the agent so it fixes them before handing over. In agent teams, `TaskCompleted` and `TeammateIdle` hooks can enforce quality gates before work is accepted.

**Lessons:** [Claude 101: hooks](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/04%20Customizing%20Claude%20Code/05%20Hooks.md) · [Skills vs other Claude Code features](../04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/Introduction%20to%20agent%20skills/04%20Skills%20vs.%20other%20Claude%20Code%20features/04%20Skills%20vs.%20other%20Claude%20Code%20features.md) · [Innowise Accelerator: security boundary](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md)

### Shell Scripts and Workflow Automation

#### Shell scripts in agent orchestration

- Deterministic steps such as build, test, lint, collecting only the failing logs, or setting up environments belong in scripts, not in prompts.
- Agents run headless from scripts and CI (`claude -p "…"`, `codex exec`), so the same workflow runs in pipelines.
- Scripts loop over files or tasks and run work in parallel worktrees.
- Skills bundle scripts whose output, not source, enters the context.
- CLIs (`gh`, `gcloud`, `glab`) let the agent act through inspectable commands instead of a heavy MCP catalog, as in the self-healing CI/CD and Lovable deployment lessons.

### Subagents

#### Tasks that suit subagents

Independent subtasks without shared mutable state, where only the result matters to the main conversation: review from different angles, research and codebase exploration, reading long logs, migrating files independently, test runs whose details you don't need. Avoid them for sequential, tightly dependent steps (reproduce → diagnose → fix), and for work whose intermediate output you need while debugging.

#### Lead agent and worker agents

The lead decomposes the task, gives each worker a focused prompt with the necessary context, and aggregates the results. Workers run in isolated contexts with their own tools and models and return concise structured results. In Claude Code, subagents are Markdown files in `.claude/agents/` with `name`, `description` (triggers and required inputs), `tools`, and `model`; the body is the system prompt. Give them least-privilege tools, a structured output that acts as the stopping condition, and an "Obstacles Encountered" section. **Agent teams** (experimental) add direct messaging and a shared task list between independent Claude Code sessions.

#### Risks of concurrent agent execution

File conflicts and overwrites, race conditions on shared resources (databases, ports, branches), duplicated work, inconsistent assumptions between workers, multiplied token cost, rate limits, and harder debugging. Mitigate with clear file ownership, worktrees or branches per worker, an approved interface contract before parallel frontend and backend work, small teams (3–5), and an integration step owned by a person or the lead.

#### Shared mutable context

When several agents read and write the same files, notes, or state, one agent's changes invalidate another's assumptions, updates get lost, and nobody knows which version is authoritative. Prefer isolated contexts that exchange immutable artifacts (specs, contracts, reports), append-only handoff files with one owner per section, and one authoritative task list with locking (agent teams use file locking for task claims).

#### Synchronizing results from several agents

Through artifacts and contracts, not chat: workers return structured results, the lead reconciles duplicates and conflicts, the branches are merged, and the full test suite and review run on the integrated result. Use dependencies in the task list so that dependent work starts only when its inputs are done. In the Accelerator, agents coordinate through approved artifacts and the developer reconciles; in agent teams, the lead waits for all teammates and synthesizes.

**Lessons:** [Introduction to Subagents](../04%20Context%20Engineering/03%20Sub-Agents/01%20External%20Course%20Introduction%20to%20subagents/01%20External%20Course%20Introduction%20to%20subagents.md) · [Claude Code Agent Teams](../04%20Context%20Engineering/03%20Sub-Agents/02%20Claude%20Code%20Agent%20Teams/02%20Claude%20Code%20Agent%20Teams.md) · [Spec Kit Tasks](../03%20Spec-Driven%20Development/09%20SpecKit%20Tasks/09%20SpecKit%20Tasks.md)

---

## 9. Model Context Protocol (MCP)

#### What MCP is

An open protocol for connecting AI clients to external tools and data. An MCP server exposes tools (and resources and prompts) with descriptions and schemas; any compatible client—Claude Code, Codex, Cursor, and others—can use it. Typical servers: GitHub, Playwright, Context7, Figma, Supabase. In Claude Code: `claude mcp add` (HTTP or stdio), scopes local, user, or project (`.mcp.json`, committed), and `/mcp` to manage them.

#### MCP vs an ordinary API integration

With an API you write custom glue code per tool and per client. An MCP server describes its own tools, and the model calls them directly through the client without custom code, so one server works with many clients. The important downside: the descriptions and schemas of all enabled servers occupy context and cost tokens even when unused (unless the client loads them on demand), and every result adds more. Keep only task-relevant servers enabled; for stable direct operations a CLI is often lighter.

#### Benefits for the AI tooling ecosystem

Standardization (write a server once, use it in any client), discoverability with typed inputs, live access to current data and documentation, shared remote integrations for a team, and a clear place to apply authentication and permissions.

#### MCP security risks

An unverified server means running someone else's code with your privileges and credentials; agents trust what a connected server exposes; tool outputs and descriptions are a channel for **indirect prompt injection**; over-broad tokens enable data exfiltration; a server can change after you approved it. Use official or internally reviewed servers, an organizational allowlist, least-privilege tokens, and pinned versions; build a custom server rather than use an unknown repository; and treat all server output as untrusted data.

**Lessons:** [Using MCP servers](../01%20Intro/04%20Using%20MCP%20Servers/04%20Using%20MCP%20Servers.md) · [Claude 101: MCP](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/04%20Customizing%20Claude%20Code/04%20MCP.md) · [Reducing MCP overhead](../04%20Context%20Engineering/01%20General%20practices/06%20Reducing%20the%20number%20of%20MCP%20servers/06%20Reducing%20the%20number%20of%20MCP%20servers.md)

---

## 10. Security and Privacy

### Secrets and PII

#### Data that must not be sent to an LLM

Secrets, credentials, keys, and tokens; personal data (PII) without a lawful basis and approval; data under NDA or contractual restrictions; proprietary or client code without company or client permission; production data and regulated data (health, financial). A local harness does not mean local inference—with hosted models, selected code and prompts leave the machine. Classify data and check provider retention and processing terms first.

#### Working with secrets

- Keep values in environment variables and secret managers, never in prompts, instruction files, task lists, logs, screenshots, or frontend bundles (anything in a Vite `VITE_*` variable is public).
- Deny the agent access to `.env` and key files through permission deny rules and hooks; keep them in `.gitignore`.
- Use scoped, short-lived tokens for the agent and separate keys per project.
- Rotate any key that leaks immediately.

### AI-Generated Code Risks

#### Security risks of AI-generated code

Classic vulnerabilities (injection, missing input validation, broken authorization, insecure deserialization), hardcoded secrets, outdated or insecure practices learned from training data, insecure defaults (open CORS, disabled TLS checks), overly broad permissions in infrastructure code, and tests that confirm the wrong behavior because they were generated from the same flawed spec.

#### Insecure dependencies

It may recommend packages that don't exist (attackers register these names—"slopsquatting"), names similar to popular ones (typosquatting), or outdated versions with known vulnerabilities, because its knowledge is historical. Verify every new dependency: that it exists, who maintains it, its version and license, and its advisories; pin versions and run dependency scanners.

#### Checking AI-generated code before merge

Exactly like code from an unknown colleague: read the diff, run the tests and add missing ones, run linters, type checks, SAST, secret scanning, and dependency scanning, and get a human review—optionally first a fresh-context reviewer subagent. Check that no tests or scans were weakened to make CI green. Responsibility for the merged code stays with the developer.

### Prompt Injection

#### Prompt injection

Input that hijacks the model's behavior—making it ignore its original instructions and follow the attacker's ("ignore previous instructions and…"). It exploits the fact that instructions and data share the same context.

#### Indirect prompt injection

The malicious instruction comes not from the user but from data the agent processes: a README, code comment, issue text, web page, document, tool output, or MCP server response. For coding agents this is the main risk, because they read untrusted content and can act.

#### Defenses against prompt injection

There is no complete fix; defense is layered:
- Least privilege: scoped tokens, read-only roles, no secrets in reach of an agent that reads untrusted content.
- Apply authorization before RAG or tool content reaches the model; separate tenants and sensitive sources.
- Mediate tool calls outside the model: validate operation, target, arguments, paths, network destination, and alignment with the original user intent.
- Human approval for consequential actions; permission deny rules and `PreToolUse` hooks for dangerous commands.
- Sandboxing and network egress limits to prevent exfiltration.
- Separate untrusted content into clearly marked data sections and tell the model it is data—helpful but not sufficient.
- Avoid combining untrusted input, access to private data, and an outbound channel in one agent.
- Parse risky content in an isolated component with no secrets, action tools, or outbound channel, then pass only a narrow validated result onward.
- Allowlisted, reviewed MCP servers and skills; treat tool output as untrusted.
- Validate model output before execution or publication; review diffs and logs and monitor for unexpected actions.
See the dedicated defense lesson and the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/).

**Lessons:** [Prompt injection defenses](../07%20Additional%20Themes/04%20Prompt%20Injection%20Defenses/04%20Prompt%20Injection%20Defenses.md) · [Structuring prompts](../02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29.md) · [Using MCP servers](../01%20Intro/04%20Using%20MCP%20Servers/04%20Using%20MCP%20Servers.md) · [Innowise Accelerator: security](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md) · [Lovable deployment](../06%20Applied%20Practices/03%20Deploying%20Lovable%20project%20in%20Google%20Cloud%20with%20help%20of%20AI%20CLI/03%20Deploying%20Lovable%20project%20in%20Google%20Cloud%20with%20help%20of%20AI%20CLI.md) · [Self-healing CI/CD](../06%20Applied%20Practices/04%20Self-healing%20CI-CD%20with%20Claude%20Agents%20Teams/04%20Self-healing%20CI-CD%20with%20Claude%20Agents%20Teams.md) · [Open-weight models: privacy](../05%20Advanced%20Techniques/03%20Using%20local%20LLM%20without%20powerful%20hardware/03%20Using%20local%20LLM%20without%20powerful%20hardware.md)

---

## 11. Monitoring, Debugging, and Cost Control

#### Tracking cost

Use the tool's usage views and provider dashboards (`/status`, `/context`, the status line, `/cost` or usage reports, admin consoles), set spending limits and budget alerts, and measure **cost per completed task** rather than per token. Note that a cost estimate shown on a subscription plan may be an API list-price estimate, not a charge. For infrastructure that agents touch, use cloud budgets and daily checks (the case study's agent raised a cloud bill sixfold).

#### Signs of inefficient orchestration

More tokens without better results; agents duplicating work or waiting on each other; the lead doing the work itself instead of delegating; frequent conflicts and re-merges; workers stopping early or looping; teams used for sequential or tiny tasks; idle time due to exhausted usage limits; integration taking longer than the parallel work saved.

#### Debugging failing AI workflows

- Read the transcript or step logs.
- Check what context actually reached the failing step: which instructions and files loaded (`/context`, `/memory`), which tools were available, and what the tool returned.
- Reproduce the failing step in isolation with the same inputs, in a fresh session.
- Check skill or subagent descriptions for trigger problems, hooks for blocking, and permissions.
- Fix the root cause in the artifact, instruction, or tool that owns it, then rerun.
- Run `claude --debug` for skills and configuration issues.

**Lessons:** [Status line](../04%20Context%20Engineering/01%20General%20practices/02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline.md) · [Caching and price](../04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md) · [Troubleshooting skills](../04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/Introduction%20to%20agent%20skills/06%20Troubleshooting%20skills/06%20Troubleshooting%20skills.md) · [AI-first case study](../06%20Applied%20Practices/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation.md)

---

## 12. Tool Selection and Standardization

#### Choosing AI tools for a team

Compare candidates on the team's real, representative tasks: output quality, cost and usage limits, supported models, security and data-handling terms, enterprise controls (SSO, managed settings, audit), integration with the IDE, terminal, and CI, extensibility (skills, hooks, MCP, subagents), and portability between tools. Prefer official or internally approved tools and pilot them before rolling out. The course's current toolset is Claude Code, Codex, and Antigravity; choose by quality, cost, limits, and workflow, and re-evaluate regularly because the landscape changes every few months.

#### Standardizing AI workflows

Without standards, every developer reinvents prompts and setups, quality varies, security gaps appear, and knowledge is not shared. To standardize:
- Commit shared configuration: memory files, skills, subagents, hooks, and project settings.
- Agree on a common workflow (for example Explore → Plan → Code → Commit or Spec Kit) and a framework such as the Accelerator where it fits.
- Maintain an allowlist of tools and MCP servers, and enforce policies through managed settings.
- Pilot on a bounded project, measure outcomes, and capture corrections into shared skills.
- Train the team and review shared configuration like code.

**Lessons:** [Toolset](../01%20Intro/03%20Our%20Toolset%20as%20for%20Now/03%20Our%20Toolset%20as%20for%20Now.md) · [Introduction to frameworks](../04%20Context%20Engineering/04%20Frameworks/01%20Introduction%20to%20Frameworks/01%20Introduction%20to%20Frameworks.md) · [Sharing skills](../04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/Introduction%20to%20agent%20skills/05%20Sharing%20skills/05%20Sharing%20skills.md) · [Innowise Accelerator](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md)

---

## 13. Innowise Accelerator

The Innowise Accelerator is a stack-aware framework for coding agents. It packages engineering practice into commands, isolated agents, reusable skills, hooks, settings, and persistent artifacts, so that AI-assisted work is done in small, reviewable steps instead of one long chat. Its value is controlled, traceable work—not full autonomy.

#### Architecture and Principles

- **Command → Agent → Skill → Artifact + handoff → human chooses the next step.** A command is the entry point, an agent runs the work in an isolated context with its own tools, a skill holds the method and output contract, and the artifact persists the result.
- Each step stops after its own responsibility and recommends the next one—every transition is a human gate.
- Handoffs are explicit: what was done, which files changed, assumptions, verification, next step.
- Specifications are living artifacts indexed by a manifest, so later agents load only what is relevant; generated files carry provenance (which skill produced them).
- Skill text is guidance, not a security boundary: restrictions are enforced with permissions, sandboxing, and `PreToolUse` hooks, and shared settings are reviewed like code.

#### Phases and Typical Flows

- **Phases:** Understanding (requirements, clarification) → Planning (architecture, API and frontend design, implementation plan) → Development (worktree, implementation, review, tests, debugging) → Finalization (documentation, verification, branch completion).
- **Feature flow:** onboarding → requirements analysis → clarification → plan → *human gate* → implementation → tests → self-review → code review → verification → handoff.
- **Bug flow:** reproduction and evidence → systematic diagnosis → minimal fix → targeted tests → review → verification; a failing check returns to diagnosis.
- Parallel frontend and backend agents need an approved API contract and little file overlap; they coordinate through artifacts, and the developer integrates.

#### The `embacc` C++/Embedded Port

A related but separate product from the Node/NestJS workshop version. It runs on Claude Code, Codex, OpenCode, and Pi, and keeps its state outside the repository in `~/.embacc` (`PROJECT.md`, task `STATE.md` as the resume point).
- **Commands:** `embacc setup .`, `embacc run <host> .`, `embacc doctor .`, `embacc refresh .`, `embacc reflect .`, `embacc install … --dry-run` (opt-in shared configuration in the repository).
- **Skills:** onboarding and routing (`project-onboard`, `feature`, `bug`); continuity (`task-workspace`, `handoff`); requirements and planning (`requirements-analyst`, `requirements-clarifier`, `writing-plans`); implementation (`coder`, `testing`, `systematic-debugger`); review and verification (`self-review`, `code-reviewer`, `verify`); pull requests (`review-pr`, `pr-review-response`); learning (`stabilize`).

#### Adopting It

Start with a bounded pilot on a real task, in a branch or worktree. Track the number of tasks completed, time per task compared with your usual approach, tokens or cost from the usage dashboard, retries, review effort, and the problems you hit (wrong skill selection, context loss, permission prompts, stack mismatches, setup). It fits greenfield work best; brownfield projects need discovery and a test baseline first.

**Lessons:** [Workshop: Innowise Accelerator](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md) · [Introduction to frameworks](../04%20Context%20Engineering/04%20Frameworks/01%20Introduction%20to%20Frameworks/01%20Introduction%20to%20Frameworks.md)

---

## 14. Ten Principles of the Course

1. **AI is a multiplier, not a replacement.** It accelerates people who can judge its output.
2. **Intent must be explicit.** Anything you leave unspecified, the model will decide.
3. **Decisions live in files, not in chat.**
4. **One task, one chat.** Compact to continue, start fresh when the objective changes.
5. **Context should be sufficient and relevant, not maximal.**
6. **Ground changing facts in current sources.** Model knowledge is historical.
7. **Use the lightest mechanism that works.** Plain agent → subagent → agent team; CLI before a large MCP catalog.
8. **Prompts and skills are not security boundaries.** Enforce with permissions, hooks, sandboxes, and IaC.
9. **"Done" means verified.** An agent's success report is a claim, not evidence.
10. **Measure completed-task outcomes,** not token price, demo speed, or lines of code.

---

## 15. Course Map

| Module | Lessons |
| --- | --- |
| 01 Introduction | [Welcome](../01%20Intro/01%20Welcome/01.%20Intro.%20AI%20Assisted%20Development.md) · [Claude Code 101](../01%20Intro/02%20External%20Course%20Claude%20101/02.%20External%20Course%20Claude%20101.md) · [Toolset](../01%20Intro/03%20Our%20Toolset%20as%20for%20Now/03%20Our%20Toolset%20as%20for%20Now.md) · [MCP servers](../01%20Intro/04%20Using%20MCP%20Servers/04%20Using%20MCP%20Servers.md) · [Quiz](../01%20Intro/05%20Intro%20Quiz/05%20Intro%20Quiz.md) |
| 02 Meta-Prompting | [Structuring prompts](../02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29.md) · [Augment Code](../02%20Meta-Prompting/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code.md) · [Tool-agnostic](../02%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting.md) · [NotebookLM](../02%20Meta-Prompting/04%20Meta-Prompting%20with%20NotebookLM/04%20Meta-Prompting%20with%20NotebookLM.md) · [First PRD](../02%20Meta-Prompting/05%20Creating%20your%20first%20Product%20Requirement%20Document/05%20Creating%20your%20first%20Product%20Requirement%20Document.md) · [Quiz](../02%20Meta-Prompting/06%20Structured%20Prompts%20Quiz/06%20Structured%20Prompts%20Quiz.md) |
| 03 Spec-Driven Development | [Overview](../03%20Spec-Driven%20Development/01%20GitHub%20SpecKit%20Brief%20Overview/01%20GitHub%20SpecKit%20Brief%20Overview.md) · [Install](../03%20Spec-Driven%20Development/02%20Installing%20SpecKit/02%20Installing%20SpecKit.md) · [Constitution](../03%20Spec-Driven%20Development/03%20SpecKit%20Constitution%20-%20Interactive/03%20SpecKit%20Constitution%20-%20Interactive.md) · [Brownfield](../03%20Spec-Driven%20Development/05%20SpecKit%20Constitution%20-%20Brownfield/05%20SpecKit%20Constitution%20-%20Brownfield.md) · [Specify](../03%20Spec-Driven%20Development/06%20SpecKit%20Specify/06%20SpecKit%20Specify.md) · [Clarify](../03%20Spec-Driven%20Development/07%20SpecKit%20Clarify/07%20SpecKit%20Clarify.md) · [Plan](../03%20Spec-Driven%20Development/08%20SpecKit%20Plan/08%20SpecKit%20Plan.md) · [Tasks](../03%20Spec-Driven%20Development/09%20SpecKit%20Tasks/09%20SpecKit%20Tasks.md) · [Implement](../03%20Spec-Driven%20Development/10%20SpecKit%20Implement/10%20SpecKit%20Implement.md) · [Post-MVP](../03%20Spec-Driven%20Development/11%20SpecKit%20-%20Post-MVP/11%20SpecKit%20-%20Post-MVP.md) · [Quiz](../03%20Spec-Driven%20Development/12%20SpecKit%20Quiz/12%20SpecKit%20Quiz.md) |
| 04 Context Engineering | [Instructions](../04%20Context%20Engineering/01%20General%20practices/01%20Generating%20the%20agent%20instructions/01%20Generating%20the%20agent%20instructions.md) · [Status line](../04%20Context%20Engineering/01%20General%20practices/02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline.md) · [Caching](../04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md) · [Performance](../04%20Context%20Engineering/01%20General%20practices/04%20Context%20Window%20-%20Performance/04%20Context%20Window%20-%20Performance.md) · [Sessions](../04%20Context%20Engineering/01%20General%20practices/05%20Dividing%20tasks%20by%20sessions/05%20Dividing%20tasks%20by%20sessions.md) · [MCP overhead](../04%20Context%20Engineering/01%20General%20practices/06%20Reducing%20the%20number%20of%20MCP%20servers/06%20Reducing%20the%20number%20of%20MCP%20servers.md) · [Current docs](../04%20Context%20Engineering/01%20General%20practices/07%20Providing%20AI%20with%20up-to-date%20knowledge/07%20Providing%20AI%20with%20up-to-date%20knowledge.md) · [Indexing](../04%20Context%20Engineering/01%20General%20practices/08%20Intro%20to%20codebase%20indexing/08%20Intro%20to%20codebase%20indexing.md) · [Article](../04%20Context%20Engineering/01%20General%20practices/09%20All%20of%20above%20lessons%20as%20a%20text%20article/09%20All%20of%20above%20lessons%20as%20a%20text%20article.md) · [Skills](../04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills.md) · [Subagents](../04%20Context%20Engineering/03%20Sub-Agents/01%20External%20Course%20Introduction%20to%20subagents/01%20External%20Course%20Introduction%20to%20subagents.md) · [Agent Teams](../04%20Context%20Engineering/03%20Sub-Agents/02%20Claude%20Code%20Agent%20Teams/02%20Claude%20Code%20Agent%20Teams.md) · [Frameworks](../04%20Context%20Engineering/04%20Frameworks/01%20Introduction%20to%20Frameworks/01%20Introduction%20to%20Frameworks.md) · [Task Master](../04%20Context%20Engineering/04%20Frameworks/02%20Task-Master%20AI/02%20Task-Master%20AI.md) · [Quiz](../04%20Context%20Engineering/05%20General%20Practices%20Quiz/05%20General%20Practices%20Quiz.md) |
| 05 Advanced Techniques | [What comes next](../05%20Advanced%20Techniques/01%20More%20will%20follow%20here/01%20More%20will%20follow%20here.md) · [Where are you now?](../05%20Advanced%20Techniques/02%20Let%20us%20know%20where%20are%20you%20now/02%20Let%20us%20know%20where%20are%20you%20now.md) · [Open-weight models](../05%20Advanced%20Techniques/03%20Using%20local%20LLM%20without%20powerful%20hardware/03%20Using%20local%20LLM%20without%20powerful%20hardware.md) |
| 06 Applied Practices | [What comes next](../06%20Applied%20Practices/01%20More%20will%20follow%20here/01%20More%20will%20follow%20here.md) · [Accelerator](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md) · [Lovable → Google Cloud](../06%20Applied%20Practices/03%20Deploying%20Lovable%20project%20in%20Google%20Cloud%20with%20help%20of%20AI%20CLI/03%20Deploying%20Lovable%20project%20in%20Google%20Cloud%20with%20help%20of%20AI%20CLI.md) · [Self-healing CI/CD](../06%20Applied%20Practices/04%20Self-healing%20CI-CD%20with%20Claude%20Agents%20Teams/04%20Self-healing%20CI-CD%20with%20Claude%20Agents%20Teams.md) · [AI-first case study](../06%20Applied%20Practices/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation.md) |
| 07 Additional Themes | [Few-shot prompting](../07%20Additional%20Themes/01%20Few-Shot%20Prompting/01%20Few-Shot%20Prompting.md) · [RAG](../07%20Additional%20Themes/02%20Retrieval-Augmented%20Generation/02%20Retrieval-Augmented%20Generation.md) · [Model routing](../07%20Additional%20Themes/03%20Model%20Routing/03%20Model%20Routing.md) · [Prompt injection defenses](../07%20Additional%20Themes/04%20Prompt%20Injection%20Defenses/04%20Prompt%20Injection%20Defenses.md) · [RTK and Caveman](../07%20Additional%20Themes/05%20RTK%20and%20Caveman/05%20RTK%20and%20Caveman.md) |
