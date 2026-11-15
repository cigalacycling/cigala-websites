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
# Matteo 15 Nov: "what's covered, if there is anything you can include more". From Vivify Sports' own coaching page
# (vivifysports.com/nutritionalcoaching): the extra items its plans cover.
MORE = ['Weekly macro plan based on your training load', 'Food diary analysis and feedback', 'Gut health, IBS & gastro-intestinal issues',
        'Race & event fuelling strategy', 'Gut training for race-day fuelling', 'Weight management & body composition', 'Recovery nutrition']
IC = {   # simple line icons, one per item
    'Macronutrients requirements': '<path d="M12 2a10 10 0 1 0 10 10H12z"/><path d="M14 2.2A10 10 0 0 1 21.8 10H14z"/>',
    'Vitamins & Minerals requirements': '<path d="M10.5 20.5 3.5 13.5a5 5 0 0 1 7-7l7 7a5 5 0 0 1-7 7z"/><path d="m8.5 8.5 7 7"/>',
    'Supplements requirements': '<rect x="7" y="3" width="10" height="18" rx="3"/><path d="M7 12h10"/>',
    'Sports specific requirements': '<circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M15 6h2l3 11.5M5.5 17.5 9 9h7l-4 8.5M9 9 8 6H6"/>',
    'Lifestyle advice': '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21.2l8.8-8.8a5.5 5.5 0 0 0 0-7.8z"/>',
    'Healthy recipes': '<path d="M3 11h18a9 9 0 0 1-18 0z"/><path d="M8 7c0-2 1-3 2-4M12 7c0-2 1-3 2-4M16 7c0-2 1-3 2-4"/>',
    'Craving control guidelines': '<circle cx="12" cy="12" r="10"/><path d="M8 12h8"/>',
    'Weekly macro plan based on your training load': '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    'Food diary analysis and feedback': '<path d="M4 4h12l4 4v12H4z"/><path d="M8 12h8M8 16h5"/>',
    'Gut health, IBS & gastro-intestinal issues': '<path d="M7 3c0 4 10 2 10 7s-10 3-10 8 10 3 10 3"/>',
    'Race & event fuelling strategy': '<path d="M4 22V4M4 4h13l-2 4 2 4H4"/>',
    'Gut training for race-day fuelling': '<path d="M12 2v6M12 22v-4M4.9 4.9l4.2 4.2M14.8 14.8l4.3 4.3M2 12h6M16 12h6"/>',
    'Weight management & body composition': '<path d="M5 21h14l-2-14H7z"/><circle cx="12" cy="5" r="2"/>',
    'Recovery nutrition': '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
}
# nutrition posts (title and featured image from the post itself)
POSTS = [
    ('diet-of-a-cyclist', 'Diet of a cyclist', 'unnamed-3-1.png', 'What should a diet of a cyclist look like?'),
    ('effective-fuelling-techniques-for-winter-training', 'Fuelling for winter training', 'unnamed-4-1.png', 'Fueling techniques during winter for cyclists'),
    ('hydration-tips', 'Hydration Tips', 'imgi_18_photo-1592103634714', 'Water and hydrations tips'),
    ('why-is-hydration-vital-to-optimise-athletic-performance-2', 'Why is hydration vital to optimise performance', 'unnamed-11.jpg', 'Water is vital for cycling performance'),
    ('the-secrets-of-weight-loss', 'The secrets of weight loss', 'unnamed-7.jpg', 'Weight loss for cycling. The secret'),
    ('a-nutritionists-guide-on-surviving-christmas', 'Nutritionist’s guide on surviving Christmas', 'unnamed-6.jpg', 'Nutritionist guide for christmas'),
]
posts = ''.join(f'<a class="nu-post" href="{C}/blog/{s}/" {EXT}><span class="nu-pimg"><img src="{img(k, "nutrition-post-" + s[:40])}" alt="{E(a)}" loading="lazy"></span>'
                f'<span class="nu-ptx"><h3 class="h-sm">{E(t)}</h3><span class="arrow-link">Read the article →</span></span></a>' for s, t, k, a in POSTS)
covered = ''.join(f'<li><svg viewBox="0 0 24 24" aria-hidden="true">{IC[x]}</svg><span>{E(x)}</span></li>' for x in COVERED + MORE)

def viv(text):
    """escape, then link every 'VIVIFY SPORTS' to vivifysports.com (Matteo 15 Nov)"""
    return E(text).replace('VIVIFY SPORTS', f'<a class="viv" href="{VIVSITE}" {EXT}>VIVIFY SPORTS</a>')
VIVSITE = 'https://www.vivifysports.com/'

# what every package includes, from the live package lists (build_coaching_packages: Basic excludes the consult and the daily carbs)
PKG = [('Nutritional Guide', 'All packages'), ('Blood panel review from our Sport Nutritionist', 'All packages'),
       ('Access to work 1-to-1 with our World Class Nutritionist & Mental Coach', 'All packages'),
       ('Daily Session Carbs Recommendations', 'Advanced & Premium'), ('Nutritional Consult with our Sports Nutritionist', 'Advanced & Premium')]
pkg = ''.join(f'<li><span>{E(t)}</span><small>{E(w)}</small></li>' for t, w in PKG)

# Matteo 15 Nov: nutrition coaching as an UPGRADE to cycling coaching. Marine sees the athlete's calendar, training load and
# sessions, plans the nutrition day by day, reviews the food diary; fuelling strategy per race from Critical Power; gut training.
UPG = [
    ('One calendar', 'Your nutrition sits next to your training in Vekta or TrainingPeaks: daily macros and carbs, written for the sessions you are doing that day.'),
    ('Planned from your training load', 'Marine sees your calendar, training load and sessions, and adjusts your plan as the training changes: more carbs on the big days, less on the easy ones.'),
    ('Food diary review', 'Log what you eat (MyFitnessPal or a note in your calendar). Marine reviews your diary and sends suggestions.'),
    ('Race & event fuelling', 'A fuelling strategy for each race, built from your Critical Power and the demands of the event, with gut training so your stomach can take it on the day.'),
]
upg = ''.join(f'<li><h3 class="h-sm">{E(t)}</h3><p>{E(d)}</p></li>' for t, d in UPG)
# the calendar: redrawn from Matteo's screenshot of an athlete's week (15 Nov 2026), not a photo
WEEK = [('20', 'Nutritional note: focus on nutrient-dense foods that support immune function', [('str', '45m', 'Core & Strength Circuit | 2 lap', '')]),
        ('21', 'Daily macronutrient intake: 300 g carbohydrates · 160 g protein · 75 g fat', [('ride', '1h31m · 54 km', '4×6 min torque efforts alternating + bursts', 'TEM')]),
        ('22', 'Daily macronutrient intake: 300 g carbohydrates · 160 g protein · 75 g fat', [('ride', '58m · 33 km', 'Dynamic Efforts', 'AN')]),
        ('23', 'Daily macros: 280 g carbohydrates = 1,120 kcal (48.9%) · 140 g protein', [('str', '30m', 'Stretch Routine', '')]),
        ('24', 'Daily macronutrient intake: 560 g carbohydrates = 2,240 kcal (62.2%)', [('ride', '3h23m · 102 km', 'LDT + 3×10′ at SS, high cadence', 'THR')]),
        ('25', 'Daily macros: 280 g carbohydrates = 1,120 kcal (48.9%) · 140 g protein', [('ride', '2h05m · 63 km', 'Active Recovery 1h30', 'AER')]),
        ('26', 'Daily macronutrient intake: 560 g carbohydrates = 2,240 kcal (62.2%)', [('ride', '4h23m · 110 km', 'LDT 4h aim at 2000 m elevation', 'AER')])]
TAGC = {'TEM': '#0e7c86', 'AN': '#7c4dff', 'THR': '#22a35a', 'AER': '#2f80ed'}
def wk_card(kind, d, t, tag):
    ic = ('<svg class="cal-ic" viewBox="0 0 24 24"><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M15 6h2l3 11.5M5.5 17.5 9 9h7l-4 8.5"/></svg>' if kind == 'ride'
          else '<svg class="cal-ic" viewBox="0 0 24 24"><path d="M6 7v10M18 7v10M3 10v4M21 10v4M6 12h12"/></svg>')
    tg = f'<span class="cal-tag" style="background:{TAGC[tag]}">{tag}</span>' if tag else ''
    return f'<div class="cal-w"><div class="cal-wt">{ic} {E(d)}{tg}</div><div class="cal-wn">{E(t)}</div></div>'
cal = ''.join(f'<div class="cal-d"><div class="cal-h">{d}</div><div class="cal-n"><b>Nutrition</b><span>{E(n)}</span></div>{"".join(wk_card(*w) for w in ws)}</div>' for d, n, ws in WEEK)
NOTE = ['LUNCH', 'Target: ~80 g carbs | ~45 g protein | ~25 g fat', '', 'Option 1', '• Grilled chicken breast', '• Rice', '• Mixed vegetables', '• Olive oil dressing',
        '', 'Option 2', '• Lean beef', '• Baked potato', '• Side salad']
note = '<br>'.join(E(x) for x in NOTE)

FAQ = [
    ('Who is the nutrition consultation for?',
     'Anyone who wants to clean up their diet, boost energy levels and performance, manage their weight, support their immune system, improve their relationship with food, or simply get general guidance on nutrition.'),
    ('How does the consultation work?',
     ' '.join(how[:1]) + ' You receive a full, in-depth report and a Vital Hygiene Program with personalised advice on food, movement and tools to manage stress. You can book several sessions to add feedback and monitoring over a longer period.'),
    ('Can I add nutrition coaching to my cycling coaching?',
     'Yes. Nutrition coaching with Marine is an upgrade to any Cigala Cycling coaching package. She works from the same calendar as your coach, plans your nutrition around your training load, reviews your food diary and builds your race fuelling strategy. The price of the nutrition plan depends on the support you need: Marine will advise you in a free discovery call.'),
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

HERO = img('unnamed-2.jpg', 'nutrition-hero-pasta')   # Matteo 15 Nov: not the strawberries
MARINE = conv('coaching/vivify/marine-lenehan-sports-nutritionist.webp', 'nutrition-marine-lenehan-portrait')   # her own portrait (vivifysports.com/about)
MARINE_ALT = 'Marine Lenehan, MSc sports nutritionist and founder of Vivify Sports'

MAIN = f'''<div class="hero hero-sm nu-hero">
  <img src="{HERO}" alt="{E(live_alt('unnamed-2.jpg'))}">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Sports nutrition with Vivify Sports</div>
    <h1>{E(H1)}</h1>
    <p class="lede">{viv(lead)}</p>
    <div class="ctas"><a class="btn btn-go" href="{VIVIFY}" {EXT}>Book your consultation</a><a class="btn btn-ghost" href="#upgrade">Nutrition with your coaching ↓</a></div>
  </div>
</div>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">Your consultation</div>
      <h2>BOOK YOUR CONSULTATION BELOW</h2><div class="bar"></div>
      {''.join(f'<p>{viv(x)}</p>' for x in how)}
      <div class="ctas"><a class="btn btn-go" href="{VIVIFY}" {EXT}>Book your consultation</a><a class="btn btn-ghost" href="{VIVSITE}" {EXT}>Visit Vivify Sports</a></div>
    </div>
    <figure class="nu-marine">
      <div class="photo"><img src="{MARINE}" alt="{E(MARINE_ALT)}" loading="lazy" width="1400" height="1400"></div>
      <figcaption>
        <b>Marine Lenehan</b>
        <span>MSc Sports Nutritionist · founder of <a class="viv" href="{VIVSITE}" {EXT}>Vivify Sports</a></span>
        <span>WorldTour professional cyclist with LIDL-TREK</span>
        <span>Irish National Gravel Champion 2026 · Amateur Gravel World Champion 2024</span>
      </figcaption>
    </figure>
  </div>
</section>

<section id="covered">
  <div class="in">
    <div class="head"><div><div class="eyebrow">Vivify Sports</div><h2>WHAT’S COVERED</h2><div class="bar"></div></div></div>
    <p class="nu-lede">{viv(WHAT)} Particularly looking into:</p>
    <ul class="nu-cov">{covered}</ul>
  </div>
</section>

<section id="upgrade">
  <div class="in">
    <div class="head"><div><div class="eyebrow">Upgrade your coaching</div><h2>NUTRITION IN YOUR COACHING</h2><div class="bar"></div></div></div>
    <p class="nu-lede"><b>Train like a pro, with everything in one place.</b> Add nutrition coaching with Marine to your Cigala Cycling coaching: she works from the same calendar as your coach, so your training and your nutrition are planned together.</p>
    <ul class="nu-upg">{upg}</ul>
    <figure class="nu-cal">
      <div class="cal-scroll" tabindex="0" aria-label="Example training week with nutrition notes, scroll sideways"><div class="cal-row">{cal}</div></div>
      <div class="cal-note"><div class="cal-nh"><span>Note</span><b>Nutrition</b></div><p>{note}</p></div>
      <figcaption>An athlete’s week: training sessions with Marine’s nutrition for each day, and a meal note in the same calendar.</figcaption>
    </figure>
    <div class="nu-upg-cta panel">
      <p><b>An upgrade to any coaching package.</b> The price of your nutrition plan depends on the support you need: Marine will tell you in a free discovery call.</p>
      <div class="ctas"><a class="btn btn-go" href="{VIVIFY}" {EXT}>Book a call with Marine</a><a class="btn btn-ghost" href="{C}/individual-packages/" {EXT}>See the coaching packages</a></div>
    </div>
    <div class="split nu-inc">
      <div class="gn-txt">
        <h3 class="h-sm">Already in every coaching package</h3>
        <p>Nutrition is part of every Cigala Cycling coaching package, even without the upgrade: training and fuelling are planned together, so you have the energy for the sessions that matter.</p>
      </div>
      <ul class="nu-pkg panel">{pkg}</ul>
    </div>
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
      <img src="{img('unnamed-4-1.png', 'nutrition-cta-granola')}" alt="{E(live_alt('unnamed-4-1.png'))}" loading="lazy" width="998" height="816">
      <div class="tx">
        <div class="eyebrow"><a class="viv" href="{VIVSITE}" {EXT}>Vivify Sports</a></div>
        <h3 class="h-sec">READY TO FUEL BETTER?</h3>
        <div class="bar"></div>
        <p class="lede">Book a consultation at a time that suits you, from the comfort of your own home.</p>
        <div class="ctas"><a class="btn btn-go" href="{VIVIFY}" {EXT}>Book your consultation</a></div>
      </div>
    </div>
  </div>
</section>'''

CSS = G.GCSS + '''<style>
.nu-hero > img { object-position: 50% 50%; }
a.viv { color: var(--green-text) !important; font-weight: 700; text-decoration: none; }
a.viv:hover { text-decoration: underline; }
.nu-marine { margin: 0; display: grid; gap: 14px; max-width: 440px; justify-self: center; }
.nu-marine .photo { aspect-ratio: 1; }
.nu-marine img { width: 100%; height: 100%; object-fit: cover; object-position: 50% 30%; }
.nu-marine figcaption { display: grid; gap: 4px; font-size: 14px; color: var(--text-2); }
.nu-marine figcaption b { font: 400 24px/1.1 var(--head); color: var(--text); text-transform: uppercase; }
.nu-lede { color: var(--text-2); max-width: 75ch; margin: 0 0 20px; line-height: 1.65; }
.nu-lede b { color: var(--text); }
.nu-cov { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 12px; }
.nu-cov li { display: flex; align-items: center; gap: 12px; padding: 16px 18px; border: 1px solid var(--border); border-radius: 12px; background: var(--panel-grad), var(--panel); font-weight: 600; color: var(--text); }
.nu-cov svg { width: 26px; height: 26px; flex: none; fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.nu-upg { list-style: none; margin: 0 0 22px; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; }
.nu-upg li { padding: 18px 20px; border: 1px solid var(--border); border-left: 3px solid var(--green); border-radius: 12px; background: var(--panel-grad), var(--panel); }
.nu-upg h3 { margin: 0 0 6px; }
.nu-upg p { margin: 0; color: var(--text-2); font-size: 15px; line-height: 1.55; }
.nu-cal { margin: 0 0 22px; display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 14px; align-items: start; }
.nu-cal figcaption { grid-column: 1 / -1; color: var(--text-3); font-size: 13px; }
@media (max-width: 1000px) { .nu-cal { grid-template-columns: minmax(0, 1fr); } }
.cal-scroll { overflow-x: auto; border-radius: 12px; border: 1px solid rgba(0,0,0,.1); background: #fff; scrollbar-width: thin; }
.cal-row { display: grid; grid-template-columns: repeat(7, minmax(150px, 1fr)); min-width: 1050px; }
.cal-d { border-right: 1px solid #e8e8e8; padding: 0 8px 10px; display: grid; align-content: start; gap: 8px; font-family: Inter, system-ui, sans-serif; }
.cal-d:last-child { border-right: 0; }
.cal-h { background: #fbefc8; margin: 0 -8px; padding: 8px 10px; font-size: 13px; color: #444; }
.cal-n { background: #f2f2f2; border-radius: 6px; padding: 8px 10px; display: grid; gap: 4px; }
.cal-n b { font-size: 13px; color: #222; }
.cal-n span { font-size: 11px; line-height: 1.4; color: #444; }
.cal-w { border: 2px solid #3cc068; border-radius: 6px; padding: 8px 10px; background: #fff; display: grid; gap: 6px; }
.cal-wt { display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; color: #222; }
.cal-ic { width: 16px; height: 16px; fill: none; stroke: #333; stroke-width: 2; stroke-linecap: round; flex: none; }
.cal-tag { margin-left: auto; color: #fff; font-size: 10px; font-weight: 700; padding: 2px 5px; border-radius: 3px; }
.cal-wn { font-size: 13px; color: #222; line-height: 1.35; }
.cal-note { background: #fff; border-radius: 12px; padding: 14px 16px; font-family: Inter, system-ui, sans-serif; color: #333; }
.cal-nh { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.cal-nh span { font-weight: 700; color: #111; }
.cal-nh b { background: #fbd96b; border-radius: 6px; padding: 4px 10px; font-size: 13px; }
.cal-note p { margin: 0; font-size: 13px; line-height: 1.55; }
.nu-upg-cta { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 14px; padding: 18px 22px; margin-bottom: 26px; }
.nu-upg-cta p { margin: 0; color: var(--text-2); max-width: 60ch; }
.nu-upg-cta p b { color: var(--text); }
.nu-upg-cta .ctas { margin: 0; }
.nu-inc { align-items: center; }
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
.nu-ptx h3 { margin: 0; color: var(--text); font-size: 20px; }
</style>'''
LD = f'<script type="application/ld+json">{json.dumps(FAQ_LD, ensure_ascii=False)}</script>'
build('nutrition', '/nutrition/', MAIN, 'Nutrition page: Vivify Sports with Marine, nutrition coaching as an upgrade, what is covered, nutrition posts, FAQ.',
      h1=H1, h2_changes={'drop': ['By Founder & Head Coach, Matteo Cigala'],
                         'add': ['WHAT’S COVERED', 'NUTRITION IN YOUR COACHING', 'FREE NUTRITION TOOLS', 'FREQUENTLY ASKED QUESTIONS']},
      extra_css=CSS, extra_js=LD)
print('nutrition: covered', len(COVERED) + len(MORE), 'posts', len(POSTS), 'faq', len(FAQ))
