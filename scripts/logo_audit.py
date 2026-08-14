#!/usr/bin/env python3
"""monarch-video :: logo_audit

Inspect candidate logo images for the brand kit without eyes. Uses ffmpeg to
decode, then reports what matters for video scenes:

    python3 logo_audit.py logo1.png logo2.png ...

Reads:
  alpha_min/alpha_max  — transparent background? (alpha_min < 200 = some fully
                         transparent pixels, good for compositing)
  avg_rgb of opaque px — is the mark light (white/cream), brand gold, or dark?
  corners_light        — true = the image is a solid light box, bad on dark scenes
  std_r/g/b            — LOW = single-color logo (safe to recolor to brand color);
                         HIGH = gradient/multicolor logo, use as-is and design
                         scenes so it always sits on dark/light surfaces, never
                         on a same-tone brand-color gradient.
"""
from __future__ import annotations

import os
import statistics
import subprocess
import sys


def audit(path: str) -> str:
    p = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", path,
         "-vf", "format=rgba", "-f", "rawvideo", "-"],
        capture_output=True,
    )
    raw = p.stdout
    if not raw:
        return f"{path}: ffmpeg decode failed"
    px = [tuple(raw[i:i + 4]) for i in range(0, len(raw), 4)]
    opaque = [x for x in px if x[3] > 200]
    n = len(opaque) or 1
    rs = [x[0] for x in opaque]
    gs = [x[1] for x in opaque]
    bs = [x[2] for x in opaque]
    corners = [px[0], px[1], px[-2], px[-1]]
    alphas = [x[3] for x in px]
    return (
        f"{path}: {len(px)}px alpha_min={min(alphas)} alpha_max={max(alphas)} "
        f"opaque={n} avg_rgb=({sum(rs)/n:.0f},{sum(gs)/n:.0f},{sum(bs)/n:.0f}) "
        f"corners_light={all(sum(c[:3])/3 > 200 for c in corners)} "
        f"std_r={statistics.pstdev(rs):.0f} std_g={statistics.pstdev(gs):.0f} "
        f"std_b={statistics.pstdev(bs):.0f}"
    )


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: logo_audit.py image1.png [image2.svg ...]")
        return 2
    for f in sys.argv[1:]:
        print(audit(f) if os.path.exists(f) else f"{f}: MISSING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
