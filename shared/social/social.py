"""Shared social icon row for all Cigala sites (footer).
Icons: Simple Icons v16.37.0 (CC0 licence), monochrome; they use currentColor, so they follow the CSS colour.
Usage:
    import sys; sys.path.insert(0, ROOT + 'shared/social'); from social import social_row, SOCIAL_CSS
    html = social_row([('whatsapp', 'https://wa.me/...'), ('instagram', 'https://www.instagram.com/...'), ...])
Put SOCIAL_CSS in the site's CSS once.
"""
import os, json, html as _h
HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = json.load(open(os.path.join(HERE, 'icons.json')))

# The accounts Matteo uses (same on every site unless a site needs fewer)
CIGALA = [
    ('whatsapp', 'https://wa.me/message/WVBRO6XAMQMCH1'),
    ('instagram', 'https://www.instagram.com/cigalacycling/'),
    ('facebook', 'https://www.facebook.com/CigalaCycling/'),
    ('youtube', 'https://www.youtube.com/@cigalacycling'),
    ('tiktok', 'https://www.tiktok.com/@cigalacycling'),
    ('x', 'https://x.com/CigalaCycling'),
    ('threads', 'https://www.threads.com/@cigalacycling'),
]

def social_row(links=CIGALA):
    out = []
    for key, url in links:
        ic = ICONS[key]; label = ic['label'] if key != 'x' else 'X (Twitter)'
        out.append(f'<a href="{_h.escape(url)}" target="_blank" rel="noopener" aria-label="{label}" title="{label}">'
                   f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{ic["path"]}"/></svg></a>')
    return '<div class="cc-social">' + ''.join(out) + '</div>'

SOCIAL_CSS = """
.cc-social { display: flex; flex-wrap: wrap; gap: 4px; margin: 6px 0 0 -10px; }
.cc-social a { display: inline-grid; place-items: center; width: 40px; height: 40px; border-radius: 8px; color: var(--text-2, #d0d6e0); text-decoration: none; transition: color .15s, background-color .15s; }
.cc-social a:hover, .cc-social a:active { color: var(--green-text, #34c46a); background: rgba(255,255,255,.04); }
.cc-social a:focus-visible { outline: 2px solid var(--green, #009a44); outline-offset: 2px; }
.cc-social svg { width: 20px; height: 20px; fill: currentColor; display: block; }
"""
