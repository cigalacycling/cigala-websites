# Athlete hub ↔ Matteo's laptop (Vekta tools, season plan, availability inbox, reviews)

Answer to the Vekta "Season Plan" chat brief (HUB-REQUEST.md, 17 Nov 2026), from the cloud "athlete availability" chat, which builds and owns the hub.

**Status (17 Nov):** live on `https://coaching.cigalacycling.com` since 17 Nov (staging has the same, for tests). Use a **live** application password for the live site. Earlier note: everything below was built and tested on **staging** (`https://staging.coaching.cigalacycling.com`), which only has test athletes. It goes live on `https://coaching.cigalacycling.com` when Matteo puts the new athlete area live, together with the cloud chat. Until then the live site does not have these routes: build and test against staging.

## Auth (every route)
- WordPress **application password** for Matteo's admin user (wp-admin > Users > Profile > Application Passwords). One for staging, one for live.
- Kept on the laptop only (`vekta\.env`). Never in chat, never in a repository.
- Sent as HTTP Basic auth: `user:application-password`.
- All routes need an editor or admin. Athletes can't call them.

## Matching athletes (brief §5)
- Every athlete has a hub account. Its email is the login.
- Vekta has no email, so: match by full name once, Matteo confirms, then store the **Vekta user id** on the account with `POST /cc/v1/athlete-meta` (below). From then on, use `vekta_id` everywhere.
- Matteo can also type it in wp-admin > Users > the athlete > "Vekta user id".
- A Vekta id can be on only one account; a duplicate is refused (409).
- Any route that takes an athlete accepts **one** of: `vekta_id`, `email`, or `page` (the hub's athlete page id, `page` in the read route).

## Routes

| Route | Method | What |
|---|---|---|
| `/wp-json/cc/v1/athletes` | GET | Everything per athlete (read only). |
| `/wp-json/cc/v1/athlete-meta` | POST | Set `vekta_id` and/or `nationality` on an athlete, after Matteo confirms. |
| `/wp-json/cc/v1/report` | POST | Send a season plan, report or guide. Always a **draft**. |
| `/wp-json/cc/v1/reports` | GET | List drafts and published reports (`?email=` for one athlete). |
| `/wp-json/cc/v1/availability` | GET | Availability only (older route, still there). |
| `/wp-json/cc/v1/goals` | GET | Goals & events only (older route, still there). |
| `/wp-json/cc/v1/profile` | GET | The rider form answers (`?email=`). Contains health answers: keep them on the laptop only, never in a report. |

### GET /cc/v1/athletes (brief §3, §4, §5)
- Query (all optional):
  - one athlete: `?vekta_id=` or `?email=` or `?page=`;
  - `?since=<unix time>`: only athletes whose availability, goals or form changed after that;
  - `&former=1`: also include former athletes (coaching ended).
- Returns a list. Each item:
```json
{
 "page": 7472, "status": "active", "ended": null,
 "name": "Testa Prova", "first_name": "Testa", "last_name": "Prova", "email": "…",
 "vekta_id": "12345", "language": "pt", "nationality": "IE", "nationality_name": "Ireland",
 "form": {"status": "signed", "signed_at": 1794870000, "kind": "full"},
 "availability": {"data": {"week": {…}, "changes": […], "note": "…", "voice": […]}, "updated": 1794870000, "status": "new"},
 "goals": {"short": "…", "long": "…", "events": […], "from_form": "…", "updated": 1794870000, "changed_by": "athlete", "status": "seen"},
 "season_published": {"id": 7502, "at": 1794880000}
}
```
- `status: "new" | "seen"`: "seen" once Matteo has opened that board in the hub ("Availability" or "Goals & events") after the change. The route itself never marks anything as seen.
- `changed_by: "matteo"` means Matteo edited the goals from his coach view.
- `form.status`: `waiting` (not started), `started`, `signed` (full form), `updated` (short update, paper form on file), `unlocked` (Matteo opened the hub without the form).
- Former athletes: `status: "former"`, `ended` (time); no email, language or Vekta id (the login is gone).
- The health answers are deleted when coaching ends (privacy policy), and the whole record two years later.

### Final field names (brief §3, §4)
- **language**: one per athlete. Matteo picks it when he creates the login; the athlete can change it in the form and the hub. It's a 2-letter code; the hub is fully translated in `en`, `it`, `pt`, `sl`. Stored as user meta `cc_lang`. **The hub's language, reports and emails follow it.**
- **nationality**: only for the small flag next to the name in Matteo's list.
  - ISO 3166 code, upper case in the route (`IE`, `IT`), plus `GB-ENG`, `GB-SCT`, `GB-WLS`, `GB-NIR`.
  - The athlete's own answer in the rider form wins (`nat` in the profile); otherwise the one set with `athlete-meta` (page meta `cc_nat`).
- **vekta_id**: user meta `cc_vekta_id` (string).
- **Availability** (`availability.data`):
  - `week`: per day `mon`…`sun` → `{"h": hours, "w": windows}`.
    - `h`: `""` = not set, `"0"` = rest day, `"0.5"` = 30 min, `"1"`, `"1.5"`, `"2"`, `"3"`, `"4"` (4h+).
    - `w`: when they can ride, any of `am` (morning), `mid` (lunch), `pm` (evening).
  - `changes`: trips and other dated changes `{"from","to","days","type","h","text"}`.
    - `to: ""` means no end date; `days: []` means every day.
    - `type` is one of:
      - `away`: away, no bike;
      - `bike`: away, bike with me;
      - `indoor`: indoor trainer only;
      - `gym`: gym only;
      - `less`: less time;
      - `more`: more time;
      - `other`.
    - `h` is the time a day for that change. Changes whose end date has passed are dropped.
  - `note`: free text to Matteo.
  - `voice`: `[{"text": transcript, "at": time, "url": private link (opens only for Matteo)}]`. This is the **notes to Matteo, with voice**.
- **Goals & events** (`goals`):
  - `short` (1 year) and `long` are free text.
  - `events`: `[{"name","date":"YYYY-MM-DD","type":"race|sportive|camp|other","prio":"A|B|C","dist","elev","note"}]`.
  - `prio` is **the athlete's** priority (A = main goal, B = important, C = training race). Athletes add events and change the priority of listed ones in the hub.
  - Matteo's own priority lives in the season plan on the laptop. Keep using his until he agrees to the athlete's change.
  - `from_form`: races typed on an old paper form, plain text, for Matteo to turn into events.
  - Goals have no date field: the short-term goal is "1 year"; a dated target belongs in an event.

- **Race routes (17 Nov):** `goals.events[]` may also have the following fields:
  - `start` (`"HH:MM"`);
  - `route_type` (gpx/fit/tcx/link), `route_name`, `route_link`, `route_id`;
  - `route_url` (a private hub link, or the link itself);
  - `route_file_api` (`GET /cc/v1/route?id=` returns `{id, name, type, size, base64}`, coach only);
  - `route_at` (time the route was added or changed).

  Athletes upload the route in Goals & events (`POST /cc/v1/goals/route`, `.gpx`/`.fit`/`.tcx` up to 15 MB, content checked).
  Matteo's Reports-board switch "Publish race plans automatically" (option `cc_r_race_auto`) publishes `race-sim`/`race-plan` reports straight away.

### POST /cc/v1/athlete-meta
```json
{"email": "…", "set": {"vekta_id": "12345", "nationality": "IE"}}
```
- Use `email`, `page` or `vekta_id` to pick the athlete.
- Send only what changes. `""` clears a value.
- Answer: the athlete, as in the read route.
- Errors:
  - 404: no such active athlete;
  - 409: Vekta id already on another athlete;
  - 400: unknown nationality code.
- **Only after Matteo has said yes to the match.**

### POST /cc/v1/report (brief §1, §2, §6)
```json
{"vekta_id": "12345", "type": "season", "title": "Season plan 2027", "html": "<!doctype html>…", "note": "optional, for Matteo"}
```
- **Athlete:** `vekta_id`, `email` or `page`.
- **`type`:**
  - `season`: the season plan / periodization;
  - `prediction`: race prediction (live page, see below);
  - `snapshot`: training snapshot (live page, see below);
  - `race-sim`: race day simulator, one per race;
  - `assessment`: initial assessment;
  - `review`: e.g. the 6-month review before renewal;
  - `race-plan`;
  - `progress`: progress report;
  - `guide`: a resource for this one athlete;
  - `other`.
- **`title`:** optional. Without it the athlete sees the kind and month in their language, e.g. "Revisão · maio 2027".
- **`key`** (optional, 17 Nov, staging + live): one current report per athlete + type + key. Use the race slug for `race-sim` / `race-plan` (e.g. `"etape-2027"`), and `"training-report"` with `type: "progress"` for the Training Response Report. A new draft with the same key replaces an unpublished one (`replaced_drafts`); when Matteo publishes it, it replaces the published one with that key. Ignored for `season` (season plans keep their history). Leave it out to always add, as before (reviews, assessments). Normalised to a lower-case slug, max 80 characters.
- **Content:** `html` (one self-contained page) **or** `pdf_base64` **or** `url` (https link). Maximum 12 MB. Your 200 KB season page is fine.
- **Answer:** `{"ok": true, "id": 7502, "status": "draft", "replaced_drafts": [7500], "preview": "…", "review": "…/athletes/?board=reports"}`.
- **Always a draft.** Nothing reaches the athlete until Matteo presses Publish in the hub's Reports board. He can tick "Email the athlete": on by default for everything except season plans.
- **Season plan, replace in place:**
  - The athlete always sees **one** season plan, the latest published, in "Your season" at the top of their hub.
  - It's shown full width in the page (an `<iframe>` with `sandbox="allow-scripts allow-popups"`, about 720px tall), so zoom, hover pop-ups and the race-priority picker work. There's also an "Open full screen" button.
  - A new season draft deletes any older **unpublished** season draft for that athlete (`replaced_drafts`).
  - When Matteo publishes it, it replaces the previous one; earlier published plans move to "Earlier reports" as history.
- **Other reports:**
  - The newest of each kind sits on top; every race plan stays on top.
  - Older ones fold under "Earlier reports".
  - "New" badges clear once the athlete opens a report.
- **HTML rules:**
  - The page runs sandboxed, with no access to the site or the athlete's login: no `fetch` to the hub, no cookies, no forms that post.
  - Inline CSS/JS. Google Fonts and CDN images are fine.
  - Links open in a new tab (`target="_blank"`).
  - The race-priority picker in the season page can't save into the hub. Make it send the athlete to `https://coaching.cigalacycling.com/athletes/#goals` (open in a new tab), where they change it.

### Pages athletes open every day (Matteo 17 Nov): one per athlete, always the latest
Matteo wants each athlete to find these in the hub straight away, kept up to date by the laptop.
They're not the one-off reports: the assessment and the 6-month review stay normal reports.

| `type` | Shown to the athlete as | How many |
|---|---|---|
| `season` | "Your season": the periodisation, shown inside the hub (scripts on), "Open full screen" | 1 current; earlier versions kept as history |
| `prediction` | "Race prediction" card under the season plan | 1 current (the old one is deleted) |
| `snapshot` | "Training snapshot" card under the season plan (snapshot data, fitness, recent load…) | 1 current (the old one is deleted) |
| `race-sim` | "Race day simulator", in "Your reports", always on top | one per race |
| `race-plan` | "Race plan", in "Your reports", always on top | one per race |

**Automatic updates.** The first `season` / `prediction` / `snapshot` for an athlete arrives as a draft. Matteo publishes it with "Keep it updated automatically" (ticked by default).
- From then on, every new version you send for that athlete and type goes **live straight away**, replacing the previous one. The answer says `"status": "published", "auto": true`.
- No email goes to the athlete for these.
- Matteo can press "Stop automatic updates" at any time; then they're drafts again.
- `GET /cc/v1/athletes` → `live_pages` shows, per type, the latest published page and whether `auto` is on.

**Suggested schedule:**
- `snapshot`: once a day, after the Vekta sync;
- `prediction`: when it changes;
- `season`: when the plan changes.

**A link instead of a page:** send `"url": "https://…"` (no `html`/`pdf_base64`) if the page lives somewhere else. The athlete opens it from the hub after logging in. Prefer `html`: it stays private inside the hub, whereas a public link can be seen by anyone who has it.

### Race priority colours (Matteo 17 Nov): A gold, B silver, C bronze
On every page (season plan / periodisation chart, race prediction, race simulator, the "Your races and goals" box), colour races by priority:
- **A** (main goal): gold `#D4AF37`;
- **B** (important): silver `#C0C4CC`;
- **C** (training race): bronze `#CD7F32`.

Badges use a gradient: A `#F3D774 → #D4AF37 → #A8841F`, B `#F2F3F5 → #C0C4CC → #8E939C`, C `#E9A86B → #CD7F32 → #9A5A1F`, with dark text. Brand green is only for buttons. The hub already uses these; full table in `BRAND.md`.

### Every page in the athlete's language, with their flag (Matteo 17 Nov)
- **Language:** write every page you send (season plan, prediction, snapshot, race simulator, race plan, reports, guides) in the athlete's `language` from `GET /cc/v1/athletes`.
  - The hub is fully translated for `en`, `it`, `pt`, `sl`; for any other code, write in English.
  - Dates and numbers in that language's style (e.g. "24 abr 2027" in Portuguese).
- **Flag:** put the athlete's flag on every page, small, next to their name in the page header.
  - Use `flag_emoji` from the read route: the nationality flag, or the language's flag while the athlete hasn't given a nationality yet; `null` for English with no nationality, so no flag.
  - In HTML, show it as text, e.g. `<span class="flag">🇮🇪</span>`.
- **Titles:** send a `title` in the athlete's language, or leave it out and the hub names it ("Previsão de prova · novembro 2026").

### Resources (brief §6)
What the hub has for athletes:
- **Per athlete:**
  - reports and guides sent with `/cc/v1/report` (`type: "guide"` for a resource), draft then published by Matteo;
  - PDFs Matteo uploads into an athlete's page in wp-admin.
- **For everyone (shared hub, one per language):**
  - quick links (catch-up call, nutrition, WhatsApp, Skool), the Vekta calendar button, training guides (PDFs), training tools (calculators), and reading (latest blog posts plus chosen articles).
  - These are built by the cloud chat from `tools/coaching_athlete_area.py`. **The laptop does not edit them.** To add a shared resource, Matteo tells the cloud chat (send it the file or link).

## What the laptop must not do (brief "Send back" §4)
- Don't write anything to an athlete without Matteo: reports are drafts by design; never publish them yourself.
- Don't write into Vekta without Matteo's yes (unchanged).
- Don't edit the hub's code, its Code Snippet, the shared hub pages, or athletes' WordPress accounts. The only writes allowed are `POST /cc/v1/report` (drafts) and `POST /cc/v1/athlete-meta` (after Matteo confirms).
- Don't delete anything through the API. Ending coaching and deleting data are Matteo's buttons in the hub.
- Don't put health answers (`/cc/v1/profile`) in any report or page an athlete or anyone else sees. Don't keep them after coaching ends.
- Never put the application password in chat, a repository or a page.
- Athletes only ever see motivating, athlete-friendly things: never the weekly plan, early warnings or compliance counts.

## Vekta calendar sync (unchanged, Matteo 16 Nov)
- Uses Matteo's existing Claude–Vekta connection. The website holds no Vekta key.
- Twice a day (about 06:00 and 18:00 Irish time), read `GET /cc/v1/athletes?since=<last run>`, then write notes into each athlete's Vekta calendar (matched by `vekta_id`).
- **Which days get a note:**
  - each day a change covers (only its `days`);
  - for a change with no end date, the next 8 weeks;
  - one note on the next Monday when the usual week changes;
  - events on their date.
- **Removing:** remove or update a note when its change or event is edited or removed. Keep a record of what was written where.
- **Vekta item type for each case:** still open. Tell Matteo which Vekta calendar item fits (e.g. away = unavailable day, race = event).

## Season page: the old add-event form
The season page's "Please add any event here / Send to Matteo" form goes. In its place, a read-only "Your races and goals" box:
- the design is `coaching/athlete-area/mockup/season-races-box.html` in the cigala-websites repo;
- it lists the athlete's events from the read route, with a button "Add or change in your athlete hub" → `https://coaching.cigalacycling.com/athletes/#goals`.
