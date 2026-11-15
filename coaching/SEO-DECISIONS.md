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
