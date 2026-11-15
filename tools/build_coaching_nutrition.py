"""Build the Nutrition page: coachingpages/nutrition.html -> /nutrition/ (page 3995).

Matteo 15 Nov 2026: "the nutrition page has something [wrong] with the blogs ... I don't really like the images, and I would
like to make it more like a nutrition page. The links to Vivify Sports ... if you want to increase the SEO".
The live page's "blog posts" block was a posts widget showing the LATEST posts (strength, CP testing, an Italian race guide),
each with an H1 title and an "By Founder & Head Coach, Matteo Cigala" H2. Now it shows the nutrition posts.

Kept (SEO): URL, Yoast title + meta, the H1, H2s "BOOK YOUR CONSULTATION BELOW" and "READ VIVIFY SPORTS NUTRITIONAL BLOG POSTS",
all the live copy (two typos fixed: "VIFIFY", "CONSULATION"), the Vivify Sports booking link.
Changed (coaching/SEO-DECISIONS.md section 11): the six author-line H2s and the post-title H1s from the widget are gone;
new H2 sections: What's covered, Nutrition in your coaching, Free nutrition tools, FAQ (with FAQPage schema).
  python3 -I tools/build_coaching_nutrition.py
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
import build_coaching_generic as G

VIVIFY = 'https://www.vivifysports.com/nutritionalcoaching'
T = open(ROOT + 'coaching/text/nutrition.txt').read().split('\n')
H1 = T[0][4:].strip()
INTRO = next(l[3:] for l in T if l.startswith('P: Whether you are looking'))
INTRO = INTRO.replace('VIFIFY SPORTS', 'VIVIFY SPORTS').replace('help..The', 'help. The')
# the live paragraph runs sentences together ("home.You"): split it back into sentences
sents = re.split(r'(?<=[.])(?=[A-Z])', INTRO)
lead, how = sents[0], sents[1:]
WHAT = next(l[3:] for l in T if l.startswith('P: By assessing your dietary patterns'))
COVERED = [l[5:].strip() for l in T if l.startswith('P: ➔ ')]
assert len(COVERED) == 7, COVERED
IC = {   # simple line icons, one per item
    'Macronutrients requirements': '<path d="M12 2a10 10 0 1 0 10 10H12z"/><path d="M14 2.2A10 10 0 0 1 21.8 10H14z"/>',
    'Vitamins & Minerals requirements': '<path d="M10.5 20.5 3.5 13.5a5 5 0 0 1 7-7l7 7a5 5 0 0 1-7 7z"/><path d="m8.5 8.5 7 7"/>',
    'Supplements requirements': '<rect x="7" y="3" width="10" height="18" rx="3"/><path d="M7 12h10"/>',
    'Sports specific requirements': '<circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M15 6h2l3 11.5M5.5 17.5 9 9h7l-4 8.5M9 9 8 6H6"/>',
    'Lifestyle advice': '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21.2l8.8-8.8a5.5 5.5 0 0 0 0-7.8z"/>',
    'Healthy recipes': '<path d="M3 11h18a9 9 0 0 1-18 0z"/><path d="M8 7c0-2 1-3 2-4M12 7c0-2 1-3 2-4M16 7c0-2 1-3 2-4"/>',
    'Craving control guidelines': '<circle cx="12" cy="12" r="10"/><path d="M8 12h8"/>',
}
# nutrition posts (staging/live slugs; title and featured image from the post itself)
POSTS = [
    ('diet-of-a-cyclist', 'Diet of a cyclist', 'unnamed-2.jpg', 'Diet of a cyclist, pasta, carbs.'),
    ('effective-fuelling-techniques-for-winter-training', 'Fuelling for winter training', 'unnamed-4-1.png', 'Fueling techniques during winter for cyclists'),
    ('hydration-tips', 'Hydration Tips', 'imgi_18_photo-1592103634714', 'Water and hydrations tips'),
    ('why-is-hydration-vital-to-optimise-athletic-performance-2', 'Why is hydration vital to optimise performance', 'unnamed-11.jpg', 'Water is vital for cycling performance'),
    ('the-secrets-of-weight-loss', 'The secrets of weight loss', 'unnamed-7.jpg', 'Weight loss for cycling. The secret'),
    ('a-nutritionists-guide-on-surviving-christmas', 'Nutritionist’s guide on surviving Christmas', 'unnamed-6.jpg', 'Nutritionist guide for christmas'),
]
posts = ''.join(f'<a class="nu-post" href="{C}/blog/{s}/" {EXT}><span class="nu-pimg"><img src="{img(k, "nutrition-post-" + s[:40])}" alt="{E(a)}" loading="lazy"></span>'
                f'<span class="nu-ptx"><h3 class="h-sm">{E(t)}</h3><span class="arrow-link">Read the article →</span></span></a>' for s, t, k, a in POSTS)
covered = ''.join(f'<li><svg viewBox="0 0 24 24" aria-hidden="true">{IC[x]}</svg><span>{E(x)}</span></li>' for x in COVERED)

# what every package includes, from the live package lists (build_coaching_packages: Basic excludes the consult and the daily carbs)
PKG = [('Nutritional Guide', 'All packages'), ('Blood panel review from our Sport Nutritionist', 'All packages'),
       ('Access to work 1-to-1 with our World Class Nutritionist & Mental Coach', 'All packages'),
       ('Daily Session Carbs Recommendations', 'Advanced & Premium'), ('Nutritional Consult with our Sports Nutritionist', 'Advanced & Premium')]
pkg = ''.join(f'<li><span>{E(t)}</span><small>{E(w)}</small></li>' for t, w in PKG)

FAQ = [
    ('Who is the nutrition consultation for?',
     'Anyone who wants to clean up their diet, boost energy levels and performance, manage their weight, support their immune system, improve their relationship with food, or simply get general guidance on nutrition.'),
    ('How does the consultation work?',
     ' '.join(how[:1]) + ' You receive a full, in-depth report and a Vital Hygiene Program with personalised advice on food, movement and tools to manage stress. You can book several sessions to add feedback and monitoring over a longer period.'),
    ('Is nutrition included in my coaching package?',
     'Yes. Every package includes a nutritional guide, a blood panel review from our sports nutritionist and access to our nutritionist and mental coach. Advanced and Premium add a carbohydrate recommendation for every session and a nutritional consult with our sports nutritionist.'),
    ('How many carbs per hour should I eat on the bike?',
     'It depends on how long and how hard the ride is, and on how much your gut is trained to take. Our free carbs-per-hour calculator gives you a starting number in seconds, and in coaching every session comes with its own recommendation (Advanced and Premium).'),
    ('How much should I drink when I ride?',
     'Sweat losses vary a lot between riders and with the weather. Weigh yourself before and after a ride with our free sweat-rate calculator to find out how much you lose per hour, then plan your bottles around it.'),
]
faq_html = ''.join(f'<details{" open" if i == 0 else ""}><summary><h3>{E(q)}</h3></summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(FAQ))
FAQ_LD = {'@context': 'https://schema.org', '@type': 'FAQPage',
          'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]}

HERO = img('unnamed-6-1.jpg', 'nutrition-hero-strawberries')
MARINE = img('unnamed-7-1.png', 'nutrition-marine')

MAIN = f'''<div class="hero hero-sm nu-hero">
  <img src="{HERO}" alt="{E(live_alt('unnamed-6-1.jpg'))}">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Sports nutrition with Vivify Sports</div>
    <h1>{E(H1)}</h1>
    <p class="lede">{E(lead)}</p>
    <div class="ctas"><a class="btn btn-go" href="{VIVIFY}" {EXT}>Book your consultation</a><a class="btn btn-ghost" href="#covered">What’s covered ↓</a></div>
  </div>
</div>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">Your consultation</div>
      <h2>BOOK YOUR CONSULTATION BELOW</h2><div class="bar"></div>
      {''.join(f'<p>{E(x)}</p>' for x in how)}
      <div class="ctas"><a class="btn btn-go" href="{VIVIFY}" {EXT}>Book your consultation</a><a class="btn btn-ghost" href="{VIVIFY}" {EXT}>Learn more about Vivify Sports</a></div>
    </div>
    <div class="photo nu-marine"><img src="{MARINE}" alt="{E(live_alt('unnamed-7-1.png'))}" loading="lazy" width="947" height="1263"></div>
  </div>
</section>

<section id="covered">
  <div class="in">
    <div class="head"><div><div class="eyebrow">Vivify Sports</div><h2>WHAT’S COVERED</h2><div class="bar"></div></div></div>
    <p class="nu-lede">{E(WHAT)} Particularly looking into:</p>
    <ul class="nu-cov">{covered}</ul>
  </div>
</section>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">Coached by Cigala Cycling?</div>
      <h2>NUTRITION IN YOUR COACHING</h2><div class="bar"></div>
      <p>Nutrition is part of every Cigala Cycling coaching package: training and fuelling are planned together, so you have the energy for the sessions that matter.</p>
      <div class="ctas"><a class="btn btn-go" href="{C}/individual-packages/" {EXT}>See the packages</a></div>
    </div>
    <ul class="nu-pkg panel">{pkg}</ul>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Free calculators</div><h2>FREE NUTRITION TOOLS</h2><div class="bar"></div></div></div>
    <div class="nu-tools">
      <a class="panel nu-tool" href="{C}/tools/carbs-per-hour-calculator/" {EXT}><h3 class="h-sm">Carbs per hour</h3><p>Your fuelling plan for a ride or race: grams of carbs per hour, in gels and bottles.</p><span class="arrow-link">Open the calculator →</span></a>
      <a class="panel nu-tool" href="{C}/tools/sweat-rate-calculator/" {EXT}><h3 class="h-sm">Sweat rate</h3><p>How much you sweat per hour, and how much to drink on the bike.</p><span class="arrow-link">Open the calculator →</span></a>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head">
      <div><div class="eyebrow">From our blog</div><h2>READ VIVIFY SPORTS NUTRITIONAL BLOG POSTS</h2><div class="bar"></div></div>
      <div class="rv-links"><a class="arrow-link" href="{C}/blog/" {EXT}>All blog posts →</a></div>
    </div>
    <div class="nu-posts">{posts}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Good to know</div><h2>FREQUENTLY ASKED QUESTIONS</h2><div class="bar"></div></div></div>
    <div class="faq">{faq_html}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="band band-cta">
      <img src="{img('unnamed-2.jpg', 'nutrition-cta-pasta')}" alt="{E(live_alt('unnamed-2.jpg'))}" loading="lazy" width="1600" height="1059">
      <div class="tx">
        <div class="eyebrow">Vivify Sports</div>
        <h3 class="h-sec">READY TO FUEL BETTER?</h3>
        <div class="bar"></div>
        <p class="lede">Book a consultation at a time that suits you, from the comfort of your own home.</p>
        <div class="ctas"><a class="btn btn-go" href="{VIVIFY}" {EXT}>Book your consultation</a></div>
      </div>
    </div>
  </div>
</section>'''

CSS = G.GCSS + '''<style>
.nu-hero > img { object-position: 50% 45%; }
.nu-marine { aspect-ratio: 4 / 5; max-width: 440px; justify-self: center; }
.nu-marine img { width: 100%; height: 100%; object-fit: cover; object-position: 50% 30%; }
.nu-lede { color: var(--text-2); max-width: 70ch; margin: 0 0 20px; line-height: 1.65; }
.nu-cov { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.nu-cov li { display: flex; align-items: center; gap: 12px; padding: 16px 18px; border: 1px solid var(--border); border-radius: 12px; background: var(--panel-grad), var(--panel); font-weight: 600; color: var(--text); }
.nu-cov svg { width: 26px; height: 26px; flex: none; fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.nu-pkg { list-style: none; margin: 0; padding: 8px 20px; align-self: center; }
.nu-pkg li { display: flex; justify-content: space-between; align-items: baseline; gap: 14px; padding: 14px 0; border-bottom: 1px solid var(--border); color: var(--text); }
.nu-pkg li:last-child { border-bottom: 0; }
.nu-pkg small { flex: none; font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--green-text); }
.nu-tools { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }
.nu-tool { display: grid; gap: 8px; padding: 22px; text-decoration: none; color: var(--text); transition: border-color .2s; }
.nu-tool:hover { border-color: rgba(0,154,68,.6); }
.nu-tool h3, .nu-tool p { margin: 0; }
.nu-tool p { color: var(--text-2); font-size: 15px; }
.nu-posts { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.nu-post { display: flex; flex-direction: column; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; background: var(--panel-grad), var(--panel); text-decoration: none; transition: border-color .2s, transform .2s; }
.nu-post:hover { border-color: rgba(0,154,68,.6); transform: translateY(-2px); }
.nu-pimg { aspect-ratio: 16 / 10; overflow: hidden; background: #111; }
.nu-pimg img { width: 100%; height: 100%; object-fit: cover; }
.nu-ptx { display: grid; gap: 8px; padding: 16px 18px 18px; }
.nu-ptx h3 { margin: 0; color: var(--text); }
</style>'''
LD = f'<script type="application/ld+json">{json.dumps(FAQ_LD, ensure_ascii=False)}</script>'
build('nutrition', '/nutrition/', MAIN, 'Nutrition rebuilt as a nutrition page: Vivify Sports booking, what is covered, nutrition posts, FAQ.',
      h1=H1, h2_changes={'drop': ['By Founder & Head Coach, Matteo Cigala'],
                         'add': ['WHAT’S COVERED', 'NUTRITION IN YOUR COACHING', 'FREE NUTRITION TOOLS', 'FREQUENTLY ASKED QUESTIONS']},
      extra_css=CSS, extra_js=LD)
print('nutrition: covered', len(COVERED), 'posts', len(POSTS), 'faq', len(FAQ))
