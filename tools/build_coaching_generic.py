"""Build the remaining Coaching pages from the live text (coaching/text/<page>.txt) in the new design.

Matteo 15 Nov 2026: "finish all of the rest of the pages". SEO (CLAUDE.md): every page keeps its live H1, every live H2
(same wording), all body copy, and every image with its live alt text. The layout is the shared design system
(coaching_common); each H2 starts a section, images sit beside the text, lists become tick lists, FAQs fold, live
buttons stay buttons, and a page with a live form gets the contact section (the live Elementor form on staging).
Small black icon images (PNG under 200 px) are left out: on the dark site they were invisible. Logged in SEO-DECISIONS.md.

  python3 -I tools/build_coaching_generic.py [page ...]
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
from PIL import Image

CAL = 'https://calendly.com/cigalacycling'
DEFAULT_HERO = ('IMG_3999AWDWWWU', 'Cigala Cycling Coaching group riding in Wicklow, Ireland')   # alt typo fixed (SEO-DECISIONS)

PAGES = {   # name -> (live path, hero image key or None for the first page photo)
    'about': ('/about/', None), 'about2': ('/about2/', None), 'coaching-vision': ('/coaching-vision/', None),
    'testing': ('/testing/', None), 'nutrition': ('/nutrition/', None), 'bike-fitting': ('/bike-fitting/', None),
    'book-1-on-1-session': ('/book-1-on-1-session/', 'imgi_16_g675BzCnYW'), 'talent-scout': ('/talent-scout/', None),
    'club-talk': ('/club-talk/', None), 'contact': ('/contact/', None),
    'cycling-coach-uk': ('/cycling-coach-uk/', None), 'cycling-coach-usa': ('/cycling-coach-usa/', None),
    'cycling-coach-canada': ('/cycling-coach-canada/', None), 'preparatore-di-ciclismo-italia': ('/preparatore-di-ciclismo-italia/', None),
}
WEBP = {o['url']: o['webp'] for o in json.load(open(ROOT + 'coaching/images.json')) if o.get('webp')}
MARK = re.compile(r'^(H[1-6]|P|LI|TXT|LABEL|BUTTON):\s?|^<(img|input|textarea|select)\b')
LINK = re.compile(r'\[\s*(.*?)\s*\]\(\s*([^)]*?)\s*\)', re.S)

def inline(s):
    """markdown bold/links -> html, escaped"""
    out, pos = '', 0
    for m in LINK.finditer(s):
        out += E(s[pos:m.start()])
        t, u = re.sub(r'\s+', ' ', m.group(1)).strip(), m.group(2).strip()
        out += f'<a href="{E(u)}" {EXT}>{E(t)}</a>' if (t and u and u != '#') else E(t)
        pos = m.end()
    out += E(s[pos:])
    out = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', out, flags=re.S)
    return out.replace('\n', '<br>')

def parse(name):
    """live text -> list of (kind, data)"""
    raw = open(ROOT + f'coaching/text/{name}.txt').read().split('\n')
    blocks = []
    for line in raw:
        if MARK.match(line) or not blocks: blocks.append(line)
        else: blocks[-1] += '\n' + line
    items, form = [], False
    for b in blocks:
        if b.startswith('<img '):
            m = re.match(r"<img (\S+) alt=(['\"])(.*?)\2>", b, re.S)
            if m: items.append(('img', m.group(1), m.group(3)))
            continue
        if b.startswith(('<input', '<textarea', '<select')):
            if 'form_fields' in b: form = True
            continue
        if b.startswith(('LABEL:', 'BUTTON:')): continue
        kind, _, text = b.partition(':'); text = text.strip()
        if kind in ('H1', 'H2', 'H3', 'H4', 'H5', 'H6'):
            items.append((kind.lower(), text))
        elif kind == 'P': items.append(('p', text))
        elif kind == 'LI': items.append(('li', text))
        elif kind == 'TXT':
            # buttons: markdown links with text; image wrappers have no text
            btns = [(re.sub(r'\s+', ' ', t).strip(), u.strip()) for t, u in LINK.findall(text)]
            rest = LINK.sub('', text).strip()
            if rest:
                for para in re.split(r'\n\s*\n', rest):
                    if para.strip(): items.append(('p', para.strip()))
            for t, u in btns:
                if t and u: items.append(('btn', t, u))
    return items, form

def heading_html(tag, text, cls=''):
    """keep the live wording: multi-line link headings become spans joined by a space"""
    m = LINK.fullmatch(text.strip())
    if m:
        parts = [x.strip() for x in m.group(1).split('\n') if x.strip()]
        inner = ' '.join(f'<span>{E(x)}</span>' for x in parts)
        u = m.group(2).strip()
        if u and u != '#': inner = f'<a href="{E(u)}" {EXT}>{inner}</a>'
    else:
        inner = E(re.sub(r'\s*\n\s*', ' ', text))
    plain = re.sub(r'<[^>]+>', '', inner).strip()
    if re.fullmatch(r'[\w.+-]+@[\w-]+\.[\w.]+', plain): inner = f'<a href="mailto:{plain}">{inner}</a>'          # contact details tap to email / call
    elif re.fullmatch(r'\+?[\d ]{8,}', plain): inner = f'<a href="tel:{plain.replace(" ", "")}">{inner}</a>'
    c = f' class="{cls}"' if cls else ''
    return f'<{tag}{c}>{inner}</{tag}>'

def is_icon(url):
    w = WEBP.get(url)
    if not w: return False
    try: return url.lower().endswith('.png') and max(Image.open(ROOT + 'coaching/webp/' + w).size) < 200
    except Exception: return False

def pic(url, alt, cls='photo', eager=False):
    key = url.split('/uploads/')[1]
    if url.lower().endswith('.png'): cls += ' gn-png'   # logos and infographics: shown whole, not cropped
    name = 'pg-' + re.sub(r'[^a-z0-9]+', '-', alt.split('|')[0].lower()).strip('-')[:40] if alt else 'pg-' + re.sub(r'[^a-z0-9]+', '-', key.lower())[-40:]
    return f'<div class="{cls}"><img src="{img(key, name)}" alt="{E(alt)}" loading="{"eager" if eager else "lazy"}"></div>'

def body_html(items):
    """paragraphs, lists, sub-headings and buttons of one section"""
    out, ul, btns = '', [], []
    def flush():
        nonlocal out, ul
        if ul: out += '<ul class="ticks">' + ''.join(f'<li>{inline(x)}</li>' for x in ul) + '</ul>'; ul = []
    for it in items:
        k = it[0]
        if k == 'li': ul.append(it[1]); continue
        flush()
        if k == 'p': out += f'<p>{inline(it[1])}</p>'
        elif k in ('h3', 'h4', 'h5', 'h6'): out += heading_html(k, it[1], 'gn-sub')
        elif k == 'btn': btns.append(it)
    flush()
    if btns and all(re.search(r'facebook|instagram|youtube|tiktok|x\.com|twitter|threads|wa\.me|whatsapp', u) for _, _, u in btns):
        out += social_row(); btns = []   # the live social links: the shared icon row
    if btns:
        out += '<div class="ctas">' + ''.join(f'<a class="btn {"btn-go" if i == 0 else "btn-ghost"}" href="{E(u)}" {EXT}>{E(t)}</a>' for i, (_, t, u) in enumerate(btns)) + '</div>'
    return out

def faq_html(items):
    out, cur = '', None
    qs = []
    for it in items:
        if it[0] in ('h3', 'h4'): cur = [it[1], []]; qs.append(cur)
        elif cur and it[0] in ('p', 'li'): cur[1].append(it)
    for i, (q, body) in enumerate(qs):
        out += f'<details{" open" if i == 0 else ""}><summary>{heading_html("h3", q)}</summary>{body_html(body)}</details>'
    return f'<div class="faq">{out}</div>'

def section(h2, items, n):
    imgs = [it for it in items if it[0] == 'img' and it[1] in WEBP and not is_icon(it[1])]   # (a few live images are 404s)
    rest = [it for it in items if it[0] != 'img']
    head = heading_html('h2', h2) if h2 else ''
    bar = '<div class="bar"></div>' if h2 and not h2.startswith(('LEGGI LE NOSTRE RECENSIONI', 'READ OUR TESTIMONIALS')) else ''   # Matteo 15 Nov: no line under the testimonials heading
    if h2 and 'FREQUENTLY' in h2.upper() and any(it[0] in ('h3', 'h4') for it in rest):
        return f'<section>\n  <div class="in">\n    <div class="head"><div>{head}{bar}</div></div>\n    {faq_html(rest)}\n  </div>\n</section>'
    text = body_html(rest)
    if imgs and text:
        main, more = imgs[0], imgs[1:]
        gal = ''.join(pic(u, a, 'g') for _, u, a in more)
        flip = ' flip' if n % 2 else ''
        return (f'<section>\n  <div class="in split gn-split{flip}">\n    <div class="gn-txt">{head}{bar}{text}</div>\n    {pic(main[1], main[2], "photo gn-photo")}\n  </div>'
                + (f'\n  <div class="in"><div class="gn-gal">{gal}</div></div>' if gal else '') + '\n</section>')
    if imgs:
        gal = ''.join(pic(u, a, 'g') for _, u, a in imgs)
        return f'<section>\n  <div class="in">\n    {"<div class=head><div>" + head + bar + "</div></div>" if head else ""}\n    <div class="gn-gal">{gal}</div>\n  </div>\n</section>'
    if not text and not head: return ''
    return f'<section>\n  <div class="in gn-txt gn-solo">{head}{bar}{text}</div>\n</section>'

CONTACT_PHOTO = ('imgi_16_g675BzCnYW', 'matteo-coaching')
def contact_block(title='GET IN TOUCH TODAY', lede='Send us a message and we will get back to you.'):
    return f'''<section id="contact">
  <div class="in split">
    <div class="photo rider"><img src="{img(CONTACT_PHOTO[0], CONTACT_PHOTO[1])}" alt="{E(live_alt(CONTACT_PHOTO[0]))}" loading="lazy" width="1440" height="1081"></div>
    <div>
      <div class="eyebrow">Contact</div>
      <h3 class="h-sec">{title}</h3>
      <div class="bar"></div>
      <p class="lede">{lede}</p>
      <form class="form panel" method="post" action="#" onsubmit="return false">
        <label>Name<input name="form_fields[name]" type="text" placeholder="Name *" required autocomplete="name"></label>
        <label>Email<input name="form_fields[email]" type="email" placeholder="Email *" required autocomplete="email"></label>
        <label>Phone<input name="form_fields[phone]" type="tel" placeholder="Phone (with country code) *" required autocomplete="tel"></label>
        <label>Message<textarea name="form_fields[message]" placeholder="Your Message *" rows="5" required></textarea></label>
        <button class="btn btn-go" type="submit">Send &gt;</button>
      </form>
    </div>
  </div>
</section>'''

GCSS = '''<style>
.hero-sm { min-height: min(520px, 70svh); }
.hero-sm .in { padding-block: 110px 48px; }
.hero-sm h1 { max-width: 20ch; font-size: clamp(34px, 5.4vw, 64px); }
.gn-txt, .gn-solo, .gn-txt p, .gn-txt li, .tm blockquote { overflow-wrap: anywhere; }   /* long links and emails wrap on phones */
.gn-txt p { margin: 14px 0 0; color: var(--text-2); line-height: 1.65; max-width: 68ch; }
.gn-txt .ticks { margin-top: 16px; }
.gn-txt .ctas { margin-top: 22px; }
.gn-txt h2 span, .gn-solo h2 span { display: block; }
.gn-sub { font-size: clamp(20px, 2vw, 24px); margin: 26px 0 0; }
h4.gn-sub, h5.gn-sub, h6.gn-sub { font: 700 15px/1.4 var(--body); text-transform: none; letter-spacing: 0; color: var(--text); }
.gn-solo { max-width: 860px; }
.gn-photo { aspect-ratio: 4 / 3; }
.gn-photo img, .gn-gal img { width: 100%; height: 100%; object-fit: cover; }
.gn-png { background: #fff; }
.gn-png img { object-fit: contain !important; padding: 10px; }
.gn-gal .gn-png { aspect-ratio: 3 / 4; }
/* headings that are buttons on the live page (prices, links): shown as cards */
.gn-solo h2 a { display: grid; gap: 4px; padding: 22px 24px; border: 1px solid var(--border-strong); border-radius: 14px; background: var(--panel-grad), var(--panel); text-decoration: none; color: var(--text); max-width: 420px; transition: border-color .2s; }
.gn-solo h2 a:hover { border-color: var(--green); }
.gn-solo h2 a span { display: block; font-size: 18px; line-height: 1.3; }
.gn-solo h2 a span:first-child { font-size: 40px; color: var(--green-text); }
.gn-solo h2 a span:last-child { margin-top: 6px; font: 600 14px/1.4 var(--body); letter-spacing: .04em; color: var(--green-text); }
.gn-gal { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; margin-top: 20px; }
.gn-gal .g { aspect-ratio: 4 / 3; border-radius: 10px; overflow: hidden; border: 1px solid var(--border); }
.gn-txt a:not(.btn), .gn-solo a:not(.btn) { color: var(--green-text); }
.rider { aspect-ratio: 4 / 3; }
.form { display: grid; gap: 14px; padding: 22px; margin-top: 22px; }
.form label { display: grid; gap: 6px; font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); }
.form input, .form textarea { font: 400 16px/1.4 var(--body); color: var(--text); background: rgba(255,255,255,.04); border: 1px solid var(--border-strong); border-radius: 8px; padding: 12px 14px; width: 100%; }
.form .btn { justify-self: start; }
.panel { background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: var(--r); }
.faq h3 { display: inline; font: 600 15px/1.4 var(--body); text-transform: none; letter-spacing: 0; color: var(--text); }
@media (max-width: 900px) { .gn-photo { aspect-ratio: 16 / 10; } }
</style>'''

def hero(h1, lede, img_html, btns):
    ctas = ''.join(f'<a class="btn {"btn-go" if i == 0 else "btn-ghost"}" href="{E(u)}" {EXT}>{E(t)}</a>' for i, (_, t, u) in enumerate(btns[:2]))
    return f'''<div class="hero hero-sm">
  {img_html}
  <div class="in">
    {heading_html('h1', h1)}
    {f'<p class="lede">{inline(lede)}</p>' if lede else ''}
    {f'<div class="ctas">{ctas}</div>' if ctas else ''}
  </div>
</div>'''

def build_page(name, h2_changes=None, extra_main='', contact=None):
    path, hero_key = PAGES[name]
    items, form = parse(name)
    if name == 'preparatore-di-ciclismo-italia':   # Matteo 15 Nov: 2026 in numbers on all the country pages
        items = [('h2', '2026 IN NUMERI') if it == ('h2', '2025 IN NUMERI') else it for it in items]
        h2_changes = {'drop': ['2025 IN NUMERI'], 'add': ['2026 IN NUMERI']}
    h1s = [it for it in items if it[0] == 'h1']
    h1 = h1s[0][1] if h1s else LIVE[C + path]['h1'][0]
    # intro: everything before the first H2 (minus the H1)
    first_h2 = next((i for i, it in enumerate(items) if it[0] == 'h2'), len(items))
    intro = [it for it in items[:first_h2] if it[0] != 'h1']
    photos = [it for it in items if it[0] == 'img' and it[1] in WEBP and not is_icon(it[1])]
    if hero_key:
        hu = [u for u in WEBP if hero_key in u][0]; hero_img = (hu, live_alt(hero_key))
    elif photos and photos[0][1].lower().endswith(('.jpg', '.jpeg')):
        hero_img = (photos[0][1], photos[0][2])
    else:
        hu = [u for u in WEBP if DEFAULT_HERO[0] in u][0]; hero_img = (hu, DEFAULT_HERO[1])
    hkey = hero_img[0].split('/uploads/')[1]
    hero_tag = f'<img src="{img(hkey, "pg-hero-" + name)}" alt="{E(hero_img[1])}">'
    lede_i = next((i for i, it in enumerate(intro) if it[0] == 'p' and len(it[1]) < 420), None)
    lede = intro.pop(lede_i)[1] if lede_i is not None else ''
    hero_btns = [it for it in intro if it[0] == 'btn'][:2]
    intro = [it for it in intro if not (it[0] == 'btn' and it in hero_btns) and not (it[0] == 'img' and it[1] == hero_img[0])]
    blocks = [hero(h1, lede, hero_tag, hero_btns)]
    n = 0
    if any(it[0] in ('p', 'li', 'h3', 'h4', 'img', 'btn') for it in intro):
        blocks.append(section(None, intro, n)); n += 1
    cur, h2 = [], None
    for it in items[first_h2:]:
        if it[0] == 'h1': continue
        if it[0] == 'h2':
            if h2 is not None or cur: blocks.append(section(h2, cur, n)); n += 1
            h2, cur = it[1], []
        else:
            if it[0] == 'img' and it[1] == hero_img[0]: continue
            cur.append(it)
    if h2 is not None or cur: blocks.append(section(h2, cur, n))
    if extra_main: blocks.append(extra_main)
    if form or contact: blocks.append(contact_block(*(contact or ())))
    main = '\n\n'.join(b for b in blocks if b)
    h1_text = re.sub(r'\s+', ' ', LINK.sub(lambda m: m.group(1), h1)).strip()
    build(name, path, main, f'New {path} in the Cigala Cycling design: live H1, H2s, copy and images kept.', h1=h1_text,
          h2_changes=h2_changes, extra_css=GCSS)

if __name__ == '__main__':
    COUNTRY = ('cycling-coach-uk', 'cycling-coach-usa', 'cycling-coach-canada', 'nutrition')   # built by build_coaching_country.py / build_coaching_nutrition.py
    for name in (sys.argv[1:] or [p for p in PAGES if p not in COUNTRY]):
        assert name not in COUNTRY, 'built by its own script: ' + name
        build_page(name)
