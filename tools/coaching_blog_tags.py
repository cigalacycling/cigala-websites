"""Blog types for the filter buttons on /blog/ (Matteo 16 Nov 2026: "same as the Tours guides"), Coaching STAGING only.
Tags, not categories (tags never touch URLs). A post can have more than one. Italian posts are filtered by their
"Italiano" category (the flag button), not by a tag. Tag archives are noindex and out of the sitemap (coaching/seo/blog-lead.php).
  python3 -I tools/coaching_blog_tags.py
"""
import json, os, subprocess
HOST = 'staging.coaching.cigalacycling.com'; B = f'https://{HOST}/wp-json'
TAGS = {   # tag -> post slugs
 ('Training', 'training'): '''zone-di-potenza-critical-power-ciclismo ciclismo-dopo-i-40-anni allenamento-invernale-ciclismo-rulli come-migliorare-in-salita-ciclismo
   come-scegliere-preparatore-ciclismo-online strength-training-for-cyclists slower-in-winter-is-not-your-legs critical-power-testing ai-cycling-coaching-why-great-coaching-is-more-than-a-training-plan
   what-is-ftp-cycling cycling-coach-ireland zone-2-training critical-power w-prime the-importance-of-consistency zone-2-isnt-easy training-fasted-at-high-intensity-or-low-intensity
   the-importance-of-potentiation-in-warm-ups heat-training getting-started-with-gravel how-to-train-to-become-a-better-sprinter 5-mistake-to-avoid-when-starting-a-training-program
   10-habits-to-make-you-a-better-cyclist supercompensation calibrate-a-power-meter tips-to-train-in-the-cold-cigala-cycling-coaching over-under-training-session-cigala-cycling-coaching''',
 ('Nutrition', 'nutrition'): '''granfondo-ritmo-alimentazione-giorno-gara ironman-70-3-nutrition-plan fatigue-after-exercise-endurance-athletes carbs-per-hour-endurance-fueling lactate-gels-in-cycling
   diet-of-a-cyclist is-cherry-juice-really-worth-the-hype training-fasted-at-high-intensity-or-low-intensity a-nutritionists-guide-on-surviving-christmas the-secrets-of-weight-loss
   effective-fuelling-techniques-for-winter-training homemade-sports-drinks why-is-hydration-vital-to-optimise-athletic-performance-2 hydration-tips the-benefits-of-nitrates-in-sports
   daily-fat-intake-guide why-do-you-bonk-on-the-bike top-5-foods-for-cyclists cycling-nutrition-what-to-eat-and-drink-on-the-bike''',
 ('Racing & Events', 'racing-events'): '''granfondo-ritmo-alimentazione-giorno-gara preparazione-gran-fondo-strade-bianche preparazione-maratona-dles-dolomites gran-fondo-whistler-training-guide
   belgian-waffle-ride-training-guide w200-training-guide fred-whitton-challenge-training-guide ironman-70-3-nutrition-plan tips-for-gravel-racing how-to-train-to-become-a-better-sprinter
   tips-for-not-getting-dropped-cigala-cycling-coaching how-to-improve-on-descents bike-throw how-to-make-the-breakaway general-thoughts-on-stage-races tapering racing-thoughts zwift-racing-guide''',
 ('Recovery & Health', 'recovery-health'): '''ciclismo-dopo-i-40-anni off-season-transition fatigue-after-exercise-endurance-athletes how-to-maximse-your-recovery the-importance-of-a-warm-down supercompensation
   understanding-your-body heart-rate-variability-hrv the-secrets-of-stretching-cigala-cycling-coaching tapering the-secrets-of-weight-loss heat-training''',
}
KEEP = {9}   # "By Marine Lenehan" (her name on the cards) stays
def req(url, body=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '90', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    return json.loads(subprocess.run(a, capture_output=True, text=True).stdout or 'null')
if __name__ == '__main__':
    have = {t['slug']: t['id'] for t in req(f'{B}/wp/v2/tags?per_page=100&_fields=id,slug')}
    ids = {}
    for name, slug in TAGS:
        ids[slug] = have.get(slug) or req(f'{B}/wp/v2/tags', {'name': name, 'slug': slug}, 'POST')['id']
    want = {}
    for (name, slug), posts in TAGS.items():
        for s in posts.split(): want.setdefault(s, set()).add(ids[slug])
    posts = req(f'{B}/wp/v2/posts?per_page=100&_fields=id,slug,tags')
    for p in posts:
        if p['slug'] not in want: print('NO TYPE:', p['slug']); continue
        new = sorted(want[p['slug']] | (set(p['tags']) & KEEP))
        if sorted(p['tags']) != new: req(f'{B}/wp/v2/posts/{p["id"]}?_fields=id', {'tags': new}, 'POST')
    missing = set(want) - {p['slug'] for p in posts}
    print('tags', ids, '| posts', len(posts), '| slugs not found:', missing or 'none')
