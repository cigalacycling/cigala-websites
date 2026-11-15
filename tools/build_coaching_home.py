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
    'cta': img('unnamed-8-1.jpg', 'matteo-worlds-silver'),
    'tours': conv('tourspages/img/home-hero.jpg', 'tours-cyprus', 1600),
}


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
    <p class="lede">World-class coaching from a former pro and European Gran Fondo Champion, for cyclists and triathletes of every level.</p>
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
    <div class="stat"><div class="n">1,000+</div><div class="l">Athletes coached worldwide</div></div>
    <div class="stat"><div class="n">Worldwide</div><div class="l">Remote coaching</div></div>
  </div>
</div>

<section id="coaching">
  <div class="in">
    <div class="head"><div>
      <div class="eyebrow">Cycling &amp; triathlon</div>
      <h2>ITALIAN PERFORMANCE COACHING FOR CYCLISTS AND TRIATHLETES WORLDWIDE</h2>
      <div class="bar"></div>
      <p class="lede">Personalised coaching from Italian Head Coach Matteo Cigala, combining almost 30 years of racing experience, sports science, and professional coaching methods to help cyclists and triathletes in Ireland and worldwide improve performance and reach their goals.</p>
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
      <p>Cigala Cycling was founded by Italian Head Coach Matteo Cigala, that with almost 30 years experience in cycling, hundreds of victories in his name and a Diploma in Science and Sport, had a vision of connecting Ireland to the Italian cycling scene, bringing the most advanced and up-to date coaching through his continuous collaboration with Italian professional cyclists and coaches.</p>
      <p>With Cigala Cycling Tours we also hold Bike Tours all over Europe such as Lake Garda in Italy, the Algarve in Portugal and in the Italian Alps, French Alps, Pyrenees, Croatia and much more</p>
      <div class="ctas"><a class="btn btn-go" href="{C}/coaching-vision/" {EXT}>Our coaching vision →</a></div>
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
        <li>200+ race wins</li>
      </ul>
      <div class="ctas"><a class="btn btn-go" href="{C}/about/" {EXT}>About Matteo →</a><a class="arrow-link" href="{C}/testimonials/" {EXT}>Read our testimonials →</a></div>
    </div>
    <div class="photo cutout"><img src="{MATTEO}" alt="Matteo Cigala, Head Coach, in the white Cigala Cycling jersey" loading="lazy"></div>
  </div>
</section>

<section id="family">
  <div class="in">
    <div class="head"><div><div class="eyebrow">The Cigala Cycling family</div><h3 class="h-sec">RIDE WITH US, SHOP WITH US</h3><div class="bar"></div></div></div>
    <div class="fam">
      <a class="card" href="{T}/" {EXT}>
        <img src="{I['tours']}" alt="Cigala Cycling Tours riders celebrating on the coast in Cyprus" loading="lazy" width="1600" height="1067">
        <div class="tx">
          <span class="k">Cigala Cycling Tours</span>
          <h3>BIKE TOURS</h3>
          <p>With the partner company, Cigala Cycling Tours, we have selected the most beautiful cycling locations in Europe with a rich heritage, local culture and cuisine and combined them with amazing cycling routes to ensure that your vacation will be truly unforgettable.</p>
          <span class="btn btn-go">Go to tours site →</span>
          <span class="host">tours.cigalacycling.com</span>
        </div>
      </a>
      <a class="card" href="{R}" {EXT}>
        <img src="{I['retail']}" alt="Cyclist training on an indoor smart trainer in a garage" loading="lazy" width="1600" height="872">
        <div class="tx">
          <span class="k">Cigala Cycling Retail</span>
          <h2>SUPPLIERS OF PREMIUM BRANDS</h2>
          <p>Cycling and triathlon products from the brands we trust, with a discount for our coached riders.</p>
          <span class="btn btn-go">Go to retail site →</span>
          <span class="host">retail.cigalacycling.com</span>
        </div>
      </a>
    </div>
  </div>
</section>

<section>
  <div class="in decade">
    <img src="{I['decade']}" alt="Over a decade of dedication, expertise and results: athletes coached by Cigala Cycling" loading="lazy" width="1000" height="562">
  </div>
</section>

<section id="reviews">
  <div class="in">
    <div class="head">
      <div><div class="eyebrow">Our athletes</div><h3 class="h-sec">WHAT OUR ATHLETES SAY</h3><div class="bar"></div></div>
      <div class="rv-links"><a class="arrow-link" href="{GOOGLE_REVIEWS}" {EXT}><span class="gstar" aria-hidden="true">★</span> Read our reviews on Google →</a><a class="arrow-link" href="{C}/testimonials/" {EXT}>All testimonials →</a></div>
    </div>
    {reviews_strip()}
  </div>
</section>

{tools_band()}

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Press &amp; partners</div><h2>AS SEEN IN</h2><div class="bar"></div></div></div>
    {seen_logos()}
  </div>
</section>

<section>
  <div class="in">
    <div class="band band-cta">
      <img src="{I['cta']}" alt="{E(live_alt('unnamed-8-1.jpg'))}" loading="lazy" width="1280" height="1600">
      <div class="tx">
        <h3 class="h-sec">START WORKING WITH MATTEO</h3>
        <div class="bar"></div>
        <p class="lede">Choose a coaching package, or get in touch and we'll help you find the right one.</p>
        <div class="ctas"><a class="btn btn-go" href="https://calendly.com/cigalacycling" {EXT}>Book a free consultation →</a><a class="btn btn-ghost" href="{C}/individual-packages/" {EXT}>See the packages</a></div>
      </div>
    </div>
  </div>
</section>'''


# Matteo 15 Nov: the four squares under the hero were plain: colour, a hover lift and a count-up
HS_CSS = """<style>
.stats-wrap { margin-top: -20px !important; }   /* Matteo 15 Nov: the squares sat too close to the hero buttons */
.stats-wrap .stat { --c: #34c46a; position: relative; transition: transform .25s, box-shadow .25s, background .25s; cursor: default; }
.stats-wrap .stat:nth-child(2) { --c: #f0bf00; } .stats-wrap .stat:nth-child(3) { --c: #ff3d33; } .stats-wrap .stat:nth-child(4) { --c: #5f86c9; }
.stats-wrap .stat::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 3px; background: var(--c); transform: scaleX(.18); transform-origin: left; transition: transform .35s; }
.stats-wrap .stat:hover { transform: translateY(-4px); box-shadow: 0 18px 40px rgba(0,0,0,.45), 0 0 0 1px var(--c); background: color-mix(in srgb, var(--c) 10%, transparent); z-index: 1; }
.stats-wrap .stat:hover::before { transform: scaleX(1); }
.stats-wrap .stat .n { transition: color .25s; }
.stats-wrap .stat:hover .n { color: var(--c); }
.stats-wrap .stat:hover .l { color: var(--text); }
</style>"""
HS_JS = """<script>(function(){var l=document.querySelectorAll('.stats-wrap .stat .n');if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
l.forEach(function(el){var m=el.textContent.match(/^([\\d,]+)(\\D*)$/);if(!m)return;var to=+m[1].replace(/,/g,''),suf=m[2],fmt=function(v){return v.toLocaleString('en-US')+suf;};el.style.minWidth=el.offsetWidth+'px';el.textContent=fmt(0);
new IntersectionObserver(function(es,ob){if(!es[0].isIntersecting)return;ob.disconnect();var t0=performance.now();(function f(t){var k=Math.min(1,(t-t0)/1500);el.textContent=fmt(Math.round(to*(1-Math.pow(1-k,3))));if(k<1)requestAnimationFrame(f);})(t0);},{threshold:.5}).observe(el);});})();</script>"""
build('home', '/', MAIN, 'New Coaching homepage in the Cigala Cycling brand. Copy, H1 and H2s are the live ones; links go to the live pages until staging is built.', extra_js=REVIEWS_JS + HS_JS, extra_css=FT_CSS + HS_CSS,
      h2_changes={'drop': ['IRELAND']})   # the hidden 'IRELAND' card heading went with the destination grid (Matteo 15 Nov: no tours grid on coaching)
