# Vivify Sports: SEO plan (16 Nov 2026)

Goal from Matteo: rank Marine's site for "sports nutritionist" and "cycling sports nutritionist", above all in Ireland, and add pages that grow her international audience.

## What the search results show (checked 16 Nov 2026)

- **"sports nutritionist Ireland"**
  - Top results are directories and profiles: the BDA SENr register listings, LinkedIn, press articles and course providers.
  - Very few are a nutritionist's own service page. A focused service page with strong credentials can compete.
- **"cycling nutritionist Ireland"**
  - Nobody owns it. Results are 2019 interviews (Sport Ireland's nutritionist), pro-team staff articles and TrainingPeaks coach profiles.
  - Marine is a LIDL-TREK WorldTour rider, Amateur Gravel World Champion and MSc sports nutritionist. Nobody else in those results has that mix.
- **"online cycling nutritionist"**
  - International results are small practices and coaching companies charging about $240 one-off or $289–350 a month.
  - Marine's prices (100€ assessment; 99–199€ a month) are competitive.
- **"Marine Lenehan nutritionist Vivify Sports"**
  - Returns nothing about her or Vivify. Google does not yet connect her name to the business.
  - This is the first thing to fix (see Off-site, step 2), because her name and pro career are her strongest ranking asset.

I had no keyword-volume tool. Check the targets below in Google Keyword Planner, and in Search Console after launch.

## Keyword map: one page per search

| Page | Main search | Also targets | Status |
|---|---|---|---|
| `/sports-nutritionist-ireland` | sports nutritionist Ireland | online nutrition coaching, nutrition plans | Live page, kept |
| **`/cycling-nutritionist`** | cycling nutritionist (Ireland) | nutritionist for cyclists, cycling nutrition coach, gravel nutrition | **New** |
| **`/triathlon-nutritionist`** | triathlon nutritionist | Ironman / 70.3 nutrition coach | **New** |
| **`/womens-cycling-nutrition`** | women's cycling nutrition | nutritionist for female cyclists, female athlete nutrition, iron and energy availability | **New** (17 Nov) |
| **`/race-fuelling-plan`** | race fuelling plan | cycling fuelling plan, 70.3 nutrition plan, carbs per hour | **New** (it was only a section of the coaching page) |
| **`/online-sports-nutritionist`** | online sports nutritionist | sports nutritionist online; international, priced in € and US$ | **New** |
| **`/sports-nutritionist-dublin`** | sports nutritionist Dublin | sports nutritionist Wicklow; club talks, sports massage | **New** |
| **`/faq`** | question searches ("how many carbs per hour…", "what does a sports nutritionist do") | FAQPage markup | **New** |
| **`/testimonials`** | "Vivify Sports reviews" | trust page for all services | **New** |
| `/about` | Marine Lenehan | sports nutritionist and pro cyclist | Live page, kept; Person markup added |
| `/post/...` | long-tail questions | linked from the matching service page | Live posts, kept |

How the new pages are built:
- Each new page has one H1 and its own Yoast title and meta (in `tools/build_vivify.py`, `NEW`).
- Each has Service, FAQPage and Person structured data.
- Each links to 3–6 of Marine's articles on the same topic and to the plans.
- The footer and the homepage ("Who Marine works with") link to all of them, so Google finds them and passes weight to them.

**The copy on the new pages is a draft.** It uses only facts already on vivifysports.com: credentials, titles, prices, services, partners, real testimonials and Marine's own articles. Marine must read and approve every page before it goes live.

## Problems on the current site that hold rankings back

1. **Two pages compete for "sports nutritionist Ireland"** (cannibalisation):
   - the service page `/sports-nutritionist-ireland`;
   - the blog post `/post/sports-nutritionist-ireland` ("How to Choose the Right Expert…").

   Suggestion: retitle the post around "how to choose a sports nutritionist" and link it to the service page. Or merge it into the service page with a 301. Decide with Matteo.
2. **Two posts share one H1** ("From Curiosity to Clarity…"). Redirect one of them.
3. **A post missing from the sitemap:** `/post/iron-deficiency-anemia-and-performance`.
4. **No H1** on Home, Blog, Contact or Privacy. Yoga has two H1s. All fixed in the redesign.
5. **Typos in titles and metas** that Google shows in results (need Marine's OK):
   - "Sports Nutriton Ebook" (E-book page title);
   - "MSs Sports Nutritionist" (About meta description);
   - "Masssage Theraphy" (the default meta description on six pages).
6. **The coaching page renders unstyled on live**, and its plan table is a picture. Fixed in the redesign.
7. **No Search Console or Analytics**, so there is no data on what she ranks for. Set up Search Console on day one. Analytics must load only after consent.

### Title suggestions for existing pages (not applied, need approval)

| Page | Now | Suggested |
|---|---|---|
| Massage | MASSAGE THERAPY \| Vivify Sports | Sports Massage Wicklow & Dublin \| Deep Tissue & Cupping \| Vivify Sports |
| Yoga | YOGA \| Vivify Sports | Online Yoga for Cyclists \| Yin & Vinyasa \| Vivify Sports |
| E-book | Sports Nutriton Ebook \| Fuel Performance & Recovery | Sports Nutrition Breakfast Ebook: 30 Recipes \| Vivify Sports |
| Coaching H1 | ONLINE NUTRITION COACHING | SPORTS NUTRITIONIST IRELAND: ONLINE NUTRITION COACHING |

## Off-site: the biggest wins (Marine has to do these)

1. **Google Business Profile.** This matters most for Irish searches; the map results sit above everything for "sports nutritionist Dublin/Wicklow".
   - Category: Nutritionist.
   - Service area: Co. Wicklow and Co. Dublin, with no street address shown.
   - Website: vivifysports.com.
   - Ask the eight clients on the site to post their review on Google. Fresh Google reviews are a strong local ranking signal.
2. **Connect her name to the business:**
   - Her Instagram, LinkedIn, Strava and ProCyclingStats profiles and the LIDL-TREK rider page should say "Sports Nutritionist" and link to vivifysports.com.
   - Send me those URLs and I'll add them to the Person `sameAs` markup.
3. **Directories that already rank in Ireland:**
   - check whether her MSc makes her eligible for the BDA's SENr register, which fills page 1 for "sports nutritionist Ireland";
   - create a TrainingPeaks coach profile, which appears for "cycling nutritionist".
4. **Links and press:**
   - Story angle: "the WorldTour pro who is also a sports nutritionist".
   - Irish cycling media: Stickybottle has already covered her Gran Fondo title.
   - Ask the Wicklow 200 partner page to link to her, and every club she gives a talk to.
   - Coming with the Cigala launch: the 7 Vivify articles on the Cigala Coaching blog (on staging now) carry canonicals pointing to vivifysports.com, plus Marine's links on the Coaching Nutrition page.

## Growing the international audience: next steps

The online page (€ and US$ prices, video calls, clients in four countries) is the hub. In order:
1. **Language versions**, if Marine works in other languages: she has a French name and did her MSc in Madrid, but I haven't assumed either. French, Italian or Spanish pages with hreflang open whole new markets with far less competition than English. Ask her.
2. **Women's cycling nutrition**: page added (`/womens-cycling-nutrition`). Marine to confirm she wants to offer it and check the wording.
3. **Gravel / ultra nutrition**: event-led pages (Traka, Unbound, gravel worlds), building on her world title.
4. **Country pages (UK, USA)**: only once Search Console shows impressions from those countries. Before that they would be thin copies and can hurt.

## Measuring it

Register Search Console when the WordPress site goes live, and submit the Yoast sitemap. Each month, track the positions of:
- sports nutritionist Ireland;
- cycling nutritionist (Ireland);
- triathlon nutritionist;
- online sports nutritionist;
- sports nutritionist Dublin;
- Marine Lenehan.
