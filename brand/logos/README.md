# Logos

Drop logo files here — SVG preferred, transparent PNG works.

- Point `logo` (corner lockup) and `logo_end` (end-card lockup) in `brand/brand.json`
  at the filenames, or leave `"auto"` to use the first image found.
- Set `"logo_end": "none"` to force the text logo on the end card (use this when the
  image mark would clash with the brand-color gradient).
- For dark backgrounds, a light/reversed variant reads best as the corner lockup.
- Empty folder = the brand name renders as a clean text logo until a real logo is added.

Audit candidates with `scripts/logo_audit.py logo1.png logo2.png` to check transparency,
mark color, and whether a mark is safe to recolor.
