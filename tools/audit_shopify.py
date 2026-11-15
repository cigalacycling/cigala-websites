"""Summarise retail/products-admin.json and retail/baseline.json into retail/audit.json."""
import json, collections, sys, os
root = os.path.join(os.path.dirname(__file__), "..", "retail")
P = json.load(open(f"{root}/products-admin.json"))
B = json.load(open(f"{root}/baseline.json"))
out = {}
st = collections.Counter(p["status"] for p in P); out["status"] = st
act = [p for p in P if p["status"] == "ACTIVE"]
imgs = [(p, m) for p in act for m in p["media"]["nodes"] if m]
out["active"] = len(act)
out["active_no_image"] = [p["handle"] for p in act if not [m for m in p["media"]["nodes"] if m]]
out["images_total"] = len(imgs)
out["images_no_alt"] = sum(1 for p, m in imgs if not (m.get("alt") or "").strip())
out["products_with_any_missing_alt"] = len({p["handle"] for p, m in imgs if not (m.get("alt") or "").strip()})
out["images_small_lt800"] = sum(1 for p, m in imgs if m.get("image") and max(m["image"]["width"] or 0, m["image"]["height"] or 0) < 800)
out["no_custom_seo_title"] = sum(1 for p in act if not (p["seo"]["title"] or "").strip())
out["no_custom_meta_desc"] = sum(1 for p in act if not (p["seo"]["description"] or "").strip())
out["no_desc_and_no_meta"] = [p["handle"] for p in act if not p["description"].strip() and not (p["seo"]["description"] or "").strip()]
out["empty_description"] = sum(1 for p in act if not p["description"].strip())
out["thin_description_lt150"] = sum(1 for p in act if 0 < len(p["description"].strip()) < 150)
out["active_zero_stock_tracked"] = sum(1 for p in act if p["tracksInventory"] and (p["totalInventory"] or 0) <= 0)
out["active_not_online"] = sum(1 for p in act if not p["onlineStoreUrl"])
out["active_no_collection"] = sum(1 for p in act if not p["collections"]["nodes"])
out["no_vendor"] = sum(1 for p in act if not p["vendor"].strip())
out["no_type"] = sum(1 for p in act if not p["productType"].strip())
out["top_vendors"] = collections.Counter(p["vendor"] for p in act).most_common(12)
# crawl
ok = [b for b in B if b["status"] == 200]
out["crawl"] = {"pages": len(B), "status": collections.Counter(b["status"] for b in B)}
kind = lambda u: u.split("/")[3] if len(u.split("/")) > 4 else "home/other"
out["crawl"]["by_type"] = collections.Counter(kind(b["url"]) for b in B)
out["crawl"]["h1_not_one"] = collections.Counter(len(b["h1"]) for b in ok if len(b["h1"]) != 1)
out["crawl"]["h1_not_one_by_type"] = collections.Counter(kind(b["url"]) for b in ok if len(b["h1"]) != 1)
out["crawl"]["no_meta_desc"] = sum(1 for b in ok if not (b["meta_description"] or "").strip())
td = collections.Counter(b["title"] for b in ok); out["crawl"]["duplicate_titles"] = sum(c for t, c in td.items() if c > 1)
md = collections.Counter(b["meta_description"] for b in ok if b["meta_description"]); out["crawl"]["duplicate_meta"] = sum(c for t, c in md.items() if c > 1)
out["crawl"]["long_titles_gt60"] = sum(1 for b in ok if len(b["title"]) > 60)
out["crawl"]["imgs"] = sum(len(b["images"]) for b in ok)
out["crawl"]["imgs_no_alt"] = sum(1 for b in ok for i in b["images"] if not (i["alt"] or "").strip())
out["crawl"]["schema"] = collections.Counter(t for b in ok for t in set(map(str, b["schema_types"])))
out["crawl"]["product_pages_no_Product_schema"] = sum(1 for b in ok if "/products/" in b["url"] and "Product" not in b["schema_types"])
out["crawl"]["canonical_mismatch"] = sum(1 for b in ok if b["canonical"] and b["canonical"].rstrip("/") != b["url"].rstrip("/"))
out["crawl"]["noindex"] = sum(1 for b in ok if "noindex" in (b["robots"] or ""))
out["crawl"]["hreflang_langs"] = collections.Counter(k for b in ok for k in b["hreflang"])
S = json.load(open(f"{root}/sitemaps.json"))
out["sitemap_urls_by_locale"] = collections.Counter((u.split("/")[3] if len(u.split("/")[3]) == 2 else "en") for v in S.values() if isinstance(v, list) for u in v)
json.dump(out, open(f"{root}/audit.json", "w"), indent=1, default=list)
for k, v in out.items():
    if isinstance(v, list) and len(v) > 12: print(k, len(v), v[:5])
    else: print(k, v)
