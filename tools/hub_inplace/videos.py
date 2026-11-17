"""Add the two YouTube playlists (Matteo 17 Nov) at the end of the Training library section of each shared hub, in place.
Usage: videos.py [--live]. Re-running is safe: skips a hub that already has them."""
import sys, json, re
live = '--live' in sys.argv
sys.argv = ['x'] + (['--live'] if live else []); sys.path.insert(0, r'C:\Users\matte\vekta\athlete-hub\cigala-websites\tools')
import coaching_athlete_area as c
PL = [('PL5DQPV2sc_0WTgEJlbBZpJXFOjgDktpnz', {'en': 'Core &amp; Strength Routine', 'it': 'Routine core e forza', 'pt': 'Rotina de core e força', 'sl': 'Rutina za core in moč'}),
      ('PL5DQPV2sc_0VdvMQZYo-Qaxv6Ual0Fbm7', {'en': 'Stretch Routine', 'it': 'Routine di stretching', 'pt': 'Rotina de alongamentos', 'sl': 'Rutina raztezanja'})]
LIB = {'en': 'Training library', 'it': 'Biblioteca di allenamento', 'pt': 'Biblioteca de treino', 'sl': 'Knjižnica za trening'}
H3 = {'en': 'Video routines', 'it': 'Routine in video', 'pt': 'Rotinas em vídeo', 'sl': 'Video rutine'}
OPEN = {'en': 'Open on YouTube', 'it': 'Apri su YouTube', 'pt': 'Abrir no YouTube', 'sl': 'Odpri na YouTubu'}

def block(lang):
    out = f'<!-- wp:heading {{"level":3}} --><h3 class="wp-block-heading">{H3[lang]}</h3><!-- /wp:heading -->'
    for pid, t in PL:
        out += ('<!-- wp:html --><div class="ath-video" style="margin:0 0 22px">'
                f'<p style="margin:0 0 8px;font-weight:600">{t[lang]}</p>'
                '<div style="position:relative;width:100%;aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:#000">'
                f'<iframe src="https://www.youtube-nocookie.com/embed/videoseries?list={pid}&amp;rel=0" title="{t[lang]}" loading="lazy" '
                'style="position:absolute;inset:0;width:100%;height:100%;border:0" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div>'
                f'<p style="margin:6px 0 0;font-size:13px"><a href="https://www.youtube.com/playlist?list={pid}" target="_blank" rel="noopener">{OPEN[lang]} ↗</a></p>'
                '</div><!-- /wp:html -->')
    return out

bk = c.ROOT + ('live-coaching' if live else 'stg-coaching') + '/backup/'
for p in c.req(f'{c.B}/wp/v2/cc_athlete?status=private&per_page=100&context=edit&_fields=id,meta,content'):
    if not (p.get('meta') or {}).get('cc_shared'): continue
    lang = p['meta'].get('cc_lang') or 'en'; raw = p['content']['raw']
    if PL[0][0] in raw: print(p['id'], lang, 'already has the videos'); continue
    lib = f'<h2 class="wp-block-heading">{LIB[lang]}</h2>'
    i = raw.find(lib)
    if i < 0: print(p['id'], lang, 'no library heading: skipped'); continue
    j = raw.find('<!-- wp:heading -->', i + len(lib))   # the next h2 (Training tools)
    if j < 0: print(p['id'], lang, 'no next section: skipped'); continue
    json.dump({'id': p['id'], 'raw': raw}, open(bk + f'shared-hub-{p["id"]}-before-videos-2026-11-17.json', 'w', encoding='utf-8'), ensure_ascii=False)
    new = raw[:j] + block(lang) + raw[j:]
    r = c.req(f'{c.B}/wp/v2/cc_athlete/{p["id"]}', {'content': new}, 'POST')
    saved = (r.get('content') or {}).get('raw', '') if isinstance(r, dict) else ''
    print(p['id'], lang, 'added, iframe kept' if 'youtube-nocookie.com/embed/videoseries' in saved else 'CHECK: ' + str(r)[:200])
