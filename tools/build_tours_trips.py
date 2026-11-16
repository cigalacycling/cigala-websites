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
_SPJ = json.load(open(ROOT + 'tours/spots.json'))
SPOTS = {k: v for k, v in _SPJ.items() if not k.startswith('_')}
TRIP_VIDEO = {'cyprus-crossing-gravel': ('jrRjn70pquM', 3353)}   # YouTube id, cover photo (our own: no YouTube request until the visitor taps play) - Matteo 16 Nov
HERO_PHOTO = {'discover-the-algarve-granfondo': 710}   # media id: rider in Cigala kit above an Algarve beach
HERO_DPOS = {'tour-of-flanders-experience': '50% 65%'}   # focus point on laptops (Matteo 16 Nov: Flanders showed the arch, not the riders)
HOTEL_FALLBACK = {'tour-of-flanders-experience': ('h3', 'Hotel T')}   # live has no hotel heading: the main card (stars: add '****' once Matteo confirms)
HERO_MPOS = {'tour-of-flanders-experience': '50% 70%', 'discover-the-algarve-granfondo': '80% 45%', 'chianti-gran-fondo-strade-bianche': '52% 30%'}   # focus point of the hero photo on phones
AVAIL = {'low': ('Last few spots', ''), 'mid': ('Filling up fast', ' amber'), 'high': ('Spots available', ' green')}   # wording + dot colour, same on every tour (Matteo 16 Nov)
MON = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

_sv = lambda d: f'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{d}</svg>'
ICON = {   # line icons for the glance strip and Trip at a glance (Matteo 16 Nov)
    'route': _sv('<circle cx="5" cy="18" r="2.2"/><circle cx="19" cy="6" r="2.2"/><path d="M7 18h8.5a3.5 3.5 0 0 0 0-7h-7a3.5 3.5 0 0 1 0-7H17"/>'),
    'climb': _sv('<path d="M2 20l6.5-10 4 6 3-4.5L22 20z"/><path d="M15.5 11.5l1.8-2.7"/>'),
    'cal': _sv('<rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>'),
    'level': _sv('<path d="M5 19v-4M12 19v-8M19 19V5"/>'),
    'pin': _sv('<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>'),
    'group': _sv('<circle cx="9" cy="8.5" r="3"/><path d="M3.5 19a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="9.5" r="2.4"/><path d="M15.5 14.2A4.6 4.6 0 0 1 21 18.5"/>'),
    'flag': _sv('<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>'),
    'plane': _sv('<path d="M10.5 13.5L3 11l1.5-1.5 8 .5 4-4.5a2 2 0 0 1 3 3l-4.5 4 .5 8L14 22l-2.5-7.5L8 18v2.5L6.5 22l-1-3.5L2 17.5 3.5 16H6z"/>'),
    'dot': _sv('<circle cx="12" cy="12" r="3"/>'),
}

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
        if k == 'text' and cur['kind'] in ('inc', 'notinc', 'transfers', 'entry') and len(text_of(v)) < 40:   # short text lines used as box titles live
            tt = text_of(v).strip().rstrip(':').upper()
            if tt in ('AIRPORT TRANSFERS', 'AIRPORT TRANSFER'): secs.append(cur); cur = {'kind': 'transfers', 'h': text_of(v), 'tag': 'p', 'items': []}; continue
            if tt.startswith('GRAN FONDO ENTRY PRICE'): secs.append(cur); cur = {'kind': 'entry', 'h': text_of(v), 'tag': 'p', 'items': []}; continue
        if k == 'h4' and classify(k, text_of(v)) in ('inc', 'notinc', 'transfers'):   # some pages have "What's not included" as an H4
            secs.append(cur); cur = {'kind': classify(k, text_of(v)), 'h': v, 'tag': 'h4', 'items': []}; continue
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
    g = one('glance'); glance = []; g_trans = []
    KEYS = r'(START\s*&(?:amp;)?\s*FINISH(?: LOCATION)?|START(?: LOCATION)?|FINISH(?: LOCATION)?|DAYS RIDING|RIDING DAYS|TOTAL DISTANCE|TOTAL ELEVATION|TOTAL CLIMBING|DISTANCE|ELEVATION|CLIMBING|GROUP SIZE|LEVEL|LONGEST DAY|DIFFICULTY)'
    if g:
        in_trans = False
        for k, v, s in g['items']:
            if k == 'text':
                for ln in lines(v):
                    t = text_of(ln).strip()
                    if not t: continue
                    if re.match(r'(?i)^airport transfers?:?$', t): in_trans = True; continue
                    if in_trans:   # "Inbound 28/07 12:00 pm noon from Geneva Airport (GVA)"
                        m = re.match(r'(?i)^(inbound|outbound|arrival|departure)\s*:?\s*(.*)$', t)
                        g_trans.append((m.group(1).capitalize(), m.group(2)) if m else ('', t)); continue
                    m = re.match(r'(?i)^' + KEYS + r'\s*:*\s*(.+)$', t)
                    if m: glance.append((m.group(1).capitalize(), E(m.group(2).strip().lstrip(':：-– ').strip())))
                    else: glance.append(('', ln))
    gl = {a.upper(): b for a, b in glance}
    get = lambda *keys: next((text_of(gl[k]) for k in gl for w in keys if w in k), '')
    # ---------- hero ----------
    hero_alt = f'{text_of(h1).title()} bike tour - Cigala Cycling Tours'
    tags = [TYPE[tr['type']], tr['country'], tr['level'].replace(', ', ' · ')]
    # Matteo 16 Nov: the country as a round flag, the level with the same 3-bar meter as the tour cards
    fl = M.get('flag-' + {'Italy': 'it', 'France': 'fr', 'Portugal': 'pt', 'Slovenia': 'si', 'Cyprus': 'cy', 'Belgium': 'be'}.get(tr['country'], ''))
    lb = {'beginner': 1, 'intermediate': 2, 'expert': 3}.get(tr['level'].split(',')[0].strip().lower(), 2)
    lmeter = '<span class="lm" aria-hidden="true">' + ''.join('<i class=on></i>' if i < lb else '<i></i>' for i in range(3)) + '</span>'
    tags_html = (f'<span class="tag{" dot" if tr["type"] != "gravel" else " gdot"}">{E(tags[0])}</span>'
                 + f'<span class="tag">{E(tags[1])}</span>'   # the country by name (Matteo 16 Nov: the flags stay on the cards only)
                 + f'<span class="tag tlvl">{lmeter}{E(tags[2])}</span>')
    pr = prices[0] if prices else ''
    pr_rest = ' · '.join(prices[1:])
    li = ''.join(f'<li><span>{E(a)}</span><span>{E(b)}</span></li>' for a, b in [x for x in [
        ('Deposit', re.sub(r'(?i)^deposit\s*', '', deposit)) if deposit else None,
        ('Non-cycling companion', re.sub(r'(?i).*companion\s*(for)?\s*', '', companion)) if companion else None,
        ('Group size', re.split(r'\s*\(', get('GROUP'))[0]) if get('GROUP') else None] if x])   # short form here; the full text is in the Route facts
    extra_small = ''.join(f'<p class="note">{E(x)}</p>' for x in other_small)
    stay_html = (f'<p class="note">{E(stay)}</p>'.replace('contact us', f'<a href="{L}/contact/">contact us</a>')) if stay else ''
    sp = SPOTS.get(slug, _SPJ.get('_default'))
    av_txt, av_cls = AVAIL.get(sp, AVAIL['high'])
    spots_html = f'<div class="spots av-{sp}"><span class="dot live{av_cls}" aria-hidden="true"></span>{E(av_txt)}</div>'
    card = M.get('trip-' + slug)   # the trip's photo (tour cards); the live top image is a designed poster, shown next to the intro
    hero_img = (f'<img src="{card["url"]}" alt="{E(card["alt"])}">' if card else img_tag(hero_src, 2000, alt=hero_alt, lazy=False))
    if slug in HERO_PHOTO:   # a hero photo of its own (Matteo 16 Nov: the Algarve card photo was also used further down)
        hero_img = img_tag(HERO_PHOTO[slug], 2000, alt=hero_alt, lazy=False)
    hero_img = hero_img.replace('<img ', f'<img style="--mpos:{HERO_MPOS.get(slug, "50% 30%")};--dpos:{HERO_DPOS.get(slug, "center 40%")}" ', 1)   # phones: where the rider is in the photo
    hero = f'''<div class="hero thero">
  {hero_img}
  <div class="in">
    <div>
      <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / <a href="{L}/trips/" {EXT}>Bike tours</a> / {E(tr['name'])}</div>
      <div class="tags">{tags_html}</div>
      <h1>{E(h1)}</h1>
      <div class="dates">{E(dates_live)}</div>
      {'<a class="btn btn-ghost hvid" href="#video"><span class="pl" aria-hidden="true"></span>Watch the video</a>' if slug in TRIP_VIDEO else ''}
    </div>
    <aside class="book bk2" aria-label="Price and booking">
      <div class="bk-top">
        <span class="lab">Price per person</span>
        <div class="price">{E(pr)}<small>{E(pr_rest)}</small></div>
        {f'<span class="early">{E(early.group(1).strip())}</span>' if early else ''}
        {spots_html}
      </div>
      <ul>{li}</ul>
      <div class="bk-cta"><a class="btn btn-go btn-lg" href="{E(book)}" target="_blank" rel="noopener">Book now →</a></div>
      {f'<div class="bk-notes">{stay_html}{extra_small}</div>' if stay_html or extra_small else ''}
    </aside>
  </div>
</div>'''
    # ---------- glance strip ----------
    dist, climb, days_riding = get('DISTANCE'), get('CLIMBING', 'ELEVATION'), get('DAYS RIDING', 'RIDING DAYS')
    from datetime import date as _d
    nights = (_d.fromisoformat(tr['end']) - _d.fromisoformat(tr['start'])).days
    lvl = tr['level']; bars = {'beginner': 1, 'intermediate': 2, 'expert': 3}.get(lvl.split(',')[0].strip().lower(), 2)
    meter = '<span class="lm" aria-hidden="true">' + ''.join('<i class=on></i>' if i < bars else '<i></i>' for i in range(3)) + '</span>'
    short = lambda x: re.split(r'\s*(?:\(|approx|apprx|depending)', x, flags=re.I)[0].strip() or x   # the strip shows the number; the full line is in Trip at a glance
    cells = [('route', short(dist or tr['distance']), 'Total distance'), ('climb', short(climb or tr['climbing']).lstrip('+').replace(' mt', ' m'), 'Total climbing'),
             ('cal', short(days_riding) if days_riding else f'{nights + 1} days', 'Days riding' if days_riding else f'{nights} nights'),
             ('level', lvl.replace(', ', ' · '), 'Level')]   # 4 cells: one full row, a closed box (Matteo 16 Nov)
    strip = ''.join(f'<div><span class="gi" aria-hidden="true">{ICON[ic]}</span><div><div class="n{" sm" if len(n) > 12 else ""}">{meter if ic == "level" else ""}{E(n)}</div><div class="l">{E(l)}</div></div></div>' for ic, n, l in cells if n)
    glance_html = f'<div class="in" style="padding-top:28px"><div class="panel glance g4" aria-label="Trip at a glance">{strip}</div></div>'
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
        pst = M.get('poster-' + slug)   # the poster with our map badge (tools/tours_posters.py)
        cimg = (f'<div class="cardimg"><img src="{pst["url"]}" alt="{E(pst["alt"])}" loading="lazy"></div>' if pst else
                f'<div class="cardimg">{img_tag(hero_src, 1200, alt=hero_alt)}</div>') if hero_src and card else ''
        out.append(f'<section id="overview"><div class="in split"><div>{H(intro, "The trip")}<div class="prose">{paras}</div></div>{cimg}</div></section>')
        nav.append(('overview', 'Overview'))
    if slug in TRIP_VIDEO:   # the trip on film, right after the intro (Matteo 16 Nov); YouTube loads only when the visitor taps play (YT_JS, youtube-nocookie)
        vid, cover = TRIP_VIDEO[slug]
        out.append(f'<section id="video" style="padding-top:28px"><div class="in"><div class="head"><div><div class="eyebrow">Watch the trip</div>'
                   f'<p class="band-title">{E(re.sub(r"\s*\|\s*Gravel$", "", tr["name"]))} on film</p><div class="bar"></div></div></div>'
                   f'<div class="panel vcard tvid"><button type="button" class="yt" data-id="{vid}" aria-label="Play the {E(re.sub(r"\s*\|\s*Gravel$", "", tr["name"]))} video">'
                   f'{img_tag(cover, 1600, alt=f"{tr["name"]} gravel cycling tour video - Cigala Cycling Tours")}<span class="play" aria-hidden="true"></span></button></div></div></section>')
        nav.append(('video', 'Video'))
    op = one('operator')
    if op:
        logo = next((v for k, v, s in op['items'] if k == 'img'), None)
        out.append(f'<section style="padding-top:28px"><div class="in"><div class="panel opbox">{H(op, "Official partner")}'
                   f'{img_tag(logo, 400, cls="oplogo") if logo else ""}</div></div></section>')
    route = one('route')
    # our own route map (tools/tours_route_maps.py, Cigala style) for every trip; the live map image only as a fallback
    mp = ROOT + f'tourspages/maps/day-{slug}.svg'   # day-by-day routes on real roads (tools/tours_day_routes.py, Matteo 16 Nov)
    if not os.path.exists(mp): mp = ROOT + f'tourspages/maps/{slug}.svg'
    svg = open(mp).read().replace('aria-label="Route map"', f'aria-label="{E(text_of(h1).title())} bike tour route map by Cigala Cycling Tours"') if os.path.exists(mp) else ''
    rimg = None
    if route and not svg:
        rimg = next((v for k, v, s in route['items'] if k == 'img'), None)
        for k, v, s in route['items']:
            if rimg is None and k == 'e-image':
                try: rimg = s['image']['value']['src']['value']['id']['value']
                except (KeyError, TypeError): pass
    def ficon(a):
        u = a.upper()
        for w, ic in (('START', 'pin'), ('FINISH', 'pin'), ('DAYS', 'cal'), ('DISTANCE', 'route'), ('ELEVATION', 'climb'), ('CLIMB', 'climb'),
                      ('GROUP', 'group'), ('LEVEL', 'level'), ('DIFFICULTY', 'level'), ('LONGEST', 'flag')):
            if w in u: return ICON[ic]
        return ICON['dot']
    facts = ''.join(f'<div><span class="fi" aria-hidden="true">{ficon(a)}</span><dt>{E(a)}</dt><dd>{b}</dd></div>' for a, b in glance if a)
    if g_trans:
        facts += '<div class="ftrans"><span class="fi" aria-hidden="true">' + ICON['plane'] + '</span><dt>Airport transfers</dt><dd>' + ''.join(
            f'<span class="tl"><b>{E(a)}</b> {E(b)}</span>' if a else f'<span class="tl">{E(b)}</span>' for a, b in g_trans) + '</dd></div>'
    g_tag = (g['tag'] if g else 'h3')
    g_title = re.sub(r'<[^>]+>', '', g['h']).strip() if g else ''
    dl = f'<dl class="panel facts"><{g_tag} class="facts-h">{E(g_title)}</{g_tag}>{facts}</dl>' if facts else ''
    note = ROUTE_NOTES.get(slug, '')
    map_html = svg or (img_tag(rimg, 1400, alt=f"{text_of(h1).title()} bike tour map by Cigala Cycling Tours") if rimg else '')
    dmeta = json.load(open(ROOT + 'tours/routes/days-meta.json')).get(slug) if 'day-' in mp else None
    if dmeta and svg:   # the day list under the map: colour, day, title and distance from the itinerary; hover or tap highlights the day
        dl_ = []
        for n, d in enumerate(S('day'), 1):
            if str(n) not in dmeta: continue
            t, km, up = km_m(text_of(d['h']))
            kmv = km or re.search(r'(\d+)\s*km', text_of(''.join(v for k, v, s_ in d['items'] if k == 'text'))) and f"{re.search(r'(\d+)\s*km', text_of(''.join(v for k, v, s_ in d['items'] if k == 'text'))).group(1)} km"
            dl_.append(f'<li><button type="button" data-d="{n}"><span class="sw" style="background:{dmeta[str(n)]["color"]}">{n}</span>'
                       f'<span class="dt">{E(t)}</span>{f"<span class=dk>{E(kmv)}</span>" if kmv else ""}</button></li>')
        map_html += f'<ol class="dleg" aria-label="Days on the map">{"".join(dl_)}</ol>'
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
        # Matteo 16 Nov: no stack of boxes on the right. Included | Not included side by side, then the airport transfers
        # and the Gran Fondo entry prices as full-width bands underneath.
        no_html = ''
        if notinc:
            no_li = ''.join(f'<li><span>{x}</span></li>' for k, v, s in notinc['items'] if k == 'text' for x in lines(clean(v)))
            no_html = f'<div class="panel no"><{notinc["tag"]} class="inh">{E(text_of(notinc["h"]))}</{notinc["tag"]}><ul>{no_li}</ul></div>'
        bands = ''
        if trans:
            rows, notes_ = [], []
            for k, v, s in trans['items']:
                if k != 'text': continue
                for x in lines(clean(v)):
                    t = text_of(x).strip()
                    m = re.match(r"^\s*(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\s*(.*)$", t)
                    if m: rows.append([m.group(1), m.group(2)])
                    elif rows and not rows[-1][1]: rows[-1][1] = t   # the date on its own line, the details on the next
                    else: notes_.append(x)
            cards = ''.join(f'<div class="tcard2"><span class="ic" aria-hidden="true">{ICON["plane"]}</span><div><b>{E(d)}</b><span>{E(t)}</span></div></div>' for d, t in rows)
            tt_ = trans["tag"]
            bands += (f'<div class="panel tband"><{tt_} class="inh">{E(text_of(trans["h"]).rstrip(":"))}</{tt_}><div class="trow">{cards}</div>'
                      + ''.join(f'<p class="tnote">{x}</p>' for x in notes_) + '</div>')
        ent = one('entry')
        if ent:   # Gran Fondo entry prices (Strade Bianche): the grid prices as tiles, then the notes
            ls_ = [x for k, v, s in ent['items'] if k == 'text' for x in lines(clean(re.sub(r'(€)(?=Grid)', r'\1<br>', v)))]
            grid_ = [re.match(r'^\s*(Grid \d+)\s*\(([^)]*)\)\s*:?\s*(.*)$', text_of(x)) for x in ls_]
            tiles = ''.join(f'<div class="ptile"><span>{E(m.group(1))}</span><b>{E(m.group(3))}</b><small>Places {E(m.group(2))}</small></div>' for m in grid_ if m)
            nts = ''.join(f'<p class="tnote">{x}</p>' for x, m in zip(ls_, grid_) if not m)
            bands += f'<div class="panel tband"><p class="inh">{E(text_of(ent["h"]).rstrip("*"))}</p><div class="prow">{tiles}</div>{nts}</div>'
        out.append(f'<section id="included"><div class="in">{H(inc, "The details")}<div class="inc2"><div class="panel yes"><p class="inh">Included in the price</p><ul>{inc_li}</ul></div>{no_html}</div>'
                   f'{bands}</div></section>')
        nav.append(('included', "What's included"))
    for gsec in S('gallery'):
        pics = [x['id'] for k, v, s in gsec['items'] if k == 'gallery' for x in s.get('gallery', [])] + [v for k, v, s in gsec['items'] if k == 'img']
        seen = []; [seen.append(p) for p in pics if p not in seen]
        if not seen: continue
        n_ = 9 if len(seen) >= 9 else 5 if len(seen) >= 5 else len(seen)   # big photo + 4 or 8: the grid has no empty cells (Matteo 16 Nov)
        figs = ''.join(f'<figure{" class=g-big" if n == 0 and n_ >= 5 else ""}>{img_tag(p, 1400 if n == 0 else 900, alt=f"{text_of(h1).title()} bike tour - Cigala Cycling Tours")}</figure>' for n, p in enumerate(seen[:n_]))
        out.append(f'<section id="gallery"><div class="in">{H(gsec, "Real riders, real roads")}<div class="gallery g{n_}">{figs}</div></div></section>')
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
        if not names and slug in HOTEL_FALLBACK: names = [HOTEL_FALLBACK[slug]]
        hotels_ = []
        for n, (tg, v) in enumerate(names):
            t = text_of(v); stars = len(re.findall(r'\*', t)); sup = bool(re.search(r'\*\s*S\b', t))
            nm = re.sub(r'[*]+\s*S?\s*$', '', t).strip()
            if nm: hotels_.append((n, tg, nm, stars, sup))
        def hcard(n, tg, nm, stars, sup, body='', cls=''):
            ph = f'<div class="ph">{img_tag(pics[n], 1200, alt=f"{nm.title()} - {text_of(h1).title()} bike tour")}</div>' if n < len(pics) else ''
            st = (f'<div class="stars" aria-label="{stars} stars{" superior" if sup else ""}">{"★" * stars}{"<span class=sup>S</span>" if sup else ""}</div>') if stars else ''
            return f'<article class="panel hotel{cls}">{ph}<div class="tx"><div class="eyebrow">Your hotel</div>{st}<{tg}>{E(nm)}</{tg}>{body}</div></article>'
        if len(hotels_) == 1:   # one hotel: photo and text side by side in one card (Matteo 16 Nov: no big empty black area)
            cards_html = hcard(*hotels_[0], body=f'<div class="prose">{txt}</div>{notes}', cls=' hotel1')
            intro_html = ''
        else:
            cards_html = '<div class="hotels">' + ''.join(hcard(*h, cls=' wide' if len(hotels_) % 2 and i == len(hotels_) - 1 else '') for i, h in enumerate(hotels_)) + '</div>'
            intro_html = f'<div class="prose dprose">{txt}</div>{notes}'
        rest = pics[len(hotels_):]
        k = 8 if len(rest) >= 8 else 4 if len(rest) >= 4 else 3 if len(rest) == 3 else 0   # full rows only
        strip_html = (f'<div class="strip s{4 if k != 3 else 3}">' + ''.join(img_tag(p, 600, alt=f'{text_of(h1).title()} hotel - Cigala Cycling Tours') for p in rest[:k]) + '</div>') if k else ''
        out.append(f'<section id="hotels"><div class="in">{H(hs, "Where you stay")}{intro_html}{cards_html}{strip_html}</div></section>')
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
            num = {'500+': '700+', '10': '11'}.get(text_of(st_['h']).strip(), text_of(st_['h']).strip())   # same numbers as the homepage (Matteo 15 Nov)
            num_h = E(num).replace('★', '<i>★</i>')   # the star in gold, as on the homepage
            stats.append(f'<div class="stat"><div class="n">{num_h}</div><div class="l">{E(lab)}</div></div>')
        st_html = f'<div class="cc tstats"><div class="stats">{"".join(stats)}</div></div>' if stats else ''   # the homepage stats (Matteo 16 Nov)
        out.append(f'<section id="guides"><div class="in">{H(gd, "Who rides with you")}<div class="lede gl">{lede}</div>'
                   f'<div class="guides{" g3" if len(cards) == 3 else ""}">{"".join(cards)}</div>{st_html}</div></section>')
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
    fspots = f'<div class="spots fspots av-{sp}"><span class="dot live{av_cls}" aria-hidden="true"></span>{E(av_txt)}</div>'   # the same availability line under the dates (Matteo 16 Nov)
    out.append(f'<section><div class="in"><div class="panel final"><div class="eyebrow">Ready to ride?</div>{ftitle}{fdates}{fspots}'
               f'<div class="ctas"><a class="btn btn-go" href="{E(book)}" target="_blank" rel="noopener">Book now →</a>'
               f'<a class="btn btn-ghost" href="{L}/contact/">Ask a question</a></div></div></div></section>')
    tabs = ''.join(f'<a href="#{a}">{E(b)}</a>' for a, b in nav)
    out.insert(1, f'<nav class="tabs" aria-label="On this page"><div class="in">{tabs}<a class="btn btn-go tbook" href="{E(book)}" target="_blank" rel="noopener">Book now</a></div></nav>')
    out.append("""<script>(function(){var m=document.querySelector('.cl .dmap'),l=document.querySelector('.cl .dleg');if(!m||!l)return;var cur=null;
function set(d){cur=d;m.classList.toggle('hl',!!d);m.querySelectorAll('.dr,.db').forEach(function(g){g.classList.toggle('on',g.dataset.d===d);});
l.querySelectorAll('button').forEach(function(b){b.classList.toggle('on',b.dataset.d===d);b.setAttribute('aria-pressed',b.dataset.d===d);});}
l.querySelectorAll('button').forEach(function(b){b.addEventListener('mouseenter',function(){set(b.dataset.d);});b.addEventListener('focus',function(){set(b.dataset.d);});
b.addEventListener('click',function(){set(cur===b.dataset.d?null:b.dataset.d);});});l.addEventListener('mouseleave',function(){set(null);});})();</script>""")   # day highlight on the route map
    # one Book now on screen at a time (Matteo 16 Nov): the bar's button shows once the price box has scrolled away
    out.append("""<script>(function(){var b=document.querySelector('.cl .thero .book'),t=document.querySelector('.cl .tabs');if(!b||!t||!('IntersectionObserver' in window))return;t.classList.add('nobook');
new IntersectionObserver(function(es){t.classList.toggle('nobook',es[0].isIntersecting);}).observe(b);})();</script>""")
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
    out.append("""<script>(function(){var l=document.querySelectorAll('.cl .stats .stat .n');if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
l.forEach(function(el){if(el.children.length)return;var m=el.textContent.match(/^([\\d,]+)(\\D*)$/);if(!m)return;var to=+m[1].replace(/,/g,''),suf=m[2],fmt=function(v){return v.toLocaleString('en-US')+suf;};el.style.minWidth=el.offsetWidth+'px';el.textContent=fmt(0);
new IntersectionObserver(function(es,ob){if(!es[0].isIntersecting)return;ob.disconnect();var t0=performance.now();(function f(t){var k=Math.min(1,(t-t0)/1500);el.textContent=fmt(Math.round(to*(1-Math.pow(1-k,3))));if(k<1)requestAnimationFrame(f);})(t0);},{threshold:.5}).observe(el);});})();</script>""")
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
html .cl #overview .cardimg { aspect-ratio: auto !important; height: auto; align-self: start; }   /* the box takes the poster's own shape: no empty band under square posters */
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
/* ---- Matteo 16 Nov: second review ---- */
html .cl .thero .dates { color: var(--green-text, #2bd47a); }
html .cl .thero .book.bk2 { padding: 0; gap: 0; background: rgba(12,14,16,.95); border: 1px solid rgba(255,255,255,.16); border-radius: 16px; overflow: hidden; box-shadow: 0 24px 60px rgba(0,0,0,.5); }
html .cl .bk2 .bk-top { padding: 22px 24px 18px; display: grid; gap: 10px; justify-items: start; }
html .cl .bk2 .bk-top .price { margin: 0; }
html .cl .bk2 ul { padding: 0 24px; gap: 0; border-top: 1px solid var(--border-strong); }
html .cl .bk2 ul:empty { display: none; }
html .cl .thero .bk2 ul li { border-top: 0; border-bottom: 1px solid var(--border); padding: 12px 0; }
html .cl .thero .bk2 ul li:last-child { border-bottom: 0; }
html .cl .bk2 .bk-cta { padding: 18px 24px 22px; border-top: 1px solid var(--border-strong); }
html .cl .bk2 .bk-cta .btn { width: 100%; justify-content: center; }
html .cl .bk2 .bk-notes { padding: 14px 24px 18px; border-top: 1px solid var(--border); background: rgba(255,255,255,.025); }
html .cl .thero .bk2 .bk-notes p.note:first-child { margin-top: 0; }
html .cl .glance.g4 > div { display: flex; gap: 14px; align-items: center; }
html .cl .glance .gi { flex: none; width: 42px; height: 42px; border-radius: 50%; display: grid; place-items: center; color: var(--green-text, #2bd47a); background: rgba(0,154,68,.12); border: 1px solid rgba(43,212,122,.28); }
html .cl .glance .n.sm { font-size: 15px; }
html .cl .glance.g4 > div > div { min-width: 0; }
html .cl .glance.g4 .n { white-space: normal; overflow-wrap: break-word; }
@media (max-width: 600px) { html .cl .glance.g4 > div { flex-direction: column; align-items: flex-start; gap: 10px; padding: 16px; } html .cl .glance .gi { width: 34px; height: 34px; } html .cl .glance .gi svg { width: 17px; height: 17px; } html .cl .glance.g4 .n:not(.sm) { font-size: 26px; } }
html .cl .lm { display: inline-flex; align-items: flex-end; gap: 2px; margin-right: 8px; vertical-align: 0; }
html .cl .lm i { display: block; width: 3px; border-radius: 1px; background: rgba(255,255,255,.22); }
html .cl .lm i:nth-child(1) { height: 5px; } html .cl .lm i:nth-child(2) { height: 8px; } html .cl .lm i:nth-child(3) { height: 11px; }
html .cl .lm i.on { background: var(--green-text, #2bd47a); }
html .cl .facts .facts-h { font-family: var(--head); font-weight: 400; font-size: 28px; line-height: 1.05; letter-spacing: .01em; color: var(--green-text, #2bd47a); margin: 0 0 10px; }
html .cl .facts div { grid-template-columns: 32px 128px minmax(0, 1fr); align-items: center; gap: 12px; }   /* icon centred on its title (Matteo 16 Nov) */
html .cl .facts div.ftrans { align-items: start; }
html .cl .facts .fi { width: 30px; height: 30px; border-radius: 50%; display: grid; place-items: center; color: var(--green-text, #2bd47a); background: rgba(0,154,68,.12); }
html .cl .facts .fi svg { width: 16px; height: 16px; }
html .cl .facts dt, html .cl .facts dd { padding-top: 0; }
html .cl .facts div.ftrans dt { padding-top: 7px; } html .cl .facts div.ftrans dd { padding-top: 5px; }
html .cl .facts .tl { display: block; margin-bottom: 4px; font-weight: 500; }
html .cl .facts .tl b { color: var(--green-text, #2bd47a); font-weight: 600; }
@media (max-width: 600px) { html .cl .facts div, html .cl .facts div.ftrans { grid-template-columns: 32px minmax(0, 1fr); align-items: center; row-gap: 4px; }
  html .cl .facts dt, html .cl .facts div.ftrans dt { padding-top: 0; } html .cl .facts dd, html .cl .facts div.ftrans dd { grid-column: 2; padding-top: 0; } }   /* phones: icon beside the title, the value under the title */
html .cl #itinerary .gpx { margin: 8px 0 30px; }
html .cl .gallery.g5, html .cl .gallery.g9 { grid-template-columns: repeat(4, minmax(0, 1fr)); grid-auto-flow: dense; }
html .cl .gallery .g-big { grid-column: span 2; grid-row: span 2; }
html .cl .gallery.g1 { grid-template-columns: minmax(0, 1fr); } html .cl .gallery.g2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
html .cl .gallery.g3 { grid-template-columns: repeat(3, minmax(0, 1fr)); } html .cl .gallery.g4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
@media (max-width: 700px) { html .cl .gallery.g5, html .cl .gallery.g9, html .cl .gallery.g4 { grid-template-columns: repeat(2, minmax(0, 1fr)); } html .cl .gallery.g3 { grid-template-columns: repeat(3, minmax(0, 1fr)); grid-auto-rows: 120px; } }
html .cl .hotel1, html .cl .hotels .hotel.wide { display: grid; grid-template-columns: minmax(0, 6fr) minmax(0, 5fr); overflow: hidden; }
html .cl .hotels .hotel.wide { grid-column: 1 / -1; }
html .cl .hotel1 .ph, html .cl .hotel.wide .ph { aspect-ratio: auto !important; height: 100%; min-height: 360px; }
html .cl .hotel1 .ph img, html .cl .hotel.wide .ph img { height: 100% !important; aspect-ratio: auto !important; }
html .cl .hotel1 .tx { padding: clamp(22px, 3vw, 36px); align-content: center; gap: 10px; }
html .cl .hotel .eyebrow { margin: 0; }
html .cl .hotel1 .prose p { font-size: 15px; line-height: 1.6; color: var(--text-2); margin: 6px 0 0; }
html .cl .hotel1 .hnote { margin: 12px 0 0; }
@media (max-width: 900px) { html .cl .hotel1, html .cl .hotels .hotel.wide { grid-template-columns: minmax(0, 1fr); } html .cl .hotel1 .ph, html .cl .hotel.wide .ph { min-height: 0; aspect-ratio: 16 / 10 !important; } }
html .cl .strip.s4 { grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 14px; }
html .cl .strip.s3 { grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 14px; }
@media (max-width: 640px) { html .cl .strip.s4 { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
html .cl .dprose + .hotels { margin-top: 18px; }
html .cl .guides.g3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
html .cl .guides.g3 .guide { grid-template-columns: minmax(0, 1fr); }
html .cl .guides.g3 .guide .ph img { aspect-ratio: 4 / 3; min-height: 0; height: auto; }
@media (max-width: 900px) { html .cl .guides.g3 { grid-template-columns: minmax(0, 1fr); } html .cl .guides.g3 .guide { grid-template-columns: 140px minmax(0, 1fr); } html .cl .guides.g3 .guide .ph img { aspect-ratio: auto; height: 100%; } }
html .cl .cc.tstats { margin-top: 32px; }
html .cl .tabs .tbook { transition: opacity .25s, visibility .25s; }
html .cl .tabs.nobook .tbook { opacity: 0; visibility: hidden; }
html .cl .final .fspots { justify-content: center; margin: -6px 0 20px; }
html .cl .tvid { max-width: 1000px; }
html .cl .tvid .play { width: 84px; height: 84px; margin: -42px 0 0 -42px; }
html .cl .tvid .play::after { left: 34px; top: 26px; border-width: 16px 0 16px 25px; }
html .cl .hvid { margin-top: 18px; display: inline-flex; align-items: center; gap: 10px; }
html .cl .hvid .pl { width: 22px; height: 22px; border-radius: 50%; background: #009a44; position: relative; flex: none; }
html .cl .hvid .pl::after { content: ""; position: absolute; left: 8px; top: 6px; border-style: solid; border-width: 5px 0 5px 8px; border-color: transparent transparent transparent #fff; }
@media (min-width: 901px) { html .cl .hero.thero > img { object-position: var(--dpos, center 40%); } }
/* phones: the hero photo as a clear band at the top, the title and the price box under it (Matteo 16 Nov: the rider and the jersey logo were hidden) */
@media (max-width: 900px) {
  html .cl .hero.thero > img { inset: 0 0 auto 0; height: 440px; object-position: var(--mpos, 50% 30%); }
  html .cl .hero.thero::after { inset: 0 0 auto 0; height: 442px; background: linear-gradient(180deg, rgba(8,9,10,.45) 0%, rgba(8,9,10,.05) 22%, rgba(8,9,10,.1) 55%, rgba(8,9,10,1) 100%); }
  html .cl .hero.thero .in { padding-top: 300px !important; }
  html .cl .hero.thero .crumbs { position: absolute; top: 94px; left: 16px; max-width: calc(100% - 32px); width: fit-content; box-sizing: border-box; background: rgba(8,9,10,.62); backdrop-filter: blur(6px); border-radius: 999px; padding: 5px 12px; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }   /* readable over the photo */
}
html .cl .thero .tag.tflag { padding: 3px; background: rgba(8,9,10,.6); }
html .cl .thero .tag.tflag img { display: block; width: 22px; height: 22px; border-radius: 50%; object-fit: cover; box-shadow: 0 0 0 1px rgba(255,255,255,.35); }
html .cl .thero .tag.tlvl .lm { margin-right: 7px; }
html .cl .dleg { list-style: none; margin: 12px 0 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 6px; }
html .cl .dleg button { width: 100%; display: flex; align-items: center; gap: 10px; text-align: left; background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 10px; padding: 8px 12px; color: var(--text-2); font: 600 13px/1.3 var(--body); cursor: pointer; transition: border-color .2s, background .2s; }
html .cl .dleg button:hover, html .cl .dleg button.on { border-color: rgba(255,255,255,.3); background: rgba(255,255,255,.06); color: #fff; }
html .cl .dleg .sw { flex: none; width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; color: #0a0c0e; font: 800 12px/1 var(--body); }
html .cl .dleg .dt { flex: 1; min-width: 0; white-space: normal; overflow-wrap: break-word; text-transform: uppercase; font-size: 11.5px; letter-spacing: .05em; }
html .cl .dleg button { white-space: normal; }
html .cl .dleg .dk { flex: none; color: var(--text-3); font-weight: 600; font-size: 12px; }
html .cl .dmap .dr, html .cl .dmap .db { transition: opacity .2s; }
html .cl .dmap.hl .dr:not(.on), html .cl .dmap.hl .db:not(.on) { opacity: .12; }
html .cl .dmap.hl .dr.on .ln { stroke-width: 4.5; }
html .cl .inc2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; align-items: start; }
html .cl .inc2 .panel, html .cl .tband { padding: 24px 26px; }
html .cl #included .inh { font-family: var(--head); font-weight: 400; font-size: 22px; line-height: 1.1; text-transform: uppercase; letter-spacing: .01em; color: var(--text); margin: 0 0 16px; }
html .cl #included ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
html .cl #included li { display: grid; grid-template-columns: 22px minmax(0, 1fr); gap: 10px; font-size: 14.5px; }
html .cl #included .yes li::before, html .cl #included .no li::before { content: ""; width: 20px; height: 20px; border-radius: 50%; margin-top: 2px; }
html .cl #included .yes li::before { background: rgba(0,154,68,.18) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Cpath d='M5.5 10.5l3 3 6-7' fill='none' stroke='%232bd47a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / 20px no-repeat; }
html .cl #included .no li::before { background: rgba(255,255,255,.04) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Cpath d='M7 7l6 6M13 7l-6 6' fill='none' stroke='%238a8f98' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E") center / 20px no-repeat; }
html .cl .tband { margin-top: 16px; }
html .cl .trow { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; }
html .cl .tcard2 { display: flex; gap: 12px; align-items: flex-start; background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }
html .cl .tcard2 .ic { flex: none; width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; color: var(--green-text, #2bd47a); background: rgba(0,154,68,.12); }
html .cl .tcard2 .ic svg { width: 17px; height: 17px; }
html .cl .tcard2 b { display: block; font-family: var(--head); font-weight: 400; font-size: 19px; color: var(--green-text, #2bd47a); letter-spacing: .02em; }
html .cl .tcard2 span { font-size: 14px; color: var(--text-2); line-height: 1.45; }
html .cl .tnote { margin: 12px 0 0; font-size: 13.5px; color: var(--text-3); }
html .cl .prow { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
html .cl .ptile { background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; display: grid; gap: 2px; }
html .cl .ptile span { font-size: 11.5px; font-weight: 600; letter-spacing: .09em; text-transform: uppercase; color: var(--text-3); }
html .cl .ptile b { font-family: var(--head); font-weight: 400; font-size: 28px; color: #fff; }
html .cl .ptile small { font-size: 12.5px; color: var(--text-3); }
@media (max-width: 800px) { html .cl .inc2 { grid-template-columns: minmax(0, 1fr); } }
html .cl .inc .sidet { font-family: var(--head); font-weight: 400; font-size: 20px; line-height: 1.1; text-transform: uppercase; letter-spacing: .01em; color: var(--text); margin: 0 0 14px; }
html .cl .inc .entryp li::before { width: 7px; height: 7px; margin: 8px 0 0 7px; background: var(--green-text, #2bd47a); }   /* prices, not included items: a plain dot */
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
