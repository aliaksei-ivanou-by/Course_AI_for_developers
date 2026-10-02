# Summary: Prompt Injection Defenses

Prompt injection makes an LLM treat untrusted content as instructions. It can be direct user input or indirect content from files, web pages, issues, RAG results, tools, or MCP servers. No prompt or delimiter fully prevents it, so protection must be layered.

Map untrusted inputs, sensitive assets, powerful tools, and outbound channels. Then reduce impact with least-privilege credentials, read-only roles, tool and network allowlists, denied secret paths, authorization before retrieval, constrained schemas, deterministic policy checks, sandboxing, and exact human approval for consequential actions. Isolate untrusted-content parsing in a component with no secrets or action tools, and validate model output before executing or publishing it. Log decisions and test direct, indirect, encoded, multi-turn, multimodal, and retrieval-poisoning cases. Clear tags, phrase blocklists, hidden prompts, and guardrail models may help but are not security boundaries; the system must remain safe even when the model follows a malicious instruction.

