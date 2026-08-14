<div align="center">

# 🦋 Monarch Video

### The AI skill that turns any document or prompt into a brand-locked, narrated MP4

**Intake → Storyboard → Neural Voiceover → Compose → Render**

[![MIT License](https://img.shields.io/badge/License-MIT-c9a227.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776ab.svg)](https://python.org)
[![Node 22+](https://img.shields.io/badge/Node-22+-339933.svg)](https://nodejs.org)
[![AI Agent Ready](https://img.shields.io/badge/AI%20Agent-Ready-00d4aa.svg)](#installation)

<br />

**Stop shipping off-brand slideshows.** Drop in a logo, a palette, and a sentence —
get back a 1080p MP4 with studio-grade narration, on-brand photography, and motion.

*A Monarch skill by [Diamitani Industries](https://github.com/diamitani)*

---

[Quick Start](#-quick-start) • [Features](#-features) • [Pipeline](#-pipeline) • [Brand Kit](#-brand-kit) • [Agent Integration](#-agent-integration) • [Credits](#-credits)

</div>

---

## 🎯 The Problem

"Make me a video" usually means one of three dead ends:

- A **robotic text-to-speech** voice that screams "we cheaped out".
- A **PowerPoint deck** exported to MP4 — static type on flat slides.
- An **off-brand render** because someone hardcoded the wrong font or a neighbor's logo.

**Monarch Video fixes all three.** It compiles a strict brand lock, writes a real
storyboard, narrates with a local neural voice, and renders branded motion with
photographic depth — fully local, no API keys.

---

## ✨ Features

| Feature | What it does |
|---------|--------------|
| **🎙️ Neural voiceover** | Local Kokoro-82M narration — a person, never a robot |
| **🎬 Audio-synced timing** | Scenes re-time to the measured voice clip, so nothing cuts mid-sentence |
| **🎨 Brand lock** | One `brand.json` drives every color, font, and logo; a composition can't drift |
| **🖼️ Photographic scenes** | Full-bleed imagery with a legibility scrim + Ken Burns motion — not slides |
| **🔤 Dual fonts** | Serif display headlines + sans body, from your own font files |
| **📝 Captions** | Auto-captions baked in (optional) for sound-off viewing |
| **📐 Three ratios** | 16:9, 9:16, and 1:1 from one storyboard |
| **🔒 Local & private** | No API keys, no cloud — only npm + model downloads leave the machine |

---

## 🚀 Quick Start

### For AI Agents (Claude, GPT, Hermes, etc.)

1. Download or clone this repository.
2. Point your agent at `SKILL.md`.
3. Say: *"Make a 60-second explainer video from this deck using Monarch Video."*

The agent will load the brand kit, write a storyboard, and run the build.

### For Developers

```bash
# Clone
git clone https://github.com/diamitani/monarch-video.git
cd monarch-video

# One-time setup
npm i -g hyperframes@latest            # renderer
python3 -m pip install kokoro-onnx soundfile   # local TTS (add --break-system-packages if needed)

# Build a video from the bundled example storyboard
bash scripts/build_video.sh templates/storyboard.example.json /tmp/out
```

Output: `/tmp/out/<slug>.mp4`.

---

## 🧵 Pipeline

```
Step 0: brand kit (logo, colors, fonts, images) → brand/
document(s) and/or prompt
        │
   [1] intake.py         → plain text from .pptx .pdf .docx .md .txt .csv .json
        │
   [2] you write          → storyboard.json   (the creative step)
        │
   [3] voiceover.py      → audio/*.wav via Kokoro + scenes re-timed to speech
        │
   [4] compose.py        → index.html, brand-locked, photos + captions baked in
        │
   [5] hyperframes render → <slug>.mp4   (H.264 + AAC, 1920×1080)
```

---

## 🎨 Brand Kit

Everything brand lives in `brand/` — edit `brand.json` once and every video stays locked:

```jsonc
// brand/brand.json
{
  "name": "Acme",
  "font_family": "Inter",              // body
  "font_family_display": "Playfair Display",  // headlines (optional)
  "logo": "auto",                       // corner lockup (or filename / "none")
  "logo_end": "none",                   // end-card: image or text logo
  "fonts": [
    { "file": "Inter-Variable.ttf", "weight": "100 900", "use": "body" },
    { "file": "PlayfairDisplay-Variable.ttf", "weight": "400 900", "use": "display" }
  ],
  "colors": {
    "primary": "#c9a227", "primary_light": "#e8c868", "primary_dark": "#8a6d14",
    "secondary": "#3f3f46", "secondary_light": "#71717a", "secondary_dark": "#18181b",
    "accent": "#f5e9c9", "accent_light": "#fbf5e3", "accent_dark": "#c9b98a",
    "ink": "#09090b", "paper": "#fafafa", "white": "#ffffff"
  }
}
```

Drop logos in `brand/logos/`, fonts in `brand/fonts/`, and royalty-free scene images in
`brand/images/`. Scenes reference images by filename (`"image": "studio.jpg"`). See
`references/image-sourcing.md` for a no-key sourcing workflow and `references/voices.md`
for the voice lineup.

---

## 📁 Repository Structure

```
monarch-video/
├── SKILL.md                    # agent instructions (the skill itself)
├── manifest.json               # skill manifest for agent ecosystems
├── brand/
│   ├── brand.json              # palette + logo slots + fonts (edit this)
│   ├── brand.css               # scene styles, driven by --brand-* tokens
│   ├── logos/  fonts/  images/ # drop your assets here
├── scripts/
│   ├── intake.py               # documents → text
│   ├── voiceover.py            # Kokoro narration + scene re-timing
│   ├── compose.py              # storyboard → brand-locked HTML
│   ├── build_video.sh          # the one command that runs it all
│   ├── framecheck.py           # frame QA without eyes
│   └── logo_audit.py           # brand-kit logo audit
├── templates/storyboard.example.json
├── examples/storyboard-with-images.json
└── references/                 # image-sourcing.md, voices.md
```

---

## 🙏 Credits

Built on **Kokoro-82M** (local TTS), **Hyperframes** (render), and **GSAP** (motion).
See [NOTICE.md](NOTICE.md) for third-party attribution.

