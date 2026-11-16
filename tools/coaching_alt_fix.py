"""Alt text for the blog images that had none (audit 16 Nov 2026), Coaching STAGING only. Matteo: "check the rest of the website".
Sets the media item's alt text and fills alt="" on that image inside each post that uses it. Existing alt text is never changed.
Posts are backed up to stg-coaching/posts-backup/<id>-before-alt.html first.
  python3 -I tools/coaching_alt_fix.py
"""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.coaching.cigalacycling.com'; B = f'https://{HOST}/wp-json'
ALT = {
    6348: 'Matteo Cigala biting his medal in the European champion jersey after winning the European Gran Fondo title',
    6285: 'Vekta x Cigala Cycling: a training session in the Vekta app on a phone and a laptop',
    6194: 'Matteo Cigala climbing a steep mountain road in the Cigala Cycling kit',
    6343: 'Matteo Cigala smiling by a lake in the white Cigala Cycling jersey',
    6192: 'Matteo Cigala esulta a braccia alzate sul traguardo con la maglia Cigala Cycling',
    6237: 'Gruppo di ciclisti in salita su un passo alpino, con le montagne sullo sfondo',
    5870: 'An exhausted cyclist lying on the ground next to his bike after a hard effort',
    5869: 'A young rider in a yellow leader’s jersey signing a jersey for a young fan',
    3582: 'A rider celebrating with his arms spread wide as he crosses a gran fondo finish line',
    3752: 'A cyclist riding a narrow mountain road between stone walls',
    4883: 'Riders in the leaders’ jerseys spraying champagne on a race podium',
    7148: 'A cyclist riding alone on a quiet country road at sunset',
    7149: 'Cycling snacks on a wooden board: banana, almonds, walnuts, oat biscuits and crystallised ginger',
    7151: 'A homemade banana cake on a plate, a simple energy snack for cyclists',
    7152: 'A cyclist riding a long straight road towards snow-capped mountains',
    7127: 'A cyclist in a helmet eating an energy bar during a ride',
}
def req(url, body=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '90', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    return json.loads(subprocess.run(a, capture_output=True, text=True).stdout or 'null')
for mid, alt in ALT.items():
    m = req(f'{B}/wp/v2/media/{mid}?context=edit&_fields=alt_text')
    if not (m.get('alt_text') or '').strip(): req(f'{B}/wp/v2/media/{mid}?_fields=id', {'alt_text': alt}, 'POST'); print('media', mid, 'alt set')
    else: print('media', mid, 'kept:', m['alt_text'][:50])
posts, p = [], 1
while True:
    r = req(f'{B}/wp/v2/posts?per_page=100&page={p}&context=edit&_fields=id,slug,content')
    if not isinstance(r, list) or not r: break
    posts += r; p += 1
for post in posts:
    c = post['content']['raw']; n = c
    for mid, alt in ALT.items():
        a = alt.replace('"', '&quot;')
        n = re.sub(r'(<img\b[^>]*\bclass="[^"]*\bwp-image-' + str(mid) + r'\b[^"]*"[^>]*>)', lambda m: re.sub(r'\salt=""', f' alt="{a}"', m.group(1)) if ' alt=""' in m.group(1) else m.group(1), n)
        n = re.sub(r'(<img\b[^>]*\balt=""[^>]*\bclass="[^"]*\bwp-image-' + str(mid) + r'\b[^"]*"[^>]*>)', lambda m: m.group(1).replace(' alt=""', f' alt="{a}"', 1), n)
    if n != c:
        open(ROOT + f'stg-coaching/posts-backup/{post["id"]}-before-alt.html', 'w').write(c)
        req(f'{B}/wp/v2/posts/{post["id"]}?_fields=id', {'content': n}, 'POST'); print('post', post['slug'], 'alt filled')
