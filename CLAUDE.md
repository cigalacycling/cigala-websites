# Instructions for Claude

Read `README.md` first: it has the folder map, build/push steps, page IDs and current status. Read `BRAND.md` before designing anything.

Rules that always apply:
- Work only on Hostinger staging sites, never on the live sites. Going live is done together with Matteo.
  - **Exception, cigalacycling.com only (Matteo, 16 Nov 2026, after go-live):** test every change on staging first, then apply the same change to the live cigalacycling.com through the REST API, so staging and live stay identical. Back up what you change first (`live/backup/`). Don't publish staging over live from Hostinger any more. Titles, descriptions, headings and body copy still need Matteo's OK. Tours and Coaching stay staging-only unless Matteo says otherwise.
- Never lose SEO, only improve it. Crawl the live site with `tools/crawl.py` before changing anything, and compare against that crawl after. Keep these unchanged:
  - URLs
  - Yoast titles and meta descriptions
  - H1/H2 wording (only changes Matteo approved)
  - body copy
  - image alt text
  - sitemaps
  - structured data
- Never ask for passwords in chat. Credentials are saved on the cloud environment for the staging host only.
- Images: WebP at quality 90 from the largest original, with descriptive alt text. Keep any existing alt text.
- Tracking must load only after cookie consent: Google Analytics, the Meta Pixel and any other tag. The chat stays usable before consent.
- Use the right company for each site (`shared/BUSINESS.md`). Tours is run by Cigala Cycling Tours Ltd; the brand site, Coaching and Retail by Cigala Cycling Ltd. Each has its own Google reviews link.
- Every site uses the shared cookie banner in `shared/consent/`, rendered with that site's IDs. Follow its README. Don't restyle it or use a different cookie plugin.
- Check every page at 390, 820 and 1440 px wide: no sideways scrolling, one H1 per page.
- Form fields use 16px text, so iPhones don't zoom in.
- Commit finished work to this repository so the next session can carry on.
- Coaching athlete hub: built on staging; it goes live only by following `coaching/athlete-area/GO-LIVE.md`, with Matteo.
