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
sents = re.split(r'(?<=[.])\s*(?=[A-Z])', INTRO)
lead = sents[0]
SCHED = next(x for x in sents if x.startswith('The consultation is scheduled'))
MULTI = next(x for x in sents if x.startswith('You also have the option'))
# Matteo 15 Nov (3rd + 4th review): performance nutrition, not general health. The live "full in depth report ... be responsible
# for your own health" and "Vital Hygiene Program ... movement ... stress and emotions" sentences are replaced.
assert any('Vital Hygiene' in x for x in sents) and any('responsible for your own health' in x for x in sents)
how = [SCHED,
       'You will receive a full, in-depth report of Marine’s observations, so you understand exactly what your body needs to train, race and recover at your best.',
       'Marine then builds your personalised performance nutrition plan, adapted to your training load, your goals and your physiology.',
       'You get practical advice on what to eat and when: your daily meals and macros, fuelling before, during and after training, hydration, and supplements only where you need them.',
       MULTI]
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
# Matteo 15 Nov: Marine's articles, published on the Coaching blog from vivifysports.com (tools/coaching_vivify_posts.py), plus her
# cherry juice article that was already there. Images are the posts' featured images on the site.
VP = json.load(open(ROOT + 'stg-coaching/vivify-posts.json'))['posts']
POSTS = [(slug, p['title'], p['featured'], p['featured_alt']) for slug, p in VP.items()]
POSTS.append(('is-cherry-juice-really-worth-the-hype', 'Cherry Juice: is it really worth the hype?', 'https://staging.coaching.cigalacycling.com/wp-content/uploads/2026/06/unnamed-30.jpg', 'Cherry Juice in sports. Is really worth the hype?'))
posts = ''.join(f'<a class="nu-post" href="{C}/blog/{s}/" {EXT}><span class="nu-pimg"><img src="{u}" alt="{E(a)}" loading="lazy"></span>'
                f'<span class="nu-ptx"><span class="nu-by">By Marine Lenehan</span><h3 class="h-sm">{E(t)}</h3><span class="arrow-link">Read the article →</span></span></a>' for s, t, u, a in POSTS)
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
    ('One calendar', 'Your nutrition sits next to your training in Vekta or TrainingPeaks: your daily macros (carbohydrates, protein and fat), written for the sessions you are doing that day.'),
    ('Planned from your training load', 'Marine sees your calendar, training load and sessions, and adjusts your plan as the training changes: more carbs on the big days, less on the easy ones.'),
    ('Food diary review', 'Log what you eat in MyFitnessPal. Marine reviews your food diary and sends you suggestions.'),
    ('Race & event fuelling', 'A fuelling strategy for each race, built from your Critical Power and the demands of the event, with gut training so your stomach can take it on the day.'),
]
UIC = ['<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18M8 14h3M8 18h6"/>',       # calendar
       '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',                                                       # training load
       '<path d="M4 4h12l4 4v12H4z"/><path d="M8 12h8M8 16h5"/>',                                                   # food diary
       '<path d="M4 22V4M4 4h13l-2 4 2 4H4"/>']                                                                     # race flag
upg = ''.join(f'<li><svg class="nu-uic" viewBox="0 0 24 24" aria-hidden="true">{i}</svg><h3 class="h-sm">{E(t)}</h3><p>{E(d)}</p></li>' for i, (t, d) in zip(UIC, UPG))
# the calendar: redrawn from Matteo's screenshot of an athlete's week (15 Nov 2026), not a photo
# the calendar, redrawn from Matteo's screenshot of an athlete's week (15 Nov 2026)
WEEK = [('20', '8/28', ['Nutritional note: focus on nutrient-dense foods that support immune function'], [('str', '45m', '', 'Core & Strength Circuit | 2 lap', '', 0, None)]),
        ('21', '8/28', ['Daily macronutrient intake: 300 g carbohydrates · 160 g protein · 75 g fat'], [('ride', '1h31m', '54 km', '4×6 min torque efforts alternating + bursts', 'TEM', 1, [3, 3, 7, 7, 3, 7, 7, 3, 7, 7, 3, 2])]),
        ('22', '8/28', ['Daily macronutrient intake: 300 g carbohydrates · 160 g protein · 75 g fat'], [('ride', '58m', '33 km', 'Dynamic Efforts', 'AN', 0, [3, 4, 9, 3, 9, 3, 9, 3, 4, 2])]),
        ('23', '8/28', ['Daily macros: 280 g carbohydrates = 1,120 kcal (48.9%) · 140 g protein', 'Daily macros: 280 g carbohydrates = 1,120 kcal (48.9%) · 140 g protein'], [('str', '30m', '', 'Stretch Routine', '', 0, None)]),
        ('24', '9/28', ['Daily macronutrient intake: 560 g carbohydrates = 2,240 kcal (62.2%)'], [('ride', '3h23m', '102 km', 'LDT + 3×10′ at SS, high cadence', 'THR', 13, [4, 4, 4, 6, 6, 4, 6, 6, 4, 6, 6, 4, 4, 3])]),
        ('25', '8/28', ['Daily macros: 280 g carbohydrates = 1,120 kcal (48.9%) · 140 g protein'], [('ride', '2h05m', '63 km', 'Active Recovery 1h30', 'AER', 0, [3, 3, 3, 3, 3, 3, 3, 3, 3, 3])]),
        ('26', '8/28', ['Daily macronutrient intake: 560 g carbohydrates = 2,240 kcal (62.2%)'], [('ride', '4h23m', '110 km', 'LDT 4h aim at 2000 m elevation', 'AER', 3, [4, 5, 4, 6, 4, 5, 6, 4, 5, 4, 6, 5, 4, 3])])]
TAGC = {'TEM': '#0e8a95', 'AN': '#7c4dff', 'THR': '#22a35a', 'AER': '#2f80ed'}
CI = {'ride': '<circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M15 6h2l3 11.5M5.5 17.5 9 9h7l-4 8.5"/>',
      'str': '<path d="M6 7v10M18 7v10M3 10v4M21 10v4M6 12h12"/>',
      'leaf': '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5.1-6"/>',
      'msg': '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7A8.5 8.5 0 1 1 21 11.5z"/>',
      'ok': '<circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 5-6"/>'}
svgi = lambda k, c='cal-ic': f'<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true">{CI[k]}</svg>'
def trace(v):
    w = 100 / len(v)
    return '<svg class="cal-trace" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true">' + ''.join(f'<rect x="{i * w:.2f}" y="{10 - h}" width="{w - .6:.2f}" height="{h}"/>' for i, h in enumerate(v)) + '</svg>'
CPH = {'4×6 min torque efforts alternating + bursts': '40–50 g/h', 'LDT + 3×10′ at SS, high cadence': '60 g/h', 'LDT 4h aim at 2000 m elevation': '60 g/h'}
def wk_card(kind, d, km, t, tag, com, tr):
    tg = f'<span class="cal-tag" style="background:{TAGC[tag]}">{tag}</span>' if tag else ''
    cm = f'<span class="cal-com">{svgi("msg", "cal-ic2")}<b>{com}</b></span>' if com else ''
    return (f'<div class="cal-w"><div class="cal-wt">{svgi(kind)}<span>{E(d)}{" · " + E(km) if km else ""}</span>{tg}</div>'
            f'<div class="cal-wn"><span>{E(t)}</span><span class="cal-st">{cm}{svgi("ok", "cal-ic2 cal-done")}</span></div>'
            + (f'<span class="cal-cph"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.7s6 6.6 6 11.3a6 6 0 0 1-12 0c0-4.7 6-11.3 6-11.3z"/></svg>{CPH[t]}</span>' if t in CPH else '')
            + f'{trace(tr) if tr else ""}</div>')
cal = ''.join(f'<div class="cal-d"><div class="cal-h"><b>{d}</b></div><div class="cal-cnt">{c}</div>'
              + ''.join(f'<div class="cal-n"><b>{svgi("leaf")}Nutrition</b><span>{E(n)}</span></div>' for n in ns)
              + ''.join(wk_card(*w) for w in ws) + '</div>' for d, c, ns, ws in WEEK)
# Matteo 15 Nov: "replace with a recipe you invent ... a basic recipe for sports people" (an example; macros approximate)
RECIPE = ('Post-ride recovery bowl', 'Serves 1 · 15 minutes', 'Approx. 85 g carbs · 50 g protein · 19 g fat',
          ['100 g basmati rice (dry weight)', '150 g chicken breast', '1 small sweet pepper and a handful of spinach', '1 tbsp olive oil', 'Lemon, salt, pepper, paprika'],
          ['Cook the rice.', 'Slice the chicken, season with paprika and pan-fry in the olive oil for 6–8 minutes.', 'Add the pepper and spinach for the last 2 minutes, then serve on the rice with a squeeze of lemon.'])
BREAKFAST = ('Pre-ride overnight oats', 'Serves 1 · 5 minutes, the night before', 'Approx. 115 g carbs · 35 g protein · 13 g fat',
             ['80 g rolled oats', '250 ml milk', '150 g Greek yoghurt', '1 banana', '1 tbsp honey', 'A handful of berries'],
             ['Mix the oats, milk and yoghurt in a jar and leave in the fridge overnight.', 'In the morning, top with sliced banana, berries and honey.', 'Eat 2–3 hours before a long or hard ride.'])
SUPPS = [('Morning', 'Vitamin D3 with breakfast, in the winter months'), ('Before key sessions', 'Caffeine, about 3 mg per kg, 45–60 minutes before hard sessions and races only'),
         ('During long rides', 'Electrolytes in your bottles, more sodium on hot days'), ('After training', '20–30 g protein (whey or food) if your next meal is more than an hour away'),
         ('Only if needed', 'Iron, only when your blood panel shows low ferritin')]
def recipe(r, tag):
    return (f'<div class="cal-note"><div class="cal-nh"><span>Note</span><b>Nutrition</b><em>{tag}</em></div>'
            f'<p class="cal-rt">{E(r[0])}</p><p class="cal-rm">{E(r[1])}</p><p class="cal-rmac">{E(r[2])}</p>'
            f'<p class="cal-rh">Ingredients</p><ul>{"".join(f"<li>{E(x)}</li>" for x in r[3])}</ul>'
            f'<p class="cal-rh">Method</p><ol>{"".join(f"<li>{E(x)}</li>" for x in r[4])}</ol></div>')
notes = (recipe(RECIPE, 'Recipe') + recipe(BREAKFAST, 'Breakfast')
         + '<div class="cal-note"><div class="cal-nh"><span>Note</span><b>Nutrition</b><em>Supplements</em></div><p class="cal-rt">Supplement plan</p>'
           '<p class="cal-rm">Food first: supplements only where they help</p><dl class="cal-sup">'
         + ''.join(f'<dt>{E(t)}</dt><dd>{E(d)}</dd>' for t, d in SUPPS) + '</dl></div>')

FAQ = [
    ('Who is the nutrition consultation for?',
     'Anyone who wants to clean up their diet, boost energy levels and performance, manage their weight, support their immune system, improve their relationship with food, or simply get general guidance on nutrition.'),
    ('How does the consultation work?',
     SCHED + ' You receive a full, in-depth report and a personalised sports nutrition plan for your training and goals: daily meals and macros, fuelling around training, hydration and supplements where needed. You can book several sessions to add feedback and monitoring over a longer period.'),
    ('Can I add nutrition coaching to my cycling coaching?',
     'Yes. Nutrition coaching with Marine is an upgrade to any Cigala Cycling coaching package. She works from the same calendar as your coach, plans your nutrition around your training load, reviews your food diary and builds your race fuelling strategy. The price of the nutrition plan depends on the support you need: Marine will advise you in a free discovery call.'),
    ('Is nutrition included in my coaching package?',
     'Yes. Every package includes a nutritional guide, a blood panel review from our sports nutritionist and access to our nutritionist and mental coach. Advanced and Premium add a carbohydrate recommendation for every session and a nutritional consult with our sports nutritionist.'),
    ('What does a sports nutritionist do?',
     'A sports nutritionist plans what you eat around your training and racing: daily meals and macros for your training load, fuelling before, during and after sessions, hydration, recovery and race-day strategy, so you have the energy to train hard and perform.'),
    ('Do you work with triathletes and runners?',
     'Yes. Marine works with cyclists, triathletes, runners and other endurance athletes, from first-timers to professionals, in Ireland and worldwide.'),
    ('Can you help with stomach problems during races?',
     'Yes. Gut health and gastro-intestinal issues are part of what Marine covers, and gut training lets you build up to the carbs per hour your race needs without stomach problems.'),
    ('How many carbs per hour should I eat on the bike?',
     'It depends on how long and how hard the ride is, and on how much your gut is trained to take. Our free carbs-per-hour calculator gives you a starting number in seconds, and in coaching every session comes with its own recommendation (Advanced and Premium).'),
    ('How much should I drink when I ride?',
     'Sweat losses vary a lot between riders and with the weather. Weigh yourself before and after a ride with our free sweat-rate calculator to find out how much you lose per hour, then plan your bottles around it.'),
]
faq_html = ''.join(f'<details{" open" if i == 0 else ""}><summary><h3>{E(q)}</h3></summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(FAQ))
FAQ_LD = {'@context': 'https://schema.org', '@type': 'FAQPage',
          'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]}

HERO = img('unnamed-2.jpg', 'nutrition-hero-pasta')   # Matteo 15 Nov: not the strawberries
MARINE = conv('coaching/vivify/marine-lenehan-cutout.webp', 'nutrition-marine-lenehan-cutout')   # Matteo 15 Nov: background removed
MSIG = conv('coaching/vivify/marine-lenehan-signature-white.webp', 'nutrition-marine-lenehan-signature')   # her own portrait (vivifysports.com/about)
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
      <div class="nu-cut"><img src="{MARINE}" alt="{E(MARINE_ALT)}" loading="lazy" width="1385" height="1400"><img class="nu-sig" src="{MSIG}" alt="Marine Lenehan’s signature" loading="lazy" width="1820" height="405"></div>
      <figcaption>
        <b>Marine Lenehan</b>
        <span>MSc Sports Nutritionist · founder of <a class="viv" href="{VIVSITE}" {EXT}>Vivify Sports</a></span>
        <span>WorldTour professional cyclist with LIDL-TREK</span>
        <span>2× Irish National Champion (gravel 2026, criterium 2024) · Amateur Gravel World Champion 2024</span>
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
      <div class="cal-scroll" tabindex="0" aria-label="Example training week with nutrition notes"><div class="cal-row">{cal}</div></div>
      <div class="cal-notes">{notes}</div>
      <p class="cal-sample">These are samples only: Marine writes your recipes, meal plans and any supplement plan for you, after your assessment.</p>
      <figcaption>An athlete’s week: every session, Marine’s nutrition for each day, and recipes in the same calendar. <span class="cal-swipe">Swipe to see the whole week →</span></figcaption>
    </figure>
    <div class="nu-upg-cta panel">
      <p><b>An upgrade to any coaching package.</b> The price of your nutrition plan depends on the support you need: Marine will tell you in a free discovery call.</p>
      <div class="ctas"><a class="btn btn-go" href="{VIVSITE}contact" {EXT}>Book a free discovery call with Marine</a><a class="btn btn-ghost" href="{C}/individual-packages/" {EXT}>See the coaching packages</a></div>
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
.nu-cut { position: relative; }
.nu-cut > img:first-child { display: block; width: 100%; height: auto; -webkit-mask-image: linear-gradient(180deg, #000 78%, transparent); mask-image: linear-gradient(180deg, #000 78%, transparent); }
.nu-sig { position: absolute; left: 9%; right: 9%; bottom: 2%; width: 82%; height: auto; }
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
.nu-cal { margin: 0 0 22px; display: grid; grid-template-columns: minmax(0, 1fr); gap: 14px; align-items: start; }
.cal-notes { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; align-items: start; }
.cal-scroll { order: 0; }
.nu-cal figcaption { order: 1; }
.cal-notes { order: 2; }
.cal-sample { order: 3; margin: 0; color: var(--text-3); font-size: 13px; font-style: italic; }
.cal-sup { margin: 6px 0 0; display: grid; gap: 2px; }
.cal-sup dt { font-weight: 700; color: var(--text); margin-top: 8px; }
.cal-sup dd { margin: 0; }
.nu-cal figcaption { grid-column: 1 / -1; color: var(--text-3); font-size: 13px; }
@media (max-width: 1000px) { .nu-cal { grid-template-columns: minmax(0, 1fr); } }
.cal-scroll { border-radius: 14px; border: 1px solid var(--border); background: var(--panel-grad), var(--panel); }
.cal-row { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); }
.cal-d { border-right: 1px solid var(--border); padding: 0 7px 10px; display: grid; align-content: start; gap: 7px; min-width: 0; }
.cal-d:last-child { border-right: 0; }
.cal-h { margin: 0 -7px; padding: 8px 10px; border-bottom: 1px solid var(--border); background: rgba(255,255,255,.04); }
.cal-h b { font: 400 18px/1 var(--head); color: var(--text); }
.cal-cnt { justify-self: stretch; text-align: center; font-size: 11px; color: var(--text-3); border: 1px solid var(--border); border-radius: 6px; padding: 3px 0; }
.cal-n { background: rgba(0,154,68,.08); border: 1px solid rgba(0,154,68,.25); border-radius: 8px; padding: 7px 8px; display: grid; gap: 4px; }
.cal-n b { display: flex; align-items: center; gap: 5px; font-size: 12px; color: var(--text); }
.cal-n span { font-size: 11px; line-height: 1.4; color: var(--text-2); }
.cal-w { border: 1.5px solid #2fae5f; border-radius: 8px; background: rgba(255,255,255,.03); display: grid; gap: 5px; overflow: hidden; }
.cal-wt { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 5px; padding: 7px 8px 0; font-size: 11px; font-weight: 700; color: var(--text); }
.cal-wt span { min-width: 0; }
.cal-ic { width: 14px; height: 14px; fill: none; stroke: var(--green-text); stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; flex: none; }
.cal-ic2 { width: 14px; height: 14px; fill: none; stroke: var(--text-3); stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; flex: none; }
.cal-done { stroke: #2fae5f; }
.cal-tag { margin-left: auto; flex: none; color: #fff; font-size: 9px; font-weight: 700; padding: 2px 4px; border-radius: 3px; }
.cal-wn { display: flex; justify-content: space-between; gap: 6px; padding: 0 8px 7px; font-size: 12px; color: var(--text); line-height: 1.35; }
.cal-st { display: inline-flex; align-items: flex-start; gap: 4px; flex: none; }
.cal-com { display: inline-flex; align-items: center; gap: 2px; font-size: 10px; color: var(--text-3); }
.cal-com b { color: #f0bf00; font-weight: 700; }
.cal-cph { justify-self: start; display: inline-flex; align-items: center; gap: 4px; margin: 0 8px 4px; padding: 2px 9px; border: 1px solid #2bb3b1; border-radius: 999px; color: #47cbc9; font-size: 11px; font-weight: 700; }
.cal-cph svg { width: 11px; height: 11px; fill: none; stroke: currentColor; stroke-width: 2.2; }
.cal-trace { display: block; width: 100%; height: 22px; margin-top: -4px; }
.cal-trace rect { fill: rgba(255,255,255,.18); }
.cal-swipe { display: none; color: var(--green-text); font-style: normal; }
@media (max-width: 1100px) {
  .cal-scroll { overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: thin; }
  .cal-row { grid-template-columns: repeat(7, 165px); }
  .cal-d { scroll-snap-align: start; }
  .cal-swipe { display: inline; }
}
.cal-note { background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; color: var(--text-2); font-size: 13px; line-height: 1.55; }
.cal-nh { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.cal-nh span { font-weight: 700; color: var(--text); }
.cal-nh b { background: rgba(0,154,68,.18); color: var(--green-text); border-radius: 6px; padding: 3px 9px; font-size: 12px; }
.cal-nh em { font-style: normal; font-size: 12px; color: var(--text-3); }
.cal-note p { margin: 0; }
.cal-rt { font: 400 20px/1.15 var(--head) !important; text-transform: uppercase; color: var(--text); }
.cal-rm { color: var(--text-3); font-size: 12px; margin-top: 2px !important; }
.cal-rmac { color: var(--green-text); font-weight: 700; margin: 6px 0 4px !important; }
.cal-rh { font-weight: 700; color: var(--text); margin-top: 10px !important; }
.cal-note ul, .cal-note ol { margin: 4px 0 0; padding-left: 18px; }
.nu-uic { width: 28px; height: 28px; fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; margin-bottom: 8px; }
.nu-cal figcaption { margin-bottom: 8px; }
.nu-upg-cta { margin-top: 28px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 14px; padding: 18px 22px; margin-bottom: 26px; }
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
.nu-by { font-size: 11px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--red-text, #ff3d33); }
.nu-ptx h3 { margin: 0; color: var(--text); font-size: 20px; }
</style>'''
LD = f'<script type="application/ld+json">{json.dumps(FAQ_LD, ensure_ascii=False)}</script>'
build('nutrition', '/nutrition/', MAIN, 'Nutrition page: Vivify Sports with Marine, nutrition coaching as an upgrade, what is covered, nutrition posts, FAQ.',
      h1=H1, h2_changes={'drop': ['By Founder & Head Coach, Matteo Cigala'],
                         'add': ['WHAT’S COVERED', 'NUTRITION IN YOUR COACHING', 'FREE NUTRITION TOOLS', 'FREQUENTLY ASKED QUESTIONS']},
      extra_css=CSS, extra_js=LD)
print('nutrition: covered', len(COVERED) + len(MORE), 'posts', len(POSTS), 'faq', len(FAQ))
