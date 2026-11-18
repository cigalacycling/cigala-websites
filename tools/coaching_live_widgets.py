"""Put reviewed staging changes live on coaching.cigalacycling.com, widget by widget (never the whole page: live has
athlete-hub content and form settings staging doesn't own).
  python3 -I tools/coaching_live_widgets.py <backup dir> <page id>:<widget path>[,<widget path>...] ... [--dry]
  e.g. python3 -I tools/coaching_live_widgets.py live-coaching/backup/guarantee-intl 6098:4.0,12.0,14.6 6106:3.0,11.0,13.8
The backup dir must hold page-<id>.json taken from live just before (context=edit). For each page:
  - the widget tree must be the same shape and type as the staging build (stg-coaching/out/page-<id>.json, domain swapped);
  - every widget NOT listed must be identical to staging, otherwise it stops (something else changed: look first);
  - listed widgets get staging's html. No staging URL may be left.
Then the Elementor cache is cleared. Kit CSS is not touched (append new rules separately).
"""
import json, subprocess, sys
ROOT = '/home/user/cigala-websites/'; L = 'https://coaching.cigalacycling.com/wp-json'; STG = 'https://staging.coaching.cigalacycling.com'
DRY = '--dry' in sys.argv
args = [a for a in sys.argv[1:] if a != '--dry']
BK = ROOT + args[0].rstrip('/') + '/'
P = {int(a.split(':')[0]): {tuple(int(x) for x in w.split('.')) for w in a.split(':')[1].split(',')} for a in args[1:]}

def walk(els, out, path=()):
    for i, e in enumerate(els):
        p = path + (i,)
        if e.get('elType') == 'widget': out[p] = e
        walk(e.get('elements', []), out, p)
    return out

for pid, swap in P.items():
    live_tree = json.loads(json.load(open(BK + f'page-{pid}.json'))['meta']['_elementor_data'])
    stg_tree = json.loads(json.load(open(ROOT + f'stg-coaching/out/page-{pid}.json'))['meta']['_elementor_data'].replace(STG, 'https://coaching.cigalacycling.com'))
    lw, sw = walk(live_tree, {}), walk(stg_tree, {})
    assert list(lw) == list(sw), f'{pid}: structure differs, stop'
    for p in lw:
        assert lw[p]['widgetType'] == sw[p]['widgetType'], f'{pid} {p}: widget type differs'
        ls, ss = lw[p]['settings'], sw[p]['settings']
        diff = {k for k in set(ls) | set(ss) if ls.get(k) != ss.get(k)}
        if p in swap:
            assert diff == {'html'}, f'{pid} {p}: expected only html to differ, got {diff}'
            ls['html'] = ss['html']
        else:
            assert not diff, f'{pid} {p}: unexpected differences {diff}, stop'
    out = json.dumps(live_tree)
    assert 'staging.' not in out, f'{pid}: staging URL left'
    if DRY: print('page', pid, 'ok (dry)'); continue
    r = subprocess.run(['curl', '-sS', '-m', '180', '-X', 'POST', f'{L}/wp/v2/pages/{pid}', '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                       input=json.dumps({'meta': {'_elementor_data': out}}), capture_output=True, text=True)
    j = json.loads(r.stdout or 'null'); print('page', pid, j.get('id'), j.get('code', ''))
if not DRY:
    r = subprocess.run(['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'DELETE', f'{L}/elementor/v1/cache'], capture_output=True, text=True); print('elementor cache', r.stdout)
