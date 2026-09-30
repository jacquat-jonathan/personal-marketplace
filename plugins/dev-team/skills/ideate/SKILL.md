---
name: ideate
description: Start a new dev-team task in the Obsidian vault — a feature, fix, analysis, documentation or KTLO item. Asks only for what's missing (name, goal, type), rewrites the goal as an agent-ready outcome, and scaffolds goal.md plus companion notes. Use whenever the user wants to start a new idea, task, ideation or brainstorm for work.
argument-hint: [name and goal, any extra context]
model: haiku
---

# /dev-team:ideate

`PLUGIN_ROOT` is two directories above this skill's base directory. Read `<PLUGIN_ROOT>/resources/vault-conventions.md` first; it defines `VAULT`, the goal.md schema and the index rules used below.

## 1. Collect inputs

Take whatever the invocation already gives you: name, goal, type, Jira key, extra context. Ask only for what's missing, with one AskUserQuestion call:
- **name** (short title), and **goal** (what should be true when this is done). If the name is empty and the goal has several lines, the first line is the name.
- **type**, only if it can't be inferred. Infer implement for build/add/fix/change/migrate; analyze for analyze/investigate/why/how does/map/compare; document for document/explain/write up/present; ktlo if the user says KTLO or gives a KTLO-### key. If unsure, ask with the four types as options.

## 2. Place the task

- Slug: the name in lowercase kebab-case, at most 50 characters.
- ktlo → `TASK_DIR = VAULT/KTLO/<slug>/`, with no placement question.
- Otherwise, list initiative folders: folders directly under `VAULT/Work/_active/` that contain `index.md` and no `goal.md`. Ask "Where does this task belong?" with options: "Standalone task (Recommended)", "Start a new initiative (this is its first subtask)", and up to two existing initiatives whose names share a word with the task name (or the most recently modified ones).
  - Standalone → `VAULT/Work/_active/<slug>/`.
  - New initiative → ask for the initiative name, create `VAULT/Work/_active/<initiative-slug>/index.md` containing `# <Initiative name>` and a blank line, then `TASK_DIR = …/<initiative-slug>/<slug>/`.
  - Existing initiative → `…/<initiative>/<slug>/`.
- If `TASK_DIR` already exists, ask for a different name. Never overwrite.

## 3. Rewrite the goal

Rewrite the raw goal as an agent goal: outcome-oriented (the end state, not the activity), measurable (a verifiable result), scoped (what's in, and what's out if it helps), imperative, 1–3 sentences.
Example: "I want to understand how our users churn" → "Identify the three behavioural patterns that most often precede churn, producing a ranked list with supporting evidence for each."

## 4. Split extra context

Anything beyond the goal (background, constraints, links, research, assumptions, open questions, success criteria, scope notes) goes into small single-topic Markdown files in `TASK_DIR`: `context.md`, `constraints.md`, `assumptions.md`, `research.md`, `scope.md`, `questions.md`, `success-criteria.md`, or a new kebab-case name if none fits. Don't copy the goal into them. Skip this step when there's no extra context.

## 5. Write the files

- `mkdir -p "<TASK_DIR>"`
- `goal.md` using the schema in vault-conventions: `title` as the user wrote it, `type`, `status: idea`, `jira` if a key was given, `initiative` if nested, `created` today; leave the other keys empty. Body: `# Goal`, the rewritten goal, and `## Notes` with one `- [[<file-without-.md>]]` line per companion file (omit `## Notes` if there are none).
- `log.md`: `# Log` then a blank line, then `- <YYYY-MM-DD HH:MM> · ideate · — (haiku) · DONE · created`.
- Index: follow "Work index" in vault-conventions (skipped for ktlo).

## 6. Confirm

Reply with the task path, the companion files created, and the next step: `/dev-team:spec <slug>` (or `<initiative>/<slug>`).
