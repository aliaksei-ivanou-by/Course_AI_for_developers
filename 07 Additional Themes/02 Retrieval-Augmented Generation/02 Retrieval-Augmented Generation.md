# Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation, or RAG, combines information retrieval with language-model generation. Before the model answers, the system searches an external knowledge source, selects relevant passages, and places them in the model's context. The model then produces an answer grounded in that retrieved material.

RAG is useful when the available knowledge is larger than the context window, changes more often than the model, belongs to a private domain, or must be cited. It does not make the model inherently truthful: a RAG system can retrieve the wrong passage, omit decisive evidence, use stale content, or generate a claim unsupported by the retrieved text.

## The Basic Pipeline

A practical RAG system normally has two paths.

### Ingestion and indexing

1. Collect source documents and preserve their origin, version, and permissions.
2. Parse them into usable text and metadata.
3. Divide large documents into retrievable chunks.
4. Create search representations, such as keyword fields and vector embeddings.
5. Store the chunks and metadata in an index.
6. Refresh or remove entries when the sources change.

### Query and generation

1. Accept the user's question and identity.
2. Rewrite or decompose the query when useful.
3. Retrieve candidate chunks using keyword, vector, or hybrid search.
4. Filter by authorization, source, date, branch, language, or other metadata.
5. Rerank and select the best evidence that fits the token budget.
6. Ask the model to answer from the supplied evidence and cite its sources.
7. Validate the answer, citations, and any proposed actions.

The model sees only the selected chunks, not the entire knowledge base. Retrieval quality is therefore a first-class part of answer quality.

## Keyword, Vector, and Hybrid Retrieval

| Method | Strength | Typical weakness |
| --- | --- | --- |
| Keyword search | Exact identifiers, error codes, names, and rare terms | Can miss paraphrases and conceptual similarity |
| Vector search | Semantically similar language and paraphrases | Can miss exact symbols and return broadly related but irrelevant text |
| Hybrid search | Combines exact and semantic signals | More components and parameters to evaluate |

Code search often benefits from hybrid retrieval. A vector index can find conceptually related code, while keyword search preserves exact function names, file paths, ticket IDs, or compiler errors. Reranking can then reorder the combined candidates.

## Chunking and Metadata

Chunking determines what the search system can retrieve as a unit. Chunks that are too small lose definitions and surrounding contracts; chunks that are too large dilute the relevant part and spend more tokens.

Useful chunk boundaries follow the structure of the source where possible:

- a documentation section with its heading path;
- a function or class with its signature and containing file;
- a ticket with comments and status metadata;
- a transcript segment with speaker and timestamp.

Store metadata needed for filtering and provenance: source URL or path, document version, timestamp, repository branch or commit, tenant, access-control labels, language, and section hierarchy. Do not rely on the vector store alone to enforce authorization.

## RAG or Direct Context?

Pass context directly when the relevant material is small, known, and stable. Examples include a short file under review, a single error log, or a bounded specification.

Use retrieval when:

- the collection is too large to send every time;
- the relevant items are not known in advance;
- the content changes frequently;
- multiple users have different access rights;
- the answer must include verifiable provenance.

The simplest reliable mechanism is usually preferable. Adding a vector database to a ten-page knowledge base may increase cost and failure modes without improving results.

## RAG in Software Development

For a coding agent, retrieval may search source code, architecture notes, API documentation, tickets, commit history, runbooks, or previous incidents. The course already demonstrates related mechanisms:

- Augment Code uses a context engine to locate relevant code for prompt enhancement.
- Auggie exposes indexed codebase retrieval to other agents.
- Context7 retrieves current library documentation.
- NotebookLM grounds generation in a selected set of source documents.

These tools differ in indexing, storage, permissions, and freshness. Confirm which branch or document version was indexed before relying on a result.

## Security and Privacy

RAG creates both data-access and content-trust boundaries.

- Apply authorization before or during retrieval, not after the model has already received a forbidden chunk.
- Keep tenant and project data separated and test for cross-tenant leakage.
- Treat retrieved text as untrusted data that can contain indirect prompt injection.
- Do not place secrets in an index merely because the index is private.
- Preserve provenance so reviewers can inspect the original source.
- Define retention, deletion, residency, encryption, and provider-processing rules.

An agent that reads untrusted retrieved text and also has secrets, write access, and an outbound channel has a dangerous combination of capabilities. Limit tools and credentials independently of the prompt.

## Evaluating a RAG System

Evaluate retrieval and generation separately.

### Retrieval checks

- **Recall:** did the candidate set include the evidence needed to answer?
- **Precision or relevance:** how much of the retrieved context was useful?
- **Freshness:** was the correct current version retrieved?
- **Authorization:** could the requester legally access every returned chunk?

### Generation checks

- Is the answer supported by the retrieved evidence?
- Do citations point to the passages that support each claim?
- Does the system abstain when evidence is missing or conflicting?
- Does it distinguish retrieved facts from inference?

Maintain a representative evaluation set with expected sources, not only expected prose answers. Log query transformations, retrieved document identifiers, scores, model version, latency, and cost so regressions can be diagnosed.

## Common Failure Modes

- Indexing stale or incomplete content.
- Splitting definitions from the code or paragraphs they qualify.
- Retrieving semantically similar but factually irrelevant passages.
- Filling the context with too many weak matches.
- Generating unsupported conclusions from valid evidence.
- Showing citations that do not actually support the sentence.
- Applying permissions after retrieval instead of before exposure.
- Treating retrieved instructions as trusted system instructions.

## Related Course Material

- [Context-Aware Prompt Enhancement with Augment Code](../../02%20Meta-Prompting/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code/02%20Context-Aware%20Prompt%20Enhancement%20with%20Augment%20Code.md)
- [Providing AI with Up-to-Date Knowledge](../../04%20Context%20Engineering/01%20General%20practices/07%20Providing%20AI%20with%20up-to-date%20knowledge/07%20Providing%20AI%20with%20up-to-date%20knowledge.md)
- [Introduction to Codebase Indexing](../../04%20Context%20Engineering/01%20General%20practices/08%20Intro%20to%20codebase%20indexing/08%20Intro%20to%20codebase%20indexing.md)
- [Original RAG paper](https://arxiv.org/abs/2005.11401)
- [Azure AI Search RAG overview](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview)

