---
name: archive
description: Archive a finished dev-team task after the user confirms it shipped — keep only summary.html, move deliverables to Knowledge, update the index — and list stale active tasks. Final stage of the dev-team workflow.
argument-hint: [slug]
model: haiku
disable-model-invocation: true
---

# /dev-team:archive

`PLUGIN_ROOT` is two directories above this skill's base directory. Read `<PLUGIN_ROOT>/resources/vault-conventions.md`, resolve the task, and check the status (accepts `done`).

1. Refuse, deleting nothing, if `<TASK_DIR>/summary.html` is missing ("Run /dev-team:document first"), or if `TASK_DIR` isn't inside `VAULT/Work/_active/` or `VAULT/KTLO/`.
2. Ask: "Has <title> been merged or shipped?" (implement/ktlo) or "Is <title> final?" (analyze/document). Anything but an explicit yes → stop.
3. Show what will be kept and what deleted (`ls -R <TASK_DIR>`), and ask "Archive and delete the rest?" Explicit yes only.
4. Dispatch `dev-team:cleaner-agent` (model `haiku`) with the dispatch header and `SLUG`, `TITLE`, `INITIATIVE`, `YEAR` (the current year). Log to the index only (the task's `log.md` is being deleted).
5. If the handback says `INITIATIVE_EMPTY: yes`, ask whether to delete the now-empty initiative folder, and delete it only on yes.
6. If `STALE` lists tasks, show them (slug, status, last change) and ask about each: "Leave", or "Archive now" (only for tasks at `done`; that runs this command for that slug). Never delete stale tasks any other way.
