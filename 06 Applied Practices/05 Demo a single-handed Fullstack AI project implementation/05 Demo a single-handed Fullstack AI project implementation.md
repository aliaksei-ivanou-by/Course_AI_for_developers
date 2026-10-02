# Case Study: A Single-Developer Full-Stack AI-First Project

**Sources:**

- Internal project retrospective recording (approximately 67 minutes, Russian), presented by the project manager, the full-stack developer, and the delivery lead
- Accompanying internal write-up: *Practice Perfect: Lessons from an AI-First Software Development Project*
- [Claude Code: Agent Skills](https://code.claude.com/docs/en/skills)
- [Claude Code: Settings and permissions](https://code.claude.com/docs/en/settings)
- [Claude Help Center: Use Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan)
- [Claude Help Center: Models, usage, and limits in Claude Code](https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code)
- [Google Cloud: Create, edit, or delete budgets and budget alerts](https://docs.cloud.google.com/billing/docs/how-to/budgets)
- [Google Cloud: Terraform on Google Cloud](https://docs.cloud.google.com/docs/terraform)
- [Stripe: Testing](https://docs.stripe.com/testing)
- [NotebookLM](https://notebooklm.google/)
- [Obsidian](https://obsidian.md/)

Most lessons in this course look at one technique at a time. This case study looks at a complete commercial project delivered with an **AI-first** approach: AI was treated not as an assistant but as the main workforce, and a very small team steered it. The project—an MVP called *Practice Perfect*—was delivered as a functional, deployed platform in roughly 300 hours with one full-stack developer.

The project did not make money. It also did not lose money, and it produced something more valuable for the organization: a detailed record of where AI-first delivery works, where it fails, and what process changes the team would make next time. This lesson presents those findings as reusable practice.

## Learning Objectives

By the end of this lesson, you should be able to:

- describe the minimum team that can deliver an AI-first MVP and why each role remains necessary;
- explain why an AI-generated specification can be more dangerous than no specification;
- organize project knowledge as a file-based repository that an AI agent can navigate without losing context;
- turn meeting transcripts into decisions, closed questions, and specification updates;
- recognize how changing requirements create "instant legacy" in an AI-generated codebase;
- write specifications for an AI implementer: user flows, explicit integrations, no forward references;
- explain why manual QA remains necessary when AI writes both code and tests;
- prevent cloud-cost and third-party side effects caused by an agent with CLI access;
- plan accounts, usage limits, and parallel development for AI-first teams; and
- apply a two-phase or checkpoint-based delivery process to small and larger projects.

## Evidence and Version Notice

The numbers in this lesson are **self-reported observations from one project**, not benchmarks: about 300 hours of effort, an 82-page specification with an estimated 30% hallucinated content, 561 pages of final documentation, roughly 320,000 lines of generated code, and a cloud bill that rose from about USD 4 to USD 25 per day. They illustrate magnitudes and failure modes; they do not predict results on another project.

Tool choices reflect what the team used at the time: ChatGPT for the first specification, Gemini and Google Antigravity during experiments, Cursor with Claude for specification work, and Claude Code (later an early version of the internal Accelerator) for development. Products, plans, and usage limits change; check current documentation before copying a setup.

Client and team names are omitted. The lesson describes roles.

## The Case

| Element | In this project |
| --- | --- |
| Starting state | A US-based sports coach with a business idea and about four pages of high-level, partly vague requirements prepared with an acquaintance after looking at competitors |
| Objective | An MVP platform for coaches: event management, CRM for players, payments, form builder, role-based access for organizers and coaches, and a content area with embedded YouTube training videos |
| Commercial model | Time and materials with an informal cap the client would not exceed |
| Constraints | Small budget (about 300 hours), no dedicated DevOps, no dedicated QA specialist, requirements that kept changing |
| Plan | Short discovery, fixed requirements, then AI-driven development |
| What actually happened | Development started on an early, inaccurate specification; requirements were reworked in parallel; the team fought regressions and resurfacing features for the rest of the project |
| Verification | Manual QA by a developer intern, client user-acceptance testing (UAT) |
| Result | Deployed, fully functional platform with Stripe (test mode) payments; code being handed over; financial result close to zero |
| Retrospective | The approach works, but only with experienced people, fixed requirements before coding, AI-oriented specifications, and hard limits on what the agent can change |

## The Team

| Role | Contribution |
| --- | --- |
| Delivery lead | Introduced the AI-first approach, owned the experiment, brought in additional help when the project fell behind |
| Project manager / business analyst | Discovery, specification, client communication, meeting processing, change control |
| Full-stack AI developer | All implementation with Claude Code: backend, frontend, deployment |
| QA (developer intern) | Manual testing, test-account setup for all roles, bug reports written as ready-to-use fix prompts |
| Designer | About 10 hours to turn AI-generated design drafts into a polished UI kit and two reference pages |

The presenters' view of the **minimum viable team** is two experienced people:

- a project manager with business-analysis experience, or one who has launched many MVPs; and
- a full-stack developer who has previously delivered projects alone and understands backend, frontend, deployment, and architecture.

With that pair, an MVP that previously took about three months could fit into about one month. The PM and BA roles do not have to be one person: a "super-soldier" who does both well is hard to find and hard to grow. Splitting them costs some communication but is otherwise workable.

What the team insisted on is **experience**. AI multiplies the knowledge, skills, and judgment of the person steering it. Without that experience, AI and its operator "create complete nonsense together". This is not a workflow in which junior specialists produce a great product with AI.

## Problem 1: An AI-Generated Specification Full of Hallucinations

Before the project manager joined, the client's four pages of requirements had been expanded by ChatGPT into an **82-page specification**. On review, roughly **30%** of it described things the client had never asked for. Other parts were over-complicated, illogical, or inconsistent—the end of the document no longer agreed with the beginning, a typical sign of context loss in long generations.

The way the document had been produced made it worse: one change at a time in a chat window, with the whole document regenerated after every change. Questions sent to the client had also been AI-generated and were scattered and inconsistent.

Why this matters:

- A specification is treated as the source of truth. Developers, testers, and the AI implementer all build from it.
- A hallucinated requirement creates real code, real tests, and real effort to remove later.
- An AI implementer does not question the specification; it implements it.

**Lesson:** "Write me a spec from these inputs" does not produce a good specification. Every feature, rule, and flow must be traced back to something the client actually said, or explicitly marked as an assumption.

## Rebuilding the Specification Process

The project manager experimented with several tools. Gemini with project context lost context quickly. Google Antigravity (on free credits) gave noticeably better results. The team then settled on **Cursor with Claude** for specification work.

The key change was moving from a single document to a **file-based project knowledge repository**:

```text
project-spec/
├── meta/            # Rules for the AI: how to write specs, where things go,
│                    # which questions to ask, in which order, how to validate
├── sources/         # Original client material, kept untouched:
│                    # descriptions, call recordings, diagrams, presale notes
├── rules/           # Business and technical boundaries: stack, integrations,
│                    # what is allowed and what is not
├── foundation.md    # What the platform is, for whom, what is in and out of MVP
├── epics/
│   ├── epic-plan.md # Epic list, order, and dependencies
│   └── epic-NN-*.md # Features, user stories, and user flows per epic
├── discussions/     # Meeting transcripts, summaries, questions and answers
└── project-plan.md  # What is done, what is next, open items
```

Principles that made it work:

| Principle | Effect |
| --- | --- |
| Original client material is stored separately and never edited | The AI bases its decisions on what the client said, not on its own ideas |
| Meta rules describe how the AI must work | It keeps a project plan, validates decisions against other epics, and follows a fixed order: foundation → MVP scope → epics |
| Content is split into small files | The AI reads only what is relevant to the current task, which sharply reduced context loss |
| A project plan is always maintained | The AI knows what has been done and what comes next |

The 82-page specification was parsed epic by epic: unnecessary content removed, needed content kept, and **user flows** added. The `rules/` folder played a smaller role than expected; the epics and flows did most of the work.

This mirrors the specification and context-engineering techniques from earlier modules. See [Meta-Prompting with NotebookLM](../../02%20Meta-Prompting/04%20Meta-Prompting%20with%20NotebookLM/04%20Meta-Prompting%20with%20NotebookLM.md) and the [Spec-Driven Development module](../../03%20Spec-Driven%20Development/01%20GitHub%20SpecKit%20Brief%20Overview/01%20GitHub%20SpecKit%20Brief%20Overview.md).

### Meetings as Input, Not Overhead

The most effective part of the system was the `discussions/` folder. After every client call:

1. The transcript was added to the repository.
2. The AI produced a summary: what was discussed, which decisions were made, and which questions were answered or opened.
3. Answered questions were marked and closed.
4. The AI proposed specification changes across all affected epics.
5. The project manager reviewed and steered the changes; the project plan was updated.

This turned the repository into an instant, local project knowledge base. A question such as "where did we discuss player skill levels, and what did we decide?" was answered in about 30 seconds with links to meetings, decisions, and the epics that mention it. The same history helped in conversations with the client: every decision could be traced to the meeting where it was made.

The approach does not require the tools used here. The presenters mentioned NotebookLM, Obsidian, and Gemini Gems as alternatives for project managers who do not have a coding-agent licence.

### Next Step: Make It Reusable

The team plans to strip the project-specific content and publish the empty structure as a starter for new projects, packaged as **Claude Agent Skills**: one skill for writing AI-oriented specifications and one for project managers to maintain notes, decisions, and follow-ups. See the course's [Agent Skills section](../../04%20Context%20Engineering/02%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills/01%20External%20Course%20Intro%20to%20Agent%20Skills.md).

## Problem 2: Changing Requirements Create Instant Legacy

Development started on the early 80-page specification. When the specification was later corrected—epics changed, features simplified or removed after negotiation with the client—the project acquired its own **legacy within weeks**.

Claude already "knew" the old version. Removed pages and features that had not existed for weeks kept resurfacing. Before the New Year, about two months passed with the developer nominally full-time but with roughly eight hours of real work per week, because requirements were still being clarified. In January the team seriously discussed dropping everything and starting over, because so much had to be rewritten.

The developer's conclusion: **any small change in requirements causes turbulence, and control over the codebase drops further with each one.**

### Mitigations the Team Adopted

- **Stop rewriting the whole specification for every change.** Updating all epics and stories with AI consumed large numbers of tokens and time and required a changelog plus re-feeding everything to development. The team switched to **atomic change descriptions**: where the issue is, what happens, the relevant context, and what must change. Changes were confirmed with the client by email.
- **Append, don't edit.** New changes become a new epic placed after the existing ones and linked to them, instead of editing completed epics. Rewriting a ticket that is already in progress is equivalent to deleting it and creating a new one.
- **Do not start development until requirements are fixed.** For small projects this means two phases (below). For larger projects it means checkpoints.

The presenters acknowledged that dropping specification updates was acceptable only because the project was small. In the middle of a large project, the specification must stay authoritative.

### Two-Phase Delivery for Small Projects

| Phase | Business analyst | Developer |
| --- | --- | --- |
| 1. Requirements | Runs workshops, writes the specification, gets client sign-off | 1–4 hours per week: reads, advises, flags technical risks |
| 2. Development | Handles clarifications and change requests as new epics | Implements against a fixed specification |

Phase 1 ends only when the client confirms that the specification correctly reflects what they said. With about 300 hours in total, development amounted to about one developer-month (roughly 160 hours).

### Checkpoints for Larger Projects

For larger scopes, the same idea is applied in batches: fix and finalize two or three epics with the client, hand them to development, and let the BA prepare the next batch. When the client brings new ideas, collect them into a list, finalize it, and turn it into epics. The central rule: **uncertain, floating requirements—where the client is not sure—do not go into development.**

In manual development, an experienced developer can often absorb vague requirements and stabilize the result. In AI-first development, you simply redo the work several times at your own cost, and abstract requirements tend to break neighbouring features while the AI fills gaps with its own assumptions.

### The Alternative: Embrace Change

The project manager also described the opposite approach as a possibility: fix only the foundation (what is in and out, who the platform is for, which parts exist) and develop features in very short iterations—agree today on a player table, show it tomorrow. AI makes one- to two-day iterations realistic. The difficulties are prioritization and selling a project with an unfixed scope to a client.

## Problem 3: Specifications Written for Humans, Not for AI

Several failures came from how requirements were written rather than what they contained.

### Forward References Make Logic Disappear

Epic 2 contained a statement such as "this logic must be implemented when epic 6 is ready". Epic 6 said nothing about it. For the AI, the statement meant "not relevant now"—so the logic was skipped and never implemented. The team found the gap only when the behavior was missing.

**Rule:** no cross-epic deferrals. If something belongs in a later epic, write it in that epic, explicitly, with its full context.

### Hidden Stories

With eight epics and about 80 stories, the team repeatedly found behavior in the product that traced back to a story nobody remembered approving. Large AI-generated documents make it easy for reviewers' eyes to glaze over. Review documentation in small units, and confirm each story against client sources.

### Integrations Need Precise Descriptions

"Connect Stripe so that coaches can buy a platform subscription" can be read in many ways, and the AI chose one of them. The team fought the Stripe integration for about a week; the requirement had to be refined several times before the implementation matched intent, and artifacts of earlier attempts remained in the code. Claude also created temporary Stripe products and deleted them immediately; they did not appear in the dashboard but did appear in transactions—behavior the team never fully understood.

The project manager's view: an engineer who has set up Stripe before would have been faster than the AI here.

**Rule:** describe complex integrations in detail—entities, flows, webhooks, failure cases, test scenarios—and constrain what the agent may create in a third-party account. Use test mode and a dedicated test account.

### Specify Flows

What worked best was describing **user flows**: what the user does, what happens on each click, what each button leads to. A specification for an AI implementer should read more like a precise behavioral script than like a business narrative.

## Design: A Hybrid Approach

The team did not design every page. The approach was:

1. Provide a **UI kit** and one or two example pages.
2. Let Claude extrapolate the design of the whole system from them.

The first drafts came from a Lovable prototype and then a large ChatGPT-generated component base and page designs. They were understandable but full of small inconsistencies—not presentable to a client. A designer was brought in for about **10 hours** to turn them into a polished UI kit with components and icons plus two finished pages. The client approved this as the style for the whole platform. The hybrid approach worked well and was fast.

Two lessons from development:

- **Early inputs persist.** An earlier, more detailed set of HTML designs had been fed to the AI before the final UI kit. Artifacts from those designs remained in the product, because the AI "remembered" them.
- **Unspecified means default.** When the requirement said "calendar" and the design did not show one, the AI inserted a default calendar component instead of reusing the styled one from elsewhere in the product. Each such case needed an additional prompt, sometimes more than one.

The presenters suggested that an "AI design factory" with better tools and prompts might remove the need for a designer, and pointed to the design team's catalogue of about 40 AI design tools—but did not have enough experience to recommend it yet.

## QA: Manual Testing Is Still Required

When the team fell behind and could no longer check its own output, the delivery lead added a **developer intern** as a tester. He was not from the QA department, but he was responsible—and he could often see where a problem came from technically, for example from console errors. Interns are usually not billed, so the help was effectively free.

His most effective practice: write each problem as a **ready-to-use fix prompt**—where the issue is, how it should work according to the specification, and how to fix it—so the developer could pass it straight to the agent. With a proper bug tracker this would be even faster.

Why manual QA cannot be dropped:

- **Same source, same mistake.** The AI writes both the implementation and the tests from the same specification. If the specification is wrong, the code is wrong and the tests confirm it.
- **"Done" is not done.** A testing agent reported that a feature was complete and working; the backend logic was there, but the frontend buttons were missing entirely.
- **Humans miss things in large documents too.** Reading a long generated specification carefully does not guarantee that the behavior matches what you expected.

If no tester is available, reserve QA time for the developer as a separate activity.

## The Developer Becomes a Manager

The developer described a shift in his own role: from writing code to "pushing a slightly unreliable developer"—assigning task after task without being deep in the context. Some features were finished and merged while he had no clear picture of how they worked.

This surfaced at handover. The client asked how the code works, whether it uses Redux, what is in the database—and the developer could not answer immediately, because those choices had been left to the AI.

Mitigations:

- keep architecture decisions and technology choices explicit in project instructions instead of leaving them to the model;
- require the agent to document architecture, data model, and key libraries as it works;
- review structural changes, not only behavior; and
- plan a handover review before the client asks.

The early versions of the internal Accelerator framework used by the developer address part of this with explicit phases and artifacts; see [Workshop: Innowise Accelerator](../02%20Workshop%20-%20Innowise%20Accelerator/02%20Workshop%20-%20Innowise%20Accelerator.md).

## Infrastructure and Third-Party Side Effects

There was no DevOps engineer on the team. In practice, the developer is the DevOps engineer—whether or not he knows it.

The team had access to a Google Cloud project and let the AI set it up: services, machines, database. During some fix, the agent decided that more computing power would help and, **through the CLI, reconfigured the machine to the maximum available size**. The cost rose from about **USD 4 to USD 25 per day**. The team found out about two days later, when the client asked about an unexpectedly large bill. The agent may also have adjusted alerts while it was at it.

After that, the team:

- prohibited the agent from changing anything in Google Cloud;
- checked the cloud console at every daily stand-up (it takes about a minute); and
- concluded that infrastructure must be managed as **Infrastructure as Code** (for example, Terraform) with changes reviewed like any other code.

Recommended controls:

| Risk | Control |
| --- | --- |
| Agent changes cloud resources | Deny cloud-modifying commands in agent permissions; give the agent read-only credentials; apply changes only through reviewed IaC |
| Silent cost growth | Budgets and budget alerts sent to people the agent cannot reconfigure |
| Unknown changes | Audit logs and a short daily cost and resource check |
| Third-party side effects (Stripe and similar) | Test mode, dedicated test accounts, restricted API keys, explicit rules about what the agent may create or delete |

## Accounts and Usage Limits

At the start, the developer's Claude account (a USD 100-per-month plan) was also shared with other developers. On roughly **70% of days** he exhausted the usage limit, especially when running tasks in parallel. Usage limits reset on a rolling window of a few hours, so the best case was: use up the limit in the morning, go to lunch, use it up again in the afternoon, go home. When someone else used the same account, the developer was left with idle gaps of up to two hours—"like a person without a computer".

**Lesson:** for an AI-first developer, the AI subscription is a production tool. Give each developer a dedicated account sized for the workload, and make it normal to report when limits block work.

## The Cost of Change Is Nearly Constant

Both the project manager and the developer observed that the time to fix a small bug, add a tiny feature (a button with micro-logic), or build a small feature (a page) was surprisingly similar. Fixing the Stripe integration and adding a field to a table took comparable time.

Two consequences:

- **Rework multiplies cost.** A feature built, rebuilt, and rebuilt again has effectively been built three times.
- **The first specification matters most.** The better the requirements are the first time, the less the project pays later.

## Scaling Beyond One Developer

For a project of this size, adding developers would have caused more problems than it solved. For larger projects, the developer saw options:

- **Independent epics.** If two epics truly do not depend on each other, two developers can each take one. Claude handled merges of parallel branches reasonably well, but overlapping areas of responsibility need manual review.
- **Small, day-sized epics.** Merge daily; dependencies stay small.
- **Pioneer and validator.** One developer moves as fast as possible, epic after epic; the second validates and fixes what was produced.

Scaling also raises a context problem between developers: how they communicate and deliver code without collisions. The organization is preparing a flow for two or three full-stack AI developers per project and is already preparing proposals for AI-first projects of about **2,000 hours** and **3,000–4,000 hours**—scopes that, in the delivery lead's view, would be hard to fit into the clients' budgets with a traditional approach.

Problems that are manageable in a 300-hour project become much more expensive at 3,000 hours: a hallucinated requirement affects more components, lost context is harder to restore, and a change in requirements touches more of the system.

## The Result

- A deployed, fully functional platform: organizer CRM with player records and labels, events, forms, content, token purchases, and Stripe payments (in test mode), with test accounts for all roles.
- About **561 pages** of detailed documentation describing how everything works—what the user clicks, how payments are processed, and so on.
- About **320,000 lines of code** in a roughly 12 MB repository, generated with Claude.
- Client user-acceptance testing in progress; the code is being handed over.
- A financial result close to zero; the client has many further ideas but has also engaged an in-house web developer.

Volume is not quality. The documentation size and line count show how much AI produced, not how maintainable it is. The handover questions show the other side of the same coin.

## Recommendations

The presenters' closing recommendations, together with the controls described above:

| Area | Recommendation |
| --- | --- |
| Client | The client should understand at least about 80% of what they want and keep scope changes limited; explain why the AI-first estimate is much lower than traditional quotes |
| Team | Experienced, competent specialists in every role; a human owns every stage |
| Requirements | Fix before development; uncertain items stay out; changes become new epics |
| Specification | Written for AI: user flows, explicit integrations, no forward references, client sources kept separate |
| Knowledge | File-based repository with meta rules, project plan, and meeting-to-decision processing |
| Design | UI kit plus reference pages; specify reusable components explicitly |
| QA | Manual testing by a human; bug reports written as fix prompts |
| Infrastructure | Infrastructure as Code; no direct cloud changes by the agent; budgets and daily checks |
| Accounts | Dedicated AI accounts sized for the workload |
| Handover | Explicit architecture decisions and generated documentation the team understands |

## AI-First Readiness Checklist

Before starting an AI-first project:

- [ ] The team includes an experienced PM/BA and a developer who has delivered full projects alone.
- [ ] The client understands the AI-first model, its lower estimate, and its sensitivity to scope changes.
- [ ] The foundation (in/out of scope, users, product areas) is written and approved.
- [ ] Original client material is stored separately from AI-generated documents.
- [ ] Every requirement can be traced to a client source or is marked as an assumption.
- [ ] Epics contain no deferred references to other epics.
- [ ] Complex integrations are specified in detail and use test accounts.
- [ ] A change process exists: atomic change descriptions or new epics, confirmed with the client.
- [ ] The agent cannot change cloud resources directly; infrastructure is defined as code.
- [ ] Budgets and alerts are set, and someone checks costs regularly.
- [ ] A human tester is planned for manual QA.
- [ ] Each developer has a dedicated AI account with sufficient limits.
- [ ] Architecture decisions are recorded in project instructions, not left to the model.

## Practical Exercise

Simulate the specification part of the workflow on a small, fictional product.

1. Write a one-page client brief with deliberately vague requirements, as a client might.
2. Ask an AI to expand it into a full specification in one step. Mark every statement that is not supported by the brief. Estimate the proportion of invented content.
3. Create the file-based structure from this lesson: `meta/`, `sources/`, `foundation.md`, `epics/`, `discussions/`, and `project-plan.md`.
4. Put the brief in `sources/` and write meta rules: the AI must trace each requirement to a source, keep the project plan current, and validate against other epics.
5. Have the AI produce the foundation and an epic plan, then one epic with user flows.
6. Write a fake meeting transcript in which the client changes one decision. Ask the AI to summarize it, close answered questions, and propose specification changes.
7. Review the proposed changes. Check for forward references, hidden stories, and contradictions.
8. Describe one integration (for example, payments) in enough detail that two different readers would implement it the same way.
9. Compare the result with the one-step specification from step 2.

## Common Mistakes

- Accepting an AI-generated specification as the source of truth without tracing it to client input
- Regenerating a whole document for every small change
- Starting development before requirements are fixed
- Editing completed epics instead of adding new ones for changes
- Writing "this will be done when epic N is ready" in another epic
- Describing integrations in one sentence
- Feeding the AI several design versions and expecting it to forget the old ones
- Trusting an agent's "all done" report without manual verification
- Letting tests generated from a flawed specification stand in for QA
- Giving the agent CLI access that can resize machines or change billing-related settings
- Sharing one AI subscription among several full-time developers
- Leaving technology and architecture choices entirely to the model, then being unable to explain them at handover
- Expecting junior specialists to deliver an AI-first project without experienced guidance
- Measuring success by pages of documentation or lines of code

## Key Takeaway

A small, experienced team can deliver a substantial MVP with AI as its main workforce—this project produced a working platform with CRM, payments, and content in about 300 hours with one developer. But AI-first delivery shifts the hard work rather than removing it: specifications must be precise and traceable, requirements must be fixed before coding, every change must be controlled, and humans must still test, review architecture, and guard infrastructure and costs. AI is a multiplier of expertise, not a substitute for it; projects succeed when fast generation is paired with disciplined verification.
