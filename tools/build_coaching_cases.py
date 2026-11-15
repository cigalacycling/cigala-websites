"""Build the Case Studies page (new page, Matteo 15 Nov 2026): coachingpages/case-studies.html -> /case-studies/
Each case study uses only what the athlete wrote in their testimonial (CASES in tools/coaching_common.py).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *

CAL = 'https://calendly.com/cigalacycling'
HERO = img('IMG_4003AWDWWWU', 'tools-hero')   # Matteo coaching a group (the square athlete photos crop too tight in a banner)

def bars(c):
    if not c.get('bars'): return ''
    out = ''
    for label, sub, before, after, unit, delta in c['bars']:
        l0, l1 = c.get('labels', ('Year before', 'This year'))
        out += (f'<div class="cs-bar"><div class="cs-bar-h"><b>{E(label)}</b><span class="cs-delta">{E(delta)}</span></div><p>{E(sub)}</p>'
                f'<div class="cs-b"><span>{E(l0)}</span><i style="width:{before / after * 100:.0f}%"></i><em>{before:,}{unit}</em></div>'
                f'<div class="cs-b now"><span>{E(l1)}</span><i style="width:100%"></i><em>{after:,}{unit}</em></div></div>')
    bests = ''.join(f'<li>{E(x)}</li>' for x in c.get('bests', []))
    return (f'<div class="cs-charts">{out}</div>' + (f'<div class="cs-bests"><h3>{E(c.get("bests_title", "All-time bests"))}</h3><ul class="ticks">{bests}</ul></div>' if bests else '')
            + f'<p class="cs-src">Source: {E(c["source"])}</p>')

def photo(c, i):
    if c.get('photo_file'):
        return f'<div class="cs-photo"><img src="{conv(c["photo_file"], "case-" + c["slug"])}" alt="{E(c["photo_alt"])}" loading="lazy"></div>'
    if c['photo']:
        return f'<div class="cs-photo"><img src="{img(c["photo"], "athlete-" + c["slug"])}" alt="{E(live_alt(c["photo"]))}" loading="{"eager" if i == 0 else "lazy"}"></div>'
    return f'<div class="cs-photo cs-data" aria-hidden="true"><b>{E(c["stat"])}</b><small>{E(c.get("stat_label", ""))}</small></div>'

def case(c, i):
    how = ''.join(f'<li>{E(x)}</li>' for x in c['how'])
    return f'''<article class="cs-case panel" id="{c['slug']}">
      {photo(c, i)}
      <div class="cs-body">
        <span class="cs-tag">{E(c['tag'])}</span>
        <h2 class="cs-title">{E(c['headline'])}</h2>
        <p class="cs-who">{E(c['name'])} · {E(c['where'])}</p>
        <div class="cs-grid">
          <div><h3>Starting point</h3><p>{E(c['before'])}</p></div>
          <div><h3>Goal</h3><p>{E(c['goal'])}</p></div>
          {f'<div><h3>How we coached</h3><ul class="ticks">{how}</ul></div>' if how else ''}
          <div class="cs-res"><h3>Result</h3><p>{E(c['result'])}</p></div>
        </div>
        {bars(c)}
        {f'<blockquote>“{E(c["quote"])}”<cite>{E(c["name"])}</cite></blockquote>' if c.get('quote') else ''}
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
.cs-photo.cs-data { display: grid; place-content: center; text-align: center; gap: 8px; min-height: 320px; }
.cs-body { padding: 28px; display: grid; gap: 8px; align-content: start; }
.cs-title { font-size: clamp(28px, 3.2vw, 40px); margin: 0; }
.cs-who { margin: 0; color: var(--text-3); font-size: 14px; }
.cs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px 28px; margin-top: 14px; }
.cs-grid h3 { font: 700 11px/1.4 var(--body); letter-spacing: .12em; text-transform: uppercase; color: var(--green-text); margin: 0 0 6px; }
.cs-grid p { margin: 0; color: var(--text-2); font-size: 15px; line-height: 1.6; }
.cs-grid .ticks { margin: 0; }
.cs-res p { color: var(--text); font-weight: 600; }
.cs-charts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }
.cs-bar { padding: 14px; border: 1px solid var(--border); border-radius: 12px; background: rgba(255,255,255,.02); }
.cs-bar-h { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.cs-bar-h b { font-size: 13px; color: var(--text); }
.cs-delta { font: 400 22px/1 var(--head); color: var(--green-text); white-space: nowrap; }
.cs-bar p { margin: 4px 0 10px; font-size: 12.5px; color: var(--text-3); }
.cs-b { display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 4px 8px; font-size: 12px; color: var(--text-3); margin-top: 8px; }
.cs-b i { grid-column: 1 / -1; grid-row: 2; }   /* full-width bar under its label */
.cs-b i { display: block; height: 10px; border-radius: 5px; background: rgba(255,255,255,.18); }
.cs-b.now i { background: var(--green); }
.cs-b em { font-style: normal; font-weight: 700; color: var(--text-2); text-align: right; }
.cs-b.now em { color: var(--text); }
.cs-bests { margin-top: 16px; }
.cs-bests h3 { font: 700 11px/1.4 var(--body); letter-spacing: .12em; text-transform: uppercase; color: var(--green-text); margin: 0 0 8px; }
.cs-bests .ticks { grid-template-columns: 1fr 1fr; }
.cs-src { margin: 10px 0 0; font-size: 12px; color: var(--text-3); }
.cs-photo.cs-data b { font-size: clamp(36px, 3.6vw, 48px); padding: 0 16px; }
@media (max-width: 1100px) { .cs-charts { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 640px) { .cs-bests .ticks { grid-template-columns: minmax(0, 1fr); } }
.cs-body blockquote { margin: 16px 0 0; padding: 14px 18px; border-left: 3px solid var(--green); background: rgba(255,255,255,.03); border-radius: 0 10px 10px 0; color: var(--text-2); font-style: italic; }
.cs-body cite { display: block; margin-top: 8px; font-style: normal; font-size: 13px; color: var(--text-3); }
@media (max-width: 900px) { .cs-case { grid-template-columns: minmax(0, 1fr); } .cs-photo img { min-height: 0; aspect-ratio: 16 / 10; } .cs-grid { grid-template-columns: minmax(0, 1fr); } .cs-body { padding: 20px; } }
</style>'''

build('case-studies', '/case-studies/', MAIN, "New page: Case Studies, from the athletes' own testimonials.", h1='Case Studies', extra_css=CSS,
      new_page={'title': 'Cycling Coaching Case Studies | Cigala Cycling Coaching',
                'meta': 'Real results from Cigala Cycling coaching: from first ride to European champion, +40 W FTP in 4 months, Gran Fondo Worlds qualification and more.'})
