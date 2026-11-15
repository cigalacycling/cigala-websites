"""/about/ redesigned (Matteo 15 Nov: "too much text ... some centred, some not ... Read our testimonials, there is nothing there").

Kept (CLAUDE.md): URL, H1 "MATTEO CIGALA", every live H2 except the testimonials one (-> READ OUR CASE STUDIES, as on Vision
and the country pages, now with the case studies under it), all the live copy, word for word, and every live image with
its live alt text. New: a split hero, facts with icons, the story as a timeline (like the Tours itinerary), seasons as
cards, the coaching lists as icon chips, two more photos of Matteo (Strade Bianche, Volta Almodovar). Everything left-aligned.
  python3 tools/build_coaching_about.py
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
import build_coaching_generic as G
import build_coaching_services as S
ic, I, head = S.ic, S.I, S.head
I = dict(I, medal='<circle cx="12" cy="15" r="6"/><path d="M8.5 10.5 6 2h4l2 5 2-5h4l-2.5 8.5"/><path d="m12 12.5.9 1.8 2 .3-1.4 1.4.3 2-1.8-1-1.8 1 .3-2-1.4-1.4 2-.3z"/>',
         grad='<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 2 9 2 12 0v-5"/>',
         flag='<path d="M4 22V4M4 4h13l-2 4 2 4H4"/>', globe='<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/>',
         map='<path d="m1 6 7-3 8 3 7-3v15l-7 3-8-3-7 3z"/><path d="M8 3v15M16 6v15"/>', cart='<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6"/>',
         trophy='<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3"/>',
         tri='<circle cx="12" cy="4" r="2"/><path d="M4 21c2-3 5-4 8-4s6 1 8 4M9 10l3 2 3-2M12 12v5"/>')

T = open(ROOT + 'coaching/text/about.txt').read()
P = lambda s: s.replace('**', '').strip()
def after(h, stop=('H2:', 'H3:')):
    out, on = [], False
    for l in T.split('\n'):
        if l.startswith(h): on = True; continue
        if on and l.startswith(stop): break
        if on: out.append(l)
    return out
paras = lambda ls: [P(l[3:]) for l in ls if l.startswith('P: ')]
bul = lambda xs: [x.lstrip('\u200b•· ').strip() for x in xs]

intro = paras(T.split('\n')[:12])           # Founder line, 3 titles, then the 4 intro paragraphs
titles, bio = intro[1:4], intro[4:8]
story1 = paras(after('H3: FROM ITALIAN TALENT'))
story2 = paras(after('H3: THE IRISH CHAPTER'))
story3_raw = after('H3: A NEW ERA')
coach1, coach2, coach3 = (paras(after(h)) for h in ('H3: From Beginners', 'H3: Proven Results', 'H3: Science-Backed'))
prem = paras(after('H2: A PREMIUM COACHING EXPERIENCE'))
coaching_p = [P(l[3:] if l.startswith('P: ') else l) for l in after('H3: COACHING')]  # raw (links inside)
assert len(titles) == 3 and len(bio) == 4, (titles, bio)

def img_k(k, name, pos=None, cls='photo sv-photo'):
    st = f' style="object-position:{pos}"' if pos else ''
    return f'<div class="{cls}"><img src="{img(k, name)}" alt="{E(live_alt(k))}" loading="lazy"{st}></div>'
def chips(xs, icon='check', cls='ab-chips'):
    return f'<ul class="{cls}">' + ''.join(f'<li>{ic(I[icon])}<span>{E(x)}</span></li>' for x in xs) + '</ul>'

# ---- story 1: Italy (junior races + early wins) ----
s1_lead, s1_races_lead = story1[0], story1[1]
juniors = ['World Championship Juniors 2011 — Copenhagen', 'Paris–Roubaix Juniors 2011 — France', 'Trofeo Karlsberg 2011 — Germany',
           'Course de la Paix 2011 (Czech Republic) — podium in Stage 5']
early = [bul([x])[0] for x in story1[5:8]]
assert all(j.split(' — ')[0].split(' (')[0] in T for j in juniors) and 'His early career highlights also include:' in story1[4]
# ---- story 3: seasons ----
seasons, cur = [], None
for l in story3_raw:
    if l.startswith('<img'): continue   # the live images are placed separately
    x = l[3:].strip() if l.startswith('P: ') else l.strip()
    x = x.replace('**', '').strip()
    if not x: continue
    m = re.match(r'(\d{4}(?:, \d{4})?) Season Highlights', x)
    if m: cur = (m.group(1), []); seasons.append(cur); continue
    if cur is None: s3_lead = x; continue
    cur[1].append(x.lstrip('•').strip())
SEASON_PIC = {'2021': ('gran_fondo_strade_bianche_2022_img_1', 'about-strade-bianche-win', '50% 30%'),
              '2022': ('imgi_18_BPZw', 'about-european-champion-medal', '50% 25%'),
              '2023': ('imgi_16_Nqjd', 'about-worlds-silver-podium', '50% 20%'),
              '2024, 2025': ('Matteo-Cigala-Wins-Volta-Almodovar', 'about-volta-almodovar-win', '50% 25%')}
def season(y, items):
    k, n, pos = SEASON_PIC[y]
    sub = [i for i in items if i.startswith(('Gran Fondo', 'Medio Fondo')) and y == '2021']
    main = [i for i in items if i not in sub]
    lis = ''.join(f'<li>{E(i)}' + (chips(sub, 'trophy', 'ab-sub') if i.startswith('Won 11') else '') + '</li>' for i in main)
    return (f'<article class="ab-season panel"><div class="ab-season-img"><img src="{img(k, n)}" alt="{E(live_alt(k))}" loading="lazy" style="object-position:{pos}"></div>'
            f'<div class="ab-season-tx"><div class="ab-year">{y}</div><p class="ab-sh">Season Highlights</p><ul class="ab-list">{lis}</ul></div></article>')

QUALS = ['UCI &amp; Cycling Ireland Level 1 Coach', 'TrainingPeaks Level 2 Coach']   # Matteo 15 Nov
FACTS = [('flag', '28 years', 'of cycling experience'), ('users', 'Over a decade', 'of coaching'), ('trophy', '200+', 'race victories'),
         ('grad', 'BA &amp; Diploma', 'Business Management Degree, Diploma in Science and Sports')]
PREM_IC = ['bike', 'globe', 'users', 'target', 'chart', 'chat', 'trophy', 'heart']
WHO_IC = ['user', 'bike', 'flag', 'star', 'map', 'tri', 'users', 'power']

def link_md(s):   # the live [text](url) links, pointed at the coaching site's own pages
    fix = {'http://www.cigalacycling.com/trainsmarterridefaster': f'{C}/coaching-vision/', 'http://www.cigalacycling.com/tri-individual-packages': f'{C}/tri-individual-packages/',
           'http://www.cigalacycling.com/individual-packages': f'{C}/individual-packages/', 'http://www.cigalacycling.com/sportive-package': f'{C}/individual-packages/',
           'http://www.cigalacycling.com/group-club-packages': f'{C}/group-club-packages/', 'http://retail.cigalacycling.com/': 'https://retail.cigalacycling.com/'}
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{fix.get(m.group(2), m.group(2))}" {EXT}>{E(m.group(1).strip())}</a>' + (' ' if m.group(1)[-1:].isspace() else ''), E(s).replace('&amp;', '&')).replace('&', '&amp;').replace('&amp;amp;', '&amp;')

_pk = open(ROOT + 'coaching/text/individual-packages.txt').read()   # the same numbers as Individual Packages (Matteo 15 Nov)
NUMS = re.findall(r'H3: (.+)\nH4: (.+)', _pk[_pk.index('H2: 2026 IN NUMBERS'):].split('\nH2:', 1)[0])
assert len(NUMS) == 6, NUMS
TILES = [(f'{C}/individual-packages/', 'imgi_20_Fqav', 'about-coaching-pro-cyclist', 'bike', 'CYCLING COACHING', 'Coaching is our CORE: road, gravel, MTB and gran fondos, for every level.', 'Cycling packages'),
         (f'{C}/tri-individual-packages/', 'imgi_22_lABW', 'about-coaching-an-athlete', 'tri', 'TRIATHLON COACHING', 'Swim, bike and run, planned together around your races.', 'Triathlon packages'),
         ('https://tours.cigalacycling.com/', 'imgi_21_Lu1w', 'about-tours-tre-cime', 'map', 'BIKE TOURS', 'Memorable Adventures. New Friends. Shared Passion. Lifetime Experience.', 'tours.cigalacycling.com'),
         ('https://retail.cigalacycling.com/', 'imgi_18_BPZw', 'about-european-champion-medal', 'cart', 'RETAIL', 'Ireland’s #1 Online Shop for all cycling needs', 'retail.cigalacycling.com')]
bt = after('H3: BIKE TOURS')
tours_txt = ' '.join(l for l in bt if not l.startswith('<img'))
dest = re.findall(r'^(Italy|Spain|France|Portugal): (.+)$', tours_txt.replace(' Italy:', '\nItaly:').replace(' Spain:', '\nSpain:').replace(' France:', '\nFrance:').replace(' Portugal:', '\nPortugal:').replace(' P: ', '\nP: '), re.M)
dest = [(c, d.split('P:')[0].strip()) for c, d in dest]
rt = paras(after('H3: RETAIL'))

MAIN = f'''<div class="ab-hero">
  <div class="in ab-hero-in">
    <div class="ab-hero-tx">
      <div class="eyebrow eb-pill"><span class="dot"></span>{E(intro[0])}</div>
      <h1>MATTEO CIGALA</h1>
      <ul class="ab-titles">{''.join(f'<li>{ic(I["medal"])}<span>{E(t)}</span></li>' for t in titles)}</ul>
      <ul class="ab-quals">{''.join(f'<li>{ic(I["grad"])}<span>{q}</span></li>' for q in QUALS)}</ul>
      <div class="ctas"><a class="btn btn-go" href="{C}/individual-packages/" {EXT}>Train with Matteo</a><a class="btn btn-ghost" href="#story">Matteo’s story ↓</a></div>
    </div>
    <div class="ab-hero-img ab-cut"><img src="{conv('coaching/brand/matteo-cigala-author-signature.webp', 'about-hero-matteo-signature')}" alt="{E(live_alt('IMG_5948-1'))}" width="720" height="943"></div>
  </div>
</div>

<section>
  <div class="in">
    <ul class="ab-facts">{''.join(f'<li>{ic(I[i])}<b>{a}</b><span>{b}</span></li>' for i, a, b in FACTS)}</ul>
    <div class="ab-bio">{''.join(f'<p>{E(p)}</p>' for p in bio)}</div>
  </div>
</section>

<section id="story">
  <div class="in">
    {head('Matteo’s story', "MATTEO'S STORY")}
    <ol class="ab-tl">
      <li class="ab-ch">
        <div class="ab-dot"><span>IT</span></div>
        <div class="ab-ch-body panel">
          <h3>FROM ITALIAN TALENT TO INTERNATIONAL COMPETITOR</h3>
          <div class="ab-ch-grid">
            <div>
              <p>{E(s1_lead)}</p>
              <p class="ab-lab">{E(s1_races_lead)}</p>
              {chips(juniors, 'globe')}
              <p class="ab-lab">His early career highlights also include:</p>
              {chips(early, 'trophy')}
              <p>{E(story1[8])}</p>
            </div>
            {img_k('imgi_16_Nqjd', 'about-italian-podium', '50% 20%')}
          </div>
        </div>
      </li>
      <li class="ab-ch">
        <div class="ab-dot"><span>IE</span></div>
        <div class="ab-ch-body panel">
          <h3>THE IRISH CHAPTER — DOMINANCE, CONSISTENCY &amp; LEADERSHIP</h3>
          <div class="ab-ch-grid">
            <div>
              <p class="ab-big">{E(story2[0])}</p>
              <ul class="ab-years">{''.join(f'<li><b>{y}</b><p>{E(t)}</p></li>' for y, t in zip(('2016–2024', '2017', '2018', '2018', '2019–2020'), story2[1:6]))}</ul>
            </div>
            {img_k('imgi_17_JKPi', 'about-ras-2018', '50% 30%')}
          </div>
        </div>
      </li>
      <li class="ab-ch">
        <div class="ab-dot"><span>EU</span></div>
        <div class="ab-ch-body">
          <div class="panel ab-ch-head"><h3>A NEW ERA — EUROPEAN CHAMPION, WORLD CLASS RESULTS</h3><p>{E(s3_lead)}</p></div>
          <div class="ab-seasons">{''.join(season(y, it) for y, it in seasons)}</div>
        </div>
      </li>
    </ol>
  </div>
</section>

<section>
  <div class="in">
    {head('The coach', 'MATTEO THE COACH — SCIENCE MEETS HUMAN PERFORMANCE')}
    <div class="ab-coach">
      <div class="panel ab-col">
        <h3 class="h-sm">From Beginners to WorldTour Professionals</h3>
        <p>{E(coach1[0])}</p>
        <ul class="ab-chips ab-who">{''.join(f'<li>{ic(I[i])}<span>{E(x)}</span></li>' for i, x in zip(WHO_IC, bul(coach1[1:])))}</ul>
      </div>
      <div class="panel ab-col">
        <h3 class="h-sm">Proven Results &amp; Athlete Achievements</h3>
        <p>{E(coach2[0])}</p>
        {chips(bul(coach2[1:]), 'trophy')}
      </div>
      <div class="panel ab-col ab-sci">
        <h3 class="h-sm">Science-Backed Performance Coaching</h3>
        <p>{E(coach3[0])}</p>
        {chips(bul(coach3[1:]), 'chart')}
      </div>
    </div>
    <div class="ab-pics">{img_k('imgi_22_lABW', 'about-coaching-an-athlete', '50% 40%')}{img_k('imgi_20_Fqav', 'about-coaching-pro-cyclist', '50% 30%')}</div>
  </div>
</section>

<section>
  <div class="in">
    {head('Why Cigala Cycling', 'A PREMIUM COACHING EXPERIENCE')}
    <p class="ab-lede">{E(prem[0])}</p>
    <ul class="ab-prem">{''.join(f'<li>{ic(I[i])}<span>{E(x.lstrip("✓").strip())}</span></li>' for i, x in zip(PREM_IC, prem[1:]))}</ul>
  </div>
</section>

<section>
  <div class="in">
    {head('Real results', 'READ OUR CASE STUDIES', more=f'<div class="rv-links"><a class="btn btn-go" href="{C}/case-studies/" {EXT}>Read our case studies</a></div>')}
    {case_cards(C + '/case-studies/')}
    <div class="ab-rv">
      <div class="ab-rv-h"><p class="ab-lab">What our athletes say</p><div class="rv-links"><a class="arrow-link" href="{GOOGLE_REVIEWS}" {EXT}><span class="gstar" aria-hidden="true">★</span> Read our reviews on Google →</a><a class="arrow-link" href="{C}/testimonials/" {EXT}>All testimonials →</a></div></div>
      {reviews_strip()}
    </div>
    <div class="ab-nums">
      <div class="head"><div><div class="eyebrow">Results</div><h3 class="h-sec">2026 IN NUMBERS</h3><div class="bar"></div></div></div>
      <div class="stats nums">{''.join(f'<div class="stat"><h3 class="n" data-count="{E(n)}">{E(n)}</h3><h4 class="l">{E(l)}</h4></div>' for n, l in NUMS)}</div>
    </div>
  </div>
</section>

<section>
  <div class="in">
    {head('#TrainSmarterRideFaster', 'CIGALA CYCLING')}
    <ul class="ab-tiles">{''.join(f'<li><a href="{u}" {EXT}><span class="ab-tile-ic">{ic(I[i])}</span><h3 class="h-sm">{t}</h3><p>{d}</p><em>{l} →</em></a></li>' for u, k, n, i, t, d, l in TILES)}</ul>
  </div>
</section>'''

CSS = '''<style>
.ab-hero { position: relative; padding: clamp(36px, 6vw, 80px) 0 clamp(28px, 4vw, 48px); background: radial-gradient(900px 500px at 80% 30%, rgba(0,154,68,.16), transparent 60%); }
.ab-hero-in { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 40px; align-items: center; }
.ab-hero h1 { font-size: clamp(48px, 8vw, 104px); line-height: .95; margin: 16px 0 20px; }
.ab-titles { list-style: none; margin: 0 0 26px; padding: 0; display: grid; gap: 10px; }
.ab-titles li { display: flex; align-items: center; gap: 12px; font-weight: 600; color: var(--text); font-size: 17px; }
.ab-titles .sv-ic { flex: none; width: 36px; height: 36px; padding: 7px; border-radius: 50%; background: rgba(240,191,0,.14); stroke: #f0bf00; }
.ab-hero-img { position: relative; border-radius: 20px; overflow: hidden; background: #f4f4f2; aspect-ratio: 1108 / 1319; box-shadow: 0 30px 80px rgba(0,0,0,.5); }
.ab-hero-img img { width: 100%; height: 100%; object-fit: cover; display: block; }
@media (max-width: 900px) { .ab-hero-in { grid-template-columns: 1fr; } .ab-hero-img { max-width: 420px; } }
.ab-facts { list-style: none; margin: 0 0 32px; padding: 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.ab-facts li { display: grid; gap: 4px; padding: 20px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); transition: transform .25s, border-color .25s; }
.ab-facts li:hover { transform: translateY(-3px); border-color: var(--green); }
.ab-facts b { font: 400 28px/1.05 var(--head); text-transform: uppercase; color: var(--text); margin-top: 8px; }
.ab-facts span { font-size: 14px; color: var(--text-2); }
@media (max-width: 900px) { .ab-facts { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.ab-bio { columns: 2 340px; column-gap: 40px; }
.ab-bio p { margin: 0 0 14px; break-inside: avoid; color: var(--text-2); }
.ab-bio p:first-child { font-size: 18px; color: var(--text); }
.ab-tl { list-style: none; margin: 0; padding: 0; }
.ab-ch { display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 20px; position: relative; padding-bottom: 28px; }
.ab-ch::before { content: ""; position: absolute; left: 31px; top: 64px; bottom: 0; width: 2px; background: var(--border-strong); }
.ab-ch:last-child { padding-bottom: 0; } .ab-ch:last-child::before { display: none; }
.ab-dot { width: 64px; height: 64px; border-radius: 50%; display: grid; place-items: center; background: var(--panel-solid, #16181a); border: 2px solid var(--green); font: 400 22px/1 var(--head); color: var(--text); }
.ab-ch-body { min-width: 0; }
.ab-ch-body.panel, .ab-ch-head { padding: clamp(20px, 3vw, 30px); }
.ab-ch h3 { font-size: clamp(22px, 2.4vw, 30px); margin: 0 0 14px; }
.ab-ch-grid { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 4fr); gap: 28px; align-items: start; }
.ab-ch-grid .photo { aspect-ratio: 4 / 5; }
@media (max-width: 900px) { .ab-ch-grid { grid-template-columns: 1fr; } .ab-ch-grid .photo { aspect-ratio: 16 / 11; } }
.ab-lab { margin: 16px 0 8px !important; font-size: 13px !important; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--green-text) !important; }
.ab-big { font-size: 18px !important; color: var(--text) !important; font-weight: 600; }
.ab-chips { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 8px; }
.ab-chips li { display: flex; align-items: flex-start; gap: 10px; padding: 10px 12px; border: 1px solid var(--border); border-radius: 10px; background: rgba(255,255,255,.03); font-size: 14px; line-height: 1.4; color: var(--text-2); }
.ab-chips .sv-ic { flex: none; width: 20px; height: 20px; stroke: var(--green-text); margin-top: 1px; }
.ab-years { list-style: none; margin: 14px 0 0; padding: 0; display: grid; gap: 10px; }
.ab-years li { display: grid; grid-template-columns: 96px minmax(0, 1fr); gap: 14px; padding: 12px 14px; border-left: 3px solid var(--green); background: rgba(255,255,255,.03); border-radius: 0 10px 10px 0; }
.ab-years b { font: 400 20px/1.2 var(--head); color: var(--green-text); }
.ab-years p { margin: 0; font-size: 15px; color: var(--text-2); }
@media (max-width: 600px) { .ab-years li { grid-template-columns: 1fr; gap: 4px; } }
.ab-ch-head { margin-bottom: 14px; } .ab-ch-head p { margin: 0; color: var(--text-2); }
.ab-seasons { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
@media (max-width: 900px) { .ab-seasons { grid-template-columns: 1fr; } }
.ab-season { display: grid; grid-template-columns: 150px minmax(0, 1fr); overflow: hidden; transition: transform .25s, border-color .25s; }
.ab-season:hover { transform: translateY(-3px); border-color: var(--green); }
.ab-season-img img { width: 100%; height: 100%; object-fit: cover; display: block; }
.ab-season-tx { padding: 18px 20px; min-width: 0; overflow-wrap: anywhere; }
.ab-year { font: 400 34px/1 var(--head); color: var(--green-text); }
.ab-sh { margin: 2px 0 10px !important; font-size: 12px !important; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--text-3) !important; }
.ab-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 7px; }
.ab-list > li { position: relative; padding-left: 16px; font-size: 14px; line-height: 1.45; color: var(--text-2); }
.ab-list > li::before { content: ""; position: absolute; left: 0; top: 8px; width: 6px; height: 6px; border-radius: 50%; background: #ff3d33; }
.ab-sub { list-style: none; margin: 8px 0 0; padding: 0; display: grid; gap: 4px; }
.ab-sub li { display: flex; gap: 8px; align-items: center; font-size: 13.5px; color: var(--text); }
.ab-sub .sv-ic { width: 16px; height: 16px; stroke: #f0bf00; flex: none; }
@media (max-width: 600px) { .ab-season { grid-template-columns: 1fr; } .ab-season-img { aspect-ratio: 16 / 9; } .ab-ch { grid-template-columns: 44px minmax(0, 1fr); gap: 12px; } .ab-dot { width: 44px; height: 44px; font-size: 16px; } .ab-ch::before { left: 21px; top: 44px; } }
.ab-coach { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
@media (max-width: 1000px) { .ab-coach { grid-template-columns: 1fr; } }
.ab-col { padding: 22px; }
.ab-col h3 { margin: 0 0 8px; }
.ab-col > p { margin: 0 0 12px; color: var(--text-2); font-size: 15px; }
.ab-col .ab-chips { grid-template-columns: 1fr; }
.ab-tags { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; }
.ab-tags li { padding: 7px 12px; border-radius: 999px; border: 1px solid rgba(0,154,68,.45); background: rgba(0,154,68,.08); font-size: 13px; color: var(--text); transition: background .2s; }
.ab-tags li:hover { background: rgba(0,154,68,.22); }
.ab-wide { margin-top: 18px; aspect-ratio: 21 / 8; }
@media (max-width: 600px) { .ab-wide { aspect-ratio: 16 / 10; } }
.ab-lede { color: var(--text-2); margin: -4px 0 16px; }
.ab-prem { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.ab-prem li { display: grid; gap: 12px; align-content: start; padding: 20px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); font-weight: 600; color: var(--text); font-size: 15px; line-height: 1.4; transition: transform .25s, border-color .25s; }
.ab-prem li:hover { transform: translateY(-3px); border-color: var(--green); }
.ab-prem .sv-ic { width: 40px; height: 40px; padding: 9px; border-radius: 10px; background: var(--green-wash); stroke: var(--green-text); }
@media (max-width: 1000px) { .ab-prem { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.ab-brands { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; align-items: start; }
@media (max-width: 1000px) { .ab-brands { grid-template-columns: 1fr; } }
.ab-brand { overflow: hidden; }
.ab-brand .photo { aspect-ratio: 16 / 10; border-radius: 0; margin: 0; }
.ab-brand-tx { padding: 20px 22px; }
.ab-brand-tx h3 { margin: 0 0 6px; }
.ab-brand-tx p { margin: 0 0 10px; font-size: 14.5px; color: var(--text-2); }
.ab-brand-tx a { color: var(--green-text); }
.ab-brand-ic { aspect-ratio: 16 / 10; display: grid; place-items: center; background: radial-gradient(circle at 50% 40%, rgba(0,154,68,.25), transparent 60%), #0f1011; }
.ab-brand-ic .sv-ic { width: 84px; height: 84px; stroke: var(--green-text); stroke-width: 1.2; }
.ab-dest { list-style: none; margin: 0 0 10px; padding: 0; display: grid; gap: 6px; }
.ab-dest li { display: grid; grid-template-columns: 76px minmax(0, 1fr); gap: 8px; font-size: 13.5px; color: var(--text-2); }
.ab-dest b { color: var(--text); }
.ab-tiles { list-style: none; margin: 18px 0 0; padding: 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.ab-tiles a { display: flex; align-items: center; gap: 12px; padding: 18px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); text-decoration: none; transition: transform .25s, border-color .25s; }
.ab-tiles a:hover { transform: translateY(-3px); border-color: var(--green); }
.ab-tiles h3 { margin: 0; flex: 1; font-size: 18px; }
.ab-tiles .sv-ic { width: 38px; height: 38px; padding: 8px; border-radius: 10px; background: var(--green-wash); stroke: var(--green-text); flex: none; }
.ab-tiles span { color: var(--green-text); font-weight: 700; }
@media (max-width: 900px) { .ab-tiles { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) { .ab-tiles { grid-template-columns: 1fr; } }
.ab-cut { background: none !important; box-shadow: none !important; aspect-ratio: auto !important; overflow: visible !important; }
.ab-cut img { height: auto !important; object-fit: contain !important; filter: drop-shadow(0 30px 60px rgba(0,0,0,.5)); }
.ab-quals { list-style: none; margin: -10px 0 26px; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; }
.ab-quals li { display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 999px; border: 1px solid rgba(0,154,68,.5); background: rgba(0,154,68,.1); font-size: 13px; font-weight: 600; color: var(--text); }
.ab-quals .sv-ic { width: 18px; height: 18px; stroke: var(--green-text); }
.ab-rv { margin-top: 36px; }
.ab-nums { margin-top: 48px; }
.ab-rv-h { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px 20px; margin-bottom: 14px; }
.ab-rv-h .ab-lab { margin: 0 !important; }
.ab-tiles a { flex-direction: column; align-items: flex-start !important; padding: 0 !important; overflow: hidden; height: 100%; }
.ab-tile-ic { display: grid; place-items: center; width: 100%; aspect-ratio: 16 / 8; background: radial-gradient(circle at 50% 45%, rgba(0,154,68,.28), transparent 62%), #0f1011; border-bottom: 1px solid var(--border); }
.ab-tiles .ab-tile-ic .sv-ic { width: 64px !important; height: 64px !important; padding: 0 !important; background: none !important; stroke-width: 1.3; transition: transform .3s; }
.ab-tiles a:hover .ab-tile-ic .sv-ic { transform: scale(1.12); }
.ab-pics { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 18px; }
.ab-pics .photo { aspect-ratio: 16 / 10; margin: 0; }
@media (max-width: 600px) { .ab-pics { grid-template-columns: 1fr; } }
.ab-tiles a h3 { margin: 12px 18px 4px !important; flex: none !important; }
.ab-tiles a p { margin: 0 18px; font-size: 14px; color: var(--text-2); }
.ab-tiles a em { margin: auto 18px 18px; padding-top: 12px; font-style: normal; font-size: 13.5px; font-weight: 600; color: var(--green-text); }
</style>'''

if __name__ == '__main__':
    build('about', '/about/', MAIN, 'About redesigned: split hero, facts, the story as a timeline with season cards, coaching lists as icons, case studies, the three brands.',
          h1='MATTEO CIGALA', h2_changes={'drop': ['READ OUR TESTIMONIALS - WHAT PEOPLE SAY ABOUT CIGALA CYCLING'], 'add': ['READ OUR CASE STUDIES']},
          extra_css=G.GCSS + CS_CSS + S.CSS + CSS, extra_js=REVIEWS_JS + G.NUMS_JS)
