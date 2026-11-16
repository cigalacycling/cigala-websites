"""Shared parts of the Coaching page previews (coachingpages/*.html): design system, header, footer, images, SEO check.

Same design system as the Tours homepage (survey/NfmCmGsjq4LL9bTAi38NXN/index.html): its <style> block is reused
as-is and coaching rules are added after it. Links go to the live pages until staging is built.
Images: WebP q90 from coaching/webp/ (extracted from live), copied into coachingpages/img/.
"""
import os, re, json, html, shutil
from PIL import Image
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shared', 'social'))
from social import social_row, SOCIAL_CSS   # shared footer icon row (Matteo, all sites)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
OUT = ROOT + 'coachingpages/'
os.makedirs(OUT + 'img', exist_ok=True)
C = 'https://coaching.cigalacycling.com'
T = 'https://tours.cigalacycling.com'
R = 'https://retail.cigalacycling.com/'
SKOOL = 'https://www.skool.com/cigala-cycling-collective-1115'
EXT = 'target="_blank" rel="noopener"'
E = lambda x: html.escape(x, quote=True)
live = {r['url']: r for r in json.load(open(ROOT + 'coaching/baseline.json'))}[C + '/']

# ---------- images ----------
WEBP = {o['url'].split('/uploads/')[1]: o['webp'] for o in json.load(open(ROOT + 'coaching/images.json')) if o.get('webp')}
def img(key, name):
    """key: unique part of the uploads path; copied to img/<name>.webp"""
    hits = [w for u, w in WEBP.items() if key in u]
    assert len(hits) == 1, (key, hits)
    dst = f'{OUT}img/{name}.webp'
    shutil.copy(ROOT + 'coaching/webp/' + hits[0], dst)  # always refresh, so a changed key never leaves a stale file
    return f'img/{name}.webp'
def conv(src, name, size=None):
    dst = f'{OUT}img/{name}.webp'
    if not os.path.exists(dst):
        im = Image.open(ROOT + src)
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if size: im.thumbnail((size, size), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=90, method=6)
    return f'img/{name}.webp'

LOGO = conv('coaching/brand/ccCoachingLogo-matteo-2026-11-15.png', 'logo-v2')   # logo file Matteo sent on 15 Nov

# ---------- white partner logos, no boxes (Matteo 15 Nov), made with tools/monologo.py ----------
import monologo as _mono
def mono_img(key, name, nobox=False, holes=False):
    src = OUT + 'img/' + name + '-src.webp'
    hits = [w for u, w in WEBP.items() if key in u]; assert len(hits) == 1, (key, hits)
    shutil.copy(ROOT + 'coaching/webp/' + hits[0], src)
    _mono.mono(src, OUT + f'img/mono-{name}.webp', nobox=nobox, holes=holes); os.remove(src)
    return f'img/mono-{name}.webp'
# Matteo 15 Nov: no "square inside a square". Every logo gets the same rounded tile in its own colours:
# the badge logos (Zwift, TrainingPeaks, Cycling Ireland) fill their tile; the others sit on white.
SEEN = [('imgi_4_wHe4MESD', 'logo-red-bull', '#fff', 'contain'), ('imgi_6_6_MxiOhd', 'logo-stickybottle', '#fff', 'contain'),
        ('unnamed-87.png', 'logo-zwift', '#f9661a', 'cover'), ('unnamed-86.png', 'logo-trainingpeaks', '#011031', 'cover'),
        ('unnamed-84.png', 'logo-cycling-ireland', '#284733', 'cover'), ('unnamed-85.png', 'logo-vekta', '#fff', 'contain')]
def _seen_src(k, n, fit):
    # Matteo 15 Nov: the coloured logos sat off-centre on phones (the marks are not centred in the original files, and
    # 'cover' cropped them differently at each width) -> trimmed to the mark itself and centred on the logo's own colour.
    if fit != 'cover': return img(k, n)
    short = n.replace('logo-', '')
    shutil.copy(ROOT + f'coaching/webp/seen-{short}-centred.webp', f'{OUT}img/{n}-centred3.webp')
    return f'img/{n}-centred3.webp'
def seen_logos():
    return '<div class="seen-tiles">' + ''.join(
        f'<span class="seen-tile" style="background:{bg}"><img class="{"mark" if fit == "cover" else fit}" src="{_seen_src(k, n, fit)}" alt="{E(live_alt(k))}" loading="lazy"></span>' for k, n, bg, fit in SEEN) + '</div>'

# ---------- menu ----------
def a(u, t): return f'<a href="{u}" {EXT}>{t}</a>'
CYC = [(C + '/coaching-vision/', 'Coaching Vision'), (C + '/individual-packages/', 'Individual Packages'),
       (C + '/group-club-packages/', 'Group &amp; Club Packages'), (C + '/book-1-on-1-session/', 'Book a 1-to-1 Session'), (SKOOL, 'Community')]
TRI = [(C + '/about2/', 'About Triathlon Coaching'), (C + '/tri-individual-packages/', 'Individual Packages'),
       (C + '/group-club-packages/', 'Group &amp; Club Packages'), (SKOOL, 'Community')]
SERV = [(C + '/testing/', 'INSCYD Testing'), (C + '/nutrition/', 'Nutrition'), (C + '/bike-fitting/', 'Bike Fit'),
        (C + '/talent-scout/', 'Talent Programme'), (C + '/club-talk/', 'Workshops'), (C + '/tools/', 'Free Training Tools')]   # a top-level item wrapped the menu at 1440
RES = [(C + '/testimonials/', 'Testimonials'), (C + '/case-studies/', 'Case Studies')]   # Matteo 15 Nov: one menu for both
def dd(label, items):
    return (f'<div class="dd"><button type="button" class="dd-btn" aria-expanded="false" aria-haspopup="true">{label} <span aria-hidden="true">▾</span></button>'
            f'<div class="dd-menu">{"".join(a(u, t) for u, t in items)}</div></div>')
def mob(label, items):
    # Matteo 15 Nov: same phone menu as Tours: top-level items, submenus fold open under a green arrow
    return f'<details class="sub"><summary>{label}</summary><div class="sub-links">' + ''.join(a(u, t) for u, t in items) + '</div></details>'

HEADER = f'''<header class="nav">
  <div class="in">
    <a class="brand" href="{C}/" {EXT}><img src="{LOGO}" alt="Cigala Cycling Coaching Logo" width="58" height="58"></a>
    <nav class="menu" aria-label="Main">
      {a(C + '/about/', 'About')}
      {dd('Cycling', CYC)}
      {dd('Triathlon', TRI)}
      {dd('Services', SERV)}
      {dd('Results', RES)}
      {a(C + '/blog/', 'Blog')}
      {a(T + '/', 'Bike Tours')}
      {a(R, 'Shop')}
      {a(C + '/contact/', 'Contact')}
    </nav>
    <a class="btn btn-go" href="https://calendly.com/cigalacycling" {EXT}>Book Consultation</a>
    <details class="burger" id="menu-mobile">
      <summary>Menu</summary>
      <nav aria-label="Main (mobile)">
        {a(C + '/about/', 'About')}
        {mob('Cycling', CYC)}
        {mob('Triathlon', TRI)}
        {mob('Services', SERV)}
        {mob('Results', RES)}
        {a(C + '/blog/', 'Blog')}{a(T + '/', 'Bike Tours')}{a(R, 'Shop')}{a(C + '/contact/', 'Contact')}
      </nav>
    </details>
  </div>
</header>'''

# ---------- Free Tools band (Matteo 15 Nov: make the tools easy to find on the homepage and packages page) ----------
FT = [('/tools/training-zones-calculator/', 'Training zones', 'Power and heart-rate zones from your FTP', '<path d="M3 3v18h18"/><path d="M7 15v3M11 11v7M15 8v10M19 5v13"/>'),
      ('/tools/ftp-test-calculator/', 'FTP test', 'Your FTP from a ramp, 8-min or 20-min test', '<circle cx="12" cy="13" r="8"/><path d="M12 13l4-4M12 3V1M9 1h6"/>'),
      ('/tools/carbs-per-hour-calculator/', 'Carbs per hour', 'Your fuelling plan in gels and bottles', '<path d="M12 2v4M5 7l2.5 2.5M19 7l-2.5 2.5"/><rect x="7" y="9" width="10" height="13" rx="3"/><path d="M7 14h10"/>'),
      ('/tools/sweat-rate-calculator/', 'Sweat rate', 'How much you sweat, and how much to drink', '<path d="M12 2.7l5.7 5.6a8 8 0 1 1-11.4 0z"/>'),
      ('/tools/critical-power-calculator/', 'Critical Power &amp; W′', 'CP, W′ and your best power from 2 to 20 min', '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>'),
      ('/tools/climb-time-calculator/', 'Climb time', 'Your time on the Stelvio, Alpe d’Huez or any climb', '<path d="M2 20h20L14 6l-4 6-2-3-6 11z"/><path d="M14 6l2 3"/>'),
      ('/tools/gear-speed-calculator/', 'Gear &amp; speed', 'Your speed in every gear at any cadence', '<circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.2 4.2l2.8 2.8M17 17l2.8 2.8M1 12h4M19 12h4M4.2 19.8L7 17M17 7l2.8-2.8"/>'),
      ('/tools/swim-pace-calculator/', 'Swim pace (CSS)', 'Triathlon swim paces from two time trials', '<path d="M2 18c2 0 2-1.5 4-1.5S8 18 10 18s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M2 13c2 0 2-1.5 4-1.5S8 13 10 13s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><circle cx="16" cy="5" r="2"/><path d="M6 9l4-3 3 3"/>')]
def tools_band():
    cards = ''.join(f'<a class="ft-card" href="{C}{u}" {EXT}><svg viewBox="0 0 24 24" aria-hidden="true">{ic}</svg><span><b>{t}</b><small>{d}</small></span><i aria-hidden="true">→</i></a>' for u, t, d, ic in FT)
    return f'''<section class="ft">
  <div class="in">
    <div class="ft-box">
      <div class="ft-head"><div class="eyebrow">Train smarter</div><h3 class="h-sec">FREE TRAINING TOOLS</h3><div class="bar"></div>
        <p>Free calculators from Head Coach Matteo Cigala. Work out your numbers in seconds.</p>
        <a class="arrow-link" href="{C}/tools/" {EXT}>See all free tools →</a></div>
      <div class="ft-cards">{cards}</div>
    </div>
  </div>
</section>'''
FT_CSS = '''<style>
.sigph { position: relative; display: block; }
.sigph img { display: block; width: 100%; height: auto; }
.sigph img.signature { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.sigph .sig-anchor { position: absolute; left: 10%; right: 10%; top: 82%; bottom: 0; }
html.sig-ok .sigph img.signature { clip-path: inset(0 100% 0 0); }
html.sig-ok .sigph img.signature.go { animation: sig-write 2.2s cubic-bezier(.55,.1,.35,1) forwards; }
@keyframes sig-write { to { clip-path: inset(0 0 0 0); } }
.ft-box { display: grid; grid-template-columns: minmax(0, 4fr) minmax(0, 8fr); gap: 32px; align-items: center; padding: 32px; border: 1px solid var(--border); border-radius: 16px; background: linear-gradient(135deg, rgba(0,154,68,.12), rgba(0,154,68,0) 60%), var(--panel-grad), var(--panel); }
.ft-head p { margin: 14px 0 0; color: var(--text-2); }
.ft-head .arrow-link { display: inline-block; margin-top: 14px; }
.ft-cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }   /* 8 tools in 2 columns */
.ft-card { display: flex; align-items: center; gap: 14px; padding: 14px 16px; border: 1px solid var(--border); border-radius: 12px; background: rgba(255,255,255,.03); text-decoration: none; transition: border-color .2s, transform .2s; }
.ft-card:hover { border-color: rgba(0,154,68,.6); transform: translateX(3px); }
.ft-card svg { flex: none; width: 40px; height: 40px; padding: 9px; border-radius: 10px; background: var(--green-wash); fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.ft-card span { flex: 1; min-width: 0; display: grid; gap: 2px; }
.ft-card b { color: var(--text); font-size: 15px; }
.ft-card small { color: var(--text-3); font-size: 13px; }
.ft-card i { font-style: normal; color: var(--green-text); font-weight: 700; }
@media (max-width: 900px) { .ft-box { grid-template-columns: minmax(0, 1fr); padding: 22px; gap: 20px; } }
@media (max-width: 560px) { .ft-cards { grid-template-columns: minmax(0, 1fr); } }
</style>'''

# ---------- Case studies (Matteo 15 Nov). Every fact comes from the athlete's own testimonial on the live Testimonials
# page (coaching/text/testimonials.txt); nothing is added. Matteo will add more as he publishes them.
CASES = [
    {'slug': 'marine-lenehan',
     'timeline': [('February', 'First rides: a complete newcomer to cycling'), ('With Matteo', 'A crash course in cycling and personalised, detailed sessions'),
                  ('Within the year', 'European Gran Fondo & gravel champion (19–34)'), ('Worlds', 'Silver medal at the Gran Fondo World Championships'),
                  ('1 August 2025', 'Stagiaire with LIDL-TREK, a WorldTour team'), ('1 January 2026', 'Turned professional: WorldTour Pro with LIDL-TREK, only a few years after her first ride')],   # team: her own site, vivifysports.com/about   # Matteo 15 Nov 2026
     # WorldTour step: Matteo, 15 Nov 2026
     'source': 'From Marine’s testimonial', 'photo_file': 'coaching/athletes/marine-lenehan.webp', 'name': 'Marine Lenehan', 'where': 'Ireland', 'photo': 'T135849.182',
     'headline': 'From first ride to the WorldTour', 'stat': 'WorldTour Pro', 'stat_label': 'Pro since 1 January 2026', 'tag': 'Road · Gran Fondo & gravel',
     'before': 'A complete newcomer to cycling: she started riding in February.',
     'goal': 'Learn the sport and find out how far she could go.',
     'how': ['A crash course in cycling, built from scratch', 'Personalised sessions with attention to every detail', 'Every session different, so training stayed fun and dynamic'],
     'result': 'European Gran Fondo & gravel champion (19–34) and silver medallist at the Gran Fondo World Championships, within a year of starting cycling. Then the biggest step of all: a stagiaire with LIDL-TREK from 1 August 2025, and on 1 January 2026 she turned professional with the WorldTour team, the top level of the sport, only a few years after her first ride.',
     'quote': 'He has not only made me fall in love with cycling, but has believed in me even when I didn’t.'},
    # Tilen: Matteo's athlete case study post (15 Nov 2026, "Athlete Review" chat); numbers from his Vekta data.
    # No photo yet (Matteo will send it): the card and the case show his numbers instead.
    {'slug': 'tilen', 'name': 'Tilen Č.', 'where': 'Road racer · Slovenia', 'photo': None, 'photo_file': 'coaching/athletes/tilen.webp',
     'photo_alt': 'Tilen Č. racing in a white team kit',
     'headline': 'From not sprinting out of the saddle to 1,063 W', 'stat': '1,063 W sprint', 'stat_label': 'Best 15-second power', 'tag': 'Road racing',
     'before': 'One year ago Tilen couldn’t sprint standing up.',
     'goal': 'Race at the front, from local races to the national championships.',
     'how': ['Consistency: steady training, no huge weeks (the biggest was 16 hours)', 'A plan built around his life, adjusted week by week', 'Talking to his coach: RPE and a comment after his rides, so the plan could adapt'],
     'result': '4th overall at Portorož and first over the main climb; 9th in the amateur road race at the national championships. All-time bests from the sprint to three hours, and a Critical Power of 375 W.',
     'quote': 'Significant technical progress and gains in strength.',
     'bars': [('Riding time', 'More hours, no huge weeks', 558, 651, ' h', '+17%'),
              ('Best 15-second power', 'From seated to standing', 851, 1063, ' W', '+212 W'),
              ('Best 2-hour power', 'Stronger for longer, set at L’Étape Slovenia', 296, 316, ' W', '+20 W')],
     'bests': ['8 min: 429 W (5.5 W/kg)', '20 min: 382 W (4.9 W/kg)', '2 min: 556 W (7.1 W/kg), at the Nationals', '3 h: 298 W (3.8 W/kg), at Corsa per Haiti'],
     'source': 'Vekta data, year before vs this year (Nov 2024 – Nov 2026)'},
    # Marco: Matteo's case study post (Canva "Marco Case Study - Carousel", 15 Nov 2026), numbers from his Vekta data.
    # The post tracker says "Needs Marco's OK": staging only until Marco agrees.
    {'slug': 'marco', 'name': 'Marco B.', 'where': 'Road & gravel racer · Portugal', 'photo': None, 'photo_file': 'coaching/athletes/marco.webp',
     'photo_alt': 'Marco B. racing on gravel in a green kit, race number 96',
     'headline': 'Every number went up', 'stat': '+124 W sprint', 'tag': 'Road & gravel',
     'before': 'Marco races on the road and on gravel from Portugal, including the European Gravel Championships in Belgium and Portugal’s gravel nationals.',
     'goal': 'Raise his power from the sprint to the hour for his road and gravel races.',
     'how': [],
     'result': 'From late July to late October, every one of his power bests went up: past 4 W/kg for five minutes, and W′, his energy for attacks, up 28%.',
     'quote': None,
     'labels': ('Previous 3 months', 'Last 3 months'),
     'bars': [('Best 30-second power', 'The punch: almost a quarter more', 505, 628, ' W', '+24%'),
              ('Best 15-second power', 'The sprint: faster to the line', 728, 852, ' W', '+124 W'),
              ('Best 5-minute power', 'The climbs: from 3.8 to 4.1 W/kg', 271, 292, ' W', '+21 W')],
     'bests_title': 'Up across the board',
     'bests': ['3 minutes: 292 → 325 W', '10 minutes: 242 → 263 W', '20 minutes: 222 → 236 W', '60 minutes: 204 → 211 W', 'W′: 11.4 → 14.6 kJ (+28%)'],
     'source': 'Vekta data, last 3 months (late July – late October 2026) against the 3 months before'},
    # Vittorio and David: Matteo's case study posts (Eoin removed 16 Nov: he wants it private) (Canva, 15 Nov 2026), numbers from their Vekta data.
    # The post tracker says each needs the athlete's OK: staging only until they agree.

    {'slug': 'vittorio', 'name': 'Vittorio C.', 'where': 'MTB & cyclocross racer · Italy', 'photo': None, 'photo_file': 'coaching/athletes/vittorio.webp',
     'photo_alt': 'Vittorio C. racing mountain bike in an orange helmet',
     'headline': 'Faster out of every corner', 'stat': '1,112 W record', 'tag': 'MTB & cyclocross',
     'before': 'Vittorio races mountain bike and cyclocross in Italy: 25 races in the last 12 months.',
     'goal': 'Get stronger in the short, repeated, all-out efforts that decide off-road racing.',
     'how': [],
     'result': 'All-time bests in the sprint and the 1-minute, 7.0 W/kg for a minute (his best ever, above his previous record from 2023), and his highest power ever: 1,112 W in April 2026.',
     'quote': 'Today, a max power record.',
     'bars': [('Best 5-second power', 'A sharper sprint: an all-time best', 837, 919, ' W', '+82 W'),
              ('Best 15-second power', 'Up every steep ramp: another all-time best', 684, 782, ' W', '+98 W'),
              ('Best 1-minute power', 'The attack: 7.0 W/kg for a minute', 404, 451, ' W', '+47 W')],
     'bests_title': 'More matches to burn',
     'bests': ['W′: 7.4 → 9 kJ (+21%), Nov 2025 vs Nov 2026', 'Record power: 1,112 W, April 2026'],
     'source': 'Vekta data, last 12 months against the 12 months before (Nov 2024 – Nov 2026)'},
    {'slug': 'david', 'name': 'David O.', 'where': 'Sportive rider · Ireland', 'photo': None, 'photo_file': 'coaching/athletes/david.webp',
     'photo_alt': 'David O. racing in his Gorey CC club kit',
     'headline': '+44 watts of engine', 'stat': '+44 W CP', 'tag': 'Sportive',
     'before': 'David rides Ireland’s big sportives: the Tour de Conamara, the Tour de Kilkenny and the Tour of Wicklow, days of 140–160 km.',
     'goal': 'A bigger engine for long days in the saddle.',
     'how': [],
     'result': 'Critical Power up from 244 to 288 W in twelve months (+18%), with his highest ever, 290 W, in September, and the highest VO2max Vekta has on record for him.',
     'quote': None,
     'bars': [('Best 20-minute power', 'The long climbs on a big day out', 250, 276, ' W', '+26 W'),
              ('Best 5-minute power', 'Over a short, steep climb with the group', 288, 320, ' W', '+32 W'),
              ('Best 30-second power', 'A quarter more kick', 505, 633, ' W', '+128 W')],
     'bests_title': 'The engine',
     'bests': ['Critical Power: 244 → 288 W (+44 W, +18%), Nov 2025 vs Nov 2026', 'VO2max: 52 → 58 ml/kg/min (Vekta estimate)'],
     'source': 'Vekta data, last 12 months against the 12 months before (Nov 2024 – Nov 2026)'},
    {'slug': 'shane-courtney',
     'labels': ('Before', 'With coaching'),
     'bars': [('FTP', 'Up in under 4 months', 220, 260, ' W', '+40 W'), ('Sprint', 'From about 600 W', 600, 920, ' W', '+320 W')],
     'bests_title': 'Results', 'bests': ['Upgraded from A4 to A3 with points to spare', 'County hill-climb champion', 'Comfortable in the drops all day, with two flexibility sessions a week'],
     'source': 'Shane’s own numbers, from his testimonial', 'photo_file': 'coaching/athletes/shane-courtney.webp', 'name': 'Shane Courtney', 'where': 'Tralee Manor West ibike', 'photo': 'T142905.118',
     'headline': '+40 W FTP in under 4 months', 'stat': '220 → 260 W FTP', 'tag': 'Road racing',
     'before': 'Training 14–16 hours a week over the winter on a generic plan, and getting nowhere. Racing in A4.',
     'goal': 'Get faster and move up the racing categories.',
     'how': ['Contact by phone or WhatsApp every couple of days, and weekly feedback', 'No junk miles: every interval has a clear purpose', 'Recovery, nutrition, strength and two flexibility sessions a week'],
     'result': 'FTP up from 220 W to 260 W in under 4 months, sprint from about 600 W to 920 W. Upgraded to A3 with points to spare, and county hill-climb champion.',
     'quote': 'Matteo managed to raise my FTP from 220w to 260w in less than 4 months & my sprint from 600w ish to 920w.'},
    {'slug': 'bernd-ondruch',
     'timeline': [('3 years', 'Trying to qualify on his own, with no structured plan'), ('Week 1', 'Coaching with Matteo: varied, tailored workouts'),
                  ('4–6 weeks', 'Noticeable improvements, and consistent since'), ('After a crash', 'The plan adjusted, never beyond his limits'), ('12 months', 'Qualified for the UCI Gran Fondo World Championship')],
     'source': 'From Bernd’s testimonial', 'photo_file': 'coaching/athletes/bernd-ondruch-2x.webp', 'name': 'Bernd Ondruch', 'where': 'Germany & UK', 'photo': 'T134927.535',
     'headline': 'Qualified for the Gran Fondo Worlds', 'stat': 'Worlds qualified', 'tag': 'Gran Fondo',
     'before': 'Three years of trying to qualify on his own, riding consistently but with no structured plan.',
     'goal': 'Qualify for the UCI Gran Fondo World Championship.',
     'how': ['A coaching style adapted to him, with accountability but no pressure', 'Varied workouts targeting different parts of his riding', 'The plan adjusted after a crash, never pushing beyond his limits'],
     'result': 'Clear improvements after 4–6 weeks, and he qualified for the UCI Gran Fondo World Championship after 12 months of coaching.',
     'quote': 'With his expertise, support, and personalized approach, I have achieved my goal of qualifying for the UCI Granfondo World Championship.'},
    {'slug': 'rob-kavanagh',
     'timeline': [('Before', 'Lost interest in the gym and football, and put on weight'), ('New bike', 'Riding alone, with no progress for the time put in'),
                  ('First call', 'A 40-minute chat, and a structured plan from day one'), ('6 months', 'Close to 16 kg lost: healthier, fitter, happier')],
     'source': 'From Rob’s testimonial', 'photo_file': 'coaching/athletes/rob-kavanagh.webp', 'name': 'Rob Kavanagh', 'where': 'Ireland', 'photo': 'T143158.190',
     'headline': 'Close to 16 kg lost in 6 months', 'stat': '−16 kg', 'tag': 'Fitness & weight loss',
     'before': 'Had lost interest in the gym and football and put on a lot of weight. Bought a road bike, but wasn’t making progress riding alone.',
     'goal': 'Lose weight, get fitter and start racing.',
     'how': ['A structured training plan from the first phone call', 'Sessions planned for him, so he knew exactly what to do'],
     'result': 'Close to 16 kg lost in 6 months, and healthier, fitter and happier.',
     'quote': 'To date I’ve lost close to 16 kg thanks to Matteos coaching and support, most importantly I look forward to every session that is planned out for me.'},
    {'slug': 'derek-lawler',
     'timeline': [('Start', 'From the “couch (literally!)”'), ('9 months', 'A plan built up to the event'), ('2017', 'Haute Route Pyrenees, for his 60th birthday'),
                  ('2024', 'Heart disease and a cardiac procedure'), ('After', 'A steady, gradual plan back to regular cycling')],
     'source': 'From Derek’s testimonial', 'photo_file': 'coaching/athletes/derek-lawler-2x.webp', 'name': 'Derek Lawler', 'where': 'Kilkenny, Ireland', 'photo': 'T140239.558',
     'headline': 'From the couch to the Haute Route at 60', 'stat': 'Haute Route at 60', 'tag': 'Sportive & health',
     'before': 'Starting, in his words, from the “couch (literally!)”.',
     'goal': 'Ride the Haute Route Pyrenees to mark his 60th birthday.',
     'how': ['A 9-month plan building up to the event', 'Years later, a steady, gradual plan to recover fitness after heart disease and a cardiac procedure'],
     'result': 'Completed the Haute Route Pyrenees in 2017, “the experience of a lifetime”, and later got back to regular cycling after his cardiac procedure.',
     'quote': 'As a non-elite or serious cyclist, I can highly recommend Matteo to anyone interested in getting fit and ready for any cycling goal, no matter what level you’re at or what age you are!'},
]
# Matteo 15 Nov: keep each athlete centred in the crop (horizontal% vertical% of the photo: where the face is)
FOCUS = {'marine-lenehan': '45% 28%', 'tilen': '50% 25%', 'marco': '50% 22%', 'vittorio': '35% 32%', 'david': '45% 22%',
         'shane-courtney': '45% 50%', 'bernd-ondruch': '45% 40%', 'rob-kavanagh': '45% 38%', 'derek-lawler': '45% 48%'}
def fstyle(c): return f' style="object-position:{FOCUS[c["slug"]]}"' if c['slug'] in FOCUS else ''
# Italian labels for the case study cards on /preparatore-di-ciclismo-italia/ (Matteo 15 Nov: that page all in Italian)
CASES_IT = {
    'marine-lenehan': ('Strada · Gran Fondo e gravel', 'WorldTour Pro', 'Professionista dal 1° gennaio 2026', 'Dalla prima uscita al WorldTour', 'Irlanda'),
    'tilen': ('Corse su strada', '1.063 W sprint', 'Miglior potenza su 15 secondi', 'Da non saper scattare in piedi a 1.063 W', 'Corridore su strada · Slovenia'),
    'marco': ('Strada e gravel', '+124 W sprint', '', 'Ogni numero è salito', 'Corridore strada e gravel · Portogallo'),
    'vittorio': ('MTB e ciclocross', 'Record 1.112 W', '', 'Più veloce in uscita da ogni curva', 'Corridore MTB e ciclocross · Italia'),
    'david': ('Granfondo', '+44 W CP', '', '+44 watt di motore', 'Granfondista · Irlanda'),
    'shane-courtney': ('Corse su strada', 'FTP 220 → 260 W', '', '+40 W di FTP in meno di 4 mesi', 'Tralee Manor West ibike · Irlanda'),
    'bernd-ondruch': ('Gran Fondo', 'Qualificato ai Mondiali', '', 'Qualificato ai Mondiali Gran Fondo', 'Germania e Regno Unito'),
    'rob-kavanagh': ('Forma fisica e dimagrimento', '−16 kg', '', 'Quasi 16 kg persi in 6 mesi', 'Irlanda'),
    'derek-lawler': ('Granfondo e salute', 'Haute Route a 60 anni', '', 'Dal divano all’Haute Route a 60 anni', 'Kilkenny, Irlanda'),
}
# Matteo 16 Nov: the signature writes itself when it comes into view (as on Tours). Photo and signature are two layers
# of the same size (coaching/brand/matteo-cigala-photo-nosig.webp + -signature-layer.webp, made from the same sources as
# the old composite). The script watches a box over the signature (a fully clipped image never counts as on screen).
SIGN_JS = """<script>(function(){if(window._ccSig)return;window._ccSig=1;if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
var s=document.querySelectorAll('img.signature');if(!s.length)return;document.documentElement.classList.add('sig-ok');
var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){o.unobserve(e.target);e.target._sig.classList.add('go');}});},{threshold:.5});
s.forEach(function(x){var t=x.nextElementSibling||x.parentElement;t._sig=x;o.observe(t);});})();</script>"""
def sig_photo(name, alt):
    """Matteo's cut-out with his signature as a separate layer that writes itself"""
    return (f'<span class="sigph"><img src="{conv("coaching/brand/matteo-cigala-photo-nosig.webp", name)}" alt="{E(alt)}" width="720" height="933">'
            f'<img class="signature" src="{conv("coaching/brand/matteo-cigala-signature-layer.webp", "matteo-cigala-signature")}" alt="" aria-hidden="true" width="720" height="933">'
            f'<span class="sig-anchor" aria-hidden="true"></span></span>{SIGN_JS}')

def case_cards(link_base, lang='en'):
    """Scrolling case study cards; link_base is the case studies page URL. lang='it': Italian labels (CASES_IT)."""
    def tr(c):
        if lang != 'it': return c
        t = CASES_IT[c['slug']]
        return dict(c, tag=t[0], stat=t[1], stat_label=t[2], headline=t[3], where=t[4])
    def pic(c):
        if c.get('photo_file'): return f'<span class="cs-img"><img src="{conv(c["photo_file"], "case-" + os.path.basename(c["photo_file"]).rsplit(".", 1)[0])}" alt="{E(c.get("photo_alt") or live_alt(c["photo"]))}" loading="lazy"{fstyle(c)}></span>'
        if not c['photo']: return f'<span class="cs-img cs-data" aria-hidden="true"><b>{E(c["stat"])}</b><small>{E(c.get("stat_label", ""))}</small></span>'
        return f'<span class="cs-img"><img src="{img(c["photo"], "athlete-" + c["slug"])}" alt="{E(live_alt(c["photo"]))}" loading="lazy"{fstyle(c)}></span>'
    rd = 'Leggi il caso studio →' if lang == 'it' else 'Read the case study →'
    cards = ''.join(f'<a class="cs-card" href="{link_base}#{c["slug"]}" {EXT}>{pic(c)}'
                    f'<span class="cs-tx"><span class="cs-tag">{E(c["tag"])}</span><b class="cs-stat">{E(c["stat"])}</b><span class="cs-h">{E(c["headline"])}</span>'
                    f'<span class="cs-n">{E(c["name"])} · {E(c["where"])}</span><span class="arrow-link">{rd}</span></span></a>' for c in map(tr, CASES))
    # Matteo 15 Nov: the case studies move on slowly by themselves, like the reviews (pause on hover/touch, off for reduced motion)
    js = ("<script>(function(){var stop=false;var wr=document.currentScript.parentElement,r=wr.querySelector('.cs-row');if(!r)return;var red=matchMedia('(prefers-reduced-motion: reduce)').matches;"
          "wr.querySelectorAll('.cs-btn').forEach(function(b){b.addEventListener('click',function(){stop=true;"
          "var w=(r.firstElementChild?r.firstElementChild.getBoundingClientRect().width+14:300)*(+b.dataset.d);"
          "if(w>0&&r.scrollLeft>=r.scrollWidth-r.clientWidth-4)r.scrollTo({left:0,behavior:'smooth'});else r.scrollBy({left:w,behavior:'smooth'});});});if(red)return;"
          "var hold=false,vis=false;r.addEventListener('mouseenter',function(){hold=true;});r.addEventListener('mouseleave',function(){hold=false;});"
          "r.addEventListener('focusin',function(){hold=true;});r.addEventListener('focusout',function(){hold=false;});r.addEventListener('touchstart',function(){stop=true;},{passive:true});"
          "if('IntersectionObserver' in window)new IntersectionObserver(function(e){vis=e[0].isIntersecting;}).observe(r);"
          "setInterval(function(){if(stop||hold||!vis||document.hidden)return;var c=r.firstElementChild,w=c?c.getBoundingClientRect().width+14:300;"
          "if(r.scrollLeft>=r.scrollWidth-r.clientWidth-4)r.scrollTo({left:0,behavior:'smooth'});else r.scrollBy({left:w,behavior:'smooth'});},4000);})();</script>")
    nav = ('<div class="rv-nav cs-nav"><button type="button" class="cs-btn" data-d="-1" aria-label="Previous case studies">←</button>'
           '<button type="button" class="cs-btn" data-d="1" aria-label="Next case studies">→</button></div>')
    return f'<div class="cs-wrap"><div class="cs-row" tabindex="0" aria-label="Case studies, scroll sideways">{cards}</div>{nav}{js}</div>'
CS_CSS = """<style>
.cs-row, .rv-row { scrollbar-width: none !important; }
.rv-row, .cs-row { padding-top: 8px !important; margin-top: -8px; }   /* Matteo 15 Nov: the green top border showed cut on hover */   /* Matteo 15 Nov: arrows instead of a drag bar */
.cs-row::-webkit-scrollbar, .rv-row::-webkit-scrollbar { display: none; }
.cs-nav { display: flex; justify-content: flex-end; gap: 8px; margin-top: 10px; }
.cs-btn { width: 40px; height: 40px; border-radius: 50%; border: 1px solid var(--border-strong); background: var(--panel-solid); color: var(--text); font-size: 16px; cursor: pointer; }
.cs-btn:hover { border-color: var(--green); color: var(--green-text); }
.cs-row { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(260px, 300px); gap: 14px; overflow-x: auto; scroll-snap-type: x mandatory; padding-bottom: 10px; scrollbar-width: thin; }
.cs-card { scroll-snap-align: start; display: flex; flex-direction: column; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; background: var(--panel-grad), var(--panel); text-decoration: none; transition: border-color .2s, transform .2s; }
.cs-card:hover { border-color: rgba(0,154,68,.6); transform: translateY(-2px); }
.cs-img { aspect-ratio: 4 / 3; overflow: hidden; background: #111; }
.cs-img img { width: 100%; height: 100%; object-fit: cover; filter: brightness(.9); }
.cs-data { display: grid; place-content: center; text-align: center; gap: 6px; background: radial-gradient(circle at 30% 20%, rgba(0,154,68,.45), rgba(0,154,68,0) 60%), #0b1a12; }
.cs-data b { font: 400 40px/1 var(--head); color: #fff; }
.cs-data small { font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--green-text); }
.cs-tx { display: grid; gap: 6px; padding: 16px 18px 18px; }
.cs-tag { font-size: 11px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--red-text, #ff3d33); }
.cs-stat { font: 400 30px/1.05 var(--head); color: var(--text); text-transform: uppercase; }
.cs-h { font-size: 15px; font-weight: 600; color: var(--text); }
.cs-n { font-size: 13px; color: var(--text-3); }
.cs-card .arrow-link { margin-top: 6px; }
</style>"""

def li(u, t): return f'<li>{a(u, t)}</li>'
# Footer: same layout as cigalacycling.com (logo + tagline, two link columns, contact), Matteo 15 Nov: "less busy".
# The four international pages keep their footer links (and live H2 wording) for Google, but sit in a small
# "International coaching" toggle in the bottom row instead of a visible column. Closed <details> content is still in the HTML.
SITE = [(C + '/about/', 'About'), (C + '/testimonials/', 'Testimonials'), (C + '/case-studies/', 'Case Studies'), (C + '/blog/', 'Blog'), (T + '/', 'Bike Tours'), (R, 'Retail Store'), (C + '/contact/', 'Contact')]
COACH = [(C + '/individual-packages/', 'Cycling Packages'), (C + '/tri-individual-packages/', 'Triathlon Packages'), (C + '/group-club-packages/', 'Group &amp; Club Packages'),
         (C + '/book-1-on-1-session/', 'Book a 1-to-1 Session'), (C + '/talent-scout/', 'Talent Programme'), (C + '/nutrition/', 'Nutrition'), (C + '/tools/', 'Free Training Tools')]
INTL = [('/cycling-coach-uk/', 'Cycling Coach UK'), ('/cycling-coach-usa/', 'Cycling Coach USA'), ('/cycling-coach-canada/', 'Cycling Coach Canada'), ('/preparatore-di-ciclismo-italia/', 'Preparatore di Ciclismo Italia')]
# Brevo form for the separate "coaching.cigalacycling.com" list (id 17, made by Matteo 15 Nov). Used by the newsletter
# pop-up and the Free Tools sign-up. Empty = both stay off. Set it to the form's …sibforms.com/serve/… URL + '?isAjax=1'.
COACH_NL_URL = 'https://c20401b9.sibforms.com/serve/MUIFACJOu7ccgvzQx0Os6Ufdk7qgrrQshoPPXrCqUL3B6oEQ3ZH8GYNYsXln9tQ-g7SSytfQLolkvE5ZqLO1uADraBt1sZCRx6kQblp5154MNVlZl7Iy9x6MyrcorkvpSaaksa6KFnVDBLc8HlZMfGEnMbXcEFbgvKVKkFFEQYKm0kCexECB51T1wepBk1_8yIoblC3zdbT1bQ9g?isAjax=1'   # Matteo's Coaching form, 15 Nov
GOOGLE_REVIEWS = 'https://share.google/lwboSfcuStGhX0c0p'   # Cigala Cycling Ltd Google Business Profile (shared/BUSINESS.md)
FOOTER = f'''<footer>
  <div class="in fcols">
    <div>
      <a class="brand brand-lg" href="{C}/" {EXT}><img src="{LOGO}" alt="Cigala Cycling Coaching" width="76" height="76"></a>
      <h2 class="tag-line">TRAIN SMARTER. RIDE FASTER.</h2>
    </div>
    <div><h4>Coaching</h4><ul>{''.join(li(u, t) for u, t in COACH)}</ul></div>
    <div><h4>Explore</h4><ul>{''.join(li(u, t) for u, t in SITE)}</ul></div>
    <div><h4>Contact</h4>
      <ul>
        <li><a href="mailto:info@cigalacycling.com">info@cigalacycling.com</a></li>
        <li><a href="tel:+35340478107">+353 404 78107</a></li>
        <li>{a(GOOGLE_REVIEWS, '<span class="gstar" aria-hidden="true">★</span> Google reviews')}</li>
      </ul>
      {social_row()}
    </div>
  </div>
  <div class="legal"><div class="in">
    <span>© 2026 Cigala Cycling Ltd · Registered in Ireland No. 675577 · VAT IE3699893CH</span>
    {a(C + '/terms-conditions/', 'Terms &amp; Conditions')}
    {a(C + '/privacy-policy/', 'Privacy Policy')}
    {a(C + '/athletes/', 'Athlete login')}
    <details class="intl-dd"><summary>International coaching</summary>
      <ul class="intl">{''.join(f'<li><h2><a href="{C}{u}" {EXT}>{t}</a></h2></li>' for u, t in INTL)}</ul>
    </details>
  </div></div>
</footer>'''

# ---------- CSS: Tours design system + coaching additions ----------
SRC = open(ROOT + 'survey/NfmCmGsjq4LL9bTAi38NXN/index.html').read()
BASE = re.search(r'<style>\n/\* Cigala Cycling kit.*?</style>', SRC, re.S).group(0)
BASE = BASE.replace('url(topo-background.svg) center / cover no-repeat', 'url(img/topo-background-tile.svg) top center / auto 3000px repeat-y')
BASE = BASE.replace('rgba(8,9,10,.3), rgba(8,9,10,.3)', 'rgba(8,9,10,.6), rgba(8,9,10,.6)')  # BRAND.md: 60% dim
shutil.copy(ROOT + 'bk/up/topo-background-tile.svg', OUT + 'img/topo-background-tile.svg')
CSS = '''<style>
.gstar { color: #f0bf00; }   /* gold star before Google reviews (Matteo, all sites) */
/* ---- coaching homepage additions ---- */
.eyebrow { color: var(--red-text, #ff3d33); }
.hero .eyebrow-h { font: 600 12px/1.4 var(--body); letter-spacing: .14em; text-transform: none; color: #fff; display: inline-flex; align-items: center; gap: 8px;
  background: rgba(8,9,10,.7); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 12px; margin: 0 0 18px; }
.hero .eyebrow-h::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--red); }
.hero h1 { max-width: 14ch; }
.hero .lede { max-width: 54ch; }
.stat .n { font-size: clamp(28px, 3.4vw, 44px); }
.h-sec { font-size: clamp(30px, 4.6vw, 52px); }
.head h2 { max-width: 24ch; }
.paths { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.path { position: relative; display: flex; flex-direction: column; justify-content: flex-end; min-height: 340px; border-radius: var(--r); overflow: hidden; text-decoration: none; border: 1px solid var(--border); isolation: isolate; }
.path img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .5s ease; }
.path::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(180deg, rgba(8,9,10,0) 30%, rgba(8,9,10,.75) 62%, rgba(8,9,10,.96) 100%); }
.path:hover img { transform: scale(1.04); }
.path:hover { border-color: rgba(0,154,68,.6); }
.path .tx { padding: 26px; }
.path h3 { font-size: clamp(28px, 3vw, 38px); }
.path p { margin: 8px 0 14px; color: var(--text-2); font-size: 14.5px; }
.path .go { font-size: 14px; font-weight: 600; color: var(--green-text); }
.offer .photo { aspect-ratio: 4 / 5; }
.offer p { margin: 0 0 14px; max-width: 62ch; }
.offer .first { margin-top: 16px; }
.matteo .photo img { width: auto; max-width: 92%; max-height: 100%; }
.matteo .role { color: var(--text); font-weight: 600; margin: 16px 0 0; }
.matteo .ctas { align-items: center; gap: 16px; }
.dests { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 200px), 1fr)); gap: 12px; }
.dest { position: relative; display: flex; align-items: flex-end; aspect-ratio: 4 / 3; border-radius: 10px; overflow: hidden; border: 1px solid var(--border); text-decoration: none; isolation: isolate; }
.dest img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .5s ease; }
.dest::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(180deg, rgba(8,9,10,0) 35%, rgba(8,9,10,.9) 100%); }
.dest:hover img { transform: scale(1.05); }
.dest:hover { border-color: rgba(0,154,68,.6); }
.dest-h { margin: 0; padding: 12px 14px; font: 400 18px/1.1 var(--head); letter-spacing: .02em; text-transform: uppercase; color: var(--text); }
.eb-pill { display: inline-flex; align-items: center; gap: 8px; color: #fff; background: rgba(8,9,10,.7); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 12px; margin-bottom: 18px; }
.eb-pill .dot { margin-right: 0; }   /* category label: still dot (shared/dot) */
/* Cigala status dot, shared by every site (Matteo, 15 Nov 2026). Source: the Tours early-bird dot.
   .dot            still dot, for labels (category tags): no movement
   .dot.live       pulsing dot, ONLY for something time-sensitive or changing:
                   early-bird price, "few places left", shop "in stock" / "low stock"
   Colours: default red (#e10600), .green (#009a44, in stock / open), .amber (#f0bf00, low stock), .sand (gravel #c9a36a)
   The pulse stops for visitors who ask for reduced motion. */
.dot { display: inline-block; flex: none; width: 7px; height: 7px; border-radius: 50%; background: #e10600; vertical-align: 1px; margin-right: 7px; --dot-rgb: 225,6,0; }
.dot.green { background: #009a44; --dot-rgb: 0,154,68; }
.dot.amber { background: #f0bf00; --dot-rgb: 240,191,0; }
.dot.sand  { background: #c9a36a; --dot-rgb: 201,163,106; }
.dot.live  { animation: cigala-dot-pulse 1.8s ease-in-out infinite; }
@keyframes cigala-dot-pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(var(--dot-rgb), .7); opacity: 1; } 50% { box-shadow: 0 0 0 5px rgba(var(--dot-rgb), 0); opacity: .55; } }
@media (prefers-reduced-motion: reduce) { .dot.live { animation: none; } }

.btn-h { margin: 0; font: inherit; text-transform: none; letter-spacing: normal; }
.band .tx { min-height: 360px; display: flex; flex-direction: column; justify-content: center; align-items: flex-start; }
.decade img { width: 100%; height: auto; max-width: 760px; margin: 0 auto; border-radius: var(--r); border: 1px solid var(--border); }
.seen { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; margin: 0; }
.seen span { width: auto; height: 96px; }
.seen img { max-height: 64px; max-width: 100%; object-fit: contain; }
.band-cta::after { background: linear-gradient(90deg, rgba(8,9,10,.94) 0%, rgba(8,9,10,.75) 50%, rgba(8,9,10,.2) 100%); }
.band-cta > img { object-position: center 30%; }
.dd { position: relative; }
.dd-btn { font: 600 12.5px var(--body); letter-spacing: .04em; text-transform: uppercase; color: var(--text-2); background: none; border: 0; padding: 8px 10px; border-radius: 6px; cursor: pointer; }
.dd-btn:hover, .dd:focus-within .dd-btn { color: #fff; background: var(--wash); }
.dd-menu { position: absolute; top: 100%; left: 0; min-width: 230px; display: none; padding: 8px; background: var(--panel-solid); border: 1px solid var(--border-strong); border-radius: 10px; box-shadow: 0 16px 40px rgba(0,0,0,.5); z-index: 50; }
.dd:hover .dd-menu, .dd:focus-within .dd-menu, .dd.open .dd-menu { display: grid; }
.dd-menu a { display: block; padding: 9px 12px; text-transform: none; letter-spacing: 0; font-size: 14px; }
.burger nav { max-height: calc(100svh - 80px); overflow-y: auto; }
.burger details.sub { border-bottom: 1px solid var(--border); }   /* same as Tours (tools/build_tours_home.py) */
.burger details.sub > summary { border: 0; border-radius: 0; background: none; list-style: none; cursor: pointer; display: flex; justify-content: space-between; align-items: center; padding: 11px 0; font-weight: 600; text-transform: uppercase; font-size: 13px; letter-spacing: .05em; color: var(--text); }
.burger details.sub > summary::-webkit-details-marker { display: none; }
.burger details.sub > summary::after { content: ""; width: 8px; height: 8px; border-right: 2px solid var(--green-text); border-bottom: 2px solid var(--green-text); transform: rotate(45deg); margin: -4px 4px 0 0; transition: transform .2s; }
.burger details.sub[open] > summary::after { transform: rotate(-135deg); margin-top: 4px; }
.burger details.sub .sub-links { display: grid; padding: 0 0 8px 14px; border-left: 2px solid var(--border); margin: 0 0 6px 2px; }
.burger details.sub .sub-links a { border-bottom: 0; padding: 9px 0; font-size: 12.5px; color: var(--text-2); }
.burger details.sub .sub-links a[aria-current="page"] { padding-left: 12px; color: var(--text); }
.burger details.sub > summary:focus-visible { outline: 2px solid var(--green); outline-offset: 2px; }
.burger nav a { text-transform: none; font-size: 15px; letter-spacing: 0; }
.fcols { grid-template-columns: minmax(0, 1.4fr) repeat(3, minmax(0, 1fr)) !important; }
footer .tag-line { font-size: 22px; font-weight: 400; }
footer .tag-sub { margin: 10px 0 0; font: 600 13px var(--body); letter-spacing: .06em; text-transform: none; color: var(--green-text); }
footer .contact { margin-top: 16px; }
footer .mt { margin-top: 22px; }
footer .intl h2 { margin: 0; font: 400 14px/1.5 var(--body); text-transform: none; letter-spacing: 0; }
footer .intl h2 a { color: var(--text-2); text-decoration: none; }
footer .intl h2 a:hover { color: #fff; }
footer .in.social { display: flex; flex-wrap: wrap; gap: 8px; padding-bottom: 24px; }
.social a { font-size: 12.5px; font-weight: 600; text-decoration: none; color: var(--text-2); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 12px; }
.social a:hover { color: #fff; border-color: var(--green); }
@media (max-width: 1080px) { .fcols { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important; } .fcols > div:first-child { grid-column: 1 / -1; } }
@media (max-width: 900px) { .matteo .photo { max-width: 520px; width: 100%; } .seen { grid-template-columns: repeat(3, minmax(0, 1fr)); } .offer .photo { aspect-ratio: 16 / 10; } }
@media (max-width: 640px) {
  .paths { grid-template-columns: minmax(0, 1fr); }
  .path { min-height: 340px; }
  .dests { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
  .dest-h { font-size: 16px; padding: 10px; }
  .seen { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .fcols { grid-template-columns: minmax(0, 1fr) !important; }
  .band-cta::after { background: linear-gradient(180deg, rgba(8,9,10,.6), rgba(8,9,10,.94)); }
}
/* logo with its own border: square corners (Matteo's file, 15 Nov) */
.brand img, .brand-lg img { border-radius: 0 !important; }
/* menu: every item on the same line, submenus in capitals like the other sites */
.menu { align-items: center; }
.dd-btn { line-height: 1.6; }
.dd-menu a { text-transform: uppercase !important; letter-spacing: .04em !important; font-size: 12.5px !important; font-weight: 600; }
.burger nav a { text-transform: uppercase !important; letter-spacing: .05em !important; font-size: 13px !important; }
/* ---- menu: same as cigalacycling.com (brand.css): hover = green word + 2px green line, current page = red line ---- */
.nav .in { position: relative; }
.menu a, .dd-btn { border-radius: 0; box-shadow: inset 0 0 0 var(--green); transition: color .15s, box-shadow .15s; }
.menu a:hover, .menu a:active, .dd-btn:hover, .dd:focus-within .dd-btn, .dd.open .dd-btn { color: var(--green-text); background: none; box-shadow: inset 0 -2px 0 var(--green); }
.menu a[aria-current="page"], .dd-btn.is-current { color: var(--text); box-shadow: inset 0 -2px 0 var(--red); }
.dd-menu a { border-radius: 0; color: var(--text-2); transition: color .15s, box-shadow .15s; }
.dd-menu a:hover, .dd-menu a:active { color: var(--green-text); background: none; box-shadow: inset 2px 0 0 var(--green); }
.dd-menu a[aria-current="page"] { color: var(--text); box-shadow: inset 2px 0 0 var(--red); }
.burger nav a { transition: color .15s; }
.burger nav a:hover, .burger nav a:active { color: var(--green-text); }
.burger nav a[aria-current="page"] { color: var(--text); box-shadow: inset 3px 0 0 var(--red); padding-left: 12px; }
/* ---- athlete review cards (sideways scroll) ---- */
.rv-wrap { position: relative; }
.rv-row { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(280px, calc((100% - 32px) / 3)); gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory; padding-bottom: 14px; scrollbar-width: thin; scrollbar-color: rgba(255,255,255,.2) transparent; }
.rv-row:focus-visible { outline: 2px solid var(--green); outline-offset: 4px; border-radius: 12px; }
.rv { transition: border-color .25s, box-shadow .25s, transform .25s; }
.rv:hover { border-color: var(--green) !important; box-shadow: 0 16px 40px rgba(0,154,68,.15); transform: translateY(-3px); }
.rv { margin: 0; scroll-snap-align: start; display: flex; flex-direction: column; gap: 14px; background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: var(--r); padding: 22px; min-width: 0; }
.rv-tag { align-self: flex-start; font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--green-text); background: var(--green-wash); border-radius: 999px; padding: 4px 10px; }
.rv blockquote { margin: 0; padding: 0; border: 0; font-style: normal; font-size: 15px; line-height: 1.6; color: var(--text-2); }
.rv figcaption { display: flex; align-items: center; gap: 12px; font-style: normal; margin-top: auto; padding-top: 14px; border-top: 1px solid var(--border); font-size: 14px; }
.rv figcaption b { display: block; color: var(--text); }
.rv figcaption img { width: 48px; height: 48px; flex: none; border-radius: 50%; object-fit: cover; border: 2px solid var(--green); }   /* like the Tours guest photos */
.rv figcaption span { color: var(--text-3); font-size: 13px; }
.rv-nav { display: flex; gap: 8px; justify-content: flex-end; margin-top: 6px; }
.rv-btn { width: 40px; height: 40px; border-radius: 50%; border: 1px solid var(--border-strong); background: var(--panel-solid); color: var(--text); font-size: 16px; cursor: pointer; }
.rv-btn:hover { border-color: var(--green); color: var(--green-text); }
.rv-links { display: flex; flex-wrap: wrap; gap: 10px 22px; align-items: center; }
@media (max-width: 900px) { .rv-row { grid-auto-columns: minmax(260px, 70%); } }
@media (max-width: 640px) { .rv-row { grid-auto-columns: 86%; } .rv-nav { display: none; } }
/* ---- shared social icon row (shared/social) ---- */
''' + SOCIAL_CSS + '''
.seen-tiles { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; }
.seen-tile { height: 96px; border-radius: 12px; overflow: hidden; display: grid; place-items: center; border: 1px solid var(--border); }
.seen-tile img.cover { width: 100%; height: 100%; object-fit: cover; }
.seen-tile img.mark { max-width: 64%; max-height: 46px; width: auto; height: auto; object-fit: contain; }
.seen-tile img.contain { max-width: 78%; max-height: 72px; width: auto; height: auto; object-fit: contain; }
@media (max-width: 900px) { .seen-tiles { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 480px) { .seen-tiles { grid-template-columns: repeat(2, minmax(0, 1fr)); } .seen-tile { height: 84px; } }
.mono-logos { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 28px 40px; padding: 8px 0; }
.mono-logos img { height: 46px; width: auto; max-width: 170px; object-fit: contain; opacity: .72; transition: opacity .15s; }
.mono-logos img:hover { opacity: 1; }
@media (max-width: 640px) { .mono-logos { justify-content: center; gap: 24px 32px; } .mono-logos img { height: 36px; max-width: 130px; } }
/* ---- Matteo 15 Nov homepage feedback ---- */
.hero::after { background: linear-gradient(180deg, rgba(8,9,10,.67) 0%, rgba(8,9,10,.55) 40%, rgba(8,9,10,.95) 100%) !important; }   /* hero photo darker (Matteo: twice, -5% each) */
.path img { filter: brightness(.95); }   /* coaching cards -5% (Matteo) */
.rv-stars { color: var(--star); letter-spacing: 3px; font-size: 15px; line-height: 1; }
.matteo .photo.cutout { position: relative; background: none; border: 0; aspect-ratio: auto; overflow: visible; display: flex; justify-content: center; align-items: flex-end; isolation: isolate; }
.matteo .photo.cutout::before { content: ""; position: absolute; inset: 10% 5% 0; background: radial-gradient(circle at 50% 45%, rgba(0,154,68,.25), rgba(8,9,10,0) 65%); z-index: -1; }
.matteo .photo.cutout img { width: 100%; max-width: 460px; max-height: none; height: auto; -webkit-mask-image: linear-gradient(180deg, #000 82%, transparent 100%); mask-image: linear-gradient(180deg, #000 82%, transparent 100%); }
.fam { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.card { position: relative; display: flex; flex-direction: column; justify-content: flex-end; min-height: 380px; border-radius: var(--r); overflow: hidden; border: 1px solid var(--border); background: var(--panel-solid); isolation: isolate; text-decoration: none; }
.card > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .6s ease; }
.card::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(180deg, rgba(8,9,10,0) 15%, rgba(8,9,10,.8) 50%, rgba(8,9,10,.98) 100%); }
.card:hover > img { transform: scale(1.04); }
.card:hover { border-color: rgba(0,154,68,.6); }
.card .tx { padding: 26px; display: grid; gap: 10px; text-shadow: 0 1px 10px rgba(0,0,0,.65); }
.card .k { justify-self: start; display: inline-flex; align-items: center; gap: 8px; font-size: 11.5px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #fff; text-shadow: none; background: rgba(8,9,10,.75); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 12px; }
.card .k::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--red); }   /* BRAND.md: eyebrow on a photo = dark pill + red dot */
.card h2, .card h3 { font-size: clamp(28px, 3vw, 38px); margin: 0; }
.card p { margin: 0; font-size: 14.5px; font-weight: 500; color: var(--text); }
.card .btn { justify-self: start; margin-top: 8px; text-shadow: none; }
.card .btn-h { margin: 0; }
.card .host { font-size: 12px; color: var(--text-2); }
@media (max-width: 900px) { .fam { grid-template-columns: minmax(0, 1fr); } .card { min-height: 420px; } }
@media (prefers-reduced-motion: reduce) { .card > img { transition: none; } .card:hover > img { transform: none; } }
/* ---- footer layout: as cigalacycling.com ---- */
.fcols { grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1.45fr) !important; }
footer .tag-line { font-size: 22px; line-height: 1.15; margin: 14px 0 0; max-width: 24ch; }
footer ul { font-size: 14px; }
footer ul a { color: var(--text-2); }
.legal .in { align-items: center; }
.intl-dd { position: relative; }
.intl-dd summary { list-style: none; cursor: pointer; font-size: 12px; color: var(--text-3); }
.intl-dd summary::-webkit-details-marker { display: none; }
.intl-dd summary::after { content: " ▾"; }
.intl-dd[open] summary::after { content: " ▴"; }
.intl-dd summary:hover { color: var(--green-text); }
.intl-dd .intl { list-style: none; margin: 0; padding: 10px 12px; position: absolute; bottom: calc(100% + 8px); left: 0; min-width: 240px; display: grid; gap: 4px; background: var(--panel-solid); border: 1px solid var(--border-strong); border-radius: 10px; box-shadow: 0 16px 40px rgba(0,0,0,.5); z-index: 5; }
.intl-dd .intl h2 { margin: 0; font: 400 13px/1.6 var(--body); text-transform: none; letter-spacing: 0; }
.intl-dd .intl a { color: var(--text-2); text-decoration: none; }
@media (max-width: 1080px) { .fcols { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important; } .fcols > div:first-child { grid-column: 1 / -1; } }
@media (max-width: 640px) { .intl-dd .intl { left: auto; right: 0; } .fcols { grid-template-columns: minmax(0, 1fr) !important; } }
/* ---- footer links: green-text on hover, no underline (Matteo, all sites, 15 Nov) ---- */
footer a { text-decoration: none; transition: color .15s, border-color .15s; }
footer a:hover, footer ul a:hover, footer .intl h2 a:hover, .legal a:hover, footer .social a:hover { color: var(--green-text); text-decoration: none; }
/* Anton titles: a little more line spacing (Matteo, all sites): H1 1.08, H2/H3 1.14 */
h1 { line-height: 1.08; }
h2, h3, .h-sec, .h-sm, .h-long, footer .tag-line { line-height: 1.14; }
/* intro text under page headings: 16px, as on cigalacycling.com (BRAND.md: intro 16px) */
.hero .lede { font-size: 16px; }
@media (prefers-reduced-motion: reduce) { .path img, .dest img { transition: none; } .path:hover img, .dest:hover img { transform: none; } }
</style>'''

JS = '''<script>
document.querySelectorAll('.dd').forEach(function (d) {
  var b = d.querySelector('.dd-btn');
  b.addEventListener('click', function () { var o = d.classList.toggle('open'); b.setAttribute('aria-expanded', o); });
  d.addEventListener('focusout', function (e) { if (!d.contains(e.relatedTarget)) { d.classList.remove('open'); b.setAttribute('aria-expanded', 'false'); } });
});
</script>'''


# ---------- athlete reviews (Matteo 15 Nov: own review cards instead of the Shapo widget; reviews chosen by Claude) ----------
# Quotes are the athletes' own words from the live Testimonials page (coaching/text/testimonials.txt); no star ratings,
# because these are testimonials, not rated reviews. The Google link goes to Matteo's Google Business Profile.
REVIEWS = [   # strongest first; photo = the image above each testimonial on the live Testimonials page (Matteo 15 Nov: Marine first; 15 Nov: mix in the athletes from other countries)
    ('', 'He has not only made me fall in love with cycling, but has believed in me even when I didn’t. As I speak, I am current European Gran Fondo & gravel 19-34 champion, silver medalist at the Gran Fondo Worlds, from only starting cycling last February this year.', 'Marine Lenehan', 'Now a WorldTour Pro · Ireland', 'T135849.182'),
    ('', 'With his expertise, support, and personalized approach, I have achieved my goal of qualifying for the UCI Granfondo World Championship.', 'Bernd Ondruch', 'Germany & UK', 'T134927.535'),   # Matteo 15 Nov: lives in both
    ('', 'First time was a 9 month training plan to get me from couch (literally!) to Haute Route Pyrenees in 2017 to mark my 60th birthday. More recently, I have worked with Matteo to help me recover from heart disease and a cardiac procedure.', 'Derek Lawler', 'Kilkenny, Ireland', 'T140239.558'),
    ('', 'After 7 weeks of following his programme, which is mainly working in Z1/2 with bits of Z3, I’ve managed to get a PB FTP of 207W.', 'Lisa Dunne', 'Al Jassra Race Team, Qatar', 'T140416.718'),
    ('', 'I had entered a seven-day mountain stage race in the USA… During the event, I felt stronger each day of the race and ended up in the top 50 in a highly competitive field which included full time international professional racers.', 'Ceall O’Dunlaing', 'Stage race in the USA', 'T142535.380'),
    ('', 'I truly had a tailor-made plan every single week, and as a result, I showed up to the Mallorca 312 in the best shape I’ve ever been in.', 'Ward Den Hollander', 'Dublin, Ireland', 'T140125.193'),
    ('', 'Matteo managed to raise my FTP from 220w to 260w in less than 4 months & my sprint from 600w ish to 920w.', 'Shane Courtney', 'Tralee Manor West ibike', 'T142905.118'),
    ('', 'Matteo Cigala has been an incredible cycling coach, helping me navigate training around my family and work commitments. Thanks to his guidance, I not only reached my targets but also hit all-time personal best power numbers.', 'John Dowley', 'Carrick-on-Suir, Ireland', 'T135954.721'),
    ('', 'I don’t have the free time to dedicate to hours of junk miles, and Matteo has perfectly optimised my training to adapt to what time I do have.', 'William Rymer', 'Roscrea, Tipperary, Ireland', 'T140040.590'),
    ('', 'I commenced the cycling season in February as an A2 and by March I had gained my first points finishing 2nd in the Lucan GP. Finally last week I achieved one of my goals for the season: I won the Connor Coombes GP.', 'Gerard Dunne', 'Navan Road Club', 'T142455.462'),
    ('', 'To date I’ve lost close to 16 kg thanks to Matteos coaching and support, most importantly I look forward to every session that is planned out for me.', 'Rob Kavanagh', 'Ireland', 'T143158.190'),
    ('', 'The big revelation for me has been how fresh I feel following a full winter training and spring racing schedule tailored by Matteo… Much less fatigued than ever before with less hours of training!', 'Damian Gannon', 'Swords Cycling Club', 'T140342.560'),
]
def reviews_strip():
    cards = ''.join(f'<figure class="rv"><div class="rv-stars" role="img" aria-label="5 stars">★★★★★</div><blockquote>“{E(q)}”</blockquote>'
                    f'<figcaption><img src="{img(ph, "athlete-" + re.sub(r"[^a-z]+", "-", n.lower()).strip("-"))}" alt="{E(live_alt(ph))}" loading="lazy" width="48" height="48"><div><b>{E(n)}</b><span>{E(w)}</span></div></figcaption></figure>'
                    for t, q, n, w, ph in REVIEWS)
    return (f'<div class="rv-wrap"><div class="rv-row" id="rv-row" tabindex="0" aria-label="Athlete reviews, scroll sideways">{cards}</div>'
            '<div class="rv-nav"><button type="button" class="rv-btn" data-d="-1" aria-label="Previous reviews">←</button><button type="button" class="rv-btn" data-d="1" aria-label="Next reviews">→</button></div></div>')
REVIEWS_JS = """<script>(function(){var r=document.getElementById('rv-row');if(!r)return;var red=matchMedia('(prefers-reduced-motion: reduce)').matches;
function go(d){var max=r.scrollWidth-r.clientWidth;if(d>0&&r.scrollLeft>=max-4){r.scrollTo({left:0,behavior:red?'auto':'smooth'});return;}r.scrollBy({left:d*r.clientWidth*0.85,behavior:red?'auto':'smooth'});}
document.querySelectorAll('.rv-btn').forEach(function(b){b.addEventListener('click',function(){stop=true;go(+b.dataset.d);});});
/* Matteo 15 Nov: the reviews move on slowly by themselves; they stop while you hover, touch or use the arrows */
var stop=red,hold=false;['mouseenter','focusin','touchstart'].forEach(function(e){r.addEventListener(e,function(){hold=true;},{passive:true});});
['mouseleave','focusout'].forEach(function(e){r.addEventListener(e,function(){hold=false;});});r.addEventListener('touchstart',function(){stop=true;},{passive:true});
var vis=false;if('IntersectionObserver' in window)new IntersectionObserver(function(es){vis=es[0].isIntersecting;}).observe(r);
setInterval(function(){if(!stop&&!hold&&vis&&!document.hidden)go(1);},5000);})();</script>"""

LIVE = {r['url']: r for r in json.load(open(ROOT + 'coaching/baseline.json'))}
ALTS = {}
for _r in LIVE.values():
    for _i in _r.get('images') or []:
        if _i['src'] and _i['alt']: ALTS.setdefault(_i['src'].split('/uploads/')[-1], _i['alt'])

def live_alt(key):
    """Live alt text for an image whose uploads path contains key."""
    hits = {a for u, a in ALTS.items() if key in u}
    assert len(hits) == 1, (key, hits)
    return hits.pop()

def build(name, path, main, ribbon, h1=None, h2_changes=None, extra_css='', extra_js='', new_page=None):
    """Write coachingpages/<name>.html and check it against the live page at <path>.
    h1: the approved H1 when it differs from live (SEO-DECISIONS.md). h2_changes: {'drop': [...], 'add': [...]} approved H2 changes."""
    # new_page: {'title', 'meta'} for a page that does not exist on live yet (no H2s to keep)
    live = LIVE[C + path] if not new_page else {'title': new_page['title'], 'meta_description': new_page['meta'], 'h1': [h1], 'h2': None}
    page = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(live['title'])}</title>
<meta name="description" content="{E(live['meta_description'] or '')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="icon" href="{LOGO}">
</head><body>
{BASE}
{CSS}
{extra_css}
<div class="topo" aria-hidden="true"></div>
<div class="page">
<div class="ribbon"><div class="in"><b>Preview</b><span>{E(ribbon)}</span></div></div>
{HEADER}
{main}
{FOOTER}
</div>
{JS}{extra_js}
</body></html>
'''
    open(OUT + name + '.html', 'w').write(page)
    want_h1 = [h1] if h1 else live['h1'][:1]
    got_h1 = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<h1[^>]*>(.*?)</h1>', page, re.S)]
    assert got_h1 == want_h1, (got_h1, want_h1)
    h2 = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<h2[^>]*>(.*?)</h2>', page, re.S)]
    ch = h2_changes or {}
    if live['h2'] is None: live = dict(live, h2=[x for x in h2])   # new page: nothing on live to keep
    # sitewide approved change (Matteo 15 Nov, SEO-DECISIONS.md section 8): the footer tagline H2
    FOOTER_H2 = {'Cycling & Triathlon Coaching - Bike Tours - Retail': 'TRAIN SMARTER. RIDE FASTER.'}
    want = [FOOTER_H2.get(x, x) for x in live['h2'] if x not in ch.get('drop', [])] + ch.get('add', [])
    missing = sorted({x for x in want if x not in h2}); extra = sorted({x for x in h2 if x not in want})
    assert not missing and not extra, ('H2 missing', missing, 'extra', extra)
    bad = [t for t in re.findall(r'<img\b[^>]*>', page) if ' alt="' not in t]
    assert not bad, bad
    print(f'wrote coachingpages/{name}.html', len(page), 'bytes; H1 ok;', len(set(want)), 'H2s match live')
    return page

