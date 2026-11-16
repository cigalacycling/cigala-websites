# Training sheets (Cigala Cycling Coaching)

Gym Circuit Winter First Month, Gym Circuit Winter Second and Third Month, Gym Circuit In Season, Stretches & Core, rebuilt in the brand kit (same stylesheet as `../nutrition-guide/`).

- Build: `python3 -I coaching/training-sheets/make.py && node coaching/training-sheets/build.js [previewDir]` → `Cigala-Cycling-*.pdf`.
- Gym photos: free-exercise-db (github.com/yuhonas/free-exercise-db), public domain (Unlicense), in `img/exercises/` (`<id>_0` start, `<id>_1` finish); mapping in `PHOTO` in `make.py`. "Back extension on side" has no exact match, so it uses the side bend on a ball.
- Stretches & Core photos: Matteo's own, extracted from his PDF (`img/sc-*`).
- Colour key (same in all four): green = strength & core, blue = bike & cardio, yellow = stretching & mobility, red = the Important notes only.
- Wording is Matteo's. Only spelling/grammar was fixed (thighs, plank, overdo it, Explosive, recover well, g, Wattbike/exercise bike, emails), and the Stretches & Core text is in sentence case instead of capitals.
- Open point: exercises 13 and 14 in Stretches & Core have the same text in the original (14's photo shows both arms behind the head).
