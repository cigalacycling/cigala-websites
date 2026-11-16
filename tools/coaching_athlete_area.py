"""Athlete area on Coaching STAGING (Matteo, 16 Nov 2026): one login per athlete, removed when they finish.
  python3 -I tools/coaching_athlete_area.py
Switches Code Snippets on, pushes coaching/athlete-area/athlete-area.php as a snippet (ID kept in stg-coaching/athlete-snippet-id.txt),
creates the /athletes/ page and the "Shared hub (all athletes)" page once. Re-running updates the snippet only.
The proxy adds the staging application password; there are no secrets here.
"""
import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.coaching.cigalacycling.com'   # never the live host
B = f'https://{HOST}/wp-json'
SNIP = ROOT + 'stg-coaching/athlete-snippet-id.txt'

def req(url, body=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '90', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    r = subprocess.run(a, capture_output=True, text=True)
    try: return json.loads(r.stdout or 'null')
    except ValueError: raise SystemExit('bad response: ' + r.stdout[:300])

def btn(text, url, outline=False, ext=True):
    st = ' {"className":"is-style-outline"}' if outline else ''
    cls = ' is-style-outline' if outline else ''
    tgt = ' target="_blank" rel="noreferrer noopener"' if ext else ''
    return (f'<!-- wp:button{st} --><div class="wp-block-button{cls}"><a class="wp-block-button__link wp-element-button" href="{url}"{tgt}>{text}</a></div><!-- /wp:button -->')

HUB = ('<!-- wp:heading --><h2 class="wp-block-heading">Quick links</h2><!-- /wp:heading -->'
       '<!-- wp:buttons --><div class="wp-block-buttons">'
       + btn('Book a catch-up call', 'https://calendly.com/cigalacycling')
       + btn('Nutrition consult with Marine', 'https://www.vivifysports.com/nutritionalcoaching')
       + btn('WhatsApp Matteo', 'https://wa.me/message/WVBRO6XAMQMCH1', True)
       + btn('Free training tools', '/tools/', True, False)
       + '</div><!-- /wp:buttons -->'
       '<!-- wp:heading --><h2 class="wp-block-heading">Training guides</h2><!-- /wp:heading -->'
       '<!-- wp:paragraph --><p>Core routine, exercises and gym sessions: the PDFs will be here soon.</p><!-- /wp:paragraph -->')

if __name__ == '__main__':
    print('code snippets', req(f'{B}/wp/v2/plugins/code-snippets/code-snippets?_fields=plugin,status', {'status': 'active'}, 'POST'))
    code = open(ROOT + 'coaching/athlete-area/athlete-area.php').read()
    assert code.startswith('<?php\n'); code = code[len('<?php\n'):]
    body = {'name': 'Cigala athlete area (one login per athlete)', 'desc': 'Built by tools/coaching_athlete_area.py from coaching/athlete-area/athlete-area.php in the cigala-websites repo. Do not edit here.',
            'code': code, 'scope': 'global', 'active': True, 'priority': 10}
    if os.path.exists(SNIP):
        r = req(f'{B}/code-snippets/v1/snippets/{open(SNIP).read().strip()}', body, 'PUT')
    else:
        r = req(f'{B}/code-snippets/v1/snippets', body, 'POST')
        if r and r.get('id'): open(SNIP, 'w').write(str(r['id']))
    print('snippet', r.get('id'), 'active', r.get('active'), (r.get('code_error') or ''))
    # /athletes/ page: the shortcode inside the site header and footer
    pg = req(f'{B}/wp/v2/pages?slug=athletes&status=publish,draft,private&context=edit&_fields=id,link')
    if not pg:
        pg = [req(f'{B}/wp/v2/pages', {'title': 'Athlete area', 'slug': 'athletes', 'status': 'publish', 'template': 'elementor_header_footer',
                                         'content': '<!-- wp:shortcode -->[cc_athletes]<!-- /wp:shortcode -->',
                                         'meta': {}}, 'POST')]
    print('page', pg[0].get('id'), pg[0].get('link'))
    hub = [p for p in (req(f'{B}/wp/v2/cc_athlete?status=private&per_page=100&context=edit&_fields=id,title,meta') or []) if isinstance(p, dict) and (p.get('meta') or {}).get('cc_shared')]
    if not hub:
        hub = [req(f'{B}/wp/v2/cc_athlete', {'title': 'Shared hub (all athletes)', 'status': 'private', 'content': HUB, 'meta': {'cc_shared': True}}, 'POST')]
    print('hub', hub[0].get('id'), hub[0].get('message', ''))
