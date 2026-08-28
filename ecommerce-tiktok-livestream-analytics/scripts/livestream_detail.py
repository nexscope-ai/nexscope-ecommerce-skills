#!/usr/bin/env python3
"""
NexScope proxy client for /api/v1/tools/research/kalodata/livestream/detail.

Usage:
  python livestream_detail.py '<JSON parameters>'
  python livestream_detail.py '<JSON parameters>' --inline    # force full stdout output
  python livestream_detail.py '<JSON parameters>' --no-cache  # skip local cache

Output strategy (default script behavior):
  - Always writes full response to <cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce-tiktok-livestream-analytics-livestream_detail-<timestamp>.json
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

API_PATH = '/api/v1/tools/research/kalodata/livestream/detail'
SLUG = 'ecommerce-tiktok-livestream-analytics-livestream_detail'
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
def call_api(params):
    base = os.environ.get("NEXSCOPE_PROXY_BASE", "").strip()
    key = os.environ.get("NEXSCOPE_API_KEY", "").strip()
    if not base or not key:
        raise SystemExit("NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY are required")
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

    result = load_cache(params) if use_cache else None
    if result is None:
        result = call_api(params)
        if use_cache:
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
