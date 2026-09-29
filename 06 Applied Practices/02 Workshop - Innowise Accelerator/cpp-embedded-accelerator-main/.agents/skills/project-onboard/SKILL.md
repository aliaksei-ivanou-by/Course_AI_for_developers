---
name: project-onboard
description: "Guided project onboarding for a developer joining or starting work on an outstaff project. Fill missing PROJECT.md context through a short interview, identify sources of truth, recommend useful external integrations such as Jira, Confluence, Context7, GitHub/GitLab and observability tools, configure approved MCP servers in hidden embacc state, and verify them without putting secrets in chat or the client repository."
---

# Project Onboard

Turn deterministic repository discovery into usable day-one project context. This is the human/context layer that `embacc setup` cannot infer.

## 1. Read before asking

1. Run `embacc config . --file PROJECT.md` and read the external project document.
2. Read repository evidence relevant to the missing sections.
3. Do not ask for facts already discoverable from code/build/CI/configuration.
4. Interview one decision at a time; offer a draft/default when evidence supports one.

Prioritize unresolved sections: **Purpose**, **Architecture**, **Sources of truth**, **Project rules**, and any missing target/debugging procedure.

## 2. Guided interview

Ask only what changes how the agent should work. Typical questions:
- What does the product/system do and who uses it?
- What are the important components and ownership boundaries?
- Where do tickets, requirements, design decisions, operational knowledge, and release notes actually live?
- Which constraints are non-negotiable: supported platforms/compilers, C++ standard, allocation/exceptions/RTTI policy, compatibility, generated code, threading/real-time rules, target/HIL expectations?
- What does "done" mean in this team beyond local tests?

Write each approved answer into the matching section of external `PROJECT.md`; never overwrite an already hand-maintained section without approval.

## 3. Context integrations — recommend, do not blindly install

After sources of truth are known, actively propose integrations that would materially reduce missing context. Do not wait for the developer to remember the word MCP.

Always consider these candidates:
- **Jira / Confluence** when the team uses Atlassian for tasks, requirements, decisions, runbooks, or specs;
- **Context7** when current third-party library/framework/API documentation matters;
- **GitHub / GitLab** when issues, PRs/MRs, discussions, releases, or CI metadata are important and the agent cannot already access them conveniently through an existing authenticated CLI;
- **Sentry / Grafana / Datadog / similar observability** when bug work depends on production diagnostics;
- one open-ended question: “What other tracker, wiki, CI dashboard, chat, internal docs, or engineering system should the agent be able to read?”

For each candidate explain the concrete benefit for this project and ask separately whether to configure it. Prefer read-only access by default. Do not install integrations merely because they exist.

## 4. MCP configuration

Project MCP configuration belongs at:

`<external_state_dir>/mcp/servers.json`

Get `<external_state_dir>` from `embacc config .`. Merge approved entries; never replace unrelated existing entries.

For a known integration, verify the current server/package/configuration from authoritative documentation before writing it; MCP packages and authentication flows change. Do not invent a plausible package name or stale credential URL from memory.

### Secrets rule

Never ask the developer to paste a password, API token, private key, or secret into chat. Write configuration with environment-variable references or a visible placeholder and tell the developer exactly which hidden config/file or environment variable to populate locally. Then verify the integration with a cheap read-only call without printing the credential.

## 5. Verification

A configured integration is not “done” merely because JSON parses. When the active agent supports that MCP integration, perform one cheap read-only operation and record the result in `PROJECT.md` Sources of truth or Known limitations. If the current agent cannot consume that integration directly, record it honestly rather than pretending it is active.

## 6. Finish onboarding

Summarize:
- project context filled;
- sources of truth;
- integrations configured / declined / still pending;
- remaining UNKNOWNs;
- recommended first workflow (`feature`, `bug`, or `review-pr`).

Then stop. Onboarding is allowed to be rerun later when the project or team changes.
