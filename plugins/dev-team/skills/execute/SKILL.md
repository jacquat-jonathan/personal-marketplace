---
name: execute
description: Run the execution stage of a dev-team task — coder agents for implement/ktlo, analyst-agent for analyze, writer-agent for document. Sonnet by default; --deep uses Opus. Stage 3 of the dev-team workflow.
argument-hint: [slug] [--deep]
model: sonnet
disable-model-invocation: true
---

# /dev-team:execute

`PLUGIN_ROOT` is two directories above this skill's base directory. Read `<PLUGIN_ROOT>/resources/vault-conventions.md`, resolve the task, and check the status (accepts `approved`, `executed`).

## 1. Read the task

`frontmatter.py get` for `type`, `tier`, `complexity`, `stacks`, `repos`. If `stacks` is empty for implement/ktlo, stop: say no stacks are set and the user should rerun `/dev-team:spec <slug>` or set them. Dispatch nothing.

If the status is `executed`: if `review.html` doesn't exist, or the latest verdicts in `review.html` and `qa.html` are PASS, say the task is ready for `/dev-team:review` and stop. If the review PASS but QA not PASS (`qa.html` missing, or its verdict is BLOCKED), say `/dev-team:review <slug>` should run again once the environment is fixed, and stop. Otherwise this is a fix run: read `section.py <TASK_DIR>/review.html verdict` (and `qa.html verdict` if it exists) and set `REVIEW_FAILURES` to the listed blockers.

## 2. Choose the model

- `--deep` in the arguments → `opus`, with no further question.
- Otherwise, if `complexity: high`, or this is a fix run after a failed review → ask "Use Opus for this run? <one-sentence reason>" with options "Stay on Sonnet (Recommended)" and "Use Opus". Use Opus only on an explicit yes.
- Otherwise `sonnet`.

## 3. Dispatch

Each dispatch prompt has the dispatch header, then `REPOS`, `REVIEW_FAILURES`, and the extra inputs listed below. Pass the chosen model as the Agent `model` parameter.

- **implement / ktlo**
  1. If `kmp` is in `stacks`: dispatch `dev-team:kmp-agent` and wait. BLOCKED → show the question, log it, stop. Keep its `SHARED_KMP_FILES`.
  2. Dispatch every other stack's agent in one message so they run in parallel, with one exception: If `kmp` is in `stacks`, run ios-agent and android-agent one after the other (android first), because both rebuild the shared library in `~/migrosonline/migrosapp`; backend and web still run alongside them. Agents: `ios` → `dev-team:ios-agent`, `android` → `dev-team:android-agent`, `backend` → `dev-team:backend-agent` (REPOS without `migrosapp` and `website-js`), `web` → `dev-team:web-agent`. Pass `SHARED_KMP_FILES` to ios and android.
- **analyze** → `dev-team:analyst-agent`.
- **document** → `dev-team:writer-agent`.

## 4. Record

- For each coder handback, replace the `<ul>` inside `<div id="plan-<stack>">` in `spec.html` with the `PLAN` bullets as `<li>` items. You are the only writer of spec.html during this stage.
- Append one `## <YYYY-MM-DD HH:MM> · execute` block to `changes.md`, with one `- <stack>: <CHANGED_FILES>` line per agent (analyze/document: `- deliverables: …`).
- If two agents report the same file, flag it to the user as a scope overlap.
- Append one `log.md` line per agent (name, model, STATUS, a short note).

## 5. Finish

- Every agent DONE → `frontmatter.py set … status executed` (it may already be `executed`). Report the files changed per stack and the test results, and say the next step is `/dev-team:review <slug>`.
- Any agent BLOCKED → leave the status unchanged. Show each blocker's question. The user answers, and `/dev-team:execute` runs again.
