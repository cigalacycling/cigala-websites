"""Make Marine's Blog page (/blog/) list her WordPress posts automatically, so a new post shows up when she publishes it.

  python3 tools/build_vivify.py && python3 tools/vivify_blog_wp.py

- /blog/ stops being an Elementor page with a fixed list of cards. Its content becomes blocks:
  header + hero + filter buttons (Custom HTML), a Query Loop of all published posts, newest first, then the footer (Custom HTML).
  Same look as before: cards with photo, title, short excerpt and date; same filters (by title keywords, like before).
- Each imported post gets its card excerpt (the Wix blog-list text) as its WordPress excerpt, and its card photo as
  featured image if it has none. New posts: WordPress makes the excerpt from the text; Marine can set a featured image.
"""
import os, re, json, html, subprocess, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
V = ROOT + 'vivify/'
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
B = load('b', ROOT + 'tools/build_vivify.py')
W = load('w', ROOT + 'tools/build_vivify_wp.py')
API = W.SITE + '/wp-json/wp/v2'
POSTS = json.load(open(V + 'wp-posts.json'))['posts']

def api(method, path, body=None):
    a = ['curl', '-sS', '-m', '120', '-X', method, API + path]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', '@-']
    r = subprocess.run(a, input=json.dumps(body) if body is not None else None, capture_output=True, text=True)
    return json.loads(r.stdout)

# 1. excerpts + featured images of the imported posts
cur = {p['id']: p for p in api('GET', '/posts?per_page=100&status=publish&_fields=id,featured_media,excerpt')}
for p in B.blog_posts():
    slug = p['url'].rstrip('/').split('/post/')[1]
    pid = POSTS[slug]['id']
    ex = p['ex'].strip()
    if len(ex) > 220: ex = ex[:220].rsplit(' ', 1)[0] + '…'
    body = {'excerpt': ex}
    if not cur[pid]['featured_media'] and p['img'] and (p['img'] + '.webp') in W.MEDIA:
        body['featured_media'] = W.MEDIA[p['img'] + '.webp']['id']
    j = api('POST', f'/posts/{pid}', body)
    assert 'id' in j, (slug, j)

# 2. the page
s = W.fix(open(V + 'site/blog.html').read())
header = re.search(r'<a class="skip".*?</header>', s, re.S).group(0)
footer = re.search(r'<footer class="site">.*?</footer>', s, re.S).group(0)
hero = re.search(r'<section class="page-hero".*?</section>', s, re.S).group(0)
filters = re.search(r'<div class="filters".*?</div>', s, re.S).group(0)
CSS = W.CSS + """
/* Blog page: WordPress Query Loop styled like the Vivify cards */
.vv-blog .wp-block-post-template{list-style:none;margin:0;padding:0}
.vv-blog .wp-block-post{position:relative;display:flex;flex-direction:column;overflow:hidden;margin:0;background:var(--panel);border:1px solid var(--border);border-radius:var(--r);transition:border-color .2s,transform .2s}
.vv-blog .wp-block-post:hover{border-color:var(--aqua);transform:translateY(-3px)}
.vv-blog .wp-block-post-featured-image{margin:0;aspect-ratio:16/10;overflow:hidden;background:var(--teal)}
.vv-blog .wp-block-post-featured-image img{width:100%;height:100%;object-fit:cover;transition:transform .8s cubic-bezier(.2,.7,.2,1)}
.vv-blog .wp-block-post:hover .wp-block-post-featured-image img{transform:scale(1.05)}
.vv-blog .wp-block-post:not(:has(.wp-block-post-featured-image))::before{content:"";display:block;aspect-ratio:16/10;background:var(--teal)}   /* Marine 19 Nov: no old logo as placeholder */
.vv-blog .tx{padding:20px 22px 24px;display:flex;flex-direction:column;flex:1;gap:0}
.vv-blog .wp-block-post-title{font-family:Anton,Impact,sans-serif;font-weight:400;text-transform:uppercase;font-size:21px;line-height:1.18;margin:0 0 10px;color:var(--text)}
.vv-blog .wp-block-post-title a{color:inherit;text-decoration:none}
.vv-blog .wp-block-post-title a::after{content:"";position:absolute;inset:0}
.vv-blog .wp-block-post-excerpt{margin:0 0 14px}
.vv-blog .wp-block-post-excerpt__excerpt{font-size:14px;color:var(--text-2);margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;text-align:justify;hyphens:auto}
.vv-blog .wp-block-post-excerpt__more-text{display:none}
.vv-blog .wp-block-post-date{margin-top:auto;font-size:12px;color:var(--text-3);letter-spacing:.06em;text-transform:uppercase}
"""
cats = [(n, rx) for n, rx in B.CATS]
script = ("<script>(function(){var C=" + json.dumps([rx for _, rx in cats]) + ";"
          "document.querySelectorAll('.vv-blog .wp-block-post').forEach(function(li){var t=(li.querySelector('.wp-block-post-title')||{}).textContent||'';"
          "li.dataset.t=C.map(function(r,i){return r&&new RegExp(r).test(t.toLowerCase())?i:null}).filter(function(x){return x!==null}).join(' ');});"
          "document.querySelectorAll('.filters button').forEach(function(b){b.addEventListener('click',function(){"
          "document.querySelectorAll('.filters button').forEach(function(x){x.setAttribute('aria-pressed',x===b)});var f=b.dataset.f;"
          "document.querySelectorAll('.vv-blog .wp-block-post').forEach(function(c){c.style.display=(!f||c.dataset.t.split(' ').indexOf(f)>-1)?'':'none'});});});})();</script>")

def hblock(h):
    return '<!-- wp:html -->\n' + h + '\n<!-- /wp:html -->'

top = W.FONTS + '<style>' + CSS + '</style>' + header + '<span id="main"></span>' + hero + '<section style="padding-top:0"><div class="wrap">' + filters
query = """<!-- wp:query {"queryId":7,"query":{"perPage":100,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false},"className":"vv-blog"} -->
<div class="wp-block-query vv-blog"><!-- wp:post-template {"className":"bgrid"} -->
<!-- wp:post-featured-image {"isLink":false,"aspectRatio":"16/10"} /-->
<!-- wp:group {"className":"tx","layout":{"type":"default"}} -->
<div class="wp-block-group tx"><!-- wp:post-title {"level":2,"isLink":true} /-->
<!-- wp:post-excerpt {"moreText":"","excerptLength":30} /-->
<!-- wp:post-date {"format":"j M Y"} /--></div>
<!-- /wp:group -->
<!-- /wp:post-template --></div>
<!-- /wp:query -->"""
bottom = '</div></section>' + script + footer
content = '\n\n'.join([hblock(top), query, hblock(bottom)])
pid = W.st['blog.html']
j = api('POST', f'/pages/{pid}', {'content': content, 'template': 'elementor_canvas',
                                  'meta': {'_elementor_edit_mode': '', '_elementor_data': '', '_elementor_template_type': ''}})
assert 'id' in j, j
subprocess.run(['curl', '-sS', '-m', '60', '-X', 'DELETE', W.SITE + '/wp-json/elementor/v1/cache'], capture_output=True)
print(j['id'], j['link'])
