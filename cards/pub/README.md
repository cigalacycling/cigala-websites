# Tour cards: FINAL set (approved by Matteo, 2026-11-14)

Use these for the new tours website and for Instagram. Don't redesign them; the style rules are in
`brand\tours\card-style.md`. Nothing here has been uploaded to the live site yet.

| Folder | What | Size | Use |
|---|---|---|---|
| `cards-web\<slug>.jpg` | Website tour card, 4:5 | 1100×1375 JPG, ~180 KB | **Upload these to the website** (sharp on retina at the 440×550 card size) |
| `cards-HQ\<slug>.png` | Same card, full quality | 2200×2750 PNG, ~3.5 MB | Master copy, print, re-exports |
| `stories-HQ\<slug>-story.png` | Instagram Story, 9:16 | 1080×1920 PNG | Instagram / Facebook Stories |

`manifest.json` lists every tour: slug, title, trip page URL, tags, the three file paths and suggested alt text.
The slug matches the trip page address (`tours.cigalacycling.com/trips/<slug>/`).

## For the website rebuild
- The card already carries the tour name, flag, type, dates, level, distance and elevation, so the website card
  needs **no text overlay** on top of it: show the image, link it to the trip page, and put the tour name in the
  alt text / a visually hidden heading for SEO and screen readers.
- Show at 4:5 (`aspect-ratio: 4 / 5; object-fit: cover`), never cropped to another shape: the text sits close to the
  edges. On phones, keep 4:5 too (one card per row).
- The cards hold dates and figures: when a tour's dates, distance, elevation or level change, the card must be rebuilt
  (`py -3.12 tools\tour_card.py --levels content\tour-cards\specs\<slug>.json`, then copy into this set).

## Notes
- Levels for French Alps (Intermediate & Expert) and Alpine Gravel Escape (Expert) were confirmed by Matteo; the
  live trip page headers still say otherwise.
- Figures that differ between the old cards and the trip pages: `content\tour-cards\REVIEW.md`.
- Per-photo framing (Chianti rider moved right, Slovenia church raised) is stored in each spec's `frame`.
