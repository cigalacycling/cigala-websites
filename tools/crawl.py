import sys, json, re, urllib.request, urllib.parse, ssl
from html.parser import HTMLParser
host = sys.argv[1]; seeds = sys.argv[2:]
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NoRedir, urllib.request.HTTPSHandler(context=ctx))
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.d={"title":"","meta_description":None,"canonical":None,"robots":None,"og_title":None,"h1":[],"h2":[],"images":[],"links":[],"schema_types":[]}; s.stack=None; s.buf=""; s.inld=False; s.ld=""
    def handle_starttag(s,t,a):
        a=dict(a)
        if t in("title","h1","h2"): s.stack=t; s.buf=""
        if t=="meta":
            n=(a.get("name") or a.get("property") or "").lower()
            if n=="description": s.d["meta_description"]=a.get("content")
            if n=="robots": s.d["robots"]=a.get("content")
            if n=="og:title": s.d["og_title"]=a.get("content")
        if t=="link" and "canonical" in (a.get("rel") or ""): s.d["canonical"]=a.get("href")
        if t=="img": s.d["images"].append({"src":a.get("src") or a.get("data-src"),"alt":a.get("alt")})
        if t=="a" and a.get("href"): s.d["links"].append(a["href"])
        if t=="script" and a.get("type")=="application/ld+json": s.inld=True; s.ld=""
    def handle_data(s,x):
        if s.stack: s.buf+=x
        if s.inld: s.ld+=x
    def handle_endtag(s,t):
        if t==s.stack:
            txt=re.sub(r"\s+"," ",s.buf).strip()
            if t=="title": s.d["title"]=txt
            else: s.d[t].append(txt)
            s.stack=None
        if t=="script" and s.inld:
            s.inld=False
            try:
                j=json.loads(s.ld); g=j.get("@graph",[j]) if isinstance(j,dict) else j
                for n in g:
                    ty=n.get("@type"); s.d["schema_types"]+= ty if isinstance(ty,list) else [ty]
            except Exception: pass
def norm(u):
    p=urllib.parse.urlsplit(u); return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path or "/",p.query,""))
seen={}; queue=[norm(u) for u in seeds]; insitemap=set(queue)
while queue:
    u=queue.pop(0)
    if u in seen: continue
    try:
        r=op.open(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (baseline-crawler)"}),timeout=30); code=r.status; body=r.read().decode("utf-8","replace"); loc=None
    except urllib.error.HTTPError as e:
        code=e.code; body=""; loc=e.headers.get("Location")
    rec={"url":u,"status":code,"in_sitemap":u in insitemap}
    if loc: rec["redirect_to"]=loc
    if body and code==200:
        p=P(); p.feed(body); d=p.d
        links=[]
        for h in d["links"]:
            if h.startswith(("mailto:","tel:","#","javascript:")): continue
            links.append(norm(urllib.parse.urljoin(u,h)))
        d["internal_links"]=sorted(set(l for l in links if urllib.parse.urlsplit(l).netloc==host))
        d["external_links"]=sorted(set(l for l in links if urllib.parse.urlsplit(l).netloc!=host))
        del d["links"]
        rec.update(d)
        for l in d["internal_links"]:
            if "/wp-content/" in l or "/wp-admin" in l or "/feed" in l: continue
            if l not in seen and l not in queue: queue.append(l)
    seen[u]=rec
json.dump(list(seen.values()),sys.stdout,indent=1,ensure_ascii=False)
