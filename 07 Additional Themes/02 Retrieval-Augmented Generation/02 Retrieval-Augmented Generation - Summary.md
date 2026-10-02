# Summary: Retrieval-Augmented Generation (RAG)

RAG retrieves relevant material from an external knowledge source and inserts it into the model's context before generation. Use it when the corpus is larger than the context window, changes frequently, contains private domain knowledge, or must support citations. Pass context directly when the relevant material is already small and known.

A complete pipeline ingests and chunks sources, indexes text and metadata, retrieves candidates with keyword, vector, or hybrid search, applies authorization filters, reranks evidence, and asks the model to answer from that evidence. Evaluate retrieval separately from generation: the necessary source must be found, current, relevant, and authorized; the answer must be supported by it and cite it accurately. RAG can still fail through stale indexes, poor chunks, irrelevant matches, unsupported synthesis, or indirect prompt injection. Treat retrieved content as untrusted, enforce permissions before exposure, preserve provenance, and make the system abstain when evidence is missing.

