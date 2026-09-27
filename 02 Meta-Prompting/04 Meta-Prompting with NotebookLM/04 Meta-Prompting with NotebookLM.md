# Meta-Prompting with NotebookLM

NotebookLM can be used as more than a question-answering tool. In an AI-assisted development workflow, it can act as a source-grounded prompt enhancer: the developer provides raw thoughts, meeting notes, a long user story, an audio recording, or reference material, and NotebookLM transforms that material into a structured document for another tool or agent.

This lesson demonstrates two related outcomes:

- Turning informal product ideas into a product requirements document (PRD) or technical task
- Turning an external engineering reference into project principles that can later become a Spec Kit constitution

The central idea is to explain the intent naturally first, then use source-grounded generation to create a more precise artifact.

## What NotebookLM Does

NotebookLM is a Google service available at [notebook.google.com](https://notebook.google.com/). It organizes information into notebooks built from selected sources. After adding sources, a user can ask questions about them or generate derived artifacts.

Depending on the current product version and account, supported sources can include:

- Audio recordings
- Copied and pasted text
- Documents and presentations
- Files from Google Drive
- Web pages
- Public YouTube videos with captions

NotebookLM grounds its answers in the sources selected for the notebook. This makes it useful when the desired output should reflect specific discussions, documents, or reference material rather than only a model's general knowledge.

## From Raw Information to Structured Artifacts

A notebook can turn its sources into several useful formats, including:

- Answers to questions about the material
- Summaries and next steps
- Mind maps
- Briefing documents and study guides
- Reports and technical references
- Slide decks and other presentation material

For example, a team could add the recording or transcript of a meeting and ask:

```text
What decisions were made in this meeting?
What are the agreed next steps, owners, and unresolved questions?
```

The same source can then support a mind map, report, or slide deck based on what was discussed.

> **Privacy note:** Obtain the participants' permission and follow organizational data-handling rules before uploading meeting recordings, internal documents, or other sensitive material.

## NotebookLM as a Meta-Prompting Tool

Meta-prompting means using an AI system to improve or construct the instructions and artifacts that will guide another AI system.

NotebookLM supports this workflow because the initial input does not need to be a polished technical specification. A developer can provide:

- A voice recording explaining an idea
- A long user story written in informal language
- Meeting notes with product expectations
- Existing business documents
- Reference videos or web pages

The user can then ask NotebookLM to produce a PRD, technical task, engineering standard, or another structured document. That document becomes better input for a coding agent or a spec-driven development workflow.

```text
Raw intent and reference material
        ↓
NotebookLM sources and grounded analysis
        ↓
PRD, technical task, or engineering standard
        ↓
Reviewed instructions for a coding or specification agent
```

## Example: Creating a Product Requirements Document

A product idea often begins as an explanation rather than a formal specification. The developer may know what problem should be solved but may not yet know how to organize the requirements.

A practical workflow is:

1. Record the explanation or write the rough user story.
2. Add that material to a notebook as an audio file, document, or pasted text.
3. Ask NotebookLM to identify the product goal, users, expected behavior, constraints, and open questions.
4. Generate a structured PRD or technical task.
5. Review the result and correct assumptions before giving it to an implementation agent.

An example request is:

```text
Based only on the selected sources, create a product requirements document.

Include:
- problem statement and product goal;
- target users and primary use cases;
- functional and non-functional requirements;
- scope and explicit non-goals;
- constraints and dependencies;
- acceptance criteria;
- risks, assumptions, and unresolved questions.

Do not present missing information as fact. List it under unresolved questions.
```

The resulting PRD is still a draft. Source grounding improves relevance, but it does not make inferred requirements automatically correct.

## Adding Sources

The lesson demonstrates several ways to populate a notebook:

- Upload an audio recording or supported file.
- Import material from Google Drive.
- Paste a web address.
- Paste a public YouTube URL.
- Copy and paste text directly.

For YouTube sources, the user pastes the link instead of downloading and uploading the video. NotebookLM imports the transcript of a public video when captions are available; it does not use a private video's visual content as a source.

This makes public educational videos useful as input for reports and project guidance. Private, captionless, recently uploaded, or otherwise unsupported videos may fail to import.

## Demonstration: NASA-Inspired Engineering Principles

The lesson uses a public video about NASA-style software engineering practices as a reference source. The goal is not to implement a feature from the video. The goal is to extract reusable engineering principles that can govern future projects.

The workflow is:

1. Create or open a notebook.
2. Add the public YouTube video as a source by pasting its URL.
3. Open the report-generation area.
4. Choose or describe a suitable output such as an engineering standard or technical reference.
5. Generate a report based on the video.
6. Review the generated principles for applicability and accuracy.

Generic report templates such as a blog post, study guide, or briefing document are not the best fit for this goal. A custom engineering standard gives the generated artifact a clearer role.

An example instruction is:

```text
Based only on the selected source, create an engineering standard for an
AI-assisted software project.

Extract the concrete software-engineering principles discussed in the source.
For each principle, provide:
- a concise rule;
- its rationale;
- practical implications for implementation and review;
- a verifiable compliance check.

Separate source-backed rules from any additional recommendations.
```

The demonstration produces a substantial set of NASA-inspired project principles. These principles can be used as input to the next stage, but they should first be reviewed: rules designed for safety-critical systems may be excessive or inappropriate for a small commercial or experimental project.

## Moving the Principles into GitHub Spec Kit

GitHub Spec Kit supports spec-driven development workflows. One of its artifacts is a project constitution: a set of persistent principles and governance rules that guide later specifications, plans, tasks, and implementations.

The NotebookLM report can serve as draft input for that constitution:

1. Create or select the target project directory.
2. Initialize Spec Kit for the chosen coding-agent integration.
3. Review and reduce the generated engineering principles to the rules the project genuinely adopts.
4. Run the Spec Kit constitution workflow with the reviewed principles.
5. Inspect the resulting constitution and verify that its rules are concrete, relevant, and testable.

Conceptually, the agent receives an instruction such as:

```text
/speckit.constitution

Create the project constitution from the reviewed engineering principles below.
Preserve their intent, remove duplication, and express each principle as a
clear rule with a rationale and a verifiable quality gate.

[Reviewed principles from the NotebookLM report]
```

The command and integration details can change between Spec Kit versions, so the current Spec Kit documentation should be followed during setup.

## PRD Versus Project Constitution

The lesson connects two document-generation use cases, but their purposes differ.

| Artifact | Main purpose | Typical content | Scope |
| --- | --- | --- | --- |
| Product requirements document | Define what a product or feature should achieve | Users, use cases, requirements, constraints, acceptance criteria, risks | A product, feature, or initiative |
| Technical task | Give an implementation agent a bounded piece of work | Objective, affected behavior, constraints, deliverables, validation | One implementation task or change |
| Engineering standard | Convert reference material into reusable technical guidance | Rules, rationale, practices, and compliance checks | A team, project, or technical domain |
| Project constitution | Establish persistent principles that govern later development work | Non-negotiable rules, quality gates, and governance | The entire project |

NotebookLM can help draft all four, but the user must choose the intended artifact before generation. A detailed report is not automatically suitable as a constitution; it may need consolidation and prioritization.

## A Reusable Workflow

### 1. Capture the Intent

Explain the goal naturally through text or voice. Include product decisions and constraints that cannot be discovered elsewhere.

### 2. Add Supporting Sources

Add the relevant documents, recordings, web pages, Drive files, or public captioned videos. Exclude unrelated material so that retrieval stays focused.

### 3. Request the Correct Artifact

Name the expected document—PRD, technical task, engineering standard, or another format—and define its required sections.

### 4. Review Source Grounding

Check whether claims are supported by the sources. Mark assumptions, resolve contradictions, and add missing business intent.

### 5. Adapt the Output

Remove irrelevant or overly strict rules, resolve duplication, and rewrite vague statements as testable requirements.

### 6. Pass It to the Next Tool

Use the reviewed artifact as input for a coding agent or a specification tool such as GitHub Spec Kit.

### 7. Validate the Result

Review the final specification, constitution, or implementation. Meta-prompting improves the input but does not remove human responsibility for the result.

## Limitations and Risks

- Generated reports can contain mistakes or unsupported interpretations.
- A source may describe practices unsuitable for the current project's risk level.
- Private YouTube links cannot be imported as public YouTube sources.
- Meeting recordings and internal documents may contain confidential information.
- Large collections of unrelated sources can reduce focus.
- Product interfaces, artifact names, limits, and availability can change.
- A generated constitution can create unnecessary friction if every recommendation is promoted to a mandatory rule.

The safest pattern is to treat NotebookLM output as a structured draft backed by selected sources, then apply engineering and product judgment before adopting it.

## Key Takeaway

NotebookLM can serve as a source-grounded meta-prompting layer between informal human thinking and structured AI-assisted development. It can turn recordings, rough user stories, documents, and public captioned videos into PRDs, technical tasks, reports, and engineering standards.

The lesson's demonstration extends this idea by extracting NASA-inspired engineering principles from a public video and passing the reviewed result into GitHub Spec Kit as the basis for a project constitution. The value comes from the complete pipeline: capture intent, ground it in sources, generate the right artifact, review it, and only then use it to guide development.

## Further Reading

- [Add or discover sources in NotebookLM](https://support.google.com/gemininotebook/answer/16215270)
- [Use chat in NotebookLM](https://support.google.com/gemininotebook/answer/16179559)
- [Generate reports in NotebookLM](https://support.google.com/gemininotebook/answer/18323649)
- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [Spec Kit guidance for project constitutions](https://github.com/github/spec-kit/blob/main/docs/guides/existing-projects.md)
