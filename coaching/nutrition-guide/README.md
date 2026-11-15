# Nutritional Guide (Cigala Cycling × Vivify Sports)

The co-branded nutrition guide by Marine Lenehan, rebuilt in the Cigala brand kit (BRAND.md) with a Vivify Sports nod.

- Source: `guide.html` (A4 pages, Anton + Montserrat bundled in `assets/fonts`, topo background baked into `assets/topo-a4.jpg` by `topo-bg.js`).
- Build: `node coaching/nutrition-guide/build.js [previewDir]` writes `Cigala-Cycling-x-Vivify-Sports-Nutritional-Guide.pdf`, reports any page whose content runs into the footer, and saves page PNGs if a folder is given.
- Vivify Sports: logo cut out in white from the original PDF; teal #19444b / #2f6f7a used as the second data colour beside Cigala green.
- Text is Marine's, word for word, apart from the fixes listed in the commit (missing comma, phone format, "WorldTour", contents now lists every section, Section 09/10 headers).

## Colour rule (v2, Matteo asked for a clear logic)
- Green = recommended / do this (key numbers, bullets, intensity meters, icons).
- Red = avoid (trans fats, processed meat) and the "From the coach" box only.
- Grey = neutral or moderate (low-fibre foods, saturated fat, isolated proteins, high GI).
- Vivify teal = Vivify Sports only (Marine's contact panel).
- Number boxes are all dark; scales (carbs per day / per hour) show a 5-step green meter.

## Added in v2 (from Matteo's coaching blog posts and the Coaching Nutrition page)
- Section 07 Recovery & race day (3:1 rule, race day timeline) — posts 4913, 4890.
- Hydration page 2: 2% → 6%, 2 L a day, 2–3 g salt per litre, sweat-rate example — post 4902.
- Energy needs 2,500–10,000 kcal on the Athlete's Plate page — post 5205.
- Consultation contents, nutrition per coaching package, free calculators — Nutrition page 3995.
- Calculator links point to coaching.cigalacycling.com/tools/…, which only work once the tools go live.
