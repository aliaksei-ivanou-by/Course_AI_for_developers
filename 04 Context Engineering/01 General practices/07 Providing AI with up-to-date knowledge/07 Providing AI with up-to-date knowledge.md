# Providing AI Agents with Up-to-Date Documentation

An AI coding agent can produce syntactically convincing code while relying on obsolete APIs, unsupported versions, removed parameters, or deprecated practices. The model's internal knowledge is useful for general concepts, but it is not a live dependency catalog or a substitute for current vendor documentation.

The practical response is **grounding**: retrieve authoritative information for the exact technology and version before making a time-sensitive engineering decision, then validate the generated result with deterministic tools.

> **Core principle:** Use model knowledge to reason, current sources to establish facts, and tests or product tools to verify the implementation.

## Why Model Knowledge Becomes Stale

A model learns from a historical body of training data. Its published knowledge cutoff describes an approximate boundary for that training data; it does not guarantee that every fact before the date is present, correct, or equally reliable.

Software changes continuously:

- Libraries publish new major and minor versions.
- Cloud services change supported versions by region and support tier.
- APIs add, rename, deprecate, and remove fields.
- Security guidance changes after new vulnerabilities are found.
- Providers revise pricing, quotas, authentication, and product names.
- Documentation corrects errors without changing the software version.
- Infrastructure modules and providers impose compatibility constraints of their own.

A newer cutoff reduces some risk but does not eliminate it. The model may still recall a popular older example more readily than the newest supported pattern. It may also combine valid details from incompatible versions.

Model metadata is itself time-sensitive. For example, Google's Gemini 3 guide currently documents a January 2025 knowledge cutoff and recommends Search Grounding for newer information. Anthropic publishes separate training-data and reliable-knowledge cutoffs for its models. These values should be read from the current model documentation rather than memorized in a course or prompt.

## Knowledge Cutoff Is Not a Documentation Version

Do not infer software support from the model's cutoff:

```text
model knowledge cutoff: January 2026
                     ≠
all January 2026 documentation is known
                     ≠
the model selects the correct product version
                     ≠
the generated configuration is supported today
```

Even when a release predates the cutoff, the model may lack a minor migration note, cloud-provider exception, or newly published end-of-life date. Conversely, a model may know a newer release through supplied context or tools even though it was not part of training.

Treat the cutoff as a warning about possible staleness, not as evidence that a particular answer is current.

## The Lesson's Practical Experiment

The recorded demonstration asks an agent to generate a sample Terraform configuration for a Kubernetes cluster on AWS.

### Baseline: Internal Knowledge Only

With documentation retrieval disabled, the agent produced a plausible configuration using Kubernetes 1.30. The code looked reasonable, but its version decision came from model memory rather than a cited source.

### Grounded Attempt: Context7 Enabled

In a new session, the same task explicitly asked the agent to retrieve current documentation through Context7. The agent resolved a documentation library, queried relevant material, and produced a more comprehensive configuration using Kubernetes 1.33.

The exercise demonstrates a real effect: retrieval can move the model away from an older memorized example. It does **not** prove that the second version is automatically correct.

### Optional Comparison in the Recording

The central lesson ends with the distinction between internal and external knowledge. The remainder of the recording is an optional comparison of agents attempting the same task through different context paths:

- Antigravity generating from internal model knowledge
- Claude using web search to retrieve current external information

This comparison illustrates workflow behavior, not a controlled model benchmark. The agents differ in model, harness, enabled tools, permissions, latency, and retrieved evidence. A fast or visually polished answer is not evidence that the selected API or version is correct. Compare the sources, generated configuration, and validation results rather than ranking the agents from a single run.

### Important Correction: Upstream Kubernetes Is Not Amazon EKS

The target in the exercise is Amazon EKS, a managed Kubernetes service. Upstream Kubernetes and EKS publish different support schedules.

For example, official upstream records list:

- Kubernetes 1.30 upstream end of life: July 15, 2025
- Kubernetes 1.33 upstream end of life: June 28, 2026

AWS, however, documents a separate EKS lifecycle. Its version table lists EKS 1.33 with standard support through July 29, 2026 and extended support through July 29, 2027.

This means that “upstream end of life” and “unavailable on EKS” are not equivalent. A generated EKS version must be checked against:

- The current Amazon EKS version lifecycle
- Availability in the target account and region
- Standard versus extended support requirements and cost
- The selected Terraform AWS provider version
- The EKS module version, if a module is used
- Add-on, node image, and workload compatibility
- The organization's upgrade policy

The specific version numbers in the video are historical evidence from an experiment, not recommendations for a new cluster.

## “Latest” Is Usually an Incomplete Requirement

Asking for “the latest version” sounds precise but often is not. It may mean:

- The latest upstream release
- The newest version offered by a managed service
- The newest version in standard support
- The newest version allowed by an organization's platform team
- The newest version supported by a Terraform module
- The newest version available in a particular region
- The newest patch in an already approved minor series

A better requirement is explicit:

> Select a Kubernetes version currently in Amazon EKS standard support, available in the target region, compatible with the repository's pinned Terraform provider and module versions, and permitted by the project policy. Cite the sources and state the date checked.

“Newest” and “best for this system” are different decisions.

## Sources of Current Context

Several grounding methods can solve different parts of the problem.

| Method | Best use | Main limitation |
| --- | --- | --- |
| Known official page plus web fetch | Reading a specific authoritative URL | Does not discover a page when the URL is unknown |
| Web search | Discovering current releases, lifecycle pages, and migration guidance | Results require source-quality checks and may have usage cost |
| Documentation retriever such as Context7 | Querying focused library documentation and code examples | The correct library and version must still be selected |
| Vendor CLI or API | Checking what a target account or service actually supports | Requires credentials and may describe only the current environment |
| Repository manifests and lockfiles | Establishing versions already used by the project | They show local state, not whether it remains supported |
| Internal documentation retrieval | Grounding on private APIs, standards, and service contracts | Requires access control, indexing, and freshness ownership |
| Pinned local documentation | Reproducible offline or restricted workflows | Becomes stale unless maintained deliberately |

These methods are complementary. A strong workflow may inspect the repository, retrieve official documentation, query the target service, and run validation tools.

## Web Search, Web Fetch, and Documentation Retrieval

### Web Search

Search is appropriate when the relevant page is unknown or a claim must be checked across current sources. OpenAI, Anthropic, and Google provide web-grounding capabilities in some products, APIs, models, and hosting environments.

Availability is not universal. It can depend on:

- The product surface or agent harness
- The selected model and API
- Hosting provider and region
- Organization settings and permissions
- Plan, rate limits, and usage charges
- Network policy and allowed domains

Therefore, “the provider supports web search” does not guarantee that a particular coding session can use it.

### Web Fetch

Fetch reads a known URL. It is useful when the authoritative page has already been identified, such as the official EKS version lifecycle. Fetch avoids broad discovery but cannot help if the supplied URL is wrong, stale, or incomplete.

### Documentation Retrieval

A specialized documentation service searches a curated or indexed documentation corpus. Context7, for example, supports a two-step flow:

1. Resolve a library name to a library ID.
2. Query documentation for that library, preferably with a specific version and question.

This can return more focused framework context than general web search. It still requires the agent to inspect the selected library, source reputation, version, and returned passages.

```text
task and repository versions
          ↓
resolve the exact product/library
          ↓
retrieve version-matched documentation
          ↓
cross-check operational support source
          ↓
implement and validate
```

## Using Context7 Carefully

Context7 can be used through MCP or through the `ctx7` CLI and a skill. The interface choice does not change the evidence requirements.

A focused CLI query follows this pattern:

```bash
ctx7 library terraform-provider-aws "Amazon EKS cluster version configuration"
ctx7 docs /hashicorp/terraform-provider-aws "EKS cluster version requirements"
```

The exact library ID returned by the first command should be inspected rather than assumed from this example. When version-specific IDs are available, select the version compatible with the project.

Before trusting retrieved content, check:

- Is this the official or intended repository?
- Does the library ID identify the correct product?
- Does the material match the installed version?
- How current is the indexed documentation?
- Is the answer drawn from documentation or a code example with different assumptions?
- Does a cloud provider's operational support page override a generic library example?

Context7 also supports private sources on eligible paid plans. This can help agents work with internal API contracts and documentation across multiple services. It does not remove governance obligations: confirm authorization, retention and privacy rules, access scope, refresh behavior, and whether the indexed material is the approved source of truth.

## A Reliable Grounding Prompt

A vague prompt invites the model to fill gaps from memory:

```text
Create a Terraform configuration for an EKS cluster.
```

A stronger task separates research, decision, implementation, and verification:

```markdown
Create a sample Terraform configuration for an Amazon EKS cluster.

Before writing code:

1. Inspect this repository's Terraform version, AWS provider constraints,
   lockfile, modules, and existing platform policy.
2. Retrieve current official AWS documentation for EKS Kubernetes versions.
3. Retrieve official documentation for the exact Terraform AWS provider and
   module versions used by this repository.
4. Select a Kubernetes version that is available in the target region and in
   standard support. Do not assume that the newest upstream version is valid.
5. Record the source URLs, the date checked, and the reason for the choice.
6. If the evidence conflicts or the target region/account is unknown, stop and
   ask instead of guessing.

Then implement the smallest configuration that meets the stated requirements.
Run formatting and validation, and report anything that still requires a live
AWS account or deployment test.
```

For high-risk work, require the research result before authorizing implementation.

## Evidence Should Travel with the Decision

A source is useful only if reviewers can see which claim it supports. Record a compact evidence table in the plan, pull request, or architecture decision:

| Decision | Source | Checked | Project constraint | Result |
| --- | --- | --- | --- | --- |
| EKS control-plane version | Official AWS EKS lifecycle | Current task date | Must remain in standard support | Selected supported minor version |
| Provider arguments | Exact Terraform AWS provider docs | Current task date | Match `.terraform.lock.hcl` | Used only supported fields |
| Module inputs | Exact module release docs | Current task date | Match module constraint | Avoided inputs from newer module versions |
| Upgrade policy | Internal platform standard | Current revision | Approved version range | No unapproved upgrade |

Do not paste entire documentation pages into the context. Preserve the relevant claim, source, version, and retrieval date.

## Validate More Than the Version Number

Grounding improves the input to generation; it does not certify the output. The generated Terraform can still contain incorrect module names, invalid arguments, incompatible add-ons, insecure defaults, or missing dependencies.

A proportionate validation workflow can include:

1. Run `terraform fmt -check`.
2. Initialize safely for validation where appropriate.
3. Run `terraform validate`.
4. Inspect `terraform providers` and `.terraform.lock.hcl`.
5. Run the repository's configured linter and security scanner.
6. Query the target environment for available EKS versions when credentials and authorization permit it.
7. Review the plan for replacements, destructive changes, network exposure, and IAM scope.
8. Test in an isolated non-production environment before rollout.

AWS documents `aws eks describe-cluster-versions` as a way to obtain current EKS version information. A live provider query can reveal account- or region-specific reality that a documentation index cannot know.

## Prevent Staleness in Project Instructions

Put the rule in project-level agent instructions so it survives beyond one chat:

```markdown
## Current documentation requirements

- For cloud services, frameworks, SDKs, and infrastructure providers, do not
  select versions or APIs from model memory alone.
- Read installed versions and constraints from manifests and lockfiles first.
- Retrieve authoritative documentation for those exact versions.
- Prefer official vendor sources for lifecycle, compatibility, security, and
  pricing claims.
- Record the URL and date for time-sensitive decisions.
- Do not upgrade a dependency or service version without explicit task scope.
- If current documentation is unavailable or sources conflict, report the
  uncertainty and ask before implementing.
```

This rule is more durable than naming one retrieval product. The project can switch between web search, Context7, another MCP server, a CLI, or an internal documentation service without changing the engineering standard.

## Working with Private Documentation

Private documentation is often more important than public library docs because the agent cannot infer an organization's internal APIs and policies from training data.

Before connecting an internal source:

- Confirm that the user and agent are authorized to access it.
- Restrict retrieval to the current project or team where possible.
- Exclude secrets, production data, credentials, and unnecessary repositories.
- Define which system is the source of truth.
- Assign an owner for refresh and removal of obsolete material.
- Preserve document version, revision date, or commit identifier.
- Evaluate the retrieval provider's storage, retention, and data-use terms.
- Treat retrieved text as untrusted content that can contain prompt injection.

Retrieval cannot correct an obsolete internal wiki whose owner never updates it.

## Failure Modes of Grounded Generation

### The Wrong Library Is Resolved

Package names may be ambiguous or forks may have similar names. Verify the owner, repository, version, and source reputation before querying.

### Documentation and Runtime Support Differ

Upstream documentation can describe a valid release that a managed service has not yet adopted. Check the operational provider and target environment.

### The Agent Retrieves but Ignores the Source

Require the agent to state which retrieved facts changed the implementation. Review the diff against those facts.

### Search Returns Secondary or Stale Content

Prefer official documentation, release notes, compatibility matrices, and actual repository manifests over tutorials or snippets with unknown dates.

### The Source Is Current but for the Wrong Version

“Latest documentation” may describe an API unavailable in the project's pinned dependency. Retrieve version-specific docs whenever possible.

### Retrieval Produces Too Much Context

Broad search results or entire documentation pages can bury the decisive passage. Query narrowly and retain only evidence relevant to the current decision.

### Current Information Is Mistaken for Correct Design

A supported version can still violate organizational requirements, budget, security posture, or compatibility constraints. Product decisions remain the developer's responsibility.

## Recommended Workflow

```text
identify volatile facts in the task
                ↓
inspect repository versions and constraints
                ↓
choose authoritative public and internal sources
                ↓
retrieve focused, version-matched evidence
                ↓
resolve conflicts and record the decision
                ↓
generate or modify the implementation
                ↓
run deterministic validation and review the diff
                ↓
retain source, version, and date for future maintenance
```

## Common Mistakes

- Assuming a powerful or recently released model is automatically current
- Treating a knowledge cutoff as a guarantee of complete knowledge
- Asking for “latest” without defining the product, support tier, region, and compatibility constraints
- Comparing a managed service only with the upstream lifecycle
- Trusting Context7, web search, or any retriever without checking the selected source and version
- Using general web results when an official lifecycle or compatibility page exists
- Assuming web search is present and free in every model, client, or hosting environment
- Enabling broad retrieval when a known official page can be fetched directly
- Copying large documentation pages into context instead of extracting relevant evidence
- Indexing private documentation without access, privacy, and freshness controls
- Accepting generated code because it looks comprehensive or was produced quickly
- Skipping deterministic validation after grounding
- Allowing unrestricted edits merely to make an experiment finish faster

## Key Takeaway

An AI agent's internal knowledge is a starting point, not an authoritative version registry. Ground time-sensitive coding decisions in the exact repository state, current official documentation, and the target environment. Context7, web search, web fetch, vendor CLIs, and private documentation systems are different retrieval paths; none removes the need to select the correct product and version. Record the evidence, distinguish upstream from managed-service support, and validate the generated result before trusting it.

## Further Reading

- [OpenAI API: Web search](https://developers.openai.com/api/docs/guides/tools-web-search)
- [Anthropic: Web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)
- [Google AI: Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search)
- [Google AI: Gemini 3 developer guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [Anthropic: Models overview](https://platform.claude.com/docs/en/models/overview)
- [Context7: CLI](https://context7.com/docs/clients/cli)
- [Context7: Add private sources](https://context7.com/docs/howto/private-sources)
- [Kubernetes releases](https://kubernetes.io/releases/)
- [Amazon EKS Kubernetes version lifecycle](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html)
