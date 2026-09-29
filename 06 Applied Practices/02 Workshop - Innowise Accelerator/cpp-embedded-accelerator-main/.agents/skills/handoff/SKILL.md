---
name: handoff
description: "Compact an in-progress task into a resumable handoff before context reset, agent/model switch, interruption or end of day. Update the existing hidden task STATE.md rather than creating competing state."
---

# Handoff

If a task workspace exists, update its `STATE.md` first, then optionally add `handoff.md` beside it. Otherwise provide the handoff in chat.

Include goal, current phase, repo/branch/baseline/dirty state, approved gates, decisions, files/symbols touched, commands and PASS/FAIL/NOT RUN evidence, failed hypotheses not to retry, blockers/unknowns, and the smallest next action. Reference existing spec/plan/diagnosis/verification files instead of duplicating them.

Never copy credentials, secrets, private dumps or unrelated client data into the handoff.
