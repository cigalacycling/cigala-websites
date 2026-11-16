# Italian versions (-IT) of the six coaching PDFs

- `it.json`: every English string → Italian (1,040+ entries). `translate.py` swaps them into a copy of each finished English HTML (`*-IT.html`), plus a few fixes in `POST` (split cover title, plate labels, Italian number format, slightly tighter heading spacing because Italian runs longer).
- Build: `python3 -I coaching/italian/translate.py && node coaching/italian/build.js [previewDir]` → `*-IT.pdf` next to the English PDFs.
- After changing an English document: rebuild it, run `translate.py --list` to see new strings without a translation (written to `todo.json`), add them to `it.json`, then build.
- Matteo (16 Nov): the Italian Nutritional Guide and Supplement List are not drafts; no separate approval needed.
