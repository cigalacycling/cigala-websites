"""Shared parts of the Coaching page previews (coachingpages/*.html): design system, header, footer, images, SEO check.

Same design system as the Tours homepage (survey/NfmCmGsjq4LL9bTAi38NXN/index.html): its <style> block is reused
as-is and coaching rules are added after it. Links go to the live pages until staging is built.
Images: WebP q90 from coaching/webp/ (extracted from live), copied into coachingpages/img/.
"""
import os, re, json, html, shutil
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
OUT = ROOT + 'coachingpages/'
os.makedirs(OUT + 'img', exist_ok=True)
C = 'https://coaching.cigalacycling.com'
T = 'https://tours.cigalacycling.com'
R = 'https://retail.cigalacycling.com/'
SKOOL = 'https://www.skool.com/cigala-cycling-collective-1115'
EXT = 'target="_blank" rel="noopener"'
E = lambda x: html.escape(x, quote=True)
live = {r['url']: r for r in json.load(open(ROOT + 'coaching/baseline.json'))}[C + '/']

# ---------- images ----------
WEBP = {o['url'].split('/uploads/')[1]: o['webp'] for o in json.load(open(ROOT + 'coaching/images.json')) if o.get('webp')}
def img(key, name):
    """key: unique part of the uploads path; copied to img/<name>.webp"""
    hits = [w for u, w in WEBP.items() if key in u]
    assert len(hits) == 1, (key, hits)
    dst = f'{OUT}img/{name}.webp'
    shutil.copy(ROOT + 'coaching/webp/' + hits[0], dst)  # always refresh, so a changed key never leaves a stale file
    return f'img/{name}.webp'
def conv(src, name, size=None):
    dst = f'{OUT}img/{name}.webp'
    if not os.path.exists(dst):
        im = Image.open(ROOT + src)
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if size: im.thumbnail((size, size), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=90, method=6)
    return f'img/{name}.webp'

LOGO = img('ccCoachingLogo.png', 'logo')
# ---------- menu ----------
def a(u, t): return f'<a href="{u}" {EXT}>{t}</a>'
CYC = [(C + '/coaching-vision/', 'Coaching Vision'), (C + '/individual-packages/', 'Individual Packages'),
       (C + '/group-club-packages/', 'Group &amp; Club Packages'), (C + '/book-1-on-1-session/', 'Book a 1-to-1 Session'), (SKOOL, 'Community')]
TRI = [(C + '/about2/', 'About Triathlon Coaching'), (C + '/tri-individual-packages/', 'Individual Packages'),
       (C + '/group-club-packages/', 'Group &amp; Club Packages'), (SKOOL, 'Community')]
SERV = [(C + '/testing/', 'INSCYD Testing'), (C + '/nutrition/', 'Nutrition'), (C + '/bike-fitting/', 'Bike Fit'),
        (C + '/talent-scout/', 'Talent Programme'), (C + '/club-talk/', 'Club Talk')]
def dd(label, items):
    return (f'<div class="dd"><button type="button" class="dd-btn" aria-expanded="false" aria-haspopup="true">{label} <span aria-hidden="true">▾</span></button>'
            f'<div class="dd-menu">{"".join(a(u, t) for u, t in items)}</div></div>')
def mob(label, items):
    return f'<div class="mgrp">{label}</div>' + ''.join(a(u, t) for u, t in items)

HEADER = f'''<header class="nav">
  <div class="in">
    <a class="brand" href="{C}/" {EXT}><img src="{LOGO}" alt="Cigala Cycling Coaching home" width="58" height="58"></a>
    <nav class="menu" aria-label="Main">
      {a(C + '/about/', 'About')}
      {dd('Cycling', CYC)}
      {dd('Triathlon', TRI)}
      {dd('Services', SERV)}
      {a(C + '/testimonials/', 'Testimonials')}
      {a(C + '/blog/', 'Blog')}
      {a(T + '/', 'Bike Tours')}
      {a(R, 'Shop')}
      {a(C + '/contact/', 'Contact')}
    </nav>
    <a class="btn btn-go" href="{C}/individual-packages/" {EXT}>Find Your Package</a>
    <details class="burger" id="menu-mobile">
      <summary>Menu</summary>
      <nav aria-label="Main (mobile)">
        {a(C + '/', 'Home')}{a(C + '/about/', 'About')}
        {mob('Cycling', CYC)}
        {mob('Triathlon', TRI)}
        {mob('Services', SERV)}
        <div class="mgrp">More</div>{a(C + '/testimonials/', 'Testimonials')}{a(C + '/blog/', 'Blog')}{a(T + '/', 'Bike Tours')}{a(R, 'Shop')}{a(C + '/contact/', 'Contact')}
      </nav>
    </details>
  </div>
</header>'''

def li(u, t): return f'<li>{a(u, t)}</li>'
FOOTER = f'''<footer>
  <div class="in fcols">
    <div>
      <a class="brand brand-lg" href="{C}/" {EXT}><img src="{LOGO}" alt="Cigala Cycling Coaching" width="76" height="76"></a>
      <h2 class="tag-line">Cycling &amp; Triathlon Coaching - Bike Tours - Retail</h2>
      <h3 class="tag-sub">#TrainSmarterRideFaster</h3>
      <ul class="contact">
        <li><a href="mailto:info@cigalacycling.com">info@cigalacycling.com</a></li>
        <li><a href="tel:+35340478107">+353 404 78107</a></li>
      </ul>
    </div>
    <div><h4>Cycling</h4><ul>{''.join(li(u, t) for u, t in CYC)}</ul></div>
    <div><h4>Triathlon</h4><ul>{''.join(li(u, t) for u, t in TRI)}</ul>
      <h4 class="mt">Services</h4><ul>{''.join(li(u, t) for u, t in SERV)}</ul></div>
    <div><h4>International Coaching</h4>
      <ul class="intl">
        <li><h2><a href="{C}/cycling-coach-uk/" {EXT}>Cycling Coach UK</a></h2></li>
        <li><h2><a href="{C}/cycling-coach-usa/" {EXT}>Cycling Coach USA</a></h2></li>
        <li><h2><a href="{C}/cycling-coach-canada/" {EXT}>Cycling Coach Canada</a></h2></li>
        <li><h2><a href="{C}/preparatore-di-ciclismo-italia/" {EXT}>Preparatore di Ciclismo Italia</a></h2></li>
      </ul>
      <h4 class="mt">Cigala Cycling</h4>
      <ul>{li(C + '/', 'Home')}{li(C + '/about/', 'About')}{li(C + '/testimonials/', 'Testimonials')}{li(C + '/blog/', 'Blog')}{li(T + '/', 'Bike Tours')}{li(R, 'Shop')}{li(C + '/contact/', 'Contact')}</ul>
    </div>
  </div>
  <div class="in social">
    {a('https://www.instagram.com/cigalacycling/', 'Instagram')}{a('https://www.facebook.com/CigalaCycling/', 'Facebook')}{a('https://www.youtube.com/@cigalacycling', 'YouTube')}{a('http://tiktok.com/@cigalacycling', 'TikTok')}{a('https://x.com/CigalaCycling', 'X')}{a('https://www.threads.com/@cigalacycling', 'Threads')}{a('https://wa.me/message/WVBRO6XAMQMCH1', 'WhatsApp')}
  </div>
  <div class="legal"><div class="in">
    <span>© 2026, Cigala Cycling Ltd</span>
    <span>VAT No: IE 3699893CH | Company Registration No: 675577</span>
    {a(C + '/terms-conditions/', 'Terms &amp; Conditions')}
    {a(C + '/privacy-policy/', 'Privacy Policy')}
  </div></div>
</footer>'''

# ---------- CSS: Tours design system + coaching additions ----------
SRC = open(ROOT + 'survey/NfmCmGsjq4LL9bTAi38NXN/index.html').read()
BASE = re.search(r'<style>\n/\* Cigala Cycling kit.*?</style>', SRC, re.S).group(0)
BASE = BASE.replace('url(topo-background.svg) center / cover no-repeat', 'url(img/topo-background-tile.svg) top center / auto 3000px repeat-y')
BASE = BASE.replace('rgba(8,9,10,.3), rgba(8,9,10,.3)', 'rgba(8,9,10,.6), rgba(8,9,10,.6)')  # BRAND.md: 60% dim
shutil.copy(ROOT + 'bk/up/topo-background-tile.svg', OUT + 'img/topo-background-tile.svg')
CSS = '''<style>
/* ---- coaching homepage additions ---- */
.eyebrow { color: var(--red-text, #ff3d33); }
.hero .eyebrow-h { font: 600 12px/1.4 var(--body); letter-spacing: .14em; text-transform: none; color: #fff; display: inline-flex; align-items: center; gap: 8px;
  background: rgba(8,9,10,.7); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 12px; margin: 0 0 18px; }
.hero .eyebrow-h::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--red); }
.hero h1 { max-width: 14ch; }
.hero .lede { max-width: 54ch; }
.stat .n { font-size: clamp(28px, 3.4vw, 44px); }
.h-sec { font-size: clamp(30px, 4.6vw, 52px); }
.head h2 { max-width: 24ch; }
.paths { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.path { position: relative; display: flex; flex-direction: column; justify-content: flex-end; min-height: 420px; border-radius: var(--r); overflow: hidden; text-decoration: none; border: 1px solid var(--border); isolation: isolate; }
.path img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .5s ease; }
.path::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(180deg, rgba(8,9,10,0) 30%, rgba(8,9,10,.75) 62%, rgba(8,9,10,.96) 100%); }
.path:hover img { transform: scale(1.04); }
.path:hover { border-color: rgba(0,154,68,.6); }
.path .tx { padding: 26px; }
.path h3 { font-size: clamp(28px, 3vw, 38px); }
.path p { margin: 8px 0 14px; color: var(--text-2); font-size: 14.5px; }
.path .go { font-size: 14px; font-weight: 600; color: var(--green-text); }
.offer .photo { aspect-ratio: 4 / 5; }
.offer p { margin: 0 0 14px; max-width: 62ch; }
.offer .first { margin-top: 16px; }
.matteo .photo img { width: auto; max-width: 92%; max-height: 100%; }
.matteo .role { color: var(--text); font-weight: 600; margin: 16px 0 0; }
.matteo .ctas { align-items: center; gap: 16px; }
.dests { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 200px), 1fr)); gap: 12px; }
.dest { position: relative; display: flex; align-items: flex-end; aspect-ratio: 4 / 3; border-radius: 10px; overflow: hidden; border: 1px solid var(--border); text-decoration: none; isolation: isolate; }
.dest img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .5s ease; }
.dest::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(180deg, rgba(8,9,10,0) 35%, rgba(8,9,10,.9) 100%); }
.dest:hover img { transform: scale(1.05); }
.dest:hover { border-color: rgba(0,154,68,.6); }
.dest-h { margin: 0; padding: 12px 14px; font: 400 18px/1.1 var(--head); letter-spacing: .02em; text-transform: uppercase; color: var(--text); }
.eb-pill { display: inline-flex; align-items: center; gap: 8px; color: #fff; background: rgba(8,9,10,.7); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 12px; margin-bottom: 18px; }
.eb-pill span { width: 7px; height: 7px; border-radius: 50%; background: var(--red); }
.btn-h { margin: 0; font: inherit; text-transform: none; letter-spacing: normal; }
.band .tx { min-height: 360px; display: flex; flex-direction: column; justify-content: center; align-items: flex-start; }
.decade img { width: 100%; height: auto; max-width: 1000px; margin: 0 auto; border-radius: var(--r); border: 1px solid var(--border); }
.seen { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; margin: 0; }
.seen span { width: auto; height: 96px; }
.seen img { max-height: 64px; max-width: 100%; object-fit: contain; }
.band-cta::after { background: linear-gradient(90deg, rgba(8,9,10,.94) 0%, rgba(8,9,10,.75) 50%, rgba(8,9,10,.2) 100%); }
.band-cta > img { object-position: center 30%; }
.dd { position: relative; }
.dd-btn { font: 600 12.5px var(--body); letter-spacing: .04em; text-transform: uppercase; color: var(--text-2); background: none; border: 0; padding: 8px 10px; border-radius: 6px; cursor: pointer; }
.dd-btn:hover, .dd:focus-within .dd-btn { color: #fff; background: var(--wash); }
.dd-menu { position: absolute; top: 100%; left: 0; min-width: 230px; display: none; padding: 8px; background: var(--panel-solid); border: 1px solid var(--border-strong); border-radius: 10px; box-shadow: 0 16px 40px rgba(0,0,0,.5); z-index: 50; }
.dd:hover .dd-menu, .dd:focus-within .dd-menu, .dd.open .dd-menu { display: grid; }
.dd-menu a { display: block; padding: 9px 12px; text-transform: none; letter-spacing: 0; font-size: 14px; }
.burger nav { max-height: calc(100svh - 80px); overflow-y: auto; }
.burger .mgrp { margin-top: 14px; font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--red-text, #ff3d33); }
.burger nav a { text-transform: none; font-size: 15px; letter-spacing: 0; }
.fcols { grid-template-columns: minmax(0, 1.4fr) repeat(3, minmax(0, 1fr)) !important; }
footer .tag-line { font-size: 22px; font-weight: 400; }
footer .tag-sub { margin: 10px 0 0; font: 600 13px var(--body); letter-spacing: .06em; text-transform: none; color: var(--green-text); }
footer .contact { margin-top: 16px; }
footer .mt { margin-top: 22px; }
footer .intl h2 { margin: 0; font: 400 14px/1.5 var(--body); text-transform: none; letter-spacing: 0; }
footer .intl h2 a { color: var(--text-2); text-decoration: none; }
footer .intl h2 a:hover { color: #fff; }
footer .in.social { display: flex; flex-wrap: wrap; gap: 8px; padding-bottom: 24px; }
.social a { font-size: 12.5px; font-weight: 600; text-decoration: none; color: var(--text-2); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 12px; }
.social a:hover { color: #fff; border-color: var(--green); }
@media (max-width: 1080px) { .fcols { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important; } .fcols > div:first-child { grid-column: 1 / -1; } }
@media (max-width: 900px) { .matteo .photo { max-width: 520px; width: 100%; } .seen { grid-template-columns: repeat(3, minmax(0, 1fr)); } .offer .photo { aspect-ratio: 16 / 10; } }
@media (max-width: 640px) {
  .paths { grid-template-columns: minmax(0, 1fr); }
  .path { min-height: 340px; }
  .dests { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
  .dest-h { font-size: 16px; padding: 10px; }
  .seen { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .fcols { grid-template-columns: minmax(0, 1fr) !important; }
  .band-cta::after { background: linear-gradient(180deg, rgba(8,9,10,.6), rgba(8,9,10,.94)); }
}
/* ---- menu: same as cigalacycling.com (brand.css): hover = green word + 2px green line, current page = red line ---- */
.nav .in { position: relative; }
.menu a, .dd-btn { border-radius: 0; box-shadow: inset 0 0 0 var(--green); transition: color .15s, box-shadow .15s; }
.menu a:hover, .menu a:active, .dd-btn:hover, .dd:focus-within .dd-btn, .dd.open .dd-btn { color: var(--green-text); background: none; box-shadow: inset 0 -2px 0 var(--green); }
.menu a[aria-current="page"], .dd-btn.is-current { color: var(--text); box-shadow: inset 0 -2px 0 var(--red); }
.dd-menu a { border-radius: 0; color: var(--text-2); transition: color .15s, box-shadow .15s; }
.dd-menu a:hover, .dd-menu a:active { color: var(--green-text); background: none; box-shadow: inset 2px 0 0 var(--green); }
.dd-menu a[aria-current="page"] { color: var(--text); box-shadow: inset 2px 0 0 var(--red); }
.burger nav a { transition: color .15s; }
.burger nav a:hover, .burger nav a:active { color: var(--green-text); }
.burger nav a[aria-current="page"] { color: var(--text); box-shadow: inset 3px 0 0 var(--red); padding-left: 12px; }
/* ---- footer links: green-text on hover, no underline (Matteo, all sites, 15 Nov) ---- */
footer a { text-decoration: none; transition: color .15s, border-color .15s; }
footer a:hover, footer ul a:hover, footer .intl h2 a:hover, .legal a:hover, footer .social a:hover { color: var(--green-text); text-decoration: none; }
@media (prefers-reduced-motion: reduce) { .path img, .dest img { transition: none; } .path:hover img, .dest:hover img { transform: none; } }
</style>'''

JS = '''<script>
document.querySelectorAll('.dd').forEach(function (d) {
  var b = d.querySelector('.dd-btn');
  b.addEventListener('click', function () { var o = d.classList.toggle('open'); b.setAttribute('aria-expanded', o); });
  d.addEventListener('focusout', function (e) { if (!d.contains(e.relatedTarget)) { d.classList.remove('open'); b.setAttribute('aria-expanded', 'false'); } });
});
</script>'''


LIVE = {r['url']: r for r in json.load(open(ROOT + 'coaching/baseline.json'))}
ALTS = {}
for _r in LIVE.values():
    for _i in _r.get('images') or []:
        if _i['src'] and _i['alt']: ALTS.setdefault(_i['src'].split('/uploads/')[-1], _i['alt'])

def live_alt(key):
    """Live alt text for an image whose uploads path contains key."""
    hits = {a for u, a in ALTS.items() if key in u}
    assert len(hits) == 1, (key, hits)
    return hits.pop()

def build(name, path, main, ribbon, h1=None, h2_changes=None, extra_css='', extra_js='', new_page=None):
    """Write coachingpages/<name>.html and check it against the live page at <path>.
    h1: the approved H1 when it differs from live (SEO-DECISIONS.md). h2_changes: {'drop': [...], 'add': [...]} approved H2 changes."""
    # new_page: {'title', 'meta'} for a page that does not exist on live yet (no H2s to keep)
    live = LIVE[C + path] if not new_page else {'title': new_page['title'], 'meta_description': new_page['meta'], 'h1': [h1], 'h2': None}
    page = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(live['title'])}</title>
<meta name="description" content="{E(live['meta_description'])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="icon" href="{LOGO}">
</head><body>
{BASE}
{CSS}
{extra_css}
<div class="topo" aria-hidden="true"></div>
<div class="page">
<div class="ribbon"><div class="in"><b>Preview</b><span>{E(ribbon)}</span></div></div>
{HEADER}
{main}
{FOOTER}
</div>
{JS}{extra_js}
</body></html>
'''
    open(OUT + name + '.html', 'w').write(page)
    want_h1 = [h1] if h1 else live['h1'][:1]
    got_h1 = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<h1[^>]*>(.*?)</h1>', page, re.S)]
    assert got_h1 == want_h1, (got_h1, want_h1)
    h2 = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<h2[^>]*>(.*?)</h2>', page, re.S)]
    ch = h2_changes or {}
    if live['h2'] is None: live = dict(live, h2=[x for x in h2])   # new page: nothing on live to keep
    want = [x for x in live['h2'] if x not in ch.get('drop', [])] + ch.get('add', [])
    missing = sorted({x for x in want if x not in h2}); extra = sorted({x for x in h2 if x not in want})
    assert not missing and not extra, ('H2 missing', missing, 'extra', extra)
    bad = [t for t in re.findall(r'<img\b[^>]*>', page) if ' alt="' not in t]
    assert not bad, bad
    print(f'wrote coachingpages/{name}.html', len(page), 'bytes; H1 ok;', len(set(want)), 'H2s match live')
    return page

