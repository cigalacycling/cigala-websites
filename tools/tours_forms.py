"""Tours contact forms in the Coaching style (Matteo 15 Nov: all contact forms look like Coaching's).

Patches the live Elementor form widgets on Tours STAGING in place:
  Contact 461 (/contact/) and Custom tours 1576 (/trips/private-trips/).
- class "cc-form" (the CSS is in the kit, see FORM_CSS in tools/build_tours_wp.py; same rules as tools/build_coaching_wp.py)
- no visible labels, a " *" at the end of every placeholder, every field required
- Name, Email, Phone (with country code), Your Message. Phone is a text field: Elementor's number/tel fields
  reject "+353 87 ...". Custom tours keeps its phone field id, so nothing else changes.
Email settings (recipient, subject, [all-fields]) are untouched. Idempotent: safe to run again.
Backups of the pages before the first change: stg-tours/backup/page-<id>-before-form.json
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_tours_wp import req, B

PH = {'name': 'Name', 'email': 'Email', 'message': 'Your Message'}
PHONE_PH = 'Phone (with country code) *'

def fix_form(s):
    cls = (s.get('_css_classes') or '').split()
    if 'cc-form' not in cls: cls.append('cc-form')
    s['_css_classes'] = ' '.join(cls)
    s['show_labels'] = ''
    s['mark_required'] = 'yes'
    ff = s['form_fields']
    phone = [f for f in ff if f.get('field_type') in ('number', 'tel') or 'phone' in (f.get('field_label') or '').lower()]
    if phone:
        f = phone[0]; f['field_type'] = 'text'; f['field_label'] = 'Phone'; f['placeholder'] = PHONE_PH
    else:
        i = next(i for i, f in enumerate(ff) if f.get('field_type') == 'email') + 1
        ff.insert(i, {'custom_id': 'phone', 'field_type': 'text', 'required': 'true', 'field_label': 'Phone',
                      'placeholder': PHONE_PH, 'width': '100', '_id': 'cc0phon'})
    for f in ff:
        f['required'] = 'true'
        key = f.get('custom_id') or f.get('field_type')
        if key in PH and not f.get('placeholder', '').endswith('*'): f['placeholder'] = PH[key] + ' *'
        if f.get('placeholder') and not f['placeholder'].endswith('*'): f['placeholder'] += ' *'
    return [(f.get('custom_id'), f.get('field_type', 'text'), f['placeholder']) for f in ff]

for pid in (461, 1576):
    code, r = req(f'{B}/wp/v2/pages/{pid}?context=edit&_fields=meta')
    d = json.loads(json.loads(r)['meta']['_elementor_data'])
    out = []
    def walk(els):
        for e in els:
            if e.get('widgetType') == 'form': out.append(fix_form(e['settings']))
            walk(e.get('elements', []))
    walk(d)
    assert len(out) == 1, (pid, len(out))
    code, r = req(f'{B}/wp/v2/pages/{pid}', json.dumps({'meta': {'_elementor_data': json.dumps(d)}}).encode(), 'POST')
    print(pid, code, out[0])
code, r = req(f'{B}/elementor/v1/cache', method='DELETE'); print('elementor cache', code)
