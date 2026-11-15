# Cigala Cycling websites

This repository holds the redesign of the Cigala Cycling sites in the Cigala Cycling brand:

1. cigalacycling.com: built on staging, waiting to go live
2. tours.cigalacycling.com: designs done, fresh SEO baseline taken 15 Nov; waiting for Matteo to create the Hostinger staging copy
3. coaching.cigalacycling.com: homepage and Individual Packages built on staging (15 Nov); the other pages are next (see `coaching/SEO-DECISIONS.md`)
4. retail.cigalacycling.com: runs on Shopify, not started

## Ground rules (from Matteo)

- **Never lose SEO, only improve it.** Keep these exactly as they are:
  - URLs
  - Yoast titles and meta descriptions
  - H1/H2 wording (only approved changes)
  - body copy
  - image alt text
  - sitemaps
  - structured data

  Take a baseline crawl before changing anything and compare against it afterwards (`tools/crawl.py`).
- **Work only on Hostinger staging, never on the live sites.** Pushing staging to live is done together with Matteo.
- **Credentials:**
  - Never ask Matteo to paste a password into the chat.
  - WordPress application passwords are saved on the cloud environment through the credential tool. The proxy then adds them to requests for the staging host.
  - No secrets in this repository.
- **Every page must:**
  - work at phone, tablet and desktop widths (390/820/1440, with no sideways scroll)
  - have one H1
  - have alt text on every image
- **Brand:** follow `BRAND.md`. It covers:
  - colours: green `#009a44`, red `#E10600`, green text `#34c46a`, red text `#ff3d33`
  - fonts: Anton and Montserrat
  - the topo background tile at 60% dim
  - red eyebrows and spacing ("nothing touching")

## Layout

The repository keeps the original working layout so the build scripts run unchanged. Each script finds the repository root from its own location.

| Path | What it is |
|---|---|
| `BRAND.md`, `bk/` | Brand kit (README, tokens, design system) |
| `brand.css`, `part_header.html`, `part_footer.html`, `part_home_main.html`, `terms.txt`, `home/` | **cigalacycling.com** preview source. `home/img` holds the source photos; `home/topo-*` is the background |
| `tools/build.py` | Builds the cigalacycling.com preview: `home/index.html` plus about, contact and terms |
| `tools/build_wp.py` | Builds the Elementor payloads for **staging.cigalacycling.com** into `wp/out/` |
| `shared/consent/` | **Shared cookie banner for all sites** (template, renderer, head snippet, WPCode line, install guide). cigalacycling.com renders it with GA G-955J6LHQ2P and Pixel 1986332861692106. The chat button works before consent. |
| `wp/nl-band.html`, `wp/nl-popup.html` | Newsletter signup in the footer and as a pop-up. It posts to the Brevo form, which saves to the "cigalacycling.com" list. |
| `stg/backup/` | Original staging pages and templates, taken before the redesign (to restore from) |
| `stg/media.json`, `stg/media-webp.json` | Staging media IDs and URLs. The WebP set is the one in use. |
| `webp/` | WebP images (quality 90, from the largest originals) |
| `baseline.json` | SEO crawl of the live cigalacycling.com before the redesign |
| `crawl-staging-now.json`, `audit/` | Latest staging crawl and the tracking/image audit |
| `tools/build_tours.py`, `tourspages/`, `tp/`, `tp2/` | **tours.cigalacycling.com**: the 7 page designs and the extracted live content |
| `survey/NfmCmGsjq4LL9bTAi38NXN/` | Tours homepage design |
| `trip/` | Tours trip-page design (Dolomites: 323 km, 8,800 m) |
| `tools/coaching_common.py`, `tools/build_coaching_*.py`, `coachingpages/` | **Coaching** page previews (`coachingpages/*.html`, screenshots in `coachingpages/shots/`). `coaching_common.py` holds the shared header, footer, design system and the SEO check (live H1/H2s kept, every image has alt). Homepage approved by Matteo 15 Nov; Individual Packages waiting for review |
| `coaching/baseline.json` | SEO crawl of the live Coaching site before the redesign: 76 sitemap URLs (23 pages, 53 posts), all 200 |
| `coaching/SEO-DECISIONS.md` | **Approved** coaching SEO fixes (typos, one H1 per page, redirects for `/dummy-page/` and `/group-club-packages2/`, missing alt text). Apply on staging only |
| `coaching/html/`, `coaching/text/`, `coaching/css/` | Live coaching pages: raw HTML, extracted copy/headings/links/images, Elementor CSS |
| `coaching/webp/`, `coaching/images.json` | Every coaching image as WebP q90 (long edge ≤2560) + manifest: original URL, alt, background or not, pages. Originals go to `coaching/img/` (gitignored). Re-run: `python3 -I tools/extract_site.py coaching.cigalacycling.com coaching` |
| `tours/baseline.json` | SEO crawl of the live Tours site before the redesign |
| `tours/baseline-2026-11-15.json`, `tours/sitemap-urls-2026-11-15.txt` | Fresh live Tours crawl taken before the staging build (121 URLs, 90 from the sitemaps). Identical to `tours/baseline.json`. Re-run: `python3 -I tools/crawl.py tours.cigalacycling.com $(cat tours/sitemap-urls-2026-11-15.txt)` |
| `cards/` | Tour cards (web, high-quality and story versions) |
| `cp/`, `cand/`, `live/` | Source photos taken from the coaching and live sites |
| `tools/*.js` | Playwright checks: images, newsletter, pixel, consent order, iPhone zoom, screenshots |
| `tools/recolor.py`, `tools/topo.py`, `tools/extract.py`, `tools/crawl.py` | Colour swap, background trace, Elementor content extractor, SEO crawler |

## cigalacycling.com staging: how to rebuild and push

```
python3 -I tools/build.py && python3 -I tools/build_wp.py
B=https://staging.cigalacycling.com/wp-json
curl -X POST $B/wp/v2/elementor_library/6   -H 'Content-Type: application/json' --data-binary @wp/out/lib-6.json    # kit (global CSS)
curl -X POST $B/wp/v2/elementor_library/170 -H 'Content-Type: application/json' --data-binary @wp/out/lib-170.json  # header
curl -X POST $B/wp/v2/elementor_library/228 -H 'Content-Type: application/json' --data-binary @wp/out/lib-228.json  # footer + banner + newsletter
for id in 10 271 461 564 724; do curl -X POST $B/wp/v2/pages/$id -H 'Content-Type: application/json' --data-binary @wp/out/page-$id.json; done
curl -X DELETE $B/elementor/v1/cache
```

Page IDs:

| ID | Page |
|---|---|
| 10 | Home |
| 271 | About |
| 461 | Contact |
| 564 | Terms & Conditions |
| 724 | Privacy Policy (new, /privacy-policy/) |

Elementor snippet 697 holds the head code: it sends a consent update for returning visitors who already accepted. Google's default consent line sits at the top of the WPCode Header box.

## Status, 15 Nov 2026

**cigalacycling.com (staging done):**
- SEO matches live: same titles, metas and robots; only the approved homepage H1 changed.
- Images are WebP, every image has alt text, and the Pixel and Analytics only run after consent.
- Newsletter: single opt-in, with a "sign_up" event in Analytics and "Lead" in Meta. The contact form sends "Contact" to Meta and "generate_lead" to Analytics.

**Launch plan (decided 15 Nov):** all sites go live on the **same day**, once Tours and Coaching are finished on staging. Until then:
- cigalacycling.com staging stays ready as it is.
- **No edits on the live sites.** A push to live overwrites live with staging. If Matteo needs to change something on live, make the same change on staging too.
- Just before launch: re-crawl each live site and compare it with its baseline, take Hostinger backups of each live site, then push the sites one after another on the same morning.

**Before going live:**
- Matteo tests on his phone.
- No edits on live until the push.

**After the push:**
- Revoke the application passwords on live.
- Check robots.txt is not blocking Google.
- Re-crawl live and compare with `baseline.json`.
- Clear the LiteSpeed cache, resubmit the sitemap, and check Analytics realtime and the Pixel.
- About 2 weeks after launch, once the re-crawls match the baselines: delete the staging copies in hPanel first (cigalacycling.com and Tours, plus Coaching), then delete their DNS records (`staging`, `staging.tours`). Never remove a DNS record while its staging copy still exists.

**Week of 23 Nov:**
- Meta domain verification
- Meta Conversions API (a reminder is set)

## Content problems found on the live Tours site

- Gran Canaria page: the H1 says "Mallorca".
- Belgium destination card: links to a 404 page.
- Terms footnote: linked to the retail returns page.
- Algarve page: one sentence is repeated.

The new designs fix the last three. The Gran Canaria H1 still has to be fixed on the live page.

## Tours staging: status 15 Nov

- **Staging:** https://staging.tours.cigalacycling.com. Hostinger's copy sits in the `/staging` folder of tours.cigalacycling.com, with an A record `staging.tours`. WordPress home and siteurl are set to the staging address, and robots.txt has `Disallow: /`.
- **Login:** an application password ("Claude", user `infocigalacycling-com`, administrator) is saved as a network secret for the staging host only. Matteo logs in through hPanel → Staging → Admin panel.
- **DNS** was still spreading on 15 Nov, and many requests got a 502 from the proxy. Retry every request in a loop until it returns 200.
- **Backup:** `stg-tours/backup/` holds all 53 pages, 15 Elementor templates (header 170, footer 228, kit 6, loop items, 404, single post) and 37 posts, taken before any change. Restore from these files.
- Key page IDs: Home 5212, Trips 8689, Granfondo 2796, Gravel 2821, Italian 4402, Custom 1576, Destinations 10, Guides 5030, About 271, Contact 461, Terms 564, Testimonials 2844.

## Tours staging: how to rebuild and push

```
python3 -I tools/build_tours_home.py      # preview tourspages/home.html (from survey/ design)
python3 -I tools/tours_media.py           # WebP q90 images -> staging media (skips ones already uploaded)
python3 -I tools/build_tours_wp.py        # Elementor payloads -> stg-tours/out/
python3 -I tools/push_tours_wp.py lib-6 lib-170 lib-228 page-5212   # staging only, then clears the Elementor cache
```

- **Kit 6** gets the brand CSS, scoped to `.cc`. Pages that haven't been rebuilt yet keep their old look; only header and footer are new everywhere.
- **Header 170:** new nav with the Bike Tours dropdown.
- **Footer 228:** new footer, plus the existing OpenWidget chat and cookie widgets, unchanged apart from the cookie colours.
- **Status 15 Nov:** homepage (5212) is live on staging.
  - Checked at 390/820/1440: no sideways scroll, one H1, alt text on every image, form fields at 16px.
  - Title, meta, canonical, robots and schema match live.
  - The 8 H2s use the live wording (Matteo approved making the label H2s normal text).
- **Menu:** Bike Tours order is All, Road, Gravel, Gran Fondo, Italian, Custom (Matteo). The current page gets a red underline, as on cigalacycling.com; on tour pages "Bike tours" is underlined too.
- **Consent and chat (15 Nov):** Tours uses the **shared banner** `shared/consent/` (`render.py`), with GA4 G-QRF16ZZVDB and OpenWidget org 43e5f685…, both confirmed on the live site.
  - It sits in footer 228, and the footer has a "Cookie settings" link. The old Elementor cookie popup is gone.
  - Elementor custom code **9279** (head) is the shared `head-snippet.html`.
  - **Meta Pixel 1986332861692106:** added on 15 Nov after Matteo confirmed the same pixel on all sites. It loads only after Accept (init + PageView); nothing loads before a choice or after Reject (tested). The banner text is identical to cigalacycling.com.
  - The other tags on live Tours are only GA4, OpenWidget and the WeTravel booking widget (Book now checkout, functional). No GTM, Pixel, Hotjar or Clarity.
  - **WPCode line done (Matteo, 15 Nov).** Checked: `consent default` comes before `gtag/js` and `config` on /, /trips/ and /trips/road-trips/. `tools/dlcheck_tours.js` gives default denied → update granted on Accept → re-granted for returning visitors. `tools/pxcheck_tours.js` gives Pixel only after Accept and none after Reject.
  - **Chat:** OpenWidget picks the template by page address. tours.cigalacycling.com gets the Tours template (196a47eb…); any other address, including the staging one, gets the default Cigala Cycling template. On live it will be right automatically. To preview it on staging, add `staging.tours.cigalacycling.com` to the Tours template's address rule in OpenWidget.
- **Logo:** header and footer use the file Matteo sent on 15 Nov, `tours/brand/ccToursLogo-matteo-2026-11-15.png` (WebP media 9281), with square corners.
- **Signature:** under "Matteo Cigala, Tours Director" in Our story. Cut from the coaching blog image `Matteo-Cigala-6-years-old.png` as white ink on transparent (media 9282).
- **Road tours page (new, 15 Nov):** https://staging.tours.cigalacycling.com/trips/road-trips/, page **9301**, child of Trips 8689.
  - Made with the trip-list design: `tools/build_tours_list.py` (preview `tourspages/road-trips.html`), pushed with `python3 -I tools/push_tours_list.py road-trips`.
  - Rank Math title "Guided Road Bike Tours Europe | Cigala Cycling Tours" and a matching description, set through `/rankmath/v1/updateMeta`. The page is in the page sitemap.
  - Sections: 6 road tours, then the 5 Gran Fondo tours as "Road tours with a Gran Fondo". Dates appear as text on every card.
  - The intro is new copy and still needs Matteo's OK.
  - The list-page CSS is scoped to `.cl` and added to the kit by `build_tours_wp.py`.
- **All five tour pages are rebuilt on staging (15 Nov):** All tours 8689, Road 9301, Gravel 2821, Gran Fondo 2796, Italian 4402. They come from one builder, `tools/build_tours_list.py`.
  - Existing pages keep their live H1, intro text and tour order (`tours/list-pages-live.json`), and the live card alt text.
  - `push_tours_list.py` only changes their content and layout. Title, slug, parent, status and Rank Math SEO are untouched; checked against the baseline, title, meta, robots, OG and schema are identical.
  - Heading tidy-ups approved by Matteo: "2027 Calendar" is an H2; "MORE DETAILS" is no longer a heading; the Italy intro (an H2 on live) is now a paragraph; "Can't find the perfect one?" is the banner's H2.
  - Each page has a row of links to the other tour pages (All, Road, Gravel, Gran Fondo, Italy).
  - **Tour cards, reworked 15 Nov (Matteo):** 3 per row on laptops, 2 on tablets, 1 on phones. Each card has the plain trip photo (live alt text) with the type labels; then badge, H2 name (live wording), location, date / nights / level, the full description (clamped to 4 lines with "Read more"; all text stays in the page), price, early bird, and More details + Book now. The baked-in card images are no longer used on these pages. The `.cl` wrapper is transparent so the topo background shows.
  - Checked at 390/820/1440: no sideways scroll, one H1, alt text on every image, no broken images.
- **Terms (564) and Privacy Policy (new, 9347, /privacy-policy/), 15 Nov:** built in the cigalacycling.com Terms style by `tools/build_tours_legal.py`, pushed with `push_tours_list.py terms` and `push_tours_list.py privacy-policy`.
  - The terms text is the live page word for word, with the same H1, and title, meta, robots, OG and schema are unchanged.
  - The privacy text is in `tours/privacy.txt`: Tours' own processors (WeTravel, tour partners, event organisers, Hostinger, Google, Meta, OpenWidget), with no tracking IDs. **Matteo to review it** (ideally his accountant or solicitor too).
  - The Rank Math title and meta for the privacy page are set.
  - The footer legal row reads Refund/cancellation policy & terms · Privacy policy · Cookie settings. The shared banner (no vendor names) links to /privacy-policy/.
- **Next:** destinations, guides, about, contact, testimonials, the trip pages, and the custom-tour page.
  - The other pages haven't been rebuilt.

## Tours build plan: Matteo's notes, 15 Nov

- **Homepage:** use the design in `survey/NfmCmGsjq4LL9bTAi38NXN/index.html`. It isn't among the 7 pages in `tourspages/`. Keep the live Yoast title and meta. The design's H1 ("Bike tours across Europe's best cycling roads") differs from the live H1, so it needs Matteo's OK; otherwise keep the live H1.
- **Tour categories stay as separate pages**, not one page with filter chips. Each one has its own URL, title, meta, H1 and copy, which Google ranks (e.g. "Italy bike tours"):
  - `/trips/`: all upcoming tours
  - `/trips/granfondo-trips/`: Gran Fondo tours
  - `/trips/gravel-trips/`: gravel tours
  - `/italian-trips/`: Italy tours
  - `/trips/private-trips/`: custom tours
  - Each page uses the trip-list design from `tourspages/index.html`, already showing that category. The chips become links to these pages, not a JavaScript filter.
- **Bike Tours menu** (Matteo, 15 Nov): keep the live dropdown and add Road.
  - All Tours → `/trips/`
  - Granfondo Tours → `/trips/granfondo-trips/`. Live links to `/trips/granfondo/`, which 301-redirects there. Link straight to the final URL, and keep the redirect.
  - Italian Tours → `/italian-trips/`
  - Gravel Tours → `/trips/gravel-trips/`
  - **Road Tours (new)** → `/trips/road-trips/`
  - Custom Tours → `/trips/private-trips/`
- **Road tours:** approved. Add a new `/trips/road-trips/` page (a new URL, so nothing is lost).
- **Homepage H1:** keep the live wording, "Bike Tours & Cycling Holidays Across Europe's Best Cycling Destinations", in the new design (approved).
- **Homepage tour finder** (approved idea, inspired by italybiketours.com's hero search bar). A bar in the homepage hero with three dropdowns: **Tour type** (Road, Gran Fondo, Gravel), **Country** (Italy, France, Portugal, Belgium, Cyprus, Slovenia) and **Level** (Beginner, Intermediate, Expert), plus a **Find tours** button.
  - **Built (preview `tourspages/home.html`, from `tools/build_tours_home.py`):** the finder filters the homepage tour grid in place, and **Find tours** scrolls down to the results. When only one choice is set and it has a category page (Italy, Gravel, Gran Fondo, Road), a "See the … tours page →" link appears, so the category pages keep getting internal links. Screenshots are in `tourspages/preview/`.
  - Reviewer photos aren't in the repository yet, so the preview shows initials. Take the real photos from the live site during the WordPress build.
  - **Month** dropdown (Feb–Oct 2027): the dates are in `tours/trips-2027.json`, read from the card images on the live `/trips/` page. On live they only exist inside the images. On the new cards they'll also be real text, which Google can read.
  - At 390px the bar stacks vertically. Selects use 16px text so iPhones don't zoom in.


## Coaching staging: status 15 Nov

- **Staging:** https://staging.coaching.cigalacycling.com (Hostinger copy). WordPress home and siteurl point to the staging address, and robots.txt has `Disallow: /`.
- **Login:** an application password ("Claude", user `infocigalacycling-com`, administrator) is saved as a network secret for this staging host only. Checked 15 Nov: `wp-json/wp/v2/users/me` answers as Matteo Cigala (administrator).
- **Backup (15 Nov, before any change):** `stg-coaching/backup/` holds all 23 pages, 13 Elementor templates, 54 posts (53 published + 1 empty draft), menus and menu items, categories, tags and site settings. `stg-coaching/media.json` lists the 414 media items (ID, URL, alt). Restore from these files.
- Active templates: header 170 "HEADER 1", footer 228 "footer1", popup 5090 "MENU LAPPY TABI MOBI" (mobile menu), single post 4028, kit 6. The others (5628, 5664, 6311, 4718, 6065, 6068, 6071, 6077) are unused drafts.
- Page IDs: Home 2924, About 2109, About2 (triathlon) 3770, Individual 3338, Tri individual 3795, Group 3738, Group2 3845, Testing 3865, Nutrition 3995, Bike fitting 4256, Blog 4354, Book 1-on-1 3750, Club talk 4395, Vision 3272, Contact 461, Terms 564, Testimonials 2844, Talent scout 896, UK 6098, USA 6100, Canada 6102, Italia 6106, Dummy 6074.
- **Build in progress (started 15 Nov, in parallel with Tours, Matteo's OK):** designs are previewed in the repo first (`coachingpages/`), then pushed to staging.
- **On staging (15 Nov):** homepage https://staging.coaching.cigalacycling.com/ (2924) and Individual Packages https://staging.coaching.cigalacycling.com/individual-packages/ (3338), plus the new header 170, footer 228 and kit 6 CSS (scoped to `.cc`, so the other pages keep their old look under the new header/footer).
  - How: `python3 -I tools/coaching_media.py` (WebP images -> staging media, `stg-coaching/media-webp.json`), `python3 -I tools/build_coaching_wp.py` (payloads -> `stg-coaching/out/`), `python3 -I tools/push_coaching_wp.py lib-6 lib-170 lib-228 page-2924 page-3338 snippet-head` (staging only, clears the Elementor cache).
  - Packages keeps the live Elementor contact form (to info@cigalacycling.com, styled in the brand, 16px fields) and the Shapo testimonials widget.
  - Cookie banner: the shared one (`shared/consent/`), GA4 G-E1WWZCLBRB + Meta Pixel 1986332861692106 + OpenWidget, in footer 228 with a "Cookie settings" link. The old "Got it!" bar and old chat widget are gone. Head snippet = Elementor custom code (ID in `stg-coaching/snippet-head-id.txt`). Tested: nothing before a choice; Accept loads the Pixel; Reject loads nothing.
  - WPCode Header (Matteo, 15 Nov): consent default line pasted first, before gtag.js (checked: dataLayer = consent default denied -> js -> config; Accept -> update granted). The hreflang block is fixed too (see `coaching/SEO-DECISIONS.md`).
  - Checked at 390/820/1440: no sideways scroll, one H1, alt on every image.
- **Triathlon packages (3795) and Group & Club (3738), 15 Nov:** `tools/build_coaching_tri.py`, `tools/build_coaching_group.py`, pushed with the same builder. Both checked at 390/820/1440 with the live contact form and the cookie banner.
  - **Tri Basic:** the live buy link is an expired Shopify checkout that redirects to the shop home, and the shop has no €237 Tri Basic product. The button says "Contact us to sign up" (prefills the form) until Matteo says which product to link.
  - **Tri copy contradictions, kept as live and waiting for Matteo:** "We have 2 coaching packages" (3 are shown); Advanced "5 months subscription" vs "Advanced 6 Months"; Basic "€79/mo" vs €237 one-off.
  - **Group & Club:** live copy and H1 kept, plus the clubs from the testimonials, Club Talks, reviews and an on-page enquiry form. Yoast focus keyphrase "group cycling coaching".
- **Moving topo background (15 Nov):** `shared/parallax/parallax.html` in footer 228, only on redesigned pages (`.cc-page`), same as Tours. It's off with reduced motion.
- **Share image (15 Nov):** `brand-assets/share/cigala-coaching-share.jpg` (1200x630, made from `share-image-template.html`; the filled-in template is `coaching-share.html`), uploaded to Coaching staging (`stg-coaching/share-image.txt`). Matteo sets it as Yoast's site image: Yoast SEO -> Settings -> General -> Site basics -> Site image.
- **Redirects still to add (301 Redirects plugin, no REST API):** `/group-club-packages2/` -> `/group-club-packages/` and `/dummy-page/` -> `/`. Matteo adds them in wp-admin, or they're done at go-live.
- **Terms & Privacy (15 Nov, Matteo's decision via the main chat):** `tools/build_coaching_legal.py`, in the cigalacycling.com Terms style (sidebar "On this page" + numbered sections).
  - Terms (564): live copy, H1 and H2s.
  - Privacy Policy is a **new page**, https://staging.coaching.cigalacycling.com/privacy-policy/ (ID in `stg-coaching/page-privacy-id.txt`), text in `coaching/privacy.txt`. It is a **draft for Matteo to check**: health data, retention periods and the list of providers (Calendly, Shopify, GoCardless, Vekta, TrainingPeaks, Skool, Shapo, nutritionist/mental coach). Yoast title is the default; the page is in the page sitemap.
  - The footer has Terms, Privacy Policy and Cookie settings; the cookie banner links to /privacy-policy/.

## Tours schema (WPCode Header), 15 Nov
- Matteo replaced the Organization + 6 Review block with `tours/wpcode-schema-without-reviews.html`: Organization with legalName and vatID, no self-serving reviews. Checked on / and /trips/: Organization, WebSite and Service; all JSON valid; no Review left; consent default still comes before gtag.js.
- Optional, still to decide with Matteo: the Service catalogue lists 12 of 15 tours (no Maratona, Coast to Coast, Lake Como, Road page), and 3 URLs lack the trailing slash (dolomites, lake-garda-and-stelvio, lake-garda-gravel). Those URLs redirect, so they work.
- **Schema moved out of WPCode (15 Nov):** Organization, WebSite and Service (every tour, from `tours/trips-2027.json`) now come from Elementor custom code **snippet 9352** (head), made by `python3 -I tools/tours_schema.py`. Re-run it when tours are added, removed or renamed.
  - The WPCode Header box should contain only `tours/wpcode-header.html`: the consent default line plus the Google tag.

