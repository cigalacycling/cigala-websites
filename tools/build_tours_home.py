"""Build the Tours homepage preview: tourspages/home.html

Source design: survey/NfmCmGsjq4LL9bTAi38NXN/index.html
Changes on top of the design (approved by Matteo, 15 Nov 2026):
  - H1 keeps the live wording
  - tour finder (Month / Tour type / Country / Level) in the hero
  - all 15 tours from tours/trips-2027.json, with dates as real text
  - Bike Tours menu keeps the live split and adds Road Tours
Images are copied into tourspages/img/ (home-*) so the preview opens locally.
"""
import os, re, sys, json, html, shutil, urllib.request, ssl
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
SRC = ROOT + 'survey/NfmCmGsjq4LL9bTAi38NXN/index.html'
OUT = ROOT + 'tourspages/'
L = 'https://tours.cigalacycling.com'
E = lambda x: html.escape(x, quote=True)
EXT = 'target="_blank" rel="noopener"'

s = open(SRC).read()
trips = json.load(open(ROOT + 'tours/trips-2027.json'))['trips']

# ---------- images ----------
def cp(src, name):
    dst = OUT + 'img/' + name
    if not os.path.exists(dst):
        shutil.copy(ROOT + src, dst)
    return 'img/' + name

def fetch(url, name):
    dst = OUT + 'img/' + name
    if not os.path.exists(dst):
        ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
        with urllib.request.urlopen(url, context=ctx, timeout=60) as r, open(dst, 'wb') as f:
            f.write(r.read())
    return 'img/' + name

IMG = {
    'img/hero.jpg': cp('cand/img/hero.jpg', 'home-hero.jpg'),
    'img/custom.jpg': cp('cand/img/custom.jpg', 'home-custom.jpg'),
    'img/cta.jpg': cp('cand/img/cta.jpg', 'home-cta.jpg'),
    'img/matteo.png': cp('survey/NfmCmGsjq4LL9bTAi38NXN/matteo-white.png', 'home-matteo.png'),
    'img/story.jpg': fetch(L + '/wp-content/uploads/2026/07/1720641-scaled.jpg', 'home-story.jpg'),
    'img/g_flanders.jpg': 'img/guides-0.jpg',
    'img/g_como.jpg': 'img/guides-1.jpg',
    'img/g_pack.jpg': 'img/guides-2.jpg',
    'img/p_mdd.png': 'img/logo-mdd.png',
    'img/p_8.jpg': 'img/logo-lombardia.png',
    'img/p_1.jpg': 'img/logo-strade.png',
    'img/p_11.jpg': 'img/logo-algarve.png',
    'img/logo.png': 'img/logo.png',
}
for k, v in IMG.items():
    s = s.replace(f'src="{k}"', f'src="{v}"')

# guest photos: the live homepage crops, rebuilt from the originals (webp-tours/cigala-tours-guest-*.webp)
s = re.sub(r'src="img/t_([a-z]+)\.(?:jpg|png)"', r'src="img/cigala-tours-guest-\1.webp"', s)

# ---------- small fixes ----------
s = s.replace(L + '/trips/destinations/', L + '/destinations/')   # wrong link in the design
s = s.replace(L + '/trips/granfondo/', L + '/trips/granfondo-trips/')  # final URL, skip the 301
s = s.replace('<b>Design preview</b><span>A concept of the tours homepage in the Cigala Cycling brand. Content and photos come from the live site; links go to the live pages.</span>',
              '<b>Preview</b><span>New Tours homepage with the tour finder. Links go to the live pages until staging is ready.</span>')

# ---------- H1: live wording ----------
LIVE_H1 = "Bike Tours &amp; Cycling Holidays Across Europe's Best Cycling Destinations"
s = s.replace("<h1>Bike tours across Europe's best cycling roads</h1>", f'<h1>{LIVE_H1}</h1>')

# ---------- H2: live wording (SEO rule), design wording moves to the eyebrow ----------
H2_FIX = [
    ('<h2>Italy, France, Spain, Portugal, Slovenia, Croatia, Cyprus and more</h2>', '<h2>Bike Tours in Italy, France, Spain, Portugal, Slovenia, Croatia, Cyprus and more</h2>'),
    ('Meet our Tours Director</div>', 'Ride with Matteo Cigala</div>'),
    ('<h2>Ride with Matteo Cigala</h2>', '<h2>Meet Our Tours Director</h2>'),
    ('Ten years of guests</div>', 'What our riders say</div>'),
    ('<h2>What our riders say</h2>', '<h2>Read what our guests from the last 10 years have to say</h2>'),
]
for a, b in H2_FIX:
    assert s.count(a) == 1, a
    s = s.replace(a, b)

# ---------- menu ----------
MENU_TOURS = [   # order from Matteo (15 Nov): all, road, gravel, gran fondo, italian, custom
    ('All tours', '/trips/'),
    ('Road tours', '/trips/road-trips/'),
    ('Gravel tours', '/trips/gravel-trips/'),
    ('Gran Fondo tours', '/trips/granfondo-trips/'),
    ('Italian tours', '/italian-trips/'),
    ('Custom tours', '/trips/private-trips/'),
]
MENU_SUB = [m for m in MENU_TOURS if m[0] != 'Custom tours']   # Custom tours is its own menu item (Matteo, 15 Nov)
dd = ''.join(f'<a href="{L}{u}" {EXT}>{t}</a>' for t, u in MENU_SUB)
s = s.replace(f'<a href="{L}/trips/" {EXT}>Bike tours</a>',
              f'<div class="dd"><button type="button" class="dd-btn" aria-expanded="false" aria-haspopup="true">Bike tours <span aria-hidden="true">▾</span></button><div class="dd-menu">{dd}</div></div>')
s = s.replace(f'<a href="{L}/trips/gravel-trips/" {EXT}>Gravel tours</a>\n        <a href="{L}/trips/private-trips/" {EXT}>Custom tours</a>',
              f'<a href="{L}/trips/gravel-trips/" {EXT}>Gravel tours</a>\n        <a href="{L}/trips/road-trips/" {EXT}>Road tours</a>\n        <a href="{L}/trips/private-trips/" {EXT}>Custom tours</a>')

# ---------- tour data ----------
MON = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MONTH = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
TYPE = {'road': 'Road', 'gf': 'Gran Fondo', 'gravel': 'Gravel'}
# short card copy: the design's lines, or the first sentence of the live card text
BLURB = {
    'discover-the-algarve-granfondo': 'Early season sunshine, watch the pros and ride the Gran Fondo.',
    'chianti-gran-fondo-strade-bianche': 'Ride the rolling hills of Chianti, watch the pros and ride the Gran Fondo.',
    'tour-of-flanders-experience': 'Ride it. Watch it. Live it. Take on the cobbles in the ultimate cycling experience.',
    'cyprus-crossing-gravel': 'A lifetime trip in one of the most beautiful islands in Europe.',
    'tuscany-epic-gravel': 'An incredible trip across Italy’s best region for gravel, on the Tuscany Trail route.',
    'maratona-dles-dolomites': 'Official Tour Operator of the Maratona dles Dolomites – Enel, for the 40th edition on 4 July 2027.',
    'dolomites': 'Giau, Gardena, Sella, Pordoi, Falzarego, Fedaia and Tre Cime di Lavaredo.',
    'italian-alps': 'Iconic Giro climbs including Stelvio, Gavia, Mortirolo and Cancano.',
    'alpine-gravel-escape': 'Take on the Stelvio Gravel and explore the Alps on remote gravel roads and mountain passes.',
    'french-alps': 'Conquer legendary climbs including Galibier, Alpe d’Huez, Izoard and Cime de la Bonette.',
    'wonderful-slovenia': 'From the Julian Alps and Vršič Pass to the turquoise Soča Valley and Lake Bled.',
    'lake-garda-and-stelvio': 'From the shores of Lake Garda to the legendary Stelvio Pass.',
    'lake-garda-gravel': 'Discover Lake Garda’s hidden side on gravel roads, mountain tracks and quiet countryside.',
    'italys-coast-to-coast': 'From the Tyrrhenian Sea to the Adriatic Sea, through Tuscany, Umbria and Marche.',
    'lake-como-gran-fondo-il-lombardia': 'Discover Lake Como, watch the pros and ride the Gran Fondo “Il Lombardia”.',
}
SHORT = {'Discover the Algarve & Gran Fondo': 'Algarve & Gran Fondo', 'Chianti & Gran Fondo Strade Bianche': 'Chianti & Strade Bianche',
         'Cyprus Crossing | Gravel': 'Cyprus Crossing', 'Tuscany Epic | Gravel': 'Tuscany Epic',
         'Lake Garda & Day Trip to Stelvio': 'Lake Garda & Stelvio', 'Lake Como, Gran Fondo Il Lombardia & Pro Race': 'Lake Como & Il Lombardia'}

def dates(t):
    a, b = date.fromisoformat(t['start']), date.fromisoformat(t['end'])
    if a.month == b.month:
        return f'{a.day}–{b.day} {MON[a.month]} {b.year}'
    return f'{a.day} {MON[a.month]} – {b.day} {MON[b.month]} {b.year}'

def months(t):
    a, b = date.fromisoformat(t['start']), date.fromisoformat(t['end'])
    return [str(m) for m in range(a.month, b.month + 1)]

BADGE = json.load(open(ROOT + 'tours/badges.json'))   # Gran Fondo badges from the survey design
BADGE = {'entry': BADGE['entry'], 'support': BADGE['support']}
cards = []
for t in trips:
    lv = [x.strip().lower() for x in t['level'].split(',')]
    img = f'img/trip-{t["slug"]}.webp'  # featured photo of the live trip page, WebP q90
    name = SHORT.get(t['name'], t['name'])
    a = date.fromisoformat(t['start'])
    cards.append(
        f'<a class="tour" data-k="{t["type"]}" data-country="{t["country"].lower()}" data-month="{" ".join(months(t))}" data-level="{" ".join(lv)}" href="{t["url"]}" {EXT}>'
        f'<img src="{img}" alt="{E(name)} bike tour" loading="lazy">'
        f'<span class="tag{" gravel" if t["type"] == "gravel" else ""}">{TYPE[t["type"]]}</span>'
        f'<div class="tx">{BADGE.get(t.get("badge"), "")}<time class="when" datetime="{t["start"]}">{dates(t)}</time>'
        f'<h3>{E(name)}</h3><p>{E(BLURB[t["slug"]])}</p>'
        f'<span class="facts"><span>{t["country"]}</span><span>{t["distance"]}</span><span>{t["climbing"]} climbing</span></span>'
        f'<span class="go">View tour →</span></div></a>')

# ---------- finder ----------
used_months = sorted({int(m) for t in trips for m in months(t)})
countries = []
for t in trips:
    if t['country'] not in countries: countries.append(t['country'])
countries.sort()

def opts(first, pairs):
    return f'<option value="">{first}</option>' + ''.join(f'<option value="{v}">{t}</option>' for v, t in pairs)

finder = f'''
    <form class="finder" id="finder" role="search" aria-label="Find a tour" action="{L}/trips/">
      <label class="fi"><span>Month</span><select name="month" id="q-month">{opts("Any month", [(m, MONTH[m] + " 2027") for m in used_months])}</select></label>
      <label class="fi"><span>Tour type</span><select name="type" id="q-type">{opts("Any type", [("road", "Road"), ("gravel", "Gravel"), ("gf", "Gran Fondo")])}</select></label>
      <label class="fi"><span>Country</span><select name="country" id="q-country">{opts("Any country", [(c.lower(), c) for c in countries])}</select></label>
      <label class="fi"><span>Level</span><select name="level" id="q-level">{opts("Any level", [("beginner", "Beginner"), ("intermediate", "Intermediate"), ("expert", "Expert")])}</select></label>
      <button class="btn btn-go" type="submit">Find tours</button>
    </form>'''

s = re.sub(r'(<p class="lede">From Italy’s lakes.*?</p>)\s*<div class="ctas">.*?</div>', lambda m: m.group(1) + finder, s, count=1, flags=re.S)

# grid + result line (replaces the old chips)
s = re.sub(r'<div class="filters" role="group" aria-label="Filter tours">.*?</div>', '', s, count=1, flags=re.S)
s = re.sub(r'<div class="tours" id="tour-grid">.*?</div>\s*<div class="center">',
           '<div class="result" id="result" aria-live="polite"><span id="r-count">15 tours in 2027</span>'
           '<a id="r-cat" class="arrow-link" hidden href="#"></a>'
           '<button type="button" class="reset" id="r-reset" hidden>Clear filters</button></div>\n'
           '    <p class="none" id="r-none" hidden>No tour matches all of these. Try another month or level, or <a href="' + L + '/trips/private-trips/" ' + EXT + '>ask us for a custom tour</a>.</p>\n'
           '    <div class="tours" id="tour-grid">\n      ' + '\n      '.join(cards) + '\n    </div>\n    <div class="center">',
           s, count=1, flags=re.S)
s = s.replace('Our 2027 public tours, from February to November.', 'Our 2027 public tours, from February to October.')

# ---------- CSS ----------
CSS = '''
/* ---- finder, menu dropdown, tour facts (15 Nov 2026) ---- */
.hero h1 { font-size: clamp(38px, 5.2vw, 72px); max-width: 22ch; }
#tours { scroll-margin-top: 70px; }
.finder { margin-top: 26px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)) auto; align-items: stretch; background: rgba(15,16,17,.9); border: 1px solid var(--border-strong); border-radius: 16px; padding: 8px; gap: 0; max-width: 980px; box-shadow: 0 18px 50px rgba(0,0,0,.45); backdrop-filter: blur(6px); }
.fi { display: grid; gap: 2px; padding: 8px 14px; border-right: 1px solid var(--border); min-width: 0; position: relative; }
.fi span { font-size: 11px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--red); }
.fi select { appearance: none; -webkit-appearance: none; width: 100%; min-width: 0; font: 600 16px/1.3 var(--body); color: var(--text); background: transparent; border: 0; padding: 2px 18px 2px 0; cursor: pointer; background-image: linear-gradient(45deg, transparent 50%, var(--green-text) 50%), linear-gradient(135deg, var(--green-text) 50%, transparent 50%); background-position: right 5px center, right 0 center; background-size: 5px 5px; background-repeat: no-repeat; }
.fi select:focus-visible { outline: 2px solid var(--green); outline-offset: 4px; border-radius: 4px; }
.fi select option { color: #111; background: #fff; }
.finder .btn { margin: 4px; padding: 14px 26px; font-size: 14px; border-radius: 10px; white-space: nowrap; }
.dd { position: relative; }
.dd-btn { font: 600 12.5px var(--body); letter-spacing: .04em; text-transform: uppercase; color: var(--text-2); background: none; border: 0; padding: 8px 10px; border-radius: 6px; cursor: pointer; }
.dd-btn:hover, .dd:focus-within .dd-btn { color: #fff; background: var(--wash); }
.dd-menu { position: absolute; top: 100%; left: 0; min-width: 210px; display: none; padding: 8px; background: var(--panel-solid); border: 1px solid var(--border-strong); border-radius: 10px; box-shadow: 0 16px 40px rgba(0,0,0,.5); z-index: 50; }
.dd:hover .dd-menu, .dd:focus-within .dd-menu, .dd.open .dd-menu { display: grid; }
.dd-menu a { display: block; padding: 9px 12px; }
.result { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; margin: 0 0 18px; font-weight: 600; color: var(--text-2); }
.result #r-count { color: var(--text); }
.reset { font: 600 13px var(--body); color: var(--text-2); background: var(--wash); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 14px; cursor: pointer; }
.reset:hover { color: #fff; }
.none { color: var(--text-2); margin: 0 0 18px; }
.none a { color: var(--green-text); }
.tour .entry { display: flex; width: fit-content; background: rgba(8,9,10,.72); backdrop-filter: blur(4px); }
.tour .when { display: inline-block; font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #fff; background: var(--red); border-radius: 6px; padding: 4px 9px; margin-bottom: 10px; }
.tour .facts { display: flex; flex-wrap: wrap; gap: 4px 12px; margin: -4px 0 12px; font-size: 12.5px; font-weight: 600; color: var(--text-3); }
.tour[hidden] { display: none; }
.who .av { width: 40px; height: 40px; border-radius: 50%; flex: none; display: grid; place-items: center; font-family: var(--head); font-size: 18px; color: #fff; background: var(--green); }
@media (max-width: 900px) {
  .finder { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .fi:nth-child(2) { border-right: 0; }
  .fi:nth-child(-n+2) { border-bottom: 1px solid var(--border); }
  .finder .btn { grid-column: 1 / -1; }
}
@media (max-width: 520px) {
  .finder { grid-template-columns: minmax(0, 1fr); padding: 6px; }
  .fi { border-right: 0; border-bottom: 1px solid var(--border); padding: 10px 12px; }
  .hero .in { padding-block: 96px 36px; }
}
'''
s = s.replace('@media (max-width: 1080px)', CSS + '\n@media (max-width: 1080px)', 1)

# ---------- JS ----------
CAT = {  # a single choice that has its own category page
    'type:gf': ('/trips/granfondo-trips/', 'Gran Fondo tours page'),
    'type:gravel': ('/trips/gravel-trips/', 'Gravel tours page'),
    'type:road': ('/trips/road-trips/', 'Road tours page'),
    'country:italy': ('/italian-trips/', 'Italian tours page'),
}
JS = '''<script>
(function () {
  var f = document.getElementById('finder');
  var cards = [].slice.call(document.querySelectorAll('#tour-grid .tour'));
  var q = { month: f.month, type: f.type, country: f.country, level: f.level };
  var CAT = %s, L = '%s';
  var count = document.getElementById('r-count'), cat = document.getElementById('r-cat');
  var reset = document.getElementById('r-reset'), none = document.getElementById('r-none');
  function apply() {
    var v = {}; Object.keys(q).forEach(function (k) { v[k] = q[k].value; });
    var n = 0;
    cards.forEach(function (c) {
      var ok = (!v.month || c.dataset.month.split(' ').indexOf(v.month) > -1) &&
               (!v.type || c.dataset.k === v.type) &&
               (!v.country || c.dataset.country === v.country) &&
               (!v.level || c.dataset.level.split(' ').indexOf(v.level) > -1);
      c.hidden = !ok; if (ok) n++;
    });
    var picked = Object.keys(v).filter(function (k) { return v[k]; });
    count.textContent = picked.length ? n + (n === 1 ? ' tour matches' : ' tours match') : cards.length + ' tours in 2027';
    var c1 = picked.length === 1 && CAT[picked[0] + ':' + v[picked[0]]];
    cat.hidden = !c1; if (c1) { cat.href = L + c1[0]; cat.textContent = 'See the ' + c1[1] + ' →'; }
    reset.hidden = !picked.length; none.hidden = n > 0;
  }
  Object.keys(q).forEach(function (k) { q[k].addEventListener('change', apply); });
  f.addEventListener('submit', function (e) {
    e.preventDefault(); apply();
    document.getElementById('tours').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  });
  reset.addEventListener('click', function () { f.reset(); apply(); });
  document.querySelectorAll('.dd').forEach(function (d) {
    var b = d.querySelector('.dd-btn');
    b.addEventListener('click', function () { var o = d.classList.toggle('open'); b.setAttribute('aria-expanded', o); });
    d.addEventListener('focusout', function (e) { if (!d.contains(e.relatedTarget)) { d.classList.remove('open'); b.setAttribute('aria-expanded', 'false'); } });
  });
  apply();
})();
</script>''' % (json.dumps({k: list(v) for k, v in CAT.items()}), L)
s = re.sub(r'<script>\s*\(function \(\) \{\s*var chips.*?</script>', lambda m: JS, s, count=1, flags=re.S)


# ---------- Matteo's feedback, 15 Nov 2026 ----------
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)

# hero: shorter text. The long live paragraph moves down under "Bike Tours in Italy, France..." (kept on the page)
m = re.search(r'\s*<p class="lede">From Italy’s lakes.*?</p>', s, re.S)
long_lede = m.group(0).strip().replace('<p class="lede">', '<p class="lede">', 1)
s = s[:m.start()] + '\n    <p class="lede">Fully supported cycling tours across Europe’s best roads, guided by former pro riders.</p>' + s[m.end():]
rep('<p class="lede">Our 2027 public tours, from February to October.', long_lede + '\n        <p class="lede">Our 2027 public tours, from February to October.')
# stats
rep('<div class="stat"><div class="n">500+</div><div class="l">Cyclists guided</div></div>', '<div class="stat"><div class="n">700+</div><div class="l">Cyclists guided</div></div>')
# green buttons
rep('<a class="btn btn-ghost" href="https://tours.cigalacycling.com/about/" target="_blank" rel="noopener">Read our story →</a>', '<a class="btn btn-go" href="https://tours.cigalacycling.com/about/" target="_blank" rel="noopener">Read our story →</a>')
rep('<a class="btn btn-ghost" href="https://tours.cigalacycling.com/about/" target="_blank" rel="noopener">Meet Matteo &amp; the team →</a>', '<a class="btn btn-go" href="https://tours.cigalacycling.com/about/" target="_blank" rel="noopener">Meet Matteo &amp; the team →</a>')
# Matteo's titles: same list as cigalacycling.com
s = re.sub(r'<ul class="creds">.*?</ul>', '<ul class="creds">\n        <li>European Road Champion Gran Fondo</li>\n        <li>UCI Gran Fondo Vice World Champion</li>\n        <li>UCI Gravel Vice World Champion</li>\n        <li>Italian Gravel Champion</li>\n        <li>200+ race wins</li>\n      </ul>', s, count=1, flags=re.S)
# signature under the name in "Our story" (cut from the coaching blog; typed name stays for Google and screen readers)
rep('<p class="sig">Matteo Cigala<span>Tours Director</span></p>', '<img class="signature" src="img/cigala-tours-signature.webp" alt="Matteo Cigala\'s signature" width="924" height="251" loading="lazy">\n      <p class="sig">Matteo Cigala<span>Tours Director</span></p>')  # letter style: signature, then typed name
# phone menu: same order as the desktop menu, with Bike tours as a sub-menu (Matteo, 15 Nov)
m = re.search(r'(<nav aria-label="Main \(mobile\)">)(.*?)(\n      </nav>)', s, re.S)
sub = ''.join(f'\n            <a href="{L}{u}" {EXT}>{t}</a>' for t, u in MENU_SUB)
mob_items = [('About us', L + '/about/'), ('Destinations', L + '/destinations/'), None,
             ('Custom tours', L + '/trips/private-trips/'), ('Cycling guides', L + '/guides/'),
             ('Coaching', 'https://coaching.cigalacycling.com/'), ('Shop', 'https://retail.cigalacycling.com/'),
             ('Testimonials', L + '/testimonials/'), ('Contact', L + '/contact/')]
body = ''
for it in mob_items:
    if it is None:
        body += f'\n        <details class="sub"><summary>Bike tours</summary><div class="sub-links">{sub}\n          </div></details>'
    else:
        body += f'\n        <a href="{it[1]}" {EXT}>{it[0]}</a>'
s = s[:m.start()] + m.group(1) + body + m.group(3) + s[m.end():]

# icons instead of 01-06 in 'Why ride with us' (Matteo, 15 Nov)
WHY_ICONS = {'01': '<circle cx="9" cy="8" r="3.2"/><path d="M3 19c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5"/><circle cx="17" cy="9" r="2.6"/><path d="M15.5 13.7c2.9.3 5 2.3 5 5.3"/>', '02': '<circle cx="5.5" cy="16.5" r="3.5"/><circle cx="18.5" cy="16.5" r="3.5"/><path d="M5.5 16.5 9 9h6l3.5 7.5M9 9l3 7.5H5.5M12 16.5 15 9M13.5 6h3"/>', '03': '<path d="M2 7h11v9H2zM13 10h4.5l3.5 3.5V16h-8"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>', '04': '<path d="M3 18V6M3 14h18v4M21 14v-2.5A2.5 2.5 0 0 0 18.5 9H11v5"/><circle cx="7" cy="11" r="1.8"/>', '05': '<path d="M2 19 9 7l4 6 2.5-3.5L22 19z"/>', '06': '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>'}
for n, svg in WHY_ICONS.items():
    rep(f'<div class="num">{n}</div>', f'<div class="ico"><svg viewBox="0 0 24 24" aria-hidden="true">{svg}</svg></div>')
# one quiet line under the signature
# signature, then 'Matteo Cigala', then 'Tours Director' underneath (Matteo, 15 Nov): the design's two-line format stays

# partners: no longer an official partner of the Algarve Granfondo (Matteo, 15 Nov) -> 'Event day support' with Algarve + Flanders
rep('<div class="lab">Official event partner</div><div class="logos"><span><img src="img/logo-algarve.png" alt="Algarve Granfondo" loading="lazy"></span></div>',
    '<div class="lab">Event day support</div><div class="logos"><span><img src="img/logo-algarve.png" alt="Algarve Granfondo" loading="lazy"></span><span class="fill"><img src="img/logo-wrf.png" alt="We Ride Flanders logo" loading="lazy"></span></div>')
# Tours is its own company (shared/BUSINESS.md, Matteo 15 Nov): footer legal row + reviews link to the Tours Google profile
rep('<span>© 2026 Cigala Cycling Tours Ltd</span>\n    <span>VAT No: IE4385007EH · Company Registration No: 780307</span>',
    '<span>© 2026 Cigala Cycling Tours Ltd · Registered in Ireland No. 780307 · VAT IE4385007EH</span>')
s = s.replace('<div class="stars" aria-label="5 out of 5">★★★★★</div>', '')   # no star ratings on our own reviews (same as Coaching)
rep(f'<a class="arrow-link" href="{L}/testimonials/" {EXT}>All testimonials →</a>',
    f'<div class="rv-links"><a class="arrow-link" href="https://share.google/WNvIKe4CJP8CnL8ns" {EXT}>★ Read our reviews on Google →</a><a class="arrow-link" href="{L}/testimonials/" {EXT}>All testimonials →</a></div>')

# footer social links -> shared icon row (shared/social, Matteo 15 Nov), under phone / email / Google reviews
sys.path.insert(0, ROOT + 'shared/social'); from social import social_row, SOCIAL_CSS
m = re.search(r'(<h4>Contact</h4>\s*<ul>\s*<li>tours@cigalacycling\.com</li>\s*<li>\+353 40478107</li>)\s*<li><a href="https://wa\.me.*?</li>\s*<li><a href="https://www\.youtube.*?</li>\s*</ul>', s, re.S)
assert m, 'footer contact column'
s = s[:m.start()] + m.group(1) + f'\n        <li><a href="https://share.google/WNvIKe4CJP8CnL8ns" {EXT}>★ Google reviews</a></li>\n      </ul>\n      ' + social_row() + s[m.end():]
s = s.replace('@media (max-width: 1080px)', SOCIAL_CSS + '\n@media (max-width: 1080px)', 1)

# more FAQs (facts from the live terms, custom tours and Dolomites pages)
FAQ = [
  ('What is included in the price?', 'Each tour page lists exactly what is included. As an example, the Dolomites tour includes hotel nights, buffet breakfasts, airport transfers with bike and luggage at set times, guided rides every day with our ex-pro guides, a support vehicle, snacks and water on the route, and GPX files sent in advance. Flights, dinners, bike rental and travel insurance are extra.'),
  ('How big are the groups?', 'We keep groups small so everyone gets proper support. The Dolomites tour, for example, takes a maximum of 12 riders. You will find the group size on each tour page.'),
  ('How do I book, and when is the balance due?', 'A deposit secures your place when you book. Deposits are non-refundable. The outstanding balance is due 31 days before the trip.'),
  ('What happens if I need to cancel?', 'Email us at tours@cigalacycling.com. If you cancel between booking and 31 days before departure, your full balance (not including the deposit) is carried forward as a credit for a future trip within two years. Cancellations fewer than 31 days before the trip cannot be refunded, which is why travel insurance is mandatory on all our tours.'),
  ('Can you organise a private or custom tour?', 'Yes. We are a boutique tour operator and specialise in bespoke tours for any group size, from a couple of riders to a whole club. We organise accommodation, guiding, support, bike rental, transfers and restaurants, and we can also put together a self-guided trip.'),
]
extra = ''.join(f'\n      <details id="faq-{i}"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(FAQ, 5))
rep('<details id="faq-4">', '<details id="faq-4">')
i = s.index('</details>', s.index('<details id="faq-4">')) + len('</details>')
s = s[:i] + extra + s[i:]

CSS2 = """
/* ---- Matteo's feedback, 15 Nov 2026 ---- */
.cc [hidden], [hidden] { display: none !important; }
.eyebrow { color: var(--red-text, #ff3d33); margin-bottom: 10px; }
.hero .eyebrow { display: inline-flex; align-items: center; gap: 8px; color: var(--text); text-shadow: none; background: rgba(8,9,10,.78); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 14px; margin-bottom: 16px; }
.hero .eyebrow::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--red); flex: none; }
.story .quote { margin-bottom: 18px; }
.brand img { border-radius: 0; }   /* Matteo's logo file has its own square white border */
.story img.signature { display: block; width: 150px; max-width: 45%; height: auto; margin: 22px 0 0 -4px; opacity: .92; }
.story img.signature + .sig { margin-top: 6px !important; font-size: 14px; }
.story img.signature + .sig span { display: block; font-size: 12.5px; margin-top: 2px; }
.burger details.sub { border-bottom: 1px solid var(--border); }
.burger details.sub > summary { border: 0; border-radius: 0; background: none; list-style: none; cursor: pointer; display: flex; justify-content: space-between; align-items: center; padding: 11px 0; font-weight: 600; text-transform: uppercase; font-size: 13px; letter-spacing: .05em; color: var(--text); }
.burger details.sub > summary::-webkit-details-marker { display: none; }
.burger details.sub > summary::after { content: ""; width: 8px; height: 8px; border-right: 2px solid var(--green-text); border-bottom: 2px solid var(--green-text); transform: rotate(45deg); margin: -4px 4px 0 0; transition: transform .2s; }
.burger details.sub[open] > summary::after { transform: rotate(-135deg); margin-top: 4px; }
.burger details.sub .sub-links { display: grid; padding: 0 0 8px 14px; border-left: 2px solid var(--border); margin: 0 0 6px 2px; }
.burger details.sub .sub-links a { border-bottom: 0; padding: 9px 0; font-size: 12.5px; color: var(--text-2); }
.burger details.sub .sub-links a[aria-current="page"] { padding-left: 12px; color: var(--text); }
.burger details.sub > summary:focus-visible { outline: 2px solid var(--green); outline-offset: 2px; }
.rv-links { display: flex; flex-wrap: wrap; gap: 8px 22px; }
.why .ico { width: 46px; height: 46px; border-radius: 12px; display: grid; place-items: center; background: var(--green-wash); border: 1px solid rgba(0,154,68,.35); }
.why .ico svg { width: 24px; height: 24px; fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.why h3 { margin-top: 16px; }
@media (min-width: 901px) {
  .hero::after { background: linear-gradient(90deg, rgba(8,9,10,.72) 0%, rgba(8,9,10,.45) 50%, rgba(8,9,10,.2) 100%), linear-gradient(180deg, rgba(8,9,10,.3) 0%, rgba(8,9,10,.2) 40%, rgba(8,9,10,.92) 100%); }
}
.hero h1, .hero .lede { text-shadow: 0 2px 18px rgba(0,0,0,.55); }
.finder { margin-bottom: 26px; }
#tour-grid .tour img { filter: brightness(.82); }
#tour-grid .tour::before { content: ""; position: absolute; inset: 0 0 auto; height: 38%; z-index: -1; background: linear-gradient(180deg, rgba(8,9,10,.6), rgba(8,9,10,0)); }
.stat .n i { font-size: .6em; margin-left: .14em; vertical-align: .38em; }
.story p { margin-bottom: 16px; }
.band .tx .eyebrow + h2, .band .tx h2 + .bar { margin-top: 0; }
.fi select:focus, .fi select:focus-visible { outline: none; }
.fi:focus-within { box-shadow: inset 0 0 0 2px var(--green); border-radius: 10px; }
.tour .facts span { white-space: nowrap; }
.tour .facts span:not(:last-child)::after { content: "·"; margin-left: 12px; color: var(--red); font-weight: 700; }
.matteo .photo { background: none; aspect-ratio: auto; position: relative; display: flex; justify-content: center; align-items: flex-end; isolation: isolate; }
.matteo .photo::before { content: ""; position: absolute; inset: 10% 5% 0; background: radial-gradient(circle at 50% 45%, rgba(0,154,68,.25), rgba(8,9,10,0) 65%); z-index: -1; }
.matteo .photo img { width: 100%; max-width: 480px; height: auto; -webkit-mask-image: linear-gradient(180deg, #000 82%, transparent 100%); mask-image: linear-gradient(180deg, #000 82%, transparent 100%); }
section.matteo .in .photo { aspect-ratio: auto !important; overflow: visible; border: 0; border-radius: 0; background: none; }
@media (max-width: 900px) {
  .finder { margin-bottom: 30px; }
  section.matteo .in .photo img { width: 100%; max-width: 340px; }
}
#tour-grid .tour { aspect-ratio: auto; min-height: 380px; }   /* grow with long text + badge; rows stay equal height */
#tour-grid .tour .tx { padding-top: 58px; padding-bottom: 18px; }
#tour-grid .tour p { margin: 6px 0 10px; }
@media (min-width: 1100px) { #tour-grid .tour .facts { margin-bottom: 8px; } }
"""
s = s.replace('@media (max-width: 1080px)', CSS2 + '\n@media (max-width: 1080px)', 1)

# same tour order in the phone menu and the footer
mob = '\n        '.join(f'<a href="{L}{u}" {EXT}>{t}</a>' for t, u in MENU_SUB)
s = re.sub(r'<a href="' + re.escape(L) + r'/trips/" ' + re.escape(EXT) + r'>All tours</a>(?:\s*<a href="[^"]+" ' + re.escape(EXT) + r'>(?:Gran Fondo|Italian|Gravel|Road|Custom) tours</a>)+', mob, s)  # desktop dropdown and phone menu
foot = '\n        '.join(f'<li><a href="{L}{u}" {EXT}>{t}</a></li>' for t, u in MENU_TOURS)
s, n = re.subn(r'<li><a href="' + re.escape(L) + r'/trips/" ' + re.escape(EXT) + r'>All tours</a></li>(?:\s*<li><a href="[^"]+" ' + re.escape(EXT) + r'>(?:Gran Fondo|Italian|Gravel|Road|Custom) tours</a></li>)+', foot, s, count=1)
assert n == 1

s = s.replace('<title>Cigala Tours Homepage</title>', '<title>Cigala Cycling Tours | Europe Bike Tour Operator</title>')
open(OUT + 'home.html', 'w').write(s)
print('wrote tourspages/home.html', len(s), 'bytes,', len(cards), 'tours')
