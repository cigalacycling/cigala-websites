"""Build the Case Studies page (new page, Matteo 15 Nov 2026): coachingpages/case-studies.html -> /case-studies/
Each case study uses only what the athlete wrote in their testimonial (CASES in tools/coaching_common.py).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *

CAL = 'https://calendly.com/cigalacycling'
HERO = img('IMG_4003AWDWWWU', 'tools-hero')   # Matteo coaching a group (the square athlete photos crop too tight in a banner)

def case(c, i):
    how = ''.join(f'<li>{E(x)}</li>' for x in c['how'])
    return f'''<article class="cs-case panel" id="{c['slug']}">
      <div class="cs-photo"><img src="{img(c['photo'], 'athlete-' + c['slug'])}" alt="{E(live_alt(c['photo']))}" loading="{'eager' if i == 0 else 'lazy'}"></div>
      <div class="cs-body">
        <span class="cs-tag">{E(c['tag'])}</span>
        <h2 class="cs-title">{E(c['headline'])}</h2>
        <p class="cs-who">{E(c['name'])} · {E(c['where'])}</p>
        <div class="cs-grid">
          <div><h3>Starting point</h3><p>{E(c['before'])}</p></div>
          <div><h3>Goal</h3><p>{E(c['goal'])}</p></div>
          <div><h3>How we coached</h3><ul class="ticks">{how}</ul></div>
          <div class="cs-res"><h3>Result</h3><p>{E(c['result'])}</p></div>
        </div>
        <blockquote>“{E(c['quote'])}”<cite>{E(c['name'])}</cite></blockquote>
      </div>
    </article>'''

MAIN = f'''<div class="hero hero-sm">
  <img src="{HERO}" alt="{E(live_alt('IMG_4003AWDWWWU'))}" width="2560" height="1707">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Results</div>
    <h1>Case Studies</h1>
    <p class="lede">Real athletes, real goals, real results. How Cigala Cycling coaching took riders from where they started to where they wanted to be, in their own words.</p>
    <div class="ctas"><a class="btn btn-go" href="{CAL}" {EXT}>Book a free consultation</a><a class="btn btn-ghost" href="{C}/testimonials/" {EXT}>All testimonials</a></div>
  </div>
</div>

<section>
  <div class="in cs-list">
    {''.join(case(c, i) for i, c in enumerate(CASES))}
  </div>
</section>

<section>
  <div class="in">
    <div class="band band-cta">
      <img src="{img('unnamed-8-1.jpg', 'matteo-worlds-silver')}" alt="{E(live_alt('unnamed-8-1.jpg'))}" loading="lazy" width="1280" height="1600">
      <div class="tx">
        <h3 class="h-sec">YOUR STORY COULD BE NEXT</h3>
        <div class="bar"></div>
        <p class="lede">Tell us where you are now and where you want to be, and we'll build the plan to get you there.</p>
        <div class="ctas"><a class="btn btn-go" href="{CAL}" {EXT}>Book a free consultation →</a><a class="btn btn-ghost" href="{C}/individual-packages/" {EXT}>See the packages</a></div>
      </div>
    </div>
  </div>
</section>'''

CSS = CS_CSS + '''<style>
.hero-sm { min-height: min(560px, 74svh); }
.hero-sm .in { padding-block: 110px 48px; }
.hero-sm h1 { font-size: clamp(38px, 6vw, 72px); }
.hero-sm > img { object-position: 50% 40%; }
.cs-list { display: grid; gap: 24px; }
.cs-case { display: grid; grid-template-columns: minmax(0, 4fr) minmax(0, 8fr); overflow: hidden; border-radius: 16px; scroll-margin-top: 100px; }
.cs-photo { min-height: 100%; background: #111; }
.cs-photo img { width: 100%; height: 100%; object-fit: cover; min-height: 320px; }
.cs-body { padding: 28px; display: grid; gap: 8px; align-content: start; }
.cs-title { font-size: clamp(28px, 3.2vw, 40px); margin: 0; }
.cs-who { margin: 0; color: var(--text-3); font-size: 14px; }
.cs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px 28px; margin-top: 14px; }
.cs-grid h3 { font: 700 11px/1.4 var(--body); letter-spacing: .12em; text-transform: uppercase; color: var(--green-text); margin: 0 0 6px; }
.cs-grid p { margin: 0; color: var(--text-2); font-size: 15px; line-height: 1.6; }
.cs-grid .ticks { margin: 0; }
.cs-res p { color: var(--text); font-weight: 600; }
.cs-body blockquote { margin: 16px 0 0; padding: 14px 18px; border-left: 3px solid var(--green); background: rgba(255,255,255,.03); border-radius: 0 10px 10px 0; color: var(--text-2); font-style: italic; }
.cs-body cite { display: block; margin-top: 8px; font-style: normal; font-size: 13px; color: var(--text-3); }
@media (max-width: 900px) { .cs-case { grid-template-columns: minmax(0, 1fr); } .cs-photo img { min-height: 0; aspect-ratio: 16 / 10; } .cs-grid { grid-template-columns: minmax(0, 1fr); } .cs-body { padding: 20px; } }
</style>'''

build('case-studies', '/case-studies/', MAIN, "New page: Case Studies, from the athletes' own testimonials.", h1='Case Studies', extra_css=CSS,
      new_page={'title': 'Cycling Coaching Case Studies | Cigala Cycling Coaching',
                'meta': 'Real results from Cigala Cycling coaching: from first ride to European champion, +40 W FTP in 4 months, Gran Fondo Worlds qualification and more.'})
