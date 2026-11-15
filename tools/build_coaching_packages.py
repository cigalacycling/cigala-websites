"""Build the Individual (cycling) Packages preview: coachingpages/individual-packages.html

All live copy is kept: package names, prices, every feature line, the payment links (Shopify / GoCardless),
testimonials, Vekta text, FAQ, 2026 numbers, featured athletes gallery, contact form.
Approved SEO change (coaching/SEO-DECISIONS.md): the page gets the H1 "Individual Cycling Coaching Packages".
Layout changes: the payment dropdowns become buttons; Premium (sold out) gets a waiting-list button to the contact form.
Each card has its complete feature list: the lines that make the package different come first, the rest open with "Show all".
"""
import os, sys, re, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import build_coaching_nutrition as NUT   # the athlete calendar (Matteo 15 Nov: show it here, instead of the team photo)
_c = NUT.CSS
CAL_CSS = '<style>' + _c[_c.index('.cal-scroll {'):_c.index('.nu-upg-cta {')] + '''
.pk-cal { margin: 0; display: grid; gap: 10px; }
.pk-cal .cal-row { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.pk-notes { display: grid; grid-auto-flow: column; grid-auto-columns: 100%; gap: 14px; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: thin; align-items: start; }
.pk-notes > .cal-note { scroll-snap-align: start; margin: 0; }
.pk-nav { display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; }
.pk-btn { width: 38px; height: 38px; border-radius: 50%; border: 1px solid var(--border-strong); background: var(--panel-solid); color: var(--text); font-size: 16px; cursor: pointer; }
.pk-btn:hover { border-color: var(--green); color: var(--green-text); }
.pk-note .cal-rm { font-size: 13px; }
.pk-cal figcaption { color: var(--text-2); font-size: 14px; line-height: 1.55; }
.pk-cal figcaption a { color: var(--green-text); font-weight: 600; }
@media (max-width: 1100px) { .pk-cal .cal-row { grid-template-columns: repeat(3, 165px); } }
</style>'''

PATH = '/individual-packages/'
SRC = open(ROOT + 'coaching/html/individual-packages.html').read()
TXT = open(ROOT + 'coaching/text/individual-packages.txt').read().split('\n')
CAL = 'https://calendly.com/cigalacycling'
VEKTA = 'https://joinvekta.com/'

# ---------- package features, straight from the live page ----------
def feats(after):
    i = TXT.index(after); out = []
    for l in TXT[i + 1:]:
        if l.startswith('LI: '): out.append(re.sub(r'\s+', ' ', l[4:]).strip())
        elif l.startswith('LABEL:'): break
    return out
# live included / excluded marks (the text extract loses them)
_LI = re.findall(r'<li class="(included|excluded)[^"]*">(.*?)</li>', SRC, re.S)
_n = next(i for i, (c, t) in enumerate(_LI) if 'on a weekly basis' in t)   # Basic's list ends where Advanced's starts
EXCLUDED = [re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', t))).strip() for c, t in _LI[:_n] if c == 'excluded']
assert EXCLUDED == ['Feedback on sessions', 'Schedule Adjustment', 'Daily Training Analysis', 'Daily Session Carbs Recommendations',
                    'Nutritional Consult with our Sports Nutritionist'], EXCLUDED
F = {'basic': feats('H2: Basic'), 'advanced': feats('H2: Advanced'), 'premium': feats('H2: Premium')}
norm = lambda s: s.lower().replace('metabolic inscyd testing', 'inscyd metabolic testing').replace('carb ', 'carbs ')
common = [f for f in F['advanced'] if all(norm(f) in map(norm, F[k]) for k in F)]
own = {k: [f for f in v if norm(f) not in map(norm, common)] for k, v in F.items()}
# every live feature line must still be on the page
for k, v in F.items():
    for f in v: assert f in common or f in own[k] or norm(f) in map(norm, common), f

# "Good to know" strip with icons, separate from the package cards (Matteo 15 Nov: the notes looked like part of a package)
ICON = {
    'spots': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    'currency': '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    'platform': '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    'person': '<circle cx="12" cy="7" r="4"/><path d="M4 21v-1a7 7 0 0 1 14 0v1"/>',   # the live page used a user icon and a rocket icon here
    'rocket': '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    'student': '<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 2 9 2 12 0v-5"/>',
}
def notes_strip(items):
    cells = ''.join(f'<div class="note"><svg viewBox="0 0 24 24" aria-hidden="true">{ICON[k]}</svg><p>{t}</p></div>' for k, t in items)
    return f'<div class="notes-wrap"><div class="notes-lab">Good to know</div><div class="notes">{cells}</div></div>'

PAY = dict(re.findall(r'<option value="(https://[^"]+)"[^>]*>\s*([^<]+?)\s*<', SRC))
pay = {label: url for url, label in PAY.items()}
def btn(label, url, cls='btn-go', note=''):
    return f'<a class="btn {cls} pay" href="{E(url)}" {EXT}>{label}</a>' + (f'<span class="pay-note">{note}</span>' if note else '')

# New feature line, added by Matteo (15 Nov 2026): Advanced and Premium only, a normal line after the training plan.
# Matteo 15 Nov (2nd review): 'deep initial assessment ... across the year or 6 months, depending on how much training data'
ASSESS = 'Deep Initial Assessment of your training data (last 6–12 months)'   # Matteo 15 Nov: shorter
# Who each package is for: short lines taken from the live FAQ answer "What would the most suitable package for me?"
FOR = {
    'basic': 'For riders who can follow the training without the human aspect of a coach.',
    'advanced': 'Access to Matteo as your coach, with weekly feedback, a monthly catch up call and deep training analysis, plus Vekta.',
    'premium': 'The closest coaching: daily contact, feedback and analysis, and a weekly catch up call.',
}
def card(key, h2, term, price, per, sub, buttons, badge='', cls=''):
    top = list(own[key])
    if key in ('advanced', 'premium'): top.insert(1, ASSESS)
    rest = [f for f in F[key] if f not in own[key]]
    # Matteo, 15 Nov 2026: Basic does NOT include training analysis (the live list said "Daily Training Analysis")
    # Matteo 15 Nov (2nd review): Basic has no feedback, schedule adjustment or training analysis; show with an X
    # everything the coached packages add, so the difference is clear on the card itself.
    # The live page marks each line <li class="included|excluded">: Basic's excluded lines come from there (EXCLUDED),
    # plus what Advanced/Premium add that isn't in Basic's live list at all.
    # Matteo 15 Nov (4th review): Basic's zones don't change weekly either -> 'Adaptive Training Zones changing weekly' is an X too
    no = (EXCLUDED + ['Adaptive Training Zones changing weekly', ASSESS, 'Monthly catch up call', 'Race Strategy', 'Continuous Support & Motivation', 'Vekta membership']) if key == 'basic' else []
    top = [x for x in top if x not in no]
    # Matteo 15 Nov (3rd review): lead with what you GET. Every card shows its first 8 included lines; "Show all" opens
    # the rest and, on Basic only, the lines it does not include, at the very end under their own label.
    inc = [x for x in top + rest if x not in no]; SHOW = 12   # Matteo 15 Nov: two more lines visible before "See all"
    NUT = 'Nutritional Consult with our Sports Nutritionist'   # Matteo 15 Nov: higher up, right after the assessment
    if NUT in inc: inc.remove(NUT); inc.insert(3 if key != 'basic' else 2, NUT)
    AZ = 'Adaptive Training Zones changing weekly'   # now a coached-only line (not in Basic), so show it with the other differences
    if key != 'basic' and AZ in inc: inc.remove(AZ); inc.insert(11, AZ)
    LBL = {'Race Strategy': 'Race & Pacing Strategy',   # Matteo 15 Nov: pacing on the same line
           'Access to World Class Nutritionist & Mental Coach': 'Access to work 1-to-1 with our World Class Nutritionist & Mental Coach'}
    items = ''.join(f'<li{" class=\"more\"" if i >= SHOW else ""}>{E(LBL.get(x, x))}</li>' for i, x in enumerate(inc))
    if no:
        items += '<li class="more no-lab">Included in Advanced &amp; Premium</li>'
        NO_LABEL = {'Daily Training Analysis': 'Training Analysis', 'Race Strategy': 'Race & Pacing Strategy'}   # Matteo 15 Nov: Basic has no training analysis at all, not just no daily one
        items += ''.join(f'<li class="more no">{E(NO_LABEL.get(x, x))}<span class="vh"> (not included in Basic)</span></li>' for x in no)
    total = len(inc)
    return f'''<article class="pkg {cls}" id="pkg-{key}">
        {badge}
        <div class="pkg-term">{term}</div>
        <h2>{h2}</h2>
        <p class="pkg-for">{FOR[key]}</p>
        <div class="pkg-price"><b>{price}</b><span>{per}</span></div>
        <p class="pkg-sub">{sub}</p>
        <div class="pkg-buy">{buttons}<a class="pkg-call" href="{CAL}" {EXT}>Not sure? Book a free consultation →</a></div>
        <div class="pkg-lab">What you get</div>
        <ul class="ticks">{items}</ul>
        <button type="button" class="pkg-all" aria-expanded="false"><span>See all features</span><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 8l5 5 5-5"/></svg></button>
        <div class="pkg-buy2">{re.search(r'<a [^>]*>.*?</a>', buttons).group(0).replace(' pay"', ' pay pay2"')}</div>
      </article>'''   # Matteo 15 Nov: the button stays by the price, and again at the end of the list

# ---------- compare table: only the differences, wording from the live feature lines ----------
Y, N = '<span class="y" aria-label="Included">✓</span>', '<span class="n" aria-label="Not included">✗</span>'
ROWS = [
    ('Coaching package', 'Daily plan built for 12 weeks', 'Daily plan built on a weekly basis', 'Daily plan built on a weekly basis'),
    ('Deep Initial Assessment of your training data', N, Y, Y),
    ('Contact', 'When needed via email', 'Weekly', 'Daily'),
    ('Feedback', N, 'Weekly', 'Daily'),
    ('Schedule adjustment', N, 'Weekly', 'Daily'),
    ('Training analysis', N, 'Weekly', 'Daily'),
    ('Daily session carbs recommendations', N, Y, Y),
    ('Nutritional consult with our Sports Nutritionist', N, Y, Y),
    ('Catch up call', N, 'Monthly or when needed', 'Weekly or when needed'),
    ('Race &amp; pacing strategy', N, Y, Y),
    ('Adaptive training zones changing weekly', N, Y, Y),
    ('Continuous support &amp; motivation', N, Y, Y),
    ('Platform', 'Training Peaks Basic account', 'Vekta membership included (value €19.99/m)', 'Vekta membership included (value €19.99/m)'),
    ('Price', '€228 one-time for 12 weeks', '€149/mo, 6 months', '€249/mo for 3 months, €239/mo for 6'),
]
compare = ('<div class="cmp-wrap"><h3 class="h-sm">Compare coaching packages</h3><div class="bar"></div><div class="cmp-scroll"><table class="cmp">'
           '<thead><tr><th scope="col"><span class="vh">Feature</span></th><th scope="col">Basic</th><th scope="col" class="hot">Advanced</th><th scope="col">Premium</th></tr></thead><tbody>'
           + ''.join(f'<tr><th scope="row">{r[0]}</th><td data-l="Basic">{r[1]}</td><td class="hot" data-l="Advanced">{r[2]}</td><td data-l="Premium">{r[3]}</td></tr>' for r in ROWS)
           + '</tbody></table></div><p class="cmp-note">Every package also includes the plan tailored to your availability, testing, nutrition support, the gym &amp; winter program, our community and more: open “Show all” on each card for the full list.</p></div>')

cards = ''.join([
    card('basic', 'Basic', '12 Weeks', '€19', '/week', 'Charged with one-time payment of €228 for the 12 weeks.',
         btn('Buy Basic 12 Weeks · €228', pay['Basic 12 Weeks: 228 EUR - one-time payment'])),
    card('advanced', 'Advanced', '6 months subscription', '€149', '/mo', '',
         btn('Subscribe to Advanced · €149/mo', pay['Advanced 6 months: 149 EUR - monthly']),
         '<span class="pkg-badge">Monthly (Our Most Popular)</span>', 'hot'),
    card('premium', 'Premium', '3 months subscription (€10 off for 6 mo)', '€249', '/mo', '',
         # Premium is sold out: Matteo chose a waiting list instead of the GoCardless links (15 Nov 2026)
         '<a class="btn btn-go pay" href="#contact" data-waitlist="Premium">Join the waiting list</a>'
         '<span class="pay-note">Premium 3 months €249/mo · 6 months €239/mo</span>',
         '', 'sold'),   # Matteo 15 Nov: no "Monthly (SOLD OUT!)" badge, the SOLD OUT stamp is enough
])

# ---------- testimonials (live quotes; photos had no alt text, see SEO-DECISIONS.md) ----------
QUOTES = re.findall(r'TXT: "(.*?)"\n<img https://[^ ]*/(unnamed-\d+)\.png', '\n'.join(TXT), re.S)
quotes = ''.join(
    f'<figure class="q"><img src="{img(n + ".png", "athlete-" + n)}" alt="Photo of a coached athlete, shown with their testimonial | Cigala Cycling Coaching" loading="lazy" width="200" height="200">'
    f'<div class="rv-stars" role="img" aria-label="5 stars">★★★★★</div><blockquote>“{E(re.sub(r"\s*\n\s*", " ", q))}”</blockquote></figure>' for q, n in QUOTES)
assert len(QUOTES) == 5

# ---------- Vekta + devices ----------
def section_lines(start, stop):
    i = TXT.index(start); out = []
    for l in TXT[i + 1:]:
        if l.startswith(stop): break
        out.append(l)
    return out
vk = [l[3:] for l in section_lines('H2: USING VEKTA - NEXT GENERATION TRAINING & COACHING PLATFORM', 'TXT:') if l.startswith('P: ')]
def md(s):  # **bold** and [text](url) from the extractor
    s = E(s).replace('&amp;', '&')
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    return re.sub(r'\[(.+?)\]\((.+?)\)', lambda m: f'<a href="{m.group(2)}" {EXT}>{m.group(1).strip()}</a>', s)
vk_intro = ''.join(f'<p>{md(x)}</p>' for x in vk[:3])
# Matteo 15 Nov: an icon for each Vekta feature instead of the tick
VK_IC = ['<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',                       # adaptive zones: sliders
         '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>',  # AI modelling: chip
         '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',                                                                     # beyond FTP: power trace
         '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',          # personalised: target
         '<circle cx="12" cy="8" r="6"/><path d="M15.48 12.89 17 22l-5-3-5 3 1.52-9.11"/>']                          # elite tools: award
vk_points = ''.join(f'<li><svg viewBox="0 0 24 24" aria-hidden="true">{ic}</svg><p>{md(x)}</p></li>' for ic, x in zip(VK_IC, vk[3:8]))
vk_end = f'<p>{md(vk[8])}</p>'
DEV = re.findall(r'<img https://[^ ]*/uploads/(\S+) alt=\'([^\']*)\'>', '\n'.join(section_lines('H2: FOLLOW YOUR STRUCTURED TRAINING SESSIONS ON YOUR FAVOURITE DEVICES & APPS (BELOW SOME APPS - THE LIST IS MUCH LONGER)', 'H2:')))
devices = ''.join(f'<a href="https://joinvekta.com/partnerships" {EXT}><img src="{img(u, "app-" + re.sub(r"[^a-z0-9]+", "-", a.split("|")[0].lower()).strip("-")[:24])}" alt="{E(a)}" loading="lazy"></a>' for u, a in DEV)

# ---------- FAQ ----------
faq_lines = section_lines('H2: FREQUENTLY ASKED QUESTIONS', 'H2:')
faq, cur = [], None
for l in faq_lines:
    if l.startswith('H3: '): cur = [l[4:], []]; faq.append(cur)
    elif cur and l.startswith('P: '): cur[1].append(l[3:])
    elif cur and l and not l.startswith(('TXT', '<')): cur[1][-1] += '\n' + l
# Matteo 15 Nov: a question on working 1-to-1 with the nutritionist
faq.append(('Can I work 1-to-1 with a sports nutritionist?', ['Yes. Every package includes access to our sports nutritionist, Marine Lenehan (MSc, WorldTour professional cyclist), and Advanced and Premium include a nutritional consult and daily carb recommendations for your sessions.',
            'You can also add nutrition coaching with Marine: your daily macros and carbs per hour in the same calendar as your training, food diary reviews, and a fuelling plan for your races. [Read more about nutrition coaching](' + C + '/nutrition/#upgrade)']))
faq_html = ''.join(f'<details{" open" if i == 0 else ""}><summary><h3>{E(q)}</h3></summary>' + ''.join(f'<p>{md(p).replace(chr(10), "<br>")}</p>' for p in ps) + '</details>' for i, (q, ps) in enumerate(faq))

# ---------- numbers ----------
nums = re.findall(r'H3: (.+)\nH4: (.+)', '\n'.join(section_lines('H2: 2026 IN NUMBERS', 'H2:')))
nums_html = ''.join(f'<div class="stat"><h3 class="n" data-count="{E(n)}">{E(n)}</h3><h4 class="l">{E(l)}</h4></div>' for n, l in nums)

# ---------- featured athletes gallery (live order) ----------
WEBPS = {o['url']: o['webp'] for o in json.load(open(ROOT + 'coaching/images.json')) if o.get('webp')}
gal = []
for u in re.findall(r'class="e-gallery-item[^"]*" href="([^"]+)"', SRC):
    w = WEBPS.get(re.sub(r'-\d+x\d+(?=\.\w+$)', '', u))
    if w and w not in gal: gal.append(w)
gallery = ''.join(f'<a href="../coaching/webp/{w}" {EXT} class="g{" more" if i >= 24 else ""}"><img src="../coaching/webp/{w}" alt="Athlete coached by Cigala Cycling" loading="lazy"></a>' for i, w in enumerate(gal))

# ---------- logos (as seen in) ----------
LOGOS = [('imgi_4_wHe4MESD', 'logo-red-bull'), ('imgi_6_6_MxiOhd', 'logo-stickybottle'), ('unnamed-87.png', 'logo-zwift'),
         ('unnamed-86.png', 'logo-trainingpeaks'), ('unnamed-84.png', 'logo-cycling-ireland'), ('unnamed-85.png', 'logo-vekta')]
logos = ''.join(f'<span><img src="{img(k, n)}" alt="{E(live_alt(k))}" loading="lazy"></span>' for k, n in LOGOS)

HERO = img('IMG_3999AWDWWWU', 'packages-hero-lake')   # Matteo 15 Nov: option A, riders by the lake in Wicklow (2560 px, sharp)
TEAM = img('imgi_21_ZtFBdo0p', 'team-training')  # clean version of the live banner photo (imgi_43, Matteo didn't want the text banner)
RIDER = img('imgi_42_FoPYDRwS', 'rider')
COACHPIC = img('imgi_16_g675BzCnYW', 'matteo-coaching')   # Matteo 15 Nov: new photo for Get in touch
img('SDFASDFASDF.png', 'cigala-x-vekta'); img('PfNJBaCPkS_eSn5J', 'trainingpeaks-levels')
# dark-background versions (tools/darklogo.py): white background removed, black text turned white
# Matteo 15 Nov (2nd review): the dark Cigala x Vekta logo looked bad -> lockup of the new Coaching logo, x, and the Vekta
# logo remade with smooth edges (tools/unmix_logo.py); the TrainingPeaks badges are cropped tight so they sit centred.
shutil.copy(ROOT + 'coaching/webp/vekta-white-v2.webp', OUT + 'img/vekta-white-v2.webp')
shutil.copy(ROOT + 'coaching/webp/darklogo-trainingpeaks-levels-crop.webp', OUT + 'img/trainingpeaks-levels-dark-v2.webp')
VKLOGO, TPLOGO = 'img/vekta-white-v2.webp', 'img/trainingpeaks-levels-dark-v2.webp'

intro = [l[3:] for l in TXT[TXT.index('TXT: [', 0):TXT.index('TXT: 12 Weeks')] if l.startswith('P: ')]
MAIN = f'''<div class="hero hero-sm hero-lake">
  <img src="{HERO}" alt="Cigala Cycling Coaching group riding in Wicklow, Ireland" width="2560" height="1707">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Cycling coaching</div>
    <h1>Individual Cycling Coaching Packages</h1>
    <p class="lede">I have 3 coaching packages: Basic, Advanced and Premium<br>For all you can add 1 or 2 One-on-One sessions a month with myself, Matteo Cigala</p>
    <div class="ctas">
      <a class="btn btn-go" href="{CAL}" {EXT}>Book free consultation</a>
      <a class="btn btn-ghost" href="#packages">Compare coaching packages ↓</a>
    </div>
  </div>
</div>

<section id="packages">
  <div class="in">
    {notes_strip([('spots', 'I coach a limited number of athletes, so every one of them gets my full attention: a one-to-one, personal coaching experience, never a template.'),   # Matteo 15 Nov: no "get in touch before"; a unique experience
                 ('currency', E(intro[1])), ('platform', 'For Advanced &amp; Premium Packages Vekta membership is included (worth €19.99/ month)<br>On demand Training Peaks Premium is also an option.')])}
    <div class="pkgs">
      {cards}
    </div>
    {compare}
    <p class="terms"><b>By subscribing to any of our packages, you accept our Terms &amp; Conditions. View T&amp;C <a href="{C}/terms-conditions/" {EXT}>HERE</a></b></p>


    <div class="addons">
      <div class="panel addon">
        <svg class="addon-ic" viewBox="0 0 24 24" aria-hidden="true">{ICON['person']}</svg>
        <h3 class="h-sm">Purchase multiple One-on-One Sessions</h3>
        <p>Purchase multiple One-on-One Sessions with Head Coach Matteo Cigala.</p>
        <p>Sessions are held in Wicklow Town, Co.Wicklow, Ireland and can be booked after purchase.</p>
        <a class="arrow-link" href="{C}/book-1-on-1-session/" {EXT}>Book a 1-to-1 session →</a>
      </div>
      <div class="panel addon">
        <svg class="addon-ic" viewBox="0 0 24 24" aria-hidden="true">{ICON['rocket']}</svg>
        <h3 class="h-sm">Talent programme</h3>
        <p>Underage, Juniors &amp; U23 will avail of a 20% student discount for all packages.</p>
        <p class="addon-aj"><img src="{conv('coaching/matteo-uploads/aj-allsports-logo.png', 'packages-aj-allsports-logo', 600)}" alt="A&amp;J All Sports Agency logo" loading="lazy" width="120" height="48"><span>Coached by a talent scout for <b>A&amp;J AllSports</b>, the agency of Tadej Pogačar and other WorldTour stars.</span></p>
        <p>See our talent programme for more information <a href="{C}/talent-scout/" {EXT}><b>HERE</b></a></p>
        <a class="arrow-link" href="{C}/talent-scout/" {EXT}>Talent programme →</a>
      </div>
    </div>
  </div>
</section>

{tools_band()}

<section>
  <div class="in">
    <div class="head">
      <div><div class="eyebrow">Our athletes</div><h2>READ OUR TESTIMONIALS</h2></div>
      <div class="rv-links"><a class="arrow-link" href="{GOOGLE_REVIEWS}" {EXT}><span class="gstar" aria-hidden="true">★</span> Read our reviews on Google →</a><a class="arrow-link" href="{C}/testimonials/" {EXT}>Read more testimonials →</a></div>
    </div>
    <div class="quotes">{quotes}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head">
      <div><div class="eyebrow">Real results</div><h3 class="h-sec">CASE STUDIES</h3><div class="bar"></div></div>
      <div class="rv-links"><a class="arrow-link" href="{C}/case-studies/" {EXT}>All case studies →</a></div>
    </div>
    {case_cards(C + '/case-studies/')}
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Results</div><h2>2026 IN NUMBERS</h2><div class="bar"></div></div></div>
    <div class="stats nums">{nums_html}</div>
  </div>
</section>

<section>
  <div class="in split">
    <div>
      <div class="eyebrow">Training platform</div>
      <h2>USING VEKTA - NEXT GENERATION TRAINING &amp; COACHING PLATFORM</h2>
      <div class="bar"></div>
      <div class="vk">{vk_intro}<ul class="vk-feats">{vk_points}</ul>{vk_end}</div>
      <div class="ctas"><a class="btn btn-go" href="{VEKTA}" {EXT}>Find more about Vekta →</a></div>
    </div>
    <div class="vk-side">
      <figure class="nu-cal pk-cal">
        <div class="cal-scroll" tabindex="0" aria-label="Example days from an athlete's calendar, with nutrition"><div class="cal-row">{NUT.cal_days(('21', '24', '26'))}</div></div>
        <div class="pk-notes-wrap"><div class="pk-notes" id="pk-notes" tabindex="0" aria-label="Sample notes from Marine, scroll sideways">{NUT.notes}</div>
          <div class="pk-nav"><button type="button" class="pk-btn" data-d="-1" data-t="pk-notes" aria-label="Previous note">←</button><button type="button" class="pk-btn" data-d="1" data-t="pk-notes" aria-label="Next note">→</button></div></div>
        <figcaption>Working 1-to-1 with our sports nutritionist, Marine Lenehan? Her nutrition notes, daily macros and carbs per hour sit in the same calendar as your sessions. <a href="{C}/nutrition/#upgrade" {EXT}>Read more about nutrition coaching →</a></figcaption>
      </figure>
      <div class="vk-logos">
        <a class="vk-lock" href="https://joinvekta.com/partnerships" {EXT} aria-label="{E(live_alt('SDFASDFASDF'))}"><img src="{LOGO}" alt="" loading="lazy" width="64" height="64"><svg class="vk-x" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 4l12 12M16 4L4 16"/></svg><img src="{VKLOGO}" alt="{E(live_alt('SDFASDFASDF'))}" loading="lazy" width="531" height="139"></a>
        <span><img src="{TPLOGO}" alt="{E(live_alt('PfNJBaCPkS_eSn5J'))}" loading="lazy"></span>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Works with</div><h2>SYNC WITH YOUR FAVOURITE DEVICES &amp; APPS</h2><div class="bar"></div></div></div>
    <div class="logos apps">{devices}</div>
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
    <div class="head">
      <div><div class="eyebrow">Our riders</div><h2>SOME FEATURED ATHLETES</h2><div class="bar"></div></div>
      <button type="button" class="btn btn-ghost" id="g-more">Show all {len(gal)} photos</button>
    </div>
    <div class="gallery" id="gallery">{gallery}</div>
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
    <div class="photo rider"><img src="{COACHPIC}" alt="{E(live_alt('imgi_16_g675BzCnYW'))}" loading="lazy" width="1440" height="1081"></div>
    <div>
      <div class="eyebrow">Check availability</div>
      <h3 class="h-sec">READY TO TAKE YOUR CYCLING TO THE NEXT LEVEL?</h3>
      <div class="bar"></div>
      <p class="lede">{E(intro[2])}</p>
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

PCSS = '''<style>
.hero-sm { min-height: min(560px, 74svh); }
.hero-sm .in { padding-block: 110px 48px; }
.hero-sm h1 { max-width: 16ch; font-size: clamp(38px, 6vw, 72px); }
.hero-lake > img { object-position: 72% 78%; }   /* riders in the clear right-hand side, lake behind the heading */
@media (max-width: 640px) { .hero-lake > img { object-position: 64% 70%; } }
#packages { padding-top: 28px; }
.notes-wrap { margin: 0 0 40px; padding: 20px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
.notes-lab { font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--text-3); margin-bottom: 14px; }
.notes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px 32px; }
.note { display: flex; gap: 12px; align-items: flex-start; }
.note svg { flex: none; width: 22px; height: 22px; fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; margin-top: 1px; }
.note p { margin: 0; font-size: 14px; color: var(--text-2); line-height: 1.55; }
.pkgs { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0 16px; align-items: start; }
.pkg { display: grid; grid-row: span 10; grid-template-rows: subgrid; row-gap: 0; align-content: start; }   /* term, name, for, price, sub, buy, label, list, button line up across the cards */
.pkg { position: relative; background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 28px 24px 24px; min-width: 0; }
.pkg.hot { border-color: var(--green); box-shadow: 0 0 0 1px var(--green), 0 24px 60px rgba(0,154,68,.18); }
.pkg-badge { position: absolute; top: -13px; left: 24px; font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #fff; background: var(--green); border-radius: 999px; padding: 5px 12px; }
.pkg-badge.sold { background: var(--panel-solid); border: 1px solid var(--red); color: var(--red-text, #ff3d33); }
.pkg-term { font-size: 12px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--red-text, #ff3d33); }
.pkg h2 { font-size: 40px; margin-top: 10px; }
.pkg-price { display: flex; align-items: baseline; gap: 4px; margin-top: 14px; }
.pkg-price b { font: 400 54px/1 var(--head); color: var(--text); }
.pkg-price span { color: var(--text-3); font-weight: 600; }
.pkg-sub { font-size: 13px; color: var(--text-3); margin: 8px 0 18px; }
.pkg-buy { display: grid; gap: 8px; }
.pay { width: 100%; text-align: center; }
.pay-note { display: block; font-size: 12.5px; color: var(--text-3); text-align: center; }
.pkg-lab { margin-top: 22px; padding-top: 18px; border-top: 1px solid var(--border); font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--green-text); }   /* Matteo 15 Nov: stands out from the grey notes */
.ticks { list-style: none; margin: 12px 0 0; padding: 0; display: grid; gap: 8px; align-content: start; }
.ticks li { position: relative; padding-left: 26px; font-size: 14px; color: var(--text-2); line-height: 1.45; }
.ticks li::before { content: ""; position: absolute; left: 0; top: 3px; width: 16px; height: 16px; border-radius: 50%; background: var(--green-wash) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M4.5 8.2l2.2 2.2 4.8-4.8' fill='none' stroke='%2334c46a' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / 16px no-repeat; }
.pkg:not(.open) .ticks li.more { display: none; }
.pkg-for { margin: 8px 0 0; font-size: 13.5px; color: var(--text-2); line-height: 1.5; }
.pkg-call { font-size: 13px; font-weight: 600; color: var(--green-text); text-decoration: none; text-align: center; padding: 4px 0; }
.pkg-call:hover { color: #fff; }
.ticks li.no { color: var(--text-4, #62666d); }
.ticks li.no span { font-size: 12.5px; }
.ticks li.no::before { background: rgba(225,6,0,.12) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M5.2 5.2l5.6 5.6M10.8 5.2l-5.6 5.6' fill='none' stroke='%23ff3d33' stroke-width='1.8' stroke-linecap='round'/%3E%3C/svg%3E") center / 16px no-repeat; }
.cmp-wrap { margin-top: 44px; }
.cmp-scroll { margin-top: 20px; overflow-x: auto; border: 1px solid var(--border); border-radius: var(--r); background: var(--panel-grad), var(--panel); }
.cmp { width: 100%; min-width: 640px; border-collapse: collapse; font-size: 14px; }
.cmp th, .cmp td { padding: 13px 16px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }
.cmp tbody tr:last-child th, .cmp tbody tr:last-child td { border-bottom: 0; }
.cmp thead th { font: 400 20px/1.1 var(--head); text-transform: uppercase; color: var(--text); }
.cmp tbody th { font-weight: 600; color: var(--text); width: 28%; }
.cmp td { color: var(--text-2); }
.cmp .hot { background: rgba(0,154,68,.07); }
.cmp thead .hot { color: var(--green-text); }
.cmp .y { color: var(--green-text); font-weight: 700; font-size: 16px; }
.cmp .n { color: var(--red-text, #ff3d33); font-weight: 700; font-size: 16px; }
.cmp-note { margin: 12px 0 0; font-size: 13px; color: var(--text-3); }
.vh { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
.cmp tbody th { position: sticky; left: 0; background: var(--panel-solid); }
.pkg-all { margin-top: 16px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; font: 600 14px var(--body); color: var(--text); background: rgba(255,255,255,.04); border: 1px solid var(--border-strong); border-radius: 10px; padding: 11px 14px; cursor: pointer; }
.pkg-all svg { width: 18px; height: 18px; fill: none; stroke: var(--green-text); stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; transition: transform .2s; }
.pkg-all:hover { border-color: var(--green); }
.pkg.open .pkg-all svg { transform: rotate(180deg); }
.terms { margin: 22px 0 0; font-size: 13px; color: var(--text-3); text-align: center; }
.terms b { color: var(--text-2); font-weight: 600; }
.panel { background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: var(--r); }
.h-sm { font-size: clamp(24px, 2.6vw, 30px); }
.ticks.cols { columns: 2; column-gap: 32px; display: block; margin: 0; }
.ticks.cols li { break-inside: avoid; margin-bottom: 9px; }
.addons { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-top: 16px; }
.addon { padding: 24px; }
.addon p { margin: 10px 0 0; font-size: 14.5px; }
.addon p a { color: var(--green-text); }
.addon .arrow-link { display: inline-block; margin-top: 14px; }
.quotes { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; }
.q { margin: 0; background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: var(--r); padding: 20px; display: flex; flex-direction: column; gap: 14px; min-width: 0; }
.q img { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 2px solid var(--green); }
.q blockquote { margin: 0; font-size: 14px; color: var(--text-2); line-height: 1.55; }
.nums { grid-template-columns: repeat(6, minmax(0, 1fr)); }
.nums .n { margin: 0; font-family: var(--head); font-weight: 400; font-size: clamp(32px, 3.6vw, 46px); line-height: 1; color: var(--text); }
.nums .l { margin: 8px 0 0; }
.nums .stat:nth-child(-n+4) .n { color: var(--text); }
/* Matteo 15 Nov: "What you get" in red (green got lost), a second button at the end of each card, Premium clearly sold out */
.pkg .pkg-lab { color: #ff3d33; }
/* Matteo 15 Nov (later): ticks back to green, the X stays red */
.pkg-buy2 { margin-top: 12px; }
.addon-aj { display: flex; align-items: center; gap: 14px; padding: 12px; border-radius: 12px; background: rgba(255,255,255,.04); border: 1px solid var(--border); }
.addon-aj img { flex: none; width: 110px; height: auto; background: #fff; border-radius: 8px; padding: 8px; }
.addon-aj span { font-size: 14px; color: var(--text-2); }
.addon-aj b { color: var(--text); }
.pkg-buy2 .pay2 { min-height: 0; padding-top: 12px; padding-bottom: 12px; font-size: 14px; }
.pkg.sold { border-color: rgba(255,61,51,.55); background: repeating-linear-gradient(135deg, rgba(255,61,51,.035) 0 14px, transparent 14px 28px), var(--panel-grad), var(--panel); }
.pkg.sold .pkg-badge.sold { background: #e10600; border-color: #e10600; color: #fff; }
.pkg.sold::after { content: "SOLD OUT"; position: absolute; top: 74px; right: 18px; transform: rotate(-9deg); padding: 6px 14px; border: 3px solid #ff3d33; border-radius: 8px; font: 400 26px/1 var(--head); letter-spacing: .06em; color: #ff3d33; opacity: .92; pointer-events: none; }
.pkg.sold .pkg-price b { color: var(--text-2); }
.pkg.sold .pay { background: transparent !important; border: 2px solid #ff3d33 !important; color: #fff !important; box-shadow: none !important; }
.pkg.sold .pay:hover { background: rgba(255,61,51,.14) !important; }
@media (max-width: 600px) { .pkg.sold::after { top: 64px; font-size: 22px; } }
/* Matteo 15 Nov: 2026 in numbers with colour: medal colours for the places, a bar that fills as they count, a hover lift */
.nums .stat { --c: #34c46a; position: relative; transition: background .25s, transform .25s; }
.nums .stat:nth-child(1) { --c: #34c46a; } .nums .stat:nth-child(2) { --c: #d08a4b; } .nums .stat:nth-child(3) { --c: #c9d1db; }
.nums .stat:nth-child(4) { --c: #f0bf00; } .nums .stat:nth-child(5) { --c: #34c46a; } .nums .stat:nth-child(6) { --c: #ff3d33; }
.nums .stat .n { color: var(--c) !important; }
.nums .stat::after { content: ""; position: absolute; left: 18px; right: 18px; bottom: 12px; height: 3px; border-radius: 3px; background: var(--c); transform: scaleX(0); transform-origin: left; transition: transform 1.6s cubic-bezier(.2,.7,.2,1); }
.nums.on .stat::after { transform: scaleX(1); }
.nums .stat:hover { background: color-mix(in srgb, var(--c) 12%, transparent); transform: translateY(-3px); }
.nums .stat:hover .l { color: var(--text); }

.vk p { margin: 14px 0 0; max-width: 62ch; }
.vk p a { color: var(--green-text); }
.vk-feats { list-style: none; margin: 18px 0 4px; padding: 0; display: grid; gap: 12px; }
.vk-feats li { display: flex; gap: 14px; align-items: flex-start; }
.vk-feats svg { flex: none; width: 40px; height: 40px; padding: 9px; border-radius: 10px; background: var(--green-wash); fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.vk-feats p { margin: 0 !important; font-size: 15px; line-height: 1.55; }
.vk-feats b { color: var(--text); }
.ticks li.no-lab { padding: 10px 0 0; margin-top: 4px; border-top: 1px solid var(--border); font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--text-3); }
.ticks li.no-lab::before { display: none; }
.vk-side { display: grid; gap: 14px; }
.vk-side .photo { aspect-ratio: 3 / 2; }
.vk-side .photo img { filter: brightness(.85); }   /* Matteo 15 Nov: 15% darker */
.vk-logos { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.vk-logos > * { display: grid; place-items: center; background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: var(--r); padding: 18px; min-height: 130px; }
.vk-logos img { max-height: 92px; width: auto; max-width: 100%; }
.h-long { font-size: clamp(24px, 3vw, 36px); max-width: 32ch; }
.apps { display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 10px; margin: 0; }
.apps a { background: #fff; border-radius: 10px; height: 84px; display: grid; place-items: center; padding: 10px; }
.apps img { max-height: 54px; max-width: 100%; object-fit: contain; }
.faq h3 { display: inline; font: 600 15px/1.4 var(--body); text-transform: none; letter-spacing: 0; color: var(--text); }
.faq details p a { color: var(--green-text); }
.gallery { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; }
.gallery .g { aspect-ratio: 1; border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }
.gallery .g img { width: 100%; height: 100%; object-fit: cover; transition: transform .4s ease; }
.gallery .g:hover img { transform: scale(1.05); }
.gallery:not(.all) .g.more { display: none; }
.rider { aspect-ratio: 1; }
.form { display: grid; gap: 14px; padding: 22px; margin-top: 22px; }
.form label { display: grid; gap: 6px; font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); }
.form input, .form textarea { font: 400 16px/1.4 var(--body); color: var(--text); background: rgba(255,255,255,.04); border: 1px solid var(--border-strong); border-radius: 8px; padding: 12px 14px; width: 100%; }
.form input:focus, .form textarea:focus { outline: 2px solid var(--green); outline-offset: 1px; border-color: transparent; }
.form .btn { justify-self: start; }
@media (max-width: 1080px) { .quotes { grid-template-columns: repeat(3, minmax(0, 1fr)); } .apps { grid-template-columns: repeat(4, minmax(0, 1fr)); } .nums { grid-template-columns: repeat(3, minmax(0, 1fr)); } .nums .stat:nth-child(4) { border-left: 0; } .nums .stat:nth-child(n+4) { border-top: 1px solid var(--border); } }
@media (max-width: 900px) {
  .pkgs, .notes { grid-template-columns: minmax(0, 1fr); }
  .pkgs { gap: 26px; }
  .gallery { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .rider { aspect-ratio: 16 / 10; }
}
@media (max-width: 640px) {
  .addons, .quotes { grid-template-columns: minmax(0, 1fr); }
  .ticks.cols { columns: 1; }
  .apps { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .nums { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .nums .stat:nth-child(odd) { border-left: 0; } .nums .stat:nth-child(even) { border-left: 1px solid var(--border); } .nums .stat:nth-child(n+3) { border-top: 1px solid var(--border); }
  .gallery { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .gallery:not(.all) .g:nth-child(n+13) { display: none; }
  .pkg h2 { font-size: 34px; }
  .cmp-scroll { overflow: visible; }
  .cmp, .cmp tbody, .cmp tr, .cmp th, .cmp td { display: block; min-width: 0; }
  .cmp thead { display: none; }
  .cmp tr { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border-bottom: 1px solid var(--border); }
  .cmp tbody tr:last-child { border-bottom: 0; }
  .cmp tbody th { grid-column: 1 / -1; position: static; width: auto; background: none; border: 0; padding: 14px 14px 4px; }
  .cmp td { border: 0; padding: 4px 10px 14px 14px; font-size: 13px; }
  .cmp td::before { content: attr(data-l); display: block; font-size: 10.5px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--text-3); margin-bottom: 3px; }
  .cmp td.hot::before { color: var(--green-text); }
}
.addon { position: relative; }
.addon-ic { width: 40px; height: 40px; padding: 9px; border-radius: 10px; background: var(--green-wash); fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; display: block; margin-bottom: 14px; }
.q .rv-stars { color: #f5b301; letter-spacing: 2px; font-size: 15px; line-height: 1; }
.vk-lock { display: flex !important; align-items: center; justify-content: center; gap: 16px; }
.vk-lock img:first-child { width: 72px; height: 72px; border-radius: 0; }
.vk-lock .vk-x { width: 18px; height: 18px; flex: none; fill: none; stroke: var(--text-2); stroke-width: 2.4; stroke-linecap: round; }
.vk-lock img:last-child { width: auto; height: 34px; max-width: 46%; }
.vk-logos img { margin: 0 auto; }
@media (max-width: 640px) {
  .vk-logos { grid-template-columns: minmax(0, 1fr); }
  .vk-logos > * { min-height: 110px; }
  .vk-lock { gap: 12px; padding: 16px 12px !important; }
  .vk-lock img:first-child { width: 60px; height: 60px; }
  .vk-lock img:last-child { height: 30px; max-width: none; }
  .vk-logos > span img { max-height: 84px; }
}
</style>'''
PJS = '''<script>
document.getElementById('g-more').addEventListener('click', function () {
  var g = document.getElementById('gallery'), all = g.classList.toggle('all');
  this.textContent = all ? 'Show fewer photos' : this.dataset.label;
});
document.querySelectorAll('[data-waitlist]').forEach(function (b) {
  b.addEventListener('click', function () {
    var m = document.querySelector('#contact textarea');
    if (m && !m.value) m.value = 'Hi Matteo, please add me to the waiting list for the ' + b.dataset.waitlist + ' package.';
  });
});
document.querySelectorAll('.pkg-all').forEach(function (b) {   // one click opens every package (Matteo 15 Nov)
  b.addEventListener('click', function () {
    var o = !b.closest('.pkg').classList.contains('open');
    document.querySelectorAll('.pkg').forEach(function (p) { p.classList.toggle('open', o); });
    document.querySelectorAll('.pkg-all').forEach(function (x) { x.setAttribute('aria-expanded', o); x.querySelector('span').textContent = o ? 'Show fewer features' : 'See all features'; });
  });
});
(function () {   // 2026 in numbers count up when they scroll into view (Matteo 15 Nov); the HTML keeps the real numbers
  document.querySelectorAll('.nums').forEach(function (g) {
    if (!('IntersectionObserver' in window)) { g.classList.add('on'); return; }
    new IntersectionObserver(function (es, ob) { if (es[0].isIntersecting) { g.classList.add('on'); ob.disconnect(); } }, { threshold: 0.4 }).observe(g);
  });
  document.querySelectorAll('.pk-btn').forEach(function (b) { b.addEventListener('click', function () { var r = document.getElementById(b.dataset.t); r.scrollBy({ left: (+b.dataset.d) * r.clientWidth, behavior: 'smooth' }); }); });
  var els = document.querySelectorAll('[data-count]');
  if (!els.length || !('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  els.forEach(function (el) {
    var m = el.dataset.count.match(/^(\\D*)(\\d+)(\\D*)$/); if (!m) return;
    var to = +m[2], dur = 1600;
    el.style.minWidth = el.offsetWidth + 'px'; el.textContent = m[1] + '0' + m[3];
    new IntersectionObserver(function (es, ob) {
      if (!es[0].isIntersecting) return; ob.disconnect();
      var t0 = performance.now();
      (function step(t) { var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
        el.textContent = m[1] + Math.round(to * e) + m[3]; if (k < 1) requestAnimationFrame(step); })(t0);
    }, { threshold: 0.4 }).observe(el);
  });
})();
document.getElementById('g-more').dataset.label = document.getElementById('g-more').textContent;
</script>'''

build('individual-packages', PATH, MAIN,
      'New Individual Packages page. Same packages, prices, payment links and copy as live; the page now has its approved H1.',
      h1='Individual Cycling Coaching Packages', extra_css=PCSS + FT_CSS + CS_CSS + CAL_CSS, extra_js=PJS,
      # Matteo 15 Nov: the devices heading was too long
      h2_changes={'drop': ['FOLLOW YOUR STRUCTURED TRAINING SESSIONS ON YOUR FAVOURITE DEVICES & APPS (BELOW SOME APPS - THE LIST IS MUCH LONGER)', 'READ OUR TESTIMONIALS - WHAT PEOPLE SAY ABOUT CIGALA CYCLING'],
                  'add': ['SYNC WITH YOUR FAVOURITE DEVICES & APPS', 'READ OUR TESTIMONIALS']})   # Matteo 15 Nov: just "Read our testimonials"
print('features:', {k: len(v) for k, v in F.items()}, 'shared:', len(common), 'gallery:', len(gal), 'faq:', len(faq), 'apps:', len(DEV))
