---

name: skill-creator
description: Create high-quality GitHub Copilot agent skills for software projects. Generates structured SKILL.md files with clear scope, inputs, outputs, constraints, and reusable workflows. Use when creating new skills or improving existing ones.
argument-hint: "[skill-name] [purpose]"
user-invocable: true
--------------------

# Skill Creator

## Purpose

Create strong, reusable GitHub Copilot skills that are focused, discoverable, and practical across different kinds of software projects.

This skill should help transform repeated workflows into maintainable skills instead of one-off prompts.

---

## When to use

Use this skill when:

* You want to create a new Copilot skill
* You want to improve or refactor an existing `SKILL.md`
* You have a repeated workflow and want to turn it into a reusable skill
* You want a skill that can be shared across repositories or teammates

---

## When NOT to use

Do not use this skill when:

* The user only needs a one-time prompt
* The workflow is still vague and not yet repeatable
* The task is too broad to fit into one skill
* The request is better handled as repository instructions, prompt files, or agent configuration

---

## Required input

Collect or infer the following:

1. Skill name
2. Primary purpose
3. What problem it solves
4. Example trigger phrases a user might actually say
5. Expected inputs
6. Expected outputs
7. Constraints or rules the skill should follow
8. Whether the skill should be user-invocable

If important details are missing, ask concise follow-up questions before generating the final skill.

---

## Output format

Always produce:

1. Recommended folder path
2. Full `SKILL.md`
3. Short explanation of design choices
4. Example usage prompts

When useful, also produce:

* Suggested supporting files
* Optional companion scripts
* Notes about scope boundaries

---

## Core design principles

### 1. One job per skill

Each skill should do one clear job well.
Avoid combining unrelated workflows into one skill.

### 2. Optimize for discovery

The `description` must be specific enough for Copilot to match the skill to the right intent.
Avoid vague descriptions like "helps with development" or "improves code quality".

### 3. Define boundaries clearly

Every skill should state:

* When to use it
* When not to use it
* What inputs it expects
* What outputs it should produce

### 4. Prefer workflows over slogans

A good skill should contain a concrete repeatable process, not just advice.
Use step-by-step procedures.

### 5. Be conservative

Do not instruct the model to:

* Make broad assumptions without evidence
* Introduce dependencies without being asked
* Perform destructive actions without explicit approval
* Claim success without verification

### 6. Make it portable

Write the skill so it can work across projects unless the user explicitly wants repository-specific behavior.

---

## Skill generation rules

### Structure rules

Generate a `SKILL.md` with:

* YAML frontmatter
* A clear title
* Usage guidance
* Inputs
* Procedure
* Output expectations
* Examples
* Constraints

### Style rules

* Be direct and specific
* Prefer short sections over long prose
* Use realistic trigger phrases
* Avoid marketing language
* Avoid filler text

### Quality rules

The generated skill must:

* Be narrow enough to be reliable
* Be broad enough to be reusable
* Contain concrete operational steps
* Avoid ambiguous wording
* Avoid redundant sections

---

## Standard template

Generate skills using this pattern:

```md
---
name: <skill-name>
description: <specific description of what the skill does, when it should be used, and what outcome it produces>
argument-hint: "<optional arguments>"
user-invocable: true
---

# <Skill Title>

## Purpose
Brief explanation of the skill's job.

## When to use
- ...
- ...

## When NOT to use
- ...
- ...

## Inputs
- ...
- ...

## Procedure
1. ...
2. ...
3. ...

## Output
- ...
- ...

## Constraints
- ...
- ...

## Examples
- "..."
- "..."
```

---

## Internal creation procedure

When generating a skill, follow this workflow:

1. Identify the repeated workflow
   Determine whether the request is truly a reusable workflow and not just a one-off prompt.

2. Define the job of the skill
   Reduce the scope until the skill has one clear responsibility.

3. Extract realistic trigger phrases
   Write examples based on how a real user would ask for the capability.

4. Define inputs and outputs
   Be explicit about what the skill consumes and what it returns.

5. Add constraints
   Prevent overreach, hallucination, and destructive behavior.

6. Write the first draft
   Generate a complete `SKILL.md`.

7. Tighten for discovery
   Improve `name` and `description` so Copilot can match the skill more reliably.

8. Remove fluff
   Cut generic advice that does not change behavior.

9. Validate portability
   Check whether the skill is too repository-specific. If so, either generalize it or clearly label the repo-specific assumptions.

---

## Evaluation checklist

Before returning a generated skill, verify:

* Does it solve one clear repeated problem?
* Is the description specific enough for discovery?
* Are the inputs and outputs obvious?
* Are scope boundaries clear?
* Does it include a concrete procedure?
* Does it avoid dangerous or unverifiable instructions?
* Can another developer reuse it with minimal edits?

If any answer is no, revise the draft before returning it.

---

## Heuristics for deciding between skill types

Use these guidelines:

* If the behavior should always apply in a repository, prefer instructions.
* If the behavior is a reusable multi-step workflow, prefer a skill.
* If the behavior is just a reusable shortcut phrase, consider a prompt file.
* If the behavior depends on role/persona selection, consider a custom agent.

---

## Common mistakes to avoid

* Skills that are too broad
* Descriptions that are too generic
* Missing examples
* Missing output expectations
* Advice without procedure
* Repository-specific assumptions hidden as general rules
* Telling the model to do things it cannot verify

---

## Response behavior

When asked to create a skill, respond in this order:

1. Briefly summarize the intended skill
2. State any assumptions
3. Provide the folder path
4. Provide the complete `SKILL.md`
5. Provide 2 to 5 example prompts
6. Mention optional supporting files if relevant

---

## Example request

"Create a skill that drafts release notes from git history"

## Example request

"Create a skill that reviews pull requests against a team checklist"

## Example request

"Create a skill that turns bug reports into reproducible investigation plans"
