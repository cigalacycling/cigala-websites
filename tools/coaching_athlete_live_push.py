# Usage: python3 -I tools/coaching_athlete_live_push.py 8   (back up live-coaching/backup/athlete-snippet-8-<date>.json first, and diff it against the repo build)
# Push the athlete-area snippet to LIVE with exactly the module list the push tool uses for staging (so no other chat's module is dropped).
import json, subprocess, re, sys
ROOT = '/home/user/cigala-websites/'
src = open(ROOT + 'tools/coaching_athlete_area.py').read()
m = re.search(r"for f in \((\'hub-i18n\.php'[^)]*)\):", src); files = [x.strip().strip("'") for x in m.group(1).split(',') if x.strip()]
code = open(ROOT + 'coaching/athlete-area/athlete-area.php').read(); assert code.startswith('<?php\n'); code = code[6:]
for f in files:
    x = open(ROOT + 'coaching/athlete-area/' + f).read(); assert x.startswith('<?php\n'), f; code += '\n' + x[6:].replace("if (!defined('ABSPATH')) return;", '', 1)
print('modules:', len(files), files[-5:])
body = {'name': 'Cigala athlete area (one login per athlete)', 'desc': 'Built by tools/coaching_athlete_area.py from coaching/athlete-area/ in the cigala-websites repo. Do not edit here.', 'code': code, 'scope': 'global', 'active': True, 'priority': 10}
r = subprocess.run(['curl', '-sS', '-m', '120', '-X', 'PUT', 'https://coaching.cigalacycling.com/wp-json/code-snippets/v1/snippets/' + sys.argv[1], '-H', 'Content-Type: application/json', '--data-binary', '@-'], input=json.dumps(body), capture_output=True, text=True)
d = json.loads(r.stdout); print('snippet', d.get('id'), 'active', d.get('active'), 'error:', d.get('code_error'), 'len', len(d.get('code', '')))
