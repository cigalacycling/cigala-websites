"""Publish the six original Italian articles (coaching/blog-it/articles.py) on Coaching STAGING, Matteo 16 Nov 2026.
- Gutenberg posts in the same style as the existing Italian posts (intro, photo, H2 sections, FAQ, Matteo's sign-off + author photo).
- Category Blog + "Italiano" (the two existing Italian posts are added to "Italiano" too; their URLs don't change: /blog/<slug>/).
- Yoast title, meta description and focus keyphrase via the Yoast bulk editor endpoint.
- A small Code Snippets snippet marks Italian content as Italian for search engines: <html lang="it-IT"> and og:locale it_IT
  on posts in "Italiano" and on the Italian landing page /preparatore-di-ciclismo-italia/.
State (post ids) in stg-coaching/italian-posts.json, so re-running updates instead of duplicating.
  python3 -I tools/coaching_italian_posts.py
"""
import json, os, re, subprocess, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
sys.path.insert(0, ROOT + 'coaching/blog-it'); import articles as A
HOST = 'staging.coaching.cigalacycling.com'   # never the live host
B = f'https://{HOST}/wp-json'
STATE = ROOT + 'stg-coaching/italian-posts.json'
SNIP = ROOT + 'stg-coaching/italian-lang-snippet-id.txt'
OLD_IT = ['preparazione-gran-fondo-strade-bianche', 'preparazione-maratona-dles-dolomites']

def req(url, body=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '120', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    r = subprocess.run(a, capture_output=True, text=True)
    return json.loads(r.stdout or 'null')

def media(mid):
    m = req(f'{B}/wp/v2/media/{mid}?_fields=id,source_url'); return m['source_url']

def blocks(a):
    out = []
    P = lambda h: f'<!-- wp:paragraph -->\n<p>{h}</p>\n<!-- /wp:paragraph -->'
    first = next(i for i, b in enumerate(a['blocks']) if b[0] == 'p')   # the opening paragraph is the excerpt: the post template shows it as the lead
    for b in a['blocks'][:first] + a['blocks'][first + 1:]:
        k = b[0]
        if k == 'p': out.append(P(b[1]))
        elif k == 'h2': out.append(f'<!-- wp:heading -->\n<h2 class="wp-block-heading">{b[1]}</h2>\n<!-- /wp:heading -->')
        elif k == 'h3': out.append(f'<!-- wp:heading {{"level":3}} -->\n<h3 class="wp-block-heading">{b[1]}</h3>\n<!-- /wp:heading -->')
        elif k == 'ul':
            li = ''.join(f'<!-- wp:list-item -->\n<li>{x}</li>\n<!-- /wp:list-item -->' for x in b[1])
            out.append(f'<!-- wp:list -->\n<ul class="wp-block-list">{li}</ul>\n<!-- /wp:list -->')
        elif k == 'img':
            u = media(a['img']); alt = html.escape(a['alt'], quote=True)
            out.append(f'<!-- wp:image {{"id":{a["img"]},"sizeSlug":"full","linkDestination":"none"}} -->\n'
                       f'<figure class="wp-block-image size-full"><img src="{u}" alt="{alt}" class="wp-image-{a["img"]}"/></figure>\n<!-- /wp:image -->')
        elif k == 'faq':
            out.append('<!-- wp:heading -->\n<h2 class="wp-block-heading">Domande frequenti</h2>\n<!-- /wp:heading -->')
            out += [P(f'<strong>{q}</strong> {ans}') for q, ans in b[1]]
    # Matteo's sign-off, exactly as on the existing posts
    out.append(P('Matteo Cigala<br>Founder &amp; Head Coach'))
    out.append('<!-- wp:spacer {"height":"10px"} -->\n<div style="height:10px" aria-hidden="true" class="wp-block-spacer"></div>\n<!-- /wp:spacer -->')
    out.append('<!-- wp:image {"id":7001,"width":"240px","sizeSlug":"full","linkDestination":"none","className":"cc-author"} -->\n'
               f'<figure class="wp-block-image size-full is-resized cc-author"><img src="{media(7001)}" alt="Matteo Cigala, Founder &amp; Head Coach of Cigala Cycling, in the white Cigala Cycling jersey, with his signature" class="wp-image-7001" style="width:240px"/></figure>\n<!-- /wp:image -->')
    return '\n\n'.join(out)

LANG_SNIPPET = r'''// Italian content is marked as Italian (Matteo 16 Nov 2026): posts in the "Italiano" category and the Italian landing page.
function cc_is_italian_view() {
    if (is_page('preparatore-di-ciclismo-italia')) return true;
    return is_singular('post') && has_category('italiano');
}
add_filter('language_attributes', function ($out) { return cc_is_italian_view() ? preg_replace('/lang="[^"]*"/', 'lang="it-IT"', $out) : $out; }, 20);
add_filter('wpseo_locale', function ($l) { return cc_is_italian_view() ? 'it_IT' : $l; });
'''

if __name__ == '__main__':
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    cat = req(f'{B}/wp/v2/categories?slug=italiano&_fields=id')
    cat = cat[0]['id'] if cat else req(f'{B}/wp/v2/categories', {'name': 'Italiano', 'slug': 'italiano', 'description': 'Articoli in italiano di Matteo Cigala.'}, 'POST')['id']
    print('category Italiano', cat)
    seo = []
    for a in A.ARTICLES:
        first = re.sub(r'<[^>]+>', '', next(b[1] for b in a['blocks'] if b[0] == 'p'))
        body = {'title': a['title'], 'slug': a['slug'], 'status': 'publish', 'content': blocks(a), 'excerpt': first,
                'categories': [1, cat], 'featured_media': a['img'], 'author': 1}
        if a['slug'] in st: r = req(f'{B}/wp/v2/posts/{st[a["slug"]]}', body, 'POST')
        else:
            r = req(f'{B}/wp/v2/posts', body, 'POST')
            if r.get('id'): st[a['slug']] = r['id']; json.dump(st, open(STATE, 'w'), indent=1)
        print(a['slug'], r.get('id'), r.get('link') or r.get('message'))
        seo += [{'id': r['id'], 'seo_title': a['seo_title']}, {'id': r['id'], 'meta_description': a['desc']}, {'id': r['id'], 'focus_keyphrase': a['key']}]
    for slug in OLD_IT:   # existing Italian posts join the category (no URL change)
        p = req(f'{B}/wp/v2/posts?slug={slug}&_fields=id,categories')[0]
        if cat not in p['categories']: req(f'{B}/wp/v2/posts/{p["id"]}', {'categories': p['categories'] + [cat]}, 'POST')
        print('category added', slug)
    r = subprocess.run(['curl', '-sS', '-m', '60', '-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', json.dumps({'items': seo}),
                        f'{B}/yoast/v1/bulk_editor/update_search'], capture_output=True, text=True)
    res = json.loads(r.stdout).get('results', [])
    print('yoast', len(res), 'items,', sum(not x['success'] for x in res), 'failed' if res else r.stdout[:300])
    # the line under the title ("Founder & Head Coach, Matteo Cigala") is the ACF field author_name; ACF isn't in REST, so a
    # temporary snippet exposes it, the value is copied from the Dolomites post, then the snippet is deleted (plugin stays on)
    tmp = req(f'{B}/code-snippets/v1/snippets', {'name': 'TEMP: expose author_name to REST (Claude)', 'scope': 'global', 'active': True,
              'code': "add_action('init', function () { foreach (array('author_name', '_author_name') as $k) { register_post_meta('post', $k, array('type' => 'string', 'single' => true, 'show_in_rest' => true, 'auth_callback' => function () { return current_user_can('edit_posts'); })); } });"}, 'POST')
    try:
        ref = req(f'{B}/wp/v2/posts/6234?context=edit&_fields=meta')['meta']
        assert ref.get('author_name') and ref.get('_author_name'), ref
        for slug, pid in st.items():
            r = req(f'{B}/wp/v2/posts/{pid}?_fields=meta', {'meta': {'author_name': ref['author_name'], '_author_name': ref['_author_name']}}, 'POST')
            print('author line', slug, r['meta'].get('author_name'))
    finally:
        print('temp snippet deleted', req(f'{B}/code-snippets/v1/snippets/{tmp["id"]}', None, 'DELETE') is not None)
    body = {'name': 'Italian content language (it-IT)', 'desc': 'Built by tools/coaching_italian_posts.py (cigala-websites repo).', 'code': LANG_SNIPPET, 'scope': 'global', 'active': True}
    if os.path.exists(SNIP): s = req(f'{B}/code-snippets/v1/snippets/{open(SNIP).read().strip()}', body, 'PUT')
    else:
        s = req(f'{B}/code-snippets/v1/snippets', body, 'POST')
        if s.get('id'): open(SNIP, 'w').write(str(s['id']))
    print('lang snippet', s.get('id'), s.get('active'), s.get('code_error') or '')
