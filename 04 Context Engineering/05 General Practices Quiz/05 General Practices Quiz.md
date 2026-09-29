# Context Engineering General Practices Quiz

**Minimum grade to pass:** 70%  
**Attempts allowed:** Unlimited  
**Number of questions:** 12  
**Question type:** Single choice

## Questions, Answers, and Feedback

### 1. Why is web search not treated as a guaranteed replacement for a documentation MCP such as Context7?

- A. Web search may be unavailable, provider-dependent, or require paid search API access.
  - **Feedback:** Correct. The lesson explains that web search is not universally available and may require services such as paid search APIs.
- B. Web search prevents agents from reading private repository documentation.
  - **Feedback:** Incorrect. Web search generally cannot access private docs, but it does not “prevent” private documentation access through other mechanisms.
- C. Web search can only be used for frontend libraries and not infrastructure tools.
  - **Feedback:** Incorrect. Web search can be used for many domains; the issue is not limited category support.
- D. Web search always returns older documentation than a model's training data.
  - **Feedback:** Incorrect. Web search can find current information, but availability and cost are the concerns.

**Correct answer:** A. Web search may be unavailable, provider-dependent, or require paid search API access.

### 2. What is a context clash?

- A. A conflict between previous instructions or goals and the current task
  - **Feedback:** Correct. Earlier goals, examples, or directions may interfere with the new task and weaken the AI’s response.
- B. A technical error that prevents an AI model from opening a chat
  - **Feedback:** Incorrect. A context clash concerns conflicting information inside a conversation, not a failure to access the chat.
- C. A delay caused by running several AI agents at the same time
  - **Feedback:** Incorrect. Context clash is related to competing instructions and examples, not the number of active agents.
- D. A situation where the AI does not have enough conversation history
  - **Feedback:** Incorrect. The problem is usually irrelevant or conflicting history rather than insufficient history.

**Correct answer:** A. A conflict between previous instructions or goals and the current task.

### 3. In the comparison without Auggie MCP, what did the agent have to do?

- A. Use Context7 to generate new project documentation before answering.
  - **Feedback:** Incorrect. Context7 was used later for external documentation, not for direct repository exploration in this comparison.
- B. Refuse the task because large repositories cannot be analyzed by coding agents.
  - **Feedback:** Incorrect. The agent still attempted the task, but it was slower and more token-heavy.
- C. Delete cached context and restart the operating system shell.
  - **Feedback:** Incorrect. Restarting the shell was not the method used to answer the codebase question.
- D. Explore the huge codebase directly with built-in file-reading and search tools.
  - **Feedback:** Correct. Without the index, the agent had to inspect files using its normal exploration tools.

**Correct answer:** D. Explore the huge codebase directly with built-in file-reading and search tools.

### 4. Which practice helps reduce the context window during a long AI coding session?

- A. Keep every file attached in case it becomes useful later to keep context awareness
  - **Feedback:** Incorrect. Unnecessary files increase the amount of information the model must consider.
- B. Use the `/compact` command to summarize the discussion
  - **Feedback:** Correct. Compacting a long discussion preserves important information while reducing unnecessary context.
- C. Repeatedly paste the complete message history into the conversation
  - **Feedback:** Incorrect. Repeating the full history makes the context larger and may increase cost and response time.
- D. Avoid removing outdated instructions until the project is finished to prevent context clash
  - **Feedback:** Incorrect. Outdated instructions should be removed when they are no longer relevant so the context remains clean.

**Correct answer:** B. Use the `/compact` command to summarize the discussion.

### 5. What role did Context7 play in improving the Kubernetes/Terraform generation task?

- A. It let the agent fetch up-to-date documentation instead of relying only on training data.
  - **Feedback:** Correct. The improved output came from giving the agent current documentation through Context7.
- B. It disabled all model reasoning and forced the agent to use a fixed template.
  - **Feedback:** Incorrect. Context7 supplied documentation; it did not replace model reasoning with a fixed template.
- C. It cloned the Kubernetes source code and indexed every file locally.
  - **Feedback:** Incorrect. Codebase indexing was handled by Auggie in a different example. Context7 was used for documentation retrieval.
- D. It converted Terraform files into Kubernetes YAML manifests automatically.
  - **Feedback:** Incorrect. The lesson does not describe Context7 as a Terraform-to-YAML converter.

**Correct answer:** A. It let the agent fetch up-to-date documentation instead of relying only on training data.

### 6. What is the context window in an AI coding session?

- A. A permanent database containing every previous user conversation
  - **Feedback:** Incorrect. The context window relates to the current session or task, not a permanent record of every conversation.
- B. The model's short-term memory containing information for the current task
  - **Feedback:** Correct. The context window contains messages, instructions, files, and other information the model considers while working on the current task.
- C. A tool for storing completed source code outside the conversation
  - **Feedback:** Incorrect. External code storage is separate from the model’s active context.
- D. A billing dashboard that displays only token costs
  - **Feedback:** Incorrect. Usage screens may show costs, but the context window is the information available to the model, not the billing interface.

**Correct answer:** B. The model's short-term memory containing information for the current task.

### 7. Why can CLI-based tool usage reduce context overhead compared with directly connected MCP servers?

- A. Skills can load minimal frontmatter first and call the CLI only when needed.
  - **Feedback:** Correct. Minimal skill descriptions reduce the initial context load.
- B. CLI tools force all documentation into the system prompt.
  - **Feedback:** Incorrect. CLI usage is meant to avoid loading large tool descriptions into the main context unnecessarily.
- C. CLI tools prevent the model from calling any external program.
  - **Feedback:** Incorrect. The point is that the agent can call an external CLI tool when needed.
- D. CLI tools remove the need for the agent to understand the task.
  - **Feedback:** Incorrect. The agent still needs task understanding; CLI tools only change how capabilities are exposed.

**Correct answer:** A. Skills can load minimal frontmatter first and call the CLI only when needed.

### 8. What does a cache read indicate?

- A. The system is reusing previously stored context instead of processing it from zero
  - **Feedback:** Correct. Cached instructions, files, or message history can be read again without being processed entirely from the beginning.
- B. The system is saving new instructions, files, or messages for later reuse
  - **Feedback:** Incorrect. Saving reusable information is a cache write rather than a cache read.
- C. The system is opening files that are not part of the current context
  - **Feedback:** Incorrect. Cache reads concern stored context that has already been processed, not unrelated files.
- D. The system is deleting outdated conversation history
  - **Feedback:** Incorrect. A cache read retrieves reusable context; it does not remove conversation history.

**Correct answer:** A. The system is reusing previously stored context instead of processing it from zero.

### 9. What does the Kubernetes/Terraform example demonstrate?

- A. AWS automatically upgrades every generated Kubernetes configuration to the latest version
  - **Feedback:** Incorrect. The lesson does not claim AWS fixes outdated generated configuration automatically.
- B. AI-generated code can be outdated when the model relies only on internal training data.
  - **Feedback:** Correct. The model produced an outdated Kubernetes version when it did not use current documentation.
- C. Terraform is not suitable for generating AWS infrastructure from an AI prompt.
  - **Feedback:** Incorrect. The lesson does not reject Terraform generation; it shows the need for current documentation.
- D. Kubernetes versions are irrelevant when generating sample infrastructure code.
  - **Feedback:** Incorrect. The Kubernetes version was the key issue in the example.

**Correct answer:** B. AI-generated code can be outdated when the model relies only on internal training data.

### 10. What is the main purpose of codebase indexing in a very large software project?

- A. To automatically rewrite every file in the repository using the agent's preferred coding style.
  - **Feedback:** Incorrect. Codebase indexing is about retrieval and understanding, not mass rewriting files.
- B. To reduce the number of source files in the repository before the agent starts working.
  - **Feedback:** Incorrect. Indexing does not shrink or delete the repository; it creates a searchable representation of it.
- C. To replace the need for project documentation by storing all files in the model's prompt permanently.
  - **Feedback:** Incorrect. The index does not paste the whole project permanently into the prompt; it retrieves relevant pieces when needed.
- D. To let the AI retrieve relevant parts of the codebase without scanning the entire project from scratch.
  - **Feedback:** Correct. Indexing helps the agent locate relevant implementation details efficiently in a huge repository.

**Correct answer:** D. To let the AI retrieve relevant parts of the codebase without scanning the entire project from scratch.

### 11. What should you do when beginning a new task after completion of the previous task?

- A. Combine the new task with an older project to preserve context
  - **Feedback:** Incorrect. Context should be preserved only when it is relevant to the same task or project.
- B. Start a new chat and provide only the necessary details
  - **Feedback:** Correct. A clean context helps the AI focus on the current goal with less irrelevant information.
- C. Ask the AI to ignore the context without changing chats
  - **Feedback:** Incorrect. A request to ignore earlier content may help, but starting a separate session provides a cleaner and more reliable context.
- D. Continue in the existing chat to keep all the necessary context
  - **Feedback:** Incorrect. Keeping unrelated history adds noise and may create conflicts with the new task.

**Correct answer:** B. Start a new chat and provide only the necessary details.

### 12. Why should developers be careful about enabling many MCP servers at once?

- A. MCP servers permanently change the repository structure after connection.
  - **Feedback:** Incorrect. Connecting MCP servers adds tools to the agent environment; it does not permanently alter the repository by itself.
- B. MCP tool descriptions, schemas, and instructions can consume the context window.
  - **Feedback:** Correct. Each MCP server may add tool information that the model must process.
- C. MCP servers only work when the context window is already full.
  - **Feedback:** Incorrect. MCP servers are tools; they do not require the context window to be full.
- D. MCP servers prevent the agent from using command-line tools.
  - **Feedback:** Incorrect. MCP and CLI tools can both be used in AI workflows.

**Correct answer:** B. MCP tool descriptions, schemas, and instructions can consume the context window.

## Answer Key

| Question | Answer |
| --- | --- |
| 1 | A |
| 2 | A |
| 3 | D |
| 4 | B |
| 5 | A |
| 6 | B |
| 7 | A |
| 8 | A |
| 9 | B |
| 10 | D |
| 11 | B |
| 12 | B |
