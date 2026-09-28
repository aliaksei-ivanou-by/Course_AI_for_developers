# Summary: Introduction to Codebase Indexing for AI Agents

A codebase index keeps a searchable representation of files, symbols, relationships, history, and semantic meaning outside the model's context. For each question, it retrieves a bounded evidence set that the agent must verify in the current source tree. It does not load the entire repository into the prompt and does not replace tests or direct code inspection.

Use exact search for known strings and symbols, language or static-analysis tools for definitions and references, Git for history, and semantic retrieval for concepts or cross-repository questions. Hybrid retrieval is usually stronger than relying on one search method.

The lesson demonstrates indexing the large OpenClaw repository with Auggie and exposing Augment's `codebase-retrieval` tool through MCP to Codex or another compatible agent. Local mode follows the active workspace and edits; remote mode indexes selected default branches. Verify branch and index freshness, exclude sensitive or irrelevant files, and review storage, privacy, licensing, and current pricing before adoption.

The observed repository size, seven-minute indexing time, faster indexed response, and cache-read count belong to one recorded run. A fair evaluation pins the repository and agent configuration, separates cold indexing from warm queries, repeats trials, uses verifiable tasks, and measures correctness, latency, tool calls, tokens, total cost, tests, and review effort.
