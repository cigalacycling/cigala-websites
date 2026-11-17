"""301 redirects for Wix-only addresses on Marine's WordPress site (Redirection plugin, group 1).
Every live Wix page and post keeps its own address in WordPress; these are the Wix system pages that have no
WordPress page, plus the duplicate recovery-nutrition post.   python3 -I tools/vivify_redirects.py
"""
import json, subprocess
R = 'https://basic-darkslategray-cod-55.hostingersite.com/wp-json/redirection/v1'
REDIRECTS = [
    ('/nutritionalcoaching', '/sports-nutritionist-ireland/'),                       # already a 301 on Wix
    ('/service-page/vivify-sport-s-discovery-call', '/free-sports-nutrition-consultation/'),
    ('/booking-calendar/vivify-sport-s-discovery-call', '/free-sports-nutrition-consultation/'),
    ('/pricing-plans/list', '/sports-nutritionist-ireland/'),
    ('/challenges', '/sports-nutritionist-ireland/'),
    ('/coming-soon', '/'),
    ('/subscription-successful', '/'),
    ('/paywall', '/'),
    ('/profile/marine_lenehan/profile', '/about/'),
    # two Wix posts with the same H1 ("From Curiosity to Clarity"): keep the one in the sitemap
    ('/post/from-curiosity-to-clarity-a-journey-into-recovery-nutrition', '/post/recovery-nutrition-tart-cherry-juice/'),
]
have = {r['url'] for r in json.loads(subprocess.run(['curl', '-sS', f'{R}/redirect?per_page=200'], capture_output=True, text=True).stdout).get('items', [])}
for src, dst in REDIRECTS:
    if src in have: continue
    body = {'url': src, 'action_data': {'url': dst}, 'action_type': 'url', 'action_code': 301, 'group_id': 1, 'match_type': 'url', 'regex': False,
            'match_data': {'source': {'flag_query': 'ignore', 'flag_trailing': True, 'flag_case': True, 'flag_regex': False}}}
    out = subprocess.run(['curl', '-sS', '-X', 'POST', f'{R}/redirect', '-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)], capture_output=True, text=True).stdout
    print(src, '->', dst, 'OK' if '"items"' in out else out[:200])
