# Athlete hub: going live on coaching.cigalacycling.com

> **Done, 17 Nov 2026 (Matteo: "Marine test on the live").** Steps 1–8 and 10's prep done:
> - live snippet 8 was exactly commit 3a811c5, nobody else had changed it; backup in `live-coaching/backup/athlete-snippet-8-2026-11-17.json`;
> - crawl before and after: 101 pages identical (only new URL: /athletes/?cc_forgot=1, noindex);
> - snippet pushed, with all modules (`push_live` = the same body as the staging push);
> - shared hubs EN/IT rebuilt and PT/SL created on live (7488, 7489);
> - languages already right (28 en / 5 it / 1 pt / 1 sl); 32 athletes marked "paper form on file" (no prefill yet); Marine, Tommie and Vittorio get the full form;
> - full test with a temporary athlete and coach, then both deleted (this found and fixed: the single "Delete for good" button, and reports left behind on delete).
>
> **Still to do:**
> - step 9, the welcome emails: Marine first, on Matteo's OK; the others on his "send";
> - step 10: tell the laptop chats;
> - step 11: clean staging.
>
> **Night of 17 Nov, also live:**
> - daily pages from the laptop: season / prediction / snapshot, with automatic updates after Matteo's first publish; race day simulator;
> - guides in Portuguese and Slovenian (12 PDFs, private, in their hubs);
> - email headers in PT and SL;
> - fixes found by a full language sweep (EN/IT/PT/SL at 390/820/1440, no leftovers except the legal texts, which stay English for PT/SL until Matteo approves a translation).
>
> **Welcome emails:** Marine Lenehan's sent 17 Nov (Matteo's OK) for the live test. Nobody else yet: they go on Matteo's "send".
>
> **From now on, every hub change:** test on staging, then push live the same way (back up first).

Everything since 16 Nov evening is built and tested **on staging only** (`staging.coaching.cigalacycling.com`). The live site still has the first, older hub. This is the checklist for putting it live. **Any session doing the go-live follows it, step by step, together with Matteo.**

## Rules
- Only with Matteo's explicit "go", on the day, together.
- **Never publish staging over live from Hostinger.** Live has the 35 real athlete logins and their data; staging has only test athletes. The go-live is a **code (snippet) update plus a few settings**, nothing else.
- Back up first, test after, and tell Matteo what changed.
- **No email to any athlete** until Matteo says "send" (step 9).

## What goes live
The whole `coaching/athlete-area/` code, as one Code Snippet (live snippet id in `live-coaching/athlete-snippet-id.txt`):
- **Main file:** `athlete-area.php`.
- **Modules,** in this order: `hub-i18n.php`, `availability-i18n.php`, `availability.php`, `form-legal.php`, `form-legal-it.php`, `onboarding-i18n.php`, `onboarding.php`, `goals.php`, `passwords.php`, `reports.php`, `pc-api.php`.
- **Features:**
  - rider form / short update with signed PDF, and the hub lock;
  - availability, goals & events;
  - self-service passwords;
  - reports and the season plan from the laptop, with the Reports board and bulk tools;
  - end coaching and delete, with the health answers removed and the 2-year auto-delete;
  - hub in it/pt/sl and the language switch;
  - nationality and flags;
  - add to home screen;
  - one branded email design;
  - the laptop routes.

## Steps
1. **Check nobody else changed live.** Ask Matteo whether the Athlete Review or marketing chats touched the live hub; compare the live snippet with the last version pushed live (git history of `athlete-area.php`). Anything found is merged into the repo first.
2. **Back up the live snippet:**
   - `GET https://coaching.cigalacycling.com/wp-json/code-snippets/v1/snippets/<live id>`;
   - save it to `live-coaching/backup/athlete-snippet-<date>.json`;
   - commit.
3. **Crawl live** (`tools/crawl.py`) to keep for comparison (SEO rule: nothing public may change; /athletes/ is noindex).
4. **Push the snippet to live** with all the modules, by hand. The push script refuses `--live` together with `--availability` on purpose: build the snippet body the same way (`tools/coaching_athlete_area.py`, the `--availability` file list) and `PUT` it to the live snippet id. Check that the answer says `active: true` and gives no code error. If it shows an error, put the backup straight back.
5. **Shared hub pages on live:**
   - rebuild the English and Italian ones (`--hub` content: Vekta calendar button, no Training zones/FTP tools, "New on the blog");
   - create "Shared hub (Portuguese athletes)" and "(Slovenian athletes)" from `HUB_T`;
   - upload the guide PDFs to live if they're missing.

   This is done by hand with the same functions, against live.
6. **Settings on live:**
   - Site icon (already set: the square logo).
   - Email header pictures `cc_mail_header_en` / `_it` (already on live).
   - Matteo's notices go to `info@cigalacycling.com` (live default in `cc_av_notify_to()`).
   - Check the daily job `cc_f_retention` is scheduled.
7. **Athletes' data on live** (the 35 logins already exist; no emails):
   - each athlete's **language** (`cc_lang`): **already set on live** (Matteo, 17 Nov). Only check it against his list (28 en, 5 it, 1 pt, 1 sl);
   - the **32 paper forms**: `POST /cc/v1/form-admin {email, action: "prefill", data}` then `{action: "paper"}`, so they get the short update. The answers come from the forms in Gmail, which are never committed;
   - Vittorio, Tommie and Marine have no form, so they get the full form;
   - Vekta ids later, by the laptop after Matteo confirms (`/cc/v1/athlete-meta`).
8. **Test on live,** with one temporary test athlete, deleted afterwards. Check:
   - login and the form;
   - hub, availability, goals;
   - a report draft, publish and "Send me a test email" (to Matteo only);
   - 390 / 820 / 1440 px, no sideways scroll, one H1;
   - `/athletes/` not cached and noindex, and `/wp-content/uploads/cc-private/` answers 403;
   - crawl again and compare with step 3.
9. **Welcome emails:** only when Matteo says "send". Users > "Send hub welcome email", or `POST /cc/v1/athlete-welcome`. Then tell the Coaching chat.
10. **Tell the laptop chats** the routes are live: same paths on `coaching.cigalacycling.com`, with a live application password (`PC-TOOLS-HANDOVER.md`).
11. **Clean staging:** delete the test athlete "Testa Prova" and its sample reports, and the test coach `cc-test-coach2`.

## After go-live
Every hub change is tested on staging first, then pushed to live the same way (backup, then the snippet). Staging and live stay identical.
