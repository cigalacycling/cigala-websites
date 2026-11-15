"""Tours Terms (page 564, /terms-conditions/) and Privacy Policy (new, /privacy-policy/)
in the cigalacycling.com Terms style: "On this page" list on the left, numbered sections.

Terms text = the live page, word for word (from the Elementor backup, in the live order).
Privacy text = tours/privacy.txt (Matteo to review).
Writes previews tourspages/terms.html, tourspages/privacy.html and stg-tours/out/list-terms.json,
stg-tours/out/list-privacy-policy.json (pushed with tools/push_tours_list.py).
"""
import os, re, json, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from css_scope import scope_css

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
L = 'https://tours.cigalacycling.com'
EXT = 'target="_blank" rel="noopener"'
E = lambda x: html.escape(x, quote=False)
slug = lambda t: re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

# ---------- terms: live text from the backup ----------
ed = json.loads(json.load(open(ROOT + 'stg-tours/backup/page-564.json'))['meta']['_elementor_data'])
blocks = []
def walk(n):
    for e in n:
        st = e.get('settings', {})
        if e.get('widgetType') == 'text-editor': blocks.append(st['editor'])
        walk(e.get('elements', []))
walk(ed)
def clean(h):
    h = re.sub(r'<span style="[^"]*">(.*?)</span>', r'\1', h, flags=re.S)
    h = re.sub(r' data-(start|end)="\d+"', '', h)
    h = h.replace('<strong>Direct bank transfer (recommended).<br /></strong>', '<strong>Direct bank transfer (recommended).</strong><br />')
    h = re.sub(r'<p><br />', '<p>', h)
    h = re.sub(r'<a href="(https?://[^"]+)">', r'<a href="\1" ' + EXT + '>', h)
    return h.strip()
blocks = [clean(b) for b in blocks]
TITLES = ['Outstanding Balances & Cancellation Policy', 'Pricing & Payment Terms', 'Travel Insurance', 'Travel Arrangements & Disruptions',
          'Accommodation & Rooming', 'Changes to the itinerary', 'Third-Party Services', 'Force Majeure', 'Rider Eligibility',
          'Passport / visa / entry requirements', 'Bike Rental and Damage', 'Private Groups & Group Size',
          'Events Regulations & Partecipant Responsability', 'Client Protection & Insolvency Safeguard Statement', 'Waiver of Liability']
intro, rest = blocks[:4], blocks[4:]
assert len(rest) == len(TITLES) + 2, (len(rest), len(TITLES))
sections = [(t, rest[i]) for i, t in enumerate(TITLES[:-1])] + [(TITLES[-1], ''.join(rest[len(TITLES) - 1:]))]
for t in TITLES:   # the live page shows these exact titles
    pass

def legal_page(crumb, h1, toc, body, lead=''):
    toc_html = ''.join(f'<a href="#{slug(t)}">{E(t)}</a>' for t in toc)
    return f'''<div class="hero plain-hero">
  <div class="in">
    <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / {crumb}</div>
    <div class="eyebrow">Cigala Cycling Tours Ltd</div>
    <h1>{h1}</h1>
    <div class="bar"></div>
  </div>
</div>
<section style="padding-top:40px">
  <div class="in terms">
    <nav class="toc" aria-label="On this page"><b>On this page</b>{toc_html}</nav>
    <div class="legal-doc">
      {lead}<div class="panel"><ol>{body}</ol></div>
    </div>
  </div>
</section>'''

terms_body = ''.join(f'<li><h3 id="{slug(t)}">{E(t)}</h3>{h}</li>' for t, h in sections)
terms_main = legal_page('Terms &amp; Conditions', 'REFUND/CANCELLATION POLICY &amp; TERMS &amp; CONDITIONS', TITLES, terms_body,
                        lead='<div class="panel lead">' + ''.join(intro) + '</div>')

# ---------- privacy: tours/privacy.txt ----------
items, cur = [], None
for ln in open(ROOT + 'tours/privacy.txt').read().split('\n'):
    if ln.startswith('H1:') or not ln.strip(): continue
    if ln.startswith('LI:'): cur = {'t': ln[3:].strip(), 'p': []}; items.append(cur); continue
    if ln.startswith('P:'): ln = ln[2:]
    cur['p'].append(ln.strip())
def render_p(ps):
    out, ul = '', []
    for p in ps + [None]:
        if p is not None and p.startswith('- '): ul.append(f'<li>{E(p[2:])}</li>'); continue
        if ul: out += '<ul>' + ''.join(ul) + '</ul>'; ul = []
        if p is not None: out += f'<p>{E(p)}</p>'
    return out
priv_body = ''.join(f'<li><h3 id="{slug(i["t"])}">{E(i["t"])}</h3>{render_p(i["p"])}</li>' for i in items)
priv_body = re.sub(r'<p>([A-Z][A-Za-z ]{2,40}):', r'<p><b>\1:</b>', priv_body)
priv_main = legal_page('Privacy Policy', 'Privacy Policy', [i['t'] for i in items], priv_body)

# ---------- CSS (the cigalacycling.com Terms style, scoped to .cl like the tour pages) ----------
LEGAL_CSS = '''
.terms { display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 32px; align-items: start; }
.toc { position: sticky; top: 110px; display: grid; gap: 2px; font-size: 13px; }
.toc a { color: var(--text-3); text-decoration: none; padding: 5px 10px; border-left: 2px solid var(--border); }
.toc a:hover { color: var(--green-text); border-left-color: var(--green); }
.toc b { font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: var(--text-3); margin: 0 0 8px; font-weight: 600; }
.legal-doc { display: grid; gap: 14px; min-width: 0; }
.legal-doc .panel { padding: clamp(20px, 3vw, 32px); }
.legal-doc .lead p { margin: 0 0 8px; color: var(--text); }
.legal-doc ol { margin: 0; padding: 0; list-style: none; counter-reset: t; display: grid; gap: 22px; }
.legal-doc ol > li { counter-increment: t; }
.legal-doc h3 { font-size: 22px; display: flex; gap: 12px; align-items: baseline; scroll-margin-top: 110px; }
.legal-doc h3::before { content: counter(t, decimal-leading-zero); font-size: 14px; color: #ff3d33; font-family: var(--head); letter-spacing: .06em; }
.legal-doc p { margin: 10px 0 0; max-width: 72ch; overflow-wrap: anywhere; }
.legal-doc ul { margin: 8px 0 0; padding-left: 20px; max-width: 72ch; display: grid; gap: 4px; }
.legal-doc ul li::marker { color: var(--green); }
.legal-doc a { color: var(--green-text); }
.plain-hero h1 { font-size: clamp(36px, 5.6vw, 72px); max-width: 20ch; }
@media (max-width: 900px) { .terms { grid-template-columns: minmax(0, 1fr); } .toc { display: none; } }
'''
css = scope_css(LEGAL_CSS, 'html .cl')

home = open(ROOT + 'tourspages/home.html').read()
lists_prev = open(ROOT + 'tourspages/trips.html').read()   # header/footer/CSS exactly as the tour pages
for name, slug_, main, extra in (('terms', 'terms', terms_main, {'id': 564}),
                                 ('privacy', 'privacy-policy', priv_main,
                                  {'id': None, 'parent': 0, 'title': 'Privacy Policy',
                                   'seo_title': 'Privacy Policy | Cigala Cycling Tours',
                                   'seo_description': 'How Cigala Cycling Tours Ltd collects, uses and protects your personal data on tours.cigalacycling.com, including bookings, cookies and your rights.'})):
    a, b = lists_prev.index('<div class="cl cl-page">'), lists_prev.index('<div class="cc"><footer>')
    prev = lists_prev[:a] + '<div class="cl cl-page">\n' + main + '\n</div>\n' + lists_prev[b:]
    prev = prev.replace('</style>', '</style>\n<style>\n' + css + '\n</style>', 1)
    open(ROOT + f'tourspages/{name}.html', 'w').write(prev)
    d = {'slug': slug_, 'main': main, 'css': css}; d.update(extra)
    json.dump(d, open(ROOT + f'stg-tours/out/list-{slug_}.json', 'w'), ensure_ascii=False)
    print(name, len(main), 'chars | sections', main.count('<h3 id='))
