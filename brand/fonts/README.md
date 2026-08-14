# Fonts

Drop font files here — `.otf`, `.ttf`, or `.woff2`.

List them under `fonts` in `brand/brand.json` with the weights they cover
(400 = regular, 500 = medium, 600 = semibold, 900 = black) and which family
they belong to (`"use": "body"` for the sans stack, `"use": "display"` for
headline serif):

```json
"font_family": "Brand Sans",
"font_family_display": "Brand Serif",
"fonts": [
  { "file": "BrandSans-Regular.otf", "weight": 400, "use": "body" },
  { "file": "BrandSans-SemiBold.otf", "weight": 600, "use": "body" },
  { "file": "BrandSerif-Black.otf", "weight": 900, "use": "display" }
]
```

- `font_family_display` is optional — omit it and headlines use the body font.
- Variable fonts work too: set `"weight": "100 900"`.
- If `fonts` is empty, any files here auto-load at weight 400, and an empty folder
  falls back to a system font stack.
