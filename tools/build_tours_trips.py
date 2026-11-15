"""Tours trip pages (15, /trips/<slug>/) in the trip design (trip/pub/index.html, Dolomites).

Source of the words = each trip page's ORIGINAL Elementor data (stg-tours/backup/page-<id>.json), read in
order and sorted into the design's sections. Headings keep their live level (H2 stays H2, H3 stays H3) and
wording; body text, links and prices are copied as they are. Repeated link-only headings ("BOOK NOW") become
buttons; the "20+ / 500+ / 5★ / 10" stats become numbers (not headings).
Booking: the live WeTravel links, opened in a new tab as live.

Usage: python3 -I tools/build_tours_trips.py [slug ...]   (no slug = all 15)
Writes tourspages/page-trip-<slug>.html and stg-tours/out/list-trip-<slug>.json; push with
python3 -I tools/push_tours_list.py trip-<slug>.
"""
import os, re, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_tours_pages import fix_text, items, text_of, clean, img_tag, reviews_block, PARTNERS_H2, PAGE_CSS, L, EXT, E, YT_JS
from tours_img import media, webp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
IDS = json.load(open(ROOT + 'stg-tours/trip-ids.json'))
TRIPS = {t['slug']: t for t in json.load(open(ROOT + 'tours/trips-2027.json'))['trips']}
M = json.load(open(ROOT + 'stg-tours/media-webp.json'))
TYPE = {'road': 'Road', 'gf': 'Gran Fondo', 'gravel': 'Gravel'}
import importlib.util as _iu
_sp = _iu.spec_from_file_location('trm', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tours_route_maps.py')); _trm = _iu.module_from_spec(_sp); _sp.loader.exec_module(_trm)
ROUTE_NOTES = {k: v.get('note', '') for k, v in _trm.ROUTES.items()}
SPOTS = {k: v for k, v in json.load(open(ROOT + 'tours/spots.json')).items() if not k.startswith('_')}
MON = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def raw(pid): return json.loads(json.load(open(ROOT + f'stg-tours/backup/page-{pid}.json'))['meta']['_elementor_data'] or '[]')

def faqs(data):
    """Nested accordion -> [(question, answer html)] (titles in settings, answers in the child containers)."""
    out = []
    def walk(xs):
        for e in xs:
            if e.get('widgetType') == 'nested-accordion':
                titles = [i.get('item_title', '') for i in e['settings'].get('items', [])]
                for t, child in zip(titles, e.get('elements', [])):
                    ans = ''.join(clean(v) for k, v, s in items([child]) if k == 'text')
                    out.append((t.strip(), ans))
            walk(e.get('elements', []))
    walk(data)
    return out

def classify(k, t):
    u = t.upper().replace('’', "'").strip()
    if re.match(r'^BO+K NOW', u): return 'book'
    if k == 'h3' and u.startswith('BUILD YOUR TOUR WITH US'): return 'custom-sub'
    rules = [("WHAT'S NOT INCLUDED", 'notinc'), ("WHAT'S INCLUDED", 'inc'), ('AIRPORT TRANSFER', 'transfers'), ('AT GLANCE', 'glance'),
             ('DAY TO DAY', 'd2d'), ('GALLERY', 'gallery'), ('ACCOMODATION', 'hotels'), ('ACCOMMODATION', 'hotels'), ('WHERE YOU WILL STAY', 'hotels'),
             ('BIKE RENTAL', 'bike'), ('READ OUR TESTIMONIALS', 'reviews'), ('CUSTOMISE YOUR TOUR', 'custom'), ('YOUR TOUR GUIDES', 'guides'),
             ('FREQUENTLY ASKED', 'faq'), ('PLAN YOUR TRIP', 'related'), ('OFFICIAL TOUR OPERATOR', 'operator'), ('FANCY A FEW DAYS', 'extra'), ('OPTIONAL DAY-TRIP', 'extra')]
    for w, kind in rules:
        if w in u: return kind
    if re.match(r'^ROUTE( MAP)?$', u): return 'route'
    if re.match(r'^[\d,.]+\s*[+★]?$', u): return 'stat'
    return None

def lines(h):
    """A text block -> list items: <li>s if it is a list, else its lines (paragraphs / <br>)."""
    lis = re.findall(r'<li[^>]*>(.*?)</li>', h, re.S)
    if lis: return [x.strip() for x in lis if text_of(x)]
    parts = re.split(r'<br\s*/?>|</p>\s*<p[^>]*>|\n', re.sub(r'^<p[^>]*>|</p>$', '', h.strip()))
    return [p.strip() for p in parts if text_of(p)]

def km_m(title):
    """'SELLA RONDA WITH A TWIST 80km | 2400mt' -> ('SELLA RONDA WITH A TWIST', '80 km', '2,400 m')"""
    m = re.search(r'\s*(\d[\d.,]*)\s*km\s*[|/]?\s*(\d[\d.,]*)?\s*(mt|m)?\b.*$', title, re.I)
    if not m: return title.strip(), None, None
    fmt = lambda n: f'{int(n.replace(",", "").replace(".", "")):,} m' if n else None
    return title[:m.start()].strip(), f'{m.group(1)} km', fmt(m.group(2))

def nice(t):   # headings typed in capitals live: the design shows them in capitals with CSS, words unchanged
    return t


POSTS = {p['id']: p for p in json.load(open(ROOT + 'stg-tours/backup/posts.json'))}
def related_html(sec, h1):
    """'Plan Your Trip' + 'Cycling Guides & Tips' (both H2 live) + intro + three chosen guides (live loop grid by post id)."""
    ids = next((s.get('post_query_posts_ids') for k, v, s in sec['items'] if k == 'loop-grid'), []) or []
    h2b = next((v for k, v, s in sec['items'] if k == 'h2'), '')
    lede = ''.join(f'<p>{text_of(v)}</p>' for k, v, s in sec['items'] if k == 'text')
    cards = []
    for i in ids:
        p = POSTS.get(int(i))
        if not p: continue
        t = html.unescape(p['title']['raw']); u = p['link'].replace('https://staging.tours.cigalacycling.com', L)
        ex = html.unescape(re.sub(r'<[^>]+>', '', p['excerpt']['raw'] or '')).strip()
        ph = f'<a class="ph" href="{u}">{img_tag(p["featured_media"], 900, alt=t)}</a>' if p.get('featured_media') else ''
        cards.append(f'<article class="tcard dtour">{ph}<div class="tx"><div class="by">By Tours Director Matteo Cigala</div><h3>{E(t)}</h3>'
                     f'<div class="desc"><p>{E(ex)}</p></div><div class="bottom"><div class="ctas one"><a class="btn btn-go" href="{u}">Read the guide →</a></div></div></div></article>')
    if not cards: return ''
    return (f'<section id="guides-tips"><div class="in"><div class="head"><div><h2 class="eyebrow ey2">{E(text_of(sec["h"]))}</h2>'
            f'<h2>{E(text_of(h2b))}</h2><div class="bar"></div><div class="lede">{lede}</div></div></div><div class="tgrid">{"".join(cards)}</div></div></section>')

def trip(slug):
    pid = IDS[slug]; tr = TRIPS[slug]; data = raw(pid)
    it = [x for x in items(data) if x[0] not in ('open', 'close', 'divider', 'spacer')]
    h1i = next(i for i, x in enumerate(it) if x[0] == 'h1'); h1 = it[h1i][1]
    secs, cur = [], {'kind': 'top', 'h': None, 'tag': None, 'items': []}
    for k, v, s in it[h1i + 1:]:
        if k in ('h2', 'h3', 'h5'):
            t = text_of(v); kind = classify(k, t)
            if kind == 'book':
                cur['items'].append(('book', s.get('link', {}).get('url', ''), s)); continue
            if kind == 'custom-sub' or (kind is None and cur['kind'] in ('hotels', 'guides', 'final', 'custom') and k == 'h3') or (kind is None and cur['kind'] == 'related' and not any(x[0] == 'h2' for x in cur['items'])):
                cur['items'].append((k, v, s)); continue
            if kind is None and cur['kind'] == 'top' and k == 'h2':
                kind = 'intro'
            elif kind is None and k == 'h2' and re.sub(r'\W', '', t.upper()).startswith(re.sub(r'\W', '', text_of(h1).upper())[:6]) and secs and secs[-1]['kind'] != 'top':
                kind = 'final'
            elif kind is None and k == 'h3' and cur['kind'] in ('glance', 'route', 'd2d', 'day', 'gallery', 'inc', 'notinc', 'transfers'):
                kind = 'day'
            elif kind is None and k == 'h2' and cur['kind'] == 'hotels':
                cur['items'].append((k, v, s)); continue
            elif kind is None and k in ('h2', 'h3') and cur['kind'] == 'final':
                cur['items'].append((k, v, s)); continue
            elif kind is None:
                kind = 'other'
            moved = []   # live puts a section's photo just before its heading: it belongs to the new section
            while cur['items'] and cur['items'][-1][0] == 'img' and cur['kind'] != 'top': moved.insert(0, cur['items'].pop())
            secs.append(cur); cur = {'kind': kind, 'h': v, 'tag': k, 'items': moved}
            continue
        cur['items'].append((k, v, s))
    secs.append(cur)
    S = lambda kind: [x for x in secs if x['kind'] == kind]
    one = lambda kind: (S(kind) or [None])[0]

    # ---------- top: dates, price, deposit, companion, book link, hero photo ----------
    top = secs[0]
    texts = [v for k, v, s in top['items'] if k == 'text']
    price_h = next((v for k, v, s in top['items'] if k in ('h4', 'h3', 'h5', 'h6') and '€' in text_of(v)), '')
    price_t = text_of(price_h).replace('​', '')
    early = re.search(r'(Early bird.*)$', price_t, re.I)
    price_main = price_t[:early.start()].strip() if early else price_t
    prices = [p.strip() for p in price_main.split('|')]
    book_urls = [v for k, v, s in it if k == 'book' and v] + [x[1] for x in [(k, v) for k, v, s in it] if False]
    book = next((s.get('link', {}).get('url') for k, v, s in it if k in ('h2', 'h3', 'h5') and classify(k, text_of(v)) == 'book' and s.get('link', {}).get('url')), None)
    book = book or next((v[1] for k, v, s in it if k == 'btn' and 'wetravel' in (v[1] or '')), '')
    assert 'wetravel' in book, (slug, book)
    small = [text_of(t) for t in texts[1:]]
    deposit = next((x for x in small if x.lower().startswith('deposit')), '')
    companion = next((x for x in small if 'companion' in x.lower()), '')
    stay = next((x for x in small if 'shorter or longer' in x.lower()), '')
    other_small = [x for x in small if x not in (deposit, companion, stay)]
    dates_live = text_of(texts[0]) if texts else ''
    hero_src = next((v for k, v, s in top['items'] if k == 'img'), None) or json.load(open(ROOT + f'stg-tours/backup/page-{pid}.json')).get('featured_media')
    # ---------- glance ----------
    g = one('glance'); glance = []
    if g:
        for k, v, s in g['items']:
            if k == 'text':
                for ln in lines(v):
                    t = text_of(ln)
                    a, sep, b = t.partition(':')
                    if sep and 1 < len(a.strip()) <= 40: glance.append((a.strip().capitalize(), E(b.strip().lstrip(':：-– ').strip())))
                    elif t: glance.append(('', ln))
    gl = {a.upper(): b for a, b in glance}
    get = lambda *keys: next((text_of(gl[k]) for k in gl for w in keys if w in k), '')
    # ---------- hero ----------
    hero_alt = f'{text_of(h1).title()} bike tour - Cigala Cycling Tours'
    tags = [TYPE[tr['type']], tr['country'], tr['level'].replace(', ', ' · ')]
    pr = prices[0] if prices else ''
    pr_rest = ' · '.join(prices[1:])
    li = ''.join(f'<li><span>{E(a)}</span><span>{E(b)}</span></li>' for a, b in [x for x in [
        ('Deposit', re.sub(r'(?i)^deposit\s*', '', deposit)) if deposit else None,
        ('Non-cycling companion', re.sub(r'(?i).*companion\s*(for)?\s*', '', companion)) if companion else None,
        ('Group size', re.split(r'\s*\(', get('GROUP'))[0]) if get('GROUP') else None] if x])   # short form here; the full text is in the Route facts
    extra_small = ''.join(f'<p class="note">{E(x)}</p>' for x in other_small)
    stay_html = (f'<p class="note">{E(stay)}</p>'.replace('contact us', f'<a href="{L}/contact/">contact us</a>')) if stay else ''
    sp = SPOTS.get(slug)
    spots_html = (f'<div class="spots"><span class="dot live" aria-hidden="true"></span>{E(f"{sp} spot{"s" if sp != 1 else ""} left" if isinstance(sp, int) else sp)}</div>') if sp else ''
    card = M.get('trip-' + slug)   # the trip's photo (tour cards); the live top image is a designed poster, shown next to the intro
    hero_img = (f'<img src="{card["url"]}" alt="{E(card["alt"])}">' if card else img_tag(hero_src, 2000, alt=hero_alt, lazy=False))
    hero = f'''<div class="hero thero">
  {hero_img}
  <div class="in">
    <div>
      <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / <a href="{L}/trips/" {EXT}>Bike tours</a> / {E(tr['name'])}</div>
      <div class="tags">{''.join(f'<span class="tag{" dot" if i == 0 and tr["type"] != "gravel" else " gdot" if i == 0 else ""}">{E(t)}</span>' for i, t in enumerate(tags))}</div>
      <h1>{E(h1)}</h1>
      <div class="dates">{E(dates_live)}</div>
    </div>
    <aside class="book" aria-label="Price and booking">
      <span class="lab">Price</span>
      <div class="price">{E(pr)}<small>{E(pr_rest)}</small></div>
      {f'<span class="early">{E(early.group(1).strip())}</span>' if early else ''}
      {spots_html}
      <ul>{li}</ul>
      <a class="btn btn-go btn-lg" href="{E(book)}" target="_blank" rel="noopener">Book now →</a>
      {stay_html}{extra_small}
    </aside>
  </div>
</div>'''
    # ---------- glance strip ----------
    dist, climb, days_riding = get('DISTANCE'), get('CLIMBING', 'ELEVATION'), get('DAYS RIDING', 'RIDING DAYS')
    cells = [(dist or tr['distance'], 'Total distance'), (climb or tr['climbing'], 'Total climbing'), (days_riding, 'Days riding'),
             (get('GROUP'), 'Group size'), (get('LEVEL') or tr['level'], 'Level'), (get('START'), 'Start & finish')]
    strip = ''.join(f'<div><div class="n{" sm" if len(n) > 12 else ""}">{E(n)}</div><div class="l">{E(l)}</div></div>' for n, l in cells if n)
    glance_html = f'<div class="in" style="padding-top:28px"><div class="panel glance" aria-label="Trip at a glance">{strip}</div></div>'
    # ---------- sections ----------
    def H(sec, eyebrow, fallback=None, tag=None):
        t = re.sub(r'<[^>]+>', '', sec['h']).replace('​', '').strip() if sec and sec['h'] else fallback
        tg = (sec['tag'] if sec and sec['tag'] in ('h2', 'h3') else None) or tag or 'h2'
        return f'<div class="head"><div><div class="eyebrow">{eyebrow}</div><{tg} class="sh">{E(t)}</{tg}><div class="bar"></div></div></div>'
    out = [hero, glance_html]
    nav = []
    intro = one('intro')
    if intro:
        paras = ''.join(clean(v) for k, v, s in intro['items'] if k == 'text')
        cimg = f'<div class="cardimg">{img_tag(hero_src, 1200, alt=hero_alt)}</div>' if hero_src and card else ''
        out.append(f'<section id="overview"><div class="in split"><div>{H(intro, "The trip")}<div class="prose">{paras}</div></div>{cimg}</div></section>')
        nav.append(('overview', 'Overview'))
    op = one('operator')
    if op:
        logo = next((v for k, v, s in op['items'] if k == 'img'), None)
        out.append(f'<section style="padding-top:28px"><div class="in"><div class="panel opbox">{H(op, "Official partner")}'
                   f'{img_tag(logo, 400, cls="oplogo") if logo else ""}</div></div></section>')
    route = one('route')
    # our own route map (tools/tours_route_maps.py, Cigala style) for every trip; the live map image only as a fallback
    mp = ROOT + f'tourspages/maps/{slug}.svg'
    svg = open(mp).read().replace('aria-label="Route map"', f'aria-label="{E(text_of(h1).title())} bike tour route map by Cigala Cycling Tours"') if os.path.exists(mp) else ''
    rimg = None
    if route and not svg:
        rimg = next((v for k, v, s in route['items'] if k == 'img'), None)
        for k, v, s in route['items']:
            if rimg is None and k == 'e-image':
                try: rimg = s['image']['value']['src']['value']['id']['value']
                except (KeyError, TypeError): pass
    facts = ''.join(f'<div><dt>{E(a)}</dt><dd>{b}</dd></div>' for a, b in glance if a)
    g_tag = (g['tag'] if g else 'h3')
    g_title = re.sub(r'<[^>]+>', '', g['h']).strip() if g else ''
    dl = f'<dl class="panel facts"><{g_tag} class="facts-h">{E(g_title)}</{g_tag}>{facts}</dl>' if facts else ''
    note = ROUTE_NOTES.get(slug, '')
    map_html = svg or (img_tag(rimg, 1400, alt=f"{text_of(h1).title()} bike tour map by Cigala Cycling Tours") if rimg else '')
    if map_html or dl:
        head = H(route, 'Where you ride') if route else '<div class="head"><div><div class="eyebrow">Where you ride</div><p class="band-title">Route</p><div class="bar"></div></div></div>'
        out.append(f'<section id="route"><div class="in">{head}<div class="route"><div class="map">{map_html}'
                   f'{f"<p class=mapnote>{E(note)}</p>" if note else ""}</div>{dl}</div></div></section>')
        nav.append(('route', 'Route'))
    days = S('day')
    if days:
        d2d = one('d2d')
        gpx = ''.join(f'<p class="gpx">{text_of(v)}</p>' for k, v, s in (d2d['items'] if d2d else []) if k == 'text')
        lis = []
        for n, d in enumerate(days, 1):
            t, km, up = km_m(text_of(d['h']))
            chips = (f'<span class="chip km">{km}</span>' if km else '') + (f'<span class="chip up">{up}</span>' if up else '')
            body = ''.join(clean(v) for k, v, s in d['items'] if k in ('text',)) + ''.join(f'<p>{clean(v)}</p>' for k, v, s in d['items'] if k in ('h4', 'h5', 'h6'))
            tg = d['tag'] if d['tag'] in ('h2', 'h3') else 'h3'
            lis.append(f'<li class="day"><div class="num"><span><small>DAY</small>{n}</span></div><div class="panel box"><{tg}>{E(t)}</{tg}>'
                       f'{f"<div class=meta>{chips}</div>" if chips else ""}<div class="prose">{body}</div></div></li>')
        head = H(d2d, 'Itinerary') if d2d else '<div class="head"><div><div class="eyebrow">Itinerary</div><p class="band-title">Day by day</p><div class="bar"></div></div></div>'
        out.append(f'<section id="itinerary"><div class="in">{head}{gpx}<ol class="days">{"".join(lis)}</ol></div></section>')
        nav.append(('itinerary', 'Day by day'))
    for ex in S('extra') + S('other'):
        body = ''.join(clean(v) for k, v, s in ex['items'] if k == 'text') + ''.join(f'<p>{clean(v)}</p>' for k, v, s in ex['items'] if k in ('h4', 'h5', 'h6'))
        btns = ''.join(f'<a class="btn btn-go" href="{E(u)}">{E(t.capitalize())} →</a>' for k, (t, u), s in [(k, v, s) for k, v, s in ex['items'] if k == 'btn'] if u)
        imgs = [v for k, v, s in ex['items'] if k == 'img']
        vid = next((re.search(r'(?:v=|youtu\.be/)([\w-]{11})', s.get('youtube_url', '')) for k, v, s in ex['items'] if k == 'video'), None)
        media_html = (f'<div class="vcard panel" style="margin-top:16px"><button type="button" class="yt" data-id="{vid.group(1)}" aria-label="Play the video">'
                      f'<img src="https://i.ytimg.com/vi/{vid.group(1)}/hqdefault.jpg" alt="{E(text_of(ex["h"]))} video" loading="lazy"><span class="play" aria-hidden="true"></span></button></div>') if vid else ''
        if imgs: media_html += '<div class="gal3" style="margin-top:16px">' + ''.join(img_tag(x, 1200, alt=f'{text_of(h1).title()} - Cigala Cycling Tours') for x in imgs[:3]) + '</div>'
        out.append(f'<section><div class="in"><div class="panel xbox">{H(ex, "Make it yours" if ex["kind"] == "extra" else "Good to know")}'
                   f'<div class="prose">{body}</div>{f"<div class=ctas>{btns}</div>" if btns else ""}{media_html}</div></div></section>')
    inc, notinc, trans = one('inc'), one('notinc'), one('transfers')
    if inc:
        inc_li = ''.join(f'<li><span>{x}</span></li>' for k, v, s in inc['items'] if k == 'text' for x in lines(clean(v)))
        side = ''
        if notinc:
            no_li = ''.join(f'<li><span>{x}</span></li>' for k, v, s in notinc['items'] if k == 'text' for x in lines(clean(v)))
            side += f'<div class="panel no" style="padding:22px 24px"><{notinc["tag"]}>{E(text_of(notinc["h"]))}</{notinc["tag"]}><ul>{no_li}</ul></div>'
        if trans:
            tl = []
            for k, v, s in trans['items']:
                if k == 'text':
                    for x in lines(clean(v)):
                        m = re.match(r'^\s*(\d{1,2}/\d{1,2})\s*(.*)$', text_of(x))
                        tl.append(f'<div><b>{m.group(1)}</b>{E(m.group(2))}</div>' if m else f'<div>{x}</div>')
            side += f'<div class="panel" style="padding:22px 24px"><{trans["tag"]}>{E(text_of(trans["h"]).rstrip(":"))}</{trans["tag"]}><div class="transfers">{"".join(tl)}</div></div>'
        out.append(f'<section id="included"><div class="in">{H(inc, "The details")}<div class="inc"><div class="panel"><ul>{inc_li}</ul></div>'
                   f'<div class="side">{side}</div></div></div></section>')
        nav.append(('included', "What's included"))
    for gsec in S('gallery'):
        pics = [x['id'] for k, v, s in gsec['items'] if k == 'gallery' for x in s.get('gallery', [])] + [v for k, v, s in gsec['items'] if k == 'img']
        seen = []; [seen.append(p) for p in pics if p not in seen]
        if not seen: continue
        figs = ''.join(f'<figure{" class=g-big" if n == 0 else ""}>{img_tag(p, 1400 if n == 0 else 900, alt=f"{text_of(h1).title()} bike tour - Cigala Cycling Tours")}</figure>' for n, p in enumerate(seen[:9]))
        out.append(f'<section id="gallery"><div class="in">{H(gsec, "Real riders, real roads")}<div class="gallery">{figs}</div></div></section>')
    hs = one('hotels')
    if hs:
        names = [(k, v) for k, v, s in hs['items'] if k == 'h3']
        notes = ''.join(f'<h2 class="hnote">{E(text_of(v))}</h2>' for k, v, s in hs['items'] if k == 'h2')
        mt = re.match(r'^\s*(ACCOM+ODATION|WHERE YOU WILL STAY)\s+(\S.*)$', text_of(hs['h']), re.I)
        if mt:   # one live heading holds both: split it into the section title and the hotel name
            names.insert(0, (hs['tag'] if hs['tag'] in ('h2', 'h3') else 'h3', mt.group(2)))
            hs = dict(hs, h=mt.group(1))
        txt = ''.join(clean(v) for k, v, s in hs['items'] if k == 'text')
        pics = [x['id'] for k, v, s in hs['items'] if k == 'gallery' for x in s.get('gallery', [])] + [v for k, v, s in hs['items'] if k == 'img']
        cards = []
        for n, (tg, v) in enumerate(names):
            t = text_of(v); stars = len(re.findall(r'\*', t)); sup = bool(re.search(r'\*\s*S\b', t))
            nm = re.sub(r'[*]+\s*S?\s*$', '', t).strip()
            if not nm: continue
            ph = f'<div class="ph">{img_tag(pics[n], 900, alt=f"{nm.title()} - {text_of(h1).title()} bike tour")}</div>' if n < len(pics) else ''
            st = (f'<div class="stars" aria-label="{stars} stars{" superior" if sup else ""}">{"★" * stars}{"<span class=sup>S</span>" if sup else ""}</div>') if stars else ''
            cards.append(f'<article class="panel hotel">{ph}<div class="tx">{st}<{tg}>{E(nm)}</{tg}></div></article>')
        rest = pics[len(cards):len(cards) + 5]
        strip_html = ('<div class="strip">' + ''.join(img_tag(p, 600, alt=f'{text_of(h1).title()} hotel - Cigala Cycling Tours') for p in rest) + '</div>') if rest else ''
        out.append(f'<section id="hotels"><div class="in">{H(hs, "Where you stay")}<div class="prose dprose">{txt}</div>{notes}'
                   f'<div class="hotels">{"".join(cards)}</div>{strip_html}</div></section>')
        nav.append(('hotels', 'Hotels'))
    bk = one('bike')
    if bk:
        bimg = next((v for k, v, s in bk['items'] if k == 'img'), None)
        dl, lede = [], []
        for k, v, s in bk['items']:
            if k != 'text': continue
            for ln in lines(clean(v)):
                m = re.match(r'^\s*(?:<[^>]+>)*([A-Z][A-Z ]{2,20}):?\s*(?:</[^>]+>)?\s+(.+)$', ln, re.S)
                if m and m.group(1).strip().isupper(): dl.append((m.group(1).strip().capitalize(), m.group(2).strip()))
                else: lede.append(ln)
        dlh = ''.join(f'<dt>{E(a)}</dt><dd>{b}</dd>' for a, b in dl)
        out.append(f'<section id="bike-rental"><div class="in"><div class="panel bike">'
                   f'{f"<div class=ph>{img_tag(bimg, 1000, alt=f'Rental bike for the {text_of(h1).title()} tour')}</div>" if bimg else ""}'
                   f'<div class="tx">{H(bk, "Travel light")}<div class="lede">{"".join(f"<p>{x}</p>" for x in lede)}</div><dl>{dlh}</dl></div></div></div></section>')
        nav.append(('bike-rental', 'Bike rental'))
    gd = one('guides')
    if gd:
        lede = ''; ppl = []; started = False
        for k, v, s in gd['items']:
            if k == 'img': ppl.append({'img': v, 'texts': []}); started = True
            elif k == 'h3' and ppl: ppl[-1]['name'] = (k, v)
            elif k == 'h3': ppl.append({'img': None, 'texts': [], 'name': (k, v)})
            elif k == 'text' and ppl: ppl[-1]['texts'].append(v)
            elif k == 'text': lede += clean(v)
        cards = []
        for p in ppl:
            if 'name' not in p: continue
            nm = text_of(p['name'][1]); role = text_of(p['texts'][0]) if p['texts'] else ''
            bio = ''.join(clean(x) for x in p['texts'][1:])
            ph = f'<div class="ph">{img_tag(p["img"], 600, alt=f"{nm.title()}, {role} at Cigala Cycling Tours")}</div>' if p['img'] else ''
            cards.append(f'<article class="panel guide">{ph}<div class="tx"><h3>{E(nm)}</h3><div class="role">{E(role)}</div>{bio}</div></article>')
        stats = []
        for st_ in S('stat'):
            lab = next((text_of(v) for k, v, s in st_['items'] if k == 'text'), '')
            stats.append(f'<div class="stat"><div class="n">{E(text_of(st_["h"]))}</div><div class="l">{E(lab)}</div></div>')
        st_html = f'<div class="panel stats">{"".join(stats)}</div>' if stats else ''
        out.append(f'<section id="guides"><div class="in">{H(gd, "Who rides with you")}<div class="lede gl">{lede}</div>'
                   f'<div class="guides">{"".join(cards)}</div>{st_html}</div></section>')
        nav.append(('guides', 'Guides'))
    fq = one('faq')
    qa = faqs(data)
    if fq and qa:
        fh = ''.join(f'<details class="panel faq"><summary><h3>{E(q)}</h3></summary><div class="a">{a}</div></details>' for q, a in qa)
        out.append(f'<section id="faq"><div class="in">{H(fq, "Good to know")}<div class="faqs">{fh}</div></div></section>')
    rel = one('related')
    if rel: out.append(related_html(rel, h1))
    rv = one('reviews')
    if rv: out.append(reviews_block(text_of(rv['h'])))
    cu = one('custom')
    if cu:
        sub = next((v for k, v, s in cu['items'] if k == 'h3'), '')
        b = next((v for k, v, s in cu['items'] if k == 'btn'), ('More information', L + '/trips/private-trips/'))
        bg = next((v for k, v, s in cu['items'] if k == 'bg'), None) or 4440
        out.append(f'<section><div class="in"><div class="band">{img_tag(bg, 1600, alt="Riders on a Cigala Cycling custom tour")}<div class="tx">'
                   f'<div class="eyebrow">Custom tours</div><h2>{E(text_of(cu["h"]))}</h2><div class="bar"></div>'
                   f'{f"<h3 class=lede>{E(text_of(sub))}</h3>" if sub else ""}<div class="ctas"><a class="btn btn-go" href="{E(b[1])}">{E(b[0].capitalize())} →</a></div></div></div></div></section>')
    fin = one('final')
    fin_dates = next((text_of(v) for k, v, s in (fin['items'] if fin else []) if k in ('h3', 'h2', 'text')), dates_live)
    ftag = fin['tag'] if fin else None
    ftitle = f'<{ftag} class="fin-h">{E(text_of(fin["h"]))}</{ftag}>' if fin else f'<p class="band-title">{E(text_of(h1))}</p>'
    dtag = next((k for k, v, s in (fin['items'] if fin else []) if k in ('h3', 'h2')), None)
    fdates = f'<{dtag} class="fin-d">{E(fin_dates)}</{dtag}>' if dtag else f'<div class="fin-d">{E(fin_dates)}</div>'
    out.append(f'<section><div class="in"><div class="panel final"><div class="eyebrow">Ready to ride?</div>{ftitle}{fdates}'
               f'<div class="ctas"><a class="btn btn-go" href="{E(book)}" target="_blank" rel="noopener">Book now →</a>'
               f'<a class="btn btn-ghost" href="{L}/contact/">Ask a question</a></div></div></div></section>')
    tabs = ''.join(f'<a href="#{a}">{E(b)}</a>' for a, b in nav)
    out.insert(1, f'<nav class="tabs" aria-label="On this page"><div class="in">{tabs}<a class="btn btn-go" href="{E(book)}" target="_blank" rel="noopener">Book now</a></div></nav>')
    # structured data (SEO, Matteo: only improve): TouristTrip with the route places and the euro price, linked to the site's Organization
    num = re.sub(r'[^\d.]', '', pr.replace(',', ''))
    places = [n for n, la, lo, k, ps in _trm.ROUTES.get(slug, {}).get('pts', [])]
    intro_txt = text_of(''.join(clean(v) for k, v, s in (intro['items'] if intro else []) if k == 'text'))[:300]
    ld = {"@context": "https://schema.org", "@type": "TouristTrip", "name": tr['name'], "url": f"{L}/trips/{slug}/",
          "description": intro_txt or f"Guided {TYPE[tr['type']].lower()} cycling tour in {tr['country']} with Cigala Cycling Tours.",
          "touristType": "Cyclists", "provider": {"@id": f"{L}/#organization"}}
    if card: ld["image"] = card['url']
    if places: ld["itinerary"] = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i, "item": {"@type": "Place", "name": n}} for i, n in enumerate(places, 1)]}
    if num: ld["offers"] = {"@type": "Offer", "price": num, "priceCurrency": "EUR", "url": book, "availability": "https://schema.org/InStock"}
    out.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>')
    out.append(YT_JS if 'class="yt"' in ''.join(out) else '')
    main = '\n'.join(x for x in out if x)
    main = main.replace('href="https://staging.tours.cigalacycling.com', 'href="' + L)   # links only; images stay on staging
    return {'id': pid, 'slug': 'trip-' + slug, 'main': main, 'css': PAGE_CSS + TRIP_CSS, 'crumb': tr['name']}

TRIP_CSS = '''
html .cl .thero .in { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 32px; align-items: end; }
@media (max-width: 900px) { html .cl .thero .in { grid-template-columns: minmax(0, 1fr); } }
html .cl .tag.gdot::before { content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--gravel); margin-right: 7px; vertical-align: 1px; }
html .cl .book .price small { display: block; margin-top: 8px; }
html .cl .book .spots { display: flex; align-items: center; gap: 2px; margin: 12px 0 4px; font-size: 13.5px; font-weight: 700; color: #fff; }
html .cl .book p.note a { color: var(--green-text); text-decoration: underline; text-underline-offset: 3px; }
html .cl .route .map { background: none !important; border: 0 !important; padding: 0 !important; aspect-ratio: auto !important; }
html .cl .dtour .desc { display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden; }
html .cl .route .map svg { display: block; width: 100%; height: auto; border-radius: 12px; border: 1px solid var(--border); }
html .cl .route .map .mapnote { margin: 10px 0 0; font-size: 13px; color: var(--text-3); }
html .cl .route .map img { object-fit: contain !important; height: auto !important; aspect-ratio: auto !important; }
html .cl #overview .cardimg img { aspect-ratio: auto !important; height: auto !important; object-fit: contain !important; }
html .cl .hnote { font-family: var(--body); font-size: 15px; font-weight: 600; letter-spacing: .02em; text-transform: none; color: var(--green-text); margin: 4px 0 16px; }
html .cl .thero .book { min-width: 0; grid-template-columns: minmax(0, 1fr); }
html .cl .thero .book > * { max-width: 100%; }
html .cl .thero .book ul { min-width: 0; width: 100%; }
html .cl .thero .book li { display: grid !important; grid-template-columns: auto minmax(0, 1fr); gap: 14px; white-space: normal; min-width: 0; }
html .cl .thero .book li span { white-space: normal !important; min-width: 0; }
html .cl .thero .book li span:last-child { text-align: right; overflow-wrap: anywhere; }
html .cl .thero .book p.note { display: block; margin: 8px 0 0; }
html .cl .sh { }
html .cl h3.sh { font-size: clamp(30px, 4.4vw, 48px); }
html .cl .facts .facts-h { grid-column: 1 / -1; font-size: 13px; font-family: var(--body); font-weight: 600; letter-spacing: .1em; color: var(--text-3); margin: 0 0 6px; }
html .cl .days { list-style: none; margin: 0; padding: 0; }
html .cl .day .prose p { margin: 0 0 10px; }
html .cl .xbox, html .cl .opbox { padding: clamp(20px, 3vw, 32px); }
html .cl .opbox { display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
html .cl .opbox .head { margin: 0; }
html .cl .opbox .oplogo { width: 120px; height: auto; background: #fff; border-radius: 10px; padding: 10px; }
html .cl .hotel h3, html .cl .hotel h2 { font-size: 22px; }
html .cl .stars .sup { font-size: 11px; letter-spacing: 0; vertical-align: 2px; margin-left: 4px; }
html .cl .guide .tx p { margin: 8px 0 0; font-size: 14px; color: var(--text-2); }
html .cl .gl p { margin: 0 0 16px; }
html .cl .final { text-align: center; padding: clamp(28px, 5vw, 56px) 20px; }
html .cl .final .fin-h { font-size: clamp(34px, 5vw, 60px); }
html .cl .final .fin-d { font-family: var(--body); font-size: 16px; font-weight: 600; letter-spacing: .06em; color: var(--text-2); margin: 10px 0 20px; text-transform: uppercase; }
html .cl .final .ctas { justify-content: center; }
html .cl h2.ey2 { font-family: var(--body); font-size: 12px; line-height: 1.4; font-weight: 600; letter-spacing: .14em; color: #ff3d33; margin: 0 0 10px; }
html .cl .dtour .by { font-size: 11px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: #ff3d33; }
html .cl .dtour h3 { font-size: 22px; line-height: 1.14; }
html .cl .band h3.lede { font-family: var(--body); font-weight: 400; text-transform: none; letter-spacing: 0; font-size: 17px; line-height: 1.5; color: var(--text-2); }
'''

# the shared status dot (shared/dot/dot.css), scoped to the spots line (the trip tags also use a .dot class)
TRIP_CSS += re.sub(r'(?m)^\.dot', 'html .cl .spots .dot', re.sub(r'/\*.*?\*/', '', open(ROOT + 'shared/dot/dot.css').read(), flags=re.S)).replace('{ .dot.live', '{ html .cl .spots .dot.live')

if __name__ == '__main__':
    prev_shell = open(ROOT + 'tourspages/trips.html').read()
    for slug in sys.argv[1:] or IDS:
        d = trip(slug)
        d['main'] = fix_text(d['main'])
        a, b = prev_shell.index('<div class="cl cl-page">'), prev_shell.index('<div class="cc"><footer>')
        prev = prev_shell[:a] + '<div class="cl cl-page">\n' + d['main'] + '\n</div>\n' + prev_shell[b:]
        prev = prev.replace('</style>', '</style>\n<style>\n' + d['css'] + '\n</style>', 1)
        open(ROOT + f'tourspages/page-trip-{slug}.html', 'w').write(prev)
        json.dump(d, open(ROOT + f'stg-tours/out/list-trip-{slug}.json', 'w'), ensure_ascii=False)
        m = d['main']
        print(slug, len(m), 'chars | h1', m.count('<h1'), '| h2', m.count('<h2'), '| h3', m.count('<h3'), '| days', m.count('class="day"'), '| img', m.count('<img'))
