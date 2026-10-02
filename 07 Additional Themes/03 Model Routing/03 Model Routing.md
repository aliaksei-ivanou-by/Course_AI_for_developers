# Model Routing

Model routing selects which language model should handle each request or workflow step. Instead of sending every task to the fastest, cheapest, or most capable model, a router chooses from an approved pool according to the task's needs and the system's quality, latency, cost, availability, and compliance constraints.

Routing can happen once for a whole request or repeatedly inside an agent workflow. A coding agent might use a fast model to classify a task, a stronger reasoning model to design a risky migration, and a specialized model to process an image. The architecture is useful only when the extra selection logic improves outcomes on real workloads.

## Why Route Between Models?

Models differ along several dimensions:

- reasoning and coding quality;
- latency and throughput;
- input and output price;
- context-window and output limits;
- supported modalities, tools, and structured-output features;
- regional availability, data-processing terms, and enterprise approval;
- reliability for a particular domain or language.

No single model is necessarily best on every dimension. Routing can reserve expensive capacity for tasks that need it while letting simpler work use a faster or cheaper path. It can also provide fallback when a provider or deployment is unavailable.

## Common Routing Strategies

### Explicit selection

The caller chooses the model because the task type is known. For example, a code-review command always uses the approved review model, while a title-generation endpoint uses a small fast model. This is simple, observable, and often the best starting point.

### Rule-based routing

Deterministic rules select a model from request metadata or measured constraints:

- context length;
- required modality or tool support;
- customer tier or data residency;
- task label;
- latency budget;
- maximum price;
- previous failure or rate limit.

Rules are easy to audit but can become brittle when prompt difficulty does not align with surface features.

### Classifier or learned routing

A lightweight classifier or specialized router estimates which model is suitable for the prompt. It may predict task type, difficulty, expected quality, or the probability that a smaller model will succeed. Learned routing adapts better to heterogeneous traffic but requires representative data, evaluation, and monitoring.

### Cascade or escalation

Start with a cheaper model and escalate when a verifier, confidence signal, schema validator, test suite, or user feedback indicates that the result is insufficient. Cascades work best when failure is detectable. A fluent but subtly wrong answer can pass a weak confidence check.

### Fallback routing

Retry another deployment or model after timeout, capacity failure, safety refusal, or malformed output. A fallback is not automatically equivalent: models may differ in tool behavior, context limits, safety policies, and output schemas. Define which failures are safe to retry and preserve idempotency for tool-using workflows.

## Routing Constraints Come Before Optimization

First remove models that cannot legally or technically serve the request. An eligible model must satisfy requirements such as:

- approved region and data handling;
- required context size and modality;
- tool-calling and schema support;
- required availability or service tier;
- organizational allowlist;
- task-specific quality floor.

Only then optimize cost, latency, or quality across the eligible pool. A cheap model is not a valid route if it cannot process the input or is not approved for the data.

## A Practical Routing Policy

```text
1. Filter the pool by compliance, modality, context size, and required tools.
2. Pin high-risk or specialized tasks to an evaluated model.
3. Route low-risk, well-bounded tasks to the least expensive model that meets the quality floor.
4. Escalate when deterministic validation fails or the task exceeds the smaller model's scope.
5. Fall back only to models that preserve the workflow contract.
6. Log the selected model, reason, result, cost, latency, and fallback path.
```

For an agent, routing policy may be defined per step rather than per conversation. Search-query generation, summarization, planning, implementation, and review have different error costs. Keep the lead/orchestrator capable enough to detect weak worker output; otherwise cheap workers can create expensive integration failures.

## Evaluation

Evaluate a router against meaningful alternatives:

- a single strong-model baseline;
- a single economical-model baseline;
- explicit task-to-model rules;
- the proposed dynamic router.

Use a representative workload with expected outcomes and measure:

- task success and human acceptance;
- schema or tool-call validity;
- latency, including router overhead and retries;
- input, output, and reasoning-token cost;
- escalation and fallback rates;
- behavior by task category, language, tenant, and risk level;
- regression after model or prompt updates.

Average cost alone hides failures. A route that saves on inference but increases retries, review time, or production defects is not cheaper at the task level.

## Multi-Turn Conversations and Caching

Changing the backing model in the middle of a conversation can alter style, interpretation, and tool behavior. It may also reduce prompt-cache reuse. Session affinity can preserve continuity, while per-turn routing can optimize each request. Choose deliberately and log the actual model used for every turn.

If the smallest eligible model has a shorter context window, design prompts for that limit or remove it from the pool. Silent truncation is not a routing strategy.

## Common Failure Modes

- Routing by prompt length while ignoring actual difficulty.
- Using the model's self-reported confidence as the only escalation signal.
- Sending sensitive data to an unapproved fallback.
- Changing models without retesting prompts, tool schemas, and output parsers.
- Hiding the selected model, making regressions difficult to diagnose.
- Counting per-token savings while ignoring retries and human correction.
- Routing every step independently when the workflow needs behavioral continuity.
- Using a weak router or orchestrator that cannot recognize when escalation is needed.

## Related Course Material

- [Current AI Development Toolset](../../01%20Intro/03%20Our%20Toolset%20as%20for%20Now/03%20Our%20Toolset%20as%20for%20Now.md)
- [Context Windows, Caching, Cost, and Performance](../../04%20Context%20Engineering/01%20General%20practices/03%20Context%20window%20-%20Caching%20and%20Price/03%20Context%20window%20-%20Caching%20and%20Price.md)
- [Using Open-Weight Models Without Powerful Local Hardware](../../05%20Advanced%20Techniques/03%20Using%20local%20LLM%20without%20powerful%20hardware/03%20Using%20local%20LLM%20without%20powerful%20hardware.md)
- [Microsoft Foundry model router concepts](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router-how-it-works)

