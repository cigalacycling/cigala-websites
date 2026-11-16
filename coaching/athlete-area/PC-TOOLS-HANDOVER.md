# Athlete data for Matteo's PC sessions (Vekta tools, availability scheduling, reviews, periodization)

Written 16 Nov 2026 by the availability chat. Paste this into a PC session (e.g. "Athlete Availability Scheduling", "Training Response Report") so it reads athletes from the Coaching website instead of asking Matteo.

**Status:** planned. Nothing below is live until Matteo says go. It goes on staging first, then live together with him. The availability box and the rider form are designed and in mock-up only.

## One place for every athlete
The Coaching website (`coaching.cigalacycling.com`, athlete area `/athletes/`) holds each coached athlete's own data. Athletes are matched everywhere by **email**: the website login email must be the same as the athlete's Vekta email.

## How a PC session reads it
- **Authentication:** a WordPress application password for Matteo's admin user.
  - Matteo creates it in wp-admin: Users > Profile > Application Passwords.
  - Keep it on the PC only, in an environment variable or the OS keychain. Never in chat, never in a repository.
  - Send it as HTTP Basic auth. Read-only use.
- **Availability** (built, not live yet): `GET https://coaching.cigalacycling.com/wp-json/cc/v1/availability` returns all athletes, or one with `?email=athlete@example.com`.
  ```json
  [{"athlete": "Name", "email": "…", "updated": 1794830000,
    "availability": {
      "week": {"mon": {"h": "1", "w": ["pm"]}, "...": {}},
      "changes": [{"from": "2026-11-24", "to": "2027-01-26", "days": ["tue"], "type": "gym", "h": "1", "text": "Strength block"}],
      "note": "free text",
      "voice": [{"text": "transcript", "at": 1794830000, "url": "private link, opens for Matteo"}]}}]
  ```
  - `h` is the time available a day: `""` = not set, `"0"` = rest day, `"0.5"` = 30 min, then `"1"`, `"1.5"`, `"2"`, `"3"`, `"4"` (4h+).
  - `w` is when they can ride: `am` (morning), `mid` (lunch), `pm` (evening).
  - Change `type` is one of: away, less, more, gym, indoor, other.
  - `to: ""` means no end date. `days: []` means every day.
  - Changes whose end date has passed are dropped automatically.
- **Rider form / profile** (planned, same API): `GET /wp-json/cc/v1/profile?email=` will return the answers from the online Rider Information Form:
  - contact details and emergency contact;
  - date of birth, sport;
  - numbers with test dates: FTP/CP, threshold HR, run pace, height, weight, target weight;
  - equipment;
  - training history and example week;
  - goals (short-term, long-term), race calendar, the A race;
  - motivation, strengths, weaknesses;
  - health answers, diet;
  - signed date.

  The usual week from the form fills the availability above. The form is locked once signed.
- **Goals & events** (planned, same API): `GET /wp-json/cc/v1/goals?email=` will return the athlete's current goals and events list. Each event has a name, date, type, priority (A/B/C) and a note. The athlete keeps it up to date, and it starts from the form's answers. Use it for periodization.

## Where athletes enter things (Matteo 16 Nov)
- Athletes enter availability, goals and events only in their Cigala area, never in Vekta.
- The website writes them into Vekta.
- So the PC tools should read them from the website API above, not from Vekta events.

## Periodization plan: one place for events (Matteo 16 Nov)
- Athletes add and change their goals and events only in their athlete hub: "My goals & events" at https://coaching.cigalacycling.com/athletes/#goals. Matteo gets an email on every change.
- The periodization plan must not have its own "add event" form for athletes. It reads the events from `GET /wp-json/cc/v1/goals?email=` (name, date, type, priority A/B/C, distance, climbing, note) and builds the plan around them.
- Where the plan now says something like "some events are missing, please add them here", replace it with a link: "Missing an event? Add it in your athlete hub" → https://coaching.cigalacycling.com/athletes/#goals.
- If the plan shows "From the form" text (`goals.from_form`), those are races an athlete typed on an old paper form. Matteo turns them into proper events.

## Vekta calendar (Matteo 16 Nov: use his existing Claude–Vekta connection)
- **The website does not hold a Vekta key and does not write to Vekta.** Matteo's existing Claude–Vekta connection does the writing.
- **Each run:**
  1. Read availability (and later goals & events) from the website API above. Only athletes whose `updated` time is newer than the last sync.
  2. Write notes into each athlete's Vekta calendar, matched by email.
- **Which days get a note:**
  - each day a change covers, only on its chosen weekdays (`days`);
  - for a change with no end date, the next 8 weeks;
  - when the usual week changes, one note on the next Monday;
  - for events, the event date.
- **Removing:** when a change or event is removed or edited, remove or update the note written for it. Keep a record of what was written for which athlete and date.
- **Question for this session:** which Vekta calendar item type fits each case? For example: away = unavailable day; gym only, indoor only, less or more time = note; race = event. Tell Matteo or the availability chat.
- **Running it (Matteo 16 Nov):** a scheduled task twice a day, at about 06:00 and 18:00 Irish time. If the Vekta connection is a claude.ai connector, the task runs with the PC off; otherwise it runs whenever the PC session runs.
- Matteo already gets an email the moment an athlete saves, so a delay in Vekta is fine.

## Rules (Matteo)
- Athletes only ever see motivating, athlete-friendly things.
- Never shown to athletes: the weekly plan, early warnings, compliance counts.
- Health answers are private: only the athlete and Matteo see them.
