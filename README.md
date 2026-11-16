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
- **Share image (15 Nov):** `brand-assets/share/cigala-cycling-tours-share.jpg` (1200x630), made from `share-image-template.html`; the filled-in template is `tours-share.html`. It uses the Cyprus homepage hero photo.
  - Uploaded to Tours staging as media **9364** with alt text, by `tools/tours_share_image.py`.
  - JPG on purpose, because some apps don't show WebP link previews.
  - **Done (15 Nov):** Matteo set it as the Rank Math default: Rank Math SEO -> Titles & Meta -> Global Meta -> OpenGraph Thumbnail.
  - Home 5212, Contact 461, Destinations 10 and Terms 564 had a logo as their own share image (their featured image, or Destinations' own Rank Math social image). They now share the new image too:
    - set with `/rankmath/v1/updateMeta`, sending only `rank_math_facebook_image` and `rank_math_facebook_image_id`;
    - checked afterwards: title, description, OG title/description, robots and schema are unchanged.
  - Every other page shares its own photo, which is kept on purpose (the trip and destination pages, the list pages, About, Guides, Testimonials).
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
- **15 Nov, Matteo's review:**
  - Homepage review cards show 5 gold stars again, like Coaching.
  - On the tour list cards, the "Event entry guaranteed" / "Event day fully supported" badge now sits on the photo (bottom left), so every title in a row starts at the same height.
  - The red date chip is bigger (13px).
  - Checked on staging at 390/820/1440: no sideways scroll, one H1, titles aligned.
- **Contact forms like Coaching (15 Nov, Matteo: all sites the same):** the forms on Contact 461 and Custom tours 1576 are patched in place by `tools/tours_forms.py`.
  - The script adds the class `cc-form`; `build_tours_wp.py` copies the `.cc-form` CSS from `tools/build_coaching_wp.py` into the kit.
  - Fields: no visible labels, every field required, placeholders "Name *", "Email *", "Phone (with country code) *", "Your Message *". Phone is a text field, so +353 and spaces are accepted.
  - Style: 16px text, 8px corners, green focus outline, green "Send >" button.
  - Contact gained the phone field. Custom tours keeps its phone field id (now text instead of number).
  - Emails go to **tours@cigalacycling.com** (Matteo 15 Nov; the per-site inboxes are in `shared/BUSINESS.md`). Subjects: "New message from the Tours website" (Contact) and "New custom tour enquiry from the Tours website" (Custom tours). Content: [all-fields].
  - Before-change backups: `stg-tours/backup/page-461-before-form.json`, `page-1576-before-form.json`.
  - When these pages get the new design, keep the same form widget.
- **Terms (564) and Privacy Policy (new, 9347, /privacy-policy/), 15 Nov:** built in the cigalacycling.com Terms style by `tools/build_tours_legal.py`, pushed with `push_tours_list.py terms` and `push_tours_list.py privacy-policy`.
  - The terms text is the live page word for word, with the same H1, and title, meta, robots, OG and schema are unchanged.
  - The privacy text is in `tours/privacy.txt`: Tours' own processors (WeTravel, tour partners, event organisers, Hostinger, Google, Meta, OpenWidget), with no tracking IDs. **Matteo to review it** (ideally his accountant or solicitor too).
  - The Rank Math title and meta for the privacy page are set.
  - The footer legal row reads Refund/cancellation policy & terms · Privacy policy · Cookie settings. The shared banner (no vendor names) links to /privacy-policy/.
- **All the other Tours pages, rebuilt on staging (15 Nov):**
  - **Source of the words:** each page's ORIGINAL Elementor data (`stg-tours/backup/page-<id>.json`), never the current staging page. The builders keep the H1/H2 wording and level, body copy, links and image alt text.
  - `tools/build_tours_pages.py`: About 271, Contact 461 (live form kept), Destinations 10, the 26 destination pages (ids in `stg-tours/destination-ids.json`), Testimonials 2844 and Custom tours 1576 (live form kept).
  - `tools/build_tours_trips.py`: the 15 trip pages (ids in `stg-tours/trip-ids.json`), in the trip design `trip/pub/index.html`. It covers the price box with the live WeTravel links, the key numbers, route map, day by day, what's included, gallery, hotels, bike rental, guides, FAQ, reviews and the closing booking band.
  - `tools/build_tours_guides.py`: single post template 5104 (all 37 guides), guide card 5087 and the Guides page 5030 (live loop grid, so new guides appear by themselves).
  - Push: `python3 -I tools/push_tours_list.py <name>` (about, contact, destinations, dest-<slug>, testimonials, private-trips, trip-<slug>); `python3 -I tools/build_tours_guides.py --push`. Then `build_tours_wp.py` + `push_tours_wp.py lib-6` for the CSS.
  - Images: `tools/tours_img.py` makes WebP q90 from the largest staging original on demand, with the library alt (records in `stg-tours/media-webp.json`).
  - Checks: `python3 -I tools/seo_check_tours.py <paths>` (title, meta, robots, canonical, OG, H1/H2 against the live baseline) and `node tools/layout_check_tours.js <paths> [--shots dir]` (390/820/1440, no sideways scroll, one H1, 16px fields, alt on every image).
  - Intended SEO changes:
    - Repeated link-only headings became buttons or links: "View Destination→" ×30 on Destinations, "View/Enquire Tour →" on the destination pages, "BOOK NOW", the "20+/500+/5★/10" stats, and the countries under each testimonial video.
    - "Official event partner" became "Event day support" (Matteo).
    - "SWIZERLAND" became "Switzerland"; the "REASTURANTS" and "ACTIVITES" typos are fixed.
    - The Belgium card links to the Flanders tour (live /destinations/belgium/ is a 404).
    - Testimonials gains an H1 (live had none); the Guides cards use H3, so the page has one H1.
    - Body text that live had in H4 headings is now paragraphs, with the same words.
  - **Newsletter (15 Nov):** footer band plus pop-up, the shared `wp/nl-band.html` and `wp/nl-popup.html`, posting to Matteo's Brevo form on the "tours.cigalacycling.com" list (`TOURS_NL_URL` in `build_tours_wp.py`).
  - CORS checked for staging and live.
  - Tested with the request mocked, so no contact was added: the footer sign-up works, and the pop-up opens after the cookie choice at 390 and 1440.
  - Tours CSS keeps the band title in Anton and puts the pop-up above the chat widget.
- **Matteo's review round, 15 Nov (all done on staging):**
  - **Route maps in the Cigala style for all 15 trips:** `tools/tours_route_maps.py` writes `tourspages/maps/<slug>.svg`, which `build_tours_trips.py` inlines in the Route section.
    - Each map has dark land, real lakes and rivers (Natural Earth), the green route through the overnight stops (red numbers), the hotel base (white) and climbs/places (gold triangles).
    - Coordinates are approximate and typed in `ROUTES`: check them on review.
  - **Trip pages:**
    - The poster image next to the intro shows in full (not cropped).
    - Hotels are in the Dolomites card style everywhere (the Algarve heading "ACCOMODATION VILAR DO GOLF****" is split into the section title and the hotel card).
    - "Read the guide" buttons are green; the bottom "Book now" is normal size.
    - The price box has more space under GBP/USD, a "contact us" link, and the short group size.
  - **Spots left:** `tours/spots.json`, shown in the price box with the pulsing red dot from `shared/dot`. Algarve "More than 5", Chianti 3, Flanders "More than 5"; the other tours wait for Matteo's numbers.
  - **Newsletter (Tours wording):** "Tour news / Ride with us in 2027 / New tour dates, early-bird offers, route guides and news from our bike tours across Europe." The gap to the footer is now 32px.
  - **Custom tours:**
    - New hero photo (the Colosseum is gone).
    - Icons for "What we organise".
    - Location ideas on a Europe map (`tourspages/maps/custom-locations.svg`), with numbered dots matching a numbered list. Patagonia is left out.
- **Finishing touches (15 Nov):**
  - Link check: 56 rebuilt pages, 84 internal links, none broken.
  - 404 page (template 7275) is in the new design with the live wording ("404 — Wrong turn"), via `tools/tours_404.py`. It returns a real 404 status.
  - Every trip page has `TouristTrip` structured data: name, description, photo, route places and the euro price with the WeTravel link, provider = the site's Organization (`build_tours_trips.py`). Existing schema (Organization, WebSite, Service) is unchanged.
- **Matteo's review round, 16 Nov (all done on staging):**
  - **Destination pages:**
    - Every gallery fills complete rows of 3 (`gallery_extras` in `build_tours_pages.py` adds matching photos from the media library).
    - "Enquire" cards always go to Custom tours: the live Portugal Madeira card linked to Cyprus.
    - The Tuscany upcoming cards link to the tours their titles name (`FIX_CARD_URL`): live linked them to Lake Garda.
    - Every hero is the same height (640px laptop, 600px phone), with more space around the maps.
    - The France map outline is smoothed (the Gironde estuary drew as spikes).
  - **Tour lists:** a level filter (Beginner / Intermediate / Expert, same logic as the homepage finder), and a 3-bar level meter next to the level text on the cards.
  - **Trip pages:**
    - Green dates.
    - New price box with full lines.
    - A 4-cell strip with icons.
    - Trip at a glance with icons and a green title; airport transfers have their own rows (live times like "12:00" were being split).
    - "What's not included" is on all 15 trips (Strade Bianche had it as an H4), plus the airport transfers and the Gran Fondo entry prices box.
    - Galleries and hotel photos fill complete rows.
    - A single hotel shows its photo and text side by side.
    - The homepage stats block.
    - Three guides sit in 3 columns.
    - The section bar's Book now shows only after the price box scrolls away.
    - The final band has a pulsing "Only N spots left" when spots are 5 or fewer.
  - **Posters with our map badge:** `tools/tours_posters.py` paints our badge (`tourspages/maps/badge-<slug>.svg`, areas in `POSTER_BADGES` in `tours_route_maps.py`) over the live poster's badge and uploads `poster-<slug>` WebPs.
  - **Day-by-day route maps (Matteo approved brouter.de):** `tools/tours_day_routes.py` routes every riding day on real roads with BRouter (OpenStreetMap; road profile for road tours, gravel profile for gravel tours).
    - Waypoints come from each day's text (`DAYS`, coordinates in `G`). Tracks are cached in `tours/routes/<slug>.json`, so maps rebuild offline.
    - Output: `tourspages/maps/day-<slug>.svg`, in the country-map style (Matteo 16 Nov): the tour's country in green with a green outline, neighbours dark, days in a family of greens with a soft glow, numbered badges, hotels/overnight towns in white, named climbs. The frame height follows the route's shape.
    - Lake Garda and Lake Como are drawn from their shore roads: Natural Earth's outlines were too coarse at this zoom.
    - Under the map, the trip page lists the days (colour, title, distance from the itinerary). Hover or tap highlights that day's route.
    - The old overview maps (`<slug>.svg`) stay as the fallback.
    - Router distances differ a little from the itinerary in places (e.g. the French Alps loops). The list shows Matteo's itinerary numbers.
  - **Hero tags:** the country by name (Matteo did not want a flag there; the flags stay on the tour cards), and the level has the 3-bar meter. Trip at a glance icons sit centred beside their titles.
  - **What's included:** Included and Not included side by side. The airport transfers are a full-width band of date cards, and the Gran Fondo entry prices are tiles.
- **Phone review, 16 Nov:**
  - **Availability:** a word and a pulsing dot instead of numbers, the same on every tour (`tours/spots.json`): red "Last few spots" (Strade Bianche), amber "Filling up fast" (Algarve), green "Spots available" (the rest, `_default`). Shown in the price box and in the bottom "Ready to ride" band.
  - **Phone hero:** on phones the trip photo is a clear band at the top (440px, focus point per trip in `HERO_MPOS`), with the title and price box below it. The breadcrumb sits in a dark pill. On laptops the focus point is in `HERO_DPOS` (Flanders: the riders).
  - **Algarve hero:** media 710 (rider in Cigala kit above the beach, `HERO_PHOTO`). On laptops the price box covers the rider.
  - **Availability on cards:** home, tour lists and destination cards show the red "Last few spots" and amber "Filling up fast" pills with the pulse (`avail()` in `build_tours_home.py` and `build_tours_list.py`, same `tours/spots.json`). Green stays on the trip pages only.
  - **Cyprus video:** "Watch the trip" section after the intro, plus a "Watch the video" button in the hero (`TRIP_VIDEO`). Our own cover photo (media 3353); YouTube (no-cookie) loads only when the visitor taps play. Add more tours to `TRIP_VIDEO` as videos come.
  - **Flanders:** "Hotel T" main card (`HOTEL_FALLBACK`: live has no hotel heading) and 8 photos below. Star rating to add when Matteo confirms it.
  - **Text:** no space before a comma, site-wide (`TYPOS`): "RIDE INTO THE LEGEND, TAKE PART…".
  - **Maps:**
    - Strade Bianche day 3 is a loop back to Radda (Castellina, Panzano, Greve, Lamole, Volpaia).
    - Algarve day 4 is the Gran Fondo to Lagos via Monchique (approximate, until Matteo sends the Komoot GPX).
    - Rivers are off the day maps.
- **Dynamic pages and more fixes, 16 Nov:**
  - **Every trip page** (`DYN` in `build_tours_trips.py`):
    - the numbers count up;
    - the poster's map badge draws itself on a tile-only poster (`tours_posters.py --base` → `posterbase-<slug>`);
    - the route map draws day by day;
    - the day cards slide in.
    - All of it only runs when JS is on and the visitor hasn't asked for reduced motion.
  - **Exit pop-up** on every trip page and on Custom tours (`exit_pop()` in `build_tours_pages.py`):
    - wording per tour, with WhatsApp and contact buttons;
    - once per visit, never before the cookie choice;
    - skipped when the newsletter pop-up is open or was closed in the last hour;
    - snoozed 3 days after closing.
  - **Custom tours location map:** the dots pop in one by one, and the list and the dots highlight each other.
  - **About:** Matteo's cut-out photo with the signature; the signature writes itself on About and the homepage; team cards lift with a green outline on hover.
  - **Homepage:** section titles and tour cards rise in as you scroll (`HOME_DYN` in `build_tours_wp.py`).
  - **Spacing:** one gap under the hero on every page (44px). The day timeline line no longer runs into the circles. The Contact social icons start under the text column.
  - **Guides on tours:** per-tour line-ups in `GUIDES_SET`, `GUIDES_ADD` and `GUIDES_SWAP`; team members' photos and roles in `TEAM`. Still to come:
    - **Alessio "Bone"** (Support & Mechanic, photo `tours/team/alessio-bone.jpg`, media 10683): done on 16 Nov. He is on About, Maratona and Dolomites, and on Slovenia and French Alps in place of Amedeo.
    - **Coast to Coast:** Matteo, Antonio and Marco (the younger support & mechanic, not Marco "DS"); no Amedeo. Marine (operations & bookings) is on no tour, only on About (`GUIDES_DROP`). Giampietro is "JP" everywhere. About first row: Matteo, Amedeo, Marine, Piero, Alessio, Antonio, JP. Hotel T is 4 stars.
    - **Komoot GPX:** Matteo decided to go live with the current routed maps (16 Nov).
  - **Photos:** heroes in `HERO_PHOTO`, with focus points in `HERO_DPOS` and `HERO_MPOS`. Italian Alps cards use the Stelvio photo. The Garda & Stelvio gallery is rebuilt from sharper photos (`GALLERY_PHOTOS`).
  - **Maps:**
    - The Garda & Stelvio day 3 sits in a corner inset.
    - Short out-and-back spikes are removed (`despike`).
    - Tuscany Epic day 3 leaves Peccioli to the east.
    - Lake Como day 5 is the Gran Fondo from Bergamo (approximate until the GPX).
- **Live errors fixed (Matteo 15 Nov: "any error you see, fix it"):**
  - The Gran Canaria H1 now reads "Cycling in Gran Canaria" (live: "Cycling in Mallorca").
  - In the Lake Como guide (post 8945), the second FAQ question is now "How hard is the Muro di Sormano?". Backup: `stg-tours/backup/post-8945-before-faq-fix.json`.
  - The stray "harmony." line in the Dolomites intro is gone.
  - Spelling is fixed through `fix_text()` in `build_tours_pages.py`, on visible text and alt text only, applied to every rebuilt page and trip. Examples: Mechanical, Dura-Ace, Accommodation, Coffee, Alentejo, Morocco, recipes, cuisine, Trentino, luggage, San Gimignano, Nova Gorica, Barcelonnette, Grosseto, peninsula, countryside, Col du Télégraphe, Crostini. The Terms text is untouched (kept word for word).
  - One meta description per page: the Hello theme's own description tag is off (`hello_elementor_settings_description_meta_tag` = true), so only Rank Math's remains.

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
- **All Coaching pages are now on staging in the new design (15 Nov):** besides the pages above, About 2109, Triathlon About 3770, Vision 3272, Testing 3865, Nutrition 3995, Bike Fit 4256, Book 1-on-1 3750, Talent 896, Club Talks 4395, Contact 461, Testimonials 2844, Blog 4354 (keeps the live loop grid, template 4718 restyled, titles H3) and the four country pages (6098, 6100, 6102, 6106). Built by `tools/build_coaching_generic.py` (live text -> sections; Italia),
  `build_coaching_country.py` (UK/USA/Canada: own copy per country, real testimonials, local currency; SEO-DECISIONS.md section 10), `build_coaching_testimonials.py`, `build_coaching_blog.py`; single posts (template 4028) restyled by CSS in `build_coaching_wp.py`. Menu: Results ▾ (Testimonials, Case Studies). Open points: SEO-DECISIONS.md section 9.
- **Case Studies (new page /case-studies/, Matteo 15 Nov):** built by `tools/build_coaching_cases.py` from `CASES` in `tools/coaching_common.py`; a scrolling section on Individual Packages. Order: Marine, Tilen, Marco, Eoin, Vittorio, David, then Shane, Bernd, Rob, Derek. Tilen, Marco, Eoin, Vittorio and David come from Matteo's Canva case study posts (Vekta data); the post tracker says each still **needs the athlete's OK**: don't take them live without it. Athlete photos Matteo sent: `coaching/athletes/` (gently sharpened WebP). Eoin's photo still to come (his card shows his number instead).
- **Free Tools (new pages, Matteo 15 Nov):** https://staging.coaching.cigalacycling.com/tools/ (hub) with `/tools/training-zones-calculator/`, `/tools/carbs-per-hour-calculator/`, `/tools/critical-power-calculator/`, `/tools/sweat-rate-calculator/`, `/tools/swim-pace-calculator/` (CSS), `/tools/climb-time-calculator/` (standard cycling power equation: gravity, rolling resistance Crr 0.004, CdA 0.40 on the hoods, 2.5% drivetrain loss, air density from altitude; famous climbs use their published average gradient). Built by `tools/build_coaching_tools.py`; calculated in the browser, nothing stored. New pages are created by the push (`page-new-*`, IDs in `stg-coaching/new-pages.json`); Yoast title/meta/focus keyphrase by `tools/yoast_coaching_new_pages.py`. Linked from the Services menu and the footer (a top-level menu item wrapped the menu at 1440). Not live yet: go live with the rest.
  - Newsletter: Matteo wants a separate Brevo list per site. Brevo has no Coaching list yet (15 Nov: only cigalacycling.com, Subscribers, Shopify lists). When Matteo sends the Brevo form URL for a new Coaching list, set `NL_URL` in `tools/build_coaching_tools.py` and rebuild: the sign-up box (email + required consent tick) appears under every tool.
  - How: `python3 -I tools/coaching_media.py` (WebP images -> staging media, `stg-coaching/media-webp.json`), `python3 -I tools/build_coaching_wp.py` (payloads -> `stg-coaching/out/`), `python3 -I tools/push_coaching_wp.py lib-6 lib-170 lib-228 page-2924 page-3338 snippet-head` (staging only, clears the Elementor cache).
  - Packages keeps the live Elementor contact form (to info@cigalacycling.com, styled in the brand, 16px fields) and the Shapo testimonials widget.
  - Cookie banner: the shared one (`shared/consent/`), GA4 G-E1WWZCLBRB + Meta Pixel 1986332861692106 + OpenWidget, in footer 228 with a "Cookie settings" link. The old "Got it!" bar and old chat widget are gone. Head snippet = Elementor custom code (ID in `stg-coaching/snippet-head-id.txt`). Tested: nothing before a choice; Accept loads the Pixel; Reject loads nothing.
  - WPCode Header (Matteo, 15 Nov): consent default line pasted first, before gtag.js (checked: dataLayer = consent default denied -> js -> config; Accept -> update granted). The hreflang block is fixed too (see `coaching/SEO-DECISIONS.md`).
  - Checked at 390/820/1440: no sideways scroll, one H1, alt on every image.
- **Triathlon packages (3795) and Group & Club (3738), 15 Nov:** `tools/build_coaching_tri.py`, `tools/build_coaching_group.py`, pushed with the same builder. Both checked at 390/820/1440 with the live contact form and the cookie banner.
  - **Tri Basic:** the live buy link is an expired Shopify checkout that redirects to the shop home, and the shop has no €237 Tri Basic product. The button says "Contact us to sign up" (prefills the form) until Matteo says which product to link.
  - **Tri copy contradictions, kept as live and waiting for Matteo:** "We have 2 coaching packages" (3 are shown); Advanced "5 months subscription" vs "Advanced 6 Months"; Basic "€79/mo" vs €237 one-off.
  - **Group & Club:** live copy and H1 kept, plus the clubs from the testimonials, Club Talks, reviews and an on-page enquiry form. Yoast focus keyphrase "group cycling coaching".
- **Logo (15 Nov):** Matteo's file `coaching/brand/ccCoachingLogo-matteo-2026-11-15.png` is used in the header, footer and share image (share image re-uploaded with the new logo, see `stg-coaching/share-image.txt`).
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


## Coaching athlete area (16 Nov 2026, staging)
- One login per coached athlete at `/athletes/` (footer link "Athlete login"). noindex, not in the sitemap, never cached.
- Code: `coaching/athlete-area/athlete-area.php`, pushed as Code Snippets snippet 8 by `python3 -I tools/coaching_athlete_area.py`. **Code Snippets must stay active** (it was off before; snippets 5–7 stay off).
- Matteo's steps:
  - **New athlete:** Users > Add New, role Subscriber. Their page is created automatically under "Athletes".
  - **Reports:** upload the PDF inside the athlete's page. It goes to `uploads/cc-private/`, which can't be opened directly (403), and opens only for that athlete or Matteo.
  - **Shared hub:** "Shared hub (all athletes)", page 7365.
  - **Athlete finishes:** delete the user. The login stops at once and the page stays as "Former athlete: …".
- Logged-in athletes: the free tools open without the newsletter step on any device, and the newsletter and exit pop-ups stay away. Matteo logged in still sees the site as a visitor.
- Tested 16 Nov on staging: login and wrong password, 1-year login cookie, file open/refused/direct-download blocked, a deleted athlete can't log in, wp-admin redirects athletes. 390/820/1440 widths, 16px fields, one H1. Test users removed.
- After go-live: open /athletes/ logged out on live and check that LiteSpeed doesn't cache it, and that `/wp-content/uploads/cc-private/` answers 403.

### Athlete area: reports from Matteo's PC tools (planned, after launch, Matteo 16 Nov)
- **Plan:** the PC tools (Vekta: progress report, race day simulator, assessment, reviews) deliver each athlete's page to their area, matched by email, instead of public Netlify or claude.ai links.
- **Rule (Matteo):** only motivating, athlete-friendly content. That means progress and highlights, race plans, the first assessment framed as a starting point, milestones.
- **Never shown to athletes:** the Weekly Athlete Plan (Matteo: "for sure"), Early Warning flags, fatigue or risk alerts, missed-session or compliance counts, comment drafts, Command Centre, comparisons with other athletes.
- **Every delivered report arrives as a draft only Matteo sees.** He previews and publishes it (he can edit or skip it). Nothing reaches an athlete automatically.
- **Report wording:** lead with positives and numbers, no "you missed" or "you're behind".
- **Notifications (Matteo 16 Nov, "perfect"):**
  - On Publish, a branded email "your new report is ready" goes out with a button to /athletes/. Matteo can untick it per report; nothing is emailed without his Publish.
  - In the hub: a "New" badge on the card and "You have N new reports" at the top, both cleared once opened.
  - Optional: a note in the athlete's Vekta calendar (the report session already does this); the hub as a home-screen app.
- **New tools:** any future tool from the Vekta sessions can deliver to the athlete area with a label and icon (generic upload with a `type`), under the same draft, motivating-only and notify rules.
- **Build:**
  - Website: a secure upload endpoint (application password on Matteo's PC only), draft/publish, report cards with a "new" badge, HTML reports served sandboxed.
  - PC side: one helper script the tools call at the end.

### Athlete area: availability (planned, after launch, Matteo 16 Nov)
- **"My availability" card in each athlete's area:**
  - **Usual week:** per day, the time available (rest day, 1h, 1.5h, 2h, 3h+) and when (morning, lunch, evening). It repeats every week.
  - **Changes:** dated exceptions ("12–19 Dec away", "next week 4h total"), plus a free note. Expired changes drop off by themselves.
- **When an athlete saves:** Matteo gets an email every time, plus an optional phone push (ntfy app on a private topic, or Telegram, his choice).
- **Coach page:** all athletes' availability on one screen, with a "changed since you last looked" badge.
- **Voice (Matteo 16 Nov):** a microphone button in the availability box (browser recording, iPhone and Android, no app).
  - Speech is written into the box as text while they speak (browser speech recognition), so the athlete can correct it before saving.
  - The audio is kept privately (cc-private, like the reports) for Matteo to listen to. His notification has the text and a "listen" link.
- **Vekta calendar (Matteo 16 Nov, wanted):** every saved change is also written to the athlete's Vekta calendar as notes on those days.
  - Preferred: from the website, so it works with the PC off. That needs Matteo's Vekta key in the server config, never in chat.
  - Alternative: the PC session syncs while the PC is on.
- **Notifications:** email is fine for Matteo; a phone push app is not needed for now.
- **Read access:** the PC availability session (mdv workspace) can read it through the same secure API as the report delivery.
- Each athlete sees only their own. 16px fields.
- **Built locally 16 Nov (not on any site yet; waiting for Matteo's go after the Coaching launch):**
  - Code: `coaching/athlete-area/availability.php`. Hooks into `athlete-area.php` through four filters (`cc_ath_nav`, `cc_ath_after_reports`, `cc_ath_coach_links`, `cc_ath_board`), which do nothing without it. Pushed only with `python3 -I tools/coaching_athlete_area.py --availability` (staging first).
  - Data: post meta `cc_avail` (JSON) on the athlete's page. Voice recordings go to `uploads/cc-private`, attached to that page, so the existing file check serves them only to the athlete and Matteo. Coach board: `/athletes/?board=availability`. Read API for the PC tools: `GET /wp-json/cc/v1/availability[?email=]` (application password).
  - Email to `info@cigalacycling.com` (or `CC_AVAIL_NOTIFY` in wp-config) on every save, with Reply-To set to the athlete.
  - Vekta: notes worked out per day (each day of a dated change, max 31; a new usual week as one note on the next Monday). Nothing is sent until the call is confirmed against the API the PC tools use and Matteo puts `CC_VEKTA_API_URL`/`CC_VEKTA_API_KEY` in wp-config.php himself.
  - Tests: `php tools/test_availability.php`. Mock-up: `php tools/mock_availability.php > coaching/athlete-area/mockup/parts.json && python3 -I tools/build_availability_mockup.py` (checked at 390/820/1440, 16px fields, mic and save simulated).
  - Open: Vekta key location and calendar item type; whether the privacy policy draft should mention voice notes.
