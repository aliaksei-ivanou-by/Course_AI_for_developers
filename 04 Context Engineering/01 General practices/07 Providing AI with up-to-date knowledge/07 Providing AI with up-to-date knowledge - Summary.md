# Summary: Providing AI Agents with Up-to-Date Documentation

An AI model's knowledge cutoff is not a live software-version catalog and does not guarantee complete knowledge before that date. For changing APIs, cloud services, dependencies, and security guidance, inspect the repository's pinned versions and retrieve current evidence from authoritative sources before implementation.

Use web search to discover current pages, web fetch for a known URL, specialized retrieval such as Context7 for focused library documentation, vendor CLIs or APIs for target-environment reality, and controlled private retrieval for internal contracts. Verify the exact product, library ID, version, region, support tier, and source. “Latest” is not a sufficient requirement.

The lesson's Terraform/EKS experiment illustrates the benefit and limitation of grounding: documentation retrieval replaced an older memorized Kubernetes version, but the newer answer was not automatically correct. Upstream Kubernetes and Amazon EKS have different support lifecycles, and module, provider, account, region, and organizational constraints also matter.

Record the source URL, version, retrieval date, and decision rationale. Then validate generated code with deterministic tools and environment checks. Grounding improves evidence; it does not replace engineering review.
