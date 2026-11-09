#!/usr/bin/env python3
"""
Nexscope proxy client for /api/v1/tools/research/dld/productSearch.

Usage:
  python 1688_product_search.py '<JSON parameters>'
  python 1688_product_search.py '<JSON parameters>' --inline    # force full stdout output
  python 1688_product_search.py '<JSON parameters>' --no-cache  # skip local cache

Output strategy (default script behavior):
  - Always writes full response to <cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.1688-product-search-1688_product_search-<timestamp>.json
  - Response <= 8 KB: prints full JSON to stdout after saving
  - Response > 8 KB: prints only summary to stdout after saving
  - Add --inline to force full stdout output (still saves to disk)
"""
import hashlib
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_PATH = '/api/v1/tools/research/dld/productSearch'
SLUG = 'ecommerce.1688-product-search-1688_product_search'
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60

# ── cache ──
def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def _cache_path(params):
    d = os.path.join(os.getcwd(), "nexscope", ".cache", SLUG)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{SLUG}-{_cache_key(params)}.json")

def load_cache(params):
    p = _cache_path(params)
    if not os.path.isfile(p):
        return None
    if time.time() - os.path.getmtime(p) > CACHE_TTL_SEC:
        return None
    try:
        with open(p, encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            payload.setdefault("_cache", {})["hit"] = True
        return payload
    except (OSError, json.JSONDecodeError):
        return None

def save_cache(params, payload):
    try:
        with open(_cache_path(params), "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass

# ── disk output ──
def _nexscope_root():
    for cand in [
        os.path.join(os.getcwd(), "nexscope"),
        os.path.join(os.path.expanduser("~"), "nexscope"),
    ]:
        try:
            os.makedirs(cand, exist_ok=True)
            probe = os.path.join(cand, ".w")
            open(probe, "w").close()
            os.remove(probe)
            return os.path.abspath(cand)
        except OSError:
            continue
    import tempfile
    return os.path.join(tempfile.gettempdir(), "nexscope")

def resolve_output(ts=None):
    if ts is None:
        ts = time.time()
    date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
    sid = os.environ.get("SESSION_ID", "").strip() or time.strftime("%H%M%S", time.localtime(ts))
    root = _nexscope_root()
    session_dir = os.path.join(root, date_str, sid, "data")
    os.makedirs(session_dir, exist_ok=True)
    fname = f"{SLUG}-{int(ts * 1_000_000)}.json"
    return os.path.join(session_dir, fname)

# ── summary ──
def _find_longest_list(obj, prefix=""):
    best = (None, -1, None)
    if isinstance(obj, list):
        return (prefix, len(obj), obj)
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            c = _find_longest_list(v, p)
            if c[1] > best[1]:
                best = c
    return best

def summarize(result):
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "code", "errmsg", "msg", "total", "count", "costToken", "costTime"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")
    path, n, lst = _find_longest_list(result)
    if path and lst:
        print()
        print(f"Longest list: `{path}` ({n} items)")
        print(f"First {min(3, n)}:")
        print(json.dumps(lst[:3], indent=2, ensure_ascii=False))

# ── call_api ──
def validate_params(params):
    if not isinstance(params, dict):
        raise ValueError("Parameters must be a JSON object.")
    for key in ("pageIndex", "pageSize"):
        if key in params and (type(params[key]) is not int or params[key] < 1):
            raise ValueError(f"{key} must be a positive integer.")
    if "pageSize" in params and not 10 <= params["pageSize"] <= 100:
        raise ValueError("pageSize must be between 10 and 100.")
    keyword = params.get("keyWord")
    if keyword is not None and (not isinstance(keyword, str) or not keyword.strip() or len(keyword) > 50 or not any("\u4e00" <= char <= "\u9fff" for char in keyword)):
        raise ValueError("keyWord must contain a Chinese search term, at most 50 characters; translate before calling.")
    if keyword and params.get("goodsUrl"):
        raise ValueError("keyWord and goodsUrl are mutually exclusive.")
    if "productIds" in params:
        values = params["productIds"].split(',') if isinstance(params["productIds"], str) else []
        if not 1 <= len(values) <= 20 or any(not value.isascii() or not value.isdecimal() or int(value) <= 0 for value in values):
            raise ValueError("productIds must contain at most 20 positive ID strings separated by " + ',')
    for field, allowed in {"sortType": {"asc", "desc"}, "searchType": {1, 3}, "companyType": {0, 1, 2}, "offerType": {0, 2, 3, 4, 5, 6}}.items():
        if field in params and (type(params[field]) is bool or params[field] not in tuple(allowed)):
            raise ValueError(f"Invalid {field}.")
    if "cycle" in params and params["cycle"] not in ("7", "30"):
        raise ValueError("cycle must be the string 7 or 30.")
    if "sortField" in params and params["sortField"] not in ("orderCount7d", "orderCount30d", "saleCount7d", "saleCount30d", "saleVolume7d", "saleVolume30d", "offerCreateTime", "price", "consignPrice"):
        raise ValueError("Unsupported sortField.")
    return params


def call_api(params):
    validate_params(params)
    base = (os.environ.get("NEXSCOPE_PROXY_BASE") or "https://api.nexscope.ai").strip()
    key = os.environ.get("NEXSCOPE_API_KEY", "").strip()
    if not key:
        raise SystemExit("NEXSCOPE_API_KEY is required")
    body = json.dumps(params, ensure_ascii=False).encode("utf-8")
    request = Request(base.rstrip("/") + API_PATH, data=body, method="POST", headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace") if error.fp else ""
        try:
            return json.loads(raw)
        except ValueError:
            return {"error": "HTTP {}: {}".format(error.code, error.reason), "details": raw}
    except URLError as error:
        return {"error": "Connection failed: {}".format(error.reason)}

# ── main ──
def main():
    argv = sys.argv[1:]
    inline = False
    use_cache = True
    opts = []
    for a in argv:
        if a == "--inline":
            inline = True
        elif a == "--no-cache":
            use_cache = False
        else:
            opts.append(a)

    if len(opts) < 1:
        print(f"Usage: {sys.argv[0]} '<JSON params>' [--inline] [--no-cache]", file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(opts[0])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        sys.exit("Params must be JSON object")

    try:
        validate_params(params)
    except ValueError as error:
        raise SystemExit(str(error)) from None

    result = load_cache(params) if use_cache else None
    if result is None:
        result = call_api(params)
        if use_cache and isinstance(result, dict) and type(result.get("code")) is int and result["code"] == 0:
            save_cache(params, result)

    serialized = json.dumps(result, ensure_ascii=False)
    out_path = resolve_output()

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"Saved full response: {out_path} ({len(serialized)} bytes)")
        if result.get("_cache", {}).get("hit"):
            print("Cache hit")
    except OSError as e:
        print(f"Failed to save to {out_path}: {e}", file=sys.stderr)

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)

if __name__ == "__main__":
    main()
