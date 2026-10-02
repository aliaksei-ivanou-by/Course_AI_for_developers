# Summary: Model Routing

Model routing chooses an eligible model for each request or workflow step according to quality, latency, cost, availability, capability, and compliance requirements. Start by excluding models that cannot satisfy data-handling, modality, context, tool, or quality constraints; optimize only within the remaining pool.

Common strategies are explicit task-to-model selection, deterministic rules, learned classifiers, cheap-first cascades with validation-based escalation, and fallbacks for availability failures. Dynamic routing adds complexity, so compare it with single-model and simple rule-based baselines on representative tasks. Measure completed-task success, schema and tool-call validity, latency, total cost, retries, escalation, and human correction—not token price alone. Log the actual model and reason for every route. Be careful with multi-turn continuity, prompt-cache reuse, output-contract differences, unsafe fallbacks, and weak confidence signals. A router is valuable only when it improves real workload outcomes without violating the workflow's technical or security constraints.

