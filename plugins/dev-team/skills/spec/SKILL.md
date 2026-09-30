---
name: spec
description: Interview the user about a dev-team task and have spec-agent write spec.html, then ask for approval. Stage 2 of the dev-team workflow.
argument-hint: [slug]
model: sonnet
disable-model-invocation: true
---

# /dev-team:spec

`PLUGIN_ROOT` is two directories above this skill's base directory. Read `<PLUGIN_ROOT>/resources/vault-conventions.md`, then resolve the task ("Resolving a task") and check the status ("Status machine"; accepts `idea`, `specified`).

## 1. Existing spec

If the status is `specified` and `spec.html` exists, show the key sections (`section.py <TASK_DIR>/spec.html goal acceptance-criteria questions outline open-questions`; ignore MISSING for ids the type doesn't use). Then ask: "Approve", "Revise", or "Not now".
- Approve → go to step 6.
- Revise → ask what should change (one question at a time), append the answers to `interview.md` under `## Revision <date>`, then go to step 5 with `REVISION` set.
- Not now → stop.

## 2. Read the task

Read `goal.md` and every companion `.md` in `TASK_DIR`, including `interview.md` if present. Don't re-ask anything they already answer.

## 3. Interview

Ask one question per message, using AskUserQuestion with concrete options whenever you can. Propose drafts for the user to correct rather than asking open-ended questions. Stop when every section of the type's template can be filled. After 8 questions, record anything still open as an open question instead of asking more.

- **implement / ktlo**: stacks (multiSelect: ios, android, kmp, backend, web; add kmp when shared logic, networking or models change); repos for backend (check each exists under `~/migrosonline/`); entry points; happy path; edge cases (propose a list); acceptance criteria (propose observable, testable criteria); out of scope; dependencies (APIs, feature flags, other teams); whether it is unusually complex.
- **analyze**: the questions to answer (1–5, each answerable with evidence); repos; boundaries; output (report page, Obsidian canvas, or both); audience.
- **document**: audience; subject; sources (repos, `VAULT/Knowledge/` notes); outline (propose one); output (page, canvas, presentation-style page); length.

Save the answers to `<TASK_DIR>/interview.md`, as a heading per topic with the user's answers.

## 4. Classify

Pick a tier with a one-sentence reason: **spike** (feasibility question), **bounded** (well-scoped change to an existing flow), **architectural** (new subsystem, cross-stack, or an interface others depend on). Tell the user; they may override. Set `complexity: high` only if the user said it's unusually complex, or the tier is architectural and spans 3+ stacks. Write `stacks`, `repos`, `tier` and `complexity` with `frontmatter.py set` (lists as `[a, b]`).

## 5. Dispatch spec-agent

Dispatch `dev-team:spec-agent` (model `sonnet`) with the dispatch header, then:

```
TEMPLATE: <PLUGIN_ROOT>/resources/templates/ + spec-implement.html (implement, ktlo) | spec-analyze.html | spec-document.html
STACKS: <list>
REPOS: <list>
REVISION: <what changed, or none>
```

If it returns BLOCKED, show the question and stop. Otherwise set the status to `specified` and append to `log.md`.

## 6. Approval

Show the goal, the acceptance criteria / questions / outline, and the open questions (with `section.py`). If `#open-questions` has content other than the placeholder, resolve each question with the user, record the answers in `interview.md`, re-dispatch spec-agent with `REVISION`, and show the result again. A spec with open questions can't be approved.
Ask explicitly: "Approve this spec?" Only an explicit yes → `frontmatter.py set … status approved`, log it, and tell the user the next step is `/dev-team:execute <slug>`.
