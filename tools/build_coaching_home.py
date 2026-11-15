"""Build the Coaching homepage preview: coachingpages/home.html

Approved by Matteo, 15 Nov 2026: layout, new short copy, Algarve photo, menu. Facts strip: 28 years of racing, 200+ race victories.

Same design system as the Tours homepage (survey/NfmCmGsjq4LL9bTAi38NXN/index.html): its <style> block is reused
as-is and coaching-only rules are added after it.
SEO (CLAUDE.md): the live title, meta, H1 and every live H2 keep their exact wording; all live copy is kept.
New headings are H3 or lower. Links go to the live pages until staging is built.
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
    if not os.path.exists(dst): shutil.copy(ROOT + 'coaching/webp/' + hits[0], dst)
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
MATTEO = conv('survey/NfmCmGsjq4LL9bTAi38NXN/matteo-white.png', 'matteo')
I = {
    'hero': img('imgi_21_ZtFBdo0p', 'hero'),
    'cyc': img('imgi_23_gd4FHBmB', 'cycling-coaching'),
    'tri': img('imgi_24__E7-jKP0', 'triathlon-coaching'),
    'offer': img('imgi_25_F42ZwHhq', 'what-we-offer'),
    'retail': img('imgi_40_0eNt09UI', 'retail'),
    'decade': img('imgi_41_BuSQtzIz', 'over-a-decade'),
    'cta': img('imgi_21_Lu1whOJ', 'cta'),
}

# ---------- destinations (live cards, now linked to the Tours destination pages) ----------
DEST = [  # live H4 wording, image, Tours page
    ('THE Algarve, PORTUGAL', conv('tourspages/img/dest-portugal.jpg', 'dest-algarve', 900), '/destinations/algarve/'),  # live reused the Cyprus photo
    ('LAKE GARDA, ITALY', img('imgi_27_iSz7efyZ', 'dest-lake-garda'), '/destinations/lake-garda/'),
    ('ITALIAN ALPS', img('imgi_28_c86-CyF3', 'dest-italian-alps'), '/destinations/alps-dolomites/'),
    ('DOLOMITES, ITALY', img('imgi_29_MfgBeBTZ', 'dest-dolomites'), '/destinations/alps-dolomites/'),
    ('LAKE COMO, ITALY', img('RgwYLfqonxRK', 'dest-lake-como'), '/destinations/lake-como/'),
    ('TUSCANY, ITALY', img('imgi_31_5DzKbhi4', 'dest-tuscany'), '/destinations/tuscany/'),
    ('PUGLIA, ITALY', img('imgi_32_qpHml-Jf', 'dest-puglia'), '/destinations/puglia/'),
    ('SICILY, ITALY', img('imgi_33_0SfKgJK4', 'dest-sicily'), '/destinations/sicily/'),
    ('FRENCH ALPS, FRANCE', img('x_xNJZ-zsEc', 'dest-french-alps'), '/destinations/french-alps/'),
    ('BALEARIC ISLANDS, SPAIN', img('eimEMuSmvmfm', 'dest-balearic-islands'), '/destinations/mallorca/'),
    ('COSTA BLANCA, SPAIN', img('imgi_36__F7ZRc5t', 'dest-costa-blanca'), '/destinations/costa-blanca/'),
    ('SLOVENIA', img('imgi_37_WCsbGGZh', 'dest-slovenia'), '/destinations/slovenia/'),
    ('CYPRUS', img('imgi_38_pzWP7-BV', 'dest-cyprus'), '/destinations/cyprus/'),
    ('CROATIA', img('imgi_39_I1VfzQrq', 'dest-croatia'), '/destinations/croatia/'),
    ('IRELAND', conv('tourspages/img/dest-ireland.jpg', 'dest-ireland', 900), '/destinations/ireland/'),  # live H2 "IRELAND"
]
def place(t):
    t = t.replace('THE Algarve', 'The Algarve')
    return t.title() if t.isupper() or t.startswith('The') else t
dest_cards = '\n      '.join(
    f'<a class="dest" href="{T}{u}" {EXT}><img src="{im}" alt="Cycling in {E(place(t))}" loading="lazy" width="400" height="300">'
    + (f'<h2 class="dest-h">{E(t)}</h2>' if t == 'IRELAND' else f'<h4 class="dest-h">{E(t)}</h4>') + '</a>'
    for t, im, u in DEST)

LOGOS = [  # live "As seen in" logos with their live alt text
    ('imgi_4_wHe4MESD', 'logo-red-bull'), ('imgi_6_6_MxiOhd', 'logo-stickybottle'), ('unnamed-87.png', 'logo-zwift'),
    ('unnamed-86.png', 'logo-trainingpeaks'), ('unnamed-84.png', 'logo-cycling-ireland'), ('unnamed-85.png', 'logo-vekta'),
]
alts = {i['src'].split('/uploads/')[1]: i['alt'] for i in live['images'] if i['src']}
def alt_of(key): return [a for u, a in alts.items() if key in u][0]
logos = ''.join(f'<span><img src="{img(k, n)}" alt="{E(alt_of(k))}" loading="lazy"></span>' for k, n in LOGOS)

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
  </div></div>
</footer>'''

MAIN = f'''<div class="hero">
  <img src="{I['hero']}" alt="Four Cigala Cycling riders climbing together in team kit" width="1600" height="1082">
  <div class="in">
    <h2 class="eyebrow-h">#TrainSmarterRideFaster</h2>
    <h1>Premium Cycling &amp; Triathlon Coaching</h1>
    <p class="lede">Personalised training plans, expert feedback and support from Head Coach Matteo Cigala, on TrainingPeaks and Vekta.</p>
    <div class="ctas">
      <a class="btn btn-go" href="{C}/individual-packages/" {EXT}>Cycling coaching →</a>
      <a class="btn btn-ghost" href="{C}/tri-individual-packages/" {EXT}>Triathlon coaching</a>
    </div>
  </div>
</div>

<div class="in stats-wrap">
  <div class="stats">
    <div class="stat"><div class="n">28</div><div class="l">Years of racing</div></div>
    <div class="stat"><div class="n">200+</div><div class="l">Race victories</div></div>
    <div class="stat"><div class="n">1-to-1</div><div class="l">Sessions in Wicklow</div></div>
    <div class="stat"><div class="n">Worldwide</div><div class="l">Remote coaching</div></div>
  </div>
</div>

<section id="coaching">
  <div class="in">
    <div class="head"><div>
      <div class="eyebrow">Cycling &amp; triathlon</div>
      <h2>ITALIAN PERFORMANCE COACHING FOR CYCLISTS AND TRIATHLETES WORLDWIDE</h2>
      <div class="bar"></div>
      <p class="lede">Personalised coaching from Italian Head Coach Matteo Cigala, combining over 20 years of racing experience, sports science, and professional coaching methods to help cyclists and triathletes in Ireland and worldwide improve performance and reach their goals.</p>
    </div></div>
    <div class="paths">
      <a class="path" href="{C}/individual-packages/" {EXT}>
        <img src="{I['cyc']}" alt="Cyclist riding a quiet country road" loading="lazy" width="1067" height="1600">
        <div class="tx"><h3>CYCLING COACHING</h3><p>Road, gravel and Gran Fondo. Individual, group and club packages.</p><span class="go">View cycling packages →</span></div>
      </a>
      <a class="path" href="{C}/tri-individual-packages/" {EXT}>
        <img src="{I['tri']}" alt="Triathlete standing by a lake at sunrise" loading="lazy" width="1600" height="1200">
        <div class="tx"><h3>triathlon COACHING</h3><p>Swim, bike and run, from Sprint to Ironman.</p><span class="go">View triathlon packages →</span></div>
      </a>
    </div>
  </div>
</section>

<section class="offer">
  <div class="in split">
    <div class="photo"><img src="{I['offer']}" alt="Cyclist finishing the Gran Fondo Strade Bianche in Siena" loading="lazy" width="1600" height="1066"></div>
    <div>
      <div class="eyebrow">Why Cigala Cycling</div>
      <h3 class="h-sec">WHAT WE OFFER</h3>
      <div class="bar"></div>
      <p class="first">Cigala Cycling provides premium cycling and triathlon coaching for all levels of cyclist, from leisure to professional.<br>
No matter where you are in the world, we coach remotely in different countries, developing customised coaching plans to suit your needs.</p>
      <p>Cigala Cycling was founded by Italian Head Coach Matteo Cigala, that with over 20 years experience in cycling, hundreds of victories in his name and a Diploma in Science and Sport, had a vision of connecting Ireland to the Italian cycling scene, bringing the most advanced and up-to date coaching through his continuous collaboration with Italian professional cyclists and coaches.</p>
      <p>With Cigala Cycling Tours we also hold Bike Tours all over Europe such as Lake Garda in Italy, the Algarve in Portugal and in the Italian Alps, French Alps, Pyrenees, Croatia and much more</p>
      <div class="ctas"><a class="btn btn-ghost" href="{C}/coaching-vision/" {EXT}>Our coaching vision →</a></div>
    </div>
  </div>
</section>

<section class="matteo">
  <div class="in split flip">
    <div>
      <div class="eyebrow">Meet your coach</div>
      <h3 class="h-sec">MATTEO CIGALA</h3>
      <div class="bar"></div>
      <p class="role">Head Coach &amp; Tours Director · 28 years in cycling</p>
      <ul class="creds">
        <li>European Road Champion Gran Fondo</li>
        <li>UCI Gran Fondo Vice World Champion</li>
        <li>UCI Gravel Vice World Champion</li>
        <li>Italian Gravel Champion</li>
      </ul>
      <div class="ctas"><a class="btn btn-ghost" href="{C}/about/" {EXT}>About Matteo →</a><a class="arrow-link" href="{C}/testimonials/" {EXT}>Read our testimonials →</a></div>
    </div>
    <div class="photo"><img src="{MATTEO}" alt="Matteo Cigala, Head Coach, in the white Cigala Cycling jersey" loading="lazy"></div>
  </div>
</section>

<section id="tours">
  <div class="in">
    <div class="head">
      <div>
        <div class="eyebrow">Ride with us</div>
        <h3 class="h-sec">CYCLING TOURS</h3>
        <div class="bar"></div>
        <p class="lede">With the partner company, Cigala Cycling Tours, we have selected the most beautiful cycling locations in Europe with a rich heritage, local culture and cuisine and combined them with amazing cycling routes to ensure that your vacation will be truly unforgettable.</p>
      </div>
      <a class="arrow-link" href="{T}/" {EXT}>Visit Cigala Cycling Tours →</a>
    </div>
    <div class="dests">
      {dest_cards}
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="band">
      <img src="{I['retail']}" alt="Cyclist training on an indoor smart trainer in a garage" loading="lazy" width="1600" height="872">
      <div class="tx">
        <div class="eyebrow eb-pill"><span></span>Cigala Cycling Retail</div>
        <h2>SUPPLIERS OF PREMIUM BRANDS</h2>
        <div class="bar"></div>
        <div class="ctas"><h3 class="btn-h"><a class="btn btn-go" href="{R}" {EXT}>VISIT OUR RETAIL SITE</a></h3></div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="in decade">
    <img src="{I['decade']}" alt="Over a decade of dedication, expertise and results: athletes coached by Cigala Cycling" loading="lazy" width="1000" height="562">
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Press &amp; partners</div><h2>AS SEEN IN</h2><div class="bar"></div></div></div>
    <div class="logos seen">{logos}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="band band-cta">
      <img src="{I['cta']}" alt="Cyclists riding below the Tre Cime di Lavaredo peaks" loading="lazy" width="1367" height="1492">
      <div class="tx">
        <h3 class="h-sec">START WORKING WITH MATTEO</h3>
        <div class="bar"></div>
        <p class="lede">Choose a coaching package, or get in touch and we'll help you find the right one.</p>
        <div class="ctas"><a class="btn btn-go" href="{C}/individual-packages/" {EXT}>Find your package →</a><a class="btn btn-ghost" href="{C}/contact/" {EXT}>Contact us</a></div>
      </div>
    </div>
  </div>
</section>'''

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
@media (prefers-reduced-motion: reduce) { .path img, .dest img { transition: none; } .path:hover img, .dest:hover img { transform: none; } }
</style>'''

JS = '''<script>
document.querySelectorAll('.dd').forEach(function (d) {
  var b = d.querySelector('.dd-btn');
  b.addEventListener('click', function () { var o = d.classList.toggle('open'); b.setAttribute('aria-expanded', o); });
  d.addEventListener('focusout', function (e) { if (!d.contains(e.relatedTarget)) { d.classList.remove('open'); b.setAttribute('aria-expanded', 'false'); } });
});
</script>'''

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
<div class="topo" aria-hidden="true"></div>
<div class="page">
<div class="ribbon"><div class="in"><b>Preview</b><span>New Coaching homepage in the Cigala Cycling brand. Copy, H1 and H2s are the live ones; links go to the live pages until staging is built.</span></div></div>
{HEADER}
{MAIN}
{FOOTER}
</div>
{JS}
</body></html>
'''
open(OUT + 'home.html', 'w').write(page)

# ---------- SEO self-check against the live page ----------
h1 = re.findall(r'<h1[^>]*>(.*?)</h1>', page, re.S)
h2 = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<h2[^>]*>(.*?)</h2>', page, re.S)]
assert [html.unescape(x) for x in h1] == live['h1'], h1
missing = [x for x in live['h2'] if x not in h2]
extra = [x for x in h2 if x not in live['h2']]
assert not missing and not extra, (missing, extra)
assert all(' alt="' in t for t in re.findall(r'<img\b[^>]*>', page))
print('wrote coachingpages/home.html', len(page), 'bytes; H1 and all', len(live['h2']), 'live H2s match')
