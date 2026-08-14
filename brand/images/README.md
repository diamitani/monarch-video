# Images

Drop royalty-free photographic images here (JPG/PNG, landscape, 1920px+ recommended).
Scenes reference them by filename via the storyboard `image` field:

```json
{ "id": "s1_hook", "layout": "hook", "image": "studio.jpg", "headline": "...", "narration": "..." }
```

- Prefer **landscape**, ≥1920px wide. `compose.py` renders them full-bleed with a
  dark legibility scrim (text on the left, photo breathing on the right) plus a slow
  Ken Burns zoom so image scenes move like video, not slides.
- **No identifiable people** without documented consent — objects, gear, environments,
  and abstract light shots work best.
- License must permit commercial use and derivatives (CC0, CC-BY, or your own).
  CC-BY requires attribution — keep a credit list; see `references/image-sourcing.md`.
- Upscale soft images before use:
  ```bash
  ffmpeg -y -i src.jpg -vf "scale=1920:-2:flags=lanczos,unsharp=5:5:0.35" out.jpg
  ```
- Empty folder = scenes fall back to typography + brand gradient (no photo).
