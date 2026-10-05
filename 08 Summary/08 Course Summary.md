# AI for Developers — Course Summary

This page distills the course into a practical reference. It revisits LLMs and agents, token economics, context windows, prompt and context design, project memory, session hygiene, model selection, specification-led delivery, skills, hooks, subagents, MCP, security, spending controls, team conventions, and the Innowise Accelerator. Short explanations provide a quick refresher, while lesson links make it easy to return to the full material.

The same reference is also available in Russian: [08 Course Summary (RU)](08%20Course%20Summary%20%28RU%29.md).

> **Check current sources:** Most tooling information represents the state of the ecosystem in June 2026; newer lessons were reviewed during autumn 2026. Because concrete workflows can become outdated within a few months, confirm model availability, commands, pricing, and quotas in the latest official documentation.

**Using this reference**

- Sections correspond to the main subject areas and contain brief, focused explanations.
- Entries marked **Lessons:** point to the longer treatment of that subject.
- References into Module 07 open focused material about few-shot examples, RAG, routing between models, prompt-injection protection, and RTK/Caveman.
- The final table serves as a concise directory of the entire course.

## Contents

1. [AI Fundamentals](#1-ai-fundamentals)
   - [LLMs](#question-ai-001) · [LLMs vs AI agents](#question-ai-002) · [Tool calling](#question-ai-003) · [Agent loop vs single-shot prompting](#question-ai-004) · [When a plain LLM call is enough](#question-ai-005) · [Risks of autonomous agents](#question-ai-006) · [Autonomy levels](#question-ai-007)
   - [Tokens and cost](#question-ai-008) · [The context window](#question-ai-009) · [Context fill and quality](#question-ai-010) · [Lost in the middle](#question-ai-011)
2. [Prompt Engineering and Meta-Prompting](#2-prompt-engineering-and-meta-prompting)
   - [What prompt engineering is](#question-ai-012) · [Prompting techniques](#question-ai-013) · [Few-shot prompting](#question-ai-014) · [Chain-of-thought](#question-ai-015) · [Decomposition](#question-ai-016) · [One big prompt or a chain](#question-ai-017)
   - [What meta-prompting is](#question-ai-018) · [Generating and improving prompts](#question-ai-019) · [Prompt critique loop](#question-ai-020) · [Self-improving prompt workflows](#question-ai-021)
3. [Context Engineering](#3-context-engineering)
   - [Context vs prompt engineering](#question-ai-022) · [Context sources](#question-ai-023) · [Choosing needed context](#question-ai-024) · [What to exclude](#question-ai-025) · [Reducing token usage](#question-ai-026) · [Hierarchical context](#question-ai-027) · [Context pipelines](#question-ai-028) · [RAG vs direct context](#question-ai-029)
4. [Memory Files](#4-memory-files-project-rules)
   - [Purpose of memory files](#question-ai-030) · [What belongs in memory](#question-ai-031) · [Why long instructions hurt](#question-ai-032) · [Memory files for large codebases](#question-ai-033)
5. [Session Degradation](#5-session-degradation)
   - [Signs of degradation](#question-ai-034) · [When to start a new session](#question-ai-035) · [Compaction and long-running work](#question-ai-036)
6. [Models: Speed, Cost, Quality](#6-models-speed-cost-quality)
   - [Fast vs reasoning models](#question-ai-037) · [Choosing a model per task](#question-ai-038) · [When expensive reasoning is not justified](#question-ai-039) · [Model routing](#question-ai-040) · [Orchestration vs one model](#question-ai-041) · [Team cost](#question-ai-042) · [RTK and Caveman](#question-ai-043)
7. [Specification-Driven Development](#7-specification-driven-development-sdd)
   - [What SDD is](#question-ai-044) · [SDD vs implementation-first](#question-ai-045) · [Why SDD fits AI-assisted coding](#question-ai-046) · [Good spec sections](#question-ai-047) · [Large-scale spec generation](#question-ai-048)
8. [AI-Assisted Tools](#8-ai-assisted-tools-ide-and-terminal)
   - [Skills](#question-ai-049) · [How skills enter context](#question-ai-050) · [Skills vs commands vs prompts](#question-ai-051) · [Tasks for skills](#question-ai-052) · [Reusable skill workflows](#question-ai-053) · [Standardizing with skills](#question-ai-054)
   - [Custom slash commands](#question-ai-055) · [Slash commands in teams](#question-ai-056) · [Hooks and types](#question-ai-057) · [Hooks vs instructions](#question-ai-058) · [Pre-tool hooks](#question-ai-059) · [Post-tool hooks](#question-ai-060) · [Security hooks](#question-ai-061) · [Review hooks](#question-ai-062) · [Shell scripts](#question-ai-063)
   - [Tasks for subagents](#question-ai-064) · [Lead and worker agents](#question-ai-065) · [Concurrency risks](#question-ai-066) · [Shared mutable context](#question-ai-067) · [Synchronizing agents](#question-ai-068)
9. [Model Context Protocol](#9-model-context-protocol-mcp)
   - [What MCP is](#question-ai-069) · [MCP vs API integration](#question-ai-070) · [Ecosystem benefits](#question-ai-071) · [MCP security risks](#question-ai-072)
10. [Security and Privacy](#10-security-and-privacy)
   - [Data not to send to an LLM](#question-ai-073) · [Working with secrets](#question-ai-074) · [AI-generated code risks](#question-ai-075) · [Insecure dependencies](#question-ai-076) · [Pre-merge checks](#question-ai-077) · [Prompt injection](#question-ai-078) · [Indirect prompt injection](#question-ai-079) · [Defenses](#question-ai-080)
11. [Monitoring, Debugging, and Cost Control](#11-monitoring-debugging-and-cost-control)
   - [Tracking cost](#question-ai-081) · [Inefficient orchestration](#question-ai-082) · [Debugging workflows](#question-ai-083)
12. [Tool Selection and Standardization](#12-tool-selection-and-standardization)
   - [Choosing team tools](#question-ai-084) · [Standardizing workflows](#question-ai-085)
13. [Innowise Accelerator](#13-innowise-accelerator)
   - [Architecture and principles](#question-ai-086) · [Phases and flows](#question-ai-087) · [`embacc` C++/Embedded port](#question-ai-088) · [Adoption](#question-ai-089)
14. [Ten Principles of the Course](#14-ten-principles-of-the-course)
15. [Course Map](#15-course-map)

---

## 1. AI Fundamentals

### LLMs and Agents

#### Question AI-001

[↑ Back to question index](#contents)

#### LLMs

A large language model is usually a transformer network that learns next-token prediction from extensive collections of text and source code. At inference time it consumes a token sequence and extends that sequence token by token. Anything it should remember must be supplied in the current context; its built-in knowledge has a cutoff date, and convincing language does not guarantee factual accuracy.

[↑ Back to question index](#contents)

#### Question AI-002

[↑ Back to question index](#contents)

#### LLMs vs AI agents

A standalone LLM transforms an input sequence into an output sequence. An agent adds **tools, an execution loop, and environmental feedback**: it may inspect files, invoke a shell or API, examine the response, and then choose another action. A typical cycle is context gathering → action → validation → completion or another iteration, with the user able to redirect the process throughout.

[↑ Back to question index](#contents)

#### Question AI-003

[↑ Back to question index](#contents)

#### Tool calling

The neural model does not directly operate the computer. Instead, it emits a **structured request** naming a tool and supplying JSON arguments based on the tool descriptions it received. A host such as Claude Code, Codex, or OpenCode checks permissions, performs the operation, and returns the outcome to the model. If this mechanism is absent, the model can suggest an action but cannot carry it out or learn what happened.

[↑ Back to question index](#contents)

#### Question AI-004

[↑ Back to question index](#contents)

#### Agent loop vs single-shot prompting

Single-shot prompting ends after one request and one response, so the model never receives operational feedback. An agent instead repeats plan → act → observe → revise, using signals such as a test failure or compiler diagnostic to change course. Claude Code exposes the same distinction by keeping read-only planning in Plan Mode separate from the later execution stage.

[↑ Back to question index](#contents)

#### Question AI-005

[↑ Back to question index](#contents)

#### When a plain LLM call is enough and when an agent is needed

Use one model call when the job is a self-contained transformation—for example, summarization, translation, classification, rewriting, or drafting. Choose an agent when progress depends on several actions, inspection of the working environment, and validation along the way, as in feature delivery, CI repair, multi-file refactoring, or defect investigation.

[↑ Back to question index](#contents)

#### Question AI-006

[↑ Back to question index](#contents)

#### Risks of autonomous agents

- Actions may be difficult to undo: an agent can erase a branch, push code, or alter cloud resources. One course example increased a VM size and moved daily spend from roughly USD 4 to USD 25.
- Small mistakes can compound across a long run, while the final report may still claim success; the course includes a feature declared complete even though its UI controls were absent.
- Unbounded iterations can consume tokens and money unexpectedly.
- Untrusted input may steer the agent through prompt injection (see [Security](#prompt-injection)).
- The agent can exceed its assignment by touching unrelated code or weakening checks merely to obtain a green pipeline.

[↑ Back to question index](#contents)

#### Question AI-007

[↑ Back to question index](#contents)

#### Autonomy levels: human-in-the-loop vs autonomous

- **Human-in-the-loop:** a person authorizes every action with meaningful consequences; this matches Claude Code's standard permission behavior.
- **Human-on-the-loop:** the system proceeds inside agreed boundaries while a person supervises and retains a stop control, such as automatic edit acceptance combined with an allowlist of commands.
- **Autonomous:** no one watches the run in real time. This level is appropriate only inside an isolated sandbox with narrow credentials and enforced limits.
Select a level after considering whether operations are reversible, how wide the potential impact is, whether checks can prove correctness, how sensitive the data is, and whether the workflow has been exercised before. Shift+Tab in Claude Code rotates among the default approval flow, automatic acceptance of edits, and read-only Plan Mode. Permission bypass should remain confined to isolated environments.

**Lessons:** [Welcome](../01%20Intro/01%20Welcome/01.%20Intro.%20AI%20Assisted%20Development.md) · [What is Claude Code](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/01%20What%20is%20Claude%20Code/01%20What%20is%20Claude%20Code.md) · [How Claude Code works](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/01%20What%20is%20Claude%20Code/02%20How%20Claude%20Code%20works.md) · [Structuring prompts](../02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29.md) · [AI-first case study](../06%20Applied%20Practices/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation.md)

[↑ Back to question index](#contents)

### Tokens and the Context Window

#### Question AI-008

[↑ Back to question index](#contents)

#### Tokens and cost

Models process text as tokens, which may represent whole words, fragments, or symbols. As a rough English estimate, one token spans about four characters; code and many other languages tokenize less compactly. Billing normally distinguishes **input tokens**—instructions, prior messages, files, tool schemas, and tool responses—from **output tokens** generated by the model. Agent sessions tend to send far more input than output, although generation often has the higher unit price. Since the active context accompanies every new call, later turns in a long conversation cost progressively more.

[↑ Back to question index](#contents)

#### Question AI-009

[↑ Back to question index](#contents)

#### The context window

The context window is the token budget available to a single inference call. That budget must hold the system message, repository guidance, conversation, attached code, tool descriptions and outputs, plus space for the response. Think of it as temporary working memory rather than durable storage. Do not confuse window utilization with total tokens accumulated during a session, provider throttles, or monetary usage.

[↑ Back to question index](#contents)

#### Question AI-010

[↑ Back to question index](#contents)

#### Context fill level and answer quality

Greater window occupancy means more input is resent on every turn, increasing cost and often reducing reliability. Old, irrelevant, or inconsistent material competes for attention, and centrally located details may be overlooked. Keeping usage near **20–50%** and compacting or restarting before the window becomes crowded is a useful operating heuristic, not a universal law. Judge whether the material is adequate, pertinent, and up to date, and consider the raw count as well as the percentage: 13% of a one-million-token window is still approximately 130K tokens.

[↑ Back to question index](#contents)

#### Question AI-011

[↑ Back to question index](#contents)

#### Lost in the middle

Liu et al. (2023) found a recurring positional effect: in long inputs, models often recover facts near the opening or closing more successfully than material buried in the center, though severity differs across models and tasks. Counter it by shortening and filtering the input, using explicit sections, placing essential constraints early or restating them near the end, and recording durable decisions in files rather than leaving them deep in a conversation.

**Lessons:** [Context windows, caching, and price](../04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md) · [Context size and performance](../04%20Context%20Engineering/01%20General%20practices/04%20Context%20Window%20-%20Performance/04%20Context%20Window%20-%20Performance.md) · [Status line](../04%20Context%20Engineering/01%20General%20practices/02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline.md) · [Claude 101: context management](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/03%20Daily%20Workflows/02%20Context%20Management.md)

[↑ Back to contents](#contents)

---

## 2. Prompt Engineering and Meta-Prompting

### Prompt Engineering

#### Question AI-012

[↑ Back to question index](#contents)

#### What prompt engineering is

Prompt engineering is the deliberate construction of model input so the response consistently matches an intended outcome. A useful prompt identifies the work, supplies required data, establishes constraints, and defines the result's shape. Coding assistants now assemble much of this structure automatically, so developers write fewer elaborate prompts during routine work. The discipline is still central when creating AI applications, agent runtimes, or customer-facing assistants that must stay within a defined purpose.

[↑ Back to question index](#contents)

#### Question AI-013

[↑ Back to question index](#contents)

#### Prompting techniques

- **Role framing:** establish the viewpoint the model should adopt, such as a security reviewer.
- **Few-shot examples:** demonstrate the intended mapping from input to output.
- **Chain-of-thought prompting:** request intermediate reasoning before the conclusion when that is useful.
- **Explicit organization:** put the task, source material, restrictions, and output contract in separate sections or tags, and name the expected format or schema.
- **Scope and completion rules:** state what belongs in the task, what does not, how success is recognized, and how it will be checked.
- **Decomposition:** turn a broad request into several independently verifiable operations.
Markdown is easy to read but can make nested boundaries ambiguous; YAML relies on correct indentation; JSON is unambiguous yet cumbersome for manual authoring; XML provides named opening and closing boundaries. Poorly separated input can cause source content to be interpreted as an instruction, as shown in the course translation exercise. Clear layout helps comprehension, but it does not neutralize prompt injection.

[↑ Back to question index](#contents)

#### Question AI-014

[↑ Back to question index](#contents)

#### Few-shot prompting

With few-shot prompting, several demonstrations are included in the request so the model can infer a subtle classification boundary, precise output convention, writing style, or condition for abstaining. This changes the current inference context; it is not training or fine-tuning. Begin without examples, then introduce them only when evaluation exposes a specific ambiguity. A compact and consistently delimited set should be accurate and varied—for instance, one normal case, one edge condition, and one legitimate refusal—while test cases remain separate. Demonstrations take up window space and may encode unintended patterns or inconsistencies, and they provide no protection from prompt injection. Re-evaluate the set after changing the model or system instructions.

[↑ Back to question index](#contents)

#### Question AI-015

[↑ Back to question index](#contents)

#### Chain-of-thought

Chain-of-thought techniques encourage the model to work through intermediate steps before reaching a conclusion. They are most valuable for logic, mathematics, and plans with several dependencies, but offer little benefit for straightforward retrieval or stylistic changes. Dedicated reasoning models and extended-thinking modes already perform internal deliberation, so their depth is better governed through effort or reasoning controls than by repeatedly asking them to think step by step. The course relates these controls to reasoning levels and plan mode.

[↑ Back to question index](#contents)

#### Question AI-016

[↑ Back to question index](#contents)

#### Decomposition

Narrow tasks reduce the amount of required context and make completion easier to define, which limits hidden assumptions and simplifies review. Decompose work around **observable outcomes**, rather than assigning arbitrary groups of files: a stage should end with evidence such as a passing test, an approved interface contract, or a functioning endpoint. Course examples include Explore → Plan → Code → Commit, the Spec Kit progression from specify to plan to tasks, and Task Master's dependency-aware graph.

[↑ Back to question index](#contents)

#### Question AI-017

[↑ Back to question index](#contents)

#### One big prompt vs a chain of small prompts

Multiple prompts create checkpoints where results can be inspected and corrected, while each stage receives only the context it needs. The tradeoff is additional latency and more model calls. A single request remains suitable for compact work whose parts cannot usefully be separated; larger efforts benefit from a sequence of testable stages connected by saved artifacts.

**Lessons:** [Structuring prompts](../02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29.md) · [Few-shot prompting](../07%20Additional%20Themes/01%20Few-Shot%20Prompting/01%20Few-Shot%20Prompting.md) · [Explore → Plan → Code → Commit](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/03%20Daily%20Workflows/01%20The%20Explore%20%E2%86%92%20Plan%20%E2%86%92%20Code%20%E2%86%92%20Commit%20Workflow.md) · [Task Master AI](../04%20Context%20Engineering/04%20Frameworks/02%20Task-Master%20AI/02%20Task-Master%20AI.md)

[↑ Back to question index](#contents)

### Meta-Prompting

#### Question AI-018

[↑ Back to question index](#contents)

#### What meta-prompting is

Meta-prompting asks a model to design or refine the instruction that will later drive another model call. It explicitly separates prompt construction from execution—for example, requesting a precise implementation prompt while prohibiting implementation at that stage. The deliverable is the improved instruction itself rather than source code.

[↑ Back to question index](#contents)

#### Question AI-019

[↑ Back to question index](#contents)

#### Generating and improving prompts with AI

- Divide the meta-prompt into named regions such as `<meta_task>`, `<draft_prompt>`, `<investigation>` for permitted research, and `<output_requirements>` for the final contract.
- Prefer an agent with repository access so the resulting instruction reflects the actual language, directory layout, conventions, and test suite. A generic chatbot can improve prose but may invent technical context; one course run selected TypeScript for a Go codebase.
- Require separate lists of verified facts, assumptions, and unresolved questions, then inspect the generated prompt before using it.
- Different tools ground the refinement differently: Augment Code retrieves semantically relevant code, NotebookLM works from chosen documents, and `ai-dev-tasks` gathers three to five clarifications before producing a PRD.
- Treat the revised prompt as a draft. Repository evidence cannot expose product or UX decisions that have never been written down, so provide those decisions directly.

[↑ Back to question index](#contents)

#### Question AI-020

[↑ Back to question index](#contents)

#### The prompt critique / refinement loop

The refinement cycle is: create an instruction, execute it, evaluate both the instruction and its output against the goal, revise, and run again. Repeat until the predefined acceptance checks pass. Keep those checks stable between trials and isolate each attempt in a new session so an earlier failure does not influence the next result through conversation history.

[↑ Back to question index](#contents)

#### Question AI-021

[↑ Back to question index](#contents)

#### Self-improving prompt workflows

A self-improving workflow converts observed failures into explicit rules instead of relying on ad hoc wording changes. Once validated, the refined instruction can become a shared template, a project rule, or a reusable skill. Guard against optimizing for only a handful of examples or gradually changing the original objective by maintaining a modest but representative evaluation set and requiring human review. In the Accelerator, `stabilize` and `reflect` illustrate how one-off corrections can become durable team knowledge.

**Lessons:** [Augment Code enhancement](../02%20Meta-Prompting/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code.md) · [Tool-agnostic meta-prompting](../02%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting.md) · [NotebookLM](../02%20Meta-Prompting/04%20Meta-Prompting%20with%20NotebookLM/04%20Meta-Prompting%20with%20NotebookLM.md) · [First PRD with ai-dev-tasks](../02%20Meta-Prompting/05%20Creating%20your%20first%20Product%20Requirement%20Document/05%20Creating%20your%20first%20Product%20Requirement%20Document.md)

[↑ Back to contents](#contents)

---

## 3. Context Engineering

### Question AI-022

[↑ Back to question index](#contents)

#### Context engineering vs prompt engineering

Prompt engineering concentrates on the wording of a request. Context engineering governs the complete information package presented to the model and the moment each part is introduced: system guidance, repository rules, prior messages, source files, diffs, tool schemas and responses, retrieved references, skills, and reports from subagents. Success means assembling an authorized, well-organized set that is current, relevant, and sufficient—not maximizing or minimizing token count for its own sake.

[↑ Back to question index](#contents)

### Question AI-023

[↑ Back to question index](#contents)

#### Context sources in AI coding workflows

- Platform-level prompts and instructions supplied by the agent host.
- Repository memory such as `CLAUDE.md`, `AGENTS.md`, and scoped rule files.
- Relevant implementation, patches, and Git history.
- Results returned by tests, build tools, linters, and command-line utilities.
- MCP tool schemas made visible to the model.
- Current external or internal references, including official documentation, Context7, and vendor CLIs.
- Requirements and delivery artifacts such as a PRD, constitution, `spec.md`, `plan.md`, or `tasks.md`.
- On-demand skills, concise subagent findings, and matches retrieved from a code index.

[↑ Back to question index](#contents)

### Question AI-024

[↑ Back to question index](#contents)

#### Deciding what context the agent needs

Work backward from the requested outcome and its completion test. Initially provide what a capable engineer would need: pertinent files, operating constraints, acceptance conditions, and a verification method. Additional code or documentation should be retrieved only when the work calls for it, rather than loaded speculatively. The course captures this package in a **task contract** containing the objective, scope, supporting evidence, limits, completion condition, and boundaries for independent decisions.

[↑ Back to question index](#contents)

### Question AI-025

[↑ Back to question index](#contents)

#### Overstuffed context and what to exclude

An overloaded window increases repeated input cost and makes distraction, contradictory guidance, and middle-position failures more likely. Leave out bulky or generated content: dependency locks, compiler artifacts, `dist/`, `node_modules/`, minified assets, unrelated packages, obsolete conversation history, inactive MCP integrations, and every secret. Trim logs to the evidence that matters—for example, collect only failed job output with `gh run view --log-failed`.

[↑ Back to question index](#contents)

### Question AI-026

[↑ Back to question index](#contents)

#### Reducing token usage without losing quality

- Supply selected passages or search hits rather than entire documents, and cap the amount returned by tools.
- If the objective remains unchanged, summarize accumulated history or invoke `/compact`; when the objective changes, open a clean session.
- Isolate high-volume activities such as log inspection or research in subagents, optionally using a less costly model, and return only a brief conclusion.
- Expose only the MCP servers needed for the current task; defer large tool catalogs or favor a CLI where it is simpler.
- Preserve a stable prompt prefix to benefit from caching: writing a cache is relatively expensive and reading it is discounted, although cached material still consumes window capacity.
- Reserve project instruction files for enduring rules and place multi-step procedures in skills.
- Consider compression utilities such as RTK on input and Caveman on output (see [Models](#6-models-speed-cost-quality)).

[↑ Back to question index](#contents)

### Question AI-027

[↑ Back to question index](#contents)

#### Hierarchical context for large projects

Arrange project knowledge in layers, moving from permanent guidance to information fetched only when required:
1. Keep the root `CLAUDE.md` or `AGENTS.md` concise, covering purpose, essential build and test commands, core conventions, and prohibited areas.
2. Put package-specific guidance near the relevant module and use path filters where supported, such as `paths:` frontmatter under Claude Code's `.claude/rules/`.
3. Store operational playbooks as skills that load only for matching work.
4. Link to durable specifications and documentation through an index or manifest—`Specs/manifest.md` in the Accelerator—so later agents select only applicable artifacts.
5. Discover everything else through exact search, language-server navigation, Git history, or a semantic codebase index.

[↑ Back to question index](#contents)

### Question AI-028

[↑ Back to question index](#contents)

#### Context pipelines for coding agents

Model context can be managed as a repeatable flow: **baseline guidance → task contract → retrieval** from search, indexes, and documentation **→ filtering and compression → work → persistence** of decisions and results **→ compaction or a handoff** for the next session. Prefer reproducible mechanisms, including scripts that extract only failing diagnostics, startup hooks that add known context, subagents that return condensed findings, and file-based handoffs instead of conversational memory. Capture source identity and version information so conclusions remain auditable.

[↑ Back to question index](#contents)

### Question AI-029

[↑ Back to question index](#contents)

#### RAG vs passing context directly

Retrieval-Augmented Generation selects passages from an external collection and adds them to the inference input before an answer is produced. A mature RAG system parses sources, forms coherent chunks, records provenance and authorization metadata, searches by keyword, vector similarity, or a hybrid method, reranks candidates, and instructs the model to base its response and citations on the retained evidence. It is useful when the corpus exceeds the window, changes frequently, contains organization-specific knowledge, or demands traceability. Direct inclusion is simpler when the correct material is already known and small.

Measure retrieval independently from response generation. First ask whether the system returned evidence that is sufficient, current, relevant, and permitted for this user; then determine whether the response follows that evidence, cites it correctly, and declines to answer when support is absent. Enforce access policy before any retrieved passage enters the model, and regard that passage as untrusted because it could carry indirect prompt injection. Course examples include Augment's context engine, the Auggie `codebase-retrieval` index, Context7 for library references, and NotebookLM for source-bound document work. Search output remains a lead that should be confirmed against the latest authoritative source.

**Lessons:** [Consolidated context-engineering article](../04%20Context%20Engineering/01%20General%20practices/09%20All%20of%20above%20lessons%20as%20a%20text%20article/09%20All%20of%20above%20lessons%20as%20a%20text%20article.md) · [RAG](../07%20Additional%20Themes/02%20Retrieval-Augmented%20Generation/02%20Retrieval-Augmented%20Generation.md) · [One task, one chat](../04%20Context%20Engineering/01%20General%20practices/05%20Dividing%20tasks%20by%20sessions/05%20Dividing%20tasks%20by%20sessions.md) · [MCP overhead](../04%20Context%20Engineering/01%20General%20practices/06%20Reducing%20the%20number%20of%20MCP%20servers/06%20Reducing%20the%20number%20of%20MCP%20servers.md) · [Up-to-date documentation](../04%20Context%20Engineering/01%20General%20practices/07%20Providing%20AI%20with%20up-to-date%20knowledge/07%20Providing%20AI%20with%20up-to-date%20knowledge.md) · [Codebase indexing](../04%20Context%20Engineering/01%20General%20practices/08%20Intro%20to%20codebase%20indexing/08%20Intro%20to%20codebase%20indexing.md)

[↑ Back to contents](#contents)

---

## 4. Memory Files (Project Rules)

### Question AI-030

[↑ Back to question index](#contents)

#### Purpose of CLAUDE.md, AGENTS.md, and Cursor rules

Memory files give an assistant durable repository guidance that is loaded at the beginning of its sessions. They save repeated explanations by recording the technology stack, essential build and test commands, local conventions, architectural limits, and protected areas. Claude Code conventionally reads `CLAUDE.md`; Codex and several other tools use the portable `AGENTS.md` convention, which Claude Code can also consume; Cursor stores comparable guidance under `.cursor/rules/`. `/init` can produce a starting point, but every statement and command still needs human verification. These files influence the model rather than enforce policy, so hard restrictions belong in permission controls or hooks.

[↑ Back to question index](#contents)

### Question AI-031

[↑ Back to question index](#contents)

#### What belongs in memory files and what does not

- **Include:** authoritative commands for building, testing, and linting; nonstandard coding rules; important structural and architectural boundaries; actions or locations that are off limits; recurring traps; and pointers to longer documentation.
- **Leave out:** facts readily discoverable from the repository, such as complete directory or dependency inventories; temporary task notes; credentials; generated codebase maps; constraints already guaranteed by automated checks; and lengthy procedures that should be packaged as skills.
- A practical trigger for adding guidance is a repeated agent mistake or a review finding that existing project knowledge should have prevented.

[↑ Back to question index](#contents)

### Question AI-032

[↑ Back to question index](#contents)

#### Why long instruction files hurt

Because project instructions accompany every request, excess text repeatedly consumes tokens. A crowded rule set also weakens attention to each individual item and tends to retain obsolete or mutually inconsistent guidance. Claude Code recommends aiming for roughly fewer than 200 lines in an instruction file, while Codex applies a default 32 KiB ceiling to project guidance.

[↑ Back to question index](#contents)

### Question AI-033

[↑ Back to question index](#contents)

#### Memory files for a large codebase

- Combine a small root document with additional guidance inside individual services or packages. Claude Code concatenates these files with the nearest one read last; Codex gives more local guidance precedence and recognizes `AGENTS.override.md`.
- Use path-filtered entries such as `.claude/rules/*.md` with `paths:` so specialized rules appear only while relevant files are in scope.
- Move procedures into skills. Imports such as `@docs/...` may improve organization, but they still load initially and therefore do not reduce context usage.
- Keep developer-specific preferences in uncommitted `CLAUDE.local.md` or user-level configuration.
- Maintain one authoritative body of guidance across tools—for example, have `CLAUDE.md` import `@AGENTS.md`—and verify in a clean session that the intended hierarchy is actually loaded.
- Review the hierarchy regularly for conflicts and stale content; in a monorepo, use options such as `claudeMdExcludes` to avoid loading another team's instructions.

**Lessons:** [Generating project instructions](../04%20Context%20Engineering/01%20General%20practices/01%20Generating%20the%20agent%20instructions/01%20Generating%20the%20agent%20instructions.md) · [Claude 101: the CLAUDE.md file](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/04%20Customizing%20Claude%20Code/01%20The%20CLAUDE.md%20File.md)

[↑ Back to contents](#contents)

---

## 5. Session Degradation

### Question AI-034

[↑ Back to question index](#contents)

#### Signs of a degrading session

A session may be deteriorating when the assistant repeats the same exploration, restores defects it had removed, loses agreed constraints, conflicts with its own prior conclusions, overlooks repository guidance, or becomes increasingly vague. A nearly full context indicator is another warning. Two common mechanisms are **context clash**, in which old objectives contradict the present one, and **context distraction**, in which irrelevant history competes with the useful material.

[↑ Back to question index](#contents)

### Question AI-035

[↑ Back to question index](#contents)

#### When to start a new session

Open a fresh conversation after a change of objective, at the first clear signs of degraded behavior, or at a natural boundary such as specification approval, plan acceptance, or feature integration. Before leaving the current session, persist decisions and status in a specification, plan, checklist, or handoff document. Seed the next conversation with a compact task contract. The course's shorthand is “one task, one chat”: activities may remain together only while they share the same completion condition.

[↑ Back to question index](#contents)

### Question AI-036

[↑ Back to question index](#contents)

#### Context compaction and long-running work

Compaction frees window capacity by replacing earlier dialogue with a shorter synopsis. Claude Code and Codex expose this through `/compact`, and Claude Code may trigger it automatically near its limit. Since summarization can omit important detail:
- compact only to continue the **same** goal, then inspect the generated synopsis for omissions;
- persist long-lived state in specifications, `tasks.md`, or handoff notes instead of relying on the transcript;
- use `/clear` or begin another session for a different objective, and create a fork when comparing approaches;
- anchor extended efforts in a tracker such as Spec Kit artifacts, Task Master, or the Accelerator's `STATE.md`.
After compaction, the project-level `CLAUDE.md` is loaded again, whereas guidance that existed only in chat may disappear.

**Lessons:** [One task, one chat](../04%20Context%20Engineering/01%20General%20practices/05%20Dividing%20tasks%20by%20sessions/05%20Dividing%20tasks%20by%20sessions.md) · [Status line](../04%20Context%20Engineering/01%20General%20practices/02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline.md) · [Spec Kit overview](../03%20Spec-Driven%20Development/01%20GitHub%20SpecKit%20Brief%20Overview/01%20GitHub%20SpecKit%20Brief%20Overview.md)

[↑ Back to contents](#contents)

---

## 6. Models: Speed, Cost, Quality

### Question AI-037

[↑ Back to question index](#contents)

#### Fast models vs reasoning models

Reasoning-oriented models spend additional computation on internal deliberation, often with a configurable effort level. That improves performance on ambiguous or multi-stage work such as architecture, difficult debugging, and critical review, but adds latency and expense. Faster models, including Haiku-class options, are a better fit for inexpensive execution of clear and mechanical instructions.

[↑ Back to question index](#contents)

### Question AI-038

[↑ Back to question index](#contents)

#### Choosing a model per task

- **Low-cost, low-latency models:** extract data, search files, summarize logs, apply formatting, create boilerplate, or perform straightforward edits.
- **Balanced models (Sonnet class):** handle routine development when the plan and acceptance criteria are already clear.
- **High-reasoning models (Opus/Fable class at greater effort):** take on architecture, planning, unclear failures, security analysis, code review, and coordination of other agents.
The self-healing CI/CD example assigned log inspection to Haiku, code repair to Sonnet, and coordination plus review to Opus. Evaluate that allocation using the cost of a **successfully completed task**, rather than comparing token prices in isolation.

[↑ Back to question index](#contents)

### Question AI-039

[↑ Back to question index](#contents)

#### When an expensive reasoning model is not justified

Do not pay for deep reasoning when the work is repetitive or deterministic: basic retrieval, mass processing, renaming, formatting, and other simple transformations rarely benefit. The same applies to latency-critical interactions and jobs already solved more reliably by a formatter, codemod, linter, or another deterministic program.

[↑ Back to question index](#contents)

### Question AI-040

[↑ Back to question index](#contents)

#### Routing between models

Routing assigns a model at the granularity of a request, workflow stage, or agent responsibility. Begin by excluding candidates that fail mandatory requirements for data residency and handling, modality or tool support, context length, service availability, or minimum task quality. Selection can then follow a fixed task-to-model map, deterministic policy, trained classifier, verified-failure escalation cascade, or approved fallback chain. The model's own confidence should never be the sole reason to escalate.

For every decision, record which model ran, why it was selected, whether a fallback occurred, and the resulting latency and cost. Test the router against both a single-model baseline and a simple rules baseline on realistic tasks. Relevant measures include end-to-end completion, valid schemas and tool calls, retry counts, and the amount of human correction—not merely price per token. Longer conversations may deliberately retain model affinity to preserve behavioral consistency and reuse cached prefixes. Course tooling examples include Claude Code's `/model`, model choices in subagent configuration, Task Master's main/research/fallback roles, and gateways that expose several providers.

[↑ Back to question index](#contents)

### Question AI-041

[↑ Back to question index](#contents)

#### Orchestration vs one powerful model

Orchestration can narrow each worker's context, execute independent branches concurrently, reserve inexpensive models for volume, and use stronger models where judgment matters. A separate reviewer also approaches the result without the implementer's accumulated assumptions. These benefits come with communication cost, higher aggregate token use because every teammate owns a separate session, and potential merge or integration failures. Multi-agent execution is worthwhile only when the problem divides cleanly.

[↑ Back to question index](#contents)

### Question AI-042

[↑ Back to question index](#contents)

#### Optimizing team cost

- Keep conversations tied to one objective; summarize or restart before they become indefinitely long.
- Reduce repeated context through concise memory files, procedural skills, a small MCP surface, and limits on tool output.
- Avoid unnecessary changes to reusable prompt prefixes so caching remains effective.
- Route by task characteristics and assign high-volume investigation to lower-cost subagents.
- Invest in specifications and plans to avoid expensive rework; in the course case study, revisiting finished work consumed about as much as building new functionality.
- Size dedicated accounts to actual demand, configure budget controls and usage reporting, and track spend per completed outcome.
- Share proven skills and delivery patterns so each developer does not pay to rediscover the same approach.

[↑ Back to question index](#contents)

### Question AI-043

[↑ Back to question index](#contents)

#### RTK and Caveman

- **[RTK](https://github.com/rtk-ai/rtk), or Rust Token Killer,** sits in front of supported command-line operations and filters their output before an agent receives it. Its main target is **input volume** produced by commands such as `git`, searches, test suites, and linters; available integrations can use tool-specific hooks to redirect eligible calls.
- **[Caveman](https://github.com/JuliusBrussee/caveman)** includes a skill that makes agent replies more terse, together with wider proxy and runtime features that condense content read by the agent. Depending on the selected component, it may reduce generated text, incoming context, or both.
- Neither project is part of the model provider's trusted core. Compression may remove a vital diagnostic, and headline savings published by a project do not necessarily translate to total session reduction. Preserve access to unfiltered output, audit hook and proxy boundaries, understand storage and telemetry as well as removal behavior, and run paired trials that compare provider-reported usage, correctness, retries, and human review time.

**Lessons:** [Model routing](../07%20Additional%20Themes/03%20Model%20Routing/03%20Model%20Routing.md) · [RTK and Caveman](../07%20Additional%20Themes/05%20RTK%20and%20Caveman/05%20RTK%20and%20Caveman.md) · [Caching and price](../04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md) · [Agent Teams](../04%20Context%20Engineering/03%20Sub-Agents/02%20Claude%20Code%20Agent%20Teams/02%20Claude%20Code%20Agent%20Teams.md) · [Self-healing CI/CD](../06%20Applied%20Practices/04%20Self-healing%20CI-CD%20with%20Claude%20Agents%20Teams/04%20Self-healing%20CI-CD%20with%20Claude%20Agents%20Teams.md) · [Open-weight models](../05%20Advanced%20Techniques/03%20Using%20local%20LLM%20without%20powerful%20hardware/03%20Using%20local%20LLM%20without%20powerful%20hardware.md) · [Toolset](../01%20Intro/03%20Our%20Toolset%20as%20for%20Now/03%20Our%20Toolset%20as%20for%20Now.md)

[↑ Back to contents](#contents)

---

## 7. Specification-Driven Development (SDD)

### Question AI-044

[↑ Back to question index](#contents)

#### What specification-driven development is

Specification-driven development makes an agreed written specification the authority for subsequent delivery. Code is produced only after that artifact is approved, and the finished implementation is judged against it. The document forms the working agreement between a person and an AI system by describing the desired outcome, its purpose, measurable acceptance conditions, and explicit exclusions. GitHub Spec Kit is the course's concrete implementation of this approach.

[↑ Back to question index](#contents)

### Question AI-045

[↑ Back to question index](#contents)

#### SDD vs implementation-first

In an implementation-first process, development begins with a rough idea and requirements emerge during coding, leaving many decisions in memory or conversation history. SDD resolves ambiguity before implementation and stores the results in lasting artifacts: a constitution for project policy, a specification for the outcome and rationale, a plan for the technical method, and a set of executable tasks. When requirements change, the relevant artifact is updated before downstream code, and validation uses the written agreement instead of recollection.

[↑ Back to question index](#contents)

### Question AI-046

[↑ Back to question index](#contents)

#### Why AI-assisted coding fits SDD

A specification supplies reusable context that survives conversation boundaries; a clean session can load it without reconstructing old chat. It curbs invented requirements and implicit assumptions, creates an objective basis for acceptance, and permits safe context resets between stages. The AI-first case study demonstrates the opposite pattern: when AI-oriented requirements were not stabilized, rapid changes produced immediate legacy code and recurring rework.

[↑ Back to question index](#contents)

### Question AI-047

[↑ Back to question index](#contents)

#### Sections of a good implementation spec

A useful implementation specification identifies the goal and intended users, defines both included and **excluded** scope, and describes user journeys or stories with acceptance criteria. It also covers functional behavior, non-functional expectations such as performance, security, and accessibility, edge and failure cases, measurable success indicators, precisely named dependencies and integrations, assumptions, and unresolved questions. In Spec Kit, `spec.md` avoids prescribing technology, while `plan.md` introduces the stack, data structures, contracts, and required research.

[↑ Back to question index](#contents)

### Question AI-048

[↑ Back to question index](#contents)

#### Problems of large-scale spec generation

- Generated documents can silently add requirements. In the course case study, a four-page brief expanded into an 82-page specification whose content was roughly 30% invented.
- Over a long generation, earlier context may be lost and later sections can disagree with the opening.
- The system may introduce unnecessary complexity or unapproved “hidden stories.”
- Dependencies expressed as forward references between epics can be overlooked instead of revisited later.
- After a change, specifications easily become stale, while wholesale regeneration is expensive and may alter unrelated decisions.
Reduce these risks by linking every requirement to a client source or labeling it as an assumption, dividing the design into smaller files for foundations, epics, discussions, and the project plan, and reviewing each unit independently. Capture revisions as focused change records or additional epics, and designate exactly one authoritative artifact for every decision.

**Spec Kit at a glance**
- **Sequence:** create the project constitution once, then run specify → clarify\* → plan → checklist\* → tasks → analyze\* → implement → converge, where the asterisk denotes an optional stage.
- **Installation and initialization:** run `uv tool install specify-cli`, followed by `specify init --here --integration <agent>`. The `specify` command belongs in the terminal; individual stages are started from agent chat using `/speckit.plan` in the canonical form, `/speckit-plan` for Claude Code skills, or `$speckit-plan` in Codex.
- **Stored outputs:** the constitution lives at `.specify/memory/constitution.md`. Each `specs/NNN-feature/` directory can contain `spec.md`, `checklists/requirements.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, and `tasks.md`.
- **Operating discipline:** correct a decision in the artifact responsible for it, then rebuild the dependent artifacts. The analyze stage must not mutate content, whereas converge may append tasks that were missed. A checkbox becomes `[X]` only after evidence verifies completion, and every distinct capability begins another `specs/00N-…` cycle.

**Lessons:** [Spec-Driven Development module](../03%20Spec-Driven%20Development/01%20GitHub%20SpecKit%20Brief%20Overview/01%20GitHub%20SpecKit%20Brief%20Overview.md) · [Specify](../03%20Spec-Driven%20Development/06%20SpecKit%20Specify/06%20SpecKit%20Specify.md) · [Post-MVP](../03%20Spec-Driven%20Development/11%20SpecKit%20-%20Post-MVP/11%20SpecKit%20-%20Post-MVP.md) · [AI-first case study](../06%20Applied%20Practices/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation.md) · [First PRD](../02%20Meta-Prompting/05%20Creating%20your%20first%20Product%20Requirement%20Document/05%20Creating%20your%20first%20Product%20Requirement%20Document.md)

[↑ Back to contents](#contents)

---

## 8. AI-Assisted Tools (IDE and Terminal)

### Claude Code Agent Skills

#### Question AI-049

[↑ Back to question index](#contents)

#### What a skill is

A skill is a directory centered on `SKILL.md`. Its YAML frontmatter declares a lowercase, hyphenated `name` and a `description`, followed by the workflow instructions in Markdown. The directory may additionally provide `references/` that are opened only when needed, executable helpers in `scripts/` whose source need not enter the model context, and reusable `assets/`. Optional metadata can select a `model` or list `allowed-tools`; the latter pre-authorizes those tools while the skill runs but does not prohibit every other tool. Personal skills reside in `~/.claude/skills/`, repository skills in `.claude/skills/`, and name collisions are resolved in the order enterprise, personal, project, then plugin.

[↑ Back to question index](#contents)

#### Question AI-050

[↑ Back to question index](#contents)

#### How a skill enters the context

Skills use **progressive disclosure**. At first, the model sees only the catalog of names and descriptions. The full `SKILL.md` enters context after the model matches its description to the task or the user explicitly requests `/skill-name`; referenced documents are opened later only when the workflow calls for them. Consequently, the description must communicate both the capability **and its trigger conditions**. Invocation can be constrained in frontmatter: `disable-model-invocation: true` reserves activation for the user, while `user-invocable: false` hides it from direct user invocation.

[↑ Back to question index](#contents)

#### Question AI-051

[↑ Back to question index](#contents)

#### Skills vs slash commands vs prompts

A slash command is a named shortcut deliberately invoked by a person. A skill can also be called by name, but the agent may discover and activate it from its description, and it can carry scripts, references, and assets. A normal conversational prompt has no reusable package around it. Recent Claude Code versions treat custom commands as part of the skills system, so both `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` expose `/deploy`.

[↑ Back to question index](#contents)

#### Question AI-052

[↑ Back to question index](#contents)

#### Tasks that suit skills

Package a skill when a procedure recurs with largely stable stages—for example, releasing software, creating a module from a template, applying a review checklist, producing a standardized report, or following a deployment runbook. Other mechanisms fit different needs: use an ordinary prompt for a one-time request, memory files for guidance that is always present, hooks for behavior that must execute, subagents for context isolation, and MCP for connections to external tools or data.

[↑ Back to question index](#contents)

#### Question AI-053

[↑ Back to question index](#contents)

#### Reusable engineering workflows with skills

Give each skill one well-defined responsibility, a trigger description that distinguishes it from neighboring capabilities, and an explicit input/output contract. Aim to keep `SKILL.md` below roughly 500 lines by moving background material to references and predictable operations to scripts. Larger workflows can connect several skills through durable handoff artifacts and deliberate human checkpoints, following the Accelerator pattern of command → agent → skill → artifact. Store skills in Git, exercise them against realistic scenarios, and revise them when the actual engineering process evolves. A workflow should become a skill only after repeated manual use has shown it to be stable.

[↑ Back to question index](#contents)

#### Question AI-054

[↑ Back to question index](#contents)

#### Standardizing team development with skills

Shared skills give every developer the same procedure and output contract, shorten onboarding, and let one correction improve future runs for the entire team. They may be delivered with the repository, through a plugin or marketplace, or by centrally managed enterprise configuration. Treat any external skill as executable supply-chain material and review it with the same care as source code.

**Lessons:** [Introduction to Agent Skills](../04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills.md) · [Innowise Accelerator](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md)

[↑ Back to question index](#contents)

### Custom Slash Commands (deprecated—merged into skills)

#### Question AI-055

[↑ Back to question index](#contents)

#### What custom slash commands are

Legacy custom commands are Markdown prompt templates stored in `.claude/commands/` for a project or `~/.claude/commands/` for a user. They run only when someone enters `/name`, and receive parameters through `$ARGUMENTS` or positional placeholders such as `$1` and `$2`. Claude Code continues to recognize existing files, but skills are preferred for new automation because they support companion resources, activation policies, and model-driven discovery.

[↑ Back to question index](#contents)

#### Question AI-056

[↑ Back to question index](#contents)

#### Slash commands in a team workflow

Repository-level commands make shortcuts such as `/review`, `/release`, and `/commit-push-pr` consistent across the team. Their names should reveal intent and their arguments should be documented. Pair them with hooks when a check must be unavoidable, and convert a command to a skill once it needs supporting resources or automatic selection by the agent.

[↑ Back to question index](#contents)

### Claude Code Hooks

#### Question AI-057

[↑ Back to question index](#contents)

#### Hooks and their types

Hooks attach predictable handlers to events in the agent lifecycle. Shell commands are the common handler type, although HTTP, prompt, and agent-based hooks are also available. Core events include `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `PreCompact`, and `Notification`; newer versions also expose `PermissionRequest`, `SessionEnd`, and team-related events. Matchers narrow a hook to selected tools, for example `Edit|Write`. Configuration can be edited in `settings.json` or through `/hooks`, while shared project hooks belong in the committed `.claude/settings.json`.

[↑ Back to question index](#contents)

#### Question AI-058

[↑ Back to question index](#contents)

#### Hooks vs agent instructions

Unlike natural-language guidance, a hook is invoked **whenever** its matching event occurs. Text in `CLAUDE.md` or a skill can influence the model but cannot guarantee compliance. `PreToolUse` may prevent execution: status 2 rejects the call and returns stderr to Claude, while status 0 can accompany JSON that changes the input or sets `permissionDecision` to `allow`, `deny`, or `ask`. Put mandatory, repeatable behavior in a hook rather than trusting a prompt to remember it.

[↑ Back to question index](#contents)

#### Question AI-059

[↑ Back to question index](#contents)

#### Pre-tool hooks

Before a tool runs, a hook can reject destructive operations such as `rm -rf`, a forced push, or `terraform apply`; shield paths containing `.env` files, credentials, or migrations; validate and transform command lines; enforce branch policy; or demand explicit approval for selected tools. RTK, for example, can replace `git status` with `rtk git status` at this stage.

[↑ Back to question index](#contents)

#### Question AI-060

[↑ Back to question index](#contents)

#### Post-tool hooks

After execution, hooks can format or lint modified files, run the relevant tests and type checks, record tool activity for audit, and inspect newly written content for exposed credentials. Returning any failure to the agent enables correction before the workflow advances.

[↑ Back to question index](#contents)

#### Question AI-061

[↑ Back to question index](#contents)

#### Enforcing security policies with hooks

Security hooks create a policy layer that does not depend on model judgment. They can prevent access to secrets, reject destructive or unauthorized network and cloud operations, scan for leaked credentials and vulnerable packages, confine writes to approved paths, and produce an audit trail. Use them alongside permission policies, managed configuration, and sandboxing. Because a hook executes with the user's own privileges, inspect repository-provided hooks as carefully as any other executable code before trusting the project.

[↑ Back to question index](#contents)

#### Question AI-062

[↑ Back to question index](#contents)

#### Automating code-review checks with hooks

Review automation can trigger formatters, linters, test suites, type analysis, and SAST either after each modification or when the agent reaches `Stop`. Feed diagnostics back into the same run so defects are addressed before handoff. For agent teams, gates attached to `TaskCompleted` or `TeammateIdle` can withhold acceptance until required checks pass.

**Lessons:** [Claude 101: hooks](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/04%20Customizing%20Claude%20Code/05%20Hooks.md) · [Skills vs other Claude Code features](../04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/Introduction%20to%20agent%20skills/04%20Skills%20vs.%20other%20Claude%20Code%20features/04%20Skills%20vs.%20other%20Claude%20Code%20features.md) · [Innowise Accelerator: security boundary](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md)

[↑ Back to question index](#contents)

### Shell Scripts and Workflow Automation

#### Question AI-063

[↑ Back to question index](#contents)

#### Shell scripts in agent orchestration

- Encode predictable operations—building, testing, linting, environment setup, or extraction of failed logs—in scripts instead of asking a model to reproduce them.
- Noninteractive entry points such as `claude -p "…"` and `codex exec` allow those agent workflows to run from scripts or CI.
- A script can iterate across tasks or files and coordinate isolated worktrees for parallel execution.
- When a skill invokes a helper, only the helper's result needs to consume context; its complete source can remain outside the window.
- Command-line clients including `gh`, `gcloud`, and `glab` expose transparent, inspectable operations without loading a large MCP tool catalog, as demonstrated in the self-healing pipeline and Lovable deployment lessons.

[↑ Back to question index](#contents)

### Subagents

#### Question AI-064

[↑ Back to question index](#contents)

#### Tasks that suit subagents

Subagents are most effective for separable work whose internal transcript is unimportant to the parent: independent review perspectives, research, repository exploration, high-volume log analysis, disjoint file migrations, or test execution where only the outcome matters. They are a poor match for tightly ordered chains such as reproduce → diagnose → repair, or for debugging in which the parent must inspect intermediate observations.

[↑ Back to question index](#contents)

#### Question AI-065

[↑ Back to question index](#contents)

#### Lead agent and worker agents

The lead divides the objective, prepares a narrowly scoped assignment and sufficient context for each worker, and then reconciles their outputs. Every worker owns an isolated window and may use a different model or tool set, returning a compact structured report rather than its complete history. Claude Code defines such workers as Markdown files under `.claude/agents/`; frontmatter specifies `name`, a `description` containing triggers and required inputs, available `tools`, and the `model`, while the Markdown body becomes the system instruction. Limit tools according to least privilege, define a response schema that also serves as the stop condition, and request an “Obstacles Encountered” section. Experimental **agent teams** extend this arrangement with peer messaging and a task list shared among otherwise separate Claude Code sessions.

[↑ Back to question index](#contents)

#### Question AI-066

[↑ Back to question index](#contents)

#### Risks of concurrent agent execution

Concurrent agents can overwrite the same files, race for databases, ports, or branches, duplicate effort, and proceed from incompatible assumptions. They also multiply token consumption, encounter service limits sooner, and make failures harder to reconstruct. Reduce exposure by assigning file ownership explicitly, isolating workers in separate branches or worktrees, approving an interface contract before splitting frontend and backend work, limiting a team to roughly three to five members, and making one person or lead responsible for final integration.

[↑ Back to question index](#contents)

#### Question AI-067

[↑ Back to question index](#contents)

#### Shared mutable context

If several workers mutate the same code, notes, or state, each update can invalidate another worker's view, later writes may erase earlier ones, and authority becomes ambiguous. Prefer isolation with immutable exchange artifacts such as specifications, contracts, and reports. Where a common handoff file is necessary, make it append-only and assign ownership by section. Maintain a single authoritative task list and protect claims with locking; agent teams, for example, use file locks when workers take tasks.

[↑ Back to question index](#contents)

#### Question AI-068

[↑ Back to question index](#contents)

#### Synchronizing results from several agents

Coordination should flow through explicit contracts and persistent artifacts rather than informal conversation. Workers submit standardized results, after which the lead resolves overlaps and disagreements, integrates branches, and runs full-system tests and review. Task dependencies must prevent a consumer from beginning before its prerequisites exist. The Accelerator relies on approved artifacts with reconciliation by the developer; an agent-team lead waits for all assigned workers and synthesizes their findings.

**Lessons:** [Introduction to Subagents](../04%20Context%20Engineering/03%20Sub-Agents/01%20External%20Course%20Introduction%20to%20subagents/01%20External%20Course%20Introduction%20to%20subagents.md) · [Claude Code Agent Teams](../04%20Context%20Engineering/03%20Sub-Agents/02%20Claude%20Code%20Agent%20Teams/02%20Claude%20Code%20Agent%20Teams.md) · [Spec Kit Tasks](../03%20Spec-Driven%20Development/09%20SpecKit%20Tasks/09%20SpecKit%20Tasks.md)

[↑ Back to contents](#contents)

---

## 9. Model Context Protocol (MCP)

### Question AI-069

[↑ Back to question index](#contents)

#### What MCP is

The Model Context Protocol is an open interface through which AI clients discover external capabilities and information. A server advertises tools—and optionally resources and prompts—using descriptions and typed schemas that compatible clients such as Claude Code, Codex, or Cursor can consume. Common integrations cover GitHub, Playwright, Context7, Figma, and Supabase. Claude Code adds an HTTP or stdio server with `claude mcp add`, supports local, user, and committed project scope through `.mcp.json`, and provides `/mcp` for management.

[↑ Back to question index](#contents)

### Question AI-070

[↑ Back to question index](#contents)

#### MCP vs an ordinary API integration

A conventional API integration requires client-specific adapter code for every service. With MCP, the server declares its operations, allowing a model to invoke them through any compatible host without a new adapter for each client. Portability has a context cost: unless deferred discovery is supported, the descriptions and schemas of enabled servers consume tokens even when no tool is selected, and responses add further volume. Enable only integrations relevant to current work; a command-line utility is often more efficient for stable, direct operations.

[↑ Back to question index](#contents)

### Question AI-071

[↑ Back to question index](#contents)

#### Benefits for the AI tooling ecosystem

MCP makes an integration reusable across multiple clients, lets models discover operations through typed contracts, provides access to live documentation or business data, and allows teams to share centrally hosted connectors. The server boundary also gives authentication and authorization a defined place in the architecture.

[↑ Back to question index](#contents)

### Question AI-072

[↑ Back to question index](#contents)

#### MCP security risks

Connecting an unreviewed server can amount to executing third-party code with the user's credentials and access. Agents are inclined to trust advertised capabilities, while tool metadata and responses can carry **indirect prompt injection**. Excessively broad tokens permit exfiltration, and upstream behavior may change after an initial review. Prefer vendor-supported or internally audited servers, enforce an organizational allowlist, pin versions, and issue narrowly scoped credentials. Building a small internal connector is safer than adopting an unknown repository, and every server response should be processed as untrusted input.

**Lessons:** [Using MCP servers](../01%20Intro/04%20Using%20MCP%20Servers/04%20Using%20MCP%20Servers.md) · [Claude 101: MCP](../01%20Intro/02%20External%20Course%20Claude%20101/Claude%20101/04%20Customizing%20Claude%20Code/04%20MCP.md) · [Reducing MCP overhead](../04%20Context%20Engineering/01%20General%20practices/06%20Reducing%20the%20number%20of%20MCP%20servers/06%20Reducing%20the%20number%20of%20MCP%20servers.md)

[↑ Back to contents](#contents)

---

## 10. Security and Privacy

### Secrets and PII

#### Question AI-073

[↑ Back to question index](#contents)

#### Data that must not be sent to an LLM

Do not submit passwords, credentials, cryptographic keys, access tokens, or regulated production records. Personally identifiable information requires a valid legal basis and the necessary approval; NDA-bound material, contract-restricted data, and proprietary or client code likewise require explicit authorization. Health and financial information deserve particular care. A tool that runs locally may still send selected code and prompts to a hosted model, so local execution does not imply local inference. Classify the material first and confirm the provider's processing and retention terms before use.

[↑ Back to question index](#contents)

#### Question AI-074

[↑ Back to question index](#contents)

#### Working with secrets

- Store sensitive values in environment variables or a dedicated secrets service, not in prompts, repository instructions, task artifacts, logs, screenshots, or browser-delivered bundles. In Vite, every `VITE_*` value should be considered public.
- Keep `.env` and key material out of version control and block agent reads through deny rules and hooks.
- Provide the agent with short-lived, least-privilege tokens and isolate credentials by project.
- If exposure occurs, revoke or rotate the credential without delay.

[↑ Back to question index](#contents)

### AI-Generated Code Risks

#### Question AI-075

[↑ Back to question index](#contents)

#### Security risks of AI-generated code

Generated code can contain the same flaws as human-written code: injection paths, insufficient validation, authorization gaps, and unsafe deserialization. Additional patterns include embedded credentials, obsolete techniques reproduced from training data, permissive defaults such as unrestricted CORS or disabled TLS verification, and infrastructure roles broader than necessary. Tests generated from the same defective requirement may reinforce the mistake instead of detecting it.

[↑ Back to question index](#contents)

#### Question AI-076

[↑ Back to question index](#contents)

#### Insecure dependencies

Because model knowledge is historical and probabilistic, a recommendation may name a nonexistent package that an attacker can later register, a misspelling of a popular package, or a release with known defects. The first pattern is often called slopsquatting and the second typosquatting. Before adding any dependency, confirm that the package is real, identify its maintainer, examine the proposed version, license, and security advisories, pin an approved version, and run dependency analysis.

[↑ Back to question index](#contents)

#### Question AI-077

[↑ Back to question index](#contents)

#### Checking AI-generated code before merge

Review AI output as if it came from an unfamiliar contributor. Inspect the patch, execute existing tests, add coverage for missing cases, and run formatting, linting, type checking, SAST, credential detection, and dependency scanning. Human review remains required, though a separate reviewer agent with a clean context can provide an additional first pass. Verify in particular that the change did not relax tests or security checks simply to make CI pass. The developer who merges the patch retains responsibility for it.

[↑ Back to question index](#contents)

### Prompt Injection

#### Question AI-078

[↑ Back to question index](#contents)

#### Prompt injection

Prompt injection is crafted input intended to redirect model behavior away from the authorized task and toward an attacker's instruction—for example, a demand to disregard earlier rules. The weakness arises because operational instructions and ordinary data are represented together inside the model's context.

[↑ Back to question index](#contents)

#### Question AI-079

[↑ Back to question index](#contents)

#### Indirect prompt injection

In an indirect attack, the adversarial instruction is embedded in material the agent consumes rather than typed by the current user. It might appear in a README, source comment, issue, website, document, tool response, or MCP payload. Coding agents face particular exposure because they routinely ingest untrusted repository and external content while also possessing tools that can change state.

[↑ Back to question index](#contents)

#### Question AI-080

[↑ Back to question index](#contents)

#### Defenses against prompt injection

No single control eliminates prompt injection, so protection must use several independent layers:
- Grant only the access needed for the task: narrowly scoped tokens, read-only roles where possible, and no reachable secrets for an agent that handles untrusted input.
- Enforce tenant separation and access checks before retrieved or tool-provided content is exposed to the model.
- Place a trusted mediator around tool execution that checks the operation, target, arguments, filesystem paths, network destination, and consistency with the user's original request.
- Require a person to approve high-impact operations, and reject known-dangerous commands using deny policies and `PreToolUse` hooks.
- Isolate execution and restrict outbound networking to reduce the chance of exfiltration.
- Mark external material as data in a distinct section. This helps the model interpret it correctly but cannot be treated as a security boundary.
- Do not place untrusted content, sensitive private information, and an outbound communication channel within one agent's reach.
- Process especially risky input in a separate component that has neither secrets nor action tools nor network egress, and forward only a small validated result.
- Limit MCP servers and skills to reviewed allowlists, and continue treating their responses as untrusted.
- Before any model output is executed or published, validate it, inspect relevant diffs and logs, and monitor for behavior outside the expected workflow.
The focused security lesson and the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) provide a broader treatment.

**Lessons:** [Prompt injection defenses](../07%20Additional%20Themes/04%20Prompt%20Injection%20Defenses/04%20Prompt%20Injection%20Defenses.md) · [Structuring prompts](../02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29.md) · [Using MCP servers](../01%20Intro/04%20Using%20MCP%20Servers/04%20Using%20MCP%20Servers.md) · [Innowise Accelerator: security](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md) · [Lovable deployment](../06%20Applied%20Practices/03%20Deploying%20Lovable%20project%20in%20Google%20Cloud%20with%20help%20of%20AI%20CLI/03%20Deploying%20Lovable%20project%20in%20Google%20Cloud%20with%20help%20of%20AI%20CLI.md) · [Self-healing CI/CD](../06%20Applied%20Practices/04%20Self-healing%20CI-CD%20with%20Claude%20Agents%20Teams/04%20Self-healing%20CI-CD%20with%20Claude%20Agents%20Teams.md) · [Open-weight models: privacy](../05%20Advanced%20Techniques/03%20Using%20local%20LLM%20without%20powerful%20hardware/03%20Using%20local%20LLM%20without%20powerful%20hardware.md)

[↑ Back to contents](#contents)

---

## 11. Monitoring, Debugging, and Cost Control

### Question AI-081

[↑ Back to question index](#contents)

#### Tracking cost

Monitor consumption through the client and provider interfaces available to you, including `/status`, `/context`, a status line, `/cost`, usage reports, and administrative dashboards. Configure hard spending limits where possible and alerts before those limits are reached. The meaningful efficiency measure is **cost per task successfully delivered**, not the price of an isolated token. A subscription client may display an equivalent API list-price estimate rather than an amount that will actually be billed. Apply separate cloud budgets and daily reviews to infrastructure an agent can modify; in the case study, an automated change multiplied the cloud bill by six.

[↑ Back to question index](#contents)

### Question AI-082

[↑ Back to question index](#contents)

#### Signs of inefficient orchestration

Orchestration is inefficient when higher token use does not improve outcomes, workers repeat the same investigation or remain blocked on one another, or the lead completes assignments that should have been delegated. Other signals include frequent merge conflicts, repeated reintegration, premature worker exits, endless loops, and the use of a team for tiny or inherently sequential work. Exhausted quotas can leave agents idle, and if final integration consumes more time than concurrency saved, parallelization was a net loss.

[↑ Back to question index](#contents)

### Question AI-083

[↑ Back to question index](#contents)

#### Debugging failing AI workflows

- Begin with the conversation transcript and any per-step execution records.
- Reconstruct the precise environment at the failure: inspect the guidance and files loaded through `/context` or `/memory`, the tools exposed at that moment, and their returned data.
- In a clean session, repeat only the failing operation with identical inputs.
- Audit skill and subagent descriptions for incorrect activation, then inspect hooks and permission decisions that might have prevented progress.
- Correct the problem in the responsible specification, instruction, configuration, or tool and execute the affected stage again.
- For Claude Code skill-loading or configuration failures, collect diagnostics with `claude --debug`.

**Lessons:** [Status line](../04%20Context%20Engineering/01%20General%20practices/02%20Configuring%20the%20Statusline/02%20Configuring%20the%20Statusline.md) · [Caching and price](../04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md) · [Troubleshooting skills](../04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/Introduction%20to%20agent%20skills/06%20Troubleshooting%20skills/06%20Troubleshooting%20skills.md) · [AI-first case study](../06%20Applied%20Practices/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation/05%20Demo%20a%20single-handed%20Fullstack%20AI%20project%20implementation.md)

[↑ Back to contents](#contents)

---

## 12. Tool Selection and Standardization

### Question AI-084

[↑ Back to question index](#contents)

#### Choosing AI tools for a team

Evaluate competing tools with work that reflects the team's actual workload. Compare delivered quality, total cost and quotas, available models, contractual data treatment and security, enterprise features such as SSO, centrally managed settings and audit records, support for the IDE, terminal and CI, extension mechanisms including skills, hooks, MCP and subagents, and the portability of artifacts between products. Favor vendor-supported or internally approved options and run a limited pilot before broad adoption. The course currently demonstrates Claude Code, Codex, and Antigravity; select among them according to outcome quality, expense, limits, and fit with the delivery process. Repeat the evaluation regularly because capabilities shift within months.

[↑ Back to question index](#contents)

### Question AI-085

[↑ Back to question index](#contents)

#### Standardizing AI workflows

In the absence of common practice, developers repeatedly rebuild prompts and configuration, results vary, security controls develop gaps, and useful lessons remain personal. A standardized setup should:
- version repository memory, shared skills, subagent definitions, hooks, and other project configuration;
- establish a default delivery path such as Explore → Plan → Code → Commit or Spec Kit, adopting a framework like the Accelerator when appropriate;
- maintain an approved catalog of tools and MCP servers and apply organizational policy through managed settings;
- begin with a narrowly scoped pilot, measure its outcomes, and incorporate recurring corrections into shared skills;
- train users and subject common configuration to the same review process as production code.

**Lessons:** [Toolset](../01%20Intro/03%20Our%20Toolset%20as%20for%20Now/03%20Our%20Toolset%20as%20for%20Now.md) · [Introduction to frameworks](../04%20Context%20Engineering/04%20Frameworks/01%20Introduction%20to%20Frameworks/01%20Introduction%20to%20Frameworks.md) · [Sharing skills](../04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/Introduction%20to%20agent%20skills/05%20Sharing%20skills/05%20Sharing%20skills.md) · [Innowise Accelerator](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md)

[↑ Back to contents](#contents)

---

## 13. Innowise Accelerator

The Innowise Accelerator is a technology-aware operating framework for coding agents. It expresses engineering routines as commands, isolated workers, reusable skills, hooks, configuration, and durable artifacts. Instead of asking one conversation to carry an entire initiative, it moves through bounded stages that can each be inspected. The benefit is governed and auditable delivery, rather than unattended autonomy.

### Question AI-086

[↑ Back to question index](#contents)

#### Architecture and Principles

- The core chain is **command → agent → skill → persisted artifact and handoff → human selection of the following step**. The command opens the workflow, an agent works inside its own context and tool boundary, the skill supplies the method and output contract, and the artifact preserves the result.
- A stage finishes when its assigned responsibility is complete and proposes, but does not automatically start, the next stage. Every transition remains a human checkpoint.
- Handoff records identify completed work, modified files, assumptions, validation performed, and the suggested continuation.
- Specifications evolve as maintained artifacts. A manifest lets subsequent agents load only applicable material, and generated outputs identify the skill responsible for them.
- Natural-language skill instructions do not enforce security. Permissions, sandboxes, and `PreToolUse` hooks impose the actual restrictions, while shared configuration is reviewed as code.

[↑ Back to question index](#contents)

### Question AI-087

[↑ Back to question index](#contents)

#### Phases and Typical Flows

- **Lifecycle:** Understanding establishes and clarifies requirements; Planning chooses architecture, API and user-interface design, and an implementation sequence; Development manages an isolated worktree, coding, review, tests, and debugging; Finalization updates documentation, verifies the outcome, and closes the branch.
- **Feature path:** onboard the project → analyze requirements → resolve ambiguity → write the plan → pass a *human checkpoint* → implement → test → self-review → independent code review → verify → hand off.
- **Defect path:** reproduce and collect evidence → diagnose methodically → apply the smallest correction → run focused tests → review → verify. Any failed check routes the work back to diagnosis.
- Frontend and backend workers may proceed concurrently only after an API contract is approved and file ownership has little overlap. Artifacts carry coordination information, while the developer owns integration.

[↑ Back to question index](#contents)

### Question AI-088

[↑ Back to question index](#contents)

#### The `embacc` C++/Embedded Port

The `embacc` variant is related to, but distinct from, the Node/NestJS edition used in the workshop. It supports Claude Code, Codex, OpenCode, and Pi. Operational state is stored outside the working repository under `~/.embacc`, where `PROJECT.md` describes the project and each task's `STATE.md` provides the continuation point.
- **CLI surface:** `embacc setup .`, `embacc run <host> .`, `embacc doctor .`, `embacc refresh .`, `embacc reflect .`, and `embacc install … --dry-run`; repository-level shared configuration is installed only by explicit choice.
- **Capability groups:** onboarding and routing use `project-onboard`, `feature`, and `bug`; continuity uses `task-workspace` and `handoff`; requirements and design use `requirements-analyst`, `requirements-clarifier`, and `writing-plans`; delivery uses `coder`, `testing`, and `systematic-debugger`; assurance uses `self-review`, `code-reviewer`, and `verify`; pull-request handling uses `review-pr` and `pr-review-response`; reusable learning is captured through `stabilize`.

[↑ Back to question index](#contents)

### Question AI-089

[↑ Back to question index](#contents)

#### Adopting It

Adoption should begin with a genuine but constrained assignment isolated in a branch or worktree. Measure completed tasks, elapsed time relative to the team's normal method, dashboard-reported tokens or spend, retries, review effort, and operational failures such as incorrect skill routing, lost context, excessive permission requests, stack incompatibilities, or setup friction. The framework is easiest to introduce on a new codebase. Existing systems first require discovery and a credible test baseline.

**Lessons:** [Workshop: Innowise Accelerator](../06%20Applied%20Practices/02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md) · [Introduction to frameworks](../04%20Context%20Engineering/04%20Frameworks/01%20Introduction%20to%20Frameworks/01%20Introduction%20to%20Frameworks.md)

[↑ Back to contents](#contents)

---

## 14. Ten Principles of the Course

1. **AI amplifies expertise; it does not substitute for it.** The greatest benefit goes to people capable of evaluating the result.
2. **State the intended outcome plainly.** Wherever requirements are silent, the model must make a choice on your behalf.
3. **Persist decisions in artifacts.** Conversation history is not a reliable system of record.
4. **Keep one objective per conversation.** Compress history to pursue the same goal, and reset when the goal changes.
5. **Optimize context for relevance and sufficiency.** More tokens are not automatically better.
6. **Verify time-sensitive claims with current evidence.** A model's internal knowledge describes the past.
7. **Choose the smallest mechanism that solves the problem.** Escalate from a single agent to a subagent and then a team only when justified, and prefer a focused CLI over a large MCP catalog.
8. **Do not treat model instructions as access control.** Real enforcement comes from permissions, hooks, isolation, and infrastructure policy.
9. **Completion requires evidence.** A model saying that work succeeded is only an assertion until checks confirm it.
10. **Evaluate delivered outcomes.** Token rates, demonstration speed, and code volume are weaker measures than successfully completed tasks.

[↑ Back to contents](#contents)

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

[↑ Back to contents](#contents)
