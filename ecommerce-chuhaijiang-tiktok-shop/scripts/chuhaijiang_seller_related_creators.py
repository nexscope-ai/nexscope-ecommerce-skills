#!/usr/bin/env python3
"""
TikTok Shop Store Related Creators - Nexscope Skill
Call the /api/v1/tools/research/chuhaijiang/sellers/related-creators endpoint.

Usage:
  python chuhaijiang_seller_related_creators.py '<JSON parameters>'           # Automatic: full small results; save large results and print a summary
  python chuhaijiang_seller_related_creators.py '<JSON parameters>' --inline  # Force full output to stdout

Output policy (default script behavior):
  - **Always** write the complete response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.chuhaijiang-tiktok-shop-<timestamp>.json` (`<cwd>` is the working directory when the script runs, which is the current project directory in Claude Code; `<session>` comes from the `SESSION_ID` environment variable and automatically groups outputs by user task; **writing to /tmp is prohibited**; raise an error if the current directory is not writable)
  - Response body ≤ 8 KB: save it, then print the complete JSON to stdout
  - Response body > 8 KB: save it, then print only a summary to stdout (top-level fields, common counts such as `total`/`count`, and the largest list field's length + first 3 sample records)
  - Add `--inline` to force full output to stdout (also saved to disk)
"""

import json
import re
import hashlib
import os
import sys
import time
import secrets
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_PATH = "/api/v1/tools/research/chuhaijiang/sellers/related-creators"
SLUG = "ecommerce.chuhaijiang-tiktok-shop"

# For responses at or below this byte count, also print the full response after saving it.
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
_LAST_CALL_WAS_HTTP_ERROR = False

_SESSION_CACHE: dict[str, str] = {}

def get_api_base() -> str:
    """Gateway base URL: prefer env NEXSCOPE_PROXY_BASE; otherwise use the production URL."""
    return (os.environ.get("NEXSCOPE_PROXY_BASE") or "https://api.nexscope.ai").rstrip("/")

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
     'id': {'type': 'string'}}
    required = ('country', 'id')
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
            payload = json.loads(response.read().decode("utf-8"))
            return _unwrap_nexscope(payload, response.headers)
    except HTTPError as e:
        _LAST_CALL_WAS_HTTP_ERROR = True
        body = e.read().decode("utf-8") if e.fp else ""
        try:
            payload = json.loads(body) if body else {"error": f"HTTP {e.code}: {e.reason}"}
            return _unwrap_nexscope(payload, e.headers)
        except Exception:
            return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


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
    cwd = os.getcwd()
    path = os.path.join(cwd, "nexscope", ".cache", SLUG)
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



def _find_main_list(obj):
    """Recursively find the list field with the most elements; avoid hardcoded field names to support any structure."""
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)

    walk(obj, "")
    return best[0], best[1]


def summarize(result):
    """Print a compact summary."""
    envelope = result.get("_nexscope") if isinstance(result, dict) else None
    if isinstance(envelope, dict):
        print("Nexscope code: {}; msg: {}".format(envelope.get("code"), envelope.get("msg")))
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")

    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costTime", "success"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        sample = main_list[:3]
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))

def _ensure_meta(root: str, session_dir: str, date_str: str, sid: str, ts: float) -> None:
    """Create _meta.json when the session first appears and append one entry to index.jsonl."""
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
            f.write(
                json.dumps(
                    {
                        "session_id": sid,
                        "date": date_str,
                        "path": os.path.relpath(session_dir, root),
                        "started_at": _format_iso(ts),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass

def _nexscope_root() -> str:
    """Return the nexscope root directory under the current working directory; the caller raises an error if it is not writable."""
    cached = _SESSION_CACHE.get("_root")
    if cached:
        return cached
    root = os.path.abspath(os.path.join(os.getcwd(), "nexscope"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, ".write_probe")
    with open(probe, "w", encoding="utf-8") as f:
        f.write("")
    os.remove(probe)
    _SESSION_CACHE["_root"] = root
    return root

def _format_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))

def _session_id(ts: float) -> str:
    """Prefer env SESSION_ID; otherwise generate HHMMSS-<6 hex> (stable within the same process)."""
    env = (os.environ.get("SESSION_ID") or "").strip()
    if env:
        return env
    if "_auto" not in _SESSION_CACHE:
        _SESSION_CACHE["_auto"] = (
            time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3)
        )
    return _SESSION_CACHE["_auto"]

def _ensure_session(ts: float) -> tuple[str, str]:
    """Return (nexscope_root, session_dir); session_dir is guaranteed to exist."""
    date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
    sid = _session_id(ts)
    root = _nexscope_root()
    session_dir = os.path.join(root, date_str, sid)
    os.makedirs(session_dir, exist_ok=True)
    _ensure_meta(root, session_dir, date_str, sid, ts)
    return root, session_dir

def _update_meta(session_dir: str, *, skill: str, kind: str, file_rel: str, ts: float) -> None:
    """Add this output to the corresponding category list in _meta.json. kind ∈ {data, deliverable, media}."""
    meta_path = os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    if skill and skill not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(skill)
    bucket = {"data": "data_files", "deliverable": "deliverables", "media": "media_files"}.get(
        kind, "data_files"
    )
    files = meta.setdefault(bucket, [])
    if file_rel not in files:  # Deduplicate concurrent or repeated registration of the same path.
        files.append(file_rel)
    meta["last_used_at"] = _format_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def resolve_data_path(slug: str, ts: float, ext: str = "json") -> str:
    """Save raw data for a standard skill to <session>/data/<slug>-<ts>.<ext>."""
    _, session_dir = _ensure_session(ts)
    sub = os.path.join(session_dir, "data")
    os.makedirs(sub, exist_ok=True)
    out = os.path.join(sub, f"{slug}-{int(ts * 1_000_000)}.{ext}")
    _update_meta(session_dir, skill=slug, kind="data", file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out

def _resolve_output_path(ts):
    """Save to <cwd>/nexscope/<date>/<session>/data/<slug>-<ts>.json, grouping by SESSION_ID into the same session."""
    return resolve_data_path(SLUG, ts)


def main():
    argv = sys.argv[1:]
    inline = False
    use_cache = True
    if "--inline" in argv:
        inline = True
        argv = [a for a in argv if a != "--inline"]
    if "--no-cache" in argv:
        use_cache = False
        argv = [a for a in argv if a != "--no-cache"]

    if not argv:
        print(
            "Usage: chuhaijiang_seller_related_creators.py '<JSON parameters>' [--inline] [--no-cache]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
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
    ts = time.time()
    try:
        out_path = _resolve_output_path(ts)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized.encode('utf-8'))} bytes)")
        if cache_hit:
            print(f"Cache hit: {cache_path}")
    except OSError as e:
        print(f"Failed to save full response: {e}", file=sys.stderr)
        sys.exit(1)

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        if cache_hit:
            print(f"Cache hit: {cache_path}", file=sys.stderr)
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
