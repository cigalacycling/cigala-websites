"""Matteo 15 Nov: the blog cards of the 7 articles from vivifysports.com didn't show "By Marine Lenehan".
The blog card reads the ACF field `author_name` (field_6a429034e5022), which the older Marine posts have and the new ones
didn't. ACF isn't in the REST API, so (staging only) a temporary Code Snippets snippet registers the two meta keys,
the value is copied from an older Marine post, then the snippet is deleted and Code Snippets switched off again.
  python3 -I tools/coaching_vivify_author_field.py
"""
import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
B = 'https://staging.coaching.cigalacycling.com/wp-json'
def req(url, body=None, method='GET'):
    a = ['curl', '-sS', '-m', '60', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    r = subprocess.run(a, capture_output=True, text=True); return json.loads(r.stdout or 'null')
CODE = ("add_action('init', function () { foreach (array('author_name', '_author_name') as $k) { register_post_meta('post', $k, array('type' => 'string', "
        "'single' => true, 'show_in_rest' => true, 'auth_callback' => function () { return current_user_can('edit_posts'); })); } });")
print(req(f'{B}/wp/v2/plugins/code-snippets/code-snippets?_fields=status', {'status': 'active'}, 'POST'))
snip = req(f'{B}/code-snippets/v1/snippets', {'name': 'TEMP: expose author_name to REST (Claude)', 'scope': 'global', 'active': True, 'code': CODE}, 'POST')
sid = snip['id']; print('snippet', sid)
try:
    ref = req(f'{B}/wp/v2/posts/4933?context=edit&_fields=id,meta')['meta']
    val, key = ref.get('author_name'), ref.get('_author_name')
    print('from older post:', repr(val), repr(key))
    assert val and key
    for slug, p in json.load(open(ROOT + 'stg-coaching/vivify-posts.json'))['posts'].items():
        r = req(f'{B}/wp/v2/posts/{p["id"]}?_fields=id,meta', {'meta': {'author_name': val, '_author_name': key}}, 'POST')
        print(slug, '->', r['meta'].get('author_name'))
finally:
    print('delete snippet', req(f'{B}/code-snippets/v1/snippets/{sid}', None, 'DELETE') is not None)
    print(req(f'{B}/wp/v2/plugins/code-snippets/code-snippets?_fields=status', {'status': 'inactive'}, 'POST'))
