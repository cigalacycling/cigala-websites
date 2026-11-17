"""Set Yoast SEO title and meta description on Marine's WordPress draft pages.
Live pages: exactly the Wix title and meta (vivify/baseline-2026-11-16.json). New pages: build_vivify.NEW.
  python3 -I tools/vivify_yoast.py
"""
import os, json, subprocess, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
spec = importlib.util.spec_from_file_location('b', ROOT + 'tools/build_vivify.py'); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
B = 'https://basic-darkslategray-cod-55.hostingersite.com/wp-json/yoast/v1/bulk_editor/update_search'
pages = json.load(open(ROOT + 'vivify/wp-pages.json'))
items = []
for f, pid in pages.items():
    if f in b.NEW:
        t, d = b.NEW[f][1], b.NEW[f][2]
    else:
        r = b.BASE.get(b.LIVE + b.PAGES[f]) or b.BASE[b.LIVE]
        t, d = r['title'], (r.get('meta_description') or '')
    t, d = b.fix_typos(t), b.fix_typos(d)
    items += [{'id': pid, 'seo_title': t}, {'id': pid, 'meta_description': d}]
fails = 0
for i in range(0, len(items), 18):
    r = subprocess.run(['curl', '-sS', '-m', '60', '-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', json.dumps({'items': items[i:i + 18]}), B], capture_output=True, text=True)
    try: res = json.loads(r.stdout).get('results', [])
    except Exception: print('FAIL', r.stdout[:300]); fails += 1; continue
    if not res: print('FAIL', r.stdout[:300]); fails += 1
    fails += sum(not x['success'] for x in res)
print(len(items), 'items, failed:', fails)
