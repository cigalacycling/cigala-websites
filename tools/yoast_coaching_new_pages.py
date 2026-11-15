"""Yoast title, meta description and focus keyphrase for the new Coaching pages (staging only).
  python3 -I tools/yoast_coaching_new_pages.py
"""
import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
B = 'https://staging.coaching.cigalacycling.com/wp-json/yoast/v1/bulk_editor/update_search'
ids = json.load(open(ROOT + 'stg-coaching/new-pages.json'))
Y = {   # same as the previews (tools/build_coaching_tools.py)
    'tools': ('Free Cycling Training Tools | Cigala Cycling Coaching',
              'Free cycling calculators from Cigala Cycling Coaching: training zones from FTP and heart rate, carbs per hour for your rides, and Critical Power and W′.', 'free cycling tools'),
    'training-zones-calculator': ('Cycling Training Zones Calculator (Power & Heart Rate) | Cigala Cycling Coaching',
              'Free cycling training zones calculator: your 7 power zones from FTP or a 20-minute test, and heart-rate zones from threshold heart rate, with W/kg.', 'training zones calculator'),
    'carbs-per-hour-calculator': ('Carbs per Hour Calculator for Cycling | Cigala Cycling Coaching',
              'How many carbs per hour should you eat on the bike? Free fuelling calculator: grams per hour, gels and bottles for your ride length and intensity.', 'carbs per hour calculator'),
    'critical-power-calculator': ('Critical Power & W Prime Calculator for Cycling | Cigala Cycling Coaching',
              'Free Critical Power and W′ (W prime) calculator: enter two all-out efforts to get your CP, W′ and predicted best power from 2 to 20 minutes.', 'critical power calculator'),
    'climb-time-calculator': ('Cycling Climb Time Calculator (Stelvio, Alpe d’Huez, Ventoux) | Cigala Cycling Coaching',
              'How long will a climb take you? Free cycling climb time calculator for the Stelvio, Alpe d’Huez, Ventoux or any climb, from your power and weight.', 'climb time calculator'),
    'sweat-rate-calculator': ('Sweat Rate Calculator for Cyclists | Cigala Cycling Coaching',
              'Free sweat rate calculator: weigh yourself before and after a ride to find how much you sweat per hour and how much to drink on the bike.', 'sweat rate calculator'),
    'swim-pace-calculator': ('CSS Swim Pace Calculator for Triathletes | Cigala Cycling Coaching',
              'Free Critical Swim Speed (CSS) calculator: your CSS pace per 100 m from a 400 m and 200 m time trial, plus training paces for every swim session.', 'css swim calculator'),
}
items = []
for slug, (t, m, k) in Y.items():
    items += [{'id': ids[slug], 'seo_title': t}, {'id': ids[slug], 'meta_description': m}, {'id': ids[slug], 'focus_keyphrase': k}]
for i in range(0, len(items), 18):   # Yoast takes at most 20 items per request
    r = subprocess.run(['curl', '-sS', '-m', '60', '-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', json.dumps({'items': items[i:i + 18]}), B], capture_output=True, text=True)
    res = json.loads(r.stdout).get('results', [])
    print(f'batch {i // 18 + 1}:', len(res), 'items,', sum(not x['success'] for x in res), 'failed' if res else r.stdout[:300])
