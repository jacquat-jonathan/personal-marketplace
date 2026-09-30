---
name: document
description: Write the final documentation for a reviewed dev-team task — summary.html, the Features note, and an ADR draft if the user agrees. Stage 5 of the dev-team workflow.
argument-hint: [slug]
model: haiku
disable-model-invocation: true
---

# /dev-team:document

`PLUGIN_ROOT` is two directories above this skill's base directory. Read `<PLUGIN_ROOT>/resources/vault-conventions.md`, resolve the task, and check the status (accepts `reviewed`).

1. Dispatch `dev-team:docs-agent` (model `haiku`) with the dispatch header and `MODE: summary`. Log it. BLOCKED → show it and stop.
2. If the handback says `ADR_NEEDED: yes — <decision>`, ask "Draft an ADR for: <decision>?" with options "Draft ADR" and "Skip". On "Draft ADR", dispatch `dev-team:docs-agent` with model `sonnet` and `MODE: adr`, `DECISION: <decision>`. Log it.
3. `frontmatter.py set … status done`. Report the paths written. Say that once the work is merged or shipped (implement/ktlo), or final (analyze/document), the next step is `/dev-team:archive <slug>`.
