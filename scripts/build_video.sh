#!/usr/bin/env bash
# monarch-video :: end-to-end build
#
#   ./build_video.sh <storyboard.json> <project-dir> [output.mp4]
#
# Runs: narration (Kokoro) -> re-time scenes -> compose brand-locked HTML -> render MP4.
# Works in the Claude sandbox and on a Mac. No API keys.

set -euo pipefail

SB="${1:?usage: build_video.sh <storyboard.json> <project-dir> [out.mp4]}"
PROJ="${2:?usage: build_video.sh <storyboard.json> <project-dir> [out.mp4]}"
OUT="${3:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { printf '\n\033[1m▸ %s\033[0m\n' "$*"; }

# ---- Chrome resolution -----------------------------------------------------
# hyperframes downloads its own Chrome by default, which is slow and fails on
# restricted networks. Prefer a browser that is already on the machine.
if [[ -z "${HYPERFRAMES_BROWSER_PATH:-}" ]]; then
  # chrome-headless-shell first: it enables the fast BeginFrame capture path.
  for c in \
    /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell \
    "$HOME/.cache/hyperframes/chrome/chrome-headless-shell" \
    /opt/pw-browsers/chromium-*/chrome-linux/chrome \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "$HOME/Library/Caches/ms-playwright/chromium-"*/chrome-mac/Chromium.app/Contents/MacOS/Chromium \
    /usr/bin/google-chrome /usr/bin/chromium /usr/bin/chromium-browser
  do
    if [[ -x "$c" ]]; then export HYPERFRAMES_BROWSER_PATH="$c"; break; fi
  done
fi
if [[ -n "${HYPERFRAMES_BROWSER_PATH:-}" ]]; then
  echo "Chrome: $HYPERFRAMES_BROWSER_PATH"
else
  echo "Chrome: none found locally — hyperframes will download one (first run only)"
fi

HF=(npx -y hyperframes@latest)
command -v hyperframes >/dev/null 2>&1 && HF=(hyperframes)

# ---- 1. Narration + re-time ------------------------------------------------
log "Generating narration (Kokoro-82M, local, no API key)"
python3 "$HERE/voiceover.py" "$SB" --project-dir "$PROJ"

# ---- 2. Compose ------------------------------------------------------------
log "Composing brand-locked stage"
python3 "$HERE/compose.py" "$PROJ/storyboard.fitted.json" --project-dir "$PROJ"

# ---- 3. Render -------------------------------------------------------------
SLUG="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('slug','monarch-video'))" "$SB")"
OUT="${OUT:-$PROJ/$SLUG.mp4}"

# Render tuning. hyperframes auto-enables low-memory mode at <=8 GB RAM, which
# pins to 1 worker and forces the slow screenshot capture path. On a 2-core
# sandbox that turns a 60s video into a 15-minute render. Opt out explicitly
# and cap workers to the core count.
FPS="${VIDEO_FPS:-24}"
WORKERS="${VIDEO_WORKERS:-$(python3 -c 'import os;print(max(1,min(4,(os.cpu_count() or 2))))')}"

log "Rendering MP4 (${FPS}fps, ${WORKERS} workers)"
mkdir -p "$(dirname "$OUT")"
ABS_OUT="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
( cd "$PROJ" && "${HF[@]}" render -o "$ABS_OUT" \
    --fps "$FPS" --workers "$WORKERS" --no-low-memory-mode \
    2>&1 | grep -vE '^\s*[█░]+\s+[0-9]+%|Render:trace' | tail -20 )

log "Done"
ls -lh "$OUT"
ffprobe -v error -show_entries format=duration -show_entries stream=codec_name,width,height \
  -of default=nw=1 "$OUT" 2>/dev/null || true
