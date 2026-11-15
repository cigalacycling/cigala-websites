# Apps and theme features on retail.cigalacycling.com

Inventory taken 15 Nov 2026 for the move to a new theme. It's built from three sources:
- the apps installed on the store (Admin API)
- the app embeds and snippets in the live theme "NEW District"
- what actually loads on live pages (home, a collection, a product)

## Installed and in use: must work on the new theme

| App | What it does on the store | How it's wired in today | On a new theme |
|---|---|---|---|
| **Translate & Adapt** (Shopify) | Store in en/fr/de/it/es/nl | Shopify-native, plus old Langify v2 code still in the theme (see below) | Works natively. Needs a language selector in the header |
| **Selecty** | Language/currency selector | App embed (on) | App embed; or use the new theme's built-in selector and drop the app |
| **Judge.me Reviews** | Product reviews and stars | App embed (on) | App embed plus a review block on product pages |
| **Klarna On-Site Messaging** | "Pay in 3 with Klarna" on products/cart | Theme code | App block on the product page |
| **humm (flexifi)** | Finance messaging | Theme code / description text | Check with Matteo: keep or drop? |
| **Labeler** | Product badges (sale, new, etc.) | App embed (on) | App embed |
| **STOQ** (Restock Rocket) | Back-in-stock alerts, pre-orders | App embed "back-in-stock-restock-alerts" (on) | App embed |
| **Ordersify: Restocked Alerts** | Back-in-stock alerts (second app doing the same job) | Snippet `ordersify-bis` in `<head>` | **Duplicate of STOQ.** Pick one |
| **Ordersify: Order Printer** | Invoices/packing slips | Admin only | Nothing to move |
| **Hextom Shipping Bar** | Free-shipping progress bar | Snippet in theme | App embed, or a built-in announcement bar |
| **Hextom Sales Boost** | Upsell/urgency widgets (`hextom_usb_main`) | Snippet in theme | Check if still wanted |
| **Brevo PushOwl** | Web push notifications | App embed (on) | App embed. Must respect cookie consent |
| **tawk.to Live Chat** | Chat bubble | Loads on every page | Keep, or switch to Shopify Inbox/the same chat as the other sites? |
| **Shopify Messaging / Inbox** | Shopify chat | App embed (**off**) | Off today |
| **Flow** | Shopify automations | Admin only | Nothing to move |
| **Revolut Payment Gateway** | Checkout payment | Checkout only | Nothing to move |
| **Pricefy** | Price monitoring | Admin only | Nothing to move |
| **JDM integration** | Unknown (no handle) | – | Ask Matteo what it is |

## Tracking in the theme code (must move behind cookie consent)

- Google Tag Manager `GTM-5D9TJGX5`, hard-coded in `<head>`
- Google Ads `AW-806343489`, hard-coded in `<head>`
- On the new theme, load these through Shopify's Customer Privacy API / Google & YouTube app, only after consent.

## Leftovers from uninstalled apps: don't carry over

| Leftover | Notes |
|---|---|
| **Booster SEO** (`booster-seo`) | Uninstalled. This is why titles went missing; fixed by `seo-meta` on the staging copy |
| **MLveda currency switcher** (`mlveda-*`) | Uninstalled. Shopify says "not rendered" |
| **Langify v2** (`ly-*` snippets, wraps the whole `theme.liquid`) | Not in the installed list but its code still runs on every page. Replaced by Translate & Adapt |
| **BSS Product Labels** (`bss-*`) | Not installed. Old code still included |
| **Sections Pro** (`sections-pro`, `section-any-where`, 612 sections) | Not installed; CSS/JS still loads from tc.cdnhub.co. Its 612 saved sections (307 "featured text", 145 video, 115 hero…) hold content on product/collection pages. **That content needs checking before we drop it** |
| **Weglot / GTranslate** | Only in the 2020 backup theme |

## Theme templates in use

Product templates `product` and `product.pre-order`, plus collection, collection list, page, page.wide, contact, blog, article, cart, search, 404, gift card and customer account pages.

## Matteo's answers (15 Nov 2026)

1. Back-in-stock: keep **both** STOQ and Ordersify.
2. Chat: keep **tawk.to** on the shop.
3. humm finance and Hextom Sales Boost: keep **both**.
4. "JDM integration" is the **distributor connection. Keep it.** It's admin-side, so nothing to move in the theme.
5. Sections Pro content: bring it across **if possible**, but it's not essential.
