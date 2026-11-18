"""Put three approved staging changes live on coaching.cigalacycling.com (Matteo's go, 18 Nov 2026):
  - home (2924): "I've coached athletes from 28 countries" flags box
  - Individual packages (3338): 14-day money-back guarantee badge (Advanced, Premium), box and FAQ; Basic button fix (CSS)
  - Talent programme (896): full application form (W/kg 5s-1h, racing history) and the "After you apply" panel
Backups first: live-coaching/backup/guarantee-talent-countries/ (pages + kit, taken before this runs).
Only the listed widgets are replaced, and only after checking every other widget is identical to the staging build.
Flags must already be on live media (live-coaching/countries-flags-media.json).
  python3 -I tools/coaching_live_push_181126.py [--dry]
"""
import json, subprocess, sys
ROOT = '/home/user/cigala-websites/'; L = 'https://coaching.cigalacycling.com/wp-json'; BK = ROOT + 'live-coaching/backup/guarantee-talent-countries/'
DRY = '--dry' in sys.argv
# page -> {widget path: settings keys to take from staging}
P = {2924: {(7, 0): ['html']},
     3338: {(1, 0): ['html'], (8, 0): ['html']},
     896: {(8, 0, 0, 0): ['html'], (8, 0, 1, 1): ['success_message', 'form_fields', 'button_text']}}
# held back until Matteo OKs the new wording: allowed to differ, live kept (--with-panel puts it live)
HOLD = set() if '--with-panel' in sys.argv else {(896, (8, 0, 0, 0))}
STG = 'https://staging.coaching.cigalacycling.com'

def post(url, body):
    if DRY: return {'id': 'dry'}
    r = subprocess.run(['curl', '-sS', '-m', '180', '-X', 'POST', url, '-H', 'Content-Type: application/json', '--data-binary', '@-'], input=json.dumps(body), capture_output=True, text=True)
    return json.loads(r.stdout or 'null')

def walk(els, out, path=()):
    for i, e in enumerate(els):
        p = path + (i,)
        if e.get('elType') == 'widget': out[p] = e
        walk(e.get('elements', []), out, p)
    return out

def blocks(css):
    out = []; depth = 0; start = 0
    for i, c in enumerate(css):
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: out.append(css[start:i + 1].strip()); start = i + 1
    return out

# 1. kit CSS: append the rules the live kit lacks (hub rules are already live, pushed by the athlete-hub chat with a comment prefix)
stg_css = json.load(open(ROOT + 'stg-coaching/out/lib-6.json'))['meta']['_elementor_page_settings']['custom_css']
kit = json.load(open(BK + 'lib-6.json'))['meta']['_elementor_page_settings']
have = set(blocks(kit['custom_css']))
new = []
for b in blocks(stg_css):
    if b in have or b in new or '.hb' in b: continue
    new.append(b)
assert all(b.count('{') == b.count('}') for b in new)
print('kit: appending', len(new), 'rules')
for b in new: print('   ', b[:110].replace('\n', ' '))
kit['custom_css'] = kit['custom_css'].rstrip() + '\n/* 18 Nov 2026: countries flags, money-back guarantee, Basic button, talent application form */\n' + '\n'.join(new) + '\n'
r = post(f'{L}/wp/v2/elementor_library/6', {'meta': {'_elementor_page_settings': kit}}); print('kit', r.get('id'), r.get('code', ''))

# 2. pages
for pid, swap in P.items():
    live_tree = json.loads(json.load(open(BK + f'page-{pid}.json'))['meta']['_elementor_data'])
    stg_tree = json.loads(json.load(open(ROOT + f'stg-coaching/out/page-{pid}.json'))['meta']['_elementor_data'].replace(STG, 'https://coaching.cigalacycling.com'))
    lw, sw = walk(live_tree, {}), walk(stg_tree, {})
    assert list(lw) == list(sw), f'{pid}: structure differs, stop'
    for p in lw:
        assert lw[p]['widgetType'] == sw[p]['widgetType'], f'{pid} {p}: widget type differs'
        ls, ss = lw[p]['settings'], sw[p]['settings']
        keys = swap.get(p, [])
        if (pid, p) in HOLD: print('  held back', pid, p); keys = list(swap[p]); continue
        others = {k for k in set(ls) | set(ss) if k not in keys and ls.get(k) != ss.get(k)}
        assert not others, f'{pid} {p}: unexpected differences {others}, stop'
        for k in keys: ls[k] = ss[k]
    out = json.dumps(live_tree)
    assert 'staging.' not in out, f'{pid}: staging URL left'
    r = post(f'{L}/wp/v2/pages/{pid}', {'meta': {'_elementor_data': out}}); print('page', pid, r.get('id'), r.get('code', ''))
if not DRY:
    r = subprocess.run(['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'DELETE', f'{L}/elementor/v1/cache'], capture_output=True, text=True); print('elementor cache', r.stdout)
