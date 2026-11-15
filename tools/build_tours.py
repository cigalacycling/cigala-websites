import re, json, html
S = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/'
OUT = S + 'tourspages/'
TP = S + 'tp2/'
E = lambda x: html.escape(x, quote=False)
EXT = 'target="_blank" rel="noopener"'
L = 'https://tours.cigalacycling.com'

css = open(OUT + '_trip.css').read().replace('  body { padding-bottom: 76px; }\n', '')
EXTRA = r'''
/* ---- shared page parts for the Tours pages ---- */
.phero { position: relative; overflow: hidden; isolation: isolate; }
.phero > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; }
.phero::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(90deg, rgba(8,9,10,.88) 0%, rgba(8,9,10,.6) 55%, rgba(8,9,10,.4) 100%), linear-gradient(180deg, rgba(8,9,10,0) 55%, rgba(8,9,10,.95) 100%); }
.hero.phero .in, .hero.plain-hero .in { display: block; }
.phero .in { padding-block: 88px 48px; }
.phero h1 { font-size: clamp(44px, 7.4vw, 92px); max-width: 16ch; }
.phero .lede { color: var(--text); }
.plain-hero .in { padding-block: 64px 8px; }
.plain-hero h1 { font-size: clamp(44px, 7.4vw, 92px); }
.pill-eyebrow { display: inline-flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--text); background: rgba(8,9,10,.78); border: 1px solid var(--border-strong); border-radius: 999px; padding: 6px 14px; margin-bottom: 18px; }
.pill-eyebrow::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--red); flex: none; }
.lede p { margin: 0 0 12px; } .lede p:last-child { margin-bottom: 0; }
.note { font-size: 13px; color: var(--text-3); }
.filters { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { font-family: var(--body); font-size: 12.5px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: var(--text-2); background: var(--wash); border: 1px solid var(--border-strong); border-radius: 999px; padding: 7px 14px; cursor: pointer; }
.chip:hover { color: #fff; border-color: rgba(255,255,255,.3); }
.chip[aria-pressed="true"] { background: var(--green); border-color: var(--green); color: #fff; }
.chip[data-f="road"]::before, .chip[data-f="gf"]::before, .chip[data-f="gravel"]::before { content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--red); margin-right: 7px; vertical-align: 1px; }
.chip[data-f="gravel"]::before { background: var(--gravel); }
.chip[aria-pressed="true"]::before { box-shadow: 0 0 0 1.5px #fff; }
.tag.gravel::before { background: var(--gravel); }
/* trips list */
.trips { display: grid; gap: 18px; }
.trip { display: grid; grid-template-columns: 300px minmax(0, 1fr); overflow: hidden; }
.trip .cimg { display: block; aspect-ratio: 4 / 5; max-width: 100%; }
.trip .cimg img { width: 100%; height: 100%; object-fit: cover; }
.trip .tx { padding: 24px 26px; display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.trip .tags { margin: 0; }
.trip h2 { font-size: clamp(26px, 3vw, 36px); }
.trip .where { font-family: var(--body); text-transform: none; font-size: 14px; font-weight: 600; color: var(--text-2); letter-spacing: 0; }
.trip .meta { display: flex; flex-wrap: wrap; gap: 8px; }
.trip .desc p { margin: 0 0 8px; max-width: 70ch; font-size: 14.5px; }
.trip .bottom { margin-top: auto; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 14px; padding-top: 14px; border-top: 1px solid var(--border); }
.trip .price { font-family: var(--head); font-size: 26px; color: var(--text); line-height: 1.1; }
.trip .price small { display: block; font-family: var(--body); font-size: 12px; font-weight: 600; color: var(--text-3); letter-spacing: .06em; text-transform: uppercase; margin-bottom: 2px; }
.trip .early { display: inline-flex; align-items: center; gap: 8px; font-size: 12.5px; font-weight: 600; color: var(--text); background: rgba(225,6,0,.12); border: 1px solid rgba(225,6,0,.45); border-radius: 6px; padding: 4px 10px; }
.trip .early::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--red); }
.trip .ctas { margin: 0; }
.trip .btn { padding: 10px 18px; }
.footnote { font-size: 13px; color: var(--text-3); margin-top: 22px; max-width: 90ch; }
/* destinations */
.dgrid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.dcard { position: relative; display: flex; align-items: flex-end; aspect-ratio: 4 / 5; max-width: 100%; border-radius: var(--r); overflow: hidden; border: 1px solid var(--border); text-decoration: none; isolation: isolate; background: var(--panel-solid); }
.dcard img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .5s ease; }
.dcard::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(180deg, rgba(8,9,10,0) 40%, rgba(8,9,10,.92) 100%); }
.dcard:hover img { transform: scale(1.04); } .dcard:hover { border-color: rgba(0,154,68,.6); }
.dcard .tx { padding: 18px; display: grid; gap: 4px; }
.dcard h3 { font-size: 26px; }
.dcard .go { font-size: 13px; font-weight: 600; color: var(--green-text); }
.regions { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
.region { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 16px 18px; text-decoration: none; }
.region h3 { font-size: 20px; }
.region span { color: var(--green-text); font-weight: 600; font-size: 13px; white-space: nowrap; }
.region:hover { border-color: rgba(0,154,68,.6); }
.partners { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.partners > div { padding: 18px; min-width: 0; }
.logos { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
.logos span { background: #fff; border-radius: 10px; width: 96px; height: 96px; display: grid; place-items: center; padding: 8px; }
.logos img { max-height: 80px; width: auto; }
.lab { text-transform: uppercase; font-size: 11px; letter-spacing: .09em; color: var(--text-3); font-weight: 600; }
/* destination page */
.prose p { margin: 0 0 14px; max-width: 68ch; }
.prose p:last-child { margin-bottom: 0; }
.gal3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.gal3 img { width: 100%; aspect-ratio: 4 / 3; max-width: 100%; object-fit: cover; border-radius: 10px; border: 1px solid var(--border); }
.facts4 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.fact { padding: 22px; display: grid; grid-template-columns: 48px minmax(0, 1fr); gap: 16px; align-items: start; }
.fact .ic { width: 48px; height: 48px; border-radius: 12px; display: grid; place-items: center; background: var(--green-wash); border: 1px solid rgba(0,154,68,.35); }
.fact .ic svg { width: 24px; height: 24px; fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.fact h3 { font-size: 20px; margin-bottom: 8px; }
.fact p { margin: 0 0 8px; font-size: 14.5px; } .fact p:last-child { margin: 0; }
.tcards { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 16px; }
.tcard { overflow: hidden; display: flex; flex-direction: column; text-decoration: none; }
.tcard .ph { position: relative; aspect-ratio: 16 / 10; max-width: 100%; overflow: hidden; }
.tcard .ph img { width: 100%; height: 100%; object-fit: cover; }
.tcard .ph .tag { position: absolute; top: 14px; left: 14px; }
.tcard .tx { padding: 18px 20px 20px; display: flex; flex-direction: column; gap: 10px; flex: 1; }
.tcard h3 { font-size: 22px; }
.tcard p { margin: 0; font-size: 14px; }
.tcard .go { margin-top: auto; font-size: 13px; font-weight: 600; color: var(--green-text); }
.tcard:hover { border-color: rgba(0,154,68,.6); }
/* guides */
.ggrid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.gcard { overflow: hidden; display: flex; flex-direction: column; text-decoration: none; min-width: 0; }
.gcard .ph { aspect-ratio: 16 / 10; max-width: 100%; overflow: hidden; }
.gcard .ph img { width: 100%; height: 100%; object-fit: cover; }
.gcard .tx { padding: 18px 20px 20px; display: flex; flex-direction: column; gap: 10px; flex: 1; }
.gcard h2 { font-size: 22px; line-height: 1.12; }
.gcard .by { font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--red-text); }
.gcard p { margin: 0; font-size: 14px; }
.gcard .go { margin-top: auto; font-size: 13px; font-weight: 600; color: var(--green-text); }
.gcard:hover { border-color: rgba(0,154,68,.6); }
/* article */
.article { max-width: 820px; margin: 0 auto; padding: clamp(22px, 4vw, 48px); }
.article .by { font-size: 13px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--red-text); margin: 0 0 18px; }
.article h2 { font-size: clamp(24px, 3vw, 32px); margin: 36px 0 14px; scroll-margin-top: 100px; }
.article h2::after { content: ""; display: block; width: 40px; height: 3px; border-radius: 2px; background: var(--green); margin-top: 12px; }
.article p, .article li { max-width: 68ch; font-size: 16px; line-height: 1.7; }
.article p { margin: 0 0 16px; }
.article ul { margin: 0 0 16px; padding-left: 20px; display: grid; gap: 8px; }
.article li::marker { color: var(--green-text); }
.article h3 { font-family: var(--body); text-transform: none; font-size: 18px; font-weight: 700; letter-spacing: 0; margin: 22px 0 8px; }
.article .intro { font-size: 19px; font-weight: 500; color: var(--text); line-height: 1.55; }
.article figure { margin: 24px 0; }
.article figure img { width: 100%; border-radius: 10px; border: 1px solid var(--border); max-height: 560px; object-fit: cover; }
.article a { color: var(--green-text); }
.faq { display: grid; gap: 10px; }
.faq details { background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 10px; }
.faq summary { cursor: pointer; list-style: none; padding: 14px 18px; font-weight: 600; color: var(--text); display: flex; justify-content: space-between; gap: 16px; }
.faq summary::-webkit-details-marker { display: none; }
.faq summary::after { content: "+"; color: var(--green-text); font-size: 20px; line-height: 1; }
.faq details[open] summary::after { content: "–"; }
.faq details p { padding: 0 18px 16px; margin: 0; }
.author { display: grid; grid-template-columns: 96px minmax(0, 1fr); gap: 18px; align-items: center; margin-top: 30px; padding-top: 24px; border-top: 1px solid var(--border); }
.author img { width: 96px; height: 96px; border-radius: 50%; object-fit: cover; object-position: center 20%; background: #fff; }
.author b { display: block; font-size: 16px; }
.author span { font-size: 13.5px; color: var(--text-3); }
/* about */
.story { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: clamp(24px, 5vw, 64px); align-items: start; }
.story .prose b { color: var(--text); }
.story .photo { position: sticky; top: 110px; border-radius: var(--r); overflow: hidden; border: 1px solid var(--border); aspect-ratio: 4 / 5; max-width: 100%; }
.story .photo img { width: 100%; height: 100%; object-fit: cover; }
.why6 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.why6 > div { padding: 22px; display: grid; grid-template-columns: 26px minmax(0, 1fr); gap: 12px; }
.why6 .tick { width: 24px; height: 24px; border-radius: 50%; background: var(--green-wash) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Cpath d='M5.5 10.5l3 3 6-7' fill='none' stroke='%2334c46a' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / 22px no-repeat; border: 1px solid rgba(0,154,68,.4); }
.why6 h3 { font-size: 20px; margin-bottom: 6px; }
.why6 p { margin: 0; font-size: 14px; }
.team { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 14px; }
.member { overflow: hidden; }
.member img { width: 100%; aspect-ratio: 1 / 1; max-width: 100%; object-fit: cover; object-position: center 25%; display: block; }
.member .tx { padding: 12px 14px 14px; }
.member h3 { font-size: 18px; }
.member p { margin: 4px 0 0; font-size: 12.5px; color: var(--text-3); font-weight: 600; }
/* contact (same as the approved cigalacycling.com contact page) */
.contact-grid { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 16px; align-items: start; }
.cpanel { padding: clamp(20px, 3vw, 32px); min-width: 0; }
.form { display: grid; gap: 14px; }
.form label { font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); display: grid; gap: 6px; }
.form label i { color: var(--red-text); font-style: normal; }
.form input, .form textarea { font: 15px/1.5 var(--body); color: var(--text); background: rgba(8,9,10,.6); border: 1px solid var(--border-strong); border-radius: 8px; padding: 12px 14px; width: 100%; }
.form input:focus, .form textarea:focus { outline: none; border-color: var(--green); box-shadow: 0 0 0 3px var(--green-wash); }
.form textarea { min-height: 150px; resize: vertical; }
.form .btn { justify-self: start; }
.form .fnote { font-size: 13px; color: var(--green-text); min-height: 1.2em; margin: 0; }
.info { display: grid; gap: 16px; }
.info .row { display: grid; grid-template-columns: 44px minmax(0, 1fr); gap: 14px; align-items: center; }
.info .ic { width: 44px; height: 44px; border-radius: 10px; display: grid; place-items: center; background: var(--green-wash); border: 1px solid rgba(0,154,68,.35); }
.info .ic svg { width: 20px; height: 20px; fill: none; stroke: var(--green-text); stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.info h2 { font-size: 15px; font-family: var(--body); font-weight: 600; letter-spacing: .1em; color: var(--text-3); }
.info .val { color: var(--text); font-weight: 600; font-size: 17px; overflow-wrap: anywhere; }
.social { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }
.social a { font-size: 13px; font-weight: 600; text-decoration: none; color: var(--text); border: 1px solid var(--border-strong); background: var(--wash); border-radius: 999px; padding: 7px 14px; }
.social a:hover { border-color: var(--green); }
@media (max-width: 980px) {
  .trip { grid-template-columns: 220px minmax(0, 1fr); }
  .dgrid, .regions { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .ggrid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .story, .contact-grid { grid-template-columns: minmax(0, 1fr); }
  .story .photo { position: static; aspect-ratio: 16 / 10; }
  .why6 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .team { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .partners { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 640px) {
  .trip { grid-template-columns: minmax(0, 1fr); }
  .trip .cimg { aspect-ratio: 4 / 5; }
  .trip .tx { padding: 20px; }
  .dgrid, .regions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .dcard h3 { font-size: 20px; }
  .region h3 { font-size: 17px; }
  .ggrid, .why6, .facts4 { grid-template-columns: minmax(0, 1fr); }
  .gal3 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .gal3 img:nth-child(3n) { grid-column: span 2; aspect-ratio: 16 / 9; }
  .team { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .phero .in { padding-block: 64px 32px; }
  .author { grid-template-columns: 72px minmax(0, 1fr); }
  .author img { width: 72px; height: 72px; }
}
'''

NAV = [('./', 'Bike tours'), ('destinations.html', 'Destinations'), (L + '/trips/private-trips/', 'Custom tours'), ('guides.html', 'Guides'), ('about.html', 'About'), (L + '/testimonials/', 'Reviews'), ('https://coaching.cigalacycling.com/', 'Coaching'), ('https://retail.cigalacycling.com/', 'Shop'), ('contact.html', 'Contact')]

def a(href, text, cls='', cur=False):
    ext = '' if not href.startswith('http') else ' ' + EXT
    c = f' class="{cls}"' if cls else ''
    ac = ' aria-current="page"' if cur else ''
    return f'<a{c} href="{href}"{ext}{ac}>{text}</a>'

def header(cur):
    menu = '\n      '.join(a(h, t, cur=(h == cur)) for h, t in NAV)
    return f'''<header class="nav">
  <div class="in">
    <a class="brand" href="./"><img src="img/logo.png" alt="Cigala Cycling Tours home" width="58" height="58"></a>
    <nav class="menu" aria-label="Main">
      {menu}
    </nav>
    <a class="btn btn-go" href="./">Find a tour</a>
    <details class="burger" id="menu-mobile">
      <summary>Menu</summary>
      <nav aria-label="Main (mobile)">
      {menu}
      </nav>
    </details>
  </div>
</header>'''

FOOTER = f'''<footer>
  <div class="in">
    <div>
      <a class="brand" href="./"><img src="img/logo.png" alt="Cigala Cycling Tours" width="76" height="76"></a>
      <p class="tag-line">Memorable adventures. New friends.<br>Shared passion. Lifetime experience.</p>
    </div>
    <div>
      <h4>Tours</h4>
      <ul>
        <li><a href="./">All Tours</a></li>
        <li><a href="{L}/trips/granfondo-trips/" {EXT}>Gran Fondo Tours</a></li>
        <li><a href="{L}/italian-trips/" {EXT}>Italian Tours</a></li>
        <li><a href="{L}/trips/gravel-trips/" {EXT}>Gravel Tours</a></li>
        <li><a href="{L}/trips/private-trips/" {EXT}>Custom Tours</a></li>
      </ul>
    </div>
    <div>
      <h4>Contact</h4>
      <ul>
        <li>tours@cigalacycling.com</li>
        <li>+353 404 78107</li>
        <li><a href="https://wa.me/message/WVBRO6XAMQMCH1" {EXT}>WhatsApp</a> · <a href="https://www.instagram.com/cigalacycling/" {EXT}>Instagram</a> · <a href="https://www.facebook.com/CigalaCycling/" {EXT}>Facebook</a></li>
        <li><a href="https://www.youtube.com/@cigalacycling" {EXT}>YouTube</a> · <a href="https://www.tiktok.com/@cigalacycling" {EXT}>TikTok</a> · <a href="https://x.com/CigalaCycling" {EXT}>X</a> · <a href="https://www.threads.com/@cigalacycling" {EXT}>Threads</a></li>
      </ul>
    </div>
  </div>
  <div class="legal"><div class="in">
    <span>© 2026 Cigala Cycling Tours Ltd</span>
    <span>VAT No: IE4385007EH · Company Registration No: 780307</span>
    <a href="{L}/terms-conditions/" {EXT}>Refund/cancellation policy &amp; terms</a>
  </div></div>
</footer>'''

RIBBON = '<div class="ribbon"><div class="in"><b>Design preview</b><span>The new Tours pages in the Cigala Cycling brand. Text and photos come from the live site; the menu moves between the preview pages, other links go to the live site.</span></div></div>'

PARTNERS = '''<section>
  <div class="in partners">
    <div class="panel"><div class="lab">Official tour operator</div><div class="logos"><span><img src="img/logo-mdd.png" alt="Logo Maratona Dles Dolomites" loading="lazy"></span></div></div>
    <div class="panel"><div class="lab">Official event entry packages</div><div class="logos"><span><img src="img/logo-lombardia.png" alt="Gran Fondo Il Lombardia logo" loading="lazy"></span><span><img src="img/logo-strade.png" alt="Strade Bianche Gran Fondo logo" loading="lazy"></span></div></div>
    <div class="panel"><div class="lab">Official event partner</div><div class="logos"><span><img src="img/logo-algarve.png" alt="Algarve Granfondo logo" loading="lazy"></span></div></div>
  </div>
</section>'''

def page(title, cur, main, full=True, script=''):
    head = f'''<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700&display=swap">
<style>{css}{EXTRA}</style>'''
    body = f'<div class="topo" aria-hidden="true"></div>\n<div class="page">\n{RIBBON}\n{header(cur)}\n{main}\n{FOOTER}\n</div>\n{script}'
    if not full:
        return head + '\n' + body + '\n'
    return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'

def head_block(eyebrow, h, lede='', tag='h2', right=''):
    l = f'<p class="lede">{lede}</p>' if lede else ''
    return f'<div class="head"><div><div class="eyebrow">{eyebrow}</div><{tag}>{h}</{tag}><div class="bar"></div>{l}</div>{right}</div>'

def md(x):
    x = E(x)
    x = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', x, flags=re.S)
    x = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', lambda m: f'<a href="{m.group(2)}" {EXT}>{m.group(1)}</a>', x)
    return x.replace('**', '')

def tokens(path):
    out = []
    for ln in open(path).read().split('\n'):
        m = re.match(r'^(H[1-6]|P|LI|TXT|LABEL|BUTTON): ?(.*)$', ln)
        if m:
            out.append([m.group(1), m.group(2)])
        elif ln.startswith('<img'):
            mm = re.match(r"<img (\S+) alt=(['\"])(.*)\2>", ln)
            out.append(['IMG', (mm.group(1), mm.group(3)) if mm else (ln, '')])
        elif out and out[-1][0] != 'IMG':
            out[-1][1] += '\n' + ln
    return out

def paras(t):
    return [p.strip() for p in re.split(r'\n\s*\n|\n', t) if p.strip()]

# ===================== 1. BIKE TOURS (index) =====================
man = {t['slug']: t for t in json.load(open(S + 'cards/pub/manifest.json'))['tours']}
SLUGMAP = {'lake-garda-and-stelvio': 'lake-garda-stelvio', 'lake-como-gran-fondo-il-lombardia': 'lake-como-il-lombardia'}
tk = tokens(TP + 'trips.txt')
intro = tk[1][1]
custom_line = tk[2][1]
i = [k for k, t in enumerate(tk) if t[0] == 'H3' and 'CALENDAR' in t[1]][0] + 1
trips = []
cur = None
for typ, val in tk[i:]:
    if typ == 'H2' and not val.startswith('['):
        cur = {'name': val.strip(), 'h4': []}; trips.append(cur)
    elif cur is None:
        continue
    elif typ == 'H3' and 'loc' not in cur:
        cur['loc'] = val.strip()
    elif typ == 'H4':
        cur['h4'].append(val.replace('​', '').strip())
    elif typ in ('H5', 'H2') and 'MORE DETAILS' in val:
        cur['more'] = re.search(r'\((https[^)]+)\)', val).group(1)
    elif typ == 'H5' and 'BOOK NOW' in val:
        cur['book'] = re.search(r'\((https[^)]+)\)', val).group(1)
    elif typ == 'P' and 'Prices in GBP' in val:
        footnote = val
NAMEFIX = {'LAKE GARDA &': 'LAKE GARDA & STELVIO', 'LAKE GARDA & STELVIO': 'LAKE GARDA & STELVIO', 'MARATONA DLES DOLOMITES - ENEL': 'MARATONA DLES DOLOMITES – ENEL'}
rows = []
for t in trips:
    nm = ' '.join(t['name'].split())
    name = NAMEFIX.get(nm, nm)
    if name.isupper():
        ws = name.title().replace("'S ", "'s ").split(' ')
        name = ' '.join(w.lower() if i and w.lower() in ('the', 'of', 'to', 'and', 'dles') else w for i, w in enumerate(ws))
    nights, rest = t['h4'][0], t['h4'][1:]
    desc = []; level = ''; early = ''; price = ''
    for x in rest:
        if x.startswith('Level:'): level = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', x[6:]).strip()
        elif x.lower().startswith('early bird'): early = x
        elif re.search(r'[€£\$]\d', x): price = x
        else: desc.append(x)
    slug = t['more'].rstrip('/').split('/')[-1]
    cs = SLUGMAP.get(slug, slug)
    c = man[cs]
    tags = c['tags']
    k = 'gravel' if 'GRAVEL' in tags else ('gf' if 'GRAN FONDO' in tags else 'road')
    tagh = ''.join(f'<span class="tag{" gravel" if g == "GRAVEL" else " dot"}">{E(g.title())}</span>' for g in tags)
    more = t['more'] if t['more'].endswith('/') else t['more'] + '/'
    dp = ''.join(f'<p>{md(p)}</p>' for d in desc for p in paras(d))
    pfrom = 'From' if price.lower().startswith('from') else 'Price'
    pval = re.sub(r'^From\s*', '', price, flags=re.I)
    earlyh = f'<span class="early">{E(early)}</span>' if early else ''
    rows.append(f'''<article class="panel trip" data-k="{k}">
  <a class="cimg" href="{more}" {EXT}><img src="cards/{cs}.jpg" alt="{E(c['alt'])}" loading="lazy" width="1100" height="1375"></a>
  <div class="tx">
    <div class="tags">{tagh}</div>
    <h2>{E(name)}</h2>
    <h3 class="where">{E(t['loc'])}</h3>
    <div class="meta"><span class="chip-s chip km">{E(nights)}</span><span class="chip">{E("Level: " + level)}</span></div>
    <div class="desc">{dp}</div>
    <div class="bottom">
      <div><div class="price"><small>{pfrom}</small>{E(pval)}</div>{earlyh}</div>
      <div class="ctas"><a class="btn btn-ghost" href="{more}" {EXT}>More details</a><a class="btn btn-go" href="{t['book']}" {EXT}>Book now →</a></div>
    </div>
  </div>
</article>''')
intro_html = ''.join(f'<p>{md(p)}</p>' for p in paras(intro))
fn = md(footnote.replace('[*****', '*').replace('[ ](None)', ''))
main = f'''<div class="hero phero">
  <img src="img/lg-gal-unnamed-2026-06-23T075405.720.jpg" alt="Cigala Cycling Tours group celebrating with arms raised on a coastal road">
  <div class="in">
    <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / Bike tours</div>
    <div class="pill-eyebrow">2027 season · road &amp; gravel</div>
    <h1>Upcoming bike tours</h1>
    <div class="bar"></div>
    <div class="lede">{intro_html}</div>
    <p class="lede" style="margin-top:10px">{md(custom_line)}</p>
  </div>
</div>
<section id="calendar" style="padding-top:44px">
  <div class="in">
    {head_block('All public tours', '2027 Calendar', right='<div class="filters" role="group" aria-label="Filter tours"><button class="chip" type="button" id="f-all" data-f="all" aria-pressed="true">All</button><button class="chip" type="button" id="f-road" data-f="road" aria-pressed="false">Road</button><button class="chip" type="button" id="f-gf" data-f="gf" aria-pressed="false">Gran Fondo</button><button class="chip" type="button" id="f-gravel" data-f="gravel" aria-pressed="false">Gravel</button></div>', tag='h2')}
    <div class="trips" id="trip-list">
{chr(10).join(rows)}
    </div>
    <p class="footnote">{fn}</p>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      <img src="img/dest-private-custom-tours.jpg" alt="" loading="lazy">
      <div class="tx">
        <div class="eyebrow">Custom tours</div>
        <h2>Can't find the perfect one?</h2>
        <div class="bar"></div>
        <p class="lede">Build your own tour. Choose your dates, location, distances and much more.</p>
        <div class="ctas"><a class="btn btn-go" href="{L}/trips/private-trips/" {EXT}>Plan your custom tour →</a></div>
      </div>
    </div>
  </div>
</section>
{PARTNERS}'''
FILTER_JS = '''<script>
(function () {
  var chips = document.querySelectorAll('.chip[data-f]');
  var rows = document.querySelectorAll('#trip-list .trip');
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      var f = c.getAttribute('data-f');
      chips.forEach(function (x) { x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); });
      rows.forEach(function (r) { var k = r.getAttribute('data-k'); r.hidden = !(f === 'all' || k === f || (f === 'road' && k === 'gf')); });
    });
  });
})();
</script>'''
open(OUT + 'index.html', 'w').write(page('Cigala Tours Pages', './', main, full=False, script=FILTER_JS))

# ===================== 2. DESTINATIONS =====================
countries = [('Italy', 'italy'), ('France', 'france'), ('Slovenia', 'slovenia'), ('Croatia', 'croatia'), ('Portugal', 'portugal'), ('Spain', 'spain'), ('Cyprus', 'cyprus'), ('Switzerland', 'swizerland'), ('Ireland', 'ireland'), ('Greece', 'greece'), ('Belgium', 'belgium')]
cslug = {'Switzerland': 'switzerland'}
cc = ''.join(f'<a class="dcard" href="{L}/destinations/{cslug.get(n, n.lower())}/" {EXT}><img src="img/dest-{k}.jpg" alt="Cycling in {n}" loading="lazy"><div class="tx"><h3>{n}</h3><span class="go">View destination →</span></div></a>' for n, k in countries)
regions = [('Tuscany', 'tuscany'), ('Lake Garda', 'lake-garda'), ('Alps & Dolomites', 'alps-dolomites'), ('French Alps', 'french-alps'), ('Algarve', 'algarve'), ('Pyrenees', 'pyrenees'), ('Lake Como', 'lake-como'), ('Corsica', 'corsica'), ('Girona', 'girona'), ('Sardinia', 'sardinia'), ('Costa Blanca', 'costa-blanca'), ('Sicily', 'sicily'), ('Mallorca', 'mallorca'), ('Gran Canaria', 'gran-canaria'), ('Puglia', 'puglia'), ('Tenerife', 'tenerife')]
rr = ''.join(f'<a class="panel region" href="{"destination-lake-garda.html" if k == "lake-garda" else L + "/destinations/" + k + "/"}"{"" if k == "lake-garda" else " " + EXT}><h3>{E(n)}</h3><span>View →</span></a>' for n, k in regions)
dtk = tokens(TP + 'destinations.txt')
dintro = ''.join(f'<p>{md(p)}</p>' for p in paras(dtk[1][1]))
ult = [v for t, v in dtk if t == 'P' and v.startswith('We have selected')][0]
main = f'''<div class="hero phero">
  <img src="img/dest-italy.jpg" alt="Coastal road cut into the cliffs above Lake Garda">
  <div class="in">
    <div class="crumbs"><a href="./">Home</a> / Destinations</div>
    <div class="pill-eyebrow">Where we ride</div>
    <h1>Destinations</h1>
    <div class="bar"></div>
    <div class="lede">{dintro}</div>
    <div class="ctas"><a class="btn btn-go" href="#countries">Explore countries</a><a class="btn btn-ghost" href="#regions">Explore regions</a></div>
  </div>
</div>
<section id="countries" style="padding-top:44px">
  <div class="in">
    {head_block('Countries', 'Browse by country')}
    <div class="dgrid">{cc}</div>
  </div>
</section>
<section id="regions">
  <div class="in">
    {head_block('Regions', 'Browse by region')}
    <div class="regions">{rr}</div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      <img src="img/lg-01098812.jpg" alt="" loading="lazy">
      <div class="tx">
        <div class="eyebrow">Every destination</div>
        <h2>Your ultimate cycling holiday</h2>
        <div class="bar"></div>
        <p class="lede">{md(ult)}</p>
        <div class="ctas"><a class="btn btn-go" href="./">View all trips →</a><a class="btn btn-ghost" href="{L}/trips/private-trips/" {EXT}>Private/custom tours</a></div>
      </div>
    </div>
  </div>
</section>
{PARTNERS}'''
open(OUT + 'destinations.html', 'w').write(page('Cigala Tours Destinations', 'destinations.html', main))

# ===================== 3. DESTINATION: LAKE GARDA =====================
ltk = tokens(TP + 'destinations_lake-garda.txt')
h4s = [v for t, v in ltk if t == 'H4']
intro3 = h4s[:3]; food = h4s[3]
facts = h4s[4:8]
ICON = {
 'LOCATION': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',
 'CLIMATE': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/></svg>',
 'CUISINE': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3h8l-.5 6a3.5 3.5 0 0 1-7 0L8 3zM12 12.5V20M8.5 20.5h7"/></svg>',
 'TERRAIN': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 19.5 9 8l4 6.5 2.5-3.5 6 8.5z"/></svg>'}
fh = ''.join(f'<div class="panel fact"><div class="ic">{ICON[n]}</div><div><h3>{n.title()}</h3>{"".join(f"<p>{md(p)}</p>" for p in paras(v))}</div></div>' for n, v in zip(['LOCATION', 'CLIMATE', 'CUISINE', 'TERRAIN'], facts))
lp = [v for t, v in ltk if t == 'P']
upcoming_p, garda1_p, garda2_p, custom_p = lp[0], lp[1], lp[2], lp[3]
customs = [('Italian Luxury Lakes', lp[4], 'lg-italian-luxury-lakes'), ('Lake Garda Classic', lp[5], 'lg-lake-garda-classic'), ('Lake Garda & Dolomites', lp[6], 'lg-lake-garda-dolomites')]
can = lp[7]
custh = ''.join(f'<a class="panel tcard" href="{L}/trips/private-trips/" {EXT}><div class="ph"><img src="img/{img}.jpg" alt="{E(n)} custom cycling tour" loading="lazy"><span class="tag dot">Road</span></div><div class="tx"><h3>{E(n)}</h3><p>{md(p)}</p><span class="go">Enquire tour →</span></div></a>' for n, p, img in customs)
gal = ['lg-gal-unnamed-3-1', 'lg-gal-unnamed-2-1', 'lg-gal-unnamed-1-1', 'lg-gal-unnamed-5-1', 'lg-gal-unnamed-4-1', 'lg-gal-unnamed-22']
galalt = ['Three cyclists climb a coastal road above Lake Garda', 'Aerial view of a coastal cliff road', 'Aerial view of the Lake Garda hills', 'Cyclists ride a winding road', 'Cyclists on a scenic cliffside road', 'Aerial view of boats and cars on the lakefront']
galh = ''.join(f'<img src="img/{g}.jpg" alt="{a_}" loading="lazy">' for g, a_ in zip(gal, galalt))
main = f'''<div class="hero phero">
  <img src="img/lg-gal-unnamed-21.jpg" alt="Lake Garda seen from the mountains above Riva">
  <div class="in">
    <div class="crumbs"><a href="./">Home</a> / <a href="destinations.html">Destinations</a> / Lake Garda</div>
    <div class="pill-eyebrow">Italy's hidden paradise</div>
    <h1>Cycling in Lake Garda</h1>
    <div class="bar"></div>
    <div class="ctas"><a class="btn btn-go" href="#garda-tours">Upcoming Lake Garda tours →</a><a class="btn btn-ghost" href="#garda-custom">Custom tours</a></div>
  </div>
</div>
<section style="padding-top:44px">
  <div class="in split">
    <div class="prose">
      <div class="eyebrow">Why Lake Garda</div>
      <h2>No better place for cycling</h2>
      <div class="bar" style="margin-bottom:18px"></div>
      {''.join(f"<p>{md(p)}</p>" for x in intro3 for p in paras(x))}
    </div>
    <div class="gal3" style="grid-template-columns:minmax(0,1fr)"><img src="img/lg-gal-unnamed-2026-06-23T075405.720.jpg" alt="Cigala Cycling Tours group celebrating above Lake Garda" loading="lazy" style="aspect-ratio:4/5"></div>
  </div>
</section>
<section>
  <div class="in">
    <div class="gal3">{galh}</div>
    <div class="prose panel" style="padding:22px 24px;margin-top:16px">{''.join(f"<p>{md(p)}</p>" for p in paras(food))}</div>
  </div>
</section>
<section>
  <div class="in">
    {head_block('Good to know', 'Lake Garda facts')}
    <div class="facts4">{fh}</div>
  </div>
</section>
<section id="garda-tours">
  <div class="in">
    {head_block('2027 season', 'Upcoming Lake Garda tours', md(upcoming_p))}
    <div class="tcards">
      <a class="panel tcard" href="{L}/trips/lake-garda-and-stelvio/" {EXT}><div class="ph"><img src="img/lg-lake-garda-day-trip-to-passo-stelvio.jpg" alt="Lake Garda and Stelvio cycling tour" loading="lazy"><span class="tag dot">Road</span></div><div class="tx"><h3>Lake Garda &amp; day trip to Passo Stelvio</h3><p>{md(garda1_p)}</p><span class="go">View tour →</span></div></a>
      <a class="panel tcard" href="{L}/trips/lake-garda-gravel/" {EXT}><div class="ph"><img src="img/lg-lake-garda-gravel.jpg" alt="Lake Garda gravel cycling tour among the vineyards" loading="lazy"><span class="tag gravel">Gravel</span></div><div class="tx"><h3>Lake Garda Gravel</h3><p>{md(garda2_p)}</p><span class="go">View tour →</span></div></a>
    </div>
  </div>
</section>
<section id="garda-custom">
  <div class="in">
    {head_block('Custom tours', 'Most popular Lake Garda custom tours', md(custom_p))}
    <div class="tcards">{custh}</div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      <img src="img/lg-01098812.jpg" alt="" loading="lazy">
      <div class="tx">
        <div class="eyebrow">Custom tours</div>
        <h2>Can't find the perfect one?</h2>
        <div class="bar"></div>
        <p class="lede">Build your tour with us. Choose your dates, location, distances and much more.</p>
        <div class="ctas"><a class="btn btn-go" href="{L}/trips/private-trips/" {EXT}>Learn more →</a></div>
      </div>
    </div>
  </div>
</section>'''
open(OUT + 'destination-lake-garda.html', 'w').write(page('Cycling in Lake Garda', 'destinations.html', main))

# ===================== 4. GUIDES =====================
gtk = tokens(TP + 'guides.txt')
gintro = [v for t, v in gtk if t == 'H2'][0]
cards = []
imgs = [v for t, v in gtk if t == 'IMG']
titles = [v for t, v in gtk if t == 'H1'][1:]
excerpts = [v for t, v in gtk if t == 'TXT' and 'Read More' in v]
for idx, (ttl, img, ex) in enumerate(zip(titles, imgs, excerpts)):
    m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', ttl)
    name, url = m.group(1), m.group(2)
    exc = re.split(r'\s*\[', ex.replace('Read More', '').replace('Continue Reading ...', ''))[0].strip()
    href = 'guide-lake-como.html' if 'lake-como' in url else url
    ext = '' if href.endswith('.html') else ' ' + EXT
    cards.append(f'<a class="panel gcard" href="{href}"{ext}><div class="ph"><img src="img/guides-{idx}.jpg" alt="{E(img[1])}" loading="lazy"></div><div class="tx"><span class="by">By Tours Director Matteo Cigala</span><h2>{E(name)}</h2><p>{E(exc)}</p><span class="go">Read more →</span></div></a>')
main = f'''<div class="hero plain-hero">
  <div class="in">
    <div class="crumbs"><a href="./">Home</a> / Guides</div>
    <div class="eyebrow">Plan your trip</div>
    <h1>Cycling guides &amp; tips</h1>
    <div class="bar"></div>
    <p class="lede">{md(gintro)}</p>
  </div>
</div>
<section style="padding-top:40px">
  <div class="in">
    <div class="ggrid">{''.join(cards)}</div>
    <div class="ctas" style="justify-content:center;margin-top:28px"><a class="btn btn-ghost" href="{L}/guides/" {EXT}>Continue reading: all guides →</a></div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      <img src="img/dest-croatia.jpg" alt="" loading="lazy">
      <div class="tx">
        <div class="eyebrow">Ride it with us</div>
        <h2>Ready for your next cycling adventure?</h2>
        <div class="bar"></div>
        <div class="ctas"><a class="btn btn-go" href="./">Explore tours →</a></div>
      </div>
    </div>
  </div>
</section>'''
open(OUT + 'guides.html', 'w').write(page('Cigala Cycling Guides', 'guides.html', main))

# ===================== 5. GUIDE: LAKE COMO =====================
ctk = tokens(TP + 'guides_cycling-lake-como.txt')
end = [k for k, t in enumerate(ctk) if t[0] == 'H2' and t[1].strip() == 'CIGALA CYCLING TOURS'][0]
body = []
imgi = 0
ul = []
def flush_ul():
    global ul
    if ul:
        body.append('<ul>' + ''.join(f'<li>{md(x)}</li>' for x in ul) + '</ul>'); ul = []
faq_mode = False; faqs = []; related = False; sig = ''
for typ, val in ctk[1:end]:
    if typ != 'LI': flush_ul()
    if typ == 'H2' and val.startswith('By '):
        continue
    if typ == 'IMG':
        if 'Signature' in val[1]: continue
        body.append(f'<figure><img src="img/guides_cycling-lake-como-{imgi}.jpg" alt="{E(val[1])}" loading="lazy"></figure>'); imgi += 1
        if imgi == 1: pass
        continue
    if typ == 'H2':
        faq_mode = val.strip().startswith('Frequently'); related = val.strip().startswith('Related')
        body.append(f'<h2 id="{re.sub(r"[^a-z]+","-",val.lower()).strip("-")}">{E(val.strip())}</h2>')
        if faq_mode: body.append('<div class="faq">@@FAQ@@</div>')
        continue
    if typ == 'TXT':
        body.append(f'<p class="intro">{md(val.strip())}</p>'); continue
    if typ == 'LI':
        ul.append(val.strip()); continue
    if typ == 'P':
        v = val.strip()
        if v.startswith('— Matteo'):
            sig = v; continue
        if faq_mode:
            m = re.match(r'\*\*(.+?)\*\*\s*(.*)', v.replace('\n', ' '), re.S)
            if m: faqs.append((m.group(1).strip(), m.group(2).strip())); continue
        mm = re.fullmatch(r'\*\*(.+?)\*\*', v)
        if mm:
            body.append(f'<h3>{E(mm.group(1))}</h3>'); continue
        body.append(f'<p>{md(v)}</p>')
flush_ul()
# fix: the second FAQ repeats the Ghisallo question but answers about the Muro di Sormano
fixed = []
seen = set()
for q, an in faqs:
    if q in seen and 'Ghisallo' in q: q = 'How hard is the Muro di Sormano?'
    seen.add(q); fixed.append((q, an))
faqh = ''.join(f'<details id="faq-{n}"{" open" if n == 0 else ""}><summary>{E(q)}</summary><p>{md(an)}</p></details>' for n, (q, an) in enumerate(fixed))
art = '\n'.join(body).replace('@@FAQ@@', faqh)
sigtxt = sig.replace('— Matteo Cigala', '').strip()
main = f'''<div class="hero phero">
  <img src="img/guides_cycling-lake-como-0.jpg" alt="Cigala Cycling Tours group by Lake Como">
  <div class="in">
    <div class="crumbs"><a href="./">Home</a> / <a href="guides.html">Guides</a> / Cycling Lake Como</div>
    <div class="pill-eyebrow">Climb guide · Italy</div>
    <h1 style="max-width:22ch;font-size:clamp(36px,5.6vw,64px)">Cycling Lake Como: Ghisallo, Sormano and the Giro di Lombardia Roads</h1>
    <div class="bar"></div>
  </div>
</div>
<section style="padding-top:40px">
  <div class="in">
    <article class="panel article">
      <p class="by">By Tours Director Matteo Cigala</p>
      {art.replace('<figure><img src="img/guides_cycling-lake-como-0.jpg"', '<figure hidden><img src="img/guides_cycling-lake-como-0.jpg"', 1)}
      <div class="author"><img src="img/guides_cycling-lake-como-4.jpg" alt="Matteo Cigala" loading="lazy"><div><b>Matteo Cigala</b><span>{E(sigtxt)}</span></div></div>
    </article>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      <img src="img/guides_cycling-lake-como-1.jpg" alt="" loading="lazy">
      <div class="tx">
        <div class="eyebrow">Ride it with us</div>
        <h2>Lake Como, Gran Fondo Il Lombardia &amp; Pro Race</h2>
        <div class="bar"></div>
        <p class="lede">6–11 October 2027 · Ghisallo, Sormano and the Lombardia roads, guided by our team.</p>
        <div class="ctas"><a class="btn btn-go" href="{L}/trips/lake-como-gran-fondo-il-lombardia/" {EXT}>View the tour →</a><a class="btn btn-ghost" href="{L}/trips/private-trips/" {EXT}>Custom tour</a></div>
      </div>
    </div>
  </div>
</section>'''
open(OUT + 'guide-lake-como.html', 'w').write(page('Cycling Lake Como Guide', 'guides.html', main))

# ===================== 6. ABOUT =====================
atk = tokens(TP + 'about.txt')
stop = [k for k, t in enumerate(atk) if t[0] == 'H2' and 'WHY RIDERS' in t[1]][0]
story = ''.join(f'<p>{md(v.strip())}</p>' for t, v in atk[1:stop] if t == 'P')
why = []
team_start = [k for k, t in enumerate(atk) if t[0] == 'H2' and 'OUR TEAM' in t[1]][0]
for t, v in atk[stop + 1:team_start]:
    if t == 'P':
        m = re.match(r'\*\*✔\s*(.+?)\*\*\s*(.*)', v, re.S)
        if m: why.append((m.group(1).strip(), m.group(2).strip()))
whyh = ''.join(f'<div class="panel"><span class="tick" aria-hidden="true"></span><div><h3>{E(h)}</h3><p>{md(p)}</p></div></div>' for h, p in why)
ps = [v.strip().replace('\n', ' ') for t, v in atk[team_start + 1:] if t == 'P']
ready_i = [k for k, t in enumerate(atk) if t[0] == 'H2' and 'READY' in t[1]][0]
ps = [v.strip().replace('\n', ' ') for t, v in atk[team_start + 1:ready_i] if t == 'P']
team = list(zip(ps[0::2], ps[1::2]))
def tkey(n):
    return re.sub(r'[^a-z]+', '-', n.lower().replace('’', '').replace('‘', '').replace('“', '').replace('”', '')).strip('-')
import os
th = []
for n, role in team:
    k = tkey(n)
    cand = [f for f in os.listdir(OUT + 'img') if f.startswith('team-') and f[5:-4].replace('-', '') == k.replace('-', '')]
    src = cand[0] if cand else None
    disp = n.replace('GIAMPIETRO ‘GIAMPI’', 'Giampietro “Giampi”')
    disp = ' '.join(w.capitalize() if not w.startswith('“') else '“' + w[1:].capitalize() for w in disp.split()) if disp.isupper() or '“' in disp else disp
    img = f'<img src="img/{src}" alt="{E(disp)}, {E(role)} at Cigala Cycling Tours" loading="lazy">' if src else ''
    th.append(f'<div class="panel member">{img}<div class="tx"><h3>{E(disp)}</h3><p>{E(role)}</p></div></div>')
ready_p = [v for t, v in atk if t == 'P' and v.startswith('Join us')][0]
main = f'''<div class="hero plain-hero">
  <div class="in">
    <div class="crumbs"><a href="./">Home</a> / About</div>
    <div class="eyebrow">About Cigala Cycling Tours</div>
    <h1>Our story</h1>
    <div class="bar"></div>
  </div>
</div>
<section style="padding-top:40px">
  <div class="in story">
    <div class="panel prose" style="padding:clamp(22px,4vw,40px)">{story}</div>
    <div class="photo"><img src="img/team-matteo.jpg" alt="Matteo Cigala, founder and Tours Director, in the white Cigala Cycling jersey" loading="lazy"></div>
  </div>
</section>
<section>
  <div class="in">
    {head_block('The difference', 'Why riders choose us')}
    <div class="why6">{whyh}</div>
  </div>
</section>
<section>
  <div class="in">
    {head_block('Who rides with you', 'Our team')}
    <div class="team">{''.join(th)}</div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      <img src="img/team-why-riders-choose-us.jpg" alt="" loading="lazy">
      <div class="tx">
        <div class="eyebrow">Join us</div>
        <h2>Ready to ride with us?</h2>
        <div class="bar"></div>
        <p class="lede">{md(ready_p)}</p>
        <div class="ctas"><a class="btn btn-go" href="./">View upcoming tours →</a></div>
      </div>
    </div>
  </div>
</section>
{PARTNERS}'''
open(OUT + 'about.html', 'w').write(page('About Cigala Cycling Tours', 'about.html', main))

# ===================== 7. CONTACT =====================
ic_mail = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'
ic_phone = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M11 18h2"/></svg>'
ic_soc = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="m8.2 10.8 7.6-4.6M8.2 13.2l7.6 4.6"/></svg>'
main = f'''<div class="hero plain-hero">
  <div class="in">
    <div class="crumbs"><a href="./">Home</a> / Contact</div>
    <div class="eyebrow">Get in touch</div>
    <h1>Contact us</h1>
    <div class="bar"></div>
    <p class="lede">Questions about a tour, dates, bikes or a custom trip? Send us a message, call, or reach us on WhatsApp.</p>
  </div>
</div>
<section style="padding-top:40px">
  <div class="in contact-grid">
    <div class="panel cpanel">
      <form class="form" id="contact-form" novalidate>
        <label for="f-name"><span>Name</span><input id="f-name" name="name" type="text" placeholder="Name" autocomplete="name"></label>
        <label for="f-email"><span>Email <i>*</i></span><input id="f-email" name="email" type="email" placeholder="Email" autocomplete="email" required></label>
        <label for="f-msg"><span>Message</span><textarea id="f-msg" name="message" placeholder="Your Message"></textarea></label>
        <button class="btn btn-go" type="submit">Send →</button>
        <p class="fnote" role="status"></p>
      </form>
    </div>
    <div class="panel cpanel info">
      <div class="row"><div class="ic">{ic_mail}</div><div><h2>Email</h2><div class="val">tours@cigalacycling.com</div></div></div>
      <div class="row"><div class="ic">{ic_phone}</div><div><h2>Phone</h2><div class="val">+353 404 78107</div></div></div>
      <div class="row"><div class="ic">{ic_soc}</div><div><h2>Follow us online</h2></div></div>
      <div class="social">
        <a href="https://wa.me/message/WVBRO6XAMQMCH1" {EXT}>WhatsApp</a>
        <a href="https://www.instagram.com/cigalacycling/" {EXT}>Instagram</a>
        <a href="https://www.facebook.com/CigalaCycling/" {EXT}>Facebook</a>
        <a href="https://www.youtube.com/@cigalacycling" {EXT}>YouTube</a>
        <a href="https://www.tiktok.com/@cigalacycling" {EXT}>TikTok</a>
        <a href="https://x.com/CigalaCycling" {EXT}>X</a>
        <a href="https://www.threads.com/@cigalacycling" {EXT}>Threads</a>
      </div>
    </div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      <img src="img/dest-private-custom-tours.jpg" alt="" loading="lazy">
      <div class="tx">
        <div class="eyebrow">Planning a group trip?</div>
        <h2>Build your own tour</h2>
        <div class="bar"></div>
        <p class="lede">Choose your dates, location, distances and much more.</p>
        <div class="ctas"><a class="btn btn-go" href="{L}/trips/private-trips/" {EXT}>Custom tours →</a><a class="btn btn-ghost" href="./">Upcoming tours</a></div>
      </div>
    </div>
  </div>
</section>'''
FORM_JS = '<script>document.querySelectorAll("form.form").forEach(f=>f.addEventListener("submit",e=>{e.preventDefault();f.querySelector(".fnote").textContent="Preview only: on the live site this sends your message to tours@cigalacycling.com.";}));</script>'
open(OUT + 'contact.html', 'w').write(page('Contact Cigala Tours', 'contact.html', main, script=FORM_JS))
print('built', len(rows), 'tours;', len(team), 'team;', len(cards), 'guides;', len(fixed), 'faqs;', len(why), 'why')

# ---- Matteo-approved content fixes (applied after build) ----
import shutil as _sh
from PIL import Image as _Im
_O = OUT
def _fix(fn, pairs):
    p = _O + fn; s = open(p).read()
    for a, b in pairs:
        assert a in s, (fn, a[:60]); s = s.replace(a, b)
    open(p, 'w').write(s)
_fix('index.html', [('<p>Quiet roads and a stunning coastline make this region unforgettable.</p>', ''),
                    ('href="https://retail.cigalacycling.com/pages/returns"', 'href="https://tours.cigalacycling.com/terms-conditions/"')])
_fix('destinations.html', [('href="https://tours.cigalacycling.com/destinations/belgium/"', 'href="https://tours.cigalacycling.com/trips/tour-of-flanders-experience/"')])
print('fixes applied')
