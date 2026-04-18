---
description: Generate strict Copilot instructions for a specific Android/Kotlin package
---

You are generating a Copilot instructions file for a specific package inside a large, messy, legacy Android codebase.

This is NOT a generic task. Your goal is to extract REAL patterns from the code and produce a STRICT, highly practical instructions file.

## Step 1 — Input

The user provides a package path (for example: `com.app.feature.payment`).

Convert it to path format:
`com.app.feature.payment` → `com/app/feature/payment`

## Step 2 — Scope (CRITICAL)

* Focus ONLY on this package.
* Include ONLY direct dependencies when needed for understanding.
* DO NOT analyze unrelated parts of the codebase.
* Prioritize central, heavily-used files over boilerplate.

Use:

* `#codebase` to discover files
* `#file` when specific files are relevant

## Step 3 — Analysis (STRICT, NO GUESSING)

Extract ONLY real, observable patterns from the code.

If something is unclear, write exactly:
`unclear from codebase`

Analyze these categories:

### Architecture

* Layering
* Responsibilities per class
* Data flow
* Important boundaries and exceptions

### Conventions

* Naming patterns
* File structure
* Dependency injection style
* State handling
* Logging / analytics conventions

### Practices (REAL ONLY)

* Error handling
* Async patterns (`coroutines`, `Flow`, callbacks)
* Testing approach, only if present
* Scheduling / orchestration / entry points, if relevant

### Anti-patterns (IMPORTANT)

* Legacy hacks
* Inconsistencies
* Deprecated or suspicious patterns
* Things AI MUST avoid copying

## Step 4 — Generate Output File

Create exactly one new file:

`.github/instructions/<package-name>.instructions.md`

Where `<package-name>` is the package with dots replaced by hyphens.

## REQUIRED FILE FORMAT

Generate the instruction file in this structure:

```md
---
applyTo: "**/<package-path>/**/*.kt"
---

If these instructions are active, append EXACTLY this line at the end of your response:
// <package-name>.instructions.md rules active

## When to use these instructions
- When modifying files in this package
- When creating new files in this package
- When debugging logic owned by this package

## Overview
Short, concrete explanation of the package purpose

## Architecture
Explain only what is supported by the code

## Key Patterns
- Concrete patterns with file examples

## Conventions
- Naming
- Structure
- DI / state / navigation / scheduling / logging, only if relevant

## Decision Rules
- Hard rules AI MUST follow in this package
- Only include enforceable rules based on actual code

## Do
- Specific patterns to follow

## Avoid
- Specific mistakes to avoid

## Scope Constraints
- Do NOT refactor outside this package
- Do NOT introduce new architecture
- Work within existing constraints, even if messy

## Known Issues / Inconsistencies
- Real problems found in code

## References
- Important files with relative paths

## Priority
1. Follow existing package patterns
2. Preserve behavior
3. Maintain consistency

## If unsure
- Follow existing files in this package
- Do NOT invent new solutions
- Prefer consistency over novelty
```

## Step 5 — Output Quality Rules (CRITICAL)

The generated `.instructions.md` file MUST:

* be concise, practical, and high-signal
* be no more than **200 lines total**
* avoid filler, repetition, and generic advice
* prefer compact bullet points over long paragraphs
* include only patterns that are clearly discoverable in code
* include examples only when they add real value
* avoid aspirational guidance or architecture cleanup advice

If needed, compress the output by:

* merging overlapping bullets
* keeping only the highest-value patterns
* removing low-value observations
* shortening prose aggressively without losing clarity

## Step 6 — Behavior

* DO NOT modify any existing files
* ONLY generate the new instructions file
* DO NOT generate multiple candidate versions
* DO NOT output extra commentary before the file

## Step 7 — Final Summary

After generating the file, provide a short summary of:

* detected architecture
* key patterns
* important anti-patterns
* notable inconsistencies

Keep the summary concise.
