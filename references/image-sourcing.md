# Sourcing royalty-free images

Photo scenes need images that are (a) landscape and 1920px+, (b) free of identifiable
people, and (c) licensed for commercial use + derivatives. The two no-key sources below
cover all three without an account.

## Fast path — Openverse (aggregates Flickr + Wikimedia, CC-licensed)

`https://api.openverse.org/v1/images/?q=<query>&license_type=commercial&per_page=20`

- `license_type=commercial` filters to CC0 / CC-BY / CC-BY-SA (commercial OK).
- Every result has a `license`, `license_url`, `creator`, and a direct `url`.
- Flickr results come back at 1024px (`_b`); try swapping the size suffix in the URL
  (`_b` → `_h` = 1600, `_k` = 2048). If the larger render 404s/410s, keep `_b` and
  upscale (below). Wikimedia results are often already 1920px+.

```bash
curl -s "https://api.openverse.org/v1/images/?q=recording+studio&license_type=commercial&per_page=20" \
  | python3 -m json.tool | grep -E '"license"|"url"|"title"|"creator"'
```

## High-res fallback — Wikimedia Commons API

```bash
curl -s "https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=recording+studio&gsrnamespace=6&gsrlimit=10&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1920&format=json"
```

- `iiurlwidth=1920` returns a clean 1920px thumbnail URL directly.
- `extmetadata.LicenseShortName` gives the license; `Artist` gives attribution.

## Filtering for video

- **Landscape only:** reject `width/height < 1.2`.
- **No faces:** reject titles/descriptions containing `person`, `people`, `portrait`,
  `selfie`, `man`, `woman`, `group`. Prefer objects, gear, environments, light.
- **License:** prefer CC0 (no attribution) and CC-BY (attribution only). Avoid
  CC-BY-SA and CC-BY-ND for a commercial brand film unless you're comfortable with
  share-alike / no-derivatives terms.

## Post-processing

Upscale soft images and restore edge crispness before dropping them into `brand/images/`:

```bash
ffmpeg -y -i src.jpg -vf "scale=1920:-2:flags=lanczos,unsharp=5:5:0.35" brand/images/scene.jpg
```

## Attribution

Keep a credit list for CC-BY assets (author + license + source URL) and ship it with
the video (description, end screen, or a credits file). CC0 needs no attribution but
crediting anyway is good practice.
