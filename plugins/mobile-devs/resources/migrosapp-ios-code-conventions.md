---
title: migrosapp — Enforced iOS Code Conventions
tags: [migrosapp, ios, swift, swiftlint, swiftformat, periphery, tuist, architecture, conventions]
source: migrosapp-ios/.swiftlint.yml, .swiftformat, .periphery.yml, CLAUDE.md, docs/conventions.md, Tuist/
---

# migrosapp (iOS) — Good Practices Enforced by Tooling

Derived from SwiftLint, SwiftFormat, Periphery, the Tuist project definitions and `docs/conventions.md` in `migrosapp-ios/`.

> Unlike Kotlin, **there is no Konsist equivalent on the Swift side** — architecture is enforced by Tuist target boundaries and code review, not by tests. See [[migrosapp-kotlin-code-conventions|the Kotlin note]] for the enforced-by-test counterpart.

## 1. Architecture & module structure

- **Clean Architecture + MVVM** for all new code and refactors
- Feature slice: `Feature/{View, ViewModel, Model, Repository}`
- **Coordinator pattern** for navigation
- KMP integration goes through `migros/migrosAppLibraryImpl/`; observe KMP StateFlows via NativeCoroutines / `KMPObservableViewModel`
- 31 Swift packages under `Packages/`. Package layering is enforced by Tuist targets:
  - `XxxPublicUI` — leaf UI, must **not** depend on Presentation
  - `XxxPresentation` — depends on PublicUI
  - `XxxTestSupport` — fakes and factories
  - `XxxPublicUITests` / `XxxPresentationTests`
- Package conventions: `product: .framework`, `bundleId: ch.migros.m-go.<Target>`, sources globbed `Sources/<Target>/**`, `disableSynthesizedResourceAccessors: true`, per-target scheme with scoped coverage
- `MigrosAppLibrary` is consumed only via `MigrosKMPSupport` (Tuist `.foreignBuild` target — no manual framework scripts)

## 2. Always / Never (from `CLAUDE.md` + `docs/conventions.md`)

### Always
- Use **Design System components** (`MButton`, `MTextField`, …) — never raw SwiftUI equivalents
- Protocols + constructor injection with default values
- `[weak self]` when a closure takes ownership
- Sort imports alphabetically
- iOS 17+ `onChange` (0-param or 2-param form)
- Use `./tuistw` / `make` targets — **never raw `xcodebuild`**

### Never
- **Avoid singletons.** Never access `.shared` directly — wrap it in a private property, use `EnvironmentProviding` or a feature DI container
- No singleton formatters (thread safety); minimize formatter instances
- `TrackingService` in SwiftUI previews (crashes live previews)
- Edit localization files directly — Lokalise + `L10n` from `MigrosTranslations`, `make update-strings`; plurals via `PluralizedLocalizationKey` / `Localized.pluralized()`
- `NSUserDefaults` directly — extend `UserSettings` / `AppSettings`, or use `MGOUserDatabase`
- Keychain access during app launch; use `KeychainSwift` and always handle errors
- `.registerCustomFonts()` outside `#Preview`
- `make build.ios-quick` after KMP changes
- `@InjectedObject(\.themeManager)` — enforced by a **SwiftLint custom rule**; use `@ObservedObject` with `Container.shared.themeManager()`

## 3. Coding conventions (`docs/conventions.md`)

**Code arrangement order** (convention only, not machine-enforced):
public types → private types → constant properties → public properties → private properties → funcs

- **Constants**: extract a magic number once it's used ≥2×; complex ones at first usage; never reuse a constant whose name doesn't match the new meaning
- **Booleans**: assertion-style, present tense, positively named; extract complex conditions into named bools; no `cond ? true : false`; use `if let message {}` shorthand
- **Functions/Views**: no selector (Bool) arguments; minimize arguments; don't overuse `onChange`/`didSet` for side effects
- **Data layer**: don't expose publishers for one-shot values — use async/await. Pick exactly one of `async throws` | `Result` | `AnyPublisher`, never combine
- **View models**: `@StateObject` (private) in the owner, `@ObservedObject` in children. No non-trivial logic in views. Share logic via repositories/use cases. **Never pass data via VM init or `StateObject(wrappedValue:)`** — pass params to a `load(...)` called from `.task`. No duplicated state properties. Prefer `init` over factory funcs
- **Shared components**: small and single-purpose; no flag-configured mega components; prefer explicit args or environment over singletons
- **Tracking**: each feature has a `tracking/` folder with a `Trackable` event factory (e.g. `Feature1Event`); parameter mapping lives in the factory, not in the view or VM
- **General**: no optional arrays (use empty); do conversions in DTO→domain mapping, not presentation; don't create entities with a single constant field; delete unused code

## 4. Testing

- XCTest, Given-When-Then, `sut` + mocks, nil out in `tearDown`
- Test naming: `test<FunctionName>_<doesThis>_when<That>`, one behaviour per test
- Standard test deps: `FactoryKit`, `ViewInspector`, `Fakery`, `SnapshotTesting`, `MigrosTestUtils`
- Mocks generated with **Cuckoo** (per-package `Cuckoofile.toml`)
- **`withTestFake` pattern** (`SharedContainer.withTestFake`): declare each dependency's test fake on the dependency in its `DIContainer`
  - Never `autoRegister()` / `AutoRegistering` — dead-stripped
  - Never `.onTest` for view models — it outranks `register {}`
  - Never register a single shared VM instance for N rendered views
- `AutoTestObserver` resets containers between tests and registers fonts for snapshots
- Snapshots in `__Snapshots__/`; `make clear-ios-snapshots` to reset
- ViewInspector: use `callOnChange(oldValue:newValue:)` for the 2-param modifier

## 5. SwiftLint (`.swiftlint.yml`, `strict: true`)

**Custom rule** — the only one:
- `no_injected_object_theme_manager` — bans `@InjectedObject(\.themeManager)` (error)

**Opt-in rules enabled**: `closure_spacing`, `contains_over_first_not_nil`, `discouraged_direct_init`, `discouraged_optional_boolean`, `empty_count`, `empty_string`, `explicit_init`, `fatal_error_message`, `first_where`, `for_where`, `joined_default_parameter`, `lower_acl_than_parent`, `multiline_parameters`, `operator_usage_whitespace`, `operator_whitespace`, `overridden_super_call`, `prohibited_super_call`, `sorted_first_last`, `unavailable_function`, `unneeded_parentheses_in_closure_argument`

**Thresholds**: `file_length` 800/1200 · `type_body_length` 500/800 (warning) · `type_name` 2–60

**Disabled**: `nesting`, `line_length` (SwiftFormat owns width), `identifier_name`, `xctfail_message`, `force_try`, `function_body_length`, `trailing_comma`. `force_cast` downgraded to warning; `force_unwrapping` deliberately not enabled.

**Analyzer rules configured** (`unused_declaration`, `unused_import`) but no make target runs `swiftlint analyze`.

## 6. SwiftFormat (`.swiftformat`)

Explicit `--rules` list — anything not listed is off.

- `--maxwidth 130` ("recommend 100, strictly enforce 130"), indent 4
- `--self remove`, `--commas always`, `--importgrouping testable-bottom`
- Wrapping: `before-first` for arguments/parameters/collections/conditions/typealiases; `--closingparen same-line`; `--wrapreturntype if-multiline`
- `--funcattributes`/`--typeattributes prev-line`, `--extensionacl on-declarations`, `--patternlet hoist`, `--redundanttype explicit`, `--guardelse next-line`, `--elseposition same-line`
- `markTypes`, `sortImports`, `sortDeclarations`, `sortTypealiases`, `enumNamespaces`, `strongifiedSelf`, `redundant*` family, spacing rules
- **`organizeDeclarations` is intentionally NOT enabled** — the arrangement order in `docs/conventions.md` is review-enforced only

## 7. Dead code — Periphery (`.periphery.yml`)

- `retain_public: false` → **public symbols are reported** too
- Retains: assign-only properties, files, ObjC-accessible/annotated, SwiftUI previews, Codable properties, unused protocol func params
- Run via `make detect-unused-code` or the `Periphery` Xcode target
- **Safety rule**: before deleting ANY iOS resource, grep `migrosapp-library/**/iosMain/**/*.kt` for the filename — KMP `iosMain` loads bundle resources via `NSBundle.mainBundle.pathForResource()`, invisible to Periphery
- ObjC is not analyzable by Periphery — manually check the bridging header, `[Class alloc]`, `@objc` selectors, and `.m` test fixtures loaded by name
- Known false positives: same-file protocol usage, conformance-only properties, `@objc` selectors, `Codable` properties
- Use `// periphery:ignore` for intentional retention

## 8. Build-level enforcement (Tuist)

- `SwiftLint` aggregate target runs before the app on **every local build** — but only on `git diff HEAD` changed files, and it **skips entirely on CI** (`$CI` set). Full strict linting is `make lint.swift`
- **`ConcurrencyTier`** ratchet per target: `.swift5Legacy` → `.swift6Targeted` → `.swift6Complete`
- Compiler warnings escalated to errors: `CLANG_WARN_DIRECT_OBJC_ISA_USAGE`, `CLANG_WARN_OBJC_ROOT_CLASS`, `GCC_WARN_ABOUT_RETURN_TYPE`; UB sanitizers, `-fstack-protector-all`
- Perf guards: `-warn-long-function-bodies=100`, `-warn-long-expression-type-checking=100`
- iPhone only (`TARGETED_DEVICE_FAMILY 1`); `MARKETING_VERSION` single source of truth in `BuildConstants.swift`
- Post-action strips nested `MigrosAppLibrary.framework` copies (CFBundleIdentifier collisions)
- External libraries need team review; package versions pinned exactly
- **No Dangerfile** — no PR-level automated enforcement

## 9. Known gaps / tensions

1. Code arrangement order documented but not machine-enforced
2. Build-phase SwiftLint runs on changed files only, and never on CI
3. `force_cast` is a warning and `force_unwrapping` is off, despite "avoid force unwrap" guidance — review-enforced
4. SwiftLint analyzer rules configured but never run
5. No architecture tests on the Swift side; `docs/navigation-refactor-plan.md` proposes a Konsist-style guard on route `==` that is not implemented
6. `ConcreteAppNavigationController` (~670 LOC) carries a file-wide `swiftlint:disable type_body_length`

## Related
- [[migrosapp-kotlin-code-conventions]]
- `migrosapp-ios/docs/conventions.md` — canonical 789-line conventions doc
- `migrosapp-ios/docs/dead-code-removal-findings.md` — Periphery campaign report + ObjC migration roadmap
- `migrosapp-ios/docs/navigation-refactor-plan.md` — proposed, not implemented
