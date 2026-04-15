---
name: android-device-screenshot
description: Capture a live screenshot from the connected Android device or emulator using ADB. Use this skill whenever the user reports a visual bug, blank screen, or UI glitch, or wants you to see what is currently on the screen. Runs the capture script, pulls the image locally, and opens it so you can inspect the actual device state before diagnosing or fixing anything. Reports element sizes in px, dp, and sp so UI dimension bugs can be diagnosed precisely.
argument-hint: "[label]   e.g. 'spot_detail_crash' or 'login_blank_screen'"
user-invocable: true
---

# Android Screen Inspector

## Purpose

**See what is currently on the connected Android device screen — and measure it.**

The ultimate goal is for the agent to understand the real UI state: what text is visible, which screen is open, what the user actually sees, and **the exact pixel/dp/sp dimensions of every UI element**.

The screenshot + accessibility tree + dimension analysis give a complete picture:
- **What** is on screen (text, elements, zones)
- **How it looks** (colors, theme)
- **How big it is** (px, dp, sp — ready to compare against Compose code)

Use this skill as the **first step** in any visual debugging session. Never diagnose UI issues blind.

---

## When to use

- User reports a UI bug, layout issue, wrong spacing, or wrong size
- You need to measure actual dp/sp values on device vs. code expectations
- You need to verify a fix actually worked on a real device
- Capturing before/after state of a UI change
- User says: "תצלם מסך", "תראה מה יש לי", "screenshot", "look at the screen", "מה הגדלים"
- Any time you need ground truth about what the device is currently showing

---

## When NOT to use

- No Android device is connected and no emulator is running
- The user wants a static Compose `@Preview` (use Android Studio instead)
- The user is asking about a historical bug that is no longer reproducible

---

## How it works (pipeline)

```
ADB screencap  →  ADB uiautomator dump  →  ADB wm density + font_scale  →  OCR + zone analysis  →  structured report with px/dp/sp
```

The master script runs all steps automatically.

---

## Primary command (use this)

```bash
bash .github/skills/android-device-screenshot/scripts/inspect_screen.sh [label]
```

| Argument | Required | Default  | Description                        |
|----------|----------|----------|------------------------------------|
| `label`  | No       | `screen` | Short tag appended to the filename |

**Examples:**
```bash
# Default
bash .github/skills/android-device-screenshot/scripts/inspect_screen.sh

# With context label
bash .github/skills/android-device-screenshot/scripts/inspect_screen.sh login_bug
bash .github/skills/android-device-screenshot/scripts/inspect_screen.sh spot_detail_crash
```

---

## Output (what the agent gets)

```
────────────────────────────────────────────────────────────────
📱  ANDROID SCREEN ANALYSIS  —  COMBINED REPORT
────────────────────────────────────────────────────────────────
  Resolution  : 1080×2340 px  →  384×834 dp
  Density     : 450 dpi (xxhdpi)  |  font-scale: 1.0
  Scale ratio : 1 dp = 2.81 px   |   1 sp = 2.81 px
  Theme       : DARK  #1C1C1E (content bg)
  Method      : ✅ UIAUTOMATOR + VISUAL
  Package     : com.david.h.myspots
  Screen/App  : My Spots

┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
📐  DIMENSIONS  (px → dp  @  450 dpi / xxhdpi  |  font-scale 1.0)
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
  Screen      : 1080×2340 px  →  384.0×834.0 dp
  Scale ratio : 1 dp = 2.81 px   |   1 sp = 2.81 px

  ELEMENT SIZES  (🔘 = clickable  |  sp = estimated font size for text elements):

  [TOP_BAR]  #1C1C1E
    🔘 My Spots                      1080×  56px  →   384.0×  20.0dp  ≈20.0sp

  [CONTENT]  #1C1C1E
       Spots (3)                      360×  24px  →   128.0×   8.5dp  ≈8.5sp
    🔘 Summer Mushrooms               800×  96px  →   284.4×  34.1dp  ≈34.1sp

  [BOTTOM_ACTION_BAR]  #2C2C2E
    🔘 + New Find                    1080×  80px  →   384.0×  28.4dp  ≈28.4sp
```

### Why dp/sp matter for UI debugging

| Unit | What it means | Use case |
|------|---------------|----------|
| `px` | Raw screen pixels | Exact screenshot coordinates |
| `dp` | Device-independent pixels (160 dpi baseline) | What your Compose code specifies (`Modifier.size(48.dp)`) |
| `sp` | Scale-independent pixels | Font sizes (`fontSize = 16.sp`) — scales with user's font preference |

**Example:** if a button shows `56×56px` at 450 dpi → `56 * 160 / 450 = 19.9 dp` → your Compose code should have `size(20.dp)`.

---

## Advanced: JSON output for programmatic use

```bash
python3 .github/skills/android-device-screenshot/scripts/analyze_screen.py \
  ./tmp/screenshots/my_shot.png ui_dump.xml \
  --density 450 --font-scale 1.0 --json
```

JSON output includes `resolution_dp`, `dpi_class`, `font_scale`, and `zones_with_dims` (each element has `width_dp`, `height_dp`, `height_sp`).

---

## Manual steps (capture only, no analysis)

```bash
bash .github/skills/android-device-screenshot/scripts/capture_screenshot.sh [output_dir] [label]
```

---

## Prerequisites

| Requirement              | Install command                                    |
|--------------------------|----------------------------------------------------|
| `adb` in PATH            | `brew install --cask android-platform-tools`       |
| USB Debugging            | `Settings → Developer options → USB debugging`     |
| Python 3                 | pre-installed on macOS                             |
| `pillow` + `pytesseract` | auto-installed by `analyze_screen.py` on first run |
| `tesseract` OCR engine   | `brew install tesseract`                           |

**Verify device is connected:**
```bash
adb devices
# Expected: RFCX80XXXXX    device
```

---

## Files in this skill

```
.github/skills/android-device-screenshot/
├── SKILL.md                        ← this file
└── scripts/
    ├── inspect_screen.sh           ← PRIMARY: capture + density + analyze (use this)
    ├── analyze_screen.py           ← OCR + zone analysis + px/dp/sp engine
    └── capture_screenshot.sh       ← capture only (no analysis)
```

Screenshots are saved to `tmp/screenshots/` which is gitignored.

---

## Trigger phrases

- "תצלם מסך" / "צלם לי מסך"
- "תראה מה יש לי במסך"
- "screenshot the device"
- "look at what I see"
- "I see a bug, look at the screen"
- "מה יש על המסך"
- "take a screenshot of the phone"
- "תמדוד את הרכיב הזה"
- "מה הגודל ב-dp של..."
- "כמה sp הטקסט הזה"


# Android Screen Inspector


