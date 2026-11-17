"""Vivify Sports (vivifysports.com) redesign preview, for the move from Wix to WordPress.

Matteo 16 Nov 2026: "remake this site using my own style of fonts but using their logos and colours".
- Fonts and layout system from BRAND.md (Anton capitals for headlines, Montserrat for everything else, eyebrow ->
  heading -> short bar, panels, 8px buttons, "nothing touching" spacing).
- Colours and logo are Vivify's own, taken from the live site: teal #19444B, deep teal #0C2226, aqua #B1D8DD,
  lime #80A315 (About page accents), white V logo on the teal square.
- Copy, titles, meta descriptions, H1/H2 wording, alt text: from the live site (vivify/baseline-2026-11-16.json,
  vivify/text/). Deviations are listed in vivify/SEO-NOTES.md.

  python3 -I tools/build_vivify.py      -> vivify/site/*.html (+ vivify/site/img/)
"""
import os, re, sys, json, html, shutil, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
V = ROOT + 'vivify/'
OUT = V + 'site/'
os.makedirs(OUT + 'img', exist_ok=True)
BASE = {r['url'].rstrip('/'): r for r in json.load(open(V + 'baseline-2026-11-16.json'))}
LIVE = 'https://www.vivifysports.com'
e = html.escape

# ---------------------------------------------------------------- images
def img(prefix, alt, cls='', lazy=True, w=None, h=None, style=''):
    src = glob.glob(V + 'webp/' + prefix + '*.webp')
    assert src, prefix
    name = os.path.basename(src[0])
    dst = OUT + 'img/' + name
    if not os.path.exists(dst):
        shutil.copy(src[0], dst)
    if w is None:
        from PIL import Image
        w, h = Image.open(src[0]).size
    return (f'<img src="img/{name}" alt="{e(alt)}" width="{w}" height="{h}"'
            + (f' class="{cls}"' if cls else '') + (f' style="{style}"' if style else '')
            + (' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"') + '>')

LOGO = '0e1488-f038fcb12444476fab18be6dc4bf'      # 909x855 teal square, white V + VIVIFY SPORTS
LOGO_ALT = 'vivify sports logo '                    # live alt, kept

# ---------------------------------------------------------------- pages / nav
PAGES = {  # file -> live path
    'index.html': '', 'about.html': '/about', 'nutrition-nutrition-philosophy.html': '/nutrition-nutrition-philosophy',
    'sports-nutritionist-ireland.html': '/sports-nutritionist-ireland', 'workshops.html': '/workshops',
    'recipies.html': '/recipies', 'blog.html': '/blog', 'contact.html': '/contact',
    'massage-therapy.html': '/massage-therapy', 'yoga.html': '/yoga', 'privacy-policy.html': '/privacy-policy',
    'free-sports-nutrition-consultation.html': '/free-sports-nutrition-consultation',
    'post-carbohydrate-fueling-endurance-sports.html': '/post/carbohydrate-fueling-endurance-sports',
}
# New SEO pages (16 Nov 2026, not on the live site): file -> (path, Yoast title, meta description). Copy in vivify_seo_pages.py.
NEW = {
    'cycling-nutritionist.html': ('/cycling-nutritionist', 'Cycling Nutritionist Ireland & Online | Vivify Sports',
        'Cycling nutrition coaching from Marine Lenehan, MSc sports nutritionist and LIDL-TREK WorldTour rider. Road, gravel and sportive fuelling, Ireland and online.'),
    'race-fuelling-plan.html': ('/race-fuelling-plan', 'Race Fuelling Plan for Cyclists & Triathletes | Vivify Sports',
        'A personal race fuelling plan for your event: carbs per hour, hydration and gut training, built by a WorldTour cyclist and MSc sports nutritionist.'),
    'triathlon-nutritionist.html': ('/triathlon-nutritionist', 'Triathlon Nutritionist | Ironman & 70.3 Nutrition | Vivify Sports',
        'Triathlon nutrition coaching for Ironman, 70.3 and sprint athletes: daily fuelling for swim, bike and run training and a race-day plan. Online, from Ireland.'),
    'online-sports-nutritionist.html': ('/online-sports-nutritionist', 'Online Sports Nutritionist for Endurance Athletes | Vivify Sports',
        'Work with an MSc sports nutritionist from anywhere. Online nutrition coaching for cyclists, triathletes and runners, with plans priced in euro and US dollars.'),
    'sports-nutritionist-dublin.html': ('/sports-nutritionist-dublin', 'Sports Nutritionist Dublin & Wicklow | Vivify Sports',
        'Sports nutritionist for athletes in Dublin and Wicklow: online nutrition coaching, club workshops and sports massage on call in Co. Wicklow and Co. Dublin.'),
    'womens-cycling-nutrition.html': ('/womens-cycling-nutrition', "Women's Cycling Nutrition | Nutritionist for Female Cyclists | Vivify Sports",
        "Nutrition coaching for women who ride, from a female WorldTour cyclist and MSc sports nutritionist: energy, iron, fuelling and recovery for female athletes."),
    'faq.html': ('/faq', 'Sports Nutrition FAQ | Vivify Sports',
        'Answers to common questions about sports nutrition coaching with Vivify Sports: online consultations, plans, fuelling, carbs per hour and working together.'),
    'testimonials.html': ('/testimonials', 'Client Reviews | Sports Nutrition Coaching | Vivify Sports',
        'What cyclists and triathletes say about sports nutrition coaching with Marine Lenehan at Vivify Sports: more energy, better fuelling and race PBs.'),
}
PAGES.update({f: v[0] for f, v in NEW.items()})
NAV = [('index.html', 'Home'), ('about.html', 'About'), ('nutrition-nutrition-philosophy.html', 'Sports Nutrition Philosophy'),
       ('sports-nutritionist-ireland.html', 'Sports Nutrition Coaching'), ('workshops.html', 'Workshops'),
       ('recipies.html', 'E-Book'), ('blog.html', 'Blog'), ('contact.html', 'Contact')]
DISCOVERY = 'https://cal.com/marine-lenehan/discovery-call'   # Marine 17 Nov: Cal.com replaces Wix Bookings
BOOK_CAL = DISCOVERY
MASSAGE_BOOK = 'http://VEV.CO/MASSAGE-THERAPIST-VIVIFY-SPORTS-IE'
PAY = {'healthy': 'https://pay.gocardless.com/BRT0004V6AWJMPG', 'happy': 'https://pay.gocardless.com/BRT00045M0TDENA',
       'performing': 'https://pay.gocardless.com/BRT00045M0SDGT2', 'yoga_monthly': 'https://pay.gocardless.com/BRT0002A1NBMZ4S'}
EMAIL, PHONE, PHONE_TEL = 'marine@vivifysports.com', '+353 87 224 7402', '+353872247402'
IG = 'https://www.instagram.com/vivifysports/'
GBP = 'https://share.google/d4C3iwnzpSU1VDUqt'   # Marine's Google Business Profile (reviews), 17 Nov

ICON = {
 'ig': '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.3" fill="currentColor"/></svg>',
 'mail': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 7l9 6 9-6" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
 'phone': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M6.6 10.8a15 15 0 006.6 6.6l2.2-2.2a1 1 0 011-.25 11.4 11.4 0 003.6.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.25.2 2.45.57 3.6a1 1 0 01-.25 1z" fill="currentColor"/></svg>',
 'pin': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 2a7 7 0 00-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 00-7-7zm0 9.5A2.5 2.5 0 1112 6a2.5 2.5 0 010 5.5z" fill="currentColor"/></svg>',
 'check': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 'star': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 2.8l2.8 5.9 6.4.8-4.7 4.4 1.2 6.4L12 17.2l-5.7 3.1 1.2-6.4-4.7-4.4 6.4-.8z" fill="currentColor"/></svg>',
 'quote': '<svg viewBox="0 0 32 24" width="30" height="22" aria-hidden="true"><path d="M0 24V14C0 6 4 1.5 12 0l1.5 3C9 4.5 7 7.5 7 11h6v13zm18 0V14c0-8 4-12.5 12-14l1.5 3C27 4.5 25 7.5 25 11h6v13z" fill="currentColor"/></svg>',
 'clock': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
 'arrow': '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 'talk': '<svg viewBox="0 0 48 48" width="40" height="40" aria-hidden="true"><rect x="6" y="8" width="36" height="22" rx="4" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M14 30l-4 10 12-10" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><path d="M14 17h20M14 22h12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>',
}

# ---------------------------------------------------------------- CSS
CSS = r"""
:root{
 --bg:#0C2226;--bg-2:#0f2b30;--teal:#19444B;--panel:rgba(25,68,75,.42);--panel-solid:#123338;
 --border:rgba(177,216,221,.12);--border-strong:rgba(177,216,221,.26);
 --text:#f4f8f8;--text-2:#d2e1e3;--text-3:#8fb0b4;
 --aqua:#B1D8DD;--aqua-hover:#c9e6ea;--on-aqua:#0C2226;--lime:#80A315;--lime-text:#9cc21f;
 --wrap:1200px;--r:12px;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:radial-gradient(1200px 600px at 85% -10%,rgba(177,216,221,.07),transparent 60%),radial-gradient(900px 500px at -10% 40%,rgba(128,163,21,.05),transparent 60%),var(--bg);
 color:var(--text-2);font:15px/1.7 Montserrat,system-ui,sans-serif;overflow-x:hidden}
img{max-width:100%;height:auto;display:block}
a{color:var(--aqua)}
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible{outline:2px solid var(--aqua);outline-offset:3px}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 24px}
.h1,.h2,.h3,h1,h2,h3{font-family:Anton,Impact,sans-serif;font-weight:400;text-transform:uppercase;color:var(--text);letter-spacing:.01em;line-height:1.08;margin:0}
h1,.h1{font-size:clamp(40px,6.4vw,76px)}
h2,.h2{font-size:clamp(30px,4vw,48px)}
h3,.h3{font-size:22px;line-height:1.2}
p{margin:0 0 16px}
.eyebrow{display:block;font:600 12px/1.4 Montserrat,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:var(--lime-text);margin:0 0 12px}
.bar{display:block;width:40px;height:3px;background:var(--aqua);border-radius:2px;margin:16px 0 18px}
.center{text-align:center}.center .bar{margin-left:auto;margin-right:auto}
.lead{font-size:16px;color:var(--text-2);max-width:760px}
.center .lead{margin-left:auto;margin-right:auto}
.muted{color:var(--text-3)}
section{padding:88px 0}
.section-tight{padding:56px 0}
.btn{display:inline-flex;align-items:center;gap:10px;font:600 14px/1 Montserrat,sans-serif;letter-spacing:.04em;text-transform:uppercase;text-decoration:none;
 padding:16px 24px;border-radius:8px;border:1px solid transparent;transition:background .2s,border-color .2s,transform .2s;cursor:pointer;text-align:center}
.btn-primary{background:var(--aqua);color:var(--on-aqua)}
.btn-primary:hover{background:var(--aqua-hover);transform:translateY(-1px)}
.btn-secondary{background:rgba(12,34,38,.6);color:var(--text);border-color:var(--border-strong)}
.btn-secondary:hover{border-color:var(--aqua);color:var(--aqua)}
.panel{background:var(--panel);border:1px solid var(--border);border-radius:var(--r)}
.chips{display:flex;flex-wrap:wrap;gap:10px;padding:0;margin:0;list-style:none}
.chips li{border:1px solid var(--border-strong);border-radius:999px;padding:9px 16px;font-size:13.5px;color:var(--text);background:rgba(12,34,38,.5);display:flex;align-items:center;gap:8px}
.chips li::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--lime);flex:none}
.ticks{list-style:none;padding:0;margin:0}
.ticks li{display:flex;gap:12px;align-items:flex-start;padding:7px 0}
.ticks li svg{color:var(--aqua);flex:none;margin-top:4px}
.pill{display:inline-flex;align-items:center;gap:8px;background:rgba(12,34,38,.72);border:1px solid var(--border-strong);color:#fff;border-radius:999px;
 padding:8px 14px;font:600 12px/1 Montserrat,sans-serif;letter-spacing:.16em;text-transform:uppercase;margin-bottom:18px;backdrop-filter:blur(6px)}
.pill::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--lime)}

/* header */
.skip{position:absolute;left:-9999px}.skip:focus{left:16px;top:16px;z-index:100;background:var(--aqua);color:var(--on-aqua);padding:10px 14px;border-radius:8px}
header.site{position:sticky;top:0;z-index:50;background:rgba(12,34,38,.86);backdrop-filter:blur(12px);border-bottom:1px solid var(--border)}
header.site .wrap{display:flex;align-items:center;gap:24px;height:82px;max-width:1360px}
.logo img{width:58px;height:58px;object-fit:cover}
nav.main{margin-left:auto}
nav.main ul{display:flex;gap:4px;list-style:none;margin:0;padding:0}
nav.main a{display:block;color:var(--text);text-decoration:none;font:600 13px/1 Montserrat,sans-serif;padding:12px 10px;position:relative;white-space:nowrap}
nav.main a::after{content:"";position:absolute;left:10px;right:10px;bottom:4px;height:2px;background:transparent;transition:background .2s}
nav.main a:hover{color:var(--aqua)}nav.main a:hover::after{background:var(--aqua)}
nav.main a[aria-current=page]::after{background:var(--lime)}
.hdr-cta{padding:13px 18px;font-size:13px}
.burger{display:none}
#menu-t{position:absolute;opacity:0;pointer-events:none}
@media (max-width:1240px){
 .burger{display:flex;margin-left:auto;width:46px;height:46px;border:1px solid var(--border-strong);border-radius:8px;align-items:center;justify-content:center;cursor:pointer;color:var(--text)}
 nav.main{position:fixed;inset:82px 0 auto 0;background:var(--bg);border-bottom:1px solid var(--border);display:none;margin:0;max-height:calc(100vh - 82px);overflow:auto}
 #menu-t:checked~nav.main{display:block}
 nav.main ul{flex-direction:column;padding:12px 24px 24px}
 nav.main a{font-size:16px;padding:16px 0;border-bottom:1px solid var(--border)}
 nav.main a::after{left:0;right:auto;width:28px;bottom:10px}
 .hdr-cta{display:none}
}

/* hero */
.hero{position:relative;min-height:min(86vh,760px);display:flex;align-items:flex-end;padding:0;overflow:hidden}
.hero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:60% 62%}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(12,34,38,.15) 0%,rgba(12,34,38,.35) 45%,rgba(12,34,38,.94) 100%),linear-gradient(90deg,rgba(12,34,38,.75),rgba(12,34,38,0) 65%)}
.hero .wrap{position:relative;z-index:1;padding-top:120px;padding-bottom:72px;width:100%}
.hero h1{max-width:820px;margin-bottom:10px}
.hero .lead{color:#e6f0f1;margin:16px 0 28px}
.page-hero{padding:96px 0 56px;text-align:center}
.page-hero .lead{margin:0 auto}
.page-hero .btn{margin-top:26px}

/* grids */
.g2{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
@media (max-width:980px){.g2{grid-template-columns:1fr;gap:36px}.g3{grid-template-columns:1fr 1fr}.g4{grid-template-columns:1fr 1fr}}
@media (max-width:640px){.g3,.g4{grid-template-columns:1fr}section{padding:64px 0}.page-hero{padding:72px 0 40px}}

/* home intro band */
.intro{display:grid;grid-template-columns:1fr 1.1fr 1fr;gap:24px;align-items:stretch;margin-top:-1px}
.intro>div{padding:36px 32px}
.intro .feature{background:linear-gradient(160deg,var(--teal),#0f2f34);border:1px solid var(--border-strong);border-radius:var(--r);text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center}
.intro .feature h2{font-size:clamp(40px,5vw,60px);letter-spacing:.08em}
.intro h3{font:600 12px/1.4 Montserrat,sans-serif;letter-spacing:.18em;color:var(--lime-text);margin-bottom:14px}
@media (max-width:980px){.intro{grid-template-columns:1fr}}

/* testimonials */
.tgrid{columns:3 300px;column-gap:24px}
.tcard{break-inside:avoid;margin:0 0 24px;padding:28px;position:relative}
.tcard .who{display:flex;gap:14px;align-items:center;margin-bottom:16px}
.tcard .who img{width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid var(--border-strong)}
.tcard h2,.tcard .name{font:700 15px/1.3 Montserrat,sans-serif;text-transform:none;color:var(--text);letter-spacing:0}
.tcard .sport{display:block;margin-top:3px;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--lime-text);font-weight:600}
.tcard blockquote{margin:0;color:var(--text-2);font-size:14.5px}
.tcard .q{position:absolute;right:22px;top:24px;color:rgba(177,216,221,.22)}

/* service cards */
.scard{display:flex;flex-direction:column;overflow:hidden;text-decoration:none;color:inherit;transition:border-color .2s,transform .2s}
.scard:hover{border-color:var(--aqua);transform:translateY(-3px)}
.scard .ph{aspect-ratio:4/3;overflow:hidden;background:var(--teal);display:flex;align-items:center;justify-content:center;color:var(--aqua)}
.scard .ph img{width:100%;height:100%;object-fit:cover}
.scard .tx{padding:20px 22px 24px}
.scard .h3{display:block;margin-bottom:8px}
.scard .go{display:inline-flex;gap:8px;align-items:center;color:var(--aqua);font:600 13px Montserrat,sans-serif;text-transform:uppercase;letter-spacing:.06em}

/* CTA band */
.cta{padding:56px 48px;display:grid;grid-template-columns:1.4fr auto;gap:32px;align-items:center;background:linear-gradient(120deg,var(--teal),#0f2f34);border:1px solid var(--border-strong);border-radius:16px}
.cta .h2{font-size:clamp(28px,3.4vw,42px)}
@media (max-width:820px){.cta{grid-template-columns:1fr;padding:40px 28px}}

/* about */
.portrait{border-radius:var(--r);overflow:hidden;border:1px solid var(--border-strong);box-shadow:0 30px 80px rgba(0,0,0,.35)}
.titles{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;list-style:none;padding:0;margin:20px 0}
.titles li{display:flex;gap:12px;align-items:center;padding:14px 16px;color:var(--text);font-weight:500}
.titles li svg{color:var(--lime-text);flex:none}
.titles a{color:var(--text);text-decoration-color:var(--lime)}
@media (max-width:640px){.titles{grid-template-columns:1fr}}
.prose{max-width:780px}
.prose h3{margin:36px 0 14px}
.num{font:400 54px/1 Anton,sans-serif;color:var(--aqua);opacity:.9}
.pcard{padding:30px 28px}
.pcard .h3{display:block;margin:14px 0 12px;font-size:21px}
.bigquote{font:400 clamp(30px,4.4vw,56px)/1.1 Anton,sans-serif;text-transform:uppercase;color:var(--text);max-width:900px;margin:0 auto}
.bigquote span{color:var(--aqua)}

/* coaching */
.tbl-wrap{overflow-x:auto;border-radius:var(--r);border:1px solid var(--border-strong);-webkit-overflow-scrolling:touch}
table.cmp{border-collapse:collapse;width:100%;min-width:860px;font-size:14px}
.cmp th,.cmp td{padding:14px 12px;border-bottom:1px solid var(--border);text-align:center}
.cmp thead th{background:var(--teal);color:var(--text);font:400 17px/1.15 Anton,sans-serif;text-transform:uppercase;letter-spacing:.02em}
.cmp tbody th{text-align:left;color:var(--text);font-weight:600;background:#14363b;position:sticky;left:0;z-index:1;min-width:170px}
.cmp thead th:first-child{position:sticky;left:0;z-index:2}
.cmp tbody th small{display:block;font-weight:400;color:var(--text-3);font-size:12px}
.cmp td{color:var(--text-2)}
.cmp td svg{color:var(--lime-text);margin:auto}
.cmp .dash{color:var(--text-3)}
.cmp tr.price td{font-weight:700;color:var(--text);background:rgba(177,216,221,.06)}
.cmp tr.price small{display:block;font-weight:500;color:var(--text-3)}
.plans{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:22px}
.plans.two{grid-template-columns:repeat(2,1fr)}
@media (max-width:980px){.plans,.plans.two{grid-template-columns:1fr}}
.plan{padding:30px 28px;display:flex;flex-direction:column}
.plan.feat{border-color:var(--aqua);background:linear-gradient(170deg,rgba(25,68,75,.75),rgba(18,51,56,.6));position:relative}
.plan.soldout{position:relative;opacity:.85}
.plan.soldout::before{content:"Sold out for now";position:absolute;top:-12px;left:28px;background:#2a4a50;color:var(--text);font:700 11px/1 Montserrat,sans-serif;letter-spacing:.14em;text-transform:uppercase;padding:7px 10px;border-radius:999px;border:1px solid var(--border-strong)}
.plan.feat::before{content:"Most popular";position:absolute;top:-12px;left:28px;background:var(--lime);color:#0C2226;font:700 11px/1 Montserrat,sans-serif;letter-spacing:.14em;text-transform:uppercase;padding:7px 10px;border-radius:999px}
.plan h2{font-size:26px;line-height:1.12}
.plan h2 .price{display:block;font:700 15px/1.4 Montserrat,sans-serif;color:var(--aqua);text-transform:none;letter-spacing:0;margin-top:10px}
.plan .dur{display:block;font-family:Montserrat,sans-serif;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--lime-text);font-weight:600;margin:12px 0 6px}
.plan .inc{font-weight:700;color:var(--text);margin:8px 0 4px}
.plan .ticks{margin-bottom:22px}
.plan .btn{margin-top:auto;align-self:flex-start}
.partners{display:flex;flex-wrap:wrap;gap:18px;justify-content:center;align-items:center}
.partners a,.partners span{display:flex;align-items:center;justify-content:center;background:#fff;border-radius:10px;padding:12px;width:150px;height:96px}
.partners img{max-height:72px;width:auto;object-fit:contain}

/* massage rows */
.mrow{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--border);border-radius:var(--r);overflow:hidden;margin-bottom:28px;background:var(--panel)}
.mrow .ph{min-height:420px}.mrow .ph img{width:100%;height:100%;object-fit:cover}
.mrow .tx{padding:44px 44px 40px}
.mrow.rev .ph{order:2}
.mrow h2{font-size:clamp(28px,3vw,38px);margin-bottom:6px}
.mrow h4{font:600 12px/1.4 Montserrat,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--lime-text);margin:22px 0 8px}
.mrow .mq{margin-top:22px;padding-left:16px;border-left:3px solid var(--aqua);color:var(--text);font-style:italic}
.mrow ul{margin:0;padding-left:20px}
@media (max-width:900px){.mrow{grid-template-columns:1fr}.mrow.rev .ph{order:0}.mrow .ph{min-height:260px}.mrow .tx{padding:30px 24px}}
.facts{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:28px 0}
.facts>div{padding:20px}
.facts b{display:block;color:var(--text);font-size:13px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:4px}
@media (max-width:760px){.facts{grid-template-columns:1fr}}

/* blog */
.bgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
@media (max-width:980px){.bgrid{grid-template-columns:1fr 1fr}}
@media (max-width:640px){.bgrid{grid-template-columns:1fr}}
.bcard{display:flex;flex-direction:column;overflow:hidden;text-decoration:none;color:inherit;transition:border-color .2s,transform .2s}
.bcard:hover{border-color:var(--aqua);transform:translateY(-3px)}
.bcard .ph{aspect-ratio:16/10;overflow:hidden;background:var(--teal)}
.bcard .ph img{width:100%;height:100%;object-fit:cover}
.bcard .tx{padding:20px 22px 24px;display:flex;flex-direction:column;flex:1}
.bcard h2{font-size:21px;line-height:1.18;margin-bottom:10px}
.bcard p{font-size:14px;color:var(--text-2);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.bcard .meta{margin-top:auto;font-size:12px;color:var(--text-3);letter-spacing:.06em;text-transform:uppercase;display:flex;gap:14px}
.filters{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:0 0 36px}
.filters button{font:600 13px Montserrat,sans-serif;color:var(--text);background:rgba(12,34,38,.6);border:1px solid var(--border-strong);border-radius:999px;padding:10px 16px;cursor:pointer}
.filters button[aria-pressed=true]{background:var(--aqua);color:var(--on-aqua);border-color:var(--aqua)}

/* article */
.article{max-width:760px;margin:0 auto}
.article h1{font-size:clamp(34px,5vw,58px)}
.article .byline{display:flex;align-items:center;gap:12px;color:var(--text-3);font-size:13px;margin:18px 0 28px}
.article .byline img{width:44px;height:44px;border-radius:50%;object-fit:cover}
.article .byline b{color:var(--text)}
.article h2{font-size:clamp(26px,3vw,34px);margin:44px 0 14px}
.article h3{margin:28px 0 10px;font-size:20px}
.article p,.article li{font-size:16px;line-height:1.8;color:var(--text-2)}
.article figure{margin:32px 0}
.article figure img{border-radius:var(--r);width:100%}
.article .callout{padding:18px 22px;margin:20px 0;font:700 17px/1.5 Montserrat,sans-serif;color:var(--text);border-left:3px solid var(--lime)}
.article table{width:100%;border-collapse:collapse;margin:20px 0;font-size:15px}
.article th,.article td{border:1px solid var(--border-strong);padding:12px;text-align:left}
.article th{background:var(--teal);color:var(--text)}
.article .tbl-wrap table{min-width:520px;margin:0}
.article .tbl-wrap{margin:20px 0}
.author{display:flex;gap:20px;align-items:center;padding:26px;margin-top:48px}
.author img{width:84px;height:84px;border-radius:50%;object-fit:cover;flex:none}
@media (max-width:560px){.author{flex-direction:column;align-items:flex-start}}

/* forms */
.form{display:grid;gap:16px}
.form label{display:block;font:600 12px Montserrat,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--text-3);margin-bottom:8px}
.form input,.form textarea,.form select{width:100%;font:16px Montserrat,sans-serif;color:var(--text);background:rgba(12,34,38,.75);border:1px solid var(--border-strong);border-radius:8px;padding:14px 14px}
.form textarea{min-height:140px;resize:vertical}
.form .two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:560px){.form .two{grid-template-columns:1fr}}
.cinfo{list-style:none;padding:0;margin:0}
.cinfo li{display:flex;gap:14px;align-items:center;padding:14px 0;border-bottom:1px solid var(--border)}
.cinfo svg{color:var(--aqua);flex:none}
.cinfo a{color:var(--text);text-decoration:none}

/* faq */
.qa{margin-bottom:12px;padding:0}
.qa summary{cursor:pointer;list-style:none;padding:20px 56px 20px 24px;font:700 16px/1.4 Montserrat,sans-serif;color:var(--text);position:relative}
.qa summary::-webkit-details-marker{display:none}
.qa summary::after{content:"+";position:absolute;right:22px;top:50%;transform:translateY(-50%);font:400 26px/1 Montserrat,sans-serif;color:var(--aqua)}
.qa[open] summary::after{content:"–"}
.qa>div{padding:0 24px 8px;color:var(--text-2)}
/* footer */
footer.site{margin-top:40px;background:linear-gradient(180deg,rgba(25,68,75,.35),rgba(25,68,75,.7));border-top:1px solid var(--border)}
footer.site .top{display:grid;grid-template-columns:1.4fr 1fr 1fr 1.1fr;gap:40px;padding:64px 24px 40px}
footer.site .logo img{width:76px;height:76px}
footer.site .tag{font:400 24px/1.1 Anton,sans-serif;text-transform:uppercase;color:var(--text);margin:20px 0 0;max-width:300px}
footer.site .fh{font:600 12px/1.4 Montserrat,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:var(--lime-text);margin:6px 0 14px}
footer.site ul{list-style:none;margin:0;padding:0}
footer.site li a{display:inline-block;color:var(--text-2);text-decoration:none;padding:6px 0;font-size:14px}
footer.site li a:hover{color:var(--aqua)}
footer.site .social{display:inline-flex;width:42px;height:42px;border-radius:50%;border:1px solid var(--border-strong);align-items:center;justify-content:center;color:var(--text);margin-top:10px}
footer.site .social:hover{color:var(--aqua);border-color:var(--aqua)}
footer.site .bottom{border-top:1px solid var(--border);padding:22px 24px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:13px;color:var(--text-3)}
footer.site .bottom a{color:var(--text-3)}
@media (max-width:980px){footer.site .top{grid-template-columns:1fr 1fr}}
@media (max-width:560px){footer.site .top{grid-template-columns:1fr}}
"""

# ---------------------------------------------------------------- shell
TYPOS = [('BREAKFATS', 'BREAKFASTS'), ('ASSESEMENT', 'ASSESSMENT'), ('REQUIMENTS', 'REQUIREMENTS'), ('VIFIFY', 'VIVIFY'),
         ('PERFORMACE', 'PERFORMANCE'), ('STRENGHTENING', 'STRENGTHENING'), ('to loose ', 'to lose '), ('loose or gain', 'lose or gain'),
         ('every pallet', 'every palate'), ('Nutriton', 'Nutrition'), ('MSs Sports', 'MSc Sports'), ('Masssage Theraphy', 'Massage Therapy'),
         ('NOT LOOSING', 'NOT LOSING'), ('Matteo Cigala,Italy', 'Matteo Cigala, Italy'), ('Damian Maloney,Ireland', 'Damian Maloney, Ireland')]

def fix_typos(s):
    for a, b in TYPOS:
        s = s.replace(a, b)
    return s

def shell(file, body, schema=None):
    path = PAGES[file]
    if file in NEW:
        b = {'title': NEW[file][1], 'meta_description': NEW[file][2]}
    else:
        b = BASE[LIVE + path] if (LIVE + path) in BASE else BASE[LIVE]
    title, desc = b['title'], b.get('meta_description') or ''
    navh = ''.join(f'<li><a href="{f}"' + (' aria-current="page"' if f == file else '') + f'>{t}</a></li>' for f, t in NAV)
    ld = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>' if schema else ''
    return fix_typos(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{LIVE}{path}">
<meta property="og:title" content="{e(b.get('og_title') or title)}">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="img/{os.path.basename(glob.glob(V+'webp/'+LOGO+'*')[0])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="vivify.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to Main Content</a>
<header class="site"><div class="wrap">
 <a class="logo" href="index.html" aria-label="Vivify Sports home">{img(LOGO, LOGO_ALT, lazy=False, w=58, h=55)}</a>
 <input type="checkbox" id="menu-t" aria-label="Menu">
 <label class="burger" for="menu-t" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></label>
 <nav class="main" aria-label="Main"><ul>{navh}</ul></nav>
 <a class="btn btn-primary hdr-cta" href="{DISCOVERY}">Free Discovery Call</a>
</div></header>
<main id="main">
{body}
</main>
<footer class="site">
 <div class="wrap top">
  <div><a class="logo" href="index.html">{img(LOGO, LOGO_ALT, w=76, h=72)}</a>
   <p class="tag">Healthy habits to ignite your potential</p></div>
  <div><p class="fh">Explore</p><ul>
   <li><a href="about.html">About Marine</a></li><li><a href="nutrition-nutrition-philosophy.html">Sports Nutrition Philosophy</a></li>
   <li><a href="blog.html">Blog</a></li><li><a href="recipies.html">E-Book</a></li><li><a href="testimonials.html">Client Reviews</a></li>
   <li><a href="faq.html">FAQ</a></li><li><a href="contact.html">Contact</a></li></ul></div>
  <div><p class="fh">Services</p><ul>
   <li><a href="sports-nutritionist-ireland.html">Sports Nutrition Coaching</a></li><li><a href="free-sports-nutrition-consultation.html">Free Discovery Call</a></li>
   <li><a href="workshops.html">Workshops &amp; Talks</a></li><li><a href="massage-therapy.html">Massage Therapy</a></li><li><a href="yoga.html">Online Yoga</a></li></ul>
   <p class="fh" style="margin-top:22px">Who I help</p><ul>
   <li><a href="cycling-nutritionist.html">Cycling Nutritionist</a></li><li><a href="triathlon-nutritionist.html">Triathlon Nutritionist</a></li>
   <li><a href="womens-cycling-nutrition.html">Women's Cycling Nutrition</a></li><li><a href="race-fuelling-plan.html">Race Fuelling Plan</a></li><li><a href="online-sports-nutritionist.html">Online, Worldwide</a></li>
   <li><a href="sports-nutritionist-dublin.html">Dublin &amp; Wicklow</a></li></ul></div>
  <div><p class="fh">Get in touch</p><ul class="cinfo">
   <li>{ICON['mail']}<a href="mailto:{EMAIL}">{EMAIL}</a></li>
   <li>{ICON['phone']}<a href="tel:{PHONE_TEL}">{PHONE}</a></li>
   <li>{ICON['pin']}<span>Wicklow, Ireland</span></li>
   <li>{ICON['star']}<a href="{GBP}" target="_blank" rel="noopener">Google reviews</a></li></ul>
   <a class="social" href="{IG}" aria-label="Vivify Sports on Instagram">{ICON['ig']}</a></div>
 </div>
 <div class="wrap bottom"><span>© 2023 by Vivify Sports</span><a href="privacy-policy.html">Privacy Policy</a></div>
</footer>
</body></html>""")

def head(eyebrow, title, tag='h2', lead=None, center=False, cls=''):
    h = f'<{tag}{" class=%s" % chr(34)+cls+chr(34) if cls else ""}>{title}</{tag}>' if tag else f'<div class="h2">{title}</div>'
    return (f'<div class="{"center" if center else ""}">' + (f'<span class="eyebrow">{eyebrow}</span>' if eyebrow else '') + h
            + '<span class="bar"></span>' + (f'<p class="lead">{lead}</p>' if lead else '') + '</div>')

def ticks(items):
    return '<ul class="ticks">' + ''.join(f'<li>{ICON["check"]}<span>{i}</span></li>' for i in items) + '</ul>'

def chips(items):
    return '<ul class="chips">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'

def cta(title, text, label, href, ext=False):
    t = ' target="_blank" rel="noopener"' if ext else ''
    return f"""<section class="section-tight"><div class="wrap"><div class="cta">
 <div><span class="eyebrow">Vivify Sports</span><div class="h2">{title}</div><span class="bar"></span><p class="lead" style="margin:0">{text}</p></div>
 <div><a class="btn btn-primary" href="{href}"{t}>{label} {ICON['arrow']}</a></div></div></div></section>"""

# ---------------------------------------------------------------- testimonials (live copy, live alt)
T = [
 ('0e1488-12e7dafd294d4fb1bdd2c91ef3e8', 'Francesco Pippa, Italy, gravel cyclist, Vivify Sports client', 'Francesco Pippa, Italy', 'Gravel Cyclist',
  "Thank you Marine for everything we have done together so far. It was a very difficult and tiring journey, but I must say that with your approach you taught me what it means to EAT and have good habits. Now the long-awaited month has arrived, the month where I will face my ultra endurance gravel race. Thanks to your help I'm sure it will go as I expect."),
 ('0e1488-b61442552ce945e3a69078a5b0bd', 'Sean Goggin, Ireland, road cyclist, Vivify Sports client', 'Sean Goggin, Ireland', 'Road Cyclist',
  "Working with Marine has enhanced my understanding and approach to the type of foods I should be consuming to maximize my performance on the bike. Her personalized plan and support helped me reach my goals and make better food choices. I feel more confident and healthier overall and I would highly recommend working with Marine."),
 ('0e1488-dd9b8d0527804135a7702494e568', 'Eleonore Vaillon, France, leisure cyclist, Vivify Sports client', 'Eleonore Vaillon, France', 'Leisure Cyclist',
  "I had gotten in touch with Marine to loose a few kilos. I lost 6 kgs in 4 months. She not only made my goal possible but she also increased my energy levels and my general well-being. A very professional nutritionist for sure!"),
 ('0e1488-9726c9f5f34c4bc0a075d5cb639e', 'Colum Traynor, Ireland, triathlete, Vivify Sports client', 'Colum Traynor, Ireland', 'Triathlete',
  "I would highly recommend Marine and the team in Vivify Sports. The nutrition advice I received for my 70.3 Ironman training & race day resulted in a 30 min PB & I never felt so good on the run leg. Don't waste money on expensive bike kit when you can shave 10 times more time with the right nutrition plan!"),
 ('0e1488-e2519416f668488c87b778c3f655', 'Matteo Cigala,Italy, road & gravel cyclist, Vivify Sports client', 'Matteo Cigala,Italy', 'Road & Gravel cyclist',
  "Working with Marine has helped me increase my endurance and my performance. She has taught me to optimise my nutrition and fuelling to bring out the best of me on the bike. Energy levels increased and no more cramping at the end of races. I think what makes working with Marine so special is that she really focuses on what works for you."),
 ('nsplsh-586757424e557349764f45', 'Iwan Harmsen, Netherlands, road cyclist, Vivify Sports client', 'Iwan Harmsen, Netherlands', 'Road cyclist',
  "Marine helped me understand in more detail my training needs in relation to food during and after my cycling. Further she provided my clear information on foods that would work for me individually. I'm very happy with the information she provided."),
 ('0e1488-2062d596f6f94b6dbae416691757', 'Damian Maloney, Ireland, road & leisure cyclist, Vivify Sports client', 'Damian Maloney, Ireland', 'Road & Leisure Cyclist',
  "My original goal was to shed a few lbs, but the focus shifted to adopting better eating habits and eating better quality food choices. I'm happy to recommend Marine to all who are looking to improve their diet and wellbeing!"),
 ('0e1488-bea1a60dd96d43b4af51cddfa40c', 'James Makin, Ireland, road & gravel cyclist, Vivify Sports client', 'James Makin, Ireland', 'Road & Gravel Cyclist',
  "I have been working with Marine since the end of last year in preparation for the Traka gravel race. I can honestly say I have learned so much about food and performance over this time and through her nutrition plan I have lost over 13 kg so far with an increase in power and fitness . Marine is very dedicated and a pleasure to deal with I look forward to what we can achieve in the future"),
]

def testimonials(h2_names=True, names=None):
    tag = 'h2' if h2_names else 'p'
    names = names or {}
    cards = ''.join(f"""<article class="tcard panel"><span class="q">{ICON['quote']}</span>
 <div class="who">{img(p, a, w=64, h=64)}<div><{tag} class="name">{e(names.get(n, n))} <span class="sport">{e(s)}</span></{tag}></div></div>
 <blockquote>{e(q)}</blockquote></article>""" for p, a, n, s, q in T)
    return f"""<section><div class="wrap">
 {head('Client stories', 'Athletes who fuel with Marine', tag=None, center=True)}
 <div class="tgrid" style="margin-top:36px">{cards}</div>
 <div class="center" style="margin-top:12px"><a class="btn btn-secondary" href="{GBP}" target="_blank" rel="noopener">{ICON['star']} Read our Google reviews</a></div></div></section>"""

# ---------------------------------------------------------------- HOME
def home():
    services = [
        ('massage-therapy.html', img('11062b-c7086e8444c14484a9e3ec96b46e', 'Deep Tissue Massage', w=640, h=427), 'Massage Therapy', 'Deep tissue, sports, cupping and Thai massage in Co. Wicklow & Dublin. Currently sold out.'),
        ('yoga.html', img('0e1488-a687b5ba8de7467fa18ece35f8a9', 'Yoga pose on a clifftop by the sea at sunset', w=640, h=424), 'Online Yoga', 'Yin, Vinyasa and yoga for cyclists.'),
        ('recipies.html', img('0e1488-8cee9e1e3ac743dd828b4bd69d89', 'Raspberry Chia Seed pudding', w=640, h=363), 'E-Book', 'Breakfasts to ignite your potential: 30 recipes.'),
        ('workshops.html', f'<span>{ICON["talk"]}</span>', 'Workshops & Talks', 'Nutrition talks for clubs, gyms and teams.'),
    ]
    who = [('cycling-nutritionist.html', 'Cyclists', 'Road, gravel and sportive riders'), ('triathlon-nutritionist.html', 'Triathletes', 'Ironman, 70.3 and shorter races'),
           ('race-fuelling-plan.html', 'Race day', 'A fuelling plan for your event'), ('online-sports-nutritionist.html', 'Worldwide', 'Online coaching, wherever you train')]
    WHO_I_HELP = ('<section style="padding-top:24px"><div class="wrap">' + head('Who Marine works with', 'Nutrition for endurance athletes', tag=None, center=True)
                  + '<div class="g4" style="margin-top:32px">' + ''.join(f'<a class="scard panel" href="{h}"><div class="tx"><span class="eyebrow">{e(d)}</span><span class="h3">{e(t)}</span><span class="go">Learn more {ICON["arrow"]}</span></div></a>' for h, t, d in who)
                  + '</div></div></section>')
    sc = ''.join(f'<a class="scard panel" href="{h}"><div class="ph">{im}</div><div class="tx"><span class="h3">{e(t)}</span><p class="muted">{e(d)}</p><span class="go">Learn more {ICON["arrow"]}</span></div></a>' for h, im, t, d in services)
    body = f"""
<section class="hero">
 {img('0e1488-70faaa082bbd4ad4b8d8f16a5bc3', 'Cyclist riding a lakeside road above a lake', lazy=False, w=1922, h=2560)}
 <div class="wrap">
  <span class="pill">Sports Nutritionist · Wicklow, Ireland</span>
  <h1>Healthy habits to ignite your potential</h1>
  <a class="btn btn-primary" href="{DISCOVERY}">Book your free nutrition discovery call {ICON['arrow']}</a>
 </div>
</section>
<section class="section-tight"><div class="wrap intro">
 <div class="panel"><h3>Sports Nutrition Coaching for Endurance Athletes</h3>
  <p>Personalised nutrition plans for triathletes, runners and cyclists. Fuel your training, improve recovery and perform at your best with evidence-based sports nutrition coaching.</p></div>
 <div class="feature"><span class="eyebrow">The Vivify Sports method</span><h2>Nutrition</h2><span class="bar"></span>
  <a class="btn btn-primary" href="nutrition-nutrition-philosophy.html">Learn more</a></div>
 <div class="panel"><h3>Why work with Vivify Sports?</h3>
  {ticks(['MSc-qualified Sports Nutritionist', 'Professional WorldTour cycling experience', 'Individualised nutrition plans', 'Online coaching worldwide', 'Practical, science-based advice'])}</div>
</div></section>
{testimonials()}
{WHO_I_HELP}
<section style="padding-top:24px"><div class="wrap">
 {head('More from Vivify Sports', 'Support for the whole athlete', tag=None, center=True)}
 <div class="g4" style="margin-top:32px">{sc}</div></div></section>
{cta('Ready to fuel smarter?', 'A free 30-minute discovery call with Marine to talk through your training, goals and nutrition.', 'Book your free call', DISCOVERY)}
"""
    schema = {"@context": "https://schema.org", "@type": "ProfessionalService", "name": "Vivify Sports", "url": LIVE,
              "email": EMAIL, "telephone": PHONE, "areaServed": "Worldwide", "address": {"@type": "PostalAddress", "addressLocality": "Wicklow", "addressCountry": "IE"},
              "founder": {"@type": "Person", "name": "Marine Lenehan", "jobTitle": "Sports Nutritionist"}, "sameAs": [IG, GBP]}
    return shell('index.html', body, schema)

# ---------------------------------------------------------------- ABOUT
def about():
    titles = ['Irish National Gravel Champion (2026)', 'Amateur Gravel World Champion (2024)', 'Amateur Gravel European Champion (2023,2024)',
              'Irish National E-Sport Champion (2024, 2025)', 'Irish National Criterium Champion (2024)',
              '<a href="https://www.stickybottle.com/races-results/irelands-lenehan-wins-gran-fondo-european-championships/" target="_blank" rel="noopener">European Gran Fondo Champion (2023)</a>',
              'Podium Elite Irish Road Nationals (2025)', 'Podium Elite Irish TT Nationals (2026)']
    quals = ['MSc in Sports Nutrition – Universidad Europea de Madrid (2025)', 'Professional Diploma in Sports Nutrition (2023)',
             'Master’s Degree in Massage Therapy (2021)', 'Bachelor of Arts (BA) in Wellness (2020)', '200-hour Yoga Alliance Teaching Certificate (2021)']
    princ = [('Evidence-based, individualised nutrition', 'Every athlete is different. Your nutrition plan should reflect your training load, performance goals, nutritional requirements and personal preferences.'),
             ('Fuel for performance, not restriction', 'Eating enough to support training is essential. I focus on appropriate energy and carbohydrate intake, adequate protein, hydration and recovery, without unnecessary food restrictions or extreme approaches.'),
             ('Sustainable habits and practical strategies', 'Nutrition should complement your life, not complicate it. I help athletes develop realistic habits and practical fueling strategies they can maintain throughout training, competition and everyday life.')]
    body = f"""
<section style="padding-top:72px"><div class="wrap g2">
 <div class="portrait">{img('0e1488-5ffa2e2730204ef0bae918a9e4ae', 'Marine Lenehan, MSc Sports Nutritionist and founder of Vivify Sports', lazy=False, w=1200, h=1200)}</div>
 <div><span class="eyebrow">About Vivify Sports</span>
  <h1>Meet Marine Lenehan <span style="display:block;color:var(--aqua);font-size:.56em;margin-top:14px;line-height:1.15">MSc Sports Nutritionist | WorldTour Professional Cyclist</span></h1>
  <span class="bar"></span>
  <p class="lead">Combining sports nutrition science with real-world experience at the highest level of professional cycling, I help endurance athletes fuel smarter, recover better and achieve their performance goals.</p>
  <a class="btn btn-primary" href="{DISCOVERY}" style="margin-top:10px">Book a free discovery call {ICON['arrow']}</a></div>
</div></section>
<section style="padding-top:24px"><div class="wrap prose">
 {head('Wicklow, Ireland · working worldwide', 'Sports Nutritionist | Helping Endurance Athletes Fuel for Performance')}
 <p>Hi, I'm Marine Lenehan, founder of Vivify Sports, a sports nutritionist based in Wicklow, Ireland, working with athletes worldwide.</p>
 <p>My passion for sports nutrition comes from two worlds that have shaped my life: <strong style="color:var(--text)">competitive sport and nutrition science.</strong></p>
 <p>As a professional WorldTour cyclist and a qualified sports nutritionist, I understand the demands of endurance training from both sides. I know what it takes to prepare for competition, manage demanding training schedules, fuel long sessions and prioritize recovery.</p>
 <p>My goal is to turn sports nutrition science into practical strategies that help athletes feel stronger, perform better and get more out of their training</p>
 <h3>From the Athletics Track to the WorldTour</h3>
 <p>As a longtime athlete, formerly a hurdler and now a professional cyclist, I understand firsthand what it takes to support both the body and the mind through training, racing, and recovery.</p>
 <p>In 2025, I signed with LIDL-TREK, marking the moment I officially stepped into the WorldTour as a professional rider. Competing at the highest level has strengthened both my experience and my philosophy as a nutritionist because the strategies I use to fuel myself for the WorldTour racing are the same evidence-based tools I bring to the athletes I support. I’m still proud to hold titles as:</p>
 <ul class="titles">{''.join(f'<li class="panel">{ICON["star"]}<span>{t}</span></li>' for t in titles)}</ul>
 <p>But more than medals, what drives me is helping others discover their own version of success through personalised coaching that balances both science and individuality.</p>
 <h3>Education &amp; Qualifications</h3>
 <p>I’ve spent years building a well-rounded foundation to support the athletes I coach. My qualifications include:</p>
 {ticks(quals)}
 <p style="margin-top:16px">These tools enable me to support the entire athlete, not just their diet, but also their movement, mindset, and recovery.</p>
</div></section>
<section style="padding-top:24px"><div class="wrap">
 <div class="prose">{head('My coaching philosophy', 'Elite-Level Experience, Practical Nutrition Coaching')}
 <p>As a professional WorldTour cyclist, I understand the physical demands of endurance sport first-hand. I know how important nutrition is in supporting demanding training schedules, improving recovery and preparing for competition. But good sports nutrition isn't just about what works in theory. It needs to work in real life.</p>
 <p>At Vivify Sports, I combine evidence-based nutrition with practical experience to create personalized strategies that fit your training, goals, lifestyle and individual needs.</p>
 <p>My coaching philosophy is built around three principles:</p></div>
 <div class="g3" style="margin-top:20px">{''.join(f'<div class="pcard panel"><span class="num">{i+1}.</span><span class="h3">{e(t)}</span><p style="margin:0">{e(d)}</p></div>' for i, (t, d) in enumerate(princ))}</div>
 <div class="prose" style="margin-top:32px">
 <p>Whether you're preparing for your first endurance event or competing at an advanced level, my goal is to give you the knowledge, confidence and nutritional support to perform at your best.</p>
 <p>My aim is to make nutrition easier to understand, easier to implement and more effective in everyday life.</p></div>
</div></section>
<section class="center" style="padding-top:32px"><div class="wrap">
 <p class="bigquote">“You are unique, <span>simply and wonderfully you.</span>”</p>
 <p class="lead" style="margin-top:24px">Your uniqueness is your power. I believe in working with, not against, your body. Together, we’ll uncover what energizes you, makes you feel strong, and keeps you in sync with your goals.</p>
</div></section>
{cta('Let’s Work Together', "Whether you're preparing for your first triathlon, training for an Ironman, targeting a marathon or looking to improve your cycling performance, I can help you develop a nutrition strategy that supports your training, recovery and goals.", 'Let’s build something sustainable, empowering, and truly yours.', 'sports-nutritionist-ireland.html')}
"""
    schema = {"@context": "https://schema.org", "@type": "Person", "name": "Marine Lenehan", "jobTitle": "Sports Nutritionist",
              "worksFor": {"@type": "Organization", "name": "Vivify Sports", "url": LIVE}, "url": LIVE + '/about', "sameAs": [IG]}
    return shell('about.html', body, schema)

# ---------------------------------------------------------------- PHILOSOPHY
def philosophy():
    P = [('IMPROVED ENERGY LEVELS AND PERFORMACE', ['In order for our bodies to perform and feel good, the food we choose is very important. While some food make us feel awesome, some foods can actually make us feel depleted. Having the right diet can actually be a game changer in terms of performance.']),
         ('WEIGHT MANAGEMENT', ['Whether you are trying to loose or gain weight, VIVIFY SPORTS will have the personalized solution for you. Each body is built differently and has different needs.',
                                'Weight is determined by the quantity of energy (aka calories) we eat  &amp; how satisfied these foods make us feel. Unfortunately, certain foods in our environment which we tend to consume in excess like refined carbs, sugar &amp;  fats tend to be high in calorie density &amp; low in satiety : causing us to eat more calories.',
                                'Looking on the bright side, foods like protein, fiber, fruit, vegetables,.. have the opposite combination as they are lower in calorie density and also higher in satiety....causing us to naturally eat less.',
                                '<b class="callout-inline">BALANCE IS THE KEY</b>']),
         ('STRONGER &amp; LEANER  MUSCLES', ['We often tend to forget about Protein but proteins are the building blocks for our muscles.']),
         ('STRENGHTENING OF THE IMMUNE SYSTEM', ['The immune system is our body’s defence system against external elements such as viruses, bacteria, and fungi. It has been proven that physical activity, following adequate training, activates it, thus strengthening our barriers. But, the high demands of competitive or recreational sport, can cause the immune system to be suppressed. This is what is called immunosuppression. VIVIFY SPORTS will help you avoid this natural immunodepression.',
                                                 'A balanced diet is the key to a healthy and performing body.']),
         ('A HEALTHY GUT', ['Gut health is directly related to athletic performance. Athletes should consider improving their gut health as this can result in reductions in gastrointestinal stress while training/ competing (such as cramping, nausea, bloating, etc), better carbohydrate absorption, optimized immune function, and inflammation regulation.'])]
    cards = ''.join(f'<div class="pcard panel"{" style=%sgrid-column:span 2%s" % (chr(34), chr(34)) if i == 1 else ""}><span class="num">{i+1}</span><span class="h3">{t}</span>' + ''.join(f'<p>{p}</p>' for p in ps) + '</div>' for i, (t, ps) in enumerate(P))
    body = f"""
<section class="page-hero"><div class="wrap">
 <p class="bigquote" style="font-size:clamp(26px,3.6vw,44px)">"Our food should be our medicine and <span>our medicine should be our food</span>"</p>
 <p class="eyebrow" style="margin-top:18px">Hippocrates</p>
</div></section>
<section style="padding-top:8px"><div class="wrap">
 {head('Sports nutrition philosophy', 'THE VIVIFY SPORTS METHOD', tag='h1', center=True, lead="At Vivify sports, we don't believe in dieting and the main goal is to make healthy eating simple and every meal enjoyable.", cls='h2')}
 <div class="g3 phil" style="margin-top:40px">{cards}</div>
</div></section>
<style>.callout-inline{{display:inline-block;color:var(--on-aqua);background:var(--aqua);padding:8px 14px;border-radius:8px;font:700 13px Montserrat,sans-serif;letter-spacing:.14em}}
@media (max-width:980px){{.phil>div{{grid-column:auto!important}}}}</style>
{cta('Put the method to work', 'Personalised nutrition coaching built around your training load, goals and lifestyle.', 'See coaching plans', 'sports-nutritionist-ireland.html')}
"""
    return shell('nutrition-nutrition-philosophy.html', body)

# ---------------------------------------------------------------- COACHING
def coaching():
    S, D = 'S', '-'
    rows = [('Dietary Monitoring', '', ['50 min', '30 min', '3 months', '3 months', '3 months']),
            ('Number of calls', '', ['1', '1', '3', '5', 'Unlimited']),
            ('Daily contact via WhatsApp', '', [D, D, D, D, S]),
            ('Weekly Meal Plan', 'based on your training load', [D, D, D, S, S]),
            ('Weekly Macro Plan', 'based on your training load', [D, D, S, D, S]),
            ('Advice on healthy nutritional habits', '', [S, S, S, S, S]),
            ('Food Diary Analysis', '', [D, D, 'Weekly', 'Daily', 'Daily']),
            ('Vitamins &amp; minerals requirements', '', [S, S, D, D, S]),
            ('Supplements requirements', '', [S, S, D, S, S]),
            ('Sports-specific requirements', '', [S, S, S, S, S]),
            ('“Breakfasts to ignite your potential” ebook', '', [D, D, D, D, S])]
    def cell(v):
        return f'<td>{ICON["star"]}<span class="skip">Included</span></td>' if v == S else ('<td class="dash" aria-label="Not included">–</td>' if v == D else f'<td>{v}</td>')
    trs = ''.join(f'<tr><th scope="row">{n}' + (f'<small>({s})</small>' if s else '') + '</th>' + ''.join(cell(v) for v in vs) + '</tr>' for n, s, vs in rows)
    trs += '<tr class="price"><th scope="row">Pricing</th>' + ''.join(f'<td>{a}<small>{b}</small></td>' for a, b in
           [('100 €', '120 US$'), ('50 €', '60 US$'), ('99 €/month', '119 US$/month'), ('149 €/month', '180 US$/month'), ('199 €/month', '240 US$/month')]) + '</tr>'
    table = f"""<div class="tbl-wrap"><table class="cmp"><caption class="skip">Vivify Sports nutrition coaching plans compared</caption>
<thead><tr><th scope="col"><span class="skip">Feature</span>{img(LOGO, LOGO_ALT, w=56, h=53, style='margin:auto')}</th><th scope="col">Nutritional Assessment</th><th scope="col">Follow-up Consultation</th><th scope="col">The Healthy Body Plan</th><th scope="col">The Happy Body Plan</th><th scope="col">The Performing Body Plan<br><small style="font:600 11px Montserrat,sans-serif;letter-spacing:.12em;color:var(--text-3)">SOLD OUT</small></th></tr></thead>
<tbody>{trs}</tbody></table></div>"""

    def plan(h2, price, dur, intro, inc, btn, href, feat=False, extra='', sold_out=False):
        ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
        if sold_out:   # Marine 17 Nov: The Performing Body Plan is sold out for now
            return (f'<article class="plan panel soldout"><h2>{h2}<span class="skip"> - </span><span class="price">{price}</span>'
                    + (f' <span class="dur">{dur}</span>' if dur else '') + '</h2>' + extra + f'<p>{intro}</p><p class="inc">Includes:</p>{ticks(inc)}'
                    + '<span class="btn btn-secondary" aria-disabled="true" style="cursor:default">Sold out for now</span></article>')
        sep = '<span class="skip"> - </span>' if dur else ' '
        return (f'<article class="plan panel{" feat" if feat else ""}"><h2>{h2}{sep}<span class="price">{price}</span>'
                + (f' <span class="dur">{dur}</span>' if dur else '') + '</h2>' + extra + f'<p>{intro}</p><p class="inc">Includes:</p>{ticks(inc)}'
                + f'<a class="btn {"btn-primary" if feat or href.startswith("http") else "btn-secondary"}" href="{href}"{ext}>{btn}</a></article>')
    one = plan('NUTRITIONAL ASSESEMENT', '50mn 100€ / 120 US$', '', 'A complete evaluation to understand your current nutrition, goals, and needs.',
               ['Personalized advice on healthy habits and food preferences', 'Vitamin &amp; mineral recommendations', 'Supplement guidance', 'Sports-specific nutrition'], 'Book now', BOOK_CAL)
    two = plan('FOLLOW-UP CONSULTATION', '30mn 50€ / 60 US$', '', 'A session to review your progress, fine-tune your plan, and stay on track.',
               ['1 follow-up call', 'Updated nutritional and supplement advice'], 'Book now', BOOK_CAL)
    p1 = plan('THE HEALTHY BODY PLAN', '99€/MONTH', '3 months', 'Build sustainable, healthy eating habits that energize your everyday life.',
              ['3 calls over 3 months', 'Weekly macro plan based on your training load', 'Weekly food diary analysis', 'Advice on balanced nutrition'], 'Sign up', PAY['healthy'])
    p2 = plan('THE HAPPY BODY PLAN', '149€/MONTH', '3 months', 'Create harmony between your nutrition, mood, and lifestyle to bring out the best of you.',
              ['5 calls over 3 months', 'Weekly meal plan tailored to your training', 'Daily food diary analysis', 'Advice on balanced nutrition, vitamins and supplements', 'Daily Support &amp; Motivation'], 'Sign up', PAY['happy'], feat=True)
    p3 = plan('THE PERFORMING BODY PLAN', '199€/MONTH', '3 months', 'Maximize performance and recovery with a fully personalized approach.',
              ['Unlimited coaching calls', 'Daily WhatsApp support', 'Weekly meal &amp; macro plan', 'Daily food diary analysis', 'Vitamin, supplement &amp; sports-specific optimization', 'Exclusive ebook: "Breakfast to Ignite your potential"'],
              'Sign up', PAY['performing'], sold_out=True, extra='<h2 style="font-size:17px;color:var(--aqua);margin:2px 0 10px">SPORTS SPECIFIC REQUIMENTS</h2>')
    partners = [('0e1488-356941ca85c445f1834a69b48ccf', 'TrainingPeaks logo', None), ('0e1488-a23fdd6bc1854f5a83c28cb05ea9', 'MyFitnessPal logo', None),
                ('0e1488-e926906d84424b06892a7eb7a3b6', 'Cigala Cycling logo', 'https://www.cigalacycling.com/'),
                ('vekta-logo', 'Vekta logo', None), ('0e1488-44c2783c595b4fcba972291cd77f', 'Wicklow 200 logo', None)]   # Marine 17 Nov: + Vekta, - Bryan McKinney
    pl = ''.join((f'<a href="{u}" target="_blank" rel="noopener">' if u else '<span>') + img(p, a, w=150, h=72, style='width:auto') + ('</a>' if u else '</span>') for p, a, u in partners)
    body = f"""
<section class="page-hero"><div class="wrap">
 <span class="eyebrow">Sports Nutritionist Ireland</span><h1>ONLINE NUTRITION COACHING</h1><span class="bar" style="margin:16px auto 18px"></span>
 <p class="lead">Ever wish you could have your own nutritionist that will tell you exactly what to do and be there with you every step of the way?</p>
 <a class="btn btn-primary" href="#plans">See the plans {ICON['arrow']}</a>
</div></section>
<section style="padding-top:16px"><div class="wrap g2" style="align-items:start">
 <div>{head('Personalised coaching', 'PERSONALIZED NUTRITION PLANS FOR YOU')}
  <p>As an athlete, you want to train hard, compete and be successful. Nutrition will help you do that. Your nutrition requirements are determined by your sport, your training &amp; your genetic make-up.These coaching plans are designed to give you personalized support to reach your goals. Partnered with Training Peaks, Vekta &amp; MyFitnessPal, Marine will build your nutrition plan weekly according to your training load. You will know exactly what to eat on &amp; off training. Whether you are looking to clean up your diet a bit, increase performance, support training adaptations, support your gut health, boost your energy levels or simply have a healthy relationship to food, VIFIFY SPORTS is here to help.</p>
  <p>By assessing your dietary patterns, relationship to food, macronutrient &amp; micronutrient balance, VIVIFY SPORTS will give you tailored solutions to reach your goals.</p></div>
 <div class="panel" style="padding:32px"><span class="eyebrow">What we look at</span>
  {chips(['Macronutrients requirements', 'Vitamins &amp; Minerals requirements', 'Supplements requirements', 'Sports specific requirements', 'Lifestyle advice', 'Healthy recipes', 'Craving control guidelines', 'IBS or gastro-intestinal issues'])}</div>
</div></section>
<section id="plans" style="padding-top:24px"><div class="wrap">
 {head('Compare', 'Find the right plan', tag=None, center=True)}
 <div style="margin-top:28px">{table}</div>
 <div class="plans two" style="margin-top:48px">{one}{two}</div>
 <div class="plans" style="margin-top:28px">{p1}{p2}{p3}</div>
</div></section>
<section style="padding-top:24px"><div class="wrap g2" style="align-items:start">
 <div>{head('The Performing Body Plan', 'Sport-specific nutrition', tag=None)}
  <p>The requirements for sports nutrition can vary greatly between sports, depending on the length of the activity, the intensity, training requirements and energy system requirements. Sport-specific nutrition entails a dietary regime that will aid in optimizing sports performance. You can consider food products such as sports drinks, sports bars, sports gels and protein shakes, but in most cases basic nutrition products are just as good (or sometimes even better).</p>
  <p style="color:var(--text);font-weight:600">With THE PERFORMING BODY PLAN, you can expect :</p></div>
 <div class="panel" style="padding:32px">{chips(['Daily macronutrient plan', 'Daily hydration plan', 'Daily supplement plan', 'Competition nutrition plan', 'Sweat rate test', 'Glucose sensor monitoring', 'Immunity management', 'Weight management'])}</div>
</div></section>
<section style="padding-top:8px"><div class="wrap"><div class="cta">
 <div><span class="eyebrow">Race day</span><h2>FUELLING PLAN</h2><span class="bar"></span>
  <p>As an athlete, you want to train hard, compete and be successful. Nutrition is almost as important as your training load to bring your performance to the next level. Fuelling for an event can be quite a headache. Remember bonking out half way through your event ?</p>
  <p style="margin:0">Let Marine help you to secure optimal performance by building a fuelling plan that is right for you giving you a precise plan to follow based on your sport, gender, weight &amp; metabolism.</p></div>
 <div><a class="btn btn-primary" href="contact.html">Book your fuelling plan here {ICON['arrow']}</a></div></div></div></section>
<section class="section-tight"><div class="wrap center">
 {head('Training Peaks · Vekta · MyFitnessPal', 'OUR PARTNERS', center=True)}
 <div class="partners" style="margin-top:24px">{pl}</div></div></section>
{testimonials(names={'Matteo Cigala,Italy': 'Matteo Cigala, Italy', 'Road & Gravel cyclistMatteo Cigala,Italy': 'Road & Gravel Cyclist', 'Damian Maloney, Ireland': 'Damian Maloney,Ireland', 'Road cyclistIwan Harmsen, Netherlands': 'Road Cyclist'})}
"""
    schema = {"@context": "https://schema.org", "@type": "Service", "name": "Online Nutrition Coaching", "serviceType": "Sports nutrition coaching",
              "provider": {"@type": "Organization", "name": "Vivify Sports", "url": LIVE}, "areaServed": "Worldwide",
              "offers": [{"@type": "Offer", "name": n, "price": p, "priceCurrency": "EUR"} for n, p in
                         [('Nutritional Assessment', '100'), ('Follow-up Consultation', '50'), ('The Healthy Body Plan (per month)', '99'),
                          ('The Happy Body Plan (per month)', '149'), ('The Performing Body Plan (per month)', '199')]]}
    return shell('sports-nutritionist-ireland.html', body, schema)

# ---------------------------------------------------------------- MASSAGE
def massage():
    rows = [
     ('11062b-c7086e8444c14484a9e3ec96b46e', 'Deep Tissue Massage', 'DEEP TISSUE MASSAGE <br>SPORTS MASSAGE',
      '<p>For tense women and men, who suffer from muscle pain, cramps, tension, tightness or who seek comfort in their joints. Ideal after sports training. Using a sports massage regularly to relieve tight muscles can help reduce the chance of injury and maximise performance.</p>',
      '<p>This massage, which combines firmness and softness, focuses on your deep muscles and contracted tissues by enhancing blood circulation through tight muscles, breaking down inflexible tissues and stretching out muscle fibers. The purpose of Deep Tissue Massage is to “unstick” the glued fibres of a muscle while releasing the build-up of tension, and eliminate toxins while relaxing and soothing the muscle itself</p>',
      '"Restorative method, optimizing your recovery"', 'WITH WHAT RESULTS?'),
     ('11062b-1cd33a811c224c289d977190d0c8', 'Cupping Therapy Sports Massage ', 'CUPPING THERAPY',
      '<p>For women and men, looking to detoxify their body by releasing the toxins present in bodily tissues and organs. Ideal to reduce muscle recovery time.</p>',
      '<p>This Dry Cupping technique alleviates muscle pain, tension and tightness. Especially recommended for :</p><ul><li>Arthritis</li><li>Back pain, neck pain, knee pain and shoulder pain.</li><li>Optimizing muscle recovery.</li><li>Breathing problems, such as asthma.</li><li>Gastrointestinal disorders, such as irritable bowel disease (IBD).</li><li>Headaches and migraines.</li><li>High blood pressure (hypertension)</li></ul>',
      '"A healthy outside, starts from the inside"', 'WITH WHAT RESULTS?'),
     ('11062b-95e9ba07b816419093bb92a63204', 'Medical Thai Massage Massage therapy ', 'TRADITIONAL THAI MASSAGE',
      '<p>For women and men who want to evacuate their stress, eliminate their back tension, release psoas tension, gain flexibility by combining relaxation and vitality and who prefer to remain dressed during their treatment.</p>',
      '<ul><li>Muscle pain relief by dislodging deep tensions.</li><li>Complementary to the practice of yoga.</li><li>Complementary to athletes looking to gain flexibility &amp; mobility.</li></ul>',
      '"Massage is fuel for our body"', 'WITH WHAT RESULTS ?')]
    rh = ''.join(f"""<div class="mrow{' rev' if i % 2 else ''}"><div class="ph">{img(p, a, w=1200, h=800)}</div><div class="tx">
 <h2>{t}</h2><h4>A MASSAGE FOR WHO?</h4>{who}<h4>{wl}</h4>{res}<p class="mq">{q}</p></div></div>""" for i, (p, a, t, who, res, q, wl) in enumerate(rows))
    body = f"""
<section class="page-hero"><div class="wrap">
 <span class="pill" style="margin-bottom:14px">Currently sold out</span><br><span class="eyebrow">Co. Wicklow · Co. Dublin</span><h1>MASSAGE THERAPY</h1><span class="bar" style="margin:16px auto 18px"></span>
 <p class="lead">Get a massage for the health of it.</p>
 <span class="btn btn-secondary" aria-disabled="true" style="cursor:default">Sold out for now</span>
</div></section>
<section style="padding-top:8px"><div class="wrap">{rh}</div></section>
<section style="padding-top:16px"><div class="wrap center">
 <span class="eyebrow">Recovery &amp; relaxation</span><div class="h2">Are you looking for the perfect way to relax and unwind&nbsp;?</div><span class="bar"></span>
 <p class="lead">After a training session, a sports event or you want to treat yourself or a loved one?<br>If the answer is yes to any of these questions, then booking a massage is a fantastic way to secure ultimate relaxation &amp; recovery. Having a massage is great for both mental and physical wellbeing.</p>
 <div class="facts">
  <div class="panel"><b>A great way to support athletic recovery or pain relief</b></div>
  <div class="panel"><b>Wicklow Town Service Area</b>Wicklow Town</div>
  <div class="panel"><b>On call (on demand)</b>Co. Wicklow - Co. Dublin</div></div>
 <span class="btn btn-secondary" aria-disabled="true" style="cursor:default">Sold out for now</span>
</div></section>"""
    return shell('massage-therapy.html', body)

# ---------------------------------------------------------------- YOGA
def yoga():
    body = f"""
<section class="hero" style="min-height:min(70vh,620px)">
 {img('0e1488-a687b5ba8de7467fa18ece35f8a9', 'Yoga pose on a clifftop by the sea at sunset', lazy=False, w=1440, h=955)}
 <div class="wrap"><span class="pill">Love, gratitude &amp; kindness</span><h1>ONLINE YOGA</h1>
  <p class="lead">LOVE, GRATITUDE &amp; KINDNESS</p>
  <a class="btn btn-primary" href="#book">Book your session {ICON['arrow']}</a></div>
</section>
<section><div class="wrap g3">
 <div class="pcard panel"><span class="eyebrow">Slow &amp; deep</span><h2 class="h3" style="font-size:30px">YIN YOGA</h2><span class="bar"></span>
  <p>Yin yoga works deeply into our body with passive, longer-held poses. It targets the deepest tissues of the body, our connective tissues – ligaments, joints, bones, the deep <a href="https://www.ekhartyoga.com/articles/anatomy/fascia-and-yoga" target="_blank" rel="noopener">fascia</a> networks of the body and the meridians.</p></div>
 <div class="pcard panel"><span class="eyebrow">Breath &amp; flow</span><h2 class="h3" style="font-size:30px">VINYASA YOGA</h2><span class="bar"></span>
  <p>A flow of postures, moving from one to another, seamlessly, using breath.</p></div>
 <div class="pcard panel" style="border-color:var(--aqua)"><span class="eyebrow">On &amp; off the bike</span><h2 class="h3" style="font-size:30px">YOGA FOR CYCLISTS</h2><span class="bar"></span>
  <p>Yoga is an amazing complement to cycling. It can help alleviate any sore muscles, strain or tension caused by a long day on the bike from tight hamstrings, calves &amp; thighs to lower back discomfort and shoulder pain.</p>
  <p>Also, a big aspect of yoga is controlling your breathing, so you get more out of every breath. By breathing more efficiently you will improve your body's ability to transport oxygen to your muscles helping in the muscle recovery process.</p></div>
</div></section>
<section id="book" style="padding-top:8px"><div class="wrap">
 {head('Classes', 'Book Your Session Now', center=True)}
 <div class="plans" style="margin-top:28px">
  <article class="plan panel"><h3>Yoga for cyclists</h3><p class="dur" style="display:block">(One-off payment)</p><a class="btn btn-secondary" href="contact.html" style="margin-top:18px">Enquire</a></article>
  <article class="plan panel feat" style="--x:0"><h3>Monthly Subscription</h3><p class="dur">(3 month subscription)</p><a class="btn btn-primary" href="contact.html" style="margin-top:18px">Enquire</a></article>
  <article class="plan panel"><h3>Private Class</h3><p class="dur" style="display:block">(One-off payment)</p><a class="btn btn-secondary" href="contact.html" style="margin-top:18px">Enquire</a></article>
 </div>
 <div class="center" style="margin-top:40px"><span style="display:inline-block;background:#fff;border-radius:50%;padding:10px">{img('0e1488-fc2524470e9740249b245fb18b25', 'Yoga alliance certified ', w=120, h=120)}</span></div>
</div></section>
<style>#book .feat::before{{content:"Best value"}}</style>"""
    return shell('yoga.html', body)

# ---------------------------------------------------------------- WORKSHOPS
def workshops():
    body = f"""
<section class="page-hero"><div class="wrap">
 <span class="eyebrow">Clubs · Gyms · Teams</span><h1>WORKSHOPS &amp; TALKS</h1><span class="bar" style="margin:16px auto 18px"></span>
 <p class="lead">If you have a competitive sports club or gym &amp; want to improve nutrition practices, Marine can come and talk to your athletes &amp; coaches on optimizing nutrition for training and competitions.</p>
</div></section>
<section style="padding-top:8px"><div class="wrap g2" style="align-items:start">
 <div class="panel" style="padding:36px"><span style="color:var(--aqua)">{ICON['talk']}</span>
  <p class="lead" style="margin-top:16px">Often this is a good way to help athletes improve on their sports performance as well as find out the latest guidelines on sports nutrition.</p>
  <p class="muted" style="margin:0">In person or online, for athletes, coaches and staff.</p></div>
 <div>{head('Who it is for', "Marine's area of expertise :", tag=None)}
  {chips(['Cycling clubs', 'Running clubs', 'Swimming clubs', 'Athletic clubs', 'Gym members &amp; staff', 'Team Sports'])}</div>
</div></section>
{cta('Book a talk for your club', 'Tell Marine about your club, your athletes and the topics you want covered.', 'Get in touch', 'contact.html')}"""
    return shell('workshops.html', body)

# ---------------------------------------------------------------- E-BOOK
def ebook():
    body = f"""
<section style="padding-top:72px"><div class="wrap g2">
 <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
  <div class="portrait" style="grid-column:span 2">{img('0e1488-02b9e172b6554125b220ca537b76', 'Blueberry Buttermilk Pancakes', lazy=False, w=1364, h=762)}</div>
  <div class="portrait">{img('0e1488-8cee9e1e3ac743dd828b4bd69d89', 'Raspberry Chia Seed pudding', w=1343, h=761)}</div>
  <div class="panel center" style="display:flex;flex-direction:column;justify-content:center;padding:18px"><span class="h2" style="font-size:54px;color:var(--aqua)">30</span><span class="eyebrow" style="margin:6px 0 0">recipes</span></div>
 </div>
 <div><span class="eyebrow">E-Book</span><h1 style="font-size:clamp(38px,5vw,62px)">BREAKFATS TO IGNITE YOUR POTENTIAL</h1><span class="bar"></span>
  <p style="font:600 18px/1.5 Montserrat,sans-serif;color:var(--text);font-style:italic">"Healthy recipes to keep you fuelled &amp; happy "</p>
  <p>A downloadable book to inspire your mornings. From sweet to savoury, there are recipes for every pallet.</p>
  <p>Breakfast lives up to its reputation as the most important meal of the day. Your first meal of the day can have long lasting effects throughout your day and on your long-term health.</p>
  <p style="color:var(--text);font-weight:700;margin-bottom:6px">What's included ?</p>
  {ticks(['30 recipes', 'Method', 'Ingredients list', 'Nutritional information'])}
  <div style="display:flex;align-items:center;gap:22px;margin-top:26px;flex-wrap:wrap"><span class="h2" style="font-size:44px">5.99€</span>
   <a class="btn btn-primary" href="{LIVE}/recipies" target="_blank" rel="noopener">Buy now {ICON['arrow']}</a></div></div>
</div></section>"""
    schema = {"@context": "https://schema.org", "@type": "Product", "name": "Breakfasts to Ignite Your Potential (e-book)",
              "brand": {"@type": "Brand", "name": "Vivify Sports"}, "offers": {"@type": "Offer", "price": "5.99", "priceCurrency": "EUR"}}
    return shell('recipies.html', body, schema)

# ---------------------------------------------------------------- BLOG
def norm(s):
    return re.sub(r'[^a-z0-9]+', '', html.unescape(s).lower())

MISSING_FROM_SITEMAP = {'Iron Deficiency, Anemia and Performance': LIVE + '/post/iron-deficiency-anemia-and-performance'}  # live 200, not in Wix sitemap

def blog_posts():
    lines = [l.strip() for l in open(V + 'text/blog.txt') if l.strip()]
    by_h1 = {}
    for r in BASE.values():
        if '/post/' in r['url'] and r.get('h1'):
            by_h1.setdefault(norm(r['h1'][0]), r['url'])
    imgs = json.load(open(V + 'images.json'))
    by_alt = {}
    for k, v in imgs.items():
        for a in v['alts']:
            by_alt.setdefault(norm(a), os.path.basename(v['webp'])[:-5])
    posts = []
    for i, l in enumerate(lines):
        if l == 'Marine Lenehan' and i >= 2:
            title, ex, date, read = lines[i-2], lines[i-1], lines[i+1], lines[i+2]
            url = by_h1.get(norm(title)) or MISSING_FROM_SITEMAP.get(title)
            posts.append(dict(title=title, ex=ex, date=date, read=read, url=url, img=by_alt.get(norm(title))))
    return posts

CATS = [('All Posts', None), ('Fuelling', r'carb|fuel|bonk|ironman|lactate|drink|cherry|gel|endurance'),
        ('Recipes', r'pancake|bread|porridge|smoothie|butter|breakfast'), ('Weight & health', r'weight|loosing|fat|fasting|christmas|tired|fatigue|supplement|iron'),
        ('Recovery & yoga', r'yoga|massage|recovery|cherry')]

def blog():
    posts = blog_posts()
    cards = ''
    for p in posts:
        href = 'post-carbohydrate-fueling-endurance-sports.html' if p['url'] and p['url'].endswith('/carbohydrate-fueling-endurance-sports') else (p['url'] or '#')
        tags = ' '.join(str(i) for i, (_, rx) in enumerate(CATS) if rx and re.search(rx, p['title'].lower()))
        ph = img(p['img'], p['title'], w=640, h=400) if p['img'] else f'<div style="height:100%;display:flex;align-items:center;justify-content:center">{img(LOGO, LOGO_ALT, w=90, h=85)}</div>'
        cards += f"""<a class="bcard panel" href="{href}" data-t="{tags}"><div class="ph">{ph}</div><div class="tx">
 <h2>{e(p['title'])}</h2><p>{e(p['ex'])}</p><div class="meta"><span>{e(p['date'])}</span><span>{e(p['read'])}</span></div></div></a>"""
    filt = ''.join(f'<button type="button" data-f="{"" if rx is None else i}" aria-pressed="{"true" if rx is None else "false"}">{e(n)}</button>' for i, (n, rx) in enumerate(CATS))
    body = f"""
<section class="page-hero" style="padding-bottom:36px"><div class="wrap">
 <span class="eyebrow">Recipes &amp; evidence-based articles</span><h1>Sports Nutrition Blog</h1><span class="bar" style="margin:16px auto 18px"></span>
 <p class="lead">Healthy recipes and evidence-based articles on cycling, endurance fuelling, recovery and weight management, by Marine Lenehan, MSc Sports Nutritionist.</p>
</div></section>
<section style="padding-top:0"><div class="wrap">
 <div class="filters" role="group" aria-label="Filter posts">{filt}</div>
 <div class="bgrid">{cards}</div></div></section>
<script>
document.querySelectorAll('.filters button').forEach(b=>b.addEventListener('click',()=>{{
 document.querySelectorAll('.filters button').forEach(x=>x.setAttribute('aria-pressed',x===b));
 const f=b.dataset.f;document.querySelectorAll('.bcard').forEach(c=>c.style.display=(!f||c.dataset.t.split(' ').includes(f))?'':'none');}}));
</script>"""
    return shell('blog.html', body), len(posts), sum(1 for p in posts if p['img']), sum(1 for p in posts if p['url'])

# ---------------------------------------------------------------- POST (template, from the live article)
def post():
    d = json.load(open(V + 'raw/post-carbs.json'))
    parts, ul = [], []
    def flush():
        if ul:
            parts.append('<ul>' + ''.join(f'<li>{e(x)}</li>' for x in ul) + '</ul>'); ul.clear()
    imgs = json.load(open(V + 'images.json'))
    for tag, val, *rest in d['out']:
        if tag != 'LI': flush()
        if tag == 'H1': continue
        if tag == 'LI': ul.append(val); continue
        if tag == 'IMG':
            m = re.search(r'media/([^/]+)', val)
            if not m: continue
            mid = m.group(1)
            if mid in imgs:
                parts.append(f'<figure>{img(os.path.basename(imgs[mid]["webp"])[:-5], rest[0] or "Carbohydrate fueling for endurance sports", w=1200, h=800)}</figure>')
            continue
        if tag == 'TABLE':
            rows = val
            parts.append('<div class="tbl-wrap"><table><thead><tr>' + ''.join(f'<th>{e(c)}</th>' for c in rows[0]) + '</tr></thead><tbody>'
                         + ''.join('<tr>' + ''.join(f'<td>{e(c)}</td>' for c in r) + '</tr>' for r in rows[1:]) + '</tbody></table></div>')
            continue
        if tag in ('H2', 'H3', 'H4'):
            t = tag.lower() if tag != 'H4' else 'h3'
            parts.append(f'<{t}>{e(val)}</{t}>'); continue
        if tag == 'P':
            if re.match(r'^[~0-9].*(g|hour)$', val) and len(val) < 70:
                parts.append(f'<p class="callout panel">{e(val)}</p>')
            else:
                parts.append(f'<p>{e(val)}</p>')
    flush()
    recent = ''.join(f'<a class="bcard panel" href="{p["url"]}"><div class="ph">{img(p["img"], p["title"], w=640, h=400)}</div><div class="tx"><h3 class="h3" style="font-size:19px;margin-bottom:10px">{e(p["title"])}</h3><div class="meta"><span>{e(p["date"])}</span><span>{e(p["read"])}</span></div></div></a>'
                     for p in [x for x in blog_posts() if x['img'] and 'carbohydrate-fueling' not in (x['url'] or '')][:3])
    r = BASE[LIVE + '/post/carbohydrate-fueling-endurance-sports']
    h1 = r['h1'][0]
    hero = img('0e1488-45f685e5e5e54029b7cf7b5211aa', 'Carbohydrate Fueling for Endurance Sports: How Many Carbs Per Hour Do You Need?', lazy=False, w=1200, h=1600, style='aspect-ratio:16/9;object-fit:cover;object-position:50% 40%')
    body = f"""
<section style="padding-top:64px"><div class="wrap"><article class="article">
 <a href="blog.html" class="eyebrow" style="text-decoration:none">← Sports Nutrition Blog</a>
 <h1>{e(h1)}</h1>
 <div class="byline">{img('0e1488-5ffa2e2730204ef0bae918a9e4ae', 'Marine Lenehan', w=44, h=44)}<span><b>Marine Lenehan</b> · MSc Sports Nutritionist<br>{e(d['meta']['date'])} · {e(d['meta']['read'])}</span></div>
 <figure style="margin-top:0">{hero}</figure>
 {''.join(parts)}
 <div class="author panel">{img('0e1488-5ffa2e2730204ef0bae918a9e4ae', 'Marine Lenehan', w=84, h=84)}<div>
  <span class="eyebrow">Written by</span><div class="h3">Marine Lenehan</div>
  <p class="muted" style="margin:8px 0 14px">MSc Sports Nutritionist | WorldTour Professional Cyclist. Founder of Vivify Sports, Wicklow, Ireland.</p>
  <a class="btn btn-primary" href="{DISCOVERY}">Book a free discovery call</a></div></div>
</article>
 <div style="margin-top:72px">{head('Keep reading', 'Recent Posts', center=True)}<div class="bgrid" style="margin-top:28px">{recent}</div></div>
</div></section>"""
    schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": h1, "author": {"@type": "Person", "name": "Marine Lenehan"},
              "publisher": {"@type": "Organization", "name": "Vivify Sports"}, "mainEntityOfPage": LIVE + '/post/carbohydrate-fueling-endurance-sports'}
    return shell('post-carbohydrate-fueling-endurance-sports.html', body, schema)

# ---------------------------------------------------------------- CONTACT / DISCOVERY / PRIVACY
def contact():
    body = f"""
<section class="page-hero" style="padding-bottom:32px"><div class="wrap">
 <span class="eyebrow">Sports nutrition consultation</span><h1>Contact</h1><span class="bar" style="margin:16px auto 18px"></span>
 <p class="lead">Contact Vivify Sports for personalised sports nutrition support.</p>
</div></section>
<section style="padding-top:8px"><div class="wrap g2" style="align-items:start">
 <div class="panel" style="padding:36px">
  <span class="eyebrow">Free · 30 min</span><h2 class="h3" style="font-size:30px">Schedule your service</h2><span class="bar"></span>
  <p><b style="color:var(--text)">Vivify Sport's Discovery Call</b></p>
  <p class="muted" style="display:flex;gap:8px;align-items:center">{ICON['clock']} 30 min · online</p>
  <a class="btn btn-primary" href="{BOOK_CAL}" target="_blank" rel="noopener">Book now {ICON['arrow']}</a>
  <ul class="cinfo" style="margin-top:28px">
   <li>{ICON['mail']}<a href="mailto:{EMAIL}">{EMAIL}</a></li>
   <li>{ICON['phone']}<a href="tel:{PHONE_TEL}">{PHONE}</a></li>
   <li>{ICON['ig']}<a href="{IG}" target="_blank" rel="noopener">@vivifysports</a></li>
   <li>{ICON['pin']}<span>Wicklow, Ireland · working with athletes worldwide</span></li></ul>
 </div>
 <form class="form panel" style="padding:36px" action="mailto:{EMAIL}" method="post" enctype="text/plain">
  <span class="eyebrow" style="margin:0">Send a message</span>
  <div class="two"><div><label for="f-n">Name</label><input id="f-n" name="name" autocomplete="name" required></div>
   <div><label for="f-e">Email</label><input id="f-e" type="email" name="email" autocomplete="email" required></div></div>
  <div><label for="f-s">I'm interested in</label><select id="f-s" name="service">
   <option>Nutrition coaching</option><option>Fuelling plan</option><option>Workshops &amp; talks</option><option>Massage therapy</option><option>Yoga</option><option>Something else</option></select></div>
  <div><label for="f-m">Message</label><textarea id="f-m" name="message" placeholder="Your sport, your goals and any upcoming events"></textarea></div>
  <button class="btn btn-primary" type="submit" style="justify-self:start">Send message</button>
 </form>
</div></section>"""
    return shell('contact.html', body)

def discovery():
    body = f"""
<section class="page-hero"><div class="wrap">
 <span class="eyebrow">Free sports nutrition consultation</span><h1>Our Services</h1><span class="bar" style="margin:16px auto 18px"></span>
</div></section>
<section style="padding-top:0"><div class="wrap" style="max-width:720px">
 <div class="panel center" style="padding:44px 32px">
  {img(LOGO, LOGO_ALT, w=90, h=85, style='margin:0 auto 18px;border-radius:8px')}
  <h2 style="font-size:clamp(28px,3.4vw,40px)">Vivify Sport's Discovery Call</h2><span class="bar"></span>
  <p class="muted" style="display:flex;gap:8px;align-items:center;justify-content:center">{ICON['clock']} 30 min</p>
  <a class="btn btn-primary" href="{BOOK_CAL}" target="_blank" rel="noopener">Book Now {ICON['arrow']}</a>
 </div></div></section>"""
    return shell('free-sports-nutrition-consultation.html', body)

def privacy():
    rows = [l.split('\t', 1)[1] for l in open(V + 'text/privacy-policy.tsv') if '\t' in l]
    out = []
    for t in rows[1:]:
        if re.match(r'^\d+\.', t) and len(t) < 90:
            out.append(f'<p class="h3" style="margin:34px 0 10px">{e(t)}</p>')
        else:
            out.append(f'<p>{e(t)}</p>')
    body = f"""
<section class="page-hero" style="padding-bottom:24px"><div class="wrap"><span class="eyebrow">Vivify Sports</span><h1>Privacy Policy</h1><span class="bar" style="margin:16px auto 0"></span></div></section>
<section style="padding-top:8px"><div class="wrap article"><p style="color:var(--text);font-weight:700">{e(rows[0])}</p>{''.join(out)}</div></section>"""
    return shell('privacy-policy.html', body)

# ---------------------------------------------------------------- write
if __name__ == '__main__':
    open(OUT + 'vivify.css', 'w').write(CSS)
    b, n, ni, nu = blog()
    for f, h in [('index.html', home()), ('about.html', about()), ('nutrition-nutrition-philosophy.html', philosophy()),
                 ('sports-nutritionist-ireland.html', coaching()), ('massage-therapy.html', massage()), ('yoga.html', yoga()),
                 ('workshops.html', workshops()), ('recipies.html', ebook()), ('blog.html', b), ('contact.html', contact()),
                 ('free-sports-nutrition-consultation.html', discovery()), ('privacy-policy.html', privacy()),
                 ('post-carbohydrate-fueling-endurance-sports.html', post())]:
        open(OUT + f, 'w').write(h)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import vivify_seo_pages
    vivify_seo_pages.build(sys.modules[__name__])
    print(f'built {len(PAGES)} pages; blog cards {n} (with image {ni}, with live URL {nu})')
