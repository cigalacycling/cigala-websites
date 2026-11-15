# Live check after publishing the Black Friday theme (15 Nov 2026)

The live theme is now "STAGING – Black Friday + Cyber Monday (Cigala)" (193226244420). All 234 baseline URLs were crawled on the live site with `tools/crawl_preview.sh` and compared with `tools/compare_preview.py`.

| Check | Result |
|---|---|
| Pages answering 200 | 234 / 234 |
| URLs | unchanged |
| Sitemaps | index unchanged (Shopify-generated) |
| Titles | 233 pages now have a "Name \| Cigala Cycling Retail" title. The old theme output none. |
| Meta descriptions | 219 pages gained one. 14 pages that had none before still have none (listed below). |
| H1 | one per page. The home page gained "Ireland's #1 Online Cycling Store", which it had no H1 for before. |
| Structured data | kept. 8 products show ProductGroup instead of Product (they have variants), which is the richer type. |
| Image alt | 1 image without alt, the one in the Bike Computers collection description (already known, content fix). |

**Pages with no meta description, before and after:** blog, Bikes, Compression boots, Computer & HRM, Frames, Helmets, Indoor trainers, Nutrition, Pissei size guide, Power meters, Sensors & accessories, Sunglasses, Wheels, Zipp. They have no description text in the admin. Adding a short one in each page's SEO box would fill them in.

`/agents.md` is a Shopify-generated file, not a page, so it has no title or H1.
