# Vivify Sports (vivifysports.com): redesign for the move from Wix to WordPress

Marine Lenehan's sports nutrition business (Wicklow), a partner of Cigala Cycling Coaching. Matteo asked on 16 Nov 2026 for the site to be remade in **his font style**, with **Vivify's own logo and colours**. The site moves from Wix to WordPress afterwards.

This is a static preview only. Nothing has been changed on the live Wix site, and no WordPress site exists yet.

## Build and check

```
python3 -I tools/build_vivify.py          # -> vivify/site/*.html + vivify/site/img/ (copied from vivify/webp/)
python3 -I tools/seo_check_vivify.py      # title / meta / H1 / H2 per page against the live baseline
cd vivify/site && python3 -m http.server 8765 &
node ../../tools/vivify_check.js          # 390/820/1440: sideways scroll, one H1, alt text, 16px form fields
node ../../tools/vivify_shots.js          # full-page screenshots -> vivify/shots/ (scrolls first so lazy images load)
```

Open `vivify/site/index.html` in a browser to click through the preview.

| Path | What it is |
|---|---|
| `baseline-2026-11-16.json` | SEO crawl of the live Wix site before any change. It holds 72 URLs: 16 pages, 32 posts, booking/pricing pages and 18 Wix demo products that already return 404. Re-run: `python3 -I tools/crawl.py www.vivifysports.com $(grep ^https vivify/raw/sitemap-urls.txt)` |
| `raw/` | Live sitemap URLs, homepage and blog HTML, rendered page data, the sample post content |
| `text/` | Copy of every main page as shown on the live site |
| `webp/`, `images.json` | All 55 live images as WebP q90 from the largest Wix original (long edge ≤ 2560), with their live alt text and the pages that use them. Originals go to `img-orig/` (gitignored). |
| `live-shots/` | Screenshots of the live Wix pages (before) |
| `shots/` | Screenshots of the new design at 390 and 1440 |
| `site/` | The built preview |

## Design

- **Matteo's system (BRAND.md):** Anton capitals for headlines and Montserrat for everything else. Each section has an eyebrow, then a heading, then a short bar. Pages use panels with 12px corners, 999px chips and 8px buttons, with "nothing touching" spacing. The header has the square logo top left at 58px, the menu and one button. The footer has the logo at 76px, an Anton tagline and links.
- **Vivify's colours, from the live site:**

  | Role | Value | Where |
  |---|---|---|
  | Page ground | `#0C2226` | Deep teal |
  | Panels, header/footer tint | `#19444B` | Vivify teal (the logo square) |
  | Action | `#B1D8DD` | Aqua buttons, dark text on top. Same as the live buttons. |
  | Accent | `#80A315` | Lime from the About page subheads. Used for eyebrows, chip dots, the current-page underline and stars. Lighter `#9cc21f` for small text. |

- **Logo:** the live master file (909×855 teal square, white V, "VIVIFY SPORTS"), used as supplied.
- **Not carried over from Cigala:**
  - The topo background, green/red, the Cigala cookie banner and chat.
  - The live site has no Analytics or Pixel, so nothing needs consent yet.
  - If Marine adds tracking on WordPress, it must load only after consent. The banner would need Vivify colours and her own chat or none, so it would be a Vivify version of `shared/consent/`, not the Cigala one. Ask Matteo first.

## Pages built (21)

| Page | Notes |
|---|---|
| Home | Built from the live content. |
| About | Built from the live content. |
| Sports Nutrition Philosophy | Built from the live content. |
| Sports Nutrition Coaching (`/sports-nutritionist-ireland`) | The live page currently renders unstyled. The plan comparison image is rebuilt as a real HTML table. |
| Massage Therapy | Built from the live content. |
| Online Yoga | Built from the live content. |
| Workshops | Built from the live content. |
| E-Book (`/recipies`) | Built from the live content. |
| Blog | 33 cards with category filters. |
| Contact | Built from the live content. |
| Free Discovery Call | Built from the live content. |
| Privacy Policy | Built from the live content. |
| One post template | Uses `/post/carbohydrate-fueling-endurance-sports`, word for word. |

**New SEO pages (8, draft copy for Marine to approve), added 16 Nov 2026:**
- Cycling Nutritionist
- Women's Cycling Nutrition
- Triathlon Nutritionist
- Race Fuelling Plan
- Online Sports Nutritionist
- Sports Nutritionist Dublin & Wicklow
- FAQ
- Client Reviews

Built by `tools/vivify_seo_pages.py`; the plan and keyword map are in `SEO-PLAN.md`.

## SEO: what is kept and what changed

**Kept, checked with `tools/seo_check_vivify.py`:**
- every Wix title and meta description, exactly;
- every live H1 and H2 wording, including the testimonial-name H2s and the plan H2s with prices;
- body copy word for word, live typos included (list below);
- all live image alt text, except the ones listed under "Alt text";
- every URL slug.

**Changed (improvements, need Matteo's/Marine's OK):**

| Page | Live | New |
|---|---|---|
| Home | H1 is an empty zero-width character | H1 = the visible hero line "HEALTHY HABITS TO IGNITE YOUR POTENTIAL" |
| About | Second, empty H1 | Removed |
| Yoga | Two H1s ("ONLINE YOGA", "Book Your Session Now") | The second one becomes an H2 |
| Blog, Contact, Privacy Policy | No H1 | H1 "Sports Nutrition Blog", "Contact", "Privacy Policy" (their page titles) |
| Blog | Only 4 card titles are H2s (Wix lazy-loads the rest) | All 33 card titles are H2s |
| Coaching | Plan table is one image with alt "choaching plans updated 2026 .png" | Real HTML table, readable by Google and screen readers |

- **Structured data:** posts keep `BlogPosting`. New markup:
  - `ProfessionalService` on Home;
  - `Person` on About;
  - `Service` with 5 offers on Coaching;
  - `Product` on the e-book.
- **Alt text:** files with no alt or a file-name alt got descriptive alt text:
  - hero: "Marine Lenehan cycling on a lakeside road";
  - yoga photo: "Yoga pose on a clifftop by the sea at sunset";
  - About portrait: "Marine Lenehan, MSc Sports Nutritionist and founder of Vivify Sports";
  - partner logos.
- **Blog post missing from the live sitemap:** `/post/iron-deficiency-anemia-and-performance` (live, 200). WordPress (Yoast) will list it.
- **Duplicate H1 on two live posts:** `/post/recovery-nutrition-tart-cherry-juice` and `/post/from-curiosity-to-clarity-a-journey-into-recovery-nutrition` both have the H1 "From Curiosity to Clarity…". One should be redirected, or retitled.
- **Already 404 on live:** the 18 `/product-page/camo-backpack-*` and `/i-m-a-product-*` URLs are Wix demo products still in the store sitemap. Leave them out of WordPress.

## Typos kept word for word (ask Marine before fixing)

- "BREAKFATS TO IGNITE YOUR POTENTIAL" (E-Book H1)
- "NUTRITIONAL ASSESEMENT"
- "SPORTS SPECIFIC REQUIMENTS"
- "VIFIFY SPORTS is here to help"
- "PERFORMACE"
- "STRENGHTENING"
- "loose weight" / "loose a few kilos"
- "recipes for every pallet"
- "Sports Nutriton Ebook" (the e-book page's title)
- "MSs Sports Nutritionist" (the About meta description)
- "Masssage Theraphy" (several default meta descriptions)

## Open questions (to check with Marine)

1. **Discovery call links:**
   - The live coaching page's "BOOK NOW" (assessment, follow-up) and "BOOK YOUR FUELLING PLAN HERE" buttons had no link the crawler could find.
   - The preview sends "Book now" to the Wix discovery-call calendar (`/booking-calendar/...`), and the fuelling button and the header button to Contact.
   - On WordPress the calendar needs a booking tool (Calendly, Amelia, or similar).
2. **Plan payment links:** the 3 GoCardless "SIGN UP" links are mapped Healthy → `BRT0004V6AWJMPG`, Happy → `BRT00045M0TDENA`, Performing → `BRT00045M0SDGT2`. That is page order; the live coaching page renders unstyled, so this can't be checked visually. Marine to confirm.
3. **E-book sale:** it is sold through Wix (5.99€). WordPress needs WooCommerce or a payment link. The preview button points to the live page.
4. **Yoga:** only "Monthly Subscription" has a payment link on live. The other two classes say "Enquire" and go to Contact.
5. **Partners:** "Bryan McKinney" logo: confirm the name and whether it links somewhere.
6. **Tracking:** does Marine want Analytics or a Pixel? If so, see Design above.

## Moving to WordPress (plan)

1. Hostinger WordPress install on a staging subdomain, with `Disallow: /`. Work only there; go live together with Matteo.
2. **Permalinks:**
   - Pages: `/%postname%/`.
   - Posts: custom base `/post/%postname%/`, so every `/post/<slug>` URL survives.
   - Wix URLs have no trailing slash. WordPress 301s `/about` → `/about/` automatically. Set Yoast canonicals to the new form and resubmit the sitemap.
3. **Redirects (Redirection plugin):**
   - `/nutritionalcoaching` → `/sports-nutritionist-ireland/` (a 301 on live today);
   - `/service-page/vivify-sport-s-discovery-call` and `/booking-calendar/...` → `/free-sports-nutrition-consultation/`;
   - `/pricing-plans/list` → `/sports-nutritionist-ireland/`;
   - `/challenges` → `/sports-nutritionist-ireland/`.
4. **Content:**
   - Yoast titles and metas copied exactly from `baseline-2026-11-16.json`.
   - Posts imported word for word with their dates and WebP images. `tools/coaching_vivify_posts.py` already converts Vivify posts to Gutenberg blocks and can be pointed at the new site.
5. **After launch:** re-crawl with `tools/crawl.py` and compare against `baseline-2026-11-16.json`.

## Review PDF for Marine

`Vivify-Sports-website-preview.pdf` has a cover (colours, fonts, what's new), one board per page (desktop full page and the top of the phone view) and her questions.

Rebuild it after the screenshots:
```
node tools/vivify_shots.js       # run from vivify/site with the local server up
node tools/vivify_board.js
python3 -I tools/vivify_board_pdf.py
```
The board PNGs in `vivify/board/` are gitignored.

## E-book: Breakfasts to Ignite Your Potential
- Build: `python3 tools/vivify_ebook.py` -> `vivify/ebook/Breakfasts-to-Ignite-Your-Potential.pdf` (52 pages, A4, website style).
- Text and macros are unchanged from Marine's PDF (`vivify/ebook/source-text.txt` -> `recipes.json`).
- Marine's photos are kept. The 13 recipes that had placeholders use CC0 / public-domain photos (`img/new-*.jpg`, sources in `photo-credits.json`).
- Status: approved by Marine (18 Nov) and uploaded: `python3 tools/vivify_ebook_upload.py` (PDF + cover + hidden page /ebook-download-<token>/, state in `vivify/wp-ebook.json`).
- Stripe redirect: done by Marine (18 Nov), to the staging URL. Change it to the vivifysports.com URL at go-live.
- Noindex: Code Snippets plugin (installed with Marine's OK, 18 Nov), snippet #5 "Hide e-book download page from Google" filters wpseo_robots + wpseo_exclude_from_sitemap_by_post_ids for page 1025.
- Go-live: the staging site is noindex site-wide (Settings > Reading > Discourage search engines). Untick it at go-live, then check the download page still says noindex and every other page is indexable. Re-run the upload script after a menu/header change so the page header stays current.

## Blog page lists posts automatically (18 Nov)
- `python3 tools/vivify_blog_wp.py`: /blog/ is now a block page (header/hero/filters + Query Loop of all published posts + footer), not Elementor. New posts appear when published.
- Do NOT push blog.html with build_vivify_wp.py any more (it would bring back the fixed list): build_vivify_wp.py skips it.
- Imported posts got their Wix card text as excerpt and a featured image where missing.

## Monthly blog draft (Marine, 18 Nov)
- Marine owns the site and asked for one draft post a month, emailed to marine@vivifysports.com by her own WordPress.
- `python3 tools/vivify_blog_draft.py vivify/blog-drafts/<slug>.json`: creates a DRAFT (never published) with the Vivify post layout, sets Yoast title/meta, then calls the Code Snippets REST route vivify/v1/notify-draft (snippet #6) which wp_mails Marine preview + edit links.
- Scheduled task "Vivify monthly blog draft" (trig_016E6F18ywgFaTpZxdbu3jv4): every Monday 08:47 Dublin, acts only on the first Monday of the month.
- First draft (test): "Winter Cycling Nutrition..." (post 1070), 18 Nov.
- After go-live: change SITE in tools/build_vivify_wp.py to https://www.vivifysports.com and save the WordPress app password for that host on the environment, or the monthly job can't reach the site.
