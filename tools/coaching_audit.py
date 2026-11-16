"""Full SEO and error audit of Coaching STAGING (Matteo 16 Nov 2026: "check the rest of the website that there are no errors").
Fetches every published page and post (from the REST API), then checks: title, meta description, H1 count, canonical, lang,
og:title/og:description/og:image (copies and broken images), JSON-LD validity, duplicate titles/descriptions, internal links and
images that 404, http:// mixed content, images without alt, and English fragments in Italian posts.
Writes stg-coaching/audit-<date>.json and prints a summary.
  python3 -I tools/coaching_audit.py
"""
import json, os, re, subprocess, html, datetime
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.coaching.cigalacycling.com'
S = f'https://{HOST}'
def get(url, head=False):
    a = ['curl', '-sS', '-m', '60', '-o', '/dev/null' if head else '-', '-w', '\n%{http_code}', '-L', url]
    if head: a[a.index('-sS')+1:a.index('-sS')+1] = []
    r = subprocess.run(a, capture_output=True, text=True, errors='replace')
    body, _, code = r.stdout.rpartition('\n')
    return (int(code) if code.isdigit() else 0), body
def items():
    out = []
    for t in ('pages', 'posts'):
        p = 1
        while True:
            c, b = get(f'{S}/wp-json/wp/v2/{t}?per_page=100&page={p}&_fields=id,link,categories')
            try: d = json.loads(b)
            except ValueError: break
            if not isinstance(d, list) or not d: break
            out += [(t, x['id'], x['link'], 21 in (x.get('categories') or [])) for x in d]; p += 1
    return out
G = lambda r, s: (re.search(r, s, re.S) or [None, None])[1]
def page(it):
    t, pid, url, is_it = it
    code, s = get(url + ('&' if '?' in url else '?') + 'audit=1')
    r = {'type': t, 'id': pid, 'url': url.replace(S, ''), 'code': code}
    if code != 200: return r
    r['title'] = html.unescape(G(r'<title>(.*?)</title>', s) or '').strip()
    r['desc'] = html.unescape(G(r'<meta name="description" content="([^"]*)"', s) or '')
    r['robots'] = G(r'<meta name=.robots. content=.([^"\']*)', s) or ''
    r['canonical'] = G(r'<link rel="canonical" href="([^"]*)"', s) or ''
    r['lang'] = G(r'<html[^>]*\slang="([^"]+)"', s) or ''
    r['og_title'] = html.unescape(G(r'property="og:title" content="([^"]*)"', s) or '')
    r['og_desc'] = html.unescape(G(r'property="og:description" content="([^"]*)"', s) or '')
    r['og_image'] = G(r'property="og:image" content="([^"]*)"', s) or ''
    body = s.split('<body', 1)[-1]
    r['h1'] = len(re.findall(r'<h1[\s>]', body))
    ld_bad = 0
    for blk in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
        try: json.loads(blk)
        except ValueError: ld_bad += 1
    r['ld_blocks'] = len(re.findall(r'application/ld\+json', s)); r['ld_bad'] = ld_bad
    r['http_mixed'] = sorted(set(re.findall(r'(?:src|href)="(http://[^"]+)"', body)))[:5]
    r['img_no_alt'] = len([m for m in re.findall(r'<img\b[^>]*>', body) if not re.search(r'\salt="[^"]+"', m) and 'aria-hidden' not in m and 'role="presentation"' not in m])
    r['links'] = sorted(set(u for u in re.findall(r'href="(https://' + re.escape(HOST) + r'[^"#?]*)', body) if '/wp-' not in u))
    r['imgs'] = sorted(set(re.findall(r'<img[^>]+src="(https://' + re.escape(HOST) + r'[^"]+)"', body)))
    if is_it:   # English sentences left in an Italian post (common English function words in a row)
        txt = re.sub(r'<[^>]+>', ' ', G(r'elementor-widget-theme-post-content(.*?)</section>', body) or body)
        r['en_bits'] = re.findall(r'[^.]{0,30}\b(?:the|this|with|assuming|your|course|and the|of the)\b \b(?:the|this|a|your|course|reasonable|existing|demands)\b[^.]{0,30}', txt)[:3]
    return r
if __name__ == '__main__':
    its = items(); print(len(its), 'URLs')
    with ThreadPoolExecutor(8) as ex: res = list(ex.map(page, its))
    links = sorted(set(u for r in res for u in r.get('links', []) + r.get('imgs', []) + ([r['og_image']] if r.get('og_image') else [])))
    print(len(links), 'internal links/images to check')
    with ThreadPoolExecutor(12) as ex: codes = dict(zip(links, ex.map(lambda u: get(u, head=True)[0], links)))
    P = defaultdict(list)
    tit, des, ogt = defaultdict(list), defaultdict(list), defaultdict(list)
    for r in res:
        u = r['url']
        if r['code'] != 200: P['page not 200'].append(f"{u} {r['code']}"); continue
        if not r['title']: P['no title'].append(u)
        elif len(r['title']) > 70: P['title over 70 chars'].append(f"{u} ({len(r['title'])})")
        if not r['desc']: P['no meta description'].append(u)
        elif len(r['desc']) > 165: P['description over 165 chars'].append(f"{u} ({len(r['desc'])})")
        if r['h1'] != 1: P['H1 count not 1'].append(f"{u} ({r['h1']})")
        if '2026' in r['title'] + r['desc']: P['2026 in title/description'].append(u)
        if r['ld_bad']: P['broken JSON-LD'].append(u)
        if r['http_mixed']: P['http:// links/images'].append(f"{u} {r['http_mixed'][:2]}")
        if r['img_no_alt']: P['images without alt'].append(f"{u} ({r['img_no_alt']})")
        if r.get('en_bits'): P['English text in an Italian post'].append(f"{u} {r['en_bits'][:2]}")
        if r['og_image'] and codes.get(r['og_image'], 0) >= 400: P['share image broken'].append(f"{u} {r['og_image'][-50:]}")
        if 'noindex' in r['robots'] and '/athletes' not in u: P['_info: noindex (staging is noindex everywhere)'].append(u)
        bad = [x for x in r['links'] + r['imgs'] if codes.get(x, 0) >= 400]
        if bad: P['broken internal links/images'].append(f"{u} -> {[b.replace(S, '') for b in bad][:4]}")
        tit[r['title']].append(u); des[r['desc']].append(u)
        if r['og_title'] and r['og_title'] != r['title']: ogt[r['og_title']].append(u)
    for k, v in tit.items():
        if k and len(v) > 1: P['duplicate titles'].append(f"{k[:60]} :: {v}")
    for k, v in des.items():
        if k and len(v) > 1: P['duplicate descriptions'].append(f"{k[:60]} :: {v}")
    for k, v in ogt.items():
        if len(v) > 1: P['same share title on several pages'].append(f"{k[:60]} :: {v}")
    langs = defaultdict(list)
    for r in res:
        if r['code'] == 200: langs[r.get('lang')].append(r['url'])
    out = {'date': str(datetime.date.today()), 'pages': len(res), 'problems': P, 'langs': {k: len(v) for k, v in langs.items()}, 'detail': res}
    json.dump(out, open(ROOT + f'stg-coaching/audit-{out["date"]}.json', 'w'), indent=1, ensure_ascii=False)
    print('languages:', out['langs'])
    for k, v in sorted(P.items()):
        if k.startswith('_info'): print(f'{k}: {len(v)}'); continue
        print(f'\n## {k}: {len(v)}'); [print('  ', x) for x in v[:12]]
        if len(v) > 12: print('   …', len(v) - 12, 'more')
