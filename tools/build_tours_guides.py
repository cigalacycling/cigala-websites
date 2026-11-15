"""Tours guides in the new design (design: tourspages/guides.html and tourspages/guide-lake-como.html).

The 37 guides are WordPress posts; their words stay in the posts. Three things change, all on Tours STAGING:
- Single post template 5104 (shows every guide): hero with the featured photo, the post title as the H1,
  then the author line (live H2 "By Tours Director Matteo Cigala", an ACF field), the excerpt and the content
  in a readable column, then the "Cigala Cycling Tours" band with links to the tours.
- Loop item 5087 (one guide card in the Guides grid): photo, author line, title (H3: one H1 per page) and
  excerpt with "Read more". Matches the homepage guide cards.
- Guides page 5030: hero (live H1 and the live intro H2), the live loop grid (all posts, newest first,
  "load more", 3 per row) and the closing band. New guides appear by themselves.
Backups of the originals: stg-tours/backup/lib-5104.json, lib-5087.json, page-5030.json.

Usage: python3 -I tools/build_tours_guides.py [--push]
CSS: GUIDES_CSS goes into the kit through stg-tours/out/list-guides-css.json (tools/build_tours_wp.py).
"""
import os, re, sys, json, copy, random, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_tours_wp import req, B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
M = json.load(open(ROOT + 'stg-tours/media-webp.json'))
from tours_img import webp
HERO = webp(8611, 2000)   # Guides hero: riders on a Dolomites road (Matteo 15 Nov: clearer than the Galibier photo)
E = lambda x: html.escape(x, quote=True)

def rid(): return ''.join(random.choice('0123456789abcdef') for _ in range(7))
def con(els, cls, **kw):
    s = {"content_width": "full", "css_classes": "cc-wrap " + cls, "flex_gap": {"unit": "px", "size": 0, "column": "0", "row": "0"},
         "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True}}
    s.update(kw)
    return {"id": rid(), "elType": "container", "settings": s, "elements": els, "isInner": False}
def w(kind, settings, cls=''):
    s = dict(settings)
    if cls: s['_css_classes'] = cls
    return {"id": rid(), "elType": "widget", "widgetType": kind, "settings": s, "elements": [], "isInner": False}
def htmlw(h, cls=''): return w('html', {'html': h}, cls)

def dyn_widgets(tid):
    """The dynamic tags of the original template (post title, ACF author line, featured image, excerpt), by widget type."""
    d = json.loads(json.load(open(ROOT + f'stg-tours/backup/lib-{tid}.json'))['meta']['_elementor_data'])
    out = {}
    def walk(xs):
        for e in xs:
            s = e.get('settings') or {}
            if isinstance(s, dict) and s.get('__dynamic__'): out.setdefault(e['widgetType'], s['__dynamic__'])
            walk(e.get('elements', []))
    walk(d)
    return out

# ---------- single post 5104 ----------
D = dyn_widgets(5104)
band_img = M['custom']
TOUR_LINKS = [('All tours', '/trips/'), ('Gran Fondo tours', '/trips/granfondo-trips/'), ('Gravel tours', '/trips/gravel-trips/'), ('Custom tours', '/trips/private-trips/')]
single = [
    con([
        w('theme-post-featured-image', {'__dynamic__': D['theme-post-featured-image'], 'image_size': 'full'}, 'cl-post-bg'),
        htmlw('<div class="cl cl-page"><div class="crumbs"><a href="/">Home</a> / <a href="/guides/">Guides</a></div>'
              '<div class="pill-eyebrow">Cycling guide</div></div>', 'cl-post-top'),
        w('theme-post-title', {'__dynamic__': D['theme-post-title'], 'header_size': 'h1'}, 'cl-post-title'),
        htmlw('<div class="cl cl-page"><div class="bar"></div></div>', 'cl-post-bar'),
    ], 'cl-post-hero'),
    con([
        w('heading', {'__dynamic__': D['heading'], 'title': '', 'header_size': 'h2'}, 'cl-post-author'),
        w('theme-post-excerpt', {'__dynamic__': D['theme-post-excerpt']}, 'cl-post-lede'),
        w('theme-post-content', {}, 'cl-post-content'),
    ], 'cl-post-body'),
    con([htmlw(f'''<div class="cl cl-page"><section><div class="in"><div class="band">
<img src="{band_img['url']}" alt="{E(band_img['alt'])}" loading="lazy">
<div class="tx"><div class="eyebrow">Ride it with us</div><h2>Cigala Cycling Tours</h2><div class="bar"></div>
<p class="lede">Europe Bike Tour Operator</p>
<div class="ctas">{''.join(f'<a class="btn {"btn-go" if i == 0 else "btn-ghost"}" href="{u}">{t}{" →" if i == 0 else ""}</a>' for i, (t, u) in enumerate(TOUR_LINKS))}</div>
</div></div></div></section></div>''')], 'cl-post-band'),
]

# ---------- loop item 5087 (guide card) ----------
L = dyn_widgets(5087)
card = [con([
    w('theme-post-featured-image', {'__dynamic__': L['theme-post-featured-image'], 'image_size': 'large', 'link_to': 'custom'}, 'cl-gcard-ph'),
    con([
        w('heading', {'__dynamic__': L['heading'], 'title': '', 'header_size': 'div'}, 'cl-gcard-by'),
        w('theme-post-title', {'__dynamic__': L['theme-post-title'], 'header_size': 'h3'}, 'cl-gcard-title'),
        w('theme-post-excerpt', {'__dynamic__': L['theme-post-excerpt'], 'excerpt_length': 22}, 'cl-gcard-ex'),
        w('button', {'__dynamic__': L['button'], 'text': 'Read more →'}, 'cl-gcard-go'),
    ], 'cl-gcard-tx', flex_direction='column'),
], 'cl-gcard', flex_direction='column')]

# ---------- Guides page 5030 ----------
page = json.loads(json.load(open(ROOT + 'stg-tours/backup/page-5030.json'))['meta']['_elementor_data'])
heads, grid = [], None
def walk(xs):
    global grid
    for e in xs:
        if e.get('widgetType') == 'heading': heads.append(e['settings'])
        if e.get('widgetType') == 'loop-grid': grid = copy.deepcopy(e)
        walk(e.get('elements', []))
walk(page)
h1 = html.unescape(re.sub(r'<[^>]+>', '', heads[0]['title'])).strip()       # live: an <h1> typed inside the H1 widget
intro = heads[1]['title'].strip()
gs = grid['settings']
for k in [k for k in gs if any(x in k for x in ('typography', 'color', 'button_', 'row_gap', 'column_gap'))]: gs.pop(k)
gs.update({'columns': 3, 'columns_tablet': 2, 'columns_mobile': 1, 'row_gap': {'unit': 'px', 'size': 16}, 'column_gap': {'unit': 'px', 'size': 16},
           'text': 'Continue reading: all guides', '_css_classes': 'cl-ggrid'})
grid['id'] = rid()
gpage = [
    con([htmlw(f'''<div class="cl cl-page"><div class="hero phero"><img src="{HERO['url']}" alt="{E(HERO['alt'])}"><div class="in">
<div class="crumbs"><a href="/">Home</a> / Guides</div>
<div class="eyebrow">Plan your trip</div>
<h1>{E(h1)}</h1>
<div class="bar"></div>
<h2 class="lede guides-intro">{E(intro)}</h2>
</div></div></div>''')], ''),
    con([grid], 'cl-guides-grid'),
    con([htmlw(f'''<div class="cl cl-page"><section><div class="in"><div class="band">
<img src="{M['cta']['url']}" alt="{E(M['cta']['alt'])}" loading="lazy">
<div class="tx"><div class="eyebrow">Ride it with us</div><p class="band-title">Ready for your next cycling adventure?</p><div class="bar"></div>
<div class="ctas"><a class="btn btn-go" href="/trips/">Explore tours →</a><a class="btn btn-ghost" href="/trips/private-trips/">Custom tours</a></div>
</div></div></div></section></div>''')], ''),
]

GUIDES_CSS = '''
/* ---- guides: single post 5104, guide cards 5087, Guides page 5030 ---- */
.e-con.cl-post-hero { position: relative; isolation: isolate; overflow: hidden; min-height: 440px; justify-content: flex-end !important; padding: 120px max(16px, calc((100% - 1200px) / 2)) 44px !important; }
.cl-post-hero > .cl-post-bg { position: absolute !important; inset: 0; z-index: -2; width: 100% !important; max-width: none !important; margin: 0 !important; }
.cl-post-hero > .cl-post-bg img { width: 100% !important; height: 100% !important; object-fit: cover; }
.cl-post-hero::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(90deg, rgba(8,9,10,.9) 0%, rgba(8,9,10,.62) 55%, rgba(8,9,10,.4) 100%), linear-gradient(180deg, rgba(8,9,10,0) 50%, rgba(8,9,10,.96) 100%); }
.cl-post-hero .cl-post-top .crumbs { margin-bottom: 14px; }
.cl-post-hero .cl-post-title .elementor-heading-title { font-family: Anton, Impact, sans-serif !important; font-weight: 400 !important; text-transform: uppercase; color: #f7f8f8 !important; font-size: clamp(38px, 6vw, 76px) !important; line-height: 1.08 !important; letter-spacing: .01em; max-width: 20ch; margin: 0; text-wrap: balance; }
.cl-post-hero .cl-post-bar .bar { margin-top: 18px; }
.e-con.cl-post-body { max-width: 860px !important; margin: 0 auto !important; padding: clamp(24px, 4vw, 44px) clamp(20px, 4vw, 44px) !important; background: linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.012)), rgba(15,16,17,.92); border: 1px solid rgba(255,255,255,.08); border-radius: 12px; position: relative; margin-top: 28px !important; }
@media (max-width: 900px) { .e-con.cl-post-body { margin: 20px 16px 0 !important; width: auto !important; max-width: none !important; } }
.cl-post-author .elementor-heading-title { font: 600 12px/1.4 Montserrat, system-ui, sans-serif !important; letter-spacing: .14em !important; text-transform: uppercase; color: #ff3d33 !important; margin: 0 0 12px !important; }
.cl-post-lede, .cl-post-lede p { font: 600 18px/1.55 Montserrat, system-ui, sans-serif !important; color: #f7f8f8 !important; margin: 0 0 18px !important; }
.cl-post-content, .cl-post-content p, .cl-post-content li, .cl-post-content figcaption { font: 400 16px/1.7 Montserrat, system-ui, sans-serif; color: #d0d6e0 !important; }   /* the old kit makes body text red */
.cl-post-content p { margin: 0 0 16px; }
.cl-post-content h2 { font-family: Anton, Impact, sans-serif !important; font-weight: 400 !important; text-transform: uppercase; color: #f7f8f8; font-size: clamp(26px, 3.4vw, 34px); line-height: 1.14 !important; letter-spacing: .01em; margin: 36px 0 14px; }
.cl-post-content h2::after { content: ""; display: block; width: 44px; height: 4px; border-radius: 2px; background: #009a44; margin-top: 10px; }
.cl-post-content h3 { font: 700 18px/1.3 Montserrat, system-ui, sans-serif; color: #f7f8f8; text-transform: none; margin: 22px 0 8px; }
.cl-post-content strong, .cl-post-content b { color: #f7f8f8; }
.cl-post-content a { color: #2bd47a; text-decoration: underline; text-underline-offset: 3px; }
.cl-post-content ul, .cl-post-content ol { margin: 0 0 18px; padding-left: 20px; display: grid; gap: 6px; }
.cl-post-content li::marker { color: #009a44; }
.cl-post-content figure { margin: 24px 0; }
.cl-post-content img { width: 100%; height: auto; border-radius: 10px; display: block; }
.cl-post-content figcaption { font-size: 13px; color: #8a8f98; margin-top: 8px; }
.cl-post-content blockquote { margin: 22px 0; padding: 4px 0 4px 18px; border-left: 3px solid #009a44; color: #f7f8f8; font-style: italic; }
.e-con.cl-post-band { padding-top: 56px !important; }
/* guide cards (loop item 5087): same look as the Coaching blog cards (title over the photo, green Read more) */
.e-con.cl-gcard { position: relative; height: 100%; display: block !important; background: #0f1011; border: 1px solid rgba(255,255,255,.08); border-radius: 14px; overflow: hidden; }
.e-con.cl-gcard:hover { border-color: rgba(0,154,68,.5); }
.cl-gcard-ph { width: 100% !important; margin: 0 !important; }
.cl-gcard-ph img { width: 100% !important; aspect-ratio: 4 / 3; height: auto !important; object-fit: cover; border-radius: 0 !important; display: block; transition: transform .5s ease; }
.e-con.cl-gcard:hover .cl-gcard-ph img { transform: scale(1.04); }
.e-con.cl-gcard-tx { position: absolute !important; left: 0; right: 0; bottom: 0; padding: 70px 18px 18px !important; gap: 6px !important; background: linear-gradient(180deg, rgba(8,9,10,0) 0%, rgba(8,9,10,.78) 45%, rgba(8,9,10,.96) 100%); }
.cl-gcard-by .elementor-heading-title { font: 600 10.5px/1.4 Montserrat, system-ui, sans-serif !important; letter-spacing: .12em !important; text-transform: uppercase; color: #ff3d33 !important; }   /* red, like the eyebrows (Matteo) */
.cl-gcard-title .elementor-heading-title, .cl-gcard-title .elementor-heading-title a { font-family: Anton, Impact, sans-serif !important; font-weight: 400 !important; text-transform: uppercase; color: #f7f8f8 !important; font-size: 21px !important; line-height: 1.14 !important; letter-spacing: .01em; text-decoration: none; }
.cl-gcard-ex { display: none !important; }
.cl-gcard-go { margin-top: 6px !important; }
.cl-gcard-go .elementor-button { background: #009a44 !important; border: 0 !important; border-radius: 8px !important; padding: 9px 16px !important; font: 600 13px Montserrat, system-ui, sans-serif !important; color: #fff !important; text-transform: none !important; box-shadow: none !important; }
.cl-gcard-go .elementor-button:hover { background: #00b350 !important; color: #fff !important; }
/* Guides page */
.e-con.cl-guides-grid { max-width: 1232px !important; margin: 0 auto !important; padding: 24px 16px 0 !important; }
.cl-ggrid .elementor-loop-container { gap: 16px !important; }
.cl-ggrid .e-loop__load-more .elementor-button { font: 600 14px Montserrat, system-ui, sans-serif !important; color: #fff !important; background: #009a44 !important; border: 0 !important; border-radius: 8px !important; padding: 12px 22px !important; text-transform: none !important; }
.cl-ggrid .e-load-more-spinner { display: none !important; }   /* Elementor shows it only while loading; its own CSS is not loaded here */
.cl-ggrid .e-loop__load-more .elementor-button:hover { background: #00b350 !important; color: #fff !important; }
html .cl h2.guides-intro { font-family: Montserrat, system-ui, sans-serif; font-weight: 400; text-transform: none; letter-spacing: 0; font-size: 17px; line-height: 1.6; color: #d0d6e0; max-width: 62ch; margin-top: 18px; }
html .cl .band-title { font-family: var(--head); text-transform: uppercase; color: var(--text); font-size: clamp(30px, 4.4vw, 48px); line-height: 1.08; margin: 0; }
'''

json.dump({'slug': 'guides-css', 'main': '', 'css': GUIDES_CSS}, open(ROOT + 'stg-tours/out/list-guides-css.json', 'w'))
out = {'lib-5104': single, 'lib-5087': card, 'page-5030': gpage}
for k, els in out.items():
    json.dump(els, open(ROOT + f'stg-tours/out/guides-{k}.json', 'w'))
print('built: single post', len(json.dumps(single)), '| card', len(json.dumps(card)), '| guides page', len(json.dumps(gpage)), '| h1', h1)

if '--push' in sys.argv:
    for k, els in out.items():
        kind, pid = k.split('-', 1)
        path = 'elementor_library' if kind == 'lib' else 'pages'
        body = {"meta": {"_elementor_data": json.dumps(els), "_elementor_edit_mode": "builder"}}
        code, r = req(f'{B}/wp/v2/{path}/{pid}', json.dumps(body).encode(), 'POST')
        print(k, code, '' if code == 200 else r[:300])
    code, r = req(f'{B}/elementor/v1/cache', method='DELETE'); print('elementor cache', code)
