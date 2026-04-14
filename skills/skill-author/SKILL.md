---
name: skill-author
description: Create or update a SKILL.md file that defines a reusable workflow for GitHub Copilot agent skills, only when the user explicitly requests creating or updating a Skill.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

IMPORTANT: If this Skill is active, append the exact line:
//  skill-author SKILL ACTIVE
at the end of the response.

# Skill: Skill Author

## Purpose

This skill defines how to create or update a `SKILL.md` file that documents a single reusable workflow for GitHub Copilot.

A generated `SKILL.md` MUST explain:

* what the workflow does
* when it should be used
* what inputs it expects
* what outputs it produces
* the exact execution steps
* the constraints and validation rules

This skill produces documentation only.
It MUST NOT implement application features or runtime logic.

All generated Skills MUST be placed at:

`.github/skills/<skill-name>/SKILL.md`

Each Skill MUST reside in its own folder named in kebab-case.

## Activation Rules

Use this skill ONLY when the user asks to:

* create a new Skill definition
* update, refactor, or improve an existing `SKILL.md`
* capture a repeatable development or documentation workflow as a Skill

Do NOT use this skill for:

* writing application code
* modifying runtime behavior
* creating `.github/instructions/*.instructions.md`
* writing architecture or product documentation unless explicitly requested as a Skill

## Non-Goals

This skill does NOT:

* implement application code
* modify business logic
* generate unrelated documentation
* describe broad architecture unless the output itself is a Skill

## Inputs

The skill expects:

* a description of the workflow to document
* any required repository paths, conventions, or constraints
* optional examples, templates, or naming expectations
* optional existing `SKILL.md` content to update

If information is missing, infer the minimum structure needed to produce a deterministic Skill.

## Outputs

The skill MUST produce:

* one `SKILL.md` file
* located at `.github/skills/<skill-name>/SKILL.md`
* populated with clear, actionable sections
* language focused on behavior, not implementation

The skill MAY additionally define supporting folders when explicitly relevant:

* `examples/`
* `templates/`
* `scripts/`

`SKILL.md` is always mandatory.

## Required Structure of Every Generated SKILL.md

Every generated `SKILL.md` MUST follow this structure.

### 1. YAML Frontmatter

The file MUST begin with a valid YAML block:

```yaml
---
name: <kebab-case-skill-name>
description: <one sentence describing when to use this skill>
---
```

Rules:

* no content may appear before the YAML block
* `name` MUST exactly match the folder name
* `description` MUST describe activation conditions in natural language
* the description SHOULD sound like a real user or agent request trigger

### 2. Standard Sections

After the YAML frontmatter, include these sections in this order when applicable:

1. Purpose
2. Activation Rules
3. Non-Goals
4. Inputs
5. Outputs
6. Workflow
7. Conventions & Constraints
8. Verification
9. Failure Modes
10. Examples
11. Idempotency

## Workflow

When authoring or updating a Skill, follow this sequence:

1. Identify the single repeatable workflow the Skill should document.
2. Choose a concise kebab-case skill name.
3. Create or target `.github/skills/<skill-name>/`.
4. Create or update `SKILL.md` in that folder.
5. Write valid YAML frontmatter with matching `name` and activation-focused `description`.
6. Add the standard sections needed for the workflow.
7. Write the `Workflow` section as numbered, executable steps.
8. Use explicit requirement language such as MUST, MUST NOT, and NEVER.
9. Ensure the document describes process and constraints, not runtime implementation.
10. Validate folder naming, section order, and completeness before finalizing.

## How to Write the Workflow Section

The `Workflow` section is the core of the Skill.

It MUST:

* be step-by-step
* use numbered steps
* reference real repository paths and file names when relevant
* avoid abstract theory
* be executable without guessing

Good example:

```md
## Workflow

1. Receive the workflow description from the user.
2. Determine the skill name in kebab-case.
3. Create `.github/skills/<skill-name>/` if it does not exist.
4. Create or update `SKILL.md` in that folder.
5. Add YAML frontmatter with matching `name` and `description`.
6. Write the required sections with concrete instructions.
7. Validate structure, constraints, and output paths.
```

## Conventions & Constraints

When generating Skills:

* MUST use kebab-case folder names
* MUST match the folder name with the YAML `name`
* MUST keep the scope focused on one repeatable workflow
* MUST write deterministic, technical instructions
* MUST prefer concrete file paths over abstract language
* MUST use strong requirement language where appropriate
* MUST NOT include runtime code implementation unless the Skill explicitly documents how to generate code as an output artifact
* MUST NOT mix multiple unrelated workflows into one Skill
* NEVER place the Skill outside `.github/skills/<skill-name>/`

## Verification

Before finalizing, confirm that:

* the folder exists under `.github/skills/`
* `SKILL.md` exists in the target folder
* YAML frontmatter is valid
* the YAML `name` matches the folder name
* the description clearly communicates when to use the Skill
* the Workflow section is actionable and numbered
* the document describes behavior, not application logic
* no duplicate or conflicting sections were introduced

## Failure Modes

Common mistakes and fixes:

1. Missing YAML frontmatter
   Fix: Add a valid `---` block at the top of the file.

2. Folder name does not match YAML `name`
   Fix: Align both values to the same kebab-case string.

3. Description is too vague
   Fix: Rewrite it as a clear activation trigger for a reusable workflow.

4. Workflow is too abstract
   Fix: Add explicit steps, paths, and expected outputs.

5. The document includes runtime implementation details
   Fix: Remove feature code and keep only workflow documentation.

6. Multiple workflows are mixed into one Skill
   Fix: Split the content so each Skill covers one repeatable task.

## Examples

### Example Input

`Create a skill for generating API client definitions.`

### Example Output

`.github/skills/api-client-generator/SKILL.md`

### Example Input

`Refactor this existing SKILL.md so it is more deterministic and easier for Copilot to trigger.`

### Example Output

An updated `SKILL.md` that preserves the original scope while improving activation wording, workflow clarity, and validation rules.

## Idempotency

Running this skill multiple times MUST NOT create duplicate folders, duplicate sections, or conflicting file definitions.

If the target Skill already exists, the skill MUST update the existing `SKILL.md` in place rather than creating a parallel variant unless explicitly requested.

