#!/usr/bin/env python3
"""GeekBI Temu API wrapper - Nexscope Skill.

Call the /api/v1/tools/research/geekbi/temu/categoryList endpoint.

Usage:
  python geekbi_temu_category_list.py '<JSON parameters>'
  python geekbi_temu_category_list.py '<JSON parameters>' --inline

The full response is always saved to the Nexscope session data directory. Responses up to 8 KB are also printed
in full; larger responses print only a summary. --inline forces full output while still saving to disk.
"""

import hashlib
import json
import re
import os
import secrets
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_SESSION_CACHE: dict[str, str] = {}


def get_api_base() -> str:
    """Gateway base URL: prefer env NEXSCOPE_PROXY_BASE; fall back to the production URL."""
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
    """Return the nexscope root directory under the current working directory; callers report write failures."""
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
    """Write the full response to the current session data directory and update session metadata."""
    _, session_dir = _ensure_session(ts)
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    out = os.path.join(data_dir, f"{slug}-{int(ts * 1_000_000)}.{ext}")
    _update_meta(session_dir, skill=slug, file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out


API_PATH = "/api/v1/tools/research/geekbi/temu/categoryList"
SLUG = "ecommerce.geekbi-temu-product"
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
            "1. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS → Settings → API KEY to obtain your Key\n"
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


REQUIRED_FIELDS = ()
SUPPORTED_COUNTRIES = {"br", "de", "es", "fr", "gb", "id", "it", "jp", "mx", "my", "ph", "sg", "th", "us", "vn"}


CONTRACT_JSON = """
{
  "type": "object",
  "properties": {
    "parentCatId": {
      "type": "integer",
      "minimum": 0
    }
  },
  "required": []
}
"""


def validate_params(params):
    """Validate this operation's published contract before any paid request."""
    import math
    from datetime import datetime, timezone
    from urllib.parse import urlsplit

    schema = json.loads(CONTRACT_JSON)
    properties = schema["properties"]
    if not isinstance(params, dict):
        return "Parameters must be a JSON object"
    for key in params:
        if key not in properties:
            return "Unsupported parameter: " + key
    for key in schema.get("required", []):
        if key not in params:
            return key + " is required"

    def timestamp(value):
        if "T" not in value:
            raise ValueError("Time bounds must use ISO-8601 date-time")
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed

    def check(key, value, rule):
        kind = rule["type"]
        if value is None:
            return key + " must not be null"
        if kind in ("integer", "number"):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or isinstance(value, float) and not math.isfinite(value):
                return key + " must be a finite number"
            if kind == "integer" and value != int(value):
                return key + " must be an integer"
            if "minimum" in rule and value < rule["minimum"] or "maximum" in rule and value > rule["maximum"]:
                return key + " is outside the allowed range"
        elif kind == "string":
            if not isinstance(value, str):
                return key + " must be a string"
            if rule.get("minLength") and not value.strip() or len(value) > rule.get("maxLength", len(value)):
                return key + " has an invalid length"
            if "pattern" in rule and re.fullmatch(rule["pattern"], value) is None:
                return key + " has an invalid value"
            if rule.get("format") == "date-time":
                try:
                    timestamp(value)
                except (ValueError, TypeError):
                    return key + " must use ISO-8601 date-time"
            if rule.get("format") == "uri":
                try:
                    url = urlsplit(value)
                    if url.scheme not in ("http", "https") or not url.hostname or url.username:
                        return key + " must be an absolute HTTP(S) asset URL"
                except ValueError:
                    return key + " has an invalid URL"
        elif kind == "array":
            if not isinstance(value, list):
                return key + " must be an array"
            for item in value:
                error = check(key + "[]", item, rule["items"])
                if error:
                    return error
        if "enum" in rule and value not in rule["enum"]:
            return key + " has an unsupported value"
        return None

    for key, value in params.items():
        error = check(key, value, properties[key])
        if error:
            return error
    if "page" in properties and params.get("page", 1) * params.get("size", 20) > 10000:
        return "page * size must not exceed 10000"
    for key, value in params.items():
        if not key.endswith("Min") or key[:-3] + "Max" not in params:
            continue
        maximum = params[key[:-3] + "Max"]
        if isinstance(value, str):
            value, maximum = timestamp(value), timestamp(maximum)
        if value > maximum:
            return key + " must not exceed " + key[:-3] + "Max"
    return None



def call_api(params):
    global _LAST_CALL_WAS_HTTP_ERROR
    _LAST_CALL_WAS_HTTP_ERROR = False
    req = Request(
        get_api_url(),
        data=json.dumps(params).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + get_api_key(),
            "Content-Type": "application/json",
            "User-Agent": "Nexscope-Skill/1.0",
            "SESSION_ID": (os.environ.get("SESSION_ID") or "").strip(),
            "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
            "MODE_ID": os.environ.get("MODE_ID", ""),
            "APP_NAME": os.environ.get("APP_NAME", ""),
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=150) as response:
            raw = response.read().decode("utf-8")
            try:
                return _unwrap_nexscope(json.loads(raw), response.headers)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response", "details": raw[:500]}
    except HTTPError as exc:
        _LAST_CALL_WAS_HTTP_ERROR = True
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        try:
            payload = json.loads(body) if body else {"error": f"HTTP {exc.code}: {exc.reason}"}
            return _unwrap_nexscope(payload, exc.headers)
        except json.JSONDecodeError:
            return {"error": f"HTTP {exc.code}: {exc.reason}", "details": body[:500]}
    except URLError as exc:
        return {"error": f"Connection failed: {exc.reason}"}
    except TimeoutError:
        return {"error": "Connection timed out"}


def _cache_key(params):
    api_key_fingerprint = hashlib.sha256(get_api_key().encode("utf-8")).hexdigest()[:12]
    raw = json.dumps(
        {
            "apiBase": get_api_base(),
            "apiPath": API_PATH,
            "apiKeyFingerprint": api_key_fingerprint,
            "params": params,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


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
        with open(path, encoding="utf-8") as file:
            payload = json.load(file)
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
        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
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
    """Recursively find the business list with the most elements, ignoring columns rendering metadata."""
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
        elif isinstance(node, dict):
            for key, value in node.items():
                if key == "columns":
                    continue
                walk(value, f"{path}.{key}" if path else key)

    walk(obj, "")
    return best[0], best[1]


def summarize(result):
    """Print a compact summary: top-level status fields and the first 3 entries of the largest business list."""
    envelope = result.get("_nexscope") if isinstance(result, dict) else None
    if isinstance(envelope, dict):
        print("Nexscope code: {}; msg: {}".format(envelope.get("code"), envelope.get("msg")))
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")
    for key in (
        "errcode", "errorCode", "code", "errmsg", "msg", "total", "totalCount",
        "count", "currentPage", "page", "perPage", "size", "costTime", "success",
    ):
        value = result.get(key)
        if isinstance(value, (int, float, bool, str)):
            print(f"  {key}: {value}")

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        sample = main_list[:3]
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

    argv = sys.argv[1:]
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not argv:
        print(
            "Usage: geekbi_temu_category_list.py '<JSON parameters>' [--inline] [--no-cache]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as exc:
        print(f"Invalid parameter format: {exc}", file=sys.stderr)
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
    out_path = resolve_data_path(SLUG, time.time())
    try:
        with open(out_path, "w", encoding="utf-8") as file:
            file.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized_bytes)} bytes)")
        if cache_hit:
            print(f"Cache hit: {cache_path}")
    except OSError as exc:
        print(f"Failed to save to {out_path}: {exc}", file=sys.stderr)

    if inline or len(serialized_bytes) <= SMALL_THRESHOLD:
        if cache_hit:
            print(f"Cache hit: {cache_path}", file=sys.stderr)
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
