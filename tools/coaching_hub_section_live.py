"""Put the Athlete Hub section (packages pages) live: swaps ONLY the <div class="hb ..."> block inside each page's HTML widget
for the staging build (domain swapped), and appends the section's new CSS rules (.hb4*) to the live kit 6. Matteo's go, 18 Nov 2026.
Backups first: live-coaching/backup/hub-section-v4/. New images must already be on live media (live-coaching/hub-media.json).
  python3 -I tools/coaching_hub_section_live.py
"""
import json, re, subprocess
ROOT = '/home/user/cigala-websites/'; L = 'https://coaching.cigalacycling.com/wp-json'; BK = ROOT + 'live-coaching/backup/hub-section-v4/'
P = {3338: (1, 0), 3795: (1, 0), 6098: (4, 0), 6100: (4, 0), 6102: (4, 0), 6106: (3, 0)}
def post(url, body):
    r = subprocess.run(['curl', '-sS', '-m', '180', '-X', 'POST', url, '-H', 'Content-Type: application/json', '--data-binary', '@-'], input=json.dumps(body), capture_output=True, text=True)
    return json.loads(r.stdout or 'null')
def block(h):
    i = h.index('<div class="hb'); depth = 0
    for m in re.finditer(r'<div\b|</div>', h[i:]):
        depth += 1 if m.group(0).startswith('<div') else -1
        if depth == 0: return i, i + m.end()
def widget(els, path):
    e = {'elements': els}
    for p in path: e = e['elements'][p]
    return e
def blocks(css):
    out = []; depth = 0; start = 0
    for i, c in enumerate(css):
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: out.append(css[start:i + 1].strip()); start = i + 1
    return out
# 1. CSS
stg_css = json.load(open(ROOT + 'stg-coaching/out/lib-6.json'))['meta']['_elementor_page_settings']['custom_css']
kit = json.load(open(BK + 'lib-6.json'))['meta']['_elementor_page_settings']
new = [b for b in blocks(stg_css) if 'hb4' in b and b not in kit['custom_css']]
if new:
    kit['custom_css'] = kit['custom_css'].rstrip() + '\n/* Athlete Hub section v4: compact + fanned phones (18 Nov 2026) */\n' + '\n'.join(new) + '\n'
    r = post(f'{L}/wp/v2/elementor_library/6', {'meta': {'_elementor_page_settings': kit}}); print('kit', r.get('id'), len(new), 'rules')
# 2. pages
for pid, path in P.items():
    live = json.loads(json.load(open(BK + f'page-{pid}.json'))['meta']['_elementor_data'])
    stg = json.loads(json.load(open(ROOT + f'stg-coaching/out/page-{pid}.json'))['meta']['_elementor_data'])
    lw = widget(live, path); sh = widget(stg, path)['settings']['html'].replace('https://staging.coaching.cigalacycling.com', 'https://coaching.cigalacycling.com')
    lh = lw['settings']['html']; li, lj = block(lh); si, sj = block(sh)
    assert lh[:li] == sh[:si] and lh[lj:] == sh[sj:], f'{pid}: the rest of the widget differs, stop'
    lw['settings']['html'] = lh[:li] + sh[si:sj] + lh[lj:]
    assert 'staging.' not in sh[si:sj]
    r = post(f'{L}/wp/v2/pages/{pid}', {'meta': {'_elementor_data': json.dumps(live)}}); print('page', pid, r.get('id'), r.get('code', ''))
r = subprocess.run(['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'DELETE', f'{L}/elementor/v1/cache'], capture_output=True, text=True); print('elementor cache', r.stdout)
