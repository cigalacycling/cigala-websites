"""Line icons in the Vivify style (Marine 19 Nov: "put icons to describe things in a box").

24x24 viewBox, stroke = currentColor (aqua), 1.7px, round caps/joins, no fill: same look as the site's existing icons.
add_icons(html) puts the matching icon at the top of each box (pcard / scard / plan note) by its title; numbered
boxes get it in the top-right corner. Boxes with a photo, flags, and boxes that already have an icon are left alone.
"""
import re

P = {
 'bike': '<circle cx="5.5" cy="16.5" r="3.5"/><circle cx="18.5" cy="16.5" r="3.5"/><path d="M5.5 16.5l4-8h6l3 8M9.5 8.5h-2M12 16.5l3.5-8M14 6h2.5"/>',
 'mountain': '<path d="M3 19l6-10 4 6 2-3 6 7z"/><path d="M8.2 10.4l1.6 1.4 1.3-1.2"/>',
 'road': '<path d="M8 3L4 21M16 3l4 18M12 4v2.5M12 10v3M12 16.5v3.5"/>',
 'stopwatch': '<circle cx="12" cy="13.5" r="7.5"/><path d="M12 13.5V9.5M10 2.5h4M18.5 6.5l1.5-1.5"/>',
 'waves': '<path d="M3 9c2-1.6 4-1.6 6 0s4 1.6 6 0 4-1.6 6 0M3 14c2-1.6 4-1.6 6 0s4 1.6 6 0 4-1.6 6 0M3 19c2-1.6 4-1.6 6 0s4 1.6 6 0 4-1.6 6 0"/>',
 'medal': '<circle cx="12" cy="15" r="5.5"/><path d="M8.5 10.5L5.5 3h4l2.5 5M15.5 10.5l3-7.5h-4L12 8M12 12.5v5"/>',
 'flag': '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
 'calendar': '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4M8 14h2M14 14h2M8 17h2"/>',
 'compass': '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
 'people': '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3.5 19c.5-3.5 2.8-5.5 5.5-5.5s5 2 5.5 5.5M15 14.2c2.6-.4 4.8 1.3 5.5 4.8"/>',
 'cap': '<path d="M2.5 9.5L12 5l9.5 4.5L12 14z"/><path d="M6.5 11.5v4c1.5 1.6 3.4 2.4 5.5 2.4s4-.8 5.5-2.4v-4M21.5 9.5v5"/>',
 'trophy': '<path d="M7.5 4h9v5a4.5 4.5 0 0 1-9 0zM7.5 6H4.5c0 3 1.5 4.5 3.3 4.7M16.5 6h3c0 3-1.5 4.5-3.3 4.7M12 13.5V17M8.5 20.5h7M9.5 17h5v3.5h-5z"/>',
 'chart': '<path d="M3.5 20.5h17M5 16l4.5-5 3.5 3 6-7"/><path d="M15 7h4v4"/>',
 'heart': '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/><path d="M7.5 12h2.5l1.2-2 1.8 4 1.2-2h2.3"/>',
 'scale': '<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><path d="M8 9a5.5 5.5 0 0 1 8 0M12 9.5l1.5-2"/>',
 'bolt': '<path d="M13 2.5L5 13.5h6l-1 8 8-11h-6z"/>',
 'plane': '<path d="M3 13.5l18-7.5-4.5 13-4-5.5-5.5 3 1-5z"/><path d="M12.5 13.5L21 6"/>',
 'plate': '<circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="3"/><path d="M3 4v5a2 2 0 0 0 2 2v9M5 4v5M21 4c-1.5 1-2 3-2 6h2v10"/>',
 'bottle': '<path d="M10 2.5h4M10.5 2.5v3L8.5 8v12a1.5 1.5 0 0 0 1.5 1.5h4a1.5 1.5 0 0 0 1.5-1.5V8l-2-2.5v-3M8.5 12h7M8.5 16h7"/>',
 'cycle': '<path d="M20 12a8 8 0 0 1-13.7 5.6M4 12a8 8 0 0 1 13.7-5.6"/><path d="M17.7 2.8v3.8h-3.8M6.3 21.2v-3.8h3.8"/><circle cx="12" cy="12" r="2"/>',
 'drop': '<path d="M12 3c3.5 4.5 6 8 6 11a6 6 0 0 1-12 0c0-3 2.5-6.5 6-11z"/><path d="M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5"/>',
 'flask': '<path d="M9.5 3h5M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2h12.4a1.5 1.5 0 0 0 1.3-2L14 9V3"/><path d="M7 15h10"/>',
 'leaf': '<path d="M5 19c0-8 5-13 15-14-1 10-6 15-14 15"/><path d="M5 19c3-5 6-8 10-10"/>',
 'chat': '<path d="M4 5.5h16v10H10l-4.5 4v-4H4z"/><path d="M8 9.5h8M8 12.5h5"/>',
 'target': '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1"/>',
 'card': '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3 10h18M7 14.5h4"/>',
 'video': '<rect x="3" y="6.5" width="12.5" height="11" rx="2"/><path d="M15.5 10.5l5.5-3v9l-5.5-3"/>',
 'doc': '<path d="M6 2.5h8.5L19 7v14.5H6z"/><path d="M14 2.5V7h5M9 12h7M9 15.5h7M9 9h3"/>',
 'lotus': '<path d="M12 18c-3-2-4.5-5-4.5-8.5 2.2 1 3.6 2.6 4.5 5 .9-2.4 2.3-4 4.5-5 0 3.5-1.5 6.5-4.5 8.5zM12 18c-4.5 0-8-2-9-5.5 2.5-.3 4.5.4 6.2 1.9M12 18c4.5 0 8-2 9-5.5-2.5-.3-4.5.4-6.2 1.9"/>',
 'moon': '<path d="M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10z"/>',
 'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.7 3.8 5.7 3.8 9s-1.2 6.3-3.8 9c-2.6-2.7-3.8-5.7-3.8-9S9.4 5.7 12 3z"/>',
 'apple': '<path d="M12 7.5c-2-1.6-6.5-1.2-6.5 4 0 4.5 3 8.5 5 8.5 1 0 1-.6 1.5-.6s.5.6 1.5.6c2 0 5-4 5-8.5 0-5.2-4.5-5.6-6.5-4z"/><path d="M12 7.5c0-2 .8-3.5 2.5-4.5"/>',
 'hands': '<path d="M4 13.5l3.5-3.5c1-1 2.5-1 3.5 0l1 1M20 13.5L16.5 10c-1-1-2.5-1-3.5 0l-3 3c-.6.6-.6 1.6 0 2.2s1.6.6 2.2 0L14 13.5M4 13.5l5 5c.8.8 2 .8 2.8 0M20 13.5l-5 5c-.8.8-2 .8-2.8 0"/>',
 'link': '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
 'coins': '<ellipse cx="9" cy="7" rx="5.5" ry="2.5"/><path d="M3.5 7v4c0 1.4 2.5 2.5 5.5 2.5M3.5 11v4c0 1.4 2.5 2.5 5.5 2.5"/><ellipse cx="15" cy="13" rx="5.5" ry="2.5"/><path d="M9.5 13v4c0 1.4 2.5 2.5 5.5 2.5s5.5-1.1 5.5-2.5v-4"/>',
 'arrow': '<circle cx="12" cy="12" r="9"/><path d="M8 12h8M13 8.5l3.5 3.5-3.5 3.5"/>',
}

# title keywords -> icon (first match wins; matched on the lowercase title)
RULES = [
 (r'mountain bike|^mtb', 'mountain'), (r'cyclocross', 'bike'), (r'^track', 'stopwatch'), (r'gravel', 'compass'),
 (r'road racing', 'road'), (r'gran fondo', 'mountain'), (r'sportive', 'people'), (r'multi-day|ultra', 'calendar'),
 (r'full distance', 'medal'), (r'middle distance', 'flag'), (r'olympic|sprint', 'stopwatch'), (r'off-road|multisport', 'compass'),
 (r'msc|qualif', 'cap'), (r'worldtour|professional cyclist', 'trophy'), (r'built on your training', 'chart'), (r'whole athlete', 'heart'),
 (r'body composition', 'scale'), (r'race calendar|stage race', 'calendar'), (r'race-day fuelling|top level', 'bolt'),
 (r'travel|camp|altitude', 'plane'), (r'eat enough', 'plate'), (r'fuel on the bike', 'bottle'), (r'know your cycle', 'cycle'),
 (r'iron', 'drop'), (r'evidence', 'flask'), (r'fuel for performance', 'bolt'), (r'sustainable|habit', 'leaf'),
 (r'pick a time', 'calendar'), (r'talk it through', 'chat'), (r'next step', 'target'), (r'buy your plan', 'card'),
 (r'30-minute call|call$', 'video'), (r'pdf', 'doc'), (r'vinyasa', 'waves'), (r'yin yoga', 'moon'), (r'yoga for cyclists', 'bike'),
 (r'^cyclists$', 'bike'), (r'triathlete', 'waves'), (r'race day', 'flag'), (r'worldwide', 'globe'), (r'nutrition coaching', 'apple'),
 (r'workshop|talk', 'people'), (r'massage', 'hands'), (r'partnered|trainingpeaks', 'link'), (r'euro|dollar', 'coins'),
 (r'not sure', 'chat'),
]

def svg(name, size=27):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P[name]}</svg>')

def pick(title):
    t = ' '.join(re.sub(r'<[^>]+>|&amp;', ' ', title).lower().split())
    for rx, name in RULES:
        if re.search(rx, t): return name
    return None

CSS = """
/* Marine 19 Nov: icons in boxes */
.vic{display:inline-flex;align-items:center;justify-content:center;width:54px;height:54px;border-radius:14px;color:var(--aqua);
 background:linear-gradient(145deg,rgba(177,216,221,.16),rgba(177,216,221,.04));border:1px solid rgba(177,216,221,.28);margin:0 0 16px;flex:none}
.vic.corner{position:absolute;top:22px;right:22px;margin:0}
.pcard,.scard .tx,.note{position:relative}
.note .vic{width:38px;height:38px;border-radius:10px;margin:0 0 10px}
.note .vic svg{width:20px;height:20px}
@media (hover:hover){.pcard:hover .vic,.scard:hover .vic{color:var(--lime-text);border-color:rgba(128,163,21,.55);transition:color .3s,border-color .3s}}
"""

BOX = re.compile(r'(<(div|a|article) class="(pcard|scard|note)[^"]*"[^>]*>)(.*?)(?=</\2>)', re.S)

def add_icons(html):
    def one(m):
        open_tag, inner = m.group(1), m.group(4)
        if 'flagcard' in open_tag or 'class="ph"' in inner or 'class="vic' in inner: return m.group(0)
        t = re.search(r'class="h3"[^>]*>(.*?)</span>|<b>(.*?)</b>|<h3[^>]*>(.*?)</h3>', inner, re.S)
        title = (t and next(x for x in t.groups() if x)) or re.sub(r'<[^>]+>', ' ', inner)[:80]
        name = pick(title)
        if not name: return m.group(0)
        numbered = 'class="num"' in inner
        ic = f'<span class="vic{" corner" if numbered else ""}">{svg(name)}</span>'
        if m.group(3) == 'scard' and '<div class="tx">' in inner:
            return open_tag + inner.replace('<div class="tx">', '<div class="tx">' + ic, 1)
        return open_tag + ic + inner
    return BOX.sub(one, html)
