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
rows = {}
for a in re.findall(r'<article class="panel trip".*?</article>', idx, re.S):
    slug = re.search(r'href="' + re.escape(L) + r'/trips/([^/"]+)/?"', a).group(1)
    t = trips[slug]
    card = CARD.get(slug, slug)
    out = f'webp-tours/cigala-tours-card-{card}.webp'
    if not os.path.exists(ROOT + out):   # 2200px original -> 1100px WebP q90
        im = Image.open(ROOT + f'cards/hq/{card}.png').convert('RGB')
        im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS).save(ROOT + out, 'WEBP', quality=90)
    if not os.path.exists(ROOT + f'tourspages/img/cigala-tours-card-{card}.webp'):
        shutil.copy(ROOT + out, ROOT + f'tourspages/img/cigala-tours-card-{card}.webp')
    a = re.sub(r'src="cards/[^"]+\.jpg"', f'src="img/cigala-tours-card-{card}.webp"', a)
    if slug in LIVE_ALT:
        a = re.sub(r'(<img src="img/cigala-tours-card-[^"]+" alt=")[^"]*"', lambda m: m.group(1) + E(LIVE_ALT[slug]) + '"', a, count=1)
    a = a.replace('<div class="meta">', f'<div class="meta"><span class="chip date"><time datetime="{t["start"]}">{dates(t)}</time></span>', 1)
    if t.get('badge'):   # Gran Fondo badge (same as the homepage cards)
        a = re.sub(r'(<div class="tags">.*?</div>)', lambda m: m.group(1) + BADGES[t['badge']], a, count=1, flags=re.S)
    a = a.replace('<h2>Maratona dles Dolomites – Enel</h2>', '<h2>Maratona dles Dolomites - Enel</h2>')   # live H2 wording (hyphen)
    rows[slug] = (t['type'], a)

by_date = lambda ss: sorted(ss, key=lambda s: trips[s]['start'])
ROAD = by_date([s for s, (k, _) in rows.items() if k == 'road'])
GF = by_date([s for s, (k, _) in rows.items() if k == 'gf'])

# ---------- shared parts ----------
hero_custom = re.search(r'<p class="lede" style="margin-top:10px">Can’t find the perfect one\?.*?</p>', idx, re.S).group(0)
band = re.search(r'<section>\s*<div class="in">\s*<div class="band">.*?</section>', idx, re.S).group(0)
partners = re.search(r'<section>\s*<div class="in partners">.*?</section>', idx, re.S).group(0)
footnote = ('<p class="footnote">*Prices in GBP or USD could be slightly different at the time of booking based on the current exchange rate. '
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

def page_main(slug):
    crumb, eyebrow, h1, intro, tour_list, hero, pid = PAGES[slug]
    if slug == 'trips':
        crumbs = f'<a href="{L}/" {EXT}>Home</a> / Bike tours'
    else:
        crumbs = f'<a href="{L}/" {EXT}>Home</a> / <a href="{L}/trips/" {EXT}>Bike tours</a> / {crumb}'
    label = 'All public tours' if slug == 'trips' else crumb
    head = (f'<div class="head"><div><div class="eyebrow">{label}</div><h2>2027 Calendar</h2>'
            f'<div class="bar"></div></div>{browse(slug)}</div>')
    tours_html = '\n'.join(rows[s][1] for s in tour_list)
    parts = [f'<div class="hero phero">\n  <img src="{hero}" alt="{E(HERO_ALT.get(hero, ""))}">\n  <div class="in">\n'
             f'    <div class="crumbs">{crumbs}</div>\n    <div class="pill-eyebrow">{eyebrow}</div>\n'
             f'    <h1>{E(h1)}</h1>\n    <div class="bar"></div>\n'
             f'    <div class="lede">{"".join(f"<p>{E(p)}</p>" for p in intro)}</div>\n    {hero_custom}\n  </div>\n</div>']
    if slug == 'road-trips':
        gf_html = '\n'.join(rows[s][1] for s in GF)
        parts.append(f'<section id="calendar" style="padding-top:44px">\n  <div class="in">\n    {head}\n'
                     f'    <div class="trips">\n{tours_html}\n    </div>\n  </div>\n</section>')
        parts.append(f'<section style="padding-top:56px">\n  <div class="in">\n'
                     f'    <div class="head"><div><div class="eyebrow">Ride the event</div><h2>Road tours with a Gran Fondo</h2><div class="bar"></div>\n'
                     f'      <p class="lede">These tours are ridden on the road bike too, built around a Gran Fondo or a pro race weekend.</p></div>\n'
                     f'      <a class="arrow-link" href="{L}/trips/granfondo-trips/" {EXT}>All Gran Fondo tours →</a></div>\n'
                     f'    <div class="trips">\n{gf_html}\n    </div>\n    {footnote}\n  </div>\n</section>')
    else:
        parts.append(f'<section id="calendar" style="padding-top:44px">\n  <div class="in">\n    {head}\n'
                     f'    <div class="trips">\n{tours_html}\n    </div>\n    {footnote}\n  </div>\n</section>')
    parts += [band, partners]
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
'''
css = scope_css(design_css + EXTRA, 'html .cl')
css += '''
body:has(.cl-page) { background: #08090a !important; overflow-x: hidden; }
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
