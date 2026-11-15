# retail.cigalacycling.com: launch checklist for the new Cigala theme

- **New theme:** "STAGING – Cigala brand (Horizon)", `gid://shopify/OnlineStoreTheme/193220739396`
- **Preview:** https://retail.cigalacycling.com/?preview_theme_id=193220739396
- **Live today:** "NEW District" (old design)

Nothing here has been done on the live store. Publishing is done together with Matteo.

## Before launch day

**Matteo (in Shopify admin, a few minutes each):**
- [ ] **Check Klarna and humm on the preview in your own browser.** Open any product. Under "Add to cart" you should see the Klarna message and the humm widget. The cloud test browser can't load these, so this needs a real browser.
- [ ] **Check the cookie banner from Ireland.** Open the preview in a private window. The dark bar should show at the bottom. Nothing from Google should load until you press Accept: in Chrome, DevTools → Network → filter "googletagmanager" shows nothing before Accept.
- [ ] **Cookie banner wording** (Settings → Customer privacy → Cookie banner → Customize). To match the other sites, use: *"We use cookies for website analytics, advertising and our live chat, to improve your experience. You can accept or reject them."* The design already matches. The wording can only be changed in the admin.
- [ ] **Notification emails** (Settings → Notifications → Customize email templates):
  - Logo: upload `cigala-cycling-retail-logo.png` (it's in Files). Logo width: 120px.
  - Accent colour: `#009a44` (Cigala green).
  - Save, then send yourself a test order confirmation.
- [ ] **Privacy policy:** approve `retail/PRIVACY-DRAFT.md`. Then it can be pasted into Settings → Policies → Privacy policy.

**Page content fixes (your OK needed; these change live pages, not the theme):**
- [ ] **About us:** 2 photos have no alt text. Suggested alt: "Cigala Cycling team riding in the black team kit" for both. Check the photos and adjust.
- [ ] **Bike to Work Scheme:** 1 image (the scheme logo) has no alt text. Suggested: "Bike to Work scheme logo".
- [ ] **Finance:** the page body contains a second H1 ("humm by flexifi. for little things…"). Make it an H2. The wording stays the same.

## Launch day (together)

1. Publish the new theme (Online Store → Themes → "STAGING – Cigala brand (Horizon)" → Publish). The old theme stays in the library as a backup.
2. Checkout branding (Settings → Checkout → Customize). This goes live immediately, so it's done right after publishing:
   - Logo: `cigala-cycling-retail-logo.png`, left aligned, small.
   - Main colour / buttons: `#009a44`. Accent: `#009a44`. Errors: `#E10600`.
   - Background: white for the form, `#08090a` for the header bar (or keep it all light if that reads better; check on a phone).
   - Fonts: Montserrat for body text. Headings in Montserrat 600 (Anton isn't offered at checkout).
3. Re-crawl the live store (`tools/crawl_shopify.py`, or `tools/crawl_preview.sh` without a preview id) and compare with `retail/baseline-live-pages.json` (`tools/compare_preview.py`).
4. Place a test order with a 100% discount code: cart drawer, checkout, confirmation email, back-in-stock button on a sold-out item, and reviews on a product page.
5. A week later, delete the old unused themes (Debut, Venture, Simple, Minimal, District, demos). Keep "NEW District" and "Back up 17/11".

## Black Friday

- **"STAGING – Black Friday (Cigala)":** a copy of the finished theme with the Black Friday look. Publish it on Black Friday morning. After Cyber Monday, publish "STAGING – Cigala brand (Horizon)" again. Both stay in the theme library, so switching back is one click.
- The Black Friday copy has to be refreshed if the main theme changes after it was made.
