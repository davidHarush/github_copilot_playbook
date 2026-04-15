#!/bin/bash
# =============================================================================
# inspect_screen.sh  — See what is on the connected Android device screen
#
# PIPELINE:
#   1. adb screencap     → PNG screenshot
#   2. adb uiautomator   → UI hierarchy XML  (real text, any language)
#   3. analyze_screen.py → structured report (uiautomator primary, OCR fallback)
#
# Usage:
#   bash inspect_screen.sh [label]
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="./tmp/screenshots"
LABEL="${1:-screen}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PNG_PATH="${OUTPUT_DIR}/${TIMESTAMP}_${LABEL}.png"
XML_PATH="${OUTPUT_DIR}/${TIMESTAMP}_${LABEL}_ui.xml"
DEVICE_PNG="/sdcard/screenshot_tmp.png"
DEVICE_XML="/sdcard/ui_dump_tmp.xml"

log()  { echo "▶ $*"; }
ok()   { echo "✅ $*"; }
fail() { echo "❌ $*" >&2; exit 1; }

# ── 1. ADB ──────────────────────────────────────────────────────────────────
if ! command -v adb &>/dev/null; then
  SDK_ADB="$HOME/Library/Android/sdk/platform-tools/adb"
  [[ -x "$SDK_ADB" ]] && export PATH="$(dirname "$SDK_ADB"):$PATH" \
    || fail "adb not found. Run: brew install --cask android-platform-tools"
fi

DEVICE_COUNT=$(adb devices | grep -c "device$" || true)
[[ "$DEVICE_COUNT" -gt 0 ]] || fail "No Android device connected. Enable USB Debugging and reconnect."

DEVICE=$(adb devices | grep "device$" | head -1 | awk '{print $1}')
log "Device  : $DEVICE"
mkdir -p "$OUTPUT_DIR"

# ── 2. Screenshot ────────────────────────────────────────────────────────────
log "Capturing screenshot..."
adb -s "$DEVICE" shell screencap -p "$DEVICE_PNG"
adb -s "$DEVICE" pull "$DEVICE_PNG" "$PNG_PATH" 2>&1 | grep -v "^$" || true
adb -s "$DEVICE" shell rm "$DEVICE_PNG" 2>/dev/null || true
[[ -f "$PNG_PATH" ]] || fail "Screenshot pull failed."
ok "Screenshot: $PNG_PATH ($(du -sh "$PNG_PATH" | awk '{print $1}'))"

# ── 3. UI Hierarchy dump (primary text extraction — works with Hebrew/RTL) ───
log "Dumping UI hierarchy..."
if adb -s "$DEVICE" shell uiautomator dump "$DEVICE_XML" 2>/dev/null | grep -q "dumped"; then
  adb -s "$DEVICE" pull "$DEVICE_XML" "$XML_PATH" 2>&1 | grep -v "^$" || true
  adb -s "$DEVICE" shell rm "$DEVICE_XML" 2>/dev/null || true
  ok "UI dump  : $XML_PATH"
else
  log "UI dump unavailable — will use OCR fallback."
  XML_PATH=""
fi

# ── 3.5. Device display info (density + font scale for dp/sp conversion) ────
log "Reading display metrics..."
DENSITY_RAW=$(adb -s "$DEVICE" shell wm density 2>/dev/null || echo "")
DENSITY=$(echo "$DENSITY_RAW" | grep -oE 'density: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "")
[[ -z "$DENSITY" ]] && DENSITY="420"
ok "Density  : ${DENSITY} dpi ($(python3 -c "
d=$DENSITY
c = 'ldpi' if d<145 else 'mdpi' if d<210 else 'hdpi' if d<280 else 'xhdpi' if d<400 else 'xxhdpi' if d<560 else 'xxxhdpi'
print(c)" 2>/dev/null || echo "xxhdpi"))  |  1 dp = $(python3 -c "print(round($DENSITY/160.0,2))" 2>/dev/null || echo "?") px"

FONT_SCALE=$(adb -s "$DEVICE" shell settings get system font_scale 2>/dev/null | tr -d '[:space:]')
[[ -z "$FONT_SCALE" || "$FONT_SCALE" == "null" ]] && FONT_SCALE="1.0"
ok "Font scale: ${FONT_SCALE}"

# ── 4. Analyze ───────────────────────────────────────────────────────────────
echo ""
log "Analyzing screen..."
if [[ -n "$XML_PATH" && -f "$XML_PATH" ]]; then
  python3 "$SCRIPT_DIR/analyze_screen.py" "$PNG_PATH" "$XML_PATH" \
    --density "$DENSITY" --font-scale "$FONT_SCALE"
else
  python3 "$SCRIPT_DIR/analyze_screen.py" "$PNG_PATH" \
    --density "$DENSITY" --font-scale "$FONT_SCALE"
fi
