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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vivify_example as EX   # 'What your coaching looks like' example week
import vivify_icons as VI   # Marine 19 Nov: line icons in boxes

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
LOGO_T = 'vivify-logo-white'   # transparent version for header and footer (Marine 17 Nov, tools/vivify_logo.py)

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
        'Cycling nutrition coaching with Marine Lenehan, MSc and LIDL-TREK WorldTour rider: Gran Fondo, sportive, gravel, track, MTB and cyclocross. Ireland and online.'),
    'race-fuelling-plan.html': ('/race-fuelling-plan', 'Race Fuelling Plan for Cyclists & Triathletes | Vivify Sports',
        'A race fuelling plan for your event: race day and the day before, carbs per hour, supplements, hydration and recovery, by a WorldTour cyclist and MSc nutritionist.'),
    'triathlon-nutritionist.html': ('/triathlon-nutritionist', 'Triathlon Nutritionist | Ironman & 70.3 Nutrition | Vivify Sports',
        'Triathlon nutrition coaching for Ironman, 70.3, Olympic and sprint: daily fuelling for swim, bike and run and a plan for race day. Online, from Ireland.'),
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
# Header menu, Cigala Coaching style (Marine 17 Nov): (label, file) or (label, [(file, label), ...])
MOTION_JS = r"""(function(){var d=document,h=d.documentElement;h.classList.add('vv-js');
function hdr(){var x=d.querySelector('header.site');if(!x)return;x.classList.toggle('scrolled',scrollY>40);h.style.setProperty('--hdr-h',x.getBoundingClientRect().height+'px');}
addEventListener('scroll',hdr,{passive:true});addEventListener('resize',hdr);
d.addEventListener('DOMContentLoaded',function(){hdr();
 if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window))return;
 var els=d.querySelectorAll('section .wrap>div:not(.g2):not(.g3):not(.g4):not(.intro):not(.tgrid):not(.bgrid):not(.plans):not(.facts),.panel,.pcard,.mrow,.portrait,.titles li,.cta');
 var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}});},{rootMargin:'0px 0px -8% 0px'});
 els.forEach(function(el){if(el.closest('header')||el.closest('.hero'))return;var r=el.getBoundingClientRect();if(r.top<innerHeight)return;
  var i=[].indexOf.call(el.parentNode.children,el)%4;el.style.transitionDelay=(i*80)+'ms';el.classList.add('rv');io.observe(el);});
 // Google reviews: Trustindex's loader (cdn.trustindex.io) reveals the widget; if it is blocked, show the reviews anyway
 setTimeout(function(){d.querySelectorAll('.ti-widget[data-css-url]').forEach(function(w){if(getComputedStyle(w).opacity!=='0')return;
  var l=d.createElement('link');l.rel='stylesheet';l.href=w.getAttribute('data-css-url');d.head.appendChild(l);w.removeAttribute('style');w.classList.add('ti-fallback');});},4000);
 d.querySelectorAll('.ddt').forEach(function(b){b.addEventListener('click',function(){var li=b.parentNode;var open=li.classList.toggle('open');b.setAttribute('aria-expanded',open);});});
});})();"""

MENU = [('Home', 'index.html'),
        ('About', 'about.html', [('about.html', 'About Marine'), ('nutrition-nutrition-philosophy.html', 'Sports Nutrition Philosophy'), ('testimonials.html', 'Client Reviews')]),
        ('Coaching', 'sports-nutritionist-ireland.html', [('sports-nutritionist-ireland.html', 'Coaching Plans'),
            ('race-fuelling-plan.html', 'Race Fuelling Plan'), ('free-sports-nutrition-consultation.html', 'Free Discovery Call')]),
        ('Who I Help', None, [('cycling-nutritionist.html', 'Cyclists'), ('womens-cycling-nutrition.html', "Women's Cycling"), ('triathlon-nutritionist.html', 'Triathletes'),
                              ('online-sports-nutritionist.html', 'Online, Worldwide'), ('sports-nutritionist-dublin.html', 'Dublin & Wicklow')]),
        ('Workshops', 'workshops.html'), ('E-Book', 'recipies.html'), ('Blog', 'blog.html'), ('Contact', 'contact.html')]
# Marine 17 Nov: lighter header; About keeps its place and holds Philosophy (+ Reviews); short "Coaching" label
DISCOVERY = 'https://cal.com/marine-lenehan/discovery-call'   # Marine 17 Nov: Cal.com replaces Wix Bookings
BOOK_CAL = DISCOVERY
MASSAGE_BOOK = 'http://VEV.CO/MASSAGE-THERAPIST-VIVIFY-SPORTS-IE'
PAY = {'healthy': 'https://pay.gocardless.com/BRT0004V6AWJMPG', 'happy': 'https://pay.gocardless.com/BRT00045M0TDENA',
       'performing': 'https://pay.gocardless.com/BRT00045M0SDGT2', 'yoga_monthly': 'https://pay.gocardless.com/BRT0002A1NBMZ4S'}
EMAIL, PHONE, PHONE_TEL = 'marine@vivifysports.com', '+353 87 224 7402', '+353872247402'
IG = 'https://www.instagram.com/vivifysports/'
VAT = 'IE8879803O'   # Marine 18 Nov (Irish E-Commerce Regulations: VAT number on the website)
EBOOK_PAY = 'https://buy.stripe.com/bJe7sN9augIR63nb6w8k800'   # Marine's Stripe payment link, 5.99 EUR (17 Nov)
ASSESSMENT_PAY = 'https://cal.com/marine-lenehan/nutritional-assessment'   # Nutritional Assessment: Cal.com paid event, pay + book in one step (17 Nov; was Stripe aFa4gBbiC3W563nb6w8k801)
FOLLOWUP_PAY = 'https://cal.com/marine-lenehan/30min'     # Follow-up Consultation: Cal.com paid event (17 Nov; was Stripe aFa3cx72m9gp1N7gqQ8k802)
FUELLING_PAY = 'https://cal.com/marine-lenehan/fuelingplan'     # Race Fuelling Plan 70 EUR: Cal.com paid event, 30 min call + PDF plan (17 Nov; was Stripe aFa28t0DY5092RbdeE8k803)
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
header.site .hdr{display:flex;align-items:center;gap:16px;height:78px;max-width:1360px;transition:height .25s}
header.site.scrolled{box-shadow:0 10px 30px rgba(0,0,0,.35)}
header.site.scrolled .hdr{height:64px}
header.site.scrolled .logo img{height:44px;width:auto}
.logo img{transition:height .25s}
.logo{flex-shrink:0}
.topbar{background:linear-gradient(90deg,#123a40,#19444B 50%,#123a40);border-bottom:1px solid var(--border);font:500 12.5px/1 Montserrat,sans-serif;color:var(--text-2);overflow:hidden;max-height:40px;transition:max-height .25s}
.topbar .wrap{display:flex;gap:10px;align-items:center;justify-content:center;height:36px;flex-wrap:wrap}
.topbar a{color:var(--lime-text);font-weight:700;text-decoration:none;margin-left:6px}
header.site.scrolled .topbar{max-height:0}
@media (max-width:640px){.topbar .tb-sep,.topbar span:nth-of-type(3){display:none}}
.logo img{height:54px;width:auto}
nav.main{margin:0;flex:1;display:flex;justify-content:center}   /* Marine 18 Nov: menu centred */
@media (min-width:1101px){header.site .hdr{display:grid;grid-template-columns:1fr auto 1fr;gap:16px}
 header.site .hdr .logo{justify-self:start}header.site .hdr .hdr-cta{justify-self:end}nav.main{flex:none}}
nav.main > ul{gap:0!important}
nav.main ul{display:flex;gap:4px;list-style:none;margin:0;padding:0}
nav.main a,nav.main .ddt{display:flex;align-items:center;gap:5px;color:var(--text);text-decoration:none;font:600 12px/1 Montserrat,sans-serif;letter-spacing:.07em;text-transform:uppercase;padding:12px 9px;position:relative;white-space:nowrap;background:none;border:0;cursor:pointer}
nav.main .ddt svg{transition:transform .2s}
nav.main .dd{position:relative}
nav.main .sub{position:absolute;top:100%;left:0;min-width:240px;flex-direction:column;gap:0;padding:10px;background:rgba(12,34,38,.98);border:1px solid var(--border-strong);border-radius:12px;box-shadow:0 18px 40px rgba(0,0,0,.45);opacity:0;visibility:hidden;transform:translateY(8px);transition:opacity .18s,transform .18s,visibility .18s}
nav.main .sub a{text-transform:uppercase;letter-spacing:.06em;font-size:13px;font-weight:600;padding:11px 12px;border-radius:8px}
nav.main .sub a:hover{background:rgba(177,216,221,.08)}
nav.main .sub a::after{display:none}
nav.main .dd:hover .sub,nav.main .dd:focus-within .sub{opacity:1;visibility:visible;transform:none}
nav.main .dd:hover .ddt svg,nav.main .dd:focus-within .ddt svg{transform:rotate(180deg)}
nav.main .ddt[data-current]::after{content:"";position:absolute;left:7px;right:20px;bottom:4px;height:2px;background:var(--lime)}
nav.main .ddt:hover{color:var(--aqua)}
nav.main > ul > li > a::after{content:"";position:absolute;left:7px;right:7px;bottom:4px;height:2px;background:transparent;transition:background .2s}
nav.main a:hover{color:var(--aqua)}nav.main a:hover::after{background:var(--aqua)}
nav.main a[aria-current=page]::after{background:var(--lime)}
nav.main li.lang{display:flex;align-items:center;gap:2px;margin-left:8px;padding-left:10px;border-left:1px solid var(--border-strong)}
nav.main li.lang a{padding:10px 6px;font-size:12px;letter-spacing:.08em;color:var(--text-3)}
nav.main li.lang a[aria-current=true]{color:var(--text)}
nav.main li.lang a::after{display:none}
.hdr-cta{padding:12px 15px;font-size:12px;white-space:nowrap}
.burger{display:none}
#menu-t{position:absolute;opacity:0;pointer-events:none}
@media (max-width:1100px){
 nav.main li.lang{margin:12px 0 0;padding:0;border:0}
 nav.main li.lang a{font-size:15px;padding:10px 14px 10px 0;border:0}
 .burger{display:flex;margin-left:auto;width:46px;height:46px;border:1px solid var(--border-strong);border-radius:8px;align-items:center;justify-content:center;cursor:pointer;color:var(--text)}
 nav.main{position:fixed;inset:var(--hdr-h,114px) 0 auto 0;background:var(--bg);border-bottom:1px solid var(--border);display:none;margin:0;max-height:calc(100vh - var(--hdr-h,114px));overflow:auto}
 nav.main .sub{position:static;opacity:1;visibility:visible;transform:none;box-shadow:none;border:0;background:none;padding:0 0 6px 14px;min-width:0}
 nav.main .ddt{width:100%;justify-content:space-between;font-size:15px;padding:16px 0;border-bottom:1px solid var(--border)}
 nav.main .ddt svg{display:none}
 nav.main .ddt[data-current]::after{display:none}
 nav.main .sub a{font-size:15px;padding:12px 0;border-bottom:1px solid var(--border)}
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
.tgrid{display:flex;flex-wrap:wrap;justify-content:center;gap:24px}   /* Marine 18 Nov: rows, last row centred */
.tcard{flex:0 1 calc((100% - 48px)/3);margin:0;padding:28px;position:relative}
@media (max-width:980px){.tcard{flex-basis:calc((100% - 24px)/2)}}@media (max-width:640px){.tcard{flex-basis:100%}}
.tgrid.single .tcard{flex-basis:100%}   /* one review on its own (Women's page) */
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

/* plan cards, Cigala Coaching style */
.notes{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:28px}
.note{border-left:3px solid var(--lime);background:rgba(25,68,75,.3);padding:14px 16px;font-size:13.5px;color:var(--text-2);border-radius:0 8px 8px 0}
@media (max-width:860px){.notes{grid-template-columns:1fr}}
.plans{align-items:start}
.plan{position:relative;padding:34px 28px 28px}
.plan .pbadge{position:absolute;top:-13px;left:50%;transform:translateX(-50%);white-space:nowrap;background:var(--lime);color:#0C2226;font:700 11px/1 Montserrat,sans-serif;letter-spacing:.14em;text-transform:uppercase;padding:8px 12px;border-radius:999px}
.plan .pbadge.sold{background:#3a1d1d;color:#ffb3ad;border:1px solid rgba(255,120,110,.35)}
.plan.feat::before,.plan.soldout::before{display:none}
.plan.feat{border:1.5px solid var(--aqua);box-shadow:0 0 0 1px rgba(177,216,221,.15),0 24px 60px rgba(177,216,221,.12);background:linear-gradient(170deg,rgba(25,68,75,.85),rgba(18,51,56,.6))}
.plan.soldout{opacity:.88}
.plan h2.pt{display:flex;flex-direction:column;align-items:flex-start;gap:0;margin:0 0 4px;font-size:27px;line-height:1.05}
.plan h2.pt .pd{order:-1;font:700 11.5px/1.3 Montserrat,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--lime-text);margin-bottom:10px}
.plan h2.pt .pn{display:block}
.plan h2.pt .pp{display:flex;align-items:baseline;gap:4px;margin-top:14px;font:400 30px/1 Anton,sans-serif;letter-spacing:.02em;color:var(--text-2)}
.plan h2.pt .pp small{font:600 13px/1 Montserrat,sans-serif;color:var(--text-3)}
.plan h2.pt .pp small.m{text-transform:lowercase}
.plan .usd{font-size:12.5px;color:var(--text-3);margin:2px 0 14px}
.plan h2.psub{font-size:15px;color:var(--aqua);margin:6px 0 8px}
.plan .pdesc{font-size:14.5px;min-height:3.2em}
.plan .pbtn{width:100%;justify-content:center;margin-top:6px}
.btn-outline{background:transparent;color:var(--text);border-color:var(--border-strong)}
.btn-outline:hover{border-color:var(--aqua);color:var(--aqua)}
.plan .after{font-size:12px;color:var(--text-3);text-align:center;margin:8px 0 0}
.plan .notsure{display:block;text-align:center;font-size:12.5px;font-weight:600;color:var(--lime-text);text-decoration:none;margin:12px 0 18px}
.plan .notsure:hover{text-decoration:underline}
.plan .wyg{font:700 11.5px/1 Montserrat,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--text-3);border-top:1px solid var(--border);padding-top:18px;margin:0 0 6px}
.plan .ticks li{font-size:14px;padding:5px 0}
.plan details.more{margin-top:14px;border-top:1px solid var(--border);padding-top:12px}
.plan details.more summary{cursor:pointer;font:700 12px/1.4 Montserrat,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--aqua);list-style:none}
.plan details.more summary::-webkit-details-marker{display:none}
.plan details.more summary::after{content:" +"}.plan details.more[open] summary::after{content:" –"}
.plan details.more p{font-size:14px;margin:10px 0 0}
.cmp th.hl,.cmp td.hl{background:rgba(177,216,221,.07)}
.cmp thead th.hl{background:#21545c;color:var(--aqua)}
/* compare table, Cigala Coaching style */
.cmp-scroll{border:1px solid var(--border-strong);border-radius:var(--r);background:var(--panel)}
.cmp2{width:100%;border-collapse:collapse;font-size:14px}
.cmp2 th,.cmp2 td{padding:13px 16px;text-align:left;border-bottom:1px solid var(--border);vertical-align:top}
.cmp2 tbody tr:last-child th,.cmp2 tbody tr:last-child td{border-bottom:0}
.cmp2 thead th{font:400 19px/1.1 Anton,sans-serif;text-transform:uppercase;color:var(--text);vertical-align:top}
.cmp2 thead th small.cmp-badge{display:block;margin-top:6px;font:700 10.5px/1 Montserrat,sans-serif;letter-spacing:.14em;color:var(--lime-text)}
.cmp2 thead th small.cmp-badge.sold{color:#ffb3ad}
.cmp2 tbody th{font-weight:600;color:var(--text);width:30%}
.cmp2 tbody th small{display:block;font-weight:400;color:var(--text-3);font-size:12px}
.cmp2 td{color:var(--text-2)}
.cmp2 .hot{background:rgba(177,216,221,.07)}
.cmp2 thead .hot{color:var(--text)}
.cmp2 .y{color:var(--lime-text);font-weight:700;font-size:16px}
.cmp2 .n{color:#ff6b61;font-weight:700;font-size:16px}
.cmp2 tr.price td{color:var(--text);font-weight:600}
.cmp2 tr.price td small{display:block;font-weight:400;color:var(--text-3);font-size:12px;margin-top:2px}
.cmp-note{margin:12px 0 0;font-size:13px;color:var(--text-3)}
@media (max-width:760px){
 .cmp2,.cmp2 tbody,.cmp2 tr,.cmp2 th,.cmp2 td{display:block}
 .cmp2 thead{display:none}
 .cmp2 tr{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-bottom:1px solid var(--border)}
 .cmp2 tbody tr:last-child{border-bottom:0}
 .cmp2 tbody th{grid-column:1/-1;width:auto;border:0;padding:14px 14px 4px}
 .cmp2 td{border:0;padding:4px 10px 14px 14px;font-size:13px}
 .cmp2 td::before{content:attr(data-l);display:block;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--text-3);margin-bottom:3px}
 .cmp2 td.hot::before{color:var(--aqua)}
}
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
/* Marine 18 Nov: justify paragraphs site-wide where suited; centred, short and caption text keeps its alignment */
p{text-align:justify;-webkit-hyphens:auto;hyphens:auto}
.center p,p.center,.page-hero p,.bigquote,p.bigquote,.center .lead,footer p,.bcard p,.cal-note p,.cal-sample,.plan .after,.plan .notsure,.plan .usd,.cmp-note,
.facts p,.wyg,.eyebrow,.pill,.tcard .name,.portrait p,p.muted:only-child{text-align:inherit;-webkit-hyphens:manual;hyphens:manual}
.center .lead,.page-hero p{text-align:center}
/* Marine 17 Nov: justified text inside boxes (as on her Wix site); hyphens keep phone lines even */
.panel p,.pcard p,.plan p,.mrow .tx p,.cta p,.scard p,.bcard p,.author p,.qa>div p,.tcard blockquote,.intro p{text-align:justify;-webkit-hyphens:auto;hyphens:auto}
.center p,.panel.center p,p.center,.facts p{text-align:center;-webkit-hyphens:manual;hyphens:manual}
/* motion (Marine 17 Nov: "more dynamic"); nothing hides without JS, nothing moves with reduced motion */
.vv-js .rv{opacity:0;transform:translateY(22px);transition:opacity .7s ease,transform .7s cubic-bezier(.2,.7,.2,1)}
.vv-js .rv.in{opacity:1;transform:none}
.btn{transition:background .2s,border-color .2s,transform .2s,box-shadow .25s}
.btn-primary:hover{box-shadow:0 10px 26px rgba(177,216,221,.25)}
.panel{transition:border-color .25s,transform .25s,box-shadow .25s}
.pcard:hover,.tcard:hover,.plan:hover{transform:translateY(-4px);border-color:var(--border-strong);box-shadow:0 18px 40px rgba(0,0,0,.3)}
.scard .ph img,.bcard .ph img,.mrow .ph img,.portrait img{transition:transform .8s cubic-bezier(.2,.7,.2,1)}
.scard:hover .ph img,.bcard:hover .ph img,.mrow:hover .ph img{transform:scale(1.05)}
.hero>img{animation:vvzoom 14s ease-out both}
@keyframes vvzoom{from{transform:scale(1.08)}to{transform:scale(1)}}
.hero .wrap>*{animation:vvup .9s cubic-bezier(.2,.7,.2,1) both}
.hero .wrap>*:nth-child(2){animation-delay:.12s}.hero .wrap>*:nth-child(3){animation-delay:.24s}.hero .wrap>*:nth-child(4){animation-delay:.36s}
@keyframes vvup{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.vv-js .rv{opacity:1;transform:none;transition:none}.hero>img,.hero .wrap>*{animation:none}*{transition:none!important}}
/* Google reviews (Trustindex): site font; backup display (loader blocked) one review per row on phones */
.greviews .ti-widget,.greviews .ti-widget *{font-family:Montserrat,system-ui,sans-serif!important}
@media (max-width:700px){.greviews .ti-widget.ti-fallback .ti-reviews-container-wrapper{display:block!important;overflow:visible!important}
 .greviews .ti-widget.ti-fallback .ti-review-item{width:100%!important;max-width:100%!important;flex:0 0 100%!important;margin-bottom:14px}
 .greviews .ti-widget.ti-fallback .ti-controls,.greviews .ti-widget.ti-fallback .ti-controls-line{display:none!important}}
/* footer */
footer.site{margin-top:40px;background:linear-gradient(180deg,rgba(25,68,75,.35),rgba(25,68,75,.7));border-top:1px solid var(--border)}
footer.site .top{display:grid;grid-template-columns:1.4fr 1fr 1fr 1.1fr;gap:40px;padding:64px 24px 40px}
footer.site .logo img{height:76px;width:auto}
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

def lang_switch(file, current='en'):
    """EN · FR · IT links: the translated version of this page if there is one (vivify/i18n.py), else that language's home"""
    sys.path.insert(0, V)
    import i18n
    def href(lang):
        if lang == 'en':
            return file if not file.startswith(('fr/', 'it/')) else file.split('/', 1)[1]
        k = file.split('/', 1)[1] if file.startswith(('fr/', 'it/')) else file
        slug = i18n.PAGES.get(k, ('', ''))[0 if lang == 'fr' else 1]
        return f'/{lang}/' + (slug + '/' if slug else '')
    return ('<li class="lang" aria-label="Language">' + ''.join(
        f'<a href="{href(l)}" hreflang="{l}" lang="{l}"' + (' aria-current="true"' if l == current else '') + f'>{l.upper()}</a>' for l in ('en', 'fr', 'it')) + '</li>')   # Marine 19 Nov: Italian site back

def shell(file, body, schema=None):
    body = VI.add_icons(body)
    path = PAGES[file]
    if file in NEW:
        b = {'title': NEW[file][1], 'meta_description': NEW[file][2]}
    else:
        b = BASE[LIVE + path] if (LIVE + path) in BASE else BASE[LIVE]
    title, desc = b['title'], b.get('meta_description') or ''
    chev = '<svg viewBox="0 0 12 8" width="9" height="6" aria-hidden="true"><path d="M1 1l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
    def item(label, target, children=None):
        if not children:
            return f'<li><a href="{target}"' + (' aria-current="page"' if target == file else '') + f'>{e(label)}</a></li>'
        cur = target == file or any(f == file for f, _ in children)
        sub = ''.join(f'<li><a href="{f}"' + (' aria-current="page"' if f == file else '') + f'>{e(t)}</a></li>' for f, t in children)
        if target:   # the parent is a page too: link + dropdown
            head_ = f'<a class="ddt" href="{target}"' + (' data-current="1"' if cur else '') + f'>{e(label)}{chev}</a>'
        else:
            head_ = f'<button type="button" class="ddt"' + (' data-current="1"' if cur else '') + f' aria-haspopup="true">{e(label)}{chev}</button>'
        return f'<li class="dd">{head_}<ul class="sub">{sub}</ul></li>'
    navh = ''.join(item(*m) for m in MENU)
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
<header class="site"><div class="topbar"><div class="wrap"><span>Free 30-minute discovery call</span><span class="tb-sep">·</span><span>Online coaching in English, French &amp; Italian</span><a href="{DISCOVERY}">Book now →</a></div></div>
<div class="wrap hdr">
 <a class="logo" href="index.html" aria-label="Vivify Sports home">{img(LOGO_T, LOGO_ALT, lazy=False, w=44, h=54)}</a>
 <input type="checkbox" id="menu-t" aria-label="Menu">
 <label class="burger" for="menu-t" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></label>
 <nav class="main" aria-label="Main"><ul>{navh}{lang_switch(file)}</ul></nav>
 <a class="btn btn-primary hdr-cta" href="{DISCOVERY}">Book a Free Call</a>
</div>
<script>{MOTION_JS}</script></header>
<main id="main">
{body}
</main>
<footer class="site">
 <div class="wrap top">
  <div><a class="logo" href="index.html">{img(LOGO_T, LOGO_ALT, w=62, h=76)}</a>
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
   <li><span class="gstars" aria-hidden="true">{ICON['star'] * 5}</span><a href="{GBP}" target="_blank" rel="noopener">Google reviews</a></li></ul>
   <a class="social" href="{IG}" aria-label="Vivify Sports on Instagram">{ICON['ig']}</a></div>
 </div>
 <div class="wrap bottom"><span>© 2023 by Vivify Sports<span class="sep"> · </span>VAT {VAT}</span>   <a href="privacy-policy.html">Privacy Policy</a></div>
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

def google_reviews():
    """Marine's Google reviews (Trustindex 'Widgets for Google Reviews' plugin, free version). In WordPress the
    shortcode runs in an Elementor Text Editor widget (tools/build_vivify_wp.py); the static preview shows a note."""
    return f"""<section class="greviews"><div class="wrap">
 {head('Google reviews', 'What clients say on Google', center=True)}
 <div class="ti-box" style="margin-top:24px">[trustindex no-registration=google]</div>
 <div class="center" style="margin-top:18px"><a class="btn btn-secondary" href="{GBP}" target="_blank" rel="noopener">{ICON['star']} Read all reviews on Google</a></div>
</div></section>"""

# Marine 19 Nov: show each client's result at a glance (taken from their own words)
HIGHLIGHT = {'Colum Traynor, Ireland': '30-min PB at Ironman 70.3', 'James Makin, Ireland': 'Over 13 kg lost before the Traka',
             'Eleonore Vaillon, France': '6 kg in 4 months', 'Matteo Cigala,Italy': 'No more cramping at the end of races',
             'Francesco Pippa, Italy': 'Fuelled for an ultra gravel race'}

def testimonials(h2_names=True, names=None):
    tag = 'h2' if h2_names else 'p'
    names = names or {}
    cards = ''.join(f"""<article class="tcard panel"><span class="q">{ICON['quote']}</span>
 <div class="who">{img(p, a, w=64, h=64)}<div><{tag} class="name">{e(names.get(n, n))} <span class="sport">{e(s)}</span></{tag}></div></div>
 {f'<p class="result">{e(HIGHLIGHT[n])}</p>' if n in HIGHLIGHT else ''}<blockquote>{e(q)}</blockquote></article>""" for p, a, n, s, q in T)
    return f"""<section><div class="wrap">
 {head('Client stories', 'Athletes who fuel with Marine', tag=None, center=True)}
 <div class="tgrid" style="margin-top:36px">{cards}</div>
 </div></section>"""

# ---------------------------------------------------------------- HOME
def who_i_help():
    """'Nutrition for endurance athletes' cards with photos, linking each sport page (Home and About)."""
    who = [('cycling-nutritionist.html', 'Cyclists', 'Leisure to elite: road, gravel, track, MTB, CX', ('0e1488-2799dd6f68d6413ca857a962316', 'Cyclist riding a quiet country road in winter')),
           ('triathlon-nutritionist.html', 'Triathletes', 'Ironman, 70.3 and shorter races', ('nsplsh-5aa897658f1e4fb8bd88bbd8b1654', 'Triathletes running during a race')),
           ('race-fuelling-plan.html', 'Race day', 'A fuelling plan for your event', ('0e1488-45f685e5e5e54029b7cf7b5211aa', 'Cyclist eating an energy bar during a ride')),
           ('online-sports-nutritionist.html', 'Worldwide', 'Online coaching, wherever you train', ('0e1488-a22022be24dc4c7893882498f30', 'Cyclist with a gravel bike on a hilltop'))]
    return ('<section style="padding-top:24px"><div class="wrap">' + head('Who Marine works with', 'Nutrition for endurance athletes', tag=None, center=True)
                  + '<div class="g4" style="margin-top:32px">' + ''.join(f'<a class="scard panel" href="{h}"><div class="tx"><span class="eyebrow">{e(d)}</span><span class="h3">{e(t)}</span><span class="go">Learn more {ICON["arrow"]}</span></div></a>' for h, t, d, ph in who)
                  + '</div></div></section>')

def home():
    services = [
        ('massage-therapy.html', img('11062b-c7086e8444c14484a9e3ec96b46e', 'Deep Tissue Massage', w=640, h=427), 'Massage Therapy', 'Deep tissue, sports, cupping and Thai massage in Co. Wicklow & Dublin. Currently sold out.'),
        ('yoga.html', img('0e1488-a687b5ba8de7467fa18ece35f8a9', 'Yoga pose on a clifftop by the sea at sunset', w=640, h=424), 'Online Yoga', 'Yin, Vinyasa and yoga for cyclists.'),
        ('recipies.html', img('0e1488-8cee9e1e3ac743dd828b4bd69d89', 'Raspberry Chia Seed pudding', w=640, h=363), 'E-Book', 'Breakfasts to ignite your potential: 38 recipes.'),
        ('workshops.html', f'<span>{ICON["talk"]}</span>', 'Workshops & Talks', 'Nutrition talks for clubs, gyms and teams.'),
    ]
    WHO_I_HELP = who_i_help()
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
{WHO_I_HELP}
{testimonials()}
<section style="padding-top:24px"><div class="wrap">
 {head('More from Vivify Sports', 'Support for the whole athlete', tag=None, center=True)}
 <div class="g4" style="margin-top:32px">{sc}</div></div></section>
{cta('Ready to fuel smarter?', 'A free 30-minute discovery call with Marine to talk about your nutrition, your goals and how you fuel your sport.', 'Book your free call', DISCOVERY)}
"""
    schema = {"@context": "https://schema.org", "@type": "ProfessionalService", "name": "Vivify Sports", "url": LIVE,
              "email": EMAIL, "telephone": PHONE, "areaServed": "Worldwide", "address": {"@type": "PostalAddress", "addressLocality": "Wicklow", "addressCountry": "IE"},
              "founder": {"@type": "Person", "name": "Marine Lenehan", "jobTitle": "Sports Nutritionist"}, "sameAs": [IG, GBP], "vatID": VAT}
    return shell('index.html', body, schema)

# ---------------------------------------------------------------- ABOUT
def about():
    titles = ['Irish National Gravel Champion (2026)', 'Amateur Gravel World Champion (2024)', 'Amateur Gravel European Champion (2023,2024)',
              'Irish National E-Sport Champion (2024, 2025)', 'Irish National Criterium Champion (2024)',
              '<a href="https://www.stickybottle.com/races-results/irelands-lenehan-wins-gran-fondo-european-championships/" target="_blank" rel="noopener">European Gran Fondo Champion (2023)</a>',
              'Podium Elite Irish Road Nationals (2025)', 'Podium Elite Irish TT Nationals (2026)']
    quals = ['MSc in Sports Nutrition – Universidad Europea de Madrid (2025)', 'Professional Diploma in Sports Nutrition – Barça Innovation Hub (2023)',
             'Two years of study in Dietetics &amp; Nutrition (BTS Diététique programme) – CNED, France',   # Marine 18 Nov: studied 2 years, did not sit the exam
             'Diploma in Spa &amp; Wellness and Massage Therapy, European Qualifications Framework level 5 – Suntaya, France (2020–2021)',   # Marine 17 Nov: Suntaya, technicien spa et bien-être + massage, BTS level
             '200-hour Yoga Alliance Teaching Certificate in Vinyasa &amp; Yin Yoga – House of OM (2021)']
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
    # Marine 18 Nov: "update the description of each of my pillars to optimise SEO and look scientific". Same five pillars,
    # rewritten from current sports nutrition consensus (sources listed on the page). Titles: typos fixed, keywords added.
    P = [('IMPROVED ENERGY LEVELS AND PERFORMANCE', [
            'Carbohydrate is the main fuel for moderate- and high-intensity exercise, and your body can only store a limited amount of it as glycogen in your muscles and liver. When your intake does not match the work you do, energy levels, training quality and recovery all suffer.',
            'We match your carbohydrate intake to your training load, from around 3–5 g per kg of body weight on light days to 6–10 g/kg on heavy endurance days, and plan what you eat before, during and after your sessions. Fuelling the work you do is one of the simplest and most effective ways to perform better.']),
         ('WEIGHT MANAGEMENT &amp; BODY COMPOSITION', [
            'Whether you are trying to lose or gain weight, VIVIFY SPORTS will have the personalized solution for you. Each body is built differently and has different needs.',
            'Body weight is regulated by energy balance: the energy you eat compared with the energy you use. Highly processed foods rich in refined carbohydrates, added sugar and fat are high in energy density and low in satiety, so it is easy to eat more than you need. Foods rich in protein and fibre, such as lean protein, vegetables, fruit, legumes and whole grains, are lower in energy density and more filling, so you naturally eat less without feeling hungry.',
            'For athletes, the goal is to change body composition without harming health or performance: a moderate energy deficit with weight loss of around 0.5–1% of body weight per week, a higher protein intake to protect muscle, and enough carbohydrate around key sessions. Eating too little for the training you do (low energy availability) can lead to Relative Energy Deficiency in Sport (REDs), which affects hormones, bone health, immunity and performance.',
            '<b class="callout-inline">BALANCE IS THE KEY</b>']),
         ('STRONGER &amp; LEANER MUSCLES', [
            'Protein provides the amino acids your body uses to repair and build muscle after training. Most athletes benefit from around 1.4–2.0 g of protein per kg of body weight per day, spread across 3–5 meals of roughly 0.3 g/kg (about 20–40 g) each, including a serving in the hours after training.',
            'Leucine-rich sources such as dairy, eggs, meat, fish and soy are particularly effective. Combined with strength training and enough total energy, this supports muscle repair, strength and a leaner body composition.']),
         ('STRENGTHENING THE IMMUNE SYSTEM', [
            'Regular, moderate exercise supports your immune system. But periods of heavy training, competition, travel, poor sleep and low energy intake can temporarily weaken your immune defences and raise the risk of illness, particularly upper respiratory infections.',
            'Nutrition helps you stay healthy: eating enough overall energy, taking in carbohydrate during long and intense sessions, adequate protein, a wide variety of fruit and vegetables, and correcting deficiencies such as vitamin D or iron when blood tests show they are low. Fewer days lost to illness means more consistent training, and consistency is what builds performance.',
            'A balanced diet is the key to a healthy and performing body.']),
         ('A HEALTHY GUT', [
            'Gut health is directly linked to athletic performance. During endurance exercise, blood flow is diverted away from the gut, which is why many athletes experience cramping, nausea or bloating, especially when taking in carbohydrate.',
            'The good news is that the gut is trainable: practising your race fuelling in training increases how much carbohydrate you can absorb and reduces gastrointestinal symptoms. Day to day, a varied diet rich in fibre and plant foods supports a healthy gut microbiome, which plays a role in immune function and inflammation. Before key races, fibre and FODMAP intake can be adjusted to keep your stomach settled.'])]
    SOURCES = ['Thomas, Erdman &amp; Burke (2016). Nutrition and athletic performance: ACSM, Academy of Nutrition and Dietetics and Dietitians of Canada joint position statement.',
               'Jäger et al. (2017). International Society of Sports Nutrition position stand: protein and exercise.',
               'Mountjoy et al. (2023). IOC consensus statement on Relative Energy Deficiency in Sport (REDs).',
               'Walsh (2018). Recommendations to maintain immune health in athletes. European Journal of Sport Science.',
               'Jeukendrup (2017). Training the gut for athletes. Sports Medicine.']
    PH = [('0e1488-2182adb27d8841c4b9d2e42d758', 'Berry and nut porridge, a carbohydrate-rich breakfast for energy'),
          ('11062b-adb55043aa3b41e79df25e7d245', 'Pasta salad with fresh vegetables, a balanced meal'),
          ('protein-salmon-fillets', 'Fresh salmon fillets on a wooden board, a protein-rich food for muscle repair'),
          ('e74ada189a6b4b21badde4860665a1ef', 'Superfood recovery smoothie rich in fruit'),
          ('0e1488-5cd296938d634927be6ebf114c5', 'Bowl of granola with fruit and yogurt')]
    cards = ''.join(f'<div class="pcard panel"{" style=%sgrid-column:span 2%s" % (chr(34), chr(34)) if i == 4 else ""}><div class="ph"{" style=%saspect-ratio:21/7%s" % (chr(34), chr(34)) if i == 4 else ""}>{img(PH[i][0], PH[i][1], w=900, h=506)}</div><span class="num">{i+1}</span><span class="h3">{t}</span>' + ''.join(f'<p>{p}</p>' for p in ps) + '</div>' for i, (t, ps) in enumerate(P))
    body = f"""
<section class="page-hero"><div class="wrap">
 <p class="bigquote" style="font-size:clamp(26px,3.6vw,44px)">"Our food should be our medicine and <span>our medicine should be our food</span>"</p>
 <p class="eyebrow" style="margin-top:18px">Hippocrates</p>
</div></section>
<section style="padding-top:8px"><div class="wrap">
 {head('Sports nutrition philosophy', 'THE VIVIFY SPORTS METHOD', tag='h1', center=True, lead="At Vivify sports, we don't believe in dieting and the main goal is to make healthy eating simple and every meal enjoyable. Every recommendation is based on current sports nutrition science and adapted to your sport, your training and your life.", cls='h2')}
 <div class="g2 phil" style="margin-top:40px;align-items:stretch">{cards}</div>
 <div class="panel" style="padding:22px 26px;margin-top:28px"><span class="eyebrow">Based on current research</span>
  <ul style="margin:6px 0 0;padding-left:20px;font-size:13.5px;color:var(--text-3)">{''.join(f'<li style="margin:4px 0">{x}</li>' for x in SOURCES)}</ul></div>
</div></section>
<style>.callout-inline{{display:inline-block;color:var(--on-aqua);background:var(--aqua);padding:8px 14px;border-radius:8px;font:700 13px Montserrat,sans-serif;letter-spacing:.14em}}
@media (max-width:980px){{.phil>div{{grid-column:auto!important}}}}</style>
{cta('Put the method to work', 'Personalised nutrition coaching built around your training load, goals and lifestyle.', 'See coaching plans', 'sports-nutritionist-ireland.html')}
"""
    return shell('nutrition-nutrition-philosophy.html', body)

# ---------------------------------------------------------------- COACHING
def coaching():
    # Compare table, Cigala Coaching style (Marine 17 Nov): the three plans, short text, ✓ / ✗, popular column highlighted
    Y, N = '<span class="y" aria-label="Included">✓</span>', '<span class="n" aria-label="Not included">✗</span>'
    rows = [('Length', '3 months', '3 months', '3 months'),
            ('Initial assessment call', Y, Y, Y),   # Marine 18 Nov: rows added and confirmed by her
            ('Plan adjusted to your training load <small>(TrainingPeaks, Vekta)</small>', Y, Y, Y),
            ('Number of calls', '3 calls over 3 months', '5 calls over 3 months', 'Unlimited'),
            ('WhatsApp support', Y, Y, 'Daily'),
            ('Weekly Macro Plan <small>(based on your training load)</small>', Y, N, Y),
            ('Weekly Meal Plan <small>(based on your training load)</small>', N, Y, Y),
            ('Food diary review <small>(MyFitnessPal)</small>', 'Weekly', 'Weekly', 'Daily'),
            ('Daily hydration plan', N, Y, Y),
            ('Race fuelling plan', N, Y, Y),
            ('Sweat rate test', Y, Y, Y),
            ('Advice on healthy nutritional habits', Y, Y, Y),
            ('Healthy recipes', N, Y, Y),
            ('Gut health support', N, Y, Y),
            ('Vitamins &amp; minerals requirements', N, N, Y),
            ('Supplements requirements', Y, Y, Y),
            ('Sports-specific requirements', N, Y, Y),
            ('“Breakfasts to ignite your potential” ebook', N, N, Y),
            ('Price', '99€/month<small>119 US$/month</small>', '149€/month<small>180 US$/month</small>', '199€/month<small>240 US$/month · sold out for now</small>')]
    cols = [('The Healthy Body Plan', ''), ('The Happy Body Plan', 'hot'), ('The Performing Body Plan', '')]
    thead = ''.join(f'<th scope="col"{" class=hot" if c else ""}>{n}' + ('<small class="cmp-badge">Most popular</small>' if c else '<small class="cmp-badge sold">Sold out</small>' if 'Performing' in n else '') + '</th>' for n, c in cols)
    trs = ''.join('<tr' + (' class="price"' if r[0] == 'Price' else '') + f'><th scope="row">{r[0]}</th>'
                  + ''.join(f'<td{" class=hot" if cols[k][1] else ""} data-l="{("Healthy", "Happy", "Performing")[k]}">{v}</td>' for k, v in enumerate(r[1:])) + '</tr>' for r in rows)
    table = f"""<div class="cmp-scroll"><table class="cmp2"><caption class="skip">Vivify Sports coaching plans compared</caption>
<thead><tr><th scope="col"><span class="skip">Feature</span></th>{thead}</tr></thead>
<tbody>{trs}</tbody></table></div>
<p class="cmp-note">The Nutritional Assessment and Follow-up Consultation are single sessions: see above.</p>"""

    def plan(name, price, dur, intro, inc, btn, href, usd='', feat=False, extra='', sold_out=False, big=None, more=''):
        """Cigala Coaching style card. The H2 text stays the live Wix wording, e.g. "THE HEALTHY BODY PLAN - 99€/MONTH 3 months";
        CSS lays it out as duration label, plan name, big price."""
        ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
        if dur:   # monthly plans: name, hidden " - ", price, duration
            amount, per = price.split('/', 1)
            h2 = (f'<h2 class="pt"><span class="pn">{name}</span><span class="skip"> - </span><span class="pp"><b>{amount}</b><small class="m">/{per}</small></span>'
                  f' <span class="pd">{dur}</span></h2>')
        else:     # single sessions: "NAME 50mn 100€ / 120 US$"
            mins, rest = price.split(' ', 1)
            h2 = (f'<h2 class="pt"><span class="pn">{name}</span> <span class="pd">{mins}</span> <span class="pp"><b>{rest.split(" / ")[0]}</b>'
                  f'<small> / {rest.split(" / ")[1]}</small></span></h2>')
        badge = ('<span class="pbadge sold">Sold out for now</span>' if sold_out else '<span class="pbadge">Most popular</span>' if feat else '')
        if sold_out:
            cta_ = '<span class="btn btn-secondary pbtn" aria-disabled="true" style="cursor:default">Sold out for now</span>'
        else:
            # Marine 18 Nov: all plan sign-ups the same colour; single sessions (assessment, follow-up) in lime to stand apart
            cta_ = f'<a class="btn {"btn-primary" if dur else "btn-lime"} pbtn" href="{href}"{ext}>{btn}</a>'
            if href.startswith('https://buy.stripe.com'):   # Marine 17 Nov: Stripe confirmation links to her Cal.com calendar
                cta_ += '<p class="after">Pay online, then choose your time in Marine’s calendar.</p>'
            elif href.startswith('https://cal.com/') and href != DISCOVERY:   # Cal.com paid event
                cta_ += '<p class="after">Choose your time and pay in one step.</p>'
        return (f'<article class="plan panel{" feat" if feat else ""}{" soldout" if sold_out else ""}">{badge}{h2}'
                + (f'<p class="usd">{usd}</p>' if usd else '') + extra + f'<p class="pdesc">{intro}</p>{cta_}'
                + f'<a class="notsure" href="{DISCOVERY}">Not sure? Book a free discovery call →</a>'
                + f'<p class="wyg">What you get</p>{ticks(inc)}{more}</article>')
    # Marine 17 Nov: "improve the description like other competitors". Only what the live page already promises;
    # the three live paragraphs about the assessment (missing from the first rebuild) are back, word for word.
    one = plan('NUTRITIONAL ASSESEMENT', '50mn 100€ / 120 US$', '',
               'A complete evaluation to understand your current nutrition, goals, and needs. The ideal first step: one private session with Marine and a full written report you can keep.',
               ['A 50-minute private online consultation with Marine', 'A review of your eating habits, training and goals',
                'Personalized advice on healthy habits and food preferences', 'Vitamin &amp; mineral recommendations', 'Supplement guidance',
                'Sports-specific nutrition', 'Your Full Nutritional Assessment Report'], 'Book now', ASSESSMENT_PAY)   # Marine 17 Nov: 'How the assessment works' removed
    two = plan('FOLLOW-UP CONSULTATION', '30mn 50€ / 60 US$', '', 'A session to review your progress, fine-tune your plan, and stay on track.',
               ['1 follow-up call', 'Updated nutritional and supplement advice'], 'Book now', FOLLOWUP_PAY)
    p1 = plan('THE HEALTHY BODY PLAN', '99€/MONTH', '3 months', 'Build sustainable, healthy eating habits that energize your everyday life.',
              ['3 calls over 3 months', 'WhatsApp support', 'Weekly macro plan based on your training load', 'Weekly food diary analysis', 'Advice on balanced nutrition', 'Supplement advice'], 'Sign up', PAY['healthy'], usd='119 US$ a month')
    p2 = plan('THE HAPPY BODY PLAN', '149€/MONTH', '3 months', 'Create harmony between your nutrition, mood, and lifestyle to bring out the best of you.',
              ['5 calls over 3 months', 'WhatsApp support', 'Weekly meal plan tailored to your training', 'Weekly food diary analysis', 'Advice on balanced nutrition, vitamins and supplements', 'Daily Support &amp; Motivation'], 'Sign up', PAY['happy'], usd='180 US$ a month', feat=True)
    p3 = plan('THE PERFORMING BODY PLAN', '199€/MONTH', '3 months', 'Maximize performance and recovery with a fully personalized approach.',
              ['Unlimited coaching calls', 'Daily WhatsApp support', 'Weekly meal &amp; macro plan', 'Daily food diary analysis', 'Vitamin, supplement &amp; sports-specific optimization', 'Exclusive ebook: "Breakfast to Ignite your potential"'],
              'Sign up', PAY['performing'], usd='240 US$ a month', sold_out=True, extra='<h2 class="psub">SPORTS SPECIFIC REQUIMENTS</h2>')
    notes = ''.join(f'<div class="note">{t}</div>' for t in [
        'Partnered with TrainingPeaks, Vekta &amp; MyFitnessPal: your plan follows your training load every week.',
        'Prices in euro and US dollars. Coaching online in English, French and Italian.',
        'Not sure which plan suits you? Start with a free 30-minute discovery call.'])
    partners = [('0e1488-356941ca85c445f1834a69b48ccf', 'TrainingPeaks logo', None), ('0e1488-a23fdd6bc1854f5a83c28cb05ea9', 'MyFitnessPal logo', None),
                ('0e1488-e926906d84424b06892a7eb7a3b6', 'Cigala Cycling logo', 'https://www.cigalacycling.com/'),
                ('vekta-logo', 'Vekta logo', None), ('0e1488-44c2783c595b4fcba972291cd77f', 'Wicklow 200 logo', None)]   # Marine 17 Nov: + Vekta, - Bryan McKinney
    pl = ''.join((f'<a href="{u}" target="_blank" rel="noopener">' if u else '<span>') + img(p, a, w=150, h=72, style='width:auto') + ('</a>' if u else '</span>') for p, a, u in partners)
    body = f"""
<section class="hero" style="min-height:min(72vh,620px)">
 {img('0e1488-26eed664485245b6b26c855875ee', 'Road cyclist riding through a forest', lazy=False, w=1600, h=1067)}
 <div class="wrap"><span class="pill">Sports Nutritionist Ireland</span><h1>ONLINE NUTRITION COACHING</h1>
  <p class="lead">Ever wish you could have your own nutritionist that will tell you exactly what to do and be there with you every step of the way?</p>
  <div style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-primary" href="{DISCOVERY}">Book a free discovery call {ICON['arrow']}</a><a class="btn btn-secondary" href="#plans">Compare plans ↓</a></div></div>
</section>
<section style="padding-top:16px"><div class="wrap g2" style="align-items:start">
 <div>{head('Personalised coaching', 'PERSONALIZED NUTRITION PLANS FOR YOU')}
  <p>As an athlete, you want to train hard, compete and be successful. Nutrition will help you do that. Your nutrition requirements are determined by your sport, your training &amp; your genetic make-up.These coaching plans are designed to give you personalized support to reach your goals. Partnered with Training Peaks, Vekta &amp; MyFitnessPal, Marine will build your nutrition plan weekly according to your training load. You will know exactly what to eat on &amp; off training. Whether you are looking to clean up your diet a bit, increase performance, support training adaptations, support your gut health, boost your energy levels or simply have a healthy relationship to food, VIFIFY SPORTS is here to help.</p>
  <p>By assessing your dietary patterns, relationship to food, macronutrient &amp; micronutrient balance, VIVIFY SPORTS will give you tailored solutions to reach your goals.</p></div>
 <div><div class="side-photo">{img('0e1488-45f685e5e5e54029b7cf7b5211aa', 'Cyclist eating an energy bar during a ride', w=900, h=563)}</div>
 <div class="panel" style="padding:32px"><span class="eyebrow">What we look at</span>
  {chips(['Macronutrients requirements', 'Vitamins &amp; Minerals requirements', 'Supplements requirements', 'Sports specific requirements', 'Lifestyle advice', 'Healthy recipes', 'Craving control guidelines', 'IBS or gastro-intestinal issues', 'Immune health'])}</div>
</div></div></section>
{EX.section(head, DISCOVERY)}
<section class="section-tight" style="padding-top:8px"><div class="wrap"><div class="pstrip">
 <figure>{img('0e1488-2182adb27d8841c4b9d2e42d758', 'Berry and nut porridge', w=600, h=750)}<figcaption>Fuel your training</figcaption></figure>
 <figure>{img('0e1488-0f8685dc06d3448fb873620002d', 'Fish with roasted vegetables and asparagus', w=600, h=750)}<figcaption>Recover well</figcaption></figure>
 <figure>{img('e74ada189a6b4b21badde4860665a1ef', 'Superfood recovery smoothie', w=600, h=750)}<figcaption>Stay healthy</figcaption></figure>
 <figure>{img('0e1488-1a90881d935c4aa0bb75472c0e9', 'Healthy Greek yogurt pancakes with berries', w=600, h=750)}<figcaption>Enjoy every meal</figcaption></figure>
</div></div></section>
<section id="plans" style="padding-top:24px"><div class="wrap">
 {head('3-month coaching', 'Find the right plan', tag=None, center=True)}
 <div class="notes">{notes}</div>
 <div class="plans" style="margin-top:34px">{p1}{p2}{p3}</div>
 <div style="margin-top:64px">{head('Single sessions', 'One-off consultations', tag=None)}</div>
 <div class="plans two" style="margin-top:10px">{one}{two}</div>
 <div style="margin-top:64px">{head('Side by side', 'Compare plans', tag=None)}</div>
 <div style="margin-top:6px">{table}</div>
</div></section>
<section style="padding-top:8px"><div class="wrap"><div class="cta">
 <div><span class="eyebrow">Race day</span><h2>FUELLING PLAN</h2><span class="bar"></span>
  <p>As an athlete, you want to train hard, compete and be successful. Nutrition is almost as important as your training load to bring your performance to the next level. Fuelling for an event can be quite a headache. Remember bonking out half way through your event ?</p>
  <p style="margin:0">Let Marine help you to secure optimal performance by building a fuelling plan that is right for you giving you a precise plan to follow based on your sport, gender, weight &amp; metabolism.</p></div>
 <div><a class="btn btn-primary" href="race-fuelling-plan.html">Book your fuelling plan here {ICON['arrow']}</a></div></div></div></section>
<section class="section-tight"><div class="wrap center">
 {head('Training Peaks · Vekta · MyFitnessPal', 'OUR PARTNERS', center=True)}
 <div class="partners" style="margin-top:24px">{pl}</div></div></section>
{testimonials(names={'Matteo Cigala,Italy': 'Matteo Cigala, Italy', 'Road & Gravel cyclistMatteo Cigala,Italy': 'Road & Gravel Cyclist', 'Damian Maloney, Ireland': 'Damian Maloney,Ireland', 'Road cyclistIwan Harmsen, Netherlands': 'Road Cyclist'})}
{google_reviews()}
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
<section class="hero" style="min-height:min(66vh,580px)">
 {img('nsplsh-5aa897658f1e4fb8bd88bbd8b1654', 'Triathletes running during a race', lazy=False, w=1600, h=1067)}
 <div class="wrap"><span class="pill">Clubs · Gyms · Teams</span><h1>WORKSHOPS &amp; TALKS</h1>
 <p class="lead">If you have a competitive sports club or gym &amp; want to improve nutrition practices, Marine can come and talk to your athletes &amp; coaches on optimizing nutrition for training and competitions.</p>
 <a class="btn btn-primary" href="contact.html">Book a talk {ICON['arrow']}</a></div>
</section>
<section style="padding-top:8px"><div class="wrap g2" style="align-items:start">
 <div><div class="side-photo">{img('workshop-nutrition-talk', 'Speaker holding an apple during a nutrition talk', w=1024, h=826)}</div>
 <div class="panel" style="padding:36px"><span style="color:var(--aqua)">{ICON['talk']}</span>
  <p class="lead" style="margin-top:16px">Often this is a good way to help athletes improve on their sports performance as well as find out the latest guidelines on sports nutrition.</p>
  <p class="muted" style="margin:0">In person or online, for athletes, coaches and staff.</p></div></div>
 <div>{head('Who it is for', "Marine's area of expertise :", tag=None)}
  {chips(['Cycling clubs', 'Triathlon clubs', 'Running clubs', 'Swimming clubs', 'Athletic clubs', 'Gym members &amp; staff', 'Team Sports'])}</div>
</div></section>
{cta('Book a talk for your club', 'Tell Marine about your club, your athletes and the topics you want covered.', 'Get in touch', 'contact.html')}"""
    return shell('workshops.html', body)

# ---------------------------------------------------------------- E-BOOK
def ebook():
    body = f"""
<section style="padding-top:72px"><div class="wrap g2">
 <div class="ebgrid">
  <div class="portrait ebcover" style="grid-row:span 2;position:relative">{img('ebook-cover', 'Cover of the Vivify Sports e-book Breakfasts to Ignite Your Potential', lazy=False, w=1075, h=1521)}<span class="ebbadge"><b>38</b> recipes</span></div>
  <div class="portrait ebpage">{img('ebook-page-raspberry-chia', 'Raspberry Chia Seed pudding', w=1075, h=1521)}</div>
  <div class="portrait ebpage">{img('ebook-page-blueberry-pancakes', 'Blueberry Buttermilk Pancakes', w=1075, h=1521)}</div>
 </div>
 <div><span class="eyebrow">E-Book</span><h1 style="font-size:clamp(38px,5vw,62px)">BREAKFATS TO IGNITE YOUR POTENTIAL</h1><span class="bar"></span>
  <p style="font:600 18px/1.5 Montserrat,sans-serif;color:var(--text);font-style:italic">"Healthy recipes to keep you fuelled &amp; happy "</p>
  <p>A downloadable book to inspire your mornings. From sweet to savoury, there are recipes for every pallet.</p>
  <p>Breakfast lives up to its reputation as the most important meal of the day. Your first meal of the day can have long lasting effects throughout your day and on your long-term health.</p>
  <p style="color:var(--text);font-weight:700;margin-bottom:6px">What's included ?</p>
  {ticks(['38 recipes', 'Method', 'Ingredients list', 'Nutritional information'])}
  <div style="display:flex;align-items:center;gap:22px;margin-top:26px;flex-wrap:wrap"><span class="h2" style="font-size:44px">5.99€</span>
   <a class="btn btn-primary" href="{EBOOK_PAY}" target="_blank" rel="noopener">Buy now {ICON['arrow']}</a></div></div>
</div></section>"""
    schema = {"@context": "https://schema.org", "@type": "Product", "name": "Breakfasts to Ignite Your Potential (e-book)",
              "brand": {"@type": "Brand", "name": "Vivify Sports"}, "offers": {"@type": "Offer", "price": "5.99", "priceCurrency": "EUR", "url": EBOOK_PAY, "availability": "https://schema.org/InStock"}}
    return shell('recipies.html', body, schema)

# ---------------------------------------------------------------- BLOG
def norm(s):
    return re.sub(r'[^a-z0-9]+', '', html.unescape(s).lower())

MISSING_FROM_SITEMAP = {'Iron Deficiency, Anemia and Performance': LIVE + '/post/iron-deficiency-anemia-and-performance'}  # live 200, not in Wix sitemap

# Marine 19 Nov: every post gets a photo (these three had none on Wix); free CC0/public-domain photos
NO_IMG_FIX = {'Why Am I So Tired After Exercise? Understanding Post-Exercise Fatigue in Endurance Athletes': 'blog-post-exercise-fatigue',
              'Intermittent Fasting for Athletes: Benefits, Risks, and Performance Insights': 'blog-intermittent-fasting',
              '“From Curiosity to Clarity: A Journey into Recovery Nutrition”': 'blog-tart-cherry-recovery'}

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
            posts.append(dict(title=title, ex=ex, date=date, read=read, url=url, img=by_alt.get(norm(title)) or NO_IMG_FIX.get(title)))
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
        ph = img(p['img'], p['title'], w=640, h=400) if p['img'] else ''
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
<section class="hero" style="min-height:min(56vh,480px)">
 {img('0e1488-a22022be24dc4c7893882498f30', 'Cyclist with a gravel bike on a hilltop', lazy=False, w=1200, h=1600, style='object-position:50% 30%')}
 <div class="wrap"><span class="pill">Sports nutrition consultation</span><h1>Contact</h1>
 <p class="lead">Contact Vivify Sports for personalised sports nutrition support.</p></div>
</section>
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
  {img('0e1488-5ffa2e2730204ef0bae918a9e4ae', 'Marine Lenehan, MSc Sports Nutritionist and founder of Vivify Sports', w=120, h=120, style='margin:0 auto 18px;border-radius:50%;width:120px;height:120px;object-fit:cover;border:2px solid var(--aqua)')}
  <h2 style="font-size:clamp(28px,3.4vw,40px)">Vivify Sport's Discovery Call</h2><span class="bar"></span>
  <p class="muted" style="display:flex;gap:8px;align-items:center;justify-content:center">{ICON['clock']} 30 min</p>
  <p style="max-width:520px;margin:0 auto 6px">A free 30-minute video call with Marine to talk about your sport, your goals and how you fuel today, and to find out which coaching option suits you. No commitment.</p>
  <a class="btn btn-primary" href="{BOOK_CAL}" target="_blank" rel="noopener">Book Now {ICON['arrow']}</a>
 </div></div></section>
<section style="padding-top:8px"><div class="wrap">
 <div class="g3">
  <div class="pcard panel"><span class="num">1</span><span class="h3">Pick a time</span><p style="margin:0">Choose a slot in Marine's calendar that suits you. You get a video link by email.</p></div>
  <div class="pcard panel"><span class="num">2</span><span class="h3">Talk it through</span><p style="margin:0">Your training, your events, what you eat now and what you want to change: performance, energy, weight or gut comfort.</p></div>
  <div class="pcard panel"><span class="num">3</span><span class="h3">Your next step</span><p style="margin:0">Marine suggests the right option for you: a coaching plan, a one-off assessment or a race fuelling plan.</p></div>
 </div></div></section>
<section style="padding-top:8px"><div class="wrap g2" style="align-items:center">
 <div class="side-photo" style="margin:0">{img('0e1488-45f685e5e5e54029b7cf7b5211aa', 'Cyclist eating an energy bar during a ride', w=900, h=563)}</div>
 <div><span class="eyebrow">Who it is for</span><span class="h2" style="display:block;font-size:clamp(26px,3vw,36px)">Endurance athletes at every level</span><span class="bar"></span>
  {ticks(['Cyclists: road, gravel, track, MTB and cyclocross', 'Triathletes and runners', 'Beginners to elite and professional riders', 'Online, worldwide, in English, French or Italian'])}</div>
</div></section>"""
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

EXTRA_CSS = r"""
/* Marine 18-19 Nov: background pattern (flowing wavy lines, our own drawing), stronger hover lift, yellow Google stars, single-session buttons */
.vv-pattern,.page-hero,.cta,.intro .feature{position:relative;isolation:isolate}
.vv-pattern::before,.page-hero::before,.cta::before,.intro .feature::before{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;border-radius:inherit;background:url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="480" height="240" viewBox="0 0 480 240" fill="none" stroke="%23B1D8DD" stroke-width="1.3" stroke-linecap="round"%3E%3Cpath d="M0 10.0 L8 11.8 L16 13.6 L24 15.2 L32 16.6 L40 17.7 L48 18.5 L56 19.0 L64 19.2 L72 19.1 L80 18.8 L88 18.3 L96 17.7 L104 17.0 L112 16.3 L120 15.6 L128 15.0 L136 14.4 L144 14.0 L152 13.6 L160 13.3 L168 13.1 L176 12.8 L184 12.6 L192 12.4 L200 12.1 L208 11.8 L216 11.4 L224 11.0 L232 10.5 L240 10.0 L248 9.5 L256 9.0 L264 8.6 L272 8.2 L280 7.9 L288 7.6 L296 7.4 L304 7.2 L312 6.9 L320 6.7 L328 6.4 L336 6.0 L344 5.6 L352 5.0 L360 4.4 L368 3.7 L376 3.0 L384 2.3 L392 1.7 L400 1.2 L408 0.9 L416 0.8 L424 1.0 L432 1.5 L440 2.3 L448 3.4 L456 4.8 L464 6.4 L472 8.2 L480 10.0"/%3E%3Cpath d="M0 32.1 L8 33.1 L16 33.9 L24 34.7 L32 35.4 L40 36.1 L48 36.6 L56 37.1 L64 37.6 L72 38.0 L80 38.4 L88 38.7 L96 38.9 L104 39.0 L112 39.0 L120 38.8 L128 38.5 L136 37.9 L144 37.1 L152 36.1 L160 34.9 L168 33.5 L176 32.0 L184 30.4 L192 28.8 L200 27.2 L208 25.8 L216 24.5 L224 23.5 L232 22.8 L240 22.3 L248 22.2 L256 22.3 L264 22.7 L272 23.2 L280 23.9 L288 24.7 L296 25.5 L304 26.2 L312 26.7 L320 27.2 L328 27.4 L336 27.5 L344 27.3 L352 27.1 L360 26.7 L368 26.3 L376 25.9 L384 25.5 L392 25.2 L400 25.1 L408 25.2 L416 25.4 L424 25.8 L432 26.5 L440 27.2 L448 28.1 L456 29.1 L464 30.1 L472 31.1 L480 32.1"/%3E%3Cpath d="M0 53.3 L8 52.9 L16 52.7 L24 52.5 L32 52.6 L40 52.8 L48 53.3 L56 53.8 L64 54.5 L72 55.3 L80 56.1 L88 56.8 L96 57.3 L104 57.7 L112 57.8 L120 57.7 L128 57.2 L136 56.5 L144 55.5 L152 54.2 L160 52.8 L168 51.2 L176 49.6 L184 48.0 L192 46.5 L200 45.1 L208 43.9 L216 42.9 L224 42.1 L232 41.5 L240 41.2 L248 41.0 L256 41.0 L264 41.1 L272 41.3 L280 41.6 L288 42.0 L296 42.4 L304 42.9 L312 43.4 L320 43.9 L328 44.6 L336 45.3 L344 46.1 L352 46.9 L360 47.9 L368 48.9 L376 49.9 L384 50.9 L392 51.9 L400 52.8 L408 53.5 L416 54.2 L424 54.6 L432 54.8 L440 54.9 L448 54.8 L456 54.5 L464 54.1 L472 53.7 L480 53.3"/%3E%3Cpath d="M0 75.6 L8 75.0 L16 74.4 L24 74.0 L32 73.6 L40 73.3 L48 73.1 L56 72.8 L64 72.6 L72 72.4 L80 72.1 L88 71.8 L96 71.4 L104 71.0 L112 70.5 L120 70.0 L128 69.5 L136 69.0 L144 68.6 L152 68.2 L160 67.9 L168 67.6 L176 67.4 L184 67.2 L192 66.9 L200 66.7 L208 66.4 L216 66.0 L224 65.6 L232 65.0 L240 64.4 L248 63.7 L256 63.0 L264 62.3 L272 61.7 L280 61.2 L288 60.9 L296 60.8 L304 61.0 L312 61.5 L320 62.3 L328 63.4 L336 64.8 L344 66.4 L352 68.2 L360 70.0 L368 71.8 L376 73.6 L384 75.2 L392 76.6 L400 77.7 L408 78.5 L416 79.0 L424 79.2 L432 79.1 L440 78.8 L448 78.3 L456 77.7 L464 77.0 L472 76.3 L480 75.6"/%3E%3Cpath d="M0 98.8 L8 98.5 L16 97.9 L24 97.1 L32 96.1 L40 94.9 L48 93.5 L56 92.0 L64 90.4 L72 88.8 L80 87.2 L88 85.8 L96 84.5 L104 83.5 L112 82.8 L120 82.3 L128 82.2 L136 82.3 L144 82.7 L152 83.2 L160 83.9 L168 84.7 L176 85.5 L184 86.2 L192 86.7 L200 87.2 L208 87.4 L216 87.5 L224 87.3 L232 87.1 L240 86.7 L248 86.3 L256 85.9 L264 85.5 L272 85.2 L280 85.1 L288 85.2 L296 85.4 L304 85.8 L312 86.5 L320 87.2 L328 88.1 L336 89.1 L344 90.1 L352 91.1 L360 92.1 L368 93.1 L376 93.9 L384 94.7 L392 95.4 L400 96.1 L408 96.6 L416 97.1 L424 97.6 L432 98.0 L440 98.4 L448 98.7 L456 98.9 L464 99.0 L472 99.0 L480 98.8"/%3E%3Cpath d="M0 117.7 L8 117.2 L16 116.5 L24 115.5 L32 114.2 L40 112.8 L48 111.2 L56 109.6 L64 108.0 L72 106.5 L80 105.1 L88 103.9 L96 102.9 L104 102.1 L112 101.5 L120 101.2 L128 101.0 L136 101.0 L144 101.1 L152 101.3 L160 101.6 L168 102.0 L176 102.4 L184 102.9 L192 103.4 L200 103.9 L208 104.6 L216 105.3 L224 106.1 L232 106.9 L240 107.9 L248 108.9 L256 109.9 L264 110.9 L272 111.9 L280 112.8 L288 113.5 L296 114.2 L304 114.6 L312 114.8 L320 114.9 L328 114.8 L336 114.5 L344 114.1 L352 113.7 L360 113.3 L368 112.9 L376 112.7 L384 112.5 L392 112.6 L400 112.8 L408 113.3 L416 113.8 L424 114.5 L432 115.3 L440 116.1 L448 116.8 L456 117.3 L464 117.7 L472 117.8 L480 117.7"/%3E%3Cpath d="M0 130.0 L8 129.5 L16 129.0 L24 128.6 L32 128.2 L40 127.9 L48 127.6 L56 127.4 L64 127.2 L72 126.9 L80 126.7 L88 126.4 L96 126.0 L104 125.6 L112 125.0 L120 124.4 L128 123.7 L136 123.0 L144 122.3 L152 121.7 L160 121.2 L168 120.9 L176 120.8 L184 121.0 L192 121.5 L200 122.3 L208 123.4 L216 124.8 L224 126.4 L232 128.2 L240 130.0 L248 131.8 L256 133.6 L264 135.2 L272 136.6 L280 137.7 L288 138.5 L296 139.0 L304 139.2 L312 139.1 L320 138.8 L328 138.3 L336 137.7 L344 137.0 L352 136.3 L360 135.6 L368 135.0 L376 134.4 L384 134.0 L392 133.6 L400 133.3 L408 133.1 L416 132.8 L424 132.6 L432 132.4 L440 132.1 L448 131.8 L456 131.4 L464 131.0 L472 130.5 L480 130.0"/%3E%3Cpath d="M0 142.3 L8 142.2 L16 142.3 L24 142.7 L32 143.2 L40 143.9 L48 144.7 L56 145.5 L64 146.2 L72 146.7 L80 147.2 L88 147.4 L96 147.5 L104 147.3 L112 147.1 L120 146.7 L128 146.3 L136 145.9 L144 145.5 L152 145.2 L160 145.1 L168 145.2 L176 145.4 L184 145.8 L192 146.5 L200 147.2 L208 148.1 L216 149.1 L224 150.1 L232 151.1 L240 152.1 L248 153.1 L256 153.9 L264 154.7 L272 155.4 L280 156.1 L288 156.6 L296 157.1 L304 157.6 L312 158.0 L320 158.4 L328 158.7 L336 158.9 L344 159.0 L352 159.0 L360 158.8 L368 158.5 L376 157.9 L384 157.1 L392 156.1 L400 154.9 L408 153.5 L416 152.0 L424 150.4 L432 148.8 L440 147.2 L448 145.8 L456 144.5 L464 143.5 L472 142.8 L480 142.3"/%3E%3Cpath d="M0 161.2 L8 161.0 L16 161.0 L24 161.1 L32 161.3 L40 161.6 L48 162.0 L56 162.4 L64 162.9 L72 163.4 L80 163.9 L88 164.6 L96 165.3 L104 166.1 L112 166.9 L120 167.9 L128 168.9 L136 169.9 L144 170.9 L152 171.9 L160 172.8 L168 173.5 L176 174.2 L184 174.6 L192 174.8 L200 174.9 L208 174.8 L216 174.5 L224 174.1 L232 173.7 L240 173.3 L248 172.9 L256 172.7 L264 172.5 L272 172.6 L280 172.8 L288 173.3 L296 173.8 L304 174.5 L312 175.3 L320 176.1 L328 176.8 L336 177.3 L344 177.7 L352 177.8 L360 177.7 L368 177.2 L376 176.5 L384 175.5 L392 174.2 L400 172.8 L408 171.2 L416 169.6 L424 168.0 L432 166.5 L440 165.1 L448 163.9 L456 162.9 L464 162.1 L472 161.5 L480 161.2"/%3E%3Cpath d="M0 184.4 L8 183.7 L16 183.0 L24 182.3 L32 181.7 L40 181.2 L48 180.9 L56 180.8 L64 181.0 L72 181.5 L80 182.3 L88 183.4 L96 184.8 L104 186.4 L112 188.2 L120 190.0 L128 191.8 L136 193.6 L144 195.2 L152 196.6 L160 197.7 L168 198.5 L176 199.0 L184 199.2 L192 199.1 L200 198.8 L208 198.3 L216 197.7 L224 197.0 L232 196.3 L240 195.6 L248 195.0 L256 194.4 L264 194.0 L272 193.6 L280 193.3 L288 193.1 L296 192.8 L304 192.6 L312 192.4 L320 192.1 L328 191.8 L336 191.4 L344 191.0 L352 190.5 L360 190.0 L368 189.5 L376 189.0 L384 188.6 L392 188.2 L400 187.9 L408 187.6 L416 187.4 L424 187.2 L432 186.9 L440 186.7 L448 186.4 L456 186.0 L464 185.6 L472 185.0 L480 184.4"/%3E%3Cpath d="M0 206.7 L8 206.3 L16 205.9 L24 205.5 L32 205.2 L40 205.1 L48 205.2 L56 205.4 L64 205.8 L72 206.5 L80 207.2 L88 208.1 L96 209.1 L104 210.1 L112 211.1 L120 212.1 L128 213.1 L136 213.9 L144 214.7 L152 215.4 L160 216.1 L168 216.6 L176 217.1 L184 217.6 L192 218.0 L200 218.4 L208 218.7 L216 218.9 L224 219.0 L232 219.0 L240 218.8 L248 218.5 L256 217.9 L264 217.1 L272 216.1 L280 214.9 L288 213.5 L296 212.0 L304 210.4 L312 208.8 L320 207.2 L328 205.8 L336 204.5 L344 203.5 L352 202.8 L360 202.3 L368 202.2 L376 202.3 L384 202.7 L392 203.2 L400 203.9 L408 204.7 L416 205.5 L424 206.2 L432 206.7 L440 207.2 L448 207.4 L456 207.5 L464 207.3 L472 207.1 L480 206.7"/%3E%3Cpath d="M0 227.9 L8 228.9 L16 229.9 L24 230.9 L32 231.9 L40 232.8 L48 233.5 L56 234.2 L64 234.6 L72 234.8 L80 234.9 L88 234.8 L96 234.5 L104 234.1 L112 233.7 L120 233.3 L128 232.9 L136 232.7 L144 232.5 L152 232.6 L160 232.8 L168 233.3 L176 233.8 L184 234.5 L192 235.3 L200 236.1 L208 236.8 L216 237.3 L224 237.7 L232 237.8 L240 237.7 L248 237.2 L256 236.5 L264 235.5 L272 234.2 L280 232.8 L288 231.2 L296 229.6 L304 228.0 L312 226.5 L320 225.1 L328 223.9 L336 222.9 L344 222.1 L352 221.5 L360 221.2 L368 221.0 L376 221.0 L384 221.1 L392 221.3 L400 221.6 L408 222.0 L416 222.4 L424 222.9 L432 223.4 L440 223.9 L448 224.6 L456 225.3 L464 226.1 L472 226.9 L480 227.9"/%3E%3C/svg%3E') repeat;background-size:480px auto;opacity:.09}
.page-hero::before{-webkit-mask-image:linear-gradient(180deg,#000 40%,transparent);mask-image:linear-gradient(180deg,#000 40%,transparent)}
.cta::before,.intro .feature::before{opacity:.12}
@media (hover:hover){
 .pcard,.tcard,.plan,.scard,.bcard,.intro>div,.notes .note,.flagcard{transition:transform .35s cubic-bezier(.2,.7,.2,1),border-color .3s,box-shadow .35s}
 .pcard:hover,.tcard:hover,.plan:hover,.scard:hover,.bcard:hover,.intro>div:hover,.notes .note:hover{transform:translateY(-6px);border-color:rgba(177,216,221,.5);box-shadow:0 22px 46px rgba(0,0,0,.4),0 0 0 1px rgba(177,216,221,.1)}
 .scard .ph img,.pcard .ph img,.pstrip img{transition:transform .8s cubic-bezier(.2,.7,.2,1)}
 .scard:hover .ph img,.pcard:hover .ph img,.pstrip figure:hover img{transform:scale(1.06)}
}
footer.site .gstars{display:inline-flex;gap:1px;color:#FBBC04}
footer.site .gstars svg{width:15px;height:15px}
.btn-lime{background:var(--lime);color:#0C2226;border-color:var(--lime)}
.btn-lime:hover{background:#93b81c;border-color:#93b81c;color:#0C2226;transform:translateY(-1px);box-shadow:0 10px 26px rgba(128,163,21,.3)}
/* Marine 19 Nov: the same pattern, very faint, across the whole site background (fixed, behind everything) */
body{position:relative}
body::before{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;background:url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="480" height="240" viewBox="0 0 480 240" fill="none" stroke="%23B1D8DD" stroke-width="1.3" stroke-linecap="round"%3E%3Cpath d="M0 10.0 L8 11.8 L16 13.6 L24 15.2 L32 16.6 L40 17.7 L48 18.5 L56 19.0 L64 19.2 L72 19.1 L80 18.8 L88 18.3 L96 17.7 L104 17.0 L112 16.3 L120 15.6 L128 15.0 L136 14.4 L144 14.0 L152 13.6 L160 13.3 L168 13.1 L176 12.8 L184 12.6 L192 12.4 L200 12.1 L208 11.8 L216 11.4 L224 11.0 L232 10.5 L240 10.0 L248 9.5 L256 9.0 L264 8.6 L272 8.2 L280 7.9 L288 7.6 L296 7.4 L304 7.2 L312 6.9 L320 6.7 L328 6.4 L336 6.0 L344 5.6 L352 5.0 L360 4.4 L368 3.7 L376 3.0 L384 2.3 L392 1.7 L400 1.2 L408 0.9 L416 0.8 L424 1.0 L432 1.5 L440 2.3 L448 3.4 L456 4.8 L464 6.4 L472 8.2 L480 10.0"/%3E%3Cpath d="M0 32.1 L8 33.1 L16 33.9 L24 34.7 L32 35.4 L40 36.1 L48 36.6 L56 37.1 L64 37.6 L72 38.0 L80 38.4 L88 38.7 L96 38.9 L104 39.0 L112 39.0 L120 38.8 L128 38.5 L136 37.9 L144 37.1 L152 36.1 L160 34.9 L168 33.5 L176 32.0 L184 30.4 L192 28.8 L200 27.2 L208 25.8 L216 24.5 L224 23.5 L232 22.8 L240 22.3 L248 22.2 L256 22.3 L264 22.7 L272 23.2 L280 23.9 L288 24.7 L296 25.5 L304 26.2 L312 26.7 L320 27.2 L328 27.4 L336 27.5 L344 27.3 L352 27.1 L360 26.7 L368 26.3 L376 25.9 L384 25.5 L392 25.2 L400 25.1 L408 25.2 L416 25.4 L424 25.8 L432 26.5 L440 27.2 L448 28.1 L456 29.1 L464 30.1 L472 31.1 L480 32.1"/%3E%3Cpath d="M0 53.3 L8 52.9 L16 52.7 L24 52.5 L32 52.6 L40 52.8 L48 53.3 L56 53.8 L64 54.5 L72 55.3 L80 56.1 L88 56.8 L96 57.3 L104 57.7 L112 57.8 L120 57.7 L128 57.2 L136 56.5 L144 55.5 L152 54.2 L160 52.8 L168 51.2 L176 49.6 L184 48.0 L192 46.5 L200 45.1 L208 43.9 L216 42.9 L224 42.1 L232 41.5 L240 41.2 L248 41.0 L256 41.0 L264 41.1 L272 41.3 L280 41.6 L288 42.0 L296 42.4 L304 42.9 L312 43.4 L320 43.9 L328 44.6 L336 45.3 L344 46.1 L352 46.9 L360 47.9 L368 48.9 L376 49.9 L384 50.9 L392 51.9 L400 52.8 L408 53.5 L416 54.2 L424 54.6 L432 54.8 L440 54.9 L448 54.8 L456 54.5 L464 54.1 L472 53.7 L480 53.3"/%3E%3Cpath d="M0 75.6 L8 75.0 L16 74.4 L24 74.0 L32 73.6 L40 73.3 L48 73.1 L56 72.8 L64 72.6 L72 72.4 L80 72.1 L88 71.8 L96 71.4 L104 71.0 L112 70.5 L120 70.0 L128 69.5 L136 69.0 L144 68.6 L152 68.2 L160 67.9 L168 67.6 L176 67.4 L184 67.2 L192 66.9 L200 66.7 L208 66.4 L216 66.0 L224 65.6 L232 65.0 L240 64.4 L248 63.7 L256 63.0 L264 62.3 L272 61.7 L280 61.2 L288 60.9 L296 60.8 L304 61.0 L312 61.5 L320 62.3 L328 63.4 L336 64.8 L344 66.4 L352 68.2 L360 70.0 L368 71.8 L376 73.6 L384 75.2 L392 76.6 L400 77.7 L408 78.5 L416 79.0 L424 79.2 L432 79.1 L440 78.8 L448 78.3 L456 77.7 L464 77.0 L472 76.3 L480 75.6"/%3E%3Cpath d="M0 98.8 L8 98.5 L16 97.9 L24 97.1 L32 96.1 L40 94.9 L48 93.5 L56 92.0 L64 90.4 L72 88.8 L80 87.2 L88 85.8 L96 84.5 L104 83.5 L112 82.8 L120 82.3 L128 82.2 L136 82.3 L144 82.7 L152 83.2 L160 83.9 L168 84.7 L176 85.5 L184 86.2 L192 86.7 L200 87.2 L208 87.4 L216 87.5 L224 87.3 L232 87.1 L240 86.7 L248 86.3 L256 85.9 L264 85.5 L272 85.2 L280 85.1 L288 85.2 L296 85.4 L304 85.8 L312 86.5 L320 87.2 L328 88.1 L336 89.1 L344 90.1 L352 91.1 L360 92.1 L368 93.1 L376 93.9 L384 94.7 L392 95.4 L400 96.1 L408 96.6 L416 97.1 L424 97.6 L432 98.0 L440 98.4 L448 98.7 L456 98.9 L464 99.0 L472 99.0 L480 98.8"/%3E%3Cpath d="M0 117.7 L8 117.2 L16 116.5 L24 115.5 L32 114.2 L40 112.8 L48 111.2 L56 109.6 L64 108.0 L72 106.5 L80 105.1 L88 103.9 L96 102.9 L104 102.1 L112 101.5 L120 101.2 L128 101.0 L136 101.0 L144 101.1 L152 101.3 L160 101.6 L168 102.0 L176 102.4 L184 102.9 L192 103.4 L200 103.9 L208 104.6 L216 105.3 L224 106.1 L232 106.9 L240 107.9 L248 108.9 L256 109.9 L264 110.9 L272 111.9 L280 112.8 L288 113.5 L296 114.2 L304 114.6 L312 114.8 L320 114.9 L328 114.8 L336 114.5 L344 114.1 L352 113.7 L360 113.3 L368 112.9 L376 112.7 L384 112.5 L392 112.6 L400 112.8 L408 113.3 L416 113.8 L424 114.5 L432 115.3 L440 116.1 L448 116.8 L456 117.3 L464 117.7 L472 117.8 L480 117.7"/%3E%3Cpath d="M0 130.0 L8 129.5 L16 129.0 L24 128.6 L32 128.2 L40 127.9 L48 127.6 L56 127.4 L64 127.2 L72 126.9 L80 126.7 L88 126.4 L96 126.0 L104 125.6 L112 125.0 L120 124.4 L128 123.7 L136 123.0 L144 122.3 L152 121.7 L160 121.2 L168 120.9 L176 120.8 L184 121.0 L192 121.5 L200 122.3 L208 123.4 L216 124.8 L224 126.4 L232 128.2 L240 130.0 L248 131.8 L256 133.6 L264 135.2 L272 136.6 L280 137.7 L288 138.5 L296 139.0 L304 139.2 L312 139.1 L320 138.8 L328 138.3 L336 137.7 L344 137.0 L352 136.3 L360 135.6 L368 135.0 L376 134.4 L384 134.0 L392 133.6 L400 133.3 L408 133.1 L416 132.8 L424 132.6 L432 132.4 L440 132.1 L448 131.8 L456 131.4 L464 131.0 L472 130.5 L480 130.0"/%3E%3Cpath d="M0 142.3 L8 142.2 L16 142.3 L24 142.7 L32 143.2 L40 143.9 L48 144.7 L56 145.5 L64 146.2 L72 146.7 L80 147.2 L88 147.4 L96 147.5 L104 147.3 L112 147.1 L120 146.7 L128 146.3 L136 145.9 L144 145.5 L152 145.2 L160 145.1 L168 145.2 L176 145.4 L184 145.8 L192 146.5 L200 147.2 L208 148.1 L216 149.1 L224 150.1 L232 151.1 L240 152.1 L248 153.1 L256 153.9 L264 154.7 L272 155.4 L280 156.1 L288 156.6 L296 157.1 L304 157.6 L312 158.0 L320 158.4 L328 158.7 L336 158.9 L344 159.0 L352 159.0 L360 158.8 L368 158.5 L376 157.9 L384 157.1 L392 156.1 L400 154.9 L408 153.5 L416 152.0 L424 150.4 L432 148.8 L440 147.2 L448 145.8 L456 144.5 L464 143.5 L472 142.8 L480 142.3"/%3E%3Cpath d="M0 161.2 L8 161.0 L16 161.0 L24 161.1 L32 161.3 L40 161.6 L48 162.0 L56 162.4 L64 162.9 L72 163.4 L80 163.9 L88 164.6 L96 165.3 L104 166.1 L112 166.9 L120 167.9 L128 168.9 L136 169.9 L144 170.9 L152 171.9 L160 172.8 L168 173.5 L176 174.2 L184 174.6 L192 174.8 L200 174.9 L208 174.8 L216 174.5 L224 174.1 L232 173.7 L240 173.3 L248 172.9 L256 172.7 L264 172.5 L272 172.6 L280 172.8 L288 173.3 L296 173.8 L304 174.5 L312 175.3 L320 176.1 L328 176.8 L336 177.3 L344 177.7 L352 177.8 L360 177.7 L368 177.2 L376 176.5 L384 175.5 L392 174.2 L400 172.8 L408 171.2 L416 169.6 L424 168.0 L432 166.5 L440 165.1 L448 163.9 L456 162.9 L464 162.1 L472 161.5 L480 161.2"/%3E%3Cpath d="M0 184.4 L8 183.7 L16 183.0 L24 182.3 L32 181.7 L40 181.2 L48 180.9 L56 180.8 L64 181.0 L72 181.5 L80 182.3 L88 183.4 L96 184.8 L104 186.4 L112 188.2 L120 190.0 L128 191.8 L136 193.6 L144 195.2 L152 196.6 L160 197.7 L168 198.5 L176 199.0 L184 199.2 L192 199.1 L200 198.8 L208 198.3 L216 197.7 L224 197.0 L232 196.3 L240 195.6 L248 195.0 L256 194.4 L264 194.0 L272 193.6 L280 193.3 L288 193.1 L296 192.8 L304 192.6 L312 192.4 L320 192.1 L328 191.8 L336 191.4 L344 191.0 L352 190.5 L360 190.0 L368 189.5 L376 189.0 L384 188.6 L392 188.2 L400 187.9 L408 187.6 L416 187.4 L424 187.2 L432 186.9 L440 186.7 L448 186.4 L456 186.0 L464 185.6 L472 185.0 L480 184.4"/%3E%3Cpath d="M0 206.7 L8 206.3 L16 205.9 L24 205.5 L32 205.2 L40 205.1 L48 205.2 L56 205.4 L64 205.8 L72 206.5 L80 207.2 L88 208.1 L96 209.1 L104 210.1 L112 211.1 L120 212.1 L128 213.1 L136 213.9 L144 214.7 L152 215.4 L160 216.1 L168 216.6 L176 217.1 L184 217.6 L192 218.0 L200 218.4 L208 218.7 L216 218.9 L224 219.0 L232 219.0 L240 218.8 L248 218.5 L256 217.9 L264 217.1 L272 216.1 L280 214.9 L288 213.5 L296 212.0 L304 210.4 L312 208.8 L320 207.2 L328 205.8 L336 204.5 L344 203.5 L352 202.8 L360 202.3 L368 202.2 L376 202.3 L384 202.7 L392 203.2 L400 203.9 L408 204.7 L416 205.5 L424 206.2 L432 206.7 L440 207.2 L448 207.4 L456 207.5 L464 207.3 L472 207.1 L480 206.7"/%3E%3Cpath d="M0 227.9 L8 228.9 L16 229.9 L24 230.9 L32 231.9 L40 232.8 L48 233.5 L56 234.2 L64 234.6 L72 234.8 L80 234.9 L88 234.8 L96 234.5 L104 234.1 L112 233.7 L120 233.3 L128 232.9 L136 232.7 L144 232.5 L152 232.6 L160 232.8 L168 233.3 L176 233.8 L184 234.5 L192 235.3 L200 236.1 L208 236.8 L216 237.3 L224 237.7 L232 237.8 L240 237.7 L248 237.2 L256 236.5 L264 235.5 L272 234.2 L280 232.8 L288 231.2 L296 229.6 L304 228.0 L312 226.5 L320 225.1 L328 223.9 L336 222.9 L344 222.1 L352 221.5 L360 221.2 L368 221.0 L376 221.0 L384 221.1 L392 221.3 L400 221.6 L408 222.0 L416 222.4 L424 222.9 L432 223.4 L440 223.9 L448 224.6 L456 225.3 L464 226.1 L472 226.9 L480 227.9"/%3E%3C/svg%3E') repeat;background-size:480px auto;opacity:.07}
/* e-book page: cover + two inside pages */
.ebgrid{display:grid;grid-template-columns:1.25fr 1fr;gap:16px;align-items:center}
.ebgrid .ebcover{aspect-ratio:1075/1521}
.ebgrid .ebpage{min-height:0}
.ebgrid .portrait{margin:0;border-radius:12px;overflow:hidden;border:1px solid var(--border)}
.ebgrid img{width:100%;height:100%;object-fit:cover;object-position:top}
.ebbadge{position:absolute;right:14px;bottom:14px;background:var(--aqua);color:var(--on-aqua);border-radius:999px;padding:8px 14px;font:600 12px/1 Montserrat,sans-serif;letter-spacing:.12em;text-transform:uppercase;box-shadow:0 10px 24px rgba(0,0,0,.35)}
.ebbadge b{font:400 20px/1 Anton,sans-serif;margin-right:4px}
/* client result highlight on review cards */
.tcard .result{display:inline-block;margin:14px 0 2px;padding:6px 12px;border-radius:999px;background:rgba(128,163,21,.16);border:1px solid rgba(128,163,21,.45);color:var(--lime-text);font:600 12px/1.3 Montserrat,sans-serif;letter-spacing:.06em;text-transform:uppercase}
/* photos on cards and photo strips */
.pcard .ph{margin:-30px -28px 22px;aspect-ratio:16/9;overflow:hidden;border-radius:var(--r) var(--r) 0 0;background:var(--teal)}
.pcard .ph img{width:100%;height:100%;object-fit:cover}
.pstrip{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.pstrip.three{grid-template-columns:repeat(3,1fr)}
.pstrip figure{margin:0;border-radius:var(--r);overflow:hidden;border:1px solid var(--border);aspect-ratio:4/5;background:var(--teal);position:relative}
.pstrip img{width:100%;height:100%;object-fit:cover}
.pstrip figcaption{position:absolute;left:0;right:0;bottom:0;padding:28px 16px 14px;background:linear-gradient(transparent,rgba(12,34,38,.92));font:600 12px/1.3 Montserrat,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--text)}
@media (max-width:980px){.pstrip{grid-template-columns:1fr 1fr}.pstrip.three{grid-template-columns:1fr 1fr 1fr}}
@media (max-width:640px){.pstrip,.pstrip.three{grid-template-columns:1fr 1fr;gap:10px}.pstrip.three figure:last-child{display:none}}
.mfeature{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:44px;align-items:center}
.mfeature .portrait img{aspect-ratio:4/5;object-fit:cover;width:100%;border-radius:16px}
@media (max-width:860px){.mfeature{grid-template-columns:1fr;gap:26px}.mfeature .portrait{max-width:420px}}
.side-photo{border-radius:16px;overflow:hidden;border:1px solid var(--border);margin-bottom:18px;aspect-ratio:16/10}
.side-photo img{width:100%;height:100%;object-fit:cover}
"""

# ---------------------------------------------------------------- write
if __name__ == '__main__':
    open(OUT + 'vivify.css', 'w').write(CSS + EX.CSS + EXTRA_CSS + VI.CSS)
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
