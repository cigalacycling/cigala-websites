"""Build the Tours homepage preview: tourspages/home.html

Source design: survey/NfmCmGsjq4LL9bTAi38NXN/index.html
Changes on top of the design (approved by Matteo, 15 Nov 2026):
  - H1 keeps the live wording
  - tour finder (Month / Tour type / Country / Level) in the hero
  - all 15 tours from tours/trips-2027.json, with dates as real text
  - Bike Tours menu keeps the live split and adds Road Tours
Images are copied into tourspages/img/ (home-*) so the preview opens locally.
"""
import os, re, json, html, shutil, urllib.request, ssl
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

# reviewer photos are not in the repo yet: show initials instead
def av(m):
    name = m.group(2)
    return f'<div class="who"><span class="av" aria-hidden="true">{E(name[:1])}</span><div>{name}'
s = re.sub(r'<div class="who"><img src="img/t_[^"]+"[^>]*>(<div>)([^<]+)', av, s)

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
MENU_TOURS = [
    ('All tours', '/trips/'),
    ('Gran Fondo tours', '/trips/granfondo-trips/'),
    ('Italian tours', '/italian-trips/'),
    ('Gravel tours', '/trips/gravel-trips/'),
    ('Road tours', '/trips/road-trips/'),
    ('Custom tours', '/trips/private-trips/'),
]
dd = ''.join(f'<a href="{L}{u}" {EXT}>{t}</a>' for t, u in MENU_TOURS)
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
        f'<div class="tx"><time class="when" datetime="{t["start"]}">{dates(t)}</time>'
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
      <label class="fi"><span>Tour type</span><select name="type" id="q-type">{opts("Any type", [("road", "Road"), ("gf", "Gran Fondo"), ("gravel", "Gravel")])}</select></label>
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

s = s.replace('<title>Cigala Tours Homepage</title>', '<title>Cigala Cycling Tours | Europe Bike Tour Operator</title>')
open(OUT + 'home.html', 'w').write(s)
print('wrote tourspages/home.html', len(s), 'bytes,', len(cards), 'tours')
