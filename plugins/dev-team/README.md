# dev-team

One task folder per piece of work in the Obsidian vault, moved forward by one command per stage. Each command runs one stage, updates `status` in `goal.md`, and stops.

| Command | Does | Status after |
|---|---|---|
| `/dev-team:ideate` | Creates the task folder with `goal.md` and companion notes | `idea` |
| `/dev-team:spec [slug]` | Interviews you, writes `spec.html`, asks for approval | `specified` → `approved` |
| `/dev-team:execute [slug] [--deep]` | Implements (coders), analyses (analyst) or documents (writer) | `executed` |
| `/dev-team:review [slug]` | Checks the spec against the evidence; QA runs the tests for implement tasks | `reviewed` |
| `/dev-team:document [slug]` | Writes `summary.html`, the Features note, and an ADR draft if you agree | `done` |
| `/dev-team:archive [slug]` | After you confirm it shipped: keeps only the summary and deletes the rest | archived |

Task types: `implement`, `analyze`, `document`, `ktlo`. Stacks: `ios`, `android`, `kmp`, `backend`, `web`.

Models: Sonnet by default, Haiku for mechanical stages. Opus only with `--deep` or after you confirm.

Rules shared by every skill and agent: `resources/vault-conventions.md`.
