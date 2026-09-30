# Shared implementation process (coder agents)

Read by `kmp-agent`, `ios-agent`, `android-agent`, `backend-agent` and `web-agent` before opening any source file. Stack-specific commands and rules are in each agent's own file.

## Step 0: context, cheaply

0. Apply "Repo preconditions" from vault-conventions to every repo you'll touch. Nothing else happens until they pass.
1. Read `<PLUGIN_ROOT>/resources/vault-conventions.md`, sections "Handback" and "HTML files".
2. Read the spec sections you need, and nothing else:
   `python3 <PLUGIN_ROOT>/resources/scripts/section.py <TASK_DIR>/spec.html goal scope acceptance-criteria edge-cases dependencies plan-<your stack>`
   Exit 3 means a section is missing: return BLOCKED naming it.
3. Repo instructions: read the repo's root `CLAUDE.md` and the `CLAUDE.md` of each module you'll touch. List the repo's skills without opening them:
   `for f in <repo>/.claude/skills/*/SKILL.md; do echo "$f: $(grep -m1 '^description:' "$f")"; done`
   Open only skills that clearly match the task.
4. Domain context skills (mobile): if the spec touches one of these areas, invoke the matching skill before exploring code: shopping list → `shopping-list-context`; SubitoGo, self-scanning, POS → `subito-context`; sponsored products, Criteo → `sponsored-products-context`; analytics, screen tracking → `tracking-context`; Cloudinary or Rokka images → `cloudinary-image-context`.
5. Check `VAULT/ADRs/` file names; read an ADR only if its title matches the area you're changing.
6. Explore with `grep -rn` and targeted reads (≤ 120-line windows). Never read whole generated, minified or lock files, and skip `node_modules/`, `target/`, `build/`, `dist/`.

## Step 1: implement

For each acceptance criterion, then each edge case, in order:
1. Write one failing test that pins the criterion. Run it and confirm it fails for the right reason (missing behaviour, not a typo or a missing import).
2. Write the minimum production code to make it pass. Re-run it.
3. Refactor only on green.

Your agent file may override this loop with a stricter build discipline (iOS does). If TDD doesn't apply (pure refactor, config or asset only), say why in `NOTES`.

Once every criterion has a passing test, run your agent's full verification command once. On failure, fix and run it once more. If it still fails, return BLOCKED with a summary of the failures.

## Step 2: hand back

Standard handback, plus:

```
PLAN: <at most 8 bullets: what you changed and where, for spec.html#plan-<stack>>
```

## Rules

- Stay inside your stack's directories and the repos in the dispatch prompt. A needed change elsewhere → BLOCKED.
- Spec ambiguous, contradicts an ADR, or needs an architectural decision → BLOCKED with the question. Never invent requirements.
- Never write to the vault. Never commit or push. No new third-party dependency without an ADR.
- Comments only for a *why* that code can't express; no narration comments; no commented-out code.
- Follow the patterns of neighbouring files for naming, structure and test style.
