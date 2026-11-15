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
F = {'basic': feats('H2: Basic'), 'advanced': feats('H2: Advanced'), 'premium': feats('H2: Premium')}
norm = lambda s: s.lower().replace('metabolic inscyd testing', 'inscyd metabolic testing').replace('carb ', 'carbs ')
common = [f for f in F['advanced'] if all(norm(f) in map(norm, F[k]) for k in F)]
own = {k: [f for f in v if norm(f) not in map(norm, common)] for k, v in F.items()}
# every live feature line must still be on the page
for k, v in F.items():
    for f in v: assert f in common or f in own[k] or norm(f) in map(norm, common), f

PAY = dict(re.findall(r'<option value="(https://[^"]+)"[^>]*>\s*([^<]+?)\s*<', SRC))
pay = {label: url for url, label in PAY.items()}
def btn(label, url, cls='btn-go', note=''):
    return f'<a class="btn {cls} pay" href="{E(url)}" {EXT}>{label}</a>' + (f'<span class="pay-note">{note}</span>' if note else '')

# New feature line, added by Matteo (15 Nov 2026): Advanced and Premium only, a normal line after the training plan.
ASSESS = 'Initial Assessment Review of your training data'
# Who each package is for: short lines taken from the live FAQ answer "What would the most suitable package for me?"
FOR = {
    'basic': 'For riders who can follow the training without the human aspect of a coach.',
    'advanced': 'Access to Matteo as your coach, with feedback, phone calls and training analysis, plus Vekta.',
    'premium': 'The closest coaching: daily contact, feedback and analysis, and a weekly catch up call.',
}
def card(key, h2, term, price, per, sub, buttons, badge='', cls=''):
    top = list(own[key])
    if key in ('advanced', 'premium'): top.insert(1, ASSESS)
    rest = [f for f in F[key] if f not in own[key]]
    # Matteo, 15 Nov 2026: Basic does NOT include training analysis (the live list said "Daily Training Analysis")
    NOT_IN_BASIC = {'Daily Training Analysis'}
    no = [ASSESS] + [x for x in top if x in NOT_IN_BASIC] if key == 'basic' else []
    top = [x for x in top if x not in no]
    items = ''.join(f'<li>{E(x)}</li>' for x in top)
    items += ''.join(f'<li class="no">{E(x)} <span>(not included)</span></li>' for x in no)  # shown, not counted
    items += ''.join(f'<li class="more">{E(x)}</li>' for x in rest)
    total = len(top) + len(rest)
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
        <button type="button" class="pkg-all" aria-expanded="false" data-n="{total}">Show all {total} features ↓</button>
      </article>'''

# ---------- compare table: only the differences, wording from the live feature lines ----------
Y, N = '<span class="y" aria-label="Included">✓</span>', '<span class="n" aria-label="Not included">✗</span>'
ROWS = [
    ('Training plan', 'Daily plan built for 12 weeks', 'Daily plan built on a weekly basis', 'Daily plan built on a weekly basis'),
    ('Initial Assessment Review of your training data', N, Y, Y),
    ('Contact', 'When needed via email', 'Weekly', 'Daily'),
    ('Feedback', 'On sessions', 'Weekly', 'Daily'),
    ('Schedule adjustment', Y, 'Weekly', 'Daily'),
    ('Training analysis', N, 'Weekly', 'Daily'),
    ('Catch up call', N, 'Monthly or when needed', 'Weekly or when needed'),
    ('Race strategy', N, Y, Y),
    ('Continuous support &amp; motivation', N, Y, Y),
    ('Platform', 'Training Peaks Basic account', 'Vekta membership included (value €19.99/m)', 'Vekta membership included (value €19.99/m)'),
    ('Price', '€228 one-time for 12 weeks', '€149/mo, 6 months', '€249/mo for 3 months, €239/mo for 6'),
]
compare = ('<div class="cmp-wrap"><h3 class="h-sm">Compare packages</h3><div class="bar"></div><div class="cmp-scroll"><table class="cmp">'
           '<thead><tr><th scope="col"><span class="vh">Feature</span></th><th scope="col">Basic</th><th scope="col" class="hot">Advanced</th><th scope="col">Premium</th></tr></thead><tbody>'
           + ''.join(f'<tr><th scope="row">{r[0]}</th><td data-l="Basic">{r[1]}</td><td class="hot" data-l="Advanced">{r[2]}</td><td data-l="Premium">{r[3]}</td></tr>' for r in ROWS)
           + '</tbody></table></div><p class="cmp-note">Every package also includes the plan tailored to your availability, testing, nutrition support, the gym &amp; winter program, our community and more: open “Show all” on each card for the full list.</p></div>')

cards = ''.join([
    card('basic', 'Basic', '12 Weeks', '€19', '/week', 'Charged with one-time payment of €228 for the 12 weeks.',
         btn('Buy Basic 12 Weeks · €228', pay['Basic 12 Weeks: 228 EUR - one-time payment'], 'btn-ghost')),
    card('advanced', 'Advanced', '6 months subscription', '€149', '/mo', '',
         btn('Subscribe to Advanced · €149/mo', pay['Advanced 6 months: 149 EUR - monthly']),
         '<span class="pkg-badge">Monthly (Our Most Popular)</span>', 'hot'),
    card('premium', 'Premium', '3 months subscription (€10 off for 6 mo)', '€249', '/mo', '',
         # Premium is sold out: Matteo chose a waiting list instead of the GoCardless links (15 Nov 2026)
         '<a class="btn btn-ghost pay" href="#contact" data-waitlist="Premium">Join the waiting list</a>'
         '<span class="pay-note">Premium 3 months €249/mo · 6 months €239/mo</span>',
         '<span class="pkg-badge sold">Monthly (SOLD OUT!)</span>', 'sold'),
])

# ---------- testimonials (live quotes; photos had no alt text, see SEO-DECISIONS.md) ----------
QUOTES = re.findall(r'TXT: "(.*?)"\n<img https://[^ ]*/(unnamed-\d+)\.png', '\n'.join(TXT), re.S)
quotes = ''.join(
    f'<figure class="q"><img src="{img(n + ".png", "athlete-" + n)}" alt="Photo of a coached athlete, shown with their testimonial | Cigala Cycling Coaching" loading="lazy" width="200" height="200">'
    f'<blockquote>“{E(re.sub(r"\s*\n\s*", " ", q))}”</blockquote></figure>' for q, n in QUOTES)
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
vk_points = ''.join(f'<li>{md(x)}</li>' for x in vk[3:8])
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
faq_html = ''.join(f'<details{" open" if i == 0 else ""}><summary><h3>{E(q)}</h3></summary>' + ''.join(f'<p>{md(p).replace(chr(10), "<br>")}</p>' for p in ps) + '</details>' for i, (q, ps) in enumerate(faq))

# ---------- numbers ----------
nums = re.findall(r'H3: (.+)\nH4: (.+)', '\n'.join(section_lines('H2: 2026 IN NUMBERS', 'H2:')))
nums_html = ''.join(f'<div class="stat"><h3 class="n">{E(n)}</h3><h4 class="l">{E(l)}</h4></div>' for n, l in nums)

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

HERO = img('imgi_41_Tuz_W_Vx', 'packages-hero')
TEAM = img('imgi_21_ZtFBdo0p', 'team-training')  # clean version of the live banner photo (imgi_43, Matteo didn't want the text banner)
RIDER = img('imgi_42_FoPYDRwS', 'rider')
img('SDFASDFASDF.png', 'cigala-x-vekta'); img('PfNJBaCPkS_eSn5J', 'trainingpeaks-levels')
# dark-background versions (tools/darklogo.py): white background removed, black text turned white
for n in ('cigala-x-vekta', 'trainingpeaks-levels'):
    shutil.copy(ROOT + f'coaching/webp/darklogo-{n}.webp', OUT + f'img/{n}-dark.webp')
VKLOGO, TPLOGO = 'img/cigala-x-vekta-dark.webp', 'img/trainingpeaks-levels-dark.webp'

intro = [l[3:] for l in TXT[TXT.index('TXT: [', 0):TXT.index('TXT: 12 Weeks')] if l.startswith('P: ')]
MAIN = f'''<div class="hero hero-sm">
  <img src="{HERO}" alt="{E(live_alt('imgi_41_Tuz_W_Vx'))}" width="1148" height="766">
  <div class="in">
    <div class="eyebrow eb-pill"><span></span>Cycling coaching</div>
    <h1>Individual Cycling Coaching Packages</h1>
    <p class="lede">I have 3 coaching packages: Basic, Advanced and Premium<br>For all you can add 1 or 2 One-on-One sessions a month with myself, Matteo Cigala</p>
    <div class="ctas">
      <a class="btn btn-go" href="{CAL}" {EXT}>BOOK FREE CONSULTATION</a>
      <a class="btn btn-ghost" href="#packages">Compare packages ↓</a>
    </div>
  </div>
</div>

<section id="packages">
  <div class="in">
    <div class="notes">
      <p>{E(intro[2])}</p>
      <p>{E(intro[1])}</p>
      <p>For Advanced &amp; Premium Packages Vekta membership is included (worth €19.99/ month)<br>On demand Training Peaks Premium is also an option.</p>
    </div>
    <div class="pkgs">
      {cards}
    </div>
    {compare}
    <p class="terms"><b>By subscribing to any of our packages, you accept our Terms &amp; Conditions. View T&amp;C <a href="{C}/terms-conditions/" {EXT}>HERE</a></b></p>


    <div class="addons">
      <div class="panel addon">
        <h3 class="h-sm">Purchase multiple One-on-One Sessions</h3>
        <p>Purchase multiple One-on-One Sessions with Head Coach Matteo Cigala.</p>
        <p>Sessions are held in Wicklow Town, Co.Wicklow, Ireland and can be booked after purchase.</p>
        <a class="arrow-link" href="{C}/book-1-on-1-session/" {EXT}>Book a 1-to-1 session →</a>
      </div>
      <div class="panel addon">
        <h3 class="h-sm">Talent programme</h3>
        <p>Underage, Juniors &amp; U23 will avail of a 20% student discount for all packages.</p>
        <p>See our talent programme for more information <a href="{C}/talent-scout/" {EXT}><b>HERE</b></a></p>
        <a class="arrow-link" href="{C}/talent-scout/" {EXT}>Talent programme →</a>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head">
      <div><div class="eyebrow">Our athletes</div><h2>READ OUR TESTIMONIALS - WHAT PEOPLE SAY ABOUT CIGALA CYCLING</h2><div class="bar"></div></div>
      <a class="arrow-link" href="{C}/testimonials/" {EXT}>READ MORE TESTIMONIALS →</a>
    </div>
    <div class="quotes">{quotes}</div>
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
      <div class="vk">{vk_intro}<ul class="ticks">{vk_points}</ul>{vk_end}</div>
      <div class="ctas"><a class="btn btn-ghost" href="{VEKTA}" {EXT}>FIND MORE ABOUT VEKTA →</a></div>
    </div>
    <div class="vk-side">
      <div class="photo"><img src="{TEAM}" alt="{E(live_alt('imgi_43_K2-r3g1h'))}" loading="lazy" width="1600" height="1082"></div>
      <div class="vk-logos">
        <a href="https://joinvekta.com/partnerships" {EXT}><img src="{VKLOGO}" alt="{E(live_alt('SDFASDFASDF'))}" loading="lazy"></a>
        <span><img src="{TPLOGO}" alt="{E(live_alt('PfNJBaCPkS_eSn5J'))}" loading="lazy"></span>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Works with</div><h2 class="h-long">FOLLOW YOUR STRUCTURED TRAINING SESSIONS ON YOUR FAVOURITE DEVICES &amp; APPS (BELOW SOME APPS - THE LIST IS MUCH LONGER)</h2><div class="bar"></div></div></div>
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
    <div class="logos seen">{logos}</div>
  </div>
</section>

<section id="contact">
  <div class="in split">
    <div class="photo rider"><img src="{RIDER}" alt="{E(live_alt('imgi_42_FoPYDRwS'))}" loading="lazy" width="1000" height="1000"></div>
    <div>
      <div class="eyebrow">Check availability</div>
      <h3 class="h-sec">GET IN TOUCH TODAY</h3>
      <div class="bar"></div>
      <p class="lede">{E(intro[2])}</p>
      <form class="form panel" method="post" action="#" onsubmit="return false">
        <label>Name<input name="form_fields[name]" type="text" placeholder="Name" autocomplete="name"></label>
        <label>Email<input name="form_fields[email]" type="email" placeholder="Email" required autocomplete="email"></label>
        <label>Message<textarea name="form_fields[message]" placeholder="Your Message" rows="5"></textarea></label>
        <button class="btn btn-go" type="submit">Send &gt;</button>
      </form>
    </div>
  </div>
</section>'''

PCSS = '''<style>
.hero-sm { min-height: min(560px, 74svh); }
.hero-sm .in { padding-block: 110px 48px; }
.hero-sm h1 { max-width: 16ch; font-size: clamp(38px, 6vw, 72px); }
.notes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-bottom: 28px; }
.notes p { margin: 0; padding: 14px 16px; border-left: 2px solid var(--green); background: var(--wash); border-radius: 0 8px 8px 0; font-size: 14px; }
.pkgs { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; align-items: start; }
.pkg { position: relative; background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 28px 24px 24px; min-width: 0; }
.pkg.hot { border-color: var(--green); box-shadow: 0 0 0 1px var(--green), 0 24px 60px rgba(0,154,68,.18); }
.pkg-badge { position: absolute; top: -13px; left: 24px; font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #fff; background: var(--green); border-radius: 999px; padding: 5px 12px; }
.pkg-badge.sold { background: var(--panel-solid); border: 1px solid var(--red); color: var(--red-text, #ff3d33); }
.pkg-term { font-size: 12px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--red-text, #ff3d33); }
.pkg h2 { font-size: 40px; margin-top: 10px; }
.pkg-price { display: flex; align-items: baseline; gap: 4px; margin-top: 14px; }
.pkg-price b { font: 400 54px/1 var(--head); color: var(--text); }
.pkg-price span { color: var(--text-3); font-weight: 600; }
.pkg-sub { font-size: 13px; color: var(--text-3); margin: 8px 0 18px; min-height: 40px; }
.pkg-buy { display: grid; gap: 8px; }
.pay { width: 100%; text-align: center; }
.pay-note { display: block; font-size: 12.5px; color: var(--text-3); text-align: center; }
.pkg-lab { margin-top: 22px; padding-top: 18px; border-top: 1px solid var(--border); font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--text-3); }
.ticks { list-style: none; margin: 12px 0 0; padding: 0; display: grid; gap: 8px; }
.ticks li { position: relative; padding-left: 26px; font-size: 14px; color: var(--text-2); line-height: 1.45; }
.ticks li::before { content: ""; position: absolute; left: 0; top: 3px; width: 16px; height: 16px; border-radius: 50%; background: var(--green-wash) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M4.5 8.2l2.2 2.2 4.8-4.8' fill='none' stroke='%2334c46a' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / 16px no-repeat; }
.pkg:not(.open) .ticks li.more { display: none; }
.pkg-for { margin: 8px 0 0; font-size: 13.5px; color: var(--text-2); line-height: 1.5; min-height: 42px; }
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
.pkg-all { margin-top: 14px; font: 600 13px var(--body); color: var(--green-text); background: none; border: 0; padding: 4px 0; cursor: pointer; }
.pkg-all:hover { color: #fff; }
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
.vk p { margin: 14px 0 0; max-width: 62ch; }
.vk p a { color: var(--green-text); }
.vk .ticks { margin-top: 14px; }
.vk-side { display: grid; gap: 14px; }
.vk-side .photo { aspect-ratio: 3 / 2; }
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
document.querySelectorAll('.pkg-all').forEach(function (b) {
  b.addEventListener('click', function () {
    var o = b.closest('.pkg').classList.toggle('open');
    b.setAttribute('aria-expanded', o);
    b.textContent = o ? 'Show fewer ↑' : 'Show all ' + b.dataset.n + ' features ↓';
  });
});
document.getElementById('g-more').dataset.label = document.getElementById('g-more').textContent;
</script>'''

build('individual-packages', PATH, MAIN,
      'New Individual Packages page. Same packages, prices, payment links and copy as live; the page now has its approved H1.',
      h1='Individual Cycling Coaching Packages', extra_css=PCSS, extra_js=PJS)
print('features:', {k: len(v) for k, v in F.items()}, 'shared:', len(common), 'gallery:', len(gal), 'faq:', len(faq), 'apps:', len(DEV))
