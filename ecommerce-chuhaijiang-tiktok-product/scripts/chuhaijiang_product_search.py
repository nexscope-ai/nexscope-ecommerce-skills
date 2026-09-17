#!/usr/bin/env python3
"""
TikTok Product Search - Nexscope Skill
Call the /api/v1/tools/research/chuhaijiang/products/search endpoint.

Usage:
  python chuhaijiang_product_search.py '<JSON parameters>'           # Automatic: full small results; save large results and print a summary
  python chuhaijiang_product_search.py '<JSON parameters>' --inline  # Force full output to stdout

Output policy (default script behavior):
  - **Always** write the complete response to `<nexscope-root>/<YYYY-MM-DD>/<session>/data/ecommerce.chuhaijiang-tiktok-product-<timestamp>.json` (`<cwd>` is the working directory when the script runs; `<session>` comes from the `SESSION_ID` environment variable and groups outputs by user task)
  - Response body ≤ 8 KB: save it, then print the complete JSON to stdout
  - Response body > 8 KB: save it, then print request parameters, top-level status, nested counts, business-list length, and the first 3 main business-list records to stdout
  - Add `--inline` to force full output to stdout (also saved to disk)
"""

import hashlib
import json
import re
import os
import secrets
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

_SESSION_CACHE: dict[str, str] = {}


def get_api_base() -> str:
    """Gateway base URL: prefer env NEXSCOPE_PROXY_BASE; otherwise use the production URL."""
    return (os.environ.get("NEXSCOPE_PROXY_BASE") or "https://api.nexscope.ai").rstrip("/")


def _format_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))


def _session_id(ts: float) -> str:
    """Prefer env SESSION_ID; otherwise generate HHMMSS-<6 hex> (stable within the process)."""
    env = (os.environ.get("SESSION_ID") or "").strip()
    if env:
        return env
    if "_auto" not in _SESSION_CACHE:
        _SESSION_CACHE["_auto"] = time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3)
    return _SESSION_CACHE["_auto"]


def _nexscope_root() -> str:
    """Return the nexscope root directory under the current working directory; the caller raises an error if it is not writable."""
    cached = _SESSION_CACHE.get("_root")
    if cached:
        return cached
    root = os.path.abspath(os.path.join(os.getcwd(), "nexscope"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, ".write_probe")
    with open(probe, "w", encoding="utf-8"):
        pass
    os.remove(probe)
    _SESSION_CACHE["_root"] = root
    return root


def _ensure_meta(root: str, session_dir: str, date_str: str, sid: str, ts: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    if os.path.exists(meta_path):
        return
    meta = {
        "session_id": sid,
        "date": date_str,
        "started_at": _format_iso(ts),
        "skills_called": [],
        "deliverables": [],
        "data_files": [],
        "media_files": [],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    try:
        with open(os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "session_id": sid,
                "date": date_str,
                "path": os.path.relpath(session_dir, root),
                "started_at": _format_iso(ts),
            }, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _ensure_session(ts: float) -> tuple[str, str]:
    date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
    sid = _session_id(ts)
    root = _nexscope_root()
    session_dir = os.path.join(root, date_str, sid)
    os.makedirs(session_dir, exist_ok=True)
    _ensure_meta(root, session_dir, date_str, sid, ts)
    return root, session_dir


def _update_meta(session_dir: str, *, skill: str, file_rel: str, ts: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    if skill and skill not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(skill)
    files = meta.setdefault("data_files", [])
    if file_rel not in files:
        files.append(file_rel)
    meta["last_used_at"] = _format_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def resolve_data_path(slug: str, ts: float, ext: str = "json") -> str:
    """Write the complete response to the current session's data directory and update session metadata."""
    _, session_dir = _ensure_session(ts)
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    out = os.path.join(data_dir, f"{slug}-{int(ts * 1_000_000)}.{ext}")
    _update_meta(session_dir, skill=slug, file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out


API_PATH = "/api/v1/tools/research/chuhaijiang/products/search"
SLUG = "ecommerce.chuhaijiang-tiktok-product"

# For responses at or below this byte count, also print the full response to stdout after saving it.
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
_LAST_CALL_WAS_HTTP_ERROR = False

def get_api_url():
    return get_api_base() + API_PATH


def get_api_key():
    key = os.environ.get("NEXSCOPE_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to obtain your Key\n"
            "2. Set the environment variable: export NEXSCOPE_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key





def _billing_from_headers(headers):
    """Return billing and trace evidence from Nexscope response headers."""
    if headers is None:
        return {}

    def header_value(name):
        value = headers.get(name)
        if isinstance(value, (list, tuple)):
            return value[-1] if value else None
        return value

    raw_token = header_value("X-Cost-Token")
    raw_credit = header_value("X-Cost-Credit")
    trace_id = header_value("X-Kong-Trace-Id")
    billing = {}
    if raw_token not in (None, ""):
        try:
            token = int(raw_token)
            billing["costToken"] = token
        except (TypeError, ValueError):
            billing["costTokenRaw"] = str(raw_token)
    if raw_credit not in (None, ""):
        billing["reportedCostCredit"] = str(raw_credit)
    if trace_id:
        billing["traceId"] = str(trace_id)
    return billing


def _unwrap_nexscope(payload, headers=None):
    """Validate the Nexscope envelope and return the business payload."""
    billing = _billing_from_headers(headers)
    if not isinstance(payload, dict):
        return {"error": "Invalid Nexscope response", "response": payload}
    if type(payload.get("code")) is not int or "data" not in payload:
        return {"error": "Invalid Nexscope response envelope", "response": payload}
    if payload.get("code") != 0:
        return {
            "error": "Nexscope gateway error",
            "code": payload.get("code"),
            "msg": payload.get("msg"),
            "response": payload,
            "_nexscope": {"billing": billing} if billing else {},
        }
    business = payload.get("data")
    if not isinstance(business, dict):
        return {"error": "Invalid Nexscope business payload", "response": payload}
    metadata = {key: payload.get(key) for key in ("code", "msg", "ts", "time", "cost", "traceId") if key in payload}
    if billing:
        metadata["billing"] = billing
    business = dict(business)
    business["_nexscope"] = metadata
    return business




def validate_params(params):
    """Validate this operation's documented request contract before any paid call."""
    from datetime import datetime
    import math

    rules = {'country': {'type': 'string',
                 'enum': ['br',
                          'de',
                          'es',
                          'fr',
                          'gb',
                          'id',
                          'it',
                          'jp',
                          'mx',
                          'my',
                          'ph',
                          'sg',
                          'th',
                          'us',
                          'vn']},
     'page': {'type': 'integer', 'minimum': 1},
     'pageSize': {'type': 'integer', 'minimum': 1, 'maximum': 10},
     'keyword': {'type': 'string'},
     'category': {'type': 'string'},
     'sellerType': {'type': 'string', 'enum': ['1', '2', '3', '4']},
     'freeShipping': {'type': 'boolean'},
     'sort': {'type': 'string',
              'pattern': '^(daily_sold|gmv_30d|gmv_7d|price|rating|sold_30d|sold_7d):(asc|desc)$'},
     'minPrice': {'type': 'number'},
     'maxPrice': {'type': 'number'},
     'minRating': {'type': 'number', 'minimum': 0, 'maximum': 5},
     'maxRating': {'type': 'number', 'minimum': 0, 'maximum': 5},
     'minSold7d': {'type': 'number'},
     'maxSold7d': {'type': 'number'},
     'minSold30d': {'type': 'number'},
     'maxSold30d': {'type': 'number'}}
    required = ('country',)
    if not isinstance(params, dict):
        return "top-level JSON must be an object"
    for key in params:
        if key not in rules:
            return "unsupported parameter: " + key
    for key in required:
        if key not in params:
            return "missing required parameter: " + key
    for key, value in params.items():
        rule = rules[key]
        kind = rule["type"]
        if kind == "string":
            if not isinstance(value, str) or (key in required and not value.strip()):
                return key + " must be a string and required values must be nonempty"
            if "pattern" in rule and not re.fullmatch(rule["pattern"], value):
                return key + " has an invalid format"
            if key in ("date", "listedFrom", "listedTo"):
                try:
                    datetime.strptime(value, "%Y%m%d")
                except ValueError:
                    return key + " must be a valid date in YYYYMMDD format"
        elif kind == "boolean":
            if not isinstance(value, bool):
                return key + " must be a boolean"
        else:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or (isinstance(value, float) and not math.isfinite(value)):
                return key + " must be a finite number"
            if kind == "integer" and value != int(value):
                return key + " must be an integer"
            if "minimum" in rule and value < rule["minimum"]:
                return key + " is below the minimum"
            if "maximum" in rule and value > rule["maximum"]:
                return key + " exceeds the maximum"
        if "enum" in rule and value not in rule["enum"]:
            return key + " is not a supported value"
    for key, value in params.items():
        if key.startswith("min"):
            upper = "max" + key[3:]
            if upper in params and value > params[upper]:
                return key + " must not exceed " + upper
    if "listedFrom" in params and "listedTo" in params and params["listedFrom"] > params["listedTo"]:
        return "listedFrom must not exceed listedTo"
    return None


def call_api(params):
    global _LAST_CALL_WAS_HTTP_ERROR
    _LAST_CALL_WAS_HTTP_ERROR = False
    api_url = get_api_url()
    api_key = get_api_key()
    data = json.dumps(params).encode("utf-8")
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
        "User-Agent": "Nexscope-Skill/1.0",
        "SESSION_ID": (os.environ.get("SESSION_ID") or "").strip(),
        "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
        "MODE_ID": os.environ.get("MODE_ID", ""),
        "APP_NAME": os.environ.get("APP_NAME", ""),
    }
    req = Request(
        api_url,
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(req, timeout=150) as response:
            raw = response.read().decode("utf-8")
            try:
                return _unwrap_nexscope(json.loads(raw), response.headers)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response", "details": raw[:500]}
    except HTTPError as e:
        _LAST_CALL_WAS_HTTP_ERROR = True
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        try:
            payload = json.loads(body) if body else {"error": f"HTTP {e.code}: {e.reason}"}
            return _unwrap_nexscope(payload, e.headers)
        except json.JSONDecodeError:
            return {"error": f"HTTP {e.code}: {e.reason}", "details": body[:500]}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
    except TimeoutError:
        return {"error": "Connection timed out"}


def _cache_key(params):
    api_key_fingerprint = hashlib.sha256(get_api_key().encode("utf-8")).hexdigest()
    raw = json.dumps(
        {
            "version": 1,
            "apiBase": get_api_base(),
            "apiPath": API_PATH,
            "apiKeyFingerprint": api_key_fingerprint,
            "params": params,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _cache_path(params):
    path = os.path.join(os.getcwd(), "nexscope", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            envelope = payload.get("_nexscope")
            if not isinstance(envelope, dict) or type(envelope.get("code")) is not int:
                payload = dict(payload)
                metadata = dict(envelope) if isinstance(envelope, dict) else {}
                metadata.update({"responseContract": "legacy-cache", "code": None, "msg": None})
                payload["_nexscope"] = metadata
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _is_success_result(result):
    if _LAST_CALL_WAS_HTTP_ERROR or not isinstance(result, dict):
        return False
    envelope = result.get("_nexscope")
    return (
        isinstance(envelope, dict)
        and type(envelope.get("code")) is int
        and envelope["code"] == 0
    )



def _business_lists(result):
    """Return the Chuhaijiang business list; avoid mistaking nested arrays such as product images for the main list."""
    if not isinstance(result, dict):
        return []
    data = result.get("data")
    if not isinstance(data, dict):
        return []

    lists = []
    if isinstance(data.get("items"), list):
        lists.append(("data.items", data["items"]))
    for section in ("core", "channel"):
        node = data.get(section)
        if isinstance(node, dict) and isinstance(node.get("items"), list):
            lists.append((f"data.{section}.items", node["items"]))
    return lists


def summarize(result, params):
    """Print a compact summary of request context, nested counts, and the endpoint business list."""
    envelope = result.get("_nexscope") if isinstance(result, dict) else None
    if isinstance(envelope, dict):
        print("Nexscope code: {}; msg: {}".format(envelope.get("code"), envelope.get("msg")))
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")
    request_text = json.dumps(params, ensure_ascii=False, sort_keys=True)
    if len(request_text) > 2000:
        request_text = request_text[:2000] + "..."
    print(f"Request parameters: {request_text}")

    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costTime", "success", "request_id"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")

    data = result.get("data")
    if isinstance(data, dict):
        for key in ("total_count", "page", "page_size", "pageSize"):
            value = data.get(key)
            if isinstance(value, (int, float, bool, str)):
                print(f"  data.{key}: {value}")

    business_lists = _business_lists(result)
    if business_lists:
        print("\nBusiness list fields:")
        for path, items in business_lists:
            print(f"  `{path}`: length={len(items)}")

    main = next(((path, items) for path, items in business_lists if items), None)
    if main:
        list_path, main_list = main
        sample = main_list[:3]
        print(f"\nMain list sample: `{list_path}`")
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))


def _resolve_output_path(ts):
    """Save to the current session's data directory, using the Skill slug for the output file."""
    return resolve_data_path(SLUG, ts)


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
    argv = sys.argv[1:]
    inline = False
    use_cache = True
    if "--inline" in argv:
        inline = True
        argv = [a for a in argv if a != "--inline"]
    if "--no-cache" in argv:
        use_cache = False
        argv = [a for a in argv if a != "--no-cache"]

    if len(argv) != 1:
        print(
            "Usage: chuhaijiang_product_search.py '<JSON parameters>' [--inline] [--no-cache]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("Invalid parameter format: top-level JSON must be an object", file=sys.stderr)
        sys.exit(1)

    validation_error = validate_params(params)
    if validation_error:
        print("Invalid parameters: " + validation_error, file=sys.stderr)
        sys.exit(1)

    cache_path = _cache_path(params) if use_cache else None
    result = _load_cache(cache_path) if cache_path else None
    cache_hit = result is not None
    if result is None:
        result = call_api(params)
        if cache_path and _is_success_result(result):
            _save_cache(cache_path, result)
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    serialized_bytes = serialized.encode("utf-8")
    ts = time.time()
    try:
        out_path = _resolve_output_path(ts)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized_bytes)} bytes)")
        if cache_hit:
            print(f"Cache hit: {cache_path}")
    except OSError as e:
        print(f"Failed to save full response: {e}", file=sys.stderr)
        sys.exit(1)

    if inline or len(serialized_bytes) <= SMALL_THRESHOLD:
        if cache_hit:
            print(f"Cache hit: {cache_path}", file=sys.stderr)
        print(serialized)
    else:
        summarize(result, params)


if __name__ == "__main__":
    main()
