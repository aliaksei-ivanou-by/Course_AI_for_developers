# Structured Prompts Quiz

**Minimum grade to pass:** 70%  
**Attempts allowed:** Unlimited  
**Number of questions:** 10  
**Question type:** Single choice

## Questions, Answers, and Feedback

### 1. When is prompt engineering still especially relevant?

- A. Only when using a free browser-based chatbot
  - **Feedback:** Incorrect. The lesson says browser-based chatbots are no longer the main development workflow, and prompt engineering is broader than free chatbot usage.
- B. When building custom AI-powered solutions, agents, or harnesses
  - **Feedback:** Correct. Prompt engineering remains important when developers design systems that control how models receive instructions, interpret context, and perform tasks.
- C. When avoiding structured data formats completely
  - **Feedback:** Incorrect. The lesson emphasizes the value of structured prompts rather than avoiding structure.
- D. Only when writing README files in Markdown
  - **Feedback:** Incorrect. Markdown is mentioned as a familiar structuring format, but prompt engineering is not limited to README files.

**Correct answer:** B. When building custom AI-powered solutions, agents, or harnesses.

### 2. What is one advantage of Markdown for prompting?

- A. It is mainly designed for machine-to-machine API calls
  - **Feedback:** Incorrect. JSON is more closely associated with machine-to-machine structured requests.
- B. It is familiar to many developers because it is commonly used in README files and Git workflows
  - **Feedback:** Correct. The lesson notes that developers often work with Markdown through README files and Git-based projects.
- C. It prevents all ambiguity in complex prompts
  - **Feedback:** Incorrect. Markdown can help structure prompts, but it does not eliminate all ambiguity, especially in complex cases.
- D. It does not require any syntax rules
  - **Feedback:** Incorrect. Markdown has syntax for headings, lists, code blocks, and other formatting.

**Correct answer:** B. It is familiar to many developers because it is commonly used in README files and Git workflows.

### 3. Why is XML presented as a practical format for structured prompts?

- A. It gives clear boundaries through custom tags without relying heavily on indentation
  - **Feedback:** Correct. XML makes sections clear with opening and closing tags, while spacing is mainly for readability rather than structure.
- B. It forces every prompt to follow a fixed universal schema
  - **Feedback:** Incorrect. XML is flexible because developers can create their own tags for the structure they need.
- C. It is useful only when the model is unable to read Markdown
  - **Feedback:** Incorrect. XML can be useful even when the model understands Markdown because it provides explicit boundaries.
- D. It removes the need to write clear task instructions
  - **Feedback:** Incorrect. XML helps organize instructions, but the instructions themselves still need to be clear.

**Correct answer:** A. It gives clear boundaries through custom tags without relying heavily on indentation.

### 4. What is a key weakness of YAML for structuring prompts?

- A. It is sensitive to spacing and indentation
  - **Feedback:** Correct. YAML structure depends heavily on indentation, so spacing mistakes can make the intended structure unclear.
- B. It cannot represent structured information
  - **Feedback:** Incorrect. YAML can represent structured information, which is why it is used in configuration files.
- C. It requires every field to be written as an XML tag
  - **Feedback:** Incorrect. XML uses tags; YAML uses an indentation-based key-value structure.
- D. It is only usable inside browser-based chatbots
  - **Feedback:** Incorrect. YAML is not limited to browser chatbots and is widely used outside prompting.

**Correct answer:** A. It is sensitive to spacing and indentation.

### 5. What is the main takeaway for developers from this lesson?

- A. The best prompt format is always JSON because models receive JSON requests
  - **Feedback:** Incorrect. JSON is machine-friendly, but XML may be more practical for humans writing structured prompts manually.
- B. Prompt engineering should be avoided when working with agents
  - **Feedback:** Incorrect. Prompt engineering is especially relevant when building or configuring agents and custom AI workflows.
- C. Perfect prompt wording is more important than prompt structure
  - **Feedback:** Incorrect. The lesson argues that perfect wording is less important than clear structure, especially with modern tools.
- D. Developers should structure prompts so the model can clearly separate tasks, inputs, rules, and outputs
  - **Feedback:** Correct. This is the main practical lesson: structure improves clarity and reduces ambiguity for the model.

**Correct answer:** D. Developers should structure prompts so the model can clearly separate tasks, inputs, rules, and outputs.

### 6. Why may JSON be inconvenient for humans writing prompts manually?

- A. It is less machine-friendly than Markdown
  - **Feedback:** Incorrect. JSON is machine-friendly, which is one of its strengths.
- B. It requires careful use of quotes, commas, braces, brackets, and nesting
  - **Feedback:** Correct. JSON is powerful for machines but can be uncomfortable for humans to write manually because its syntax is strict.
- C. It cannot be sent as part of model requests
  - **Feedback:** Incorrect. The lesson explains that model requests may contain JSON data and metadata.
- D. It has no way to represent metadata
  - **Feedback:** Incorrect. JSON can represent metadata and is commonly used for structured request data.

**Correct answer:** B. It requires careful use of quotes, commas, braces, brackets, and nesting.

### 7. Why is prompt engineering described as less central for everyday AI-assisted development than it used to be?

- A. Because prompt engineering only applies to non-technical writing tasks
  - **Feedback:** Incorrect. Prompt engineering is still relevant in technical work, especially when building agents or AI-powered systems.
- B. Because modern AI tools can often improve or structure prompts automatically
  - **Feedback:** Correct. Many current AI tools can rewrite, improve, or structure prompts, so developers do not always need to manually craft perfect prompts for everyday coding work.
- C. Because agents cannot use prompts when working with tools
  - **Feedback:** Incorrect. Agents still rely on prompts and instructions; they simply add the ability to call tools and act on structured tasks.
- D. Because large language models no longer require instructions from users
  - **Feedback:** Incorrect. Models still require instructions; the point is that tools can help improve how those instructions are written.

**Correct answer:** B. Because modern AI tools can often improve or structure prompts automatically.

### 8. What is an agent in the context of this lesson?

- A. A large language model that can call tools such as opening files or fetching web pages
  - **Feedback:** Correct. The lesson defines an agent as a language model that can use tools, such as opening files, searching, or fetching web pages.
- B. A browser extension that replaces all manual coding work
  - **Feedback:** Incorrect. An agent is not described as a browser extension or as a complete replacement for developers.
- C. A JSON file that stores prompts and metadata
  - **Feedback:** Incorrect. JSON may be involved in requests sent to models, but it is not what an agent is.
- D. A static chatbot that can only answer with plain text
  - **Feedback:** Incorrect. This describes older chatbot-style interaction, while an agent can perform tool calls.

**Correct answer:** A. A large language model that can call tools such as opening files or fetching web pages.

### 9. In a translation prompt, why is it useful to place the text to translate inside a separate XML tag?

- A. It tells the model that the text is content to process, not an instruction to follow
  - **Feedback:** Correct. Separating the input text from the task helps prevent the model from treating text inside the input as a command.
- B. It converts the prompt into a browser-based agent
  - **Feedback:** Incorrect. XML structure does not turn a prompt into an agent; agents are models with tool-calling abilities.
- C. It automatically checks the grammar of the original sentence
  - **Feedback:** Incorrect. XML tags structure the prompt, but they do not automatically perform grammar checking.
- D. It prevents the model from returning any output
  - **Feedback:** Incorrect. A structured prompt can still request output; XML simply clarifies what the input and rules are.

**Correct answer:** A. It tells the model that the text is content to process, not an instruction to follow.

### 10. Why can unstructured prompts be risky?

- A. They can make it harder for the model to distinguish instructions from content
  - **Feedback:** Correct. Without structure, the model may confuse the task with the text it is supposed to process.
- B. They are only supported by older models
  - **Feedback:** Incorrect. Unstructured prompts can be used with modern models too; the issue is reliability, not support.
- C. They always prevent modern models from answering correctly
  - **Feedback:** Incorrect. Modern models often handle unstructured prompts well, but unstructured prompts can still create ambiguity.
- D. They require XML tags even for simple tasks
  - **Feedback:** Incorrect. XML is recommended as a useful structure, but simple prompts do not always require XML.

**Correct answer:** A. They can make it harder for the model to distinguish instructions from content.

## Answer Key

| Question | Answer |
| --- | --- |
| 1 | B |
| 2 | B |
| 3 | A |
| 4 | A |
| 5 | D |
| 6 | B |
| 7 | B |
| 8 | A |
| 9 | A |
| 10 | A |
