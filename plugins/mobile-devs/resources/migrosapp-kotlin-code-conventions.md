---
title: migrosapp — Enforced Kotlin Code Conventions
tags: [migrosapp, kotlin, kmp, android, architecture, konsist, detekt, ktlint, conventions]
source: konsist-test/, detekt-config.yml, custom-ktlint-ruleset/, .editorconfig
---

# migrosapp (Kotlin) — Good Practices Enforced by Tooling

Derived from the Konsist architecture tests, the detekt configuration, and the custom ktlint ruleset in the `migrosapp` monorepo. These are the rules the build actually enforces — not aspirational guidelines.

## 1. Architecture (Konsist — `konsist-test/`)

### Layering — `architecture/Architecture.kt`
- `domain` depends on **nothing** (no framework, no data, no presentation)
- `data` → depends only on `domain`
- `presentation` → depends only on `domain`
- `data` and `presentation` may never reference each other

### Domain layer
- No `model` packages in domain — use `entities`
- Entities: `data` / `sealed` / `abstract` / `final` modifiers only
- Entity interfaces must be `sealed`
- `object`s in entity packages must be `companion` objects
- *(Disabled but intended)* entities must have no nullable properties
- Use cases live in `..usecase..` and expose exactly **one** public function named `invoke`
- `*Repository` interfaces live in `..repository..`
- `*Service` lives in `..service..`; must not take use cases or entities as constructor params

### Data layer
- `*Dto` classes live in `..dto..`
- DTO↔domain converters live in the **same file as the DTO** — never a separate `*Converter.kt`
- `List<ItemDto>` properties must use `ItemDtoListSerializer` (defensive deserialization)
- `*Repository` implementations live in `..repository..`

### General
- Package name must match the file path
- **No `utils` packages** — zero exceptions allowed

## 2. KMP conventions

- **Never `runCatching` / `mapCatching` inside `suspend` or `inline` functions** — they swallow `CancellationException`. Use `runCatchingCancellable`.
- Log tags: no property named `TAG`; a `LOGGING_TAG` value must equal the class name
- Tests use **AssertK**, never `kotlin.test.assert*`

## 3. Android conventions

- The `ViewModels` accessor may only be imported from `*KmpViewModelFactory*` (a small legacy baseline exists)
- Never use `pluralStringResource(` / `getQuantityString(` — use `pluralIcuStringResource` / `getPluralIcuString`, because the translation pipeline converts `<plurals>` to ICU `<string>`

## 4. Custom ktlint rules (`migros-app-custom-rules`)

- **`MigrosLogger` only** — no `println`, `print`, `printStackTrace`
- **Design system over Material 3** — 24 M3 components banned outside the design-system module (`Button→MButton`, `Scaffold→MScaffold`, `MaterialTheme→MigrosTheme`, `TextField→MTextField`, …)
- **Semantic color tokens** — raw palette references (`Color.MGrey`, …) banned inside the design system; use `MigrosTheme.colorScheme.*`. Escape hatch: `@IgnoreColorPaletteUsageRestriction`
- Android modules cannot depend on `migrosapp-library:main`
- KMP build-script dependency blocks must be alphabetically sorted

### `.editorconfig`
- `android_studio` code style, `max_line_length = 150`, indent 4
- No star imports, no trailing commas
- Force multiline signatures: functions at ≥2 params, classes at ≥3 params
- `Composable` exempt from function naming rules

## 5. Detekt (`detekt-config.yml`, `maxIssues: 0`)

### Stricter than defaults
- **`NamedArguments` threshold 2** — any call with ≥2 arguments requires named arguments
- **`InjectDispatcher`** — never hardcode `Dispatchers.IO / Default / Unconfined`
- Exception hygiene: no swallowed, rethrown, or overly generic exceptions; no throw-without-message; `ThrowsCount` max 2
- Null safety: `UnsafeCallOnNullableType`, `UnsafeCast`, `UnnecessaryNotNullOperator`, `MapGetWithNotNullAssertionOperator`
- `MagicNumber` (only `-1, 0, 1, 2, 100` allowed), `VarCouldBeVal`, `WildcardImport`, `MayBeConst`
- `ForbiddenComment` on `TODO:` and `FIXME:`
- Idiomatic Kotlin: `UseRequire`, `UseCheckOrError`, `UseIsNullOrEmpty`, `UseOrEmpty`, `UseAnyOrNoneInsteadOfFind`, `ObjectLiteralToLambda`

### Deliberately relaxed (pragmatic, not aspirational)
- `LongParameterList` 14/14, `LongMethod` 75, `TooManyFunctions` per file 40, `LargeClass` 600
- Off: KDoc requirements, `MatchingDeclarationName`, `LateinitUsage`, `Deprecation`, `ReturnCount`, `MaxLineLength` (ktlint owns it)

## 6. Escape hatches — debt, not approved patterns

- `detekt-baseline.xml` — 279 suppressed findings
- `@IgnoreColorPaletteUsageRestriction`
- The `ViewModels` import baseline in `AndroidCodingConventionsTest`
- The `@Disabled` entity-nullability Konsist test

## Related
- [[migrosapp-ios-code-conventions]]
- `migrosapp/CLAUDE.md` — build/test commands and architecture overview
- `make test.konsist`, `make lint.kotlin`, `./detektw`
