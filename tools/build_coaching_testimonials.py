"""Build the Testimonials page: coachingpages/testimonials.html -> /testimonials/ (page 2844)

Every live testimonial is kept word for word with its photo and live alt text; the live H1 and H2 stay.
Layout: a short intro with links to the Case Studies and Google reviews, then the testimonials as cards in columns
(first paragraph visible, the rest opens with "Read more"; the full text is in the page for Google), then Greg
Swinand's Irish Hour Record with its photo gallery.
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
import build_coaching_generic as G

items, _ = G.parse('testimonials')
h1 = next(it[1] for it in items if it[0] == 'h1')
H1 = 'READ OUR TESTIMONIALS'   # Matteo 15 Nov: no '- WHAT PEOPLE SAY ABOUT CIGALA CYCLING'
h2i = next(i for i, it in enumerate(items) if it[0] == 'h2')
tests, cur = [], None
for it in items[:h2i]:
    if it[0] == 'img':
        cur = {'img': it, 'paras': []}; tests.append(cur)
    elif it[0] == 'p' and cur is not None:
        cur['paras'].append(it[1])
# the last paragraph of each block is the athlete's name and club
cards = ''
seen = set()
for t in tests:
    if not t['paras']: continue
    name = t['paras'][-1]; body = t['paras'][:-1]
    sig = (name, body[0][:60] if body else '')
    if sig in seen: continue          # the live page shows Keith Sharkey's testimonial twice
    seen.add(sig)
    u, alt = t['img'][1], t['img'][2]
    photo = G.pic(u, alt, 'tm-photo') if u in G.WEBP else ''
    first, more = (body[0], body[1:]) if body else ('', [])
    lines = [x for x in first.split('\n') if x.strip()]
    if not more and len(lines) > 2: first, more = '\n'.join(lines[:2]), ['\n'.join(lines[2:])]   # long single paragraphs: opening + Read more
    elif len(first) > 420 and not more:
        cut = first.rfind('. ', 0, 360) + 1 or 360; first, more = first[:cut], [first[cut:].strip()]
    more_html = ''.join(f'<p>{G.inline(x)}</p>' for x in more)
    cards += (f'<figure class="tm">{photo}<div class="rv-stars" role="img" aria-label="5 stars">★★★★★</div>'
              f'<blockquote><p>{G.inline(first)}</p>' + (f'<details><summary>Read more</summary>{more_html}</details>' if more else '') +
              f'</blockquote><figcaption>{E(name)}</figcaption></figure>')

greg = G.section(items[h2i][1], items[h2i + 1:], 1)
MAIN = f'''<section class="tm-hero">
  <div class="in tm-hero-in">
    <div>
      <div class="eyebrow eb-pill"><span class="dot"></span>Our athletes</div>
      <h1>{H1}</h1>
      <p class="tm-sub">What people say about Cigala Cycling</p>
      <p class="lede">From first-time sportive riders to national champions and a WorldTour Pro: in their own words.</p>
      <div class="ctas"><a class="btn btn-go" href="{C}/case-studies/" {EXT}>See the case studies</a><a class="btn btn-ghost" href="{GOOGLE_REVIEWS}" {EXT}><span class="gstar" aria-hidden="true">★</span> Our Google reviews</a></div>
    </div>
    <figure class="tm-hero-pic"><img src="{conv('coaching/athletes/marine-lenehan.webp', 'testimonials-marine-lenehan')}" alt="{E(live_alt('T135849.182'))}" width="832" height="1040"><figcaption>Marine Lenehan · now a WorldTour Pro</figcaption></figure>
  </div>
</section>

<section>
  <div class="in">
    <div class="tm-cols">{cards}</div>
  </div>
</section>

{greg}

<section>
  <div class="in">
    <div class="band band-cta">
      <img src="{img('unnamed-8-1.jpg', 'matteo-worlds-silver')}" alt="{E(live_alt('unnamed-8-1.jpg'))}" loading="lazy" width="1280" height="1600">
      <div class="tx">
        <h3 class="h-sec">YOUR STORY COULD BE NEXT</h3>
        <div class="bar"></div>
        <p class="lede">Tell us where you are now and where you want to be.</p>
        <div class="ctas"><a class="btn btn-go" href="https://calendly.com/cigalacycling" {EXT}>Book a free consultation →</a><a class="btn btn-ghost" href="{C}/individual-packages/" {EXT}>See the packages</a></div>
      </div>
    </div>
  </div>
</section>'''

CSS = G.GCSS + '''<style>
.tm-hero { padding-top: 120px !important; }
.tm-hero-in { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); gap: 40px; align-items: center; }
.tm-hero h1 { font-size: clamp(34px, 5vw, 60px); margin: 14px 0 12px; }
.tm-hero-pic { margin: 0; justify-self: end; max-width: 400px; width: 100%; }
.tm-hero-pic img { width: 100%; height: auto; border-radius: 16px; border: 1px solid var(--border); display: block; }
.tm-hero-pic figcaption { margin-top: 8px; color: var(--text-3); font-size: 13px; text-align: right; }
@media (max-width: 820px) { .tm-hero-in { grid-template-columns: minmax(0, 1fr); } .tm-hero-pic { justify-self: stretch; max-width: none; } .tm-hero-pic img { aspect-ratio: 4 / 3; object-fit: cover; object-position: 50% 25%; } .tm-hero-pic figcaption { text-align: left; } .tm-hero { padding-top: 96px !important; } }
.tm-cols { columns: 3 300px; column-gap: 16px; }
.tm { transition: transform .25s, border-color .25s, box-shadow .25s; }
.tm:hover { transform: translateY(-3px); border-color: var(--green); box-shadow: 0 18px 44px rgba(0,154,68,.16); }   /* Matteo 15 Nov: highlight on hover */
.tm-sub { margin: -4px 0 12px; font: 400 clamp(20px, 2.4vw, 28px)/1.15 var(--head); text-transform: uppercase; color: var(--green-text); }
.tm { break-inside: avoid; margin: 0 0 16px; padding: 20px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); display: grid; gap: 12px; }
.tm-photo { border-radius: 10px; overflow: hidden; }   /* Matteo 15 Nov: photos not centred -> shown whole, no crop */
.tm-photo img { display: block; width: 100%; height: auto; max-height: 420px; object-fit: contain; background: #0d0e0f; }
.tm-photo.gn-png { background: #fff; }
.tm .rv-stars { color: #f5b301; letter-spacing: 2px; font-size: 15px; line-height: 1; }
.tm blockquote { margin: 0; color: var(--text-2); font-size: 15px; line-height: 1.6; }
.tm blockquote p { margin: 0 0 10px; }
.tm details summary { cursor: pointer; color: var(--green-text); font-weight: 600; font-size: 14px; list-style: none; }
.tm details summary::-webkit-details-marker { display: none; }
.tm details[open] summary { margin-bottom: 10px; }
.tm figcaption { font-weight: 700; color: var(--text); font-size: 14px; }
</style>'''
build('testimonials', '/testimonials/', MAIN, 'New Testimonials page: every live testimonial, H1 and H2 kept.', h1=H1, extra_css=CSS)
print('testimonials:', MAIN.count('<figure class="tm">'))
