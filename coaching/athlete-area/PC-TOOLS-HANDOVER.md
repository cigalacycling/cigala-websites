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

## Vekta calendar
When an athlete saves availability, the website writes notes into their Vekta calendar.
- **Which days:**
  - a note on each day a change covers, only on the weekdays they picked;
  - for a change with no end date, notes for the next 8 weeks;
  - when the usual week changes, one note on the next Monday.
- **Off until two things are confirmed against the Vekta API these PC tools already use:**
  - **the endpoint and calendar item type** for a note;
  - **where Matteo's Vekta key lives.** Recommended: in the website's `wp-config.php`, which Matteo adds himself, so it works with the PC off.

  If you know the endpoint and item type, tell the availability chat or Matteo.

## Rules (Matteo)
- Athletes only ever see motivating, athlete-friendly things.
- Never shown to athletes: the weekly plan, early warnings, compliance counts.
- Health answers are private: only the athlete and Matteo see them.
