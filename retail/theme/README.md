# Theme changes for retail.cigalacycling.com

Changes are made on an unpublished copy of the live theme. They go live only together with Matteo.

## STAGING – SEO titles fix (copy of NEW District)

- Theme ID: `gid://shopify/OnlineStoreTheme/193219133764` (unpublished)
- Preview: https://retail.cigalacycling.com/?preview_theme_id=193219133764
- New file `snippets/seo-meta.liquid` (copy in this folder) outputs the page `<title>` and meta description.
- In `layout/theme.liquid` and `layout/theme_copy_geolocationredirect.liquid`, `{% include 'booster-seo' %}` was replaced with `{% render 'seo-meta' %}`.
- Titles use the format "Name | Cigala Cycling Retail", the same one the Booster SEO app used.
- Descriptions use the SEO description when one is set. Otherwise they use the start of the item's own text, skipping the stock delivery/finance lines at the top of product descriptions.
- Checked on the preview:
  - home, collection, collection page 2, contact page, blog, fr collection, and 15 sampled products: each has 1 title and a clean description
  - the product page at 390px looks the same as live, with no sideways scroll and 1 H1
- Collections and the blog have no description text of their own, so they get a title but no meta description. Adding collection descriptions in the admin would fill these in.

## STAGING – Cigala brand (Horizon)

- Theme ID: `gid://shopify/OnlineStoreTheme/193220739396` (unpublished). This is Shopify's Horizon theme, installed from github.com/Shopify/horizon.
- Preview: https://retail.cigalacycling.com/?preview_theme_id=193220739396
- Design contract: `DESIGN.md` in this folder (to be copied to the theme root).
- Done so far:
  - Theme settings: dark palette, Anton/Montserrat, green buttons, the logo (Files: `cigala-cycling-logo-square.png`, fetched from the staging site), 12px cards, 8px buttons and inputs, red sale badge, cart drawer.
  - `snippets/cigala-brand.liquid`, loaded in `layout/theme.liquid`: contour background, menu hover/current marks, eyebrow and green bar kit, 16px inputs.
- The contour background needs `topo-background-tile.svg` in the store's Files. The rounded-coordinate copy in this folder is 204 KB and looks the same. Matteo uploads it via the upload box, because uploading from this cloud session wasn't allowed.
