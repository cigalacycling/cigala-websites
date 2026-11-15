"""Shared parts of the Coaching page previews (coachingpages/*.html): design system, header, footer, images, SEO check.

Same design system as the Tours homepage (survey/NfmCmGsjq4LL9bTAi38NXN/index.html): its <style> block is reused
as-is and coaching rules are added after it. Links go to the live pages until staging is built.
Images: WebP q90 from coaching/webp/ (extracted from live), copied into coachingpages/img/.
"""
import os, re, json, html, shutil
from PIL import Image
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shared', 'social'))
from social import social_row, SOCIAL_CSS   # shared footer icon row (Matteo, all sites)

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
# Footer: same layout as cigalacycling.com (logo + tagline, two link columns, contact), Matteo 15 Nov: "less busy".
# The four international pages keep their footer links (and live H2 wording) for Google, but sit in a small
# "International coaching" toggle in the bottom row instead of a visible column. Closed <details> content is still in the HTML.
SITE = [(C + '/about/', 'About'), (C + '/testimonials/', 'Testimonials'), (C + '/blog/', 'Blog'), (T + '/', 'Bike Tours'), (R, 'Retail Store'), (C + '/contact/', 'Contact')]
COACH = [(C + '/individual-packages/', 'Cycling Packages'), (C + '/tri-individual-packages/', 'Triathlon Packages'), (C + '/group-club-packages/', 'Group &amp; Club Packages'),
         (C + '/book-1-on-1-session/', 'Book a 1-to-1 Session'), (C + '/testing/', 'INSCYD Testing'), (C + '/nutrition/', 'Nutrition')]
INTL = [('/cycling-coach-uk/', 'Cycling Coach UK'), ('/cycling-coach-usa/', 'Cycling Coach USA'), ('/cycling-coach-canada/', 'Cycling Coach Canada'), ('/preparatore-di-ciclismo-italia/', 'Preparatore di Ciclismo Italia')]
GOOGLE_REVIEWS = 'https://share.google/lwboSfcuStGhX0c0p'   # Cigala Cycling Ltd Google Business Profile (shared/BUSINESS.md)
FOOTER = f'''<footer>
  <div class="in fcols">
    <div>
      <a class="brand brand-lg" href="{C}/" {EXT}><img src="{LOGO}" alt="Cigala Cycling Coaching" width="76" height="76"></a>
      <h2 class="tag-line">Cycling &amp; Triathlon Coaching - Bike Tours - Retail</h2>
    </div>
    <div><h4>Coaching</h4><ul>{''.join(li(u, t) for u, t in COACH)}</ul></div>
    <div><h4>Cigala Cycling</h4><ul>{''.join(li(u, t) for u, t in SITE)}</ul></div>
    <div><h4>Contact</h4>
      <ul>
        <li><a href="mailto:info@cigalacycling.com">info@cigalacycling.com</a></li>
        <li><a href="tel:+35340478107">+353 404 78107</a></li>
        <li>{a(GOOGLE_REVIEWS, '★ Google reviews')}</li>
      </ul>
      {social_row()}
    </div>
  </div>
  <div class="legal"><div class="in">
    <span>© 2026 Cigala Cycling Ltd · Registered in Ireland No. 675577 · VAT IE3699893CH</span>
    {a(C + '/terms-conditions/', 'Terms &amp; Conditions')}
    {a(C + '/privacy-policy/', 'Privacy Policy')}
    <details class="intl-dd"><summary>International coaching</summary>
      <ul class="intl">{''.join(f'<li><h2><a href="{C}{u}" {EXT}>{t}</a></h2></li>' for u, t in INTL)}</ul>
    </details>
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
/* ---- athlete review cards (sideways scroll) ---- */
.rv-wrap { position: relative; }
.rv-row { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(280px, calc((100% - 32px) / 3)); gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory; padding-bottom: 14px; scrollbar-width: thin; scrollbar-color: rgba(255,255,255,.2) transparent; }
.rv-row:focus-visible { outline: 2px solid var(--green); outline-offset: 4px; border-radius: 12px; }
.rv { margin: 0; scroll-snap-align: start; display: flex; flex-direction: column; gap: 14px; background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: var(--r); padding: 22px; min-width: 0; }
.rv-tag { align-self: flex-start; font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--green-text); background: var(--green-wash); border-radius: 999px; padding: 4px 10px; }
.rv blockquote { margin: 0; padding: 0; border: 0; font-style: normal; font-size: 15px; line-height: 1.6; color: var(--text-2); }
.rv figcaption { font-style: normal; margin-top: auto; padding-top: 14px; border-top: 1px solid var(--border); font-size: 14px; }
.rv figcaption b { display: block; color: var(--text); }
.rv figcaption span { color: var(--text-3); font-size: 13px; }
.rv-nav { display: flex; gap: 8px; justify-content: flex-end; margin-top: 6px; }
.rv-btn { width: 40px; height: 40px; border-radius: 50%; border: 1px solid var(--border-strong); background: var(--panel-solid); color: var(--text); font-size: 16px; cursor: pointer; }
.rv-btn:hover { border-color: var(--green); color: var(--green-text); }
.rv-links { display: flex; flex-wrap: wrap; gap: 10px 22px; align-items: center; }
@media (max-width: 900px) { .rv-row { grid-auto-columns: minmax(260px, 70%); } }
@media (max-width: 640px) { .rv-row { grid-auto-columns: 86%; } .rv-nav { display: none; } }
/* ---- shared social icon row (shared/social) ---- */
''' + SOCIAL_CSS + '''
/* ---- footer layout: as cigalacycling.com ---- */
.fcols { grid-template-columns: minmax(0, 1.3fr) repeat(3, minmax(0, 1fr)) !important; }
footer .tag-line { font-size: 22px; line-height: 1.15; margin: 14px 0 0; max-width: 24ch; }
footer ul { font-size: 14px; }
footer ul a { color: var(--text-2); }
.legal .in { align-items: center; }
.intl-dd { position: relative; }
.intl-dd summary { list-style: none; cursor: pointer; font-size: 12px; color: var(--text-3); }
.intl-dd summary::-webkit-details-marker { display: none; }
.intl-dd summary::after { content: " ▾"; }
.intl-dd[open] summary::after { content: " ▴"; }
.intl-dd summary:hover { color: var(--green-text); }
.intl-dd .intl { list-style: none; margin: 0; padding: 10px 12px; position: absolute; bottom: calc(100% + 8px); left: 0; min-width: 240px; display: grid; gap: 4px; background: var(--panel-solid); border: 1px solid var(--border-strong); border-radius: 10px; box-shadow: 0 16px 40px rgba(0,0,0,.5); z-index: 5; }
.intl-dd .intl h2 { margin: 0; font: 400 13px/1.6 var(--body); text-transform: none; letter-spacing: 0; }
.intl-dd .intl a { color: var(--text-2); text-decoration: none; }
@media (max-width: 1080px) { .fcols { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important; } .fcols > div:first-child { grid-column: 1 / -1; } }
@media (max-width: 640px) { .intl-dd .intl { left: auto; right: 0; } .fcols { grid-template-columns: minmax(0, 1fr) !important; } }
/* ---- footer links: green-text on hover, no underline (Matteo, all sites, 15 Nov) ---- */
footer a { text-decoration: none; transition: color .15s, border-color .15s; }
footer a:hover, footer ul a:hover, footer .intl h2 a:hover, .legal a:hover, footer .social a:hover { color: var(--green-text); text-decoration: none; }
/* intro text under page headings: 16px, as on cigalacycling.com (BRAND.md: intro 16px) */
.hero .lede { font-size: 16px; }
@media (prefers-reduced-motion: reduce) { .path img, .dest img { transition: none; } .path:hover img, .dest:hover img { transform: none; } }
</style>'''

JS = '''<script>
document.querySelectorAll('.dd').forEach(function (d) {
  var b = d.querySelector('.dd-btn');
  b.addEventListener('click', function () { var o = d.classList.toggle('open'); b.setAttribute('aria-expanded', o); });
  d.addEventListener('focusout', function (e) { if (!d.contains(e.relatedTarget)) { d.classList.remove('open'); b.setAttribute('aria-expanded', 'false'); } });
});
</script>'''


# ---------- athlete reviews (Matteo 15 Nov: own review cards instead of the Shapo widget; reviews chosen by Claude) ----------
# Quotes are the athletes' own words from the live Testimonials page (coaching/text/testimonials.txt); no star ratings,
# because these are testimonials, not rated reviews. The Google link goes to Matteo's Google Business Profile.
REVIEWS = [
    ('Gran Fondo Worlds qualifier', 'With his expertise, support, and personalized approach, I have achieved my goal of qualifying for the UCI Granfondo World Championship.', 'Bernd Ondruch', 'Germany'),
    ('From couch to Haute Route, and back after heart disease', 'First time was a 9 month training plan to get me from couch (literally!) to Haute Route Pyrenees in 2017 to mark my 60th birthday. More recently, I have worked with Matteo to help me recover from heart disease and a cardiac procedure.', 'Derek Lawler', 'Kilkenny, Ireland'),
    ('Mallorca 312 in the best shape ever', 'I truly had a tailor-made plan every single week, and as a result, I showed up to the Mallorca 312 in the best shape I’ve ever been in.', 'Ward Den Hollander', 'Dublin, Ireland'),
    ('PB FTP in 7 weeks', 'After 7 weeks of following his programme, which is mainly working in Z1/2 with bits of Z3, I’ve managed to get a PB FTP of 207W.', 'Lisa Dunne', 'Al Jassra Race Team, Qatar'),
    ('+40 W FTP, +300 W sprint', 'Matteo managed to raise my FTP from 220w to 260w in less than 4 months & my sprint from 600w ish to 920w.', 'Shane Courtney', 'Tralee Manor West ibike'),
    ('All-time power PBs, around family and work', 'Matteo Cigala has been an incredible cycling coach, helping me navigate training around my family and work commitments. Thanks to his guidance, I not only reached my targets but also hit all-time personal best power numbers.', 'John Dowley', 'Carrick-on-Suir, Ireland'),
    ('From A3 to A1 and the Rás', 'I commenced the cycling season in February as an A2 and by March I had gained my first points finishing 2nd in the Lucan GP. Finally last week I achieved one of my goals for the season: I won the Connor Coombes GP.', 'Gerard Dunne', 'Navan Road Club'),
    ('16 kg lighter, fitter and happier', 'To date I’ve lost close to 16 kg thanks to Matteos coaching and support, most importantly I look forward to every session that is planned out for me.', 'Rob Kavanagh', 'Ireland'),
]
def reviews_strip():
    cards = ''.join(f'<figure class="rv"><div class="rv-tag">{E(t)}</div><blockquote>“{E(q)}”</blockquote><figcaption><b>{E(n)}</b><span>{E(w)}</span></figcaption></figure>' for t, q, n, w in REVIEWS)
    return (f'<div class="rv-wrap"><div class="rv-row" id="rv-row" tabindex="0" aria-label="Athlete reviews, scroll sideways">{cards}</div>'
            '<div class="rv-nav"><button type="button" class="rv-btn" data-d="-1" aria-label="Previous reviews">←</button><button type="button" class="rv-btn" data-d="1" aria-label="Next reviews">→</button></div></div>')
REVIEWS_JS = """<script>(function(){var r=document.getElementById('rv-row');if(!r)return;document.querySelectorAll('.rv-btn').forEach(function(b){b.addEventListener('click',function(){r.scrollBy({left:(+b.dataset.d)*r.clientWidth*0.85,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});});});})();</script>"""

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

