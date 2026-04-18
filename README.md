# 🧠 Copilot Skills Playground

This repository contains custom GitHub Copilot assets for defining and testing reusable workflows using **Skills** and **prompts**.

## 📦 Contents

### 🔹 `skill-author`
- deprecated
- A reusable Skill that defines how to create and maintain other `SKILL.md` files.
---

### 🔹 `skill-creator`

- This is improved ver of skill-author
- Create high-quality GitHub Copilot agent skills for software projects. Generates structured SKILL.md files with clear scope, inputs, outputs, constraints, and reusable workflows. Use when creating new skills or improving existing ones.

---
### 🔹 `skill-android-device-screenshot`

- Capture a live screenshot from the connected Android device or emulator using ADB. Use this skill whenever the user reports a visual bug, blank screen, or UI glitch, or wants you to see what is currently on the screen. Runs the capture script, pulls the image locally, and opens it so you can inspect the actual device state before diagnosing or fixing anything. Reports element sizes in px, dp, and sp so UI dimension bugs can be diagnosed precisely.

---

### 🔹 `generate-package-instructions.prompt.md`

- A prompt file designed to Generate strict Copilot instructions for a specific Android/Kotlin package

---


