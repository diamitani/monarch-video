#!/usr/bin/env python3
"""monarch-video :: framecheck

Verify rendered frames without eyes: extract frames from an MP4 and report
luminance stats that prove each scene surface is what you designed.

    python3 framecheck.py video.mp4 2,11,20,30,34.5

Expectations for the stock themes (16:9):
  dark / gradient scenes   mean_lum ~15-80, high dark_px, some bright text px
  light scene              mean_lum > 180
  end card (brand)         mean_lum ~90-160 (brand-color gradient + white text)
A flat black frame (mean_lum < 5, 0% bright px) means the scene failed to render.
"""
from __future__ import annotations

import subprocess
import sys


def stats(mp4: str, t: float) -> tuple[float, float, float]:
    p = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", mp4,
         "-frames:v", "1", "-vf", "scale=320:-1,format=gray", "-f", "rawvideo", "-"],
        capture_output=True,
    )
    px = list(p.stdout)
    n = len(px) or 1
    lum = sum(px) / n
    hi = sum(1 for x in px if x > 200) / n * 100
    lo = sum(1 for x in px if x < 30) / n * 100
    return lum, hi, lo


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: framecheck.py video.mp4 t1,t2,t3,...")
        return 2
    mp4, times = sys.argv[1], sys.argv[2]
    for t in times.split(","):
        lum, hi, lo = stats(mp4, float(t))
        print(f"t={float(t):6.1f}s  mean_lum={lum:5.0f}/255  bright_px={hi:4.0f}%  dark_px={lo:4.0f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
