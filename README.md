# Cigala Cycling websites

This repository holds the redesign of the Cigala Cycling sites in the Cigala Cycling brand:

1. cigalacycling.com: built on staging, waiting to go live
2. tours.cigalacycling.com: designs done, fresh SEO baseline taken 15 Nov; waiting for Matteo to create the Hostinger staging copy
3. coaching.cigalacycling.com: not started
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
| `wp/consent-banner.html` | Cookie banner. It gates Google Analytics G-955J6LHQ2P and Meta Pixel 1986332861692106. The chat button works before consent. |
| `wp/nl-band.html`, `wp/nl-popup.html` | Newsletter signup in the footer and as a pop-up. It posts to the Brevo form, which saves to the "cigalacycling.com" list. |
| `stg/backup/` | Original staging pages and templates, taken before the redesign (to restore from) |
| `stg/media.json`, `stg/media-webp.json` | Staging media IDs and URLs. The WebP set is the one in use. |
| `webp/` | WebP images (quality 90, from the largest originals) |
| `baseline.json` | SEO crawl of the live cigalacycling.com before the redesign |
| `crawl-staging-now.json`, `audit/` | Latest staging crawl and the tracking/image audit |
| `tools/build_tours.py`, `tourspages/`, `tp/`, `tp2/` | **tours.cigalacycling.com**: the 7 page designs and the extracted live content |
| `survey/NfmCmGsjq4LL9bTAi38NXN/` | Tours homepage design |
| `trip/` | Tours trip-page design (Dolomites: 323 km, 8,800 m) |
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
for id in 10 271 461 564; do curl -X POST $B/wp/v2/pages/$id -H 'Content-Type: application/json' --data-binary @wp/out/page-$id.json; done
curl -X DELETE $B/elementor/v1/cache
```

Page IDs:

| ID | Page |
|---|---|
| 10 | Home |
| 271 | About |
| 461 | Contact |
| 564 | Terms & Conditions |

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

- Hostinger created the staging copy as a separate WordPress install in the `/staging` folder of tours.cigalacycling.com. `https://tours.cigalacycling.com/staging/wp-login.php` answers, and its login form posts to `https://staging.tours.cigalacycling.com`.
- `staging.tours.cigalacycling.com` doesn't resolve to a server yet: the proxy can't connect, while `staging.cigalacycling.com` works. A DNS record for `staging.tours` is needed, pointing to the same server as `tours.cigalacycling.com`.
- No application password is saved for the Tours staging host yet. It must be created in the **staging** wp-admin, never on live.

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
  - If only one choice matches an existing category page, the button goes there: Italy goes to `/italian-trips/`, Gravel to `/trips/gravel-trips/`, Gran Fondo to `/trips/granfondo-trips/`, Road to `/trips/road-trips/`.
  - Otherwise it goes to `/trips/?type=…&country=…&level=…`, which filters the cards in the browser. The full list stays in the HTML, and the canonical stays `/trips/`, so there's no duplicate content.
  - **Month** dropdown (Feb–Oct 2027): the dates are in `tours/trips-2027.json`, read from the card images on the live `/trips/` page. On live they only exist inside the images. On the new cards they'll also be real text, which Google can read.
  - At 390px the bar stacks vertically. Selects use 16px text so iPhones don't zoom in.

