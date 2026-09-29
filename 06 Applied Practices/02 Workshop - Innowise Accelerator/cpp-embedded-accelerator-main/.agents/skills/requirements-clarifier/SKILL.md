---
name: requirements-clarifier
description: "Resolve blocking ambiguity in C++/embedded requirements or design by separating facts the agent can verify from decisions the human must make, then asking only the current decision frontier with recommended defaults."
---

# Requirements Clarifier

Use when unknowns materially change architecture, interfaces, target behavior, safety, timing, resource use, or acceptance criteria.

## Method

1. Build a decision tree from the unresolved requirements.
2. Resolve **facts** yourself from repository evidence, tool output, PROJECT.md, specifications/tickets, and available documentation. Do not ask the user for information the environment can answer.
3. The **frontier** is the set of decisions whose prerequisites are already known. Ask only that frontier; do not ask downstream questions whose meaning depends on unanswered decisions.
4. For each human decision provide:
   - the question;
   - why it matters / what it blocks;
   - realistic options;
   - your recommended default and trade-off;
   - whether a safe reversible assumption is possible.
5. Record answers as confirmed requirements/decisions. Recompute the frontier until no blocking ambiguity remains.
6. Do not act on a costly or one-way assumption without explicit approval.

## Exit

Summarize confirmed decisions, safe assumptions, remaining unknowns, and requirements/spec files that should be updated. Suggest `requirements-analyst` or `writing-plans` as appropriate, then STOP.
