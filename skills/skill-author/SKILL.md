---
name: skill-author
description: Use this skill when needed to create or update a *_SKILL.md file. 
  It produces a skill definition that explains a repeatable workflow (how to do a task) and when to use it.
---

IMPORTANT: If these Skill are active, append the exact line:
//  skill-author SKILL ACTIVE
at the end of your response.


# Skill: Skill Author

## Purpose

This skill defines how to create or update a `SKILL.md` file that documents a repeatable workflow or capability in the repository.

A SKILL.md captures:

* What the workflow is
* When it should be used
* What inputs it requires
* What outputs it must produce
* The exact step-by-step execution flow
* Constraints and validation rules

This skill produces documentation only.
It does NOT implement application features.
All generated Skills MUST be placed in:

.github/skills/<skill-name>/SKILL.md

Each Skill resides in its own folder named after the skill (kebab-case).

---

## Activation Rules

This skill MUST be used ONLY when the user asks to:

* Create a new Skill definition
* Update or refactor an existing SKILL.md
* Capture a repeatable development or documentation workflow as a Skill

This skill MUST NOT be used for:

* Writing application code
* Creating `.github/instructions/*.instructions.md`
* Writing architecture documents unless explicitly requested as a Skill

---

## Where the Skill Must Be Placed

When generating a new Skill:

1. Determine the skill name (kebab-case).
2. Create a folder: .github/skills/<skill-name>/
3. Inside that folder, create exactly one required file: SKILL.md

Optional additional folders inside the skill directory:

* examples/
* templates/
* scripts/

But SKILL.md is mandatory.

---

## Structure of Every Generated SKILL.md

Every SKILL.md MUST follow this structure.

### 1. YAML Frontmatter (Required)

The file MUST begin with:

---
name: <kebab-case-skill-name>
description: <one sentence describing when to use this skill>
---

Rules:

* No content before the YAML block
* `name` must match the folder name
* Description must define activation conditions

### 2. Required Sections (In This Order)

After the YAML block, the following sections can (not must) appear in order:

1. Purpose
2. Activation Rules
3. Inputs
4. Outputs
5. Workflow
6. Conventions & Constraints
7. Verification
8. Failure Modes

---

## Workflow for Creating a New SKILL.md

When authoring a new Skill, follow this deterministic sequence:

1. Identify the workflow being documented.
2. Choose a concise kebab-case name.
3. Create `.github/skills/<skill-name>/`.
4. Create `SKILL.md` inside that folder.
5. Add YAML frontmatter with correct name and description.
6. Write each required section clearly.
7. Ensure the Workflow section contains actionable steps.
8. Ensure constraints use MUST / MUST NOT / NEVER.
9. Confirm that the skill documents behavior, not application logic.

---

## How to Write the Workflow Section

The Workflow section is the core of a Skill.

It MUST:

* Be step-by-step
* Use numbered steps
* Reference real paths and files
* Avoid abstract theory
* Be executable without guessing

Example structure:

Workflow:

1. Receive task description from user.
2. Determine required modules and folders.
3. Create necessary directories.
4. Generate required files following naming conventions.
5. Validate structure.
6. Confirm output artifacts.

---

## Conventions & Constraints

When generating Skills:

* MUST use kebab-case folder names
* MUST match folder name with `name` in YAML
* MUST keep scope focused on one repeatable workflow
* MUST NOT include runtime code implementation
* MUST be deterministic and technical
* MUST avoid vague language

---

## Verification

After generating a Skill:

* Confirm folder exists under `.github/skills/`
* Confirm `SKILL.md` exists
* Confirm YAML frontmatter is valid
* Confirm all required sections exist
* Confirm workflow is actionable

---

## Failure Modes

Common mistakes:

1. Missing YAML frontmatter
   Fix: Add proper `---` block at top.

2. Folder name does not match YAML `name`
   Fix: Align both to same kebab-case value.

3. Workflow too abstract
   Fix: Add concrete paths and commands.

4. Including application code inside SKILL.md
   Fix: Remove runtime code; describe behavior only.
