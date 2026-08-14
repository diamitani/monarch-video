#!/usr/bin/env python3
"""
monarch-video :: voiceover

Generates neural narration with the Hyperframes-bundled Kokoro-82M model,
then re-times the storyboard so every scene is exactly as long as its
audio. This is what keeps narration and picture in sync — without it,
scenes cut off mid-sentence.

Usage:
    python3 voiceover.py storyboard.json --project-dir outputs/videos/<slug>

Writes:
    <project-dir>/audio/<scene_id>.wav
    <project-dir>/storyboard.fitted.json    durations snapped to real audio

Requires: npx hyperframes (auto-fetched), and `pip install kokoro-onnx soundfile`
on first run. No API key. No network calls to a TTS vendor.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path

# Named voice profiles -> Kokoro voice id. Any other value in the storyboard's
# `voice` field is passed straight through as a raw Kokoro id (e.g. "af_bella").
VOICES = {
    "warm": "af_heart",       # default: customer-facing, prospect, LinkedIn
    "pro": "af_nova",         # crisp, neutral: product + explainer
    "bright": "af_sky",       # upbeat: social, event promo
    "direct": "am_michael",   # executive comms, internal announcements
    "narrator": "am_adam",    # thought leadership, spotlights
    "uk-f": "bf_emma",        # UK audiences
    "uk-m": "bm_george",      # UK audiences
}
DEFAULT_VOICE = "warm"
KOKORO_ID = re.compile(r"[a-z]{2}_[a-z0-9]+")

# Breathing room after each narration line so scenes don't cut on the last syllable.
TAIL_PAD_S = 0.55
MIN_SCENE_S = 2.0


def hyperframes_cmd() -> list[str]:
    if shutil.which("hyperframes"):
        return ["hyperframes"]
    return ["npx", "-y", "hyperframes@latest"]


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def synth(text: str, voice_id: str, out: Path, speed: float) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = hyperframes_cmd() + [
        "tts", text, "-v", voice_id, "-s", str(speed), "-o", str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not out.exists():
        sys.stderr.write(proc.stdout + proc.stderr)
        raise SystemExit(
            f"TTS failed for {out.name}.\n"
            "If this is the first run, install the local model:\n"
            "    pip install kokoro-onnx soundfile\n"
            "Then re-run. (No API key is needed.)"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate Kokoro narration and re-time scenes.")
    ap.add_argument("storyboard", type=Path)
    ap.add_argument("--project-dir", type=Path, required=True)
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--no-fit", action="store_true",
                    help="keep the storyboard's declared durations instead of snapping to audio")
    args = ap.parse_args()

    sb = json.loads(args.storyboard.read_text(encoding="utf-8"))
    profile = sb.get("voice", DEFAULT_VOICE)
    voice_id = VOICES.get(profile, profile)
    if not KOKORO_ID.fullmatch(voice_id):
        raise SystemExit(
            f"unknown voice {profile!r}; choose from {list(VOICES)} "
            "or pass any Kokoro voice id (e.g. 'af_bella')"
        )

    audio_dir = args.project_dir / "audio"
    scenes = sb.get("scenes") or []
    print(f"Voice: {profile} ({voice_id}) · {len(scenes)} scenes", file=sys.stderr)

    for i, sc in enumerate(scenes):
        sid = sc.get("id") or f"scene_{i+1:02d}"
        sc["id"] = sid
        text = (sc.get("narration") or "").strip()
        if not text:
            continue

        wav = audio_dir / f"{sid}.wav"
        synth(text, voice_id, wav, args.speed)
        spoken = wav_duration(wav)

        if not args.no_fit:
            fitted = max(round(spoken + TAIL_PAD_S, 2), MIN_SCENE_S)
            declared = float(sc.get("duration", fitted))
            sc["duration"] = fitted
            flag = "" if abs(fitted - declared) < 0.35 else f"  (was {declared:g}s)"
            print(f"  {sid}: {spoken:.2f}s spoken → {fitted:.2f}s scene{flag}", file=sys.stderr)
        else:
            print(f"  {sid}: {spoken:.2f}s spoken", file=sys.stderr)

    total = sum(float(s.get("duration", 5)) for s in scenes)
    sb["duration_seconds"] = round(total, 2)
    # Tells compose.py that durations are audio-derived, so it should not
    # re-apply the words-per-second authoring guardrail.
    sb["_fitted"] = not args.no_fit

    out = args.project_dir / "storyboard.fitted.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sb, indent=2), encoding="utf-8")

    print(f"\nTotal: {total:.1f}s → {out}", file=sys.stderr)
    print(json.dumps({"storyboard": str(out), "duration": round(total, 2),
                      "voice": profile, "voice_id": voice_id}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
