"""Day-by-day route maps for the 15 Tours trips (Matteo 16 Nov: "we have to see the actual route, where we go each day").

Each day of the itinerary is routed on real roads with BRouter (brouter.de, OpenStreetMap data): the road profile
for road tours, the gravel profile for gravel tours. Waypoints (start, climbs and villages named in the day's text,
finish) are typed in DAYS below with approximate coordinates in G; the router snaps them to the road network.
Tracks are cached in tours/routes/<slug>.json (in the repository), so the maps rebuild without the network.

Drawn on the same dark terrain as tours_route_maps.py: each day in its own colour with a numbered badge, the hotels
and overnight towns in white, a few named climbs. build_tours_trips.py inlines tourspages/maps/<slug>.svg and adds
the day list under the map (hovering a day highlights its route).

    python3 -I tools/tours_day_routes.py [slug ...]        (GEO=<folder with the Natural Earth data>, as tours_route_maps.py)
    REFETCH=1 to ask the router again (after changing waypoints, only the changed days are fetched).
"""
import os, sys, json, math, time, html, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tours_route_maps as trm

ROOT = trm.ROOT
CACHE = ROOT + 'tours/routes/'
OUT = trm.OUT
W, H = 900, 640
COLORS = ['#2bd47a', '#b6f36a', '#5ad6d0', '#f7f8f8', '#8fe8b6', '#e3f28a', '#1fae63']   # a family of greens, as our country maps (Matteo 16 Nov): green, lime, teal, white, mint, pale lime, emerald
COUNTRY = {t['slug']: t['country'] for t in json.load(open(ROOT + 'tours/trips-2027.json'))['trips']}

G = {   # (lat, lon), approximate: town centres, pass summits
 # Dolomites
 'La Villa': (46.586, 11.900), 'Corvara': (46.551, 11.873), 'Campolongo': (46.519, 11.874), 'Arabba': (46.497, 11.875), 'Pordoi': (46.487, 11.811),
 'Sella': (46.509, 11.762), 'Gardena': (46.549, 11.809), 'Valparola': (46.531, 11.989), 'Falzarego': (46.519, 12.008), 'Pieve di Livinallongo': (46.489, 11.945),
 'Colle Santa Lucia': (46.447, 12.012), 'Selva di Cadore': (46.448, 12.034), 'Giau': (46.483, 12.054), 'Pocol': (46.528, 12.106), 'San Cassiano': (46.570, 11.933),
 'Pedraces': (46.613, 11.889), 'San Martino in Badia': (46.680, 11.898), 'Cortina': (46.540, 12.136), 'Tre Croci': (46.556, 12.204), 'Misurina': (46.582, 12.253),
 'Rifugio Auronzo': (46.612, 12.296), 'Canazei': (46.476, 11.770), 'Moena': (46.377, 11.660), 'San Pellegrino': (46.380, 11.787), 'Falcade': (46.356, 11.871),
 'Cencenighe': (46.352, 11.968), 'Caprile': (46.441, 11.990), 'Malga Ciapela': (46.428, 11.909), 'Fedaia': (46.459, 11.869), 'Pozza di Fassa': (46.429, 11.689),
 # French Alps
 'Saint-Jean-de-Maurienne': (45.277, 6.346), 'Montvernier': (45.319, 6.343), 'Pontamafrey': (45.316, 6.326), 'La Chambre': (45.360, 6.300),
 'Col de la Madeleine': (45.435, 6.373), 'Saint-Etienne-de-Cuines': (45.346, 6.288), 'Col du Glandon': (45.239, 6.177), 'Croix de Fer': (45.227, 6.203),
 "Saint-Sorlin-d'Arves": (45.221, 6.233), 'Saint-Michel-de-Maurienne': (45.217, 6.471), 'Col du Telegraphe': (45.203, 6.444), 'Valloire': (45.165, 6.430),
 'Col du Galibier': (45.064, 6.408), 'Col du Lautaret': (45.035, 6.404), 'Monetier-les-Bains': (44.976, 6.508), "Bourg-d'Oisans": (45.055, 6.031),
 "Alpe d'Huez": (45.092, 6.070), 'Briancon': (44.899, 6.643), "Col d'Izoard": (44.820, 6.735), 'Guillestre': (44.660, 6.649), 'Col de Vars': (44.539, 6.703),
 'Barcelonnette': (44.387, 6.652), 'Jausiers': (44.417, 6.731), 'Cime de la Bonette': (44.321, 6.807),
 # Slovenia
 'Nova Gorica': (45.956, 13.648), 'Ajdovscina': (45.888, 13.910), 'Postojna': (45.776, 14.213), 'Logatec': (45.917, 14.225), 'Ziri': (46.047, 14.108),
 'Skofja Loka': (46.166, 14.306), 'Zelezniki': (46.224, 14.168), 'Sorica': (46.218, 14.033), 'Bohinj': (46.277, 13.886), 'Bled': (46.369, 14.114),
 'Kranjska Gora': (46.485, 13.786), 'Vrsic': (46.433, 13.743), 'Trenta': (46.379, 13.752), 'Bovec': (46.338, 13.552), 'Kobarid': (46.247, 13.579),
 'Tolmin': (46.183, 13.733), 'Kanal': (46.086, 13.637),
 # Lake Garda
 'Moniga del Garda': (45.528, 10.540), 'San Felice del Benaco': (45.585, 10.553), 'Manerba del Garda': (45.550, 10.552), 'Puegnago del Garda': (45.567, 10.507),
 'Padenghe': (45.506, 10.507), 'Lonato': (45.461, 10.483), 'Castiglione delle Stiviere': (45.389, 10.488), 'Solferino': (45.372, 10.566), 'Cavriana': (45.349, 10.603),
 'Pozzolengo': (45.405, 10.631), 'Desenzano': (45.469, 10.536), 'Rivoltella': (45.462, 10.582), 'Peschiera': (45.439, 10.692), 'Borghetto sul Mincio': (45.355, 10.744), 'Valeggio sul Mincio': (45.352, 10.735),
 "Sant'Ambrogio di Valpolicella": (45.522, 10.833), 'Fumane': (45.543, 10.882), 'Negrar': (45.529, 10.937), "Sant'Anna d'Alfaedo": (45.627, 10.952),
 'Polpenazze': (45.551, 10.505), 'Soiano del Lago': (45.527, 10.510), 'Salo': (45.607, 10.522), 'Sirmione': (45.493, 10.608), 'Gargnano': (45.688, 10.663),
 'Porto di Tremosine': (45.757, 10.763), 'Pieve di Tremosine': (45.772, 10.755), 'Vesio': (45.796, 10.722), 'Tignale': (45.738, 10.718), 'Limone': (45.813, 10.792),
 'Riva del Garda': (45.885, 10.841), 'Torbole': (45.871, 10.874), 'Malcesine': (45.764, 10.809), 'Garda': (45.575, 10.707), 'Gardone Riviera': (45.620, 10.562),
 # Bormio
 'Bormio': (46.468, 10.370), 'Stelvio': (46.529, 10.453), 'Umbrail': (46.542, 10.434), 'Santa Maria Val Mustair': (46.600, 10.425), 'Prato allo Stelvio': (46.619, 10.592),
 'Glurns': (46.671, 10.555), 'San Giacomo di Fraele': (46.520, 10.284), 'Lago di Cancano': (46.533, 10.288), 'Passo Alpisella': (46.552, 10.193),
 'Livigno': (46.538, 10.135), 'Foscagno': (46.495, 10.217), 'Isolaccia': (46.488, 10.287), 'Arnoga': (46.464, 10.240), 'Rifugio Val Viola': (46.428, 10.180),
 'Grosio': (46.297, 10.276), 'Fusino': (46.322, 10.226), 'Eita': (46.364, 10.198), 'Mazzo': (46.256, 10.257), 'Mortirolo': (46.247, 10.293),
 'Monno': (46.213, 10.340), 'Santa Caterina': (46.412, 10.494), 'Gavia': (46.344, 10.488), 'Ponte di Legno': (46.258, 10.510), 'Torri di Fraele': (46.528, 10.300),
 # Tuscany / Italy
 'Castagneto Carducci': (43.160, 10.610), 'Bolgheri': (43.236, 10.615), 'Lajatico': (43.474, 10.729), 'Peccioli': (43.548, 10.719), 'Castel San Gimignano': (43.434, 10.986), 'Volterra east': (43.4045, 10.8935), 'Ghizzano': (43.575, 10.784), 'Villamagna': (43.483, 10.858), 'Volterra': (43.402, 10.861),
 'San Gimignano': (43.467, 11.043), "Colle di Val d'Elsa": (43.421, 11.126), 'Monteriggioni': (43.390, 11.223), 'Siena': (43.318, 11.331), 'Buonconvento': (43.134, 11.484),
 "Lucignano d'Asso": (43.148, 11.590), 'Pienza': (43.077, 11.679), "Castiglione d'Orcia": (43.004, 11.615), 'Paganico': (42.950, 11.287), 'Grosseto': (42.763, 11.113),
 'Marina di Grosseto': (42.718, 10.981), 'Castiglione della Pescaia': (42.764, 10.881), 'Follonica': (42.926, 10.761), 'Suvereto': (43.077, 10.676),
 'Radda in Chianti': (43.486, 11.374), 'Gaiole in Chianti': (43.467, 11.435), 'Monteaperti': (43.364, 11.410), 'Colle Pinzuto': (43.338, 11.392), 'Tolfe': (43.346, 11.357),
 'Castelnuovo Berardenga': (43.346, 11.503), 'Panzano': (43.545, 11.313), 'Greve in Chianti': (43.584, 11.317), 'Lamole': (43.547, 11.354), 'Volpaia': (43.512, 11.393), 'Castellina in Chianti': (43.471, 11.287),
 'Vescovado di Murlo': (43.170, 11.388), 'Montalcino': (43.058, 11.489), "San Giovanni d'Asso": (43.153, 11.590), 'Asciano': (43.234, 11.561),
 'Viareggio': (43.872, 10.250), 'Pisa': (43.723, 10.396), 'Montepulciano': (43.093, 11.781), 'Castiglione del Lago': (43.127, 12.051), 'Magione': (43.141, 12.205),
 'Assisi': (43.071, 12.617), 'Foligno': (42.956, 12.703), 'Colfiorito': (43.026, 12.890), 'Camerino': (43.135, 13.068), 'Sarnano': (43.034, 13.300),
 'Amandola': (42.980, 13.355), 'Ripatransone': (43.000, 13.762), 'San Benedetto del Tronto': (42.948, 13.881),
 # Cyprus
 'Paphos': (34.776, 32.424), 'Kelokedara': (34.808, 32.586), 'Omodos': (34.849, 32.809), 'Lofou': (34.810, 32.888), 'Pelendri': (34.892, 32.968), 'Agros': (34.917, 33.016),
 'Mount Olympus': (34.936, 32.864), 'Prodromos': (34.950, 32.833), 'Kalopanagiotis': (34.993, 32.830), 'Kykkos': (35.046, 32.741), 'Stavros tis Psokas': (35.026, 32.633),
 'Polis': (35.035, 32.426), 'Drouseia': (34.958, 32.399), 'Kathikas': (34.893, 32.432), 'Neo Chorio': (35.018, 32.351), 'Agios Georgios Pegeias': (34.896, 32.326),
 'Coral Bay': (34.856, 32.364),
 # Flanders
 'Waregem': (50.888, 3.426), 'Oude Kwaremont': (50.784, 3.531), 'Paterberg': (50.781, 3.573), 'Oudenaarde': (50.845, 3.605), 'Koppenberg': (50.816, 3.600),
 'Muur van Geraardsbergen': (50.773, 3.882), 'Bosberg': (50.761, 3.900),
 # Algarve
 'Quinta do Lago': (37.028, -8.018), 'Sao Bras de Alportel': (37.152, -7.888), 'Loule': (37.138, -8.020), 'Alto do Malhao': (37.214, -7.940), 'Salir': (37.240, -8.050),
 'Alte': (37.236, -8.174), 'Boliqueime': (37.135, -8.162), 'Querenca': (37.198, -7.989), 'Barranco do Velho': (37.234, -7.937), 'Tavira': (37.127, -7.649),
 'Olhao': (37.026, -7.841), 'Sao Bartolomeu de Messines': (37.258, -8.287), 'Silves': (37.189, -8.438), 'Lagos': (37.102, -8.673), 'Monchique': (37.318, -8.556), 'Santa Catarina da Fonte do Bispo': (37.150, -7.780), 'Faro': (37.019, -7.931), 'Almancil': (37.084, -8.032), 'Vale do Lobo': (37.054, -8.069),
 # Lake Como
 'Como': (45.808, 9.085), 'Civiglio': (45.826, 9.110), 'Brunate': (45.818, 9.098), 'Erba': (45.811, 9.226), 'Canzo': (45.848, 9.272), 'Sormano': (45.878, 9.247),
 'Colma di Sormano': (45.893, 9.231), 'Nesso': (45.913, 9.159), 'Bellagio': (45.987, 9.262), 'Ghisallo': (45.923, 9.268), 'Asso': (45.861, 9.270),
 'Varenna': (46.010, 9.284), 'Lecco': (45.853, 9.390), 'Cernobbio': (45.842, 9.073), 'Menaggio': (46.021, 9.238), 'Gravedona': (46.145, 9.307),
 'Colico': (46.134, 9.371), 'Onno': (45.926, 9.348), 'Bergamo': (45.698, 9.677), 'Almenno San Salvatore': (45.750, 9.590),
 "Sant'Omobono Terme": (45.806, 9.536), 'Costa Valle Imagna': (45.832, 9.497), 'Brembilla': (45.818, 9.596), 'Zogno': (45.794, 9.664), 'Selvino': (45.781, 9.751), 'Nembro': (45.744, 9.759),
}

R, GR = 'fastbike', 'gravel'
# slug: (profile, {itinerary day number: [waypoints]}, overnight towns / hotels, climbs to name)
DAYS = {
 'maratona-dles-dolomites': (R, {
    1: ['La Villa', 'Valparola', 'La Villa'],
    2: ['La Villa', 'Corvara', 'Campolongo', 'Arabba', 'Pordoi', 'Sella', 'Gardena', 'Corvara', 'La Villa'],
    3: ['La Villa', 'Corvara', 'Gardena', 'Corvara', 'Campolongo', 'Corvara', 'La Villa'],
    4: ['La Villa', 'Pedraces', 'San Martino in Badia', 'La Villa'],
    5: ['Corvara', 'Campolongo', 'Pordoi', 'Sella', 'Gardena', 'Corvara', 'Campolongo', 'Arabba', 'Pieve di Livinallongo', 'Selva di Cadore', 'Giau',
        'Falzarego', 'Valparola', 'San Cassiano', 'Corvara']},   # no Pocol waypoint: it sat off the road and drew an out-and-back (Matteo 16 Nov)
    ['La Villa'], ['Campolongo', 'Pordoi', 'Sella', 'Gardena', 'Giau', 'Falzarego', 'Valparola']),
 'dolomites': (R, {
    2: ['La Villa', 'San Cassiano', 'Valparola', 'Falzarego', 'Pieve di Livinallongo', 'Arabba', 'Pordoi', 'Sella', 'Gardena', 'Corvara', 'La Villa'],
    3: ['La Villa', 'Corvara', 'Campolongo', 'Arabba', 'Pieve di Livinallongo', 'Colle Santa Lucia', 'Selva di Cadore', 'Giau', 'Pocol', 'Falzarego', 'Valparola', 'La Villa'],
    4: ['Cortina', 'Tre Croci', 'Misurina', 'Rifugio Auronzo', 'Misurina', 'Tre Croci', 'Cortina'],
    5: ['Canazei', 'Moena', 'San Pellegrino', 'Falcade', 'Cencenighe', 'Caprile', 'Malga Ciapela', 'Fedaia', 'Canazei'],
    6: ['Canazei', 'Pozza di Fassa', 'Canazei']},
    ['La Villa', 'Canazei', 'Cortina'], ['Pordoi', 'Sella', 'Gardena', 'Giau', 'Falzarego', 'Tre Croci', 'Rifugio Auronzo', 'San Pellegrino', 'Fedaia']),
 'french-alps': (R, {
    2: ['Saint-Jean-de-Maurienne', 'Pontamafrey', 'Montvernier', 'La Chambre', 'Col de la Madeleine', 'La Chambre', 'Saint-Jean-de-Maurienne'],
    3: ['Saint-Jean-de-Maurienne', 'Saint-Etienne-de-Cuines', 'Col du Glandon', 'Croix de Fer', "Saint-Sorlin-d'Arves", 'Saint-Jean-de-Maurienne'],
    4: ['Saint-Jean-de-Maurienne', 'Saint-Michel-de-Maurienne', 'Col du Telegraphe', 'Valloire', 'Col du Galibier', 'Col du Lautaret', 'Monetier-les-Bains'],
    5: ["Bourg-d'Oisans", "Alpe d'Huez", "Bourg-d'Oisans"],
    6: ['Monetier-les-Bains', 'Briancon', "Col d'Izoard", 'Guillestre', 'Col de Vars', 'Barcelonnette'],
    7: ['Barcelonnette', 'Jausiers', 'Cime de la Bonette', 'Jausiers', 'Barcelonnette']},
    ['Saint-Jean-de-Maurienne', 'Monetier-les-Bains', 'Barcelonnette'],
    ['Col de la Madeleine', 'Col du Glandon', 'Col du Galibier', "Alpe d'Huez", "Col d'Izoard", 'Col de Vars', 'Cime de la Bonette']),
 'wonderful-slovenia': (R, {
    2: ['Nova Gorica', 'Ajdovscina', 'Postojna'],
    3: ['Postojna', 'Logatec', 'Ziri', 'Skofja Loka'],
    4: ['Skofja Loka', 'Zelezniki', 'Sorica', 'Bohinj', 'Bled'],
    5: ['Bled', 'Kranjska Gora', 'Vrsic', 'Trenta', 'Bovec'],
    6: ['Bovec', 'Kobarid', 'Tolmin', 'Kanal', 'Nova Gorica']},
    ['Nova Gorica', 'Postojna', 'Skofja Loka', 'Bled', 'Bovec'], ['Vrsic']),
 'lake-garda-gravel': (GR, {
    1: ['Moniga del Garda', 'San Felice del Benaco', 'Manerba del Garda', 'Puegnago del Garda', 'Moniga del Garda'],
    2: ['Moniga del Garda', 'Padenghe', 'Lonato', 'Castiglione delle Stiviere', 'Solferino', 'Cavriana', 'Pozzolengo', 'Desenzano', 'Moniga del Garda'],
    3: ['Moniga del Garda', 'Desenzano', 'Peschiera', 'Borghetto sul Mincio', 'Valeggio sul Mincio', 'Pozzolengo', 'Moniga del Garda'],
    4: ["Sant'Ambrogio di Valpolicella", 'Fumane', "Sant'Anna d'Alfaedo", 'Negrar', "Sant'Ambrogio di Valpolicella"],
    5: ['Moniga del Garda', 'Polpenazze', 'Puegnago del Garda', 'Salo', 'Soiano del Lago', 'Moniga del Garda'],
    6: ['Moniga del Garda', 'Desenzano', 'Sirmione', 'Rivoltella', 'Padenghe', 'Moniga del Garda']},   # by road (the router took the ferry back)
    ['Moniga del Garda'], ['Solferino', 'Borghetto sul Mincio', 'Sirmione', 'Negrar']),
 'lake-garda-and-stelvio': (R, {
    1: ['Moniga del Garda', 'Desenzano', 'Sirmione', 'Moniga del Garda'],
    2: ['Moniga del Garda', 'Salo', 'Gargnano', 'Porto di Tremosine', 'Pieve di Tremosine', 'Tignale', 'Gargnano', 'Salo', 'Moniga del Garda'],
    3: ['Prato allo Stelvio', 'Stelvio', 'Prato allo Stelvio'],   # the Stelvio day trip by van: drawn in a corner inset (INSET)
    4: ['Moniga del Garda', 'Lonato', 'Castiglione delle Stiviere', 'Solferino', 'Pozzolengo', 'Desenzano', 'Moniga del Garda'],
    5: ['Moniga del Garda', 'Salo', 'Gargnano', 'Limone', 'Riva del Garda', 'Torbole', 'Malcesine', 'Garda', 'Peschiera', 'Desenzano', 'Moniga del Garda'],
    6: ['Moniga del Garda', 'Salo', 'Gardone Riviera', 'Salo', 'Moniga del Garda']},
    ['Moniga del Garda'], ['Pieve di Tremosine', 'Riva del Garda', 'Malcesine', 'Sirmione']),
 'alpine-gravel-escape': (GR, {
    2: ['Bormio', 'Stelvio', 'Bormio'],
    3: ['Bormio', 'Torri di Fraele', 'Lago di Cancano', 'Passo Alpisella', 'Livigno', 'Foscagno', 'Bormio'],
    4: ['Bormio', 'Isolaccia', 'Arnoga', 'Rifugio Val Viola', 'Arnoga', 'Bormio'],
    5: ['Bormio', 'Grosio', 'Fusino', 'Eita', 'Fusino', 'Grosio', 'Bormio'],
    6: ['Bormio', 'Torri di Fraele', 'Lago di Cancano', 'Bormio']},
    ['Bormio'], ['Stelvio', 'Passo Alpisella', 'Livigno', 'Rifugio Val Viola', 'Eita', 'Lago di Cancano']),
 'italian-alps': (R, {
    2: ['Bormio', 'Umbrail', 'Santa Maria Val Mustair', 'Glurns', 'Prato allo Stelvio', 'Stelvio', 'Bormio'],
    3: ['Bormio', 'Grosio', 'Mazzo', 'Mortirolo', 'Mazzo', 'Bormio'],
    4: ['Bormio', 'Foscagno', 'Livigno', 'Foscagno', 'Bormio'],
    5: ['Bormio', 'Santa Caterina', 'Gavia', 'Ponte di Legno', 'Monno', 'Mortirolo', 'Mazzo', 'Bormio'],
    6: ['Bormio', 'Torri di Fraele', 'Bormio']},
    ['Bormio'], ['Stelvio', 'Umbrail', 'Mortirolo', 'Foscagno', 'Livigno', 'Gavia', 'Torri di Fraele']),
 'tuscany-epic-gravel': (GR, {
    2: ['Castagneto Carducci', 'Bolgheri', 'Lajatico', 'Peccioli'],
    3: ['Peccioli', 'Ghizzano', 'Villamagna', 'Volterra', 'Volterra east', 'Castel San Gimignano', 'San Gimignano', "Colle di Val d'Elsa"],   # through Volterra and out east (Matteo 16 Nov: no out-and-back)   # leave Peccioli eastwards: no out-and-back on the Lajatico road (Matteo 16 Nov)
    4: ["Colle di Val d'Elsa", 'Monteriggioni', 'Siena', 'Buonconvento', "Lucignano d'Asso", 'Pienza'],
    5: ['Pienza', "Castiglione d'Orcia", 'Paganico', 'Grosseto', 'Marina di Grosseto'],
    6: ['Marina di Grosseto', 'Castiglione della Pescaia', 'Follonica', 'Suvereto', 'Castagneto Carducci']},
    ['Castagneto Carducci', 'Peccioli', "Colle di Val d'Elsa", 'Pienza', 'Marina di Grosseto'], ['Bolgheri', 'Volterra', 'San Gimignano', 'Siena']),
 'cyprus-crossing-gravel': (GR, {
    2: ['Paphos', 'Kelokedara', 'Omodos', 'Lofou'],
    3: ['Lofou', 'Pelendri', 'Agros'],
    4: ['Agros', 'Mount Olympus', 'Prodromos', 'Kalopanagiotis'],
    5: ['Kalopanagiotis', 'Kykkos', 'Stavros tis Psokas', 'Polis'],
    6: ['Polis', 'Drouseia', 'Kathikas', 'Polis'],
    7: ['Polis', 'Neo Chorio', 'Agios Georgios Pegeias', 'Coral Bay', 'Paphos']},
    ['Paphos', 'Lofou', 'Agros', 'Kalopanagiotis', 'Polis'], ['Mount Olympus', 'Kykkos']),
 'tour-of-flanders-experience': (R, {
    1: ['Waregem', 'Oude Kwaremont', 'Paterberg', 'Oudenaarde', 'Waregem'],
    2: ['Waregem', 'Oudenaarde', 'Koppenberg', 'Paterberg', 'Waregem'],
    3: ['Oudenaarde', 'Muur van Geraardsbergen', 'Bosberg', 'Oude Kwaremont', 'Paterberg', 'Oudenaarde']},
    ['Waregem'], ['Oude Kwaremont', 'Paterberg', 'Koppenberg', 'Muur van Geraardsbergen']),
 'chianti-gran-fondo-strade-bianche': (R, {
    1: ['Radda in Chianti', 'Gaiole in Chianti', 'Radda in Chianti'],
    2: ['Radda in Chianti', 'Castelnuovo Berardenga', 'Monteaperti', 'Colle Pinzuto', 'Tolfe', 'Siena', 'Castellina in Chianti', 'Radda in Chianti'],
    3: ['Radda in Chianti', 'Castellina in Chianti', 'Panzano', 'Greve in Chianti', 'Lamole', 'Volpaia', 'Radda in Chianti'],   # a loop back to Radda (Matteo 16 Nov)
    4: ['Radda in Chianti', 'Castellina in Chianti', 'Radda in Chianti'],
    5: ['Siena', 'Vescovado di Murlo', 'Montalcino', "San Giovanni d'Asso", 'Asciano', 'Monteaperti', 'Colle Pinzuto', 'Tolfe', 'Siena']},
    ['Radda in Chianti', 'Siena'], ['Gaiole in Chianti', 'Monteaperti', 'Montalcino', 'Greve in Chianti', 'Castellina in Chianti']),
 'discover-the-algarve-granfondo': (R, {
    1: ['Quinta do Lago', 'Loule', 'Sao Bras de Alportel', 'Faro', 'Quinta do Lago'],
    2: ['Quinta do Lago', 'Loule', 'Alto do Malhao', 'Salir', 'Alte', 'Boliqueime', 'Quinta do Lago'],
    3: ['Quinta do Lago', 'Loule', 'Querenca', 'Loule', 'Quinta do Lago'],
    4: ['Loule', 'Salir', 'Alte', 'Sao Bartolomeu de Messines', 'Silves', 'Monchique', 'Lagos'],   # the Gran Fondo goes west all the way to Lagos (Matteo 16 Nov); exact course to come from Komoot
    5: ['Quinta do Lago', 'Santa Catarina da Fonte do Bispo', 'Tavira', 'Olhao', 'Quinta do Lago'],
    6: ['Quinta do Lago', 'Almancil', 'Vale do Lobo', 'Quinta do Lago']},
    ['Quinta do Lago'], ['Alto do Malhao', 'Querenca', 'Tavira', 'Alte', 'Monchique', 'Lagos']),
 'lake-como-gran-fondo-il-lombardia': (R, {
    1: ['Como', 'Civiglio', 'Brunate', 'Como'],
    2: ['Como', 'Erba', 'Canzo', 'Sormano', 'Colma di Sormano', 'Nesso', 'Bellagio', 'Ghisallo', 'Asso', 'Erba', 'Como'],
    3: [['Como', 'Erba', 'Asso', 'Ghisallo', 'Bellagio'], ['Varenna', 'Lecco', 'Erba', 'Como']],   # ferry Bellagio - Varenna
    4: ['Como', 'Erba', 'Lecco'],
    5: ['Bergamo', 'Almenno San Salvatore', "Sant'Omobono Terme", 'Costa Valle Imagna', 'Brembilla', 'Zogno', 'Selvino', 'Nembro', 'Bergamo']},   # the Gran Fondo now starts and ends in Bergamo (Matteo 16 Nov); approximate course until the GPX
    ['Como'], ['Civiglio', 'Colma di Sormano', 'Ghisallo', 'Bellagio', 'Varenna', 'Lecco', 'Bergamo', 'Selvino']),
 'italys-coast-to-coast': (R, {
    2: ['Viareggio', 'Pisa', 'Peccioli'],
    3: ['Peccioli', 'San Gimignano', 'Monteriggioni', 'Siena'],
    4: ['Siena', 'Buonconvento', 'Pienza', 'Montepulciano'],
    5: ['Montepulciano', 'Castiglione del Lago', 'Magione', 'Assisi'],
    6: ['Assisi', 'Foligno', 'Colfiorito', 'Camerino'],
    7: ['Camerino', 'Sarnano', 'Amandola', 'Ripatransone', 'San Benedetto del Tronto']},
    ['Viareggio', 'Peccioli', 'Siena', 'Montepulciano', 'Assisi', 'Camerino', 'San Benedetto del Tronto'], ['Pisa', 'San Gimignano', 'Pienza']),
}
COUNTRY_LABELS = {'italian-alps': [('SWITZERLAND', 46.33, 10.06), ('ITALY', 46.40, 10.42)]}   # Matteo 16 Nov: show where the Stelvio loop crosses into Switzerland
INSET = {'lake-garda-and-stelvio': {'3': 'Day trip by van: Passo dello Stelvio'}}   # days far from the rest: a small map in the corner (Matteo 16 Nov)
LABEL = {'Monetier-les-Bains': 'Monêtier-les-Bains', 'Col du Telegraphe': 'Col du Télégraphe', 'Briancon': 'Briançon', 'Ajdovscina': 'Ajdovščina', 'Ziri': 'Žiri',
         'Skofja Loka': 'Škofja Loka', 'Zelezniki': 'Železniki', 'Vrsic': 'Vršič Pass', 'Bled': 'Lake Bled', 'Salo': 'Salò', 'Loule': 'Loulé', 'Querenca': 'Querença',
         'Alto do Malhao': 'Alto do Malhão', 'Sao Bras de Alportel': 'São Brás de Alportel', 'Olhao': 'Olhão', 'Stelvio': 'Passo dello Stelvio', 'Gavia': 'Passo Gavia',
         'Mortirolo': 'Passo del Mortirolo', 'Foscagno': 'Passo Foscagno', 'Pordoi': 'Passo Pordoi', 'Sella': 'Passo Sella', 'Gardena': 'Passo Gardena',
         'Giau': 'Passo Giau', 'Falzarego': 'Passo Falzarego', 'Valparola': 'Passo Valparola', 'Campolongo': 'Passo Campolongo', 'Fedaia': 'Passo Fedaia',
         'San Pellegrino': 'Passo San Pellegrino', 'Tre Croci': 'Passo Tre Croci', 'Rifugio Auronzo': 'Tre Cime di Lavaredo', 'Ghisallo': 'Madonna del Ghisallo',
         'Umbrail': 'Umbrail Pass', 'Eita': 'Val Grosina', 'Rifugio Val Viola': 'Val Viola', 'Torri di Fraele': 'Cancano lakes', 'Lago di Cancano': 'Cancano lakes',
         'Pieve di Tremosine': 'Tremosine', 'Mount Olympus': 'Mount Olympus'}
lab = lambda n: LABEL.get(n, n)

def fetch(profile, names):
    pts = '|'.join(f'{G[n][1]:.5f},{G[n][0]:.5f}' for n in names)
    u = 'https://brouter.de/brouter?' + urllib.parse.urlencode({'lonlats': pts, 'profile': profile, 'alternativeidx': 0, 'format': 'geojson'})
    for i in range(4):
        try:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'cigala-route-maps'}), timeout=120).read())
            f = d['features'][0]
            return {'coords': [[round(x, 5), round(y, 5)] for x, y, *_ in f['geometry']['coordinates']], 'km': round(int(f['properties']['track-length']) / 1000),
                    'up': int(f['properties'].get('filtered ascend', 0)), 'via': names, 'profile': profile}
        except Exception as e:
            err = e; time.sleep(3 + 3 * i)
    raise RuntimeError(f'router failed for {names}: {err}')

def tracks(slug):
    profile, days, _, _ = DAYS[slug]
    os.makedirs(CACHE, exist_ok=True)
    fn = CACHE + slug + '.json'
    cache = json.load(open(fn)) if os.path.exists(fn) else {}
    out = {}
    for n, wps in days.items():
        legs = wps if isinstance(wps[0], list) else [wps]
        key = str(n)
        legs = [[[w, *G[w]] for w in leg] for leg in legs]   # names with their coordinates: a moved point is fetched again
        if key in cache and cache[key].get('via') == legs and cache[key].get('profile') == profile and not os.environ.get('REFETCH_ALL'):
            out[key] = cache[key]; continue
        got = [fetch(profile, [w[0] for w in leg]) for leg in legs]
        out[key] = {'legs': [g['coords'] for g in got], 'km': sum(g['km'] for g in got), 'up': sum(g['up'] for g in got), 'via': legs, 'profile': profile}
        print(f'  {slug} day {n}: {out[key]["km"]} km, {out[key]["up"]} m')
        time.sleep(1)
    json.dump(out, open(fn, 'w'), separators=(',', ':'))
    return out

GARDA_SOUTH = [(45.441, 10.693), (45.447, 10.660), (45.459, 10.623), (45.468, 10.612), (45.490, 10.604), (45.506, 10.608), (45.494, 10.596),
               (45.466, 10.596), (45.463, 10.565), (45.469, 10.541), (45.488, 10.528), (45.509, 10.523), (45.528, 10.548), (45.548, 10.567),
               (45.565, 10.572), (45.586, 10.560), (45.598, 10.536), (45.606, 10.525)]   # Peschiera - Sirmione peninsula - Desenzano - Moniga - Salò (lat, lon)
def garda_ring():
    """Lake Garda from the shore roads: the Gardesana loop (Garda & Stelvio, day 5) from Salò round the north to Peschiera, then the south shore
    by hand (with the Sirmione peninsula). Natural Earth's lake has 63 points: too coarse at the zoom of the Garda maps."""
    fn = CACHE + 'lake-garda-and-stelvio.json'
    if not os.path.exists(fn): return None
    tr = json.load(open(fn))['5']['legs'][0]
    near = lambda q: min(range(len(tr)), key=lambda j: (tr[j][0] - q[1]) ** 2 + (tr[j][1] - q[0]) ** 2)
    a, b = near(G['Salo']), near(G['Peschiera'])
    seg = tr[a:b + 1] if a < b else tr[b:a + 1][::-1]
    return [tuple(x) for x in seg] + [(lon, lat) for lat, lon in GARDA_SOUTH]

def como_ring():
    """Lake Como from its shore roads, round both branches: Como - west shore - Gravedona - Colico - east shore - Lecco - Onno - Bellagio - Nesso - Como.
    Natural Earth's outline is too coarse at the zoom of the Como map (the east-shore road ran over the water)."""
    fn = CACHE + 'shore-como.json'
    way = ['Como', 'Cernobbio', 'Menaggio', 'Gravedona', 'Colico', 'Varenna', 'Lecco', 'Onno', 'Bellagio', 'Nesso', 'Como']
    if os.path.exists(fn) and json.load(open(fn)).get('via') == way: return [tuple(p) for p in json.load(open(fn))['coords']]
    got = fetch(R, way)
    json.dump({'via': way, 'coords': got['coords']}, open(fn, 'w'), separators=(',', ':'))
    return [tuple(p) for p in got['coords']]

def despike(pts, maxlen_km=2.5):
    """Remove short out-and-back spikes: where a waypoint sits just off the road, the router goes to it and comes straight back
    (Matteo 16 Nov: 'weird things coming out' of the routes). Real out-and-back climbs (Alpe d'Huez, the Bonette) are far longer than 2.5 km."""
    d = lambda a, b: math.hypot((a[0] - b[0]) * 111 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 111)
    out = list(pts); changed = True
    while changed:
        changed = False
        for m in range(1, len(out) - 1):
            k = 1
            while m - k >= 0 and m + k < len(out) and d(out[m - k], out[m + k]) < .008: k += 1   # the same road both ways (hairpin legs are further apart)
            k -= 1
            if k >= 2:
                spike = sum(d(out[j], out[j + 1]) for j in range(m - k, m))
                if .15 < spike < maxlen_km:
                    out = out[:m - k + 1] + out[m + k:]; changed = True; break
    return out

def draw(slug, countries, lakes, rivers, named=None):
    from shapely.geometry import LineString
    profile, days, stays, climbs = DAYS[slug]
    T = tracks(slug)
    T = {k: dict(v, legs=[despike(l) for l in v['legs']]) for k, v in T.items()}
    inset = INSET.get(slug, {})
    allpts = [(x, y) for k_, d in T.items() if k_ not in inset for leg in d['legs'] for x, y in leg]
    lons = [p[0] for p in allpts]; lats = [p[1] for p in allpts]
    lat0 = (min(lats) + max(lats)) / 2; k0 = math.cos(math.radians(lat0))
    span_x = (max(lons) - min(lons)) * k0; span_y = max(lats) - min(lats)
    H = int(min(900, max(520, W * span_y / max(span_x, 1e-6) + 70)))   # the frame follows the routes' shape: tall routes get a taller map
    span = max(span_x / W * (H - 70), span_y, 0.05) * 1.22    # fit the routes, a little margin
    s = (H - 70) / span
    cx, cy = (min(lons) + max(lons)) / 2, lat0
    P = lambda lon, lat: (W / 2 + (lon - cx) * k0 * s, (H - 70) / 2 + 8 - (lat - cy) * s)
    E = lambda x: html.escape(x, quote=True)
    # terrain: reuse tours_route_maps' drawing (land, rivers, lakes) by drawing an empty route spec on the same frame
    bx0, bx1 = cx - W / 2 / (k0 * s) - .5, cx + W / 2 / (k0 * s) + .5
    by0, by1 = cy - H / 2 / s - .5, cy + H / 2 / s + .5
    def ring_d(rings, min_area=0, maxspan=None):
        out = []
        for r in rings:
            xs_ = [x for x, y in r]; ys_ = [y for x, y in r]
            if max(xs_) < bx0 or min(xs_) > bx1 or max(ys_) < by0 or min(ys_) > by1: continue   # the shape's box overlaps the frame
            if len(r) > 200 and (min(xs_) < bx0 or max(xs_) > bx1 or min(ys_) < by0 or max(ys_) > by1):   # big shapes: keep only the part in the frame
                from shapely.geometry import Polygon, box
                cl = Polygon(r).buffer(0).intersection(box(bx0, by0, bx1, by1))
                for g in getattr(cl, 'geoms', [cl]):
                    if g.geom_type == 'Polygon' and not g.is_empty:
                        out.append(ring_d([list(g.exterior.coords)], min_area, maxspan))
                continue
            if maxspan and (max(x for x, y in r) - min(x for x, y in r) > maxspan): continue
            d, last = [], None
            for x, y in r:
                X, Y = P(x, y)
                if last and abs(X - last[0]) < .8 and abs(Y - last[1]) < .8: continue
                d.append(f'{X:.1f},{Y:.1f}'); last = (X, Y)
            if len(d) > 2:
                if min_area:
                    a = 0
                    for (x1, y1), (x2, y2) in zip([tuple(map(float, q.split(','))) for q in d], [tuple(map(float, q.split(','))) for q in d[1:] + d[:1]]): a += x1 * y2 - x2 * y1
                    if abs(a) / 2 < min_area: continue
                out.append('M' + 'L'.join(d) + 'Z')
        return ''.join(out)
    gr = garda_ring()
    if gr and bx0 < 10.7 < bx1 and by0 < 45.6 < by1:   # our Garda outline instead of the coarse one
        lakes = [r for r in lakes if not (10.5 < sum(x for x, y in r) / len(r) < 10.9 and 45.4 < sum(y for x, y in r) / len(r) < 45.95)] + [gr]
    if bx0 < 9.25 < bx1 and by0 < 45.95 < by1 and (by1 - by0) < 3:   # zoomed on Lake Como: our shore-road outline
        lakes = [r for r in lakes if not (9.0 < sum(x for x, y in r) / len(r) < 9.5 and 45.8 < sum(y for x, y in r) / len(r) < 46.25)] + [como_ring()]
    land, water = ring_d(countries), ring_d(lakes, 30, 3)
    riv = []
    for l in rivers:
        if not any(bx0 <= x <= bx1 and by0 <= y <= by1 for x, y in l): continue
        d = [f'{P(x, y)[0]:.1f},{P(x, y)[1]:.1f}' for x, y in l]
        if len(d) > 1: riv.append('M' + 'L'.join(d))
    label = f'{trm.ROUTES.get(slug, {}).get("label", "")}' or 'Route map'
    svg = [f'<svg class="rmap dmap" viewBox="0 0 {W} {H}" role="img" aria-label="Route map" xmlns="http://www.w3.org/2000/svg">',
           '<defs><filter id="gl" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3.5"/></filter></defs>',
           f'<rect width="{W}" height="{H}" fill="#0a0c0e"/>',
           f'<path d="{land}" fill="#16191d" stroke="#2c3036" stroke-width=".8" fill-rule="evenodd"/>']   # neighbours: as the country maps
    home = [r for n in ({'Cyprus': ['Cyprus', 'N. Cyprus']}.get(COUNTRY.get(slug), [COUNTRY.get(slug)])) for r in (named or {}).get(n, [])]
    if home:   # the tour's country in our green, with a green outline (the country-map style)
        hd = ring_d(home)
        svg += [f'<path d="{hd}" fill="#009a44" fill-opacity=".13" fill-rule="evenodd"/>',
                f'<path d="{hd}" fill="none" stroke="#2bd47a" stroke-opacity=".55" stroke-width="1.6" stroke-linejoin="round"/>']
    svg += [f'<path d="{water}" fill="#0c1c20" stroke="#2b5d5a" stroke-width="1" stroke-opacity=".8"/>']   # no rivers: at this zoom they read as stray lines (Matteo 16 Nov)
    order = sorted(T, key=int)
    badges = []
    for i, key in enumerate(order):
        if key in inset: continue
        c = COLORS[i % len(COLORS)]
        ds = []
        for leg in T[key]['legs']:
            xy = [P(x, y) for x, y in leg]
            ln = LineString(xy).simplify(.6)
            ds.append('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in ln.coords))
        d = ''.join(ds)
        svg.append(f'<defs><path id="dr{key}" d="{d}"/></defs><g class="dr" data-d="{key}" fill="none" stroke-linejoin="round" stroke-linecap="round">'   # one path, drawn three times
                   f'<use href="#dr{key}" stroke="{c}" stroke-width="8" stroke-opacity=".28" filter="url(#gl)"/>'
                   f'<use href="#dr{key}" stroke="#0a0c0e" stroke-width="6" stroke-opacity=".7"/>'
                   f'<use class="ln" href="#dr{key}" stroke="{c}" stroke-width="3.2"/></g>')
        if len(T[key]['legs']) > 1:   # ferry crossings between legs: dashed
            for a, b in zip(T[key]['legs'], T[key]['legs'][1:]):
                (x1, y1), (x2, y2) = P(*a[-1]), P(*b[0])
                svg.append(f'<path d="M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}" stroke="{c}" stroke-width="2" stroke-dasharray="4 5" fill="none"/>')
        # badge: the point of the day farthest from where it starts (shows where the day goes), nudged off other badges
        leg0 = [p for leg in T[key]['legs'] for p in leg]
        sx, sy = P(*leg0[0])
        pts = [P(*p) for p in leg0]
        cand = sorted(range(len(pts)), key=lambda j: -((pts[j][0] - sx) ** 2 + (pts[j][1] - sy) ** 2))
        if math.dist(pts[cand[0]], (sx, sy)) < 30: cand = list(range(len(pts) // 2, len(pts))) + list(range(len(pts) // 2))   # a tiny loop: its middle
        bx, by = pts[cand[0]]
        avoid = [P(G[n][1], G[n][0]) for n in stays]
        for j in cand[:600]:
            x, y = pts[j]
            if (all(math.dist((x, y), b) > 32 for b, _, _ in badges) and all(math.dist((x, y), a) > 30 for a in avoid)
                    and not any(abs(y - a[1]) < 14 and 0 < (x - a[0]) * (1 if a[0] <= W * .62 else -1) < 150 for a in avoid)   # not on a town's name
                    and 16 < x < W - 16 and 16 < y < H - 60): bx, by = x, y; break
        badges.append(((bx, by), c, key))
    # climbs (gold triangles) and hotels / overnight towns (white)
    used = [b for b, _, _ in badges]
    def text(x, y, t, big, side):
        fs = 14 if big else 12
        dx, anc = (12, 'start') if side == 'r' else (-12, 'end')
        st = f'font-family="Montserrat, Arial, sans-serif" font-size="{fs}" font-weight="{700 if big else 600}" text-anchor="{anc}"'
        return (f'<text x="{x + dx:.1f}" y="{y + 4.5:.1f}" {st} fill="none" stroke="#0a0c0e" stroke-width="4" stroke-linejoin="round">{E(t)}</text>'
                f'<text x="{x + dx:.1f}" y="{y + 4.5:.1f}" {st} fill="{"#f7f8f8" if big else "#c9a36a"}">{E(t)}</text>')
    boxes = [(x - 14, y - 14, x + 14, y + 14) for (x, y), _, _ in badges]
    def free(x, y, t, big, side):
        w = (8.6 if big else 7.3) * len(t) + 4
        bx = (x + 12, y - 9, x + 12 + w, y + 9) if side == 'r' else (x - 12 - w, y - 9, x - 12, y + 9)
        ok = bx[0] > 2 and bx[2] < W - 2 and not any(bx[0] < c[2] and c[0] < bx[2] and bx[1] < c[3] and c[1] < bx[3] for c in boxes)
        return ok, bx
    def place(x, y, t, big, pref, must):
        for side in (pref, 'l' if pref == 'r' else 'r'):
            ok, bx = free(x, y, t, big, side)
            if ok: boxes.append(bx); return side
        if must:
            side = pref if free(x, y, t, big, pref)[1][2] < W - 2 and free(x, y, t, big, pref)[1][0] > 2 else ('l' if pref == 'r' else 'r')
            boxes.append(free(x, y, t, big, side)[1]); return side
        return None
    stay_svg = []
    for n in stays:   # hotels first: their names always show
        x, y = P(G[n][1], G[n][0])
        boxes.append((x - 9, y - 9, x + 9, y + 9))
    for n in stays:
        x, y = P(G[n][1], G[n][0])
        side = place(x, y, lab(n), True, 'l' if x > W * .62 else 'r', True)
        stay_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="#009a44" fill-opacity=".3"/><circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="#f7f8f8" stroke="#009a44" stroke-width="3"/>' + text(x, y, lab(n), True, side))
    seen_lab = set()
    for n in climbs:
        if lab(n) in seen_lab or n not in G: continue
        seen_lab.add(lab(n))
        x, y = P(G[n][1], G[n][0])
        if not (10 < x < W - 10 and 10 < y < H - 60): continue
        if any(math.dist((x, y), P(G[m][1], G[m][0])) < 14 for m in stays): continue   # same place as a hotel
        side = place(x, y, lab(n), False, 'l' if x > W * .62 else 'r', False)   # no room for the name: the triangle alone
        svg.append(f'<path d="M{x:.1f},{y - 6:.1f}L{x + 5.5:.1f},{y + 4:.1f}L{x - 5.5:.1f},{y + 4:.1f}Z" fill="#c9a36a" stroke="#0a0c0e" stroke-width="1.5"/>' + (text(x, y, lab(n), False, side) if side else ''))
    svg += stay_svg
    for (x, y), c, key in badges:
        svg.append(f'<g class="db" data-d="{key}"><circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="{c}" fill-opacity=".18"/><circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="{c}" stroke="#0a0c0e" stroke-width="2"/>'
                   f'<text x="{x:.1f}" y="{y + 4.6:.1f}" font-family="Montserrat, Arial, sans-serif" font-size="12.5" font-weight="800" fill="#0a0c0e" text-anchor="middle">{key}</text></g>')
    for key, title in inset.items():   # the inset: its own frame top right, its own scale
        c = COLORS[order.index(key) % len(COLORS)]
        pts_ = [p for leg in T[key]['legs'] for p in leg]
        iw, ih, ix, iy = 270, 200, W - 270 - 14, H - 200 - 14   # bottom right: the empty corner (the legend is bottom left)
        xs = [p[0] for p in pts_]; ys = [p[1] for p in pts_]
        k1 = math.cos(math.radians(sum(ys) / len(ys)))
        sc = min((iw - 40) / max((max(xs) - min(xs)) * k1, 1e-6), (ih - 64) / max(max(ys) - min(ys), 1e-6))
        Q = lambda lon, lat: (ix + iw / 2 + (lon - (min(xs) + max(xs)) / 2) * k1 * sc, iy + 34 + (ih - 44) / 2 - (lat - (min(ys) + max(ys)) / 2) * sc)
        d = ''.join('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in LineString([Q(*q) for q in leg]).simplify(.5).coords) for leg in T[key]['legs'])
        bx_, by_ = Q(*max(pts_, key=lambda q: (q[0] - pts_[0][0]) ** 2 + ((q[1] - pts_[0][1]) / k1) ** 2))   # badge at the far end: the pass
        px_, py_ = Q(*pts_[0])
        svg.append(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="12" fill="#0a0c0e" fill-opacity=".92" stroke="#2bd47a" stroke-opacity=".35"/>'
                   f'<text x="{ix + 14}" y="{iy + 22}" font-family="Montserrat, Arial, sans-serif" font-size="12" font-weight="700" fill="#d0d6e0">{E(title)}</text>'
                   f'<g class="dr" data-d="{key}" fill="none" stroke-linejoin="round" stroke-linecap="round"><path d="{d}" stroke="{c}" stroke-width="7" stroke-opacity=".25" filter="url(#gl)"/>'
                   f'<path class="ln" d="{d}" stroke="{c}" stroke-width="3"/></g>'
                   f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="5.5" fill="#f7f8f8" stroke="#009a44" stroke-width="2.5"/>'
                   f'<text x="{px_ + (10 if px_ < ix + iw - 120 else -10):.1f}" y="{py_ + 4:.1f}" text-anchor="{"start" if px_ < ix + iw - 120 else "end"}" font-family="Montserrat, Arial, sans-serif" font-size="11.5" font-weight="700" fill="#f7f8f8">Prato allo Stelvio</text>'
                   f'<g class="db" data-d="{key}"><circle cx="{bx_:.1f}" cy="{by_:.1f}" r="11" fill="{c}" stroke="#0a0c0e" stroke-width="2"/>'
                   f'<text x="{bx_:.1f}" y="{by_ + 4.3:.1f}" font-family="Montserrat, Arial, sans-serif" font-size="12" font-weight="800" fill="#0a0c0e" text-anchor="middle">{key}</text></g>'
                   f'<text x="{bx_ + (16 if bx_ < ix + iw / 2 else -16):.1f}" y="{by_ + 4:.1f}" font-family="Montserrat, Arial, sans-serif" font-size="11.5" font-weight="600" fill="#c9a36a" text-anchor="{"start" if bx_ < ix + iw / 2 else "end"}">Passo dello Stelvio 2,757 m</text>')
    for t_, la_, lo_ in COUNTRY_LABELS.get(slug, []):   # neighbouring countries the route crosses into
        x_, y_ = P(lo_, la_)
        svg.append(f'<text x="{x_:.1f}" y="{y_:.1f}" font-family="Montserrat, Arial, sans-serif" font-size="13" font-weight="700" letter-spacing="3" fill="#d0d6e0" fill-opacity=".55" text-anchor="middle">{E(t_)}</text>')
    # small legend: hotel / overnight, climbs
    multi = len(stays) > 1
    svg.append(f'<rect x="12" y="{H - 44}" width="{(205 if multi else 160) + 175}" height="32" rx="8" fill="#0a0c0e" fill-opacity=".85" stroke="#ffffff" stroke-opacity=".12"/>'
               f'<circle cx="30" cy="{H - 28}" r="6" fill="#f7f8f8" stroke="#009a44" stroke-width="3"/>'
               f'<text x="44" y="{H - 23.5}" font-family="Montserrat, Arial, sans-serif" font-size="12.5" font-weight="600" fill="#d0d6e0">{"Hotels &amp; overnight stops" if multi else "Hotel base"}</text>')
    x0 = 44 + (205 if multi else 160) - 12
    svg.append(f'<path d="M{x0},{H - 34}L{x0 + 5.5},{H - 24}L{x0 - 5.5},{H - 24}Z" fill="#c9a36a"/>'
               f'<text x="{x0 + 14}" y="{H - 23.5}" font-family="Montserrat, Arial, sans-serif" font-size="12.5" font-weight="600" fill="#d0d6e0">Climbs &amp; places</text>')
    svg.append('</svg>')
    meta = {k: {'km': T[k]['km'], 'up': T[k]['up'], 'color': COLORS[i % len(COLORS)]} for i, k in enumerate(order)}
    return ''.join(svg), meta

if __name__ == '__main__':
    f = trm.geo_files()
    countries, lakes, rivers = trm.topo_polys(f['countries']), trm.geojson_polys(f['lakes']), trm.geojson_lines(f['rivers'])
    named = trm.topo_named(f['countries'])
    allmeta = {}
    for slug in sys.argv[1:] or DAYS:
        svg, meta = draw(slug, countries, lakes, rivers, named)
        open(OUT + 'day-' + slug + '.svg', 'w').write(svg)   # day-<slug>.svg: build_tours_trips.py prefers it to the overview map <slug>.svg
        allmeta[slug] = meta
        print(slug, len(svg) // 1024, 'KB', {k: v['km'] for k, v in meta.items()})
    mf = CACHE + 'days-meta.json'
    old = json.load(open(mf)) if os.path.exists(mf) else {}
    old.update(allmeta); json.dump(old, open(mf, 'w'), indent=1)
