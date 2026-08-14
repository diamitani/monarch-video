#!/usr/bin/env python3
"""
monarch-video :: compose

Turns a storyboard.json into a brand-locked Hyperframes composition
(index.html) plus a narration manifest the voiceover step consumes.

Usage:
    python3 compose.py storyboard.json --project-dir outputs/videos/<slug>

Writes:
    <project-dir>/index.html          the composition
    <project-dir>/narration.json      [{id, text, file}] for the TTS step
    <project-dir>/brand/              copied brand kit + generated tokens.css

The brand kit is injected last: no field in the storyboard can introduce a
color, font, or logo that is not in brand/brand.json. tokens.css (generated
from brand.json) defines every --brand-* variable and @font-face in use.
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent

RESOLUTIONS = {
    "16:9": (1920, 1080, "landscape"),
    "9:16": (1080, 1920, "portrait"),
    "1:1": (1080, 1080, "square"),
}

# Words per second ceiling. Over-writing narration is the #1 failure mode.
MAX_WPS = 2.5

# Decorative circle motif — drawn from brand tokens only.
CIRCLES = [
    ("--brand-primary", 620, -160, -180),
    ("--brand-secondary", 460, 1500, 720),
    ("--brand-accent", 300, 1180, -110),
]

FONT_FORMATS = {".otf": "opentype", ".ttf": "truetype", ".woff2": "woff2"}
IMAGE_EXT = {".svg", ".png", ".jpg", ".jpeg", ".webp"}

# Neutral demo palette — used until the user loads a real brand into brand.json.
DEFAULT_COLORS = {
    "primary": "#2563eb",
    "primary_light": "#93c5fd",
    "primary_dark": "#1e3a8a",
    "secondary": "#7c3aed",
    "secondary_light": "#c4b5fd",
    "secondary_dark": "#4c1d95",
    "accent": "#db2777",
    "accent_light": "#f9a8d4",
    "accent_dark": "#831843",
    "ink": "#0b1220",
    "paper": "#f8fafc",
    "white": "#ffffff",
}

# brand.json color slot -> generated CSS variable suffix.
SLOT_TO_TOKEN = {
    "primary": "primary",
    "primary_light": "primary-light",
    "primary_dark": "primary-dark",
    "secondary": "secondary",
    "secondary_light": "secondary-light",
    "secondary_dark": "secondary-dark",
    "accent": "accent",
    "accent_light": "accent-light",
    "accent_dark": "accent-dark",
    "ink": "ink",
    "paper": "paper",
    "white": "white",
}


def esc(v) -> str:
    return html.escape(str(v), quote=True)


def load_brand() -> dict:
    path = SKILL_DIR / "brand" / "brand.json"
    if not path.exists():
        return {"name": "Your Brand", "logo": "auto", "logo_end": "auto"}
    return json.loads(path.read_text(encoding="utf-8"))


def tokens_css(brand: dict) -> str:
    """@font-face rules + :root variables derived from brand/brand.json."""
    family = esc(brand.get("font_family") or "Brand Font")
    family_display = esc(
        brand.get("font_family_display") or brand.get("font_family") or "Brand Font"
    )
    fonts_dir = SKILL_DIR / "brand" / "fonts"
    fonts = brand.get("fonts") or []
    if not fonts:
        fonts = [
            {"file": p.name, "weight": 400}
            for p in sorted(fonts_dir.iterdir())
            if p.suffix.lower() in FONT_FORMATS
        ]
    faces = []
    for f in fonts:
        fmt = FONT_FORMATS.get(Path(str(f["file"])).suffix.lower(), "opentype")
        fam = family_display if str(f.get("use", "body")) == "display" else family
        faces.append(
            f'@font-face {{ font-family: "{fam}"; '
            f'src: url("fonts/{esc(f["file"])}") format("{fmt}"); '
            f'font-weight: {f.get("weight", 400)}; font-display: block; }}'
        )
    colors = brand.get("colors") or {}
    vars_ = [
        f"  --brand-{css}: {colors.get(slot, DEFAULT_COLORS.get(slot, '#000000'))};"
        for slot, css in SLOT_TO_TOKEN.items()
    ]
    vars_.append(f'  --brand-font: "{family}", -apple-system, "Segoe UI", sans-serif;')
    vars_.append(
        f'  --brand-font-display: "{family_display}", Georgia, "Times New Roman", serif;'
    )
    return "\n".join(faces) + "\n\n:root {\n" + "\n".join(vars_) + "\n}\n"


def resolve_logo(brand: dict, slot: str) -> str | None:
    """Return a logo filename from brand/logos/, or None (→ text logo).

    brand.json values: a filename, "auto" (first image in logos/), or
    "none" (force the text logo for this slot).
    """
    logos_dir = SKILL_DIR / "brand" / "logos"
    explicit = brand.get(slot) or "auto"
    if explicit == "none":
        return None
    if explicit != "auto" and (logos_dir / explicit).is_file():
        return explicit
    for p in sorted(logos_dir.iterdir()):
        if p.is_file() and p.suffix.lower() in IMAGE_EXT:
            return p.name
    return None


def logo_markup(brand: dict, slot: str = "logo") -> str:
    """Corner logo, or a text logo built from the brand name when no image exists."""
    name = esc(brand.get("name") or "Brand")
    img = resolve_logo(brand, slot)
    if img:
        alt = esc(brand.get("logo_alt") or name)
        return f'<div class="logo"><img src="brand/logos/{esc(img)}" alt="{alt}" /></div>'
    return f'<div class="logo logo--text">{name}</div>'


def circles_markup() -> str:
    spans = "".join(
        f'<span style="width:{s}px;height:{s}px;left:{x}px;top:{y}px;'
        f"background:var({c});opacity:.30\"></span>"
        for c, s, x, y in CIRCLES
    )
    return f'<div class="circles">{spans}</div>'


def scene_body(sc: dict, brand: dict) -> str:
    layout = sc.get("layout", "statement")
    parts = []

    if layout == "end":
        cta = esc(sc.get("cta", sc.get("headline", "")))
        return (
            '<div class="end-card">'
            f'{logo_markup(brand, "logo_end")}'
            f'<p class="cta">{cta}</p>'
            "</div>"
        )

    if sc.get("eyebrow"):
        parts.append(f'<p class="eyebrow">{esc(sc["eyebrow"])}</p>')

    if sc.get("headline"):
        klass = "headline" + (" headline--sm" if layout == "stats" else "")
        # <em> is the one inline tag allowed — it maps to the brand accent color.
        head = esc(sc["headline"]).replace("&lt;em&gt;", '<em class="accent">').replace(
            "&lt;/em&gt;", "</em>"
        )
        parts.append(f'<h1 class="{klass}">{head}</h1>')

    if sc.get("subhead"):
        parts.append(f'<p class="subhead">{esc(sc["subhead"])}</p>')

    if layout == "stats" and sc.get("stats"):
        cells = "".join(
            f'<div><div class="stat-value">{esc(s.get("value", ""))}</div>'
            f'<div class="stat-label">{esc(s.get("label", ""))}</div></div>'
            for s in sc["stats"]
        )
        parts.append(f'<div class="stats">{cells}</div>')

    if layout == "points" and sc.get("points"):
        items = "".join(f'<div class="point">{esc(p)}</div>' for p in sc["points"])
        parts.append(f'<div class="points">{items}</div>')

    return "\n        ".join(parts)


def build(storyboard: dict, project_dir: Path) -> dict:
    brand = load_brand()
    aspect = storyboard.get("aspect_ratio", "16:9")
    if aspect not in RESOLUTIONS:
        raise SystemExit(f"aspect_ratio must be one of {list(RESOLUTIONS)}, got {aspect!r}")
    width, height, res_name = RESOLUTIONS[aspect]

    scenes = storyboard.get("scenes") or []
    if not scenes:
        raise SystemExit("storyboard has no scenes")

    project_dir.mkdir(parents=True, exist_ok=True)

    # --- brand lock: copy, never link outside the project -------------------
    brand_dst = project_dir / "brand"
    if brand_dst.exists():
        shutil.rmtree(brand_dst)
    shutil.copytree(SKILL_DIR / "brand", brand_dst)
    # Generated token sheet: @font-face + :root variables from brand.json.
    (brand_dst / "tokens.css").write_text(tokens_css(brand), encoding="utf-8")

    blocks, narration, warnings = [], [], []
    t = 0.0

    for i, sc in enumerate(scenes):
        sid = sc.get("id") or f"scene_{i+1:02d}"
        dur = float(sc.get("duration", 5))
        theme = sc.get("theme", "gradient")
        if sc.get("layout") == "end":
            theme = "brand"
        text = (sc.get("narration") or "").strip()

        if text:
            # The wps ceiling is an *authoring* guardrail. Once voiceover.py has
            # snapped durations to real audio, the scene is correct by
            # construction and this check would only ever fire falsely.
            if not storyboard.get("_fitted"):
                words = len(text.split())
                if words > dur * MAX_WPS:
                    warnings.append(
                        f"{sid}: {words} words in {dur:.0f}s "
                        f"({words/dur:.1f} wps) exceeds the {MAX_WPS} wps ceiling — shorten the narration"
                    )
            narration.append({"id": sid, "text": text, "file": f"audio/{sid}.wav"})

        show_logo = sc.get("layout") != "end"
        logo = logo_markup(brand) if show_logo else ""
        image = (sc.get("image") or "").strip()
        if image:
            media = f'<div class="scene-image"><img src="brand/images/{esc(image)}" alt="" /></div>'
        else:
            media = circles_markup() if theme in ("gradient", "dark") else ""
        scene_cls = "scene--image" if image else ""
        caption = (
            f'<div class="caption">{esc(text)}</div>'
            if text and storyboard.get("captions", True)
            else ""
        )

        blocks.append(
            f'''      <div id="{sid}" class="clip scene scene--{theme}{scene_cls}"
           data-start="{t:g}" data-duration="{dur:g}" data-track-index="{i}">
        {media}
        {logo}
        {scene_body(sc, brand)}
        {caption}
      </div>'''
        )

        if text:
            blocks.append(
                f'      <audio data-start="{t:g}" data-duration="{dur:g}" '
                f'data-track-index="{50+i}" data-volume="1" src="audio/{sid}.wav"></audio>'
            )
        t += dur

    total = t

    # Gentle, brand-appropriate reveals. No bounce, no spin.
    #
    # fromTo() rather than from(): the renderer captures frames by seeking the
    # timeline, and parallel workers each seek into a different segment. from()
    # infers its end state from whatever the DOM happens to hold at that moment,
    # so a worker starting mid-timeline can bake in a stale transform and leave
    # a ghosted duplicate of the text. fromTo() pins both ends, so any seek from
    # any worker lands on the same pixels.
    tl_lines = []
    for i, sc in enumerate(scenes):
        sid = sc.get("id") or f"scene_{i+1:02d}"
        start = sum(float(s.get("duration", 5)) for s in scenes[:i])
        dur = float(sc.get("duration", 5))
        tl_lines.append(
            f'      tl.fromTo("#{sid} .headline, #{sid} .eyebrow, '
            f'#{sid} .subhead, #{sid} .stats > div, #{sid} .point, '
            f'#{sid} .cta", '
            f'{{ opacity: 0, y: 34 }}, '
            f'{{ opacity: 1, y: 0, duration: 0.62, stagger: 0.12, ease: "power2.out", '
            f'immediateRender: false, overwrite: "auto" }}, {start:g});'
        )
        # Slow Ken Burns zoom-out on photo backgrounds — keeps image scenes alive
        # without motion that would fight the text reveals.
        if sc.get("image"):
            tl_lines.append(
                f'      tl.fromTo("#{sid} .scene-image img", '
                f'{{ scale: 1.12 }}, '
                f'{{ scale: 1, duration: {dur:g}, ease: "power1.out", immediateRender: false }}, {start:g});'
            )

    title = storyboard.get("title") or brand.get("name") or "Monarch video"

    doc = f'''<!doctype html>
<html lang="en" data-resolution="{res_name}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={width}, height={height}" />
    <title>{esc(title)}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <link rel="stylesheet" href="brand/brand.css" />
    <link rel="stylesheet" href="brand/tokens.css" />
    <style>
      html, body {{ width: {width}px; height: {height}px; }}
    </style>
  </head>
  <body>
    <div id="root"
         data-composition-id="main"
         data-start="0"
         data-duration="{total:g}"
         data-width="{width}"
         data-height="{height}">
{chr(10).join(blocks)}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl_lines)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''

    (project_dir / "index.html").write_text(doc, encoding="utf-8")
    (project_dir / "narration.json").write_text(
        json.dumps(narration, indent=2), encoding="utf-8"
    )
    (project_dir / "hyperframes.json").write_text(
        json.dumps(
            {
                "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                "media": {"autoProxy": True},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (project_dir / "meta.json").write_text(
        json.dumps({"id": storyboard.get("slug", "monarch-video"), "name": title}, indent=2),
        encoding="utf-8",
    )

    return {
        "duration": total,
        "scenes": len(scenes),
        "narration_segments": len(narration),
        "resolution": f"{width}x{height}",
        "warnings": warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Compose a brand-locked Hyperframes stage.")
    ap.add_argument("storyboard", type=Path)
    ap.add_argument("--project-dir", type=Path, required=True)
    args = ap.parse_args()

    sb = json.loads(args.storyboard.read_text(encoding="utf-8"))
    info = build(sb, args.project_dir)

    print(json.dumps(info, indent=2))
    for w in info["warnings"]:
        print(f"  ! {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
