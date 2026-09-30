---
name: review
description: Review a dev-team task after execution — spec-review-agent checks the work against the spec, then qa-agent runs the tests for implement/ktlo tasks. Stage 4 of the dev-team workflow.
argument-hint: [slug]
model: sonnet
disable-model-invocation: true
---

# /dev-team:review

`PLUGIN_ROOT` is two directories above this skill's base directory. Read `<PLUGIN_ROOT>/resources/vault-conventions.md`, resolve the task, and check the status (accepts `executed`).

1. Read `type`, `tier`, `stacks` and `repos`. Build `CHANGED_FILES` as the union of every file listed in `changes.md`.
2. Dispatch `dev-team:spec-review-agent` (model `sonnet`) with the dispatch header, `REPOS` and `CHANGED_FILES`. Log it.
   - FAIL → leave the status unchanged, show the blockers, and say the next step is `/dev-team:execute <slug>`. Stop.
   - BLOCKED → show the question and stop.
3. implement / ktlo only: dispatch `dev-team:qa-agent` (model `sonnet`) with the dispatch header, `STACKS`, `REPOS` and `CHANGED_FILES`. Log it.
   - FAIL (product defect) → leave the status unchanged, show the failures, and say the next step is `/dev-team:execute <slug>`. Stop.
   - BLOCKED (environment) → show what the user needs to fix, and stop.
4. Everything PASS → `frontmatter.py set … status reviewed`. Say the next step is `/dev-team:document <slug>`.
