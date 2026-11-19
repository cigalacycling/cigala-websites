# Builds the Pyrenees 2027 private group proposal (Cigala Cycling Tours brand) as proposal.html.
# Shares the Nutritional Guide stylesheet (A4 pages, Anton + Montserrat, topo background).
# Run: python3 -I tours/proposals/pyrenees-2027/make.py && node tours/proposals/pyrenees-2027/build.js [previewDir]
import os
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, '..', '..', '..', 'coaching', 'nutrition-guide')
guide = open(os.path.join(G, 'guide.html')).read()
A = '../../../coaching/nutrition-guide/assets/'
style = guide[guide.index('<style>') + 7:guide.index('</style>')].replace('url(assets/', 'url(' + A)

# ---- prices: Mallorca 2026 group table minus 2%, rounded to the nearest €5
MALLORCA = [(7, 2480), (8, 2340), (9, 2250), (10, 2170), (11, 2110), (12, 2040), (13, 1980), (14, 1920)]
PRICES = [(n, int(5 * round(p * 0.98 / 5))) for n, p in MALLORCA]
SINGLE = 420
DEPOSIT = 499

DAYS = [
 ('Sat 19 June', 'Arrival in Luchon & shake-out ride', '30 km', '400 m', 'Alti Hotel, Luchon',
  'Welcome to the Pyrenees! Transfer from the airport to Bagnères-de-Luchon, the “Queen of the Pyrenees”. Bike set-up and fitting with our mechanics, then an easy shake-out ride along the valley to loosen the legs after the journey. Welcome briefing and first evening together.', 'meadow'),
 ('Sun 20 June', 'Superbagnères & Col du Portillon', '75 km', '2,100 m', 'Alti Hotel, Luchon',
  'Straight from the hotel we climb to Superbagnères, a former Tour de France summit finish with huge views over the Luchon valley. In the afternoon we cross the Col du Portillon into Spain and return through the Val d’Aran.', 'two'),
 ('Mon 21 June', 'Col de Peyresourde & Col d’Azet to Saint-Lary', '65 km', '1,900 m', 'Mercure, Saint-Lary-Soulan',
  'Our first point-to-point stage. We leave Luchon on the Col de Peyresourde, a Tour de France classic, then ride through the Val Louron and over the Col d’Azet before descending into Saint-Lary-Soulan. Luggage travels with the support vehicle.', 'valley'),
 ('Tue 22 June', 'Col du Portet', '55 km', '1,700 m', 'Mercure, Saint-Lary-Soulan',
  'A day for the queen climb of this side of the range: the Col du Portet (2,215 m), one of the highest roads in the Pyrenees and a modern Tour de France summit finish. Long, steady and spectacular above the Néouvielle massif. Afternoon to rest and recover.', 'hairpins'),
 ('Wed 23 June', 'Col d’Aspin & Col du Tourmalet to Lourdes', '115 km', '2,600 m', 'Hotel Gallia, Lourdes',
  'The big day. We climb the Col d’Aspin, then the legendary Col du Tourmalet (2,115 m), the most climbed pass in Tour de France history. A long descent through Luz-Saint-Sauveur and the Gave de Pau valley brings us to Lourdes.', 'tourmalet'),
 ('Thu 24 June', 'Col du Soulor & Col d’Aubisque', '105 km', '2,200 m', 'Hotel Gallia, Lourdes',
  'From Lourdes we ride up the Val d’Azun to the Col du Soulor and on along the famous balcony road to the Col d’Aubisque, with its giant bikes at the summit. Return the same way for one of the most scenic descents of the week.', 'goats'),
 ('Fri 25 June', 'Hautacam (or Luz Ardiden)', '60 km', '1,600 m', 'Hotel Gallia, Lourdes',
  'The grand finale on the slopes of Hautacam, scene of many Tour de France battles. Riders who want more can choose Luz Ardiden instead; an easier valley option is always available. Celebration dinner in the evening.', 'group'),
 ('Sat 26 June', 'Departure day', '', '', '',
  'After breakfast, transfer to the airport. See you next time!', None),
]
km = sum(int(d[2].split()[0]) for d in DAYS if d[2])
up = sum(int(d[3].split()[0].replace(',', '')) for d in DAYS if d[3])

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
 'Bike rental from €280, depending on bike specs',
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
COLS = {'Superbagnères': (0.570, 42.752), 'Col du Portillon': (0.680, 42.805), 'Col de Peyresourde': (0.445, 42.797),
        'Col d’Azet': (0.380, 42.812), 'Col du Portet': (0.230, 42.800), 'Col d’Aspin': (0.328, 42.943),
        'Col du Tourmalet': (0.145, 42.908), 'Col du Soulor': (-0.262, 42.959), 'Col d’Aubisque': (-0.339, 42.977),
        'Hautacam': (0.000, 43.000)}
def xy(p):
    x0, x1, y0, y1 = -0.45, 0.78, 42.72, 43.14
    return 30 + (p[0] - x0) / (x1 - x0) * 640, 20 + (y1 - p[1]) / (y1 - y0) * 300
route = ['Luchon', 'Col de Peyresourde', 'Col d’Azet', 'Saint-Lary', 'Col d’Aspin', 'Col du Tourmalet', 'Lourdes']
allp = {**PTS, **COLS}
path = ' '.join(('M' if i == 0 else 'L') + '%.1f %.1f' % xy(allp[k]) for i, k in enumerate(route))
svg = f'<svg viewBox="0 0 700 340" role="img" aria-label="Schematic route map: Luchon to Saint-Lary-Soulan to Lourdes, with the main climbs">'
svg += '<rect x="0" y="0" width="700" height="340" fill="none"/>'
svg += f'<path d="{path}" fill="none" stroke="#009a44" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="1 0"/>'
lab = {'Superbagnères': (8, 14), 'Col du Portillon': (-4, -12), 'Col de Peyresourde': (-30, 26), 'Col d’Azet': (8, -8), 'Col du Portet': (-40, 24),
       'Col d’Aspin': (8, -8), 'Col du Tourmalet': (-30, -12), 'Col du Soulor': (8, 16), 'Col d’Aubisque': (-40, -12), 'Hautacam': (10, 4)}
for k, p in COLS.items():
    x, y = xy(p); dx, dy = lab[k]
    svg += f'<path d="M{x:.1f} {y-7:.1f} L{x+6:.1f} {y+4:.1f} L{x-6:.1f} {y+4:.1f} Z" fill="#f0bf00"/>'
    svg += f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-family="Montserrat" font-size="11" font-weight="600" fill="#d0d6e0">{k}</text>'
for i, (k, p) in enumerate([('Luchon', PTS['Luchon']), ('Saint-Lary', PTS['Saint-Lary']), ('Lourdes', PTS['Lourdes'])], 1):
    x, y = xy(p)
    svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="#E10600" stroke="#fff" stroke-width="2"/><text x="{x:.1f}" y="{y+4.5:.1f}" text-anchor="middle" font-family="Anton" font-size="14" fill="#fff">{i}</text>'
    off = {'Luchon': (18, 5), 'Saint-Lary': (-60, -20), 'Lourdes': (18, -8)}[k]
    svg += f'<text x="{x+off[0]:.1f}" y="{y+off[1]:.1f}" font-family="Anton" font-size="17" fill="#f7f8f8" letter-spacing=".5">{k.upper()}</text>'
svg += '<text x="690" y="332" text-anchor="end" font-family="Montserrat" font-size="9.5" fill="#8a8f98">Schematic map · day loops from each base not drawn</text></svg>'

pages = []
pages.append(f'''<section class="page tours-cover">
  <div class="bg"><img src="{I}hero.jpg" alt="Aerial view of a hairpin road climbing through the Pyrenees"></div>
  <div class="in">
    <img class="logo" src="{I}logo.png" alt="Cigala Cycling Tours logo">
    <h1>Pyrenees<br>2027</h1>
    <div class="bar" style="width:56px;height:4px;margin-top:18px"></div>
    <p class="tag">Ride the legendary cols of the Tour de France. A private group tour from Luchon to Lourdes.</p>
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
  <p class="lead">The Pyrenees are home to some of the most famous climbs in cycling: the Tourmalet, the Aubisque, the Peyresourde and the Col du Portet. We have designed a week that moves across the heart of the range, staying at three bases so every day brings new roads, quieter valleys and authentic mountain villages.</p>
  <p>We start in Luchon, the “Queen of the Pyrenees”, cross to Saint-Lary-Soulan for the Col du Portet, and finish in Lourdes after riding the Tourmalet, the Aubisque and Hautacam. Every day is fully supported by our guides and support vehicle, with easier options always available.</p>
  <div class="glance">
    <div><b>~{km} km</b><span>Total distance</span></div>
    <div><b>~{up:,} m</b><span>Total climbing</span></div>
    <div><b>10</b><span>Iconic climbs</span></div>
    <div><b>6</b><span>Days riding</span></div>
  </div>
  <div class="map">{svg}</div>
  <h3>Three bases</h3><div class="bar"></div>
  <div class="bases">
    <div class="base"><div class="n">Nights 1–2 · 19–20 June</div><div class="anton">Alti Hotel</div><p>Bagnères-de-Luchon</p></div>
    <div class="base"><div class="n">Nights 3–4 · 21–22 June</div><div class="anton">Mercure Saint-Lary</div><p>Saint-Lary-Soulan</p></div>
    <div class="base"><div class="n">Nights 5–7 · 23–25 June</div><div class="anton">Hotel Gallia</div><p>Lourdes</p></div>
  </div>
''' + FOOT(2) + '</section>')

def day_html(i, d):
    date, title, dist, gain, hotel, txt, img = d
    st = f'<div class="st"><span>{dist}</span><span>+{gain}</span></div>' if dist else ''
    h = f'<div class="h">Hotel: <b>{hotel}</b></div>' if hotel else ''
    ph = f'<div class="ph"><img src="{I}{img}.jpg" alt="{title}"></div>' if img else ''
    cls = 'day' if img else 'day np'
    return f'<div class="{cls}"><div class="dn"><small>DAY</small><b>{i}</b><em>{date}</em></div><div><div class="anton">{title}</div>{st}<p>{txt}</p>{h}</div>{ph}</div>\n'

pages.append('<section class="page">\n' + RUN + sec('Itinerary', 'Day by day', 'Routes, distances and climbing are indicative and will be finalised with the group. GPX files are sent before the trip.')
             + ''.join(day_html(i + 1, d) for i, d in enumerate(DAYS[:4])) + FOOT(3) + '</section>')
pages.append('<section class="page">\n' + RUN + ''.join(day_html(i + 5, d) for i, d in enumerate(DAYS[4:])) + f'''  <div class="panel exc" style="margin-top:6px"><div class="anton" style="font-size:19px;margin-bottom:8px">Not included</div><ul class="dots c2">{''.join(f"<li>{x}</li>" for x in NOT_INCLUDED)}</ul></div>
''' + FOOT(4) + '</section>')

rows = ''.join(f'<tr{" class=hl" if n == 8 else ""}><td>{n} cyclists</td><td><b>€{p:,}</b></td></tr>' for n, p in PRICES)
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
    <div class="rev"><div class="s">★★★★★</div><p>“Had a wonderful tour with Cigala in the French Alps in June 2025. I just showed up ready to pedal and they took care of the rest: excellent rental bikes, phenomenal routes with stunning views, gracious accommodations and delicious food with local charm.”</p><div class="w">Hank · USA · French Alps</div></div>
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
print('prices', PRICES, 'km', km, 'up', up)
