# C++ / Embedded Accelerator Instructions

Repository instructions, build files, CI, compiler/tool output, and target evidence override generic guidance here.

## Work safely

- Inspect the repository before changing it. Do not invent build systems, directories, target assumptions, or coding conventions.
- Verify facts from repository evidence when possible. Ask a human only for decisions, inaccessible facts, or authorization.
- Keep changes scoped; do not turn a task into an unrelated refactor.
- Treat client source, logs, dumps, symbols, tickets, generated context, and build artifacts as confidential.
- Do not read credentials, private keys, tokens, `.env`, `secrets/`, unrelated home data, or sibling client repositories.
- Do not upload client material or perform destructive Git/filesystem/device/firmware/production operations without explicit authorization.
- Never claim target behavior from host-only evidence.

## Engineering defaults

- Prefer simple, reviewable code over clever abstractions.
- Match the existing codebase before introducing new patterns.
- Make ownership, lifetime, state transitions, units, bounds, and failure behavior explicit.
- Avoid undefined behavior, dangling references, out-of-bounds access, data races, unchecked narrowing, and hidden blocking.
- Use RAII where the platform permits it and clean up correctly after partial initialization.
- Respect project policy for exceptions, RTTI, allocation, STL, ABI, packing, alignment, endianness, and compiler extensions.
- Validate external sizes and conversions before allocation, copy, parsing, indexing, or protocol handling.
- For concurrency/real-time code, consider lock ordering, shutdown, backpressure, priority inversion, allocation, latency, jitter, stack and queue limits.
- Keep hardware/platform-specific code behind narrow boundaries when practical.
- Optimize from measurements, not intuition.

## Skills

Use a skill only when it helps the current task; do not chain skills mechanically. The maintained core is:

- `requirements-clarifier`
- `systematic-debugger`
- `self-review`
- `code-reviewer`
- `verify`
- `reflect`

## Before claiming completion

Use only checks relevant to the change, but never silently skip a required one:

- configure/build succeeds where applicable;
- relevant tests pass;
- changed behavior has a credible regression signal, or the missing signal is explained;
- applicable formatting/lint/static analysis/compiler warnings/sanitizers pass;
- target-dependent claims have cross-build/simulator/target/HIL evidence at the required level;
- performance/resource claims are measured when they are acceptance criteria.

Report exact verification commands or methods as **PASS**, **FAIL**, or **NOT RUN**. Missing tooling or hardware is NOT RUN, never PASS. Do not bypass hooks with `--no-verify` or rewrite public history without explicit consent.
