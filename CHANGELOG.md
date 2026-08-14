# Changelog

## 1.0.0 — 2026-08-13

Initial public release as a Monarch skill.

- Brand-locked MP4 pipeline: intake → storyboard → Kokoro voiceover → compose → render.
- Brand kit manifest (`brand/brand.json`): palette, logo slots, dual font families, images.
- Per-scene photographic backgrounds with legibility scrim + Ken Burns motion.
- Text-logo fallback and `logo_end: "none"` for brand-color end cards.
- Voice profiles (`warm`, `pro`, `bright`, `direct`, `narrator`, `uk-f`, `uk-m`) + raw Kokoro ids.
- Diagnostic tools: `scripts/framecheck.py` (frame QA without eyes), `scripts/logo_audit.py` (brand-kit logo audit).
- Reference docs: image sourcing, voices.
