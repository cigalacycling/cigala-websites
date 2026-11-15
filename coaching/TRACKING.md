# coaching.cigalacycling.com: tracking on the live site (15 Nov 2026)

Checked in all 76 saved pages (`coaching/html/`) and with a live page load in Playwright, before any consent click.

| Tag | Live coaching site | Notes |
|---|---|---|
| Google Analytics 4 | **G-E1WWZCLBRB** on 76/76 pages | Plain `gtag.js` in the head, loaded on page load. No Consent Mode default, so it isn't gated by consent today. Matches `shared/consent/README.md`. |
| Meta Pixel | **not present** | There's no `fbq` / `fbevents.js` on any page. The shared banner uses Matteo's Pixel 1986332861692106 on every site, so adding it to Coaching is new tracking. **Matteo confirmed on 15 Nov (in the Tours chat) that the same Pixel goes on Coaching.** |
| OpenWidget chat | org **43e5f685-37fc-4f78-9420-122fd2a3c5e3** on 76/76 pages | The same org as cigalacycling.com. |
| Cookie banner | Elementor cookie-consent bar in footer template 228 | Text: "This website uses cookies to ensure you get the best experience on our website." It has a "Got it!" button and a "Learn more" link, and no Reject. It doesn't block anything. To be replaced by the shared banner (`shared/consent/`). |
| Other (GTM, Google Ads, Hotjar, Clarity, TikTok, LinkedIn, Pinterest, reCAPTCHA, Brevo) | none found | |

Hosts requested on a fresh load of the homepage: `www.googletagmanager.com`, `api.openwidget.com`, `cdn.openwidget.com`, plus the site itself and Google Fonts. No cookies were set before a click in that test.

## For the staging build

- Render the banner with `shared/consent/render.py`, using `ga_id='G-E1WWZCLBRB'`. Follow `shared/consent/README.md`.
- Remove the Elementor cookie-consent bar from footer template 228.
- Matteo pastes `wpcode-header-line.html` as the first line of the coaching staging site's WPCode Header box, above the GA tag.
- Meta Pixel: confirmed. Render the banner with the default `pixel_id` (1986332861692106). It loads only after Accept.
