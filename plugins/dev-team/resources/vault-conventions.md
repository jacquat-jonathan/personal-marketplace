# Vault conventions (dev-team)

Read by every dev-team skill and agent. It defines where task files live, their formats, who writes them, and how status moves.

## Paths

- `VAULT` = `/Users/jonathan.jacquat/Documents/Obsidian/Migros Online/MO/_AI`
- Repos: `~/migrosonline/<repo>/`. Mobile: `~/migrosonline/migrosapp` (`migrosapp-ios/`, `migrosapp-android/`, `migrosapp-library/`). Web: `~/migrosonline/website-js`.
- `PLUGIN_ROOT`: skills compute it as two directories above their own base directory ("Base directory for this skill: …/skills/<name>"). Agents receive it in the dispatch header.
- Scripts: `<PLUGIN_ROOT>/resources/scripts/`. Templates: `<PLUGIN_ROOT>/resources/templates/`.
- Never write inside `MO/Human/` or `MO/Skills/`.

## Task folder (`TASK_DIR`)

| Type | Location |
|---|---|
| implement, analyze, document | `VAULT/Work/_active/<slug>/`, or `VAULT/Work/_active/<initiative>/<slug>/` |
| ktlo | `VAULT/KTLO/<slug>/` |

| File | Format | Written by |
|---|---|---|
| `goal.md` | md | ideate; frontmatter changed only by skills, only with `frontmatter.py` |
| `<topic>.md` companion notes (`context.md`, `constraints.md`, `interview.md`, …) | md | ideate, spec skill |
| `log.md` | md | skills only |
| `changes.md` | md | execute skill only |
| `findings.md` | md | analyst-agent |
| `spec.html` | html | spec-agent; execute skill updates `#plan-<stack>` blocks |
| `review.html` | html | spec-review-agent |
| `qa.html` | html | qa-agent |
| `summary.html` | html | docs-agent |
| `deliverables/` | html, `.canvas` | analyst-agent, writer-agent |

An initiative folder holds only `index.md` (links to its subtasks) and subtask folders.

Long-lived notes outside task folders: `VAULT/Features/<slug>.md` (md, docs-agent), `VAULT/ADRs/ADR-NNNN-<slug>.md` (md, docs-agent), `VAULT/Knowledge/` (archived deliverables land in `Knowledge/<slug>/`).

## goal.md

```markdown
---
title: <Name as the user wrote it>
type: implement
status: idea
tier:
complexity:
stacks: []
repos: []
jira:
initiative:
created: 2026-09-30
---

# Goal

<Rewritten goal, 1–3 sentences>

## Notes

- [[context]]
```

| Key | Values |
|---|---|
| `type` | `implement`, `analyze`, `document`, `ktlo` |
| `status` | `idea`, `specified`, `approved`, `executed`, `reviewed`, `done` |
| `tier` | empty, `spike`, `bounded`, `architectural` |
| `complexity` | empty or `high` |
| `stacks` | list of `ios`, `android`, `kmp`, `backend`, `web` |
| `repos` | list of folder names under `~/migrosonline/` |
| `initiative` | parent folder name when nested, else empty |

## Status machine

```
idea ──/spec writes spec.html──▶ specified ──user approves in /spec──▶ approved
approved ──/execute, every agent DONE──▶ executed ──/review PASS──▶ reviewed
reviewed ──/document──▶ done ──/archive──▶ (folder archived)
```

Read with `python3 <PLUGIN_ROOT>/resources/scripts/frontmatter.py get <TASK_DIR>/goal.md status` and write with `… set <TASK_DIR>/goal.md status <value>`. Never edit frontmatter by hand.

| Command | Accepts status |
|---|---|
| `/dev-team:spec` | `idea`, `specified` |
| `/dev-team:execute` | `approved`, `executed` (re-run after a failed review) |
| `/dev-team:review` | `executed` |
| `/dev-team:document` | `reviewed` |
| `/dev-team:archive` | `done` |

If the status isn't accepted, stop without changing anything. Say: "`<slug>` is at `<status>`; run `<next command>` next." Next command by status: idea → `/dev-team:spec`, specified → `/dev-team:spec` (to approve), approved → `/dev-team:execute`, executed → `/dev-team:review`, reviewed → `/dev-team:document`, done → `/dev-team:archive`.

## Resolving a task

Reject an argument that contains `..` or starts with `/`: say it must be a slug or `<initiative>/<slug>`, and stop.

With an argument `<arg>` (a slug, or `<initiative>/<slug>`), collect every existing match among:
1. `VAULT/Work/_active/<arg>/goal.md`
2. `VAULT/KTLO/<arg>/goal.md`
3. `VAULT/Work/_active/*/<arg>/goal.md`

- One match: that folder is `TASK_DIR`.
- Several matches: list them and ask the user which one (AskUserQuestion). Never pick one yourself.
- None: repeat the search for the folder without `goal.md`. If a folder is found, follow "Legacy folders". Otherwise say no task was found and suggest `/dev-team:ideate`.

Without an argument, run `find "VAULT/Work/_active" "VAULT/KTLO" -maxdepth 3 -name goal.md`, keep the tasks whose status this command accepts, and ask the user to pick with AskUserQuestion (up to 4 options, most recently modified first; they can type another slug under "Other"). If there are none, say so and stop.

## Legacy folders

A task folder without `goal.md` (created before dev-team): ask "This folder has no goal.md. Create one from its existing files?" If yes, read the file names plus the first 20 lines of the main note, ask the user for type and current status, and write `goal.md` using the schema above. Never rename, move or rewrite existing files.

## Dispatch header

Every agent dispatch prompt starts with:

```
PLUGIN_ROOT: <absolute path>
VAULT: /Users/jonathan.jacquat/Documents/Obsidian/Migros Online/MO/_AI
TASK_DIR: <absolute path>
TYPE: <type>
TIER: <tier>
```

followed by the agent-specific inputs. Agents read `<PLUGIN_ROOT>/resources/vault-conventions.md` first.

## Handback

Every agent ends its reply with exactly this block:

```
STATUS: DONE | BLOCKED | PASS | FAIL
CHANGED_FILES: <comma-separated absolute paths, or none>
TESTS_RUN: <commands, or none>
TEST_RESULT: PASS | FAIL | n/a
NOTES: <at most 10 lines>
```

Workers return DONE or BLOCKED; reviewers and QA return PASS, FAIL or BLOCKED. BLOCKED must name the exact question or missing input the user has to resolve. Agent-specific extra fields go after `NOTES`.

## HTML files

- Start from the template: `cp` it into place, then replace `{{TITLE}}`, `{{TYPE}}` and `{{DATE}}` (YYYY-MM-DD) with Edit.
- Never change the `<style>` block, never restyle, never remove or rename an element that has an `id`, never add scripts or external resources.
- A section with nothing yet contains `<p class="empty">Nothing yet.</p>`. Replace that placeholder with content; leave it in sections that have nothing.
- Allowed markup inside sections: `p`, `ul`/`ol`/`li`, `table`/`tr`/`th`/`td`, `pre`/`code`, `h3`, `strong`, `em`, `a`, `div` with an id. Close every tag you open.
- Code references are written as `<code>path/File.kt:42</code>`, with the path relative to the repo root and the repo name first: `<code>checkout/service/src/main/java/…/CheckoutService.java:88</code>`.
- `review.html` and `qa.html` are append-only. `#verdict` is replaced on every run; each run adds `<article class="run" id="run-YYYYMMDD-HHMM">` as the first child of `#runs`. Older runs are never edited.
- Read with `python3 <PLUGIN_ROOT>/resources/scripts/section.py <file> <id> [<id>...]`. Open a whole HTML file only right before editing it. If `section.py` exits 3, a needed section is missing: return BLOCKED naming the id instead of guessing.

## log.md

One line per stage run, appended by the skill:

```
- 2026-09-30 14:12 · execute · ios-agent, android-agent (sonnet) · DONE · 6 files changed, tests pass
```

## changes.md

Appended by the execute skill after each run:

```markdown
## 2026-09-30 14:12 · execute
- ios: /Users/…/Checkout/OrderConfirmationView.swift, /Users/…/OrderConfirmationViewTests.swift
- android: /Users/…/OrderConfirmationScreen.kt
```

Review unions the files from every run.

## Work index

`VAULT/Work/_index.md`:
- ideate adds `- [[Work/_active/<path>/goal|<Title>]] — <type>` under `## Active`. For a nested task it also adds `- [[<slug>/goal|<Title>]]` to `<initiative>/index.md`.
- archive removes that line and adds `- [[Work/_archive/<YYYY>/<slug>/summary.html|<Title>]] — <type>` under `### <YYYY>` in `## Archived` (creating the heading if needed and removing a `_(none yet)_` line under it).
- KTLO tasks are not listed.
