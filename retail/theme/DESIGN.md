# DESIGN.md: Cigala Cycling Retail

The design contract for the Cigala Cycling Retail store theme (Horizon base). It follows the approved Cigala brand kit, `BRAND.md` in the cigala-websites repository, approved by Matteo Cigala in November 2026. When the two differ, the brand kit wins.

## Brand overview

- **What we sell:** Ireland's specialist shop for premium cycling and triathlon gear: power meters, smart trainers, wheels, frames, Garmin/Wahoo electronics, wetsuits and components. It ships across Europe.
- **Who buys:** serious amateur and racing cyclists and triathletes who know the kit they want and compare on price, delivery time and trust.
- **How it should feel:** the same club as cigalacycling.com, Tours and Coaching. Dark, technical and confident, a racer's shop rather than a lifestyle boutique.

## Design thesis

Racing-night black and contour lines, with white Anton capitals for the shouting and Montserrat for the facts. Green means "buy" and red only ever points.

## Colors

| Name | Value | Token / setting | Role |
|---|---|---|---|
| Ground | #08090a | `color_palette.background`, `page_background_color` | Every page |
| Panel | #0f1011 | `color_palette.color2`, drawers, inputs, popovers | Cards, boxes, drawers |
| Hairline | #2b2c2d (≈8% white) | `color_palette.color3` | Borders, dividers |
| Strong hairline | #3a3b3c (≈14% white) | secondary button and input borders | Outlined buttons, inputs |
| Heading text | #f7f8f8 | `color_palette.foreground` | Headings, prices |
| Body text | #d0d6e0 | `color_palette.color1`, `page_text_color` | Paragraphs |
| Secondary text | #8a8f98 | CSS `--cc-text-3` | Captions, meta |
| Action green | #009a44 | primary button, selected variant | Buttons, focus, heading bar |
| Green text | #34c46a | CSS `--cc-green-text` | Green words on black, link hover |
| Accent red | #E10600 | sale badge, current menu underline | Small accents only |
| Red text | #ff3d33 | CSS `--cc-red-text` | Eyebrow labels |
| Gold | #f0bf00 | review stars | Stars only |

## Typography

- **Anton 400** (`anton_n4`): h1–h3, always UPPERCASE. Use it only at 20px and up: h1 72px desktop, h2 48px, h3 24px. Fallback: Impact, "Arial Narrow", sans-serif.
- **Montserrat** 400/600 (`montserrat_n4`, `montserrat_n6`): everything else.
  - Body text is 15px, line-height 1.6.
  - Buttons are 14px semibold.
  - Eyebrows are 12px semibold UPPERCASE, letter spacing .14em, in red text.
- Headings use `text-wrap: balance`.

## Spacing and composition

- Page width "normal" (~1200px content). Side gutter at least 16px on phones.
- Section rhythm is 72px on desktop and 56px on phones.
- **Nothing touching:**
  - at least 10px from eyebrow to heading
  - 14px from heading to the green bar
  - 16px from the bar to the text
- Corners: 12px for cards, panels and product images. 8px for buttons and inputs. 999px for pills and badges.
- Background: the topo contour tile under a 60% dim, scrolling with the page:
  `linear-gradient(rgba(8,9,10,.6),rgba(8,9,10,.6)), #08090a url(topo-background-tile.svg) top center / auto 3000px repeat-y`
- Never put the contour behind photos. Product media sits on its own panel.

## Components

- **Header:** square logo top left at 58px (48px on phone), with no brand text next to it.
  - Menu in Montserrat 12.5px semibold UPPERCASE.
  - Hover: the word turns green-text with a 2px green underline. The current page gets a 2px red underline.
  - Bar background is #08090a at 88% with a blur and a hairline bottom border.
- **Footer:** logo at 76px, the tagline in Anton, link columns and a legal line with the company details: Cigala Cycling Ltd, Reg. No. 675577, VAT IE3699893CH.
- **Primary button:** green fill, white text, 8px corners, 14px semibold. One per area where possible.
- **Secondary button:** dark fill with a strong hairline outline. On hover the border turns green.
- **Section heading:** red eyebrow, then the Anton heading, then a green 40×3px bar.
- **Product card:** panel fill, hairline border and 12px corners. The image sits on its own panel. Title is Montserrat 600. The price is in white; the sale price is white with the compare-at price struck through in secondary text, plus a red "Sale" badge.
- **Badges:** pills, uppercase Montserrat 600. Sale is red; sold out is a panel with a hairline.
- **Inputs:** panel fill, strong hairline and 8px corners. Text is **16px** so iPhones don't zoom in. Focus shows a 2px green ring.
- **Drawers and popovers:** panel fill with a hairline border.

## Dos and don'ts

- Do keep every page dark, and keep one H1 per page.
- Do give every image alt text, and keep the existing alt text.
- Do use green only for "do something", red only for small pointers, and gold only for stars.
- Don't use red for big blocks, backgrounds or Italian-flag stripes.
- Don't recolour, round or add a shadow to the logo.
- Don't put text straight on the contours if it's longer than a short paragraph. Use a panel.
- Don't load tracking before cookie consent. The chat stays usable before consent.

## Motion

Quiet and quick. Hover changes are colour and underline over 150ms, product images scale up to 1.04 over 600ms, and nothing bounces. Everything respects `prefers-reduced-motion`.
