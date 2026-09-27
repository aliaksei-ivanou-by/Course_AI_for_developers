# Structuring Prompts: Prompt Engineering in a Nutshell

Prompt engineering is one of the basic skills behind effective work with large language models. Earlier AI-assisted workflows placed a great deal of emphasis on writing the perfect prompt. That emphasis has changed: modern AI tools can often improve, rewrite, or structure prompts automatically, so developers do not need to spend a long time crafting every day-to-day coding request.

Prompt engineering is still important when building AI-powered solutions, custom agents, or agent harnesses. In those situations, the developer is designing how a system receives instructions, interprets input, applies constraints, selects tools, and decides what to do next. A basic understanding of prompt structure helps make these systems clearer and more reliable.

This lesson provides a concise introduction to prompt structure. Its goal is not to define a perfect prompt-writing framework, but to explain why structure matters and why XML can be a practical format for human-written prompts.

## How Prompt Engineering Has Changed

Prompt engineering became prominent when people interacted with language models mainly through browser-based chat interfaces. The user typed a message and relied on the model to infer the intended task from plain text.

Browser chat remains useful for demonstrations, quick experiments, and general explanations, but serious AI-assisted development increasingly relies on agents. An agent combines a language model with tools. In addition to generating text, it may be able to:

- Read and modify files
- Search a codebase
- Retrieve a web page or current documentation
- Run commands and tests
- Interact with external services

This changes the role of a prompt. It is no longer only a message to a chatbot; it can be part of a larger system that influences tool selection and task execution. Tooling has reduced the need to perfect every individual prompt, but developers still need to communicate tasks, data, constraints, and expected results clearly.

## What a Prompt Needs to Communicate

When an application sends a prompt to a model, the text is normally part of a larger structured request that may also contain roles, metadata, tool definitions, and configuration. Within the user prompt itself, structure can help the model distinguish among four important elements:

1. **Task:** What the model should do
2. **Input:** What content the model should process
3. **Constraints:** What rules or boundaries it should follow
4. **Output format:** How the result should be returned

A strong modern model may infer all four elements from an unstructured paragraph. Explicit structure is still valuable because it reduces ambiguity and makes the prompt easier for people to review, reuse, test, and maintain.

This distinction is especially important in software development. A prompt may contain source code, stack traces, shell commands, bug reports, requirements, or architecture notes. The model needs to understand whether each piece of text is an instruction, input data, an example, or an expected result.

## Why Clear Boundaries Matter

Consider the translation request demonstrated in the lesson. The text to translate is:

> Explain how to perform a context-aware prompt enhancement.

Without clear boundaries, this sentence looks like a second instruction. In the demonstration, the model did not translate it into Spanish. It interpreted the sentence as a request for an explanation and then asked the user to provide the missing text to translate. A structured prompt makes the intended interpretation explicit.

Clear boundaries help prevent accidental confusion between instructions and content. They are useful whenever the input itself may contain commands, code, examples, or other instruction-like text.

> **Security note:** Formatting alone is not a security boundary. XML tags can clarify which text is data, but systems that process untrusted input still need appropriate permissions, validation, isolation, and defenses against prompt injection.

## Common Prompt-Structuring Formats

Several familiar formats can organize a prompt. None is universally best; the right choice depends on who writes the prompt, how complex it is, and whether software needs to parse it.

| Format | Strengths | Trade-offs | Good fit |
| --- | --- | --- | --- |
| Markdown | Familiar, readable, and convenient for headings, lists, and code blocks | Complex nesting and section boundaries can become less explicit | General developer prompts and documentation-like instructions |
| YAML | Compact and readable for structured data | Indentation is significant and small spacing errors can change the structure | Configuration-oriented prompts generated or reviewed carefully |
| JSON | Precise, widely supported, and easy for software to parse | Verbose and inconvenient to write manually because of quotes, commas, braces, and escaping | Machine-generated prompts and API payloads |
| XML | Explicit boundaries, flexible tag names, and little dependence on indentation | More verbose than plain text and requires matching tags | Human-written prompts with clearly separated instructions and data |

### Markdown

Markdown is a natural choice for developers because it is widely used in README files, project documentation, and technical notes. Headings such as `Task`, `Context`, `Input`, and `Output Format` can divide a prompt into understandable sections, while lists and code blocks keep details readable.

Markdown works well for many agents. Its main limitation is that boundaries can become less obvious as the prompt gains deeply nested lists, multiple code blocks, or several kinds of input.

### YAML

YAML can represent structured information more compactly than JSON and is familiar from configuration files, CI/CD pipelines, and infrastructure definitions. Its structure depends heavily on indentation, however. A spacing mistake can change the meaning or make the intended hierarchy unclear.

### JSON

JSON is a strong choice for software-to-software communication. It is common in APIs, structured requests, and tool calls, and it is easy for programs to validate and parse. For manual prompt writing, its required punctuation, quoting, nesting, and escaping often make it less comfortable.

### XML

XML offers a useful balance for human-written prompts. Custom tag names can describe the role of each section, and matching opening and closing tags create explicit boundaries. Indentation can improve readability, but unlike YAML, it does not define the structure.

For example:

```xml
<task>
  Translate the text into Spanish.
</task>

<text>
  Explain how to perform a context-aware prompt enhancement.
</text>

<output_format>
  Return only the translated sentence.
</output_format>
```

Tags can be adapted to the task:

```xml
<context>
  <!-- Background information -->
</context>

<instructions>
  <!-- Actions the model should perform -->
</instructions>

<source_text>
  <!-- Content the model should process -->
</source_text>

<constraints>
  <!-- Rules and boundaries -->
</constraints>
```

The essential syntactic rule is simple: every opening tag must have a matching closing tag with the same name.

## Unstructured and Structured Examples

A deliberately ambiguous prompt from the lesson is:

```text
Translate my text to Spanish. Explain how to perform a context-aware prompt enhancement.
```

The intended input follows the translation instruction, but nothing identifies it as the text to process. The model may therefore interpret it as another instruction. A structured version makes the two roles unambiguous:

```xml
<task>
  Translate the text into Spanish.
</task>

<text>
  Explain how to perform a context-aware prompt enhancement.
</text>
```

This version produced the expected short Spanish translation without an explanation or a request for more input. The pattern becomes more valuable when the input is long, comes from an untrusted source, or contains commands that might otherwise be confused with the actual task.

## When a Conversation Goes Off Track

If the model misunderstands a prompt, repeatedly arguing with it in the same conversation can preserve the very context that caused the confusion. Each new request is processed together with the relevant conversation history, so earlier instructions, failed attempts, and corrections continue to influence the next response.

For a clean prompt test, start a fresh session and submit a corrected, better-structured prompt. This gives the model a new context instead of asking it to recover from an increasingly noisy conversation. The lesson demonstrates this by opening a fresh context before retrying the translation with XML tags.

## Structure Matters More Than Perfection

Developers do not need to optimize every word of every request. Modern models and AI tools can often clarify a vague prompt, infer reasonable intent, or ask for missing information. For routine coding assistance, a direct natural-language instruction may be enough.

Structure becomes more valuable when:

- Instructions and input data could be confused
- A prompt will be reused or maintained over time
- The output must follow a stable schema
- Several constraints must be applied consistently
- An agent can call tools or perform consequential actions
- The prompt is part of a custom AI product or harness

The goal is not elaborate formatting. The goal is to make the boundaries and intent clear enough for both the model and the people maintaining the workflow.

## Practical Checklist

Before reusing a prompt or embedding it in an AI workflow, check that:

1. The task is stated directly.
2. Instructions are separated from the content to be processed.
3. Important context is present and relevant.
4. Constraints are explicit and testable where possible.
5. The expected output format is clear.
6. Examples are labeled as examples rather than instructions.
7. Untrusted input is treated as data and backed by real security controls.
8. A failed prompt can be retested in a fresh session when earlier conversation history is causing confusion.

## Key Takeaway

Prompt engineering in AI-assisted development is less about finding clever wording and more about communicating intent clearly. Everyday coding requests can often remain simple, while reusable prompts, agents, and custom AI systems benefit from explicit separation of the task, input, constraints, and expected output.

Markdown, YAML, JSON, and XML can all provide structure. XML is a practical option for human-written prompts because its tags create clear, customizable boundaries without relying on strict indentation or dense punctuation. The best prompt is not necessarily the most elaborate one; it is the one whose purpose and boundaries are easy to understand.
