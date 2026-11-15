# Nutritional Guide (Cigala Cycling × Vivify Sports)

The co-branded nutrition guide by Marine Lenehan, rebuilt in the Cigala brand kit (BRAND.md) with a Vivify Sports nod.

- Source: `guide.html` (A4 pages, Anton + Montserrat bundled in `assets/fonts`, topo background baked into `assets/topo-a4.jpg` by `topo-bg.js`).
- Build: `node coaching/nutrition-guide/build.js [previewDir]` writes `Cigala-Cycling-x-Vivify-Sports-Nutritional-Guide.pdf`, reports any page whose content runs into the footer, and saves page PNGs if a folder is given.
- Vivify Sports: logo cut out in white from the original PDF; teal #19444b / #2f6f7a used as the second data colour beside Cigala green.
- Text is Marine's, word for word, apart from the fixes listed in the commit (missing comma, phone format, "WorldTour", contents now lists every section, Section 09/10 headers).
