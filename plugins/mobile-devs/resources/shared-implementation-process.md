# Shared implementation process (iOS / Android / KMP agents)

This file is read by `ios-agent`, `android-agent`, and `kmp-agent` at the start of every task, before opening any source files. It holds the process that is identical across all three platform agents. Platform-specific tech stack, code rules, and test rules live in each agent's own file — only the shared workflow lives here.

---

## Step 0: domain context skills and code conventions

**Code conventions come first.** Before touching any source file, read your platform's enforced-conventions file:

- iOS → `${CLAUDE_PLUGIN_ROOT}/resources/migrosapp-ios-code-conventions.md`
- Android or KMP → `${CLAUDE_PLUGIN_ROOT}/resources/migrosapp-kotlin-code-conventions.md`

These are generated from the actual lint/architecture tooling (SwiftLint/SwiftFormat/Periphery/Tuist for iOS; Konsist/detekt/ktlint for Kotlin), not aspirational style guides — code that violates them fails CI even with passing tests. Your own agent file also points you at the correct one; this is just the canonical place that says to always do it.

This project has dedicated `*-context` skills that bundle module structure, backend wiring, key models, and known pitfalls for specific feature areas. If the spec touches one of these domains, invoke the matching skill via the Skill tool **before** reading the spec a second time or opening any source files:

- Shopping list / Einkaufsliste → `shopping-list-context`
- SubitoGo, self-scanning, POS → `subito-context`
- Sponsored products, Criteo, retail media beacons → `sponsored-products-context`
- Analytics events, screen view tracking, Firebase events → `tracking-context`
- Cloudinary / Rokka images, product / brand / category images → `cloudinary-image-context`

If the spec area is not listed above, scan the global skill list once for any `*-context` skill that might match before falling back to ad-hoc code exploration. Skipping this step is the most common cause of agents reinventing patterns the codebase already documents.

---

## Step 1: read before writing

1. Read `SPEC_PATH` fully before writing anything.
2. Check the vault's `ADRs/` folder for decisions relevant to this feature (architecture, patterns, third-party SDKs).
3. List the files you expect to create or modify, so the orchestrator knows the scope.
4. If you were handed `SHARED_KMP_FILES` (output of the KMP agent), read them before writing any platform binding code — do not re-derive shared models or repository contracts that already exist.

---

## Step 2: red-green-refactor loop

Work test-first. For every acceptance criterion in the spec (then every edge case), repeat this loop:

1. **Red.** Write one failing test that pins down the criterion. Use your agent's own "Test rules" section for naming/conventions.
2. Run that single test and confirm it fails for the *right* reason — asserts on missing behaviour, not a typo, missing import, or unresolved type/reference.
3. **Green.** Write the minimum production code needed to make the test pass. No speculative scaffolding for criteria you haven't tested yet.
4. Re-run the test and confirm it passes.
5. **Refactor.** Tidy production or test code if it improves clarity. Re-run the test after each non-trivial refactor — never refactor on red.

After every criterion and edge case has a passing test, run the broader test suite (your agent's own commands) to catch regressions. Fix any failures before handing back.

### When TDD does not apply

State explicitly in your handback notes if you took one of these paths and why:

- **Pure refactor with no behaviour change** — existing tests should already cover the behaviour. Don't write new ones; rely on the existing suite staying green.
- **Config / asset / build-script only edits** with no logic to test.
- **Throwaway prototype work** the orchestrator explicitly marked as exploratory.

For every other change, follow the loop. If you want to skip TDD for a different reason, escalate to the orchestrator instead of deciding unilaterally.

---

## Step 3: escalation rule

If something in the spec is ambiguous, conflicts with an ADR, or requires an architectural decision, **stop and escalate to the orchestrator** — never invent a solution, never make the call yourself.

---

## Shared "do NOT do" rules

- Do not modify anything in the Obsidian vault. It holds `spec.md`, `plan.md`, `review.md`, `qa.md`, `summary.md`, ADRs, and logs — all owned by the spec, review, QA, and docs agents. You read from it; you never write to it.
- Do not create `specs/`, `reviews/`, `qa/`, or `orchestrator-log.md` inside the project repo — those paths are deprecated and live in the vault.
- Do not make architectural decisions — raise them to the orchestrator.
- Do not add third-party dependencies without an ADR.
- Do not push or commit — the dev lead handles that.
- Avoid inline code comments (`//`, `/* */`, KDoc/doc-comments used as narration, etc.) as much as possible. Prefer self-explanatory names, small well-named functions, and clear structure over comments explaining *what* code does. Only exception: a comment is acceptable when it captures *why* a non-obvious decision was made and that reasoning cannot be expressed in code (e.g. a workaround for a platform bug, a deliberate deviation from the obvious approach). Never leave commented-out code.
