"""Tours trip-list pages from the trip-list design in tourspages/index.html.

Pages: /trips/ (8689), /trips/road-trips/ (new, 9301), /trips/gravel-trips/ (2821),
/trips/granfondo-trips/ (2796), /italian-trips/ (4402).
Existing pages keep their live H1, intro text and tour order (tours/list-pages-live.json);
their Rank Math title and description are not touched. Only the new Road page gets SEO set here.

Writes previews tourspages/<slug>.html (header/footer from tourspages/home.html, CSS scoped like WordPress)
and stg-tours/out/list-<slug>.json for tools/push_tours_list.py.
Card images: the 2027 tour cards (cards/hq, 2200px originals) as WebP q90 in webp-tours/.
"""
import os, re, json, html, shutil
from datetime import date
from PIL import Image
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I skips the script folder
from css_scope import scope_css

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
L = 'https://tours.cigalacycling.com'
EXT = 'target="_blank" rel="noopener"'
E = lambda x: html.escape(x, quote=True)
idx = open(ROOT + 'tourspages/index.html').read()
home = open(ROOT + 'tourspages/home.html').read()
trips = {t['slug']: t for t in json.load(open(ROOT + 'tours/trips-2027.json'))['trips']}
LIVE = json.load(open(ROOT + 'tours/list-pages-live.json'))   # exact H1, intro and tour order of the live pages
FLAG = {'Italy': 'it', 'France': 'fr', 'Portugal': 'pt', 'Slovenia': 'si', 'Cyprus': 'cy', 'Belgium': 'be'}   # small country flag on each card, top right (Matteo 15 Nov)
MON = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def dates(t):
    a, b = date.fromisoformat(t['start']), date.fromisoformat(t['end'])
    return f'{a.day}–{b.day} {MON[a.month]} {b.year}' if a.month == b.month else f'{a.day} {MON[a.month]} – {b.day} {MON[b.month]} {b.year}'

# ---------- trip rows from the design ----------
CARD = {'lake-garda-and-stelvio': 'lake-garda-stelvio', 'lake-como-gran-fondo-il-lombardia': 'lake-como-il-lombardia'}
BADGES = json.load(open(ROOT + 'tours/badges.json'))
os.makedirs(ROOT + 'tourspages/img', exist_ok=True)
LIVE_ALT = {
 "discover-the-algarve-granfondo": "Algarve & Gran Fondo Tour",
 "chianti-gran-fondo-strade-bianche": "Chianti & Strade Bianche Tour",
 "tour-of-flanders-experience": "Tour of Flanders Experience Tour",
 "cyprus-crossing-gravel": "Cyprus Crossing Gravel Tour",
 "tuscany-epic-gravel": "Tuscany Gravel Epic",
 "maratona-dles-dolomites": "Maratona Dles Dolomites Bike Tour",
 "dolomites": "Dolomites Tour",
 "italian-alps": "Italian Alps Tour",
 "alpine-gravel-escape": "Alpine Gravel Tour Bormio Cigala",
 "french-alps": "French Alps Bike Tour",
 "wonderful-slovenia": "Wonderful Slovenia Bike Tour",
 "lake-garda-and-stelvio": "Lake Garda Bike Tour | Cigala Cycling",
 "lake-como-gran-fondo-il-lombardia": "Lake Como & Lombardia 2027"
}   # live card alts ('Cigla' typo on Lake Garda fixed)
_SPJ = json.load(open(ROOT + 'tours/spots.json'))
def avail(slug):   # the same availability as the trip pages (tours/spots.json); cards show only low and mid
    lv = _SPJ.get(slug, _SPJ.get('_default'))
    return {'low': '<span class="avl low">Last few spots</span>', 'mid': '<span class="avl mid">Filling up fast</span>'}.get(lv, '')
rows = {}
TAGS = {'road': ['Road'], 'gf': ['Road', 'Gran Fondo'], 'gravel': ['Gravel']}
for a in re.findall(r'<article class="panel trip".*?</article>', idx, re.S):
    slug = re.search(r'href="' + re.escape(L) + r'/trips/([^/"]+)/?"', a).group(1)
    t = trips[slug]
    g = lambda rx: re.search(rx, a, re.S).group(1)
    name = g(r'<h2>(.*?)</h2>').replace('Maratona dles Dolomites – Enel', 'Maratona dles Dolomites - Enel')   # live H2 wording
    name = name.replace(' | Gravel', '')   # Matteo 15 Nov: "Gravel" is already the tag on the photo
    where = g(r'<h3 class="where">(.*?)</h3>').rstrip('.').strip()   # no full stop after the country
    chips = re.findall(r'<span class="chip[^"]*">(.*?)</span>', g(r'<div class="meta">(.*?)</div>'))
    nights = [c for c in chips if 'night' in c.lower()][0]
    level = [c for c in chips if c.startswith('Level')][0].replace('Level: ', '')
    desc = g(r'<div class="desc">(.*?)</div>')
    price_label = g(r'<div class="price"><small>(.*?)</small>')
    price = g(r'<div class="price"><small>.*?</small>(.*?)</div>')
    early = re.search(r'<span class="early">(.*?)</span>', a)
    more = g(r'<a class="btn btn-ghost" href="([^"]+)"')
    book = g(r'<a class="btn btn-go" href="([^"]+)"')
    img = f'img/cigala-tours-trip-{slug}.webp'
    src = ROOT + f'webp-tours/cigala-tours-trip-{slug}.webp'
    if os.path.exists(src) and not os.path.exists(ROOT + 'tourspages/' + img):
        shutil.copy(src, ROOT + 'tourspages/' + img)
    tags = ''.join(f'<span class="tag{" gravel" if x == "Gravel" else ""}">{x}</span>' for x in TAGS[t['type']])
    badge = BADGES[t['badge']] if t.get('badge') else ''
    alt = LIVE_ALT.get(slug) or f'{t["name"]} bike tour'
    lv = [x.strip().lower() for x in level.split(',')]
    bars = {'beginner': 1, 'intermediate': 2, 'expert': 3}.get(lv[0], 2)   # how hard: set by the easiest level the tour suits
    meter = f'<span class="lm" aria-hidden="true">{"".join("<i class=on></i>" if i < bars else "<i></i>" for i in range(3))}</span>'
    rows[slug] = (t['type'], f"""<article class="tcard" data-k="{t['type']}" data-level="{' '.join(lv)}">
  <a class="ph" href="{more}" {EXT}><img src="{img}" alt="{E(alt)}" loading="lazy" width="1200" height="900"><span class="tags">{tags}</span><img class="flag" src="img/flag-{FLAG[t['country']]}.webp" alt="Flag of {t['country']}" width="40" height="30">{badge}</a>
  <div class="tx">
    <h2>{name}</h2>
    <h3 class="where">{where}</h3>
    <div class="meta"><span class="chip date"><time datetime="{t['start']}">{dates(t)}</time></span><span class="chip">{nights}</span><span class="chip lvl">{meter}Level: {level}</span>{f'<span class="chip avc">{avail(slug)}</span>' if avail(slug) else ''}</div>
    <div class="desc clamp">{desc}</div>
    <button type="button" class="more-txt" aria-expanded="false" hidden>Read more</button>
    <div class="bottom">
      <div class="price"><small>{price_label}</small>{price}</div>
      {f'<span class="early">{early.group(1)}</span>' if early else '<span class="early none" aria-hidden="true">&nbsp;</span>'}
      <div class="ctas"><a class="btn btn-ghost" href="{more}" {EXT}>More details</a><a class="btn btn-go" href="{book}" {EXT}>Book now →</a></div>
    </div>
  </div>
</article>""")
by_date = lambda ss: sorted(ss, key=lambda s: trips[s]['start'])
ROAD = by_date([s for s, (k, _) in rows.items() if k == 'road'])
GF = by_date([s for s, (k, _) in rows.items() if k == 'gf'])

# ---------- shared parts ----------
hero_custom = re.search(r'<p class="lede" style="margin-top:10px">Can’t find the perfect one\?.*?</p>', idx, re.S).group(0)
band = re.search(r'<section>\s*<div class="in">\s*<div class="band">.*?</section>', idx, re.S).group(0)
partners = re.search(r'<section>\s*<div class="in partners">.*?</section>', idx, re.S).group(0)
partners = partners.replace('<div class="lab">Official event partner</div>', '<div class="lab">Event day support</div>')   # Matteo, 15 Nov
partners = partners.replace('alt="Algarve Granfondo logo" loading="lazy"></span>', 'alt="Algarve Granfondo logo" loading="lazy"></span><span class="fill"><img src="img/logo-wrf.png" alt="We Ride Flanders logo" loading="lazy"></span>', 1)
footnote = ('<p class="footnote">*Prices in GBP or USD could be slightly different at the time of booking based on the current exchange rate. '
            'On our booking page you can choose your currency, see the live price in it and pay in the currency you prefer. '
            'By signing up to any of our Cycling Holidays (public or custom) you accept our Terms &amp; Conditions. '
            f'<a href="{L}/terms-conditions/" {EXT}>View T&amp;C</a></p>')

def live_intro(slug):
    """live intro text before the calendar, split on <br>, without the custom-tour line"""
    out = []
    for tag, v in LIVE[slug]['intro']:
        if v.startswith('Can’t find the perfect one'):
            continue
        out += [x.strip() for x in re.split(r'<br\s*/?>', v) if x.strip()]
    return out

ROAD_INTRO = [  # new copy for the new page (Matteo to check)
    "Road cycling is where Cigala Cycling Tours began. Our road bike tours take you over the climbs that made the Giro d’Italia and the Tour de France famous: the Stelvio, Gavia and Mortirolo in the Italian Alps, the Giau and Sella Ronda passes in the Dolomites, the Galibier and Alpe d’Huez in the French Alps, and the Vršič Pass in Slovenia.",
    "Every trip is guided by former pro riders who handle the routes, logistics and bike support, so all you need to do is ride. From relaxed lakeside days on Lake Garda to big mountain weeks, there is a road tour for every level.",
]
# slug: (crumb, eyebrow, H1, intro paragraphs, tours, hero image (preview path), page id)
PAGES = {
    'trips': ('Bike tours', '2027 season · road &amp; gravel', LIVE['trips']['h1'], live_intro('trips'), LIVE['trips']['trips'], 'img/home-hero.jpg', 8689),
    'road-trips': ('Road tours', '2027 season · road', 'Road Bike Tours', ROAD_INTRO, ROAD, 'img/cigala-tours-hero-road.webp', 9301),
    'gravel-trips': ('Gravel tours', '2027 season · gravel', LIVE['gravel-trips']['h1'], live_intro('gravel-trips'), LIVE['gravel-trips']['trips'], 'img/cigala-tours-hero-gravel.webp', 2821),
    'granfondo-trips': ('Gran Fondo tours', '2027 season · gran fondo', LIVE['granfondo-trips']['h1'], live_intro('granfondo-trips'), LIVE['granfondo-trips']['trips'], 'img/cigala-tours-hero-granfondo.webp', 2796),
    'italian-trips': ('Italian tours', '2027 season · italy', LIVE['italian-trips']['h1'], live_intro('italian-trips'), LIVE['italian-trips']['trips'], 'img/cigala-tours-hero-italian.webp', 4402),
}
URL = {'trips': '/trips/', 'road-trips': '/trips/road-trips/', 'gravel-trips': '/trips/gravel-trips/',
       'granfondo-trips': '/trips/granfondo-trips/', 'italian-trips': '/italian-trips/'}
HERO_ALT = {'img/home-hero.jpg': 'Cigala Cycling Tours riders celebrating on the coast in Cyprus'}

def browse(cur):
    """links between the tour pages: easy switching, and internal links for Google"""
    items = [('All', 'trips'), ('Road', 'road-trips'), ('Gravel', 'gravel-trips'), ('Gran Fondo', 'granfondo-trips'), ('Italy', 'italian-trips')]
    return '<nav class="browse" aria-label="Tour types">' + ''.join(
        f'<a class="chip" href="{L}{URL[s]}" {EXT}' + (' aria-current="page"' if s == cur else '') + f'>{t}</a>'
        for t, s in items) + '</nav>'

LEVELS = ('<div class="fchips lvchips" role="group" aria-label="Filter by level">'
          '<button type="button" class="fchip on" data-lv="" aria-pressed="true">All levels</button>'
          + ''.join(f'<button type="button" class="fchip" data-lv="{k}" aria-pressed="false"><span class="lm" aria-hidden="true">{"".join("<i class=on></i>" if i < n else "<i></i>" for i in range(3))}</span>{k.title()}</button>'
                    for n, k in ((1, 'beginner'), (2, 'intermediate'), (3, 'expert'))) + '</div>')
LEVEL_JS = """<script>(function(){var g=document.querySelector('.cl .lvchips');if(!g)return;g.querySelectorAll('.fchip').forEach(function(b){b.addEventListener('click',function(){
g.querySelectorAll('.fchip').forEach(function(x){x.classList.toggle('on',x===b);x.setAttribute('aria-pressed',x===b);});var v=b.dataset.lv;
document.querySelectorAll('.cl .tgrid').forEach(function(grid){var n=0;[].forEach.call(grid.querySelectorAll('.tcard'),function(c){var ok=!v||c.dataset.level.split(' ').indexOf(v)>-1;c.hidden=!ok;if(ok)n++;});
var m=grid.nextElementSibling&&grid.nextElementSibling.classList.contains('lvnone')?grid.nextElementSibling:null;if(m)m.hidden=n>0;});});});})();</script>"""
NONE = f'<p class="lvnone" hidden>No tour here for this level yet. <a href="{L}/trips/private-trips/" {EXT}>Ask us for a custom tour</a> and we will plan one for you.</p>'

READMORE = """<script>(function(){document.querySelectorAll('.cl .tcard .desc.clamp').forEach(function(d){var b=d.parentNode.querySelector('.more-txt');if(d.scrollHeight>d.clientHeight+4){b.hidden=false;b.addEventListener('click',function(){var o=d.classList.toggle('clamp');b.textContent=o?'Read more':'Show less';b.setAttribute('aria-expanded',!o);});}});})();</script>"""

def page_main(slug):
    crumb, eyebrow, h1, intro, tour_list, hero, pid = PAGES[slug]
    if slug == 'trips':
        crumbs = f'<a href="{L}/" {EXT}>Home</a> / Bike tours'
    else:
        crumbs = f'<a href="{L}/" {EXT}>Home</a> / <a href="{L}/trips/" {EXT}>Bike tours</a> / {crumb}'
    label = 'All public tours' if slug == 'trips' else crumb
    head = (f'<div class="head"><div><div class="eyebrow">{label}</div><h2>2027 Calendar</h2>'
            f'<div class="bar"></div></div>{browse(slug)}</div>{LEVELS}')
    tours_html = '\n'.join(rows[s][1] for s in tour_list)
    parts = [f'<div class="hero phero">\n  <img src="{hero}" alt="{E(HERO_ALT.get(hero, ""))}">\n  <div class="in">\n'
             f'    <div class="crumbs">{crumbs}</div>\n    <div class="pill-eyebrow">{eyebrow}</div>\n'
             f'    <h1>{E(h1)}</h1>\n    <div class="bar"></div>\n'
             f'    <div class="lede">{"".join(f"<p>{E(p)}</p>" for p in intro)}</div>\n    {hero_custom}\n  </div>\n</div>']
    if slug == 'road-trips':
        gf_html = '\n'.join(rows[s][1] for s in GF)
        parts.append(f'<section id="calendar" style="padding-top:44px">\n  <div class="in">\n    {head}\n'
                     f'    <div class="tgrid">\n{tours_html}\n    </div>{NONE}\n  </div>\n</section>')
        parts.append(f'<section style="padding-top:56px">\n  <div class="in">\n'
                     f'    <div class="head"><div><div class="eyebrow">Ride the event</div><h2>Road tours with a Gran Fondo</h2><div class="bar"></div>\n'
                     f'      <p class="lede">These tours are ridden on the road bike too, built around a Gran Fondo or a pro race weekend.</p></div>\n'
                     f'      <a class="arrow-link" href="{L}/trips/granfondo-trips/" {EXT}>All Gran Fondo tours →</a></div>\n'
                     f'    <div class="tgrid">\n{gf_html}\n    </div>{NONE}\n    {footnote}\n  </div>\n</section>')
    else:
        parts.append(f'<section id="calendar" style="padding-top:44px">\n  <div class="in">\n    {head}\n'
                     f'    <div class="tgrid">\n{tours_html}\n    </div>{NONE}\n    {footnote}\n  </div>\n</section>')
    parts += [band, partners, READMORE, LEVEL_JS]
    return '\n'.join(parts)

# ---------- CSS: design CSS scoped to .cl, plus the brand fixes used on the homepage ----------
design_css = re.search(r'<style>\n(.*?)</style>', idx, re.S).group(1)
EXTRA = BADGES['css'] + '''
.trip .entry { margin: 2px 0 0; width: fit-content; }
[hidden] { display: none !important; }
.eyebrow { color: #ff3d33; margin-bottom: 10px; }
button, .btn { text-transform: none; letter-spacing: .02em; }
.trip .meta .chip.date { background: var(--red); border-color: var(--red); color: #fff; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
.trip h3.where { margin-top: 2px; }
.head .lede { margin-top: 14px; }
.browse { display: flex; flex-wrap: wrap; gap: 8px; }
.browse .chip { text-decoration: none; }
.browse .chip[aria-current="page"] { background: var(--green); border-color: var(--green); color: #fff; }
:root { background: transparent; }
/* tour cards: 3 per row on laptops, 2 on tablets, 1 on phones */
.tgrid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.tcard { display: flex; flex-direction: column; min-width: 0; background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: var(--r); overflow: hidden; }
.tcard:hover { border-color: rgba(0,154,68,.5); }
.tcard .ph { position: relative; display: block; aspect-ratio: 4 / 3; overflow: hidden; }
.tcard .ph img { width: 100%; height: 100%; object-fit: cover; filter: brightness(.95); transition: transform .5s ease; }
.tcard:hover .ph img { transform: scale(1.04); }
.tcard .ph .tags { position: absolute; top: 12px; left: 12px; display: flex; gap: 6px; margin: 0; }
.tcard .tag { display: inline-flex; align-items: center; white-space: nowrap; line-height: 1.2; font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--text); background: rgba(8,9,10,.78); border: 1px solid var(--border-strong); border-radius: 999px; padding: 4px 10px; }
.tcard .tag::before { content: ""; flex: none; display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--red); margin-right: 7px; vertical-align: 1px; }
.tcard .tag.gravel::before { background: var(--gravel); }
.tcard .tx { flex: 1; display: flex; flex-direction: column; gap: 14px; padding: 20px 22px 22px; min-width: 0; }
.tcard .entry { width: fit-content; margin: 0; }
.tcard .ph .flag { position: absolute; top: 26px; right: 26px; width: auto !important; height: 23px !important; aspect-ratio: 1 / 1; object-fit: cover; object-position: center; border-radius: 50%; filter: none !important; box-shadow: 0 0 0 1px rgba(255,255,255,.35), 0 2px 8px rgba(0,0,0,.4); }
.tcard:hover .ph .flag { transform: none; }
.tcard .ph .entry { position: absolute; left: 26px; bottom: 26px; background: rgba(8,9,10,.85); border-radius: 999px; padding: 4px 10px; }   /* badge on the photo, lined up with the type tag above it */
.tcard h2 { font-size: clamp(24px, 2.2vw, 30px); }
.tcard h3.where { font-size: 14px; font-weight: 600; color: var(--text-2); margin-top: -6px; }
.tcard .meta { display: flex; flex-wrap: wrap; gap: 6px; }
.tcard .meta .chip { display: inline-flex; align-items: center; line-height: 1.2; font-size: 11px; padding: 6px 10px 5px; cursor: default; }   /* text centred in the chip (Matteo 16 Nov) */
.tcard .meta .chip.date { background: var(--red); border-color: var(--red); color: #fff; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; font-size: 13px; padding: 5px 11px; }
.tcard .meta { margin: 2px 0; }
.phero .lede a { color: var(--green-text); font-weight: 600; text-decoration: none; }
.phero .lede a:hover { color: #fff; }
.tcard .desc p { margin: 0 0 8px; font-size: 14px; color: var(--text-2); line-height: 1.55; }
.tcard .desc.clamp { display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
.tcard .more-txt { align-self: flex-start; font: 600 13px var(--body); color: var(--green-text); background: none; border: 0; padding: 0; cursor: pointer; margin-top: -4px; }
.tcard .bottom { margin-top: auto; padding-top: 16px; border-top: 1px solid var(--border); display: grid; gap: 10px; }
.tcard .price { font-family: var(--head); font-size: 26px; line-height: 1.1; color: var(--text); }
.tcard .price small { display: block; padding: 0; margin: 0 0 8px !important; font-family: var(--body); font-size: 11.5px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); margin-bottom: 4px; }
.tcard .early { justify-self: start; display: inline-flex; align-items: center; gap: 8px; font-size: 12.5px; font-weight: 600; color: var(--text); background: rgba(225,6,0,.12); border: 1px solid rgba(225,6,0,.45); border-radius: 6px; padding: 5px 10px; }
.tcard .early.none { visibility: hidden; }   /* keeps prices level across a row */
.tcard .early::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--red); }
.tcard .early::before { animation: early-pulse 1.8s ease-in-out infinite; }   /* the red dot gently glows: the early-bird price ends soon */
@keyframes early-pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(225,6,0,.7); opacity: 1; } 50% { box-shadow: 0 0 0 5px rgba(225,6,0,0); opacity: .55; } }
@media (prefers-reduced-motion: reduce) { .tcard .early::before { animation: none; } }
.tcard .ctas { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 6px 0 0; }
.tcard .ctas .btn { padding: 11px 10px; text-align: center; justify-content: center; }
.avl { display: inline-flex; align-items: center; gap: 7px; font-size: 12px; font-weight: 700; letter-spacing: .02em; color: #fff; white-space: nowrap; }   /* availability on the cards: only low (red) and mid (amber), Matteo 16 Nov */
.avl::before { content: ""; flex: none; width: 7px; height: 7px; border-radius: 50%; background: rgb(var(--av)); animation: avl-pulse 1.8s ease-in-out infinite; }
.avl.low { --av: 225,6,0; } .avl.mid { --av: 240,191,0; }
@keyframes avl-pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(var(--av), .7); opacity: 1; } 50% { box-shadow: 0 0 0 5px rgba(var(--av), 0); opacity: .55; } }
@media (prefers-reduced-motion: reduce) { .avl::before { animation: none; } }
.tcard .meta .chip.avc { border-color: rgba(var(--avb), .5); background: rgba(var(--avb), .1); } .tcard .meta .chip.avc:has(.low) { --avb: 225,6,0; } .tcard .meta .chip.avc:has(.mid) { --avb: 240,191,0; }
.tcard .meta .chip.avc .avl { font-size: 11px; }
.lm { display: inline-flex; align-items: flex-end; gap: 2px; margin-right: 7px; vertical-align: -1px; }   /* level meter: 3 bars (Matteo 16 Nov: text + meter, not icons only) */
.lm i { display: block; width: 3px; border-radius: 1px; background: rgba(255,255,255,.22); }
.lm i:nth-child(1) { height: 5px; } .lm i:nth-child(2) { height: 8px; } .lm i:nth-child(3) { height: 11px; }
.lm i.on { background: var(--green-text, #2bd47a); }
.fchip.on .lm i.on { background: #fff; } .fchip.on .lm i { background: rgba(255,255,255,.35); }
.lvchips { margin: 18px 0 22px; }
.lvnone { color: var(--text-2); font-size: 15px; margin: 8px 0 0; } .lvnone a { color: var(--green-text); }
@media (max-width: 1100px) { .tgrid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) { .tgrid { grid-template-columns: minmax(0, 1fr); } }
'''
css = scope_css(design_css + EXTRA, 'html .cl')
css += '''
body:has(.cl-page) { overflow-x: hidden; }   /* topo background: set in build_tours_wp.py, same as the homepage */
body:has(.cl-page) .site-header, body:has(.cl-page) .site-footer { display: none; }
html .cl h1, html .cl h2, html .cl h3, html .cl h4 { font-family: var(--head); font-weight: 400; text-transform: uppercase; color: var(--text); letter-spacing: .01em; line-height: 1.04; }
html .cl p, html .cl li, html .cl a, html .cl span, html .cl div, html .cl button { font-family: var(--body); }
html .cl h1, html .cl h2, html .cl h3, html .cl .price { font-family: var(--head); }
html .cl h3.where { font-family: var(--body); text-transform: none; }
'''

# ---------- previews + WordPress payloads ----------
hs, he = home.index('</header>') + len('</header>'), home.index('<footer>')
home_css = re.search(r'<style>\n/\* Cigala Cycling kit.*?</style>', home, re.S).group(0)
head0 = home[:hs].replace(home_css, '<style>\n' + scope_css(home_css[len('<style>'):-len('</style>')], 'html .cc') + '</style>')
head0 = head0.replace('<header class="nav">', '<div class="cc"><header class="nav">').replace('</header>', '</header></div>')
head0 = re.sub(r'<div class="ribbon">.*?</div></div>', '', head0, flags=re.S)
foot0 = home[he:].replace('<footer>', '<div class="cc"><footer>', 1).replace('</footer>', '</footer></div>', 1)
for key in ('hero-road', 'hero-gravel', 'hero-granfondo', 'hero-italian'):
    src = ROOT + f'webp-tours/cigala-tours-{key}.webp'
    if os.path.exists(src):
        shutil.copy(src, ROOT + f'tourspages/img/cigala-tours-{key}.webp')
os.makedirs(ROOT + 'stg-tours/out', exist_ok=True)
for slug in PAGES:
    main = page_main(slug)
    prev = head0 + '\n<div class="cl cl-page">\n' + main + '\n</div>\n' + foot0
    prev = re.sub(r'<script>\s*\(function \(\) \{\s*var f = document\.getElementById.*?</script>', '', prev, flags=re.S)  # no finder here
    prev = prev.replace('</style>', '</style>\n<style>\n' + css + '\n</style>', 1)
    open(ROOT + f'tourspages/{slug}.html', 'w').write(prev)
    d = {'slug': slug, 'id': PAGES[slug][6], 'main': main, 'css': css}
    if slug == 'road-trips':   # the new page: title, parent and Rank Math SEO set by us
        d.update({'parent': 8689, 'title': 'Road Bike Tours',
                  'seo_title': 'Guided Road Bike Tours Europe | Cigala Cycling Tours',
                  'seo_description': 'Explore guided road bike tours across Europe with Cigala Cycling Tours. Ride the Dolomites, the Italian and French Alps, Slovenia and Lake Garda with former pros.'})
    json.dump(d, open(ROOT + f'stg-tours/out/list-{slug}.json', 'w'), ensure_ascii=False)
    print(slug, len(re.findall(r'<article', main)), 'tours | preview tourspages/' + slug + '.html')
