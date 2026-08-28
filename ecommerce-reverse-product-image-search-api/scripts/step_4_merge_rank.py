#!/usr/bin/env python3

import sys as _nexscope_help_sys
if "--help" in _nexscope_help_sys.argv or "-h" in _nexscope_help_sys.argv:
    print('Usage: python step_4_merge_rank.py [arguments]')
    raise SystemExit(0)

"""Provider-neutral implementation documentation."""

import argparse
import json
import sys
import time
from pathlib import Path

try:
    import nexscope_paths
except Exception:
    nexscope_paths = None

DOMAIN_TO_SITE = {
    "amazon.com": "us", "amazon.co.uk": "uk", "amazon.de": "de", "amazon.fr": "fr",
    "amazon.it": "it", "amazon.es": "es", "amazon.co.jp": "jp", "amazon.in": "in",
}

# implementation（report implementation）
PLATFORM_COLUMNS = {
    "amazon":  ["imageUrl", "title", "site", "asin", "price", "category", "bsr",
                "unitsSold", "revenue", "fulfillment", "weight", "dimensions"],
    "walmart": ["imageUrl", "title", "site", "itemId", "price", "category",
                "unitsSold", "revenue", "fulfillment"],
    "tiktok":  ["imageUrl", "title", "site", "itemId", "price", "category",
                "unitsSold", "revenue"],
    "ebay":    ["imageUrl", "title", "site", "itemId", "price", "soldQuantity",
                "fulfillment", "seller"],
    "ozon":    ["imageUrl", "title", "itemId", "price", "category",
                "unitsSold", "revenue", "rating"],
}


def load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _num(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _leaf_category(tree):
    if not tree:
        return None
    if isinstance(tree, list):
        t = [str(x) for x in tree if x]
        return t[-1] if t else None
    s = str(tree)
    for sep in (">", "->", "›", "|", ":", "/"):
        if sep in s:
            parts = [p.strip() for p in s.split(sep) if p.strip()]
            return parts[-1] if parts else s
    return s


def _iter(data):
    items = data.get("products") or data.get("data") or []
    return [items] if isinstance(items, dict) else items


# ---------- implementation（implementation） ----------

def extract_sorftime(files):
    """asin -> {unitsSold, bsr, category}（Keepa value）。"""
    out = {}
    for fp in files or []:
        try:
            data = load_json(fp)
        except Exception:
            continue
        items = data.get("data") or data.get("products") or []
        if isinstance(items, dict):
            items = [items]
        for it in items:
            asin = it.get("asin")
            if not asin:
                continue
            bsr = it.get("salesRank") or it.get("bsr")
            if isinstance(bsr, list):
                bsr = bsr[-1].get("rank") if bsr and isinstance(bsr[-1], dict) else None
            out[asin] = {
                "unitsSold": _num(it.get("monthlySalesUnits")),
                "bsr": _num(bsr),
                "category": _leaf_category(it.get("categoryName") or it.get("category")),
            }
    return out


def rows_amazon(search_files, sf_map=None):
    sf_map = sf_map or {}
    out = []
    for fp in search_files or []:
        try:
            data = load_json(fp)
        except Exception as e:
            print(f"Warning: load {fp} failed: {e}", file=sys.stderr); continue
        site = DOMAIN_TO_SITE.get(Path(fp).stem.replace("step2_amazon_", ""), "us")
        for p in _iter(data):
            if not p.get("asin"):
                continue
            sf = sf_map.get(p.get("asin"), {})
            price = _num(p.get("price"))
            # Keepa implementation；implementation Sorftime implementation
            units = _num(p.get("monthlySalesUnits")) or sf.get("unitsSold")
            bsr = _num(p.get("salesRank") or p.get("salesRank30")) or sf.get("bsr")
            category = _leaf_category(p.get("categoryTree")) or sf.get("category")
            revenue = _num(p.get("monthlySalesRevenue"))
            if not revenue and price and units:
                revenue = round(price * units, 2)
            out.append({
                "platform": "amazon", "site": DOMAIN_TO_SITE.get(p.get("amazonDomain"), site),
                "asin": p.get("asin"), "title": p.get("title") or "", "brand": p.get("brand") or "",
                "imageUrl": p.get("imageUrl") or "", "price": price,
                "currency": p.get("currency") or "USD",
                "category": category, "bsr": bsr, "unitsSold": units, "revenue": revenue,
                "fulfillment": p.get("fulfillment"),
                "weight": p.get("weight") or p.get("packageWeight"),
                "dimensions": p.get("dimension") or p.get("packageDimensions"),
            })
    return out


def rows_walmart(search_files, detail_files):
    detail = {}
    for fp in detail_files or []:
        try:
            d = load_json(fp)
        except Exception:
            continue
        for it in _iter(d):
            iid = it.get("usItemId") or it.get("itemId") or it.get("productId")
            if iid:
                ft = it.get("fulfillmentType")
                detail[str(iid)] = {
                    "unitsSold": _num(it.get("salesEstimate")), "revenue": _num(it.get("revenue")),
                    "category": it.get("departmentName"),
                    "fulfillment": {"WFS": "WFS", "MARKETPLACE": "Seller"}.get(ft, ft),
                }
    out = []
    for fp in search_files or []:
        try:
            data = load_json(fp)
        except Exception:
            continue
        site = Path(fp).stem.replace("step2_walmart_", "") or "us"
        for p in _iter(data):
            iid = p.get("usItemId") or p.get("productId")
            if not iid:
                continue
            dd = detail.get(str(iid), {})
            ship = [x for x, k in (("2-Day", "twoDayShipping"), ("Free", "freeShipping"),
                                   ("Walmart+", "freeShippingWithWalmartPlus")) if p.get(k)]
            price = _num(p.get("price") or p.get("minPrice"))
            rev = dd.get("revenue")
            if not rev and price and dd.get("unitsSold"):
                rev = round(price * dd["unitsSold"], 2)
            out.append({
                "platform": "walmart", "site": site, "itemId": str(iid),
                "title": p.get("title") or "", "imageUrl": p.get("imageUrl") or "",
                "price": price, "currency": p.get("currency") or "USD",
                "category": dd.get("category"), "unitsSold": dd.get("unitsSold"), "revenue": rev,
                "fulfillment": dd.get("fulfillment") or (" / ".join(ship) if ship else None),
            })
    return out


def rows_tiktok(search_files):
    out = []
    for fp in search_files or []:
        try:
            data = load_json(fp)
        except Exception:
            continue
        for p in _iter(data):
            if not p.get("productId"):
                continue
            out.append({
                "platform": "tiktok", "site": p.get("region") or "US",
                "itemId": str(p.get("productId")), "title": p.get("title") or "",
                "imageUrl": p.get("imageUrl") or "", "price": _num(p.get("price")),
                "currency": p.get("currency") or "USD",
                "category": _leaf_category(p.get("categoryName")),
                "unitsSold": _num(p.get("totalSaleCnt")),
                "revenue": _num(p.get("totalSaleGmvAmt")),  # GMV implementationrevenue
            })
    return out


def rows_ebay(search_files):
    out = []
    for fp in search_files or []:
        try:
            data = load_json(fp)
        except Exception:
            continue
        site = Path(fp).stem.replace("step2_ebay_", "") or "us"
        for p in _iter(data):
            if not p.get("productId"):
                continue
            out.append({
                "platform": "ebay", "site": site, "itemId": str(p.get("productId")),
                "title": p.get("title") or "", "imageUrl": p.get("imageUrl") or "",
                "price": _num(p.get("price")), "currency": p.get("currency") or "USD",
                "soldQuantity": _num(p.get("salesQuantity")),
                "fulfillment": p.get("shipping"), "seller": p.get("sellerName"),
            })
    return out


def rows_ozon(detail_files):
    out = []
    for fp in detail_files or []:
        try:
            data = load_json(fp)
        except Exception:
            continue
        for p in _iter(data):
            if not p.get("productId"):
                continue
            out.append({
                "platform": "ozon", "site": "ru", "itemId": str(p.get("productId")),
                "title": p.get("title") or "", "imageUrl": p.get("imageUrl") or "",
                "price": _num(p.get("price")), "currency": p.get("currency") or "₽",
                "category": _leaf_category(p.get("nicheName")),
                "unitsSold": _num(p.get("monthlySalesUnits")),
                "revenue": _num(p.get("monthlySalesRevenue")),
                "rating": _num(p.get("rating")),
            })
    return out


def _topn(rows, n):
    rows = sorted(rows, key=lambda x: ((x.get("unitsSold") is None), -(x.get("unitsSold") or 0)))
    return rows[:n]


def merge(args):
    sf_map = extract_sorftime(args.sorftime_files)
    by_platform = {
        "amazon": _topn(rows_amazon(args.amazon_search_files, sf_map), args.top_n),
        "walmart": _topn(rows_walmart(args.walmart_search_files, args.walmart_detail_files), args.top_n),
        "tiktok": _topn(rows_tiktok(args.tiktok_search_files), args.top_n),
        "ebay": _topn(rows_ebay(args.ebay_search_files), args.top_n),
        "ozon": _topn(rows_ozon(args.ozon_detail_files), args.top_n),
    }
    products = []
    for plat in ["amazon", "walmart", "tiktok", "ebay", "ozon"]:
        cols = PLATFORM_COLUMNS[plat]
        for r in by_platform[plat]:
            # implementation + platform implementation（implementation）
            item = {"platform": plat}
            for c in cols:
                if r.get(c) is not None and r.get(c) != "":
                    item[c] = r[c]
            item.setdefault("currency", r.get("currency") or "USD")
            products.append(item)
    return products, {k: len(v) for k, v in by_platform.items()}


def build_envelope(products, counts):
    platforms = [p for p, n in counts.items() if n]
    summary = "；".join(f"{p} {counts[p]} text" for p in platforms) or "value"
    return {
        "type": "skill-output", "skill": "nexscope-image-competitor-scout", "version": "v1",
        "id": f"product-list-{time.strftime('%Y%m%d')}", "subject": "product_list",
        "label": f"text · {time.strftime('%Y-%m-%d')} · {'/'.join(platforms)}",
        "icon": "📦", "component": "ProductListRenderer",
        "props": {
            "summary": f"text {len(platforms)} text：{summary}（textunits Top）。",
            "data": {"type": "productList", "total": len(products),
                     "products": products, "platformColumns": PLATFORM_COLUMNS},
        },
        "data_sources": [
            {"tool": "nexscope-multimodal-recognize-image"},
            {"tool": "nexscope-amazon-search-by-image"},
            {"tool": "nexscope-walmart-search"},
            {"tool": "nexscope-wallysmarter-product-detail"},
            {"tool": "nexscope-fastmoss-product-search"},
            {"tool": "nexscope-ebay-search"},
            {"tool": "nexscope-mpstats-ozon-product-search"},
            {"tool": "nexscope-mpstats-ozon-product-detail"},
        ],
        "caveats": [
            "value：value（value BSR/value/value Amazon、deliveryvalue TikTok/Ozon）",
            "Ozon valuekeywords + value；eBay valueunits",
            "Amazon unitsvalue Keepa value；revenuevalue，value price×units value",
        ],
    }


def main():
    ap = argparse.ArgumentParser(description="5 value + value + envelope")
    ap.add_argument("--amazon-search-files", nargs="*", default=[])
    ap.add_argument("--sorftime-files", nargs="*", default=[], help="Amazon Keepa value Sorftime value")
    ap.add_argument("--walmart-search-files", nargs="*", default=[])
    ap.add_argument("--walmart-detail-files", nargs="*", default=[])
    ap.add_argument("--tiktok-search-files", nargs="*", default=[])
    ap.add_argument("--ebay-search-files", nargs="*", default=[])
    ap.add_argument("--ozon-detail-files", nargs="*", default=[])
    ap.add_argument("--top-n", type=int, default=10, help="value，value 10")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if not any([args.amazon_search_files, args.walmart_search_files, args.tiktok_search_files,
                args.ebay_search_files, args.ozon_detail_files]):
        print(json.dumps({"error": True, "message": "value"}, ensure_ascii=False))
        sys.exit(1)
    try:
        products, counts = merge(args)
        envelope = build_envelope(products, counts)
        ts = time.time()
        if args.out:
            out_path = Path(args.out); out_path.parent.mkdir(parents=True, exist_ok=True)
        elif nexscope_paths is not None:
            out_path = Path(nexscope_paths.resolve_report_path("nexscope-image-competitor-scout", ts, "json"))
        else:
            out_path = Path("image_competitor_scout_result.json")
        out_path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "ok", "counts": counts, "total": len(products),
                          "output": str(out_path)}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
