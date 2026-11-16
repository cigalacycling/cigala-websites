"""Upload the branded share cards (tools/coaching_share_cards.js -> coaching/share/*.jpg) to Coaching STAGING and set
them as the Yoast og/twitter image of the homepage, the athlete area and the Italian page (Matteo 16 Nov 2026:
"on cigalacycling.com you made a nice image with my branding, here I don't see it"). Old values are in
stg-coaching/backup/share-images-before.json (homepage, Italia) and stg-coaching/backup/share-cards-before.json.
  python3 -I tools/coaching_share_cards.py
"""
import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.coaching.cigalacycling.com'; B = f'https://{HOST}/wp-json'
CARDS = {2924: ('cigala-coaching-share-home.jpg', 'Head Coach Matteo Cigala coaching an athlete on the bike | Cigala Cycling Coaching'),
         7364: ('cigala-coaching-share-athletes.jpg', 'Cigala Cycling Coaching Athlete Hub, training data on a laptop and phone'),
         6106: ('cigala-coaching-share-italia.jpg', 'Ciclisti Cigala Cycling in gruppo lungo un lago | Preparatore di ciclismo online')}
KEYS = ['_yoast_wpseo_opengraph-image', '_yoast_wpseo_opengraph-image-id', '_yoast_wpseo_twitter-image', '_yoast_wpseo_twitter-image-id']
MEDIA = ROOT + 'stg-coaching/share-cards-media.json'
def req(url, body=None, method='GET', extra=None):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '120', '-X', method, url] + (extra or [])
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    return json.loads(subprocess.run(a, capture_output=True, text=True).stdout or 'null')
media = json.load(open(MEDIA)) if os.path.exists(MEDIA) else {}
for pid, (f, alt) in CARDS.items():
    if f not in media:   # upload once; re-running replaces nothing
        m = req(f'{B}/wp/v2/media', None, 'POST', ['-H', 'Content-Type: image/jpeg', '-H', f'Content-Disposition: attachment; filename={f}', '--data-binary', '@' + ROOT + 'coaching/share/' + f])
        req(f'{B}/wp/v2/media/{m["id"]}?_fields=id', {'alt_text': alt}, 'POST')
        media[f] = {'id': m['id'], 'url': m['source_url']}; json.dump(media, open(MEDIA, 'w'), indent=1)
code = ("add_action('init', function () { foreach (" + repr(KEYS).replace('[', 'array(').replace(']', ')') +
        " as $k) register_post_meta('page', $k, array('type' => 'string', 'single' => true, 'show_in_rest' => true, 'auth_callback' => function () { return current_user_can('edit_posts'); })); });")
tmp = req(f'{B}/code-snippets/v1/snippets', {'name': 'TEMP: Yoast share image fields in REST (Claude, share cards)', 'scope': 'global', 'active': True, 'code': code}, 'POST')
try:
    bk = ROOT + 'stg-coaching/backup/share-cards-before.json'
    if not os.path.exists(bk):
        json.dump({pid: {k: req(f'{B}/wp/v2/pages/{pid}?context=edit&_fields=meta')['meta'].get(k) for k in KEYS} for pid in CARDS}, open(bk, 'w'), indent=1)
    for pid, (f, _) in CARDS.items():
        m = media[f]
        r = req(f'{B}/wp/v2/pages/{pid}?_fields=id', {'meta': {KEYS[0]: m['url'], KEYS[1]: str(m['id']), KEYS[2]: m['url'], KEYS[3]: str(m['id'])}}, 'POST')
        print('page', pid, '->', f, r.get('id') or r)
finally:
    print('temp snippet deleted', req(f'{B}/code-snippets/v1/snippets/{tmp["id"]}', None, 'DELETE') is not None)
