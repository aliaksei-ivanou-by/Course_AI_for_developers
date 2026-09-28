# Summary: Context Engineering for AI-Assisted Development

Context engineering controls what an AI coding agent can see, when additional evidence is retrieved, and which information should persist beyond the current conversation. The goal is not the largest or smallest prompt, but a sufficient, relevant, current, structured, traceable, and authorized working set.

Preserve stable conventions in reviewed project instructions, give each session one coherent objective, and monitor context occupancy without confusing it with cumulative usage, cache tokens, or final cost. Prompt caching reuses computation but does not remove cached material from context. Compact a continuing task, start a new session when the objective changes, and save requirements, decisions, progress, and validation evidence in durable project files.

Expose only task-relevant tools, defer large tool catalogs when supported, and bound their results. Ground changing APIs and versions in authoritative documentation and the target environment. For large repositories, combine exact, structural, historical, and semantic search; treat index results as candidates that must be verified in current source files and tests. Apply least privilege to tools, retrieval systems, and indexed data.

A reliable workflow is: load reviewed instructions, define the task contract, select minimal tools, retrieve focused repository and external evidence, implement narrowly, validate deterministically, record evidence and uncertainty, and begin a clean session for the next independent objective.
