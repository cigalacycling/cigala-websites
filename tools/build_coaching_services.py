"""Redesigned service pages (Matteo 15 Nov 2026: "redo completely in our style, improve the SEO, the wording, the linking").
  contact               /contact/               page 461
  book-1-on-1-session   /book-1-on-1-session/   page 3750   (buy link: the shop's One-on-One Sessions product)
  bike-fitting          /bike-fitting/          page 4256   (new prices €80/£70, second bike €60/£50; reservation form)
  testing               /testing/               page 3865   (INSCYD; buy link: the shop's INSCYD test product)
  about2                /about2/                page 3770   (Triathlon coaching)
  club-talk             /club-talk/             page 4395   (photos of Matteo presenting / coaching groups)

SEO (CLAUDE.md): every page keeps its URL, Yoast title and meta, H1 and live H2 wording; live copy is kept, with typos fixed;
new sections use new H2s, logged in coaching/SEO-DECISIONS.md section 13. Forms are the live Elementor form (to matteo@),
with a subject and message hint per page (build_coaching_wp: data-subject / data-msg, side content between <!--side--> marks).

  python3 -I tools/build_coaching_services.py [page ...]
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
import build_coaching_generic as G

CAL = 'https://calendly.com/cigalacycling'
SHOP_1TO1 = R + 'products/one-on-one-sessions'
SHOP_INSCYD = R + 'products/inscyd-metabolic-ppd-testing'

def ic(path): return f'<svg class="sv-ic" viewBox="0 0 24 24" aria-hidden="true">{path}</svg>'
I = {
    'phone': '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    'mail': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    'chat': '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8v.5z"/>',
    'pin': '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    'cal': '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    'bike': '<circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M15 6h2l3 11.5M5.5 17.5 9 9h7l-4 8.5M9 9 8 6H6"/>',
    'bag': '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18M16 10a4 4 0 0 1-8 0"/>',
    'star': '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
    'users': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    'mic': '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M19 10v1a7 7 0 0 1-14 0v-1M12 18v4M8 22h8"/>',
    'chart': '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
    'swim': '<path d="M2 18c2 0 2-1.5 4-1.5S8 18 10 18s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><circle cx="16" cy="7" r="2"/><path d="m6 13 4-4 3 2 3-2"/>',
    'run': '<circle cx="14" cy="4" r="2"/><path d="m6 20 3-6 3 2v5M8 9l4-2 3 3 3 1M12 7l-2 6"/>',
    'check': '<path d="M20 6 9 17l-5-5"/>',
    'power': '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
    'lab': '<path d="M9 2v6L4 18a2 2 0 0 0 2 3h12a2 2 0 0 0 2-3L15 8V2M8 2h8M7 14h10"/>',
    'list': '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    'user': '<circle cx="12" cy="7" r="4"/><path d="M4 21v-1a7 7 0 0 1 14 0v1"/>',
    'heart': '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21.2l8.8-8.8a5.5 5.5 0 0 0 0-7.8z"/>',
    'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
}

def hero(h1, eyebrow, lede, src, alt, btns, pos='50% 50%', cls=''):
    b = ''.join(f'<a class="btn {"btn-go" if i == 0 else "btn-ghost"}" href="{E(u)}" {EXT}>{t}</a>' for i, (t, u) in enumerate(btns))
    return f'''<div class="hero hero-sm {cls}">
  <img src="{src}" alt="{E(alt)}" style="object-position:{pos}">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>{eyebrow}</div>
    <h1>{h1}</h1>
    {f'<p class="lede">{lede}</p>' if lede else ''}
    <div class="ctas">{b}</div>
  </div>
</div>'''

def head(eyebrow, h, tag='h2', more=''):
    return f'<div class="head"><div><div class="eyebrow">{eyebrow}</div><{tag}{" class=h-sec" if tag == "h3" else ""}>{h}</{tag}><div class="bar"></div></div>{more}</div>'

def cards(items, cls='sv-cards'):
    """items: (icon, title, text)"""
    return f'<ul class="{cls}">' + ''.join(f'<li>{ic(I[i])}<h3 class="h-sm">{t}</h3><p>{x}</p></li>' for i, t, x in items) + '</ul>'

def enquiry(eyebrow, title, lede, side, subject, msg):
    """the live Elementor form on the right, `side` on the left (build_coaching_wp swaps the static form for the live one)"""
    return f'''<section id="contact" data-subject="{E(subject)}" data-msg="{E(msg)}">
  <div class="in split">
    <!--side--><div class="sv-side">{side}</div><!--/side-->
    <div>
      <div class="eyebrow">{eyebrow}</div>
      <h3 class="h-sec">{title}</h3>
      <div class="bar"></div>
      <p class="lede">{lede}</p>
      <form class="form panel" method="post" action="#" onsubmit="return false">
        <label>Name<input name="form_fields[name]" type="text" placeholder="Name *" required autocomplete="name"></label>
        <label>Email<input name="form_fields[email]" type="email" placeholder="Email *" required autocomplete="email"></label>
        <label>Phone<input name="form_fields[phone]" type="tel" placeholder="Phone (with country code) *" required autocomplete="tel"></label>
        <label>Message<textarea name="form_fields[message]" placeholder="{E(msg)}" rows="5" required></textarea></label>
        <button class="btn btn-go" type="submit">Send &gt;</button>
      </form>
    </div>
  </div>
</section>'''

def photo(key, name, alt=None, cls='photo sv-photo', pos=None):
    a = alt if alt is not None else live_alt(key)
    st = f' style="object-position:{pos}"' if pos else ''
    return f'<div class="{cls}"><img src="{img(key, name)}" alt="{E(a)}" loading="lazy"{st}></div>'

def faq(items):
    h = ''.join(f'<details{" open" if i == 0 else ""}><summary><h3>{E(q)}</h3></summary><p>{a}</p></details>' for i, (q, a) in enumerate(items))
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'<[^>]+>', '', a)}} for q, a in items]}
    return f'<div class="faq">{h}</div>', f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'

SOCIAL = [('Facebook', 'https://www.facebook.com/CigalaCycling/'), ('X-twitter', 'https://x.com/CigalaCycling'), ('Youtube', 'https://www.youtube.com/@cigalacycling'),
          ('Instagram', 'https://www.instagram.com/cigalacycling/'), ('Whatsapp', 'https://wa.me/message/WVBRO6XAMQMCH1'), ('Threads', 'https://www.threads.com/@cigalacycling'),
          ('Tiktok', 'http://tiktok.com/@cigalacycling')]
WA = 'https://wa.me/message/WVBRO6XAMQMCH1'

# ------------------------------------------------------------------ contact
def contact():
    side = f'''<div class="ct-cards">
      <a class="ct-card" href="tel:+35340478107">{ic(I['phone'])}<div><h2 class="ct-k">PHONE</h2><h2 class="ct-v">+353 404 78107</h2><span>Call or text</span></div></a>
      <a class="ct-card" href="mailto:info@cigalacycling.com">{ic(I['mail'])}<div><h2 class="ct-k">EMAIL</h2><h3 class="ct-v">info@cigalacycling.com</h3><span>We reply within one working day</span></div></a>
      <a class="ct-card" href="{WA}" {EXT}>{ic(I['chat'])}<div><span class="ct-k">WHATSAPP</span><span class="ct-v">Message us on WhatsApp</span><span>The quickest way to reach Matteo</span></div></a>
      <div class="ct-card ct-static">{ic(I['pin'])}<div><span class="ct-k">WHERE WE ARE</span><span class="ct-v">Co. Wicklow, Ireland</span><span>Coaching online worldwide · 1-to-1 sessions and bike fits in Wicklow Town</span></div></div>
      <div class="ct-card ct-static ct-soc"><div><h2 class="ct-k">follow us online</h2>{social_row()}</div></div>
    </div>'''
    QUICK = [('cal', 'Free consultation', 'Talk to Matteo about your goals before you sign up.', CAL, 'Book a call'),
             ('bike', 'Coaching packages', 'Basic, Advanced and Premium: cycling and triathlon.', C + '/individual-packages/', 'See the packages'),
             ('target', 'Bike fitting', 'In Wicklow Town, by appointment.', C + '/bike-fitting/', 'Reserve a bike fit'),
             ('user', '1-to-1 sessions', 'Train in person with Matteo.', C + '/book-1-on-1-session/', 'Book sessions'),
             ('star', 'Bike tours', 'Cycling holidays with Cigala Cycling Tours.', T + '/', 'Go to tours'),
             ('bag', 'Shop', 'Premium brands, with a discount for our athletes.', R, 'Go to the shop')]
    quick = '<div class="ct-quick">' + ''.join(f'<a class="panel ct-q" href="{u}" {EXT}>{ic(I[i])}<h3 class="h-sm">{t}</h3><p>{d}</p><span class="arrow-link">{b} →</span></a>' for i, t, d, u, b in QUICK) + '</div>'
    MAIN = f'''{hero('CONTACT US', 'Get in touch', 'Questions about coaching, testing, bike fitting or club talks? Call, email or send us a message and Matteo will get back to you.',
                    img('IMG_3999AWDWWWU', 'contact-hero-lake'), 'Cigala Cycling Coaching group riding in Wicklow, Ireland',
                    [('Call +353 404 78107', 'tel:+35340478107'), ('WhatsApp us', WA)], '50% 60%', 'ct-hero')}

{enquiry('Send us a message', 'GET IN TOUCH TODAY', 'Tell us a little about you and your goals. Every field is needed so we can call or email you back.',
         side, 'New message from the Coaching website (Contact page)', 'Your message *')}

<section>
  <div class="in">
    {head('Looking for something specific?', 'HOW CAN WE HELP?', 'h3')}
    {quick}
  </div>
</section>'''
    build('contact', '/contact/', MAIN, 'Contact page redesigned: phone, email, WhatsApp and the form side by side; quick links.',
          h1='CONTACT US', extra_css=G.GCSS + CSS)

# ------------------------------------------------------------------ book 1-on-1
def book():
    PRICES = [('3 Sessions', 240, 32547841572910, ''), ('6 Sessions', 480, 32547841605678, ''),
              ('10 Sessions', 750, 32547841671214, 'Best value'), ('20 Sessions', 1400, 32547841703982, '')]
    def per(n, p): return f'€{p / int(n.split()[0]):.0f} per session'
    price = '<div class="sv-prices">' + ''.join(
        f'<div class="panel sv-price{" hot" if b else ""}">{f"<span class=sv-badge>{b}</span>" if b else ""}<div class="sv-pn">{n}</div><div class="sv-pp">€{p:,}</div>'
        f'<div class="sv-ps">{per(n, p)}</div><a class="btn btn-go" href="{SHOP_1TO1}?variant={v}" {EXT}>Buy {n.lower()}</a></div>' for n, p, v, b in PRICES) + '</div>'
    side = f'''{photo('IMG_4003AWDWWWU', 'one-to-one-group-coaching', cls='photo rider')}
      <ul class="sv-facts">
        <li>{ic(I['pin'])}<span>Sessions are held in Wicklow Town, Co.Wicklow, Ireland</span></li>
        <li>{ic(I['cal'])}<span>Choose your dates after purchase: send us your preferred days and times</span></li>
        <li>{ic(I['user'])}<span>With Head Coach Matteo Cigala</span></li>
      </ul>'''
    MAIN = f'''{hero('BOOK YOUR 1 ON 1 SESSION', 'In person with Matteo', 'Train face to face with Head Coach Matteo Cigala in Wicklow, Ireland. Buy a pack of sessions, then pick your dates.',
                    img('imgi_17_zCRmNmCA', 'one-to-one-hero'), live_alt('imgi_17_zCRmNmCA'), [('See the prices ↓', '#prices'), ('Ask a question', '#contact')], '50% 35%')}

<section id="prices">
  <div class="in">
    {head('One-on-One Sessions', 'Purchase multiple One-on-One Sessions')}
    <p class="sv-lede">Purchase multiple One-on-One Sessions with Head Coach Matteo Cigala.<br>Sessions are held in Wicklow Town, Co.Wicklow, Ireland and can be booked after purchase.</p>
    {price}
    <p class="sv-note">Secure checkout on our shop, retail.cigalacycling.com. By buying you accept our <a href="{C}/terms-conditions/" {EXT}>Terms &amp; Conditions</a>.</p>
  </div>
</section>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">How it works</div>
      <h2>FROM PURCHASE TO YOUR FIRST SESSION</h2><div class="bar"></div>
      <ol class="sv-steps">
        <li><b>Choose your pack</b><span>3, 6, 10 or 20 sessions: the more sessions, the lower the price per session.</span></li>
        <li><b>Buy online</b><span>Pay securely on our shop.</span></li>
        <li><b>Book your dates</b><span>Send us your preferred days and times with the form below, and we confirm your sessions.</span></li>
        <li><b>Train with Matteo</b><span>Meet Matteo in Wicklow Town for your session.</span></li>
      </ol>
    </div>
    {photo('imgi_16_g675BzCnYW', 'one-to-one-matteo', pos='50% 30%')}
  </div>
</section>

{enquiry('Already bought your sessions?', 'BOOK YOUR DATES', 'Tell us which days and times suit you, and how many sessions you bought. We will confirm your dates.',
         side, '1-to-1 session booking (Coaching website)', 'Pack bought, preferred days and times *')}

{tools_band()}'''
    build('book-1-on-1-session', '/book-1-on-1-session/', MAIN, '1-to-1 page redesigned: the shop packs (3/6/10/20 sessions) with buy buttons, how it works, date booking form.',
          h1='BOOK YOUR 1 ON 1 SESSION', h2_changes={'add': ['FROM PURCHASE TO YOUR FIRST SESSION']}, extra_css=G.GCSS + FT_CSS + CSS)

# ------------------------------------------------------------------ bike fitting
def bikefit():
    T_ = open(ROOT + 'coaching/text/bike-fitting.txt').read()
    intro = re.search(r'P: (By working alongside Italy.*?)\n', T_).group(1).replace('for many occasion', 'on many occasions')
    quote = re.search(r'P: “(As a performance.*?)”', T_, re.S).group(1).replace('confort', 'comfort').replace('Software are great tool', 'Software is a great tool').replace('is then the experience', 'it is then the experience')
    qparas = [x.strip() for x in quote.split('\n') if x.strip()]
    GAL = [('imgi_25_XtZo', 'Bike fit session with Matteo Cigala: measuring position on a time trial bike'), ('imgi_21_rurB', 'Matteo Cigala adjusting a rider’s position during a bike fit'),
           ('imgi_20_K4nM', 'Riders and Matteo Cigala after a bike fit on a time trial bike'), ('imgi_18_wFsV', 'Matteo Cigala checking a road bike fit on the trainer'),
           ('imgi_17_Vqid', 'Bike fitting a rider in Cigala Cycling kit'), ('imgi_23_dqRg', 'Matteo Cigala fitting a young rider on a road bike'),
           ('imgi_22_NgDI', 'Bike fit adjustment on a road bike'), ('imgi_19_kjv2', 'Time trial position bike fit')]
    gal = ''.join(f'<div class="g">{G.pic([u for u in G.WEBP if k in u][0], a, "bf-g").replace("class=\"bf-g\"", "class=\"bf-g\"")}</div>' for k, a in GAL)
    PRICE = [('One bike', '€80', '£70', 'About 40 min to 1 hr'), ('Second bike', '+ €60', '+ £50', 'Same appointment')]
    price = '<div class="sv-prices sv-prices-2">' + ''.join(
        f'<div class="panel sv-price"><div class="sv-pn">{n}</div><div class="sv-pp">{e}<small> / {g}</small></div><div class="sv-ps">{d}</div></div>' for n, e, g, d in PRICE) + '</div>'
    side = f'''<div class="panel bf-info">
        <h3 class="h-sm">Your appointment</h3>
        <ul class="sv-facts">
          <li>{ic(I['clock'])}<span>Appointments are approximately 40 min to 1hr per bike.</span></li>
          <li>{ic(I['pin'])}<span>Bike fit are held in Wicklow Town, Co. Wicklow, Ireland.</span></li>
          <li>{ic(I['bike'])}<span>Bring your bike, kit, cycling shoes.</span></li>
          <li>{ic(I['star'])}<span>Limited availability.</span></li>
          <li>{ic(I['mail'])}<span>Or email <a href="mailto:bikefit@cigalacycling.com">bikefit@cigalacycling.com</a></span></li>
        </ul>
        <div class="bf-cost"><b>€80 / £70</b> for 1 bike · second bike <b>+ €60 / £50</b></div>
      </div>'''
    MAIN = f'''<div class="hero hero-sm bf-hero">
  <img src="{img('imgi_21_ZtFBdo0p', 'bike-fit-hero')}" alt="Cigala Cycling riders climbing together in Wicklow" style="object-position:50% 40%">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Bike fitting in Wicklow, Ireland</div>
    <h1>BIKE FITTING</h1>
    <p class="lede">A precise, hands-on bike fit with Head Coach Matteo Cigala: more comfort, more power, fewer niggles. €80 / £70 per bike.</p>
    <div class="ctas"><a class="btn btn-go" href="#contact">Make your reservation</a><a class="btn btn-ghost" href="#prices">Prices ↓</a></div>
  </div>
</div>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">Learned from the best</div>
      <h2>PRECISION AND EXPERIENCE</h2><div class="bar"></div>
      <p>{E(intro)}</p>
      <blockquote class="bf-quote">{''.join(f'<p>{E(x)}</p>' for x in qparas)}<cite>Matteo Cigala, Founder &amp; Head Coach</cite></blockquote>
    </div>
    {G.pic([u for u in G.WEBP if 'imgi_25_XtZo' in u][0], 'Bike fit session with Matteo Cigala: measuring position on a time trial bike', 'photo sv-photo bf-main')}
  </div>
</section>

<section>
  <div class="in">
    {head('What we look at', 'EVERY MILLIMETRE COUNTS')}
    {cards([('target', 'Saddle height &amp; setback', 'Set from how you pedal, not only from a formula.'),
            ('bike', 'Reach &amp; handlebar', 'A position you can hold for hours, on the road or on the TT bike.'),
            ('heart', 'Flexibility &amp; injuries', 'Your flexibility, bone structure, muscle mass and injury history.'),
            ('power', 'Comfort &amp; power', 'The smallest adjustments that make the difference for comfort and performance.')])}
  </div>
</section>

<section>
  <div class="in">
    {head('Behind the scenes', 'BIKE FITS WITH MATTEO')}
    <div class="bf-gal">{gal}</div>
  </div>
</section>

<section id="prices">
  <div class="in">
    {head('Prices', 'BIKE FIT PRICES')}
    {price}
    <p class="sv-note">Pay at your appointment. Limited availability: reserve your slot below.</p>
  </div>
</section>

{enquiry('Make your reservation', 'MAKE YOUR RESERVATION', 'Book an appointment by entering your details below: tell us how many bikes and the days that suit you, and we confirm your slot.',
         side, 'Bike fit reservation (Coaching website)', 'Number of bikes, road or TT, preferred days *')}

{tools_band()}'''
    build('bike-fitting', '/bike-fitting/', MAIN, 'Bike fitting redesigned: photos, new prices (€80/£70, second bike €60/£50), reservation form, free tools.',
          h1='BIKE FITTING', h2_changes={'add': ['PRECISION AND EXPERIENCE', 'EVERY MILLIMETRE COUNTS', 'BIKE FITS WITH MATTEO', 'BIKE FIT PRICES']},
          extra_css=G.GCSS + FT_CSS + CSS)

# ------------------------------------------------------------------ testing (INSCYD)
def testing():
    T_ = open(ROOT + 'coaching/text/testing.txt').read().split('\n')
    P = [l[3:] for l in T_ if l.startswith('P: ')]
    first = P[0]; claim = P[1]; paras = P[2:9]
    metrics = [l[4:] for l in T_ if l.startswith('LI: ')]
    MIC = ['heart', 'target', 'chart', 'power', 'clock', 'lab']
    INF = [('imgi_23_O2VW', 'ftp'), ('imgi_26_aHT5', 'vo2max'), ('imgi_25__Is4', 'fueling'), ('imgi_24_z4M9', 'marathon')]
    inf = ''.join(f'<a class="ts-inf" href="{img(k, "inscyd-" + n)}" {EXT}><img src="{img(k, "inscyd-" + n)}" alt="{E(live_alt(k))}" loading="lazy"></a>' for k, n in INF)
    STEPS = [('ALL YOU NEED IS A POWER METER', 'Test on your own bike with your own power meter or smart trainer: no special equipment.'),
             ('NO LAB NEEDED', 'No masks and no blood samples, and you don’t need to travel to a lab or be with us in person.'),
             ('SIMPLE PROTOCOL', 'A short set of all-out efforts, indoors or outdoors. There is even a Zwift protocol for you to use.'),
             ('FULL PROFILE', 'VO2max, anaerobic threshold, VLamax, fat and carbohydrate combustion, lactate accumulation and recovery.'),
             ('FULL METABOLIC PROFILE', 'How your aerobic and anaerobic systems work together, and how much you need to eat per hour to keep your performance.'),
             ('RESULTS REPORT', 'Your INSCYD report, with the training zones and the focus your training needs next.')]
    steps = '<ol class="ts-steps">' + ''.join(f'<li><span class="ts-n">{i + 1}</span><div><h3 class="h-sm">{t}</h3><p>{E(d)}</p></div></li>' for i, (t, d) in enumerate(STEPS)) + '</ol>'
    MAIN = f'''{hero('INSCYD METABOLIC TESTING', 'Physiological testing', 'Lab-quality metabolic testing from your own power data. €189, or included in Premium.',
                    img('imgi_22_unnamed', 'testing-hero'), 'Matteo Cigala analysing race data on a laptop in a team car', [('Buy the test · €189', SHOP_INSCYD), ('What you get ↓', '#inscyd')], '50% 40%')}

<section id="inscyd">
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">INSCYD Power-Performance Decoder</div>
      <h2>A FULL 360° PHYSIOLOGICAL ASSESSMENT</h2><div class="bar"></div>
      <p>{E(first)}</p>
      <p class="ts-claim">{E(claim.capitalize())}</p>
      {''.join(f'<p>{E(x)}</p>' for x in paras[:3])}
    </div>
    <div class="photo gn-png ts-logo"><img src="{img('imgi_3_F-6', 'inscyd-logo')}" alt="{E(live_alt('imgi_3_F-6'))}" loading="lazy"></div>
  </div>
</section>

<section>
  <div class="in">
    {head('What INSCYD measures', 'THE METRICS THAT MATTER')}
    <p class="sv-lede">{E(paras[4])}</p>
    {cards([(MIC[i], E(m), '') for i, m in enumerate(metrics)], 'sv-cards sv-mini')}
    <div class="gn-txt ts-more"><p>{E(paras[3])}</p><p>{E(paras[5])}</p><p>{E(paras[6])}</p></div>
  </div>
</section>

<section>
  <div class="in">
    {head('What the report shows', 'INSCYD VS CONVENTIONAL TESTING')}
    <div class="ts-infs">{inf}</div>
  </div>
</section>

<section>
  <div class="in">
    {head('How it works', 'WHAT WE ORGANISE')}
    {steps}
    <p class="ts-pro"><b>USED BY THE WORLD’S BEST ATHLETES</b> · WorldTour teams include Bora Hansgrohe, Lotto Jumbo Visma, Team CCC and Team Alpecin Fenix.</p>
  </div>
</section>

<section>
  <div class="in">
    {head('Prices', 'pricing')}
    <div class="sv-prices sv-prices-2">
      <div class="panel sv-price hot"><h2 class="ts-h"><span class="sv-pp">€189*</span> <span class="sv-pn">STAND ALONE TEST</span> <span class="sv-ps">*20% Discount for Members</span> <a class="btn btn-go" href="{SHOP_INSCYD}" {EXT}>BUY NOW</a></h2></div>
      <div class="panel sv-price"><h2 class="ts-h"><span class="sv-pp">iNCLUDED</span> <span class="sv-pn">For premium Package</span> <span class="sv-ps">Athlete with minimum 6 months subcription</span></h2>
        <a class="btn btn-ghost" href="{C}/individual-packages/" {EXT}>See Premium</a></div>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="band band-cta">
      <img src="{img('IMG_4003AWDWWWU', 'testing-cta')}" alt="{E(live_alt('IMG_4003AWDWWWU'))}" loading="lazy" width="2560" height="1707">
      <div class="tx">
        <div class="eyebrow">Train to your physiology</div>
        <h2>WANT TO JOIN CIGALA CYCLING?</h2>
        <div class="bar"></div>
        <p class="lede">Your INSCYD profile sets your zones and the focus of your training plan.</p>
        <div class="ctas"><a class="btn btn-go" href="{C}/individual-packages/" {EXT}>VIEW INDIVIDUAL COACHING PACKAGE</a><a class="btn btn-ghost" href="{CAL}" {EXT}>Book a free consultation</a></div>
      </div>
    </div>
  </div>
</section>

{tools_band()}'''
    build('testing', '/testing/', MAIN, 'INSCYD testing redesigned: what it measures, report graphics, the six steps with real text, prices with the shop link.',
          h1='INSCYD METABOLIC TESTING', h2_changes={'add': ['A FULL 360° PHYSIOLOGICAL ASSESSMENT', 'THE METRICS THAT MATTER', 'INSCYD VS CONVENTIONAL TESTING']},
          extra_css=G.GCSS + FT_CSS + CSS)

# ------------------------------------------------------------------ triathlon (about2)
def about2():
    T_ = open(ROOT + 'coaching/text/about2.txt').read()
    p1 = re.search(r'P: (Whether you’re training.*?)\n', T_).group(1); p2 = re.search(r'P: (Led by former.*?)\n', T_).group(1)
    WHY = [('user', 'Personalised Training Plans', 'Your plan is tailored to your schedule, fitness level, goals, and race calendar — no generic templates, ever.'),
           ('bike', 'Expert Cycling Foundation', 'Improve your strongest discipline or fix your weakest. With Matteo’s pro cycling background, you get unmatched guidance on power, pacing, and race strategy.'),
           ('swim', 'Full Triathlon Approach', 'We support all three disciplines — swim, bike, run — with balanced weekly programming and progression.'),
           ('chart', 'Data-Driven Coaching', 'Training is structured around: power and heart-rate metrics; periodisation, fueling strategy, recovery optimisation.'),
           ('chat', 'Dedicated Support', 'Regular check-ins, feedback on workouts, open communication, and guidance to keep you accountable and progressing.'),
           ('users', 'For All Levels', 'From beginners to advanced age-group or pro athletes — everyone is welcome and supported.')]
    PK = [('Basic', '€19', '/week', '12 weeks · €228 one payment', 'A personalised plan you follow on your own.'),
          ('Advanced', '€149', '/mo', '6 months subscription', 'Our most popular: weekly feedback, analysis and a monthly call.'),
          ('Premium', '€249', '/mo', '3 months subscription', 'Daily contact and feedback. Waiting list.')]
    pk = '<div class="sv-prices">' + ''.join(f'<div class="panel sv-price{" hot" if n == "Advanced" else ""}"><div class="sv-pn">{n}</div><div class="sv-pp">{p}<small>{u}</small></div><div class="sv-ps">{s}</div><p>{d}</p></div>' for n, p, u, s, d in PK) + '</div>'
    faq_html, faq_ld = faq([
        ('Do you coach sprint, Olympic, 70.3 and Ironman?', 'Yes. Our triathlon coaching covers all disciplines of triathlon from Sprint to Ironman, for first-timers and experienced age-groupers alike.'),
        ('Do you coach all three disciplines?', 'Yes. Your plan balances swim, bike and run every week, with the bike built on Matteo’s professional cycling background: power, pacing and race strategy.'),
        ('How many hours do I need to train?', 'It depends on your training availability. Your plan is built around the time you have, so every session counts.'),
        ('Which platform do you use?', 'Your plan is delivered in TrainingPeaks or Vekta and syncs to Garmin, Wahoo, Zwift and more.'),
        ('Do you offer a student discount?', 'Yes. Underage, Juniors &amp; U23 avail of a 20% student discount for all packages.')])
    MAIN = f'''<div class="hero hero-sm tri-hero">
  <img src="{img('imgi_16_d3HssY4x', 'triathlon-hero-edmonton')}" alt="{E(live_alt('imgi_16_d3HssY4x'))}" style="object-position:50% 40%">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Triathlon coaching · Sprint to Ironman</div>
    <h1>WHY CHOOSE OUR TRIATHLON COACHING?</h1>
    <p class="lede">{E(p1)}</p>
    <div class="ctas"><a class="btn btn-go" href="{C}/tri-individual-packages/" {EXT}>See our triathlon coaching packages</a><a class="btn btn-ghost" href="{CAL}" {EXT}>Book a free consultation</a></div>
  </div>
</div>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">Online triathlon coaching</div>
      <h2>SWIM, BIKE, RUN: ONE PLAN</h2><div class="bar"></div>
      <p>{E(p2)}</p>
      <p>Based in Ireland and coaching athletes worldwide, we plan your three disciplines together, around your work, family and race calendar, so you arrive at the start line fit, fresh and confident.</p>
    </div>
    {photo('imgi_17_2yiBvLGw', 'triathlon-run', 'Two triathletes racing on the run course', pos='50% 30%')}
  </div>
</section>

<section>
  <div class="in">
    {head('Why choose us', 'WHAT YOU GET')}
    {cards([(i, E(t), E(d)) for i, t, d in WHY])}
  </div>
</section>

<section>
  <div class="in">
    {head('Triathlon packages', 'TRIATHLON COACHING PACKAGES', more=f'<div class="rv-links"><a class="arrow-link" href="{C}/tri-individual-packages/" {EXT}>Compare all features →</a></div>')}
    {pk}
    <div class="ctas sv-center"><a class="btn btn-go" href="{C}/tri-individual-packages/" {EXT}>See our triathlon coaching packages</a></div>
  </div>
</section>

<section>
  <div class="in split">
    {photo('imgi_24_photo-1533049426476', 'triathlon-swim', 'Triathlete swimming freestyle in open water', pos='50% 50%')}
    <div class="gn-txt">
      <div class="eyebrow">Free tools for triathletes</div>
      <h2>KNOW YOUR NUMBERS</h2><div class="bar"></div>
      <p>Set your swim pace and your bike zones in seconds with our free calculators.</p>
      <div class="ctas"><a class="btn btn-go" href="{C}/tools/swim-pace-calculator/" {EXT}>Swim pace (CSS)</a><a class="btn btn-ghost" href="{C}/tools/training-zones-calculator/" {EXT}>Training zones</a><a class="btn btn-ghost" href="{C}/tools/" {EXT}>All free tools</a></div>
    </div>
  </div>
</section>

<section>
  <div class="in">
    {head('Good to know', 'FREQUENTLY ASKED QUESTIONS')}
    {faq_html}
  </div>
</section>'''
    build('about2', '/about2/', MAIN, 'Triathlon coaching page redesigned: why us, packages, free tools, FAQ.',
          h1='WHY CHOOSE OUR TRIATHLON COACHING?', h2_changes={'add': ['SWIM, BIKE, RUN: ONE PLAN', 'WHAT YOU GET', 'TRIATHLON COACHING PACKAGES', 'KNOW YOUR NUMBERS', 'FREQUENTLY ASKED QUESTIONS']},
          extra_css=G.GCSS + CSS, extra_js=faq_ld)

# ------------------------------------------------------------------ club talks
def clubtalk():
    T_ = open(ROOT + 'coaching/text/club-talk.txt').read()
    ps = re.findall(r'^P: (.*(?:\n(?![A-Z]+:|<).*)*)', T_, re.M)
    ps = [p.strip() for p in ps]
    led = ps[1].replace('\n', ' ')
    FORMATS = [('users', 'Club information days', 'An introduction to training with structure for your members, with time for their questions.'),
               ('mic', 'Coaching nights', 'Presentations on training, periodisation and nutrition, followed by Q&amp;A.'),
               ('bike', 'Group coaching sessions', 'On the bike with your club: skills, pacing and a structured session together.')]
    TOPICS = ['Training and periodisation', 'Nutrition and fuelling', 'Common mistakes to avoid', 'Power, heart rate and testing', 'Racing and pacing', 'Recovery']
    side = f'''{photo('imgi_14_NWZxZmK6', 'club-talk-presentation', cls='photo rider', pos='30% 40%')}
      <ul class="sv-facts">
        <li>{ic(I['pin'])}<span>These sessions can be held all over Ireland.</span></li>
        <li>{ic(I['users'])}<span>For cycling and triathlon clubs</span></li>
        <li>{ic(I['mail'])}<span>Drop us a line to organise and get a quote.</span></li>
      </ul>'''
    MAIN = f'''<div class="hero hero-sm ck-hero">
  <img src="{img('imgi_14_NWZxZmK6', 'club-talk-hero')}" alt="{E(live_alt('imgi_14_NWZxZmK6'))}" style="object-position:20% 35%">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Club talks across Ireland</div>
    <h1>Club information days, coaching nights, Q&amp;A, group coaching sessions and more</h1>
    <p class="lede">Talks and coaching sessions for cycling and triathlon clubs, led by Founder &amp; Head Coach Matteo Cigala.</p>
    <div class="ctas"><a class="btn btn-go" href="#contact">Organise a club talk</a><a class="btn btn-ghost" href="#formats">What we offer ↓</a></div>
  </div>
</div>

<section id="formats">
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">CLUB INFORMATION DAYS</div>
      <h2><a href="#contact">LEARN MORE</a></h2><div class="bar"></div>
      <p>{E(ps[1].split(chr(10))[0])}</p>
      <p>{E(ps[1].split(chr(10))[1]) if chr(10) in ps[1] else ''}</p>
      <p>{E(ps[2])}</p>
    </div>
    {photo('IMG_4003AWDWWWU', 'club-talk-group-coaching', pos='50% 50%')}
  </div>
</section>

<section>
  <div class="in">
    {head('What we offer', 'TALKS, Q&amp;A AND GROUP SESSIONS', 'h3')}
    {cards(FORMATS)}
  </div>
</section>

<section>
  <div class="in split">
    {photo('imgi_17_zCRmNmCA', 'club-talk-coaching-session', pos='50% 35%')}
    <div class="gn-txt">
      <div class="eyebrow">Topics</div>
      <h3 class="h-sec">WHAT WE TALK ABOUT</h3><div class="bar"></div>
      <ul class="ticks">{''.join(f'<li>{t}</li>' for t in TOPICS)}</ul>
      <p>Every talk is adapted to your club: road, gravel, track or triathlon, beginners or racers.</p>
    </div>
  </div>
</section>

{enquiry('Organise a club talk', 'GET A QUOTE', 'We will be glad to hear from you to organise a club talk. Tell us about your club and what you would like to cover.',
         side, 'Club talk enquiry (Coaching website)', 'Club name, location, possible dates and topics *')}'''
    build('club-talk', '/club-talk/', MAIN, 'Club talks redesigned: Matteo presenting, formats, topics, quote form.',
          h1='Club information days, coaching nights, Q&A, group coaching sessions and more', extra_css=G.GCSS + CSS)

CSS = '''<style>
#formats h2 a { color: var(--text) !important; font: inherit; text-decoration: none; }
#formats h2 a:hover { color: var(--green-text) !important; }
.sv-ic { width: 26px; height: 26px; flex: none; fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.sv-lede { color: var(--text-2); max-width: 75ch; margin: 0 0 22px; line-height: 1.65; }
.sv-note { color: var(--text-3); font-size: 14px; margin: 16px 0 0; }
.sv-note a { color: var(--green-text); }
.sv-center { justify-content: center; margin-top: 22px; }
.sv-cards { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; }
.sv-cards li { padding: 22px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); display: grid; gap: 8px; align-content: start; }
.sv-cards h3 { margin: 4px 0 0; }
.sv-cards p { margin: 0; color: var(--text-2); font-size: 15px; line-height: 1.55; }
.sv-cards p:empty { display: none; }
.sv-mini { grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); }
.sv-mini li { grid-template-columns: auto 1fr; align-items: center; padding: 16px 18px; }
.sv-mini h3 { margin: 0; font-size: 18px; }
.sv-photo { aspect-ratio: 4 / 3; }
.sv-photo img { width: 100%; height: 100%; object-fit: cover; }
.sv-prices { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; }
.sv-prices-2 { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); max-width: 820px; }
.sv-price { position: relative; padding: 24px 22px; display: grid; gap: 6px; align-content: start; }
.sv-price.hot { border-color: rgba(0,154,68,.7); }
.sv-price p { margin: 6px 0 0; color: var(--text-2); font-size: 14px; }
.sv-badge { position: absolute; top: -11px; left: 18px; background: var(--green); color: #fff; font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; padding: 4px 10px; border-radius: 999px; }
.sv-pn { font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--red-text, #ff3d33); }
.sv-pp { font: 400 44px/1 var(--head); color: var(--text); }
.sv-pp small { font: 600 15px var(--body); color: var(--text-3); margin-left: 4px; }
.sv-ps { color: var(--text-2); font-size: 14px; margin-bottom: 8px; }
.sv-price .btn { justify-self: start; margin-top: 8px; }
.ts-h { display: grid; gap: 6px; margin: 0; font: inherit; text-transform: none; }
.ts-h .sv-pp, .ts-h .sv-pn { text-transform: uppercase; }
.sv-steps { list-style: none; counter-reset: s; margin: 18px 0 0; padding: 0; display: grid; gap: 14px; }
.sv-steps li { counter-increment: s; display: grid; grid-template-columns: 36px 1fr; gap: 2px 14px; }
.sv-steps li::before { content: counter(s); grid-row: span 2; width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; background: var(--green); color: #fff; font-weight: 800; }
.sv-steps b { color: var(--text); }
.sv-steps span { color: var(--text-2); font-size: 15px; }
.sv-side { display: grid; gap: 16px; }
.sv-facts { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }
.sv-facts li { display: flex; gap: 12px; align-items: flex-start; color: var(--text-2); font-size: 15px; line-height: 1.5; }
.sv-facts a { color: var(--green-text); }
/* contact */
.ct-hero { min-height: min(440px, 60svh); }
.ct-cards { display: grid; gap: 12px; }
.ct-card { display: flex; gap: 16px; align-items: flex-start; padding: 18px 20px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); text-decoration: none; color: var(--text); transition: border-color .2s; }
a.ct-card:hover { border-color: rgba(0,154,68,.7); }
.ct-card > div { display: grid; gap: 2px; min-width: 0; }
.ct-card .ct-k { margin: 0; font: 700 11px/1.4 var(--body); letter-spacing: .12em; text-transform: uppercase; color: var(--text-3); }
.ct-card .ct-v { margin: 0; font: 600 19px/1.3 var(--body); text-transform: none; letter-spacing: 0; color: var(--text); overflow-wrap: anywhere; }
.ct-card span:last-child:not(.ct-v) { color: var(--text-3); font-size: 13px; }
.ct-soc .cc-social { margin-top: 8px; }
.ct-quick { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; }
.ct-q { display: grid; gap: 8px; padding: 22px; text-decoration: none; color: var(--text); transition: border-color .2s, transform .2s; }
.ct-q:hover { border-color: rgba(0,154,68,.6); transform: translateY(-2px); }
.ct-q h3, .ct-q p { margin: 0; }
.ct-q p { color: var(--text-2); font-size: 15px; }
/* bike fit */
.bf-quote { margin: 18px 0 0; padding: 18px 22px; border-left: 3px solid var(--green); background: rgba(255,255,255,.03); border-radius: 0 12px 12px 0; }
.bf-quote p { font-style: italic; color: var(--text) !important; margin: 0 0 10px !important; }
.bf-quote cite { font-style: normal; font-size: 13px; font-weight: 700; color: var(--green-text); }
.bf-main { aspect-ratio: 1; max-width: 520px; justify-self: center; }
.bf-main img { width: 100%; height: 100%; object-fit: cover; }
.bf-gal { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
.bf-gal .g { aspect-ratio: 1; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
.bf-gal .bf-g, .bf-gal .bf-g img { width: 100%; height: 100%; }
.bf-gal img { object-fit: cover; }
.bf-info { padding: 22px; display: grid; gap: 14px; }
.bf-info h3 { margin: 0; }
.bf-cost { padding-top: 12px; border-top: 1px solid var(--border); color: var(--text-2); }
.bf-cost b { color: var(--text); }
/* testing */
.ts-claim { font-weight: 700; color: var(--text) !important; }
.ts-logo { background: #fff; aspect-ratio: 16 / 7; display: grid; place-items: center; border-radius: 14px; }
.ts-logo img { width: 80%; height: auto; object-fit: contain; }
.ts-more { margin-top: 18px; max-width: 900px; }
.ts-infs { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.ts-inf { display: block; border-radius: 12px; overflow: hidden; background: #fff; border: 1px solid var(--border); }
.ts-inf img { width: 100%; height: auto; display: block; }
.ts-steps { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; }
.ts-steps li { display: grid; grid-template-columns: auto 1fr; gap: 14px; padding: 20px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); }
.ts-n { width: 36px; height: 36px; border-radius: 50%; display: grid; place-items: center; background: var(--green); color: #fff; font-weight: 800; }
.ts-steps h3 { margin: 4px 0 6px; }
.ts-steps p { margin: 0; color: var(--text-2); font-size: 15px; line-height: 1.55; }
.ts-pro { margin: 20px 0 0; color: var(--text-2); font-size: 14px; }
.ts-pro b { color: var(--text); }
</style>'''

PAGES = {'contact': contact, 'book-1-on-1-session': book, 'bike-fitting': bikefit, 'testing': testing, 'about2': about2, 'club-talk': clubtalk}
if __name__ == '__main__':
    for n in (sys.argv[1:] or PAGES):
        PAGES[n]()
