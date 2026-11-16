"""LIVE Coaching (Matteo gave live access 16 Nov 2026 evening): push the breadcrumb snippet and the redirects + llms.txt
snippet, store coaching/llms.txt in the option cc_llms_txt, and set /dummy-page/ (6074) and /group-club-packages2/ (3845) to draft.
Backup: live-coaching/backup/before-2026-11-16-evening.json. Snippet IDs: live-coaching/snippet-ids.json. Safe to re-run.
  python3 -I tools/coaching_live_snippets.py
"""
import base64, json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'coaching.cigalacycling.com'; B = f'https://{HOST}/wp-json'
IDS = ROOT + 'live-coaching/snippet-ids.json'
def req(url, body=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '90', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    return json.loads(subprocess.run(a, capture_output=True, text=True).stdout or 'null')
ids = json.load(open(IDS)) if os.path.exists(IDS) else {}
SNIPS = {'breadcrumbs': ('Breadcrumb structured data (BreadcrumbList)', 'coaching/seo/breadcrumbs.php'),
         'redirects': ('Redirects (dummy-page, group-club-packages2) and llms.txt', 'coaching/seo/redirects-llms.php')}
for k, (name, f) in SNIPS.items():
    code = open(ROOT + f).read(); assert code.startswith('<?php\n'); code = code[6:]
    body = {'name': name, 'desc': f'Built by tools/coaching_live_snippets.py from {f} (cigala-websites repo).', 'code': code, 'scope': 'global', 'active': True}
    s = req(f'{B}/code-snippets/v1/snippets/{ids[k]}', body, 'PUT') if k in ids else req(f'{B}/code-snippets/v1/snippets', body, 'POST')
    if s.get('id'): ids[k] = s['id']; json.dump(ids, open(IDS, 'w'), indent=1)
    print(k, s.get('id'), s.get('active'), s.get('code_error') or '')
# llms.txt text in an option (a one-off temp snippet writes it, then is deleted)
txt = open(ROOT + 'coaching/llms.txt').read()
tmp = req(f'{B}/code-snippets/v1/snippets', {'name': 'TEMP: store llms.txt (Claude)', 'scope': 'global', 'active': True,
          'code': "update_option('cc_llms_txt', base64_decode('" + base64.b64encode(txt.encode()).decode() + "'), false);"}, 'POST')
print('llms temp', tmp.get('id'), tmp.get('active'), tmp.get('code_error') or '')
subprocess.run(['curl', '-sS', '-o', '/dev/null', f'https://{HOST}/?cc_llms_store=1'])
print('temp deleted', req(f'{B}/code-snippets/v1/snippets/{tmp["id"]}', None, 'DELETE') is not None)
for pid in (6074, 3845): print('draft', pid, req(f'{B}/wp/v2/pages/{pid}?_fields=id,status', {'status': 'draft'}, 'POST'))
