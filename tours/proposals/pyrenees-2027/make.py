# Builds the Pyrenees 2027 private group proposal (Cigala Cycling Tours brand) as proposal.html.
# Shares the Nutritional Guide stylesheet (A4 pages, Anton + Montserrat, topo background).
# Run: python3 -I tours/proposals/pyrenees-2027/make.py && node tours/proposals/pyrenees-2027/build.js [previewDir]
import os
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, '..', '..', '..', 'coaching', 'nutrition-guide')
guide = open(os.path.join(G, 'guide.html')).read()
A = '../../../coaching/nutrition-guide/assets/'
style = guide[guide.index('<style>') + 7:guide.index('</style>')].replace('url(assets/', 'url(' + A)

# ---- prices (Matteo, 19 Nov 2026): Mallorca table minus ~2%, rounded up to the next €50
PRICES = [(7, 2450), (8, 2300), (9, 2250), (10, 2150), (11, 2100), (12, 2000), (13, 1950), (14, 1900)]
SINGLE = 420
DEPOSIT = 499
GROUP = 'Nat Maple Group'

H1 = 'Alti Hotel *** · Bagnères-de-Luchon'
H2 = 'Mercure Saint-Lary **** · Saint-Lary-Soulan'
H3 = 'Hotel Gallia **** · Lourdes'
# (date, title, climbs, hotel, text, photo). No distances/elevation until Matteo confirms the routes.
DAYS = [
 ('Sat 19 June', 'Arrival in Luchon', '', H1,
  'Welcome to the Pyrenees! Transfer from the airport to Bagnères-de-Luchon, the “Queen of the Pyrenees”. Bike set-up and fitting with our mechanics, welcome briefing and first evening together. No riding today: the legs stay fresh for the week ahead.', 'meadow'),
 ('Sun 20 June', 'Col de Portet d’Aspet & Col de Menté', 'Col de Portet d’Aspet · Col de Menté', H1,
  'Our first ride: a loop from Luchon over two climbs full of Tour de France history, the steep Col de Portet d’Aspet and the Col de Menté, through quiet forests and remote mountain villages.', 'two'),
 ('Mon 21 June', 'Peyresourde & Azet to Saint-Lary, then Cap de Long', 'Col de Peyresourde · Col d’Azet · Lac de Cap de Long', H2,
  'Our first point-to-point stage, from base to base by bike. We leave Luchon on the Col de Peyresourde, a Tour de France classic, and ride over the Col d’Azet into Saint-Lary-Soulan. From there we climb to the Lac de Cap de Long, high in the Néouvielle massif. Luggage travels with the support vehicle.', 'valley'),
 ('Tue 22 June', 'Col d’Aspin & Col du Portet', 'Col d’Aspin · Col du Portet', H2,
  'From Saint-Lary we ride the Col d’Aspin and turn at Payolle back towards the valley. Then the queen climb of this side of the range: the Col du Portet (2,215 m), one of the highest roads in the Pyrenees and a modern Tour de France summit finish.', 'hairpins'),
 ('Wed 23 June', 'Hourquette d’Ancizan & Tourmalet to Lourdes', 'Hourquette d’Ancizan · Col du Tourmalet', H3,
  'The big point-to-point day. We leave Saint-Lary over the Hourquette d’Ancizan, a quiet high road with wide views, drop to Payolle and climb the legendary Col du Tourmalet (2,115 m), the most climbed pass in Tour de France history. A long descent brings us to Lourdes.', 'tourmalet'),
 ('Thu 24 June', 'Col d’Aubisque loop', 'Col d’Aubisque', H3,
  'A loop from Lourdes up the Val d’Azun and along the famous balcony road to the Col d’Aubisque, with its giant bikes at the summit and some of the most scenic roads of the week.', 'goats'),
 ('Fri 25 June', 'Hautacam', 'Hautacam', H3,
  'The grand finale on the slopes of Hautacam, scene of many Tour de France battles, just outside Lourdes. Easier options are always available. Celebration dinner in the evening.', 'group'),
 ('Sat 26 June', 'Departure day', '', '',
  'After breakfast, transfer to the airport. See you next time!', None),
]
CLIMBS = ['Col de Portet d’Aspet', 'Col de Menté', 'Col de Peyresourde', 'Col d’Azet', 'Col d’Aspin', 'Hourquette d’Ancizan', 'Col du Portet', 'Lac de Cap de Long', 'Col du Tourmalet', 'Col d’Aubisque', 'Hautacam']

INCLUDED = ['7 nights in hand-picked hotels at three bases: Luchon, Saint-Lary-Soulan and Lourdes',
 '6 days of guided cycling',
 'Daily buffet breakfast',
 'Airport transfers, including bike and luggage, at set times',
 'Guided routes every day with our ex-pro, experienced and friendly guides',
 'Daily PRO experience with support vehicle and mechanic',
 'Snacks & water on route',
 'Luggage transfers from hotel to hotel',
 'GPX files sent in advance',
 'Pro tips from our ex-pro staff',
 '1 cycling kit washing service during the week']
NOT_INCLUDED = ['Flights',
 'Dinners – organised with great restaurants along the route',
 f'Single room supplement €{SINGLE}',
 'Bike rental from €300, depending on bike specs',
 'Travel insurance']

style += '''
.tours-cover{padding:0}
.tours-cover .bg{position:absolute;inset:0}
.tours-cover .bg img{width:100%;height:100%;object-fit:cover;object-position:50% 40%}
.tours-cover .bg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,9,10,.55) 0%,rgba(8,9,10,.25) 35%,rgba(8,9,10,.85) 72%,#08090a 100%)}
.tours-cover .in{position:absolute;inset:0;padding:16mm 16mm}
.tours-cover .logo{width:28mm;height:28mm}
.tours-cover h1{font-size:118px;line-height:.9;margin-top:92mm}
.tours-cover .tag{font-size:18px;color:var(--text);max-width:150mm;margin-top:14px;line-height:1.4}
.tours-cover .meta{position:absolute;left:16mm;right:16mm;bottom:16mm;display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.tours-cover .meta div{background:rgba(15,16,17,.85);border:1px solid var(--border-strong);border-radius:12px;padding:12px 14px}
.tours-cover .meta b{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:22px;color:var(--text);text-transform:uppercase;line-height:1.1}
.tours-cover .meta span{font-size:9.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--text-3)}
.glance{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin:14px 0}
.glance div{background:var(--panel);border:1px solid var(--border);border-top:3px solid var(--green);border-radius:12px;padding:12px;text-align:center}
.glance b{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:26px;color:var(--text);line-height:1.1}
.glance span{font-size:9px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--text-3)}
.map{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:10px 12px}
.map svg{width:100%;height:auto;display:block}
.bases{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.base{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:14px 16px;border-top:3px solid var(--red)}
.base .n{font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--red-text)}
.base .anton{font-size:20px;margin:6px 0 2px}
.base p{margin:0;font-size:11.5px}
.base p.cl{margin-top:8px;font-size:10.5px;color:var(--text-3);line-height:1.45}
.st3{color:#f0bf00;font-family:Montserrat,sans-serif;font-size:.6em;letter-spacing:1px;vertical-align:.15em}
.day .h .st3{font-size:1em;vertical-align:0}
.day{display:grid;grid-template-columns:66px 1fr 44mm;gap:14px;background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:12px 14px;margin-bottom:9px;align-items:start}
.day.np{grid-template-columns:66px 1fr}
.day .dn{text-align:center;border-right:1px solid var(--border-strong);padding-right:10px}
.day .dn small{display:block;font-size:9px;font-weight:700;letter-spacing:.16em;color:var(--text-3)}
.day .dn b{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:38px;color:var(--green-text);line-height:1}
.day .dn em{display:block;font-style:normal;font-size:9.5px;color:var(--text-3);margin-top:4px;line-height:1.3}
.day .anton{font-size:18px;line-height:1.1}
.day .st{display:flex;gap:8px;margin:6px 0 6px;flex-wrap:wrap}
.day .st span{font-size:10.5px;font-weight:600;color:var(--text);border:1px solid var(--border-strong);border-radius:999px;padding:2px 10px}
.day p{margin:0;font-size:11.2px;line-height:1.5}
.day .h{font-size:10.5px;color:var(--text-3);margin-top:6px}
.day .h b{color:var(--text-2);font-weight:600}
.day .ph{height:34mm;border-radius:8px;overflow:hidden}
.day .ph img{width:100%;height:100%;object-fit:cover}
.prices{width:100%}
.prices td,.prices th{text-align:center;font-size:12.5px;padding:6px 10px}
.prices th:first-child,.prices td:first-child{text-align:left}
.prices td b{font-family:Anton,sans-serif;font-weight:400;font-size:20px;color:var(--text)}
.prices tr.hl td{background:rgba(0,154,68,.12)}
.inc li::before{background:var(--green)}
.exc li::before{background:var(--text-3)}
.gal{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.gal img{width:100%;height:42mm;object-fit:cover;border-radius:10px;display:block}
.rev{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:14px 16px}
.rev .s{color:#f0bf00;letter-spacing:2px;font-size:13px}
.rev p{margin:6px 0 6px;font-size:11.5px;font-style:italic}
.rev .w{font-size:10.5px;color:var(--text-3)}
.next{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.step{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:14px 16px}
.step b.k{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:30px;color:var(--green-text);line-height:1}
'''

I = 'img/'
FOOT = lambda n: f'  <div class="foot"><span>Cigala Cycling Tours · Pyrenees 2027 · Private group proposal</span><span class="n">{n}</span></div>\n'
RUN = '  <div class="run"><span>Pyrenees 2027 · 19–26 June</span><span>Cigala Cycling Tours</span></div>\n'

def sec(eb, title, sub=''):
    return f'  <div class="sec"><div class="eyebrow">{eb}</div><h2>{title}</h2><div class="bar"></div>{f"<p class=sub>{sub}</p>" if sub else ""}</div>\n'

# schematic route map (approximate positions, lon/lat projected)
PTS = {'Lourdes': (-0.046, 43.095), 'Luchon': (0.593, 42.790), 'Saint-Lary': (0.322, 42.817)}
COLS = {'Col de Portet d’Aspet': (0.836, 42.936), 'Col de Menté': (0.752, 42.941), 'Col de Peyresourde': (0.445, 42.797),
        'Col d’Azet': (0.380, 42.812), 'Col d’Aspin': (0.328, 42.943), 'Hourquette d’Ancizan': (0.287, 42.884),
        'Col du Portet': (0.230, 42.800), 'Lac de Cap de Long': (0.143, 42.807), 'Col du Tourmalet': (0.145, 42.908),
        'Col d’Aubisque': (-0.339, 42.977), 'Hautacam': (0.000, 43.000)}
def xy(p):
    x0, x1, y0, y1 = -0.45, 0.92, 42.74, 43.14
    return 30 + (p[0] - x0) / (x1 - x0) * 640, 25 + (y1 - p[1]) / (y1 - y0) * 290
allp = {**PTS, **COLS}
P = lambda ks: ' '.join(('M' if i == 0 else 'L') + '%.1f %.1f' % xy(allp[k]) for i, k in enumerate(ks))
svg = '<svg viewBox="0 0 700 340" role="img" aria-label="Schematic map: Luchon to Saint-Lary-Soulan to Lourdes by bike, with the climbs of the week">'
svg += f'<path d="{P(['Luchon', 'Col de Peyresourde', 'Col d’Azet', 'Saint-Lary', 'Hourquette d’Ancizan', 'Col du Tourmalet', 'Lourdes'])}" fill="none" stroke="#009a44" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>'
lab = {'Col de Portet d’Aspet': (-60, 22), 'Col de Menté': (-40, -12), 'Col de Peyresourde': (-30, 28), 'Col d’Azet': (4, -10),
       'Col d’Aspin': (8, -6), 'Hourquette d’Ancizan': (-142, 4), 'Col du Portet': (-34, 24), 'Lac de Cap de Long': (-125, 6),
       'Col du Tourmalet': (-112, 4), 'Col d’Aubisque': (-30, -12), 'Hautacam': (-64, 4)}
for k, p in COLS.items():
    x, y = xy(p); dx, dy = lab[k]
    svg += f'<path d="M{x:.1f} {y-7:.1f} L{x+6:.1f} {y+4:.1f} L{x-6:.1f} {y+4:.1f} Z" fill="#f0bf00"/>'
    svg += f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-family="Montserrat" font-size="11" font-weight="600" fill="#d0d6e0">{k}</text>'
for i, k in enumerate(['Luchon', 'Saint-Lary', 'Lourdes'], 1):
    x, y = xy(PTS[k])
    svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="#E10600" stroke="#fff" stroke-width="2"/><text x="{x:.1f}" y="{y+4.5:.1f}" text-anchor="middle" font-family="Anton" font-size="14" fill="#fff">{i}</text>'
    off = {'Luchon': (18, 18), 'Saint-Lary': (-34, -22), 'Lourdes': (18, -8)}[k]
    svg += f'<text x="{x+off[0]:.1f}" y="{y+off[1]:.1f}" font-family="Anton" font-size="17" fill="#f7f8f8" letter-spacing=".5">{k.upper()}</text>'
svg += '<text x="690" y="332" text-anchor="end" font-family="Montserrat" font-size="9.5" fill="#8a8f98">Schematic map · green: by bike from base to base · day loops not drawn</text></svg>'

pages = []
pages.append(f'''<section class="page tours-cover">
  <div class="bg"><img src="{I}hero.jpg" alt="Aerial view of a hairpin road climbing through the Pyrenees"></div>
  <div class="in">
    <img class="logo" src="{I}logo.png" alt="Cigala Cycling Tours logo">
    <h1>Pyrenees<br>2027</h1>
    <div class="bar" style="width:56px;height:4px;margin-top:18px"></div>
    <p class="tag">A cycling journey through the legendary climbs of the French Pyrenees, from Luchon to Lourdes.</p>
    <div class="eyebrow" style="margin-top:16px;color:var(--text)">Private tour proposal for the {GROUP}</div>
  </div>
  <div class="meta">
    <div><span>Dates</span><b>19–26 June</b></div>
    <div><span>Nights</span><b>7 nights</b></div>
    <div><span>Riding</span><b>6 days</b></div>
    <div><span>Bases</span><b>3 hotels</b></div>
  </div>
</section>''')

pages.append(f'''<section class="page">
{RUN}{sec('Private group tour proposal', 'The Pyrenees, cols of legend')}
  <p class="lead">This itinerary focuses entirely on the French Pyrenees, combining some of the most iconic Tour de France climbs with spectacular mountain roads and three different accommodation bases.</p>
  <p>The route is designed to explore different areas of the Pyrenees while incorporating point-to-point riding days, allowing us to travel between locations by bike rather than relying on vehicle transfers. Every riding day is fully supported by our guides and support vehicle, with easier options always available.</p>
  <div class="glance">
    <div><b>{len(CLIMBS)}</b><span>Iconic climbs</span></div>
    <div><b>6</b><span>Days riding</span></div>
    <div><b>7</b><span>Nights</span></div>
    <div><b>3</b><span>Bases</span></div>
  </div>
  <div class="map">{svg}</div>
  <h3>Three bases</h3><div class="bar"></div>
  <div class="bases">
    <div class="base"><div class="n">2 nights · 19–20 June</div><div class="anton">Alti Hotel <span class="st3">★★★</span></div><p>Bagnères-de-Luchon</p><p class="cl">Col de Menté · Col de Portet d’Aspet · Col de Peyresourde · Col d’Azet</p></div>
    <div class="base"><div class="n">2 nights · 21–22 June</div><div class="anton">Mercure Saint-Lary <span class="st3">★★★★</span></div><p>Saint-Lary-Soulan</p><p class="cl">Lac de Cap de Long · Col d’Aspin · Col du Portet</p></div>
    <div class="base"><div class="n">3 nights · 23–25 June</div><div class="anton">Hotel Gallia <span class="st3">★★★★</span></div><p>Lourdes</p><p class="cl">Hourquette d’Ancizan · Col du Tourmalet · Col d’Aubisque · Hautacam</p></div>
  </div>
''' + FOOT(2) + '</section>')

def day_html(i, d):
    date, title, climbs, hotel, txt, img = d
    st = ''.join(f'<span>▲ {c}</span>' for c in climbs.split(' · ')) if climbs else ''
    st = f'<div class="st">{st}</div>' if st else ''
    h = f'<div class="h">Hotel: <b>{hotel.replace("***", "<span class=st3>★★★</span>").replace("<span class=st3>★★★</span>*", "<span class=st3>★★★★</span>")}</b></div>' if hotel else ''
    ph = f'<div class="ph"><img src="{I}{img}.jpg" alt="{title}"></div>' if img else ''
    cls = 'day' if img else 'day np'
    return f'<div class="{cls}"><div class="dn"><small>DAY</small><b>{i}</b><em>{date}</em></div><div><div class="anton">{title}</div>{st}<p>{txt}</p>{h}</div>{ph}</div>\n'

pages.append('<section class="page">\n' + RUN + sec('Itinerary', 'Day by day', 'Routes are finalised with the group. Full GPX files, distances and elevation are sent before the trip.')
             + ''.join(day_html(i + 1, d) for i, d in enumerate(DAYS[:4])) + FOOT(3) + '</section>')
pages.append('<section class="page">\n' + RUN + ''.join(day_html(i + 5, d) for i, d in enumerate(DAYS[4:])) + f'''  <div class="panel exc" style="margin-top:6px"><div class="anton" style="font-size:19px;margin-bottom:8px">Not included</div><ul class="dots c2">{''.join(f"<li>{x}</li>" for x in NOT_INCLUDED)}</ul></div>
''' + FOOT(4) + '</section>')

rows = ''.join(f'<tr><td>{n} cyclists</td><td><b>€{p:,}</b></td></tr>' for n, p in PRICES)
pages.append(f'''<section class="page">
{RUN}{sec('Price', 'Price per person', 'The price per person depends on the final size of the group. All prices in euro, sharing a twin or double room.')}
  <div class="g2" style="align-items:start">
    <div class="tbl"><table class="prices"><tr><th>Group size</th><th>Price per person</th></tr>{rows}</table></div>
    <div>
      <div class="tile wide" style="border-top:3px solid var(--green)"><div class="v" style="color:var(--text)">€{SINGLE}</div><div class="u">per person</div><div class="l">Single room supplement</div></div>
      <div class="tile wide" style="border-top:3px solid var(--green);margin-top:10px"><div class="v" style="color:var(--text)">€{DEPOSIT}</div><div class="u">per person, to confirm a place</div><div class="l">Deposit</div></div>
      <p class="note" style="margin-top:10px">Balance due before the trip. Payment by bank transfer or card.</p>
    </div>
  </div>
  <div class="panel inc" style="margin-top:14px"><div class="anton" style="font-size:19px;margin-bottom:8px">What’s included</div><ul class="dots c2">{''.join(f"<li>{x}</li>" for x in INCLUDED)}</ul></div>
''' + FOOT(5) + '</section>')

pages.append(f'''<section class="page">
{RUN}{sec('Real riders, real roads', 'The Pyrenees with Cigala')}
  <div class="gal">
    <img src="{I}aerial.jpg" alt="Hairpin road on a Pyrenean climb seen from the air">
    <img src="{I}hairpins.jpg" alt="Winding road climbing a green Pyrenean slope">
    <img src="{I}tourmalet.jpg" alt="Cyclist climbing the Col du Tourmalet">
    <img src="{I}two.jpg" alt="Two cyclists riding up a winding mountain road">
    <img src="{I}goats.jpg" alt="A herd of goats on a mountain road with cyclists">
    <img src="{I}valley.jpg" alt="Cyclist climbing high above a Pyrenean valley">
  </div>
  <div class="g2" style="margin-top:14px">
    <div class="rev"><div class="s">★★★★★</div><p>“Very well organised from the very first contact. Marine or Matteo rode with us each day and captured the best moments with hundreds of photos. A special thanks to Alessio, the driver of the support vehicle and bike mechanic.”</p><div class="w">Andreas · Mexico · Italian mountains</div></div>
    <div class="rev"><div class="s">★★★★★</div><p>“I have gone on a number of trips organised by Cigala Cycling Tours and they have been fantastic. Matteo pays attention to every last detail, from logistics, food and accommodation to the spectacular routes.”</p><div class="w">Mike · Ireland · repeat guest</div></div>
  </div>
  <h3>Next steps</h3><div class="bar"></div>
  <div class="next">
    <div class="step"><b class="k">1</b><div class="anton" style="font-size:17px;margin:6px 0 4px">Confirm the group</div><p style="margin:0;font-size:11.5px">Let us know your numbers and any changes to the itinerary. We hold the hotels for the group.</p></div>
    <div class="step"><b class="k">2</b><div class="anton" style="font-size:17px;margin:6px 0 4px">Pay the deposit</div><p style="margin:0;font-size:11.5px">€{DEPOSIT} per person confirms each place. We then send the booking form and waiver.</p></div>
  </div>
  <div class="made" style="display:flex;justify-content:space-between;align-items:center;margin-top:14px;padding:16px 20px;border:1px solid var(--border-strong);border-radius:12px;background:var(--panel)">
    <div><div class="eyebrow" style="margin-bottom:4px">Questions?</div><div class="anton" style="font-size:20px">Cigala Cycling Tours</div>
      <div style="font-size:11.5px;color:var(--text);margin-top:4px">tours@cigalacycling.com · +353 40478107 · tours.cigalacycling.com</div></div>
    <img src="{I}logo.png" alt="Cigala Cycling Tours logo" style="width:20mm;height:20mm">
  </div>
''' + FOOT(6) + '</section>')

html = f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><title>Pyrenees 2027 | Cigala Cycling Tours</title>
<link rel="stylesheet" href="{A}fonts.css"><style>{style}</style></head>
<body>
{chr(10).join(pages)}
</body></html>
'''
open(os.path.join(HERE, 'proposal.html'), 'w').write(html)
print('prices', PRICES, 'climbs', len(CLIMBS))
