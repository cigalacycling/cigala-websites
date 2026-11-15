# Theme changes for retail.cigalacycling.com

Changes are made on an unpublished copy of the live theme. They go live only together with Matteo.

## STAGING – SEO titles fix (copy of NEW District)

- Theme ID: `gid://shopify/OnlineStoreTheme/193219133764` (unpublished)
- Preview: https://retail.cigalacycling.com/?preview_theme_id=193219133764
- New file `snippets/seo-meta.liquid` (copy in this folder) outputs the page `<title>` and meta description.
- In `layout/theme.liquid` and `layout/theme_copy_geolocationredirect.liquid`, `{% include 'booster-seo' %}` was replaced with `{% render 'seo-meta' %}`.
- Titles use the format "Name | Cigala Cycling Retail", the same one the Booster SEO app used.
- Descriptions use the SEO description when one is set. Otherwise they use the start of the item's own text, skipping the stock delivery/finance lines at the top of product descriptions.
- Checked on the preview:
  - home, collection, collection page 2, contact page, blog, fr collection, and 15 sampled products: each has 1 title and a clean description
  - the product page at 390px looks the same as live, with no sideways scroll and 1 H1
- Collections and the blog have no description text of their own, so they get a title but no meta description. Adding collection descriptions in the admin would fill these in.

## STAGING – Cigala brand (Horizon)

- Theme ID: `gid://shopify/OnlineStoreTheme/193220739396` (unpublished). This is Shopify's Horizon theme, installed from github.com/Shopify/horizon.
- Preview: https://retail.cigalacycling.com/?preview_theme_id=193220739396
- Design contract: `DESIGN.md` in this folder (to be copied to the theme root).
- Done so far:
  - Theme settings: dark palette, Anton/Montserrat, green buttons, the logo (Files: `cigala-cycling-logo-square.png`, fetched from the staging site), 12px cards, 8px buttons and inputs, red sale badge, cart drawer.
  - `snippets/cigala-brand.liquid`, loaded in `layout/theme.liquid`: contour background, menu hover/current marks, eyebrow and green bar kit, 16px inputs.
- The contour background needs `topo-background-tile.svg` in the store's Files. The rounded-coordinate copy in this folder is 204 KB and looks the same. Matteo uploads it via the upload box, because uploading from this cloud session wasn't allowed.
- Matteo's notes from 15 Nov, done:
  - Product cards: square image box on every listing, and titles held to 2 lines so prices line up.
  - Home "why" panel: green line icons, and the heading is now "Buy with confidence".
  - Footer: the shop's own tagline ("Your Cycling & Triathlon needs at your fingertips").
  - Footer reviews: "★ Google reviews" and "★ Trustpilot reviews" (https://ie.trustpilot.com/review/www.cigalacycling.com) in the Contact column, plus the shared 7-icon social row (`snippets/cigala-social.liquid`, from shared/social).
  - Menu: uppercase, with the underline only as wide as the word.
  - Bright inline colours in old product descriptions are toned to brand text.
- New logo "Cigala Cycling Retail" (`logo/cigala-cycling-retail-logo.png`, 343px) is in Files as `cigala-cycling-retail-logo.png`. It was fetched by Shopify from the staging WordPress media library (id 733) and is set as the header logo, footer logo and favicon.
- Waiting on Matteo: the contour background upload. Staging WordPress refuses SVG files, so it can't be routed that way.
- Round 2 (15 Nov):
  - Footer newsletter posts to the shared Brevo form (same list as cigalacycling.com), with the agreed wording.
  - The topo background is on the footer only (body is plain #08090a). The footer image is `cigala-topo-footer.webp`, rendered at 2004px from the SVG master (76 KB, Files; fetched via staging media id 734); the source is in this folder.
  - The footer logo now has a 1x/2x/3x srcset.
  - Product pages: new `blocks/cigala-trust.liquid` (fast delivery, finance, expert support, duties & taxes included) under the buy buttons. All texts are editable.
- Privacy policy update: drafted in `retail/PRIVACY-DRAFT.md`, not applied.
- Round 3 (15 Nov):
  - The trust strip now uses the old site's four points: Secure checkout, Quick shipping, 30 days returns, Quick support. No phone number or delivery times.
  - New `blocks/cigala-finance.liquid` under the buy buttons. It has the humm by flexifi widget (same merchant id as the old theme, now over https) and a `<klarna-placement>`. `snippets/cigala-klarna-globals.liquid` sets `window.KlarnaThemeGlobals` like the old theme.
  - These could not be seen from the cloud browser, because it blocks the widget hosts. Check them in a normal browser.
  - App embeds copied from the old theme: Labeler, Judge.me, PushOwl, Selecty, STOQ; Inbox stays off.
  - Prices are bigger (cards 15px, product page 24px).
  - YouTube iframes, images and tables in descriptions are now responsive. A 560px video was causing sideways scroll on phones.
- Round 4 (15 Nov, "finish the rest"):
  - The new theme has every app piece the old theme had:
    - Ordersify Restocked Alerts (`snippets/ordersify-bis.liquid` + `#osf_bis`, brand colours)
    - Hextom Sales Boost (`hextom_usb_main`, `hextom_usb_coll` in product cards; `hextom_usb_cart` is copied but not placed)
    - Judge.me review widget (custom-liquid section under the product)
    - Labeler's data feed (`templates/search.acoProductLabelJson.liquid`)
    - `templates/product.pre-order.json`
  - Google Tag Manager GTM-5D9TJGX5 and Google Ads AW-806343489 are back, behind cookie consent (`snippets/cigala-tracking.liquid`, Customer Privacy API).
  - The test browser exits in the US, where Shopify needs no consent. The EU behaviour needs checking from Ireland (LAUNCH.md).
  - Contact page: `sections/cigala-contact.liquid` + `templates/page.contact.json` (Tours/Coaching layout). The live H1 "Contact" and the live intro wording are kept.
  - Search page gets an H1. Horizon's title/description are replaced by `snippets/seo-meta.liquid` (same rules as the SEO fix), with a fallback description for collections that have none.
  - `snippets/cigala-schema.liquid` puts back the structured data the old theme had: WebSite + SearchAction on home, ItemList on collections and the blog.
  - The Shopify cookie banner is restyled like shared/consent (dark bottom bar, Decline outlined first, Accept green). The wording is set in the admin (LAUNCH.md).
- Black Friday copy: "STAGING – Black Friday (Cigala)", `gid://shopify/OnlineStoreTheme/193226244420`. Preview: https://retail.cigalacycling.com/?preview_theme_id=193226244420
  - `sections/cigala-bf.liquid` band above the hero ("BLACK FRIDAY", countdown to 2026-11-30 23:59 Irish time, "Shop the deals" to /collections/bfcm).
  - A "Black Friday deals" row from the BFCM collection, and a BF announcement bar.
  - Any later change to the main theme must be repeated here.
- Tools: `tools/crawl_preview.sh` (curl crawl of an unpublished theme) and `tools/compare_preview.py` (checks against the baseline).
- Round 5 (15 Nov): consistency with the other sites and the sale season.
  - Shared status dot (shared/dot) on product pages via `blocks/cigala-stock.liquid` (In stock / Low stock ≤3 / Available to order / Out of stock).
  - "Cookie settings" link in the footer legal row (reopens Shopify's preferences).
  - The sale-season theme `193226244420` is renamed "STAGING – Black Friday + Cyber Monday (Cigala)". It switches itself by date via `snippets/cigala-season.liquid`:
    - before Mon 30 Nov 2026 00:00 UTC: Black Friday look, red accents, "Black Friday deal" stickers
    - from then: Cyber Monday look, green accents, "Cyber Monday deal" stickers
  - Every product on sale (compare-at price above price) gets the sticker on cards and on the product page.
  - The CM switch was tested by temporarily moving the date, then put back.
  - The theme library is full (20 themes), so a separate Cyber Monday theme couldn't be made. Deleting old themes needs Matteo (the API refuses).
- Sale price changes: when Matteo asks for Black Friday price drops, log each variant's original price and compare-at price in `retail/price-changes/YYYY-MM-DD-<collection>.json` before changing anything. Set the compare-at price to the original so the sticker shows. Restore from that file after the campaign (scheduled task).
- Round 6 (15 Nov), Matteo's sale-season notes:
  - Stickers: black for Black Friday, violet (#7c3aed, light #a78bfa) for Cyber Monday. The cards use the `color-custom-badge-sale` badge.
  - Every sale product page shows a ticking countdown (`snippets/cigala-deal-clock.liquid`) in the sticker colour:
    - "Black Friday deals end in", to Sun 29 Nov 23:59
    - "Cyber Monday deals end in", to Mon 30 Nov 23:59
  - Season dates (Matteo, 15 Nov): Black Friday look from now until the end of Sunday 29 Nov, Cyber Monday look on Monday 30 Nov.
    - `cigala-season` returns bf / cm / off. "off" (from Tue 1 Dec 00:00) hides all campaign pieces as a safety net.
  - On Cyber Monday the page, header, footer and panels turn violet (#120a24 base, violet band).
  - Bottom campaign bar (`snippets/cigala-campaign-bar.liquid`): text, countdown and "Shop the deals" (/collections/bfcm). It can be closed for the session, and switches wording and colour on Cyber Monday.
- Round 7 (15 Nov), in both the main and sale-season themes:
  - `snippets/cigala-stock-status.liquid` puts a pulsing status dot on product cards and product pages:
    - blue "Back order" when the description mentions back order / backorder / back-order
    - red "Out of stock"
    - amber "Low stock" (≤3)
    - green "In stock"
  - The "Sold out" badge is red with white text.
  - Judge.me is in brand colours: green buttons and bars, gold stars, Montserrat/Anton.
  - Sale theme only:
    - The "Shop the deals" button in the home band is white (Matteo, 15 Nov).
    - The bottom bar button stays green.
    - "Deal ends in" replaces "Black Friday deals end in" on the countdowns.
    - During Black Friday the home band and announcement don't mention Cyber Monday (eyebrow "Black Friday", announcement "Black Friday deals are live · Shop the deals").
- Round 8 (15 Nov), both themes:
  - Each home category tile shows its best seller (by Shopify BEST_SELLING), using a new `product` setting on the tile block:
    - Assioma UNO
    - KICKR CORE 2 with Zwift Cog and Click
    - Garmin Edge 1040 (the top seller, the Varia radar, isn't a computer)
    - C-Bear alloy pulley
    - Zone3 men's Agile
    - Normatec 3.0 legs
  - "Advice from racers" is now "Advice from experts".
- Round 9 (15 Nov): new page templates in the Cigala style:
  - Reusable sections: `cigala-page-hero`, `cigala-split`, `cigala-cards` (icons or numbered steps), `cigala-band` (photo + CTA), plus `snippets/cigala-icon.liquid`.
  - `templates/page.about.json`:
    - Keeps the live story wording. Matteo's cut-out photo is in the hero, and the story is shown as numbered cards.
    - The **registered (home) address is removed** (shared/BUSINESS.md). The page shows company name, CRO, VAT and "Co. Wicklow, Ireland" only.
  - `templates/page.bike-to-work.json`: keeps the live wording and the H2s "Introduction" and "Rules". The scheme logo image is replaced by a team photo.
  - `templates/page.finance.json`: rewritten (Matteo: "change everything"). It keeps the humm facts (little things <€500, 3 months 0%; big things up to €15,000, 36 months) and the apply link.
  - Page templates are set via the API: about-us → about, bike-to-work → bike-to-work, finance → finance. The live old theme lacks them and falls back to its page template, so it is unchanged (checked).
  - Until then the pages can be previewed with `?view=about` etc.
  - File alt text set for IMG_3999… and IMG_4003… (the About photos).
  - Home tile 5: Wetsuits is replaced by Sport Watches (`watches`, photo: Garmin Forerunner 55, its best seller).
  - Collection and search grids now keep side margins on phones (`full_width_on_mobile: false`). The first product was being cut off at the screen edge.

## Round 10 (15 Nov 2026): policies, topo pages, About/Bike to Work fixes

**Store content**

- **Returns page** (`/pages/returns`):
  - Removed the old "Cycling holidays refund/cancellation" section (tours T&Cs and waiver) and the pasted old-theme markup.
  - Legal references corrected from UK/NZ law to Irish law: EU (Consumer Information, Cancellation and Other Rights) Regulations 2013 and the Consumer Rights Act 2022.
  - Standard delivery is refunded when an order is cancelled within 14 days.
  - Typos fixed.
- **Terms page** (`/pages/terms-of-service`):
  - Same legal fixes.
  - "Governed by the laws of [home address]" now reads "the laws of Ireland".
  - Black Friday promotion dates now say it runs until 30 Nov.
  - Broken link icon removed; Privacy Policy link added.
- **Shop policies (privacy, refund, terms):** the connector has no write access to policies. Paste-ready HTML is in `retail/policies-new/` (privacy.html, refund.html, tos.html), and Matteo pastes them in Settings → Policies.
  - The privacy policy also removes the home address and adds: Who we are, One newsletter, the Google, Meta, Judge.me, PushOwl and STOQ/Ordersify sections, and the DPC.
- **Backups:** originals are in `retail/policies-before/` (home address redacted).

**Theme (both themes)**

- Contour background behind every page template (About, Contact, Bike to Work, Finance, Returns, Terms, …).
- The photo band has a new "Photo focus" setting:
  - About: 50% 18%, so faces aren't cut off.
  - Bike to Work "Talk to us": the lake ride photo replaces the smart bike.
- Less space between the page hero and the first card section (20px).
- Home tile "Power Meters" now uses the Favero Assioma PRO RS-2. The Assioma UNO/DUO are being discontinued.
- Sale theme only: the bottom "Shop the deals" button is white.

**Matteo's answers (15 Nov 2026)**

- **Home address in the shop policies:** Matteo is fine with it being there. The cleaned versions leave it out anyway. The Terms clause now reads "laws of Ireland", which is the correct wording.
- **Shipping outside the EU:** the Terms are right, it is US and Canada only.
- **Redirects created:**
  - `/products/assioma-uno` → `/products/favero-assioma-pro-rs-1`
  - `/products/assioma-duo` → `/products/favero-assioma-pro-rs-2`
  - Shopify only follows a redirect once the product page is gone, so they start working when the UNO and DUO are archived.
- **Checking later:** the festive returns section and the automatic BFCM collection.
- **Failed or refused delivery charges:** Matteo confirmed the Returns page amounts. The Terms page (live page content) now uses the same: €10 Ireland / €35 EU per package, and €25 / €60 for bulky items (it had €7 / €19 and €49). The drafts in `retail/policies-new/` are updated to match.
- **Shop policies pasted (15 Nov 2026):** Matteo pasted the Privacy, Refund and Terms of service drafts into Settings → Policies. Checked against the drafts: identical text, with the new delivery charges and Irish consumer law. The festive returns section is still in the Refund policy and Terms, waiting for Matteo's decision.
