# Prompt Injection Defenses

Prompt injection occurs when untrusted text changes an LLM application's behavior in a way the system designer did not intend. The attack works because natural-language instructions and data are processed in the same model context. A user can inject instructions directly, or malicious instructions can arrive indirectly through a web page, repository file, issue, email, retrieved document, image, tool result, or MCP server response.

There is no single prompt that eliminates this risk. The practical goal is defense in depth: reduce what an injected instruction can reach, detect suspicious behavior, and prevent a model's text from directly authorizing consequential actions.

## Direct and Indirect Injection

### Direct prompt injection

The attacker places adversarial instructions in the user input. The text may ask the model to ignore previous rules, reveal internal data, change its role, or call a tool outside the user's legitimate request.

### Indirect prompt injection

The model reads adversarial instructions from content that appears to be data. For coding agents, common channels include:

- source files, comments, and generated artifacts;
- README files and dependency documentation;
- issue and pull-request text;
- logs, test output, and error messages;
- web pages and retrieved RAG chunks;
- tool descriptions and MCP responses.

Indirect injection is especially dangerous when the same agent can read private data, take actions, and communicate externally.

## Start With a Threat Model

Identify four things for each workflow:

1. **Untrusted inputs:** what content can an attacker influence?
2. **Sensitive assets:** which secrets, private files, customer records, or system prompts are reachable?
3. **Consequential actions:** which tools can write, deploy, purchase, send, delete, or change permissions?
4. **Outbound channels:** where could data be exfiltrated—HTTP requests, email, issue comments, logs, or tool calls?

The highest-risk design combines untrusted input, sensitive data, powerful tools, and an outbound channel in one unconstrained context. Break that combination architecturally.

## Layered Defenses

### Least privilege and capability boundaries

- Give the agent scoped, short-lived credentials.
- Prefer read-only access for analysis tasks.
- Allowlist tools, hosts, commands, and writable paths.
- Separate production from development credentials.
- Deny access to secrets the workflow does not need.

This is the most important layer because it limits impact even when the model follows a malicious instruction.

### Separate trusted instructions from untrusted data

Use explicit message roles, structured fields, and clear delimiters. Tell the model that retrieved or user-provided content is data and must not redefine the task. This improves instruction clarity, but it is not a security boundary: the model can still be influenced by content inside the marked section.

### Validate inputs and retrieved content

Apply size limits, accepted formats, content-type checks, and deterministic sanitization where appropriate. Remove active HTML or executable content when the use case does not require it. Scan retrieval corpora and external documents for suspicious instructions, but assume detection can miss obfuscated or novel attacks.

### Mediate tool calls outside the model

Do not let the model's decision alone authorize an action. A policy layer should compare the proposed tool call with the original user intent and enforce:

- permitted operation and target;
- argument schemas and path constraints;
- network allowlists;
- data classification rules;
- transaction and spending limits;
- approval requirements.

Deterministic checks are preferable when a rule can be expressed in code. A second LLM can help classify risky actions, but it is also susceptible to manipulation and should remain only one layer.

### Require human approval for consequential actions

Ask for explicit approval before deployment, deletion, permission changes, sending external messages, purchases, or access to sensitive data. Present the exact action and target, not a vague "continue?" prompt. Avoid approval fatigue by requiring confirmation only at meaningful gates.

### Isolate risky parsing

Use a restricted process or agent to read untrusted content and return a narrow structured result. It should have no secrets, no write tools, and no outbound channel. A separate privileged component can act on validated fields rather than on the original document's free text.

### Validate outputs

Treat model output as untrusted until checked. Validate schemas, escape content for its destination, verify citations, scan for secrets, and reject unexpected URLs or commands. Never execute generated code or shell text merely because it came from the model.

### Monitor and test

Log retrieved source identifiers, tool requests, policy decisions, approvals, and results without logging secrets. Test direct, indirect, encoded, multimodal, multi-turn, and RAG-poisoning scenarios. Include attacks that attempt data exfiltration or gradual policy drift rather than only the phrase "ignore previous instructions."

## Coding-Agent Example

Suppose an agent reviews a pull request from an external contributor. A comment in the repository tells the agent to read `.env` and upload it for "validation."

A resilient design does not depend on the agent recognizing the sentence as malicious:

- the review agent has read-only repository access;
- `.env` and credential paths are denied;
- outbound network access is restricted;
- the agent cannot merge or comment without approval;
- proposed commands are checked against an allowlist;
- review output is inspected before publication.

The injected instruction can still distort the review text, but it cannot reach the secret or perform the exfiltration path.

## Controls That Are Not Sufficient Alone

- "Ignore malicious instructions" in the system prompt.
- XML or Markdown delimiters.
- Hiding the system prompt.
- A blocklist of suspicious phrases.
- Asking the model whether content is safe.
- A single guardrail model.
- Manual review after an irreversible action has already occurred.

These controls may contribute to a layered design, but none removes the underlying confusion between instructions and data.

## Review Checklist

- What untrusted content reaches the model?
- Which secrets and tools are reachable in the same execution?
- Are authorization filters applied before retrieval and model exposure?
- Can a model response directly trigger a side effect?
- Which actions require exact human approval?
- Are tool arguments constrained and independently validated?
- Can the workflow exfiltrate data through links, requests, logs, or messages?
- Are security events observable without recording secrets?
- Have direct and indirect injection cases been tested?

## Related Course Material

- [Structuring Prompts](../../02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29.md)
- [Using MCP Servers](../../01%20Intro/04%20Using%20MCP%20Servers/04%20Using%20MCP%20Servers.md)
- [Providing AI with Up-to-Date Knowledge](../../04%20Context%20Engineering/01%20General%20practices/07%20Providing%20AI%20with%20up-to-date%20knowledge/07%20Providing%20AI%20with%20up-to-date%20knowledge.md)
- [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [OWASP LLM01: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

