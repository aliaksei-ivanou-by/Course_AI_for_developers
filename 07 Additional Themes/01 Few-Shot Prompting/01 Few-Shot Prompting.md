# Few-Shot Prompting

Few-shot prompting teaches a model the desired behavior by placing a small number of input/output examples in the prompt. The examples do not update the model's weights. They become temporary context that demonstrates the task, the decision boundary, and the expected response format for the current request.

This technique is useful when a written instruction is technically correct but still leaves several plausible interpretations. An example can make a subtle convention concrete: how to classify an ambiguous ticket, how terse a review comment should be, which fields belong in a JSON object, or how a team wants a requirement rewritten.

## Zero-Shot, One-Shot, and Few-Shot

| Approach | Prompt contents | Good fit |
| --- | --- | --- |
| Zero-shot | Instructions and the new input, but no worked example | Familiar tasks with an obvious output contract |
| One-shot | One representative example followed by the new input | A simple convention or format that is difficult to describe precisely |
| Few-shot | Several examples followed by the new input | Tasks with multiple classes, edge cases, or style distinctions |

More examples are not automatically better. Every example consumes context, and a large or inconsistent example set can distract the model from the current input. Start without examples, add one when the model repeatedly misinterprets the task, and add further examples only when each one teaches a distinct boundary.

## What Examples Teach

A useful example can demonstrate several things at once:

- **Semantics:** which answer is correct for a particular kind of input.
- **Decision boundaries:** how two similar cases should be treated differently.
- **Structure:** the exact fields, ordering, or markup expected in the output.
- **Style:** tone, level of detail, naming conventions, or review-comment format.
- **Abstention:** when the model should return `unknown`, ask for missing information, or refuse to guess.

Examples are especially valuable for classification, extraction, transformation, and structured generation. They are less useful when the main problem is missing current knowledge; retrieval is the appropriate mechanism for that case.

## Designing a Good Example Set

### Make each example correct

The model can reproduce mistakes and inconsistencies in the demonstration. Review examples like test fixtures: confirm the input, expected output, terminology, and formatting before reusing them.

### Cover meaningful variation

Choose examples that represent the behavior you want to generalize:

- one ordinary case;
- one boundary or easily confused case;
- one failure, abstention, or missing-data case when relevant.

Do not fill the prompt with near-duplicates. A diverse set usually teaches more than many repetitions of the easiest case.

### Keep the mapping explicit

Use identical labels and delimiters for every example. XML tags, Markdown headings, or JSON objects can make it clear which text is an input and which text is the expected output. Keep untrusted user content in a separate, clearly marked field; examples improve clarity but are not a prompt-injection defense.

### Match the production task

Examples should resemble real inputs in length, vocabulary, ambiguity, and output requirements. An example set made only of clean toy cases may not transfer to noisy logs, partial bug reports, mixed languages, or large source fragments.

### Avoid accidental rules

Models notice patterns that the author did not intend. If every positive example is long and every negative example is short, length can become an unintended signal. Vary irrelevant properties so that the true decision boundary is the stable pattern.

## Example: Classifying a Change Request

```xml
<task>
Classify the request as bug, feature, or question.
Return JSON with fields "label" and "reason".
</task>

<examples>
  <example>
    <input>The export button produces an empty CSV for accounts with Unicode names.</input>
    <output>{"label":"bug","reason":"Existing export behavior fails for a valid input."}</output>
  </example>
  <example>
    <input>Add an option to export the same report as Parquet.</input>
    <output>{"label":"feature","reason":"The request adds a new output format."}</output>
  </example>
  <example>
    <input>Which roles are currently allowed to export reports?</input>
    <output>{"label":"question","reason":"The request asks about current behavior without requesting a change."}</output>
  </example>
</examples>

<input>
CSV export worked yesterday, but today it returns HTTP 500 for every account.
</input>
```

The examples show the distinction more reliably than a long abstract definition alone. In a production system, validate the returned JSON against a schema and handle invalid output explicitly.

## Common Failure Modes

- **Too many examples:** relevant instructions and current input receive less attention.
- **Contradictory examples:** the model has to infer which demonstration wins.
- **Unrepresentative examples:** performance looks good in a demo but fails on real inputs.
- **Examples that leak the answer:** evaluation results become meaningless because the test case or a near-duplicate is already in the prompt.
- **Using examples as a security control:** a malicious or indirect instruction can still redirect a tool-using model.
- **No output validation:** correct-looking demonstrations do not guarantee schema-valid or safe production output.

## Evaluation Workflow

1. Define a small evaluation set that is separate from the prompt examples.
2. Establish a zero-shot baseline.
3. Add the smallest useful example set.
4. Compare accuracy, format validity, latency, and token cost.
5. Test edge cases and adversarial inputs, not only happy paths.
6. Version the prompt and examples together so results can be reproduced.

If changing the model changes results, retest the examples. Few-shot behavior is model-dependent, and examples tuned for one model or version may not transfer cleanly to another.

## Related Course Material

- [Structuring Prompts](../../02%20Meta-Prompting/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29/01%20Structuring%20Prompts%20%28Prompt%20Engineering%20in%20a%20Nutshell%29.md)
- [Tool-Agnostic Meta-Prompting](../../02%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting/03%20Tool-Agnostic%20Meta-Prompting.md)
- [Anthropic prompting best practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables)

