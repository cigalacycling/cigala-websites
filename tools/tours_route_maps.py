"""Route maps for the 15 Tours trips, drawn in the Cigala style (Matteo 15 Nov: "make the routes our style and colours").

Dark land on a darker sea, country borders, real lake shapes, the route in green through the overnight stops
(red numbered dots), the start/base in white, and key climbs / places as small markers with their names.
Data: Natural Earth (public domain): countries-10m from npm world-atlas@2.0.2; lakes and rivers 1:10m (+ Europe supplements)
from the Natural Earth repository (github.com/nvkelso/natural-earth-vector, geojson/).
Stop coordinates are approximate (town centres / pass summits), typed in ROUTES below: check them on review.

Usage: python3 -I tools/tours_route_maps.py      -> tourspages/maps/<slug>.svg (inlined by build_tours_trips.py)
The npm data is downloaded once into a scratch folder (GEO env var, default /tmp/cigala-geo).
"""
import os, json, math, subprocess, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
GEO = os.environ.get('GEO', '/tmp/cigala-geo')
OUT = ROOT + 'tourspages/maps/'

# kind: 'base' (white, where you stay / start), 'stop' (numbered overnight stop on the route), 'climb' (small marker)
# route: names in order, drawn as the green line. pos: label side r/l/t/b. note: a line under the map.
ROUTES = {
 'dolomites': {'route': ['La Villa', 'Canazei'], 'pts': [
    ('La Villa', 46.586, 11.900, 'base', 'r'), ('Canazei', 46.476, 11.770, 'base', 'l'),
    ('Passo Gardena', 46.549, 11.809, 'climb', 'l'), ('Passo Sella', 46.509, 11.762, 'climb', 'l'), ('Passo Pordoi', 46.487, 11.811, 'climb', 'r'),
    ('Campolongo', 46.519, 11.874, 'climb', 'r'), ('Passo Giau', 46.483, 12.054, 'climb', 'r'), ('Falzarego', 46.519, 12.008, 'climb', 't'),
    ('Tre Cime di Lavaredo', 46.618, 12.302, 'climb', 'l'), ('Cortina', 46.540, 12.136, 'climb', 'r'),
    ('San Pellegrino', 46.380, 11.787, 'climb', 'r'), ('Fedaia', 46.459, 11.869, 'climb', 'r')],
    'note': 'Transfers from and to Venice Marco Polo Airport (VCE)'},
 'maratona-dles-dolomites': {'route': [], 'pts': [
    ('La Villa · Alta Badia', 46.586, 11.900, 'base', 'r'), ('Corvara', 46.551, 11.873, 'climb', 'l'),
    ('Passo Gardena', 46.549, 11.809, 'climb', 'l'), ('Passo Sella', 46.509, 11.762, 'climb', 'l'), ('Passo Pordoi', 46.487, 11.811, 'climb', 'b'),
    ('Campolongo', 46.519, 11.874, 'climb', 'r'), ('Passo Giau', 46.483, 12.054, 'climb', 'r'), ('Falzarego', 46.519, 12.008, 'climb', 'r'),
    ('Valparola', 46.531, 11.989, 'climb', 't')], 'note': 'Every ride starts from the hotel in La Villa, Alta Badia'},
 'french-alps': {'route': ['Saint-Jean-de-Maurienne', 'Monêtier-les-Bains', 'Barcelonnette'], 'pts': [
    ('Saint-Jean-de-Maurienne', 45.277, 6.346, 'stop', 'r'), ('Monêtier-les-Bains', 44.976, 6.508, 'stop', 'r'), ('Barcelonnette', 44.387, 6.652, 'stop', 'l'),
    ('Col de la Madeleine', 45.435, 6.373, 'climb', 'r'), ('Lacets de Montvernier', 45.315, 6.335, 'climb', 'l'), ('Col du Glandon', 45.239, 6.177, 'climb', 'l'),
    ('Croix de Fer', 45.227, 6.203, 'climb', 'b'), ('Col du Télégraphe', 45.203, 6.444, 'climb', 'r'), ('Col du Galibier', 45.064, 6.408, 'climb', 'l'),
    ("Alpe d'Huez", 45.092, 6.070, 'climb', 'l'), ("Col d'Izoard", 44.820, 6.735, 'climb', 'r'), ('Col de Vars', 44.539, 6.703, 'climb', 'r'),
    ('Col de la Bonette', 44.326, 6.807, 'climb', 'r')]},
 'wonderful-slovenia': {'route': ['Nova Gorica', 'Postojna', 'Škofja Loka', 'Lake Bled', 'Bovec', 'Nova Gorica'], 'pts': [
    ('Nova Gorica', 45.956, 13.648, 'stop', 'l'), ('Postojna', 45.776, 14.213, 'stop', 'r'), ('Škofja Loka', 46.166, 14.306, 'stop', 'r'),
    ('Lake Bled', 46.369, 14.114, 'stop', 'r'), ('Bovec', 46.338, 13.552, 'stop', 'l'), ('Ljubljana', 46.051, 14.506, 'climb', 'r'),
    ('Vršič Pass', 46.433, 13.743, 'climb', 't')]},
 'lake-garda-gravel': {'route': [], 'pts': [
    ('Moniga del Garda', 45.528, 10.540, 'base', 'l'), ('Sirmione', 45.493, 10.608, 'climb', 'b'), ('Valtenesi', 45.590, 10.510, 'climb', 'l'),
    ('Solferino', 45.372, 10.566, 'climb', 'l'), ('Borghetto sul Mincio', 45.355, 10.744, 'climb', 'b'), ('Valpolicella', 45.535, 10.910, 'climb', 'r'),
    ('Lazise', 45.505, 10.733, 'climb', 'r')], 'note': 'Every ride starts from the hotel in Moniga del Garda'},
 'lake-garda-and-stelvio': {'route': [], 'pts': [
    ('Moniga del Garda', 45.528, 10.540, 'base', 'l'), ('Sirmione', 45.493, 10.608, 'climb', 'b'), ('Tremosine · Strada della Forra', 45.775, 10.760, 'climb', 'l'),
    ('Riva del Garda', 45.885, 10.841, 'climb', 'r'), ('Malcesine', 45.764, 10.809, 'climb', 'r'), ('Garda', 45.575, 10.707, 'climb', 'r'), ('Salò', 45.607, 10.522, 'climb', 'l')],
    'note': 'Day 3: day trip to Passo dello Stelvio (2,757 m), about 2 hours north by van'},
 'alpine-gravel-escape': {'route': [], 'pts': [
    ('Bormio', 46.468, 10.370, 'base', 'b'), ('Passo dello Stelvio', 46.529, 10.453, 'climb', 'r'), ('Livigno', 46.538, 10.135, 'climb', 'l'),
    ('Val Viola', 46.420, 10.200, 'climb', 'l'), ('Val Grosina', 46.330, 10.250, 'climb', 'l'), ('Cancano lakes', 46.525, 10.300, 'climb', 't')],
    'note': 'Transfers from and to Milan Bergamo Airport (BGY)'},
 'italian-alps': {'route': [], 'pts': [
    ('Bormio', 46.468, 10.370, 'base', 'r'), ('Passo dello Stelvio', 46.529, 10.453, 'climb', 'r'), ('Mortirolo', 46.247, 10.293, 'climb', 'l'),
    ('Passo Foscagno', 46.495, 10.217, 'climb', 'l'), ('Livigno', 46.538, 10.135, 'climb', 'l'), ('Passo Gavia', 46.344, 10.488, 'climb', 'r'),
    ('Cancano lakes', 46.525, 10.300, 'climb', 't')], 'note': 'Transfers from and to Milan Bergamo Airport (BGY)'},
 'tuscany-epic-gravel': {'route': ['Castagneto Carducci', 'Peccioli', "Colle di Val d'Elsa", 'Pienza', 'Marina di Grosseto', 'Castagneto Carducci'], 'pts': [
    ('Castagneto Carducci', 43.160, 10.610, 'stop', 'l'), ('Peccioli', 43.548, 10.719, 'stop', 'l'), ("Colle di Val d'Elsa", 43.421, 11.126, 'stop', 'r'),
    ('Pienza', 43.077, 11.679, 'stop', 'r'), ('Marina di Grosseto', 42.718, 10.981, 'stop', 'l'), ('Siena', 43.318, 11.331, 'climb', 'r'),
    ('Volterra', 43.402, 10.861, 'climb', 'r')]},
 'cyprus-crossing-gravel': {'route': ['Paphos', 'Lofou', 'Agros', 'Kalopanagiotis', 'Polis', 'Paphos'], 'pts': [
    ('Paphos', 34.776, 32.424, 'stop', 'l'), ('Lofou', 34.810, 32.888, 'stop', 'b'), ('Agros', 34.917, 33.016, 'stop', 'r'),
    ('Kalopanagiotis', 34.993, 32.830, 'stop', 't'), ('Polis', 35.035, 32.426, 'stop', 'l'), ('Mount Olympus', 34.936, 32.864, 'climb', 'r')]},
 'tour-of-flanders-experience': {'route': [], 'pts': [
    ('Waregem', 50.888, 3.426, 'base', 'l'), ('Oudenaarde', 50.845, 3.605, 'climb', 'r'), ('Oude Kwaremont', 50.787, 3.548, 'climb', 'l'),
    ('Paterberg', 50.782, 3.574, 'climb', 'b'), ('Koppenberg', 50.807, 3.601, 'climb', 'r'), ('Muur van Geraardsbergen', 50.770, 3.873, 'climb', 'l'),
    ('Bruges', 51.209, 3.225, 'climb', 'r')], 'note': 'Every ride starts from the hotel in Waregem'},
 'chianti-gran-fondo-strade-bianche': {'route': [], 'pts': [
    ('Radda in Chianti', 43.486, 11.374, 'base', 'r'), ('Castellina in Chianti', 43.471, 11.287, 'climb', 'l'), ('Gaiole in Chianti', 43.467, 11.435, 'climb', 'r'),
    ('Siena · Piazza del Campo', 43.318, 11.331, 'climb', 'r'), ('Monteaperti', 43.364, 11.410, 'climb', 'r'), ('Montalcino', 43.058, 11.489, 'climb', 'r'),
    ('Greve in Chianti', 43.584, 11.317, 'climb', 'l')], 'note': 'Every ride starts from the hotel in Radda in Chianti'},
 'discover-the-algarve-granfondo': {'route': [], 'pts': [
    ('Quinta do Lago', 37.028, -8.018, 'base', 'l'), ('Faro', 37.019, -7.931, 'climb', 'b'), ('Loulé', 37.138, -8.020, 'climb', 'l'),
    ('Querença', 37.198, -7.989, 'climb', 'r'), ('Alto do Malhão', 37.214, -7.940, 'climb', 'r'), ('Tavira', 37.127, -7.649, 'climb', 'r')],
    'note': 'Every ride starts from Vilar do Golf, Quinta do Lago'},
 'lake-como-gran-fondo-il-lombardia': {'route': [], 'pts': [
    ('Como', 45.808, 9.085, 'base', 'l'), ('Civiglio', 45.826, 9.110, 'climb', 'r'), ('Madonna del Ghisallo', 45.923, 9.268, 'climb', 'r'),
    ('Bellagio', 45.987, 9.262, 'climb', 'r'), ('Muro di Sormano', 45.876, 9.240, 'climb', 'l'), ('Varenna', 46.010, 9.284, 'climb', 't'),
    ('Lecco', 45.853, 9.390, 'climb', 'r')]},
 'italys-coast-to-coast': {'route': ['Viareggio', 'Peccioli', 'Siena', 'Montepulciano', 'Assisi', 'Camerino', 'San Benedetto del Tronto'], 'pts': [
    ('Viareggio', 43.872, 10.250, 'stop', 'l'), ('Peccioli', 43.548, 10.719, 'stop', 'l'), ('Siena', 43.318, 11.331, 'stop', 'b'),
    ('Montepulciano', 43.093, 11.781, 'stop', 'l'), ('Assisi', 43.071, 12.617, 'stop', 'b'), ('Camerino', 43.135, 13.068, 'stop', 't'),
    ('San Benedetto del Tronto', 42.948, 13.881, 'stop', 'l')]},
}

# ---------- data ----------
NE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
NE_FILES = ['ne_10m_lakes', 'ne_10m_lakes_europe', 'ne_10m_rivers_lake_centerlines', 'ne_10m_rivers_europe']
def geo_files():
    import ssl, urllib.request
    os.makedirs(GEO, exist_ok=True)
    cp = f'{GEO}/world-atlas/package/countries-10m.json'
    if not os.path.exists(cp):
        tgz = subprocess.run(['npm', 'pack', '-q', 'world-atlas@2.0.2'], cwd=GEO, capture_output=True, text=True, check=True).stdout.strip().split('\n')[-1]
        os.makedirs(f'{GEO}/world-atlas', exist_ok=True)
        subprocess.run(['tar', 'xzf', tgz, '-C', f'{GEO}/world-atlas'], cwd=GEO, check=True)
    ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt') if os.path.exists('/root/.ccr/ca-bundle.crt') else None
    for n in NE_FILES:
        if not os.path.exists(f'{GEO}/{n}.geojson'):
            open(f'{GEO}/{n}.geojson', 'wb').write(urllib.request.urlopen(NE + n + '.geojson', context=ctx, timeout=120).read())
    return {'countries': cp, 'lakes': [f'{GEO}/{n}.geojson' for n in NE_FILES[:2]], 'rivers': [f'{GEO}/{n}.geojson' for n in NE_FILES[2:]]}

def geojson_lines(paths):
    out = []
    for p in paths:
        for f in json.load(open(p))['features']:
            g = f['geometry']
            if not g: continue
            if g['type'] == 'LineString': out.append(g['coordinates'])
            elif g['type'] == 'MultiLineString': out += g['coordinates']
    return out

def topo_polys(path):
    """TopoJSON (quantized) -> list of rings [(lon, lat)], for every country."""
    t = json.load(open(path)); sc, tr = t['transform']['scale'], t['transform']['translate']
    arcs = []
    for a in t['arcs']:
        x = y = 0; pts = []
        for dx, dy in a:
            x += dx; y += dy; pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
        arcs.append(pts)
    def ring(idx):
        out = []
        for i in idx:
            pts = arcs[i] if i >= 0 else arcs[~i][::-1]
            out += pts if not out else pts[1:]
        return out
    rings = []
    for g in t['objects']['countries']['geometries']:
        if g['type'] == 'Polygon': rings += [ring(r) for r in g['arcs']]
        elif g['type'] == 'MultiPolygon': rings += [ring(r) for p in g['arcs'] for r in p]
    return rings

def geojson_polys(paths):
    rings = []
    for path in paths: rings += _polys(path)
    return rings

def _polys(path):
    rings = []
    d = json.load(open(path))
    geoms = [f['geometry'] for f in d['features']] if 'features' in d else d.get('geometries', [])
    for g in geoms:
        if not g: continue
        if g['type'] == 'Polygon': rings += g['coordinates']
        elif g['type'] == 'MultiPolygon': rings += [r for p in g['coordinates'] for r in p]
    return rings

# ---------- drawing ----------
W, H = 900, 640
def draw(slug, spec, countries, lakes, rivers):
    pts = spec['pts']
    lats = [p[1] for p in pts]; lons = [p[2] for p in pts]
    lat0 = (min(lats) + max(lats)) / 2; k0 = math.cos(math.radians(lat0))
    span_x = (max(lons) - min(lons)) * k0; span_y = max(lats) - min(lats)
    span = max(span_x / W * H, span_y, 0.08) * 1.8          # padding around the points
    s = H / span                                               # px per degree latitude
    cx, cy = (min(lons) + max(lons)) / 2, lat0
    P = lambda lon, lat: (W / 2 + (lon - cx) * k0 * s, (H - 40) / 2 - (lat - cy) * s)   # room for the legend at the bottom
    bx0, bx1 = cx - W / 2 / (k0 * s) - .5, cx + W / 2 / (k0 * s) + .5
    by0, by1 = cy - H / 2 / s - .5, cy + H / 2 / s + .5
    def area(r):
        a = 0
        for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]):
            X1, Y1 = P(x1, y1); X2, Y2 = P(x2, y2); a += X1 * Y2 - X2 * Y1
        return abs(a) / 2
    def path(rings, min_area=0):
        out = []
        for r in rings:
            if min_area and area(r) < min_area: continue
            if min_area and (max(x for x, y in r) - min(x for x, y in r) > 3 or max(y for x, y in r) - min(y for x, y in r) > 3): continue   # lakes: skip huge stray rings
            if not any(bx0 <= x <= bx1 and by0 <= y <= by1 for x, y in r): continue
            d, last = [], None
            for x, y in r:
                X, Y = P(x, y)
                if last and abs(X - last[0]) < .8 and abs(Y - last[1]) < .8: continue
                d.append(f'{X:.1f},{Y:.1f}'); last = (X, Y)
            if len(d) > 2: out.append('M' + 'L'.join(d) + 'Z')
        return ''.join(out)
    land, water = path(countries), path(lakes, 60)   # skip specks: only lakes you can see
    def lines(ls):
        out = []
        for l in ls:
            if not any(bx0 <= x <= bx1 and by0 <= y <= by1 for x, y in l): continue
            d = [f'{P(x, y)[0]:.1f},{P(x, y)[1]:.1f}' for x, y in l]
            if len(d) > 1: out.append('M' + 'L'.join(d))
        return ''.join(out)
    river = lines(rivers)
    by = {p[0]: p for p in pts}
    E = lambda x: html.escape(x, quote=True)
    svg = [f'<svg class="rmap" viewBox="0 0 {W} {H}" role="img" aria-label="{E(spec.get("label", "Route map"))}" xmlns="http://www.w3.org/2000/svg">',
           '<defs><filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4"/></filter>'
           '<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity=".03"/></pattern></defs>',
           f'<rect width="{W}" height="{H}" fill="#0a0c0e"/><rect width="{W}" height="{H}" fill="url(#grid)"/>',
           f'<path d="{land}" fill="#1b1e22" stroke="#3a3f46" stroke-width="1" fill-rule="evenodd"/>',
           f'<path d="{river}" fill="none" stroke="#1d4f63" stroke-width="1.2" stroke-opacity=".8"/>',
           f'<path d="{water}" fill="#0f2a36" stroke="#1d4f63" stroke-width="1"/>']
    route = [P(by[n][2], by[n][1]) for n in spec['route']]
    if len(route) > 1:
        d = 'M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in route)
        svg += [f'<path d="{d}" fill="none" stroke="#009a44" stroke-width="10" stroke-opacity=".35" filter="url(#glow)" stroke-linejoin="round" stroke-linecap="round"/>',
                f'<path d="{d}" fill="none" stroke="#2bd47a" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>']
    stops = [n for n in dict.fromkeys(spec['route'])]
    def label(x, y, t, pos, big):
        fs = 15 if big else 12.5
        dx, dy, anc = {'r': (12, 5, 'start'), 'l': (-12, 5, 'end'), 't': (0, -12, 'middle'), 'b': (0, 22, 'middle')}[pos]
        st = f'font-family="Montserrat, Arial, sans-serif" font-size="{fs}" font-weight="{700 if big else 600}" text-anchor="{anc}"'
        return (f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" {st} fill="none" stroke="#0a0c0e" stroke-width="4" stroke-linejoin="round">{E(t)}</text>'
                f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" {st} fill="{"#f7f8f8" if big else "#c3c9d4"}">{E(t)}</text>')
    for name, lat, lon, kind, pos in pts:
        if kind != 'climb': continue
        x, y = P(lon, lat)
        svg.append(f'<path d="M{x:.1f},{y - 6:.1f}L{x + 5.5:.1f},{y + 4:.1f}L{x - 5.5:.1f},{y + 4:.1f}Z" fill="#c9a36a" stroke="#0a0c0e" stroke-width="1.5"/>')
        svg.append(label(x, y, name, pos, False))
    for name, lat, lon, kind, pos in pts:
        if kind == 'climb': continue
        x, y = P(lon, lat)
        if kind == 'base' or name not in stops:
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#009a44" fill-opacity=".25"/><circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#f7f8f8" stroke="#009a44" stroke-width="3"/>')
        else:
            n = stops.index(name) + 1
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="#e10600" stroke="#0a0c0e" stroke-width="2"/>'
                       f'<text x="{x:.1f}" y="{y + 4.5:.1f}" font-family="Montserrat, Arial, sans-serif" font-size="12.5" font-weight="700" fill="#fff" text-anchor="middle">{n}</text>')
        svg.append(label(x, y, name, pos, True))
    # legend
    items = []
    if any(p[3] == 'base' for p in pts): items.append(('base', 'Hotel base'))
    if len(spec['route']) > 1: items.append(('stop', 'Overnight stop' if not any(p[3] == 'base' for p in pts) else 'Route'))
    if any(p[3] == 'climb' for p in pts): items.append(('climb', 'Climbs & places'))
    x0 = 22
    svg.append(f'<rect x="12" y="{H - 46}" width="{24 + 170 * len(items)}" height="34" rx="8" fill="#0a0c0e" fill-opacity=".82" stroke="#ffffff" stroke-opacity=".12"/>')
    for kind, t in items:
        y = H - 29
        if kind == 'base': svg.append(f'<circle cx="{x0 + 8}" cy="{y}" r="6" fill="#f7f8f8" stroke="#009a44" stroke-width="3"/>')
        elif kind == 'stop': svg.append(f'<circle cx="{x0 + 8}" cy="{y}" r="7" fill="#e10600"/>')
        else: svg.append(f'<path d="M{x0 + 8},{y - 6}L{x0 + 13.5},{y + 4}L{x0 + 2.5},{y + 4}Z" fill="#c9a36a"/>')
        svg.append(f'<text x="{x0 + 22}" y="{y + 4.5}" font-family="Montserrat, Arial, sans-serif" font-size="12.5" font-weight="600" fill="#d0d6e0">{E(t)}</text>')
        x0 += 170
    svg.append('</svg>')
    return ''.join(svg)


# ---------- Custom tours: location ideas on a map of Europe (numbered dots, matched to the numbered list) ----------
LOCATIONS = [   # same order and words as the live list on /trips/private-trips/ (Patagonia left out: Europe map, Matteo 15 Nov)
 ('Italian Northern Lakes (Garda, Como, Iseo, Maggiore), Italy', 45.85, 9.75), ('Tuscany, Italy', 43.35, 11.2), ('Italian Alps & Dolomites, Italy', 46.5, 11.4),
 ('Piedmont, Italy', 44.75, 7.9), ('Puglia, Italy', 40.85, 17.0), ('Sardinia, Italy', 40.1, 9.0), ('Sicily, Italy', 37.5, 14.2),
 ("Italy's Coast to Coast, Italy", 43.15, 12.6), ('French Alps, France', 45.05, 6.45), ('Pyrenees, France', 42.9, 0.9), ('Brittany, France', 48.2, -3.0),
 ('The Algarve, Portugal', 37.15, -8.1), ('N2 Road, Porto to Faro, Portugal', 39.6, -7.95), ('Alentejo, Portugal', 38.4, -7.6),
 ('Canary Islands (Tenerife, Gran Canaria, Lanzarote), Spain', 28.3, -15.6), ('Baleares Islands (Mallorca, Minorca, Ibiza, Formentera), Spain', 39.6, 2.9),
 ('Calpe & Denia, Spain', 38.7, 0.0), ('Girona, Spain', 41.98, 2.82), ('Basque Country, Spain', 43.1, -2.4), ('Spanish Pyrenees, Spain', 42.45, -0.5),
 ('Croatia', 43.6, 16.2), ('Slovenia', 46.1, 14.8), ('Cyprus', 35.0, 33.0), ('Turkey', 38.6, 29.5), ('Greek Islands', 37.1, 25.3),
 ('Albania', 41.1, 20.0), ('Morocco', 31.7, -7.2), ('Flanders, Belgium', 50.9, 3.6),
 ('Ireland', 53.0, -8.0), ('Provence, France', 43.95, 5.4), ('Switzerland', 46.7, 8.2)]   # added by Matteo 15 Nov

def draw_locations(countries, lakes):
    W2, H2 = 1000, 700
    lon0, lon1, lat0, lat1 = -19.0, 36.0, 26.5, 55.5
    k0 = math.cos(math.radians((lat0 + lat1) / 2))
    s = min(W2 / ((lon1 - lon0) * k0), H2 / (lat1 - lat0))
    ox = (W2 - (lon1 - lon0) * k0 * s) / 2; oy = (H2 - (lat1 - lat0) * s) / 2
    P = lambda lon, lat: (ox + (lon - lon0) * k0 * s, oy + (lat1 - lat) * s)
    def clip(poly, x0, y0, x1, y1):   # Sutherland-Hodgman against the frame
        for edge in range(4):
            out, n = [], len(poly)
            if not n: break
            inside = [lambda p: p[0] >= x0, lambda p: p[0] <= x1, lambda p: p[1] >= y0, lambda p: p[1] <= y1][edge]
            def cut(a, b):
                if edge < 2:
                    xc = x0 if edge == 0 else x1; t = (xc - a[0]) / (b[0] - a[0]); return (xc, a[1] + t * (b[1] - a[1]))
                yc = y0 if edge == 2 else y1; t = (yc - a[1]) / (b[1] - a[1]); return (a[0] + t * (b[0] - a[0]), yc)
            for i in range(n):
                a, b = poly[i - 1], poly[i]
                if inside(b):
                    if not inside(a): out.append(cut(a, b))
                    out.append(b)
                elif inside(a): out.append(cut(a, b))
            poly = out
        return poly
    d = []
    for r in countries:
        if not any(lon0 - 2 <= x <= lon1 + 2 and lat0 - 2 <= y <= lat1 + 2 for x, y in r): continue
        pts, last = [], None
        for X, Y in clip([P(x, y) for x, y in r], -2, -2, W2 + 2, H2 + 2):
            if last and abs(X - last[0]) < 1.6 and abs(Y - last[1]) < 1.6: continue
            pts.append(f'{X:.1f},{Y:.1f}'); last = (X, Y)
        if len(pts) > 2: d.append('M' + 'L'.join(pts) + 'Z')
    E = lambda x: html.escape(x, quote=True)
    out = [f'<svg class="lmap" viewBox="0 0 {W2} {H2}" role="img" aria-label="Map of our custom tour location ideas across Europe" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="{W2}" height="{H2}" fill="#0a0c0e"/>', f'<path d="{"".join(d)}" fill="#1b1e22" stroke="#3a3f46" stroke-width=".8"/>']
    for n, (name, lat, lon) in enumerate(LOCATIONS, 1):
        x, y = P(lon, lat)
        out.append(f'<g><title>{E(name)}</title><circle cx="{x:.1f}" cy="{y:.1f}" r="11.5" fill="#e10600" stroke="#0a0c0e" stroke-width="2"/>'
                   f'<text x="{x:.1f}" y="{y + 4.2:.1f}" font-family="Montserrat, Arial, sans-serif" font-size="11.5" font-weight="700" fill="#fff" text-anchor="middle">{n}</text></g>')
    out.append('</svg>')
    return ''.join(out)


# ---------- destination pages: the country, in our style, with the region(s) marked (Matteo 15 Nov) ----------
CB = {'Italy': (6.4, 18.7, 36.5, 47.2), 'France': (-5.3, 9.8, 41.2, 51.2), 'Spain': (-9.5, 4.5, 35.8, 44.0),
      'Canary Islands': (-18.3, -13.3, 27.5, 29.5), 'Portugal': (-9.7, -6.0, 36.8, 42.3), 'Croatia': (13.3, 19.6, 42.2, 46.7),
      'Slovenia': (13.2, 16.8, 45.3, 47.0), 'Greece': (19.2, 28.4, 34.6, 41.9), 'Switzerland': (5.8, 10.6, 45.7, 47.9),
      'Ireland': (-10.8, -5.8, 51.2, 55.6), 'Cyprus': (32.1, 34.7, 34.4, 35.8)}
CN = {'Canary Islands': ['Spain'], 'Cyprus': ['Cyprus', 'N. Cyprus']}
REGIONS = {   # destination slug: (country map, lat, lon, label)
 'tuscany': ('Italy', 43.35, 11.2, 'Tuscany'), 'lake-garda': ('Italy', 45.65, 10.65, 'Lake Garda'), 'alps-dolomites': ('Italy', 46.45, 11.6, 'Alps & Dolomites'),
 'lake-como': ('Italy', 45.98, 9.25, 'Lake Como'), 'sardinia': ('Italy', 40.1, 9.0, 'Sardinia'), 'sicily': ('Italy', 37.5, 14.2, 'Sicily'),
 'puglia': ('Italy', 40.85, 17.0, 'Puglia'), 'french-alps': ('France', 45.05, 6.45, 'French Alps'), 'pyrenees': ('France', 42.9, 0.9, 'Pyrenees'),
 'corsica': ('France', 42.15, 9.1, 'Corsica'), 'algarve': ('Portugal', 37.15, -8.1, 'Algarve'), 'girona': ('Spain', 41.98, 2.82, 'Girona'),
 'mallorca': ('Spain', 39.6, 2.9, 'Mallorca'), 'costa-blanca': ('Spain', 38.65, -0.05, 'Costa Blanca'),
 'gran-canaria': ('Canary Islands', 27.95, -15.6, 'Gran Canaria'), 'tenerife': ('Canary Islands', 28.27, -16.6, 'Tenerife')}
COUNTRY_PAGES = {'italy': 'Italy', 'france': 'France', 'spain': 'Spain', 'portugal': 'Portugal', 'croatia': 'Croatia', 'slovenia': 'Slovenia',
                 'greece': 'Greece', 'switzerland': 'Switzerland', 'ireland': 'Ireland', 'cyprus': 'Cyprus'}

def topo_named(path):
    """{country name: [rings]} from the world-atlas TopoJSON."""
    t = json.load(open(path)); sc, tr = t['transform']['scale'], t['transform']['translate']
    arcs = []
    for a in t['arcs']:
        x = y = 0; pts = []
        for dx, dy in a:
            x += dx; y += dy; pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
        arcs.append(pts)
    def ring(idx):
        out = []
        for i in idx:
            pts = arcs[i] if i >= 0 else arcs[~i][::-1]
            out += pts if not out else pts[1:]
        return out
    out = {}
    for g in t['objects']['countries']['geometries']:
        rs = [ring(r) for r in g['arcs']] if g['type'] == 'Polygon' else [ring(r) for p in g.get('arcs', []) for r in p] if g['type'] == 'MultiPolygon' else []
        out.setdefault(g['properties']['name'], []).extend(rs)
    return out

def draw_country(map_name, dots, named):
    W2, H2 = 640, 640
    lon0, lon1, lat0, lat1 = CB[map_name]
    k0 = math.cos(math.radians((lat0 + lat1) / 2))
    s = min(W2 * .9 / ((lon1 - lon0) * k0), H2 * .9 / (lat1 - lat0))
    ox = (W2 - (lon1 - lon0) * k0 * s) / 2; oy = (H2 - (lat1 - lat0) * s) / 2
    P = lambda lon, lat: (ox + (lon - lon0) * k0 * s, oy + (lat1 - lat) * s)
    mine = set(CN.get(map_name, [map_name]))
    def d_of(rings):
        out = []
        for r in rings:
            if not any(lon0 - 3 <= x <= lon1 + 3 and lat0 - 3 <= y <= lat1 + 3 for x, y in r): continue
            pts, last = [], None
            for x, y in r:
                X, Y = P(x, y)
                if last and abs(X - last[0]) < 1.4 and abs(Y - last[1]) < 1.4: continue
                pts.append(f'{X:.1f},{Y:.1f}'); last = (X, Y)
            if len(pts) > 2: out.append('M' + 'L'.join(pts) + 'Z')
        return ''.join(out)
    others = d_of([r for n, rs in named.items() if n not in mine for r in rs])
    me = d_of([r for n in mine for r in named.get(n, [])])
    E = lambda x: html.escape(x, quote=True)
    out = [f'<svg class="cmap" viewBox="0 0 {W2} {H2}" role="img" aria-label="Map of {E(map_name)}{" showing " + E(", ".join(d[2] for d in dots)) if dots else ""}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="{W2}" height="{H2}" fill="#0a0c0e"/>',
           f'<path d="{others}" fill="#16191d" stroke="#2c3036" stroke-width=".8"/>',
           f'<path d="{me}" fill="#009a44" fill-opacity=".16" stroke="#2bd47a" stroke-width="2" stroke-linejoin="round"/>']
    for lat, lon, label in dots:
        x, y = P(lon, lat)
        right = x < W2 * .62
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="#e10600" fill-opacity=".22"/><circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#e10600" stroke="#fff" stroke-width="2"/>')
        tx = x + 14 if right else x - 14; anc = 'start' if right else 'end'
        st = f'font-family="Montserrat, Arial, sans-serif" font-size="17" font-weight="700" text-anchor="{anc}"'
        out.append(f'<text x="{tx:.1f}" y="{y + 6:.1f}" {st} fill="none" stroke="#0a0c0e" stroke-width="5" stroke-linejoin="round">{E(label)}</text>'
                   f'<text x="{tx:.1f}" y="{y + 6:.1f}" {st} fill="#f7f8f8">{E(label)}</text>')
    out.append('</svg>')
    return ''.join(out)

def country_maps(path50):
    named = topo_named(path50)
    for slug, (cm, lat, lon, label) in REGIONS.items():
        open(OUT + f'country-{slug}.svg', 'w').write(draw_country(cm, [(lat, lon, label)], named))
    for slug, cm in COUNTRY_PAGES.items():
        dots = [(la, lo, lb) for s2, (c2, la, lo, lb) in REGIONS.items() if c2 == cm or (cm == 'Spain' and c2 == 'Canary Islands' and False)]
        open(OUT + f'country-{slug}.svg', 'w').write(draw_country(cm, dots, named))

if __name__ == '__main__':
    f = geo_files()
    countries, lakes, rivers = topo_polys(f['countries']), geojson_polys(f['lakes']), geojson_lines(f['rivers'])
    os.makedirs(OUT, exist_ok=True)
    for slug, spec in ROUTES.items():
        out = draw(slug, spec, countries, lakes, rivers)
        open(OUT + slug + '.svg', 'w').write(out)
        print(slug, len(out) // 1024, 'KB')
    open(OUT + 'custom-locations.svg', 'w').write(draw_locations(topo_polys(f['countries'].replace('-10m', '-50m')), lakes))   # 1:50m is plenty at this scale
    print('custom-locations', os.path.getsize(OUT + 'custom-locations.svg') // 1024, 'KB')
    country_maps(f['countries'].replace('-10m', '-50m'))
    print('country maps', len([x for x in os.listdir(OUT) if x.startswith('country-')]))
