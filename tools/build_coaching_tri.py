"""Build the Triathlon Individual Packages preview: coachingpages/tri-individual-packages.html

Same design as the cycling packages page (tools/build_coaching_packages.py); its CSS and helpers are reused.
All live copy is kept: package names, prices, every feature line, FAQ (live H2s), payment links.
Approved: H1 "TRIATHLON INDIVIDUAL PACKAGES" (the page's existing top line, coaching/SEO-DECISIONS.md).
Matteo 15 Nov, applied as on the cycling page: Premium is sold out -> waiting list; Basic does not include training analysis.
The live Tri Basic buy link is an expired Shopify checkout (redirects to the shop home).
Matteo 15 Nov: "the pricing and the structure of the pricing, copy, and also the link: copy the individual coaching" ->
same prices, wording and payment links as the cycling Individual Packages page (Basic €19/week, €228 one payment;
Advanced 6 months €149/mo; Premium sold out). The intro said "2 coaching packages: Advanced and Premium": it is 3.
"""
import os, sys, io, re, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
with contextlib.redirect_stdout(io.StringIO()):
    import build_coaching_packages as P          # reuse CSS and helpers (rebuilds the cycling page, harmless)

PATH = '/tri-individual-packages/'
SRC = open(ROOT + 'coaching/html/tri-individual-packages.html').read()
TXT = open(ROOT + 'coaching/text/tri-individual-packages.txt').read().split('\n')

def feats(after):
    i = TXT.index(after); out = []
    for l in TXT[i + 1:]:
        if l.startswith('LI: '): out.append(re.sub(r'\s+', ' ', l[4:]).strip())
        elif l.startswith('LABEL:'): break
    return out
F = {'basic': feats('H2: Basic Package'), 'advanced': feats('H2: Advanced'), 'premium': feats('H2: Premium')}
norm = lambda s: s.lower().replace('metabolic inscyd testing', 'inscyd metabolic testing')
common = [f for f in F['advanced'] if all(norm(f) in map(norm, F[k]) for k in F)]
own = {k: [f for f in v if norm(f) not in map(norm, common)] for k, v in F.items()}
PAY = {label.strip(): url for url, label in re.findall(r'<option value="(https://[^"]+)"[^>]*>\s*([^<]+?)\s*<', SRC)}
NOT_IN_BASIC = {'Feedback on sessions', 'Schedule Adjustment', 'Daily Training Analysis'}   # marked excluded on the live page

FOR = {
    'basic': 'A 12-week plan built in advance, for triathletes who can follow the training on their own.',
    'advanced': 'For triathletes committed to a disciplined programme with definitive seasonal goals. Our most popular package.',
    'premium': 'For triathletes who want the very best and the utmost from their personal coach.',
}
def card(key, h2, term, price, per, sub, buttons, badge='', cls=''):
    top = [x for x in own[key] if not (key == 'basic' and x in NOT_IN_BASIC)]
    no = [x for x in own[key] if key == 'basic' and x in NOT_IN_BASIC]
    rest = [f for f in F[key] if f not in own[key]]
    # same as the cycling cards (Matteo 15 Nov): what you get first, 12 lines visible, Basic's missing lines last
    LBL = {'Race Strategy': 'Race & Pacing Strategy', 'Access to World Class Nutritionist & Mental Coach': 'Access to work 1-to-1 with our World Class Nutritionist & Mental Coach'}
    inc = top + rest
    items = ''.join(f'<li{" class=\"more\"" if i >= 12 else ""}>{E(LBL.get(x, x))}</li>' for i, x in enumerate(inc))
    if no:
        items += '<li class="more no-lab">Included in Advanced &amp; Premium</li>' + ''.join(
            f'<li class="more no">{E({"Daily Training Analysis": "Training Analysis"}.get(x, x))}<span class="vh"> (not included in Basic)</span></li>' for x in no)
    total = len(inc)
    return f'''<article class="pkg {cls}" id="pkg-{key}">
        {badge}
        <div class="pkg-term">{term}</div>
        <h2>{h2}</h2>
        <p class="pkg-for">{FOR[key]}</p>
        <div class="pkg-price"><b>{price}</b><span>{per}</span></div>
        <p class="pkg-sub">{sub}</p>
        <div class="pkg-buy">{buttons}<a class="pkg-call" href="{P.CAL}" {EXT}>Not sure? Book a free consultation →</a></div>
        <div class="pkg-lab">What you get</div>
        <ul class="ticks">{items}</ul>
        <button type="button" class="pkg-all" aria-expanded="false"><span>See all features</span><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 8l5 5 5-5"/></svg></button>
      </article>'''

cards = ''.join([
    card('basic', 'Basic Package', '12 Weeks', '€19', '/week', 'Charged with one-time payment of €228 for the 12 weeks.',
         P.btn('Buy Basic 12 Weeks · €228', P.pay['Basic 12 Weeks: 228 EUR - one-time payment'])),
    card('advanced', 'Advanced', '6 months subscription', '€149', '/mo', '',
         P.btn('Subscribe to Advanced · €149/mo', P.pay['Advanced 6 months: 149 EUR - monthly']),
         '<span class="pkg-badge">Monthly (Our Most Popular)</span>', 'hot'),
    card('premium', 'Premium', '3 months subscription (€10 off for 6 mo)', '€249', '/mo', '',
         '<a class="btn btn-go pay" href="#contact" data-waitlist="Triathlon Premium">Join the waiting list</a>'
         '<span class="pay-note">Premium 3 months €249/mo · 6 months €239/mo</span>',
         '', 'sold'),   # Matteo 15 Nov: no sold-out badge, the SOLD OUT stamp is enough
])
Y, N = '<span class="y" aria-label="Included">✓</span>', '<span class="n" aria-label="Not included">✗</span>'
ROWS = [
    ('Coaching package', 'Daily plan built for 12 weeks', 'Daily plan built on a weekly basis', 'Daily plan built on a weekly basis'),
    ('Contact', 'When needed via email', 'Weekly', 'Daily'),
    ('Feedback', 'On sessions', 'Weekly', 'Daily'),
    ('Schedule adjustment', Y, 'Weekly', 'Daily'),
    ('Training analysis', N, 'Weekly', 'Daily'),
    ('Catch up call', N, 'Monthly or when needed', 'Weekly or when needed'),
    ('Race strategy', N, Y, Y),
    ('Continuous support &amp; motivation', N, Y, Y),
    ('Platform', 'Training Peaks membership included (value €19.99/m)', 'Training Peaks membership included (value €19.99/m)', 'Training Peaks membership included (value €19.99/m)'),
    ('Price', '€237 one-time for 12 weeks', '€149/mo', '€249/mo for 3 months'),
]
compare = ('<div class="cmp-wrap"><h3 class="h-sm">Compare coaching packages</h3><div class="bar"></div><div class="cmp-scroll"><table class="cmp">'
           '<thead><tr><th scope="col"><span class="vh">Feature</span></th><th scope="col">Basic</th><th scope="col" class="hot">Advanced</th><th scope="col">Premium</th></tr></thead><tbody>'
           + ''.join(f'<tr><th scope="row">{r[0]}</th><td data-l="Basic">{r[1]}</td><td class="hot" data-l="Advanced">{r[2]}</td><td data-l="Premium">{r[3]}</td></tr>' for r in ROWS)
           + '</tbody></table></div><p class="cmp-note">Every package also includes the plan tailored to your availability, testing, nutrition support, the gym &amp; winter program, our community and more: open “Show all” on each card for the full list.</p></div>')

# FAQ: the questions are H2s on live, so they stay H2s
faq, cur = [], None
for l in TXT[TXT.index('H2: FREQUENTLY ASKED QUESTIONS') + 1:TXT.index('H2: #TrainSmarterRideFaster')]:
    if l.startswith('H2: '): cur = [l[4:], []]; faq.append(cur)
    elif cur and l.startswith('P: '): cur[1].append(l[3:])
    elif cur and l.strip(): cur[1][-1] += '\n' + l
faq_html = ''.join(f'<details{" open" if i == 0 else ""}><summary><h2>{E(q)}</h2></summary>' + ''.join(f'<p>{P.md(p).replace(chr(10), "<br>")}</p>' for p in ps) + '</details>' for i, (q, ps) in enumerate(faq))
# Matteo 15 Nov: working 1-to-1 with the nutritionist (an H3: the live FAQ questions are H2s and stay as they are)
faq_html += ('<details><summary><h3>Can I work 1-to-1 with a sports nutritionist?</h3></summary><p>Yes. Every package includes access to our sports nutritionist, '
             'Marine Lenehan (MSc, WorldTour professional cyclist). You can also add nutrition coaching with her: daily macros and carbs per hour in the same calendar as '
             f'your swim, bike and run sessions, food diary reviews and a race fuelling plan. <a href="{C}/nutrition/#upgrade" {EXT}>Read more about nutrition coaching</a></p></details>')
assert len(faq) == 5, faq

LOGOS = [('imgi_4_wHe4MESD', 'logo-red-bull'), ('imgi_6_6_MxiOhd', 'logo-stickybottle'), ('unnamed-87.png', 'logo-zwift'),
         ('unnamed-86.png', 'logo-trainingpeaks'), ('unnamed-84.png', 'logo-cycling-ireland'), ('unnamed-85.png', 'logo-vekta')]
logos = ''.join(f'<span><img src="{img(k, n)}" alt="{E(live_alt(k))}" loading="lazy"></span>' for k, n in LOGOS)
apps = (f'<a href="https://www.trainingpeaks.com/" {EXT}><img src="{img("unnamed-86.png", "logo-trainingpeaks")}" alt="{E(live_alt("unnamed-86.png"))}" loading="lazy"></a>'
        f'<a href="https://zwift.com/" {EXT}><img src="{img("unnamed-87.png", "logo-zwift")}" alt="{E(live_alt("unnamed-87.png"))}" loading="lazy"></a>')

HERO = img('imgi_24__E7-jKP0', 'triathlon-coaching')
RACE = img('imgi_16_d3HssY4x', 'triathletes-racing')
intro = [l[3:] for l in TXT[:TXT.index('TXT: 12 Weeks')] if l.startswith('P: ')]
assert intro[0] == 'TRIATHLON INDIVIDUAL PACKAGES', intro

MAIN = f'''<div class="hero hero-sm">
  <img src="{HERO}" alt="Triathlete standing by a lake at sunrise" width="1600" height="1200">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Triathlon coaching</div>
    <h1>TRIATHLON INDIVIDUAL PACKAGES</h1>
    <p class="lede">{E(intro[1].replace('We have 2 coaching packages: Advanced and Premium', 'We have 3 coaching packages: Basic, Advanced and Premium'))}<br>{E(intro[2])}<br>{E(intro[3])}</p>
    <div class="ctas">
      <a class="btn btn-go" href="{P.CAL}" {EXT}>Book free consultation</a>
      <a class="btn btn-ghost" href="#packages">Compare coaching packages ↓</a>
    </div>
  </div>
</div>

<section id="packages">
  <div class="in">
    {P.notes_strip([('currency', E(intro[4])), ('student', '*Underage, Juniors &amp; U23 will avail of a 20% student discount for all packages')]).replace('class="notes"', 'class="notes notes-2"')}
    <div class="pkgs">
      {cards}
    </div>
    {compare}
    <p class="terms"><b>By subscribing to any of our packages, you accept our Terms &amp; Conditions. View T&amp;C <a href="{C}/terms-conditions/" {EXT}>HERE</a></b></p>
  </div>
</section>

<section>
  <div class="in">
    <div class="head">
      <div><div class="eyebrow">Our athletes</div><h3 class="h-sec">WHAT OUR ATHLETES SAY</h3><div class="bar"></div></div>
      <div class="rv-links"><a class="arrow-link" href="{GOOGLE_REVIEWS}" {EXT}><span class="gstar" aria-hidden="true">★</span> Read our reviews on Google →</a><a class="arrow-link" href="{C}/testimonials/" {EXT}>All testimonials →</a></div>
    </div>
    {reviews_strip()}
  </div>
</section>

<!-- Matteo 15 Nov: 'Follow your plan on' section removed (TrainingPeaks and Zwift logos stay under As seen in) -->

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Good to know</div><h2>FREQUENTLY ASKED QUESTIONS</h2><div class="bar"></div></div></div>
    <div class="faq">{faq_html}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="band band-cta">
      <img src="{RACE}" alt="{E(live_alt('imgi_16_d3HssY4x'))}" loading="lazy" width="1600" height="1067">
      <div class="tx">
        <h2 class="hashtag">#TrainSmarterRideFaster</h2>
        <div class="bar"></div>
        <p class="lede">Our triathlon coaching covers all disciplines of triathlon from Sprint to Ironman.</p>
        <div class="ctas"><a class="btn btn-go" href="{P.CAL}" {EXT}>Book free consultation</a><a class="btn btn-ghost" href="{C}/about2/" {EXT}>About our triathlon coaching</a></div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Press &amp; partners</div><h2>AS SEEN IN</h2><div class="bar"></div></div></div>
    {seen_logos()}
  </div>
</section>

<section id="contact">
  <div class="in split">
    <div class="photo rider"><img src="{img('photo-1533049426476', 'triathlon-open-water-swim')}" alt="Triathletes swimming in open water during a race" loading="lazy" width="1600" height="1068"></div>
    <div>
      <div class="eyebrow">Check availability</div>
      <h3 class="h-sec">READY TO TAKE YOUR TRIATHLON TO THE NEXT LEVEL?</h3>
      <div class="bar"></div>
      <p class="lede">{E(intro[4])}</p>
      <form class="form panel" method="post" action="#" onsubmit="return false">
        <label>Name<input name="form_fields[name]" type="text" placeholder="Name *" required autocomplete="name"></label>
        <label>Email<input name="form_fields[email]" type="email" placeholder="Email *" required autocomplete="email"></label>
        <label>Phone<input name="form_fields[phone]" type="tel" placeholder="Phone (with country code) *" required autocomplete="tel"></label>
        <label>Message<textarea name="form_fields[message]" placeholder="Your Message *" rows="5" required></textarea></label>
        <button class="btn btn-go" type="submit">Send &gt;</button>
      </form>
    </div>
  </div>
</section>'''

TCSS = P.PCSS + '''<style>
.notes-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.hashtag { text-transform: none !important; }
.apps-2 { grid-template-columns: repeat(2, minmax(0, 200px)); }
.faq summary h2 { display: inline; margin: 0; font: 600 15px/1.4 var(--body); text-transform: none; letter-spacing: 0; color: var(--text); }
@media (max-width: 900px) { .notes-2 { grid-template-columns: minmax(0, 1fr); } }
</style>'''
TJS = '''<script>
document.querySelectorAll('.pkg-all').forEach(function (b) {
  b.addEventListener('click', function () {   // one click opens every package, like the cycling page
    var o = !b.closest('.pkg').classList.contains('open');
    document.querySelectorAll('.pkg').forEach(function (p) { p.classList.toggle('open', o); });
    document.querySelectorAll('.pkg-all').forEach(function (x) { x.setAttribute('aria-expanded', o); x.querySelector('span').textContent = o ? 'Show fewer features' : 'See all features'; });
  });
});
document.querySelectorAll('[data-waitlist]').forEach(function (b) {
  b.addEventListener('click', function () {
    var m = document.querySelector('#contact textarea');
    if (m && !m.value) m.value = b.dataset.msg || ('Hi Matteo, please add me to the waiting list for the ' + b.dataset.waitlist + ' package.');
  });
});
</script>''' + REVIEWS_JS

build('tri-individual-packages', PATH, MAIN,
      'New Triathlon Individual Packages page. Same packages, prices, copy and FAQ as live; the page now has its approved H1.',
      h1='TRIATHLON INDIVIDUAL PACKAGES', extra_css=TCSS, extra_js=TJS, h2_changes={'drop': ['FOLLOW YOUR PLAN ON']})   # Matteo 15 Nov
