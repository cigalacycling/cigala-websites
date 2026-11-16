"""Share photos (og:image / twitter:image) and the last SEO text fixes, Coaching STAGING, Matteo 16 Nov 2026:
"if you find pages with no image or the wrong image or just a logo, or small or big SEO improvements, I would like that we change."
- Home, UK, USA, Canada, Italia shared the logo; tools pages and case studies all shared one photo; terms/privacy had none;
  the packages pages shared a screenshot / another post's photo. Each gets its own real photo (its hero, or a fitting photo).
- "Tips for not getting dropped" title (73 chars), the Descents description (526 chars), 1-to-1 page description (none).
- The Granfondo post's featured image was the homepage hero: now its own photo.
Old values: stg-coaching/backup/share-images-before.json. Yoast fields are exposed by a temporary snippet, then it is deleted.
  python3 -I tools/coaching_share_images.py
"""
import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.coaching.cigalacycling.com'; B = f'https://{HOST}/wp-json'
NP = json.load(open(ROOT + 'stg-coaching/new-pages.json'))
PRIV = int(open(ROOT + 'stg-coaching/page-privacy-id.txt').read().strip())
MW = json.load(open(ROOT + 'stg-coaching/media-webp.json'))
byname = lambda n: next(v['id'] for k, v in MW.items() if k.endswith('/' + n) or k == 'img/' + n)
IMG = {   # page id -> media id
    2924: byname('hero.webp'), 6098: byname('country-uk-hero-coaching.webp'), 6100: byname('country-usa-hero-matteo-sun.webp'),
    6102: byname('country-canada-hero-team.webp'), 6106: byname('italia-hero-team.webp'),
    3338: byname('packages-hero-lake.webp'), 3795: byname('triathlon-coaching.webp'), 3738: 7166,
    NP['case-studies']: 6348, NP['tools']: byname('tools-hero.webp'),
    NP['training-zones-calculator']: 7185, NP['ftp-test-calculator']: 7257, NP['carbs-per-hour-calculator']: 7127,
    NP['sweat-rate-calculator']: 7152, NP['critical-power-calculator']: 6194, NP['climb-time-calculator']: 6873,
    NP['gear-speed-calculator']: 6660, NP['swim-pace-calculator']: 7079, 564: 6450, PRIV: 6450,
}
TEXT = [   # Yoast bulk editor items
    {'id': 4927, 'seo_title': 'Tips for Not Getting Dropped | Cigala Cycling Coaching'},
    {'id': 3582, 'meta_description': 'Strong climbers can still lose time downhill. Coach Matteo Cigala explains why descending skills matter on the road and MTB, and how to improve them.'},
    {'id': 3750, 'meta_description': 'Book 1-to-1 sessions with Head Coach Matteo Cigala in Wicklow Town, Ireland. Packs of 3, 6, 10 or 20 sessions from €70 per session; pick your dates.'},
]
GRANFONDO_POST, GRANFONDO_IMG = 7403, 4883
KEYS = ['_yoast_wpseo_opengraph-image', '_yoast_wpseo_opengraph-image-id', '_yoast_wpseo_twitter-image', '_yoast_wpseo_twitter-image-id']
def req(url, body=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '90', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    return json.loads(subprocess.run(a, capture_output=True, text=True).stdout or 'null')
if __name__ == '__main__':
    # resolve the post ids of the two text fixes by slug (ids above are checked)
    for it, slug in zip(TEXT, ['tips-for-not-getting-dropped-cigala-cycling-coaching', 'how-to-improve-on-descents']):
        it['id'] = req(f'{B}/wp/v2/posts?slug={slug}&_fields=id')[0]['id']
    TEXT[2]['id'] = req(f'{B}/wp/v2/pages?slug=book-1-on-1-session&_fields=id')[0]['id']
    code = ("add_action('init', function () { foreach (array('page', 'post') as $t) foreach (" + repr(KEYS).replace('[', 'array(').replace(']', ')') +
            " as $k) register_post_meta($t, $k, array('type' => 'string', 'single' => true, 'show_in_rest' => true, 'auth_callback' => function () { return current_user_can('edit_posts'); })); });")
    tmp = req(f'{B}/code-snippets/v1/snippets', {'name': 'TEMP: Yoast share image fields in REST (Claude)', 'scope': 'global', 'active': True, 'code': code}, 'POST')
    try:
        bk = ROOT + 'stg-coaching/backup/share-images-before.json'
        before = {pid: req(f'{B}/wp/v2/pages/{pid}?context=edit&_fields=meta')['meta'] for pid in IMG}
        if not os.path.exists(bk): json.dump({k: {m: v.get(m) for m in KEYS} for k, v in before.items()}, open(bk, 'w'), indent=1)
        for pid, mid in IMG.items():
            url = req(f'{B}/wp/v2/media/{mid}?_fields=source_url')['source_url']
            r = req(f'{B}/wp/v2/pages/{pid}?_fields=id', {'meta': {'_yoast_wpseo_opengraph-image': url, '_yoast_wpseo_opengraph-image-id': str(mid),
                                                                 '_yoast_wpseo_twitter-image': url, '_yoast_wpseo_twitter-image-id': str(mid)}}, 'POST')
            print('page', pid, '->', url.split('/')[-1], r.get('id') or r)
    finally:
        print('temp snippet deleted', req(f'{B}/code-snippets/v1/snippets/{tmp["id"]}', None, 'DELETE') is not None)
    r = subprocess.run(['curl', '-sS', '-m', '60', '-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', json.dumps({'items': TEXT}),
                        f'{B}/yoast/v1/bulk_editor/update_search'], capture_output=True, text=True)
    res = json.loads(r.stdout).get('results', []); print('yoast text', len(res), 'items,', sum(not x['success'] for x in res), 'failed')
    print('granfondo featured', req(f'{B}/wp/v2/posts/{GRANFONDO_POST}?_fields=featured_media', {'featured_media': GRANFONDO_IMG}, 'POST'))
