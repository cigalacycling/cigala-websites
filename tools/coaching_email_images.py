"""Upload the welcome-email images (tools/coaching_email_images.js -> coaching/email/) to Coaching and store their URLs in the
options cc_mail_topo, cc_mail_header_en, cc_mail_header_it (read by cc_ath_welcome_mail in athlete-area.php).
  python3 -I tools/coaching_email_images.py [--live]
"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
LIVE = '--live' in sys.argv
HOST = 'coaching.cigalacycling.com' if LIVE else 'staging.coaching.cigalacycling.com'; B = f'https://{HOST}/wp-json'
OUT = ROOT + ('live-coaching' if LIVE else 'stg-coaching') + '/email-images.json'
def req(url, body=None, method='GET', extra=None):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '120', '-X', method, url] + (extra or [])
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    return json.loads(subprocess.run(a, capture_output=True, text=True).stdout or 'null')
done = json.load(open(OUT)) if os.path.exists(OUT) else {}
for opt, f in [('cc_mail_topo', 'cigala-email-topo-bg.jpg'), ('cc_mail_header_en', 'cigala-email-header-en.jpg'), ('cc_mail_header_it', 'cigala-email-header-it.jpg')]:
    if opt not in done:
        m = req(f'{B}/wp/v2/media', None, 'POST', ['-H', 'Content-Type: image/jpeg', '-H', f'Content-Disposition: attachment; filename={f}', '--data-binary', '@' + ROOT + 'coaching/email/' + f])
        done[opt] = m['source_url']; json.dump(done, open(OUT, 'w'), indent=1)
code = ' '.join(f"update_option('{k}', '{v}');" for k, v in done.items())
tmp = req(f'{B}/code-snippets/v1/snippets', {'name': 'TEMP: email image options (Claude)', 'scope': 'global', 'active': True, 'code': code}, 'POST')
subprocess.run(['curl', '-sS', '-o', '/dev/null', f'https://{HOST}/?x=email-opts'])
print(done, '| temp deleted', req(f'{B}/code-snippets/v1/snippets/{tmp["id"]}', None, 'DELETE') is not None)
