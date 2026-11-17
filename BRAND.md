# Cigala Cycling

The brand kit for Cigala Cycling, Cigala Cycling Tours and Cigala Cycling Coaching. It covers the websites, tour sheets, Vekta and coaching pages, social posts and anything else made for the brand. Approved by Matteo Cigala, November 2026.

## The look in one line

Near-black pages with a grey topographic contour background, white Anton capitals for headlines, Montserrat for everything else, **green for action**, **red for small accents**, gold only for stars.

## Logos

Logos live in the **Logos** asset group. Always use the files themselves, never a redrawn version.

- **Cigala Cycling square logo** (`cigala-cycling-logo-square.png`): the master logo, a dark square with its thin white border. Use it exactly as supplied: keep the white border, no rounded corners, no shadow, no recolouring.
- **Cigala Cycling Tours square logo** (`cigala-tours-logo-square.png`) and **round logo** (`cigala-tours-logo-round.jpg`): the Tours versions.
- **Website header:** the square logo top left at **58px**, with no brand text beside it.
- **Website footer:** **76px**.

## Background: the topographic contour

The background files are in the **Backgrounds** asset group.

- `topo-background.svg` is the master. It's a sharp vector trace of the original image, with exactly the same lines and the same grey (#313131) on black, and it stays sharp at any size. Never use the old 1336px PNG again.
- `topo-background-tile.svg` is the web version. It repeats down long pages without a visible seam.
- `topo-story-1080x1920.png` is the portrait crop for Instagram and Facebook Stories.

**Rules**
- **Web pages:** lay the background on `bg` (#08090a), then cover it with `topo-dim`, a 60% overlay. It scrolls with the page: `background: linear-gradient(rgba(8,9,10,.6),rgba(8,9,10,.6)), #08090a url(topo-background-tile.svg) top center / auto 3000px repeat-y`.
- **Long text:** put it in a `panel` (cards, boxes) or keep it short where it sits straight on the contours.
- **Tools and documents** (tour sheets, the Pesenti page, coaching and Vekta pages): the same background at 55–60%.
- **Photos and tour cards:** never put the contour behind them.

## Colour

| Role | Token | Value | Rule |
|---|---|---|---|
| Page ground | `bg` | #08090a | Every page is dark. |
| Panels | `panel` / `panel-solid` | rgba(15,16,17,.92) / #0f1011 | Cards and boxes on the background. |
| Hairlines | `border` / `border-strong` | 8% / 14% white | Borders, dividers, outlined buttons. |
| Headings | `text` | #f7f8f8 | |
| Body | `text-2` | #d0d6e0 | |
| Secondary | `text-3` | #8a8f98 | Captions, small labels. |
| **Action** | `green` | **#009a44** | The logo green. |
| Green text | `green-text` | #34c46a | Green words on black. |
| **Accent** | `red` | **#E10600** | Small accents only. |
| Red text | `red-text` | #ff3d33 | Red words on black. |
| Gravel | `gravel` | #b9895a | Gravel tour dot only. |
| Stars | `gold` | #f0bf00 | Stars only. |

**Green means "do something".** Use `green` for:
- primary buttons, with white text;
- the short 40×3px bar under every section heading;
- focus rings;
- the menu hover: the word turns `green-text` and a 2px green line appears under it.

Use `green-text` for green words on black, where #009a44 would be too dark to read.

**Red means "look here", in small doses.** Use `red` for:
- the 2px underline on the menu item of the current page;
- the dot on Road tags;
- the early-bird label.

Use `red-text` for the small uppercase label above a heading (the "eyebrow"). Never use red for big blocks, backgrounds or Italian-flag stripes.

**Gold** is for stars: review ratings, Matteo's titles and the "Event entry guaranteed" badge.

**Tour type dots:** red for Road and Road & Gran Fondo, `gravel` brown for Gravel. Filter chips use the same dots.

## Type

- **Headlines:** **Anton**, always UPPERCASE, only from about 20px up (h1 ~76px, h2 ~48px, h3 ~22px).
- **Everything else:** **Montserrat**. Body text is 15px, intro text 16px and buttons 14px semibold. Eyebrows are 12px semibold UPPERCASE with wide letter spacing.
- Both fonts are free on Google Fonts.

## Components

- **Buttons:**
  - **Primary:** `green` fill, white text, 8px corners. Use it for the main next step ("Book now", "View the full 2027 calendar", "Read our story").
  - **Secondary:** outlined with `border-strong` on a dark fill.
  - One green button per area where possible.
- **Section heading:** red eyebrow, then the Anton heading, then the green 40×3 bar.
- **Spacing:** text never touches the next element. Leave at least 10px between an eyebrow and its heading (18px for the eyebrow pill on a photo), 14px between a heading and its green bar, and 16px between the bar and the text below. Check every new section on phone and desktop for anything sitting too close.
- **Eyebrow on a photo:** red text can't be read over a photo. Put it in a dark pill instead: dark fill, `border-strong` outline, white text and a small red dot in front.
- **Panels:** `panel` fill, `border` hairline and 12px corners.
- **Chips and tags:** 999px pills. Tour type tags carry the coloured dot.
- **Badges:**
  - **Chianti & Strade Bianche only:** the gold "Event entry guaranteed" badge.
  - **Algarve and Tour of Flanders:** a plain dark "Event day fully supported" badge.

## Writing rules

- **Menus and footer links:** use Title Case ("All Tours", "Gran Fondo Tours", "Italian Tours", "Gravel Tours", "Custom Tours"). Write "Gran Fondo" as two words.
- **Phone:** +353 404 78107.
- **Matteo:** his title is "Head Coach & Tours Director". His wins are listed without years, with gold stars:
  - European Road Champion Gran Fondo
  - UCI Gran Fondo Vice World Champion
  - UCI Gravel Vice World Champion
  - Italian Gravel Champion
- **Experience:** "28 years in cycling".
- **Matteo's photo:** use the one in the white Cigala Cycling jersey, cut out with no background, standing on the contour background with a soft green glow.
- **Tour cards:** use the approved 2027 set as it is: 4:5, no text on top, linked to the trip page, with the tour name in the alt text.

## Websites

- **Header:** logo, menu and one green button.
- **Footer:** logo, the tagline in Anton, and links.
- **Headings:** one H1 per page.
- **Every image:** has alt text.
- **Layout:** every page works at phone, tablet and desktop widths, with no sideways scrolling.


## Cookie banner

All Cigala sites use one shared cookie banner (`shared/consent/` in the website repository): a dark bottom bar `#0f1011`, Montserrat 14px, an outlined Reject button and a green `#009a44` Accept button, plus the green "Chat with us" pill bottom right. Never restyle it per site. Only the tracking IDs change.

## Race priority colours (Matteo, 17 Nov 2026)
Used everywhere for A/B/C goals and events: the athlete hub, the rider form, the coach boards, the Vekta season plan / periodisation and every page made for an athlete.

| Priority | Meaning | Colour | Gradient (badges, buttons) | Text on it |
|---|---|---|---|---|
| **A** | main goal | gold `#D4AF37` | `#F3D774 → #D4AF37 → #A8841F` | `#1a1406` |
| **B** | important race | silver `#C0C4CC` | `#F2F3F5 → #C0C4CC → #8E939C` | `#15171a` |
| **C** | training race | bronze `#CD7F32` | `#E9A86B → #CD7F32 → #9A5A1F` | `#1c1006` |

Brand green stays for buttons and actions; gold, silver and bronze are only for race priority.
