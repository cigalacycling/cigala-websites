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
- /cycling-coach-uk/, -usa/, -canada/: done, see section 10 (Matteo approved the rewrite on 15 Nov).
- Crawl of staging (15 Nov, `stg-coaching/crawl-after-2026-11-15.json`, compared by `tools/compare_coaching_crawl.py`): 76 live pages; titles, metas, H1s, H2s, alt texts and schema types match except the approved changes (homepage hidden "IRELAND" H2, two Yoast title typo fixes, icon images left out, the two packages photos Matteo replaced, /dummy-page/ to be redirected). The header logo keeps its live alt "Cigala Cycling Coaching Logo".
- Structured data added (15 Nov): each free tool page has a WebApplication (free, SportsApplication) JSON-LD; /tools/ and /case-studies/ have an ItemList. Existing site schema (Organization, Service, WebSite) untouched. Verified on staging: valid JSON.
- Yoast focus keyphrases set where missing (`tools/yoast_coaching_keyphrases.py`): Book 1-on-1 (3750), Terms (564), two blog posts (4917, 4894). Titles and metas unchanged.

## 10. UK, USA and Canada pages rewritten (15 Nov 2026, Matteo: "Yes go ahead")

Builder: `tools/build_coaching_country.py` (replaces the generic build for pages 6098, 6100, 6102).

Kept exactly as live: URL, Yoast title (Canada typo fix from section 1), meta description, H1, all live H2s (checked by
`build()` and on staging), the intro paragraphs, the event and region lists, prices and GoCardless payment links in GBP/USD/CAD,
the package feature lists (in each page's own currency), every live FAQ question (same wording, checked by an assert).

Changed, for Matteo to read on staging:
- **Testimonials.** Live showed five quotes credited to people who don't exist ("William - Wales, UK", "Bernd - England, UK",
  "Peter - New York, UK", "John - Quebec, Canda"...). They were real testimonials (Bernd, Bryan Nolan, William Rymer, Derek Lawler)
  under invented UK/US/Canadian names, or rewordings of them. Fake reviews are a Google and consumer-law risk, so each page
  now shows six real testimonials, word for word, with the athlete's real name and place (picked per country: Mallorca 312
  and time-crunched riders for the UK; the US stage race, family/work balance and weight loss for the USA; winter training for Canada).
- **Own copy per country.** New: three facts under the intro (time zone, currency, terrain/winter), "How it works" in 4 steps
  (H3, time-zone details per country), a region paragraph on terrain and climate, and "Guides from our blog" links
  (Fred Whitton / winter for the UK, gravel and heat for the USA, Gran Fondo Whistler / winter for Canada).
  FAQ answers rewritten per country (prices in the local currency, UK same clock as Ireland, US/Canada time differences,
  local events in "My event is months away"), plus one extra question: UK time trials and hill climbs, USA long gravel races.
  Overlap of the text between the pages went from 81-88% to under half, and what's left is mostly headings and shared site blocks.
- **Typos:** "Canda" -> "Canada" (body), "reccomendations", "New York, UK" (removed with the fake quotes), "remotely delivering in".
- The "Why ... choose" Vekta line shows Vekta's value in the page's currency (£17.99, $21.99, $30.99), as the package cards on live already did.
- Premium shows "Join the waiting list" as on the main Packages page (sold out). Basic has no payment link on the live
  country pages, so its button is "Start with a free call".
- Live had three H1s: "#TrainSmarterRideFaster" is now the eyebrow of "It's our vision" and "START WORKING WITH MATTEO"
  the eyebrow of the closing call to action (one H1, section 2).
- A contact form was added at the end (the Premium waiting-list button needed one). The form is the live Elementor form, sending to matteo@.

To check with Matteo:
- Canada Basic: the live card says "one-time payment of $387", the live option says "390 CAD". Left as live.
- Matteo 15 Nov: confirmed calls in the client's morning, payment by GoCardless and "no exchange fees" for UK clients.
- Matteo 15 Nov: Basic must have a payment button. The live pages DO have one: a Revolut checkout link in the Basic drop-down
  (missed at first because the live option value ends with a space). Basic now has "Buy Basic 12 Weeks" with that live link.
- Canada Basic: the live card said $387 ($129/mo) but the live Revolut link is "390 CAD": the card now shows what is charged ($390 CAD, $130/mo).
- Matteo 15 Nov: hero photos are now Cigala/Matteo photos instead of random cyclists (UK: coaching an athlete; USA: Matteo in
  Cigala kit in Wicklow; Canada: Matteo winning Tre Valli Varesine); event photos too. Currency codes removed (only CAD
  stays, as "$" alone reads as US dollars); "by GoCardless" removed from the facts (Basic pays by Revolut).
- Matteo 15 Nov: H2 "2025 IN NUMBERS" -> "2026 IN NUMBERS" on UK/USA/Canada and "2025 IN NUMERI" -> "2026 IN NUMERI" on Italia
  (same numbers as the Packages page, which already says 2026). No green line under the testimonials heading (as on Packages).
- Marine: turned professional in the WorldTour on 1 January 2026 (Matteo): on her case study timeline and result.

## 12. Blog, blog posts and Testimonials (15 Nov 2026, Matteo)

- Blog posts (staging, all 46 by Matteo): the childhood photo at the end ("Matteo Cigala 6 years old", RGB with a white
  background that showed as a white card) is replaced by the white-jersey cut-out with his signature in white
  (`tools/make_author_signature.py`, `tools/coaching_posts_author.py`; originals in stg-coaching/posts-backup/).
  New alt: "Matteo Cigala, Founder & Head Coach of Cigala Cycling, in the white Cigala Cycling jersey, with his signature".
- Single post template 4028: topo background (same as the redesigned pages); the "CIGALA CYCLING #TrainSmarterRideFaster"
  block under every post was unreadable (dark grey hashtag, tiles without their photos): now white/green, four photo tiles.
- "Strength Training for Cyclists" had no featured image (blank card on /blog/): set to the gym photo from the post itself.
- /blog/ cards: smaller (16:9 photo, 3-line excerpt, no divider), "Read More →" as an outline button.
- Testimonials: photos shown whole (no crop). Found and fixed: images with the same alt text were saved under the same file
  name, so one photo replaced the others (Shane Courtney, Barry Fitzgerald and David Sheanan showed one photo; John Dowley
  and Jack Caldwell another). File names now get a short hash when an alt is shared (build_coaching_generic.pic).

## 13. Service pages redesigned, Nutrition upgrade, Triathlon prices (15 Nov 2026, Matteo)

Builder `tools/build_coaching_services.py` (Contact 461, Book 1-to-1 3750, Bike Fitting 4256, Testing 3865, Triathlon About 3770,
Club Talks 4395). Each keeps its URL, Yoast title and meta, H1 and every live H2 (checked by build()); live copy kept, typos fixed.
New H2s (logged here): 1-to-1 "FROM PURCHASE TO YOUR FIRST SESSION"; Bike fit "PRECISION AND EXPERIENCE", "EVERY MILLIMETRE COUNTS",
"BIKE FITS WITH MATTEO", "BIKE FIT PRICES"; Testing "A FULL 360° PHYSIOLOGICAL ASSESSMENT", "THE METRICS THAT MATTER",
"INSCYD VS CONVENTIONAL TESTING"; Triathlon "SWIM, BIKE, RUN: ONE PLAN", "WHAT YOU GET", "TRIATHLON COACHING PACKAGES",
"KNOW YOUR NUMBERS", "FREQUENTLY ASKED QUESTIONS" (+ FAQPage JSON-LD).
- 1-to-1: buy buttons go to the shop product "One-on-One Sessions" (3/6/10/20 sessions, €240/€480/€750/€1,400). The shop
  product description still says "Navan, Co.Meath": Matteo to update it to Wicklow Town (not changed from here).
- Bike fit: new prices (Matteo): €80/£70 per bike, second bike €60/£50 (live said €70/£60, +€50/£40). Reservation form
  (subject "Bike fit reservation"), bikefit@cigalacycling.com kept, free tools band.
- Testing: the six "What we organise" steps had placeholder text (the Premium package line, six times): now real text for
  each step title. "Buy now" goes to the shop product "INSCYD Metabolic PPD Testing" (€189) instead of a cart link.
- Club talks: Matteo presenting (the only presentation photo in the media library) + group coaching photos; quote form.
- Contact: phone, email, WhatsApp, area and socials beside the form; quick links. No street address (shared/BUSINESS.md).
- Forms: per-page subject and message hint (build_coaching_wp: data-subject / data-msg; side content between <!--side--> marks).
- Nutrition: Marine's own portrait and credentials from vivifysports.com/about (MSc, LIDL-TREK, titles); every "VIVIFY SPORTS"
  links to vivifysports.com; "What's covered" + 7 items from Vivify's coaching page; nutrition coaching as an upgrade
  (calendar redrawn from Matteo's screenshot, food diary, race fuelling from CP, gut training; price set by Marine).
- Triathlon packages: same prices, wording and payment links as Individual (Matteo); intro "2 packages" -> 3.
- Package buttons: Basic buy and Premium waiting list are solid green on every packages page (Matteo).
- Talent Programme (/talent-scout/, page 896, Matteo 15 Nov: "completely to be redone"): `build_coaching_services.py talent`.
  H1 and all five live H2s kept; FAQ answers kept (typos fixed; "Skype" -> "video call"), FAQPage JSON-LD; A&J results as tiles
  (race names spelled correctly). New H2 "THE DATA BEHIND THE TALENT" with a power-duration chart from Marco B.'s case-study
  numbers (year 1 vs year 2; hover values, "See the numbers" table) and what Matteo analyses. Apply form (subject "Talent
  Programme application"). To check with Matteo: the live price "Advanced Package at €104" vs "20% discount" (20% off €149 is €119).

## 14. Nutrition (3rd review) and Marine's articles (15 Nov 2026)

- Nutrition copy: the live "Vital Hygiene Program ... healthy lifestyle ... physical exercises to promote movement ... stress and
  emotions" was not accurate (Matteo: sports nutrition only). Rewritten as the personalised sports nutrition plan; FAQ to match.
- Marine: "2× Irish National Champion (gravel 2026, criterium 2024) · Amateur Gravel World Champion 2024" (no e-sport title).
- Upgrade cards with icons; "daily macros (carbohydrates, protein and fat)"; food diary in MyFitnessPal; calendar redrawn closer to
  Matteo's screenshot (day counters, both notes on the 23rd, comments, completed ticks, power traces) in the site's style; the
  meal note is now an example recipe; "Book a free discovery call with Marine" -> vivifysports.com/contact.
- Five of Marine's articles published on the Coaching blog (staging) from vivifysports.com, word for word, images as WebP with
  their alt text, tag "By Marine Lenehan" (her name on the blog cards), her signature and a "first published on vivifysports.com"
  link (`tools/coaching_vivify_posts.py`, `tools/yoast_coaching_vivify_posts.py`): carbs-per-hour-endurance-fueling,
  ironman-70-3-nutrition-plan, fatigue-after-exercise-endurance-athletes, daily-fat-intake-guide,
  cycling-nutrition-what-to-eat-and-drink-on-the-bike. Yoast title, meta and keyphrase set. To decide with Matteo: the same
  text is on vivifysports.com (duplicate content); a canonical to her site, or rewording, would avoid the two competing.
- The Nutrition page lists these five plus her cherry juice article.
- Nutrition (4th review): the consultation copy no longer repeats the report sentence; "responsible for your own health" removed
  (performance nutrition). Marine's photo with the background removed (rembg isnet + alpha matting) and her signature in white
  (`tools/make_marine_signature.py`); carbs per hour on the calendar rides (Matteo: torque 40–50 g/h, both LDT 60 g/h, none on
  recovery, dynamic, stretch, strength); three sample notes (recovery bowl, breakfast, supplement plan) marked "samples only";
  3 more FAQs (FAQPage JSON-LD); 8 articles listed, all Marine's.
- Two more of Marine's articles published (why-do-you-bonk-on-the-bike, top-5-foods-for-cyclists). Every article signed by Marine
  (the 7 new + 6 that were already on the blog: cherry juice, Christmas, weight loss, winter fuelling, homemade sports drinks,
  hydration) is tagged "By Marine Lenehan" and ends with her new author image (`tools/coaching_marine_existing_posts.py`).

## 15. Matteo's page-by-page review (15 Nov 2026, evening)

- /coaching-vision/ redesigned (`build_coaching_services.py vision`): H1 "#TrainSmarterRideFaster" -> "Train Smarter. Ride Faster."
  (Matteo: no hashtag); H2 "READ OUR TESTIMONIALS - WHAT PEOPLE SAY ABOUT CIGALA CYCLING" -> "READ OUR CASE STUDIES" (case studies
  instead of testimonials, Matteo). Other H2s and all copy kept. New hero photo (the lake photo is on the packages pages); the
  "Over a decade" montage without the white frame; homepage-style As Seen In logos; package cards with "from €19/week".
- /individual-packages/: the team photo in the Vekta section is replaced by the athlete calendar with nutrition (live alt of
  imgi_43 no longer on the page); H2 "FOLLOW YOUR STRUCTURED TRAINING SESSIONS ON YOUR FAVOURITE DEVICES & APPS (BELOW SOME APPS -
  THE LIST IS MUCH LONGER)" -> "SYNC WITH YOUR FAVOURITE DEVICES & APPS" (Matteo: too long); FAQ + nutritionist question.
- Small fixes: Group page club band photo + button; club talk photo zoomed past the photographer's credit; 1-to-1 without
  "Best value"; Triathlon "What you get" + 2 cards and a nutrition FAQ; bike fit "BIKE FITS WITH CIGALA CYCLING" + WhatsApp;
  contact 8 quick links; testimonials hero with the sharper Marine photo; blog "Read more" in the brand font.
- /talent-scout/ round 2: H1 and all 11 live H2s kept, live copy kept (cost line updated to the current talent price,
  €119.20 a month = 20% off €149, Matteo). Added: intro naming A&J AllSports' riders (Pogačar, Del Toro, Girmay, Philipsen;
  press sources: cyclingnews, cyclingweekly, escapecollective), power-duration chart now Tilen's (Vekta data, case study),
  8 analysis boxes, the wins count up on scroll (numbers as on live: no official A&J site found to verify them), itinerary-style
  steps, one-calendar block with nutrition, 5 more FAQs (FAQPage JSON-LD). Still needed from Matteo: a larger A&J logo
  (live file is 205×105) and a photo of Alex & Johnny Carera we are allowed to use.
- /cycling-coach-uk|usa|canada/ round 3: H2 "READ OUR TESTIMONIALS - WHAT PEOPLE SAY ABOUT CIGALA CYCLING" -> "READ OUR CASE
  STUDIES" with a "Read our case studies" button (Matteo). "How it works" in the Tours itinerary style, with a 5th step
  (nutrition) and the athlete calendar beside it; nutritionist FAQ added. USA hero: Vekta x Cigala Cycling app photo (new alt,
  the live file had none); Canada hero: Matteo winning at Strade Bianche (live alt). Neither implies Ireland (Matteo).
  Shorter on mobile: event and region lists as compact 2-column cards, free tools as a sideways row, smaller device logos,
  shorter events photo. All live copy, lists and FAQ questions kept.
  Not changed: the live quotes under invented names ("William - Wales, UK", "Peter - New York, UK"...) stay off the pages
  (see section 10); real names and places stay. Matteo can send real clients from each country to add.
- Matteo's answers (15 Nov, late): A&J logo and team photo supplied (talent page; logo keeps the live alt); wins checked on
  aejallsports.ch "About us" counters: Tour 6 -> 7, Vuelta 3 -> 4, World titles 44 -> 45, Giro 6 unchanged; source line added.
  Club Talk: Matteo's presentation photo. Footer tagline H2 "Train Smarter, Ride Faster" -> "TRAIN SMARTER. RIDE FASTER."
  (every page). Shopify "One-on-One Sessions": Navan, Co.Meath -> Wicklow Town, Co.Wicklow (live store, Matteo's answer).
  Vivify articles: Yoast canonical -> the original vivifysports.com post (7 posts, tools/coaching_vivify_canonical.py).
  Packages: "Monthly (SOLD OUT!)" badge removed (SOLD OUT stamp on the card instead), second buy button under each card,
  A&J line in the Talent box; Vision "Over a decade" image smaller.
- /about/ redesigned (tools/build_coaching_about.py; Matteo: "terrible, too much text, alignment mixed, Read our testimonials
  shows nothing"). H1 and all live H2s kept except "READ OUR TESTIMONIALS - WHAT PEOPLE SAY ABOUT CIGALA CYCLING" ->
  "READ OUR CASE STUDIES" (with the case study cards under it, as on Vision/countries). All live copy kept word for word
  (typo "we provides" -> "we provide"), all live images with their live alt (unnamed-35.png had no alt and no content:
  left out). Added photos: Strade Bianche win, Volta Almodovar win. Old cigalacycling.com links point to the coaching pages.
- Later fixes (15 Nov): Group page club band without the green bar and hover outline; the contact photo next to the form is
  as tall as the form (4:5) on every page; 1-to-1 page: Matteo's presentation photo beside the booking form (the live
  "Matteo Cigala Coaching" photo stays), hover highlight on the packs, a line joining the step dots (all step lists);
  homepage stats strip 24px lower; Italia "2026 IN NUMERI" uses the coloured, counting boxes; packages note reworded to
  "a limited number of athletes" (Matteo, replaces "get in touch before signing up") and a sample note from Marine
  under the Vekta calendar.
- About round 2 (Matteo): hero = the transparent cut-out with signature (keeps the live alt), qualification badges
  (UCI & Cycling Ireland Level 1, TrainingPeaks Level 2), "200+ race victories", science list in the same chip style,
  reviews strip and the coloured 2026 numbers under the case studies; the long COACHING / BIKE TOURS / RETAIL cards
  replaced by four short icon tiles with links (Matteo: too much text, repeated the tiles). The Tre Cime tour photo
  (live alt "Cyclists at Tre Cime peaks") is no longer on /about/; its copy is on the Tours site.
- Individual Packages H2 "READ OUR TESTIMONIALS - WHAT PEOPLE SAY ABOUT CIGALA CYCLING" -> "READ OUR TESTIMONIALS" (Matteo).
- Contact headings (H3, not H2): "GET IN TOUCH TODAY" -> "READY TO TAKE YOUR CYCLING TO THE NEXT LEVEL?" (triathlon /
  group / contact page variants). Vision: hero eyebrow "Our vision", the quote section eyebrow "Train Smarter. Ride Faster."
  above the live H2 "It's our vision". Marine's three sample notes in a slider under the Vekta calendar.
- Triathlon packages: H2 "FOLLOW YOUR PLAN ON" section removed (Matteo; the TrainingPeaks and Zwift logos, with their live
  alts, stay under As seen in); contact photo is an open-water swim instead of the hero photo again. Package cards lift on
  hover; review strips move on every 5 s (pause on hover/touch/arrows, off with reduced motion); case studies stay static.
- Talent: chart now Eoin R. (both seasons at 15 s, 1 min, 5 min and Critical Power, Vekta data); A&J riders past and
  present as a full row with each one's top win on hover (A&J history page); wins boxes highlight on hover; step titles
  above the text. Nutrition tool icons match the free tools. Bike fit: booking eyebrow, smaller contact headings, side
  panels top-aligned. "Club talk" is called "Workshops" in the menu, buttons and eyebrows; URL /club-talk/, H1 and Yoast
  title unchanged (no SEO change). Topics as icon tiles.
- Blog: 12 posts per load (full rows of 3, or 2 on tablet) and a new hero (Matteo riding, live alt of imgi_20; the
  autograph photo IMG_5144 is no longer on /blog/). Testimonials hero photo full width on phones. Canada hero: the team in
  Cigala kit (not the Strade Bianche win). Marine's notes slider with arrows and dots (no scrollbar), also under the
  calendar on UK/USA/Canada. Individual Packages: Free Training Tools moved under the Vekta section. Triathlon cards:
  second buy button like cycling. Forms: a real test submission on staging /contact/ returned "Your submission was
  successful"; every page's form is the live Elementor form with 16px fields.
- About round 3: hero titles without years (Matteo): 200+ race wins, European Road Champion Gran Fondo, Vice-World Champion
  UCI Gran Fondo (road), Vice-World Champion UCI Gravel, Italian Gravel Champion; "UCI & Cycling Ireland Coach"; flags on
  the story timeline; one bullet style for all seasons; no repeated trophy/chart icons; tiles = title + link.
  Footer: "INSCYD Testing" link replaced by "Talent Programme". Homepage hero line names Matteo and his titles; the stats
  say the 28 years and 200+ wins are Matteo's own.
- Case-study rows move on by themselves every 4 s on every page (pause on hover/touch, off for reduced motion), like the
  reviews. About: "Vice-World Champion UCI Gran Fondo" (no "(road)"), EU flag for the new-era chapter, icons back on the
  results and science lists (a different icon per line), bottom tiles with photos (the Tre Cime tour photo is back with
  its live alt; the cycling tile uses the Wicklow climb photo, retail the smart-trainer photo).
- Talent: chart now David O. (real Vekta data: 30 s 505 → 633 W, 5 min 288 → 320 W, 20 min 250 → 276 W, CP 244 → 288 W);
  Matteo: not Eoin. Text under "We are a Talent Scout" all one size; 4 more A&J athletes (Vainšteins, Pellegrini,
  Brugnetti, Zorzi: from the A&J history page), label "Athletes managed by A&J".
- /club-talk/ H1 "Club information days, coaching nights, Q&A, group coaching sessions and more" -> "... coaching workshops,
  ..." and "coaching nights" -> "coaching workshops" in the copy (Matteo). URL and Yoast title/description unchanged.
- /testimonials/ H1 "READ OUR TESTIMONIALS - WHAT PEOPLE SAY ABOUT CIGALA CYCLING" -> "READ OUR TESTIMONIALS" (Matteo: no
  hyphen); "What people say about Cigala Cycling" stays right under it as a subtitle (not a heading). Testimonial and
  review cards highlight on hover. Blog hero: Matteo winning in Siena, whole rider in frame (the riding photo cut his face).
- Individual Packages: the 5 live testimonials (same quotes and photos with their live alt) now in the moving review strip
  like the rest of the site; the currency note in the first person ("please contact me"), like the note beside it.
- Talent chart (Matteo chose this): "What the teams look for": typical W/kg at 5 s, 1 min, 5 min and threshold for club
  racer, elite amateur/U23, Continental pro and WorldTour; approximate values after Allen & Coggan's power profile (men),
  labelled as such. No athlete named or invented. A&J wins light up in their own colour on hover (yellow Tour, pink Giro,
  red Vuelta, rainbow Worlds, polka dots, etc.). FAQ "Who are A&J AllSports?" showed "&amp;": fixed.
- Blog cards: the 7 Vivify articles had no "author_name" ACF value, so their cards lacked Marine's label; copied the value
  from her older posts (tools/coaching_vivify_author_field.py, temporary snippet removed). Author label in red.
  Case-study rows: left/right arrows like the reviews; no drag bars on either. Testimonials: Marine's photo smaller.
  Talent chart restyled like Vekta's power curve (smooth curves on a time axis), U23 / Continental / WorldTour only.
- Country testimonials: Matteo asked again (15 Nov) to restore the live names (William-Wales, Greg-Colorado, Mark-Texas,
  Chris-Ontario...). Checked the live pages: the quotes are real testimonials by other clients (e.g. Bryan Nolan, Limerick;
  Derek Lawler, Kilkenny; Bernd, Germany) shown under different names, and the same quote appears under two or three
  names in different countries (Bryan's under "Daniel, Northern Ireland", "Mark, Texas" and "Mark, Alberta"). Not
  restored; real names kept; waiting for real clients from those countries.
- /preparatore-di-ciclismo-italia/ rebuilt like UK/USA/Canada (tools/build_coaching_italia.py, Italian): URL, Yoast, first
  H1, live H2s kept except 2025 -> 2026 IN NUMERI and the reviews H2 -> "LEGGI I NOSTRI CASI STUDIO" (as on the English
  country pages); all live copy, the 6 FAQs, live images with live alts, live pay links (Shopify Base, GoCardless
  Avanzato). Reviews: the live ones were real quotes under invented Italian names; now 6 real testimonials translated
  from English, real names, labelled as translated. Contact form in Italian (placeholders, "Invia").
- About: "200+ race wins" removed from the hero titles (it's in the facts row), facts row closer to the hero.
  Bernd Ondruch: "Germany & UK" (Matteo: lives in both); UK page leads with his review.
- Country reviews: the non-duplicated live quotes (William-Wales, Nat-California, Chris-Ontario) are rewordings of
  Marine's testimonial under invented names: not used. Bernd is the one real UK-linked client.
- USA hero: Matteo riding in the blue Italia kit on a dry, sunny road (live alt of imgi_20); not the Vekta image, nothing that looks like Ireland.
- Reviews on UK/USA/Canada: text only, first name + real place, no photos, eyebrow 'What our athletes say' (Matteo). Italian page: no English names, 'Atleta seguito da Matteo · Recensione tradotta dall'inglese'. Same H2s; no review schema on these pages, so no SEO change.
- Italia: events as cards (discipline tag, icon, place; live wording kept) next to the Strade Bianche win photo (live alt); case study cards in Italian (CASES_IT); newsletter band, its messages and the sold-out stamp in Italian on this page (JS/CSS on the page; the shared footer template is unchanged). Live H2s unchanged.
- Italia: motto band 'ALLENATI CON METODO, VAI PIÙ FORTE' with the live H2 'E' il nostro motto' under it; reviews under H2 'LEGGI LE NOSTRE RECENSIONI' (live H2 shortened, its second half kept as the line under it). 24 events: added gravel (Campionato Italiano Gravel, Serenissima Gravel, Nova Eroica, L'Eroica, Veneto Gravel), ultra (Tuscany Trail, Italy Divide), national championships and big granfondos; Matteo's own wins marked. Regions kept as a text list (better for SEO than a map).
- Italia: the sample calendar in Italian (Nutrizione, macronutrienti, session names), same days and numbers.
- Italia events: discipline filters (Tutti/Strada/Gravel/MTB/Ultra/Tutte le discipline; all cards stay in the HTML), 2 more MTB (Dolomiti Superbike, Capoliveri Legend Cup), 'Vinta da Matteo' on Mondiali/Europei (European Champion Gran Fondo 2022). 26 events.
- Italia: map of Italy in the brand style (Natural Earth outline, public domain) with a pulsing dot for each listed city, next to the region list (list kept as text for SEO); device logos moved under it.
- Italia intro: Matteo's cut-out with signature, 28+/10+/200+ numbers, the two live paragraphs (first larger), facts as a row; 'Perché sceglierci' list as icon cards. All live copy kept.
- Italia: intro paragraphs one size; 'Comunicazione in italiano / Prezzi in euro / ...' cards removed (Matteo); motto + reviews moved after packages and how it works, just before Presente su; 'Stampa e partners'; regions + Puglia, Sicilia, Sardegna (new list items and map dots); map labels repositioned.
- Italia in the first person (Matteo: "agli italiani piace la prima persona"). H2s approved by Matteo: "E' il nostro motto" ->
  "È il mio motto"; "Gli Eventi per Cui Prepariamo i Nostri Atleti" -> "... Preparo i Miei Atleti"; "Seguiamo ciclisti in
  tutta Italia" -> "Seguo ..."; the closing H2 "... Seguiamo ciclisti ..." -> "... Seguo ciclisti ..."; reviews/case study
  H2s "LEGGI LE MIE RECENSIONI", "LEGGI I MIEI CASI STUDIO". Body copy in the first person too (offro, preparo, seguo,
  alleno); "Matteo Cigala" kept in the hero line and in the H2 "Perche' atleti in Italia scelgono Matteo Cigala" (search).
  Contact: "Hai domande sulla preparazione? Scrivimi." Intro section 24px closer to the hero.
- Italia: hero eyebrow 'Allenatore di ciclismo online' (not a heading; adds the synonym, H1 unchanged); events photo: the summer Strade Bianche win (new Italian alt).
- UK/USA/Canada in the Italian page's style (Matteo): intro with Matteo's cut-out and 28+/10+/200+, facts row; events as
  cards with discipline filters (all live events kept word for word, plus real big events: UK Dirty Reiver, Grinduro,
  Battle on the Beach, Highland Trail 550, National Hill Climb; USA Unbound, Belgian Waffle Ride, Mid South, Leadville 100,
  Tour Divide; Canada BC Bike Race, Tour Divide); country map (Natural Earth, public domain) with the listed cities next to
  the region list. H2s unchanged. Italia: "membership incluso" -> "iscrizione inclusa" (Matteo).
- UK/USA/Canada: reviews with photos again (first name + real place); review/case rows have room for the hover border; blog guides as green buttons; events to full rows (UK +Etape du Dales, The Gralloch, LEJOG; USA +SBT GRVL, Gravel Worlds; Canada +Paris to Ancaster).
- SEO for the country pages (Matteo: rank high in each country). Already in place from live: hreflang en-gb/en-us/en-ca/it +
  x-default, site-wide Organization/Service schema. Added: per page a Service with areaServed (United Kingdom / United
  States / Canada / Italia) and a FAQPage from the page's FAQ. Bug fixed in tools/build_coaching_wp.py: page JSON-LD
  placed after the footer (FAQPage on Talent, Nutrition, Triathlon About...) was never pushed to staging; now it is,
  without duplicating the blocks that were already pushed (checked: one of each per page). UK box "Same time as
  Ireland" -> "Same time zone as you".
  Known gap: the site's <html lang> is en-US on every page, including the Italian one (WordPress site language); hreflang
  "it" tells Google the right language. To fix properly at go-live: set the language per page (WPML/Polylang or a small
  snippet). Not done on staging.
- 16 Nov, pre-go-live check (fresh crawl stg-coaching/crawl-after-2026-11-16.json vs live): all differences are approved
  changes already logged, except a crawler artefact: SVG <title> tags in the maps/chart were read as the page title by
  simple parsers -> replaced with aria-label (page titles now read correctly). AI search: Person schema for Matteo on
  /about/ (facts from the page), coaching/llms.txt drafted (to upload to the site root at go-live). robots.txt on live
  allows all crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended): keep it that way.
