"""Tours structured data (Organization, WebSite, Service with every tour), generated from tours/trips-2027.json
and pushed as an Elementor custom-code snippet (head, entire site) on Tours STAGING.

Replaces the hand-edited JSON-LD that used to live in WPCode (Matteo, 15 Nov): when tours change,
update tours/trips-2027.json, run this script, and the schema follows. Same content as the WPCode version
(tours/wpcode-schema-without-reviews.html + tours/wpcode-schema-service.html).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_tours_wp import req, B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
SITE = 'https://staging.tours.cigalacycling.com'   # Hostinger rewrites the domain when staging is pushed live
SHORT = {'discover-the-algarve-granfondo': 'Algarve & Gran Fondo', 'chianti-gran-fondo-strade-bianche': 'Chianti & Strade Bianche',
         'cyprus-crossing-gravel': 'Cyprus Crossing', 'tuscany-epic-gravel': 'Tuscany Epic', 'maratona-dles-dolomites': 'Maratona dles Dolomites',
         'lake-garda-and-stelvio': 'Lake Garda & Stelvio', 'lake-como-gran-fondo-il-lombardia': 'Lake Como & Il Lombardia'}
COUNTRIES = ['Italy', 'France', 'Portugal', 'Spain', 'Slovenia', 'Croatia', 'Cyprus', 'Belgium']
trips = sorted(json.load(open(ROOT + 'tours/trips-2027.json'))['trips'], key=lambda t: t['start'])
logo = {"@type": "ImageObject", "url": SITE + "/wp-content/uploads/2026/06/ccToursLogo.png"}
org = {"@context": "https://schema.org", "@graph": [{
    "@type": "Organization", "@id": SITE + "/#organization", "name": "Cigala Cycling Tours",
    "legalName": "Cigala Cycling Tours Ltd", "vatID": "IE4385007EH", "url": SITE + "/", "logo": logo, "telephone": "+35340478107"}]}
website = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Cigala Cycling Tours",
           "publisher": {"@id": SITE + "/#organization"},
           "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": SITE + "/?s={search_term_string}"},
                               "query-input": "required name=search_term_string"}}
service = {"@context": "https://schema.org", "@type": "Service", "@id": SITE + "/#service", "name": "Cigala Cycling Tours",
           "serviceType": "Guided Cycling Tours",
           "description": "Fully supported guided cycling tours and holidays across Europe's best destinations, including Italy, France, Portugal, Spain, Slovenia, Croatia and Cyprus, led by expert former professional cyclists.",
           "provider": {"@type": "Organization", "@id": SITE + "/#organization", "name": "Cigala Cycling Tours", "url": SITE + "/", "logo": logo,
                        "email": "tours@cigalacycling.com", "telephone": "+35340478107",
                        "sameAs": ["https://www.facebook.com/CigalaCycling/", "https://x.com/CigalaCycling", "https://www.youtube.com/@cigalacycling",
                                   "https://www.instagram.com/cigalacycling/", "https://wa.me/message/WVBRO6XAMQMCH1",
                                   "https://www.threads.com/@cigalacycling", "https://tiktok.com/@cigalacycling"]},
           "areaServed": [{"@type": "Country", "name": c} for c in COUNTRIES],
           "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Cigala Cycling Tours", "itemListElement": [
               {"@type": "Offer", "itemOffered": {"@type": "Trip", "name": SHORT.get(t['slug'], t['name']), "url": f"{SITE}/trips/{t['slug']}/"}}
               for t in trips]}}
code = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in (org, website, service))
IDS = ROOT + 'stg-tours/pages.json'
ids = json.load(open(IDS))
body = {"title": "Tours structured data (Organization, WebSite, Service)", "status": "publish",
        "meta": {"_elementor_location": "elementor_head", "_elementor_priority": 2, "_elementor_code": code}}
if 'snippet-schema' in ids:
    code_, r = req(f"{B}/wp/v2/elementor_snippet/{ids['snippet-schema']}", json.dumps(body).encode(), 'POST')
else:
    code_, r = req(f"{B}/wp/v2/elementor_snippet", json.dumps(body).encode(), 'POST')
    if code_ == 201: ids['snippet-schema'] = json.loads(r)['id']; json.dump(ids, open(IDS, 'w'), indent=1)
print('schema snippet', code_, ids.get('snippet-schema'), len(trips), 'tours')
