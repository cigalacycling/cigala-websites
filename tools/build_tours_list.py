"""Tours trip-list pages (category pages) from the trip-list design in tourspages/index.html.

First page: /trips/road-trips/ (new, approved by Matteo on 15 Nov 2026).
Writes the preview tourspages/road-trips.html (header/footer from tourspages/home.html)
and, for WordPress, stg-tours/out/list-road-trips.json  {css, content, ...}.
Card images: the 2027 tour cards (cards/hq, 2200px originals) as WebP q90 in webp-tours/.
"""
import os, re, json, html
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
MON = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def dates(t):
    a, b = date.fromisoformat(t['start']), date.fromisoformat(t['end'])
    return f'{a.day}–{b.day} {MON[a.month]} {b.year}' if a.month == b.month else f'{a.day} {MON[a.month]} – {b.day} {MON[b.month]} {b.year}'

# ---------- trip rows from the design ----------
CARD = {'lake-garda-and-stelvio': 'lake-garda-stelvio', 'lake-como-gran-fondo-il-lombardia': 'lake-como-il-lombardia'}
BADGES = json.load(open(ROOT + 'tours/badges.json'))
rows = {}
for a in re.findall(r'<article class="panel trip".*?</article>', idx, re.S):
    slug = re.search(r'href="' + re.escape(L) + r'/trips/([^/"]+)/?"', a).group(1)
    t = trips[slug]
    card = CARD.get(slug, slug)
    out = f'webp-tours/cigala-tours-card-{card}.webp'
    if not os.path.exists(ROOT + out):   # 2200px original -> 1100px WebP q90
        im = Image.open(ROOT + f'cards/hq/{card}.png').convert('RGB')
        im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS).save(ROOT + out, 'WEBP', quality=90)
    os.makedirs(ROOT + 'tourspages/img', exist_ok=True)
    if not os.path.exists(ROOT + f'tourspages/img/cigala-tours-card-{card}.webp'):
        import shutil; shutil.copy(ROOT + out, ROOT + f'tourspages/img/cigala-tours-card-{card}.webp')
    a = re.sub(r'src="cards/[^"]+\.jpg"', f'src="img/cigala-tours-card-{card}.webp"', a)
    # dates as real text, first in the facts row
    a = a.replace('<div class="meta">', f'<div class="meta"><span class="chip date"><time datetime="{t["start"]}">{dates(t)}</time></span>', 1)
    if t.get('badge'):   # Gran Fondo badge (same as the homepage cards)
        a = re.sub(r'(<div class="tags">.*?</div>)', lambda m: m.group(1) + BADGES[t['badge']], a, count=1, flags=re.S)
    rows[slug] = (t['type'], a)

ROAD = [s for s, (k, _) in rows.items() if k == 'road']
GF = [s for s, (k, _) in rows.items() if k == 'gf']
by_date = lambda ss: sorted(ss, key=lambda s: trips[s]['start'])

# ---------- page ----------
hero_custom = re.search(r'<p class="lede" style="margin-top:10px">Can’t find the perfect one\?.*?</p>', idx, re.S).group(0)
band = re.search(r'<section>\s*<div class="in">\s*<div class="band">.*?</section>', idx, re.S).group(0)
partners = re.search(r'<section>\s*<div class="in partners">.*?</section>', idx, re.S).group(0)
footnote = ('<p class="footnote">*Prices in GBP or USD could be slightly different at the time of booking based on the current exchange rate. '
            'By signing up to any of our Cycling Holidays (public or custom) you accept our Terms &amp; Conditions. '
            f'<a href="{L}/terms-conditions/" {EXT}>View T&amp;C</a></p>')

INTRO = [  # new copy for the new page (Matteo to check)
    "Road cycling is where Cigala Cycling Tours began. Our road bike tours take you over the climbs that made the Giro d’Italia and the Tour de France famous: the Stelvio, Gavia and Mortirolo in the Italian Alps, the Giau and Sella Ronda passes in the Dolomites, the Galibier and Alpe d’Huez in the French Alps, and the Vršič Pass in Slovenia.",
    "Every trip is guided by former pro riders who handle the routes, logistics and bike support, so all you need to do is ride. From relaxed lakeside days on Lake Garda to big mountain weeks, there is a road tour for every level.",
]
main = f'''<div class="hero phero">
  <img src="img/cigala-tours-hero-road.webp" alt="Cigala Cycling Tours Lake Garda">
  <div class="in">
    <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / <a href="{L}/trips/" {EXT}>Bike tours</a> / Road tours</div>
    <div class="pill-eyebrow">2027 season · road</div>
    <h1>Road Bike Tours</h1>
    <div class="bar"></div>
    <div class="lede">{''.join(f'<p>{E(p)}</p>' for p in INTRO)}</div>
    {hero_custom}
  </div>
</div>
<section id="calendar" style="padding-top:44px">
  <div class="in">
    <div class="head"><div><div class="eyebrow">Road tours</div><h2>2027 Calendar</h2><div class="bar"></div></div></div>
    <div class="trips">
{chr(10).join(rows[s][1] for s in by_date(ROAD))}
    </div>
  </div>
</section>
<section style="padding-top:56px">
  <div class="in">
    <div class="head"><div><div class="eyebrow">Ride the event</div><h2>Road tours with a Gran Fondo</h2><div class="bar"></div>
      <p class="lede">These tours are ridden on the road bike too, built around a Gran Fondo or a pro race weekend.</p></div>
      <a class="arrow-link" href="{L}/trips/granfondo-trips/" {EXT}>All Gran Fondo tours →</a></div>
    <div class="trips">
{chr(10).join(rows[s][1] for s in by_date(GF))}
    </div>
    {footnote}
  </div>
</section>
{band}
{partners}'''

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
'''
css = scope_css(design_css + EXTRA, 'html .cl')
css += '''
body:has(.cl-page) { background: #08090a !important; overflow-x: hidden; }
body:has(.cl-page) .site-header, body:has(.cl-page) .site-footer { display: none; }
html .cl h1, html .cl h2, html .cl h3, html .cl h4 { font-family: var(--head); font-weight: 400; text-transform: uppercase; color: var(--text); letter-spacing: .01em; line-height: 1.04; }
html .cl h3.where { font-family: var(--body); text-transform: none; }
html .cl p, html .cl li, html .cl a, html .cl span, html .cl div, html .cl button { font-family: var(--body); }
html .cl h1, html .cl h2, html .cl h3, html .cl .price { font-family: var(--head); }
html .cl h3.where { font-family: var(--body); }
'''

# ---------- preview (homepage header/footer + scoped CSS, like WordPress) ----------
hs, he = home.index('</header>') + len('</header>'), home.index('<footer>')
# scope the homepage CSS to .cc (header/footer) exactly as on WordPress, so the two designs don't mix
home_css = re.search(r'<style>\n/\* Cigala Cycling kit.*?</style>', home, re.S).group(0)
head = home[:hs].replace(home_css, '<style>\n' + scope_css(home_css[len('<style>'):-len('</style>')], 'html .cc') + '</style>')
head = head.replace('<header class="nav">', '<div class="cc"><header class="nav">').replace('</header>', '</header></div>')
foot = home[he:].replace('<footer>', '<div class="cc"><footer>', 1).replace('</footer>', '</footer></div>', 1)
head = re.sub(r'<div class="ribbon">.*?</div></div>', '', head, flags=re.S)
prev = head + '\n<div class="cl cl-page">\n' + main + '\n</div>\n' + foot
prev = re.sub(r'<script>\s*\(function \(\) \{\s*var f = document\.getElementById.*?</script>', '', prev, flags=re.S)  # no finder here
prev = prev.replace('</style>', '</style>\n<style>\n' + css + '\n</style>', 1)
prev = prev.replace('<title>Cigala Cycling Tours | Europe Bike Tour Operator</title>', '<title>Guided Road Bike Tours Europe | Cigala Cycling Tours</title>')
prev = prev.replace('href="' + L + '/trips/road-trips/" ' + EXT + '>Road tours', 'href="' + L + '/trips/road-trips/" ' + EXT + ' aria-current="page">Road tours')
open(ROOT + 'tourspages/road-trips.html', 'w').write(prev)

os.makedirs(ROOT + 'stg-tours/out', exist_ok=True)
json.dump({'slug': 'road-trips', 'parent': 8689, 'title': 'Road Bike Tours',
           'seo_title': 'Guided Road Bike Tours Europe | Cigala Cycling Tours',
           'seo_description': 'Explore guided road bike tours across Europe with Cigala Cycling Tours. Ride the Dolomites, the Italian and French Alps, Slovenia and Lake Garda with former pros.',
           'css': css, 'main': main, 'cards': sorted(set(CARD.get(s, s) for s in ROAD + GF))},
          open(ROOT + 'stg-tours/out/list-road-trips.json', 'w'), ensure_ascii=False)
print('road', len(ROAD), 'gf', len(GF), '| css', len(css), '| preview tourspages/road-trips.html')
