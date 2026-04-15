#!/bin/bash
# =============================================================================
# capture_screenshot.sh
# Takes a screenshot from the connected Android device via ADB,
# pulls it to the local machine, and opens it for inspection.
#
# Usage:
#   ./capture_screenshot.sh [output_dir] [label]
#
#   output_dir  — local folder to save screenshots (default: ./tmp/screenshots)
#   label       — optional filename suffix for context (default: screen)
#
# Examples:
#   ./capture_screenshot.sh
#   ./capture_screenshot.sh ./tmp/screenshots login_bug
#   ./capture_screenshot.sh /tmp spot_detail_crash
# =============================================================================

set -euo pipefail

# ---------- CONFIG -----------------------------------------------------------
OUTPUT_DIR="${1:-./tmp/screenshots}"
LABEL="${2:-screen}"
DEVICE_TMP="/sdcard/screenshot_tmp.png"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="${TIMESTAMP}_${LABEL}.png"
LOCAL_PATH="${OUTPUT_DIR}/${FILENAME}"
# ----------------------------------------------------------------------------

# ---------- HELPERS ----------------------------------------------------------
log()  { echo "▶ $*"; }
ok()   { echo "✅ $*"; }
fail() { echo "❌ $*" >&2; exit 1; }
# ----------------------------------------------------------------------------

# 1. Check ADB is available
if ! command -v adb &>/dev/null; then
  fail "adb not found. Install Android SDK Platform-Tools and ensure it is in PATH.
  Homebrew: brew install --cask android-platform-tools
  Or add Android SDK to PATH: export PATH=\$PATH:\$ANDROID_HOME/platform-tools"
fi

# 2. Check a device is connected
DEVICES=$(adb devices | grep -v "List of devices" | grep -v "^$" | grep "device$" || true)
DEVICE_COUNT=$(echo "$DEVICES" | grep -c "device$" || true)

if [[ "$DEVICE_COUNT" -eq 0 ]]; then
  fail "No Android device connected.
  - Connect your phone via USB and enable USB Debugging.
  - Or start an emulator from Android Studio."
elif [[ "$DEVICE_COUNT" -gt 1 ]]; then
  log "Multiple devices found:"
  adb devices
  log "Using first device. To target a specific device run: adb -s <serial> ..."
fi

DEVICE_SERIAL=$(adb devices | grep "device$" | head -1 | awk '{print $1}')
log "Device: $DEVICE_SERIAL"

# 3. Create local output directory
mkdir -p "$OUTPUT_DIR"

# 4. Take the screenshot on device
log "Taking screenshot on device..."
adb -s "$DEVICE_SERIAL" shell screencap -p "$DEVICE_TMP"

# 5. Pull to local machine
log "Pulling screenshot to: $LOCAL_PATH"
adb -s "$DEVICE_SERIAL" pull "$DEVICE_TMP" "$LOCAL_PATH"

# 6. Clean up temp file on device
adb -s "$DEVICE_SERIAL" shell rm "$DEVICE_TMP" 2>/dev/null || true

# 7. Verify the file exists locally
if [[ ! -f "$LOCAL_PATH" ]]; then
  fail "Pull succeeded but file not found at $LOCAL_PATH"
fi

FILE_SIZE=$(du -sh "$LOCAL_PATH" | awk '{print $1}')
ok "Screenshot saved: $LOCAL_PATH ($FILE_SIZE)"

# 8. Open the image (macOS: open, Linux: xdg-open)
if [[ "$(uname)" == "Darwin" ]]; then
  open "$LOCAL_PATH"
elif command -v xdg-open &>/dev/null; then
  xdg-open "$LOCAL_PATH"
fi

# 9. Print absolute path for easy copy-paste or agent reference
echo ""
echo "SCREENSHOT_PATH=$(realpath "$LOCAL_PATH")"

