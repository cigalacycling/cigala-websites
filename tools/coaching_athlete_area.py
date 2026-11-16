"""Athlete area on Coaching STAGING (Matteo, 16 Nov 2026): one login per athlete, removed when they finish.
  python3 -I tools/coaching_athlete_area.py [--hub]   (--hub rewrites the shared hub page; only before Matteo edits it himself)
Switches Code Snippets on, pushes coaching/athlete-area/athlete-area.php as a snippet (ID kept in stg-coaching/athlete-snippet-id.txt),
creates the /athletes/ page and the "Shared hub (all athletes)" page once. Re-running updates the snippet only.
The proxy adds the staging application password; there are no secrets here.
"""
import json, os, subprocess, sys
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

def h2(t): return f'<!-- wp:heading --><h2 class="wp-block-heading">{t}</h2><!-- /wp:heading -->'
def para(t): return f'<!-- wp:paragraph --><p>{t}</p><!-- /wp:paragraph -->'
def buttons(*b, cls=''):
    if cls: return f'<!-- wp:buttons {{"className":"{cls}"}} --><div class="wp-block-buttons {cls}">' + ''.join(b) + '</div><!-- /wp:buttons -->'
    return '<!-- wp:buttons --><div class="wp-block-buttons">' + ''.join(b) + '</div><!-- /wp:buttons -->'
def links(items):
    li = ''.join(f'<!-- wp:list-item --><li><a href="{u}">{t}</a></li><!-- /wp:list-item -->' for t, u in items)
    return f'<!-- wp:list --><ul class="wp-block-list">{li}</ul><!-- /wp:list -->'
TOOLS = [('Training zones', '/tools/training-zones-calculator/'), ('Carbs per hour', '/tools/carbs-per-hour-calculator/'),
         ('Critical Power', '/tools/critical-power-calculator/'), ('FTP test', '/tools/ftp-test-calculator/'),
         ('Sweat rate', '/tools/sweat-rate-calculator/'), ('Climb time', '/tools/climb-time-calculator/'),
         ('Gear &amp; speed', '/tools/gear-speed-calculator/'), ('Swim pace (CSS)', '/tools/swim-pace-calculator/')]
READ = [('Training', [('The power of Zone 2 training', '/blog/zone-2-training/'), ('Critical Power', '/blog/critical-power/'),
                      ('What is W Prime?', '/blog/w-prime/'), ('Critical Power testing: how to get reliable data', '/blog/critical-power-testing/'),
                      ('Strength training for cyclists', '/blog/strength-training-for-cyclists/'), ('How to calibrate a power meter', '/blog/calibrate-a-power-meter/')]),
        ('Fuelling', [('How many carbs per hour?', '/blog/carbs-per-hour-endurance-fueling/'), ('What to eat and drink on the bike', '/blog/cycling-nutrition-what-to-eat-and-drink-on-the-bike/'),
                      ('Hydration tips', '/blog/hydration-tips/'), ('Avoid bonking on the bike', '/blog/why-do-you-bonk-on-the-bike/')]),
        ('Recovery', [('How to maximise your recovery', '/blog/how-to-maximse-your-recovery/'), ('Why am I so tired after exercise?', '/blog/fatigue-after-exercise-endurance-athletes/'),
                      ('Heart rate variability (HRV)', '/blog/heart-rate-variability-hrv/')]),
        ('Race week', [('Tapering', '/blog/tapering/'), ('Potentiation in warm-ups', '/blog/the-importance-of-potentiation-in-warm-ups/'),
                       ('Tips for not getting dropped', '/blog/tips-for-not-getting-dropped-cigala-cycling-coaching/'), ('Tips for gravel racing', '/blog/tips-for-gravel-racing/')])]
HUB = (h2('Quick links')
       + buttons(btn('Book a catch-up call', 'https://calendly.com/cigalacycling'), btn('Nutrition consult with Marine', 'https://www.vivifysports.com/nutritionalcoaching'),
                 btn('WhatsApp Matteo', 'https://wa.me/message/WVBRO6XAMQMCH1', True), btn('Community on Skool', 'https://www.skool.com/cigala-cycling-collective-1115', True))
       + h2('Your training apps')
       + para('Your plan is in Vekta or TrainingPeaks and syncs to your Garmin, Wahoo or Zwift.')
       + buttons(btn('Open Vekta', 'https://joinvekta.com/', True), btn('Open TrainingPeaks', 'https://app.trainingpeaks.com/', True))
       + h2('Training guides')
       + para('Core routine, exercises and gym sessions: the PDFs will be here soon.')
       + h2('Training tools')
       + buttons(*[btn(t, u, True, False) for t, u in TOOLS], cls='ath-tools')
       + h2('Worth reading')
       + ''.join(f'<!-- wp:heading {{"level":3}} --><h3 class="wp-block-heading">{g}</h3><!-- /wp:heading -->' + links(items) for g, items in READ))

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
    elif '--hub' in sys.argv:   # rewrite the shared hub from HUB above (overwrites edits made in WordPress)
        req(f'{B}/wp/v2/cc_athlete/{hub[0]["id"]}', {'content': HUB}, 'POST')
    print('hub', hub[0].get('id'), hub[0].get('message', ''))
