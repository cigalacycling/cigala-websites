# retail.cigalacycling.com: SEO and product audit

Taken 15 Nov 2026. Read-only: nothing on the store was changed.

## What was captured (the "before" record)

| File | What it is |
|---|---|
| `sitemaps.json` | Every URL in every sitemap: 1,691 English URLs, plus fr/de/it/es/nl copies (10,141 in all) |
| `products-admin.json` | All 1,787 products from the Shopify admin: handle (URL), status, SEO title/description, description start, every image with its alt text and size, stock, vendor, type |
| `baseline-live-pages.json` | 234 live pages crawled in full: home, all 198 collections, 25 info pages, 8 products. Each has its title, meta description, canonical, hreflang, H1/H2, image alt text and structured data |
| `product-issues.csv` | One row per active product with its problems listed, ready to open in Excel/Sheets |

**Gap:** Shopify blocked the crawler on product pages after the first few, so the remaining ~1,450 live product pages weren't crawled. Product URLs, SEO fields and alt text are all captured from the admin instead. The theme renders every product page the same way, so the findings below apply to them too.

## 1. Urgent: no page on the store has a title or meta description

Not one of the 234 crawled pages has a `<title>` tag or a meta description.

**Why:** the live theme ("NEW District") hands titles and descriptions to a snippet from the **Booster SEO** app. The theme's own title and description lines were commented out. The app has since been uninstalled, so Shopify skips its snippet. The page source says so:
`<!-- "snippets/booster-seo.liquid" was not rendered, the associated app was uninstalled -->`

**Effect:** Google has no page titles to show and makes up its own from the page content. This costs rankings and clicks across all ~1,700 URLs and the translated copies.

**Fix:** a small theme change, tried on a copy of the theme first. Bring back the titles in the same format Booster used (`Product name | Cigala Cycling Retail`) and descriptions from the product/collection text. Nobody wrote titles or descriptions by hand (no product has a custom SEO title or description), so nothing is lost. **Needs Matteo's go-ahead.**

## 2. Images and alt text

- 6,611 images on 1,495 active products. **3,088 have no alt text**, spread over 603 products. Worst brands: Garmin (635), Albaoptics (266), CeramicSpeed (159), Air-Relax (113), Sweet Protection (107), Shokz (102), Withings (98), Wahoo (90).
- 1,345 product images are under 800px on their longest side, which is soft on retina screens and when zoomed.
- One active product has no image: `1x-one-to-one-session`.

Fix: write descriptive alt text for the 3,088 (product name plus what the photo shows). Existing alt text stays untouched.

## 3. Products

- 1,495 active, 221 draft, 70 archived, 1 unlisted.
- **467 active products are out of stock** (stock tracked, 0 or less). Most are Garmin (75), Cycling Ceramic (36), Jackery (21) and Zone3 (19). 319 active products don't track stock at all.
- 22 drafts have stock: products you could sell that are hidden.
- 21 handles contain "copy", left over from duplicating products, e.g. `cycplus-t3-high-power-smart-trainer-copy`. Changing a URL needs a redirect, so these get flagged only, not changed.
- 20 active products aren't on the Online Store channel, 21 are in no collection, and 46 have no product type.
- 5 have no description, 25 have a thin one (under 150 characters).

The full list is in `product-issues.csv`.

## 4. Headings and structure

- One H1 per page everywhere except:
  - `/pages/finance`, which has two H1s
  - `/pages/preview-geobar` and `/agents.md`, which have none
- Canonicals are all correct. Hreflang is set for en/fr/de/it/es/nl and several country versions.
- Structured data: Organization on every page, ItemList on collections, Product on product pages. The WebSite schema with site search came from Booster and is gone.

## 5. Tracking, consent and privacy policy

- Google Tag Manager (`GTM-5D9TJGX5`) and the Google Ads tag (`AW-806343489`) are hard-coded at the top of the theme. They load before the visitor answers the cookie banner, which breaks the rule that tracking only loads after consent. Fix: load them through Shopify's Customer Privacy API.
- Shopify's own cookie banner is on, and TAWK chat is on the store.
- The privacy policy page still lists TAWK and should be updated to match the tools the store really uses: Google Analytics/Ads, the Meta Pixel if used, and the chat tool.
- The cookie banner should be restyled to match the other Cigala sites (dark bar, outlined Reject, green Accept), using Shopify's banner rather than adding a second one.

## 6. Housekeeping

There are 9 unused themes (Debut, Venture, Simple, Minimal, District, "Back up 17/11" and 3 demos), some from 2018–2020. They're safe to delete once a fresh backup of the live theme exists.

## Suggested order

1. Restore titles and meta descriptions (item 1). Biggest SEO win, small change, test on a theme copy first.
2. Move tracking behind consent and update the privacy policy (item 5).
3. Alt text for the 3,088 images, done by brand (item 2).
4. Stock and drafts tidy-up with Matteo (item 3).
5. The brand redesign on an unpublished theme copy.
