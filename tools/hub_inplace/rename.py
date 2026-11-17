"""Rename the guides heading in the 4 shared hub pages, in place (keeps any WordPress edits). Usage: rename.py [--live]"""
import sys, json, os
live = '--live' in sys.argv
sys.argv = ['x'] + (['--live'] if live else []); sys.path.insert(0, r'C:\Users\matte\vekta\athlete-hub\cigala-websites\tools')
import coaching_athlete_area as c
NEW = {'en': ('Training guides', 'Training library'), 'it': ('Guide di allenamento', 'Biblioteca di allenamento'),
       'pt': ('Guias de treino', 'Biblioteca de treino'), 'sl': ('Vodniki za trening', 'Knjižnica za trening')}
bk = c.ROOT + ('live-coaching' if live else 'stg-coaching') + '/backup/'
for p in c.req(f'{c.B}/wp/v2/cc_athlete?status=private&per_page=100&context=edit&_fields=id,title,meta,content'):
    if not (p.get('meta') or {}).get('cc_shared'): continue
    lang = p['meta'].get('cc_lang') or 'en'; old, new = NEW[lang]; raw = p['content']['raw']
    tag_old = f'<h2 class="wp-block-heading">{old}</h2>'
    n = raw.count(tag_old)
    if n != 1: print(p['id'], lang, 'heading found', n, 'times: skipped'); continue
    json.dump({'id': p['id'], 'raw': raw}, open(bk + f'shared-hub-{p["id"]}-before-rename-2026-11-17.json', 'w', encoding='utf-8'), ensure_ascii=False)
    r = c.req(f'{c.B}/wp/v2/cc_athlete/{p["id"]}', {'content': raw.replace(tag_old, f'<h2 class="wp-block-heading">{new}</h2>')}, 'POST')
    print(p['id'], lang, 'renamed' if new in (r.get('content') or {}).get('raw', '') or r.get('id') else 'FAILED ' + str(r)[:150])
