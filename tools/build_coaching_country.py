"""Build the international Coaching pages: /cycling-coach-uk/, /cycling-coach-usa/, /cycling-coach-canada/.

Matteo 15 Nov 2026 ("Yes go ahead"): rewrite the three pages so each one has its own content instead of the same text with
a different country name, and stop showing testimonials under made-up names and places.

What stays as on live (SEO, CLAUDE.md): URL, Yoast title and meta description, the H1, every H2 (same wording), the
intro, the event and region lists, prices and GoCardless links in each currency, and the package feature lists.
What changed (logged in coaching/SEO-DECISIONS.md, section 10):
  - the five quotes were real testimonial excerpts (or rewordings of them) under invented UK/US/Canadian names.
    They are replaced by real testimonials, word for word, with the athlete's real name and home town.
  - FAQ answers, "how it works" and the region paragraph are written for each country (time zone, currency, climate,
    local events); the shared copy was 70% identical across the three pages.
  - typos fixed ("Canda", "reccomendations", "New York, UK"), Vekta's value shown in the page's own currency.
  - Premium shows the waiting list, as on the main Packages page (Matteo: Premium is sold out).

  python3 -I tools/build_coaching_country.py
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
import build_coaching_generic as G
import build_coaching_packages as P   # (rebuilds the packages page too: same output)

CAL = 'https://calendly.com/cigalacycling'
TP_LEVELS = P.TPLOGO

def rv(i):
    t, q, n, w, ph = REVIEWS[i]
    return (f'<figure class="rv"><div class="rv-stars" role="img" aria-label="5 stars">★★★★★</div><blockquote>“{E(q)}”</blockquote>'
            f'<figcaption><img src="{img(ph, "athlete-" + re.sub(r"[^a-z]+", "-", n.lower()).strip("-"))}" alt="{E(live_alt(ph))}" loading="lazy" width="48" height="48"><div><b>{E(n)}</b><span>{E(w)}</span></div></figcaption></figure>')
def strip(ids):
    return (f'<div class="rv-wrap"><div class="rv-row" id="rv-row" tabindex="0" aria-label="Athlete reviews, scroll sideways">{"".join(rv(i) for i in ids)}</div>'
            '<div class="rv-nav"><button type="button" class="rv-btn" data-d="-1" aria-label="Previous reviews">←</button><button type="button" class="rv-btn" data-d="1" aria-label="Next reviews">→</button></div></div>')

# REVIEWS index: 0 Marine, 1 Bernd (Germany), 2 Derek, 3 Lisa (Qatar), 4 Ceall (US stage race), 5 Ward (Mallorca 312),
# 6 Shane, 7 John Dowley, 8 William Rymer, 9 Gerard, 10 Rob, 11 Damian (winter + spring racing)
C_ = {
'uk': dict(
    name='the UK', adj='UK', cur='£', code='GBP', hero=('imgi_22_lABWBM7F', 'country-uk-hero-coaching'), pos='60% 35%', photo=('unnamed-6.png', 'country-uk-events-tre-valli'),
    vekta='£17.99', guides=[('fred-whitton-challenge-training-guide', 'How to train for the Fred Whitton Challenge'), ('slower-in-winter-is-not-your-legs', 'Slower in winter? It’s not your legs'), ('effective-fuelling-techniques-for-winter-training', 'Fuelling for winter training')], reviews=[5, 1, 8, 2, 11, 3],
    facts=[('clock', 'Same time as Ireland', 'GMT/BST: calls and replies happen in your own day, not overnight.'),
           ('currency', 'Prices in pounds', 'You pay in pounds, so no exchange fees on your side.'),
           ('route', 'Built for UK roads', 'Short steep climbs, wind, wet winters and the TT and sportive calendar.')],
    how=[('Sign up or talk first', 'Choose your package and sign up straight away, or book a free consultation with Matteo first. Ireland and the UK share a time zone, so a lunch break or an evening works.'),
         ('Testing & zones', 'Every package starts with tests (CP, FTP, FTHR or INSCYD) to set your zones. On Advanced and Premium, Matteo also does a deep assessment of your last 6–12 months of training data.'),
         ('Your plan', 'Sessions land in Vekta or TrainingPeaks and sync to your Garmin, Wahoo or Zwift: commute, club run and turbo nights included.'),
         ('Feedback', 'On Advanced and Premium, Matteo reviews your sessions (weekly or daily) and adjusts the week around work, family and the weather.')],
    region='The UK has some of the steepest climbs in Europe and a long, wet winter. Your plan uses both: hard, short efforts that suit the Peak District, the Lakes or the Welsh hills, and indoor sessions on the turbo when the roads are flooded.',
    faq={
     'Which package is right for me?': ['It depends on your budget and how much direct feedback you want. Basic (£195, one payment for 12 weeks) is a plan you follow on your own. Advanced (£135/month) adds Matteo: weekly feedback and schedule changes, a monthly call and Vekta membership, and it is our most popular package. Premium is the closest coaching, with daily contact; it is full at the moment, but you can join the waiting list.'],
     "I'm based in the UK — does coaching work remotely?": ['Yes, entirely. Plans, feedback and test analysis are in Vekta or TrainingPeaks and calls are on video. Ireland and the UK are on the same clock all year (GMT in winter, BST in summer), so you talk to Matteo during your own day and replies come the same day, not overnight.'],
     'Do you only coach people who race?': ['No. We coach riders working towards weight loss, their first 100-mile sportive, a Fred Whitton finish, general fitness, triathlon, club time trials or road racing. The only requirement is that you ride a bike and want to improve.'],
     'Do I need to switch from Training Peaks to Vekta?': ['No — we can continue working in Training Peaks if you’re already comfortable there, or explore Vekta’s Critical Power and W′ analytics alongside it.'],
     'What age do I need to be?': ['We coach all ages, 14 and up — no upper limit. Riders under U23 receive a 20% student discount, so juniors racing their first British Cycling events pay less.'],
     'My event is months away — can I still sign up now?': ['Yes, and earlier is better. The big UK sportives are in late spring and summer (the Fred Whitton and Etape Caledonia in May, the Dragon Ride in June), so starting in the winter gives you a base block, a build block and a taper. Pick the package that fits the time you have.'],
    },
    extra_q=('Do you coach time trials and hill climbs?', ['Yes. Time trials and hill climbs are short, all-out efforts, and we train them that way: pacing work, efforts at and above Critical Power, and sessions in your race position. Advanced and Premium include race and pacing strategy for each event.'])),
'usa': dict(
    name='the USA', adj='US', cur='$', code='USD', hero=('Vekta-x-Cigala', 'country-usa-hero-vekta', 'Vekta x Cigala Cycling: a training session in the Vekta app on a phone and a laptop'), pos='60% 50%', photo=('imgi_17_zCRmNmCA', 'country-usa-events-coaching'),
    vekta='$21.99', guides=[('tips-for-gravel-racing', 'Tips for gravel racing'), ('getting-started-with-gravel', 'Getting started with gravel'), ('heat-training', 'Heat training: why it is a game changer')], reviews=[4, 1, 7, 10, 6, 0],
    facts=[('clock', 'Works across US time zones', 'Feedback is written in Vekta or TrainingPeaks, so you never need to be online at the same time.'),
           ('currency', 'Prices in US dollars', 'You pay in dollars, so no exchange fees on your side.'),
           ('route', 'Climate and terrain', 'Altitude in Colorado, heat in Texas, long gravel days: the plan follows where you ride.')],
    how=[('Sign up or talk first', 'Choose your package and sign up straight away, or book a free consultation with Matteo first: the booking page shows the times in your own time zone.'),
         ('Testing & zones', 'Every package starts with tests (CP, FTP, FTHR or INSCYD) to set your zones. On Advanced and Premium, Matteo also does a deep assessment of your last 6–12 months of training data.'),
         ('Your plan', 'Sessions land in Vekta or TrainingPeaks and sync to your Garmin, Wahoo, Hammerhead or Zwift.'),
         ('Feedback', 'On Advanced and Premium, Matteo reviews your sessions (weekly or daily). Feedback and changes are written in Vekta or TrainingPeaks, so you read them when it suits you.')],
    region='From altitude in Colorado to heat and humidity in Texas and Florida and long gravel days in the Midwest, where you ride changes how you should train. Your plan is built for your terrain and climate, with heat, altitude and fuelling advice where you need it.',
    faq={
     'Which package is right for me?': ['It depends on your budget and how much direct feedback you want. Basic ($264, one payment for 12 weeks) is a plan you follow on your own. Advanced ($179/month) adds Matteo: weekly feedback and schedule changes, a monthly call and Vekta membership, and it is our most popular package. Premium is the closest coaching, with daily contact; it is full at the moment, but you can join the waiting list.'],
     "I'm based in the USA — does coaching work remotely?": ['Yes. All coaching is delivered online — plans, feedback, testing and communication happen asynchronously via Vekta or Training Peaks, so you never need to be online at the same time. Calls are booked at a time that suits you, whether you’re on the East Coast, West Coast, or anywhere between.'],
     'Do you only coach people who race?': ['No. We coach riders working toward weight loss, their first century ride, RAGBRAI, general fitness, Gran Fondos, gravel, triathlon or racing — the only requirement is that you ride a bike and want to improve.'],
     'Do I need to switch from Training Peaks to Vekta?': ['No — we can continue working in Training Peaks if you’re already comfortable there, or explore Vekta’s Critical Power and W′ analytics alongside it.'],
     'What age do I need to be?': ['We coach all ages, 14 and up — no upper limit. Riders under U23 receive a 20% student discount, which also covers juniors racing USA Cycling events.'],
     'My event is months away — can I still sign up now?': ['Yes, and earlier is better: a summer target like RAGBRAI in late July or a fall century gives you time for a base block, a build block and a taper. Pick the package that fits the time you have.'],
    },
    extra_q=('Can you coach me for a long gravel race?', ['Yes. Gravel and MTB are part of what we coach. Long gravel races are won or lost on pacing and fuelling as much as fitness: Advanced and Premium include daily carb recommendations for each session and a race and pacing strategy for the event.'])),
'canada': dict(
    name='Canada', adj='Canadian', cur='$', code='CAD', hero=('gran_fondo_strade_bianche_2022_img_1', 'country-canada-hero-matteo-win'), pos='45% 30%', photo=('pzrIm4dp1o9W5oO', 'country-canada-events-podium'),
    vekta='$30.99', guides=[('gran-fondo-whistler-training-guide', 'How to train for Gran Fondo Whistler'), ('slower-in-winter-is-not-your-legs', 'Slower in winter? It’s not your legs'), ('effective-fuelling-techniques-for-winter-training', 'Fuelling for winter training')], reviews=[11, 4, 1, 3, 8, 2],
    facts=[('snow', 'A real winter plan', 'Indoor blocks on Zwift, MyWhoosh or ROUVY so you start spring fit, not from zero.'),
           ('currency', 'Prices in Canadian dollars', 'You pay in Canadian dollars, so no exchange fees on your side.'),
           ('clock', 'Coast to coast', 'Feedback is written in Vekta or TrainingPeaks, so time zones don’t matter.')],
    how=[('Sign up or talk first', 'Choose your package and sign up straight away, or book a free consultation with Matteo first: the booking page shows the times in your own time zone.'),
         ('Testing & zones', 'Every package starts with tests (CP, FTP, FTHR or INSCYD) to set your zones. On Advanced and Premium, Matteo also does a deep assessment of your last 6–12 months of training data.'),
         ('Your plan', 'Sessions land in Vekta or TrainingPeaks and sync to your Garmin, Wahoo or your indoor app for the winter.'),
         ('Feedback', 'On Advanced and Premium, Matteo reviews your sessions (weekly or daily). Feedback and changes are written in Vekta or TrainingPeaks, so you read them when it suits you.')],
    region='In most of Canada the road season is short and the winter is long. Your year is planned around that: an indoor block with structured trainer sessions and gym work through the winter, then a short, focused build to your summer Gran Fondo.',
    faq={
     'Which package is right for me?': ['It depends on your budget and how much direct feedback you want. Basic (one payment for 12 weeks) is a plan you follow on your own. Advanced ($250 CAD/month) adds Matteo: weekly feedback and schedule changes, a monthly call and Vekta membership, and it is our most popular package. Premium is the closest coaching, with daily contact; it is full at the moment, but you can join the waiting list.'],
     "I'm based in Canada — does coaching work remotely? How you handle winter training?": [
        'Yes. All coaching is delivered online — plans, feedback, testing and communication happen asynchronously via Vekta or Training Peaks, so it works the same in Vancouver, Toronto or Halifax. Calls are booked at a time that suits both sides.',
        'Your plan includes a dedicated gym & winter programme, built for indoor trainer work (Zwift, RGT, MyWhoosh, etc.) during the colder months, periodised so you come into spring with a real fitness base rather than starting over.'],
     'Do you only coach people who race?': ['No. We coach riders working toward weight loss, their first Gran Fondo or Ride to Conquer Cancer, general fitness, gravel, triathlon or racing — the only requirement is that you ride a bike and want to improve.'],
     'Do I need to switch from Training Peaks to Vekta?': ['No — we can continue working in Training Peaks if you’re already comfortable there, or explore Vekta’s Critical Power and W′ analytics alongside it.'],
     'What age do I need to be?': ['We coach all ages, 14 and up — no upper limit. Riders under U23 receive a 20% student discount.'],
     'My event is months away — can I still sign up now?': ['Yes, and with a short outdoor season it pays to start early. For a September event like the RBC GranFondo Whistler, starting in the winter gives you an indoor base block, an outdoor build in spring and a taper. Pick the package that fits the time you have.'],
    },
    extra_q=None),
}
FIX = [('reccomendations', 'recommendations'), ('Canda', 'Canada'), ('New York, UK', 'New York, USA'), ('delivering in from coast to coast in Canada', 'from coast to coast in Canada'),
       ('remotely delivering in every', 'remotely in every')]
IC = {
    'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    'currency': P.ICON['currency'], 'route': '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
    'snow': '<path d="M12 2v20M4.9 4.9l14.2 14.2M2 12h20M4.9 19.1 19.1 4.9"/>',
}

def fix(s):
    for a, b in FIX: s = s.replace(a, b)
    return s

def lines(T, start, stop=('H2:', 'H1:')):
    i = T.index(start); out = []
    for l in T[i + 1:]:
        if l.startswith(stop): break
        out.append(l)
    return out

def build_country(key):
    c = C_[key]; name = f'cycling-coach-{key}'; path = f'/{name}/'
    T = open(ROOT + f'coaching/text/{name}.txt').read().split('\n')
    h1 = T[0][4:].strip()
    intro = [fix(l[3:]) for l in T[1:T.index(next(l for l in T if l.startswith('H2:')))] if l.startswith('P: ')]
    h2s = [l[4:].strip() for l in T if l.startswith('H2: ')]
    H = lambda pref: next(h for h in h2s if h.startswith(pref))
    why_h2 = H('Why ')
    why = [fix(l[4:]) for l in lines(T, 'H2: ' + why_h2) if l.startswith('LI: ')]
    why = [re.sub(r'€19\.99/month', f'{c["vekta"]}/month', x) for x in why]
    ev_h2 = H('Events We Help'); ev = lines(T, 'H2: ' + ev_h2)
    ev_p = [fix(l[3:]) for l in ev if l.startswith('P: ')]
    ev_li = [fix(re.sub(r'\*\*\s*\n\s*\*\*', '', l[4:]).strip()) for l in '\n'.join(ev).replace('\n**\n**', '').split('\n') if l.startswith('LI: ')]
    rg_h2 = H('Coaching Cyclists Across'); rg = '\n'.join(lines(T, 'H2: ' + rg_h2))
    rg_p = [fix(x) for x in re.findall(r'^P: (.*)$', rg, re.M)]
    rg_li = [fix(re.sub(r'\*\*\s*$', '', x.replace('— **', '— ').replace('**California — **', '**California** — ')).strip()) for x in re.findall(r'^LI: (.*(?:\n\*\*)?)', rg, re.M)]
    rg_li = [x.replace('\n**', '').rstrip('*').strip() for x in rg_li]
    rg_li = [re.sub(r'^\*\*([^*]+?) — ', r'**\1** — ', x) if x.count('**') == 1 else x for x in rg_li]   # live USA: "**California — **LA ...**"
    end_h2 = H('Personalised to your goals')
    nums = re.findall(r'H3: (.+)\nH4: (.+)', '\n'.join(lines(T, 'H2: 2025 IN NUMBERS', ('H2:',))))
    # prices + payment links from the live page
    html_src = open(ROOT + f'coaching/html/{name}.html').read()
    pay = {lab.strip(): u for u, lab in re.findall(r'<option value="(https://[^"\s]+)\s*"[^>]*>\s*([^<]+?)\s*<', html_src)}
    pb = lambda k: next(l for l in lines(T, 'H2: ' + k, ('LABEL:',)))
    def price(k): return next(l[5:].strip() for l in lines(T, 'H2: ' + k, ('LABEL:',)) if l.startswith('TXT: ') and re.match(r'TXT: [£$]', l))
    sub_basic = next(l[3:] for l in lines(T, 'H2: Basic', ('LABEL:',)) if l.startswith('P: '))
    if key == 'canada':   # live card said $387 ($129/mo) but the live Revolut link charges 390 CAD: show what is charged
        sub_basic = sub_basic.replace('$387', '$390 CAD')
    prem_sub = next(l[3:] for l in lines(T, 'H2: Premium', ('LABEL:',)) if l.startswith('P: '))
    adv_lab = next(k for k in pay if k.startswith('Advanced')); bas_lab = next(k for k in pay if k.startswith('Basic'))
    p3 = next(k for k in pay if k.startswith('Premium 3')); p6 = next(k for k in pay if k.startswith('Premium 6'))
    nump = lambda s: re.search(r'(\d+) ' + c['code'], s).group(1)
    bp, bper = re.match(r'([£$][\d.]+)(/\w+)', price('Basic')).groups()
    if key == 'canada': bp = '$130'
    ap, aper = re.match(r'([£$][\d.]+)(/\w+)', price('Advanced')).groups()
    pp, pper = re.match(r'([£$][\d.]+)(/\w+)', price('Premium')).groups()
    cur_note = ' CAD' if key == 'canada' else ''   # Matteo 15 Nov: no currency codes, except CAD ($ alone reads as US dollars)
    cards = ''.join([
        P.card('basic', 'Basic', '12 Weeks', bp, bper, sub_basic,
               # the live country pages have no payment link for Basic: start with the free call
               # Basic pays by the live Revolut checkout link (one payment), as on the live pages
               P.btn(f'Buy Basic 12 Weeks · {c["cur"]}{nump(bas_lab)}{cur_note}', pay[bas_lab])),
        P.card('advanced', 'Advanced', '6 months subscription', ap, aper, '',
               P.btn(f'Subscribe to Advanced · {c["cur"]}{nump(adv_lab)}{cur_note}/mo', pay[adv_lab]),
               '<span class="pkg-badge">Monthly (Our Most Popular)</span>', 'hot'),
        P.card('premium', 'Premium', fix(prem_sub), pp, pper, '',
               '<a class="btn btn-go pay" href="#contact" data-waitlist="Premium">Join the waiting list</a>'
               f'<span class="pay-note">Premium 3 months {c["cur"]}{nump(p3)}{cur_note}/mo · 6 months {c["cur"]}{nump(p6)}{cur_note}/mo</span>',
               '', 'sold'),   # Matteo 15 Nov: no sold-out badge, the SOLD OUT stamp is enough
    ])
    # feature lines in this page's currency (the live country lists use these values)
    vals = dict(re.findall(r'^LI: (Access to our online Community|Vekta membership included) \(value ([^)]*)\)', '\n'.join(T), re.M))
    cards = cards.replace('(value €9/m)', f'(value {vals["Access to our online Community"]})').replace('(value €19.99/m)', f'(value {vals["Vekta membership included"]})')
    assert '€' not in cards, re.findall(r'.{30}€.{20}', cards)
    cad_note = '<p class="cur-note">Prices in Canadian Dollar (CAD)</p>' if key == 'canada' else ''

    def img_of(k, n, alt=None):
        u = next(u for u in G.WEBP if k in u); return img(u.split('/uploads/')[1], n), alt or live_alt(k)
    hsrc, halt = img_of(*c['hero']); psrc, palt = img_of(*c['photo'])
    facts = ''.join(f'<div class="note"><svg viewBox="0 0 24 24" aria-hidden="true">{IC[i]}</svg><p><b>{E(t)}</b><br>{E(d)}</p></div>' for i, t, d in c['facts'])
    steps = c['how'] + [('Nutrition, if you want it', 'Add 1-to-1 nutrition coaching with our sports nutritionist, Marine Lenehan (WorldTour Pro): daily macros, carbs per hour and notes in the same calendar as your training.')]
    how = ''.join(f'<li class="cn-day"><div class="cn-num"><span><small>STEP</small>{i + 1}</span></div><div class="panel cn-box"><h3 class="h-sm">{E(t)}</h3><p>{E(d)}</p></div></li>' for i, (t, d) in enumerate(steps))
    faq = list(c['faq'].items()) + ([c['extra_q']] if c['extra_q'] else []) + [NUT_Q]
    live_q = [l[5:].strip() for l in lines(T, 'H2: FREQUENTLY ASKED QUESTIONS', ('H1:',)) if l.startswith('TXT: ')]
    assert [q for q, _ in faq][:len(live_q)] == live_q, ([q for q, _ in faq], live_q)   # every live question kept, same wording
    faq_html = ''.join(f'<details{" open" if i == 0 else ""}><summary><h3>{E(q)}</h3></summary>' + ''.join(f'<p>{E(p)}</p>' for p in ps) + '</details>' for i, (q, ps) in enumerate(faq))
    nums_html = ''.join(f'<div class="stat"><h3 class="n" data-count="{E(n)}">{E(n)}</h3><h4 class="l">{E(l)}</h4></div>' for n, l in nums)
    tick = lambda xs: '<ul class="ticks">' + ''.join(f'<li>{G.inline(x)}</li>' for x in xs) + '</ul>'

    MAIN = f'''<div class="hero hero-sm">
  <img src="{hsrc}" alt="{E(halt)}" style="object-position: {c['pos']}">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Online cycling coaching</div>
    <h1>{E(h1)}</h1>
    <p class="lede">{G.inline(intro[0])}</p>
    <div class="ctas"><a class="btn btn-go" href="{CAL}" {EXT}>Book free consultation</a><a class="btn btn-ghost" href="#packages">See the packages ↓</a></div>
  </div>
</div>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">Your coach</div>
      {''.join(f'<p>{G.inline(x)}</p>' for x in intro[1:])}
    </div>
    <div class="notes cn-facts">{facts}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Why riders choose us</div><h2>{E(why_h2)}</h2><div class="bar"></div></div></div>
    <div class="gn-txt cn-why">{tick(why)}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">#TrainSmarterRideFaster</div><h2>It's our vision</h2><div class="bar"></div></div>
      <div class="rv-links"><a class="arrow-link" href="{GOOGLE_REVIEWS}" {EXT}><span class="gstar" aria-hidden="true">★</span> Read our reviews on Google →</a><a class="arrow-link" href="{C}/case-studies/" {EXT}>Case studies →</a></div></div>
    <p class="cn-lede">Real athletes, in their own words, with their own names and home towns.</p>
    {strip(c['reviews'])}
  </div>
</section>

<section id="packages">
  <div class="in">
    <div class="head"><div><div class="eyebrow">Choose your package</div><h2>COACHING PACKAGES</h2><div class="bar"></div></div></div>
    {cad_note}
    <div class="pkgs">{cards}</div>
    <p class="terms"><b>By subscribing to any of our packages, you accept our Terms &amp; Conditions. View T&amp;C <a href="{C}/terms-conditions/" {EXT}>HERE</a></b></p>
    <div class="vk-logos cn-tp">
      <a class="vk-lock" href="https://joinvekta.com/partnerships" {EXT} aria-label="{E(live_alt('SDFASDFASDF'))}"><img src="{LOGO}" alt="" loading="lazy" width="64" height="64"><svg class="vk-x" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 4l12 12M16 4L4 16"/></svg><img src="{P.VKLOGO}" alt="{E(live_alt('SDFASDFASDF'))}" loading="lazy" width="531" height="139"></a>
      <span><img src="{TP_LEVELS}" alt="{E(live_alt('PfNJBaCPkS_eSn5J'))}" loading="lazy"></span>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Getting started from {E(c["name"])}</div><h3 class="h-sec">HOW IT WORKS</h3><div class="bar"></div></div></div>
    <div class="cn-howgrid">
      <ol class="cn-days">{how}</ol>
      <figure class="nu-cal pk-cal cn-cal">
        <div class="cal-scroll" tabindex="0" aria-label="Example days from an athlete's calendar, with nutrition"><div class="cal-row">{P.NUT.cal_days(('21', '24', '26'))}</div></div>
        <figcaption>Example days from an athlete’s calendar: your sessions and, with nutrition coaching, Marine’s notes and carbs per hour. <a href="{C}/nutrition/#upgrade" {EXT}>Read more about nutrition coaching →</a></figcaption>
      </figure>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Press &amp; partners</div><h2>AS SEEN IN</h2><div class="bar"></div></div></div>
    {seen_logos()}
  </div>
</section>

<section>
  <div class="in split gn-split">
    <div class="gn-txt">
      <div class="eyebrow">Your target</div>
      <h2>{E(ev_h2)}</h2><div class="bar"></div>
      <p>{G.inline(ev_p[0])}</p>
      <ul class="cn-chips">{''.join(f'<li>{G.inline(x)}</li>' for x in ev_li)}</ul>
      {''.join(f'<p>{G.inline(x)}</p>' for x in ev_p[1:])}
      <h3 class="h-sm cn-gh">Guides from our blog</h3>
      <ul class="cn-guides cn-gcards">{''.join(f'<li><a class="arrow-link" href="{C}/blog/{u}/" {EXT}>{E(t)} →</a></li>' for u, t in c['guides'])}</ul>
    </div>
    <div class="photo gn-photo cn-evphoto"><img src="{psrc}" alt="{E(palt)}" loading="lazy"></div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Results</div><h2>2026 IN NUMBERS</h2><div class="bar"></div></div></div>
    <div class="stats nums">{nums_html}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head">
      <div><div class="eyebrow">Real results</div><h2>READ OUR CASE STUDIES</h2><div class="bar"></div></div>
      <div class="rv-links"><a class="btn btn-go" href="{C}/case-studies/" {EXT}>Read our case studies</a></div>
    </div>
    {case_cards(C + '/case-studies/')}
  </div>
</section>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">Where we coach</div>
      <h2>{E(rg_h2)}</h2><div class="bar"></div>
      <p>{G.inline(rg_p[0])}</p>
      <ul class="cn-regions">{''.join(f'<li>{G.inline(x)}</li>' for x in rg_li)}</ul>
      <p>{E(c["region"])}</p>
      {''.join(f'<p>{G.inline(x)}</p>' for x in rg_p[1:])}
    </div>
    <div>
      <div class="eyebrow">Works with your devices &amp; apps</div>
      <div class="logos apps cn-apps">{P.devices}</div>
    </div>
  </div>
</section>

<div class="cn-ft">{tools_band()}</div>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Good to know</div><h2>FREQUENTLY ASKED QUESTIONS</h2><div class="bar"></div></div></div>
    <div class="faq">{faq_html}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="band band-cta">
      <img src="{img('unnamed-8-1.jpg', 'matteo-worlds-silver')}" alt="{E(live_alt('unnamed-8-1.jpg'))}" loading="lazy" width="1280" height="1600">
      <div class="tx">
        <div class="eyebrow">Start working with Matteo</div>
        <h2>{E(end_h2)}</h2>
        <div class="bar"></div>
        <div class="ctas"><a class="btn btn-go" href="{CAL}" {EXT}>Book Free Consultation</a><a class="btn btn-ghost" href="#packages">See the packages</a></div>
      </div>
    </div>
  </div>
</section>

{G.contact_block('READY TO TAKE YOUR CYCLING TO THE NEXT LEVEL?', 'Questions about coaching from ' + c["name"] + '? Send us a message and Matteo will get back to you.')}'''
    JS = REVIEWS_JS + P.PJS.replace("document.getElementById('g-more').addEventListener", "document.getElementById('g-more') && document.getElementById('g-more').addEventListener") \
        .replace("document.getElementById('g-more').dataset.label = document.getElementById('g-more').textContent;", '')
    build(name, path, MAIN, f'{path} rewritten for {c["name"]}: own copy, real testimonials, prices in {c["code"]}. H1, H2s and lists kept.',
          h1=h1, h2_changes={'drop': ['2025 IN NUMBERS', 'READ OUR TESTIMONIALS - WHAT PEOPLE SAY ABOUT CIGALA CYCLING'], 'add': ['2026 IN NUMBERS', 'READ OUR CASE STUDIES']},   # Matteo 15 Nov: 2026; case studies
          extra_css=G.GCSS + P.PCSS + FT_CSS + CS_CSS + P.CAL_CSS + CCSS, extra_js=JS)
    words = len(re.sub(r'<[^>]+>', ' ', MAIN).split())
    print(name, 'words', words, 'reviews', len(c['reviews']), 'faq', len(faq))

NUT_Q = ('Can I work 1-to-1 with a nutritionist?', ['Yes. You can add nutrition coaching with our sports nutritionist, Marine Lenehan: a WorldTour Pro with LIDL-TREK, 2× Irish National Champion and Amateur Gravel World Champion 2024. She writes your daily macros, carbs per hour and nutrition notes into the same calendar as your training, reviews your food diary and plans your race fuelling and gut training. The price depends on what you need, and is agreed with Marine.'])
CCSS = '''<style>
.cn-facts { grid-template-columns: 1fr; align-content: center; }
.cn-facts .note p { margin: 0; }
.cn-lede { color: var(--text-2); margin: -6px 0 18px; }
.cn-why .ticks { columns: 2 340px; column-gap: 32px; }
.cn-why .ticks li { break-inside: avoid; }
.cur-note { color: var(--text-3); font-size: 14px; margin: 0 0 14px; }
.cn-tp { max-width: 760px; margin: 26px auto 0; }
@media (max-width: 600px) { .cn-tp { grid-template-columns: 1fr; } }
.cn-howgrid { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 32px; align-items: start; }
.cn-cal { position: sticky; top: 110px; }
@media (max-width: 1000px) { .cn-howgrid { grid-template-columns: 1fr; } .cn-cal { position: static; } }
.cn-days { list-style: none; margin: 0; padding: 0; }
.cn-day { display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 20px; position: relative; padding-bottom: 20px; }
.cn-day::before { content: ""; position: absolute; left: 31px; top: 64px; bottom: 0; width: 2px; background: var(--border-strong); }
.cn-day:last-child { padding-bottom: 0; }
.cn-day:last-child::before { display: none; }
.cn-num { width: 64px; height: 64px; border-radius: 50%; display: grid; place-items: center; background: var(--panel-solid, #16181a); border: 2px solid var(--green); font: 400 26px/1 var(--head); color: var(--text); text-align: center; }
.cn-num small { display: block; font: 700 9px/1 var(--body); letter-spacing: .12em; color: var(--text-3); margin-bottom: 3px; }
.cn-box { padding: 18px 22px; min-width: 0; }
.cn-box h3 { margin: 0 0 6px; }
.cn-box p { margin: 0; color: var(--text-2); font-size: 15px; line-height: 1.55; }
@media (max-width: 600px) { .cn-day { grid-template-columns: 48px minmax(0, 1fr); gap: 14px; } .cn-num { width: 48px; height: 48px; font-size: 20px; } .cn-num small { font-size: 8px; } .cn-day::before { left: 23px; top: 48px; } .cn-box { padding: 16px; } }
.cn-chips, .cn-regions { list-style: none; margin: 14px 0 16px; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 8px; }
.cn-chips li, .cn-regions li { padding: 10px 12px; border: 1px solid var(--border); border-radius: 10px; background: rgba(255,255,255,.03); font-size: 14px; line-height: 1.4; color: var(--text-2); }
.cn-chips li strong, .cn-regions li strong, .cn-chips li b, .cn-regions li b { color: var(--text); }
@media (max-width: 600px) { .cn-chips, .cn-regions { grid-template-columns: 1fr 1fr; gap: 6px; } .cn-chips li, .cn-regions li { padding: 8px 10px; font-size: 13px; } }
.cn-gcards { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)) !important; }
.cn-gcards li a { display: block; padding: 10px 12px; border: 1px solid var(--border); border-radius: 10px; font-size: 14px; }
@media (max-width: 600px) { .cn-ft .ft-cards { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 10px; padding-bottom: 6px; } .cn-ft .ft-card { flex: 0 0 78%; scroll-snap-align: start; } .cn-ft .ft-box { padding: 20px; gap: 18px; }
  .cn-apps { grid-template-columns: repeat(4, minmax(0, 1fr)) !important; gap: 8px !important; } }
@media (max-width: 600px) { .cn-evphoto { aspect-ratio: 16 / 10 !important; height: auto !important; min-height: 0 !important; } .cn-evphoto img { height: 100% !important; } }
.cn-how { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; counter-reset: none; }
.cn-how li { display: grid; grid-template-columns: auto 1fr; gap: 14px; padding: 20px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); }
.cn-how .hw-n { width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; background: var(--green); color: #08090a; font-weight: 800; }
.cn-how h3 { margin: 4px 0 6px; }
.cn-how p { margin: 0; color: var(--text-2); font-size: 15px; line-height: 1.55; }
.cn-gh { margin: 24px 0 8px; }
.cn-guides { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.cn-apps { margin-top: 14px; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
</style>'''

if __name__ == '__main__':
    for k in (sys.argv[1:] or C_):
        build_country(k)
