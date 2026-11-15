# Shared cookie banner (all Cigala sites)

Every Cigala site uses this one banner, so it looks and behaves the same everywhere. Don't copy it and restyle it per site. Render it with `render.py`, so the text, colours and behaviour stay identical. Only the IDs change from site to site.

## Look

- A dark bar fixed to the bottom of the screen: `#0f1011`, with a 1px `rgba(255,255,255,.14)` top border. Montserrat 14px, text `#d0d6e0`.
- The text: "We use cookies for website analytics (Google Analytics), advertising (Meta Pixel) and our live chat, to improve your experience. You can accept or reject them." It ends with a Privacy policy link.
- The buttons:
  - **Reject:** outlined, transparent background.
  - **Accept:** solid brand green `#009a44`, `#00b350` on hover.
  - Both have an 8px radius. Reject comes first, then Accept.
- A green "Chat with us" pill sits bottom right. It moves up while the banner is showing.
- A "Cookie settings" link in each site's footer (`<a href="#" data-cc-settings>`) reopens the banner.

## Behaviour

- **Before a choice:** no Google Analytics cookies and no Meta Pixel. Google Consent Mode v2 starts as denied.
- **Accept:** saves `cc_consent=granted`, updates consent to granted, loads the Meta Pixel and records a PageView, and loads the OpenWidget chat.
- **Reject:** saves `denied`, keeps Analytics disabled, and revokes the Pixel if it was loaded.
- **The chat works before consent:** "Chat with us" loads OpenWidget only when the visitor clicks it.
- **Events:**
  - The Elementor form `submit_success` sends `generate_lead` to Analytics and `Contact` to Meta.
  - The newsletter sends `sign_up` to Analytics and `Lead` to Meta (in each site's newsletter code).

## Per site

| Site | GA4 ID | Meta Pixel | OpenWidget org |
|---|---|---|---|
| cigalacycling.com | G-955J6LHQ2P | 1986332861692106 | 43e5f685-37fc-4f78-9420-122fd2a3c5e3 |
| tours.cigalacycling.com | G-QRF16ZZVDB (from the live site) | 1986332861692106 (new on this site, only once Matteo confirms) | check the live site's footer scripts |
| coaching.cigalacycling.com | G-E1WWZCLBRB (from the live site) | 1986332861692106 (new on this site, only once Matteo confirms) | 43e5f685-37fc-4f78-9420-122fd2a3c5e3 (see coaching/TRACKING.md) |

The Pixel is Matteo's single Meta Pixel. In November 2026 it was installed only on cigalacycling.com; live Tours and Coaching had no Pixel. Add it to a site only after Matteo confirms. Until then, render the banner without it: pass `pixel_id=''`, and drop "advertising (Meta Pixel)" from the banner text. Always confirm IDs against the live site before building, and keep every existing tag. If a live site has a tag not listed here, ask Matteo, then gate it behind consent the same way.

## Installing on a WordPress staging site

1. `banner(ga_id=...)` goes in an HTML widget inside the site's footer template, as on cigalacycling.com (`tools/build_wp.py`).
2. `head-snippet.html` goes in Elementor → Custom Code, location head, condition "entire site". It re-grants consent for visitors who already accepted.
3. `wpcode-header-line.html` must be the **first line** of the WPCode Header box, above the existing GA tag. Matteo pastes it himself in wp-admin. Check it in the page source: `consent','default'` must come before `gtag/js`.
4. Remove the site's old cookie plugin or banner script, so only this banner shows.
5. Test with the Playwright checks in `tools/` (`dlcheck.js`, `pxcheck.js`):
   - Before a choice: no Pixel.
   - Accept: Pixel loads and consent updates.
   - Reject: nothing loads.
   - Check at phone and desktop widths.
