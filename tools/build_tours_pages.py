"""Tours content pages in the new design: About (more pages are added here one by one).

Source of truth for the words = the page's own Elementor data on Tours staging (a copy of live), so the
H1/H2 wording and tags, body copy, links and image alt text stay exactly as they are live (CLAUDE.md).
The layout follows the page designs in tourspages/ (tools/build_tours.py); their CSS is already in the kit (.cl).

Usage: python3 -I tools/build_tours_pages.py about
Writes the preview tourspages/page-<slug>.html and stg-tours/out/list-<slug>.json; push with
python3 -I tools/push_tours_list.py <slug>.
Images: WebP q90 from the largest originals on staging (tools/tours_img.py), alt text from the media library.
"""
import os, re, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_tours_wp import req, B
from tours_img import webp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
L = 'https://tours.cigalacycling.com'
EXT = 'target="_blank" rel="noopener"'
E = lambda x: html.escape(x, quote=True)

# ---------- Elementor data -> a flat list of content items, in page order ----------
def elementor(pid):
    """The page's ORIGINAL Elementor data: stg-tours/backup/page-<id>.json (saved before the first change).
    Never the current staging page, which holds our new layout once pushed."""
    f = ROOT + f'stg-tours/backup/page-{pid}.json'
    if not os.path.exists(f):
        code, r = req(f'{B}/wp/v2/pages/{pid}?context=edit&_fields=id,link,meta,featured_media')
        assert code == 200, (pid, code)
        d = json.loads(r)['meta']['_elementor_data'] or '[]'
        assert '"widgetType":"html"' not in d.replace(' ', '') or 'cl-page' not in d, f'page {pid} already rebuilt: restore its backup first'
        open(f, 'w').write(r.decode())
    p = json.load(open(f))
    return json.loads(p['meta']['_elementor_data'] or '[]')

def clean(h):
    h = re.sub(r'<span style="[^"]*">(.*?)</span>', r'\1', h, flags=re.S)
    h = re.sub(r' (data-[a-z-]+|style|class)="[^"]*"', '', h)
    h = re.sub(r'</?(div|section|article)\b[^>]*>', '', h)          # wrappers pasted in from other apps (they add big gaps)
    h = re.sub(r'<p>\s*(<p[ >])', r'\1', h); h = re.sub(r'(</p>)\s*</p>', r'\1', h)
    h = re.sub(r' (dir|tabindex|role|aria-[a-z-]+)="[^"]*"', '', h)
    h = re.sub(r'<p>(&nbsp;|\s)*</p>', '', h)
    h = h.replace('https://staging.tours.cigalacycling.com', L)
    return h.strip()

def items(els, out=None, depth=0):
    """[(kind, value, settings)]: h1..h6, text (html), img (media id or url), bg (container background), btn (text, url)."""
    out = [] if out is None else out
    for e in els:
        s = e.get('settings') or {}; s = s if isinstance(s, dict) else {}; w = e.get('widgetType')
        if w == 'heading': out.append((s.get('header_size', 'h2'), s.get('title', '').strip(), s))
        elif w == 'text-editor': out.append(('text', clean(s.get('editor', '')), s))
        elif w == 'image': out.append(('img', s.get('image', {}).get('id') or s.get('image', {}).get('url'), s))
        elif w == 'button': out.append(('btn', (s.get('text', '').strip(), s.get('link', {}).get('url', '')), s))
        elif e.get('elType') in ('container', 'section', 'column'):
            bg = s.get('background_image', {})
            if bg.get('url'): out.append(('bg', bg.get('id') or bg['url'], s))
            out.append(('open', depth, s))
            items(e.get('elements', []), out, depth + 1)
            out.append(('close', depth, s))
        elif w:
            out.append((w, None, s))
            if e.get('elements'): items(e['elements'], out, depth + 1)   # e.g. nested carousels hold containers
        elif e.get('elements'):   # newer Elementor elements (e-flexbox, e-div-block) hold containers and widgets
            items(e['elements'], out, depth + 1)
    return out

def text_of(h): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()
def link(u): return u.replace('https://staging.tours.cigalacycling.com', L)

def head_block(eyebrow, h, tag='h2', lede=''):
    l = f'<p class="lede">{lede}</p>' if lede else ''
    return f'<div class="head"><div><div class="eyebrow">{eyebrow}</div><{tag}>{E(h)}</{tag}><div class="bar"></div>{l}</div></div>'

def img_tag(src, maxw, cls='', alt=None, lazy=True):
    im = webp(src, maxw, alt)
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="{im["url"]}" alt="{E(im["alt"])}"{" loading=\"lazy\"" if lazy else ""}>'

# shared parts from the trip-list design (same as the tour pages): partners strip and the "custom tour" band
lists = open(ROOT + 'stg-tours/out/list-trips.json').read()
PARTNERS = re.search(r'<section>\s*<div class="in partners">.*?</section>', json.loads(lists)['main'], re.S).group(0)
# the live pages have these labels as H2s: keep them as H2s (styled like the small labels)
PARTNERS_H2 = re.sub(r'<div class="lab">([^<]*)</div>', r'<h2 class="lab">\1</h2>', PARTNERS)

# ===================== About (271) =====================
WHY_ICONS = [   # Why riders choose us, in the live order (Matteo 15 Nov: own icons instead of ticks)
 '<circle cx="12" cy="9" r="5"/><path d="M8.5 13 7 21l5-3 5 3-1.5-8"/>',                                    # expertise: medal
 '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4M8 14h2M12 14h2M16 14h0"/>',   # 10+ years: calendar
 '<circle cx="6" cy="18" r="2.2"/><circle cx="18" cy="6" r="2.2"/><path d="M8 18h7a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h7"/>',   # hand-built routes
 '<path d="M3 16V8a1 1 0 0 1 1-1h11l4 4h1a1 1 0 0 1 1 1v4H3z"/><circle cx="7.5" cy="16.5" r="1.8"/><circle cx="16.5" cy="16.5" r="1.8"/>',   # support vehicle
 '<path d="M12 4v16M5 8h14M5 8l-2.5 6a2.5 2.5 0 0 0 5 0zM19 8l-2.5 6a2.5 2.5 0 0 0 5 0zM8 20h8"/>',          # balance
 '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3 20a6 6 0 0 1 12 0M14.5 20a4.5 4.5 0 0 1 7-3.7"/>']   # all levels: people
def about():
    it = items(elementor(271))
    h1 = next(v for k, v, s in it if k == 'h1')
    heads = [i for i, (k, v, s) in enumerate(it) if k == 'h2']
    def h2_index(word): return next(i for i in heads if word in it[i][1].upper())
    why_i, team_i, ready_i, op_i = h2_index('WHY RIDERS'), h2_index('OUR TEAM'), h2_index('READY'), h2_index('TOUR OPERATOR')
    story = ''.join(v for k, v, s in it[:why_i] if k == 'text')
    why = []
    for k, v, s in it[why_i:team_i]:
        if k != 'text': continue
        m = re.match(r'<p><strong>✔\s*(.*?)</strong>\s*(?:<br\s*/?>)?\s*(.*)</p>$', v, re.S)
        assert m, v
        why.append((m.group(1).strip(), m.group(2).strip()))
    whyh = ''.join(f'<div class="panel"><span class="oic" aria-hidden="true"><svg viewBox="0 0 24 24">{WHY_ICONS[n % len(WHY_ICONS)]}</svg></span><div><h3>{h}</h3><p>{p}</p></div></div>' for n, (h, p) in enumerate(why))
    team = []   # each member: a container with a background photo, then two texts: name, role
    for k, v, s in it[team_i:ready_i]:
        if k == 'bg': team.append([v])
        elif k == 'text' and team and len(team[-1]) < 3: team[-1].append(text_of(v))
    assert team and all(len(m) == 3 for m in team), team
    # Matteo 16 Nov: Alessio "Bone", support & mechanic (photo from Matteo, media 10683), with the support crew after the second Marco
    i_ = max(i for i, (src, n, r) in enumerate(team) if n.upper().startswith('MARCO')) + 1
    team.insert(i_, (10683, 'ALESSIO "BONE"', 'Support & Mechanic'))
    # Matteo 16 Nov: first row Matteo, Amedeo, Marine, Piero, Alessio, Antonio, Giampietro 'JP'; Nicola and Jacopo move to the second row
    team = [(a, 'GIAMPIETRO "JP"' if b.upper().startswith('GIAMPIETRO') else b, c) for a, b, c in team]
    first = ['MATTEO', 'AMEDEO', 'MARINE', 'PIERO', 'ALESSIO', 'ANTONIO', 'GIAMPIETRO']
    key = lambda m: next((i for i, f in enumerate(first) if m[1].upper().startswith(f)), len(first))
    team = sorted(team, key=key)   # stable: the rest keep their live order
    def disp(n):   # live names are typed in capitals; the card shows them in capitals too (CSS), keep the words
        return n.replace("'", '’').replace('"', '“', 1).replace('"', '”', 1)
    th = ''.join(f'<div class="panel member">{img_tag(src, 600)}<div class="tx"><h3>{E(disp(n))}</h3><p>{E(r)}</p></div></div>' for src, n, r in team)
    ready_h = it[ready_i][1]
    ready_p = next(v for k, v, s in it[ready_i:op_i] if k == 'text')
    btn_t, btn_u = next(v for k, v, s in it[ready_i:op_i] if k == 'btn')
    hero_bg = next(v for k, v, s in it if k == 'bg')
    band_bg = 2650   # Matteo 15 Nov: the live "Why riders choose us" photo is a tilted shot; the About hero group photo instead
    matteo = next(src for src, n, r in team if n.upper().startswith('MATTEO'))
    # Matteo 16 Nov: the same cut-out photo and signature as on the other sites (the homepage "Our story" block)
    _MW = json.load(open(ROOT + 'stg-tours/media-webp.json'))
    SIGN = (f'<img class="signature" src="{_MW["signature"]["url"]}" alt="Matteo Cigala\'s signature" width="924" height="251">'
            '<p class="sig">Matteo Cigala<span>Tours Director</span></p>' + SIGN_JS)
    main = f'''<div class="hero plain-hero">
  <div class="in">
    <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / About</div>
    <div class="eyebrow">About Cigala Cycling Tours</div>
    <h1>{E(h1)}</h1>
    <div class="bar"></div>
  </div>
</div>
<section style="padding-top:44px">
  <div class="in story">
    <div class="panel prose" style="padding:clamp(22px,4vw,40px)">{story}{SIGN}</div>
    <div class="photo mcut"><img src="{_MW['matteo']['url']}" alt="{E(_MW['matteo']['alt'])}" loading="lazy"></div>
  </div>
</section>
<section>
  <div class="in">
    {head_block('The difference', it[why_i][1])}
    <div class="why6">{whyh}</div>
  </div>
</section>
<section>
  <div class="in">
    {head_block('Who rides with you', it[team_i][1])}
    <div class="team">{th}</div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      {img_tag(band_bg, 1600)}
      <div class="tx">
        <div class="eyebrow">Join us</div>
        <h2>{E(ready_h)}</h2>
        <div class="bar"></div>
        <div class="lede">{ready_p}</div>
        <div class="ctas"><a class="btn btn-go" href="{link(btn_u)}">{E(btn_t.capitalize())} →</a></div>
      </div>
    </div>
  </div>
</section>
{PARTNERS_H2}'''
    return {'id': 271, 'slug': 'about', 'main': main, 'css': PAGE_CSS, 'crumb': 'About'}


# ===================== Contact (461) =====================
# The live Elementor form stays (tools/tours_forms.py: Coaching style, sends to tours@): the push puts it where
# <!--FORM--> is, next to the info panel (push_tours_list.py, 'form': True).
sys.path.insert(0, ROOT + 'shared/social')
from social import social_row
IC_MAIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'
IC_PHONE = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M11 18h2"/></svg>'
IC_WA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20l1.3-3.8A8 8 0 1 1 8 19z"/><path d="M9 9.5c.5 2 2.5 4 4.5 4.5l1.2-1.2 2 1-.5 1.7c-3.5.3-7.5-3.7-7.2-7.2L10.7 8l1 2z"/></svg>'
IC_SOC = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="m8.2 10.8 7.6-4.6M8.2 13.2l7.6 4.6"/></svg>'
def contact():
    it = items(elementor(461))
    h1 = next(v for k, v, s in it if k == 'h1')
    h2s = [v for k, v, s in it if k == 'h2']          # '+353 404 78107', 'tours@cigalacycling.com', '+353 404 78107'
    h3s = [v for k, v, s in it if k == 'h3']          # 'EMAIL', 'PHONE', 'follow us online'
    phone, email = h2s[0], h2s[1]
    tel = 'tel:' + re.sub(r'[^+\d]', '', phone)
    hero_bg = next(v for k, v, s in it if k == 'bg')
    main = f'''<div class="hero phero">
  {img_tag(hero_bg, 2000, lazy=False)}
  <div class="in">
    <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / Contact</div>
    <div class="pill-eyebrow">Get in touch</div>
    <h1>{E(h1)}</h1>
    <div class="bar"></div>
    <div class="ctas"><a class="btn btn-go" href="https://wa.me/message/WVBRO6XAMQMCH1" target="_blank" rel="noopener">WhatsApp us →</a><a class="btn btn-ghost" href="mailto:{email}">Email us</a></div>
  </div>
</div>
<section style="padding-top:44px">
  <div class="in contact-grid">
<!--FORM-->
    <div class="panel cpanel info">
      <div class="row"><div class="ic">{IC_MAIL}</div><div><h3>{E(h3s[0])}</h3><h2><a href="mailto:{email}">{E(email)}</a></h2></div></div>
      <div class="row"><div class="ic">{IC_PHONE}</div><div><h3>{E(h3s[1])}</h3><h2><a href="{tel}">{E(h2s[2])}</a></h2></div></div>
      <div class="row"><div class="ic">{IC_WA}</div><div><h3>WhatsApp</h3><h2 class="wa"><a href="https://wa.me/message/WVBRO6XAMQMCH1" target="_blank" rel="noopener">Message us on WhatsApp</a></h2></div></div>
      <div class="row"><div class="ic">{IC_SOC}</div><div><h3>{E(h3s[2])}</h3></div></div>
      {social_row()}
    </div>
  </div>
</section>'''
    return {'id': 461, 'slug': 'contact', 'main': main, 'css': PAGE_CSS, 'crumb': 'Contact', 'form': True}


# ===================== Destinations hub (10) =====================
def home_block(word):
    """A block of the new homepage (already pushed with staging image URLs), e.g. the review cards."""
    els = json.loads(json.load(open(ROOT + 'stg-tours/out/page-5212.json'))['meta']['_elementor_data'])
    hs = []
    def walk(xs):
        for e in xs:
            if e.get('widgetType') == 'html': hs.append(e['settings']['html'])
            walk(e.get('elements', []))
    walk(els)
    return next(h for h in hs if word in h)

def reviews_block(h2):
    """The homepage review cards (stars, guest photos, Google + testimonials links) under this page's own live H2."""
    b = home_block('rv-links')
    b = re.sub(r'<h2>.*?</h2>', '<h2>' + E(h2) + '</h2>', b, count=1, flags=re.S)
    return b

def card_list(it, a, b):
    """Destination cards between two items: (name, url, background photo)."""
    out, bg, name = [], None, None
    for k, v, s in it[a:b]:
        if k == 'bg': bg = v
        elif k == 'h2' and 'VIEW DESTINATION' not in v.upper(): name = v.replace('\u200b', '').strip()
        elif k == 'h2':
            out.append((name, s.get('link', {}).get('url', ''), bg)); name = None
    return out

FIX_NAME = {'SWIZERLAND': 'SWITZERLAND'}   # typo on the live page
FIX_H1 = {'gran-canaria': 'Cycling in Gran Canaria'}   # live H1 said 'Cycling in Mallorca' (copied page)
FIX_URL = {'/destinations/belgium/': '/trips/tour-of-flanders-experience/'}   # live link is a 404: Belgium = the Flanders tour
# live Tuscany "Upcoming" cards link to the Lake Garda tours: send each card to the tour its title names (Matteo 15 Nov)
FIX_CARD_URL = {('tuscany', 'chianti & gran fondo strade bianche'): '/trips/chianti-gran-fondo-strade-bianche/',
                ('tuscany', 'tuscany epic | gravel'): '/trips/tuscany-epic-gravel/',
                ("tuscany", "italy's coast to coast"): '/trips/italys-coast-to-coast/'}
# photo keywords per destination, to fill gallery rows to 3 from the media library (Matteo 15 Nov: full rows on every page)
GAL_KW = {'italy': ['italy', 'italian', 'tuscany', 'dolomites', 'garda', 'como', 'stelvio', 'chianti'], 'france': ['france', 'french', 'alpe d', 'galibier', 'ventoux', 'pyrenees', 'corsica'],
          'spain': ['spain', 'spanish', 'mallorca', 'girona', 'calpe', 'costa blanca', 'tenerife', 'canaria', 'teide'],
          'girona': ['girona', 'catalonia'], 'slovenia': ['slovenia', 'bled', 'vrsic', 'soca'], 'french-alps': ['french alps', 'alpe d', 'galibier', 'izoard', 'france']}
# Matteo 16 Nov: the live Ireland cards reuse the Tuscany page's photos: Irish photos by card title
DEST_CARD_PHOTOS = {'ireland': {'wild atlantic way': 4938, 'wicklow mountains cycling escape': 6788, 'mizen head to malin head': 4939, 'wicklow gravel': 6787,
                                "giant's causeway & antrim coast": 1469, 'the burren & cliffs of moher': 1484},
                     'costa-blanca': {'sierra & sea gravel tour': 6403}}   # live used a Cyprus gravel photo
BAD_PHOTOS = {1414}   # labelled 'Cigala Cycling Tours Ireland' in the media library, but it is Tuscany
def gallery_extras(slug, name, need, used):
    kws = GAL_KW.get(slug, [name.lower()])
    out = []
    for x in json.load(open(ROOT + 'stg-tours/media-library.json')):
        w, h = int(x.get('width') or 0), int(x.get('height') or 0)
        if w < 1200 or h * 1.05 > w or 'webp' in x.get('mime_type', '') or not x.get('mime_type', '').startswith('image/'): continue
        txt = ((x.get('alt_text') or '') + ' ' + x['source_url'].rsplit('/', 1)[-1]).lower()
        if x['source_url'].lower().endswith('.png'): continue   # PNGs are designs/graphics, not photos
        if int(x['id']) in BAD_PHOTOS: continue
        if any(re.search(r'\b' + re.escape(k) + r's?\b', txt) for k in kws) and media(x['source_url'])['id'] not in used and 'logo' not in txt and 'map' not in txt:
            out.append(x['source_url'])
    return out[:need]

def destinations():
    it = items(elementor(10))
    h1 = next(v for k, v, s in it if k == 'h1')
    H = [(i, v) for i, (k, v, s) in enumerate(it) if k == 'h2']
    at = lambda w: next(i for i, v in H if w in text_of(v).upper())
    c_i, r_i, u_i, p_i, t_i = at('BY COUNTRY'), at('BY REGION'), at('ULTIMATE'), at('PRIVATE/CUSTOM'), at('TESTIMONIALS')
    intro = next(v for k, v, s in it[:c_i] if k == 'text')
    btns = [v for k, v, s in it[:c_i] if k == 'btn']
    hero_bg = 8604   # Matteo 15 Nov: not the homepage photo here; riders on a Dolomites pass
    def card(n, u, bg, big):
        path = FIX_URL.get(link(u).replace(L, ''), link(u).replace(L, ''))
        n = FIX_NAME.get(n, n)
        if big:
            return (f'<a class="dcard" href="{path}">{img_tag(bg, 900)}<div class="tx"><h2>{E(n.title() if n.isupper() else n)}</h2>'
                    f'<span class="go">View destination →</span></div></a>')
        return f'<a class="panel region" href="{path}"><h2>{E(n.title() if n.isupper() else n)}</h2><span>View →</span></a>'
    countries = ''.join(card(n, u, bg, True) for n, u, bg in card_list(it, c_i, r_i))
    regions = ''.join(card(n, u, bg, True) for n, u, bg in card_list(it, r_i, u_i))   # photo cards like the countries (Matteo 15 Nov)
    ult_p = next(v for k, v, s in it[u_i:p_i] if k == 'text')
    ult_btn = next(v for k, v, s in it[u_i:p_i] if k == 'btn')
    priv_btn = next(v for k, v, s in it[p_i:t_i] if k == 'btn')
    priv_bg = 8763   # Matteo 15 Nov: the live photo is low quality; a sharp group photo (Lake Como)
    ult_bg = 4900   # Matteo 15 Nov: not the live photo here; the Dolomites group photo
    title = lambda h: re.sub(r'<[^>]+>', '', h)
    def browse(h):   # live: 'Browse by <span style="color:#D64A4A">Country</span>' -> keep the words, red word as in the design eyebrow
        return E(title(h))
    main = f'''<div class="hero phero">
  {img_tag(hero_bg, 2000, lazy=False)}
  <div class="in">
    <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / Destinations</div>
    <div class="pill-eyebrow">Where we ride</div>
    <h1>{E(h1)}</h1>
    <div class="bar"></div>
    <div class="lede">{intro}</div>
    <div class="ctas"><a class="btn btn-go" href="#country">{E(btns[0][0].capitalize())}</a><a class="btn btn-ghost" href="#region">{E(btns[1][0].capitalize())}</a></div>
  </div>
</div>
<section id="country" style="padding-top:44px">
  <div class="in">
    {head_block('Countries', browse(it[c_i][1]))}
    <div class="dgrid">{countries}</div>
  </div>
</section>
<section id="region">
  <div class="in">
    {head_block('Regions', browse(it[r_i][1]))}
    <div class="dgrid">{regions}</div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band band-up">
      {img_tag(ult_bg, 1600)}
      <div class="tx">
        <div class="eyebrow">Every destination</div>
        <h2>{E(it[u_i][1])}</h2>
        <div class="bar"></div>
        <div class="lede">{ult_p}</div>
        <div class="ctas"><a class="btn btn-go" href="{link(ult_btn[1]).replace(L, '')}">{E(ult_btn[0].capitalize())} →</a></div>
      </div>
    </div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band band-up priv">
      {img_tag(priv_bg, 1600)}
      <div class="tx">
        <div class="eyebrow">Your dates, your group</div>
        <h2>{E(it[p_i][1])}</h2>
        <div class="bar"></div>
        <div class="ctas"><a class="btn btn-go" href="{link(priv_btn[1]).replace(L, '')}">{E(priv_btn[0].capitalize())} →</a></div>
      </div>
    </div>
  </div>
</section>
{reviews_block(it[t_i][1])}
{PARTNERS_H2}'''
    return {'id': 10, 'slug': 'destinations', 'main': main, 'css': PAGE_CSS, 'crumb': 'Destinations'}


# ===================== Destination pages (26, children of /destinations/) =====================
# One layout for all of them (design: tourspages/destination-lake-garda.html), filled in page order from each
# page's own Elementor data: hero (photo, H1, subtitle H2), then one section per live H2 with its text,
# photo gallery, facts (H3 + text) and tour cards (photo + tag + H2 + text + "View/Enquire tour" link).
# Body text that live sits in H4 headings becomes paragraphs (same words; H4 were not real headings).
DEST_IDS = json.load(open(ROOT + 'stg-tours/destination-ids.json'))
from tours_img import media
FACT_ICON = {
 'LOCATION': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',
 'CLIMATE': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/></svg>',
 'CUISINE': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3h8l-.5 6a3.5 3.5 0 0 1-7 0L8 3zM12 12.5V20M8.5 20.5h7"/></svg>',
 'TERRAIN': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 19.5 9 8l4 6.5 2.5-3.5 6 8.5z"/></svg>'}
FACT_ICON_DEFAULT = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 8v4.5M12 15.5v.5"/></svg>'

def para_html(v):
    """Live H4/text-editor content -> paragraphs with the same words (links and line breaks kept)."""
    v = clean(v)
    if v.startswith('<p') or v.startswith('<ul') or v.startswith('<ol'): return v
    v = re.sub(r'\s*<br\s*/?>\s*', '<br>', v.strip())
    parts = [x.strip() for x in re.split(r'\n\s*\n|\n', v) if x.strip()]
    return ''.join(f'<p>{x}</p>' for x in parts)

def is_go(v, s):   # the "View Tour →", "Enquire Tour →", "View Destination→" headings that only carry a link
    return '→' in v and isinstance(s.get('link'), dict) and s['link'].get('url') and len(text_of(v)) < 30


# homepage tour cards (Matteo 15 Nov: the upcoming tours on destination pages = the homepage cards)
def home_cards():
    els = json.loads(json.load(open(ROOT + 'stg-tours/out/page-5212.json'))['meta']['_elementor_data'])
    hs = []
    def walk(xs):
        for e in xs:
            if e.get('widgetType') == 'html': hs.append(e['settings']['html'])
            walk(e.get('elements', []))
    walk(els)
    blob = ''.join(hs)
    return {re.search(r'/trips/([^"/]+)/?"', m.group(0)).group(1): m.group(0) for m in re.finditer(r'<a class="tour".*?</a>', blob, re.S)}
HOME_CARDS = home_cards()
DEST_CC = {'it': 'italy tuscany lake-como lake-garda alps-dolomites puglia sardinia sicily', 'es': 'spain mallorca costa-blanca gran-canaria tenerife girona',
           'fr': 'france french-alps pyrenees corsica', 'pt': 'portugal algarve', 'si': 'slovenia', 'cy': 'cyprus', 'be': 'belgium', 'hr': 'croatia',
           'gr': 'greece', 'ie': 'ireland', 'ch': 'switzerland'}
DEST_CC = {d: cc for cc, ds in DEST_CC.items() for d in ds.split()}
CC_NAME = {'it': 'Italy', 'es': 'Spain', 'fr': 'France', 'pt': 'Portugal', 'si': 'Slovenia', 'cy': 'Cyprus', 'be': 'Belgium', 'hr': 'Croatia', 'gr': 'Greece', 'ie': 'Ireland', 'ch': 'Switzerland'}
def dflag(slug):   # the country flag, top right, on every tour card of a destination page, like the tour lists (Matteo 16 Nov)
    cc = DEST_CC.get(slug)
    return f'<img class="flag" src="img/flag-{cc}.webp" alt="Flag of {CC_NAME[cc]}" width="40" height="30">' if cc else ''
KNAME = {'road': 'Road', 'gf': 'Gran Fondo', 'gravel': 'Gravel'}
def chips(cards):
    """Filter chips (All / Road / Gran Fondo / Gravel) when a section mixes tour types (Matteo 15 Nov). JS: FILTER_JS."""
    ks = [k for k in ('road', 'gf', 'gravel') if f'data-k="{k}"' in cards]
    if len(ks) < 2: return ''
    b = '<button type="button" class="fchip on" data-f="all"><span class="fd"></span>All</button>'
    b += ''.join(f'<button type="button" class="fchip" data-f="{k}"><span class="fd"></span>{KNAME[k]}</button>' for k in ks)
    return f'<div class="fchips" role="group" aria-label="Filter by tour type">{b}</div>'
FILTER_JS = """<script>(function(){document.querySelectorAll('.fchips').forEach(function(g){var grid=g.nextElementSibling;g.querySelectorAll('.fchip').forEach(function(b){b.addEventListener('click',function(){
g.querySelectorAll('.fchip').forEach(function(x){x.classList.toggle('on',x===b);x.setAttribute('aria-pressed',x===b);});var f=b.dataset.f;
[].forEach.call(grid.children,function(c){c.hidden=!(f==='all'||c.dataset.k===f||(f==='road'&&c.dataset.k==='gf')||c.dataset.k==='all');});});});});})();</script>"""

LIST_BAND = re.search(r'<div class="band">.*?</div>\s*</div>\s*(?=</div>\s*</section>)', json.loads(open(ROOT + 'stg-tours/out/list-trips.json').read())['main'], re.S).group(0)

def destination(slug):
    pid = DEST_IDS[slug]
    it = [x for x in items(elementor(pid)) if x[0] not in ('open', 'close', 'divider', 'spacer')]
    h1i = next(i for i, x in enumerate(it) if x[0] == 'h1')
    h1 = FIX_H1.get(slug, it[h1i][1])
    name = re.sub(r'^(cycling in( the)?)\s+', '', text_of(h1), flags=re.I).strip()
    name = name.title() if name.isupper() or name.islower() or name == name.capitalize() else name
    hero_bg = next(v for k, v, s in it if k == 'bg')
    used = {media(hero_bg)['id']} | set(DEST_CARD_PHOTOS.get(slug, {}).values())   # Matteo 15 Nov: never the same photo twice on one page (card photos reserved)
    spare = [v for k, v, s in it if k == 'img' and (media(v).get('width') or 0) >= 900]
    def pick(x):
        mid = media(x)['id']
        if mid not in used: used.add(mid); return x
        for y in spare:
            if media(y)['id'] not in used: used.add(media(y)['id']); return y
        return x
    rest = it[h1i + 1:]
    sub = None
    if len(rest) > 1 and rest[0][0] == 'h2' and rest[1][0] in ('h2',) and not is_go(*rest[0][1:]):
        sub = rest[0][1]; rest = rest[1:]
    sections, cur = [], {'h2': None, 'blocks': []}
    def add(kind, val):
        b = cur['blocks']
        if b and b[-1][0] == kind and kind in ('p', 'gal', 'facts', 'cards'): b[-1][1].append(val)
        else: b.append((kind, [val]))
    i = 0
    while i < len(rest):
        k, v, s = rest[i]
        if k == 'bg':
            j = i + 1   # a card: background photo, then (tag button), H2 title, text, and a "→" H2 link, before the next photo
            while j < len(rest) and rest[j][0] != 'bg' and not (rest[j][0] == 'h2' and is_go(rest[j][1], rest[j][2])): j += 1
            if j < len(rest) and rest[j][0] == 'h2' and is_go(rest[j][1], rest[j][2]):
                seg = rest[i + 1:j]
                tag = next((bv[0] for bk, bv, bs in seg if bk == 'btn' and not bv[1]), '')
                title = next((hv for hk, hv, hs in seg if hk == 'h2'), '')
                desc = ''.join(para_html(tv) for tk, tv, ts in seg if tk in ('text', 'h4', 'h3'))
                imgs = [iv for ik, iv, _ in seg if ik == 'img']
                add('cards', {'bg': v, 'tag': tag, 'title': title, 'desc': desc, 'go': text_of(rest[j][1]).replace('\u200b', ''), 'url': rest[j][2]['link']['url']})
                i = j + 1; continue
            i += 1; continue
        if k == 'h2' and is_go(v, s): i += 1; continue
        if k == 'h2':
            if cur['h2'] or cur['blocks']: sections.append(cur)
            cur = {'h2': v, 'blocks': []}; i += 1; continue
        if k == 'h3' and i + 1 < len(rest) and rest[i + 1][0] in ('h4', 'text'):
            add('facts', (text_of(v), para_html(rest[i + 1][1]))); i += 2; continue
        if k in ('h4', 'h5', 'h6', 'text', 'h3'):
            if 'perfect one' in text_of(v).lower():
                btn = next((x for x in rest[i + 1:i + 3] if x[0] == 'btn'), None)
                add('band', (para_html(v), btn[1] if btn else ('Learn more', L + '/trips/private-trips/')))
                i += 2 if btn else 1; continue
            add('p', para_html(v)); i += 1; continue
        if k == 'img':
            m = media(v)
            if (m.get('width') or 0) >= 300: add('gal', v)
            i += 1; continue
        if k == 'btn' and v[1]:
            add('btn', v); i += 1; continue
        i += 1
    sections.append(cur)
    # Matteo 16 Nov: two "Why ...?" sections in a row (Ireland: "Why Ireland?" + "Why ride Ireland?") -> one section, two lists side by side
    for n_ in range(len(sections) - 1, 0, -1):
        a_, b_ = sections[n_ - 1], sections[n_]
        if a_['h2'] and b_['h2'] and text_of(a_['h2']).strip().upper().startswith('WHY') and text_of(b_['h2']).strip().upper().startswith('WHY'):
            pa = [v for k, v in a_['blocks'] if k == 'p']; pb = [v for k, v in b_['blocks'] if k == 'p']
            rest = [x for x in a_['blocks'] if x[0] != 'p'] + [x for x in b_['blocks'] if x[0] != 'p']
            two = ('<div class="why2"><div class="panel"><h3>Why riders love it</h3>' + ''.join(sum(pa, [])) + '</div>'
                   '<div class="panel"><h3>Highlights</h3>' + ''.join(sum(pb, [])) + '</div></div>')
            sections[n_ - 1:n_ + 1] = [{'h2': b_['h2'], 'blocks': [('raw', [two])] + rest}]

    def eyebrow(h):
        t = text_of(h).upper()
        if 'FACT' in t: return 'Good to know'
        if 'UPCOMING' in t: return '2027 season'
        if 'CUSTOM' in t: return 'Custom tours'
        if 'REGION' in t or 'DESTINATION' in t: return 'Where to ride'
        return name
    def render_block(kind, vals):
        if kind == 'p': return f'<div class="prose dprose">{"".join(vals)}</div>'
        if kind == 'raw': return ''.join(vals)
        if kind == 'gal':
            seen = []
            for x in vals:
                if media(x)['id'] not in used: used.add(media(x)['id']); seen.append(x)
            if not seen: return ''
            if len(seen) % 3:
                extra = gallery_extras(slug, name, 3 - len(seen) % 3, used)
                for x in extra: used.add(media(x)['id']); seen.append(x); print('  + gallery', slug, media(x)['id'], (media(x).get('alt_text') or '')[:70], x.rsplit('/', 1)[-1][:50])
                if len(seen) % 3 and len(seen) > 3: seen = seen[:len(seen) - len(seen) % 3]   # no photo left to fill the row: full rows only
                elif len(seen) % 3: print('  !! gallery not full', slug, len(seen))
            return f'<div class="gal3">{"".join(img_tag(x, 1200, alt=f"Cycling in {name} - Cigala Cycling Tours") for x in seen)}</div>'
        if kind == 'facts':
            return '<div class="facts4">' + ''.join(
                f'<div class="panel fact"><div class="ic">{FACT_ICON.get(t.upper().strip(), FACT_ICON_DEFAULT)}</div><div><h3>{E(t.title())}</h3>{p}</div></div>'
                for t, p in vals) + '</div>'
        if kind == 'cards':
            out = []
            for c in vals:
                u = link(c['url']).replace(L, '')
                u = FIX_URL.get(u, u)
                u = FIX_CARD_URL.get((slug, re.sub(r'<[^>]+>', '', c['title']).replace('\u200b', '').strip().lower()), u)
                tag = c['tag'].title() if c['tag'] else ''
                title = re.sub(r'<[^>]+>', '', c['title']).replace('\u200b', '').strip()
                tags = f'<span class="tags"><span class="tag{" gravel" if tag == "Gravel" else ""}">{E(tag)}</span></span>' if tag else ''
                title = re.sub(r'<[^>]+>', '', c['title']).replace('\u200b', '').strip()
                go = c['go'].replace('→', '').strip().capitalize() + ' →'
                desc = re.sub(r'<p>(\s|&nbsp;|\u200b|<br\s*/?>)*</p>', '', c['desc'])
                if 'nquire' in c['go']: u = '/trips/private-trips/'   # an Enquire card is a custom tour: never another tour's page (live Madeira linked to Cyprus)
                hm = re.match(r'^/trips/([^/]+)/?$', u)
                if hm and hm.group(1) in HOME_CARDS and hm.group(1) != 'private-trips':
                    out.append(('home', HOME_CARDS[hm.group(1)])); continue
                out.append(('card', f'<article class="tcard dtour" data-k="{ {"Gravel": "gravel", "Gran Fondo": "gf", "Road & Gran Fondo": "gf"}.get(tag, "road") }"><a class="ph" href="{u}">{img_tag(DEST_CARD_PHOTOS.get(slug, {}).get(html.unescape(title).lower()) or pick(c["bg"]), 900, alt=f"{title} - {name} cycling tour")}{tags}{dflag(slug)}</a><div class="tx">'
                           f'<h2>{E(title)}</h2><div class="desc">{desc}</div><div class="ctas one"><a class="btn btn-go" href="{u}">{E(go)}</a></div></div></article>'))
            if out and all(k == 'home' for k, _ in out):
                return '<!--HOMECARDS-->' + ''.join(h for k, h in out)
            grid = ''.join(h for k, h in out)
            if len(out) % 3 and any('Enquire' in c['go'] for c in vals):   # fill the last row on laptops (Matteo 15 Nov)
                grid += ('<article class="tcard dcta" data-k="all"><div class="tx"><div class="eyebrow">Your dates, your group</div>'
                         '<p class="ctat">Build your own tour</p><div class="bar"></div><p>Tell us where, when and how hard you want to ride: '
                         'we plan the routes, hotels, support and every detail.</p><div class="ctas one"><a class="btn btn-go" href="/trips/private-trips/">'
                         'Plan your custom tour →</a></div></div></article>')
            return chips(grid) + f'<div class="tgrid">{grid}</div>'
        if kind == 'btn':
            return '<div class="ctas">' + ''.join(f'<a class="btn btn-go" href="{link(u).replace(L, "")}">{E(t.capitalize())} →</a>' for t, u in vals) + '</div>'
        if kind == 'band':   # the same "Can't find the perfect one?" band as at the bottom of All tours (Matteo 15 Nov)
            return '<div class="dband">' + LIST_BAND + '</div>'
        return ''
    html_s = []
    cmap_done = False
    for n, sec in enumerate(sections):
        body = ''.join(render_block(k, v) for k, v in sec['blocks'])
        if not body and not sec['h2']: continue
        head = head_block(eyebrow(sec['h2']), re.sub(r'<[^>]+>', '', sec['h2']).replace('\u200b', '').strip()) if sec['h2'] else ''
        sid = ' id="tours"' if sec['h2'] and 'UPCOMING' in text_of(sec['h2']).upper() else ''
        if '<!--HOMECARDS-->' in body:   # upcoming tours: the homepage cards (homepage CSS, .cc)
            lede = ''.join(re.findall(r'<p>.*?</p>', body.split('<!--HOMECARDS-->')[0], re.S))
            cards = body.split('<!--HOMECARDS-->', 1)[1]
            h2t = re.sub(r'<[^>]+>', '', sec['h2']).replace('\u200b', '').strip() if sec['h2'] else 'Upcoming tours'
            html_s.append(f'<div class="cc cc-page"><section id="tours" class="dtours"><div class="in"><div class="head"><div><div class="eyebrow">2027 season</div>'
                          f'<h2>{E(h2t)}</h2><div class="bar"></div>{lede.replace("<p>", "<p class=lede>")}</div></div>{chips(cards)}<div class="tours">{cards}</div></div></section></div>')
            continue
        if not cmap_done and body.startswith('<div class="prose dprose">') and os.path.exists(ROOT + f'tourspages/maps/country-{slug}.svg'):
            cmap = open(ROOT + f'tourspages/maps/country-{slug}.svg').read()   # beside the heading and the first text (Matteo 15 Nov)
            k = body.index('</div>') + len('</div>')
            body = f'<div class="dsplit"><div>{head}{body[:k]}</div><div class="cmapbox">{cmap}</div></div>' + body[k:]
            head = ''
            cmap_done = True
        html_s.append(f'<section{sid}{" style=\"padding-top:44px\"" if n == 0 else ""}>\n  <div class="in">\n    {head}\n    {body}\n  </div>\n</section>')
    has_tours = any('id="tours"' in x for x in html_s)
    sub_html = f'<h2 class="pill-eyebrow hero-sub">{E(re.sub(r"<[^>]+>", "", sub).strip())}</h2>' if sub else '<div class="pill-eyebrow">Destination</div>'
    main = f'''<div class="hero phero dhero">
  {img_tag(hero_bg, 2000, alt=f'Cycling in {name} - Cigala Cycling Tours', lazy=False)}
  <div class="in">
    <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / <a href="{L}/destinations/" {EXT}>Destinations</a> / {E(name)}</div>
    {sub_html}
    <h1>{E(h1)}</h1>
    <div class="bar"></div>
    <div class="ctas">{f'<a class="btn btn-go" href="#tours">Upcoming tours →</a>' if has_tours else f'<a class="btn btn-go" href="{L}/trips/">Upcoming tours →</a>'}<a class="btn btn-ghost" href="{L}/trips/private-trips/">Custom tours</a></div>
  </div>
</div>
''' + '\n'.join(html_s) + '\n' + READMORE_JS
    return {'id': pid, 'slug': slug, 'main': main, 'css': PAGE_CSS, 'crumb': name}

READMORE_JS = FILTER_JS


# ===================== Testimonials (2844) =====================
# Live: the testimonials H2 + an old reviews widget, then 23 YouTube videos, each with H2 name + H2 country.
# New: an H1 (live has none), our review cards under the live H2, then the videos as click-to-play cards:
# a still picture and a play button; the YouTube player (youtube-nocookie) loads only when clicked.
YT_JS = """<script>(function(){document.querySelectorAll('.cl .yt').forEach(function(b){b.addEventListener('click',function(){
var f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+b.dataset.id+'?autoplay=1&rel=0';
f.title=b.getAttribute('aria-label');f.allow='accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; fullscreen';f.allowFullscreen=true;
b.replaceWith(f);});});})();</script>"""
def testimonials():
    it = [x for x in items(elementor(2844)) if x[0] not in ('open', 'close', 'divider', 'spacer')]
    h2_top = next(v for k, v, s in it if k == 'h2')
    vids, i = [], 0
    while i < len(it):
        k, v, s = it[i]
        m = re.search(r'youtube\.com/embed/([\w-]+)', s.get('html', '') or '') if k == 'html' else None
        if m:
            hs = [x[1] for x in it[i + 1:i + 3] if x[0] == 'h2']
            vids.append((m.group(1), text_of(hs[0]) if hs else '', text_of(hs[1]) if len(hs) > 1 else ''))
        i += 1
    cards = ''.join(
        f'<figure class="panel vcard"><button type="button" class="yt" data-id="{vid}" aria-label="Play {E(n)}\'s video review">'
        f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="{E(n)} from {E(c)} talks about riding with Cigala Cycling Tours" loading="lazy">'
        f'<span class="play" aria-hidden="true"></span></button><figcaption><h2>{E(n)}</h2><span>{E(c)}</span></figcaption></figure>'
        for vid, n, c in vids)
    main = f'''<div class="hero phero">
  {img_tag(4893, 2000, lazy=False)}
  <div class="in">
    <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / Testimonials</div>
    <div class="pill-eyebrow">What our riders say</div>
    <h1>Testimonials</h1>
    <div class="bar"></div>
  </div>
</div>
{reviews_block(h2_top).replace('<section', '<section style="padding-top:44px"', 1)}
<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">On video</div><p class="band-title">Hear it from our guests</p><div class="bar"></div></div></div>
    <div class="vgrid">{cards}</div>
    <div class="ctas vmore-wrap"><button type="button" class="btn btn-go vmore">Show all {len(vids)} videos</button></div>
  </div>
</section>
{PARTNERS_H2}
{YT_JS}
<script>(function(){{var g=document.querySelector('.cl .vgrid'),b=document.querySelector('.cl .vmore');if(!g||!b)return;g.classList.add('few');b.addEventListener('click',function(){{g.classList.remove('few');b.parentNode.remove();}});}})();</script>'''
    return {'id': 2844, 'slug': 'testimonials', 'main': main, 'css': PAGE_CSS, 'crumb': 'Testimonials', 'videos': len(vids)}


# ===================== Custom tours (1576, /trips/private-trips/) =====================
H3_FIX = {'REASTURANTS': 'RESTAURANTS', 'OFF THE BIKE ACTIVITES': 'OFF THE BIKE ACTIVITIES'}   # typos on the live page
ORG_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12.5 4.2 4.2L19 7"/></svg>'
ORG_ICONS = {   # What we organise: one line icon per item (Matteo 15 Nov)
 'ACCOMMODATION': '<path d="M3 18V7M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5"/><circle cx="7" cy="11" r="2"/>',
 'TECHNICAL ASSISTANCE': '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3.5 17.5l3 3 5.8-5.8a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
 'GUIDING': '<path d="M5 21V4M5 4h12l-2.5 4L17 12H5"/>',
 'BIKE RENTAL': '<circle cx="6" cy="16" r="3.5"/><circle cx="18" cy="16" r="3.5"/><path d="M6 16l4-8h5l3 8M10 8l3.5 8M9 5h3"/>',
 'TRANSFERS': '<path d="M3 16V8a1 1 0 0 1 1-1h11l4 4h1a1 1 0 0 1 1 1v4H3z"/><circle cx="7.5" cy="16.5" r="1.8"/><circle cx="16.5" cy="16.5" r="1.8"/><path d="M15 7v4h4"/>',
 'RESTAURANTS': '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M16 21V3c-2 1.5-3 4-3 7v3h3"/>',
 'OFF THE BIKE ACTIVITIES': '<path d="M4 8h3l1.5-2h7L17 8h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
 'CUSTOM KIT': '<path d="M8 4 4 6.5 5.5 10 7 9.5V20h10V9.5l1.5.5L20 6.5 16 4c-.7 1.6-2.2 2.5-4 2.5S8.7 5.6 8 4z"/>'}
def custom():
    it = [x for x in items(elementor(1576)) if x[0] not in ('open', 'close', 'divider', 'spacer')]
    idx = lambda k_, w=None: next(i for i, (k, v, s) in enumerate(it) if k == k_ and (w is None or w in text_of(v).upper()))
    h1 = it[idx('h1')][1]
    intro = next(v for k, v, s in it if k == 'text')
    b_i, o_i, l_i, f_i, g_i = idx('h2', 'BUILD YOUR'), idx('h2', 'ORGANISE'), idx('h2', 'LOCATIONS'), idx('h2', 'FAQ'), idx('h3', 'GET IN TOUCH')
    asks = [v for k, v, s in it[:b_i] if k == 'h3']
    org = [H3_FIX.get(v.strip(), v.strip()) for k, v, s in it[o_i:l_i] if k == 'h3']
    loc_txt = [v for k, v, s in it[l_i:f_i] if k == 'text']
    faq, i = [], f_i + 1
    while i < g_i:
        if it[i][0] == 'h3' and it[i + 1][0] == 'text': faq.append((it[i][1], it[i + 1][1])); i += 2
        else: i += 1
    contact_txt = [v for k, v, s in it[g_i:] if k == 'text']
    hero_bg = it[0][1]; build_bg = 4440   # Matteo 15 Nov: the live photo here is low quality
    photo = next(v for k, v, s in it[f_i:g_i] if k == 'img')
    btn = it[b_i + 1][1][0] if it[b_i + 1][0] == 'btn' else 'Customise your tour'
    ask_html = ''.join(f'<div class="panel step"><span class="n">{n:02d}</span><h3>{E(text_of(a))}</h3></div>' for n, a in enumerate(asks, 1))
    org_html = ''.join(f'<div class="panel org"><span class="oic" aria-hidden="true"><svg viewBox="0 0 24 24">{ORG_ICONS.get(fix_text(o).strip().upper(), "<path d=\'m5 12.5 4.2 4.2L19 7\'/>")}</svg></span><h3>{E(o.title())}</h3></div>' for o in org)
    locs = re.findall(r'<li>(.*?)</li>', loc_txt[1], re.S)
    locs = [x.replace(chr(0x200b), '').strip() for x in locs if 'Patagonia' not in x]   # Europe map (Matteo 15 Nov)
    locs += ['Ireland', 'Provence, France', 'Switzerland']   # added by Matteo 15 Nov (same order as the map, tools/tours_route_maps.py)
    lmap = open(ROOT + 'tourspages/maps/custom-locations.svg').read()
    # Matteo 16 Nov: a livelier map: the numbered dots pop in one by one, and the list and the dots highlight each other
    lmap = re.sub(r'<g>(<circle[^>]*/><text[^>]*>(\d+)</text>)</g>', lambda m_: f'<g class="ld" data-n="{m_.group(2)}" style="--i:{m_.group(2)}">{m_.group(1)}</g>', lmap)
    lmap = lmap.replace('<svg class="lmap"', '<svg class="lmap dyn-l"', 1)
    loc_html = ('<div class="locwrap"><div class="lmapbox">' + lmap + '</div><ol class="locs loclist">' +
                ''.join(f'<li data-n="{i}" tabindex="0"><span class="n">{i}</span>{x}</li>' for i, x in enumerate(locs, 1)) + '</ol></div>' + LOC_JS)
    faq_html = ''.join(f'<details class="panel faq"><summary><h3>{E(q)}</h3></summary><div class="a">{a}</div></details>' for q, a in faq)
    tel = '+35340478107'
    main = f'''<div class="hero phero">
  {img_tag(1632, 2000, lazy=False)}
  <div class="in">
    <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / <a href="{L}/trips/" {EXT}>Bike tours</a> / Custom tours</div>
    <div class="pill-eyebrow">Private &amp; tailor-made</div>
    <h1>{E(h1)}</h1>
    <div class="bar"></div>
    <div class="lede">{intro}</div>
    <div class="ctas"><a class="btn btn-go" href="#enquire">{E(btn.capitalize())} →</a></div>
  </div>
</div>
<section style="padding-top:44px">
  <div class="in">
    <div class="head"><div><div class="eyebrow">Tell us</div><p class="band-title">Four questions to start</p><div class="bar"></div></div></div>
    <div class="steps4">{ask_html}</div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      {img_tag(build_bg, 1600, alt='Riders on a Cigala Cycling custom tour')}
      <div class="tx">
        <div class="eyebrow">Your dates, your group</div>
        <h2>{E(it[b_i][1])}</h2>
        <div class="bar"></div>
        <div class="ctas"><a class="btn btn-go" href="#enquire">{E(btn.capitalize())} →</a></div>
      </div>
    </div>
  </div>
</section>
<section>
  <div class="in">
    {head_block('Fully organised', it[o_i][1])}
    <div class="org4">{org_html}</div>
  </div>
</section>
<section>
  <div class="in">
    {head_block('Where to', it[l_i][1])}
    <div class="prose dprose">{loc_txt[0]}</div>
    {loc_html}
  </div>
</section>
<section>
  <div class="in">
    {head_block('Good to know', it[f_i][1])}
    <div class="faqs">{faq_html}</div>
  </div>
</section>
<section id="enquire">
  <div class="in contact-grid">
<!--FORM-->
    <div class="panel cpanel info">
      {img_tag(photo, 1100, cls='cphoto')}
      <h3 class="gt">{E(it[g_i][1])}</h3>
      {''.join(c for c in contact_txt if 'call us' not in c.lower())}
      <p>Alternatively, message us on WhatsApp.</p>
      <div class="ctas"><a class="btn btn-go" href="https://wa.me/message/WVBRO6XAMQMCH1" target="_blank" rel="noopener">WhatsApp us →</a></div>
    </div>
  </div>
</section>'''
    xp_ = exit_pop('Planning a tour of your own?', 'Tell us where, when and how you like to ride: we will put together a first idea for your group, free and with no commitment.', ('Send us your idea', '#enquire'))
    main = main.replace('<section id="enquire">', xp_ + '\n<section id="enquire">', 1)   # the exit pop-up (before the form block: the push keeps the form last)
    return {'id': 1576, 'slug': 'private-trips', 'main': main, 'css': PAGE_CSS, 'crumb': 'Custom tours', 'form': True}


# Spelling mistakes on the live pages (Matteo 15 Nov: "any error you see, fix it"). Visible text only, never links.
TYPOS = [(r'(?<=\w) +,(?=\s)', ','),   # Matteo 16 Nov: FAQ and page typos
         ('\\breasturants\\b', 'restaurants'), ('\\b(S|s)pectaculars days\\b', '\\1pectacular days'), ('\\bstay shorter then\\b', 'stay shorter than'), ('\\bLong ruote\\b', 'Long route'), ('\\bLake Gravel Garda\\b', 'Lake Garda Gravel'), ('\\bjoin also join\\b', 'also join'), ('\\bjust let your guide during\\b', 'just let your guide know during'), ('\\bEach days have\\b', 'Each day has'), ('\\bparticipate to this tour\\b', 'participate in this tour'), ('\\bone of the best month to\\b', 'one of the best months to'), ('\\bmaking idea for\\b', 'making it ideal for'), ('\\bin advanced\\b', 'in advance'), ('\\bGran Fondo is Guaranteed\\b', 'Gran Fondo is guaranteed'), ("\\byou might don't need it\\b", 'you might not need it'), ('\\bsince is early season and you can expect the frequent showers\\b', "since it's early season and showers are frequent"), ('\\bsince is early season\\b', "since it's early season"), ('\\bIs best a road or a gravel bike for this tour\\?', 'Is a road or a gravel bike best for this tour?'), ('\\bis a good idea to put some training for it and arrive with some good level of preparation\\b', "it's a good idea to do some training and arrive well prepared"), ("If you're planning to be a serious and enjoying the climbs and arrive in the evening a little fresher a bit of training preparation is recommended\\.", 'If you want to enjoy the climbs and arrive each evening a little fresher, some training beforehand is recommended.'), ('\\bIs there an option also for a E-', 'Is there also an option for an E-'), ('\\bex pro staffs\\b', 'ex-pro staff'), ('\\bDay 8 - San Pellegrino\\b', 'Day 5 - San Pellegrino'), ('Ride like a hero/', 'Ride like a hero.'), (r'\breland enjoys', 'Ireland enjoys'),   # no space before a comma (Matteo 16 Nov: 'RIDE INTO THE LEGEND , TAKE PART')
         (r'\bMechnical\b', 'Mechanical'), (r'\bmechnical\b', 'mechanical'), (r'\bDurace\b', 'Dura-Ace'), (r'\bACCOMODATION', 'ACCOMMODATION'),
         (r'\bAccomodation\b', 'Accommodation'), (r'\baccomodation\b', 'accommodation'), (r'\baccomodate\b', 'accommodate'), (r'\bCOFFE\b', 'COFFEE'),
         (r'\bAlantejo\b', 'Alentejo'), (r'\bMarocco\b', 'Morocco'), (r'\brecipies\b', 'recipes'), (r'\bcusine\b', 'cuisine'), (r'\bTentino\b', 'Trentino'),
         (r'\blagguages\b', 'luggage'), (r'\bsuitcaseses\b', 'suitcases'), (r'\bwinfe\b', 'wine'), (r'\bprive viewing\b', 'private viewing'),
         (r'\bpreparatio\.', 'preparation.'), (r'\bFframeset\b', 'Frameset'), (r'\bClimate reland\b', 'Climate Ireland'), (r'\bGiminiano\b', 'Gimignano'),
         (r'\bNova Goricia\b', 'Nova Gorica'), (r'\bWashing maching\b', 'Washing machine'), (r'\bBarcellonette\b', 'Barcelonnette'),
         (r'\bGrossetto\b', 'Grosseto'), (r'\bpenisula\b', 'peninsula'), (r'\bcontryside\b', 'countryside'), (r'TÉLÉGRAPHIE', 'TÉLÉGRAPHE'),
         (r'\bCrostine\b', 'Crostini'), (r'\bREASTURANTS\b', 'RESTAURANTS'), (r'\bACTIVITES\b', 'ACTIVITIES'), (r'\bSWIZERLAND\b', 'SWITZERLAND'),
         (r'\bBOOOK\b', 'BOOK'), (r'\bPEFORMANCE\b', 'PERFORMANCE'), (r'\bBaleares Islands\b', 'Balearic Islands'), (r'\bEUROPE NEWEST\b', "EUROPE'S NEWEST")]
def fix_text(h):
    parts = re.split(r'(<[^>]+>)', h)
    out = []
    for x in parts:
        if not x.startswith('<'):
            for a, b in TYPOS: x = re.sub(a, b, x)
        elif ' alt="' in x:   # image alt text too
            def _alt(m):
                v = m.group(1)
                for a, b in TYPOS: v = re.sub(a, b, v)
                return f' alt="{v}"'
            x = re.sub(r' alt="([^"]*)"', _alt, x)
        out.append(x)
    h = ''.join(out)
    return re.sub(r'<p>\s*harmony\.\s*</p>', '', h)   # an editing leftover on the Dolomites page

# small additions on top of the design CSS, scoped to .cl by the kit build
PAGE_CSS = '''
html .cl .band .lede p { margin: 0; }
html .cl .member h3 { text-transform: uppercase; }
html .cl .hero-phone { font-family: var(--body); font-size: 20px; font-weight: 600; letter-spacing: .02em; margin-top: 18px; }
html .cl .hero-phone a, html .cl .info h2 a { color: var(--text); text-decoration: none; }
html .cl .hero-phone a:hover, html .cl .info h2 a:hover { color: var(--green-text); }
html .cl .info h3 { font-family: var(--body); font-size: 12px; font-weight: 600; letter-spacing: .1em; color: var(--text-3); margin: 0 0 2px; }
html .cl .info h2 { font-family: var(--body); font-size: 17px; font-weight: 600; letter-spacing: 0; text-transform: none; color: var(--text); overflow-wrap: anywhere; }
html .cl .info .cc-social { margin-top: 2px; margin-left: 48px !important; }   /* icons start under the text column (Matteo 16 Nov) */
.e-con.cl-contact { display: grid !important; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 16px !important; align-items: start; max-width: 1232px !important; margin: 0 auto !important; padding: 44px 16px 0 !important; }   /* the same gap under the hero as every page (Matteo 16 Nov) */
.e-con.cl-contact > .elementor-widget-form { margin: 0 !important; width: 100% !important; max-width: 100% !important; --container-widget-width: 100% !important; }
.e-con.cl-contact > .elementor-widget-form .cc-form, .e-con.cl-contact .elementor-widget-form.cc-form { margin-top: 0 !important; }
@media (max-width: 900px) { .e-con.cl-contact { grid-template-columns: minmax(0, 1fr); } }
html .cl .dcard h2 { font-size: clamp(22px, 2.2vw, 28px); }
html .cl .region h2 { font-size: 18px; }
html .cl .band .lede p { margin: 0; }
html .cl h2.hero-sub { font-family: var(--body); font-size: 12px; line-height: 1.4; font-weight: 600; letter-spacing: .14em; color: var(--text); margin: 0 0 18px; }
html .cl .dprose { max-width: 78ch; }
html .cl .dprose p { margin: 0 0 14px; color: var(--text-2); }
html .cl .dprose + .gal3, html .cl .gal3 + .dprose, html .cl .facts4 + .dprose, html .cl .dprose + .facts4, html .cl .dprose + .tgrid, html .cl .tgrid + .dprose, html .cl .gal3 + .facts4 { margin-top: 22px; }
html .cl .fact p { margin: 6px 0 0; }
html .cl .dtour .desc p { margin: 0 0 8px; font-size: 14px; color: var(--text-2); line-height: 1.55; }
html .cl .dtour .ctas.one { grid-template-columns: minmax(0, 1fr); }
html .cl .band .lede p { margin: 0; }
html .cl .vgrid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
@media (max-width: 1000px) { html .cl .vgrid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) { html .cl .vgrid { grid-template-columns: minmax(0, 1fr); } }
html .cl .story .photo.mcut { background: none; border: 0; border-radius: 0; overflow: visible; aspect-ratio: auto !important; position: relative; display: flex; justify-content: center; align-items: flex-end; isolation: isolate; }
html .cl .story .photo.mcut::before { content: ""; position: absolute; inset: 10% 5% 0; background: radial-gradient(circle at 50% 45%, rgba(0,154,68,.25), rgba(8,9,10,0) 65%); z-index: -1; }
html .cl .story .photo.mcut img { width: 100%; max-width: 480px; height: auto !important; aspect-ratio: auto !important; object-fit: contain !important; -webkit-mask-image: linear-gradient(180deg, #000 82%, transparent 100%); mask-image: linear-gradient(180deg, #000 82%, transparent 100%); }
html .cl .story img.signature { display: block; width: 150px; max-width: 45%; height: auto; margin: 22px 0 0 -4px; opacity: .92; }
html.sig-ok .cl img.signature, html.sig-ok .cc img.signature { clip-path: inset(0 100% 0 0); }   /* the signature writes itself, left to right, when it comes into view (Matteo 16 Nov) */
html.sig-ok .cl img.signature.go, html.sig-ok .cc img.signature.go { animation: sig-write 2.2s cubic-bezier(.55,.1,.35,1) forwards; }
@keyframes sig-write { to { clip-path: inset(0 0 0 0); } }
html .cl .team .member { transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease; }
html .cl .team .member img { transition: transform .5s ease; }
html .cl .team .member:hover { transform: translateY(-4px); border-color: rgba(43,212,122,.7); box-shadow: 0 18px 40px rgba(0,0,0,.45), 0 0 0 1px rgba(43,212,122,.35); }   /* team cards come alive on hover (Matteo 16 Nov) */
html .cl .team .member:hover img { transform: scale(1.04); }
html .cl .team .member { overflow: hidden; }
@media (prefers-reduced-motion: reduce) { html .cl .team .member, html .cl .team .member img { transition: none; } html .cl .team .member:hover { transform: none; } }
html .cl .story .sig { margin: 6px 0 0 !important; font-family: var(--head); font-size: 14px; letter-spacing: .04em; text-transform: uppercase; color: var(--text); }
html .cl .story .sig span { display: block; font-family: var(--body); font-size: 12.5px; letter-spacing: 0; text-transform: none; color: var(--text-3); margin-top: 2px; }
html .cl .band-up > img { object-position: center 58% !important; }   /* show the riders' faces (Matteo) */
html .cl .band-up.priv > img { object-position: center 75% !important; }
html .cl .hero.phero.dhero .in { padding-block: 150px 60px !important; }   /* taller destination hero: more of the photo (Matteo) */
/* every destination hero the same height, whatever the H1 length (Matteo 15 Nov): content sits at the bottom */
html .cl .hero.phero.dhero { min-height: 640px; display: flex; flex-direction: column; justify-content: flex-end; }
html .cl .hero.phero.dhero > .in { width: 100%; box-sizing: border-box; }
@media (max-width: 900px) { html .cl .hero.phero.dhero { min-height: 600px; } }
/* breathing room between text, map and photos (Matteo 15 Nov: map and photos were touching) */
html .cl .dsplit + .gal3, html .cl .dsplit + .dprose, html .cl .dprose + .gal3, html .cl .gal3 + .dprose, html .cl .gal3 + .gal3 { margin-top: 36px; }
html .cl .dsplit { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); gap: 32px; align-items: start; }
@media (max-width: 900px) { html .cl .dsplit { grid-template-columns: minmax(0, 1fr); } }
html .cl .cmapbox { width: 100%; max-width: 374px; justify-self: end; }
html .cl .cmapbox svg { display: block; width: 100%; height: auto; border-radius: 12px; border: 1px solid var(--border); }
html .cl .dtour .tx { gap: 10px; }
html .cl .dtour .ctas.one { margin-top: auto; padding-top: 6px; }
html .cl .dband { margin-top: 48px; }
html .cc .dtours { padding-top: 56px; }
html .cc .dtours .tour { min-height: 380px; aspect-ratio: auto; }   /* same height as the homepage cards */
html .cl .fchips, html .cc .fchips { display: flex; flex-wrap: wrap; gap: 8px; margin: 28px 0 20px; }
html .cl .fchip, html .cc .fchip { display: inline-flex; align-items: center; gap: 8px; font: 600 12.5px/1 var(--body); letter-spacing: .05em; text-transform: uppercase; color: var(--text-2); background: var(--wash); border: 1px solid var(--border-strong); border-radius: 999px; padding: 9px 15px; cursor: pointer; }
html .cl .fchip:hover, html .cc .fchip:hover { color: #fff; border-color: rgba(255,255,255,.3); }
html .cl .fchip .fd, html .cc .fchip .fd { width: 7px; height: 7px; border-radius: 50%; background: var(--text-3); }
html .cl .fchip.on, html .cc .fchip.on { background: var(--green); border-color: var(--green); color: #fff; }
html .cl .fchip[data-f=road] .fd, html .cc .fchip[data-f=road] .fd, html .cl .fchip[data-f=gf] .fd, html .cc .fchip[data-f=gf] .fd { background: #e10600; }
html .cl .fchip[data-f=gravel] .fd, html .cc .fchip[data-f=gravel] .fd { background: var(--gravel, #b9895a); }
html .cl .fchip.on[data-f=road], html .cc .fchip.on[data-f=road], html .cl .fchip.on[data-f=gf], html .cc .fchip.on[data-f=gf] { background: #e10600; border-color: #e10600; }
html .cl .fchip.on[data-f=gravel], html .cc .fchip.on[data-f=gravel] { background: var(--gravel, #b9895a); border-color: var(--gravel, #b9895a); }
html .cl .dcta { background: linear-gradient(160deg, rgba(0,154,68,.22), rgba(0,154,68,.06)), var(--panel) !important; border-color: rgba(0,154,68,.45) !important; }
html .cl .dcta .tx { justify-content: center; }
html .cl .dcta .ctat { font-family: var(--head); text-transform: uppercase; color: var(--text); font-size: clamp(26px, 2.6vw, 34px); line-height: 1.08; margin: 0; }
html .cl .dcta p { color: var(--text-2); font-size: 14.5px; }
html .cl .dcta .btn { white-space: nowrap; width: 100%; justify-content: center; }
html .cl .fchip.on .fd, html .cc .fchip.on .fd { background: #fff; animation: fchip-pulse 1.8s ease-in-out infinite; }
@keyframes fchip-pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(255,255,255,.7); opacity: 1; } 50% { box-shadow: 0 0 0 5px rgba(255,255,255,0); opacity: .6; } }
@media (prefers-reduced-motion: reduce) { html .cl .fchip[data-f=road] .fd, html .cc .fchip[data-f=road] .fd, html .cl .fchip[data-f=gf] .fd, html .cc .fchip[data-f=gf] .fd { background: #e10600; }
html .cl .fchip[data-f=gravel] .fd, html .cc .fchip[data-f=gravel] .fd { background: var(--gravel, #b9895a); }
html .cl .fchip.on[data-f=road], html .cc .fchip.on[data-f=road], html .cl .fchip.on[data-f=gf], html .cc .fchip.on[data-f=gf] { background: #e10600; border-color: #e10600; }
html .cl .fchip.on[data-f=gravel], html .cc .fchip.on[data-f=gravel] { background: var(--gravel, #b9895a); border-color: var(--gravel, #b9895a); }
html .cl .dcta { background: linear-gradient(160deg, rgba(0,154,68,.22), rgba(0,154,68,.06)), var(--panel) !important; border-color: rgba(0,154,68,.45) !important; }
html .cl .dcta .tx { justify-content: center; }
html .cl .dcta .ctat { font-family: var(--head); text-transform: uppercase; color: var(--text); font-size: clamp(26px, 2.6vw, 34px); line-height: 1.08; margin: 0; }
html .cl .dcta p { color: var(--text-2); font-size: 14.5px; }
html .cl .dcta .btn { white-space: nowrap; width: 100%; justify-content: center; }
html .cl .fchip.on .fd, html .cc .fchip.on .fd { animation: none; } }
html .cl [hidden], html .cc .tours > [hidden] { display: none !important; }
html .cl .vgrid.few .vcard:nth-child(n+7) { display: none; }
html .cl .vmore-wrap { justify-content: center; margin-top: 22px; }
html .cl .info h2.wa a { color: var(--green-text); }
html .cl .why6 .panel { display: flex; gap: 14px; align-items: flex-start; }
html .cl .vcard { margin: 0; padding: 0; overflow: hidden; }
html .cl .vcard .yt, html .cl .vcard iframe { display: block; width: 100%; aspect-ratio: 16 / 9; border: 0; padding: 0; margin: 0; background: #000; position: relative; cursor: pointer; }
html .cl .vcard .yt img { width: 100%; height: 100%; object-fit: cover; display: block; filter: brightness(.82); transition: filter .2s; }
html .cl .vcard .yt:hover img { filter: brightness(1); }
html .cl .vcard .play { position: absolute; left: 50%; top: 50%; width: 64px; height: 64px; margin: -32px 0 0 -32px; border-radius: 50%; background: #009a44; box-shadow: 0 6px 24px rgba(0,0,0,.4); }
html .cl .vcard .play::after { content: ""; position: absolute; left: 26px; top: 20px; border-style: solid; border-width: 12px 0 12px 19px; border-color: transparent transparent transparent #fff; }
html .cl .vcard figcaption { padding: 14px 18px 16px; display: flex; align-items: baseline; gap: 10px; }
html .cl .vcard figcaption h2 { font-size: 22px; }
html .cl .vcard figcaption span { font-size: 13px; color: var(--text-3); }
html .cl .steps4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
html .cl .org4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
@media (max-width: 1000px) { html .cl .steps4, html .cl .org4 { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 520px) { html .cl .steps4, html .cl .org4 { grid-template-columns: minmax(0, 1fr); } }
html .cl .step { padding: 20px 22px; }
html .cl .step .n { display: block; font-family: var(--head); font-size: 15px; color: #ff3d33; letter-spacing: .06em; margin-bottom: 8px; }
html .cl .step h3 { font-size: 22px; }
html .cl .org { padding: 16px 18px; display: flex; gap: 12px; align-items: center; }
html .cl .org h3 { font-size: 18px; }
html .cl .oic { flex: none; width: 40px; height: 40px; border-radius: 10px; display: grid; place-items: center; background: var(--green-wash); border: 1px solid rgba(0,154,68,.35); }
html .cl .oic svg { width: 21px; height: 21px; fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
html .cl .locwrap { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); gap: 22px; align-items: start; margin-top: 18px; }
@media (max-width: 900px) { html .cl .locwrap { grid-template-columns: minmax(0, 1fr); } }
html .cl .lmapbox svg { display: block; width: 100%; height: auto; border-radius: 12px; border: 1px solid var(--border); }
html .cl .locs.loclist { display: block !important; columns: 3; column-gap: 28px; margin: 0; padding: 0; width: 100%; max-width: none; list-style: none; }
@media (max-width: 1000px) { html .cl .locs.loclist { columns: 2; } html .cl .locwrap { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 600px) { html .cl .locs.loclist { columns: 1; } }
html .cl .locs.loclist li::before, html .cl .locs.loclist li::after { content: none !important; display: none !important; }
html .cl .locs.loclist li { break-inside: avoid; margin-bottom: 6px !important; display: flex; gap: 10px; align-items: flex-start; justify-content: flex-start; text-align: left; line-height: 1.4; margin: 0; background: none; border: 0; padding: 0; border-radius: 0; font-size: 14px; color: var(--text-2); }
html .cl .locs.loclist .n { flex: none; width: 22px; height: 22px; border-radius: 50%; background: #e10600; color: #fff; font-size: 11px; font-weight: 700; display: grid; place-items: center; margin-top: 1px; }
html .cl .locs { list-style: none; margin: 18px 0 0; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; }
html .cl .locs li { font-size: 13.5px; color: var(--text); background: var(--wash); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 13px; }
html .cl .faqs { display: grid; gap: 10px; max-width: 900px; }
html .cl .faq { padding: 0; }
html .cl .faq summary { list-style: none; cursor: pointer; padding: 16px 52px 16px 20px; position: relative; }
html .cl .faq summary::-webkit-details-marker { display: none; }
html .cl .faq summary::after { content: "+"; position: absolute; right: 20px; top: 50%; transform: translateY(-50%); font: 600 22px var(--body); color: var(--green-text); }
html .cl .faq[open] summary::after { content: "–"; }
html .cl .faq summary h3 { font-family: var(--body); font-size: 16px; font-weight: 600; text-transform: none; letter-spacing: 0; line-height: 1.4; }
html .cl .faq .a { padding: 0 20px 16px; color: var(--text-2); }
html .cl .faq .a p { margin: 0; }
html .cl .info .cphoto { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; border-radius: 10px; display: block; }
html .cl .info h3.gt { font-family: var(--head); font-size: clamp(26px, 3vw, 34px); color: var(--text); letter-spacing: .01em; margin: 6px 0 0; }
html .cl .info p { margin: 0; color: var(--text-2); }
html .cl .info p a { color: var(--text); font-weight: 600; text-decoration: none; }
html .cl h2.lab { font-family: var(--body); font-size: 11px; line-height: 1.4; letter-spacing: .09em; font-weight: 600; color: var(--text-3); text-transform: uppercase; margin: 0 0 12px; }
'''

# ---------- exit pop-up (Matteo 16 Nov): "any questions?" when a visitor is about to leave a tour page or Custom tours ----------
# Once per visit; not before the cookie choice; not when the newsletter pop-up is open or was closed in the last hour; snoozed 3 days after closing.
# Desktop: the pointer leaves through the top of the window. Phones: a fast scroll back up after reading half the page.
def exit_pop(title, text, second):
    t2, u2 = second
    return (f'<div class="xpop" id="xpop" hidden><div class="xpop-bg" data-x></div><div class="xpop-box panel" role="dialog" aria-modal="true" aria-labelledby="xpop-t" tabindex="-1">'
            f'<button type="button" class="xpop-x" aria-label="Close" data-x>×</button><div class="eyebrow">Before you go</div><p class="xpop-t" id="xpop-t">{E(title)}</p>'
            f'<p class="xpop-p">{E(text)}</p><div class="ctas"><a class="btn btn-go" href="https://wa.me/message/WVBRO6XAMQMCH1" target="_blank" rel="noopener">WhatsApp us →</a>'
            f'<a class="btn btn-ghost" href="{E(u2)}">{E(t2)}</a></div><p class="xpop-s">We usually reply within a few hours.</p></div></div>' + EXIT_JS)
EXIT_JS = """<script>(function(){var p=document.getElementById('xpop');if(!p)return;var K='cc_exit',t0=Date.now(),last=null,maxY=0,ys=[];
function g(k){try{return localStorage.getItem(k);}catch(e){return null;}}
function ok(){if(!g('cc_consent'))return false;try{if(sessionStorage.getItem(K))return false;}catch(e){}
var c=+(g(K)||0);if(c&&Date.now()-c<3*864e5)return false;var n=document.getElementById('nl-pop');if(n&&!n.hidden)return false;
try{var nl=JSON.parse(g('cc_nl')||'{}');if(nl.c&&Date.now()-nl.c<36e5)return false;}catch(e){}return Date.now()-t0>8000;}
function open(){if(!ok())return;try{sessionStorage.setItem(K,'1');}catch(e){}last=document.activeElement;p.hidden=false;p.querySelector('.xpop-box').focus({preventScroll:true});document.addEventListener('keydown',key);}
function close(){p.hidden=true;document.removeEventListener('keydown',key);try{localStorage.setItem(K,String(Date.now()));}catch(e){}if(last&&last.focus)last.focus({preventScroll:true});}
function key(e){if(e.key==='Escape')close();}
p.querySelectorAll('[data-x]').forEach(function(b){b.addEventListener('click',close);});
document.addEventListener('mouseout',function(e){if(!e.relatedTarget&&e.clientY<=0)open();});
if(matchMedia('(hover: none)').matches){addEventListener('scroll',function(){var y=scrollY,h=document.documentElement.scrollHeight-innerHeight;maxY=Math.max(maxY,y);ys.push([Date.now(),y]);while(ys.length&&Date.now()-ys[0][0]>700)ys.shift();
if(maxY>h*.5&&ys.length&&ys[0][1]-y>500)open();},{passive:true});}})();</script>"""
EXIT_CSS = '''
html .cl .xpop { position: fixed; inset: 0; z-index: 99990; display: grid; place-items: center; padding: 16px; }
html .cl .xpop[hidden] { display: none; }
html .cl .xpop-bg { position: absolute; inset: 0; background: rgba(4,5,6,.72); backdrop-filter: blur(3px); }
html .cl .xpop-box { position: relative; width: min(460px, 100%); padding: 30px 28px 24px; border: 1px solid rgba(43,212,122,.35); border-radius: 16px; background: #0f1113; box-shadow: 0 30px 80px rgba(0,0,0,.6); outline: none; animation: xpop-in .3s ease; }
@keyframes xpop-in { from { opacity: 0; transform: translateY(14px) scale(.98); } to { opacity: 1; transform: none; } }
@media (prefers-reduced-motion: reduce) { html .cl .xpop-box { animation: none; } }
html .cl .xpop-x { position: absolute !important; min-height: 0 !important; line-height: 0 !important; top: 12px; right: 12px; width: 36px; height: 36px; display: grid; place-items: center; padding: 0 !important; border: 0; border-radius: 50%; background: rgba(255,255,255,.08); cursor: pointer; font-size: 0; }
html .cl .xpop-x::before, html .cl .xpop-x::after { content: ""; position: absolute; left: 50%; top: 50%; width: 14px; height: 2px; margin: -1px 0 0 -7px; border-radius: 1px; background: #fff; transform: rotate(45deg); }   /* a drawn X, pinned to the middle (Matteo 16 Nov) */
html .cl .xpop-x::after { transform: rotate(-45deg); }
html .cl .xpop-x:hover { background: rgba(255,255,255,.16); }
html .cl .xpop-t { font-family: var(--head); font-size: clamp(26px, 5vw, 32px); line-height: 1.05; text-transform: uppercase; color: #fff; margin: 4px 0 10px; padding-right: 30px; }
html .cl .xpop-p { color: var(--text-2); font-size: 15px; line-height: 1.55; margin: 0 0 18px; }
html .cl .xpop .ctas { display: flex; flex-wrap: wrap; gap: 10px; margin: 0; }
html .cl .xpop-s { margin: 14px 0 0; font-size: 12.5px; color: var(--text-3); }
'''

PAGE_CSS += EXIT_CSS
PAGE_CSS += '''
html .cl .why2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-top: 4px; }
html .cl .why2 .panel { padding: 22px 26px; }
html .cl .why2 h3 { font-size: 20px; margin: 0 0 12px; color: var(--green-text, #2bd47a); }
html .cl .why2 p { margin: 0; line-height: 1.9; color: var(--text-2); }
@media (max-width: 760px) { html .cl .why2 { grid-template-columns: minmax(0, 1fr); } }
'''
PAGE_CSS += '''
html.hdyn-ok .cc-page section .head, html.hdyn-ok .cc-page .tour { opacity: 0; transform: translateY(18px); }
html.hdyn-ok .cc-page section .head.in-view, html.hdyn-ok .cc-page .tour.in-view { opacity: 1; transform: none; transition: opacity .7s ease, transform .7s ease; transition-delay: var(--d, 0ms); }
'''   # homepage: titles and tour cards rise in (Matteo 16 Nov); only when the script runs and motion is welcome
SIGN_JS = """<script>(function(){if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches)return;var s=document.querySelectorAll('img.signature');if(!s.length)return;
document.documentElement.classList.add('sig-ok');var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){o.unobserve(e.target);e.target._sig.classList.add('go');}});},{threshold:.5});
s.forEach(function(x){var t=x.nextElementSibling||x.parentElement;t._sig=x;o.observe(t);});})();</script>"""   # watch the name under the signature: a clipped image never counts as on screen   # the signature writes itself (About, homepage)
LOC_JS = """<script>(function(){var m=document.querySelector('.cl .lmap.dyn-l'),l=document.querySelector('.cl .loclist');if(!m||!l)return;
var rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
if(!rm&&'IntersectionObserver' in window){m.classList.add('wait');new IntersectionObserver(function(es,o){if(es[0].isIntersecting){o.disconnect();m.classList.add('go');}},{threshold:.3}).observe(m);}
function set(n){m.classList.toggle('hl',!!n);m.querySelectorAll('.ld').forEach(function(g){g.classList.toggle('on',g.dataset.n===n);});l.querySelectorAll('li').forEach(function(li){li.classList.toggle('on',li.dataset.n===n);});}
l.querySelectorAll('li').forEach(function(li){['mouseenter','focus'].forEach(function(ev){li.addEventListener(ev,function(){set(li.dataset.n);});});li.addEventListener('click',function(){set(li.dataset.n);});});
l.addEventListener('mouseleave',function(){set(null);});m.querySelectorAll('.ld').forEach(function(g){g.addEventListener('mouseenter',function(){set(g.dataset.n);});g.addEventListener('mouseleave',function(){set(null);});});})();</script>"""
PAGE_CSS += '''
html .cl .lmap .ld { transform-box: fill-box; transform-origin: center; transition: opacity .25s, transform .25s; cursor: default; }
html .cl .lmap.wait .ld { opacity: 0; transform: scale(.3); }
html .cl .lmap.wait.go .ld { opacity: 1; transform: none; transition: opacity .35s ease, transform .35s cubic-bezier(.3,1.6,.5,1); transition-delay: calc(var(--i) * 60ms); }
html .cl .lmap.hl .ld:not(.on) { opacity: .25; transition-delay: 0s; }
html .cl .lmap .ld.on { transform: scale(1.45); transition-delay: 0s; }
html .cl .lmap .ld.on circle { fill: #2bd47a; }
html .cl .loclist li { cursor: default; border-radius: 8px; transition: background .2s, color .2s; outline: none; }
html .cl .loclist li.on, html .cl .loclist li:focus-visible { background: rgba(0,154,68,.14); color: #fff; }
html .cl .loclist li.on .n { background: #2bd47a; color: #0a0c0e; }
'''   # the location ideas map (Custom tours): dots pop in, list and dots highlight each other (Matteo 16 Nov)

PAGES = {'about': about, 'contact': contact, 'destinations': destinations, 'testimonials': testimonials, 'private-trips': custom}
for _slug in DEST_IDS: PAGES['dest-' + _slug] = (lambda s_: (lambda: destination(s_)))(_slug)

from css_scope import scope_css
from social import SOCIAL_CSS
PAGE_CSS += scope_css(SOCIAL_CSS, 'html .cl')   # the shared social icon row, outside the footer too

if __name__ == '__main__':
    lists_prev = open(ROOT + 'tourspages/trips.html').read()   # header/footer/CSS exactly as the tour pages
    for name in sys.argv[1:] or PAGES:
        d = PAGES[name]()
        d['main'] = fix_text(d['main'])
        a, b = lists_prev.index('<div class="cl cl-page">'), lists_prev.index('<div class="cc"><footer>')
        prev = lists_prev[:a] + '<div class="cl cl-page">\n' + d['main'] + '\n</div>\n' + lists_prev[b:]
        prev = prev.replace('</style>', '</style>\n<style>\n' + d['css'] + '\n</style>', 1)
        open(ROOT + f'tourspages/page-{name}.html', 'w').write(prev)   # page-*: the design files keep their names
        json.dump(d, open(ROOT + f'stg-tours/out/list-{name}.json', 'w'), ensure_ascii=False)
        print(name, len(d['main']), 'chars | h1', d['main'].count('<h1'), '| h2', d['main'].count('<h2'), '| img', d['main'].count('<img'))
