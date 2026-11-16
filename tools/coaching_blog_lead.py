"""Blog post opening line (Matteo 16 Nov 2026), Coaching STAGING only.
Pushes coaching/seo/blog-lead.php as a Code Snippets snippet (ID in stg-coaching/blog-lead-snippet-id.txt).
The matching CSS (same size as the article; hidden with body.cc-no-lead) is in tools/build_coaching_wp.py.
  python3 -I tools/coaching_blog_lead.py
"""
import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.coaching.cigalacycling.com'
B = f'https://{HOST}/wp-json'
SNIP = ROOT + 'stg-coaching/blog-lead-snippet-id.txt'
def req(url, body=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '90', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    return json.loads(subprocess.run(a, capture_output=True, text=True).stdout or 'null')
code = open(ROOT + 'coaching/seo/blog-lead.php').read(); assert code.startswith('<?php\n'); code = code[6:]
body = {'name': 'Blog: hide an opening line that repeats the article', 'desc': 'Built by tools/coaching_blog_lead.py (cigala-websites repo).', 'code': code, 'scope': 'global', 'active': True}
if os.path.exists(SNIP): s = req(f'{B}/code-snippets/v1/snippets/{open(SNIP).read().strip()}', body, 'PUT')
else:
    s = req(f'{B}/code-snippets/v1/snippets', body, 'POST')
    if s.get('id'): open(SNIP, 'w').write(str(s['id']))
print('snippet', s.get('id'), s.get('active'), s.get('code_error') or '')
