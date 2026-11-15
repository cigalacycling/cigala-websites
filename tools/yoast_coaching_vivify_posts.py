"""Yoast title, meta description and focus keyphrase for Marine's articles (tools/coaching_vivify_posts.py), staging only.
  python3 -I tools/yoast_coaching_vivify_posts.py
"""
import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
B = 'https://staging.coaching.cigalacycling.com/wp-json/yoast/v1/bulk_editor/update_search'
P = json.load(open(ROOT + 'stg-coaching/vivify-posts.json'))['posts']
KEY = {'carbs-per-hour-endurance-fueling': 'carbs per hour', 'ironman-70-3-nutrition-plan': 'ironman 70.3 nutrition plan',
       'fatigue-after-exercise-endurance-athletes': 'fatigue after exercise', 'daily-fat-intake-guide': 'daily fat intake',
       'cycling-nutrition-what-to-eat-and-drink-on-the-bike': 'cycling nutrition', 'why-do-you-bonk-on-the-bike': 'bonking on the bike', 'top-5-foods-for-cyclists': 'foods for cyclists'}
items = []
for slug, p in P.items():
    t = p['seo_title'].replace(' | Vivify Sports', '').strip()
    if len(t) > 58: t = t[:t.rfind(' ', 0, 58)].rstrip(':,') 
    items += [{'id': p['id'], 'seo_title': t + ' | Cigala Cycling Coaching'}, {'id': p['id'], 'meta_description': p['desc']}, {'id': p['id'], 'focus_keyphrase': KEY[slug]}]
for i in range(0, len(items), 18):   # Yoast takes at most 20 items per request
    r = subprocess.run(['curl', '-sS', '-m', '60', '-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', json.dumps({'items': items[i:i + 18]}), B], capture_output=True, text=True)
    res = json.loads(r.stdout).get('results', [])
    print(len(res), 'items,', sum(not x['success'] for x in res), 'failed' if res else r.stdout[:300])
