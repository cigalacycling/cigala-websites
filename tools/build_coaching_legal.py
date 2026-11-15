"""Build the Coaching Terms & Conditions and Privacy Policy previews, in the cigalacycling.com Terms style
(sidebar "On this page" + numbered sections; the CSS and parsing follow tools/build.py).

  coachingpages/terms-conditions.html  live copy, live H1 and H2s (coaching/text/terms-conditions.txt)
  coachingpages/privacy-policy.html    NEW page (coaching/privacy.txt), Matteo's decision 15 Nov: one privacy page per site
"""
import os, sys, re, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *

def parse(path):
    items, waiver, h2s, target, cur = [], [], [], None, None
    target = items
    for ln in open(path).read().split('\n'):
        if ln.startswith('H1:') or not ln.strip(): continue
        if ln.startswith('H2:'): target = waiver; h2s.append(ln[3:].strip()); continue
        if ln.startswith('LI:'): cur = {'t': ln[3:].strip(), 'p': []}; target.append(cur); continue
        if ln.startswith(('P:', 'TXT:')) and cur is not None: cur['p'].append(ln.split(':', 1)[1].strip()); continue
        if cur is not None: cur['p'].append(ln.strip())
    return items, waiver, h2s

def esc(x):
    x = H.escape(x, quote=False)
    return re.sub(r'\[(https?://[^\]]+)\]\((https?://[^)]+)\)', lambda m: f'<a href="{m.group(2)}" {EXT}>{m.group(1)}</a>', x)
slug = lambda t: re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
title = lambda t: t.title() if t.isupper() else t

def render(lst):
    out = []
    for it in lst:
        ps, ul = '', []
        for p in it['p'] + [None]:
            if p is not None and p.startswith(('- ', '-')) and not p.startswith('--'):
                ul.append(f'<li>{esc(p.lstrip("- "))}</li>'); continue
            if ul: ps += '<ul>' + ''.join(ul) + '</ul>'; ul = []
            if p is not None: ps += f'<p>{esc(p)}</p>'
        out.append(f'<li><h3 id="{slug(it["t"])}">{esc(title(it["t"]))}</h3>{ps}</li>')
    return '<ol>' + ''.join(out) + '</ol>'

def doc(eyebrow, h1, crumb, items, extra_toc='', extra=''):
    toc = ''.join(f'<a href="#{slug(i["t"])}">{esc(title(i["t"]))}</a>' for i in items) + extra_toc
    return f'''<div class="hero page-hero">
  <div class="in">
    <div class="crumbs"><a href="{C}/" {EXT}>Home</a> / {crumb}</div>
    <div class="eyebrow">{eyebrow}</div>
    <h1>{h1}</h1>
    <div class="bar"></div>
  </div>
</div>

<section class="legal">
  <div class="in terms">
    <nav class="toc" aria-label="On this page"><b>On this page</b>{toc}</nav>
    <div class="legal-doc">
      <div class="panel">{render(items)}</div>{extra}
    </div>
  </div>
</section>'''

LCSS = '''<style>
.hero.page-hero { min-height: 0; display: block; overflow: visible; }
.hero.page-hero::after { display: none; }
.hero.page-hero .in { padding-block: 64px 8px; display: block; }
.page-hero h1 { font-size: clamp(44px, 7vw, 84px); max-width: none; }
.crumbs { font-size: 12.5px; color: var(--text-3); margin-bottom: 14px; }
.crumbs a { color: var(--text-3); text-decoration: none; } .crumbs a:hover { color: #fff; }
.page-hero .eyebrow { margin-bottom: 10px; }
section.legal { padding-top: 40px; }
.panel { background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: var(--r); padding: clamp(20px, 3vw, 32px); }
.terms { display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 32px; align-items: start; }
.toc { position: sticky; top: calc(env(safe-area-inset-top, 0px) + 96px); display: grid; gap: 2px; font-size: 13px; }
.toc a { color: var(--text-3); text-decoration: none; padding: 5px 10px; border-left: 2px solid var(--border); }
.toc a:hover { color: #fff; border-left-color: var(--green); }
.toc b { font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: var(--text-3); margin: 0 0 8px; font-weight: 600; }
.legal-doc { display: grid; gap: 14px; }
.legal-doc ol { margin: 0; padding: 0; list-style: none; counter-reset: t; display: grid; gap: 22px; }
.legal-doc ol > li { counter-increment: t; }
.legal-doc h3 { font-size: 22px; display: flex; gap: 12px; align-items: baseline; scroll-margin-top: 100px; }
.legal-doc h3::before { content: counter(t, decimal-leading-zero); font-size: 14px; color: var(--red-text, #ff3d33); font-family: var(--head); letter-spacing: .06em; }
.legal-doc p { margin: 10px 0 0; max-width: 72ch; overflow-wrap: anywhere; }
.legal-doc p a { color: var(--green-text); }
.legal-doc ul { margin: 8px 0 0; padding-left: 20px; max-width: 72ch; display: grid; gap: 4px; }
.legal-doc ul li::marker { color: var(--green); }
.legal-doc .waiver-head { margin-top: 14px; scroll-margin-top: 100px; }
.legal-doc .waiver-head h2 { font-size: clamp(24px, 3vw, 34px); }
.legal-doc .waiver-head .provider { font-family: var(--body); text-transform: none; font-weight: 600; font-size: 15px; color: var(--text-2); letter-spacing: 0; margin-top: 14px; }
@media (max-width: 900px) { .terms { grid-template-columns: minmax(0, 1fr); } .toc { position: static; display: none; } }
</style>'''

# ---------- Terms & Conditions (live copy) ----------
items, waiver, h2s = parse(ROOT + 'coaching/text/terms-conditions.txt')
assert len(h2s) == 2, h2s
waiver_html = f'''
      <div class="panel waiver-head" id="waiver">
        <h2>{esc(h2s[0])}</h2>
        <h2 class="provider">{esc(h2s[1])}</h2>
        <div style="margin-top:20px">{render(waiver)}</div>
      </div>'''
terms = doc('Cigala Cycling Limited', 'TERMS &amp; CONDITIONS', 'Terms &amp; Conditions', items, '<a href="#waiver">Liability waiver</a>', waiver_html)
build('terms-conditions', '/terms-conditions/', terms, 'New Terms & Conditions page: same copy, H1 and H2s as live, in the cigalacycling.com Terms style.', extra_css=LCSS)

# ---------- Privacy Policy (new page) ----------
pitems, _, _ = parse(ROOT + 'coaching/privacy.txt')
privacy = doc('Cigala Cycling Limited', 'Privacy Policy', 'Privacy Policy', pitems)
privacy = re.sub(r'<p>([A-Z][A-Za-z ]{2,40}):', r'<p><b>\1:</b>', privacy)
build('privacy-policy', '/privacy-policy/', privacy, 'NEW Privacy Policy page for the coaching site (draft for Matteo to check).', h1='Privacy Policy', extra_css=LCSS,
      new_page={'title': 'Privacy Policy | Cigala Cycling Coaching',
                'meta': 'How Cigala Cycling Coaching collects, uses and protects your personal data, and which cookies and services the coaching website uses.'})
