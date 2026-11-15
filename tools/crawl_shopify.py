"""SEO baseline crawl for the Shopify store (retail.cigalacycling.com).

Usage: python3 tools/crawl_shopify.py HOST OUTDIR [--locales en,fr]
Reads every sitemap, saves the sitemap URL lists, then fetches each page of the
default locale (and any extra locales given) and records title, meta
description, canonical, robots, hreflang, H1/H2, image alt text and JSON-LD
types. Links are not followed: Shopify filter/tag URLs would explode the crawl.
"""
import sys, json, re, ssl, urllib.request, urllib.parse, concurrent.futures as cf
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

host, outdir = sys.argv[1], sys.argv[2]
extra = []
if "--locales" in sys.argv: extra = sys.argv[sys.argv.index("--locales")+1].split(",")
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NoRedir, urllib.request.HTTPSHandler(context=ctx))
UA = {"User-Agent": "Mozilla/5.0 (baseline-crawler)"}
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

def get(u, tries=8):
    import time
    for n in range(tries):
        try:
            r = op.open(urllib.request.Request(u, headers=UA), timeout=40)
            return r.status, r.read().decode("utf-8", "replace"), None
        except urllib.error.HTTPError as e:
            if e.code == 429 and n < tries - 1:
                time.sleep(min(60, float(e.headers.get("Retry-After") or 0) or 5 * 2 ** n)); continue
            return e.code, "", e.headers.get("Location")
        except Exception:
            if n < tries - 1: time.sleep(2 ** n); continue
            return 0, "", None

class P(HTMLParser):
    def __init__(s):
        super().__init__()
        s.d = {"title": "", "meta_description": None, "canonical": None, "robots": None, "og_title": None,
               "hreflang": {}, "h1": [], "h2": [], "images": [], "schema_types": []}
        s.stack = None; s.buf = ""; s.inld = False; s.ld = ""; s.inhead = True
    def handle_starttag(s, t, a):
        a = dict(a)
        if t == "body": s.inhead = False
        if t in ("h1", "h2") or (t == "title" and s.inhead): s.stack = t; s.buf = ""
        if t == "meta" and s.inhead:
            n = (a.get("name") or a.get("property") or "").lower()
            if n == "description": s.d["meta_description"] = a.get("content")
            if n == "robots": s.d["robots"] = a.get("content")
            if n == "og:title": s.d["og_title"] = a.get("content")
        if t == "link":
            rel = a.get("rel") or ""
            if "canonical" in rel: s.d["canonical"] = a.get("href")
            if "alternate" in rel and a.get("hreflang"): s.d["hreflang"][a["hreflang"]] = a.get("href")
        if t == "img": s.d["images"].append({"src": a.get("src") or a.get("data-src"), "alt": a.get("alt")})
        if t == "script" and a.get("type") == "application/ld+json": s.inld = True; s.ld = ""
    def handle_data(s, x):
        if s.stack: s.buf += x
        if s.inld: s.ld += x
    def handle_endtag(s, t):
        if t == "head": s.inhead = False
        if t == s.stack:
            txt = re.sub(r"\s+", " ", s.buf).strip()
            if t == "title": s.d["title"] = txt
            else: s.d[t].append(txt)
            s.stack = None
        if t == "script" and s.inld:
            s.inld = False
            try:
                j = json.loads(s.ld); g = j.get("@graph", [j]) if isinstance(j, dict) else j
                for n in g:
                    ty = n.get("@type"); s.d["schema_types"] += ty if isinstance(ty, list) else [ty]
            except Exception: s.d["schema_types"].append("INVALID_JSON")

# 1. sitemaps (reused from a previous run if present)
import os
if os.path.exists(f"{outdir}/sitemaps.json"):
    sitemaps = json.load(open(f"{outdir}/sitemaps.json")); maps = list(sitemaps)
else:
    sitemaps = None
if sitemaps is None:
  _, idx, _ = get(f"https://{host}/sitemap.xml")
  maps = [e.text for e in ET.fromstring(idx).iter(NS + "loc")]
  sitemaps = {}
  for m in maps:
    code, body, _ = get(m)
    try: sitemaps[m] = [e.find(NS + "loc").text for e in ET.fromstring(body).iter(NS + "url")]
    except Exception: sitemaps[m] = {"status": code, "error": "unparseable"}
  json.dump(sitemaps, open(f"{outdir}/sitemaps.json", "w"), indent=1)

def locale(u):
    seg = urllib.parse.urlsplit(u).path.split("/")[1:2]
    return seg[0] if seg and re.fullmatch(r"[a-z]{2}(-[a-z]{2})?", seg[0]) else "default"
urls = sorted({u for v in sitemaps.values() if isinstance(v, list) for u in v})
todo = [u for u in urls if locale(u) == "default" or locale(u) in extra]
todo = [f"https://{host}/"] + [u for u in todo if u.rstrip("/") != f"https://{host}"]

# 2. pages
def crawl(u):
    code, body, loc = get(u)
    rec = {"url": u, "status": code, "in_sitemap": u in urls}
    if loc: rec["redirect_to"] = loc
    if body and code == 200:
        p = P(); p.feed(body); rec.update(p.d)
    return rec
# progress is appended to a .jsonl file so an interrupted run resumes where it stopped
import time
part = f"{outdir}/baseline.partial.jsonl"
done = {}
if os.path.exists(part):
    for line in open(part):
        r = json.loads(line)
        if r["status"] == 200 or r["status"] in (301, 302, 404, 410): done[r["url"]] = r
left = [u for u in todo if u not in done]
print(len(done), "already done,", len(left), "to fetch", flush=True)
with open(part, "a") as f:
    for i, u in enumerate(left):
        r = crawl(u); done[u] = r
        f.write(json.dumps(r, ensure_ascii=False) + "\n"); f.flush()
        if i % 50 == 0: print(i, u, r["status"], flush=True)
        time.sleep(2.5)
pages = [done[u] for u in todo]
json.dump(pages, open(f"{outdir}/baseline.json", "w"), indent=1, ensure_ascii=False)
os.remove(part)
print(len(maps), "sitemaps,", len(urls), "sitemap URLs,", len(pages), "pages crawled")
