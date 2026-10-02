# Summary: Few-Shot Prompting

Few-shot prompting places a small number of correct input/output examples in the prompt so the model can infer the desired behavior for the current request. It does not train or fine-tune the model. Use it when plain instructions leave an important decision boundary, format, or style ambiguous; prefer zero-shot prompting when the task is already clear.

Good examples are correct, representative, consistently delimited, and meaningfully different from one another. A compact set often includes an ordinary case, a boundary case, and an abstention or missing-data case. Evaluate it against separate test inputs and measure quality, format validity, latency, and token cost. Examples can reproduce mistakes, teach accidental correlations, consume useful context, or leak evaluation answers. They also do not prevent prompt injection, so production workflows still need validation, least privilege, and appropriate security controls.

