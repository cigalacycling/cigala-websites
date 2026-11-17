"""Matteo 17 Nov 2026 (everything in the athlete's language): the Portuguese and Slovenian hubs drop the "New on the blog"
row (newest English posts, titles can't be translated automatically); the translated reading list stays. The Italian hub
keeps its row (it lists Italian posts). In place, backup first. Usage: no_english_new_posts.py [--live]"""
import sys, json, re
live = '--live' in sys.argv
sys.argv = ['x'] + (['--live'] if live else []); sys.path.insert(0, r'C:\Users\matte\vekta\athlete-hub\cigala-websites\tools')
import coaching_athlete_area as c
bk = c.ROOT + ('live-coaching' if live else 'stg-coaching') + '/backup/'
for p in c.req(f'{c.B}/wp/v2/cc_athlete?status=private&per_page=100&context=edit&_fields=id,meta,content'):
    if not (p.get('meta') or {}).get('cc_shared') or (p['meta'].get('cc_lang') or 'en') not in ('pt', 'sl'): continue
    raw = p['content']['raw']
    new, n = re.subn(r'<!-- wp:heading \{"level":3\} --><h3 class="wp-block-heading">[^<]*</h3><!-- /wp:heading -->\s*<!-- wp:shortcode -->\[cc_latest_posts[^\]]*\]<!-- /wp:shortcode -->', '', raw)
    if not n: print(p['id'], 'row not found'); continue
    json.dump({'id': p['id'], 'raw': raw}, open(bk + f'shared-hub-{p["id"]}-before-no-new-posts-2026-11-17.json', 'w', encoding='utf-8'), ensure_ascii=False)
    r = c.req(f'{c.B}/wp/v2/cc_athlete/{p["id"]}', {'content': new}, 'POST')
    print(p['id'], p['meta'].get('cc_lang'), 'row removed' if isinstance(r, dict) and r.get('id') else 'FAILED ' + str(r)[:150])
