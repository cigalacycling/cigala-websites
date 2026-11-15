# coaching.cigalacycling.com: approved SEO fixes

Matteo approved these on 15 Nov 2026 ("do all 3", and for the duplicate/thin pages "you choose").
Apply them **on the coaching staging site only**, during the build. Never edit the live site.
Everything not listed here stays exactly as in `coaching/baseline.json`: URLs, Yoast titles and metas, H1/H2 wording, body copy, existing alt text, structured data.

After the build, crawl staging and compare with `baseline.json`. The only differences allowed are the ones below.

## 1. Typos (title / H1 only)

| URL | Field | Live | New |
|---|---|---|---|
| `/cycling-coach-canada/` | Yoast title | Cycling Coach **Canda** \| Online Cycling Coaching by Matteo Cigala | Cycling Coach **Canada** \| Online Cycling Coaching by Matteo Cigala |
| `/blog/training-fasted-at-high-intensity-or-low-intensity/` | H1 | Training fasted at high or low **instensity**? | Training fasted at high or low **intensity**? |
| `/blog/10-habits-to-make-you-a-better-cyclist/` | Yoast title | 10 Habits to make you a better **cyclists** \| Cigala Cycling Coaching | 10 Habits to make you a better **cyclist** \| Cigala Cycling Coaching |
| `/blog/slower-in-winter-is-not-your-legs/` | Yoast title | Slower In Winter? **Is Not** Your Legs. By Coach Matteo Cigala | Slower In Winter? **It's Not** Your Legs. By Coach Matteo Cigala |

## 2. One H1 per page

Add an H1 where there is none:

| URL | New H1 | Why this wording |
|---|---|---|
| `/individual-packages/` | Individual Cycling Coaching Packages | The page has no headline at all. This matches its Yoast title. |
| `/tri-individual-packages/` | TRIATHLON INDIVIDUAL PACKAGES | This is already the page's top line (a paragraph). It becomes the H1 with the same wording. |

Demote the extra H1s to H2s, keeping the wording. This changes the tag only:

| URL | Keeps as H1 | Becomes H2 |
|---|---|---|
| `/blog/` | STAY UP TO DATE WITH OUR LATEST BLOG POSTS | the 10 post-card titles |
| `/nutrition/` | PERSONALIZED NUTRITIONAL PLAN FOR YOU TO IGNITE YOUR POTENTIAL | the 6 post-card titles |
| `/cycling-coach-uk/`, `-usa/`, `-canada/` | CYCLING COACH UK / USA / CANADA | #TrainSmarterRideFaster, START WORKING WITH MATTEO |
| `/preparatore-di-ciclismo-italia/` | PREPARATORE DI CICLISMO ITALIA | ALLENATI CON METODO, VAI PIU' FORTE · VUOI FARE IL SALTO DI QUALITÀ? · INIZIA A COLLABORARE CON MATTEO |

The blog post-card titles become H2s wherever the blog-card widget is used, on any page.

## 3. Duplicate and thin pages (Claude's choice, delegated by Matteo)

| URL | Decision | Reason |
|---|---|---|
| `/dummy-page/` | **Delete, then 301 to `/`.** It leaves the sitemap. | The page is empty: no H1, no meta and no copy, and nothing links to it. A noindex would still leave an empty public page. A 301 keeps any stray link working. |
| `/group-club-packages2/` | **301 to `/group-club-packages/`.** It leaves the sitemap. Point the Triathlon menu's "Group Club Packages" item straight to `/group-club-packages/`. | The page is a byte-for-byte copy of `/group-club-packages/`, minus the meta description. Two indexed copies compete with each other. The redirect merges them into one URL. |
| `/about2/` | **Keep it indexed and unchanged.** | It's the real Triathlon "About" page: its own copy, its own title ("Triathlon Coaching …") and its own meta, and it's linked from the Triathlon menu. Only the slug is ugly, and changing a URL is off-limits. |

No page gets a plain noindex. Redirecting the two empty or duplicate pages is better for SEO than noindexing them.

## 4. Missing alt text (add; existing alt text stays)

| Image (uploads/…) | Used on | New alt |
|---|---|---|
| 2026/06/pzrIm4dp…vws1600.jpg | /blog/understanding-your-body/ | Four race leaders' jerseys on the podium spraying champagne \| Cigala Cycling Coaching |
| 2026/06/imgi_15_H9OhSBW…s999.jpg | /blog/10-habits-to-make-you-a-better-cyclist/ | Cyclist in Cigala Cycling kit climbing a narrow mountain road \| Cigala Cycling Coaching |
| 2026/06/gallery-1.png | /blog/how-to-improve-on-descents/ | Cyclist celebrating with arms wide at a Gran Fondo finish \| Cigala Cycling Coaching |
| 2026/06/IMG_5144.jpg | /blog/what-is-ftp-cycling/ | Young rider signing a yellow jersey for a fan after a race \| Cigala Cycling Coaching |
| 2026/08/266728937_…_n.jpg | /blog/, /nutrition/, /blog/preparazione-gran-fondo-strade-bianche/ | Cigala Cycling rider winning a race with arms raised in front of the crowd \| Cigala Cycling Coaching |
| 2026/08/1730751-scaled.jpg | /blog/preparazione-maratona-dles-dolomites/ | Group of cyclists riding a mountain pass in the Dolomites \| Cigala Cycling Coaching |
| 2026/10/01265307-scaled.jpg | /blog/off-season-transition/ | Smiling cyclist in Cigala Cycling jersey by the lake \| Cigala Cycling Coaching |
| 2026/08/Vekta-x-Cigala-Cycling.png | /blog/, /nutrition/, 3 posts | Vekta training dashboard on a laptop and phone \| Cigala Cycling Coaching |
| 2026/10/download-2026-10-20T183643.559.png | /blog/, /nutrition/, /blog/critical-power-testing/ | Cyclist in European champion's jersey biting a medal \| Cigala Cycling Coaching |
| 2026/08/336532986_…_n.jpg | /blog/critical-power-testing/ | Cyclist in Cigala Cycling kit climbing a hairpin by a stone wall \| Cigala Cycling Coaching |
| 2026/06/IMG_1758-scaled.jpg | /blog/lactate-gels-in-cycling/ | Exhausted cyclist sitting against a wall beside the bike \| Cigala Cycling Coaching |
| 2026/06/unnamed-88.png … unnamed-93.png (5) | /individual-packages/ | Photo of a coached athlete, shown with their testimonial \| Cigala Cycling Coaching |

`2026/06/unnamed-35.png` on `/about/` is a **broken image on live** (the file returns 404, and the image has an empty alt). Leave it out of the staging build.

These alt texts describe the scene and don't name anyone. If Matteo wants riders named (for example, the testimonial photos), swap in the names.

## 5. Found 15 Nov, waiting for Matteo: hreflang tags

Every live coaching page has the same five `<link rel="alternate" hreflang>` tags in the head: en-gb UK page, en-us USA page, en-ca Canada page, it Italia page, and **x-default -> `https://coaching.cigala**cycy**cling.com/cycling-coach-uk/`**, a misspelled domain that doesn't exist.

Proposed fix, on staging only:
- correct the domain;
- point x-default at the homepage;
- only put the tags on the country pages and the homepage, not on every blog post.

They're probably in the WPCode header (not in the Elementor templates). Not changed yet.

### 5a. Matteo's answer (15 Nov) and the fix

- Fix the misspelling: **approved**. Matteo's priority is not to lose the Italia page (`/preparatore-di-ciclismo-italia/`), which brings a lot of traffic from Italy, and to improve the UK, USA and Canada pages.
- The tags sit in the **WPCode Header** box, after the JSON-LD schema, wrapped in a stray `<head>...</head>` pair. WPCode can't be edited over the REST API, so Matteo pastes the fix in wp-admin (staging first): replace those lines, **including the stray `<head>` and `</head>`**, with `coaching/wpcode-hreflang-fix.html`. The schema above them stays exactly as it is.
- Only the domain changes; the tags and their targets are otherwise the same, so the Italia page keeps its signal.
- Why UK/USA/Canada don't rank: they're 81-88% identical to each other (word comparison of the live pages), so Google treats them as duplicates. The Italia page is 80% different (Italian). Fix when those pages are rebuilt: give each one its own content (local events and guides the blog already has, e.g. Fred Whitton / W200 for UK and Ireland, BWR for USA, Gran Fondo Whistler for Canada; local currency; local testimonials), keeping URLs, titles (Canada typo fixed) and H1s.

## 6. Applied on staging, 15 Nov

- Typos (section 1) fixed on Coaching staging:
  - Canada title **and** its Yoast focus keyphrase ("Cycling Coach Canda" -> "Canada"), via `/yoast/v1/bulk_editor/update_search`;
  - "10 Habits ... better cyclist" title;
  - "It's Not Your Legs" title;
  - the fasted-training post title/H1 ("intensity"). The URL is unchanged.
- The Yoast values before these changes are saved in `stg-coaching/yoast-before.json`.
- Footer (Matteo: "less busy"): cigalacycling.com layout. The four international pages keep their footer links and live H2 wording, inside an "International coaching" toggle in the bottom row (still in the HTML, so Google sees and follows them).
- Yoast scores on staging (15 Nov):
  - pages: 4 good, 15 ok, 0 bad, 5 not analysed;
  - posts: 36 good, 15 ok, 0 bad, 2 not analysed.
  
  These are Yoast's own checklist scores, saved when a page is edited in wp-admin. Pushing through the REST API doesn't recalculate them, so they're the scores the live site already had.

- **hreflang fixed on Coaching staging (15 Nov):** Matteo replaced the block in WPCode Header. It's now 5 tags with correct `coaching.cigalacycling.com` URLs, and the stray `<head>`/`</head>` wrapper is gone (checked in the page source). The consent default line isn't in the WPCode Header yet.

## 7. Reviews (Matteo 15 Nov: "do what you suggest")

- No Review/AggregateRating markup on Coaching. Google hasn't shown stars for a business's own reviews on its own site since 2019, so it brings nothing.
- The Shapo widget (JS-loaded, third-party content, empty in our test) is removed from Individual Packages and won't be used in the rebuilt pages.
- Our own review cards, as real page text: 8 athlete quotes chosen from the live Testimonials page, in the athletes' own words, with no star ratings. The source is `REVIEWS` in `tools/coaching_common.py`.
- Every reviews section has a "Read our reviews on Google" link to Matteo's Google Business Profile (https://share.google/lwboSfcuStGhX0c0p).
- The Testimonials page keeps all its written testimonials as text.

## 8. Individual Packages, Matteo's second review (15 Nov 2026)

Approved by Matteo (content changes, not SEO-sensitive: H1/H2s, title and meta unchanged):
- Basic: "Feedback on sessions", "Schedule Adjustment" and "Daily Training Analysis" are not part of Basic; they now show with a red X, together with the things Advanced/Premium add (deep initial assessment, catch up call, race strategy, continuous support, Vekta). Compare table updated to match.
- New line wording: "Deep Initial Assessment of your training data from the past year or 6 months, depending on the data available" (Advanced and Premium).
- Advanced summary: weekly feedback, a monthly catch up call and deep training analysis, plus Vekta.
- Contact form (all Coaching pages): new required Phone field; Name, Email and Message now required too.
- The live icon images on the add-on panels (user / rocket, with alt text) are replaced by inline line icons in the brand style (decorative, aria-hidden).
- Footer tagline (an H2 on every page, live wording "Cycling & Triathlon Coaching - Bike Tours - Retail") changed to "Train Smarter, Ride Faster": Matteo, 15 Nov, since this is the coaching site. Small sitewide H2 change, approved.
- Basic's not-included lines now follow the live page's own included/excluded marks (Feedback on sessions, Schedule Adjustment, Daily Training Analysis, Daily Session Carbs Recommendations, Nutritional Consult); Triathlon Basic likewise (its live list excludes the first three).
- Packages hero photo: Matteo chose the riders by the lake in Wicklow (IMG_3999, 2560 px). Its live alt text had a typo ("Cycling Cycling Coaching group riding in Wicklow, Ireland"), fixed to "Cigala Cycling Coaching ...". The old soft hero photo (imgi_41) is no longer used on this page.

## 9. Remaining pages rebuilt (15 Nov 2026, Matteo: "finish all of the rest of the pages")

Built by `tools/build_coaching_generic.py`, `build_coaching_testimonials.py` and `build_coaching_blog.py`. Every page keeps its live H1 and every live H2 wording (checked by the build), all body copy, and every image with its live alt text. Changes:
- Small black icon images (PNG under 200 px, e.g. numbered circles, user and rocket icons) are left out: they were invisible on the dark design. A few live images that return 404 (e.g. `unnamed-35.png` on /about/) are left out too.
- Blog loop item (template 4718): post titles were H1, giving /blog/ ten H1s. Now H3, so the page has one H1. The "By ..." author H2s stay in the loop template.
- Testimonials: Keith Sharkey's testimonial appears twice on the live page; shown once.
- Menu: "Testimonials" is now a "Results" dropdown with Testimonials and Case Studies (same URLs).
- Single blog posts: the template is restyled with CSS only (dark background, brand fonts); content untouched.

To check with Matteo (copy left exactly as live):
- /testing/ "What we organise": all six steps repeat the same placeholder text ("The Premium package is for those triathletes...").
- /cycling-coach-uk/, -usa/, -canada/: the 5-star quotes credited to "John - England, UK", "Peter - New York, UK", "Peter - British Columbia, Canda" are reworded versions of Derek's testimonial; the planned rewrite with unique content still needs Matteo's approval.
- Crawl of staging (15 Nov, `stg-coaching/crawl-after-2026-11-15.json`, compared by `tools/compare_coaching_crawl.py`): 76 live pages; titles, metas, H1s, H2s, alt texts and schema types match except the approved changes (homepage hidden "IRELAND" H2, two Yoast title typo fixes, icon images left out, the two packages photos Matteo replaced, /dummy-page/ to be redirected). The header logo keeps its live alt "Cigala Cycling Coaching Logo".
- Structured data added (15 Nov): each free tool page has a WebApplication (free, SportsApplication) JSON-LD; /tools/ and /case-studies/ have an ItemList. Existing site schema (Organization, Service, WebSite) untouched. Verified on staging: valid JSON.
- Yoast focus keyphrases set where missing (`tools/yoast_coaching_keyphrases.py`): Book 1-on-1 (3750), Terms (564), two blog posts (4917, 4894). Titles and metas unchanged.
