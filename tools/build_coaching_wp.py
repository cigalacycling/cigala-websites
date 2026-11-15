"""Build the Elementor payloads for Coaching STAGING from the approved preview pages (coachingpages/*.html).

Writes stg-coaching/out/:
  lib-6.json      kit: the brand CSS, scoped to .cc, so pages not rebuilt yet keep their old look
  lib-170.json    header: new nav (Cycling / Triathlon / Services dropdowns)
  lib-228.json    footer: new footer + the shared cookie banner (shared/consent/), which also loads the OpenWidget chat.
                  Replaces the old "Got it!" cookie bar and the old chat widget.
  page-2924.json  homepage
  page-3338.json  Individual Packages (keeps the live Elementor contact form and the Shapo testimonials widget)
  snippet-head.json  the shared consent head snippet (Elementor custom code)

Run the preview builders and tools/coaching_media.py first. Push with tools/push_coaching_wp.py.
"""
import html, os, re, sys, json, copy, random, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
OUT = ROOT + 'stg-coaching/out/'
os.makedirs(OUT, exist_ok=True)
C = 'https://coaching.cigalacycling.com'
M = json.load(open(ROOT + 'stg-coaching/media-webp.json'))
PAGES = {'home': 2924, 'individual-packages': 3338, 'tri-individual-packages': 3795, 'group-club-packages': 3738, 'terms-conditions': 564, 'privacy-policy': 'privacy',
         # new pages (Free Tools, Matteo 15 Nov): created by the push, IDs kept in stg-coaching/new-pages.json
         'tools': 'new-tools', 'tools-training-zones': 'new-training-zones-calculator', 'tools-carbs-per-hour': 'new-carbs-per-hour-calculator',
         'tools-critical-power': 'new-critical-power-calculator', 'tools-climb-time': 'new-climb-time-calculator',
         'tools-sweat-rate': 'new-sweat-rate-calculator', 'tools-swim-pace': 'new-swim-pace-calculator',
         'tools-ftp-test': 'new-ftp-test-calculator', 'tools-gear-speed': 'new-gear-speed-calculator',
         'case-studies': 'new-case-studies',
         # the remaining live pages, rebuilt by tools/build_coaching_generic.py (Matteo 15 Nov: finish every page)
         'about': 2109, 'about2': 3770, 'coaching-vision': 3272, 'testing': 3865, 'nutrition': 3995, 'bike-fitting': 4256,
         'book-1-on-1-session': 3750, 'talent-scout': 896, 'club-talk': 4395, 'contact': 461,
         'testimonials': 2844, 'blog': 4354,
         'cycling-coach-uk': 6098, 'cycling-coach-usa': 6100, 'cycling-coach-canada': 6102, 'preparatore-di-ciclismo-italia': 6106}
NEW = {'new-tools': ('Free Cycling Training Tools', 'tools', None),
       'new-training-zones-calculator': ('Training Zones Calculator', 'training-zones-calculator', 'tools'),
       'new-carbs-per-hour-calculator': ('Carbs per Hour Calculator', 'carbs-per-hour-calculator', 'tools'),
       'new-critical-power-calculator': ('Critical Power & W′ Calculator', 'critical-power-calculator', 'tools'),
       'new-climb-time-calculator': ('Climb Time Calculator', 'climb-time-calculator', 'tools'),
       'new-sweat-rate-calculator': ('Sweat Rate Calculator', 'sweat-rate-calculator', 'tools'),
       'new-swim-pace-calculator': ('Swim Pace (CSS) Calculator', 'swim-pace-calculator', 'tools'),
       'new-ftp-test-calculator': ('FTP Test Calculator', 'ftp-test-calculator', 'tools'),
       'new-gear-speed-calculator': ('Gear & Speed Calculator', 'gear-speed-calculator', 'tools'),
       'new-case-studies': ('Case Studies', 'case-studies', None)}   # 'privacy' = new page, created by the push
SRC = {k: open(ROOT + f'coachingpages/{k}.html').read() for k in PAGES}

rid = lambda: ''.join(random.choice('0123456789abcdef') for _ in range(7))
def between(s, a, b):
    i = s.index(a); j = s.index(b, i + len(a)); return s[i:j + len(b)]

# ---------- images and links ----------
def fix_img(m):
    tag = m.group(0); src = re.search(r'src="([^"]+)"', tag).group(1)
    if src.startswith('https://staging.coaching.cigalacycling.com/wp-content/uploads/'): return tag   # already in the staging media library (e.g. post images)
    if src not in M: raise SystemExit('not uploaded: ' + src + ' (run tools/coaching_media.py)')
    return tag.replace(f'src="{src}"', f'src="{M[src]["url"]}"')   # alt stays as in the preview (live alt or approved)

def fix(s):
    s = re.sub(r'<img [^>]*>', fix_img, s)
    s = re.sub(r'href="(\.\./coaching/webp/[^"]+)"', lambda m: f'href="{M[m.group(1)]["url"]}"', s)   # gallery full-size links
    s = re.sub(r'href="' + re.escape(C) + r'(/[^"]*)" target="_blank" rel="noopener"', r'href="\1"', s)   # internal links stay on this site
    return re.sub(r'href="' + re.escape(C) + r'(/[^"]*)"', r'href="\1"', s)

# ---------- CSS: every <style> block of the previews, scoped to .cc ----------
css_blocks = []
for k, s in SRC.items():
    for b in re.findall(r'<style>(.*?)</style>', s, re.S):
        if 'color-scheme:light' in b: continue     # artifact skeleton, not ours
        if b not in css_blocks: css_blocks.append(b)
P = 'html .cc'
def scope_sel(sel):
    sel = sel.strip()
    if sel in (':root', 'html', 'body', 'html, body'): return P
    if sel == '*': return P + ' *'
    return P + ' ' + sel
def scope(block):
    out, i = [], 0
    while i < len(block):
        j = block.find('{', i)
        if j < 0: out.append(block[i:]); break
        head = re.sub(r'/\*.*?\*/', '', block[i:j], flags=re.S).strip()
        if head.startswith(('@media', '@supports')):
            depth, k = 1, j + 1
            while depth:
                depth += {'{': 1, '}': -1}.get(block[k], 0); k += 1
            out.append(head + ' {' + scope(block[j + 1:k - 1]) + '}\n'); i = k; continue
        k = block.index('}', j); body = block[j + 1:k]
        if head.startswith('@'): out.append(head + ' {' + body + '}\n')
        elif head in ('body::before', '.topo', '.page') or head.startswith('.ribbon'): pass   # preview-only
        else: out.append(', '.join(scope_sel(x) for x in head.split(',')) + ' {' + body + '}\n')
        i = k + 1
    return ''.join(out)
css = ''.join(scope(re.sub(r'/\*.*?\*/', '', b, flags=re.S)) for b in css_blocks)
tile_uri = 'data:image/svg+xml,' + urllib.parse.quote(open(ROOT + 'wp/topo-tile-min.svg').read(), safe=' =:/(),.-')
css += '''
/* ---- WordPress / Elementor integration (Coaching) ---- */
body:has(.cc-page), body.single-post { background: linear-gradient(rgba(8,9,10,.6),rgba(8,9,10,.6)), #08090a url("''' + tile_uri + '''") top center / auto 3000px repeat-y !important; overflow-x: hidden; }
html .cc { background: transparent; color: var(--text-2); font-family: var(--body); font-size: 15px; line-height: 1.6; }
[data-elementor-type="header"]:has(.cc) { position: sticky; top: 0; z-index: 50; }
html .cc .nav { position: relative; top: 0; }
.e-con.cc-wrap, .cc-wrap > .e-con-inner { padding: 0 !important; gap: 0 !important; max-width: none !important; }
.cc-wrap .elementor-widget-html, .cc-wrap .elementor-widget-html .elementor-widget-container, .cc-wrap .elementor-widget-shortcode { width: 100%; }
body:has(.cc-page) .site-header, body:has(.cc-page) .site-footer { display: none; }
html .cc h1, html .cc h2, html .cc h3, html .cc h4 { font-family: var(--head); font-weight: 400; text-transform: uppercase; color: var(--text); letter-spacing: .01em; line-height: 1.14; }
html .cc h1 { line-height: 1.08; }
html .cc p, html .cc li, html .cc a, html .cc span, html .cc div, html .cc button, html .cc label, html .cc td, html .cc th, html .cc blockquote { font-family: var(--body); }
html .cc .tag-line, html .cc .stat .n, html .cc .pkg-price b, html .cc .cmp thead th, html .cc .dest-h { font-family: var(--head); }
html .cc .faq h3, html .cc footer .intl h2, html .cc footer .tag-sub, html .cc .btn-h { font-family: var(--body); text-transform: none; }
html .cc footer h4 { font: 600 11px/1.4 var(--body); letter-spacing: .1em; text-transform: uppercase; color: var(--text-3); }
html .cc .nums .l { font: 600 12px/1.4 var(--body); letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); }
.cc-contact > .e-con-inner { gap: 48px !important; align-items: center; }
.cc-contact > .e-con-inner > .e-con:first-child { flex: 0 0 40% !important; width: auto !important; }
.cc-contact > .e-con-inner > .e-con:last-child { flex: 1 1 0 !important; width: auto !important; min-width: 0; }
html .cc footer .in > div { min-width: 0; }
html .cc footer li { overflow-wrap: anywhere; }
html .cc button, html .cc .btn { text-transform: none; letter-spacing: .02em; }
html .cc .dd-btn { text-transform: uppercase; letter-spacing: .04em; }
html body #cc-consent button, html body #cc-chat { text-transform: none; letter-spacing: normal; font-family: Montserrat, system-ui, sans-serif; }
html .cc .menu a[aria-current="page"], html .cc .dd-btn.is-current { color: var(--text); box-shadow: inset 0 -2px 0 var(--red); }
html .cc .dd-menu a[aria-current="page"] { color: var(--text); box-shadow: inset 3px 0 0 var(--red); }
html .cc .burger nav a[aria-current="page"] { color: var(--text); box-shadow: inset 3px 0 0 var(--red); padding-left: 12px; }
html .cc .burger nav a, html .cc .burger details.sub > summary { transition: color .15s; }
html .cc .burger nav a:hover, html .cc .burger nav a:active, html .cc .burger details.sub > summary:hover { color: var(--green-text); }
html .cc .burger details.sub > summary.is-current { box-shadow: inset 3px 0 0 var(--red); padding-left: 12px; }
/* footer links: Elementor's kit link colour (.elementor-kit-6 a) must not win over the green hover */
.elementor-kit-6 .cc footer a:hover, .elementor-kit-6 .cc .legal a:hover { color: var(--green-text) !important; text-decoration: none !important; }
.elementor-kit-6 .cc footer a, .elementor-kit-6 .cc .legal a { text-decoration: none; }
.elementor-kit-6 .cc-social a { color: var(--text-2) !important; }
.elementor-kit-6 .cc-social a:hover { color: var(--green-text) !important; }
/* Shapo testimonials widget and the live Elementor contact form, in the brand */
.cc-shapo { margin-top: 18px; }
.cc-contact.e-con { --gap: 0px; }
.cc-contact .cc-form { width: 100% !important; max-width: 100% !important; --container-widget-width: 100% !important; margin: 22px 0 0 !important; box-sizing: border-box; }
.e-con.cc-wrap.cc-contact { padding: 96px 16px 0 !important; max-width: 1232px !important; margin: 0 auto !important; gap: 48px !important; }
.cc-contact .cc-page > div > .eyebrow { margin-top: 0; }
/* Matteo 15 Nov: the contact headings were too big; side panels start at the top, level with the heading */
.cc-contact .cc .h-sec { font-size: clamp(28px, 3.2vw, 42px); }
/* Matteo 15 Nov: the photo next to the form was much smaller than the form: as tall as the form now */
.cc-contact-ph .photo.rider { aspect-ratio: 4 / 5; }
.cc-contact-ph .photo.rider img { width: 100%; height: 100%; object-fit: cover; }
.cc-contact .cc-form .elementor-form, .cc-contact .cc-form .elementor-field-group { max-width: 100%; }
@media (max-width: 900px) {
  .cc-contact.e-con, .cc-contact > .e-con-inner { flex-direction: column !important; gap: 24px !important; }
  .cc-contact > .e-con-inner > .e-con:first-child, .cc-contact > .e-con-inner > .e-con:last-child { flex: 0 0 auto !important; width: 100% !important; }
  .cc-contact > .e-con, .cc-contact > .e-con-inner > .e-con { width: 100% !important; --width: 100% !important; }
  .cc-contact .photo.rider { aspect-ratio: 16 / 10; }
}
.cc-form .elementor-field-group { padding: 0 0 14px !important; width: 100% !important; max-width: 100% !important; flex: 0 0 100% !important; }
.cc-form .elementor-field-label { font: 600 12px Montserrat, system-ui, sans-serif !important; letter-spacing: .08em; text-transform: uppercase; color: #8a8f98 !important; padding-bottom: 6px; }
.cc-form .elementor-field-textual { font: 400 16px/1.4 Montserrat, system-ui, sans-serif !important; color: #f7f8f8 !important; background: rgba(255,255,255,.04) !important; border: 1px solid rgba(255,255,255,.14) !important; border-radius: 8px !important; padding: 12px 14px !important; }
.cc-form .elementor-field-textual:focus { outline: 2px solid #009a44 !important; outline-offset: 1px; }
.cc-form .elementor-button { font: 600 14px Montserrat, system-ui, sans-serif !important; letter-spacing: .02em; text-transform: none !important; border: 0 !important; box-shadow: none !important; background: #009a44 !important; color: #fff !important; border-radius: 8px !important; padding: 12px 22px !important; }
.cc-form .elementor-button:hover { background: #00b350 !important; }
.cc-form .elementor-field-type-submit { width: auto !important; flex: 0 0 auto !important; }
.cc-form .elementor-message { color: #d0d6e0; font-family: Montserrat, system-ui, sans-serif; }
.cc-form { background: linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.012)), rgba(15,16,17,.92); border: 1px solid rgba(255,255,255,.08); border-radius: 12px; padding: 22px !important; margin-top: 22px; }
/* blog: the live loop grid (posts appear automatically) as cards, and the single post template 4028 in the brand */
.cc-blog-wrap { padding: 8px 16px 0 !important; max-width: 1232px !important; margin: 0 auto !important; }
.cc-blog .elementor-loop-container { display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr)) !important; }
@media (max-width: 1024px) { .cc-blog .elementor-loop-container { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; } }
@media (max-width: 640px) { .cc-blog .elementor-loop-container { grid-template-columns: minmax(0, 1fr) !important; } }
.cc-blog .e-loop-item .e-con, .cc-blog .e-loop-item .e-con-inner { background: transparent !important; background-image: none !important; flex-direction: column !important; width: 100% !important; max-width: 100% !important; --width: 100% !important; border: 0 !important; }
.cc-blog .e-loop-item > .e-con > .e-con:last-child, .cc-blog .e-loop-item .e-con + .e-con { padding: 18px 20px 22px !important; gap: 10px !important; }
.cc-blog .elementor-loop-container { gap: 16px !important; }
.cc-blog .e-loop-item, .cc-blog .elementor-4718 { background: linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.012)), rgba(15,16,17,.92) !important; border: 1px solid rgba(255,255,255,.08) !important; border-radius: 14px !important; overflow: hidden; }
.cc-blog .e-loop-item img { border-radius: 0 !important; aspect-ratio: 16 / 10; object-fit: cover; width: 100% !important; }
.cc-blog .elementor-widget-theme-post-title .elementor-heading-title, .cc-blog .elementor-widget-theme-post-title a { font: 400 24px/1.14 Anton, Impact, sans-serif !important; text-transform: uppercase !important; color: #f7f8f8 !important; letter-spacing: .01em; }
.cc-blog .elementor-widget-theme-post-title a:hover { color: #34c46a !important; }
.cc-blog .elementor-widget-heading:not(.elementor-widget-theme-post-title) .elementor-heading-title { font: 600 12px/1.4 Montserrat, system-ui, sans-serif !important; letter-spacing: .08em; text-transform: uppercase !important; color: #ff3d33 !important; }
.cc-blog .elementor-widget-theme-post-excerpt, .cc-blog .elementor-widget-theme-post-excerpt p { font: 400 15px/1.6 Montserrat, system-ui, sans-serif !important; color: #d0d6e0 !important; }
.cc-blog .elementor-divider-separator { border-color: #009a44 !important; width: 40px !important; border-top-width: 3px !important; }
.cc-blog .elementor-button { background: none !important; color: #34c46a !important; padding: 0 !important; font: 600 14px Montserrat, system-ui, sans-serif !important; text-transform: none !important; border: 0 !important; box-shadow: none !important; }
.cc-blog .elementor-button:hover { color: #fff !important; }
.cc-blog .e-load-more-anchor + div .elementor-button, .cc-blog .elementor-button-wrapper .e-load-more-spinner + .elementor-button-text { color: #fff !important; }
/* Matteo 15 Nov (2nd): the hero shows the autograph; cards end at the image (title and button over the photo);
   Read more and Continue reading solid green */
html .cc .blog-hero { min-height: min(680px, 82svh); }
html .cc .blog-hero > img { object-position: 50% 58%; }
.cc-blog .e-loop-item { position: relative; }
.cc-blog .e-loop-item > .e-con { position: relative; display: block !important; }
.cc-blog .e-loop-item img { aspect-ratio: 4 / 3 !important; display: block; }
.cc-blog .e-loop-item > .e-con > .e-con:last-child { position: absolute !important; left: 0; right: 0; bottom: 0; padding: 60px 18px 18px !important;
  background: linear-gradient(180deg, rgba(8,9,10,0), rgba(8,9,10,.82) 45%, rgba(8,9,10,.95)) !important; }
.cc-blog .e-loop-item .elementor-widget-theme-post-excerpt { display: none !important; }
/* Matteo 15 Nov: "Read More" in the brand's button style (Montserrat 600, no letter spacing, sentence case) */
.cc-blog .e-loop-item .elementor-button .elementor-button-text { font-size: 0 !important; letter-spacing: 0 !important; }
.cc-blog .e-loop-item .elementor-button .elementor-button-text::before { content: "Read more →"; font: 600 14px/1.2 Montserrat, system-ui, sans-serif; letter-spacing: 0; text-transform: none; }
/* Marine Lenehan's articles (tag "By Marine Lenehan", tools/coaching_vivify_posts.py): her name on the card instead of Matteo's */
.cc-blog .e-loop-item.tag-by-marine-lenehan .elementor-element-f9f544d .elementor-heading-title { font-size: 0 !important; }
.cc-blog .e-loop-item.tag-by-marine-lenehan .elementor-element-f9f544d .elementor-heading-title::after { content: "By Sports Nutritionist, Marine Lenehan"; display: block; font: 600 11px/1.4 Montserrat, system-ui, sans-serif !important; letter-spacing: .08em !important; text-transform: uppercase; color: #d0d6e0; }
.single-post .elementor-4028 .cc-marine-sig { margin-top: 32px !important; padding-top: 18px; border-top: 1px solid rgba(255,255,255,.12); color: #d0d6e0 !important; }
.single-post .elementor-4028 .cc-marine-src { font-size: 14px !important; color: #8a8f98 !important; }
.single-post .elementor-4028 .wp-block-table table { width: 100%; border-collapse: collapse; font: 400 15px/1.5 Montserrat, system-ui, sans-serif; color: #d0d6e0; }
.single-post .elementor-4028 .wp-block-table th, .single-post .elementor-4028 .wp-block-table td { border: 1px solid rgba(255,255,255,.14); padding: 8px 10px; text-align: left; vertical-align: top; }
.single-post .elementor-4028 .wp-block-table th { color: #f7f8f8; background: rgba(255,255,255,.05); }
.single-post .elementor-4028 .wp-block-table { overflow-x: auto; }
.cc-blog .e-loop-item > .e-con > .e-con:last-child { top: auto !important; height: auto !important; min-height: 0 !important; flex-grow: 0 !important; justify-content: flex-end !important; gap: 6px !important; }
.cc-blog .e-loop-item > .e-con > .e-con:first-child { height: auto !important; min-height: 0 !important; }
.cc-blog .e-loop-item > .e-con, .cc-blog .e-loop-item > .e-con > .e-con:first-child .elementor-widget, .cc-blog .e-loop-item .elementor-widget-theme-post-featured-image a { min-height: 0 !important; height: auto !important; display: block; }
.cc-blog .e-loop-item .elementor-widget-theme-post-featured-image img { height: auto !important; max-height: none !important; }
.cc-blog .e-loop-item .elementor-widget-heading:not(.elementor-widget-theme-post-title) .elementor-heading-title { color: #d0d6e0 !important; }
.cc-blog .e-loop-item .elementor-widget-button { margin-top: 6px !important; padding-top: 0 !important; }
.cc-blog .elementor-widget-theme-post-title .elementor-heading-title, .cc-blog .elementor-widget-theme-post-title a { font-size: 22px !important; text-shadow: 0 1px 8px rgba(0,0,0,.5); }
.cc-blog .e-loop-item .elementor-button, .cc-blog .e-loop__load-more .elementor-button, .cc-blog .e-load-more-anchor ~ * .elementor-button { background: #009a44 !important; color: #fff !important; border: 0 !important; border-radius: 8px !important; padding: 9px 16px !important; }
.cc-blog .e-loop-item .elementor-button:hover, .cc-blog .e-loop__load-more .elementor-button:hover { background: #00b350 !important; color: #fff !important; }
.cc-blog .e-loop__load-more .elementor-button { padding: 13px 26px !important; font: 600 15px Montserrat, system-ui, sans-serif !important; }
/* Matteo 15 Nov: cards were too big with a lot of empty space; "Read more" as a button with an arrow */
.cc-blog .elementor-loop-container { max-width: 1200px; margin: 0 auto !important; gap: 18px !important; }
.cc-blog .e-loop-item .elementor-widget { margin: 0 !important; width: 100% !important; max-width: 100% !important; --container-widget-width: 100% !important; }
.cc-blog .e-loop-item, .cc-blog .e-loop-item > .e-con { height: 100%; }
.cc-blog .elementor-widget-heading:not(.elementor-widget-theme-post-title) .elementor-heading-title { font-size: 11px !important; }
.cc-blog .e-loop-item .elementor-widget-divider { display: none !important; }
.cc-blog .elementor-widget-theme-post-excerpt, .cc-blog .elementor-widget-theme-post-excerpt p { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin: 0 !important; font-size: 14px !important; }
.cc-blog .e-loop-item .elementor-widget-button { margin-top: auto !important; padding-top: 6px; }

.single-post .elementor-4028, .single-post .elementor-4028 .e-con:not(a) { background: transparent !important; background-image: none !important; }
.single-post .elementor-4028 { max-width: 860px; margin: 0 auto; padding: 40px 16px 0; }
.single-post .elementor-4028 .elementor-widget-theme-post-excerpt, .single-post .elementor-4028 .elementor-widget-theme-post-excerpt p { font: 500 19px/1.6 Montserrat, system-ui, sans-serif !important; color: #f7f8f8 !important; }
.single-post .elementor-4028 .elementor-widget-theme-post-content strong, .single-post .elementor-4028 .elementor-widget-theme-post-content b, .single-post .elementor-4028 .elementor-widget-theme-post-content h4 { color: #f7f8f8 !important; }
.single-post .elementor-4028 .elementor-widget-heading:not(:first-child):not(.elementor-widget-theme-post-title) .elementor-heading-title { color: #f7f8f8 !important; }
.single-post .elementor-4028 .elementor-widget-theme-post-title .elementor-heading-title { font: 400 clamp(34px, 5vw, 56px)/1.08 Anton, Impact, sans-serif !important; text-transform: uppercase !important; color: #f7f8f8 !important; }
.single-post .elementor-4028 .elementor-widget-heading:not(.elementor-widget-theme-post-title) .elementor-heading-title { font-family: Montserrat, system-ui, sans-serif !important; color: #ff3d33 !important; }
.single-post .elementor-4028 .elementor-widget-theme-post-content, .single-post .elementor-4028 .elementor-widget-theme-post-content p, .single-post .elementor-4028 .elementor-widget-theme-post-content li { font: 400 17px/1.75 Montserrat, system-ui, sans-serif !important; color: #d0d6e0 !important; }
.single-post .elementor-4028 .elementor-widget-theme-post-content h2, .single-post .elementor-4028 .elementor-widget-theme-post-content h3 { font-family: Anton, Impact, sans-serif !important; font-weight: 400 !important; text-transform: uppercase; color: #f7f8f8 !important; line-height: 1.14 !important; margin: 32px 0 10px; }
.single-post .elementor-4028 .elementor-widget-theme-post-content a { color: #34c46a !important; }
.single-post .elementor-4028 img { border-radius: 12px; }
.single-post .elementor-4028 .elementor-divider-separator { border-color: #009a44 !important; }
/* Matteo 15 Nov: the author image (white jersey + white signature, no box) and the "CIGALA CYCLING #TrainSmarterRideFaster" block
   under every post: the hashtag was dark grey on the dark page and the four tiles had lost their photos */
.single-post .elementor-4028 figure.cc-author img, .single-post .elementor-4028 img[src*="matteo-cigala-author-signature"] { border-radius: 0 !important; background: none !important; width: 240px !important; height: auto !important; }
.single-post .elementor-element-4493ab3 { text-align: center; padding: 56px 0 40px !important; gap: 10px !important; align-items: center !important; }
.single-post .elementor-element-4493ab3 .elementor-divider-separator { width: 56px !important; margin: 0 auto !important; border-top-width: 3px !important; }
.single-post .elementor-4028 .elementor-widget-heading.elementor-element-57713bd:not(.elementor-widget-theme-post-title) .elementor-heading-title { font: 400 clamp(30px, 4vw, 42px)/1.1 Anton, Impact, sans-serif !important; color: #f7f8f8 !important; letter-spacing: .01em; }
.single-post .elementor-element-2bc2c98, .single-post .elementor-element-2bc2c98 p { width: 100% !important; max-width: none !important; margin: 0 !important; font: 600 16px/1.4 Montserrat, system-ui, sans-serif !important; color: #34c46a !important; text-align: center; }
.single-post .elementor-element-e5504e1, .single-post .elementor-element-29c6d12 { width: 100% !important; --width: 100% !important; }
.single-post .elementor-element-29c6d12 { display: grid !important; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px !important; margin-top: 18px; }
@media (max-width: 760px) { .single-post .elementor-element-29c6d12 { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.single-post .elementor-element-29c6d12 > a.e-con { position: relative; min-height: 130px !important; width: auto !important; --width: auto !important; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,.1);
  background-size: cover !important; background-position: center !important; justify-content: flex-end !important; align-items: flex-start !important; padding: 14px !important; transition: border-color .2s, transform .2s; }
.single-post .elementor-element-29c6d12 > a.e-con::before { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(8,9,10,.15), rgba(8,9,10,.85)); z-index: 0; }
.single-post .elementor-element-29c6d12 > a.e-con:hover { border-color: rgba(0,154,68,.7); transform: translateY(-2px); }
.single-post .elementor-element-29c6d12 > a.e-con .elementor-widget { position: relative; z-index: 1; }
.single-post .elementor-4028 .elementor-element-29c6d12 .elementor-widget-heading:not(.elementor-widget-theme-post-title) .elementor-heading-title { font: 400 20px/1.1 Anton, Impact, sans-serif !important; color: #f7f8f8 !important; text-align: left; letter-spacing: .01em !important; text-transform: uppercase; }
'''
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700&display=swap">'

# ---------- elementor helpers ----------
def html_widget(h, **st):
    return {"id": rid(), "elType": "widget", "widgetType": "html", "settings": {"html": h, **st}, "elements": [], "isInner": False}
def wrap(elements, cls='cc-wrap', inner=False, **st):
    s = {"content_width": "full", "css_classes": cls, "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True},
         "flex_gap": {"unit": "px", "size": 0, "column": "0", "row": "0"}, **st}
    return {"id": rid(), "elType": "container", "settings": s, "elements": elements, "isInner": inner}
def blocks_of(page_html):
    """top-level sections between the header and the footer, one Elementor container each"""
    main = page_html[page_html.index('</header>') + len('</header>'):page_html.index('<footer>')].strip()
    parts = re.split(r'\n\n(?=<(?:div|section)[ >])', main)
    return [p.strip() for p in parts if p.strip()]
def page_js(page_html):
    """the page's own script (after the shared menu script)"""
    scripts = re.findall(r'<script>.*?</script>', page_html, re.S)
    return [s for s in scripts if '.dd' not in s or 'pkg-all' in s or 'g-more' in s or 'rv-row' in s]

CURJS = "<script>(function(){var p=location.pathname;document.querySelectorAll('.cc .nav a[href]').forEach(function(a){var h=a.getAttribute('href');if(h&&h.charAt(0)==='/'&&!a.classList.contains('btn')&&!a.classList.contains('brand')&&h===p){a.setAttribute('aria-current','page');var d=a.closest('.dd');if(d){d.querySelector('.dd-btn').classList.add('is-current');}var sb=a.closest('details.sub');if(sb){sb.querySelector('summary').classList.add('is-current');}}});})();</script>"
DDJS = "<script>(function(){document.querySelectorAll('.cc .dd').forEach(function(d){var b=d.querySelector('.dd-btn');b.addEventListener('click',function(){var o=d.classList.toggle('open');b.setAttribute('aria-expanded',o);});d.addEventListener('focusout',function(e){if(!d.contains(e.relatedTarget)){d.classList.remove('open');b.setAttribute('aria-expanded','false');}});});})();</script>"

home = SRC['home']
# ---------- header ----------
hdr = fix(between(home, '<header class="nav">', '</header>'))
json.dump({"meta": {"_elementor_data": json.dumps([wrap([html_widget(FONTS + '<div class="cc">' + hdr + '</div>' + CURJS + DDJS)])])}}, open(OUT + 'lib-170.json', 'w'))

# ---------- footer + shared cookie banner ----------
ftr = fix(between(home, '<footer>', '</footer>'))
ftr = ftr.replace('<a href="/privacy-policy/">Privacy Policy</a>', '<a href="/privacy-policy/">Privacy Policy</a>\n    <a href="#" data-cc-settings>Cookie settings</a>')
assert 'data-cc-settings' in ftr
sys.path.insert(0, ROOT + 'shared/consent')
from render import banner as render_banner, head_snippet
GA = 'G-E1WWZCLBRB'            # live coaching site, checked 15 Nov (coaching/TRACKING.md)
PIXEL = '1986332861692106'     # Matteo's Meta Pixel, confirmed for Coaching 15 Nov; loads only after Accept
OW = '43e5f685-37fc-4f78-9420-122fd2a3c5e3'   # OpenWidget org on the live coaching site
banner = render_banner(ga_id=GA, privacy_url='/privacy-policy/', pixel_id=PIXEL, openwidget_org=OW)
# moving topo background (shared/parallax, Matteo: same on every site); only on redesigned pages (.cc-page), like Tours
PARALLAX = open(ROOT + 'shared/parallax/parallax.html').read().strip().replace("(function(){", "(function(){if(!document.querySelector('.cc-page')&&!document.body.classList.contains('single-post'))return;", 1)
assert '.cc-page' in PARALLAX
# newsletter pop-up: the cigalacycling.com one (wp/nl-popup.html, same look and timing), with coaching wording and the
# Coaching Brevo list. Not on /tools/ pages (they have their own sign-up) or /contact/. Off until COACH_NL_URL is set.
sys.path.insert(0, ROOT + 'tools'); from coaching_common import COACH_NL_URL
widgets = [html_widget('<div class="cc">' + ftr + '</div>'), html_widget(banner), html_widget(PARALLAX)]
# newsletter footer band (main chat 15 Nov: same as cigalacycling.com and Tours, "everything consistent across sites"):
# wp/nl-band.html as it is, above the footer columns; the pop-up script below binds it and posts to the Coaching Brevo form
if COACH_NL_URL:
    widgets[0] = html_widget('<div class="cc">' + open(ROOT + 'wp/nl-band.html').read() + ftr + '</div>')
    css += ('\n/* ---- newsletter band (shared wp/nl-band.html) ---- */\nhtml .cc .nl-band .nl-t { font-family: Anton, Impact, "Arial Narrow", sans-serif; font-weight: 400; }'
            '\nhtml .cc .nl-band { border-bottom: 0 !important; }\nhtml .cc .nl-band .nl-band-in { padding-block: 40px !important; }\nhtml .cc .nl-band + footer { margin-top: 0 !important; }\n')
if COACH_NL_URL:
    pop = open(ROOT + 'wp/nl-popup.html').read()
    for a, b in [('<p class="nl-eyebrow">Newsletter</p>', '<p class="nl-eyebrow">Free training tips</p>'),
                 ('<p class="nl-t" id="nl-pop-t">Stay in the loop</p>', '<p class="nl-t" id="nl-pop-t">Train smarter, ride faster</p>'),
                 ("if(/^\\/contact\\/?$/.test(location.pathname)){return;}", "if(/^\\/(contact|tools)(\\/|$)/.test(location.pathname)){return;}")]:
        assert a in pop, a; pop = pop.replace(a, b)
    pop = re.sub(r"var URL='https://[^']+';", "var URL='" + COACH_NL_URL + "';", pop); assert COACH_NL_URL in pop
    # the description: same wording on every site now (one newsletter); set it whatever the main site's file says
    pop = re.sub(r'<p class="nl-d">.*?</p>', '<p class="nl-d">Training tips, news, blogs and deals on coaching, bike tours and our shop.</p>', pop, count=1)
    # the OpenWidget chat (loaded after Accept) sat above the pop-up on phones and covered the email field (main chat, 15 Nov)
    pop += '<style>#nl-pop{z-index:2147483647!important}#nl-pop .nl-t{font-family:Anton,Impact,"Arial Narrow",sans-serif!important}</style>'
    widgets.append(html_widget(pop))
json.dump({"meta": {"_elementor_data": json.dumps([wrap(widgets)])}}, open(OUT + 'lib-228.json', 'w'))
json.dump({"title": "Cigala consent mode default", "status": "publish",
           "meta": {"_elementor_location": "elementor_head", "_elementor_priority": 1, "_elementor_code": head_snippet()}}, open(OUT + 'snippet-head.json', 'w'))

# ---------- pages ----------
def live_widget(page_id, wtype):
    d = json.loads(json.load(open(ROOT + f'stg-coaching/backup/page-{page_id}.json'))['meta']['_elementor_data'])
    def walk(els):
        for e in els:
            if e.get('widgetType') == wtype: return e
            r = walk(e.get('elements', []))
            if r: return r
    w = copy.deepcopy(walk(d)); assert w, (page_id, wtype); return w

def build_page(key):
    src = SRC[key]; els = []; content = []
    for b in blocks_of(src):
        b = fix(b)
        content.append('<div class="cc cc-page">' + b + '</div>')
        lw = re.search(r'data-live-widget="(\d+):([\w-]+)"', b)
        if lw:   # a live WordPress widget (the blog's automatic post list) where the preview has a placeholder
            w = live_widget(int(lw.group(1)), lw.group(2)); w['settings']['_css_classes'] = 'cc-blog'
            els.append(wrap([w], 'cc-wrap cc-blog-wrap')); continue
        if 'id="contact"' in b:   # any page with the contact section gets the live Elementor form
            # live Elementor form (sends to info@cigalacycling.com) instead of the preview's static form
            form = live_widget(3338, 'form')
            form['settings']['_css_classes'] = 'cc-form'
            form['settings']['email_subject'] = 'New message from the Coaching website'
            # shared/BUSINESS.md "Form emails" (Matteo 15 Nov): Coaching forms go to matteo@, sent from noreply@cigalacycling.com
            st = form['settings']
            for k in ('email_to', 'email_to_2'): st[k] = 'matteo@cigalacycling.com'
            for k in ('email_from', 'email_from_2'): st[k] = 'noreply@cigalacycling.com'
            for k in ('email_from_name', 'email_from_name_2'): st[k] = 'Cigala Cycling Coaching'
            st['email_subject_2'] = 'New message from the Coaching website'
            # Matteo 15 Nov: add a phone number and make every field compulsory. Phone is a text field: Elementor's
            # tel field rejects spaces, and people type "+353 87 ...". [all-fields] in the email includes it.
            form['settings']['mark_required'] = 'yes'   # show the * so people can see every field is compulsory
            ff = form['settings']['form_fields']
            for f in ff: f['required'] = 'true'; f['width'] = '100'
            for f in ff:   # the form shows placeholders, not labels: a * on each, so it's clear every field is compulsory
                if f.get('placeholder') and not f['placeholder'].endswith('*'): f['placeholder'] += ' *'
            if not any(f.get('custom_id') == 'phone' for f in ff):
                ff.insert(2, {'custom_id': 'phone', 'field_type': 'text', 'required': 'true', 'field_label': 'Phone',
                              'placeholder': 'Phone (with country code) *', 'width': '100', '_id': 'cc0phon'})
            # per-page enquiry forms (Matteo 15 Nov: bike fit reservation, 1-to-1, club talks...): the section can set the
            # email subject and the message placeholder, and put any content on the left between <!--side--> markers
            subj = re.search(r'data-subject="([^"]+)"', b); hint = re.search(r'data-msg="([^"]+)"', b)
            if subj:
                st['email_subject'] = st['email_subject_2'] = html.unescape(subj.group(1))
            if hint:
                for f in ff:
                    if f.get('field_type') == 'textarea': f['placeholder'] = html.unescape(hint.group(1))
            pre, post = b.split('<form', 1)
            post = post.split('</form>', 1)[1]
            lcls = 'cc-wrap'
            if '<!--side-->' in pre:
                photo = pre[pre.index('<!--side-->') + 11:pre.index('<!--/side-->')]
                pre = pre[pre.index('<!--/side-->'):]
            else:
                photo = re.search(r'<div class="photo rider">.*?</div>', pre, re.S).group(0); lcls = 'cc-wrap cc-contact-ph'
            text = pre[pre.index('<div class="eyebrow">'):]
            left = wrap([html_widget('<div class="cc cc-page">' + photo + '</div>')], lcls, True, width={"unit": "%", "size": 42}, width_mobile={"unit": "%", "size": 100})
            right = wrap([html_widget('<div class="cc cc-page"><div>' + text + '</div></div>'), form], 'cc-wrap', True, width={"unit": "%", "size": 58}, width_mobile={"unit": "%", "size": 100})
            row = wrap([left, right], 'cc-wrap cc-contact', True, flex_direction='row', flex_direction_mobile='column',
                       flex_gap={"unit": "px", "size": 48, "column": "48", "row": "24"}, flex_align_items='center' if 'cc-contact-ph' in lcls else 'flex-start',
                       boxed_width={"unit": "px", "size": 1200}, content_width='boxed',
                       padding={"unit": "px", "top": "72", "right": "16", "bottom": "0", "left": "16", "isLinked": False}, _element_id='contact')
            els.append(wrap([row]))
            continue
        w = [html_widget('<div class="cc cc-page">' + b + '</div>')]
        # (the Shapo widget is gone: Matteo chose our own review cards + a link to the Google reviews, 15 Nov)
        els.append(wrap(w))
    for s in page_js(src): els[-1]['elements'].append(html_widget(s))
    payload = {"meta": {"_elementor_data": json.dumps(els), "_elementor_edit_mode": "builder", "_elementor_template_type": "wp-page"}, "content": '\n'.join(content)}
    if PAGES[key] == 'privacy':
        payload.update({"title": "Privacy Policy", "slug": "privacy-policy", "status": "publish"})
    if PAGES[key] in NEW:
        t, slug, parent = NEW[PAGES[key]]
        payload.update({"title": t, "slug": slug, "status": "publish", "parent_slug": parent})
    json.dump(payload, open(OUT + f'page-{PAGES[key]}.json', 'w'))
    return len(els)

n = {k: build_page(k) for k in PAGES}

# ---------- blog loop item 4718: post title H1 -> H3 (one H1 per page) ----------
li = json.load(open(ROOT + 'stg-coaching/backup/lib-4718.json'))
lid = json.loads(li['meta']['_elementor_data'])
def _t(els):
    for e in els:
        if e.get('widgetType') == 'theme-post-title': e['settings']['header_size'] = 'h3'
        _t(e.get('elements', []))
_t(lid)
json.dump({"meta": {"_elementor_data": json.dumps(lid)}}, open(OUT + 'lib-4718.json', 'w'))

# ---------- kit: add the scoped CSS, keep everything else ----------
kit = copy.deepcopy(json.load(open(ROOT + 'stg-coaching/backup/lib-6.json'))['meta']['_elementor_page_settings'])
kit['custom_css'] = css
json.dump({"meta": {"_elementor_page_settings": kit}}, open(OUT + 'lib-6.json', 'w'))
print('built:', n, '| css', len(css), '| header', len(hdr), '| footer', len(ftr))
