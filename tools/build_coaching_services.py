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
    'leaf': '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z"/><path d="M2 21c0-3 1.9-5.4 5.2-6.1C9.6 14.4 12 13 13 12"/>',
    'alert': '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
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

def enquiry(eyebrow, title, lede, side, subject, msg, tag='h3'):
    """the live Elementor form on the right, `side` on the left (build_coaching_wp swaps the static form for the live one)"""
    return f'''<section id="contact" data-subject="{E(subject)}" data-msg="{E(msg)}">
  <div class="in split">
    <!--side--><div class="sv-side">{side}</div><!--/side-->
    <div>
      <div class="eyebrow">{eyebrow}</div>
      <{tag} class="h-sec">{title}</{tag}>
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
             ('bag', 'Shop', 'Premium brands, with a discount for our athletes.', R, 'Go to the shop'),
             ('heart', 'Nutrition coaching', 'Performance nutrition with Marine Lenehan.', C + '/nutrition/', 'See nutrition'),
             ('lab', 'INSCYD testing', 'Your full metabolic profile, no lab needed.', C + '/testing/', 'See testing')]
    quick = '<div class="ct-quick">' + ''.join(f'<a class="panel ct-q" href="{u}" {EXT}>{ic(I[i])}<h3 class="h-sm">{t}</h3><p>{d}</p><span class="arrow-link">{b} →</span></a>' for i, t, d, u, b in QUICK) + '</div>'
    MAIN = f'''{hero('CONTACT US', 'Get in touch', 'Questions about coaching, testing, bike fitting or workshops? Call, email or send us a message and Matteo will get back to you.',
                    img('IMG_3999AWDWWWU', 'contact-hero-lake'), 'Cigala Cycling Coaching group riding in Wicklow, Ireland',
                    [('Call +353 404 78107', 'tel:+35340478107'), ('WhatsApp us', WA)], '50% 60%', 'ct-hero')}

{enquiry('Send us a message', "LET'S TALK ABOUT YOUR GOALS", 'Tell us a little about you and your goals. Every field is needed so we can call or email you back.',
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
              ('10 Sessions', 750, 32547841671214, ''), ('20 Sessions', 1400, 32547841703982, '')]
    def per(n, p): return f'€{p / int(n.split()[0]):.0f} per session'
    price = '<div class="sv-prices">' + ''.join(
        f'<div class="panel sv-price{" hot" if b else ""}">{f"<span class=sv-badge>{b}</span>" if b else ""}<div class="sv-pn">{n}</div><div class="sv-pp">€{p:,}</div>'
        f'<div class="sv-ps">{per(n, p)}</div><a class="btn btn-go" href="{SHOP_1TO1}?variant={v}" {EXT}>Buy {n.lower()}</a></div>' for n, p, v, b in PRICES) + '</div>'
    side = f'''<div class="photo rider"><img src="{conv('coaching/matteo-uploads/matteo-club-talk-queens-bay.webp', 'club-talk-matteo-speaking')}" alt="Matteo Cigala in the white Cigala Cycling jersey, talking to a group of riders before a ride" loading="lazy" style="object-position:40% 22%"></div>
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
          <li>{ic(I['chat'])}<span><a href="{WA}" {EXT}>Message us on WhatsApp</a></span></li>
        </ul>
        <div class="bf-cost"><b>€80 / £70</b> for 1 bike · second bike <b>+ €60 / £50</b></div>
      </div>'''
    MAIN = f'''<div class="hero hero-sm bf-hero">
  <img src="{img('imgi_21_ZtFBdo0p', 'bike-fit-hero')}" alt="Cigala Cycling riders climbing together in Wicklow" style="object-position:50% 40%">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Bike fitting in Wicklow, Ireland</div>
    <h1>BIKE FITTING</h1>
    <p class="lede">A precise, hands-on bike fit with Head Coach Matteo Cigala: more comfort, more power, fewer niggles. €80 / £70 per bike.</p>
    <div class="ctas"><a class="btn btn-go" href="#contact">Make your reservation</a><a class="btn btn-ghost" href="{WA}" {EXT}>WhatsApp us</a><a class="btn btn-ghost" href="#prices">Prices ↓</a></div>
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
    {head('Behind the scenes', 'BIKE FITS WITH CIGALA CYCLING')}
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

{enquiry('Bike fit booking', 'MAKE YOUR RESERVATION', 'Book an appointment by entering your details below: tell us how many bikes and the days that suit you, and we confirm your slot.',
         side, 'Bike fit reservation (Coaching website)', 'Number of bikes, road or TT, preferred days *')}

{tools_band()}'''
    build('bike-fitting', '/bike-fitting/', MAIN, 'Bike fitting redesigned: photos, new prices (€80/£70, second bike €60/£50), reservation form, free tools.',
          h1='BIKE FITTING', h2_changes={'add': ['PRECISION AND EXPERIENCE', 'EVERY MILLIMETRE COUNTS', 'BIKE FITS WITH CIGALA CYCLING', 'BIKE FIT PRICES']},
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
           ('users', 'For All Levels', 'From beginners to advanced age-group or pro athletes — everyone is welcome and supported.'),
           # Matteo 15 Nov: more from the packages
           ('lab', 'Testing & Zones', 'Test protocols (CP, FTP, FTHR or INSCYD) and adaptive training zones that change as you get fitter.'),
           ('heart', 'Nutrition & Mental Coach', 'Access to work 1-to-1 with our sports nutritionist, Marine Lenehan, and our mental coach, with daily carb recommendations on Advanced and Premium.')]
    PK = [('Basic', '€19', '/week', '12 weeks · €228 one payment', 'A personalised plan you follow on your own.'),
          ('Advanced', '€149', '/mo', '6 months subscription', 'Our most popular: weekly feedback, analysis and a monthly call.'),
          ('Premium', '€249', '/mo', '3 months subscription', 'Daily contact and feedback. Waiting list.')]
    pk = '<div class="sv-prices">' + ''.join(f'<div class="panel sv-price{" hot" if n == "Advanced" else ""}"><div class="sv-pn">{n}</div><div class="sv-pp">{p}<small>{u}</small></div><div class="sv-ps">{s}</div><p>{d}</p></div>' for n, p, u, s, d in PK) + '</div>'
    faq_html, faq_ld = faq([
        ('Do you coach sprint, Olympic, 70.3 and Ironman?', 'Yes. Our triathlon coaching covers all disciplines of triathlon from Sprint to Ironman, for first-timers and experienced age-groupers alike.'),
        ('Do you coach all three disciplines?', 'Yes. Your plan balances swim, bike and run every week, with the bike built on Matteo’s professional cycling background: power, pacing and race strategy.'),
        ('How many hours do I need to train?', 'It depends on your training availability. Your plan is built around the time you have, so every session counts.'),
        ('Which platform do you use?', 'Your plan is delivered in TrainingPeaks or Vekta and syncs to Garmin, Wahoo, Zwift and more.'),
        ('Do you offer a student discount?', 'Yes. Underage, Juniors &amp; U23 avail of a 20% student discount for all packages.'),
        ('Can I work 1-to-1 with a sports nutritionist?', f'Yes. Every package includes access to our sports nutritionist, Marine Lenehan (MSc, WorldTour professional cyclist). You can also add nutrition coaching with her: your daily macros and carbs per hour in the same calendar as your training, food diary reviews and a race fuelling plan for swim, bike and run. <a href="{C}/nutrition/">See how it works</a>.')])
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
    side = f'''{photo('imgi_14_NWZxZmK6', 'club-talk-presentation', cls='photo rider ck-zoom', pos='30% 40%')}
      <ul class="sv-facts">
        <li>{ic(I['pin'])}<span>These sessions can be held all over Ireland.</span></li>
        <li>{ic(I['users'])}<span>For cycling and triathlon clubs</span></li>
        <li>{ic(I['mail'])}<span>Drop us a line to organise and get a quote.</span></li>
      </ul>'''
    MAIN = f'''<div class="hero hero-sm ck-hero">
  <img src="{img('imgi_14_NWZxZmK6', 'club-talk-hero')}" alt="{E(live_alt('imgi_14_NWZxZmK6'))}" style="object-position:20% 30%;transform:scale(1.15);transform-origin:70% 20%">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Workshops across Ireland</div>
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
    <div class="photo sv-photo"><img src="{conv('coaching/matteo-uploads/matteo-club-talk-queens-bay.webp', 'club-talk-matteo-speaking')}" alt="Matteo Cigala in the white Cigala Cycling jersey, talking to a group of riders before a ride" loading="lazy" style="object-position:40% 25%"></div>
    <div class="gn-txt">
      <div class="eyebrow">Topics</div>
      <h3 class="h-sec">WHAT WE TALK ABOUT</h3><div class="bar"></div>
      <ul class="ck-topics">{''.join(f'<li>{ic(I[i])}<span>{t}</span></li>' for t, i in zip(TOPICS, ('cal', 'leaf', 'alert', 'power', 'bike', 'heart')))}</ul>
      <p>Every talk is adapted to your club: road, gravel, track or triathlon, beginners or racers.</p>
    </div>
  </div>
</section>

{enquiry('Organise a workshop', 'GET A QUOTE', 'We will be glad to hear from you to organise a workshop. Tell us about your club and what you would like to cover.',
         side, 'Club talk enquiry (Coaching website)', 'Club name, location, possible dates and topics *')}'''
    build('club-talk', '/club-talk/', MAIN, 'Club talks redesigned: Matteo presenting, formats, topics, quote form.',
          h1='Club information days, coaching nights, Q&A, group coaching sessions and more', extra_css=G.GCSS + CSS)

# ------------------------------------------------------------------ talent programme
# Eoin R.'s best power, May–Nov 2025 vs May–Nov 2026 (Vekta data; his case study in coaching_common.CASES).
# Matteo 15 Nov: show high numbers and a clear progression at every point -> both seasons, all four points.
PD = [(15, '15 s', 1041, 1145), (60, '1 min', 643, 697), (300, '5 min', 383, 414), (1500, 'Critical Power', 313, 332)]
def pd_chart():
    import math
    W, H, L, Rr, Tt, B = 760, 360, 56, 40, 24, 44
    t0, t1 = 15, 1500
    x = lambda t: L + (math.log(t) - math.log(t0)) / (math.log(t1) - math.log(t0)) * (W - L - Rr)
    y = lambda w: Tt + (1250 - w) / (1250 - 200) * (H - Tt - B)
    grid = ''.join(f'<line x1="{L}" x2="{W - Rr}" y1="{y(w):.1f}" y2="{y(w):.1f}" class="pd-grid"/><text x="{L - 8}" y="{y(w) + 4:.1f}" class="pd-ax" text-anchor="end">{w}</text>' for w in (300, 500, 700, 900, 1100))
    xt = ''.join(f'<text x="{x(t):.1f}" y="{H - B + 20}" class="pd-ax" text-anchor="{"end" if t == t1 else "middle"}">{lab}</text>' for t, lab, _, _ in PD)
    def line(i, cls):
        pts = ' '.join(f'{x(t):.1f},{y(v[i]):.1f}' for t, _, *v in PD)
        return f'<polyline points="{pts}" class="{cls}"/>' + ''.join(f'<circle cx="{x(t):.1f}" cy="{y(v[i]):.1f}" r="4.5" class="{cls}-dot"/>' for t, _, *v in PD)
    gains = ''.join(f'<text x="{x(t) + (10 if t < t1 else -10):.1f}" y="{y(b) - 10:.1f}" class="pd-lab pd-up" text-anchor="{"start" if t < t1 else "end"}">+{b - a} W</text>' for t, _, a, b in PD)
    hits = ''.join(f'<rect x="{x(t) - 22:.1f}" y="{Tt}" width="44" height="{H - Tt - B}" class="pd-hit" data-x="{x(t):.1f}" data-t="{lab}" data-b="{b}" data-a="{a}"/>' for t, lab, a, b in PD)
    svg = (f'<svg class="pd-svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="pd-t">'
           f'<title id="pd-t">Eoin’s best power one season apart: higher at every point, from 1,041 to 1,145 W for 15 seconds and from 313 to 332 W Critical Power</title>'
           f'{grid}{xt}<line x1="{L}" x2="{W - Rr}" y1="{H - B}" y2="{H - B}" class="pd-base"/>'
           f'<line class="pd-cross" x1="0" x2="0" y1="{Tt}" y2="{H - B}"/>{line(0, "pd-a")}{line(1, "pd-b")}{gains}{hits}</svg>')
    rows = ''.join(f'<tr><td>{lab}</td><td>{a} W</td><td>{b} W</td><td>+{b - a} W</td></tr>' for _, lab, a, b in PD)
    return f'''<figure class="pd panel">
      <div class="pd-top"><div><b class="pd-title">Power-duration profile</b><span>Best power, watts · Eoin R., IVCA racer, Ireland</span></div>
        <div class="pd-leg"><span><i class="pd-sw pd-sw-b"></i>2026 season with Matteo</span><span><i class="pd-sw pd-sw-a"></i>2025 season</span></div></div>
      <div class="pd-wrap">{svg}<div class="pd-tip" hidden></div></div>
      <figcaption>Higher at every point: +104 W in the 15-second sprint, +54 W over a minute, +31 W over 5 minutes and his highest Critical Power on record, 332 W. <a href="{C}/case-studies/#eoin" {EXT}>Read Eoin’s case study →</a></figcaption>
      <details class="pd-tbl"><summary>See the numbers</summary><table><thead><tr><th>Duration</th><th>2025</th><th>2026</th><th>Change</th></tr></thead><tbody>{rows}</tbody></table></details>
    </figure>'''
PD_JS = """<script>(function(){document.querySelectorAll('.pd-wrap').forEach(function(w){var tip=w.querySelector('.pd-tip'),cr=w.querySelector('.pd-cross'),svg=w.querySelector('svg');
w.querySelectorAll('.pd-hit').forEach(function(h){function on(){var x=+h.dataset.x;cr.setAttribute('x1',x);cr.setAttribute('x2',x);cr.style.opacity=1;
var a=h.dataset.a,b=h.dataset.b;tip.innerHTML='<b>'+h.dataset.t+'</b><span><i class=\\"pd-sw pd-sw-b\\"></i>2026: '+b+' W</span>'+(a?'<span><i class=\\"pd-sw pd-sw-a\\"></i>2025: '+a+' W</span><em>+'+(b-a)+' W</em>':'');
var r=svg.getBoundingClientRect(),px=x/760*r.width;tip.hidden=false;tip.style.left=Math.min(Math.max(px-70,0),r.width-150)+'px';}
function off(){tip.hidden=true;cr.style.opacity=0;}h.addEventListener('mouseenter',on);h.addEventListener('mouseleave',off);h.addEventListener('click',on);});});})();</script>"""

def talent():
    T_ = open(ROOT + 'coaching/text/talent-scout.txt').read()
    blk = lambda a, b: re.search(re.escape(a) + r'\n(?:H4|H3): (.*?)\n(?=H[23]:|<img|$)', T_, re.S).group(1).strip()
    what = blk('H3: What is the Cigala Cycling Talent Programme?', '').replace('It is coaching relationship', 'It is a coaching relationship')
    helpme = blk('H3: How the programme can help me?', '').replace('A&J all sports', 'A&J AllSports')
    start = blk('H3: What do I need to do to get started?', '').replace('a Skype interview', 'a video call')
    cost = blk("H3: What's the cost?", '').replace('\nSee the Advanced Package', '').replace('at €104', 'at €119.20 a month (20% off €149)')
    scout = re.search(r'H2: We are a Talent Scout\nH3: (.*?)\n', T_).group(1)
    aj = re.search(r'H2: TALENT SCOUT\nH3: (.*?)\nH2:', T_, re.S).group(1).replace('mange', 'manage').replace('A&j', 'A&J').replace('to taking care', 'to take care')
    wins = [w.strip() for w in re.search(r'H2: RACES WON BY ATHLETES WITH A&J\nH3: (.*)', T_, re.S).group(1).replace('​', '').replace('Tour De\n France', 'Tour De France').split('\n') if w.strip()]
    FIX = {'Jerserys': 'Jerseys', 'Tour Deuphine': 'Critérium du Dauphiné', 'Tour De France': 'Tour de France', "Giro D'Italia": "Giro d'Italia", 'Giro Di Lombardia': 'Il Lombardia', 'Tour De Suisse': 'Tour de Suisse', 'Liege-Bastogne-Liege': 'Liège-Bastogne-Liège'}
    def fx(w):
        for a, b in FIX.items(): w = w.replace(a, b)
        return w
    wins = [fx(w) for w in wins]
    VER = {'Tour de France': '7', "Giro d'Italia": '6', 'Vuelta': '4', 'World Championships': '45'}   # aejallsports.ch, 15 Nov 2026
    wins = [re.sub(r'^\d+(\s*x\s*)(.*)$', lambda m: (VER.get(m.group(2).strip()) or m.group(0).split('x')[0].strip()) + m.group(1) + m.group(2), w) for w in wins]
    def win(w):
        m = re.match(r'(\d+)\s*x\s*(.*)', w)
        return f'<li><b><span class="tl-n" data-n="{m.group(1)}">{m.group(1)}</span>×</b><span>{E(m.group(2))}</span></li>' if m else f'<li><b>All</b><span>{E(w[4:] if w.startswith("All ") else w)}</span></li>'
    wins_html = '<ul class="tl-wins">' + ''.join(win(w) for w in wins) + '</ul>'
    para = lambda t: ''.join(f'<p>{E(x.strip())}</p>' for x in t.split('\n') if x.strip())
    LOOK = [('chart', 'Power profile', 'Best power from a 5-second sprint to an hour, compared with what riders at the next level produce.'),
            ('power', 'Critical Power &amp; W′', 'How much you can sustain, and how many hard efforts you have in the tank.'),
            ('clock', 'Durability', 'The power you still have after hours of racing: where races are won.'),
            ('target', 'Race files', 'Every race analysed: where you lost time, where you can win.'),
            ('heart', 'Recovery &amp; load', 'Training load, sleep and recovery, so you improve without burning out.'),
            ('star', 'Year-on-year progression', 'The numbers that show a team you are on the way up.'),
            ('bike', 'Pacing &amp; race tactics', 'How you spend your energy in a race: when to sit in, when to go, and how to finish the job.'),
            ('lab', 'Physiology testing', 'INSCYD metabolic testing: VO2max, VLamax, fat and carb use, so training targets what holds you back.')]
    faq_items = [('What is the Cigala Cycling Talent Programme?', E(what)), ('How can the programme help me?', '<br>'.join(E(x) for x in helpme.split('\n'))),
                 ('What do I need to do to get started?', '<br>'.join(E(x) for x in start.split('\n'))),
                 ("What's the cost?", '<br>'.join(E(x) for x in cost.split('\n')) + f' <a href="{C}/individual-packages/" {EXT}>See the Advanced Package</a>'),
                 ('Does the programme include nutrition?', f'Yes, if you want it. You can add 1-to-1 nutrition coaching with our sports nutritionist, Marine Lenehan: a WorldTour Pro with LIDL-TREK, 2× Irish National Champion and Amateur Gravel World Champion 2024. She writes your daily macros, carbs per hour and nutrition notes into the same calendar as your training, reviews your food diary and builds your race fuelling and gut training. <a href="{C}/nutrition/#upgrade" {EXT}>Read more about nutrition coaching</a>'),
                 ('What does my training calendar look like?', 'Every session is planned in your calendar on Vekta, synced to your devices and apps, with the targets for the day. If you work with Marine, her nutrition notes and carbs per hour sit next to each session (see the example above). After each ride you add your RPE and a comment, so Matteo can adapt the plan.'),
                 ('Who are A&amp;J AllSports?', 'A&amp;J AllSports is the sports management agency of Alex and Johnny Carera, founded in 1997. It represents some of the best riders in the WorldTour, such as Tadej Pogačar, Isaac Del Toro, Biniam Girmay and Jasper Philipsen, and in the past Chris Froome and Vincenzo Nibali.'),
                 ('Can I stay with my club or team?', 'Yes. The programme is your coaching: you keep racing with your club or team, and Matteo plans your training around your race calendar.'),
                 ('Does joining guarantee a professional contract?', 'No. Nobody can promise that. What we promise is world-class coaching, an honest analysis of your numbers, and that when a rider is ready, the right people hear about it.')]
    faq_html, faq_ld = faq(faq_items)
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        import build_coaching_nutrition as NUT
        import build_coaching_packages as PK
    # wins from aejallsports.ch/history (Del Toro, Girmay, Philipsen: well-known results; A&J lists them as its riders in the press)
    RIDERS = [('Tadej Pogačar', 'Tour de France 2020, 2021, 2024, 2025 · World Champion 2024, 2025 · Giro d’Italia 2024'),
              ('Isaac Del Toro', 'Tour de l’Avenir 2023'), ('Biniam Girmay', 'Green jersey, Tour de France 2024'),
              ('Jasper Philipsen', 'Milan–San Remo 2024'), ('Elisa Balsamo', 'World Champion 2021'), ('Vittoria Guazzini', 'Olympic Games 2024'),
              ('Paula Blasi', 'La Vuelta Femenina 2026'), ('Vincenzo Nibali', 'Giro d’Italia 2013, 2016 · Tour de France 2014'),
              ('Chris Froome', 'Tour de France 2013'), ('Fabio Aru', 'Vuelta a España 2015'), ('Thor Hushovd', 'World Champion 2010'),
              ('Damiano Cunego', 'Giro d’Italia 2004'), ('Gilberto Simoni', 'Giro d’Italia 2001, 2003'), ('Danilo Di Luca', 'Giro d’Italia 2007')]
    STEPS = [('Apply', 'Contact us at info@cigalacycling.com or with the form below to state your interest in the programme. Tell us your age, club, results so far and goals.'),
             ('Interview', 'If we have availability, a video call or face to face interview might be requested, so we get to know you and your goals.'),
             ('Sign up', 'We send you the link to sign up to the Advanced Package at the talent price: €119.20 a month, 20% off €149.'),
             ('Deep assessment', 'Your power data, race files and testing: where you are today and how far you are from the level the teams look for.'),
             ('Train &amp; race', 'Your plan in your calendar, adjusted week by week around school, work and your race calendar.'),
             ('Get seen', 'Your progress is shared with the right people at the right time: A&amp;J AllSports and the professional teams we work with.')]
    side = f'''{photo('imgi_17_zCRmNmCA', 'talent-coaching-session', cls='photo rider', pos='50% 35%')}
      <ul class="sv-facts">
        <li>{ic(I['user'])}<span>For riders aged 15 to 22</span></li>
        <li>{ic(I['chat'])}<span>A video call or face to face interview might be requested before getting started</span></li>
        <li>{ic(I['star'])}<span>Limited availability</span></li>
      </ul>'''
    MAIN = f'''<div class="hero hero-sm tl-hero">
  <img src="{img('imgi_17_JKPi1bTj', 'talent-hero-ras')}" alt="{E(live_alt('imgi_17_JKPi1bTj'))}" style="object-position:60% 30%">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Ages 15–22 · Talent scout for A&amp;J AllSports</div>
    <h1>Cigala Cycling Talent Programme</h1>
    <p class="lede">World-class coaching for young riders who want to turn professional, from a coach who is a talent scout for A&amp;J AllSports: the agency of Tadej Pogačar and other WorldTour stars.</p>
    <div class="ctas"><a class="btn btn-go" href="#contact">Apply to the programme</a><a class="btn btn-ghost" href="#data">How we find talent ↓</a></div>
  </div>
</div>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">Our aim</div>
      <h2>We are a Talent Scout</h2><div class="bar"></div>
      <p class="tl-big">{E(scout)}</p>
      <p>{E(what)}</p>
      <p>Matteo Cigala is a talent scout for <b>A&amp;J AllSports</b>, the agency of some of the best riders in the WorldTour, such as <b>Tadej Pogačar</b>, <b>Isaac Del Toro</b>, <b>Biniam Girmay</b> and <b>Jasper Philipsen</b>. On the programme you get world-class coaching from him, and when you are ready, the agency and the teams hear about you.</p>
    </div>
    <a class="photo gn-png tl-aj" href="https://aejallsports.ch/" {EXT}><img src="{conv('coaching/matteo-uploads/aj-allsports-logo.png', 'talent-aj-allsports-logo')}" alt="{E(live_alt('T161857.829'))}" loading="lazy"></a>
  </div>
  <div class="in tl-rwrap">
      <p class="tl-rl">Riders managed by A&amp;J, past and present <span>(hover or tap a name)</span></p>
      <ul class="tl-riders" aria-label="Riders managed by A&amp;J AllSports">{''.join(f'<li tabindex="0" data-win="{E(w)}">{n}<span class="vh">: {E(w)}</span></li>' for n, w in RIDERS)}</ul>
  </div>
</section>

<section id="data">
  <div class="in">
    {head('How we find talent', 'THE DATA BEHIND THE TALENT')}
    <p class="sv-lede">Turning pro is not just about numbers, but the numbers open the door. Matteo analyses every ride and race file to see where a rider is today, how fast they are improving, and how far they are from the level the teams look for.</p>
    {pd_chart()}
    {cards(LOOK)}
  </div>
</section>

<section>
  <div class="in split">
    <div class="photo sv-photo tl-carera"><img src="{conv('coaching/matteo-uploads/aj-allsports-carera-team.webp', 'talent-aj-allsports-team')}" alt="The A&amp;J AllSports team, including founders Alex and Johnny Carera" loading="lazy" style="object-position:50% 25%"></div>
    <div class="gn-txt">
      <div class="eyebrow">A&amp;J AllSports</div>
      <h2>TALENT SCOUT</h2><div class="bar"></div>
      {para(aj)}
    </div>
  </div>
</section>

<section>
  <div class="in">
    {head('The agency’s riders', 'RACES WON BY ATHLETES WITH A&amp;J')}
    {wins_html}
    <p class="tl-src">Grand Tours and world titles as listed by <a href="https://aejallsports.ch/about-us/" {EXT}>A&amp;J AllSports</a>, November 2026.</p>
  </div>
</section>

<section>
  <div class="in">
    {head('From application to coaching', 'HOW IT WORKS', 'h3')}
    <ol class="tl-days">{''.join(f'<li class="tl-day"><div class="tl-num"><span><small>STEP</small>{n}</span></div><div class="panel tl-box"><h3 class="h-sm">{t}</h3><p>{d}</p></div></li>' for n, (t, d) in enumerate(STEPS, 1))}</ol>
  </div>
</section>

<section>
  <div class="in split tl-cal">
    <div class="gn-txt">
      <div class="eyebrow">Training &amp; nutrition</div>
      <h3 class="band-title">ONE CALENDAR</h3><div class="bar"></div>
      <p>Your sessions, targets and, if you add nutrition coaching with our sports nutritionist Marine Lenehan, your daily macros, carbs per hour and nutrition notes: all in one calendar, synced to your devices.</p>
      <div class="ctas"><a class="btn btn-go" href="{C}/nutrition/#upgrade" {EXT}>Read more about nutrition coaching</a></div>
    </div>
    <figure class="nu-cal pk-cal">
      <div class="cal-scroll" tabindex="0" aria-label="Example days from an athlete's calendar, with nutrition"><div class="cal-row">{NUT.cal_days(('21', '24', '26'))}</div></div>
      <figcaption>Example days from an athlete’s calendar.</figcaption>
    </figure>
  </div>
</section>

<section>
  <div class="in">
    {head('Good to know', 'FREQUENTLY ASKED QUESTIONS')}
    {faq_html}
  </div>
</section>

{enquiry('Apply to the programme', "LET'S WORK TOGETHER", 'Tell us about you: age, club, results so far and your goals. If we have availability, we will send you the link to sign up.',
         side, 'Talent Programme application (Coaching website)', 'Age, club, results so far and goals *', tag='h2')}'''
    build('talent-scout', '/talent-scout/', MAIN, 'Talent Programme redesigned: the scout and A&J, a real power-duration chart, what Matteo analyses, wins, how it works, FAQ.',
          h1='Cigala Cycling Talent Programme', h2_changes={'add': ['THE DATA BEHIND THE TALENT']}, extra_css=G.GCSS + CSS + TL_CSS + PK.CAL_CSS, extra_js=faq_ld + PD_JS + WIN_JS)

WIN_JS = """<script>(function(){var l=document.querySelectorAll('.tl-n');if(!l.length||!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
l.forEach(function(e){e.textContent='0';});var io=new IntersectionObserver(function(es){es.forEach(function(x){if(!x.isIntersecting)return;io.unobserve(x.target);var el=x.target,n=+el.dataset.n,t0=null;
function f(t){if(!t0)t0=t;var k=Math.min((t-t0)/1400,1);el.textContent=Math.round(n*(1-Math.pow(1-k,3)));if(k<1)requestAnimationFrame(f);}requestAnimationFrame(f);});},{threshold:.4});l.forEach(function(e){io.observe(e);});})();</script>"""
TL_CSS = """<style>
.tl-hero { min-height: min(560px, 74svh); }
.tl-big { font-size: 18px !important; color: var(--text) !important; font-weight: 600; }
.tl-aj { background: #fff; border-radius: 14px; display: grid; place-items: center; aspect-ratio: 16 / 9; }
.tl-aj img { width: min(70%, 300px); height: auto; object-fit: contain; }
.pd { margin: 0 0 clamp(36px, 5vw, 56px) !important; padding: 22px; display: grid; gap: 14px; }
.pd-top { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px 20px; }
.pd-top > div:first-child { display: grid; gap: 2px; }
.pd-title { font: 400 24px/1.1 var(--head); text-transform: uppercase; color: var(--text); }
.pd-top span { color: var(--text-3); font-size: 13px; }
.pd-leg { display: flex; gap: 16px; align-items: center; font-size: 13px; color: var(--text-2); }
.pd-leg span { display: inline-flex; align-items: center; gap: 6px; color: var(--text-2) !important; }
.pd-sw { display: inline-block; width: 18px; height: 0; border-top: 2px solid #2fae5f; }
.pd-sw-a { border-top: 2px dashed #5f86c9; }
.pd-wrap { position: relative; overflow-x: auto; scrollbar-width: thin; }
@media (max-width: 640px) { .pd-svg { min-width: 600px; } }
.pd-svg { width: 100%; height: auto; display: block; }
.pd-grid { stroke: rgba(255,255,255,.07); stroke-width: 1; }
.pd-base { stroke: rgba(255,255,255,.25); stroke-width: 1; }
.pd-ax { fill: #8a8f98; font: 500 12px var(--body); }
.pd-a { fill: none; stroke: #5f86c9; stroke-width: 2; stroke-dasharray: 6 5; }
.pd-b { fill: none; stroke: #2fae5f; stroke-width: 2.5; }
.pd-a-dot { fill: #5f86c9; stroke: #0f1011; stroke-width: 2; }
.pd-b-dot { fill: #2fae5f; stroke: #0f1011; stroke-width: 2; }
.pd-lab { font: 700 12px var(--body); fill: #d0d6e0; }
.pd-cross { stroke: rgba(255,255,255,.35); stroke-width: 1; opacity: 0; }
.pd-hit { fill: transparent; cursor: crosshair; }
.pd-tip { position: absolute; top: 6px; width: 150px; padding: 10px 12px; border-radius: 10px; background: rgba(8,9,10,.95); border: 1px solid rgba(255,255,255,.14); display: grid; gap: 4px; font-size: 13px; color: var(--text-2); pointer-events: none; }
.pd-tip[hidden] { display: none !important; }
.pd-tip b { color: var(--text); }
.pd-tip span { display: flex; align-items: center; gap: 6px; }
.pd-tip em { font-style: normal; font-weight: 700; color: var(--text); }
.pd figcaption { color: var(--text-2); font-size: 14px; }
.pd figcaption a { color: var(--green-text); }
.pd-tbl summary { cursor: pointer; color: var(--green-text); font-size: 13px; font-weight: 600; }
.pd-tbl table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; color: var(--text-2); }
.pd-tbl th, .pd-tbl td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--border); }
.pd-tbl th { color: var(--text); }
.tl-wins { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; }
.tl-wins li { transition: transform .25s, border-color .25s, background .25s; }
.tl-wins li:hover { transform: translateY(-4px); border-color: var(--green); background: linear-gradient(160deg, rgba(0,154,68,.22), transparent 70%), var(--panel); }
.tl-wins li:hover b { color: #f0bf00; }
.tl-wins li { padding: 16px 18px; border: 1px solid var(--border); border-radius: 12px; background: var(--panel-grad), var(--panel); display: grid; gap: 2px; }
.tl-wins b { font: 400 30px/1 var(--head); color: var(--green-text); font-variant-numeric: tabular-nums; }
.tl-wins b span { color: inherit !important; font: inherit !important; }
.tl-src { margin: 14px 0 0; font-size: 13px; color: var(--text-3); }
.tl-src a { color: var(--green-text); }
.tl-carera { background: #f4f4f2; }
.tl-carera img { object-fit: cover; }
a.tl-aj { text-decoration: none; }
.tl-riders { list-style: none; margin: 14px 0 0; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; }
.tl-rwrap { margin-top: 26px; }
.tl-rl { margin: 0 !important; font-size: 12px !important; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--green-text) !important; }
.tl-rl span { text-transform: none; letter-spacing: 0; font-weight: 400; color: var(--text-3); }
.tl-riders li { position: relative; padding: 6px 12px; border-radius: 999px; border: 1px solid var(--border-strong); font-size: 13px; font-weight: 600; color: var(--text); cursor: default; transition: background .2s, border-color .2s, color .2s; outline: none; }
.tl-riders li:hover, .tl-riders li:focus { background: var(--green); border-color: var(--green); color: #fff; }
.tl-riders li::after { content: attr(data-win); position: absolute; left: 50%; bottom: calc(100% + 10px); transform: translate(-50%, 4px); width: max-content; max-width: 260px; padding: 9px 12px; border-radius: 10px; background: rgba(8,9,10,.96); border: 1px solid var(--green); color: var(--text); font-size: 12.5px; font-weight: 500; line-height: 1.4; text-align: center; white-space: normal; opacity: 0; pointer-events: none; transition: opacity .2s, transform .2s; z-index: 5; }
.tl-riders li:hover::after, .tl-riders li:focus::after { opacity: 1; transform: translate(-50%, 0); }
.tl-riders li:first-child::after { left: 0; transform: translate(0, 4px); } .tl-riders li:first-child:hover::after, .tl-riders li:first-child:focus::after { transform: none; }
.pd-up { fill: #34c46a; }
.pd-sw-dot { width: 9px; height: 9px; border: 0 !important; border-radius: 50%; background: #5f86c9; }
.tl-days { list-style: none; margin: 0; padding: 0; max-width: 860px; }
.tl-day { display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 20px; position: relative; padding-bottom: 22px; }
.tl-day::before { content: ""; position: absolute; left: 31px; top: 64px; bottom: 0; width: 2px; background: var(--border-strong); }
.tl-day:last-child { padding-bottom: 0; }
.tl-day:last-child::before { display: none; }
.tl-num { width: 64px; height: 64px; border-radius: 50%; display: grid; place-items: center; background: var(--panel-solid, #16181a); border: 2px solid var(--green); font: 400 26px/1 var(--head); color: var(--text); text-align: center; }
.tl-num small { display: block; font: 700 9px/1 var(--body); letter-spacing: .12em; color: var(--text-3); margin-bottom: 3px; }
.tl-box { padding: 18px 22px; min-width: 0; display: block !important; }   /* the title above the text, as in the Tours itinerary */
.tl-box h3 { margin: 0 0 6px; }
.tl-box p { margin: 0; }
.tl-cal { align-items: center; }
.tl-cal .pk-cal figcaption { font-size: 13px; color: var(--text-3); }
@media (max-width: 600px) { .tl-day { grid-template-columns: 48px minmax(0, 1fr); gap: 14px; } .tl-num { width: 48px; height: 48px; font-size: 20px; } .tl-num small { font-size: 8px; } .tl-day::before { left: 23px; top: 48px; } .tl-box { padding: 16px; } }
.tl-wins span { color: var(--text); font-weight: 600; font-size: 14px; }
</style>"""

# ------------------------------------------------------------------ coaching vision
def vision():
    T_ = open(ROOT + 'coaching/text/coaching-vision.txt').read()
    quote = re.search(r'P: “(.*?)”', T_).group(1)
    why = re.search(r'H3: WHY A CYCLING COACH\?\nP: (.*?)\n', T_).group(1)
    APP = [('target', 'Your goals first', 'At Cigala Cycling, we start by understanding your goals, abilities, and limitations.'),
           ('cal', 'A periodised annual plan', 'From there, we build an annual training plan that is periodised and tailored with daily sessions designed specifically for you.'),
           ('clock', 'Built around your life', 'Your plan is created to maximise your time on the bike and fit around your schedule, goals, and lifestyle. Every plan is hand-crafted, completely customised, and built for your training availability — no two plans are alike, no copy-paste templates.'),
           ('chat', 'A two-way process', 'Coaching is a two-way process. With your ongoing feedback, we adjust your training load and schedule as needed to ensure continuous improvement.')]
    PK = [('Basic', '€19', '/week', '12 weeks · €228 one payment', 'A personalised plan you follow on your own.'),
          ('Advanced', '€149', '/mo', '6 months subscription', 'Our most popular: weekly feedback, analysis, a monthly call and Vekta.'),
          ('Premium', '€249', '/mo', '3 months subscription', 'The closest coaching: daily contact and feedback.')]
    pk = '<div class="sv-prices">' + ''.join(f'<div class="panel sv-price{" hot" if n == "Advanced" else ""}"><div class="sv-pn">{n}</div><div class="sv-pp">{p}<small>{u}</small></div><div class="sv-ps">{s_}</div><p>{d}</p></div>' for n, p, u, s_, d in PK) + '</div>'
    MAIN = f'''<div class="hero hero-sm vi-hero">
  <img src="{img('V6A9680-scaled', 'vision-hero-matteo')}" alt="Matteo Cigala in the Cigala Cycling kit looking over a mountain valley" style="object-position:18% 40%">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Our vision</div>
    <h1>Train Smarter. Ride Faster.</h1>
    <p class="lede">Structured, personalised coaching that makes every hour on the bike count.</p>
    <div class="ctas"><a class="btn btn-go" href="{C}/individual-packages/" {EXT}>View our coaching packages</a><a class="btn btn-ghost" href="{CAL}" {EXT}>Book a free consultation</a></div>
  </div>
</div>

<section>
  <div class="in split vi-q">
    <div class="gn-txt">
      <div class="eyebrow">Train Smarter. Ride Faster.</div>
      <h2>It's our vision</h2><div class="bar"></div>
      <blockquote class="bf-quote vi-quote"><p>“{E(quote)}”</p><cite>Matteo Cigala – Founder &amp; Head Coach</cite></blockquote>
    </div>
    <div class="vi-sig"><img src="{conv('coaching/brand/matteo-cigala-author-signature.webp', 'vision-matteo-signature')}" alt="Matteo Cigala, Founder &amp; Head Coach, in the white Cigala Cycling jersey, with his signature" loading="lazy" width="720" height="933"></div>
  </div>
</section>

<section>
  <div class="in">
    <div class="gn-txt vi-why">
      <div class="eyebrow">Why a coach</div>
      <h3 class="h-sec">WHY A CYCLING COACH?</h3><div class="bar"></div>
      <p>{E(why)}</p>
    </div>
  </div>
</section>

<section>
  <div class="in">
    {head('How we coach', 'OUR COACHING APPROACH', 'h3')}
    {cards([(i, t, E(d)) for i, t, d in APP])}
    <p class="vi-result">The result? You train smarter, ride faster, and achieve your goals. That’s our vision.</p>
  </div>
</section>

<section>
  <div class="in">
    <div class="vi-montage"><img src="{img('imgi_23_IRXpnPR4', 'vision-over-a-decade')}" alt="{E(live_alt('imgi_23_IRXpnPR4'))}" loading="lazy" width="1600" height="900"></div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Good value</div><h2>Time on the bike maximised with structured training periodised to your goals.</h2><div class="bar"></div></div></div>
    <p class="vi-value"><b>Good value. No matter what package you choose.</b> The packages start from only 19 euro/week. Yes, you read it right. Less than a coffee a day.</p>
    {pk}
    <div class="ctas sv-center"><a class="btn btn-go" href="{C}/individual-packages/" {EXT}>View our coaching packages</a><a class="btn btn-ghost" href="{C}/tri-individual-packages/" {EXT}>Triathlon packages</a></div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head">
      <div><div class="eyebrow">Real results</div><h2>READ OUR CASE STUDIES</h2><div class="bar"></div></div>
      <div class="rv-links"><a class="btn btn-go" href="{C}/case-studies/" {EXT}>Read our case studies</a><a class="btn btn-ghost" href="{C}/testimonials/" {EXT}>Read more testimonials</a></div>
    </div>
    {case_cards(C + '/case-studies/')}
  </div>
</section>

<section>
  <div class="in">
    {head('Press &amp; partners', 'AS SEEN IN')}
    {seen_logos()}
  </div>
</section>

{tools_band()}'''
    build('coaching-vision', '/coaching-vision/', MAIN, 'Coaching Vision redesigned: quote, approach with icons, value, packages, case studies, As seen in.',
          h1='Train Smarter. Ride Faster.', h2_changes={'drop': ['READ OUR TESTIMONIALS - WHAT PEOPLE SAY ABOUT CIGALA CYCLING'], 'add': ['READ OUR CASE STUDIES']},
          extra_css=G.GCSS + FT_CSS + CS_CSS + CSS + VI_CSS)

VI_CSS = """<style>
.vi-hero { min-height: min(560px, 74svh); }
.vi-q { align-items: center; }
.vi-quote p { font-size: 18px !important; line-height: 1.6 !important; }
.vi-sig { justify-self: center; max-width: 340px; }
.vi-sig img { width: 100%; height: auto; display: block; }
.vi-why { max-width: 900px; }
.vi-result { margin: 22px 0 0; font: 400 24px/1.2 var(--head); text-transform: uppercase; color: var(--green-text); }
.vi-montage { max-width: 760px; margin: 0 auto; }   /* Matteo 15 Nov: smaller, it loses quality when big */
.vi-montage img { width: 100%; height: auto; display: block; border-radius: 16px; }
.vi-value { color: var(--text-2); font-size: 17px; margin: 0 0 20px; max-width: 70ch; }
.vi-value b { color: var(--text); }
</style>"""

CSS = '''<style>
.ck-topics { list-style: none; margin: 14px 0 16px; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
.ck-topics li { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border: 1px solid var(--border); border-radius: 12px; background: var(--panel-grad), var(--panel); font-weight: 600; color: var(--text); font-size: 15px; }
.ck-topics .sv-ic { flex: none; width: 36px; height: 36px; padding: 8px; border-radius: 10px; background: var(--green-wash); stroke: var(--green-text); }
#formats h2 a { color: var(--text) !important; font: inherit; text-decoration: none; }
#formats h2 a:hover { color: var(--green-text) !important; }
.ck-zoom img { transform: scale(1.18); transform-origin: 75% 25%; }   /* hides the photographer's credit in the corner */
.ck-hero { overflow: hidden; }
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
.sv-mini li { grid-template-columns: 26px 1fr; align-items: center; align-content: center; padding: 16px 18px; min-height: 72px; }
.sv-mini li .sv-ic { align-self: center; justify-self: center; }
.sv-mini h3 { margin: 0; font-size: 18px; }
.sv-photo { aspect-ratio: 4 / 3; }
.sv-photo img { width: 100%; height: 100%; object-fit: cover; }
.sv-prices { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; }
.sv-prices-2 { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); max-width: 820px; }
.sv-price { position: relative; padding: 24px 22px; display: grid; gap: 6px; align-content: start; }
.sv-price.hot { border-color: rgba(0,154,68,.7); }
.sv-price { transition: transform .25s, box-shadow .25s, border-color .25s; }
.sv-price:hover { transform: translateY(-4px); border-color: var(--green); box-shadow: 0 0 0 1px var(--green), 0 22px 50px rgba(0,154,68,.18); }   /* Matteo 15 Nov: highlight on hover */
.sv-price:hover .sv-pp { color: var(--green-text); }
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
.sv-steps li { counter-increment: s; display: grid; grid-template-columns: 36px 1fr; gap: 2px 14px; position: relative; }
.sv-steps li:not(:last-child)::after { content: ""; position: absolute; left: 16px; top: 36px; bottom: -14px; width: 2px; background: var(--border-strong); }   /* Matteo 15 Nov: a line joining the dots */
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
.ct-card { display: flex; gap: 16px; align-items: center; padding: 18px 20px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); text-decoration: none; color: var(--text); transition: border-color .2s; }
a.ct-card:hover { border-color: rgba(0,154,68,.7); }
.ct-card > div { display: grid; gap: 2px; min-width: 0; }
.ct-card .ct-k { margin: 0; font: 700 11px/1.4 var(--body); letter-spacing: .12em; text-transform: uppercase; color: var(--text-3); }
.ct-card .ct-v { margin: 0; font: 600 19px/1.3 var(--body); text-transform: none; letter-spacing: 0; color: var(--text); overflow-wrap: anywhere; }
.ct-card span:last-child:not(.ct-v) { color: var(--text-3); font-size: 13px; }
.ct-soc .cc-social { margin-top: 8px; }
.ct-quick { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
@media (max-width: 1000px) { .ct-quick { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 520px) { .ct-quick { grid-template-columns: minmax(0, 1fr); } }
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

PAGES = {'contact': contact, 'book-1-on-1-session': book, 'bike-fitting': bikefit, 'testing': testing, 'about2': about2, 'club-talk': clubtalk, 'talent-scout': talent, 'coaching-vision': vision}
if __name__ == '__main__':
    for n in (sys.argv[1:] or PAGES):
        PAGES[n]()
