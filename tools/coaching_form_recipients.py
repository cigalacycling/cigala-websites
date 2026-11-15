"""Point the forms on the not-yet-rebuilt Coaching pages (staging only) to matteo@cigalacycling.com
(shared/BUSINESS.md "Form emails", Matteo 15 Nov). Changes only the email settings of each form widget.
Rebuilt pages get the same settings from tools/build_coaching_wp.py.
  python3 -I tools/coaching_form_recipients.py 4256 4395 461
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_coaching_wp import req, B

def walk(els, n=[0]):
    for e in els:
        if e.get('widgetType') == 'form':
            st = e['settings']
            for k in ('email_to', 'email_to_2'):
                if k in st: st[k] = 'matteo@cigalacycling.com'
            for k in ('email_from', 'email_from_2'):
                if k in st: st[k] = 'noreply@cigalacycling.com'
            for k in ('email_from_name', 'email_from_name_2'):
                if k in st: st[k] = 'Cigala Cycling Coaching'
            n[0] += 1
        walk(e.get('elements', []), n)
    return n[0]

for pid in sys.argv[1:]:
    code, r = req(f'{B}/wp/v2/pages/{pid}?context=edit')
    data = json.loads(json.loads(r)['meta']['_elementor_data'])
    n = walk(data, [0])
    code, r = req(f'{B}/wp/v2/pages/{pid}', json.dumps({'meta': {'_elementor_data': json.dumps(data)}}).encode(), 'POST')
    print(pid, 'forms', n, code)
code, _ = req(f'{B}/elementor/v1/cache', method='DELETE'); print('cache', code)
