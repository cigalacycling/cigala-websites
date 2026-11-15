"""Yoast focus keyphrases for the Coaching pages that had none (staging, 15 Nov 2026). Titles and metas unchanged.
  python3 -I tools/yoast_coaching_keyphrases.py
"""
import json, subprocess
B = 'https://staging.coaching.cigalacycling.com/wp-json/yoast/v1/bulk_editor/update_search'
ITEMS = [{'id': 3750, 'focus_keyphrase': 'one to one cycling coaching'},
         {'id': 564, 'focus_keyphrase': 'coaching terms and conditions'},
         {'id': 4917, 'focus_keyphrase': 'better sprinter'},
         {'id': 4894, 'focus_keyphrase': 'calibrate a power meter'}]
r = subprocess.run(['curl', '-sS', '-m', '60', '-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', json.dumps({'items': ITEMS}), B], capture_output=True, text=True)
print(r.stdout[:400])
