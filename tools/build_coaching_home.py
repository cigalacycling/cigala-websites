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
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *

live = LIVE[C + '/']
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


build('home', '/', MAIN, 'New Coaching homepage in the Cigala Cycling brand. Copy, H1 and H2s are the live ones; links go to the live pages until staging is built.')
