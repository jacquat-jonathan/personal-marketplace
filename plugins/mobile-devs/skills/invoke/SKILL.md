---
name: invoke
description: Plan, implement, review, test, and document a mobile feature using the mobile development agent team.
argument-hint: <feature request>
disable-model-invocation: true
---

# Mobile feature workflow

Delegate the following request to `mobile-devs:orchestrator-agent`, which owns the full spec → KMP → iOS/Android → review → QA → docs pipeline:

$ARGUMENTS

Do not duplicate the orchestrator's workflow here — invoke it and let it drive. This command exists only as an explicit manual entry point; in normal use, talk to the orchestrator agent directly and it will engage without needing this command.
